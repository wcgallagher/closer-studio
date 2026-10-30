"""SMA VSL v7 builder (v6 + motion-graphic cutaways rendered from vsl/mg/scenes.html, blur transitions, B&W FOMO beat) (sma-vsl-producer skill, audited facts only).

Reads the frame maps (word timing + silence windows), locks the beat sheet, splits every beat at dead air
longer than 0.3 s, assigns 100% / 112% punch-ins, and writes:
  <out>/edit_decision_list.json   frame-exact cut list (ms)
  <out>/vsl_script_active.txt     the locked script, by beat
  <out>/captions.ass              word-highlight captions + text slams + CTA
  <out>/render_vsl.sh             standalone, multi-threaded FFmpeg render

Usage: python v7_build.py <frame_map_dir> <raw_dir> <out_dir> [--preview]
"""

import json
import math
import re
import sys
from pathlib import Path

FMAP, RAW, OUT = (Path(p) for p in sys.argv[1:4])
PREVIEW = "--preview" in sys.argv
OUT.mkdir(parents=True, exist_ok=True)
FPS = 30
W, H = (1280, 720) if PREVIEW else (1920, 1080)
SX = W / 1920

GAP_MAX = 0.30      # dead air longer than this gets cut
PAD_IN = 0.05       # before the first word of a piece
PAD_OUT_MAX = 0.18  # how far a piece may run into the silence after its last word
PUNCH = 1.12        # 100% -> 112%

# Beat sheet: (beat, take, first word, its approx start s, last word, its approx start s)
BEATS = [
    ("HOOK",      "take2", "Life",      0.00, "business.",   5.6),
    ("PROBLEM",   "take2", "There",     7.86, "manage.",    19.0),
    ("STAKES",    "take1", "The",      30.96, "market.",    47.9),
    ("WHY NOW",   "take3", "In",        6.02, "apps,",       8.3),
    ("WHY NOW",   "take3", "Now,",     13.24, "virtual,",   15.9),
    ("WHY NOW",   "take3", "And",      25.22, "business.",  28.78),
    ("PIVOT",     "take3", "want",     34.00, "appointments.", 35.98),   # the hand gesture: SELL (his right) / SET (his left)
    ("MECHANISM", "take2", "So",       20.00, "annuities.", 34.0),
    ("OFFER",     "take3", "If",       36.76, "simple.",    42.9),
    ("TRAINING",  "take3", "if",       47.0,  "free.",      50.0),
    ("TRAINING",  "take1", "Wednesday", 85.22, "call.",      87.24),
    ("URGENCY",   "take2", "Annuities", 47.92, "later.",     55.40),
    ("CTA",       "take2", "If",       82.04, "training.",  91.1),
    ("CTA",       "take3", "Now",      50.94, "below,",     52.50),
    ("CLOSE",     "take3", "Finally,", 66.36, "soon.",      68.50),
]

# Full-frame text slams: (take, anchor word, approx time, text, seconds, subline). Audited: sma-vsl-producer/AUDIT.md
SLAMS_V6 = [
    ("take1", "have",      32.78, "\u201cI HAVE A 401(K)\u201d", 1.4, "WHAT YOUR CLIENTS ALREADY TELL YOU"),
    ("take2", "two",       26.0,  "2-3 QUESTIONS",                1.4, "THAT FIND THE MONEY"),
    ("take3", "50-50",     41.8,  "50/50",                        1.3, "ON EVERY CASE THAT CLOSES"),
    ("take2", "Annuities", 47.92, "$434.1B",                      2.2, "2024 U.S. ANNUITY SALES. A RECORD."),
]
SLAMS = []   # v6 slams now live inside the cutaways
SOURCES = {"$434.1B": "SOURCE: LIMRA"}
HEADLINE = "THE MONEY\\NIS ALREADY\\NIN YOUR BOOK."
HEAD_END = 3.5
# continuous punch-ins inside long shots: (take, word, approx time). Audio is not cut, only the framing jumps.
PUNCH_AT = [("take2", "which", 25.16), ("take2", "and", 28.72)]
AUTO_PUNCH_S = 2.4  # a long shot gets a continuous punch-in about this often (audio runs on)
ZOOMS = (1.12, 1.22)  # odd pieces alternate between these; even pieces sit at 100%
KICK_S = 0.27       # zoom-kick transition at every new beat
SHAKE = (14, 9)     # px at 1080p, x / y, decaying over 0.4 s on every slam
# Side callouts over the sky on the right: ([(take, word, near, text)], end (take, word, near) or None, strike_on_last)
CALLOUTS_V6 = [
    ([("take2", "401k", 10.88, "401(K)"), ("take2", "IRA", 11.6, "IRA"), ("take2", "old", 12.32, "STOCKS")],
     ("take2", "Because", 15.14), False),
    ([("take3", "person", 7.48, "IN PERSON"), ("take3", "paper", 8.02, "PAPER APPS"), ("take3", "virtual", 15.94, "VIRTUAL")],
     None, True),
    ([("take2", "tee", 29.44, "YOU SET IT"), ("take2", "specialist", 30.18, "WE CLOSE IT")], None, False),
    ([("take1", "Wednesday", 85.22, "TRAINING"), ("take1", "at", 85.7, "WEDS 1 PM")], None, False),
]
CALLOUTS = []
MUSIC = ("Industrial Cinematic.mp3", 85.0)   # Kevin MacLeod (incompetech.com), CC BY 4.0; file, start offset s
MIN_PIECE = 1.0     # pieces shorter than this merge into the one before (no sub-second zoom ping-pong)
HOLD_S = 2.8        # end card (motion graphic) after the last word
IN_FIX = {("take1", "wednesday"): 85.14}
ZOOM_FIX = {("take3", "want"): 1.0}      # keep both hands in frame for the SET / SELL labels   # whisper ends 'directly' late; the true gap is 85.12-85.17

NAME_TAG = ("CHASE GALLAGHER", "$3.8M PLACED IN 2025 WITH 20+ AGENTS")
CTA_TEXT = "CREATE YOUR FREE ACCOUNT BELOW"

KEYWORDS = {"annuities", "annuity", "401k", "ira", "retirement", "commission", "free", "split", "5050",
            "specialist", "money", "questions", "agents", "account", "virtual", "regret",
            "training", "blueprint", "business"}
DISPLAY = {"401K": "401(K)", "50-50": "50/50", "P.M.": "PM", "P.M": "PM", "CROSS-SELLING": "CROSS-SELLING"}


def norm(w):
    return re.sub(r"[^a-z0-9$]", "", w.lower())


def load(take):
    m = json.loads((FMAP / f"{take}.json").read_text())
    words = [{"s": a / 1000, "e": b / 1000, "w": t} for a, b, t, _ in m["words"]]
    merged = []
    for w in words:   # whisper splits "50 -50", "p .m.", "cross -selling"
        if merged and (w["w"].startswith("-") or w["w"].startswith(".") or w["w"].startswith(",0")):
            merged[-1] = {**merged[-1], "w": merged[-1]["w"] + w["w"], "e": w["e"]}
        else:
            merged.append(w)
    sil = [(a / 1000, b / 1000) for a, b in m["silences"]]
    return merged, sil


TAKES = {t: load(t) for t in ("take1", "take2", "take3")}


