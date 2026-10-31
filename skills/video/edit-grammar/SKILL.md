---
name: edit-grammar
description: The house editing brain. Loads the measured rules (hook deadline, visual change clock, late payoff, caption zoning, end on the payoff) and the three dialects we cut in (Hormozi idea density, Gadzhi premium minimal, Nelk energy), then maps a brief to engine settings. Use before any edit decision, when someone asks "how should this be cut", "make it feel like Hormozi / Gadzhi / Nelk", "why does this feel slow", or when planning a montage, a VSL or a long-form video.
---

# Edit grammar

Read `EDITING_GRAMMAR.md` at the kit root. It is short. Every number in it has a source row in `RESEARCH.md`.

## Use it like this

1. Name the format: short (reel) or long (YouTube, VSL). The clock changes with it (hook by 2.5 s or 10 s; a visible
   change every 3 to 8 s or a layout flip every 20 to 40 s; payoff at 55 to 85 % or a verdict hold at 72 % plus).
2. Name the dialect from the brief and the brand table in section 3 of `EDITING_GRAMMAR.md`:
   - "punchy", "Hormozi", advice monologue, listicle: idea density. Engine: `--style impact` or `clean`, punch-ins on,
     fillers kept, no music or a faint bed, no CTA inside the clip.
   - "premium", "clean", "Gadzhi", "cinematic": premium minimal. Engine: `--style serif` or `clean`, `--hook-serif`,
     `--grade cinematic` or the brand LUT, cards from `tools/vsl/mg/scenes.html`, slow continuous motion.
   - "hype", "Nelk", montage, event recap: energy. Engine: `--riser`, hits on, music bed, hard cuts on the beat,
     smash to black between sections, establishing shot after it.
3. Build the beat map from the job's transcript.txt (one claim per beat; mark hook and payoff). Check the payoff lands past
   the halfway mark. If not, change the window before you touch the look.
4. Run the engine, then check the clock with the report and the sheet.

## Things people ask for that we refuse

- "Add emoji captions and a yellow box and a bounce": three emphasis mechanisms. Offer one.
- "Remove every um": only for scripted or corporate pieces. On a talking-head reel the fillers carry trust.
- "Add a follow-for-more at the end": the clip ends on the payoff; the end card carries the one call to action.
- "Put the stat on screen": only if the footage or the brand sheet contains it.
