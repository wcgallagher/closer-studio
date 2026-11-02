---
name: editor-brain
description: The skill to read first when someone drops a video in and says what they want ("make this a 90 second homepage VSL", "cut a reel from this", "make it cinematic", "make it better"). It is a human editor's judgement written as rules with numbers. It covers how each section should make the viewer feel (cut rate, zoom, music level and graphics density per section), what the eye sees (one focal point, the face carries trust, type sizes, contrast, placement), when the edit changes (motivated cuts and the breath rule), where the sound and the look are decided, the AI-slop tells to catch with their thresholds, and the loop (plan, preview, review, fix, compare with the last version, the owner listens). Runs `closer.py edit VIDEO "intent"` and hands each job to the skill that owns it. Use at the start of any edit, and when someone says "it feels rushed", "it looks like AI", "make it feel like a real editor cut it" or "make it premium".
---

# Editor brain

A good editor decides how each minute should feel before touching the timeline, then makes every cut, zoom, card and sound serve that feeling. This page is that judgement in numbers. Engine numbers come from the code (`tools/studio/edit.py`, `tools/studio/cut.py`, `tools/studio/finish.py`, `tools/studio/placement.py`, `tools/studio/sound.py`, `tools/studio/compare.py`). Craft numbers come from `docs/EDITOR_RULEBOOK.md` and sound numbers from `docs/AUDIO_SPEC.md`, where each one carries its source and how sure we are. When this page and the code disagree, the code wins and this page gets fixed.

Before any edit, read `HOUSE_RULES.md` and `EDITING_GRAMMAR.md` once. Before anything goes on screen, read `skills/sales/closer-mentality/SKILL.md` too. The kit's `CLAUDE.md` asks for all of them.

## 0. Start the job

Check ffmpeg first, because two problems stop a render on a fresh install:

- `ffmpeg -version` must say 8.1 or older. The engine passes `-filter_complex_script`, which FFmpeg 9.0 removed, so on 9.x every 16:9 render stops with an unrecognized option until the code moves to `-/filter_complex` (an open BLOCK in `docs/EDITOR_RULEBOOK.md` section 9). Homebrew and the gyan.dev Windows build both ship 9.0.2 today.
- Burned captions need libass. Homebrew's plain `ffmpeg` formula has none.

On a Mac, fix both with `brew install ffmpeg@7`, then put it first on the PATH with `export PATH="$(brew --prefix ffmpeg@7)/bin:$PATH"` (add that line to `~/.zshrc` to keep it). On Windows, use the gyan.dev 8.1.2 build; the steps are in `docs/EDITOR_RULEBOOK.md` section 9. On Linux, Ubuntu's apt ffmpeg (6.1.1 on 24.04) works.

Mac and Linux:

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
mkdir -p "$KIT/music" "$KIT/sfx"
"$PY" "$KIT/tools/closer.py" edit "$KIT/inbox/<file>" "a 90 second homepage VSL, premium" \
  --out "$KIT/output/<job>" --brand btc --music-dir "$KIT/music" --sfx-dir "$KIT/sfx"
