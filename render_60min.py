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

# ─── Config ─────────────────────────────────────────────────────────────────
SECONDS_PER_VERSE  = 20       # 20s per verse = 180 verses for 60 min
TARGET_MINUTES     = 60
RENDER_FPS         = 12       # 12fps — fine for slow Ken Burns pans
PARALLEL_JOBS      = 6        # ffmpeg subprocesses in parallel (tune to CPU cores)
WATERMARK          = "@FeEnAcción"
OUTPUT_BASE        = "output/youtube_60min"

# Oil paintings pool (all 11)
BG_IMAGES = sorted([
    p for p in glob.glob("output/fondos/*.jpg")
    if not os.path.basename(p).startswith("imagen_")
])

# Videos to render: (theme, audio_moods, label)
VIDEOS = [
    ("paz",       ["Paz profunda", "Meditacion", "Sanacion"],    "Paz de Dios"),
    ("fe",        ["Adoración", "Devoción", "Paz profunda"],     "Fe que mueve montañas"),
    ("esperanza", ["Sanacion", "Adoración", "Meditacion"],       "Esperanza en Dios"),
]

os.makedirs(OUTPUT_BASE, exist_ok=True)


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
    total_seconds = TARGET_MINUTES * 60
    target_count = total_seconds // SECONDS_PER_VERSE
    print(f"  Versos: {len(verses)} únicos → {target_count} ciclados = {total_seconds//60} min")

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
        crossfade_seconds=8.0,
    )
    print(f"  Audio listo en {time.time()-t0:.0f}s → {audio_path}")

    # Render video
    print(f"  Renderizando video ({len(verses)} versos × {SECONDS_PER_VERSE}s, {RENDER_FPS}fps)...")
    print(f"  Fondos: {len(BG_IMAGES)} pinturas rotando cada verso")
    t0 = time.time()

    def progress(pct, msg):
        bar = "█" * int(pct * 30) + "░" * (30 - int(pct * 30))
        elapsed = time.time() - t0
        eta = (elapsed / pct * (1 - pct)) if pct > 0.01 else 0
        print(f"\r  [{bar}] {pct*100:.0f}%  ETA {eta/60:.0f}min  {msg[:40]}", end="", flush=True)

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
        text_style="fea",
        layout_preset="centrado_bajo",
        background_images=BG_IMAGES,
        verses_per_background=1,
        random_ken_burns=True,
        render_fps=RENDER_FPS,
        parallel_jobs=PARALLEL_JOBS,
        progress_callback=progress,
    )
    elapsed = time.time() - t0
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\n  ✅ Completado en {elapsed/60:.0f} min  —  {output_path}  ({size_mb:.0f} MB)")
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
