"""Compare two edits of the same video, side by side, with numbers: `closer.py compare A.mp4 B.mp4 --out dir`.

Writes compare.json (every measure for both) and compare.html, a page that plays both cuts in sync with a wipe and a
difference view, and draws their timelines over each other: cuts, loudness (momentary and short-term), voice quality
(DNSMOS when installed), picture (luma, contrast, saturation, clipped highlights), motion, face on screen, and a
filmstrip. A blind judge's verdict (judge.json) is shown when present. Nothing here listens; it measures.
"""
from __future__ import annotations

import base64
import html
import json
import subprocess
from pathlib import Path

import numpy as np

from . import sound
from .common import HERE

COMPARE_RULES = {"sample_fps": 4, "thumb_every_s": 2.0, "thumb_w": 240, "web_w": 960, "web_crf": 30}


def _probe(path: Path) -> dict:
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate,codec_type",
                                   "-of", "json", str(path)], capture_output=True, text=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    n, d = v["r_frame_rate"].split("/")
    return {"duration": float(j["format"]["duration"]), "w": v["width"], "h": v["height"], "fps": float(n) / float(d)}


def picture(path: Path, fps: float) -> dict:
    """Per-sample picture stats at 160 px: luma, contrast, saturation, clipped share, motion, and cuts (scene change)."""
    w, h = 160, 90
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.float32) / 255
    L = fr @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    sat = fr.max(-1) - fr.min(-1)
    mot = np.r_[0, np.abs(np.diff(L, axis=0)).mean((1, 2))]
    return {"t": [round(i / fps, 2) for i in range(len(fr))], "luma": L.mean((1, 2)).round(3).tolist(), "contrast": L.std((1, 2)).round(3).tolist(),
            "sat": sat.mean((1, 2)).round(3).tolist(), "clip": (L > 0.98).mean((1, 2)).round(4).tolist(), "motion": mot.round(4).tolist()}


def cuts(path: Path) -> list[float]:
    """Every cut, punch-ins included: a frame whose difference from the last one spikes over its neighbours
    (at least 5x the local median and 0.025 of full scale), at the native frame rate on a 96 px proxy."""
    fps = _probe(path)["fps"]
    w, h = 96, 54
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32) / 255
    d = np.r_[0, np.abs(np.diff(fr, axis=0)).mean((1, 2))]
    out = []
    for i in range(1, len(d)):
        nb = np.r_[d[max(1, i - 6):i], d[i + 1:i + 7]]
        if d[i] > 0.025 and d[i] > 5 * (np.median(nb) + 1e-4) and (not out or i / fps - out[-1] > 0.2):
            out.append(round(i / fps, 3))
    return out


def faces(path: Path, every: float = 0.5) -> dict:
    """Share of samples with a face and the face height (YuNet, MIT, already in the kit)."""
    import cv2
    model = HERE / "models" / "face_detection_yunet_2023mar.onnx"
    w, h = 640, 360
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={1 / every},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    det = cv2.FaceDetectorYN.create(str(model), "", (w, h), 0.7)
    on, fh = [], []
    for f in fr:
        _, d = det.detect(np.ascontiguousarray(f))
        on.append(1 if d is not None and len(d) else 0)
        fh.append(round(float(d[0][3] / h), 3) if d is not None and len(d) else 0)
    return {"every": every, "on": on, "face_h": fh, "share": round(float(np.mean(on)) if on else 0, 3)}


