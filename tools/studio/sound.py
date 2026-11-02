"""Sound director: the mix a human engineer makes, written down as rules with numbers.

Three stems (voice, music, sound effects) are built on the output clock from the words, then summed and measured.
Nothing here guesses with a model; every move is a rule an engineer would name, and every rule is in SOUND_RULES
so a skill file, a review and a person can read the same numbers.

  voice   noise reduced against the speaker's own room tone (12 dB at most, so no watery artifacts), tonal balance
          matched to a speech target curve (corrections capped at 4 dB), sibilance tamed only on the frames that hiss,
          breaths kept but 10 dB lower, phrase loudness evened by 70 % (clip gain before compression), then a slow
          leveller and a fast peak catcher.
  music   picked by measured traits (tempo, mode, how much it sits in the voice band, whether it builds), fitted to
          the cut on bar lines with the track's own ending spliced in, ridden by hand-style automation: down before
          a word starts (not after, like a sidechain), up in real pauses, a pocket cut in 300 Hz to 4 kHz under speech,
          drops that come back on a downbeat, a swell into the end card.
  sfx     few, motivated, timed to the frame: a whoosh peaks on its cut, an impact lands on the word, a riser ends on
          the drop, a tick lands with the element; a density budget so it never turns into a sound board.

Loudness is ITU-R BS.1770 (K-weighted, gated), measured in numpy so stems can be compared over time.
"""
from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000

SOUND_RULES = {
    # numbers from docs/AUDIO_SPEC (closer-studio audio spec v1, 2026-11-02): measured on Iman Gadzhi uploads (demucs stems,
    # BS.1770 momentary loudness, whisper word alignment), ACX, EBU R128 s1, iZotope; "house" where the spec says so
    "voice": {
        "highpass_hz": 80, "highpass_wind_hz": 110, "wind_ratio": 0.45,
        "wind_burst_over_db": 8.0, "wind_burst_cut_db": 12.0, "wind_burst_hz": 180,
        "denoise": "wiener", "denoise_max_db": 12, "denoise_oversub": 1.5, "dd_alpha": 0.98,
        "tone_notch_over_db": 8.0, "tone_notch_max_db": 18.0,
        "eq_max_cut_db": 4.0, "eq_max_boost_db": 2.0, "eq_max_boost_above_6k_db": 0.0, "eq_apply": 0.5,
        "pause_cut_db": 4.0, "pause_min_s": 0.18, "pause_margin_s": 0.04,
        "deess_band_hz": [4500, 10000], "deess_trigger_db": 6.0, "deess_max_db": 6.0,
        "breath_cut_db": 6.0, "breath_min_s": 0.12, "breath_max_s": 1.2,
        "phrase_gap_s": 0.25, "clip_gain_apply": 0.7, "clip_gain_max_db": 6.0,
        "level_ratio": 1.5, "level_threshold_db": -26.0, "peak_ratio": 3.0, "peak_threshold_db": -10.0,
        "stem_lufs": -16.0,
    },
    "music": {
        # voice minus music (momentary LU, word frames) per section; vsl_hero defaults from the spec: hook 11, body 14, CTA 12
        "vm_target_lu": 14.0, "vm_p10_min_lu": 8.0,
        "gap_min_s": 1.2, "gap_lift_db": 6.0, "gap_lift_hook_db": 8.0, "hook_s": 8.0,
        "duck_lead_s": 0.2, "duck_ramp_s": 0.15, "lift_delay_s": 0.25, "lift_ramp_s": 0.6,
        "pocket_hz": [300, 4000], "pocket_static_db": -2.0,
        "outro_lift_db": 6.0, "outro_ramp_s": 2.0, "fade_out_s": 1.2,
        "drop_db": -40.0, "drop_lead_s": 0.4, "drop_ramp_s": 0.06, "return_ramp_s": 0.02, "return_downbeat_within_s": 1.0, "drops_max": 3,
        "cta_lift_db": 2.0,
        "splice_xfade_s": 0.04,
        "pick": {"tempo": [70, 115], "voice_band_max": 0.42, "prefer_minor": True, "want_build": True},
    },
    "sfx": {
        "dialect": "gadzhi",
        "min_gap_s": 0.35, "under_word_db": -5.0, "rotate_max_repeat": 2,
        # event -> [(role, level LU relative to the voice stem's integrated loudness)], per dialect; [] = leave it dry
        "grammar": {
            "gadzhi": {"punch_in_hook": [("whoosh", -18)], "punch_in": [], "hard_cut": [], "card_in": [("whoosh", -14)], "card_out": [],
                       "card_element": [], "chip": [("shine", -22)], "hand_label": [], "section_change": [("reverse", -16)],
                       "number_reveal": [("shine", -14), ("sub", -10)], "cta_riser": [("riser", -12)], "pointer": [("tick", -20)],
                       "end_card": [("shine", -18)], "drop_return": [("reverse", -18)]},
            "nelk": {"punch_in_hook": [("whoosh", -12)], "punch_in": [("whoosh", -12)], "hard_cut": [("swish", -16)], "card_in": [("whoosh", -11)],
                     "card_out": [("swish", -16)], "card_element": [("tick", -14)], "chip": [("tick", -14)], "hand_label": [("tick", -22)],
                     "section_change": [("riser", -10), ("impact", -6)], "number_reveal": [("riser", -8), ("impact", -4), ("sub", -8)],
                     "cta_riser": [("riser", -8)], "pointer": [("tick", -14)], "end_card": [("impact", -6), ("sub", -10)], "drop_return": [("impact", -8)]},
        },
        "density": {"gadzhi": {"first_20s_max": 8, "per_min_body_max": 4, "ticks_per_10s": 1, "risers_max": 1, "reverse_max": 3},
                    "nelk": {"first_20s_max": 14, "per_min_body_max": 12, "ticks_per_10s": 3, "risers_max": 3, "reverse_max": 4}},
        # where the sound must hit relative to t0: whoosh, riser and reverse peak on it; impacts, subs, shines and ticks start on it
        "align": {"whoosh": "peak", "riser": "end", "reverse": "peak", "swish": "peak", "impact": "onset", "sub": "onset", "shine": "onset", "tick": "onset"},
    },
    "master": {"lufs": -14.0, "true_peak_db": -1.0, "short_term_over_integrated_max_lu": 5.0},
}

SECTION_PRESETS = {   # vsl_hero: hook to the offer, body, turn and CTA (anchors on the cut's words, set in the layers file)
    "vsl_hero": [{"name": "hook", "vm": 11.0, "p10": 5.0}, {"name": "body", "vm": 14.0, "p10": 8.0}, {"name": "cta", "vm": 12.0, "p10": 6.0}],
    "paid_ad": [{"name": "all", "vm": 12.0, "p10": 6.0}], "organic_reel": [{"name": "all", "vm": 16.0, "p10": 9.0}],
    "tutorial": [{"name": "all", "vm": 20.0, "p10": 13.0}], "story": [{"name": "all", "vm": 23.0, "p10": 15.0}],
}


# ---------------------------------------------------------------- io


def read_audio(path: Path, sr: int = SR, mono: bool = True, start: float = 0.0, dur: float | None = None) -> np.ndarray:
    """Decode anything ffmpeg reads to float32 at sr (mono, or stereo as (n, 2))."""
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) + \
          ["-i", str(path), "-vn", "-ac", "1" if mono else "2", "-ar", str(sr), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype="<f4").astype(np.float32)
    return y if mono else y.reshape(-1, 2)


def write_audio(path: Path, y: np.ndarray, sr: int = SR):
    y = np.asarray(y, dtype=np.float32)
    if y.ndim == 1:
        y = np.stack([y, y], 1)
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2")
    import wave
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-12))


