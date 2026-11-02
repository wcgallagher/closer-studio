# AUDIT: editor-brain

Written 2026-11-02, Mode 2 of `skills/core/zero-context-auditor/SKILL.md`; cold-reviewed and corrected the same day. The code is the source of truth for engine numbers: `tools/studio/edit.py` (`INTENT_RULES`, `DEFAULTS`), `tools/studio/cut.py`, `tools/studio/longform.py`, `tools/studio/render.py`, `tools/studio/grade.py`, `tools/studio/finish.py` (`FINISH_RULES`, `FINISH_PROFILES`), `tools/studio/placement.py` (`PLACEMENT_RULES`), `tools/studio/sound.py` (`SOUND_RULES`, `SECTION_PRESETS`), `tools/studio/review.py`, `tools/studio/compare.py`, `formats.json`. Line numbers are from the working tree on 2026-11-02. Research sources:

- RB = `docs/EDITOR_RULEBOOK.md`, cited by rule id (TY-05, AS-01, DA-1 ...) or by section. It keeps only rules with a public source or a house label.
- AS = `docs/AUDIO_SPEC.md`, cited by section.
- ARC = the emotional-arc research notes of 2026-11-02 (states, parameters and format overrides, every number tagged src, derived or house; plus the emotion-and-pacing and what-the-viewer-sees rule sweeps). The notes are held by the owner and are not in this repo, so every ARC row names the public paper or page the note cites, or says house or derived. No ARC rule used here has a proprietary source.
- RUN = commands run on 2026-11-02 with `/root/.closer-studio/venv/bin/python` (the kit venv) on Linux, ffmpeg 6.1.1. No Windows or Mac machine was available.
- WEB = pages fetched on 2026-11-02 (TOOL sources in the auditor's terms): the Homebrew formula API (formulae.brew.sh/api/formula/<name>.json), gyan.dev/ffmpeg/builds, the FFmpeg source tree (raw.githubusercontent.com/FFmpeg/FFmpeg, branches release/7.0, release/7.1, release/8.0, release/8.1, release/9.0 and master Changelog).

## 0. Start the job

| Claim | Status | Source |
|---|---|---|
| FFmpeg 9.0 removed `-filter_complex_script`; 8.1 and older still accept it | WEB | release/8.1 `fftools/ffmpeg_opt.c` has `filter_complex_script` under `#if FFMPEG_OPT_FILTER_SCRIPT` ("deprecated, use -/filter_complex instead"); release/9.0 `ffmpeg_opt.c` has no match and its `ffmpeg.h` defines no `FFMPEG_OPT_*` flags; release/7.0, 7.1 and 8.0 still have it with the same "deprecated" text |
| The engine passes `-filter_complex_script` | VERIFIED | `tools/studio/render.py` line 125 (every long-form piece), `tools/studio/longform.py` line 408 (the final encode) |
| `-/filter_complex` is the replacement | WEB | FFmpeg Changelog, version 7.0: "ffmpeg CLI options may now be used as -/opt <path>"; the 8.0 deprecation text above |
| Homebrew ships 9.0.2; plain `ffmpeg` has no libass | WEB | `ffmpeg.json` stable 9.0.2, dependencies without libass; `ffmpeg-full.json` 9.0.2, keg-only, with libass. Also RB XP-03 |
| gyan.dev ships 9.0.2; 8.1.2 is its previous release, essentials build has libass | WEB | `gyan.dev/ffmpeg/builds/release-version` returned 9.0.2; the builds page lists "previous release, version: 8.1.2" with `ffmpeg-8.1.2-essentials_build.zip` and its `.sha256`, and libass and libzimg under "libraries in essentials build" |
| `brew install ffmpeg@7` gives a keg-only 7.1.5 with libass | WEB | `ffmpeg@7.json`: stable 7.1.5, keg_only true, dependencies include libass, freetype, fontconfig, zimg |
| `export PATH="$(brew --prefix ffmpeg@7)/bin:$PATH"` | INFERRED | keg-only formulas are not linked into the Homebrew prefix, so the engine (which calls `ffmpeg` by name, `longform.py` `_run(["ffmpeg", ...])`) finds it only through PATH. Not run on a Mac |
| Ubuntu 24.04 apt ffmpeg 6.1.1 works | VERIFIED / RUN | RB XP-03 ("apt ffmpeg (6.1.1 on Ubuntu 24.04: has libass ...)"); every RUN here used ffmpeg 6.1.1 |
| KIT and PY lines | RUN | same lines as `skills/video/sound-director/SKILL.md` section 0; the venv python exists and ran `closer.py edit --help` (exit 0) |
| Windows: `powershell -ExecutionPolicy Bypass -File .\install.ps1`; venv at `$HOME\.closer-studio\venv\Scripts\python.exe`; kit path in `$HOME\.closer-studio\kit_path`; not yet run on Windows | VERIFIED, not RUN | `install.ps1` line 2 (the command), lines 26-28 (`$Py = Join-Path $Venv "Scripts\python.exe"`), line 59 (`Set-Content ... kit_path`), line 8 ("not yet run on a Windows machine"). `New-Item -ItemType Directory -Force -Path a, b` is the form install.ps1 uses at line 60 |
| `edit VIDEO "intent" --out --brand --music-dir --sfx-dir --no-render` | RUN | `closer.py edit --help` printed exactly these options; `tools/studio/cli.py` lines 226-230 |
| The kit ships no `music` or `sfx` folder | RUN | `ls -d music sfx` in the kit: no such file or directory |
| Empty music folder: no bed, no ranking | VERIFIED | `edit.py` `pick_music` returns `(None, [])` with no audio files (lines 69-83); `brand/btc.json` and `brand/sma.json` `"music": ""`, so `longform.py` line 348 finds no bed |
| Empty sfx folder: the synthesized set | VERIFIED | `sound.py` `Library.pick` returns `SYNTH[role]()` and `"synth"` when a role has no files |
| Effect files named `<role>__<name>.wav` | VERIFIED | `sound.py` `Library.__init__` (`"__" not in f.stem` skipped; role = text before `__`); AS section 6 |
| "a 90 second homepage VSL, premium" -> vsl_hero, gadzhi, 90 s | RUN | `edit.read_intent` returned `{'format': 'vsl_hero', 'dialect': 'gadzhi', 'length_s': 90}` |
| Format order (VSL, ad, reel, YouTube, lesson words); first rule that matches wins; nothing named = yt_authority | VERIFIED | `tools/studio/edit.py` lines 23-29 (`INTENT_RULES["format"]`, comment "first match wins"), lines 50-54 |
| Nothing named gets the brand finish with heavier grain | VERIFIED | `edit.py` `DEFAULTS["yt_authority"]["finish"] = "brand"`; `finish.py` `FINISH_PROFILES["brand"] = {}` falls back to `FINISH_RULES` grain 0.012 against vsl 0.007 |
| "make it cinematic" and "make it better" get yt_authority | RUN | `read_intent("make it cinematic")` -> yt_authority, gadzhi; `read_intent("make it better")` -> yt_authority |
| "an ad for my homepage" becomes a VSL | RUN | `read_intent("an ad for my homepage")` -> `{'format': 'vsl_hero'}` |
| Energy words checked before premium words; "premium but fast" gets the energy dialect | VERIFIED / RUN | `edit.py` lines 30-33, 55-58; `read_intent("a premium but fast VSL")` -> dialect `nelk` |
| Length recorded in `why.length_s`, nothing cuts to it | VERIFIED | `edit.py` lines 59-62 set it; `plan()` (lines 86-132) never reads `length_s` except through `it["why"]` into plan.json |
| "2-minute" with a hyphen is not read | RUN | `read_intent("a 2-minute VSL")` returned no `length_s`; `read_intent("a 2 min sales video")` returned 120 |
| Analyses the footage, measures words per minute | VERIFIED | `edit.py` lines 95-97 |
| layers.json holds finish profile, breath, sound sections, track, sfx folder | VERIFIED | `edit.py` lines 109-113 |
| 16:9 formats render a preview with longform and run the review; vertical formats print the reel command; reel cutter does not read layers yet | VERIFIED | `edit.py` lines 122-131 (comment "vertical formats go through the reel cutter, which does not read layers yet") |
| DEFAULTS table: platforms, LU 11/14/12, 12, 16, 20, 20; breath 0.45, 0.3, 0.3, 0.4, 0.4; finish vsl, reel, reel, brand, vsl; dialects | VERIFIED | `edit.py` lines 37-44 |
| vsl_hero sections: four or more sentences; hook first sentence, body from the second, CTA at the sentence 80% of the way | VERIFIED | `edit.py` lines 105-108 (`len(an["sentences"]) >= 4`, `int(len(an["sentences"]) * 0.8)`) |
| Over 200 wpm gets at least 0.45 s; persuasion peaks near 181 wpm | VERIFIED | `edit.py` lines 100-102 ("persuasion peaks near 181 in the research"); RB section 14 KIM19 (meta-analysis, 2019) |
| `edit` has no `--audience`; it lints for the brand's usual viewer | RUN / VERIFIED | `closer.py edit --help` (no such option); `edit.py` line 128 calls `longform` without `audience`; `brands.py` `check_copy` uses `brand["audience"]` when none is given |
| Client-facing SMA never shows annuity; `longform ... --audience client` adds it | VERIFIED | `brand/sma.json` (`"audience": "agent"`, `"never_client": ["annuity", "annuities"]`); `HOUSE_RULES.md` ("Client-facing annuity copy never says 'annuity'"); `closer.py longform --help` lists `--audience {default,client}` (RUN) |
| The longform command reuses the job folder's analysis | VERIFIED | `analyze.py` lines 138-151: the cache is `out/analysis.json`, keyed on video, mtime, start, end, model, faces and stride; `edit.py` calls `analyze(video, out)` with the defaults and the `longform` CLI defaults are the same (start 0, end none, small.en, track camera, stride 2; `cli.py` `common`) |

## 1. The arc

| Claim | Status | Source |
|---|---|---|
| No automatic arc engine yet | RUN | `grep` for arousal / valence / arc.json across `tools/studio/*.py`: no hits |
| Hook: message with face by 3 s on reels and ads, promise by 10 s | VERIFIED (research) | ARC HOOK params, citing Meta/Nielsen ("47% of value in 3 s, 74% in 10 s") and TikTok ("> 63% of top-CTR ads") |
| vsl_hero hook by 3 s, spoken from frame one | VERIFIED | `formats.json` vsl_hero `"hook_deadline_s": 3` and check "Hook spoken from frame one"; `review.py` line 102 (`opens by {hook_deadline_s} s`) |
| YouTube hook by 15 s | VERIFIED | `formats.json` yt_authority `"hook_deadline_s": 15`; ARC HOOK citing vidIQ and YouTube Help |
| Hook: effects allowed on each visible event, inside the dialect budget | VERIFIED (research) / VERIFIED | ARC HOOK "SFX allowed on each visible event"; budgets in `SOUND_RULES["sfx"]["density"]` |
| Payoff: one effect hit at most | VERIFIED (research) | ARC PAYOFF "one hit max" |
| vsl_hero hook 11 LU, body 14, CTA 12 | VERIFIED | `edit.py` `DEFAULTS["vsl_hero"]["sections"]`; the same values in `sound.py` `SECTION_PRESETS["vsl_hero"]`. ARC proposed 12 and 15 LU; the code's measured spec values win |
| VSL of 2 minutes or more: first 60 s at 1.5 to 2 times the body rate | VERIFIED (house) | RB section 1, "intro density multiplier", vsl column "1.5-2x for the first 60 s" (house); RB section 1 defines the vsl profile as "2-20 min" |
| 60 to 150 s homepage VSL: the dense part is the first 15% | INFERRED | the 60 s window does not fit a 60 to 150 s piece; the hook share comes from the 60 to 150 s shape below (hook 0 to 15%) |
| Calm: about every 4 s | VERIFIED (research) | ARC CALM_EXPLAIN, citing Cutting 2016 (CRPI, 4.3 s modern average shot length) |
| Alternation 1.00 and about 1.08 | VERIFIED (house) | ARC CALM_EXPLAIN "punch-in alternation 1.00 / 1.08", house within the 5 to 15% sources |
| Calm is not settable per section; the vsl_hero clock runs everywhere; a zoom hold sets one framing | VERIFIED | `formats.json` lines 672-678 (`punch_every_s` 2.6, zooms 1.0, 1.12, 1.0, 1.22); `longform.py` lines 149-150 pass one clock and one zoom list to `cut.build`; lines 159-163 set a single `zoom` on every piece inside a hold |
| About 2 graphics per minute in the body | VERIFIED (research) | ARC CALM_EXPLAIN, citing Joseph, "I Trained Claude to Edit Like Iman Gadzhi", youtube.com/watch?v=UH4l4QjHDOQ (2026-08-08); RB section 1 brand 1.5-3 per minute (SOZAI_GADZHI) |
| Pain: holds of 5 to 10 s, no B-roll over first-person lines | VERIFIED (research, low) | ARC PAIN, citing B-Script (arxiv.org/abs/1902.11216) and Guo, Kim & Rubin 2014, plus a heuristic |
| Pain: tight and still about 1.10 | VERIFIED (house) | ARC PAIN "static tight frame 1.10, no zoom drift [house]" |
| A section runs until the next one's `from`, so a pain section needs one after it to return | VERIFIED | `longform.py` lines 370-374 (`b0` is the next section's `from`, or the end) |
| A pause cut inside a zoom hold shows as a jump at one scale | INFERRED | `cut.py` breaks a run at a gap over 0.35 s (line 26), so the next piece starts later in the source; the hold gives both pieces the same zoom (`longform.py` lines 159-163) |
| Pain: at most 1 new element per sentence | VERIFIED (derived) | ARC PAIN, derived from Lang 1999 (overload) and LC4MP |
| Pain: music out or 20 LU or more under | VERIFIED (house) | ARC PAIN, citing Cutting 2016 (PBR) with the gap as house |
| Build: about 4 then 3 then 2 s | VERIFIED (derived) | ARC BUILD "change interval steps 4 -> 3 -> 2 s [derived]" |
| Kicks 1.10 to 1.15 on emphasised words | VERIFIED (research, low) | ARC BUILD, citing No Film School and Epidemic Sound (low) |
| The punch clock lands framing changes on emphasised words | VERIFIED | `cut.py` line 51 (`due >= punch_every - 0.8 and words[i].get("emph")`) |
| A `kicks` entry: an 8% zoom pulse that settles in 0.27 s, plus a section-change sound | VERIFIED | `render.py` line 115 (`+0.08*pow(max(0,1-t/0.27),2)` when `kick_in`); `longform.py` lines 164-168 (kicks set `kick_in` on the piece within 0.5 s) and line 363 (`section_change` event for every `kick_in`) |
| A kick is a scale reversal inside 1.0 s | INFERRED | the pulse rises and falls inside 0.27 s; RB AS-05 ("0 scale reversals within 1.0 s") |
| Proofs ascending, biggest last; most important claim last | VERIFIED | ARC BUILD, citing the MrBeast production memo (2024); ARC rule STAIR-STEP, citing Olsen 1995 (J. Advertising 24(4)) |
| Bed rising toward 12 LU | VERIFIED (house) | ARC BUILD "bed rises 1 LU per step toward 12 LU under speech [house]" |
| Payoff: strongest visual on the word or up to 0.15 s early | VERIFIED (research) | ARC PAYOFF, citing talking-head-editor (github.com/griffinwooldridge/talking-head-editor, MIT) |
| Card holds 3 to 7 s | VERIFIED (research) | ARC PAYOFF, citing video-use (github.com/browser-use/video-use, MIT); RB MO-09 ("simple cards 5-7 s", "at least 3 s") |
| Silent 0.5 to 1.0 s before the line, dry, back on the next downbeat | VERIFIED (derived) | ARC PAYOFF, derived from Olsen 1995 and Lin 2022, level house |
| Resolve: 5 to 8 s shots, wide again 1.00 | VERIFIED (house / research) | ARC RESOLVE_CTA "longer shots 5-8 s [house; Cutting]", "frame widens to 1.00 [src: Cutting]" |
| The 2 dB CTA lift cancels out; lower the cta `vm` for a louder bed | RUN / VERIFIED | `sound.py` `music_automation` adds `cta_lift_db` (2.0) inside the `cta` section; `music_stem` then corrects each section's median to its own `vm` on word frames. RUN on synthetic stems (30 s, body vm 14 then cta vm 12): with `cta_lift_db` 0 and 2 the cta section measured 12.0 LU both times and the bed RMS was -35.46 and -35.45 dB |
| A riser builds tension; leave the calm ask dry unless an A/B says otherwise | VERIFIED (house) | RB AU-11 ("a riser builds into the reveal"); RB DA-1 VSL setting (soft effects only); house call for the ask |
| "Set it with" keys: `zoom`, `music.mute`, `kicks`, chips, scenes, `breath.after`, sections `vm`, sfx `cta_riser` | VERIFIED | `tools/studio/longform.py` lines 144-168 (breath, zoom, kicks), 349-351 (music.mute), 365-374 (sfx events, sections); `tools/studio/layers.py` docstring (scenes, chips, music.mute); `skills/video/sound-director/SKILL.md` section 1 |
| Man in a hole shape; flag a flat script | VERIFIED (derived) | ARC script arc check, derived from Reagan et al. 2016 |
| Quarters of about 25% each, slow open, fastest at the start of the last quarter | VERIFIED (research) | ARC rule FOUR-QUARTER PACING CURVE, citing Cutting 2016 (PBR, PMC5133278: 24.9 / 26.5 / 25.1 / 23.5) |
| Re-engagement near 3:00 and 6:00, a demo or a sourced proof | VERIFIED (research) | ARC rule LONG-FORM ARC, citing the MrBeast production memo 2024; RB VO-25 ("re-engagement near 180 s and 360 s"). "Sourced" follows `CLAUDE.md` (never invent a number) |
| Blocks within about 6 minutes | VERIFIED (research) | ARC rule SPEECH TIGHTENING, citing Guo, Kim & Rubin 2014 |
| 60 to 150 s VSL: hook 0 to 15%, problem 15 to 40%, proof 40 to 75%, offer 75 to 100%; music strong, out, building | VERIFIED (house / research) | ARC format override vsl_hero_60_150s (house, mapped from Cutting; music citing Cutting 2016 PBR, about 75% / 35% / > 50% of shots) |
| High-arousal words: slower cutting; calm words: related edits | VERIFIED (research) | ARC rule PACING AND CONTENT INTERACTION, citing Lang et al. 1999 and Lang et al. 2000 |
| A price counts as a high-arousal claim | INFERRED | this page's own rule that a price is a claim (section 3); the source names big claims |
| Over 55: hold numbers and the offer longer | VERIFIED (research) | ARC rule AGE-AWARE PACING, citing Lang, Schwartz & Mayell 2015. "Guarantees" removed from this line: `brand/btc.json` bans "guarantee" on screen |

