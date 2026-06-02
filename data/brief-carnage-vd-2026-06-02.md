# BRIEF CARNAGE — Operación de Dios · Lanzamiento Fase 1
> Emitido por: venom · Fecha: 2026-06-02
> Proyecto: @VersiculoDeDios / Página "Palabra De Dios" (FB 452922677899760)
> Aprobación Fernando requerida antes de ejecutar cualquier acción

---

## Contexto operativo (para carnage)

Estado hoy (ya ejecutado, NO re-hacer):
- 3 lofi 2h encolados en YouTube: Jun 11 (jdOSUMO3dbk) · Jun 12 (l5LFYLVZOd4) · Jun 13 (7cOYmo27qS4)
- Pinned comment Short r43LS0y0Wrg → sleep 6eHgRtGjaYA → activo
- 5 workflows cero-agent activos en n8n VPS (auto-publicador + comments FB/IG/YT + daily stats)
- FB Stars: activo pero $0 ganados (audiencia desconoce que existe)
- Fans FB: 1,933 (gate Reels Bonus: ya elegible — pending invite verification)

Restricción plataforma relevante: targeting religioso directo eliminado en Meta desde ene 2025.
Workaround validado: Lookalike 1% fans + copy secular ("música para dormir" no "oraciones").

---

## Acción 1 — Posts FB/IG el día de cada lofi (3 fechas)

- Qué: publicar exactamente el fb_post_copy y el ig_caption del lofi_push_plan.json el día que cada video se active en YouTube. Son 3 posts FB + 3 posts IG, uno por día en Jun 11, 12 y 13.
- Plataforma: Facebook Page + Instagram (ambas)
- IDs relevantes:
  - FB Page ID: `452922677899760`
  - IG Account ID: `17841469453382962`
- Assets (copy listo, NO modificar):
  - `data/lofi_push_plan.json` → campo `push_strategy.fb_post_copy` y `push_strategy.ig_caption` por video
  - Links YouTube reales ya en el JSON (`youtube_url`)
- Timing: el mismo día del publish (Jun 11, 12, 13) — no antes, no después
- Prioridad: Alta
- Impacto esperado: distribución orgánica del lofi en el momento de mayor impulso del algoritmo. Si el patrón reflexion-hook FB funciona (200+ likes en posts anteriores), estos posts deberían generar engagement real el día del launch.

---

## Acción 2 — Test Meta Ads $50 · Lookalike 1% fans FB

- Qué: crear campaña Meta Ads con objetivo "Page Likes" o "Reach" (NO conversión) usando audiencia Lookalike 1% basada en los 1,933 fans actuales de la página Palabra De Dios. Budget total $50 USD. Duración: 7 días.
- Plataforma: Meta Ads (Facebook Ad Account vinculado a página 452922677899760)
- IDs relevantes:
  - FB Page: `452922677899760`
  - Custom Audience base: fans actuales de la página (crear desde Meta Ads → Audiences → Custom Audience → Page Fans → luego Lookalike 1% México+LATAM)
- Copy del anuncio (copy secular, NO religioso para evitar "limited deliverability"):
  - Headline: "Música para dormir y relajar la mente"
  - Body: "2 horas de música tranquila y versículos de paz. Sin anuncios. Gratis en YouTube."
  - CTA: "Me gusta la página" o "Ver más"
  - Creative: thumbnail del lofi Jun 11 (jdOSUMO3dbk) — imagen cinematica, sin texto religioso explícito
- Targeting:
  - Audience: Lookalike 1% de fans de la página (no usar intereses religiosos directos)
  - Intereses indirectos permitidos si necesita ampliar: Marcos Witt, Hillsong, Marco Barrientos (música, no categoría religión)
  - Geo: México + Colombia + Argentina (LATAM español)
  - Age: 25-55
- Métricas a reportar de vuelta a venom:
  - CPF real (costo por fan nuevo)
  - Fans nuevos totales al día 7
  - CTR del anuncio
  - Impresiones / alcance
