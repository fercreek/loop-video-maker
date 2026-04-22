# Troubleshooting

Problemas comunes y cómo resolverlos.

---

## Render falla / ffmpeg error

**Síntoma:** `RuntimeError: ffmpeg failed clip N: <stderr>`

**Diagnóstico:**
```bash
# Ver último log
cat logs/renders/$(ls -t logs/renders/ | head -1)

# Test ffmpeg manualmente
ffmpeg -version
python3 -c "from imageio_ffmpeg import get_ffmpeg_exe; print(get_ffmpeg_exe())"
```

**Causas frecuentes:**
- Disco lleno (ver abajo)
- Input image corrupta → revisar `output/fondos/*.jpg`
- Workers > CPU cores → bajar a `PARALLEL_JOBS = 4`

---

## Render muy lento (> 15min para 60min video)

**Baseline típico:** 3-4min para 60min video (M-series Mac, 6 workers, 12fps).

**Outliers conocidos:** `paz` 42min, `esperanza` 43min en v3.2 — causa no identificada. Si te pasa:

1. **Revisar thermal throttling:** laptop caliente → CPU baja frecuencia
   ```bash
   sudo powermetrics --samplers cpu_power -n 1 | grep "CPU die temp"
   ```
2. **Revisar contención I/O:** otro render en paralelo, backup corriendo, time machine
3. **Matar procesos zombie ffmpeg:**
   ```bash
   pkill -f ffmpeg
   ```
4. **Reducir workers temporalmente:**
   - Editar `render_60min.py:35` → `PARALLEL_JOBS = 3`

Si persiste, logs por-clip vendrán en v3.4 (ver VERSION.md roadmap).

---

## Disco lleno

Cada video 60min = ~1.5 GB. Batch completo (8 videos) = ~12 GB. Work dirs intermedios = +10 GB.

**Limpiar work dirs (seguros tras render exitoso):**
```bash
find output/youtube_60min -name "_work" -type d -exec rm -rf {} +
```

**Limpiar audio intermedio (WAV baked en MP4):**
```bash
find output/youtube_60min -name "audio" -type d -exec rm -rf {} +
```

**Archivar videos viejos:**
```bash
# Mover a disco externo
rsync -av --remove-source-files output/youtube_60min/ /Volumes/Backup/fe-en-accion/
```

---

## Audio con silencios o bajo volumen

**Detectar automáticamente:**
```bash
.venv/bin/python3 eval_render.py output/youtube_60min/<tema>/<tema>_60min.mp4
```

Issues esperados en v3.3:
- `Loudness -18 a -20 LUFS` → OK pero subóptimo (target -16). Fix manual:
  ```bash
  ffmpeg -i input.mp4 -c:v copy -c:a aac -b:a 192k \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp4
  ```
- `Silencios > 2s` → bug en v3.2. Re-renderizar con v3.3:
  ```bash
  git checkout v3.3-audio-fix
  rm output/youtube_60min/<tema>/<tema>_60min.mp4
  .venv/bin/python3 render_60min.py
  ```

---

## Thumbnail no se genera

**Síntoma:** `[thumb] Warning: no se pudo generar thumbnail: <error>`

**Causas:**
- Fuente faltante: requiere `/System/Library/Fonts/Supplemental/Impact.ttf` (macOS). En Linux instalar Impact equivalente.
- Imagen base no existe: verificar `output/fondos/fondo_<tema>.jpg` según mapping en `core/thumbnail_gen.py:77-84`

**Regenerar manualmente:**
```bash
.venv/bin/python3 generate_thumbnails.py --themes paz fe
```

---

## Rollback a versión anterior

Si una mejora rompió algo:

```bash
# Ver versiones disponibles
git tag -l

# Checkout temporal (detached HEAD)
git checkout v3.2-baseline
# Trabajar, probar

# Volver a main
git checkout main

# Rollback DEFINITIVO (destructivo — pierdes commits nuevos)
git reset --hard v3.3-audio-fix
```

Siempre hay un tag estable para volver. Nunca rompe work in progress porque branches feature están separados.

---

## Tests fallan

```bash
.venv/bin/python3 -m pytest tests/ -v
```

Issues comunes:
- `ModuleNotFoundError` → faltó `pip install -r requirements.txt`
- `fixture 'xyz' not found` → revisar `tests/conftest.py`
- Tests de render tardan mucho → mark como `@pytest.mark.slow` y correr solo rápidos con `pytest -m "not slow"`

---

## Python version issues

Proyecto probado con Python 3.9.6. Si usas 3.11+:
- `moviepy==2.2.1` puede fallar → actualizar a `moviepy>=2.2.0`
- `numpy==2.0.2` compatible con 3.9-3.12

Si tienes múltiples pythons:
```bash
python3 --version  # verificar cuál es
python3.9 -m venv .venv
```

---

## Logs desaparecen

Los logs viven en:
- `logs/renders/YYYY-MM-DD_HH-MM_<tema>.md` — por render
- `logs/LEARNINGS.md` — tabla acumulada + lecciones
- `logs/files.log` — eventos de archivos
- `eval/` — reportes JSON de eval

No se auto-rotan. Si crecen mucho:
```bash
# Archivar logs > 30 días
find logs/renders -name "*.md" -mtime +30 -exec tar czf logs/archive_$(date +%Y%m).tar.gz {} +
find logs/renders -name "*.md" -mtime +30 -delete
```

---

## Cuando nada de esto ayuda

1. Revisa el log del render específico: `logs/renders/<fecha>_<tema>.md`
2. Busca en `logs/LEARNINGS.md` → sección "Lecciones por versión"
3. Corre eval: `.venv/bin/python3 eval_render.py <archivo>` — el JSON output tiene detalles crudos
4. Git reflog: `git reflog` → estado del repo en los últimos cambios
