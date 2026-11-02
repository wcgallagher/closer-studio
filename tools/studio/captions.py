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
    # premium VSL / brand film: the UI face in bold, the speaker's own case, a soft shadow instead of a stroke, gold on
    # at most one meaning word per line and 15 % of all words, no per-word flicker, phrases of 3 to 7 words. From the
    # v9 blind A/B (2026-11-02): both cinematic reviews read the caps-and-stroke karaoke as "the Submagic template"
    # under an editorial card system, and the rulebook keeps capitals for reels (TY-07) and two families (TY-01)
    # second panel (2026-11-02): at 3.6 % with a soft glow the captions measured about 1.4:1 against bright sky and lost
    # the muted-phone viewer, so 4.6 % (about 92 px at 1080 on 16:9) with a firm 3 px dark outline and a light blur
    "premium": {"font": "ui", "size": 0.046, "case": "mixed", "words": (3, 7), "mechanism": "keyword", "outline": 3, "shadow": 2,
                "pop": False, "box": False, "bold": True, "soft": True, "max_chars": 42},
}

# words that bind to the word after them: a line never ends on one (an article, a preposition, an auxiliary or modal,
# a negation, a subject pronoun, a contraction). v8 broke "DON'T / WANT", "WHAT I'M / GOING", "WE'VE / DONE".
BIND_NEXT = {"a", "an", "the", "to", "of", "in", "on", "at", "for", "with", "from", "by", "about", "into", "over", "as",
             "and", "or", "but", "if", "so", "that", "which", "who", "than", "my", "your", "our", "their", "his", "her", "its",
             "i", "you", "we", "they", "he", "she", "it", "is", "are", "was", "were", "be", "been", "am", "do", "does", "did",
             "have", "has", "had", "can", "could", "will", "would", "should", "may", "might", "must", "not", "no", "going",
             "gonna", "want", "wanna", "im", "youre", "were", "theyre", "its", "thats", "whats", "theres", "dont", "doesnt",
             "didnt", "cant", "wont", "isnt", "arent", "wasnt", "ive", "weve", "youve", "theyve", "ill", "youll", "id",
             "youd", "just", "very", "these", "those", "this", "every", "some", "any", "how", "what", "where", "when",
             # adverbs before their verb and adjectives before their noun ("I always | recommend", "live | sales")
             "always", "never", "also", "actually", "really", "even", "still", "extremely", "live", "good", "existing",
             "old", "new", "real", "big", "whole", "next", "last", "first", "simple"}
# pairs read as one unit: never split between them
COLLOC = {("life", "insurance"), ("mortgage", "protection"), ("right", "now"), ("worry", "about"), ("ask", "of"),
          ("training", "calls"), ("can", "now"), ("now", "capture"), ("protection", "agents"), ("insurance", "agents"), ("50-50", "split"), ("one", "thing"), ("p.m.", "we"), ("book", "of"), ("of", "business"),
          ("two", "or"), ("or", "three"), ("a", "lot"), ("each", "other"), ("sales", "presentations"), ("time", "commitment")}
# meaning words that may take the gold in the keyword mechanism, besides any number or money figure
KEYWORDS = {"free", "money", "bag", "split", "50-50", "wednesday", "regret", "sell", "set", "selling", "setting", "close",
            "retirement", "401k", "401(k)", "ira", "training", "account", "simple", "big", "paid", "exactly", "program"}


# display spellings: the same word on screen in captions and cards (rulebook CP-04); formatting, never rewording
DISPLAY = {"401k": "401(k)", "401ks": "401(k)s", "403b": "403(b)", "457b": "457(b)", "50-50": "50/50"}


