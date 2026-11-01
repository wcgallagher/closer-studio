---
name: format-brain
description: The marketer's brain for Closer Studio. Turns the goal someone states (more reach, more booked calls, people showing up, a sales page video, a lesson for the community, an authority video) into a format id from FORMATS.md with its one-screen brief (length, structure, hook, CTA, cover, platforms), and the exact tools/closer.py command to run. Use when someone asks "what should I make" or "which format", names a funnel, a VSL or BVSL, show rate or no-shows, Skool, a YouTube video or an ad, or drops a recording and asks what to do with it.
---

# Format brain

What a video is for decides how it is cut. `FORMATS.md` holds the sourced numbers; the engine reads them from `formats.json` at the kit root. Read it once per session, and `skills/sales/closer-mentality/SKILL.md` before any hook. The output: a format id with its brief, and the command to run.

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
```

## 1. Choose: in order, stop at the first format

**Q0. Brand.** `btc` (the four words the brand file bans never appear; section 6) or `sma` (the product name never appears in client-facing copy; the engine refuses a hook carrying it).

**Q1. The one action you want from the viewer.**

| They say | Next action | Format id in `FORMATS.md` | `--format` id built into the engine |
|---|---|---|---|
| reach or follows, "just a reel" | send it or comment the keyword | `organic_reel`; from a long recording, `yt_authority` first, then its reels | `organic_reel` (reel), `youtube_long` (longform) |
| an ad, paid clicks to the quiz or the account page | click | `paid_ad_reel` (9:16, plus a 15 s cutdown) or `paid_ad_feed` (4:5, 1:1); on YouTube in-stream, `ad_instream_169` | `ad_reel` with `--safe ads` |
| a sales page video, "the VSL", "BVSL", the opt-in or quiz page | book or apply | `vsl_book_call` (warm cut 5 to 6 min, cold 7 to 9); a program purchase: `vsl_long` | `vsl_short`, `vsl_long` (longform, `web_vsl`) |
| show-ups, "they book and ghost" | reply YES, add to calendar | `confirmation_how` (90 s) then `confirmation_why` (3 to 7 min); `reminder_clip` at 24 h and 1 h; `noshow_recovery_clip` inside the hour | `show_confirmation` (longform), `show_reminder` (reel) |
| Skool: a welcome, one skill, the weekly call, someone leaving | finish lesson one, attend, post a win, stay | `skool_welcome`, `skool_lesson`, `replay`, `skool_cancel_video` | the same (longform) except `skool_cancel_video`, which needs the registry |
| proof | believe it | `testimonial_clip` (ads, under 90 s); `testimonial_case_clip` (booked prospect, up to 4 min) | `testimonial` (reel) |

BVSL is not a defined term in any source; `FORMATS.md` maps it to `vsl_book_call` and tags the job "confirm BVSL meaning with the owner". Say so.

**Tie-breaker.** Two formats fit: the one closer to the money wins (page over feed, show-up over page).

Left-hand ids need `formats.json` at the kit root. Branch `closer-studio` at 0bf1b88 does not carry it, so until it ships the right-hand ids run on the engine's built-in bands, which are tighter than the registry's: `organic_reel` 15 to 60 s (ideal 30) built in, 15 to 180 s (60) in the registry; `show_reminder` 10 to 30 s against `reminder_clip` 30 to 90 s; `vsl_short` 180 to 600 s against `vsl_book_call` 240 to 720 s; `replay` 600 to 3600 s built in, 1800 to 2700 s in the registry. Without the file a 60 s reminder cut gets the note "60 s is over the Reminder clip maximum of 30 s". Quote the band the `formats` table prints, never one from memory.

## 2. The funnel map

| Step | Become The Closer | Set More Annuities |
|---|---|---|
| Discovery | `organic_reel` cut from `yt_authority`; one authority video a week | `organic_reel`; `yt_authority` is agent-facing |
| Paid | `paid_ad_reel` or `paid_ad_feed`, plus `ad_instream_169` on YouTube, to the closer quiz | the same under Meta's Financial products and services special ad category, to the account page |
| Page | `vsl_book_call` on the quiz result page | `vsl_book_call` on the website: open the account, register for the Wednesday 1 PM ET training |
| Booked, not shown | `confirmation_how`, `confirmation_why`, `testimonial_case_clip` under them, `reminder_clip`, `noshow_recovery_clip` | `confirmation_how` and `confirmation_why`; `reminder_clip` at D-3, D-1, day-of, 1 h and 15 min, with registration open until start |
| Sold or attended | `vsl_long` on the program page, `testimonial_clip` in its proof block | `replay` the same day (30 to 45 min cut) to Skool and the email list |
| Community | `skool_welcome`, `skool_lesson`, weekly `replay`, `skool_cancel_video` | `skool_welcome`, `skool_lesson` modules on setting retirement appointments, weekly `replay`, `testimonial_clip` from agent wins; no cancel video is mapped |
| Loop back | wins become `testimonial_clip`; calls feed `yt_authority` and the reels | not mapped in `FORMATS.md`; ask before reusing the BTC loop |

## 3. The brief

In this order: format id; length band (min and max, with the ideal, as the `formats` table prints it: the registry's when `formats.json` is at the kit root, the built-in band when it is not); beats with times; hook (four to seven words, the viewer's sentence first); CTA policy (none, end_card, in_band, spoken_plus_card); cover (reel 420x654 with 1 to 4 words; thumbnail 1280x720 as `cover` writes it, with a 2 to 4 word title and 1 or 2 faces; the engine's 2 to 4 sits inside Galloway's 1 to 4); platforms; the review's checks.

## 4. The command

```bash
# analyze first
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<file>" --out "$KIT/output/<job>"

