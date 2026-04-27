# Getting Started

Guía para correr tu primer render desde cero.

---

## 1. Setup

**Requisitos:**
- Python 3.9+ (probado con 3.9.6 en macOS M-series)
- ~20 GB espacio libre (1.5 GB por video × 8 temas + work dirs)

```bash
git clone <repo>
cd loop-video-maker

# Virtual env
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

**ffmpeg:** viene bundled con `imageio-ffmpeg` — no requiere instalación manual. Si quieres usar el ffmpeg del sistema (recomendado para performance):

```bash
brew install ffmpeg  # macOS
# Luego en tu shell:
export IMAGEIO_FFMPEG_EXE=$(which ffmpeg)
```

---

## 2. Primer render (1 video de prueba)

Usa `generate_video.py` para un render rápido con parámetros custom:

```bash
.venv/bin/python3 generate_video.py \
  --theme paz \
  --duration 5 \
  --fps 12 \
  --workers 4
```

- `--theme`: uno de `paz fe esperanza amor gratitud victoria fuerza salmos`
- `--duration`: minutos (5 para test rápido, 60 para producción)
- `--fps`: 12 funciona bien para Ken Burns lento
- `--workers`: procesos ffmpeg paralelos (6 típico en M-series)

Output:
```
output/youtube_60min/paz/
├── paz_5min.mp4         (~130 MB)
└── paz_thumb.jpg        (1280×720)
```

---

## 3. Batch completo de 8 temas (producción)

```bash
.venv/bin/python3 render_60min.py
```

Renderiza los 8 temas en serie. Tiempo esperado: **~28min** (3.4min/video × 8).

Cada video:
- 60min exactos (180 versos × 20s)
- Música multi-mood con crossfade
- 11 pinturas al óleo rotando por verso
- Ken Burns aleatorio
- Texto Cormorant Garamond con glow
- Thumbnail auto-generado

---

## 4. Evaluar calidad automática

Tras renderizar, correr eval:

```bash
.venv/bin/python3 eval_render.py output/youtube_60min/
```

Output: score 0-100 por video, con issues específicos. Target: >=80.

Métricas medidas:
- Duración (±5s vs target)
- Bitrate video (≥3000k)
- FPS real
- MB/min (18-32)
- Loudness audio (LUFS -16 ±3)
- Silencios (>2s = bug)
- Dips audio (>6dB = bug crossfade)
- Thumbnail presente

Reportes: `eval/<tema>_<fecha>.json` + `eval/summary.md`.

---

## 5. Loop de mejora

Para iterar mejoras en batches de 5:

```bash
.venv/bin/python3 iterate.py
```

Renderiza próximos 5 temas (rotación automática), evalúa, agrupa issues por patrón, sugiere root cause y genera `iterations/iter_NN_<fecha>.md` con análisis.

Ver [iterations/README.md](../iterations/README.md) para el workflow completo.

---

## 6. Subir a YouTube

La carpeta `output/youtube_60min/upload/` contiene:
- Videos listos
- `README.md` con **títulos, descripciones y hashtags** por video

Pasos:
1. Copiar título + descripción desde `upload/README.md`
2. Subir MP4 + thumbnail (`<tema>_thumb.jpg`)
3. Categoría: Música / Entretenimiento espiritual
4. Idioma: Español
5. Activar monetización
6. Agregar a playlist "Devocionales 60 Minutos — VersiculoDeDios"
7. Programar 1-2 días entre subidas

---

## Siguientes pasos

- Algo falla → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Agregar un tema nuevo → [ADD_THEME.md](ADD_THEME.md)
- Entender el pipeline → [../SYSTEM_DESIGN.md](../SYSTEM_DESIGN.md)
- Ver qué cambió entre versiones → [../VERSION.md](../VERSION.md)
