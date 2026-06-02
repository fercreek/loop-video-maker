#!/usr/bin/env python3
"""
generate_etsy_premium.py — Wallpapers premium nivel 10/10 para @VersiculoDeDios
Target: Mujer cristiana latinoamericana 30-50 años, pantalla todo el día + impresión.

Diseño:
- Tipografía dominante 46-72px Georgia Bold (serif espiritual)
- Fondo oscuro dramático con vignette radial (sin caja de texto)
- Sombra de texto profunda multicapa (no outline)
- Acento de línea por tema (azul cielo / dorado / mint)
- Watermark sutil @VersiculoDeDios + RVR1960
- 1080x1080 PNG optimizado para pantalla + impresión

Packs: paz (10) · fe (10) · sanacion (10) = 30 wallpapers
"""

import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).parent.parent
FONDOS_DIR = BASE / "output" / "fondos"
OUT_BASE = BASE / "output" / "etsy" / "premium"

# ---------------------------------------------------------------------------
# VERSÍCULOS CURADOS — cortos, poderosos, curados editorialmente
# ---------------------------------------------------------------------------

PACK_PAZ = [
    {"texto": "La paz de Dios sobrepasa todo entendimiento.", "ref": "Fil 4:7"},
    {"texto": "Tú guardarás en completa paz al que en ti confía.", "ref": "Is 26:3"},
    {"texto": "Mi paz os doy; no como el mundo la da.", "ref": "Jn 14:27"},
    {"texto": "En paz me acostaré, porque solo tú, Jehová,\nme haces vivir confiado.", "ref": "Sal 4:8"},
    {"texto": "Estad quietos, y conoced que yo soy Dios.", "ref": "Sal 46:10"},
    {"texto": "La paz sea contigo; no temas, no morirás.", "ref": "Jue 6:23"},
    {"texto": "Jehová está en medio de ti, poderoso; él salvará.", "ref": "Sof 3:17"},
    {"texto": "Ven a mí todos los que están cargados;\nyo os haré descansar.", "ref": "Mt 11:28"},
    {"texto": "No se turbe vuestro corazón, ni tenga miedo.", "ref": "Jn 14:27b"},
    {"texto": "El fruto del Espíritu es amor, gozo, paz.", "ref": "Gál 5:22"},
]

PACK_FE = [
    {"texto": "La fe es la certeza de lo que se espera.", "ref": "Heb 11:1"},
    {"texto": "Todo lo puedo en Cristo que me fortalece.", "ref": "Fil 4:13"},
    {"texto": "Si tuvieras fe como un grano de mostaza.", "ref": "Mt 17:20"},
    {"texto": "El justo por su fe vivirá.", "ref": "Hab 2:4"},
    {"texto": "Confía en Jehová con todo tu corazón.", "ref": "Prov 3:5"},
    {"texto": "No temas, solo cree.", "ref": "Mc 5:36"},
    {"texto": "La fe sin obras es muerta.", "ref": "Stg 2:17"},
    {"texto": "Nada os será imposible.", "ref": "Mt 17:20b"},
    {"texto": "Dios es fiel.", "ref": "1 Cor 1:9"},
    {"texto": "Camina en fe, no por vista.", "ref": "2 Cor 5:7"},
]

PACK_SANACION = [
    {"texto": "Yo soy Jehová tu sanador.", "ref": "Ex 15:26"},
    {"texto": "Él sana todas tus dolencias.", "ref": "Sal 103:3"},
    {"texto": "Su palabra sana mis enfermedades.", "ref": "Sal 107:20"},
    {"texto": "Por su llaga fuimos nosotros curados.", "ref": "Is 53:5"},
    {"texto": "Quiero; sé limpio.", "ref": "Mt 8:3"},
    {"texto": "Levántate, toma tu lecho y anda.", "ref": "Jn 5:8"},
    {"texto": "El Señor está cerca de los que tienen\nel corazón quebrantado.", "ref": "Sal 34:18"},
    {"texto": "Él restaura mi alma.", "ref": "Sal 23:3"},
    {"texto": "Derramaré agua sobre el sediento.", "ref": "Is 44:3"},
    {"texto": "Serás sano.", "ref": "Jn 5:14"},
]

# ---------------------------------------------------------------------------
# CONFIGURACIÓN POR TEMA
# ---------------------------------------------------------------------------

