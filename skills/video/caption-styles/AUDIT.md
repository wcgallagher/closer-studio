# AUDIT: caption-styles

| Claim | Status | Source |
|---|---|---|
| four styles, mechanisms, sizes 4.8 %, 4.4 %, 4.0 %, 4.4 % of frame height | RUN | `STYLES` in `tools/studio/captions.py` |
| clearance pass: camera steps 0.40 to 0.28, 24 px margins, top-zone fallback | RUN | `place` and `clearance` in `tools/studio/render.py`; `tools/studio/review.py` re-check |
| band from 50 % of height to 40 px above the bottom safe zone; 30 % hook position; 2.6 s hook | RUN | `tools/studio/platforms.py` `caption_band`; `tools/studio/cards.py` `hook_event`; `tools/studio/render.py` |
| one emphasis mechanism, 1 to 6 words, captions in the 48 to 66 % band, never over a face | VERIFIED | writepanda.ai retention study and Hormozi caption measurement (July 2026), rows in `RESEARCH.md` |
| Hormozi 2021 look (caps, yellow active word) and 2024+ look (mixed case, weight) | VERIFIED | choppity.com style page; writepanda.ai Hormozi measurement; TomsProject masterclass transcript, rows in `RESEARCH.md` |
| Gadzhi serif "special word" | VERIFIED | Gadzhi masterclass transcript (two fonts: a sans and a special serif), row in `RESEARCH.md` |