def undb(d):
    return 10 ** (np.asarray(d) / 20)


# ---------------------------------------------------------------- loudness (BS.1770)


_KW = ((np.array([1.53512485958697, -2.69169618940638, 1.19839281085285]), np.array([1.0, -1.69065929318241, 0.73248077421585])),
       (np.array([1.0, -2.0, 1.0]), np.array([1.0, -1.99004745483398, 0.99007225036621])))


def _kweight(y):
    for b, a in _KW:
        y = signal.lfilter(b, a, y, axis=0)
    return y


def _ms(y, win, hop):
    """Mean square per channel-summed block (K-weighted input), block length win, hop in samples."""
    if y.ndim == 1:
        y = y[:, None]
    p = (y ** 2).sum(1)
    c = np.concatenate([[0.0], np.cumsum(p)])
    starts = np.arange(0, max(1, len(p) - win + 1), hop)
    return (c[np.minimum(starts + win, len(p))] - c[starts]) / win, starts


def lufs(y: np.ndarray, sr: int = SR) -> float:
    """Integrated loudness, gated as BS.1770-4 (400 ms blocks, 75 % overlap, -70 LUFS absolute and -10 LU relative)."""
    k = _kweight(y)
    ms, _ = _ms(k, int(0.4 * sr), int(0.1 * sr))
    l = -0.691 + 10 * np.log10(ms + 1e-12)
    g = ms[l > -70]
    if not len(g):
        return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = ms[(l > -70) & (l > rel)]
    return float(-0.691 + 10 * np.log10(g2.mean() + 1e-12))


def loudness_curve(y: np.ndarray, sr: int = SR, win_s: float = 0.4, hop_s: float = 0.1):
    """Momentary (400 ms) or short-term (3 s) loudness over time: (times at block centre, LUFS)."""
    k = _kweight(y)
    ms, st = _ms(k, int(win_s * sr), int(hop_s * sr))
    return (st + win_s * sr / 2) / sr, -0.691 + 10 * np.log10(ms + 1e-12)


def true_peak_db(y: np.ndarray) -> float:
    """4x oversampled peak, the BS.1770 true-peak approximation."""
    x = y if y.ndim == 1 else y.max(1)
    up = signal.resample_poly(x, 4, 1)
    return float(db(np.abs(up).max()))


# ---------------------------------------------------------------- speech map


@dataclass
class Phrase:
    s: float
    e: float
    i0: int
    i1: int


def out_words(an: dict, segs: list[dict]) -> list[dict]:
    """The words on the output clock (start t, end e) from the analysis words and the cut's pieces."""
    words, out = an["words"], []
    for sg in segs:
        for i in range(sg["w0"], sg["w1"] + 1):
            w = words[i]
            out.append({"w": w["w"], "t": sg["out_t"] + w["s"] - sg["in"], "e": sg["out_t"] + w["e"] - sg["in"],
                        "emph": bool(w.get("emph"))})
    return sorted(out, key=lambda w: w["t"])


def phrases(words: list[dict], gap: float) -> list[Phrase]:
    out = []
    for i, w in enumerate(words):
        if out and w["t"] - out[-1].e < gap:
            out[-1].e = max(out[-1].e, w["e"]); out[-1].i1 = i
        else:
            out.append(Phrase(w["t"], w["e"], i, i))
    return out


# ---------------------------------------------------------------- voice


TARGET_SPEECH = {   # house target, dB relative to 250 Hz: the long-term average speech spectrum's shape (peak 200-500 Hz,
    80: -10, 100: -6, 125: -3, 160: -1.5, 200: -0.5, 250: 0, 315: -0.5, 400: -1.5, 500: -2.5, 630: -3.5,   # about -5 dB per
    800: -5, 1000: -6, 1250: -7, 1600: -8.5, 2000: -9.5, 2500: -10.5, 3150: -11, 4000: -12.5,              # octave above
    5000: -14, 6300: -16, 8000: -18.5, 10000: -21, 12500: -24}                                              # 500 Hz) + 1-2 dB presence


def _band_edges(fc):
    return fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)


