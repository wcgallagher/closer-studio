---
name: longform-editor
description: Cuts long-form masters with the longform command: YouTube authority videos, book-a-call and program VSLs, Skool lessons, call replays, the confirmation WHY video and case-study clips. Chapters with cards, keyword pops on their own layer, quote cards on the exact spoken line, B-roll on the format's cadence, the verdict hold, an ending on the payoff, chapters.txt, captions.srt for the closed-caption upload and a thumbnail, then the review and a cold review. Use when a brief names a 16:9 piece over 3 minutes or a long format id (yt_authority, vsl_book_call, vsl_long, skool_lesson, replay, confirmation_why, testimonial_case_clip).
---

# Long-form editor

The viewer chose to sit down for this. The reel rules in `skills/video/reel-editor/SKILL.md` (a cut every 2 to 4 s, burned impact captions) are wrong here; a 12 minute video cut like a reel feels like being shouted at. The house grammar in `EDITING_GRAMMAR.md` and `skills/video/edit-grammar/SKILL.md` holds, and where this skill or the format guide says otherwise, the grammar wins.

Long means over 180 s (`FORMATS.md`). The format id loads the length band, caption style, cadence, CTA policy, hook deadline, music mode and filler rule from `formats.json` at the kit root. Use the registry ids; youtube_long and vsl_short still resolve as older spellings of yt_authority and vsl_book_call. The beats per format:

| Format id | Beats and page rules |
|---|---|
| `yt_authority` | section 1 below |
| `vsl_book_call`, `vsl_long` | `skills/video/funnel-vsl/SKILL.md` |
| `skool_lesson`, `replay` | `skills/video/skool-content/SKILL.md` |
| `confirmation_why`, `testimonial_case_clip` | `skills/video/show-rate-videos/SKILL.md` |

Brand words come from `skills/brand/brand-kit/SKILL.md` and `HOUSE_RULES.md`.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
ls "$KIT/inbox"
```

The table prints the 17 ids with their bands and ends with the older ids that still resolve.

## 1. Analyze, then map the beats

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<file>" --out "$KIT/output/<job>"
```

Read transcript.txt before you touch the cut. Then write the beat map: a timestamp for every beat in the format's structure. For yt_authority: the title words spoken inside the first 15 s (if the take never says them, change the title, not the opening); stakes by 0:30; show, do not tell, up to 3:00, with a planned re-engagement near 3:00; chapters of 2 to 5 min; the heavier explanation after minute 6; the payoff inside the last third; the verdict hold at 72% or later.

Chapters: count = max(3, min(15, round(minutes / 3))), first at 0, each at least 10 s, each title 3 to 8 words naming the question the section answers. A quote card goes on the line a viewer would screenshot, one per chapter at most, never inside the hold.

## 2. Cut

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/<file>" --out "$KIT/output/<job>" \
  --start <s> --end <s> --brand btc --format yt_authority \
  --chapters "0:First chapter,190:Second chapter" --quotes "the line, as spoken" \
  --pops "word|two words" --broll "$KIT/inbox/broll" --title "Up to four words" --hold 530:570
