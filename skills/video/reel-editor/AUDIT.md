# AUDIT: reel-editor

| Claim | Status | Source |
|---|---|---|
| `tools/reel_build.py`, `tools/transcribe.py`, `tools/vsl/luts/sma_pro.cube`, `tools/music_industrial_cinematic.mp3` | RUN | files in this kit; reel_build.py ran end to end on a 14 s window of take2 on 2026-10-30 (15.6 s reel, 1080x1920, 4 cuts) |
| `~/.closer-studio/kit_path`, `~/.closer-studio/venv` | RUN | written by `install.sh` |
| 2.6 s hook, 0.35 s dead-air cut, 100 / 110 / 120% punch-ins, one crop anchor, 500 Hz / 2.2 kHz voice cuts, 2 s end card, -14 LUFS, 320 px bottom margin | RUN | constants in `tools/reel_build.py` (HOOK_END, GAP_MAX, ZOOMS, KY, VOICE, HOLD_S, captions MarginV 520) |
| 20 to 45 s reels, 4 to 7 word hooks, 1.05x speed ceiling | INFERRED | house choices from the SMA VSL work; adjust on results |
| Hook lines ("I want to think about it is stealing your commissions", "There are only four types of closers") | VERIFIED | becomethecloser.com home page, scraped 2026-10-30 (see `brand/becomethecloser.md`) |
| "Results vary" line | VERIFIED | becomethecloser.com testimonials disclaimer, same scrape |
| No "free" / "guarantee" / "no cost" for Become The Closer | USER | the Become The Closer connector's own rules, restated by the owner's team; the SMA account is free per the owner (2026-10-30) |
| 1080x1920, 30 fps, 4 cuts, 15.6 s test | RUN | ffprobe on the test render 2026-10-30 |
