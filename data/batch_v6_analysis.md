# Análisis Batch v6 — Shorts @VersiculoDeDios
> Fecha generación: 2026-05-22 (1 día después del último video: trabajo_001, May 21)
> Autor: generado por Claude Code — métricas reales PENDIENTES (ver sección abajo)

---

## ⚠️ Pendiente de métricas reales

Fernando debe correr localmente después de que YouTube/Facebook procesen 24–48h:

```bash
# Pull métricas YouTube vía API
python3 scripts/content_tracker.py --pull-metrics

# Si content_tracker.py no existe aún:
python3 scripts/yt_stats.py

# Facebook Insights manual:
# Meta Business Suite → Página 452922677899760 → Insights → Contenido
# Filtrar: May 12–21 → Shorts/Reels → views, retención, comentarios, compartidos
```

> **Nota:** Los archivos `data/shorts_schedule.json`, `data/content_registry.json` y
> `data/oraciones_pool.json` no existen en el repo al momento de este análisis.
> Crearlos después del primer pull de métricas para mantener el historial de batches.

---

## Spec del batch_v6

| Campo | Valor |
|-------|-------|
| Total Shorts | 10 |
| Período | May 12–21 2026 |
| Plataformas | YouTube Shorts + Facebook Reels |
| Publicación | 5am MTY (UTC-6), 1 video/día |
| Voz | ElevenLabs ES-MX (Daniel/Antonio) |
| Música | YouTube Audio Library / Kevin MacLeod CC-BY / MusicGen local |
| Fondos | Únicos por Short (sin repetición entre los 10) |

### Quick wins aplicados en v6
- **Subtítulos:** 4 → 6 palabras por chunk (ritmo más lento, mayor legibilidad)
- **CTA:** 'Escribe AMÉN si esto te llegó al corazón' (vs 'Comparte' de batches anteriores)
- **Hook duration:** 2.2s → 3.5s (más tiempo para enganchar antes del scroll)
- **Fondos únicos:** cada Short tiene fondo distinto (sin reutilización dentro del batch)

### Videos publicados (orden estratégico)

| # | ID | Hook | Tema | Día pub |
|---|----|------|------|---------|
| 1 | tiempos_dificiles_001 | ¿Sientes que Dios te abandonó? | Crisis de fe | May 12 |
| 2 | dormir_001 | ¿No puedes dormir esta noche? | Descanso nocturno | May 13 |
| 3 | ansiedad_001 | ¿El miedo no te deja respirar? | Ansiedad/miedo | May 14 |
| 4 | milagro_001 | ¿Necesitas un milagro hoy? | Fe/milagro | May 15 |
| 5 | manana_001 | Empieza tu día con esta oración | Oración matutina | May 16 |
| 6 | soledad_001 | ¿Te sientes completamente solo? | Soledad | May 17 |
| 7 | hijos_001 | Esta oración es por tus hijos | Familia/intercesión | May 18 |
| 8 | corazon_001 | ¿Tienes el corazón roto? | Duelo/dolor | May 19 |
| 9 | tristeza_001 | ¿Estás triste sin saber por qué? | Tristeza/depresión | May 20 |
| 10 | trabajo_001 | ¿Necesitas un milagro en tu trabajo? | Trabajo/provisión | May 21 |

---

## Tabla de métricas — LLENAR después de content_tracker.py

| ID | Views YT | Ret% YT | Likes YT | Coment YT | Views FB | Ret% FB | Coment FB |
|----|----------|---------|----------|-----------|----------|---------|-----------|
| tiempos_dificiles_001 | — | — | — | — | — | — | — |
| dormir_001 | — | — | — | — | — | — | — |
| ansiedad_001 | — | — | — | — | — | — | — |
| milagro_001 | — | — | — | — | — | — | — |
| manana_001 | — | — | — | — | — | — | — |
| soledad_001 | — | — | — | — | — | — | — |
| hijos_001 | — | — | — | — | — | — | — |
| corazon_001 | — | — | — | — | — | — | — |
| tristeza_001 | — | — | — | — | — | — | — |
| trabajo_001 | — | — | — | — | — | — | — |
| **TOTAL/AVG** | — | — | — | — | — | — | — |

