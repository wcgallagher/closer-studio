# Audio spec

The readable form of the Closer Studio audio spec v1 (2026-11-02): how the voice is cleaned, how music is chosen and ridden under it, how sound effects are placed in each of the two dialects, how the mix is finished and checked, and where every number came from. The engine that runs it is `tools/studio/sound.py` (`SOUND_RULES`, `SECTION_PRESETS`), driven by `skills/video/sound-director/SKILL.md`; the editing rules around it are in `docs/EDITOR_RULEBOOK.md`.

How to read it:

- **Engine** values are what the code does today. When this page and the code disagree, the code wins and this page gets fixed.
- **Proposed** values are research recommendations the code does not run yet. They stay here so the next change has its numbers and sources ready.
- Every number names its source key (the table in section 9) or **house**: our own choice, with the figure it was set against when there was one.
- Nothing here listens. Every check is a measurement, so results are reported as "measured, not listened", and the owner judges taste by ear (section 7).

## 1. Terms

| Term | Meaning | Source |
|---|---|---|
| V-M (voice over music) | the voice stem's momentary loudness (BS.1770, K-weighted, 0.4 s window, 0.1 s hop) minus the music stem's, on frames where a word plays and the voice is above -50 LUFS. Reported as the median and the 10th percentile per section. Engine | ebu_tech3341_3342; kit_sound |
| V-M>120 | the same with the music high-passed at 120 Hz first, so low end that does not mask words is ignored. Proposed | iman_promo |
| SFX level (LU) | the loudest 400 ms of a placed sound on its own, in LU relative to the voice stem's integrated loudness; negative means under the voice. Gain = target - the sound's own loudest momentary + the voice's integrated. Engine | house; kit_sound |
| t0 | an event's anchor frame: the cut frame, the first visible frame of a card or text, the reveal frame. At 30 fps one frame is 33.3 ms | manifest (the takes are 30 fps) |
| band dB | long-term spectrum energy per band, in dB relative to the total (FFT 8192, Hann) | iman_4vid |

## 2. Voice: less is more

### Why the chain got lighter

The first chain was called over-processed by the owner ("sounds too enhanced", 2026-10-30). What the diagnosis found (manifest; kit_voice; kit_sound; acx):

- The v6 and v7 chains boosted 120 Hz and denoised hard. Noise ended 14.8 dB under speech against 17.5 dB in the raw take, so the denoise made the floor worse relative to the speech.
- The legacy `VOICE` chain in `tools/studio/voice.py` gates the band under 300 Hz between words (agate threshold 0.03, ratio 3, release 250 ms). Low end switching on and off per word is a processed tell. It is still the chain the older mix uses when a layers file has no `sound` block.
- The same chain adds 1.5 dB at 9 kHz. Phone mics plus "clarity" boosts raise sibilance (izotope).
- Pause cuts of 12 dB, breath cuts of 10 dB and up to 18 dB of denoise read as a vacuum between words.
- The measured floor sat 24.7 dB under speech; ACX's spoken-word spec implies 37 to 42 dB.

On the kit's test VSL (about 95 s, phone audio, DNSMOS P.835) the lighter chain scored OVRL 2.66 against 2.63 for the raw take and 2.59 for the old chain: a cleaner background (BAK 3.20 against 3.01 raw) at the cost of a little voice character (SIG 3.29 against 3.41 raw) (kit_sd). So even this chain costs something: when in doubt, lower a rule, never add a stage.

### The phone chain, in order

The order is the order of `voice_master`. Steps 4, 5, 7 and 8 run inside one STFT pass.

| Step | Engine (`SOUND_RULES["voice"]`, `voice_master`) | Proposed, not built | Sources |
|---|---|---|---|
| 1. Ingest | decoded to mono at 48 kHz by ffmpeg | pick a channel: sum to mono when L/R correlation is 0.9 or more, otherwise keep the channel with less energy under 150 Hz in the pauses; resample with soxr | house (0.9); deepfilternet (its binary takes 48 kHz WAV only) |
| 2. Subsonic | none | high-pass 30 Hz, 2nd order | house |
| 3. High-pass | 80 Hz, or 110 Hz when over 0.45 of the pause energy sits under 150 Hz. The filter is a 2nd-order Butterworth run forward and backward (`sosfiltfilt`), which doubles the slope: about 24 dB per octave with the corner 6 dB down (measured 2026-11-02 at 80 Hz: -6.0 dB at 80 Hz and -24.6 dB at 40 Hz) | target: the band under 80 Hz at -25 dB or lower relative to total | kit_sound; iman_4vid (voice under 80 Hz at -20.7 to -31.8 dB); house |
| 4. Noise reduction | decision-directed Wiener gain against the median of the pauses (`denoise_max_db` 12, oversubtraction 1.5, smoothing 0.98); steady room tones that stand 8 dB over their neighbours are notched, up to 18 dB | DeepFilterNet3 (deep-filter binary, delay compensation on, post-filter off) with the dry signal mixed back at -12 dB, which caps the reduction near 12 dB. Today `--denoise deep` runs DeepFilterNet at full strength before the director, which then denoises again | kit_sound ("12 dB at most, so no watery artifacts"); deepfilternet (an attenuation-limit flag is unverified, hence the mix-back) |
| 5. Wind bursts | frames whose energy under 150 Hz jumps 8 dB over its voiced median get a low shelf up to 180 Hz, at most 12 dB, on those frames only | ffmpeg-only fallback: `adynamicequalizer=dfrequency=100:dqfactor=0.7:dftype=lowpass:tfrequency=180:tftype=lowshelf:mode=cut:range=12:attack=5:release=80:auto=on`, verified by measurement | kit_sound; ffmpeg |
| 6. No low-band gate | the director never gates; the gate lives only in the legacy `VOICE` chain | remove the gate from `VOICE` too | house; manifest |
| 7. Corrective EQ | third-octave match from 80 Hz to 12.5 kHz toward a long-term speech curve (`TARGET_SPEECH`), applied at 50%, cuts up to 4 dB, boosts up to 2 dB, no boost at 6 kHz and above | check the result against the measured reference bands below | kit_sound; iman_4vid; house (0.5 and the caps; the kit was 0.7 / 4 / 2.5 / 1.5) |
| 8. De-ess | frames where 4.5 to 10 kHz runs 6 dB hotter than usual against 1 to 4 kHz, at most 6 dB | detect on 5 to 8 kHz against 0.3 to 4 kHz; ffmpeg fallback `deesser=i=0.4:m=0.5:f=0.5` (its default i=0 does nothing) | kit_sound; izotope (5-8 kHz); ffmpeg |
| 9. Breaths | kept, 6 dB lower: gaps of 0.12 to 1.2 s that rise about 9 dB over the room | | erv_hormozi (editors leave breaths in); kit_sound |
| 10. Phrase clip gain | phrases split at gaps of 0.25 s move 70% of the way to the median phrase loudness, at most 6 dB | | kit_sound |
| 11. Leveller | 1.5:1 above -26 dB, attack 15 ms, release 180 ms, knee 6 dB | expect 2 to 3 dB of gain reduction | kit_sound; house |
| 12. Peak catcher | 3:1 above -10 dB, attack 1 ms, release 50 ms, knee 2 dB, peak detection | at most 3 dB of gain reduction | kit_sound; house |
| 13. Stem level | one static gain to -16 LUFS, no limiter on the voice stem | | kit_sound; iman_promo (voice stem -16.5 LUFS); manifest (a voice-stem limiter pulled RMS down 1.9 dB) |
| 14. Pauses | pauses of 0.18 s or more go 4 dB down, after the dynamics so a compressor cannot lift them again; joins are 10 ms equal-power crossfades (`assemble_voice`) | room tone from the same take under every splice and pause cut (an ambience bus), 20 ms crossfades | kit_sound; house (4 dB, the kit was 12) |
| 15. Never by default | reverb, exciter or saturation, bandwidth extension, vocoder re-synthesis (resemble-enhance, VoiceFixer, Auphonic Studio Voice), a denoise post-filter, boosts above 6 kHz | | house; manifest |

