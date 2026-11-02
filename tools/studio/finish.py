"""Finish: what a colourist does to a phone talking head after the cut, written as measured rules.

Runs on the cut picture (base video, output clock) before any graphics, so type and cards are never graded.

  measure   face luma (tracked window), sky and highlight share, how much clips, overall contrast
  sky       a qualifier (bright and blue, or bright and colourless clouds/walls) pulls highlights down (only when the sky
            is hot), deepens the blue a little and softens it a touch, which reads as depth behind the speaker
  face      a tracked soft window lifts the face toward a skin target and warms it slightly; never brighter than the target
  halation  the brightest parts bloom a warm glow, the way film does around a hot sky
  texture   a fine moving grain weighted to the midtones and a gentle vignette

Clean footage gets less: every move scales with what it measured (a well-exposed face gets no lift). The pipeline is
BT.709 in and out with explicit matrix and range, so the round trip never shifts hues.
"""
from __future__ import annotations

import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

FINISH_RULES = {
    "sky": {"luma_lo": 0.52, "luma_hi": 0.72, "blue_lo": 0.015, "blue_hi": 0.09, "white_lo": 0.80, "hot_from": 0.66,
            "ev_max": -0.45, "white_share": 0.5, "sat": 0.08, "soften_sigma": 1.4, "soften_mix": 0.45},
    "face": {"target_luma": 0.52, "ev_max": 0.30, "warm": 0.010, "grow_w": 1.35, "grow_h": 1.30, "drop": 0.12},
    "halation": {"thresh": 0.88, "sigma": 5.0, "mix": 0.03, "tint": (1.0, 0.58, 0.38)},
    "grain": {"amount": 0.012},
    "vignette": {"strength": 0.16},
}


# profiles: a sales VSL sells trust in a person, so it gets no local moves at all: in the v9 blind A/B (2026-11-02,
# 12 reviews) the sky pull, the face window and grain read as "a halo around the head and a blotchy, posterized
# sky", cited by 6 reviewers, and the cut without a finish pass won. Only a light vignette stays. A brand film gets
# the full pass. Web players re-encode at low bitrates and turn grain into mush.
FINISH_PROFILES = {"vsl": {"halation": False, "grain": 0.0, "vignette": 0.10, "sky": False, "face": False},
                   "reel": {"halation": False, "grain": 0.006, "vignette": 0.10},
                   "brand": {}}


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _probe(video: Path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_frames,r_frame_rate",
                          "-show_entries", "format=duration", "-of", "json", str(video)], capture_output=True, text=True).stdout
    j = json.loads(out)
    st = j["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    n = int(st.get("nb_frames") or 0) or int(round(float(j["format"]["duration"]) * fps))
    return st["width"], st["height"], fps, n


def _decode(video, W, H, start_frame, count, fps):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start_frame / fps:.4f}", "-i", str(video), "-frames:v", str(count), "-an",
           "-vf", "scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24", "-f", "rawvideo", "-"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def _encoder(dst, W, H, fps, crf=14):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-",
           "-vf", "scale=in_range=full:out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "fast",
           "-crf", str(crf), "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", str(dst)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def measure(video: Path, faces: list, samples: int = 24) -> dict:
    """Stats on evenly spaced frames: face luma, sky share and heat, clipped share."""
    import cv2
    W, H, fps, n = _probe(video)
    R = FINISH_RULES
    fl, sky_l, sky_s, clip = [], [], [], []
    for k in range(samples):
        i = int((k + 0.5) * n / samples)
        p = _decode(video, W, H, i, 1, fps)
        raw = p.stdout.read(W * H * 3); p.wait()
        if len(raw) < W * H * 3:
            continue
        x = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        L = small @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        m = _sky_mask(small, L, R["sky"])
        if m.mean() > 0.01:
            sky_l.append(float((L * m).sum() / m.sum()))
        sky_s.append(float(m.mean()))
        clip.append(float((L > 0.985).mean()))
        f = faces[i] if i < len(faces) else None
        if f:
            x0, y0, x1, y1 = (int(v / 4) for v in f)
            x0, y0 = max(0, x0), max(0, y0)
            patch = L[y0:max(y0 + 1, y1), x0:max(x0 + 1, x1)]
            if patch.size:
                fl.append(float(np.median(patch)))
    return {"face_luma": round(float(np.median(fl)), 3) if fl else None, "sky_luma": round(float(np.median(sky_l)), 3) if sky_l else None,
            "sky_share": round(float(np.median(sky_s)), 3), "clipped_share": round(float(np.median(clip)), 4)}


