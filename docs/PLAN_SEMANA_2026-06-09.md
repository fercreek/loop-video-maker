# PLAN DUAL DE LA SEMANA — @VersiculoDeDios

> Semana: **2026-06-09 → 06-15** · Emitido por: **venom** (análisis) · Ejecuta: Fernando + Claude + **carnage**
> Data fresca: `data/venom_truth.json` (06-09) · Plan maestro: `data/PLAN_MAESTRO_VD.md`
> Operación de Dios · Plan aprobado: **DUAL (opción C)** — dos motores en paralelo

---

## ⚠️ CORRECCIONES DE REALIDAD (vs planes previos)

Tres supuestos del plan anterior cambiaron con research duro. Quedan corregidos aquí:

1. **Reels Play Bonus MURIÓ globalmente el 31-ago-2025.** Ya no existe el programa. El reemplazo es **FB Content Monetization** (programa unificado), **invite-only**, piso real ~5–10k followers + cumplimiento de políticas. → El camino FB ya NO es "verificar invite Bonus", es **llegar a ~5k fans para calificar al invite**.
2. **Etsy DESCARTADO.** Research frío: 65% de tiendas hacen <$100/año, 74% del GMS es US/inglés. Mismatch total con audiencia LATAM-español. **No se incluye Etsy en ningún tablero.**
3. **El gap de Fernando NO es el punto de partida** (ya tiene la audiencia de 14k YT + 2,722 FB que a otros indies les costó años). El gap es **oferta de pago + captura de email + CTA**. No más pipeline de contenido como prioridad de monetización.

---

## 🎯 METAS DE LA SEMANA (una por motor)

| Motor | Meta medible 06-15 | Hoy (06-09) |
|---|---|---|
| **A — FB Reels diario** | Sistema de 1 Reel/día FB+IG corriendo + fans **2,722 → ~3,200** (rumbo a 5k para invite FB Content Monetization en ~3 sem) | 2,722 fans, +42% (campaña Meta CPF $0.012 USD) |
| **B — UNA oferta + captura email** | **1 oferta de pago LIVE** (Ko-fi membresía $5) + captura de email funcionando HOY (sin beehiiv) + CTA puesto en 3 lugares frente a los 14k | Ko-fi existe, $0 captura email, sin CTA activo |

Ambos motores cuestan **~$0 upfront**. Las únicas comisiones son ~10%/venta (Ko-fi/Hotmart) y el gasto opcional de Meta Ads (ya corriendo, decisión aparte).

---

## 🟦 MOTOR A — FB Reels diario (camino real a monetización FB)

> **Tesis:** los Reels reflexión-hook son lo que impulsó el +42% de fans. FB Content Monetization es invite-only con piso ~5–10k followers. El camino es **subir fans con 1 Reel/día reciclado de los Shorts-hook de YT** hasta calificar al invite.

### Tablero A

| # | Acción | Esfuerzo | Owner | Días a resultado | Métrica de éxito |
|---|--------|----------|-------|------------------|------------------|
| A1 | **Automatizar reciclaje Shorts-hook YT → 1 Reel/día FB+IG** (9:16, hook 2s ya viene en el Short). Pipeline: tomar Short ya renderizado → push a FB Reel + IG Reel vía cero-agent (n8n) | medio (setup 1 vez) | 🤖→🕷️ | 2–3 días setup, luego diario auto | Reel publicado cada día sin intervención |
| A2 | **Alternar duración por objetivo:** días impares Reel **14–21s** (algoritmo premia alcance/completion) · días pares **60–68s** (más watch time / engagement). Etiquetar cuál es cuál para medir | bajo | 🤖 | inmediato | tener data de qué duración rinde a 14 días |
| A3 | **Convertir el daemon de versículo-imagen plano** (4 likes) al formato reflexión-hook (200+ likes, 50×) como segundo post diario de respaldo | bajo | 🤖 | 1 día | post imagen >50 likes |
| A4 | **Escalar campaña Meta** (CPF $0.012 USD/fan, 6× bajo umbral) para acelerar la subida a 5k fans → calificar invite. Decisión de Fernando A/B/C abajo | 10 min decisión | 🧑→🕷️ | — | fans rumbo a 5k |
| A5 | **Trackear distancia a 5k fans** semanal (gate del invite FB Content Monetization) | bajo | 🕷️ reporta a 🧑 | semanal | dashboard: fans / 5,000 |

