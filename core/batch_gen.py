"""
core/batch_gen.py — Batch content generation orchestrator.

Generates multiple posts, reels, and shorts in one operation,
organized by format for easy Metricool bulk upload.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime

from core.formats import FORMAT_DEFS, get_dimensions
from core.verse_gen import cargar_versiculos, versiculos_a_lista
from core.image_gen import generar_imagen
from core.music_gen import generar_musica
from core.post_gen import generar_post
from core.caption_gen import generar_caption, guardar_caption
from core.video_render import renderizar_video
from core import db


@dataclass
class BatchConfig:
    """Configuration for a batch generation run."""
    theme: str = "paz"
    formats: list = field(default_factory=lambda: ["post_1080"])
    num_verses: int = 10
    layout_preset: str = "centrado_bajo"
    watermark_text: str = ""
    use_gemini: bool = False
    gemini_api_key: str = ""
    image_preset_key: str = None
    audio_mood: str = "Paz profunda"
    seconds_per_verse: int = 15
    efecto_imagen: str = "Zoom lento ↗"
    output_base_dir: str = "output"


def generar_batch(config: BatchConfig, progress_callback=None) -> dict:
    """
    Generate a batch of content (posts, reels, shorts) for a theme.

    Args:
        config: BatchConfig with all generation parameters.
        progress_callback: Optional callable(float, str) for progress updates.

    Returns:
        Dict with keys: posts, reels, shorts, captions, youtube, total, batch_dir.
    """
    # 1. Load verses
    datos = cargar_versiculos(config.theme)
    versiculos = versiculos_a_lista(datos)
    verses_to_use = versiculos[:config.num_verses]
    if not verses_to_use:
        raise ValueError(f"No hay versículos para el tema '{config.theme}'")

    # 2. Create output directories
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = os.path.join(config.output_base_dir, f"batch_{ts}")
    dirs = _create_output_dirs(batch_dir, config.formats)

    # 3. Create batch job record
    formats_str = ",".join(config.formats)
    total_items = len(verses_to_use) * len(config.formats)
    batch_id = db.record_batch_job(
        theme=config.theme,
        formats=formats_str,
        total_items=total_items,
    )

    # 4. Generate background image (one per batch)
    if progress_callback:
        progress_callback(0.05, "Generando imagen de fondo...")

    # Choose the largest resolution needed for this batch
    max_w, max_h = 0, 0
    for fmt_key in config.formats:
        w, h = get_dimensions(fmt_key)
        if w * h > max_w * max_h:
            max_w, max_h = w, h

    imagen_path = generar_imagen(
        prompt=config.theme,
        api_key=config.gemini_api_key if config.use_gemini else "",
        output_dir=batch_dir,
        preset_key=config.image_preset_key,
        resolution=(max_w, max_h),
        theme=config.theme,
    )

    image_id = db.record_image(
        path=imagen_path, style="batch",
        theme=config.theme, width=max_w, height=max_h,
    )

    # 5. Generate audio if video formats are requested
    audio_path = None
    audio_id = None
    video_formats = [f for f in config.formats if FORMAT_DEFS.get(f, {}).get("output_type") == "video"]

    if video_formats:
        if progress_callback:
            progress_callback(0.10, "Generando música de fondo...")

        # Generate enough audio for the longest video
        max_duration = config.seconds_per_verse * len(verses_to_use)
        audio_path = generar_musica(
            mood=config.audio_mood,
            duracion_segundos=max_duration,
            api_key="",
            output_dir=batch_dir,
        )
        audio_id = db.record_audio(
            path=audio_path, mood=config.audio_mood,
            duration_sec=max_duration, generator="ambient",
        )

    # 6. Generate content for each verse × format
    results = {
        "posts": [],
        "reels": [],
        "shorts": [],
        "youtube": [],
        "captions": [],
        "total": 0,
        "batch_dir": os.path.abspath(batch_dir),
    }

    completed = 0
    for i, verso in enumerate(verses_to_use):
        texto = verso.get("texto", "")
        referencia = verso.get("referencia", "")
        slug = f"{i + 1:02d}_{config.theme}_{referencia.lower().replace(':', '').replace(' ', '_')}"

        # Generate caption (shared across all formats)
        caption = generar_caption(texto, referencia, config.theme)
        caption_path = os.path.join(dirs.get("captions", batch_dir), f"{slug}_caption.txt")
        guardar_caption(caption, caption_path)
        results["captions"].append(caption_path)

        for fmt_key in config.formats:
            fmt_def = FORMAT_DEFS.get(fmt_key, {})
            output_type = fmt_def.get("output_type", "image")

            if output_type == "image":
                # Static post (JPG)
                out_path = os.path.join(dirs.get("posts", batch_dir), f"{slug}.jpg")
                generar_post(
                    texto=texto,
                    referencia=referencia,
                    imagen_fondo_path=imagen_path,
                    output_path=out_path,
                    layout_preset=config.layout_preset,
                    format_key=fmt_key,
                    watermark_text=config.watermark_text,
                )
                results["posts"].append(out_path)

                db.record_post(
                    path=out_path, format_key=fmt_key,
                    theme=config.theme, verse_ref=referencia,
                    caption_path=caption_path, batch_id=batch_id,
                    image_id=image_id,
                    width=fmt_def.get("width", 1080),
                    height=fmt_def.get("height", 1080),
                )

            elif output_type == "video":
                # Video (reel, short, or youtube)
                if fmt_key == "reel_1080":
                    subdir = "reels"
                    result_key = "reels"
                    suffix = "_reel"
                elif fmt_key == "youtube_1080":
                    subdir = "youtube"
                    result_key = "youtube"
                    suffix = "_yt"
                else:
                    subdir = "shorts"
                    result_key = "shorts"
                    suffix = "_short"

                out_path = os.path.join(dirs.get(subdir, batch_dir), f"{slug}{suffix}.mp4")

                renderizar_video(
                    imagen_path=imagen_path,
                    musica_path=audio_path,
                    versiculos=[verso],
                    duracion_total_segundos=config.seconds_per_verse,
                    segundos_por_versiculo=config.seconds_per_verse,
                    config_texto={
                        "fade_duration": 1.5,
                        "watermark_text": config.watermark_text,
                    },
                    output_path=out_path,
                    efecto_imagen=config.efecto_imagen,
                    format_key=fmt_key,
                    text_style="fea",
                    layout_preset=config.layout_preset,
                )
                results[result_key].append(out_path)

                db.record_video(
                    path=out_path, theme=config.theme,
                    duration_min=config.seconds_per_verse // 60,
                    seconds_per_verse=config.seconds_per_verse,
                    image_id=image_id, audio_id=audio_id,
                    efecto_imagen=config.efecto_imagen,
                    verses_count=1,
                )

            completed += 1
            results["total"] = completed

            if progress_callback:
                pct = 0.15 + 0.80 * (completed / total_items)
                progress_callback(pct, f"Generado {completed}/{total_items}: {referencia} ({fmt_key})")

            db.update_batch_progress(batch_id, completed)

    # 7. Mark batch as completed
    db.update_batch_progress(batch_id, completed, status="completed")

    if progress_callback:
        progress_callback(1.0, f"¡Batch completado! {completed} archivos en {batch_dir}")

    return results


def _create_output_dirs(batch_dir: str, formats: list) -> dict:
    """Create output subdirectories and return a mapping of type → dir path."""
    dirs = {"captions": os.path.join(batch_dir, "captions")}

    for fmt_key in formats:
        fmt_def = FORMAT_DEFS.get(fmt_key, {})
        if fmt_def.get("output_type") == "image":
            dirs["posts"] = os.path.join(batch_dir, "posts")
        elif fmt_key == "reel_1080":
            dirs["reels"] = os.path.join(batch_dir, "reels")
        elif fmt_key == "youtube_1080":
            dirs["youtube"] = os.path.join(batch_dir, "youtube")
        else:
            dirs["shorts"] = os.path.join(batch_dir, "shorts")

    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    return dirs
