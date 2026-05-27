#!/bin/bash
# Instala los 4 daemons de VersiculoDeDios en ~/Library/LaunchAgents/
# Correr después de clonar repo en Mac nueva o después de resetear daemons.
#
# Requisito previo — FDA (Full Disk Access) para /bin/bash:
#   System Settings → Privacy & Security → Full Disk Access → agregar /bin/bash
#
# Uso: bash scripts/launchd/install_daemons.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LAUNCHD_SRC="$REPO_DIR/scripts/launchd"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

PLISTS=(
    "com.versiculodedios.ig-daemon"
    "com.versiculodedios.yt-fb-uploader"
    "com.versiculodedios.morning-status"
    "com.versiculodedios.wake-reminder"
)

echo "Repo: $REPO_DIR"
echo ""

for label in "${PLISTS[@]}"; do
    src="$LAUNCHD_SRC/$label.plist"
    dst="$LAUNCH_AGENTS/$label.plist"

    # Unload si existe
    if launchctl list | grep -q "$label" 2>/dev/null; then
        echo "Unloading $label..."
        launchctl unload "$dst" 2>/dev/null || true
    fi

    cp "$src" "$dst"
    launchctl load "$dst"

    exit_code=$(launchctl list | grep "$label" | awk '{print $2}')
    echo "✅ $label → exit $exit_code"
done

echo ""
echo "Done. Verify with: launchctl list | grep versiculodedios"
echo ""
echo "Si algún daemon falla (exit != 0):"
echo "  cat $REPO_DIR/logs/<daemon>.stderr"