### Qué automatiza cero-agent vs qué necesita Fernando

| Pieza | Quién | Detalle |
|---|---|---|
| Selección del Short del día | 🤖 Claude/daemon | Rotar de la pool de Shorts-hook ya renderizados (r43LS0y0Wrg, MdenXXdtW60, batch venom_*) |
| Publicar Reel FB + IG | 🕷️ cero-agent (n8n VPS) | Graph API, mismo token `palabra-de-dios`. n8n NO depende de la Mac |
| Copy del Reel (hook + caption) | 🤖 Claude | Reusar `short_hook` del registry; disclosure IA |
| Aprobar el batch antes de auto | 🧑 Fernando | Ver 3 Reels de muestra antes de activar el diario (regla: 1 unidad de test antes del batch) |
| Decisión escalar Meta | 🧑 Fernando | A/B/C abajo |

### Decisión Fernando — escalar Meta (NO de carnage)

Campaña `VD-PageLikes-LAL1pct-Jun2026` ACTIVE, CPF **$0.012 USD/fan** (6× bajo el umbral $0.08), CTR 5.77%, sin fatiga. Es la responsable del +42% de fans.

- **A) ⭐🕷️ Escalar a $3,000 MXN lifetime + extender a 06-30** — CPF probado, momentum +42%, empuja a 5k fans (invite FB Content Monetization). Pick venom (data sólida) y Claude (riesgo bajo, creative fuera de learning phase). A $0.012/fan, +5k fans ≈ ~$1,200 MXN.
- **B) Mantener como está** ($1,400, termina 06-17) — conservador, no aprovecha el CPF.
- **C) Escalar fuerte a $5,000 MXN** — llegaría a ~5k fans rápido pero quema presupuesto sin más data de fatiga.

---

## 🟩 MOTOR B — UNA oferta de pago + captura email (vender al activo existente)

> **Tesis (confirmada por benchmark indie):** Fernando ya tiene la audiencia. El bloqueo es que **no hay nada que comprar ni forma de capturar el email**. Shippear UNA oferta esta semana > seguir produciendo.

### B.1 — Qué oferta shippear PRIMERO (recomendación con data)

| Oferta | Conversión esperada | Setup | Fee | Veredicto venom |
|---|---|---|---|---|
| ⭐🕷️ **Ko-fi membresía $5/mes** | Donación/membresía convierte **mejor con audiencia devocional caliente** (low-friction, "apoya el ministerio", sin promesa de entregable complejo). Ya tienes Ko-fi creado | **0** (ya existe, solo activar tier membresía + lead magnet) | ~5% Ko-fi | **SHIPPEAR PRIMERO** |
| Planner Hotmart $12–15 | Mayor ticket pero **requiere producto terminado + página de ventas + más fricción de compra**. Conversión más baja en frío | alto (crear planner PDF, página, checkout) | ~10% Hotmart | Mes 1, después de validar con Ko-fi |

**Por qué Ko-fi primero (data):** (1) cero setup nuevo — está vivo hoy; (2) la audiencia devocional responde a "apoya el ministerio" mejor que a un producto; (3) valida willingness-to-pay HOY sin construir nada; (4) Ko-fi **captura el email** del que baja el lead magnet → resuelve Motor B.2 gratis. El planner Hotmart es el upsell del mes 1, una vez que sepamos quién paga.

