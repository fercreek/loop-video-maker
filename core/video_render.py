"""
Renderizado de video con MoviePy 2.x + Pillow.
Genera .mp4 1920x1080 con versículos bíblicos sobre imagen de fondo.
"""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)

# Paths de fonts
FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"
FONT_VERSE = FONTS_DIR / "EBGaramond-Italic.ttf"
FONT_REF = FONTS_DIR / "Cinzel-Regular.ttf"

# Fallbacks de sistema
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


def _get_font(font_path: Path, fallbacks: list, size: int) -> ImageFont.FreeTypeFont:
    """Carga font con fallback a system fonts."""
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    for fb in fallbacks:
        if os.path.exists(fb):
            return ImageFont.truetype(fb, size)
    return ImageFont.load_default()


def _render_text_frame(
    texto: str,
    referencia: str,
    width: int,
    height: int,
    config: dict,
) -> np.ndarray:
    """
    Renderiza un frame RGBA con el texto del versículo y su referencia.
    Retorna numpy array (height, width, 4) con canal alpha.
    """
    font_size = config.get("tamano", 52)
    color_texto = config.get("color_texto", "#FFFFFF")
    color_ref = config.get("color_referencia", "#E8D5A3")
    posicion = config.get("posicion", "bottom")
    mostrar_ref = config.get("mostrar_referencia", True)

    font_verse = _get_font(FONT_VERSE, SYSTEM_FONTS, font_size)
    font_ref = _get_font(FONT_REF, SYSTEM_FONTS_REF, int(font_size * 0.54))

    # Crear imagen RGBA transparente
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Wrap text al 75% del ancho
    max_text_width = int(width * 0.75)
    wrapped = _wrap_text(draw, texto, font_verse, max_text_width)

    # Medir texto
    text_bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_verse)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    # Medir referencia
    ref_text = f"— {referencia} —" if mostrar_ref else ""
    ref_h = 0
    separator_h = 0
    if mostrar_ref and referencia:
        ref_bbox = draw.textbbox((0, 0), ref_text, font=font_ref)
        ref_h = ref_bbox[3] - ref_bbox[1]
        separator_h = 32  # espacio para línea decorativa

    total_content_h = text_h + separator_h + ref_h

    # Posición vertical
    if posicion == "top":
        y_start = int(height * 0.08)
    elif posicion == "center":
        y_start = (height - total_content_h) // 2
    else:  # bottom
        y_start = height - total_content_h - int(height * 0.08)

    # Sombra/fondo detrás del texto
    padding = 24
    bg_left = (width - max(text_w, 200)) // 2 - padding
    bg_top = y_start - padding
    bg_right = (width + max(text_w, 200)) // 2 + padding
    bg_bottom = y_start + total_content_h + padding

    # Rectángulo negro 40% opacidad
    shadow_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_draw.rounded_rectangle(
        [bg_left, bg_top, bg_right, bg_bottom],
        radius=12,
        fill=(0, 0, 0, 102),  # 40% opacity
    )
    img = Image.alpha_composite(img, shadow_img)
    draw = ImageDraw.Draw(img)

    # Sombra del texto
    x_text = (width - text_w) // 2
    draw.multiline_text(
        (x_text + 2, y_start + 2), wrapped,
        font=font_verse, fill=(0, 0, 0, 180), align="center",
    )
    # Texto principal
    draw.multiline_text(
        (x_text, y_start), wrapped,
        font=font_verse, fill=color_texto, align="center",
    )

    # Separador y referencia
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


def _wrap_text(draw, text: str, font, max_width: int) -> str:
    """Wrap text para que no exceda max_width píxeles."""
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


