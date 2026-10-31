# AUDIT: reel-editor

| Claim | Status | Source |
|---|---|---|
| `tools/closer.py` and the `tools/studio/` engine (analyze, cut, track, captions, voice, grade, render, review) | RUN | files in this kit; `closer reel` ran end to end on a 28 s window of take3 (3840x2160 source) on 2026-10-31, tracked camera, ig_reels output |
| `~/.closer-studio/kit_path`, `~/.closer-studio/venv` | RUN | written by `install.sh` |
| 0.35 s dead-air cut, 100 / 110 / 120 % punch-ins, one crop anchor (0.33), 2.6 s hook, 2 s end card, 1.05x speed ceiling | RUN | constants in `tools/studio/cut.py` (GAP_MAX, ZOOMS), `tools/studio/render.py` (KY, HOLD_S), `tools/studio/captions.py` (hook_end) |
| hook by 2.5 s, no static stretch over 8 s, payoff ending, caption band | VERIFIED | writepanda.ai retention study (22 videos, July 2026), rows in `RESEARCH.md`; checks in `tools/studio/review.py` |
| 50 % face coverage threshold for the tracked camera | RUN | `tools/studio/render.py` falls back to the static crop under 0.5 coverage |
| 18 to 45 s windows, 4 to 7 word hooks | INFERRED | house choices from the SMA VSL and Hormozi measurements (1 idea every 3 to 7 s); adjust on results |
| platform safe zones and loudness targets | VERIFIED | `tools/studio/platforms.py` docstring: Meta Reels ad specs, Google Ads vertical safe zones, TikTok in-feed template |
| DeepFilterNet optional pre-pass | VERIFIED | Rikorose/DeepFilterNet v0.5.6 release assets (macOS arm64 / x86_64, Linux, Windows binaries), checked 2026-10-31 |
| "Results vary" line; no "free" / "guarantee" / "no cost" for Become The Closer | VERIFIED / USER | becomethecloser.com testimonials disclaimer (scrape 2026-10-30); the Become The Closer connector rules restated by the owner |
