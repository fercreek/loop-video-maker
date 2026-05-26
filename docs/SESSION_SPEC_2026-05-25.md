# 📋 Session Spec — 2026-05-25 (Batch venom + Sleep pipeline + Auto-publish)

> **Spec-kit principal de esta sesión** — punto de entrada para próxima sesión Claude.
> Si abres Claude nuevo, lee este archivo PRIMERO (junto con `_NEXT.md`).
> Esto es el contexto canónico — no se pierde aunque cierres chat.

---

## 🎯 Qué se hizo esta sesión

### Producción (20 videos venom Shorts)
- 20 oraciones devocionales escritas en `data/oraciones_pool.json` como `venom_001` a `venom_020`
- Fórmula: replica del Short top performer `bi_B78HZuJ4` (27% watch time canal, 127.6% retención)
- Cada uno tiene mismatch título-narración intencional (replay-trigger)
- Split A/B: 10 voz Dalia + 10 voz Jorge
- Todos rendered + QA 9-10/10 en `output/shorts/semana_2026-05-25/`

### Bugs críticos arreglados (5 + 5 = 10 total)
**Mañana (sesión 1):**
1. EQ silenciador (-91dB) en `core/shorts_render.py:546` — `t=o:w=3000` (octavas nonsense)
2. Fondo congelado 2da mitad — `t_offset=t_switch` en `_build_bg_ffmpeg`
3. FG estático en zoom_in/zoom_out — faltaba `zoompan`
4. Audio LUFS -39 → -16 — loudnorm post-mix + `amix normalize=0`
5. Watermark duplicado — quitar ffmpeg drawtext, mantener Pillow

**Tarde-noche (sesión gym):**
6. Pixel-threshold WM detection false-negatives
7. YT quota daily 6 uploads (script abortaba en 429)
8. FB error 429-like
9. Drawtext recurrente en pipelines nuevos
10. Overlay `alpha` option no existe

### Pipeline nuevo: Sleep videos
- `render_sleep.py` v1 — 60-120 min audio ambient + Ken-Burns ultra-lento + overlay título
- 5 temas preset: salmo91, salmo23, ansiedad, promesas, rosario
- Test 60min Salmo 91 → QA 10/10 PASS
- Math YPP: 10 sleeping × 1.5h × 200 views × 50% ret = 15K h/año → desbloquea YPP en 6-8 semanas

### Tooling nuevo
- `scripts/qa_short.py` — QA Shorts (motion SSIM, LUFS, sync, duration)
- `scripts/qa_longform.py` — QA adaptado long-form
- `scripts/upload_shorts_venom.py` — batch uploader con skip-auto + try/except
- `scripts/ig_daemon.py` — IG idempotent uploader con catch-up
- `scripts/morning_status.sh` — auto-status diario 11am
- `scripts/dashboard_server.py` — local dashboard puerto 8090
- `dashboard.html` — UI live para daemons
- `~/Documents/new-focus/daemons.30s.sh` — SwiftBar plugin menubar

### Agente nuevo
- `~/.claude/agents/shorts-qa.md` — supervisor QA pre-upload con bugs conocidos #1-10

### Documentación creada
- `_SCHEDULE_VENOM.md` — living spec tabla 20 días × plataforma
- `docs/SLEEPING_PIPELINE.md` — spec sleep content + math YPP
- `docs/YT_QUOTA_INCREASE.md` — plantilla request Google
- `REPORT_GYM_SESSION.md` — wrap-up sesión gym
- `logs/LEARNINGS.md` — 10 bugs documentados
- Este archivo

### Git
- Branch: `feat/venom-shorts-batch-sleep-pipeline`
- 7 commits ordenados por feature
- PR open: https://github.com/fercreek/loop-video-maker/pull/1

---

## 📤 Estado upload (al cerrar sesión)

| Plataforma | Subidos | Pendientes | Cómo resolver |
|------------|---------|------------|---------------|
| **YouTube** | 7/20 (venom_001, 004, 009, 002, 005, 010, 007) | 13 | Manualmente: `python3 scripts/upload_shorts_venom.py` (skip-ea auto los OK) |
| **Facebook** | 18/20 | 2 (venom_007, 020) | Mismo comando |
| **Instagram** | 0/20 | 20 | Manual Meta Business Suite o fix FDA |

**Cada video subido tiene `publish_at` futuro distinto** — YT+FB publican solos en sus fechas (May 26 → Jun 14, 1/día 5am MTY).

