"""
generate_thumbnails.py — Batch CLI: generate YouTube thumbnails for all themes.

Usage:
    .venv/bin/python3 generate_thumbnails.py
    .venv/bin/python3 generate_thumbnails.py --themes fe paz amor
    .venv/bin/python3 generate_thumbnails.py --out output/thumbnails/

Each thumbnail: 1280×720 JPEG, oil painting bg + glow title + accent bar.
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
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print(f"\nGenerando {len(args.themes)} thumbnails → {os.path.abspath(args.out)}/\n")

    for theme in args.themes:
        suffix = FILE_SUFFIX.get(theme, f"{theme}_60min")
        out_path = os.path.join(args.out, f"{suffix}_thumb.jpg")
        make_thumbnail(theme=theme, output_path=out_path)
        print(f"  ✓ {out_path}")

    print(f"\nListo. {len(args.themes)} thumbnails generados.")


if __name__ == "__main__":
    main()