def find(words, text, near):
    cands = [i for i, w in enumerate(words) if norm(w["w"]) == norm(text)]
    assert cands, f"word not found: {text}"
    return min(cands, key=lambda i: abs(words[i]["s"] - near))


def out_point(take, i, limit):
    """End a piece just inside the silence after word i (whisper ends words early)."""
    words, sil = TAKES[take]
    e = words[i]["e"]
    after = [a for a, b in sil if a >= e - 0.06]
    end = min(after[0] + 0.04, e + PAD_OUT_MAX) if after else e + 0.08
    return min(max(end, e + 0.03), limit)


def in_point(take, i, floor):
    words, sil = TAKES[take]
    s = words[i]["s"]
    before = [b for a, b in sil if b <= s + 0.06]
    start = max(before[-1] - 0.03, s - 0.15) if before else s - PAD_IN
    return max(min(start, s - 0.02), floor)


# 1. Build pieces: split at dead air > GAP_MAX, merge sub-MIN_PIECE pieces back, then add continuous punch splits.
pieces = []
for beat, take, w0, t0, w1, t1 in BEATS:
    words, _ = TAKES[take]
    a, b = find(words, w0, t0), find(words, w1, t1)
    assert a <= b, (beat, w0, w1)
    runs, run = [], [a]
    for i in range(a + 1, b + 1):
        if words[i]["s"] - words[i - 1]["e"] > GAP_MAX:
            runs.append([run[0], run[-1]])
            run = []
        run.append(i)
    runs.append([run[0], run[-1]])
    merged = []
    for r in runs:
        dur = words[r[1]]["e"] - words[r[0]]["s"]
        if merged and dur < MIN_PIECE:
            merged[-1][1] = r[1]          # keep the short pause instead of a sub-second jump
        elif merged and words[merged[-1][1]]["e"] - words[merged[-1][0]]["s"] < MIN_PIECE:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    punch_idx = {find(TAKES[t][0], w, n) for t, w, n in PUNCH_AT if t == take}
    for i0, i1 in merged:
        last = words[i0]["s"]
        for i in range(i0 + 1, i1 + 1):
            el, left = words[i]["s"] - last, words[i1]["e"] - words[i]["s"]
            gap = words[i]["s"] - words[i - 1]["e"]
            if left >= 1.4 and (el >= AUTO_PUNCH_S and gap >= 0.04 or el >= AUTO_PUNCH_S + 1.2):
                if not any(abs(words[j]["s"] - words[i]["s"]) < 1.4 for j in punch_idx):
                    punch_idx.add(i)
                last = words[i]["s"]
            if i in punch_idx:
                last = words[i]["s"]
        cuts = sorted(i for i in punch_idx if i0 < i <= i1)
        starts = [i0] + cuts
        ends = [c - 1 for c in cuts] + [i1]
        for k, (x0, x1) in enumerate(zip(starts, ends)):
            pieces.append({"beat": beat, "take": take, "i0": x0, "i1": x1, "cont_next": k < len(cuts)})

