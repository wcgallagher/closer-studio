"""Render: tracked pieces, cleaned voice, end card, captions, sound design, music, loudness, platform encode."""
from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import brands, captions, cards, cut as cutmod, grade, platforms, track as trk, voice
from .common import FPS, probe, sh

KY = 0.33          # one crop anchor for every punch-in: the eye line never moves at a cut
HOLD_S = 2.0       # end card


def _run(args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"render step failed:\n{' '.join(map(str, args))[:400]}\n{r.stderr[-1500:]}")


def clearance(tr: dict, cam: dict, segs: list, H: int, kick: float = 1.05) -> dict:
    """Where the face is in the output, over the whole cut: chin_max (95th pct of the face bottom) and face_top_min
    (5th pct of the face top), in output pixels, accounting for each piece's punch-in (anchor KY) and the slow push."""
    import numpy as np
    chins, tops = [], []
    for sg in segs:
        z = sg["zoom"] * kick
        for t in np.arange(sg["in"], sg["in"] + sg["frames"] / FPS, 0.25):
            box = trk.face_box_out(tr, cam, t)
            if box is None:
                continue
            y0, y1 = box[1], box[1] + box[3]
            chins.append((y1 - (1 - 1 / z) * H * KY) * z)
            tops.append((y0 - (1 - 1 / z) * H * KY) * z)
    if not chins:
        return {"chin_max": None, "face_top_min": None}
    return {"chin_max": float(np.percentile(chins, 95)), "face_top_min": float(np.percentile(tops, 5))}


def place(tr, cam_fn, segs, plat, style, hook: bool, log=print):
    """Pick the camera face_y and the caption / hook placement so nothing lands on the face. Returns (cam, placement)."""
    W, H = plat["w"], plat["h"]
    band_top, band_bottom = platforms.caption_band(plat)
    zone = plat["zone"]
    hook_h = int(H * 0.044 * 1.25 * 3)                    # three lines, worst case
    for fy in (0.40, 0.36, 0.32, 0.28):
        cam = cam_fn(fy)
        c = clearance(tr, cam, segs, H)
        if c["chin_max"] is None:
            return cam, {"face_y": fy, "captions": "bottom", "band_bottom": band_bottom, "hook_y": 0.30, "chin_max": None, "face_top": None}
        cap_top = captions.text_top(H, style, band_bottom, 2)
        caps_ok = c["chin_max"] + 24 <= cap_top
        room_top = c["face_top_min"] - 24 - zone["top"]
        if caps_ok:
            hook_y = (zone["top"] + room_top / 2) / H if room_top >= hook_h else None
            pl = {"face_y": fy, "captions": "bottom", "band_bottom": band_bottom, "hook_y": hook_y, "chin_max": round(c["chin_max"]),
                  "face_top": round(c["face_top_min"])}
            if hook and hook_y is None:
                pl["hook_where"] = "band"              # hook takes the caption band for its 2.6 s; captions wait
                pl["hook_y"] = (cap_top + band_bottom) / 2 / H
            log(f"placement: face_y {fy}, chin at {c['chin_max']:.0f} px, captions bottom (top edge {cap_top} px), hook at {pl['hook_y']:.2f} H")
            return cam, pl
    # the face fills the frame: captions go to the top zone; keep the head as low as the top block allows
    top_margin = zone["top"] + 20
    block_h = captions.text_top(H, style, 0, 2) * -1
    chosen = None
    for fy in (0.40, 0.36, 0.32, 0.28):
        cam = cam_fn(fy)
        c = clearance(tr, cam, segs, H)
        if c["face_top_min"] - 24 >= top_margin + block_h:
            chosen = (fy, cam, c)
            break
    if chosen is None:
        chosen = (0.28, cam, c)
    fy, cam, c = chosen
    pl = {"face_y": fy, "captions": "top", "top_margin": top_margin, "band_bottom": band_bottom, "hook_y": None,
          "hook_where": "band", "chin_max": round(c["chin_max"]), "face_top": round(c["face_top_min"])}
    cap_top = captions.text_top(H, style, band_bottom, 2)
    pl["hook_y"] = (cap_top + band_bottom) / 2 / H
    log(f"placement: the face fills the frame (chin at {c['chin_max']:.0f} px); captions go to the top zone, hook to the band")
    return cam, pl


