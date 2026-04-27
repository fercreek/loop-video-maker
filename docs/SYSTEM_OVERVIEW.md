# System Overview — Loop Video Maker
**Version:** v3.7-quality-gate · Canal: @VersiculoDeDios

---

## ¿Qué hace este sistema?

Genera videos devotionales de larga duración (60min y 120min) para YouTube:
versículos bíblicos en español con pinturas al óleo animadas y música instrumental cristiana.
Totalmente automatizado desde datos hasta MP4 + thumbnail listos para subir.

---

## Arquitectura general

```
data/versiculos/<tema>.json
        │
        ▼
core/verse_gen.py          ← carga versos del tema, cicla hasta llenar duración
        │
        ├──► core/music_gen.py     ← genera playlist multi-mood con crossfade 8s
        │         (Kevin MacLeod CC-BY, audio/loops/*.mp3)
        │
        ├──► core/video_render.py  ← renderiza cada verso como clip ffmpeg
        │         (zoompan Ken Burns 12fps, 2 templates alternados, stroke Cormorant Garamond)
        │
        ▼
   MUXEO (ffmpeg)
   video clips + audio playlist → MP4 final + loudnorm -16 LUFS
        │
        ├──► core/thumbnail_gen.py  ← genera thumbnail 1280×720 JPEG (Impact + oil painting)
        │
        └──► core/quality_gate.py   ← eval score 0-100, auto-fix LUFS si fuera de rango
                  (llama eval_render.py internamente)
```

---

## Scripts de entrada (CLI)

| Script | Qué genera | Comando |
|--------|-----------|---------|
| `render_60min.py` | 8 × 60min devotional (todos los temas) | `.venv/bin/python3 render_60min.py` |
| `render_120min.py` | 8 × 120min sleep/relajación | `.venv/bin/python3 render_120min.py` |
| `generate_video.py` | 1 video custom (tema + duración) | `.venv/bin/python3 generate_video.py --theme paz --duration 60` |
| `generate_thumbnails.py` | Thumbnails batch (1 o 3 templates) | `.venv/bin/python3 generate_thumbnails.py --all-variants` |
| `eval_render.py` | Evalúa MP4s, score 0-100 | `.venv/bin/python3 eval_render.py output/youtube_60min/` |
| `iterate.py` | Loop de mejora: render 5 → eval → doc | `.venv/bin/python3 iterate.py` |

---

## Config central (`config.py`)

Fuente única de verdad. Todos los scripts importan desde aquí.

### Parámetros de render

| Parámetro | Valor | Significado |
|-----------|-------|-------------|
| `SECONDS_PER_VERSE` | 20 (60min) / 25 (120min) | Duración de cada clip |
| `RENDER_FPS` | 12 | 12fps es suficiente para Ken Burns lento |
| `PARALLEL_JOBS` | 6 | Subprocesos ffmpeg simultáneos |
| `VIDEO_BITRATE` | 3500k | YouTube reencoda, ultrafast preset OK |
| `CROSSFADE_SECONDS` | 8.0 | Transición suave entre tracks musicales |
| `QUALITY_GATE_THRESHOLD` | 80 | Score mínimo para pass |

### Temas activos (8)

| Tema | Moods audio | Label |
|------|------------|-------|
| paz | Paz profunda + Meditacion + Sanacion | Paz de Dios |
| fe | Adoración + Devoción + Paz profunda | Fe que mueve montañas |
| esperanza | Sanacion + Adoración + Meditacion | Esperanza en Dios |
| amor | Adoración + Paz profunda + Sanacion | El Amor de Dios |
| gratitud | Meditacion + Adoración + Paz profunda | Gratitud a Dios |
| victoria | Devoción + Adoración + Sanacion | Victoria en Cristo |
| fuerza | Sanacion + Devoción + Paz profunda | Fuerza en Dios |
| salmos | Paz profunda + Adoración + Meditacion | Salmos — Adoración |

---

## Módulos core (`core/`)

### `verse_gen.py`
- Carga `data/versiculos/<tema>.json`
- `versiculos_a_lista()` → lista plana de strings
- Engine cicla la lista hasta llenar `target_count` versos

**Datos actuales:** 10 temas JSON, ~26–80 versos únicos por tema, ciclados para llenar 60/120min.

### `music_gen.py`
- Lee `audio/loops/manifest.json` → mapeo mood → archivo MP3
- `generate_playlist(moods, total_sec, crossfade_sec)` → lista de segmentos de audio
- Cada playlist tiene 3 moods × ~20–40min, crossfade 8s entre bloques
- **Tracks:** Kevin MacLeod CC-BY 4.0 (incompetech.com)

**Loops disponibles:**
| Mood | Archivo | Track |
|------|---------|-------|
| Paz profunda | paz_profunda.mp3 | Meditation Impromptu 02 |
| Adoración | adoracion.mp3 | Enchanted Valley |
| Meditación | meditacion.mp3 | Peaceful Desolation |
| Devoción | devocion.mp3 | Healing |
| Sanación | sanacion.mp3 | Meditation Impromptu 02 |
| Esperanza | esperanza.mp3 | Healing (alt) |

