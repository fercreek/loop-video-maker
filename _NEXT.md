# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-05-25 (tarde) · Canal: @VersiculoDeDios · 12.7K subs · Views 28d: 88.3K · Watch 28d: 518.9h

---

## 🔴 BLOQUEOS / Acción Fernando

### Upload Shorts venom INCOMPLETO (YT quota daily hit)
**Subidos OK:**
- YouTube (7/20): venom_001, 004, 009, 002, 005, 010, 007
- Facebook (4/20): venom_001, 004, 002, 005

**Pendientes upload (13 YT + 16 FB):**
- Mañana 2026-05-26 después de quota reset (24h desde primer upload)
- Comando: `.venv/bin/python3 scripts/upload_shorts_venom.py`
- Bug: el script abortó en 429 sin retry. Debería continuar con siguientes (skip los YT con error, intentar FB siempre)

**FB errors específicos (009, 010, 007):**
- "Please reduce the amount of data you're asking for" — probable rate limit FB
- Re-intentar mañana junto con los 13 pendientes

### Sleep video pipeline LISTO PARA PROBAR
- `render_sleep.py` v1 funcional (5min test PASS QA 7/10)
- `scripts/qa_longform.py` adaptado con thresholds long-form
- Test 60min Salmo 91 corriendo en background (resultado al regresar)
- Cuando Chrome cerrado → mejor render 90-120min sin riesgo swap

---

## ⚡ En proceso (retomar aquí)

### 🎬 Batch venom (20 shorts) — POST-FIX PIPELINE
Sesión 2026-05-25: replicar fórmula `bi_B78HZuJ4` (Short 1m1s, 27% watch time canal).

**Estado actual:**
- 20 scripts en `data/oraciones_pool.json` (venom_001-020)
- venom_001 rendered con bugs críticos descubiertos y arreglados (ver `logs/LEARNINGS.md` sesión 2026-05-25)
- QA pipeline nuevo en `scripts/qa_short.py` — score 9/10 en venom_001
- venom_001 PASS QA pero falta validación final Fernando (voz + visuales)

**Pendiente:**
- [ ] Fernando aprueba venom_001 final (voz audible + watermark dedup + animación 2da mitad)
- [ ] **Multi-imagen 3-5 por video** (actualmente solo 2: image1 + image2 a 18s). Para 64s ideal: 4 imágenes cada 16s. Requiere modificar `core/shorts_render.py` xfade chain + `data/oraciones_pool.json` schema (campo `fondos: [a, b, c, d]` en lugar de `fondo` + `fondo2`)
- [ ] Más KB_VARIANTS (actual: 4 — pan_lr, pan_rl, zoom_in, zoom_out). Agregar: diagonal_tl_br, diagonal_tr_bl, slow_rotate, zoom_pan_combo
- [ ] Batch render venom_002-020 con A/B voz Dalia (10) / Jorge (10)
- [ ] Upload programado a YT + cross-post FB Reels

**QA agent debt:**
- [ ] Check voice-band presence (300-3kHz mean > -45dB) — actualmente NO detecta silencio si música rellena LUFS

### 📱 Batch v6 Shorts — LISTOS PARA SUBIR
- 10/10 aprobados en content-review
- Quick wins aplicados: subtítulos 4→6 palabras · CTA "Escribe AMÉN" · hook 3.5s
- **Subir:** `python3 scripts/upload_shorts_scheduled.py`
- Plan: 1/día · 5am MTY · 12-21 mayo · YouTube (private+publishAt) + Facebook (scheduled)
- Ambas plataformas quedan programadas — se publican solas, sin intervención

### 📅 May 22 — Análisis batch_v6 (rutina programada)
Rutina remota dispara automáticamente. ANTES de revisarla, correr:
```bash
cd /Users/fernandocastaneda/Documents/loop-video-maker
python3 scripts/content_tracker.py --pull-metrics
```
También revisar Facebook Insights: Meta Business Suite → page Palabra De Dios (452922677899760)
Rutina: https://claude.ai/code/routines/trig_01TfyuhGQYbWXGdqCfxQfcJM

### Pipeline de publicación dual (YT + FB) — cómo funciona
```
python3 scripts/upload_shorts_scheduled.py
  → YouTube: sube como private + publishAt → YT publica solo a las 5am
  → Facebook: sube con scheduled_publish_time → Meta Business Suite publica solo
  Verificar en: YT Studio → Contenido → Programados
               Meta Business Suite → Contenido → Programado
```

### 📤 Upload semana 2 — corriendo en background
- 6 videos subiendo ahora: buen-samaritano, hijo-prodigo, lazaro, resurreccion, ruth, job
- Quedan private hasta su fecha — YT Studio para revisar/eliminar si algo falla
- Notificación cuando termine → actualizar `_CALENDARIO-SUBIDA.md` con links

### 📋 Semana 3 — scripts por generar
- **Flujo nuevo:** render → **tú revisas MP4 en QuickTime** → "listo sube" → upload
- Historias pendientes (P1):
  1. La Creación del Mundo
  2. Torre de Babel
  3. Sodoma y Gomorra (Lot)
  4. Elías y los Profetas de Baal
  5. Gedeón y los 300
  6. Josué y Jericó
  7. Salomón y su Sabiduría
  8. Sermón del Monte
  9. Última Cena
  10. Pedro camina sobre el agua
- Generar: lanzar agentes Book Co-Author (igual sesión anterior)
- Render batch: `python3 scripts/batch_render.py --max 10 --priority 1`
- Revisar: `open output/stories/{id}/{id}.mp4` en QuickTime
- Subir: decirle a Claude "listo, sube"

---

## ✅ Completado 2026-05-11

- [x] 100-story catalog (`data/video_catalog.json`) — fuente de verdad
- [x] 16 videos renderizados (10 semana 1 + 6 semana 2)
- [x] **Semana 1 subida completa (10/10)** — programados may 11-24
  - abraham-e-isaac · daniel-foso-leones · david-goliat · ester-y-el-rey
  - jonas · jose-y-sus-hermanos · moises · noe · sanson-y-dalila · pentecostes
- [x] `_CALENDARIO-SUBIDA.md` — tracking completo con YT IDs
- [x] Copy auditado: hooks corregidos (4 genéricos → narrativos), tags 14/video
- [x] batch_render.py · upload_schedule.py · upload_to_youtube.py — scripts completos
- [x] YouTube token auto-refresh (no requiere re-auth manual)

---

## 💡 Backlog

- [ ] Shorts pipeline: `render_short.py` con `data/oraciones_pool.json` (14 oraciones listas)
- [ ] Pin comment primera hora de cada video publicado (pregunta emocional)
- [ ] Responder comentarios primeras 24h (señal algoritmo)
- [ ] Resolve strike Oraciones Cortas (90 días o respuesta solicitante)
- [ ] Auditar canal: bajar videos con audio CapCut narrado
- [ ] V2 retención: cold open con clímax, dinámica musical por mood, end screen verbal

---

## 🔒 Bloqueado

- Strike Oraciones Cortas → esperar 90 días o respuesta del solicitante
