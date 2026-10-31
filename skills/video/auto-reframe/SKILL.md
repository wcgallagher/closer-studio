---
name: auto-reframe
description: Turns any horizontal or square clip into a vertical 9:16, 4:5 or 1:1 version that keeps the speaker in frame, using a face-tracked virtual camera (no manual keyframes). Use for "make this vertical", "reframe for TikTok", "crop this for Reels", podcast clips, screen recordings with a webcam, or any footage that was not shot for the platform it is going to.
---

# Auto-reframe

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" reframe "$KIT/inbox/<file>" --out "$KIT/output/<name>_vertical.mp4" --platform ig_reels
```

Options: `--start` and `--end` for a window; `--platform ig_feed` (4:5), `square` (1:1), `youtube` (16:9 from a vertical
source, rare); `--zoom auto` (default: the face fills about 27 % of the frame height) or a number such as `--zoom 1.15`;
`--per-scene` locks one crop size per shot for multi-camera or edited sources; `--stride 1` for fast movement;
`--preview` for a quick draft.

## How it works (say this in one sentence when asked)

A small face detector (YuNet, runs on the CPU) finds the face every second frame; a damped virtual camera follows it
with a dead zone so the frame only moves when the person really moves and never overshoots; cuts in the source make
the camera snap instead of pan; the path is compiled into the crop filter's own expressions so ffmpeg renders it at
full speed. Audio is untouched.

## Check

```bash
ffmpeg -v error -y -i "$KIT/output/<name>_vertical.mp4" -vf "fps=1,scale=216:-2,tile=8x6" -frames:v 1 "$KIT/output/<name>_sheet.jpg"
```

Look at the sheet: the face stays inside the frame and near the upper third throughout; no black bars; no jitter
between neighbouring frames. The command prints the face coverage: under 50 % means the detector lost the face (two
people, a mask, strong backlight). Then use `--zoom 1.0` with the reel editor's `--camera static` crop instead, or ask
for a tighter window.

## When not to use it

- Slides, screen recordings without a face, product shots: the tracker has nothing to follow. Use a static crop or a
  blurred fill (the engine's static crop handles the first; the blurred fill is on the open list in `RESEARCH.md`).
- Two speakers in one wide shot: the camera will pick the larger face and stay on it. For a true two-shot, cut the
  reel per speaker and alternate windows.
