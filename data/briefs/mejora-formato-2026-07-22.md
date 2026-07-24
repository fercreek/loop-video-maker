# 🎬 Mejora de formato — VDD (YouTube + Facebook)
> Autor: **venom** · 2026-07-22 · Canal @VersiculoDeDios-v1u · FB "Palabra De Dios" (452922677899760)
> Pregunta: ¿cómo mejoramos el TIPO de video que producimos?
> Data leída ESTA sesión: `ypp-progress.jsonl` (al 07-11, token YT Analytics roto desde entonces) ·
> `video_catalog.json` · `orphan-uploads.json` (07-23 UTC) · `FORMAT_ROI_LONGFORM.md` (06-15) ·
> `PRODUCTION_BRIEF_2026-07-04.md` · outlier-briefs 06-29→07-20 · `venom/data/versiculos-fb.json` (fetch 07-22, Graph API vivo)
> ⚠️ Todo dato YT posterior al 2026-07-11 es invisible (token roto). FB sí está al día de hoy.

---

## 1 · Diagnóstico: por qué cayó el ritmo a 3.6h/día

**El 3.6 exagera la caída, pero la caída es real. Dos capas:**

**Capa medición (parcial):**
- El "13h/día" del 07-10 estaba **inflado por el catch-up del 07-02** (+66.6h en un día: los 2 sleep entrando al top con data acumulada de días sin snapshot). Ese pico rodó dentro de la ventana 7d y la sostuvo alta.
- El ritmo orgánico REAL de julio (deltas diarios 07-05→07-10) fue **~5-6h/día**: +7.7, +6.3, +5.0, +4.7/2d.
- El delta del 07-11 fue **+0.2h** — el mismo día que murió el token. Hipótesis: snapshot parcial/truncado, no colapso real [SIN VERIFICAR — no hay forma de confirmar sin re-mint del token].

**Capa estructural (la que importa):**
- **Cero long-form nuevo subido desde el 2026-06-22** (`video_catalog.json`: últimos = reflexión `0rmdsqsJpLk` + oración `h7E7qa2qHxc`, ambos 06-22). Excepción: el Salmo 23 3h `T-ljF2qcNYQ` apareció en top contributors el 07-05 — **no está registrado en catalog ni en upload_schedule** (huérfano de tracking; subida ~07-04 inferida de su primera aparición [SIN VERIFICAR fecha exacta]).
- `orphan-uploads.json` (corrida 07-23 UTC) confirma: en la ventana de 14 días **lo ÚNICO publicado son Shorts de 32-34s** (versículo diario, n8n auto). Shorts NO cuentan YPP.
- Consecuencia: el motor del canal es el **sub-push a 14.3k subs + RELATED** (trazado 06-20: Rut = SUBSCRIBER 25.9h + RELATED 22.1h, SEARCH 0.6h). Ese push solo dispara con uploads nuevos. Un mes sin long-form fresco = el push se gasta en Shorts que no mueven el gate, y la curva vive del catálogo viejo, que ya decayó:
  - Rut `HeGUMgQlfFo`: **congelado en 51.0h desde ~06-15** (front-loaded, +0 en un mes).
  - Sleep 2h `aqFlPGDD2ww`: congelado en 23.6h desde 07-02.
- **Lo único que empuja hoy:** `T-ljF2qcNYQ` (Salmo 23 · 3h): 24.7h→36.6h en 6 días = **~2h/día él solo, con apenas 100 views**. Y la reflexión `0rmdsqsJpLk` (+1.3h/sem, ret 35.6%).

**Respuesta corta:** no es que un formato "dejara de funcionar" — es que **se dejó de subir el formato que funciona**. El único long-form de julio (1 sleep 3h) es también el que más empuja.

---

## 2 · Ranking de formatos por ROI-al-gate (data más fresca, al 07-11)

