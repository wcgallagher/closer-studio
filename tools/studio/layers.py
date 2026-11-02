"""Layers: the VSL graphics on top of a long-form cut, declared in one JSON file and anchored to spoken words.

`longform ... --layers layers.json` reads it. Every time in it is an anchor on the clock of the video you cut (the
times in transcript.txt), so the graphics follow the words when the cut changes:
  "There@6.2"            the word "There" nearest 6.2 s, at its start
  "manage.@19.0:end"     at the end of the word
  "Because@13.5-0.08"    80 ms before the word starts (+/- seconds)
  "one out of seven"     a spoken phrase (3+ words), at its start
  12.4                   a plain time
  "SPEECH_END" / "END"   the last word / the end of the video (end card included)

{
  "scenes_html": "tools/vsl/mg/scenes.html",              optional; the scenes file render.js loads
  "scenes": [{"scene": "crm", "from": "There@6.2-0.05", "to": "Because@13.5-0.08", "cues": {"c401": "401k@9.2"}}],
  "chips":  [{"at": "book@27.0", "text": "YOUR EXISTING BOOK", "hold": 1.6, "row": 0}],
  "headline": {"text": "The money\\Nis already\\Nin your book.", "until": 3.5, "pos": [0.66, 0.12]},
  "proof": {"eyebrow": "CHASE GALLAGHER  ·  FOUNDER", "big": "$3.8M", "small": "PLACED IN 2025  ·  20+ AGENTS", "from": 0.4, "until": 6.0},
  "moments": [{"from": "and@76.0+0.25", "to": "later.@79.7:end+0.2", "style": "bw", "lines": ["20+ agents.", "$3.8M placed in 2025."]}],
  "lockup": {"eyebrow": "...", "headline": "The money is\\Nalready in\\Nyour book.", "head_until": 3.5,
             "big": "$3.8M", "label": "...", "name": "...", "until": "we@10.6-0.05"},   a glass lockup on the left, drawn on frame 0
  "captions": {"from": 3.56, "plain_over_scenes": true, "off": [["Now@95.5", "END"]], "words": [2, 5]},
  "hands": {"file": "hands_take3.json", "take": "take3", "labels": {"L": ["SELL", "sell@47.1"], "R": ["SET", "set@47.9"]}},
  "music": {"file": "path/to/track.mp3", "start": 85.0, "mute": [["You@8.1", "Pretty@14.2"]]},
  "sfx": [{"at": "Now@95.5-1.5", "name": "riser", "gain": 0.25}],
  "take_change_kick": true,                                 a zoom kick and a whoosh on every take change
  "end_scene": true                                      the last scene (to "END") replaces the brand end card
}
Numbers on screen come from the brand file or the owner, never from here (see HOUSE_RULES.md).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np

from .common import FPS, KIT, hex_ass, norm, ts

LEAD = 0.25          # a scene is rendered this long before and after its window, for the dissolve
ANCHOR = re.compile(r"^(?P<word>[^@]+)@(?P<near>-?\d+(?:\.\d+)?)(?P<end>:end)?(?P<pad>[+-]\d+(?:\.\d+)?)?$")
MG = KIT / "tools" / "vsl" / "mg"


def load(path: Path | None) -> dict:
    if not path:
        return {}
    d = json.loads(Path(path).read_text())
    d["_base"] = str(Path(path).resolve().parent)
    return d


def _src(words: list[dict], spec) -> float:
    if isinstance(spec, (int, float)):
        return float(spec)
    s = str(spec).strip()
    m = ANCHOR.match(s)
    if m:
        t = norm(m["word"])
        hits = [w for w in words if norm(w["w"]) == t] or [w for w in words if norm(w["w"]).startswith(t)]
        if not hits:
            raise SystemExit(f"layers: word '{m['word']}' is not in the transcript")
        near = float(m["near"])
        w = min(hits, key=lambda w: abs(w["s"] - near))
        if abs(w["s"] - near) > 2.0:
            raise SystemExit(f"layers: '{m['word']}' is nearest at {w['s']:.2f} s, more than 2 s from {near} s; check transcript.txt")
        return (w["e"] if m["end"] else w["s"]) + float(m["pad"] or 0)
    from .longform import find_quote
    span = find_quote(words, s)
    if not span:
        raise SystemExit(f"layers: phrase not found: {s}")
    return span[0]


def to_out(segs: list[dict], t: float) -> float:
    """Source time to output time; a time inside a removed stretch snaps to the next kept frame."""
    for sg in segs:
        a, b = sg["in"], sg["in"] + sg["frames"] / FPS
        if a <= t < b:
            return sg["out_t"] + (t - a)
        if t < a:
            return sg["out_t"]
    last = segs[-1]
    return last["out_t"] + last["frames"] / FPS


def anchor(words, segs, spec, speech_end: float, total: float) -> float:
    if spec == "END":
        return total
    if spec == "SPEECH_END":
        return speech_end
    if isinstance(spec, str) and spec.startswith("SPEECH_END"):
        return speech_end + float(spec[len("SPEECH_END"):] or 0)
    return round(to_out(segs, _src(words, spec)), 3)


# ---------- scenes ----------

def resolve_scenes(L: dict, words, segs, speech_end, total) -> list[dict]:
    G = []
    for k, sc in enumerate(L.get("scenes", [])):
        a = anchor(words, segs, sc["from"], speech_end, total)
        b = anchor(words, segs, sc["to"], speech_end, total)
        if b <= a + 0.5:
            raise SystemExit(f"layers: scene {sc['scene']} is {b - a:.2f} s long; check its from/to anchors")
        t0 = a - LEAD
        cues = {c: round(anchor(words, segs, v, speech_end, total) - t0, 3) for c, v in sc.get("cues", {}).items()}
        dur = (b - t0) if sc["to"] == "END" else (b + LEAD - t0)
        G.append({"id": f"s{k + 1:02d}_{sc['scene']}", "scene": sc["scene"], "text": sc.get("text"), "frost": sc.get("frost"),
                  "start": round(a, 3), "end": round(b, 3),
                  "dur": round(dur, 3), "cues": cues, "is_end": sc["to"] == "END", "alpha": sc.get("layout") == "overlay",
                  "hard_in": sc.get("cut_in") == "hard", "hard_out": sc.get("cut_out") == "hard"})
    full = [g for g in G if not g["alpha"]]
    for k, g in enumerate(full):
        g["from_aroll"] = k == 0 or g["start"] - full[k - 1]["end"] > 0.3
        g["to_aroll"] = not g["is_end"] and (k == len(full) - 1 or full[k + 1]["start"] - g["end"] > 0.3)
    for g in G:
        if g["alpha"]:
            g["from_aroll"] = g["to_aroll"] = False
    return G


def render_scenes(G: list[dict], out: Path, L: dict, log=print) -> Path:
    if not G:
        return out
    node = shutil.which("node")
    if not node:
        raise SystemExit("the animated scenes need Node.js and Playwright: run `bash install.sh --scenes`")
    html = Path(L.get("scenes_html") or MG / "scenes.html")
    if not html.is_absolute():
        html = (Path(L["_base"]) / html) if (Path(L["_base"]) / html).exists() else (KIT / html)
    mg = out / "mg"
    mg.mkdir(parents=True, exist_ok=True)
    spec = mg / "graphics.json"
    entries = []
    for g in G:
        e = {k: g[k] for k in ("id", "scene", "dur", "cues", "alpha", "text") if g.get(k) is not None}
        if g.get("frost") == "solid":
            e["frost"] = "solid"
        entries.append(e)
        if g.get("frost") == "mask":       # the card's matte (white, no type) for the frosted-glass pass under it
            entries.append(dict(e, id=g["id"] + "_mask", frost="mask", alpha=True))
    spec.write_text(json.dumps(entries, indent=1))
    log(f"rendering {len(G)} animated scenes ({sum(g['dur'] for g in G):.0f} s) ...")
    subprocess.run([node, str(MG / "render.js"), str(spec), str(mg), "--html", str(html)], check=True)
    return mg


def scene_graph(G: list[dict], mg: Path, W: int, H: int, first_input: int, base: str) -> tuple[list[str], list[str], str]:
    """Filter-graph fragments: the speaker softens (6 px, then 14 px) under each dissolve, scenes overlay on top."""
    if not G:
        return [], [], base
    blur = []
    for g in G:
        if g["alpha"]:
            continue
        if g["from_aroll"] and not g.get("hard_in"):
            blur += [(g["start"] - 0.26, g["start"] - 0.13, 1), (g["start"] - 0.13, g["start"] + 0.04, 2)]
        if g["to_aroll"] and not g.get("hard_out"):
            blur += [(g["end"] - 0.04, g["end"] + 0.10, 2), (g["end"] + 0.10, g["end"] + 0.22, 1)]
    en = lambda lv: "+".join(f"between(t\\,{a:.3f}\\,{b:.3f})" for a, b, l in blur if l == lv) or "0"
    inputs_mask = []
    chain = [f"{base}split=3[sv0][svb1][svb2]", "[svb1]gblur=sigma=6[sb1]", "[svb2]gblur=sigma=14[sb2]",
             f"[sv0][sb1]overlay=enable='{en(1)}'[sx1]", f"[sx1][sb2]overlay=enable='{en(2)}'[sx2]"]
    cur, inputs = "[sx2]", []
    nxt = first_input + len(G)                 # mask inputs follow the scene inputs
    for k, g in enumerate(G):
        inputs += ["-i", str(mg / f"{g['id']}.{'mov' if g['alpha'] else 'mp4'}")]
        a0, d = g["start"] - LEAD, g["dur"]
        if g.get("frost") == "mask":
            # real glass: the shot under the card is blurred, desaturated and warmed, cut to the card's matte
            inputs_mask.append(str(mg / f"{g['id']}_mask.mov"))
            mi = nxt + len(inputs_mask) - 1
            chain.append(f"{cur}split=2[fq{k}a][fq{k}b]")
            chain.append(f"[fq{k}b]trim=start={max(0.0, a0):.3f}:end={a0 + d:.3f},gblur=sigma=28,eq=brightness=-0.24:saturation=0.25,"
                         f"colorchannelmixer=rr=.62:gg=.58:bb=.54,format=rgba[fz{k}]")
            # the matte fades exactly as its card does (below), so glass never outlives the card on top of it: v9's
            # colour clip faded at its cut while the matte stayed up, leaving an empty frosted slab for 0.25 s
            m_in = f"fade=t=in:st={LEAD - 0.04:.3f}:d=0.04" if g.get("hard_in") else f"fade=t=in:st=0:d={LEAD - 0.03:.2f}"
            m_out = f"fade=t=out:st={d - LEAD:.3f}:d={0.034 if g.get('hard_out') else LEAD:.3f}"
            chain.append(f"[{mi}:v]scale={W}:{H},format=rgba,alphaextract,{m_in},{m_out},setpts=PTS-STARTPTS+{a0:.3f}/TB[fm{k}]")
            chain.append(f"[fz{k}][fm{k}]alphamerge[fza{k}]")
            chain.append(f"[fq{k}a][fza{k}]overlay=eof_action=pass:enable='between(t\\,{a0:.3f}\\,{a0 + d:.3f})'[fqo{k}]")
            cur = f"[fqo{k}]"
        fin = f"fade=t=in:st={LEAD - 0.04:.3f}:d=0.04" if g.get("hard_in") else f"fade=t=in:st=0:d={(LEAD - 0.03) if (g['from_aroll'] or g['alpha']) else 0.08:.2f}"
        f = f"[{first_input + k}:v]scale={W}:{H}:flags=lanczos:out_color_matrix=bt709:out_range=tv,format=yuva420p,{fin}:alpha=1"
        if g["alpha"] and g.get("hard_out"):        # an overlay that leaves with a cut: gone in one frame
            f += f",fade=t=out:st={d - LEAD:.3f}:d=0.034:alpha=1"
        elif g["alpha"]:
            f += f",fade=t=out:st={d - LEAD:.3f}:d={LEAD:.2f}:alpha=1"
        elif g["to_aroll"] and g.get("hard_out"):
            f += f",fade=t=out:st={d - LEAD:.3f}:d=0.04:alpha=1"
        elif g["to_aroll"]:
            f += f",fade=t=out:st={d - LEAD - 0.05:.3f}:d={LEAD + 0.05:.2f}:alpha=1"
        chain.append(f + f",setpts=PTS-STARTPTS+{a0:.3f}/TB[sg{k}]")
        chain.append(f"{cur}[sg{k}]overlay=eof_action=pass:enable='between(t\\,{a0:.3f}\\,{a0 + d:.3f})'[sy{k}]")
        cur = f"[sy{k}]"
    for m in inputs_mask:
        inputs += ["-i", m]
    return inputs, chain, cur


def moment_graph(moments: list[dict], base: str) -> tuple[list[str], str]:
    """Styled moments on the speaker: bw / tint = the saturation given (0.25 = mostly grey) with a touch more contrast."""
    out, cur = [], base
    for k, m in enumerate([m for m in moments if m.get("style") == "dim"]):
        # the live shot steps back behind a proof: darker, less colour, soft focus; ramps in over ramp_s, out the same
        a, b, r = m["a"], m["b"], float(m.get("ramp", 0.12))
        e = f"between(t\\,{a:.3f}\\,{b:.3f})"
        out.append(f"{cur}split=2[dm{k}a][dm{k}b];[dm{k}b]gblur=sigma={float(m.get('blur', 10)) / 2:.1f},"
                   f"eq=saturation={float(m.get('saturation', 0.5)):.2f},format=gbrp,colorchannelmixer=rr={float(m.get('brightness', 0.35)):.2f}:gg={float(m.get('brightness', 0.35)):.2f}:bb={float(m.get('brightness', 0.35)):.2f},format=yuv420p[dm{k}c];"
                   f"[dm{k}a][dm{k}c]overlay=enable='{e}'[dm{k}]")
        cur = f"[dm{k}]"
    base = cur
    mm = [m for m in moments if m.get("style", "bw") in ("bw", "tint")]
    if not mm:
        return out, base
    f = ",".join(f"hue=s={m.get('saturation', 0.25):.2f}:enable='between(t\\,{m['a']:.3f}\\,{m['b']:.3f})',"
                 f"eq=contrast={1.10 if m.get('saturation', 0.25) < 0.5 else 1.04:.2f}:brightness=-0.02:enable='between(t\\,{m['a']:.3f}\\,{m['b']:.3f})'" for m in mm)
    return out + [f"{base}{f}[mo]"], "[mo]"


# ---------- text layers (ASS) ----------

def styles(W: int, H: int, brand: dict) -> list[str]:
    """Sizes measured from the shipped SMA VSL v7 at 1920x1080, scaled to this frame's height."""
    f, c = brand["fonts"], brand["colors"]
    s = H / 1080
    txt, acc = hex_ass(c["text"]), hex_ass(c["accent"])
    gold_hot = hex_ass(c.get("gold_hot", c.get("accent_soft", c["accent"])))
    gold = hex_ass(c.get("gold", c.get("accent_soft", c["accent"])))
    sand = hex_ass(c.get("sand", "#F1EADD"))
    cap, cap2 = f["caption"], f.get("caption_2", f["caption"])
    o = max(1, int(3 * s))
    return [
        f"Style: Headline,{f['display']},{int(108 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,{o},0,5,0,0,0,1",
        f"Style: Plate,{cap},10,{txt},{txt},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: ProofEyebrow,{cap2},{int(26 * s)},{sand},{sand},&H00000000,&H00000000,0,0,0,0,100,100,{max(2, int(5 * s))},0,1,0,0,7,0,0,0,1",
        f"Style: ProofBig,{f['display']},{int(124 * s)},{gold_hot},{gold_hot},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: ProofSmall,{cap2},{int(34 * s)},{txt},{txt},&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
        f"Style: Chip,{cap},{int(58 * s)},{txt},{txt},{acc},&H00000000,0,0,0,0,100,100,1,0,3,{max(3, int(16 * s))},0,7,0,0,0,1",
        f"Style: Moment,{f['display']},{int(120 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,{o},0,5,0,0,0,1",
        f"Style: Moment2,{f['display']},{int(74 * s)},{gold},{gold},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,{o},0,5,0,0,0,1",
        f"Style: LockEyebrow,{f.get('mono', 'JetBrains Mono')},{int(40 * s)},{sand},{sand},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: LockHead,{f['display']},{int(92 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: LockBig,{f['display']},{int(124 * s)},{gold_hot},{gold_hot},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: LockLabel,{f.get('ui', cap2)},{int(48 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: LockName,{f.get('ui', cap2)},{int(36 * s)},{sand},{sand},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: ChipQuiet,{cap},{int(56 * s)},{sand},{sand},{hex_ass(c.get('bg', '#0e1114'), '40')},&H00000000,0,0,0,0,100,100,1,0,3,{max(3, int(14 * s))},0,7,0,0,0,1",
        f"Style: Pointer,{f.get('ui', cap)},{int(58 * s)},{txt},{txt},{acc},&H00000000,-1,0,0,0,100,100,0,0,3,{max(3, int(16 * s))},0,9,0,0,0,1",
        f"Style: LockMoment,{f['display']},{int(96 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: Hand,{cap},{int(84 * s)},{txt},{txt},{acc},&H00000000,0,0,0,0,100,100,2,0,3,{max(4, int(22 * s))},0,2,0,0,0,1",
        f"Style: GlassChip,{f.get('ui', cap)},{int(54 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,{max(1, int(1 * s))},0,1,0,0,4,0,0,0,1",
        f"Style: HandText,{f.get('ui', cap)},{int(110 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,{max(1, int(2 * s))},0,1,0,0,2,0,0,0,1",
    ]


