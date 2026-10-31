---
name: caption-styles
description: Chooses and tunes the burned-in caption look for a video (impact, clean, serif, boxed), the hook card, keyword pops and the listicle pill, inside the platform's safe caption band. Use when someone asks for Hormozi-style captions, cleaner captions, a cinematic look, bigger or smaller text, a different highlight colour, or when a reel's captions sit on the face.
---

# Caption styles

Four looks, one rule: one emphasis mechanism per video. Pick the look, never mix mechanisms.

| Style | Look | Mechanism | Use for |
|---|---|---|---|
| `impact` | Montserrat Black, caps, outline, 2 to 4 words, pop on the first word | spoken word in the brand accent colour | Become The Closer reels, high energy, young audience |
| `clean` | Montserrat ExtraBold, mixed case, soft shadow, no box, 2 to 3 words | the operative word in the heavier weight, no colour | the 2024+ Hormozi look, advice monologues, older audiences |
| `serif` | Fraunces Display, sentence case, one line, fades | none | cinematic cuts, Set More Annuities, lower thirds in a VSL |
| `boxed` | Montserrat Black on a dark plate, caps | spoken word in the accent | TikTok-native feel, busy backgrounds |

Set it per run with `--style`, or per brand in `brand/<id>.json` under `style.captions`.

## Placement

Captions live in the band from 50 % of the frame height down to 40 px above the platform's bottom UI
(`tools/studio/platforms.py`, `caption_band`; organic zones by default, `--safe ads` for paid placements). Before
rendering, the engine measures where the chin and the top of the head sit across the whole cut (the face track,
every punch-in included) and moves the virtual camera up in steps until a two-line caption block clears the chin; if
the face fills the frame it sends the captions to the top zone and the hook into the caption band. The review then
re-measures on the real block. Never move captions onto the face to make room.

The hook card sits at 30 % of the frame height for 2.6 s and the captions wait until it is gone: one thing to read at
a time. `--hook-serif` sets it in Fraunces for the Set More Annuities look.

## Sizes

Caption size is a fraction of frame height (impact 4.8 %, clean 4.4 %, serif 4.0 %, boxed 4.4 %), so the same style
reads the same on 9:16, 4:5 and 16:9. To change it, edit `STYLES` in `tools/studio/captions.py` and say so in the
reply; do not pass ad-hoc sizes.

## Text

- 1 to 5 words per screen; at least 0.3 s on screen; chunks break at punctuation and pauses, never start or end on
  a function word (`tools/studio/captions.py`, `chunk`).
- Caps for `impact` and `boxed`, mixed case for `clean` and `serif`. Never emoji.
- Proofread `captions.srt`. Names, numbers, "not" and "don't" are the words transcription gets wrong; fix them in
  the analysis file and re-run.
- Keyword pops (1 to 4 words landing on the spoken word, top zone, display face) are for long-form and VSLs where
  burned speech captions are off; `cards.pop_event` in `tools/studio/cards.py`. The listicle pill (`cards.pill_events`)
  sits just above the caption band and counts the items.
