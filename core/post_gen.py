"""
core/post_gen.py — Static image post generation (JPG).

Generates 1080×1080 (or other format) images with Fe en Acción style
text overlay for Instagram, Facebook, and other platforms.
"""
from __future__ import annotations

import os
from datetime import datetime

import numpy as np
from PIL import Image

from core.formats import get_dimensions
from core.text_style import render_fea_frame


def generar_post(
    texto: str,
    referencia: str,
    imagen_fondo_path: str,
    output_path: str,
    layout_preset: str = "centrado_bajo",
    format_key: str = "post_1080",
    watermark_text: str = "",
) -> str:
    """
    Generate a static JPG image post with Fe en Acción style text overlay.

    Args:
        texto: Verse text.
        referencia: Bible reference (e.g., "Filipenses 4:7").
        imagen_fondo_path: Path to background image.
        output_path: Where to save the JPG.
        layout_preset: Layout variant (centrado_bajo, centrado_alto, centro_absoluto).
        format_key: Output format (post_1080, etc.).
        watermark_text: Brand watermark text (optional).

    Returns:
        Absolute path to the generated JPG.
    """
    width, height = get_dimensions(format_key)

    # Open and resize/crop background to target dimensions
    bg = Image.open(imagen_fondo_path).convert("RGB")
    bg = _center_crop_resize(bg, width, height)

    # Render Fe en Acción text overlay
    config = {}
    if watermark_text:
        config["watermark_text"] = watermark_text

    text_overlay = render_fea_frame(
        texto, referencia, width, height,
        layout_preset=layout_preset,
        format_key=format_key,
        config_overrides=config,
    )

    # Composite text overlay onto background
    overlay_img = Image.fromarray(text_overlay, "RGBA")
    bg_rgba = bg.convert("RGBA")
    composite = Image.alpha_composite(bg_rgba, overlay_img)
    final = composite.convert("RGB")

    # Save
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    final.save(output_path, quality=95)

    return os.path.abspath(output_path)


def _center_crop_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """
    Resize image maintaining aspect ratio, then center-crop to exact target dimensions.
    """
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # Source is wider — fit height, crop width
        new_h = target_h
        new_w = int(src_w * (target_h / src_h))
    else:
        # Source is taller — fit width, crop height
        new_w = target_w
        new_h = int(src_h * (target_w / src_w))

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))

    return img
