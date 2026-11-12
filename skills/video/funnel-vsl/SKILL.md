---
name: funnel-vsl
description: Builds sales-funnel VSLs for Become The Closer and Set More Annuities. The book-a-call cut (4 to 12 min) for a quiz result page, an opt-in thank-you page, the website page or an application page, and the program-sale cut (15 to 45 min) for the sales page. Beat timings, where the button reveals, which proof goes in, how each page is set up, the longform command and the vsl-producer cutaway route, the claim and brand checks, and what to test after launch. Use when someone asks for a VSL, a BVSL, a sales video, "the video for the page" or "the video for the application".
---

# Funnel VSL

The viewer already clicked. They are curious and guarded, deciding whether to give you a calendar slot or their money. Read `skills/sales/closer-mentality/SKILL.md` first (See, Own, Lead, Decide) and `FORMATS.md`, which sources every number below. "BVSL" is defined in no source: treat it as the book-a-call cut (the engine sends `bvsl` there too) and say so in your reply.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
```

The table it prints comes from `formats.json` at the kit root. Older ids such as `vsl_short` still resolve to `vsl_book_call`.

## 1. Pick the cut

| What is sold | Format id | Length | Where it plays |
|---|---|---|---|
| A call or an application | `vsl_book_call` | 4 to 12 min, 7 the target. Warm cut 5 to 6 min, cold cut 7 to 9. | BTC quiz result page, opt-in thank-you page, SMA website page, application page |
| The program itself | `vsl_long` | 15 to 45 min, 25 the house target | sales page or application page |
| The homepage hero | `vsl_hero` | 60 to 150 s, 100 the target | above the fold on the homepage; several takes go through `skills/video/vsl-builder/SKILL.md` |

Warm means they already sat through your training or workshop. Cold means the ad landed them here. Two more cases from the same source: a VSL sent inside an email sequence runs 4 to 5 min, and a list that has already weighed up your category takes 9 to 12. Never under 4 min. Never over 12 unless it is a case-study video rather than a sales video.

## 2. Beats and the button

Book-a-call cut: hook 0:00 to 0:30 on the viewer's situation, not the ad's claim; problem 0:30 to 2:00 (80% of viewers watch the first 2 to 3 minutes, the widest audience the video has); proof 2:00 to 4:00 with the escape hatch at about 2:30 to 3:00 ("If that's all you need to hear, you can book a call below"); objections said out loud 4:00 to 5:30; the ask 5:30 to 7:00 with a reason to act now and who it is not for. The price stays off the video. No agitation stretch past 90 s.

Long cut: hook 0:00 to 0:45; problem and root cause to 3:00; mechanism to 7:00; proof to 11:00; offer and value stack to 15:00; objections 15:00 to 18:00; the ask and terms to the end. One call to action, repeated but singular.

The button reveals at the escape hatch (book-a-call) or at the offer (long) and stays. Page rules: controls visible, no navigation links, a text version of the offer under the player, one open-text qualifying question above the application. The engine does not write the reveal time to the page yet (`FORMATS.md` section 3), so read the start time of that line from `captions.srt` in the finished job (it runs on the cut's own clock) and hand it to whoever builds the page. Judge the reveal time by sales, not clicks. A later button gets fewer clicks from better people.

Proof that goes in: the person's own takes, the site's own lines, `testimonial_clip` cuts in the long cut's proof block, and the one figure the owner cleared for Set More Annuities (20+ agents, $3.8M placed in 2025), which appears on agent-facing SMA pieces only. A specific result carries the brand's results line on screen. Nothing else.

## 3. Page variants

The house standard for the page around the VSL is `docs/blueprints/VSL_PAGE.md` (owner's call, 2026-11-12): its section order, design tokens, copy pattern and funnel map (the page sells a call on the same page, the call sells the offer). Build every VSL page from it unless the owner says otherwise; the variants below decide which cut plays.

- Opt-in thank-you page: the warm cut when the opt-in came through your training, otherwise the cold cut; the button sits under the player. Wistia's hosted-video data puts the play rate on thank-you pages at 10%, so the headline and the text offer carry the promise for everyone who never presses play.
- Quiz result page or website page: the cold cut for direct traffic. The headline matches the ad's first line and the first spoken line. SMA's one ask: open the account and register for the Wednesday training.
- Application page: the book-a-call cut, one open-text qualifying question under the player, the 5 to 8 question application, then the confirmation page from `skills/video/show-rate-videos/SKILL.md`.
- Sales page: the long cut with `testimonial_clip` cuts in its proof block; the button reveals at the offer.

No controlled comparison of these placements exists. Choose by traffic temperature and test the rest.

## 4. Cut it

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<take>.mp4" --out "$KIT/output/<job>"
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/<take>.mp4" --out "$KIT/output/<job>" \
  --brand btc --format vsl_book_call --cta "Book your call below" --title "<1 to 4 words of the headline>" \
  --quotes "the problem line|the proof line|the escape hatch line|the objection line"
"$PY" "$KIT/tools/closer.py" review "$KIT/output/<job>"
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/<job>" --title "<the same words>" --brand btc --out "$KIT/output/<job>/cover" --at <s>
```