---

## 🔴 BLOQUEO CRÍTICO PENDIENTE

### macOS TCC bloquea launchd acceso a `~/Documents/`

**Síntoma:** Los 3 daemons LaunchAgent que creé fallan con `PermissionError: Operation not permitted` al leer `pyvenv.cfg` o ejecutar scripts en Documents.

**Daemons afectados:**
- `com.versiculodedios.ig-daemon` — IG auto-publish 5:10am
- `com.versiculodedios.yt-fb-uploader` — YT+FB pendientes 1:30am
- `com.versiculodedios.morning-status` — Status diario 11am

**Fix (Fernando acción manual — 30 segundos):**

1. Abrir: `open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"`
2. Click 🔓 + Touch ID
3. Click **+** → agregar:
   - `/bin/bash`
   - `/usr/bin/python3`
4. Habilitar ambos (toggle azul)
5. Recargar daemons:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.versiculodedios.*.plist
   launchctl load ~/Library/LaunchAgents/com.versiculodedios.*.plist
   ```
6. Validar: `bash scripts/morning_status.sh` → debe correr sin error

**Alternativa (más limpia, requiere break-fix):** mover proyecto a `~/Code/` (fuera Documents). Plists necesitan path update.

**Mientras NO se resuelve:**
- 7 YT + 18 FB ya subidos publican SOLOS (no necesitan daemon)
- IG: 20 pendientes sin auto-publish — opciones:
  - Manual Meta Business Suite UI (bulk schedule)
  - Cron manual diario: tú corres `python3 scripts/ig_daemon.py` cada mañana
- YT pendientes: tú corres `python3 scripts/upload_shorts_venom.py` mañana después quota reset (~1am MTY)

---

## 🛠 Cómo retomar mañana (sin perder contexto)

### 1. Lee archivos en orden (boot sequence)
```
1. docs/SESSION_SPEC_2026-05-25.md  ← este archivo
2. _NEXT.md                          ← pendientes actualizados
3. _SCHEDULE_VENOM.md                ← tabla maestro upload
4. REPORT_GYM_SESSION.md             ← wrap-up sesión hoy
5. logs/LEARNINGS.md (último entry)  ← bugs nuevos
6. CLAUDE.md (repo)                  ← reglas técnicas
```

### 2. Verifica si Fernando hizo FDA grant
```bash
# Test rápido:
launchctl start com.versiculodedios.morning-status
sleep 2
tail logs/morning_status.stderr   # vacío = OK | error = aún pendiente
```

### 3. Si FDA OK → recargar todos
```bash
launchctl unload ~/Library/LaunchAgents/com.versiculodedios.*.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.versiculodedios.*.plist
launchctl list | grep versiculodedios   # deben aparecer 4
```

### 4. Validar status real publicaciones
```bash
.venv/bin/python3 scripts/ig_daemon.py --status
cat STATUS_TODAY.md 2>/dev/null
open http://127.0.0.1:8090/dashboard.html  # primero arranca server: python3 scripts/dashboard_server.py &
```

### 5. Decidir próximo paso con Fernando
- ¿Subir 13 YT pendientes manual o esperar daemon (si FDA OK)?
- ¿Programar IG manual o daemon arregló?
- ¿Render más sleep videos esta semana?
- ¿Cerrar PR #1 (merge a main)?

---

## 🔗 Referencias

- **PR GitHub:** https://github.com/fercreek/loop-video-maker/pull/1
- **YouTube canal:** https://youtube.com/channel/UC2l5TZjHzRtaRjH8kT_yQ2w
- **FB Page:** ID 452922677899760 (Palabra De Dios)
- **IG account:** @palabradedios111 ID 17841469453382962
- **YT API project:** versiculos-de-dios-youtube (449814655542)

## 📞 Chat thread referencia

Este spec fue generado al final de la sesión Claude del 2026-05-25 (~16h trabajo continuo). La conversación está completa — todo lo importante quedó persistido en archivos del repo. NO necesitas el thread chat para retomar.

**Si abres Claude nuevo y dices:** `"abre versiculos de dios"` o `"qué quedó pendiente"` → primera acción debe ser leer este archivo + `_NEXT.md`.

---

_Última actualización: 2026-05-25 19:30 MTY_
_Próxima sesión target: 2026-05-26 mañana (verificar publicaciones + FDA fix + IG status)_
