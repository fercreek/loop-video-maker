"""
core/thumbnail_gen.py — YouTube thumbnail generator for VersiculoDeDios.

Produces 1280×720 JPEG thumbnails with:
  - Oil painting background with left-zone dark gradient
  - Impact bold title (accent line 1, white line 2)
  - Colored glow halo behind title text
  - Thin accent left bar
  - Subtitle with auto-wrap
  - Accent divider line
  - Channel watermark
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── Constants ────────────────────────────────────────────────────────────────

THUMB_SIZE  = (1280, 720)
FONT_BOLD   = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_SUB    = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
CHANNEL_TAG = "@VersiculoDeDios"

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

# Copy override for 120-min (Template B, sleep/rest angle)
COPY_120MIN: dict[str, dict] = {
    "fe":        {"title": "¡FE QUE MUEVE\nMONTAÑAS! 2H",  "subtitle": "Música Cristiana · 2 Horas de Adoración"},
    "amor":      {"title": "¡EL AMOR\nDE DIOS! 2H",         "subtitle": "Música Suave para Descansar en Su Amor"},
    "esperanza": {"title": "¡ESPERANZA\nEN DIOS! 2H",        "subtitle": "Música para Dormir con Paz y Esperanza"},
    "fuerza":    {"title": "¡FUERZA\nEN DIOS! 2H",           "subtitle": "Música para Restaurarte mientras Duermes"},
    "gratitud":  {"title": "¡GRATITUD\nA DIOS! 2H",          "subtitle": "Música para Alabar mientras Descansas"},
    "paz":       {"title": "¡PAZ SOBRENATURAL!\n2 HORAS",    "subtitle": "Música para Dormir y Descansar en Dios"},
    "salmos":    {"title": "¡SALMOS DE\nADORACIÓN! 2H",      "subtitle": "Música para Orar y Descansar en Dios"},
    "victoria":  {"title": "¡VICTORIA\nEN CRISTO! 2H",       "subtitle": "Música para Dormir como Vencedor"},
}

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


# ─── Template B helpers ───────────────────────────────────────────────────────

def _make_thumbnail_b(
    theme: str, output_path: str,
    title: str, subtitle: str,
    bg_abs: str, accent: tuple, channel: str,
) -> str:
    """
    Template B — Centered layout / meditación / sleep.

    Layout:
    - Full-bleed background with radial dark vignette (center stays bright)
    - Title CENTERED, 110px Impact — accent line 1, white line 2
    - Centered subtitle below
    - Horizontal accent bar under subtitle (centered)
    - 60min / 120min badge top-right
    - Channel tag bottom-right
    No arrow — clean, minimal energy for sleep/relaxation audience.
    """
    W, H = THUMB_SIZE

    bg = Image.open(bg_abs).convert("RGB").resize((W, H), Image.LANCZOS)

    # Radial vignette — edges dark, center brighter
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    cx_v, cy_v = W // 2, H // 2
    max_r = (W**2 + H**2) ** 0.5 / 2
    for x in range(0, W, 2):
        for y in range(0, H, 2):
            r = ((x - cx_v)**2 + (y - cy_v)**2) ** 0.5
            t = r / max_r
            alpha = int(200 * t * t)
            ov_draw.point([(x, y), (x+1, y), (x, y+1), (x+1, y+1)],
                          fill=(0, 0, 0, alpha))
    canvas = Image.alpha_composite(bg.convert("RGBA"), overlay)

    try:
        font_title = ImageFont.truetype(FONT_BOLD, 110)
        font_sub   = ImageFont.truetype(FONT_SUB,  40)
        font_ch    = ImageFont.truetype(FONT_SUB,  30)
    except Exception:
        font_title = font_sub = font_ch = ImageFont.load_default()

    title_lines  = title.split("\n")
    tmp_draw     = ImageDraw.Draw(canvas)
    line_heights = [tmp_draw.textbbox((0, 0), ln, font=font_title)[3]
                    - tmp_draw.textbbox((0, 0), ln, font=font_title)[1]
                    for ln in title_lines]
    total_title_h = sum(line_heights) + 12 * (len(title_lines) - 1)

    title_block_top = H // 2 - total_title_h // 2 - 40

    # Glow layer
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    y = title_block_top
    for i, line in enumerate(title_lines):
        bbox = glow_draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        glow_draw.text((W // 2 - lw // 2, y), line, font=font_title, fill=(*accent, 170))
        y += line_heights[i] + 12
    glow = glow.filter(ImageFilter.GaussianBlur(radius=22))
    canvas = Image.alpha_composite(canvas, glow)

    composite = canvas.convert("RGB")
    draw = ImageDraw.Draw(composite)

    # Title centered
    y = title_block_top
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        _outlined_text(draw, (W // 2 - lw // 2, y), line,
                       font=font_title,
                       fill=accent if i == 0 else (255, 255, 255),
                       stroke_w=7)
        y += line_heights[i] + 12

    # Subtitle centered
    sub_y = y + 18
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw = bbox[2] - bbox[0]
    _outlined_text(draw, (W // 2 - sw // 2, sub_y), subtitle,
                   font=font_sub, fill=(220, 220, 220), stroke_w=3)

    # Horizontal accent bar centered
    bar_y = int(sub_y + 48)
    draw.rectangle([(W // 2 - 180, bar_y), (W // 2 + 180, bar_y + 5)], fill=accent)

    # Channel bottom-right
    bbox = draw.textbbox((0, 0), channel, font=font_ch)
    cw = bbox[2] - bbox[0]
    _outlined_text(draw, (W - cw - 28, H - 44), channel,
                   font=font_ch, fill=(255, 255, 255), stroke_w=3)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    composite.save(output_path, "JPEG", quality=95)
    return output_path


def _make_thumbnail_c(
    theme: str, output_path: str,
    title: str, subtitle: str,
    bg_abs: str, accent: tuple, channel: str,
) -> str:
    """
    Template C — Bottom-third / modern / impact-first.

    Layout:
    - Large oil painting dominates top 60% (attracts eye, no text)
    - Bottom strip: dark gradient, huge title (left-aligned), no subtitle
    - Top accent color pill badge (e.g. "60 MIN BÍBLICO")
    - Accent left bar (4px)
    High CTR variant for viewers who respond to bold bottom-text overlays.
    """
    W, H = THUMB_SIZE
    split_y = int(H * 0.52)    # painting above, text strip below

    bg = Image.open(bg_abs).convert("RGB").resize((W, H), Image.LANCZOS)

    # Full-bleed bottom darkening (split_y downward)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for y in range(split_y, H):
        t = (y - split_y) / (H - split_y)
        alpha = int(220 * (0.4 + 0.6 * t))
        ov_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    # Subtle top vignette
    for y in range(0, int(H * 0.15)):
        t = 1.0 - y / (H * 0.15)
        ov_draw.line([(0, y), (W, y)], fill=(0, 0, 0, int(80 * t)))

    canvas = Image.alpha_composite(bg.convert("RGBA"), overlay)

    try:
        font_huge  = ImageFont.truetype(FONT_BOLD, 115)
        font_badge = ImageFont.truetype(FONT_SUB,  30)
        font_ch    = ImageFont.truetype(FONT_SUB,  28)
    except Exception:
        font_huge = font_badge = font_ch = ImageFont.load_default()

    # Glow layer — title only
    title_lines  = title.split("\n")
    tmp_draw     = ImageDraw.Draw(canvas)
    line_heights = [tmp_draw.textbbox((0, 0), ln, font=font_huge)[3]
                    - tmp_draw.textbbox((0, 0), ln, font=font_huge)[1]
                    for ln in title_lines]
    total_title_h = sum(line_heights) + 10 * (len(title_lines) - 1)
    title_y = H - total_title_h - 64

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    y = title_y
    for i, line in enumerate(title_lines):
        glow_draw.text((60, y), line, font=font_huge, fill=(*accent, 170))
        y += line_heights[i] + 10
    glow = glow.filter(ImageFilter.GaussianBlur(radius=20))
    canvas = Image.alpha_composite(canvas, glow)

    composite = canvas.convert("RGB")
    draw = ImageDraw.Draw(composite)

    # Accent left bar (4px)
    draw.rectangle([(0, 0), (4, H)], fill=accent)

    # Title bottom-aligned, left
    y = title_y
    for i, line in enumerate(title_lines):
        _outlined_text(draw, (64, y), line, font=font_huge,
                       fill=accent if i == 0 else (255, 255, 255),
                       stroke_w=6)
        y += line_heights[i] + 10

    # Accent badge pill top-left
    badge_text = subtitle[:28] if subtitle else "VERSÍCULOS BÍBLICOS"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0] + 28
    bh = bbox[3] - bbox[1] + 14
    draw.rounded_rectangle([(50, 22), (50 + bw, 22 + bh)],
                            radius=8, fill=(*accent, 220))
    draw.text((64, 22 + 7), badge_text, font=font_badge, fill=(0, 0, 0))

    # Channel bottom-right
    bbox = draw.textbbox((0, 0), channel, font=font_ch)
    cw = bbox[2] - bbox[0]
    _outlined_text(draw, (W - cw - 28, H - 38), channel,
                   font=font_ch, fill=(255, 255, 255), stroke_w=3)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    composite.save(output_path, "JPEG", quality=95)
    return output_path


# ─── Core function ────────────────────────────────────────────────────────────

def make_thumbnail(
    theme: str,
    output_path: str,
    title: str | None = None,
    subtitle: str | None = None,
    bg_path: str | None = None,
    accent_hex: str | None = None,
    channel: str = CHANNEL_TAG,
    template: str = "A",
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
        template:    "A" (default, left-aligned), "B" (centered/sleep),
                     "C" (bottom-third/modern). Used for A/B CTR testing.

    Returns:
        output_path
    """
    copy     = THEME_COPY.get(theme, {"title": theme.upper(), "subtitle": ""})
    title    = title    or copy["title"]
    subtitle = subtitle or copy["subtitle"]
    bg_rel   = bg_path or THEME_BG.get(theme, "output/fondos/fondo_light.jpg")
    bg_abs   = bg_rel if os.path.isabs(bg_rel) else os.path.join(PROJECT_DIR, bg_rel)
    accent   = _hex(accent_hex or THEME_ACCENT.get(theme, "#FFD700"))

    # Dispatch to template-specific renderer
    if template == "B":
        return _make_thumbnail_b(theme, output_path, title, subtitle, bg_abs, accent, channel)
    if template == "C":
        return _make_thumbnail_c(theme, output_path, title, subtitle, bg_abs, accent, channel)

    # Template A (original) — continue below
    W, H = THUMB_SIZE

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

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    composite.save(output_path, "JPEG", quality=95)
    return output_path


def generate_thumbnail_for_theme(theme: str, output_dir: str, all_variants: bool = False) -> str:
    """
    Generate thumbnail(s) for theme into output_dir.

    Default (all_variants=False): generates template A only → {theme}_thumb.jpg
    With all_variants=True: generates A + B + C:
        {theme}_thumb.jpg       ← Template A (canonical, left-aligned)
        {theme}_thumb_b.jpg     ← Template B (centered/sleep)
        {theme}_thumb_c.jpg     ← Template C (bottom-third/modern)

    Returns absolute path of primary thumbnail (template A).
    """
    out_a = os.path.join(output_dir, f"{theme}_thumb.jpg")
    make_thumbnail(theme=theme, output_path=out_a, template="A")
    if all_variants:
        make_thumbnail(theme=theme, output_path=os.path.join(output_dir, f"{theme}_thumb_b.jpg"),
                       template="B")
        make_thumbnail(theme=theme, output_path=os.path.join(output_dir, f"{theme}_thumb_c.jpg"),
                       template="C")
    return out_a
