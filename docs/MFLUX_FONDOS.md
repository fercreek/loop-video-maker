# MFLUX — Generación local de fondos bíblicos
> Tercer backend de imagen. Sin costo por imagen. Requiere ~8-9GB RAM (Q4).
> Última actualización: 2026-05-09

---

## Stack de generación — Jerarquía

| Backend | RAM | Costo | Cuándo usar |
|---------|-----|-------|-------------|
| Pillow local (STYLE_PRESETS) | ~50MB | $0 | Preview rápido, sin GPU |
| Gemini API | ~0 | ~$0.02/img | Fondos variados, conexión disponible |
| **mflux (FLUX Schnell)** | **8-9GB** | **$0** | Batch de fondos realistas, alta calidad |
| Ideogram API | ~0 | ~$0.08/img | Backup si Gemini falla |

---

## Setup mflux

Modelo ya descargado (33GB en caché HuggingFace).
venv con Python 3.12 en cero-content — puede reutilizarse o crear uno local.

```bash
# Opción A: usar venv de cero-content (ya tiene mflux instalado)
MFLUX_BIN="/Users/fernandocastaneda/Documents/cero/cero-content/scripts/venv312/bin/mflux-generate"

# Opción B: crear venv local
python3.12 -m venv .venv-mflux
source .venv-mflux/bin/activate
pip install mflux
```

---

## Comando base

```bash
$MFLUX_BIN \
  --model schnell \
  --quantize 4 \
  --steps 4 \
  --height 1920 --width 1080 \
  --output /path/to/fondo.png \
  --prompt "PROMPT_AQUI"
```

Flags clave:
- `--quantize 4` → 8-9GB RAM (suficiente para producción)
- `--steps 4` → schnell es rápido con 4 pasos
- `--height 1920 --width 1080` → vertical 9:16 para Shorts
- Para FB/IG cuadrado: `--height 1080 --width 1080`

---

## Prompts por STYLE_PRESET

Mapeo directo: cada preset existente tiene un prompt mflux optimizado.

| Preset key | Prompt mflux |
|------------|-------------|
| `amanecer_dorado` | `cinematic golden sunrise over mountains, warm amber rays, dramatic sky, biblical epic mood, 8K` |
| `cielo_nocturno` | `vast starfield night sky, milky way galaxy, deep space, dark blue and purple, photorealistic, cinematic` |
| `luz_divina` | `divine light rays breaking through clouds, golden celestial glow, heavenly atmosphere, dramatic backlight` |
| `piedra_antigua` | `ancient stone wall texture, old testament temple, rough hewn rock, warm brown tones, historical` |
| `agua_viva` | `calm ocean water at dawn, gentle waves, teal and deep blue, serene, cinematic wide angle` |
| `nube_celestial` | `soft white clouds in blue sky, peaceful heaven, light and airy, photorealistic` |
| `aurora_boreal` | `northern lights aurora borealis, green and purple sky, dark landscape below, magical atmosphere` |
| `desierto_sagrado` | `vast desert landscape at golden hour, sand dunes, biblical wilderness, warm sandy tones` |
| `gloria_eterna` | `crown of golden light in clouds, radiant glory, throne of heaven concept, epic cinematic` |
| `bosque_profundo` | `ancient forest with light beams through trees, green and emerald, peaceful and majestic` |
| `sangre_de_cristo` | `dramatic red sunset sky with dark clouds, crimson and deep red, powerful emotional mood` |
| `paz_clasica` | `calm lake at twilight, dark blue water, peaceful stillness, minimalist landscape` |

**Nota:** mflux no genera figuras humanas/Jesús de forma confiable. Usar para paisajes y fondos abstractos únicamente.

---

## Script de batch — generate_fondos_mflux.py

Ubicación sugerida: `scripts/generate_fondos_mflux.py`

