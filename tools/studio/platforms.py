"""Platform formats and safe zones. Pixels on the platform's native canvas.

Sources (checked 2026-10-31):
- Meta, Instagram Reels video ad specs: keep the top 14%, the bottom 35% and 6% on each side free of text and logos
  (https://www.facebook.com/business/ads-guide/update/video/instagram-reels).
- Google Ads Help, safe zones for vertical video ads on YouTube: 288 px top, 672 px bottom, 48 px left, 192 px right
  on a 1080x1920 canvas (https://support.google.com/google-ads/answer/9128498).
- TikTok Ads Manager in-feed template, measured by upload-post.com: 240 px top, 660 px bottom, 120 px each side,
  action buttons 300 px wide from 840 px down (https://www.upload-post.com/tools/safe-zone-checker/).
- Organic (non-ad) UI is lighter than the ad overlays: Instagram Reels about 220 px top / 430 px bottom / 130 px sides,
  YouTube Shorts 110 / 420 / 140 right, TikTok 160 / 420 / 120 right (xyla.ai social sizes sheet and orsonlord.com
  overlays, 2026). `safe` holds the ad zones, `organic` the lighter ones; reels default to organic, `--safe ads` for paid.
- Loudness: YouTube and most streaming normalise around -14 LUFS integrated; the EBU R128 broadcast target is -23 LUFS.
  Reels and TikTok re-encode and normalise on upload, so we deliver -14 LUFS, -1.5 dBTP everywhere except broadcast.
"""
from __future__ import annotations

PLATFORMS = {
    "ig_reels": {"name": "Instagram Reels", "w": 1080, "h": 1920, "fps": 30, "max_s": 180,
                 "safe": {"top": 269, "bottom": 672, "left": 65, "right": 65}, "organic": {"top": 220, "bottom": 430, "left": 130, "right": 130},
                 "lufs": -14, "tp": -1.5, "maxrate": "12M", "ext": "mp4"},
    "fb_reels": {"name": "Facebook Reels", "w": 1080, "h": 1920, "fps": 30, "max_s": 180,
                 "safe": {"top": 269, "bottom": 672, "left": 65, "right": 65}, "organic": {"top": 220, "bottom": 430, "left": 130, "right": 130},
                 "lufs": -14, "tp": -1.5, "maxrate": "12M", "ext": "mp4"},
    "ig_story": {"name": "Instagram Story", "w": 1080, "h": 1920, "fps": 30, "max_s": 60,
                 "safe": {"top": 269, "bottom": 672, "left": 65, "right": 65}, "organic": {"top": 250, "bottom": 350, "left": 65, "right": 65},
                 "lufs": -14, "tp": -1.5, "maxrate": "12M", "ext": "mp4"},
    "tiktok": {"name": "TikTok", "w": 1080, "h": 1920, "fps": 30, "max_s": 600,
               "safe": {"top": 240, "bottom": 660, "left": 120, "right": 120}, "organic": {"top": 160, "bottom": 420, "left": 60, "right": 120},
               "lufs": -14, "tp": -1.5, "maxrate": "12M", "ext": "mp4"},
    "yt_shorts": {"name": "YouTube Shorts", "w": 1080, "h": 1920, "fps": 30, "max_s": 180,
                  "safe": {"top": 288, "bottom": 672, "left": 48, "right": 192}, "organic": {"top": 110, "bottom": 420, "left": 48, "right": 140},
                  "lufs": -14, "tp": -1.5, "maxrate": "12M", "ext": "mp4"},
    "ig_feed": {"name": "Instagram feed (4:5)", "w": 1080, "h": 1350, "fps": 30, "max_s": 60,
                "safe": {"top": 0, "bottom": 120, "left": 40, "right": 40}, "lufs": -14, "tp": -1.5, "maxrate": "10M", "ext": "mp4"},
    "linkedin": {"name": "LinkedIn (4:5)", "w": 1080, "h": 1350, "fps": 30, "max_s": 600,
                 "safe": {"top": 0, "bottom": 120, "left": 40, "right": 40}, "lufs": -14, "tp": -1.5, "maxrate": "10M", "ext": "mp4"},
    "square": {"name": "Square (1:1)", "w": 1080, "h": 1080, "fps": 30, "max_s": 140,
               "safe": {"top": 0, "bottom": 100, "left": 40, "right": 40}, "lufs": -14, "tp": -1.5, "maxrate": "10M", "ext": "mp4"},
    "x": {"name": "X (16:9)", "w": 1280, "h": 720, "fps": 30, "max_s": 140,
          "safe": {"top": 0, "bottom": 60, "left": 40, "right": 40}, "lufs": -14, "tp": -1.5, "maxrate": "6M", "ext": "mp4"},
    "youtube": {"name": "YouTube (16:9)", "w": 1920, "h": 1080, "fps": 30, "max_s": 0,
                "safe": {"top": 0, "bottom": 110, "left": 60, "right": 60}, "lufs": -14, "tp": -1.5, "maxrate": "14M", "ext": "mp4"},
    "web_vsl": {"name": "Website VSL (16:9)", "w": 1920, "h": 1080, "fps": 30, "max_s": 0,
                "safe": {"top": 0, "bottom": 90, "left": 60, "right": 60}, "lufs": -15, "tp": -1.2, "maxrate": "14M", "ext": "mp4"},
    "broadcast": {"name": "Broadcast / TV (16:9, EBU R128)", "w": 1920, "h": 1080, "fps": 30, "max_s": 0,
                  "safe": {"top": 54, "bottom": 54, "left": 96, "right": 96}, "lufs": -23, "tp": -1.0, "maxrate": "20M", "ext": "mp4"},
}

