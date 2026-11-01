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
        G.append({"id": f"s{k + 1:02d}_{sc['scene']}", "scene": sc["scene"], "start": round(a, 3), "end": round(b, 3),
                  "dur": round(dur, 3), "cues": cues, "is_end": sc["to"] == "END", "alpha": sc.get("layout") == "overlay"})
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
    spec.write_text(json.dumps([{k: g[k] for k in ("id", "scene", "dur", "cues", "alpha")} for g in G], indent=1))
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
        if g["from_aroll"]:
            blur += [(g["start"] - 0.26, g["start"] - 0.13, 1), (g["start"] - 0.13, g["start"] + 0.04, 2)]
        if g["to_aroll"]:
            blur += [(g["end"] - 0.04, g["end"] + 0.10, 2), (g["end"] + 0.10, g["end"] + 0.22, 1)]
    en = lambda lv: "+".join(f"between(t\\,{a:.3f}\\,{b:.3f})" for a, b, l in blur if l == lv) or "0"
    chain = [f"{base}split=3[sv0][svb1][svb2]", "[svb1]gblur=sigma=6[sb1]", "[svb2]gblur=sigma=14[sb2]",
             f"[sv0][sb1]overlay=enable='{en(1)}'[sx1]", f"[sx1][sb2]overlay=enable='{en(2)}'[sx2]"]
    cur, inputs = "[sx2]", []
    for k, g in enumerate(G):
        inputs += ["-i", str(mg / f"{g['id']}.{'mov' if g['alpha'] else 'mp4'}")]
        a0, d = g["start"] - LEAD, g["dur"]
        f = f"[{first_input + k}:v]scale={W}:{H}:flags=lanczos,format=yuva420p,fade=t=in:st=0:d={(LEAD - 0.03) if (g['from_aroll'] or g['alpha']) else 0.08:.2f}:alpha=1"
        if g["alpha"]:
            f += f",fade=t=out:st={d - LEAD:.3f}:d={LEAD:.2f}:alpha=1"
        elif g["to_aroll"]:
            f += f",fade=t=out:st={d - LEAD - 0.05:.3f}:d={LEAD + 0.05:.2f}:alpha=1"
        chain.append(f + f",setpts=PTS-STARTPTS+{a0:.3f}/TB[sg{k}]")
        chain.append(f"{cur}[sg{k}]overlay=eof_action=pass:enable='between(t\\,{a0:.3f}\\,{a0 + d:.3f})'[sy{k}]")
        cur = f"[sy{k}]"
    return inputs, chain, cur


def moment_graph(moments: list[dict], base: str) -> tuple[list[str], str]:
    """Styled moments on the speaker: bw / tint = the saturation given (0.25 = mostly grey) with a touch more contrast."""
    mm = [m for m in moments if m.get("style", "bw") in ("bw", "tint")]
    if not mm:
        return [], base
    f = ",".join(f"hue=s={m.get('saturation', 0.25):.2f}:enable='between(t\\,{m['a']:.3f}\\,{m['b']:.3f})',"
                 f"eq=contrast={1.10 if m.get('saturation', 0.25) < 0.5 else 1.04:.2f}:brightness=-0.02:enable='between(t\\,{m['a']:.3f}\\,{m['b']:.3f})'" for m in mm)
    return [f"{base}{f}[mo]"], "[mo]"


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
        f"Style: LockEyebrow,{f.get('mono', 'JetBrains Mono')},{int(36 * s)},{sand},{sand},&H00000000,&H00000000,0,0,0,0,100,100,{max(1, int(2 * s))},0,1,0,0,7,0,0,0,1",
        f"Style: LockHead,{f['display']},{int(92 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: LockBig,{f['display']},{int(124 * s)},{gold_hot},{gold_hot},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: LockLabel,{f.get('ui', cap2)},{int(44 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: LockName,{f.get('ui', cap2)},{int(36 * s)},{sand},{sand},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: ChipQuiet,{cap},{int(48 * s)},{sand},{sand},{hex_ass(c.get('bg', '#0e1114'), '40')},&H00000000,0,0,0,0,100,100,1,0,3,{max(3, int(14 * s))},0,7,0,0,0,1",
        f"Style: Pointer,{cap},{int(50 * s)},{txt},{txt},{acc},&H00000000,0,0,0,0,100,100,1,0,3,{max(3, int(14 * s))},0,9,0,0,0,1",
        f"Style: LockMoment,{f['display']},{int(96 * s)},{txt},{txt},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        f"Style: Hand,{cap},{int(84 * s)},{txt},{txt},{acc},&H00000000,0,0,0,0,100,100,2,0,3,{max(4, int(22 * s))},0,2,0,0,0,1",
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


