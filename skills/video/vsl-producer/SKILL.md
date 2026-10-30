---
name: vsl-producer
description: Produces long-form sales videos (website VSLs, 90 s to 5 min) from raw talking-head takes for Become The Closer or Set More Annuities, the way the Set More Annuities VSL was built. Locks the script from the takes, audits every claim, cuts with punch-ins, word captions and full-frame animated cutaways rendered from HTML scenes, grades and cleans the audio, then runs hard checks and a cold review before anything ships. Use when asked for a VSL, a sales video, a long-form edit, or "the video for the website".
---

# VSL producer

The finished reference lives in this kit: `tools/vsl/vsl_build_reference.py` built the Set More Annuities VSL (99 s,
31 pieces, 9 animated cutaways), and `tools/vsl/mg/scenes.html` plus `tools/vsl/mg/render.js` are its motion-graphics
engine. You do not run the reference as is; you copy it next to the new project and change the parts marked below.

## 0. Before anything: the brand and the claims

- Read the brand sheet: `brand/becomethecloser.md` or `brand/setmoreannuities.md`. Colours, type, the site's own
  lines. The cutaways take their tokens from it, the on-video text takes the same palette.
- Read `skills/sales/closer-mentality/SKILL.md`: the video walks the viewer through our frame, one ask per video.
- Zero-context audit: list every fact, number, name and promise the video will say or show next to its source (the
  takes' own words, the brand sheet, the company's documents, the person's own messages). No source, no claim. Write
  it to `AUDIT.md` in the project folder. Spoken lines that cannot be sourced stay spoken but never get amplified on
  screen.

## 1. Words first

```bash
"$HOME/.closer-studio/venv/bin/python" "$KIT/tools/transcribe.py" <takes...> --edit-dir <project>/edit --model medium.en
```

Word timestamps and silences are the only timing source. Never re-transcribe a take that already has a map.

## 2. Lock the script from the takes

Best take per line across all takes. Restarts, stumbles and brand-name slips go. Order: hook in the viewer's own world,
the problem, the stakes, why now, the mechanism, the offer, the proof, the urgency, one ask, a two-second close.
85 to 100 s for a website VSL. The person records the beat sheet into `BEATS` in their copy of the builder (take, first
word, approximate time, last word, approximate time).

## 3. Cutaways (the "animations")

About half the runtime. Cut to a card whenever he explains a mechanism, lists things, quotes a number or names a step;
back to the face for promises, stakes and the ask. Nine scenes ship in `tools/vsl/mg/scenes.html` (CRM list, live call,
then vs now, system map, split bar, calendar, market counter, sign-up click, end card). Re-skin them with the brand
tokens at the top of the file and write new copy; add a scene by following the pattern (a `build()` and a `render(t)`
that is deterministic in t). Every element lands on a spoken word (`GRAPHICS` in the builder maps cues to words).

Rules that came out of a cold review and stay: the speaker never appears for under 2.5 s between two cards; card to
card is a hard cut with the outgoing card clearing first; later elements sit as 16% ghosts so a card is never half
empty; no flash frames; captions keep running under cards but never collide with card text (cards keep the bottom
quarter clear).

## 4. Footage, voice, music

- Every cut is a punch-in: 100 / 112 / 122% alternating, one crop anchor for every scale, a slow push on every shot.
- Grade: `tools/vsl/luts/sma_pro.cube` plus the face fill light, clarity, mild vignette (see `tools/vsl/luts/README.md`).
- Voice: the measured chain (band under 300 Hz gated between words, mud cut at 500 Hz, 2.2 kHz tamed, light denoise,
  S notch, air), one safety limiter at the end, fixed gain to -15 LUFS. Measure the new recording first: a 1/3-octave
  long-term spectrum of the loud frames against normal speech balance tells you where its hump is.
- Music: a licensed bed pre-levelled to -24 LUFS, ducked under the voice (about 12 dB under), lifted at the end card.
  `tools/music_industrial_cinematic.mp3` is Kevin MacLeod, CC BY 4.0: credit him on the page.

## 5. Checks (all of them, every time)

1. Loudness: integrated within 0.5 LU of target, true peak under -1 dBTP.
2. Words: re-transcribe the render; every word on screen matches; no clipped word at a cut.
3. Frames: contact sheet at 400 px wide at every card, the hook, the proof, the end card, and five random cuts.
4. Sync: cross-correlate output audio against the source at every piece (0 to 2 ms).
5. Cold review: a fresh sub-agent with no project notes, the file and a screenshot of the site, asked for SHIP / FIX
   FIRST / DOG SHIT with timecodes and a brand-coherence list. Fix everything it calls a blocker; argue nothing.

## 6. Deliver

The 1080p file, the review page with chapters, the open decisions for the owner in plain words, and the honest list of
what the video still cannot do (usually: proof footage it does not have).
