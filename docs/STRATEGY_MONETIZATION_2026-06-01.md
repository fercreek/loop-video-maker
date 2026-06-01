# 🎯 PLAN MAESTRO MONETIZACIÓN — @VersiculoDeDios

> ## ⚠️ ÚNICA FUENTE DE VERDAD DE MONETIZACIÓN DE VERSÍCULOS DE DIOS
> El equivalente de OPERACIÓN 20K (Studio Link), para el canal.
> Si otro archivo contradice esto → **gana este**. Stats vivos = `data/venom_truth.json`.
> **Owner:** Fernando · **Mantiene:** venom · **Update:** 2026-06-01
> Scope hoy: ANÁLISIS. Nada ejecutado/irreversible — ejecución requiere "sí" explícito por frente.

---

## 🥅 META NORTE

> **Tipo de MRR: VARIADO.** A diferencia de Op20K (MRR limpio de suscripción SaaS), aquí el ingreso
> recurrente se compone de varias fuentes: donaciones recurrentes + productos digitales + afiliados
> + ad-share de plataforma (YPP/Reels). Mismo denominador (MRR), distinto enfoque. Relacionada con
> Op20K, no alineada. Estándar: `venom/registry/operaciones-estandar.md`.

| | |
|---|---|
| **Objetivo** | Construir **MRR variado** encendiendo las fuentes recurrentes — empezando por las 2 llaves de plataforma: (1) YouTube YPP = 4,000h long-form/365d · (2) Facebook Reels Play Bonus |
| **Composición MRR** | ad-share (YPP + Reels) · donaciones recurrentes (Super Thanks/Ko-fi) · productos digitales · afiliados |
| **Hito de fase 1** | DESTRABAR las 2 llaves de plataforma (no un $ fijo aún — el ingreso de contenido es lento/variable) |
| **Hoy** | YPP **3.8%** (151.6h / 4,000h) · Reels Bonus = >1k fans ✅, falta verificar invite |
| **Horizonte** | YPP realista 6–12 meses · Reels Bonus = semanas (verificar invite ya) |
| **Ingreso paralelo (ya MRR)** | ~$100–500/mes (digital + donaciones + afiliados) — NO espera las 4,000h, es la 1ra capa de MRR variado |

**Anti-switching (como Op20K):** un solo plan, este. Cambio de estrategia = editar ESTE archivo,
no crear otro con fecha. Números solo de `venom_truth.json`. No reabrir docs stale.

---

## TL;DR (4 veredictos)

1. **Subir horas:** los 6×120min ya están programados (May31–Jun10). Lo único PARADO = 6 lofi 2h + 2 sleep_salmo91. Subir eso + replicar formato sleep = la palanca real. YPP es maratón, no sprint.
2. **Cross-promo loop→cero:** el cableado existe a medias. Falta 1 sync: `upload_schedule.json` → `VIDEO_MAP` del n8n. Esfuerzo bajo, alto retorno (cada video nuevo se auto-promociona en FB/IG).
3. **Negocio alterno:** 3 AHORA sin esperar las 4,000h → productos digitales (PDF/planner), donaciones (Super Thanks ya calificas), afiliados cristianos. ~$100-500/mes combinados.
4. **Ads pagados:** Google/YT = **NO** (watch pagado no cuenta YPP + pierdes ~90%). FB = **test-chico $300-500 MXN** solo para empujar Reels Play Bonus, nunca para el gate.

---

## 1. Subir watch hours long-form (la única palanca del gate YPP)

### Estado real (ground truth en disco + schedule, 2026-06-01)

**YA programados** (`data/upload_schedule.json`, todos `uploaded:true` + `publishAt`):

| Tema | youtube_id | Publica | Dur |
|------|-----------|---------|-----|
| Salmos | 6eHgRtGjaYA | 31 may 21:00 | 120min |
| Paz | aqFlPGDD2ww | 02 jun 21:00 | 120min |
| Esperanza | N7YzBNgd3l4 | 04 jun 21:00 | 120min |
| Sanación | 9ydXq8BlvWY | 06 jun 21:00 | 120min |
| Fe | wF356NTu_I0 | 08 jun 21:00 | 120min |
| Provisión | zSxs3wnTq9U | 10 jun 21:00 | 120min |

→ **12h de long-form nuevo entrando en 10 días.** Corrige el "anomalía: 30h parado" de venom_truth (contaba doble estos 120min).

**PARADO de verdad** (en disco, SIN entrada en ningún schedule):

| Archivo | Dur | Estado |
|---------|-----|--------|
| `output/lofi/lofi_v01_dormir_2h.mp4` | 120min | parado |
| `output/lofi/lofi_v02_orar_2h.mp4` | 120min | parado |
| `output/lofi/lofi_v02_verses_final.mp4` | 120min | parado |
| `output/lofi/lofi_v03_verses_final.mp4` | 120min | parado |
| `output/lofi/lofi_v03_ansiedad_2h.mp4` | 120min | parado |
| `output/sleep/sleep_salmo91_120min.mp4` | 120min | parado |
| `output/sleep/sleep_salmo91_60min.mp4` | 60min | parado (posible redundante con el 120) |

