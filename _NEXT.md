# _NEXT — Tareas pendientes

_Última actualización: 2026-04-28_

---

## 📺 Subida a YouTube — Estado

### Canal: @VersiculoDeDios | 120min batch completo programado

| Fecha | Video | Estado |
|---|---|---|
| Abr 28 | fe_120min | ✅ programado |
| Abr 29 | amor_120min | ✅ programado |
| Abr 30 | esperanza_120min | ✅ programado |
| May 1 | gratitud_120min | ✅ programado |
| May 2 | victoria_120min | ✅ programado |
| May 3 | salmos_120min | ✅ programado |
| May 4 | fuerza_120min | ✅ programado |
| May 5 | provision_120min | ✅ programado |
| May 6 | sanacion_120min | ✅ programado |
| May 7 | paz_120min | ✅ programado |

Copy completo en: `_UPLOAD.md`

---

## 🔴 v3.12 — Audio variety (BLOQUEO PRINCIPAL)

### Diagnóstico auditado Abr-28

| Problema | Impacto | Causa |
|---|---|---|
| `esperanza.mp3` == `devocion.mp3` | Audio idéntico en temas "fe" y "esperanza" | Mismo archivo, dos nombres |
| `paz_profunda.mp3` == `sanacion.mp3` | Audio idéntico en temas "paz" y "sanacion" | Mismo archivo, dos nombres |
| `quietud.mp3` (81s) loopea 14× en 20min | Detectable por ContentID / near-duplicate | Loop demasiado corto |
| `meditacion.mp3` (91s) loopea 13× | idem | idem |
| `gloria.mp3` (124s) loopea 9× | idem | idem |
| `silencio.mp3` (127s) loopea 9× | idem | idem |
| `jubilo.mp3` (150s) loopea 8× | idem | idem |

**Resumen:** De 29 loops, 5 son < 160s (críticos), 2 pares son archivos duplicados.
YouTube puede detectar repetición de patrón en audio aunque el video sea distinto.

### Plan v3.12 — 3 líneas de acción

#### A) Reemplazar duplicados + loops cortos (prioridad 1)
- Conseguir nuevas fuentes para: `esperanza`, `devocion`, `quietud`, `meditacion`, `gloria`, `silencio`, `jubilo`
- Fuentes sugeridas (CC0/CC-BY):
  - **Pixabay** — pixabay.com/music (filtrar por "worship", "ambient", "meditation")
  - **Free Music Archive** — freemusicarchive.org
  - **Musopen** — musopen.org (música clásica dominio público)
  - **ccMixter** — ccmixter.org
- Objetivo: loops ≥ 10min para segmentos de 20min → 0 repeticiones

#### B) Variantes por mood (prioridad 2)
Estructura propuesta en `audio/loops/`:
```
audio/loops/
  adoracion/
    adoracion_a.mp3   ← actual
    adoracion_b.mp3   ← nuevo
    adoracion_c.mp3   ← nuevo
  gloria/
    gloria_a.mp3
    gloria_b.mp3
```
`music_gen.py` selecciona variante aleatoria por render → mismo mood, audio diferente entre videos.

#### C) Per-theme audio locking (prioridad 3)
Configurar qué variante usa cada tema → reproducible y diferenciado:
```python
THEME_AUDIO_LOCK: dict[str, dict[str, str]] = {
    "fe":       {"Adoración": "adoracion_b", "Gloria": "gloria_a"},
    "amor":     {"Adoración": "adoracion_a", "Sanación": "sanacion_b"},
    ...
}
```

### Comando para testear audio de un tema (smoke test)
```bash
.venv/bin/python3 -c "
from core.music_gen import generate_playlist
generate_playlist(moods=['Adoración','Gloria'], total_seconds=300,
                  output_dir='/tmp/test_audio')
print('OK — escuchar /tmp/test_audio/')
"
```

---

## 🟡 Renders pendientes (victoria/fuerza/salmos/sanacion/provision)

Estos 5 videos están en YouTube como drafts con audio v3.10 (moods idénticos entre sí).
Ya tienen fecha programada (May 2–6). **Opciones:**

1. ✅ Dejarlos como están — ya tienen moods únicos por tema (THEME_MOODS_120), solo el audio source se repite
2. 🔁 Re-renderizar con v3.12 (nuevo audio) antes de May 2 — ideal si se consigue audio nuevo antes

Comando si se re-renderiza:
```bash
caffeinate -i .venv/bin/python3 render_120min.py \
  --themes victoria fuerza salmos sanacion provision \
  --force --skip-qgate
```

---

## 🟢 Backlog futuro

- [ ] Shorts automáticos — top 3 versículos como clips 60s
- [ ] 180min format — sleep/estudio, baja competencia
- [ ] Thumbnail v2 — foto de persona real (mayor CTR)
- [ ] v3.9 visual effects (god-ray, split-tone, audio swell) — plan en `.claude/plans/`