def _rrect(w: int, h: int, r: int) -> str:
    """Rounded rectangle as an ASS vector path (top-left origin)."""
    k = int(r * 0.45)
    return (f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} "
            f"l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0")


def _glass(x: int, y: int, w: int, h: int, s: float, brand: dict, a: float, b: float, fad: str, layer: int = 2) -> list[str]:
    c = brand["colors"]
    bg, sand = hex_ass(c.get("bg", "#0e1114")), hex_ass(c.get("sand", "#F1EADD"))
    return [f"Dialogue: {layer},{ts(a)},{ts(b)},Plate,,0,0,0,,{{\\an7\\pos({x},{y})\\1c{bg}\\1a&H4D&\\3c{sand}\\3a&HDE&\\bord{max(1, round(s))}\\shad0{fad}\\p1}}"
            f"{_rrect(w, h, int(14 * s))}{{\\p0}}"]


def _plus(text: str, brand: dict) -> str:
    """Display serifs often draw "+" small and high; set it in the UI face so "20+" reads as a count."""
    ui, disp = brand["fonts"].get("ui"), brand["fonts"]["display"]
    return text.replace("+", f"{{\\fn{ui}}}+{{\\fn{disp}}}") if ui and "+" in text else text


def text_events(L: dict, words, segs, speech_end, total, W, H, brand, scenes: list[dict], scene=None) -> tuple[list[str], list[dict], list[float]]:
    """ASS events for the headline, the proof card, chips and moment lines; returns (events, moments, chip_times)."""
    ev, moments, chip_t = [], [], []
    A = lambda s: anchor(words, segs, s, speech_end, total)
    hd = L.get("headline")
    if hd:
        x, y = hd.get("pos", [0.66, 0.12])
        a, b = A(hd.get("from", 0.0)), A(hd.get("until", 3.5))
        ev.append(f"Dialogue: 6,{ts(a)},{ts(b)},Headline,,0,0,0,,{{\\an{int(hd.get('align', 7))}\\pos({int(W * x)},{int(H * y)})\\fad({int(hd.get('fade_in', 0))},250)\\fscx106\\fscy106\\t(0,180,\\fscx100\\fscy100)}}{hd['text']}")
    lk = L.get("lockup")
    if lk:
        s = H / 1080
        x0, w = int(lk.get("x", 70) * s), int(lk.get("width", 650) * s)
        pad = int(30 * s)
        a, hb, b = A(lk.get("from", 0.0)), A(lk.get("head_until", 3.5)), A(lk.get("until", 10.0))
        gold = hex_ass(brand["colors"].get("gold", brand["colors"]["accent"]))
        # the headline card (eyebrow + headline), then the proof card under it; the headline card leaves first
        y1, h1 = int(lk.get("y", 96) * s), int(lk.get("head_h", 420) * s)
        y2, h2 = y1 + h1 + int(14 * s), int(lk.get("proof_h", 300) * s)
        ev += _glass(x0, y1, w, h1, s, brand, a, hb, "\\fad(0,300)")
        ev.append(f"Dialogue: 3,{ts(a)},{ts(hb)},LockEyebrow,,0,0,0,,{{\\an7\\pos({x0 + pad},{y1 + int(30 * s)})\\fad(0,300)}}{lk.get('eyebrow', '')}")
        ev.append(f"Dialogue: 3,{ts(a)},{ts(hb)},LockHead,,0,0,0,,{{\\an7\\pos({x0 + pad},{y1 + int(lk.get('head_y', 118) * s)})\\fad(0,300)}}{lk.get('headline', '')}")
        ev += _glass(x0, y2, w, h2, s, brand, a, b, "\\fad(0,250)")
        if scene is not None:
            scene.overlays += [(a, hb, (x0, y1, x0 + w, y1 + h1), "lockup"), (a, b, (x0, y2, x0 + w, y2 + h2), "lockup")]
        ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Plate,,0,0,0,,{{\\an7\\pos({x0 + pad},{y2 + int(22 * s)})\\1c{gold}\\bord0\\shad0\\fad(0,250)\\p1}}m 0 0 l {int(120 * s)} 0 l {int(120 * s)} {max(2, int(3 * s))} l 0 {max(2, int(3 * s))}{{\\p0}}")
        ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockBig,,0,0,0,,{{\\an7\\pos({x0 + pad - int(4 * s)},{y2 + int(36 * s)})\\fad(0,250)}}{_plus(lk.get('big', ''), brand)}")
        ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockLabel,,0,0,0,,{{\\an7\\pos({x0 + pad},{y2 + int(lk.get('label_y', 178) * s)})\\fad(0,250)}}{lk.get('label', '')}")
        if lk.get("name"):
            ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockName,,0,0,0,,{{\\an7\\pos({x0 + pad},{y2 + int(lk.get('name_y', 252) * s)})\\fad(0,250)}}{lk['name']}")
    pf = L.get("proof")
    if pf:
        a, b = A(pf.get("from", 0.4)), A(pf.get("until", 6.0))
        s = H / 1080
        px, py = pf.get("pos", [0.025, 0.515])
        x0, y0 = int(W * px), int(H * py)
        pw, ph = int(600 * s), int(248 * s)
        panel = hex_ass(brand["colors"].get("bg", "#0e1114"))
        ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Plate,,0,0,0,,{{\\pos({x0},{y0})\\1c{panel}\\alpha&H2E&\\fad(90,250)\\p1}}m 0 0 l {pw} 0 {pw} {ph} 0 {ph}{{\\p0}}")
        ev.append(f"Dialogue: 3,{ts(a + 0.05)},{ts(b)},ProofEyebrow,,0,0,0,,{{\\pos({x0 + int(26 * s)},{y0 + int(26 * s)})\\fad(90,250)}}{pf.get('eyebrow', '')}")
        ev.append(f"Dialogue: 3,{ts(a + 0.12)},{ts(b)},ProofBig,,0,0,0,,{{\\pos({x0 + int(18 * s)},{y0 + int(56 * s)})\\fad(90,250)\\fscx92\\fscy92\\t(0,220,\\fscx100\\fscy100)}}{pf['big']}")
        ev.append(f"Dialogue: 3,{ts(a + 0.22)},{ts(b)},ProofSmall,,0,0,0,,{{\\pos({x0 + int(26 * s)},{y0 + int(206 * s)})\\fad(90,250)}}{pf.get('small', '')}")
    in_scene = lambda t: any(g["start"] - 0.2 <= t <= g["end"] + 0.2 for g in scenes)
    for ch in L.get("chips", []):
        t = A(ch["at"])
        if in_scene(t):
            continue
        hold = A(ch["until"]) - t if "until" in ch else float(ch.get("hold", 1.6))
        kind = ch.get("style", "chip")
        if kind == "pointer":       # a red pill top right that points at the page button under the video
            x, y = int(W * ch.get("x", 0.955)), int(H * ch.get("y", 0.075))
            ev.append(f"Dialogue: 5,{ts(t)},{ts(t + hold)},Pointer,,0,0,0,,{{\\an9\\pos({x},{y})\\fad(0,120)}}{ch['text']}")
            if scene is not None:
                from . import placement as plc
                fs = int(58 * H / 1080)
                pw, ph = plc.text_box(ch["text"], font_file(brand["fonts"].get("ui", "Inter")), fs, int(16 * H / 1080), int(16 * H / 1080))
                scene.overlays.append((t, t + hold, (x - pw, y, x, y + ph), "pointer"))
        elif kind == "glass":       # the premium chip: a dark glass pill, white type, a gold bead; placed by the engine
            from . import placement as plc
            s_ = H / 1080
            fs = int(ch.get("size", 54) * s_)
            padx, pady = int(28 * s_), int(16 * s_)
            tw, th = plc.text_box(ch["text"], font_file(brand["fonts"].get("ui", "Inter")), fs, 0, 0, 0.02)
            bead = int(14 * s_)
            pw, ph = tw + 2 * padx + bead + int(16 * s_), int(fs * 1.25) + 2 * pady
            if scene is not None and "x" not in ch:
                x, y, _r = plc.place(scene, pw, ph, t - 0.1, t + hold, group="chips", style="plate", label=f"chip {ch['text']}")
            else:
                x, y = int(W * ch.get("x", 0.69)) - padx, int(H * (ch.get("y", 0.40) + 0.095 * int(ch.get("row", 0))))
            c = brand["colors"]
            bg, sand, gold = hex_ass(c.get("bg", "#0e1114")), hex_ass(c.get("sand", "#F1EADD")), hex_ass(c.get("gold_hot", c.get("accent", "#E0BE66")))
            fad, mv = "\\fad(140,180)", int(18 * s_)
            ev.append(f"Dialogue: 4,{ts(t)},{ts(t + hold)},Plate,,0,0,0,,{{\\an7\\move({x},{y + mv},{x},{y},0,220)\\1c{bg}\\1a&H38&\\3c{sand}\\3a&HD0&\\bord{max(1, round(s_))}\\shad0{fad}\\p1}}{_rrect(pw, ph, ph // 2)}{{\\p0}}")
            bx, by = x + padx, y + ph // 2 - bead // 2
            ev.append(f"Dialogue: 5,{ts(t)},{ts(t + hold)},Plate,,0,0,0,,{{\\an7\\move({bx},{by + mv},{bx},{by},0,220)\\1c{gold}\\bord0\\shad0{fad}\\p1}}{_rrect(bead, bead, bead // 2)}{{\\p0}}")
            tx, ty = bx + bead + int(16 * s_), y + ph // 2
            ev.append(f"Dialogue: 5,{ts(t)},{ts(t + hold)},GlassChip,,0,0,0,,{{\\an4\\move({tx},{ty + mv},{tx},{ty},0,220){fad}}}{ch['text']}")
        else:
            st = "ChipQuiet" if kind == "quiet" else "Chip"
            if scene is not None and "x" not in ch:
                from . import placement as plc
                fs = int((56 if kind == "quiet" else 58) * H / 1080)
                pad = int(16 * H / 1080)
                cw_, chh = plc.text_box(ch["text"], font_file(brand["fonts"]["caption"]), fs, pad, pad, 0.017)
                x, y, _r = plc.place(scene, cw_, chh, t - 0.1, t + hold, group="chips", style="plate", label=f"chip {ch['text']}")
                x, y = x + pad, y + pad
            else:
                x, y = int(W * ch.get("x", 0.69)), int(H * (ch.get("y", 0.40) + 0.095 * int(ch.get("row", 0))))
            ev.append(f"Dialogue: 5,{ts(t)},{ts(t + hold)},{st},,0,0,0,,{{\\an7\\move({x + int(70 * H / 1080)},{y},{x},{y},0,170)\\fad(120,200)}}{ch['text']}")
        chip_t.append(t)
    for m in L.get("moments", []):
        a, b = A(m["from"]), A(m["to"])
        moments.append({"a": a, "b": b, "style": m.get("style", "bw"), "saturation": float(m.get("saturation", 0.25)),
                        **{k: m[k] for k in ("blur", "brightness", "ramp") if k in m}})
        if isinstance(m.get("card"), dict):   # the opening proof again: big number and its label, on glass
            s = H / 1080
            lk = L.get("lockup") or {}
            x0, w = int(lk.get("x", 70) * s), int(lk.get("width", 650) * s)
            y2 = int((lk.get("y", 96) + lk.get("head_h", 420) + 14) * s)
            ev += _glass(x0, y2, w, int(lk.get("proof_h", 300) * s), s, brand, a, b, "\\fad(150,200)")
            ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockBig,,0,0,0,,{{\\an7\\pos({x0 + int(26 * s)},{y2 + int(36 * s)})\\fad(150,200)}}{_plus(m['card'].get('big', ''), brand)}")
            ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockLabel,,0,0,0,,{{\\an7\\pos({x0 + int(30 * s)},{y2 + int(lk.get('label_y', 178) * s)})\\fad(150,200)}}{m['card'].get('label', '')}")
        elif m.get("card"):           # one line in the lockup's proof position, on glass
            s = H / 1080
            x0, w, y2 = int(70 * s), int(650 * s), int((96 + 420 + 14) * s)
            ev += _glass(x0, y2, w, int(150 * s), s, brand, a, b, "\\fad(150,200)")
            ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockMoment,,0,0,0,,{{\\an7\\pos({x0 + int(30 * s)},{y2 + int(16 * s)})\\fad(150,200)}}{_plus(m['card'], brand)}")
        lines = m.get("lines") or []
        x, y = m.get("pos", [0.24, 0.40])
        for i, ln in enumerate(lines):
            ta = a + 0.35 * i
            st = "Moment" if i == 0 else "Moment2"
            anim = "\\fscx112\\fscy112\\t(0,160,\\fscx100\\fscy100)" if i == 0 else ""
            ev.append(f"Dialogue: 6,{ts(ta)},{ts(b)},{st},,0,0,0,,{{\\an5\\pos({int(W * x)},{int(H * (y + 0.10 * i))})\\fad(120,180){anim}}}{_plus(ln, brand)}")
    return ev, moments, chip_t


