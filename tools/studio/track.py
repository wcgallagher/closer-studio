"""Face tracking and the smoothed virtual camera behind auto-reframe.

How it works (and where the ideas come from):
- Faces: OpenCV's YuNet detector (face_detection_yunet_2023mar.onnx, Apache-2.0, from opencv/opencv_zoo), run on a
  960 px analysis copy of the frames that ffmpeg pipes in, every `stride`-th frame. No MediaPipe, no YOLO, no GPU.
- Cuts: a mean-absolute-difference content detector on a 96x54 thumbnail, the same idea as PySceneDetect's
  ContentDetector. The camera snaps at a cut instead of panning across it.
- Camera: a critically damped spring per axis with a dead zone, so the crop only moves when the face really moves and
  never overshoots (the approach supoclip's vertical pipeline and Opus-style tools use), plus a velocity clamp.
  Zoom is chosen once per scene from the median face height, so the frame never "breathes".
- Output: the camera path compiled into ffmpeg crop x/y expressions (piecewise linear between keyframes every 0.2 s,
  evaluated by the crop filter itself per frame). Render time runs zero Python per frame, the idea videopython's
  FaceTrackingCrop documents with sendcmd; expressions turned out far faster than per-frame commands, which make
  ffmpeg reconfigure the filter on every frame.
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import numpy as np

from .common import MODELS, even, probe

YUNET = MODELS / "face_detection_yunet_2023mar.onnx"
AW = 960


def iter_frames(video, start: float, dur: float, fps: float, aw: int = AW):
    info = probe(video)
    ah = even(info["h"] * aw / info["w"])
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(video),
           "-vf", f"fps={fps},scale={aw}:{ah}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=aw * ah * 3 * 4)
    n, sz = 0, aw * ah * 3
    try:
        while True:
            buf = p.stdout.read(sz)
            if len(buf) < sz:
                break
            yield n, n / fps, np.frombuffer(buf, np.uint8).reshape(ah, aw, 3)
            n += 1
    finally:
        p.stdout.close()
        p.wait()


def detect(video, start: float = 0.0, dur: float | None = None, stride: int = 2, fps: float = 30.0,
           score: float = 0.6, log=print) -> dict:
    """Faces and cuts over [start, start+dur]. Returns normalised (0..1) face centres and sizes per sampled frame."""
    import cv2
    info = probe(video)
    if dur is None:
        dur = info["dur"] - start
    aw = AW
    ah = even(info["h"] * aw / info["w"])
    det = cv2.FaceDetectorYN.create(str(YUNET), "", (aw, ah), score, 0.3, 50)
    dets, cuts, prev, last_small, last_cut = [], [], None, None, -9.0
    for n, t, fr in iter_frames(video, start, dur, fps, aw):
        small = cv2.resize(fr, (96, 54), interpolation=cv2.INTER_AREA).astype(np.float32)
        if last_small is not None:
            d = float(np.abs(small - last_small).mean())
            if d > 28.0 and t - last_cut > 0.4:
                cuts.append(round(t, 3))
                last_cut = t
        last_small = small
        if n % stride:
            continue
        _, faces = det.detect(fr)
        if faces is None or len(faces) == 0:
            dets.append({"t": round(t, 3)})
            continue
        best, best_s = None, -1e9
        for f in faces:
            x, y, w, h, sc = float(f[0]), float(f[1]), float(f[2]), float(f[3]), float(f[14])
            cx, cy = (x + w / 2) / aw, (y + h / 2) / ah
            s = sc + 0.8 * (w * h) / (aw * ah) * 10
            if prev is not None:
                s -= 2.5 * math.hypot(cx - prev[0], cy - prev[1])
            if s > best_s:
                best_s, best = s, (cx, cy, w / aw, h / ah, sc)
        prev = best[:2]
        dets.append({"t": round(t, 3), "cx": round(best[0], 4), "cy": round(best[1], 4),
                     "fw": round(best[2], 4), "fh": round(best[3], 4), "score": round(best[4], 3)})
        if n % (stride * 150) == 0 and log:
            log(f"  tracked {t:.0f}/{dur:.0f} s")
    found = sum(1 for d in dets if "cx" in d)
    return {"video": str(video), "start": start, "dur": dur, "fps": fps, "w": info["w"], "h": info["h"],
            "stride": stride, "dets": dets, "cuts": cuts, "coverage": round(found / max(1, len(dets)), 3)}


def camera(track: dict, out_w: int, out_h: int, zoom="auto", face_y: float = 0.40, zmax: float = 1.30,
           f_hz: float = 0.7, dead=(0.025, 0.035), vmax: float = 0.9, upscale: float = 1.15, per_scene: bool = False) -> dict:
    """Per-frame crop rectangles (even ints, source pixels) for an out_w:out_h output.
    zoom: "auto" (from the median face height), or a number. per_scene=False keeps one crop size for the whole span."""
    w, h, fps = track["w"], track["h"], track["fps"]
    ar = out_w / out_h
    cw0, ch0 = h * ar, float(h)
    if cw0 > w:
        cw0, ch0 = float(w), w / ar
    n = max(1, int(round(track["dur"] * fps)))
    times = np.arange(n) / fps
    dets = [d for d in track["dets"] if "cx" in d]
    if dets:
        dt = np.array([d["t"] for d in dets])
        cx, cy, fh = (np.array([d[k] for d in dets]) for k in ("cx", "cy", "fh"))
        idx = np.clip(np.searchsorted(dt, times, side="right") - 1, 0, len(dets) - 1)
        tx, ty, tfh = cx[idx], cy[idx], fh[idx]
    else:
        tx, ty, tfh = np.full(n, 0.5), np.full(n, 0.42), np.full(n, 0.22)
    bounds = [0.0] + [c for c in track["cuts"] if 0 < c < track["dur"]] + [track["dur"]]
    cut_frames = {int(round(c * fps)) for c in bounds[1:-1]}
    # zoom per scene (or one value for the whole span)
    zs = np.ones(n)
    zoom_spans = list(zip(bounds[:-1], bounds[1:])) if per_scene else [(0.0, track["dur"])]
    for a, b in zoom_spans:
        i0, i1 = int(round(a * fps)), max(int(round(a * fps)) + 1, int(round(b * fps)))
        if zoom == "auto":
            med = float(np.median(tfh[i0:i1])) if dets else 0.22
            want = 0.27                                   # face height as a fraction of the output frame
            z = want * ch0 / max(med * h, 1.0)
            cap = max(1.0, min(zmax, (cw0 / out_w) * upscale))
            zs[i0:i1] = float(np.clip(z, 1.0, cap))
        else:
            zs[i0:i1] = float(zoom)
    # spring
    k = (2 * math.pi * f_hz) ** 2
    c = 2 * math.sqrt(k)
    dt_ = 1.0 / fps
    x, y, vx, vy = float(tx[0]), float(ty[0]), 0.0, 0.0
    xt, yt = x, y
    rects = np.zeros((n, 4), np.int32)
    for i in range(n):
        if i in cut_frames:
            x, y, vx, vy = float(tx[i]), float(ty[i]), 0.0, 0.0
            xt, yt = x, y
        if abs(tx[i] - xt) > dead[0]:
            xt = float(tx[i])
        if abs(ty[i] - yt) > dead[1]:
            yt = float(ty[i])
        ax, ay = k * (xt - x) - c * vx, k * (yt - y) - c * vy
        vx = max(-vmax, min(vmax, vx + ax * dt_))
        vy = max(-vmax, min(vmax, vy + ay * dt_))
        x += vx * dt_
        y += vy * dt_
        cw, ch = cw0 / zs[i], ch0 / zs[i]
        x0 = min(max(x * w - cw / 2, 0.0), w - cw)
        y0 = min(max(y * h - face_y * ch, 0.0), h - ch)
        rects[i] = (even(x0), even(y0), even(cw), even(ch))
    return {"fps": fps, "n": n, "w": w, "h": h, "out_w": out_w, "out_h": out_h, "rects": rects.tolist(),
            "zoom": [round(float(z), 3) for z in zs[[int(round(a * fps)) for a, _ in zoom_spans]]], "cuts": bounds[1:-1]}


def face_box_out(track: dict, cam: dict, t: float) -> tuple[float, float, float, float] | None:
    """Face box in output pixels at time t (x, y, w, h), for caption clearance checks."""
    dets = [d for d in track["dets"] if "cx" in d]
    if not dets:
        return None
    d = min(dets, key=lambda d: abs(d["t"] - t))
    i = min(cam["n"] - 1, max(0, int(round(t * cam["fps"]))))
    x0, y0, cw, ch = cam["rects"][i]
    sx, sy = cam["out_w"] / cw, cam["out_h"] / ch
    fx, fy = d["cx"] * track["w"], d["cy"] * track["h"]
    fw, fh = d["fw"] * track["w"], d["fh"] * track["h"]
    return ((fx - fw / 2 - x0) * sx, (fy - fh / 2 - y0) * sy, fw * sx, fh * sy)


def crop_exprs(cam: dict, t0: float = 0.0, t1: float | None = None, step: float = 0.2) -> tuple[int, int, str, str]:
    """(w, h, x_expr, y_expr) for the span [t0, t1): piecewise-linear keyframes in `t` (seconds from the span start).
    The crop size is the span's first rectangle (crop w/h are evaluated once; x/y per frame)."""
    fps, rects = cam["fps"], cam["rects"]
    i0 = int(round(t0 * fps))
    i1 = cam["n"] if t1 is None else min(cam["n"], int(round(t1 * fps)))
    i1 = max(i1, i0 + 1)
    cw, ch = rects[i0][2], rects[i0][3]
    keys = list(range(i0, i1, max(1, int(round(step * fps))))) + [i1 - 1]
    keys = sorted(set(keys))

    def expr(axis):
        vals = [rects[i][axis] for i in keys]
        if max(vals) == min(vals):
            return str(vals[0])
        terms = []
        for k in range(len(keys) - 1):
            ta, tb = (keys[k] - i0) / fps, (keys[k + 1] - i0) / fps
            va, vb = vals[k], vals[k + 1]
            slope = (vb - va) / max(tb - ta, 1e-6)
            last = k == len(keys) - 2
            cond = f"gte(t,{ta:.3f})" + ("" if last else f"*lt(t,{tb:.3f})")
            terms.append(f"{cond}*({va}+{slope:.3f}*(t-{ta:.3f}))")
        return "trunc((" + "+".join(terms) + ")/2)*2"
    return cw, ch, expr(0), expr(1)


def vf_track(cam: dict, t0: float = 0.0, t1: float | None = None) -> str:
    cw, ch, xe, ye = crop_exprs(cam, t0, t1)
    return f"crop=w={cw}:h={ch}:x='{xe}':y='{ye}'"


def vf_chain(cam: dict, t0: float = 0.0, t1: float | None = None, flags: str = "lanczos") -> str:
    """Whole reframe chain for a span: tracked crop, then scale to the output size."""
    return f"setpts=PTS-STARTPTS,{vf_track(cam, t0, t1)},scale={cam['out_w']}:{cam['out_h']}:flags={flags},setsar=1"


def save(track: dict, path: Path):
    Path(path).write_text(json.dumps(track))


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text())
