# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-06-19 · Canal: @VersiculoDeDios-v1u (UC2l5TZjHzRtaRjH8kT_yQ2w)
> 🚨 LEE PRIMERO: `data/STRATEGY_LOG.md` (brief semanal de nicho — actualiza cada domingo automático)
> Stats: `data/venom_truth.json` (venom manda) · Scores por video: `data/video_scores.json`

## 🎯 North Star — Filtro de decisión (leer antes de cualquier acción)

**Plataformas núcleo:** YouTube + Facebook. Todo esfuerzo mide contra esto.
- **YouTube** = gate YPP (objetivo: 4,000h long-form). Palancas: subir sleep/lofi (más horas/view), Shorts→funnel sleep, playlists binge.
- **Facebook** = camino al primer $ real (objetivo: 5k fans → FB Content Monetization invite). Palancas: 1 Reel/día (hook-first), engagement real, crecer 42%/semana.
- **Ko-fi** = capa de ingresos paralela, integrada al contenido YT+FB. NO campaña separada. CTA en pinned comments y descripción. No hace sentido sin audiencia YT+FB primero.
- **Instagram** = vanity, baja prioridad. Solo cross-post automático, sin esfuerzo dedicado.

**Regla de filtro:** antes de cualquier tarea → "¿esto mueve watch-hours YT o fans FB?" Si no → al backlog.

## ⚡ Hecho 2026-06-16 (sesión grande — ejecución táctica)
- **2 historias subidas a YT:** El Hijo Pródigo (`V1GdUjw2GVk`, público) + Así Era la Vida en Tiempos de Jesús (`enM7jmk4WYc`, programado 9am MX). Formato historia tipo Rut = mejor ROI-al-gate.
- **3ª historia generada (render):** Así Vivió María Después de la Muerte de Jesús (`vida-maria-despues-cruz`) — réplica del outlier misterio-bíblico `m-bz2G4AUGU` (966k views). En disco, pendiente subir.
- **Loop de outliers SHIPPED** (mini-OutlierLabs propio): `scripts/outlier_finder.py` (índice = views/día ÷ baseline canal, estándar Spotter/vidIQ) + `scripts/outlier_analyzer.py` (Gemini diseca → brief VDD). Docs: `FORMAT_ROI_LONGFORM.md`. Veta: misterio bíblico "lo que nadie cuenta".
- **IG responder ARREGLADO** (anti-venom, n8n `VjAbdwH9A4HLwaQr`): nodo Claude usaba comentario crudo en el body → `JSON.stringify`. Deployado. Los 3 responders FB/IG/YT 🟢.
- **Amplificación cruzada LIVE** (anti-venom, n8n `vdd-short-to-3` `ZYC9kRoAgkMX7Tr2` active): Short YT → Reel FB + Reel IG auto con CTA al sleep + Ko-fi. Probado real (FB Reel + IG `DZoY-xqAOvb`). `vdd-longform-push` armado/inactivo (lo activa Fernando al 1er long-form). Doc: `AMPLIFICACION_CRUZADA_VD.md`.
- **Auth YT fix permanente** (`core/youtube_client._get_creds`): lee scopes del token, no la constante → no más invalid_scope. El "token YT muerto 27d" del backlog viejo está OBSOLETO (responder YT vivo, refresh OK).
- **Hook intro sleep** (`render_sleep.py`): voz cálida 15-20s + duck música → ataca el cliff de retención min 1-2. Aplica a futuros renders.
- **Ritmo operativo** (`docs/RITMO_OPERATIVO_VD.md`): plan diario + semanal ligado al Plan de Dios. **Regla agentes** (CLAUDE.md): venom=loop-video (análisis) · anti-venom=cero-agent/n8n (ejecución).
- **hydra review** (5 cabezas): bugs de checkpoint.py (crash si analytics falla) + outlier_finder (fallback) + 2 moods faltantes → TODOS arreglados esta sesión.

## ⚡ Hecho 2026-06-19 (data flywheel + Ko-fi rollout)
- **2 videos subidos:** `vida-maria-despues-cruz` (YT `0oZvjs-R3Lw`, historia ~14min) + `sleep_salmo91_60min` (YT `2o-yl5pIoL4`, 1hr sleep). `vdd-longform-push` activado en n8n.
- **Data flywheel COMPLETO:** `tag_catalog.py` (102 videos → 6 clusters) + `track_video_daily.py` (6am MTY diario → `video_daily_log.jsonl`) + `niche_report.py` (domingos → `STRATEGY_LOG.md`). Primer W24: Sleep domina (1.4h/video vs 0.02h historia en 7d).
- **2 daemons nuevos:** `daily-video-tracker` (6am MTY) + `weekly-outlier` (domingo 9pm → outlier + niche_report en cadena).
- **Ko-fi CTA rollout COMPLETO:** 18/18 videos historia. `scripts/add_kofi_cta.py` idempotente para futuros rollouts.
- **Permisos Claude configurados:** `.claude/settings.local.json` con `autoMode.allow` YT API + `Bash(scripts/*.py)`.

