"""
core/story_thumbnail.py — Generador de thumbnails para historias bíblicas narradas.

Pipeline:
  1. Toma imagen dramática de una escena (Scene 10/11/12 típicamente)
  2. Aumenta contraste + saturación
  3. Aplica gradient oscuro en lateral para dar contraste al texto
  4. Quema texto Impact Bold con stroke negro grueso
  5. Output: 1280×720 JPEG

Uso desde render_story.py:
    from core.story_thumbnail import generate_story_thumbnail
    generate_story_thumbnail(
        bg_image=Path("scene_11.jpg"),
        title_text="SIN MIEDO",
        subtitle_text="Historia Bíblica",
        out_path=Path("output/stories/david-goliat/thumbnail.jpg"),
    )
"""
from __future__ import annotations

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# ─── Config ───────────────────────────────────────────────────────────────────
THUMB_W, THUMB_H = 1280, 720

# Fonts (sistema macOS — Impact es estándar)
FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_ARIAL  = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# Tamaños y colores
TITLE_FONT_SIZE     = 160
TITLE_STROKE_WIDTH  = 8
SUBTITLE_FONT_SIZE  = 38
WATERMARK_FONT_SIZE = 32

COLOR_TITLE_FILL    = (255, 255, 255, 255)
COLOR_TITLE_STROKE  = (0, 0, 0, 255)
COLOR_SUBTITLE      = (255, 215, 0, 255)    # dorado
COLOR_WATERMARK     = (255, 255, 255, 200)


def _enhance_image(img: Image.Image) -> Image.Image:
    """Boost contrast + saturation para que el thumbnail destaque en feed."""
    img = ImageEnhance.Contrast(img).enhance(1.25)
    img = ImageEnhance.Color(img).enhance(1.15)
    img = ImageEnhance.Brightness(img).enhance(0.95)
    return img


def _add_dark_gradient(img: Image.Image, side: str = "bottom") -> Image.Image:
    """Añade gradient oscuro para contraste con texto. side: 'bottom'|'left'|'top'."""
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    W, H = img.size

    if side == "bottom":
        # Gradient de transparente arriba a oscuro abajo
        for y in range(H // 2, H):
            alpha = int(220 * ((y - H // 2) / (H // 2)) ** 1.5)
            draw.rectangle([0, y, W, y + 1], fill=(0, 0, 0, min(alpha, 220)))
    elif side == "left":
        for x in range(W // 2):
            alpha = int(200 * ((W // 2 - x) / (W // 2)) ** 1.5)
            draw.rectangle([x, 0, x + 1, H], fill=(0, 0, 0, min(alpha, 200)))

    return Image.alpha_composite(img, overlay).convert("RGB")


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    # Fallback macOS
    for fp in [FONT_IMPACT, FONT_ARIAL, "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def _draw_text_with_stroke(
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    stroke_width: int,
    stroke_fill: tuple,
) -> None:
    """Dibuja texto con stroke pre-fade para mayor legibilidad."""
    draw.text(pos, text, font=font, fill=fill,
              stroke_width=stroke_width, stroke_fill=stroke_fill)


def generate_story_thumbnail(
    bg_image: Path,
    title_text: str,
    subtitle_text: str,
    out_path: Path,
    watermark: str = "@VersiculoDeDios",
) -> Path:
    """
    Genera thumbnail 1280×720 a partir de imagen de escena.

    Args:
        bg_image:      path a JPEG de imagen de escena (1920×1080 típicamente)
        title_text:    2-3 palabras bold en Impact (ej: "SIN MIEDO")
        subtitle_text: línea pequeña bajo título (ej: "Historia Bíblica")
        out_path:      destino del JPEG

    Returns:
        Path al thumbnail generado
    """
    # 1. Cargar y reescalar a 1280×720
    img = Image.open(bg_image).convert("RGB")
    iw, ih = img.size
    target_ratio = THUMB_W / THUMB_H
    src_ratio = iw / ih
    if src_ratio > target_ratio:
        # Más ancho → crop horizontal
        new_w = int(ih * target_ratio)
        offset = (iw - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, ih))
    else:
        # Más alto → crop vertical
        new_h = int(iw / target_ratio)
        offset = (ih - new_h) // 2
        img = img.crop((0, offset, iw, offset + new_h))
    img = img.resize((THUMB_W, THUMB_H), Image.LANCZOS)

    # 2. Boost contraste/saturación
    img = _enhance_image(img)

    # 3. Gradient oscuro abajo
    img = _add_dark_gradient(img, side="bottom")

    # 4. Texto
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    title_font     = _load_font(FONT_IMPACT, TITLE_FONT_SIZE)
    subtitle_font  = _load_font(FONT_ARIAL,  SUBTITLE_FONT_SIZE)
    watermark_font = _load_font(FONT_ARIAL,  WATERMARK_FONT_SIZE)

    # Título centrado, en tercio inferior-medio
    title_text = title_text.upper()
    bbox = draw.textbbox((0, 0), title_text, font=title_font, stroke_width=TITLE_STROKE_WIDTH)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (THUMB_W - tw) // 2
    ty = int(THUMB_H * 0.55)
    _draw_text_with_stroke(
        draw, (tx, ty), title_text, title_font,
        fill=COLOR_TITLE_FILL,
        stroke_width=TITLE_STROKE_WIDTH,
        stroke_fill=COLOR_TITLE_STROKE,
    )

    # Subtítulo bajo título
    sub_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font, stroke_width=2)
    sw = sub_bbox[2] - sub_bbox[0]
    sx = (THUMB_W - sw) // 2
    sy = ty + th + 18
    _draw_text_with_stroke(
        draw, (sx, sy), subtitle_text, subtitle_font,
        fill=COLOR_SUBTITLE, stroke_width=2, stroke_fill=COLOR_TITLE_STROKE,
    )

    # Watermark esquina inferior izquierda
    wm_bbox = draw.textbbox((0, 0), watermark, font=watermark_font, stroke_width=2)
    ww = wm_bbox[2] - wm_bbox[0]
    wh = wm_bbox[3] - wm_bbox[1]
    _draw_text_with_stroke(
        draw, (28, THUMB_H - wh - 26), watermark, watermark_font,
        fill=COLOR_WATERMARK, stroke_width=2, stroke_fill=COLOR_TITLE_STROKE,
    )

    # 5. Save JPEG
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(out_path), "JPEG", quality=92, optimize=True)
    return out_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path imagen de escena")
    parser.add_argument("--title", required=True, help="Título 2-3 palabras")
    parser.add_argument("--subtitle", default="Historia Bíblica")
    parser.add_argument("--out", required=True, help="Path JPEG output")
    args = parser.parse_args()

    out = generate_story_thumbnail(
        bg_image=Path(args.image),
        title_text=args.title,
        subtitle_text=args.subtitle,
        out_path=Path(args.out),
    )
    print(f"Thumbnail listo: {out}")
