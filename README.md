# Closer Studio

Everything Claude Code needs to cut reels, VSLs and long-form video for Become The Closer and Set More Annuities,
with the brand, the writing rules and the sales thinking already loaded. Built by Chase's Claude; made for Owen.

## Install (once, about 5 minutes)

You need a Mac with Claude Code already installed. If you do not have Claude Code yet: https://claude.ai/code

1. Open **Terminal** (press Cmd + Space, type `Terminal`, press Enter).
2. Paste this whole line and press Enter. It downloads the kit into a folder called `closer-studio` in your home folder and installs it:

```bash
cd ~ && git clone https://github.com/wcgallagher/sellmoreannuities.git --branch closer-studio --single-branch closer-studio && cd closer-studio && bash install.sh
```

3. When it says **Done**, you are set up. If it asks to install something (ffmpeg, Python packages), say yes.

## Every time you want to edit

1. Put your raw video files in the folder `closer-studio/inbox` (Finder: your home folder, then `closer-studio`, then `inbox`).
2. Double-click **Start Closer Studio.command** in the `closer-studio` folder. Terminal opens with Claude ready.
3. Type what you want, in plain words. Examples:
   - `make a reel from the video in inbox`
   - `cut three reels from this call: the part about objections, the part about the quiz, and the close`
   - `make a VSL from these three takes for becomethecloser.com`
   - `write the caption and hook for this reel`
4. Finished videos land in `closer-studio/output`. Claude tells you the file name.

That is the whole workflow. You never need to open the tools yourself.

## What is inside

| Folder | What it is |
|---|---|
| `skills/video/reel-editor` | 9:16 reels: cut dead air, punch-ins, big captions, hook, brand end card, clean voice, graded picture |
| `skills/video/vsl-producer` | long-form VSLs with animated cutaways, the way the Set More Annuities VSL was built |
| `skills/sales/closer-mentality` | the house sales thinking, so every hook, caption and cut sells the way we sell |
| `skills/copy/*` | long-form copy, a trust scorecard that catches manipulative or fake-sounding copy, delivery and authority notes |
| `skills/media-buying/*` | 49 skills for ads, audits, landing pages, SEO, reports |
| `skills/core/zero-context-auditor` | the rule that no skill or claim ships without a source |
| `brand/` | the colour, type and copy sheets for becomethecloser.com and setmoreannuities.com |
| `tools/` | the scripts the skills run (you never run them yourself) |
| `HOUSE_RULES.md` | writing rules that apply to everything: no em dashes, no hype words, no invented numbers |

## If something goes wrong

Copy the red text from Terminal and paste it to Claude with "this failed". Claude fixes it. If Claude cannot, send it
to Chase.

## Credits and licences

See `CREDITS.md`. Fonts are Open Font License, icons ISC, the bundled music track is Kevin MacLeod (CC BY 4.0, credit
him when you use it).