def _sky_mask(x, L, S):
    """Bright blue sky at full weight, bright colourless cloud or wall at white_share; skin (warm, saturated) never matches."""
    blue = x[..., 2] - np.maximum(x[..., 0], x[..., 1])
    sat = x.max(-1) - x.min(-1)
    bright = _smooth(L, S["luma_lo"], S["luma_hi"])
    white = _smooth(L, S["white_lo"], 0.95) * (1 - _smooth(sat, 0.10, 0.25)) * S.get("white_share", 0.5)
    return bright * np.clip(_smooth(blue, S["blue_lo"], S["blue_hi"]) + white, 0, 1)


def plan(stats: dict, profile: str = "brand") -> dict:
    """Turn measurements into move sizes: nothing is applied that the footage does not need."""
    R = FINISH_RULES
    sky_ev = 0.0
    if stats.get("sky_luma") and stats["sky_luma"] > R["sky"]["hot_from"]:
        sky_ev = max(R["sky"]["ev_max"], -(stats["sky_luma"] - R["sky"]["hot_from"]) * 2.2)
    face_ev = 0.0
    if stats.get("face_luma"):
        face_ev = float(np.clip(np.log2(R["face"]["target_luma"] / max(stats["face_luma"], 0.05)) * 0.8, 0.0, R["face"]["ev_max"]))
    pr = FINISH_PROFILES.get(profile, {})
    hal = stats.get("sky_share", 0) > 0.03 or stats.get("clipped_share", 0) > 0.002
    if not pr.get("sky", True):
        sky_ev = 0.0
    if not pr.get("face", True):
        face_ev = 0.0
    return {"profile": profile, "sky_ev": round(sky_ev, 3), "face_ev": round(face_ev, 3),
            "sky_on": pr.get("sky", True) and stats.get("sky_share", 0) > 0.03,
            "halation": hal and pr.get("halation", True), "grain": pr.get("grain", R["grain"]["amount"]),
            "vignette": pr.get("vignette", R["vignette"]["strength"])}


