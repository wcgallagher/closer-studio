---
name: hooks-titles-covers
description: Writes the first line of a video (the spoken hook and the on-screen hook text), the YouTube or Skool title, the thumbnail or reel cover, and the hook variants for an ad batch, then builds the cover frame with the engine. Use when someone asks for hooks, titles, thumbnails, covers, "make it clickable", "why is nobody clicking", or more hook variants for an ad concept.
---

# Hooks, titles, thumbnails, covers

The title, the cover, the hook text and the first spoken line say one thing. The platforms grade that promise early: YouTube reads survival at 30 s as proof the opening matched the title (keep 60%, strong hooks over 65%), the Shorts report counts viewed versus swiped away, reels rank on watch time plus likes and sends per reach, and a paid ad lives on its hook rate. So the proposition is on screen by 3 s and the hook is complete by 6 s. High clicks with low watch time is clickbait.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY=python3
ls "$KIT/inbox" "$KIT/output"
```

## 1. Find the hook in the footage

```bash
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/<file>" --out "$KIT/output/<job>"
```

Read the ranked windows and transcript.txt. The hook is the first sentence that names the viewer's pain in their own words, never a sentence about us (the See move in `skills/sales/closer-mentality/SKILL.md`). Problem-first hooks beat claim-first 9 of 12 on paid cold traffic. Four to seven words, first word about them. On a reel `--hook` holds the card for 2.6 s before the captions start (`skills/video/reel-editor/SKILL.md`); long-form speaks the thesis inside 10 s (`EDITING_GRAMMAR.md`).

## 2. Pick a pattern, keep the house voice

Second person. Blunt, never cruel. Closers on the left, insurance agents on the right. Swap in the viewer's words.

| Pattern | Closers | Insurance agents |
|---|---|---|
| Their sentence | "I want to think about it" is stealing your commissions. | "I have a 401(k)." They said it. You moved on. |
| Call-out | Commission-only closers: your skill today is your ceiling. | Life agents: the money is sitting in your CRM. |
| Cost | Every "I need to think about it" is commission you earned and gave back. | You sold the policy once and never asked the question. |
| Not for you | If you blame the market, keep scrolling. | If you would rather buy another lead, keep scrolling. |
| Contrarian | Objection handling is the wrong skill. | Stop buying leads. The money is already in your book. |
| Open loop | The move most closers skip happens before the close. | Two or three questions you never asked. |
| Question | What did your last prospect say right before no? | Which of your clients mentioned a 401(k) this year? |
| Identity | Four types of closers. One of them is you. | Two kinds of agents: those who set, those who sell. |
| Ceiling | Most closers never see 350K. | 20+ agents placed $3.8M in 2025. From their own books. |
| Mirror | The easy deals will not tell you if you can sell. The hard ones will. | You keep dialing new leads for $140-a-month policies. |
| Mechanism | Four moves. The prospect makes them, not you. | Set it and we close it, or learn to close it yourself. |
| Before you | Before your next call, ask this one question. | Before you dial another lead, open your CRM. |

The 350K line is the Become The Closer site's own sentence about the viewer's ceiling, and it stays on the closer side. The $3.8M line is the owner's Set More Annuities proof figure: agent-facing only, never a Become The Closer hook, never framed as what the viewer will make, and under Meta's financial special ad category when it runs paid (`FORMATS.md` section 2).

## 3. Put the hook text on screen

- Bright frame. Galloway's 2021 count had 60 to 70% of mobile viewers on dark mode, where a dark frame vanishes.
- Clear of Meta's edges: top 14%, bottom 35%, left 6%, right 6%. The hook card sits at 30% of frame height in the brand caption style; `--hook-serif` sets it in Fraunces for the Set More Annuities look (`skills/video/caption-styles/SKILL.md`).

## 4. Write the title

YouTube: under 100 characters, key words first, branding and episode numbers last, caps and emoji rare. The title words get spoken inside the first 15 s (the yt_authority check in `FORMATS.md`). Draft 10 to 20 title and thumbnail pairs and test up to 3 in YouTube's native A/B, which picks by watch time share. `longform --title "1 to 4 words"` puts the title on the thumbnail; without it the engine uses the first chapter title, else the CTA line.

Skool: a lesson title names the one objective, and those words open the video. A replay title is the topic and the date. The Skool event's cover becomes the replay cover, so keep the event title short.

## 5. Build the cover

```bash
"$PY" "$KIT/tools/closer.py" cover "$KIT/output/<job>" --title "1 to 4 words" --brand btc --out "$KIT/output/<job>/cover"
```

Add `--at <seconds>` to pick the frame time yourself and `--audience client` when the agent's own customer will see it. A job folder supplies the face track; a bare video file starts 0.8 s in. The engine picks the largest, surest face inside the first 8 s, grabs that frame through the brand LUT, crops both aspects around the face, darkens a 34% band (top when the face sits low, else bottom), sets the caps title on up to two lines inside 88% of the width with the last line in the accent colour, and writes thumbnail.jpg (1280x720) and cover.jpg (1080x1920). Every command that takes copy (`reel --hook`, `longform --title`, `cover --title`, and the CTA on each) refuses a brand never-word and names it. Upload cover.jpg as the reel cover so the grid reads (`skills/video/platform-formatter/SKILL.md`).

What goes on it:

- YouTube thumbnail: 16:9. The engine's 1280x720 is the house floor. YouTube's own floor is a 640 px width; it recommends 3840x2160 and caps a phone upload at 2 MB, and its A/B test downscales anything under 720p. At most 3 elements, 1 or 2 faces, 1 to 4 words, a plain background, the moment before the action. Check it on black.
- Reel cover: 420x654 (1:1.55) on Instagram. Face or key words centered for the taller grid; it cannot be edited after upload.
- Ad: frame 0 is the hook frame. Bright, one face, proposition text inside the safe zone, bottom 40% clear while a disclaimer is up.
- VSL poster matches the page headline, which matches the ad's first line (house line; the VSL itself is cut per `skills/video/vsl-producer/SKILL.md`). Confirmation clips: the person they will meet. Skool welcome and cancel: the creator's face at the desk, eye contact. Skool lesson: face plus the module name.

## 6. Hook variants for an ad batch

Hooks per concept is a house choice inside the published bands. TikTok suggests 3 to 5 creatives per ad group. Meta's own cadence starts with up to 10 per ad set and keeps the top 5 after at least 4 days. We cut five hooks per concept and change only the first 3 s between them. The winner also gets a 15 s cutdown. Four of the five are concrete patterns and one is an interrupt (contrarian, confession, warning or myth-busting): Motion's 2026 ranking puts its top tactics, the concrete cluster in front, at 6 to 11% hit rate against 4 to 8% tier averages, and interrupts hit less often with more variance, so one keeps a testing slot. Name each file by pattern, `<brand>_<format>_<concept>_h<n>_<pattern>_<length>`, as in `btc_paid_ad_reel_thinkaboutit_h3_contrarian_30s`.

Judge by hook rate (3-second plays over impressions) and hold rate (15-second plays over 3-second plays; ThruPlays is the other numerator, so pick one and label it) against the account median. When hook rate is low, change only the first 3 s. Motion counts 5 to 8% of launches as winners, so volume beats polish.

## 7. Hand it over

Tell the person: the hook you chose, two alternative hooks, the title, and where the cover files are in `output/<job>/`. Paid or client-facing work goes through `skills/video/cold-review/SKILL.md` before you say done. Stop.

## Rules

- The hook is their sentence, not ours. The first word is about them.
- The `HOUSE_RULES.md` banned words never go on a hook, title, thumbnail or cover.
- The four BTC never-words (`brand/btc.json`, words.never) never appear on a Become The Closer piece. The Set More Annuities product word never appears where a client reads; run that job with `--audience client` and the engine refuses it there too (`skills/brand/brand-kit/SKILL.md`).
- No income figure framed as the viewer's outcome. No "you" next to a money problem, as in "Are you bankrupt?". No fake controls such as "swipe up". No pressure words: last chance, final, lose everything, only today.
- No number and no name that the footage or the brand sheet does not hold.
