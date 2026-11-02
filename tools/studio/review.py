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
    if s.get("kind") == "long":
        return run_long(job, j, log)
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
    if s.get("format"):
        add("length fits the format", not s.get("length_warning"), s.get("length_warning") or f"{info['dur']:.0f} s is inside the {s['format']} band")
    m = voice.measure(final, plat["lufs"], plat["tp"])
    add("loudness on target", abs(m["i"] - plat["lufs"]) <= 1.0 and m["tp"] <= plat["tp"] + 0.3, f"{m['i']:.1f} LUFS, {m['tp']:.1f} dBTP (target {plat['lufs']} / {plat['tp']})")
    ok, det = sync_check(final, an, segs)
    add("sound in sync with the picture", ok, det)
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
    off = brands.check_copy(brand, txt + " " + (s.get("hook") or ""), s.get("audience"))
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


def run_long(job: Path, j: dict, log=print) -> dict:
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
    first_t = max(0.0, segs[0]["out_t"] + (words[segs[0]["w0"]]["s"] - segs[0]["in"])) if an else 0.0
    add(f"opens by {s['hook_deadline_s']} s", first_t <= s["hook_deadline_s"], f"first word at {first_t:.2f} s")
    tail = info["dur"] - s["speech_s"]
    lim = max(3.0, float(s.get("end_hold") or 0) + 0.3)
    add("ends on the payoff", tail <= lim, f"{tail:.1f} s after the last word (end card {s.get('end_hold') or 2.5:.1f} s)")
    if s["change_every_s"] > 0:
        add(f"a layout change at least every {s['change_every_s']:.0f} s", not s["layout_gaps_over_limit"],
            f"gaps: {s['layout_gaps_over_limit']}" if s["layout_gaps_over_limit"] else f"{len(s['cutaways'])} cutaways on the cadence")
    else:
        add("no layout cadence required", True, "this format is a single take (change_every_s 0)")
    stat = cutmod.static_stretches(segs, 8.0)
    add("no static stretch over 8 s", not stat, f"{stat}" if stat else "framing changes at least every 8 s")
    add("length fits the format", not s.get("length_warning"), s.get("length_warning") or f"{info['dur']:.0f} s")
    m = voice.measure(final, plat["lufs"], plat["tp"])
    add("loudness on target", abs(m["i"] - plat["lufs"]) <= 1.0 and m["tp"] <= plat["tp"] + 0.3, f"{m['i']:.1f} LUFS, {m['tp']:.1f} dBTP")
    ok, det = sync_check(final, an, segs)
    add("sound in sync with the picture", ok, det)
    add("chapters written by a person", not s.get("auto_chapter_titles"), "chapters.txt has placeholder titles: write real ones and re-run" if s.get("auto_chapter_titles") else (f"{len(s['chapters'])} chapters" if s["chapters"] else "no chapters (fine under 4 min)"))
    add("every quote found in the speech", not s.get("missing_quotes"), f"not found: {s.get('missing_quotes')}" if s.get("missing_quotes") else "all matched")
    txt = (job / "captions.srt").read_text() if (job / "captions.srt").exists() else ""
    off = brands.check_copy(brand, txt, s.get("audience"))
    add("no banned words in the speech", not off, f"found in the transcript: {off} (a cut or a bleep, or the brand allows it)" if off else "clean")
    low = [w["w"] for w in words if w.get("p", 1) < 0.5]
    if an and an.get("imported"):
        add("caption words to proofread", True, f"words from a locked word map (proofed in the source project); low-confidence: {low[:12]}")
    else:
        add("caption words to proofread", len(low) <= 5, f"low-confidence words: {low[:12]}" if low else "none")
    extra_checks(job, add)
    sheet = contact_sheet(final, job / "sheet.jpg", every=max(2.0, info["dur"] / 48))
    report = {"file": str(final), "duration_s": round(info["dur"], 2), "checks": checks, "sheet": str(sheet), "passed": all(c["ok"] for c in checks)}
    json.dump(report, open(job / "report.json", "w"), indent=1)
    md = [f"# Review: {final.name}", "", f"{info['dur']:.0f} s, {plat['name']}, format {s['format']}, brand {brand['name']}", ""]
    md += [f"- {'PASS' if c['ok'] else 'FIX '}  {c['check']}: {c['detail']}" for c in checks]
    md += ["", f"Contact sheet: {sheet}", f"Chapters: {job / 'chapters.txt'}", f"Thumbnail: {s['cover']['thumbnail']}", ""]
    (job / "report.md").write_text("\n".join(md) + "\n")
    for c in checks:
        log(f"{'PASS' if c['ok'] else 'FIX '}  {c['check']}: {c['detail']}")
    return report

