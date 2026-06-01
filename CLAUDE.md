# CLAUDE.md — Versículos de Dios (loop-video-maker)
> Repo principal de todo el contenido de @VersiculoDeDios-v1u
> Leer este archivo PRIMERO en cualquier sesión. Tiempo: ~90 segundos.
> Última actualización: 2026-06-01 · Stats = `data/venom_truth.json` (venom manda)

---

## 🎯 OBJETIVO #1 — Monetización (leer SIEMPRE primero)

> 📡 **FUENTE DE VERDAD = `data/venom_truth.json`** — venom es dueño, data viva (YT Analytics + Meta Graph API).
> Cualquier número en ESTE doc es snapshot stale. Para stats reales → LEER el JSON primero, venom manda.
> Regenerar: `@agent venom` analiza YT+FB+IG y reescribe el JSON. NUNCA editar a mano con números inventados.

**Gate YPP = 4,000 h de LONG-FORM en 365 días. Real (venom 2026-06-01): 151.6 h = 3.8%.**
NO es 27% — ese número viejo contaba Shorts, que tienen ruta aparte (10M views/90d) y
NO cuentan para las 4,000h. **Solo long-form** (sleep 2h, 120min, historias, lofi) mueve la aguja.
Toda decisión se mide: *¿esto sube watch hours de long-form?* Producir Shorts NO acerca monetización.

Palancas gratis (auditoría venom): playlists binge ✅ · Shorts→long funnel · fix intros long-form.

## Skills recomendados (cargar por defecto en este repo)

| Skill | Cuándo usarlo |
|-------|--------------|
| `vd-youtube` | **Default del repo.** "cómo va el canal", "stats", "qué subo", "playlists", "YPP". Ancla objetivo + corre snapshot + lanza @agent venom |
| `@agent venom` | Análisis profundo cross-marca del canal (NO es skill, es agente — read-only) |
| `supernova` | Retro de sesión / "qué aprendimos" / post sobre aprendizajes |
| `content-review` | Revisar videos/thumbs antes de subir (swipe tipo Tinder) |
| `post-qa` | QA visual de cualquier thumbnail/post antes de publicar |
| `parallel-research` | Decisión de estrategia/nicho con data real (3 ángulos) |

**Regla:** al iniciar sesión de análisis/estrategia del canal → invocar `vd-youtube` (carga el objetivo real, evita re-explicar 146h/4000h cada vez).

---

## Estado del canal — ⚠️ NO hardcodear aquí

**Los números viven en `data/venom_truth.json` (venom manda).** Esta sección antes tenía una tabla
estática que quedó stale (decía 12,700 subs / YPP bloqueada / 27%). Eliminada a propósito.

Para el estado actual:
```bash
cat data/venom_truth.json | python3 -m json.tool   # snapshot completo
# o regenerar fresco:  @agent venom
```

**Snapshot venom 2026-06-01** (referencia rápida — el JSON es la verdad):
- YouTube: 14k subs · YPP long-form **3.8%** (151.6h / 4,000h) · motor del canal = Short `r43LS0y0Wrg` (324h/28d, 30% del watch time, pero NO cuenta YPP)
- Facebook: 1,917 fans · monetización por umbral (10k in-stream / Reels bonus invite >1k ✅) · formato reflexión-hook gana (200+ likes)
- Instagram: 1,189 followers · canal más chico, baja prioridad

**Caminos para monetizar (dos lógicas distintas):**
- **YouTube = GATE:** subir las ~30h de long-form parado en disco (6×120min ya programados + 3 lofi 2h). Es lo único que llena las 4,000h.
- **Facebook = UMBRAL:** Reels Play Bonus (path rápido, ya >1k fans) > in-stream ads (lejos, faltan 8,083 fans).
- **Activo compartido:** Shorts devocionales-hook alimentan subs YT + Reels FB/IG. Reciclar 1, publicar en 3.

---

## 4 Tracks de contenido activos

### Track 1 — Videos largos (60min / 120min)
**Stack:** `render_120min.py` · `render_60min.py` · MusicGen · Gemini fondos
**Output:** `output/semana_YYYY-MM-DD/`
**Subida:** YouTube manual o `scripts/yt_upload.py` (requiere re-auth)
**Docs:** `docs/CHANNEL_STRATEGY.md` · `docs/SYSTEM_OVERVIEW.md`
**Guía rápida:**
```bash
python3 render_120min.py --themes paz fe --output-dir output/semana_2026-05-07
python3 scripts/yt_auth.py   # si token YT expiró
```

