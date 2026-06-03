#!/usr/bin/env python3
"""
Generate Etsy wallpaper packs (1080x1080 PNG) for @VersiculoDeDios
Topics: paz, fe, sanacion — 10 images each

v2 improvements:
- Adaptive font size (38px → 24px min) + smart truncation for overflow
- Color theming per pack (overlay tint + text border color)
- Premium layout: no box, drop shadow only, line spacing 1.4
- Logo bottom-right, white, opacity 0.6
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

# v2: Color theming per pack
# overlay_tint: RGBA applied on top of base dark overlay
# accent_color: RGB tuple for reference text and separator line
# border_color: RGB tuple for text outline/glow

TEMA_CONFIG = {
    "paz": {
        "fondos": FONDOS_PAZ,
        "overlay_tint": (20, 30, 80, 140),       # azul/indigo suave
        "accent": (184, 212, 245),                 # #B8D4F5 text color for reference
        "border_color": (184, 212, 245),           # same for glow/shadow tint
        "out_dir": OUT_DIR / "pack_paz",
    },
    "fe": {
        "fondos": FONDOS_FE,
        "overlay_tint": (80, 50, 10, 140),         # dorado/cálido
        "accent": (245, 216, 144),                  # #F5D890
        "border_color": (245, 216, 144),
        "out_dir": OUT_DIR / "pack_fe",
    },
    "sanacion": {
        "fondos": FONDOS_SANACION,
        "overlay_tint": (10, 60, 40, 140),          # verde/mint
        "accent": (144, 228, 193),                   # #90E4C1
        "border_color": (144, 228, 193),
        "out_dir": OUT_DIR / "pack_sanacion",
    },
}

SIZE = (1080, 1080)
LOGO_TEXT = "@VersiculoDeDios"
MAX_CHARS_BEFORE_TRUNCATE = 120
VERSE_FONT_SIZE_MAX = 38
VERSE_FONT_SIZE_MIN = 24
VERSE_LINE_SPACING_FACTOR = 1.4  # line height = font_size * factor


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


def smart_truncate(text: str, referencia: str) -> str:
    """
    If text > MAX_CHARS, return first 1/3 + '...' + referencia hint.
    Keeps the spiritual intent without overflow.
    """
    if len(text) <= MAX_CHARS_BEFORE_TRUNCATE:
        return text
    # Find a word boundary near 1/3 of the text
    target = max(60, len(text) // 3)
    cut = text.rfind(" ", 0, target)
    if cut == -1:
        cut = target
    return text[:cut].rstrip(".,;:") + "..."


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


def find_adaptive_font_and_lines(texto: str, draw, max_width: int, max_height: int):
    """
    Try decreasing font sizes from MAX to MIN until text fits in the available area.
    Returns (font, lines, font_size, fits) where fits=True if no truncation needed.
    """
    for font_size in range(VERSE_FONT_SIZE_MAX, VERSE_FONT_SIZE_MIN - 1, -2):
        font = get_font(font_size)
        lines = wrap_text_to_width(texto, font, max_width, draw)
        line_height = int(font_size * VERSE_LINE_SPACING_FACTOR)
        total_h = len(lines) * line_height
        if total_h <= max_height:
            return font, lines, font_size, True
    # Still doesn't fit at minimum size — return min size (will overflow slightly)
    font = get_font(VERSE_FONT_SIZE_MIN)
    lines = wrap_text_to_width(texto, font, max_width, draw)
    return font, lines, VERSE_FONT_SIZE_MIN, False


def draw_text_with_shadow(draw, text, position, font,
                          fill=(255, 255, 255),
                          shadow_color=(0, 0, 0),
                          shadow_opacity=150,
                          shadow_offset=3):
    """Draw text with a soft drop shadow (no box, no outline)."""
    x, y = position
    # Multi-layer shadow for soft feel
    for blur_offset in range(1, shadow_offset + 1):
        alpha = shadow_opacity // (blur_offset + 1)
        shadow = shadow_color + (alpha,)
        draw.text((x + blur_offset, y + blur_offset), text, font=font, fill=shadow)
        draw.text((x - blur_offset // 2, y + blur_offset), text, font=font, fill=shadow)
    # Main text
    draw.text((x, y), text, font=font, fill=fill)


def generate_image(versiculo: dict, fondo_path: Path, out_path: Path,
                   overlay_tint: tuple, accent: tuple, border_color: tuple):
    """Generate a single 1080x1080 wallpaper image — premium layout v2."""
    # --- Background ---
    bg = Image.open(fondo_path).convert("RGBA")
    bg = bg.resize(SIZE, Image.LANCZOS)

    # Base dark overlay for readability
    base_overlay = Image.new("RGBA", SIZE, (0, 0, 0, 110))
    bg = Image.alpha_composite(bg, base_overlay)

    # Thematic color tint overlay (new in v2)
    tint_overlay = Image.new("RGBA", SIZE, overlay_tint)
    bg = Image.alpha_composite(bg, tint_overlay)

    img = bg.convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Text area geometry ---
    TEXT_AREA_TOP = 220
    TEXT_AREA_BOTTOM = 820
    REF_Y = 840
    LOGO_Y = SIZE[1] - 46
    MAX_TEXT_WIDTH = 860   # wider than before (no box margins needed)
    text_area_height = TEXT_AREA_BOTTOM - TEXT_AREA_TOP - 40  # 40px padding

    texto = versiculo.get("texto", "")
    referencia = versiculo.get("referencia") or versiculo.get("ref", "")
    version = versiculo.get("version", "RVR1960")

    # --- Smart truncation for very long verses ---
    truncated = False
    if len(texto) > MAX_CHARS_BEFORE_TRUNCATE:
        texto_display = smart_truncate(texto, referencia)
        truncated = True
    else:
        texto_display = texto

    # --- Adaptive font size ---
    temp_draw = ImageDraw.Draw(Image.new("RGB", SIZE))
    font, lines, font_size, fits = find_adaptive_font_and_lines(
        texto_display, temp_draw, MAX_TEXT_WIDTH, text_area_height
    )

    line_height = int(font_size * VERSE_LINE_SPACING_FACTOR)
    total_text_height = len(lines) * line_height

    # Center text block vertically in text area
    start_y = TEXT_AREA_TOP + (text_area_height - total_text_height) // 2
    start_y = max(TEXT_AREA_TOP, start_y)

    # --- Draw verse lines ---
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (1080 - text_w) // 2
        y = start_y + i * line_height
        draw_text_with_shadow(
            draw, line, (x, y), font,
            fill=(255, 255, 255),
            shadow_color=(0, 0, 0),
            shadow_opacity=160,
            shadow_offset=4,
        )

    # --- Separator line (simple, thematic color) ---
    sep_y = REF_Y - 14
    sep_color = accent + (180,)
    sep_x1 = 300
    sep_x2 = 780
    draw.rectangle([sep_x1, sep_y, sep_x2, sep_y + 1], fill=sep_color)

    # --- Reference text ---
    ref_font_size = 22
    ref_font = get_font(ref_font_size, bold=True)
    ref_color = accent + (255,)
    bbox = draw.textbbox((0, 0), referencia, font=ref_font)
    ref_w = bbox[2] - bbox[0]
    ref_x = (1080 - ref_w) // 2
    draw_text_with_shadow(
        draw, referencia, (ref_x, REF_Y), ref_font,
        fill=accent,
        shadow_color=(0, 0, 0),
        shadow_opacity=200,
        shadow_offset=2,
    )

    # --- Logo bottom-right, white, opacity ~0.6 ---
    logo_font = get_font(24)
    logo_color = (255, 255, 255, 153)  # 0.6 opacity = 153/255
    logo_bbox = draw.textbbox((0, 0), LOGO_TEXT, font=logo_font)
    logo_w = logo_bbox[2] - logo_bbox[0]
    logo_x = 1080 - logo_w - 30
    draw.text((logo_x, LOGO_Y), LOGO_TEXT, font=logo_font, fill=logo_color)

    # --- Version badge bottom-left ---
    version_font = get_font(20)
    draw.text((30, LOGO_Y), version, font=version_font, fill=(255, 255, 255, 120))

    img.save(out_path, "PNG", optimize=True)

    status = ""
    if truncated:
        status = " [TRUNCATED]"
    elif not fits:
        status = " [OVERFLOW-MIN-FONT]"
    return out_path, font_size, status


def generate_pack(tema: str):
    config = TEMA_CONFIG[tema]
    versiculos = load_versiculos(tema, 10)
    out_dir: Path = config["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    overlay_tint = config["overlay_tint"]
    accent = config["accent"]
    border_color = config["border_color"]
    fondos = config["fondos"]

    generated = []
    issues = []
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

        out_path_result, font_size, status = generate_image(
            versiculo, fondo_path, out_path,
            overlay_tint=overlay_tint,
            accent=accent,
            border_color=border_color,
        )
        texto_len = len(versiculo.get("texto", ""))
        print(f"  [{i+1}/10] {ref} ({texto_len}ch) → font:{font_size}px{status} → {out_name}")
        if status:
            issues.append(f"{ref}{status}")
        generated.append(out_path_result)

    return generated, issues


def main():
    temas = ["paz", "fe", "sanacion"]
    total = 0
    all_issues = []
    for tema in temas:
        print(f"\nGenerando pack_{tema}...")
        paths, issues = generate_pack(tema)
        print(f"  ✓ {len(paths)} imágenes en output/etsy/pack_{tema}/")
        if issues:
            print(f"  ⚠ Issues: {issues}")
        all_issues.extend(issues)
        total += len(paths)

    print(f"\nTotal: {total} imágenes generadas.")
    if all_issues:
        print(f"Imágenes con overflow/truncado: {len(all_issues)}")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("Todas las imágenes dentro del área de texto. ✓")


if __name__ == "__main__":
    main()