> Benchmark de referencia (batch anterior): Short "Tres Días de Espera" → 208.9% retención, 5.8K views

---

## Hipótesis a validar con métricas reales

### H1 — Tipo de hook
**¿Los hooks pregunta (¿...?) retienen más que hooks afirmación?**
- v6 usa 8 hooks pregunta + 2 afirmación (manana_001, hijos_001)
- Comparar retención promedio: hooks pregunta vs afirmación
- Umbral para confirmar: diferencia >10% retención

### H2 — Horario de publicación
**¿5am MTY es óptimo o debería moverse?**
- Audiencia hispanohablante en MX/US-Hispanic → pico matutino ~6-7am MTY
- Alternativa a probar en v7: 6am MTY
- Validar con: YouTube Analytics → Cuándo están tus espectadores

### H3 — Temas por engagement
**¿Dormir/ansiedad/milagro generan más engagement que soledad/tristeza?**
- Hipótesis: temas de necesidad inmediata (dormir, ansiedad) > temas difusos (tristeza sin causa)
- Ranking esperado por intención de búsqueda nocturna: dormir_001 > ansiedad_001

### H4 — Efectividad del CTA
**¿'Escribe AMÉN' generó más comentarios que 'Comparte'?**
- Validar: contar comentarios que contienen "amén", "amen", "AMÉN" en los 10 videos
- Señal fuerte si >30% de comentarios contienen la palabra

### H5 — Efecto día de la semana
**¿Los videos del lunes/martes (inicio de semana) arrancan mejor?**
- tiempos_dificiles_001 (lun May 12) y dormir_001 (mar May 13) son el indicador

---

## Top esperados (ranking por intención de búsqueda — antes de ver métricas)

1. **dormir_001** — búsqueda nocturna muy alta ("oración para dormir"), audiencia cautiva
2. **ansiedad_001** — alta intención, término de búsqueda trending en ES-LAT
3. **tiempos_dificiles_001** — hook más emocional, primer video del batch (boost de inicio)
4. **milagro_001** — alta intención ("oración de milagro") pero más competida
5. **hijos_001** — nicho específico pero audiencia muy leal (madres/padres)
6. **corazon_001** — alta resonancia emocional, buen potencial en FB
7. **manana_001** — uso devocional diario, repetición natural
8. **trabajo_001** — intención alta pero publicado último (menos días de tracción al día 1)
9. **tristeza_001** — tema valioso pero hook más vago que ansiedad_001
10. **soledad_001** — tema poderoso pero audiencia más difícil de retener

---

## Acciones post-análisis (completar cuando lleguen métricas)

- [ ] Identificar el Top 3 por retención → replicar estructura en v7
- [ ] Identificar el Bottom 3 → analizar hook, tema o timing como causa
- [ ] Contar comentarios "AMÉN" vs total → decidir si mantener CTA en v7
- [ ] Verificar hora de mayor visualización en YouTube Analytics → ajustar horario v7
- [ ] Comparar rendimiento YouTube vs Facebook → priorizar plataforma en v7

---

## Spec base batch_v7 (preliminar — refinar con métricas reales)

> Ver spec completo en `data/batch_v7_spec_draft.md`

**Mantener de v6:**
- Subtítulos 6 palabras por chunk
- Hook duration 3.5s
- CTA 'Escribe AMÉN si esto te llegó al corazón'
- Fondos únicos por Short
- 1 video/día, 10 días

**Cambios propuestos para v7:**
- Probar hooks en 2da persona directa: 'Dios tiene algo para ti hoy'
- Publicar a 6am MTY (probar pico matutino más tardío)
- Temas: sanación, prosperidad, gratitud, perdón, paz (distintos a los 10 de v6)
- 1 experimento nuevo: agregar slide final con versículo en texto grande (5s) antes del fade
