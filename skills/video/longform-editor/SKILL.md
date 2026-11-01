---
name: longform-editor
description: Cuts long-form for the Closer Studio kit (YouTube authority videos, book-a-call VSLs, Skool lessons and welcomes, confirmation videos, call replays) with the longform command. Beat map from the analyze transcript, chapters, keyword pops on their own layer with a closed-caption sidecar instead of burned captions, a visible layout change every 20 to 40 s, quote cards, the verdict hold, ending on the payoff, chapters.txt and thumbnail, then the review and a cold review. Use when a brief names a 16:9 master over 3 minutes or any of yt_authority, vsl_book_call, vsl_long, skool_lesson, skool_welcome, confirmation_how, confirmation_why or replay. A brief may use the alias ids in FORMATS.md section 3 instead (youtube_long and vsl_short among them); the skill translates them before the engine runs.
---

# Long-form editor

This cuts anything the viewer chose to sit down for. The reel rules in `skills/video/reel-editor/SKILL.md` (a cut every 2 to 4 s, burned impact captions) are wrong here; a 12 minute video cut like a reel feels like being shouted at. The grammar in `EDITING_GRAMMAR.md` and `skills/video/edit-grammar/SKILL.md` holds, with one disagreement between it and the format guide named in section 2 (the ending).

Read `FORMATS.md` before any cut. The format id in the brief loads the length band, caption style, cadence, CTA policy and checks from `formats.json`; this skill never overrides those numbers. The engine has no alias map: `--format` takes the registry id exactly as `formats.json` spells it. youtube_long in a brief means yt_authority and vsl_short means vsl_book_call; show_confirmation means two cuts, confirmation_how followed by confirmation_why. Passing an alias id does not fail. The engine's format loader in `tools/studio/` falls back to an unsourced built-in entry of that name, with a different length band, cadence, CTA policy and filler rule, and the cut quietly follows the wrong numbers. `formats.json` has to sit at the kit root. When `tools/closer.py formats` prints a table without yt_authority and vsl_book_call, the registry is not installed; stop and install it before cutting.

Brand rules come from `skills/brand/brand-kit/SKILL.md` and `HOUSE_RULES.md`: BTC copy never says free, no cost, guarantee or guaranteed; SMA cards, titles, descriptions and page lines never name the product. Scripts are `skills/video/vsl-producer/SKILL.md` and `skills/sales/closer-mentality/SKILL.md` territory; this skill starts once the take exists.

## 1. Analyze, then map the beats

```
tools/closer.py formats
tools/closer.py analyze raw/take.mp4 --out jobs/<job>
```

Read the whole analyze transcript before touching the cut. Then write the beat map: a timestamp for every beat in the format's structure. For yt_authority that is promise match by 0:15, stakes by 0:30, show-do-not-tell to 3:00, a planned re-engagement near 3:00, chapters of 2 to 5 min, the heavier explanation after minute 6, the open-loop payoff in the last third (a house placement; the sources give the open loop, not the clock), and the bridge in the last 20 s. The title words must be spoken inside the first 15 s. If the take never says them, change the title, not the opening.

Chapters: count = max(3, min(15, round(minutes / 3))), first at 00:00, each at least 10 s, titled in 3 to 8 words by the question the section answers.

## 2. The cut

- **Pops, not burned captions.** The master carries keyword pops on their own layer, never over the face: 1 to 4 words on the spoken word, per `EDITING_GRAMMAR.md`. The engine's auto pops run one or two emphasised words, at most one every 7 s. Full captions go out as `<job>/captions.srt` and get uploaded as the closed-caption track; the yt_authority recipe for that track splits groups at 800 ms gaps with 8 words at most. vsl_book_call is the exception: it loads clean burned captions because the page autoplays muted.
- **Cadence.** A visible layout change every 20 to 40 s: a card (chapter or quote) or a B-roll cutaway. The engine's cadence line counts those; punch-ins alternate underneath on their own clock. The yt_authority entry sets that check at 20 s. Cuts every 3 to 6 s in the first 3 minutes, looser after minute 6. Silence removal capped at 20% of runtime; fillers cut.
- **Quote cards.** One per chapter at most, on the line a viewer would screenshot. The engine shows the card while the line is spoken (2 to 4.5 s), so a line inside the verdict hold is never the quote.
- **The verdict hold** (house grammar). One deliberate long hold of 30 to 60 s carries the answer the title promised, at 72% of runtime or later. Nothing sits on the frame but the speaker: no pop, no card, no cutaway, no B-roll. The punch-in alternation keeps running underneath, since the engine fails any single framing held over 8 s. The hold is the grammar's one planned exception to the layout clock, so report.md shows it as one cadence gap over 20 s. That gap is accepted when it starts at or after 72% and runs 30 to 60 s; no other gap is. Auto pops know nothing about the hold, so pass the pop words yourself (`--pops "word|two words"`, which the engine accepts in place of auto or off) and take none from inside it.
- **End on the payoff.** `EDITING_GRAMMAR.md` (its long-form column reads "Speech runs to within 6 s of the end. No end screen, no outro sentence.") and `FORMATS.md` yt_authority (a one-line bridge to one named next video plus the end screen in the last 20 s) disagree here. This skill's reading for yt_authority: speech runs to the last word, then the engine appends its 2.5 s brand end card (the registry's end_card policy). The last spoken sentence is the bridge, which is content, not an outro. The YouTube end-screen elements go on in YouTube Studio over the final 20 s of the upload, never into the master. Never signal the ending earlier. No thanks-for-watching. Open item for the owner: settle the wording in `EDITING_GRAMMAR.md`.

