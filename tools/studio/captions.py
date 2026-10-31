"""Captions: word-timed ASS in four house styles, plus SRT for the platform's own caption upload.

Rules baked in (sources in RESEARCH.md): 1 to 5 words per screen, split at punctuation and pauses, never start or end a
chunk on a function word, at least 0.3 s on screen, one emphasis mechanism per video, captions live in the band
below the face and above the platform's bottom UI, on screen from the first spoken word.
"""
from __future__ import annotations

import itertools
import math

from .common import FONTS, FPS, FUNC, hex_ass, norm, srt_ts, ts

STYLES = {
    # Hormozi-style: caps, spoken word in the brand accent, pop on the first word of each chunk
    "impact": {"font": "caption", "size": 0.048, "case": "upper", "words": (2, 4), "mechanism": "color", "outline": 5, "shadow": 2, "pop": True, "box": False},
    # the restrained 2024+ look: mixed case, white, soft shadow, no box, weight on the operative word only
    "clean": {"font": "caption_2", "size": 0.044, "case": "mixed", "words": (2, 3), "mechanism": "weight", "outline": 2, "shadow": 3, "pop": False, "box": False},
    # editorial serif single line, sentence case, fades; for cinematic cuts and VSL lower thirds
    "serif": {"font": "display", "size": 0.040, "case": "sentence", "words": (3, 6), "mechanism": "none", "outline": 0, "shadow": 3, "pop": False, "box": False},
    # TikTok-native: dark plate behind the line, spoken word in the accent
    "boxed": {"font": "caption", "size": 0.044, "case": "upper", "words": (2, 4), "mechanism": "color", "outline": 0, "shadow": 0, "pop": False, "box": True},
}


def chunk(ws, lo=2, hi=4):
    """Split a run of words into caption chunks of lo..hi words, at clause ends and pauses, off function words."""
    clauses, cur = [], []
    for w in ws:
        cur.append(w)
        if w["w"][-1:] in ".,?!;:":
            clauses.append(cur); cur = []
    if cur:
        clauses.append(cur)
    merged = []
    for c in clauses:
        if merged and (len(c) < lo or len(merged[-1]) < lo):
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    out = []
    for c in merged:
        n = len(c)
        if n <= hi - 1:
            out.append(c); continue
        k, best = max(1, math.ceil(n / (hi - 0.5))), None
        while best is None:
            for cuts in itertools.combinations(range(1, n), k - 1):
                sizes = [b - a for a, b in zip((0,) + cuts, cuts + (n,))]
                if max(sizes) > hi or min(sizes) < 1:
                    continue
                score = -0.5 * (max(sizes) - min(sizes)) - sum(1 for z in sizes if z == 1)
                for cp in cuts:
                    if norm(c[cp]["w"]) in FUNC: score -= 2
                    if norm(c[cp - 1]["w"]) in FUNC: score -= 2
                    if c[cp]["s"] - c[cp - 1]["e"] > 0.15: score += 2
                if best is None or score > best[0]:
                    best = (score, cuts)
            if best is None:
                k += 1
                if k > n:
                    best = (0, tuple(range(hi - 1, n, hi - 1)))
        cuts = best[1]
        out += [c[a:b] for a, b in zip((0,) + cuts, cuts + (n,))]
    final = []
    for c in out:
        if final and (c[-1]["e"] - c[0]["s"]) < 0.3 and len(final[-1]) + len(c) <= hi:
            final[-1] = final[-1] + c
        else:
            final.append(c)
    return final


def _label(w, case):
    t = w["w"].strip(",.?!;:")
    if case == "upper":
        return t.upper()
    if case == "sentence":
        return t
    return t


def text_top(H, style_id, band_bottom, lines=2):
    """Top edge of a caption block of `lines` lines whose bottom sits on band_bottom."""
    size = int(H * STYLES[style_id]["size"])
    return band_bottom - int(lines * size * 1.25)


