---
name: placement
description: Where on-screen text goes on each video type (16:9 website VSL, 16:9 YouTube, 9:16 reels, 4:5 and 1:1 feed). Chips and hand labels are placed by the placement engine to stay off the face and the captions (the review fails any that do not); keyword pops, the lockup, cards and captions keep their own positions. Covers the safe area per format, the cost terms and weights (including the open-side home that pulls chips beside the face), the timing rules for labels, hand tracking for word-locked hand labels, and what fails the review. Use when a chip or label covers the face or the captions, when someone says "move the text", "the chip is on my face", "put labels on my hands" or "where should this pop-up go", or before adding chips or hand labels to a layers file.
---

# Placement

A good editor never types coordinates. They look at the frame and put the text where the eye can take it without covering what matters. The engine does the same in numbers: it maps the speaker's face, the caption lines on screen, the tracked hands and everything already placed onto the output frame, then picks the cheapest spot on a grid. Everything is measured after the same crop, zoom, push and kick the render applies, so a punch-in that brings the face closer is seen. The code is `tools/studio/placement.py`; every engine number below comes from its `PLACEMENT_RULES` or from the code that calls it, and craft numbers from research are named as such. The layers file itself is in `skills/video/vsl-builder/SKILL.md`.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" hands --help
```

On a Mac or Linux, run these in Terminal. On Windows, run them in Git Bash or WSL: the middle `PY` fallback is the venv that `install.ps1` makes (that installer has not been run on a Windows machine yet). The installers write `kit_path`; without it, run from the kit folder. The help screen should print `usage: closer hands [-h] [--start START] --end END [--fps FPS] --out OUT video`.

The engine runs inside `longform` and places what a layers file asks for (`tools/studio/longform.py`, `tools/studio/layers.py`). The `reel` command does not use it: reels place their captions and hook with their own face check (`skills/video/caption-styles/SKILL.md`).

## 1. What goes through the engine

| On screen | How it is placed | In the review check |
|---|---|---|
| Chip with no `x` (`style` `chip`, `quiet` or `glass`) | the engine (group `chips`), from 0.1 s before `at` to the end of its hold | yes |
| Hand label | the engine (group `hands`), beside its hand, inside that hand's side of the frame | yes |
| Chip with `x` | fixed at `x`, `y`, plus 0.095 of the height per `row` (a `glass` plate starts 28 px left of `x`, at 1080 tall) | no |
| Pointer chip (`style` `pointer`) | fixed top right (x 0.955, y 0.075 unless set), registered so others avoid it | no |
| Lockup | fixed glass cards on the left (from frame 0 by default), both registered for their time on screen | no |
| Burned caption lines | registered as a band from 0.07 to 0.93 of the width, for each line's time on screen (burned styles only; lines inside an `off` window are not registered) | they are what is protected |
| Keyword pops | fixed (section 2) | no |
| Headline, proof card, moment cards and lines, animated scenes, B-roll | their own positions; the engine does not see them | no |

Order matters. The lockup and the chips go first (chips in the order of the layers file), hand labels last, so a hand label moves aside for a chip and never the reverse. A chip measures its own box at its real size, so long text gets a wide box and fewer places to go:

- `chip` and `quiet`: the brand's caption font, 58 px at 1080 tall (56 for `quiet`), plus 16 px of padding.
- `glass` (a dark glass pill with a gold bead; `skills/video/vsl-builder/SKILL.md` does not list it yet): the brand's UI font at `size` (54 at 1080 tall unless set), 28 px of padding at the sides and 16 px top and bottom, plus a 14 px bead and a 16 px gap before the text.

A chip whose `at` falls inside a scene's window (0.2 s either side) is dropped, and nothing says so.

## 2. Safe areas per video type

Text sits only inside the box, given as fractions of the frame (left, top, right, bottom). The engine reads the aspect from the output size: wider than 1.5 is 16:9, narrower than 0.7 is 9:16, under 0.9 is 4:5, the rest is 1:1.

| Aspect | Box | Platforms | On the canvas |
|---|---|---|---|
| 16:9 | 0.045, 0.06, 0.955, 0.94 | `web_vsl` (every VSL and confirmation format), `youtube` (YouTube and Skool), `x`, `broadcast` | x 86 to 1834, y 65 to 1015 on 1920 x 1080 |
| 9:16 | 0.06, 0.12, 0.84, 0.70 | `ig_reels`, `fb_reels`, `ig_story`, `tiktok`, `yt_shorts` | x 65 to 907, y 230 to 1344 on 1080 x 1920 |
| 4:5 | 0.06, 0.06, 0.94, 0.86 | `ig_feed`, `linkedin` | |
| 1:1 | 0.06, 0.06, 0.94, 0.90 | `square` | |

The 16:9 box sits close to broadcast title safe (SMPTE ST 2046-1: the centred 90 % of width and height, so 5 % margins), a little wider at the sides and a little tighter at the top and bottom. The 9:16 box keeps the right 16 % clear for the like and share rail and stops at 70 % of the height, above the caption and handle area. Paid reels have taller ad overlays (Meta asks for the bottom 35 % free of text, quoted in `tools/studio/platforms.py`), and the engine does not read the platform zones: in a paid 9:16 cut, keep chips above 0.65 of the height by hand.

Per video type:

- **Website VSL (16:9).** Captions in the bottom band (`skills/video/caption-styles/SKILL.md`). The lockup on the left at the open. Chips go beside the speaker on the open side, at eye height, when that spot is clear (the `home` term, section 3); hand labels sit beside their hand. Animated cards keep their payoff above the caption band. A website player can lay an unmute button over the centre and a control bar over the bottom; the research marks their sizes unmeasured, so look at the real player before trusting a chip there.
- **YouTube and Skool (16:9).** Same box. When the format uses keyword pops instead of burned captions, a pop sits centred at the top (0.22 of the height down). With a tracked camera and the head sitting high (the top of the face box above 0.30 of the source frame's height in at least 5 % of the face detections), it goes beside the face instead, at x 0.06 or 0.94 and y 0.34, on the side away from the face.
- **Reels, Shorts, TikTok (9:16).** Inside the 9:16 box only, with no reel-specific rules beyond it. The torso costs little (weight 2), so a chip can land on the chest, the spot viewers preferred in the subtitle study the research cites (Akahori 2017). When the open side beside the face is too narrow for the chip, that is where it goes: just under the chin, on the open side.
- **Feed (4:5 and 1:1).** Same engine, its own box.

## 3. The cost

Every spot on a grid inside the box (a step of 0.02 of the width and of the height) is scored over the item's whole life. The face is sampled 5 times a second over that life; captions, hands and placed items count when they share any moment of it. Overlap terms take the worst moment; the weighted terms add up and the lowest total wins.

| Term | What it measures | Weight |
|---|---|---|
| `face` | share of the box over the face box | 60 |
| `captions` | share over a caption line on screen at the same time | 40 |
| `overlays` | share over anything already placed at the same time | 40 |
| `headroom` | share over the face box grown by 0.25 of its width each side and 0.45 of its height above | 14 |
| `hands` | share over a tracked hand, except the one the label belongs to | 8 |
| `near` | distance from the target hand, where the gap counts ten times as much as the sideways offset; sitting on the hand adds half the weight | 6 |
| `bright` | mean brightness under plain text above 0.62 | 6 |
| `home` | distance of the box centre from the group's home: on the side of the face with more room before the edge of the box, halfway across that room, at eye height (0.4 of the face box down) plus 0.05 of the frame height. Only for chips, and only when a face is on screen | 5 |
| `sticky` | distance from where the same group sat in the last 8 s | 4 |
| `busy` | how uneven the background is under plain text | 2.5 |
| `torso` | share over the body (from the chin to the frame bottom, as wide as the face plus 0.9 of a face width each side) | 2 |

What this means in practice:

- The face weight is large but it is a cost, not a wall. If nowhere is clear, the engine still places the box and the review fails it.
- On a clear frame a chip lands at its home. With the face at x 0.70 on 1920 x 1080, a 400 x 100 chip landed at x 432 to 832, y 410 to 510; with the face at x 0.30 it moved to the right side.
- With no face track there is no home, and ties go to the first spot on the grid, the top-left corner of the box. Hand labels have no home either; their target hand decides. If the open side is wrong for the shot, give the chip `x` and `y` and look at the frame yourself, since a fixed chip is not checked.
- `ui` (25) and `edge_hug` (1) are listed in `PLACEMENT_RULES` but nothing reads them yet. A `stats` home is defined there too, but nothing places in a `stats` group yet.
- `bright` and `busy` count only for plain text. Every chip (`glass` included) and every hand label today sits on a plate, so they never fire.

## 4. Time

- **Hold still.** One spot for the whole life of a chip or a label. Only the entrance moves: a `chip` or `quiet` chip slides in 70 px (at 1080 tall) over 170 ms, a `glass` chip rises 18 px over 220 ms while it fades in over 140 ms, and a hand label pops from 0.78 to 1.04 to full size over 200 ms. One fixed position per segment is the design from Hu 2014, and Madsen 2016 found labels were located more easily when their update rate was limited.
- **Never chase a hand.** A hand label sits beside the hand at the top of the gesture: from 0.35 s before its word to 0.8 s after, the engine takes the frames within 0.04 of the frame height of the highest point and uses their median box. It searches only that hand's side of the output frame (0 to 0.62 of the width for a hand on the left half, 0.38 to 1 for one on the right).
- **A label lives only while its word is the caption line.** It appears 2 frames before its word and leaves at the first of: 2 frames before the next label, the end of the caption line that holds the word, 0.12 s after the hand drops, or 1.6 s after the word. The hand drops at the first frame after both the word and the hand's highest point where its top sits more than 0.12 of the frame height below the peak, so a hand still rising into the gesture does not end the label. With no caption line around the word, the line's end counts as 1.2 s after it. It stays at least 0.45 s unless the next label comes sooner.
- **Never two labels at once.** Each label ends where the next one starts.
- **Chips** show from `at` for `hold` seconds (1.6 by default) or until `until`.

The engine does not enforce cut timing, so write chip `at` and `hold` to it. From the Netflix Timed Text Style Guide: a text event lasts 5/6 s to 7 s; an in time within 0.5 s of a cut moves onto the cut, and an out time within 0.5 s of a cut moves to 2 frames before it; the gap between two text events is 2 frames or at least 0.5 s; spoken captions run at 20 characters a second at most. Unspoken text needs about max(0.83 s, characters / 15 + the entrance) to be read. The research adds that after a cut the eye goes to the face in about half a second, so a new chip lands on the cut or 0.5 s after it, and two new things never arrive in the same half second. A hand label can be as short as 0.45 s, under that reading floor: check it at phone size, and if it does not read, hold the gesture longer in the take or drop the label.

## 5. Hand labels

Track the hands on the raw take, not the selects file. The rows are on the take's own clock.

```bash
"$PY" "$KIT/tools/closer.py" hands "$KIT/inbox/take2.mp4" --start 40 --end 55 --out "$KIT/output/<job>/hands_take2.json"
```

`--end` is required, `--start` defaults to 0 and `--fps` to 10. Frames are scaled to 1280 px wide and each half of the frame is searched on its own, so a hand stays large at the detector's input (side `L` is screen left, `R` screen right). Each half gives at most one hand per row (the palm with the best score), so two hands on the same half show as one. The models are OpenCV Zoo's ONNX versions of the MediaPipe palm detector and 21-point hand model (Apache-2.0, in the kit's `tools/studio/models` folder), run through OpenCV with no extra runtime. Each row is `{"t", "hands": [{"side", "cx", "cy", "left", "top", "right", "bottom", "px", "score", "presence", "in_frame"}]}` in fractions of the source frame. The thresholds live in `HAND_RULES` in `tools/studio/hands.py`: palm score 0.55, hand presence 0.6, box merge (NMS IoU) 0.3, in-frame margin 0.03 of the frame.

Before you write a label, read the rows around its word. You want the hand on that side with `in_frame` true and `px` (the hand box in millionths of the frame) of 2500 or more. The engine skips hands under `min_px` (2500 unless set) but does not read `in_frame`, so a label can ride a hand that is half out of the frame, and `px` is measured before the box is clipped to the frame, so such a hand can still read large. The research rule is to anchor to a hand only when it is fully in frame for the label's whole life, and to fall back to a chip otherwise.

Then add the block to the layers file:

```json
"hands": {"file": "hands_take2.json", "take": "take2",
          "labels": {"L": ["BEFORE", "before@46.2"], "R": ["AFTER", "after@47.0"]},
          "min_px": 2500, "size": 62}
