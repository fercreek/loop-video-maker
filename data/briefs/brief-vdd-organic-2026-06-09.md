# BRIEF NEXO — VDD Orgánico · Batch 1b (workflows cero-agent)
> Emitido por: venom (como nexo) · Fecha: 2026-06-09
> **Batch 1b** — revisado por el par symbiote completo (venom estrategia + carnage red-team + anti-venom infra) el 2026-06-09. Síntesis: `docs/SINTESIS_SIMBIONTES_2026-06-09.md`.
> **Tesis del cruce:** se estaba puliendo CONTENIDO sobre una capa de instrumentación/salud rota. Hay que arreglar el CIMIENTO (token YT vivo, medición real, guard de uploads) antes/junto con los cosméticos. Por eso este batch antepone una sección 🔴 P0.
> Proyecto: @VersiculoDeDios / Página "Palabra De Dios" (FB 452922677899760 · IG 17841469453382962)
> Fuente data viva: `data/venom_truth.json` (regenerado 2026-06-09 20:30, post-borrado verificado)
> Exports leídos: `cero-agent/n8n-exports/{auto-publicador-vdd, yt-comments-agent, ig-comments-agent, fb-comments-agent, daily-stats-vdd}.json`
>
> ⚠️ **NADA se deploya sin (a) aprobación de Fernando de 1 muestra y (b) skill `n8n-deploy` corriendo desde el VPS** (deactivate → PUT → activate, Python+scp, nunca heredoc con `*`, guard `errorWorkflow=nF6RyogQTkjQqkOQ`).
>
> **Convención `estado:`** cada ítem lleva `estado: pendiente | deployado | medido`.
> - `deployado` = ya en prod (verificado `active:true`), falta medir su hipótesis.
> - `medido` = se cerró la ventana y se marcó CONFIRMADA/FALLIDA/INCONCLUSA.

---

## Paso 0 — Confirmación (prerequisito, CUMPLIDO)

