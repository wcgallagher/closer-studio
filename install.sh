#!/usr/bin/env bash
# Closer Studio installer. Safe to run again any time.
#  - puts every skill where Claude Code loads it from (~/.claude/skills)
#  - makes sure ffmpeg, Python 3 and the speech-to-text package are there (Mac: via Homebrew)
#  - installs the caption fonts
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok() { printf '  ok  %s\n' "$1"; }

say "Closer Studio: setting up"

# 1. tools
if ! command -v ffmpeg >/dev/null 2>&1; then
  if [[ "$(uname)" == "Darwin" ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      say "Installing Homebrew (the Mac package manager). It may ask for your Mac password."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
    fi
    say "Installing ffmpeg (video engine)"
    brew install ffmpeg
  else
    echo "ffmpeg is missing. Install it with your package manager (for example: sudo apt install ffmpeg) and run this again."
    exit 1
  fi
fi
ok "ffmpeg $(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}')"

if ! command -v python3 >/dev/null 2>&1; then
  if [[ "$(uname)" == "Darwin" ]]; then say "Installing Python 3"; brew install python; else echo "python3 is missing"; exit 1; fi
fi
ok "python3 $(python3 --version 2>&1 | awk '{print $2}')"

say "Installing the speech-to-text package (first time takes a minute)"
VENV="$HOME/.closer-studio/venv"
if [ ! -x "$VENV/bin/python" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q numpy scipy pillow faster-whisper
ok "python packages"

# 2. fonts
if [[ "$(uname)" == "Darwin" ]]; then FONTDIR="$HOME/Library/Fonts"; else FONTDIR="$HOME/.fonts"; fi
mkdir -p "$FONTDIR" && cp "$HERE"/fonts/*.ttf "$FONTDIR"/ && ok "fonts (Montserrat)"
command -v fc-cache >/dev/null 2>&1 && fc-cache -f >/dev/null 2>&1 || true

# 3. skills into Claude Code
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
count=0
for skill in "$HERE"/skills/*/*/; do
  [ -f "$skill/SKILL.md" ] || continue
  name="$(basename "$skill")"
  rm -rf "$DEST/$name"
  mkdir -p "$DEST/$name" && cp -R "${skill%/}/." "$DEST/$name/"
  count=$((count + 1))
done
ok "$count skills installed into $DEST"

# 4. a pointer so the skills can find the tools from any folder
mkdir -p "$HOME/.closer-studio"
echo "$HERE" > "$HOME/.closer-studio/kit_path"
mkdir -p "$HERE/inbox" "$HERE/output"
chmod +x "$HERE/Start Closer Studio.command" 2>/dev/null || true

say "Done."
echo "Next: put a video in the folder  $HERE/inbox"
echo "then double-click  'Start Closer Studio.command'  and tell Claude what you want."
if ! command -v claude >/dev/null 2>&1; then
  echo
  echo "Claude Code itself is not installed yet. Get it at https://claude.ai/code and run this installer again."
fi
