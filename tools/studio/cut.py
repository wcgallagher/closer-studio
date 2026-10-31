"""The cut: pieces from words and silences, punch-in pattern, emphasis kicks, filler removal, beat map."""
from __future__ import annotations

from .common import FPS

GAP_MAX = 0.35        # dead air longer than this is removed
PAD_IN, PAD_OUT = 0.05, 0.15
MIN_PIECE = 1.0
PUNCH_EVERY = 2.6     # seconds between framing changes inside one breath
ZOOMS = (1.0, 1.10, 1.0, 1.20)


def build(words, sil, keep_silence=False, fillers="keep", punch=True, zooms=ZOOMS, punch_every=PUNCH_EVERY):
    """Returns (segments, speech_end). Each segment: w0, w1 (word indexes), in (source s), frames, zoom, cont, out_t, kick."""
    drop = {i for i, w in enumerate(words) if fillers == "cut" and w.get("filler")}
    runs, run = [], []
    for i in range(len(words)):
        if i in drop:
            if run:
                runs.append([run[0], run[-1]])
                run = []
            continue
        if run and not keep_silence and words[i]["s"] - words[run[-1]]["e"] > GAP_MAX:
            runs.append([run[0], run[-1]])
            run = []
        run.append(i)
    if run:
        runs.append([run[0], run[-1]])
    if not runs:
        return [], 0.0
    merged = []
    for r in runs:
        dur = words[r[1]]["e"] - words[r[0]]["s"]
        if merged and not any(i in drop for i in range(merged[-1][1] + 1, r[0])) and \
                (dur < MIN_PIECE or words[merged[-1][1]]["e"] - words[merged[-1][0]]["s"] < MIN_PIECE):
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    pieces = []
    for i0, i1 in merged:
        cuts, last = [], words[i0]["s"]
        if punch:
            for i in range(i0 + 1, i1 + 1):
                gap_ok = words[i]["s"] - words[i - 1]["e"] >= 0.04
                tail_ok = words[i1]["e"] - words[i]["s"] >= 1.2
                due = words[i]["s"] - last
                # land the framing change on an emphasis word when one is near the ideal spot
                if tail_ok and gap_ok and (due >= punch_every or (due >= punch_every - 0.8 and words[i].get("emph"))):
                    cuts.append(i)
                    last = words[i]["s"]
        starts = [i0] + cuts
        ends = [c - 1 for c in cuts] + [i1]
        for k, (a, b) in enumerate(zip(starts, ends)):
            pieces.append({"i0": a, "i1": b, "cont_next": k < len(cuts)})

    def in_point(i, floor):
        s = words[i]["s"]
        before = [b for a, b in sil if b <= s + 0.06]
        start = max(before[-1] - 0.03, s - 0.15) if before else s - PAD_IN
        return max(min(start, s - 0.02), floor)

    def out_point(i, limit):
        e = words[i]["e"]
        after = [a for a, b in sil if a >= e - 0.06]
        end = min(after[0] + 0.04, e + PAD_OUT) if after else e + 0.08
        return min(max(end, e + 0.03), limit)

    segs, prev, prev_end = [], None, 0.0
    for k, pc in enumerate(pieces):
        i0, i1 = pc["i0"], pc["i1"]
        if prev and prev["cont_next"]:
            s = prev_end
        else:
            s = in_point(i0, (words[i0 - 1]["e"] if i0 > 0 else 0.0) + 0.02)
        if pc["cont_next"]:
            e = words[i1 + 1]["s"] - 0.03
        else:
            nxt = words[i1 + 1]["s"] if i1 + 1 < len(words) else words[i1]["e"] + 1
            e = out_point(i1, nxt - 0.04)
        n = max(1, round((e - s) * FPS))
        prev_end = round(s + n / FPS, 4)
        segs.append({"w0": i0, "w1": i1, "in": round(s, 3), "frames": n, "zoom": zooms[k % len(zooms)],
                     "cont": bool(prev and prev["cont_next"]), "kick": bool(words[i0].get("emph"))})
        prev = pc
    for k in range(1, len(segs)):
        if segs[k]["zoom"] == segs[k - 1]["zoom"]:
            segs[k]["zoom"] = zooms[1] if segs[k - 1]["zoom"] == zooms[0] else zooms[0]
    t = 0.0
    for sg in segs:
        sg["out_t"] = round(t, 4)
        t += sg["frames"] / FPS
    return segs, round(t, 4)


def src_to_out(segs, t_src):
    """Map a source time to output time (None if it was cut)."""
    for sg in segs:
        a, b = sg["in"], sg["in"] + sg["frames"] / FPS
        if a <= t_src < b:
            return sg["out_t"] + (t_src - a)
    return None


def beat_map(segs, words):
    """Human-readable beat list: one line per piece with the framing and the first words."""
    rows = []
    for sg in segs:
        txt = " ".join(w["w"] for w in words[sg["w0"]:sg["w1"] + 1])
        rows.append(f"{sg['out_t']:6.2f}  {sg['frames'] / FPS:5.2f}s  x{sg['zoom']:.2f}{'  KICK' if sg['kick'] else '      '}  {txt[:70]}")
    return "\n".join(rows)


def static_stretches(segs, limit=8.0):
    """Pieces with no framing change for longer than `limit` seconds (retention law 2). Every piece boundary is a
    visible change (the framing jumps), so only a single long piece can be static."""
    return [(round(sg["out_t"], 2), round(sg["out_t"] + sg["frames"] / FPS, 2)) for sg in segs if sg["frames"] / FPS > limit]
