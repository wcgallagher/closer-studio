---
name: format-brain
description: The marketer's brain for Closer Studio. Takes the goal someone states (more reach, more booked calls, people showing up, a sales page video, a lesson for the community, an authority video), names the format id from FORMATS.md, writes its one-screen brief (length band, beats, hook, CTA, cover, platforms), gives the exact tools/closer.py command to run, and says what the review will check. Use when someone asks "what should I make" or "which format", names a funnel, a VSL or BVSL, show rate or no-shows, Skool, a YouTube video or an ad, drops a recording and asks what to do with it, or wants the command for a format they already picked.
---

# Format brain

What a video is for decides how it is cut. `FORMATS.md` holds the sourced numbers and the reasoning; the engine reads the same numbers from `formats.json` beside it at the kit root. Read `FORMATS.md` once per session, and `skills/sales/closer-mentality/SKILL.md` before you write any hook. You hand back four things: the format id, its brief, the command to run, and what the review will check.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
```

The table prints the 17 registry ids with the length band (min to max, ideal in brackets), caption style, safe profile, CTA policy and platforms. Quote the band it prints, never one from memory. Older ids still resolve (ad_reel, show_reminder, vsl_short, youtube_long, testimonial, show_confirmation, bvsl), but every brief and command uses the registry id.

## 1. Pick the format: in order, stop at the first that fits

**Q0. Brand.** `btc`: the four BTC never-words never appear; the engine exits on a hook, a CTA, a long-form title or a cover title that carries one, and flags one in captions at review. `sma`: the product name stays out of client-facing copy. Add `--audience client` when the viewer is an agent's own client and the engine lints it; agent-facing SMA pieces may name the product.

**Q1. The one action you want from the viewer.**

| They say | Next action | Format id |
|---|---|---|
| reach or follows, "just a reel" | send it or comment the keyword | `organic_reel`; from a long recording, `yt_authority` first, then its reels |
| an ad, paid clicks to the quiz or the account page | click | `paid_ad_reel` (9:16; always a 15 s cutdown too) or `paid_ad_feed` (4:5 and 1:1 for Meta feed). YouTube in-stream is `ad_instream_169` |
| a sales page video, "the VSL", "BVSL", the opt-in or quiz page | book or apply | `vsl_book_call` (warm cut 5 to 6 min, cold 7 to 9); a program purchase: `vsl_long` |
| the homepage video (about 100 s, above the fold) | open the account | `vsl_hero`; cut from several takes with `skills/video/vsl-builder/SKILL.md` |
| show-ups, "they book and ghost" | reply YES, add to calendar | `confirmation_how` (90 s); `confirmation_why` (3 to 7 min) under it; `reminder_clip` at 24 h and 1 h; `noshow_recovery_clip` inside the hour after a miss |
| Skool: a welcome, one skill, the weekly call, someone leaving | finish lesson one, attend, post a win, stay | `skool_welcome`, `skool_lesson`, `replay`, `skool_cancel_video` |
| proof | believe it | `testimonial_clip` (ads and proof blocks, under 90 s); `testimonial_case_clip` (the booked prospect, up to 4 min) |

BVSL is not a defined term in any source. `FORMATS.md` maps it to `vsl_book_call` and tags the job "confirm BVSL meaning with the owner". Say so when it comes up.

**Tie-breaker.** Two formats fit: the one closer to the money wins (page over feed, show-up over page).

## 2. The funnel map

| Step | Become The Closer | Set More Annuities |
|---|---|---|
| Discovery | `organic_reel` cut from `yt_authority` or phone takes; `yt_authority` weekly | `organic_reel`; `yt_authority` as agent-facing authority content |
| Paid | `paid_ad_reel` (30 s plus the 15 s cutdown) and `paid_ad_feed` on Meta, `ad_instream_169` on YouTube, all to the closer quiz | the same ids under Meta's Financial products and services special ad category, to the account page |
| Page | `vsl_book_call` on the quiz result page (warm cut 5 to 6 min; cold 7 to 9 when traffic lands direct) | `vsl_book_call` on the website page: open the account and register for the Wednesday 1 PM ET training |
| Booked, not shown | `confirmation_how` then `confirmation_why`; `testimonial_case_clip` under them; `reminder_clip` at 24 h and 1 h; `noshow_recovery_clip` inside the hour | `confirmation_how` and `confirmation_why` on the confirmation page; `reminder_clip` at D-3, D-1, day-of, 1 h and 15 min, the last two with the join link; registration stays open until start; nothing sends between 9 pm and 8 am in the contact's time zone |
| Sold or attended | `vsl_long` on the program page; `testimonial_clip` in its proof block | the live training is the source recording; `replay` (30 to 45 min cut) to Skool and the email list the same day, plus an unlisted YouTube copy with chapters |
| Community | `skool_welcome` in week one, `skool_lesson` per skill, `replay` of the weekly call, `skool_cancel_video` at the cancel step | `skool_welcome`; `skool_lesson` modules on setting retirement appointments; weekly `replay`; `testimonial_clip` from agent wins. No cancel video is mapped |
| Loop back | wins become `testimonial_clip` and `testimonial_case_clip`; call recordings feed `yt_authority` and `organic_reel` | not mapped in `FORMATS.md`; ask the owner before reusing the BTC loop |

## 3. Write the brief

One screen, in this order:

1. The format id, and why in one sentence.
2. The length band as the `formats` table prints it (min, ideal, max), and the window you propose inside it.
3. Beats with times, from the format's `structure` entry in `formats.json` (`FORMATS.md` section 5 has the reasoning).
4. The hook: four to seven words, the viewer's own sentence first. Offer two alternatives.
5. The CTA policy (none, end_card, in_band, spoken_plus_card) and the one line that carries it.
6. The cover. A reel cover is 420x654 with 1 to 4 words. A thumbnail is 1280x720 as `cover` writes it (YouTube recommends 3840x2160 with a minimum width of 640 px), with a title of 1 to 4 words and 1 or 2 faces. The engine's `--title` help says the same 1 to 4 words and does not check the count.
7. The platforms, as engine ids from the `platforms` table.
8. What the review will check (section 4).

## 4. Run the command

The `kind` column of the `formats` table decides the command: short goes to `reel`, long goes to `longform`.

```bash
# analyze first: the ranked windows and the transcript
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<file>" --out "$KIT/output/<job>"