The last line is only for re-picking the poster frame at a second you choose. Read the transcript from the analyze step and mark the beats before you cut. Afterwards check that the escape hatch lands between 2:00 and 3:30 and the final ask inside the last 90 s.

What the format sets, so you can explain it in one breath: clean burned captions (the page autoplays muted), fillers cut, no music unless `--music` names a bed, 1920x1080 at -15 LUFS. `--cta` is the page's ask in a few words; it goes on the engine's 2.5 s end card after the last word and through the brand lint, so a BTC booking page never ends on the quiz line. For Set More Annuities the brand line already is the account line, so leave `--cta` off. `--title` is 1 to 4 words of the page headline for the poster frame; the job gets `thumbnail.jpg` at 1280x720 and `cover.jpg` at 1080x1920. `--quotes` puts each section's key line on a card while it is spoken, words exactly as spoken. The review fails any line it cannot find in the speech. One card per section after the hook is the house choice. For the long cut add `--chapters "0:Hook,45:Problem,180:Mechanism,420:Proof,660:Offer,900:Objections,1080:The ask"` with your own times, so the section cards land in order.

Cutaways. `--broll <folder>` lays 3.2 s shots from your clips on sentence ends, spaced to the format's cadence: 8 s on the book-a-call cut, 10 s on the long cut. Cards and B-roll shots count as layout changes; punch-ins do not. The review prints FIX on every stretch that runs past the cadence without one. House limits on B-roll: under 40% of the runtime, and none inside the opening 3 s or the final second. `--change-every 12` spaces the shots wider when they crowd the face.

When the mechanism needs animation (a list, a number, a step, a before-and-after), use `skills/video/vsl-producer/SKILL.md`: copy its builder, record the beat sheet, map each graphic to a spoken word, re-skin its HTML scenes with the brand tokens. Its rules hold: no face beat under 2.5 s between cards, hard card-to-card cuts, the bottom quarter clear for captions, no flash frames. That route renders its own file; the length band still comes from the `formats` table.

Autoplay only with a restart on unmute, never a pause lock.

## 5. Claims and compliance

- Audit every fact, number, name and promise the script says or shows against its source (the takes, the brand sheet, the company's documents, the owner's words) before the cut, and write the project's AUDIT.md. An unsourced line stays spoken at most, never on a card. `HOUSE_RULES.md` applies to every word on screen.
- Income figures are never framed as the viewer's likely outcome: show the steps and name the risk (Google and TikTok ad policy). The page says what the ad said.
- Become The Closer never prints the four never-words listed in `brand/btc.json`. The engine refuses a `--cta` or `--title` that carries one and checks the `cover` title the same way; the review flags any that are spoken. The SMA proof figure is never a BTC line.
- Set More Annuities talks to agents and may name its product, and its brand sheet's account line is allowed as written. Only a job run with `--audience client` turns on the client-facing never-words in `brand/sma.json`; a website VSL for agents does not run with it.
- No "you" plus a financial attribute (debt, bankruptcy) in any line that will also run as an ad (Meta).
- A specific result in a testimonial gets the brand's results line on screen; on a 9:16 cut of the same take the bottom 40% stays clear while it is up (Meta).

## 6. Test after launch

1. Fix the earliest retention cliff first; a cliff before 0:30 is the hook. Then the loop: find the biggest drop, rewrite that section, relaunch, repeat.
2. Reference: 40% still watching when the button appears, a purchase-funnel figure. Only 20% stay to the end of a video over 20 min, so the ask never waits for the end.
3. Long cut: the presenter cut against plain text on screen. In Vidalytics' split the plain cut held 68% at 0:35 against 49% for the presenter cut.
4. Autoplay with restart on unmute against the page's current player. In Vidalytics' test a pause lock held 15% against 30% on the control; removing the lock and restarting on unmute converted 49% better.
5. Warm length against cold length when the page takes both.

Run `skills/video/cold-review/SKILL.md` on the final file. Hand over the file, the length, the button reveal time, the page headline, the text offer, the qualifying question, the claims audit, and what the video still cannot prove.

## Rules

- One ask per video, repeated but singular. No second offer.
- The price stays off the book-a-call cut; who it is not for stays in.
- Never a number, a name, a result or a promise that the takes, the brand sheet, the company's documents or the owner did not give you.
- Music is optional and quiet; the cut must work muted.
- The four BTC never-words stay off every BTC cut, card, title and page line.
- Say done only when every review line reads PASS and the cold review says SHIP.
