# AUDIT: caption-styles

| Claim | Status | Source |
|---|---|---|
| four styles, mechanisms, sizes 4.8 %, 4.4 %, 4.0 %, 4.4 % of frame height | RUN | `STYLES` in `tools/studio/captions.py` |
| clearance pass: camera steps 0.40 to 0.28, 24 px margins, top-zone fallback | RUN | `place` and `clearance` in `tools/studio/render.py`; `tools/studio/review.py` re-check |
| band from 50 % of height to 40 px above the bottom safe zone; 30 % hook position; 2.6 s hook | RUN | `tools/studio/platforms.py` `caption_band`; `tools/studio/cards.py` `hook_event`; `tools/studio/render.py` |
| one emphasis mechanism, 1 to 6 words, captions in the 48 to 66 % band, never over a face | VERIFIED | writepanda.ai retention study and Hormozi caption measurement (July 2026), rows in `RESEARCH.md` |
| Hormozi 2021 look (caps, yellow active word) and 2024+ look (mixed case, weight) | VERIFIED | choppity.com style page; writepanda.ai Hormozi measurement; TomsProject masterclass transcript, rows in `RESEARCH.md` |
| Gadzhi serif "special word" | VERIFIED | Gadzhi masterclass transcript (two fonts: a sans and a special serif), row in `RESEARCH.md` |
| `premium` style (Inter bold, the speaker's case, soft shadow, 3 to 7 words, gold on at most one meaning word per line and 15 % of words, first line from frame 0, size 3.6 % x 1.85 on 16:9); layers `captions.style` | RUN | `tools/studio/captions.py` (`STYLES["premium"]`, `_keywords`, the keyword branch of `events`), `tools/studio/longform.py` (layers `captions.style`); the 15 % cap and the case rule are rulebook TY-07; reviews in `docs/panels/2026-11-02_vsl_full_reset_vs_previous.md` |
| Line-break rules: `BIND_NEXT` ends cost 5, `COLLOC` splits cost 5, a line under the minimum costs 2.5, beat changes are sentence ends, short clauses join the sentence they belong to | RUN | `tools/studio/captions.py` `chunk`; rulebook CP-03 (Netflix line-break rules); checked on the SMA v8 and v9 word maps on 2026-11-02: no line ends on a binding word, the devil's advocate's 12 bad v8 breaks (for example "DON'T / WANT", "RIGHT / NOW") are gone |
| premium is about 72 px at 1080 on 16:9 | RUN | computed: 0.036 x 1.85 x 1080 = 71.9 px (`tools/studio/captions.py` `header`, the 1.85 factor for frames wider than tall) |
