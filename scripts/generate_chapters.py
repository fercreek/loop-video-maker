"""
scripts/generate_chapters.py — Generate YouTube chapter timestamps for rendered videos.

Output: one text block per video, ready to paste into YouTube description.

Usage:
    .venv/bin/python3 scripts/generate_chapters.py               # all themes, 60min + 120min
    .venv/bin/python3 scripts/generate_chapters.py --format 60min --themes paz fe
    .venv/bin/python3 scripts/generate_chapters.py --out chapters.txt  # write to file

Chapter strategy:
  60min  (3 moods × 20min each):  3 chapters
  120min (6 moods × 20min each):  6 chapters
  Each mood transition = a new chapter.
  First chapter always at 0:00.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import THEME_MOODS, THEME_MOODS_120, THEME_LABELS, ALL_THEMES


# ─── Mood display names ───────────────────────────────────────────────────────
# Human-readable chapter label per mood key
MOOD_LABELS: dict[str, str] = {
    "Paz profunda":     "Paz y Meditación",
    "Reposo":           "Reposo en Dios",
    "Contemplación":    "Contemplación",
    "Adoración":        "Adoración",
    "Devoción":         "Devoción y Oración",
    "Gracia":           "Gracia Divina",
    "Amanecer":         "Amanecer de Fe",
    "Promesa":          "Las Promesas de Dios",
    "Fe viva":          "Fe en Acción",
    "Paz tarde":        "Paz de la Tarde",
    "Gloria":           "Gloria a Dios",
    "Manantial":        "Manantial de Vida",
    "Solemnidad":       "Solemnidad",
    "Intercesión":      "Intercesión",
    "Ofrenda":          "Ofrenda",
    "Silencio":         "Silencio Santo",
    "Madrugada":        "Madrugada con Dios",
    "Ungimiento":       "Ungimiento",
    "Restauración":     "Restauración",
    "Liberación":       "Liberación",
    "Adoración serena": "Adoración Serena",
    "Alabanza":         "Alabanza",
    "Quietud":          "Quietud",
    "Reverencia":       "Reverencia",
    "Anhelo":           "Anhelo del Alma",
}


def _fmt_time(total_seconds: int) -> str:
    """Format seconds as H:MM:SS or M:SS."""
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def chapters_for_video(
    theme: str,
    format_key: str,   # "60min" | "120min"
    moods: list[str] | None = None,
) -> str:
    """
    Build YouTube chapter text for one video.

    Returns multiline string:
        0:00 Introducción — Paz y Meditación
        20:00 Reposo en Dios
        40:00 Contemplación
    """
    if format_key == "120min":
        duration_min = 120
        minutes_per_mood = 20   # 6 moods × 20min = 120min
        video_moods = moods or THEME_MOODS_120.get(theme, [
            "Paz profunda", "Reposo", "Contemplación",
            "Silencio", "Madrugada", "Ungimiento",
        ])
    else:
        duration_min = 60
        minutes_per_mood = 20   # 3 moods × 20min = 60min
        video_moods = moods or THEME_MOODS.get(theme, ["Paz profunda", "Adoración", "Devoción"])

    label = THEME_LABELS.get(theme, theme.capitalize())
    lines: list[str] = []

    for i, mood in enumerate(video_moods):
        t = i * minutes_per_mood * 60
        mood_label = MOOD_LABELS.get(mood, mood)
        if i == 0:
            lines.append(f"{_fmt_time(t)} Introducción — {mood_label}")
        else:
            lines.append(f"{_fmt_time(t)} {mood_label}")

    return "\n".join(lines)


def generate_all_chapters(
    themes: list[str],
    formats: list[str],
    moods_60: dict[str, list[str]] | None = None,
    relaxing_moods_120: list[str] | None = None,
) -> str:
    """Build full chapters text block for all theme/format combos."""
    sections: list[str] = []

    for fmt in formats:
        for theme in themes:
            label = THEME_LABELS.get(theme, theme.capitalize())
            header = f"=== {label} ({fmt}) ==="
            if fmt == "120min":
                moods = relaxing_moods_120 or THEME_MOODS_120.get(theme)
            else:
                moods = (moods_60 or THEME_MOODS).get(theme)
            chaps = chapters_for_video(theme, fmt, moods)
            sections.append(f"{header}\n{chaps}")

    return "\n\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate YouTube chapter timestamps.")
    parser.add_argument("--themes", nargs="+", metavar="THEME", default=ALL_THEMES,
                        help=f"Themes (default: all — {ALL_THEMES})")
    parser.add_argument("--format", choices=["60min", "120min", "all"], default="all",
                        help="Video format to generate chapters for (default: all)")
    parser.add_argument("--out", metavar="FILE", help="Write output to file (default: stdout)")
    args = parser.parse_args()

    formats = (
        ["60min", "120min"] if args.format == "all"
        else [args.format]
    )

    output = generate_all_chapters(args.themes, formats)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"Chapters written → {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