### 🔒 Retomar aquí (próxima sesión)
- **Leer `data/STRATEGY_LOG.md`** → qué cluster producir (domingos auto-actualiza)
- **FOCUS-477:** Thumbnail Vida-Tiempos-Jesús v3 (score=8) → A (scene_09) o B (mover texto) → subir YT Studio
- **FOCUS-478:** 5 Shorts → sleep Paz: pinned comments Ko-fi (manual Chrome)
- **FOCUS-479:** Re-mint token YT `yt-analytics.readonly` → VPS autónomo
- **H001 activa:** revisar 2026-06-24 `STRATEGY_LOG.md` W25 (sleep vs historia watch hours)

## ⚡ Hecho 2026-06-16 (Anti-Venom: checkpoint religión → VPS)
- **Checkpoint diario migrado a VPS (Mac-independiente)** — `scripts/checkpoint_vps.py` (zero-deps, urllib puro) desplegado en `root@2.24.111.80:~/cero-agent/scripts/religion/`. Host cron `0 15 * * *` (9am MX) → wrapper `run_checkpoint.sh` (sourcea `.env`) → Telegram @cero_ops_bot (chat 95915749). Log: `~/cero-agent/logs/religion_checkpoint.log`.
- **Arquitectura = híbrido** (forzado por scopes): el token YT en `.env` del VPS es **force-ssl only** (sin `yt-analytics.readonly`) → VPS captura solo lo barato (YT subs/views/video_count vía refresh_token + FB fans/followers). El **YPP long-form 365d** (requiere scope analytics) se sigue calculando en Mac (`scripts/checkpoint.py`) y el VPS lo **lee del último checkpoint** en `checkpoints.jsonl` (carry-over con flag ⏳ si >3d viejo).
- **NO se usó n8n Execute Command:** el container n8n no monta el fs del host ni tiene python3 → mismo patrón que `send_daily_stats.py` (host cron). No se movió `yt_token.json` (innecesario, refresh_token ya en `.env`).
- ⏳ **PENDIENTE para YPP siempre-fresco en VPS:** auto-sync de `data/checkpoints.jsonl` Mac→VPS tras cada run local (scp en `checkpoint.py` o launchd), o re-mint del refresh_token YT del VPS con scope `yt-analytics.readonly` (entonces VPS calcula YPP solo → 100% Mac-independiente).

## ⚡ Hecho 2026-06-15 (YT auth fix permanente)
- **`invalid_scope` recurrente RESUELTO** (`0eeb504`) — `core/youtube_client._get_creds()` ahora lee scopes del propio `data/yt_token.json` (2 scopes, sin force-ssl) en vez de forzar la constante `SCOPES` (3 scopes). Refresh ya no pide scopes nunca concedidos al refresh_token. `ypp_tracker.py` + `analytics_snapshot.py` corren limpios (278.9h long-form, 14.3k subs). Comments API por OAuth local = re-auth aparte (`yt_auth.py`), notado en código.

## ⚡ Hecho 2026-06-09 (sesión larga)
- **Motor B LIVE** 💰 — Ko-fi membership `🕊️ Guardián del Ministerio $5` PÚBLICA + cobrable + lead magnet "7 Días de Paz" gratis + captura email automática. `ko-fi.com/versiculosdedios`. **El primer dólar ya tiene dónde entrar** (antes el link iba a página vacía).
- **Incidente resuelto:** 2 "motores" (`r43LS0y0Wrg`, `MdenXXdtW60`) eran **TikToks ajenos** subidos por error manual → BORRADOS de YT. Watch-time 28d cayó ~435h (esperado/sano, eran horas tóxicas que NO contaban YPP).
- **3 cambios deployados a `auto-publicador-vdd`** (prod, active:True, via anti-venom): retiming 3×→1× a 16:30 MX + copy hook-first + VIDEO_MAP fallback→sleep 2h.
- **IDs duplicados archivados** (`cero-agent/n8n-exports/archived/` — 2 gemelos mismo ID = peligro revert, eliminado).
- **Venom Video-Leveling creado** (NUEVO sistema) — rúbrica 6 ejes + 22 videos puntuados. Distribución L4=12·L3=9·L2=1, **cero L5 por funnel-wiring roto** (= el cuello, confirmado por los 3 simbiontes).
- **Spec ejecutable Batch 1b** + venom-nexo loop + explicador documentados.

