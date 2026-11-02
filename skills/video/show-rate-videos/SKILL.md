---
name: show-rate-videos
description: The videos that get a booked call or a registered training to actually happen, and the order they go out in. The confirmation page pair (HOW at about 90 s, then WHY at 3 to 7 min), a matched case clip under them, reminder clips at 24 h and 1 h, and the no-show rescue clip inside the hour. Picks the format id, who is on camera, the length band, the one ask and the send time, cuts each with the engine, and names what to measure. Use when people book and do not show, when a confirmation page or a GoHighLevel reminder workflow needs video, when "show rate" or "no-shows" come up, or before the Set More Annuities Wednesday training.
---

# Show-rate videos

A booking is a promise not kept yet. These videos are for one person who already said yes: short and plain, from the
face they will meet on the call.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
IN="$KIT/inbox"; J="$KIT/output/<job>"
"$PY" "$KIT/tools/closer.py" formats
```

The table prints the 17 ids in `formats.json` at the kit root. The five below are among them; older names
(show_confirmation, show_reminder) still resolve. Reasoning and sources: `FORMATS.md` sections 5 and 7. The booking
video that comes before this sequence is `vsl_book_call` (older names vsl_short and bvsl resolve to it), covered in
`skills/video/funnel-vsl/SKILL.md`. Voice: `skills/sales/closer-mentality/SKILL.md`, one ask per video, said once.

## 1. The sequence

| Moment | Format id | Band (min/ideal/max) | On camera | The one ask |
|---|---|---|---|---|
| After booking, top of the page | `confirmation_how` | 60/90/120 s | the closer or host they will meet | add to calendar, reply to the text |
| Under the HOW | `confirmation_why` | 180/300/420 s | same person | the same ask, once, in the last 30 s |
| Under both | `testimonial_case_clip` | 60/150/240 s | a client in their spot | none; the page carries it |
| 24 h and 1 h before | `reminder_clip` | 30/60/90 s | same person, phone take | reply YES at 24 h; tap to join at 1 h |
| Inside 60 min of a miss | `noshow_recovery_clip` | 20/45/60 s | same person, one raw take | one rebook link, slots for 2 days |

Sends anchor to appointment start, never booking time. The 24 h clip goes only when the booking is 36 h or more
out. The 8 h text ("what do you want to cover?") and the 15 min link carry no video.

Quiet hours: nothing sends between 9 pm and 8 am in the contact's time zone, and a 1 h touch that would land inside
that window moves to 8 am. The text carries a link to the hosted clip, never the video file.

Nothing sends after a cancellation. SMS consent is captured at booking. Confirmation email and text go out inside 2
minutes from a branded sender, with the HOW link inside. SMA Wednesday training: D-3, D-1, day-of, 1 h and 15 min
with the join link; registration stays open until start.

## 2. What each one says

**HOW (one take, 16:9).** 0:00 "Your call is tentatively scheduled" and who they will meet. 0:10 date, time, time
zone, the link; point at the Add to Calendar button and say press it now. 0:40 "Someone on my team will text you
in a minute. Reply so we know we have the right number." 1:05 point to the video below, one ask. Transcript:
"calendar" before 0:45, "text" or "reply" before 1:10.

**WHY (one take, a title card per topic).** Recognition in their words inside 30 s. What happens on the call (0:30 to
1:30). The questions we will ask (1:30 to 2:30). What success looks like, and who this is not for (2:30 to 4:00).
One ask in the last 30 s. No price for Become The Closer.

**Reminder (phone, 9:16).** Name and face by 0:05. What we will cover and why it is worth their time. One thing to
bring. The ask in the last 10 s, on the card too.

**Rescue (phone, 9:16, no cuts).** "We missed you" in the first 5 s. One reason to rebook, taken from their own
application answer. "Slots are open for the next two days." The link in the last 10 s. The words "you missed" and
"no-show" fail the clip; `formats.json` carries the full list.

**Case clip.** Situation named by 0:10, the steps before the result, a results-vary card over any specific figure,
one line to someone in the same spot, no host ask. Tag it by role or starting point so the page picks the nearest
case.

## 3. Cut them

Chapter times count from `--start`; take them from `<job>/transcript.txt`, which the first run writes.

```bash
"$PY" "$KIT/tools/closer.py" longform "$IN/<how take>" --out "$J/how" --brand btc --format confirmation_how \
  --change-every 0 --cta "Add it to your calendar and reply to the text" --title "Before your call"
"$PY" "$KIT/tools/closer.py" longform "$IN/<why take>" --out "$J/why" --brand btc --format confirmation_why \
  --chapters "0:Before your call,30:What happens on the call,90:The questions we ask,150:What success looks like,270:One thing to do now" \
  --quotes "<the who-this-is-not-for sentence, word for word>" --cta "Add it to your calendar and reply to the text" --title "Before your call"
"$PY" "$KIT/tools/closer.py" longform "$IN/<client take>" --out "$J/case" --brand btc --format testimonial_case_clip \
  --broll "$IN/<folder of the client's own work>" --title "<their situation in 1 to 4 words>"
