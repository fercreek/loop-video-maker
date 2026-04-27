# _NEXT — Plan versión siguiente
**Fecha análisis:** 2026-04-25 · Basado en: VERSION.md + LEARNINGS.md + auditoría de código

---

## Estado actual post-v3.7

✅ 8 × 60min · ✅ 8 × 120min · ✅ quality gate 100/100 · ✅ docs completas

Gaps identificados en esta sesión de análisis.

---

## GAPS IDENTIFICADOS

### 🔴 Crítico

**1. Mood names con/sin tilde — inconsistencia silenciosa**
- `config.py` usa `"Meditacion"` y `"Sanacion"` (sin tilde)
- `audio/loops/manifest.json` tiene `"Meditación"` y `"Sanación"` (con tilde)
- `music_gen.py` tiene normalización tolerante (accent-insensitive) — pero si eso falla, track silencioso
- Fix: estandarizar a SIN tilde en ambos lados, o validar en `generate_playlist()` con assert
- **Archivo:** `config.py` THEME_MOODS + `audio/loops/manifest.json`

**2. Versos únicos muy pocos — repetición visible en 120min**
- 120min = 288 versos cicládos. Promedio único: ~48 versos → cada verso aparece ~6 veces
- `gratitud` tiene solo 43 únicos → cada verso 6.7× en 120min
- Estrategia actual: ciclar la lista — repetición ordenada, el mismo verso vuelve cada ~15min
- Fix: expandir JSONs a 80–100 versos únicos por tema, o implementar shuffle con ventana de no-repetición
- **Archivo:** `data/versiculos/*.json` + `render_60min.py:cycle_verses()`

### 🟡 Medio impacto

**3. `provision` y `sanacion` tienen JSON pero no se renderizan**
- `provision.json` (~45 versos), `sanacion.json` (~46 versos) existen
- No están en `config.py:ALL_THEMES` ni en `THEME_MOODS`
- Son temas con alta búsqueda ("provisión de Dios", "sanación divina")
- Fix: agregar a `ALL_THEMES` con moods apropiados, fondos asignados, copy YouTube
- **Archivo:** `config.py` + `core/thumbnail_gen.py:THEME_COPY`

**4. render_60min y render_120min son casi idénticos — code duplication**
- Ambos scripts tienen la misma estructura: `cycle_verses`, `render_video`, `_gate_results`, batch loop
- Diferencias: `TARGET_MINUTES`, `SECONDS_PER_VERSE`, `OUTPUT_BASE`, `RELAXING_MOODS`
- Fix: extraer lógica común a `core/batch_renderer.py(target_min, secs_per_verse, moods_override, output_base)`
- **Archivos:** `render_60min.py`, `render_120min.py`

**5. A/B test thumbnails sin infraestructura de medición**
- Templates A/B/C generados y listos
- No hay script que lea CTR desde YouTube Analytics y declare ganador automáticamente
- Fix: cuando exista `core/youtube_client.py`, agregar `scripts/ab_report.py`
- **Blocker:** requiere YouTube Data API (ver `docs/ANALYTICS_SETUP.md`)

**6. `iterate.py` ignora 120min**
- `iter_batch` siempre rota sobre 60min (`OUTPUT_BASE_60MIN`)
- No existe `iterate_120min.py` ni flag `--format 120min`
- Fix: agregar `--format` flag, construir path dinámicamente
- **Archivo:** `iterate.py:eval_batch()` y `render_batch()`

### 🟢 Bajo impacto / mejoras de calidad

**7. Eval no mide repetición de versos**
- `eval_render.py` mide LUFS, silencios, bitrate, fps — pero no si versos se repiten demasiado seguido
- 288 versos × 6 repeticiones en 120min no es un bug técnico pero es un problema de calidad
- Fix: agregar check `verse_repetition_interval` en eval — warning si mismo verso aparece < N min aparte

**8. No existe modo 3 horas**
- Canal de sleep muy competitivo. "Música cristiana para dormir toda la noche" = keywords con alto volumen
- Fix: `render_180min.py` es trivial: `TARGET_MINUTES=180, SECONDS_PER_VERSE=37` (437 versos × 37s)
- Requiere más versos únicos (gap #2) para no sonar repetitivo en 3h

**9. Credit Kevin MacLeod no está en ninguna descripción**
- `audio/loops/manifest.json` indica CC-BY 4.0 — requiere crédito
- Descripción de YouTube no lo incluye actualmente
- Fix: agregar línea fija al template de descripción en `docs/COPY_YOUTUBE.md` y `COPY_YOUTUBE_120MIN.md`
- **Impacto legal/ético:** bajo riesgo pero fácil de corregir

**10. Thumbnails 120min se generan en `{tema}_thumb.jpg` — sin sufijo de formato**
- 60min: `output/youtube_60min/paz/paz_thumb.jpg`
- 120min: `output/youtube_120min/paz/paz_thumb.jpg`
- Mismo nombre de archivo — si se cambia OUTPUT_BASE podría sobreescribir
- Fix: renombrar a `paz_120min_thumb.jpg` para consistencia explícita

---

## PLAN v3.8 — Propuesta

### Scope mínimo (1-2 sesiones)

**v3.8-content-expansion**

1. **Fix mood names** — estandarizar sin tildes en config.py y manifest.json (15 min)
2. **Agregar provision + sanacion** a ALL_THEMES — 2 temas nuevos, total 10 (30 min)
3. **Expandir versos** — cada tema a 80+ únicos usando Claude API (1 sesión)
4. **Kevin MacLeod credit** — agregar a templates de descripción (5 min)

Resultado: 10 temas × 2 formatos = 20 videos. Biblioteca +25%.

### Scope medio (2-3 sesiones)

**v3.9-3h-format + refactor**

5. **render_180min.py** — 3 horas dormir toda la noche (30 min, fácil)
6. **Refactor batch_renderer core** — unificar render_60min/120min/180min en un solo módulo (2-3h)
7. **Verse shuffle con ventana** — no repetir mismo verso en window de 40 versos (1h)

### Scope largo (requiere YouTube API)

**v4.0-analytics**

8. **YouTube Data API** — `core/youtube_client.py` + OAuth setup
9. **A/B report automático** — CTR por thumbnail template, ganador automático
10. **Weekly report** — `scripts/yt_report.py` → `docs/ANALYTICS_REPORT.md`

---

## Decisión de próxima sesión

Cuál atacar primero:

| Opción | Impacto canal | Esfuerzo | Recomendación |
|--------|-------------|---------|---------------|
| Fix moods + provision/sanacion | +2 temas nuevos para subir | 30 min | ✅ fácil win |
| Expandir versos 80+ | Videos más variados | 1 sesión | ✅ calidad |
| render_180min | Nuevo keyword "toda la noche" | 30 min | ✅ fácil win |
| YouTube API | Analytics reales | 30 min setup + 2h build | Cuando haya datos |

**Orden sugerido:** provision/sanacion → render_180min → expandir versos → API
