"""
core/text_style.py — VersiculoDeDios text overlay renderer.

Renders RGBA text frames with gold ornaments, diamond separators,
letter-spaced labels, and elegant typography for biblical verse content.
Also provides the legacy simple renderer for backward compatibility.
"""
from __future__ import annotations

import functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from core.formats import (
    FEA_PALETTE,
    LAYOUT_PRESETS,
    get_font_size,
    get_layout,
)

# ─── Font paths ───────────────────────────────────────────────────────────────

FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"
FONT_VERSE = FONTS_DIR / "CormorantGaramond-Italic.ttf"
FONT_REF = FONTS_DIR / "Cinzel-Regular.ttf"

SYSTEM_FONTS = [
    "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
    "/System/Library/Fonts/Times.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "C:/Windows/Fonts/timesi.ttf",
]

SYSTEM_FONTS_REF = [
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/System/Library/Fonts/Times.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "C:/Windows/Fonts/times.ttf",
]


# ─── Font loading ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=32)
def _get_font(font_path: Path, fallbacks: tuple, size: int) -> ImageFont.FreeTypeFont:
    """Load font with system fallback chain. Cached — same font+size loaded once per process."""
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    for fb in fallbacks:
        try:
            if Path(fb).exists():
                return ImageFont.truetype(fb, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _get_font_list(font_path: Path, fallbacks: list, size: int) -> ImageFont.FreeTypeFont:
    """Convenience wrapper — accepts list fallbacks (converts to tuple for cache key)."""
    return _get_font(font_path, tuple(fallbacks), size)


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    """Wrap text so it doesn't exceed max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


# ─── VersiculoDeDios style renderer ──────────────────────────────────────────────

# Base font sizes (for 1080×1080 post format)
_BASE_LABEL_SIZE = 18
_BASE_VERSE_SIZE = 72   # was 58 — too small for 1920×1080 YouTube (bumped for readability)
_BASE_REF_SIZE = 30
_BASE_BRAND_SIZE = 14

# Ornament dimensions (scaled proportionally)
_DIAMOND_SIZE = 8
_LINE_LENGTH = 50
_LINE_THICKNESS = 1
_TOP_LINE_LENGTH = 120
_LETTER_SPACING = 8


def render_fea_frame(
    texto: str,
    referencia: str,
    width: int,
    height: int,
    layout_preset: str = "centrado_bajo",
    format_key: str = "post_1080",
    config_overrides: dict | None = None,
) -> np.ndarray:
    """
    Render a VersiculoDeDios style RGBA text overlay.

    Returns numpy array (height, width, 4) with alpha channel.
    """
    cfg = config_overrides or {}
    layout = get_layout(layout_preset)
    palette = FEA_PALETTE

    # Scale factor relative to 1080 base
    scale = min(width, height) / 1080.0

    # Font sizes scaled by format and canvas
    label_size = get_font_size(int(_BASE_LABEL_SIZE * scale), format_key)
    verse_size = cfg.get("tamano", None)
    if verse_size is None:
        verse_size = get_font_size(int(_BASE_VERSE_SIZE * scale), format_key)
    else:
        verse_size = get_font_size(int(verse_size * scale / (1920 / 1080)), format_key)
    ref_size = get_font_size(int(_BASE_REF_SIZE * scale), format_key)
    brand_size = get_font_size(int(_BASE_BRAND_SIZE * scale), format_key)

    # Ornament scaling
    diamond_size = int(_DIAMOND_SIZE * scale)
    line_length = int(_LINE_LENGTH * scale)
    top_line_length = int(_TOP_LINE_LENGTH * scale)
    letter_spacing = int(_LETTER_SPACING * scale)
    ref_gap = int(layout["ref_gap"] * scale)

    # Load fonts
    font_label = _get_font(FONT_REF, tuple(SYSTEM_FONTS_REF), max(label_size, 10))
    font_verse = _get_font(FONT_VERSE, tuple(SYSTEM_FONTS), max(verse_size, 16))
    font_ref = _get_font(FONT_REF, tuple(SYSTEM_FONTS_REF), max(ref_size, 12))
    font_brand = _get_font(FONT_REF, tuple(SYSTEM_FONTS_REF), max(brand_size, 8))

    # Create transparent RGBA canvas
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    align = layout.get("align", "center")
    is_left = align == "left"

    center_x = width // 2
    max_text_width = int(width * (layout.get("text_width", 0.72) if is_left else 0.72))
    text_x_base = int(width * layout.get("left_margin", 0.12)) if is_left else None

    # Colors
    gold = palette["gold_primary_rgba"]
    gold_soft = palette["gold_soft_rgba"]
    white = palette["verse_text"]
    shadow_color = palette["shadow_rgba"]
    shadow_ref = palette["shadow_ref_rgba"]
    brand_color = palette["brand_text"]

    # ── 0. Vertical gold accent bar (lateral template) ──────────────────────
    if is_left and layout.get("show_vertical_bar", False):
        bar_x = int(width * layout.get("bar_x", 0.09))
        bar_top = int(height * (layout["verse_y"] - 0.04))
        bar_thick = max(2, int(4 * scale))
        bar_len = int(height * 0.36)
        for dy in range(bar_len):
            t = dy / bar_len
            # Fade in at top 15%, full in middle, fade out at bottom 15%
            if t < 0.15:
                alpha = int(gold[3] * (t / 0.15))
            elif t > 0.85:
                alpha = int(gold[3] * ((1.0 - t) / 0.15))
            else:
                alpha = gold[3]
            c = (gold[0], gold[1], gold[2], alpha)
            draw.line(
                [(bar_x, bar_top + dy), (bar_x + bar_thick, bar_top + dy)],
                fill=c,
            )

    # ── 1. "VERSÍCULO DEL DÍA" label (centered template only) ───────────────
    if layout.get("show_label", True):
        label_text = cfg.get("label_text", "VERSÍCULO DEL DÍA")
        label_y = int(height * layout["label_y"])

        if layout.get("ornament_top", False):
            _render_gold_line(draw, center_x, label_y - int(16 * scale),
                              top_line_length, scale, gold)

        _render_letter_spaced(draw, label_text, font_label,
                              center_x, label_y, letter_spacing, gold)

    # ── 2. Verse text ────────────────────────────────────────────────────────
    verse_y = int(height * layout["verse_y"])
    wrapped = _wrap_text(draw, texto, font_verse, max_text_width)

    text_bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_verse)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    if is_left:
        text_x = text_x_base
        pil_align = "left"
    else:
        text_x = (width - text_w) // 2
        pil_align = "center"

    # Shadow
    draw.multiline_text(
        (text_x + 2, verse_y + 3), wrapped,
        font=font_verse, fill=shadow_color, align=pil_align,
    )
    # Main verse text
    draw.multiline_text(
        (text_x, verse_y), wrapped,
        font=font_verse, fill=white, align=pil_align,
    )

    # ── 3. Separator + Reference ─────────────────────────────────────────────
    if referencia:
        sep_y = verse_y + text_h + ref_gap

        if not is_left and layout.get("ornament_divider", False):
            # Centered diamond + lines
            _render_diamond(draw, center_x, sep_y, diamond_size, gold)
            _render_gold_line(draw, center_x - diamond_size - 8 - line_length,
                              sep_y, line_length, scale, gold, direction="right")
            _render_gold_line(draw, center_x + diamond_size + 8,
                              sep_y, line_length, scale, gold, direction="left")
            ref_y = sep_y + int(16 * scale)
        else:
            ref_y = sep_y

        ref_text = f"— {referencia} —" if not is_left else referencia.upper()
        ref_bbox = draw.textbbox((0, 0), ref_text, font=font_ref)
        ref_w = ref_bbox[2] - ref_bbox[0]
        ref_x = text_x_base if is_left else (width - ref_w) // 2

        draw.text(
            (ref_x + 1, ref_y + 2), ref_text,
            font=font_ref, fill=shadow_ref,
        )
        draw.text(
            (ref_x, ref_y), ref_text,
            font=font_ref, fill=gold_soft,
        )

    # ── 4. Brand watermark ───────────────────────────────────────────────────
    watermark = cfg.get("watermark_text", "")
    if watermark:
        brand_y = int(height * layout["brand_y"])
        brand_text = watermark.upper()
        if is_left:
            # Left-aligned watermark
            bx = text_x_base
            draw.text((bx, brand_y), brand_text, font=font_brand, fill=brand_color)
        else:
            _render_letter_spaced(draw, brand_text, font_brand,
                                  center_x, brand_y, int(4 * scale), brand_color)

    return np.array(img)


# ─── Simple style renderer (backward compatible) ─────────────────────────────

def render_simple_frame(
    texto: str,
    referencia: str,
    width: int,
    height: int,
    config: dict,
) -> np.ndarray:
    """
    Legacy text frame renderer — matches the original _render_text_frame()
    behavior with rounded-rect background, simple separator line, and
    top/center/bottom positioning.

    Returns numpy array (height, width, 4) with alpha channel.
    """
    font_size = config.get("tamano", 52)
    color_texto = config.get("color_texto", "#FFFFFF")
    color_ref = config.get("color_referencia", "#E8D5A3")
    posicion = config.get("posicion", "bottom")
    mostrar_ref = config.get("mostrar_referencia", True)

    font_verse = _get_font(FONT_VERSE, tuple(SYSTEM_FONTS), font_size)
    font_ref = _get_font(FONT_REF, tuple(SYSTEM_FONTS_REF), int(font_size * 0.54))

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    max_text_width = int(width * 0.75)
    wrapped = _wrap_text(draw, texto, font_verse, max_text_width)

    text_bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_verse)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    ref_text = f"— {referencia} —" if mostrar_ref else ""
    ref_h = 0
    separator_h = 0
    if mostrar_ref and referencia:
        ref_bbox = draw.textbbox((0, 0), ref_text, font=font_ref)
        ref_h = ref_bbox[3] - ref_bbox[1]
        separator_h = 32

    total_content_h = text_h + separator_h + ref_h

    if posicion == "top":
        y_start = int(height * 0.08)
    elif posicion == "center":
        y_start = (height - total_content_h) // 2
    else:
        y_start = height - total_content_h - int(height * 0.08)

    padding = 24
    bg_left = (width - max(text_w, 200)) // 2 - padding
    bg_top = y_start - padding
    bg_right = (width + max(text_w, 200)) // 2 + padding
    bg_bottom = y_start + total_content_h + padding

    shadow_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_draw.rounded_rectangle(
        [bg_left, bg_top, bg_right, bg_bottom],
        radius=12,
        fill=(0, 0, 0, 102),
    )
    img = Image.alpha_composite(img, shadow_img)
    draw = ImageDraw.Draw(img)

    x_text = (width - text_w) // 2
    draw.multiline_text(
        (x_text + 2, y_start + 2), wrapped,
        font=font_verse, fill=(0, 0, 0, 180), align="center",
    )
    draw.multiline_text(
        (x_text, y_start), wrapped,
        font=font_verse, fill=color_texto, align="center",
    )

    if mostrar_ref and referencia:
        sep_y = y_start + text_h + 12
        sep_x = width // 2
        draw.line(
            [(sep_x - 30, sep_y), (sep_x + 30, sep_y)],
            fill=color_ref, width=1,
        )

        ref_bbox = draw.textbbox((0, 0), ref_text, font=font_ref)
        ref_w = ref_bbox[2] - ref_bbox[0]
        ref_x = (width - ref_w) // 2
        ref_y = sep_y + 12
        draw.text(
            (ref_x + 1, ref_y + 1), ref_text,
            font=font_ref, fill=(0, 0, 0, 150),
        )
        draw.text(
            (ref_x, ref_y), ref_text,
            font=font_ref, fill=color_ref,
        )

    return np.array(img)


# ─── Drawing helpers ──────────────────────────────────────────────────────────

def _render_letter_spaced(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    center_x: int,
    y: int,
    spacing: int,
    fill,
) -> None:
    """Render text centered at center_x with custom letter spacing."""
    # Measure total width with spacing
    total_width = 0
    char_widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        w = bbox[2] - bbox[0]
        char_widths.append(w)
        total_width += w
    total_width += spacing * max(0, len(text) - 1)

    # Draw each character
    x = center_x - total_width // 2
    for i, ch in enumerate(text):
        draw.text((x, y), ch, font=font, fill=fill)
        x += char_widths[i] + spacing


def _render_gold_line(
    draw: ImageDraw.ImageDraw,
    x_start: int,
    y: int,
    length: int,
    scale: float,
    color: tuple,
    direction: str = "center",
) -> None:
    """
    Render a gold horizontal line with gradient fade at the edges.
    Uses multiple segments with decreasing alpha for the fade effect.
    """
    if length <= 0:
        return

    thickness = max(1, int(_LINE_THICKNESS * scale))
    segments = max(8, length // 4)

    if direction == "center":
        # Fade from edges to center (for top ornament line)
        half = length // 2
        left_start = x_start - half
        for i in range(segments):
            t = i / segments
            # Fade in from left, fade out to right
            if t < 0.3:
                alpha = int(color[3] * (t / 0.3))
            elif t > 0.7:
                alpha = int(color[3] * ((1.0 - t) / 0.3))
            else:
                alpha = color[3]
            seg_x = left_start + int(length * t)
            seg_x2 = left_start + int(length * (t + 1.0 / segments))
            c = (color[0], color[1], color[2], alpha)
            draw.line([(seg_x, y), (seg_x2, y)], fill=c, width=thickness)
    elif direction == "right":
        # Fade from left (transparent) to right (opaque)
        for i in range(segments):
            t = i / segments
            alpha = int(color[3] * t)
            seg_x = x_start + int(length * t)
            seg_x2 = x_start + int(length * (t + 1.0 / segments))
            c = (color[0], color[1], color[2], alpha)
            draw.line([(seg_x, y), (seg_x2, y)], fill=c, width=thickness)
    elif direction == "left":
        # Fade from left (opaque) to right (transparent)
        for i in range(segments):
            t = i / segments
            alpha = int(color[3] * (1.0 - t))
            seg_x = x_start + int(length * t)
            seg_x2 = x_start + int(length * (t + 1.0 / segments))
            c = (color[0], color[1], color[2], alpha)
            draw.line([(seg_x, y), (seg_x2, y)], fill=c, width=thickness)


def _render_diamond(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    size: int,
    fill_color: tuple,
) -> None:
    """Render a small rotated-45° diamond (rhombus) at the given center point."""
    points = [
        (center_x, center_y - size),      # top
        (center_x + size, center_y),       # right
        (center_x, center_y + size),       # bottom
        (center_x - size, center_y),       # left
    ]
    draw.polygon(points, fill=fill_color)