- Si CPF real ≤ $0.08 → escalar a $240-500 para completar los 8,067 fans que faltan para 10k (decisión de Fernando, no de carnage)
- Si CPF real > $0.08 → pausar y reportar — evaluar shoutout devocional como alternativa
- Prioridad: Media (después de los posts Acción 1)
- Impacto esperado: +600–1,000 fans nuevos, validar CPF real del nicho religioso LATAM (dato que hoy no existe — sin él no se puede decidir si escalar o no)

---

## Acción 3 — Stars FB · Pinned post educativo en la página

- Qué: publicar 1 post en Facebook Page "Palabra De Dios" explicando qué son las Stars de Facebook y cómo usarlas. Objetivo: activar revenue que está habilitado pero en $0 porque la audiencia no sabe que existe.
- Plataforma: Facebook Page únicamente (452922677899760)
- IDs relevantes:
  - FB Page ID: `452922677899760`
- Copy sugerido (carnage puede ajustar tono pero mantener estructura):

```
¿Sabías que puedes apoyar este canal con una Estrella? ⭐

Facebook tiene una función que se llama "Stars" — son una forma de enviar un pequeño apoyo a los creadores que te dan contenido de valor.

Cada ⭐ que mandas equivale a $0.01 USD y llega directamente a este ministerio.

Si alguno de nuestros versículos, oraciones o videos de paz te ha ayudado, considera mandarnos una Estrella la próxima vez que los veas 🙏

Puedes hacerlo dando clic en el ícono ⭐ que aparece en cualquier video o Reel.

Que Dios te bendiga por leer esto.
```

- Acción post-publicación: pinear este post en la página (opciones → fijar post → aparece primero en el perfil)
- Prioridad: Alta (costo $0, activa revenue inmediata con audiencia existente)
- Impacto esperado: Stars recibidas > 0 en los primeros 7 días. Ingreso modesto pero señal de que la audiencia responde — valida si vale la pena amplificar.

---

## Criterios de éxito (para cerrar loop con venom)

Carnage reporta de vuelta estos datos después de ejecutar:

| Acción | Métrica clave | Umbral éxito |
|--------|--------------|-------------|
| Posts FB/IG lofi (Jun 11-13) | Likes + comentarios por post | >50 likes por post FB (señal de engagement real) |
| Meta Ads test | CPF real (USD) | ≤$0.08 = escalar · >$0.08 = pausar y evaluar shoutout |
| Meta Ads test | Fans nuevos al día 7 | >300 fans nuevos |
| Stars pinned post | Stars recibidas semana 1 | >0 Stars = audiencia receptiva |
| Stars pinned post | Alcance del post (organic reach) | Reportar número raw |

---

## Orden de ejecución recomendado

1. **Hoy (2026-06-02):** Acción 3 — Stars pinned post (5 min, $0, revenue activada antes de que los lofi lleguen)
2. **Esta semana:** Acción 2 — Meta Ads test $50 (lanzar cuanto antes para tener 7 días de data antes del Jun 11)
3. **Jun 11, 12, 13:** Acción 1 — Posts lofi automáticos (cero-agent puede encargarse si carnage programa los posts en advance)

---

## Lo que este brief NO incluye (pendiente decisión Fernando)

- Ko-fi membresía (E6): requiere setup manual por Fernando — no es acción Meta
- Super Thanks YT (E9): requiere activación en YouTube Studio — no es acción Meta
- Shoutout canal devocional LATAM $50 (E5): requiere encontrar canal primero — investigación separada
- Fix MusicGen → Suno (E10): bloquea distribución Spotify pero no bloquea Acción 1-3 arriba

---

## Fuentes de verdad que carnage debe leer antes de ejecutar

- Copy exacto de posts: `/Users/fernandocastaneda/Documents/loop-video-maker/data/lofi_push_plan.json`
- Plan maestro completo: `/Users/fernandocastaneda/Documents/loop-video-maker/data/PLAN_MAESTRO_VD.md`
- Research ads (restricciones targeting): `/Users/fernandocastaneda/Documents/loop-video-maker/data/ads-strategy/SYNTHESIS.md`
