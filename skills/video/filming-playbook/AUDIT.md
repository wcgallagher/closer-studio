# AUDIT: filming-playbook

Every figure, path, command and tool in SKILL.md, with its source. Checked 2026-11-02 against the kit's working tree; the code's RULES dicts are the source of truth.

Sources used below:

- **R**: the filming research, `<research run w6rxupr9a (session output, not in this repo)>`, angle 5 "How to film for the edit" (items 0 to 26 and its rules), angle 1 rules FILM-1 to FILM-4 and HARD-4, and the plan's rank 4 "ingest-gate" and rank 7 "filming-playbook" entries.
- **A**: the audio research, `<session scratchpad>/audio_spec_v1.json`.
- R and A are session files, not shipped in the kit, so a stranger cannot open them. The kit's own copy of A is `docs/AUDIO_SPEC.md` (line 26 "sounds too enhanced", lines 43 and 44 the high-pass and wind-burst rules, line 66 "under 0.2 of the pause energy sits below 150 Hz", line 75 "pause SNR at least 30 dB ... (house)"). R has no copy in the kit; `docs/EDITOR_RULEBOOK.md` FR-01 (180-degree shutter) and FR-02 (a 9:16 crop from 16:9 needs a 4K source) repeat two of its points.
- **Cold check**: a second, zero-context pass on 2026-11-02 read SKILL.md against `tools/studio/*.py` and re-ran every code block literally on the takes from a scratch copy of the kit layout (`tools` linked to the kit, the takes linked into `inbox/`, so the kit's own `inbox/` and `output/` stayed empty). Rows marked "cold check" come from that pass.
- **Takes**: the three raw takes of the first shoot the kit cut (the Set More Annuities website VSL: take1 92.5 s, take2 100.1 s, take3 69.5 s, all 3840x2160 at 30/1 fps, audio 44100 Hz), measured on 2026-11-02 with the skill's own commands. Test outputs went to a scratch folder, not to the kit.

## Commands, paths and tools

| Claim | Status | Source |
|---|---|---|
| Section 0 KIT and PY lines, `tools/closer.py hands --help` | RUN | run from the kit folder: KIT resolved to the kit, PY to `~/.closer-studio/venv/bin/python` (Linux); help printed. Cold check: with no `kit_path` file, KIT fell back to `pwd` and the help printed `usage: closer hands [-h] [--start START] --end END [--fps FPS] --out OUT video`, matching `cli.py` (`--end` required, `--start` 0.0, `--fps` 10.0) |
| Run in Terminal on Mac or Linux, Git Bash or WSL on Windows; the installers write `kit_path`, else run from the kit folder | VERIFIED | `install.sh` line 64 and `install.ps1` line 59 write `~/.closer-studio/kit_path`; README line 19 (Windows through WSL); the same wording in `skills/video/placement/SKILL.md` line 18 and `skills/video/sound-director/SKILL.md` line 18; Git Bash not run here |
| Windows venv path `venv/Scripts/python.exe` | INFERRED | `install.ps1` lines 26 to 28 create `%USERPROFILE%\.closer-studio\venv` and call `Scripts\python.exe`; not run on Windows |
| `install.ps1` has not been run on a Windows machine | VERIFIED | `install.ps1` header: "Written to mirror install.sh; not yet run on a Windows machine" |
| An agent's shell does not keep variables between commands | VERIFIED | this session's Bash tool contract ("Shell state (env vars, functions) does not persist"); also seen in the literal test, where a block run in a pipe did not pass CHECK to the next block |
| Raw takes in `inbox/` never changed; work in `output/<job>/` | VERIFIED | `CLAUDE.md`: "Never delete or overwrite raw files in `inbox/`. Work in `output/<job-name>/`." |
| The blocks use `shoot1` as the job name | RUN | cold check: the earlier text put a literal `<job>` in the commands, which bash accepts but which made a folder named `<job>`; `<` and `>` are not allowed in Windows file names, so the commands now use a real name; re-run literally with `shoot1` |
| Step 1 probe script; HDR transfer names `arib-std-b67` (HLG) and `smpte2084` (PQ) | RUN | run literally on take1 and take2: "3840x2160 at 30/1 fps, audio 44100 Hz", "one frame rate across takes"; both names listed by `ffmpeg -h filter=setparams` (ffmpeg 6.1.1) |
| Step 2 `closer.py analyze <take> --out <dir>`; what it prints | RUN | take3: exit 0, "256 words, 0 fillers, 15 emphasised, 56.8 s of speech, face in 100% of frames, 0 cuts"; writes analysis.json and transcript.txt (`tools/studio/analyze.py`) |
| "A 70 second 4K take took 55 s in one run and 2 min 6 s in another on the Linux container we tested" | RUN | take3 (69.5 s): real 2 min 5.5 s in the first pass; real 0 min 54.8 s (user 2 min 9 s) in the cold check, same container, so wall time varies with the load on the machine |
| Analyse whole takes (no `--start` or `--end`) | INFERRED | word times are relative to `--start` (`analyze.py` reads audio from `start`), so a word map with an offset would misplace beats in `assemble` |
| The assemble spec's `"words"` can point at a kit analysis.json, so nothing is transcribed again | VERIFIED | `tools/studio/assemble.py` docstring ("an existing word map (... or a kit analysis.json). Nothing is re-transcribed") and the `_words_from_map` branch for a kit analysis.json |
| Step 3 measure script, "under a minute per take" | RUN | run literally (only the inbox and output paths redirected to scratch) on take3 in about 25 s: "pace: 224 words per minute; face in 100% of frames", "pauses: 17 sentence ends, 0 with 1 s or more, too tight to cut at [15.6, 16.2, 24.9, 42.6, 53.8]", "eye line at 39% of the height, face centre at 50% of the width", picture and sound lines as below; the same code run on take1 via its existing analysis |
| Eye points from YuNet columns 5 and 7 | RUN | OpenCV `FaceDetectorYN` rows are x, y, w, h, then right eye x, y and left eye x, y; take3 gave 39%, between the face box top (27%) and centre (45%) read from analysis.json, as eyes should be |
| `tools/studio/models/face_detection_yunet_2023mar.onnx` | VERIFIED | `tools/studio/track.py` `YUNET = MODELS / "face_detection_yunet_2023mar.onnx"`; loaded in the RUN above |
| OpenCV may print a `WARN` line | RUN | printed during analyze and step 3: "setPreferableTarget Targets are not supported by the new graph engine for now" |
| transcript.txt shows only sentence starts; word times are in analysis.json | VERIFIED | `analyze.py` writes transcript.txt as `[{s['s']:7.2f}] {s['text']}` per sentence; `words` rows carry `w`, `s`, `e` and `sentences` rows `i0`, `i1`, `s`, `e`, `text` |
| Step 4 word-finder block | RUN | cold check on take3 with `sell set`: "sell at 34.54 s, in the line 29.82 to 36.36 s" and "set at 35.36 s, in the line 29.82 to 36.36 s", then the later uses of both words |
| Balcony example: "sell" at 34.54 s and "set" at 35.36 s in a line that ends at 36.36 s, so 33.9 to 36.6 | RUN | the word-finder output above; 33.9 is "want" (33.98 s) less a little, 36.6 is the line end plus 0.24 s |
| Step 4 `closer.py hands <take> --start 33.9 --end 36.6 --out <file>` plus the summary script | RUN | cold check repeated it literally with the same results, `px` 38030 to 101566; first pass: | take3: "hands: 19 of 27 frames with a hand (33.9-36.6 s)"; summary "of 20 hands seen, 16 fully in frame (80%), 0 inside the 9:16 column (0%)", edge frames at 34.1, 35.0, 35.3 and 35.9 s |
| Example window 33.9 to 36.6 s is a gesture beat on take3 | VERIFIED | R plan rank 1 check "On take3 33.9-36.6 s"; hands found in 19 of 27 frames (RUN above) |
| `:.0%` in the scripts (shows as "0%" to the checker) | INFERRED | Python's percent format in the print statements, not a claim |
| `tools/studio/track.py`: the vertical camera follows the face | VERIFIED | track.py docstring: "Face tracking and the smoothed virtual camera behind auto-reframe" |
| `skills/video/vsl-builder/SKILL.md`, `skills/video/longform-editor/SKILL.md`, `skills/video/placement/SKILL.md`, `FORMATS.md`, `tools/studio/*.py` named in the skill | RUN | `audit_skill.py` path check passes (last line of this file) |
| Tools named: DJI Mic 2, DJI Mic 3, RODE Wireless PRO, RODE Wireless Micro, Shure MV7+, Elgato Key Light, Blackmagic Camera, Final Cut Camera, iPhone 16 Wind Noise Reduction | VERIFIED | R items 0, 1, 2, 3, 4, 11, 12, 13, 7 |

## What went wrong on the first shoot (measured)

| Claim | Status | Source |
|---|---|---|
| Three 4K, 30 fps takes | RUN | ffprobe: 3840x2160, r_frame_rate 30/1, durations 92.533, 100.067 and 69.5 s |
| A windy balcony with the sky behind the speaker | VERIFIED | R item 6 ("Explains the windy balcony take"); A section 1_voice `phone_balcony_chain`; the sky is measured below |
| Sky at 0.80 luma | RUN | `finish.measure` on the raw takes: `sky_luma` 0.8 (take1), 0.796 (take3) |
| Sky covering 36 to 44 % of the frame | RUN | `sky_share` 0.358 (take3), 0.441 (take1) |
| Face at 0.33 to 0.36 | RUN | `face_luma` 0.334 (take1), 0.363 (take3) |
| 4 to 5 % of the frame clipped; 3.8 to 4.9 %; 0.038, 0.049 | RUN | `clipped_share` 0.0376 (take3), 0.0491 (take1) |
| Finish pulled the sky about 0.3 EV and gave the face its full 0.30 EV | RUN | `finish.plan`: sky_ev -0.308 and -0.299, face_ev 0.3 on both takes |
| Rumble share 0.24 and 0.46; high-pass 110 Hz on take3 only | RUN | `sound.voice_master`: `low_rumble_share_in_pauses` 0.24 (take1, high-pass 80), 0.459 (take3, high-pass 110) |
| Wind bursts 3.4 and 5.1 s per take | RUN | `wind_burst_frames` 318 (take3) and 476 (take1), times 512 / 48000 s |
| Earlier cleanups left the voice sounding over-processed | VERIFIED | A `1_voice.diagnosis_too_enhanced` (v6/v7 chain boosted 120 Hz and denoised hard; owner feedback "sounds too enhanced", 2026-10-30) |
| Eye line 38 and 39 % | RUN | step 3: take1 38%, take3 39% |
| Face centre at 50 % of the width (the 0.50 passed in step 4) | RUN | step 3 on take1 and take3 |
| Pace 195 and 224 words per minute | RUN | step 3: take1 195, take3 224 (words over the first-word-to-last-word span) |
| 1 of 35 sentence ends had a second of quiet; 11 too tight to cut | RUN | step 3: take1 18 ends, 1 with 1 s or more, 6 at 0.35 s or less; take3 17 ends, 0, 5 |
| Face found in 100 % of frames | RUN | analyze on take1 and take3 |
| Not one of 20 hand detections inside the 9:16 column; 4 touched the edge; 16 of 20 fully in frame (80%) | RUN | step 4 on take3 33.9 to 36.6 s with the face centre 0.50 |
| Hand boxes 38030 to 101566 millionths of the frame | RUN | `px` range in the step 4 rows |

## Sound

| Claim | Status | Source |
|---|---|---|
| A phone mic a metre or two away in a bare room records mostly room; critical distance | VERIFIED | R item 8 (Critical distance, Wikipedia, 2026-03-15): "a phone mic 1-2 m away in a bare room records mostly room" |
| Lav on the sternum 15 to 20 cm (6 to 8 in) below the chin; cable taped at collar and belt; nothing that rubs | VERIFIED | R item 9 and its MIC rule (No Film School 2017-06, thewearify) |
| DJI Mic 2: 32-bit float internal recording must be switched on in DJI Mimo; noise cancelling does not run over Bluetooth | VERIFIED | R item 0 (Newsshooter 2024-01-17; retailer listings, Adorama) |
| RODE Wireless PRO records on board; timecode | VERIFIED | R item 2 |
| DJI Mic 3 dual-file, use the original; timecode | VERIFIED | R item 1 (DJI press release 2025-08-28) |
| RODE Wireless Micro: no backup recording on its page; reels only | VERIFIED | R item 3 (confidence medium) |
| Desk dynamic mic (Shure MV7+) a hand-width from the mouth, a house value | VERIFIED | R rule "MIC (desk)": "Exact recommended distance is unverified, so the house value is a hand-width" |
| Pause energy under 150 Hz; above 0.45 the high-pass moves from 80 Hz to 110 Hz | VERIFIED | `tools/studio/sound.py` `SOUND_RULES["voice"]`: highpass_hz 80, highpass_wind_hz 110, wind_ratio 0.45; `voice_master` (150 Hz low-pass on the pauses, `hp = R["highpass_wind_hz"] if ratio > R["wind_ratio"]`) |
| Burst frames: energy under 150 Hz more than 8 dB over its median during speech, cut by the excess, 12 dB at most, on a low shelf that fades out at 180 Hz; `wind_burst_frames` counts frames with more than 1 dB of cut | VERIFIED | `SOUND_RULES["voice"]`: wind_burst_over_db 8.0, wind_burst_cut_db 12.0, wind_burst_hz 180; `voice_master`: `med` is the median of `lowE` over voiced frames, `burst = clip(lowE - med - 8, 0, 12)` smoothed over 3 frames, `shelf = clip(1 - f / 180, 0, 1)`, `wind_burst_frames = (burst > 1).sum()` (cold check reworded "shelves them down below 180 Hz" to say the cut is the excess) |
| Noise reduction stops at 12 dB on purpose; deeper sounds watery | VERIFIED | `SOUND_RULES["voice"]` denoise_max_db 12; sound.py docstring "12 dB at most, so no watery artifacts" |
| A wind-burst frame is one hop: 512 samples at 48 kHz, about 10.7 ms | VERIFIED / INFERRED | sound.py `nfft, hop = 2048, 512` and `SR = 48000`; 512 / 48000 = 0.0107 s |
| Wind cannot be fixed in post; fur on every outdoor capsule; stock foam rarely enough; lav under a thin layer plus fur in gusts | VERIFIED | R item 5 and WIND rule (The Broadcast Bridge, confidence medium) |
| Balcony corners: winds above 0.7 of rooftop speed almost only at corners (1986) | VERIFIED | R item 6 (J. Wind Engineering 1986, doi 10.5359/jawe.1986.29) |
| Partitions cut balcony wind 68% in one simulation | VERIFIED | R item 6 (large-eddy simulation study via x-mol) |
| iPhone 16 Wind Noise Reduction (Settings, Camera, Record Sound) is a fallback | VERIFIED | R item 7 (MacRumors) |
| Record 10 seconds and listen on headphones before take 1 | VERIFIED | R rule "AUDIO CHECK" (house rule derived from The Broadcast Bridge) |
| Room order: mic close (verified), then furnished room and blankets (house) | VERIFIED | R rule "ROOM": "(2) and (3) are house practice, not verified this run" |
| Audio 48 kHz | VERIFIED | R item 16 and rule "AUDIO FORMAT" (YouTube Help 1722171); the kit resamples anyway (`sound.read_audio` at `SR = 48000`; `assemble` encodes `-ar 48000`) |

## Light and exposure

| Claim | Status | Source |
|---|---|---|
| Finish table: sky pulled above 0.66, at most 0.45 EV; face lifted toward 0.52, at most 0.30 EV; clipped means luma above 0.985; sky moves on above 0.03 sky share | VERIFIED | `tools/studio/finish.py` `FINISH_RULES` (sky hot_from 0.66, ev_max -0.45; face target_luma 0.52, ev_max 0.30), `measure` (`L > 0.985`), `plan` (`sky_on: sky_share > 0.03`) |
| `longform` runs the finish only when the layers file has a `finish` entry | VERIFIED | `longform.py` line 198 `if L and L.get("finish"):`; profile `vsl` by default for a dict entry |
| Clipped share: nothing recovers it; above 0.002 it only switches on halation, which the `vsl` and `reel` finishes leave off | VERIFIED | `finish.plan`: `hal = sky_share > 0.03 or clipped_share > 0.002`, then `halation: hal and pr.get("halation", True)`; `FINISH_PROFILES` `vsl` and `reel` set `"halation": False` (cold check: the old "nothing" missed the brand-film glow) |
| Nothing in the kit tone-maps | RUN | cold check: `grep -rn "tonemap\|zscale" tools/studio/*.py` found nothing; `finish._decode` uses `scale=in_color_matrix=bt709:in_range=tv` |
| Bright colourless cloud or wall counts at half weight | VERIFIED | `_sky_mask` white term, `white_lo` 0.80, `white_share` 0.5 |
| A face at 0.33 reaches only about 0.41; a face under about 0.40 uses the whole lift | INFERRED | 0.334 x 2^0.30 = 0.411; `face_ev = clip(0.8 x log2(0.52 / f), 0, 0.30)` reaches the cap at f = 0.52 / 2^0.375 = 0.401 |
| A sky over about 0.86 uses up the 0.45 EV cap | INFERRED | `sky_ev = max(-0.45, -(sky - 0.66) x 2.2)` hits the cap at 0.66 + 0.45 / 2.2 = 0.8645 |
| Window key 30 to 45 degrees to one side, a little above eye level; fill up to half the key; too much fill looks flat | VERIFIED | R item 10 and LIGHT rules (Three-point lighting, Wikipedia, 2026-10-28) |
| One LED panel at 45 degrees; Elgato Key Light 2900 to 7000 K | VERIFIED | R item 11 (elgato.com) and LIGHT rule |
| One coloured lamp in the background, darker than the face (low confidence) | VERIFIED | R item 25 (Gadzhi editing guide, confidence low) and SET rule |
| Blackmagic Camera free on iOS and Android, Android limited to Samsung Galaxy and Pixel; false color pink, green, red; zebras | VERIFIED | R item 12 (blackmagicdesign.com) and EXPOSURE rule |
| Final Cut Camera as the Apple alternative | VERIFIED | R item 13 (Apple guide v2.4) |
| The kit renders at 30 fps; every platform is 30; assemble re-times beats to 30 | VERIFIED | `tools/studio/common.py` `FPS = 30`; `tools/studio/platforms.py` every entry `"fps": 30`; `assemble.py` encodes each beat with `-r 30` |
| A 24 or 25 fps take gets frames repeated to fill 30 | INFERRED | ffmpeg's `-r 30` output raises the rate by duplicating frames; not tested on a 24 fps take |
| Never mix frame rates | VERIFIED | R item 16 and rule "FRAME RATE" |
| Shutter about 1/(2 x fps), 1/60 at 30; 1/100 to 1/120 for tracked hands (inference); multiples of 1/60 against flicker (house, unverified) | VERIFIED | R item 15 and rule "SHUTTER" |
| Daylight 5600 K, Tungsten 3200 K; never mix daylight and warm bulbs | VERIFIED | R item 13 presets and rule "WHITE BALANCE" |
| Stock iPhone: AE/AF Lock by tap and hold, swipe down; Lock White Balance under Settings, Camera, Record Video (iOS 17 and later) | VERIFIED | R item 14 (iPhone Photography School; nerdschalk) |
| HDR off: the finish reads every clip as BT.709 with no tone mapping; the phone setting is unverified | VERIFIED | `finish.py` `_decode` ("scale=in_color_matrix=bt709"); R rule "HDR" (house, unverified) |
| Mirrorless: same numbers, timecode where the mic has it, standard picture profile | VERIFIED | R rule "MIRRORLESS" (picture-profile advice is house) |
| The kit has no log-to-Rec.709 conversion | VERIFIED | `tools/studio/grade.py` `PRESETS` are looks (sma_pro, btc_ember, clean, cinematic); no log input transform anywhere in grade.py |

## Framing

| Claim | Status | Source |
|---|---|---|
| Widest 9:16 crop of 16:9 is 31.6% of the width: 1215 of 3840 px, 607.5 of 1920 px; 15.8% each side of the face | INFERRED | arithmetic: (9/16) / (16/9) = 0.3164; 2160 x 9/16 = 1215; 1080 x 9/16 = 607.5; half is 0.158; matches R plan rank 4 ("31.6% of a 16:9 width (607.5 of 1920 px; 1215 of 3840 px) [derived]") |
| A reel is 1080 px wide | VERIFIED | `platforms.py` ig_reels, tiktok, yt_shorts `"w": 1080, "h": 1920` |
| A 1080p crop gets stretched to almost twice its width | INFERRED | 1080 / 607.5 = 1.78 |
| Punch-ins 1.10x and 1.20x in cut.py (used by `reel`), 1.15x by default in longform, 1.12x and 1.22x in `vsl_hero` | VERIFIED | `tools/studio/cut.py` `ZOOMS = (1.0, 1.10, 1.0, 1.20)`; `render.py` line 219 calls `cutmod.build` without `zooms`; `longform.py` line 150 `fmt.get("zooms", (1.0, 1.15))`; `formats.json` `vsl_hero` (line 649) `"zooms": [1.0, 1.12, 1.0, 1.22]` (line 673) |
| 4K covers a 16:9 punch-in; a 9:16 reel's 1.20x leaves 1012 of 1215 px, a slight stretch to 1080; a 1080p take would leave 506 | INFERRED | 3840 / 1.22 = 3147 px, over 1920; 1215 / 1.20 = 1012.5; 607.5 / 1.20 = 506.25; `render.py` line 116 crops `iw/{z}` from the tracked crop, then scales to the output width (cold check: the old "which 4K covers too" was not true for the reel) |
| The reel camera zooms toward a face shorter than 27 % of the frame height, up to about 1.29x from 4K | VERIFIED / INFERRED | `track.py` `camera`: `want = 0.27` (line 122), `z = want * ch0 / (med * h)`, `cap = max(1.0, min(zmax, (cw0 / out_w) * upscale))` (line 124) with `zmax` 1.30 and `upscale` 1.15; `render.reel` calls it with the default `zoom="auto"`; 1215 / 1080 x 1.15 = 1.294 |
| Film vertical when reels are the main output | VERIFIED | R rule "VERTICAL CROP MATH" |
| Eyes about a third down; house band 30 to 36 % from the top; more than 40 % down is a flag | VERIFIED | R item 17 (Headroom, Wikipedia, 2026-06-15) and HEADROOM rule ("the 30-36% band is house"); R plan rank 4 ("eye line 0.30-0.36 H, flag > 0.40 H") |
| Too much space above the head: move closer or tilt down | INFERRED | R item 17 ("too much leaves dead space"); framing geometry |
| Lens at eye level; low angle dominant, high angle weak | VERIFIED | R item 19 (Camera angle, Wikipedia, 2026-03-17) |
| Mid-chest up for gestures, widest gesture about 10 % inside the frame (house); rehearse it | VERIFIED | R rule "GESTURES IN FRAME" (house) |
| Lockup covers about the left 38 % of a 16:9 frame: 70 px in, 650 px wide at 1080 tall | VERIFIED / INFERRED | `tools/studio/layers.py` lockup defaults `lk.get("x", 70)`, `lk.get("width", 650)` scaled by H / 1080; (70 + 650) / 1920 = 0.375 |
| Busy backgrounds push labels onto the speaker | VERIFIED | R rule FILM-1 (lead room; PosterLayout; Gabbard; rule proposed) |
| On a 16:9 web VSL two caption lines sit from about 76 % to 89 % of the height; gestures stay above the bottom quarter | RUN | cold check: `platforms.caption_band(get("web_vsl"))` = (540, 950); `longform.py` line 286 caption box `band_bottom - 1.35 * csz` to `band_bottom + 0.12 * csz` with `csz = H * size * 1.85`: clean 0.771 to 0.889, impact 0.761 to 0.890 of the height (youtube: 0.742 to 0.872). The first pass took "the bottom fifth" from `skills/video/vsl-builder/SKILL.md` section 3, which the code does not match |
| 9:16 text box 6 % to 84 % across, 12 % to 70 % down, from the placement engine in `longform` with a layers file | VERIFIED | `tools/studio/placement.py` `PLACEMENT_RULES["safe"]["9:16"] = (0.06, 0.12, 0.84, 0.70)`; `skills/video/placement/SKILL.md` line 20: the engine runs inside `longform`, and "The `reel` command does not use it" |
| Meta asks for the bottom 35% free of text in paid reels | VERIFIED | `platforms.py` docstring (Meta Instagram Reels ad specs); R item 21 |
| Tripod; drift and moving plants add jitter | VERIFIED | R rule FILM-4 (rule proposed) |

## Delivery

| Claim | Status | Source |
|---|---|---|
| 6.9M edX sessions; informal desk with eye contact beat a studio lecture (2014) | VERIFIED | R item 22 (Guo, Kim and Rubin, Learning at Scale 2014) |
| House band 120 to 200 wpm in the Skool lesson checks; Guo 48 to 254, mean 136; aim 140 to 180 | VERIFIED | `FORMATS.md` lines 165 and 166, skool_lesson checks (also `formats.json` line 1137) ("speech 120 to 200 wpm (house band inside Guo's range)") and the same section ("observed 48 to 254 wpm, mean 136"); R rule "ENERGY" (140-180) |
| The cut splits only on a gap over 0.35 s; up to 0.15 s of air each side of a word | VERIFIED | `tools/studio/cut.py` `GAP_MAX = 0.35` ("dead air longer than this is removed"), `PAD_OUT = 0.15`, `in_point` start `s - 0.15` |
| Silence cutters pad 0.2 s each side | VERIFIED | R item 26 (auto-editor default margin 0.2 s) and rule "PAUSES" |
| One second of quiet between lines, hands at rest | VERIFIED | R rule "PAUSES" |
| Fluffs: restart the whole sentence (house) | VERIFIED | R rule "FLUFFS" (house) |
| Repeat key lines two or three times; assemble picks beats from any take | VERIFIED | R rule "REPEAT KEY LINES" (house); `skills/video/vsl-builder/SKILL.md` section 1 |
| Hormozi's batch days from a one-page run sheet; "an ounce of pre is worth a pound of post" | VERIFIED | R item 23 (Skool Games Q3 2025, YouTube aiPxj5np1mQ, 2025-12-02) |
| Label uses frames 0.35 s before to 0.8 s after the word; leaves when the hand drops more than 0.12 of the height, when the caption line changes or the next label comes, and 1.6 s after the word at the latest; stays at least 0.45 s | VERIFIED | `layers.py` `hand_events` lines 431 to 443 (`t_on - 0.35 <= t <= t_on + 0.8`, `top + 0.12 * H`, `b = min(nxt, ch_end, drop + 0.12, t_on + 1.6)`, `b = max(b, min(a + 0.45, nxt))`); cold check added the caption-line and next-label exits and the 0.45 s floor |
| Hold the gesture still about a second; whole hand in frame; mark the lines in the script | VERIFIED | R rules "LABEL GESTURES" (house) and FILM-3 (">= 1 s at the cue word") |
| Two labelled gestures per video at most, one per side of the screen; `L` and `R` are screen halves, not hands; one hand per half per frame | VERIFIED | `layers.py` reads `hd["labels"].items()` keyed L and R; `hands.py` `find` docstring "Screen-left half gives side L, right half side R" and keeps the best palm per half; `skills/video/placement/SKILL.md` section 5 ("Each half gives at most one hand per row"). Cold check replaced "one per hand" |
| Label region: left 62 % or right 62 % by the hand's position | VERIFIED | `layers.py` `half = (0.0, 0.0, 0.62, 1.0) if ... < W / 2 else (0.38, 0.0, 1.0, 1.0)` |
| Spoken slate plus one clap in frame | VERIFIED | R item 20 (Clapperboard, Wikipedia, 2026-10-04) and rule "SLATE" |

## B-roll

| Claim | Status | Source |
|---|---|---|
| The shot list, 8 to 10 seconds each, locked or slow, project frame rate, no personal details on screen | VERIFIED | R rule "B-ROLL LIST" ("house list, no verified source this run") |
| Additions: names blurred or fake, only a number you can source, written permission for testimonials | INFERRED | `CLAUDE.md` ("Never invent a number, a result, a testimonial or a claim"); house |
| longform fills the frame with each clip and crops the rest; a vertical clip keeps a thin band | VERIFIED / INFERRED | `longform.py` `render_overlay_clip` (`force_original_aspect_ratio=increase,crop`); a 9:16 clip scaled to 1920 wide keeps about a third of its height |
| B-roll plays silent | VERIFIED | `render_overlay_clip` passes `-an` |
| 3.2 s per cutaway; a reused clip starts 3.7 s further in; a 10 second clip gives two clean cutaways | VERIFIED / INFERRED | `longform.py` `BROLL_S = 3.2`, `used[src] = offset + BROLL_S + 0.5`; uses 0 to 3.2 and 3.7 to 6.9 s, a third would need 7.4 to 10.6 s |
| `.mp4`, `.mov`, `.mkv`, `.m4v`, used in name order, passed as `--broll` | VERIFIED | `longform.py` (`sorted(...)` over those suffixes); `cli.py` `--broll` |

## Verdict table

| Claim | Status | Source |
|---|---|---|
| PASS, LOOK, RESHOOT per take with the deciding number | INFERRED | house; modelled on R plan rank 4 ("per take PASS / WARN / RESHOOT with timestamps") |
| Sample rate: 48000 Hz passes, 44100 Hz is resampled, no audio track is a reshoot or a manual lav sync | VERIFIED | `sound.py` `SR = 48000` and `read_audio` `-ar` SR; `assemble.py` line 165 `-map 0:a:0` and line 167 `-ar 48000` (a take with no audio stream fails that map); the takes measured 44100 Hz (step 1 above) |
| Resolution: 2160x3840 when filmed vertical for reels | INFERRED | section 4's "film vertical instead" (R rule "VERTICAL CROP MATH"); the vertical twin of 3840x2160 |
| Face found in 50 % of frames or more, else no tracked camera and no hand labels | VERIFIED | `longform.py` line 179 and `render.py` line 233: `coverage >= 0.5`; `layers.py` line 395 `if not hd or not cam: return []` |
| Rumble share under 0.2 is clean (house), named as `docs/AUDIO_SPEC.md`; over 0.45 is wind (code) | VERIFIED | A `1_voice.studio_mic_chain.select_when` ("share of pause energy under 150 Hz < 0.2", house), and its kit copy `docs/AUDIO_SPEC.md` line 66 ("under 0.2 of the pause energy sits below 150 Hz"); `SOUND_RULES` wind_ratio 0.45 |
| Wind bursts: no pass mark in the code | VERIFIED | sound.py reports `wind_burst_frames` with no threshold; review.py does not check it |
| Clipped share 0.002 | VERIFIED | `finish.plan`: highlights count as hot when `clipped_share > 0.002` |
| Hands: anchor only to a hand fully in frame on every frame of a labelled word | VERIFIED | R rule HARD-4 (angle 1, 97% proposed) and R plan rank 7 check ("hands usable on 100% of marked gesture beats", house) |
| `in_frame`: all 21 points more than 3 % inside every edge | VERIFIED | `tools/studio/hands.py` `HAND_RULES["in_frame_margin"] = 0.03`; `inside = (...).all()` over the 21 landmarks |

## Honest limits

| Claim | Status | Source |
|---|---|---|
| No ingest command yet; the research plans one with PASS, WARN or RESHOOT and timestamps | VERIFIED | R plan rank 4 build ("New tools/studio/ingest.py (closer.py ingest <takes>)"); `cli.py` has no ingest parser (parsers: analyze, reel, longform, assemble, cover, formats, reframe, export, review, brands, platforms, lut, edit, compare, hands) |
| Noise under speech not measured on a raw take; research target 30 dB (house) | VERIFIED | R plan rank 4 ("speech SNR target >= 30 dB [house]"); A `1_voice.targets.pause_snr_db` min 30 (house); `voice_master` reports no speech-to-noise figure |
| The kit uses the camera file's first audio stream; no lav sync step | VERIFIED | `assemble.py` encodes each beat with `-map 0:a:0`; no sync or clap code in `tools/studio` |
| A second angle hides jump cuts; the kit cannot sync two cameras | VERIFIED / INFERRED | R item 24 and rule "SECOND ANGLE"; no multicam code in `tools/studio`, and a beat from another file plays that file's audio (`-map 0:a:0`) |
| Hands under `min_px` 2500 skipped; `in_frame` not read by the label code | VERIFIED | `layers.py` `hand_events` (`min_px` default 2500, no read of `in_frame`); `hands.py` `px` is the box area over the frame area times 1e6; `skills/video/placement/SKILL.md` section 5 says the same |
| Hand labels only on an assembled selects file with a tracked camera; otherwise nothing is drawn and nothing says so | VERIFIED | `layers.py` line 400 `ranges = [r for r in an.get("beats", []) ...]` (a plain `analyze` has no `beats`) and line 395 (no camera, no labels); `skills/video/placement/SKILL.md` line 121 |
| The Windows PY path follows `install.ps1`, not yet run on Windows | VERIFIED | `install.ps1` header |

Checker: `python3 skills/core/zero-context-auditor/scripts/audit_skill.py skills/video/filming-playbook/SKILL.md` returned "AUDIT PASS ... (47 figures sourced)" after the cold check on 2026-11-02 (39 before it). The script takes the SKILL.md path: given the folder it stops with `IsADirectoryError`. It finds the repo root by walking up to a `.git` folder, so in a kit downloaded as a ZIP (no `.git`) pass `--repo-root <kit folder>`, or every `tools/...` and `skills/...` path reports as not found. Every code block in SKILL.md was also run literally on the takes: six blocks in the cold check, each prefixed with the section 0 KIT and PY lines, from a scratch copy of the kit layout.

AUDIT: 133 claims, 85 verified, 29 run, 13 inferred, 6 verified with an inferred step, 0 user-stated, 0 gaps, 0 contradictions.
