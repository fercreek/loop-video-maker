# Auditoría Cross-Ecosistema — Planes Maestros
> Fecha: 2026-06-02 · Owner: venom · Leer desde: `_NEXT.md` de cada repo
> Standard de referencia: Operación 20K (SL) + Operación de Dios (VD)

---

## ¿Qué califica como "Plan Maestro" en este ecosistema?

El estándar observable en los dos planes que SÍ existen:

| Elemento | OPERACION-20K (SL) | Operación de Dios (VD) | Mínimo requerido |
|---|---|---|---|
| **Nombre de operación** | Operación 20K | Operación de Dios | Sí (naming + fecha) |
| **Meta norte con número** | $20,000 MXN MRR al 15-jul | YPP 4,000h + FB Reels Bonus | Sí — número + deadline |
| **Scoreboard por canal** | MRR por cliente + cobrado vs esperado | YT hrs / FB fans / IG por plataforma | Sí — métricas vivas |
| **Fases 1-3 accionables** | 0→Validar / 1→Escalar / 2→Sostener | Quick Wins / Momentum / Gate | Sí — acciones, no wishlist |
| **Experimentos con tracker** | Budget gates + kill rules | AstroCap 10 experimentos | Sí — éxito = número |
| **Reglas anti-switching** | 6 reglas explícitas | Anti-switching: un solo plan | Sí — previene fragmentación |
| **LOG de cambios** | Tabla por fecha | Tabla por fecha | Sí — historia viva |
| **Single source of truth** | SSOT pointer en studio-link | `venom_truth.json` manda | Sí — una verdad, no varias |

---

## Tabla de estado por proyecto

| Proyecto | Tiene plan maestro? | Archivo | Meta norte | Scoreboard | Fases | Experimentos | LOG | NEXT.md |
|---|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Studio Link | ✅ COMPLETO | `venom/campaigns/OPERACION-20K/README.md` | ✅ $20K MRR al 15-jul | ✅ por cliente | ✅ 3 fases + budget gates | ✅ 19 entradas log | ✅ vivo | ✅ `angels/studio/_NEXT.md` |
| Versículos de Dios | ✅ COMPLETO | `loop-video-maker/data/PLAN_MAESTRO_VD.md` | ✅ YPP dual (YT + FB) | ✅ por plataforma | ✅ Fase 1-3 | ✅ 10 experimentos AstroCap | ✅ vivo | ✅ `loop-video-maker/_NEXT.md` |
| Contreras Code | ❌ NINGUNO | — | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ `angels/cc/_NEXT.md` (backlog, sin estrategia) |
| Vayla | ❌ PARCIAL | `angels/vayla-dance/_NEXT.md` es pipeline de deals, no plan maestro | ❌ (no hay meta norte numérica) | ❌ | ❌ | ❌ | ❌ | ✅ (bien poblado comercialmente) |
| Dance Leveling | ❌ NINGUNO | `angels/dance-leveling/` tiene CLAUDE.md (guardrails WA) y finanzas internas, pero cero estrategia de crecimiento | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ (no existe `_NEXT.md`) |
| Agencia Cero | ❌ NINGUNO | `cero-agent/_NEXT.md` es un log de infra (n8n, bots, reliability) — no es un plan de marca | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (infra, no crecimiento) |
| Cargo Control | ❌ NINGUNO | Solo existe repo de código (`/Documents/cargo-control/`) — sin contexto angels, sin plan | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Gaps detallados por proyecto

### Contreras Code — Gaps críticos

**Lo que SÍ tiene:**
- `angels/cc/_NEXT.md`: pipeline de contenido LinkedIn + carousel skills
- `angels/cc/README.md`: mejor post P-035 MPP (687 impressions)
- `context/projects/contreras-code.md`: catálogo servicios (Starter/Growth/Premium)
- Leveling venom: L3★ (5.9/10) — a 0.1 de L4
- Skills: `cc-carousel`, `cc-post-image`, `proposal-pdf`
- Contenido: 16 imágenes listas en `_LISTOS_METRICOOL/`, sin programar

**Lo que NO tiene:**
- Meta norte: ¿cuántos clientes Starter/Growth/Premium en qué fecha?
- Revenue objetivo: catálogo dice $5k-15k setup + $3k-12k/mes — ¿cuál es el target?
- Embudo definido: LinkedIn → leads → demos → cierres. ¿Cuántos leads/mes?
- YouTube CC: mencionado en contexto como "en construcción" — sin plan de canal
- Métricas base: 0 datos de LinkedIn followers/engagement en venom (fetcher no existe)
- Nombre de operación: inexistente

**Dato real disponible:** el único número concreto de CC es P-035 MPP carousel = 687 impressions. Todo lo demás es backlog sin prioridad.

---

### Vayla — Gaps críticos

