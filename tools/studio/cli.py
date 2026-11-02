"""closer: the one command. `python3 tools/closer.py <command> ...`"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import analyze as an_mod, assemble as asm, brands, cover as cover_mod, formats, grade, longform as long_mod, platforms, render, review


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
    fmt = formats.get(a.format) if a.format else None
    style = a.style or (fmt["captions"] if fmt and fmt["captions"] in ("impact", "clean", "serif", "boxed") else None) or brand["style"].get("captions", "impact")
    safe = a.safe or (fmt["safe"] if fmt else "organic")
    fillers = a.fillers or (fmt["fillers"] if fmt else "keep")
    end_card = not (fmt and fmt.get("cta") == "none")
    d = _an(video, out, a)
    windows = [(a.start, d["end"], out)]
    if a.auto:
        windows = []
        for k, m in enumerate(d["moments"][:a.auto]):
            windows.append((m["s"] + d["start"], m["e"] + d["start"], out / f"auto_{k + 1}"))
            print(f"auto {k + 1}: {m['s']:.1f}-{m['e']:.1f} s  {m['hook_line'][:80]}")
    results = []
    for (ws, we, wout) in windows:
        if a.auto:
            sub = argparse.Namespace(**vars(a)); sub.start, sub.end = ws, we
            dd = _an(video, wout, sub)
        else:
            dd = d
        if fmt:
            warn = formats.check_length(fmt, dd["dur"])
            if warn:
                print(f"note: {warn}")
        for pid in a.platform.split(","):
            plat = platforms.get(pid.strip(), safe)
            job = wout if len(a.platform.split(",")) == 1 else wout / plat["id"]
            if job != wout:
                job.mkdir(parents=True, exist_ok=True)
                (job / "analysis.json").write_text(json.dumps(dd))
            s = render.reel(video, job, dd, brand, plat, style=style, hook=a.hook if not a.auto else "", cta=a.cta,
                            music=a.music or (brand["style"].get("music") or None), grade_preset=a.grade, mode=a.camera, face=(a.face_x, a.face_y),
                            preview=a.preview, fillers=fillers, keep_silence=a.keep_silence, sfx=not a.no_sfx, riser=a.riser, voice_chain=a.voice,
                            denoise=a.denoise, caps_max=a.caps_max, hook_serif=a.hook_serif, end_card=end_card, fmt=fmt, audience=a.audience)
            results.append(s)
            if not a.no_review:
                review.run(job)
    print(json.dumps(results, indent=1))


def cmd_longform(a):
    video, out = Path(a.video).resolve(), Path(a.out).resolve()
    brand = brands.load(a.brand)
    fmt = formats.get(a.format)
    plat = platforms.get(a.platform or fmt["platforms"][0], fmt.get("safe", "organic"))
    d = _an(video, out, a)
    quotes = [q.strip() for q in a.quotes.split("|")] if a.quotes else None
    s = long_mod.longform(video, out, d, brand, plat, fmt, chapters=a.chapters, quotes=quotes, pops=a.pops, broll=Path(a.broll) if a.broll else None,
                          music=a.music, fillers=a.fillers, caps=a.captions, cta=a.cta, title=a.title, grade_preset=a.grade, preview=a.preview, denoise=a.denoise,
                          change_every=a.change_every, audience=a.audience, hold=a.hold, layers=Path(a.layers).resolve() if a.layers else None, crf_master=a.crf)
    if not a.no_review:
        review.run(out)
    print(json.dumps(s, indent=1, default=str))


def cmd_assemble(a):
    d = asm.assemble(Path(a.spec), Path(a.out).resolve(), emphasis=a.emphasis, faces=not a.no_faces, stride=a.stride, model=a.model)
    for r in d["beats"]:
        print(f"  {r['sel_in']:7.2f}-{r['sel_out']:7.2f}  {r['beat']:<12} {r['take']} {r['src_in']:.2f}-{r['src_out']:.2f}")
    print(f"\nnext: longform {Path(d['video'])} --out <job> (the analysis is reused; nothing is re-transcribed)")


def cmd_cover(a):
    src = Path(a.source).resolve()
    brand = brands.load(a.brand)
    an = None; video = src; start = 0.0; end = None
    if src.is_dir():
        an = json.loads((src / "analysis.json").read_text())
        video = Path(an["video"]); start, end = an["start"], an["end"]
    off = brands.check_copy(brand, a.title, a.audience)
    if off:
        sys.exit(f"the title uses words this brand never prints: {off}")
    r = cover_mod.build(video, Path(a.out).resolve(), brand, a.title, an, at=a.at, start=start, end=end)
    print(json.dumps(r))


def cmd_formats(a):
    print(formats.table())


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
    p.add_argument("--fillers", default=None, choices=["keep", "cut"]); p.add_argument("--keep-silence", action="store_true")
    p.add_argument("--no-sfx", action="store_true"); p.add_argument("--riser", action="store_true")
    p.add_argument("--voice", default="v3", choices=["v3", "light", "none"]); p.add_argument("--denoise", default="chain", choices=["chain", "deep"])
    p.add_argument("--caps-max", type=int, default=None); p.add_argument("--preview", action="store_true"); p.add_argument("--no-review", action="store_true")
    p.add_argument("--safe", default=None, choices=["organic", "ads"], help="UI safe zones: a normal post (organic) or an ad placement")
    p.add_argument("--format", default=None, help="organic_reel, paid_ad_reel, reminder_clip, testimonial_clip ... (see `formats`; older ids such as ad_reel still resolve)")
    p.add_argument("--audience", default=None, choices=["default", "client"], help="who watches: the brand's usual viewer, or the agent's own client (adds the brand's client-facing never-words)")
    p.add_argument("--auto", type=int, default=0, help="cut the N best windows the analysis found (no hook text; you add it after)")
    p.set_defaults(f=cmd_reel)
    p = sub.add_parser("longform", help="16:9 (or any) long-form master: YouTube, VSL, Skool lesson, replay, confirmation video"); common(p)
    p.add_argument("--brand", default="btc"); p.add_argument("--format", default="yt_authority"); p.add_argument("--platform", default=None)
    p.add_argument("--audience", default=None, choices=["default", "client"], help="who watches: the brand's usual viewer, or the agent's own client")
    p.add_argument("--chapters", default=None, help="'0:Title,95:Next title' in seconds from --start, or auto")
    p.add_argument("--quotes", default=None, help="spoken lines to show as quote cards, separated by |")
    p.add_argument("--pops", default="auto", help="auto, off, or the words to pop separated by |: \"four types|objection\"")
    p.add_argument("--broll", default=None, help="folder of clips for cutaways")
    p.add_argument("--captions", default=None, help="pops (default per format), none, or a burned style: impact, clean, serif, boxed")
    p.add_argument("--music", default=None); p.add_argument("--fillers", default=None, choices=["keep", "cut"]); p.add_argument("--cta", default=None)
    p.add_argument("--title", default=None, help="thumbnail title, 1 to 4 words"); p.add_argument("--grade", default=None)
    p.add_argument("--change-every", type=float, default=None, help="seconds between layout changes (default from the format)")
    p.add_argument("--crf", type=int, default=None, help="encode quality for the delivery (lower is better; default 18, 15 for a master)")
    p.add_argument("--layers", default=None, help="a layers JSON: animated scenes, chips, headline, proof card, moments, music, all anchored to words")
    p.add_argument("--hold", default=None, help="the verdict hold, 'a:b' seconds from the window start: no B-roll or pops inside it, and the cadence check skips it")
    p.add_argument("--denoise", default="chain", choices=["chain", "deep"]); p.add_argument("--preview", action="store_true"); p.add_argument("--no-review", action="store_true")
    p.set_defaults(f=cmd_longform)
    p = sub.add_parser("assemble", help="one selects file in script order from several takes (a spec of beats); reuses locked word maps")
    p.add_argument("spec"); p.add_argument("--out", required=True)
    p.add_argument("--emphasis", default="auto", choices=["auto", "audio", "text"], help="emphasised words from loudness or from the text (auto: text when every take has a word map)")
    p.add_argument("--no-faces", action="store_true"); p.add_argument("--stride", type=int, default=2); p.add_argument("--model", default="small.en")
    p.set_defaults(f=cmd_assemble)

    p = sub.add_parser("cover", help="thumbnail (1280x720) and cover (1080x1920) from the best face frame with a title")
    p.add_argument("source", help="a video file or a job folder"); p.add_argument("--title", required=True); p.add_argument("--brand", default="btc")
    p.add_argument("--out", required=True); p.add_argument("--at", type=float, default=None); p.add_argument("--audience", default=None, choices=["default", "client"])
    p.set_defaults(f=cmd_cover)
    p = sub.add_parser("formats", help="the format table (what a video is for decides how it is cut)"); p.set_defaults(f=cmd_formats)
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