```python
#!/usr/bin/env python3
"""
Genera banco de fondos con mflux para todos los presets.
Uso:
  python3 scripts/generate_fondos_mflux.py --count 3 --format 9:16
  python3 scripts/generate_fondos_mflux.py --preset cielo_nocturno --count 5
"""
import subprocess
import os
import argparse
from pathlib import Path

MFLUX_BIN = "/Users/fernandocastaneda/Documents/cero/cero-content/scripts/venv312/bin/mflux-generate"
OUTPUT_DIR = Path("output/fondos_mflux")

PROMPTS = {
    "amanecer_dorado": "cinematic golden sunrise over mountains, warm amber rays, dramatic sky, biblical epic mood, 8K",
    "cielo_nocturno": "vast starfield night sky, milky way galaxy, deep space, dark blue and purple, photorealistic, cinematic",
    "luz_divina": "divine light rays breaking through clouds, golden celestial glow, heavenly atmosphere, dramatic backlight",
    "piedra_antigua": "ancient stone wall texture, old testament temple, rough hewn rock, warm brown tones, historical",
    "agua_viva": "calm ocean water at dawn, gentle waves, teal and deep blue, serene, cinematic wide angle",
    "nube_celestial": "soft white clouds in blue sky, peaceful heaven, light and airy, photorealistic",
    "aurora_boreal": "northern lights aurora borealis, green and purple sky, dark landscape below, magical atmosphere",
    "desierto_sagrado": "vast desert landscape at golden hour, sand dunes, biblical wilderness, warm sandy tones",
    "gloria_eterna": "crown of golden light in clouds, radiant glory, throne of heaven concept, epic cinematic",
    "bosque_profundo": "ancient forest with light beams through trees, green and emerald, peaceful and majestic",
    "sangre_de_cristo": "dramatic red sunset sky with dark clouds, crimson and deep red, powerful emotional mood",
    "paz_clasica": "calm lake at twilight, dark blue water, peaceful stillness, minimalist landscape",
}

FORMATS = {
    "9:16": (1080, 1920),   # Shorts vertical
    "1:1": (1080, 1080),    # FB/IG cuadrado
    "16:9": (1920, 1080),   # Video largo horizontal
}

def generate(preset_key: str, count: int, fmt: str):
    w, h = FORMATS[fmt]
    prompt = PROMPTS[preset_key]
    out_dir = OUTPUT_DIR / preset_key
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{preset_key}] Generando {count} fondos {fmt}...")
    for i in range(count):
        out_path = out_dir / f"{preset_key}_{fmt.replace(':','x')}_{i+1:02d}.png"
        cmd = [
            MFLUX_BIN,
            "--model", "schnell",
            "--quantize", "4",
            "--steps", "4",
            "--height", str(h),
            "--width", str(w),
            "--output", str(out_path),
            "--prompt", prompt,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {out_path.name}")
        else:
            print(f"  ✗ Error: {result.stderr[:200]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default=None, help="Preset específico (default: todos)")
    parser.add_argument("--count", type=int, default=2, help="Imágenes por preset")
    parser.add_argument("--format", dest="fmt", default="9:16", choices=FORMATS.keys())
    args = parser.parse_args()

    presets = [args.preset] if args.preset else list(PROMPTS.keys())
    for p in presets:
        generate(p, args.count, args.fmt)

    print(f"\nDone. Fondos en: {OUTPUT_DIR}/")
```

---

## Uso desde image_gen.py (integración futura)

Si se quiere agregar mflux como backend en `generar_imagen()`:

```python
# En core/image_gen.py — agregar antes del fallback a _generar_gradiente
if os.path.exists(MFLUX_BIN) and use_mflux:
    try:
        return _generar_con_mflux(prompt, output_dir, preset_key, resolution)
    except Exception as e:
        print(f"mflux falló ({e}), usando preset local...")
```

---

## Banco de fondos — dónde guardar

```
output/
  fondos_mflux/
    amanecer_dorado/
      amanecer_dorado_9x16_01.png
      amanecer_dorado_9x16_02.png
    cielo_nocturno/
      cielo_nocturno_9x16_01.png
    ...
```

Los renders de video (`render_120min.py`, `render_short.py`) pueden consumir estos fondos directamente pasando el path en lugar de generar uno nuevo.

---

## Cuándo correr batch

- **Semanal, domingo noche** — genera 2-3 fondos por preset = ~30 fondos
- Cerrar Chrome + Notion antes de correr (liberar RAM)
- Duración estimada con Q4: ~45s setup + 12 presets × 2 imgs × 20s = ~9 min total
- Los fondos se reutilizan semanas — no necesita correr cada semana si el banco está lleno
