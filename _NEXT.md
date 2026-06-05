# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-06-04 · Canal: @VersiculoDeDios-v1u (UC2l5TZjHzRtaRjH8kT_yQ2w)
> 🚨 LEE PRIMERO: `docs/PLAN_MONETIZACION_ALTERNA_2026-06-04.md` (plan frentes alternos · venom+research · tablero priorizado)
> 🚨 También: `docs/STRATEGY_MONETIZATION_2026-06-01.md` (subir horas / cross-promo / ads)

## ⚡ Hecho 2026-06-04
- Ko-fi link en **21 videos live** (9 largos + 12 Shorts top). FOCUS-323 ✅
- `sleep_salmo91_120min` encolado (QA 10/10) publish 15-jun. FOCUS-223 ✅
- **Flywheel WF#1 DEPLOYED** — Ko-fi en `first_comment` del auto-publicador-vdd (prod, active:True, verify OK). Cada post FB+IG diario fija comment con link YT + Ko-fi. Doc: `docs/FLYWHEEL_VDD_2026-06-04.md`

## 🎡 Flywheel — pendiente
- [x] **WF#2** Ko-fi 1/3 en `Primer Comentario YT` (yt-comments-agent) DEPLOYED ✅ (FB/IG replies NO tocados, anti-spam)
- [ ] **beehiiv** (Fernando ~20min) — signup abierto en Chrome → desbloquea WF#3/#4
- [x] **WF#3** kofi-email-capture construido+testeado (`cero-agent/n8n-exports/kofi-email-capture.json`) — espera API key beehiiv
- [x] **WF#4** generador email semanal (`scripts/weekly_devotional_email.py`, 7 temas, manda al video largo+Ko-fi) — beehiiv free no tiene Send API → email manual 2min
- [ ] **beehiiv API key** (Fernando) — Stripe Identity Verification con ID+cel → desbloquea WF#3 deploy
- [ ] Ko-fi en 33 videos ✅ (9 largos + 12 Shorts + 12 top incl. motor r43LS0y0Wrg)
> 📡 Stats reales: `data/venom_truth.json` (venom manda)

## 🎯 Estado real (venom 2026-06-01) — RETOMAR AQUÍ

- **Subs:** 14k · **YPP long-form:** 3.8% (151.6h / **4,000h**) — el "27%" viejo contaba Shorts, FALSO.
- Gate = **4,000h de long-form** (no 3,000). Solo long-form cuenta; Shorts NO.
- Motor del canal = Short `r43LS0y0Wrg` (324h/28d, 30% del watch time) — pero 0 para el gate.

---

## ⚡ En proceso (retomar aquí)

### 💰 Meta Ads $200 MXN — PAUSED (blocker token)
- 4/5 objetos creados en Meta: campaign + adset + audiences + creative.
- **Blocker:** token Studio Link app está en dev mode → necesita token de Agencia Cero app (Live) con `ads_management`. FOCUS-259 creado.
- **Ready para reanudar:** carnage tiene script listo en `carnage-execution-2026-06-02.md`. Cuando haya token correcto → carnage completa creative + activa ad.

### 🛍️ Etsy listings — generándose
- 5 listings generados en `data/etsy-listings.md`.
- Assets en `output/etsy/` (generándose — PDF planner ReportLab incluido).
- Pendiente: revisión Fernando + publicar en Etsy (acción manual).

### ⭐ Stars post FB
- Publicado en `fb.com/palabradedios111`.
- Falta: **pin manual** (2 clicks en la página — Fernando lo hace).

### 🎁 Super Thanks YT
- Pendiente activar en YouTube Studio (Fernando, ~5 min, no requiere código).

---

## 🔁 Scheduleds corriendo solos (sin intervención)

- **9 long-form Jun 2-13:** 5×120min + 3×lofi + salmos ya live.
- **Pinned comment** Short `r43LS0y0Wrg` → sleep `6eHgRtGjaYA` ✅
- **cero-agent** 5 workflows VD activos ✅

---

## ✅ Ready (listos · esperan acción de Fernando)

- **Token Agencia Cero app (Live) con `ads_management`** → desbloquea Meta Ads E4 → carnage activa campaña.
- **Pin Stars post** en `fb.com/palabradedios111` (2 clicks).
- **Activar Super Thanks** en YT Studio (~5 min).
- **Revisar + publicar Etsy listings** (5 listings en `data/etsy-listings.md`).

---

## 💡 Backlog

