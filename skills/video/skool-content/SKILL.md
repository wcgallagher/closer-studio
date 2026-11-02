---
name: skool-content
description: Makes every video a Skool community needs and says where each one goes. The welcome video, Classroom lesson modules, weekly call replays, win and testimonial clips, community post clips and the cancellation video, each with its format id, its engine command, what goes in the thumbnail and the title, how Skool hosts it (native upload, timestamps as chapters, auto captions, pins, drip and level gates) and the weekly cadence that keeps members active. Use when someone says welcome video, module, lesson, classroom, replay, "post this win", "for the Skool", or asks why members go quiet.
---

# Skool content

Five registry formats cover a community: `skool_welcome`, `skool_lesson`, `replay`, `testimonial_clip` and `skool_cancel_video`. Older ids still resolve (`youtube_long` is `yt_authority`). `FORMATS.md` section 8 holds the reasoning and the sources; `EDITING_GRAMMAR.md` holds the cut rules.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
ls "$KIT/inbox"
```

Brand is `btc`. Use `sma` for the agent community. Read `skills/sales/closer-mentality/SKILL.md` before you write a title or an ask.

Nothing is burned into a Classroom video. Skool generates English closed captions on a native upload, and the Transcript addendum makes the page searchable, so the four Classroom formats carry captions none and `--format` loads it (`--captions none` says the same thing out loud). Burned captions belong only on the 9:16 clip that leaves for the feed.

The long-form review wants a layout change on the format's cadence (45 s on the welcome, 30 s on a lesson, 180 s on a replay, none on the cancel video) and counts only the cutaways it placed, not punch-ins. Chapter cards and quote cards count. So do clips from a `--broll` folder, 3.2 s each, cut in at sentence ends on the cadence. A plain desk shot with none of those gets a FIX on that line, so give the welcome and the lesson a `--broll` folder of screen recordings.

## 1. Welcome video (`skool_welcome`, 90 to 180 s, 150 ideal)

The creator at the desk, looking into the lens. Five beats: who I am and who this is for (0:00 to 0:30); the tour of the feed, the Classroom, the calendar and the Start Here post (0:30 to 1:15); the first lesson by name (1:15 to 1:45); when the next call is and that replays get posted (1:45 to 2:15); one step, open lesson 1 now, in the last 15 s.

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/welcome.mp4" --out "$KIT/output/welcome" \
  --brand btc --format skool_welcome --fillers cut --cta "Open lesson 1 now" \
  --broll "$KIT/inbox/welcome_tour"
```

