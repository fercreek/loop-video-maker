# Loop Video Maker — System Design

## 1. Objetivo

Herramienta de escritorio local que genera videos `.mp4` de versículos bíblicos
para YouTube. Corre 100% local (sin servidor externo), UI en navegador vía Gradio.

---

## 2. Estado del Proyecto

**Funcional y probado.** 19/19 tests pasan (pipeline + preview + render).

```
Python:          3.9.6 (system, macOS aarch64)
Gradio:          4.36.0  — UI en localhost:7860
MoviePy:         2.1.2   — render .mp4 con libx264
ffmpeg:          imageio-ffmpeg bundled v7.1 (aarch64), sin instalación manual
Pillow:          10.4.0  — texto en video, gradientes, presets
NumPy:           2.0.2   — síntesis de audio
SQLite:          stdlib  — historial local (data/history.db)
```

---

## 3. Arquitectura de Componentes

```
app.py (Gradio 4.36)
│
├── core/db.py          — SQLite: historial images/audio/videos
├── core/verse_gen.py   — Carga versículos desde JSONs locales (10 temas)
├── core/image_gen.py   — Genera fondo 1920×1080 (presets Pillow | Gemini API)
├── core/music_gen.py   — Síntesis ambient orquestal (piano + cuerdas + coro)
├── core/video_render.py — Renderiza MP4 final con MoviePy + Pillow
└── preview/
    └── preview_engine.py — HTML/JS/CSS preview inline (Ken Burns, audio /file=)
```

---

## 4. Flujo de Datos

```
1. Seleccionar tema
   → verse_gen.py → JSON local → tabla editable de versículos

2. Imagen de fondo
   → image_gen.py:
     a. Preset (12 gradientes Pillow, nombre único con timestamp)
     b. Gemini 2.0 Flash API (opcional, requiere API key)
     c. Subir imagen propia (.jpg/.png)
   → output/imagen_YYYYMMDD_HHMMSS.jpg (1920×1080)
   → db.record_image()

3. Música de fondo
   → music_gen.py:
     a. Ambient orquestal (NumPy, offline): piano + cuerdas + coro, acordes cada 8s
     b. Subir MP3/WAV propio
     c. MusicGen IA (experimental)
   → output/musica_YYYYMMDD_HHMMSS.wav (stereo, 44100 Hz)
   → db.record_audio()

4. Preview
   → preview_engine.py:
     - Recorta audio a ≤90s (wave stdlib) → musica_preview.wav
     - Sirve audio via URL Gradio /file= (no base64)
     - HTML autocontenido con:
         · Ken Burns CSS (@keyframes kenburns, activa con .playing)
         · tryPlayAudio() con promise + canplay event (respeta autoplay policy)
         · Badge "Vista previa · Baja calidad"
         · Botones Play/Pause/Prev/Next + velocidades

5. Render final
   → video_render.py:
     - bg_clip = ImageClip(imagen, duración total) → _apply_bg_effect()
         · "Zoom lento ↗": scale 1.0→1.06 con clip.transform()
         · "Zoom lento ↙": scale inverso
         · "Paneo suave →": translate X 6%
         · "Sin efecto": estático
     - Por cada versículo: Pillow genera RGBA con texto+sombra → ImageClip con fade
     - CompositeVideoClip(fondo + textos) + AudioFileClip(música)
     - write_videofile(codec=libx264, bitrate=8000k, preset=medium)
   → output/{nombre}.mp4
   → db.record_video()
```

---

## 5. Base de Datos (SQLite — data/history.db)

```sql
images  (id, path, style, prompt, theme, width, height, created_at)
audio   (id, path, mood, duration_sec, generator, created_at)
videos  (id, path, theme, duration_min, seconds_per_verse,
         image_id → images.id, audio_id → audio.id,
         efecto_imagen, verses_count, created_at)
```