### Track 2 — Shorts devocionales (30-75 seg, 9:16)
**Stack:** `render_short.py` · `core/shorts_render.py` (Pillow text engine v4)
**Voz:** Edge TTS ES-MX (Dalia femenina contemplativa / Jorge masculina pastoral) · ElevenLabs opcional
**Música:** `audio/cache/` (MusicGen + Kevin MacLeod CC-BY)
**Imágenes:** pool `output/fondos/fondo_ai_*.jpg` (Gemini + mflux local)
**Anti-strike:** NUNCA CapCut con audio narrado externo · Pillow overlay (NO drawtext)
**Output:** `output/shorts/semana_YYYY-MM-DD/*.mp4` + `thumbs/`
**Pool:** `data/oraciones_pool.json` (43 entries: 23 originales + 20 venom_*)
**QA obligatorio:** `scripts/qa_short.py` antes de upload (score ≥8)

**Batch venom (último, 2026-05-25):** 20 shorts replicando fórmula `bi_B78HZuJ4`
(top performer 27% watch time canal). Subidos via `scripts/upload_shorts_venom.py`
+ daemon `ig-daemon` publica IG.

### Track 3 — Imágenes FB + IG (1080×1080)
**Plataforma:** Facebook "Palabra De Dios" · Instagram @palabradedios111
**Automático:** launchd publica a **9am · 1pm · 7pm MTY** (sin intervención)
**Script:** `~/Documents/context/assets/versiculos/schedule_vd.py --publish-now`
**Generador Pillow:** `~/Documents/context/assets/versiculos/gen_fb_pillow_v3.py`
**Anti-duplicados:** `~/Documents/context/assets/versiculos/published.json`
**Docs completos:** `CONTEXT_FB_IG.md` en este repo
**Metricool:** SOLO para videos — imágenes ya automatizadas

### Track 4 — Sleeping content (60-120 min, 16:9)
**Stack:** `render_sleep.py` (reusa `core/music_gen.py`)
**Por qué:** path realista YPP — 10 videos × 1.5h × 200 views × 50% ret = 15K h/año
**Audio:** MusicGen local, moods "Reposo"/"Madrugada"/"Paz profunda" (target -18 LUFS)
**Visual:** 1-2 fondos + Ken-Burns ULTRA-lento (5% zoom en 60min)
**Texto:** Pillow overlay título primeros 10s con fade
**Watermark:** `@VersiculoDeDios` siempre visible top-right
**Output:** `output/sleep/sleep_{tema}_{min}min.mp4` (~30MB / 5min = ~360MB / 60min)
**QA:** `scripts/qa_longform.py` (LUFS -18, dur 50-130min, SSIM 0.9995 threshold permisivo)
**5 temas preset:** salmo91, salmo23, ansiedad, promesas, rosario
**Spec completa:** `docs/SLEEPING_PIPELINE.md`

---

## IDs críticos

| Recurso | ID / Path |
|---------|-----|
| YouTube channel | `UC2l5TZjHzRtaRjH8kT_yQ2w` |
| YT OAuth token | `data/yt_token.json` |
| YT API project | `versiculos-de-dios-youtube` (number `449814655542`) |
| FB Page (Palabra De Dios) | `452922677899760` |
| IG Account | `17841469453382962` (@palabradedios111) |
| FB/IG tokens (permanente) | `~/Documents/cero/cero-content/scripts/configs/tokens.json` → key `palabra-de-dios` |
| Metricool blogId | `5906079` |

---

## Versículos usados — NO repetir

### Batch Mayo 11-17 (FB/IG — imágenes)
Filipenses 4:13 · Salmos 23:1 · Juan 3:16 · Jeremías 29:11 · Isaías 41:10 · Mateo 11:28 ·
Salmos 46:10 · Isaías 40:31 · Romanos 5:8 · Romanos 8:28 · Lamentaciones 3:22 ·
1 Juan 4:8 · Mateo 7:7 · Proverbios 3:5 · Juan 10:14

### Batch Mayo 7-10 (FB/IG — imágenes)
Josué 1:9 · Proverbios 16:3 · Mateo 6:33 · Gálatas 5:22-23 · Salmos 37:4 ·
Isaías 26:3 · Lucas 1:37 · Efesios 2:8-9 · Salmos 118:24 · 2 Corintios 5:7 · Apocalipsis 21:4

### Videos largos ya publicados
Fe (Hebreos 11:1) · Esperanza (Jeremías 29:11) · Salmos (23:1) · Victoria (Romanos 8:37)

