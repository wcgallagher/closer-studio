---
name: reel-editor
description: Cuts finished short-form video (Instagram Reels, TikTok, YouTube Shorts, LinkedIn, square) from raw talking-head clips with one command. Transcribes, finds the best window, cuts dead air, tracks the face into the frame, alternates punch-ins on emphasis words, grades, cleans the voice, burns captions in the house style, adds the hook and the brand end card, lands loudness, runs the checks. Use when someone drops footage in inbox/ and asks for a reel, a short, a clip, a TikTok, or "cut this up".
---

# Reel editor

One command does the edit. Your job is to choose the window, write the hook, read the report, and look at the frames.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
ls "$KIT/inbox"
```

## 1. Analyze before you cut

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<file>" --out "$KIT/output/<job>"
```

It prints the word count, fillers, emphasised words, face coverage, and the eight best windows ranked (start, end,
score, opening line), and writes transcript.txt next to analysis.json in the job folder. Read the transcript. A reel is one idea,
18 to 45 s, that starts on a sentence which stands alone and ends on a payoff line. The ranked windows are suggestions;
the person's brief wins. If they named the part they want, find it in the transcript and use those times.

## 2. Write the hook

Four to seven words that make the viewer stop. The first word is about them. Pull the pain or the identity line from
`skills/sales/closer-mentality/SKILL.md` and the brand sheet in `brand/`. No number you cannot source, no banned word
(the engine refuses a hook with one). Offer two alternatives in your reply.

## 3. Cut

```bash
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/<file>" --out "$KIT/output/<job>" \
  --start <s> --end <s> --brand btc --platform ig_reels --hook "YOUR HOOK LINE"
```

Options you will use:

- `--platform` takes a comma list: `ig_reels,tiktok,yt_shorts` renders one file per platform into sub-folders, each
  with that platform's safe zones and loudness. `ig_feed`, `linkedin` and `square` re-crop to 4:5 or 1:1 with the
  face tracked. `youtube` and `x` are 16:9.
- `--style impact` (caps, spoken word in the accent colour), `clean` (mixed case, weight on the operative word),
  `serif` (one editorial line), `boxed` (dark plate). The brand file sets the default. Read
  `skills/video/caption-styles/SKILL.md` before changing it.
- `--brand sma` for Set More Annuities; add a brand with `skills/brand/brand-kit/SKILL.md`.
- `--fillers cut` removes the ums (corporate or scripted briefs only; talking-head reels keep them).
- `--riser` adds a riser into the end card; `--music file.mp3` adds a ducked bed; `--no-sfx` drops the whooshes and hits.
- `--camera static --face-x 0.5 --face-y 0.38` when the face tracker reports coverage under 50 %
- `--safe ads` when the reel will run as a paid placement (Meta and Google reserve more of the frame for ad UI) (two people, a
  mask, heavy backlight). `--grade cinematic` or `--grade none` to change the picture.
- `--denoise deep` uses DeepFilterNet when `install.sh --deep-filter` has been run (noisy rooms, wind).
- `--preview` for a fast draft to check the cut; drop it for the delivery.

What the engine does, so you can explain it in one sentence: cuts every pause over 0.35 s, alternates 100 / 110 / 120 %
punch-ins with one crop anchor so the eye line never jumps, lands framing changes on emphasised words, follows the face
with a damped virtual camera, grades with the brand LUT plus a fill light, cleans the voice, burns word-timed captions
inside the platform's caption band, puts the hook on screen for the first 2.6 s, adds a 2 s end card, mixes a whoosh under
each punch-in and a hit under each emphasis cut, and lands the platform's loudness with one limiter. It writes
`captions.srt` for the platform's own caption upload and `cover.jpg` for the cover frame.

## 4. Read the report, look at the frames

The run ends with the review (report.md and sheet.jpg in the job folder). Every line must say PASS: hook by 2.5 s, ends
on the payoff, no static stretch over 8 s, length fits the platform, loudness on target, captions clear of the face, no
banned words, no low-confidence caption words. Open `sheet.jpg` and look: captions below the chin, nothing over the
face, the hook readable, the end card last. Read `captions.srt` top to bottom. A wrong word on screen is a fix in
the job's analysis.json (the `w` field of that word) and a re-run, which reuses the rendered pieces.

For a client-facing or paid-traffic reel, run `skills/video/cold-review/SKILL.md` before you say done.

## 5. Hand it over

Tell the person: the file name(s) in `output/<job>/`, the length, the hook you used, one sentence on the cut, and the
two alternative hooks. Stop.

## Rules

- One idea per reel. Two ideas, two reels.
- The voice is theirs. Never speed it past 1.05x, never pitch it.
- Music is optional and quiet; a reel with a bed must still work muted.
- Never "free", "guarantee", "no cost" on a Become The Closer reel. A result on screen carries the site's own line:
  individual experiences, results vary.
- Never invent a number, a name or a result for the hook or the captions.