```

It reuses the analysis in the job folder when `--start` and `--end` match. Options you will use:

- `--format` (default yt_authority) picks the numbers. `--platform` defaults to the format's own: youtube, or web_vsl for the VSL and confirmation formats. `--brand sma` for Set More Annuities.
- `--chapters "0:Title,190:Title"`: seconds from the window start, the first at 0 (otherwise the engine inserts a "Start" placeholder and the review fails it). Each chapter after the first gets a 1.8 s card. It writes chapters.txt in YouTube timestamp form, ready for the description. `--chapters auto` finds boundaries and titles them with the first words of a sentence; the review rejects those placeholder titles, so write real ones and run again.
- `--quotes "line|line"`: the exact spoken line, at least 3 words (the engine matches 80% of the words, in order). The card shows while the line is spoken, 2 to 4.5 s. A line it cannot find is a FIX in the report.
- `--pops`: `auto` (the default) pops one or two emphasised words, at most one per 7 s. `--pops "word|two words|up to four words"` pops your phrases at their first occurrence; `off` pops nothing. The grammar wants 1 to 4 words on the spoken word. Pops sit in the top zone or beside the face, never over it, and a pop that falls on a card or on B-roll is dropped.
- `--broll DIR`: a folder of clips, cycled in name order and placed at sentence ends on the format's cadence (change_every_s, 20 s for yt_authority), 3.2 s each with a slow push. `--change-every S` overrides it; 0 means no scheduled change and no B-roll. Only cards and B-roll count as layout changes. Punch-ins alternate every 4.5 s underneath, on their own clock.
- `--captions`: pops (the yt_authority default), none (Skool and replay), or a burned style: impact, clean, serif or boxed. vsl_book_call loads clean burned captions because the page autoplays muted. `--pops` works only with pops.
- `--cta "line"` and `--title "words"` are refused when they carry a brand never-word (the four BTC never-words; `--audience client` adds SMA's client-facing words).
- `--music FILE` adds a bed; the format's music mode is faint for yt_authority and none for every other long format. `--fillers` defaults to the format's rule, which is cut on every long format.
- `--hold a:b` (seconds from the window start) marks the verdict hold: no B-roll and no pop lands inside it, the cadence check skips it, and a chapter or quote card inside it gets a note on the console.
- `--preview` for a fast draft; drop it for the delivery.

It writes the master (`<file>_<format>_<platform>.mp4`), chapters.txt, captions.srt (upload it as the closed-caption track; a yt_authority master carries no burned speech captions), thumbnail.jpg and cover.jpg (titled from `--title`, or from the first chapter when there is none), beats.txt, then runs the review (report.md and sheet.jpg).

**The verdict hold.** One deliberate hold of 30 to 60 s carries the answer the title promised, at 72% of runtime or later (`EDITING_GRAMMAR.md`). Nothing sits on the frame but the speaker: no chapter card, no quote card, no pop, no B-roll. Pass it as `--hold a:b` and the engine keeps B-roll and pops out of it and skips it in the cadence check; chapter times and quote lines are yours to keep out of it (the console notes a card inside the hold). The slow push and the punch-ins keep running underneath (the grammar's own rule for a hold), which also keeps the 8 s static check green. Check the hold on sheet.jpg anyway.

**The ending.** Speech runs to within 6 s of the end. No outro sentence and no end screen in the master (`EDITING_GRAMMAR.md`); on YouTube the end screen is set in Studio over the last 20 s at upload, as `FORMATS.md` says. The engine cuts on the last word and adds the brand end card, 2.5 s, on every format whose CTA policy is not none; testimonial_case_clip ends on the last word. The review passes a tail of 3 s or less. The last spoken sentence is content, not a sign-off: a one-line bridge to a specific next video, never a thank-you.

## 3. Thumbnail and other platforms

```bash
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/<job>" --title "Up to four words" --brand btc --out "$KIT/output/<job>/cover" --at <s>
"$PY" "$KIT/tools/closer.py" export "$KIT/output/<job>/<master>.mp4" --out "$KIT/output/<job>/out" --platforms <a,b>
```

`longform` already wrote thumbnail.jpg at 1280x720 and cover.jpg at 1080x1920 from the surest face frame inside the first 8 s of the window. `cover` with `--at` picks another frame or another title, and it refuses a never-word title too. YouTube's own page: 3840x2160 recommended, 640 px minimum width, under 2 MB when uploaded from a phone. A variant under 1280x720 makes its A/B test downscale every variant, so the file `cover` writes clears that floor and sits under the recommended size. Compose it by hand: at most 3 elements, 1 or 2 faces, 1 to 4 words, bright, checked on a black phone screen. Title under 100 characters, key words first. Drafting and testing titles: `skills/video/hooks-titles-covers/SKILL.md`. Other sizes: `skills/video/platform-formatter/SKILL.md`.

## 4. Read the report, then the cold review

```bash
"$PY" "$KIT/tools/closer.py" review "$KIT/output/<job>"
```

The run ends with the review; this re-runs it after a fix. A long job's report.md has these lines: opens by the format's hook deadline (15 s for yt_authority); ends on the payoff; a layout change at least every N s (20 for yt_authority), or "no layout cadence required" when the format's change_every_s is 0; no static stretch over 8 s; length fits the format (a FIX line, never a stop: the brief step gives the band back before any render); loudness on target; chapters written by a person (fails on placeholder titles); every quote found in the speech; no banned words in the speech; caption words to proofread. Every line PASS (with `--hold` the hold is not a cadence gap). Two yt_authority checks the review leaves to you: title words inside the first 15 s, first speech within 1 s. Open sheet.jpg and look at the hold and the cards. Read captions.srt top to bottom; a wrong word is a fix in the job's analysis.json (the `w` field of that word) and a re-run.

Then `skills/video/cold-review/SKILL.md`: a fresh agent with no context gets its two contact sheets, captions.srt, report.md and one line naming the platform and the audience. Nothing else, not the brief and not your opinion. Fix the earliest timecode first and run it again with a new agent. Ship only on SHIP.

## 5. Worked example: 10 min YouTube video (BTC)

Source: a 24 min recording of a closer taking apart a lost call, cut to a 10 min window. Title: "The question that kills your close". Thumbnail: his face plus ONE QUESTION. The title line is spoken at 0:04; the lost-call audio runs 0:30 to 2:50; the pulled-forward objection clip at 3:00 is the re-engagement; the quote card lands on "You asked for the decision before you asked for the reason" at 5:10, inside chapter 2; the replacement line lands at 8:50, so the hold runs 8:50 to 9:30 (40 s, 88% to 95% of 10:00, past the 72% mark at 7:12); speech runs to the last word and the end card follows. Pop words come from before the hold.

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/lost_call.mp4" --out "$KIT/output/yt_question" --start <s> --end <s>
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/lost_call.mp4" --out "$KIT/output/yt_question" \
  --start <s> --end <s> --brand btc --format yt_authority \
  --chapters "0:The question that kills the close,190:Where it shows up,400:The replacement line" \
  --quotes "You asked for the decision before you asked for the reason" \
  --pops "kills|decision|reason|objection" --broll "$KIT/inbox/broll" --title "One question" --hold 530:570
"$PY" "$KIT/tools/closer.py" review "$KIT/output/yt_question"
```

