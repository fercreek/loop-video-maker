"""
core/formats.py — Format definitions, layout presets, and Fe en Acción palette.

Centralized constants used by video_render, image_gen, post_gen, batch_gen, and the UI.
"""
from __future__ import annotations


# ─── Output format definitions ────────────────────────────────────────────────

FORMAT_DEFS = {
    "post_1080": {
        "width": 1080,
        "height": 1080,
        "aspect": "1:1",
        "output_type": "image",
        "font_scale": 1.0,
        "label": "Post 1:1 (Instagram/Facebook)",
    },
    "reel_1080": {
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "output_type": "video",
        "font_scale": 0.85,
        "label": "Reel 9:16 (Instagram/TikTok/Shorts)",
    },
    "youtube_1080": {
        "width": 1920,
        "height": 1080,
        "aspect": "16:9",
        "output_type": "video",
        "font_scale": 1.0,
        "label": "YouTube 16:9",
    },
}


# ─── Layout presets (Fe en Acción style) ──────────────────────────────────────

LAYOUT_PRESETS = {
    "centrado_bajo": {
        "label": "Centrado bajo",
        "label_y": 0.38,
        "verse_y": 0.52,
        "ref_gap": 28,
        "brand_y": 0.96,
        "ornament_top": True,
        "ornament_divider": True,
    },
    "centrado_alto": {
        "label": "Centrado alto",
        "label_y": 0.20,
        "verse_y": 0.32,
        "ref_gap": 28,
        "brand_y": 0.96,
        "ornament_top": True,
        "ornament_divider": True,
    },
    "centro_absoluto": {
        "label": "Centro absoluto",
        "label_y": 0.34,
        "verse_y": 0.48,
        "ref_gap": 24,
        "brand_y": 0.94,
        "ornament_top": True,
        "ornament_divider": True,
    },
}


# ─── Fe en Acción color palette ───────────────────────────────────────────────

FEA_PALETTE = {
    # Gold accents
    "gold_primary": "#c9a84c",
    "gold_soft": "#e8d5a3",
    "gold_sparkle": "#f5e080",
    # Gold RGBA tuples for Pillow drawing
    "gold_primary_rgba": (201, 168, 76, 255),
    "gold_soft_rgba": (232, 213, 163, 255),
    "gold_sparkle_rgba": (245, 224, 128, 255),
    "gold_semi_rgba": (201, 168, 76, 100),
    # Text
    "verse_text": "#ffffff",
    "ref_text": "#c9a84c",
    "brand_text": (201, 168, 76, 100),
    # Shadows
    "shadow_rgba": (0, 0, 0, 200),
    "shadow_ref_rgba": (0, 0, 0, 150),
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_dimensions(format_key: str) -> tuple[int, int]:
    """Return (width, height) for the given format key."""
    fmt = FORMAT_DEFS.get(format_key, FORMAT_DEFS["youtube_1080"])
    return fmt["width"], fmt["height"]


def get_font_size(base_size: int, format_key: str) -> int:
    """Scale a base font size by the format's font_scale factor."""
    fmt = FORMAT_DEFS.get(format_key, FORMAT_DEFS["youtube_1080"])
    return int(base_size * fmt["font_scale"])


def get_layout(preset_key: str) -> dict:
    """Return layout preset dict, defaulting to centrado_bajo."""
    return LAYOUT_PRESETS.get(preset_key, LAYOUT_PRESETS["centrado_bajo"])
