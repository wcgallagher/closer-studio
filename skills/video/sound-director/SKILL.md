---
name: sound-director
description: The mix engineer's rules for the voice, the music bed, the sound effects and the final check, run by tools/studio/sound.py inside the longform command. Cleans the voice lightly (less is more), scores music candidates by measured traits, sets how far the voice sits over the music in each section, ducks the bed before each phrase starts, drops it for a line and brings it back on a bar, places sound effects by a dialect grammar (Gadzhi premium or Nelk energy) with levels and density budgets, each hit aligned to its frame, and writes every number to sound.json. Use when someone says "the music is too loud", "the voice sounds processed", "pick a track", "add sound effects", "make it sound like Gadzhi / Nelk", "fix the audio", or before mixing any VSL, ad or long-form video. Nothing here listens: it measures, and the owner picks the music by ear.
---

# Sound director

The rules are numbers in `tools/studio/sound.py` (`SOUND_RULES` and `SECTION_PRESETS`). The code is the source of truth: when this page and the code disagree, the code wins and this page gets fixed. Nothing in it listens. Every check is a measurement, so report results as "measured, not listened" and let the owner judge taste by ear.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
"$PY" -c "import librosa" 2>/dev/null || "$PY" -m pip install librosa
```

The music measurements (`track_profile`) import librosa (ISC licence). `install.sh` and `install.ps1` install it; the last line adds it only to a kit set up before they did. On a Mac or Linux, run these in Terminal. On Windows, run them in Git Bash or WSL: the middle `PY` fallback is the venv that `install.ps1` makes (that installer has not been run on a Windows machine yet).

## 1. Turn it on

The director runs inside `longform` when the layers file (`skills/video/vsl-builder/SKILL.md`, section 3) has a `sound` block with at least one key in it. An empty block is skipped and the older mix runs instead: the ffmpeg voice chain in `tools/studio/voice.py` (the one called over-processed) with a sidechain duck. Every time is a word anchor on the selects clock, as in the rest of the layers file.

`closer.py edit` writes a layers file with a `sound` block for you, so its preview runs the director. The block holds the format's sections and the dialect; `--sfx-dir` adds `sfx_dir`. That holds for the horizontal formats only (the web VSL and YouTube sizes): the vertical ones go to `reel`, which does not read the layers file yet.

```json
"music": {"file": "music/bed.mp3", "mute": [["You@8.58-0.1", "Pretty@15.15-0.1"]]},
"sound": {
  "dialect": "gadzhi",
  "sections": [
    {"name": "hook", "vm": 11, "p10": 5},
    {"name": "body", "from": "If@6.36", "vm": 14, "p10": 8},
    {"name": "cta", "from": "Finally@82.99", "vm": 12, "p10": 6}
  ],
  "land": "Now@43.79",
  "sfx_dir": "sfx"
},
"sfx": [{"event": "cta_riser", "at": "Now@91.07", "why": "into the ask"},
        {"event": "number_reveal", "at": "<word>@<s>", "why": "proof number lands"}]
```

| Key | What it does |
|---|---|
| `dialect` | `gadzhi` (the default) or `nelk`: which sound-effect grammar runs (section 5) |
| `sections` | `name` and `vm` are required. `from` is where a section starts; one without it starts at 0, so leave it off the first. Each section ends where the next begins, the last at the end of the video. `p10` defaults to `vm` minus 6. A section named exactly `cta` also gets the 2 dB lift |
| `land` | a word where the track should change section. The start bar of a long track is chosen so a section change lands near it. Not used with `music_enter` |
| `music_enter` | a word where the bed comes in. Before it the open is dry (unless `pre_roll` says otherwise), and the track starts on its strongest bar: the bar in its first 60% of bars whose next 4 bars are loudest against the 4 before it (a section change in the track counts extra) |
| `pre_roll`, `hole_s` | with `music_enter` only. `"pre_roll": "filtered"` plays the track's lead-in under the open, low-passed at 700 Hz and 6 dB down, then `hole_s` of silence (default 0.18 s) right before the entry. `"dry"`, the default, is silence |
| `sfx_dir` | a folder of recorded sounds (section 6), relative to the layers file |
| `rules` | overrides, for example `{"music": {"gap_lift_db": 5}}`. Keys inside a part such as `music` merge with the defaults one level deep, so a nested table such as `sfx.grammar` or `sfx.density` is replaced whole. To change one sound level, give the dialect's full table: `{"sfx": {"grammar": {"gadzhi": {...every event...}}}}` |
| `music.file`, `music.mute` | the bed and the drop windows. `music.file` is relative to the layers file, and `--music` on the command line wins. A window is `[from, to]` (the bed goes out 0.4 s before `from`) or `[from, to, lead]` (out `lead` seconds before it). `music.start` is ignored here: the director picks the start bar |
| `sfx` | events the cut cannot see by itself: `event` (a kind from section 5), `at`, `why`, optional `gain_db`. Write `event`, not the older `name`: an entry without `event` becomes a card-in whoosh, and a riser's end (not its start) lands on `at` |

Keep `--denoise chain` (the default) with a sound block. `--denoise deep` runs DeepFilterNet at full strength first, and then the director denoises again.

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/output/<job>/selects/selects.mkv" --out "$KIT/output/<job>/v1" \
  --brand btc --format vsl_hero --platform web_vsl --layers layers.json --preview
```