Three chapters, because round(10 / 3) is 3. `--hold 530:570` is 8:50 to 9:30 from the window start; check those frames on sheet.jpg before you hand it over.

## 6. Worked example: book-a-call VSL (SMA)

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/sma_vsl.mp4" --out "$KIT/output/sma_vsl_warm" \
  --brand sma --format vsl_book_call \
  --quotes "The money is already in your book|If that is all you need to hear, open the account below"
```

The beats, the button time, the proof that goes in and the page rules are in `skills/video/funnel-vsl/SKILL.md`. The format loads clean burned captions and cuts the fillers; no music plays unless `--music` names a bed. `--quotes` puts one key-line card per section, on the lines as spoken. A brief that says vsl_short means this id.

## Rules

- The grammar wins. Where `FORMATS.md` or this skill says otherwise, `EDITING_GRAMMAR.md` decides.
- A chapter title is a promise, written by a person. One idea per chapter.
- The voice is theirs. Never speed it past 1.05x, never pitch it.
- Never a number, a name, a result or a claim on a card that the footage or the brand sheet does not hold.
- Never the four BTC never-words on a Become The Closer title, CTA, card or thumbnail. Set More Annuities names its product to agents; `--audience client` is for a piece the agent's own client will watch.
- Never signal the ending. No outro sentence, no end screen in the master; YouTube's end screen is an upload setting.
