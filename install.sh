#!/usr/bin/env bash
# Closer Studio installer. Safe to run again any time.
#  - ffmpeg, Python 3 and the engine's packages (Mac: via Homebrew), in their own venv at ~/.closer-studio/venv
#  - the caption and display fonts
#  - every skill copied where Claude Code loads it from (~/.claude/skills)
#  - optional: --deep-filter downloads the DeepFilterNet noise-removal binary (28 MB)
#  - optional: --scenes installs Node.js and Playwright's Chromium for the animated VSL scenes (about 150 MB)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok() { printf '  ok  %s\n' "$1"; }
WANT_DF=0; WANT_SC=0; for a in "$@"; do [ "$a" = "--deep-filter" ] && WANT_DF=1; [ "$a" = "--scenes" ] && WANT_SC=1; done

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

say "Installing the engine's Python packages (first time takes a few minutes)"
VENV="$HOME/.closer-studio/venv"
if [ ! -x "$VENV/bin/python" ]; then python3 -m venv "$VENV"; fi
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q numpy scipy pillow faster-whisper opencv-python-headless "scenedetect[opencv]"
ok "python packages"

# 2. fonts
if [[ "$(uname)" == "Darwin" ]]; then FONTDIR="$HOME/Library/Fonts"; else FONTDIR="$HOME/.fonts"; fi
mkdir -p "$FONTDIR" && cp "$HERE"/fonts/*.ttf "$FONTDIR"/ && ok "fonts (Montserrat, Fraunces Display)"
command -v fc-cache >/dev/null 2>&1 && fc-cache -f >/dev/null 2>&1 || true

# 3. skills into Claude Code
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
count=0
for skill in "$HERE"/skills/*/*/; do
  [ -f "$skill/SKILL.md" ] || continue
  name="$(basename "$skill")"
  rm -rf "${DEST:?}/${name:?}"
  mkdir -p "$DEST/$name" && cp -R "${skill%/}/." "$DEST/$name/"
  count=$((count + 1))
done
ok "$count skills installed into $DEST"

# 4. a pointer so the skills can find the tools from any folder
mkdir -p "$HOME/.closer-studio" && printf '%s' "$HERE" > "$HOME/.closer-studio/kit_path"
mkdir -p "$HERE/inbox" "$HERE/output"
chmod +x "$HERE/Start Closer Studio.command" 2>/dev/null || true
ok "kit path recorded"

# 5. optional: DeepFilterNet standalone binary (Rikorose/DeepFilterNet v0.5.6, MIT / Apache-2.0)
if [ "$WANT_DF" = 1 ]; then
  BIN="$HOME/.closer-studio/bin"; mkdir -p "$BIN"
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) ASSET="deep-filter-0.5.6-aarch64-apple-darwin"; SIZE=27877081 ;;
    Darwin-x86_64) ASSET="deep-filter-0.5.6-x86_64-apple-darwin"; SIZE=29933512 ;;
    Linux-x86_64) ASSET="deep-filter-0.5.6-x86_64-unknown-linux-musl"; SIZE=36417296 ;;
    Linux-aarch64) ASSET="deep-filter-0.5.6-aarch64-unknown-linux-gnu"; SIZE=39238496 ;;
    *) ASSET="" ;;
  esac
  if [ -n "$ASSET" ]; then
    say "Downloading DeepFilterNet ($ASSET)"
    curl -fsSL -o "$BIN/deep-filter" "https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/$ASSET"
    GOT=$(wc -c < "$BIN/deep-filter" | tr -d ' ')
    if [ "$GOT" = "$SIZE" ]; then chmod +x "$BIN/deep-filter"; ok "deep-filter installed ($GOT bytes)"; else rm -f "$BIN/deep-filter"; echo "  download size mismatch ($GOT vs $SIZE); skipped"; fi
  else
    echo "  no DeepFilterNet build for this machine; skipped"
  fi
fi

# 6. optional: Node.js + Playwright Chromium, to render the animated scenes in tools/vsl/mg (VSL cards)
if [ "$WANT_SC" = 1 ]; then
  if ! command -v node >/dev/null 2>&1; then
    if [[ "$(uname)" == "Darwin" ]]; then say "Installing Node.js"; brew install node; else echo "  node is missing: install Node.js 18 or newer and run this again"; exit 1; fi
  fi
  ok "node $(node --version)"
  say "Installing Playwright and its Chromium (about 150 MB, first time only)"
  (cd "$HERE/tools/vsl/mg" && npm install --silent --no-audit --no-fund && npx --yes playwright@1.63.0 install chromium)
  ok "animated scenes ready"
fi

say "Done. Open this folder in Claude Code and say what you want."
if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code itself is not installed yet: get it at https://claude.ai/code, then run this again."
fi