## 2. What they see

| Claim | Status | Source |
|---|---|---|
| Beyond the face, one caption block and one graphic; decorative text counts | VERIFIED (research) | ARC rule ELEMENT BUDGET, citing Mayer 2017, Wang & Pomplun 2012, Cerf et al. 2007 |
| B-roll only where the picture explains faster; never over claims or emotional lines; 2 to 4 s | VERIFIED (research, low) | ARC rule B-ROLL VS FACE, citing Guo, Kim & Rubin 2014 (Captions.ai and Jupitrr, low) |
| vsl_hero: full-screen cards at most about half the runtime, speaker back every 15 s | VERIFIED | `formats.json` vsl_hero `checks` ("Full-screen cards at most about half the runtime and the speaker back on camera at least every 15 s") |
| Eye to the face within about 500 ms; on the cut or 0.5 s later; never two in the same 0.5 s | VERIFIED (derived) | ARC rule AFTER A CUT, citing Cerf et al. 2007 and the Netflix shot-change rule; the combination is derived |
| Animate in, hold still, one thing moves at a time | VERIFIED (research) | ARC rule MOTION STEALS GAZE, citing Mital et al. 2011 and Smith & Mital 2013 |
| One highlighted word per chunk; stat card = number plus a 1 to 3 word label | VERIFIED (research) | ARC rules ONE HIGHLIGHT and NO DUPLICATE SENTENCES, citing Mayer 2017; RB TY-07 |
| 9:16 at 1080 wide: under 32 px never, chips 48 px, captions 64 to 110 px, slam about 180 px | VERIFIED (computed) | RB TY-02 floor 9x16 (Apple HIG Typography plus arithmetic) |
| 16:9 on a phone: 54 px must-read, 80 px comfortable | VERIFIED (computed) | RB TY-02 floor 16x9 phone (HIG; the BBC 8% figure unverified) |
| Contrast 4.5:1 against the brightest pixels; plate, then a stroke of 3 px or more at 1080, a shadow last | VERIFIED (research) | RB TY-05 (WCAG 2.2 SC 1.4.3); ARC rule BRIGHT SKY FIX ORDER (Blitzcut, Captions.ai low; Brown et al. 2015) |
| Never change the text colour frame by frame | VERIFIED | RB TY-05 rule text |
| Eyes at 30 to 38% of the height in 9:16 | VERIFIED (research) | RB FR-04 eye y (REALEYE on Baig et al. 2025; META_SAFE; VIMEO_FRAMING) |
| Placement: no coordinates; more than 2% over the face or more than 1% over the captions fails | VERIFIED | `tools/studio/placement.py` `PLACEMENT_RULES["face_fail_overlap"] = 0.02`; `place()` sets `ok` to `face_hit <= face_fail_overlap and cap_hit <= 0.01`; `review.py` `extra_checks` fails any placed element with `ok` false |
| Plain text over more than 0.62 mean luma costs extra; chips on a plate | VERIFIED | `placement.py` `bright_text_luma: 0.62` and line 223 (`d["bright"]`, measured only for `style == "plain"`); `layers.py` line 316 (chips placed with `style="plate"`) and the chip `Plate` events |
| Easing: 250 to 400 ms, (0.05, 0.7, 0.1, 1.0); exits 150 to 200 ms, (0.3, 0, 0.8, 0.15); no linear on position or scale | VERIFIED (research) | ARC rule EASING TOKENS, citing the Material 3 motion tokens (Flutter `material/motion.dart`); RB MO-02 for the curves (M3; CARBON) |
| Springs: 0 to 0.15 premium, one slam may reach 0.3, never above 0.4 | VERIFIED (research) | RB MO-03 (APPLE_SPRING, WWDC23 "Animate with springs"); ARC rule PREMIUM VS CHEAP SPRINGS |
| Premium captions: one family, sentence case, weight shift, no bounce; short-form caps with one keyword colour | VERIFIED (research, low-medium) | ARC rule PRESET BY VIDEO TYPE (Submagic and SendShort breakdowns); RB TY-07 (UPPER in reel only; KAPWING, JOYSPACE) |

