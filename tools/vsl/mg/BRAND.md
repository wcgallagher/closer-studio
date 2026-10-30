# SMA video brand sheet

One system for everything the viewer sees: the animated cutaways (`scenes.html`), the text burned over the footage
(`vsl/pipeline/v7_build.py`, ASS styles), the end card, and the review page. Source: setmoreannuities.com (Firecrawl
branding scrape, 2026-10-30), which is a cream page with a dark, red-glow video panel. The video lives inside that panel,
so the graphics stay dark and borrow the page's accents.

## Colour

| Token | Hex | Used for |
|---|---|---|
| `--bg` | `#0e1114` | graphics background: the site's player panel black (cool), with a maroon `#491d19` radial glow, so the cards sit inside the page's panel without a seam |
| `--red` | `#B5311F` | the site's button red: buttons, pills, hand labels, word chips, hot borders, strikes, the headline and FOMO line over footage |
| `--red-hot` | `#D24A36` | the lighter edge of red gradients, live dot, eyebrow labels on hot cards |
| `--gold` | `#C9A24A` | the site's accent gold: lines, icons, chart strokes, the "OR" connector |
| `--gold-hot` | `#E0BE66` | accent words (Fraunces italic), big numbers when they land, the spoken-word highlight in captions, "$3.8M placed" |
| `--cream` / `--ink` | `#FAF6EE` | all text on dark, caption text, cursor, the flash on section changes |
| `--sand` | `#F1EADD` | secondary text, avatars, the light half of the split bar |
| `--mute` | `#A89F90` | labels, quiet copy |
| warm tan | `#E3D3B5` | second avatar tone only |

No pure white, no yellow, no green, no blue accents anywhere. Status colours reuse the palette (live dot = red-hot,
"on a call" = gold-hot).

## Type

| Role | Face | Where |
|---|---|---|
| Card headings | Fraunces 600, sentence case | "Insurance changed", "The system", "Everyone else stops at", "Wednesday", "Virtual", "Create your free account" |
| Accent | Fraunces italic 500 | one accent word per scene ("changed", "system", "free account", "your next step") |
| Numbers | Fraunces 600 | 50%, 1:00, $464B, the domain on the end card |
| UI / buttons / node titles | Inter 500 / 700 (node titles uppercase, 0.05 em) | buttons, CRM rows, call bubbles, "SET THE APPOINTMENT" |
| Labels and tags | JetBrains Mono 600, uppercase, tracked | eyebrows, sources, timers, "401(K)", "MONEY SIGNAL", "OR" |
| Footage layer only | Montserrat Black, uppercase | captions, the hook headline, the proof card, hand labels, word chips |

Inside the cards the type is the site's (Fraunces, Inter, JetBrains Mono). Montserrat Black is the one exception and it
lives only on the footage layer, as the caption voice; it never appears inside a card.

## Shape and texture

- Corners: 6 px for small controls (pills, chips, buttons, rows), 14 px for cards (the site's panel radius). Captions, hand
  labels and word chips are square boxes (libass); at video scale that reads the same as 6 px.
- Cards: faint sand glass (6% to 1.5%), 1 px sand hairline at 13%, deep soft shadow. Hot state: red-hot border plus a
  soft red glow (36 px at 20%). Buttons are flat red, no gradient. No neon, no gradients as decoration.
- Lines: gold 3 px with a soft gold glow; a cream travelling dot while a line draws.
- Texture: no grid (the site is flat); 11% grain on graphics, which also dithers the dark gradients; warm vignette; the footage gets the `sma_pro.cube` grade, a
  face fill light, clarity and a 0.35 vignette so both worlds share contrast and warmth.
- Browser chrome in the sign-up scene: three neutral sand dots, address bar with the domain.

## Motion

- Everything lands on the spoken word (cue = word start). Enter: fade + 28 px rise + de-blur, 0.55 s, cubic out;
  pops use a back-ease from 85%. Exit is the reverse.
- Footage to graphic and back: the footage blurs (6 px then 14 px) over 0.25 s while the graphic fades. Card to card:
  a hard cut (80 ms), and the outgoing card clears its elements in its last 0.3 s. Never dissolve two text cards.
- A card never sits half empty: the element that lands later is already there as a 16% ghost.
- Word chips slide 70 px from the right over 170 ms. Hand labels pop from 55% over 7 frames and follow the hand.
- Punch-ins share one crop anchor (0.33), so the eye line never moves at a cut.
- Section changes on footage: zoom kick +10% easing out over 0.27 s and a whoosh. No flash frames. None inside or right
  after a cutaway.
- Captions: 2 to 5 words, split at punctuation and pauses, never starting or ending a chunk on a function word, at least
  0.3 s on screen. Proof card in the first half second, held until the first cutaway.

## Copy on screen

Only the owner's words or the site's own lines ("Create your free account →", "Free. Nothing moves. Takes about a
minute.", "setmoreannuities.com", "1 PM ET"). Numbers come from the site or `AUDIT.md`.