API pública en `core/db.py`:
- `init_db(path)` — crea tablas si no existen
- `record_image / record_audio / record_video` → retornan `id`
- `get_images / get_audio / get_videos(limit)` → `list[dict]`
- `get_last_image_id / get_last_audio_id` — helpers para `app.py`

---

## 6. Estructura de Archivos

```
loop-video-maker/
├── app.py                   # UI Gradio — handlers, estado, tabs
├── core/
│   ├── db.py                # SQLite history
│   ├── verse_gen.py         # Carga versículos desde data/versiculos/
│   ├── image_gen.py         # Generación de imagen de fondo
│   ├── music_gen.py         # Síntesis ambient + MusicGen
│   └── video_render.py      # Render MP4 con MoviePy
├── preview/
│   └── preview_engine.py    # HTML/JS/CSS preview
├── data/
│   ├── versiculos/          # 10 JSONs (paz, fe, amor, ...)
│   └── history.db           # SQLite (gitignored)
├── output/                  # Videos e imágenes generadas (gitignored)
├── assets/
│   └── fonts/               # Fuentes para render de texto
├── tests/
│   ├── test_pipeline.py     # 11 tests de integración (sin servidor)
│   ├── test_preview_engine.py # 7 tests unitarios del preview
│   └── test_flow.py         # 6 tests Playwright (requiere app en :7860)
├── requirements.txt
├── pytest.ini
├── run.sh / run.bat
└── config_template.json     # Plantilla de config (sin secrets)
```

---

## 7. Configuración (config.json — gitignored)

```json
{
  "gemini_api_key": "",
  "output_dir": "output",
  "db_path": "data/history.db"
}
```

Sin `config.json` la app funciona en modo offline (presets + síntesis local).

---

## 8. Tests

```bash
# Tests rápidos (sin render de video) — ~2 min
.venv/bin/pytest tests/test_pipeline.py tests/test_preview_engine.py -v -m "not slow"

# Tests Playwright (requiere app corriendo en :7860)
.venv/bin/pytest tests/test_flow.py -v -m "not slow" --timeout=120

# Todo incluyendo render de 10 min
.venv/bin/pytest tests/ -v --timeout=900
```

| Suite | Tests | Cobertura |
|-------|-------|-----------|
| `test_pipeline.py` | 11 | DB, image gen, audio gen, preview engine, video render |
| `test_preview_engine.py` | 7 | HTML structure, audio URL, hasAudio flag |
| `test_flow.py` | 6 (+1 slow) | E2E Playwright contra UI real |

---

## 9. Decisiones de Diseño

| Decisión | Alternativa descartada | Razón |
|----------|----------------------|-------|
| Gradio 4.36.0 pin exacto | gradio>=4.44 | Bug huggingface_hub con Python 3.9 |
| Audio via `/file=` URL | base64 embed | WAV de 60 min = ~600MB de base64, el browser no lo carga |
| Trim audio a 90s para preview | Audio completo | Performance — preview es solo visual |
| NumPy síntesis offline | Solo APIs externas | Funciona sin internet ni API keys |
| Pillow text → ImageClip | TextClip de MoviePy | Más control tipográfico, sin ImageMagick |
| Nombres únicos con timestamp | Sobrescribir mismo archivo | Historial y galería de assets generados |
| SQLite stdlib | ORM externo | Sin dependencias extras, suficiente para uso local |

---

## 10. Limitaciones Conocidas

| Limitación | Impacto | Mitigación |
|-----------|---------|-----------|
| Render de 60 min tarda ~15-20 min | Alto | Barra de progreso Gradio, opción de 10 min para pruebas |
| Python 3.9 (sistema macOS) | Bajo | Todo el código es compatible 3.9–3.12 |
| Autoplay bloqueado en browser | Medio | `tryPlayAudio()` + evento `canplay` + hint visual al usuario |
| Gemini API requiere key | Bajo | 12 presets offline siempre disponibles |