## 3. When the edit changes

| Claim | Status | Source |
|---|---|---|
| Every cut has a reason (five reason codes) | VERIFIED (research) | ARC rule REASON CODE, citing Dmytryk, On Film Editing, 1984 |
| Murch's order: emotion, story, rhythm, eye-trace, 2D, 3D | VERIFIED (research, weights low) | RB AS-34 ("weights unverified against the book") |
| Never inside a number or demo move, never across a reaction | VERIFIED (research) | ARC rule SAFE CUT MOMENTS, citing Nakano et al. 2009 |
| Dead air over 0.35 s cut; pieces under 1.0 s merge | VERIFIED | `tools/studio/cut.py` `GAP_MAX = 0.35`, `MIN_PIECE = 1.0`, `build()` lines 26 and 37-39 |
| Punch every `punch_every_s`: 2.6 in vsl_hero, 4.5 when unset; up to 0.8 s early for an emphasised word | VERIFIED | `formats.json` line 672 (`"punch_every_s": 2.6`); `longform.py` line 149 (`fmt.get("punch_every_s", 4.5)`); `cut.py` line 51 |
| Framings alternate through `zooms` | VERIFIED | `cut.py` lines 100 and 103-105; `longform.py` line 150 |
| Without breath, a 1.2 s sentence gap came out at 0.06 s | RUN | `cut.build` on synthetic words (1.2 s gap after "first."), no `sentence_pause`: output gap 0.063 s (0.059 s in the first run) |
| Breath JSON keys `sentence` and `after`; loaded by layers.py, passed by longform.py | VERIFIED | `longform.py` lines 143-151 (`lay.load(layers)`, `br.get("after", [])`, `sentence_pause=br.get("sentence")`) |
| Example anchors `Pretty@15.15`, `Finally@82.99` | VERIFIED (illustrative) | the same anchors appear in `skills/video/sound-director/SKILL.md` section 1; illustrative only |
| Sentence end keeps the value, 60% after the line, 40% before the next | VERIFIED / RUN | `cut.py` lines 71 and 80 comments ("40 % of the pause sits before the next line", "60 % after the line ends"); RUN: `sentence_pause=0.45` kept 0.447 and 0.467 s at sentence ends |
| Only where the speaker paused more than 0.35 s; a shorter pause is left as it was | VERIFIED | `cut.py`: `pause_for` is read only in `in_point` and `out_point`, which run at piece boundaries, and a piece ends only at a gap over `GAP_MAX` (line 26) |
| Gaps inside a sentence still trimmed tight | RUN | a 0.6 s gap after a word with no full stop came out at 0.067 s with `sentence_pause=0.45` |
| VSL research band 400 to 600 ms | VERIFIED (house) | RB section 1, "sentence gap ms", vsl "400-600" (house; LIU22, VIZARD_PAUSE, R_EDITORS) |
| A VSL beat of 700 to 1200 ms, at most 2 per minute | VERIFIED (house) | RB section 1, "emphasis beat ms", vsl "700-1200 before a price, claim or CTA, at most 2 per min" |
| A pause under 0.35 s gets no beat (0.25 s stayed 0.25 s) | RUN | `holds` of 1.0 s on a word followed by a 0.25 s gap: the words stay in one piece and the gap stays 0.25 s |
| A 0.6 s pause with a 1.0 s beat came out at 0.96 s; room tone reused | RUN / VERIFIED | `holds` of 1.0 s on a 0.6 s gap: output 0.953 s (0.962 s in the first run); `cut.py` `out_point` (`min(e + 0.6 * p, limit)`) and `in_point` (`s - 0.4 * p`) let the two pieces overlap in source time |
| Never past 1.05x | VERIFIED | `EDITING_GRAMMAR.md` section 5 ("Never pitch the voice or speed it past 1.05x") |

