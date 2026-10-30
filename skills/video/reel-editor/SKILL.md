---
name: reel-editor
description: Cuts a finished 9:16 reel (Instagram, TikTok, Shorts) from one or more raw talking-head clips for Become The Closer or Set More Annuities. Transcribes, cuts dead air, alternates punch-ins, grades the picture, cleans the voice, burns word-highlight captions and a hook, adds the brand end card, lands loudness. Use when someone drops footage in inbox/ and asks for a reel, a short, a clip, or "cut this up".
---

# Reel editor

One command does the whole edit. Your job is to pick the right 20 to 45 seconds, write the hook, and check the result.

## 1. Find the kit and the footage

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"; ls "$KIT/inbox"
```

If the person did not say which clip or which part, transcribe first and choose for them:

```bash
"$HOME/.closer-studio/venv/bin/python" "$KIT/tools/reel_build.py" "$KIT/inbox/<file>" --out "$KIT/output/<job>" --end 1
```

That writes the transcript file (transcript.json inside the job folder) for the first second only; for the whole clip run the real command below with
`--preview` (fast, low quality), read the transcript file, then pick the window. A reel is one idea: the moment that makes
a closer feel seen, called out, or shown a move. 20 to 45 seconds. Start on a sentence that stands alone without the
setup before it.

## 2. Write the hook

The hook is the first 2.6 seconds on screen. It is the one line that makes a commission-only closer stop scrolling.
Pull it from `skills/sales/closer-mentality/SKILL.md` and `brand/becomethecloser.md`: name the pain in their words
("'I want to think about it' is stealing your commissions"), or the identity ("There are only four types of closers").
Four to seven words. No hype words (see `HOUSE_RULES.md`). Never a number you cannot source.

## 3. Cut

```bash
"$HOME/.closer-studio/venv/bin/python" "$KIT/tools/reel_build.py" "$KIT/inbox/<file>" \
  --out "$KIT/output/<job>" --start <s> --end <s> --brand btc --hook "YOUR HOOK LINE" [--music "$KIT/tools/music_industrial_cinematic.mp3"]
```

Options: `--brand sma` for Set More Annuities (red and gold, "Create your free account"); `--cta "line"` to change the
end card line; `--face-x 0.5 --face-y 0.38` if his face is not centred (fractions of the frame); `--keep-silence` for a
clip where the pauses are the point; `--model medium.en` for a mumbled recording; `--preview` for a fast draft.

What the script does (so you can explain it in one sentence): cuts every pause over 0.35 s, alternates 100 / 110 / 120%
punch-ins with one crop anchor so the eye line never jumps, grades with `tools/vsl/luts/sma_pro.cube` plus a fill light
on the face, runs the voice chain (low band gated between words, mud cut at 500 Hz, 2.2 kHz tamed, light denoise, air),
burns Montserrat Black captions with the brand accent on the spoken word, puts the hook top-centre for 2.6 s, adds a
2 s end card (brand background, call to action, site, handle), mixes a whoosh under each punch-in and the optional
music bed ducked under the voice, and lands at -14 LUFS with one safety limiter. It also writes `captions.srt` for the
platform's own caption upload.

## 4. Check before you say done

```bash
ffmpeg -v error -y -i "$KIT/output/<job>/<file>_reel.mp4" -vf "fps=1,scale=216:-2,tile=8x6" -frames:v 1 "$KIT/output/<job>/sheet.jpg"
```

Look at the sheet. Captions must be below the chin and above the bottom 320 px (the apps put their own UI there);
nothing over the face; the hook readable; the end card last. Read `captions.srt` top to bottom: a wrong word on screen
is a reshoot of the caption, not a shrug. If a caption is wrong, fix the word in the transcript file and run the command
again (it reuses the pieces, only the captions and the final pass re-render).

## 5. Hand it over

Tell the person: the file name in `output/<job>/`, the length, the hook you used, and one sentence on the cut. Offer two
alternative hooks. Stop.

## Rules

- One idea per reel. If the clip has two, make two reels.
- The first word on screen is about them, never about us.
- Never "free", "guarantee", "no cost" on a Become The Closer reel. A result on screen carries the site's own line:
  individual experiences, results vary.
- The voice is his. Never speed it up past 1.05x, never pitch it.
- Music is optional and quiet. The platforms add their own; a reel with a bed should still work muted.
