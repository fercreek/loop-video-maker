"""
core/shorts_render.py — Motor ffmpeg para Shorts verticales 9:16 1080x1920.

Responsabilidades:
  - Escalar imagen horizontal 16:9 → vertical 9:16 con blur+crop (no pillarbox)
  - Overlay narración + música fondo a -30dB
  - Quemar subtítulos sincronizados con timing del audio
  - Fade in/out suaves
  - Entregar MP4 listo para YouTube Shorts

No genera audio ni imágenes — solo mux/ffmpeg.

Uso típico (desde render_short.py):
    from core.shorts_render import render_short_clip, build_subtitle_segments
    segments = build_subtitle_segments(text, audio_path)
    render_short_clip(ShortClipConfig(...))
"""
from __future__ import annotations

import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

# ─── Dimensiones 9:16 ─────────────────────────────────────────────────────────
SHORT_W = 1080
SHORT_H = 1920
SHORT_RES = f"{SHORT_W}x{SHORT_H}"

# ─── Valores por defecto ──────────────────────────────────────────────────────
DEFAULT_FPS           = 30        # 30fps — Shorts necesita fluidez
DEFAULT_PRESET        = "fast"    # faster → peor compresión; slower → más tiempo
DEFAULT_BITRATE       = "4000k"   # YouTube Shorts acepta hasta 8Mbps para 1080p
DEFAULT_AUDIO_BITRATE = "192k"
MUSIC_VOL_DB          = -30       # música de fondo muy baja (-30dB = 0.032 lineal)
NARR_VOL              = 1.0
FADE_IN_SEC           = 0.4
FADE_OUT_SEC          = 0.8
CROSSFADE_SEC         = 0.6

