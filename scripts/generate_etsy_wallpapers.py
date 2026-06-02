#!/usr/bin/env python3
"""
Generate Etsy wallpaper packs (1080x1080 PNG) for @VersiculoDeDios
Topics: paz, fe, sanacion — 10 images each
"""

import json
import os
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).parent.parent
FONDOS_DIR = BASE / "output" / "fondos"
VERSICULOS_DIR = BASE / "data" / "versiculos"
OUT_DIR = BASE / "output" / "etsy"

# Cinematic backgrounds selected per theme (thematic match)
FONDOS_PAZ = [
    "fondo_ai_still_waters.jpg",
    "fondo_ai_heaven_clouds.jpg",
    "fondo_ai_morning_glory.jpg",
    "fondo_ai_galilee_sunrise.jpg",
    "fondo_ai_divine_sunrise.jpg",
    "fondo_ai_storm_peace.jpg",
    "fondo_ai_shepherd_hills.jpg",
    "fondo_ai_river_life.jpg",
    "fondo_ai_night_stars.jpg",
    "fondo_ai_starry_desert.jpg",
]

FONDOS_FE = [
    "fondo_ai_mountain_glory.jpg",
    "fondo_ai_cross_sunrise.jpg",
    "fondo_ai_aurora_faith.jpg",
    "fondo_ai_holy_land_sunset.jpg",
    "fondo_ai_mount_sinai.jpg",
    "fondo_ai_promised_land.jpg",
    "fondo_ai_ancient_temple.jpg",
    "fondo_ai_burning_bush.jpg",
    "fondo_ai_dove_descending.jpg",
    "fondo_ai_spirit_fire.jpg",
]

FONDOS_SANACION = [
    "fondo_ai_waterfall_light.jpg",
    "fondo_ai_garden_eden.jpg",
    "fondo_ai_spring_renewal.jpg",
    "fondo_ai_river_baptism.jpg",
    "fondo_ai_rain_blessing.jpg",
    "fondo_ai_ocean_worship.jpg",
    "fondo_ai_cedar_forest.jpg",
    "fondo_ai_sacred_forest.jpg",
    "fondo_ai_jordan_valley.jpg",
    "fondo_ai_winter_hope.jpg",
]

TEMA_CONFIG = {
    "paz": {
        "fondos": FONDOS_PAZ,
        "accent": (232, 213, 163),   # golden warm
        "out_dir": OUT_DIR / "pack_paz",
    },
    "fe": {
        "fondos": FONDOS_FE,
        "accent": (240, 201, 135),   # golden faith
        "out_dir": OUT_DIR / "pack_fe",
    },
    "sanacion": {
        "fondos": FONDOS_SANACION,
        "accent": (168, 230, 207),   # mint healing
        "out_dir": OUT_DIR / "pack_sanacion",
    },
}

SIZE = (1080, 1080)
LOGO_TEXT = "@VersiculoDeDios"


def load_versiculos(tema: str, count: int = 10):
    path = VERSICULOS_DIR / f"{tema}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    versiculos = data["versiculos"][:count]
    return versiculos


def get_font(size: int, bold: bool = False):
    """Try system fonts in order of preference."""
    candidates_bold = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates_regular = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    candidates = candidates_bold if bold else candidates_regular
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_text_with_shadow(draw, text, position, font, fill=(255, 255, 255), shadow_offset=3, shadow_opacity=160):
    """Draw text with a soft drop shadow."""
    x, y = position
    shadow_color = (0, 0, 0, shadow_opacity)
    # shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # main text
    draw.text((x, y), text, font=font, fill=fill)