- **IDs borrados verificados FUERA:** `r43LS0y0Wrg` y `MdenXXdtW60` devuelven 404 vía Data API. Ya NO están en `top_performers` del snapshot fresco.
- **8 motores legítimos vivos** (verificados hoy): `jvEokzazN4o` (ret 133%), `zfQYgA88gcU` ("revelación", +166 subs), `gEHFYvu1SwI`, `hvV1P06nUck` (NUEVO sub-driver #1, +474 subs), `gRxIKks-ILc`, `HeGUMgQlfFo` (Rut, narrativo, ret 25%), `6eHgRtGjaYA` (sleep 2h, ret 10.8%), `Fp44KoQurkM`.
- **Watch time 28d:** 1,182.9h → 1,172.2h (-10.7h). Caída esperada/sana por el borrado de 2 Shorts; el long-form 365d (YPP) NO se movió (267.7h). NO es regresión.
- **Token YT (auto-publicador):** se arregló `invalid_scope` (token tenía 2 scopes, el cliente pedía 3). Refrescado OK. ⚠️ OJO: esto NO es el mismo token que el de `yt-comments-agent` — ver P0-1.

---

# 🔴 P0 — CIMIENTO (arreglar ANTES de los cosméticos de contenido)

> Los simbiontes coinciden: el plan original optimizaba vanity sobre una base con engagement YT muerto, medición de humo y sin guard de uploads. Estos 4 ítems son el cimiento. El Cambio 4 (funnel) DEPENDE de P0-1.

## P0-1 — Reparar engagement YouTube (MUERTO hace 27 días) ⬅️ el hallazgo clave

- **workflow:** `YT Comments Agent — Versículos de Dios` (ID `SgkhLYIWaK1NmlZA`) — path: `cero-agent/n8n-exports/yt-comments-agent.json`
- **nodo:** nodo HTTP de YouTube (comentarios) + Schedule (cron 15min) `[verificar nombre exacto del nodo en deploy]`
- **campo:** token YT del agente de comentarios + `onError` del nodo HTTP + nuevo cron de refresh
- **HALLAZGO (anti-venom):** `yt-comments-agent` reporta "success" cada 15min, pero el token YT del agente expiró **2026-05-14 (hace 27d)**. El 401 se traga, el nodo marca verde. **El engagement de YouTube lleva ~1 mes sin postearse y nadie se enteró.** Doble golpe: el Cambio 4 (link-funnel) iba a meterse en ESTE workflow muerto → habría fallado silencioso también.
- **cambio_exacto:**
  1. **Re-auth del token YT** del agente (Fernando, OAuth) — `scripts/yt_auth.py`. (Testing-mode caduca a 7 días → ver paso 3.)
  2. **Nodo HTTP YT → `onError: stopWorkflow`** (hoy se traga el 401). Así el 401 dispara el error-workflow → alerta `@cero_ops_bot`. Guard: `errorWorkflow=nF6RyogQTkjQqkOQ`.
  3. **Cron de refresh proactivo cada 5d** (antes de que el token testing-mode caduque a 7). Workflow nuevo o nodo Schedule `[verificar/crear en deploy]`.
- **palanca_data:** engagement YT = 0 real desde 2026-05-14. Sin esto, el funnel del Cambio 4 va a un workflow muerto.
- **hipótesis:** "Si el token revive + el 401 deja de tragarse + refresh cada 5d, entonces el engagement YT se postea de nuevo y cualquier fallo futuro alerta en vez de morir en silencio."
- **baseline:** 0 comentarios posteados en 27d (silent-success) · **target:** comentarios posteados de nuevo + alerta @cero_ops_bot ante 401 · **ventana:** verificar en 24-48h post re-auth
- **owner:** Fernando (OAuth) + carnage (onError + cron refresh + deploy)
- **needs_n8n_deploy:** sí
- **estado:** pendiente
- **riesgo:** este es el más urgente del batch. Bloquea el Cambio 4. Hasta que el token esté vivo, NO deployar Cambio 4.

## P0-2 — Colector `engagement.jsonl` (la medición del loop es humo)

- **workflow:** NUEVO `metricas-vd` (no existe) `[verificar/crear en deploy]` — sustituye la medición-humo de `daily-stats-vdd` (ID `[verificar en deploy]`)
- **nodo:** cron Schedule + GET Graph API por-post + GET YT Analytics por-video + append a archivo
- **HALLAZGO (venom H7 + carnage #4 + anti-venom §3):** `daily-stats-vdd` cuenta *acciones ejecutadas*, NO *engagement recibido*. **El loop venom-nexo NO puede confirmar ninguna hipótesis** (¿el copy subió 4→50 likes? nadie lo sabe). Sin esto, todos los `target` de los cambios de contenido quedan sin forma de medirse.
- **cambio_exacto:** cron VPS "Métricas VD" cada 6h →
  - GET Graph API por-post: `likes/comments/shares/reach` por publicación FB+IG.
  - GET YT Analytics por-video: views/watch-time/retención.
  - Appendea **series temporales por post** (snapshots 6h/24h/72h, NO totales) a `/var/www/stats/engagement.jsonl`.
  - venom lee ese archivo para medir el loop REAL.
- **palanca_data:** sin series temporales por-post no hay forma de validar el lift del hook (Cambio 2) ni del retiming (Cambio 1).
- **hipótesis:** "Si existe `engagement.jsonl` con series por-post, entonces el loop puede marcar CONFIRMADA/FALLIDA cada hipótesis con data, no con humo."
- **baseline:** `daily-stats-vdd` = acciones ejecutadas (vanity) · **target:** `engagement.jsonl` con ≥1 serie/post cada 6h · **ventana:** activo en 48h
- **owner:** carnage construye
- **needs_n8n_deploy:** sí (workflow nuevo)
- **estado:** pendiente
- **riesgo:** bajo. Es additivo (no toca workflows vivos). Bloquea la medición de TODO el batch de contenido — por eso es P0.

## P0-3 — Guard de uploads huérfanos (previene el incidente de hoy)

- **workflow:** NUEVO `guard-uploads-vdd` (no existe) `[verificar/crear en deploy]`
- **nodo:** cron Schedule 1×/día + GET YT API uploads del canal + diff contra tracking local + alerta
- **HALLAZGO (carnage #2 + anti-venom §4):** lo que causó el incidente de hoy — 2 TikToks ajenos colados ~2 semanas como motores fantasma.
- **cambio_exacto:** cron VPS 1×/día →
  - GET YT API: lista uploads del canal `UC2l5TZjHzRtaRjH8kT_yQ2w`.
  - Diff contra tracking local (`data/upload_schedule.json` + `data/lofi_push_plan.json`).
  - Uploads en YT que NO están en el tracking = huérfanos → alerta `@cero_ops_bot` ("algo subió que el sistema no programó").
  - **VPS, no Mac** (regla: prod no depende de Mac encendida).
- **palanca_data:** detecta el caso exacto del incidente (upload no programado colándose como motor).
- **hipótesis:** "Si un cron diario compara uploads YT vs tracking local, entonces un upload huérfano dispara alerta el mismo día en vez de contaminar métricas 2 semanas."
- **baseline:** 0 detección (incidente duró ~2 semanas sin alerta) · **target:** alerta <24h ante upload no programado · **ventana:** activo en 48h
- **owner:** carnage construye
- **needs_n8n_deploy:** sí (workflow nuevo)
- **estado:** pendiente
- **riesgo:** bajo (read-only sobre YT API + alerta). Additivo.

## P0-4 — IDs duplicados ✅ HECHO

- 3 exports compartían `XPWXiyjraNgqSODn` (diferían 107 y 931 líneas — peligro real de revert). **Archivados a `cero-agent/n8n-exports/archived/`.** Fuente de verdad única = `auto-publicador-vdd.json`.
- **owner:** venom · **needs_n8n_deploy:** no · **estado:** medido (resuelto y verificado hoy 2026-06-09).

---

# 🟠 P1 — ESTRATEGIA (no-workflow, formato ligero)

> Reorden venom: el plan original optimizaba vanity, no el GATE (4,000h long-form) ni el primer $. Estos 3 ítems NO son edits de n8n — son palancas estratégicas que van ANTES de los cosméticos.

### P1-0 — Playlists binge (máximo ROI/esfuerzo)
- **Acción:** agregar `6eHgRtGjaYA` (sleep 2h) + `HeGUMgQlfFo` (Rut, ret 25%) a las playlists binge del canal.
- **palanca_data:** playlists binge = palanca YPP gratis fuera del batch. 5 min, sin deploy.
- **owner:** Fernando · **needs_n8n_deploy:** no · **estado:** pendiente · **riesgo:** ninguno.

### P1-1 — Motor B mínimo (cuello del 1er dólar)
- **Acción:** Ko-fi lead magnet PDF + beehiiv API key. **Sin esto, el link Ko-fi del Cambio 4 va a una página vacía.** Shippear ANTES que los cosméticos FB.
- **palanca_data:** Motor B (Ko-fi + email) sin shippear = no hay forma de capturar el primer dólar ni emails.
- **owner:** Fernando + Claude · **needs_n8n_deploy:** no · **estado:** pendiente · **riesgo:** el Cambio 4 envía tráfico Ko-fi a vacío hasta que esto exista.

### P1-3 — 3 plantillas Short ganadoras a producción semanal
- **Acción:** sacar el conversor 12.9× (**revelación / reframe / hook-25s**) de "Fase 2" a producción semanal como 3 plantillas de Short. Es la materia prima del funnel.
- **palanca_data:** estas 3 fórmulas son los motores de subs reales (ej. `zfQYgA88gcU` "revelación" +166 subs, `hvV1P06nUck` +474 subs). Reusan `render_short.py`.
- **owner:** Claude + Fernando · **needs_n8n_deploy:** no · **estado:** pendiente · **riesgo:** bajo.

---

# 🟢 CONTENIDO — cambios n8n (deployados hoy + funnel pendiente de P0-1)

## Cambio 1 — auto-publicador-vdd · retiming 3×/día → 1× a 16:30 MX + ajustar mood

- **workflow:** `Auto-Publicador Versículos — FB + IG` (ID `XPWXiyjraNgqSODn`) — path: `cero-agent/n8n-exports/auto-publicador-vdd.json`
- **nodo:** `Schedule`
- **campo:** `parameters.rule.interval` (array de 3 cronExpression)
- **cambio_exacto:**
  - Viejo (3 entradas):
    ```json
    "interval": [
      {"field":"cronExpression","expression":"0 15 * * *"},
      {"field":"cronExpression","expression":"0 18 * * *"},
      {"field":"cronExpression","expression":"0 1 * * *"}
    ]
    ```
    > Nota: estos crons NO tienen timezone por-cron; el nodo usa `"timezone": "America/Monterrey"`. Así que `0 15` ya es 15:00 MX. Para centrar en la ventana pico 15:30–17:00 → usar **`30 16`** (16:30 MX).
  - Nuevo (1 entrada):
    ```json
    "interval": [
      {"field":"cronExpression","expression":"30 16 * * *"}
    ]
    ```
- **cambio acoplado OBLIGATORIO (nodo `Contexto`):** el nodo `Contexto` deriva `mood` con `now.getUTCHours()`, NO con hora MX. A las 16:30 MX = **22:30 UTC** → `h=22` → cae en el `else` → `mood='gratitud para cerrar el día'` (rama "noche"). Eso contradice el slot pico de tarde. Fix: forzar mood fijo de tarde para el único slot. Reemplazar el bloque de branching por:
  ```js
  const now = new Date();
  const slot = 'tarde';
  const mood = 'esperanza y paz para la tarde';
  const doy = Math.floor((now - new Date(now.getFullYear(),0,0)) / 86400000);
  const books = ['Proverbios','Isaías','Juan','Romanos','Filipenses','Jeremías','Mateo','Colosenses','Santiago','1 Corintios','Lucas','Hebreos','Génesis','Apocalipsis','Efesios'];
  return [{ json: { slot, mood, book: books[doy % books.length], doy, variant: doy % 9 } }];
  ```
  > Mantiene `slot`, `mood`, `book`, `doy`, `variant` (todos consumidos aguas abajo por `Claude Haiku` y `Extraer Texto`). Solo deja de depender de la hora UTC.
- **palanca_data:** FB hora pico 15:30–17:00 = ~50× engagement (reflexión-hook 208 likes vs versículo-plano 2–6 likes, confirmado live 2026-06-09). Bajar de 3×→1× = palanca anti-slop principal.
- **hipótesis:** "Si publico 1 post/día a las 16:30 MX en vez de 3 dispersos, entonces el engagement promedio/post sube y se reduce el ruido de bajo rendimiento."
- **baseline:** antes 3 posts/día, promedio ~4–6 likes en los planos · **target:** ≥50 likes/post · **ventana:** 7 días (medible vía P0-2)
- **owner:** carnage
- **needs_n8n_deploy:** sí
- **estado:** deployado (a `auto-publicador-vdd` hoy 2026-06-09, verificado `active:true`)
- **riesgo:** breaking — si se cambia el cron sin ajustar `Contexto`, el mood saldría "noche/gratitud" a media tarde (incoherente). El cambio acoplado lo previene. (Ya deployado con el cambio acoplado incluido.)

---

## Cambio 2 — auto-publicador-vdd · copy template "reflexión-hook"

- **workflow:** `Auto-Publicador Versículos — FB + IG` (ID `XPWXiyjraNgqSODn`)
- **nodo:** `Claude Haiku`
- **campo:** `parameters.jsonBody` → clave `system`
- **contexto del contrato (NO romper):** el nodo `Extraer Texto` hace `text.split(/\n\n+/)` y espera **exactamente 4 bloques**: `blocks.slice(0,3)` = post (versículo+reflexión+hashtags) y `blocks[3]` = primer comentario. **Mantener los 4 bloques separados por doble salto de línea.** El bloque 4 debe incluir `youtube` en el texto (el safety de `Extraer Texto` añade el link solo si NO contiene "youtube").
- **cambio_exacto:** el `system` actual pide bloque 1 = "[versículo completo con referencia]". El cambio invierte el orden retórico: **el HOOK narrativo va PRIMERO**, el versículo se embebe en la reflexión. Reemplazar el valor de `system` por:
  ```
  Creas posts para 'Versículos de Dios'. Formato EXACTO — 4 bloques separados por línea en blanco:

  [HOOK narrativo de 1 línea que detiene el scroll — una afirmación o pregunta emotiva, NO la cita textual. Ej: "Cuando somos débiles, Él es fuerte." o "Deja ir para ser libre."]

  [reflexión 2-3 oraciones, tono: {{ $json.mood }}, con el versículo de {{ $json.book }} embebido naturalmente y su referencia entre paréntesis]

  [4-5 hashtags en español sin emojis]

  [primer comentario: 1 pregunta orgánica que nace del versículo + CTA breve + link: {{ $json.video_url }}]

  Reglas generales: libro OBLIGATORIO {{ $json.book }}, sin comillas, el HOOK nunca es la cita literal.
  Reglas bloque 4: max 3 líneas, conversacional, NO repitas el versículo, incluye siempre el link.
  ```
- **palanca_data:** reflexión-hook = 208 likes (top FB) vs versículo-plano = 2–6 likes. ~50× diferencia, confirmado dos snapshots seguidos. El hook narrativo en 1ª línea es el único driver.
- **hipótesis:** "Si el post abre con hook narrativo (no la cita textual), entonces el engagement sube hacia el rango de los reflexión-hook (50–200 likes)."
- **baseline:** versículo-plano 2–6 likes · **target:** ≥50 likes/post · **ventana:** 7 días (medible vía P0-2)
- **owner:** Claude redacta el copy final + carnage deploya
- **needs_n8n_deploy:** sí
- **estado:** deployado (a `auto-publicador-vdd` hoy 2026-06-09, verificado `active:true`)
- **riesgo:** slop / breaking — romper el split de 4 bloques rompe el post (queda sin primer comentario / sin link). Validado con ejecución manual de test (4 bloques OK, post hook-first).

---

## Cambio 3 — auto-publicador-vdd · VIDEO_MAP a destino funnel (optimización, NO IDs muertos)

- **workflow:** `Auto-Publicador Versículos — FB + IG` (ID `XPWXiyjraNgqSODn`)
- **nodo:** `Lookup Video YT`
- **campo:** `parameters.jsCode` → objeto `VIDEO_MAP`
- **HALLAZGO (validado contra snapshot fresco):** verifiqué los 16 IDs del VIDEO_MAP vía Data API — **TODOS están vivos** (ninguno apunta a los borrados). El problema NO es IDs muertos; es **destino sub-óptimo**: el `_fallback` apuntaba a `Fp44KoQurkM` (Noé, ret 12% — el long-form que peor retiene).
- **⚠️ CORRECCIÓN DE TESIS (decisión Fernando, 2026-06-09):** venom (Batch 1b draft) propuso `_fallback`→Rut por retención %. **Error: confundió % con minutos absolutos.** Para el gate YPP lo que cuenta son HORAS vistas, no %:
  - Sleep 2h `6eHgRtGjaYA` = 120min × 10.8% = **~13 min/view**
  - Rut `HeGUMgQlfFo` = 18min × 25% = **~4.5 min/view**
  - El sleep 2h da **~3× más minutos/view** → es el MEJOR destino del `_fallback` para el gate. Decisión: el fallback se queda en sleep 2h (lo que ya se deployó hoy).
- **cambio_exacto (deployado):** solo el fallback:
  ```js
  '_fallback':   'https://youtube.com/watch?v=6eHgRtGjaYA'   // sleep 2h: 13 min/view, máx watch-hours/view para el gate
  ```
  > Resto del mapa: ya apunta a sleep videos de 1–2h legítimos y vivos (Juan→`gv8OakHMcgs` 2h, Romanos→`SIw4hjII0nM` 2h, Filipenses→`oA2xnlVLB0s` 2h) → **NO tocar**.
- **mejora opcional pendiente (NO deployada):** Génesis/Éxodo siguen en Noé/Moisés (ret 12-16%). Entre videos de largo similar (~18-20min), Rut (4.5 min/view) > Noé (2.4 min/view) → mover Génesis/Éxodo→`HeGUMgQlfFo` SÍ mejora (aquí el % sí decide porque el largo es comparable). Pendiente, bajo impacto.
- **palanca_data:** gate YPP = watch-HOURS. Sleep 2h 13 min/view es el máximo por-view del catálogo accesible. `Fp44KoQurkM` (fallback viejo) solo 2.4 min/view.
- **hipótesis:** "Si el fallback apunta al sleep 2h (mayor min/view), entonces cada click del comentario suma más watch-hours YPP que cualquier alternativa más corta."
- **baseline:** `6eHgRtGjaYA` ~96 views · **target:** +watch-hours/semana medible · **ventana:** 14 días (medible vía P0-2)
- **owner:** carnage
- **needs_n8n_deploy:** sí (fallback YA deployado; Génesis/Éxodo→Rut = opcional pendiente)
- **estado:** deployado (fallback→sleep 2h `6eHgRtGjaYA`, verificado en deploy de hoy via anti-venom: `fallback 6eHg present: True`)
- **riesgo:** bajo (todos los IDs verificados vivos hoy).

---

## Cambio 4 — yt-comments-agent · cerrar funnel en primer comentario (destino sleep 2h + Ko-fi)

> ⚠️ **DEPENDENCIA DURA: este cambio NO se puede deployar hasta P0-1 (token YT vivo).** El workflow `yt-comments-agent` está MUERTO hace 27d — meter el funnel aquí ahora = fallo silencioso. Deployar SOLO después de re-auth + onError fix.

- **workflow:** `YT Comments Agent — Versículos de Dios` (ID `SgkhLYIWaK1NmlZA`) — path: `cero-agent/n8n-exports/yt-comments-agent.json`
- **nodo:** `Primer Comentario YT`
- **campo:** `parameters.jsCode` → array `ytCtas`
- **contexto del contrato (NO romper):** el dedup vive en `staticData.firstCommentedYT[videoId]` (1 comentario/video). `ytCta = ytCtas[new Date().getDay() % ytCtas.length]` → rota por día. ⚠️ **bug conocido (carnage):** `getDay()` usa día UTC, no MX — la rotación puede desfasarse por la noche MX. Considerar `getDay()` con offset MX al tocar este nodo. Mantener dedup + rotación.
- **cambio_exacto (decisión Fernando = sleep 2h):** destino primario de video = **sleep 2h `6eHgRtGjaYA`** (13 min/view, máx watch-hours/view para el gate — misma mate que Cambio 3, NO Rut). Mantener 1-2 CTAs de Ko-fi. Reemplazar el array:
  ```js
  const ytCtas = [
    '¿Cuál versículo te llegó más al corazón? Cuéntanos 👇\n\n🎧 Para descansar: https://youtu.be/6eHgRtGjaYA',
    'Escribe AMÉN si este video te bendijo 🙏\n\n☕ Apoya este ministerio: https://ko-fi.com/versiculosdedios',
    '¿Qué sientes al escuchar este versículo? ❤️\n\n🎧 Salmos para dormir 2h: https://youtu.be/6eHgRtGjaYA',
    'Comparte con alguien que necesite fe hoy 🙌\n\n☕ Sostén el canal: https://ko-fi.com/versiculosdedios',
    '¿A qué parte de tu vida habla este versículo? 👇\n\n🎧 Música de paz 2h: https://youtu.be/6eHgRtGjaYA'
  ];
  ```
  > **Decisión 2026-06-09:** destino = sleep 2h (no Rut). Para el gate cuentan minutos absolutos: sleep 2h ~13 min/view > Rut ~4.5 min/view. Se mantienen 2 CTAs Ko-fi (índices 1 y 3).
  > Mantener intacto TODO lo demás del nodo (dedup `staticData.firstCommentedYT`, log ping a `172.18.0.1:8765`, returnFullResponse).
- **palanca_data:** funnel roto; el engagement de comentarios no se canaliza a long-form ni a monetización. Sleep 2h 13 min/view = máx watch-hours por click. Ko-fi (`ko-fi.com/versiculosdedios`) confirmado en `data/brief-kofi-fb-ig-2026-06-04.md` — pero la página Ko-fi va vacía hasta P1-1.
- **hipótesis:** "Si el primer comentario lleva link al sleep 2h / Ko-fi, entonces se generan clics → watch hours long-form (máx min/view) y/o apoyos Ko-fi."
- **baseline:** 0 links de funnel en comentarios (y 0 comentarios reales por token muerto) · **target:** clics/watch-hours atribuibles · **ventana:** 14 días desde re-auth (medible vía P0-2)
- **owner:** carnage
- **needs_n8n_deploy:** sí
- **estado:** pendiente (BLOQUEADO por P0-1)
- **riesgo:** (1) **bloqueante:** sin P0-1, deploy = fallo silencioso. (2) Ko-fi a página vacía hasta P1-1. (3) slop/spam si el link es idéntico — la rotación de 5 (2 Ko-fi, 3 Rut) lo mitiga; YouTube puede marcar links repetidos: monitorear remociones.

---

## Cambio 5 — NUEVO workflow `cross-post-fb-reels-vdd.json` (FB Reels → IG Reels)

- **workflow:** NUEVO `cross-post-fb-reels-vdd` (no existe — gap: hoy IG solo recibe imágenes planas del auto-publicador)
- **palanca_data:** cross-post no existe; IG es el canal lento (+11 fans vs +835 FB en 8 días). Costo ~0 reusando Reels que ya se publican en FB.
- **spec a nivel nodo** (reusa patrones de `auto-publicador-vdd` y `ig-comments-agent` — mismos env vars `$env.FB_PAGE_ID`, `$env.FB_PAGE_ACCESS_TOKEN`, API `v25.0`, IG ID `17841469453382962`):

  1. **`Schedule`** (scheduleTrigger) — `0 19 * * *` (19:00), timezone `America/Monterrey`. 1×/día, fuera del slot de 16:30 (techo anti-slop: máx 2 piezas FB/día).
  2. **`GET Reels FB`** (httpRequest) — `GET https://graph.facebook.com/v25.0/{{ $env.FB_PAGE_ID }}/video_reels?fields=id,title,permalink_url,source&access_token={{ $env.FB_PAGE_ACCESS_TOKEN }}`
  3. **`Filtrar Nuevos`** (code) — dedup con `staticData.crossPostedReels` (objeto `{reelId: true}`). Tomar el más reciente NO cross-posteado. Si no hay nuevo → return [] (corta el flujo).
  4. **`Crear Container IG`** (httpRequest) — `POST https://graph.facebook.com/v25.0/17841469453382962/media` con body `{ media_type: 'REELS', video_url: <source/permalink del reel FB>, caption: <título + hashtags>, access_token: $env.FB_PAGE_ACCESS_TOKEN }`. Devuelve `{id}` = creation_id. ⚠️ carnage: `video_url` debe ser público (el `source` de Graph puede ser firmado/expirable).
  5. **`Poll Status`** (httpRequest + loop/wait) — IG Reels es **async**: `GET https://graph.facebook.com/v25.0/{creation_id}?fields=status_code&access_token=...`. Repetir cada ~10–15s hasta `status_code == 'FINISHED'` (timeout ~5 intentos). ⚠️ carnage: si queda stuck `IN_PROGRESS` y se publica antes de FINISHED, falla — respetar el timeout y NO publicar sin FINISHED.
  6. **`Publicar IG`** (httpRequest) — `POST https://graph.facebook.com/v25.0/17841469453382962/media_publish` con `{ creation_id, access_token }`.
  7. **`Marcar Posteado`** (code) — `staticData.crossPostedReels[reelId] = true`.
  8. **`HC Ping + Log`** (httpRequest) — ping a `http://172.18.0.1:8765/log` con `{action:'cross_post', platform:'ig', workflow:'cross-post-fb-reels-vdd', reel_id}`.
- **hipótesis:** "Si los Reels que ya publico en FB se cross-postean a IG Reels, entonces IG gana N Reels/semana sin esfuerzo extra y acelera su crecimiento."
- **baseline:** 0 Reels en IG · **target:** N Reels/semana (≥3) publicados con status FINISHED · **ventana:** 14 días
- **owner:** carnage construye el workflow; Fernando aprueba 1 muestra antes de activar el cron
- **needs_n8n_deploy:** sí (workflow nuevo — crear, NO PUT)
- **estado:** pendiente (al fondo del orden — vanity, depende de P0-2 para medirse)
- **riesgo:** breaking — IG Reels async (polling correcto). Correr **`n8n-env-audit`** antes para confirmar `FB_PAGE_ACCESS_TOKEN`/`FB_PAGE_ID` + permiso `instagram_content_publish`.

---

## Cambio 6 (Fase 2 — esbozo, NO en este batch)

Motor de Reels reflexión-hook reciclando Shorts ganadores (`zfQYgA88gcU`, `jvEokzazN4o`, `hvV1P06nUck`) como Reels FB/IG nativos con hook narrativo (ya existe `render_short.py`). El lever real 50×. Brief separado tras validar Cambio 2. NO bloquea este batch. Relacionado con P1-3 (las 3 plantillas Short).

---

## Tabla resumen

| # | Cambio | owner | needs_deploy | estado | riesgo | orden ejecución |
|---|--------|-------|:---:|:---:|--------|:---:|
| **P0-1** | Reparar engagement YT (muerto 27d): re-auth + onError + refresh 5d | Fernando + carnage | sí | pendiente | bloquea C4 | **1** (cimiento) |
| **P0-2** | Colector `engagement.jsonl` (medición real cada 6h) | carnage | sí (nuevo) | pendiente | bajo, additivo | **2** (sin esto no se mide nada) |
| **P0-3** | Guard uploads huérfanos (cron diario YT vs tracking) | carnage | sí (nuevo) | pendiente | bajo, additivo | **3** (previene incidente) |
| **P0-4** | IDs duplicados archivados | venom | no | medido ✅ | — | hecho |
| **P1-0** | Playlists binge (6eHgRtGjaYA + HeGUMgQlfFo) | Fernando | no | pendiente | ninguno | **4** (ROI/esfuerzo máx) |
| **P1-1** | Motor B mínimo (Ko-fi PDF + beehiiv) | Fernando + Claude | no | pendiente | C4 va a vacío sin esto | **5** (1er dólar) |
| **P1-3** | 3 plantillas Short ganadoras a producción | Claude + Fernando | no | pendiente | bajo | **6** (materia prima funnel) |
| 1 | Retiming 3×→1× a 16:30 + mood fijo | carnage | sí | deployado | breaking (mitigado) | **7** (ya en prod) |
| 2 | Copy reflexión-hook (hook 1ª línea) | Claude + carnage | sí | deployado | slop/breaking (mitigado) | **8** (ya en prod) |
| 3 | VIDEO_MAP `_fallback`→sleep 2h (13 min/view) | carnage | sí | ✅ deployado | bajo | **9** (en prod, verificado) |
| 4 | Link funnel→sleep 2h + Ko-fi en comentario YT | carnage | sí | pendiente | BLOQUEADO por P0-1 | **10** (tras P0-1) |
| 5 | NUEVO cross-post FB Reels→IG | carnage + Fernando | sí (nuevo) | pendiente | breaking (async) | **11** (vanity, al fondo) |
| 6 | Motor Reels reflexión-hook (Fase 2) | — | — | — | — | brief aparte |

**Orden de ejecución (Batch 1b):** P0-1 → P0-2 → P0-3 (cimiento) → P1-0 → P1-1 → P1-3 (estrategia) → Cambios 1/2/3 ya deployados (verificar C3 apunta a Rut) → Cambio 4 (solo tras P0-1) → Cambio 5 al fondo.

**Techo anti-slop:** FB máx ~2 piezas/día (1 post 16:30 + 1 cross-post Reel 19:00) · IG máx 2 (1 imagen + 1 Reel) · YT comentarios reactivos con dedup (1 link/video).

## Deploy / verificación

- **NADA se deploya sin:** (a) aprobación Fernando de 1 muestra, y (b) skill **`n8n-deploy`** desde VPS `root@2.24.111.80` (deactivate → PUT → activate; crear para workflows nuevos P0-2/P0-3/Cambio 5; Python+scp, nunca heredoc con `*`; guard `errorWorkflow=nF6RyogQTkjQqkOQ`).
- **Health-gate (anti-venom):** `n8n-deploy` debe probar la key (curl→200) antes del PUT + disparar 1 exec post-deploy y verificar terminal-reach (la exec llega al nodo de acción, no solo "success").
- **Post-deploy:** `n8n-health` (terminal-reach) + `n8n-env-audit` (vars `$env` en container) + confirmar `active:true` en UI.
- **Cambio 4:** NO deployar hasta P0-1 (token vivo). Cuando se deploye → ejecución manual de test que confirme el comentario se postea de verdad (no silent-success).
- **Cambio 5:** 1 ejecución de prueba → confirmar Reel en IG status FINISHED antes de activar cron.
- **Loop venom-nexo:** conservar el contrato de brief. Cambiar cadencia de "semanal fija" a **event-driven** (disparar al subir long-form o al cerrar ventana de hipótesis, NO "es lunes"). **No puede medir nada hasta que exista `engagement.jsonl` (P0-2).** Al medir → comparar baseline vs target → marcar CONFIRMADA/FALLIDA/INCONCLUSA → propagar a `next_actions` → actualizar `estado: medido`. Log crudo en `data/carnage-executions/2026-06-09-vdd-organic.json`.

## Fuentes de verdad
- `docs/SINTESIS_SIMBIONTES_2026-06-09.md` (revisión 3 simbiontes — base de Batch 1b)
- `data/venom_truth.json` (snapshot 2026-06-09 20:30)
- `cero-agent/n8n-exports/auto-publicador-vdd.json` (Cambios 1-3, ID `XPWXiyjraNgqSODn`)
- `cero-agent/n8n-exports/yt-comments-agent.json` (P0-1 + Cambio 4, ID `SgkhLYIWaK1NmlZA`)
- `cero-agent/n8n-exports/archived/` (IDs duplicados P0-4)
- `data/brief-kofi-fb-ig-2026-06-04.md` (URL Ko-fi)
- skill `n8n-deploy` (protocolo) · `n8n-health` · `n8n-env-audit`
