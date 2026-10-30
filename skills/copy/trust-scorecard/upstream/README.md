# NCI Engineered Reality Scoring System

Interactive CLI for the Chase Hughes / NCI psyop assessment rubric.

## Usage

```bash
npm start
# or
node index.js
```

## How it works

1. Enter the name of the news event or potential psyop
2. Score each of 20 categories on a 1–5 scale
3. Add optional notes per category
4. Receive a verdict with a full score breakdown
5. Assessment is saved as a Markdown file in `assessments/`

## Scoring

| Score | Meaning |
|-------|---------|
| 1 | Not present |
| 2 | Slightly present |
| 3 | Moderately present |
| 4 | Strongly present |
| 5 | Overwhelmingly present |

## Verdict thresholds

| Total (20–100) | Verdict |
|----------------|---------|
| 20–40 | Low likelihood — largely organic |
| 41–60 | Moderate — some engineered elements |
| 61–80 | Strong — narrative shaping likely |
| 81–100 | Overwhelming — coordinated information operation |

## Categories

1. Timing
2. Emotional Manipulation
3. Uniform Messaging
4. Missing Information
5. Simplistic Narratives
6. Tribal Division
7. Authority Overload
8. Call for Urgent Action
9. Overuse of Novelty
10. Financial / Political Gain
11. Suppression of Dissent
12. False Dilemmas
13. Inconsistent Details
14. Prepackaged Solutions
15. Unverifiable Claims
16. Hero / Villain Construction
17. Rapid Memory-Holing
18. Shifting Explanations
19. Selective Evidence Presentation
20. Beneficiary Analysis