segs, prev = [], None
for k, pc in enumerate(pieces):
    take, i0, i1 = pc["take"], pc["i0"], pc["i1"]
    words, _ = TAKES[take]
    if prev and prev["cont_next"]:
        s = prev_end                      # continuous: start exactly where the last piece ended
    else:
        prev_e = words[i0 - 1]["e"] if i0 > 0 else 0.0
        s = IN_FIX.get((take, norm(words[i0]["w"])), None) or in_point(take, i0, prev_e + 0.02)
    if pc["cont_next"]:
        e = words[i1 + 1]["s"] - 0.03
    else:
        next_s = words[i1 + 1]["s"] if i1 + 1 < len(words) else words[i1]["e"] + 1
        e = out_point(take, i1, next_s - 0.04)
    n = max(1, round((e - s) * FPS))
    prev_end = round(s + n / FPS, 4)
    segs.append({"beat": pc["beat"], "take": take, "w0": i0, "w1": i1, "in": round(s, 3), "frames": n,
                 "zoom": 1.0 if k % 2 == 0 else ZOOMS[(k // 2) % 2], "cont": bool(prev and prev["cont_next"])})
    if (take, norm(words[i0]["w"])) in ZOOM_FIX:
        segs[-1]["zoom"] = ZOOM_FIX[(take, norm(words[i0]["w"]))]
        segs[-1]["fixed"] = True
    prev = pc
for k in range(1, len(segs)):   # no two neighbours at the same scale, even around a fixed one
    if segs[k]["zoom"] == segs[k - 1]["zoom"] and not segs[k].get("fixed"):
        segs[k]["zoom"] = 1.12 if segs[k - 1]["zoom"] == 1.0 else 1.0

t = 0.0
for sg in segs:
    sg["out_t"] = round(t, 4)
    t += sg["frames"] / FPS
SPEECH_END = t
TOTAL = t + HOLD_S


def src_to_out(sg, src_t):
    return sg["out_t"] + (src_t - sg["in"])


# Motion-graphic cutaways (full frame, voice runs on). Anchors are spoken words: (word, approx output s).
WORDS = []
for sg in segs:
    for w in TAKES[sg["take"]][0][sg["w0"]:sg["w1"] + 1]:
        WORDS.append({"w": w["w"], "t": round(src_to_out(sg, w["s"]), 3), "e": round(src_to_out(sg, w["e"]), 3),
                      "src": w["s"], "take": sg["take"], "beat": sg["beat"]})
PIVOT_LEN = sum(sg["frames"] for sg in segs if sg["beat"] == "PIVOT") / FPS
PIVOT_AT = next(sg["out_t"] for sg in segs if sg["beat"] == "PIVOT")


def w_src(take, word, src_near, end=False):
    """Anchor by take and source time (robust to re-cuts)."""
    c = [x for x in WORDS if x["take"] == take and norm(x["w"]) == norm(word)]
    assert c, f"word not found: {take} {word}"
    x = min(c, key=lambda x: abs(x["src"] - src_near))
    assert abs(x["src"] - src_near) < 1.0, (take, word, src_near, x["src"])
    return x["e" if end else "t"]


def wt(word, near, end=False):
    if near >= PIVOT_AT - 0.1:   # anchors below were written before the PIVOT line was inserted
        near += PIVOT_LEN
    c = [x for x in WORDS if norm(x["w"]) == norm(word)]
    assert c, f"word not found: {word}"
    x = min(c, key=lambda x: abs(x["t"] - near))
    assert abs(x["t"] - near) < 1.5, (word, near, x["t"])
    return x["e" if end else "t"]


LEAD = 0.25   # each clip is rendered this much before and after its window for the blur dissolve
GRAPHICS = [  # (scene, start, end, {cue: anchor})
    ("crm",      wt("There", 6.19) - 0.05, wt("Because", 13.47) - 0.08,
     {"c401": wt("401k", 9.21), "cira": wt("IRA", 9.93), "cstock": wt("old", 10.65), "csit": wt("that's", 12.55)}),
    ("call",     wt("The", 18.05) + 0.02, wt("can", 23.70) - 0.05,
     {"c1": wt("hey", 19.73), "c2": wt("I", 20.75), "c3": wt("I", 21.82)}),
    ("thennow",  wt("In", 35.22) - 0.05, wt("annuities", 42.48),
     {"cperson": wt("go", 36.40), "cpaper": wt("paper", 37.22), "cnow": wt("Now", 37.85), "cchanged": wt("insurance", 39.41),
      "cvirtual": wt("virtual", 40.55)}),
    ("machine",  wt("system", 46.43) - 0.3, wt("at,", 57.43, True) + 0.12,
     {"cyou": wt("agents", 47.19), "cset": wt("set", 49.17), "cfind": wt("find", 51.31), "cspec": wt("specialist", 55.43),
      "cor": wt("at,", 57.43, True) - 1.3, "clearn": wt("at,", 57.43, True) - 0.8}),
    ("split",    wt("it's", 60.91) - 0.1, wt("simple.", 66.02, True) + 0.12,
     {"cfree": wt("free.", 61.31), "cyou": wt("You", 62.07), "ccome": wt("come", 63.16), "cclose": wt("close", 64.02),
      "csplit": wt("50-50", 64.88), "csimple": wt("Pretty", 65.88)}),
    ("training", wt("simple.", 66.02, True) + 0.12, wt("call.", 71.70, True) + 0.15,
     {"clearn": wt("learn", 67.82), "cfree": wt("free.", 69.38), "cwed": wt("Wednesday", 69.68), "cpm": wt("1", 70.60)}),
    ("market",   wt("call.", 71.70, True) + 0.15, wt("and", 75.96) + 0.2, {}),
    ("cta",      wt("Now", 89.42) - 0.05, wt("Finally,", 91.62) - 0.06, {"cclick": wt("click", 90.88)}),
    ("endcard",  SPEECH_END + 0.05, TOTAL, {}),
]
G = []
for k, (scene, a, b, cues) in enumerate(GRAPHICS):
    t0 = a - LEAD
    G.append({"id": f"g{k + 1}_{scene}", "scene": scene, "start": round(a, 3), "end": round(b, 3),
              "dur": round(b + LEAD - t0, 3), "cues": {c: round(v - t0, 3) for c, v in cues.items()}})
for k, g in enumerate(G):   # back-to-back graphics hand over without showing the speaker in between
    g["from_aroll"] = k == 0 or g["start"] - G[k - 1]["end"] > 0.3
    g["to_aroll"] = g["scene"] != "endcard" and (k == len(G) - 1 or G[k + 1]["start"] - g["end"] > 0.3)
(OUT / "graphics.json").write_text(json.dumps(G, indent=1))


def in_graphic(x, pad=0.0):
    return any(g["start"] - pad <= x <= g["end"] + pad for g in G)


# B&W fear-of-missing-out beat on the speaker, with the documented proof on screen (sma-vsl-producer AUDIT.md)
FOMO = (wt("and", 75.96) + 0.25, wt("later.", 79.72, True) + 0.2, wt("missing", 76.82) - 0.05,
        ("20+ AGENTS.", "$3.8M PLACED IN 2025."))


# 2. Ledger files.
edl = {"version": "v7", "fps": FPS, "units": "ms", "total_ms": round(TOTAL * 1000),
       "rules": {"dead_air_cut_over_ms": int(GAP_MAX * 1000), "audio_fade_ms": 30, "punch_in": PUNCH},
       "segments": [{"beat": s["beat"], "take": s["take"], "in_ms": round(s["in"] * 1000),
                     "out_ms": round((s["in"] + s["frames"] / FPS) * 1000), "frames": s["frames"],
                     "zoom": s["zoom"], "output_at_ms": round(s["out_t"] * 1000)} for s in segs]}
(OUT / "edit_decision_list.json").write_text(json.dumps(edl, indent=1))

script, last = [], None
for sg in segs:
    words, _ = TAKES[sg["take"]]
    text = " ".join(w["w"] for w in words[sg["w0"]:sg["w1"] + 1])
    if sg["beat"] != last:
        script.append(f"\n[{sg['beat']} SECTION]")
        last = sg["beat"]
    script.append(text)
(OUT / "vsl_script_active.txt").write_text(
    "LOCKED v7 (cut from existing takes 2026-10-30, audited: .claude/skills/sma-vsl-producer/AUDIT.md)\n" + "\n".join(script).strip() + "\n")


# 3. Captions (word highlight), text slams, name tag, CTA.
def ts(x):
    x = math.floor(max(x, 0) * 100) / 100   # never land a frame late
    h, r = divmod(x, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


# ASS colours are BGR. Site palette (setmoreannuities.com): gold #C9A24A lifted to #D9B25A for video legibility, red #B5311F
YEL, WHT = "&H0066BEE0&", "&H00EEF6FA&"   # gold-hot #E0BE66, cream #FAF6EE
RED = "&H001F31B5&"
ev = []
slam_windows = []
for take, word, near, text, dur, sub in SLAMS:
    words, _ = TAKES[take]
    i = find(words, word, near)
    sg = next(s for s in segs if s["take"] == take and s["w0"] <= i <= s["w1"])
    a = src_to_out(sg, words[i]["s"]) - 0.05
    slam_windows.append((a, a + dur))
    ev.append(f"Dialogue: 8,{ts(a)},{ts(a + dur)},Dim,,0,0,0,,{{\\pos(0,0)\\fad(60,120)\\p1}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\\p0}}")
    ev.append(f"Dialogue: 9,{ts(a)},{ts(a + dur)},Slam,,0,0,0,,{{\\pos({W // 2},{H // 2})\\fad(0,120)"
              f"\\fscx130\\fscy130\\t(0,140,\\fscx100\\fscy100)}}{text}")
    if sub:
        ev.append(f"Dialogue: 9,{ts(a + 0.12)},{ts(a + dur)},SlamSub,,0,0,0,,{{\\pos({W // 2},{int(H * 0.63)})\\fad(120,120)}}{sub}")
    if text in SOURCES:
        ev.append(f"Dialogue: 9,{ts(a + 0.2)},{ts(a + dur)},Source,,0,0,0,,{{\\pos({W // 2},{int(H * 0.72)})\\fad(120,120)}}{SOURCES[text]}")


# cold open: one headline line above his head, no dim, captions run from frame one
OPEN = HEAD_END
ev.append(f"Dialogue: 6,{ts(0)},{ts(OPEN)},Head,,0,0,0,,{{\\pos({int(W * 0.80)},{int(H * 0.34)})\\fad(0,200)\\fscx106\\fscy106\\t(0,180,\\fscx100\\fscy100)}}{HEADLINE}")


FUNC = {"to", "of", "the", "a", "an", "is", "and", "or", "we", "i", "you", "that", "in", "for", "at", "on", "it", "by",
        "your", "my", "how", "do", "what", "if", "this", "be", "are", "so", "its", "im", "youre", "were", "theyre", "not", "with"}


def chunk_words(ws):
    """Caption chunks of 2 to 4 words: split at punctuation first, then at pauses, never starting or ending on a function word."""
    import itertools
    clauses, cur = [], []
    for w in ws:
        cur.append(w)
        if w["w"][-1:] in ".,?!":
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    merged = []
    for c in clauses:                      # a one-word clause ("hey,") joins its neighbour
        if merged and (len(c) < 2 or len(merged[-1]) < 2):
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    out = []
    for c in merged:
        n = len(c)
        if n <= 4:
            out.append(c)
            continue
        k = max(1, math.ceil(n / 4.5))
        best = None
        while best is None:
            for cuts in itertools.combinations(range(1, n), k - 1):
                sizes = [b - a for a, b in zip((0,) + cuts, cuts + (n,))]
                if max(sizes) > 5 or min(sizes) < 2:
                    continue
                score = -0.5 * (max(sizes) - min(sizes)) - 1.0 * sum(1 for z in sizes if z == 5)
                for cpos in cuts:
                    if norm(c[cpos]["w"]) in FUNC: score -= 2
                    if norm(c[cpos - 1]["w"]) in FUNC: score -= 2
                    if c[cpos]["s"] - c[cpos - 1]["e"] > 0.15: score += 2
                if best is None or score > best[0]:
                    best = (score, cuts)
            if best is None:
                k += 1
                if k > n:
                    best = (0, tuple(range(4, n, 4)))
        cuts = best[1]
        out += [c[a:b] for a, b in zip((0,) + cuts, cuts + (n,))]
    final = []                             # no chunk shorter than 0.3 s on screen
    for c in out:
        if final and (c[-1]["e"] - c[0]["s"]) < 0.3 and len(final[-1]) + len(c) <= 5:
            final[-1] = final[-1] + c
        else:
            final.append(c)
    return final


def in_slam(x):
    return any(a - 0.02 <= x <= b for a, b in slam_windows)


close = next(sg for sg in segs if sg["beat"] == "CLOSE")
cta_seg = next(sg for sg in segs if sg["beat"] == "CTA" and any(norm(w["w"]) == "click" for w in TAKES[sg["take"]][0][sg["w0"]:sg["w1"] + 1]))
cta_word = next(w for w in TAKES[cta_seg["take"]][0][cta_seg["w0"]:cta_seg["w1"] + 1] if norm(w["w"]) == "click")
CTA_AT = max(src_to_out(cta_seg, cta_word["s"]) - 0.1, G[-1]["end"])

for sg in segs:
    words, _ = TAKES[sg["take"]]
    seg_end = sg["out_t"] + sg["frames"] / FPS
    ws = [w for w in words[sg["w0"]:sg["w1"] + 1] if not (sg["take"] == "take2" and norm(w["w"]) == "i" and 22.5 < w["s"] < 23.3)]
    chunks = chunk_words(ws)
    for c in chunks:
        labels = []
        for w in c:
            txt = w["w"].upper().strip(",.?!")
            labels.append(DISPLAY.get(txt, txt))
        for k, w in enumerate(c):
            a = src_to_out(sg, w["s"])
            b = src_to_out(sg, c[k + 1]["s"]) if k + 1 < len(c) else min(src_to_out(sg, w["e"]) + 0.25, seg_end)
            nxt_chunk = chunks[chunks.index(c) + 1] if chunks.index(c) + 1 < len(chunks) else None
            if k + 1 == len(c) and nxt_chunk:
                b = src_to_out(sg, nxt_chunk[0]["s"])
            b = min(b, seg_end)
            b = min(b, SPEECH_END + 0.15)
            if a < HEAD_END:
                continue
            if b - a < 0.02:
                continue
            parts = []
            for m, lab in enumerate(labels):
                col = YEL if m == k else WHT
                parts.append(f"{{\\1c{col}}}{lab}")
            pop = "\\fscx92\\fscy92\\t(0,70,\\fscx100\\fscy100)" if k == 0 else ""
            ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Cap,,0,0,0,,{{{pop}}}{' '.join(parts)}")

# name tag after the open: lower left on a dark plate so the proof line reads on a phone
# proof card: lower left from 0.4 s, held until the first cutaway (eyebrow, numeral, line, on a dark plate)
a = 0.4
b = G[0]["start"] - 0.3
px, py, pw, ph = int(48 * SX), int(556 * SX), int(600 * SX), int(248 * SX)
ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Plate,,0,0,0,,{{\\pos({px},{py})\\alpha&H2E&\\fad(90,250)\\p1}}m 0 0 l {pw} 0 {pw} {ph} 0 {ph}{{\\p0}}")
ev.append(f"Dialogue: 3,{ts(a + 0.05)},{ts(b)},TagEye,,0,0,0,,{{\\pos({int(74 * SX)},{int(582 * SX)})\\fad(90,250)}}CHASE GALLAGHER  \u00b7  FOUNDER")
ev.append(f"Dialogue: 3,{ts(a + 0.12)},{ts(b)},TagNum,,0,0,0,,{{\\pos({int(66 * SX)},{int(612 * SX)})\\fad(90,250)\\fscx92\\fscy92\\t(0,220,\\fscx100\\fscy100)}}$3.8M")
ev.append(f"Dialogue: 3,{ts(a + 0.22)},{ts(b)},TagSub,,0,0,0,,{{\\pos({int(74 * SX)},{int(756 * SX)})\\fad(90,250)}}PLACED IN 2025  \u00b7  20+ AGENTS")


# CTA lands on "click below", sits low over the chest (never the face), and holds through the end card
if False:
  ev.append(f"Dialogue: 7,{ts(CTA_AT)},{ts(TOTAL)},Dim,,0,0,0,,{{\\pos(0,0)\\alpha&H9A&\\fad(200,0)\\p1}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\\p0}}")
  ev.append(f"Dialogue: 7,{ts(SPEECH_END)},{ts(TOTAL)},Dim,,0,0,0,,{{\\pos(0,0)\\alpha&H60&\\fad(300,0)\\p1}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\\p0}}")
  ev.append(f"Dialogue: 9,{ts(CTA_AT)},{ts(TOTAL)},CTA,,0,0,0,,{{\\pos({W // 2},{int(H * 0.80)})\\fad(150,0)\\fscx90\\fscy90\\t(0,180,\\fscx100\\fscy100)}}{CTA_TEXT}")
  ev.append(f"Dialogue: 9,{ts(CTA_AT + 0.3)},{ts(TOTAL)},Arrow,,0,0,0,,{{\\fad(150,0)\\move({W // 2},{int(H * 0.89)},{W // 2},{int(H * 0.93)},0,700)}}\u2193")


# Beat-change flash (pairs with the zoom kick in the render) and side callouts over the sky.
beat_starts = [sg["out_t"] for k, sg in enumerate(segs) if k > 0 and sg["beat"] != segs[k - 1]["beat"]]
# (no flash on section changes: the zoom kick and the whoosh carry it)


def out_time(take, word, near, end=False):
    words, _ = TAKES[take]
    i = find(words, word, near)
    sg = next(s for s in segs if s["take"] == take and s["w0"] <= i <= s["w1"])
    return src_to_out(sg, words[i]["e" if end else "s"])


callout_times = []
# (take, word, source s, text, hold s, row). Slide in from the right over the sky, red box, cream text.
CHIPS = [
    ("take1", "exposed",   47.38, "EXPOSED TO THE MARKET", 2.0, 0),
    ("take3", "existing",  27.52, "YOUR EXISTING BOOK",    2.0, 0),
    ("take2", "12",        84.76, "THE NEXT 12 MONTHS",    2.0, 0),
    ("take2", "time",      89.28, "TIME",                  3.4, 0),
    ("take2", "studying",  90.50, "STUDY",                 2.2, 1),
    ("take2", "training.", 91.20, "TRAIN",                 1.5, 2),
    ("take3", "agents.",   67.60, "FOR THE AGENTS",        1.3, 0),
]
CX2, CY2, CDY2 = int(W * 0.69), int(H * 0.40), int(H * 0.095)
for take, word, src, text, hold, row in CHIPS:
    a = w_src(take, word, src) - 0.04
    b = a + hold
    for g in G:   # never under a cutaway
        if a < g["start"] - LEAD and b > g["start"] - LEAD:
            b = g["start"] - LEAD - 0.05
    if in_graphic(a, 0.1) or b - a < 0.9:
        continue
    y = CY2 + row * CDY2
    ev.append(f"Dialogue: 5,{ts(a)},{ts(b)},Chip,,0,0,0,,{{\\move({CX2 + int(70 * SX)},{y},{CX2},{y},0,170)\\fad(120,200)}}{text}")
    callout_times.append(a)
fa, fb, ft, (l1, l2) = FOMO
ev.append(f"Dialogue: 6,{ts(ft)},{ts(fb)},Fomo,,0,0,0,,{{\\pos({int(W * 0.24)},{int(H * 0.40)})\\fad(120,180)\\fscx112\\fscy112\\t(0,160,\\fscx100\\fscy100)}}{l1}")
ev.append(f"Dialogue: 6,{ts(ft + 0.35)},{ts(fb)},Fomo2,,0,0,0,,{{\\pos({int(W * 0.24)},{int(H * 0.50)})\\fad(120,180)}}{l2}")
CX, CY0, CDY = int(W * 0.69), int(H * 0.27), int(H * 0.105)
for items, end, strike in CALLOUTS:
    starts = [out_time(t, w, n) - 0.04 for t, w, n, _ in items]
    starts = [max(x, starts[k - 1] + 0.15) if k else x for k, x in enumerate(starts)]
    g_end = out_time(*end) - 0.05 if end else starts[-1] + 2.4
    for a, b in slam_windows:            # never sit under a full-frame slam
        if starts[0] < a < g_end:
            g_end = a - 0.02
    g_end = min(g_end, CTA_AT)
    for k, ((_, _, _, text), a) in enumerate(zip(items, starts)):
        if a >= g_end:
            continue
        y = CY0 + k * CDY
        mv = f"\\move({CX + int(70 * SX)},{y},{CX},{y},0,170)"
        last = k == len(items) - 1
        if strike and not last:
            ev.append(f"Dialogue: 5,{ts(a)},{ts(starts[-1])},Call,,0,0,0,,{{{mv}\\fad(110,0)}}{text}")
            ev.append(f"Dialogue: 5,{ts(starts[-1])},{ts(g_end)},Call,,0,0,0,,{{\\pos({CX},{y})\\1c&H00B0B0B0&\\alpha&H50&\\fad(0,150)}}{text}")
        else:
            ev.append(f"Dialogue: 5,{ts(a)},{ts(g_end)},Call,,0,0,0,,{{{mv}\\fad(110,150)}}{text}")
        callout_times.append(a)

head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat Black,{int(96 * SX)},&H00EEF6FA,&H00EEF6FA,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,{max(2, int(4 * SX))},{max(1, int(2 * SX))},2,60,60,{int(150 * SX)},1
Style: Slam,Montserrat Black,{int(190 * SX)},&H0066BEE0,&H0066BEE0,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,{max(2, int(6 * SX))},0,5,0,0,0,1
Style: SlamSub,Montserrat ExtraBold,{int(70 * SX)},&H00EEF6FA,&H00EEF6FA,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,{max(1, int(3 * SX))},0,5,0,0,0,1
Style: Source,Montserrat ExtraBold,{int(46 * SX)},&H00B4B4B4,&H00B4B4B4,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,{max(1, int(2 * SX))},0,5,0,0,0,1
Style: Head,Montserrat Black,{int(84 * SX)},&H001F31B5,&H001F31B5,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,{max(2, int(4 * SX))},{max(1, int(2 * SX))},5,0,0,0,1
Style: HeadSub,Montserrat Black,{int(60 * SX)},&H00EEF6FA,&H00EEF6FA,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,{max(2, int(5 * SX))},{max(1, int(2 * SX))},5,0,0,0,1
Style: Dim,Montserrat,10,&H6E000000,&H6E000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Plate,Montserrat,10,&H0014110E,&H0014110E,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: TagEye,Montserrat ExtraBold,{int(26 * SX)},&H00DDEAF1,&H00DDEAF1,&H00000000,&H00000000,0,0,0,0,100,100,{max(2, int(5 * SX))},0,1,0,0,7,0,0,0,1
Style: TagNum,Montserrat Black,{int(116 * SX)},&H0066BEE0,&H0066BEE0,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Tag,Montserrat ExtraBold,{int(40 * SX)},&H00EEF6FA,&H00EEF6FA,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,{max(1, int(3 * SX))},{max(1, int(2 * SX))},7,0,0,0,1
Style: TagBig,Montserrat Black,{int(86 * SX)},&H0066BEE0,&H0066BEE0,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,{max(1, int(3 * SX))},{max(1, int(2 * SX))},7,0,0,0,1
Style: TagSub,Montserrat ExtraBold,{int(34 * SX)},&H00EEF6FA,&H00EEF6FA,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1
Style: CTA,Montserrat Black,{int(88 * SX)},&H00EEF6FA,&H00EEF6FA,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,{max(2, int(5 * SX))},0,5,0,0,0,1
Style: Call,Montserrat Black,{int(80 * SX)},&H0066BEE0,&H0066BEE0,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,{max(2, int(6 * SX))},{max(1, int(4 * SX))},4,0,0,0,1
Style: Fomo,Montserrat Black,{int(100 * SX)},&H001F31B5,&H001F31B5,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,{max(2, int(4 * SX))},{max(1, int(2 * SX))},5,0,0,0,1
Style: Fomo2,Montserrat Black,{int(52 * SX)},&H00EEF6FA,&H00EEF6FA,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,{max(2, int(4 * SX))},{max(1, int(2 * SX))},5,0,0,0,1
Style: Chip,Montserrat Black,{int(58 * SX)},&H00EEF6FA,&H00EEF6FA,&H001F31B5,&H00000000,0,0,0,0,100,100,1,0,3,{max(3, int(16 * SX))},0,7,0,0,0,1
Style: Flash,Montserrat,10,&H00EEF6FA,&H00EEF6FA,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Arrow,DejaVu Sans,{int(120 * SX)},&H001F31B5,&H001F31B5,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,{max(2, int(4 * SX))},0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
(OUT / "captions.ass").write_text(head + "\n".join(ev) + "\n")

# 4. Sound design: whoosh on every beat change, bass hit + shake on every slam, tick on callouts, riser into the CTA.
sfx = [("whoosh-short", b - 0.12, 0.26) for b in beat_starts if not in_graphic(b, 0.3)]
sfx += [("whoosh-short", g["start"] - 0.3, 0.30) for g in G]
sfx += [("whoosh-short", g["end"] - 0.05, 0.20) for g in G if g["to_aroll"]]
sfx += [("click-soft", g["start"] - LEAD + v, 0.15) for g in G for v in g["cues"].values()]
sfx += [("hit", G[[g["scene"] for g in G].index("market")]["start"] + 0.1, 0.30)]
sfx += [("hit", G[-1]["start"] - 0.2, 0.22)]
sfx += [("click-soft", a, 0.22) for a in callout_times]
CTA_G = G[[g["scene"] for g in G].index("cta")]
sfx += [("pop", CTA_G["start"] - LEAD + CTA_G["cues"]["cclick"], 0.18)]
sfx += [("impact-bass-1", a + 0.02, 0.40) for a, _ in slam_windows]
RISER_S = 1.6
sfx += [("riser", CTA_G["start"] - 0.05 - RISER_S, 0.22)]


def write_riser(path, dur=RISER_S, sr=48000):
    """Filtered-noise sweep 300 Hz -> 7 kHz with an exponential swell, cut dead on the CTA."""
    import numpy as np
    import wave
    n = int(dur * sr)
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n)
    t = np.arange(n) / sr
    fc = 300 * (7000 / 300) ** (t / dur)
    y, lp, bp = np.zeros(n), 0.0, 0.0
    for k in range(n):                           # state-variable band-pass with a moving centre
        f = 2 * math.sin(math.pi * fc[k] / sr)
        hp = x[k] - lp - 0.5 * bp
        bp += f * hp
        lp += f * bp
        y[k] = bp
    y *= (t / dur) ** 2.2
    y /= np.abs(y).max() + 1e-9
    y[-int(0.004 * sr):] *= np.linspace(1, 0, int(0.004 * sr))
    pcm = (np.stack([y, y], 1) * 0.9 * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(sr), w.writeframes(pcm.tobytes())


def write_hit(path, sr=48000):
    """Transient hit: pitched sub thump 140 -> 45 Hz (0.35 s decay) plus a 3 kHz crack (25 ms). Peak -1 dBFS."""
    import numpy as np
    import wave
    n = int(0.8 * sr)
    t = np.arange(n) / sr
    f = 45 + 95 * np.exp(-t / 0.06)
    body = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t / 0.22)
    rng = np.random.default_rng(3)
    crack = np.diff(rng.standard_normal(n + 1)) * np.exp(-t / 0.012) * 0.5
    y = body + crack
    y[: int(0.002 * sr)] *= np.linspace(0, 1, int(0.002 * sr))
    y /= np.abs(y).max()
    pcm = (np.stack([y, y], 1) * 0.89 * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(sr), w.writeframes(pcm.tobytes())


(OUT / "sfx").mkdir(exist_ok=True)
write_riser(OUT / "sfx" / "riser.wav")
write_hit(OUT / "sfx" / "hit.wav")

LUT_DIR = Path(__file__).resolve().parent / "luts"
LUT = LUT_DIR / "sma_pro.cube"          # see luts/README.md
FILL = LUT_DIR / "fill_face.png"
POST = "unsharp=lx=13:ly=13:la=0.30,unsharp=5:5:0.45,vignette=a=0.35"


# Hand labels: SELL on the hand he raises on "sell" (viewer left), SET on the one he raises on "set" (viewer right).
# Positions come from the tracker file (normalised raw-frame coords); burned into the segment before the push, so they ride it.
HANDS = {"take": "take3", "file": Path(__file__).resolve().parent / "hands_take3.json", "t0": 33.9, "t1": 36.6,
         "labels": {"L": ("SELL", 34.55), "R": ("SET", 35.33)}}
hand_rows = json.loads(HANDS["file"].read_text()) if HANDS["file"].exists() else []


def hand_ass(sg, path):
    if sg["take"] != HANDS["take"] or not hand_rows:
        return False
    s0, s1 = sg["in"], sg["in"] + sg["frames"] / FPS
    if s1 < HANDS["t0"] or s0 > HANDS["t1"]:
        return False
    z = sg["zoom"]; ky = 0.33
    ev_h, last, born, gone, peak = [], {}, {}, {}, {}
    for i in range(sg["frames"]):
        st = s0 + i / FPS
        row = min(hand_rows, key=lambda r: abs(r["t"] - st))
        seen = {h["side"]: h for h in row["hands"] if h.get("px", 9999) >= 2500} if abs(row["t"] - st) < 0.05 else {}
        for side, (text, t_on) in HANDS["labels"].items():
            if st < t_on:
                continue
            h = seen.get(side)
            if h:
                gone[side] = 0
            else:
                gone[side] = gone.get(side, 0) + 1
                if gone[side] > 4:      # the hand left: drop the label
                    continue
            if h:
                x = (h["cx"] - (1 - 1 / z) / 2) * z * W
                y = (h["top"] - (1 - 1 / z) * ky) * z * H - 40 * SX
                peak[side] = min(peak.get(side, y), y)
                if y > peak[side] + 0.10 * H:      # the hand is coming down: the label stays, then leaves
                    gone[side] = gone.get(side, 0) + 2
                    if gone[side] > 4:
                        continue
                    x, y = last.get(side, (x, y))
                elif side in last:
                    lx, ly = last[side]
                    x, y = lx + max(-24, min(24, 0.25 * (x - lx))), ly + max(-24, min(24, 0.25 * (y - ly)))
                last[side] = (x, y)
            if side not in last:
                continue
            x, y = last[side]
            born.setdefault(side, i)
            k = min(1.0, (i - born[side]) / 7)
            sc = int(100 * (0.55 + 0.45 * (1 - (1 - k) ** 3)))
            ev_h.append(f"Dialogue: 1,{ts(i / FPS)},{ts((i + 1) / FPS)},Hand,,0,0,0,,{{\\pos({x:.0f},{y:.0f})\\fscx{sc}\\fscy{sc}}}{text}")
    if not ev_h:
        return False
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hand,Montserrat Black,{int(84 * SX)},&H00EEF6FA,&H00EEF6FA,&H001F31B5,&H00000000,0,0,0,0,100,100,2,0,3,{max(4, int(22 * SX))},0,2,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    path.write_text(hdr + "\n".join(ev_h) + "\n")
    return True


# 5. Per-segment video filters: slow push (102% -> 105%), zoom kick on beat changes, decaying shake on slams.
seg_vf = []
for k, sg in enumerate(segs):
    D = sg["frames"] / FPS
    kick = k > 0 and sg["beat"] != segs[k - 1]["beat"] and not in_graphic(sg["out_t"], 0.6)
    kexpr = f"(1.02+0.03*t/{D:.3f}" + (f"+0.10*pow(max(0\\,1-t/{KICK_S})\\,2)" if kick else "") + ")"
    sx, sy = [], []
    for a, _ in slam_windows:
        lt = a - sg["out_t"]
        if -0.01 <= lt < D:
            env = f"between(t\\,{lt:.3f}\\,{lt + 0.4:.3f})*exp(-(t-{lt:.3f})/0.12)"
            sx.append(f"{SHAKE[0] * SX:.1f}*{env}*sin(2*PI*17*(t-{lt:.3f}))")
            sy.append(f"{SHAKE[1] * SX:.1f}*{env}*cos(2*PI*13*(t-{lt:.3f}))")
    ky = 0.33
    hp = OUT / f"hands_{k:03d}.ass"
    hands_vf = f"scale={W}:{H}:flags=lanczos,ass={hp}," if hand_ass(sg, hp) else ""
    vf = (f"scale=2560:1440:flags=lanczos,crop=iw/{sg['zoom']}:ih/{sg['zoom']}:(iw-iw/{sg['zoom']})/2:(ih-ih/{sg['zoom']})*{ky},"
          f"setpts=PTS-STARTPTS,lut3d=file={LUT},{hands_vf}scale=w='trunc({W}*{kexpr}/2)*2':h=-2:eval=frame:flags=bicubic,"
          f"crop={W}:{H}:x='(iw-{W})/2{''.join('+' + e for e in sx)}':y='(ih-{H})*0.4{''.join('+' + e for e in sy)}'")
    seg_vf.append(vf)

crf, preset = ("26", "veryfast") if PREVIEW else ("17", "medium")
# Voice chain v3 (owner: v1 "too enhanced", v2 "still a little cloudy"). Measured on take2 (1/3-octave LTAS of the loud
# frames, relative to 1 kHz): the XTRA Muse built-in mics put an 8-13 dB hump at 315-630 Hz (the cloud), a +7 dB bump
# at 2 kHz (the "cheap mic" edge), and the balcony rumble sits at 120-300 Hz, right on his 116 Hz fundamental. So:
#  - the band under 300 Hz is split off (Linkwitz-Riley) and soft-gated between words, open while he speaks
#    (noise 24.7 dB under speech vs 16.4 without the gate; fundamentals kept, 125 Hz band unchanged)
#  - -7 dB at 500 Hz, -4 dB at 2.2 kHz, -1.5 dB at 3.5 kHz; light FFT denoise; -3 dB notch at 6.8 kHz for the S sounds
#    (ffmpeg's deesser measured no effect); +1.5 dB air above 9 kHz; 2:1 at 20 ms. The graph has two branches, so the
#    run-wav command uses -filter_complex.
VOICE = ("highpass=f=100:poles=2,acrossover=split=300:order=4th[lo][hi];"
         "[lo]agate=threshold=0.03:ratio=3:attack=8:release=250:knee=4:detection=rms[lg];"
         "[lg][hi]amix=inputs=2:normalize=0,"
         "equalizer=f=210:t=q:w=1.0:g=-2,equalizer=f=500:t=q:w=1.0:g=-7,equalizer=f=2200:t=q:w=1.0:g=-4,"
         "equalizer=f=3500:t=q:w=1.5:g=-1.5,afftdn=nr=6:nf=-42,atrim=start=0.025,asetpts=PTS-STARTPTS,"
         "equalizer=f=6800:t=q:w=2.5:g=-3,highshelf=f=9000:g=1.5:width_type=q:w=0.7,"
         "acompressor=threshold=-22dB:ratio=2:attack=20:release=250:makeup=2,aresample=48000")
NAME = f"SMA_VSL_v7{'_preview' if PREVIEW else ''}.mp4"
cmd_dir = OUT / "cmds"
cmd_dir.mkdir(exist_ok=True)
runs = []
for k, sg in enumerate(segs):
    if sg["cont"]:
        runs[-1].append(k)
    else:
        runs.append([k])
run_of = {r[0]: (j, r) for j, r in enumerate(runs)}
for k, (sg, vf) in enumerate(zip(segs, seg_vf)):
    aud = ""
    if k in run_of:
        j, r = run_of[k]
        d = sum(segs[i]["frames"] for i in r) / FPS
        fo = 0.30 if r[-1] == len(segs) - 1 else 0.03
        aud = (f'[ -f "$SEG/r{j:03d}.wav" ] || ffmpeg -v error -y -ss {sg["in"]:.3f} -t {d + 0.1:.6f} -i "$RAW/{sg["take"]}.mp4" '
               f'-filter_complex "[0:a:0]{VOICE},afade=t=in:st=0:d=0.03,afade=t=out:st={d - fo:.6f}:d={fo},apad,atrim=0:{d:.6f}[a]" -map "[a]" -ac 2 -ar 48000 -c:a pcm_s16le "$SEG/r{j:03d}.wav"')
    (cmd_dir / f"{k:03d}.sh").write_text("\n".join([
        "set -e", f'RAW="{RAW}"; SEG="{OUT}/segs"',
        f'[ -f "$SEG/{k:03d}.mp4" ] || ffmpeg -v error -y -ss {sg["in"]:.3f} -i "$RAW/{sg["take"]}.mp4" -an -frames:v {sg["frames"]} '
        f'-filter_complex "[0:v]{vf}[g];movie={FILL}[f];[g][f]overlay=format=auto:eof_action=repeat,{POST},setsar=1,fps=30,format=yuv420p[v]" '
        f'-map "[v]" -c:v libx264 -preset {preset} -crf {crf} -threads 2 "$SEG/{k:03d}.mp4"',
        aud, ""]))

# music envelope: 0.8 s fade-in, a dip into silence before the big number, full under the end card, 0.9 s fade-out
drop_a = G[[g["scene"] for g in G].index("market")]["start"]
env = (f"if(lt(t\\,0.8)\\,t/0.8\\,1)"
       f"*if(gt(t\\,{SPEECH_END:.3f})\\,max(0.4\\,1-(t-{SPEECH_END:.3f})/0.5)\\,1)"
       f"*if(gt(t\\,{TOTAL - 1.5:.3f})\\,max(0\\,({TOTAL:.3f}-t)/1.5)\\,1)")
MG_DIR = Path(__file__).resolve().parent.parent / "mg"
blur_on = []   # (t0, t1, level) windows where the speaker is softened under a dissolve
for g in G:
    if g["from_aroll"]:
        blur_on += [(g["start"] - 0.26, g["start"] - 0.13, 1), (g["start"] - 0.13, g["start"] + 0.04, 2)]
    if g["to_aroll"]:
        blur_on += [(g["end"] - 0.04, g["end"] + 0.10, 2), (g["end"] + 0.10, g["end"] + 0.22, 1)]
en = lambda lv: "+".join(f"between(t\\,{a:.3f}\\,{b:.3f})" for a, b, l in blur_on if l == lv)
parts = [f"[0:v]hue=s=0.25:enable='between(t\\,{FOMO[0]:.3f}\\,{FOMO[1]:.3f})',eq=contrast=1.10:brightness=-0.03:enable='between(t\\,{FOMO[0]:.3f}\\,{FOMO[1]:.3f})',split=3[v0][vb1][vb2]",
         "[vb1]gblur=sigma=6[b1]", "[vb2]gblur=sigma=14[b2]",
         f"[v0][b1]overlay=enable='{en(1)}'[x1]", f"[x1][b2]overlay=enable='{en(2)}'[x2]"]
cur = "x2"
for k, g in enumerate(G):
    a0, d = g["start"] - LEAD, g["dur"]
    f = f"[{k + 1}:v]scale={W}:{H}:flags=lanczos,format=yuva420p,fade=t=in:st=0:d={(LEAD - 0.03) if g['from_aroll'] else 0.08:.2f}:alpha=1"
    if g["to_aroll"]:
        f += f",fade=t=out:st={d - LEAD - 0.05:.3f}:d={LEAD + 0.05:.2f}:alpha=1"
    parts.append(f + f",setpts=PTS-STARTPTS+{a0:.3f}/TB[g{k}]")
    parts.append(f"[{cur}][g{k}]overlay=eof_action=pass:enable='between(t\\,{a0:.3f}\\,{a0 + d:.3f})'[y{k}]")
    cur = f"y{k}"
parts.append(f"[{cur}]null[vout]")
COMP = ";".join(parts)
lines = ["#!/usr/bin/env bash",
         "# SMA VSL v6: generated by v6_build.py. Frame-exact segments (video copy-joined, PCM audio encoded once),",
         "# slow push + punch-ins every ~2.5 s, zoom kick + flash on beat changes, slam shake, side callouts,",
         "# ducked music bed (Kevin MacLeod, CC BY 4.0), captions burned last, -14 LUFS.",
         "set -euo pipefail",
         f'RAW="{RAW}"', f'OUT="{OUT}"', 'SEG="$OUT/segs"', 'SFX="$OUT/sfx"', 'mkdir -p "$SEG"',
         'JOBS="${JOBS:-$(nproc)}"',
         'ls "$OUT"/cmds/*.sh | xargs -P "$JOBS" -n 1 bash',
         f'# clean end-card hold: the last frame, still, for {HOLD_S}s with silence (CTA burns over it)',
         'LAST=$(ls "$SEG"/[0-9]*.mp4 | sort | tail -1)',
         '[ -f "$SEG/zzz_hold.mp4" ] || { ffmpeg -v error -y -sseof -0.1 -i "$LAST" -frames:v 1 "$SEG/hold.png" && \\',
         f'  ffmpeg -v error -y -loop 1 -framerate 30 -i "$SEG/hold.png" -frames:v {round(HOLD_S * FPS)} -vf "format=yuv420p" -c:v libx264 -preset {preset} -crf {crf} -r 30 "$SEG/zzz_hold.mp4"; }}',
         f'[ -f "$SEG/r999_hold.wav" ] || ffmpeg -v error -y -f lavfi -i anullsrc=r=48000:cl=stereo -t {round(HOLD_S * FPS) / FPS:.6f} -c:a pcm_s16le "$SEG/r999_hold.wav"',
         'ls "$SEG"/*.mp4 | sort | sed "s#^#file \'#; s#\\$#\'#" > "$OUT/v.txt"',
         'ls "$SEG"/r*.wav | sort | sed "s#^#file \'#; s#\\$#\'#" > "$OUT/a.txt"',
         'ffmpeg -v error -y -f concat -safe 0 -i "$OUT/v.txt" -f concat -safe 0 -i "$OUT/a.txt" -map 0:v -map 1:a -c copy "$OUT/base.mkv"',
         "# motion graphics: rendered frame by frame in headless Chromium from vsl/mg/scenes.html",
         f'node "{MG_DIR}/render.js" "$OUT/graphics.json" "$OUT/mg"',
         f'ffmpeg -v error -y -i "$OUT/base.mkv" {" ".join(f'-i "$OUT/mg/{g["id"]}.mp4"' for g in G)} -filter_complex "{COMP}" -map "[vout]" -an \\',
         f'  -c:v libx264 -preset {preset} -crf {"16" if not PREVIEW else "24"} -pix_fmt yuv420p "$OUT/comp.mkv"',
         "# music bed: cut to length, voice-band notch so the words sit on top, pre-levelled to -23 LUFS",
         f'ffmpeg -v error -y -ss {MUSIC[1]} -i "$SFX/{MUSIC[0]}" -t {TOTAL + 0.5:.3f} -af "highpass=f=40,equalizer=f=2600:t=q:w=0.9:g=-5,equalizer=f=1000:t=q:w=1.2:g=-2,'
         f'acompressor=threshold=-26dB:ratio=3:attack=200:release=1200,loudnorm=I=-24:TP=-4:LRA=7,aresample=48000" -ac 2 -c:a pcm_s16le "$OUT/bed.wav"', ""]
inputs, chains, labels = ['-i "$OUT/base.mkv"', '-i "$OUT/bed.wav"'], [], []
for j, (name, at, gain) in enumerate(sfx):
    ext = "wav" if name in ("riser", "hit") else "mp3"
    inputs.append(f'-i "$SFX/{name}.{ext}"')
    ms = max(0, int(at * 1000))
    chains.append(f"[{j + 2}:a]volume={gain},adelay={ms}|{ms},aresample=48000[s{j}]")
    labels.append(f"[s{j}]")
# No limiter on the voice stem: ffmpeg's alimiter also pulls the RMS down (measured -1.9 dB at limit 0.3), the fixed
# gain then rises and the peaks return. The one safety limiter at the end trims consonant peaks by 1-3 dB (60 ms release).
mix = ("[0:a]asplit=2[vo][key];"
       f"[1:a]volume='{env}':eval=frame[bedv];"
       "[bedv][key]sidechaincompress=threshold=0.03:ratio=3:attack=60:release=1500:makeup=1[bed];"
       + ";".join(chains) + ";" +
       f"[vo][bed]{''.join(labels)}amix=inputs={len(sfx) + 2}:normalize=0:duration=first[mix]")
lines += ["# Mix voice + ducked bed + SFX to PCM, measure, then one fixed gain to -15 LUFS and a safety limiter.",
          f'ffmpeg -v error -y {" ".join(inputs)} -filter_complex "{mix}" -map "[mix]" -c:a pcm_s16le "$OUT/mix.wav"',
          'M=$(ffmpeg -hide_banner -i "$OUT/mix.wav" -af loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n "/^{/,/^}/p")',
          'g(){ echo "$M" | sed -n "s/.*\\"$1\\" : \\"\\([^\\"]*\\)\\".*/\\1/p"; }',
          '# one fixed gain to -15 LUFS, then a true-peak safety limiter at -1.5 dBFS (nothing rides the voice)',
          'LN="volume=$(awk -v i="$(g input_i)" "BEGIN{printf \\"%.2f\\", -15-i}")dB,alimiter=limit=0.81:attack=5:release=60:level=false"',
          'ffmpeg -v error -y -i "$OUT/comp.mkv" -i "$OUT/mix.wav" -map 0:v -map 1:a -vf "ass=$OUT/captions.ass" -af "$LN,aresample=48000" \\',
          f'  -c:v libx264 -preset {preset} -crf {"15" if not PREVIEW else crf} -maxrate 14M -bufsize 28M -threads 0 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \\',
          f'  -c:a aac -b:a 192k -movflags +faststart -t {TOTAL:.4f} "$OUT/{NAME}"',
          f'echo "done: $OUT/{NAME} ({TOTAL:.2f}s)"']
(OUT / "render_vsl.sh").write_text("\n".join(lines) + "\n")
(OUT / "render_vsl.sh").chmod(0o755)
print(f"{len(segs)} pieces from {len(BEATS)} beats, {len(beat_starts)} kicks, {len(callout_times)} callouts, {len(sfx)} sfx, total {TOTAL:.2f}s")

# 6. Word timeline in output seconds (for motion-graphic cues).
wl = []
for sg in segs:
    for w in TAKES[sg["take"]][0][sg["w0"]:sg["w1"] + 1]:
        wl.append({"w": w["w"], "t": round(src_to_out(sg, w["s"]), 3), "e": round(src_to_out(sg, w["e"]), 3), "take": sg["take"], "beat": sg["beat"]})
(OUT / "words_out.json").write_text(json.dumps(wl))
