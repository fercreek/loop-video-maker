# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-06-01 · Canal: @VersiculoDeDios-v1u (UC2l5TZjHzRtaRjH8kT_yQ2w)
> 🚨 LEE PRIMERO: `docs/STRATEGY_MONETIZATION_2026-06-01.md` (subir horas / cross-promo / negocio alterno / ads)
> 📡 Stats reales: `data/venom_truth.json` (venom manda)

## 🎯 Estado real (venom 2026-06-01) — RETOMAR AQUÍ

- **Subs:** 14k · **YPP long-form:** 3.8% (151.6h / **4,000h**) — el "27%" viejo contaba Shorts, FALSO.
- Gate = **4,000h de long-form** (no 3,000). Solo long-form cuenta; Shorts NO.
- Motor del canal = Short `r43LS0y0Wrg` (324h/28d, 30% del watch time) — pero 0 para el gate.

### ✅ Ya resuelto (corrige _NEXT viejo)
- **6×120min YA subidos + programados** (`upload_schedule.json`, May31–Jun10, todos uploaded:true). NO están parados.
- **16 stories** ya subidas.

### ⚡ Palanca #1 (lo único realmente parado en disco)
- **7 archivos lofi/sleep SIN subir** (~11h long-form): 5 lofi 2h en `output/lofi/` + `sleep_salmo91_120min` + `_60min`.
- **Acción:** encolar en `upload_schedule.json` con publishAt escalonado tras Jun 10. (No ejecutado — requiere "sí".)

### 🔁 Cross-promo loop→cero (diseñado, no implementado — doc §2)
- cero-agent `auto-publicador.json` ya postea links YT en FB/IG, pero `VIDEO_MAP` es hardcoded a mano.
- Falta: sync `promote_queue.json` (loop escribe) → nodo n8n lo lee. Cada long-form nuevo se auto-promociona.

### 💵 Ingresos paralelos (no esperan las 4,000h — doc §3)
- 3 AHORA: productos digitales (PDF/planner versículos), donaciones (Super Thanks ya calificas + Ko-fi), afiliados cristianos. ~$100-500/mes.

### 📣 Ads (veredicto doc §4)
- Google/YT = **NO** (watch pagado no cuenta YPP + pierdes ~90%). FB = **test $300-500 MXN** solo Reels bonus, nunca el gate.

### 📅 Schedule viejo (referencia — algunos ya hechos)
1. ~~6×120min~~ ✅ subidos+programados.
2. **Los lofi/sleep parados** (dormir / orar / ansiedad / salmo91) — usar `_verses_final` donde exista (FOCUS-086).
3. **Shorts diario** en paralelo — alimenta subs, no compite con long-form (FOCUS-087).
4. **Re-test 1-2 stories** (17-22min) con thumbnail nuevo — eran long-form pero con bajo view; validar si thumbnail nuevo levanta CTR antes de subir las 16 (FOCUS-088).

### 📦 Inventario exacto (paths reales confirmados 2026-05-31)

**6×120min — LISTOS (3.2GB c/u):** `output/semana_2026-05-06/videos/`
- `esperanza_120min.mp4` · `fe_120min.mp4` · `paz_120min.mp4` · `provision_120min.mp4` · `salmos_120min.mp4` · `sanacion_120min.mp4`
- Thumbnails en `output/SUBIR/120min/`: `esperanza_thumb.jpg`, `fe_thumb.jpg`, `paz_thumb.jpg`, `provision_thumb.jpg`, `salmos_thumb.jpg`, `sanacion_thumb.jpg` (carpeta tiene 10 thumbs; estos 6 son los que matchean los videos renderizados)
- Copy 120min: `docs/COPY_YOUTUBE_120MIN.md`

**3 lofi 2h — LISTOS:** `output/lofi/`
- v01 dormir → `lofi_v01_dormir_2h.mp4` (838M)
- v02 orar → `lofi_v02_verses_final.mp4` (874M, con verses) · base sin verses: `lofi_v02_orar_2h.mp4`
- v03 ansiedad → `lofi_v03_verses_final.mp4` (431M, con verses) · base sin verses: `lofi_v03_ansiedad_2h.mp4`
- Thumbs en `output/lofi/thumbs/` (varias versiones v2/v3/v4 por video) · metadata: `output/lofi/youtube_metadata.json`
- NOTA: la realidad supera el _NEXT viejo — dormir TAMBIÉN está renderizado (no solo orar/ansiedad).

