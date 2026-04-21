# VERSION — Loop Video Maker

**Current:** `v3.3-audio-fix` (commit `e495ff1`, 2026-04-21) — victoria re-render 100/100
**Prev baseline:** `v3.2-baseline` (commit `9b42956`, 2026-04-15)

Tag inmovil. Checkout: `git checkout v3.2-baseline`. Revert work: `git reset --hard v3.2-baseline`.

---

## Estado: estable — lo que funciona

- 11 videos 60min renderizados sin fallos
- Video: oil paintings, Ken Burns aleatorio, 2 templates alternados verso a verso
- Audio: multi-mood playlist con crossfade 8s (fix dip en min 20/40 aplicado en este commit)
- Texto: Cormorant Garamond Italic, stroke 4-offset + alpha 240
- Thumbnails: auto-generados post-render (Impact 130px + glow + oil bg)
- Logs: por-render en `logs/renders/` + cumulativo `logs/LEARNINGS.md`

---

## Config canónica (60min)

| Parámetro | Valor | Dónde |
|---|---|---|
| Duración | 60 min | `render_60min.py:33` |
| Segundos/verso | 20 | `render_60min.py:32` |
| Verses totales | 180 (ciclados) | engine |
| FPS render | 12 | `render_60min.py:34` |
| Bitrate | 3500k (maxrate 4000k) | `core/video_render.py:713` |
| Preset x264 | ultrafast | `core/video_render.py:712` |
| Workers paralelos | 6 | `render_60min.py:35` |
| Crossfade audio | 8.0s | `render_60min.py:109` |
| Output típico | ~1.5 GB / 60min | — |
| Tiempo render | 3–4 min típico | logs |

**Templates visuales** (alternan verso a verso):
- A: `centrado_bajo` + `text_style=fea`
- B: `lateral_izq` + `text_style=fea`

**Moods audio disponibles:** `Paz profunda`, `Meditacion`, `Sanacion`, `Adoración`, `Devoción`, `Esperanza`

**Moods más relajantes** (sleep/meditation): `Paz profunda` + `Meditacion` + `Sanacion`

---

## Known issues abiertos

1. **Render lento ocasional** — `paz` tomó 42min, `esperanza` 43min vs 3-4min típico. Causa no identificada. Revisar si coincide con contención de I/O o thermal throttling.
2. **Re-render pendiente con v3.3** — videos renderizados con v3.2 (`amor`, `esperanza`, `fe`, `fuerza`, `gratitud`, `paz`, `salmos`) heredan silencio 16s final + dips mid. Solo `victoria` re-renderizado con v3.3.
3. **Thumbnails con foto** — pinturas al óleo funcionan pero pueden tener CTR bajo vs fotos de personas. Idea pendiente.

## Fixed en v3.3-audio-fix

- ✅ Silencio 16s al final (playlist math compensa N-1 crossfades)
- ✅ Silencios mid-video 4.5s (silenceremove sobre loops con fade embebido)
- ✅ victoria arranca mudo (mismo fix #2 trim head silence)
- ✅ Mood lookup tolerante a acentos (`Meditacion` == `Meditación`)

---

## Roadmap post-baseline

Branch `feature/120min`:
- Script `render_120min.py` con SECONDS_PER_VERSE=25 (288 versos)
- Moods solo relajantes para sleep-mode
- Evaluar subir bitrate 3500k→5000k + preset `medium`

Convención tags: `v3.3-<feature>` al validar. `main` solo recibe merges validados.

---

## Auto-evaluación

Script: `eval_render.py` (ver para detalles). Mide cada MP4:
- Duración, bitrate, fps (ffprobe)
- Loudness LUFS (ffmpeg ebur128)
- Silencios y crossfade dips (silencedetect + RMS)
- Thumbnail presente y dimensiones
- Errores en render log

Output: `eval/<video>.json` + fila en `LEARNINGS.md`. Score <80 = investigar.

Correr: `.venv/bin/python3 eval_render.py output/youtube_60min/`

---

## Cómo construir mejoras sin romper baseline

```bash
git checkout -b feature/<nombre>
# cambios
.venv/bin/python3 eval_render.py output/youtube_60min/<theme>/
# si score >= baseline:
git tag v3.3-<nombre>
git checkout main && git merge feature/<nombre>
```

Si mejora falla: `git checkout main` deja baseline intacto.
