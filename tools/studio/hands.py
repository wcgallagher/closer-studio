"""Hands: where the speaker's hands are, frame by frame, from OpenCV Zoo's MediaPipe palm detector and hand-pose model
(both Apache-2.0, ONNX, run through cv2.dnn: no extra runtime, works on a Mac CPU and in a Linux container).

Each half of the frame (screen left, screen right) is searched on its own so a hand is large at the detector's input;
the palm box seeds the 21-landmark hand model, which gives the true hand extent, a presence score and whether the hand
is fully in frame. Output rows match the layers "hands" file: {"t", "hands": [{"side", "cx", "top", "left", "right",
"bottom", "px", "score", "in_frame"}]} in source-normalised coordinates.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from .common import HERE

MODELS = HERE / "models"
PALM = MODELS / "palm_detection_mediapipe_2023feb.onnx"
POSE = MODELS / "handpose_estimation_mediapipe_2023feb.onnx"
HAND_RULES = {"palm_score": 0.55, "presence": 0.6, "nms_iou": 0.3, "roi_scale": 2.6, "roi_shift": -0.5, "fps": 10,
              "in_frame_margin": 0.03}


def _anchors():
    out = []
    for stride, n in ((8, 2), (16, 6)):
        g = 192 // stride
        for y in range(g):
            for x in range(g):
                out += [((x + 0.5) / g, (y + 0.5) / g)] * n
    return np.array(out, np.float32)


ANCH = _anchors()


class HandFinder:
    def __init__(self):
        import cv2
        self.cv2 = cv2
        self.palm = cv2.dnn.readNet(str(PALM))
        self.pose = cv2.dnn.readNet(str(POSE))

    def _palms(self, rgb):
        cv2 = self.cv2
        h, w = rgb.shape[:2]
        s = 192 / max(h, w)
        nh, nw = int(round(h * s)), int(round(w * s))
        img = np.zeros((192, 192, 3), np.float32)
        oy, ox = (192 - nh) // 2, (192 - nw) // 2
        img[oy:oy + nh, ox:ox + nw] = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        self.palm.setInput(img[None])
        reg, cls = self.palm.forward(self.palm.getUnconnectedOutLayersNames())
        reg, cls = reg[0], cls[0, :, 0]
        score = 1 / (1 + np.exp(-np.clip(cls, -60, 60)))
        keep = np.where(score > HAND_RULES["palm_score"])[0]
        if not len(keep):
            return []
        r = reg[keep] / 192
        c = ANCH[keep]
        cx, cy, bw, bh = r[:, 0] + c[:, 0], r[:, 1] + c[:, 1], r[:, 2], r[:, 3]
        kps = r[:, 4:].reshape(-1, 7, 2) + c[:, None, :]
        boxes = np.stack([cx - bw / 2, cy - bh / 2, bw, bh], 1)
        idx = cv2.dnn.NMSBoxes(boxes.tolist(), score[keep].tolist(), HAND_RULES["palm_score"], HAND_RULES["nms_iou"])
        out = []
        for i in np.array(idx).flatten():
            to_img = lambda p: ((p[..., 0] * 192 - ox) / s, (p[..., 1] * 192 - oy) / s)
            bx = np.array(to_img(np.array([[boxes[i][0], boxes[i][1]], [boxes[i][0] + boxes[i][2], boxes[i][1] + boxes[i][3]]])))
            kx, ky = to_img(kps[i])
            out.append({"score": float(score[keep][i]), "box": (bx[0][0], bx[1][0], bx[0][1], bx[1][1]), "kp": np.stack([kx, ky], 1)})
        return out

    def _landmarks(self, rgb, palm):
        """Rotate and crop the hand around the palm (MediaPipe's palm-to-hand ROI), run the 21-point model."""
        cv2 = self.cv2
        x0, y0, x1, y1 = palm["box"]
        kp = palm["kp"]
        ang = np.pi / 2 - np.arctan2(-(kp[2, 1] - kp[0, 1]), kp[2, 0] - kp[0, 0])
        ang = (ang + np.pi) % (2 * np.pi) - np.pi
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        size = max(x1 - x0, y1 - y0)
        cx += -HAND_RULES["roi_shift"] * size * np.sin(ang) * -1
        cy += HAND_RULES["roi_shift"] * size * np.cos(ang)
        side = size * HAND_RULES["roi_scale"]
        M = cv2.getRotationMatrix2D((float(cx), float(cy)), float(np.degrees(ang)), 224 / side)
        M[:, 2] += (112 - cx, 112 - cy)
        crop = cv2.warpAffine(rgb, M, (224, 224), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0)).astype(np.float32) / 255
        self.pose.setInput(crop[None])
        outs = self.pose.forward(self.pose.getUnconnectedOutLayersNames())
        lm = np.array(outs[0]).reshape(21, 3)[:, :2]
        pres = float(np.array(outs[1]).ravel()[0])
        Mi = cv2.invertAffineTransform(M)
        pts = (np.c_[lm, np.ones(21)] @ Mi.T)
        return pts, pres

    def find(self, frame_rgb) -> list[dict]:
        """Hands on one frame (any size). Screen-left half gives side L, right half side R."""
        H, W = frame_rgb.shape[:2]
        found = []
        for side, x_off in (("L", 0), ("R", W // 2)):
            half = frame_rgb[:, x_off:x_off + W // 2]
            best = None
            for p in self._palms(half):
                try:
                    pts, pres = self._landmarks(half, p)
                except Exception:
                    continue
                if pres < HAND_RULES["presence"]:
                    continue
                if best is None or p["score"] > best[0]["score"]:
                    best = (p, pts, pres)
            if best:
                p, pts, pres = best
                pts = pts + np.array([x_off, 0])
                m = HAND_RULES["in_frame_margin"]
                inside = bool(((pts[:, 0] > m * W) & (pts[:, 0] < (1 - m) * W) & (pts[:, 1] > m * H) & (pts[:, 1] < (1 - m) * H)).all())
                palm_c = pts[[0, 5, 9, 13, 17]].mean(0)
                l, t, r, b = pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()
                found.append({"side": side, "cx": round(float(palm_c[0] / W), 4), "cy": round(float(palm_c[1] / H), 4),
                              "left": round(float(max(0, l) / W), 4), "top": round(float(max(0, t) / H), 4),
                              "right": round(float(min(W, r) / W), 4), "bottom": round(float(min(H, b) / H), 4),
                              "px": int((r - l) * (b - t) / (W * H) * 1e6), "score": round(p["score"], 3), "presence": round(pres, 3),
                              "in_frame": inside})
        return found


def scan(video: Path, t0: float, t1: float, fps: float | None = None, width: int = 1280, log=print) -> list[dict]:
    """Rows of hands from t0 to t1 (seconds on the video's own clock)."""
    import cv2
    fps = fps or HAND_RULES["fps"]
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", str(video)],
                        capture_output=True, text=True).stdout
    st = json.loads(pr)["streams"][0]
    H = int(round(st["height"] * width / st["width"] / 2) * 2)
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(video), "-vf", f"fps={fps},scale={width}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    hf, rows, k = HandFinder(), [], 0
    while True:
        raw = p.stdout.read(width * H * 3)
        if len(raw) < width * H * 3:
            break
        img = np.frombuffer(raw, np.uint8).reshape(H, width, 3)
        rows.append({"t": round(t0 + k / fps, 3), "hands": hf.find(img)})
        k += 1
    p.wait()
    log(f"hands: {sum(1 for r in rows if r['hands'])} of {len(rows)} frames with a hand ({t0:.1f}-{t1:.1f} s)")
    return rows
