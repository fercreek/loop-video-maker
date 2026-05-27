# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-05-27 MTY · Canal: @VersiculoDeDios · FB: 1,583 fans (+252 en 8d) · IG: venom_001 publicado ✅

## 🚨 LEE PRIMERO

**Spec sesión completa:** `docs/SESSION_SPEC_2026-05-25.md` ← TODO contexto recuperado
**Tracking live:** `_SCHEDULE_VENOM.md` ← tabla 20 videos × plataforma
**Bugs históricos:** `logs/LEARNINGS.md` ← 10 bugs documentados con fix exacto

---

## ⚡ En proceso (retomar aquí)

### 🎬 Batch venom (20 shorts) — EN PRODUCCIÓN
**Plan:** 1/día 5am MTY · May 26 → Jun 14 · YT + FB + IG cross-post

**Estado upload (2026-05-27 MTY):**
- YouTube: **7/20** (venom_001, 004, 009, 002, 005, 010, 007) — daemon `yt-fb-uploader` ROTO (PermissionError pyvenv.cfg) → subir manualmente o fixear daemon
- Facebook: **18/20** programados OK (venom_007 y venom_020 fallaron) — ✅ 1/día correcto
- Instagram: **venom_001 publicado** ✅ (`18087886448579249`) · venom_004 falla chunk final (intermitente) · resto pendiente daemon

**Bug fix deployado (commit 9f2b62c):**
- `ig_daemon.py`: upload en chunks 4MB (API rupload requiere LSVP chunked, no single-request)
- `upload_shorts_venom.py`: fallback pub_ts → 1/día desde último fb_id (evita bulk)

**Daemons activos:**
```bash
launchctl list | grep versiculodedios
# com.versiculodedios.ig-daemon       ← IG publisher (FIXEADO hoy)
# com.versiculodedios.yt-fb-uploader  ← ROTO (PermissionError)
# com.versiculos.publish              ← texto/imagen 3x/día (9am,1pm,7pm MTY)
```

**Pendiente próxima sesión:**
- [ ] Fix daemon `yt-fb-uploader`: PermissionError en `.venv/pyvenv.cfg` — posiblemente `chmod` o rehacer venv
- [ ] Subir venom_007 y venom_020 a FB manualmente (fallaron por quota)
- [ ] Monitorear IG: daemon corre 5am MTY, revisar `data/ig_state.json` diario
- [ ] venom_004 IG: retry manual si sigue fallando (video puede tener issue específico en chunk 16MB)
- [ ] Metrics 7 días batch venom (watch time, retention FB reels vs YT)
- [ ] QA tool debt: agregar voice-band check 300-3kHz mean >-45dB (catch silencio futuro)

### 🌙 Sleep video pipeline LISTO
- ✅ `render_sleep.py` v1 funcional
- ✅ `scripts/qa_longform.py` adaptado
- ✅ Test 60min Salmo 91 → QA 10/10 PASS (315MB, LUFS -18.1)
- [ ] **Decidir:** generar 5 sleep videos (salmo91, salmo23, ansiedad, promesas, rosario) — 5h render total
- [ ] **Decidir:** cómo subir sleep videos (otro pipeline upload? otra cuota YT?)

---

## 💡 Backlog

### Pipelines / código
- [ ] Multi-imagen 3-5 por video (actualmente 2: image1 + image2 a 18s) — schema `fondos: [a,b,c,d]`
- [ ] Más KB_VARIANTS visuales (zoom_in_pan combo, slow_rotate)
- [ ] `scripts/qa_short.py` agregar voice-band check (300-3kHz)
- [ ] `scripts/qa_longform.py` agregar check "NO voz dominante en sleep ambient"
- [ ] Mejorar SwiftBar plugin: agregar conteo de pendientes por proyecto
- [ ] Auto-update `_SCHEDULE_VENOM.md` desde shorts_schedule.json (script TBD)

### Growth / análisis
- [ ] Pin comment primera hora de cada video publicado (pregunta emocional)
- [ ] Responder comentarios primeras 24h (señal algoritmo)
- [ ] Cross-post FB Reels (los 5 top Shorts 28d)
- [ ] Request quota YT increase a Google (`docs/YT_QUOTA_INCREASE.md`) — esperar strike resuelto
- [ ] V2 retención: cold open con clímax, dinámica musical por mood

### Content
- [ ] Generar 5 sleep videos test (salmo91, salmo23, ansiedad, promesas, rosario)
- [ ] Investigar competidores top (Audios Católicos) — qué hacen diferente
- [ ] 100-story long-form catalog — quedan ~84 historias pendientes
- [ ] Imágenes FB+IG (1080×1080) — sigue auto via launchd separate

---

## ✅ Completado sesión 2026-05-25

- [x] 20 venom shorts rendered + QA 9-10/10 (`data/oraciones_pool.json`)
- [x] 10 bugs críticos documentados + fix (`logs/LEARNINGS.md`)
- [x] Sleep pipeline v1 implementado (`render_sleep.py` + `qa_longform.py`)
- [x] QA tools (`qa_short.py` + `qa_longform.py`)
- [x] Upload script venom + IG daemon + 3 daemons monitoring
- [x] Dashboard local puerto 8090 + SwiftBar plugin
- [x] Session spec workflow (`SESSION_SPEC_*.md` + `_SCHEDULE_VENOM.md`)
- [x] PR #1 mergeado a main (commit eca13b8)
- [x] FDA grant macOS para daemons (2026-05-26)
- [x] Bug fix morning_status grep multi-line (commit 6ec4f9f)
- [x] Agente `@agent shorts-qa` con bugs conocidos #1-10

---

## 🔒 Bloqueado

- Strike Oraciones Cortas → esperar 90 días o respuesta solicitante
- YT quota daily 6 uploads (request increase pendiente strike resuelto)

---

## 📁 Limpieza recomendada (archivos stale raíz)

```bash
mkdir -p docs/archive
git mv _CALENDARIO-SUBIDA.md _SEMANA_2026-05-07.md _UPLOAD-READY.md _UPLOAD.md _RESUME-SESSION.md docs/archive/
git mv docs/_NEXT.md docs/archive/_NEXT-old.md
git commit -m "chore: archive stale tracking docs (superseded by _SCHEDULE_VENOM + SESSION_SPEC)"
```
