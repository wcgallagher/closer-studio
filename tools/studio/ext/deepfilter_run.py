"""Run DeepFilterNet 3 (Rikorose/DeepFilterNet, MIT or Apache-2.0) on a mono 48 kHz WAV, in its own Python environment.

DeepFilterNet 0.5.6 imports torchaudio.backend, which newer torchaudio removed; a stub module keeps its loader importable
(audio is read and written here with soundfile, so the stub is never used).
usage: python deepfilter_run.py IN.wav OUT.wav [ATTEN_LIMIT_DB]
"""
import sys
import types

stub = types.ModuleType("torchaudio.backend.common")


class AudioMetaData:  # noqa: D401 - placeholder type for an import that is never used here
    pass


stub.AudioMetaData = AudioMetaData
sys.modules.setdefault("torchaudio.backend", types.ModuleType("torchaudio.backend"))
sys.modules["torchaudio.backend.common"] = stub

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import torch  # noqa: E402
from df.enhance import enhance, init_df  # noqa: E402

src, dst = sys.argv[1], sys.argv[2]
lim = float(sys.argv[3]) if len(sys.argv) > 3 else None
model, state, _ = init_df(log_level="ERROR")
y, sr = sf.read(src, dtype="float32", always_2d=True)
y = y.mean(1)
if sr != state.sr():
    raise SystemExit(f"expected {state.sr()} Hz, got {sr}")
out = enhance(model, state, torch.from_numpy(y)[None], atten_lim_db=lim)
sf.write(dst, out.squeeze(0).numpy().astype(np.float32), sr, subtype="PCM_16")
print("ok", dst)
