# Editor rulebook

The public rulebook behind `skills/video/editor-brain/SKILL.md`: what a human editor does to a talking-head video, written as rules with numbers, each with where the number came from. It covers four kinds of work: 9:16 reels, YouTube long-form, sales VSLs and brand films. Version 1, 2026-11-02, a synthesis of six research angles (aesthetics and finish, voice timing, audio layers, AI-slop tells, prompt-to-edit tools, comparing two cuts) plus cross-platform shipping.

How to read it:

- Every number carries its provenance and source keys. **sourced**: quoted from the source. **sourced-low**: from a low-confidence or unverified source. **computed**: worked out from a sourced formula or frame geometry. **measured**: our own measurement (local ffmpeg 6.1.1 or transcript analysis, 2026-11-02). **house**: our own choice, with what informed it when anything did. Source keys resolve in the last section.
- Severity: **BLOCK** refuses delivery until fixed; **FIX** is repaired automatically and reported; **WARN** is reported only.
- Frames assume 30 fps unless stated (convert with round(ms x fps / 1000)). Pixels are for 1080x1920 (9:16) or 1920x1080 (16:9); scale linearly.
- Checks run on the delivered encoded file, except plan-lint checks, which read plan.json or scene code.
- **engine** lines say what the kit's code does today. Where the code and a rule disagree, the code is what runs; the gap is listed as an open item, and changing it is a decision for the owner.
- Every rule here has a public source or is marked as a house choice. Rules with no public support are not in this copy.

## 1. Profiles and defaults

- **reel**: 9:16 social, 15-90 s, Hormozi-level energy
- **yt**: YouTube long-form talking head, 16:9
- **vsl**: Sales VSL, 2-20 min, 16:9 or 9:16. Prospects are about 55-72 and are weighing a retirement-money decision, so trust comes first.
- **brand**: Premium brand film, or Gadzhi-style long-form led by music