Measured reference bands for a voice stem (four Gadzhi uploads, separated stems; a QC reference, not enforced by the engine) (iman_4vid):

| Band | Under 80 Hz | 80-150 | 150-300 | 300-800 | 800 Hz-2k | 2k-5k | 5k-10k | 10k-16k |
|---|---|---|---|---|---|---|---|---|
| dB relative to total | -31.8 to -20.7 | -13.5 to -5.5 | -9.0 to -5.2 | -4.6 to -2.1 | -14.2 to -8.1 | -19.9 to -12.7 | -26.0 to -21.4 | -35.5 to -30.0 |

If the 300-800 Hz band sits above -2 dB, expect the EQ to take 2 to 4 dB out around 250-500 Hz (house).

### Studio microphone chain (proposed, not built)

Selected when the pause SNR is 40 dB or more and under 0.2 of the pause energy sits below 150 Hz; otherwise the phone chain runs. Mono, 48 kHz; high-pass 70 Hz at 12 dB per octave; noise reduction only when the pause SNR is under 45 dB, Wiener at most 6 dB; EQ applied at 0.4 with cuts up to 3 dB, boosts up to 1.5 dB under 6 kHz and 1.0 dB above; de-ess as the phone chain; breaths 4 dB down; no pause cut; clip gain at 0.5, at most 4 dB; the same leveller and peak catcher; -16 LUFS. Every number is house except -16 LUFS (kit_sound) and the 70 Hz anchor (iman_4vid).

### Voice targets (proposed QC)

| Measure | Target | Anchor |
|---|---|---|
| band dB | inside the reference bands, 2 dB either side (house) | iman_4vid |
| short-term p95 minus p10 | 4.0 LU or less (house) | iman_tutorial 2.4, iman_dark 3.6, iman_2023 3.2 |
| crest factor | 14 to 20 dB (house) | manifest: raw 19.6-19.7, v7 final 17.6 |
| pause SNR | at least 30 dB, aim for 35 (house) | acx implies 37-42; manifest measured 24.7 |
| L/R correlation | 0.999 or more | iman_4vid (voice 0.999-1.0) |

### Denoise shoot-out on real takes (proposed)

Candidates: DeepFilterNet locally (free to run); the ElevenLabs Voice Isolator ($0.12 per minute: three takes of 262.1 s are 4.37 min, about $0.52); Auphonic's dynamic denoiser or speech isolation (a 5 h pack is $12 and each production bills at least 3 min, so three takes bill 9 min, about $0.36) (deepfilternet; el_isolator; auphonic; manifest for the take lengths). Score each on the pause noise floor against speech, the energy under 150 Hz in pauses, DNSMOS SIG, BAK and OVRL, the distance to the reference bands, and wind bursts per minute. The top two go to the owner's blind A/B (section 7); the default stays local DeepFilterNet. No head-to-head wind benchmark exists for these tools, so this test is the evidence (dnsmos; house).

## 3. Music

### Licence before taste

- Paid ads need a plan that names paid or digital ads; several libraries' entry plans cover social posts and websites but not ads (epidemic_pricing; artlist; uppbeat).
- A CC BY track needs its credit line wherever the video plays. The kit's bed `tools/music_industrial_cinematic.mp3` is CC BY 4.0: "Music: Industrial Cinematic by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0". A paid ad with no credit needs the composer's paid licence or another track (incompetech).
- Chart songs need a sync licence. Not used (jackcole_nelk; flaunt_nelk).
- Only CC0 sound files may be committed to this public repo (section 6).

### Choosing by format

| Format | Mood | Shape | Sources |
|---|---|---|---|
| vsl_hero (homepage and paid web) | dark cinematic, documentary, ambient-electronic or piano, mysterious, serious, dramatic; minor preferred; 70 to 115 BPM | 2 cues (story and hook, then the pitch at the turn), or 1 cue with drops and a re-entry; start at a high-energy bar, never the intro | behindit; validation; yoar7; kit_sound; iman_promo (story bed louder, pitch bed steady and low) |
| organic reel, Gadzhi dialect | mysterious, dramatic, motivational classical or synth | one track, one vibe, starting on a high-energy point | validation; yoar7 |
| organic reel, Nelk dialect | upbeat, summery, hype | montage cut on the beat, a mood track per scene; a licensed library only | jackcole_nelk; flaunt_nelk |
| paid ad, 15 to 60 s | as vsl_hero, or Nelk upbeat for montage ads | a licence that names paid digital ads (Epidemic Pro or Business, Artlist Pro, Uppbeat Pro or Business); no CC BY track without an on-screen credit | epidemic_pricing; artlist; uppbeat; incompetech |
| long-form talking, tutorial | a faint constant bed, or none | V-M about 20 LU and no riding, or no bed | iman_tutorial (19.7 LU, gap ride +0.8 LU); hormozi_comments (viewers praised no bed); hormozi_ig |

### How the engine scores a track (`score_track`, engine)

The engine never picks a track by itself; it ranks the files it is given, and the owner chooses by ear from the top three (`tools/studio/edit.py`).

| Measured trait | Points |
|---|---|
| tempo 70 to 115 BPM, or half of it inside that range | +2, otherwise -1 |
| voice-band share (1 to 4 kHz over everything above 60 Hz) at most 0.42 | +1 to +3, more the lower it is; over 0.42, -2 |
| minor mode | +0.8 |
| it builds: the second quarter 2 dB or more louder than the first | up to +2 |
| shorter than 60% of the video | -1.5 (it will need looping) |
| bars more than 18 dB apart | -1 (it pokes out of the bed) |
| spectral centroid over 3200 Hz | -1 (hiss and cymbals in the voice range) |

### Spectral gate for any bed (proposed)

