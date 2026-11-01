---
name: hooks-titles-thumbnails-covers
description: Writes the first second of a video (the spoken hook and the on-screen hook text), titles for YouTube and Skool, thumbnails and reel covers, and the hook variants for an ad batch, then builds the cover frame with the engine. Use when someone asks for hooks, titles, thumbnails, covers, "make it clickable", "why is nobody clicking", or more hook variants for an ad concept.
---

# Hooks, titles, thumbnails, covers

The title, the cover, the hook text and the first spoken line say one thing. YouTube reads survival at 30 s as proof (keep 60%, strong hooks over 65%); the Shorts report counts viewed versus swiped away, and reels rank on watch time plus likes and sends per reach (`FORMATS.md`), so the proposition is on screen by 3 s and the hook complete by 6 s. High clicks with low watch time is clickbait.

## 1. Where the hook comes from

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<file>" --out "$KIT/output/<job>"
```

Pick the hook from the ranked windows or transcript.txt: the first sentence that names the viewer's pain in their words, never one about us (`skills/sales/closer-mentality/SKILL.md`, the See move). Problem-first beat claim-first 9 of 12 on cold traffic. Four to seven words, first word about them. `--hook` holds 2.6 s before the captions start (`skills/video/reel-editor/SKILL.md`); long-form speaks the thesis inside 10 s (`EDITING_GRAMMAR.md`).

## 2. Twelve hook patterns, house voice

Second person and blunt, never cruel; closers left, insurance agents right. Swap in the viewer's words.

| Pattern | Closers | Insurance agents |
|---|---|---|
| Their sentence | "I want to think about it" is stealing your commissions. | "I have a 401(k)." They said it. You moved on. |
| Call-out | Commission-only closers: your skill today is your ceiling. | Life agents: the money is sitting in your CRM. |
| Cost | Every "I need to think about it" is commission you earned and gave back. | You sold the policy once and never asked the question. |
| Not for you | If you blame the market, keep scrolling. | If you would rather buy another lead, keep scrolling. |
| Contrarian | Objection handling is the wrong skill. | Stop buying leads. The money is already in your book. |
| Open loop | The move most closers skip happens before the price. | Two or three questions you never asked. |
| Question | What did your last prospect say right before no? | Which of your clients mentioned a 401(k) this year? |
| Identity | Four types of closers. One of them is you. | Two kinds of agents: those who set, those who sell. |
| Ceiling | Most closers never see 350K. | 20+ agents placed $3.8M in 2025 from books like yours. |
| Mirror | The easy deals will not tell you if you can sell. The hard ones will. | You keep dialing new leads for $140-a-month policies. |
| Mechanism | Four moves. The prospect makes them, not you. | You set it, we close it, you get paid. |
| Before you | Before your next call, ask this one question. | Before you dial another lead, open your CRM. |

## 3. On-screen hook text

- Bright frame: 60 to 70% of mobile viewers ran dark mode in Galloway's 2021 count; a dark frame vanishes.
- Clear of Meta's edges (top 14%, bottom 35%, 6% left, 6% right); the hook card sits at 30% of frame height. Caps in the brand caption face; the Set More Annuities look sets the hook in Fraunces, a serif (`skills/video/caption-styles/SKILL.md`).

## 4. Titles

YouTube: under 100 characters, key words first, branding and episode numbers last, caps and emoji rare. Title words are spoken inside the first 15 s (the yt_authority check in `FORMATS.md`). Draft 10 to 20 title and thumbnail pairs; test up to 3 in native A/B, which picks by watch time share.

Skool: a lesson title names the one objective and those words open the video. A replay title is the topic and the date; the Skool event's cover becomes its cover, so keep that title short.

## 5. Thumbnails and covers

- YouTube thumbnail: 16:9, 1280x720 house minimum (YouTube accepts 640 px wide, and anything under 720p downscales in its A/B test), 3840x2160 recommended, under 2 MB. At most 3 elements, 1 or 2 faces, 1 to 4 words, plain background, the moment before the action; check it on black.
- Reel cover: 420x654 (1:1.55) on Instagram, not editable after upload. Face or key words centered; a 9:16 cover loses about 6% top and bottom in the grid.
- Ad: frame 0 is the hook frame, one face, proposition text in the safe zone, bottom 40% clear while a disclaimer is up.
- VSL poster matches the page headline, which matches the ad's first line (house line, `FORMATS.md` vsl_book_call; the VSL itself is cut per `skills/video/vsl-producer/SKILL.md`). Show-rate and Skool covers: the person the viewer will meet, looking into the lens; welcome "start here", lesson module number and title.

## 6. The cover command

```bash
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/<job>" --title "2 to 4 words" --brand btc --out "$KIT/output/<job>/cover" [--at S]
```

A job folder supplies the face track; a bare video starts 0.8 s in. It picks the largest, surest face inside the first 8 s, grabs it through the brand LUT, crops both aspects around the face, darkens a 34% band (top when the face sits low, else bottom), sets the caps title on up to two lines inside 88% of the width, last line in the accent colour, and writes thumbnail.jpg 1280x720 and cover.jpg 1080x1920. `longform` builds thumbnail.jpg and cover.jpg through the same builder, titled from its first chapter or its CTA line, and refuses a brand never-word in that text; `cover` does not check. Upload cover.jpg as the cover (`skills/video/platform-formatter/SKILL.md`).

## 7. Ad hook variants

Hooks per concept: a house choice inside the published bands (TikTok 3 to 5 creatives per ad group; Meta up to 10 per ad set, judged after at least 4 days by keeping the top 5): five hooks per concept, only the first 3 s changing, plus the winner's 15 s cutdown. Four concrete patterns and one interrupt (contrarian, confession, warning or myth-busting): Motion's top-ranking tactics, concrete ones in front, hit 6 to 11% against 4 to 8% tier averages; interrupts hit less often with more variance. Name each file by pattern: `<brand>_<format>_<concept>_h<n>_<pattern>_<length>`, as in `btc_paid_ad_reel_thinkaboutit_h3_contrarian_30s`. Judge by hook rate (3-second plays over impressions) and hold rate (15-second plays, or ThruPlays, over 3-second plays; pick one numerator and label it) against the account median; when hook rate is low, change only the first 3 s. About 5 to 8% of launches win, so volume beats polish.

## 8. Words never on a hook, title, thumbnail or cover

- The `HOUSE_RULES.md` banned words.
- Become The Closer never prints: free, no cost, guarantee, guaranteed. Set More Annuities, where a client reads: the product name. The engine refuses both in a hook (`skills/brand/brand-kit/SKILL.md`).
- An income figure framed as an outcome; "you" next to a money problem, as in "Are you bankrupt?"; fake controls such as "swipe up"; pressure words: last chance, final, lose everything, only today.
- A number or a name the footage and the brand sheet do not hold.

Hand over the hook, two alternatives, the title and the cover file. Paid or client-facing work goes through `skills/video/cold-review/SKILL.md` first.