## 4. How it sounds

| Claim | Status | Source |
|---|---|---|
| `edit` writes the sections from its `DEFAULTS`; `SECTION_PRESETS` holds the same numbers and nothing else reads it | VERIFIED / RUN | `edit.py` lines 104-110; `grep -rn SECTION_PRESETS tools/` finds only its definition in `sound.py` line 83 |
| A section with no `p10` gets `vm` minus 6 | VERIFIED | `longform.py` line 374 (`sc.get("p10", sc["vm"] - 6)`) |
| Drops: at most 3; `[from, to]` out 0.4 s before `from`; a third value sets the lead | VERIFIED | `longform.py` lines 349-351 (comment "a mute is [from, to] (the bed goes out 0.4 s before the line starts) or [from, to, lead]" and the arithmetic `- (lead - 0.4)`); `sound.py` `music_automation` (`a0 = a - drop_lead_s`, `drops_max` 3) |
| Example window with `:end` and lead 0.8 | VERIFIED (illustrative) | `layers.py` docstring (anchor forms `word@s` and `word@s:end`); longform line 351 reads the third value |
| Bed back on the next bar line within 1.0 s of the window's end | VERIFIED | `SOUND_RULES["music"]["return_downbeat_within_s"] = 1.0`; `music_automation` (`nxt[0] - b <= return_downbeat_within_s`) |
| Dialects gadzhi and nelk; gadzhi leaves most cuts dry | VERIFIED | `SOUND_RULES["sfx"]["grammar"]` (gadzhi `punch_in`, `hard_cut`, `card_out` are `[]`) |
| The owner picks from the top three in `music_ranked` | VERIFIED | `edit.py` line 115 ("owner listens to the top 3"), line 116 (`music_ranked`), line 83 (top 5 kept) |
| The CTA lift cancels out (2 dB, measured 2026-11-02) | RUN | see section 1, "The 2 dB CTA lift cancels out" |