def header(W, H, brand, style_id, band_bottom, hook_size=None, placement="bottom", top_margin=0):
    st = STYLES[style_id]
    fonts = brand["fonts"]
    fam = {"caption": fonts["caption"], "caption_2": fonts.get("caption_2", fonts["caption"]), "display": fonts["display"]}
    cap_font = fam[st["font"]]
    txt, acc = hex_ass(brand["colors"]["text"]), hex_ass(brand["colors"]["accent"])
    size = int(H * st["size"])
    mv = (H - band_bottom) if placement == "bottom" else top_margin
    align = 2 if placement == "bottom" else 8
    border = 3 if st["box"] else 1
    back = "&H96000000" if st["box"] else "&H78000000"
    outline = st["outline"] if not st["box"] else 18          # box padding
    sh = st["shadow"]
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,{cap_font},{size},{txt},{txt},&H00000000,{back},0,0,0,0,100,100,0,0,{border},{outline},{sh},{align},70,70,{mv},1",
        f"Style: CapB,{fam['caption']},{size},{txt},{txt},&H00000000,{back},0,0,0,0,100,100,0,0,{border},{outline},{sh},{align},70,70,{mv},1",
        f"Style: Hook,{fam['caption']},{hook_size or int(H * 0.044)},{acc},{acc},&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,5,2,5,80,80,0,1",
        f"Style: HookSerif,{fam['display']},{hook_size or int(H * 0.052)},{txt},{txt},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,4,5,80,80,0,1",
        f"Style: Pop,{fam['display']},{int(H * 0.056)},{acc},{acc},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,4,8,80,80,{int(H * 0.22)},1",
        f"Style: Pill,{fonts.get('mono', 'JetBrains Mono')},{int(H * 0.022)},{txt},{txt},&H00000000,&HB0000000,1,0,0,0,100,100,2,0,3,14,0,2,70,70,{mv + size + 60},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    return "\n".join(lines) + "\n"


def events(segs, words, brand, style_id, speech_end, hook_end=0.0, max_words=None):
    st = STYLES[style_id]
    lo, hi = st["words"]
    if max_words:
        hi = max(lo, min(hi, max_words))
    acc, txt = hex_ass(brand["colors"]["accent"]), hex_ass(brand["colors"]["text"])
    ev, srt = [], []
    for sg in segs:
        seg_end = sg["out_t"] + sg["frames"] / FPS
        ws = words[sg["w0"]:sg["w1"] + 1]
        chunks = chunk(ws, lo, hi)
        for ci, c in enumerate(chunks):
            labels = [_label(w, st["case"]) for w in c]
            a0 = max(0.0, sg["out_t"] + (c[0]["s"] - sg["in"]))
            b0 = max(a0 + 0.2, sg["out_t"] + (c[-1]["e"] - sg["in"]) + 0.2)
            srt.append((a0, min(b0, seg_end), " ".join(w["w"] for w in c)))
            if st["mechanism"] == "none":
                a, b = a0, min(b0, seg_end, speech_end + 0.15)
                if a < hook_end or b - a < 0.05:
                    continue
                ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fad(90,120)}}{' '.join(labels)}")
                continue
            emph_idx = [k for k, w in enumerate(c) if w.get("emph")]
            for k, w in enumerate(c):
                a = sg["out_t"] + (w["s"] - sg["in"])
                if k + 1 < len(c):
                    b = sg["out_t"] + (c[k + 1]["s"] - sg["in"])
                elif ci + 1 < len(chunks):
                    b = sg["out_t"] + (chunks[ci + 1][0]["s"] - sg["in"])
                else:
                    b = min(sg["out_t"] + (w["e"] - sg["in"]) + 0.25, seg_end)
                b = min(b, seg_end, speech_end + 0.15)
                if b - a < 0.02 or a < hook_end:
                    continue
                if st["mechanism"] == "color":
                    parts = [f"{{\\1c{acc if m == k else txt}}}{lab}" for m, lab in enumerate(labels)]
                else:  # weight: the operative word in the heavy face, nothing else changes
                    heavy = emph_idx[:1]
                    parts = [(f"{{\\fnMontserrat Black}}{lab}{{\\r}}" if m in heavy else lab) for m, lab in enumerate(labels)]
                pop = "\\fscx92\\fscy92\\t(0,70,\\fscx100\\fscy100)" if (st["pop"] and k == 0) else ""
                ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Cap,,0,0,0,,{{{pop}}}{' '.join(parts)}")
    return ev, srt


def write_srt(path, srt):
    out, n = [], 1
    for a, b, t in srt:
        out.append(f"{n}\n{srt_ts(a)} --> {srt_ts(b)}\n{t}\n"); n += 1
    path.write_text("\n".join(out))


def ass_filter(ass_path) -> str:
    return f"ass={ass_path}:fontsdir={FONTS}"
