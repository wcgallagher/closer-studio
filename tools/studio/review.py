"""Review: the checks a careful editor runs before calling a video done, written to report.md."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import brands, cut as cutmod, platforms, track as trk, voice
from .common import FPS, probe, sh


def contact_sheet(video: Path, out: Path, every: float = 1.0, cols: int = 8, rows: int = 6, w: int = 216):
    sh(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"fps=1/{every},scale={w}:-2,tile={cols}x{rows}", "-frames:v", "1", out])
    return out


def run(job: Path, log=print) -> dict:
    j = json.load(open(job / "job.json"))
    s, segs = j["summary"], j["segs"]
    an = json.load(open(job / "analysis.json")) if (job / "analysis.json").exists() else None
    plat = platforms.get(s["platform"])
    brand = brands.load(s["brand"])
    final = Path(s["file"])
    info = probe(final)
    checks = []

    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    words = an["words"] if an else []
    first_t = segs[0]["out_t"] + (words[segs[0]["w0"]]["s"] - segs[0]["in"]) if an else 0.0
    add("hook by 2.5 s", first_t <= 2.5, f"first word at {max(0.0, first_t):.2f} s")
    tail = info["dur"] - s["speech_s"]
    add("ends on the payoff", tail <= 2.3, f"{tail:.1f} s after the last word (end card is 2.0 s)")
    stat = cutmod.static_stretches(segs, 8.0)
    add("no static stretch over 8 s", not stat, f"{stat}" if stat else "framing changes at least every 8 s")
    add("length fits the platform", not plat["max_s"] or info["dur"] <= plat["max_s"], f"{info['dur']:.1f} s (limit {plat['max_s'] or 'none'} s)")
    m = voice.measure(final, plat["lufs"], plat["tp"])
    add("loudness on target", abs(m["i"] - plat["lufs"]) <= 1.0 and m["tp"] <= plat["tp"] + 0.3, f"{m['i']:.1f} LUFS, {m['tp']:.1f} dBTP (target {plat['lufs']} / {plat['tp']})")
    # face vs the caption block actually used
    pl = s.get("placement") or {}
    if an and an.get("track") and s.get("camera") == "tracked":
        from . import captions as capmod
        tr = dict(an["track"]); tr["dur"] = an["dur"]
        cam = trk.camera(tr, plat["w"], plat["h"], face_y=pl.get("face_y", 0.40))
        if pl.get("captions", "bottom") == "bottom":
            cap_top = capmod.text_top(plat["h"], s["style"], pl.get("band_bottom", platforms.caption_band(plat)[1]), 2)
            bad, n = 0, 0
            for sg in segs:
                z = sg["zoom"] * 1.05
                for t in np.arange(sg["in"], sg["in"] + sg["frames"] / FPS, 0.5):
                    box = trk.face_box_out(tr, cam, t)
                    if box is None:
                        continue
                    n += 1
                    chin = (box[1] + box[3] - (1 - 1 / z) * plat["h"] * 0.33) * z
                    if chin + 10 > cap_top:
                        bad += 1
            add("captions clear of the face", n == 0 or bad / n <= 0.05, f"{bad}/{n} samples had the chin inside the caption block (block top {cap_top} px)")
        else:
            add("captions clear of the face", True, "captions placed in the top zone (the face fills the frame)")
    else:
        add("captions clear of the face", True, "static camera: check the contact sheet by eye")
    txt = (job / "captions.srt").read_text() if (job / "captions.srt").exists() else ""
    off = brands.check_copy(brand, txt + " " + (s.get("hook") or ""))
    add("no banned words on screen", not off, f"found: {off}" if off else "clean")
    low = [w["w"] for w in words if w.get("p", 1) < 0.5]
    add("caption words to proofread", len(low) <= 3, f"low-confidence words: {low[:12]}" if low else "none")
    sheet = contact_sheet(final, job / "sheet.jpg")
    report = {"file": str(final), "duration_s": round(info["dur"], 2), "checks": checks, "sheet": str(sheet), "passed": all(c["ok"] for c in checks)}
    json.dump(report, open(job / "report.json", "w"), indent=1)
    md = [f"# Review: {final.name}", "", f"{info['dur']:.1f} s, {plat['name']}, brand {brand['name']}, captions {s['style']}", ""]
    md += [f"- {'PASS' if c['ok'] else 'FIX '}  {c['check']}: {c['detail']}" for c in checks]
    md += ["", f"Contact sheet: {sheet}", "", "Cold review: open the contact sheet and the file, then answer the three questions in skills/video/cold-review/SKILL.md."]
    (job / "report.md").write_text("\n".join(md) + "\n")
    for c in checks:
        log(f"{'PASS' if c['ok'] else 'FIX '}  {c['check']}: {c['detail']}")
    return report