"$PY" "$KIT/tools/closer.py" reel "$IN/<phone take>" --out "$J/reminder" --brand btc --platform ig_reels --format reminder_clip --camera static --cta "Reply YES"
"$PY" "$KIT/tools/closer.py" reel "$IN/<phone take>" --out "$J/rescue" --brand btc --platform ig_reels --format noshow_recovery_clip --camera static --cta "Grab a slot"
"$PY" "$KIT/tools/closer.py" review "$J/how"
```

- `--format` loads the band, clean captions (`skills/video/caption-styles/SKILL.md`), the spoken-plus-card CTA, no
  music and the filler rule (cut on four of them, kept on the rescue clip). A take outside the band still renders:
  the engine prints the band and the review marks the length line FIX. Trim or re-shoot; do not ship it.
- `--cta` is the spoken ask's card. Leave it off and the card prints the brand's default line ("Take the closer
  quiz"), wrong on every one of these. The case clip has no card: the page carries the ask.
- The clock comes from the format, not from `EDITING_GRAMMAR.md`. The HOW is one take, so `--change-every 0` makes
  the review print "no layout cadence required". The WHY wants a layout change at least every 60 s: the topic cards
  and the quote card cover it, and a gap in the report means one more card from that stretch. The case clip changes
  every 10 s, which is why it needs the client's work in `--broll`. The phone clips are single takes (cadence 0),
  and the engine's punch-ins keep the 8 s framing check at PASS even with the fixed crop.
- The first chapter sits at 0, or the engine adds a "Start" placeholder and the review asks for a title written by a
  person. A quote card must be a sentence the person actually said.
- `--brand sma` for the Wednesday training. It is agent-facing, so no `--audience client`; that flag is for an
  agent's own clients and adds the product-name lint.
- ig_reels for the phone clips: the same 9:16 frame as the registry's ig_story, with a 180 s cap instead of 60 s, so a
  90 s reminder passes the platform check. The clip is hosted and linked, not posted.
- Captions never sit on a face. The HOW's lower-third and arrow, and the name card on the phone clips, are not engine
  features: add them after the cut. The page plays without sound-on autoplay.
- `longform` writes thumbnail.jpg (1280x720, the page poster) and cover.jpg (1080x1920, the email GIF frame) from
  `--title`; `cover "$J/how" --title "Before your call" --brand btc --out "$J/how/cover" --at <s>` redoes them from a
  chosen second. The frame: the person they will meet, looking into the lens.
- `review` writes `<job>/report.md` and sheet.jpg. Every line PASS. The keyword-by-time checks (HOW: "calendar"
  before 0:45, "text" or "reply" before 1:10; WHY: a "not for" sentence, topics in order) you read yourself in
  `<job>/captions.srt`. Then `skills/video/cold-review/SKILL.md` before anything goes on the page.
- A BTC never-word in the hook or the CTA stops the render, and so does one in a title; one in the captions gets a
  FIX line in the report (`skills/brand/brand-kit/SKILL.md`).

## 4. What to measure

Stamp showed or no-show on every slot first; a CRM that counts bookings has no show rate. Then, in order:

1. **Confirmation rate** on the post-booking text and the 24 h YES. Confirmed calls show at 90%+, unconfirmed at 15
   to 30%: this is the lever. Low means fix the text and the HOW, not the WHY.
2. **Show rate**: calls attended over calls booked. Reference lines: setter-booked 70 to 80%+; inbound ad bookings
   40 to 60%; B2B no-show median 13.5%; best in class 3.1%. For a small operator sending cold traffic to a live
   training, 21 to 34% is a planning assumption, not a measured line. Confirmed people who still miss point at the
   booking window (same-day misses near 7%, two weeks out 42 to 67%) and at the WHY.
3. **Recovery rate** on the rescue clip. 30 to 50% inside the hour is one GoHighLevel implementer's own figure; 10 to
   25% rebooked is the floor.
4. **Play rate** on the page. Low play means the video reads as homework, buried in a confirmation email that gets
   ignored. Make it the next step on the page, not an attachment.

Elsewhere: Vidyard's own no-show rate fell from 13% to 9% in a month with a confirmation video, and SalesKick's page
and cadence took one offer from about 40% to past 68%. Vendor cases, not promises.

## 5. Open questions, never papered over

Closer or founder on camera: untested. WHY length: unpublished. Video by SMS: no A/B result. Every video figure
above is email-delivered; the SMS figures (confirmation, rebooking) are text-only touches. GoHighLevel numbers: one
implementer's builds. Wednesday 1 PM ET: no benchmark; keep the slot and measure before deciding.

## Rules

- One ask per video, said once, by the person they will meet.
- No number on screen you cannot source. A specific result carries the results-vary card.
- The four BTC never-words stay out of every hook, CTA, title and caption.
- No reminder between 9 pm and 8 am in the contact's time zone. The text links to the hosted clip, never the file.
- Nothing sends after a cancellation.
