# Closer Studio

Everything Claude Code needs to cut reels, VSLs and long-form video for Become The Closer and Set More Annuities,
with the brand, the writing rules and the sales thinking already loaded. Built by Chase's Claude; made for Owen.

## Set up (once, about 5 minutes, Mac)

1. Get the `closer-studio` folder onto your Mac. Either unzip the file Chase sent you, or on this GitHub page click
   the green **Code** button, then **Download ZIP**, then double-click the zip. Put the folder somewhere you can find it
   (your home folder or Documents is fine).
2. Open the **Claude Code** app. Choose **Open folder** and pick the `closer-studio` folder.
3. Type: `set me up` and press Enter. Claude installs what it needs (a video engine and a speech-to-text package).
   It will ask for permission a few times: click **Allow**. If your Mac asks for your password, that is normal.
4. When Claude says **Done**, you are set.

No Terminal, no commands to remember.

## Every time you want to edit

1. Put your raw video files in the folder `closer-studio/inbox` (Finder: open the `closer-studio` folder, then `inbox`).
2. Open the `closer-studio` folder in the Claude Code app (it remembers it under recent projects).
3. Type what you want, in plain words. Examples:
   - `make a reel from the video in inbox`
   - `cut three reels from this call: the part about objections, the part about the quiz, and the close`
   - `make a VSL from these three takes for becomethecloser.com`
   - `write the caption and hook for this reel`
4. Finished videos land in `closer-studio/output`. Claude tells you the file name.

## If something goes wrong

Tell Claude "this failed" and paste whatever it showed you. It fixes it. If it cannot, send it to Chase.

## Terminal users (optional)

If you use the Claude Code command line instead of the app: open Terminal in the folder, run `bash install.sh` once,
then start Claude with the double-click file **Start Closer Studio.command** or by typing `claude`.

Windows: the installer is written for Mac. On Windows use WSL and ask Chase to walk through it once.

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

The skills are also wired into this folder's own `.claude/skills`, so they load the moment the folder is open in the
app, even before setup finishes.

## Credits and licences

See `CREDITS.md`. Fonts are Open Font License, icons ISC, the bundled music track is Kevin MacLeod (CC BY 4.0, credit
him when you use it).
