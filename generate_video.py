"""
generate_video.py — Flexible CLI for generating devotional videos.

Usage:
  .venv/bin/python3 generate_video.py --theme paz --duration 60 --output output/
  .venv/bin/python3 generate_video.py --theme amor --duration 10 --output output/test/
  .venv/bin/python3 generate_video.py --themes paz fe esperanza --duration 60
"""
from __future__ import annotations

import argparse
import glob
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.verse_gen import cargar_versiculos, versiculos_a_lista
from core.music_gen import generate_playlist
from core.video_render import renderizar_video_fast
from core.render_logger import RenderLogger, clean_file, clean_dir
from core.thumbnail_gen import generate_thumbnail_for_theme
from config import (
    VISUAL_TEMPLATES,
    CROSSFADE_SECONDS,
    SECONDS_PER_VERSE as DEFAULT_SECONDS_PER_VERSE,
    RENDER_FPS as DEFAULT_FPS,
    PARALLEL_JOBS as DEFAULT_WORKERS,
    WATERMARK as DEFAULT_WATERMARK,
    FONDOS_GLOB,
    get_moods,
)


# ─── Background pool ──────────────────────────────────────────────────────────

def get_bg_images() -> list[str]:
    """Return all oil painting backgrounds (exclude imagen_* files)."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    paths = sorted([
        p for p in glob.glob(os.path.join(project_dir, FONDOS_GLOB))
        if not os.path.basename(p).startswith("imagen_")
    ])
    return paths


# ─── Single video render ──────────────────────────────────────────────────────

def render_one(
    theme: str,
    duration_min: int,
    output_dir: str,
    fps: int,
    seconds_per_verse: int,
    watermark: str,
    workers: int,
    force: bool,
    bg_images: list[str],
) -> str:
    total_seconds = duration_min * 60

    os.makedirs(output_dir, exist_ok=True)
    audio_dir = os.path.join(output_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{theme}_{duration_min}min.mp4")

    if os.path.exists(output_path) and not force:
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  [skip] {output_path} ya existe ({size_mb:.0f} MB). Usa --force para sobreescribir.")
        return output_path

    # Load verses
    datos = cargar_versiculos(theme)
    verses = versiculos_a_lista(datos)
    target_count = total_seconds // seconds_per_verse or 1
    unique_count = len(verses)
    print(f"  Versos: {unique_count} unicos -> {target_count} ciclados = {duration_min} min")

    # Generate audio
    moods = get_moods(theme)
    print(f"  Generando audio playlist ({'+'.join(moods)}, {total_seconds}s)...")
    t0 = time.time()
    audio_path = generate_playlist(
        moods=moods,
        total_seconds=total_seconds,
        output_dir=audio_dir,
        crossfade_seconds=CROSSFADE_SECONDS,
    )
    print(f"  Audio listo en {time.time() - t0:.0f}s -> {audio_path}")

    # Start learning log
    logger = RenderLogger(
        theme=theme,
        config={
            "duration_min": duration_min,
            "fps": fps,
            "seconds_per_verse": seconds_per_verse,
            "watermark": watermark,
            "workers": workers,
            "moods": moods,
            "background_images": bg_images,
            "text_style": "fea",
        },
    )
    logger.start()

    # Render video
    print(f"  Renderizando video ({fps}fps, {seconds_per_verse}s/verso, {len(bg_images)} fondos)...")
    t0 = time.time()

    def progress(pct: float, msg: str) -> None:
        bar = "=" * int(pct * 30) + "-" * (30 - int(pct * 30))
        elapsed = time.time() - t0
        eta_s = (elapsed / pct * (1 - pct)) if pct > 0.01 else 0
        eta_min = math.ceil(eta_s / 60)
        print(
            f"\r  [{bar}] {pct * 100:5.1f}%  ETA ~{eta_min}min  {msg[:40]}",
            end="",
            flush=True,
        )

    try:
        renderizar_video_fast(
            imagen_path=bg_images[0],
            musica_path=audio_path,
            versiculos=verses,
            duracion_total_segundos=total_seconds,
            segundos_por_versiculo=seconds_per_verse,
            config_texto={"fade_duration": 2.0, "watermark_text": watermark},
            output_path=output_path,
            efecto_imagen="Zoom lento ->",
            format_key="youtube_1080",
            background_images=bg_images,
            verses_per_background=1,
            random_ken_burns=True,
            render_fps=fps,
            parallel_jobs=workers,
            progress_callback=progress,
            visual_templates=VISUAL_TEMPLATES,
        )
        elapsed = time.time() - t0
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\n  Completado en {elapsed / 60:.0f} min  ->  {output_path}  ({size_mb:.0f} MB)")
        logger.end(
            output_path=output_path,
            elapsed_sec=elapsed,
            unique_verses=unique_count,
            total_verses=target_count,
        )
        # Clean up audio WAV (baked into MP4, no longer needed — can regenerate)
        freed = clean_file(audio_path, label="audio playlist post-render")
        if freed:
            print(f"  [clean] Audio WAV eliminado ({freed:.0f} MB liberados)")
        # Clean up empty audio dir
        try:
            os.rmdir(audio_dir)
        except OSError:
            pass
        # Auto-generate thumbnail
        try:
            thumb_path = generate_thumbnail_for_theme(theme, output_dir)
            print(f"  [thumb] Thumbnail generado → {thumb_path}")
        except Exception as exc:
            print(f"  [thumb] Warning: no se pudo generar thumbnail: {exc}")
    except Exception as exc:
        elapsed = time.time() - t0
        logger.end(output_path=output_path, elapsed_sec=elapsed, error=str(exc))
        raise

    return output_path


# ─── CLI ──────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Genera videos devocionales de 60 minutos para YouTube.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--theme", metavar="THEME",
                       help="Un tema (p.ej. paz, fe, amor)")
    group.add_argument("--themes", nargs="+", metavar="THEME",
                       help="Varios temas para renderizado en lote")

    p.add_argument("--duration", type=int, default=60,
                   metavar="MINUTES",
                   help="Duracion del video en minutos (default: 60)")
    p.add_argument("--output", default="output/youtube/",
                   metavar="DIR",
                   help="Directorio de salida (default: output/youtube/)")
    p.add_argument("--fps", type=int, default=DEFAULT_FPS,
                   help=f"Frames por segundo (default: {DEFAULT_FPS})")
    p.add_argument("--seconds-per-verse", type=int, default=DEFAULT_SECONDS_PER_VERSE,
                   dest="seconds_per_verse",
                   help=f"Segundos por versiculo (default: {DEFAULT_SECONDS_PER_VERSE})")
    p.add_argument("--watermark", default=DEFAULT_WATERMARK,
                   help=f"Texto de marca de agua (default: {DEFAULT_WATERMARK})")
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                   help=f"Trabajos ffmpeg en paralelo (default: {DEFAULT_WORKERS})")
    p.add_argument("--force", action="store_true",
                   help="Sobreescribir videos existentes")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    themes = [args.theme] if args.theme else args.themes
    bg_images = get_bg_images()

    if not bg_images:
        print("ERROR: No se encontraron imagenes en output/fondos/*.jpg", file=sys.stderr)
        sys.exit(1)

    print(f"\nGenerador de videos devocionales")
    print(f"  Temas:    {', '.join(themes)}")
    print(f"  Duracion: {args.duration} min")
    print(f"  FPS:      {args.fps}  |  {args.seconds_per_verse}s/verso")
    print(f"  Fondos:   {len(bg_images)} pinturas")
    print(f"  Output:   {os.path.abspath(args.output)}\n")

    all_start = time.time()
    completed = []
    failed = []

    for theme in themes:
        print(f"\n{'='*60}")
        print(f"  TEMA: {theme.upper()}")
        print(f"{'='*60}")
        theme_dir = os.path.join(args.output, theme)
        try:
            out = render_one(
                theme=theme,
                duration_min=args.duration,
                output_dir=theme_dir,
                fps=args.fps,
                seconds_per_verse=args.seconds_per_verse,
                watermark=args.watermark,
                workers=args.workers,
                force=args.force,
                bg_images=bg_images,
            )
            completed.append(out)
        except Exception as exc:
            print(f"\n  ERROR en tema '{theme}': {exc}", file=sys.stderr)
            failed.append(theme)

    total_elapsed = time.time() - all_start
    print(f"\n{'='*60}")
    print(f"  Completados: {len(completed)}  |  Fallidos: {len(failed)}")
    print(f"  Tiempo total: {total_elapsed / 3600:.2f} horas")
    if completed:
        print(f"  Carpeta: {os.path.abspath(args.output)}")
    if failed:
        print(f"  Temas con error: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