def voice_master(y: np.ndarray, words: list[dict], rules: dict | None = None, log=print) -> tuple[np.ndarray, dict]:
    """Clean and balance a voice track whose words are on the same clock. Returns (voice, report)."""
    R = dict(SOUND_RULES["voice"], **(rules or {}))
    n = len(y)
    rep = {}
    # 1. speech mask at 10 ms
    act = np.zeros(n // 480 + 2, bool)
    for w in words:
        act[max(0, int((w["t"] - 0.05) * 100)): int((w["e"] + 0.05) * 100) + 1] = True
    # 2. wind / rumble check on the pauses: share of energy under 150 Hz
    gap_idx = np.where(~act)[0]
    sos_lo = signal.butter(4, 150, "lowpass", fs=SR, output="sos")
    lo = signal.sosfiltfilt(sos_lo, y)
    if len(gap_idx) > 50:
        gmask = np.repeat(~act, 480)[:n] & (np.abs(y) > 1e-6)
        ratio = float((lo[gmask] ** 2).sum() / ((y[gmask] ** 2).sum() + 1e-12))
    else:
        ratio = 0.0
    hp = R["highpass_wind_hz"] if ratio > R["wind_ratio"] else R["highpass_hz"]
    rep["low_rumble_share_in_pauses"] = round(ratio, 3)
    rep["highpass_hz"] = hp
    y = signal.sosfiltfilt(signal.butter(2, hp, "highpass", fs=SR, output="sos"), y)

    # 3. STFT: noise profile from the pauses, gentle spectral subtraction, corrective EQ, frame-wise de-ess
    nfft, hop = 2048, 512
    f, t, X = signal.stft(y, SR, nperseg=nfft, noverlap=nfft - hop, boundary="even", padded=True)
    mag = np.abs(X)
    fr_act = np.array([act[min(len(act) - 1, int(tt * 100))] for tt in t])
    live = (mag ** 2).sum(0) > (mag ** 2).sum(0).max() * 1e-9        # digital silence (an end card, a gap) is not room tone
    noise_frames = mag[:, ~fr_act & live]
    if noise_frames.shape[1] < 40:
        noise = np.percentile(mag, 10, axis=1)
        rep["noise_profile"] = "10th percentile of all frames (few pauses)"
    else:
        noise = np.median(noise_frames, axis=1)
        rep["noise_profile"] = f"median of {noise_frames.shape[1]} pause frames"
    floor = undb(-R["denoise_max_db"])
    from scipy.ndimage import median_filter, uniform_filter
    if R.get("denoise", "wiener") == "wiener":
        # decision-directed Wiener gain (Ephraim and Malah 1984): the a-priori SNR leans on the last frame's clean
        # estimate, which keeps the residual noise smooth instead of twinkling
        Np = (noise ** 2)[:, None] * R["denoise_oversub"]
        P = mag ** 2
        g = np.empty_like(mag)
        prev = np.zeros(mag.shape[0])
        a = R.get("dd_alpha", 0.98)
        for j in range(mag.shape[1]):
            gam = P[:, j] / Np[:, 0]
            xi = a * prev / Np[:, 0] + (1 - a) * np.maximum(gam - 1, 0)
            gj = np.maximum(xi / (1 + xi), floor)
            g[:, j] = gj
            prev = (gj * mag[:, j]) ** 2
        g = uniform_filter(g, size=(3, 3))
    else:
        g = 1 - R["denoise_oversub"] * (noise[:, None] / (mag + 1e-9)) ** 2
        g = np.clip(g, floor ** 2, 1.0) ** 0.5
        g = uniform_filter(g, size=(3, 5))                # smooth across 3 bins and 5 frames: no musical noise
    # steady tones in the room (a whine, a hum harmonic): bins that stand over their neighbourhood get notched always
    nd = 20 * np.log10(noise + 1e-12)
    over = nd - median_filter(nd, size=31)
    tone = (over > R["tone_notch_over_db"]) & (f > 150)
    notch = np.where(tone, undb(-np.clip(over, 0, R["tone_notch_max_db"])), 1.0)
    rep["tones_notched_hz"] = sorted({int(round(x, -1)) for x in f[tone]})[:12]
    g = g * notch[:, None]
    # wind bursts: frames whose energy under 150 Hz jumps over its voiced median get a low shelf cut, only on those frames
    lowE = 10 * np.log10((mag[f < 150] ** 2).sum(0) + 1e-20)
    med = np.median(lowE[fr_act]) if fr_act.any() else np.median(lowE)
    burst = np.clip(lowE - med - R["wind_burst_over_db"], 0, R["wind_burst_cut_db"])
    burst = np.convolve(burst, np.ones(3) / 3, "same")
    shelf = np.clip(1 - f / R["wind_burst_hz"], 0, 1)[:, None]
    g = g * undb(-shelf * burst[None, :])
    rep["wind_burst_frames"] = int((burst > 1).sum())
    gm = np.repeat(~act, 480)[:n] & (np.abs(y) > 1e-6)
    rep["room_tone_dbfs"] = round(float(db(np.sqrt((y[gm] ** 2).mean()))), 1) if gm.any() else None

    # corrective EQ toward the target curve, measured on speech frames after noise reduction
    sp = (mag * g)[:, fr_act] if fr_act.any() else mag * g
    ltas = (sp ** 2).mean(1)
    fcs = np.array(sorted(TARGET_SPEECH))
    meas = []
    for fc in fcs:
        lo_e, hi_e = _band_edges(fc)
        sel = (f >= lo_e) & (f < hi_e)
        meas.append(10 * np.log10(ltas[sel].mean() + 1e-20) if sel.any() else np.nan)
    meas = np.array(meas)
    tgt = np.array([TARGET_SPEECH[k] for k in fcs])
    ref = (fcs >= 200) & (fcs <= 4000) & ~np.isnan(meas)
    off = np.nanmean(meas[ref] - tgt[ref])
    corr = np.nan_to_num(tgt + off - meas)
    corr = np.convolve(np.pad(corr, 1, mode="edge"), np.ones(3) / 3, "valid") * R["eq_apply"]
    cap = np.where(fcs >= 6000, R["eq_max_boost_above_6k_db"], R["eq_max_boost_db"])      # cut before you boost:
    corr = np.clip(corr, -R["eq_max_cut_db"], cap)                                           # boosts stay small, highs smaller
    rep["eq_db"] = {int(k): round(float(v), 1) for k, v in zip(fcs, corr)}
    eq_bins = undb(np.interp(np.log2(np.maximum(f, 20)), np.log2(fcs), corr))
    # de-ess: frames whose sibilance band runs hot against the speech body
    sib = (f >= R["deess_band_hz"][0]) & (f <= R["deess_band_hz"][1])
    body = (f >= 1000) & (f <= 4000)
    P = (mag * g * eq_bins[:, None]) ** 2
    ratio_db = 10 * np.log10(P[sib].sum(0) + 1e-20) - 10 * np.log10(P[body].sum(0) + 1e-20)
    base = np.median(ratio_db[fr_act]) if fr_act.any() else np.median(ratio_db)
    over = np.clip(ratio_db - base - R["deess_trigger_db"], 0, None)
    cut = np.clip(over, 0, R["deess_max_db"])
    cut = np.convolve(cut, np.ones(3) / 3, "same")
    rep["deess_frames"] = int((cut > 0.5).sum())
    G = g * eq_bins[:, None]
    G[sib] *= undb(-cut)[None, :]
    _, yv = signal.istft(X * G, SR, nperseg=nfft, noverlap=nfft - hop, boundary=True)
    y = yv[:n] if len(yv) >= n else np.pad(yv, (0, n - len(yv)))

    # 4. breaths: kept, 10 dB lower
    env = np.sqrt(np.convolve(y ** 2, np.ones(960) / 960, "same"))
    gm2 = np.repeat(~act, 480)[:n] & (env > 1e-6)
    nf = float(np.percentile(env[gm2], 50)) if gm2.any() else 1e-4
    gain = np.ones(n)
    breaths = 0
    for a, b in zip(words[:-1], words[1:]):
        s, e = a["e"] + 0.03, b["t"] - 0.03
        if not (R["breath_min_s"] <= e - s <= R["breath_max_s"]):
            continue
        i0, i1 = int(s * SR), int(e * SR)
        if i1 <= i0 or env[i0:i1].max() < nf * 2.8:        # ~9 dB over the room: something is breathing
            continue
        gain[i0:i1] = min(gain[i0:i1].min(), undb(-R["breath_cut_db"]))
        breaths += 1
    gain = _smooth_gain(gain, 0.02)
    y = y * gain
    rep["breaths_lowered"] = breaths

    # 5. clip gain per phrase: 70 % of the way to the median phrase loudness, at most 6 dB
    ph = phrases(words, R["phrase_gap_s"])
    lv = []
    for p in ph:
        seg = y[int(p.s * SR): int(p.e * SR)]
        lv.append(10 * np.log10((seg ** 2).mean() + 1e-12) if len(seg) > 480 else np.nan)
    lv = np.array(lv)
    med = np.nanmedian(lv) if len(lv) else 0
    cg = np.ones(n)
    for p, l in zip(ph, lv):
        if np.isnan(l):
            continue
        d = float(np.clip((med - l) * R["clip_gain_apply"], -R["clip_gain_max_db"], R["clip_gain_max_db"]))
        cg[max(0, int((p.s - 0.03) * SR)): int((p.e + 0.03) * SR)] = undb(d)
    cg = _smooth_gain(cg, 0.06)
    y = y * cg
    rep["phrases"] = len(ph)
    rep["phrase_spread_db_before"] = round(float(np.nanpercentile(lv, 90) - np.nanpercentile(lv, 10)), 1) if len(lv) > 2 else 0

    # 6. dynamics: slow leveller then fast peak catcher (feed-forward, numpy)
    y = _normalize(y, -20.0)
    if R["level_ratio"] > 1:
        y = compressor(y, threshold_db=R["level_threshold_db"], ratio=R["level_ratio"], attack=0.015, release=0.18, knee=6)
    if R["peak_ratio"] > 1:
        y = compressor(y, threshold_db=R["peak_threshold_db"], ratio=R["peak_ratio"], attack=0.001, release=0.05, knee=2, detect="peak")
    y = _normalize(y, R["stem_lufs"])
    # room between sentences: down pause_cut_db after the dynamics (a compressor would lift it again), kept inside a phrase
    pg = np.ones(n)
    for a, b in zip(words[:-1], words[1:]):
        s0, s1 = a["e"] + R["pause_margin_s"], b["t"] - R["pause_margin_s"]
        if s1 - s0 >= R["pause_min_s"]:
            pg[int(s0 * SR): int(s1 * SR)] = undb(-R["pause_cut_db"])
    if words:
        pg[: max(0, int((words[0]["t"] - R["pause_margin_s"]) * SR))] = undb(-R["pause_cut_db"])
        pg[int((words[-1]["e"] + R["pause_margin_s"]) * SR):] = undb(-R["pause_cut_db"])
    y = y * _smooth_gain(pg, 0.03)
    rep["stem_lufs"] = round(lufs(y), 1)       # one static gain, no limiter on the voice stem (the mix limiter catches peaks)
    return y.astype(np.float32), rep


def _smooth_gain(g, ramp_s):
    k = max(1, int(ramp_s * SR))
    return np.convolve(np.pad(g, (k, k), mode="edge"), np.ones(k) / k, "same")[k:-k]


def _normalize(y, target):
    l = lufs(y)
    return y * undb(target - l) if l > -69 else y


def compressor(y, threshold_db, ratio, attack, release, knee=4.0, detect="rms"):
    """Feed-forward compressor on a level detector (rms over 10 ms, or peak), soft knee, smoothed gain."""
    x = y if y.ndim == 1 else y.mean(1)
    if detect == "rms":
        lvl = np.sqrt(np.convolve(x ** 2, np.ones(480) / 480, "same") + 1e-12)
    else:
        lvl = np.abs(x) + 1e-12
    L = db(lvl)
    over = L - threshold_db
    gr = np.where(over <= -knee / 2, 0.0,
                  np.where(over >= knee / 2, over * (1 - 1 / ratio), (1 - 1 / ratio) * (over + knee / 2) ** 2 / (2 * knee)))
    gr = _ar_smooth(gr, attack, release)
    g = undb(-gr)
    return y * (g if y.ndim == 1 else g[:, None])


def _ar_smooth(x, attack, release):
    """One-pole attack/release smoothing of a gain-reduction curve (dB); rises with attack, falls with release."""
    a = math.exp(-1 / (attack * SR)); r = math.exp(-1 / (release * SR))
    # decimate for speed: work at 1 kHz, then interpolate
    step = 48
    xs = x[::step]
    out = np.empty_like(xs); s = 0.0
    a2 = a ** step; r2 = r ** step
    for i, v in enumerate(xs):
        c = a2 if v > s else r2
        s = c * s + (1 - c) * v
        out[i] = s
    return np.interp(np.arange(len(x)), np.arange(len(xs)) * step, out)


def limiter(y, ceiling_db=-1.0, lookahead=0.005, release=0.06):
    x = np.abs(y) if y.ndim == 1 else np.abs(y).max(1)
    need = np.maximum(0, db(x) - ceiling_db)
    need = _maxfilt(need, int(lookahead * SR))          # look ahead: the gain is already down when the peak arrives
    gr = _ar_smooth(need, 0.0005, release)
    gr = np.maximum(gr, need)
    g = undb(-gr)
    return y * (g if y.ndim == 1 else g[:, None])


def _maxfilt(x, k):
    from scipy.ndimage import maximum_filter1d
    return maximum_filter1d(x, size=2 * k + 1, origin=0)


# ---------------------------------------------------------------- music


def track_profile(path: Path) -> dict:
    """Measured traits of a music track: tempo, beats and bars, mode, energy per bar, how much it sits in the voice band,
    whether it builds, and its sections. librosa (ISC licence) does the beat tracking."""
    import librosa
    y, sr = librosa.load(str(path), sr=22050, mono=True)
    dur = len(y) / sr
    oenv = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, units="frames")
    tempo = float(np.atleast_1d(tempo)[0])
    bt = librosa.frames_to_time(beats, sr=sr)
    # downbeat phase: the beat index mod 4 with the most low-end and onset energy
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    fq = librosa.fft_frequencies(sr=sr, n_fft=2048)
    low = S[fq < 150].sum(0)
    score = [sum(oenv[b] + low[b] / (low.max() + 1e-9) for b in beats[k::4] if b < len(oenv)) for k in range(4)]
    ph = int(np.argmax(score)) if len(beats) >= 8 else 0
    bars = bt[ph::4]
    # bar energy (dB) and voice-band share
    rms = librosa.feature.rms(S=S)[0]
    tt = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
    bar_db = []
    for a, b in zip(bars[:-1], bars[1:]):
        sel = (tt >= a) & (tt < b)
        bar_db.append(float(db(rms[sel].mean())) if sel.any() else -80.0)
    vb = S[(fq >= 1000) & (fq <= 4000)].sum() / (S[(fq >= 60)].sum() + 1e-9)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(1)
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    cm = max(np.corrcoef(np.roll(major, k), chroma)[0, 1] for k in range(12))
    cn = max(np.corrcoef(np.roll(minor, k), chroma)[0, 1] for k in range(12))
    bd = np.array(bar_db) if bar_db else np.zeros(1)
    q = max(1, len(bd) // 4)
    build = float(np.median(bd[q:2 * q + 1]) - np.median(bd[:q])) if len(bd) >= 8 else 0.0
    cent = float(librosa.feature.spectral_centroid(S=S, sr=sr).mean())
    # sections: change points of a bar-level feature (energy + timbre)
    mf = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    secs = []
    if len(bars) > 8:
        feats = []
        for a, b in zip(bars[:-1], bars[1:]):
            sel = (tt >= a) & (tt < b)
            feats.append(mf[:, sel[:mf.shape[1]]].mean(1) if sel[:mf.shape[1]].any() else np.zeros(13))
        F = np.array(feats)
        dif = np.r_[0, np.linalg.norm(np.diff(F, axis=0), axis=1)]
        thr = np.percentile(dif, 88)
        secs = [float(bars[i]) for i in range(1, len(dif)) if dif[i] >= thr and (not secs or bars[i] - secs[-1] > 6)]
    return {"file": str(path), "dur": round(dur, 2), "tempo": round(tempo, 1), "beats": [round(float(b), 3) for b in bt],
            "bars": [round(float(b), 3) for b in bars], "bar_db": [round(v, 1) for v in bar_db], "mode": "minor" if cn > cm else "major",
            "mode_conf": round(abs(cn - cm), 3), "voice_band": round(float(vb), 3), "build_db": round(build, 1),
            "centroid_hz": round(cent), "sections": [round(s, 2) for s in secs]}


def score_track(p: dict, need_s: float, rules: dict | None = None) -> tuple[float, list[str]]:
    """How well a measured track fits a talking-head VSL bed. Higher is better; reasons say why."""
    R = dict(SOUND_RULES["music"]["pick"], **(rules or {}))
    s, why = 0.0, []
    t = p["tempo"]
    t_eff = t if R["tempo"][0] <= t <= R["tempo"][1] else (t / 2 if R["tempo"][0] <= t / 2 <= R["tempo"][1] else t)
    if R["tempo"][0] <= t_eff <= R["tempo"][1]:
        s += 2; why.append(f"tempo {t_eff:.0f} sits under speech")
    else:
        s -= 1; why.append(f"tempo {t:.0f} fights speech rhythm")
    if p["voice_band"] <= R["voice_band_max"]:
        s += 2 * (R["voice_band_max"] - p["voice_band"]) / R["voice_band_max"] + 1; why.append(f"voice band share {p['voice_band']:.2f} leaves room for words")
    else:
        s -= 2; why.append(f"voice band share {p['voice_band']:.2f} masks words")
    if R["prefer_minor"] and p["mode"] == "minor":
        s += 0.8; why.append("minor mode (tension, documentary)")
    if R["want_build"] and p["build_db"] >= 2:
        s += min(2, p["build_db"] / 3); why.append(f"builds {p['build_db']:+.1f} dB after the intro")
    if p["dur"] < need_s * 0.6:
        s -= 1.5; why.append("short: needs looping")
    bd = np.array(p["bar_db"]) if p["bar_db"] else np.zeros(1)
    if len(bd) > 4 and (bd.max() - np.percentile(bd, 20)) > 18:
        s -= 1; why.append("big dynamic jumps (would poke out of the bed)")
    if p["centroid_hz"] > 3200:
        s -= 1; why.append("bright: hiss and cymbals in the voice range")
    return round(s, 2), why


def fit_music(path: Path, prof: dict, length: float, land: float | None = None, rules: dict | None = None) -> tuple[np.ndarray, dict]:
    """Cut a track to length the way an editor does, on bar lines, so it ends on its own ending at the video's end.

    Long track: the body starts on a bar in the first 40 % (chosen so a section change lands near `land`, a lift on the
    proof or the ask), then splices into the track's last bars at a bar line. Short track: it plays from the top and is
    extended by repeating a run of bars whose loudness matches across the splice, never by restarting from zero."""
    R = dict(SOUND_RULES["music"], **(rules or {}))
    full = read_audio(path, mono=False)
    dur = len(full) / SR
    bars = np.array(prof["bars"]) if len(prof["bars"]) > 4 else np.arange(0, dur, 2.0)
    bar_db = np.array(prof["bar_db"]) if prof["bar_db"] else np.zeros(max(1, len(bars) - 1))
    secs = np.array(prof["sections"])
    need = length + 0.5
    x = int(R["splice_xfade_s"] * SR)

    def splice(a_seg, b_seg):
        if len(a_seg) < x or len(b_seg) < x:
            return np.concatenate([a_seg, b_seg])
        w = np.linspace(0, 1, x)[:, None]
        return np.concatenate([a_seg[:-x], a_seg[-x:] * np.sqrt(1 - w) + b_seg[:x] * np.sqrt(w), b_seg[x:]])

    S = lambda t: int(round(t * SR))
    if dur >= need + 2:
        tail_start = bars[-4] if len(bars) >= 6 else dur - 8
        tail_len = dur - tail_start
        body_len = need - tail_len
        cands = [bb for bb in bars if bb <= 0.4 * dur and bb + body_len <= tail_start + 0.01] or [0.0]
        best, best_cost = cands[0], 1e9
        for bb in cands:
            cost = bb * 0.02
            if land is not None and len(secs):
                hits = secs[(secs > bb) & (secs < bb + body_len)] - bb
                cost += float(min(abs(hits - land))) if len(hits) else 6.0
            if cost < best_cost:
                best, best_cost = bb, cost
        # the splice into the ending sits on the bar nearest best + body_len
        cut_at = float(bars[np.argmin(abs(bars - (best + body_len)))])   # on a bar line, so the beat never stumbles
        y = splice(full[S(best):S(cut_at)], full[S(tail_start):])
        how = f"body from {best:.2f} s, spliced on a bar into its ending at {tail_start:.2f} s"
        start = best
    else:
        y, start, how = full, 0.0, "plays from the top"
        bl = float(np.median(np.diff(bars))) if len(bars) > 2 else 2.0
        guard = 0
        while len(y) / SR < need and guard < 8:
            short = need - len(y) / SR
            k = max(2, int(math.ceil(short / bl / 2) * 2))           # repeat an even number of bars
            k = min(k, max(2, len(bar_db) // 2))
            # the bar pair (i, i+k) in the middle of the track whose loudness matches best
            lo, hi = len(bar_db) // 5, len(bar_db) - k - 4
            if hi <= lo:
                break
            i = min(range(lo, hi), key=lambda j: abs(bar_db[j] - bar_db[j + k]))
            a_t, b_t = bars[i + k], bars[i]
            y = splice(y[:S(a_t)], y[S(b_t):])
            how += f"; repeated bars {i}-{i + k} ({a_t - b_t:.1f} s)"
            guard += 1
    n = S(need)
    if len(y) < n:
        y = np.pad(y, ((0, n - len(y)), (0, 0)))
    y = y[:n]
    return y.astype(np.float32), {"start": round(float(start), 3), "how": how, "tempo": prof["tempo"],
                                  "bars_after_start": [round(float(bb - start), 3) for bb in bars if bb >= start]}


def music_automation(n: int, words: list[dict], total: float, speech_end: float, drops=(), rules: dict | None = None,
                     bars=None, sections=None) -> tuple[np.ndarray, list]:
    """The fader ride, in dB at the sample rate, the way an engineer draws it from the words: level under speech is 0 dB
    (the section gain sets it), up gap_lift in a real pause (more in the hook), down before a phrase starts, out for a
    drop that starts drop_lead before its line and comes back on the next downbeat, a lift across the CTA, a rise into
    the end card, a fade. Returns (gain_db, drops_used) where drops_used carry their real return time."""
    R = dict(SOUND_RULES["music"], **(rules or {}))
    fs = 100
    m = int(total * fs) + fs
    tl = np.arange(m) / fs
    g = np.zeros(m)
    lift = np.where(tl < R["hook_s"], R["gap_lift_hook_db"], R["gap_lift_db"])
    gap = np.ones(m, bool)
    for p in phrases(words, R["gap_min_s"]):
        gap[(tl >= p.s - R["duck_lead_s"]) & (tl <= p.e + R["lift_delay_s"])] = False
    gap[tl > speech_end] = False
    g = np.where(gap, lift, 0.0)
    g = _asym_ramp(g, fs, R["duck_ramp_s"], R["lift_ramp_s"])
    for sec in sections or []:
        if sec.get("name") == "cta":
            g[(tl >= sec["a"]) & (tl < min(sec["b"], speech_end))] += R["cta_lift_db"]
    out_mask = tl > speech_end + 0.2
    g[out_mask] = np.minimum(R["outro_lift_db"], (tl[out_mask] - speech_end - 0.2) / R["outro_ramp_s"] * R["outro_lift_db"])
    fo = tl > total - R["fade_out_s"]
    g[fo] += 40 * np.log10(np.clip((total - tl[fo]) / R["fade_out_s"], 1e-3, 1))
    bars = np.array(bars) if bars is not None and len(bars) else None
    used = []
    for a, b in list(drops)[:R["drops_max"]]:
        a0 = a - R["drop_lead_s"]
        if bars is not None:
            nxt = bars[bars >= b - 0.05]
            if len(nxt) and nxt[0] - b <= R["return_downbeat_within_s"]:
                b = float(nxt[0])
        k0, k1 = int(a0 * fs), int(b * fs)
        g[k0:k1] = R["drop_db"]
        r0 = max(1, int(R["drop_ramp_s"] * fs))
        g[max(0, k0 - r0):k0] = np.minimum(g[max(0, k0 - r0):k0], np.linspace(0, R["drop_db"], len(g[max(0, k0 - r0):k0])))
        used.append((round(a0, 3), round(b, 3)))
    return np.interp(np.arange(n) / SR, tl, g), used


def _asym_ramp(x, fs, down_s, up_s):
    """Slew-limit a step curve: falling edges take down_s, rising edges up_s."""
    y = x.copy()
    span = (x.max() - x.min() + 1e-9)
    dn, up = span / max(1, down_s * fs), span / max(1, up_s * fs)
    for i in range(1, len(y)):
        d = x[i] - y[i - 1]
        y[i] = y[i - 1] + (min(d, up) if d > 0 else max(d, -dn))
    return y


def music_stem(bed: np.ndarray, voice: np.ndarray, words: list[dict], gain_db: np.ndarray, sections: list[dict],
               rules: dict | None = None) -> tuple[np.ndarray, dict]:
    """The bed under the voice: a static pocket at 300 Hz to 4 kHz, a dynamic pocket while words play sized by how much
    the track lives in the voice band, then section gains set so the voice leads the music by each section's target
    (median of momentary voice minus music on word frames), measured, corrected once, measured again."""
    R = dict(SOUND_RULES["music"], **(rules or {}))
    n = len(bed)
    x = signal.sosfiltfilt(signal.butter(2, 35, "highpass", fs=SR, output="sos"), bed, axis=0)
    sos_bp = signal.butter(2, R["pocket_hz"], "bandpass", fs=SR, output="sos")
    mid = signal.sosfiltfilt(sos_bp, x, axis=0)
    share = 10 * np.log10(((signal.sosfiltfilt(signal.butter(2, [1000, 4000], "bandpass", fs=SR, output="sos"), x.mean(1))) ** 2).mean() /
                          ((x.mean(1) ** 2).mean() + 1e-20) + 1e-20)
    dyn = -4.0 if share > -15 else -2.0 if share > -19 else 0.0
    speak = np.zeros(n)
    for w in words:
        speak[max(0, int((w["t"] - R["duck_lead_s"]) * SR)): int((w["e"] + R["lift_delay_s"]) * SR)] = 1
    speak = _smooth_gain(speak, 0.15)
    pocket = undb(R["pocket_static_db"] + dyn * speak) if dyn else np.full(n, undb(R["pocket_static_db"]))
    x = x - (1 - pocket)[:, None] * mid
    x = x * undb(gain_db)[:, None]
    # section calibration on word frames
    tv, lv = loudness_curve(voice)
    word_fr = np.zeros(len(tv), bool)
    for w in words:
        word_fr |= (tv >= w["t"]) & (tv <= w["e"])
    word_fr &= lv > -50
    sec_gain = np.zeros(n)
    report = []
    for it in range(2):
        tm, lm = loudness_curve(x * undb(sec_gain)[:, None])
        rows = []
        for sec in sections:
            sel = word_fr & (tv >= sec["a"]) & (tv < sec["b"])
            d = (lv - lm[:len(lv)])[sel] if sel.any() else np.array([])
            med = float(np.median(d)) if len(d) else None
            p10 = float(np.percentile(d, 10)) if len(d) else None
            rows.append({"name": sec["name"], "a": round(sec["a"], 2), "b": round(sec["b"], 2), "target_vm": sec["vm"],
                         "vm_median": None if med is None else round(med, 1), "vm_p10": None if p10 is None else round(p10, 1), "p10_min": sec["p10"]})
            if it == 0 and med is not None:
                corr = float(np.clip(med - sec["vm"], -24, 24))
                sec_gain[int(sec["a"] * SR): int(sec["b"] * SR)] += corr
        if it == 0:
            sec_gain = _smooth_gain(sec_gain, 0.5)
        report = rows
    x = x * undb(sec_gain)[:, None]
    return x.astype(np.float32), {"pocket_dynamic_db": dyn, "bed_1k4k_share_db": round(float(share), 1), "sections": report}


# ---------------------------------------------------------------- sound effects


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def _pink(n, seed):
    w = _noise(n, seed)
    b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w)


def _sweep_bp(x, f0, f1, shape, q=1.2):
    """Band-pass with a moving centre (block-wise biquads, 256-sample blocks)."""
    y = np.zeros_like(x)
    zi = None
    blk = 256
    for i in range(0, len(x), blk):
        k = i / max(1, len(x) - 1)
        fc = f0 * (f1 / f0) ** shape(k)
        bw = fc / q
        lo, hi = max(20, fc - bw / 2), min(SR / 2 - 100, fc + bw / 2)
        sos = signal.butter(2, [lo, hi], "bandpass", fs=SR, output="sos")
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = signal.sosfilt_zi(sos) * 0
        y[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    return y


def sfx_whoosh(dur=0.6, peak=0.62, seed=1):
    """Air past the camera: pink noise in a band that rises to the peak then falls, slow swell in, fast fall,
    a low swish layer under it, panned left to right. The peak sits at `peak` of the length (aligned to the cut)."""
    n = int(dur * SR); t = np.arange(n) / n
    shape = lambda k: (k / peak) if k < peak else 1 - (k - peak) / (1 - peak) * 0.6
    air = _sweep_bp(_pink(n, seed), 500, 4200, shape, q=1.0)
    low = signal.sosfilt(signal.butter(2, [70, 350], "bandpass", fs=SR, output="sos"), _pink(n, seed + 1))
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5))
    y = (air + 0.35 * low / (np.abs(low).max() + 1e-9) * np.abs(air).max()) * env
    pan = np.clip(t * 1.4 - 0.2, 0, 1)
    st = np.stack([y * np.sqrt(1 - pan * 0.7), y * np.sqrt(0.3 + pan * 0.7)], 1)
    return _norm_peak(st), peak * dur


def sfx_impact(seed=2):
    """A cinematic hit: sub sweep 58 to 32 Hz (0.9 s decay), a body thump 140 to 80 Hz, a 3 ms transient, a short room."""
    n = int(1.4 * SR); t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(58 * (32 / 58) ** np.minimum(t / 0.6, 1)) / SR) * np.exp(-t * 3.2)
    body = np.sin(2 * np.pi * np.cumsum(140 * (80 / 140) ** np.minimum(t / 0.12, 1)) / SR) * np.exp(-t * 16)
    tr = np.zeros(n); k = int(0.003 * SR)
    tr[:k] = signal.sosfilt(signal.butter(2, 2000, "highpass", fs=SR, output="sos"), _noise(k, seed)) * np.linspace(1, 0, k)
    room = signal.fftconvolve(body * 0.5 + tr, _noise(int(0.45 * SR), seed + 3) * np.exp(-np.arange(int(0.45 * SR)) / SR * 9) * 0.04)[:n]
    y = 1.0 * sub + 0.6 * body + 0.5 * tr + room
    return _norm_peak(np.stack([y, y], 1)), 0.0