---

## Reglas anti-strike (OBLIGATORIO)

1. **NUNCA** plantillas CapCut con audio narrado externo
2. **NUNCA** descargar audio de canales YouTube (ni yt-dlp)
3. **NUNCA** oraciones con copyright moderno (solo dominio público o propias)
4. Música SOLO de: YT Audio Library · Kevin MacLeod CC-BY · MusicGen local · Pixabay CC0
5. Voz SOLO de: ElevenLabs (licenciado) o grabación propia
6. **ANTES de subir:** verificar derechos en YouTube Studio (Subir → Verificar → OK)

---

## Decisiones de contenido — Marco rápido

**¿Qué video hacer esta semana?**
1. Ver `docs/ANALYTICS_SNAPSHOT_*.md` → qué temas tienen mejor retención
2. Priorizar temas NO publicados aún (ver `docs/CHANNEL_STRATEGY.md`)
3. Para watch time: 120min > 60min — priorizar 120min
4. Para Shorts: temas de oración con alta intención de búsqueda ("oración para X")

**¿Qué imágenes FB/IG generar?**
1. Revisar lista "Versículos usados" arriba — NO repetir
2. Leer `~/Documents/context/content/brand-guidelines/versiculos-de-dios.md`
3. Agregar nuevos versículos en `gen_fb_pillow_v3.py` → generar → dry-run → confirmar

**Análisis de métricas:**
- @agent venom → solo lectura · después de cada batch semanal
- Mayo 12 9am: recordatorio en calendario para primer análisis

---

## Generación de fondos con mflux (FLUX local — gratis)

**Doc completo:** `docs/MFLUX_FONDOS.md`

mflux genera fondos fotorrealistas 100% local, sin costo. Requiere ~9GB RAM con Q4.
Modelo descargado en HF cache (~33GB). venv en cero-content ya tiene mflux instalado.

### Cómo activar desde esta sesión Claude

Decirle a Claude exactamente:

```
"Genera fondos mflux para el preset [nombre] — [count] imágenes en formato [9:16 / 1:1]"
```

Ejemplos:
```
"Genera fondos mflux para cielo_nocturno — 3 imágenes en 9:16"
"Genera fondos mflux para todos los presets — 1 imagen cada uno en 9:16"
"Genera fondos mflux para luz_divina y amanecer_dorado — 2 imágenes en 1:1"
```

Claude correrá `scripts/generate_fondos_mflux.py` con los parámetros indicados.
Output en: `output/fondos_mflux/{preset}/`

### Presets disponibles (12)

`amanecer_dorado` · `cielo_nocturno` · `luz_divina` · `piedra_antigua` · `agua_viva` ·
`nube_celestial` · `aurora_boreal` · `desierto_sagrado` · `gloria_eterna` ·
`bosque_profundo` · `sangre_de_cristo` · `paz_clasica`

### Comando directo

```bash
# Un preset específico
python3 scripts/generate_fondos_mflux.py --preset cielo_nocturno --count 3 --format 9:16

# Todos los presets (batch semanal — ~9 min, cerrar Chrome antes)
python3 scripts/generate_fondos_mflux.py --count 2 --format 9:16
```

### Reglas

- Cerrar Chrome + Notion antes de correr (liberar RAM para los 9GB de mflux)
- Solo paisajes/abstractos — mflux NO genera figuras humanas confiablemente
- Batch semanal domingo noche — fondos se reutilizan semanas

---

## QA Tools — Pre-Upload Validation

**Regla:** ningún video se sube sin pasar QA score ≥8/10.

### `scripts/qa_short.py` — para Shorts 9:16
- Motion check (SSIM entre frames cada 2s, flag estatismo >5s)
- Duration válida YT Shorts (<60 ideal, 55-90 warning)
- Sync audio/video
- LUFS target -16 ±3dB
- Voice-band check 300-3kHz (TODO: pendiente, agregar para catch silencio bugs)
- Score 1-10, exit 0 si ≥7, JSON report en `logs/qa/`

### `scripts/qa_longform.py` — para sleep/long-form
- SSIM threshold 0.9995 (KB ultra-lento)
- LUFS target -18 (sleep)
- Duration 50-130 min
- Sample frames cada 60s
- JSON report en `logs/qa/longform/`

