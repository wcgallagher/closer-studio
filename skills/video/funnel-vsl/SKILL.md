---
name: funnel-vsl
description: Builds sales-funnel VSLs for Become The Closer and Set More Annuities. The book-a-call cut (3 to 10 min) for a quiz result page, an opt-in thank-you page, the website page or an application page, and the program-sale cut (15 to 45 min) for the sales page. Beat timings, where the button reveals, which proof goes in, how each page is set up, the longform command and the vsl-producer cutaway route, the claim and brand checks, and what to test after launch. Use when someone asks for a VSL, a BVSL, a sales video, "the video for the page" or "the video for the application".
---

# Funnel VSL

The viewer already clicked. They are curious and guarded, deciding whether to give you a calendar slot or their money. Read `skills/sales/closer-mentality/SKILL.md` first (See, Own, Lead, Decide) and `FORMATS.md`, which sources every number below.

Treat "BVSL" (undefined in every source found) as the book-a-call cut and say so in your reply.

## 1. Pick the cut

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" formats
```

| What is sold | Format id | Length | Where it plays |
|---|---|---|---|
| A call or an application | `vsl_short` | 3 to 10 min engine band. Warm cut 5 to 6 min, cold cut 7 to 9. | BTC quiz result, opt-in thank-you, SMA website or application page |
| The program itself | `vsl_long` | 15 to 45 min, 25 the house target | sales or application page |

Warm means they already sat through your training or workshop; cold means the ad landed them here. `vsl_short` is the engine's built-in id for this cut. The registry's `vsl_book_call` (`FORMATS.md`: 240 to 720 s with an in-band button) lives in a registry file the kit does not ship, and the engine stops with "unknown format" when asked for it. When the `formats` table prints `vsl_book_call`, pass that id instead; the beats below do not change.

## 2. Beats and the button

Book-a-call cut: hook 0:00 to 0:30 on the viewer's situation, not the ad's claim; problem 0:30 to 2:00 (80% of viewers watch the first 2 to 3 minutes); proof 2:00 to 4:00 with the escape hatch at about 2:30 to 3:00 ("if that is all you need to hear, book below"); objections out loud 4:00 to 5:30; the ask 5:30 to 7:00 with a reason to act now and who it is not for. The price stays off the video. No agitation stretch past 90 s.

Long cut: hook 0:00 to 0:45; problem and root cause to 3:00; mechanism to 7:00; proof to 11:00; offer and value stack to 15:00; objections 15:00 to 18:00; the ask and terms to the end. One call to action, repeated but singular.

The button reveals at the escape hatch (book-a-call) or at the offer (long) and stays. Page rules: controls visible, no navigation, a text offer under the player, one open-text qualifying question above the application. The engine does not yet write the reveal time (to-add list, `FORMATS.md` section 3): read that line's time from `captions.srt` in the finished job (post-cut clock) and hand it to whoever builds the page. Judge the reveal time by sales, not clicks.

Proof that goes in: the person's own takes, the site's own lines, `testimonial_clip` cuts in the long cut's proof block, and the one figure the owner cleared (20+ agents, $3.8M placed in 2025). A specific result carries the brand's results line on screen. Nothing else.

## 3. Page variants

- Opt-in thank-you page: the warm cut when the opt-in came through your training, otherwise the cold cut; the button sits under the player. Thank-you pages hold a 10% play rate, so the headline and text offer carry the promise for those who never press play.
- Quiz result or website page: the cold cut for direct traffic. The headline matches the ad's first line and the first spoken line. SMA's one ask: open the account and register for the Wednesday training.
- Application page: the book-a-call cut, the qualifying question, the 5 to 8 question application, then a confirmation page from the show-rate formats (`FORMATS.md`, section 7).
- Sales page: the long cut with testimonial clips in its proof block; the button reveals at the offer.

No controlled comparison of these placements exists; choose by traffic temperature and test the rest.

## 4. Cut it

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<take>.mp4" --out "$KIT/output/<job>"
"$PY" "$KIT/tools/closer.py" longform "$KIT/inbox/<take>.mp4" --out "$KIT/output/<job>" \
  --brand btc --format vsl_short --platform web_vsl --fillers cut \
  --quotes "the problem line|the proof line|the escape hatch line|the objection line"
"$PY" "$KIT/tools/closer.py" review "$KIT/output/<job>"
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/<job>" --title "2 to 4 words of the headline" --brand btc --out "$KIT/output/<job>/cover"
```

Read the transcript and mark the beats. Check the escape hatch lands between 2:00 and 3:30 and the final ask inside the last 90 s. The built-in sets clean burned captions and fillers cut; no music plays unless `--music` names a bed. `--quotes` puts one key-line card per section, lines as spoken (a house choice). The end card carries the brand sheet's CTA line (the quiz line for BTC, the account line for SMA); the page's own ask lives in the spoken ask and on the page button. On a BTC book-a-call page that end-card line is not the page's ask; the owner's open items cover it. For the long cut add `--chapters "0:Hook,45:Problem,180:Mechanism,420:Proof,660:Offer,900:Objections"` so the section cards land in order. Cutaways stay under 40% of runtime and at most one per 12 s. None in the first 3 s or the last second.

When the mechanism needs animation (a list, a number, a step, a before-and-after), use `skills/video/vsl-producer/SKILL.md`: copy its builder, record the beat sheet, map each graphic to a spoken word, re-skin its HTML scenes with the brand tokens. Its rules hold: no face beat under 2.5 s between cards, hard card-to-card cuts, the bottom quarter clear for captions, no flash frames.

`cover` builds the poster frame (thumbnail 1280x720, cover 1080x1920) from the job; its title is 2 to 4 words of the page headline. Autoplay only with a restart on unmute, never a pause lock.

## 5. Claims and compliance

- Audit every fact, number, name and promise the script says or shows against its source (the takes, the brand sheet, the company's documents, the owner's words) before the cut, and write the project's AUDIT.md. An unsourced line stays spoken at most, never on a card. `HOUSE_RULES.md` applies to every word on screen.
- Income figures are never framed as likely outcomes: show the steps and name the risk (Google, TikTok policy). The page says what the ad said.
- Become The Closer never prints a word from its brand sheet's never-list. The review flags them in the transcript; nothing checks the cover title, so read it against that list yourself. Set More Annuities never prints the product word in client-facing copy; its account is free and that brand may say so.
- No "you" plus a financial attribute (debt, bankruptcy) in a hook that will also run as an ad (Meta).
- A specific result in a testimonial gets a visible results-vary card; on 9:16 the bottom 40% stays clear while it is up.

## 6. Test after launch

1. Fix the earliest retention cliff first: before 0:30 it is the hook.
2. Reference: 40% still watching when the button appears. Only 20% stay to the end past 20 min, so the ask never waits for the end.
3. Long cut: presenter against plain text-on-screen (68% held at 0:35 against 49% for the produced version).
4. Autoplay with restart on unmute against the page's control player (a pause lock dropped engagement to 15% against 30% on the control; the restart version converted 49% better).
5. Warm length against cold length when the page takes both.

Run `skills/video/cold-review/SKILL.md` on the final file. Hand over the file, the length, the button reveal time, the page headline, the text offer, the qualifying question, the claims audit, and what the video still cannot prove.