def sfx_riser(dur=2.2, seed=3):
    """Tension into a drop: a noise band 250 Hz to 7 kHz plus two detuned saws a fifth apart rising an octave,
    a low-pass that opens, volume on a curve, then dead silence at the end (the drop)."""
    n = int(dur * SR); t = np.arange(n) / n
    nz = _sweep_bp(_pink(n, seed), 250, 7000, lambda k: k ** 1.6, q=1.4)
    f = 110 * 2 ** (t ** 1.4)
    saw = sum(signal.sawtooth(2 * np.pi * np.cumsum(f * m * (1 + d)) / SR) for m in (1, 1.5) for d in (-0.004, 0.004))
    saw = signal.sosfilt(signal.butter(2, 1800, "lowpass", fs=SR, output="sos"), saw)
    y = (nz / (np.abs(nz).max() + 1e-9) + 0.25 * saw / (np.abs(saw).max() + 1e-9)) * t ** 2.4
    y[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    w = np.stack([y * (1 - 0.15 * t), y * (0.85 + 0.15 * t)], 1)
    return _norm_peak(w), dur


def sfx_tick(seed=4):
    """A UI tick for an element landing: 1.6 kHz blip with a small pitch drop and a click, 60 ms."""
    n = int(0.07 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(1600 * (1200 / 1600) ** (t / 0.07)) / SR) * np.exp(-t * 70)
    k = int(0.004 * SR); y[:k] += 0.4 * _noise(k, seed) * np.linspace(1, 0, k)
    return _norm_peak(np.stack([y, y], 1)), 0.0


def sfx_swish(seed=5):
    """A short high swish for text sliding in (0.22 s, band 3 to 9 kHz)."""
    n = int(0.22 * SR); t = np.arange(n) / n
    y = _sweep_bp(_pink(n, seed), 3000, 9000, lambda k: k, q=1.5) * np.sin(np.pi * t) ** 1.5
    return _norm_peak(np.stack([y, y], 1)), 0.11


def sfx_subdrop(seed=6):
    n = int(1.0 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(90 * (28 / 90) ** (t / 1.0)) / SR) * np.exp(-t * 2.6)
    return _norm_peak(np.stack([y, y], 1)), 0.0


def sfx_swell(dur=0.9, seed=7):
    """Reverse swell into a cut: a decaying noise burst through a low-pass, reversed, ending at the cut."""
    n = int(dur * SR); t = np.arange(n) / SR
    y = signal.sosfilt(signal.butter(2, 2500, "lowpass", fs=SR, output="sos"), _pink(n, seed)) * np.exp(-t * 5)
    y = y[::-1]
    return _norm_peak(np.stack([y, y * 0.95], 1)), dur


def sfx_shine(seed=8):
    """A bright ding for a number landing: inharmonic bell partials with fast decays and a soft air layer, 1.2 s."""
    n = int(1.2 * SR); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((1568, 1.0, 4.0), (2349, 0.6, 5.5), (3136, 0.45, 7.0), (4186, 0.3, 9.0), (5274, 0.2, 12.0)))
    air = signal.sosfilt(signal.butter(2, 6000, "highpass", fs=SR, output="sos"), _pink(n, seed)) * np.exp(-t * 6) * 0.15
    y = y + air * np.abs(y).max()
    return _norm_peak(np.stack([y, y * 0.97], 1)), 0.0