def static_crop(sw: int, shh: int, W: int, H: int, fx: float, fy: float) -> str:
    ar = W / H
    ch, cw = shh, int(shh * ar)
    if cw > sw:
        cw, ch = sw, int(sw / ar)
    cx = min(max(int(fx * sw - cw / 2), 0), sw - cw)
    cy = min(max(int(fy * shh - ch * 0.38), 0), shh - ch)
    return f"crop={cw}:{ch}:{cx}:{cy}"



def piece_jobs(video, out, segs, cam, base_crop, W, H, lut, grain, preset, crf, start, push=0.03):
    """ffmpeg commands for the footage pieces that are not rendered yet."""
    jobs = []
    for k, sg in enumerate(segs):
        dst = out / "segs" / f"{k:03d}.mp4"
        if dst.exists():
            continue
        z, D = sg["zoom"], sg["frames"] / FPS
        t0, t1 = sg["in"], sg["in"] + D
        first = trk.vf_track(cam, t0, t1 + 0.05) if cam else base_crop
        kexpr = f"(1.02+{push:.3f}*t/{D:.3f})"
        vf = (f"setpts=PTS-STARTPTS,{first},crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*{KY},"
              f"scale=w='trunc({W}*{kexpr}/2)*2':h=-2:eval=frame:flags=bicubic,crop={W}:{H}:x='(iw-{W})/2':y='(ih-{H})*0.4'")
        if lut:
            vf += f",lut3d=file={lut}"
        post = grade.POST + (f",noise=alls={int(grain * 100)}:allf=t" if grain > 0 else "")
        graph = f"[0:v]{vf}[g];movie={out / 'fill.png'}[f];[g][f]overlay=format=auto:eof_action=repeat,{post},setsar=1,fps={FPS},format=yuv420p[v]"
        gfile = out / "segs" / f"{k:03d}.graph"
        gfile.write_text(graph)
        jobs.append(["ffmpeg", "-v", "error", "-y", "-ss", f"{start + t0:.3f}", "-i", video, "-an", "-frames:v", sg["frames"],
                     "-filter_complex_script", gfile, "-map", "[v]", "-c:v", "libx264", "-preset", preset, "-crf", crf, "-threads", "2", dst])
    return jobs


def prepare_voice(video, out, an, denoise, log):
    """One clean mono 48 kHz window of the source audio (optionally through DeepFilterNet); runs are cut from it."""
    src_wav = out / "voice_src.wav"
    if not src_wav.exists():
        _run(["ffmpeg", "-v", "error", "-y", "-ss", f"{an['start']:.3f}", "-t", f"{an['dur'] + 0.2:.3f}", "-i", video, "-vn", "-ac", "1", "-ar", "48000",
              "-c:a", "pcm_s16le", src_wav])
    if denoise == "deep":
        df = voice.deep_filter_bin()
        if df:
            dfo = out / "voice_df"
            dfo.mkdir(exist_ok=True)
            if not (dfo / src_wav.name).exists():
                log("running DeepFilterNet ...")
                _run([df, "-o", dfo, src_wav])
            return dfo / src_wav.name
        log("deep-filter not installed; using the voice chain only (install.sh --deep-filter adds it)")
    return src_wav


def voice_jobs(out, segs, voice_in, chain):
    runs, cur = [], []
    for k, sg in enumerate(segs):
        if sg["cont"] and cur:
            cur.append(k)
        else:
            if cur: runs.append(cur)
            cur = [k]
    runs.append(cur)
    jobs = []
    for j, r in enumerate(runs):
        dst = out / "segs" / f"r{j:03d}.wav"
        if dst.exists():
            continue
        sg = segs[r[0]]; d = sum(segs[i]["frames"] for i in r) / FPS
        fo = 0.30 if r[-1] == len(segs) - 1 else 0.03
        jobs.append(["ffmpeg", "-v", "error", "-y", "-ss", f"{sg['in']:.3f}", "-t", f"{d + 0.1:.6f}", "-i", voice_in, "-filter_complex",
                     f"[0:a:0]{chain},afade=t=in:st=0:d=0.03,afade=t=out:st={max(0, d - fo):.6f}:d={fo},apad,atrim=0:{d:.6f}[a]",
                     "-map", "[a]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", dst])
    return jobs