def font_file(family: str, bold: bool = True) -> Path | None:
    """The kit's font file for a family name (fonts/ holds Inter-Bold.ttf, Montserrat-Black.ttf, ...)."""
    from .common import FONTS
    key = family.replace(" ", "").lower()
    files = sorted(FONTS.glob("*.ttf"))
    pick = [f for f in files if f.stem.replace("-", "").lower().startswith(key)] or \
           [f for f in files if f.stem.split("-")[0].lower() == family.split()[0].lower()]
    if not pick:
        return None
    if bold:
        b = [f for f in pick if any(x in f.stem for x in ("Black", "Bold", "ExtraBold"))]
        return (b or pick)[0]
    return pick[0]


def hand_events(L: dict, an: dict, segs: list[dict], cam: dict | None, W: int, H: int, push: float, ky: float,
                words, speech_end, total, scene=None, chunks=None, brand=None) -> list[str]:
    """Labels for a hand gesture (a rows file: [{"t": take seconds, "hands": [{"side", "cx", "top", "left", "right", "bottom", "px"}]}]).

    v2 rules (owner note 2026-11-02: the v8 labels "didn't watch the video"):
      - a label shows only while its word is the caption line on screen, and never together with the next label
      - it appears on its word (2 frames early) and leaves when the hand drops, the caption line changes or the next
        label comes, whichever is first, and stays at least 0.45 s
      - it sits beside the hand at the top of the gesture (the median of the frames within 4 % of the highest point),
        chosen by the placement engine so it never touches the face or the captions, and it holds still: a label that
        chases a moving hand reads as a glitch
      - a gold pill with dark type, popped in over 6 frames, faded out over 5"""
    hd = L.get("hands")
    if not hd or not cam:
        return []
    from . import placement as plc
    path = Path(hd["file"]) if Path(hd["file"]).is_absolute() else Path(L["_base"]) / hd["file"]
    rows = sorted(json.loads(path.read_text()), key=lambda r: r["t"])
    ranges = [r for r in an.get("beats", []) if r["take"] == hd["take"]]
    min_px, s = float(hd.get("min_px", 2500)), H / 1080
    mp = scene.mapper if scene is not None and scene.mapper is not None else plc.Mapper(an, segs, cam, W, H, push, ky)
    sc = scene or plc.Scene(W, H, mp, *plc.face_track(an))
    # hand boxes on the output clock, per side
    track = {"L": [], "R": []}
    for row in rows:
        rr = [r for r in ranges if r["src_in"] <= row["t"] < r["src_out"]]
        if not rr:
            continue
        t_sel = rr[0]["sel_in"] + row["t"] - rr[0]["src_in"]
        sg = next((g for g in segs if g["in"] <= t_sel < g["in"] + g["frames"] / FPS), None)
        if sg is None:
            continue
        t_out = sg["out_t"] + t_sel - sg["in"]
        for h in row["hands"]:
            if h.get("px", 0) < min_px or h.get("side") not in track:
                continue
            r = mp.rect(t_out, h.get("left", h["cx"] - 0.05), h["top"], h.get("right", h["cx"] + 0.05), h.get("bottom", h["top"] + 0.2))
            if r:
                track[h["side"]].append((t_out, r))
    for side in track:
        sc.hands += [(t - 0.02, t + 0.05, r) for t, r in track[side]]
    def take_to_out(t_take):
        rr = [r for r in ranges if r["src_in"] <= t_take < r["src_out"]]
        if not rr:
            return None
        t_sel = rr[0]["sel_in"] + t_take - rr[0]["src_in"]
        sg = next((g for g in segs if g["in"] <= t_sel < g["in"] + g["frames"] / FPS), None)
        return None if sg is None else sg["out_t"] + t_sel - sg["in"]

    # label specs: ["SELL", "sell@47.69"] (word-timed, v2) or {"text", "in", "out" (take seconds, from the hands), "mode":
    # "static" | "follow", "x" (px, optional), "gap" (px above the fingertips)}
    specs = []
    for side, v in hd["labels"].items():
        if isinstance(v, dict):
            a_o, b_o = take_to_out(float(v["in"])), take_to_out(float(v["out"]))
            if a_o is None or b_o is None:
                continue
            specs.append(dict(v, side=side, a=a_o, b=b_o, timed="hands"))
        else:
            t_on = anchor(words, segs, v[1], speech_end, total)
            specs.append({"side": side, "text": v[0], "a": t_on - 2 / FPS, "b": None, "timed": "words", "mode": "static"})
    specs.sort(key=lambda x: x["a"])
    ui = (brand or {}).get("fonts", {}).get("ui", "Inter")
    size = int(hd.get("size", 110) * s)
    fpath = font_file(ui)
    cols = (brand or {}).get("colors", {})
    bg, cream = hex_ass(cols.get("bg", "#0d0b09")), hex_ass(cols.get("text", "#FAF6EE"))
    padx, pady, rad = int(22 * s), int(14 * s), int(10 * s)
    ev = []
    for i, sp in enumerate(specs):
        side, text = sp["side"], sp["text"].upper()
        nxt = specs[i + 1]["a"] - 2 / FPS if i + 1 < len(specs) else 1e9
        pts = [(t, r) for t, r in track[side] if sp["a"] - 0.35 <= t <= (sp["b"] or sp["a"] + 1.2) + 0.1]
        if not pts:
            continue
        top = min(r[1] for _, r in pts)
        tp = min(pts, key=lambda q: q[1][1])[0]
        if sp["b"] is None:                       # word-timed: leave when the hand drops, the caption changes or the next label comes
            ch_end = next((bb for (ca, bb, *_r) in (chunks or []) if ca - 0.06 <= sp["a"] + 0.07 < bb), sp["a"] + 1.2)
            drop = next((t for t, r in track[side] if t > max(sp["a"], tp) and r[1] > top + 0.12 * H), sp["a"] + 1.6)
            sp["b"] = max(min(nxt, ch_end, drop + 0.12, sp["a"] + 1.6), min(sp["a"] + 0.45, nxt))
        if sp.get("timed") == "hands":            # a word needs about half a second to be read where it lands
            sp["b"] = max(sp["b"], sp["a"] + float(hd.get("min_s", 0.5)))
        a, b = sp["a"], min(sp["b"], nxt)
        tw, th = plc.text_box(text, fpath, size, 0, 0, 0.0)
        w, h = tw + 2 * padx, int(size * 0.95) + 2 * pady
        gap = int(sp.get("gap", 30) * s)
        inwin = [(t, r) for t, r in pts if a - 0.05 <= t <= b + 0.05] or pts
        cx = sp.get("x") * s if sp.get("x") else float(np.median([(r[0] + r[2]) / 2 for _, r in inwin]))
        cx = min(max(cx, 0.05 * W + w / 2), 0.95 * W - w / 2)          # inside title-safe even when the hand clips the edge
        fade_in, fade_out = int(4 * 1000 / FPS), int(3 * 1000 / FPS)
        if sp.get("mode", "static") == "follow":
            # rides the hand: bottom = fingertip top - gap, x fixed, freezes at its out time. Smoothed over `smooth` frames
            # (default 5) and never moving more than `max_step` of the height per frame (default 2.5 %): a label that
            # jumps with every finger twitch reads as a glitch (v9 review: 170 px in one frame at 3-frame smoothing)
            seq = sorted(inwin)
            tops = np.array([r[1] for _, r in seq]); ts_ = np.array([t for t, _ in seq])
            win = max(1, int(hd.get("smooth", 5)) | 1)
            if len(tops) >= win > 1:
                tops = np.convolve(np.pad(tops, win // 2, mode="edge"), np.ones(win) / win, "valid")
            step = float(hd.get("max_step", 0.025)) * H
            n_fr = max(1, int(round((b - a) * FPS)))
            y_prev = None
            for k in range(n_fr + 3):
                t = a + k / FPS
                tt = min(t, b)
                bottom = float(np.interp(tt, ts_, tops)) - gap
                y = max(0.06 * H + h, bottom)
                if y_prev is not None:
                    y = min(max(y, y_prev - step), y_prev + step)
                y_prev = y
                al = "" if k < n_fr else f"\\alpha&H{int(255 * (k - n_fr + 1) / 3):02X}&"
                scl = 85 + 15 * min(1.0, k / 4)
                tag = f"\\an2\\pos({cx:.0f},{y:.0f})\\fscx{scl:.0f}\\fscy{scl:.0f}{al}"
                ev.append(f"Dialogue: 4,{ts(t)},{ts(t + 1 / FPS)},Plate,,0,0,0,,{{{tag}\\1c{bg}\\1a&H66&\\3c{cream}\\3a&HD1&\\bord{max(1, round(s))}\\shad0\\p1}}"
                          f"{_rrect_an2(w, h, rad)}{{\\p0}}")
                ev.append(f"Dialogue: 5,{ts(t)},{ts(t + 1 / FPS)},HandText,,0,0,0,,{{\\an2\\pos({cx:.0f},{y - pady + int(4 * s):.0f})\\fscx{scl:.0f}\\fscy{scl:.0f}{al}}}{text}")
            sc.report.append({"label": f"hand {text}", "a": round(a, 2), "b": round(b, 2), "mode": "follow", "x": round(cx), "ok": True})
        else:
            bottom = top - gap
            y = max(0.06 * H + h, bottom)
            x0 = int(cx - w / 2)
            plc.place(sc, w, h, a, b, group="hands", fixed=(x0, int(y - h)), label=f"hand {text}")
            anim = f"\\fscx85\\fscy85\\blur4\\t(0,{fade_in},\\fscx100\\fscy100\\blur0)\\fad({fade_in},{fade_out})"
            ev.append(f"Dialogue: 4,{ts(a)},{ts(b + 3 / FPS)},Plate,,0,0,0,,{{\\an2\\pos({cx:.0f},{y:.0f}){anim}\\1c{bg}\\1a&H66&\\3c{cream}\\3a&HD1&\\bord{max(1, round(s))}\\shad0\\p1}}"
                      f"{_rrect_an2(w, h, rad)}{{\\p0}}")
            ev.append(f"Dialogue: 5,{ts(a)},{ts(b + 3 / FPS)},HandText,,0,0,0,,{{\\an2\\pos({cx:.0f},{y - pady + int(4 * s):.0f}){anim}}}{text}")
    return ev


def _rrect_an2(w: int, h: int, r: int) -> str:
    """Rounded rectangle path for \\an2 (bottom-centre anchor): libass anchors drawings by their bounding box."""
    return _rrect(w, h, r)


def _rrect_c(w: int, h: int, r: int) -> str:
    """Rounded rectangle path centred on its origin (for \\an5 scaling about the middle)."""
    return _rrect(w, h, r)