```

- `file` is relative to the layers file, so keep the layers file in the job folder next to the rows file. `take` is the take's name in the assemble spec. The times in `labels` are word anchors on the selects clock (transcript.txt), the same as every other anchor.
- `labels` is keyed by side, so one layers file carries two hand labels at most, one per hand.
- `size` is the type size at 1080 tall. Use `zoom` to hold one framing over the gesture.
- Hand labels need an assembled selects file (its beats map take time to the cut) and a tracked camera (a face in at least half the frames). Without either, no label is drawn and nothing says so.

## 6. Cut and read the report

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/output/<job>/selects/selects.mkv" --out "$KIT/output/<job>/v1" \
  --format vsl_hero --platform web_vsl --layers "$KIT/output/<job>/layers.json" --preview
```

The `--out` folder gets placement.json: the rules used, then one row per placed chip and hand label with `label`, `group`, `a` and `b` (seconds), `rect` (pixels), `cost`, `terms` (the costs that shaped the pick), `face_overlap`, `caption_overlap` and `ok`. Read `terms` first: a large `face` or `captions` there says why the item moved where it did, and a `home` alone means it sat at its home on a clear frame.

## 7. What fails review

report.md carries the line "graphics clear of the face and the captions". It is FIX when any placed chip or hand label has more than 2 % of its own area on the face box or more than 1 % on a caption line, and it names up to six of them. It does not look at fixed chips, the pointer, the lockup, pops, cards or scenes; check those on sheet.jpg and on frames at phone size (360 px wide).