**16 stories 14-22min — LISTAS (mp4 final + thumbnail.jpg cada una):** `output/stories/{slug}/`
- abraham-e-isaac · buen-samaritano · daniel-foso-leones · david-goliat · ester-y-el-rey · hijo-prodigo · job-sufrimiento · jonas · jose-y-sus-hermanos · lazaro-resurreccion · moises · noe · pentecostes · resurreccion-de-jesus · ruth-y-noemi · sanson-y-dalila
- (Algunas ya subidas como long-form al canal con bajo view — re-test thumbnail antes de subir el resto.)

### 🎯 OBJETIVO REAL (corregido 2026-05-31 — auditoría venom)
**Gate YPP = 4,000h LONG-FORM en 365d. Real: ~146h = 3.6%** (NO 27% — eso contaba Shorts que NO cuentan).
Solo long-form (sleep 2h / 120min / historias / lofi) mueve la aguja. Shorts = ruta aparte, no toca este gate.
Skill `vd-youtube` ancla esto cada sesión. Palancas gratis: playlists ✅ · Shorts→long funnel · fix intros long-form.

### ✅ Hecho 2026-05-31 (sesión upload)
- **3 playlists binge creadas** (55 vids): PARA DORMIR (32) · Historias Biblia (17) · Lo-Fi (6). IDs en `data/playlists.json`. Mantener con `scripts/build_playlists.py`.
- **Skill `vd-youtube`** creado (`~/.claude/skills/vd-youtube/`) — ancla objetivo + snapshot + venom.
- **6×120min:** subidos como private+publishAt (Salmos→Provisión, c/2 días 9pm MTY, 31may→10jun). Títulos SEO keyword-led. `data/upload_schedule.json`.
- **3 lofi 2h:** prep listo (NO subidos) — `data/lofi_upload_schedule.json` (12/14/16 jun). Activar: `cp` → `upload_schedule.json` → run.
- **8 thumbnails re-test** swapeados en YT (verificado API 23:09 GMT): Pródigo/Daniel/Jonás/Samaritano/José/Pentecostés/Moisés/Noé. Copy curiosity-gap, subtítulo "Historia Bíblica" eliminado. Originales sin tocar (solo swap imagen). Medir CTR delta en 7-14 días.
- Scripts nuevos: `swap_thumbnail.py` · `archive_uploaded.py` · `_build_120min_schedule.py` · `_build_lofi_schedule.py`. Generador `core/story_thumbnail.py` ahora auto-shrink (no overflow).

### ✅ Cerrado 2026-05-31 noche
- 6/6 120min subidos (provision completo) · 3 playlists binge (55 vids) · skill vd-youtube · 4 posts CC en _LISTOS_METRICOOL · hex CC unificado #1f4bff · fix upload --yes · 4 skills Cortex archivados
- Focus: FOCUS-118/119/121 done · 085/086/088 (dup) cerradas