**Lo que SÍ tiene:**
- `angels/vayla-dance/_NEXT.md`: pipeline de 4 deals activos con fechas y montos
- Pricing real: `_PRICING.md` + `_PRICING.yaml` (cotizador funciona)
- Playbooks completos: foráneo, discovery, objection-handling, pricing-decisions
- Clientes documentados: Dahyana ($22k-25.6k), Manuel, Ingrid, Irma con fichas individuales
- Propuesta template y 1 propuesta real (Dahyana v2)
- Leveling venom: L4 (6.4/10) — producto sólido, SEO fuerte, redes muerto

**Lo que NO tiene:**
- Meta norte: ¿cuántos eventos/año? ¿revenue anual target? Pricing actual = $7k-$25k+/evento pero no hay objetivo
- Scoreboard: ¿cuántos eventos en 2026? ¿MRR de gestión si alguien paga mensual?
- Estrategia de redes: IG @vayla.dance y FB Vayla dance existen pero sin contenido propio (0 posts según leveling)
- Embudo nuevo: hoy es 100% inbound (según contexto). ¿Hay plan de activación outbound?
- Experimentos: ninguno documentado
- Nombre de operación: inexistente

**Dato real disponible:** Deals activos valen ~$47.6k-53.6k MXN combinados (Dahyana+Manuel). Sin plan, solo pipeline.

---

### Dance Leveling — Gaps críticos

**Lo que SÍ tiene:**
- App Rails en `cargo-control/` (no dance-leveling, ese repo no existe como directorio)
- `angels/dance-leveling/`: CLAUDE.md (guardrails WA bot), `_INTERNAL-FINANCES.md` (costo de oportunidad Fernando: ~$2,850 USD invertidos sin facturar), `_QUE-PODEMOS-HACER.md`, specs del bot WA
- WA-cart-bot operacional (skill `wa-bot-operator` funcional)
- `vayla-dance-spec-kit` skill disponible para nuevos eventos
- Leveling venom: L3 (5.5/10) — producto fuerte (8.5), redes muerto (1.5), SEO medio (6.6)

**Lo que NO tiene:**
- Meta norte: ¿qué modelo de negocio? ¿socios con Flow Corp es el modelo definitivo?
- Revenue target: finanzas internas muestran modelo "% por evento" (~$9k MXN/evento neto) pero sin objetivo de eventos/año
- Redes: plataformas no definidas para DL como marca propia
- NEXT.md: no existe (confirmado por `ls angels/dance-leveling/` — no hay _NEXT.md)
- Plan de marketing propio: depende de Flow Corp para adquisición

**Dato real disponible:** ~95 horas Fernando invertidas sin facturar = ~$2,850 USD costo de oportunidad. Sin plan maestro que justifique o recupere esa inversión.

---

### Agencia Cero — Gaps críticos

**Lo que SÍ tiene:**
- `cero-agent/_NEXT.md`: registro exhaustivo de infra n8n (bots, workflows, confiabilidad)
- `angels/cc/_VENOM-REPOSITION-2026-06-01.md`: doc de reposicionamiento reciente
- `angels/coreo/CONTEXT.md`: algo de contexto (no leído completamente)
- Leveling venom: L4★ (6.6/10) — producto (7.8) + SEO (8.8) fuertes, redes (3.3) muerto — "zapatero sin zapatos"

**Lo que NO tiene:**
- Plan de crecimiento como marca: `cero-agent/_NEXT.md` es 100% infra, no hay ni una línea de estrategia de adquisición de clientes
- Meta norte: ¿cuántos clientes Agencia Cero directos? ¿A cuánto? ¿En qué plazo?
- Pipeline de ventas propio: Cero vende servicios pero no tiene pipeline documentado fuera de operaciones
- Contenido propio: 51 posts en `configs/cero-posts.json` pero sin publicar y sin plan editorial
- IG @cero.agencia: `social-growth-orchestrator` referenciado pero sin leveling de redes real

---

### Cargo Control — Gaps críticos

**Lo que SÍ tiene:**
- Código del producto en `/Documents/cargo-control/` (app funcional)
- Mencionado en contexto de angels como proyecto latente

**Lo que NO tiene:**
- Prácticamente todo: no hay angels/cargo-control, no hay `_NEXT.md`, no hay contexto en venom, no hay leveling, no hay plan maestro
- No aparece en el scoreboard de leveling-marcas.md (no está entre las 8 marcas calificadas)

**Veredicto:** proyecto más oscuro del ecosistema. Sin visibilidad de estado real.

---

## Propuestas de nombre de operación + meta norte

Para los proyectos sin plan, estas son sugerencias con data real del ecosistema:

