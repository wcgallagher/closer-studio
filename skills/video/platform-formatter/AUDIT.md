# AUDIT: platform-formatter

| Claim | Status | Source |
|---|---|---|
| 1080x1920 for Reels, TikTok, Shorts, Stories; 1080x1350 feed and LinkedIn; 1080x1080 square; 1280x720 X; 1920x1080 YouTube and VSL | VERIFIED | `tools/studio/platforms.py` table; xyla.ai and upload-post.com size sheets (checked 2026-10-31) |
| safe zones: Reels 269 / 672 / 65 px, Shorts 288 / 672 / 48 / 192 px, TikTok 240 / 660 / 120 px | VERIFIED | Meta Reels ad specs (14 % / 35 % / 6 %), Google Ads vertical safe zones, TikTok in-feed template measured by upload-post.com; cited in `tools/studio/platforms.py` |
| length limits 180 / 60 / 140 / 600 s | VERIFIED | platform help pages as summarised in `tools/studio/platforms.py` (Reels up to 3 minutes since 2025; Shorts 3 minutes; X 140 s; TikTok 10 minutes) |
| -14 LUFS / -1.5 dBTP; -23 LUFS broadcast; -15 LUFS / -1.2 dBTP VSL | VERIFIED / RUN | YouTube normalisation and EBU R128 as noted in `tools/studio/platforms.py`; the VSL target measured on the shipped `SMA_VSL_v7.mp4` (-15.2 LUFS, -1.2 dBTP) |
| 15 % upscale cap | RUN | `upscale=1.15` in `tools/studio/track.py` |
| cover at 0.4 s | RUN | `tools/studio/render.py` |
