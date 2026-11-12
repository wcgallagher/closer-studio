# VSL page blueprint (house standard)

The owner's standard for every VSL and VSL landing page (owner, 2026-11-12: "whenever we want to do it, we want it to be
built like this"). Reference build: Acquisition.com's Scaling Workshop page, www.acquisition.com/workshop-4b, read on
2026-11-12 from the live page, its stylesheets and the browser's computed styles. Every value below was measured, not
eyeballed. Copy their structure and system, never their words, photos or reviews.

The VSL video itself (section 6) was pulled from the page's own player stream on 2026-11-12, transcribed with the
kit's faster-whisper (small.en), and its cuts measured with ffmpeg scene detection. The full transcript is kept in the
owner's private repo for internal reference only.

## 1. Where the funnel leads

1. Paid and organic traffic lands on the page. The URL ends in `4b`, and two split-testing tools run on it (Convert
   Experiments and Mida), so this is one variant of a live test.
2. The VSL autoplays muted with burned-in captions and a "Your Video Is Playing / Click To Unmute" overlay (Vidalytics).
3. Every "Apply for a seat" button and every date card jumps to `#book` on the same page. The visitor never leaves.
4. `#book` is an embedded iClosed widget ("ACQ Scaling Workshop Meeting"): a short form first (name, email, phone),
   then a calendar. Copy above it: "Choose a slot for a short call with our team to see if you're a fit and confirm your seat."
5. The fit call sells the seat: $5,000, two days in person, 80 seats, travel not included. Address and arrival details
   come by email after the seat is confirmed. What iClosed shows after booking was not tested (no fake bookings).
6. Measurement on the page: HubSpot, Hyros (attribution), the TikTok pixel, Microsoft Clarity, heatmap.com, Cookiebot.

The model: a VSL page that sells a call, and a call that sells the offer. The page never takes money.

## 2. Section order (top to bottom, desktop heights at 1440 px)

| # | Section | Background | What it does |
|---|---|---|---|
| 0 | Top bar, about 40 px | near-black | Gold dot, then uppercase tracked line: offer, place, dates, "Dec sold out, Jan now open" |
| 1 | Hero (977 px) | dark radial gradient | Logo; gold-gradient qualifier callout ("$1M+ Business Owners:"); white outcome headline; VSL 640 x 360; gold button; star rating line; proof line (attendees, seats per event); one short paragraph |
| 2 | The problem (900) | cream | Big headline that names the problem as an identity ("You're still the best operator in your company. That's the problem."); "Typical symptoms:" and six symptoms in the viewer's words; a bold reframe line (the six are one problem) |
| 3 | The mechanism (1290) | sand | Eyebrow "THE FOUR SYSTEMS"; headline; four short videos; four numbered cards (01-04, gold numerals), each a system and its failure in one or two sentences |
| 4 | What it covers (760) | cream | Headline; seven check-mark lines, each an outcome, not a topic; photo grid |
| 5 | The exclusivity stat (248) | cream | One line: "Fewer than 1 in 20 businesses ever pass $1M a year." and who is in the room |
| 6 | The objection, named (505) | sand | The objection as a quoted eyebrow ("I can't be gone two days"); a headline that turns it ("Most founders who come here almost didn't."); a short paragraph that makes the objection the reason to come |
| 7 | The founders (1302) | dark radial gradient | Photo; authority in numbers (portfolio, exits, books, followers); a first-person founder letter with two short client stories and a handwritten-style signature |
| 8 | Dates and scarcity (425) | cream | Upcoming dates as cards: "Sold out / 0 seats left", "7 seats left", "Open"; price stated plainly |
| 9 | Who it's for (1192) | sand | Eyebrow; "Owners at your level, in industries like yours"; who it is not for; industry list with "+13 more" |
| 10 | Booking (`#book`) | sand | iClosed form and calendar, embedded |
| 11 | Where it happens (499) | cream | Venue photo and one paragraph |
| 12 | Reviews (1844) | sand | Eyebrow "DON'T TAKE OUR WORD FOR IT"; 50 verified Google reviews, each with a name and an industry; "Show all 50 reviews"; results disclaimer |
| 13 | FAQ (933) | cream | Accordion: who it's for, the main objections, what happens, what you leave with, how it differs, industry fit, price, where and when |
| 14 | Final CTA (438) | dark radial gradient | The hero headline as a question; three short lines; gold button; date cards again |

