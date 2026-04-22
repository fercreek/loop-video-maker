"""
core/thumbnail_gen.py — YouTube thumbnail generator for Fe en Acción.

Produces 1280×720 JPEG thumbnails with:
  - Oil painting background with left-zone dark gradient
  - Impact bold title (accent line 1, white line 2)
  - Colored glow halo behind title text
  - Thin accent left bar
  - Subtitle with auto-wrap
  - Accent divider line
  - Channel watermark
  - Diagonal arrow pointing into the painting
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── Constants ────────────────────────────────────────────────────────────────

THUMB_SIZE  = (1280, 720)
FONT_BOLD   = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_SUB    = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
CHANNEL_TAG = "@FeEnAcción"

# Default accent color per theme
THEME_ACCENT: dict[str, str] = {
    "fe":        "#FFD700",
    "amor":      "#FF9F6B",
    "esperanza": "#A8D8FF",
    "fuerza":    "#FFD700",
    "gratitud":  "#B8F5A0",
    "paz":       "#A8D8FF",
    "salmos":    "#FFD700",
    "victoria":  "#FFD700",
}

# Title + subtitle copy per theme
THEME_COPY: dict[str, dict] = {
    "fe": {
        "title":    "¡FE QUE\nMUEVE MONTAÑAS!",
        "subtitle": "Música Cristiana para Fortalecer tu Fe",
    },
    "amor": {
        "title":    "¡EL AMOR\nDE DIOS!",
        "subtitle": "Música Cristiana para Meditar y Orar",
    },
    "esperanza": {
        "title":    "¡ESPERANZA\nEN DIOS!",
        "subtitle": "Versículos de Esperanza y Restauración",
    },
    "fuerza": {
        "title":    "¡FUERZA\nEN DIOS!",
        "subtitle": "Música para los Momentos Difíciles",
    },
    "gratitud": {
        "title":    "¡GRATITUD\nA DIOS!",
        "subtitle": "Música para Alabar y Dar Gracias",
    },
    "paz": {
        "title":    "¡PAZ\nSOBRENATURAL!",
        "subtitle": "Música Cristiana para Meditar y Dormir",
    },
    "salmos": {
        "title":    "¡SALMOS DE\nADORACIÓN!",
        "subtitle": "Música para Orar y Adorar a Dios",
    },
    "victoria": {
        "title":    "¡VICTORIA\nEN CRISTO!",
        "subtitle": "Música Cristiana para Vencer",
    },
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THEME_BG: dict[str, str] = {
    "fe":        "output/fondos/fondo_light.jpg",
    "amor":      "output/fondos/fondo_sunset.jpg",
    "esperanza": "output/fondos/fondo_dawn.jpg",
    "fuerza":    "output/fondos/fondo_mountains.jpg",
    "gratitud":  "output/fondos/fondo_valley.jpg",
    "paz":       "output/fondos/fondo_cielo.jpg",
    "salmos":    "output/fondos/fondo_celestial.jpg",
    "victoria":  "output/fondos/fondo_pastoral.jpg",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _hex(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _outlined_text(
    draw: ImageDraw.ImageDraw,
    pos: tuple,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    stroke: tuple = (0, 0, 0),
    stroke_w: int = 6,
):
    x, y = pos
    for dx in range(-stroke_w, stroke_w + 1):
        for dy in range(-stroke_w, stroke_w + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=stroke)
    draw.text(pos, text, font=font, fill=fill)


def _draw_diagonal_arrow(draw: ImageDraw.ImageDraw, cx: int, cy: int, accent: tuple, size: int = 70):
    """Draw a bold diagonal ↘ arrow centered at (cx, cy)."""
    half = size // 2
    # Arrow body going ↘
    points = [
        (cx - half,       cy - half + size // 3),
        (cx,              cy - half + size // 3),
        (cx,              cy - half),
        (cx + half,       cy),
        (cx,              cy + half),
        (cx,              cy + half - size // 3),
        (cx - half,       cy + half - size // 3),
    ]
    # Rotate 45° by swapping to a simpler chevron diagonal shape
    pts = [
        (cx - half + 10,  cy - 10),
        (cx + half - 10,  cy - 10),
        (cx + half - 10,  cy - half + 10),
        (cx + half + 10,  cy + half - 10),
        (cx - 10,         cy + half - 10),
        (cx - 10,         cy + 10),
    ]
    # Simple bold → arrow: shaft + head pointing ↘
    shaft_w = size // 5
    # Shaft diagonal line
    draw.line([(cx - half, cy - half), (cx + half, cy + half)],
              fill=accent, width=shaft_w)
    # Arrowhead (filled triangle at bottom-right)
    head = [
        (cx + half,                cy + half),
        (cx + half - size // 2,    cy + half),
        (cx + half,                cy + half - size // 2),
    ]
    draw.polygon(head, fill=accent)
    draw.polygon(head, outline=(0, 0, 0))


# ─── Core function ────────────────────────────────────────────────────────────

def make_thumbnail(
    theme: str,
    output_path: str,
    title: str | None = None,
    subtitle: str | None = None,
    bg_path: str | None = None,
    accent_hex: str | None = None,
    channel: str = CHANNEL_TAG,
) -> str:
    """
    Generate a YouTube thumbnail for the given theme.

    Args:
        theme:       Theme key (fe, amor, paz, etc.)
        output_path: Destination JPEG path.
        title:       Override title (uses THEME_COPY default if None).
        subtitle:    Override subtitle (uses THEME_COPY default if None).
        bg_path:     Override background image path.
        accent_hex:  Override accent color ("#RRGGBB").
        channel:     Channel watermark string.

    Returns:
        output_path
    """
    W, H = THUMB_SIZE

    copy    = THEME_COPY.get(theme, {"title": theme.upper(), "subtitle": ""})
    title   = title   or copy["title"]
    subtitle = subtitle or copy["subtitle"]
    bg_rel  = bg_path or THEME_BG.get(theme, "output/fondos/fondo_light.jpg")
    bg_abs  = bg_rel if os.path.isabs(bg_rel) else os.path.join(PROJECT_DIR, bg_rel)
    accent  = _hex(accent_hex or THEME_ACCENT.get(theme, "#FFD700"))

    # ── Background ──────────────────────────────────────────────────────────
    bg = Image.open(bg_abs).convert("RGB").resize((W, H), Image.LANCZOS)

    # ── Overlay: smooth left-zone dark gradient + bottom vignette ───────────
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for x in range(W):
        # Ease-out curve — stays darker longer then falls off fast at ~70%
        t = x / (W * 0.70)
        alpha = int(210 * max(0.0, 1.0 - t * t))
        ov_draw.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    for y in range(H // 2, H):
        t = (y - H // 2) / (H // 2)
        alpha = int(110 * t * t)
        ov_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    canvas = Image.alpha_composite(bg.convert("RGBA"), overlay)

    # ── Glow layer behind title ──────────────────────────────────────────────
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 130)
        font_sub   = ImageFont.truetype(FONT_SUB,  42)
        font_ch    = ImageFont.truetype(FONT_SUB,  32)
    except Exception:
        font_title = font_sub = font_ch = ImageFont.load_default()

    title_lines  = title.split("\n")
    tmp_draw     = ImageDraw.Draw(canvas)
    line_heights = [tmp_draw.textbbox((0, 0), ln, font=font_title)[3]
                    - tmp_draw.textbbox((0, 0), ln, font=font_title)[1]
                    for ln in title_lines]

    title_y = int(H * 0.11)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    y = title_y
    for i, line in enumerate(title_lines):
        glow_draw.text((60, y), line, font=font_title,
                       fill=(*accent, 180))
        y += line_heights[i] + 12
    glow = glow.filter(ImageFilter.GaussianBlur(radius=22))
    canvas = Image.alpha_composite(canvas, glow)

    # ── Final draw layer ─────────────────────────────────────────────────────
    composite = canvas.convert("RGB")
    draw      = ImageDraw.Draw(composite)

    # Left accent bar (6px)
    draw.rectangle([(0, 0), (6, H)], fill=accent)

    # Title text
    y = title_y
    for i, line in enumerate(title_lines):
        _outlined_text(
            draw, (68, y), line,
            font=font_title,
            fill=accent if i == 0 else (255, 255, 255),
            stroke_w=7,
        )
        y += line_heights[i] + 12

    # Subtitle (auto-wrap at ~38 chars)
    sub = subtitle
    if len(sub) > 38:
        idx = sub.rfind(" ", 0, 38)
        if idx > 0:
            sub = sub[:idx] + "\n" + sub[idx + 1:]
    sub_y = y + 26
    _outlined_text(draw, (68, sub_y), sub, font=font_sub,
                   fill=(230, 230, 230), stroke_w=3)

    # Accent divider line
    n_sub_lines = sub.count("\n") + 1
    line_y = int(sub_y + 42 * n_sub_lines + 12 * n_sub_lines)
    draw.rectangle([(68, line_y), (68 + 320, line_y + 5)], fill=accent)

    # Channel watermark bottom-left
    _outlined_text(draw, (68, H - 52), channel, font=font_ch,
                   fill=(255, 255, 255), stroke_w=3)

    # Diagonal ↘ arrow — positioned in center-right of dark zone
    arrow_cx = int(W * 0.62)
    arrow_cy = int(H * 0.68)
    _draw_diagonal_arrow(draw, arrow_cx, arrow_cy, accent, size=80)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    composite.save(output_path, "JPEG", quality=95)
    return output_path


def generate_thumbnail_for_theme(theme: str, output_dir: str) -> str:
    """
    Convenience wrapper: generate thumbnail for theme into output_dir.
    Filename: {theme}_thumb.jpg
    Returns absolute path.
    """
    out = os.path.join(output_dir, f"{theme}_thumb.jpg")
    path = make_thumbnail(theme=theme, output_path=out)
    return path
