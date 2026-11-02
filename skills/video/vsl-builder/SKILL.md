---
name: vsl-builder
description: Builds a VSL or any scripted video from several raw takes. You lock the script as beats (which take, which words), assemble one selects file from them without re-transcribing, declare the graphics in one layers file anchored to spoken words (animated scenes, the opening lockup, chips, hand labels, a tinted moment, the end card, music drops), cut it with the format's rules, and judge it in a blind A/B against the last version. Use when a VSL or a homepage video is cut from more than one take, when someone says "re-edit the VSL", "move this line earlier", "use the other take for this line" or "cut it from the takes", or when cards need to land on words.
---

# VSL builder

A single take goes through `skills/video/longform-editor/SKILL.md`. This skill is for a script cut from several takes, with graphics that land on words. Read `skills/video/funnel-vsl/SKILL.md` for what goes in a VSL and `skills/sales/closer-mentality/SKILL.md` before choosing lines.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
```

The animated scenes need Node.js and Playwright's Chromium once: `bash install.sh --scenes`.

## 1. Lock the script as beats

Read every take's words first. A take with a word map already (a project that locked its words) uses it; otherwise the assemble step transcribes that take once and caches it. Then write the beats in script order, one range of one take each, in a spec file next to the project:

```json
{
 "takes": {"take1": {"video": "inbox/take1.mp4", "words": "frame_map/take1.json"},
           "take2": {"video": "inbox/take2.mp4"}},
 "beats": [
  {"beat": "HOOK",  "take": "take2", "from": "Life", "from_s": 0.0, "to": "business.", "to_s": 5.7},
  {"beat": "OFFER", "take": "take1", "from": "If", "from_s": 36.8, "to": "split.", "to_s": 42.4}
 ]
}
```

`from_s` and `to_s` are the approximate times of those words in that take, so the right occurrence is picked. A beat can be a whole sentence or a half: drop a phrase by ending one beat before it and starting the next after it. Only the speaker's own words, never a re-worded line; a caption is fixed by cutting audio, not by rewording.

## 2. Assemble

```bash
"$PY" "$KIT/tools/closer.py" assemble spec.json --out "$KIT/output/<job>/selects"
```

It writes `selects.mkv`, every beat in order and frame exact at the source resolution. Next to it go analysis.json (the words on the new clock, sentences, the face track, a hard cut at every take change) and transcript.txt. Beat starts are capitalised so the caption file reads as sentences. Nothing is transcribed again later: `longform` and `reel` reuse that analysis. A take change is a hard cut: no piece joins two takes, and the tracked camera snaps there.

## 3. Write the layers file

Every time in it is a word on the selects clock, read from transcript.txt:

| Anchor | Means |
|---|---|
| `"There@6.2"` | the word nearest that time, at its start |
| `"manage.@19.0:end"` | at the end of the word |
| `"Because@13.5-0.08"` | 80 ms before it (plus or minus seconds) |
| `"END"`, `"SPEECH_END+0.05"` | the end of the video, the last word |

The parts, all optional:

- `scenes`: animated cards from a scenes HTML file (`scenes_html`), each with `from`, `to` and `cues` (element name to anchor). `"layout": "overlay"` renders the card on a transparent background beside the speaker instead of full screen. `"cut_in": "hard"` or `"cut_out": "hard"` replaces the blur dissolve with a hard cut. A scene `to` `"END"` becomes the end card. Keep card content above the caption band (the bottom fifth of the frame) so captions never sit on a card's payoff.
- `lockup`: the opening glass card on the left, on screen from frame 0: eyebrow, headline (leaves at `head_until`), the proof number, its label and the name (leave at `until`).
- `captions`: `from` (start after the headline), `words` (chunk size), `plain_over_scenes` (no spoken-word highlight over a card), `off` (windows with no burned caption, for a card that already shows the words). One caption line is on screen at a time.
- `chips` (`at`, `text`, `hold` or `until`, `row`; `style` `quiet` for a calm one, `pointer` for the red pill that points at the page button).
- `hands`: labels that ride a tracked hand (a rows file of hand positions on the take's clock).
- `moments`: a tinted stretch (`saturation`) with an optional `card`: one line, or `{"big": ..., "label": ...}` to bring the opening proof back.
- `music` (`file`, `start`, `mute` windows), `sfx` (a riser into the ask), `kicks` (zoom kick and whoosh at section changes), `zoom` (hold a framing, for hand labels), `end_hold`.

Every number on a card comes from the project's audit file or the owner. Spoken-only numbers never go on a card or a chip.

## 4. Cut

```bash
"$PY" "$KIT/tools/closer.py" longform "$KIT/output/<job>/selects/selects.mkv" --out "$KIT/output/<job>/v1" \
  --brand sma --format vsl_hero --platform web_vsl --layers layers.json --preview
```

`vsl_hero` is the homepage video (about 100 s, 16:9, burned captions, music faint); a longer page VSL is `vsl_book_call`. `--preview` first; drop it for the delivery, and add `--crf 15` for the master. The scenes render once and are reused while their length and cues stay the same.

## 5. Judge it

Read report.md: every line PASS. Look at sheet.jpg and at frames on every card at phone size (360 px wide). Then a blind A/B: two cold reviewers or more get the same pack for the new cut and the last shipped one (contact sheets, frames, transcript, card list), labelled A and B only, and pick one with reasons (`skills/video/cold-review/SKILL.md`). Ship the winner after its low-effort fixes; log what changed and why.

## Rules

- The speaker's words only, in their order or a new one; never re-worded.
- No unsourced number on screen, ever; drop the spoken line if the caption would carry it.
- The face carries trust: keep full-screen cards to about half the runtime or less.
- Every card readable on a phone, or it is not on screen.
- Owner calls (a claim only the owner can confirm, a line that could mislead) wait for the owner; cut the safe version meanwhile.