ALIASES = {"reels": "ig_reels", "instagram": "ig_reels", "ig": "ig_reels", "shorts": "yt_shorts", "yt": "youtube",
           "facebook": "fb_reels", "story": "ig_story", "stories": "ig_story", "feed": "ig_feed", "li": "linkedin",
           "twitter": "x", "vsl": "web_vsl", "tv": "broadcast"}


def get(name: str, profile: str = "organic") -> dict:
    """profile: 'organic' (default, the lighter UI of a normal post) or 'ads' (Meta / Google ad overlays)."""
    key = ALIASES.get(name.lower(), name.lower())
    if key not in PLATFORMS:
        raise SystemExit(f"unknown platform '{name}'. Choose from: {', '.join(PLATFORMS)}")
    p = {"id": key, **PLATFORMS[key]}
    p["zone"] = p["organic"] if (profile == "organic" and "organic" in p) else p["safe"]
    p["profile"] = profile
    return p


def aspect(p: dict) -> tuple[int, int]:
    from math import gcd
    g = gcd(p["w"], p["h"])
    return p["w"] // g, p["h"] // g


def caption_band(p: dict) -> tuple[int, int]:
    """(top_y, bottom_y) of the band captions may use: above the platform's bottom UI, below the face zone.
    Measured talking-head edits put captions at 48 to 66% of frame height (writepanda.ai retention study, July 2026);
    we start the band at 50% and end 40 px above the bottom safe zone."""
    zone = p.get("zone", p["safe"])
    top = int(p["h"] * 0.50)
    bottom = p["h"] - zone["bottom"] - 40
    if bottom - top < 140:                      # short canvases (1:1, 16:9): sit just above the UI
        top = max(int(p["h"] * 0.60), bottom - 260)
    return top, bottom


def table() -> str:
    rows = ["platform      size        max   ads t/b/l/r        organic t/b/l/r   loudness"]
    for k, p in PLATFORMS.items():
        s = p["safe"]; o = p.get("organic", s)
        rows.append(f"{k:<13} {p['w']}x{p['h']:<6} {('%ds' % p['max_s']) if p['max_s'] else '-':<5} "
                    f"{s['top']}/{s['bottom']}/{s['left']}/{s['right']:<10} {o['top']}/{o['bottom']}/{o['left']}/{o['right']:<10} {p['lufs']} LUFS / {p['tp']} dBTP")
    return "\n".join(rows)