TEMA_CONFIG = {
    "paz": {
        "versiculos": PACK_PAZ,
        # Fondos: agua, amanecer sereno, nubes, estrellas
        "fondos": [
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
        ],
        "accent_color": (184, 212, 245),    # #B8D4F5 azul cielo
        "vignette_color": (8, 15, 35),      # azul noche profundo
    },
    "fe": {
        "versiculos": PACK_FE,
        # Fondos: montaña, cima, nubes dramáticas, aurora
        "fondos": [
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
        ],
        "accent_color": (245, 216, 144),    # #F5D890 dorado
        "vignette_color": (25, 12, 3),      # marrón oscuro cálido
    },
    "sanacion": {
        "versiculos": PACK_SANACION,
        # Fondos: bosque, luz entre árboles, agua, amanecer
        "fondos": [
            "fondo_ai_waterfall_light.jpg",
            "fondo_ai_garden_eden.jpg",
            "fondo_ai_spring_renewal.jpg",
            "fondo_ai_river_baptism.jpg",
            "fondo_ai_rain_blessing.jpg",
            "fondo_ai_sacred_forest.jpg",
            "fondo_ai_cedar_forest.jpg",
            "fondo_ai_gethsemane.jpg",
            "fondo_ai_jordan_valley.jpg",
            "fondo_ai_winter_hope.jpg",
        ],
        "accent_color": (144, 228, 193),    # #90E4C1 mint
        "vignette_color": (3, 18, 12),      # verde oscuro profundo
    },
}

SIZE = (1080, 1080)
W, H = SIZE

# ---------------------------------------------------------------------------
# FUENTES — Georgia Bold (serif espiritual, legible, premium)
# ---------------------------------------------------------------------------

FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/System/Library/Fonts/Supplemental/Baskerville.ttc",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]

FONT_CANDIDATES_REGULAR = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Baskerville.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]

