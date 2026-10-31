"""Analysis pass: words with timestamps, silences, fillers, emphasis, sentences, faces, cuts, candidate moments.

Everything downstream (cut, captions, reframe, review) reads analysis.json; nothing re-transcribes.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

import numpy as np

from .common import FILLERS, FUNC, norm, probe, save_json

SR = 16000
HOP = 320  # 20 ms

HOOK_OPENERS = ("you", "your", "if", "stop", "why", "most", "never", "every", "here", "the reason", "nobody", "the biggest",
                "there are", "there is", "i", "when", "this is", "what", "how", "people", "closers", "agents", "sales")


def _audio(video: Path, start: float, dur: float) -> np.ndarray:
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(video), "-vn", "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768


def transcribe(a: np.ndarray, model_name: str, prompt: str | None = None, language: str | None = "en") -> list[dict]:
    from faster_whisper import WhisperModel
    m = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5, language=language, condition_on_previous_text=False,
                           initial_prompt=prompt or "Umm, uh, so, like, you know. Closer, objection, commission, 401(k), IRA, annuity, rollover.")
    words = []
    for s in segs:
        for w in s.words or []:
            t = w.word.strip()
            if not t:
                continue
            if words and (t.startswith(("-", ".")) or words[-1]["w"].endswith("-")) and len(t) > 1 and not t[1:2].isspace():
                # Whisper splits hyphenated words ("cross", "-selling", "50", "-50"): keep them as one word
                words[-1]["w"] = words[-1]["w"] + t
                words[-1]["e"] = round(float(w.end), 3)
                words[-1]["p"] = round(min(words[-1]["p"], float(w.probability)), 2)
                continue
            words.append({"w": t, "s": round(float(w.start), 3), "e": round(float(w.end), 3), "p": round(float(w.probability), 2)})
    return words


def silences(a: np.ndarray) -> list[tuple[float, float]]:
    """(start, end) of every quiet stretch >= 150 ms, 25 dB under the speech level."""
    rms = np.array([np.sqrt(np.mean(a[i:i + HOP] ** 2)) + 1e-9 for i in range(0, len(a) - HOP, HOP)])
    db = 20 * np.log10(rms)
    thr = np.percentile(db, 80) - 25
    out, run = [], None
    for i, v in enumerate(db):
        if v < thr and run is None:
            run = i
        if v >= thr and run is not None:
            if (i - run) * HOP / SR >= 0.15:
                out.append((round(run * HOP / SR, 3), round(i * HOP / SR, 3)))
            run = None
    if run is not None and (len(db) - run) * HOP / SR >= 0.15:
        out.append((round(run * HOP / SR, 3), round(len(a) / SR, 3)))
    return out


def mark_words(words: list[dict], a: np.ndarray):
    """Adds filler, emphasis (loudness z-score) and function-word flags in place."""
    lv = []
    for w in words:
        i0, i1 = int(w["s"] * SR), max(int(w["s"] * SR) + HOP, int(w["e"] * SR))
        seg = a[i0:i1]
        lv.append(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) if len(seg) else -80.0)
    lv = np.array(lv)
    content = np.array([norm(w["w"]) not in FUNC and len(norm(w["w"])) >= 3 for w in words])
    base = lv[content] if content.any() else lv
    mu, sd = float(np.mean(base)), float(np.std(base) + 1e-6)
    for w, v, c in zip(words, lv, content):
        n = norm(w["w"])
        w["db"] = round(float(v), 1)
        w["filler"] = n in FILLERS
        w["func"] = n in FUNC
        w["emph"] = bool(c and (v - mu) / sd > 1.0 and (w["e"] - w["s"]) >= 0.18)


def sentences(words: list[dict]) -> list[dict]:
    out, i0 = [], 0
    for i, w in enumerate(words):
        if w["w"][-1:] in ".?!" or i == len(words) - 1:
            out.append({"i0": i0, "i1": i, "s": words[i0]["s"], "e": words[i]["e"],
                        "text": " ".join(x["w"] for x in words[i0:i + 1])})
            i0 = i + 1
    return out


def moments(words: list[dict], sents: list[dict], lo: float = 18.0, hi: float = 45.0) -> list[dict]:
    """Candidate reel windows: start on a sentence that stands alone, end on a sentence end, 18 to 45 s, ranked."""
    cands = []
    for si, s in enumerate(sents):
        first = norm(words[s["i0"]]["w"])
        text_l = s["text"].lower()
        hook = 0.0
        if text_l.startswith(HOOK_OPENERS) or first in ("you", "your", "if", "stop", "why", "most", "never", "every"):
            hook += 2.0
        if "?" in s["text"][:80]:
            hook += 1.0
        if any(k in text_l for k in ("mistake", "secret", "nobody", "reason", "truth", "stop", "never", "biggest", "problem", "money")):
            hook += 1.0
        if first in ("and", "but", "so", "because", "which", "that"):
            hook -= 2.0
        for sj in range(si, len(sents)):
            dur = sents[sj]["e"] - s["s"]
            if dur < lo:
                continue
            if dur > hi:
                break
            ws = words[s["i0"]:sents[sj]["i1"] + 1]
            density = len([w for w in ws if not w["func"]]) / max(dur, 1)
            emph = sum(1 for w in ws if w.get("emph"))
            fill = sum(1 for w in ws if w.get("filler"))
            ends_strong = any(k in sents[sj]["text"].lower() for k in ("that's", "so ", "which means", "because", "money", "close", "deal"))
            score = hook + density * 0.8 + emph * 0.25 - fill * 0.3 + (0.5 if ends_strong else 0) + (0.5 if 22 <= dur <= 38 else 0)
            cands.append({"s": round(s["s"], 2), "e": round(sents[sj]["e"], 2), "dur": round(dur, 1), "score": round(score, 2),
                          "hook_line": s["text"][:120], "last_line": sents[sj]["text"][-120:]})
    cands.sort(key=lambda c: -c["score"])
    picked = []
    for c in cands:
        if all(abs(c["s"] - p["s"]) > 8 for p in picked):
            picked.append(c)
        if len(picked) >= 8:
            break
    return picked


def analyze(video: Path, out: Path, start: float = 0.0, end: float | None = None, model: str = "small.en",
            faces: bool = True, stride: int = 2, log=print) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "analysis.json"
    info = probe(video)
    end = end if end is not None else info["dur"]
    key = {"video": str(video), "mtime": os.path.getmtime(video), "start": start, "end": end, "model": model, "faces": faces, "stride": stride}
    if cache.exists():
        d = json.loads(cache.read_text())
        if d.get("key") == key:
            return d
    t0 = time.time()
    dur = end - start
    a = _audio(video, start, dur)
    log(f"transcribing {dur:.0f} s with {model} ...")
    words = transcribe(a, model)
    sil = silences(a)
    mark_words(words, a)
    sents = sentences(words)
    d = {"key": key, "video": str(video), "start": start, "end": end, "dur": dur, "w": info["w"], "h": info["h"], "src_fps": info["fps"],
         "words": words, "silences": sil, "sentences": sents, "moments": moments(words, sents),
         "stats": {"words": len(words), "fillers": sum(w["filler"] for w in words), "emphasis": sum(w["emph"] for w in words),
                   "speech_s": round(sum(w["e"] - w["s"] for w in words), 1)}}
    if faces:
        from . import track
        log("tracking the face ...")
        tr = track.detect(video, start, dur, stride=stride, log=log)
        d["track"] = {k: tr[k] for k in ("fps", "w", "h", "stride", "dets", "cuts", "coverage")}
    d["elapsed_s"] = round(time.time() - t0, 1)
    save_json(cache, d)
    (out / "transcript.txt").write_text("\n".join(f"[{s['s']:7.2f}] {s['text']}" for s in sents) + "\n")
    return d
