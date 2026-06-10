# VENOM SPEC — Explicado (manual de lectura)

> El compañero del spec ejecutable `data/briefs/brief-vdd-organic-2026-06-09.md`.
> Si abres el spec y no entiendes qué es o cómo usarlo → lee esto primero (~3 min).
> Última actualización: 2026-06-09.

---

## 1. ¿Qué es un "venom spec"?

Es un **contrato ejecutable** que conecta dos mundos que antes vivían separados:

```
LO QUE LA DATA DICE          →  EL CAMBIO EXACTO EN EL SISTEMA
(venom_truth.json)              (qué nodo, qué línea, qué valor)
```

Antes, venom decía cosas como *"el funnel está roto, manda más tráfico al sleep"* — una observación que **alguien tenía que traducir a mano** a un cambio concreto. Esa traducción manual es donde se pierde el contexto (y donde se colaron los 2 TikToks ajenos: nadie tenía un contrato que dijera "esto NO es tuyo").

El spec elimina esa traducción. Cada ítem ya viene con: **qué workflow, qué nodo, qué campo, el valor viejo → nuevo copy-pasteable, la hipótesis que prueba, y cómo se mide.** Quien lo ejecuta (carnage o Fernando) no interpreta nada — aplica.

**Por qué importa:** sin spec, cada mejora es una conversación que se re-deriva cada vez. Con spec, es un artefacto auditable que cualquiera (o tú en otra sesión, sin memoria de hoy) puede ejecutar y medir.

---

## 2. Cómo leer un ítem (campo por campo)

Cada cambio del spec tiene esta forma. Ejemplo real anotado:

```
## Cambio 1 — retiming 3×/día → 1× a 16:30 MX
- workflow: Auto-Publicador (ID XPWXiyjraNgqSODn)   ← QUÉ workflow tocar en n8n
- nodo: Schedule                                     ← QUÉ caja dentro del workflow
- campo: parameters.rule.interval                    ← QUÉ propiedad exacta
- cambio_exacto: 3 crons → "30 16 * * *"             ← copy-paste, sin interpretar
- palanca_data: FB hora pico 15:30-17:00 = 50×       ← el NÚMERO de venom_truth que lo justifica
- hipótesis: "si publico 1×/día a las 16:30..."      ← qué creemos que pasará
- baseline: 4 likes · target: 50+ · ventana: 7d      ← cómo sabremos si funcionó
- owner: carnage                                     ← QUIÉN lo ejecuta
- needs_n8n_deploy: sí                                ← ¿toca el VPS?
- riesgo: breaking (mood acoplado)                   ← qué puede salir mal
- estado: deployado                                  ← pendiente | deployado | medido
```

La regla de oro: **si un campo no tiene número real de `venom_truth.json`, es hipótesis, no hecho** — y se marca como tal. venom nunca inventa cifras.

---

## 3. Por qué cada cambio del batch (en una línea)

**🔴 Cimiento (P0) — sin esto, lo demás es teatro:**
- **P0-1 Token YT:** el engagement de YouTube lleva 27 días muerto (el token expiró y el bot marcaba "success" sobre el error). Reparar + alertar cuando falle.
- **P0-2 Colector de métricas:** hoy medimos "acciones ejecutadas", no "likes recibidos" → el loop no puede saber si algo funcionó. Esto lo arregla.
- **P0-3 Guard de huérfanos:** lo que dejó pasar los 2 TikToks ajenos 2 semanas. Avisa el mismo día si sube algo que no programamos.

**🟠 Estrategia (P1):**
- **P1-0 Playlists:** encadenar videos largos = más horas vistas gratis (la palanca más barata del gate YPP).
- **P1-1 Motor B:** el link de Ko-fi no sirve si la página está vacía → poner el PDF gratis + lista de correo. Es el camino al primer dólar.
- **P1-2 Funnel→Rut:** mandábamos tráfico al sleep 2h que retiene 10.8% (lo quema). Rut retiene 25% → ahí debe ir.
- **P1-3 Plantillas Short:** 3 formatos ya probados que ganan suscriptores ("revelación", "reframe", "hook-25s") → producirlos en serie.

**Contenido (ya deployado hoy):**
- **C1 retiming:** 3 posts/día dispersos → 1 a las 16:30 (hora pico, 50× engagement).
- **C2 copy hook-first:** abrir con gancho narrativo, no con la cita (la cita plana = 4 likes; el gancho = 200+).
- **C3 VIDEO_MAP:** el comentario automático ahora apunta al destino-funnel correcto.

---

## 4. Cómo se mide (el loop)

```
1. venom emite el spec (cada ítem con baseline + target + ventana)
2. carnage/Fernando ejecuta el cambio
3. el colector (P0-2) guarda el engagement real por post en engagement.jsonl
4. cuando vence la ventana (7-14d), venom compara:
        baseline vs número real
   → CONFIRMADA (alcanzó target) · FALLIDA (no) · INCONCLUSA (muestra chica)
5. lo que CONFIRMA entra al plan permanente; lo que FALLA se documenta y se itera
```

**Clave:** el loop NO puede cerrar hasta que exista el colector (P0-2). Por eso es P0 — sin medición, el spec emite hipótesis que nunca se confirman, y el "loop" es solo deploys a ciegas.

**Cadencia:** no es "cada lunes" fijo. Se dispara por **evento**: cuando subes un long-form nuevo, o cuando vence la ventana de una hipótesis. Menos teatro de proceso, más señal.

---

## 5. Quién hace qué