> 🧪 **Validación pre-producto (idea Marc Lou, ver plan maestro):** antes de pulir el planner Hotmart, preguntar/vender a los que ya donaron en Ko-fi. Si 3 personas dicen "sí lo compro" → construirlo. No al revés.

### B.2 — Captura email HOY sin beehiiv (workaround)

beehiiv está bloqueado (API key pendiente de Fernando). **No esperar a beehiiv para empezar.**

| Opción | Cómo empieza HOY | Costo | Nota |
|---|---|---|---|
| ⭐🕷️ **Ko-fi captura nativa** | Activar lead magnet "7 días de paz" (PDF) en Ko-fi → Ko-fi pide email para descargar → lista exportable a beehiiv después | $0 | Cero setup extra, ya viene con el Motor B.1 |
| **Google Form simple** | Form "Recibe el devocional diario por correo" linkeado en descripción YT + bio FB/IG → respuestas a Google Sheet | $0 | Backup / paralelo. Migrar a beehiiv cuando se desbloquee |

**Recomendación:** activar **ambas** — Ko-fi captura al que ya tiene intención de pago, el Google Form captura al lurker que solo quiere el devocional gratis. Cuando beehiiv se desbloquee (B en plan maestro), importar las dos listas. No se pierde ningún email por esperar.

### B.3 — Dónde poner el CTA frente a los 14k (sin spam)

| Lugar | Qué poner | Por qué no es spam |
|---|---|---|
| ⭐ **Descripción de cada video YT** (arriba del fold) | 1 línea: "🙏 Apoya el ministerio: [Ko-fi]" + "📩 Devocional diario por correo: [Form]" | Es la zona estándar de links, el viewer la ignora si no le interesa |
| ⭐ **Pinned comment** en los 2 Shorts motor (r43LS0y0Wrg 331h, MdenXXdtW60 104h) | Mismo CTA corto, pineado | Los 2 Shorts generan el 28% del watch time — máxima exposición sin tocar el contenido |
| **Post FB orgánico** 1×/semana (no diario) | "Si este ministerio te bendice, puedes apoyarlo aquí 🙏 [Ko-fi]" + link | 1×/semana, tono de gratitud, no venta agresiva |

**Regla anti-spam:** el CTA va en **metadata** (descripción, comentario pineado, bio) y en **máximo 1 post/semana**, nunca dentro del video ni en cada post. La oferta está disponible, no se empuja.

### Tablero B

| # | Acción | Esfuerzo | Owner | Días a 1er $ | Métrica de éxito |
|---|--------|----------|-------|--------------|------------------|
| B1 | **Activar Ko-fi membresía $5/mes + lead magnet "7 días de paz" PDF** | 30 min | 🧑+🤖 | 1–7 | membresía live + 1ª donación |
| B2 | **Crear Google Form "devocional diario por correo"** + Sheet | 15 min | 🤖 | hoy | form recibiendo emails |
| B3 | **Poner CTA en descripción de videos + pinned comment de los 2 Shorts motor** | 20 min | 🤖→🕷️ | hoy | CTA visible en 3+ lugares |
| B4 | **Post FB de gratitud con link Ko-fi** (1×, tono ministerio) | 10 min | 🕷️ | 1–7 | post >50 likes + clicks a Ko-fi |
| B5 | **Activar Super Thanks YT** (ya calificas con 14k) | 5 min | 🧑 | 1–14 | Super Thanks habilitado |
| B6 | **(Mes 1) Validar planner Hotmart** preguntando a donadores Ko-fi antes de construirlo | bajo | 🤖+🧑 | mes 1 | 3 "sí lo compro" antes de codear |
| B7 | **Desbloquear beehiiv** (API key) — multiplica captura ×3, importa listas Ko-fi+Form | 20 min | 🧑 | desbloquea mes 1 | API key pegada, WF#3/#4 activos |

**Costo total Motor B:** ~$0 upfront. Fees ~5–10%/venta. Sin riesgo monetario.

---

## 🕷️ BRIEF DE EJECUCIÓN — carnage (Motor A automatización + CTA)

