#!/usr/bin/env python3
"""Closer Studio reel builder: one talking-head clip in, a finished 9:16 reel out.

What it does, in order:
  1. transcribes the clip (faster-whisper, word timestamps) and finds the pauses
  2. cuts dead air over 0.35 s, keeps every word, alternates 100 / 110 / 120 % punch-ins with one crop anchor
  3. grades the footage (tools/vsl/luts/sma_pro.cube), adds a soft fill light on the face, clarity, a mild vignette
  4. cleans the voice (the chain from the SMA VSL: low band gated between words, mud cut, light denoise)
  5. burns word-highlight captions, an optional hook headline, and a brand end card
  6. mixes an optional music bed under the voice, measures loudness, lands at -14 LUFS with one safety limiter

Usage:
  python3 reel_build.py <video> --out <folder> [--start 12.5] [--end 41] [--brand btc|sma]
                        [--hook "TEXT FOR THE FIRST 2.5 S"] [--cta "End card line"] [--music file.mp3]
                        [--face-x 0.5] [--face-y 0.38] [--model small.en] [--keep-silence] [--preview]

Everything it needs: ffmpeg, python3 with numpy, faster-whisper (install.sh sets these up). Fonts: fonts/Montserrat-Black.ttf.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FPS = 30
W, H = 1080, 1920

BRANDS = {
    # becomethecloser.com (Firecrawl branding scrape 2026-10-30): dark ember site, square buttons, Fraunces / Inter / JetBrains Mono
    "btc": {"bg": "#0C0806", "accent": "#F3680F", "text": "#EFEAE2", "muted": "#2E2017", "cta": "Take the closer quiz",
            "sub": "becomethecloser.com", "handle": "@_owensantos_"},
    # setmoreannuities.com (same scrape): cream page, dark red-glow player, red buttons, gold accent
    "sma": {"bg": "#0e1114", "accent": "#B5311F", "text": "#FAF6EE", "muted": "#E0BE66", "cta": "Create your free account",
            "sub": "setmoreannuities.com", "handle": ""},
}

GAP_MAX = 0.35       # dead air longer than this is cut
PAD_IN, PAD_OUT = 0.05, 0.15
MIN_PIECE = 1.0
ZOOMS = (1.0, 1.10, 1.0, 1.20)
KY = 0.33            # one crop anchor for every scale: the eye line never moves at a cut
HOLD_S = 2.0         # end card
# Voice chain v3 (measured on the XTRA Muse balcony takes; see the sma-vsl-producer skill for the numbers)
VOICE = ("highpass=f=100:poles=2,acrossover=split=300:order=4th[lo][hi];"
         "[lo]agate=threshold=0.03:ratio=3:attack=8:release=250:knee=4:detection=rms[lg];"
         "[lg][hi]amix=inputs=2:normalize=0,"
         "equalizer=f=210:t=q:w=1.0:g=-2,equalizer=f=500:t=q:w=1.0:g=-7,equalizer=f=2200:t=q:w=1.0:g=-4,"
         "equalizer=f=3500:t=q:w=1.5:g=-1.5,afftdn=nr=6:nf=-42,atrim=start=0.025,asetpts=PTS-STARTPTS,"
         "equalizer=f=6800:t=q:w=2.5:g=-3,highshelf=f=9000:g=1.5:width_type=q:w=0.7,"
         "acompressor=threshold=-22dB:ratio=2:attack=20:release=250:makeup=2,aresample=48000")
POST = "unsharp=lx=13:ly=13:la=0.30,unsharp=5:5:0.45,vignette=a=0.35"
FUNC = {"to", "of", "the", "a", "an", "is", "and", "or", "we", "i", "you", "that", "in", "for", "at", "on", "it", "by",
        "your", "my", "how", "do", "what", "if", "this", "be", "are", "so", "its", "im", "youre", "were", "theyre", "not", "with"}


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"command failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r.stdout


def norm(w):
    return re.sub(r"[^a-z0-9$]", "", w.lower())


def hex_ass(h):
    h = h.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}&"


def ts(x):
    x = math.floor(max(x, 0) * 100) / 100
    h, r = divmod(x, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


# ---------------------------------------------------------------- 1. words and silences
def transcribe(video: Path, start: float, end: float, out: Path, model_name: str):
    cache = out / "transcript.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        if d.get("start") == start and d.get("end") == end and d.get("model") == model_name:
            return d["words"], d["silences"]
    dur = end - start
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(video), "-vn", "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    from faster_whisper import WhisperModel
    print(f"transcribing {dur:.1f} s with {model_name} (first run downloads the model) ...", flush=True)
    m = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5,
                           initial_prompt="Umm, uh, so, like, you know. Annuities, 401(k), IRA, commission, closer, objection.")
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"w": w.word.strip(), "s": round(float(w.start), 3), "e": round(float(w.end), 3)})
    # silences from RMS (20 ms frames): 25 dB under the speech level, at least 150 ms long
    sr, h = 16000, 320
    rms = np.array([np.sqrt(np.mean(a[i:i + h] ** 2)) + 1e-9 for i in range(0, len(a) - h, h)])
    db = 20 * np.log10(rms)
    thr = np.percentile(db, 80) - 25
    sil, run = [], None
    for i, v in enumerate(db):
        if v < thr and run is None:
            run = i
        if v >= thr and run is not None:
            if (i - run) * h / sr >= 0.15:
                sil.append((round(run * h / sr, 3), round(i * h / sr, 3)))
            run = None
    if run is not None and (len(db) - run) * h / sr >= 0.15:
        sil.append((round(run * h / sr, 3), round(len(a) / sr, 3)))
    cache.write_text(json.dumps({"start": start, "end": end, "model": model_name, "words": words, "silences": sil}, indent=1))
    return words, sil


# ---------------------------------------------------------------- 2. the cut
def build_pieces(words, sil, keep_silence):
    runs, run = [], [0]
    for i in range(1, len(words)):
        if not keep_silence and words[i]["s"] - words[i - 1]["e"] > GAP_MAX:
            runs.append([run[0], run[-1]])
            run = []
        run.append(i)
    runs.append([run[0], run[-1]])
    merged = []
    for r in runs:
        dur = words[r[1]]["e"] - words[r[0]]["s"]
        if merged and (dur < MIN_PIECE or words[merged[-1][1]]["e"] - words[merged[-1][0]]["s"] < MIN_PIECE):
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    # long runs get a continuous punch-in about every 2.6 s at a word gap (framing jumps, audio runs on)
    pieces = []
    for i0, i1 in merged:
        cuts, last = [], words[i0]["s"]
        for i in range(i0 + 1, i1 + 1):
            if words[i]["s"] - last >= 2.6 and words[i1]["e"] - words[i]["s"] >= 1.2 and words[i]["s"] - words[i - 1]["e"] >= 0.04:
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
        segs.append({"w0": i0, "w1": i1, "in": round(s, 3), "frames": n, "zoom": ZOOMS[k % 4], "cont": bool(prev and prev["cont_next"])})
        prev = pc
    for k in range(1, len(segs)):
        if segs[k]["zoom"] == segs[k - 1]["zoom"]:
            segs[k]["zoom"] = 1.10 if segs[k - 1]["zoom"] == 1.0 else 1.0
    t = 0.0
    for sg in segs:
        sg["out_t"] = round(t, 4)
        t += sg["frames"] / FPS
    return segs, t


# ---------------------------------------------------------------- 3. captions
def chunk_words(ws):
    clauses, cur = [], []
    for w in ws:
        cur.append(w)
        if w["w"][-1:] in ".,?!":
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    merged = []
    for c in clauses:
        if merged and (len(c) < 2 or len(merged[-1]) < 2):
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    out = []
    for c in merged:
        n = len(c)
        if n <= 3:
            out.append(c)
            continue
        k, best = max(1, math.ceil(n / 3.5)), None
        while best is None:
            for cuts in itertools.combinations(range(1, n), k - 1):
                sizes = [b - a for a, b in zip((0,) + cuts, cuts + (n,))]
                if max(sizes) > 4 or min(sizes) < 1:
                    continue
                score = -0.5 * (max(sizes) - min(sizes)) - sum(1 for z in sizes if z == 1)
                for cp in cuts:
                    if norm(c[cp]["w"]) in FUNC: score -= 2
                    if norm(c[cp - 1]["w"]) in FUNC: score -= 2
                    if c[cp]["s"] - c[cp - 1]["e"] > 0.15: score += 2
                if best is None or score > best[0]:
                    best = (score, cuts)
            if best is None:
                k += 1
                if k > n:
                    best = (0, tuple(range(3, n, 3)))
        cuts = best[1]
        out += [c[a:b] for a, b in zip((0,) + cuts, cuts + (n,))]
    final = []
    for c in out:
        if final and (c[-1]["e"] - c[0]["s"]) < 0.3 and len(final[-1]) + len(c) <= 4:
            final[-1] = final[-1] + c
        else:
            final.append(c)
    return final


def wrap_hook(text, max_px=W - 180, start=84, floor=56):
    """Break the hook into up to three lines that fit the frame; shrink the size only if a single word is too wide."""
    from PIL import ImageFont
    font_file = ROOT / "fonts" / "Montserrat-Black.ttf"
    px = start
    while True:
        f = ImageFont.truetype(str(font_file), px)
        lines, cur = [], ""
        for w in text.split():
            t = (cur + " " + w).strip()
            if f.getlength(t) <= max_px:
                cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        lines.append(cur)
        if (len(lines) <= 3 and all(f.getlength(l) <= max_px for l in lines)) or px <= floor:
            return "\\N".join(lines), px
        px -= 4


def captions(segs, words, brand, hook, total, speech_end, out):
    acc, txt = hex_ass(brand["accent"]), hex_ass(brand["text"])
    ev = []
    HOOK_END = 2.6 if hook else 0.0
    if hook:
        hook_lines, hook_px = wrap_hook(hook)
        ev.append(f"Dialogue: 6,{ts(0)},{ts(HOOK_END)},Hook,,0,0,0,,{{\\pos({W // 2},{int(H * 0.60)})\\fs{hook_px}\\fad(0,200)\\fscx106\\fscy106\\t(0,180,\\fscx100\\fscy100)}}{hook_lines}")
    for sg in segs:
        seg_end = sg["out_t"] + sg["frames"] / FPS
        ws = words[sg["w0"]:sg["w1"] + 1]
        chunks = chunk_words(ws)
        for ci, c in enumerate(chunks):
            labels = [w["w"].upper().strip(",.?!") for w in c]
            for k, w in enumerate(c):
                a = sg["out_t"] + (w["s"] - sg["in"])
                if k + 1 < len(c):
                    b = sg["out_t"] + (c[k + 1]["s"] - sg["in"])
                elif ci + 1 < len(chunks):
                    b = sg["out_t"] + (chunks[ci + 1][0]["s"] - sg["in"])
                else:
                    b = min(sg["out_t"] + (w["e"] - sg["in"]) + 0.25, seg_end)
                b = min(b, seg_end, speech_end + 0.15)
                if b - a < 0.02 or a < HOOK_END:
                    continue
                parts = [f"{{\\1c{acc if m == k else txt}}}{lab}" for m, lab in enumerate(labels)]
                pop = "\\fscx92\\fscy92\\t(0,70,\\fscx100\\fscy100)" if k == 0 else ""
                ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Cap,,0,0,0,,{{{pop}}}{' '.join(parts)}")
    font = "Montserrat Black"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},92,{txt},{txt},&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,5,2,2,70,70,520,1
Style: Hook,{font},84,{acc},{acc},&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,5,2,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    (out / "captions.ass").write_text(head + "\n".join(ev) + "\n")
    # plain SRT for the platform's own caption upload
    srt, n = [], 1
    for sg in segs:
        for c in chunk_words(words[sg["w0"]:sg["w1"] + 1]):
            a = max(0.0, sg["out_t"] + (c[0]["s"] - sg["in"])); b = max(a + 0.2, sg["out_t"] + (c[-1]["e"] - sg["in"]) + 0.2)
            f = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int((x % 1) * 1000):03d}"
            srt.append(f"{n}\n{f(a)} --> {f(b)}\n{' '.join(w['w'] for w in c)}\n"); n += 1
    (out / "captions.srt").write_text("\n".join(srt))


# ---------------------------------------------------------------- 4. assets
def write_fill(path, fx, fy):
    from PIL import Image
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - fx * W) / 560.0) ** 2 + ((y - fy * H) / 620.0) ** 2)
    a = np.clip(1 - d, 0, 1) ** 1.6
    img = np.zeros((H, W, 4), np.uint8); img[..., 0] = 255; img[..., 1] = 246; img[..., 2] = 236; img[..., 3] = (a * 255 * 0.28).astype(np.uint8)
    Image.fromarray(img, "RGBA").save(path)


def write_whoosh(path, sr=48000):
    n = int(0.3 * sr); t = np.arange(n) / sr
    rng = np.random.default_rng(5); x = rng.standard_normal(n)
    fc = 4000 * (300 / 4000) ** (t / 0.3)
    y, lp, bp = np.zeros(n), 0.0, 0.0
    for k in range(n):
        f = 2 * math.sin(math.pi * fc[k] / sr); hp = x[k] - lp - 0.6 * bp; bp += f * hp; lp += f * bp; y[k] = bp
    y *= np.sin(np.pi * t / 0.3) ** 1.5
    y /= np.abs(y).max() + 1e-9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.stack([y, y], 1) * 0.6 * 32767).astype("<i2").tobytes())


# ---------------------------------------------------------------- 5. render
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=float, default=0.0); ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--brand", default="btc", choices=sorted(BRANDS)); ap.add_argument("--hook", default="")
    ap.add_argument("--cta", default=None); ap.add_argument("--music", default=None)
    ap.add_argument("--face-x", type=float, default=0.5); ap.add_argument("--face-y", type=float, default=0.38)
    ap.add_argument("--model", default="small.en"); ap.add_argument("--keep-silence", action="store_true")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    video, out = Path(a.video).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "segs").mkdir(exist_ok=True)
    brand = dict(BRANDS[a.brand]); cta = a.cta or brand["cta"]
    info = json.loads(sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(video)]))
    sw, shh = info["streams"][0]["width"], info["streams"][0]["height"]
    end = a.end if a.end is not None else float(info["format"]["duration"])
    words, sil = transcribe(video, a.start, end, out, a.model)
    if not words:
        sys.exit("no speech found in that window")
    segs, speech_end = build_pieces(words, sil, a.keep_silence)
    total = speech_end + HOLD_S
    print(f"{len(segs)} pieces, {speech_end:.1f} s of speech, {total:.1f} s total")

    # 9:16 crop region inside the source, centred on the face, then the zoom crop inside that
    crop_h = shh; crop_w = int(shh * 9 / 16)
    if crop_w > sw:
        crop_w = sw; crop_h = int(sw * 16 / 9)
    cx = min(max(int(a.face_x * sw - crop_w / 2), 0), sw - crop_w)
    cy = min(max(int(a.face_y * shh - crop_h * 0.38), 0), shh - crop_h)
    lut = HERE / "vsl" / "luts" / "sma_pro.cube"
    fill = out / "fill.png"; write_fill(fill, 0.5, 0.36)
    crf, preset = ("26", "veryfast") if a.preview else ("18", "medium")
    cmds = []
    for k, sg in enumerate(segs):
        z = sg["zoom"]; D = sg["frames"] / FPS
        kexpr = f"(1.02+0.03*t/{D:.3f})"
        vf = (f"crop={crop_w}:{crop_h}:{cx}:{cy},crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*{KY},setpts=PTS-STARTPTS,"
              f"lut3d=file={lut},scale=w='trunc({W}*{kexpr}/2)*2':h=-2:eval=frame:flags=bicubic,"
              f"crop={W}:{H}:x='(iw-{W})/2':y='(ih-{H})*0.4'")
        cmds.append(f'[ -f "{out}/segs/{k:03d}.mp4" ] || ffmpeg -v error -y -ss {a.start + sg["in"]:.3f} -i "{video}" -an -frames:v {sg["frames"]} '
                    f'-filter_complex "[0:v]{vf}[g];movie={fill}[f];[g][f]overlay=format=auto:eof_action=repeat,{POST},setsar=1,fps=30,format=yuv420p[v]" '
                    f'-map "[v]" -c:v libx264 -preset {preset} -crf {crf} -threads 2 "{out}/segs/{k:03d}.mp4"')
    runs, cur = [], []
    for k, sg in enumerate(segs):
        if sg["cont"] and cur:
            cur.append(k)
        else:
            if cur: runs.append(cur)
            cur = [k]
    runs.append(cur)
    for j, r in enumerate(runs):
        sg = segs[r[0]]; d = sum(segs[i]["frames"] for i in r) / FPS
        fo = 0.30 if r[-1] == len(segs) - 1 else 0.03
        cmds.append(f'[ -f "{out}/segs/r{j:03d}.wav" ] || ffmpeg -v error -y -ss {a.start + sg["in"]:.3f} -t {d + 0.1:.6f} -i "{video}" '
                    f'-filter_complex "[0:a:0]{VOICE},afade=t=in:st=0:d=0.03,afade=t=out:st={d - fo:.6f}:d={fo},apad,atrim=0:{d:.6f}[a]" -map "[a]" -ac 2 -ar 48000 -c:a pcm_s16le "{out}/segs/r{j:03d}.wav"')
    (out / "cmds.txt").write_text("\n".join(cmds) + "\n")
    print("rendering pieces ...", flush=True)
    from concurrent.futures import ThreadPoolExecutor
    def run(c):
        r = subprocess.run(["bash", "-c", c], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"piece failed:\n{c[:300]}\n{r.stderr[-1500:]}")
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(run, cmds))

    # end card: brand background, CTA, site, handle
    font = ROOT / "fonts" / "Montserrat-Black.ttf"
    font2 = ROOT / "fonts" / "Montserrat-ExtraBold.ttf"
    esc = lambda s: s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    lines = [f"drawtext=fontfile={font}:text='{esc(cta.upper())}':fontsize=78:fontcolor={brand['accent']}:x=(w-tw)/2:y=h*0.44",
             f"drawtext=fontfile={font2}:text='{esc(brand['sub'])}':fontsize=44:fontcolor={brand['text']}:x=(w-tw)/2:y=h*0.52"]
    if brand["handle"]:
        lines.append(f"drawtext=fontfile={font2}:text='{esc(brand['handle'])}':fontsize=40:fontcolor={brand['text']}@0.7:x=(w-tw)/2:y=h*0.57")
    sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={brand['bg']}:s={W}x{H}:d={HOLD_S}:r=30",
        "-vf", ",".join(lines) + ",vignette=a=0.4,format=yuv420p", "-c:v", "libx264", "-preset", preset, "-crf", crf, str(out / "segs" / "zzz_end.mp4")])
    sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{HOLD_S:.3f}", "-c:a", "pcm_s16le", str(out / "segs" / "r999_end.wav")])
    vlist = "\n".join(f"file '{p}'" for p in sorted((out / "segs").glob("*.mp4")))
    alist = "\n".join(f"file '{p}'" for p in sorted((out / "segs").glob("r*.wav")))
    (out / "v.txt").write_text(vlist + "\n"); (out / "a.txt").write_text(alist + "\n")
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(out / "v.txt"), "-f", "concat", "-safe", "0", "-i", str(out / "a.txt"),
        "-map", "0:v", "-map", "1:a", "-c", "copy", str(out / "base.mkv")])

    captions(segs, words, brand, a.hook.upper(), total, speech_end, out)
    whoosh = out / "whoosh.wav"; write_whoosh(whoosh)
    sfx = [(whoosh, sg["out_t"] - 0.1, 0.22) for sg in segs if sg["zoom"] > 1]
    inputs = ["-i", str(out / "base.mkv")]
    chains, labels = [], []
    idx = 1
    if a.music:
        sh(["ffmpeg", "-v", "error", "-y", "-i", a.music, "-t", f"{total + 0.5:.3f}", "-af",
            "highpass=f=40,equalizer=f=2600:t=q:w=0.9:g=-5,acompressor=threshold=-26dB:ratio=3:attack=200:release=1200,loudnorm=I=-24:TP=-4:LRA=7,aresample=48000",
            "-ac", "2", "-c:a", "pcm_s16le", str(out / "bed.wav")])
        inputs += ["-i", str(out / "bed.wav")]
        env = f"if(lt(t\\,0.6)\\,t/0.6\\,1)*if(gt(t\\,{speech_end:.3f})\\,max(0.4\\,1-(t-{speech_end:.3f})/0.5)\\,1)*if(gt(t\\,{total - 1.2:.3f})\\,max(0\\,({total:.3f}-t)/1.2)\\,1)"
        chains.append(f"[1:a]volume='{env}':eval=frame[bedv];[bedv][key]sidechaincompress=threshold=0.03:ratio=3:attack=60:release=1500:makeup=1[bed]")
        labels.append("[bed]"); idx = 2
    for j, (f, at, g) in enumerate(sfx):
        inputs += ["-i", str(f)]
        chains.append(f"[{idx + j}:a]volume={g},adelay={max(0, int(at * 1000))}|{max(0, int(at * 1000))},aresample=48000[s{j}]")
        labels.append(f"[s{j}]")
    graph = ("[0:a]asplit=2[vo][key];" if a.music else "[0:a]anull[vo];") + (";".join(chains) + ";" if chains else "") + \
            f"[vo]{''.join(labels)}amix=inputs={1 + len(labels)}:normalize=0:duration=first[mix]"
    if not a.music:
        graph = graph.replace("[0:a]anull[vo];", "[0:a]anull[vo];")
    sh(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[mix]", "-c:a", "pcm_s16le", str(out / "mix.wav")])
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out / "mix.wav"), "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    i_in = float(re.search(r'"input_i" : "([^"]+)"', meas).group(1))
    gain = -14 - i_in
    name = f"{video.stem}_reel.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(out / "base.mkv"), "-i", str(out / "mix.wav"), "-map", "0:v", "-map", "1:a",
        "-vf", f"ass={out / 'captions.ass'}", "-af", f"volume={gain:.2f}dB,alimiter=limit=0.81:attack=5:release=60:level=false,aresample=48000",
        "-c:v", "libx264", "-preset", preset, "-crf", crf, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        "-t", f"{total:.4f}", str(out / name)])
    (out / "summary.txt").write_text(f"{name}\n{total:.1f} s, {len(segs)} cuts, brand {a.brand}, hook: {a.hook or '(none)'}\n"
                                     f"source {video.name} {a.start:.1f}-{end:.1f} s\ncaptions: captions.srt\n")
    print(f"done: {out / name} ({total:.1f} s)")


if __name__ == "__main__":
    main()
