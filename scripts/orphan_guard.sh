#!/bin/bash
# Daily orphan-upload guard wrapper (launchd). Runs the guard with --alert so any
# HIGH-severity orphan fires a venom-tone WhatsApp. See scripts/orphan_guard.py.
set -uo pipefail
cd /Users/fernandocastaneda/Documents/loop-video-maker || exit 1

# launchd gives a minimal PATH; heroku CLI (for WASENDER_API_KEY) lives in these dirs.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Catch-up semantics (BUG-4 fix): plist runs this at 8pm AND on every load/login
# (RunAtLoad). The 8pm slot always runs. On login we only run if the last report is
# stale (>12h) — i.e. a genuinely missed day, not every login. Prevents alert-spam
# while guaranteeing a missed run gets caught up when the Mac wakes.
HOUR=$(date '+%H')
REPORT="data/orphan-uploads.json"
if [ "$HOUR" != "20" ] && [ -f "$REPORT" ]; then
    AGE_H=$(( ( $(date +%s) - $(stat -f %m "$REPORT") ) / 3600 ))
    if [ "$AGE_H" -lt 12 ]; then
        echo "=== orphan_guard $(date '+%Y-%m-%d %H:%M:%S') — skip (report ${AGE_H}h old, not stale) ==="
        exit 0
    fi
    echo "=== orphan_guard CATCH-UP (report ${AGE_H}h old) ==="
fi

echo "=== orphan_guard $(date '+%Y-%m-%d %H:%M:%S') ==="
.venv/bin/python3 scripts/orphan_guard.py --alert --window 14
echo "exit=$? (0=clean 1=LOW 2=HIGH)"
