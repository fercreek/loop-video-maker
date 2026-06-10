#!/bin/bash
# Daily orphan-upload guard wrapper (launchd). Runs the guard with --alert so any
# HIGH-severity orphan fires a venom-tone WhatsApp. See scripts/orphan_guard.py.
set -uo pipefail
cd /Users/fernandocastaneda/Documents/loop-video-maker || exit 1

# launchd gives a minimal PATH; heroku CLI (for WASENDER_API_KEY) lives in these dirs.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

echo "=== orphan_guard $(date '+%Y-%m-%d %H:%M:%S') ==="
.venv/bin/python3 scripts/orphan_guard.py --alert --window 14
echo "exit=$? (0=clean 1=LOW 2=HIGH)"
