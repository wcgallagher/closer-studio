"""Placement: where a label, chip, pop-up or card goes, decided from what is on screen at that moment.

A human editor never types coordinates; they look at the frame and put the text where the eye can take it without
covering what matters. This module does the same in numbers:

  occupancy   the speaker's face (with headroom), torso, tracked hands, the caption band while captions show,
              everything already placed, and the platform's UI zones, all mapped onto the output frame over time
  candidates  every position on a grid inside the format's safe area (16:9 web, YouTube, 9:16 reels, 1:1, 4:5)
  cost        face overlap (a hard fail), captions and other overlays, hands (unless the label belongs to that hand),
              distance from what the label points at, a busy or too-bright background under plain text, and moving
              away from where the same group sat a moment ago (things that belong together stay put)
  result      the best box and a report; anything that still touches the face or the captions is flagged for review

Every weight is in PLACEMENT_RULES so the skill file and the review quote the same numbers.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .common import FPS

PLACEMENT_RULES = {
    "safe": {   # margins as fractions of the frame (x0, y0, x1, y1) where text may sit
        "16:9": (0.045, 0.06, 0.955, 0.94),
        "9:16": (0.06, 0.12, 0.84, 0.70),       # reels/shorts: the right rail and the bottom caption and handle area stay clear
        "1:1": (0.06, 0.06, 0.94, 0.90),
        "4:5": (0.06, 0.06, 0.94, 0.86),
    },
    "grid_step": 0.02,
    "weights": {"face": 60.0, "headroom": 14.0, "torso": 2.0, "hands": 8.0, "captions": 40.0, "overlays": 40.0, "ui": 25.0,
                "near": 6.0, "busy": 2.5, "bright": 6.0, "sticky": 4.0, "edge_hug": 1.0, "home": 5.0},
    # where a group lives when nothing pulls it elsewhere: the open side of the frame (the side with more room beside the
    # face), halfway between the face and the safe edge, at eye height (chips) or a little lower (stats)
    "home": {"chips": {"side": "open", "x": 0.5, "y_from_eyes": 0.05}, "stats": {"side": "open", "x": 0.45, "y_from_eyes": 0.12}},
    "face_fail_overlap": 0.02,          # share of the box over the face that fails review
    "bright_text_luma": 0.62,           # plain white text over a mean luma above this needs a plate
    "sample_hz": 5,
}


def aspect_key(W: int, H: int) -> str:
    r = W / H
    return "16:9" if r > 1.5 else "9:16" if r < 0.7 else "4:5" if r < 0.9 else "1:1"


# ---------------------------------------------------------------- source -> output mapping


class Mapper:
    """Maps a point on the source frame (normalised 0-1) to output pixels at an output time, through the same crop,
    zoom, push and kick that render.piece_jobs applies to each piece."""

    def __init__(self, an: dict, segs: list[dict], cam: dict | None, W: int, H: int, push: float, ky: float):
        self.an, self.segs, self.cam, self.W, self.H, self.push, self.ky = an, segs, cam, W, H, push, ky
        self.sw, self.sh = an["w"], an["h"]

    def seg_at(self, t_out: float):
        for sg in self.segs:
            if sg["out_t"] - 1e-6 <= t_out < sg["out_t"] + sg["frames"] / FPS:
                return sg
        return None

    def src_time(self, t_out: float) -> float | None:
        sg = self.seg_at(t_out)
        return None if sg is None else sg["in"] + (t_out - sg["out_t"])

    def at(self, t_out: float):
        """(to_out(xn, yn) -> (x, y), scale px-per-source-px) at an output time, or None outside the cut."""
        sg = self.seg_at(t_out)
        if sg is None:
            return None
        tau, D, z = t_out - sg["out_t"], sg["frames"] / FPS, sg["zoom"]
        W, H = self.W, self.H
        if self.cam:
            fps, n = self.cam["fps"], self.cam["n"]
            t_sel = sg["in"] + tau
            x0, y0 = self.cam["rects"][min(n - 1, int(round(t_sel * fps)))][:2]
            cw, ch = self.cam["rects"][min(n - 1, int(round(sg["in"] * fps)))][2:4]
        else:
            ar = W / H
            ch, cw = self.sh, self.sh * ar
            if cw > self.sw:
                cw, ch = self.sw, self.sw / ar
            x0, y0 = (self.sw - cw) / 2, (self.sh - ch) * 0.38
        k = 1.02 + self.push * tau / D + (0.08 * max(0.0, 1 - tau / 0.27) ** 2 if sg.get("kick_in") else 0.0)
        sc = W * k / (cw / z)

        def to_out(xn, yn):
            px = xn * self.sw - x0 - (cw - cw / z) / 2
            py = yn * self.sh - y0 - (ch - ch / z) * self.ky
            return px * sc - (W * k - W) / 2, py * sc - ((ch / z) * sc - H) * 0.4
        return to_out, sc

    def rect(self, t_out: float, l: float, t: float, r: float, b: float):
        m = self.at(t_out)
        if m is None:
            return None
        f, _ = m
        (x0, y0), (x1, y1) = f(l, t), f(r, b)
        return (x0, y0, x1, y1)


def face_track(an: dict) -> tuple[np.ndarray, np.ndarray]:
    d = [x for x in an.get("track", {}).get("dets", []) if "cx" in x]
    if not d:
        return np.zeros(0), np.zeros((0, 4))
    return np.array([x["t"] for x in d]), np.array([[x["cx"], x["cy"], x["fw"], x["fh"]] for x in d])


# ---------------------------------------------------------------- the frame at a moment


@dataclass
class Scene:
    W: int
    H: int
    mapper: Mapper | None
    face_t: np.ndarray
    face_v: np.ndarray
    captions: list = field(default_factory=list)       # (a, b, (x0, y0, x1, y1))
    overlays: list = field(default_factory=list)       # (a, b, rect, group)
    hands: list = field(default_factory=list)          # (a, b, rect)
    frames: object = None                              # callable t -> small grey frame (0-1) or None
    history: dict = field(default_factory=dict)        # group -> [(t, rect)]
    report: list = field(default_factory=list)

    def face_rect(self, t_out: float):
        if self.mapper is None or not len(self.face_t):
            return None
        ts = self.mapper.src_time(t_out)
        if ts is None:
            return None
        i = int(np.clip(np.searchsorted(self.face_t, ts) - 1, 0, len(self.face_t) - 1))
        cx, cy, fw, fh = self.face_v[i]
        return self.mapper.rect(t_out, cx - fw / 2, cy - fh / 2, cx + fw / 2, cy + fh / 2)


def _ov(a, b):
    """Overlap area of two rects (x0, y0, x1, y1)."""
    w = min(a[2], b[2]) - max(a[0], b[0]); h = min(a[3], b[3]) - max(a[1], b[1])
    return max(0.0, w) * max(0.0, h)


def _grow(r, gx, gy_up, gy_down=None):
    w, h = r[2] - r[0], r[3] - r[1]
    return (r[0] - w * gx, r[1] - h * gy_up, r[2] + w * gx, r[3] + h * (gy_down if gy_down is not None else gy_up))


def place(sc: Scene, w: int, h: int, a: float, b: float, group: str = "", near=None, style: str = "plate",
          region=None, fixed=None, label: str = "") -> tuple[int, int, dict]:
    """Best top-left (x, y) for a w x h box on screen from a to b. near: a rect to sit next to (a hand, a chart);
    region: (x0, y0, x1, y1) fractions to search in; style 'plain' text cares about the background, 'plate' less so."""
    R = PLACEMENT_RULES
    Wt = R["weights"]
    W, H = sc.W, sc.H
    if fixed is not None:
        x, y = fixed
        rep = {"label": label, "a": round(a, 2), "b": round(b, 2), "rect": [x, y, x + w, y + h], "fixed": True}
        sc.report.append(rep)
        sc.overlays.append((a, b, (x, y, x + w, y + h), group))
        return x, y, rep
    sx0, sy0, sx1, sy1 = R["safe"][aspect_key(W, H)]
    if region:
        sx0, sy0, sx1, sy1 = max(sx0, region[0]), max(sy0, region[1]), min(sx1, region[2]), min(sy1, region[3])
    step = R["grid_step"]
    xs = np.arange(sx0 * W, max(sx0 * W + 1, sx1 * W - w + 1), step * W)
    ys = np.arange(sy0 * H, max(sy0 * H + 1, sy1 * H - h + 1), step * H)
    times = np.arange(a, max(a + 1e-3, b), 1 / R["sample_hz"]) if b > a else np.array([a])
    faces = [f for f in (sc.face_rect(t) for t in times) if f]
    caps = [c[2] for c in sc.captions if c[0] < b and c[1] > a]
    ovs = [o[2] for o in sc.overlays if o[0] < b and o[1] > a]
    hands = [x[2] for x in sc.hands if x[0] < b and x[1] > a]
    if near is not None:
        hands = [hh for hh in hands if _ov(hh, near) < 0.5 * max(1, (near[2] - near[0]) * (near[3] - near[1]))]
    prev = [r for t, r in sc.history.get(group, []) if a - t < 8.0] if group else []
    lum = None
    if style == "plain" and sc.frames is not None:
        fr = [sc.frames(t) for t in (a, (a + b) / 2)]
        fr = [f for f in fr if f is not None]
        lum = np.mean(fr, 0) if fr else None
    home = None
    hz = R.get("home", {}).get(group)
    if hz and faces and near is None:
        fx0 = float(np.median([f[0] for f in faces])); fx1 = float(np.median([f[2] for f in faces]))
        eyes = float(np.median([f[1] + 0.4 * (f[3] - f[1]) for f in faces]))
        left_room, right_room = fx0 - sx0 * W, sx1 * W - fx1
        if left_room >= right_room:
            hx = sx0 * W + (fx0 - sx0 * W) * hz["x"]
        else:
            hx = fx1 + (sx1 * W - fx1) * (1 - hz["x"])
        home = (hx, eyes + hz["y_from_eyes"] * H)
    best, bc, bd = None, 1e18, {}
    area = w * h
    for y in ys:
        for x in xs:
            r = (x, y, x + w, y + h)
            d = {}
            if faces:
                fo = max(_ov(r, f) for f in faces) / area
                ho = max(_ov(r, _grow(f, 0.25, 0.45, 0.0)) for f in faces) / area
                to = max(_ov(r, (f[0] - (f[2] - f[0]) * 0.9, f[3], f[2] + (f[2] - f[0]) * 0.9, H)) for f in faces) / area
                d["face"], d["headroom"], d["torso"] = fo * Wt["face"], ho * Wt["headroom"], to * Wt["torso"]
            if caps:
                d["captions"] = max(_ov(r, c) for c in caps) / area * Wt["captions"]
            if ovs:
                d["overlays"] = max(_ov(r, o) for o in ovs) / area * Wt["overlays"]
            if hands:
                d["hands"] = max(_ov(r, hh) for hh in hands) / area * Wt["hands"]
            if near is not None:
                cxn, cyn = (near[0] + near[2]) / 2, (near[1] + near[3]) / 2
                dx = max(near[0] - r[2], 0, r[0] - near[2]); dy = max(near[1] - r[3], 0, r[1] - near[3])
                d["near"] = (np.hypot(dx, dy) / W) * Wt["near"] * 10 + abs((x + w / 2) - cxn) / W * Wt["near"]
                d["near"] += _ov(r, near) / area * Wt["near"] * 0.5        # beside the hand, not on it
            if lum is not None:
                gh, gw = lum.shape
                patch = lum[int(y / H * gh): max(int(y / H * gh) + 1, int((y + h) / H * gh)), int(x / W * gw): max(int(x / W * gw) + 1, int((x + w) / W * gw))]
                d["busy"] = float(patch.std()) * Wt["busy"] * 4
                d["bright"] = max(0.0, float(patch.mean()) - R["bright_text_luma"]) * Wt["bright"] * 4
            if prev:
                d["sticky"] = min(np.hypot(r[0] - p[0], r[1] - p[1]) for p in prev) / W * Wt["sticky"]
            if home is not None:
                d["home"] = np.hypot((x + w / 2) - home[0], (y + h / 2) - home[1]) / W * Wt["home"]
            c = sum(d.values())
            if c < bc:
                best, bc, bd = r, c, d
    x, y = int(round(best[0])), int(round(best[1]))
    rect = (x, y, x + w, y + h)
    face_hit = max((_ov(rect, f) for f in faces), default=0) / area
    cap_hit = max((_ov(rect, c) for c in caps), default=0) / area
    rep = {"label": label, "group": group, "a": round(a, 2), "b": round(b, 2), "rect": [x, y, x + w, y + h], "cost": round(bc, 3),
           "terms": {k: round(v, 3) for k, v in bd.items() if v > 0.001}, "face_overlap": round(face_hit, 3), "caption_overlap": round(cap_hit, 3),
           "ok": face_hit <= R["face_fail_overlap"] and cap_hit <= 0.01}
    sc.report.append(rep)
    sc.overlays.append((a, b, rect, group))
    if group:
        sc.history.setdefault(group, []).append((a, rect))
    return x, y, rep


def frame_sampler(video: Path, W: int, H: int, gw: int = 96):
    """t -> grey frame (gw x gw*H/W, 0-1) from the output base video; cached per 0.1 s."""
    cache = {}
    gh = max(1, int(gw * H / W))

    def get(t: float):
        k = round(t, 1)
        if k not in cache:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, k):.2f}", "-i", str(video), "-frames:v", "1",
                                  "-vf", f"scale={gw}:{gh},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
            cache[k] = np.frombuffer(raw, np.uint8).reshape(gh, gw) / 255.0 if len(raw) == gw * gh else None
        return cache[k]
    return get


def text_box(text: str, font_file: Path | None, size: int, pad_x: int = 0, pad_y: int = 0, tracking: float = 0.0) -> tuple[int, int]:
    """Pixel size of one or more lines of text in a font (PIL), plus padding. Falls back to an estimate."""
    lines = text.replace("\\N", "\n").split("\n")
    try:
        from PIL import ImageFont
        f = ImageFont.truetype(str(font_file), size) if font_file else None
    except Exception:
        f = None
    ws = []
    for ln in lines:
        if f:
            b = f.getbbox(ln)
            ws.append(b[2] - b[0] + tracking * size * max(0, len(ln) - 1))
        else:
            ws.append(len(ln) * size * 0.62)
    return int(max(ws) + 2 * pad_x), int(len(lines) * size * 1.18 + 2 * pad_y)


def write_report(sc: Scene, path: Path):
    path.write_text(json.dumps({"rules": PLACEMENT_RULES, "placed": sc.report}, indent=1, default=float))