### Monetización alternativa (Operación de Dios)
- [ ] Ko-fi membresía — Fernando setup manual.
- [ ] Shoutout canal devocional LATAM ~$50 (buscar canal).
- [ ] MusicGen → Suno fix (CC BY-NC red flag bloquea Spotify/DistroKid).

### Automatización / infra
- [ ] n8n workflow: YT video live → auto-post FB/IG (FOCUS-259).
- [ ] Cross-promo loop→cero: sync `promote_queue.json` (loop escribe) → nodo n8n lo lee. Cada long-form nuevo se auto-promociona.

### Content pipeline
- [x] **FOCUS-223 encolar long-form parado** (2026-06-04) — hallazgo: los "7 parados ~11h" estaban STALE. `lofi_v02_orar_2h`/`v03_ansiedad_2h` = raws viejos superseded por `_verses_final` YA subidos. Único real parado = `sleep_salmo91_120min` (QA 10/10) → encolado en `upload_schedule.json` publish **2026-06-15** (uploaded:false, assets generados). `sleep_salmo91_60min` no se sube (decisión A: solo 120min, evita canibalizar).
- [ ] **Verificar daemon yt-fb-uploader vivo** (FOCUS-178) — el salmo91 encolado depende de él + token YT. Si daemon roto → no sube.
- [ ] **Medir CTR delta 8 thumbnails** (7-14 días) — Pródigo/Daniel/Jonás/Samaritano/José/Pentecostés/Moisés/Noé.
- [ ] **Verificar 6×120min publicaron** en sus fechas (31may→10jun) + que entraron a playlist PARA DORMIR.
- [ ] **Shorts→long funnel:** pinned comment + link a sleep video en top 10 Shorts.
- [ ] Generar 5 sleep videos test (salmo91, salmo23, ansiedad, promesas, rosario).
- [ ] Request quota YT increase a Google (`docs/YT_QUOTA_INCREASE.md`) — esperar strike resuelto.
- [ ] 100-story long-form catalog — quedan ~84 historias pendientes.

### Deuda técnica
- [ ] Fix `upload_to_youtube.py` — agregar flag `--yes`/no-TTY detect.
- [ ] Reconciliar `#4B6BFF`→`#1f4bff` en `cc-post-image` SKILL.md + `compose_pro.py`.
- [ ] Commit 2 repos externos: `contreras-code-website` (5 SVGs logo #1f4bff) + `context` (~13 logos CC).

---

## 🔒 Bloqueado

- **Meta Ads E4** — token app Live `ads_management` (FOCUS-259).
- **Strike Oraciones Cortas** — esperar 90 días o respuesta solicitante.
- **YT quota daily 6 uploads** — request increase pendiente strike resuelto.

---

## 📦 Inventario long-form en disco

**6×120min — SUBIDOS + PROGRAMADOS** (output/semana_2026-05-06/videos/):
- `esperanza_120min.mp4` · `fe_120min.mp4` · `paz_120min.mp4` · `provision_120min.mp4` · `salmos_120min.mp4` · `sanacion_120min.mp4`

**3 lofi 2h — PROGRAMADOS Jun 12/14/16** (output/lofi/):
- `lofi_v01_dormir_2h.mp4` · `lofi_v02_verses_final.mp4` · `lofi_v03_verses_final.mp4`
- Metadata: `output/lofi/youtube_metadata.json`

**16 stories 14-22min — EN DISCO** (output/stories/{slug}/):
- abraham-e-isaac · buen-samaritano · daniel-foso-leones · david-goliat · ester-y-el-rey · hijo-prodigo · job-sufrimiento · jonas · jose-y-sus-hermanos · lazaro-resurreccion · moises · noe · pentecostes · resurreccion-de-jesus · ruth-y-noemi · sanson-y-dalila
- (Algunas con CTR bajo — re-test thumbnail antes de subir el resto.)

---

## 🚨 Referencias clave

| Archivo | Para qué |
|---------|---------|
| `docs/STRATEGY_MONETIZATION_2026-06-01.md` | Plan maestro dual YT+FB, 10 experimentos |
| `_LEARNING_LOG.md` | Auto-reflexión por sesión |
| `_SCHEDULE_VENOM.md` | Living spec: tabla videos × plataforma |
| `logs/LEARNINGS.md` | 10+ bugs documentados con fix exacto |
| `data/upload_schedule.json` | Schedule upload activo |
| `data/lofi_upload_schedule.json` | Schedule lofi (activar jun 12) |
| `data/etsy-listings.md` | 5 listings listos para Etsy |