SYNTH = {"whoosh": sfx_whoosh, "impact": sfx_impact, "riser": sfx_riser, "tick": sfx_tick, "swish": sfx_swish,
         "sub": sfx_subdrop, "reverse": sfx_swell, "shine": sfx_shine}
SFX = SYNTH


def _norm_peak(y, p=0.9):
    return (y / (np.abs(y).max() + 1e-9) * p).astype(np.float32)


class Library:
    """Recorded sound effects in a folder, named <role>__<anything>.<ext> (whoosh, swish, impact, sub, shine, tick,
    riser, reverse). Each file is measured once: onset (first point within 30 dB of its peak), peak (the envelope's
    maximum), end (where it falls 20 dB under its peak for good) and its loudest 400 ms. Missing roles fall back to the
    synthesized set, and the report says so."""

    def __init__(self, folder: Path | None):
        self.items, self.used = {}, {}
        if not folder or not Path(folder).exists():
            return
        idx_file = Path(folder) / "index.json"
        idx = json.loads(idx_file.read_text()) if idx_file.exists() else {}
        changed = False
        for f in sorted(Path(folder).iterdir()):
            if f.suffix.lower() not in (".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aif", ".aiff") or "__" not in f.stem:
                continue
            role = f.stem.split("__")[0]
            if f.name not in idx:
                y = read_audio(f, mono=False)
                env = np.convolve(np.abs(y).max(1), np.ones(480) / 480, "same")
                pk = int(env.argmax()); top = env[pk] + 1e-9
                on = int(np.argmax(env > top * undb(-30)))
                after = np.where(env[pk:] > top * undb(-20))[0]
                end = pk + int(after[-1]) if len(after) else len(env) - 1
                _, m = loudness_curve(y)
                idx[f.name] = {"role": role, "onset": on / SR, "peak": pk / SR, "end": end / SR, "max_m": float(m.max()), "dur": len(y) / SR}
                changed = True
            self.items.setdefault(role, []).append((f, idx[f.name]))
        if changed:
            idx_file.write_text(json.dumps(idx, indent=1))

    def pick(self, role: str):
        """(audio, meta, source) for a role, rotating through the files so one sound never plays three times running."""
        files = self.items.get(role)
        if not files:
            y, hit = SYNTH[role]()
            _, m = loudness_curve(y)
            al = SOUND_RULES["sfx"]["align"].get(role, "onset")
            meta = {"onset": 0.0, "peak": hit, "end": len(y) / SR if al == "end" else hit, "max_m": float(m.max())}
            if role in ("riser",):
                meta["end"] = hit
            return y, meta, "synth"
        k = self.used.get(role, -1) + 1
        self.used[role] = k
        f, meta = files[k % len(files)]
        return read_audio(f, mono=False), meta, f.name