→ **~11h de long-form listo SIN SUBIR.** Acción inmediata: encolarlos en `upload_schedule.json` con `publishAt` escalonado tras Jun 10.

### Math al gate

- Hoy: 151.6h / 4,000h (3.8%). Faltan ~3,848h.
- Si cada sleep/lofi 2h promedia 200 views × ~50% retención = ~200h/video/año. 13 videos (6 ya prog + 7 parados) ≈ potencial 2,000-2,600h/año si la retención sleep (61-91%) se sostiene.
- **Realidad:** YPP toma 6-12 meses. La palanca no es producir más Shorts (no cuentan) — es subir el inventario sleep parado + sostener cadencia long-form.

### 3 palancas (de venom_truth, priorizadas)

1. **Subir lofi+sleep parados** — impacto alto, esfuerzo bajo (ya renderizado, escalonar publishAt).
2. **End-screen + pinned comment del top Short** (`r43LS0y0Wrg`, 324h/28d) → manda su tráfico a un sleep. Transfiere horas al contenido que SÍ cuenta YPP.
3. **Replicar formato sleep/devocional** (61-91% ret) en duración larga. Las stories de 20min retienen 12-16% — NO ayudan al gate.

---

## 2. Cross-promo loop-video-maker → cero-agent (qué videos promocionar)

### Cómo está hoy (ground truth)

- **Mecanismo:** `cero-agent/n8n-exports/auto-publicador.json` — nodos "FB Comentario" / "IG Comentario" postean a Graph API un primer comentario con el link de YouTube. El texto lo genera Claude Haiku.
- **Qué promociona:** nodo "Lookup Video YT" con un `VIDEO_MAP` **hardcoded a mano** (libro bíblico → URL YT). Cada video nuevo hay que agregarlo manualmente.
- **Señal cross-repo ya existente:** `loop-video-maker/data/upload_schedule.json` (story_id, youtube_id, publish_date, uploaded). Nadie la lee aún.

### Diseño del handoff (a implementar en otra ronda)

```
loop-video-maker/data/promote_queue.json   ← loop-maker escribe (qué videos viven y son promocionables)
        │
        ▼
cero-agent n8n "Lookup Video YT"  ← lee el JSON en vez del VIDEO_MAP hardcoded
        │
        ▼
FB/IG comment con link YT del video relevante al post del día
```

- **Esfuerzo:** bajo-medio. 1 nodo n8n que hace fetch del JSON + 1 script en loop-maker que regenera `promote_queue.json` desde `upload_schedule.json` (solo `uploaded:true` + ya públicos).
- **Qué promocionar primero:** los sleep/120min ya públicos con mejor retención (Salmos, Paz) — manda tráfico de FB/IG a long-form que llena el gate. Mata 2 pájaros: engagement FB + watch hours YT.

### Por qué se complementa (la tesis de Fernando)

Loop-maker produce y conoce la data de cada video (retención, tipo, gate). cero-agent tiene el canal de distribución (comentarios FB/IG con links). Hoy el puente es manual. Automatizarlo = cada long-form nuevo se auto-promociona en las 2 redes sin tocar nada.

---

## 3. Modelos de negocio alternos (ingresos PARALELOS al gate YPP)

### El dato que cambia el juego