## 5. The look

| Claim | Status | Source |
|---|---|---|
| Measures face brightness, sky brightness, sky share, clipping first | VERIFIED | `finish.py` `measure()` returns `face_luma`, `sky_luma`, `sky_share`, `clipped_share` |
| Face toward 0.52 luma, at most 0.30 EV, never darkened; well-exposed face gets no lift | VERIFIED | `finish.py` `FINISH_RULES["face"]` (`target_luma: 0.52`, `ev_max: 0.30`); `plan()` (`np.clip(..., 0.0, ev_max)`); docstring line 12 |
| Sky pulled down only above 0.66 luma, at most 0.45 EV | VERIFIED | `FINISH_RULES["sky"]` (`hot_from: 0.66`, `ev_max: -0.45`); `plan()` |
| Profiles: vsl off / 0.007 / 0.12; reel off / 0.006 / 0.10; brand full (grain 0.012, vignette 0.16) | VERIFIED | `finish.py` `FINISH_PROFILES` lines 36-38; brand falls back to `FINISH_RULES` `grain.amount: 0.012`, `vignette.strength: 0.16` |
| Brand halation when sky share over 3% or over 0.2% clips | VERIFIED | `plan()` (`sky_share > 0.03 or clipped_share > 0.002`) |
| Corner stops -0.18, -0.15, -0.25 | RUN (computed) | `_work()` vignette `1 - strength * smooth(r, 0.55, 1.45)` at the corner (r = 1.414): factors 0.881, 0.900, 0.841, log2 = -0.184, -0.151, -0.250 |
| Every long-form piece goes through `grade.POST`: two unsharp passes and a vignette at a=0.35 | VERIFIED | `grade.py` line 16 (`POST = "unsharp=lx=13:ly=13:la=0.30,unsharp=5:5:0.45,vignette=a=0.35"`); `render.py` line 120 in `piece_jobs` (`post = grade.POST + ...`, no condition) |
| a=0.35 measured at -0.36 stops | RUN | ffmpeg 6.1.1, a flat 0xbfbfbf 1920x1080 frame through `vignette=a=0.35`: centre 190, corner 148, log2 = -0.36; RB TX-06 ("0.35 rad = -0.36 stops", measured) |
| A VSL's corners land near -0.54 stops | INFERRED | the two vignettes multiply, so their stops add: -0.36 + -0.18 |
| The double sharpening is the open TX-04 item (a crunchy, AI-looking face) | VERIFIED | RB TX-04 and RB section 9 known defects ("the double unsharp pass gives a crunchy, AI-looking face") |
| VSL gets the clean finish because it sells trust in a person; grain must survive the player | VERIFIED | `finish.py` comment above `FINISH_PROFILES` ("a sales VSL sells trust in a person ... Web players re-encode at low bitrates"); RB DA-4 |
| Teal-orange for B-roll and brand moments only | VERIFIED (house) | RB GR-02 |
| Skin-hue check warns, never auto-corrects | VERIFIED | RB GR-04 ("Report only, never auto-correct (DA-5)") |
| No generative face fixes: eye contact, jump-cut synthesis, face swap, beauty filter | VERIFIED | RB AS-26 ("Generative face fixes (eye contact, jump-cut synthesis, swaps, beauty filters)", BLOCK; JUMPCUT_SYNTH, arxiv.org/abs/2401.04718, an anti-reference) |