The job folder gets voice_raw.wav (the cut voice before the director touches it), voice.wav, sfx.wav, mix.wav, music.wav when there is a bed, and sound.json, which records every decision with its reason.

## 2. Pick the music

Licence before taste. A track or a sound library must allow the use it gets:

- Paid ads need a plan that names paid or digital ads. Several libraries' entry plans cover social posts and websites but not ads.
- A CC BY track needs its credit line wherever the video plays. The bed in `tools/music_industrial_cinematic.mp3` is CC BY 4.0: "Music: Industrial Cinematic by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0". A paid ad with no credit needs the composer's paid licence or another track. Very common stock tracks also carry other people's videos with them, so ask the owner whether a track sounds familiar.
- Chart songs need a sync licence. Not used.
- This kit is public. Only CC0 sound files (Freesound files marked CC0, the Kenney packs) may be committed. Files from paid libraries stay outside the kit folder: their terms forbid passing the files on.

Then measure the candidates. `score_track` ranks the files you give it as a bed under a talking head:

```bash
"$PY" -c "
import sys; sys.path.insert(0, sys.argv[1] + '/tools')
from studio import sound
for f in sys.argv[3:]:
    p = sound.track_profile(f); s, why = sound.score_track(p, float(sys.argv[2]))
    print(f'{s:+.2f}  {f}'); print('    ' + '; '.join(why))
" "$KIT" 95 music/*.mp3
```

`95` is the video's length in seconds; `music/*.mp3` stands for your candidate files. The points come from `SOUND_RULES["music"]["pick"]`:

| Measured trait | Points |
|---|---|
| tempo 70 to 115 BPM, or half of it inside that range | +2, otherwise -1 |
| voice-band share (spectrum in 1 to 4 kHz over everything above 60 Hz) at most 0.42 | +1 to +3, more the lower it is; over 0.42, -2 |
| minor mode | +0.8 |
| its second quarter 2 dB or more louder than its first (it builds) | up to +2 |
| shorter than 60% of the video | -1.5 (it will need looping) |
| its loudest bar more than 18 dB over its 20th-percentile bar | -1 (it pokes out of the bed) |
| spectral centroid over 3200 Hz | -1 (hiss and cymbals in the voice range) |

The engine picks a track by itself only in `closer.py edit ... --music-dir <folder>`: it scores every track in the folder this way, writes the best one into its layers file for the first preview, and lists the top five in plan.json `music_ranked`. Treat that as a shortlist, not a pick.

The score is measured, not listened. It says a track leaves room for words, not that it sounds expensive. Give the owner at least two tracks that pass the licence check, each with its score line, cut under the same 10 to 15 s of the video at the same loudness, and let them choose by ear.

## 3. The voice: less is more

What `voice_master` does, in order (`SOUND_RULES["voice"]`):