PRIORITY = {"number_reveal": 6, "cta_riser": 5, "section_change": 4, "card_in": 3, "drop_return": 3, "end_card": 3,
            "punch_in_hook": 2, "chip": 1, "pointer": 1, "card_element": 0, "hand_label": 0, "hard_cut": 0, "punch_in": 0, "card_out": 0}


def plan_sfx(events: list[dict], words: list[dict], rules: dict | None = None, total: float = 0.0) -> tuple[list[dict], list[dict]]:
    """Events (kind = an edit event: card_in, chip, section_change, number_reveal, cta_riser, pointer, end_card,
    punch_in, drop_return ...; at = its frame) become sounds by the dialect's grammar, then the density budget keeps the
    ones that matter most: a dry cut is a choice, not a gap."""
    R = dict(SOUND_RULES["sfx"], **(rules or {}))
    G = R["grammar"][R["dialect"]]
    D = R["density"][R["dialect"]]
    ev = sorted(events, key=lambda e: (-PRIORITY.get(e["kind"], 0), e["at"]))
    kept, dropped = [], []
    for e in ev:
        kind = "punch_in_hook" if e["kind"] == "punch_in" and e["at"] < SOUND_RULES["music"]["hook_s"] else e["kind"]
        roles = G.get(kind, [])
        if not roles:
            dropped.append(dict(e, reason=f"left dry ({R['dialect']} grammar)")); continue
        if any(abs(k["at"] - e["at"]) < R["min_gap_s"] for k in kept):
            dropped.append(dict(e, reason="crowded")); continue
        n20 = sum(1 for k in kept if k["at"] < 20)
        if e["at"] < 20 and n20 >= D["first_20s_max"]:
            dropped.append(dict(e, reason="first 20 s budget")); continue
        win = [k for k in kept if abs(k["at"] - e["at"]) < 30 and k["at"] >= 20]
        if e["at"] >= 20 and len(win) >= D["per_min_body_max"] and PRIORITY.get(kind, 0) < 5:
            dropped.append(dict(e, reason="per-minute budget")); continue
        rl = [r for r, _ in roles]
        if "tick" in rl and sum(1 for k in kept if "tick" in k["roles"] and abs(k["at"] - e["at"]) < 5) >= D["ticks_per_10s"]:
            dropped.append(dict(e, reason="tick budget")); continue
        if "riser" in rl and sum(1 for k in kept if "riser" in k["roles"]) >= D["risers_max"]:
            dropped.append(dict(e, reason="riser budget")); continue
        if "reverse" in rl and sum(1 for k in kept if "reverse" in k["roles"]) >= D["reverse_max"]:
            dropped.append(dict(e, reason="reverse budget")); continue
        kept.append(dict(e, kind=kind, roles=rl, levels=[lv for _, lv in roles]))
    return sorted(kept, key=lambda e: e["at"]), dropped


