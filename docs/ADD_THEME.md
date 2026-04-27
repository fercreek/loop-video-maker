# Agregar un tema nuevo

Cómo agregar un tema nuevo al sistema (ej: "perdon", "familia", "protección").

---

## 1. Crear JSON de versículos

Archivo: `data/versiculos/<tema>.json`

**Schema mínimo:**
```json
{
  "tema": "perdon",
  "titulo_sugerido": "Versículos de Perdón — Música Cristiana para el Alma",
  "descripcion_youtube": "Versículos sobre el perdón de Dios...",
  "tags_youtube": ["perdón", "versículos bíblicos", "RVR1960"],
  "prompt_imagen": "Soft forgiving light, dove of peace, biblical, cinematic",
  "mood_mubert": "gentle forgiveness peace ambient",
  "color_acento": "#E8D5A3",
  "versiculos": [
    {
      "id": 1,
      "texto": "Sed bondadosos unos con otros, misericordiosos, perdonándoos unos a otros...",
      "referencia": "Efesios 4:32",
      "version": "RVR1960"
    },
    {
      "id": 2,
      "texto": "Si perdonáis a los hombres sus ofensas, os perdonará también a vosotros...",
      "referencia": "Mateo 6:14",
      "version": "RVR1960"
    }
  ]
}
```

**Tips:**
- Mínimo 40 versos únicos (se ciclan hasta 180 en render 60min)
- Ideal 50-100 versos para mayor variedad
- Usar RVR1960 (Reina Valera) para consistencia de estilo
- Generar con Claude API si te falta corpus: usar `core/verse_gen.py::generar_mas_versiculos()`

---

## 2. Agregar mood mapping

Editar `render_60min.py` o `iterate.py` según tu flujo:

```python
# render_60min.py: tupla (theme, moods, label)
VIDEOS = [
    # ... existentes
    ("perdon", ["Sanacion", "Paz profunda", "Meditacion"], "El Perdón de Dios"),
]

# iterate.py: dict THEME_MOODS
THEME_MOODS = {
    # ... existentes
    "perdon": ["Sanacion", "Paz profunda", "Meditacion"],
}
THEME_LABELS = {
    # ... existentes
    "perdon": "El Perdón de Dios",
}
```

**Moods disponibles:** `Paz profunda`, `Meditacion`, `Sanacion`, `Adoración`, `Devoción`, `Esperanza`.

Combinar 3 moods por tema para evitar monotonía en video de 60min.

---

## 3. Configurar thumbnail

Editar `core/thumbnail_gen.py:77-84` — mapping `THEME_BG`:

```python
THEME_BG = {
    # ... existentes
    "perdon": "output/fondos/fondo_dove.jpg",   # o el que uses
}
```

Y `core/thumbnail_gen.py:86-93` — mapping accent color `THEME_ACCENT`:

```python
THEME_ACCENT = {
    # ... existentes
    "perdon": "#FFE4A3",   # tono cálido para perdón
}
```

**Disponibles fondos** (oil paintings):
- `fondo_light.jpg` — luz suave
- `fondo_sunset.jpg` — atardecer cálido
- `fondo_dawn.jpg` — amanecer
- `fondo_mountains.jpg` — paisaje épico
- `fondo_valley.jpg` — valle
- `fondo_cielo.jpg` — nubes tranquilas
- `fondo_celestial.jpg` — rayos dramáticos
- `fondo_pastoral.jpg` — pastoral
- Más en `output/fondos/`

---

## 4. Agregar copy para YouTube

Editar `output/youtube_60min/upload/README.md`:

```markdown
## N. `perdon_60min.mp4` — 60 min

**Título:**
El Perdón de Dios — 60 Minutos de Versículos Bíblicos | Música Cristiana

**Descripción:**
60 minutos de versículos bíblicos sobre el perdón de Dios...

📖 Versículos sobre: perdón, misericordia, reconciliación
🎵 Música: sanación, paz profunda, meditación

"Sed bondadosos unos con otros, misericordiosos, perdonándoos unos a otros..." — Efesios 4:32

#PerdónDeDios #VersículosBíblicos #MúsicaCristiana #VersiculoDeDios
```

---

## 5. Probar

```bash
# Render del tema nuevo
.venv/bin/python3 generate_video.py --theme perdon --duration 5

# Evaluar
.venv/bin/python3 eval_render.py output/youtube_60min/perdon/perdon_5min.mp4

# Si score >= 80 → render producción
.venv/bin/python3 generate_video.py --theme perdon --duration 60
```

---

## 6. Commit

```bash
git add data/versiculos/perdon.json \
        render_60min.py iterate.py \
        core/thumbnail_gen.py \
        output/youtube_60min/upload/README.md
git commit -m "feat(theme): agregar tema perdon con 60 versos RVR1960"
```

---

## Checklist

- [ ] JSON versículos con schema correcto
- [ ] Mínimo 40 versos únicos
- [ ] Mood mapping en render_60min.py + iterate.py
- [ ] Thumbnail: bg + accent color
- [ ] Copy en upload/README.md
- [ ] Test render 5min → eval score >= 80
- [ ] Render producción 60min
- [ ] Commit
