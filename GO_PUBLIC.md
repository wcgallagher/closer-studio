# Publishing this kit and getting Owen and Antonio on it

**Status (2026-10-31):** live and public at https://github.com/wcgallagher/closer-studio (branch `main`). Owen and Antonio were
emailed the four setup steps the same night. The steps below stay here for the next brand or the next partner.

## What "public" means here

A public repo is readable by anyone on the internet, including the sales thinking in `skills/sales/closer-mentality`
and the brand tokens. If that is fine (it reads as authority marketing), go public. If not, make the repo **private**
and add Owen and Antonio as collaborators: same three steps for them, they just need a free GitHub account.

## Step 1. Create the repo (2 minutes, in the browser)

1. Go to https://github.com/new (signed in as the account that will own it).
2. Repository name: `closer-studio`. Visibility: **Public** (or Private, see above). Leave "Add a README" unchecked.
3. Click **Create repository**. Leave that page open; it shows the repo address, for example
   `https://github.com/wcgallagher/closer-studio.git`.

## Step 2. Put the kit in it (one of two ways)

**A. From this Claude session.** Tell Claude: "the repo is created at github.com/wcgallagher/closer-studio, push the kit".
Claude attaches the repo and pushes the `closer-studio` branch as `main`. If the session cannot attach it
(a permission prompt declines), use B.

**B. From your Mac, in the Claude Code app.** Open the `closer-studio` folder (unzip the file Claude sent, or download
the branch from GitHub) and say: "publish this folder to github.com/wcgallagher/closer-studio as main". Claude will run,
and you can run yourself in Terminal from inside the folder:

```bash
git init -b main
git add -A
git commit -m "Closer Studio"
git remote add origin https://github.com/wcgallagher/closer-studio.git
git push -u origin main
```

GitHub asks you to sign in once (a browser window, or a token). After that, the page https://github.com/wcgallagher/closer-studio
shows the kit with its README.

## Step 3. Add people (private repo only)

Repo page, **Settings**, **Collaborators**, **Add people**, their GitHub username or email, **Write** access.

## Step 4. What Owen and Antonio do (5 minutes each, no Terminal)

1. Open https://github.com/wcgallagher/closer-studio. Click the green **Code** button, then **Download ZIP**. Double-click
   the zip. Move the `closer-studio` folder to Documents.
2. Install the Claude Code desktop app from https://claude.ai/code and sign in.
3. In Claude Code: **Open folder**, pick `closer-studio`. Type `set me up`. Click **Allow** when asked. Wait for **Done**.
4. Put a video in `closer-studio/inbox`, come back to Claude, say `make a reel from the video in inbox`.

That is the whole onboarding. The folder's own `CLAUDE.md` tells their Claude how to behave, which skills to use and
what never to say.

## Step 5. Updating later

When the kit changes: push the new version (step 2), they download the ZIP again and replace their folder, then say
`set me up` once more. Their `inbox` and `output` folders are theirs; copy them across.

## Antonio's brand

Open the folder in Claude Code and say: "add a brand for <site>". Claude follows `skills/brand/brand-kit/SKILL.md`,
scrapes the site, writes `brand/<id>.json`, and from then on `--brand <id>` makes every reel and card match that site.