def _apply_bg_effect(clip, efecto: str):
    """
    Aplica efecto de movimiento al clip de fondo.
    - "Zoom lento ↗": zoom in lento (6% de escala sobre toda la duración)
    - "Zoom lento ↙": zoom out lento
    - "Paneo suave →": desplazamiento horizontal de izquierda a derecha
    - "Sin efecto": sin cambios
    """
    if not efecto or efecto == "Sin efecto":
        return clip

    duration = clip.duration
    W, H = 1920, 1080
    zoom_ratio = 0.06  # 6% de escala — sutil, no mareante

    if efecto == "Zoom lento ↗":
        def zoom_in(get_frame, t):
            scale = 1.0 + zoom_ratio * (t / duration)
            frame = get_frame(t)
            img = Image.fromarray(frame)
            new_w, new_h = int(W * scale), int(H * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - W) // 2
            top = (new_h - H) // 2
            return np.array(img.crop((left, top, left + W, top + H)))
        return clip.transform(zoom_in, apply_to="video")

    elif efecto == "Zoom lento ↙":
        def zoom_out(get_frame, t):
            scale = (1.0 + zoom_ratio) - zoom_ratio * (t / duration)
            frame = get_frame(t)
            img = Image.fromarray(frame)
            new_w, new_h = int(W * scale), int(H * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - W) // 2
            top = (new_h - H) // 2
            return np.array(img.crop((left, top, left + W, top + H)))
        return clip.transform(zoom_out, apply_to="video")

    elif efecto == "Paneo suave →":
        def pan_right(get_frame, t):
            frame = get_frame(t)
            img = Image.fromarray(frame)
            scale = 1.0 + zoom_ratio
            new_w, new_h = int(W * scale), int(H * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            offset_x = int((new_w - W) * (t / duration))
            top = (new_h - H) // 2
            return np.array(img.crop((offset_x, top, offset_x + W, top + H)))
        return clip.transform(pan_right, apply_to="video")

    return clip


def renderizar_video(
    imagen_path: str,
    musica_path: str,
    versiculos: list[dict],
    duracion_total_segundos: int,
    segundos_por_versiculo: int,
    config_texto: dict,
    output_path: str,
    efecto_imagen: str = "Zoom lento ↗",
    progress_callback=None,
) -> str:
    """
    Renderiza el video final .mp4.

    - Imagen de fondo estática durante todo el video
    - Cada versículo: fade in (1.5s) → visible → fade out (1.5s) → siguiente
    - Audio de fondo
    - Codec: libx264, audio: aac, bitrate: 8000k

    Retorna el path del .mp4 generado.
    """
    width, height = 1920, 1080
    fps = 24
    fade_dur = config_texto.get("fade_duration", 1.5)

    if progress_callback:
        progress_callback(0.05, "Preparando imagen de fondo...")

    # 1. Imagen de fondo
    bg_img = Image.open(imagen_path).resize((width, height), Image.LANCZOS)
    bg_array = np.array(bg_img)

    # Calcular cuántos versículos necesitamos para la duración total
    num_verses_needed = duracion_total_segundos // segundos_por_versiculo
    if num_verses_needed == 0:
        num_verses_needed = 1

    # Ciclar versículos si no hay suficientes
    full_verses = []
    while len(full_verses) < num_verses_needed:
        for v in versiculos:
            full_verses.append(v)
            if len(full_verses) >= num_verses_needed:
                break

    actual_duration = len(full_verses) * segundos_por_versiculo

    if progress_callback:
        progress_callback(0.1, f"Renderizando {len(full_verses)} versículos...")

    # 2. Clip de fondo + efecto Ken Burns / paneo
    bg_clip = ImageClip(bg_array, duration=actual_duration).with_fps(fps)
    bg_clip = _apply_bg_effect(bg_clip, efecto_imagen)

    # 3. Crear clips de texto para cada versículo
    text_clips = []
    total = len(full_verses)

    for i, v in enumerate(full_verses):
        texto = v.get("texto", "")
        referencia = v.get("referencia", "")

        # Renderizar frame de texto con Pillow
        text_frame = _render_text_frame(texto, referencia, width, height, config_texto)

        # Crear clip de texto con fade in/out manual via transform
        start_time = i * segundos_por_versiculo
        dur = segundos_por_versiculo
        fd = fade_dur

        def make_filter(d=dur, f=fd):
            def filter_func(get_frame, t):
                frame = get_frame(t)
                if t < f:
                    factor = t / f
                elif t > d - f:
                    factor = (d - t) / f
                else:
                    factor = 1.0
                factor = max(0.0, min(1.0, factor))
                if factor < 1.0:
                    return (frame * factor).astype(frame.dtype)
                return frame
            return filter_func

        text_clip = (
            ImageClip(text_frame, duration=dur)
            .with_fps(fps)
            .with_start(start_time)
            .transform(make_filter())
        )
        text_clips.append(text_clip)

        if progress_callback and i % 5 == 0:
            pct = 0.1 + 0.6 * (i / total)
            progress_callback(pct, f"Versículo {i + 1} de {total}...")

    if progress_callback:
        progress_callback(0.7, "Componiendo video...")

    # 4. Componer video
    final = CompositeVideoClip([bg_clip] + text_clips, size=(width, height))

    # 5. Audio
    if musica_path and os.path.exists(musica_path):
        audio_clip = AudioFileClip(musica_path)
        # Si el audio es más corto que el video, loop
        if audio_clip.duration < actual_duration:
            loops_needed = int(actual_duration / audio_clip.duration) + 1
            from moviepy import concatenate_audioclips
            audio_clip = concatenate_audioclips([audio_clip] * loops_needed)
        audio_clip = audio_clip.subclipped(0, actual_duration)
        final = final.with_audio(audio_clip)

    if progress_callback:
        progress_callback(0.75, "Escribiendo archivo .mp4 (esto toma tiempo)...")

    # 6. Escribir video
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        bitrate="8000k",
        preset="medium",
        logger="bar",
    )

    if progress_callback:
        progress_callback(1.0, "¡Video completado!")

    # Limpiar
    final.close()
    bg_clip.close()

    return os.path.abspath(output_path)


