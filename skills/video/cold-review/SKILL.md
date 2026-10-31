---
name: cold-review
description: An unbiased second viewer for a finished video. Spawns a reviewer that has none of the edit's context, makes it watch the frames and read the captions, and returns SHIP, FIX FIRST or DOG SHIT with timecodes. Use before any client-facing, paid-traffic or website video ships, when the person asks "is this actually good", or after the third revision of anything.
---

# Cold review

The engine's report.md checks the mechanics. This checks whether a stranger would keep watching. Run it on the
finished file, never on a preview.

## 1. Evidence pack

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
J="$KIT/output/<job>"
ffmpeg -v error -y -i "$J/<file>.mp4" -vf "fps=2,scale=270:-2,tile=6x8" -frames:v 1 "$J/review_sheet_a.jpg"
ffmpeg -v error -y -i "$J/<file>.mp4" -vf "select='gte(t\,0)*lte(t\,3)',fps=6,scale=270:-2,tile=6x3" -frames:v 1 "$J/review_hook.jpg"
```

The first sheet is the whole piece at two frames a second; the second is the first three seconds at six frames a
second (the hook is where most of the audience leaves). Add the job's captions.srt and report.md.

## 2. The reviewer

Start a fresh agent (the Agent tool, a general-purpose agent, never a fork: a fork knows what you meant to do). Give
it only: the sheets, the SRT, the report, the platform and the audience in one line ("commission-only closers on
Instagram, 22 to 40, scrolling at night"). Do not give it the hook you chose, the brief, or your opinion.

Ask it to answer, in order, with timecodes:

1. Would you have stopped scrolling in the first second? What is on screen at 0.0 s, 0.5 s, 1.0 s?
2. Where did you want to leave, and why (slow stretch, caption on the face, a word you could not read, a claim you
   did not believe)?
3. What is the one line you remember? Does the ending land on it?

Then a verdict: **SHIP** (nothing you would fix before posting), **FIX FIRST** (a list, each with a timecode and the
fix), or **DOG SHIT** (start over, and the one reason).

## 3. Act on it

- FIX FIRST items with timecodes go back into the edit (window, hook, caption word, caption position, cut) and the
  engine re-renders. Then run the cold review again with a new agent.
- Owner taste calls (font, colour, music) are not review items; log them and move on.
- Ship only on SHIP. Three rounds without SHIP means the footage or the script is the problem; say so.
