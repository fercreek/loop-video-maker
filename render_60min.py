"""
render_60min.py — Render multiple 60-minute YouTube devotional videos.

Usage:
    .venv/bin/python3 render_60min.py

Each video:
  - 60 minutes (180 verses × 20s each)
  - 11 oil painting backgrounds cycling every verse
  - Random Ken Burns per verse
  - Multi-mood audio playlist
  - 12fps (smooth enough for slow pans, 2× faster render)
  - 4Mbps bitrate (great quality for YouTube)
"""
from __future__ import annotations

import sys
import os
import glob
import time
import math

sys.path.insert(0, ".")

from core.verse_gen import cargar_versiculos, versiculos_a_lista
from core.music_gen import generate_playlist
from core.video_render import renderizar_video_fast
from core.render_logger import RenderLogger, clean_file
from core.thumbnail_gen import generate_thumbnail_for_theme
from config import (
    SECONDS_PER_VERSE,
    RENDER_FPS,
    PARALLEL_JOBS,
    WATERMARK,
    CROSSFADE_SECONDS,
    VISUAL_TEMPLATES,
    OUTPUT_BASE_60MIN as OUTPUT_BASE,
    FONDOS_GLOB,
    THEME_MOODS,
    THEME_LABELS,
    ALL_THEMES,
)

TARGET_MINUTES = 60

# Oil paintings pool (all 11)
BG_IMAGES = sorted([
    p for p in glob.glob(FONDOS_GLOB)
    if not os.path.basename(p).startswith("imagen_")
])

# Videos to render: (theme, audio_moods, label) — sourced from config
VIDEOS = [(t, THEME_MOODS[t], THEME_LABELS[t]) for t in ALL_THEMES]

os.makedirs(OUTPUT_BASE, exist_ok=True)

# Accumulates quality gate results across the batch (populated in render_video)
_gate_results: list = []


def cycle_verses(verses: list, target_count: int) -> list:
    """Repeat verse list until we have exactly target_count verses."""
    if not verses:
        return []
    result = []
    while len(result) < target_count:
        result.extend(verses)
    return result[:target_count]