1. High-pass at 80 Hz, or at 110 Hz when more than 0.45 of the energy in the pauses sits under 150 Hz (wind, rumble).
2. Noise reduction against the speaker's own room tone (the median of the pauses), a decision-directed Wiener gain that never takes more than 12 dB off, so nothing goes watery. Steady tones above 150 Hz (a whine, a hum harmonic) that stand 8 dB or more over their neighbouring bins get notched by as much as they stand out, up to 18 dB.
3. Wind bursts: only the frames whose energy under 150 Hz jumps 8 dB over the voiced median get a low cut (a shelf up to 180 Hz), at most 12 dB.
4. Tonal balance toward a speech target curve in third-octave bands from 80 Hz to 12.5 kHz, applied at 50%: cuts up to 4 dB, boosts up to 2 dB, no boost from the 6.3 kHz band up.
5. De-essing only on frames where 4.5 to 10 kHz runs 6 dB hotter than usual against 1 to 4 kHz, at most 6 dB.
6. Breaths stay, 6 dB lower. A gap of 0.12 to 1.2 s between words counts as a breath when something in it stands about 9 dB over the room tone.
7. Each phrase (split at gaps of 0.25 s) moves 70% of the way to the median phrase loudness, at most 6 dB, before any compressor.
8. The voice is set to -20 LUFS, then a slow leveller (1.5:1 above -26 dB, 15 ms attack, 180 ms release) and a fast peak catcher (3:1 above -10 dB, 1 ms, 50 ms).
9. One static gain to -16 LUFS. Then every pause of 0.18 s or longer goes 4 dB down, and so does the room before the first word and after the last. No limiter on the voice stem.

Why so little: the owner called the old processing over-processed ("sounds too enhanced"). The ffmpeg chain (`VOICE` in `tools/studio/voice.py`) gates everything under 300 Hz between words and lifts 9 kHz by 1.5 dB, and the director's first rules took up to 18 dB of noise off and cut pauses 12 dB and breaths 10 dB. Every move now has a cap. On the kit's test VSL (about 95 s, phone audio, DNSMOS P.835, 2026-11-02) the director scored OVRL 2.66 against 2.63 for the raw take and 2.59 for the v8 cut's voice (the old chain). The background got cleaner (BAK 3.20 against 3.01 raw) but the voice itself lost a little (SIG 3.29 against 3.41 raw). So even this chain costs some character: when in doubt, lower a rule; never add a stage. Never put reverb, an exciter, saturation or a boost above 6 kHz on a phone voice.

The `voice` part of sound.json shows what ran: the high-pass, the tones notched, the wind frames, the EQ per band, the breaths and the phrases.

## 4. Music under the voice

V-M is the voice's momentary loudness (400 ms, BS.1770) minus the music's, on frames where a word plays. Each section has a target median (`vm`) and a floor for its worst 10% (`p10`). The engine steers each median to its target; the floor is only reported (section 7). The presets are in `SECTION_PRESETS`; the engine does not apply them by itself, so copy them into `sections`. `closer.py edit` writes its own (`DEFAULTS` in `tools/studio/edit.py`): the `vm` values below for vsl_hero and for both reel formats (paid and organic), 20 for YouTube and lessons, and each `p10` left at `vm` minus 6.

| Format | Section | vm (LU) | p10 floor (LU) |
|---|---|---|---|
| vsl_hero | hook (to the offer) | 11 | 5 |
| vsl_hero | body | 14 | 8 |
| vsl_hero | cta (the turn and the ask) | 12 | 6 |
| paid_ad | all | 12 | 6 |
| organic_reel | all | 16 | 9 |
| tutorial | all | 20 | 13 |
| story | all | 23 | 15 |

With no sections there is one section at 14 LU, floor 8. For scale, measured on public uploads (separated stems): a Gadzhi promo-style video ran the voice a median 9.9 LU over the bed and swelled the bed 10.2 LU in voice gaps; a Gadzhi tutorial ran 19.7 LU with almost no riding.

`music_stem` sets each section's bed gain, measures V-M, corrects once and measures again. Around that:

- A pocket at 300 Hz to 4 kHz: 2 dB down all the time, and while words play another 4 dB for a bright bed (its 1 to 4 kHz band over -15 dB), 2 dB for a medium one (-15 to -19 dB), nothing for a dark one.
- The ride leads the word: the bed starts down 0.2 s before a phrase and gets there in 0.15 s.
- It comes up only in pauses of 1.2 s or more: 6 dB (8 dB in the first 8 s), starting 0.25 s after the phrase, over 0.6 s. Shorter gaps hold, so nothing pumps. There is no sidechain compressor: its depth changes word to word and the bed breathes between words.
- The `cta` section rides 2 dB up. After the last word the bed rises 6 dB over 2 s (starting 0.2 s later), and the last 1.2 s fade out.

Fit and drops:

- The track is cut on bar lines. A long one (at least 2.5 s longer than the video) starts on a bar in its first 40%, chosen so a section change lands near `land` (with `music_enter`, on its strongest bar instead), and splices on a bar into its ending from its fourth-last bar line (40 ms equal-power crossfade), so it ends on its real ending. A short one plays from the top and repeats whole 4-bar phrases whose loudness matches across the splice.
- A track whose own ending fades (its last 4 bars more than 6 dB under its median bar) never fades under the ask: it stays at full level, extended with matched 4-bar phrases if needed, under the end card to the last frame, where the final fade (1.5 s, floored at -48 dB, never digital zero) takes it down. `ending` in the music rules: `auto` or `hold` (the default behaviour), `button` (stop on the downbeat after the last word and die away 60 dB over 2.4 s) or `own`. The fit line in sound.json says "holds at full level under the end card" when it does. History: in v9's first master Lord Knows' own fade took the bed from about -14 to -55 LUFS under the CTA; the button that replaced it left the end card silent, which 11 of 12 reviews in the second blind panel rejected and the rulebook counts as a BLOCK (VO-13). The review gate "no digital silence" now fails any run under -90 dBFS longer than 50 ms. It never restarts from zero. If 8 splices are not enough, or the track has too few bars to splice, the rest is silence.
- Each `music.mute` window drops the bed to -40 dB from 0.4 s before its first anchor (or its `lead`), with a 60 ms fade, so the line lands dry. The bed comes back on the next bar line the beat tracker found, if that bar is within 1.0 s of the window's end, and the dialect marks the return (`drop_return`). At most 3 drops; later ones are ignored.

## 5. Sound effects

Levels are in LU against the voice stem's integrated loudness, measured on each sound's loudest 400 ms. A sound that lands on a word goes 5 dB lower, except risers and reverses. "Dry" means no sound.

| Event (kind) | Gadzhi (premium, default) | Nelk (energy) |
|---|---|---|
| punch-in in the first 8 s (`punch_in_hook`) | whoosh -18 | whoosh -12 |
| punch-in later (`punch_in`) | dry | whoosh -12 |
| hard cut (`hard_cut`) | dry | swish -16 |
| card in (`card_in`) | whoosh -14 | whoosh -11 |
| card out (`card_out`) | dry | swish -16 |
| card element lands (`card_element`) | dry | tick -14 |
| chip (`chip`) | shine -22 | tick -14 |
| hand label (`hand_label`) | dry | tick -22 |
| section change (`section_change`) | reverse -16 | riser -10, impact -6 |
| number reveal (`number_reveal`) | shine -14, sub -10 | riser -8, impact -4, sub -8 |
| into the ask (`cta_riser`) | riser -12 | riser -8 |
| pointer (`pointer`) | tick -20 | tick -14 |
| end card (`end_card`) | shine -18 | impact -6, sub -10 |
| bed returns after a drop (`drop_return`) | reverse -18 | impact -8 |

Each sound's own hit point lands on the event's frame (`SOUND_RULES["sfx"]["align"]`):

| Role | What lands on the frame |
|---|---|
| whoosh | its loudest point |
| swish | its loudest point |
| reverse | its loudest point |
| riser | its end (it is cut there, dead) |
| impact | its start |
| sub | its start |
| shine | its start |
| tick | its start |

The cut makes these events by itself: card in and out, card elements, chips, the end card, section changes (at a take change when the layers file sets `take_change_kick`, and at each word in its `kicks` list), punch-ins and drop returns. Number reveals, CTA risers, pointers, hand labels and hard cuts come only from the layers `sfx` list (a pointer chip is logged as a plain chip).

Budgets (`SOUND_RULES["sfx"]["density"]`):

| Budget | Gadzhi | Nelk |
|---|---|---|
| events in the first 20 s | 8 | 14 |
| events in the 60 s around one, after the first 20 s | 4 | 12 |
| ticks within 5 s either side | 1 | 3 |
| risers per video | 1 | 3 |
| reverses per video | 3 | 4 |

An event closer than 0.35 s to one already kept is dropped. The planner keeps the most important first (`PRIORITY`: number reveal 6, CTA riser 5, section change 4, card in / end card / drop return 3, a hook punch-in 2, chip and pointer 1, everything else 0), and number reveals and CTA risers skip the 60 s budget. The hook punch-in's 2 counts only for a layers entry written as `punch_in_hook`: the cut's own punch-ins are sorted as plain punch-ins (0) and renamed after. Every dropped event is in sound.json `sfx.dropped` with its reason. A dry cut is a choice, not a gap: no sound on a cut that says nothing new.

## 6. Recorded sounds

The synthesized sounds are the fallback. Recorded ones read as real, so give the director a folder:

