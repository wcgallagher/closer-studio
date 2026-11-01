# FORMATS.md: the house format guide

Date: 2026-10-31. Brands: Become The Closer (becomethecloser.com) and Set More Annuities (setmoreannuities.com). The engine reads `formats.json`; this file is the readable version with the reasoning. Every number below traces to a URL in the sources list or is marked house choice. `formats.json` sits beside this file at the kit root.

Two lint sets ride on every format. BTC: the words free, no cost, guarantee and guaranteed never appear. SMA: the product name never appears in client-facing copy (hooks, captions, cards, titles, descriptions, page lines); agent-facing marketing may name it. The engine applies that list only when a job runs with `--audience client`; Set More Annuities' own marketing is agent-facing and names the product.

BVSL is not a defined term in any source the research pack found. The nearest real usages are "book-a-call VSL" and "bridge VSL". The registry maps BVSL to `vsl_book_call` and tags the job "confirm BVSL meaning with the owner" until the owner says otherwise.

## 1. How to choose

A brief names a brand, a goal and a placement. Answer the questions in order; stop at the first format id.

**Q0. Brand?** BTC lint set or SMA lint set.

**Q1. The one action you want from the viewer?**
- Watch, share or follow, no click: Q2.
- Click an ad to the quiz or the account page: Q3.
- Book, apply or open the account from a page: Q4.
- Show up to something already booked: Q5.
- Learn or finish something inside Skool: Q6.
- Prove a result: `testimonial_clip` (ads and proof blocks, under 90 s) or `testimonial_case_clip` (page cut for the booked prospect, up to 4 min).

**Q2. Organic.** Source is a long recording (a call, a training, a sit-down): `yt_authority` for the 16:9 master, then `organic_reel` cuts from the ranked reel windows. Phone take: `organic_reel`. On Instagram a new hook goes out as a trial reel first.

**Q3. Paid. Placement?** Reels, Stories, TikTok in-feed, Shorts: `paid_ad_reel` plus the 15 s cutdown. Meta Feed 4:5 or 1:1, or a screen-plus-webcam demo ad: `paid_ad_feed`. YouTube skippable in-stream: `ad_instream_169` (Action cut 15 to 20 s, Consideration cut 2 to 3 min).

**Q4. Page. What is sold?** A call or an application (BTC quiz result page, opt-in thank-you page, SMA website page): `vsl_book_call`; warm audience (post-training, email list) gets the 5 to 6 min cut, cold gets 7 to 9. A program purchase needing mechanism and proof first: `vsl_long`. Registration for the SMA live training: `vsl_book_call` aimed at the account page, with `replay` as the nurture piece after each Wednesday.

**Q5. Show-up. Where does it play?** Confirmation page right after booking: `confirmation_how` (90 s) then `confirmation_why` (3 to 7 min), in that order. 24 h, morning-of or 1 h before: `reminder_clip`. Missed the slot: `noshow_recovery_clip` inside the hour.

**Q6. Skool.** Just joined: `skool_welcome`. One skill: `skool_lesson`. A recorded call: `replay` (same day, plus a Classroom page with timestamps). A member win: `testimonial_clip` into Wins, then back into ads and VSL proof. Leaving: `skool_cancel_video`.

**Q7. Who is on camera, and what is the length budget?** The show-rate formats need the person the prospect will meet (Vidyard). A brief that asks for a length outside the band gets the band back (min and max) before any render; if it renders anyway, the review fails the length check.

**Tie-breakers.** Two formats fit: the one closer to the money wins (page over feed, show-up over page). A question went unanswered: the engine asks it (brand, the one action, placement or page, audience temperature, already booked or not) rather than guessing.

## 2. Funnel map

### Become The Closer

| Step | Format | Viewer's next action |
|---|---|---|
| Discovery | `organic_reel` (cut from `yt_authority` or phone takes); `yt_authority` weekly | Send, comment keyword, profile visit |
| Paid acquisition | `paid_ad_reel` (30 s plus 15 s cutdown); `paid_ad_feed`; `ad_instream_169` | Click to the closer quiz |
| Quiz result page | `vsl_book_call` (warm cut 5 to 6 min; cold cut 7 to 9 min if traffic lands direct) | Book the call or apply |
| Booked, not shown | `confirmation_how` then `confirmation_why`; `testimonial_case_clip` under them; `reminder_clip` at 24 h and 1 h; `noshow_recovery_clip` inside the hour after a miss | Reply YES, add to calendar, show |
| Call to program | `vsl_long` on the sales or application page; `testimonial_clip` in its proof block | Buy or apply |
| Program delivery (Skool) | `skool_welcome` in week one; `skool_lesson` per skill; `replay` of the weekly call the same day; `skool_cancel_video` at the cancel step | Finish a lesson in week one, attend the call, post a win |
| Loop back | Wins become `testimonial_clip` and `testimonial_case_clip`; call recordings feed `yt_authority` and `organic_reel` | |

Income figures are never framed as likely outcomes; the steps are shown instead (Google and TikTok policy, cited in the ad formats).

### Set More Annuities

| Step | Format | Viewer's next action |
|---|---|---|
| Discovery | `organic_reel`; `yt_authority` (agent-facing authority content) | Send, comment keyword for the account link |
| Paid acquisition | `paid_ad_reel`, `paid_ad_feed`, `ad_instream_169` under Meta's Financial products and services special ad category for US delivery | Click to the account page |
| Website VSL page | `vsl_book_call` aimed at opening the account and registering for the Wednesday 1 PM ET training; timed CTA, text offer under the player, controls visible | Open the account, register |
| Registered, not attended | `confirmation_how` and `confirmation_why`; `reminder_clip` at D-3, D-1, day-of, 1 h and the 15-minute join link; registration open until start | Add to calendar, reply, join |
| Live training | Source recording for `replay` | Attend; book the retirement appointment process next step |
| Replay | `replay` (30 to 45 min cut, ask in Q1 and Q4) to Skool and the email list the same day; unlisted YouTube copy with chapters | Watch, then open the account or book |
| Community (Skool) | `skool_welcome`; `skool_lesson` modules on setting retirement appointments; weekly `replay`; `testimonial_clip` from agent wins | Finish lesson one in week one |

Wednesday 1 PM ET has no published benchmark. The nearest data points (Tuesday 51.7% live show-up, Livestorm; 2 PM 55%, Contrast; 3 PM 58%, Univid) are logged in the show-rate system for a later test, not acted on now.

## 3. Engine mapping

