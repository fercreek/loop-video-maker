# FORMAT ROI — Long-form hacia el gate YPP

> Autor: venom · Generado: 2026-06-15 · Data viva: YT Analytics API (365d, per-video)
> Fuente de verdad de stats: `data/venom_truth.json` · scores: `data/video_scores.json`
> **Objetivo único de este doc:** decidir qué formato long-form producir/subir MÁS para cerrar el gate YPP (4,000 h de long-form / 365 d). Estado: 294.1 h = 7.4%.
> ⚠️ Re-leer ESTE doc antes de decidir "qué long-form subo" — no re-derivar cada sesión.

---

## TL;DR (la decisión en 4 líneas)

1. **El cuello NO es producción de long-form nuevo — es retención de intro + funnel.** Tienes ~30 h en disco sin subir y sleep 2h con 96 views. Producir más no mueve el gate si nadie lo ve y se cae al minuto 6.
2. **Ranking ROI-al-gate: Historias bíblicas (tipo Rut) #1 · Sleep 2h #2 (solo si arreglas intro + funnel) · Lofi 2h #3 (muerto, 1-8 views) · 120min-temas #4 (no existe como formato propio en este canal).**
3. **Regla:** Historias = el caballo de ahora (mejor retención + SEO + views orgánicas). Sleep 2h = la apuesta de volumen-hora, pero apágala hasta arreglar el early-drop del 78%.
4. **Próximo $ de esfuerzo va a:** (a) acortar/arreglar intro sleep 2h, (b) wire Shorts→sleep, (c) replicar el formato Rut. NO a renderizar más lofi.

---

## Data viva por formato (YT Analytics, 365d, 2026-06-15)

| Formato | Video (id) | dur | watch-h 365d | views | retención | subs |
|---|---|---|---|---|---|---|
| **Historia** | Rut y Noemí `HeGUMgQlfFo` | 18min | **51.0** | 660 | **25.6%** | 2 |
| **Historia** | Job `iMPxY1zAsFw` | 20min | 14.8 | 184 | **23.8%** | 0 |
| **Historia** | Moisés `4OxApIJ7L-E` | 24min | 17.1 | 272 | 16.1% | 1 |
| **Historia** | Noé `Fp44KoQurkM` | 21min | 20.0 | 476 | 12.2% | 1 |
| **Sleep 2h** | Paz de Dios `aqFlPGDD2ww` | 120min | 23.3 | 112 | 10.4% | 2 |
| **Sleep 2h** | Salmos `6eHgRtGjaYA` | 120min | 19.4 | 98 | 9.9% | 0 |
| **Sleep 2h** | Esperanza `N7YzBNgd3l4` | 120min | 3.1 | 38 | 4.1% | 0 |
| **Sleep 2h** | Salmo 91 `MYITKgMsMOU` | 120min | s/data | recién (15-jun) | — | — |
| **Lofi 2h** | Biblia `jdOSUMO3dbk` | 120min | 1.1 | 8 | 7.3% | 0 |
| **Lofi 2h** | Ansiedad `l5LFYLVZOd4` | 120min | 0.1 | 7 | 1.2% | 0 |
| **120min-temas** | — | — | **no existe como formato propio** | — | — | — |

**Hallazgo estructural:** los "120min temas (paz/fe/provisión)" del CLAUDE.md NO son un formato vivo separado — los únicos videos de 120min en el canal son los de **sleep/lofi** (música + versículos). Lo que el repo llama "120min temas" es de facto el mismo bucket que sleep. Tratarlos como categorías separadas era ficción documental. Quedan **3 formatos reales**: Historias (18-24min), Sleep 2h, Lofi 2h.

---

## Costo de producción relativo (esfuerzo por unidad)