### `video_render.py`
- `renderizar_video_fast()` — motor principal ffmpeg
- Cada verso = clip: zoompan Ken Burns aleatorio + texto superpuesto
- Templates alternados verso a verso: `centrado_bajo` (A) y `lateral_izq` (B)
- Texto: Cormorant Garamond Italic, stroke 4-offset + alpha 240
- Auto-crop bordes blancos (`_autocrop_borders`, threshold=8)
- Clips paralelos con `ThreadPoolExecutor(max_workers=6)`
- Mux final: ffmpeg concat + loudnorm=I=-16:TP=-1.5:LRA=11

### `thumbnail_gen.py`
- `make_thumbnail(theme, output_path, title, subtitle, template)` — función principal
- 3 templates: A (left-aligned, devotional), B (centered/vignette, sleep), C (bottom-third, bold)
- Fuentes: Impact 130px (título) + Arial Bold 42px (subtítulo)
- Glow/halo: layer separado, GaussianBlur r=22, composite previo
- `THEME_COPY` — copy 60min por tema
- `COPY_120MIN` — copy 120min con ángulo dormir/descansar

### `quality_gate.py`
- `gate(path, nominal_min, auto_fix_lufs, fail_threshold)` → dict con pass/score/issues/fixed
- Llama `eval_render.evaluate_video()` internamente (no duplica lógica)
- Auto-fix LUFS: ffmpeg stream-copy video + loudnorm audio (~6min para 60min)
- `print_batch_report()` — tabla ASCII al final del batch

### `render_logger.py`
- Crea log por render en `logs/renders/YYYY-MM-DD_HH-MM_<tema>.md`
- `RenderLogger.end()` escribe duración, score, issues, estado
- Cumulativo en `logs/LEARNINGS.md`

---

## Datos de versículos (`data/versiculos/`)

JSON por tema. Estructura:
```json
{
  "tema": "paz",
  "versiculos": [
    { "texto": "...", "referencia": "Filipenses 4:7" },
    ...
  ]
}
```

10 archivos activos: amor, esperanza, fe, fuerza, gratitud, paz, provision, salmos, sanacion, victoria.
(provision y sanacion existen como datos pero no están en `THEME_MOODS` — no se renderizan en batch).

---

## Fondos (`output/fondos/`)

11 pinturas al óleo JPG. Cicladas por tema:

| Fondo | Tema asignado | Estilo |
|-------|-------------|--------|
| fondo_light.jpg | fe | Luminoso, divino |
| fondo_sunset.jpg | amor | Atardecer cálido |
| fondo_dawn.jpg | esperanza | Alba, amanecer |
| fondo_mountains.jpg | fuerza | Montañas épicas (Bierstadt) |
| fondo_valley.jpg | gratitud | Valle pastoral |
| fondo_cielo.jpg | paz | Nubes (Constable) |
| fondo_celestial.jpg | salmos | Rayos de luz dramáticos |
| fondo_pastoral.jpg | victoria | Pastoral clásico |
| fondo_forest.jpg | — | Bosque (sin tema fijo) |
| fondo_sea.jpg | — | Mar (sin tema fijo) |
| luz_divina.jpg | — | Luz divina (alternativa) |

---

## Outputs (`output/`)

```
output/
├── youtube_60min/<tema>/
│   ├── <tema>_60min.mp4      ← ~1.5 GB
│   ├── <tema>_thumb.jpg      ← 1280×720 Template A
│   └── audio/                ← playlist WAVs temporales
├── youtube_120min/<tema>/
│   ├── <tema>_120min.mp4     ← ~3.1 GB
│   └── <tema>_thumb.jpg      ← 1280×720 Template B
└── SUBIR/
    ├── pendiente/            ← symlinks a videos por subir
    └── subido/               ← symlinks a videos ya en canal
```

Todo `output/` está en `.gitignore`. Solo el código va a git.

---

## Pipeline de iteración (`iterate.py`)

Loop de mejora continua:
1. Lee último `iterations/iter_NN.md` para estado previo
2. Renderiza 5 temas en rotación
3. Eval automático (score + issues)
4. Agrupa issues por patrón
5. Genera `iterations/iter_NN_YYYY-MM-DD.md` con hipótesis root cause
6. Humano aplica fix → re-render 1 tema → valida mejora

---

## Calidad actual (v3.7)

| Formato | Videos | Score promedio | LUFS | Render/video |
|---------|--------|---------------|------|-------------|
| 60min | 8 | 100/100 | -15.9 | ~3.5 min |
| 120min | 8 | 100/100 | -15.9 | ~10.4 min |

---

## Créditos musicales

Kevin MacLeod (incompetech.com) · Licencia CC-BY 4.0.
Incluir en descripción de YouTube: "Música: Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0"
