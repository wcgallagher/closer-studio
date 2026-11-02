"""Captions: word-timed ASS in four house styles, plus SRT for the platform's own caption upload.

Rules baked in (sources in RESEARCH.md): 1 to 5 words per screen, split at punctuation and pauses, never start or end a
chunk on a function word, at least 0.3 s on screen, one emphasis mechanism per video, captions live in the band
below the face and above the platform's bottom UI, on screen from the first spoken word.
"""
from __future__ import annotations

import itertools
import math

from .common import FONTS, FPS, FUNC, hex_ass, norm, srt_ts, ts, fpath

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
    """Split a run of words into caption chunks of lo..hi words, at clause ends and pauses, off function words.
    Clauses longer than hi words are split by a dynamic program over the cut positions (linear in the clause length):
    groups near hi words, a group of one word costs extra, a cut on a function word costs 2 per side, a cut at a pause
    of more than 150 ms earns 2."""
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
        if n <= hi:
            out.append(c); continue
        INF = 1e9
        best = [INF] * (n + 1); back = [0] * (n + 1)
        best[0] = 0.0
        for i in range(1, n + 1):
            for size in range(1, hi + 1):
                j = i - size
                if j < 0:
                    break
                cost = best[j] + 0.5 * (hi - size) + (3.0 if size == 1 else 0.0)
                if j > 0:
                    if norm(c[j]["w"]) in FUNC: cost += 2
                    if norm(c[j - 1]["w"]) in FUNC: cost += 2
                    if c[j]["s"] - c[j - 1]["e"] > 0.15: cost -= 2
                if cost < best[i]:
                    best[i], back[i] = cost, j
        cuts, i = [], n
        while i > 0:
            cuts.append(back[i]); i = back[i]
        cuts = sorted(set(cuts) - {0})
        out += [c[a:b] for a, b in zip([0] + cuts, cuts + [n])]
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
    size = int(H * st["size"] * (1.85 if W > H else 1.0))     # a 16:9 frame needs about the same pixel height as a 9:16 one (v7: 96 px at 1080)
    mv = (H - band_bottom) if placement == "bottom" else top_margin
    align = 2 if placement == "bottom" else 8
    border = 3 if st["box"] else 1
    back = "&H96000000" if st["box"] else "&H78000000"
    outline = st["outline"] if not st["box"] else 18          # box padding
    sh = st["shadow"]
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "YCbCr Matrix: TV.709", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,{cap_font},{size},{txt},{txt},&H00000000,{back},0,0,0,0,100,100,0,0,{border},{outline},{sh},{align},70,70,{mv},1",
        f"Style: CapB,{fam['caption']},{size},{txt},{txt},&H00000000,{back},0,0,0,0,100,100,0,0,{border},{outline},{sh},{align},70,70,{mv},1",
        f"Style: Hook,{fam['caption']},{hook_size or int(H * 0.044)},{acc},{acc},&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,5,2,5,80,80,0,1",
        f"Style: HookSerif,{fam['display']},{hook_size or int(H * 0.052)},{txt},{txt},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,4,5,80,80,0,1",
        f"Style: Pop,{fam['display']},{int(H * 0.064)},{acc},{acc},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,4,8,80,80,{int(H * 0.22)},1",
        f"Style: Pill,{fonts.get('mono', 'JetBrains Mono')},{int(H * 0.022)},{txt},{txt},&H00000000,&HB0000000,1,0,0,0,100,100,2,0,3,14,0,2,70,70,{mv + size + 60},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    return "\n".join(lines) + "\n"


def events(segs, words, brand, style_id, speech_end, hook_end=0.0, max_words=None, words_range=None, plain=None, off=None):
    """plain: output windows where the line shows without the spoken-word highlight (over a card); off: windows with no
    burned caption at all (the SRT keeps every line)."""
    st = STYLES[style_id]
    lo, hi = tuple(words_range) if words_range else st["words"]
    inside = lambda t, wins: any(a - 0.05 <= t < b for a, b in (wins or []))
    if max_words:
        hi = max(lo, min(hi, max_words))
    acc, txt = hex_ass(brand["colors"].get("caption_accent") or brand["colors"]["accent"]), hex_ass(brand["colors"]["text"])
    ev, srt = [], []
    # chunk over a whole breath (a piece and the punch-ins that continue it), not per punch-in, so a chunk never starts
    # on the tail of a phrase just because the framing changed there
    runs = []
    for sg in segs:
        if runs and sg.get("cont"):
            runs[-1].append(sg)
        else:
            runs.append([sg])
    for run in runs:
        seg_of = {i: sg for sg in run for i in range(sg["w0"], sg["w1"] + 1)}
        i0 = run[0]["w0"]
        ws = words[i0:run[-1]["w1"] + 1]
        pos = {id(w): i0 + k for k, w in enumerate(ws)}
        O = lambda w: seg_of[pos[id(w)]]["out_t"] + (w["s"] - seg_of[pos[id(w)]]["in"])
        Oe = lambda w: seg_of[pos[id(w)]]["out_t"] + (w["e"] - seg_of[pos[id(w)]]["in"])
        seg_end = run[-1]["out_t"] + run[-1]["frames"] / FPS
        sg = run[0]
        chunks = chunk(ws, lo, hi)
        for ci, c in enumerate(chunks):
            labels = [_label(w, st["case"]) for w in c]
            a0 = max(0.0, O(c[0]))
            b0 = max(a0 + 0.2, Oe(c[-1]) + 0.2)
            srt.append((a0, min(b0, seg_end), " ".join(w["w"] for w in c)))
            if inside(a0, off):
                continue
            if st["mechanism"] == "none" or inside(a0, plain):
                a, b = a0, min(b0, seg_end, speech_end + 0.15)
                if ci + 1 < len(chunks):        # one line on screen at a time: never overlap the next chunk
                    b = min(b, O(chunks[ci + 1][0]) - 1 / FPS)
                if a < hook_end or b - a < 0.05:
                    continue
                ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fad(90,120)}}{' '.join(labels)}")
                continue
            emph_idx = [k for k, w in enumerate(c) if w.get("emph")]
            for k, w in enumerate(c):
                a = O(w)
                if k + 1 < len(c):
                    b = O(c[k + 1])
                elif ci + 1 < len(chunks):
                    b = O(chunks[ci + 1][0])
                else:
                    b = min(Oe(w) + 0.25, seg_end)
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
    return f"ass={fpath(ass_path)}:fontsdir={fpath(FONTS)}"
