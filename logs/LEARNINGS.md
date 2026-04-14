# Loop Video Maker — Learnings

Registro acumulativo de aprendizajes por iteración.
Después de cada render, revisar el log y mover las mejores lecciones aquí.

---

## Historial de renders

| Fecha | Tema | Engine | Render | Tamaño | Duración | Moods | Log |
|-------|------|--------|--------|--------|----------|-------|-----|
| 2026-04-14 | salmos | v3.2-d37b529 | 0.2min render | 26MB | 1min video | Paz profunda + Meditacion + Adoración | [log](renders/2026-04-14_14-31_salmos.md) |
<!-- renders-table-end -->

---

## Lecciones por versión

### v3.x — ffmpeg fast renderer (Sprint 3, 2026-04)

**Performance**
- MoviePy frame-by-frame = 3h por video de 60min. ffmpeg zoompan = 4min. Nunca volver a MoviePy para videos largos.
- `ThreadPoolExecutor(max_workers=6)` para clips en paralelo es seguro y efectivo en M-series Mac.
- 12fps es imperceptible para slow Ken Burns pans; reduce el frame count a la mitad.
- Config óptima 60min: 20s/verso × 180 versos, 12fps, 3500k bitrate → ~1.7GB, ~4min render.

**ffmpeg filter bugs**
- `fade=alpha=1` sobre text overlay DESPUÉS de zoompan → texto invisible (timestamp drift).
  Fix: aplicar fade al composite completo: `[bg][txt]overlay,fade=in,fade=out[out]`
- `format=rgba` funciona para overlay con fondo zoompan. `format=yuva420p` pierde el alpha.

**Borders / imágenes**
- `_autocrop_borders(threshold=8)`: std de columna border ≈ 0, columna contenido ≈ 10-100.
  Threshold 240 (error previo) hacía que nada se detectara como borde.
- Siempre usar `ImageOps.fit` (crop-to-fill) después de autocrop para evitar letterboxing.

**Audio**
- `generate_playlist()` con 3 moods + 8s crossfade elimina la monotonía de 60min con un solo loop.
- Tracks Kevin MacLeod CC-BY disponibles: paz_profunda, adoracion, meditacion, devocion, sanacion, esperanza.

**Texto**
- Stroke de referencia: offsets (-3,0),(3,0),(0,-3),(0,3) + alpha 240 mejora legibilidad en fondos claros.
- Fuente Cormorant Garamond Italic da el estilo devocional correcto.

---

## Ideas pendientes

- [ ] Descargar pinturas sin bordes de museo (versiones de alta resolución)
- [ ] Probar 15fps para ver si mejora la fluidez perceptible
- [ ] Agregar fade de audio al inicio/fin del video
- [ ] Template de descripción YouTube con crédito Kevin MacLeod
- [ ] Considerar texto animado (fade in letra por letra) para engagement
