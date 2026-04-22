# output/

Carpeta de salida — videos renderizados, thumbnails, backgrounds.

## Estructura

```
output/
├── fondos/                       ← 11 pinturas al óleo (bg para videos + thumbs)
│   ├── fondo_cielo.jpg
│   ├── fondo_mountains.jpg
│   └── ...
│
├── youtube_60min/                ← producto principal: videos 60min
│   ├── <tema>/                   ← uno por tema (paz, fe, amor, ...)
│   │   ├── <tema>_60min.mp4     ← video final (~1.5 GB)
│   │   ├── <tema>_thumb.jpg     ← 1280×720 auto-generado
│   │   └── audio/                ← playlist WAV (auto-limpiado post-render)
│   │
│   ├── upload/
│   │   ├── README.md             ← ⭐ COPY LISTO: títulos + descripciones + hashtags
│   │   ├── <tema>_60min.mp4     ← copias de videos listos para subir
│   │   └── fixed/                ← videos v3.2 con trim manual (pre-v3.3 fix)
│   │
│   └── <tema>/_work/             ← intermedios ffmpeg (auto-cleaned tras render)
│
└── <otras salidas legacy>        ← renders viejos, pruebas
```

---

## Qué hay en cada subcarpeta

### `fondos/`
Pinturas al óleo usadas como fondos en videos Y thumbnails. 11 imágenes curadas, paisajes cinemáticos.

Uso:
- `render_60min.py` rota las 11 aleatoriamente, 1 por verso
- `thumbnail_gen.py` mappea tema → pintura específica (`core/thumbnail_gen.py:77`)

### `youtube_60min/<tema>/`
Producto listo para YouTube. Estructura post-render:
- `<tema>_60min.mp4` — 60min exactos, 12fps, 3500k bitrate, h264+aac
- `<tema>_thumb.jpg` — 1280×720, Impact bold + glow
- `audio/` — se auto-limpia tras render exitoso

### `youtube_60min/upload/`
Carpeta dedicada a subida. `README.md` **es el doc más importante para publicación** — contiene:
- Títulos optimizados por tema
- Descripciones largas con emojis
- Hashtags
- Versículo ancla

### `youtube_60min/upload/fixed/`
Videos de la era v3.2 que tenían bugs de audio. Fueron trimmeados/normalizados manualmente post-hoc. Ver `docs/TROUBLESHOOTING.md` sección "Audio con silencios".

### `_work/` (cualquier subcarpeta)
Intermedios ffmpeg: clips individuales por verso, text PNGs pre-renderizados. El RenderLogger los limpia automáticamente post-render exitoso. Si ves `_work/` con GB de contenido, es que un render falló — limpiar manual:

```bash
find output/youtube_60min -name "_work" -type d -exec rm -rf {} +
```

---

## Tamaños típicos

| Contenido | Tamaño |
|---|---|
| 1 video 60min | ~1.5 GB |
| 1 video 40min | ~1.0 GB |
| 1 video 20min | ~0.5 GB |
| 1 thumbnail | ~400 KB |
| Batch completo (8 temas) | ~12 GB |
| Work dir durante render | ~2-3 GB (auto-cleaned) |

Disco mínimo recomendado: **20 GB libres** para un batch completo.

---

## Gitignore

`output/` **no se commitea** (ver `.gitignore` raíz). Esto es intencional:
- Videos muy grandes para git
- Regenerables desde código + data/versiculos/

Excepciones (sí commiteadas):
- `output/README.md` (este archivo)
- `output/youtube_60min/upload/README.md` (copy YouTube)
- `output/fondos/*.jpg` (no, están también ignoradas — se regeneran o se descargan)

---

## Backup manual

Antes de limpiar work dirs o regenerar:

```bash
# Solo videos finales
rsync -av --include="*.mp4" --include="*_thumb.jpg" --include="*/" --exclude="*" \
  output/youtube_60min/ /Volumes/Backup/fe-en-accion/

# Copiar archivo de copy también (crítico)
cp output/youtube_60min/upload/README.md /Volumes/Backup/fe-en-accion/
```