def sync_check(final, an, segs, sr: int = 8000) -> tuple[bool, str]:
    """Picture and sound together: each piece's audio in the final is cross-correlated against the source at the same
    place. A stale or shifted voice track shows as a lag far from the rest, or as no match at all."""
    import subprocess
    if not an:
        return True, "no analysis to check against"
    src, start = an["video"], an.get("start", 0.0)

    def pcm(f, ss, d):
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{d:.3f}", "-i", str(f), "-vn", "-ac", "1", "-ar", str(sr),
                            "-f", "s16le", "-"], capture_output=True).stdout
        return np.frombuffer(b, np.int16).astype(np.float32)
    rows = []
    for sg in segs:
        if sg["frames"] / FPS < 1.0:
            continue
        best = None
        for off in sorted({0.25, round(max(0.25, sg["frames"] / FPS / 2 - 0.3), 2)}):   # a soft word under music can hide one window
            a, b = pcm(final, sg["out_t"] + off, 0.6), pcm(src, start + sg["in"] + off - 0.15, 0.9)
            if len(a) < 100 or len(b) < len(a) or a.std() < 1e-3:
                continue
            a, b = (a - a.mean()) / (a.std() + 1e-6), (b - b.mean()) / (b.std() + 1e-6)
            c = np.correlate(b, a, mode="valid") / len(a)
            i = int(np.argmax(c))
            if best is None or c[i] > best[2]:
                best = (sg["out_t"], (i / sr - 0.15) * 1000, float(c[i]))
        if best:
            rows.append(best)
    if not rows:
        return True, "no piece long enough to check"
    med = float(np.median([r[1] for r in rows]))
    bad = [r for r in rows if abs(r[1] - med) > 40 or r[2] < 0.2]
    detail = f"{len(rows)} pieces, offset {med:.0f} ms" + (f"; out of step or not matching at {[round(r[0], 1) for r in bad]} s" if bad else ", none drifting")
    return len(bad) <= max(0, len(rows) // 20), detail


def extra_checks(job: Path, add):
    """Checks on what the placement engine, the sound director and the finish pass wrote (when they ran)."""
    pj = job / "placement.json"
    if pj.exists():
        placed = json.loads(pj.read_text()).get("placed", [])
        bad = [p for p in placed if not p.get("ok", True)]
        add("graphics clear of the face and the captions", not bad,
            "; ".join(f"{p['label']} at {p['a']} s: face {p['face_overlap']:.0%}, captions {p['caption_overlap']:.0%}" for p in bad[:6]) if bad
            else f"{len(placed)} placed elements, none on the face or the captions")
    sj = job / "sound.json"
    if sj.exists():
        r = json.loads(sj.read_text())
        q = r.get("qc", {})
        if "voice_over_music_median_db" in q:
            add("voice clear of the music", q.get("music_ok", False),
                f"voice over music: median {q['voice_over_music_median_db']} dB, worst 5 % {q['voice_over_music_p5_db']} dB (want >= 15 and >= 9)")
        add("no clicks at the audio cuts", q.get("click_suspects", 0) == 0, f"{q.get('click_suspects', 0)} suspects")
        per_min = r.get("sfx", {}).get("per_min", 0)
        add("sound effects stay rare", per_min <= 12, f"{per_min} per minute (budget 12; dropped {len(r.get('sfx', {}).get('dropped', []))})")
    fj = job / "finish.json"
    if fj.exists():
        st = json.loads(fj.read_text()).get("stats", {})
        add("finish pass measured the footage", True, f"face luma {st.get('face_luma')}, sky {st.get('sky_luma')}, clipped {st.get('clipped_share')}")
