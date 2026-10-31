"""closer: the one command. `python3 tools/closer.py <command> ...`"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import analyze as an_mod, brands, grade, platforms, render, review


def _an(video: Path, out: Path, a):
    d = an_mod.analyze(video, out, a.start, a.end, a.model, faces=(a.camera != "static"), stride=a.stride)
    return d


def cmd_analyze(a):
    video, out = Path(a.video).resolve(), Path(a.out).resolve()
    d = _an(video, out, a)
    st = d["stats"]
    print(f"{st['words']} words, {st['fillers']} fillers, {st['emphasis']} emphasised, {st['speech_s']} s of speech"
          + (f", face in {d['track']['coverage']:.0%} of frames, {len(d['track']['cuts'])} cuts" if d.get("track") else ""))
    print("\nbest windows (start-end, score, opening line):")
    for m in d["moments"]:
        print(f"  {m['s']:7.2f}-{m['e']:7.2f}  {m['dur']:4.0f}s  {m['score']:4.1f}  {m['hook_line'][:90]}")
    print(f"\ntranscript: {out / 'transcript.txt'}")


def cmd_reel(a):
    video, out = Path(a.video).resolve(), Path(a.out).resolve()
    brand = brands.load(a.brand)
    style = a.style or brand["style"].get("captions", "impact")
    d = _an(video, out, a)
    results = []
    for pid in a.platform.split(","):
        plat = platforms.get(pid.strip(), a.safe)
        job = out if len(a.platform.split(",")) == 1 else out / plat["id"]
        if job != out:
            job.mkdir(parents=True, exist_ok=True)
            (job / "analysis.json").write_text(json.dumps(d))
        s = render.reel(video, job, d, brand, plat, style=style, hook=a.hook, cta=a.cta, music=a.music or (brand["style"].get("music") or None),
                        grade_preset=a.grade, mode=a.camera, face=(a.face_x, a.face_y), preview=a.preview, fillers=a.fillers,
                        keep_silence=a.keep_silence, sfx=not a.no_sfx, riser=a.riser, voice_chain=a.voice, denoise=a.denoise,
                        caps_max=a.caps_max, hook_serif=a.hook_serif)
        results.append(s)
        if not a.no_review:
            review.run(job)
    print(json.dumps(results, indent=1))


def cmd_reframe(a):
    plat = platforms.get(a.platform)
    r = render.reframe(Path(a.video).resolve(), Path(a.out).resolve(), plat, a.start, a.end, zoom=("auto" if a.zoom == "auto" else float(a.zoom)),
                       per_scene=a.per_scene, stride=a.stride, preview=a.preview)
    print(json.dumps(r))


def cmd_export(a):
    rows = render.export(Path(a.master).resolve(), Path(a.out).resolve(), [platforms.get(p) for p in a.platforms.split(",")])
    print(json.dumps(rows, indent=1))


def cmd_review(a):
    review.run(Path(a.job).resolve())


def cmd_brands(a):
    for b in brands.list_brands():
        d = brands.load(b)
        print(f"{b:<8} {d['name']:<22} accent {d['colors']['accent']}  captions {d['style']['captions']}  grade {d['style']['lut']}  cta '{d['cta']['line']}'")


def cmd_platforms(a):
    print(platforms.table())


def cmd_lut(a):
    print(grade.lut_path(a.preset))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="closer", description="Closer Studio: raw clips in, platform-ready edits out.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("video"); p.add_argument("--out", required=True)
        p.add_argument("--start", type=float, default=0.0); p.add_argument("--end", type=float, default=None)
        p.add_argument("--model", default="small.en", help="faster-whisper model: tiny.en, base.en, small.en, medium.en")
        p.add_argument("--camera", default="track", choices=["track", "static"], help="face-tracked crop or a fixed crop")
        p.add_argument("--stride", type=int, default=2, help="detect the face every N frames")

    p = sub.add_parser("analyze", help="transcribe, find pauses, fillers, emphasis, faces and the best windows"); common(p); p.set_defaults(f=cmd_analyze)
    p = sub.add_parser("reel", help="finished reel(s) from a clip"); common(p)
    p.add_argument("--platform", default="ig_reels", help="comma list: ig_reels,tiktok,yt_shorts,ig_feed,linkedin,square,x,youtube")
    p.add_argument("--brand", default="btc"); p.add_argument("--style", default=None, help="captions: impact, clean, serif, boxed")
    p.add_argument("--hook", default=""); p.add_argument("--hook-serif", action="store_true"); p.add_argument("--cta", default=None)
    p.add_argument("--music", default=None); p.add_argument("--grade", default=None, help="sma_pro, btc_ember, clean, cinematic, none")
    p.add_argument("--face-x", type=float, default=0.5); p.add_argument("--face-y", type=float, default=0.38)
    p.add_argument("--fillers", default="keep", choices=["keep", "cut"]); p.add_argument("--keep-silence", action="store_true")
    p.add_argument("--no-sfx", action="store_true"); p.add_argument("--riser", action="store_true")
    p.add_argument("--voice", default="v3", choices=["v3", "light", "none"]); p.add_argument("--denoise", default="chain", choices=["chain", "deep"])
    p.add_argument("--caps-max", type=int, default=None); p.add_argument("--preview", action="store_true"); p.add_argument("--no-review", action="store_true")
    p.add_argument("--safe", default="organic", choices=["organic", "ads"], help="UI safe zones: a normal post (organic) or an ad placement")
    p.set_defaults(f=cmd_reel)
    p = sub.add_parser("reframe", help="auto-reframe any clip to a platform with face tracking")
    p.add_argument("video"); p.add_argument("--out", required=True); p.add_argument("--platform", default="ig_reels")
    p.add_argument("--start", type=float, default=0.0); p.add_argument("--end", type=float, default=None)
    p.add_argument("--zoom", default="auto"); p.add_argument("--per-scene", action="store_true"); p.add_argument("--stride", type=int, default=2)
    p.add_argument("--preview", action="store_true"); p.set_defaults(f=cmd_reframe)
    p = sub.add_parser("export", help="re-encode a master for other platforms of the same aspect")
    p.add_argument("master"); p.add_argument("--out", required=True); p.add_argument("--platforms", required=True); p.set_defaults(f=cmd_export)
    p = sub.add_parser("review", help="run the checks on a finished job folder"); p.add_argument("job"); p.set_defaults(f=cmd_review)
    p = sub.add_parser("brands", help="list brands"); p.set_defaults(f=cmd_brands)
    p = sub.add_parser("platforms", help="platform sizes and safe zones"); p.set_defaults(f=cmd_platforms)
    p = sub.add_parser("lut", help="write a grade preset as a .cube file"); p.add_argument("preset"); p.set_defaults(f=cmd_lut)
    a = ap.parse_args(argv)
    a.f(a)