def chunk(ws, lo=2, hi=4, max_chars=None):
    """Split a run of words into caption chunks of lo..hi words, at clause ends and pauses, off function words.
    Clauses longer than hi words are split by a dynamic program over the cut positions (linear in the clause length):
    groups near hi words, a group of one word costs extra, a line that ends on a word binding to the next (BIND_NEXT)
    or splits a fixed pair (COLLOC) costs 5, a line starting on a function word 0.5, a cut at a pause of more than
    150 ms earns 2. A beat change in a multi-take selects (the words' "beat") is a sentence end even without a period."""
    clauses, ends, cur = [], [], []
    for k, w in enumerate(ws):
        cur.append(w)
        nb = ws[k + 1].get("beat") if k + 1 < len(ws) else None
        beat_end = nb is not None and w.get("beat") is not None and nb != w["beat"]
        if w["w"][-1:] in ".,?!;:" or beat_end:
            clauses.append(cur); ends.append(w["w"][-1:] in ".?!" or beat_end); cur = []
    if cur:
        clauses.append(cur); ends.append(True)
    # a short clause joins its neighbour: the one before when it continues that sentence, the one after when it opens
    # a new sentence ("Finally," + "a program that's here..."); a whole short sentence ("Pretty simple.") keeps its line
    merged, m_end, carry = [], [], []
    for k, c in enumerate(clauses):
        c = carry + c; carry = []
        starts_sentence = k == 0 or ends[k - 1]
        if len(c) < lo and starts_sentence and not ends[k] and k + 1 < len(clauses):
            carry = c; continue
        if merged and len(c) < lo and not (starts_sentence and ends[k]) and not m_end[-1]:
            merged[-1] = merged[-1] + c; m_end[-1] = ends[k]
        elif merged and len(merged[-1]) < lo and not m_end[-1]:
            merged[-1] = merged[-1] + c; m_end[-1] = ends[k]
        else:
            merged.append(c); m_end.append(ends[k])
    if carry:
        merged.append(carry); m_end.append(True)
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
                cost = best[j] + 0.5 * (hi - size) + (3.0 if size == 1 else 2.5 if size < lo else 0.0)   # no orphan lines
                if max_chars and len(" ".join(w["w"] for w in c[j:i])) > max_chars:
                    cost += 8.0                                   # one line of at most max_chars (rulebook CP-01: 42)
                if c[i - 1]["e"] - c[j]["s"] < 0.6:
                    cost += 3.0                                   # a line read in under 0.6 s is a flash (CP-02)
                if j > 0:
                    prev, nxt = norm(c[j - 1]["w"]), norm(c[j]["w"])
                    if prev in BIND_NEXT or prev in FUNC: cost += 5       # a line never ends on a word that needs the next
                    if nxt in FUNC: cost += 0.5                          # starting on "and" / "to" reads fine
                    if (c[j - 1]["w"].lower().strip(",.?!;:"), c[j]["w"].lower().strip(",.?!;:")) in COLLOC: cost += 5
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


def _keywords(words, segs, share=0.15):
    """{index of a chunk's first word -> position of its gold word}: computed per chunk later; here, which words may
    take the gold at all: a number or money figure (score 3), a meaning word (2), a loudness emphasis (1), keeping the
    best `share` of all words."""
    def score(w):
        t = w["w"].lower().strip(",.?!;:")
        if "$" in t or "%" in t or "-" in t and any(ch.isdigit() for ch in t) or sum(ch.isdigit() for ch in t) >= 2:
            return 3                                    # a figure (a lone digit, as in "1 p.m.", is not one)
        return 2 if t in KEYWORDS else 0                # loudness alone does not earn the gold
    idx = [i for i, w in enumerate(words) if score(w) > 0]
    idx.sort(key=lambda i: -score(words[i]))
    keep = set(idx[:max(1, int(len(words) * share))])
    return _KwMap(words, keep, score)


class _KwMap(dict):
    """Looks up a chunk by its first word's index and returns the position of its best allowed word (one per line)."""
    def __init__(self, words, keep, score):
        super().__init__(); self.words, self.keep, self.score = words, keep, score

    def get(self, i0, default=None):
        best, bp, k = 0, None, 0
        while i0 + k < len(self.words) and k < 8:
            i = i0 + k
            if i in self.keep and self.score(self.words[i]) > best:
                best, bp = self.score(self.words[i]), k
            if self.words[i]["w"][-1:] in ".,?!;:" and k > 0:
                break
            k += 1
        return bp


