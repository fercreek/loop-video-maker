# 🕷️ venom spec — Monitor Operación de Dios
> Doc VIVO. Dueño: venom. Propósito: monitorear el sistema de monetización de @VersiculoDeDios
> (flywheel + gate YPP) y acumular PAUTAS sin asumir cambios. Decisiones abiertas se loguean aquí
> hasta tener data, no se ejecutan a ciegas.
> Creado: 2026-06-04 · Última revisión: 2026-06-04

---

## 0. Cómo se usa este doc

- **NO se asume nada estructural** (daemons, auto-publish, ads) sin que la decisión pase por la sección §4 con criterio + data.
- Cada sesión que toque Operación de Dios: leer §3 (qué monitorear hoy) + agregar a §5 (pautas) lo aprendido.
- venom actualiza §2 (métricas) en cada análisis. Las decisiones abiertas (§4) se resuelven con la data de §2, no por intuición.

---

## 1. El sistema (qué está vivo)

| Componente | Estado | Mide |
|------------|--------|------|
| Flywheel Ko-fi→email | ✅ live (WF#3 probado E2E) | subs nuevos beehiiv, apoyos Ko-fi |
| Ko-fi en 33 videos + funnel 12 Shorts | ✅ | clicks a Ko-fi / playlist |
| Post Ko-fi FB+IG | ✅ live | reach, clicks link |
| Playlists binge (PARA DORMIR 40 · Lo-Fi 9) | ✅ | watch-time por sesión |
| WF#1+#2 (Ko-fi en comments) | ✅ deployed | — |
| WF#4 generador email semanal | ✅ (envío manual) | open rate cuando se mande |
| salmo91 long-form | ✅ subido (publica 15-jun) | views, retención |

---

## 2. Métricas a monitorear (venom actualiza)

> Fuente de verdad: `data/venom_truth.json`. Regenerar con @agent venom.

| Métrica | Baseline (2026-06-01) | Última | Meta | Cadencia |
|---------|----------------------|--------|------|----------|
| YPP long-form watch-h | 151.6h (3.8%) | — | 4,000h | semanal |
| Subs YT | 14,000 | — | — | semanal |
| **Retención long-form** | — | **5.2%** (1 video, 23 views) | >40% sleep | semanal |
| **Subscribers beehiiv** | 0 | 0 (post-cleanup) | primeros 10 | **3-5 días** |
| **Apoyos Ko-fi** | 0 | 0 | primer $ | **3-5 días** |
| Fans FB | 1,917 | — | — | semanal |
| Watch-time playlist PARA DORMIR | — (pre-binge) | — | ↑ vs baseline | semanal |

---

## 3. Qué revisar en la PRÓXIMA sesión (checklist venom)

- [ ] **3-5 días post-2026-06-04:** ¿llegó algún subscriber real a beehiiv? ¿algún apoyo Ko-fi? (valida si el flywheel convierte antes de sobre-invertir).
- [ ] ¿El auto-publicador VDD ya fijó comments con Ko-fi? (verificar 1 post reciente FB/IG).
- [ ] ¿salmo91 (MYITKgMsMOU) publicó el 15-jun + entró bien a la playlist?
- [ ] Watch-time de PARA DORMIR: ¿subió tras agregar 8 largos + funnel Shorts?
- [ ] IG bio link puesto? (pendiente Fernando).

---

## 4. Decisiones ABIERTAS (no asumir — resolver con data)

### D1 · Daemon auto-upload long-form
- **Qué:** sumar `upload_to_youtube.py --yes` al daemon `yt-fb-uploader` (hoy solo sube Shorts).
- **A favor:** futuros encolados del schedule suben solos (sube private + publishAt, no público inmediato). Evita el scramble manual de hoy (salmo91).
- **En contra / riesgo:** auto-publish = sensibilidad de Fernando. Si el schedule tiene un video no-revisado, se sube solo. Persistencia automática.
- **Criterio para decidir:** activar SOLO cuando (a) haya ≥2 long-form encolados esperando, Y (b) exista gate de QA previo al encolado (ya existe: qa_longform ≥8). Mientras tanto = subida manual con `--yes`.
- **Estado:** ABIERTA. Default actual = manual. Decidir en sesión con cola real de long-form.

### D2 · Producir más sleep vs medir primero
- **Qué:** rendir salmo23/ansiedad/promesas/rosario.
- **DATA 2026-06-04 (YT Analytics):** único largo con data = `6eHgRtGjaYA` → **23 views, retención 5.2%, avg 6:17 de 120min**. Los otros 8 ≈0 data (recién publicados). El math "sleep 12× historias" asumía 30% ret; real = 5.2% → sleep rinde MUCHO menos de lo proyectado.
- **Verdicto: NO mass-producir sleep aún.** El cuello NO es cantidad de contenido — es **descubrimiento (23 views/5sem) + retención (5.2%) bajos**. Producir 4 sleep al 5% = poco watch-h.
- **Antes de producir, diagnosticar:** ¿por qué no retiene (intro larga? audio? loop obvio?) y por qué no se descubre (thumbnail CTR? título? 0 recomendación del algoritmo?). 
- **Caveat:** sample chico (1 video, 23 views). Re-medir cuando los otros 8 acumulen views (semanal §2).
- **Estado:** ABIERTA → inclinada a PAUSAR producción. salmo23 assets listos (no desperdiciados, esperan).

### D3 · Rotar BEEHIIV_API_KEY (quedó expuesto en chat)
- **Estado:** Fernando dijo NO rotar por ahora. Revisar si el canal es sensible. ABIERTA (low prio).

---

## 4.6 · DIAGNÓSTICO del cuello (2026-06-04, curva retención 6eHgRtGjaYA)

Curva audienceWatchRatio: **1%→100%, 5%→22%, 20%+→4.3% estable**.
- **El cuello tiene 2 capas:** (1) descubrimiento (23 views/5sem) + (2) **early-drop: 78% se va en los primeros ~6min**.
- La **cola 4.3%** que llega a 60min+ = audiencia real de sleep (sesiones largas, genera watch-h). Es el activo a proteger.
- **Hipótesis del drop:** intro/primeros minutos pierden gente (text card largo? arranque de música? mismatch thumbnail↔contenido). NO es solo descubrimiento.
- **Acción próxima sesión:** EXP-002 (intro corta / hook directo 30s) bien apuntado. Reducir el drop convierte samplers→durmientes = más watch-h sin más views. Diagnosticar QUÉ en los primeros 6min ahuyenta (ver el video, no solo la curva).

## 4.5 · Lab operable (capa de captura)

- **Ledger:** `data/experiments.jsonl` (1 línea/experimento: id, hipótesis, video_id, métrica, baseline, ventana, status, decisión, measurements[]).
- **Medición por-video:** `python3 scripts/measure_experiment.py <video_id> [--since YYYY-MM-DD] [--exp EXP-NNN]` → views/watch-h/retención/avg-view. Graba al ledger con `--exp`.
- **EXP-001/002 sembrados** (status: planned) — thumbnail A/B + título intención-búsqueda sobre `6eHgRtGjaYA` (atacan descubrimiento, cuello de D2).
- ⚠️ **Limitación:** impresiones + CTR NO disponibles vía Analytics API con scope actual → medir CTR MANUAL en YT Studio. Views/retención/watch SÍ son auto.
- **Loop ahora cerrado:** experimento (ledger) → medición (script) → log (measurements[] + §6) → decisión (§4). Falta solo el paso de PROMOCIÓN cross-proyecto (venom: hook ritual domingo — decisión de Fernando).

## 5. PAUTAS acumuladas (aprendizajes que ya son regla)

> Se agregan aquí conforme emergen. Son las reglas duras del sistema.

1. **Solo long-form mueve el gate.** Shorts NO cuentan para las 4,000h. Producir Shorts ≠ acercar monetización.
2. **Sleep 120min = 12× más eficiente para el gate que historias** (sleep ~120 watch-h/video vs historia ~10). Priorizar sleep sobre narraciones bíblicas. (data: historias mediana 88 views, 2026-06-04).
3. **El gap no es contenido, es CTA.** El eje del flywheel es la email list (beehiiv). Sin email, todo rinde 1/3.
4. **CTA Ko-fi: 1 de cada 3 comments**, nunca todos. Audiencia mujeres 35-55 valora "tiempo devocional", no venta. Disclosure IA siempre.
5. **beehiiv v2 API: publication ID requiere prefijo `pub_`.** El que muestra la UI viene sin prefijo.
6. **Uploads >500MB: chunks de 10MB + retry**, nunca `chunksize=-1` (broken pipe). Fix en `upload_to_youtube.py`.
7. **Verify-before-build:** confirmar estado REAL antes de construir. Hoy ahorró: 7 "historias para subir" eran flojas, "long-form parado" estaba casi todo subido, daemon "yt-fb-uploader" solo hacía Shorts.
8. **Uploads largos: usar `nohup` detached**, no background del harness (muere en session resume).
10. **Thumbnail DEBE matchear el título + la intención.** Hallazgo 2026-06-05: 6 largos sleep tenían thumbnails de worship clickbait (¡PAZ!, ¡SANIDAD!, fondos día brillantes) contra título DORMIR → mismatch mata discovery+retención. La plantilla GANADORA (cozy/vela/noche del batch lofi) ya existía en el canal — el batch viejo usó la equivocada. Regla: thumbnail de sleep = noche/calma, "PARA DORMIR" visible, CERO clickbait. EXP-001 (6 thumbs realineados, running).
9. **MEDIR retención antes de producir.** Data 2026-06-04: sleep largo real retiene 5.2% (no 30% asumido) + 23 views/5sem. El cuello del gate NO es cantidad de contenido — es **descubrimiento + retención**. Más videos al 5% no acerca las 4,000h. Diagnosticar thumbnail/intro/algoritmo ANTES de rendir más. (mató el supuesto "produce más sleep").

---

## 6. Log de decisiones (fechado)

- **2026-06-04** — Flywheel construido + live E2E. Playlists binge actualizadas. salmo91 subido (fix chunked). Daemon long-form = decisión D1 ABIERTA (no asumida, a petición de Fernando). Triage historias → pivote a sleep (pauta #2).

---

## Refs
- `docs/FLYWHEEL_VDD_2026-06-04.md` · `docs/PLAN_MONETIZACION_ALTERNA_2026-06-04.md` · `data/PLAN_MAESTRO_VD.md`
- venom learning: `apocalipsis/venom/data/learnings/flywheel-monetizacion-vdd.md`
