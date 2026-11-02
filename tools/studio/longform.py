"""Long-form masters: YouTube authority videos, VSLs, Skool lessons and welcome videos, replays, confirmation videos.

Keeps the speech, cuts the air, alternates framings on the beat, lands keyword pops on emphasised words, cuts away to
chapter cards, quote cards and B-roll on a cadence (a visible layout change every 20 to 40 s), ends on the payoff.
Writes chapters.txt (YouTube timestamps), captions.srt, thumbnail.jpg, cover.jpg, report.md.
"""
from __future__ import annotations

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import brands, captions, cards, cover as cover_mod, cut as cutmod, grade, layers as lay, platforms, track as trk, voice
from .common import FPS, FUNC, norm, probe, fpath, graph_file_flag
from .render import HOLD_S, KY, _run, concat, mix, piece_jobs, prepare_voice, static_crop, voice_jobs

CARD_S = 1.8          # chapter card on screen
QUOTE_MAX_S = 4.5
BROLL_S = 3.2


def _fmt_ts(t: float) -> str:
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}" if t < 3600 else f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}"


def parse_chapters(spec: str | None, an: dict, segs: list) -> list[dict]:
    """'0:Intro,95:The problem' (seconds from the window start) or 'auto'. Returns [{src, out, title, auto}]."""
    out = []
    if not spec:
        return out
    if spec == "auto":
        sents = an["sentences"]
        last, target = 0.0, 110.0
        for s in sents:
            if s["s"] - last >= target - 25 and (s["s"] - last >= target or s["s"] - last >= 85):
                out.append({"src": s["s"], "title": " ".join(s["text"].split()[:5]).strip(",.?!"), "auto": True})
                last = s["s"]
        if not out or out[0]["src"] > 1.0:
            out.insert(0, {"src": 0.0, "title": " ".join(sents[0]["text"].split()[:5]).strip(",.?!") if sents else "Start", "auto": True})
    else:
        for part in spec.split(","):
            t, _, title = part.partition(":")
            out.append({"src": float(t.strip()), "title": title.strip(), "auto": False})
        if out and out[0]["src"] > 1.0:
            out.insert(0, {"src": 0.0, "title": "Start", "auto": True})
    for c in out:
        o = cutmod.src_to_out(segs, c["src"])
        if o is None:
            nxt = [sg for sg in segs if sg["in"] >= c["src"]]
            o = nxt[0]["out_t"] if nxt else segs[-1]["out_t"]
        c["out"] = round(o, 3)
    return out


def find_quote(words: list, line: str) -> tuple[float, float] | None:
    """Locate a spoken line in the words (ordered token match, 80 % hits). Returns (start, end) in window seconds."""
    toks = [norm(w) for w in line.split() if norm(w)]
    if len(toks) < 3:
        return None
    wn = [norm(w["w"]) for w in words]
    best = None
    for i in range(len(wn)):
        j, hit = i, 0
        k = 0
        while k < len(toks) and j < len(wn) and j - i < len(toks) * 2:
            if wn[j] == toks[k]:
                hit += 1; k += 1
            j += 1
        if hit >= 0.8 * len(toks) and (best is None or hit > best[0]):
            best = (hit, i, j - 1)
    if not best:
        return None
    return words[best[1]]["s"], words[best[2]]["e"]


POP_STOP = {"right", "really", "actually", "thing", "things", "gonna", "wanna", "okay", "yeah", "welcome", "name", "basically",
            "literally", "little", "pretty", "about", "there", "where", "which", "would", "could", "should", "every", "going",
            "people", "someone", "something", "anything", "everything", "today", "again", "still", "maybe", "already"}


def pops_from_words(segs, words, every: float = 7.0, show: float = 1.15) -> list[tuple[float, float, str]]:
    """Keyword pops: emphasised content words (a stoplist drops filler-like words and names), one or two words,
    at most one per `every` seconds. (out_t, dur, text)."""
    out, last = [], -99.0
    for sg in segs:
        ws = words[sg["w0"]:sg["w1"] + 1]
        for k, w in enumerate(ws):
            n = norm(w["w"])
            if not w.get("emph") or w.get("func") or len(n) < 5 or n in POP_STOP or w["w"][0].isupper() and k > 0 and not ws[k - 1]["w"].endswith((".", "?", "!")):
                continue
            t = sg["out_t"] + (w["s"] - sg["in"])
            if t - last < every:
                continue
            txt = w["w"].strip(",.?!;:")
            if k + 1 < len(ws) and not ws[k + 1].get("func") and not w["w"].endswith((".", ",", "?", "!")) and len(norm(ws[k + 1]["w"])) >= 4 \
                    and norm(ws[k + 1]["w"]) not in POP_STOP:
                txt += " " + ws[k + 1]["w"].strip(",.?!;:")
            out.append((round(t, 3), show, txt[0].upper() + txt[1:]))
            last = t
    return out