## 6. AI-slop tells

| Claim | Status | Source |
|---|---|---|
| beats.txt in the cut folder | VERIFIED | `longform.py` line 443 (`(out / "beats.txt").write_text(cutmod.beat_map(segs, words))`) |
| Metronome: CV 0.5 or more, no more than 2 intervals in a row within 10% | VERIFIED (house) | RB AS-01 (CUTTING10; ONEOF10) |
| Zoom mid-clause: within 80 ms before a clause start or after 250 ms of pause | VERIFIED (house, principle sourced) | RB AS-03 (VIZARD_PUNCH) |
| Same scale: steps of 0.10 or more, no more than 3 in a row | VERIFIED | RB AS-04 (ONEOF10) |
| Zoom pulses: no reversal within 1.0 s; at most 1 push-in per 30 s in VSL and brand | VERIFIED (house) | RB AS-05 (JOYSPACE; SUBMAGIC) |
| Breathless: CV 0.3, no more than 70% under 120 ms | VERIFIED (house) | RB AS-06 and VO-06 (R_EDITORS; VIZARD_PAUSE) |
| 0.6 s held after an emotional or punchline line | VERIFIED (house) | RB AS-11 (ONEOF10; MURCH) |
| Graphic triggers; 20 s since the last visual | VERIFIED | RB AS-12 (SOZAI_GADZHI triggers; 20 s house) |
| No repeat more than 3 times in a row | VERIFIED (research) | ARC rule PATTERN-INTERRUPT FATIGUE, citing Potter, Lynch & Krause 2015 ("identical SFX, whoosh, pop, zoom curve or chip animation") |
| The engine takes a role's files in turn; one file or the synthesized fallback repeats every time | VERIFIED | `sound.py` `Library.pick` (`files[k % len(files)]`; with no files, `SYNTH[role]()`); `SOUND_RULES["sfx"]["rotate_max_repeat"]` is defined but read nowhere (`grep`) |
| Effects on no more than 25% of cuts | VERIFIED (house) | RB AU-12 cut share (CHOPPITY_AH, no transition SFX) |
| One accent colour, one accented word, no emoji outside reels | VERIFIED (house) | RB TY-07 (OPUS; JOYSPACE; SUBMAGIC) |
| No more than 50% of overlay centres within 5% of the centre (16:9) | VERIFIED (house) | RB AS-19 (KAPWING; applies to yt, vsl, brand) |
| B-roll within 12% of the A-roll's mean brightness | VERIFIED (house) | RB AS-21 (WIDEFRAME) |
| Compression 4:1 or lower | VERIFIED | RB AS-23 (VIDPROS, about 3:1 typical; 4:1 house); the engine runs 1.5:1 and 3:1 (`SOUND_RULES["voice"]` `level_ratio`, `peak_ratio`) |
| Every number on screen from the footage or the brand file | VERIFIED | kit `CLAUDE.md` ("If the footage or the brand file does not say it, it is not on screen"); RB AS-31 |
| The 16:9 review fails: hook deadline, static over 8 s, a graphic on the face or captions, banned words, voice under the music (median under 9, worst 5% under 3), more than 12 effects a minute | VERIFIED | `review.py` `run_long` line 102 (hook deadline), 112 (static stretch), 122 (banned words), `extra_checks` 182 (placement), 190 (`music_ok`), 194 (effects per minute); `sound.py` `qc` (`median >= 9.0 and p5 >= 3.0`) |
| The reel review fails captions on the chin | VERIFIED | `review.py` `run` line 66 (chin inside the caption block on more than 5% of samples); `run_long` has no chin check |

