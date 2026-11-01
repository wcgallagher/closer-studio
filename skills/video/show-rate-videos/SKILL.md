---
name: show-rate-videos
description: The videos that get a booked call or a registered training to actually happen, and the order they go out in. The confirmation page pair (HOW at about 90 s, then WHY at 3 to 7 min), a matched case clip under them, reminder clips at 24 h and 1 h, and the no-show rescue clip inside the hour. Picks the format id, who is on camera, the length band, the one ask and the send time, cuts each with the engine, and names what to measure. Use when people book and do not show, when a confirmation page or a GoHighLevel reminder workflow needs video, when "show rate" or "no-shows" come up, or before the Set More Annuities Wednesday training.
---

# Show-rate videos

A booking is a promise not kept yet. These videos are for one person who already said yes: plain and short, from
the face they will meet.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
IN="$KIT/inbox"; J="$KIT/output/<job>"
"$PY" "$KIT/tools/closer.py" formats
```

The ids below live in `formats.json` at the kit root (without it the engine knows only its built-in ids and every
command below exits "unknown format"); reasoning and sources in `FORMATS.md` sections 5 and 7. The booking video
before this sequence is `vsl_book_call` (the registry's reading of "BVSL", unconfirmed with the owner), defined in
`FORMATS.md` section 5; `skills/video/vsl-producer/SKILL.md` covers the Set More Annuities website VSL build and
does not use the format ids. Voice per `skills/sales/closer-mentality/SKILL.md`: one ask per video, said once.

## 1. The sequence

| Moment | Format id | Band (min/ideal/max) | On camera | The one ask |
|---|---|---|---|---|
| After booking, top of the page | `confirmation_how` | 60/90/120 s | closer or host they will meet | add to calendar, reply to the text |
| Under the HOW | `confirmation_why` | 180/300/420 s | same person | the same ask, once, last 30 s |
| Under both | `testimonial_case_clip` | 60/150/240 s | a client in their spot | none; the page carries it |
| 24 h and 1 h before | `reminder_clip` | 30/60/90 s | same person, phone take | reply YES at 24 h; tap to join at 1 h |
| Inside 60 min of a miss | `noshow_recovery_clip` | 20/45/60 s | same person, one raw take | one rebook link, slots for 2 days |

Sends anchor to appointment start, never booking time. The 24 h clip goes only when the booking is 36 h or more
out; the 8 h text ("what do you want to cover?") and the 15 min link carry no video. Nothing sends after a
cancellation; SMS consent is captured at booking. Confirmation email and text go inside 2 minutes from a branded
sender, HOW link inside. SMA training: D-3, D-1, day-of, 1 h and 15 min with the join link; registration
open until start.

## 2. What each one says

**HOW (one take, 16:9).** 0:00 "Your call is tentatively scheduled" and who they will meet. 0:10 date, time, time
zone, the link; point at the Add to Calendar button and say press it now. 0:40 "Someone on my team will text you
in a minute. Reply so we know we have the right number." 1:05 point to the video below, one ask. Transcript:
"calendar" before 0:45, "text" or "reply" before 1:10.

**WHY (one take, title card per topic).** Recognition in their words inside 30 s. What happens on the call (0:30 to
1:30). The questions we will ask (1:30 to 2:30). What success looks like, and who this is not for (2:30 to 4:00).
One ask in the last 30 s. No price for Become The Closer.

**Reminder (phone, 9:16).** Name and face by 0:05. What we will cover and why it is worth their time. One thing to
prepare. The ask in the last 10 s, on the card too.

**Rescue (phone, 9:16, no cuts).** "We missed you" in the first 5 s. One reason to rebook, taken from their own
application answer. "Slots are open for the next two days." The link in the last 10 s. The words "you missed" and
"no-show" fail the clip (full list in `FORMATS.md`).

**Case clip.** Situation named by 0:10, steps before the result, a results-vary card on any specific figure, one
line to someone in the same spot, no host ask. Tag it by role or starting point so the page picks the nearest case.

## 3. Cut them

```bash
"$PY" "$KIT/tools/closer.py" longform "$IN/<take>" --out "$J" --brand btc --format confirmation_how \
  --platform web_vsl --pops off
"$PY" "$KIT/tools/closer.py" longform "$IN/<take>" --out "$J" --brand btc --format confirmation_why \
  --platform web_vsl --pops off --chapters "0:What happens on the call,90:The questions we ask,150:What success looks like"
"$PY" "$KIT/tools/closer.py" reel "$IN/<phone take>" --out "$J" --brand btc --platform ig_reels --format reminder_clip --camera static --cta "Reply YES"
"$PY" "$KIT/tools/closer.py" reel "$IN/<phone take>" --out "$J" --brand btc --platform ig_reels --format noshow_recovery_clip --camera static --cta "Grab a slot"
"$PY" "$KIT/tools/closer.py" cover "$J" --title "Before your call" --brand btc --out "$J/cover"
"$PY" "$KIT/tools/closer.py" review "$J"
```

- `--format` loads the band, `clean` captions (`skills/video/caption-styles/SKILL.md`), the spoken-plus-card CTA,
  no music and the filler rule (kept on the rescue clip). Outside the band: a warning, not a render. `--brand sma`
  for the training.
- Captions never sit on a face. One lower-third and one arrow on the HOW; only a name card on the phone clips. The
  retention clock in `EDITING_GRAMMAR.md` does not apply.
- Cover: the person they will meet, looking into the lens; thumbnail 1280x720 for the page poster, cover 1080x1920
  for the email GIF frame. No sound-on autoplay.
- `review` writes `<job>/report.md`. The keyword-by-time and word-list checks in `FORMATS.md` section 5 you read
  against `<job>/captions.srt` yourself, then `skills/video/cold-review/SKILL.md`.
- SMS needs the 9:16 file under 10 MB (`ls -l`); other sizes in `skills/video/platform-formatter/SKILL.md`. The
  engine refuses a hook or CTA with a banned word (`skills/brand/brand-kit/SKILL.md`); SMA client copy never names
  the product.

## 4. What to measure

Stamp showed or no-show on every slot first; a CRM that counts bookings has no show rate. Then, in order:

1. **Confirmation rate** on the post-booking text and the 24 h YES. Confirmed calls show at 90%+, unconfirmed at 15
   to 30%: this is the lever. Low means fix the text and the HOW, not the WHY.
2. **Show rate**: calls attended over calls booked. Reference lines: setter-booked 70 to 80%+; inbound ad bookings
   40 to 60%; B2B no-show median 13.5%. For a small operator on cold traffic to a live training, 21 to 34% is a
   planning assumption, not a measured line. Confirmed people who still miss point at the booking window (same-day
   misses near 7%, two weeks out 42 to 67%) and the WHY.
3. **Recovery rate** on the rescue clip: 30 to 50% inside the hour; 10 to 25% rebooked is the floor.
4. **Play rate** on the page. Low play means it reads as homework: make it the next step, not an attachment.

Elsewhere: Vidyard's own no-show rate fell from 13% to 9% in a month with a confirmation video, and SalesKick's page
and cadence took one offer from about 40% to past 68%. Vendor cases, not promises.

## 5. Open questions, never papered over

Closer or founder on camera: untested. WHY length: unpublished. Video by SMS: no A/B result (every video figure
above is email-delivered). GoHighLevel numbers: one implementer's builds. Wednesday 1 PM ET: no benchmark; keep the
slot and measure before deciding.
