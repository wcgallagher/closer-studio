# Credits and licenses

| Folder | Source | License |
|---|---|---|
| `skills/video/video-use` | [browser-use/video-use](https://github.com/browser-use/video-use) | MIT (`LICENSE` in the folder). We added `helpers/transcribe_local.py` so it runs without an ElevenLabs key. |
| `skills/video/vsl-editor` | Ours, adapted from the video-use method | Ours |
| `skills/copy/longform-copywriter` | [brandonuttley/direct-response-copywriting-skill](https://github.com/brandonuttley/direct-response-copywriting-skill) | MIT (`LICENSE` in the folder) |
| `skills/copy/trust-scorecard` | Ours, built on [heyJonBray/psyop-scorecard](https://github.com/heyJonBray/psyop-scorecard) (Chase Hughes / NCI rubric); the CLI is in `upstream/` | MIT (`upstream/LICENSE`). The rubric PDF from that repo is not included. |
| `skills/copy/human-tradecraft` | Ours, from Chase Hughes / NCI behavior concepts | Ours |
| `skills/media-buying/*` (49 skills) | [irinabuht12-oss/marketing-skills](https://github.com/irinabuht12-oss/marketing-skills) | MIT, per the upstream README ("all 49, MIT licensed"). The upstream repo ships no LICENSE file; its README is kept as `skills/media-buying/UPSTREAM_README.md`. |

## Referenced, not included

- [tenfoldmarc/video-edit-skill](https://github.com/tenfoldmarc/video-edit-skill): 9:16 Instagram reel editor (behind-head words, three looks, safe zones). It has no license, so its files can't be copied here. Install it straight from its repo when making reels.

## Engine components (added 2026-10-31)

| Component | Licence | Where |
|---|---|---|
| YuNet face detector `face_detection_yunet_2023mar.onnx` (opencv/opencv_zoo) | Apache-2.0 | `tools/studio/models/` |
| OpenCV (`opencv-python-headless`) | Apache-2.0 | installed by `install.sh` |
| faster-whisper (SYSTRAN) and the Whisper models (OpenAI) | MIT | installed by `install.sh` |
| PySceneDetect | BSD-3 | installed by `install.sh` (the inline cut detector follows its ContentDetector method) |
| DeepFilterNet standalone binary (Rikorose/DeepFilterNet v0.5.6) | MIT / Apache-2.0 | optional, `install.sh --deep-filter` |
| Fraunces Display (Undercase Type) | SIL OFL 1.1 | `fonts/` (instanced at optical size 144, family renamed) |
| Inter (Rasmus Andersson) | SIL OFL 1.1 | `fonts/Inter-Bold.ttf`, `fonts/Inter-Medium.ttf` (instanced at weights 700 and 500 from the variable font, for the VSL lockup labels) |
| JetBrains Mono (JetBrains) | SIL OFL 1.1 | `fonts/JetBrainsMono-SemiBold.ttf` (eyebrows and tags) |
| Technique sources (repos, measurements, masterclass transcripts) | see `RESEARCH.md` | |