# short formats (organic_reel, paid_ad_reel, paid_ad_feed, ad_instream_169, confirmation_how, reminder_clip,
# noshow_recovery_clip, skool_welcome, skool_cancel_video, testimonial_clip)
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/<file>" --out "$KIT/output/<job>" --start <s> --end <s> \
  --brand btc --format organic_reel --platform ig_reels,tiktok,yt_shorts --hook "Their sentence"
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/<call>" --out "$KIT/output/<job>" --auto 3 --brand btc --format organic_reel
# paid: add --safe ads --fillers cut --cta "Take the closer quiz"; the 15 s cutdown is a second run on a tighter window

# long formats (yt_authority, vsl_book_call, vsl_long, confirmation_why, skool_lesson, replay, testimonial_case_clip)
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/<file>" --out "$KIT/output/<job>" --brand btc --format yt_authority \
  --platform youtube --chapters "0:The setup,95:The mistake" --quotes "a line they said" --pops auto --title "Up to four words"
# a page VSL: --format vsl_book_call --platform web_vsl --fillers cut

# then the cover, the exports and the checks
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/<job>" --title "Up to four words" --brand btc --out "$KIT/output/<job>/cover"
"$PY" "$KIT/tools/closer.py" export "$KIT/output/<job>/<master>.mp4" --out "$KIT/output/<job>/exports" --platforms tiktok,yt_shorts
"$PY" "$KIT/tools/closer.py" review "$KIT/output/<job>"
```

`--format` loads the format's defaults: the length band, caption style, safe profile, CTA policy and fillers. `longform` also takes its music mode, hook deadline, layout cadence and default platform from the format; `reel` takes music only from `--music` or the brand file. Any flag overrides one field. `longform` writes the 16:9 master (punch-ins, keyword pops, chapter cards, quote cards and B-roll on the cadence) plus chapters.txt, captions.srt, thumbnail.jpg, cover.jpg and report.md. Its `--title` sets the thumbnail words; without it the thumbnail takes the first chapter title, and the `cover` step re-makes it with the real one.

Length. A window outside the band is refused at the brief step (`FORMATS.md` Q7): give the band back and ask for a new window before any render, because the engine does not refuse for you. If it renders anyway, `reel` (when `--format` was given) and `longform` both print a FIX on "length fits the format" in the review. Nothing hard-fails on length. Change the window, not the format.

The review. A reel checks: hook by 2.5 s; ends on the payoff; no static stretch over 8 s; length fits the platform; length fits the format; loudness on target; captions clear of the face; no banned words on screen; caption words to proofread. A long cut checks: opens by the format's hook deadline; ends on the payoff; a layout change on the cadence (or none required when the cadence is 0); no static stretch over 8 s; length fits the format; loudness on target; chapters written by a person; every quote found in the speech; no banned words in the speech; caption words to proofread.

Where the detail lives: the window and the hook, `skills/video/reel-editor/SKILL.md`; long cuts, `skills/video/longform-editor/SKILL.md`; show-rate pieces, `skills/video/show-rate-videos/SKILL.md`; Skool pieces, `skills/video/skool-content/SKILL.md`; page VSLs, `skills/video/funnel-vsl/SKILL.md` with `skills/video/vsl-producer/SKILL.md` for animated cutaways; captions, `skills/video/caption-styles/SKILL.md`; sizes and safe zones, `skills/video/platform-formatter/SKILL.md`; the cut, `skills/video/edit-grammar/SKILL.md` with `EDITING_GRAMMAR.md`; clickability, `skills/video/hooks-titles-covers/SKILL.md`; a new brand, `skills/brand/brand-kit/SKILL.md`. Anything client-facing or paid ends with `skills/video/cold-review/SKILL.md`.

## 5. When the goal is unclear

One question at a time, in this order, until a format is fixed: which brand; the one thing the viewer should do after watching; where it plays (feed, ad placement, page, email, SMS, Skool); warm or cold; already booked or not; who is on camera; the length budget. Guess none of them. "Make something good from this call" needs no question: analyze, then propose `yt_authority` plus its ranked `organic_reel` windows.

## 6. Hand it over

Say: the format id and why in one sentence; the brief; the command; after a render, the file name, the length, one sentence on the cut and two alternative hooks. Stop.

## Rules

- An income figure is never framed as the viewer's likely outcome; show the steps instead (Google and TikTok ad policy). "Most closers never see 350K. The skill they have today is their ceiling." is the BTC site's own line and names a ceiling, so it may open a BTC piece. "20+ agents, $3.8M placed in 2025" is the owner's SMA proof figure: a sourced proof line on agent-facing SMA pieces only; never a BTC line; never a promised outcome; under Meta's financial special ad category when paid.
- No number in a hook or a caption that the footage or the brand file cannot source.
- The four BTC never-words stay off a BTC piece. The product name stays out of SMA client-facing copy; agent-facing SMA copy may name it.
- No title card before the hook. One idea per reel; two ideas, two reels.
- The CTA is the one action from Q1, nothing else.
- A show-rate video is fronted by the person the prospect will meet, nobody else.
- No trial and no re-post of a reel this account already published.
- "Done" comes after the review passes and, for paid or client-facing work, after the cold review.
