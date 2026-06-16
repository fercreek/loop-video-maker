# RITMO OPERATIVO — Vertical Religión (@VersiculoDeDios + Palabra De Dios)

> Autor: venom · Generado: 2026-06-15 · Owner del ritmo: Fernando (1-2h/día)
> Plan que alimenta: `data/PLAN_MAESTRO_VD.md` (Operación de Dios) · North Star: `_NEXT.md`
> ROI por formato: `docs/FORMAT_ROI_LONGFORM.md` · Stats vivos: `data/venom_truth.json`
> **Qué es esto:** el ciclo DIARIO (Fernando) + SEMANAL (venom) + reportes de anti-venom, todos atados a las 2 métricas del Plan de Dios. No es un plan nuevo — es el motor que ejecuta el plan que ya existe.

---

## 🟢 EMPIEZA AQUÍ (para Fernando, cada mañana)

1. **Abre Telegram** → chat con @cero_ops_bot. Cada día 9am MX llega tu checkpoint (subs YT + fans FB). Si NO llegó → corre tú el comando del paso 3.
2. **Lee 2 números:** ¿subieron las horas de YouTube? ¿subieron los fans de FB? Eso es todo el "cómo voy".
3. **Abre la terminal y entra a la carpeta** (esto es lo único técnico, cópialo tal cual):
   ```
   cd /Users/fernandocastaneda/Documents/loop-video-maker
   .venv/bin/python3 scripts/checkpoint.py        # tu reporte (refresca el % YPP)
   .venv/bin/python3 scripts/outlier_finder.py    # qué temas están jalando
   .venv/bin/python3 scripts/outlier_analyzer.py --kind historia --top 3   # ideas listas
   ```
   Si un comando da error rojo → no pasa nada, mándamelo y lo veo.
4. **Decide:** ¿produzco 1 historia hoy, o arreglo funnel? (Bloque 1-2 abajo.)

**Diccionario rápido (sin jerga):**
- *YPP / gate* = las 4,000 horas de video largo que YouTube pide para pagarte.
- *Watch hours / horas* = cuánto tiempo total ve la gente tus videos largos.
- *Funnel / wire* = poner en tus Shorts un comentario/link que manda gente a tus videos de dormir.
- *Outlier* = un video que tuvo MUCHAS más vistas de lo normal → el tema jala, lo puedes copiar.
- *Sleep / long-form* = tus videos largos (historias, música para dormir).
- *venom_truth.json* = el archivo donde viven los números reales (se actualiza solo; NO lo edites a mano).

**Quién hace qué:** TÚ produces y decides · **venom** analiza/planea · **anti-venom** (el bot del VPS) publica y reposta solo. Las secciones marcadas "anti-venom" NO las haces tú.

---

## Las 2 únicas métricas que importan (la regla madre)

Todo paso de este ritmo apunta a una de estas dos. Si un paso no mueve ninguna → no se hace.

| # | Métrica del Plan de Dios | Hoy (baseline 06-16) | Meta | Palanca real |
|---|---|---|---|---|
| **M1** | **YouTube — watch-hours long-form / 365d** | 7.0% (279h / 4,000h) | 4,000h | Historias tipo Rut + funnel Shorts→sleep + retención intro |
| **M2** | **Facebook — fans** | 3,332 fans | 5,000 → FB Content Monetization invite | 1 Reel/día hook-first + engagement real |

**Filtro de 1 línea (pégalo en la frente):** *"¿esto sube watch-hours long-form (M1) o fans FB (M2)?"* — Si no → backlog.

**Lo que NO mueve la aguja (no gastar tiempo aquí):** más Shorts sin funnel, lofi 2h nuevo, Google Ads, stories de 20min, Instagram dedicado.

---

# 1. PLAN DIARIO — Fernando (~1-2h)

> Orden fijo. Cada bloque tiene su métrica al lado. La mayoría de días NO produces — optimizas y decides. La producción nueva (historias) es ~2 días/semana, no diaria.