def concat(out):
    (out / "v.txt").write_text("".join(f"file '{p}'\n" for p in sorted((out / "segs").glob("*.mp4"))))
    (out / "a.txt").write_text("".join(f"file '{p}'\n" for p in sorted((out / "segs").glob("r*.wav"))))
    _run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", out / "v.txt", "-f", "concat", "-safe", "0", "-i", out / "a.txt",
          "-map", "0:v", "-map", "1:a", "-c", "copy", out / "base.mkv"])


def mix(out, total, speech_end, hits, music):
    """Voice plus sound design plus an optional ducked bed -> mix.wav. hits: [(file, at_s, gain)]."""
    inputs = ["-i", out / "base.mkv"]
    chains, labels, idx = [], [], 1
    if music:
        _run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", music, "-t", f"{total + 0.5:.3f}", "-af", voice.BED, "-ac", "2", "-c:a", "pcm_s16le", out / "bed.wav"])
        inputs += ["-i", out / "bed.wav"]
        env = (f"if(lt(t\\,0.6)\\,t/0.6\\,1)*if(gt(t\\,{speech_end:.3f})\\,max(0.4\\,1-(t-{speech_end:.3f})/0.5)\\,1)"
               f"*if(gt(t\\,{total - 1.2:.3f})\\,max(0\\,({total:.3f}-t)/1.2)\\,1)")
        chains.append(f"[1:a]volume='{env}':eval=frame[bedv];[bedv][key]{voice.DUCK}[bed]")
        labels.append("[bed]"); idx = 2
    for j, (f, at, g) in enumerate(hits):
        inputs += ["-i", f]
        ms = max(0, int(at * 1000))
        chains.append(f"[{idx + j}:a]volume={g},adelay={ms}|{ms},aresample=48000[s{j}]")
        labels.append(f"[s{j}]")
    graph = ("[0:a]asplit=2[vo][key];" if music else "[0:a]anull[vo];") + (";".join(chains) + ";" if chains else "") + \
            f"[vo]{''.join(labels)}amix=inputs={1 + len(labels)}:normalize=0:duration=first[mix]"
    _run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[mix]", "-c:a", "pcm_s16le", out / "mix.wav"])
    return out / "mix.wav"