## 7. The loop

| Claim | Status | Source |
|---|---|---|
| Graphics only where the words name a thing or a sourced number | VERIFIED | `edit.py` line 117 (plan.json `next`) |
| Stop after 3 self-review passes | VERIFIED (research) | RB section 7, Review loop ("At most 3 self-review passes per render, then report what is still open (sourced; VIDEOUSE)") |
| Say done only on all PASS | VERIFIED | kit `CLAUDE.md` ("Say done only on all PASS") |
| Cold review for client-facing or paid | VERIFIED | kit `CLAUDE.md`; `skills/video/cold-review/SKILL.md` |
| `compare old.mp4 new.mp4 --out --labels v8,v9`; synced players, wipe, timelines of cuts, loudness, picture, faces | RUN / VERIFIED | `closer.py compare --help` (exit 0); `tools/studio/compare.py` docstring and `run()`; `cli.py` help text "'v8,v9'" |
| The Windows compare line | VERIFIED, not RUN | the same `& $PY` call form as section 0 |
| A verdict shows when judge.json sits in the `--out` folder | VERIFIED | `compare.py` `run()` (`judge = out / "judge.json"`; read when it exists) |
| Blind judge: no names or plan, evidence before verdict, both orders, win only if it holds both ways | VERIFIED (research) | RB section 8, Judge protocol items 2, 4 and 5 (PANICKSSERY24; WANG23; SHI24) |
| Blind A/B protocol in `skills/video/compare-cuts/SKILL.md`; research in the rulebook section 8 | RUN / VERIFIED | the skill exists and its own audit passes (`audit_skill.py`, 2026-11-02); named in `edit.py` line 119 |
| Owner A/B: 10 to 15 s, same section, matched loudness, phone speaker and earbuds | VERIFIED | AS section 7 ("Clips of 10 to 15 s, the same section on both sides, matched in loudness to within 0.2 LU"; "on a phone speaker at 50 to 70% volume and on earbuds"); `skills/video/sound-director/SKILL.md` section 7 |
| Move the rule in that video's layers, not the code | VERIFIED | `skills/video/sound-director/SKILL.md` section 7 ("in that video's `sound.rules`, not in `tools/studio/sound.py`") |

## 8. Devil's advocate