> venom analiza, **carnage ejecuta**. Fernando aprueba antes de cualquier acción que gaste o publique.

### Brief carnage 1 — Pipeline reciclaje Shorts → Reel diario FB+IG (Motor A1/A2)
- **Qué:** construir/activar en cero-agent (n8n VPS) el flujo: tomar 1 Short-hook ya renderizado del repo → publicar como Reel en FB (`452922677899760`) + IG (`17841469453382962`) vía Graph API, 1×/día.
- **Params:** token `palabra-de-dios`; alternar duración por día (impar 14–21s alcance / par 60–68s engagement); copy = `short_hook` del registry + disclosure IA; 1 Reel/día MÁXIMO (anti-spam).
- **Fuente de Shorts:** rotar pool (r43LS0y0Wrg, MdenXXdtW60, batch `venom_*`) sin repetir en 14 días.
- **Success criteria:** Reel publicado cada día sin intervención de la Mac; reportar likes/views/reach por Reel y cuál duración rinde más.
- **Reportar a venom:** al cierre de semana, tabla Reel × día × duración × engagement → venom decide qué duración escalar.

### Brief carnage 2 — Escalar campaña Meta (Motor A4, espera aprobación Fernando A/B/C)
- **Qué:** si Fernando aprueba A → subir lifetime budget del adset `120245943144590194` a $3,000 MXN + extender a 06-30, mismo creative `1004017758752293`, LAL 1% MX `120245943055860194`.
- **Objetivo:** llegar a ~5,000 fans (gate invite FB Content Monetization).
- **Success criteria:** CPF se mantiene <$0.04 USD; frequency <2.5 (flag fatiga si supera).

### Brief carnage 3 — Poner CTA en pinned comments + post FB gratitud (Motor B3/B4)
- **Qué:** dejar pinned comment con CTA Ko-fi+Form en los 2 Shorts motor (r43LS0y0Wrg, MdenXXdtW60) + publicar 1 post FB de gratitud con link Ko-fi.
- **Success criteria:** CTA visible en 3 lugares; post FB >50 likes; clicks a Ko-fi medibles.

### Brief carnage 4 — Auditar fatiga + reportar (Motor A)
- **Qué:** al cerrar semana, reportar CPF final, fans totales, frequency, distancia a 5k, y si la LAL 1% conviene refrescar con el seed de los 2,722 fans nuevos.

**Loop de aprendizaje:** carnage escribe en `data/carnage-executions/` → venom lee y cierra el ciclo.

---

## ✅ RESUMEN EJECUTIVO (6 líneas)

1. **Motor A (meta):** sistema de **1 Reel/día FB+IG** corriendo (reciclando Shorts-hook vía cero-agent) → fans **2,722 → ~3,200** rumbo a 5k para calificar al invite **FB Content Monetization** (Reels Play Bonus murió 31-ago-2025).
2. **Motor B (meta):** **1 oferta de pago LIVE** (Ko-fi membresía $5) + captura email funcionando HOY sin beehiiv + CTA en 3 lugares frente a los 14k.
3. **ROI #1:** **shippear Ko-fi membresía $5 + lead magnet HOY** — cero setup, valida willingness-to-pay, y Ko-fi captura el email gratis.
4. **ROI #2:** **CTA en descripción YT + pinned comment de los 2 Shorts motor** (28% del watch time) — máxima exposición a los 14k sin spam, esfuerzo de 20 min.
5. **ROI #3:** **escalar Meta a $3,000 MXN** (CPF $0.012/fan, 6× bajo umbral) para empujar a 5k fans = el gate del invite FB.
6. **Oferta B a shippear PRIMERO: Ko-fi membresía $5/mes** (no el planner Hotmart) — cero fricción, audiencia devocional convierte mejor a "apoya el ministerio", y captura el email. El planner Hotmart es el upsell del mes 1, validado preguntando a los donadores antes de construirlo.
