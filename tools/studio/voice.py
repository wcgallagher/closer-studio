"""Voice chain, loudness, music bed, synthesized sound design.

Voice chain v3 was tuned on 1/3-octave long-term spectra of the XTRA Muse takes against typical speech: a dynamic
low band (gated between words so room rumble vanishes), mud cut at 500 Hz, a 2.2 kHz tame, light denoise, a 6.8 kHz
de-ess notch and a little air. Loudness is one measured gain plus one safety limiter, never dynamic gain riding.
Optional: DeepFilterNet (Rikorose/DeepFilterNet, MIT/Apache-2.0) as a standalone binary, run before the chain.
"""
from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

VOICE = ("highpass=f=100:poles=2,acrossover=split=300:order=4th[lo][hi];"
         "[lo]agate=threshold=0.03:ratio=3:attack=8:release=250:knee=4:detection=rms[lg];"
         "[lg][hi]amix=inputs=2:normalize=0,"
         "equalizer=f=210:t=q:w=1.0:g=-2,equalizer=f=500:t=q:w=1.0:g=-7,equalizer=f=2200:t=q:w=1.0:g=-4,"
         "equalizer=f=3500:t=q:w=1.5:g=-1.5,afftdn=nr=6:nf=-42,atrim=start=0.025,asetpts=PTS-STARTPTS,"
         "equalizer=f=6800:t=q:w=2.5:g=-3,highshelf=f=9000:g=1.5:width_type=q:w=0.7,"
         "acompressor=threshold=-22dB:ratio=2:attack=20:release=250:makeup=2,aresample=48000")
VOICE_LIGHT = ("highpass=f=90:poles=2,equalizer=f=400:t=q:w=1.2:g=-3,afftdn=nr=4:nf=-45,"
               "acompressor=threshold=-20dB:ratio=1.8:attack=25:release=250:makeup=1,aresample=48000")
BED = ("highpass=f=40,equalizer=f=2600:t=q:w=0.9:g=-5,acompressor=threshold=-26dB:ratio=3:attack=200:release=1200,"
       "loudnorm=I=-24:TP=-4:LRA=7,aresample=48000")
DUCK = "sidechaincompress=threshold=0.03:ratio=3:attack=60:release=1500:makeup=1"


def chain(kind: str = "v3") -> str:
    return {"v3": VOICE, "light": VOICE_LIGHT, "none": "aresample=48000"}[kind]


def deep_filter_bin() -> str | None:
    for p in (os.environ.get("DEEP_FILTER"), str(Path.home() / ".closer-studio" / "bin" / "deep-filter"), shutil.which("deep-filter")):
        if p and Path(p).exists():
            return p
    return None


def measure(path: Path, lufs: float = -14, tp: float = -1.5) -> dict:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", f"loudnorm=I={lufs}:TP={tp}:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    g = lambda k: float(re.search(rf'"{k}" : "([^"]+)"', err).group(1))
    return {"i": g("input_i"), "tp": g("input_tp"), "lra": g("input_lra"), "thresh": g("input_thresh")}


def final_filter(input_i: float, lufs: float = -14, tp: float = -1.5) -> str:
    """One fixed gain to the target, one limiter. alimiter's ceiling is not literal; 0.81 lands about -1.2 dBTP."""
    gain = lufs - input_i
    lim = {-1.0: 0.84, -1.5: 0.80, -1.2: 0.81, -2.0: 0.74, -4.0: 0.60}.get(tp, 0.80)
    return f"volume={gain:.2f}dB,alimiter=limit={lim}:attack=5:release=60:level=false,aresample=48000"


def write_wav(path: Path, y: np.ndarray, sr: int = 48000, gain: float = 0.6):
    y = y / (np.abs(y).max() + 1e-9) * gain
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.stack([y, y], 1) * 32767).astype("<i2").tobytes())


def _svf_bandpass(x, fc, sr, q=0.6):
    y, lp, bp = np.zeros_like(x), 0.0, 0.0
    for k in range(len(x)):
        f = 2 * math.sin(math.pi * fc[k] / sr); hp = x[k] - lp - q * bp; bp += f * hp; lp += f * bp; y[k] = bp
    return y


def whoosh(path: Path, sr: int = 48000, dur: float = 0.3):
    n = int(dur * sr); t = np.arange(n) / sr
    x = np.random.default_rng(5).standard_normal(n)
    fc = 4000 * (300 / 4000) ** (t / dur)
    y = _svf_bandpass(x, fc, sr) * np.sin(np.pi * t / dur) ** 1.5
    write_wav(path, y, sr, 0.6)


def hit(path: Path, sr: int = 48000):
    """A soft low thump for emphasis kicks: 70 to 45 Hz sine sweep with a fast decay and a tiny click."""
    n = int(0.45 * sr); t = np.arange(n) / sr
    f = 70 * (45 / 70) ** (t / 0.45)
    ph = 2 * np.pi * np.cumsum(f) / sr
    y = np.sin(ph) * np.exp(-t * 9)
    click = np.random.default_rng(2).standard_normal(int(0.004 * sr)) * np.linspace(1, 0, int(0.004 * sr))
    y[:len(click)] += 0.25 * click
    write_wav(path, y, sr, 0.7)


def riser(path: Path, sr: int = 48000, dur: float = 1.4):
    """Noise sweep up into the CTA: band rises 300 Hz to 5 kHz, volume ramps, cut dead at the end."""
    n = int(dur * sr); t = np.arange(n) / sr
    x = np.random.default_rng(9).standard_normal(n)
    fc = 300 * (5000 / 300) ** (t / dur)
    y = _svf_bandpass(x, fc, sr, 0.8) * (t / dur) ** 2
    write_wav(path, y, sr, 0.5)


def sfx_pack(folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    files = {"whoosh": folder / "whoosh.wav", "hit": folder / "hit.wav", "riser": folder / "riser.wav"}
    if not files["whoosh"].exists(): whoosh(files["whoosh"])
    if not files["hit"].exists(): hit(files["hit"])
    if not files["riser"].exists(): riser(files["riser"])
    return files
