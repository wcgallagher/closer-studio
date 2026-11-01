---
name: skool-content
description: Makes every video a Skool community needs and says where each one goes. The welcome video, Classroom lesson modules, weekly call replays, win and testimonial clips, community post clips and the cancellation video, each with its format id, its engine command, what goes in the thumbnail and the title, how Skool hosts it (native upload, timestamps as chapters, auto captions, pins, drip and level gates) and the weekly cadence that keeps members active. Use when someone says welcome video, module, lesson, classroom, replay, "post this win", "for the Skool", or asks why members go quiet.
---

# Skool content

Five formats cover a community. `FORMATS.md` holds the reasoning and the sources, `EDITING_GRAMMAR.md` the cut rules.

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
```

The table must list `skool_welcome`, `skool_lesson`, `replay`, `testimonial_clip` and `skool_cancel_video` (else `formats.json` is missing). Brand `btc`, or `sma` for the agent community; read `skills/sales/closer-mentality/SKILL.md` first.

Nothing is burned into a Classroom video: Skool generates English closed captions on a native upload and the Transcript addendum makes it searchable, so the Classroom formats carry captions none as their default and `--format` loads it. Burned captions belong only on the 9:16 clip that leaves for the feed.

## 1. Welcome video (`skool_welcome`, 90 to 180 s, 150 ideal)

The creator at the desk, looking into the lens. Beats: who I am and who this is for (0:00 to 0:30); the tour of the feed, the Classroom, the calendar and the Start Here post (0:30 to 1:15); the first lesson by name (1:15 to 1:45); when the next call is and that replays get posted (1:45 to 2:15); one step, open lesson 1 now, in the last 15 s.

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/welcome.mp4" --out "$KIT/output/welcome" \
  --brand btc --format skool_welcome --fillers cut
```

It goes in the Pro onboarding plugin and a pinned Start Here post, paired with the AutoDM (1 to 5 minutes after joining; one open question, one closed). The review wants "start here", "lesson", "call" and "replay" spoken by 2:15 and one ask in the last 20 s. Why it exists: a lesson finished in week one predicts completion, 78.2% against 17.2% (Ruzuku).

## 2. Lesson modules (`skool_lesson`, 2 to 12 min, 6 ideal)

One micro-objective per page; the title names the skill and the first 15 s state it. Target 6 min with 12 as the ceiling; the review marks "length fits the format" as a fix past 720 s, so split long recordings at natural breaks. Beats, 6 min cut: the objective (0:00 to 0:15); the concept to about 3:30, slides cut with the talking head and drawn over for how-to; a worked example to end minus 60 s; a 10 to 15 minute action step plus "post the result" in the last 45 to 60 s. Cut fillers and pauses over 1 s and keep the energy up; the median viewer leaves by minute 6 whatever the length (Guo, 6.9M sessions).

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/m2l3.mp4" --out "$KIT/output/m2l3" \
  --brand btc --format skool_lesson --fillers cut \
  --chapters "0:The objective,15:The concept,210:Worked example,300:Your action step"
```

Hosting, per Skool's docs: native upload, which the help page says is included in the plan (200 pages per course, unlimited courses). Paste chapters.txt under the video; the timestamps become chapters (required over 360 s; YouTube's rules apply, 00:00 first, at least 3, each 10 s or more, so an unlisted YouTube fallback also works with Allow Embedding on; a Loom embed needs comments and reactions off). Pin one discussion post under every lesson (12 pins per page, 3 on the feed) for the action-step result: courses with lesson-level discussion finished at 50.9% against 37.3%, with assignments at 59.1% against 42.4% (Ruzuku). Gate the Classroom: a short Quick Start open to all, later pages dripped by days since joining, deeper courses behind Level 2 (5 points) or Level 3 (20 points), one point per like.

## 3. Weekly call replays (`replay`, 30 to 45 min, 40 ideal)

A recurring Skool Call (short title and cover image; 30 min to 24 h), recorded, downloaded inside 14 days, posted the same day, then uploaded to a Classroom page with timestamps. Replays draw at least 10 times the live viewers (Skool Games, Q3 2025).

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/call_wk12.mp4" --out "$KIT/output/call_wk12"
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/call_wk12.mp4" --out "$KIT/output/call_wk12" \
  --brand btc --format replay --fillers cut \
  --chapters "0:The promise,30:Block one,1200:Reset,1320:Block two,2100:Q&A" \
  --quotes "strongest line one|strongest line two"
```

Chapter times are seconds from the start; take them and the titles from transcript.txt, which `analyze` writes into the job folder. The review fails chapter titles no person wrote. Shape: first speech inside 10 s, a chapter every 2 to 5 min, a reset near minute 20 to 22 (Contrast: drop-off starts around minute 22), the ask spoken in the first and last quarters (Wistia: quarters 1 and 4 convert at 50 to 51% on 30 to 60 min videos), the Q&A tail trimmed.

## 4. Win and testimonial clips (`testimonial_clip`, 20 to 90 s)

The member's own words: their situation line by 0:03, where they were, what they did, the result with one specific.

```bash
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/win_member.mp4" --out "$KIT/output/win_member" \
  --brand btc --format testimonial_clip --platform ig_reels --style clean --safe ads --fillers cut
```

`--safe ads` applies the ad safe zones (the bottom 672 px of 1920 on Reels and Shorts, 660 px on TikTok). Meta wants the bottom 40% clear under a disclaimer, and the engine's results-vary card is still on the to-build list in `FORMATS.md` section 3, so place the card over the specific number by hand and keep that band clear. Name and role lower-third by 0:05, consent on file, no income figure framed as typical, no banned word in the disclaimer. It goes to Wins first. The ad library and the VSL proof block pull from there.

## 5. Community post clips

Raw, phone-to-face, one idea, under 60 s. Cut them from the replay pool; re-run the keeper with a hook per `skills/video/reel-editor/SKILL.md`:

```bash
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/call_wk12.mp4" --out "$KIT/output/wk12_clips" \
  --brand btc --format organic_reel --platform ig_reels --auto 3
```

Daily answers are short Loom videos (a Skool Games winner does 4 to 8 a day) in one batch per 24 hours; the best become Classroom pages.

## 6. Thumbnail and title

```bash
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/m2l3" --title "Objection prevention" --brand btc --out "$KIT/output/m2l3/cover"
```

Best face frame, title in the display face: thumbnail.jpg (1280x720) and cover.jpg (1080x1920). Course cover: face plus module name (Skool publishes no size; 1920x1080 is the house choice). Lesson title: the one skill in plain words, key words first. The unlisted YouTube copy follows the thumbnail rules: 1 to 4 words, at most 3 elements, 1 or 2 faces, bright and checked on a black phone screen, title under 100 characters.

## 7. Cadence

- One live recording session a week: long videos back to back, then open Q&A. Everything else is clipped from that pool; polish those, keep clips raw.
- Categories well under the 10 cap: Wins, Questions, Accountability, Intros, plus admin-only Announcements sorted by newest.
- At the cancel step, `skool_cancel_video` (45 to 120 s) in the cancellation plugin: the next call by date and one recent win, kept light, then one question and one ask. No pressure words.

## 8. Checks

`"$PY" "$KIT/tools/closer.py" review "$KIT/output/<job>"` re-runs the report; read report.md and chapters.txt, then open sheet.jpg. Lint follows `HOUSE_RULES.md` and the lint sets in `FORMATS.md`. Anything leaving Skool (an ad, VSL proof) also passes `skills/video/cold-review/SKILL.md`. Still unverified (house choices): upload size limit, cover pixel sizes, recording length cap, chapters on post videos.