| The report or the frame says | Do |
|---|---|
| a chip on the face | shorter text, or another `at` where the speaker is framed wider |
| a chip on the captions | an `off` window for the captions over the chip, or move the chip |
| a chip is missing | it fell inside a scene's window; move its `at` |
| a hand label is missing | no tracked hand on that side near the word (check `take` and `min_px` against the rows), or no tracked camera |
| a hand label on the face | the gesture is too close to the face; use another gesture or a chip |
| a hand label far from its hand | a chip holds that space; move the chip |

## 8. Honest limits

- HTML scenes keep their own layout. Positions inside `tools/vsl/mg/scenes.html` are written in the scene; the engine neither sees nor moves them, and a chip inside a scene's window is dropped.
- Saliency is not yet a cost term. The research method scores the mean saliency under the box (SmartOverlays, 2020). Here only the face, the captions, the hands and placed items count, and the background terms are off for plated text.
- Nothing keeps clear of the platform UI (`ui` is not read). Only chips have a home; a hand label, or a chip on a take with no face track, falls back to the top-left tie.
- Keyword pops, the headline, the proof card and moment cards are not registered, so a chip can land on one. Check those frames.
- The face keep-out is the detector's face box with a soft headroom margin and nothing added below the chin. The research asks for a larger hard keep-out around the mouth and chin.
- The entrance starts off the box the engine checked: a `chip` or `quiet` chip 70 px to the right for its first 170 ms, a `glass` chip 18 px below for its first 220 ms.
- At most two hand labels per video, and `in_frame` is not checked.