```

Windows (PowerShell). Set up once from the kit folder with `powershell -ExecutionPolicy Bypass -File .\install.ps1`, which writes the venv and the kit path; its own header says it has not yet been run on a Windows machine, so report anything that fails.

```powershell
$KIT = Get-Content "$HOME\.closer-studio\kit_path"; $PY = "$HOME\.closer-studio\venv\Scripts\python.exe"
New-Item -ItemType Directory -Force -Path "$KIT\music", "$KIT\sfx" | Out-Null
& $PY "$KIT\tools\closer.py" edit "$KIT\inbox\<file>" "a 90 second homepage VSL, premium" --out "$KIT\output\<job>" --brand btc --music-dir "$KIT\music" --sfx-dir "$KIT\sfx"
```

The kit ships no `music` or `sfx` folder. Put licensed tracks in `music` and CC0 effects named `<role>__<name>.wav` in `sfx` (`docs/AUDIO_SPEC.md` section 6 lists them). An empty `music` folder means no bed and no ranking. An empty `sfx` folder means every effect falls back to the synthesized set. Add `--no-render` to get the plan without a cut.

What it does (`tools/studio/edit.py`):

1. Reads the sentence into decisions, each with its reason in plan.json `why`. The format is the first rule that matches, in this order: VSL words (vsl, sales video, homepage, landing page, hero video), then ad words, then reel words, then YouTube words, then lesson words. Nothing named means `yt_authority`, with the brand finish and its heavier grain. So "make it cinematic" and "make it better" get the YouTube format: for a sales video, say VSL in the sentence. "An ad for my homepage" becomes a VSL. The dialect: energy words (nelk, hormozi, hype, energy, fast, punchy, loud, viral) are checked before premium words (gadzhi, cinematic, premium, documentary, luxury, clean, elegant, minimal, apple), so "premium but fast" gets the energy dialect. A length ("90 seconds", "2 min") is recorded in `why.length_s` but nothing cuts to it yet: choose the window yourself. "2-minute" with a hyphen is not read.
2. Analyses the footage (words, pauses, face track) and measures words per minute.
3. Writes layers.json: the finish profile, the breath, the sound sections, the best-scoring track and the effects folder.
4. For 16:9 formats, renders a preview with `longform` and runs the review. Vertical formats print the `closer.py reel` command instead, and the reel cutter does not read layers yet, so the breath, finish and sound sections below apply to 16:9 jobs only.

Format defaults it writes (`DEFAULTS`):

| Format | Platform | Voice over music (LU) | Sentence breath (s) | Finish | Dialect |
|---|---|---|---|---|---|
| `vsl_hero` | web_vsl | hook 11, body 14, CTA 12 | 0.45 | vsl | gadzhi |
| `paid_ad_reel` | ig_reels | 12 | 0.3 | reel | nelk |
| `organic_reel` | ig_reels | 16 | 0.3 | reel | nelk |
| `yt_authority` | youtube | 20 | 0.4 | brand | gadzhi |
| `skool_lesson` | youtube | 20 | 0.4 | vsl | gadzhi |

For `vsl_hero` with four or more sentences it places the sections itself. The hook is the first sentence and the body starts at the second; the CTA starts at the sentence 80% of the way through. Move them to the real turn and the real ask after reading the transcript. A speaker over 200 words per minute gets at least 0.45 s of breath (persuasion peaks near 181 wpm in the research the code cites).

`edit` has no `--audience` flag, so it lints on-screen words for the brand's usual viewer. A client-facing Set More Annuities video must never show the word annuity: after the plan, render it with `"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/<file>" --out "$KIT/output/<job>" --format vsl_hero --brand sma --audience client --layers "$KIT/output/<job>/layers.json"` (on Windows start with `& $PY` and use backslashes). It reuses the analysis already in the job folder.

Then read plan.json and transcript.txt before you change anything.

## 1. How it should feel: one arc, section by section

Label each section by reading the transcript (hook, problem, proof, offer, ask). Each label sets the dials below. The table is the research target; the right column is how you set it today, since there is no automatic arc engine yet. Treat every number here as a starting value to A/B, not a law.

| Section | The viewer should feel | Visual change | Framing | Music | Graphics | Set it with |
|---|---|---|---|---|---|---|
| Hook | "this is for me", curious | message with the face on screen by 3 s on reels, ads and `vsl_hero` (its `hook_deadline_s` is 3 and its brief says spoken from frame one), promise paid by 10 s; on YouTube the hook by 15 s | effects allowed on each visible event, inside the dialect's budget | vsl_hero 11 LU under the voice | the densest part: in a VSL of 2 minutes or more, 1.5 to 2 times the body rate across the first 60 s; in a 60 to 150 s homepage VSL, the first 15% | the format's punch clock; the opening lockup in layers |
| Calm explaining | clarity, trust | about every 4 s | gentle alternation (1.00 and about 1.08) | body 14 LU | about 2 per minute | not settable per section today: the `vsl_hero` clock (every 2.6 s, 1.00 / 1.12 / 1.00 / 1.22) runs everywhere, and a `zoom` hold can only calm a stretch to one framing |
| Pain, the problem in their words | understood; let it land | holds of 5 to 10 s on the face, no B-roll over first-person lines | tight and still, about 1.10, no drift | out, or 20 LU or more under | at most 1 new element per sentence | a `zoom` hold over the stretch (a pause cut inside it shows as a jump at one scale); a `music.mute` window, or a section with `vm` 20 followed by one that returns to the body level (a section runs until the next one's `from`) |
| Build, the proof stack | momentum, belief | the interval steps down, about 4 then 3 then 2 s | kicks of 1.10 to 1.15 on emphasised words only | rising toward 12 LU | proofs in ascending size, the biggest last | chips or scenes on the proof words. The punch clock already lands framing changes on emphasised words. A `kicks` entry is an 8% zoom pulse that settles in 0.27 s plus a section-change sound, which the slop table flags as a reversal inside 1.0 s: on a VSL use it at the real turn only |
| Payoff, the number or the offer | it hits | the strongest visual on the word or up to 0.15 s early; a card holds 3 to 7 s | one effect hit at most | silent 0.5 to 1.0 s before the line, the line dry, back on the next downbeat | one | a `breath.after` beat on the line before; a `music.mute` window with a lead (section 4) |
| Resolve and the ask | calm certainty | longer shots, 5 to 8 s | wide again, 1.00 | CTA 12 LU (lower the cta `vm` for a louder bed: the code's 2 dB CTA lift cancels out, section 4) | one clean graphic | the `cta` section. A `cta_riser` sfx event builds tension, so on a calm ask leave it dry unless an A/B says otherwise |

Shape rules on top of the table:

- The whole piece is a "man in a hole": a problem dip, a rise, a smaller objection dip, a rise to the offer. Read the transcript's mood sentence by sentence; if it is flat, say so before cutting, because editing cannot add an arc the words lack.
- Long-form runs in quarters of about 25% each. Change comes slowly at the open, faster across the first quarter, steady through the middle half, fastest at the start of the last quarter (the offer and payoff), and slower again after the ask. Put a re-engagement beat (a demo or a sourced proof) near 3:00 and 6:00, and keep each block self-contained within about 6 minutes.
- A 60 to 150 s VSL compresses the same shape: hook 0 to 15%, problem 15 to 40%, proof and solution 40 to 75%, offer and ask 75 to 100%. Music is strong over the open and mostly out under the problem. From the proof on it builds to the end.
- When the words are high-arousal (pain, fear, a big claim, a price), slow the cuts and zooms and hold back on graphics. Fast pace on arousing content overloads the viewer. When the words are calm, add change with related edits (a punch-in on the same shot) rather than new elements.
- Viewers over 55 lose the benefit of fast pacing, so hold numbers and the offer on screen longer for them.
- Order proof by size and put the most important claim last in any list.

## 2. What they see

- One focal point. Beyond the face, any frame holds at most one caption block and one graphic. Decorative text counts as an element, because text pulls the eye whatever it says.
- The face carries trust. Full-frame B-roll only where the picture explains faster than the face, never over a claim or an emotional line (a credibility line is a claim); cutaways of 2 to 4 s. In `vsl_hero`, full-screen cards cover at most about half the runtime and the speaker is back on camera at least every 15 s (`formats.json`).
- After a cut the eye goes to the face within about 500 ms. A new element appears on the cut or waits at least 0.5 s, and two new elements never arrive in the same 0.5 s. An element animates in, then holds still: no idle pulses, and one thing moves at a time.
- One highlighted word per caption chunk. A stat card shows the number and a 1 to 3 word label, never the spoken sentence again.
- Type sizes on 9:16 (1080 wide): nothing under 32 px, chips and labels 48 px or more, captions 64 to 110 px, a one-word slam up to about 180 px. On 16:9 watched on a phone, must-read text 54 px or more, comfortable from 80 px.
- Contrast at least 4.5:1 against the brightest pixels behind the text (WCAG). When it fails, add a dark plate first. If that is not enough, add a stroke of 3 px or more at 1080, and a shadow only as the last step. Never change the text colour frame by frame.
- Eyes in 9:16 sit at 30 to 38% of the frame height, centred.
- Placement goes through the engine: `skills/video/placement/SKILL.md`. It never types coordinates. A box with more than 2% of its area over the face, or more than 1% over the captions, fails the review (`PLACEMENT_RULES`, `place()`). Plain text over a background brighter than 0.62 mean luma costs extra, so the engine moves it somewhere darker; chips are drawn on a plate.
- Motion: entrances 250 to 400 ms, easing cubic-bezier(0.05, 0.7, 0.1, 1.0); exits 150 to 200 ms, (0.3, 0, 0.8, 0.15); never linear on position or scale. Premium springs bounce 0 to 0.15; one deliberate slam per scene may reach 0.3; never above 0.4.
- Captions: the looks and the band are in `skills/video/caption-styles/SKILL.md`. Premium pieces use one family, sentence case, a weight shift on the spoken word and no bounce; short-form hooks may use caps with one keyword colour.

## 3. When the edit changes

Every cut needs a reason: new information, an emotion shift, rhythm, dead air or a flub, or a re-engage. A cut with no reason goes. When two rules fight, settle it in Murch's order: emotion, story, rhythm, eye-trace, then the 2D and 3D layout of the frame. Cut at the end of a thought or a gesture. Never cut inside a number or a demo move, and never across a facial reaction.

What the engine does (`tools/studio/cut.py`): dead air over 0.35 s is cut, pieces under 1.0 s merge into their neighbour, and inside a breath the framing changes every `punch_every_s` seconds (2.6 in `vsl_hero`, 4.5 when a format sets none), moved up to 0.8 s early to land on an emphasised word. Framings alternate through the format's `zooms`. The punch clock is fixed, so read beats.txt for a ticking pattern (section 6) and break it with `zoom` holds.

The breath rule. Without it the cutter removes nearly all the air between sentences: in a test, a 1.2 s pause between two sentences came out at 0.06 s. A fast talker needs more room, not more trimming. Set it in the layers file (`tools/studio/layers.py` loads it, `tools/studio/longform.py` passes it to the cutter):

```json
"breath": {"sentence": 0.45, "after": [["Pretty@15.15", 0.9], ["Finally@82.99", 1.0]]}
```

- `sentence`: every sentence end where the speaker paused more than 0.35 s keeps this much, 60% after the line and 40% before the next. A shorter pause is left as it was. The research band for a VSL is 400 to 600 ms, so the default 0.45 sits inside it. Gaps inside a sentence are still trimmed tight.
- `after`: a held beat after the named word, for the moment before a claim or the ask (a price is a claim). A VSL gets 700 to 1200 ms there, at most 2 per minute.
- A beat needs a real pause in the take. Where the speaker paused less than 0.35 s nothing changes (a 0.25 s pause stayed 0.25 s). Where they did pause, the beat can run longer than the pause, because the room tone either side is reused (a 0.6 s pause with a 1.0 s beat came out at 0.96 s). No pause at the spot means another take or a re-record (`skills/video/filming-playbook/SKILL.md` covers pauses between lines).
- Never speed a voice up to fix pacing (`EDITING_GRAMMAR.md`: never past 1.05x).

## 4. How it sounds

Everything about the mix belongs to `skills/video/sound-director/SKILL.md`, with the readable spec in `docs/AUDIO_SPEC.md`. From here, four decisions and one warning:

- The sections and their voice-over-music targets, moved onto the real turn and the real ask. `edit` writes them from its `DEFAULTS` (the same numbers as `SECTION_PRESETS` in `tools/studio/sound.py`, which nothing else reads). A section with no `p10` gets its `vm` minus 6 as its floor.
- Where the music drops: a `music.mute` window before each reveal and the ask, at most 3 per video. A window `[from, to]` takes the bed out 0.4 s before `from`. Give it a third value, the lead in seconds, for more: `["Finally@82.99", "<last word of the line>@<s>:end", 0.8]` is silent 0.8 s before the line and dry through it. The bed comes back on the next bar line if one falls within 1.0 s of the window's end.
- One dialect for the whole video: gadzhi (premium, most cuts dry) or nelk (energy).
- The track: the owner picks it by ear from the top three in plan.json `music_ranked`.
- The warning: the code adds `cta_lift_db` (2 dB) to the bed across the `cta` section, then the section calibration sets every section back to its own target, so the lift cancels out (measured on test stems, 2026-11-02). For a louder bed under the ask, lower the cta section's `vm`.

The engine never listens. Report "measured, not listened".

## 5. The look

The finish is measured, not a recipe (`tools/studio/finish.py`). It first measures four things (face brightness, sky brightness, how much of the frame is sky, how much clips), and every move scales with what it found. The face is lifted toward a luma of 0.52 by at most 0.30 EV and never darkened, and a well-exposed face gets no lift at all. A sky is pulled down only when it measures above 0.66 luma, by at most 0.45 EV.

| Profile (`FINISH_PROFILES`) | Halation | Grain | Vignette (corner, computed) |
|---|---|---|---|
| vsl | off | 0.007 | 0.12 (about -0.18 stops) |
| reel | off | 0.006 | 0.10 (about -0.15 stops) |
| brand | when the sky covers over 3% of the frame or over 0.2% clips | 0.012 | 0.16 (about -0.25 stops) |

Before the finish, every long-form piece already goes through `grade.POST` in `tools/studio/grade.py` (applied in `tools/studio/render.py`): two unsharp passes and an ffmpeg vignette at a=0.35, measured at -0.36 stops. So a VSL's corners land near -0.54 stops in total, and the double sharpening is the rulebook's open TX-04 item, the one that makes a face look crunchy and AI-made. Look at the face at full size before you ship.

A sales VSL sells trust in a person, so it gets the clean finish: a natural grade, no halation, no letterbox, light grain that must survive the web player's re-encode. Teal-orange belongs to B-roll and brand moments only. The skin-hue check warns and never auto-corrects. No generative face fixes: no eye-contact correction, no synthesized jump cuts, no face swap, no beauty filter.

## 6. AI-slop tells

Check the beat map (beats.txt in the cut folder) and the render for these. Thresholds are from `docs/EDITOR_RULEBOOK.md`, mostly house values to tune on A/B.

| Tell | Threshold |
|---|---|
| Engine-placed events on a metronome (punch-ins and overlays) | intervals vary (CV of 0.5 or more); no more than 2 intervals in a row within 10% of each other |
| A zoom landing mid-clause | a scale change starts at a clause start (within 80 ms before it) or after a pause of 250 ms or more |
| Every jump cut at the same scale | scale steps of 0.10 or more; no more than 3 cuts in a row at one scale |
| Zoom pulses everywhere | no scale reversal within 1.0 s; in VSL and brand work, at most 1 animated push-in per 30 s |
| Breathless pacing | sentence gaps vary (CV 0.3 or more) and no more than 70% of them under 120 ms |
| Cutting into an emotional or punchline beat | at least 0.6 s held after the last word of that line |
| Graphics everywhere | every body graphic has a trigger: a spoken number, proof, a new concept, or more than 20 s since the last visual |
| The same effect again and again | never the same sound, whoosh, zoom curve or chip animation more than 3 times in a row. The engine takes files of a role in turn, so put at least two files per role in the `sfx` folder: with one file, or the synthesized fallback, every event of that role sounds the same |
| A whoosh on every cut | effects on no more than 25% of cuts; a dry cut is a choice |
| Rainbow karaoke and auto-emoji | one accent colour and one accented word per caption; no emoji outside reels |
| Everything dead centre | no more than 50% of overlay centres within 5% of the frame centre (16:9 work) |
| Stock B-roll that does not match | after the grade, within 12% of the A-roll's mean brightness |
| Squashed, robotic voice | compression ratio 4:1 or lower |
| Invented numbers on screen | zero: every number on screen comes from the footage or the brand file |

What the review already fails on a 16:9 job (`tools/studio/review.py`): no speech by the format's hook deadline, a static stretch over 8 s, a graphic on the face or the captions, banned words, a voice buried under the music (a median under 9 LU, or the worst 5% under 3), and more than 12 effects a minute. The reel review also fails captions on the chin.

## 7. The loop

1. **Plan.** Run `edit` (with `--no-render` if unsure), read plan.json `why`, read the transcript, label the sections, then write the beats, holds, drops, chips and scenes into layers.json by hand. Graphics only where the words name a thing or a sourced number.
2. **Preview.** Re-run with the layers file through the format skill (below), as a preview first.
3. **Review.** Read report.md, look at sheet.jpg yourself, fix every FIX, render again. Stop after 3 self-review passes and report what is still open. Say done only on all PASS.
4. **Cold review.** Anything client-facing or paid gets a fresh second viewer: `skills/video/cold-review/SKILL.md`.
5. **Compare with the last version.** `"$PY" "$KIT/tools/closer.py" compare old.mp4 new.mp4 --out "$KIT/output/<job>/compare" --labels v8,v9` (Windows: `& $PY "$KIT\tools\closer.py" compare old.mp4 new.mp4 --out "$KIT\output\<job>\compare" --labels v8,v9`) writes compare.html: synced players with a wipe, and both timelines drawn over each other (cuts, loudness, picture, faces). A blind verdict shows when judge.json sits in that `--out` folder. A blind judge sees no file names or plan and scores the evidence before giving a verdict. It runs both orders, and a win counts only if it holds both ways. The full protocol, with the blind panel, is `skills/video/compare-cuts/SKILL.md`; the research behind it is in `docs/EDITOR_RULEBOOK.md` section 8.
6. **The owner listens.** Blind A/B clips of 10 to 15 s from the same section, matched in loudness, on a phone speaker and on earbuds. Move the matching rule toward the winner in that video's layers file, never in the code.

## 8. Devil's advocate for sales VSLs

These rules are the most likely to backfire on a sales VSL, where the viewer has already clicked and is weighing a money decision. Each one has the test that would overturn it.

- **More motion converts better.** The energy numbers come from short-form entertainment built for cold scrollers. Persuasion depends on the viewer processing the argument, and effects compete for that attention; shake and flash read as hype on a financial product. VSL setting: 2 to 4 graphic moments per minute, only on numbers or proof, plus one on the ask; punch-ins only to hide jump cuts; soft effects, never shake or flash. Test: the same VSL at equal length, restrained against energetic, on the live page, at least 500 plays per side before reading play-through, bookings read only with a significance test.
- **Tighter is better.** A fast talker is already above the 181 wpm persuasion peak, and trimming can only raise the rate. VSL setting: sentence gaps of 400 to 600 ms with beats before price and claims, and no pause caps in the first minute. Test: a tight cut (250 to 350 ms gaps) against a breathing one (450 to 600 ms).
- **Punchy captions are readable.** One-to-three-word caps chunks are a short-form convention, and every size floor here is a minimum for young eyes. Muted autoplay makes captions carry the opening. VSL setting: phrases of 4 to 7 words, up to 42 characters, sentence case, at least 52 px on 16:9.
- **A cinematic finish reads premium.** Web players re-encode at low bitrates and grain turns to mush; a 2.39:1 letterbox blacks out a quarter of a 16:9 frame and shrinks the face. VSL setting: the vsl profile above.
- **A skin target is truth.** The hue target rests on a chart and a rule of thumb, and real skin spreads widely. Warn only; after the owner approves 3 to 5 frames, measure against his own reference instead.
- **Where this kit's own settings pull the other way.** The `vsl_hero` registry entry punches every 2.6 s and alternates 1.00, 1.12, 1.00, 1.22, busier and deeper than the restraint above and past the 112% punch in `HOUSE_RULES.md` unless the source is 4K. Every piece also gets a slow push of 2.5% (`tools/studio/longform.py`), where the slop table allows one animated push-in per 30 s. Its captions are `impact` (caps, 2 to 4 words, one colour accent), not the phrase captions above; the closest look is `--captions serif` on `longform` (sentence case, no highlight) with `"captions": {"words": [4, 7]}` in layers.json. Its brief asks for music at least 13 dB under the voice, while the presets put the hook at 11 and the CTA at 12, and the review passes a median of 9. The finish lifts the face through a tracked soft window, while the rulebook's skin rule prefers whole-frame curves; the lift is capped and a well-lit face gets none, but the owner should judge it. The 55-plus audience applies to client-facing VSLs; the `vsl_hero` homepage speaks to agents. And on a VSL the best music may be none.

## 9. Who owns what

| The job | Skill |
|---|---|
| What to make, which format, the brief | `skills/strategy/format-brain/SKILL.md` |
| A VSL cut from several takes, cards that land on words, the layers file | `skills/video/vsl-builder/SKILL.md` |
| Funnel VSL structure, proof, CTA placement and compliance | `skills/video/funnel-vsl/SKILL.md` |
| YouTube videos, lessons, replays | `skills/video/longform-editor/SKILL.md` |
| Reels, shorts, TikTok | `skills/video/reel-editor/SKILL.md` |
| Caption looks and the caption band | `skills/video/caption-styles/SKILL.md` |
| The dialects and the measured clock | `skills/video/edit-grammar/SKILL.md` |
| Where text and labels go | `skills/video/placement/SKILL.md` |
| Voice, music, effects, the mix | `skills/video/sound-director/SKILL.md` |
| A fresh second viewer before shipping | `skills/video/cold-review/SKILL.md` |
| Comparing two cuts, the blind A/B | `skills/video/compare-cuts/SKILL.md` |
| How to film the next take, and checking raw takes | `skills/video/filming-playbook/SKILL.md` |

## Rules

- Decide the feeling of each section before touching a cut, and say it in plain words in the plan.
- Never put a number or a claim on screen that the footage or the brand file does not contain.
- The code's numbers are the rules. A change goes into the code or the layers file first, then onto this page and into AUDIT.md.
- Measured, not listened: the owner judges taste.
