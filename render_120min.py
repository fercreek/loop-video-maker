"""
render_120min.py — Render 120-minute relaxation/sleep videos for YouTube.

Usage:
    .venv/bin/python3 render_120min.py

Different from render_60min.py:
  - 120 minutes (288 verses × 25s each)
  - Only 3 relaxation moods: Paz profunda + Meditacion + Sanacion
  - 25s/verse: slower transitions — more meditative, ideal for sleep
  - Output: output/youtube_120min/<tema>/<tema>_120min.mp4
  - All 8 themes rendered in series (~8 min total on M-series Mac)

Target audience: sleep / background meditation / deep relaxation.
"""
from __future__ import annotations

import sys
import os
import glob
import time

sys.path.insert(0, ".")

from core.verse_gen import cargar_versiculos, versiculos_a_lista
from core.music_gen import generate_playlist
from core.video_render import renderizar_video_fast
from core.render_logger import RenderLogger, clean_file
from core.thumbnail_gen import generate_thumbnail_for_theme
from config import (
    RENDER_FPS,
    VERSES_PER_BG,
    PARALLEL_JOBS,
    WATERMARK,
    CROSSFADE_SECONDS,
    VISUAL_TEMPLATES,
    FONDOS_GLOB,
    THEME_LABELS,
    ALL_THEMES,
)

# ─── 120min config — overrides config.py defaults ────────────────────────────
TARGET_MINUTES       = 120
SECONDS_PER_VERSE    = 25     # slower = more meditative (288 versos × 25s = 120min)
OUTPUT_BASE          = "output/youtube_120min"

# Only the 3 most relaxing moods — every theme gets same playlist flavour
RELAXING_MOODS = ["Paz profunda", "Meditacion", "Sanacion"]

# All 8 themes at 120min — same content basis, different verse sets
VIDEOS = [(t, RELAXING_MOODS, THEME_LABELS[t]) for t in ALL_THEMES]

def _get_bg_images(theme: str = "") -> list[str]:
    """Return fondos pool shuffled deterministically per-theme."""
    import random as _r
    paths = sorted([
        p for p in glob.glob(FONDOS_GLOB)
        if not os.path.basename(p).startswith("imagen_")
    ])
    seed = hash(theme or "default") & 0xFFFFFFFF
    _r.Random(seed).shuffle(paths)
    return paths


# Static pool used for display counts
BG_IMAGES = _get_bg_images()

os.makedirs(OUTPUT_BASE, exist_ok=True)

_gate_results: list = []   # acumula quality gate results del batch


