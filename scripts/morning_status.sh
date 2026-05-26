#!/bin/bash
# scripts/morning_status.sh — Auto-status diario 11am MTY
# Genera STATUS_TODAY.md + manda notif macOS si algo crítico

PROJECT_DIR="/Users/fernandocastaneda/Documents/loop-video-maker"
cd "$PROJECT_DIR"

TODAY=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M MTY')
OUT="$PROJECT_DIR/STATUS_TODAY.md"

# ── Daemons status ───────────────────────────────────────────────────────
IG_DAEMON=$(launchctl list | grep com.versiculodedios.ig-daemon | awk '{print $1" "$2}')
YT_DAEMON=$(launchctl list | grep com.versiculodedios.yt-fb-uploader | awk '{print $1" "$2}')

# ── IG state ─────────────────────────────────────────────────────────────
IG_PUB=$(.venv/bin/python3 -c "
import json
try:
    d = json.load(open('data/ig_state.json'))
    pub = d.get('published', {})
    last = d.get('last_check', 'never')[:19]
    print(f'{len(pub)}|{last}')
except: print('0|never')
" 2>/dev/null)
IG_COUNT=$(echo $IG_PUB | cut -d'|' -f1)
IG_LAST=$(echo $IG_PUB | cut -d'|' -f2)

# ── YT/FB schedule status ────────────────────────────────────────────────
SCHED=$(.venv/bin/python3 -c "
import json
try:
    s = json.load(open('data/shorts_schedule.json'))
    yt = sum(1 for e in s['schedule'] if e.get('yt_id'))
    fb = sum(1 for e in s['schedule'] if e.get('fb_id'))
    total = len(s['schedule'])
    print(f'{yt}|{fb}|{total}')
except: print('0|0|0')
" 2>/dev/null)
YT_OK=$(echo $SCHED | cut -d'|' -f1)
FB_OK=$(echo $SCHED | cut -d'|' -f2)
TOTAL=$(echo $SCHED | cut -d'|' -f3)

# ── Errores en logs ──────────────────────────────────────────────────────
IG_ERR=$(grep -c "ERROR\|Exception" logs/ig_daemon.log 2>/dev/null || echo 0)
YT_FB_ERR=$(grep -c "error\|Error\|✗" logs/yt_fb_uploader.stderr 2>/dev/null || echo 0)

# ── Build report ─────────────────────────────────────────────────────────
cat > "$OUT" <<EOF
# 📅 Status — $TODAY $TIME

## Resumen rápido

- YT: **$YT_OK/$TOTAL** programados
- FB: **$FB_OK/$TOTAL** programados
- IG: **$IG_COUNT/$TOTAL** publicados (vía daemon)

## Daemons

| Daemon | Status | Notas |
|--------|--------|-------|
| ig-daemon | \`$IG_DAEMON\` | Última corrida: $IG_LAST |
| yt-fb-uploader | \`$YT_DAEMON\` | — |

## Errores

- IG daemon errors: $IG_ERR
- YT/FB uploader errors: $YT_FB_ERR

## Schedule pendientes hoy y mañana

EOF

.venv/bin/python3 <<PYEOF >> "$OUT"
import json
from datetime import datetime, timezone, timedelta
MTY = timezone(timedelta(hours=-6))
now = datetime.now(MTY)
try:
    s = json.load(open('data/shorts_schedule.json'))
    ig_state = json.load(open('data/ig_state.json')) if __import__('os').path.exists('data/ig_state.json') else {'published': {}}
    ig_pub = ig_state.get('published', {})

    upcoming = []
    for e in s['schedule']:
        try:
            t = datetime.strptime(e['publish_mty'], '%Y-%m-%d %H:%M MTY').replace(tzinfo=MTY)
            if (t - now).total_seconds() > -3600 and (t - now).total_seconds() < 172800:  # ±1h to +48h
                upcoming.append((t, e))
        except: pass

    if upcoming:
        print('| Fecha MTY | ID | YT | FB | IG |')
        print('|-----------|-----|-----|-----|-----|')
        for t, e in sorted(upcoming):
            yt = '✅' if e.get('yt_id') else '❌'
            fb = '✅' if e.get('fb_id') else '❌'
            ig = '✅' if e['id'] in ig_pub else '⏳'
            print(f"| {t.strftime('%m-%d %H:%M')} | {e['id']} | {yt} | {fb} | {ig} |")
    else:
        print('Sin items próximos en ventana ±48h.')
except Exception as ex:
    print(f'Error reading schedule: {ex}')
PYEOF

cat >> "$OUT" <<EOF

## Logs recientes (últimas 5 líneas)

### ig_daemon.log
\`\`\`
$(tail -5 logs/ig_daemon.log 2>/dev/null || echo "no log")
\`\`\`

### yt_fb_uploader.stdout
\`\`\`
$(tail -5 logs/yt_fb_uploader.stdout 2>/dev/null || echo "no log")
\`\`\`

---
_Generado automático por \`scripts/morning_status.sh\` vía launchd com.versiculodedios.morning-status._
EOF

# ── Notif macOS ─────────────────────────────────────────────────────────
ALERT=""
if [ "$IG_ERR" -gt 0 ] || [ "$YT_FB_ERR" -gt 0 ]; then
    ALERT="⚠️ Errores: IG=$IG_ERR YT/FB=$YT_FB_ERR"
fi

MSG="YT $YT_OK/$TOTAL · FB $FB_OK/$TOTAL · IG $IG_COUNT/$TOTAL"
[ -n "$ALERT" ] && MSG="$MSG · $ALERT"

osascript -e "display notification \"$MSG\" with title \"VersiculoDeDios Status\" subtitle \"$TODAY $TIME\""

echo "Status generado: $OUT"