| Proyecto | Nombre sugerido | Meta norte en 1 línea | Razón del nombre |
|---|---|---|---|
| Contreras Code | **Operación Arquitecto** | 3 clientes Growth ($15k setup + $5k/mes) = $15k MRR antes del 15-jul 2026 | "Agentic AI Architect" es el posicionamiento activo |
| Vayla | **Operación Tarima** | 8 eventos pagados en 2026 = $80k-160k MXN bruto | "Tarima" = lo que gestiona: escenarios de baile y competencia |
| Dance Leveling | **Operación Escenario** | Primer evento autónomo (Flow Corp mínimo 150 competidores) + $9k MXN neto Fernando | Diferencia Vayla (jueceo/sistema) de DL (el evento J&J en sí) |
| Agencia Cero | **Operación Cero a Cien** | 2 clientes Agencia Cero directos a $5k/mes = $10k MRR antes del 15-jul | Nombre pun sobre "cero clientes → 100 potencial" y el nombre CERØ |
| Cargo Control | **Pendiente discovery** | Desconocido — necesita 1 sesión de discovery antes de proponer meta | No hay suficiente data para proponer algo honesto |

---

## ¿Cuál proyecto es el SIGUIENTE prioritario en recibir su plan maestro?

**Veredicto con data:**

### Prioridad 1 — Contreras Code

**Por qué ahora:**
- Está a 0.1 de subir de L3 a L4 en leveling (5.9 → 6.0)
- Tiene 16 imágenes listos en `_LISTOS_METRICOOL/` sin publicar — contenido parado
- Tiene skills funcionales (cc-carousel, cc-post-image, proposal-pdf) sin plan que los dirija
- Fernando tiene posicionamiento claro (Agentic AI Architect) pero sin objetivo de revenue
- Es la única marca de servicios B2B directos de Fernando fuera de Studio Link — complemento natural del MRR
- El plan maestro de CC puede escribirse en 1-2h con data real que ya existe (catálogo, mejor post, leveling)

### Prioridad 2 — Vayla

**Por qué segundo:**
- Ya tiene el armazón comercial más completo de todos los que no tienen plan (4 deals activos, playbooks, pricing yaml)
- Solo le falta la capa de meta norte + scoreboard anual — lo que tiene es un excelente pipeline sin techo
- Operación Tarima podría escribirse en 1h usando los deals activos como Fase 1

### Prioridad 3 — Agencia Cero

**Por qué tercero:**
- Es la marca "zapatero sin zapatos": vende lo que no practica en sí misma
- El leveling ya lo señala (redes 3.3, "IG enabled=false, FB 0 followers")
- Pero requiere más work que CC y Vayla porque el posicionamiento de CERØ está siendo revisado (`_VENOM-REPOSITION-2026-06-01.md`)
- No tiene sentido un plan maestro si el modelo de negocio está siendo reposicionado

### Fuera de prioridad ahora — Dance Leveling y Cargo Control

- **DL:** el modelo socios con Flow Corp no está resuelto. Sin resolver eso, no hay plan que tenga sentido
- **Cargo Control:** cero visibilidad. Necesita discovery antes de planear

---

## Resumen ejecutivo — gaps del ecosistema

| Lo que funciona | Lo que falta |
|---|---|
| SL y VD tienen planes maestros completos con SSOT, scoreboard, fases y experimentos | CC, Vayla, DL, Cero y Cargo sin plan — 5 de 7 proyectos sin norte numérico |
| El leveling de venom califica 8 marcas con 3 ejes + evidencia | Redes es el cuello universal (promedio 3.2/10) — el problema no es el producto |
| angels/ tiene estructura comercial para SL, CC, Vayla, DL | El `_NEXT.md` de CC y DL es backlog de tareas, no estrategia de crecimiento |
| `venom_truth.json` y `data/` tienen métricas para SL y VD | CC, Vayla, DL, Cero sin sensor de redes en venom — no se puede medir lo que no se monitorea |
| Operación 20K tiene reglas anti-switching que resolvieron el problema de 19 planes en conflicto | CC tiene catálogo de servicios pero 0 número que perseguir — misma trampa que tuvo SL antes de Op20K |

---

## Formato a replicar (checklist para crear un plan maestro)

Basado en el estándar observado en los 2 planes existentes:

```
1. Nombre de operación + fecha inicio/deadline
2. Declaración SSOT: "esta es LA única fuente de verdad, si otro archivo contradice → gana este"
3. Verdad base: números reales verificados contra DB/API (no memoria, no estimados)
4. Meta única: UN número + deadline. Lo que NO cuenta (evitar mezclar one-time con MRR, etc.)
5. Scoreboard por canal: tabla métrica | requisito | hoy | gap
6. Estrategia en 3 inputs paralelos: qué maneja este plan vs qué es scope de Fernando
7. Fases con gates: condición para pasar de Fase 0 a 1, de 1 a 2
8. Kill rules: cuándo parar un experimento
9. Reglas anti-switching: explícitas, numeradas
10. LOG de cambios: tabla fecha | cambio (se edita aquí, no se crea doc nuevo)
11. Referencias cruzadas: cómo llega a este doc desde el repo de código, desde venom, desde memoria Claude
```

**Tiempo estimado para crear desde cero:** 2-4h con venom + Fernando revisando data real.
**Deuda acumulada sin plan:** decisiones ad-hoc, fragmentación de archivos, switching de estrategia al abrir el doc equivocado (el problema exacto que SL tenía con 19 planes compitiendo).
