---
name: caption-styles
description: Chooses and tunes the burned-in caption look for a video (impact, clean, serif, boxed, premium), the hook card, keyword pops and the listicle pill, inside the platform's safe caption band. Use when someone asks for Hormozi-style captions, cleaner captions, a cinematic look, bigger or smaller text, a different highlight colour, or when a reel's captions sit on the face.
---

# Caption styles

Five looks, one rule: one emphasis mechanism per video. Pick the look, never mix mechanisms.

| Style | Look | Mechanism | Use for |
|---|---|---|---|
| `impact` | Montserrat Black, caps, outline, 2 to 4 words, pop on the first word | spoken word in the brand accent colour | Become The Closer reels, high energy, young audience |
| `clean` | Montserrat ExtraBold, mixed case, soft shadow, no box, 2 to 3 words | the operative word in the heavier weight, no colour | the 2024+ Hormozi look, advice monologues, older audiences |
| `serif` | Fraunces Display, sentence case, one line, fades | none | cinematic cuts, Set More Annuities, lower thirds in a VSL |
| `boxed` | Montserrat Black on a dark plate, caps | spoken word in the accent | TikTok-native feel, busy backgrounds |
| `premium` | Inter bold in the speaker's own case, a soft shadow and no stroke, phrases of 3 to 7 words, a gentle fade per line | gold on at most one meaning word per line (a figure, or a word in `KEYWORDS`), at most 15 % of all words, no per-word flicker | sales VSLs and brand films next to a serif card system |

Set it per run with `--style`, per brand in `brand/<id>.json` under `style.captions`, or per job in the layers file: `"captions": {"style": "premium", "words": [3, 7]}`. In a blind panel on 2026-11-02 both cinematic reviewers read `impact` under an editorial card system as a stock caption template, which is why `premium` exists.

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

Caption size is a fraction of frame height (impact 4.8 %, clean 4.4 %, serif 4.0 %, boxed 4.4 %, premium 3.6 %), so the
same style reads the same on 9:16, 4:5 and 16:9 (16:9 multiplies it by 1.85: premium is about 72 px at 1080). To change it, edit `STYLES` in `tools/studio/captions.py` and say so in the
reply; do not pass ad-hoc sizes.

## Text

- 1 to 5 words per screen (3 to 7 in `premium`); at least 0.3 s on screen; chunks break at punctuation, pauses and beat
  changes. A line never ends on a word that binds to the next one (an article, a preposition, an auxiliary or modal, a
  negation, a subject pronoun, a contraction, an adverb before its verb, a common adjective before its noun:
  `BIND_NEXT`), never splits a fixed pair such as "life insurance" or "right now" (`COLLOC`), and a line shorter than
  the style's minimum costs extra (`tools/studio/captions.py`, `chunk`). The first line shows from frame 0 in `premium`.
- Caps for `impact` and `boxed`, mixed case for `clean`, `serif` and `premium`. Never emoji.
- Proofread `captions.srt`. Names, numbers, "not" and "don't" are the words transcription gets wrong; fix them in
  the analysis file and re-run.
- Keyword pops (1 to 4 words landing on the spoken word, top zone, display face) are for long-form and VSLs where
  burned speech captions are off; `cards.pop_event` in `tools/studio/cards.py`. The listicle pill (`cards.pill_events`)
  sits just above the caption band and counts the items.