# short: organic_reel, ad_reel, show_reminder, testimonial
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/<file>" --out "$KIT/output/<job>" --start <s> --end <s> \
  --brand btc --format organic_reel --platform ig_reels,tiktok,yt_shorts --hook "Their sentence"
"$PY" "$KIT/tools/closer.py" reel "$KIT/inbox/<call>" --out "$KIT/output/<job>" --auto 3 --brand btc --format organic_reel
# paid: --safe ads --fillers cut --cta "Take the closer quiz"; the 15 s cutdown is a second run

# long: youtube_long, vsl_short, vsl_long, skool_welcome, skool_lesson, show_confirmation, replay
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/<file>" --out "$KIT/output/<job>" --brand btc --format youtube_long \
  --platform youtube --chapters "0:The setup,95:The mistake" --quotes "a line" --pops auto
# a page VSL: --format vsl_short --platform web_vsl --fillers cut

# then the cover and the checks
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/<job>" --title "Two to four words" --brand btc --out "$KIT/output/<job>/cover"
"$PY" "$KIT/tools/closer.py" export "$KIT/output/<job>/<master>.mp4" --out "$KIT/output/<job>/exports" --platforms tiktok,yt_shorts
"$PY" "$KIT/tools/closer.py" review "$KIT/output/<job>"
```

`--format` loads the defaults (length band, caption style, safe zones, CTA policy, fillers); `longform` also takes the format's music mode, hook deadline, layout cadence and default platform, while `reel` takes music only from `--music` or the brand file. Flags override them. `longform` writes the 16:9 master (punch-ins, keyword pops, chapter cards and quote cards) plus chapters.txt, captions.srt, thumbnail.jpg, cover.jpg and report.md; the thumbnail title is left to `cover`. A window outside the band: do not run it; give the band and ask for a new window (`FORMATS.md` Q7 puts that refusal on the brief step, and the engine does not refuse for you). If it runs anyway, `reel` prints the band as a note and its review checks only the platform cap ("length fits the platform"), so the reel passes with the note on the console; `longform` carries the warning into its report and fails "length fits the format". Either way: change the window, not the format. Window and hook: `skills/video/reel-editor/SKILL.md`; captions: `skills/video/caption-styles/SKILL.md`; sizes and safe zones: `skills/video/platform-formatter/SKILL.md`; the cut: `skills/video/edit-grammar/SKILL.md` with `EDITING_GRAMMAR.md`; a new brand: `skills/brand/brand-kit/SKILL.md`; cutaways for a page VSL: `skills/video/vsl-producer/SKILL.md`. Anything client-facing or paid ends with `skills/video/cold-review/SKILL.md`.

## 5. When the goal is unclear

One question at a time, in this order, until a format is fixed: which brand; the one thing the viewer should do after watching; where it plays (feed, ad placement, page, email, SMS, Skool); warm or cold; already booked or not; who is on camera; the length budget. Guess none of them. "Make something good from this call" needs no question: analyze, then propose `yt_authority` plus its ranked `organic_reel` windows.

## 6. Never

- An income figure framed as a likely outcome; show the steps (Google and TikTok ad policy).
- A number in a hook or caption that the footage or the brand file cannot source.
- The four BTC words on a BTC piece; the product name in SMA client-facing copy.
- A title card before the hook; a second idea inside one reel.
- A CTA that is not the one action from Q1.
- A show-rate video fronted by anyone but the person the prospect will meet.
- A trial or re-post of a reel this account already published.
- "Done" before the review passes and, for paid or client-facing work, before the cold review.

## 7. Hand-over

Say: the format id and why in one sentence, the brief, the command, the file name and length, two alternative hooks. Stop.