def reel(video: Path, out: Path, an: dict, brand: dict, plat: dict, style: str = "impact", hook: str = "",
         cta: str | None = None, music: str | None = None, grade_preset: str | None = None, mode: str = "track",
         face=(0.5, 0.38), preview: bool = False, fillers: str = "keep", keep_silence: bool = False, sfx: bool = True,
         riser: bool = False, voice_chain: str = "v3", denoise: str = "chain", caps_max: int | None = None,
         hook_serif: bool = False, end_card: bool = True, log=print) -> dict:
    W, H = plat["w"], plat["h"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "segs").mkdir(exist_ok=True)
    words, sil = an["words"], [tuple(s) for s in an["silences"]]
    segs, speech_end = cutmod.build(words, sil, keep_silence=keep_silence, fillers=fillers)
    if not segs:
        sys.exit("no speech in that window")
    total = round(speech_end + (HOLD_S if end_card else 0.3), 4)
    start = an["start"]
    cta = cta or brand["cta"]["line"]
    offenders = brands.check_copy(brand, f"{hook} {cta}")
    if offenders:
        sys.exit(f"the hook or CTA uses words this brand never prints: {offenders}")

    # camera: tracked (face found in most frames) or static
    cam = None
    band_top, band_bottom = platforms.caption_band(plat)
    pl = {"captions": "bottom", "band_bottom": band_bottom, "hook_y": 0.30, "face_y": face[1]}
    if mode == "track" and an.get("track") and an["track"].get("coverage", 0) >= 0.5:
        tr = dict(an["track"]); tr["dur"] = an["dur"]
        cam, pl = place(tr, lambda fy: trk.camera(tr, W, H, face_y=fy), segs, plat, style, bool(hook), log)
        json.dump({"zoom": cam["zoom"], "cuts": cam["cuts"], "rects_first": cam["rects"][0], "placement": pl}, open(out / "camera.json", "w"), indent=1)
    base_crop = None if cam else static_crop(an["w"], an["h"], W, H, *face)

    lut = grade.lut_path(grade_preset or brand["style"].get("lut", "clean"))
    grain = float(brand["style"].get("grain", 0) or 0)
    fill = out / "fill.png"
    grade.write_fill(fill, W, H, 0.5, 0.36)
    crf, preset = ("26", "veryfast") if preview else ("18", "medium")

    jobs = piece_jobs(video, out, segs, cam, base_crop, W, H, lut, grain, preset, crf, start)
    voice_in = prepare_voice(video, out, an, denoise, log)
    jobs += voice_jobs(out, segs, voice_in, voice.chain(voice_chain))
    log(f"{len(segs)} pieces, {speech_end:.1f} s of speech; rendering {len(jobs)} parts ...")
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(_run, jobs))

    if end_card:
        cards.end_card(brand, W, H, HOLD_S, out / "segs" / "zzz_end.mp4", cta, preset, crf)
        _run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{HOLD_S:.3f}", "-c:a", "pcm_s16le", out / "segs" / "r999_end.wav"])
    concat(out)

    # captions + hook, placed from the clearance pass
    hook_end = 2.6 if hook else 0.0
    ev, srt = captions.events(segs, words, brand, style, speech_end, hook_end, caps_max)
    if hook:
        ev.insert(0, cards.hook_event(hook, brand, W, H, hook_end, serif=hook_serif, y=pl.get("hook_y") or 0.30))
    head = captions.header(W, H, brand, style, pl["band_bottom"], placement=pl.get("captions", "bottom"), top_margin=pl.get("top_margin", 0))
    (out / "captions.ass").write_text(head + "\n".join(ev) + "\n")
    captions.write_srt(out / "captions.srt", srt)

    # sound design and music
    sfx_files = voice.sfx_pack(out / "sfx")
    hits = []
    if sfx:
        hits += [(sfx_files["whoosh"], sg["out_t"] - 0.1, 0.22) for sg in segs if sg["zoom"] > 1]
        hits += [(sfx_files["hit"], sg["out_t"], 0.30) for sg in segs if sg["kick"] and not sg["cont"]]
    if riser:
        hits.append((sfx_files["riser"], max(0.0, speech_end - 1.3), 0.28))
    mix(out, total, speech_end, hits, music)
    m = voice.measure(out / "mix.wav", plat["lufs"], plat["tp"])
    name = f"{video.stem}_{plat['id']}.mp4"
    final = out / name
    _run(["ffmpeg", "-v", "error", "-y", "-i", out / "base.mkv", "-i", out / "mix.wav", "-map", "0:v", "-map", "1:a",
          "-vf", captions.ass_filter(out / "captions.ass"), "-af", voice.final_filter(m["i"], plat["lufs"], plat["tp"]),
          "-c:v", "libx264", "-preset", preset, "-crf", crf, "-maxrate", plat["maxrate"], "-bufsize", plat["maxrate"], "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.4f}", final])
    _run(["ffmpeg", "-v", "error", "-y", "-ss", "0.4", "-i", final, "-frames:v", "1", "-q:v", "2", out / "cover.jpg"])
    fin = voice.measure(final, plat["lufs"], plat["tp"])
    summary = {"file": str(final), "duration_s": total, "speech_s": round(speech_end, 2), "pieces": len(segs), "brand": brand["id"],
               "platform": plat["id"], "style": style, "hook": hook, "cta": cta, "lufs": fin["i"], "true_peak": fin["tp"],
               "camera": "tracked" if cam else "static", "zoom": cam["zoom"] if cam else None, "placement": pl, "fillers": fillers, "music": bool(music),
               "captions_srt": str(out / "captions.srt"), "cover": str(out / "cover.jpg"), "source": f"{video.name} {start:.1f}-{an['end']:.1f} s"}
    json.dump({"summary": summary, "segs": segs}, open(out / "job.json", "w"), indent=1)
    (out / "beats.txt").write_text(cutmod.beat_map(segs, words) + "\n")
    log(f"done: {final} ({total:.1f} s, {fin['i']:.1f} LUFS, {fin['tp']:.1f} dBTP)")
    return summary


