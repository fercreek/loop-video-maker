"""
core/shorts_render.py — Motor ffmpeg para Shorts verticales 9:16 1080x1920.

v4 — Pillow como engine primario de texto (NO drawtext):
  - drawtext de ffmpeg requiere libfreetype — NO disponible en este build
  - Todo texto generado via core/shorts_subtitle.py (Pillow)
  - PNGs RGBA transparentes overlayados por ffmpeg con enable='between'
  - Pre-flight check: verify_text_engine() falla rápido si PIL no disponible

  Ken Burns 12% visible, 4 variantes por ID
  Doble imagen (xfade a los 18s)
  Música -18dB, EQ + compressor + reverb en voz
  Hard cut entrada

SPEC DEL BUG RESUELTO (2026-05-11):
  Bug: DRAWTEXT_OK=False silencioso → renders sin texto en v1/v2/v3/v4
  Causa: ffmpeg local sin libfreetype compilado
  Fix: engine switched to Pillow (subtitle_burn pattern)
  Pre-flight: verify_text_engine() antes de cualquier render
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path as _Path

from core.shorts_subtitle import (
    generate_all_layers,
    build_text_track,
    verify_text_engine,
    TextLayer,
)
from dataclasses import dataclass, field
from pathlib import Path

# ─── Dimensiones 9:16 ─────────────────────────────────────────────────────────
SHORT_W = 1080
SHORT_H = 1920
SHORT_RES = f"{SHORT_W}x{SHORT_H}"

# ─── Valores por defecto ──────────────────────────────────────────────────────
DEFAULT_FPS           = 30
DEFAULT_PRESET        = "fast"
DEFAULT_BITRATE       = "4000k"
DEFAULT_AUDIO_BITRATE = "192k"
MUSIC_VOL_DB          = -18      # v2: -18dB = música audible (era -30dB)
NARR_VOL              = 1.0
FADE_IN_SEC           = 0.05    # v2: casi hard cut (era 0.4s)
FADE_OUT_SEC          = 0.6
CROSSFADE_SEC         = 0.5

# Ken Burns — 4 variantes para evitar detección de template
# Cada video usa una variante diferente basada en hash del oracion_id
KB_VARIANTS = [
    "pan_lr",    # pan izquierda → derecha (default)
    "pan_rl",    # pan derecha → izquierda
    "zoom_in",   # zoom in lento centro
    "zoom_out",  # zoom out + pan diagonal
]
KB_ZOOM_RANGE = 0.12   # 12% movement — VISIBLE, no sutil (era 4%)

# Fade in por segmento de subtítulo
SUB_FADE_IN_DUR = 0.18   # segundos de fade-in por cada segmento

# ─── Subtítulos ───────────────────────────────────────────────────────────────
FONT_PATHS = [
    # v2: Montserrat ExtraBold — primer choice
    str(Path(__file__).parent.parent / "assets" / "fonts" / "Montserrat-ExtraBold.ttf"),
    # Fallback
    "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]

SUB_FONTSIZE    = 78             # v2: más grande y bold
SUB_COLOR_GOLD  = "0xF5C842"    # v2: oro devocional (era blanco)
SUB_COLOR_CTA   = "0xFFFFFF"    # CTA en blanco limpio
SUB_SHADOW_COL  = "black@0.85"
SUB_Y_POS       = "(h*0.80)"    # v2: 80% (más abajo, zona segura thumb)
SUB_MAX_CHARS   = 26            # v2: 4-5 palabras por línea (era 38)
SUB_LINE_SPACING = 8
STROKE_WIDTH    = 3             # v2: stroke en lugar de caja negra

# Verse / tema label — esquina superior izquierda (visible todo el video)
VERSE_FONTSIZE  = 38
VERSE_COLOR     = "0xFFFFFF@0.85"
VERSE_BG_COLOR  = "black@0.45"   # pill background detrás del label

# Hook overlay — primeros HOOK_DUR segundos
HOOK_FONTSIZE  = 72
HOOK_COLOR     = "0xFFFFFF"
HOOK_Y_POS     = "(h*0.42)"    # centro-alto del frame
HOOK_DUR       = 3.5           # batch_v6 QW: hook 2.2→3.5s (más tiempo de enganche)

# CTA overlay — últimos CTA_DUR segundos
# v3: "Comparte" genera virality (share signal > save signal para algoritmo)
CTA_TEXT      = "Escribe AMÉN si esto te llegó al corazón 🙏"  # batch_v6 QW: AMÉN > Comparte (engagement signal)
CTA_FONTSIZE  = 54
CTA_Y_POS     = "(h*0.85)"
CTA_DUR       = 3.5

# Doble imagen — corte a IMAGE_SWITCH_SEC (v3)
IMAGE_SWITCH_SEC = 18.0   # segundos donde cambia la imagen de fondo

WATERMARK_TEXT  = "@VersiculoDeDios"
WATERMARK_SZ    = 32
WATERMARK_COLOR = "white@0.7"


# ─── Data classes ─────────────────────────────────────────────────────────────
@dataclass
class SubtitleSegment:
    text: str
    start_sec: float
    end_sec: float


@dataclass
class ShortClipConfig:
    oracion_id: str
    text: str
    narr_path: Path
    image_path: Path
    out_path: Path

    music_path: Path | None = None
    image2_path: Path | None = None  # v3: segunda imagen para corte a IMAGE_SWITCH_SEC
    hook_text: str = ""        # Texto de gancho (ej: "¿Estás creyendo sin ver el camino?")
    verse_label: str = ""      # Label superior: tema o referencia (ej: "Fe · Filipenses 4:13")
    cta_text: str = CTA_TEXT   # CTA al final (default global)
    fps: int = DEFAULT_FPS
    preset: str = DEFAULT_PRESET
    force: bool = False


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _find_font() -> str:
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return ""


def _get_audio_duration(audio_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError(f"ffprobe no pudo leer duración de {audio_path}")


def _check_drawtext() -> bool:
    r = subprocess.run(["ffmpeg", "-filters"], capture_output=True, text=True)
    return "drawtext" in (r.stdout + r.stderr)


DRAWTEXT_OK = _check_drawtext()


def _escape_drawtext(text: str) -> str:
    """Escapa texto para uso seguro en filtro drawtext de ffmpeg."""
    return (
        text
        .replace("\\", "\\\\")
        .replace("'", "’")   # comilla curva evita escape hell
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("%", "\\%")
        .replace("🙏", "")        # emoji no soportado en drawtext
    )


# ─── Subtitle timing ──────────────────────────────────────────────────────────
def build_subtitle_segments(
    text: str,
    audio_duration: float,
    hook_text: str = "",
    hook_duration: float = HOOK_DUR,
) -> list[SubtitleSegment]:
    """
    Genera segmentos cortos (4-5 palabras) con timing proporcional.
    v2: MAX_CHARS reducido a 26 → frases más cortas y rítmicas.
    """
    import re

    segments: list[SubtitleSegment] = []

    # El hook se muestra ANTES de la voz — no se incluye como segmento de subtítulo
    # porque render_hook lo maneja por separado con drawtext
    offset = hook_duration if hook_text else 0.0

    # Dividir en frases por puntuación
    raw = re.split(r"(?<=[.,;:!?¡¿])\s+", text.strip())
    phrases = [p.strip() for p in raw if p.strip()]
    if not phrases:
        return segments

    available = max(0.1, audio_duration - offset)

    # Contar palabras totales para timing proporcional
    all_words = [w for p in phrases for w in p.split()]
    total_words = len(all_words) or 1

    # Agrupar en chunks de ~6 palabras — batch_v6 QW: 4→6 (subtítulos más lentos, legibles)
    chunks: list[str] = []
    current_chunk: list[str] = []
    for word in all_words:
        current_chunk.append(word)
        if len(current_chunk) >= 6:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    chunk_word_counts = [len(c.split()) for c in chunks]
    total_chunk_words = sum(chunk_word_counts) or 1

    current_time = offset
    for chunk, wc in zip(chunks, chunk_word_counts):
        fraction = wc / total_chunk_words
        dur = max(0.7, available * fraction)
        end_time = min(current_time + dur, audio_duration - CTA_DUR - 0.3)
        if end_time <= current_time:
            break
        segments.append(SubtitleSegment(
            text=chunk,
            start_sec=round(current_time, 3),
            end_sec=round(end_time, 3),
        ))
        current_time = end_time + 0.04

    return segments


def _kb_variant(oracion_id: str) -> str:
    """Elige variante de Ken Burns basada en hash del ID — cada video es diferente."""
    h = sum(ord(c) for c in oracion_id)
    return KB_VARIANTS[h % len(KB_VARIANTS)]


def _build_bg_ffmpeg(input_label: str, out_label: str, duration: float,
                     t_offset: float, variant: str) -> str:
    """
    Genera filtro Ken Burns según variante:
      pan_lr   — pan horizontal izquierda→derecha
      pan_rl   — pan horizontal derecha→izquierda
      zoom_in  — zoom lento al centro
      zoom_out — zoom out + pan diagonal
    """
    pad = KB_ZOOM_RANGE + 0.02          # padding extra para el movimiento
    sw  = int(SHORT_W  * (1 + pad))    # ~1113
    sh  = int(SHORT_H  * (1 + pad))    # ~1981
    dur_expr = f"max(1,{duration:.2f})"
    t_rel    = f"(t-{t_offset:.2f})"   # tiempo relativo al segmento

    if variant == "pan_lr":
        x_expr = f"({sw}-{SHORT_W})*{t_rel}/{dur_expr}"
        y_expr = f"({sh}-{SHORT_H})/2"
    elif variant == "pan_rl":
        x_expr = f"({sw}-{SHORT_W})*(1-{t_rel}/{dur_expr})"
        y_expr = f"({sh}-{SHORT_H})/2"
    elif variant == "zoom_in":
        # Empieza más alejado, hace zoom in → crop se achica progresivamente
        # Implementado como pan al centro con escala fija
        x_expr = f"({sw}-{SHORT_W})/2"
        y_expr = f"({sh}-{SHORT_H})*(1-{t_rel}/{dur_expr})"
    else:  # zoom_out / diagonal
        x_expr = f"({sw}-{SHORT_W})*{t_rel}/{dur_expr}"
        y_expr = f"({sh}-{SHORT_H})*(1-{t_rel}/{dur_expr})"

    return (
        f"{input_label}"
        f"scale={sw}:{sh}:flags=lanczos:force_original_aspect_ratio=increase,"
        f"crop={sw}:{sh},"
        f"crop={SHORT_W}:{SHORT_H}:x='{x_expr}':y='{y_expr}',"
        "gblur=sigma=35,setsar=1"
        f"{out_label}"
    )


def _build_fg_ffmpeg(input_label: str, out_label: str, variant: str,
                     duration: float, t_offset: float) -> str:
    """Imagen principal con leve movimiento opuesto al BG (parallax sutil)."""
    fg_h = int(SHORT_H * 1.04)
    t_rel = f"(t-{t_offset:.2f})"
    dur_e = f"max(1,{duration:.2f})"

    # Parallax: si BG va izquierda→derecha, FG va ligeramente derecha→izquierda
    if variant in ("pan_lr",):
        x_expr = f"(iw-{SHORT_W})/2 + (iw-{SHORT_W})*0.15*(1-{t_rel}/{dur_e})"
    elif variant in ("pan_rl",):
        x_expr = f"(iw-{SHORT_W})/2 + (iw-{SHORT_W})*0.15*{t_rel}/{dur_e}"
    else:
        x_expr = f"(iw-{SHORT_W})/2"

    return (
        f"{input_label}"
        f"scale=-1:{fg_h}:flags=lanczos,"
        f"crop={SHORT_W}:{SHORT_H}:x='{x_expr}':y=0,setsar=1"
        f"{out_label}"
    )


# ─── Video filter ──────────────────────────────────────────────────────────────
def _build_video_filter(
    duration: float,
    subtitle_segments: list[SubtitleSegment],
    font: str,
    hook_text: str = "",
    verse_label: str = "",
    cta_text: str = CTA_TEXT,
    has_image2: bool = False,
    oracion_id: str = "",
) -> str:
    """
    v2: Ken Burns + hook overlay + subtítulos dorados + CTA.
    """
    total_frames = int(duration * DEFAULT_FPS)
    fade_out_start = max(0.0, duration - FADE_OUT_SEC)
    cta_start = max(0.0, duration - CTA_DUR)

    filters: list[str] = []
    variant = _kb_variant(oracion_id)  # variante Ken Burns por ID

    if has_image2 and duration > IMAGE_SWITCH_SEC + 4:
        t_switch = IMAGE_SWITCH_SEC
        dur_a    = t_switch
        dur_b    = duration - t_switch
        # Variante opuesta para imagen2 (más variación visual)
        variant2 = KB_VARIANTS[(KB_VARIANTS.index(variant) + 2) % len(KB_VARIANTS)]

        filters += [
            _build_bg_ffmpeg("[0:v]", "[bg1]", dur_a, 0.0,      variant),
            _build_fg_ffmpeg("[0:v]", "[fg1]", variant,  dur_a, 0.0),
            "[bg1][fg1]overlay=(W-w)/2:(H-h)/2[frame1]",
            _build_bg_ffmpeg("[2:v]", "[bg2]", dur_b, t_switch,  variant2),
            _build_fg_ffmpeg("[2:v]", "[fg2]", variant2, dur_b, t_switch),
            "[bg2][fg2]overlay=(W-w)/2:(H-h)/2[frame2]",
            f"[frame1][frame2]xfade=transition=fade:offset={t_switch-0.2:.2f}:duration=0.4[frame]",
        ]
    else:
        filters += [
            _build_bg_ffmpeg("[0:v]", "[bg]", duration, 0.0, variant),
            _build_fg_ffmpeg("[0:v]", "[fg]", variant, duration, 0.0),
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[frame]",
        ]

    # ── Fade out ──────────────────────────────────────────────────────────────
    fade = (
        "[frame]"
        f"fade=t=in:st=0:d={FADE_IN_SEC:.2f},"
        f"fade=t=out:st={fade_out_start:.2f}:d={FADE_OUT_SEC:.2f}"
        "[vfaded]"
    )
    filters.append(fade)
    last_label = "[vfaded]"

    if not (font and DRAWTEXT_OK):
        filters.append(f"{last_label}copy[vout]")
        return ";".join(filters)

    # ── 4. Watermark (siempre visible) ────────────────────────────────────────
    safe_wm = _escape_drawtext(WATERMARK_TEXT)
    wm = (
        f"{last_label}"
        f"drawtext=fontfile='{font}'"
        f":text='{safe_wm}'"
        f":fontsize={WATERMARK_SZ}"
        f":fontcolor={WATERMARK_COLOR}"
        f":x=w-text_w-28:y=60"
        f":shadowcolor=black@0.8:shadowx=2:shadowy=2"
        "[vwm]"
    )
    filters.append(wm)
    last_label = "[vwm]"

    # ── 5a. Verse/tema label — esquina superior izquierda, todo el video ─────
    if verse_label:
        safe_verse = _escape_drawtext(verse_label.upper())
        verse_filter = (
            f"{last_label}"
            f"drawtext=fontfile='{font}'"
            f":text='{safe_verse}'"
            f":fontsize={VERSE_FONTSIZE}"
            f":fontcolor={VERSE_COLOR}"
            f":x=28:y=100"
            f":shadowcolor=black@0.9:shadowx=2:shadowy=2"
            f":box=1:boxcolor={VERSE_BG_COLOR}:boxborderw=14"
            "[vverse]"
        )
        filters.append(verse_filter)
        last_label = "[vverse]"

    # ── 5b. Hook text (primeros HOOK_DUR segundos, antes de la voz) ──────────
    if hook_text:
        safe_hook = _escape_drawtext(hook_text)
        # Fade in 0.3s, visible hasta HOOK_DUR, fade out 0.3s
        hook_filter = (
            f"{last_label}"
            f"drawtext=fontfile='{font}'"
            f":text='{safe_hook}'"
            f":fontsize={HOOK_FONTSIZE}"
            f":fontcolor={HOOK_COLOR}"
            f":x=(w-text_w)/2"
            f":y={HOOK_Y_POS}"
            f":shadowcolor=black@0.9:shadowx=3:shadowy=3"
            f":borderw={STROKE_WIDTH}:bordercolor=black@0.6"
            f":enable='between(t,0,{HOOK_DUR:.2f})'"
            f":alpha='if(lt(t,0.3),t/0.3,if(gt(t,{HOOK_DUR-0.3:.2f}),({HOOK_DUR:.2f}-t)/0.3,1))'"
            "[vhook]"
        )
        filters.append(hook_filter)
        last_label = "[vhook]"

    # ── 6. Vignette cinematográfico (bordes oscuros, foco al centro) ─────────
    # geq genera gradiente radial oscuro en las esquinas — look premium
    vignette = (
        f"{last_label}"
        "geq=lum='lum(X,Y)':"
        "cb='cb(X,Y)':"
        "cr='cr(X,Y)':"
        f"a='255*pow(1-sqrt(((X-{SHORT_W//2})/({SHORT_W//2}*1.1))^2+((Y-{SHORT_H//2})/({SHORT_H//2}*1.05))^2),0.45)'"
        "[vvig]"
    )
    # Alternativa más simple y compatible: overlay de negro con alpha radial
    # Si geq no funciona, usamos drawbox con alpha en las esquinas
    # Por ahora usamos el método de overlay de color negro transparente en bordes
    # que es más compatible con ffmpeg sin libvmaf
    vignette_safe = (
        f"{last_label}"
        f"vignette=angle=PI/4:mode=forward:eval=frame"
        "[vvig]"
    )
    filters.append(vignette_safe)
    last_label = "[vvig]"

    # ── 7. Subtítulos en oro con fade-in por segmento ─────────────────────────
    for idx, seg in enumerate(subtitle_segments):
        safe_text = _escape_drawtext(seg.text)
        next_label = f"[vsub{idx}]" if idx < len(subtitle_segments) - 1 else "[vsubs]"
        enable = f"between(t,{seg.start_sec:.3f},{seg.end_sec:.3f})"
        # Fade-in suave: primeros SUB_FADE_IN_DUR segundos de cada segmento
        fade_expr = (
            f"if(lt(t-{seg.start_sec:.3f},{SUB_FADE_IN_DUR}),"
            f"(t-{seg.start_sec:.3f})/{SUB_FADE_IN_DUR},1)"
        )
        sub = (
            f"{last_label}"
            f"drawtext=fontfile='{font}'"
            f":text='{safe_text}'"
            f":fontsize={SUB_FONTSIZE}"
            f":fontcolor={SUB_COLOR_GOLD}"
            f":x=(w-text_w)/2"
            f":y={SUB_Y_POS}"
            f":shadowcolor=black@0.9:shadowx=3:shadowy=3"
            f":borderw={STROKE_WIDTH}:bordercolor=black"
            f":line_spacing={SUB_LINE_SPACING}"
            f":enable='{enable}'"
            f":alpha='{fade_expr}'"
            f"{next_label}"
        )
        filters.append(sub)
        last_label = next_label

    if not subtitle_segments:
        filters.append(f"{last_label}copy[vsubs]")
        last_label = "[vsubs]"
    else:
        last_label = "[vsubs]"

    # ── 9. CTA últimos 3.5s ───────────────────────────────────────────────────
    safe_cta = _escape_drawtext(cta_text)
    cta_filter = (
        f"{last_label}"
        f"drawtext=fontfile='{font}'"
        f":text='{safe_cta}'"
        f":fontsize={CTA_FONTSIZE}"
        f":fontcolor={SUB_COLOR_CTA}"
        f":x=(w-text_w)/2"
        f":y={CTA_Y_POS}"
        f":shadowcolor=black@0.9:shadowx=2:shadowy=2"
        f":borderw=2:bordercolor=black"
        f":enable='between(t,{cta_start:.2f},{duration:.2f})'"
        f":alpha='if(lt(t,{cta_start+0.4:.2f}),(t-{cta_start:.2f})/0.4,1)'"
        "[vout]"
    )
    filters.append(cta_filter)

    return ";".join(filters)


# ─── Video base filter (sin texto — solo imagen + KB + vignette) ──────────────
def _build_video_base(duration: float, has_image2: bool, variant: str, oracion_id: str) -> str:
    """
    Construye el filter_complex de video SIN texto.
    Output label: [vvig] — listo para overlay de text layers.
    """
    filters: list[str] = []

    if has_image2 and duration > IMAGE_SWITCH_SEC + 4:
        t_switch = IMAGE_SWITCH_SEC
        dur_a, dur_b = t_switch, duration - t_switch
        variant2 = KB_VARIANTS[(KB_VARIANTS.index(variant) + 2) % len(KB_VARIANTS)]
        filters += [
            _build_bg_ffmpeg("[0:v]", "[bg1]", dur_a, 0.0, variant),
            _build_fg_ffmpeg("[0:v]", "[fg1]", variant, dur_a, 0.0),
            "[bg1][fg1]overlay=(W-w)/2:(H-h)/2[frame1]",
            _build_bg_ffmpeg("[2:v]", "[bg2]", dur_b, t_switch, variant2),
            _build_fg_ffmpeg("[2:v]", "[fg2]", variant2, dur_b, t_switch),
            "[bg2][fg2]overlay=(W-w)/2:(H-h)/2[frame2]",
            f"[frame1][frame2]xfade=transition=fade:offset={t_switch-0.2:.2f}:duration=0.4[frame]",
        ]
    else:
        filters += [
            _build_bg_ffmpeg("[0:v]", "[bg]", duration, 0.0, variant),
            _build_fg_ffmpeg("[0:v]", "[fg]", variant, duration, 0.0),
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[frame]",
        ]

    fade_out_start = max(0.0, duration - FADE_OUT_SEC)
    filters.append(
        f"[frame]fade=t=in:st=0:d={FADE_IN_SEC:.2f},"
        f"fade=t=out:st={fade_out_start:.2f}:d={FADE_OUT_SEC:.2f},"
        f"vignette=angle=PI/4:mode=forward:eval=frame"
        "[vvig]"
    )
    return ";".join(filters)


def _build_audio_filter_indexed(duration: float, has_music: bool, music_idx: int) -> str:
    """Audio filter con índice explícito para música."""
    fade_out_start = max(0.0, duration - CROSSFADE_SEC)
    narr_filter = (
        "[1:a]"
        "highpass=f=100,"
        "equalizer=f=250:t=o:w=200:g=-3,"
        "equalizer=f=3000:t=o:w=800:g=+4,"
        "equalizer=f=8000:t=o:w=3000:g=-2,"
        "acompressor=threshold=0.089:ratio=3:attack=5:release=50:makeup=2,"
        "aecho=0.8:0.6:40:0.12,"
        f"afade=t=in:ss=0:d={FADE_IN_SEC:.2f},"
        f"afade=t=out:st={fade_out_start:.2f}:d={CROSSFADE_SEC:.2f},"
        "loudnorm=I=-14:TP=-1:LRA=7"
        "[narr]"
    )
    if has_music:
        vol = 10 ** (MUSIC_VOL_DB / 20)
        music_filter = (
            f"[{music_idx}:a]"
            f"volume={vol:.4f},"
            f"atrim=0:{duration:.2f},"
            "aloop=loop=-1:size=2e9[bg]"
        )
        return f"{narr_filter};{music_filter};[narr][bg]amix=inputs=2:duration=first:dropout_transition=0.5[a]"
    return narr_filter.replace("[narr]", "[a]")


# ─── Audio filter (legacy — kept for reference) ──────────────────────────────
def _build_audio_filter(duration: float, has_music: bool, has_image2: bool = False) -> str:
    """
    v2: EQ + compressor + reverb sutil en voz TTS.
    Música a -18dB (soporte emocional audible).
    """
    fade_out_start = max(0.0, duration - CROSSFADE_SEC)

    # Voice EQ chain — de voz bancaria a voz devocional
    narr_filter = (
        f"[1:a]"
        # Limpiar rumble y nasalidad TTS
        "highpass=f=100,"
        "equalizer=f=250:t=o:w=200:g=-3,"      # quita barro nasal
        "equalizer=f=3000:t=o:w=800:g=+4,"     # presencia y calidez
        "equalizer=f=8000:t=o:w=3000:g=-2,"    # recorta sibilancias
        # Compresión para consistencia
        "acompressor=threshold=0.089:ratio=3:attack=5:release=50:makeup=2,"
        # Reverb de sala pequeña — sensación sagrada, no corporativa
        "aecho=0.8:0.6:40:0.12,"
        # Fade y normalización
        f"afade=t=in:ss=0:d={FADE_IN_SEC:.2f},"
        f"afade=t=out:st={fade_out_start:.2f}:d={CROSSFADE_SEC:.2f},"
        "loudnorm=I=-14:TP=-1:LRA=7"
        "[narr]"
    )

    if has_music:
        music_vol_linear = 10 ** (MUSIC_VOL_DB / 20)  # -18dB = 0.1259
        # Si hay imagen2, ocupa input 2 (video) → música es input 3
        # Si no hay imagen2, música es input 2
        music_idx = "3" if has_image2 else "2"
        music_filter = (
            f"[{music_idx}:a]"
            f"volume={music_vol_linear:.4f},"
            f"atrim=0:{duration:.2f},"
            "aloop=loop=-1:size=2e9"
            "[bg]"
        )
        mix_filter = "[narr][bg]amix=inputs=2:duration=first:dropout_transition=0.5[a]"
        return f"{narr_filter};{music_filter};{mix_filter}"
    else:
        return f"{narr_filter.replace('[narr]', '[a]')}"


# ─── Core render function ──────────────────────────────────────────────────────
def render_short_clip(cfg: ShortClipConfig) -> Path:
    """
    Renderiza un Short vertical 1080x1920 — v4 Pillow text engine.

    PRE-FLIGHT: verifica PIL disponible antes de hacer nada.
    TEXT ENGINE: Pillow genera PNGs RGBA → ffmpeg overlay (NO drawtext).
    """
    # ── Pre-flight ────────────────────────────────────────────────────────────
    verify_text_engine()   # falla rápido si PIL no disponible

    if cfg.out_path.exists() and not cfg.force:
        size_mb = cfg.out_path.stat().st_size / 1024 / 1024
        print(f"  [short] Cache hit: {cfg.out_path.name} ({size_mb:.1f}MB)")
        return cfg.out_path

    cfg.out_path.parent.mkdir(parents=True, exist_ok=True)
    txt_dir = cfg.out_path.parent / f"_txt_{cfg.oracion_id}"
    txt_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    print(f"  [short] Renderizando {cfg.oracion_id} [Pillow text engine]...")

    # ── Audio duration ────────────────────────────────────────────────────────
    duration = _get_audio_duration(cfg.narr_path)
    print(f"  [short] Duración: {duration:.1f}s")

    # ── Subtitle segments ─────────────────────────────────────────────────────
    subtitle_segments = build_subtitle_segments(
        text=cfg.text,
        audio_duration=duration,
        hook_text=cfg.hook_text,
        hook_duration=HOOK_DUR if cfg.hook_text else 0.0,
    )

    # ── Generar PNGs + text track via concat demuxer ──────────────────────────
    # v5 perf fix: 1 text track video → 1 overlay (era 51 overlays = 24 min)
    text_layers = generate_all_layers(
        segments=subtitle_segments,
        out_dir=txt_dir,
        duration=duration,
        hook_text=cfg.hook_text,
        verse_label=cfg.verse_label,
        cta_text=cfg.cta_text,
        hook_dur=HOOK_DUR,
        cta_dur=CTA_DUR,
    )
    print(f"  [short] {len(text_layers)} capas texto | generando text track...")
    text_track = build_text_track(text_layers, txt_dir, duration, fps=cfg.fps)
    print(f"  [short] text track: {text_track.name}")

    # ── Video base filter ─────────────────────────────────────────────────────
    has_image2 = cfg.image2_path is not None and cfg.image2_path.exists()
    variant    = _kb_variant(cfg.oracion_id)
    vf_base    = _build_video_base(duration, has_image2, variant, cfg.oracion_id)

    # 1 overlay: alpha_composite del text track sobre el video base
    full_vf = vf_base + ";[vvig][txt_trk]overlay=0:0:format=auto[vout]"

    # ── Audio filter ──────────────────────────────────────────────────────────
    # Inputs: 0=img1, 1=narr, [2=img2], N=txt_track, [N+1=music]
    base_inputs = 2 + (1 if has_image2 else 0)
    txt_track_idx = base_inputs       # txt_track input index
    music_idx     = base_inputs + 1   # music comes after txt_track
    af = _build_audio_filter_indexed(duration, has_music=cfg.music_path is not None, music_idx=music_idx)

    full_filter = f"{full_vf};{af}"

    # ── Construir comando ffmpeg ───────────────────────────────────────────────
    video_duration = duration + 0.5
    cmd: list[str] = ["ffmpeg", "-y"]
    cmd += ["-loop", "1", "-t", f"{video_duration:.2f}", "-i", str(cfg.image_path)]   # 0
    cmd += ["-i", str(cfg.narr_path)]                                                   # 1
    if has_image2:
        dur_b = duration - IMAGE_SWITCH_SEC + 1.0
        cmd += ["-loop", "1", "-t", f"{dur_b:.2f}", "-i", str(cfg.image2_path)]        # 2
    cmd += ["-i", str(text_track)]                                                      # txt_track
    if cfg.music_path:
        cmd += ["-stream_loop", "-1", "-i", str(cfg.music_path)]                        # last

    # Mapear txt_track como label [txt_trk]
    filter_with_label = full_filter.replace(
        "[vvig][txt_trk]overlay",
        f"[vvig][{txt_track_idx}:v]overlay"
    )

    cmd += ["-filter_complex", filter_with_label]
    cmd += ["-map", "[vout]", "-map", "[a]"]
    cmd += ["-t", f"{duration:.2f}"]
    cmd += ["-c:v", "libx264", "-preset", cfg.preset,
            "-b:v", DEFAULT_BITRATE, "-r", str(cfg.fps),
            "-s", SHORT_RES, "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", DEFAULT_AUDIO_BITRATE, "-ar", "44100"]
    cmd += ["-movflags", "+faststart",
            "-metadata", f"title={cfg.oracion_id}",
            "-metadata", "comment=Versiculos de Dios — @VersiculoDeDios"]
    cmd.append(str(cfg.out_path))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [short] STDERR:\n{result.stderr[-1200:]}")
        raise RuntimeError(f"ffmpeg falló {cfg.oracion_id} (code {result.returncode})")

    if not cfg.out_path.exists():
        raise RuntimeError(f"ffmpeg OK pero no creó {cfg.out_path}")

    # Cleanup text PNGs temporales
    shutil.rmtree(txt_dir, ignore_errors=True)

    elapsed = time.time() - t0
    size_mb = cfg.out_path.stat().st_size / 1024 / 1024
    print(f"  [short] ✓ {elapsed:.1f}s → {cfg.out_path.name} ({size_mb:.1f}MB, {duration:.1f}s) [Pillow text]")
    return cfg.out_path


# ─── Batch render ─────────────────────────────────────────────────────────────
def render_shorts_batch(
    configs: list[ShortClipConfig],
    max_workers: int = 3,
) -> list[Path]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results: dict[int, Path] = {}
    errors: dict[int, Exception] = {}

    def _render_one(idx_cfg: tuple[int, ShortClipConfig]) -> tuple[int, Path]:
        idx, cfg = idx_cfg
        return idx, render_short_clip(cfg)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(_render_one, (i, cfg)): i
            for i, cfg in enumerate(configs)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result_idx, path = future.result()
                results[result_idx] = path
                print(f"  [batch] Short {result_idx + 1}/{len(configs)} completado")
            except Exception as e:
                errors[idx] = e
                print(f"  [batch] ERROR short {idx + 1}: {e}")

    if errors:
        failed_ids = [configs[i].oracion_id for i in sorted(errors.keys())]
        print(f"  [batch] {len(errors)} shorts fallaron: {failed_ids}")

    return [results[i] for i in range(len(configs)) if i in results]
