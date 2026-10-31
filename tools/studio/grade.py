"""Picture: generated 3D LUTs, face fill light, clarity, vignette, grain.

The LUT generator reproduces sma_pro.cube (the SMA VSL grade): a mid lift, an S-curve around a pivot, a tanh shoulder
so highlights roll off instead of clipping, split toning (warm highlights, cool shadows), saturation and vibrance.
Presets are parameter sets; `.cube` files are written once into tools/studio/luts/.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .common import HERE, LUTS

LUT_DIR = HERE / "luts"
POST = "unsharp=lx=13:ly=13:la=0.30,unsharp=5:5:0.45,vignette=a=0.35"

PRESETS = {
    # the SMA VSL grade, measured on the XTRA Muse takes
    "sma_pro": dict(gamma=0.88, contrast=1.16, pivot=0.44, shoulder=0.82, hi=(0.020, 0.006, -0.016), sh=(-0.006, 0.000, 0.012), sat=1.10, vib=0.18),
    # Become The Closer: deeper blacks, ember-orange highlights, brown-cool shadows
    "btc_ember": dict(gamma=0.92, contrast=1.22, pivot=0.42, shoulder=0.80, hi=(0.030, 0.010, -0.020), sh=(-0.004, -0.004, 0.008), sat=1.06, vib=0.22),
    # neutral: contrast and a touch of life, no tint
    "clean": dict(gamma=0.96, contrast=1.08, pivot=0.45, shoulder=0.86, hi=(0, 0, 0), sh=(0, 0, 0), sat=1.04, vib=0.10),
    # teal shadows / orange highlights, slightly desaturated
    "cinematic": dict(gamma=0.90, contrast=1.18, pivot=0.43, shoulder=0.80, hi=(0.028, 0.008, -0.018), sh=(-0.016, 0.004, 0.022), sat=0.94, vib=0.16),
    # pass-through
    "none": None,
}


def _curve(x, p):
    y = np.power(np.clip(x, 0, 1), p["gamma"])
    y = p["pivot"] + (y - p["pivot"]) * p["contrast"]
    s = p["shoulder"]
    hi = y > s
    y[hi] = s + (1 - s) * np.tanh((y[hi] - s) / (1 - s))
    return np.clip(y, 0, 1)


def make_lut(preset: str, size: int = 33) -> Path:
    p = PRESETS[preset]
    LUT_DIR.mkdir(parents=True, exist_ok=True)
    path = LUT_DIR / f"{preset}.cube"
    if path.exists():
        return path
    g = np.linspace(0, 1, size)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")          # .cube order: R fastest
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    rgb = _curve(rgb, p)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    wh, ws = (lum ** 2)[:, None], ((1 - lum) ** 2)[:, None]
    rgb = rgb + wh * np.array(p["hi"]) + ws * np.array(p["sh"])
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    satv = rgb.max(1) - rgb.min(1)
    k = p["sat"] * (1 + p["vib"] * (1 - satv))[:, None]
    rgb = lum[:, None] + (rgb - lum[:, None]) * k
    rgb = np.clip(rgb, 0, 1)
    lines = [f"TITLE \"closer-studio {preset}\"", f"LUT_3D_SIZE {size}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    lines += [f"{x:.6f} {y:.6f} {z:.6f}" for x, y, z in rgb]
    path.write_text("\n".join(lines) + "\n")
    return path


def lut_path(preset: str) -> Path | None:
    if preset in (None, "", "none"):
        return None
    if preset == "sma_pro" and (LUTS / "sma_pro.cube").exists():
        return LUTS / "sma_pro.cube"
    if preset not in PRESETS:
        raise SystemExit(f"unknown grade '{preset}'. Presets: {', '.join(k for k in PRESETS)}")
    return make_lut(preset)


def write_fill(path: Path, W: int, H: int, fx: float = 0.5, fy: float = 0.36, strength: float = 0.28):
    """A soft warm fill light centred on the face, as an RGBA PNG to overlay."""
    from PIL import Image
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - fx * W) / (W * 0.52)) ** 2 + ((y - fy * H) / (H * 0.32)) ** 2)
    a = np.clip(1 - d, 0, 1) ** 1.6
    img = np.zeros((H, W, 4), np.uint8); img[..., 0] = 255; img[..., 1] = 246; img[..., 2] = 236
    img[..., 3] = (a * 255 * strength).astype(np.uint8)
    Image.fromarray(img, "RGBA").save(path)


def vf(preset: str, grain: float = 0.0, post: bool = True) -> str:
    """Video filter fragment (apply after the crop, before any text)."""
    parts = []
    lp = lut_path(preset)
    if lp:
        parts.append(f"lut3d=file={lp}")
    if post:
        parts.append(POST)
    if grain and grain > 0:
        parts.append(f"noise=alls={int(grain * 100)}:allf=t")
    return ",".join(parts)
