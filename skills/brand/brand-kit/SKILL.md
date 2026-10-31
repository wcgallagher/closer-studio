---
name: brand-kit
description: Adds or updates a brand for the video engine (colours, fonts, call to action, caption style, grade, banned words) from a website or a brand sheet, so every reel, card and end card for that brand comes out on-brand without flags. Use when a new company joins (Antonio's brand, a client), when someone says "make it match my site", or when a brand's colours or CTA change.
---

# Brand kit

A brand is one JSON file: `brand/<id>.json`. The engine reads it for the end card, the caption colours, the hook, the
grade and the banned-word check. `brand/btc.json` and `brand/sma.json` are the two shipped examples.

## Add a brand

1. Get the tokens from the source of truth, in this order: the live website (scrape it: background, button colour,
   headline font, body font, the exact call-to-action line, the handle), then a brand sheet if one exists. Write what
   you found and where in `brand/<id>.md` (two paragraphs: colours and type with hex codes, the site's own lines).
2. Write `brand/<id>.json`:

```json
{
  "id": "acme", "name": "Acme", "site": "acme.com", "handle": "@acme",
  "colors": {"bg": "#0B0B0C", "accent": "#F2C14E", "accent_soft": "#F7D98A", "text": "#F5F2EC", "muted": "#9A958C", "panel": "#1C1C1F"},
  "fonts": {"caption": "Montserrat Black", "caption_file": "Montserrat-Black.ttf", "caption_2": "Montserrat ExtraBold", "caption_2_file": "Montserrat-ExtraBold.ttf",
            "display": "Fraunces Display", "display_file": "FrauncesDisplay-Bold.ttf", "mono": "JetBrains Mono"},
  "cta": {"line": "Book a call", "sub": "acme.com"},
  "style": {"captions": "clean", "lut": "clean", "music": "", "grain": 0.0},
  "words": {"never": [], "result_disclaimer": ""},
  "source": "brand/acme.md (scrape of acme.com, <date>)"
}
```

   - `colors.bg` is the end-card and card background (the 60 % colour), `panel` the 30 %, `accent` the 10 %. Keep the
     accent readable on the background (a light accent on a dark background, never two mid-tones).
   - Fonts must exist in `fonts/`. Drop a brand's own TTF there and name it; the caption face must be heavy (Black or
     ExtraBold) or captions will not read at phone size.
   - `style.lut`: `clean`, `btc_ember`, `sma_pro`, `cinematic` or `none`. `style.captions`: `impact`, `clean`, `serif`, `boxed`.
   - `words.never`: words the engine refuses in a hook or CTA and flags in captions (compliance words, competitor
     names, "free" when it is not).
3. Check: `python3 tools/closer.py brands` lists it. Render one 10 s preview reel with `--brand <id>` and look at the
   end card and a caption frame.

## Rules

- Never guess a hex code from memory. Scrape or ask.
- Never write a CTA line the site does not use.
- A brand's "never" list is a floor, not a style choice: add to it, do not remove from it without the owner.
