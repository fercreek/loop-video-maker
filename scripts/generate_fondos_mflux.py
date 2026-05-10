#!/usr/bin/env python3
"""
Genera banco de fondos con mflux (FLUX Schnell local) para Versículos de Dios.

Uso:
  python3 scripts/generate_fondos_mflux.py --count 3 --format 9:16
  python3 scripts/generate_fondos_mflux.py --preset cielo_nocturno --count 5
  python3 scripts/generate_fondos_mflux.py --count 2 --format 1:1

Presets: amanecer_dorado, cielo_nocturno, luz_divina, piedra_antigua, agua_viva,
         nube_celestial, aurora_boreal, desierto_sagrado, gloria_eterna,
         bosque_profundo, sangre_de_cristo, paz_clasica

Requiere: ~9GB RAM libre. Cerrar Chrome y Notion antes de correr.
Output:   output/fondos_mflux/{preset}/
Doc:      docs/MFLUX_FONDOS.md
"""
import subprocess
import os
import argparse
from pathlib import Path

MFLUX_BIN = "/Users/fernandocastaneda/Documents/cero/cero-content/scripts/venv312/bin/mflux-generate"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "fondos_mflux"

PROMPTS = {
    "amanecer_dorado":  "cinematic golden sunrise over mountains, warm amber rays, dramatic sky, biblical epic mood, 8K",
    "cielo_nocturno":   "vast starfield night sky, milky way galaxy, deep space, dark blue and purple, photorealistic, cinematic",
    "luz_divina":       "divine light rays breaking through clouds, golden celestial glow, heavenly atmosphere, dramatic backlight",
    "piedra_antigua":   "ancient stone wall texture, old testament temple, rough hewn rock, warm brown tones, historical",
    "agua_viva":        "calm ocean water at dawn, gentle waves, teal and deep blue, serene, cinematic wide angle",
    "nube_celestial":   "soft white clouds in blue sky, peaceful heaven, light and airy, photorealistic",
    "aurora_boreal":    "northern lights aurora borealis, green and purple sky, dark landscape below, magical atmosphere",
    "desierto_sagrado": "vast desert landscape at golden hour, sand dunes, biblical wilderness, warm sandy tones",
    "gloria_eterna":    "crown of golden light in clouds, radiant glory, throne of heaven concept, epic cinematic",
    "bosque_profundo":  "ancient forest with light beams through trees, green and emerald, peaceful and majestic",
    "sangre_de_cristo": "dramatic red sunset sky with dark clouds, crimson and deep red, powerful emotional mood",
    "paz_clasica":      "calm lake at twilight, dark blue water, peaceful stillness, minimalist landscape",
}

FORMATS = {
    "9:16": (1080, 1920),
    "1:1":  (1080, 1080),
    "16:9": (1920, 1080),
}


def generate(preset_key: str, count: int, fmt: str):
    if preset_key not in PROMPTS:
        print(f"Preset '{preset_key}' no existe. Opciones: {', '.join(PROMPTS.keys())}")
        return

    w, h = FORMATS[fmt]
    prompt = PROMPTS[preset_key]
    out_dir = OUTPUT_DIR / preset_key
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{preset_key}] {count} fondos {fmt} ({w}x{h})...")
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
            print(f"  OK  {out_path.name}")
        else:
            print(f"  ERR {preset_key} img {i+1}: {result.stderr[:300]}")


if __name__ == "__main__":
    if not os.path.exists(MFLUX_BIN):
        print(f"ERROR: mflux no encontrado en {MFLUX_BIN}")
        print("Setup: ver docs/MFLUX_FONDOS.md")
        exit(1)

    parser = argparse.ArgumentParser(description="Genera fondos bíblicos con mflux")
    parser.add_argument("--preset", default=None,
                        help="Preset específico (default: todos los 12)")
    parser.add_argument("--count", type=int, default=2,
                        help="Imágenes por preset (default: 2)")
    parser.add_argument("--format", dest="fmt", default="9:16",
                        choices=list(FORMATS.keys()),
                        help="Formato de salida (default: 9:16 para Shorts)")
    args = parser.parse_args()

    presets = [args.preset] if args.preset else list(PROMPTS.keys())

    print(f"mflux batch — {len(presets)} preset(s), {args.count} img c/u, formato {args.fmt}")
    print(f"Output: {OUTPUT_DIR}/")
    print("Asegurate de haber cerrado Chrome y Notion (necesita ~9GB RAM)")

    for p in presets:
        generate(p, args.count, args.fmt)

    print(f"\nListo. Fondos en: {OUTPUT_DIR}/")