### ☕ Bloque 0 — Leer el pulso (5 min) · [M1 + M2]
1. Abrir Telegram → leer el **checkpoint diario de @cero_ops_bot** (llega 9am MX automático desde VPS).
   - Mide: YT subs · YPP% · watch-hours · FB fans. Es tu tablero de la mañana, ya viene servido.
2. Mirar la **flecha**: ¿YPP% subió vs ayer? ¿FB fans subió? Eso es todo lo que necesitas del estado.
   - Si el checkpoint trae ⏳ (YPP viejo >3d) → correr en Mac `python3 scripts/checkpoint.py` para refrescar.

### 🔎 Bloque 1 — Cazar la próxima historia (15-20 min) · [M1] · solo días de producción
> El outlier loop es nuestro mini-OutlierLabs: te dice QUÉ tema producir, no adivinas.
1. Correr `python3 scripts/outlier_finder.py` → descubre temas con índice alto (views/día ÷ baseline canal).
2. Correr `python3 scripts/outlier_analyzer.py` → Gemini disecciona el top tema + te deja un **brief VDD**.
3. Decisión venom-ROI: **solo produces si el brief es formato Historia tipo Rut** (hook lealtad/emoción).
   No diluvio/éxodo (Noé/Moisés retienen 12%, Rut retiene 25%). Ver `FORMAT_ROI_LONGFORM.md`.