| Default | reel | yt | vsl | brand | Provenance | Sources | Engine (what runs) |
|---|---|---|---|---|---|---|---|
| effective wpm | 200-235 | 175-215 | 165-200 | 175-215 | house | KIM19 (persuasion peaks near 181 wpm); GUYER24; M_HORMOZI (226 edited); M_HORMOZI_POD (216 natural); M_MRBEAST (189 inside speech runs); M_GADZHI (178-218 blocks) |  |
| clause gap ms | 80-150 | 120-250 | 150-300 | 150-300 | house | LIU22; OWNER_FM (comma gaps median 140-200); AUTOEDITOR |  |
| sentence gap ms | 170-300 | 250-450 | 400-600 | 350-600 | house | LIU22 (0.6-1.2 s most natural, 0.075-0.15 s worst); VIZARD_PAUSE (a 0.2 s cap sounds breathless); R_EDITORS (5-10 frames of air); OWNER_FM (median 420-480) | breath 300 / 400 / 450 ms (edit.py DEFAULTS) |
| emphasis beat ms | 350-500, at most 1 per 10 s | 600-800 | 700-1200 before a price, claim or CTA, at most 2 per min | section rests of 3-13 s at scripted turns only | house | LIU22; YAMASHITA via LIU22 (top speeches 0.83-1.24 s between sentences); M_GADZHI (7-13 s breathers) | layers breath.after holds (cut.py) |
| first 60s max pause ms | 300 | 400 | not applied (DA-2) | not applied | house | MRBEAST_GUIDE |  |
| filler removal pct | 85-100 | 70-85 | 90-100 (scripted) | 70-85 | house (yt and brand values sourced) | R_EDITORS (about 75%); R_PODCAST (3 of 4; little gain past 70-80%) | formats.json fillers cut (every flagged filler) for these formats |
| breaths | none inside sentences; between sentences remove only where room tone fills the gap, otherwise -10 dB | none inside sentences; -6 to -10 dB between | same as yt | same as yt | sourced | SSE_BREATH; GRAVY; IZO_BREATH | 6 dB down (sound.py) |
| median shot s | 1-3 | 3-7 | 4-8 | 3-8 | sourced except vsl (house) | CHOPPITY_AH; SUBSCRIBR; ONEOF10; CHOPPITY_LH | punch every 2.6 s in vsl_hero (formats.json); 4.5 s when a format sets none (longform.py) |
| max static framing s | 10 | 12 | 15 (a 1.00-1.04 slow push counts as motion) | 15 | house | SUBSCRIBR; AI-13 proposal | review fails over 8 s, every format |
| jumpcut punch scale | 1.10-1.20 | 1.10-1.15 | 1.10-1.12 | 1.10-1.12 or a B-cam angle | sourced range; vsl and brand caps are house | ONEOF10 (110-120%); CHOPPITY_AH (10-20%); KIT_RULES (112%) | vsl_hero 1.00 / 1.12 / 1.00 / 1.22; default 1.00 / 1.15 |
| graphic moments per min body | not set here: the reel clock is a visible change every 3 to 8 s (KIT_EG) | 2-4 | 2-4, only on numbers, proof and CTA | 1.5-3 | yt and vsl house; brand sourced | SOZAI_GADZHI; KIT_EG |  |
| intro density multiplier | 1x (already dense) | 2-3x for the first 30-60 s | 1.5-2x for the first 60 s | 2-5x (4-10 visuals per min) | brand sourced; others house | SOZAI_GADZHI |  |
| sfx per min | up to 10 in the body, up to 4 in the first 5 s | 4-6 | up to 4, soft UI and hits only | 4-6 | yt and brand sourced-low; reel and vsl house | YTSFX (business 4-6 per min); YTSFX_CREATORS | gadzhi 8 in the first 20 s then 4 per 60 s; review gate 12 per min |
| music gap lu under voice | 20, or no music | 20-24 | off by default; 22-26 if used | 15-20 | house | WCAG147 (at least 20 dB); OVERSEER (finance 20-26, storytelling 15-20); CHOPPITY_AH (subtle music) | edit.py DEFAULTS win (AU-04): vsl_hero 11 / 14 / 12, paid ad 12, organic reel 16, yt_authority and skool_lesson 20 |
| caption mode | 1 to 6 words, one emphasis mechanism, UPPER allowed (KIT_EG) | phrases of 3-5 words in sentence case, or none | phrases of 4-7 words, up to 42 chars, 1-2 lines, sentence case (DA-3) | none, or sentence-case keywords only | reel measured; yt sourced; vsl and brand house | KIT_EG; NFX_TTSG; CHOPPITY_LH (no burned captions) | vsl_hero renders `impact` by default (caps, 2-4 words, a colour accent; formats.json, captions.py); layers `"captions": {"style": "premium", "words": [3, 7]}` gives the vsl column: Inter bold in the speaker's case, a soft shadow, gold on at most one meaning word per line and 15 % of words, line breaks per CP-03 (captions.py `BIND_NEXT`, `COLLOC`) |
| caption font px | 64-96 on 9:16 | 44-56 on 16:9 | at least 64 on 9:16, at least 52 on 16:9 | 40-52 on 16:9 | house | HIG_TYPE (see TY-02) |  |
| entrance frames 30fps | 3-4 for pops, otherwise 6-9 | 6-10 | 8-12 | 9-12; slow title reveals up to 24 | bands sourced; profile split house | NNG; M3 |  |
| overshoot max pct | 10 | 4.6 | 1 | 1 | computed values; assignment house | APPLE_SPRING; BACK |  |
| grain noise alls 1080 | 0-3 | 3-5 | 0-3 (DA-4) | 3-5 | house | FFMPEG_local (measured std); CK_grain | finish.py grain amounts (TX-02) |
| vignette corner stops | -0.3 to -0.5 | -0.3 to -0.6 | -0.3 to -0.5 | -0.3 to -0.7 | house | FFMPEG_local; KIT_grade (the kit's own -0.36) | finish.py about -0.18 (vsl), -0.15 (reel), -0.25 (brand), on top of grade.py POST's -0.36 on every long-form piece, so about -0.54 in total for vsl (TX-06) |
| halation | off | off | off | optional; on only over hot skies or clipped highlights (engine) | house | KIT_CODE (finish.py) | off in vsl and reel profiles (finish.py) |
| black point lift pct | 0-3 | 2-6 | 2-6 | 5-10 | house | CHOPPITY_AH (crushed blacks); CHOPPITY_LH (lifted blacks) |  |
| letterbox | never | never | never | 2.39:1 on brand or b-roll segments only | house | FR-05 |  |
| loudness | -14 LUFS, TP <= -1 dBTP | same | same | same; OTT delivery -27 LKFS dialogue-gated, TP -2 | sourced | SPOTIFY; YT_SFN; NFX_MIX | platforms.py: -14 / -1.5 social and YouTube; web_vsl -15 / -1.2 |
| safe zone preset | universal_default | 16:9 | 16:9 or universal_default; meta_ads when run as an ad | 16:9 | house | safe_zones |  |

Dropped from this copy for lack of a public source: punch-and-shake hit accents and caption stroke as a share of the font size. The default transition rule went too; what stays is that speech is never dissolved (VO-10) and a VSL gets no shake or flash (DA-1).

## 2. Safe zones

| Preset | Box | Provenance | Sources |
|---|---|---|---|
| Instagram Reels, organic | about 220 px top, 430 px bottom, 130 px each side (platforms.py `organic`) | sourced-low | XYLA (xyla.ai social sizes sheet, orsonlord.com overlays, 2026, via platforms.py) |
| Instagram and Facebook Reels ads | top 14%, bottom 35%, 6% each side: x 65-1015, y 269-1248 | sourced | META_ADS (Meta Reels ad specs, via platforms.py); META_SAFE |
| TikTok | x 120-930, y 240-1440 (right column 150 px, bottom 480 px, top up to 240 px). Engine (platforms.py `tiktok`): organic top 160, bottom 420, left 60, right 120 px; ads top 240, bottom 660, 120 each side | sourced-low | TIKTOK_SAFE; REAP; KIT_CODE |
| universal default (9:16) | x 120-930, y 240-1440: the stricter edge of Instagram and TikTok on each side. Engine (placement.py `PLACEMENT_RULES["safe"]["9:16"]`): x 0.06-0.84, y 0.12-0.70 of the frame, x 65-907 and y 230-1344 at 1080x1920 | house | OPUS (avoid the bottom 25%); KIT_CODE |
| 16:9 | graphics safe x 96-1824, y 54-1026; action safe x 67-1853, y 38-1042 | computed | EBU_R95 |
| caption band (engine) | from 50% of the height to 40 px above the platform's bottom safe zone | sourced | KIT_CODE (platforms.py caption_band, citing a talking-head retention study that measured captions at 48-66% of the height) |

## 3. Aesthetics

### Grade

**GR-01** (BLOCK). Step 0 of every grade is to detect HDR and tone-map it to SDR BT.709. Never just retag HDR as bt709.

- detect: ffprobe color_transfer is arib-std-b67 or smpte2084, or Dolby Vision side data is present (sourced; HDR_DEVTO)
- chain: zscale linear npl=100 -> gbrpf32le -> zscale primaries bt709 -> tonemap hable desat=0 -> zscale transfer and matrix bt709, range tv -> yuv420p (sourced; HDR_DEVTO; FFMPEG_local)
- washout guard: face median luma within 10% of an SDR proxy; saturation drop no more than 20% (house)
- check: Output is tagged bt709 for primaries, transfer and matrix, range tv. When the input was HLG or PQ, the filter log must contain tonemap. This needs a zscale (libzimg) build; see XP-02.

**GR-02** (FIX). The default talking-head look is natural: a gentle S-curve, modest saturation and a faint split tone. Teal-orange is for b-roll or brand moments only and must still pass GR-04.

- contrast: 1.08-1.16 around a pivot of 0.42-0.45 (house; KIT_grade (tuned on the owner's takes))
- saturation: 1.00-1.10 (house; KIT_grade)
- split tone: highlights up to 0.03 RGB, shadows up to 0.02 (house; KIT_grade)
- face chroma drift: within +/-20% of the ungraded source (house)
- check: Per cut, compare face-skin mean chroma magnitude with the ungraded source.
- engine: Grade presets are generated .cube LUTs in tools/studio/grade.py (brand files pick one).

**GR-03** (FIX). The tone curve has a soft highlight shoulder, so skies and windows compress instead of clipping. Expose for the face.

- shoulder start: 0.80-0.86 display luma (house; KIT_grade)
- hable: A0.15 B0.50 C0.10 D0.20 E0.02 F0.30, white 11.2, exposure bias 2.0 (sourced; HABLE)
- clip fraction: no more than 0.5% of non-face pixels at Y>=235, and never more than the source (house)
- check: Histogram outside the face mask, graded vs source.

**GR-04** (WARN). Skin hue check. Report only, never auto-correct (DA-5).

- target: 123 deg as atan2(Cr-128, Cb-128) in BT.709 (ColorChecker dark skin 122.2, light skin 123.3) (computed; VSCOPE)
- warn: more than 8 deg from target (house)
- review: more than 15 deg (sourced-low; VSCOPE (pixls: skin spreads about +/-15 deg))
- axis trap: the classic 123 deg is an NTSC U/V figure and lands at 132-134 deg in Cb/Cr, so compute everything in one space (computed; VSCOPE)
- calibration: 3-5 frames the owner approves replace 123 as the target (house)
- check: Run the MediaPipe face-skin mask every 0.5 s and report the chroma-weighted mean angle per cut.

**GR-05** (WARN (a clipped face is FIX)). Skin exposure check. When correction is needed, use whole-plate curves only, never face-local edits.

- p95 face luma: (Y-16)/219: light skin 0.65-0.75, darker skin 0.50-0.60 (sourced-low; ZEBRA)
- clip: 0 face pixels at Y>=235 (house)
- check: 95th percentile of the face mask on sampled frames, plus a count of clipped face pixels.
- engine: tools/studio/finish.py lifts the face through a tracked soft window, at most 0.30 EV toward a luma of 0.52, never darker; a well-exposed face gets no lift. Open conflict with this rule's whole-frame-only wording; the owner decides.

**GR-07** (BLOCK). Never apply a log-input or print-film LUT to Rec.709 footage, and never ship third-party LUTs. Our generated .cube files are the only LUTs in the repo.

- registry: every LUT declares its input space (house; LUTS)
- check: The engine refuses a log-input LUT when the clip's transfer is bt709 or srgb.

### Finish and texture

**TX-01** (FIX). Finish in this order: grade, soften, halation if on, vignette on the footage plate, composite text and scenes, apply grain once over everything, encode.

- grain once: grain is applied exactly once, last, over all layers (sourced; CK_grain)
- soften before grain: blur comes before grain because grain is the sharpest element (sourced; CK_grain)
- vignette before text: the vignette goes on the plate so overlay contrast checks stay valid (house)
- check: plan-lint of filtergraph order.
- engine: finish.py grades the cut picture and adds grain before any graphics, so text and cards are never grained, while this rule puts grain last over everything. Open item.

**TX-02** (FIX). Grain is monochrome and temporal, felt rather than seen. Generate it at 2x and downscale, and keep it out of clipped highlights.

- strength: see profile_defaults; never above alls 6 on talking heads (house)
- std table: noise alls 3 = 1.36, 4 = 1.93, 6 = 3.06, 9 = 4.77 code values (1080p, grey 128) (measured; FFMPEG_local)
- clumps: 1-2 px at delivery (sourced; GIST_grain)
- mask: midtone-weighted, peaking near luma 75 (sourced; GIST_grain)
- check: On a flat mid-grey patch the added temporal luma std is 1.3-2.5 code values, and std is below 0.5 in pixels at 235 or above.
- engine: tools/studio/finish.py adds grain once, after the face and sky moves and before any graphics: amount 0 (vsl profile since BP-02), 0.006 (reel), 0.012 (brand), weighted 4L(1-L) so it peaks at mid grey, from half-resolution noise upscaled. 0.007 is about 1.8 code values at mid grey before the upscale (computed).

**TX-03** (WARN). The texture must survive encoding.

- master: libx264 crf 18 or lower; -tune grain when grain is on (sourced (-tune grain) / house (crf 18, the kit's master default); GIST_grain; KIT_CODE)
- retention: at least 60% of pre-encode grain std after decoding, tested through the real delivery path where possible (house; NETFLIX_FGS)
- social: 9:16 social: grain off or alls 3 or lower (house; NETFLIX_FGS)
- check: Encode a 5 s sample, decode it and re-measure.

**TX-04** (FIX). Soften, do not sharpen. Remove the kit's double unsharp pass.

- remove: unsharp 13x13 0.30 + 5x5 0.45 in grade.py POST: delete it or face-mask it (house; KIT_grade)
- cas: strength 0.3 or lower, outside faces only (house)
- check: Variance of Laplacian on the face, output against source, 0.85-1.10 (house).
- engine: The two unsharp passes are still in tools/studio/grade.py POST (unsharp 13x13 0.30 + 5x5 0.45). render.py piece_jobs applies POST to every long-form piece with no switch; the reel chain adds it when post is on. Open item.

**TX-05** (FIX). Halation only on real practical highlights, never as a glow on skin.

- skip: run the stage only when the sky covers over 3% of the frame or over 0.2% of pixels clip, which is what finish.py does in the brand profile (KIT_CODE)
- face: added red inside the face mask at most 1 code value (house)
- what: halation is a warm glow that blooms around hot highlights on film (sourced; DEHANCER)
- check: Face-mask red delta.
- engine: finish.py: threshold 0.88 luma, blur sigma 5 at half resolution, mix 0.03, tint (1.0, 0.58, 0.38). Off in the vsl and reel profiles; in brand only when the sky covers over 3% of the frame or over 0.2% clips.

**TX-06** (FIX). Vignette is gentle and centred on the face, not the frame.

- ffmpeg angle: 0.35 rad = -0.36 stops, 0.45 = -0.60, 0.50 = -0.74; avoid PI/5 = -1.21 and PI/4.6 = -1.46 (measured; FFMPEG_local)
- kit now: a=0.35 rad = -0.36 stops, keep it (measured; KIT_grade)
- centre: x0/y0 at the face centre (house)
- check: Flat 75% grey frame through the chain: corner/centre ratio 0.62-0.81 (-0.7 to -0.3 stops, computed).
- engine: finish.py centres its vignette on the frame, not the face: strength 0.12 (vsl), 0.10 (reel), 0.16 (brand), which is about -0.18, -0.15 and -0.25 stops at the corners (computed from the code's falloff). grade.py POST also carries ffmpeg vignette a=0.35 (-0.36 stops, measured) on every long-form piece, so the two stack to about -0.54 stops at the corners in the vsl profile, just past the profile band; the finish alone is gentler than the band.

**TX-08** (BLOCK). Delivery encode settings (engine house choice).

- master: libx264 crf 18 unless --crf is given; previews crf 26 veryfast (house; KIT_CODE longform.py)
- colour: the finish pass encodes yuv420p with BT.709 primaries, transfer and matrix, tv range (house; KIT_CODE finish.py)
- check: ffprobe -count_frames plus the colour tags.

### Framing

**FR-01** (WARN). Capture guidance for premium pieces: shoot from a distance with a longer lens, using a 180-degree shutter.

- distance: at least 1.5 m (5 ft). At 12 in the nose reads about 30% larger (sourced; SELFIE)
- lens: 2x (about 48 mm-eq) or longer (sourced (lens spec) / house (recommendation); IPHONE)
- shutter: 1/(2 x fps); 1/60 at 24 fps under 60 Hz lights (sourced; SHUTTER)
- check: Metadata: warn when the 35mm-eq focal length is under 40 mm. Flag when focal is 28 mm or less and face width exceeds 35% of W (house).

**FR-02** (WARN). A 9:16 crop from 16:9 needs a 4K source.

- min source height: 1920 px for a non-upscaled 1080x1920 crop; a 1080p source gives a 608x1080 crop, a 1.78x upscale (computed)
- check: Crop width in source pixels must be at least 1080, otherwise warn 'upscaled vertical'.

**FR-03** (FIX). Punch-ins have an upscale budget.

- cap: effective upscale = punch scale x (output height / source crop height), at most 1.12 (house; KIT_RULES)
- check: plan-lint for every scale key.
- engine: formats.json vsl_hero zooms are 1.00, 1.12, 1.00, 1.22; formats without zooms use 1.00 and 1.15 (longform.py). On a 2160-line source cut to 1080 the effective upscale of 1.22 is 0.61, inside the cap; on a 1080 source it is 1.22, past it.

**FR-04** (FIX). 9:16 face framing.

- subject height: 0.5-0.6 of H for premium, at least 0.6 for reel (sourced; CHOPPITY_LH; CHOPPITY_AH)
- chin: above the top of the caption block (house)
- eye y: eye line at 30-38% of H, subject centred horizontally (upper third, pushed down for the top UI band) (sourced; REALEYE; META_SAFE; VIMEO_FRAMING)
- check: Face landmarks every 0.5 s; no more than 10% of frames out of band (house).
- engine: Every punch-in shares one crop anchor (render.py KY = 0.33) so the eye line holds across cuts; the tracked camera aims the face at 0.42 of the height (longform.py). Every piece also gets a slow push from 1.02 to 1.045 (push 0.025).

**FR-05** (FIX). 16:9 graphics stay inside graphics-safe. Letterbox is for brand segments only, never 9:16.

- graphics safe: 5% margins: x 96-1824, y 54-1026 (computed; EBU_R95)
- letterbox: 2.39:1 = 1920x804 active, 138 px bars at 1080; 3840x1606, 277 px bars at 4K (computed)
- check: Every text and graphic alpha bbox is inside the box.
- engine: placement.py keeps text inside x 0.045-0.955 and y 0.06-0.94 of a 16:9 frame (x 86-1834, y 65-1015 at 1920x1080): slightly wider than the EBU box on x, slightly narrower on y.

**FR-06** (FIX). Reframing keeps what matters, not just the face.

- containment: hands, product or slides at least 90% inside the crop whenever the transcript refers to them (house; R_REFRAME)
- check: Person and hand detection per sampled frame against the crop window.

**FR-07** (FIX). Background blur on CPU: segment, refine the mask, blur by circle-of-confusion weight at low resolution, then light-wrap. Do not bundle RVM (GPL).

- mask input: 256x256 or 256x144 (sourced; MEDIAPIPE; MEET)
- blur res: 0.25-0.5x (house; MEET)
- light wrap: 1-3 px (house; MEET)
- halo: mean luma difference in a 6 px band outside the edge under 4 code values (house)
- stability: mask IoU between consecutive frames at least 0.95 (house)
- check: Halo test and temporal IoU.

**FR-08** (WARN). On same-subject cuts, the eye point should not jump unless the move is deliberate.

- face centre jump: at most 15% of W (house; MURCH; SMITH12)
- check: Face centroid on the frames either side of the cut.

### Type

**TY-01** (BLOCK). Fonts: at most 2 families, licensed OFL or Unlicense, never light weights, and loading verified before render.

- families: at most 2 (house)
- licence: OFL fonts only, such as TikTok Sans, Geist, Inter and Instrument Serif; the kit ships Inter, Fraunces Display and JetBrains Mono (listed in CREDITS.md) and Montserrat (not yet listed there), all SIL OFL 1.1 (sourced; FONTS; KIT_CREDITS; SENDSHORT_CAPS)
- weight: at least 500 over footage; captions 600-900 (house; HIG_TYPE (avoid light weights))
- load assert: every family and weight loads before render (document.fonts.check() in scenes; libass gets fontsdir); confirm the weight file exists (sourced; VIDEOUSE)
- check: Renderer throws on a fallback font; review crops each text style at native size.

**TY-02** (FIX). Text size floors on a phone. Re-chunk text rather than shrink it below a floor.

- ios equiv 9x16: about 47 px = iOS 17 pt body; 11 pt minimum = about 30 px (2.75 px per pt) (computed; HIG_TYPE)
- floor 16x9: 23 px minimum, 29 px default at 1080 (sourced; HIG_TYPE (tvOS))
- floor 9x16: no text below 32 px (about Apple's 11 pt Caption 2); chips and labels 48 px or more (about 17 pt Body); primary captions 64-110 px; one-word or number slams up to about 180 px, at 1080 wide (computed; HIG_TYPE (1 video px = 0.364 pt on a 393 pt wide phone))
- floor 16x9 phone: must-read text 54 px or more (5% of H); comfortable from 80 px (about 8% of H), for 16:9 watched inline on a phone (computed; HIG_TYPE; BBC 8% figure unverified)
- check: Font size from ASS and scene JSON; OCR bbox as backup.

**TY-03** (WARN). Track large sans display text tighter. Do not port SF Pro's table to other fonts.

- formula: tracking_em = -0.0223 + 0.185*exp(-0.1745*px): -0.0195 at 24 px, -0.022 at 48 px or more (sourced; INTER)
- check: Letter-spacing within +/-0.01 em of the formula.

**TY-04** (WARN). Line height and line count.

- titles: 0.9-1.05 (house)
- body: 1.3-1.5 (house)
- lines: at most 2, bottom-heavy (sourced; NFX_TTSG)
- check: ASS and scene styles; top line no longer than the bottom line.

**TY-05** (FIX). Every overlay meets WCAG contrast against the real pixels behind it. Fix failures with stroke, shadow or a dim plate, never by changing colour per frame.

- ratio: 4.5:1 normal text; 3:1 for large text (24 px or more, or 18.7 px or more bold); no rounding (sourced; WCAG143)
- background sample: 90th-percentile luminance inside the text box over 3 frames (house)
- check: Minimum ratio per text event.
- engine: placement.py gives plain text over a background brighter than 0.62 mean luma a cost, and the plate style for chips; the review does not yet measure WCAG ratios.

**TY-06** (FIX). Stroke and shadow: never a thick outline together with a heavy drop shadow.

- combo: flag Outline > 0 together with Shadow > 2 px (house)
- neon: no saturated green stroke (hue 90-150 deg, S > 0.7) in yt, vsl or brand (house; JOYSPACE)
- check: ASS Outline/Shadow relative to Fontsize; HSV of the 3c colour.

**TY-07** (FIX). Case, accent colour and emoji discipline.

- case: UPPER allowed in reel only; sentence case elsewhere (sourced; KAPWING; JOYSPACE)
- accent: 1 accent colour per video plus neutrals; at most 1 accented word per caption event; in premium, at most 15% of words highlighted (house; OPUS)
- accent contrast: at least 3:1 (sourced; WCAG143)
- emoji: 0 in yt, vsl and brand; reel at most 1 per 30 s, placed by a human (house; JOYSPACE; SUBMAGIC)
- check: ASS colour overrides per word; emoji regex.

**TY-08** (WARN). Graphics use a 60/30/10 palette.

- split: 60% dark variant, 30% light variant, 10% accent (sourced; SOZAI_GADZHI)
- accent area: 5-15% of overlay area, one accent hue, variants within +/-15 deg (house)
- check: k-means (k=4) on the overlay alpha region.

**TY-09** (FIX). Glass cards: one at a time, never over the face, never thin.

- dim: about 35% dark layer under clear glass on bright footage (sourced; HIG_MAT)
- blur fill: backdrop blur 12-20 CSS px at 1080 width; fill 12-25% (sourced-low; vendor glassmorphism guides)
- contrast: 4.5:1 against the worst-case blurred backdrop (sourced; WCAG143)
- check: At most 1 glass node per frame; glass bbox does not touch the face bbox.

### Captions

**CP-01** (FIX). Chunk captions according to the profile's caption_mode.

- word mode: about 2 words, break on pauses of 0.3 s or more; grow to 3 words rather than show a cue under 0.35 s (sourced; VIDEOUSE)
- sentence mode: at most 42 chars per line, 2 lines, 20 cps (sourced; NFX_TTSG)
- cps scope: the cps limit applies only in sentence mode, since word-synced captions run at the speech rate (house)
- reel: burned captions of 1 to 6 words; the Hormozi look uses 2 to 3 words (measured; KIT_EG (EDITING_GRAMMAR.md, 22 videos, sources in RESEARCH.md))
- check: Parse ASS for words, chars and duration per event.

**CP-02** (FIX). Caption timing follows the word clock.

- in time: first frame of the first word, +/-2 frames (sourced; NFX_TIME)
- gaps: 2 frames, or at least 0.5 s; close gaps of 3-11 frames to 2 (sourced; NFX_TIME)
- min dur: sentence mode 20 frames at 24 fps (25 at 30); word mode 0.35 s (sourced; NFX_TIME; VIDEOUSE)
- tail: at least 0.5 s after the audio ends when nothing follows (sourced; NFX_TIME)
- cut snap: speech starting within 0.5 s after a cut starts on the cut; an out-time within 0.5 s before a cut moves to cut minus 2 frames (sourced; NFX_TIME)
- onset error: 40 ms or less (house)
- punch word: never show a punch word before it is spoken (sourced; SONILO)
- check: Compare ASS events with mapped word times and EDL cuts.

**CP-03** (FIX). Line breaks follow Netflix rules: never split article+noun, adjective+noun, first+last name, pronoun+verb, verb+preposition, or auxiliary/negation+verb.

- forbidden splits: 0 (sourced; NFX_TTSG)
- check: POS check with a small spaCy model (MIT) on line and chunk boundaries.

**CP-04** (BLOCK). On-screen words and numbers mirror the speech or the brief exactly. Whisper supplies the clock, not the words.

- invented values: 0 (sourced; KIT_RULES)
- check: Every text layer string must appear in the cached transcript or the brief.

**CP-05** (FIX). Captions never cover the face, mouth, chin, hands or a discussed product. If the face sits low, move captions to the upper safe area rather than shrinking them below the floor.

- exclusion: face bbox expanded 15% downward and 4% on the other sides (house; REAP)
- zone: inside the profile's safe_zones preset (sourced; safe_zones)
- check: Rasterised caption bbox vs MediaPipe face and hand boxes on the burned file.
- engine: review.py fails captions when more than 5% of sampled frames have the chin inside the caption block; placement.py fails any chip or label with more than 2% of its box over the face.

**CP-06** (FIX). Burn captions last, after every overlay, and verify them on the encoded file.

- order: subtitle filter is last in the graph (sourced; VIDEOUSE)
- check: Graph order plus sampled frames.

**CP-07** (BLOCK). Owner copy lint for SMA work: on-screen text never contains the word 'annuity' and never contains an em dash.

- hits: 0 (sourced; KIT_RULES)
- check: Case-insensitive regex over ASS and scene text. A hit also flags the script line it came from.

### Motion

**MO-01** (FIX). Durations in frames.

- micro: 3 f (100 ms) (sourced; NNG)
- enter: 6-12 f (200-400 ms); 5-10 f at 24 fps (sourced; NNG; M3; CARBON)
- exit: 5-8 f and never longer than the entrance (sourced; NNG)
- max: 15 f unless it is a deliberate slow title (sourced; NNG (500 ms or more drags))
- check: plan-lint of every enter and exit track.

**MO-02** (FIX). Entrances decelerate, exits accelerate, moves use a standard curve. Linear is never used on transform tracks; it is allowed only on opacity and constant drift.

- enter: cubic-bezier(0.05,0.7,0.1,1.0) or (0,0,0.3,1) or easeOutCubic (0.215,0.61,0.355,1) (sourced; M3; CARBON; BACK)
- exit: (0.3,0,0.8,0.15) or (0.4,0.14,1,1) (sourced; M3; CARBON)
- move: (0.2,0,0,1) or (0.4,0.14,0.3,1) (sourced; M3; CARBON)
- check: Lint scene CSS/JS and ASS t-accel values.

**MO-03** (FIX). Overshoot budget per profile.

- spring: stiffness=(2*pi/d)^2, damping=4*pi*(1-bounce)/d; Spring(0.5, 0.3) = k 157.9, c 17.6 (sourced; APPLE_SPRING)
- overshoot: bounce 0.15 = 0.6%, 0.2 = 1.5%, 0.3 = 4.6%, 0.4 = 9.5%; easeOutBack peaks 8.7% (Flutter) or 9.8% (easings.net) (computed; APPLE_SPRING; BACK)
- never: bounce above 0.4 on text (sourced; APPLE_SPRING)
- check: Sample each scale/position track per frame; maximum excursion past the final value must be within profile_defaults.overshoot_max_pct.

**MO-04** (FIX). Stagger rules. Reveal one new independent element at a time.

- stagger: 20-50 ms per item, whole cascade within 500 ms (sourced (20/500) / house (50); CARBON)
- parallel: no simultaneous entrances of unrelated elements (sourced; VIDEOUSE)
- check: Item start offsets per group.

**MO-05** (WARN). Pop profiles.

- premium: scale 0.92 -> 1.0 with opacity 0 -> 1 over 6-9 f, plus a 4-8 px rise (house; M3; NNG)
- check: Keyframe lint per profile.

**MO-07** (FIX). Moment cadence follows the profile, and a recurring concept reuses the same template.

- cadence: see profile_defaults.graphic_moments_per_min_body (sourced/house; SOZAI_GADZHI)
- callbacks: same concept key -> same template, colour and position (sourced; SOZAI_GADZHI)
- check: Timeline lint of moment spacing and concept-key to template map.

**MO-08** (FIX). The animation payoff lands on the spoken payoff word.

- start: overlay start = payoff word start - reveal duration; reveal completes within 1 f of the word (sourced; VIDEOUSE)
- check: plan-lint plus a frame at the cue.

**MO-09** (FIX). Overlays stay up long enough to read.

- explanatory: at least 3 s; simple cards 5-7 s; complex diagrams 8-14 s; beat accents 0.5-2 s; hold the last frame at least 1 s; over narration, at least narration length + 1 s (sourced; VIDEOUSE)
- text: at least 0.3 s per word + 0.5 s (sourced; OPUS)
- check: plan-lint by overlay type.
- engine: layers.py chips hold 1.6 s unless the layers file sets hold or until, which fits a label of up to 3 words at this rule's 0.3 s per word plus 0.5 s.

**MO-10** (BLOCK). HTML scenes are pure functions of time.

- contract: render(t, f) with t = f/fps; no Math.random, Date, performance.now, timers or running CSS animations; seeded RNG; local fonts awaited; video frames from an image sequence (sourced; HYPERFRAMES)
- clock: Playwright clock.install() first, then run_for(1000/fps) between screenshots (sourced; PLAYWRIGHT_CLOCK)
- check: Render a frame sample twice: PNGs byte-identical, no network requests during render, grep for banned APIs.

## 4. Voice timing

**VO-01** (BLOCK). Measure before touching speed or pauses. Reuse a project's locked word maps and never re-transcribe.

- inputs: raw_wpm, sentence_gap_p50/p90, comma_gap_p50, silence_p90 per take (house; OWNER_FM; KIT_VSLB)
- check: plan.json carries the stats before any render.

**VO-02** (FIX). Hit the profile's effective wpm band, measured on the render from first word to last word.

- band: see profile_defaults.effective_wpm (house; KIM19; GUYER24)
- window: each 60 s window within +/-15% of the mean (house)
- check: Map source word times through the EDL cuts and stretch ratios; never re-transcribe.

**VO-03** (BLOCK). Choose one global speed factor from the raw rate. Never use speed to fix a slow script.

- raw ge 190: 1.00 (house; M_HORMOZI_POD)
- raw 160 189: 1.03-1.07 (house; GUYER24)
- raw lt 160: 1.08-1.10 (house; GUYER24 (+10-15% helped))
- cap: 1.12; 1.10 on tight face or hand close-ups (house; DESPERATI17 (+/-12% unnoticed on wide footage); QUENE_DRIFT (drift JND 14-15%))
- never: 1.15 or more on persuasive talk; never below 1.00 (re-record instead) (house; GUYER24 (+25% hurt strong arguments); ROBERTS20)
- check: Every stretch ratio in the EDL is within the cap and matches the table.
- engine: The engine never time-stretches, and EDITING_GRAMMAR.md caps speed at 1.05x. The bands above 1.05 are research only until an A/B says otherwise.

**VO-04** (FIX). Trim dead air first. Stretch only if post-trim wpm is still below the band. If post-trim wpm is above the band, restore pauses toward the top of the band and flag a slower re-record.

- evidence: Hormozi edited 226 vs natural 216 wpm, about 5% (measured; M_HORMOZI; M_HORMOZI_POD)
- check: Render log shows wpm after trim and after stretch.

**VO-05** (BLOCK). The owner's own takes are already fast: never speed them up.

- raw: 199/226/219 wpm on takes 1-3; sentence gaps median 420-480 ms; comma gaps 140-200 ms; no RMS silence of 800 ms or more (measured; OWNER_FM)
- stretch: 1.00 (house; OWNER_FM)
- check: Any owner plan shows stretch 1.00.

**VO-06** (FIX). Pause targets by boundary type and profile. Pauses must vary.

- targets: see profile_defaults clause/sentence/emphasis (house; LIU22)
- variation: sentence-gap CV at least 0.3; no more than 70% of sentence gaps under 120 ms (house; R_EDITORS; VIZARD_PAUSE)
- lower bound note: Whisper word ends absorb silence, so measure on RMS-refined boundaries (measured; OWNER_FM)
- check: p50 and p90 per boundary type inside the band; zero gaps above the format max except allowed beats.
- engine: cut.py removes dead air over 0.35 s; the layers breath keeps sentence ends at the set value: 0.45 s (vsl_hero), 0.4 s (yt_authority, skool_lesson), 0.3 s (reels), from edit.py DEFAULTS. Without breath, a 1.2 s sentence gap came out at 0.06 s (run 2026-11-02).

**VO-07** (BLOCK). Never cut inside a word. Splice in RMS silence at its quietest 20 ms window.

- pads rms: 50 ms before onset, 80 ms after offset (house; AFP (35/60); VIDEOUSE (50/80))
- pads whisper only: 120 ms before, 180 ms after (house; AFP (100-200/150-300))
- cut level: 20 ms RMS at the cut <= -36 dBFS, or 20 dB or more under median speech (sourced; OWNER_FM)
- gap safety: 400 ms or more is clean; 150-400 ms needs a visual check; under 150 ms is unsafe (sourced; VIDEOUSE)
- check: Per splice: level at the cut and distance to the nearest word boundary.
- engine: cut.py pads: a piece starts at the end of the silence before the word minus 0.03 s (no earlier than 0.15 s before the word), or 0.05 s before it with no silence found; it ends 0.04 s into the silence after the word (no later than 0.15 s), or 0.08 s after it.

**VO-08** (FIX). Trim only what is worth trimming, and never create micro-clips.

- min excess: shorten a gap only if it exceeds its target by more than 120 ms (house)
- min removed: 120 ms (house; AFP (220 ms auto gap))
- min kept: 100 ms (sourced; AUTOEDITOR (0.2 s min-cut / 0.1 s min-clip))
- check: EDL scan.

**VO-09** (FIX). Crossfade every audio splice with an equal-power fade. Never leave ffmpeg's 1 s linear default.

- default: 30 ms qsin acrossfade (house; VIDEOUSE (30 ms))
- range: 10-67 ms: 10-20 ms in clean room tone, 20-50 ms where noise is audible, 1-2 frames by NLE convention (sourced; AUDIOJS; AFP; PEACHPIT)
- ffmpeg default: acrossfade and afade default to 1 s tri (sourced; FFMPEG_local)
- check: Every join has an explicit 10-67 ms fade, and energy above 8 kHz within +/-5 ms of the join is no more than baseline + 6 dB (house).
- engine: sound.py assemble_voice joins the pieces with a 10 ms equal-power crossfade centred on each cut, and fades the last 0.25 s.

**VO-10** (BLOCK). Speech is jump-cut, never dissolved. The picture may jump, punch in or morph.

- overlap: any transition over 100 ms requires both sides <= -36 dBFS inside the overlap (house)
- morph: 12-15 f picture; 8 f video / 2 f audio also reported (sourced; LJ_MORPH; R_EDITORS)
- check: RMS of both sides inside every overlap.

**VO-11** (WARN). Split edits (J/L cuts) by frame count.

- j lead: 4-12 f, default 8 (sourced; FLASHBOARDS; SALT15)
- l tail: 8-15 f (sourced-low; SPLIT_TIPS)
- section: 1-3 s (sourced; FLASHBOARDS)
- speaker change: picture cut within 6 f after the outgoing last word (sourced; SALT15)
- quota: at least 40% of b-roll entries and section changes are split edits offset 6-24 f (house)
- check: Offset between each video cut and its audio cut.

**VO-12** (FIX). Breaths follow profile_defaults.breaths. Never replace a breath with digital silence. Attenuate toward a target level instead of deleting.

- attenuation: -6 to -10 dB with 10-20 ms fades (sourced; SSE_BREATH; GRAVY; IZO_BREATH)
- check: No breath inside a sentence; kept breaths 6-10 dB below source.
- engine: sound.py keeps breaths 6 dB down (gaps of 0.12-1.2 s that rise about 9 dB over the room).

**VO-13** (BLOCK). Room tone is continuous: no digital silence anywhere in the program.

- digital silence: fail any run of 10 ms or more below -90 dBFS (sourced; AUDIOJS)
- window: warn on any 100 ms window below -80 dBFS (house)
- fill: within +/-2 dB of the take's own floor (house; AUDIOJS)
- floor: between -75 and -60 dBFS (-60 or below from ACX) (house; ACX)
- across cuts: floor difference 3 dB or less (house; ONEOF10)
- check: Scan the mix between the first and last frame.
- engine: sound.py drops pauses of 0.18 s or more by 4 dB, never to silence. Open item: the voice stem is zeros after the last word and the end card's audio is generated silence (longform.py anullsrc), so a video with no music bed has digital silence over the end card.

**VO-14** (FIX). Speed stays constant per speaker, with no ramps inside a sentence.

- adjacent delta: 0.03 or less (house; QUENE07 (paired JND about 5%))
- check: Maximum difference between neighbouring EDL ratios.

**VO-15** (BLOCK). Stretcher policy.

- default: Signalsmith Stretch via python-stretch 0.3.1 (MIT, wheels for macOS arm64/x86_64, Windows, Linux) (sourced; SIGNALSMITH)
- fallback: ffmpeg atempo (LGPL, WSOLA) (sourced; ATEMPO)
- owner only: Rubber Band R3 CLI (GPL), user-installed (sourced; RUBBERBAND)
- banned: librosa.phase_vocoder (artifacts), pytsmod (GPL-3.0), ffmpeg rubberband filter as a dependency (sourced; LIBROSA_PV; PYTSMOD; RUBBERBAND)
- check: Licence scan of the default install; render log names the backend.

**VO-16** (BLOCK). After any stretch, picture and sound move by the same factor and stay in sync.

- sync: A/V offset 1 frame or less (house; ITU1359 (detectability +45 ms lead / -125 ms lag))
- duration: per-segment error 1 frame or less; audiotsm overshot 1.10 to 1.123 on a 2 s clip (measured; AUDIOTSM)
- check: Per-segment stream duration deltas.

**VO-17** (FIX). Re-time captions from the post-edit mapping, never from a new transcription.

- error: 40 ms or less on 20 sampled words (house; KIT_VSLB)
- check: ASS start vs audio onset in the render.

**VO-18** (WARN). De-ess with a dynamic EQ, only during sibilant events.

- band: detect 4-10 kHz; centre 5-6 kHz (male, the owner) or 7-8 kHz (female) (sourced; IZO_DEESS; ANTARES)
- cap: about 6 dB gain reduction (house (unverified))
- no lisp: vowel-frame HF within +/-1 dB of source (house)
- check: adynamicequalizer log plus band levels.
- engine: sound.py de-esses frames where 4.5-10 kHz runs 6 dB hotter than usual against 1-4 kHz, at most 6 dB.

**VO-19** (WARN). Plosives: gentle high-pass on the whole voice, targeted cuts on individual pops.

- hpf: 80 Hz male to 100 Hz, 2 poles or more (sourced; PLOSIVE)
- pop: 100-200 Hz low cut on the pop region only (sourced; PLOSIVE)
- check: No 20-100 Hz burst above speech-band RMS at p/b onsets.
- engine: sound.py high-passes at 80 Hz, or 110 Hz when over 0.45 of the pause energy sits under 150 Hz, with a 2nd-order Butterworth run forward and backward (scipy sosfiltfilt). That doubles the slope: measured 2026-11-02 at 80 Hz, -6.0 dB at the corner and -24.6 dB an octave below, so about 24 dB per octave with the corner 6 dB down.

**VO-20** (FIX). Voice chain order: high-pass/de-plosive, denoise, trim/splice, stretch (speech only), de-ess, breath attenuation, room tone, loudness. Music and SFX are never stretched.

- order: as listed (house (no single source))
- check: Render log order; music/SFX ratio 1.00.
- engine: sound.py voice_master order: high-pass; one STFT pass for noise reduction, tone notches, wind shelf, EQ and de-ess; breaths; phrase clip gain; leveller; peak catcher; one gain to -16 LUFS; pause dip. There is no stretch stage.

**VO-21** (BLOCK). Stretch quality needs ears, because objective metrics are unreliable.

- ab: 3 blind headphone checkpoints whenever any ratio is not 1.00: hook line, densest sentence, sibilant-heavy line (sourced; ROBERTS20)
- check: QC log has 3 passing A/B entries.

**VO-22** (WARN). Silence detection parameters.

- params: 20 ms RMS window; -36 dBFS on the owner's setup, or 3-5% of mean energy adaptively; minimum silence 80 ms (sourced; OWNER_FM; AFP; FFMPEG_local)
- check: Reproducible silence list on re-run.

**VO-23** (FIX). Filler removal follows the profile band and never clips the next word.

- onset guard: no cut within 20 ms of an onset energy rise (house)
- check: Filler counts source vs output; RMS envelope at each cut.

**VO-24** (WARN). Brand and Gadzhi pattern: move pauses out of sentences into deliberate rests at section turns.

- rest: speech-free beats of 3 s or more only at scripted section markers (Gadzhi breathers 7-13 s) (measured (breathers) / house (3 s); M_GADZHI)
- check: No beat of 3 s or more inside a sentence.

**VO-25** (WARN). Front-load density in reel and yt; plan re-engagement beats in long-form. Not applied to vsl (DA-2).

- caps: see profile_defaults.first_60s_max_pause_ms; re-engagement near 180 s and 360 s (house; MRBEAST_GUIDE)
- check: Maximum gap in the first 60 s; plan tags.

## 5. Audio layers

The full audio spec, with the engine's numbers, is `docs/AUDIO_SPEC.md`.

**AU-01** (BLOCK). Keep the voice, music and effects as separate stems, and transcribe only the clean voice.

- stems: voice.wav, music.wav, sfx.wav and mix.wav, every decision in sound.json (house; KIT_CODE sound.py direct)
- check: the transcript comes from the voice track, never from the mix.

**AU-02** (FIX). Each voice is brought to one loudness before mixing, so cuts between takes do not jump in level.

- stem: -16 LUFS, one static gain, no limiter on the voice stem (house; KIT_CODE sound.py stem_lufs; M_GADZHI measured voice stem -16.5 LUFS)
- spread: 1 LU or less between takes (house)

**AU-03** (BLOCK). Master once and measure the encoded file.

- target: -14 LUFS integrated, pass -15.0 to -13.0 (sourced; SPOTIFY; YT_SFN)
- tp: -1.0 dBTP or lower, measured on the encoded AAC (sourced; SPOTIFY)
- loudnorm: two-pass, linear=true, I set explicitly; the ffmpeg defaults (I -24, LRA 7, TP -2) are not our target (sourced; FFMPEG_local)
- ott: -27 LKFS dialogue-gated +/-2 LU, TP -2 (sourced; NFX_MIX)
- check: ebur128 peak=true on the delivered MP4; re-run the limiter until it passes.
- engine: Delivery targets are in tools/studio/platforms.py: -14 LUFS and -1.5 dBTP for social and YouTube, -15 and -1.2 for web_vsl, -23 and -1.0 for broadcast. voice.py final_filter sets one gain and one limiter; review.py passes within 1.0 LU and a true peak no more than 0.3 dB over target.

**AU-04** (FIX). The music bed sits under the voice by the profile gap. Loudness-normalize each track before applying the gap.

- gap: see profile_defaults.music_gap_lu_under_voice (house; WCAG147; OVERSEER)
- measure: 3 s short-term LUFS, music stem vs voice stem, in VAD speech windows; the median must be in range (house)
- floor: flag any 3 s window under 15 LU (house; OVERSEER)
- spread: commercial tracks span about 18 LU (-28 to -10 LUFS) (sourced; OVERSEER)
- check: Per-stem LUFS logged in the sound manifest.
- engine: The engine's targets win: the layers file's `sound.sections` set voice over music per section on momentary loudness while words play. `closer.py edit` writes them from edit.py DEFAULTS (vsl_hero 11 / 14 / 12 LU; paid ad 12; organic reel 16; yt_authority and skool_lesson 20), and a section with no p10 floor gets its target minus 6 (longform.py), which gives vsl_hero 5 / 8 / 6. SECTION_PRESETS in sound.py holds the same values plus story 23 and is read by nothing; with no sections the target is 14. The review gate is a median of 9 or more and a worst 5% of 3 or more. The profile gaps above were this rulebook's first proposal, superseded by the measured audio spec (docs/AUDIO_SPEC.md).

**AU-05** (FIX). Duck with keyframes precomputed from word timings. The sidechain compressor is only a fallback.

- pre duck: fully ducked 100-200 ms before each phrase's first word (house (unverified); DUCK_TUT)
- extra: 6-12 dB on top of the static gap (sourced-low; DUCK_TUT)
- ramp up: 500-800 ms (sourced-low; PREMIERE_DUCK; VIDPROS)
- rise: music rises only in speech gaps of 1.5 s or more, toward its music-alone level (house; EPIDEMIC; VIDPROS)
- fallback: attack 20-60 ms, release 300-500 ms (700 if pumping); hold of 400 ms or more done in the envelope, since sidechaincompress has no hold and its default release of 250 ms is too fast (sourced-low; DUCK_TUT; FFMPEG_local)
- no pump: no recovery above 3 dB inside gaps under 400 ms (house)
- check: Music stem gain envelope.
- engine: sound.py: the bed is down 0.2 s before each phrase and gets there in 0.15 s; it rises 6 dB (8 dB in the first 8 s) only in pauses of 1.2 s or more, starting 0.25 s after the phrase, over 0.6 s. No sidechain compressor.

**AU-06** (WARN). Carve space for the voice by cutting the music, never by boosting the voice.

- carve: -3 dB at 3 kHz, Q about 1 (range -2 to -4 dB), only while the voice is active (sourced-low; EQ_CARVE)
- alt: -3 to -6 dB at 800-3000 Hz for vocal or mid-heavy beds (sourced-low; VIDPROS)
- check: Music 2-5 kHz band at least 2 dB lower in speech windows than in gaps (house).
- engine: sound.py: a 300 Hz-4 kHz pocket, 2 dB down all the time, plus 4 dB (bright bed), 2 dB (medium) or nothing (dark) while words play.

**AU-07** (FIX). SFX levels relative to the voice's short-term loudness. Nothing is louder than the voice.

- hits: -6 to -12 dB (house; YTSFX; WCAG147 (exempts sounds of 1-2 s))
- whoosh: -12 to -20 dB (house; YTSFX)
- ui: -15 to -20 dB (house; YTSFX)
- check: Momentary loudness per SFX event minus the voice median.
- engine: sound.py dialect tables set every level in LU against the voice stem; a sound on a word goes 5 dB lower except risers and reverses (docs/AUDIO_SPEC.md section 4).

**AU-08** (BLOCK). Every recorded sound is measured once when it is imported, and placed by its own hit point, never by file zero.

- tool: librosa (ISC) (sourced; LIBROSA)
- fields: onset (first point within 30 dB of the peak), peak, end (where it falls 20 dB under the peak for good), loudest 400 ms, length; cached in index.json in the folder (house; KIT_CODE (sound.py Library))
- check: Unit test: every catalog entry has the fields and placement code uses them.

**AU-09** (FIX). A whoosh starts before the cut, and its peak lands on the first frame of the new shot.

- align: peak on the cut frame +/-1 f; start = cut_t - peak_offset (sourced; MORPHIC)
- check: Envelope peak time vs cut time.
- engine: sound.py lands the peak of whooshes, swishes and reverses on the event frame.

**AU-10** (FIX). Impacts, pops, clicks and text landings put their onset on the landing frame. Late is better than early.

- window: [-1, +2] f = [-33, +67] ms at 30 fps, [-42, +83] ms at 24 fps (house; ITU1359)
- check: librosa onset_detect on the SFX stem vs event times.
- engine: sound.py lands the start of impacts, subs, shines and ticks on the event frame.

**AU-11** (FIX). A riser builds into the reveal, peaks just before it and stops dead on it, with an impact or a silence on the reveal frame.

- start: 2-3 s early; 4-6 s for a big build (sourced-low; YTSFX; MORPHIC)
- stop: maximum within 1 f before the reveal; at least 20 dB down within 2 f after (house)
- check: Riser stem envelope.
- engine: sound.py lands the end of a riser on the event frame and cuts it there.

**AU-12** (FIX). Every SFX is motivated and tied to an event. SFX attach to graphic moments, not to plain jump cuts.

- density: see profile_defaults.sfx_per_min; montage segments may reach about 0.45/s (8 in 18 s reads designed, about 20 reads generic) (sourced/house; VIDEOUSE; YTSFX)
- event id: 100% of cues name the event they belong to (sourced; VIDEOUSE)
- cut share: SFX on no more than 25% of cuts (house; CHOPPITY_AH (no transition SFX))
- check: Sliding 60 s count, sample hashes and event links.
- engine: sound.py budgets: gadzhi 8 events in the first 20 s, 4 in any 60 s after; nelk 14 and 12; events closer than 0.35 s are dropped; files of a role are taken in turn (Library.pick), so a role with one file, or with only the synthesized fallback, repeats the same sound every time (`rotate_max_repeat` 2 is defined but not read). review.py gate: 12 per minute.

**AU-13** (WARN). Silence drop before a punchline: pull the music and SFX tails, keep room tone, land the line dry.

- drop: 0.3-1.0 s; music at least 30 dB down (house (unverified); SONILO; MASTERCLASS)
- check: Music stem level in the drop window; room tone RMS above -70 dBFS.
- engine: sound.py drops the bed to -40 dB from 0.4 s before the line (a third value in the layers `music.mute` window sets another lead, longform.py), reached through a 60 ms fade. The bed comes back on the next bar if one falls within 1.0 s of the window's end, in one 10 ms step of the gain curve (`return_ramp_s` 0.02 is defined but not read). At most 3 drops.

**AU-14** (FIX). Edit music only on downbeats at section boundaries. Hide unavoidable splices under an impact or whoosh.

- seam: on a downbeat +/-1 f (sourced; SOUNDSTRIPE; PREMIUMBEAT)
- tempo: inter-beat interval change across the seam under 3%; no two downbeats closer than 0.75 bar (house)
- tool: Beat This! (MIT code and weights), CPU, without --dbn (madmom) (sourced; BEATTHIS)
- check: Re-track the rendered music stem.
- engine: sound.py cuts music on bar lines with a 40 ms equal-power crossfade: a long track starts on a bar in its first 40% and splices into its own last 4 bars; a short one repeats an even number of bars.

**AU-15** (FIX). End on the music, not a lazy fade.

- button: final hit within 1 f of the last content or end-card frame (sourced; PREMIUMBEAT)
- fallback: a fade of 0.3 s or more from a phrase end (sourced-low; MUBERT)
- check: Last strong onset vs end frame.
- engine: sound.py raises the bed 6 dB over 2 s after the last word and fades the last 1.2 s: the fade fallback, not a button.

**AU-16** (WARN). Cut picture to the beat only in music-led montage. Talking-head cuts follow the speech.

- grid: frames per beat = fps*60/BPM; 120 BPM = 15 f at 30 fps, 12 f at 24 fps (computed)
- hit rate: at least 70% of montage cuts within 1 f of a beat (house)
- check: Beat track vs EDL in montage segments.

**AU-17** (WARN). Sub drops, tape stops and record scratches are rare punctuation.

- cap: at most 1 per type per minute (house (no source found))
- check: Manifest count; impact alignment rules apply.

**AU-18** (FIX). Section loudness is consistent: no end card 15 dB under the dialogue, no effects louder than speech.

- rule: as stated (sourced; VIDEOUSE)
- check: RMS per section on the encoded file.

**AU-19** (WARN). Report audio as 'measured, not listened' unless real playback was used.

- rule: include LUFS and dBTP in the report (sourced; VIDEOUSE)
- check: Text present in the delivery message.
- engine: sound.json carries the qc numbers; the sound-director skill reports them as measured, not listened.

## 6. Anti-slop tells

| ID | Tell | Threshold | Provenance | Sources | Severity |
|---|---|---|---|---|---|
| AS-01 | Metronomic engine events (punch-ins, overlays, SFX). Cuts forced by the speech are exempt. | CV of intervals at least 0.5; no more than 2 consecutive intervals within +/-10%; autocorrelation peak below 0.4 at any fixed lag | house | CUTTING10; ONEOF10 | FIX |
| AS-02 | Flat tempo with no phrasing | lag-1 Pearson r of log shot durations above 0.1 (only when there are more than 20 shots) | house | CUTTING10 | WARN |
| AS-03 | Zooms landing mid-clause | a scale change starts within 80 ms before a sentence or clause start, or after a pause of 250 ms or more | house (principle sourced) | VIZARD_PUNCH | FIX |
| AS-04 | Every jump cut at the same scale | scale delta at least 0.10, or B-roll or morph cover; no more than 3 consecutive cuts at the same scale; alternate every 2nd-3rd cut | sourced (110-120%, alternation) / house (run cap) | ONEOF10 | FIX |
| AS-05 | Zoom pulses and breathing zooms everywhere | 0 scale reversals within 1.0 s; at most 1 animated push-in per 30 s in vsl and brand; no more than 40% of shots with continuous scale animation | house | JOYSPACE; SUBMAGIC | FIX |
| AS-06 | Breathless pacing with every pause removed | VO-06 bands, CV at least 0.3, no more than 70% of sentence gaps under 120 ms | house | R_EDITORS; VIZARD_PAUSE; ONEOF10 | FIX |
| AS-07 | Sterile 100% filler removal in conversational content | profile filler band | sourced | R_EDITORS; R_PODCAST; SOUNDGIRLS | WARN |
| AS-08 | Clicks at cuts | VO-09 | see VO-09 | ONEOF10 | FIX |
| AS-09 | Dead-air holes and room tone that changes at cuts | VO-13 | see VO-13 | ONEOF10; VIZARD_PAUSE | BLOCK |
| AS-10 | Cuts with no motivating motion | at least 30% of non-jump cuts have optical flow above the shot median in the 4 f after the cut; suggest shifting up to 6 f toward a motion onset | house | SMITH08 (about 25% of edits missed, about 33% at motion onset) | WARN |
| AS-11 | Cutting into emotional or punchline beats | hold at least 0.6 s after the last word of a tagged line | house | ONEOF10; MURCH | FIX |
| AS-12 | Uniform, unmotivated graphic density | each body overlay has a trigger (a digit, proof, new concept, or more than 20 s since the last visual); intro/body ratio per profile | sourced (triggers) / house (20 s) | SOZAI_GADZHI | FIX |
| AS-13 | Shot lengths out of style | profile median band; shots under 1.0 s at most 15% | house | SUBSCRIBR; CHOPPITY_AH; CHOPPITY_LH | WARN |
| AS-14 | Text too fast to read | MO-09 | sourced | OPUS; VIDEOUSE | FIX |
| AS-15 | Rainbow karaoke, every word highlighted | TY-07 | house | OPUS; JOYSPACE; KAPWING | FIX |
| AS-16 | Auto-emoji | TY-07 | house | JOYSPACE; SUBMAGIC | FIX |
| AS-17 | Stock 'bold font + neon green stroke' caption look | TY-06 and TY-01 | house | JOYSPACE; KAPWING | FIX |
| AS-18 | Jarring pops and linear slides | MO-02 and MO-03 | sourced | M3; JOYSPACE | FIX |
| AS-19 | Everything dead centre | no more than 50% of overlay x-centroids within 5% of frame centre (yt, vsl, brand) | house (unverified convention) | KAPWING | WARN |
| AS-20 | No callbacks; every mention of a concept looks new | MO-07 callbacks at 100% | sourced | SOZAI_GADZHI | FIX |
| AS-21 | Context-blind stock B-roll | after the grade, mean luminance within +/-12% of the adjacent A-roll and mean chroma delta-E 8 or less; optional open_clip (MIT) similarity at least the project median; no topic-to-stock fill | house | WIDEFRAME; MONEYPRINTER | FIX |
| AS-22 | Grade drifting across A-roll | face Lab delta-E 5 or less between A-roll shots; black point per profile | house | WIDEFRAME | WARN |
| AS-23 | Squashed, robotic voice | compression ratio 4:1 or less (about 3:1 typical); PLR (TP minus I) at least 9 dB | sourced (3:1) / house (4:1, PLR unverified) | VIDPROS; R_PODCAST | WARN |
| AS-24 | A whoosh on every cut | AU-12 | house | GETIMG; SONILO; CHOPPITY_AH | FIX |
| AS-25 | SFX off the frame | AU-09 and AU-10 | see rules | ITU1359; MORPHIC | FIX |
| AS-26 | Generative face fixes (eye contact, jump-cut synthesis, swaps, beauty filters) | 0 (the render graph has only whole-frame transforms on footage) | house (JUMPCUT_SYNTH shows the technique to avoid) | JUMPCUT_SYNTH | BLOCK |
| AS-29 | Captions straddling cuts by a few frames | CP-02 cut_snap | sourced | NFX_TIME | FIX |
| AS-30 | Robotic TTS (only when TTS is used) | speed 0.9-1.1; break tags of 3 s or less and at most 1 per 2 sentences; 0 raw digits; pause CV at least 0.3 | sourced (0.7-1.2 range, 3 s) / house (rest) | ELEVEN | FIX |
| AS-31 | Invented numbers on screen | CP-04 | sourced | KIT_RULES | BLOCK |
| AS-32 | Auto-reframe tunnel vision | FR-06 | house | R_REFRAME | FIX |
| AS-33 | Captions over the face | CP-05 | house | REAP | FIX |
| AS-34 | Rules fighting each other | resolve in Murch order: emotion, story, rhythm, eye-trace, 2D plane, 3D space (weights 0.51/0.23/0.10/0.07/0.05/0.04) | sourced-low (weights unverified against the book) | MURCH | WARN |

- AS-04 engine: cut.py alternates the format's zooms and flips any two equal neighbours.
- AS-05 engine: Every piece carries the slow push (FR-04), so every shot has continuous scale animation. Open conflict with this rule's 40% (house).
- AS-13 engine: review.py fails any static stretch over 8 s in every format, stricter than the profile's max_static_framing.
- AS-23 engine: sound.py runs a 1.5:1 leveller and a 3:1 peak catcher.

Dropped from this copy for lack of a public source: plastic or over-sharpened skin as its own tell (TX-04 covers sharpening) and a ban on synthesized effects (the engine keeps synthesized sounds as a fallback, see docs/AUDIO_SPEC.md).

## 7. From a sentence to an edit

### What runs today

- `closer.py edit VIDEO "what you want" --out DIR` reads the sentence with a fixed word list (`INTENT_RULES` in `tools/studio/edit.py`, first match wins), analyses the footage, writes plan.json (format, platform, dialect, words per minute, a reason for every decision, the ranked music, next steps) and layers.json (finish profile, breath, sound sections), then renders a preview and runs the review for 16:9 formats. Vertical formats get the reel command to run. A requested length is recorded, not yet applied (KIT_CODE).
- `closer.py review JOB` writes report.md and sheet.jpg; `closer.py compare A B` writes compare.html (section 8) (KIT_CODE).

### The target design (research, not built yet)

- **Ingest.** ffprobe; word-level verbatim ASR (faster-whisper int8 on CPU); 20 ms RMS silences; EBU R128; shot cuts (PySceneDetect); the face track (YuNet). Results are cached by source hash and never rewritten, and a project with locked word maps is never transcribed again (VIDEOUSE; CASSETTE; KIT_VSLB).
- **Packed transcript.** Phrase lines break on silences of 0.5 s or more (sourced; VIDEOUSE).
- **Visual facts come from measurement.** Brightness, motion and face position come from computer vision, never from an LLM's captions; LAVE's 1 fps captions could not trim on brightness or motion (sourced; LAVE).
- **Plan.** strategy text and who confirmed it; output target (w, h, fps, frames); sources with hashes; ranges with source, start, end, word ids, beat, quote and reason; layers (captions, scenes with a concept key and a cue word, punch-ins at word ids, B-roll with licence); audio (music with licence and gap, duck lead, ramp and depth, effects with event ids); grade; finish. Every range, scene, punch-in and B-roll entry cites word ids or measured events, never free timecodes or caption text (VIDEOUSE; BSCRIPT; LAVE).
- **Reading an instruction.** Every instruction resolves to a word-anchored time range, an optional screen region (thirds grid or face-relative) and one operation from a fixed verb list before it becomes a change to the plan. Timecodes like 0:42 and regions like "top left" are accepted. ExpressEdit studied 176 commands from 10 editors and found three kinds of reference (temporal, spatial, operational) (sourced; EXPRESSEDIT).
- **Strategy gate.** Before cutting, confirm a plain-English strategy of 4 to 8 sentences (sourced; VIDEOUSE, its Hard Rule 11).
- **Style profiles.** One file per profile holds every numeric default with its provenance. Resolution order, lowest to highest: profile, platform preset, the user's locks, latest correction. BLOCK rules sit outside the chain and nothing overrides them (house; the CAPTIONS_APP pattern).
- **Validator.** One rulebook checks agent edits and manual edits alike. Errors point at the exact field, with the expected value and repair options, and a batch commits all or nothing. In Cassette-Editor's test on 277 damaged edits, located feedback cut repair input from 7.5M to 3.3M tokens and collateral damage from 7 cases to 1 (sourced; CASSETTE).
- **Render order.** Per-segment extract with grade and short fades, concat without re-encoding, overlays shifted by PTS, HTML scenes (MO-10), captions last, the mix, two-pass loudness, a BT.709 encode, then a true-peak check on the encoded file. Segments are cached by hash, so a correction re-renders only what it touches. Render a short preview and a contact sheet before the full render (VIDEOUSE; KAPWING_AI).
- **Review loop.** The checks marked BLOCK and FIX run on the encoded file. Review artefacts: a filmstrip and waveform at every cut, 1.5 s either side; the first and last 2 s and two or more mid-points; a contact sheet every 0.5 s that the agent actually looks at; stills at the start, peak and end of each moment (VIDEOUSE). At most 3 self-review passes per render, then report what is still open (sourced; VIDEOUSE). One fresh-eyes critic briefed to roast, then a regression check; a second round only if a BLOCK remains (house; KIT_RULES: a second agent reviews the final render with fresh eyes). Never chase a score: an MLLM judge agreed with humans at Pearson r = 0.73 on 20 videos (sourced; VIDEOUSE; AUTODIRECTOR). A scene passes at 4 of 5 on both meaning and look and is then frozen, with at most 3 iterations and every fix typed (retime, relayout, re-pick the take, rewrite the caption) (sourced; AUTODIRECTOR). Composition is the largest gap between agent and human edits, so spend review effort on framing (sourced; AUTODIRECTOR). Never mark a fix done without checking it on the new render (house; KIT_RULES, "say done only on all PASS").
- **Corrections.** Plain-English feedback becomes a patch on plan.json. "Keep" or "don't touch" adds a lock to the plan. Then validate again, re-render the touched segments, run the gates and append one line to the project log. Never re-transcribe (house; VIDEOUSE project memory).
- **Tools for an agent.** Expose plan-level tools (ingest, plan check, render, review, apply a correction), not two dozen ffmpeg verbs; video-audio-mcp wraps 27 ffmpeg tools (sourced; VAMCP).
- **Hand-off.** Export plan.json to .otio and FCP XML so a human editor can finish in Resolve or Premiere (sourced; OTIO).
- **Acceptance prompts.** "Edit this down to 2 minutes, focusing on when I talked about Freud" and "Hide my jumpcuts by adding zooms" (UNDERLORD); "Cut the VSL to 6 minutes, keep the pricing section untouched", "Make the hook hit harder but don't speed me up" and "Move the captions off my face from 1:10 to 1:30" (house).
- **Never.** LLM trims without word timing (LAVE); topic-to-stock pipelines (MONEYPRINTER); generative face fixes (JUMPCUT_SYNTH); a hosted speech-to-text service as the default (VIDEOUSE); a GPU-heavy multi-model stack as a requirement (VIDEOAGENT); Remotion or Node 22+ in the core (REMOTION; HYPERFRAMES).

## 8. Comparing two cuts

### What runs today

`closer.py compare A.mp4 B.mp4 --out DIR --labels v8,v9` (`tools/studio/compare.py`) measures both files and writes compare.json and compare.html: synced players with a wipe and a difference view, and both timelines drawn over each other. It measures:

- cuts, punch-ins included: a frame whose difference from the last spikes to at least 5 times the local median and 0.025 of full scale, at least 0.2 s after the previous cut, on a 96 px proxy at the native frame rate; then shot count, mean, median, longest and cuts per minute;
- picture at 4 samples per second on a 160 px proxy: luma, contrast, saturation, clipped highlights, motion;
- faces every 0.5 s with YuNet (share of samples with a face, face height);
- loudness: integrated LUFS, true peak, momentary and short-term curves, an approximate loudness range, and DNSMOS on the full mix when installed;
- a filmstrip every 2 s. A blind verdict in judge.json is shown when present.

Not built yet: VMAF and SSIM, scoring aligned by source timecode, caption and pacing pass rates, and the judge itself.

### Modes

- **Same timeline.** The edit lists match, so A and B differ only in grade, encode or render. Full-reference metrics are allowed (VMAF).
- **Different edits.** Align by source timecode through the two edit lists and score only the overlapping source ranges. Everything else uses structural metrics plus a blind judge. A global VMAF or SSIM between different cuts is refused (VMAF).

### Metrics (target design)

| Metric | How | Sources |
|---|---|---|
| VMAF | [distorted][reference]libvmaf; setpts=PTS-STARTPTS on both; -r before each -i; scale the distorted file to the reference with bicubic; the NEG model whenever sharpening, eq or a LUT differ. Report min, P1, P5 and mean; flag any 1 s window more than 10 points under the clip mean (house, unverified) | VMAF; FQM |
| SSIM / PSNR | ffmpeg ssim and psnr with stats_file; the fallback when libvmaf is missing (Ubuntu's apt ffmpeg 6.1.1 has none) | FFMPEG_local |
| loudness | ebur128 peak=true for I, LRA and TP; short-term every 0.1 s for both edits; the hook against the body median | FFMPEG_local; PYLOUDNORM |
| cuts and shot lengths | from the edit list when present; otherwise PySceneDetect ContentDetector at threshold 27, min_scene_len lowered from 15 to 4-6 frames for reels (house); TransNetV2 as a second opinion; cuts per minute, median, P10, P90 and a KS test on log length | PYSCENEDETECT; TRANSNET |
| punch-ins | from the edit list's scale events, or scdet (threshold 10) plus a jump in face size; histogram detectors miss same-shot punch-ins | FFMPEG_local |
| motion and freezes | siti TI per frame (ITU-T P.910); freezedetect n=0.001 d=2 s; every freeze must map to an intended hold | FFMPEG_local; P910 |
| colour and exposure | signalstats YAVG, SATAVG and stat=brng per shot; GR-04 and GR-05 on face masks | FFMPEG_local |
| faces and framing | YuNet at 5 fps (house); share of frames with a face, face height over H in 5 bins, eye height against the safe zone; keep the 2023mar model for OpenCV 4.x | YUNET |
| captions | CP-01 and CP-02 pass rates per edit | NFX_TIME; NFX_TTSG |
| voice pacing | effective wpm, pause p50 and p90 per boundary type, filler rate (VO-02, VO-06) | OWNER_FM (house) |
| audio layers | music gap per window, effects per minute, effect sync error | AU-04; AU-12 (house) |

### Views

- Synced two-player page: requestVideoFrameCallback drives B from A's mediaTime and shows the drift in frames (the callback can run one vsync late); frame step, 1 s step, shared pause (RVFC).
- A wipe slider for stills and grades (VIVICT design, MIT).
- Static strips: side by side, a blended difference, a tiled filmstrip, a waveform, a spectrogram, an ebur128 meter (FFMPEG_local).
- Charts of short-term loudness, shot-length histograms and face-size histograms drawn over each other.
- Optional outside viewers, never vendored: pixop video-compare (GPL-2.0), Vivict hosted, mpv side by side (syntax unverified).

### Judge protocol

1. The judge never receives video. It gets frame packs: the first and last frame of every shot, the peak frame of every caption and a uniform 1 fps track, in labelled 4x4 grids stamped MM:SS, images before text. Keep the long edge at 2576 px or less (at most 4784 visual tokens per image), and each image at 3000 px or less per side when sending more than 20 images (sourced; CLAUDE_VISION).
2. Blind: no file names, version numbers, metadata or plan; a fresh context, never the session that planned the edit (sourced; PANICKSSERY24).
3. Match both edits in loudness before any human or AI preference test: integrated loudness within 0.5 LU (house; FFMPEG_local).
4. Evidence first: score each criterion 1 to 5 with MM:SS timestamps before the verdict. Criteria: hook, pacing, caption legibility, framing and composition, grade and skin, graphics restraint, trust and credibility (VSL), audio balance (audio-capable judges only). An output that gives the verdict first is rejected (sourced; WANG23).
5. Run both orders (A then B, B then A) with 3 samples per order and take the majority. A win counts only if it holds in both orders; otherwise it is a tie that goes to the owner (sourced for the orders, house for 3 samples; WANG23; SHI24).
6. Close calls are the least reliable, because position bias grows as the quality gap shrinks. Report the consistency rate with every result; many ties mean the versions are not meaningfully different (sourced; SHI24).
7. Calibrate against the owner's own blind picks before trusting the judge, and rank several versions with Bradley-Terry: at least 20 owner-labelled pairs (house), trust the judge at about 80% agreement (sourced; ZHENG23; CHOIX).
8. An optional second judge that hears the audio, owner-only and opt-in by API key: Gemini, 1 fps by default, 258 tokens per frame plus 32 audio tokens per second (sourced; GEMINI_VIDEO).

**Decision rule.** Same timeline: the metrics decide the technical question. Different edits: the owner's blind pick, helped by a calibrated judge. For a VSL, a conversion A/B on the landing page beats both (house; DA-1 to DA-4).

Excluded: DOVER (non-commercial licence) and APCA (patent pending, all rights reserved).

## 9. Shipping on every desktop

**XP-01** (BLOCK). Find ffmpeg in this order: the CLOSER_FFMPEG environment variable, then ffmpeg on PATH if it passes the filter probe, then imageio_ffmpeg.get_ffmpeg_exe(), then an error with a fix line for that OS. imageio-ffmpeg ships no ffprobe, so use PyAV or parse `ffmpeg -i` instead. imageio-ffmpeg 0.7.0 carries ffmpeg 7.0.2 on linux-x86_64 and 7.1 on macOS arm64 and win64, each with libass, freetype, libvmaf, x264 and zimg and no fontconfig, read from configure strings; the binaries were not executed (sourced; IMAGEIO_FFMPEG).

**XP-02** (BLOCK). A `doctor` command parses `ffmpeg -hide_banner -filters`. A missing required filter is an error, a missing optional one a warning. Required: ass, subtitles, zscale, tonemap, lut3d, ebur128, loudnorm, alimiter, sidechaincompress, acrossfade, adynamicequalizer, signalstats, siti, scdet. Optional: libvmaf; rubberband (GPL, owner-only) (BREW_FFMPEG; FFMPEG_local).

**XP-03** ffmpeg by OS:

| OS | Use | Avoid | Sources |
|---|---|---|---|
| macOS arm64 | today `brew install ffmpeg@7` (7.1.5, keg-only, with libass and zimg; put `$(brew --prefix ffmpeg@7)/bin` first on PATH), because `ffmpeg-full` is 9.0.2 and the engine still needs `-filter_complex_script` (known defects below); after that fix, `brew install ffmpeg-full` (keg-only; call `$(brew --prefix ffmpeg-full)/bin/ffmpeg`), or a Martin Riedl notarized arm64 build checked by SHA256 | Homebrew core `ffmpeg` 9.0.2: no libass, freetype, fontconfig, harfbuzz or zimg, so caption burn and HDR tone-mapping fail; evermeet (Intel only, runs under Rosetta) | BREW_FFMPEG; BREW_FULL; BREW_AT7; RIEDL; EVERMEET |
| macOS Intel | brew ffmpeg@7 until the known defect below is fixed, then brew ffmpeg-full, or evermeet with its GPG signature (key 0x476C4B611A660874) | | BREW_AT7; EVERMEET |
| Windows x64 | today the gyan.dev previous release, essentials 8.1.2 zip (it has libass and zimg), checked against its .sha256 and extracted under LOCALAPPDATA/closer-studio/ffmpeg; after the known defect below is fixed, the current release (9.0.2); BtbN as the LGPL option. install.ps1 runs `winget install --id Gyan.FFmpeg`, which follows gyan.dev's current release | | GYAN; BTBN |
| Linux | apt ffmpeg (6.1.1 on Ubuntu 24.04: has libass, no libvmaf), BtbN static, or the imageio-ffmpeg fallback | johnvansickle (stale 7.0.2 from 2024-06-29, MD5 only) | BTBN; JVS |

**XP-04** (BLOCK). Check the checksum first (Get-FileHash, `shasum -a 256` or `sha256sum`), stop on a mismatch, then confirm the `ffmpeg -version` string (GYAN; RIEDL; EVERMEET).

**XP-05.** Use uv with a lockfile and uv-managed Python, so Windows needs no system Python. Pin the versioned installer URLs. macOS and Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`; Windows: `powershell -ExecutionPolicy ByPass -c 'irm https://astral.sh/uv/install.ps1 | iex'`; versioned URLs under astral.sh/uv/0.13.6/ (sourced; UV).

**XP-06.** Ship install.sh and install.ps1. install.ps1 runs with ExecutionPolicy ByPass, which applies to that process only; Windows clients with no policy set default to Restricted. For zip downloads the README says to run `Get-ChildItem -Recurse | Unblock-File` (sourced; PS_EXEC).

**XP-07.** `playwright install chromium --only-shell`, adding `--with-deps` on Linux. Warn up front about unsupported OS versions: macOS 14+, Windows 11+ or Server 2019+ or WSL, Ubuntu 22.04, 24.04 or 26.04, Debian 12-13. PLAYWRIGHT_BROWSERS_PATH may move the cache (sourced; PLAYWRIGHT_BROWSERS).

**XP-08.** Bundle the OFL fonts in the kit. libass gets fontsdir=<kit>/fonts and HTML scenes use local woff2 @font-face, so nothing depends on fontconfig or on fonts installed in the OS. Target: a golden caption frame matches at SSIM 0.98 or more on all three OSes (house; IMAGEIO_FFMPEG; FFMPEG_local).

**XP-09.** Run ffmpeg with the job folder as its working directory and pass relative forward-slash names inside filter strings. When an absolute path is unavoidable, escape colons with a backslash and quote the value. Put graphs over 2,000 characters in a file: `-/filter_complex file` on FFmpeg 7.0 and later (the 7.0 Changelog adds `-/opt <path>`), `-filter_complex_script` on 6.x. `-filter_complex_script` is deprecated in 7.x and 8.x and removed in 9.0, so pick the flag from `ffmpeg -version` (FFMPEG_SRC). Use argument lists, never shell=True, and pass encoding='utf-8', errors='replace' on every text subprocess: UTF-8 mode is the default only from Python 3.15, and before that Windows uses the ANSI code page (sourced; PYWIN; FFMPEG_OPTFILE).

**XP-10.** install.ps1 reads LongPathsEnabled. If it is 0, default the workspace to C:/CloserStudio and warn when a job path passes 200 characters; MAX_PATH is 260 (sourced; PYWIN).

**XP-11.** .gitattributes: `* text=auto`, `*.sh text eol=lf`, `*.command text eol=lf`, `*.ps1 text eol=crlf`, `*.bat text eol=crlf`; media and fonts binary; then `git add --renormalize .` (GITATTR).

**XP-12.** CI matrix: ubuntu-24.04, macos-15 (arm64), windows-2025, with ubuntu-24.04-arm and macos-15-intel optional; fail-fast false; every action pinned by SHA (setup-uv v10.3.3 = 68559e99cc807c1eb7e9238fd43a15bba460eec2). Install ffmpeg from the same sources users get, not from FedericoCarboni/setup-ffmpeg. Tests: the resolver returns an ass-capable binary on each OS; a caption burn with a path containing a space and an apostrophe; the MO-10 double render is byte-identical; a 200-segment graph on Windows; install.ps1 on a clean runner, then doctor exits 0; a licence scan; no ffmpeg binaries tracked in git (GH_RUNNERS; SETUPUV; SETUPFFMPEG).

**XP-13.** faster-whisper defaults to device=cpu, compute_type=int8 (there is no Apple GPU path); NVIDIA needs CUDA 12 and cuDNN 9. Decode to 16 kHz mono with ffmpeg first, and prompt with names and fillers so restarts survive. Use whisperX (BSD-2) when boundary drift clips words. The small model ran in 1m42s at int8 against 2m37s at fp32 on an i7-12700K, and the built-in VAD removes only silences over 2 s by default (sourced; FASTERWHISPER; WHISPERX; VIDEOUSE).

### Known kit defects (status read from the code on 2026-11-02)

| Where | Issue | Status | Severity |
|---|---|---|---|
| install.sh | `brew install ffmpeg` (line 25) gets the core formula, which has no libass, so caption burn fails on a fresh Mac; switch to ffmpeg@7 now and ffmpeg-full once the row below is fixed | open | BLOCK |
| tools/studio/render.py line 125, tools/studio/longform.py line 408 | every long-form piece and the final encode pass `-filter_complex_script`, which FFmpeg 9.0 removed (FFMPEG_SRC). Homebrew (both formulas) and gyan.dev's current release are 9.0.2, so a 16:9 render fails on a fresh Mac or Windows install. Fix: `-/filter_complex` on 7.0 and later. Until then use an 8.1 or older build (XP-03; the Windows steps follow this table) | open | BLOCK |
| filter paths | captions.py once wrote `ass={path}:fontsdir={FONTS}` unescaped | fixed for drive colons: paths now go through `common.fpath`, which turns backslashes to slashes and escapes colons; apostrophes are not escaped yet | BLOCK |
| tools/studio/common.py | `sh()` runs subprocess with text=True and no encoding, which decodes as cp1252 on Windows before Python 3.15 | open | FIX |
| repo root | no Windows installer | install.ps1 added 2026-11-02; it says it has not yet been run on a Windows machine | BLOCK until run |
| tools/studio/grade.py | the double unsharp pass gives a crunchy, AI-looking face (TX-04) | open | FIX |

Windows, until the `-filter_complex_script` row is fixed. In PowerShell, remove the 9.0.2 that install.ps1 put in and add the 8.1.2 essentials build to your user PATH with the lines below. Then open a new PowerShell: `ffmpeg -version` should say 8.1.2 (GYAN).

```powershell
winget uninstall --id Gyan.FFmpeg
$Z = Join-Path $env:LOCALAPPDATA "closer-studio\ffmpeg"; New-Item -ItemType Directory -Force -Path $Z | Out-Null
Invoke-WebRequest "https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-8.1.2-essentials_build.zip" -OutFile "$Z\ffmpeg.zip"
(Get-FileHash "$Z\ffmpeg.zip" -Algorithm SHA256).Hash   # must match ffmpeg-8.1.2-essentials_build.zip.sha256 on the same page
Expand-Archive "$Z\ffmpeg.zip" -DestinationPath $Z -Force
$Bin = (Get-ChildItem $Z -Directory -Filter "ffmpeg-*")[0].FullName + "\bin"
[Environment]::SetEnvironmentVariable("Path", "$Bin;" + [Environment]::GetEnvironmentVariable("Path", "User"), "User")
```

Not yet run on a Windows machine.

## 10. Licence policy

- **Bundle:** MIT, Apache-2.0, BSD-2/3, BSD-2-Clause-Patent, ISC and Unlicense code; OFL or Unlicense fonts; CC0 audio (Kenney, OpenGameArt CC0 after re-checking each page, Freesound CC0).
- **Bundle with credits:** CC BY assets, with a generated credits file.
- **Call from outside only:** GPL ffmpeg builds downloaded at install time; video-compare (GPL-2.0); mpv; the Rubber Band CLI (owner-only); RVM (optional, user-installed).
- **Never bundle:** Pixabay, Sonniss, the YouTube Audio Library (treat it as YouTube-only), Mixkit (unverified), BBC sound effects (reportedly non-commercial, unverified); third-party LUTs (Melara: no licence; RawTherapee: CC BY-SA, unverified; AgX: unverified); SF Pro; easings.net code; the logiclrd gist code (no licence); any proprietary agent's text, scripts, templates or sound files.
- **Banned dependencies:** DOVER (non-commercial), madmom models (CC BY-NC-SA), Essentia (AGPL plus non-commercial models), pytsmod, pedalboard, aubio and matchering (GPL), APCA (patent pending), Remotion as core (a company licence above 3 employees), allin1 as core (it pulls in madmom, and its NATTEN dependency is hard to build on Windows).
- **At render time:** every audio cue's licence must be on the allow-list. CC BY-NC (including Free Music Archive NC tracks) is rejected for business videos.
- Sources: KENNEY; FREESOUND; PIXABAY; SONNISS; YTAL; FMA; MIXKIT_BBC; LUTS; MADMOM; ESSENTIA; GPL_AUDIO; APCA; REMOTION; DOVER; ALLIN1.

## 11. Conflicts and how they were settled

| Topic | Options | Settled | Basis |
|---|---|---|---|
| Music under the voice | WCAG at least 20 dB; video-use ducks 12-15 dB against music alone; music-led brand 15-20; finance 20-26; measured Gadzhi promo about 10 LU | measure voice over music per section; the engine's measured presets win (AU-04) | WCAG147; OVERSEER; VIDEOUSE; docs/AUDIO_SPEC.md |
| Splice crossfade length | 10 ms (audiojs); 20-50 ms (AFP); 30 ms (video-use); 2 frames = 67 ms (1of10) | range 10-67 ms; the engine uses 10 ms equal-power | VO-09 |
| Reel sentence gaps | 150-250 ms against 167-333 ms (5-10 frames) | 170-300 ms plus tagged beats of 350-500 ms | R_EDITORS; VIZARD_PAUSE |
| Caption case | UPPER (Hormozi) against sentence case (Kapwing, Joyspace) | UPPER in reels only | TY-07 |
| 9:16 bottom clearance | about 22% (organic Reels, platforms.py), 25% (Opus, Reap, TikTok), 35% (Meta ads) | platform presets; the universal default takes the strictest Instagram and TikTok edges (bottom 25%) | section 2 |
| Caption chunk size | 1 to 6 words (kit grammar); 5-7 words (Opus); 42 chars x 2 lines (Netflix) | by caption mode per profile; VSL uses phrase mode | CP-01; DA-3 |
| Graphic cadence | a visible change every 3 to 8 s in reels (kit grammar) against about 2 graphics per minute in a Gadzhi body | per profile; VSL 2-4 per minute | MO-07; DA-1 |
| SFX density | 0.45 per second (video-use promo) against 4-6 per minute (business) against no transition SFX (Hormozi) | effects attach to graphic moments, not cuts; caps per dialect; 0.45 per second only in montage | AU-12 |
| Punch-in scale | 110-120% (1of10) against the house 112% cap | the cap applies to the effective upscale (FR-03), so 4K sources may punch further | FR-03 |
| Digital-silence thresholds | -90 dBFS for 10 ms; -80 dBFS for 100 ms; above -70 dBFS in pauses | -90 / 10 ms BLOCK; -80 / 100 ms WARN; pause floor -75 to -60 | VO-13 |
| Music EQ carve | -2 to -4 dB at 3 kHz against -3 to -6 dB at 800-3000 Hz | 3 kHz by default, the wider band only for mid-heavy beds; the engine uses a 300 Hz-4 kHz pocket | AU-06 |
| Caption snap to a cut | 0.5 s (Netflix) against 12 frames (unverified) | 0.5 s | NFX_TIME |
| SFX sync tolerance | 40 ms or less against [-1, +2] frames | [-1, +2] frames: asymmetric, because early sound is noticed sooner | ITU1359 |
| Vignette and text | vignette over the stacked layers against the plate only | vignette on the plate, grain over everything (TX-01); the engine grains the plate too, before graphics | TX-01 |
| Hook pause caps against VSL beats | no pause over 300 or 400 ms in the first 60 s against VSL beats of 700-1200 ms | caps not applied to VSLs | DA-2 |
| Filler removal | about 75% (editors) against 100% | conversational 70-85%; scripted VSL 90-100%; reel 85-100% | section 1 |
| Face exposure | the finish lifts the face through a tracked soft window (at most 0.30 EV toward 0.52 luma) against GR-05's whole-frame curves only | open: the engine's lift is capped and a well-exposed face gets none; the owner decides | GR-05; KIT_CODE |
| Slow push | every piece pushes from 1.02 to 1.045 against AS-05's 40% of shots | open | AS-05; KIT_CODE |
| VSL punch clock | vsl_hero punches every 2.6 s, zooms up to 1.22, against the VSL profile's 4-8 s median shot and 1.10-1.12 punch | open: the registry entry is busier than DA-1 | formats.json; DA-1 |
| Speed | the research speed table allows up to 1.10 against the kit's 1.05x cap | the kit's cap holds; the engine never time-stretches | VO-03; KIT_EG |

## 12. Devil's advocate

These five rules are the most likely to be wrong, or to backfire, on a sales VSL sold to 55 to 72 year-old, middle-income retirement prospects. Each stays in the rulebook, the vsl profile already uses the safer setting, and each comes with the test that would overturn it.

**DA-1. More motion and more effects keep attention, so the edit converts better.** Rules: MO-07 cadence, AU-12 densities, VO-25 front-loading.

- Why it may backfire: these numbers come from short-form social and entertainment (MrBeast's internal guide and creator breakdowns), built to hold cold, young scrollers. A VSL viewer has already clicked and is weighing a money decision. Persuasion depends on the viewer processing the arguments (GUYER24), and effects compete for the same attention, so a strong offer can lose. Shake and flash read as hype on a financial product, which costs credibility and invites compliance scrutiny.
- Evidence quality: no source measured VSL conversion against effect density.
- VSL setting: 2-4 graphic moments per minute, on numbers, proof and the CTA only; no shake or flash; punch-ins only to hide jump cuts; up to 4 soft effects per minute.
- Test: an A/B on the landing page of the same VSL at equal length, restrained against reel energy. Read play-through at 25, 50 and 75% after at least 500 plays per side (house), and read booking rate only with a significance test.
- Kill if: the energetic cut wins booking rate significantly. Then relax the vsl caps toward yt.

**DA-2. Trimming dead air to creator density raises persuasion.** Rules: VO-02 bands, VO-04 trim first, VO-06 pause targets, VO-25 first-minute caps, applied to the owner.

- Why it may backfire: the owner's raw takes already run 199-226 wpm (OWNER_FM), 10-25% above the 181 wpm persuasion inflection (KIM19). Take 2 at 226 wpm is above GUYER24's fastest condition (+25% over 174 = 218 wpm), where strong arguments persuaded less. Trimming can only push the rate higher. The benchmarks are Hormozi and MrBeast, whose audiences are younger; our sources do not cover listener age (unverified), but the buyer is 59 to 72. Speed cannot safely go down either, because stretching below 1.00 adds artefacts (ROBERTS20).
- Evidence quality: the rate findings are real but come mostly from younger lab samples; the age interaction is unverified.
- VSL setting: sentence gaps of 400-600 ms, never trimmed below 400; beats of 700-1200 ms before price and claims; no first-minute caps. Over 200 wpm, flag "speak slower on the next take" rather than stretch.
- Test: an A/B on the same take, tight (sentence gaps 250-350 ms) against breathing (450-600 ms), on retention and bookings.
- Kill if: the tight cut wins on bookings.

**DA-3. Punchy 1 to 3 word captions and floors tied to phone type sizes are readable.** Rules: CP-01 chunking, TY-02 floors, TY-07 case.

- Why it may backfire: flashing short caps chunks is a short-form convention. The size floors come from Apple's minimums, which assume average young eyesight. Many viewers over 60 have presbyopia, and feed autoplay starts muted, so captions carry the opening. Fast chunk swaps force more re-fixations, and all caps are called harder to read (KAPWING, low confidence). Netflix's phrase rules were designed for comprehension, not punch.
- Evidence quality: no source tested caption chunking or size on older viewers. Every size number is a floor, not an optimum.
- VSL setting: phrase mode, 4-7 words, up to 42 characters, 1-2 lines, sentence case; at least 64 px on 9:16 and 52 px on 16:9; WCAG 4.5:1 as the minimum, aiming higher.
- Test: an A/B with muted autoplay on 3 s and 30 s hold and CTA clicks.
- Kill if: punchy chunks win on muted hold and on clicks.

**DA-4. A cinematic finish reads as premium.** Rules: TX-02 grain, TX-05 halation, TX-06 vignette, FR-05 letterbox, GR-02's teal-orange allowance.

- Why it may backfire: grain is costly to encode, and streaming encoders strip or smear it (NETFLIX_FGS). Landing-page players and Facebook re-encode at low bitrates, so grain turns to mush that reads as a dirty camera. A 2.39:1 letterbox inside 16:9 blacks out 25.6% of the frame (276 of 1080 lines) and shrinks the face on phones. "Cinematic" signals ad production at the moment a VSL is selling trust in a person.
- Evidence quality: the finishing numbers come from cinema-style colour work; no source covers VSL conversion.
- VSL setting: grain alls 0-3, kept only if it survives the TX-03 test through the real host; halation off; vignette -0.3 to -0.5 stops (on long-form the engine stacks grade.py POST's -0.36 and the vsl finish's -0.18, about -0.54); no letterbox; a natural grade.
- Test: upload to the real host and measure the grain again after download (TX-03); then an A/B, clean against finished.
- Kill if: the finished cut wins on bookings and survives the encode.

**DA-5. Skin should sit near 123 degrees on the vectorscope and at 65-75 IRE.** Rules: GR-04 skin hue, GR-05 skin exposure.

- Why it may be wrong: the hue target rests on two ColorChecker patches and a rule of thumb. The I axis was never designed as average skin, and real skin spreads about 15 degrees either side. The classic 123 degrees is an NTSC U/V figure that lands at 132-134 degrees in Cb/Cr, a 10 degree error larger than our warn band. Mixed light and make-up move the number, and so does deeper skin. The exposure bands come from low-confidence forum posts that themselves warn skin varies too much for one number. An auto-correct loop built on this would push the owner's face toward a "corrected" but unnatural hue, which is exactly the AI look he dislikes.
- Evidence quality: low to medium.
- VSL setting: WARN only, never auto-correct. After the owner approves 3-5 frames, measure deviation from his own reference (8 degrees either side) instead of from 123.
- Test: run GR-04 and GR-05 on frames from VSLs the owner already approved.
- Kill if: approved frames get flagged more than 10% of the time. Then the absolute targets are wrong; switch to reference-only.

**Also watch:**

- AS-01 and AS-02, the anti-metronome statistics, come from feature-film shot lengths. Talking-head cuts follow the speech, so forcing a spread could reshuffle good cuts; the rule is limited to engine-placed events.
- AS-07 keeps about a quarter of the fillers, but fillers cost credibility in a scripted VSL, so the vsl profile removes 90-100%.
- AU-04, the music gap: on a VSL the best music may be none.
- VO-11, the 40% split-edit quota, is a house number with no source and can become a forced pattern.
- VO-03, the speed table: its band edges are house values interpolated from studies that used other speakers and pitch-preserving compression.
- The 55-72 audience is the client-facing VSL. The kit's vsl_hero homepage video speaks to agents, so its numbers may sit between the vsl and yt columns.

## 13. Verify next

- Measure three or more real clips each of Hormozi, Gadzhi and Nelk with the same measures before shipping their presets (Nelk has no data yet, and the creator SFX numbers are vendor inferences).
- Calibrate GR-04 and GR-05 on frames the owner approved.
- Run the DA-1 to DA-4 A/B tests on the live VSL landing page.
- Check whether age changes the speech-rate optimum; no source covers it.
- Get Meta's official Reels and Stories safe-zone page; TikTok publishes no official numbers.
- The BBC subtitle guideline values (the fetch was blocked).
- The Mixkit and BBC SFX licence texts; Pixabay Content ID per track.
- Actually run the imageio-ffmpeg binaries on all three OSes (only their configure strings were read).
- Whether winget's Gyan.FFmpeg package is 9.0.2 today (gyan.dev's current release is; the winget manifest was not read).
- static-ffmpeg build flags; mpv lavfi-complex syntax; licence files for the homebrew-ffmpeg tap, Martin Riedl builds, uv, wavesurfer.js and img-comparison-slider.
- House thresholds that need tuning on real renders: the 60% grain retention after encode, PLR 9 dB, the 100-200 ms pre-duck, the 1.5 s music rise, the 0.3-1.0 s silence drop, the 6 dB de-ess cap.
- The exact EBU R37 values (the page did not show them).
- The Hormozi caption colour (#FDE047 or #EAC70C) and font (sources disagree).
- The Instrument Serif and DeepFilterNet licence files.

## Lessons from the blind panels

Rules added after a blind panel judged a full re-edit against the shipped cut (2026-11-02; the panel, its votes and the
claims that did not survive checking are in `docs/panels/2026-11-02_vsl_full_reset_vs_previous.md`, source PANEL_V9).

**BP-01** (BLOCK, vsl). The offer lands by 15 s: what the viewer gets and what it costs are said (and, muted, shown)
before the 15th second. The re-edit that put it at 36-41 s lost to the cut that put it at 11 s, on the three lenses
that answered the same in both orders.
- check: the first word of the offer sentence on the output clock (transcript.txt) is under 15.0 s.
- source: PANEL_V9 (direct-response editor and target viewer, both orders).

**BP-02** (FIX, vsl). No local moves on a talking head: no sky pull-down, no tracked face lift, no grain. A light
whole-frame vignette only. The measured local moves read as a halo and a posterized sky at phone size.
- engine: finish.py `FINISH_PROFILES["vsl"]` has `sky` and `face` off and grain 0 since this panel.
- source: PANEL_V9 (6 reviews).

**BP-03** (BLOCK). A sourced number lands already final: no count-up, roll or ticker on it, since every intermediate
frame is an unsourced number on screen. Scale or blur it in instead.
- source: PANEL_V9 (12 of 12 reviews).

**BP-04** (FIX). No fine print that hedges a verified claim. A qualifier names a real limit (who, when, results vary),
it never takes the claim back.
- source: PANEL_V9 (9 reviews read "Real splits are agreed up front" under a verified 50/50 as "the 50/50 is not real").

**BP-05** (FIX). No empty container on any frame: a card's box and its text enter together and leave together.
- check: no sampled frame shows a card box without its first line.
- source: PANEL_V9 (5 reviews).

**BP-06** (FIX). Overlay card type at 1080: body lines 44 px or more, labels 30 px or more, fine print 34 px or more;
judge every card at 360 px wide. Hold the 100 % framing while a card sits beside the head.
- source: PANEL_V9 (6 reviews measured body type near 20 px at 1920 wide, about 6-8 px on a phone); house.

**BP-07** (FIX). The bed never fades under the ask and never leaves the end card silent: it holds under the end card and
fades on the last frame, floored above digital zero. Effects are one-shots that stop near their hit (AUDIO_SPEC; review
gates "the bed holds under the ask", "no digital silence" and "no sound effect outstays its frame"). A second panel on
the same night rejected a button ending that left 2.8 s of near silence under the end card (11 of 12 reviews).
- source: PANEL_V9 (mixer, both orders); kit_sound measurements in `skills/video/sound-director/AUDIT.md`.

**BP-08** (FIX, process). A reviewer's measurement is a claim: reproduce it on the source before acting. A reviewer's
timecode is a pointer: take every cut point from the word map. Count only lenses whose preference survives the A/B swap.
- source: PANEL_V9 ("Claims that did not survive checking").

**BP-09** (FIX, vsl). An overlay card beside the speaker never replaces the captions: captions run under every overlay,
and only a full-screen card that shows the same words takes them off. Card lines that mirror speech use the speech word
for word (CP-04), with one spelling per term in cards and captions (captions.py `DISPLAY`).
- source: PANEL_V9 rounds 2 and 3 (the target-viewer lens chose the cut with readable full-screen cards in both orders
  until captions ran under the overlays).

**BP-10** (FIX, multi-take). Beat edges sit inside the measured silences around each line (frame_map silences), so
the pauses a person leaves can exist at take changes; then hold them (layers `breath.after`). Tight beat edges made
the offer run at about 270 words a minute with 0.03-0.25 s between sentences.
- source: PANEL_V9 round 3 (devil's advocate measurements on the word map).

**BP-11** (FIX, vsl). A full-screen slam over the speaker carries one beat, about 2 s: the speech's own words in at
most two rows, then the face and the captions come back for the rest of the line. A 7.4 s deal slam (four rows and a
pill) hid the founder through the payout line, and 10 of 12 reviews asked to split it. Keep the speaker hidden or
dimmed behind cards to about a third of the runtime or less (that cut: 34%).
- source: PANEL_V9 round 4 (v13 against v12).

**BP-12** (FIX, sound). Every beat's audio fades in and out at a take change (assemble.py `JOIN_FADE_S`, 15 ms
equal power), and the review checks each join (sound.py `join_clicks`). A cut clicked at 51.5 s: the selects spliced
two takes mid-wave, the 10 ms voice crossfade straddled that splice, and the whole-file click test passed it.
- source: PANEL_V9 round 4 (sound lens, both orders; reproduced as a 0.33 full-scale one-sample step in voice.wav).

**BP-13** (FIX, process). The devil's advocate reads the merged fix list against this rulebook before anything is
built. In round 4 it struck fixes that would have broken BP-04, BP-09, CP-04 or AU-07 (a disclaimer under the payout
line, captions hidden under overlays, paraphrased card copy, hits at the voice's level). A 2 to 1 split of the lenses
that survive the A/B swap is a lean, not a win: the owner's blind pick settles it.
- source: PANEL_V9 round 4.

**BP-14** (FIX, process). Read a panel through its order-stable lenses and check every "missing" claim against the
render's own files before building. With three samples per order, the cut shown second won 69% of 36 samples and
three of six lenses followed position. Every claim that a caption was missing came from the 1 fps sheets and was false
in captions.ass. When a persona lens (the muted target viewer) prefers the older cut in every round, stop iterating
against it and hand the owner a split test, with a variant built to test its stated reason.
- source: PANEL_V9 round 5.

## 14. Sources

Each key used above, with where it points and the date read. Kit files are this repository's own.

| Key | Source |
|---|---|
| ACX | https://www.production-expert.com/production-expert-1/want-to-make-an-audiobook-for-audible; unverified |
| AFP | https://audioforgepro.com/blog/silence-removal-guide; 2026-04-07 |
| ALLIN1 | https://github.com/mir-aidj/all-in-one; 1.1.0, 2023-10-10; MIT repo, depends on madmom, flag |
| ANTARES | https://www.antarestech.com/blog/what-is-a-de-esser-how-it-works-and-how-to-use-one-on-vocals; unverified |
| APCA | https://github.com/Myndex/apca-w3; 2019-2023; all rights reserved, flag |
| APPLE_SPRING | https://developer.apple.com/documentation/swiftui/spring ; https://wwdcnotes.com/documentation/wwdc23-10158-animate-with-springs/; 2023 |
| ATEMPO | https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/af_atempo.c; 2026-11-02; LGPL |
| AUDIOJS | https://github.com/audiojs/audio; npm 2.14.0; MIT |
| AUDIOTSM | https://github.com/Muges/audiotsm; 2017-09-21; MIT |
| AUTODIRECTOR | https://arxiv.org/abs/2610.28346; 2026-10-20 |
| AUTOEDITOR | https://auto-editor.com/ref/options; v31.6.1, 2026-09-07; Unlicense (check paid features) |
| BACK | https://easings.net/#easeOutBack ; flutter curves.dart; 2026-11-02; values only |
| BEATTHIS | https://github.com/CPJKU/beat_this; v1.1.0, 2026-04-14; MIT |
| BREW_FFMPEG | https://formulae.brew.sh/formula/ffmpeg; 9.0.2, 2026-11-02; GPL-3.0+, no libass |
| BREW_FULL | https://formulae.brew.sh/api/formula/ffmpeg-full.json; 9.0.2, 2026-11-02; keg-only |
| BREW_AT7 | https://formulae.brew.sh/api/formula/ffmpeg@7.json; 7.1.5, keg-only, depends on libass, freetype, fontconfig and zimg; read 2026-11-02 |
| BSCRIPT | https://arxiv.org/abs/1902.11216; 2019-02-28 |
| BTBN | https://github.com/BtbN/FFmpeg-Builds; daily; GPL/LGPL variants |
| CAPTIONS_APP | https://www.captions.ai/; 2026-11-02 |
| CARBON | https://carbondesignsystem.com/elements/motion/overview/; 2026-08-12 |
| CASSETTE | https://arxiv.org/abs/2610.37690; 2026-10-19 |
| CHOIX | https://github.com/lucasmaystre/choix; 2026-11-02; MIT |
| CHOPPITY_AH | https://www.choppity.com/tools/recreate-video-editing-style/alex-hormozi/; unverified 2026 |
| CHOPPITY_LH | https://www.choppity.com/tools/recreate-video-editing-style/leila-hormozi/; unverified 2026 |
| CK_grain | https://blog.frame.io/2023/08/14/how-a-pro-colorist-uses-film-grain/; 2023-08-14 |
| CLAUDE_VISION | https://platform.claude.com/docs/en/build-with-claude/vision; 2026-11-02 |
| CUTTING10 | https://www.psychologicalscience.org/observer/the-science-of-hollywood-blockbusters-2; 2010-04-01 |
| DEHANCER | https://dehancer.com/learn/article/halation; undated |
| DESPERATI17 | https://www.nature.com/articles/s41598-017-15619-8; 2017 |
| DOVER | https://github.com/VQAssessment/DOVER; 2023-11-22; non-commercial, flag |
| DUCK_TUT | https://tryuncle.com/learn/davinci-resolve/how-to-duck-background-music-under-dialogue-in-davinci-resolve ; https://www.capcut.com/create/audio-ducking-for-clear-dialogue-in-video; July 2026 / unverified; low |
| EBU_R95 | https://tech.ebu.ch/publications/r095 ; ITU-R BT.1848-1; 2015 |
| ELEVEN | https://elevenlabs.io/docs/best-practices/prompting; undated |
| EPIDEMIC | https://www.epidemicsound.com/blog/how-to-mix-music-and-vocals/; 2023-05-25 |
| EQ_CARVE | https://www.dvinfo.net/forum/archive/index.php/t-73903.html ; https://nathanjameslewis.blogs.lincoln.ac.uk/2014/03/21/the-magical-foley-curve; 2006-2014 |
| ESSENTIA | https://essentia.upf.edu/licensing_information.html; 2026-05-19; AGPL + NC models, flag |
| EVERMEET | https://evermeet.cx/ffmpeg/; 9.0.2, 2026-09-18; GPL, Intel only |
| EXPRESSEDIT | https://arxiv.org/abs/2403.17693; 2024-03-26 |
| FASTERWHISPER | https://github.com/SYSTRAN/faster-whisper; 2026-10-31; MIT |
| FFMPEG_OPTFILE | https://ffmpeg.org/ffmpeg.html; 2026-11-02; the current page documents `-/filter:v filter.script` and no longer lists `-filter_complex_script` |
| FFMPEG_SRC | https://raw.githubusercontent.com/FFmpeg/FFmpeg/ branches release/7.0, release/7.1, release/8.0, release/8.1 and release/9.0 (`fftools/ffmpeg_opt.c`, `fftools/ffmpeg.h`) and the master Changelog (version 7.0: "ffmpeg CLI options may now be used as -/opt <path>"); read 2026-11-02: `filter_complex_script` present and deprecated through 8.1, absent in 9.0; LGPL/GPL |
| FFMPEG_local | https://ffmpeg.org/ffmpeg-filters.html + local ffmpeg 6.1.1 runs; 2026-11-02; LGPL/GPL build |
| FLASHBOARDS | https://flashboards.yaroflasher.com/learn/editing/j-cut/; unverified |
| FMA | https://freemusicarchive.org/License_Guide; 2026-11-02; mixed CC |
| FONTS | https://github.com/tiktok/TikTokSans ; https://github.com/vercel/geist-font ; https://github.com/rsms/inter ; https://fonts.google.com/specimen/Instrument+Serif; 2024-2025; OFL |
| FQM | https://github.com/slhck/ffmpeg-quality-metrics; v3.11.4; MIT, needs FFmpeg 7.1+ |
| FREESOUND | https://freesound.org/help/faq/; 2026-11-02; per-sound CC0/BY/BY-NC |
| GEMINI_VIDEO | https://ai.google.dev/gemini-api/docs/video-understanding; 2026-11-02 |
| GETIMG | https://getimg.ai/ai-whoosh-sound-effect-generator; unverified; low |
| GH_RUNNERS | https://docs.github.com/en/actions/reference/runners/github-hosted-runners; 2026-11-02 |
| GIST_grain | https://gist.github.com/logiclrd/287140934c12bed1fd4be75e8624c118; 2019-04-19; no licence, ideas only |
| GITATTR | https://git-scm.com/docs/gitattributes; 2026-11-02 |
| GPL_AUDIO | https://pypi.org/project/pedalboard/ ; https://pypi.org/project/aubio/ ; https://pypi.org/project/matchering/; 2019-2026; GPL, flag |
| GRAVY | https://www.gravyforthebrain.com/commercial-voiceover-when-should-you-debreath/; unverified; low |
| GUYER24 | https://link.springer.com/article/10.1007/s10919-024-00477-6; 2024-12-03 |
| GYAN | https://www.gyan.dev/ffmpeg/builds/; current release 9.0.2 (2026-09-19), previous release 8.1.2 with libass and libzimg in the essentials build; read 2026-11-02; GPLv3, flag |
| HABLE | http://filmicworlds.com/blog/filmic-tonemapping-operators/; 2010-05-05 |
| HDR_DEVTO | https://dev.to/masonwritescode/ffmpeg-hdr-to-sdr-tone-mapping-that-doesnt-look-washed-out-2026-24ie; 2026 |
| HIG_MAT | https://developer.apple.com/design/human-interface-guidelines/materials; 2025-09-09 |
| HIG_TYPE | https://developer.apple.com/design/human-interface-guidelines/typography; 2026-11-02 |
| HYPERFRAMES | https://github.com/heygen-com/hyperframes; 2026-11-01; Apache-2.0 |
| IMAGEIO_FFMPEG | https://pypi.org/project/imageio-ffmpeg/; 0.7.0, 2026-10-28; wrapper BSD-2; binaries GPL, flag |
| INTER | https://d.rsms.me/inter-website/v3/dynmetrics/; Inter v3; OFL |
| IPHONE | https://www.techradar.com/phones/iphone/iphone-16-pro-cameras; 2024-09 |
| ITU1359 | https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-1-199811-I!!MSW-E.doc; 1998 |
| IZO_BREATH | https://downloads.izotope.com/docs/rx6/18-breath-control/index.html; RX6 |
| IZO_DEESS | https://www.izotope.com/community/blog/the-dos-and-donts-of-de-essing; unverified |
| JOYSPACE | https://joyspace.ai/hormozi-editing-style-2026-analysis; 2025-12-10; low |
| JUMPCUT_SYNTH | https://arxiv.org/abs/2401.04718; 2024-01-09; anti-reference |
| JVS | https://johnvansickle.com/ffmpeg/; 7.0.2 / 2024-06-29; stale |
| KAPWING | https://www.kapwing.com/resources/social-media-captions-styles-a-complete-guide/; 2025-06-09 |
| KAPWING_AI | https://www.kapwing.com/ai; 2026-11-02 |
| KENNEY | https://kenney.nl/assets/interface-sounds; 2026-11-02; CC0 |
| KIM19 | https://www.researchgate.net/publication/330543418_Meta-Analysis_of_the_Curvilinear_Relationship_between_Rate_of_Delivery_and_Message_Persuasiveness; 2019-01-22 |
| KIT_CODE | closer-studio tools/studio/*.py and formats.json (edit, cut, longform, layers, render, finish, placement, sound, voice, platforms, review, compare); read 2026-11-02; ours, MIT |
| KIT_CREDITS | closer-studio CREDITS.md (fonts and their licences); read 2026-11-02; ours |
| KIT_EG | closer-studio EDITING_GRAMMAR.md: the clock measured across 22 top-performing videos, sources in RESEARCH.md; read 2026-11-02; ours, MIT |
| KIT_RULES | closer-studio CLAUDE.md and HOUSE_RULES.md: never a number or claim on screen the footage or brand file does not contain; no em dashes; client-facing annuity copy never says the word; punch-ins 100% to about 112%; read 2026-11-02; ours, MIT |
| KIT_VSLB | closer-studio skills/video/vsl-builder/SKILL.md: assemble from locked word maps, nothing transcribed again; read 2026-11-02; ours, MIT |
| KIT_grade | closer-studio tools/studio/grade.py; read 2026-11-02; ours, MIT |
| LAVE | https://arxiv.org/abs/2402.10294; 2024-02-15 |
| LIBROSA | https://pypi.org/project/librosa/; 1.0.0, 2026-08-11; ISC |
| LIBROSA_PV | https://librosa.org/doc/0.11.0/generated/librosa.phase_vocoder.html; 2026-08-11 |
| LIU22 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8874014/; 2022-02-11 (cites Yamashita 2019) |
| LJ_MORPH | https://larryjordan.com/articles/adobe-premiere-pro-cc-2105-morph-cut/; 2015-06-28 |
| LUTS | https://juan-melara.squarespace.com/blog/print-film-emulation-luts-for-download ; https://rawpedia.rawtherapee.com/Film_Simulation ; https://github.com/EaryChow/AgX; 2021-10-12 / various; flags |
| M3 | https://github.com/flutter/flutter/blob/master/packages/flutter/lib/src/material/motion.dart ; material-components-android Motion.md; 2026-11-02; BSD-3 / Apache-2.0 |
| MADMOM | https://github.com/CPJKU/madmom; 0.16.1, 2018-11-14; models CC BY-NC-SA, flag |
| MASTERCLASS | https://masterclass.com/articles/guide-to-comedic-timing; unverified |
| MEDIAPIPE | https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter; 2023-05-10; Apache-2.0 |
| MEET | https://research.google/blog/background-features-in-google-meet-powered-by-web-ml/; 2020-10-30 |
| META_ADS | https://www.facebook.com/business/ads-guide/update/video/instagram-reels (keep the top 14%, bottom 35% and 6% each side free), as cited in tools/studio/platforms.py; checked 2026-10-31 |
| META_SAFE | https://www.hopperhq.com/blog/instagram-reel-size/ ; https://admanage.ai/instagram-reels-safe-zone; 2026-10-29; unverified against Meta |
| MIXKIT_BBC | https://mixkit.co/license/ ; https://sound-effects.bbcrewind.co.uk/licensing; 2026-11-02; unverified, flag |
| MONEYPRINTER | https://github.com/harry0703/MoneyPrinterTurbo; 2026-10-31; MIT, anti-reference |
| MORPHIC | https://morphic.com/resources/sounds/transition-sound-effects; 2026 |
| MRBEAST_GUIDE | https://cdn.prod.website-files.com/6623bf84e83241ec49b548e4/66edaa19db6e9359bb92931f_How-To-Succeed-At-MrBeast-Production%20(2).pdf; 2024-09; leaked, do not redistribute |
| MUBERT | https://mubert.com/blog/how-to-make-music-fit-your-video-length-exactly; unverified; low |
| MURCH | https://nofilmschool.com/2016/11/6-rules-good-cutting-according-oscar-winning-editor-walter-murch; 2016-12-01; weights unverified |
| M_GADZHI | https://www.youtube.com/watch?v=YZ6OyZKrRh8; measured 2026-11-02 |
| M_HORMOZI | https://www.youtube.com/watch?v=yb2cLMMuMdQ; measured 2026-11-02 |
| M_HORMOZI_POD | https://www.youtube.com/watch?v=HwmwyBgzj8c; measured 2026-11-02 |
| M_MRBEAST | https://www.youtube.com/watch?v=Ah_uuTwGOYU; measured 2026-11-02 |
| NETFLIX_FGS | https://www.broadbandtvnews.com/2025/07/04/netflix-film-grain-synthesis-saves-on-the-bitrate/; 2025-07-04 |
| NFX_MIX | https://backlothelp.netflix.com/hc/en-us/articles/360001794307-Netflix-Sound-Mix-Specifications-Best-Practices-v1-5; v1.5, date unverified |
| NFX_TIME | https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394-Timed-Text-Style-Guide-Subtitle-Timing-Guidelines; 2025-07-04 |
| NFX_TTSG | https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide; 2025-12-19 |
| NNG | https://www.nngroup.com/articles/animation-duration/; 2020-02-09 |
| ONEOF10 | https://1of10.com/blog/what-is-a-jump-cut/; 2026-10-05 |
| OPUS | https://www.opus.pro/blog/youtube-shorts-caption-subtitle-best-practices; 2025-11-11 |
| OTIO | https://github.com/AcademySoftwareFoundation/OpenTimelineIO; 2026-10-31; Apache-2.0 |
| OVERSEER | https://www.overseeros.com/blog/background-music-volume-under-voiceover; 2026-10-20 |
| OWNER_FM | the owner's own phone takes: word maps and silence measurements of three takes; 2026-10-30; private project data, numbers only |
| P910 | https://www.itu.int/rec/T-REC-P.910; 07/26 |
| PANICKSSERY24 | https://arxiv.org/abs/2404.13076; 2024-04-15 |
| PEACHPIT | https://www.peachpit.com/articles/article.aspx?p=3150372&seqNum=6; 2022-10-25 |
| PIXABAY | https://pixabay.com/service/terms/; 2026-10-20; no standalone redistribution, flag |
| PLAYWRIGHT_BROWSERS | https://playwright.dev/python/docs/browsers ; https://playwright.dev/python/docs/intro; 2026-11-02; Apache-2.0 |
| PLAYWRIGHT_CLOCK | https://playwright.dev/python/docs/clock; 2026-11-02; Apache-2.0 |
| PLOSIVE | https://noiseworksaudio.com/blog/how-to-remove-plosives/ ; https://www.production-expert.com/production-expert-1/how-to-reduce-plosive-thumps-in-vocal-recordings; unverified |
| PREMIERE_DUCK | https://origin-www.lynda.com/Premiere-Pro-tutorials/Automatic-ducking/2871078/2381099-4.html; unverified; low |
| PREMIUMBEAT | https://www.premiumbeat.com/blog/timing-music-for-video-editing/; 2016-10-11 |
| PS_EXEC | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies; 2026-08-31 |
| PYLOUDNORM | https://pypi.org/project/pyloudnorm/; 0.2.0, 2026-01-04; MIT |
| PYSCENEDETECT | https://www.scenedetect.com/docs/latest/api/detectors.html; v0.7.2, 2026-10-11; BSD-3 |
| PYTSMOD | https://pypi.org/project/pytsmod/; 2023-11-22; GPL-3.0, flag |
| PYWIN | https://docs.python.org/3/using/windows.html; 3.15.2 docs, 2026-11-02 |
| QUENE07 | https://hugoquene.nl/onderzoek/q.jphon.20060912.pdf; 2007 |
| QUENE_DRIFT | https://www.researchgate.net/publication/311817264_On_the_just-noticeable_difference_for_tempo_in_speech; date unverified |
| REALEYE | https://realeye.io/blog/post/the-gravity-of-the-center-what-grabs-attention-in-vertical-videos/ (on Baig et al. 2025); 2025-11-03 |
| REAP | https://reap.video/blog/short-form-video-safe-zones; 2026-09-07 |
| REMOTION | https://github.com/remotion-dev/remotion; 2026-11-01; Remotion License, flag |
| RIEDL | https://ffmpeg.martin-riedl.de/; 9.0.2, 2026-09-20; licence unverified |
| ROBERTS20 | https://arxiv.org/abs/2006.00848; 2020-07 |
| RUBBERBAND | https://github.com/breakfastquay/rubberband; v4.0.0; GPL or commercial, flag |
| RVFC | https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback; Baseline 2024 |
| R_EDITORS | https://reddit.sentinel-team.org/posts/1t5889j/snapshots/2026-05-07T15%3A52%3A26.7606Z; about 2025-11-09; mirror, medium |
| R_PODCAST | https://reddit.sentinel-team.org/posts/1sgxfhj/snapshots/2026-04-10T10%3A15%3A38.733477Z; about 2025-09-17; mirror, medium |
| R_REFRAME | https://reddit.sentinel-team.org/posts/1ttgimr/snapshots/2026-06-02T13%3A21%3A35.999915Z; about 2025-12-31; mirror, medium |
| SALT15 | https://ochre.lib.uchicago.edu/ochre?uuid=b3c2546c-f0d8-473f-a012-531171718682&load; 2015 |
| SELFIE | https://www.smithsonianmag.com/smart-news/your-selfies-are-lying-you-180968340; 2018-03 |
| SENDSHORT_CAPS | https://sendshort.ai/guides/hormozi-captions/ (Hormozi-style caption spec; notes Montserrat is SIL OFL 1.1); last updated 2026-01-11 |
| SETUPFFMPEG | https://github.com/FedericoCarboni/setup-ffmpeg; v3; MIT, avoid |
| SETUPUV | https://github.com/astral-sh/setup-uv; v10.3.3; MIT |
| SHI24 | https://arxiv.org/abs/2406.07791; 2024-06-12 |
| SHUTTER | https://www.manualslib.com/manual/983838/Red-Epic.html?page=89; various |
| SIGNALSMITH | https://github.com/Signalsmith-Audio/signalsmith-stretch ; https://pypi.org/project/python-stretch/; 0.3.1, 2025-02-14; MIT |
| SMITH08 | https://bop.unibe.ch/JEMR/article/view/2264; 2008-12-16; CC BY 4.0 |
| SMITH12 | https://ualresearchonline.arts.ac.uk/id/eprint/21187/; 2012; CC BY-NC-ND |
| SONILO | https://sonilo.com/blog/guides/funny-sound-effects-for-videos; 2026-08-26 |
| SONNISS | https://sonniss.com/gdc-bundle-license/; 2026-11-02; no redistribution, flag |
| SOUNDGIRLS | https://soundgirls.org/how-to-avoid-over-editing-podcasts/; about 2022, unverified |
| SOUNDSTRIPE | https://www.soundstripe.com/blogs/how-to-cut-music-for-video-from-stock-music-sites; 2026-08-26 |
| SOZAI_GADZHI | https://sozai.app/transcript/ai-edit-iman-gadzhi-videos/; 2026, channel unverified |
| SPLIT_TIPS | https://www.instagram.com/reel/C8C6JZxpR2w/; unverified; low |
| SPOTIFY | https://support.spotify.com/us/artists/article/loudness-normalization/; 2026-11-02 |
| SSE_BREATH | https://sound.stackexchange.com/questions/27870/effective-way-to-reduce-breathing-in-adrs-and-voiceovers; unverified; CC BY-SA |
| SUBMAGIC | https://www.submagic.co/; 2026-11-02 |
| SUBSCRIBR | https://subscribr.ai/youtube-strategy/editing-talking-head-videos-engaging; unverified 2026; low |
| TIKTOK_SAFE | https://www.socialync.io/tools/safe-zones/tiktok ; https://www.revid.ai/tiktok-safe-zone ; https://www.remotion.dev/elements/overlays/social-safe-zones/; 2026; low |
| TRANSNET | https://github.com/soCzech/TransNetV2; 2026-11-02; MIT |
| UNDERLORD | https://www.descript.com/underlord; 2026-11-02 |
| UV | https://docs.astral.sh/uv/getting-started/installation/; 0.13.6; licence unverified |
| VAMCP | https://github.com/misbahsy/video-audio-mcp; date not shown; MIT |
| VIDEOAGENT | https://github.com/HKUDS/VideoAgent; 2026-07-22; MIT |
| VIDEOUSE | https://github.com/browser-use/video-use; last push 2026-10-08; MIT |
| VIDPROS | https://vidpros.com/fix-background-music-too-loud-video/; 2026-05-21 |
| PANEL_V9 | docs/panels/2026-11-02_vsl_full_reset_vs_previous.md (this kit); 2026-11-02; 12 blind reviews and a devil's advocate |
| VIMEO_FRAMING | https://vimeo.com/blog/post/framing-and-composition/; unverified date |
| VIVICT | https://github.com/svt/vivict; 2026-11-02; MIT |
| VIZARD_PAUSE | https://agent.vizard.ai/how-to/cut-the-pauses-and-stutters-out-of-a-raw-talking-head-video.html; 2026-10-10 |
| VIZARD_PUNCH | https://agent.vizard.ai/how-to/stop-the-punch-ins-cycling-too-fast-in-a-talking-head-edit.html; 2026-10-10 |
| VMAF | https://github.com/Netflix/vmaf (resource/doc/ffmpeg.md); libvmaf v3.0.0; v1 models 2026-06; BSD-2-Clause-Patent |
| VSCOPE | https://docs.kdenlive.org/en/tips_and_tricks/scopes/vectorscope_i_and_q_lines.html ; https://discuss.pixls.us/t/art-white-balance-vectorscope/48204 ; local ColorChecker computation; 2025-26 |
| WANG23 | https://arxiv.org/abs/2305.17926; 2023-05-29 |
| WCAG143 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html; WCAG 2.2 |
| WCAG147 | https://www.w3.org/WAI/WCAG22/Understanding/low-or-no-background-audio.html; 2025-09-16 |
| WHISPERX | https://github.com/m-bain/whisperX; 2026-10-22; BSD-2 |
| WIDEFRAME | https://try-wideframe-6ke.pages.dev/blog/what-is-contextual-ai-generation-for-video; 2026-03-04 |
| XYLA | https://www.xyla.ai/tools/social-media-sizes/ and orsonlord.com overlays, as cited in tools/studio/platforms.py; 2026 |
| YAMASHITA | cited inside LIU22; 2019 |
| YTAL | https://support.google.com/youtube/answer/3376882?hl=en; 2026-11-02; YouTube-only, flag |
| YTSFX | https://youtubesfx.com/guides/sound-effects-for-every-type-of-youtube-video/; 2026-02; low |
| YTSFX_CREATORS | https://youtubesfx.com/creators/; 2026; low |
| YT_SFN | https://productionadvice.co.uk/stats-for-nerds/; unverified |
| YUNET | https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet; 2023mar / 2026may; MIT |
| ZEBRA | https://community.adobe.com/t5/premiere-pro-discussions/re-colorists-luma-waveform-ranges-is-my-grade-too-dark/m-p/14349647 ; dvxuser ; dvinfo; 2006-2024; low |
| ZHENG23 | https://arxiv.org/abs/2306.05685; 2023-06-09 |
