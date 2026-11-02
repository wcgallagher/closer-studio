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


_FF_MAJOR = None


def ffmpeg_major() -> int:
    """The installed ffmpeg's major version (cached)."""
    global _FF_MAJOR
    if _FF_MAJOR is None:
        out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout
        m = re.search(r"ffmpeg version n?(\d+)", out)
        _FF_MAJOR = int(m.group(1)) if m else 6
    return _FF_MAJOR


def graph_file_flag() -> str:
    """The option that reads a filter graph from a file: '-/filter_complex' from ffmpeg 7 on ('-filter_complex_script'
    is deprecated in 7 and 8 and gone in 9, the version Homebrew and the Windows builds ship), the old one before 7."""
    return "-/filter_complex" if ffmpeg_major() >= 7 else "-filter_complex_script"


def fpath(path) -> str:
    """A file path written inside an ffmpeg filter graph. Windows drive letters ("C:") and backslashes break the graph
    parser, so slashes go forward and colons are escaped; on Mac and Linux the path is unchanged."""
    return str(path).replace("\\", "/").replace(":", "\\:")


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