YouTube bajó el gate a **500 subs + 3,000 watch hours/90d** para *fan-funding* (Super Thanks,
Membresías, Shopping). Con 14k subs **ya calificas para varios** — SIN esperar las 4,000h de ads.
([YouTube Help](https://support.google.com/youtube/answer/13429240))

### Los 8 modelos (req · esfuerzo · retorno/mes a 14k/1.9k · ejemplo)

| Modelo | Req | Esfuerzo | Retorno/mes real | Veredicto |
|--------|-----|----------|-------------------|-----------|
| **Productos digitales** (PDF devocional, planner oración, wallpapers versículos) | ~0 | Bajo | **$50–300** (margen ~100%) | ★★★★★ AHORA |
| **Donaciones** (Super Thanks + Ko-fi/PayPal) | 500 subs ✅ | 1h | **$5–50** (te quedas 70%) | ★★★★★ AHORA |
| **Afiliados cristianos** (biblias, libros, Logos) | ~0 | Bajo | **$20–150** | ★★★★ AHORA |
| **Comunidad de pago** (Patreon/Membresías) | ~200 fans | Medio | **$150–400** (conv 0.5-1%) | ★★★ pronto — necesita engagement |
| **Merch POD** (camisetas/tazas versículo) | marca | Medio | **$30–150** | ★★ probar 3-5 diseños |
| **Cursos / estudios pagados** | 5k+ engaged | Alto | $0–200 | ★ audiencia sleep es pasiva |
| **Licensing música/fondos** | 150+ tracks | — | — | ✗ BLOQUEADO (MusicGen=AI, Pond5/Epidemic prohíben IA) |
| **App / membresía propia** | 50k+ | Muy alto | negativo | ✗ necesita 5-10x escala |

### Recomendación — los 3 AHORA (suman ~$100-500/mes sin tocar el gate YPP)

1. **Productos digitales** (mayor ROI) — empaca las imágenes de versículos que YA generas + un
   planner de oración PDF en Etsy/Gumroad. Pipeline de generación ya existe (`gen_fb_pillow_v3.py`).
2. **Donaciones** — activa Super Thanks (ya calificas) + link Ko-fi/PayPal en cada descripción.
3. **Afiliados** — links a biblias/libros cristianos en descripciones de los sleep videos. Pasivo, escala con views.

⚠️ **Copyright:** merch + productos digitales solo con versículos de **dominio público** (Reina-Valera 1909).
NVI/NTV tienen copyright. Misma regla anti-strike que ya aplica al canal.

⚠️ **Licensing de música descartado:** la música es MusicGen (AI) y las stock libraries prohíben audio IA.

---

## 4. Veredicto ads pagados — Facebook vs Google

### El hallazgo que define todo

**El watch time de tráfico PAGADO no cuenta para las 4,000h de YPP.** Política oficial YouTube:
los views/watch hours de campañas de ads se descartan por completo para calificar a monetización.
→ Pagar Google/YouTube Ads para llenar el gate es **imposible por diseño**, no caro — YouTube
filtra esas horas a cero. ([ppc.land](https://ppc.land/youtube-clarifies-partner-program-eligibility-metrics-for-watch-hours/))

### Math (nicho religioso ES, ad account MXN)

| Métrica | Valor real | Fuente |
|---------|-----------|--------|
| CPV YouTube Ads LATAM | $0.010–0.030 USD/view | Store Growers |
| CPM Meta México | $0.96–3.92 USD | ADCostly / Lebesgue |
| Costo/like Meta LATAM (inspiracional) | ~$0.05–0.15 USD | uproas |
| RPM religioso ES (revenue) | $1.00–2.50 / 1,000 views | venom_truth |

**ROI YouTube Ads:** 1,000 views a CPV $0.02 = **$20 gasto** → generan ~$1–2.50 de RPM (y solo
si ya estás en YPP). Pérdida **~90% garantizada**. El contenido religioso ES nunca paga su CPV.

### Veredicto

- **Google / YouTube Ads → NO.** Doble pérdida: (a) las horas no cuentan para YPP (regla oficial),
  (b) aun ya monetizado pierdes ~90% (CPV $0.02 vs RPM $1–2.50/1k). No resuelve el gate ni se paga.
- **Facebook / Meta Ads → TEST-CHICO ($300–500 MXN máx).** NO sirve para YPP. SÍ puede servir para
  crecer fans baratos (~$0.05–0.15/like) hacia **Reels Play Bonus** (umbral por audiencia, ya >1k fans).
  Meta monetiza por umbral, no por watch-hours filtradas → ahí el tráfico pagado SÍ ayuda a cruzar.
  - **Métrica de corte:** si costo/fan > $0.20 o costo/ThruPlay alto en los primeros $300 MXN → apagar.
  - **NUNCA** ejecutar sin "sí" explícito (regla dinero/cloud).

**Casos reales:** no hay canal religioso ES que escalara a monetización vía ads con ROI positivo.
Consenso de creadores cristianos: el ingreso viene de cursos/sponsors/afiliados, no de ads.

**Conclusión:** para las 4,000h la única palanca sigue siendo orgánica — subir el long-form parado
+ funnel Shorts→long. Ads solo como experimento chico en Meta para Reels bonus.

---

## Próximas acciones (priorizadas — ninguna ejecutada aún)

1. **[bajo esfuerzo, alto impacto]** Encolar los 7 lofi/sleep parados en `upload_schedule.json` con publishAt escalonado tras Jun 10.
2. **[bajo-medio]** Cablear `promote_queue.json` → VIDEO_MAP n8n (cross-promo auto).
3. **[según veredicto §4]** Decidir ads sí/no/test.
4. **[según §3]** Activar 1-2 modelos de negocio alternos viables a 14k subs.
5. **[5 min, alto]** Verificar invite Reels Play Bonus en Professional Dashboard FB — es la llave #2 de la meta norte.

---

## Log de cambios (editar AQUÍ, no crear doc nuevo)

| Fecha | Cambio |
|-------|--------|
| 2026-06-01 | Creado. Consolida los 4 frentes (subir horas / cross-promo / negocio alterno / ads). Mata el "27%" stale del _NEXT viejo. Meta norte = destrabar las 2 monetizaciones (YPP + Reels Bonus). Elevado a plan maestro estilo OPERACIÓN 20K. |

---

## Referencias cruzadas

- **Stats vivos:** `data/venom_truth.json` (venom dueño)
- **Pickup operativo:** `_NEXT.md`
- **Plan hermano (Studio Link):** `apocalipsis/venom/campaigns/OPERACION-20K/README.md`
- **Learnings:** `venom/data/learnings/{ads-canal-religioso-es, modelos-negocio-canal-cristiano}.md`
