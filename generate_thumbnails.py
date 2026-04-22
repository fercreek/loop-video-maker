"""
generate_thumbnails.py — Batch CLI: generate YouTube thumbnails for all themes.

Usage:
    .venv/bin/python3 generate_thumbnails.py
    .venv/bin/python3 generate_thumbnails.py --themes fe paz amor
    .venv/bin/python3 generate_thumbnails.py --out output/thumbnails/
    .venv/bin/python3 generate_thumbnails.py --all-variants   # genera A + B + C por tema

Each thumbnail: 1280×720 JPEG, oil painting bg + glow title + accent bar.

Templates disponibles (--all-variants genera los 3):
  A (default): left-aligned, arrow, glow — canal principal
  B: centered/radial vignette — sleep/meditación
  C: bottom-third, bold, badge — más agresivo en CTR
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.thumbnail_gen import (
    make_thumbnail,
    THEME_COPY,
    THEME_BG,
    THEME_ACCENT,
    generate_thumbnail_for_theme,
)

ALL_THEMES = list(THEME_COPY.keys())

# Override file suffix per theme (matches the trimmed video names)
FILE_SUFFIX: dict[str, str] = {
    "fe":        "fe_60min",
    "amor":      "amor_40min",
    "esperanza": "esperanza_40min",
    "fuerza":    "fuerza_40min",
    "gratitud":  "gratitud_40min",
    "paz":       "paz_20min",
    "salmos":    "salmos_40min",
    "victoria":  "victoria_40min",
}


def main():
    p = argparse.ArgumentParser(description="Genera thumbnails YouTube para Fe en Acción.")
    p.add_argument("--themes", nargs="+", default=ALL_THEMES,
                   metavar="THEME", help="Temas a generar (default: todos)")
    p.add_argument("--out", default="output/thumbnails",
                   metavar="DIR", help="Directorio de salida (default: output/thumbnails)")
    p.add_argument("--all-variants", action="store_true", dest="all_variants",
                   help="Genera templates A + B + C por tema (para A/B CTR testing)")
    p.add_argument("--template", choices=["A", "B", "C"], default="A",
                   help="Template único a generar (default: A)")
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    n_variants = 3 if args.all_variants else 1
    print(f"\nGenerando {len(args.themes)} temas × {n_variants} variante(s) → {os.path.abspath(args.out)}/\n")

    total = 0
    for theme in args.themes:
        if args.all_variants:
            # Template A → canonical name; B/C → suffixed
            out_a = os.path.join(args.out, f"{theme}_thumb.jpg")
            make_thumbnail(theme=theme, output_path=out_a, template="A")
            out_b = os.path.join(args.out, f"{theme}_thumb_b.jpg")
            make_thumbnail(theme=theme, output_path=out_b, template="B")
            out_c = os.path.join(args.out, f"{theme}_thumb_c.jpg")
            make_thumbnail(theme=theme, output_path=out_c, template="C")
            print(f"  ✓ {theme}  →  A: {os.path.basename(out_a)}  B: {os.path.basename(out_b)}  C: {os.path.basename(out_c)}")
            total += 3
        else:
            suffix = FILE_SUFFIX.get(theme, f"{theme}_60min")
            t_suffix = "" if args.template == "A" else f"_{args.template.lower()}"
            out_path = os.path.join(args.out, f"{suffix}_thumb{t_suffix}.jpg")
            make_thumbnail(theme=theme, output_path=out_path, template=args.template)
            print(f"  ✓ {out_path}")
            total += 1

    print(f"\nListo. {total} thumbnails generados.")


if __name__ == "__main__":
    main()