def sfx_stem(n: int, kept: list[dict], words: list[dict], voice_lufs: float, lib: "Library", rules: dict | None = None) -> tuple[np.ndarray, list]:
    """Place each sound so its own hit point lands on the event's frame, at its level relative to the voice."""
    R = dict(SOUND_RULES["sfx"], **(rules or {}))
    out = np.zeros((n, 2), np.float32)
    log = []
    for e in kept:
        for role, lv in zip(e["roles"], e["levels"]):
            y, meta, src = lib.pick(role)
            al = R["align"].get(role, "onset")
            hit = meta["peak"] if al == "peak" else meta["end"] if al == "end" else meta["onset"]
            level = lv + float(e.get("gain_db", 0))
            if any(w["t"] - 0.05 <= e["at"] <= w["e"] + 0.05 for w in words) and role not in ("riser", "reverse"):
                level += R["under_word_db"]
            gain = undb(level + voice_lufs - meta["max_m"])
            if al == "end":
                y = y[: int(hit * SR)]
            start = int(round((e["at"] - hit) * SR))
            a, b = max(0, start), min(n, start + len(y))
            if b > a:
                out[a:b] += y[a - start:b - start] * gain
            log.append({"at": round(e["at"], 3), "event": e["kind"], "role": role, "file": src, "level_lu": round(level, 1), "why": e.get("why", "")})
    return out, log


