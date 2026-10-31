# Closer Studio

Raw clips in, finished videos out, with only Claude Code on your Mac. Built for Become The Closer and Set More
Annuities; works for any brand you add. It cuts reels, reframes anything to vertical with a face-tracked camera,
burns captions in four house styles, cleans the voice, grades the picture, adds the hook and the end card, lands the
right loudness for each platform, runs the checks, and ships the SRT and cover frame. Long-form VSLs with animated
cutaways use the same kit.

## Set up (once, about 5 minutes, Mac)

1. Get this folder onto your Mac: on this GitHub page click the green **Code** button, then **Download ZIP**, then
   double-click the zip. Put the `closer-studio` folder in your home folder or Documents.
2. Open the **Claude Code** app, choose **Open folder**, pick `closer-studio`.
3. Type `set me up` and press Enter. Claude installs the video engine and the speech-to-text package. Click **Allow**
   when it asks. If your Mac asks for your password, that is normal.
4. When Claude says **Done**, you are set.

No Terminal, no commands to remember. Windows users: install WSL first, then the same three steps inside it.

## Every time you want to edit

1. Put raw videos in `closer-studio/inbox`.
2. Open `closer-studio` in the Claude Code app.
3. Say what you want:
   - `make a reel from the video in inbox`
   - `cut three reels from this call: objections, the quiz, the close`
   - `make this vertical for TikTok`
   - `export the reel for Shorts and LinkedIn too`
   - `make a VSL from these three takes`
   - `is this actually good?` (runs the cold review)
4. Finished files land in `closer-studio/output/<job>/`. Claude tells you the file name, the length, and what it did.

## What is inside

| Folder | What it is |
|---|---|
| `tools/closer.py` | the one command: `analyze`, `reel`, `reframe`, `export`, `review`, `brands`, `platforms` |
| `tools/studio/` | the engine: transcription and moments, face tracking and virtual camera, the cut, captions, voice, grade, cards, render, review |
| `skills/video/` | reel-editor, auto-reframe, caption-styles, platform-formatter, edit-grammar, cold-review, vsl-producer, video-use |
| `skills/brand/brand-kit` | add a brand in five minutes from its website |
| `skills/sales/closer-mentality` | how we sell, loaded before any hook or caption |
| `skills/copy/*`, `skills/media-buying/*` | copy, trust scoring, ads and growth skills |
| `brand/` | brand tokens (colours, fonts, CTA, banned words) as JSON plus the scrape notes |
| `EDITING_GRAMMAR.md` | the house editing brain: the measured retention laws and the Hormozi / Gadzhi / Nelk dialects |
| `RESEARCH.md` | every repo and source we studied, what we took, what we left |
| `HOUSE_RULES.md`, `CREDITS.md`, `GO_PUBLIC.md` | writing rules, licences, how to publish and share this kit |

## For the technical

```bash
bash install.sh                       # once; add --deep-filter for DeepFilterNet noise removal
python3 tools/closer.py analyze inbox/clip.mp4 --out output/job
python3 tools/closer.py reel inbox/clip.mp4 --out output/job --start 12 --end 41 --brand btc --platform ig_reels,tiktok --hook "Your hook line"
python3 tools/closer.py reframe inbox/wide.mp4 --out output/wide_vertical.mp4 --platform ig_reels
python3 tools/closer.py export output/job/clip_ig_reels.mp4 --out output/job/exports --platforms yt_shorts,fb_reels
python3 tools/closer.py review output/job
```

Needs ffmpeg, Python 3.10+, and the packages `install.sh` adds (numpy, scipy, pillow, faster-whisper, opencv-python-headless,
scenedetect). Everything runs on the CPU. The face detector (YuNet, 230 KB) ships in the repo.
