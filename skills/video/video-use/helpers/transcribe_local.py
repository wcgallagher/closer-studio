"""Key-free stand-in for transcribe.py (local faster-whisper instead of ElevenLabs Scribe).

Writes <edit_dir>/transcripts/<video_stem>.json in Scribe's shape (words with type
word/spacing, start/end, speaker_id) so pack_transcripts.py and render.py work unchanged.

Usage:
    python helpers/transcribe_local.py <video> [<video> ...] [--edit-dir DIR] [--model medium.en] [--prompt "names"]
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

FILLERS = "Umm, uh, so, like, you know, I mean. Um, let me, let me say that again."


def load_audio(video: Path) -> np.ndarray:
    # Decode with ffmpeg; faster-whisper's own decoder breaks on newer PyAV releases.
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768


def transcribe(model: WhisperModel, video: Path, edit_dir: Path, prompt: str) -> None:
    out = edit_dir / "transcripts" / f"{video.stem}.json"
    if out.exists():
        print(f"cached: {out}")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    segs, info = model.transcribe(load_audio(video), language="en", word_timestamps=True,
                                  initial_prompt=f"{FILLERS} {prompt}".strip(),
                                  condition_on_previous_text=False)
    words, prev = [], 0.0
    for seg in segs:
        for w in seg.words or []:
            if w.start > prev:
                words.append({"text": " ", "start": prev, "end": w.start, "type": "spacing", "speaker_id": "speaker_0"})
            words.append({"text": w.word.strip(), "start": w.start, "end": w.end, "type": "word",
                          "speaker_id": "speaker_0", "logprob": w.probability})
            prev = w.end
    text = " ".join(w["text"] for w in words if w["type"] == "word")
    out.write_text(json.dumps({"language_code": "en", "text": text, "words": words}, indent=1))
    print(f"wrote {out} ({sum(w['type'] == 'word' for w in words)} words, {info.duration:.1f}s)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+", type=Path)
    ap.add_argument("--edit-dir", type=Path)
    ap.add_argument("--model", default="medium.en")
    ap.add_argument("--prompt", default="", help="names and keywords Whisper should spell right")
    a = ap.parse_args()
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    for v in a.videos:
        transcribe(model, v, a.edit_dir or v.parent / "edit", a.prompt)


if __name__ == "__main__":
    main()