def wrap_text_to_width(text: str, font, max_width: int, draw) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def generate_image(versiculo: dict, fondo_path: Path, out_path: Path, accent: tuple):
    """Generate a single 1080x1080 wallpaper image."""
    # Load and resize background
    bg = Image.open(fondo_path).convert("RGBA")
    bg = bg.resize(SIZE, Image.LANCZOS)

    # Dark overlay for readability
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    # Gradient-ish: darker at center-bottom where text will live
    draw_overlay.rectangle([0, 0, 1080, 1080], fill=(0, 0, 0, 120))
    # Lighter vignette effect at edges
    bg = Image.alpha_composite(bg, overlay)

    img = bg.convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # Decorative separator bar
    bar_color = accent + (200,)
    draw.rectangle([200, 280, 880, 283], fill=bar_color)
    draw.rectangle([200, 750, 880, 753], fill=bar_color)

    # === Verse text ===
    verse_font_size = 46
    verse_font = get_font(verse_font_size)

    texto = versiculo.get("texto", "")
    referencia = versiculo.get("referencia") or versiculo.get("ref", "")

    max_text_width = 800
    lines = wrap_text_to_width(texto, verse_font, max_text_width, draw)

    # Calculate total text block height
    line_height = verse_font_size + 14
    total_text_height = len(lines) * line_height

    # Center text block vertically between bars
    text_area_top = 310
    text_area_bottom = 730
    text_area_height = text_area_bottom - text_area_top
    start_y = text_area_top + (text_area_height - total_text_height) // 2

    # Draw each line centered
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=verse_font)
        text_w = bbox[2] - bbox[0]
        x = (1080 - text_w) // 2
        y = start_y + i * line_height
        draw_text_with_shadow(draw, line, (x, y), verse_font, fill=(255, 255, 255), shadow_offset=2, shadow_opacity=180)

    # === Reference ===
    ref_font = get_font(38, bold=True)
    accent_color = tuple(int(c * 0.9) for c in accent) + (255,)
    ref_color = accent
    bbox = draw.textbbox((0, 0), referencia, font=ref_font)
    ref_w = bbox[2] - bbox[0]
    ref_x = (1080 - ref_w) // 2
    draw_text_with_shadow(draw, referencia, (ref_x, 770), ref_font, fill=ref_color, shadow_offset=2, shadow_opacity=200)

    # === Logo ===
    logo_font = get_font(28)
    logo_color = (255, 255, 255, 180)
    draw.text((1080 - 260, 1080 - 48), LOGO_TEXT, font=logo_font, fill=logo_color)

    # === Version badge ===
    version_font = get_font(22)
    version = versiculo.get("version", "RVR1960")
    draw.text((38, 1080 - 48), version, font=version_font, fill=(255, 255, 255, 140))

    img.save(out_path, "PNG", optimize=True)
    return out_path


def generate_pack(tema: str):
    config = TEMA_CONFIG[tema]
    versiculos = load_versiculos(tema, 10)
    out_dir: Path = config["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    accent = config["accent"]
    fondos = config["fondos"]

    generated = []
    for i, versiculo in enumerate(versiculos):
        fondo_name = fondos[i % len(fondos)]
        fondo_path = FONDOS_DIR / fondo_name

        # Fallback if specific fondo missing
        if not fondo_path.exists():
            available = sorted(FONDOS_DIR.glob("fondo_ai_*.jpg"))
            if available:
                fondo_path = available[i % len(available)]
            else:
                available = sorted(FONDOS_DIR.glob("*.jpg"))
                fondo_path = available[i % len(available)]

        ref = versiculo.get("referencia") or versiculo.get("ref", f"versiculo_{i+1}")
        safe_ref = ref.replace(":", "_").replace(" ", "_").replace("-", "_")
        out_name = f"{tema}_{i+1:02d}_{safe_ref}.png"
        out_path = out_dir / out_name

        print(f"  [{i+1}/10] {ref} → {out_name}")
        generate_image(versiculo, fondo_path, out_path, accent)
        generated.append(out_path)

    return generated


def main():
    temas = ["paz", "fe", "sanacion"]
    total = 0
    for tema in temas:
        print(f"\nGenerando pack_{tema}...")
        paths = generate_pack(tema)
        print(f"  ✓ {len(paths)} imágenes en output/etsy/pack_{tema}/")
        total += len(paths)
    print(f"\nTotal: {total} imágenes generadas.")


if __name__ == "__main__":
    main()
