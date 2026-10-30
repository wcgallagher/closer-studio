#!/usr/bin/env bash
# Double-click me. Opens Claude Code inside the Closer Studio folder.
cd "$(dirname "$0")"
export PATH="$HOME/.closer-studio/venv/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code is not installed yet. Get it at https://claude.ai/code, then double-click this again."
  read -r -p "Press Enter to close."
  exit 1
fi
echo "Closer Studio. Put raw videos in the inbox folder, then tell Claude what you want."
echo "Example: make a reel from the video in inbox"
echo
claude