The 1 to 4 kHz band at -13 dB or lower relative to total; the bands under 80 Hz and 80-250 Hz the two largest; L/R correlation between 0.35 and 0.9; a bright bed gets a static cut of 3 to 6 dB at 1 to 4 kHz until the band reaches -13 dB (house; anchored on iman_4vid: Gadzhi beds measured 1-4 kHz at -12.9 to -23.5 dB, under 80 Hz at -1.6 to -4.2 dB, L/R 0.35-0.89). The engine measures brightness differently: the voice-band share above, and the pocket tiers in "Riding the bed".

### The kit's bundled bed, measured (ic_measure)

| Measure | 85 s segment (the cut of a 96 s video) | Full track, 244 s |
|---|---|---|
| under 80 Hz / 80-250 Hz / 250 Hz-1k | -3.3 / -3.5 / -11.7 dB | -3.5 / -3.2 / -12.4 dB |
| 1-4 kHz / 4-10 kHz / 10-16 kHz | -18.8 / -24.7 / -34.2 dB | -19.3 / -23.4 / -36.1 dB |
| L/R correlation | 0.547 | 0.408 |
| integrated loudness, loudness range | -19.9 LUFS, 8.5 LU | -17.8 LUFS, 9.4 LU |
| sample peak | 0.0 dBFS | 0.1 dBFS |

It passes the spectral gate on every band and is darker than the Gadzhi beds at 250 Hz-1 kHz, so masking is not the problem. The reasons to replace it are the licence (the credit line, or a paid licence for ads) and stock familiarity: Kevin MacLeod tracks are widely heard (discoverpods), though this particular track's recognisability is unverified. It peaks at 0 dBFS, so pre-gain it before any processing.

### Fitting it to the cut (engine)