def render_video(theme: str, moods: list[str], label: str) -> str:
    """Generate a single 120-minute relaxation video."""
    print(f"\n{'='*60}")
    print(f"  VIDEO 120min: {label}  (tema: {theme})")
    print(f"{'='*60}")
    theme_bg_images = _get_bg_images(theme)

    datos = cargar_versiculos(theme)
    verses = versiculos_a_lista(datos)
    unique_count = len(verses)
    total_seconds = TARGET_MINUTES * 60
    target_count = total_seconds // SECONDS_PER_VERSE
    print(f"  Versos: {unique_count} únicos → {target_count} ciclados = {total_seconds//60} min")
    print(f"  Pace: {SECONDS_PER_VERSE}s/verso  (vs 20s en 60min — más meditativo)")

    video_dir = os.path.join(OUTPUT_BASE, theme)
    os.makedirs(video_dir, exist_ok=True)
    audio_dir = os.path.join(video_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    output_path = os.path.join(video_dir, f"{theme}_120min.mp4")

    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  ⚠️  Ya existe ({size_mb:.0f} MB) — saltando. Usa --force para re-renderizar.")
        return output_path

    # Audio playlist — 3 moods más relajantes, 7200s
    print(f"  Generando audio ({'+'.join(moods)}, {total_seconds}s)...")
    t0 = time.time()
    audio_path = generate_playlist(
        moods=moods,
        total_seconds=total_seconds,
        output_dir=audio_dir,
        crossfade_seconds=CROSSFADE_SECONDS,
    )
    print(f"  Audio listo en {time.time()-t0:.0f}s → {audio_path}")

    logger = RenderLogger(
        theme=theme,
        config={
            "duration_min": TARGET_MINUTES,
            "fps": RENDER_FPS,
            "seconds_per_verse": SECONDS_PER_VERSE,
            "watermark": WATERMARK,
            "workers": PARALLEL_JOBS,
            "moods": moods,
            "background_images": theme_bg_images,
            "text_style": "fea",
            "format": "120min_relaxation",
        },
    )
    logger.start()

    print(f"  Renderizando ({target_count} clips × {SECONDS_PER_VERSE}s, {RENDER_FPS}fps, {PARALLEL_JOBS} workers)...")
    t0 = time.time()

    def progress(pct: float, msg: str) -> None:
        bar = "█" * int(pct * 30) + "░" * (30 - int(pct * 30))
        elapsed = time.time() - t0
        eta = (elapsed / pct * (1 - pct)) if pct > 0.01 else 0
        print(f"\r  [{bar}] {pct*100:.0f}%  ETA {eta/60:.0f}min  {msg[:40]}", end="", flush=True)

    try:
        renderizar_video_fast(
            imagen_path=theme_bg_images[0],
            musica_path=audio_path,
            versiculos=verses,
            duracion_total_segundos=total_seconds,
            segundos_por_versiculo=SECONDS_PER_VERSE,
            config_texto={"fade_duration": 2.5, "watermark_text": WATERMARK},
            output_path=output_path,
            efecto_imagen="Zoom lento ↗",
            format_key="youtube_1080",
            background_images=theme_bg_images,
            verses_per_background=VERSES_PER_BG,
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
        freed = clean_file(audio_path, label="audio playlist post-render 120min")
        if freed:
            print(f"  [clean] Audio WAV eliminado ({freed:.0f} MB liberados)")
        try:
            os.rmdir(audio_dir)
        except OSError:
            pass
        # Thumbnail para canal — misma calidad visual que 60min
        try:
            thumb_path = generate_thumbnail_for_theme(theme, video_dir)
            print(f"  [thumb] Thumbnail generado → {thumb_path}")
        except Exception as exc:
            print(f"  [thumb] Warning: {exc}")

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
    import argparse

    parser = argparse.ArgumentParser(description="Renderiza batch de videos 120min relajación.")
    parser.add_argument("--themes", nargs="+", metavar="THEME",
                        help=f"Temas a renderizar (default: todos — {ALL_THEMES})")
    parser.add_argument("--force", action="store_true",
                        help="Re-renderizar aunque ya exista el .mp4")
    args = parser.parse_args()

    themes_to_render = args.themes if args.themes else ALL_THEMES

    print(f"\n🎬 Iniciando renders 120 minutos — Relajación / Sleep")
    print(f"   Temas:   {', '.join(themes_to_render)}")
    print(f"   Moods:   {' + '.join(RELAXING_MOODS)}")
    print(f"   Fondos:  {len(BG_IMAGES)} pinturas  |  {SECONDS_PER_VERSE}s/verso  |  {RENDER_FPS}fps")
    print(f"   Output:  {os.path.abspath(OUTPUT_BASE)}/\n")

    if args.force:
        # Remove existing outputs for forced re-render
        for t in themes_to_render:
            p = os.path.join(OUTPUT_BASE, t, f"{t}_120min.mp4")
            if os.path.exists(p):
                os.remove(p)
                print(f"  [force] Eliminado: {p}")

    all_start = time.time()
    completed = []
    failed = []

    for theme in themes_to_render:
        moods, label = RELAXING_MOODS, THEME_LABELS.get(theme, theme.capitalize())
        try:
            out = render_video(theme, moods, label)
            completed.append(out)
        except Exception as exc:
            print(f"\n  ERROR en tema '{theme}': {exc}", file=sys.stderr)
            failed.append(theme)

    total_elapsed = time.time() - all_start
    print(f"\n{'='*60}")
    print(f"  Completados: {len(completed)}  |  Fallidos: {len(failed)}")
    if completed:
        print(f"  Tiempo total: {total_elapsed / 3600:.2f} horas  (~{total_elapsed/len(completed)/60:.1f} min/video)")
        print(f"  Carpeta: {os.path.abspath(OUTPUT_BASE)}")
    if failed:
        print(f"  Errores: {', '.join(failed)}", file=sys.stderr)

    if _gate_results:
        from core.quality_gate import print_batch_report
        print_batch_report(_gate_results)

    if failed:
        sys.exit(1)