def audio(path: Path) -> dict:
    y = sound.read_audio(path, mono=False)
    t, m = sound.loudness_curve(y, win_s=0.4, hop_s=0.1)
    ts, s = sound.loudness_curve(y, win_s=3.0, hop_s=0.5)
    out = {"lufs": round(sound.lufs(y), 1), "true_peak": round(sound.true_peak_db(y), 1),
           "momentary": {"t": t[::2].round(2).tolist(), "v": np.maximum(m[::2], -60).round(1).tolist()},
           "short": {"t": ts.round(2).tolist(), "v": np.maximum(s, -60).round(1).tolist()}}
    sl = s[s > -50]
    out["lra_approx"] = round(float(np.percentile(sl, 95) - np.percentile(sl, 10)), 1) if len(sl) > 4 else None
    try:
        from speechmos import dnsmos
        y16 = sound.read_audio(path, sr=16000)
        y16 = y16 / (np.abs(y16).max() + 1e-9) * 0.9
        w = int(9.01 * 16000)
        starts = list(range(0, max(1, len(y16) - w + 1), w)) or [0]
        rs = [dnsmos.run(y16[i:i + w] if len(y16) >= w else np.resize(y16, w), sr=16000) for i in starts]
        out["dnsmos"] = {k: round(float(np.mean([r[k] for r in rs])), 2) for k in ("sig_mos", "bak_mos", "ovrl_mos", "p808_mos")}
        out["dnsmos"]["note"] = "DNSMOS on the full mix (voice plus music and effects); music lowers BAK by design"
    except Exception as e:  # optional
        out["dnsmos"] = {"note": f"not installed ({type(e).__name__})"}
    return out


def thumbs(path: Path, dur: float, every: float, w: int) -> list[str]:
    out = []
    t = 0.0
    while t < dur - 0.05:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "image2", "-c:v", "mjpeg", "-q:v", "6", "-"],
                             capture_output=True).stdout
        out.append("data:image/jpeg;base64," + base64.b64encode(raw).decode())
        t += every
    return out


def web_copy(path: Path, dst: Path, w: int, crf: int) -> Path:
    if not dst.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf", f"scale={w}:-2", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                        "-g", "30", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)], check=True)
    return dst


def measure(path: Path, log=print) -> dict:
    p = _probe(path)
    log(f"compare: measuring {path.name} ({p['duration']:.1f} s)")
    pic = picture(path, COMPARE_RULES["sample_fps"])
    cs = cuts(path)
    shots = np.diff([0.0] + cs + [p["duration"]])
    return {"file": str(path), "probe": p, "picture": pic, "cuts": cs,
            "shots": {"n": int(len(shots)), "mean_s": round(float(shots.mean()), 2), "median_s": round(float(np.median(shots)), 2),
                      "max_s": round(float(shots.max()), 2), "per_min": round(len(cs) / max(p["duration"] / 60, 0.01), 1)},
            "faces": faces(path), "audio": audio(path)}


def run(a: Path, b: Path, out: Path, labels=("A", "B"), log=print) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    ma, mb = measure(a, log), measure(b, log)
    data = {"labels": list(labels), "a": ma, "b": mb}
    judge = out / "judge.json"
    if judge.exists():
        data["judge"] = json.loads(judge.read_text())
    (out / "compare.json").write_text(json.dumps(data))
    wa = web_copy(a, out / "a.mp4", COMPARE_RULES["web_w"], COMPARE_RULES["web_crf"])
    wb = web_copy(b, out / "b.mp4", COMPARE_RULES["web_w"], COMPARE_RULES["web_crf"])
    ta = thumbs(a, ma["probe"]["duration"], COMPARE_RULES["thumb_every_s"], COMPARE_RULES["thumb_w"])
    tb = thumbs(b, mb["probe"]["duration"], COMPARE_RULES["thumb_every_s"], COMPARE_RULES["thumb_w"])
    tpl = (HERE / "compare_template.html").read_text()
    safe = lambda o: json.dumps(o, allow_nan=False, default=str).replace("<", "\\u003c")
    data["thumb_every_s"] = COMPARE_RULES["thumb_every_s"]
    page = tpl.replace("/*DATA*/null", safe(data)).replace("/*THUMBS*/null", safe({"a": ta, "b": tb})) \
              .replace("{{LA}}", html.escape(labels[0])).replace("{{LB}}", html.escape(labels[1])) \
              .replace("{{SRC_A}}", wa.name).replace("{{SRC_B}}", wb.name)
    (out / "compare.html").write_text(page)
    log(f"compare: {out / 'compare.html'}")
    return out / "compare.html"