Sections alternate cream and sand, framed by three dark gradient sections (hero, founders, final CTA). The ask
appears in the hero, at the dates, at the booking widget and at the end.

## 3. Design tokens

Colors (computed):

| Token | Value | Use |
|---|---|---|
| ink | #131628 | headlines, card titles |
| body grey | #61636F (subhead grey #5A6473) | paragraphs on light |
| cream | #FBF8F1 | light sections |
| sand | #F4EEDF | alternate light sections |
| card border | #E3E8EE | cards, 1 px |
| hero gradient | radial-gradient(90% 70% at 50% 0%, #2A2418 0%, #141210 60%, #0B0B0C 100%) | hero, founders, final CTA |
| gold text gradient | linear-gradient(90deg, #F7DB8C, #D4A142 60%, #B9832A), clipped to text | the qualifier callout |
| gold button | linear-gradient(90deg, #F2CF74, #C9932F), text #141210 | every CTA |
| gold accent | #A87A1F | eyebrows, card numerals |
| bright gold | #F6B100 | stars |
| white 78% | rgba(255,255,255,.78) | paragraphs on dark |

Type: Poppins for everything (Google Fonts, weights 100-900); Homemade Apple, a handwritten script, for one accent
(the founder's signature).

| Element | Desktop | Mobile (390 px) |
|---|---|---|
| Qualifier callout | 70 px, 800, -1.5 px tracking, gold gradient | 40 px |
| Hero headline (h1) | 34 px, 800, line 1.2, -0.4 px, white | 21 px |
| Section headline (h2) | 44-52 px, 600, line about 1.12, -0.9 to -1.6 px tracking | 32 px |
| Short-section h2 | 32 px, 800 | 32 px |
| Body | 17 px, 400, line 1.65 | 17 px |
| Emphasis line | 17 px, 600, ink | 17 px |
| Eyebrow | 13 px, 600, uppercase, 1.56 px tracking, #A87A1F | same |
| Card numeral | 28 px, 600, #A87A1F | same |

Components:
- Button: gold gradient, 8 px radius, 18 px x 48 px padding, 17 px weight 600, shadow 0 10px 30px rgba(0,0,0,.18).
- Card: white, 1 px #E3E8EE border, 12 px radius, 20 px padding.
- Date card: white, 12 px radius, 28 px x 20 px padding; status line in caps ("7 SEATS LEFT").
- Sections: 110 px top padding on the big ones, 48-64 px on short ones; content about 1040 px wide; three-card
  grids collapse to one column under 820 px.
- VSL player: 640 x 360 on desktop, full width (343 x 193) on a phone, centered under the headline, above the first button.

## 4. Copy pattern

1. Call out the buyer by qualifier before anything else ("$1M+ Business Owners:").
2. Promise the end state in plain words ("Build a business that runs without you.").
3. Name the problem as who they are, then list the symptoms in their words, then say it is one problem with one fix.
4. Give the mechanism a number ("four systems") and show each with a short video and a numbered card.
5. List outcomes, not topics.
6. Use one exclusivity stat that flatters the reader for being there.
7. Say the main objection out loud in quotes, then turn it into the reason to act.
8. Authority comes as numbers, then a first-person letter with two short client stories.
9. Scarcity has to be real: sold-out dates, seats left, a plain price.
10. Say who it is for and who it is not.
11. Proof is volume: dozens of named, attributed reviews and a results disclaimer under them.
12. The FAQ answers objections, logistics and price.
13. Close by asking the hero headline as a question.

## 5. How the house uses it

- Agent-facing pages (Set More Annuities): callout the agent ("Life & mortgage protection agents:"); the mechanism is
  set or sell; the proof is the $2.6M with its attribution on file; the booking is the account signup or a call.
  Every number and claim still needs a source in the project's audit file, and every proof block carries its disclaimer.
- Client-facing pages: same skeleton; the house writing rules and the client-facing word bans still apply.
- The VSL inside the page follows `skills/video/vsl-builder` and `docs/EDITOR_RULEBOOK.md`; this blueprint decides the
  page around it.

## 6. The VSL video: script beats and edit

Measured: 7:21 long, 2,075 words, 282 words a minute (314 in the opening questions, 262-297 elsewhere), 156 shots,
median shot 2.4 s, about 21 cuts a minute (28 in the first minute, 7 in the last 21 seconds).

Beats (times from the video):

| Time | Beat | What happens |
|---|---|---|
| 0:00-0:26 | Hook: "Let me ask you a question." | Five symptom questions in the viewer's own words (vacation spent on the laptop, delegating feels risky, the team asks you everything, revenue if you got sick, guilt at work and at home) |
| 0:26-0:37 | Name the enemy | Gives the problem a name ("key man risk"), defines it in one line, and stacks three costs (can't scale, can't sell, feel trapped) |
| 0:37-0:51 | Authority plus reframe | "After hosting over a thousand businesses..."; the reframe: you don't own a business, you own a high-paying job |
| 0:51-1:23 | Stakes | When it bites (growth, a new product line, a sale); "This is something that I went through" |
| 1:23-1:33 | Analogy | The bridge: if you are the bridge, everyone falls in when you leave |
| 1:33-2:23 | Origin story as proof | He was the key man when selling his company; fixed it in two years to one meeting a week; sold for $46.2M; portfolio now $250M a year; same systems across industries, "probably a business like yours" |
| 2:23-2:35 | Fit | The four ways anything is sold, and they have worked with every one |
| 2:35-3:16 | Mechanism, numbered | The problem lives in four areas (marketing, sales, product, operations), each with an on-screen chapter number |
| 3:16-3:47 | Twist | The better you get, the worse it is for the business; the more places one person sits, the less sellable it is |
| 3:47-4:23 | Promise | It can be removed with a repeatable system; everyone asks "how do I stop being the bottleneck?"; there is a system for each of the four |
| 4:23-5:18 | Offer | What the workshop is, what it is not (no conference, no hype, capped room), and the deliverable (a 3 to 5 step plan with owners and timelines) |
| 5:18-5:48 | Future pace | "Imagine this": the business runs on systems, you step away and revenue flows; a business that works for you, not because of you |
| 5:48-6:15 | Cost of waiting | "You're building a very comfortable prison"; permission to say no; who comes (owners turning jobs into assets) |
| 6:15-6:37 | Urgency and the step | No perfect time, problems compound; book a call, reserve a seat before picking a date, fit checked both ways |
| 6:37-7:12 | Objections | A doctor analogy for waiting; the busy-season objection answered (fix it busy, breeze when it's quiet) |
| 7:12-7:21 | Close | "Book a call with my team, we'll see if it's a fit. And if it is, can't wait to meet you." |

The order: symptoms, named enemy, authority, stakes, analogy, origin proof, numbered mechanism, twist, promise, offer,
future pace, cost of waiting, the step, objections, close. The offer arrives at 4:23 (60% in), after the problem is
fully owned; the ask is a fit call, never a purchase.

Edit and look:
- One founder seated at a desk on a dark set (vertical light bars, the logo mark on the wall), two camera angles plus
  punch-ins, cut every 2-3 s.
- Captions on every line: small white text in a rounded purple box, lower third, centered, 3 to 6 words.
- Graphics are front-loaded: nearly all of them sit in the first 3:15 (animated keyword cards on navy, a hand-drawn
  whiteboard sketch for the named problem, B-roll with big gold numbers for proof, 3D words for the reframe, a simple
  animated diagram for the analogy, a white list card for industries, numbered chapter tags with progress dots for the
  four areas). From 4:00 to the end it is the founder on camera with captions only.
- The player autoplays muted with a click-to-unmute overlay, so the captions carry the first seconds.

How the house uses it: keep the beat order and the timing shape (offer near 60%, graphics in the first half, the
founder alone for the close), the 2-3 s cut rhythm, and captions on every line. Scripts are ours; every claim still
needs its source in the project's audit file.
