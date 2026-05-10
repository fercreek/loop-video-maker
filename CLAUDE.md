# CLAUDE.md — Versículos de Dios (loop-video-maker)
> Repo principal de todo el contenido de @VersiculoDeDios-v1u
> Leer este archivo PRIMERO en cualquier sesión. Tiempo: ~90 segundos.
> Última actualización: 2026-05-07

---

## Estado del canal (Mayo 2026)

| Métrica | Valor |
|---------|-------|
| Suscriptores | ~11,500 (+2.1K/28d) |
| Views/28d | ~208,900 (95.9% Shorts) |
| Watch time long-form real | ~42h (necesita 3,000h para YPP) |
| Monetización YPP | ❌ Bloqueada — meta: Nov 2026 |
| Strikes activos | 1 (Oraciones Cortas — audio narrado CapCut) |

**Caminos para monetizar (elegir uno):**
- Long-form: 3,000h watch time en 365 días → faltan ~2,958h → subir más 60/120min
- Shorts: 3,000,000 vistas en 90 días → faltan ~2.84M → escala de Shorts devocionales

---

## 3 Tracks de contenido activos

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

### Track 2 — Shorts devocionales (30-60 seg, 9:16)
**Stack:** `render_short.py` (en construcción) · ElevenLabs voz ES-MX · ffmpeg vertical  
**Anti-strike:** NUNCA usar plantillas CapCut con audio narrado externo  
**Música:** YouTube Audio Library · Kevin MacLeod CC-BY · MusicGen local  
**Voz:** ElevenLabs Starter ($5/mes) — voz Daniel/Antonio ES-MX  
**Output:** `output/shorts/semana_YYYY-MM-DD/`  
**Estado Sprint 1:** ver `_NEXT.md`

### Track 3 — Imágenes FB + IG (1080×1080)
**Plataforma:** Facebook "Palabra De Dios" · Instagram @palabradedios111  
**Automático:** launchd publica a **9am · 1pm · 7pm MTY** (sin intervención)  
**Script:** `~/Documents/context/assets/versiculos/schedule_vd.py --publish-now`  
**Generador Pillow:** `~/Documents/context/assets/versiculos/gen_fb_pillow_v3.py`  
**Anti-duplicados:** `~/Documents/context/assets/versiculos/published.json`  
**Docs completos:** `CONTEXT_FB_IG.md` en este repo  
**Metricool:** SOLO para videos — imágenes ya automatizadas

---

## IDs críticos

| Recurso | ID |
|---------|-----|
| YouTube channel | `UC2l5TZjHzRtaRjH8kT_yQ2w` |
| YT OAuth token | `data/yt_token.json` |
| FB Page (Palabra De Dios) | `452922677899760` |
| IG Account | `17841469453382962` |
| FB/IG token (permanente) | `tokens.json` → `"palabra-de-dios"` |
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

## Comandos frecuentes

```bash
# Render video largo
python3 render_120min.py --themes [tema] --output-dir output/semana_$(date +%Y-%m-%d)

# Re-auth YouTube
python3 scripts/yt_auth.py

# Stats YT
python3 scripts/yt_stats.py

# Generar fondos mflux (nuevo — reemplaza generate_fondos_ai.py para batch)
python3 scripts/generate_fondos_mflux.py --count 2 --format 9:16

# Generar fondos AI (Gemini — fallback si no hay RAM)
python3 scripts/generate_fondos_ai.py --count 20

# Generar imágenes FB/IG
cd ~/Documents/context/assets/versiculos
python3 gen_fb_pillow_v3.py

# Verificar posts FB/IG programados
python3 schedule_vd.py --dry-run

# Ver log de publicaciones automáticas
cat /tmp/versiculos_publish.log
```

---

## Archivos de referencia en este repo

| Archivo | Para qué |
|---------|---------|
| `_NEXT.md` | Pendientes inmediatos — leer primero |
| `_SEMANA_*.md` | Plan de subida de la semana actual |
| `CONTEXT_FB_IG.md` | Pipeline FB + IG completo |
| `docs/MFLUX_FONDOS.md` | Setup mflux + prompts por preset + script batch |
| `docs/CHANNEL_STRATEGY.md` | Biblioteca de videos, qué falta |
| `docs/ANALYTICS_SNAPSHOT_*.md` | Métricas históricas del canal |
| `docs/COPY_YOUTUBE.md` | Templates de título/descripción |
| `data/versiculos/` | Banco de versículos por tema |
