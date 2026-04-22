# Loop Video Maker — Learnings

Registro acumulativo de aprendizajes por iteración.
Después de cada render, revisar el log y mover las mejores lecciones aquí.

---

## Historial de renders

| Fecha | Tema | Engine | Render | Tamaño | Duración | Moods | Log |
|-------|------|--------|--------|--------|----------|-------|-----|
| 2026-04-14 | salmos | v3.2-d37b529 | 0.2min render | 26MB | 1min video | Paz profunda + Meditacion + Adoración | [log](renders/2026-04-14_14-31_salmos.md) |
| 2026-04-14 | paz | v3.2-470e901 | 0.2min render | 25MB | 1min video | Paz profunda + Meditacion + Sanacion | [log](renders/2026-04-14_14-35_paz.md) |
| 2026-04-14 | fuerza | v3.2-396a30f | 0.2min render | 25MB | 1min video | Paz profunda + Meditacion + Adoración | [log](renders/2026-04-14_18-14_fuerza.md) |
| 2026-04-14 | amor | v3.2-561c5d9 | 3.4min render | 1538MB | 60min video | Adoración + Paz profunda + Sanacion | [log](renders/2026-04-14_18-31_amor.md) |
| 2026-04-14 | gratitud | v3.2-561c5d9 | 3.4min render | 1537MB | 60min video | Meditacion + Adoración + Paz profunda | [log](renders/2026-04-14_18-38_gratitud.md) |
| 2026-04-14 | victoria | v3.2-9b42956 | 3.2min render | 1541MB | 60min video | Devoción + Adoración + Sanacion | [log](renders/2026-04-14_18-44_victoria.md) |
| 2026-04-14 | fuerza | v3.2-9b42956 | 3.5min render | 1537MB | 60min video | Sanacion + Devoción + Paz profunda | [log](renders/2026-04-14_18-51_fuerza.md) |
| 2026-04-14 | salmos | v3.2-9b42956 | 3.1min render | 1540MB | 60min video | Paz profunda + Adoración + Meditacion | [log](renders/2026-04-14_18-57_salmos.md) |
| 2026-04-14 | paz | v3.2-9b42956 | 42.5min render | 1536MB | 60min video | Paz profunda + Meditacion + Sanacion | [log](renders/2026-04-14_19-19_paz.md) |
| 2026-04-14 | esperanza | v3.2-9b42956 | 43.9min render | 1538MB | 60min video | Sanacion + Adoración + Meditacion | [log](renders/2026-04-14_21-31_esperanza.md) |
| 2026-04-15 | amor | v3.2-9b42956 | 3.7min render | 1539MB | 60min video | Adoración + Paz profunda + Sanacion | [log](renders/2026-04-15_03-37_amor.md) |
| 2026-04-21 | victoria | v3.2-2441361 | 4.3min render | 1543MB | 60min video | Devoción + Adoración + Sanacion | [log](renders/2026-04-21_12-58_victoria.md) |
| 2026-04-22 | paz | v3.2-06d4be4 | 3.3min render | 1539MB | 60min video | Paz profunda + Meditacion + Sanacion | [log](renders/2026-04-22_03-54_paz.md) |
| 2026-04-22 | fe | v3.2-06d4be4 | 4.1min render | 1542MB | 60min video | Adoración + Devoción + Paz profunda | [log](renders/2026-04-22_03-57_fe.md) |
| 2026-04-22 | esperanza | v3.2-06d4be4 | 3.4min render | 1540MB | 60min video | Sanacion + Adoración + Meditacion | [log](renders/2026-04-22_04-01_esperanza.md) |
| 2026-04-22 | amor | v3.2-06d4be4 | 3.6min render | 1537MB | 60min video | Adoración + Paz profunda + Sanacion | [log](renders/2026-04-22_04-05_amor.md) |
| 2026-04-22 | gratitud | v3.2-06d4be4 | 3.7min render | 1539MB | 60min video | Meditacion + Adoración + Paz profunda | [log](renders/2026-04-22_04-09_gratitud.md) |
| 2026-04-22 | fuerza | v3.2-06d4be4 | 3.7min render | 1541MB | 60min video | Sanacion + Devoción + Paz profunda | [log](renders/2026-04-22_04-12_fuerza.md) |
| 2026-04-22 | salmos | v3.2-06d4be4 | 4.3min render | 1537MB | 60min video | Paz profunda + Adoración + Meditacion | [log](renders/2026-04-22_04-16_salmos.md) |
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

### v3.x — Thumbnails YouTube (Sprint 3, 2026-04)

**Pipeline completo de thumbnail**
- `core/thumbnail_gen.py` — módulo reutilizable con `make_thumbnail(theme, output_path, ...)` y `generate_thumbnail_for_theme(theme, output_dir)`
- `generate_thumbnails.py` — CLI batch; también genera con `--themes fe paz`
- Integrado en `generate_video.py` y `render_60min.py` — se genera automáticamente después de cada render

**Diseño validado (Impact bold, 1280×720)**
- Fuente: Impact.ttf para título (130px), Arial Bold.ttf para subtítulo (42px) — ambas en macOS Supplemental
- Estructura: título 2 líneas (línea 1 acento, línea 2 blanca) + subtítulo + línea divisora + canal
- Color accent por tema: fe/fuerza/salmos/victoria=#FFD700, amor=#FF9F6B, esperanza/paz=#A8D8FF, gratitud=#B8F5A0
- Jerarquía visual lograda sin mockup: pinturas al óleo funcionan mejor que fondos genéricos

**Efectos que funcionan**
- Glow/halo: dibujar título en layer separado con alpha 180, GaussianBlur(r=22), composite antes del texto final
- Gradiente de overlay: curva cuadrática (t*t) en lugar de lineal — mantiene el lado izquierdo más oscuro y la transición más suave
- Barra vertical accent de 6px en el borde izquierdo — da cohesión con el template lateral_izq del video
- Flecha diagonal ↘: shaft + triángulo relleno, funciona mejor que flecha horizontal cuando no hay sujeto claro en el fondo

**Fondos óptimos por tema**
- fuerza → fondo_mountains.jpg (Albert Bierstadt): el más impresionante visualmente, paisaje épico
- salmos → fondo_celestial.jpg: dramático con rayos de luz, muy espiritual
- paz → fondo_cielo.jpg (Constable nubes): tranquilo y limpio, funciona con acento azul
- amor → fondo_sunset.jpg: cálido, complementa el acento naranja

---

## Ideas pendientes

- [ ] Probar 15fps para ver si mejora la fluidez perceptible
- [ ] Agregar fade de audio al inicio/fin del video
- [ ] Template de descripción YouTube con crédito Kevin MacLeod
- [ ] Considerar texto animado (fade in letra por letra) para engagement
- [ ] Re-renderizar temas con crossfade dip (esperanza, victoria, salmos, paz) para tener videos 60min limpios
- [ ] Thumbnails con foto de persona (Suno/Midjourney) para mayor CTR — pinturas al óleo son únicos pero foto puede generar más clicks