# ─── Subtítulos ───────────────────────────────────────────────────────────────
# Cormorant Garamond 72px — igual que canal
FONT_PATHS = [
    # Proyecto local
    str(Path(__file__).parent.parent / "assets" / "fonts" / "CormorantGaramond-Regular.ttf"),
    # Fallback sistema macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
SUB_FONTSIZE   = 72     # px en 1080x1920 — legible en mobile
SUB_FONTCOLOR  = "white"
SUB_SHADOW_COL = "black@0.7"
SUB_BOX_COL    = "black@0.45"
SUB_Y_POS      = "(h*3/4)"   # 75% desde arriba → zona segura inferior
SUB_MAX_CHARS  = 38          # máximo por línea antes de partir
SUB_LINE_SPACING = 12        # px extra entre líneas del drawtext

WATERMARK_TEXT  = "@VersiculoDeDios"
WATERMARK_SZ    = 30
WATERMARK_COLOR = "white@0.65"

# Palabras por minuto de referencia para timing estimado (macOS say 145wpm)
WPM_REFERENCE = 145


# ─── Data classes ─────────────────────────────────────────────────────────────
@dataclass
class SubtitleSegment:
    """Segmento de subtítulo con timing."""
    text: str
    start_sec: float
    end_sec: float


@dataclass
class ShortClipConfig:
    """Configuración completa para renderizar 1 Short."""
    oracion_id: str           # Ej: "fe_001"
    text: str                 # Texto completo de la oración
    narr_path: Path           # WAV/MP3 de la narración
    image_path: Path          # Imagen de fondo (cualquier aspect ratio)
    out_path: Path            # Salida MP4

    music_path: Path | None = None   # Música de fondo (None = sin música)
    hook_text: str = ""              # Texto del hook (se muestra primero ~1.5s)
    fps: int = DEFAULT_FPS
    preset: str = DEFAULT_PRESET
    force: bool = False              # Re-renderizar aunque exista


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _find_font() -> str:
    """Devuelve el primer path de fuente disponible en el sistema."""
    import os
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return ""


def _get_audio_duration(audio_path: Path) -> float:
    """Retorna duración en segundos de un archivo de audio."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(audio_path),
        ],
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


# ─── Subtitle timing ──────────────────────────────────────────────────────────
def build_subtitle_segments(
    text: str,
    audio_duration: float,
    hook_text: str = "",
    hook_duration: float = 1.5,
) -> list[SubtitleSegment]:
    """
    Genera segmentos de subtítulo con timing proporcional al texto.

    Estrategia: divide el texto en frases por puntuación, asigna tiempo
    proporcional a la cantidad de palabras. El hook se muestra en los primeros
    hook_duration segundos antes de la oración.

    Args:
        text:           texto completo de la oración
        audio_duration: duración total del audio en segundos
        hook_text:      texto del hook (se muestra en el inicio)
        hook_duration:  duración del hook en segundos

    Returns:
        Lista de SubtitleSegment ordenada cronológicamente
    """
    import re

    segments: list[SubtitleSegment] = []
    offset = 0.0

    # Hook
    if hook_text:
        segments.append(SubtitleSegment(
            text=hook_text.upper(),
            start_sec=0.0,
            end_sec=hook_duration,
        ))
        offset = hook_duration

    # Dividir oración en frases (por . , ; : ¡ ¿ !)
    # Preserva el delimitador en la frase
    raw_phrases = re.split(r"(?<=[.,;:!?])\s+", text.strip())
    phrases = [p.strip() for p in raw_phrases if p.strip()]

    if not phrases:
        return segments

    # Tiempo disponible para la oración (descontando hook)
    available = audio_duration - offset
    if available <= 0:
        available = audio_duration

    # Peso proporcional a palabras
    word_counts = [len(p.split()) for p in phrases]
    total_words = sum(word_counts)
    if total_words == 0:
        return segments

    current_time = offset
    for i, (phrase, wc) in enumerate(zip(phrases, word_counts)):
        fraction = wc / total_words
        duration = available * fraction
        # Mínimo 0.8s por segmento para legibilidad
        duration = max(0.8, duration)

        # Wrap automático si la frase es muy larga
        lines = _wrap_text(phrase, SUB_MAX_CHARS)
        display_text = "\n".join(lines)

        end_time = min(current_time + duration, audio_duration - 0.2)
        segments.append(SubtitleSegment(
            text=display_text,
            start_sec=current_time,
            end_sec=end_time,
        ))
        current_time = end_time + 0.05  # micro-gap entre segmentos

    return segments


def _wrap_text(text: str, max_chars: int) -> list[str]:
    """
    Parte un texto en líneas de máximo max_chars caracteres,
    respetando palabras completas.
    """
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + (1 if current else 0) <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


# ─── FFmpeg video filter ───────────────────────────────────────────────────────
def _build_video_filter(
    duration: float,
    subtitle_segments: list[SubtitleSegment],
    font: str,
) -> str:
    """
    Construye el filtro de video ffmpeg completo:
    - Escala imagen 16:9 → 9:16 con técnica blur+crop (no pillarbox)
    - Fade in/out
    - Watermark
    - Subtítulos quemados segmento a segmento

    La técnica blur+crop:
    1. Escala y voltea horizontalmente para crear espejo del fondo
    2. Aplica Gaussian blur heavy (r=40) → queda como fondo difuso
    3. Escala la imagen original al alto (1920) con aspect ratio preservado
    4. Overlay centrado sobre el fondo difuso
    """
    fade_out_start = max(0.0, duration - FADE_OUT_SEC)

    # ── Construir cadena de filtros ──
    filters: list[str] = []

    # 1. Fondo difuminado 9:16 (portrait blur background)
    # [0:v] → escala para llenar ancho 1080 manteniendo AR → crop a 1920 alto → blur
    bg = (
        "[0:v]"
        "scale=1080:-1:flags=lanczos,"            # escala al ancho
        "crop=1080:1920:(iw-1080)/2:(ih-1920)/2," # centrar si excede
        "gblur=sigma=40,"                          # blur fuerte → bokeh
        "setsar=1"
        "[bg]"
    )
    # 2. Imagen principal escalada para llenar alto (pillar-fit)
    fg = (
        "[0:v]"
        "scale=-1:1920:flags=lanczos,"            # escalar al alto preservando AR
        "crop=1080:1920:(iw-1080)/2:0,"           # crop horizontal si más ancho
        "setsar=1"
        "[fg]"
    )
    # 3. Overlay fg sobre bg centrado
    overlay = "[bg][fg]overlay=(W-w)/2:(H-h)/2[frame]"

    # 4. Fade in/out
    fade = (
        "[frame]"
        f"fade=t=in:st=0:d={FADE_IN_SEC:.2f},"
        f"fade=t=out:st={fade_out_start:.2f}:d={FADE_OUT_SEC:.2f}"
        "[vfaded]"
    )

    filters += [bg, fg, overlay, fade]
    last_label = "[vfaded]"

    # 5. Watermark
    if font and DRAWTEXT_OK:
        safe_wm = WATERMARK_TEXT.replace("@", "\\@")
        wm_filter = (
            f"{last_label}"
            f"drawtext="
            f"fontfile='{font}'"
            f":text='{safe_wm}'"
            f":fontsize={WATERMARK_SZ}"
            f":fontcolor={WATERMARK_COLOR}"
            f":x=w-text_w-24:y=h-text_h-28"
            f":shadowcolor=black@0.6:shadowx=1:shadowy=1"
            "[vwm]"
        )
        filters.append(wm_filter)
        last_label = "[vwm]"

    # 6. Subtítulos quemados por segmento
    if font and DRAWTEXT_OK and subtitle_segments:
        current_label = last_label
        for idx, seg in enumerate(subtitle_segments):
            # Escapar texto para drawtext (comillas simples, comas, dos puntos)
            safe_text = (
                seg.text
                .replace("\\", "\\\\")
                .replace("'", "’")   # reemplaza comilla recta → curva (evita escape issues)
                .replace(":", "\\:")
                .replace(",", "\\,")
                .replace("[", "\\[")
                .replace("]", "\\]")
            )
            next_label = f"[vsub{idx}]" if idx < len(subtitle_segments) - 1 else "[vout]"
            enable = f"between(t,{seg.start_sec:.3f},{seg.end_sec:.3f})"

            sub_filter = (
                f"{current_label}"
                f"drawtext="
                f"fontfile='{font}'"
                f":text='{safe_text}'"
                f":fontsize={SUB_FONTSIZE}"
                f":fontcolor={SUB_FONTCOLOR}"
                f":x=(w-text_w)/2"
                f":y={SUB_Y_POS}"
                f":box=1:boxcolor={SUB_BOX_COL}:boxborderw=18"
                f":shadowcolor={SUB_SHADOW_COL}:shadowx=2:shadowy=2"
                f":line_spacing={SUB_LINE_SPACING}"
                f":enable='{enable}'"
                f"{next_label}"
            )
            filters.append(sub_filter)
            current_label = next_label

        # Si no se cerró con [vout], renombrar último
        if subtitle_segments:
            last_label = "[vout]"
        # Si no hay subs, el output ya viene de last_label
    else:
        # Sin drawtext disponible → renombrar último label a [vout]
        filters.append(f"{last_label}copy[vout]")
        last_label = "[vout]"

    return ";".join(filters)


# ─── Audio filter ─────────────────────────────────────────────────────────────
def _build_audio_filter(duration: float, has_music: bool) -> str:
    """
    Construye filtro de audio:
    - Narración con fade in/out y volumen normalizado
    - Música de fondo a MUSIC_VOL_DB si se proporciona
    - amix con duración de la narración como referencia

    Entradas ffmpeg esperadas:
    - [1:a] = narración
    - [2:a] = música (si has_music=True)
    """
    fade_out_start = max(0.0, duration - CROSSFADE_SEC)

    narr_filter = (
        f"[1:a]"
        f"volume={NARR_VOL},"
        f"afade=t=in:ss=0:d={FADE_IN_SEC:.2f},"
        f"afade=t=out:st={fade_out_start:.2f}:d={CROSSFADE_SEC:.2f}"
        "[narr]"
    )

    if has_music:
        # Convierte dB a factor lineal: 10^(db/20)
        music_vol_linear = 10 ** (MUSIC_VOL_DB / 20)
        music_filter = (
            f"[2:a]"
            f"volume={music_vol_linear:.4f},"
            f"atrim=0:{duration:.2f},"
            f"aloop=loop=-1:size=2e9"
            "[bg]"
        )
        mix_filter = "[narr][bg]amix=inputs=2:duration=first:dropout_transition=0.5[a]"
        return f"{narr_filter};{music_filter};{mix_filter}"
    else:
        return f"{narr_filter.replace('[narr]', '[a]')}"


# ─── Core render function ──────────────────────────────────────────────────────
def render_short_clip(cfg: ShortClipConfig) -> Path:
    """
    Renderiza un Short vertical 1080x1920 con subtítulos quemados.

    Flujo:
    1. Lee duración del audio de narración
    2. Genera segmentos de subtítulo con timing proporcional
    3. Construye filtros ffmpeg (video + audio)
    4. Ejecuta ffmpeg y verifica resultado

    Args:
        cfg: ShortClipConfig con todas las rutas y parámetros

    Returns:
        Path al MP4 generado

    Raises:
        RuntimeError: si ffmpeg falla o el archivo de salida no se crea
    """
    if cfg.out_path.exists() and not cfg.force:
        size_mb = cfg.out_path.stat().st_size / 1024 / 1024
        print(f"  [short] Cache hit: {cfg.out_path.name} ({size_mb:.1f}MB)")
        return cfg.out_path

    cfg.out_path.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    print(f"  [short] Renderizando {cfg.oracion_id}...")

    # 1. Duración audio
    duration = _get_audio_duration(cfg.narr_path)
    print(f"  [short] Duración audio: {duration:.1f}s")

    # 2. Subtítulos con timing
    subtitle_segments = build_subtitle_segments(
        text=cfg.text,
        audio_duration=duration,
        hook_text=cfg.hook_text,
        hook_duration=1.5 if cfg.hook_text else 0.0,
    )
    print(f"  [short] {len(subtitle_segments)} segmentos de subtítulo")

    # 3. Fuente disponible
    font = _find_font()
    if not font:
        print("  [short] WARN: No font found — subtítulos desactivados")

    # 4. Filtros ffmpeg
    vf = _build_video_filter(duration, subtitle_segments, font)
    af = _build_audio_filter(duration, has_music=cfg.music_path is not None)

    # 5. Construir comando ffmpeg
    # Nota: imagen loop de duración exacta del audio + pequeño buffer
    video_duration = duration + 0.5

    cmd: list[str] = ["ffmpeg", "-y"]

    # Input 0: imagen de fondo (loop)
    cmd += ["-loop", "1", "-t", f"{video_duration:.2f}", "-i", str(cfg.image_path)]

    # Input 1: narración
    cmd += ["-i", str(cfg.narr_path)]

    # Input 2: música (opcional, con stream_loop para repetir)
    if cfg.music_path:
        cmd += ["-stream_loop", "-1", "-i", str(cfg.music_path)]

    # Filtros
    cmd += ["-filter_complex", f"{vf};{af}"]

    # Mapeo
    cmd += ["-map", "[vout]", "-map", "[a]"]

    # Duración exacta
    cmd += ["-t", f"{duration:.2f}"]

    # Codec video
    cmd += [
        "-c:v", "libx264",
        "-preset", cfg.preset,
        "-b:v", DEFAULT_BITRATE,
        "-r", str(cfg.fps),
        "-s", SHORT_RES,
        "-pix_fmt", "yuv420p",  # compatibilidad máxima YouTube
    ]

    # Codec audio
    cmd += [
        "-c:a", "aac",
        "-b:a", DEFAULT_AUDIO_BITRATE,
        "-ar", "44100",
    ]

    # Metadata para YouTube Shorts
    cmd += [
        "-movflags", "+faststart",       # streaming web
        "-metadata", f"title={cfg.oracion_id}",
        "-metadata", "comment=Versiculos de Dios — @VersiculoDeDios",
    ]

    cmd.append(str(cfg.out_path))

    # 6. Ejecutar
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Imprimir últimas 800 chars de stderr para diagnóstico
        stderr_tail = result.stderr[-800:] if result.stderr else "(vacío)"
        print(f"  [short] FFmpeg STDERR:\n{stderr_tail}")
        raise RuntimeError(f"ffmpeg falló renderizando {cfg.oracion_id} (code {result.returncode})")

    if not cfg.out_path.exists():
        raise RuntimeError(f"ffmpeg terminó OK pero no creó {cfg.out_path}")

    elapsed = time.time() - t0
    size_mb = cfg.out_path.stat().st_size / 1024 / 1024
    print(f"  [short] OK {elapsed:.1f}s → {cfg.out_path.name} ({size_mb:.1f}MB, {duration:.1f}s)")

    return cfg.out_path


# ─── Batch render ─────────────────────────────────────────────────────────────
def render_shorts_batch(
    configs: list[ShortClipConfig],
    max_workers: int = 3,
) -> list[Path]:
    """
    Renderiza múltiples Shorts en paralelo.

    Args:
        configs:     lista de ShortClipConfig — uno por short
        max_workers: threads paralelos (3 recomendado en Mac para no saturar memoria)

    Returns:
        Lista de Paths de MP4s generados, en el mismo orden que configs
    """
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