## 3. Render and package

```
tools/closer.py cover jobs/<job> --title "2 to 4 words" --brand btc --out jobs/<job>/cover --at <s>
tools/closer.py export <master> --out jobs/<job>/out --platforms youtube
```

The longform call (template in section 5) writes the 16:9 master with punch-ins, pops, chapter cards and quote cards, plus `<job>/chapters.txt` (for the description), `<job>/captions.srt`, `<job>/thumbnail.jpg`, `<job>/cover.jpg` and `<job>/report.md`. The cover command grades the best face frame and sets the title in the display face: thumbnail 1280x720 and cover 1080x1920. Thumbnail: at most 3 elements, 1 or 2 faces, 1 to 4 words, bright, checked on a black phone screen. YouTube's spec: 3840x2160 recommended, 640 px minimum width. Under 2 MB when uploaded from a phone, 50 MB from a desktop. A variant under 1280x720 makes YouTube downscale every A/B variant to 854x480, so the 1280x720 the cover command writes clears that threshold and sits under the recommended size. Title under 100 characters, key words first. Draft 10 to 20 title and thumbnail pairs and test 3 in YouTube's native A/B.

## 4. Review, then cold review

```
tools/closer.py review jobs/<job>
```

report.md carries the engine's own checks: opens by the format's hook deadline (15 s for yt_authority), ends on the payoff, a layout change at least every 20 s, no framing held over 8 s, length inside the band, loudness, chapters written by a person, every quote found in the speech, banned words in the transcript, caption words to proofread. The yt_authority checks it does not compute, read by hand from the transcript and the sheet: first speech within 1.0 s, title words inside 15 s, pops clear of the face, silence removal under 20%. Fix every fail first; the one accepted FIX line is the verdict hold's cadence gap (section 2). Then the cold review per `skills/video/cold-review/SKILL.md`: a fresh agent with no context, given that skill's two contact sheets (the whole piece at two frames a second, the first 3 s at six), `<job>/captions.srt`, `<job>/report.md` and one line naming the platform and the audience. Nothing else goes in, not the brief and not your opinion. It answers that skill's three questions with timecodes. The verdict is SHIP or FIX FIRST with timecodes; a DOG SHIT verdict (start over, with the one reason) means the footage or the script is the problem. Fix the earliest timecode first and run it again with a new agent; ship only on SHIP. Post-launch, yt_authority is read against 60% still watching at 0:30 and an average view near 30% (41% stretch). CTR is judged against your own videos; the platform band is 2 to 10%.

## 5. Worked example: 10 min YouTube video (BTC)

Source: a 24 min recording of a closer taking apart a lost call. Title: "The question that kills your close". Thumbnail: his face plus ONE QUESTION. The title line is spoken at 0:04; the lost-call audio runs 0:30 to 2:50; the pulled-forward objection clip at 3:00 is the re-engagement; the quote card lands on "You asked for the decision before you asked for the reason" at 5:10, inside chapter 2; the replacement line lands at 8:50, so the hold runs 8:50 to 9:30 (88% to 95% of 10:00, past the 72% mark) with nothing on the frame; the bridge to the next video is the last sentence, 9:40 to the end. Pop words come from before the hold.

```
tools/closer.py analyze raw/lost_call.mp4 --out jobs/yt_question
tools/closer.py longform raw/lost_call.mp4 --out jobs/yt_question --brand btc --format yt_authority --platform youtube --chapters "0:The question that kills the close,190:Where it shows up,400:The replacement line" --quotes "You asked for the decision before you asked for the reason" --pops "kills|decision|reason|objection" --music <bed.mp3> --fillers cut
tools/closer.py cover jobs/yt_question --title "One question" --brand btc --out jobs/yt_question/cover --at 530
tools/closer.py review jobs/yt_question
```

Three chapters, because round(10 / 3) is 3. `--music` takes a file path; yt_authority's music policy is faint.

## 6. Worked example: 6 min VSL (SMA, warm)

A brief that says vsl_short means vsl_book_call. A warm viewer (post-training, email list) gets the 5 to 6 min cut. Beat map for 6:00, compressed from the 7 min template: hook 0:00 to 0:30 (who it is for, the one result, a reason to stay, the viewer's own situation first); problem 0:30 to 1:45, which keeps agitation under 90 s; proof 1:45 to 3:15 with the escape hatch placed at 2:30 (a house placement inside the 2:00 to 3:30 window for the first ask; Roezan gives the line, not the clock); objections out loud 3:15 to 4:45; the ask 4:45 to 6:00 with a reason to act now and who it is not for, inside the last 90 s. One CTA: open the account and register for the Wednesday 1 PM ET training. The page's button reveal time equals the escape-hatch time, 150 s in this cut.

```
tools/closer.py longform raw/sma_vsl.mp4 --out jobs/sma_vsl_warm --brand sma --format vsl_book_call --platform web_vsl --quotes "The money is already in your book|If that is all you need to hear, open the account below" --pops off --fillers cut
tools/closer.py review jobs/sma_vsl_warm
```

No chapters flag: the key-line card per section replaces chapter cards. Cutaways at most one per 12 s, none in the first 3 s or last 1 s, snapped to the spoken word, under 40% of runtime.