Built in `tools/studio/` (the `tools/closer.py` commands): `reel` cuts every short format for the 12 platform targets with ad and organic safe zones, the tracked YuNet camera, impact / clean / serif / boxed captions, the hook, pill and end cards, cover.jpg and captions.srt; `longform` cuts every long format at 16:9 with keyword pops, chapter and quote cards, B-roll on the format's cadence, chapters.txt and a thumbnail; `cover` builds a thumbnail or reel cover from a title; `export` re-frames a master for other platforms; `review` runs the checks (opens by the format's deadline, ends on the payoff, a layout change on the cadence, no static stretch over 8 s, length inside the format band, loudness, captions clear of the face, banned words, chapters written by a person, quotes found, words to proofread). `--format <id>` loads the band, caption style, safe profile, CTA policy, fillers, music mode, hook deadline and layout cadence from `formats.json`; a flag overrides one field at a time. `--audience client` switches on a brand's client-facing never-words.

Not built yet, with the format each serves:
- Timed-CTA marker: the button reveal time written to the page config from the escape-hatch or offer timestamp (`vsl_book_call`, `vsl_long`, `replay`).
- Disclaimer band: a specific-result detector that forces a results-vary card and keeps the bottom 40% clear. Today the editor adds the card by hand, and `--safe ads` keeps the platform's ad zone (35% of the frame on Reels and Shorts) clear (`testimonial_clip`, `testimonial_case_clip`, `paid_ad_reel`).
- Screen-plus-webcam split and the speaker cut for two-host recordings (`paid_ad_feed`, `skool_lesson`, `replay`).
- Policy lint for ad copy (income figures, personal attributes) beyond the brand never-words (`paid_ad_reel`, `paid_ad_feed`, `ad_instream_169`).
- Thumbnail checks: OCR word count, face count and brightness against a black background (`yt_authority`).
- FFMETADATA chapter embed; the closed-caption track is the captions.srt every job writes (`yt_authority`, `replay`).

Alias ids a brief may use: ad_reel = `paid_ad_reel`; show_confirmation = `confirmation_how` + `confirmation_why`; show_reminder = `reminder_clip`; vsl_short = `vsl_book_call`; youtube_long = `yt_authority`; testimonial = `testimonial_clip`.

## 4. What each registry entry stores

