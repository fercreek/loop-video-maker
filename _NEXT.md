# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-06-09 · Canal: @VersiculoDeDios-v1u (UC2l5TZjHzRtaRjH8kT_yQ2w)
> 🚨 LEE PRIMERO: `docs/SINTESIS_SIMBIONTES_2026-06-09.md` (revisión 3 simbiontes) + `docs/VENOM_SPEC_EXPLAINED.md` (manual del spec)
> Plan maestro de sesión: `~/.claude/plans/revisemos-el-plnm-que-iridescent-pebble.md` (v2 cimiento + v3 video-leveling)
> Stats: `data/venom_truth.json` (venom manda) · Scores por video: `data/video_scores.json`

## ⚡ Hecho 2026-06-09 (sesión larga)
- **Motor B LIVE** 💰 — Ko-fi membership `🕊️ Guardián del Ministerio $5` PÚBLICA + cobrable + lead magnet "7 Días de Paz" gratis + captura email automática. `ko-fi.com/versiculosdedios`. **El primer dólar ya tiene dónde entrar** (antes el link iba a página vacía).
- **Incidente resuelto:** 2 "motores" (`r43LS0y0Wrg`, `MdenXXdtW60`) eran **TikToks ajenos** subidos por error manual → BORRADOS de YT. Watch-time 28d cayó ~435h (esperado/sano, eran horas tóxicas que NO contaban YPP).
- **3 cambios deployados a `auto-publicador-vdd`** (prod, active:True, via anti-venom): retiming 3×→1× a 16:30 MX + copy hook-first + VIDEO_MAP fallback→sleep 2h.
- **IDs duplicados archivados** (`cero-agent/n8n-exports/archived/` — 2 gemelos mismo ID = peligro revert, eliminado).
- **Venom Video-Leveling creado** (NUEVO sistema) — rúbrica 6 ejes + 22 videos puntuados. Distribución L4=12·L3=9·L2=1, **cero L5 por funnel-wiring roto** (= el cuello, confirmado por los 3 simbiontes).
- **Spec ejecutable Batch 1b** + venom-nexo loop + explicador documentados.

## ⚡ Próximos pasos (orden corregido por verify-before-build de venom)
1. **P0-2 colector `engagement.jsonl`** — cron VPS cada 6h mide engagement REAL (hoy daily-stats cuenta acciones, no resultados). Sin esto el loop venom-nexo NO confirma hipótesis. owner: carnage build.
2. ✅ **P0-3 guard uploads huérfanos — SHIPPED 06-10** (`09da0c2`). `scripts/orphan_guard.py` + launchd `com.versiculodedios.orphan-guard` @8pm MX (local, NO cron VPS — token+venv en Mac). Windowed 14d · HIGH=licensedContent o ≥50h → WA venom. allowlist + `--ack-low` (28 auto-publishes n8n acked). 0 huérfanos hoy, TikToks borrados. ⏳ **4 BUGs carnage por reparar:** FOCUS-442 (API muere callado + analytics lag 72h ciega foráneo nuevo), FOCUS-443 (WA sin fallback), FOCUS-444 (Mac-off=no corre). FOCUS-441 = raíz n8n write-back.
3. **Y1 funnel** — pinned/end-screen de los ~5 Shorts L4 → sleep 2h (sube Funnel-wiring a L5 sin producir). Manual YT Studio.
4. **P1-3** generar 3 Shorts revelación/reframe (temas sin usar: `milagro_001`/`soledad_001`/`tristeza_001`) wired al sleep.

## 🔒 Bloqueado / Fernando manual
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