| Formato | Pipeline | Costo variable | Render | Esfuerzo total |
|---|---|---|---|---|
| **Historia** | Script Claude (14 escenas, ~2.5k palabras) + Gemini Imagen ×14-16 (personajes) + TTS + render 4 workers | **Medio-alto** — Gemini Imagen $ + filtros de contenido + QA por escena | ~2.5 min | **ALTO** (creativo + visual + revisión) |
| **Sleep 2h** | MusicGen local (gratis) + 1-2 fondos + Ken-Burns ultra-lento + overlay título | **~0** (todo local) | 25-40 min | **BAJO** |
| **Lofi 2h** | Igual que sleep (MusicGen local + fondo) | **~0** | 25-40 min | **BAJO** |

Nota: render largo ≠ esfuerzo humano. Sleep/lofi tardan más en render pero corren solos. Historias tardan poco en render pero consumen sesión creativa + Gemini $ + QA.

---

## ROI-al-gate = watch-hours por unidad de esfuerzo

**La métrica que importa: ¿cuántas horas-que-cuentan-YPP gano por unidad de trabajo invertido?**

| Formato | watch-h / video (mejor caso vivo) | watch-h / view | Esfuerzo | **ROI-al-gate** |
|---|---|---|---|---|
| **Historia (Rut)** | 51.0 h | 0.077 h/view | Alto | **🥇 ALTO** — retención 2.5× sleep, trae views orgánicas (660 vs 98), genera el #1 driver del +116h YPP |
| **Sleep 2h (bueno)** | 23.3 h | 0.21 h/view | Bajo | **🥈 MEDIO** — h/view altísimo (6min/persona) PERO solo si llega tráfico; hoy muere por falta de views + early-drop |
| **Lofi 2h** | 1.1 h | 0.14 h/view | Bajo | **🥉 NULO** — 1-8 views/video. Producir es gratis pero la distribución es cero. ROI real = 0 |
| **120min-temas** | n/a | n/a | n/a | **N/A** — no existe; es sleep con otro nombre |

**Lectura crítica de h/view:** sleep 2h captura 0.21 h por cada view (vs 0.077 de historias) — en teoría es la máquina de volumen-hora más eficiente POR VIEW. Pero historias gana 6.7× más views orgánicas. El gate se cierra con `views × h/view`. Hoy:
- Historia Rut: 660 × 0.077 = **51 h** (real)
- Sleep mejor: 112 × 0.21 = **23 h** (real, capado por tráfico)
- **Si sleep tuviera el tráfico de un Short top (4,975 views de `jvEokzazN4o`) a 1% transfer = 50 views → +10 h. A 5% = 250 views → +52 h de UN solo video.** Ahí está la palanca dormida.

---

## 1. Ranking de formatos por ROI-al-gate (qué produces MÁS de aquí en adelante)

1. **🥇 Historias bíblicas (formato Rut, NO Noé/Moisés)** — produce más de este. Mejor retención (25%), mejor SEO buscable, trae views orgánicas solas, es el driver confirmado del avance YPP. El sub-formato importa: **Rut/Job (25%) >> Noé/Moisés (12-16%)**. Replicar el patrón de Rut (hook fuerte + lealtad/emoción), retirar el de Noé/Moisés.
2. **🥈 Sleep 2h — CONDICIONAL.** Es el formato de mayor volumen-hora potencial (0.21 h/view, casi cero costo). Pero NO produzcas más hasta arreglar (a) intro early-drop 78% y (b) funnel desde Shorts. Tienes 4 ya subidos rindiendo 4-23 h cada uno por falta de tráfico — más unidades sin tráfico = más ceros.
3. **🥉 Lofi 2h — PAUSAR producción.** 1-8 views/video, 0.1-1.1 h. Idéntico costo a sleep pero sin tracción. No produzcas más hasta entender por qué sleep (mismo formato) saca 10× sus views. Hipótesis: thumbnail/keyword. Medir antes de gastar render.
4. **N/A 120min-temas** — no es un formato real; consolidar mentalmente con sleep.

---

## 2. Cuándo conviene cada uno (regla de decisión)

