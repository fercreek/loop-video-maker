# Loop Video Maker

Genera videos de **60 minutos** para YouTube con versículos bíblicos, música instrumental relajante y pinturas al óleo como fondo. 100% local, sin servidor externo.

**Canal objetivo:** [@FeEnAcción](https://youtube.com/@FeEnAcción) — contenido devocional en español.

Versión actual: **`v3.3-audio-fix`** · Score calidad promedio: **88.6/100** (ver [VERSION.md](VERSION.md)).

---

## Quick start

```bash
# Setup
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Renderizar los 8 videos temáticos (60min c/u, ~28min total)
.venv/bin/python3 render_60min.py

# Evaluar calidad de los videos generados
.venv/bin/python3 eval_render.py output/youtube_60min/
```

Output: `output/youtube_60min/<tema>/<tema>_60min.mp4` + `<tema>_thumb.jpg`.

---

## Comandos principales

| Comando | Propósito |
|---|---|
| `.venv/bin/python3 render_60min.py` | Batch de 8 videos de 60min (todos los temas) |
| `.venv/bin/python3 generate_video.py --theme paz --duration 60` | 1 video custom (duración, FPS, workers configurables) |
| `.venv/bin/python3 generate_thumbnails.py` | Regenerar solo thumbnails |
| `.venv/bin/python3 eval_render.py <path>` | Auditar calidad (LUFS, silencios, bitrate, thumb) |
| `.venv/bin/python3 iterate.py` | Loop de mejora: render batch de 5 + análisis automático |

---

## Arquitectura

Pipeline ffmpeg-nativo: oil paintings + Ken Burns por verso, crossfade de 8s en audio multi-mood, texto en estilo Cormorant Garamond con glow, thumbnail auto-generado.

```
render_60min.py → core/verse_gen.py      (cargar JSON versículos)
                → core/music_gen.py      (playlist con crossfade)
                → core/video_render.py   (ffmpeg pipeline paralelo)
                → core/thumbnail_gen.py  (1280×720 JPEG post-render)
                → core/render_logger.py  (log + lecciones)
```

Detalles: [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md).

---

## Docs

| Doc | Para qué |
|---|---|
| [VERSION.md](VERSION.md) | Estado actual, tabla de versiones, config canónica, known issues |
| [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) | Arquitectura técnica completa |
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | Setup paso a paso + primer render |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Fallas comunes: ffmpeg, render lento, disco, rollback |
| [docs/ADD_THEME.md](docs/ADD_THEME.md) | Agregar un tema nuevo (JSON versículos + mood + thumbnail) |
| [logs/LEARNINGS.md](logs/LEARNINGS.md) | Lecciones acumuladas por versión + tabla histórica de renders |
| [iterations/README.md](iterations/README.md) | Loop de mejora gradual por batches de 5 videos |
| [output/youtube_60min/upload/README.md](output/youtube_60min/upload/README.md) | Copy listo para subir (títulos + descripciones + hashtags) |

---

## Versiones protegidas

```bash
git tag -l                              # ver tags
git checkout v3.3-audio-fix             # volver a última versión validada
git checkout v3.2-baseline              # baseline inmóvil
```

Cada versión validada queda con tag inmutable. Mejoras nuevas van en `feature/<nombre>` hasta pasar eval.

---

## Música usada

6 tracks [Kevin MacLeod](https://incompetech.com) (CC-BY 4.0) combinados en playlists de 3 moods por tema:

- Meditation Impromptu 02 → Paz profunda / Sanacion
- Enchanted Valley → Adoración
- Peaceful Desolation → Meditacion
- Healing → Devoción / Esperanza

Manifest: `audio/loops/manifest.json`.

---

## Stack

Python 3.9 · ffmpeg (imageio-ffmpeg bundled) · Pillow · NumPy · Gradio 4.36 (UI opcional) · SQLite (historial).

Tested en macOS M-series. Render 60min ≈ 3.4min con 6 workers paralelos.