`--cta` puts those words on the end card (otherwise the brand's default line). The B-roll folder holds the screen recordings of the tour. Then read transcript.txt in the job folder: "start here", "lesson", "call" and "replay" should all be said by 2:15, with one ask in the last 20 s. The file goes in the Pro onboarding plugin and a pinned Start Here post, paired with the AutoDM (1 to 5 minutes after joining; one open question, one closed). Why it exists: a lesson finished in week one predicts completion, 78.2% against 17.2% (Ruzuku).

## 2. Lesson module (`skool_lesson`, 2 to 12 min, 6 ideal)

One micro-objective per page. The title names the skill and the first 15 s say it. Target 6 min with 12 as the ceiling: past 720 s the review marks "length fits the format" as a FIX, never a hard stop, so split a long recording at a natural break and make two pages. Beats on a 6 min cut: the objective (0:00 to 0:15); the concept to about 3:30, slides cut with the talking head and drawn over for how-to; a worked example to end minus 60 s; a 10 to 15 minute action step plus "post the result" in the last 45 to 60 s. Cut fillers and pauses over 1 s and keep the energy up (speech 120 to 200 wpm, a house band inside Guo's observed 48 to 254). The median viewer leaves by minute 6 whatever the length (Guo, 6.9M sessions).

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/m2l3.mp4" --out "$KIT/output/m2l3" \
  --brand btc --format skool_lesson --fillers cut --title "Objection prevention" \
  --chapters "0:The objective,15:The concept,210:Worked example,300:Your action step" \
  --broll "$KIT/inbox/m2l3_slides"
```

Write the chapter titles yourself, starting at 0. `--chapters auto` only copies the first words of a sentence into each title, and the review marks "chapters written by a person" as a FIX until you replace them. `--title` is the thumbnail title, 1 to 4 words.

Hosting: native upload (Skool's help page says native hosting is included in the plan; 200 pages per course, unlimited courses). Paste chapters.txt into the text field under the video and the timestamps become chapters. Over 360 s they are required (house rule). YouTube's chapter rules apply, so an unlisted YouTube copy with Allow Embedding on also works: 00:00 first, at least 3 timestamps, in ascending order, each 10 s or more. A Loom embed needs comments and reactions off. Pin one discussion post under every lesson (12 pins per page, 3 on the feed) for the action-step result: courses with lesson-level discussion finished at 50.9% against 37.3%, with assignments at 59.1% against 42.4% (Ruzuku). Gate the Classroom: a short Quick Start open to all, later pages dripped by days since joining, deeper courses behind Level 2 (5 points) or Level 3 (20 points), one point per like.

## 3. Weekly call replay (`replay`, 30 to 45 min, 40 ideal)

A Skool Call on the calendar (a short title, a cover image, a duration from 30 min to 24 h, set to recur), recorded, downloaded inside 14 days, posted the same day, then uploaded to a Classroom page with timestamps. Replays draw at least 10 times the live viewers (Skool Games recording, Q3 2025).

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/call_wk12.mp4" --out "$KIT/output/call_wk12"
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/call_wk12.mp4" --out "$KIT/output/call_wk12" \
  --brand btc --format replay --fillers cut --cta "Come to the next call" \
  --chapters "0:The promise,30:Block one,1200:Reset,1320:Block two,2100:Q&A" \
  --quotes "strongest line one|strongest line two"
```

Chapter times are seconds from the start. Take them and the titles from transcript.txt, which `analyze` writes into the job folder; the second command reuses that analysis. Shape: first speech inside 10 s (waiting room cut), a chapter every 2 to 5 min, a reset near minute 20 to 22 (Contrast: drop-off starts around minute 22), the ask spoken in the first and last quarters (Wistia: quarters 1 and 4 convert at 50 to 51% on 30 to 60 min videos), the Q&A tail trimmed to the useful answers.

## 4. Win clip (`testimonial_clip`, 20 to 90 s)

The member's own words, in this order: the situation line by 0:03, where they were, what they did, the result with one specific.

```bash
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/win_member.mp4" --out "$KIT/output/win_member" \
  --brand btc --format testimonial_clip --platform ig_reels --style clean --safe ads --fillers cut
```

`--safe ads` keeps the platform's ad zone clear: the bottom 672 px of 1920 on Reels and Shorts (35%), 660 px on TikTok (34.4%). Meta's own rule is wider. Under a disclaimer the bottom 40% of a Reels ad stays clear of text and logos, and the engine has no disclaimer band yet (`FORMATS.md` section 3), so put the results-vary card over the specific number by hand and keep that 40% clear yourself. Name and role lower-third by 0:05, consent on file, no income figure framed as typical, the disclaimer clear of the four BTC never-words. The clip goes to the Wins category first; the ad library and the VSL proof block pull from there.

## 5. Community post clips

Raw, phone-to-face, one idea, under 60 s. Cut them from the replay pool, then re-run the keeper with a hook per `skills/video/reel-editor/SKILL.md`:

```bash
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/call_wk12.mp4" --out "$KIT/output/wk12_clips" \
  --brand btc --format organic_reel --platform ig_reels --auto 3
```

Daily answers are short Loom videos (a Skool Games winner does 4 to 8 a day), handled in one batch per 24 hours; the best become Classroom pages.

## 6. Thumbnail and title

`longform` writes thumbnail.jpg (1280x720) and cover.jpg (1080x1920) from the best face frame, titled from `--title` or else the first chapter. For another frame or another title, re-run the builder:

```bash
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/m2l3" --title "Objection prevention" --brand btc \
  --out "$KIT/output/m2l3/cover" --at 42
```

Lesson title: the one skill in plain words, key words first. Course cover: face plus module name (Skool publishes no size; 1920x1080 is the house choice). An unlisted YouTube copy follows the thumbnail rules: 1 to 4 words, at most 3 elements, 1 or 2 faces, bright and checked on a black phone screen. YouTube recommends 3840x2160 (640 px wide at minimum, under 2 MB from a phone) and caps the title at 100 characters.

## 7. Cadence and the cancel step

- One live recording session a week: long videos back to back, then open Q&A. Everything else is clipped from that pool. Polish the long pieces; keep the clips raw.
- Categories well under the 10 cap: Wins, Questions, Accountability, Intros, plus admin-only Announcements sorted by newest.
- At the cancel step, `skool_cancel_video` (45 to 120 s, one take) in the cancellation plugin: say they can leave, name the next call by date and one recent win, ask what they came for and whether they got it, then one ask. No pressure words.

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/cancel.mp4" --out "$KIT/output/cancel" \
  --brand btc --format skool_cancel_video --fillers cut --cta "Come to the next call first"
```

## 8. Check and hand over

```bash
"$PY" "$KIT/tools/closer.py" review "$KIT/output/<job>"
```

Read report.md: every line PASS, or a FIX you can name. Open sheet.jpg, then chapters.txt. Lint follows `HOUSE_RULES.md` and the brand's never-words; the engine refuses a title or a CTA that carries one and flags one in the captions. Anything leaving Skool (an ad, VSL proof) also passes `skills/video/cold-review/SKILL.md`. Tell the person the file, the length, the chapters and where it goes. Stop.

## Rules

- One skill per lesson page. Two skills, two pages.
- Never burn captions into a Classroom video. Skool's closed captions and the Transcript addendum do that job.
- Write the chapter titles yourself; the review rejects placeholder titles.
- A brief that asks for a length outside the band gets the band back before any render (`FORMATS.md` Q7). If it renders anyway, the length line is a FIX in the review, never a hard stop. Split; do not rush the speaker.
- A member's result on screen carries the site's own line: individual experiences, results vary. No income figure framed as typical.
- The four BTC never-words stay off every Become The Closer piece, the disclaimer included.
- Still unverified, so house choices until checked: upload size limit, cover pixel sizes, recording length cap, chapters on post videos.
