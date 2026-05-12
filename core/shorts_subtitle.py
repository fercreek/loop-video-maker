"""
core/shorts_subtitle.py — Generador Pillow de texto para Shorts 1080x1920.

Funciona SIN drawtext/libfreetype en ffmpeg.
Genera PNGs RGBA transparentes por segmento → ffmpeg los overlaya con enable='between'.

Capas generadas:
  - hook_text    : primeros HOOK_DUR segundos (pregunta emocional)
  - verse_label  : todo el video (tema + referencia, esquina superior)
  - subtitles    : segmentos gold con fade (texto oración)
  - cta_text     : últimos CTA_DUR segundos

Pre-flight check:
  verify_text_engine() → RuntimeError si PIL no disponible
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NamedTuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

PROJECT_DIR = Path(__file__).parent.parent

# ─── Canvas Shorts 9:16 ───────────────────────────────────────────────────────
W, H = 1080, 1920

# ─── Fonts ────────────────────────────────────────────────────────────────────
FONT_PATHS = [
    str(PROJECT_DIR / "assets" / "fonts" / "Montserrat-ExtraBold.ttf"),
    "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]

# ─── Colores ──────────────────────────────────────────────────────────────────
GOLD        = (245, 200,  66, 255)   # #F5C842 — subtítulo activo
WHITE       = (255, 255, 255, 255)   # hook + CTA
WHITE_DIM   = (255, 255, 255, 200)   # verse label
BLACK_STROKE= (  0,   0,   0, 255)
PILL_BG     = (  0,   0,   0, 130)   # fondo pill detrás del verse label
WM_COLOR    = (255, 255, 255, 170)   # watermark

# ─── Layout ───────────────────────────────────────────────────────────────────
SUB_Y_RATIO     = 0.80    # subtítulos al 80% del alto
HOOK_Y_RATIO    = 0.42    # hook text al 42%
VERSE_Y         = 100     # verse label en px desde arriba
VERSE_X         = 28      # verse label margen izquierdo
CTA_Y_RATIO     = 0.87    # CTA al 87%
WM_X_PAD        = 28      # watermark padding
WM_Y_PAD        = 60      # watermark desde arriba

# ─── Fuente size ──────────────────────────────────────────────────────────────
SUB_SIZE        = 76
HOOK_SIZE       = 72
VERSE_SIZE      = 36
CTA_SIZE        = 52
WM_SIZE         = 30


class TextLayer(NamedTuple):
    image_path: str
    start_sec: float
    end_sec: float


def verify_text_engine() -> None:
    """Pre-flight: falla rápido si PIL no está disponible."""
    if not PIL_AVAILABLE:
        raise RuntimeError(
            "PIL no disponible — texto imposible.\n"
            "Fix: .venv/bin/pip install Pillow"
        )


def _load_font(size: int) -> "ImageFont.FreeTypeFont":
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _blank() -> "Image.Image":
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def _draw_text_centered(
    draw: "ImageDraw.ImageDraw",
    text: str,
    y_ratio: float,
    font: "ImageFont.FreeTypeFont",
    color: tuple,
    stroke: int = 3,
    alpha_scale: float = 1.0,
) -> None:
    """Dibuja texto centrado horizontalmente con stroke negro."""
    # Multi-line support
    lines = text.split("\n") if "\n" in text else [text]
    line_h = font.size + 8
    total_h = line_h * len(lines)
    y_start = int(H * y_ratio) - total_h // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = y_start + i * line_h

        # Aplicar alpha_scale al color
        r, g, b, a = color
        scaled_color = (r, g, b, int(a * alpha_scale))
        stroke_color = (0, 0, 0, int(255 * alpha_scale))

        draw.text(
            (x, y), line, font=font,
            fill=scaled_color,
            stroke_width=stroke,
            stroke_fill=stroke_color,
        )


def _draw_watermark(draw: "ImageDraw.ImageDraw") -> None:
    font = _load_font(WM_SIZE)
    text = "@VersiculoDeDios"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = W - tw - WM_X_PAD
    draw.text((x, WM_Y_PAD), text, font=font, fill=WM_COLOR, stroke_width=2, stroke_fill=(0,0,0,200))


def _wrap_text(text: str, font: "ImageFont.FreeTypeFont", max_w: int) -> str:
    """Parte texto en líneas que caben en max_w px."""
    words = text.split()
    lines, current = [], ""
    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


# ─── Generadores de capas ─────────────────────────────────────────────────────

def generate_hook_frame(hook_text: str, out_dir: Path, hook_dur: float) -> TextLayer:
    """PNG para hook text — primeros hook_dur segundos."""
    verify_text_engine()
    out_dir.mkdir(parents=True, exist_ok=True)
    img = _blank()
    draw = ImageDraw.Draw(img)
    _draw_watermark(draw)

    font = _load_font(HOOK_SIZE)
    wrapped = _wrap_text(hook_text, font, int(W * 0.85))
    _draw_text_centered(draw, wrapped, HOOK_Y_RATIO, font, WHITE, stroke=3)

    path = out_dir / "hook.png"
    img.save(str(path), "PNG")
    return TextLayer(str(path), 0.0, hook_dur)


def generate_verse_label(verse_text: str, out_dir: Path, duration: float) -> TextLayer:
    """PNG para verse label — todo el video, esquina superior izquierda."""
    verify_text_engine()
    out_dir.mkdir(parents=True, exist_ok=True)
    img = _blank()
    draw = ImageDraw.Draw(img)
    _draw_watermark(draw)

    font = _load_font(VERSE_SIZE)
    text = verse_text.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]

    # Pill background
    pad_h, pad_w = 10, 16
    draw.rounded_rectangle(
        [VERSE_X - pad_w, VERSE_Y - pad_h, VERSE_X + tw + pad_w, VERSE_Y + th + pad_h],
        radius=10, fill=PILL_BG
    )
    draw.text((VERSE_X, VERSE_Y), text, font=font, fill=WHITE_DIM, stroke_width=2, stroke_fill=(0,0,0,200))

    path = out_dir / "verse_label.png"
    img.save(str(path), "PNG")
    return TextLayer(str(path), 0.0, duration)


def generate_subtitle_frames(
    segments: list,  # list[SubtitleSegment]
    out_dir: Path,
    fade_dur: float = 0.18,
    n_fade_steps: int = 3,
) -> list[TextLayer]:
    """
    Genera PNGs por segmento de subtítulo.
    fade_dur: duración del fade-in → genera n_fade_steps frames intermedios.
    """
    verify_text_engine()
    out_dir.mkdir(parents=True, exist_ok=True)
    layers: list[TextLayer] = []
    font = _load_font(SUB_SIZE)

    for idx, seg in enumerate(segments):
        text = seg.text if hasattr(seg, 'text') else seg['text']
        start = seg.start_sec if hasattr(seg, 'start_sec') else seg['start_sec']
        end = seg.end_sec if hasattr(seg, 'end_sec') else seg['end_sec']

        wrapped = _wrap_text(text, font, int(W * 0.88))

        # Frame fade-in (alpha 0.4)
        img_fade = _blank()
        draw_fade = ImageDraw.Draw(img_fade)
        _draw_text_centered(draw_fade, wrapped, SUB_Y_RATIO, font, GOLD, stroke=3, alpha_scale=0.4)
        path_fade = out_dir / f"sub_{idx:03d}_fade.png"
        img_fade.save(str(path_fade), "PNG")

        # Frame full (alpha 1.0)
        img_full = _blank()
        draw_full = ImageDraw.Draw(img_full)
        _draw_text_centered(draw_full, wrapped, SUB_Y_RATIO, font, GOLD, stroke=3, alpha_scale=1.0)
        path_full = out_dir / f"sub_{idx:03d}_full.png"
        img_full.save(str(path_full), "PNG")

        # Fade-in period: usar frame_fade
        fade_end = min(start + fade_dur, end - 0.05)
        layers.append(TextLayer(str(path_fade), start, fade_end))
        # Full period
        layers.append(TextLayer(str(path_full), fade_end, end))

    return layers


def generate_cta_frame(cta_text: str, out_dir: Path, start_sec: float, end_sec: float) -> TextLayer:
    """PNG para CTA — últimos CTA_DUR segundos."""
    verify_text_engine()
    out_dir.mkdir(parents=True, exist_ok=True)
    img = _blank()
    draw = ImageDraw.Draw(img)

    font = _load_font(CTA_SIZE)
    # CTA sin emoji (Pillow no renderiza emoji en todos los sistemas)
    clean = cta_text.replace("🙏", "").strip()
    wrapped = _wrap_text(clean, font, int(W * 0.85))
    _draw_text_centered(draw, wrapped, CTA_Y_RATIO, font, WHITE, stroke=2)

    path = out_dir / "cta.png"
    img.save(str(path), "PNG")
    return TextLayer(str(path), start_sec, end_sec)


def generate_all_layers(
    segments: list,
    out_dir: Path,
    duration: float,
    hook_text: str = "",
    verse_label: str = "",
    cta_text: str = "Comparte si Dios te habló hoy",
    hook_dur: float = 2.2,
    cta_dur: float = 3.5,
) -> list[TextLayer]:
    """
    Genera TODAS las capas de texto para un Short.
    Retorna lista de TextLayer ordenada por start_sec.
    """
    verify_text_engine()
    layers: list[TextLayer] = []

    if verse_label:
        layers.append(generate_verse_label(verse_label, out_dir, duration))

    if hook_text:
        layers.append(generate_hook_frame(hook_text, out_dir, hook_dur))

    sub_layers = generate_subtitle_frames(segments, out_dir)
    layers.extend(sub_layers)

    cta_start = max(0.0, duration - cta_dur)
    layers.append(generate_cta_frame(cta_text, out_dir, cta_start, duration))

    return sorted(layers, key=lambda l: l.start_sec)


def build_text_track(
    layers: list[TextLayer],
    out_dir: Path,
    duration: float,
    fps: int = 30,
) -> Path:
    """
    Genera un video de texto (RGBA PNG frames via concat demuxer).
    Cada frame es la composición de todos los layers activos en ese momento.
    Returns: Path al text_track.mp4

    Performance: 1 overlay en ffmpeg (vs 51 overlays = 24 min → ~40s).
    """
    verify_text_engine()
    frames_dir = out_dir / "txt_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Recopilar todos los timestamps de cambio
    events: set[float] = {0.0, duration}
    for l in layers:
        events.add(l.start_sec)
        events.add(l.end_sec)
    timeline = sorted(events)

    concat_lines: list[str] = []
    seen_states: dict[str, str] = {}  # state_key → png_path

    for i in range(len(timeline) - 1):
        t_start = timeline[i]
        t_end   = timeline[i + 1]
        seg_dur = t_end - t_start
        if seg_dur < 0.001:
            continue

        t_mid = (t_start + t_end) / 2
        # Layers activos en este segmento
        active = [l for l in layers if l.start_sec <= t_mid < l.end_sec]

        state_key = "|".join(l.image_path for l in active)
        if state_key in seen_states:
            png_path = seen_states[state_key]
        else:
            # Componer todos los layers activos
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for layer in active:
                layer_img = Image.open(layer.image_path).convert("RGBA")
                canvas = Image.alpha_composite(canvas, layer_img)
            png_path = str(frames_dir / f"state_{len(seen_states):04d}.png")
            canvas.save(png_path, "PNG")
            seen_states[state_key] = png_path

        abs_png = str(Path(png_path).absolute())
        concat_lines.append(f"file '{abs_png}'")
        concat_lines.append(f"duration {seg_dur:.4f}")

    # Último frame (requerido por ffmpeg concat)
    if concat_lines:
        last_file = concat_lines[-2].split("'")[1]  # already absolute
        concat_lines.append(f"file '{last_file}'")

    concat_path = out_dir / "text_concat.txt"
    concat_path.write_text("\n".join(concat_lines))

    # PNG codec — único que preserva alpha RGBA correctamente en ffmpeg
    text_track = out_dir / "text_track.mkv"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_path),
        "-vf", f"fps={fps},scale={W}:{H}",
        "-c:v", "png",   # lossless, preserva canal alpha
        str(text_track),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"text_track falló: {result.stderr[-500:]}")

    return text_track


def build_overlay_filters(layers: list[TextLayer], base_label: str = "[vvig]") -> tuple[list[str], list[str]]:
    """
    Genera entradas ffmpeg + filtros overlay para las TextLayers.

    Returns:
        (input_args, filter_chains)
        input_args: ["-loop","1","-t","X","-i","path.png", ...] por cada layer
        filter_chains: lista de filtros overlay para filter_complex
    """
    input_args: list[str] = []
    filter_parts: list[str] = []
    current_label = base_label

    # Agrupar por image_path — misma imagen puede tener múltiples rangos de tiempo
    # ffmpeg necesita 1 input por imagen única
    unique_images: dict[str, int] = {}  # path → input_index
    # Los primeros inputs ya están ocupados: 0=img1, 1=narr, 2=img2(opt), 3=music(opt)
    # El índice de start depende de lo que llame el caller — aquí retornamos índice relativo

    relative_idx = 0
    for layer in layers:
        path = layer.image_path
        if path not in unique_images:
            unique_images[path] = relative_idx
            input_args += ["-loop", "1", "-t", f"{layer.end_sec:.3f}", "-i", path]
            relative_idx += 1

    # Construir filtros overlay por layer
    # El caller debe ajustar los índices sumando el offset de inputs previos
    for i, layer in enumerate(layers):
        img_idx_rel = unique_images[layer.image_path]
        next_label = f"[vtxt{i}]" if i < len(layers) - 1 else "[vout]"
        enable = f"between(t,{layer.start_sec:.3f},{layer.end_sec:.3f})"
        flt = (
            f"{current_label}[txt_in_{img_idx_rel}]"
            f"overlay=0:0:enable='{enable}'"
            f"{next_label}"
        )
        filter_parts.append(flt)
        current_label = next_label

    return input_args, filter_parts, unique_images
