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
| **Retención long-form** | — | **5.2%** (1 video, 23 views) | >40% sleep | semanal |
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

## 3.5 · Decision-tree de CONVERSIÓN (día 3-5, correr `check_flywheel.py`)

El cuello para L5 = conversión (=0 hoy). Esta tabla evita 3 días de diagnóstico a ciegas — al revisar, mapear el estado a la acción:

| Subs beehiiv | Apoyos Ko-fi | Views creciendo | Diagnóstico | Acción (<24h) |
|:--:|:--:|:--:|---|---|
| >0 | >0 | — | ✅ Flywheel CONVIERTE | Escalar: email semanal (WF#4) + más posts Ko-fi. → empuja L5. |
| >0 | 0 | — | Captura OK, monetización no | Revisar oferta Ko-fi (¿precio? ¿framing del apoyo?). Email nurture primero. |
| 0 | 0 | sí (↑ vs 23) | Discovery OK, **funnel roto** | Revisar fricción Ko-fi: ¿link visible? ¿PDF entrega? Test E2E manual del descargador. |
| 0 | 0 | no (~plano) | **Cuello = descubrimiento** | Track B ya en marcha (thumbs ✅ + EXP-001/002/003). Esperar señal 14d, no tocar más. |

> Regla: NO escalar producción ni CTAs hasta que esta tabla diga "CONVIERTE". Optimización prematura sobre funnel no-probado = desperdicio (veredicto workflow leveling 2026-06-05).

## 4. Decisiones ABIERTAS (no asumir — resolver con data)

### D1 · Daemon auto-upload long-form
- **Qué:** sumar `upload_to_youtube.py --yes` al daemon `yt-fb-uploader` (hoy solo sube Shorts).
- **A favor:** futuros encolados del schedule suben solos (sube private + publishAt, no público inmediato). Evita el scramble manual de hoy (salmo91).
- **En contra / riesgo:** auto-publish = sensibilidad de Fernando. Si el schedule tiene un video no-revisado, se sube solo. Persistencia automática.
- **Criterio para decidir:** activar SOLO cuando (a) haya ≥2 long-form encolados esperando, Y (b) exista gate de QA previo al encolado (ya existe: qa_longform ≥8). Mientras tanto = subida manual con `--yes`.
- **Estado:** ABIERTA. Default actual = manual. Decidir en sesión con cola real de long-form.

### D2 · Producir más sleep vs medir primero
- **Qué:** rendir salmo23/ansiedad/promesas/rosario.
- **DATA 2026-06-04 (YT Analytics):** único largo con data = `6eHgRtGjaYA` → **23 views, retención 5.2%, avg 6:17 de 120min**. Los otros 8 ≈0 data (recién publicados). El math "sleep 12× historias" asumía 30% ret; real = 5.2% → sleep rinde MUCHO menos de lo proyectado.
- **Verdicto: NO mass-producir sleep aún.** El cuello NO es cantidad de contenido — es **descubrimiento (23 views/5sem) + retención (5.2%) bajos**. Producir 4 sleep al 5% = poco watch-h.
- **Antes de producir, diagnosticar:** ¿por qué no retiene (intro larga? audio? loop obvio?) y por qué no se descubre (thumbnail CTR? título? 0 recomendación del algoritmo?). 
- **Caveat:** sample chico (1 video, 23 views). Re-medir cuando los otros 8 acumulen views (semanal §2).
- **Estado:** ABIERTA → inclinada a PAUSAR producción. salmo23 assets listos (no desperdiciados, esperan).

### D3 · Rotar BEEHIIV_API_KEY (quedó expuesto en chat)
- **Estado:** Fernando dijo NO rotar por ahora. Revisar si el canal es sensible. ABIERTA (low prio).

---

## 4.6 · DIAGNÓSTICO del cuello (2026-06-04, curva retención 6eHgRtGjaYA)

Curva audienceWatchRatio: **1%→100%, 5%→22%, 20%+→4.3% estable**.
- **El cuello tiene 2 capas:** (1) descubrimiento (23 views/5sem) + (2) **early-drop: 78% se va en los primeros ~6min**.
- La **cola 4.3%** que llega a 60min+ = audiencia real de sleep (sesiones largas, genera watch-h). Es el activo a proteger.
- **Hipótesis del drop:** intro/primeros minutos pierden gente (text card largo? arranque de música? mismatch thumbnail↔contenido). NO es solo descubrimiento.
- **Acción próxima sesión:** EXP-002 (intro corta / hook directo 30s) bien apuntado. Reducir el drop convierte samplers→durmientes = más watch-h sin más views. Diagnosticar QUÉ en los primeros 6min ahuyenta (ver el video, no solo la curva).

## 4.5 · Lab operable (capa de captura)

- **Ledger:** `data/experiments.jsonl` (1 línea/experimento: id, hipótesis, video_id, métrica, baseline, ventana, status, decisión, measurements[]).
- **Medición por-video:** `python3 scripts/measure_experiment.py <video_id> [--since YYYY-MM-DD] [--exp EXP-NNN]` → views/watch-h/retención/avg-view. Graba al ledger con `--exp`.
- **EXP-001/002 sembrados** (status: planned) — thumbnail A/B + título intención-búsqueda sobre `6eHgRtGjaYA` (atacan descubrimiento, cuello de D2).
- ⚠️ **Limitación:** impresiones + CTR NO disponibles vía Analytics API con scope actual → medir CTR MANUAL en YT Studio. Views/retención/watch SÍ son auto.
- **Loop ahora cerrado:** experimento (ledger) → medición (script) → log (measurements[] + §6) → decisión (§4). Falta solo el paso de PROMOCIÓN cross-proyecto (venom: hook ritual domingo — decisión de Fernando).

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
11. **La plantilla GANADORA suele YA existir en tus propios assets — copiar, no inventar.** Emergió 2× el 2026-06-05: (a) thumbnails — el batch lofi cozy/noche ya era el correcto, el batch salmos worship-clickbait era el malo; (b) bot replies — FB/IG ya eran pastoral, solo YT era robótico "amén". Antes de construir algo nuevo, buscar si el patrón bueno ya vive en otra parte del mismo proyecto y replicarlo. Hermana de verify-before-build.
10. **Thumbnail DEBE matchear el título + la intención.** Hallazgo 2026-06-05: 6 largos sleep tenían thumbnails de worship clickbait (¡PAZ!, ¡SANIDAD!, fondos día brillantes) contra título DORMIR → mismatch mata discovery+retención. La plantilla GANADORA (cozy/vela/noche del batch lofi) ya existía en el canal — el batch viejo usó la equivocada. Regla: thumbnail de sleep = noche/calma, "PARA DORMIR" visible, CERO clickbait. EXP-001 (6 thumbs realineados, running).
9. **MEDIR retención antes de producir.** Data 2026-06-04: sleep largo real retiene 5.2% (no 30% asumido) + 23 views/5sem. El cuello del gate NO es cantidad de contenido — es **descubrimiento + retención**. Más videos al 5% no acerca las 4,000h. Diagnosticar thumbnail/intro/algoritmo ANTES de rendir más. (mató el supuesto "produce más sleep").

---

## 6. Log de decisiones (fechado)

- **2026-06-04** — Flywheel construido + live E2E. Playlists binge actualizadas. salmo91 subido (fix chunked). Daemon long-form = decisión D1 ABIERTA (no asumida, a petición de Fernando). Triage historias → pivote a sleep (pauta #2).

---

## Refs
- `docs/FLYWHEEL_VDD_2026-06-04.md` · `docs/PLAN_MONETIZACION_ALTERNA_2026-06-04.md` · `data/PLAN_MAESTRO_VD.md`
- venom learning: `apocalipsis/venom/data/learnings/flywheel-monetizacion-vdd.md`

---

## 🕷️ Análisis venom 2026-06-09 — FB Reels Bonus (realidad) + veredicto Etsy frío

> Data LIVE Meta Graph API (page token `palabra-de-dios`, page 452922677899760). Probe de scopes: token es **Page Access Token**, no User token (`/me` devuelve la página). `/me/permissions` y `page/insights` agregado NO accesibles (esperado para page token). Trabajado con métricas **por-post / video_reels** que sí accede.

### (a) Qué impulsa el +42% de fans (2,722 → live 2,726)

NO es texto, NO es imágenes de versículo. **Es el formato Reel reflexión-hook (`added_video`).** Comparación cruda misma semana (rx = reacciones):

| Tipo | Ejemplo | Engagement |
|---|---|---|
| `mobile_status_update` (texto versículo) | "Hebreos 13:5", "1 Cor 13:4" | rx 1-7, cm 1-2, sh 0-1 |
| `added_video` Reel reflexión-hook | "Cuando Somos Débiles, El es Fuerte" | **rx 230, cm 25, sh 17** |
| `added_video` Reel reflexión-hook | "Deja Ir Para Ser Libre" | rx 69, cm 6, sh 2 |
| `added_video` Reel reflexión-hook | "Salvación. Perdón. Eternidad." | rx 94, cm 5, sh 7 |

Views nativos (`video_reels`) confirman tracción: top reels **4,650 / 4,626 / 2,757 / 2,036 views**. Los Reels de hook + duración 14-68s son el motor del growth. El texto/imagen NO mueve la aguja (engagement de un dígito).

**Hallazgo duro:** el +42% viene del **shift a Reels**, no de más posteo. La página dejó de depender de imágenes-versículo (Track 3) y empezó a subir Reels con título-hook. ESO escaló. Los Reels cortos (14-21s) outperforman a los largos (60-68s) en views (4.6k vs 2k) — formato corto gana alcance, formato largo gana engagement profundo (rx/cm).

### (b) Reels Play Bonus — ¿existe? → ❌ NO. Está MUERTO.

**Corrección de supuesto stale en CLAUDE.md** ("Reels bonus invite >1k ✅"):
- **Reels Play Bonus cerró GLOBAL el 31-ago-2025.** Ya no existe el invite-based bonus por views. En US estaba muerto desde 2024.
- Reemplazo real = **Facebook Content Monetization (FCM)** — programa unificado (consolidó Reels Play Bonus + In-Stream Ads + Performance Bonus en uno solo el 31-ago-2025). Monetiza Reels + video largo + foto + texto bajo un mismo paraguas.
- **México SÍ es elegible** para FCM / Performance Bonus (lista 2026: MX, US, CA, UK, ES, BR, CO, AR, CL, etc.). Pero es **invite-only** y el umbral práctico es **~5,000–10,000 followers** (la beta llegó a invitar páginas con 5k). Palabra De Dios tiene **2,726** → todavía abajo del piso realista.
- El "invite >1k fans" del doc es de la era Reels Play Bonus (extinto). Ya no aplica. **Borrar esa línea del CLAUDE.md.**

### (c) Spec de comportamiento FB para calificar a FCM

Meta paga FCM por **performance** (reach + engagement + views), no por densidad de ads. Para llegar al invite-threshold y maximizar payout cuando entre:

- **Frecuencia:** 1 Reel/día mínimo (ritmo humano, respeta guardrail anti-slop). NO subir texto-solo como contenido principal — no escala fans.
- **Formato ganador (replicar):** Reel vertical 9:16, **hook de título en los primeros 2s** (ej. "Cuando Somos Débiles, El es Fuerte"), duración **dos carriles**: 14-21s para ALCANCE (top views), 60-68s para ENGAGEMENT profundo. Alternar ambos.
- **Reusar de lo que ya rinde:** los Shorts devocionales-hook de YouTube (`output/shorts/`) son el mismo activo. 1 Short → publicar como Reel FB + Reel IG. El batch venom (fórmula `bi_B78HZuJ4`) es directamente reciclable.
- **Meta de growth:** de 2,726 → 5,000 fans para entrar al rango de invite beta. A ritmo +805/8d actual (≈100/día si se sostiene), eso es ~3 semanas SI mantiene el ritmo de Reels. El driver es Reels, no más texto.
- **Pista paralela:** página YA es `is_eligible_for_branded_content: true` → puede hacer contenido de marca/colab pagado aunque no esté en FCM aún.

### (d) Veredicto Etsy frío para VD → 🟡 SECUNDARIO, casi ❌

**Veredicto: NO es buen canal primario para VD. Esfuerzo mal invertido como apuesta principal.**

Data, sin wishful thinking:
- **Etsy es US-céntrico:** 53-57% del tráfico es US, **74% del GMS (ventas) es US**, browsing default en inglés. El comprador típico es mujer 25-44 US/anglo.
- **Audiencia de VD es LATAM hispana** que ya consume el contenido **gratis** (YT/FB/IG). Mismatch de geografía Y de idioma Y de disposición a pagar.
- **El embudo no conecta:** VD no manda tráfico a Etsy (audiencia en español no busca en Etsy.com en inglés). Sin tráfico propio, dependes 100% del SEO interno de Etsy, donde compites en inglés contra sellers US establecidos en el nicho "Christian wall art / printables".
- **Lo único defendible (por eso 🟡 y no ❌ seco):** productos digitales en inglés (versículo printables, wallpapers) tienen costo marginal cero y Etsy tiene 86.6M compradores + 40% ventas internacionales. PERO eso es construir una marca-producto NUEVA en inglés para audiencia US — NO es monetizar la audiencia que VD ya tiene. Es un negocio distinto disfrazado de extensión.

**Conclusión:** Etsy ≠ palanca de monetización de VD. Si Fernando quiere vender al fan LATAM existente → Hotmart/Gumroad/MercadoPago en español (devocionarios PDF, packs wallpaper) convierten mejor que Etsy. Etsy solo si se acepta arrancar marca-producto US-anglo desde cero, y eso compite por tiempo contra el gate real (4,000h YPP long-form). Mantener foco en el gate.

---

## 🌱 Análisis CRECIMIENTO ORGÁNICO — 2026-06-09 (venom, data live YT Analytics + Meta Graph)

> Foco: con la data que YA tenemos, ¿qué movemos para crecer orgánico (sin ads)?
> Toda cifra de aquí es de query LIVE hoy (no del JSON snapshot). Muros marcados explícitos.

### Data nueva jalada hoy (no estaba en venom_truth.json)

**YT — fuentes de tráfico 28d (channel):**
| Fuente | Views | Min vistos | Avg dur | Lectura |
|---|---|---|---|---|
| SHORTS | 132,861 | 56,408 | 65s | el 97% del volumen vive en el feed de Shorts |
| RELATED_VIDEO | 2,132 | 8,684 | **244s** | el tráfico que SÍ cruza a long-form; alto valor (4min avg) pero diminuto |
| YT_SEARCH | 2,098 | 792 | 57s | búsqueda orgánica viva pero corta |
| SUBSCRIBER | 559 | 2,482 | **282s** | el sub vuelve y ve 4.7min — la audiencia leal es de altísimo valor |
| PLAYLIST | 34 | 146 | **258s** | playlists casi sin uso pero retención altísima → palanca dormida |

**Funnel Shorts → long-form (LA fuga central):**
- Shorts generan **132,861 views/28d**. El cruce a long-form (RELATED_VIDEO) es **2,132 views = 1.6%** del volumen Shorts.
- El sleep 2h (6eHgRtGjaYA) recibió **62 related-video views** de los 132,861 de Shorts = **0.047%**. Prácticamente CERO trasvase.
- Si solo **1%** del tráfico Shorts cruzara a long-form = **+1,328 views/28d** en videos que SÍ cuentan YPP. Hoy se está perdiendo casi todo.

**YT — conversión de subs por video (subs ganados / 1k views, 28d):**
| Video | Tipo | Views | subs/1k | avgViewPct |
|---|---|---|---|---|
| zfQYgA88gcU "sangre de Jesús REVELA" | Short | 3,950 | **42.0** | 97.7% |
| gEHFYvu1SwI "Luz Eterna" | Short | 2,836 | 20.5 | 123.9% |
| RzGs_o-cyBk "Descanso en Fe" | Short | 1,272 | 17.3 | 91.7% |
| jvEokzazN4o "El dolor tiene propósito" | Short | 4,975 | 11.1 | 133.3% |
| MdenXXdtW60 "Este dolor INTENCIONAL" | Short | 8,512 | 3.6 | 87.1% |
| **r43LS0y0Wrg "NACISTE MUERTO" (motor)** | Short | 25,723 | **3.3** | 61.1% |
| HeGUMgQlfFo "Rut y Noemí" | Long | 660 | 3.0 | 25.4% |

> Hallazgo clave: el **motor de watch-time NO es el motor de subs**. `zfQYgA88gcU` convierte **12.9× mejor** subs/view que el motor `r43LS0y0Wrg`. El patrón conversor = Short de **"revelación/secreto"** con retención >97% (loop perfecto). El motor `r43LS0y0Wrg` tiene retención 61% (no loopea) → mucha view, poco sub. **Replicar el formato "revelación" para subs, no solo el formato "dolor".**

**YT — views por día de semana (28d):**
- Pico: Jue (23,970) · Lun (23,076) · Mié (22,236). Valle: Dom (15,983) · Sáb (17,304).
- Min vistos (proxy long-form/calidad): **Lun 17,433** domina por mucho. Lunes = mejor día para soltar long-form.

**FB — posts por engagement + hora (live, últimos 25):**
| Eng | Hora | Tipo | Texto |
|---|---|---|---|
| 732 | **17:01** | Reel video | "Setenta veces siete. No hay límite" |
| 309 | **15:31** | Reel video | "Cuando Somos Débiles, Él es Fuerte" |
| 186 | 16:01 | Reel video | "Sin cadenas / sin culpa" |
| 116 | 16:02 | Reel video | "Salvación. Perdón. Eternidad" |
| 92 | 15:31 | Reel video | "Deja Ir Para Ser Libre" |
| 4-19 | 11:00 | Reel (Short cross-post, caption hashtag-spam) | "PROVISIÓN DIVINA #...", "RESURRECCIÓN #..." |
| 1-9 | 00/07/21h | versículo-plano (mobile_status_update) | "Lucas 4:18", "1 Cor 13:4" |

> Hallazgos FB:
> 1. **Ganadores = Reels video reflexión-hook publicados 15:00–17:00.** Los 5 top posts caen TODOS en esa franja. Texto-plano y los Reels publicados a las 11:00 mueren.
> 2. **Los Short cross-posts (11:00) rinden 4-19 eng** mientras los Reels nativos reflexión-hook (15-17h) rinden 92-732. No es solo el formato: es **hora + caption**. Los cross-posts de Short llevan caption de hashtag-spam ("#Provisión #...") y van a mala hora → cross-post crudo NO funciona; hay que reempaquetar caption + hora.
> 3. Hora óptima FB confirmada por data: **15:30–17:00**.

**IG — muro parcial + hallazgo:** todos los posts IG recientes son **IMAGE versículo-plano con 0 likes**. IG NO está recibiendo Reels ni reflexión-hooks — solo el daemon de imágenes planas. Insights detallados bloqueados (falta scope `instagram_manage_insights`).

---

### 🎯 TABLERO DE PALANCAS ORGÁNICAS — priorizado por ROI

#### YouTube (gate YPP vivo — prioridad #1)

| # | Palanca | Esfuerzo | Impacto | Quick-win | Por qué (data) |
|---|---|---|---|---|---|
| Y1 | **End-screen + pinned comment** de los 2 top Shorts (r43LS0y0Wrg 132k+ feed, MdenXXdtW60) → sleep 2h + Rut y Noemí | Bajo | **Alto** | ✅ | Funnel Shorts→long hoy = 1.6%. Sleep 2h recibió 0.047% del tráfico Shorts. +1% cruce = +1,328 views/28d long-form |
| Y2 | **Playlists binge ordenadas por retención** (sleep 2h al inicio, encadenar long-form) | Bajo | **Alto** | ✅ | PLAYLIST trae solo 34 views PERO con avg 258s (4.3min). Es la fuente de mayor retención sin explotar. Encadenar = watch-time compuesto |
| Y3 | **Replicar formato "revelación/secreto"** (zfQYgA88gcU, 42 subs/1k) para Shorts, no solo "dolor" | Medio | Alto | ❌ | El motor de watch convierte 3.3 subs/1k; el "revelación" convierte 42 = 12.9×. Más subs = más SUBSCRIBER traffic (282s avg, el de mayor valor) |
| Y4 | **Soltar long-form en LUNES** (no fin de semana) | Bajo | Medio | ✅ | Lun = 17,433 min vistos (líder por mucho). Dom/Sáb son valle. Timing gratis |
| Y5 | **Replicar hook de "Rut y Noemí"** (ret 25%) en próximos long-form, retirar formato Noe/Moisés (12-16%) | Medio | Alto | ❌ | Rut retiene 2× mejor que Noe. El inventario long-form ya existe; el problema es hook/intro |
| Y6 | **Re-test thumbnail/intro Noe-Moisés** (12-16% ret) | Bajo | Medio | ❌ | Inventario long-form parado; CTR/intro es el cuello. Cuenta YPP si retiene |
| Y7 | A/B títulos cluster "dolor/propósito" (saturado, 4 videos mismo tema) | Medio | Bajo | ❌ | Riesgo de canibalización entre Shorts del mismo tema; diversificar tema |

> **Muro YT:** `impressions` / `impressionsCtr` / `subscribersGained × insightTrafficSourceType` NO disponibles vía esta API tier (requieren reportes Studio-only). El CTR de thumbnail solo se ve manual en YT Studio. Recomendación A/B de thumbnail (Y6) se valida ahí, no por API.

#### Facebook (camino a 5k fans → FCM invite — prioridad #2)

| # | Palanca | Esfuerzo | Impacto | Quick-win | Por qué (data) |
|---|---|---|---|---|---|
| F1 | **Mover todos los Reels a la franja 15:30–17:00** | Bajo | **Alto** | ✅ | Los 5 top posts (92-732 eng) caen TODOS en 15-17h. Reels a las 11:00 mueren (4-19). Solo cambiar la hora del schedule |
| F2 | **Matar/convertir el daemon de versículo-plano** (1-5 eng) a reflexión-hook | Bajo | Alto | ✅ | versículo-plano = 50× peor que reflexión-hook. Sigue subiendo automático y ensucia el feed (señal negativa al algoritmo) |
| F3 | **Reempaquetar caption de los Short cross-posts** (quitar hashtag-spam, agregar hook narrativo) | Bajo | Medio | ❌ | Cross-posts de Short rinden 4-19 vs Reels nativos 92-732. No es el video, es caption + hora |
| F4 | **2 Reels/día sostenibles** (uno 14-21s alcance + uno 60s engagement), ambos en franja tarde | Medio | Alto | ❌ | Ritmo actual mezcla calidad; el algoritmo premia consistencia de Reels reflexión-hook. Respeta guardrail 1-2/día |
| F5 | **Verificar invite Reels Play / FCM** en Professional Dashboard (fans +42%/8d, ahora 2,728) | Bajo | Alto | ✅ | No expuesto por API. 5min manual. El salto de fans pudo gatillar invite |

#### Instagram (1,200 — prioridad #3, casi parado)

| # | Palanca | Esfuerzo | Impacto | Quick-win | Por qué (data) |
|---|---|---|---|---|---|
| I1 | **Dejar de publicar SOLO imágenes planas** (0 likes consistente) → cruzar los mismos Reels de FB | Bajo | Medio | ❌ | Todos los posts IG recientes = IMAGE 0 likes. IG no recibe el formato ganador. Reusar Reel FB cuesta ~0 |
| I2 | NO invertir esfuerzo extra en IG más allá del cross-post | — | — | — | +11 fans/8d vs +805 FB. ROI marginal hoy. Data dice: mantener en cross-post, foco en YT+FB |

> **Veredicto IG (data, no opinión):** seguir en **baja prioridad**. El canal no responde (+11/8d) y solo recibe el formato muerto. Pero el cross-post de Reels FB→IG cuesta casi cero, así que vale conectarlo (I1) sin invertir tiempo de producción dedicado. NO empujar IG como canal propio hasta que YT (gate) y FB (5k fans) avancen.

---

### ⭐ TOP 3 QUICK-WINS (mayor impacto / menor esfuerzo)

1. **Y1 — End-screen + pinned comment de los 2 top Shorts → sleep 2h + Rut y Noemí.** El funnel hoy fuga 98% del tráfico. Conectar el motor de 132k views al long-form que cuenta YPP. Esfuerzo: 15 min en YT Studio.
2. **F1 — Reprogramar los Reels FB a 15:30–17:00.** Los 5 mejores posts ya están en esa franja; los flojos están a las 11:00. Solo cambiar la hora del schedule = subir el alcance de cada Reel sin producir nada nuevo.
3. **F2/Y-shared — Matar el daemon de versículo-plano (FB+IG) y reemplazar por reflexión-hook / Reel.** Formato plano = 50× peor en FB y 0 likes en IG; además ensucia el feed con señal negativa. Apagar daemon hoy.

> Estos 3 son ejecutables (handoff a carnage / Fernando manual). Y1+F1+F2 = cero producción nueva, solo redistribuir y reconectar lo que ya existe.

