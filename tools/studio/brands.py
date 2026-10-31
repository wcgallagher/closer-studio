"""Brand tokens. One JSON per brand in brand/<id>.json; `python3 -m studio brands` lists them."""
from __future__ import annotations

import json
from pathlib import Path

from .common import KIT

BRAND_DIR = KIT / "brand"

DEFAULT = {
    "id": "generic", "name": "Generic", "site": "", "handle": "",
    "colors": {"bg": "#0B0B0C", "accent": "#F2C14E", "accent_soft": "#F7D98A", "text": "#F5F2EC", "muted": "#9A958C", "panel": "#1C1C1F"},
    "fonts": {"caption": "Montserrat Black", "caption_file": "Montserrat-Black.ttf", "caption_2": "Montserrat ExtraBold",
              "caption_2_file": "Montserrat-ExtraBold.ttf", "display": "Fraunces Display", "display_file": "FrauncesDisplay-Bold.ttf", "mono": "JetBrains Mono"},
    "cta": {"line": "", "sub": ""},
    "style": {"captions": "impact", "lut": "clean", "music": "", "grain": 0.0},
    "words": {"never": [], "result_disclaimer": ""},
}


def list_brands():
    return sorted(p.stem for p in BRAND_DIR.glob("*.json"))


def load(brand_id: str) -> dict:
    p = BRAND_DIR / f"{brand_id}.json"
    if not p.exists():
        raise SystemExit(f"no brand '{brand_id}'. Brands: {', '.join(list_brands()) or '(none)'}. Add brand/{brand_id}.json (see brand/README.md).")
    b = json.loads(p.read_text())
    out = json.loads(json.dumps(DEFAULT))
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def check_copy(brand: dict, text: str) -> list[str]:
    """Words the brand never prints. Returns the offenders found in `text`."""
    low = f" {text.lower()} "
    return [w for w in brand["words"].get("never", []) if f" {w.lower()} " in low or f" {w.lower()}." in low or f" {w.lower()}," in low]