### ⏭️ PENDIENTE próxima sesión (de 2026-05-31 noche)
- [ ] **Commit 2 repos externos:** `contreras-code-website` (5 SVGs logo #1f4bff + llms.txt) + `context` (~13 logos CC). NO commiteados aún — revisar render logo primero
- [ ] FOCUS-122 programar 4 posts CC en Metricool · FOCUS-123 rasterizar PNGs logo · FOCUS-120 CTR thumbnails (7-14d)
- [ ] **Medir CTR delta 8 thumbnails** (7-14 días) — Pródigo/Daniel/Jonás/Samaritano/José/Pentecostés/Moisés/Noé. Replicar el copy ganador
- [ ] **Verificar 6×120min publicaron** en sus fechas (31may→10jun) + que entraron a playlist PARA DORMIR
- [ ] **Subir 3 lofi** cuando toque (12/14/16 jun): `cp data/lofi_upload_schedule.json data/upload_schedule.json` → `echo "y" | python3 scripts/upload_to_youtube.py`
- [ ] **Fix `upload_to_youtube.py`** — agregar flag `--yes`/no-TTY detect (hoy depende de `echo "y" |`, falla silencioso en background)
- [ ] **Shorts→long funnel** (palanca #2 venom, sin tocar aún): pinned comment + link a sleep video en top 10 Shorts
- [ ] **Reconciliar `#4B6BFF`→`#1f4bff`** en `cc-post-image` SKILL.md + `compose_pro.py` (deuda brand CC)
- [ ] **4 posts CC** en `_LISTOS_METRICOOL/` listos para programar en Metricool

### 🔒 Constraints de upload
- **Quota YT:** 6 uploads/día (request increase pendiente strike resuelto — `docs/YT_QUOTA_INCREASE.md`)
- **APRUEBO Fernando** obligatorio antes de cualquier upload real.

---

## 🚨 LEE PRIMERO

**Spec sesión completa:** `docs/SESSION_SPEC_2026-05-25.md` ← TODO contexto recuperado
**Tracking live:** `_SCHEDULE_VENOM.md` ← tabla 20 videos × plataforma
**Bugs históricos:** `logs/LEARNINGS.md` ← 10 bugs documentados con fix exacto

---

## ⚡ En proceso (retomar aquí)

### 🎵 Lo-Fi Cristiano — Batch v1 EN RENDER

**Estado (2026-05-28):**
- [ ] v01 `dormir` — renderizando (`lofi_veo3_clean_8s.mp4` noche, Biblia+vela)
- [ ] v02 `orar` — renderizando (`lofi_veo3_clip2_clean_8s.mp4` noche, cruz+libros)
- [ ] v03 `ansiedad` — renderizando (`lofi_v03_kb30s.mp4` mañana KB 30s, tonos dorados)
- [ ] Todos: 6 verse overlays Pillow PNG dorado cada 20min, 25s fade · audio `output/sleep/playlist.wav`

**Stack:** `Imagen 4 API → Veo3 Google Flow (16:9, 8s) → ffmpeg watermark+crop → ffmpeg loop×900 + audio + verse overlays → YouTube`

**Assets reutilizables en `output/lofi/`:**
- `lofi_veo3_clean_8s.mp4` · `lofi_veo3_clip2_clean_8s.mp4` · `lofi_v03_kb30s.mp4`
- `verse_cards/verse_01-06.png` (6 overlays) · `_wm_1280.png` · `youtube_metadata.json`

**Pendientes post-render:**
- [ ] Agregar verses faltantes en v02 y v03
- [ ] Crear playlist "Lo-Fi Cristiano" en YouTube Studio
- [ ] Upload — esperar **APRUEBO Fernando** antes de subir

**7 mejoras engagement (aplicar a futuros):**
1. Playlist "Lo-Fi Cristiano" → autoplay encadena watch time ×3
2. Capítulos en descripción (timestamps por versículo)
3. Comentario fijado: "¿Cuál versículo resonó contigo? 👇"
4. End screen → siguiente video playlist
5. Subir domingo 9pm MTY (pico consumo religioso)
6. "sin anuncios" en descripción (alto search volume)
7. Keyword "PARA DORMIR" en primeras 3 palabras título

**Métrica objetivo:** >200h watch time/video en 30 días (baseline: 1 lofi 2h visto al 30% = 36min vs 21s avg Short)

---

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
- [ ] **Decidir:** generar 5 sleep videos (salmo91, salmo23, ansiedad, promesas, rosario) — 5h render
- [ ] **Decidir:** cómo subir sleep videos (otro pipeline upload? otra cuota YT?)

---

## 💡 Backlog

### Pipelines / código
- [ ] Multi-imagen 3-5 por video (hoy 2: image1 + image2 a 18s) — schema `fondos: [a,b,c,d]`
- [ ] Más KB_VARIANTS visuales (zoom_in_pan combo, slow_rotate)
- [ ] `scripts/qa_short.py` agregar voice-band check (300-3kHz)
- [ ] `scripts/qa_longform.py` agregar check "NO voz dominante en sleep ambient"
- [ ] Mejorar SwiftBar plugin: conteo pendientes por proyecto
- [ ] Auto-update `_SCHEDULE_VENOM.md` desde shorts_schedule.json (script TBD)

### Growth / análisis
- [ ] Pin comment primera hora cada video (pregunta emocional)
- [ ] Responder comentarios primeras 24h (señal algoritmo)
- [ ] Cross-post FB Reels (top 5 Shorts 28d)
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