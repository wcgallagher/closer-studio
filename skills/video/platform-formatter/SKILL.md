---
name: platform-formatter
description: Formats and exports a finished video for each social platform (Instagram Reels, Facebook Reels, Stories, TikTok, YouTube Shorts, Instagram feed 4:5, LinkedIn, square, X, YouTube 16:9, website VSL, broadcast) with the right size, safe zones, duration limit, bitrate and loudness, plus the SRT and cover frame. Use when someone asks "export this for TikTok and Shorts too", "what size for LinkedIn", "is this too long for Reels", or wants one edit delivered everywhere.
---

# Platform formatter

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" platforms
```

prints the table: size, maximum length, safe zones (top / bottom / left / right in pixels) and loudness target per
platform. The numbers and their sources live in `tools/studio/platforms.py`.

## Two ways to deliver everywhere

1. **Same aspect, several platforms** (Reels, TikTok, Shorts are all 1080x1920): render once, then

   ```bash
   "$PY" "$KIT/tools/closer.py" export "$KIT/output/<job>/<file>_ig_reels.mp4" --out "$KIT/output/<job>/exports" --platforms tiktok,yt_shorts,fb_reels
   ```

   re-encodes with each platform's bitrate cap and loudness and warns when the file is over that platform's length limit.
   Captions were placed for the first platform's band; Reels, TikTok and Shorts bands overlap enough that one placement
   serves all three (bottom UI 660 to 672 px).

2. **Different aspect** (4:5 feed, 1:1, 16:9): render again with the reel editor and a platform list; the face track
   re-frames the crop and captions are re-laid for that canvas:

   ```bash
   "$PY" "$KIT/tools/closer.py" reel ... --platform ig_reels,ig_feed,square
   ```

## Rules of thumb

- Export at the native size; never upscale a 720p source past its own height (the engine caps zoom to 15 % upscale).
- Loudness: -14 LUFS integrated, -1.5 dBTP, everywhere except broadcast (-23 LUFS, EBU R128) and the website VSL
  (-15 LUFS, -1.2 dBTP, matched to the Set More Annuities VSL).
- Length: Reels and Shorts 180 s, Stories 60 s, X 140 s, TikTok 600 s, LinkedIn 600 s, feed 60 s. A reel that must
  run on Stories gets cut to 60 s, not sped up.
- Deliver the SRT with every file; the platforms index spoken words from it.
- The cover frame (`cover.jpg`, taken at 0.4 s) carries the hook; upload it as the cover so the grid reads.