FONT_CANDIDATES_LIGHT = [
    "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Avenir.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]

_font_cache: dict = {}


def get_font(size: int, style: str = "bold") -> ImageFont.FreeTypeFont:
    key = (size, style)
    if key in _font_cache:
        return _font_cache[key]

    if style == "bold":
        candidates = FONT_CANDIDATES_BOLD
    elif style == "light":
        candidates = FONT_CANDIDATES_LIGHT
    else:
        candidates = FONT_CANDIDATES_REGULAR

    for path in candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                _font_cache[key] = font
                return font
            except Exception:
                continue
    font = ImageFont.load_default()
    _font_cache[key] = font
    return font


# ---------------------------------------------------------------------------
# TIPOGRAFÍA ADAPTATIVA
# ---------------------------------------------------------------------------

def measure_line(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_to_width(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Wrap a single paragraph to fit max_width. Respects explicit \\n."""
    result = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            result.append("")
            continue
        current = []
        for word in words:
            test = " ".join(current + [word])
            w, _ = measure_line(draw, test, font)
            if w <= max_width:
                current.append(word)
            else:
                if current:
                    result.append(" ".join(current))
                current = [word]
        if current:
            result.append(" ".join(current))
    return result


def pick_font_size(text: str, draw: ImageDraw.ImageDraw, max_w: int, max_h: int) -> tuple:
    """
    Premium font-size ladder per spec:
    - ≤50 chars → 72px
    - 51-70 chars → 58px
    - >70 chars → 46px
    Tries each size, reduces if overflow. Returns (font, lines, size).
    """
    char_count = len(text.replace("\n", " "))

    if char_count <= 50:
        size_ladder = [72, 60, 52, 46, 40]
    elif char_count <= 70:
        size_ladder = [58, 52, 46, 40, 36]
    else:
        size_ladder = [46, 40, 36, 32, 28]

    for size in size_ladder:
        font = get_font(size, "bold")
        lines = wrap_to_width(text, font, max_w, draw)
        line_h = int(size * 1.5)
        total_h = len(lines) * line_h
        if total_h <= max_h:
            return font, lines, size, line_h
    # fallback minimum
    font = get_font(28, "bold")
    lines = wrap_to_width(text, font, max_w, draw)
    return font, lines, 28, int(28 * 1.5)


# ---------------------------------------------------------------------------
# RENDERING UTILITIES
# ---------------------------------------------------------------------------

def apply_vignette(img: Image.Image, vignette_color: tuple, strength: float = 0.72) -> Image.Image:
    """
    Radial vignette: dark ellipse in center → text readable without box.
    strength: max opacity 0..1 at center.
    """
    vig = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(vig)

    cx, cy = W // 2, H // 2
    # Draw concentric ellipses from outside in, building up the dark center
    steps = 60
    for i in range(steps):
        # Reversed: i=0 is outer (transparent), i=steps-1 is center (darkest)
        t = i / steps  # 0=outer edge, 1=center
        # Ellipse dims: outer → smaller
        rx = int(cx * (1 - t * 0.65))
        ry = int(cy * (1 - t * 0.65))
        alpha = int(strength * 255 * (t ** 1.6))
        r, g, b = vignette_color
        draw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=(r, g, b, alpha),
        )

    # Gaussian blur to smooth
    vig = vig.filter(ImageFilter.GaussianBlur(radius=90))

    result = img.convert("RGBA")
    result = Image.alpha_composite(result, vig)
    return result


def draw_text_shadow(draw: ImageDraw.ImageDraw, text: str, pos: tuple,
                     font, fill=(255, 255, 255)) -> None:
    """
    Premium drop shadow: 5 layers with decreasing opacity.
    No outline/stroke — only shadow. Gives depth without box feel.
    """
    x, y = pos
    shadow_layers = [
        (3, 4, (0, 0, 0, 200)),
        (5, 7, (0, 0, 0, 160)),
        (7, 10, (0, 0, 0, 100)),
        (10, 14, (0, 0, 0, 60)),
        (13, 18, (0, 0, 0, 30)),
    ]
    for dx, dy, shadow_fill in shadow_layers:
        draw.text((x + dx, y + dy), text, font=font, fill=shadow_fill)
    draw.text((x, y), text, font=font, fill=fill)


def draw_accent_line(draw: ImageDraw.ImageDraw, center_y: int, accent_color: tuple) -> None:
    """Horizontal accent line, 120px wide, 2px tall, centered."""
    line_w = 120
    x1 = (W - line_w) // 2
    x2 = x1 + line_w
    r, g, b = accent_color
    # Main line
    draw.rectangle([x1, center_y, x2, center_y + 2], fill=(r, g, b, 230))
    # Subtle glow above/below
    draw.rectangle([x1 + 10, center_y - 1, x2 - 10, center_y], fill=(r, g, b, 80))
    draw.rectangle([x1 + 10, center_y + 3, x2 - 10, center_y + 4], fill=(r, g, b, 80))


# ---------------------------------------------------------------------------
# MAIN IMAGE GENERATOR
# ---------------------------------------------------------------------------

def generate_wallpaper(verso: dict, fondo_path: Path, out_path: Path,
                       accent_color: tuple, vignette_color: tuple) -> None:
    texto = verso["texto"]
    ref = verso["ref"]

    # 1. Load & resize background
    bg = Image.open(fondo_path).convert("RGB")
    bg = bg.resize(SIZE, Image.LANCZOS)

    # 2. Very light base darkening (preserve fondo drama)
    base_dark = Image.new("RGBA", SIZE, (0, 0, 0, 60))
    bg = Image.alpha_composite(bg.convert("RGBA"), base_dark).convert("RGB")

    # 3. Radial vignette (dark ellipse center — the key effect)
    bg = apply_vignette(bg, vignette_color, strength=0.58)
    img = bg.convert("RGB")

    draw = ImageDraw.Draw(img, "RGBA")

    # 4. Typography zones
    MARGIN = 80                          # px from edge
    TEXT_MAX_W = W - MARGIN * 2          # 920px
    VERSE_ZONE_TOP = 200                 # start of verse area
    VERSE_ZONE_BOTTOM = 800              # end of verse area
    VERSE_ZONE_H = VERSE_ZONE_BOTTOM - VERSE_ZONE_TOP   # 600px
    REF_ZONE_Y = 840                     # reference text y
    ACCENT_LINE_Y = REF_ZONE_Y - 18      # line above reference
    WATERMARK_Y = H - 46                 # bottom strip

    # 5. Adaptive font + layout
    temp_draw = ImageDraw.Draw(Image.new("RGB", SIZE))
    font, lines, font_size, line_h = pick_font_size(
        texto, temp_draw, TEXT_MAX_W, VERSE_ZONE_H
    )

    total_text_h = len(lines) * line_h
    # Center verse block vertically in zone
    start_y = VERSE_ZONE_TOP + (VERSE_ZONE_H - total_text_h) // 2

    # 6. Draw verse lines with deep shadow
    for i, line in enumerate(lines):
        lw, lh = measure_line(draw, line, font)
        x = (W - lw) // 2
        y = start_y + i * line_h
        draw_text_shadow(draw, line, (x, y), font, fill=(255, 255, 255))

    # 7. Accent line
    draw_accent_line(draw, ACCENT_LINE_Y, accent_color)

    # 8. Reference — dorado suave, italic feel
    ref_size = 36
    ref_font = get_font(ref_size, "light")
    ref_color = (232, 213, 163)    # #E8D5A3 dorado suave
    rw, _ = measure_line(draw, ref, ref_font)
    rx = (W - rw) // 2
    draw_text_shadow(draw, ref, (rx, REF_ZONE_Y), ref_font,
                     fill=ref_color)

    # 9. Watermark @VersiculoDeDios — bottom right, 18px, 50% opacity
    wm_font = get_font(18, "regular")
    wm_text = "@VersiculoDeDios"
    wm_w, _ = measure_line(draw, wm_text, wm_font)
    wm_x = W - wm_w - 32
    draw.text((wm_x, WATERMARK_Y), wm_text, font=wm_font, fill=(255, 255, 255, 127))

    # 10. RVR1960 — bottom left, 14px, 40% opacity
    rvr_font = get_font(14, "regular")
    draw.text((32, WATERMARK_Y + 4), "RVR1960", font=rvr_font, fill=(255, 255, 255, 102))

    # 11. Save PNG
    img.save(out_path, "PNG", optimize=True)


# ---------------------------------------------------------------------------
# FONDO SELECTION WITH FALLBACK
# ---------------------------------------------------------------------------

def resolve_fondo(preferred: str, index: int) -> Path:
    """Return existing fondo path, with intelligent fallback."""
    path = FONDOS_DIR / preferred
    if path.exists():
        return path
    # Fallback: pick any available fondo by index
    available = sorted(FONDOS_DIR.glob("fondo_ai_*.jpg"))
    if available:
        return available[index % len(available)]
    # Last resort: any jpg
    all_jpgs = sorted(FONDOS_DIR.glob("*.jpg"))
    if all_jpgs:
        return all_jpgs[index % len(all_jpgs)]
    raise FileNotFoundError(f"No background images found in {FONDOS_DIR}")


# ---------------------------------------------------------------------------
# PACK GENERATOR
# ---------------------------------------------------------------------------

def generate_pack(tema: str) -> int:
    config = TEMA_CONFIG[tema]
    out_dir = OUT_BASE / f"pack_{tema}"
    out_dir.mkdir(parents=True, exist_ok=True)

    versiculos = config["versiculos"]
    fondos = config["fondos"]
    accent = config["accent_color"]
    vignette = config["vignette_color"]

    count = 0
    print(f"\n  pack_{tema} ({len(versiculos)} wallpapers)")
    print(f"  {'─' * 52}")

    for i, verso in enumerate(versiculos):
        fondo_path = resolve_fondo(fondos[i % len(fondos)], i)
        ref_safe = verso["ref"].replace(":", "_").replace(" ", "_")
        out_name = f"{tema}_{i+1:02d}_{ref_safe}.png"
        out_path = out_dir / out_name

        texto = verso["texto"]
        char_count = len(texto.replace("\n", " "))

        # Determine font size label for logging
        if char_count <= 50:
            size_label = "72px"
        elif char_count <= 70:
            size_label = "58px"
        else:
            size_label = "46px"

        generate_wallpaper(verso, fondo_path, out_path, accent, vignette)

        print(f"  [{i+1:02d}] {verso['ref']:12s} {char_count:3d}ch → {size_label} → {out_name}")
        count += 1

    return count


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    print("Generating premium Etsy wallpapers for @VersiculoDeDios")
    print(f"Output: {OUT_BASE}")
    print(f"{'=' * 60}")

    total = 0
    for tema in ["paz", "fe", "sanacion"]:
        n = generate_pack(tema)
        total += n
        print(f"  OK — {n} wallpapers in output/etsy/premium/pack_{tema}/")

    print(f"\n{'=' * 60}")
    print(f"Total generados: {total} wallpapers premium.")
    print(f"Ruta: {OUT_BASE}")


if __name__ == "__main__":
    main()