| # | Formato | Evidencia viva | h/view | Estado |
|---|---|---|---|---|
| 🥇 | **Sleep 3h título-búsqueda** | `T-ljF2qcNYQ`: 36.6h / 100 views / 6 días · ~2h/día sostenido | **0.37** — el más alto jamás medido en el canal (sleep 2h = 0.21) | PRODUCIR MÁS — es el único upload de julio y es el #2 del canal ya |
| 🥈 | **Reflexión 13-15min (título-pregunta)** | `0rmdsqsJpLk` "¿Por Qué Dios Permite el Dolor?": 19.8h / 259 views / **ret 35.6%** = la retención más alta de TODO el long-form del canal | 0.076 | Nuevo caballo de views orgánicas — mitad del costo de una historia (sin 14 escenas Gemini) |
| 🥉 | **Historia tipo Rut** | 51.0h lifetime pero **+0h en 30 días** (front-loaded) | 0.077 | Motor de subs/views al publicar, no de horas sostenidas. Tope 2/sem sigue vigente |
| 4 | Sleep 2h viejos | `aqFlPGDD2ww` +0h desde 07-02; `6eHgRtGjaYA` estancado | 0.21 | Sin tráfico dirigido no crecen — destino de funnel, no producción nueva |
| 5 | Lofi 2h | 1.1h / 8 views (sin cambio desde 06-15) | — | MUERTO — confirmado otra vez. Y ver §4: el funnel FB apunta AQUÍ (bug) |

Los 4 outlier-briefs consecutivos (06-29, 07-06, 07-13, 07-20) convergen: **sleep con SEO de necesidad universal ("dormir", "ansiedad", año futuro) es el formato outlier del nicho** (ratios 19-135×). La data propia del canal ahora lo confirma con `T-ljF2qcNYQ`.

---

## 3 · TOP 3 mejoras CONCRETAS al tipo de video

### ⭐ Mejora 1 — Duración: el sleep default pasa de 2h a 3h
- **Evidencia:** `T-ljF2qcNYQ` (180min) rinde **0.37 h/view vs 0.21** del mejor 2h — +76% de horas por cada view, con el MISMO esfuerzo humano (MusicGen local, render corre solo). Con 100 views ya es el #2 del canal en 6 días.
- **Qué cambiar en el próximo render:** `render_sleep.py --duration 180` como default; título fórmula probada: `SALMO/keyword + PARA DORMIR + duración + año` (ej: "SALMO 91 PARA DORMIR 3 HORAS 2026 · Bajo Su Sombra Toda la Noche"). Intro corta 4s ya es default del script (EXP-003).
- **Extra obligatorio:** registrar `T-ljF2qcNYQ` en `video_catalog.json` (hoy es huérfano de tracking — riesgo de dup y de ceguera de medición).
- **Esfuerzo:** BAJO (render desatendido, ~horas de máquina, 0 Gemini). 2-3 por semana es sostenible.

### Mejora 2 — Nuevo sub-formato: reflexión 13min con título-pregunta
- **Evidencia:** `0rmdsqsJpLk` tiene **ret 35.6% — nadie más en el canal pasa de 25%** — y 259 views orgánicas sin push especial. Es exactamente el patrón de los outliers ("pregunta existencial + revelación bíblica directa", replicabilidad 85% según brief 07-20).
- **Qué cambiar:** producir 1-2/semana con la fórmula: título = pregunta que duele ("¿Por qué Dios guarda silencio?", "¿Dios sigue ahí cuando nada cambia?") · hook = confrontar la creencia común en la 1ª frase · 13-15min · fondos reusados (93 en disco).
- **Por qué mueve el gate:** es el formato que mejor convierte el sub-push en horas (ret 2× historias) a la MITAD del costo de una historia narrada (sin 14 escenas de personajes, sin Gemini $).
- **Esfuerzo:** MEDIO (guión Claude + TTS + render_story con fondos existentes).