def _work(args):
    video, dst, W, H, fps, f0, cnt, faces, pl = args
    import cv2
    R = FINISH_RULES
    dec = _decode(video, W, H, f0, cnt, fps)
    enc = _encoder(dst, W, H, fps)
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    r = np.hypot((xx - W / 8) / (W / 8), (yy - H / 8) / (H / 8))
    vig = cv2.resize((1 - pl["vignette"] * _smooth(r, 0.55, 1.45)).astype(np.float32), (W, H))[..., None]
    rng = np.random.default_rng(f0 + 7)
    tint = np.array(R["halation"]["tint"], np.float32)
    lw = np.array([0.2126, 0.7152, 0.0722], np.float32)
    for k in range(cnt):
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            break
        x = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        Ls = small @ lw
        # face window (quarter res), used both to lift the face and to keep the sky moves off it
        fm = np.zeros((H // 4, W // 4), np.float32)
        f = faces[f0 + k] if f0 + k < len(faces) else None
        if f:
            cx, cy = (f[0] + f[2]) / 8, (f[1] + f[3]) / 8 + (f[3] - f[1]) / 4 * R["face"]["drop"]
            rx, ry = (f[2] - f[0]) / 8 * R["face"]["grow_w"], (f[3] - f[1]) / 8 * R["face"]["grow_h"]
            d = ((xx - cx) / max(rx, 1)) ** 2 + ((yy - cy) / max(ry, 1)) ** 2
            fm = (1 - _smooth(d, 0.45, 1.0)).astype(np.float32)
        if pl["sky_on"]:
            # the qualifier runs on every pixel at full size and is only de-noised by 1 px: a mask blurred across the
            # subject's edge leaves the sky next to the head undarkened, which reads as a bright halo
            M = cv2.GaussianBlur(_sky_mask(x, x @ lw, R["sky"]).astype(np.float32), (0, 0), 1.0)[..., None]
            if pl["sky_ev"] < 0:
                x = x * (1 + (2 ** pl["sky_ev"] - 1) * M)
            L = x @ lw
            x = L[..., None] + (x - L[..., None]) * (1 + R["sky"]["sat"] * M)
            soft = cv2.GaussianBlur(x, (0, 0), R["sky"]["soften_sigma"])
            x = x + (soft - x) * M * R["sky"]["soften_mix"]
        if f and pl["face_ev"] > 0:
            F = cv2.resize(fm, (W, H))[..., None]
            x = x * (1 + (2 ** pl["face_ev"] - 1) * F)
            x[..., 0] += R["face"]["warm"] * F[..., 0]
            x[..., 2] -= R["face"]["warm"] * F[..., 0]
        if pl["halation"]:
            hs = cv2.resize(x, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
            hl = np.clip((hs @ lw - R["halation"]["thresh"]) / (1 - R["halation"]["thresh"]), 0, 1)
            glow = cv2.GaussianBlur(hl, (0, 0), R["halation"]["sigma"])
            x = x + R["halation"]["mix"] * cv2.resize(glow, (W, H))[..., None] * tint
        L = np.clip(x @ lw, 0, 1)
        g = cv2.resize(rng.standard_normal((H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        x = x * vig + (pl["grain"] * g * (4 * L * (1 - L)))[..., None]
        enc.stdin.write((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    return dst


def run(base: Path, faces: list, log=print, workers: int = 4, profile: str = "brand") -> dict:
    """Finish base (keeps its audio). faces: per output frame (x0, y0, x1, y1) or None. Writes base_raw.mkv once and
    replaces base.mkv with the finished picture; returns the measurements and the plan."""
    base = Path(base)
    raw = base.with_name("base_raw.mkv")
    stamp = base.with_name("finish.json")
    key = f"{raw.stat().st_size if raw.exists() else base.stat().st_size}|{profile}|{json.dumps(FINISH_RULES, sort_keys=True)}"
    if raw.exists() and stamp.exists() and json.loads(stamp.read_text()).get("key") == key and base.exists():
        return json.loads(stamp.read_text())
    if not raw.exists() or base.stat().st_mtime > raw.stat().st_mtime:
        base.replace(raw)
    W, H, fps, n = _probe(raw)
    stats = measure(raw, faces)
    pl = plan(stats, profile)
    log(f"finish: measured {stats}; plan {pl}")
    parts, step = [], int(np.ceil(n / workers))
    jobs = []
    for j in range(workers):
        f0, cnt = j * step, min(step, n - j * step)
        if cnt <= 0:
            continue
        dst = base.with_name(f"finish_{j}.mkv")
        parts.append(dst)
        jobs.append((str(raw), dst, W, H, fps, f0, cnt, faces, pl))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        list(ex.map(_work, jobs))
    lst = base.with_name("finish.txt")
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(raw), "-map", "0:v", "-map", "1:a?",
                    "-c", "copy", str(base)], check=True)
    for p in parts:
        p.unlink()
    rep = {"key": key, "stats": stats, "plan": pl, "rules": FINISH_RULES}
    stamp.write_text(json.dumps(rep, indent=1))
    return rep