def render_video(theme: str, moods: list, label: str):
    """Generate a single 60-minute video for the given theme."""
    print(f"\n{'='*60}")
    print(f"  VIDEO: {label}  (tema: {theme})")
    print(f"{'='*60}")

    # Load verses (engine will cycle them internally)
    datos = cargar_versiculos(theme)
    verses = versiculos_a_lista(datos)
    unique_count = len(verses)
    total_seconds = TARGET_MINUTES * 60
    target_count = total_seconds // SECONDS_PER_VERSE
    print(f"  Versos: {unique_count} únicos → {target_count} ciclados = {total_seconds//60} min")

    # Output paths
    video_dir = os.path.join(OUTPUT_BASE, theme)
    os.makedirs(video_dir, exist_ok=True)
    audio_dir = os.path.join(video_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    output_path = os.path.join(video_dir, f"{theme}_60min.mp4")

    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  ⚠️  Ya existe ({size_mb:.0f} MB) — saltando.")
        return output_path

    # Generate multi-mood audio
    print(f"  Generando audio playlist ({'+'.join(moods)}, {total_seconds}s)...")
    t0 = time.time()
    audio_path = generate_playlist(
        moods=moods,
        total_seconds=total_seconds,
        output_dir=audio_dir,
        crossfade_seconds=CROSSFADE_SECONDS,
    )
    print(f"  Audio listo en {time.time()-t0:.0f}s → {audio_path}")

    # Start learning log
    logger = RenderLogger(
        theme=theme,
        config={
            "duration_min": TARGET_MINUTES,
            "fps": RENDER_FPS,
            "seconds_per_verse": SECONDS_PER_VERSE,
            "watermark": WATERMARK,
            "workers": PARALLEL_JOBS,
            "moods": moods,
            "background_images": BG_IMAGES,
            "text_style": "fea",
        },
    )
    logger.start()

    # Render video
    print(f"  Renderizando video ({unique_count} versos × {SECONDS_PER_VERSE}s, {RENDER_FPS}fps)...")
    print(f"  Fondos: {len(BG_IMAGES)} pinturas rotando cada verso")
    t0 = time.time()

    def progress(pct, msg):
        bar = "█" * int(pct * 30) + "░" * (30 - int(pct * 30))
        elapsed = time.time() - t0
        eta = (elapsed / pct * (1 - pct)) if pct > 0.01 else 0
        print(f"\r  [{bar}] {pct*100:.0f}%  ETA {eta/60:.0f}min  {msg[:40]}", end="", flush=True)

    try:
        renderizar_video_fast(
            imagen_path=BG_IMAGES[0],
            musica_path=audio_path,
            versiculos=verses,
            duracion_total_segundos=total_seconds,
            segundos_por_versiculo=SECONDS_PER_VERSE,
            config_texto={"fade_duration": 2.0, "watermark_text": WATERMARK},
            output_path=output_path,
            efecto_imagen="Zoom lento ↗",
            format_key="youtube_1080",
            background_images=BG_IMAGES,
            verses_per_background=1,
            random_ken_burns=True,
            render_fps=RENDER_FPS,
            parallel_jobs=PARALLEL_JOBS,
            progress_callback=progress,
            visual_templates=VISUAL_TEMPLATES,
        )
        elapsed = time.time() - t0
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"\n  ✅ Completado en {elapsed/60:.0f} min  —  {output_path}  ({size_mb:.0f} MB)")
        logger.end(
            output_path=output_path,
            elapsed_sec=elapsed,
            unique_verses=unique_count,
            total_verses=target_count,
        )
        # Clean up audio WAV (baked into MP4, can regenerate if needed)
        freed = clean_file(audio_path, label="audio playlist post-render")
        if freed:
            print(f"  [clean] Audio WAV eliminado ({freed:.0f} MB liberados)")
        try:
            os.rmdir(audio_dir)
        except OSError:
            pass
        # Auto-generate thumbnail alongside the video
        try:
            thumb_path = generate_thumbnail_for_theme(theme, video_dir)
            print(f"  [thumb] Thumbnail generado → {thumb_path}")
        except Exception as exc:
            print(f"  [thumb] Warning: no se pudo generar thumbnail: {exc}")

        # Quality gate — eval + auto-fix LUFS si necesario
        try:
            from core.quality_gate import gate as _qgate
            qg = _qgate(output_path, nominal_min=TARGET_MINUTES)
            icon = "✅" if qg["pass"] else "⚠️ "
            fix_msg = (
                f"  [LUFS fix: {qg['lufs_before']:.1f}→{qg['lufs_after']:.1f}]"
                if qg["fixed"] else ""
            )
            print(f"  {icon} Quality gate: {qg['score']}/100{fix_msg}")
            for iss in qg["issues"]:
                print(f"       ⚠ {iss}")
            _gate_results.append(qg)
        except Exception as exc:
            print(f"  [quality-gate] warning: {exc}")

    except Exception as exc:
        elapsed = time.time() - t0
        logger.end(output_path=output_path, elapsed_sec=elapsed, error=str(exc))
        raise

    return output_path


if __name__ == "__main__":
    print(f"\n🎬 Iniciando renders 60 minutos")
    print(f"   Fondos: {len(BG_IMAGES)} pinturas")
    print(f"   FPS: {RENDER_FPS}  |  {SECONDS_PER_VERSE}s/verso  |  {TARGET_MINUTES} min/video")
    print(f"   Output: {OUTPUT_BASE}/\n")

    all_start = time.time()
    for theme, moods, label in VIDEOS:
        render_video(theme, moods, label)

    total_elapsed = time.time() - all_start
    print(f"\n🎉 TODOS LOS VIDEOS COMPLETADOS en {total_elapsed/3600:.1f} horas")
    print(f"   Carpeta: {os.path.abspath(OUTPUT_BASE)}")

    if _gate_results:
        from core.quality_gate import print_batch_report
        print_batch_report(_gate_results)