### Mejora 3 — Cadencia: mínimo 2 long-form/semana, sin semanas en cero
- **Evidencia:** la caída de ritmo correlaciona 1:1 con las 4 semanas sin uploads long-form (solo Shorts 33s auto). El catálogo viejo dejó de crecer (Rut +0h/30d); cada semana sin upload = sub-push de 14.3k subs desperdiciado en Shorts que no cuentan YPP.
- **Qué cambiar:** mix semanal fijo = **2 sleep 3h + 1 reflexión** (ambos render barato). Historia tipo Rut solo cuando haya sesión creativa disponible — es bonus, no base.
- **Proyección con ese mix [estimación, no dato]:** si cada sleep 3h nuevo replica ~2h/día en su 1ª semana y decae a ~0.5h/día, 8-10 sleep vivos + reflexiones ≈ 12-18h/día en 6-8 semanas — vs 5-6 actual. El gate (2,653h restantes) baja de ~500 días a ~150-200.
- **Esfuerzo:** BAJO en horas-humano; el costo es disciplina de arranque de render.

**NO producir (sin cambio):** lofi 2h · historias tipo Noé/Moisés (ret 12-16%).

---

## 4 · Facebook: qué crece fans y qué replicar

**Estado (Graph API, fetch 2026-07-22):** **4,256 fans** · **+797 follows/28d (~28/día)** · faltan **744 para 5k** → al ritmo actual la meta cae **~mediados-fines de agosto** sin hacer nada nuevo.

**Qué SÍ jala (replicar):**
| Post (últimos 2 días) | Tipo | Views | Engagement |
|---|---|---|---|
| "Ven a Cristo hoy ✝️" | **Reel** | 1,276 | **330** (268 reacts, 39 comments, 23 shares) |
| "Cada día es una oportunidad 🌅" | **Reel** | 221 | 90 (74 reacts, 14 comments) |
| "Gracias por los desafíos" | Reel | 72 | 24 |

**Qué NO jala:** imágenes estáticas de versículo (posts 14:00) = **0 engagement** en las últimas 4 · posts de texto largo (22:30 auto) = 0-3. Las 28d insights lo confirman: 36,991 video views vs 550 page views — la página ES sus Reels.

**Patrón del Reel ganador:** invitación directa/emocional corta ("Ven a Cristo hoy") > gratitud genérica. Los comments (39) y shares (23) del top sugieren que el CTA emocional simple dispara el algoritmo. Mantener 1 Reel/día; sesgar los hooks a invitación/consuelo directo.

**🐛 BUG DE FUNNEL detectado (fix inmediato, esfuerzo ~0):** los captions de TODOS los Reels recientes linkean a `https://youtu.be/jdOSUMO3dbk` — que es el **LOFI muerto (1.1h, 8 views, ROI=0 según FORMAT_ROI)**. El funnel FB→YT está apuntando al peor video del canal. Cambiar el link del template (n8n `vdd-short-to-3` / auto-publicador) → `T-ljF2qcNYQ` (Salmo 23 3h, el mejor h/view). Con 1,276 views en un Reel, un 2% de click = ~25 views ≈ **+9h de gate de UN Reel**. Hoy esos clicks caen en un pozo.

---

## Resumen ejecutivo (5 líneas)
1. El ritmo no cayó por formato — cayó porque **no se sube long-form desde 06-22** (salvo 1 sleep 3h huérfano que es justo el que más empuja).
2. **Sleep 3h = nuevo rey** (0.37 h/view, +76% vs 2h, mismo esfuerzo). Default de producción.
3. **Reflexión título-pregunta = el descubrimiento** (ret 35.6%, la más alta del canal, mitad de costo que historia).
4. **FB llega a 5k en ~1 mes solo** con los Reels actuales — pero el funnel apunta al lofi muerto: cambiar 1 link = horas gratis.
5. Bloqueador de medición: re-mint token YT Analytics (cuenta brand) — sin él, todo lo posterior al 07-11 es ciego.