def text_events(L: dict, words, segs, speech_end, total, W, H, brand, scenes: list[dict]) -> tuple[list[str], list[dict], list[float]]:
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
        ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Plate,,0,0,0,,{{\\an7\\pos({x0 + pad},{y2 + int(22 * s)})\\1c{gold}\\bord0\\shad0\\fad(0,250)\\p1}}m 0 0 l {int(120 * s)} 0 l {int(120 * s)} {max(2, int(3 * s))} l 0 {max(2, int(3 * s))}{{\\p0}}")
        ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockBig,,0,0,0,,{{\\an7\\pos({x0 + pad - int(4 * s)},{y2 + int(36 * s)})\\fad(0,250)}}{lk.get('big', '')}")
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
            ev.append(f"Dialogue: 5,{ts(t)},{ts(t + hold)},Pointer,,0,0,0,,{{\\an9\\move({x + int(60 * H / 1080)},{y},{x},{y},0,200)\\fad(150,150)}}{ch['text']}")
        else:
            st = "ChipQuiet" if kind == "quiet" else "Chip"
            x, y = int(W * ch.get("x", 0.69)), int(H * (ch.get("y", 0.40) + 0.095 * int(ch.get("row", 0))))
            ev.append(f"Dialogue: 5,{ts(t)},{ts(t + hold)},{st},,0,0,0,,{{\\an7\\move({x + int(70 * H / 1080)},{y},{x},{y},0,170)\\fad(120,200)}}{ch['text']}")
        chip_t.append(t)
    for m in L.get("moments", []):
        a, b = A(m["from"]), A(m["to"])
        moments.append({"a": a, "b": b, "style": m.get("style", "bw"), "saturation": float(m.get("saturation", 0.25))})
        if m.get("card"):           # one line in the lockup's proof position, on glass
            s = H / 1080
            x0, w, y2 = int(70 * s), int(650 * s), int((96 + 420 + 14) * s)
            ev += _glass(x0, y2, w, int(150 * s), s, brand, a, b, "\\fad(150,200)")
            ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},LockMoment,,0,0,0,,{{\\an7\\pos({x0 + int(30 * s)},{y2 + int(16 * s)})\\fad(150,200)}}{m['card']}")
        lines = m.get("lines") or []
        x, y = m.get("pos", [0.24, 0.40])
        for i, ln in enumerate(lines):
            ta = a + 0.35 * i
            st = "Moment" if i == 0 else "Moment2"
            anim = "\\fscx112\\fscy112\\t(0,160,\\fscx100\\fscy100)" if i == 0 else ""
            ev.append(f"Dialogue: 6,{ts(ta)},{ts(b)},{st},,0,0,0,,{{\\an5\\pos({int(W * x)},{int(H * (y + 0.10 * i))})\\fad(120,180){anim}}}{ln}")
    return ev, moments, chip_t


def hand_events(L: dict, an: dict, segs: list[dict], cam: dict | None, W: int, H: int, push: float, ky: float,
                words, speech_end, total) -> list[str]:
    """Labels that ride a tracked hand (a rows file: [{"t": take seconds, "hands": [{"side", "cx", "top", "px"}]}]).
    Each label appears on its anchor word and leaves when the hand drops or disappears."""
    hd = L.get("hands")
    if not hd or not cam:
        return []
    path = Path(hd["file"]) if Path(hd["file"]).is_absolute() else Path(L["_base"]) / hd["file"]
    rows = sorted(json.loads(path.read_text()), key=lambda r: r["t"])
    ranges = [r for r in an.get("beats", []) if r["take"] == hd["take"]]
    labels = {side: (text, anchor(words, segs, at, speech_end, total)) for side, (text, at) in hd["labels"].items()}
    min_px, s = float(hd.get("min_px", 2500)), H / 1080
    sw, sh, fps = an["w"], an["h"], cam["fps"]
    ev, last, born, gone, peak = [], {}, {}, {}, {}
    for row in rows:
        rr = [r for r in ranges if r["src_in"] <= row["t"] < r["src_out"]]
        if not rr:
            continue
        t_sel = rr[0]["sel_in"] + row["t"] - rr[0]["src_in"]
        sg = next((g for g in segs if g["in"] <= t_sel < g["in"] + g["frames"] / FPS), None)
        if sg is None:
            continue
        tau, D, z = t_sel - sg["in"], sg["frames"] / FPS, sg["zoom"]
        t_out = sg["out_t"] + tau
        i = min(cam["n"] - 1, int(round(t_sel * fps)))
        x0, y0 = cam["rects"][i][0], cam["rects"][i][1]
        cw, ch = cam["rects"][min(cam["n"] - 1, int(round(sg["in"] * fps)))][2:4]
        k = 1.02 + push * tau / D + (0.08 * max(0.0, 1 - tau / 0.27) ** 2 if sg.get("kick_in") else 0.0)
        sc = W * k / (cw / z)
        seen = {h["side"]: h for h in row["hands"] if h.get("px", 1e9) >= min_px}
        for side, (text, t_on) in labels.items():
            if t_out < t_on:
                continue
            h = seen.get(side)
            if h:
                gone[side] = 0
                px, py = h["cx"] * sw - x0 - (cw - cw / z) / 2, h["top"] * sh - y0 - (ch - ch / z) * ky
                x = px * sc - (W * k - W) / 2
                y = py * sc - ((ch / z) * sc - H) * 0.4 - 40 * s
                peak[side] = min(peak.get(side, y), y)
                if y > peak[side] + 0.10 * H:           # the hand is coming down: the label holds, then leaves
                    gone[side] = gone.get(side, 0) + 2
                    if gone[side] > 4:
                        continue
                    x, y = last.get(side, (x, y))
                elif side in last:
                    lx, ly = last[side]
                    x, y = lx + max(-24, min(24, 0.25 * (x - lx))), ly + max(-24, min(24, 0.25 * (y - ly)))
                last[side] = (x, y)
            else:
                gone[side] = gone.get(side, 0) + 1
                if gone[side] > 4 or side not in last:
                    continue
            x, y = last[side]
            x = max(0.10 * W, min(0.90 * W, x)); y = max(0.14 * H, y)     # keep the label box inside the frame
            born.setdefault(side, t_out)
            kk = min(1.0, (t_out - born[side]) / (7 / FPS))
            pc = int(100 * (0.55 + 0.45 * (1 - (1 - kk) ** 3)))
            ev.append(f"Dialogue: 1,{ts(t_out)},{ts(t_out + 1 / FPS)},Hand,,0,0,0,,{{\\pos({x:.0f},{y:.0f})\\fscx{pc}\\fscy{pc}}}{text}")
    return ev