### 🎬 Bloque 2 — Producir o avanzar inventario (30-50 min) · [M1]
Elige UNA según el día:
- **Día de producción (~2×/semana):** render de 1 historia desde el brief del Bloque 1 → QA (`qa_longform.py`, score ≥8) → entra a `data/upload_schedule.json`.
- **Día de optimización (resto):** mover una palanca de retención/funnel del backlog en vez de producir:
  - end-screens en Shorts top → sleep (Fernando manual, pendiente en `_NEXT.md`)
  - re-trim de intro sleep 2h (early-drop 78% — la fuga #1)
  - subir 1 video del inventario parado SOLO si es historia (sleep/lofi NO sin funnel arreglado).

> ⚠️ Regla dura del ROI: **no renderizar lofi/sleep nuevo.** El gate no se cierra produciendo más balde con fugas — se cierra wireando tráfico + tapando la fuga. Producción nueva = solo historias.

### 📘 Bloque 3 — Mover Facebook (10-15 min) · [M2]
1. Confirmar que salió el **Reel del día hook-first** (lo postea el auto-publicador n8n — solo verificas que se publicó).
2. Si no salió → es alerta de infra: lo revisa anti-venom (ver §3), tú no entras al VPS.
3. Mirar el último Reel: ¿hook que para el scroll en 2s? El formato reflexión-hook trae 200+ likes; imagen-plana trae 0-5. Si ves un plano colado → nota para el review semanal de venom (matar ese formato).

### 💬 Bloque 4 — Revisar los responders (5-10 min) · [M1 + M2]
> Tú NO respondes comentarios uno por uno — eso lo hace cero-agent/n8n (anti-venom). Tú auditas que esté vivo y sano.
1. En el **resumen semanal de anti-venom** (Telegram, ver §3) o de un vistazo en FB/YT: ¿los comentarios tienen respuesta real?
2. Los replies reales son el diferenciador vs el AI-slop que YouTube elimina → señal de comunidad → algoritmo favorece.
3. Si ves comentarios sin contestar hace días → es flag de responder caído → anti-venom lo arregla.

### 🎁 Bloque 5 — Capa Ko-fi (2 min, pasivo) · [paralelo]
1. Solo verificar 1×/día: ¿hay un Ko-fi nuevo (miembro/donación)? `ko-fi.com/versiculosdedios`.
2. No es campaña aparte — el CTA ya vive en pinned comments + descripción. Aquí solo registras si entró el primer dólar.

**Cierre del día (1 min):** si algo se atoró o emergió una hipótesis, anótala en `_NEXT.md` (⚡ En proceso). Eso es lo que venom lee el día del review semanal.

---

## Mapa rápido del día (lo que cabe en una tarjeta)

```
9am Telegram checkpoint  →  ¿YPP↑? ¿FB fans↑?           [leer el pulso]
Outlier loop             →  ¿qué historia produzco?      [solo días de prod]
Producir/optimizar       →  1 historia O 1 palanca de retención/funnel
Verificar Reel del día   →  ¿salió el hook-first?        [FB]
Auditar responders       →  ¿comentarios contestados?    [comunidad]
Ko-fi check              →  ¿entró un dólar?             [pasivo]
```

---

# 2. PLAN SEMANAL — venom (1 día fijo: DOMINGO)

> Análisis profundo vs el Plan de Dios. venom NO ejecuta — analiza, decide el foco de la semana, y emite briefs. Output va a `_NEXT.md` + (si aplica) brief a carnage/anti-venom.

### Insumos que venom lee (en orden)
1. `data/venom_truth.json` — refrescar stats YT+FB (¿>24h? regenerar con `@agent venom`).
2. `data/PLAN_MAESTRO_VD.md` — scoreboard + experimentos AstroCap.
3. `docs/FORMAT_ROI_LONGFORM.md` — ranking de formatos (no re-derivar).
4. `_NEXT.md` — qué se atoró / hipótesis del Fernando esta semana.
5. **Resumen semanal de anti-venom** (Telegram, ver §3) — qué se ejecutó realmente.

### Las 4 preguntas del domingo (el análisis)
1. **Progreso del gate (M1):** ¿cuántas watch-hours long-form ganamos esta semana? ¿el ritmo proyecta cerrar el gate en 8-10 meses o nos atrasamos? (tabla de proyección en el plan maestro).
2. **Salud del funnel:** ¿el tráfico de Shorts top está transfiriendo a sleep? ¿la retención de intro subió tras los fixes? El funnel es el cuello confirmado — medirlo cada semana.
3. **ROI por formato:** ¿qué historia retuvo mejor esta semana? ¿algún Reel FB rompió el patrón? Actualizar el ranking si la data cambió.
4. **M2 — fans FB:** ¿crecimos hacia 5k? ¿qué formato de Reel trajo los fans? ¿hay posts planos que matar?

### Output del domingo (lo que venom entrega)
- **Foco de la semana en 1 frase** — ej. "esta semana = tapar la fuga de intro sleep + 1 historia Rut nueva". Va al top de `_NEXT.md`.
- **Cola de producción:** qué historia(s) producir (tema del outlier loop) + qué optimización.
- **Brief a carnage/anti-venom** (si hay ejecución): qué automatizar, success criteria, qué reportar de vuelta.
- **Marcar experimentos AstroCap:** ✅ funcionó / ❌ no / 🔄 optimizar (decisión a fecha 6-jul).

> **Por qué domingo:** el checkpoint diario da la foto del día; el domingo es donde se conecta la foto con el Plan de Dios y se decide la semana. Sin este día, el ritmo diario flota sin dirección.

---

# 3. REPORTES DE ANTI-VENOM — dónde y cuándo

> anti-venom = cero-agent/n8n VPS (MANOS · ejecución). venom analiza → anti-venom automatiza. Estos reportes son el puente: anti-venom deja la evidencia de ejecución donde venom y Fernando la consumen sin entrar al VPS.

| Reporte | Cadencia | Dónde | Quién lo consume | Para qué métrica |
|---|---|---|---|---|
| **Checkpoint diario** (YT subs/YPP%/watch + FB fans) | Diario 9am MX | Telegram @cero_ops_bot (chat 95915749) | Fernando (Bloque 0) | M1 + M2 — el pulso |
| **Salud de infra** (auto-publicador, responders FB/IG/YT, crons vivos) | Diario, integrado al checkpoint o flag-only | Telegram @cero_ops_bot — solo avisa si algo cayó | Fernando | que el Reel/responders no se caigan silenciosos |
| **Resumen semanal de ejecución** (Reels publicados, comentarios contestados, deploys, Ko-fi push) | Semanal (sábado, antes del review venom) | Telegram + log en VPS `/var/www/stats/actions.jsonl` | **venom** (insumo #5 del domingo) | cierra el loop: ¿lo que venom pidió, se ejecutó? |

### Lineamiento venom para anti-venom (cómo deben verse los reportes)
1. **Diario = pulso + excepción.** El checkpoint trae los números; la salud de infra solo grita si algo se rompió (no ruido cuando todo está bien).
2. **Semanal = evidencia de ejecución para el domingo.** venom necesita saber, antes de analizar, qué se movió realmente esta semana — no asumir. El sábado deja el resumen, el domingo venom lo lee.
3. **Todo a Telegram + log persistente** (`actions.jsonl`) para que venom pueda auditar histórico, no solo el último mensaje.
4. **Encaja en el ritmo, no suelto:** diario alimenta el Bloque 0 de Fernando; semanal alimenta el insumo #5 de venom. Cada reporte tiene un consumidor y un momento.

---

# 4. CÓMO TODO SE LIGA AL PLAN DE DIOS

```
                    PLAN DE DIOS (data/PLAN_MAESTRO_VD.md)
                    M1: 4,000h long-form  ·  M2: 5,000 fans FB
                                  ▲
                                  │  decide foco + emite briefs
                    ┌─────────────┴──────────────┐
                    │   DOMINGO — venom (análisis) │  ← lee checkpoints + resumen semanal anti-venom
                    └─────────────┬──────────────┘
                                  │  foco de la semana → _NEXT.md
                    ┌─────────────▼──────────────┐
                    │   DIARIO — Fernando (1-2h)   │  ← outlier loop, produce/optimiza, audita
                    └─────────────┬──────────────┘
                                  │  ejecuta lo automatizable
                    ┌─────────────▼──────────────┐
                    │ ANTI-VENOM — n8n/VPS (manos) │  → checkpoint diario + resumen semanal
                    └──────────────────────────────┘
                                  │
                                  └──► reportes regresan a venom (cierra el loop)
```

- **Diario** → mueve M1 (1 historia / optimización de funnel) y M2 (verifica Reel hook-first). Cada bloque etiquetado [M1]/[M2].
- **Semanal** → mide el avance vs M1/M2, decide qué producir, marca experimentos AstroCap.
- **Anti-venom** → ejecuta la distribución (Reels, responders) que sostiene M2 y el engagement que el algoritmo premia; reporta para que venom mida.

**Anti-switching:** este ritmo NO crea metas nuevas. Las 2 métricas viven en el plan maestro; este doc solo las convierte en hábito diario + revisión semanal.

---

## Cadencia mínima garantizada por semana (no negociable)
- **M1 (YouTube):** 1-2 historias tipo Rut producidas O 1 fix de funnel/retención ejecutado.
- **M2 (Facebook):** 1 Reel hook-first/día (lo sostiene anti-venom) + 0 posts planos.
- **venom:** 1 review domingo con foco de semana en `_NEXT.md`.
- **anti-venom:** checkpoint diario + 1 resumen semanal de ejecución (sábado).

---

## Log de cambios
| Fecha | Cambio |
|-------|--------|
| 2026-06-15 | v1 — Ritmo operativo creado por venom. Diario (Fernando 1-2h, 6 bloques) + semanal (venom domingo, 4 preguntas) + reportes anti-venom (diario/semanal a Telegram + actions.jsonl). Atado a M1 (4,000h long-form) y M2 (5,000 fans FB) del Plan de Dios. Integra checkpoint diario, outlier loop, FORMAT_ROI (historias tipo Rut > sleep > lofi), división venom/anti-venom. |
