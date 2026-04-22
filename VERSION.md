# VERSION — Loop Video Maker

**Current:** `v3.4-clean` (commit `963230a`, 2026-04-22) — config central + loudnorm fix + clip instrumentation
**Prev:** `v3.3.1-docs` (commit `422ddea`) — docs milestone
**Prev:** `v3.3-audio-fix` (commit `e495ff1`, 2026-04-21) — victoria re-render 100/100
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

| Parámetro | Valor | Dónde (desde v3.4) |
|---|---|---|
| Duración default | 60 min | `config.py:TARGET_MINUTES_DEFAULT` |
| Segundos/verso | 20 | `config.py:SECONDS_PER_VERSE` |
| Verses totales | 180 (ciclados) | engine |
| FPS render | 12 | `config.py:RENDER_FPS` |
| Bitrate | 3500k (maxrate 4000k) | `core/video_render.py:714` |
| Preset x264 | ultrafast | `config.py:X264_PRESET` |
| Workers paralelos | 6 | `config.py:PARALLEL_JOBS` |
| Crossfade audio | 8.0s | `config.py:CROSSFADE_SECONDS` |
| Loudnorm target | -16 LUFS / TP -1.5 / LRA 11 | `core/video_render.py` mux step |
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

## Fixed en v3.4-clean

- ✅ LUFS bajo (amor -19.8 / paz -20.5 en v3.3) — loudnorm=I=-16:TP=-1.5:LRA=11 en mux
- ✅ Config duplicado en 3 scripts — `config.py` central fuente única
- ✅ Outliers render 42min no instrumentados — per-clip timing + top-5 slowest + warning >30s
- ✅ Eval score penalizaba _5min sin thumb — regex `\d+min$` soporta cualquier duración
- ✅ Eval sin validar specs thumbnail — checks `thumbnail_size` (<2MB) y `thumbnail_resolution` (1280x720)

## Fixed en v3.3-audio-fix

- ✅ Silencio 16s al final (playlist math compensa N-1 crossfades)
- ✅ Silencios mid-video 4.5s (silenceremove sobre loops con fade embebido)
- ✅ victoria arranca mudo (mismo fix #2 trim head silence)
- ✅ Mood lookup tolerante a acentos (`Meditacion` == `Meditación`)

---

## Tabla de métricas por versión

Actualizar cada vez que se corre `eval_render.py` sobre batch nuevo o se crea tag nuevo.

| Versión | Fecha | Videos eval | Score avg | Render time 60min | Música | Estado |
|---|---|---|---|---|---|---|
| v3.2-baseline | 2026-04-15 | 14 | **77/100** | 3.4min (rango 3.1–43.9min) | Kevin MacLeod loops + synth fallback | 🟡 bugs audio |
| v3.3-audio-fix | 2026-04-21 | 1 (victoria) | **100/100** | 4.0min | Kevin MacLeod loops (head/tail trim) | ✅ validado |
| v3.3 (batch pending) | — | 0/7 | — | — | — | ⏳ re-render pendiente |

**Render time outliers v3.2:** `paz` 42.5min, `esperanza` 43.9min. Causa no identificada.

### Música usada (todos los videos 60min)

| Tema | Moods (orden) | Fuente |
|---|---|---|
| paz | Paz profunda + Meditacion + Sanacion | Meditation Impromptu 02 + Peaceful Desolation + Meditation Impromptu 02 |
| fe | Adoración + Devoción + Paz profunda | Enchanted Valley + Healing + Meditation Impromptu 02 |
| esperanza | Sanacion + Adoración + Meditacion | Meditation Impromptu 02 + Enchanted Valley + Peaceful Desolation |
| amor | Adoración + Paz profunda + Sanacion | Enchanted Valley + Meditation Impromptu 02 + Meditation Impromptu 02 |
| gratitud | Meditacion + Adoración + Paz profunda | Peaceful Desolation + Enchanted Valley + Meditation Impromptu 02 |
| victoria | Devoción + Adoración + Sanacion | Healing + Enchanted Valley + Meditation Impromptu 02 |
| fuerza | Sanacion + Devoción + Paz profunda | Meditation Impromptu 02 + Healing + Meditation Impromptu 02 |
| salmos | Paz profunda + Adoración + Meditacion | Meditation Impromptu 02 + Enchanted Valley + Peaceful Desolation |

**Composición playlist**: cada video = 3 segmentos × ~20min cada uno, crossfade 8s. Todos los tracks son Kevin MacLeod CC-BY 4.0 (incompetech.com). Manifest: [audio/loops/manifest.json](audio/loops/manifest.json).

**Loops bundled** (después de v3.3 fix — silencio head/tail removido):
- paz_profunda.mp3 — Meditation Impromptu 02 (249s)
- adoracion.mp3 — Enchanted Valley (190s)
- meditacion.mp3 — Peaceful Desolation (91s)
- devocion.mp3 — Healing (520s)
- esperanza.mp3 — Healing alt (520s)
- sanacion.mp3 — Meditation Impromptu 02 (249s)

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
