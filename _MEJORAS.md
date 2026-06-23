# 🛠 Plan de Mejoras — Loop Video Maker (Mac B dedicada)
> Generado 2026-06-22 · Fuente: carnage-kill break-list + priorización venom + sesión Mac B
> Objetivo: que el programa corra solo, confiable y sin publicar nada roto.
> Leyenda: 🔴 BUG (rompe) · 🟠 GAP (frágil) · 💭 NIT · Esfuerzo B/M/A

---

## FASE 0 — Proteger (AHORA, lo corre Fernando)
| Item | Qué | Esf | Estado |
|---|---|---|---|
| GAP-5 | **Commit + push** de los fixes de hoy (render_sleep, generate_yt_metadata, build_subir, vd_review_server, 4 guiones, uploader reels). Protege contra pérdida + da el fix de sleep a Mac A. | B | ⬜ Fernando (Terminal) |

```bash
cd ~/Documents/personal/loop-video-maker
git add render_sleep.py scripts/generate_yt_metadata.py scripts/upload_reels_batch_v2.py \
  scripts/build_subir.py vd_review_server.py data/stories/oracion_*.json data/stories/reflexion_*.json \
  data/video_catalog.json data/upload_schedule.json data/reels_uploaded.json data/local-music-research/
git commit -m "Mac B: fix render_sleep + descripciones type-aware + guiones + reels horas coherentes"
git push origin main
```

---

## FASE 1 — Confiabilidad (esta sesión · venom/repair)
Sin esto, "déjala corriendo sola" NO es confiable (ya falló 1 noche).

| Item | Problema (trazado) | Fix | Esf |
|---|---|---|---|
| 🔴 BUG-1 | Keep-awake nocturno no aguanta: `caffeinate -t Nh` vence + lid-close en batería lo mata → murieron batches + corrompió salmo91. | `caffeinate -w <PID_del_render>` (atado al proceso, no a timer) + check "¿enchufada?" antes de batch + abortar si batería. | B |
| 🔴 BUG-3 | MP4 corrupto pasa el review sin validación (salmo91 inválido fue aprobado). | Gate `ffprobe` (duración+streams) en `vd_review_server.py` (no mostrar/aprobar inválidos) y antes de cada upload. | B |
| 🔴 BUG-2 | `render_sleep.py:253` cae a MusicGen/torch si el mood no tiene cache (promesas/Madrugada, rosario/Devoción) → crash. | Si no hay cache, caer a mood cacheado (reposo) en vez de torch. | B |
| 🟠 GAP-3 | Scripts truenan con `python3` system (ModuleNotFoundError google). | Guard al inicio: detectar venv o re-exec con `.venv/bin/python3`. | B |
| 🟠 GAP-1 | `upload_reels_batch_v2` no valida fecha futura → publishAt en pasado → API 422. | Saltar/avisar entries con `publish_utc <= now`. | B |

---

## FASE 2 — Cobertura (esta semana · venom/repair)
| Item | Problema | Fix | Esf |
|---|---|---|---|
| 🔴 BUG-4 | Los sleeps no se programan por API: no están en `video_catalog` → `upload_to_youtube.py` los ignora. salmo91 sigue sin ruta. | Entrada de catálogo tipo `sleep` con mp4/desc explícitos, O un `upload_sleep.py` con publishAt. | M |
| 🟠 GAP-4 | `BATCH` de reels hardcodeado, edición manual semanal → fácil de olvidar/misdate. | Auto-armar BATCH escaneando `output/shorts/{semana}/` + fechas desde "mañana", con franja día/noche por keyword. | M |
| 🟠 GAP-2 | Anti-dup por id bloquea re-subir un reel corregido; `--force` re-sube todo (dup real). | `--only <id>` para re-subir uno, o hash de archivo además del id. | M |

---

## FASE 3 — Calidad y escala (después · mejora continua)
| Item | Mejora | Por qué | Esf |
|---|---|---|---|
| QA | Calibrar `qa_longform` por tipo (narrado 12-25min/-14 LUFS vs sleep 50-130min/-18). | Hoy reprueba falsamente oración/reflexión (dio 3/10 falso). | B |
| Visual | Curar pool "noche" de fondos para sleep/oración (reuse evita random diurnos). | Mejor "caída" visual coherente. | B |
| Música | Montar **Sonic Pi / FluidSynth** para ambient propio infinito ($0, inmune Content ID) + curar YouTube Audio Library. | Variedad nueva sin pelear el hardware (ver `data/local-music-research/`). | M |
| Escala | Script de **render-farm** (N renders en paralelo controlado) aprovechando CPU ocioso (usa ~1.2 de 12 cores). | 3-5× throughput en la box dedicada. | M |
| Reservorio | Generar scripts del backlog (Claude API) → render overnight → semanas adelantadas. | Banco de contenido para el gate YPP. | M |

---

## Orden recomendado (venom)
1. **Fase 0** (Fernando, ya) → protege todo.
2. **Fase 1** completa (venom, esta sesión) → producción nocturna confiable.
3. **Fase 2 BUG-4** (esta semana) → sleeps se programan solos.
4. **Fase 3** según prioridad de growth.

## Loop de cierre
carnage rompió → venom priorizó (este plan) → **repair ejecuta Fase 1** → carnage re-rompe (regresión sobre los fixes) antes de confiar que corra solo.

## Referencias
- Break-list carnage 2026-06-22 (en histórico de sesión)
- Learning: `../venom/data/learnings/loop-video-maker-mac-b-intel.md`
- Research música: `data/local-music-research/SYNTHESIS.md`
