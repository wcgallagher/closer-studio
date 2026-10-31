"""Shared helpers: shell, probing, timecodes, colours, paths."""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # tools/studio
TOOLS = HERE.parent                              # tools
KIT = TOOLS.parent                               # the closer-studio folder
FONTS = KIT / "fonts"
MODELS = HERE / "models"
LUTS = TOOLS / "vsl" / "luts"
FPS = 30

FUNC = {"to", "of", "the", "a", "an", "is", "and", "or", "we", "i", "you", "that", "in", "for", "at", "on", "it", "by",
        "your", "my", "how", "do", "what", "if", "this", "be", "are", "so", "its", "im", "youre", "were", "theyre", "not",
        "with", "but", "as", "was", "they", "he", "she", "them", "us", "our", "their", "than", "then", "there", "here"}
FILLERS = {"um", "uh", "umm", "uhh", "hmm", "mm", "mmm", "erm", "ah", "er", "uhm"}


def sh(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"command failed:\n{' '.join(map(str, cmd))[:600]}\n{r.stderr[-2000:]}")
    return r.stdout


def probe(video) -> dict:
    d = json.loads(sh(["ffprobe", "-v", "error", "-select_streams", "v:0",
                       "-show_entries", "stream=width,height,r_frame_rate,nb_frames:format=duration", "-of", "json", video]))
    st = d["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    return {"w": int(st["width"]), "h": int(st["height"]), "fps": float(num) / float(den or 1),
            "dur": float(d["format"]["duration"])}


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9$]", "", w.lower())


def hex_ass(h: str, alpha: str = "00") -> str:
    """#RRGGBB to ASS &HAABBGGRR&."""
    h = h.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}&"


def ts(x: float) -> str:
    x = math.floor(max(x, 0) * 100) / 100
    h, r = divmod(x, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def srt_ts(x: float) -> str:
    x = max(x, 0)
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int((x % 1) * 1000):03d}"


def even(x: float) -> int:
    return int(round(x / 2) * 2)


def esc_drawtext(s: str) -> str:
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")


def load_json(p: Path, default=None):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return default


def save_json(p: Path, obj):
    Path(p).write_text(json.dumps(obj, indent=1))
