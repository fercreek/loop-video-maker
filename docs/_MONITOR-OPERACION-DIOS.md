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
- **Qué:** rendir salmo23/ansiedad/promesas/rosario (sleep 12× más watch-h que historias).
- **Criterio:** producir tras confirmar que los sleep ya vivos retienen >40% (medir en §2). No producir a ciegas.
- **Estado:** ABIERTA. salmo23 assets listos; render pospuesto (RAM).

### D3 · Rotar BEEHIIV_API_KEY (quedó expuesto en chat)
- **Estado:** Fernando dijo NO rotar por ahora. Revisar si el canal es sensible. ABIERTA (low prio).

---

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

---

## 6. Log de decisiones (fechado)

- **2026-06-04** — Flywheel construido + live E2E. Playlists binge actualizadas. salmo91 subido (fix chunked). Daemon long-form = decisión D1 ABIERTA (no asumida, a petición de Fernando). Triage historias → pivote a sleep (pauta #2).

---

## Refs
- `docs/FLYWHEEL_VDD_2026-06-04.md` · `docs/PLAN_MONETIZACION_ALTERNA_2026-06-04.md` · `data/PLAN_MAESTRO_VD.md`
- venom learning: `apocalipsis/venom/data/learnings/flywheel-monetizacion-vdd.md`