`id`, `name`, `goal`, `funnel_stage`, `kind` (short = 180 s or under, the Reels and Shorts cap; long = over 180 s), `platforms`, `length_s` (min, ideal, max), `captions` (impact, clean, serif, boxed, pops, none), `safe` (organic = the 9:16 Meta safe zone applied to every vertical target; ads = that zone plus the bottom-40% disclaimer rule and the policy lint), `cta` (none = the ask lives on the page or in the post; end_card = a card in the final seconds; in_band = a timed button or card inside the body; spoken_plus_card = the speaker says the ask and a card carries the same words), `hook_deadline_s`, `change_every_s` (0 = no scheduled visual change), `payoff_window_pct` (the slice of runtime where the hook's promise is delivered: the answer, the proof block, the offer), `structure` (beats with timing and purpose), `cover`, `music` (none, faint, bed), `fillers` (keep, cut), `checks` (pre-publish and post-publish), `sources`.

The viewer state line in each section below is the editor-facing brief: what the viewer is doing and feeling at that moment.

## 5. The formats

Full check text and the per-format URL lists live in `formats.json`; each section here gives the numbers, where they come from, and the beats.

### organic_reel (short, 9:16, 15 / 60 / 180 s)
Viewer state: thumb on the screen, mid-scroll, owes you nothing and will swipe inside 3 s.
Length: max 180 s from the Instagram and YouTube Shorts 3-minute caps; min 15 and ideal 60 are house choices informed by Buffer's TikTok data (over 60 s got 43.2% more reach than 30 to 60 s; Buffer calls length not make-or-break).
Beats: proposition as burned text plus voice by 0:03 (TikTok); hook complete by 0:06 (TikTok); one idea shown, with a quotable moment in the middle (Instagram ranks on reshare and watch-through predictions); one spoken ask plus a word card in the last 5 s (end placement is a house choice).
Captions impact in the upper-middle, outside the top 14%, bottom 35% and 6% sides (Meta safe zone, applied to all 9:16 as a house choice). Cut every 2 to 4 s and a visual change at least every 5 s after the hook (house). CTA: spoken plus card, no URL on screen. Cover 420x654 px, face or key words centered, 1 to 4 words (Instagram; word count house). Music faint under the voice, fillers cut.
Checks: length band; hook text by 3.0 s; safe zone; 720 px and 30 fps minimum; no watermark, border or majority-text frame; audio present; caption keywords first and at most 5 hashtags; originality; brand lint; 24 h read of watch time, likes per reach and sends per reach; trial reel for new hooks (metrics at 24 h, auto-share inside 72 h).

### paid_ad_reel (short, 9:16, 6 / 30 / 60 s)
Viewer state: did not ask for this, half-listening, will give you one recognisable sentence before deciding.
Length: TikTok policy 5 to 60 s, its guide 21 to 34 s best; Meta 6 to 15 s effective (Feed under 15, Stories under 10); Google under 60 s for Shorts ads. Ideal 30 is a house choice inside TikTok's band; always cut a 15 s version.
Beats: recognition hook plus brand mark by 0:03 (Meta; problem-first beat claim-first 9 of 12 in Green Frog's vendor tests); hook done by 0:06 (TikTok); steps and risk 0:06 to 0:20 (Google, TikTok policy); first ask by 25% of runtime (Wistia hosted-video data, a hypothesis); proof or founder line 0:20 to 0:26 (Motion: Founder 8.57%, Testimonial 6.57%); closing ask in the last 4 s with a specific line (TikTok).
Captions boxed mid-frame plus an SRT named filename.en_US.srt on the asset (Meta). Cut every 1.5 to 3 s, hook frame holds 3 s then a new visual every 3 to 5 s (house). CTA spoken plus card. Cover is the first frame. Music faint and unlicensed (Meta), fillers cut.
Checks: length and 15 s cutdown; ad safe zone with the bottom 40% clear under a disclaimer; brand by 3.0 s; SRT; no licensed music or effects; policy lint (no income figure, no you plus a financial attribute, steps spoken); SMA special ad category; landing headline match; primary text short enough to survive truncation (house); hook rate and hold rate against the account median; test cadence (Meta 10 per ad set over 4 days, TikTok 3 to 5 per ad group, Motion 4.7 a week for Finance small tier).

### paid_ad_feed (short, 4:5 and 1:1, 6 / 15 / 60 s)
Viewer state: scrolling a feed with the sound likely off, reading the first frame as a still.
Length: Meta says Feed video under 15 s performs best; max 60 is a house choice. Beats: brand and proposition by 0:03 (Meta); hook done by 0:05 (house); steps and one proof line 0:05 to 0:12; spoken ask with card 0:12 to 0:15.
Captions boxed, re-laid out for the frame with a 10% edge margin (house; no 4:5 safe zone is published). Change every 3 to 5 s (house). Cover: frame 0 with the face centered, derived through the tracked camera. Screen-plus-webcam demo ads split 700/380 px for 1:1 and 878/472 px for 4:5 (vidpipe). Music faint, fillers cut.
Checks: aspect exact; face inside the frame on every frame; proposition by 3.0 s; margin; webcam inset detection; policy lint, SRT, special ad category and landing headline match as the reel.

### ad_instream_169 (short, 16:9 and 1:1, 15 / 20 / 180 s)
Viewer state: waiting for the skip button, counting to five.
Length: Google's best practice is :15 to :20 for Awareness and Action and 2:00 to 3:00 for Consideration; views count only past 10 s; skip at 5 s. Beats: proposition by 0:03 (Meta rule as house practice); hook sentence ends before 0:05; steps and proof inside 10 s; spoken ask with card, headline 15 characters and CTA 10 characters or fewer (Google). The Consideration cut adds mechanism and proof between hook and ask.
Captions clean. Change every 3 to 5 s (house). Cover: frame 0, 1080p (Google). Music faint, fillers cut. Checks: aspect exact, no letterbox; hook by 5.0 s; proof inside 10 s; character caps; policy lint; brand lint.

### confirmation_how (short, 16:9, 60 / 90 / 120 s)
Viewer state: just booked, a little suspicious, wants to know what happens next and whether a real person is on the other end.
Length: SalesKick specifies a 90-second HOW video; Fluxi about 90 s; min and max house. Beats: "tentatively scheduled" in the first 10 s (SalesKick); logistics and an arrow to the Add to Calendar button 0:10 to 0:40 (SalesKick traced about 15% show-rate drops to Google's May 2023 invite change); "a team member will text you, reply so we have the right number" 0:40 to 1:05; point to the WHY video and give the one ask 1:05 to 1:30.
Captions clean. Single take, one lower-third and one arrow (house). CTA spoken plus card. Cover: the person they will meet, no sound-on autoplay (Vidyard, Fluxi). Music none, fillers cut. Checks: "calendar" before 0:45 and "text" or "reply" before 1:10; one CTA in the last 20 s; speaker is the closer or host; page has the tentative headline, the button and written steps (SalesKick); brand lint.

### confirmation_why (long, 16:9, 180 / 300 / 420 s)
Viewer state: booked and already drifting; needs a reason the call is worth an hour of a working day.
Length: no source publishes a WHY video length (open question); the band is a house choice set against Inflo's 5 to 6 minute warm cut. Beats: recognition inside 10 to 30 s (Fluxi); what happens on the call 0:30 to 1:30, the questions we will ask 1:30 to 2:30, what success looks like 2:30 to 4:00 (Inflo's three pre-call topics) with Fluxi's "who this is not for" filter; single ask in the last 30 s.
Captions clean, a title card per topic (house). CTA spoken plus card. Cover as confirmation_how. Music none, fillers cut. Checks: a "not for" sentence present; no BTC price; one CTA; topic order call, question, success in the transcript (house); brand lint.

### reminder_clip (short, 9:16 phone take, 30 / 60 / 90 s)
Viewer state: the call is tomorrow or in an hour; they half-forgot and need a face and a reason.
Length: WebinarKit's 24-hour email carries a 60 to 90 s personal video; Vidyard's scripts run 30 to 45 s. Beats: name and face 0:00 to 0:05; what we will cover 0:05 to 0:25, why it is worth their time 0:25 to 0:45, how to prepare 0:45 to 0:55 (Vidyard's pre-meeting script); one ask in the last 5 to 10 s (reply YES at 24 h, tap to join at 1 h).
Captions clean. No cuts beyond a name lower-third (house). CTA spoken plus card. Cover: the closer mid-sentence, used as the email GIF frame (WebinarKit). Music none, fillers cut. SMS carries a link to the hosted clip, not the file (house). Nothing sends between 9 pm and 8 am in the contact's time zone, so a 1 h touch that would land inside that window moves to 8 am (house, from the SMA outreach policy).
Checks: speaker is the rep or host; one CTA in the last 10 s; sends anchored to appointment start at 24 h, 1 h and 15 min (SalesKick; RevenueHero 24 h / 1 h / 30 min; HL Growth Partner); the 24 h touch only when the booking is 36 h or more out (SalesKick); SMA training reminders at D-3, D-1 and day-of (Livestorm's above-average teams) plus 1 h and 15 min with the join link (WebinarKit), registration open until start (Livestorm: 15.3% register on the day); nothing after a cancellation (AgentATM); SMS consent captured at booking (RevenueHero); brand lint.

### noshow_recovery_clip (short, 9:16 phone take, 20 / 45 / 60 s)
Viewer state: missed the slot, a bit embarrassed, ready to ghost unless the door stays open.
Length: house choice. Beats: no-guilt open 0:00 to 0:05 ("we missed you", HL Growth Partner); one reason to rebook tied to what they wrote on the application 0:05 to 0:25 (SalesKick); slots open for the next 2 days only 0:25 to 0:35 (SalesKick window; Focus Digital: same-day no-shows near 7%, two weeks out 42 to 67%); one-click rebook link in the last 10 s.
Captions clean, no cuts, fillers kept (house: speed over polish). CTA spoken plus link card. Music none. Why: HL Growth Partner reports 30 to 50% recovery when the message goes out within the hour; Vidyard's video follow-ups converted 63% of event no-shows to MQL.
Checks: fires within 60 minutes of the missed slot; no-show status stamped first (without it there is no show rate, Ziel Lab); word list passes "we missed you" and fails "you missed", "no-show", "wasted" (house); one link, 2-day window; not sent after a cancellation; brand lint.

### vsl_book_call (long, 16:9, 240 / 420 / 720 s)
Viewer state: opted in or finished the quiz, curious and guarded, deciding whether to give you a calendar slot.
Length: Inflo's rule is 6 to 9 min with 7 as the target, never under 4 and never over 12; warm audiences 5 to 6, cold 7 to 9; Palmer's short-form band is 3 to 10; Roezan's closers.io example runs about 5 min. Beats (Inflo timings): hook 0:00 to 0:30 (who it is for, the one result, a reason to stay, Vidalytics; open on the viewer's situation, Green Frog); problem 0:30 to 2:00 (Vidalytics: 80% of viewers watch the first 2 to 3 minutes); authority and proof 2:00 to 4:00 with the escape-hatch ask at about 2:30 to 3:00 ("if that is all you need to hear, book below", Roezan); objections out loud 4:00 to 5:30 (Digistore24); ask with a reason to act now and who it is not for 5:30 to 7:00 (Fluxi, price not revealed).
Captions clean plus one key-line card per section (VSL by Baran). Cutaways every 4 to 8 s, at most one per 12 s, none in the first 3 s or last 1 s, under 40% of runtime (SupoClip planner rules, borrowed). CTA in-band: the button reveals at the escape hatch and stays, controls visible, text offer under the player, one open-text qualifying question above the application (Vidalytics, Digistore24, Inflo). Cover: poster frame matching the page headline and the ad's first line; autoplay only with restart on unmute, never a pause lock (Vidalytics: pause lock 15% vs 30% engagement; restart version converted 49% better). Music none, fillers cut.
Checks: hook complete by 0:30; first ask between 2:00 and 3:30, final ask inside the last 90 s; no agitation stretch over 90 s (Green Frog); one CTA type; button time equals escape-hatch time; B-roll limits; brand lint and no income figure; post-launch fix the earliest retention cliff first (Digistore24).

### vsl_long (long, 16:9, 900 / 1500 / 2700 s)
Viewer state: considering a real purchase, wants the mechanism and the proof before anyone asks for money.
Length: Benson runs nothing under 15 min and his best run 30 to 40; Palmer's long-form band is 20 to 45; Vidalytics' six parts reach the CTA at 15:00. Ideal 25 min is a house pick. Beats (Vidalytics parts): hook 0:00 to 0:45 (Palmer: it lands in the first 5 to 15 s); problem and root cause 0:45 to 3:00; mechanism 3:00 to 7:00; proof 7:00 to 11:00 (testimonial clips here); offer and value stack 11:00 to 15:00 with the button at the offer (Benson 16:34, Vidalytics 16:45); objections out loud 15:00 to 18:00 (Digistore24, house placement); ask and terms 18:00 to end, one CTA repeated but singular. Text-on-screen variant: one sentence per slide, a three-word slide every 5 to 10 slides (Benson).
Captions clean on the presenter cut; test it against the plain text-on-screen cut (Vidalytics split: 68% vs 49% held at 0:35). Cut every 6 to 12 s with one visual per claim (VSL by Baran). CTA in-band. Cover: presenter or first slide line, headline matches the first spoken line. Music none, fillers cut.
Checks: six section markers in order; offer reveal between 11:00 and 17:00 and button time equal to it; objection block after the offer; slide rules on the text cut; brand lint, terms stated plainly; post-launch judge the reveal by sales not clicks (Vidalytics), 40% still watching at the CTA as the reference, and only 20% stay to the end of videos over 20 min (Vidyard) so the ask cannot wait.

### yt_authority (long, 16:9, 480 / 720 / 1200 s)
Viewer state: clicked a promise, will give you 30 seconds to prove the thumbnail was honest.
Length: vidIQ's benchmark case is a 6 to 9 min talking head at roughly 30% viewed; AIR gives a 30% median and 41% top quarter for 5 to 15 min; Wistia puts 5 to 30 min in the convert-or-nurture band. Ideal 12 min is a house pick. Beats: promise match 0:00 to 0:15 (vidIQ: value promise inside 15 s; YouTube's Intro metric reads survival at 30 s); stakes 0:15 to 0:30; show, do not tell 0:30 to 3:00 and a planned re-engagement near 3:00 (MrBeast memo); body with chapters of 2 to 5 min, keyword pops and a quote card, heavier explanation after minute 6 (memo, vidpipe); open-loop payoff in the last third (vidIQ); one-line bridge to a specific next video plus end screen in the last 20 s, never signal the ending earlier (YouTube, memo).
Captions: pops layer (1 to 4 words on the spoken word, one pop per 7 s, per `EDITING_GRAMMAR.md`; vidpipe's caption groups, split at 800 ms gaps with 8 words max, are the reference for the uploaded track) plus an uploaded closed-caption track; no burned full captions on the master. Cuts every 3 to 6 s in the first 3 min, looser after minute 6 (house). CTA: end screen; the quiz or account link sits in the description's first line and the pinned comment (house). Cover: thumbnail 1280x720 as `cover` writes it (YouTube recommends 3840x2160 with a minimum width of 640 px, under 2 MB from a phone); 3 elements, 1 or 2 faces, 1 to 4 words, bright, checked on black (Galloway, 2021); title under 100 characters, key words first (YouTube); 10 to 20 variants drafted, 3 tested in native A/B by watch time share. Music faint, fillers cut, silence removal capped at 20% (vidpipe).
Checks: first speech within 1.0 s; title words in the first 15 s of transcript; chapters at 00:00, at least 3, each 10 s or more, count = max(3, min(15, round(minutes / 3))); thumbnail OCR 4 words and 2 faces max; description 5,000 characters max; end screen last 5 to 20 s with 4 elements max; pops never over the face; brand lint; post-launch 60% at 0:30 (vidIQ), APV 30% median and 41% stretch (AIR), CTR against own videos with 2 to 10% as the platform band and high CTR with low AVD read as clickbait (YouTube); one upload a week (vidIQ cadence study).

### skool_welcome (short, 16:9 desk shot, 90 / 150 / 180 s)
Viewer state: just joined, inside a new interface, wants to be told where to start.
Length: Welter's spec is two to three minutes covering five items; min 90 is house. Beats: who I am and who this is for 0:00 to 0:30 (creator on camera, Skool plugin guidance); the tour 0:30 to 1:15; first lesson by name 1:15 to 1:45; the next call and that replays get posted 1:45 to 2:15; one step in the last 15 s (open lesson 1, comment on the Start Here post).
Captions none (Skool auto closed captions plus the Transcript addendum). Screen share with a camera bubble for the tour (house). CTA spoken plus a plain card. Cover: creator's face at the desk, eye contact (Guo). Music none, fillers cut. Why: a lesson finished in week one predicts completion, 78.2% vs 17.2% (Ruzuku).
Checks: transcript has "start here", "lesson", "call" (or "live") and "replay" by 2:15; one CTA in the last 20 s; native upload; face in 50% of frames (house); AutoDM asks one open and one closed question (Skool); brand lint.

### skool_lesson (long, 16:9 screen plus webcam, 120 / 360 / 720 s)
Viewer state: sat down to learn one thing, will skim and re-watch, quits if the page runs long.
Length: Guo's 6.9M-session data puts median engagement at most 6 min regardless of length, with viewers quitting before halfway past 9 min; UCSD says under 12 and never over 20; Ruzuku's concept video is under 12. Over 720 s the review fails the length check; split at natural breaks. Beats on a 6 min cut: objective in the first 15 s (UCSD: one micro-objective); concept 0:15 to about 3:30, drawn over slides for how-to (Guo: 1.5x to 2x longer attention than slides); worked example to end minus 60 s; action step of 10 to 15 minutes and "post the result" in the last 45 to 60 s (Ruzuku's lesson shape).
Captions none in the Classroom (auto closed captions, Transcript addendum, timestamps typed under the video make chapters); clean captions only on the 9:16 feed clip, split 65/35 at 1248 over 672 px (vidpipe). Camera cut-in at each slide or topic change, fillers and pauses over 1 s cut, energy up rather than slowed (Guo: faster, enthusiastic speakers engaged more; observed 48 to 254 wpm, mean 136). CTA: spoken action step plus a pinned discussion post (up to 12 pins per page, Skool). Cover: face plus module name; 1920x1080 is a house choice until Skool publishes a size. Music none.
Checks: one objective in the title and the first 15 s; timestamps when over 360 s (00:00 first, at least 3, each 10 s or more); action keyword in the last 60 s; speech 120 to 200 wpm (house band inside Guo's range); silence removal 20% max and bursts under 2 s removed (vidpipe, ai-video-editor); webcam inset found on 60% of sampled frames before the split (house threshold; vidpipe floor 30%); native upload, Loom comments and reactions off (Skool); drip or level gate after the Quick Start course (Level 2 at 5 points, Level 3 at 20, Skool); brand lint.

### skool_cancel_video (short, 16:9 desk shot, 45 / 75 / 120 s)
Viewer state: finger on the cancel button, half-decided, braced for a guilt trip.
Length: house choice. Beats: plain open 0:00 to 0:05 (they can leave); what a member loses, kept light, 0:05 to 0:40, naming the next call by date and one recent win (Skool plugin guidance; Hormozi churn checklist items on community calls and wins); one question 0:40 to 1:00 (what did you come for, did you get it); one ask in the last 15 s (reply, or come to the next call before deciding).
Captions none, no cuts, CTA spoken plus card, music none, fillers cut. Checks: transcript names the next call and a win; exactly one ask; pressure words fail (last chance, final, lose everything, only today; house) and the BTC words never appear; native upload; brand lint.

### replay (long, 16:9, 1800 / 2400 / 2700 s)
Viewer state: missed the live or came back for it; will scrub, so chapters and the asks must survive scrubbing.
Length: Wistia found replays of 31 to 45 min saw more than twice the engagement of replays under 30; Univid reports 86% of webinars run 30 to 60 min; ideal 40 is a house pick. Beats: cold open on the promise 0:00 to 0:30 (waiting room cut, house); teaching block 1 to about 20:00 with chapters every 2 to 5 min (vidpipe); a reset at 20:00 to 22:00 (Contrast: drop-off starts around minute 22); teaching block 2 to about 35:00 with quote cards; the ask in the first and last quarters (Wistia lead-form data for 30 to 60 min videos: quarters 1 and 4 at 50 to 51% CTR; for a 30 min cut, every quarter except the third at 53 to 55%); a Q&A tail with only the useful answers (house).
Captions none burned (closed-caption track), chapter card per block, two-host cut to the active speaker (interjections under 1.2 s ignored, cut 0.15 s before the next speaker's first word, snapped to scene cuts within 0.3 s, SupoClip rules; pyannote community-1 for diarization). Still stretches sped through rather than removed (auto-editor cookbook); total removal 20% max (vidpipe). CTA in-band: timed card plus spoken ask in Q1 and Q4, link in the post. Cover: the Skool event cover; YouTube copy gets a thumbnail per yt_authority. Music none, fillers cut.
Checks: first speech within 10 s; CTA keyword inside the Q1 and Q4 windows; chapters per YouTube's rules; posted the same day and the Skool Call recording downloaded within 14 days (Skool); brand lint on titles, cards, description and post text. Why the format exists: Skool's CEO reports replays get at least 10 times the viewers of the live session.

### testimonial_clip (short, 9:16 master, 20 / 45 / 90 s)
Viewer state: skeptical, scanning for someone like them and for the catch.
Length: house choice; ad use capped at 60 s by TikTok policy. Beats: the subject's own result or situation line by 0:03 (problem-first, Green Frog); before 0:03 to 0:15; what they did 0:15 to 0:35 (Google: show the legitimate steps; TikTok: say how the outcome is delivered); the result with one specific and a results-vary card over it 0:35 to 0:45 (Google's unreliable claims policy); the host format's ask in the last 5 s when standalone.
Captions clean with a name and role lower-third inside the safe zone; bottom 40% clear while the disclaimer is up (Meta). Cut every 3 to 6 s with the subject's own work as B-roll (house). CTA none (inherits the host). Cover: face plus 1 to 4 words of the result line. Music faint, fillers cut.
Checks: specific-result detector forces the disclaimer card; no income figure as typical (Google, TikTok); steps before the result; consent on file (house); lower-third by 0:05; brand lint, disclaimer wording without the BTC banned words; Motion's Testimonial 6.57% and Founder 8.57% hit rates are DTC reference only.

### testimonial_case_clip (long, 16:9, 60 / 150 / 240 s)
Viewer state: booked, nervous, looking for proof that someone in their exact spot came out ahead.
Length: house choice. Beats: situation match by 0:10 (Calendly: redirect to a relevant case study right after scheduling); before 0:10 to 0:40; the steps in order 0:40 to 2:00 (Google); what changed with the disclaimer card 2:00 to 3:20; one sentence to someone in the same spot in the last 30 s, no host ask (the page carries it).
Captions clean, change every 10 s (house), CTA none, cover is the face plus 1 to 4 words naming the situation, music none, fillers cut. Checks: match tag on the asset (role, market or starting point) so the page or sequence picks the nearest case for the prospect's application answers (house); disclaimer on specific results; steps before result; lower-third by 0:10; consent on file; placed as the next step on the page, not homework in an email (KS Advantage); brand lint.

## 6. Clickability: hooks, titles, thumbnails and cover frames

- Promise match: the title, the thumbnail or cover and the first spoken line say the same thing. YouTube's Intro metric reads survival at 30 s as proof of promise match; vidIQ's target is 60% at 0:30, strongest hooks over 65%.
- Thumbnail composition: at most 3 major elements, 1 or 2 faces, 1 to 4 words, a plain background, a bright image checked on a black phone screen (Galloway's 2021 thread: roughly 60 to 70% of mobile viewers used dark mode then). Tease the moment just before the action.
- Thumbnail spec: 16:9, 3840x2160 recommended with a minimum width of 640 px, under 2 MB when uploaded from a phone; 90% of best-performing videos use a custom thumbnail (YouTube). `cover` writes 1280x720, the floor under which YouTube's Test and compare downscales every variant (YouTube).
- Title: under 100 characters, key words first, episode numbers and branding last, limited caps and emoji; decide up front whether it is searchable or intriguing (YouTube).
- Packaging volume: 10 to 20 title and thumbnail variants per video, up to 3 in YouTube's native A/B (winner by watch time share, concurrent, up to two weeks, older videos first). Top creators spend about 30% of production time on ideation and packaging, small creators about 5% (Galloway via Colin and Samir).
- Reading CTR: half of all channels and videos sit between 2% and 10%; compare your own videos over time by traffic source, wait for a substantial number of impressions, and treat high CTR with low average view duration as clickbait (YouTube).
- Reel cover: 420x654 px (1:1.55), face or key words centered for the taller grid, cannot be edited after upload (Instagram).
- Short-form hook: proposition on screen by 3 s, hook complete by 6 s, on-screen text at 5 to 10 words per second (TikTok). YouTube Shorts report viewed vs swiped away; that number is the hook grade.
- Paid hooks: problem-first beat claim-first 9 of 12 times on cold traffic (Green Frog, vendor data). Motion's 2026 ranking puts concrete hooks (Newness, Sale Announcement, Price Anchor, Urgency, Announcement, Offer Only) at 6 to 11% hit rate against 4 to 8% averages; interrupt hooks (Confession, Contrarian, Warning) have lower hit rates and higher variance, and Motion names Finance as a vertical where Confession may feel off-brand. Keep one interrupt slot per batch for cold.
- Trial every new hook on Instagram: non-followers first, metrics at about 24 h, auto-share decided on views inside 72 h, limited reach for content already posted. Meta's 400,000-creator analysis: 40% posted more often after trials and 80% of those saw more non-follower reach.
- Judge a reel by watch time, likes per reach and sends per reach; likes matter slightly more for followers, sends slightly more for non-followers (Mosseri, January 2025).
- Original footage only: no watermark, no borders, no majority-text reels, no re-upload of a posted reel (Instagram). Since April 2026 accounts that mostly repost without meaningful edits lose recommendations for reels and for photo and carousel posts alike.
- Safe zone and brightness on 9:16: text outside the top 14%, bottom 35% and 6% sides (Meta); a bright hook frame, because dark frames vanish in dark mode (Galloway).
- Ad diagnostics: hook rate (3-second plays / impressions) and hold rate (ThruPlays / 3-second plays) as custom columns, compared to the account median; when hook rate is low change only the first 3 s (Triple Whale; Meta metric definitions).
- Front-load: 65% of viewers finish a video under 1 min and 20% finish one over 20 min; engagement peaks in the first quarter of runtime (Vidyard).
- Feed floor: 3 to 5 feed posts a week; moving up from 1 to 2 posts gives the largest per-post reach gain (+12% at 3 to 5, +18% at 6 to 9, +24% at 10 or more, Buffer). Reels win reach (36% more than carousels); carousels win engagement (12% more). Alternate them.
- Early distribution: almost 45% of recommended Instagram Reels are under one day old (Meta Q3 2026 call), so publish when the audience is online and answer comments in the first hours.
- Caption as page copy: keywords in the first line, up to 5 targeted hashtags, none in comments; public professional accounts are indexed by search engines (Instagram).

## 7. Show-rate system

Each line names its source; URLs are in the sources list.
- Booking window: the next 2 days, 3 at most, with 6 to 8 slots per closer per day; lower ad spend before widening it (SalesKick). Calendly advises 2 to 3 days inbound, 5 outbound. Same-day meetings no-show near 7%; two weeks out, 42 to 67% (Focus Digital).
- Qualify before the calendar loads: at least two fill-in questions, grade every application 1 to 4, pull show rate by grade, double-book grades under 65% (SalesKick: 47% of multiple-choice answers were false against real financial data). Poor qualification is the biggest single cause of no-shows (CallingAgency).
- Confirmation page: headline "Congrats, your call is tentatively scheduled", then `confirmation_how` and `confirmation_why`, written steps under both, one-click Add to Calendar links (SalesKick, whose case moved show rate from about 40% to past 68% with this page, the 2-day window and human SMS confirmation).
- Instant confirmation inside 2 minutes by email plus SMS from a branded sender (HL Growth Partner; RevenueHero's top performers at 5.5% no-show all white-label). The email carries a short video from the closer: Vidyard's own no-show rate fell from 13% to 9% in the first month, and its confirmation emails with video open at 70 to 77%.
- A human text that demands a reply right after booking, from a dedicated person who is not the closer, plain SMS not iMessage (SalesKick: confirmed calls show at 90%+, unconfirmed 15 to 30%; plain SMS lifted confirmation by a net 19%).
- Reminders anchored to appointment start: 24 h (`reminder_clip`, ask for YES), 8 h ("what do you want to cover?"), 1 h, 15 min with the link (SalesKick; RevenueHero's stack is 24 h, 1 h, 30 min). No reminder sends between 9 pm and 8 am in the contact's time zone; a touch that would land inside that window moves to 8 am (house, from the SMA outreach policy). Two reminders beat one in a 54,066-patient trial (4.4% missed vs 5.8% and 5.3%, Steiner); SMS cut non-attendance from 18.1% to 11.2% (Koshy). GHL builds report 60 to 75% confirmation on the 24-hour SMS and 3 to 7% no-shows (HL Growth Partner, self-reported).
- Pre-call content: a matched `testimonial_case_clip` (Calendly), an agenda from the closer's own address (a RevenueHero customer saw 50% show with an agenda email vs 20% with a bare invite), one objection-handling video, and a "who this is not for" filter in the VSL and the application (Fluxi). Positioned as the next step, not homework (KS Advantage). Inflo's pre-call breakout set claims show rates moving from 45 to 55% to 75 to 80%, a vendor claim with no dataset.
- Consent and stops: SMS consent checkbox at booking (RevenueHero); every reminder stops when a cancellation lands (AgentATM).
- Mark showed or no-show on every slot, then `noshow_recovery_clip` inside the hour (HL Growth Partner 30 to 50% recovery; Vidyard 63% of event no-shows to MQL; RevenueHero 10 to 25% rebooked). HubSpot counts bookings, not held meetings (Ziel Lab).
- SMA Wednesday 1 PM ET: registration open until start (15.3% register on the day, 49.7% in the final 7 days, Livestorm); half the promotion in the last week; 1 h and 15 min "starting now" email plus SMS (WebinarKit); personalised video reminders moved attendance from a 30 to 40% baseline to about 50% (Vidyard). Nearest day and hour data: Tuesday 51.7% (Livestorm), 2 PM 55% (Contrast), 3 PM 58% (Univid). Keep the slot, measure, then decide.
- Targets: setter-booked 70 to 80%+, inbound ad bookings 40 to 60% (SalesKick); B2B no-show median 13.5%, best in class 3.1% (RevenueHero); live webinar show-up 47.7% platform-wide (Livestorm) but 22% for hosts under $1M revenue (Demio via AInora, unverified at source), so 21 to 34% is the honest starting line for a small operator on cold traffic.
- Open questions the system must not paper over: closer vs founder on camera is untested (Vidyard uses the rep, KS Advantage the founder); the WHY video has no published length; SMS-delivered video has no A/B result (every video figure is email-delivered; the SMS figures are for text-only touches); GoHighLevel publishes no benchmark (the 3 to 7% figure is one implementer's builds); Wednesday 1 PM has no benchmark.

## 8. Skool content system

- Welcome: `skool_welcome` in the Pro onboarding plugin and a pinned Start Here post; the AutoDM arrives 1 to 5 minutes after joining and asks one open and one closed question (Skool plugin guidance; Welter).
- Activation KPI: a lesson finished in the first week, 78.2% completion vs 17.2% (Ruzuku, 1.3M enrollments).
- Lesson shape (`skool_lesson`): one micro-objective, concept video under 6 min as target, 12 as ceiling, 20 as hard stop; then a 10 to 15 minute action step and a 3-minute share prompt (Guo; UCSD; Ruzuku). Split long recordings at natural breaks.
- Hosting: native upload on either plan, 200 pages per course, unlimited courses; timestamps under the video make chapters; English closed captions generate automatically; add the Transcript addendum. Unlisted YouTube embeds need Allow Embedding; Loom embeds need comments and reactions off (Skool help).
- A pinned discussion under every lesson (12 pins per course page, 3 on the feed): lesson-level discussion completed at 50.9% vs 37.3%, assignments at 59.1% vs 42.4% (Ruzuku).
- Gating: a short Quick Start open to all, later pages dripped by days since joining, deeper courses behind Level 2 (5 points) or Level 3 (20 points); one point per like (Skool). Hormozi's churn list names time-released and level-released content and reducing overwhelm.
- Weekly call: a recurring Skool Call (short title, cover image, 30 min to 24 h), recorded, downloaded inside 14 days, posted the same day and uploaded to a Classroom page with timestamps (`replay`). Skool's CEO called scheduled, recorded calls the most underutilized feature; replays get at least 10 times the live viewers.
- Categories: well under the 10 cap. Wins, Questions, Accountability, Intros, plus admin-only Announcements sorted by newest (Skool's own example; Nick Saraev keeps categories simple with Wins first).
- Daily presence: short Loom answers (a Skool Games winner does 4 to 8 a day), answered in one batch per 24 hours; the best become Classroom pages.
- Production rhythm: one live recording session a week, long videos back to back then open Q&A, per-platform editors clipping from the pool; planning effort into the idea and packaging, then the key points, before recording (Hormozi, Skool Games Q3 2025).
- Barbell the formats: polish the long-form pieces, keep shorts and community-post videos raw and phone-to-face (Hormozi).
- Lesson style: desk shot, tight frame, eye contact; slides cut with the talking head; draw over slides for how-to; fast and warm delivery (Guo: the informal course out-engaged the studio course by roughly 2x at 6 to 12 min and 3x past 12).
- Captions: auto closed captions in the Classroom, burned captions only on social cuts (Voice Creator Pro; Rev). Students with normal hearing use captions heavily (SUNY OSCQR).
- Cancellation: `skool_cancel_video` (Skool plugin guidance; Hormozi churn list).
- Unverified, treat as house choices until checked: native upload size limit (claims range from 20 MB to 30 GB), cover and thumbnail pixel sizes, whether Skool Call recordings have a length cap, whether timestamp chapters work on community-post videos. Skool publishes no lesson-length or completion data of its own.

## 9. Sources

### Platform help and policy (Meta, Instagram, TikTok, Google, YouTube, Skool, Loom)
- https://ads.tiktok.com/help/article/creative-best-practices
- https://www.facebook.com/business/help/980593475366490
- https://about.instagram.com/blog/announcements/instagram-ranking-explained
- https://help.instagram.com/1038071743007909
- https://blog.youtube/news-and-events/tall-updates-coming-to-shorts/
- https://creators.instagram.com/blog/rewarding-original-creators-on-instagram
- https://help.instagram.com/1013292530224018
- https://about.instagram.com/blog/announcements/break-down-how-instagram-search-works
- https://support.google.com/youtube/answer/12942217?hl=en-GB&co=YOUTUBE._YTVideoType%3Dshorts
- https://www.facebook.com/business/ads-guide/update/video/instagram-reels
- https://www.facebook.com/business/help/188534925073536
- https://www.facebook.com/business/help/1675722002698686
- https://www.facebook.com/business/help/1792720544284355
- https://ads.tiktok.com/business/en/guides/video-advertising-guide
- https://ads.tiktok.com/resources/help/article/creative-best-practices
- https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-ad-format-and-functionality
- https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-deceptive-practices
- https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-financial-services
- https://business.google.com/us/ad-solutions/youtube-ads/shorts-ads/
- https://support.google.com/adspolicy/answer/10249050
- https://support.google.com/adspolicy/answer/15936857
- https://transparency.meta.com/policies/ad-standards/restricted-goods-services/financial-services/
- https://www.facebook.com/business/help/2220749868045706
- https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes/
- https://support.google.com/google-ads/answer/6055025
- https://support.google.com/google-ads/answer/13547298
- https://support.google.com/youtube/answer/9314415?hl=en
- https://support.google.com/youtube/answer/12340300?hl=en
- https://support.google.com/youtube/answer/72431?hl=en
- https://support.google.com/youtube/answer/16391400?hl=en
- https://support.google.com/youtube/answer/7628154?hl=en
- https://support.google.com/youtube/answer/9884579?hl=en
- https://support.google.com/youtube/answer/6388789?hl=en
- https://support.google.com/youtube/answer/57404?hl=en&co=GENIE.Platform%3DDesktop
- https://help.skool.com/article/176-how-to-use-plugins
- https://help.skool.com/article/58-video
- https://help.skool.com/article/166-what-is-classroom
- https://help.skool.com/article/38-how-do-to-pin-a-post
- https://help.skool.com/article/145-how-does-level-locked-courses-work
- https://help.skool.com/article/53-how-to-drip-the-content
- https://help.skool.com/article/225-how-to-add-loom-videos
- https://support.google.com/youtube/answer/9884579
- https://support.atlassian.com/loom/docs/use-looms-different-capture-modes/
- https://www.skool.com/acceleratoruniversity/churn-checklist-alex-hormozis-14-strategies
- https://help.skool.com/article/210-how-to-go-live-on-skool
- https://help.skool.com/article/146-how-to-create-an-event-in-your-group
- https://about.fb.com/news/2025/06/inspiring-creativity-that-brings-people-together/
- https://creators.instagram.com/blog/instagram-trial-reels
- https://help.instagram.com/147542625391305/
- https://help.skool.com/article/67-how-to-setup-categories
- https://www.facebook.com/business/ads/facebook-instagram-reels-ads

### Platform data and practitioner sources
- https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/
- https://buffer.com/resources/longer-tiktoks-get-more-views-data/
- https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-to-3-minutes/737766/
- https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/
- https://wistia.com/blog/using-video-ctas
- https://www.triplewhale.com/blog/facebook-ad-analytics
- https://motionapp.com/blog/key-creative-performance-metrics
- https://runneth.com/thumbstop-pulse/creative-benchmarks-2026
- https://motionapp.com/library/talk/meta-ads-in-2026-how-many-creatives-do-you-actually-need-to-launch/
- https://motionapp.com/library/research/creative-benchmarks-2026/top-hook-tactics
- https://www.vidyard.com/video-in-motion-benchmark-report/
- https://www.vidyard.com/blog/reduce-no-shows-recover-meetings/
- https://www.vidyard.com/business-video-benchmarks/
- https://wistia.com/blog/optimal-video-length
- https://vidiq.com/blog/post/increase-audience-retention-youtube/
- https://vidiq.com/blog/post/average-view-duration/
- https://vidiq.com/research/youtube-upload-frequency-study/
- https://air.io/en/youtube-hacks/watch-time-vs-average-view-duration
- https://cdn.prod.website-files.com/6623bf84e83241ec49b548e4/66edaa19db6e9359bb92931f_How-To-Succeed-At-MrBeast-Production%20(2).pdf
- https://x.com/PaddyG96/status/1450463472907657220
- https://www.colinandsamir.com/resources/the-new-rules-of-youtube-from-paddy-galloway
- https://www.marketingexamined.com/blog/paddy-galloway-youtube-guide
- https://voicecreator.pro/blog/burned-in-vs-closed-captions
- https://kevinwelter.com/en/blog/skool-onboarding
- https://www.youtube.com/watch?v=aiPxj5np1mQ
- https://wistia.com/blog/video-marketing-statistics
- https://buffer.com/resources/how-often-to-post-on-instagram/
- https://buffer.com/resources/instagram-reach-engagement-analysis/
- https://buffer.com/resources/state-of-social-media-engagement-2026/
- https://socialmediatoday.com/news/meta-offers-insights-on-individual-platform-growth/833807
- https://www.linkedin.com/posts/nick-saraev_i-won-the-latest-skool-games-with-a-290k-activity-7356331758415482880-FZ5v
- https://www.rev.com/blog/benefits-of-burn-in-captions
- https://oscqr.suny.edu/how-long-should-instructional-videos-be/
- https://www.tubebuddy.com/blog/11-youtube-thumbnail-tips-from-big-creators/
- https://www.linkedin.com/posts/nielsklement_most-agency-book-a-call-funnels-hit-the-activity-7379430515763736578-2qvs

### VSL and funnel sources
- https://greenfroglabs.com/blog/what-is-vsl
- https://fluxi.co/en/blog/what-is-a-vsl/
- https://www.inflopartners.com/blog/vsl-funnel-high-ticket-coaching
- https://www.inflopartners.com/blog/vsl-length-high-ticket-sales
- https://www.roezan.com/post/vsl-script-template
- https://www.vidalytics.com/video-sales-letter
- https://www.digistore24.com/blog/video-sales-letter/
- https://vslbybaran.com/video-sales-letter-editor
- https://robpalmer.com/blog/what-is-a-vsl
- https://www.clickfunnels.com/blog/how-to-create-a-video-sales-funnel/
- https://robpalmer.com/blog/long-form-sales-letter-vs-vsl
- https://ilovemarketing.com/episode-44the-one-with-jon-benson-video-sales-letters/
- https://www.vidalytics.com/analytics
- https://orangeandblackdigitals.com/blog/high-ticket-affiliate-marketing-what-it-is-how-to-start/

### Show-rate sources
- https://www.saleskick.com/blog/increase-show-rates
- https://getwebinarkit.com/blog/increase-webinar-show-up-rates
- https://ksadvantage.com/
- https://www.revenuehero.io/blog/ways-to-reduce-no-show-rates-in-sales-calls
- https://hlgrowthpartner.com/post/gohighlevel-appointment-reminder-workflows-no-shows
- https://livestorm.co/webinar-benchmark-report-2026
- https://agentatms.com/pages/reduce-life-insurance-recruiting-interview-no-shows
- https://pubmed.ncbi.nlm.nih.gov/30130032/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2438329/
- https://focus-digital.co/average-no-show-rate-for-booked-sales-meetings-by-booking-channel/
- https://ziellab.com/post/sales-meeting-no-show-rate-b2b-revops-guide
- https://www.getcontrast.io/learn/webinar-benchmarks
- https://univid.io/webinar-statistics/
- https://calendly.com/blog/reduce-no-show-rates-sales
- https://callingagency.com/benchmarks-and-resources/appointment-setting-statistics/
- https://ainora.lt/blog/webinar-attendance-statistics-every-study-2026

### Learning research
- https://www.ruzuku.com/learn/articles/course-completion-rates
- https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf
- https://multimedia.ucsd.edu/best-practices/video-length.html

### Open-source tooling
- https://raw.githubusercontent.com/htekdev/vidpipe/main/docs/research-aspect-ratios.md
- https://github.com/fujiwarachoki/supoclip/issues/268
- https://raw.githubusercontent.com/htekdev/vidpipe/main/docs/research-chapters.md
- https://raw.githubusercontent.com/htekdev/vidpipe/main/docs/research-captions.md
- https://github.com/htekdev/vidpipe
- https://github.com/timkulbaev/ai-video-editor
- https://github.com/wyattblue/auto-editor/blob/5883594ea9dbf0922506d02786196e056f7d2df5/docs/src/docs/cookbook.md
- https://github.com/fujiwarachoki/supoclip/issues/175
- https://github.com/pyannote/pyannote-audio
