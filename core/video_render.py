"""
Renderizado de video con MoviePy 2.x + Pillow.
Genera .mp4 con versículos bíblicos sobre imagen de fondo.
Soporta múltiples formatos (16:9, 9:16, 1:1) y estilos de texto.
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

from core.formats import get_dimensions
from core.text_style import (
    render_fea_frame,
    render_simple_frame,
    _get_font,
    _wrap_text,
    FONT_VERSE,
    FONT_REF,
    FONTS_DIR,
    SYSTEM_FONTS,
    SYSTEM_FONTS_REF,
)


def _autocrop_borders(img: Image.Image, threshold: int = 8) -> Image.Image:
    """
    Remove uniform light borders (white/gray museum scan margins) from an image.
    Detects columns and rows where pixel std-dev is below threshold — those are
    solid-color margins. Crops to the content bounding box.
    """
    arr = np.array(img)
    # A column/row is 'content' if it has meaningful variation (std > threshold)
    col_std = arr.std(axis=(0, 2))   # std per column across all rows and channels
    row_std = arr.std(axis=(1, 2))   # std per row across all columns and channels
    content_cols = np.where(col_std > threshold)[0]
    content_rows = np.where(row_std > threshold)[0]
    if len(content_cols) == 0 or len(content_rows) == 0:
        return img  # can't detect border, return as-is
    left, right = int(content_cols[0]), int(content_cols[-1])
    top, bottom = int(content_rows[0]), int(content_rows[-1])
    # Only crop if the border takes up more than 5% on any side
    w, h = img.size
    if left > w * 0.05 or right < w * 0.95 or top > h * 0.05 or bottom < h * 0.95:
        return img.crop((left, top, right + 1, bottom + 1))
    return img


def _apply_split_tone(img: Image.Image) -> Image.Image:
    """
    Split-tone color grade: warm shadows + cool highlights.

    Shadows  (dark pixels):  R+15, B-12  — golden/warm feel
    Highlights (bright px):  R-8,  B+10  — cool/ethereal feel

    More cinematic than a flat warm-grade; closer to Heaven Instrumental
    and other top-performing Christian channels.
    """
    arr = np.array(img, dtype=np.float32)
    lum = arr.mean(axis=2, keepdims=True) / 255.0       # 0=dark, 1=bright

    # Shadows mask: strongest at darkest pixels
    shadow_mask = np.clip(1.0 - lum * 2, 0, 1)
    arr[..., 0] += shadow_mask[..., 0] * 15   # R boost in shadows
    arr[..., 2] -= shadow_mask[..., 0] * 12   # B cut  in shadows

    # Highlights mask: strongest at brightest pixels
    hi_mask = np.clip(lum * 2 - 1, 0, 1)
    arr[..., 0] -= hi_mask[..., 0] * 8        # R cut  in highlights
    arr[..., 2] += hi_mask[..., 0] * 10       # B boost in highlights

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def _apply_vignette(img: Image.Image, strength: float = 0.35) -> Image.Image:
    """
    Add a subtle dark vignette around the edges.
    strength: 0.0 = no vignette, 1.0 = fully black edges.
    """
    w, h = img.size
    arr = np.array(img, dtype=np.float32)

    # Build an elliptical gradient mask (1 = center, 0 = edge)
    cx, cy = w / 2.0, h / 2.0
    y_idx, x_idx = np.mgrid[0:h, 0:w]
    # Normalise to [-1, 1] range (slightly tighter horizontally for 16:9)
    nx = (x_idx - cx) / (cx * 1.05)
    ny = (y_idx - cy) / (cy * 1.05)
    dist = np.clip(nx ** 2 + ny ** 2, 0, 1)  # 0 = center, 1 = corner

    # Smoothstep curve: gentle centre, fast falloff at edges
    t = dist
    smooth = t * t * (3 - 2 * t)
    vignette = 1.0 - smooth * strength  # 1 at center, (1-strength) at corner

    arr[..., :3] *= vignette[..., np.newaxis]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


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

    # Subtle shadow only directly behind the text block — not a full-width band
    padding_v = 24
    padding_h = 60
    strip_top = max(0, y_start - padding_v)
    strip_bot = min(height, y_start + total_content_h + padding_v)
    text_center_x = width // 2
    text_half_w = min(int(width * 0.42), max(text_w, 300) // 2 + padding_h)
    strip_left = max(0, text_center_x - text_half_w)
    strip_right = min(width, text_center_x + text_half_w)
    strip_h = strip_bot - strip_top
    strip_w = strip_right - strip_left

    if strip_h > 0 and strip_w > 0:
        shadow_arr = np.zeros((height, width, 4), dtype=np.uint8)
        # Vertical gradient: transparent → dark (max 45%) → transparent
        for row_i in range(strip_h):
            rel = row_i / max(strip_h - 1, 1)
            v_alpha = 4 * rel * (1 - rel)  # parabola, peaks at 1.0 at center
            # Horizontal gradient: fade to transparent at left/right edges
            for col_i in range(strip_w):
                h_rel = col_i / max(strip_w - 1, 1)
                h_alpha = min(1.0, 4 * h_rel * (1 - h_rel) + 0.5)  # wider flat top
                alpha = int(115 * v_alpha * min(1.0, h_alpha))  # max ~45% opacity
                shadow_arr[strip_top + row_i, strip_left + col_i, 3] = alpha
        shadow_img = Image.fromarray(shadow_arr, "RGBA")
        img = Image.alpha_composite(img, shadow_img)
        draw = ImageDraw.Draw(img)

    # Stroke (contorno negro) para legibilidad sobre cualquier fondo
    x_text = (width - text_w) // 2
    stroke = 3
    for dx in range(-stroke, stroke + 1):
        for dy in range(-stroke, stroke + 1):
            if dx == 0 and dy == 0:
                continue
            draw.multiline_text(
                (x_text + dx, y_start + dy), wrapped,
                font=font_verse, fill=(0, 0, 0, 220), align="center",
            )
    # Texto principal blanco
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
        # Stroke fino en referencia
        for dx2, dy2 in [(-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,-1),(-1,1),(1,1),
                         (-3,0),(3,0),(0,-3),(0,3)]:
            draw.text(
                (ref_x + dx2, ref_y + dy2), ref_text,
                font=font_ref, fill=(0, 0, 0, 240),
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


def _apply_bg_effect(clip, efecto: str, target_w: int = 1920, target_h: int = 1080):
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
    W, H = target_w, target_h
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

    elif efecto == "Paneo suave ←":
        def pan_left(get_frame, t):
            frame = get_frame(t)
            img = Image.fromarray(frame)
            scale = 1.0 + zoom_ratio
            new_w, new_h = int(W * scale), int(H * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            offset_x = int((new_w - W) * (1.0 - t / duration))
            top = (new_h - H) // 2
            return np.array(img.crop((offset_x, top, offset_x + W, top + H)))
        return clip.transform(pan_left, apply_to="video")

    elif efecto == "Paneo suave ↑":
        def pan_up(get_frame, t):
            frame = get_frame(t)
            img = Image.fromarray(frame)
            scale = 1.0 + zoom_ratio
            new_w, new_h = int(W * scale), int(H * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - W) // 2
            offset_y = int((new_h - H) * (1.0 - t / duration))
            return np.array(img.crop((left, offset_y, left + W, offset_y + H)))
        return clip.transform(pan_up, apply_to="video")

    return clip


# All available Ken Burns / pan effects for random selection
# v3.8: expanded from 5 → 10 effects, includes zoom-out and diagonal combos
BG_EFFECTS = [
    # Zoom in — con easing coseno (más cinematográfico que linear)
    "Zoom lento ↗",       # zoom-in + pan diagonal arriba-derecha
    "Zoom lento ↙",       # zoom-in + pan diagonal abajo-izquierda
    "Zoom lento ↘",       # zoom-in + pan diagonal abajo-derecha  [nuevo]
    "Zoom lento ↖",       # zoom-in + pan diagonal arriba-izquierda  [nuevo]
    # Zoom out — sale de cerca, revela el cuadro  [nuevo]
    "Zoom out ↗",         # zoom-out + drift diagonal
    "Zoom out ↙",         # zoom-out + drift opuesto  [nuevo]
    # Paneos puros — sin cambio de zoom
    "Paneo suave →",
    "Paneo suave ←",
    "Paneo suave ↑",
    "Paneo suave ↓",      # [nuevo]
]


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
    format_key: str = "youtube_1080",
    text_style: str = "simple",
    layout_preset: str = "centrado_bajo",
    background_images: list = None,
    verses_per_background: int = 1,
    random_ken_burns: bool = True,
    render_fps: int = 24,
) -> str:
    # DEPRECATED (v3.4): MoviePy renderer. Uso producción: renderizar_video_fast.
    # Conservado para compat con app.py (Gradio) + tests legacy.
    """
    Renderiza el video final .mp4.

    - Cada versículo: fade in → visible → fade out → siguiente
    - Si background_images se provee, rota fondos cada verses_per_background versículos
    - Si random_ken_burns=True, cada fondo recibe un efecto Ken Burns/paneo distinto
    - Audio de fondo con loop automático
    - Codec: libx264, audio: aac, bitrate: 8000k

    Args:
        format_key: "youtube_1080", "reel_1080", etc.
        background_images: List of image paths to cycle through. Falls back to imagen_path.
        verses_per_background: How many verses share the same background (1 = change every verse).
        random_ken_burns: Randomize pan/zoom direction per background clip.
    """
    import random as _random

    width, height = get_dimensions(format_key)
    fps = render_fps
    fade_dur = config_texto.get("fade_duration", 1.5)

    if progress_callback:
        progress_callback(0.05, "Preparando imágenes de fondo...")

    # 1. Build background image pool — apply warm grade + vignette to all
    all_bg_paths = background_images if background_images else [imagen_path]
    # Always include the primary image
    if imagen_path not in all_bg_paths:
        all_bg_paths = [imagen_path] + list(all_bg_paths)

    def _load_bg(path: str) -> np.ndarray:
        from PIL import ImageOps
        img = Image.open(path).convert("RGB")
        img = _autocrop_borders(img)
        img = ImageOps.fit(img, (width, height), Image.LANCZOS)
        img = _apply_split_tone(img)
        img = _apply_vignette(img, strength=0.35)
        return np.array(img)

    bg_pool = [_load_bg(p) for p in all_bg_paths]

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

    # 2. Background clips — one per group of verses, each with its own Ken Burns
    bg_clips = []
    _rng = _random.Random(42)  # deterministic seed for reproducibility
    num_bg_groups = (len(full_verses) + verses_per_background - 1) // verses_per_background

    for group_idx in range(num_bg_groups):
        verse_start = group_idx * verses_per_background
        verse_end = min(verse_start + verses_per_background, len(full_verses))
        group_dur = (verse_end - verse_start) * segundos_por_versiculo
        group_start_time = verse_start * segundos_por_versiculo

        # Pick background from pool (cycle through)
        bg_arr = bg_pool[group_idx % len(bg_pool)]

        # Pick Ken Burns effect
        if random_ken_burns:
            effect = _rng.choice(BG_EFFECTS)
        else:
            effect = efecto_imagen

        bg_clip = (
            ImageClip(bg_arr, duration=group_dur)
            .with_fps(fps)
            .with_start(group_start_time)
        )
        bg_clip = _apply_bg_effect(bg_clip, effect, width, height)
        bg_clips.append(bg_clip)

    # 3. Crear clips de texto para cada versículo
    text_clips = []
    total = len(full_verses)

    for i, v in enumerate(full_verses):
        texto = v.get("texto", "")
        referencia = v.get("referencia", "")

        # Renderizar frame de texto con Pillow
        if text_style == "fea":
            text_frame = render_fea_frame(
                texto, referencia, width, height,
                layout_preset=layout_preset,
                format_key=format_key,
                config_overrides=config_texto,
            )
        else:
            text_frame = _render_text_frame(
                texto, referencia, width, height, config_texto,
            )

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
    final = CompositeVideoClip(bg_clips + text_clips, size=(width, height))

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
        bitrate="4000k",
        preset="fast",
        logger="bar",
    )

    if progress_callback:
        progress_callback(1.0, "¡Video completado!")

    # Limpiar
    final.close()
    bg_clip.close()

    return os.path.abspath(output_path)


# ─── Fast ffmpeg-native renderer ─────────────────────────────────────────────

def _zoompan_expr(effect: str, total_frames: int, start_frame: int = 0) -> tuple:
    """
    Return (z_expr, x_expr, y_expr) for ffmpeg zoompan filter.
    Source images are at native output size (e.g. 1920×1080).
    z > 1.0 gives room for panning without black bars.
    'on' = output frame counter, starting from 0 for each individual clip.

    v3.8: cosine easing for organic motion.
    v3.9: start_frame offset for continuous Ken Burns across multi-verse backgrounds.
      When verses_per_background=3, total_frames = 3×verse_frames, and each
      verse clip within the group passes start_frame = verse_pos × verse_frames.
      This means the animation continues seamlessly across all verses on the
      same background instead of restarting every 20s.

      Formula:  F = on + start_frame   (effective global frame position)
                ease(t) = (1-cos(π·F/T))/2   where T = total_frames-1
    """
    T   = max(total_frames - 1, 1)
    PI  = "3.14159265"
    F   = f"(on+{start_frame})" if start_frame > 0 else "on"

    # Eased zoom-in: 1.05 → 1.15 (slow start, accelerates, slow end)
    z_in  = f"1.05+0.10*(1-cos({PI}*{F}/{T}))/2"
    # Eased zoom-out: 1.15 → 1.05
    z_out = f"1.15-0.10*(1-cos({PI}*{F}/{T}))/2"
    # Static zoom for pure pans
    z_pan = "1.12"

    if effect == "Zoom lento ↗":
        return (
            z_in,
            f"max(0,(iw-iw/zoom)/2+{F}/{T}*35)",
            f"max(0,(ih-ih/zoom)/2-{F}/{T}*20)",
        )
    elif effect == "Zoom lento ↙":
        return (
            z_in,
            f"max(0,(iw-iw/zoom)/2-{F}/{T}*35)",
            f"min(ih-ih/zoom,(ih-ih/zoom)/2+{F}/{T}*20)",
        )
    elif effect == "Zoom lento ↘":
        return (
            z_in,
            f"max(0,(iw-iw/zoom)/2+{F}/{T}*35)",
            f"min(ih-ih/zoom,(ih-ih/zoom)/2+{F}/{T}*20)",
        )
    elif effect == "Zoom lento ↖":
        return (
            z_in,
            f"max(0,(iw-iw/zoom)/2-{F}/{T}*35)",
            f"max(0,(ih-ih/zoom)/2-{F}/{T}*20)",
        )
    elif effect == "Zoom out ↗":
        return (
            z_out,
            f"max(0,(iw-iw/zoom)/2+{F}/{T}*30)",
            f"max(0,(ih-ih/zoom)/2-{F}/{T}*18)",
        )
    elif effect == "Zoom out ↙":
        return (
            z_out,
            f"max(0,(iw-iw/zoom)/2-{F}/{T}*30)",
            f"min(ih-ih/zoom,(ih-ih/zoom)/2+{F}/{T}*18)",
        )
    elif effect == "Paneo suave →":
        return z_pan, f"{F}/{T}*(iw-iw/zoom)", "(ih-ih/zoom)/2"
    elif effect == "Paneo suave ←":
        return z_pan, f"(iw-iw/zoom)*(1-{F}/{T})", "(ih-ih/zoom)/2"
    elif effect == "Paneo suave ↑":
        return z_pan, "(iw-iw/zoom)/2", f"(ih-ih/zoom)*(1-{F}/{T})"
    elif effect == "Paneo suave ↓":
        return z_pan, "(iw-iw/zoom)/2", f"{F}/{T}*(ih-ih/zoom)"
    else:
        # fallback: centered static
        return "1.10", "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"


def renderizar_video_fast(
    imagen_path: str,
    musica_path: str,
    versiculos: list,
    duracion_total_segundos: int,
    segundos_por_versiculo: int,
    config_texto: dict,
    output_path: str,
    efecto_imagen: str = "Zoom lento ↗",
    progress_callback=None,
    format_key: str = "youtube_1080",
    text_style: str = "fea",
    layout_preset: str = "centrado_bajo",
    background_images: list = None,
    verses_per_background: int = 1,
    random_ken_burns: bool = True,
    render_fps: int = 12,
    parallel_jobs: int = 4,
    visual_templates: list | None = None,
    cleanup_work_dir: bool = True,
) -> str:
    """
    Fast video renderer using ffmpeg native filters (10-20× faster than MoviePy).

    Strategy:
      1. Pre-process backgrounds with warm grade + vignette → temp JPGs
      2. Pre-render each verse as a transparent text PNG (Pillow, once per verse)
      3. Per verse: ffmpeg zoompan Ken Burns + text overlay + fade → short clip
         (clips run in parallel via ThreadPoolExecutor)
      4. ffmpeg concat all clips (stream copy, no re-encode)
      5. ffmpeg mix audio
    """
    import subprocess
    import random as _random
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed

    width, height = get_dimensions(format_key)
    fps = render_fps
    fade_dur = float(config_texto.get("fade_duration", 1.5))
    dur = segundos_por_versiculo
    fade_out_start = dur - fade_dur

    work_dir = output_path.replace(".mp4", "_work")
    os.makedirs(work_dir, exist_ok=True)

    # 1. Pre-process background images → warm grade + vignette → save as temp JPGs
    all_bg_paths = list(background_images) if background_images else [imagen_path]
    if imagen_path not in all_bg_paths:
        all_bg_paths.insert(0, imagen_path)

    processed_bg = []
    for i, bg_path in enumerate(all_bg_paths):
        out_p = os.path.join(work_dir, f"bg_{i:03d}.jpg")
        if not os.path.exists(out_p):
            from PIL import ImageOps
            img = Image.open(bg_path).convert("RGB")
            img = _autocrop_borders(img)
            img = ImageOps.fit(img, (width, height), Image.LANCZOS)
            img = _apply_split_tone(img)
            img = _apply_vignette(img, strength=0.35)
            img.save(out_p, quality=95)
        processed_bg.append(out_p)

    if progress_callback:
        progress_callback(0.03, f"{len(processed_bg)} fondos preparados.")

    # v3.9: Pre-render god-ray RGBA overlay (once, reused for all clips via closure)
    from core.effects import create_godray_png
    from config import GODRAY_ALPHA, GODRAY_BLUR
    godray_png = create_godray_png(work_dir, width, height,
                                   alpha=GODRAY_ALPHA, blur=GODRAY_BLUR)

    # 2. Cycle verses to fill total duration
    target_count = duracion_total_segundos // dur or 1
    full_verses = []
    while len(full_verses) < target_count:
        full_verses.extend(versiculos)
    full_verses = full_verses[:target_count]

    # 3. Pre-render text overlays — one RGBA PNG per verse (fast Pillow, runs once)
    # visual_templates lets you alternate 2+ visual styles verse-by-verse.
    # Each entry: {"layout_preset": "...", "text_style": "fea"} (text_style optional).
    # Falls back to single layout_preset/text_style when not provided.
    _templates = visual_templates or [
        {"layout_preset": layout_preset, "text_style": text_style}
    ]

    if progress_callback:
        progress_callback(0.05, f"Pre-renderizando {len(full_verses)} textos...")

    text_pngs = []
    for i, v in enumerate(full_verses):
        png_path = os.path.join(work_dir, f"txt_{i:04d}.png")
        if not os.path.exists(png_path):
            tpl = _templates[i % len(_templates)]
            tpl_style = tpl.get("text_style", "fea")
            tpl_layout = tpl.get("layout_preset", layout_preset)
            if tpl_style == "fea":
                frame = render_fea_frame(
                    v.get("texto", ""), v.get("referencia", ""),
                    width, height,
                    layout_preset=tpl_layout,
                    format_key=format_key,
                    config_overrides=config_texto,
                )
            else:
                frame = _render_text_frame(
                    v.get("texto", ""), v.get("referencia", ""),
                    width, height, config_texto,
                )
            Image.fromarray(frame).save(png_path)
        text_pngs.append(png_path)

    if progress_callback:
        progress_callback(0.10, "Textos pre-renderizados. Iniciando clips ffmpeg...")

    # 4. Assign Ken Burns effect per verse (deterministic)
    _rng = _random.Random(42)
    verse_effects = []
    groups = (len(full_verses) + verses_per_background - 1) // verses_per_background
    for g in range(groups):
        eff = _rng.choice(BG_EFFECTS) if random_ken_burns else efecto_imagen
        verse_effects.extend([eff] * verses_per_background)
    verse_effects = verse_effects[:len(full_verses)]

    # 5. Render each verse clip with ffmpeg (parallel)
    frames_per_verse       = dur * fps
    # Total frames for a full background group — Ken Burns spans this whole duration.
    # Each verse within the group starts at verse_pos_in_group × frames_per_verse
    # so the animation continues seamlessly instead of restarting every verse.
    total_frames_group = frames_per_verse * verses_per_background

    def render_clip(args):
        idx, bg_p, txt_p, effect = args
        out_clip = os.path.join(work_dir, f"clip_{idx:04d}.mp4")
        if os.path.exists(out_clip):
            return idx, True, out_clip

        # Continuous Ken Burns: offset by verse position within the background group
        verse_pos   = idx % verses_per_background
        start_frame = verse_pos * frames_per_verse
        zp_z, zp_x, zp_y = _zoompan_expr(effect, total_frames_group, start_frame)
        # Note: applying fade to the text layer with zoompan causes timestamp
        # drift that makes the text invisible. Fade the full composite instead.
        filt = (
            f"[0:v]"
            f"zoompan=z='{zp_z}':x='{zp_x}':y='{zp_y}'"
            f":d=1:s={width}x{height}:fps={fps}"
            f"[bg];"
            f"[bg][1:v]overlay=0:0[t];"
            f"[t][2:v]overlay=0:0[out_raw];"
            f"[out_raw]"
            f"fade=t=in:st=0:d={fade_dur},"
            f"fade=t=out:st={fade_out_start}:d={fade_dur}"
            f"[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", bg_p,
            "-i", txt_p,
            "-loop", "1", "-i", godray_png,   # [2:v] — god-ray RGBA overlay
            "-filter_complex", filt,
            "-map", "[out]",
            "-t", str(dur),
            "-r", str(fps),
            "-c:v", "libx264", "-preset", "ultrafast",
            "-b:v", "3500k", "-maxrate", "4000k", "-bufsize", "8000k",
            "-pix_fmt", "yuv420p",
            "-an",
            out_clip,
        ]
        t_start = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - t_start
        if r.returncode != 0:
            return idx, False, r.stderr[-800:], elapsed
        return idx, True, out_clip, elapsed

    clip_args = [
        (i, processed_bg[i % len(processed_bg)], text_pngs[i], verse_effects[i])
        for i in range(len(full_verses))
    ]

    clip_map = {}
    clip_times: list[tuple[int, float]] = []   # (clip_idx, seconds) for instrumentation
    done = 0
    report_every = max(1, len(full_verses) // 20)
    SLOW_CLIP_THRESHOLD_SEC = 30.0   # umbral para log detallado de outliers

    with ThreadPoolExecutor(max_workers=parallel_jobs) as exe:
        futs = {exe.submit(render_clip, a): a[0] for a in clip_args}
        for fut in as_completed(futs):
            result = fut.result()
            # Backward compat: new tuple (idx, ok, result, elapsed)
            if len(result) == 4:
                idx, ok, payload, elapsed = result
            else:
                idx, ok, payload = result
                elapsed = 0.0
            if not ok:
                raise RuntimeError(f"ffmpeg failed clip {idx}: {payload}")
            clip_map[idx] = payload
            clip_times.append((idx, elapsed))
            if elapsed > SLOW_CLIP_THRESHOLD_SEC:
                print(f"  [slow-clip] idx={idx} took {elapsed:.1f}s (>30s threshold)")
            done += 1
            if progress_callback and done % report_every == 0:
                pct = 0.10 + 0.75 * (done / len(full_verses))
                progress_callback(pct, f"Clips: {done}/{len(full_verses)}")

    # Top-5 slowest clips — útil para identificar outliers (paz/esperanza 42min bug)
    if clip_times:
        top5 = sorted(clip_times, key=lambda t: t[1], reverse=True)[:5]
        avg = sum(t[1] for t in clip_times) / len(clip_times)
        print(f"  [clip-stats] avg={avg:.2f}s  top-5 slowest: " +
              ", ".join(f"#{i}:{s:.1f}s" for i, s in top5))

    if progress_callback:
        progress_callback(0.86, "Concatenando clips...")

    # 6. Concat all clips (stream copy — no re-encode)
    concat_list = os.path.join(work_dir, "concat.txt")
    with open(concat_list, "w") as f:
        for idx in range(len(full_verses)):
            f.write(f"file '{os.path.abspath(clip_map[idx])}'\n")

    concat_silent = os.path.join(work_dir, "video_silent.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-c", "copy", concat_silent],
        capture_output=True, check=True,
    )

    # 7. Add audio
    if progress_callback:
        progress_callback(0.93, "Añadiendo audio...")

    actual_dur = len(full_verses) * dur
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if musica_path and os.path.exists(musica_path):
        # v3.4-clean: loudnorm a -16 LUFS en el mux final.
        # Fix para amor/paz v3.3 que quedaron a -19/-20 LUFS (YouTube sube volumen visible).
        # Target I=-16, True Peak -1.5, Loudness Range 11 — sweet spot para música relajante.
        subprocess.run(
            ["ffmpeg", "-y",
             "-i", concat_silent, "-i", musica_path,
             "-c:v", "copy",
             "-af", "afade=t=in:st=0:d=5,loudnorm=I=-16:TP=-1.5:LRA=11",
             "-c:a", "aac", "-b:a", "192k",
             "-t", str(actual_dur), "-shortest",
             output_path],
            capture_output=True, check=True,
        )
    else:
        import shutil
        shutil.copy(concat_silent, output_path)

    if progress_callback:
        progress_callback(1.0, "¡Video completado!")

    # Clean up temp work dir (clips + PNGs — already baked into the output)
    if cleanup_work_dir and os.path.exists(work_dir):
        import shutil as _shutil
        from core.render_logger import clean_dir
        freed = clean_dir(work_dir, label="_work temp clips")
        if freed > 0:
            print(f"  [clean] _work/ eliminado ({freed:.0f} MB liberados)")

    return os.path.abspath(output_path)
