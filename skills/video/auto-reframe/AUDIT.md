# AUDIT: auto-reframe

| Claim | Status | Source |
|---|---|---|
| YuNet detector, every second frame, damped camera with dead zone, snap at cuts, crop expressions | RUN | `tools/studio/track.py`; detect + render of a 20 s 4K window: 11 s to track, 12 s to render, on 2026-10-31 |
| 27 % face height target, 50 % coverage threshold | RUN | `track.camera` (want = 0.27) and `render.reel` fallback (coverage < 0.5) |
| the face stays near the upper third | RUN | `face_y = 0.40` in `track.camera`; contact sheets of the test render |
| YuNet licence Apache-2.0, from opencv/opencv_zoo | VERIFIED | opencv_zoo model card, file sha256 8f2383e4...2fa4 downloaded 2026-10-31 |
