# AUDIT: vsl-builder

| Claim | Status | Source |
|---|---|---|
| `tools/closer.py assemble`, `longform --layers`, `formats` | RUN | `tools/studio/cli.py` (assemble and longform parsers); assembled and cut the SMA website VSL v8 from three 4K takes on 2026-11-01 (19 beats, 18 take changes) |
| `bash install.sh --scenes` installs Node.js and Playwright's Chromium for the scenes | RUN | `install.sh` section 6; `tools/vsl/mg/package.json` pins playwright 1.63.0 |
| A take with a word map is not re-transcribed; others are transcribed once and cached | RUN | `tools/studio/assemble.py` (`_words_from_map`, `analyze` per take into `<out>/takes/`); `tools/studio/analyze.py` reuses an imported analysis beside the selects file |
| `from_s` / `to_s` pick the nearest occurrence of the word | RUN | `tools/studio/assemble.py` `_find` |
| Beat starts are capitalised; a take change is a hard cut; the camera snaps there | RUN | `tools/studio/assemble.py` (capitalisation, `hard_cuts`, track cuts); `tools/studio/cut.py` `build(hard=...)`; `tools/studio/track.py` camera snaps at `cuts` |
| Selects file frame exact at the source resolution | RUN | `tools/studio/assemble.py` per-beat encode with accurate seek, x264 crf 12, joined with stream copy; frame counts re-read to re-base the clock |
| Anchor forms: word@time, :end, +/- seconds (the example is 80 ms), END, SPEECH_END | RUN | `tools/studio/layers.py` `ANCHOR`, `_src`, `anchor` |
| Layers parts: scenes (overlay layout, END as end card), lockup, captions, chips (quiet, pointer), hands, moments, music, sfx, kicks, zoom, end_hold | RUN | `tools/studio/layers.py` and `tools/studio/longform.py` (layers wiring), all used in `vsl/v8/layers_v8.json` of the sellmoreannuities repo |
| Scenes render once and are reused while length and cues match | RUN | `tools/vsl/mg/render.js` cache key (scene, dur, alpha, cues) |
| `vsl_hero` about 100 s, 16:9, burned captions, music faint; `vsl_book_call` for a longer page VSL | RUN | `formats.json` entries `vsl_hero` (60 / 100 / 150 s, web_vsl, impact, faint) and `vsl_book_call` |
| Check cards at 360 px wide | INFERRED | house rule from the five-reviewer panel on SMA VSL v7 (2026-11-01): the homepage plays in a phone player about 358 px wide |
| Full-screen cards about half the runtime or less | INFERRED | the same panel (v7 had 53% cards, rated a slideshow from 48 to 79 s); `FORMATS.md` vsl_book_call keeps cutaways under 40% (SupoClip planner rule) |
| Blind A/B with labels A and B only | INFERRED | house method; run on SMA VSL v8 against v7 on 2026-11-01 |
| No unsourced number on screen; a caption is fixed by cutting audio, never by rewording | USER / VERIFIED | `HOUSE_RULES.md`; the owner's audit rules in `skills/video/vsl-producer/SKILL.md` |
| Example times in the spec and the anchor table (5.7, 13.5, 19.0, 36.8, 42.4 s) | RUN | word times from the SMA takes' frame maps (`vsl/frame_map/take2.json`, `take3.json` in the sellmoreannuities repo); illustrative only |
| `cut_in` / `cut_out` hard cuts; moment card with big number and label; one caption line at a time; `--crf 15` for the master; card content above the caption band | RUN / INFERRED | `tools/studio/layers.py` (hard_in, hard_out, dict card), `tools/studio/captions.py` (chunk end clamped to the next chunk), `tools/studio/cli.py` `--crf`; the caption-band rule is the blind A/B panel's fix 1 on SMA VSL v8 (2026-11-02, 4 of 5 reviewers) |
