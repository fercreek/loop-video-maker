#!/bin/bash
# keep_awake.sh — corre un comando manteniendo la Mac despierta, ATADO AL PROCESO (no a un timer).
# Mata la causa de fallo de la noche: caffeinate -t Nh vencía + lid-close en batería lo ignoraba.
#
# Uso:  bash scripts/keep_awake.sh .venv/bin/python3 render_sleep.py --tema salmo91 --duration 120
#       KEEP_AWAKE_FORCE=1 bash scripts/keep_awake.sh <cmd>   # ignora el check de batería (riesgo)
#
# Regla dura: en BATERÍA aborta — caffeinate NO evita el sleep por cerrar la tapa en batería.

if [ $# -eq 0 ]; then echo "uso: keep_awake.sh <comando...>"; exit 2; fi

if ! pmset -g batt 2>/dev/null | grep -q "AC Power"; then
  echo "⛔ keep_awake: la Mac está en BATERÍA."
  echo "   caffeinate no evita el sleep si cierras la tapa en batería → el render moriría a medias."
  echo "   👉 Enchúfala y reintenta (o KEEP_AWAKE_FORCE=1 para ignorar, bajo tu riesgo)."
  [ "$KEEP_AWAKE_FORCE" = "1" ] || exit 1
  echo "   ⚠️  KEEP_AWAKE_FORCE=1 — continúo en batería."
fi

# caffeinate atado al PID de ESTA shell → vive exactamente lo que viva el comando, ni más ni menos.
caffeinate -dimsu -w $$ &
_CAFF=$!
echo "☕ keep_awake activo (caffeinate $_CAFF atado a PID $$) — corriendo: $*"
"$@"
_RC=$?
kill "$_CAFF" 2>/dev/null
echo "☕ keep_awake liberado (exit $_RC)"
exit $_RC