- **Quieres views orgánicas + subs + retención decente + alimentar el gate de forma sostenible** → **Historia tipo Rut.** Es el único long-form que se descubre solo (SEO + retención). Default para producción nueva.
- **Quieres volumen-hora masivo y YA tienes tráfico para mandarle (Shorts top wired, playlist binge activa)** → **Sleep 2h.** Su h/view es el más alto del canal. Pero es un amplificador de tráfico, no una fuente — sin funnel es un pozo seco.
- **Nunca produzcas lofi nuevo** hasta que un test A/B de thumbnail/keyword explique el gap views sleep-vs-lofi. Mismo costo, 10× menos retorno.
- **Regla de oro:** Historia = motor de adquisición de horas. Sleep = multiplicador de horas (necesita combustible = tráfico de Shorts). Lofi = en cuarentena.

---

## 3. El cuello real: ¿producción o optimización?

**El cuello es OPTIMIZACIÓN, no producción.** Evidencia dura:

- Tienes **~30 h de long-form en disco sin subir** (6×120min + 3 lofi 2h) + 16 stories en disco. Producción no es la restricción.
- El **sleep 2h destino del funnel tiene 96-112 views** tras semanas. El inventario existe; el tráfico no llega.
- El **early-drop del 78% en los primeros 6 min** del sleep tira la retención a 10% — cada view que sí llega rinde la mitad de lo que podría.
- Los Shorts generan **924,665 views / 4,574 h** que NO cuentan YPP y NO están wired al long-form que SÍ cuenta.

**Los 3 fixes de optimización, en orden de ROI:**

1. **Funnel Shorts→Sleep** (esfuerzo bajo, impacto alto) — pinned comment + end-screen de los Shorts top (`jvEokzazN4o` 4,975 views, `hvV1P06nUck` +474 subs, `zfQYgA88gcU`) → sleep 2h. Transferir 1-5% del tráfico de Shorts = decenas-cientos de horas que hoy se pierden. **Ya parcialmente hecho (Y1 funnel pinned comments 06-10); falta end-screens (Fernando manual).**
2. **Arreglar intro sleep 2h** (esfuerzo medio, impacto alto) — el 78% se va en 6 min. Hook de 30s directo (EXP-002) sube la retención → cada view rinde más. Sin esto, mandar tráfico a un balde con fugas.
3. **Replicar formato Rut, retirar Noé/Moisés** (esfuerzo medio, impacto medio) — única producción nueva justificada: historias que retengan 25%, no 12%.

**Conclusión:** el gate no se cierra renderizando — se cierra wireando el tráfico que ya tienes (Shorts→sleep) y tapando la fuga de retención. Producción nueva = solo historias tipo Rut. Todo lo demás es optimizar lo existente.

---

## Brief sugerido a carnage (handoff ejecución)

> venom analiza, carnage ejecuta. Acciones derivadas de este análisis, pendientes de aprobación de Fernando:

1. **End-screens en 5 Shorts L4** → sleep 2h `6eHgRtGjaYA` (pinned comments ya hechos 06-10). Success: end-screen visible en los 5. Reportar CTR si la API lo expone.
2. **Re-render intro sleep 2h** con hook 30s (EXP-002) → re-subir o trim. Success: retención primeros 6min sube de 22% a >40%. Medir a 14d.
3. **NO producir lofi/sleep nuevo** hasta cerrar #1 y #2. Próxima producción long-form = 1 historia formato Rut (hook lealtad/emoción, no diluvio/éxodo).

---

## Notas de método

- watch-h 365d, retención (averageViewPercentage) y views = YT Analytics API live per-video, 2026-06-15.
- Salmo 91 `MYITKgMsMOU` recién publicado (15-jun) sin data aún — medir a 14d; SEO top (keyword altísima intención), candidato si retiene.
- Costo de producción = juicio venom sobre los pipelines (`STORY_PIPELINE.md` ~2.5min render + Gemini Imagen; `SLEEPING_PIPELINE.md` 25-40min render, MusicGen local gratis).
- "120min-temas" listado en CLAUDE.md como Track 1 NO tiene videos vivos distintos de sleep — corregir la doc si se quiere precisión (los 120min publicados son todos sleep/lofi).
