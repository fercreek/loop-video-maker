# Referencia de CLAUDE.md — texto movido

> Lo que salió de `CLAUDE.md` para adelgazarlo, tal cual estaba. Se lee cuando hace falta; `CLAUDE.md` deja un puntero.

## Fragmento: **Por qué se apagaron 4 (4-nov-2026, con el sí de Fernando).** El `.ve — movido de CLAUDE.md el 2026-11-23

**Por qué se apagaron 4 (4-nov-2026, con el sí de Fernando).** El `.venv` desapareció entre
el 20 y el 21-oct-2026 y desde entonces las tareas que lo usan salían con `exit 127`.
Al revisarlo:

- `ig-daemon`: IG (@palabradedios111) ya recibe 1 video al día por la vía de n8n / olas
  (visto en la API: 1 VIDEO diario del 17-oct al 3-nov). De los 20 reels `venom_0xx` del
  schedule sólo 2 salieron por el daemon; los otros 18 quedaron atrasados y el daemon
  publica los atrasados todos en una corrida (catch-up `late=true`). Revivirlo = 18 reels de
  golpe, duplicando la cadencia de n8n. **No se vuelve a cargar sin vaciar o rehacer
  `shorts_schedule.json`.**
- `yt-fb-uploader`: los 20 del schedule ya están programados en YT y FB (hasta el 9-nov);
  no queda nada que subir, y la fuente de Shorts (los videos de la mamá) se acabó el 15-oct.
  VDD publica por olas desde cero-agent / n8n.
- `morning-status`: sólo reportaba esos dos daemons.
- `wake-reminder`: recordatorio de un pendiente de mayo.

Se apagaron con `launchctl unload` **sin borrar el plist**. Para volver a prender uno:
`launchctl load ~/Library/LaunchAgents/com.versiculodedios.<nombre>.plist`.

## Session Spec Workflow — movido de CLAUDE.md el 2026-11-23

Para sesiones largas (>3h trabajo o múltiples deploys), genera spec persistido:

**Patrón:** `docs/SESSION_SPEC_YYYY-MM-DD.md`

**Contenido obligatorio:**
- Qué se hizo (features, bugs, scripts nuevos)
- Estado actual upload/deploy
- Bloqueos pendientes (con acción concreta usuario)
- Cómo retomar (lista de archivos a leer + comandos)
- Referencias (PR, URLs, IDs)

**Para qué:** próxima sesión Claude lee este archivo PRIMERO + `_NEXT.md`
→ reconstruye contexto sin chat history. Cero memoria conversacional necesaria.

**Linkear desde `_NEXT.md`** banner top:
```md
🚨 LEE PRIMERO: `docs/SESSION_SPEC_YYYY-MM-DD.md` ← TODO el contexto
```

**Tracking spec vivo:** `_SCHEDULE_VENOM.md` (en raíz) — tabla por video × plataforma
con status ✅/🕐/❌. Se actualiza después de cada upload.