# ---------------------------------------------------------------- the director


def direct(out: Path, voice_raw: Path, words: list[dict], total: float, speech_end: float, music: Path | None,
           events: list[dict], drops=(), land: float | None = None, fmt_rules: dict | None = None, log=print,
           sections: list[dict] | None = None, sfx_dir: Path | None = None) -> dict:
    """Build the voice, music and effects stems on the output clock and the mix. sections: [{name, a, b, vm, p10}] in
    output seconds (default: one section at the music's vm_target). Writes voice.wav, music.wav, sfx.wav, mix.wav and
    sound.json (every decision with its reason)."""
    fr = fmt_rules or {}
    n = int((total + 0.05) * SR)
    v = read_audio(voice_raw)
    v = np.pad(v, (0, max(0, n - len(v))))[:n]
    vm, vrep = voice_master(v, [w for w in words if w["t"] < speech_end + 0.1], fr.get("voice"), log)
    vl = lufs(vm)
    rep = {"voice": vrep}
    stems = [np.stack([vm, vm], 1)]
    mrules = dict(SOUND_RULES["music"], **(fr.get("music") or {}))
    secs = sections or [{"name": "all", "a": 0.0, "b": total, "vm": mrules["vm_target_lu"], "p10": mrules["vm_p10_min_lu"]}]
    ms = None
    if music:
        prof = track_profile(Path(music))
        bed, fit = fit_music(Path(music), prof, total, land, fr.get("music"))
        bed = bed[:n] if len(bed) >= n else np.pad(bed, ((0, n - len(bed)), (0, 0)))
        bars_out = np.array(fit["bars_after_start"])
        g, used = music_automation(n, words, total, speech_end, drops, fr.get("music"), bars_out, secs)
        for a, b in used:   # the bed comes back on a downbeat: mark it the way the dialect does
            events = list(events) + [{"kind": "drop_return", "at": b, "why": "bed returns after a drop"}]
        ms, mrep = music_stem(bed, vm, words, g, secs, fr.get("music"))
        stems.append(ms)
        write_audio(out / "music.wav", ms)
        rep["music"] = {"file": str(music), "fit": {k: fit[k] for k in ("start", "how", "tempo")},
                        "profile": {k: prof[k] for k in ("tempo", "mode", "voice_band", "build_db", "centroid_hz", "dur")},
                        "drops": [list(d) for d in used], **mrep}
    lib = Library(sfx_dir)
    kept, dropped = plan_sfx(events, words, fr.get("sfx"), total)
    sx, placed = sfx_stem(n, kept, words, vl, lib, fr.get("sfx"))
    stems.append(sx)
    write_audio(out / "sfx.wav", sx)
    write_audio(out / "voice.wav", vm)
    rep["sfx"] = {"dialect": dict(SOUND_RULES["sfx"], **(fr.get("sfx") or {}))["dialect"], "placed": placed, "dropped": dropped,
                  "per_min": round(len(kept) / max(total / 60, 0.1), 1), "library": {k: len(v) for k, v in lib.items.items()}}
    mix = sum(stems)
    mix = limiter(mix, -1.5)
    write_audio(out / "mix.wav", mix)
    rep["qc"] = qc(vm, ms, mix, words, speech_end)
    json.dump(rep, open(out / "sound.json", "w"), indent=1, default=float)
    secs_txt = "; ".join(f"{r['name']} {r['vm_median']}/{r['target_vm']} LU" for r in rep.get("music", {}).get("sections", []))
    log(f"sound: voice {vrep['stem_lufs']} LUFS, breaths {vrep['breaths_lowered']}, wind frames {vrep.get('wind_burst_frames')}; "
        f"music {rep.get('music', {}).get('fit', {}).get('how', 'none')}; voice over music {secs_txt}; "
        f"sfx {len(placed)} placed, {len(dropped)} left dry")
    return rep


def qc(voice: np.ndarray, music: np.ndarray | None, mix: np.ndarray, words: list[dict], speech_end: float) -> dict:
    """Numbers a mix engineer checks: the voice's lead over the music while words play, loudness, peaks, clicks."""
    R = SOUND_RULES["master"]
    out = {"mix_lufs": round(lufs(mix), 1), "mix_true_peak_db": round(true_peak_db(mix), 1)}
    ts_, st_ = loudness_curve(mix, win_s=3.0, hop_s=0.5)
    out["short_term_max_over_integrated_lu"] = round(float(st_.max() - out["mix_lufs"]), 1)
    tv, lv = loudness_curve(voice)
    if music is not None:
        tm, lm = loudness_curve(music)
        speak = np.array([any(w["t"] <= t <= w["e"] for w in words) for t in tv])
        d = (lv - lm)[speak & (lv > -50)]
        if len(d):
            out["voice_over_music_median_db"] = round(float(np.median(d)), 1)
            out["voice_over_music_p5_db"] = round(float(np.percentile(d, 5)), 1)
            out["music_ok"] = bool(out["voice_over_music_median_db"] >= 9.0 and out["voice_over_music_p5_db"] >= 3.0)
    d2 = np.abs(np.diff(voice, 2))
    loc = np.sqrt(np.convolve(d2 ** 2, np.ones(240) / 240, "same")) + 1e-6
    out["click_suspects"] = int(((d2 > 12 * loc) & (d2 > 0.05)).sum())
    out["clipped_samples"] = int((np.abs(mix) >= 0.999).sum())
    return out


def assemble_voice(src: Path, segs: list[dict], total: float, dst: Path, fps: int = 30, xfade_s: float = 0.010) -> Path:
    """The raw voice on the output clock, cut from the selects' voice track at the same frames as the picture.
    Every join is a 10 ms equal-power crossfade centred on the cut (each side reaches 5 ms past it), so nothing
    clicks and nothing drifts: a run keeps its exact start on the output clock."""
    y = read_audio(src)
    n = int((total + 0.05) * SR)
    out = np.zeros(n, np.float32)
    runs, cur = [], []
    for k, sg in enumerate(segs):
        if sg.get("cont") and cur:
            cur.append(k)
        else:
            if cur:
                runs.append(cur)
            cur = [k]
    if cur:
        runs.append(cur)
    h = int(xfade_s * SR / 2)
    ramp = np.sin(np.linspace(0, np.pi / 2, 2 * h)) if h else np.ones(0)
    for j, r in enumerate(runs):
        sg = segs[r[0]]
        d = sum(segs[i]["frames"] for i in r) / fps
        a = int(round(sg["in"] * SR)) - h
        b = int(round((sg["in"] + d) * SR)) + h
        x = y[max(0, a):max(0, b)].astype(np.float32).copy()
        if a < 0:
            x = np.concatenate([np.zeros(-a, np.float32), x])
        if len(x) < b - a:
            x = np.pad(x, (0, b - a - len(x)))
        if h:
            if j > 0:
                x[:2 * h] *= ramp
            else:
                x[:h] = 0
                x[h:2 * h] *= np.sin(np.linspace(0, np.pi / 2, h))
            if j < len(runs) - 1:
                x[-2 * h:] *= ramp[::-1]
            else:
                tail = int(0.25 * SR)
                x[-tail:] *= np.cos(np.linspace(0, np.pi / 2, tail)) ** 2
        o = int(round(sg["out_t"] * SR)) - h
        lo, hi = max(0, o), min(n, o + len(x))
        if hi > lo:
            out[lo:hi] += x[lo - o:hi - o]
    write_audio(dst, out)
    return dst
