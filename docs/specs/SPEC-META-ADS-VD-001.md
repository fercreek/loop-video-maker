# SPEC-META-ADS-VD-001 — Campaña Page Likes Operación de Dios
> Fecha: 2026-06-02 · Owner: carnage (ejecuta) + venom (monitorea)
> Estado: ACTIVA — en ejecución desde 2026-06-02

---

## Problem Statement

La Página FB "Palabra De Dios" tiene 1,933 fans — por debajo del gate de 10,000 necesario para FB Subscriptions (monetización mensual recurrente). Sin crecer fans, el canal solo puede monetizar via YPP (gate 4,000h, 8-10 meses) sin ingresos intermedios. El costo de no resolver: $0 ingreso FB hasta que YPP destrabarse.

---

## Goals

1. Validar CPF real del nicho devocional cristiano LATAM con paid ads (dato que no existe hoy)
2. Crecer fans de 1,933 → mínimo 2,033 (+100) con MX$300 lifetime
3. Fans de calidad: ER post-campaña ≥ 2% (señal de que no son fans fantasma)
4. Decisión accionable al día 7: escalar / pivotar a Video Views / activar shoutout

---

## Non-Goals

1. **NO** crecer subs YouTube — objetivo es fans FB, no canal YT
2. **NO** reemplazar el shoutout orgánico — es complementario, no sustituto
3. **NO** validar contenido de video — solo valida targeting + copy + CPF del nicho
4. **NO** escalar automáticamente — Fernando decide con la data del día 7
5. **NO** resolver el gate YPP — ese camino es long-form orgánico, no paid ads

---

## Contexto

Primer test de Meta Ads para Página "Palabra De Dios" (FB 452922677899760).
Objetivo de negocio: crecer fans de 1,933 → 10,000 para desbloquear FB Subscriptions monetización.
Budget: MX$300 lifetime (~$15 USD). Único intento — con data real decidimos si escalar.

---

## IDs de campaña

| Objeto | ID | Estado |
|---|---|---|
| Custom Audience (seed fans) | `120245942980230194` | ✅ |
| Lookalike 1% MX | `120245943055860194` | ✅ |
| Campaña | `120245943071430194` | ACTIVE |
| Adset | `120245943144590194` | ACTIVE Jun 2-17 |
| Creative v1 (copy secular) | `1004017758752293` | EN USO (pendiente swap) |
| Creative v2 (copy devocional) | PENDIENTE | Por crear |
| Ad | `120245946921170194` | ACTIVE |

---

## Decisiones de diseño

### Audiencia
- Lookalike 1% de fans existentes (1,933 fans) — workaround al targeting religioso eliminado ene 2025
- Geo: MX + CO (español LATAM, CPF más bajo)
- Age: 25-55
- Bid: LOWEST_COST_WITHOUT_CAP

### Copy — CAMBIO APROBADO (Expert 2 ganó debate)

**v1 (actual, secular):**
- Headline: "Música para dormir y relajar la mente"
- Body: "2 horas de música tranquila y versículos de paz. Sin anuncios. Gratis en YouTube."

**v2 (pendiente deploy, devocional con filtro):**
- Headline: "Versículos que calman la mente antes de dormir"
- Body: "Para los que necesitan paz real antes de dormir. 2 horas de Palabra y música suave. Sin anuncios. 🙏"

**Razón del cambio:** "Música para dormir" atrae audiencia secular → ER bajo post-like → penaliza reach orgánico. "Versículos" actúa como filtro natural → fans con inclinación devocional → 3-5x mejor ER.

### Objetivo — DEBATE PERDIDO (carnage mantiene)
- Page Likes se mantiene para este test (cambio de objetivo = nueva campaña)
- Expert 1 tiene razón: próxima campaña → Video Views con Short `r43LS0y0Wrg`
- Este ciclo valida CPF real del nicho, que es la data que falta para decidir escalar

---

## Criterios de éxito (evaluar al día 7 — Jun 9)

| Métrica | Verde | Amarillo | Rojo | Acción |
|---|---|---|---|---|
| CPF real | <MX$3 | MX$3-8 | >MX$8 | Verde→escalar, Rojo→parar |
| Fans nuevos | >100 | 50-100 | <50 | — |
| CTR del anuncio | >1% | 0.5-1% | <0.5% | — |
| ER posts post-campaña | >2% | 1-2% | <1% | Si rojo: fans de baja calidad |

---

## Backlog de mejoras (post este ciclo)

| # | Mejora | Origen | Prioridad |
|---|---|---|---|
| 1 | Creative v2 (copy devocional) | Expert 2 ganó debate | ⚡ Esta semana |
| 2 | Campaign 2: Video Views con Short `r43LS0y0Wrg` | Expert 1 | 🟡 Si CPF >$0.08 |
| 3 | Shoutout canal devocional LATAM $50 | Expert 3 + venom | 🟡 Paralelo a ads |
| 4 | Pipeboard Pro para no tener límite semanal | Blocker operativo | 🔵 Evaluar ROI |

---

## Open Questions

| # | Pregunta | Quién responde | Cuándo | Bloqueante |
|---|---|---|---|---|
| Q1 | ¿CPF real del nicho en MX será <MX$3? | Data Meta Ads | Jun 9 (día 7) | Sí — decide si escalar |
| Q2 | ¿Fans de Page Likes tendrán ER ≥2% post-campaña? | venom Analytics | Jun 17-30 | Sí — valida calidad de audiencia |
| Q3 | ¿Pipeboard Pro (~MX$580/mes) vale para el uso actual de carnage? | Fernando | Post-ciclo | No — puede esperar reset semanal |
| Q4 | ¿El copy v2 ("Versículos que calman...") mejora CTR vs v1? | Comparar cuando esté live | Jun 9+ | No — mejora marginal |
| Q5 | ¿Hay canal devocional LATAM para shoutout $50 disponible? | venom research | Esta semana | No — paralelo al ad |

---

## Requirements

### P0 — Campaña activa entregando
- [x] Campaña ACTIVE con audience LAL 1% fans
- [x] Budget MX$300 lifetime Jun 2-17
- [x] Ad con creative cinematico y CTA Like Page
- [ ] Creative v2 (copy devocional) swap antes del día 7

### P1 — Calidad y seguimiento
- [ ] Venom reporta CPF real al día 7 (Jun 9)
- [ ] Venom compara ER posts antes vs después del ciclo
- [ ] Decisión documentada en este spec: escalar / pivotar / parar

### P2 — Mejoras futuras
- [ ] Campaign 2: Video Views con Short `r43LS0y0Wrg` (si CPF confirma nicho receptivo)
- [ ] Shoutout canal devocional LATAM $50 (paralelo, independiente de esta campaña)

---

## Execution log

| Fecha | Acción | Quién | Resultado |
|---|---|---|---|
| 2026-06-02 | Campaña creada (4/5 objetos) | carnage | Blocker app dev mode |
| 2026-06-02 | Creative v1 + Ad creados via Pipeboard | carnage | ✅ |
| 2026-06-02 | Campaña activada, start hoy Jun 2 | carnage | ✅ ACTIVE |
| 2026-06-02 | Budget corregido MX$1,400→MX$300 | carnage | ✅ |
| 2026-06-02 | Debate 3 expertos — copy cambia, objetivo se mantiene | venom+carnage | Creative v2 pendiente |
| 2026-06-02 | Creative v2 pendiente | carnage | Pipeboard semanal agotado |