- Files named `<role>__<anything>.<ext>`, with a double `__` after the role and the role in lower case. Roles: whoosh, swish, impact, sub, shine, tick, riser, reverse. Extensions: wav, mp3, ogg, flac, m4a, aif, aiff. A file without `__` is skipped.
- Each file is measured once into index.json in the same folder: onset (the first point within 30 dB of its peak), peak, end (where it falls 20 dB under the peak for good), its loudest 400 ms and its length. It caches by file name, so delete index.json after replacing a file under the same name.
- One-shots only. A sound timed on its start (impact, sub, shine, tick, click) whose peak comes later than its role allows (`max_lead_s`: impact 0.6 s, sub 0.4, shine 0.9, tick and click 0.3) is a swell or a bed, not a hit: the library leaves it out and lists it in sound.json `sfx.library_rejected` with the reason. A sound timed on its peak (reverse, whoosh, swish) keeps at most 1.5, 1.2 or 0.8 s of build before it (`lead_trim_s`); the front is trimmed with a 0.15 s fade-in.
- Every sound stops a role-sized time after its hit (`tail_max_s`: click 0.3 s, tick 0.35, swish 0.8, whoosh 1.2, shine 1.8, impact and sub 2.0, reverse 0.3), and never later than 0.3 s past where it falls 20 dB under its peak, with a 0.25 s fade. Stock libraries mislabel long pieces: in v9 a 51 s "impact" droned under the end card and a 65 s "sub" peaked 40 s in.
- Files rotate per role. With one file per role the same sound plays every time, so keep two or more.
- A role with no file falls back to the synthesized sound, and sound.json `sfx.placed` shows `synth` as its file.

Measure a new folder and see what it holds (run it from the folder that holds the layers file, or put the sound folder's full path in place of `sfx`):

```bash
"$PY" -c "
import sys; sys.path.insert(0, sys.argv[1] + '/tools')
from studio import sound
print({k: len(v) for k, v in sound.Library(sys.argv[2]).items.items()})
" "$KIT" sfx
```

The licence rules of section 2 apply to every file: only CC0 goes in this repo.

## 7. Check it: measured, not listened

```bash
"$PY" -c "
import json, sys; r = json.load(open(sys.argv[1]))
print(json.dumps(r['qc'], indent=1))
for s in r.get('music', {}).get('sections', []): print(s)
" "$KIT/output/<job>/v1/sound.json"
```

| Number in sound.json | Want | Who checks it |
|---|---|---|
| `qc.voice_over_music_median_db`, `qc.voice_over_music_p5_db` | 9 or more, 3 or more (`music_ok`) | review: "voice clear of the music" (its text says "want >= 15 and >= 9"; the gate in the code is 9 and 3) |
| `qc.click_suspects` | 0 | review: "no clicks at the audio cuts" |
| `sfx.per_min` | 12 or fewer | review: "sound effects stay rare", the same for both dialects, so hold Gadzhi to its own budgets above |
| `music.sections[].vm_median` | within 2 LU of `target_vm` | you |
| `music.sections[].vm_p10` | at or over `p10_min` | you: nothing gates it |
| `qc.short_term_max_over_integrated_lu` | 5 or less | you |
| `qc.clipped_samples` | 0 | you |
| `qc.mix_lufs`, `qc.mix_true_peak_db` | for the record: the final encode sets loudness per platform | `skills/video/platform-formatter/SKILL.md` |

On the test VSL the section medians hit their targets exactly (11/14/12 LU), but the CTA's p10 came out at 3.0 against its floor of 6, and every check still passed. Read the sections yourself.

Then the ears. Say "measured, not listened" in the report and give the owner the choices: blind, 10 to 15 s clips of the same section at the same loudness so the louder side cannot win, labelled A and B only, on a phone speaker and on earbuds. Ask:

- Which one sounds like you talking in a quiet room, not a filter?
- Is any word hard to catch?
- Does the music feel expensive, or like a free YouTube track?
- Is any sound effect cheesy or too much?

Move the matching rule toward the winner in that video's `sound.rules`, not in `tools/studio/sound.py`.

## Rules

- Licence before taste: no track and no sound goes in until its licence covers the use.
- Report "measured, not listened". Never say a mix sounds good.
- Less processing wins. Lower a rule before you add a stage.
- The code's numbers are the rules. A change goes in `SOUND_RULES` or the layers file first, then on this page and in AUDIT.md.