def reframe(video: Path, out_file: Path, plat: dict, start: float = 0.0, end: float | None = None, zoom="auto",
            per_scene: bool = False, stride: int = 2, preview: bool = False, log=print) -> dict:
    """Standalone auto-reframe of any clip (audio kept as is)."""
    info = probe(video)
    end = end if end is not None else info["dur"]
    dur = end - start
    log("tracking ...")
    tr = trk.detect(video, start, dur, stride=stride, log=log)
    cam = trk.camera(tr, plat["w"], plat["h"], zoom=zoom, per_scene=per_scene)
    work = out_file.parent / (out_file.stem + "_work")
    work.mkdir(parents=True, exist_ok=True)
    trk.save(tr, work / "track.json")
    crf, preset = ("24", "veryfast") if preview else ("18", "medium")
    spans = [(0.0, dur)] if not per_scene else list(zip([0.0] + cam["cuts"], cam["cuts"] + [dur]))
    parts = []
    for i, (a, b) in enumerate(spans):
        vf = trk.vf_chain(cam, a, b) + f",fps={FPS},format=yuv420p"
        (work / f"{i:03d}.vf").write_text(vf)
        p = work / f"{i:03d}.mp4"
        _run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start + a:.3f}", "-t", f"{b - a:.3f}", "-i", video, "-filter_script:v", work / f"{i:03d}.vf",
              "-c:v", "libx264", "-preset", preset, "-crf", crf, "-c:a", "aac", "-b:a", "192k", p])
        parts.append(p)
    if len(parts) == 1:
        parts[0].replace(out_file)
    else:
        (work / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
        _run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", work / "list.txt", "-c", "copy", out_file])
    log(f"done: {out_file} (zoom {cam['zoom']}, face coverage {tr['coverage']:.0%})")
    return {"file": str(out_file), "zoom": cam["zoom"], "coverage": tr["coverage"], "cuts": cam["cuts"]}


def export(master: Path, out_dir: Path, targets: list[dict], log=print) -> list[dict]:
    """Re-encode a finished master for other platforms with the same aspect: bitrate cap, loudness, duration warning."""
    out_dir.mkdir(parents=True, exist_ok=True)
    info = probe(master)
    m = voice.measure(master)
    rows = []
    for p in targets:
        if abs(info["w"] / info["h"] - p["w"] / p["h"]) > 0.01:
            log(f"skip {p['id']}: aspect differs (render it with `reel --platform {p['id']}` instead)")
            continue
        dst = out_dir / f"{master.stem.rsplit('_', 1)[0]}_{p['id']}.mp4"
        warn = f"over the {p['max_s']} s limit" if p["max_s"] and info["dur"] > p["max_s"] else ""
        _run(["ffmpeg", "-v", "error", "-y", "-i", master, "-vf", f"scale={p['w']}:{p['h']}:flags=lanczos", "-af", voice.final_filter(m["i"], p["lufs"], p["tp"]),
              "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-maxrate", p["maxrate"], "-bufsize", p["maxrate"], "-pix_fmt", "yuv420p",
              "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst])
        rows.append({"platform": p["id"], "file": str(dst), "warning": warn})
        log(f"{p['id']}: {dst.name}{(' (' + warn + ')') if warn else ''}")
    return rows