| Claim | Status | Source |
|---|---|---|
| Energy numbers from short-form entertainment; persuasion needs processing; hype on a financial product | VERIFIED | RB DA-1 (GUYER24 for persuasion) |
| VSL setting: 2 to 4 graphic moments per minute on numbers or proof plus the ask; punch-ins only to hide jump cuts; soft effects, no shake or flash | VERIFIED (house) | RB DA-1 VSL setting |
| At least 500 plays per side; bookings with a significance test | VERIFIED (house) | RB DA-1 test ("at least 500 plays per side (house)") |
| Fast talker above the 181 wpm peak; tight 250 to 350 ms against breathing 450 to 600 ms | VERIFIED | RB DA-2 (KIM19; test arms) |
| VSL sentence gaps 400 to 600 ms, beats before price and claims, no first-minute caps | VERIFIED (house) | RB DA-2 VSL setting |
| Captions: phrases of 4 to 7 words, up to 42 characters, sentence case, at least 52 px on 16:9 | VERIFIED (house) | RB DA-3 VSL setting |
| Letterbox blacks out a quarter of a 16:9 frame | VERIFIED (computed) | RB DA-4 ("blacks out 25.6% of the frame (276 of 1080 lines)") |
| Skin target: warn only; 3 to 5 approved frames as the reference | VERIFIED (house) | RB DA-5 |
| vsl_hero punches every 2.6 s, zooms 1.00, 1.12, 1.00, 1.22 | VERIFIED | `formats.json` lines 672-678 |
| Past the 112% punch unless the source is 4K | VERIFIED / INFERRED | `HOUSE_RULES.md` ("Punch-ins (100% to about 112%)"); RB FR-03 (effective upscale = punch scale x output height / source crop height, cap 1.12). Inferred: a 2160-line source cut to 1080 gives 1.22 x 0.5 = 0.61 |
| Slow push of 2.5% on every piece | VERIFIED | `longform.py` line 188 (`push=0.025`); `render.py` line 115 (`1.02+push*t/D`) |
| One animated push-in per 30 s in the slop table | VERIFIED (house) | RB AS-05 |
| vsl_hero captions are `impact`: caps, 2 to 4 words, a colour accent | VERIFIED | `formats.json` vsl_hero `"captions": "impact"`; `captions.py` `STYLES["impact"]` (`case: upper`, `words: (2, 4)`, `mechanism: color`) |
| Closest look: `--captions serif` (sentence case, no highlight) with `"captions": {"words": [4, 7]}` | VERIFIED | `captions.py` `STYLES["serif"]` (`case: sentence`, `mechanism: none`); `cli.py` longform `--captions`; `longform.py` lines 268-276 (`words_range` from the layers `captions.words`) and `captions.events` (`lo, hi = words_range`) |
| Brief: music at least 13 dB under; presets 11 and 12; review passes a median of 9 | VERIFIED | `formats.json` vsl_hero check ("Music under the voice at least 13 dB down"); `edit.py` `DEFAULTS["vsl_hero"]`; `sound.py` `qc` |
| Finish lifts the face through a tracked soft window; rulebook prefers whole-frame curves | VERIFIED | `finish.py` docstring ("a tracked soft window lifts the face toward a skin target"); RB GR-05 rule text ("use whole-plate curves only, never face-local edits") |
| 55-plus audience is client-facing; vsl_hero speaks to agents | VERIFIED | RB section 1 vsl profile ("Prospects are about 55-72"); `formats.json` vsl_hero checks ("Brand lint: agent-facing") |
| Best music on a VSL may be none | VERIFIED | RB section 12, Also watch ("AU-04, the music gap: on a VSL the best music may be none") |

## 9. Routing

| Claim | Status | Source |
|---|---|---|
| Every skill path in the routing table exists | RUN | `ls skills/video skills/strategy/format-brain skills/sales/closer-mentality` on 2026-11-02; the auditor's path check passes |
| filming-playbook covers filming and raw-take checks, including pauses between lines | RUN / VERIFIED | `skills/video/filming-playbook/SKILL.md` description ("delivery (pauses between lines, ...)"); its own audit passes (2026-11-02) |

## Proprietary sources

None used. This page, its rows and the two docs it points to carry no rule whose only source is proprietary; the research notes behind ARC and the rulebook were checked for that on 2026-11-02, and every rule used here cites a public paper, page, upload, standard or the kit's own code, or is marked house.

## Result

AUDIT: 177 claims, 171 verified (25 of them backed by a RUN and 5 by a WEB fetch in this session), 0 user-stated, 6 inferred, 0 gaps, 0 unresolved contradictions.

Fixed in the cold review: an ffmpeg 9.0 render blocker and the missing libass on Homebrew's plain formula (section 0 now says how to get a working build on each OS); the `music` and `sfx` folders the commands assumed; no `--audience` on `edit` for client-facing annuity videos; "make it cinematic" falling back to the YouTube format; the vsl_hero hook deadline (3 s, not 15 s); `kicks` described as framing when they are a zoom pulse with a sound; the CTA music lift that the calibration cancels; the drop lead set by a third value instead of moving anchors; the hidden `grade.POST` sharpening and vignette; sound rotation needing two files per role; the 16:9 review list (no chin check outside reels); "guarantees" on screen for a brand that bans the word; the caption and music-level conflicts in `vsl_hero`; Windows forms for every command; local `/tmp` research paths replaced by the published rulebook and audio spec.

Not run: the Windows and Mac commands (no machine of either kind), and a full `edit` render (this audit ran the parser, the cutter, the music automation and calibration, and the help screens only). The research-against-code conflicts stay on the page, with the code winning until the owner decides.
