# Editing grammar: how we cut

This is the house editing brain. The engine follows it by default; a human editor using Claude reads it before
touching a frame. Sources for every number are in `RESEARCH.md`.

## 1. The clock (the same in every style)

Measured across 22 top-performing videos (Hormozi, Abdaal, Diary of a CEO, Abram, MKBHD, Fireship), the same rules held in
shorts and long-form. Only the dial settings change.

| Law | Shorts (reels, TikTok, Shorts) | Long-form (YouTube, VSL) |
|---|---|---|
| The hook has a deadline | Speech or payoff within 2.5 s. No title card first. Captions from frame one | Thesis spoken within 10 s, cold open. Intro over by 6 % of runtime |
| Something visible changes on a clock | Every 3 to 8 s (median 5): a punch-in, a card, a word pop. Any 8 s static stretch is a hole | Shot median 3 to 6.5 s; the layout itself (face, B-roll, graphic) flips every 20 to 40 s |
| Open a loop early, close it late | Promise in the first 5 s, payoff at 55 to 85 % | One deliberate long hold (30 to 60 s) carries the verdict, at 72 % or later |
| Captions are a format decision | Burned captions always on, 1 to 6 words, one emphasis mechanism | No burned speech captions. Keyword pops of 1 to 4 words on the spoken word; platform captions for accessibility |
| Authenticity survives the edit | Keep the ums and the laughs. Cut the air between ideas, never inside a sentence | Same |
| Zoning | Graphics own the top 40 %, captions the 48 to 66 % band, the face owns the rest. Nothing ever covers a face | Same physics for pops, lower thirds and cards |
| End on the payoff | The last 1.5 to 2 s is the completed state. Cut right after the last payoff word | Speech runs to within 6 s of the end. No end screen, no outro sentence |

The engine enforces these: `review.py` fails a job that hooks late, ends late, holds a frame over 8 s, or lands a caption on
the chin.

## 2. Three dialects we speak

### Hormozi (idea density)

- One idea every 3 to 7 s. The cut lands on the idea boundary, not on a timer.
- Two framings only, wide and tight, alternating at each cut (about 1.5x between them). A slow push on any hold.
- Captions: 2 to 3 words mixed case with weight on the operative word (the 2024+ look, `--style clean`), or caps with the
  spoken word in the accent colour (the 2021 look, `--style impact`). Pick one mechanism and never stack colour, box
  and emoji.
- The hook is on screen for the first 2 to 4 s as a native-looking text block, and the captions wait until it is gone
  (one thing to read at a time).
- A B-cam hides cuts. We have one camera, so the punch-in is our B-cam.
- Listicles get a numbered pill above the caption band; it doubles as a progress bar.
- No CTA inside the clip. The end card carries it.

### Gadzhi (premium minimal)

- Colour from one source: 60 % main (the dark variant), 30 % secondary, 10 % accent. Our brand files carry exactly
  that: `bg`, `panel`, `accent`.
- Two fonts. A sans for everything (Inter / Montserrat), and a special face for the one word that matters (Fraunces,
  the serif). The special word gets the accent colour and, in a card, a soft glow.
- Shapes are rounded rectangles, corners 30 to 70 px at 1080p, a hairline and a faint glow. Cards float on a blurred,
  darkened plate so the text reads.
- Animation is slow and continuous: enter, settle, exit; the next camera move starts before the last one ends.
  Text arrives word by word, sometimes stepped to 15 fps.
- Four scene types: text write-outs over the speaker or B-roll, abstract story scenes, character scenes, and UI
  pop-ups (three stacked rounded cards). Our `tools/vsl/mg/scenes.html` implements the text, UI and card types.
- Captions in this dialect are a single serif line, sentence case, no highlight (`--style serif`).

### Nelk (energy)

- Montages cut to the beat of a real song, letterboxed, graded teal and orange, summer feel.
- The drop is three sounds: a build-up (riser) under the last line, a bang on the cut, a bass boom under the next
  shot. `voice.py` synthesizes a riser, a hit and a whoosh so no library file is needed.
- A montage ends with a smash to black; the next scene opens on an establishing shot.
- A pop tag slides in when a new person appears. Subtitles are heavy italic with an RGB-split shadow.
- Mood music under every scene, ducked under speech.

## 3. Which dialect per brand

| Brand | Talking-head reels | Cards and cutaways | Montage and B-roll |
|---|---|---|---|
| Become The Closer | Hormozi: `--style impact` (or `clean` for softer topics), `btc_ember` grade, hits on emphasis words | Gadzhi cards in the ember palette, Fraunces for the special word | Nelk energy: riser into the CTA, hard cuts on the beat |
| Set More Annuities | Gadzhi: `--style clean` or `serif`, `sma_pro` grade, hook in Fraunces | Gadzhi cards, red and gold, as in the VSL | Rare; calm |

## 4. The process (every edit)

1. **Analyze first.** `closer analyze` gives the words, pauses, fillers, emphasis, the face track and the best windows.
   Read `transcript.txt`. Never cut what you have not read.
2. **Beat map.** Split the transcript into idea beats (one claim per beat). Mark the hook beat and the payoff beat.
   The payoff must land past the halfway mark; if it lands at 30 %, change the window.
3. **Hook.** Pull the first sentence that makes a claim or names the viewer's pain in their words. Four to seven
   words on screen. The first word is about them.
4. **Cut.** `closer reel` removes the air between beats, alternates framings, lands framing changes on emphasised words,
   keeps the fillers unless the brief is corporate (`--fillers cut`).
5. **Captions.** One style, one mechanism, inside the band. Proofread `captions.srt`. A wrong word on screen is a
   re-render, not a shrug: fix it in `analysis.json` and run again.
6. **Sound.** Voice chain, then one whoosh per punch-in, a hit on an emphasis kick, a riser into the end card when the
   brief wants energy. Music is optional and must work muted.
7. **Review.** Read `report.md`, look at `sheet.jpg`, then run the cold review (`skills/video/cold-review`). Fix,
   re-render, repeat. Ship only on a pass.

## 5. Never

- Never stack emphasis mechanisms (colour plus box plus emoji). It reads as 2021 content farming.
- Never sand the speech smooth. Rough delivery does trust work.
- Never cover the face, the hands when they hold something, or on-screen text.
- Never add an outro, a "follow for more", or a fade to black at the end of a reel.
- Never put a number, a name or a claim on screen that the footage or the brand sheet does not contain.
- Never pitch the voice or speed it past 1.05x.