| Owner | Hace | Ejemplos |
|-------|------|----------|
| **venom** | Analiza data + emite/actualiza el spec. NO ejecuta. | Regenera `venom_truth.json`, escribe el brief |
| **Claude** | Redacta copy/prompts, edita exports locales, escribe docs | Copy hook-first (C2), este explicador |
| **carnage** | Ejecuta cambios en producción (con aprobación) | Deploy n8n, construir workflows nuevos |
| **anti-venom** | Salud de infra, resuelve deploys, monitorea | Arregló el 401 de hoy, diseña el colector |
| **Fernando** | Aprueba 1 muestra antes de cada batch + acciones manuales | Re-auth token YT, activar Ko-fi, OAuth |

**Regla de oro (no negociable):** nada se activa en automático (cron diario) sin que Fernando vea **1 muestra** primero (1 copy, 1 Reel, 1 comentario). Y nada toca producción sin el skill `n8n-deploy` desde el VPS.

---

## TL;DR
El venom spec es la lista de cambios concretos + por qué + cómo se mide. Este doc explica cómo leerla. El spec vive en `data/briefs/brief-vdd-organic-2026-06-09.md`; la data que lo respalda en `data/venom_truth.json`; la síntesis que lo corrigió en `docs/SINTESIS_SIMBIONTES_2026-06-09.md`.

---

## 6. Content-gen loop (Venom Video-Leveling)

> El spec de arriba arregla la **distribución** (workflows n8n). Este loop gobierna la **producción**:
> qué Shorts/textos generar, en qué orden, y solo si la rúbrica predice que van a rendir.
> Rúbrica: `venom/registry/video-leveling.md` · Scores: `data/video_scores.json`.

### El ciclo (6 pasos)

```
1. PUNTUAR     todo video (vivo + programado) con la rúbrica de 6 ejes -> video_scores.json
2. GAPS        leer los scores: ¿qué eje rinde bajo cross-portafolio? ¿qué tema/formato falta?
3. DECIDIR     elegir qué generar: de las 23 oraciones SIN usar en oraciones_pool.json
               (fe/esperanza/paz/gratitud/protección/sanación/familia/dormir/ansiedad/...)
               aplicando una de las 3 plantillas ganadoras:
                 - "revelación/secreto"  (control zfQYgA88gcU, 42 subs/1k)
                 - "reframe NO-era-X"     (control 5mv5kXnfZ1U, +189 subs)
                 - "hook-25s"             (control hvV1P06nUck, +474 subs)
4. SCORE PRE   puntuar el borrador ANTES de producir. Gate: solo se genera lo que predice >=L4.
               (un Short de plantilla ganadora + tema buscable + funnel wired predice ~6.5-7 = L4)
5. WIRE        producir con render_short.py -> entry en data/shorts_schedule.json (yt_id/fb_id)
               -> ig-daemon publica. CADA pieza nace con funnel-wiring: pinned comment + end-screen
               -> sleep 2h (6eHgRtGjaYA). Esto sube el eje #6 de 2 a 9 desde el dia 1.
6. REALIMENTAR tras publicar, engagement.jsonl (P0-2) trae retención/subs reales
               -> re-puntuar el eje Retención (deja de ser hipótesis) -> vuelve a paso 1.
```

### Por qué este loop (alineado al plan v2 + anti-slop)

- **Los scores SON las hipótesis del venom-nexo.** Cada puntaje pre-publish es una apuesta ("este Short dará L4"); `engagement.jsonl` la confirma o la mata. Sin el colector (P0-2), Retención del score queda como hipótesis — el loop NO cierra hasta que exista.
- **El eje Funnel-wiring obliga la decisión A:** cada pieza linkea al sleep 2h `6eHgRtGjaYA` (destino del funnel, cuenta horas para YPP). Por eso ningún video nace huérfano.
- **Anti-slop respetado:** el gate >=L4 + cadencia 1 Short/día + 1 reel cross-post evita el volumen-basura que YouTube eliminó. No se produce por producir; se produce lo que la rúbrica predice que rinde.
- **Copiar, no inventar (pauta #11):** las 3 plantillas YA existen como controles ganadores. El loop replica esas fórmulas sobre temas nuevos del pool, no diseña formatos desde cero.

### Gap actual + la decisión que sale (2026-06-09)

De los 22 videos puntuados: **0 en L5, 12 en L4, 9 en L3, 1 en L2.** El eje que frena a TODO el portafolio = **Funnel-wiring** (casi todo en 2/10: huérfano). Ningún Short toca L5 no por mala calidad creativa sino porque **no linkea al long-form que cuenta YPP**.

**Decisión que sale del gap (no de opinión):**
1. **Primero distribución, no producción.** Antes de generar 1 Short nuevo, ejecutar Y1 (pinned comment + end-screen de los Shorts L4 → sleep 2h). Eso sube el eje Funnel de ~5 Shorts L4 a L5 sin producir nada. ROI máximo.
2. **Luego generar 3 Shorts formato "revelación/reframe"** sobre temas con keyword de búsqueda fuerte del pool aún sin usar — candidatos: `milagro_001` (reframe "¿necesitas un milagro?"), `soledad_001` (revelación "no estás solo"), `tristeza_001` (hook "¿triste sin saber por qué?"). Cada uno nace wired al sleep 2h → predice L4-L5.
3. **NO mass-producir sleep** (pauta #9 + D2): los 7 sleep/lofi puntúan L3 por retención 10.8% real. Arreglar la intro de `6eHgRtGjaYA` (EXP-002, hook 30s) ANTES de rendir más sleep.

> Este loop NO genera contenido en automático. Sigue la regla de oro §5: Fernando ve 1 muestra (1 Short scoreado) antes de cualquier batch.