- The track is cut on bar lines. A long track starts on a bar inside its first 40%, chosen so a section change lands near the `land` word, and splices on a bar into its own last 4 bars with a 40 ms equal-power crossfade, so it ends on its real ending; only the last 1.2 s fade (kit_sound). A track whose own ending is a fade (last 4 bars more than 6 dB under its median bar) ends on a button instead: full level under the last word, then the first downbeat after it decays 60 dB over 2.4 s. The bed never fades under the ask (v9 review, 2026-11-02; kit_sound).
- Effects are one-shots: a start-timed sound whose peak comes late for its role is refused, peak-timed swells keep at most 1.5 s of build, and every sound stops a role-sized time after its hit with a 0.25 s fade (`SOUND_RULES["sfx"]`: `max_lead_s`, `lead_trim_s`, `tail_max_s`; kit_sound).
- A short track plays from the top and repeats an even number of bars whose loudness matches across the splice. It never restarts from zero (kit_sound).
- Proposed: a tempo nudge of at most 3% (ffmpeg's rubberband filter if present, otherwise atempo); exact-length services such as Epidemic's EditRecording (through its MCP server) or its adapt-length API (beta, 1 s to 5 min), or an ElevenLabs Music composition plan (house; epidemic_mcp; epidemic_api; el_music).

### Voice over music, per section (engine)

`music_stem` sets each section's bed gain so the V-M median hits its target, renders, measures V-M again and applies one correction pass. The sections come from the layers file's `sound.sections`. `closer.py edit` writes them from its own `DEFAULTS` (`tools/studio/edit.py`), which match the presets below for vsl_hero, paid ad and organic reel and use 20 LU for yt_authority and skool_lesson; it writes no `p10`, and a section without one gets its `vm` minus 6 (`tools/studio/longform.py`). `SECTION_PRESETS` itself is read by no code. With no sections, one section runs at 14 LU with a floor of 8.

| Format | Section | V-M median (LU) | Worst-10% floor (LU) | Proposed V-M>120 floor (LU) | Anchor |
|---|---|---|---|---|---|
| vsl_hero | hook (to the start of the offer) | 11 | 5 | 13 | iman_promo story section: median 9.9, p10 3.3, >120 median 12.2 |
| vsl_hero | body (problem to urgency) | 14 | 8 | 16 | iman_promo pitch bed about 11.5 LU under the voice; kit_formats vsl_hero "at least 13 dB down" |
| vsl_hero | turn and CTA (to the ask) | 12 | 6 | 14 | house |
| paid_ad | all | 12 | 6 | | house |
| organic_reel | all | 16 | 9 | | house |
| tutorial | all | 20 | 13 | | iman_tutorial 19.7 |
| story | all | 23 | 15 | | iman_dark 23.5 |

For the owner's ears, A/B the body at 11 against 17 LU around the default 14 (section 7).

### Riding the bed (engine)

Deterministic automation drawn from the word timings, never a sidechain compressor. A sidechain's gain reduction depends on how far the voice is over threshold, with no hold and no look-ahead, so its depth changes word to word and the bed climbs back between words: viewers hear that as pumping (ffmpeg; umbrella_bed; adobe_duck).

- Under speech the bed sits at the section's gain (0 dB of extra riding).
- It goes down 0.2 s before each phrase and gets there in 0.15 s.
- It comes up only in pauses of 1.2 s or more: 6 dB (8 dB in the first 8 s), starting 0.25 s after the phrase, over 0.6 s. Shorter gaps hold, so nothing pumps. Measured for scale: the Gadzhi promo swelled its bed 10.2 LU in voice gaps (iman_promo).
- A voice-band pocket at 300 Hz to 4 kHz: 2 dB down all the time, and while words play another 4 dB for a bright bed (its 1 to 4 kHz band above -15 dB), 2 dB for a medium one (-15 to -19 dB), nothing for a dark one. The kit's bundled bed measures -18.8 dB, so it gets the 2 dB tier.
- The `cta` section rides 2 dB up (`cta_lift_db`), but `music_stem` then calibrates every section to its own V-M target, so on word frames the lift cancels out. Measured 2026-11-02 on synthetic stems (body 14, cta 12): the cta section came out at 12.0 LU and the same bed level with the lift at 0 or 2 dB. To get a louder bed under the ask, lower the cta section's `vm`.
- ffmpeg-only fallback, for when the numpy path is unavailable: `acrossover=split=1000 4000:order=8th` on the bed, `sidechaincompress` on the middle band only (`threshold=0.02:ratio=6:attack=15:release=300:knee=4`) keyed by the high-passed voice, `amix=inputs=3:normalize=0`, plus 2 to 3 dB of slow broadband ducking (ffmpeg_carve_test).

Sources: kit_sound for every engine number; house for 1.2 s, the 6 and 8 dB lifts, the 0.2 s lead, the 0.6 s ramp and the pocket tiers (the 1.2 s anchor is a craft convention, craft_unverified).

### Drops to silence (engine)

Each `music.mute` window drops the bed to -40 dB, fully down 0.4 s before its first anchor after a 60 ms fade, so the line lands dry. A third value in the window, `[from, to, lead]`, sets the lead in seconds instead of 0.4 (`tools/studio/longform.py`). The bed comes back on the next bar line the beat tracker found, if that bar is within 1.0 s of the window's end, in one 10 ms step of the gain curve (`return_ramp_s` 0.02 is in `SOUND_RULES` but no code reads it), and the dialect marks the return (`drop_return`). At most 3 drops per video; later ones are ignored (kit_sound). A drop runs 1 to 7 s (proposed, house). For scale, one Gadzhi upload had 25 dropouts of 1.4 to 26.1 s, under thesis and truth lines (iman_dark). The 0.4 s lead sits inside the 0.3 to 1.0 s craft range (craft_unverified).

### Swell and resolve

- Engine: after the last word the bed rises 6 dB over 2 s, starting 0.2 s later, and the last 1.2 s fade out (kit_sound; house; the kit was 10 dB).
- Target, reported but not enforced: every swell keeps the mix's maximum short-term loudness at or under the integrated loudness plus 5 LU (sound.json `qc.short_term_max_over_integrated_lu`) (ebu_r128s1).
- Proposed: a music-only swell of 2 to 4 s before a reveal, 6 dB over the gap level, only where a voice gap allows (iman_promo had a 9 s music-only swell before its reveal; craft_unverified gives 3 to 6 dB over 2 to 4 s).

## 4. Sound effects

### Global rules

- Recorded sounds first; the synthesized set (`sfx_whoosh`, `sfx_impact`, `sfx_riser`, `sfx_tick` and the rest in sound.py) is only the fallback for a role with no file, and sound.json shows `synth` as its file. Audiences know recorded timbres (the Nelk research angle; house).
- The library takes a role's files in turn (`Library.pick`), so give each role at least two files: with one file, or with the synthesized fallback, every event of that role plays the same sound. `rotate_max_repeat` (2) is in `SOUND_RULES` but no code reads it (engine, kit_sound).
- A sound that overlaps a word goes 5 dB lower, except risers and reverses (engine, kit_sound). Proposed: place a number reveal in a voice gap of 0.4 s or more where the cut allows, otherwise only 3 dB lower (house).
- Every event should keep the mix's maximum short-term loudness at or under integrated plus 5 LU; sound.json reports it, nothing enforces it yet (ebu_r128s1).
- Mono one-shots centred; whooshes may pan up to 0.3 toward the motion (proposed, house).
- No sound on a cut that says nothing new. A dry cut is a choice (umbrella_dopamine; visclub).

### Where each sound hits (engine, `SOUND_RULES["sfx"]["align"]`)

| Role | What lands on t0 |
|---|---|
| whoosh, swish, reverse | its loudest point (a whoosh peaks on the frame of most motion blur) |
| riser | its end; it is cut there, dead |
| impact, sub, shine, tick | its start (a tick lands on the element's first visible frame) |

Sources: joseph_sd (whoosh peak on the most blur, a riser peaks at the end of the build and the hit releases it); jackcole_nelk (the impact on the drop); kit_sound. Proposed tolerance: 1 frame either side (house).

### The grammar of the two dialects (engine levels, LU against the voice)

"Dry" means no sound. The suggested recorded files are CC0 Freesound pages (section 6), checked 2026-11-02; any CC0 file of the same role works.

| Event (kind) | Gadzhi (premium, the default) | Nelk (energy) | Suggested files | Sources |
|---|---|---|---|---|
| punch-in in the first 8 s (`punch_in_hook`) | whoosh -18 | whoosh -12 | low soft whoosh: ch_ase 423799; whip-zoom whoosh: BennettFilmTeacher 486234, with DJT4NN3R 449996 layered at -18 when two moves stack (proposed) | validation (a deep whoosh on slow moves); joseph_sd (a whoosh on every move, layering) |
| punch-in later (`punch_in`) | dry | whoosh -12 | as above | joseph_sd; house |
| hard cut (`hard_cut`) | dry | swish -16 | short swish: lesaucisson 585257 | visclub; umbrella_dopamine; erv_hormozi (heavy in the hook, toned down in the body) |
| card in (`card_in`) | whoosh -14 | whoosh -11 | deep whoosh: anagar 267951 or ch_ase 423799 | validation; joseph_sd (texture pass) |
| card out (`card_out`) | dry | swish -16 | lesaucisson 585257 | house |
| card element lands (`card_element`) | dry | tick -14 | pop: D.S.G. 328119, or Kenney Interface Sounds | joseph_sd (clicks on text pop-ups) |
| chip (`chip`) | shine -22 | tick -14 | ding: chennes 376807 | validation (a ding or shine on important items) |
| hand label (`hand_label`) | dry | tick -22 | Kenney Interface Sounds | house |
| section change (`section_change`) | reverse -16 | riser -10, impact -6 | reverse cymbal: deleted_user_7146007 383903 (trimmed) or burnttoys 9523; riser: syntheffects 685256; impact: Kenney Impact Sounds | yoar7 (track changes at topic turns); behindit (reverse impacts); jackcole_nelk (build to a drop) |
| number reveal (`number_reveal`) | shine -14, sub -10 | riser -8, impact -4, sub -8 | shine: 5ro4 611113; sub: JarredGibb 263892; riser: syntheffects 685256 | iman_dark (music cut under key lines); validation (shine); jackcole_nelk (riser, bang, bass boost) |
| into the ask (`cta_riser`) | riser -12 | riser -8 | syntheffects 685256, or reathance 503818 for a long build | jackcole_nelk; house |
| pointer (`pointer`) | tick -20 | tick -14 | click: Pixeliota 678248 or pbimal 534104 | house |
| end card (`end_card`) | shine -18 | impact -6, sub -10 | 5ro4 611113; Kenney Impact Sounds; JarredGibb 263892 | iman_promo (a swell at the end) |
| bed returns after a drop (`drop_return`) | reverse -18 | impact -8 | burnttoys 9523 | behindit |

Every level is house, set against umbrella_bed (hits about 10 dB under the voice). The cut makes card in and out, card elements, chips, the end card, section changes (at a take change when the layers file sets `take_change_kick`, and at each word in its `kicks` list), punch-ins and drop returns by itself. Number reveals, CTA risers, pointers, hand labels and hard cuts come only from the layers file's `sfx` list (`skills/video/sound-director/SKILL.md` section 5).

### Reveal designs (proposed, beyond what the grammar row places)

- **Gadzhi:** the bed drops to silence from 0.4 s before t0 (or an existing mute covers it); shine and sub start on t0; an optional single low riser ending on t0 only if the line builds; the bed returns on the next downbeat with a reverse cymbal peaking on the return.
- **Hormozi counter:** the numerals count up over 0.8 to 1.2 s with a tick (-18) on each change (Pixeliota 678248 or Kenney Casino Audio) and stop on a bass boom (-6, LordHannes 268084). A cash register (-14, Zott820 209578) at most once per video, replacing the ticks (erv_hormozi).
- **Nelk drop:** a riser peaking on t0, impact and sub on t0, the bed hard-cut at t0, an optional 0.3 to 0.5 s smash to black, then the voice resumes dry (jackcole_nelk).
- A proof screenshot gets a camera shutter on its first frame (-18 Gadzhi, Tonik1105 520684; Nelk adds a paper slide at -18, XTYL33 68224), at most once per VSL. Whether Gadzhi uses shutter sounds is unverified.
- At most 2 designed reveals per 95 s (house).

### Density budgets (engine, `SOUND_RULES["sfx"]["density"]`)

| Budget | Gadzhi | Nelk | Proposed in the research |
|---|---|---|---|
| events in the first 20 s | 8 | 14 | Gadzhi 8 (iman_dark: 8 of 12 events in the first 22 s); Nelk a sound on every motion event in the first 8 s, 0.35 s apart |
| events in the 60 s around one, after the first 20 s | 4 | 12 | Gadzhi 2 audible events per minute (iman_dark under 1 per minute; iman_4vid 1.4 to 3.4, low confidence); Nelk 4 per 10 s |
| ticks within 5 s either side | 1 | 3 | 1 per 10 s (Gadzhi) |
| risers per video | 1 | 3 | per 95 s: 1 (Gadzhi), 3 (Nelk), plus 4 impacts (Nelk) |
| reverses per video | 3 | 4 | 3 section changes per VSL (Gadzhi) |

An event closer than 0.35 s to one already kept is dropped. The planner keeps the most important first (`PRIORITY`: number reveal 6, CTA riser 5, section change 4, card in, end card and drop return 3, a punch-in in the hook 2, chip and pointer 1, everything else 0), and number reveals and CTA risers skip the 60 s budget. Every dropped event is listed in sound.json with its reason (kit_sound). For a vsl_hero the default dialect is Gadzhi; Nelk is the A/B challenger on the hook and the reveal (house).

## 5. Mix and master

### Buses

| Bus | Engine | Proposed | Sources |
|---|---|---|---|
| Voice | the section 2 chain, mono, centred, -16 LUFS | | kit_sound; iman_promo (-16.5) |
| Ambience | none | room tone from the same take under splices and pause cuts, at the take's own pause level minus the pause cut | house |
| Music | stereo bed: fit, static pocket, section gain, word-mask automation, drops, outro | with Epidemic stems: drums and bass (and instruments) under speech, the melody only where nobody speaks | kit_sound; epidemic_stems |
| Effects | library one-shots at the grammar levels | high-pass at 30 Hz | house |
| Master | the stems summed, then a limiter at -1.5 dB (5 ms look-ahead, 60 ms release, sample-peak detection) into mix.wav; the final encode sets loudness per platform with one static gain and one limiter (`voice.final_filter`) | detect peaks 4x oversampled (true peak); no dynamic loudnorm, no multiband, no stereo widening | kit_sound; kit_voice; auphonic (4x-oversampled true-peak limiter); ffmpeg (loudnorm falls back to dynamic mode without measured values) |

### Targets

| Measure | Engine | Proposed | Sources |
|---|---|---|---|
| integrated loudness | -14 LUFS for social and YouTube, -15 LUFS for web_vsl, -23 for broadcast (`tools/studio/platforms.py`); review passes within 1.0 LU | -14.5 LUFS, 0.5 LU either side | kit_formats (vsl_hero -15 to -14); iman_promo -14.9; iman_tutorial -14.3; umbrella_loud median -16.3; spotify -14 |
| true peak | -1.5 dBTP for social and YouTube, -1.2 for web_vsl, -1.0 for broadcast; review allows 0.3 dB over | -1.5 dBTP measured on the final AAC encode | ebu_r128 (-1 or lower); spotify (under -1, under -2 if louder than -14) |
| maximum short-term | integrated plus 5 LU or less (`SOUND_RULES["master"]`, reported in sound.json) | | ebu_r128s1 |
| loudness range | not checked | report it; warn over 8 LU; never a gate | ebu_r128s1 (LRA does not apply to short-form); iman_promo 7.6 |
| loudness to dialogue (mix integrated minus the speech-gated voice) | not checked | 0 to 3 LU; fail over 5 | ebu_r128s4 (5 LU or less); house |
| section short-term median | not checked | within 4 LU under to 3 LU over the integrated loudness | house (anchor: ebu_r128s4 and Tech 3343, a comfort zone of about +3 / -5 LU) |

### QC gates

What the engine checks today (sound.json `qc`, read by `tools/studio/review.py`):

| Number | Pass | Note |
|---|---|---|
| voice over music, median and worst 5% | 9 or more and 3 or more (`music_ok`) | the review's text still says "want >= 15 and >= 9"; the gate in the code is 9 and 3 |
| click suspects at the audio cuts | 0 | |
| effects per minute | 12 or fewer | the same for both dialects; hold Gadzhi to its own budgets |
| clipped samples | 0 | reported, not gated |
| sound in sync with the picture | each piece cross-correlated against the source | review.py |

Proposed gates (not built):

| Check | Measure | Fail | Sources |
|---|---|---|---|
| pumping | the applied music gain inside each phrase and inside any gap under 1.2 s | a move over 1 dB outside planned drops and lifts; on a rendered stem, the music's 100 ms RMS spread over 2 dB during continuous speech | house; a craft proposal, unverified as a standard |
| masking | V-M and V-M>120 per section | a median more than 2 LU off target, or a p10 or >120 median under the floor | house |
| sibilance | the voice's 5-10 kHz band; 20 ms frames where 5-9 kHz over 0.3-4 kHz runs 12 dB over the voiced median | the band above -19 dB, or over 0.5% of voiced frames flagged | iman_4vid (5-10 kHz at -21.4 to -26.0); izotope; house |
| boom | the voice's bands under 80 Hz and 80-150 Hz | under 80 Hz above -20 dB, or 80-150 Hz above -5 dB | iman_4vid |
| harshness | the voice's 2-5 kHz band | above -11 dB (warn dull under -22) | iman_4vid (-12.7 to -19.9); house |
| wind | 20 ms voiced frames where the energy under 150 Hz jumps 10 dB over its median | over 3 bursts per minute | house; a wind-noise paper via the tools research |
| noise floor | the voice stem in pauses of 0.3 s or more against the speech-gated level | warn under 30 dB, fail under 24 dB | acx; manifest |
| over-processing | the largest per-frame denoise; any EQ boost above 6 kHz; DNSMOS SIG | attenuation over 12 dB or any boost above 6 kHz (phone chain); warn when SIG is under 3.5 | house; dnsmos (speechmos is archived; NISQA's weights are non-commercial, do not use) |
| voice dynamics | short-term p95 minus p10 on voiced frames; crest factor | over 4 LU, or crest outside 14-20 dB | iman_4vid; manifest |
| loudness jumps | the mix's 3 s short-term median per section and between neighbouring windows | a section outside -4 / +3 LU of integrated; a jump over 6 LU between neighbours outside planned drops and reveals | ebu_r128s1; house |
| effect levels and density | each event's loudest momentary against the voice; events per window | a level more than 3 LU off its grammar value; density over the dialect cap | house |
| stereo | the voice's L/R correlation; ffmpeg aphasemeter on the music | voice under 0.999; any music window with mean phase under 0 | iman_4vid; ffmpeg |

Optional extra ears, all measured: Brouhaha (frame SNR and C50 room echo, MIT) and DNSMOS (SIG, BAK, OVRL at 16 kHz). Echo and poor clarity lower how listeners rate the speaker and the content (brouhaha; dnsmos; newman2018).

## 6. Where the sounds come from

### In this repo: CC0 only

Commit recorded effects as mono 48 kHz WAV with the leading silence trimmed, plus a licence manifest (proposed fields: Freesound id, title, author, source URL, licence CC0-1.0, the date the licence was checked, sha256, duration, peak dBFS, loudest momentary LUFS, integrated LUFS, onset ms, peak ms, spectral centroid, role). The engine's library today reads any folder of files named `<role>__<anything>.<ext>` and measures them itself (section 4; kit_sound). The originals need a logged-in browser or Freesound OAuth2 (the research sandbox got 403 and 401), so download them once on a desktop and commit (freesound_faq). The kit's `.gitignore` ignores `*.wav`, so a plain `git add` skips them: add a `!sfx/*.wav` line to `.gitignore` first, or use `git add -f`.

Freesound suggestions. Each page was opened and its CC0 licence checked on 2026-11-02 (freesound_faq):

| Role | Title | Author | Page | Length (s) | Licence |
|---|---|---|---|---|---|
| whoosh (low) | Little Whoosh 2 | ch_ase | https://freesound.org/people/ch_ase/sounds/423799/ | 3.31 | CC0 |
| whoosh (short) | whoosh_short_mid.wav | DJT4NN3R | https://freesound.org/people/DJT4NN3R/sounds/449996/ | 2.68 | CC0 |
| whoosh (low) | whoosh2.wav | anagar | https://freesound.org/people/anagar/sounds/267951/ | 2.46 | CC0 |
| whoosh (zoom) | Whoosh For Whip Zoom | BennettFilmTeacher | https://freesound.org/people/BennettFilmTeacher/sounds/486234/ | 2.13 | CC0 |
| swoosh (logo) | Swoosh FX Medium.wav | MasterEngine | https://freesound.org/people/MasterEngine/sounds/418007/ | 7.87 | CC0 |
| swish (text) | swoosh-1.mp3 | lesaucisson | https://freesound.org/people/lesaucisson/sounds/585257/ | 0.45 | CC0 |
| pop | Pop sound | deraj | https://freesound.org/people/deraj/sounds/202230/ | 0.65 | CC0 |
| pop | Pop 9 | D.S.G. | https://freesound.org/people/D.S.G./sounds/328119/ | 0.092 | CC0 |
| click | Mouse Click Sound.mp3 | Pixeliota | https://freesound.org/people/Pixeliota/sounds/678248/ | 1.24 | CC0 |
| click | mouse-click-double-00.flac | pbimal | https://freesound.org/people/pbimal/sounds/534104/ | 0.47 | CC0 |
| typing | Mechanical Keyboard Typing (Treble Version) | stu556 | https://freesound.org/people/stu556/sounds/450282/ | 183 | CC0 |
| shutter | Contarex camera shutter.wav | Tonik1105 | https://freesound.org/people/Tonik1105/sounds/520684/ | 2.3 | CC0 |
| sub | Sub Rush 1 | JarredGibb | https://freesound.org/people/JarredGibb/sounds/263892/ | 3.38 | CC0 |
| boom | Bass Boom | LordHannes | https://freesound.org/people/LordHannes/sounds/268084/ | 10.35 | CC0 |
| riser (short) | Riser sound effect short.wav | syntheffects | https://freesound.org/people/syntheffects/sounds/685256/ | 3.05 | CC0 |
| riser (long) | riser 3.wav | reathance | https://freesound.org/people/reathance/sounds/503818/ | 19.9 | CC0 |
| reverse cymbal | Reverse Crash Cymbal Projection | deleted_user_7146007 | https://freesound.org/people/deleted_user_7146007/sounds/383903/ | 8.92 | CC0 |
| reverse cymbal | cymbal-reversed-glassy-resonance.wav | burnttoys | https://freesound.org/people/burnttoys/sounds/9523/ | 3.16 | CC0 |
| ding | bell ding 1.wav | 5ro4 | https://freesound.org/people/5ro4/sounds/611113/ | 2.52 | CC0 |
| ding | Ding.wav | chennes | https://freesound.org/people/chennes/sounds/376807/ | 1.11 | CC0 |
| glitch | glitched sound 1.wav | Elnosos | https://freesound.org/people/Elnosos/sounds/424375/ | 0.64 | CC0 |
| glitch | Glitch Noise 1 | Flying_Deer_Fx | https://freesound.org/people/Flying_Deer_Fx/sounds/369145/ | 1.57 | CC0 |
| paper | paper_double.wav | XTYL33 | https://freesound.org/people/XTYL33/sounds/68224/ | 1.09 | CC0 |
| paper | Paper_Flip_01 | Rookster | https://freesound.org/people/Rookster/sounds/615337/ | 0.83 | CC0 |
| cash register | Cash Register Purchase | Zott820 | https://freesound.org/people/Zott820/sounds/209578/ | 2.75 | CC0 |

To use one with the engine, save it as `<role>__<name>.wav` with one of the engine's roles (whoosh, swish, impact, sub, shine, tick, riser, reverse): a ding is a `shine`, a pop or click a `tick`, a boom an `impact`.

Kenney packs, CC0 (kenney):

| Pack | Page | Files | Ship |
|---|---|---|---|
| Interface Sounds | https://kenney.nl/assets/interface-sounds | 100 | yes |
| Impact Sounds | https://kenney.nl/assets/impact-sounds | 130 | yes |
| UI Audio | https://kenney.nl/assets/ui-audio | 50 | optional |
| Digital Audio | https://kenney.nl/assets/digital-audio | 60 | optional |
| Casino Audio | https://kenney.nl/assets/casino-audio | 50 | optional (counter ticks, chips) |

### Never commit

Epidemic Sound, Artlist, Musicbed, Uppbeat, Pixabay, Zapsplat, the Sonniss GDC bundle, BBC Sound Effects, the YouTube Audio Library, creator asset packs sold on Gumroad, and CC BY tracks such as Kevin MacLeod's (move `tools/music_industrial_cinematic.mp3` out of the default assets, or behind an optional download with an attribution file). Epidemic downloads and the Sonniss GDC bundle (commercial use, no attribution, no redistribution, no AI training) may live in a gitignored local cache on the owner's machine (freesound_faq; kenney; sonniss; epidemic_terms; pixabay; zapsplat; bbc; incompetech).

### Music for paid ads

- **Recommended: Epidemic Sound Business**, $30 a month billed $360 a year, for brands under $10M revenue: social, websites and ads, 2 seats. Or Pro at $16.99 a month billed $203.88 a year for an individual professional; Creator at $9.99 excludes digital ads (epidemic_pricing). Its MCP server works in Claude Code (search, download, edit a recording to an exact length, search and download effects; an API key lasts 1 year; downloads need a paid plan), and every track comes in 4 stems (drums, bass, instruments, melody), so the melody can leave under speech (epidemic_mcp; epidemic_stems). Search brief: dark cinematic or ambient electronic, mysterious, serious, minor, 80 to 110 BPM, builds; then run the spectral gate and the track score on the candidates (house, anchored on the engine's 70 to 115 BPM).
- **Alternatives:** Artlist Music and SFX Pro, about $24.92 a month billed yearly (a 2023 article, may be stale), covers paid ads, though whether a company needs the Business plan is ambiguous (artlist). Uppbeat Pro at $14.99 or Business at $34.99 a month billed yearly; its own pages disagree on which tier covers paid ads (uppbeat).
- **Generated music:** license rather than generate by default. ElevenLabs Music (model music_v2_5, 3 s to 5 min, a composition plan per section) costs $0.15 per minute by its own page against $0.30 in a third-party guide, about $0.24 per 95 s; its Starter ($6), Creator ($22) and Pro ($99) plans are for individual use only, a company likely needs Scale at $299 a month (fewer than 10 employees), and there is no clearance warranty. Use it only if the owner confirms he qualifies (el_music).
- **Do not use:** MusicGen (its weights are CC-BY-NC 4.0) (musicgen); Stable Audio Open 1.0 and Small (the community licence covers only businesses under $1M annual revenue, with registration) (stability).
- **Experiment only:** ACE-Step (Apache-2.0, runs locally; real-time factor 2.27x on an M2 Max, about 26 s per minute of audio; `--bf16 false` on macOS; quality for ad beds unverified) (acestep).

## 7. The owner's ears

What the engine cannot judge, and only proxies exist for:

- whether the voice sounds like the speaker in a quiet room or "too enhanced" (watery, phasey, lispy); the proxies are the processing caps and DNSMOS SIG;
- whether residual wind, traffic or a warble after denoise can be heard;
- taste: whether the bed feels premium or like a free stock track, and whether it fits the brand's swagger;
- whether an effect's timbre feels cheesy, and whether a stat moment lands as a flex or as corny;
- whether drops feel intentional or like a glitch, and whether re-entries feel on the beat (bar alignment is measurable, the feel is not);
- intelligibility and comfort on a phone speaker with the bed under (V-M>120 is only a proxy);
- whether loudness feels even when a viewer unmutes the homepage player halfway through.

The blind A/B (house; the earlier VSL rounds used a blind A/B with 5 reviewers as the precedent, manifest):

- Clips of 10 to 15 s, the same section on both sides, matched in loudness to within 0.2 LU so the louder side cannot win.
- Random A and B labels; the key in ab/key.json, hidden from the page.
- One private review page per round with an A/B toggle per pair, buttons A, B and same, and a one-word reason; results saved to ab/results.json. At most 5 pairs per sitting.
- Listen on a phone speaker at 50 to 70% volume and on earbuds; laptop speakers are an extra check.
- Rounds: (1) the voice: the top two of the denoise shoot-out, plus a 12 dB against a 6 dB cap; (2) the bed level: body V-M 11 against 17 LU, then half the step toward the winner; (3) the dialect: Gadzhi against Nelk on the hook and the first reveal; (4) the reveal design (drop with shine and sub, counter ticks with a boom, riser with impact and sub); (5) the music: the current bed against two licensed candidates.
- Questions: Which one sounds like you talking in a quiet room, not a filter? Do you hear wind thumps or an underwater swish? Is any word hard to catch? Does the music feel expensive, or like a free YouTube track? Does the stat moment hit without feeling corny? Is any sound effect cheesy or too much? Does the ending feel finished?
- Closing the loop: each pick moves the matching rule halfway toward the winner, recorded with the date and the pair id; two rounds in a row of "same" lock that rule; every QC gate runs again after each change. The sound-director skill writes the change into that video's `sound.rules` first, never straight into `tools/studio/sound.py`.

## 8. Open questions

- Audio of Gadzhi's VSLs, paid ads and short reels; his microphone; whether he uses shutter or typing effects.
- Measured loudness and bed levels of Nelk and Hormozi content (no source measured them).
- Adobe's auto-duck defaults; craft numbers for duck pre-roll, hold and release; the figures in Torcoli et al. 2019.
- Whether DeepFilterNet exposes an attenuation-limit flag (this spec mixes the dry signal back instead).
- Whether Industrial Cinematic itself is widely recognised.
- Epidemic's effects redistribution wording in its full terms (the spec never commits Epidemic files either way).
- Artlist Pro or Business for a company; incompetech's paid licence price; YouTube Audio Library rights off YouTube.

## 9. Sources

| Key | Source |
|---|---|
| iman_promo | Iman Gadzhi upload, https://www.youtube.com/watch?v=YZ6OyZKrRh8; video 2026-10-12; measured 2026-11-02 (demucs 4.1.0 htdemucs two-stem separation, ffmpeg 6.1.1 ebur128, faster-whisper 1.2.1 word alignment) |
| iman_tutorial | https://www.youtube.com/watch?v=wtDDjBOfTZo; video 2026-07-22; first 6 minutes measured 2026-11-02 |
| iman_dark | https://www.youtube.com/watch?v=O6DrQJ5OOlU; video 2026-04-01; measured 2026-11-02 |
| iman_2023 | https://www.youtube.com/watch?v=3xC-JZzEeic; video about 2023 (exact date unverified); measured 2026-11-02 |
| iman_4vid | the four measurements above combined (band ranges, L/R correlation, events per minute); 2026-11-02 |
| behindit | Behind It, "Behind Editing for Iman Gadzhi", https://www.youtube.com/watch?v=Chr2j89aGAg; 2024-07-16 |
| validation | Validation, "How to make Videos like Iman Gadzhi", https://www.youtube.com/watch?v=CJoWIbI3R54; 2024-01-15 |
| yoar7 | yoar7, "How To Find THE BEST Background Music EASILY (Like Iman Gadzhi)", https://www.youtube.com/watch?v=ah5Akj69TPU; 2025-08-10 |
| visclub | Visualizers Club, https://www.youtube.com/watch?v=hcJXfR0Ef0g; 2024-02-19 |
| joseph_sd | Joseph, Video Editing, "Master Viral Sound Design for Short-Form Content!", https://www.youtube.com/watch?v=HqPDRa7i97s; 2024-10-20 |
| jackcole_nelk | Jack Cole, "How to Edit Videos Like NELK", https://www.youtube.com/watch?v=n3FS2en3HdE; 2020-07-21 |
| flaunt_nelk | Flaunt profile of the Nelk editor Austin Ermes, https://www.flaunt.com/blog/austin-ermes; about 2021-02 |
| erv_hormozi | Erv Animations, "I Studied Alex Hormozi's Editing...", https://www.youtube.com/watch?v=jLR0G0WmPss; 2026-03-13 |
| hormozi_ig | Hormozi post https://www.instagram.com/p/C6Smf9iLWtY/ (verbatim embed at https://nowbam.com/why-every-agent-needs-to-pay-attention-to-alex-hormozis-content-shift/); late April 2024 |
| hormozi_comments | YouTube comments on https://www.youtube.com/watch?v=q9OmYf_IlQ0; video 2025-04-15; read 2026-11-02 |
| umbrella_bed | https://umbrellacreators.com/blog/background-music-volume-under-voiceover; 2026-09-26 |
| umbrella_loud | https://umbrellacreators.com/blog/youtube-loudness-lufs-study-2026; 2026-09-27, updated 2026-10-15 |
| umbrella_dopamine | https://umbrellacreators.com/blog/dopamine-editing-vs-retention-editing; 2026-09-27 |
| adobe_duck | https://helpx.adobe.com/premiere/desktop/add-audio-effects/adjust-volume-and-levels/automatically-duck-audio.html; dB examples https://www.magnific.com/blog/how-to-use-auto-ducking-in-premiere-pro-for-clean-professional-audio/; accessed 2026-11-02 |
| newman2018 | Newman and Schwarz, "Good Sound, Good Research", Science Communication 40(2):246-257, https://journals.sagepub.com/doi/abs/10.1177/1075547018759345; 2018-04 |
| ebu_r128 | https://tech.ebu.ch/docs/r/r128.pdf; 2023-11 |
| ebu_r128s1 | https://tech.ebu.ch/docs/r/r128s1.pdf; V3, 2020-08 |
| ebu_r128s4 | https://tech.ebu.ch/docs/r/r128s4.pdf and https://tech.ebu.ch/docs/tech/tech3343.pdf; 2023-11 |
| ebu_tech3341_3342 | https://tech.ebu.ch/docs/tech/tech3341.pdf and https://tech.ebu.ch/docs/tech/tech3342.pdf; 2023 |
| spotify | https://support.spotify.com/us/artists/article/loudness-normalization/; fetched 2026-11-02 |
| acx | https://help.acx.com/s/article/acx-audio-submission-requirements; fetched 2026-11-02 |
| ffmpeg | ffmpeg 6.1.1 built-in docs, `ffmpeg -h filter=<name>` (sidechaincompress, deesser, adynamicequalizer, acrossover, ebur128, loudnorm, aphasemeter); checked 2026-11-02 |
| ffmpeg_carve_test | an acrossover plus sidechaincompress test on synthetic signals; 2026-11-02 |
| izotope | https://www.izotope.com/community/blog/how-to-eq-vocals; accessed 2026-11-02 |
| craft_unverified | craft conventions reported by the mix-targets research without a fetched primary source; unverified |
| deepfilternet | https://github.com/Rikorose/DeepFilterNet (v0.5.6, PyPI 2023-08-31) and https://pypi.org/pypi/deepfilterlib/json; checked 2026-11-02 |
| el_isolator | https://elevenlabs.io/docs/capabilities/voice-isolator and https://elevenlabs.io/pricing/api; 2026-11-02 |
| auphonic | https://auphonic.com/pricing, https://auphonic.com/help/algorithms/singletrack.html, https://auphonic.com/help/algorithms/multitrack.html; 2026-11-02 |
| brouhaha | https://github.com/marianne-m/brouhaha-vad (MIT; ASRU 2023) |
| dnsmos | https://pypi.org/project/speechmos/ (archived); NISQA https://github.com/gabrielmittag/NISQA (weights CC BY-NC-SA 4.0); 2026-11-02 |
| incompetech | https://incompetech.com/music/royalty-free/licenses/ and https://incompetech.com/music/royalty-free/faq.html; accessed 2026-11-02 |
| discoverpods | https://discoverpods.com/overused-royalty-free-songs/; 2020-07-29 |
| epidemic_pricing | https://www.epidemicsound.com/pricing/; cached 2026-11-01, read 2026-11-02 |
| epidemic_mcp | https://developers.epidemicsound.com/docs/mcp/ and https://www.epidemicsound.com/tools/mcp/; 2026-11-02 |
| epidemic_terms | https://www.epidemicsound.com/personal-subscription/ and https://www.epidemicsound.com/staticfiles/legacy/20/documents/SingleTrackLicensesV9.pdf; 2026-11-02 |
| epidemic_stems | https://www.epidemicsoundhelp.com/hc/en-us/articles/25921163391762-Download-the-music-in-stems-or-audio-layers; 2026-11-02 |
| epidemic_api | https://developers.epidemicsound.com/docs/soundtracking-with-llm/; 2026-11-02 |
| artlist | https://artlist.io/blog/artlist-pricing-and-plans-explained/; byline 2023-06-29, read 2026-11-02 |
| uppbeat | https://uppbeat.io/pricing and https://uppbeat.io/user-agreement; 2026-11-02 |
| el_music | https://elevenlabs.io/docs/capabilities/music, https://elevenlabs.io/pricing/api, https://elevenlabs.io/music-terms (updated 2026-10-09); conflicting price at https://developer.puter.com/tutorials/elevenlabs-api-pricing/; 2026-11-02 |
| stability | https://stability.ai/license and https://huggingface.co/stabilityai/stable-audio-open-small; 2026-11-02 |
| musicgen | https://huggingface.co/facebook/musicgen-small; 2026-11-02 |
| acestep | https://github.com/ace-step/ACE-Step; 2026-11-02 |
| freesound_faq | https://freesound.org/help/faq/ and https://freesound.org/docs/api/resources_apiv2.html (CC0 is the only licence safe for uncredited ads and for redistribution); 2026-11-02 |
| kenney | https://kenney.nl/support and https://kenney.nl/assets/category:Audio; 2026-11-02 |
| sonniss | https://sonniss.com/gdc-bundle-license/ (v2.0, effective 2026-08-27); 2026-11-02 |
| pixabay | https://pixabay.com/service/terms/ (updated 2026-10-20); 2026-11-02 |
| zapsplat | https://www.zapsplat.com/license-type/standard-license/ (updated 2026-05-08); 2026-11-02 |
| bbc | https://sound-effects.bbcrewind.co.uk/licensing; cached 2026-10-31 |
| kit_sound | this repo, `tools/studio/sound.py`; read 2026-11-02 |
| kit_voice | this repo, `tools/studio/voice.py`; read 2026-11-02 |
| kit_formats | this repo, `formats.json` (the vsl_hero checks); read 2026-11-02 |
| kit_sd | this repo, `skills/video/sound-director/SKILL.md` (the DNSMOS comparison on the test VSL, 2026-11-02) |
| manifest | the owner's VSL project notes (state manifest, owner feedback and earlier review rounds), private; numbers only; read 2026-11-02 |
| ic_measure | this repo's `tools/music_industrial_cinematic.mp3` (244.4 s), measured 2026-11-02 with band analysis and ffmpeg 6.1.1 ebur128 peak=true |
