"""
core/subtitle_burn.py — Subtítulos karaoke sincronizados con PIL.

Genera imágenes PNG transparentes por cada word boundary de Edge TTS.
Cada imagen muestra la línea actual con la palabra en curso resaltada en dorado.

Sin drawtext/libass — todo via Pillow. Compatible con cualquier ffmpeg build.

Uso:
    from core.subtitle_burn import generate_subtitle_sequence
    frames = generate_subtitle_sequence(word_boundaries, out_dir, duration)
    # frames → list de {duration_sec, image_path}
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

PROJECT_DIR = Path(__file__).parent.parent

# ─── Config visual ────────────────────────────────────────────────────────────
CANVAS_W, CANVAS_H = 1920, 1080

FONT_SIZE_NORMAL  = 58    # palabras no activas en la línea
FONT_SIZE_ACTIVE  = 64    # palabra activa — ligeramente más grande
STROKE_WIDTH      = 3     # borde negro para legibilidad sobre cualquier fondo

COLOR_ACTIVE   = (255, 215,   0, 255)   # dorado — palabra activa
COLOR_NORMAL   = (255, 255, 255, 255)   # blanco — otras palabras de la línea
COLOR_STROKE   = (  0,   0,   0, 255)   # negro — stroke/shadow
COLOR_BOX      = (  0,   0,   0, 180)   # negro semitransparente — fondo píldora

WORDS_PER_LINE = 5      # cuántas palabras forman una línea de subtítulo
Y_POS_RATIO    = 0.82   # posición vertical (80% de la altura)
BOX_PAD_H      = 18     # padding vertical del fondo
BOX_PAD_W      = 28     # padding horizontal del fondo
BOX_RADIUS     = 14     # radio de bordes redondeados

# Fonts disponibles en el proyecto
FONT_PATHS = [
    str(PROJECT_DIR / "assets" / "fonts" / "Cinzel-Regular.ttf"),     # mejor para subtítulos (caps)
    str(PROJECT_DIR / "assets" / "fonts" / "CormorantGaramond-Regular.ttf"),
    "/System/Library/Fonts/Helvetica.ttc",
]


def _load_font(size: int) -> "ImageFont.FreeTypeFont":
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _group_into_lines(boundaries: list[dict], words_per_line: int = WORDS_PER_LINE) -> list[list[dict]]:
    """Agrupa word boundaries en líneas de subtítulo."""
    lines = []
    for i in range(0, len(boundaries), words_per_line):
        lines.append(boundaries[i:i + words_per_line])
    return lines


WATERMARK_TEXT  = "@VersiculoDeDios"
WATERMARK_FONT_SIZE = 26
WATERMARK_COLOR = (255, 255, 255, 153)   # blanco @ 60% opacidad
WATERMARK_X_PAD = 30
WATERMARK_Y_PAD = 22


def _draw_watermark(draw: "ImageDraw.ImageDraw", canvas_size: tuple[int, int]) -> None:
    """Dibuja watermark en esquina inferior derecha."""
    font = _load_font(WATERMARK_FONT_SIZE)
    tw = int(draw.textlength(WATERMARK_TEXT, font=font))
    W, H = canvas_size
    x = W - tw - WATERMARK_X_PAD
    y = H - WATERMARK_FONT_SIZE - WATERMARK_Y_PAD
    draw.text(
        (x, y), WATERMARK_TEXT, font=font,
        fill=WATERMARK_COLOR,
        stroke_width=2, stroke_fill=(0, 0, 0, 200),
    )


def _make_subtitle_frame(
    line_words: list[dict],
    active_idx: int,
    canvas_size: tuple[int, int] = (CANVAS_W, CANVAS_H),
) -> "Image.Image":
    """
    Genera imagen RGBA transparente con la línea de subtítulo + watermark.
    La palabra en active_idx aparece en dorado, el resto en blanco.
    """
    img = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _draw_watermark(draw, canvas_size)

    font_normal = _load_font(FONT_SIZE_NORMAL)
    font_active = _load_font(FONT_SIZE_ACTIVE)

    W, H = canvas_size
    cy = int(H * Y_POS_RATIO)

    # Construir piezas de texto con su font y color
    pieces: list[tuple[str, Any, tuple]] = []
    for i, w in enumerate(line_words):
        word = w["word"].strip()
        if not word:
            continue
        is_active = (i == active_idx)
        font  = font_active if is_active else font_normal
        color = COLOR_ACTIVE if is_active else COLOR_NORMAL
        pieces.append((word, font, color))

    if not pieces:
        return img

    # Medir ancho total (incluyendo espacios entre palabras)
    space_w = int(draw.textlength(" ", font=font_normal))
    total_w = sum(int(draw.textlength(p[0], font=p[1])) for p in pieces) + space_w * (len(pieces) - 1)

    # Posición inicial X (centrado)
    x = (W - total_w) // 2

    # Calcular altura máxima de línea
    line_h = max(FONT_SIZE_ACTIVE, FONT_SIZE_NORMAL) + 8

    # Dibujar fondo semitransparente (píldora)
    box_x0 = x - BOX_PAD_W
    box_x1 = x + total_w + BOX_PAD_W
    box_y0 = cy - BOX_PAD_H
    box_y1 = cy + line_h + BOX_PAD_H
    draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=BOX_RADIUS, fill=COLOR_BOX)

    # Dibujar cada palabra con stroke (negro) + fill (blanco/dorado)
    cursor_x = x
    for word, font, color in pieces:
        w_w = int(draw.textlength(word, font=font))
        draw.text(
            (cursor_x, cy),
            word,
            font=font,
            fill=color,
            stroke_width=STROKE_WIDTH,
            stroke_fill=COLOR_STROKE,
        )
        cursor_x += w_w + space_w

    return img


def generate_subtitle_sequence(
    word_boundaries: list[dict],
    out_dir: Path,
    total_duration: float,
    words_per_line: int = WORDS_PER_LINE,
) -> list[dict]:
    """
    Genera secuencia de imágenes de subtítulo para ffmpeg concat demuxer.

    Args:
        word_boundaries: [{word, offset_sec, duration_sec}, ...]
        out_dir:         directorio donde guardar PNGs
        total_duration:  duración total del clip en segundos
        words_per_line:  cuántas palabras por línea

    Returns:
        list de {duration_sec, image_path} — listo para concat demuxer
    """
    if not PIL_AVAILABLE:
        raise RuntimeError("PIL no disponible. Run: .venv/bin/pip install Pillow")

    out_dir.mkdir(parents=True, exist_ok=True)

    # Imagen en blanco para gaps — solo watermark, sin texto subtítulo
    blank = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    _draw_watermark(ImageDraw.Draw(blank), (CANVAS_W, CANVAS_H))
    blank_path = out_dir / "sub_blank.png"
    blank.save(str(blank_path), "PNG")

    frames: list[dict] = []
    lines = _group_into_lines(word_boundaries, words_per_line)

    # Gap inicial antes del primer word
    if word_boundaries:
        first_start = word_boundaries[0]["offset_sec"]
        if first_start > 0.1:
            frames.append({"duration_sec": first_start, "image_path": str(blank_path)})

    frame_idx = 0
    for line_words in lines:
        for word_idx, word in enumerate(line_words):
            img = _make_subtitle_frame(line_words, word_idx)
            img_path = out_dir / f"sub_{frame_idx:04d}.png"
            img.save(str(img_path), "PNG")

            MIN_FRAME = 1.0 / 12   # 1 frame @ 12fps = 0.0833s — evita flicker sub-frame
            frames.append({
                "duration_sec": max(MIN_FRAME, word["duration_sec"]),
                "image_path": str(img_path),
            })
            frame_idx += 1

    # Gap final hasta el total_duration
    if frames:
        covered = sum(f["duration_sec"] for f in frames)
        remaining = total_duration - covered
        if remaining > 0.1:
            frames.append({"duration_sec": remaining, "image_path": str(blank_path)})

    return frames


def write_concat_file(frames: list[dict], concat_path: Path) -> None:
    """Escribe archivo de concat demuxer para ffmpeg."""
    with open(concat_path, "w") as f:
        for frame in frames:
            img_path = Path(frame["image_path"]).absolute()
            f.write(f"file '{img_path}'\n")
            f.write(f"duration {frame['duration_sec']:.4f}\n")
        # ffmpeg concat demuxer requiere el último archivo repetido sin duration
        if frames:
            last_path = Path(frames[-1]["image_path"]).absolute()
            f.write(f"file '{last_path}'\n")