def sentence_ends_out(an, segs):
    pts = []
    for s in an["sentences"]:
        o = cutmod.src_to_out(segs, max(s["e"] - 0.05, 0))
        if o is not None:
            pts.append(o)
    return sorted(pts)


def render_overlay_clip(src: Path, dst: Path, W: int, H: int, dur: float, offset: float, lut, preset, crf, push=0.06):
    """A B-roll cutaway: cover-fit to the frame with a slow push, graded, no audio."""
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setpts=PTS-STARTPTS,"
          f"scale=w='trunc({W}*(1+{push}*t/{dur:.3f})/2)*2':h=-2:eval=frame,crop={W}:{H}:x='(iw-{W})/2':y='(ih-{H})/2'")
    if lut:
        vf += f",lut3d=file={fpath(lut)}"
    vf += f",fps={FPS},format=yuv420p"
    _run(["ffmpeg", "-v", "error", "-y", "-ss", f"{offset:.3f}", "-t", f"{dur:.3f}", "-i", src, "-an", "-vf", vf, "-c:v", "libx264", "-preset", preset, "-crf", crf, dst])
    return dst


def png_clip(png: Path, dst: Path, dur: float, preset, crf):
    _run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", png, "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", preset, "-crf", crf, dst])
    return dst


def longform(video: Path, out: Path, an: dict, brand: dict, plat: dict, fmt: dict, chapters: str | None = None,
             quotes: list[str] | None = None, pops: str = "auto", broll: Path | None = None, music: str | None = None,
             fillers: str | None = None, caps: str | None = None, cta: str | None = None, title: str | None = None,
             grade_preset: str | None = None, preview: bool = False, denoise: str = "chain", change_every: float | None = None, audience: str | None = None, hold: str | None = None, layers: Path | None = None, crf_master: int | None = None, log=print) -> dict:
    W, H = plat["w"], plat["h"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "segs").mkdir(exist_ok=True)
    (out / "cutaways").mkdir(exist_ok=True)
    words, sil = an["words"], [tuple(s) for s in an["silences"]]
    fillers = fillers or fmt.get("fillers", "keep")
    caps = caps or fmt.get("captions", "pops")
    cta_policy = fmt.get("cta", "end_card")
    end_card = cta_policy != "none"
    L = lay.load(layers)
    br = (L.get("breath") if L else None) or fmt.get("breath") or {}
    holds = {}
    for spec, sec in br.get("after", []):             # a held beat after a line: before a claim, a price, the ask
        t = lay._src(words, spec)
        holds[min(range(len(words)), key=lambda i: min(abs(words[i]["e"] - t), abs(words[i]["s"] - t)))] = float(sec)
    segs, speech_end = cutmod.build(words, sil, keep_silence=False, fillers=fillers, punch_every=float(fmt.get("punch_every_s", 4.5)),
                                    zooms=tuple(fmt.get("zooms", (1.0, 1.15))), hard=an.get("hard_cuts"),
                                    sentence_pause=br.get("sentence"), holds=holds)
    if not segs:
        raise SystemExit("no speech in that window")
    if L.get("take_change_kick") and an.get("hard_cuts"):
        for k in range(1, len(segs)):
            prev_end = segs[k - 1]["in"] + segs[k - 1]["frames"] / FPS
            if any(prev_end - 0.02 <= h <= segs[k]["in"] + 0.05 for h in an["hard_cuts"]):
                segs[k]["kick_in"] = True
    for zo in L.get("zoom", []):             # hold a framing over a stretch (hand labels, a held moment)
        a_src, b_src = lay._src(words, zo["from"]), lay._src(words, zo["to"])
        for g in segs:
            if a_src - 0.3 <= g["in"] <= b_src:
                g["zoom"] = float(zo["zoom"])
    for spec in L.get("kicks", []):          # a zoom kick and a whoosh on the piece that starts at these words
        t_src = lay._src(words, spec)
        near = min(segs, key=lambda g: abs(g["in"] - t_src))
        if abs(near["in"] - t_src) < 0.5:
            near["kick_in"] = True
    end_hold = float(L.get("end_hold", HOLD_S + 0.5))
    total = round(speech_end + (end_hold if end_card else 0.0), 4)      # no card: the cut ends on the last word
    start = an["start"]
    cta = cta or brand["cta"]["line"]
    off = brands.check_copy(brand, f"{cta} {title or ''}", audience)
    if off:
        raise SystemExit(f"the title or CTA uses words this brand never prints: {off}")

    # camera: the whole frame for a same-aspect source, tracked otherwise
    cam = None
    if an.get("track") and an["track"].get("coverage", 0) >= 0.5:
        tr = dict(an["track"]); tr["dur"] = an["dur"]
        cam = trk.camera(tr, W, H, face_y=0.42, zmax=1.15)
    base_crop = None if cam else static_crop(an["w"], an["h"], W, H, 0.5, 0.40)
    lut = grade.lut_path(grade_preset or brand["style"].get("lut", "clean"))
    grain = float(brand["style"].get("grain", 0) or 0)
    grade.write_fill(out / "fill.png", W, H, 0.5, 0.40, 0.22)
    crf, preset = ("26", "veryfast") if preview else (str(crf_master or 18), "medium")

    jobs = piece_jobs(video, out, segs, cam, base_crop, W, H, lut, grain, preset, crf, start, push=0.025)
    voice_in = prepare_voice(video, out, an, denoise, log)
    jobs += voice_jobs(out, segs, voice_in, voice.chain("v3"))
    log(f"{len(segs)} pieces, {speech_end:.0f} s of speech; rendering {len(jobs)} parts ...")
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(_run, jobs))
    if end_card:
        own_end = any(str(sc.get("to", "")).upper() == "END" for sc in (L.get("scenes") or [])) if L else False
        cards.end_card(brand, W, H, end_hold, out / "segs" / "zzz_end.mp4", cta, preset, crf, plain=own_end)
        _run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{end_hold:.3f}", "-c:a", "pcm_s16le", out / "segs" / "r999_end.wav"])
    concat(out)
    if L and L.get("finish"):            # the colourist's pass on the cut picture, before any graphics
        from . import finish as fin, placement as plc
        sc0 = plc.Scene(W, H, plc.Mapper(an, segs, cam, W, H, 0.025, KY), *plc.face_track(an))
        faces = [sc0.face_rect(i / FPS) for i in range(int(round(total * FPS)) + 2)]
        prof = L["finish"].get("profile", "vsl") if isinstance(L["finish"], dict) else ("vsl" if "vsl" in fmt["id"] else "brand")
        fin.run(out / "base.mkv", faces, log, profile=prof)

    # animated scenes from the layers file, anchored to words on this cut
    scenes = lay.resolve_scenes(L, words, segs, speech_end, total) if L else []
    mg = lay.render_scenes(scenes, out, L, log) if scenes else out
    in_scene = lambda t, pad=0.0: any(g["start"] - pad <= t <= g["end"] + pad for g in scenes)

    # cutaways: chapter cards, quote cards, B-roll on the cadence
    cutaways = []          # (out_t, dur, clip_path, kind)
    chs = parse_chapters(chapters, an, segs)
    for i, c in enumerate(chs):
        if c["out"] < 0.5:
            continue                                            # the first chapter is the open; no card
        png = cards.chapter_card(i + 1, c["title"], brand, W, H, out / "cutaways" / f"ch{i:02d}.png")
        cutaways.append((c["out"], CARD_S, png_clip(png, out / "cutaways" / f"ch{i:02d}.mp4", CARD_S, preset, crf), "chapter"))
    missing_quotes = []
    for qi, q in enumerate(quotes or []):
        span = find_quote(words, q)
        if not span:
            missing_quotes.append(q); continue
        a = cutmod.src_to_out(segs, span[0]); b = cutmod.src_to_out(segs, span[1])
        if a is None:
            missing_quotes.append(q); continue
        d = min(max((b or a + 2.5) - a + 0.4, 2.0), QUOTE_MAX_S)
        png = cards.quote_card(q, brand, W, H, out / "cutaways" / f"q{qi:02d}.png")
        cutaways.append((a, d, png_clip(png, out / "cutaways" / f"q{qi:02d}.mp4", d, preset, crf), "quote"))
    every = float(change_every if change_every is not None else fmt.get("change_every_s", 40))   # 0 = no scheduled layout change
    # the verdict hold: "a:b" seconds from the window start; no B-roll, no pops, and the cadence check skips it
    hold_out = None
    if hold:
        a, _, b = str(hold).partition(":")
        ha, hb = cutmod.src_to_out(segs, float(a)), cutmod.src_to_out(segs, float(b))
        if ha is None or hb is None or hb <= ha:
            log(f"hold {hold} does not land on kept speech; ignored")
        else:
            hold_out = (round(ha, 3), round(hb, 3))
            inside = [c for c in cutaways if ha - 0.5 < c[0] < hb]
            if inside:
                log(f"note: {len(inside)} card(s) sit inside the hold {ha:.0f}-{hb:.0f} s; move the chapter or quote if the hold must stay clean")
    if broll and every > 0:
        clips = sorted([p for p in Path(broll).iterdir() if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".m4v")])
        ends = sentence_ends_out(an, segs)
        last = 0.0; k = 0; used = {}
        for t in ends:
            if t - last < every * 0.75 or t + BROLL_S > speech_end - 2:
                continue
            if any(abs(t - c[0]) < 6 for c in cutaways):
                last = t; continue
            if hold_out and hold_out[0] - BROLL_S < t < hold_out[1]:
                continue
            if in_scene(t, BROLL_S) or in_scene(t + BROLL_S, 0.3):
                continue
            src = clips[k % len(clips)] if clips else None
            if not src:
                break
            offset = used.get(src, 0.0); used[src] = offset + BROLL_S + 0.5
            try:
                clip = render_overlay_clip(src, out / "cutaways" / f"b{k:02d}.mp4", W, H, BROLL_S, offset, lut, preset, crf)
            except SystemExit:
                used[src] = 0.0; k += 1; continue
            cutaways.append((t - 0.3, BROLL_S, clip, "broll")); last = t; k += 1
    cutaways.sort(key=lambda c: c[0])

    # captions: pops or burned
    band_top, band_bottom = platforms.caption_band(plat)
    cl = L.get("captions") or {}
    if cl.get("style") in captions.STYLES:      # the layers file can pick the caption style (e.g. "premium")
        caps = cl["style"]
    A = lambda x: lay.anchor(words, segs, x, speech_end, total)
    cap_kw = {"cuts": sorted({g["start"] for g in scenes if not g["alpha"]} | {g["end"] for g in scenes if not g["alpha"]} | {speech_end}),
              "words_range": cl.get("words") or fmt.get("caption_words"),
              "plain": [(g["start"], g["end"]) for g in scenes if not g["alpha"]] if cl.get("plain_over_scenes") else None,
              "off": [(A(a), A(b)) for a, b in cl.get("off", [])],
              "breaks": [A(x) for x in cl.get("breaks", [])] or None,
              "display": {k.lower(): v for k, v in (cl.get("display") or {}).items()} or None}
    cap_from = A(cl["from"]) if cl.get("from") is not None else 0.0
    ev, srt = captions.events(segs, words, brand, "clean", speech_end, 0.0, None)
    if caps in captions.STYLES:
        ev, srt = captions.events(segs, words, brand, caps, speech_end, cap_from, None, **cap_kw)
        head = captions.header(W, H, brand, caps, band_bottom)
    else:
        head = captions.header(W, H, brand, "clean", band_bottom)
        ev = []
    # the placement engine sees the face, the captions on screen and everything placed so far
    from . import placement as plc
    psc = plc.Scene(W, H, plc.Mapper(an, segs, cam, W, H, 0.025, KY), *plc.face_track(an))
    if caps in captions.STYLES:
        csz = int(H * captions.STYLES[caps]["size"] * (1.85 if W > H else 1.0))
        crect = (0.07 * W, band_bottom - 1.35 * csz, 0.93 * W, band_bottom + 0.12 * csz)
        offw = cap_kw.get("off") or []
        psc.captions = [(a, b, crect) for a, b, _t in srt if not any(oa - 0.05 <= a < ob for oa, ob in offw)]
    psc.frames = plc.frame_sampler(out / "base.mkv", W, H)
    if caps == "pops" and pops == "auto":
        pop_list = pops_from_words(segs, words)
    elif caps == "pops" and pops not in ("auto", "off", None):
        pop_list = []
        for phrase in [x.strip() for x in str(pops).split("|") if x.strip()]:
            span = find_quote(words, phrase) if len(phrase.split()) >= 3 else None
            if span is None:                                   # one or two words: first occurrence
                toks = [norm(x) for x in phrase.split()]
                for i in range(len(words) - len(toks) + 1):
                    if [norm(w["w"]) for w in words[i:i + len(toks)]] == toks:
                        span = (words[i]["s"], words[i + len(toks) - 1]["e"]); break
            if span is None:
                log(f"pop not found in the speech: {phrase}"); continue
            t = cutmod.src_to_out(segs, span[0])
            if t is not None:
                pop_list.append((round(t, 3), max(1.15, min(2.5, span[1] - span[0] + 0.6)), phrase))
    else:
        pop_list = []
    # where the pops go: the top zone when the head sits low, else the clear third beside the face
    side = "top"
    if cam is not None:
        import numpy as np
        dets = [d for d in an["track"]["dets"] if "cx" in d]
        top_min = np.percentile([(d["cy"] - d["fh"] / 2) for d in dets], 5) * H if dets else H
        if top_min < H * 0.30:
            side = "left" if (np.median([d["cx"] for d in dets]) >= 0.5) else "right"
    for t, d, txt in pop_list:
        if any(c[0] <= t <= c[0] + c[1] for c in cutaways):
            continue
        if hold_out and hold_out[0] <= t <= hold_out[1]:
            continue
        if in_scene(t, 0.3):
            continue
        ev.append(cards.pop_event(txt, t, d, W, H, side))
    moments, chip_t = [], []
    if L:
        lev, moments, chip_t = lay.text_events(L, words, segs, speech_end, total, W, H, brand, scenes, scene=psc)
        lev += lay.hand_events(L, an, segs, cam, W, H, 0.025, KY, words, speech_end, total, scene=psc, chunks=srt, brand=brand)
        head = head.replace("\n[Events]", "\n" + "\n".join(lay.styles(W, H, brand)) + "\n\n[Events]", 1)
        ev += lev
    plc.write_report(psc, out / "placement.json")
    (out / "captions.ass").write_text(head + "\n".join(ev) + "\n")
    captions.write_srt(out / "captions.srt", srt)

    # sound and mix
    sfx = voice.sfx_pack(out / "sfx")
    hits = [(sfx["whoosh"], c[0] - 0.08, 0.18) for c in cutaways if c[3] != "quote"]
    hits += [(sfx["hit"], sg["out_t"], 0.22) for sg in segs if sg["kick"] and not sg["cont"] and not in_scene(sg["out_t"], 0.3)][:12]
    hits += [(sfx["whoosh"], g["start"] - 0.12, 0.16) for g in scenes if g["from_aroll"]]
    hits += [(sfx["tick"], g["start"] - lay.LEAD + v, 0.10) for g in scenes for v in g["cues"].values()]
    hits += [(sfx["tick"], t, 0.12) for t in chip_t]
    hits += [(sfx["whoosh"], sg["out_t"] - 0.12, 0.14) for sg in segs if sg.get("kick_in")]
    for fx in L.get("sfx", []):
        hits.append((sfx[fx.get("name", "whoosh")], lay.anchor(words, segs, fx["at"], speech_end, total), float(fx.get("gain", 0.2))))
    music_mode = fmt.get("music", "none")
    lm = L.get("music") or {}
    if lm.get("file") and not music:
        music = str(lm["file"] if Path(lm["file"]).is_absolute() else Path(L["_base"]) / lm["file"])
    bed = music if music else (brand["style"].get("music") or None if music_mode != "none" else None)
    # a mute is [from, to] (the bed goes out 0.4 s before the line starts) or [from, to, lead] (out exactly lead seconds before)
    mutes = [(lay.anchor(words, segs, m[0], speech_end, total) - (float(m[2]) - 0.4 if len(m) > 2 else 0.0),
              lay.anchor(words, segs, m[1], speech_end, total)) for m in lm.get("mute", [])]
    sd = L.get("sound") if L else None
    if sd:
        from . import sound as snd
        ow = snd.out_words(an, segs)
        snd.assemble_voice(voice_in, segs, total, out / "voice_raw.wav")
        A_ = lambda x: lay.anchor(words, segs, x, speech_end, total)
        evs = [{"kind": "card_in", "at": c[0], "why": f"cut to {c[3]}"} for c in cutaways if c[3] != "quote"]
        evs += [{"kind": "end_card" if g["is_end"] else "card_in", "at": g["start"], "why": f"card {g['scene']} in"} for g in scenes if g["from_aroll"] or g["is_end"]]
        evs += [{"kind": "card_out", "at": g["end"], "why": f"card {g['scene']} out"} for g in scenes if g.get("to_aroll")]
        evs += [{"kind": "card_element", "at": g["start"] - lay.LEAD + v, "why": f"{g['scene']} element lands"} for g in scenes for v in g["cues"].values()]
        evs += [{"kind": "chip", "at": t, "why": "chip in"} for t in chip_t]
        evs += [{"kind": "section_change", "at": sg["out_t"], "why": "take change"} for sg in segs if sg.get("kick_in")]
        evs += [{"kind": "punch_in", "at": sg["out_t"], "why": "punch-in"} for sg in segs if sg.get("kick") and not sg.get("cont") and not sg.get("kick_in")]
        for fx in L.get("sfx", []):
            evs.append({"kind": fx.get("event", "card_in"), "at": A_(fx["at"]), "why": fx.get("why", "layers file"), "gain_db": float(fx.get("gain_db", 0))})
        land = A_(sd["land"]) if sd.get("land") is not None else None
        secs = None
        if sd.get("sections"):
            secs = []
            for i, sc in enumerate(sd["sections"]):
                a0 = A_(sc["from"]) if sc.get("from") is not None else 0.0
                b0 = A_(sd["sections"][i + 1]["from"]) if i + 1 < len(sd["sections"]) else total
                secs.append({"name": sc["name"], "a": a0, "b": b0, "vm": float(sc["vm"]), "p10": float(sc.get("p10", sc["vm"] - 6))})
        sfx_dir = sd.get("sfx_dir")
        if sfx_dir and not Path(sfx_dir).is_absolute():
            sfx_dir = str(Path(L["_base"]) / sfx_dir)
        rules = dict(sd.get("rules") or {})
        if sd.get("music_enter"):                      # the score's first beat lands on this word
            rules["music"] = dict(rules.get("music") or {}, enter_s=A_(sd["music_enter"]), pre_roll=sd.get("pre_roll", "dry"),
                                  hole_s=float(sd.get("hole_s", 0.18)))
        if sd.get("dialect"):
            rules["sfx"] = dict(rules.get("sfx") or {}, dialect=sd["dialect"])
        snd.direct(out, out / "voice_raw.wav", ow, total, speech_end, Path(bed) if bed else None, evs, mutes, land,
                   rules, log=log, sections=secs, sfx_dir=Path(sfx_dir) if sfx_dir else None,
                   joins=[sg["out_t"] for k, sg in enumerate(segs) if k and not sg.get("cont")])
    else:
        mix(out, total, speech_end, hits, bed, float(lm.get("start", 0.0)) if music and lm.get("file") else 0.0, mutes)
    m = voice.measure(out / "mix.wav", plat["lufs"], plat["tp"])

    # composite the cutaways over the base, burn pops/captions, loudness, encode
    inputs = ["-i", out / "base.mkv", "-i", out / "mix.wav"]
    chain, prev = [], "[0:v]"
    mchain, prev = lay.moment_graph(moments, prev)
    chain += mchain
    s_in, s_chain, prev = lay.scene_graph(scenes, mg, W, H, 2, prev)
    inputs += s_in
    chain += s_chain
    first = 2 + len(s_in) // 2
    for i, (t, d, clip, kind) in enumerate(cutaways):
        inputs += ["-i", clip]
        chain.append(f"[{first + i}:v]format=yuva420p,fade=t=in:st=0:d=0.10:alpha=1,fade=t=out:st={d - 0.10:.3f}:d=0.10:alpha=1,setpts=PTS-STARTPTS+{t:.3f}/TB[c{i}]")
        chain.append(f"{prev}[c{i}]overlay=eof_action=pass:enable='between(t,{t:.3f},{t + d:.3f})'[v{i}]")
        prev = f"[v{i}]"
    chain.append(f"{prev}{captions.ass_filter(out / 'captions.ass')},format=yuv420p[vout]")
    (out / "final.graph").write_text(";".join(chain))
    name = f"{video.stem}_{fmt['id']}_{plat['id']}.mp4"
    final = out / name
    _run(["ffmpeg", "-v", "error", "-y", *inputs, graph_file_flag(), out / "final.graph", "-map", "[vout]", "-map", "1:a",
          "-af", voice.final_filter(m["i"], plat["lufs"], plat["tp"]), "-c:v", "libx264", "-preset", preset, "-crf", crf,
          "-maxrate", plat["maxrate"], "-bufsize", plat["maxrate"], "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
          "-color_trc", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "192k",
          "-movflags", "+faststart", "-t", f"{total:.4f}", final])
    fin = voice.measure(final, plat["lufs"], plat["tp"])

    # chapters, cover, summary
    lines = []
    for i, c in enumerate(chs):
        lines.append(f"{_fmt_ts(c['out'] if i else 0)} {c['title']}")
    (out / "chapters.txt").write_text("\n".join(lines) + ("\n" if lines else ""))
    cov = cover_mod.build(video, out, brand, title or (chs[0]["title"] if chs else cta), an, start=start, end=an["end"], log=log)
    layout_times = sorted(set([c[0] for c in cutaways] + (list(hold_out) if hold_out else []) + [g["start"] for g in scenes] + [g["end"] for g in scenes] +
                              [g["start"] - lay.LEAD + v for g in scenes for v in g["cues"].values()] + chip_t + [m["a"] for m in moments] + [m["b"] for m in moments] +
                              [sg["out_t"] for sg in segs if sg.get("kick_in")] +
                              [lay.anchor(words, segs, v[1], speech_end, total) for v in (L.get("hands") or {}).get("labels", {}).values() if not isinstance(v, dict)]))
    gaps, last = [], 0.0
    for t in layout_times + [speech_end]:
        is_hold = bool(hold_out) and last == hold_out[0] and t == hold_out[1]
        if every > 0 and t - last > every and not is_hold:
            gaps.append((round(last, 1), round(t, 1)))
        last = t
    summary = {"file": str(final), "kind": "long", "format": fmt["id"], "platform": plat["id"], "brand": brand["id"], "duration_s": total,
               "speech_s": round(speech_end, 2), "pieces": len(segs), "cutaways": [{"t": c[0], "dur": c[1], "kind": c[3]} for c in cutaways],
               "chapters": chs, "auto_chapter_titles": any(c.get("auto") for c in chs), "missing_quotes": missing_quotes,
               "pops": len(pop_list), "captions": caps, "lufs": fin["i"], "true_peak": fin["tp"], "camera": "tracked" if cam else "static",
               "layout_gaps_over_limit": gaps, "change_every_s": every, "hook_deadline_s": fmt.get("hook_deadline_s", 10),
               "audience": audience or brand.get("audience", "prospect"), "hold": hold_out,
               "scenes": [{k: g[k] for k in ("id", "scene", "start", "end")} for g in scenes], "scene_share": round(sum(g["end"] - g["start"] for g in scenes) / max(total, 1), 3),
               "end_hold": end_hold,
               "length_warning": None, "cover": cov, "source": f"{video.name} {start:.1f}-{an['end']:.1f} s"}
    from . import formats as fm
    summary["length_warning"] = fm.check_length(fmt, total)
    if L and L.get("offer"):          # the word the offer starts on (rulebook BP-01: a VSL's offer lands by 15 s)
        summary["offer_s"] = round(lay.anchor(words, segs, L["offer"], speech_end, total), 2)
    json.dump({"summary": summary, "segs": segs}, open(out / "job.json", "w"), indent=1)
    (out / "beats.txt").write_text(cutmod.beat_map(segs, words) + "\n")
    log(f"done: {final} ({total:.0f} s, {len(cutaways)} cutaways, {len(pop_list)} pops, {fin['i']:.1f} LUFS)")
    return summary
