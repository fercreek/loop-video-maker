# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-05-27 14:30 MTY · Canal: @VersiculoDeDios · FB: 1,583 fans · IG: venom_001+004 publicados ✅ · 4/4 daemons OK

## 🚨 LEE PRIMERO

**Spec sesión completa:** `docs/SESSION_SPEC_2026-05-25.md` ← TODO contexto recuperado
**Tracking live:** `_SCHEDULE_VENOM.md` ← tabla 20 videos × plataforma
**Bugs históricos:** `logs/LEARNINGS.md` ← 10 bugs documentados con fix exacto

---

## ⚡ En proceso (retomar aquí)

### 🎬 Batch venom (20 shorts) — EN PRODUCCIÓN
**Plan:** 1/día 5:10am MTY IG · 5:00am YT/FB · daemon auto diario

**Estado upload (2026-05-27 14:30 MTY):**
- YouTube: **7/20** scheduled · daemon `yt-fb-uploader` ✅ FIXEADO · sube ~6/noche 1:30am
- Facebook: **17/20** scheduled · venom_007 + venom_020 pendientes retry
- Instagram: **2/20** publicados (venom_001 + venom_004 ✅) · venom_009 mañana 5:10am auto

**Daemons: 4/4 exit 0** (commit be44a27 — bash wrapper FDA)
```bash
launchctl list | grep versiculodedios      # verificar exit codes
cat data/ig_state.json                     # IG publicados
tail -20 logs/ig_daemon.log                # último run IG
tail -20 logs/yt_fb_uploader.stdout        # último run YT/FB
```

**Pendiente próxima sesión:**
- [ ] Verificar venom_009 publicó IG 5:10am (`data/ig_state.json`)
- [ ] Verificar YT subió ~6 más en noche (`logs/yt_fb_uploader.stdout`)
- [ ] Reintentar venom_007 + venom_020 FB (failed, retry daemon)
- [ ] Metrics 7 días batch venom (watch time, retention)
- [ ] QA tool debt: voice-band check 300-3kHz mean >-45dB

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

## ✅ Completado sesión 2026-05-27 (tarde)

- [x] Análisis exhaustivo estado sistema — daemons, uploads, errores
- [x] Fix plists bash wrapper FDA: ig-daemon + yt-fb-uploader (ambos exit 0)
- [x] Fix `ig_daemon.py`: dry-run no escribe ig_state.json (commit be44a27)
- [x] venom_004 publicado IG (`17992374638986813`) vía force-publish
- [x] Pushed a origin/main

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