def _label(w, case):
    raw = w["w"]
    t = raw.strip(",.?!;:")
    if "." in t and raw.rstrip(",?!;:").endswith("."):      # an abbreviation keeps its last period ("p.m.")
        t = raw.rstrip(",?!;:")
    t = DISPLAY.get(t.lower(), t)
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
    fam = {"caption": fonts["caption"], "caption_2": fonts.get("caption_2", fonts["caption"]), "display": fonts["display"],
           "ui": fonts.get("ui", "Inter")}
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
        f"Style: Cap,{cap_font},{size},{txt},{txt},{'&H30000000' if st.get('soft') else '&H00000000'},{back},{-1 if st.get('bold') else 0},0,0,0,100,100,0,0,{border},{outline},{sh},{align},70,70,{mv},1",
        f"Style: CapB,{fam['caption']},{size},{txt},{txt},&H00000000,{back},0,0,0,0,100,100,0,0,{border},{outline},{sh},{align},70,70,{mv},1",
        f"Style: Hook,{fam['caption']},{hook_size or int(H * 0.044)},{acc},{acc},&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,5,2,5,80,80,0,1",
        f"Style: HookSerif,{fam['display']},{hook_size or int(H * 0.052)},{txt},{txt},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,4,5,80,80,0,1",
        f"Style: Pop,{fam['display']},{int(H * 0.064)},{acc},{acc},&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,4,8,80,80,{int(H * 0.22)},1",
        f"Style: Pill,{fonts.get('mono', 'JetBrains Mono')},{int(H * 0.022)},{txt},{txt},&H00000000,&HB0000000,1,0,0,0,100,100,2,0,3,14,0,2,70,70,{mv + size + 60},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    return "\n".join(lines) + "\n"


def _snap(a, b, cuts):
    """No line straddles a hard cut (a full-screen card in or out, the end card): a line that would start just before
    a cut starts on it; a line a cut interrupts ends 2 frames before it (rulebook CP-02, AS-29)."""
    for c in cuts or []:
        if c - 0.2 <= a < c:
            a = c
        elif a < c < b:
            b = c - 2 / FPS
    return a, b


def events(segs, words, brand, style_id, speech_end, hook_end=0.0, max_words=None, words_range=None, plain=None, off=None,
           cuts=None):
    """plain: output windows where the line shows without the spoken-word highlight (over a card); off: windows with no
    burned caption at all (the SRT keeps every line)."""
    st = STYLES[style_id]
    lo, hi = tuple(words_range) if words_range else st["words"]
    inside = lambda t, wins: any(a - 0.05 <= t < b for a, b in (wins or []))
    if max_words:
        hi = max(lo, min(hi, max_words))
    acc, txt = hex_ass(brand["colors"].get("caption_accent") or brand["colors"]["accent"]), hex_ass(brand["colors"]["text"])
    ev, srt = [], []
    kw = _keywords(words, segs) if st["mechanism"] == "keyword" else {}
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
        chunks = chunk(ws, lo, hi, st.get("max_chars"))
        if st["mechanism"] == "keyword":
            for ci, c in enumerate(chunks):
                labels = [_label(w, st["case"]) for w in c]
                a0 = max(0.0, O(c[0]))
                b0 = max(a0 + 0.3, Oe(c[-1]) + 0.25)
                srt.append((a0, min(b0, seg_end), " ".join(w["w"] for w in c)))
                if inside(a0, off):
                    continue
                a, b = a0, min(b0, seg_end, speech_end + 0.15)
                if ci + 1 < len(chunks):        # one line on screen at a time
                    b = min(b, O(chunks[ci + 1][0]) - 1 / FPS)
                if a < hook_end or b - a < 0.05:
                    continue
                if not ev and a < 0.8 and hook_end <= 0:      # the first line is on frame 0: a muted autoplay opens on words
                    a = 0.0
                a, b = _snap(a, b, cuts)
                if b - a < 0.05:
                    continue
                k = None if inside(a0, plain) else kw.get(pos[id(c[0])])
                parts = [(f"{{\\1c{acc}}}{lab}{{\\1c{txt}}}" if (k is not None and m == k) else lab) for m, lab in enumerate(labels)]
                ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fad(80,60)\\blur1.5}}{' '.join(parts)}")
            continue
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
