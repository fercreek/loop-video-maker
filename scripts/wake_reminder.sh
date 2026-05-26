#!/bin/bash
# wake_reminder.sh — Notif macOS para recordar abrir Claude + cargar contexto sesión.
# Corre 10am MTY diario hasta que pendientes resueltos.

PROJECT="/Users/fernandocastaneda/Documents/loop-video-maker"
SPEC="$PROJECT/docs/SESSION_SPEC_2026-05-25.md"

# Solo notif si spec existe + hay pendientes
if [ ! -f "$SPEC" ]; then exit 0; fi

# Mensaje basado en estado
YT_PENDING=$(grep -c "yt_id.*null\|\"yt_id\": null" "$PROJECT/data/shorts_schedule.json" 2>/dev/null || echo 0)
IG_PUBLISHED=$(/usr/bin/python3 -c "
import json,os
try:
    if os.path.exists('$PROJECT/data/ig_state.json'):
        d=json.load(open('$PROJECT/data/ig_state.json'))
        print(len(d.get('published',{})))
    else: print(0)
except: print(0)
" 2>/dev/null)

MSG="VersiculoDeDios pendientes — YT pend: $YT_PENDING · IG pub: $IG_PUBLISHED/20"
osascript -e "display notification \"$MSG\" with title \"📋 Loop Video — Abre Claude\" subtitle \"Lee docs/SESSION_SPEC_2026-05-25.md\" sound name \"Glass\""