### Agente `@agent shorts-qa` (en `~/.claude/agents/shorts-qa.md`)
Supervisor que diagnostica bugs conocidos (#1-10), aplica fixes, re-renderea hasta PASS.
Auto-actualizado con bugs nuevos cada sesión (feedback loop).

---

## Daemons macOS (Auto-publish + monitoring)

**Plists:** `~/Library/LaunchAgents/com.versiculodedios.*.plist`

| Daemon | Schedule | Función |
|--------|----------|---------|
| `ig-daemon` | 5:10am MTY + RunAtLoad | Publica IG del día (Graph API, idempotente) |
| `yt-fb-uploader` | 1:30am MTY | Sube YT+FB pendientes (post quota reset) |
| `morning-status` | 11am MTY | Genera `STATUS_TODAY.md` + notif macOS |
| `wake-reminder` | 10am MTY | Notif "abre Claude — pendientes X" |

### ⚠️ Requisito macOS Sequoia: Full Disk Access

macOS Sequoia bloquea launchd acceso a `~/Documents/` por default. Para daemons
funcionen, agregar a **System Settings → Privacy & Security → Full Disk Access**:
- `/bin/bash`
- `/usr/bin/python3`

Sin FDA: daemons fallan con `PermissionError`. Test:
```bash
launchctl kickstart -k gui/$(id -u)/com.versiculodedios.morning-status
sleep 2 && cat logs/morning_status.stderr   # debe estar vacío
```

### IG daemon detalles
- Lee `data/shorts_schedule.json` + `data/ig_state.json`
- Si target_time pasado y NO publicado → upload via Graph API + marca state
- Catch-up: si Mac off durante target, publica al despertar (flag `late=true`)
- Token: `~/Documents/cero/cero-content/scripts/configs/tokens.json` → key `palabra-de-dios`

---

## Monitoring local — Dashboard + Menubar

### Dashboard HTTP (puerto 8090)
**Archivo:** `dashboard.html` + `scripts/dashboard_server.py` (ThreadingHTTPServer)

```bash
.venv/bin/python3 scripts/dashboard_server.py &
open http://127.0.0.1:8090/dashboard.html
```

Auto-refresh 30s. Muestra: counts YT/FB/IG, daemons status (PID + last exit),
próximas 48h publicaciones, logs en vivo (botones IG / YT-FB / Morning).

### SwiftBar plugin (menubar macOS)
**Plugin:** `~/Documents/new-focus/daemons.30s.sh` (cross-projects)
Status icon 🟢/🔴 con count daemons activos. Click → desplegable grupos por proyecto.

Install: `brew install --cask swiftbar`

### Auto-status diario
- `scripts/morning_status.sh` → 11am MTY → `STATUS_TODAY.md` + notif
- `scripts/wake_reminder.sh` → 10am MTY → notif "abre Claude — N pendientes"

---

## Session Spec Workflow

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

---

## Comandos frecuentes

```bash
# === LONG-FORM ===
python3 render_120min.py --themes [tema] --output-dir output/semana_$(date +%Y-%m-%d)
python3 scripts/yt_auth.py   # si token YT expiró
python3 scripts/yt_stats.py

# === SHORTS pipeline ===
.venv/bin/python3 render_short.py --id venom_001 --voice dalia
.venv/bin/python3 scripts/qa_short.py output/shorts/semana_*/short_venom_001_*.mp4
# Batch render IDs específicos
for id in venom_001 venom_002 venom_003; do
  .venv/bin/python3 render_short.py --id $id --voice dalia --force
done
.venv/bin/python3 scripts/upload_shorts_venom.py   # skip-auto IDs ya OK

# === SLEEP pipeline ===
.venv/bin/python3 render_sleep.py --tema salmo91 --duration 60
.venv/bin/python3 scripts/qa_longform.py output/sleep/sleep_salmo91_60min.mp4

# === MONITORING ===
launchctl list | grep versiculodedios
.venv/bin/python3 scripts/dashboard_server.py & ; open http://127.0.0.1:8090/dashboard.html
bash scripts/morning_status.sh ; cat STATUS_TODAY.md
.venv/bin/python3 scripts/ig_daemon.py --status

# === FONDOS ===
python3 scripts/generate_fondos_mflux.py --count 2 --format 9:16
python3 scripts/generate_fondos_ai.py --count 20   # Gemini fallback

# === FB+IG IMÁGENES (separate pipeline) ===
cd ~/Documents/context/assets/versiculos
python3 gen_fb_pillow_v3.py
python3 schedule_vd.py --dry-run
cat /tmp/versiculos_publish.log
```

---

## Archivos de referencia en este repo

| Archivo | Para qué |
|---------|---------|
| `_NEXT.md` | Pendientes inmediatos — leer primero |
| `_LEARNING_LOG.md` | Auto-reflexión por sesión (pros/cons/consejos Claude) |
| `_SCHEDULE_VENOM.md` | Living spec: tabla 20 videos × plataforma con status |
| `docs/SESSION_SPEC_2026-05-25.md` | Spec sesión completa — entry point próxima sesión |
| `docs/SLEEPING_PIPELINE.md` | Spec sleep content + math YPP + 5 temas preset |
| `docs/YT_QUOTA_INCREASE.md` | Plantilla request quota Google (form URL + justification) |
| `REPORT_GYM_SESSION.md` | Wrap-up sesión gym (1h Fernando out) |
| `logs/LEARNINGS.md` | 10 bugs documentados con fix exacto (sesiones 05-25 + 05-26) |
| `data/shorts_schedule.json` | Plan upload con IDs reales YT/FB |
| `data/ig_state.json` | Estado runtime IG daemon (published, last_check) |
| `dashboard.html` | UI live para daemons (puerto 8090) |
| `CONTEXT_FB_IG.md` | Pipeline FB + IG completo (Track 3 — imágenes) |
| `docs/MFLUX_FONDOS.md` | Setup mflux + prompts por preset + script batch |
| `docs/CHANNEL_STRATEGY.md` | Biblioteca de videos, qué falta |
| `docs/ANALYTICS_SNAPSHOT_*.md` | Métricas históricas del canal |
| `docs/COPY_YOUTUBE.md` | Templates de título/descripción |
| `data/versiculos/` | Banco de versículos por tema |

---

## Principio arquitectónico — Todo pasa por n8n en producción

**INVARIANTE:** En producción, n8n (VPS root@2.24.111.80) es el orquestador. La Mac local
es solo para prototipado y renders pesados. Ningún flujo de producción debe depender de
que la Mac esté encendida.

**Patrón correcto:**
```
n8n cron (VPS) → APIs externas (Ideogram, ElevenLabs, YT, Claude)
  → si render local necesario: n8n webhook → Mac renderiza → sube resultado
  → log en /var/www/stats/actions.jsonl
  → alerta @cero_ops_bot Telegram
```

**loop-video-maker local = prototipado.** Cuando un pipeline está validado aquí,
se migra a workflow n8n en VPS. Scripts como `render_sleep.py` son la referencia
de implementación, no el destino final de producción.

---

## Guardrails anti-AI slop — Contenido de valor

**Contexto (investigación Mayo 2026):** YouTube eliminó canales masivos de AI religioso
("Imperio de Jesús" 5.87M subs, AI Jesús como influencer Gen-Z). El riesgo es real.

**Lo que diferencia contenido de valor vs AI slop eliminado:**

| AI Slop (eliminado) | Contenido de valor (sobrevive) |
|--------------------|-------------------------------|
| Jesús como meme/influencer | Escritura real + reflexión genuina |
| 10+ videos/día | 1-2/día, ritmo humano |
| Sin engagement real | Replies reales con Claude (cero-agent) |
| Sin disclosure AI | "Creado con asistencia de IA" en descripción |
| Shorts sin destino | Shorts → sleep videos (watch time real) |
| Voz robótica genérica | ElevenLabs voz cálida consistente |
| Formato repetido infinito | Rotación de temas y formatos |

**Guardrails que DEBEN estar en cada pipeline:**

1. **Claude valida script** antes de render — si score <7 en valor espiritual, no producir
2. **Disclosure automático** en descripción: `"Contenido creado con asistencia de IA 🙏"`
3. **Cross-link Shorts → long-form**: cada Short apunta al sleep video correspondiente
4. **Pacing máximo:** 1 Short/día. No publicar si canal tiene strike activo.
5. **Rotación de temas** semanal: miedo→propósito→gratitud→fe (no mismo tema siempre)
6. **Imágenes bíblicas cinematics**, NO Jesús fotorrealista hablando (riesgo strike)

**Fórmula viral segura (replicar esto):**
```
Hook 2s: pregunta que detiene el scroll ("¿Por qué Dios permite el dolor?")
  ↓
Versículo + imagen cinematic (3-5s)
  ↓
Reflexión corta + voz ElevenLabs cálida (15-20s)
  ↓
CTA + link sleep video (3s)
```
| `data/oraciones_pool.json` | Pool 43 oraciones (23 originales + 20 venom_*) |
