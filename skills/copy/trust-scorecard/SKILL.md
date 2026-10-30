---
name: trust-scorecard
description: Pre-launch trust check for sales copy, VSL scripts, ads, landing pages and emails. Scores the piece against the 20 manipulation tells in the Chase Hughes / NCI engineered-reality rubric and flags every line a skeptical buyer (or a compliance reviewer) would read as a trick. Use before publishing any persuasive asset, especially for financial, insurance or retirement offers, or when asked "does this sound salesy", "is this too pushy" or "will this trip people's BS detector".
---

# Trust Scorecard

The NCI rubric was built to spot engineered narratives in the news. Run it in reverse on our own copy: every tell it
catches is a place where a skeptical buyer stops trusting us. Retirement money buyers are the most skeptical buyers
there are, and insurance regulators read the same tells as unfair or misleading marketing. **Low score wins.**

Upstream CLI and its 20 original questions: `upstream/` (`node upstream/index.js` after `npm install` there).

## How to run it

1. Read the whole asset once. Note the offer, the audience and the single action it asks for.
2. Score each of the 20 tells below from 1 (not present) to 5 (overwhelming). Quote the exact line behind every
   score of 3 or more.
3. Total them (20-100) and give the verdict.
4. For every line scoring 3+, write the replacement: same persuasive job, without the tell. Usually that means
   adding the missing specific, the real reason, or the proof.

## The 20 tells, translated for marketing

| # | Tell | What it looks like in copy | Fix |
|---|---|---|---|
| 1 | Timing | "Before the market crashes", pegging the pitch to a news event to borrow fear | Tie urgency to the buyer's own clock (age 59.5, RMDs at 73, a CD maturing) |
| 2 | Emotional manipulation | Fear or guilt with no fact underneath ("you could lose everything") | State the real risk with a number or an example, then the feeling |
| 3 | Uniform messaging | Lines lifted from every other guru ("missing the bag", "level up") | Say it the way this speaker actually talks |
| 4 | Missing information | No mention of cost, surrender periods, splits, who closes the deal | Put the terms in plain view; buyers assume the worst about what's hidden |
| 5 | Simplistic narratives | "Stocks bad, annuities good" with no trade-offs | Name who it's for and who it isn't for |
| 6 | Tribal division | Us vs. them (agents vs. "Wall Street", "advisors are robbing you") | Make the enemy the problem, not a group of people |
| 7 | Authority overload | Stacked logos, "experts agree", credentials doing the arguing | One credible proof beats ten name-drops |
| 8 | Urgent action | Countdown timers, "only today", pressure to decide before thinking | Real deadlines only, with the reason for them |
| 9 | Overuse of novelty | "Never before seen", "secret loophole" | Show the mechanism; it's more believable when it's ordinary |
| 10 | Hidden gain | It's unclear how the seller makes money | Say how you get paid (commission, split) up front |
| 11 | Suppression of dissent | Mocking objections ("if you're too lazy to...") | Answer the objection seriously |
| 12 | False dilemmas | "Join now or stay broke" | Offer the honest alternatives, then why this one |
| 13 | Inconsistent details | Numbers that change between the headline, the video and the page | One source of truth for every figure |
| 14 | Prepackaged solutions | The product shows up before the problem is understood | Diagnose first, prescribe second |
| 15 | Unverifiable claims | "$3.8M placed" with nothing behind it, anonymous results | Show the receipt, the screenshot or the named source; else cut it |
| 16 | Hero / villain | The founder as savior, everyone else as fool | Make the buyer the hero; the founder is the guide |
| 17 | Memory-holing | Old promises quietly removed, results that disappear | Keep claims consistent across versions |
| 18 | Shifting explanations | The pitch changes depending on the objection | One clear reason it works, repeated |
| 19 | Selective evidence | Only the best case, no typical result | Show typical results next to the best case |
| 20 | Beneficiary analysis | The seller wins far more than the buyer | Make the buyer's upside the biggest number on the page |

## Verdict

| Total | Verdict | Ship it? |
|---|---|---|
| 20-30 | Clean. Reads like a straight shooter. | Yes |
| 31-45 | A few tells. Fix every line scored 3+. | After fixes |
| 46-60 | Reads like a pitch. Buyers will discount it. | Rewrite the flagged sections |
| 61+ | Reads like a con, whatever the intent. | Start over |

## Output

```
TRUST SCORE: 34/100  (A few tells)
3+ flags:
- #10 Hidden gain (3): "It's completely free" -- never says how the agent or Chase gets paid.
  Fix: "Free to join. When you set an appointment and we close it, we split the commission 50/50."
- #15 Unverifiable (4): "$3.8M placed in 2025" -- no proof on screen.
  Fix: show the carrier production report (names redacted) for 2 seconds, or cut the number.
Clean: 1, 2, 3, ...
```

Score honestly. A low score earned by hiding tells is worse than a high score you fix.
