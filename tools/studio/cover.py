"""Cover frames and thumbnails: the best face frame, graded, with a 2 to 4 word title in the display face."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

from . import grade, track as trk
from .common import FONTS, probe


def best_time(an: dict | None, start: float, end: float) -> float:
    """A frame where the face is large and the detector is sure, near the hook."""
    if not an or not an.get("track"):
        return start + 0.8
    dets = [d for d in an["track"]["dets"] if "cx" in d and 0.3 <= d["t"] <= min(8.0, end - start)]
    if not dets:
        return start + 0.8
    best = max(dets, key=lambda d: d["score"] * (1 + d["fh"]))
    return start + best["t"]


def grab(video: Path, t: float, out_png: Path, lut_preset: str | None = None):
    vf = "format=rgb24"
    lp = grade.lut_path(lut_preset) if lut_preset else None
    if lp:
        vf = f"lut3d=file={lp}," + vf
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-vf", vf, str(out_png)], check=True)
    return out_png


def compose(frame_png: Path, title: str, brand: dict, W: int, H: int, out: Path, face_box=None, position: str = "auto"):
    """Crop or fit the frame to W x H around the face, darken a band, set the title. Returns the path."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    img = Image.open(frame_png).convert("RGB")
    sw, sh = img.size
    ar = W / H
    cw, ch = (sw, int(sw / ar)) if sw / sh > ar else (int(sh * ar), sh)
    cw, ch = min(cw, sw), min(ch, sh)
    fx, fy = (face_box[0] + face_box[2] / 2, face_box[1] + face_box[3] / 2) if face_box else (sw / 2, sh * 0.42)
    x0 = int(min(max(fx - cw / 2, 0), sw - cw))
    y0 = int(min(max(fy - ch * 0.42, 0), sh - ch))
    img = img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
    c = brand["colors"]
    # title band: top if the face sits low, else bottom
    face_top_frac = ((fy - face_box[3] / 2 - y0) / ch) if face_box else 0.25
    where = position if position != "auto" else ("top" if face_top_frac > 0.42 else "bottom")
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bh = int(H * 0.34)
    for i in range(bh):
        a = int(200 * (i / bh) ** 1.4) if where == "bottom" else int(200 * (1 - i / bh) ** 1.4)
        y = H - bh + i if where == "bottom" else i
        bd.line([(0, y), (W, y)], fill=(8, 6, 5, a))
    img = Image.alpha_composite(img.convert("RGBA"), band)
    d = ImageDraw.Draw(img)
    ff = FONTS / brand["fonts"]["caption_file"]
    words = title.strip().split()
    px = int(H * (0.11 if W < H else 0.13))
    while px > 30:
        f = ImageFont.truetype(str(ff), px)
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if f.getlength(t) <= W * 0.88:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 2 and all(f.getlength(l) <= W * 0.88 for l in lines):
            break
        px -= 4
    lh = int(px * 1.12)
    total = lh * len(lines)
    y = (H - int(H * 0.06) - total) if where == "bottom" else int(H * 0.07)
    for i, ln in enumerate(lines):
        tw = f.getlength(ln.upper())
        x = (W - tw) / 2
        fill = c["accent"] if i == len(lines) - 1 and len(lines) > 1 else c["text"]
        d.text((x + 4, y + 5), ln.upper(), font=f, fill=(0, 0, 0, 190))
        d.text((x, y), ln.upper(), font=f, fill=fill)
        y += lh
    img.convert("RGB").save(out, quality=92)
    return out


def build(video: Path, out_dir: Path, brand: dict, title: str, an: dict | None = None, at: float | None = None,
          start: float = 0.0, end: float | None = None, log=print) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    end = end if end is not None else info["dur"]
    t = at if at is not None else best_time(an, start, end)
    frame = grab(video, t, out_dir / "cover_frame.png", brand["style"].get("lut"))
    box = None
    if an and an.get("track"):
        dets = [d for d in an["track"]["dets"] if "cx" in d]
        if dets:
            d = min(dets, key=lambda d: abs(start + d["t"] - t))
            box = ((d["cx"] - d["fw"] / 2) * info["w"], (d["cy"] - d["fh"] / 2) * info["h"], d["fw"] * info["w"], d["fh"] * info["h"])
    thumb = compose(frame, title, brand, 1280, 720, out_dir / "thumbnail.jpg", box)
    cover = compose(frame, title, brand, 1080, 1920, out_dir / "cover.jpg", box)
    log(f"cover frames from {t:.2f} s: {thumb.name}, {cover.name}")
    return {"time": round(t, 2), "thumbnail": str(thumb), "cover": str(cover)}
