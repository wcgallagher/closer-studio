"""Assemble: a script cut from several takes, as one selects file plus its analysis.

A spec names the takes and the beats in script order. Each beat is a range of one take, given either as words
("from" / "to", with an approximate time to pick the right occurrence) or as seconds ("in" / "out"). The command
writes one selects file in script order, an analysis.json that `longform` and `reel` reuse as is, and selects.json
(where every beat came from). A take change is a hard cut: the cut never joins two takes inside one piece and the
camera snaps there instead of panning.

Word timing comes from one of two places, per take:
  - "words": an existing word map (a frame map with "words": [[start, end, word, p], ...] and "silences" in ms, or a
    kit analysis.json). Nothing is re-transcribed. Use this when a project already locked its words.
  - nothing: the take is analysed once with faster-whisper (cached in <out>/takes/<take>/analysis.json).

Spec (JSON; relative paths resolve from the spec's folder):
{
  "takes": {"take1": {"video": "inbox/take1.mp4", "words": "frame_map/take1.json"}, ...},
  "beats": [
    {"beat": "HOOK", "take": "take2", "from": "Life", "from_s": 0.0, "to": "business.", "to_s": 5.6},
    {"beat": "CTA",  "take": "take3", "in": 50.9, "out": 52.6}
  ]
}
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from .common import FILLERS, FUNC, norm, probe, save_json

PAD_IN = 0.14      # room before a beat's first word (more than the cut's own in-pad, so a piece never reaches across)
PAD_OUT = 0.22     # room after its last word
FPS = 30


def _words_from_map(path: Path) -> tuple[list[dict], list[tuple[float, float]]]:
    d = json.loads(path.read_text())
    if "words" in d and d["words"] and isinstance(d["words"][0], dict):          # a kit analysis.json
        return [dict(w) for w in d["words"]], [tuple(s) for s in d.get("silences", [])]
    k = 0.001 if d.get("units", "ms") == "ms" else 1.0
    words = []
    for s, e, w, p in d["words"]:
        w = str(w).strip()
        if words and len(w) > 1 and (w[0] in "-.," or words[-1]["w"].endswith("-")) and not w[1:2].isspace():
            # the word map splits "$30" ",000", "50" "-50", "p" ".m." and "cross" "-selling": keep them as one word
            words[-1]["w"] += w
            words[-1]["e"] = round(e * k, 3)
            words[-1]["p"] = round(min(words[-1]["p"], float(p)), 2)
            continue
        words.append({"w": w, "s": round(s * k, 3), "e": round(e * k, 3), "p": round(float(p), 2)})
    sil = [(round(a * k, 3), round(b * k, 3)) for a, b in d.get("silences", [])]
    return words, sil


def _find(words: list[dict], token: str, near: float | None) -> int:
    t = norm(token)
    hits = [i for i, w in enumerate(words) if norm(w["w"]) == t]
    if not hits:
        hits = [i for i, w in enumerate(words) if norm(w["w"]).startswith(t) or t.startswith(norm(w["w"]) or "~")]
    if not hits:
        raise SystemExit(f"word '{token}' not found in the take")
    return min(hits, key=lambda i: abs(words[i]["s"] - (near if near is not None else words[i]["s"])))


def _flags(words: list[dict], a: np.ndarray | None, sr: int = 16000):
    """filler / function flags, and emphasis: from loudness when audio is given, else from the text and the pauses."""
    hop = 320
    content = [norm(w["w"]) not in FUNC and len(norm(w["w"])) >= 3 for w in words]
    if a is not None:
        lv = []
        for w in words:
            i0, i1 = int(w["s"] * sr), max(int(w["s"] * sr) + hop, int(w["e"] * sr))
            seg = a[i0:i1]
            lv.append(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) if len(seg) else -80.0)
        lv = np.array(lv)
        base = lv[np.array(content)] if any(content) else lv
        mu, sd = float(np.mean(base)), float(np.std(base) + 1e-6)
        z = (lv - mu) / sd
    else:
        z = None
    last_emph = -9.0
    for i, w in enumerate(words):
        n = norm(w["w"])
        w["filler"] = n in FILLERS
        w["func"] = n in FUNC
        if z is not None:
            w["db"] = round(float(lv[i]), 1)
            w["emph"] = bool(content[i] and z[i] > 1.0 and (w["e"] - w["s"]) >= 0.18)
            continue
        # text emphasis: numbers, long content words, a word before a pause or a full stop; at most one per 2 s
        gap = (words[i + 1]["s"] - w["e"]) if i + 1 < len(words) else 1.0
        score = (3 if any(c.isdigit() for c in n) else 0) + (1 if len(n) >= 7 else 0) + (2 if gap >= 0.25 else 0) + \
                (1 if w["w"][-1:] in ".!?," else 0)
        w["emph"] = bool(content[i] and score >= 3 and (w["e"] - w["s"]) >= 0.18 and w["s"] - last_emph >= 2.0)
        if w["emph"]:
            last_emph = w["s"]


def _range(words, beat) -> tuple[float, float]:
    if "in" in beat:
        return float(beat["in"]), float(beat["out"])
    i0 = _find(words, beat["from"], beat.get("from_s"))
    i1 = _find(words, beat["to"], beat.get("to_s"))
    if i1 < i0:
        raise SystemExit(f"beat {beat.get('beat')}: '{beat['to']}' comes before '{beat['from']}' in {beat['take']}")
    return words[i0]["s"], words[i1]["e"]


def assemble(spec_path: Path, out: Path, emphasis: str = "auto", faces: bool = True, stride: int = 2, model: str = "small.en",
             log=print) -> dict:
    from . import analyze as an_mod, track
    spec_path = spec_path.resolve()
    base = spec_path.parent
    spec = json.loads(spec_path.read_text())
    out.mkdir(parents=True, exist_ok=True)
    rp = lambda p: (Path(p) if Path(p).is_absolute() else (base / p)).resolve()

    takes = {}
    for tid, t in spec["takes"].items():
        video = rp(t["video"])
        if t.get("words"):
            words, sil = _words_from_map(rp(t["words"]))
            src = "map"
        else:
            d = an_mod.analyze(video, out / "takes" / tid, model=model, faces=False, log=log)
            words, sil, src = d["words"], [tuple(s) for s in d["silences"]], "whisper"
        takes[tid] = {"video": video, "words": words, "sil": sil, "info": probe(video), "src": src}

    # ranges in script order, frame-aligned
    ranges, t_sel = [], 0.0
    for b in spec["beats"]:
        tk = takes[b["take"]]
        s, e = _range(tk["words"], b)
        a = max(0.0, s - PAD_IN)
        z = min(tk["info"]["dur"], e + PAD_OUT)
        nxt = [w["s"] for w in tk["words"] if w["s"] > e + 0.01]
        if nxt:
            z = min(z, nxt[0] - 0.02)            # never carry the start of the next word
        prv = [w["e"] for w in tk["words"] if w["e"] < s - 0.01]
        if prv:
            a = max(a, prv[-1] + 0.02)
        fa, fz = round(a * FPS), round(z * FPS)
        a, z = fa / FPS, fz / FPS
        ranges.append({"beat": b.get("beat", ""), "take": b["take"], "src_in": round(a, 4), "src_out": round(z, 4),
                       "sel_in": round(t_sel, 4), "sel_out": round(t_sel + (z - a), 4)})
        t_sel += z - a

    # the selects file: each beat encoded on its own (accurate seek, frame exact, source size kept, PCM audio), then joined
    # without re-encoding. One filter graph over every range buffers too many 4K frames and runs out of memory.
    sel = out / "selects.mkv"
    parts = out / "parts"
    parts.mkdir(exist_ok=True)
    used = sorted({r["take"] for r in ranges})

    def enc(k_r):
        k, r = k_r
        dst = parts / f"p{k:03d}.mkv"
        stamp = parts / f"p{k:03d}.json"
        sig = json.dumps({"video": str(takes[r["take"]]["video"]), "in": r["src_in"], "out": r["src_out"]})
        if dst.exists() and stamp.exists() and stamp.read_text() == sig:
            return dst                                   # same take, same range: reuse the encoded part
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{r['src_in']:.4f}", "-i", str(takes[r["take"]]["video"]),
                        "-t", f"{r['src_out'] - r['src_in']:.4f}", "-map", "0:v:0", "-map", "0:a:0", "-r", str(FPS),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-pix_fmt", "yuv420p",
                        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(dst)], check=True)
        stamp.write_text(sig)
        return dst

    log(f"{len(ranges)} beats from {len(used)} takes, {t_sel:.1f} s; writing the selects file ...")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as ex:
        files = list(ex.map(enc, enumerate(ranges)))
    (out / "parts.txt").write_text("".join(f"file '{f}'\n" for f in files))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(out / "parts.txt"), "-c", "copy", str(sel)], check=True)
    # the real clock of the joined file: re-base every range on the frame counts actually written
    t = 0.0
    for r, f in zip(ranges, files):
        n = int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                                "-of", "csv=p=0", str(f)], capture_output=True, text=True, check=True).stdout.strip())
        r["frames"] = n
        r["sel_in"], r["sel_out"] = round(t, 4), round(t + n / FPS, 4)
        r["src_out"] = round(r["src_in"] + n / FPS, 4)
        t += n / FPS

    # words, silences and hard cuts on the selects clock
    words, sil, hard = [], [], []
    for r in ranges:
        tk = takes[r["take"]]
        off = r["sel_in"] - r["src_in"]
        for w in tk["words"]:
            if w["s"] >= r["src_in"] - 1e-3 and w["e"] <= r["src_out"] + 1e-3:
                nw = {k: v for k, v in w.items() if k in ("w", "p")}
                nw.update({"s": round(w["s"] + off, 3), "e": round(w["e"] + off, 3), "beat": r["beat"], "take": r["take"]})
                words.append(nw)
        for a, b in tk["sil"]:
            a2, b2 = max(a, r["src_in"]), min(b, r["src_out"])
            if b2 - a2 >= 0.05:
                sil.append((round(a2 + off, 3), round(b2 + off, 3)))
        if r["sel_in"] > 0:
            hard.append(r["sel_in"])
    # each beat starts a sentence on screen and in the SRT: capital first letter, and the line before it ends with a stop
    starts = {r["sel_in"] for r in ranges}
    for i, w in enumerate(words):
        first = i == 0 or any(words[i - 1]["e"] <= s0 <= w["s"] + 1e-3 for s0 in starts)
        if first and w["w"][:1].islower():
            w["w"] = w["w"][0].upper() + w["w"][1:]
            if i > 0 and words[i - 1]["w"][-1:] not in ".?!":
                words[i - 1]["w"] = words[i - 1]["w"].rstrip(",;:") + "."

    info = probe(sel)
    a = None
    if emphasis == "audio" or (emphasis == "auto" and any(takes[t]["src"] == "whisper" for t in used)):
        a = an_mod._audio(sel, 0.0, info["dur"])
    _flags(words, a)
    sents = an_mod.sentences(words)
    d = {"key": {"video": str(sel), "imported": True}, "imported": True, "video": str(sel), "start": 0.0, "end": info["dur"],
         "dur": info["dur"], "w": info["w"], "h": info["h"], "src_fps": info["fps"], "words": words, "silences": sil,
         "sentences": sents, "moments": an_mod.moments(words, sents), "hard_cuts": hard, "beats": ranges,
         "emphasis_from": "audio" if a is not None else "text",
         "stats": {"words": len(words), "fillers": sum(w["filler"] for w in words), "emphasis": sum(w["emph"] for w in words),
                   "speech_s": round(sum(w["e"] - w["s"] for w in words), 1)}}
    if faces:
        log("tracking the face ...")
        tr = track.detect(sel, 0.0, info["dur"], stride=stride, log=log)
        cuts = sorted(set([round(c, 3) for c in tr["cuts"]] + [round(h, 3) for h in hard]))
        d["track"] = {k: tr[k] for k in ("fps", "w", "h", "stride", "dets", "coverage")}
        d["track"]["cuts"] = cuts
    d["key"]["mtime"] = sel.stat().st_mtime
    save_json(out / "analysis.json", d)
    save_json(out / "selects.json", {"spec": str(spec_path), "ranges": ranges, "words_from": {t: takes[t]["src"] for t in used}})
    (out / "transcript.txt").write_text("\n".join(f"[{s['s']:7.2f}] {s['text']}" for s in sents) + "\n")
    log(f"selects: {sel} ({info['dur']:.1f} s, {len(words)} words, {len(hard)} take changes, emphasis from {d['emphasis_from']})")
    return d