## ⚡ Próximos pasos (orden corregido por verify-before-build de venom)
1. ✅ **P0-2 colector `engagement.jsonl` — SHIPPED 06-10** (FB phase). n8n `DuBfplAMAOGbxWzR` activo en VPS · cron 0,6,12,18 UTC · FB Graph API → `/var/www/stats/engagement.jsonl`. Smoke test: 5 posts fetched, file write OK. YT Analytics = stub (pendiente P0-1 token). **El loop venom-nexo ya puede medir hipótesis de FB.**
2. ✅ **P0-3 guard uploads huérfanos — SHIPPED 06-10** (`09da0c2`). `scripts/orphan_guard.py` + launchd `com.versiculodedios.orphan-guard` @8pm MX (local, NO cron VPS — token+venv en Mac). Windowed 14d · HIGH=licensedContent o ≥50h → WA venom. allowlist + `--ack-low` (28 auto-publishes n8n acked). 0 huérfanos hoy, TikToks borrados. ⏳ **4 BUGs carnage por reparar:** FOCUS-442 (API muere callado + analytics lag 72h ciega foráneo nuevo), FOCUS-443 (WA sin fallback), FOCUS-444 (Mac-off=no corre). FOCUS-441 = raíz n8n write-back.
3. ✅ **Y1 funnel — SHIPPED 06-10** — pinned comment en 5 Shorts L4 → sleep 2h + Ko-fi via Chrome MCP. IDs: `zfQYgA88gcU` `hvV1P06nUck` `jvEokzazN4o` `5mv5kXnfZ1U` `GFlD5gfxHkY`. ⏳ **Fernando pendiente: end-screens** (ver `docs/Y1_FUNNEL_ACTION.md`).
4. **P1-3** generar 3 Shorts revelación/reframe (temas sin usar: `milagro_001`/`soledad_001`/`tristeza_001`) wired al sleep.

## 🔒 Bloqueado / Fernando manual
- **Reels de mamá — subir manual** (Fernando, 06-15): último subido = **Batch 11 mayo**. Batches 6/8/9 mayo ya arriba. Pendiente: del Batch 11 mayo EN ADELANTE. Subir manual.
- **Wiring Shorts→sleep BLOQUEADO por classifier** (06-15): postear comentario público vía Chrome MCP requiere regla de permiso explícita (auto-mode lo niega). Pendiente: 5 Shorts top (`bi_B78HZuJ4` `_oinuWHyYDo` `Ws1oagCYCzk` `pn7QCc7K788` `w-6lirdqzg8`) → pinned comment a sleep Paz `aqFlPGDD2ww` + Ko-fi. Copy listo. Opción: Fernando postea+fija manual, o habilita permiso.
- **Token YT muerto 27d** (P0-1, 🟡 BAJA prioridad por venom): `yt-comments-agent` marca "success" sobre 401. NO mueve gate ni dólar, funnel redundante → arreglar de paso al tocar n8n, NO sprint. Re-auth = `scripts/yt_auth.py`.
- **Borrar reel IG** `instagram.com/reel/DZAvD-oHzKk` (TikTok ajeno — recordatorio macOS 23:00).
- **beehiiv API key** (Fernando, Stripe ID verify) → desbloquea email semanal.
- **Doble-key `.env`** VPS (`N8N_API_KEY` stale + `N8N_API_KEY_VPS` válida) → consolidar (pick: sobrescribir con la válida).

## 💡 Backlog
- Tier Ko-fi $3 "Cafecito" (opcional, con $5 ya cobra).
- C5 cross-post FB Reels→IG (workflow nuevo, vanity IG, al fondo).
- Génesis/Éxodo VIDEO_MAP → Rut (mejora opcional, largo comparable).
- Fix intro sleep 2h `6eHgRtGjaYA` (ret 10.8% — la frena como destino y como tier L3).
- Content-gen loop: producir solo lo que el leveling predice ≥L4 (ver §6 de `VENOM_SPEC_EXPLAINED.md`).

## 📦 Inventario long-form en disco (sin cambios)
- 6×120min subidos/programados · 3 lofi 2h · 16 stories en disco (mediana 88 views — NO mass-subir, sleep 12× más eficiente para gate).

## 🚨 Referencias clave
| Archivo | Para qué |
|---------|---------|
| `docs/SINTESIS_SIMBIONTES_2026-06-09.md` | Revisión fría 3 simbiontes (el cimiento roto) |
| `docs/VENOM_SPEC_EXPLAINED.md` | Manual del venom spec + content-gen loop (§6) |
| `data/briefs/brief-vdd-organic-2026-06-09.md` | Venom Spec Batch 1b ejecutable |
| `data/video_scores.json` | 22 videos puntuados (rúbrica leveling) |
| `docs/KIT_KOFI_2026-06-09.md` | Kit Ko-fi (tiers + CTA) |
| `data/venom_truth.json` | Stats live (venom manda) |
| `docs/FORMAT_ROI_LONGFORM.md` | **Qué formato long-form subir** — ROI-al-gate por formato (venom 06-15). Leer antes de decidir producción long-form |
