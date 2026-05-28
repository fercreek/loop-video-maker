"""
render_sleep.py — Pipeline para sleeping content cristiano 60-120 min. v2

Stack:
  - Audio: MusicGen medium mono (facebook/musicgen-medium, ~4-5GB RAM)
  - Visual: 6 imágenes secuenciadas con xfade 3s + Ken-Burns alternado (zoom/pan)
  - Color: grading nocturno (colorbalance azul profundo + vignette)
  - Texto: Overlay título primeros 10s (Pillow)
  - Watermark: @VersiculoDeDios siempre visible

Output: mp4 1920x1080 @ 24fps, 60-120min, ~600MB-1.2GB
Anti-strike: música propia (MusicGen) + imágenes propias (mflux/AI pool)

Uso:
    # Test rápido (5 min)
    .venv/bin/python3 render_sleep.py --tema salmo91 --duration 5 --dry-run

    # 60 min Salmo 91
    .venv/bin/python3 render_sleep.py --tema salmo91 --duration 60

    # 120 min Promesas
    .venv/bin/python3 render_sleep.py --tema promesas --duration 120

    # Custom title + image
    .venv/bin/python3 render_sleep.py --titulo "Versículos Paz" --duration 90 \
        --bg fondo_ai_starry_desert.jpg --mood Reposo
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))
for _pyver in ["python3.13", "python3.12", "python3.11", "python3.10", "python3.9"]:
    _site = PROJECT_DIR / ".venv" / "lib" / _pyver / "site-packages"
    if _site.exists():
        sys.path.insert(0, str(_site))
        break

# ─── Paths ────────────────────────────────────────────────────────────────────
FONDOS_DIR  = PROJECT_DIR / "output" / "fondos"
MUSIC_CACHE = PROJECT_DIR / "audio" / "cache"
OUT_BASE    = PROJECT_DIR / "output" / "sleep"
OUT_BASE.mkdir(parents=True, exist_ok=True)

# ─── Defaults ─────────────────────────────────────────────────────────────────
RESOLUTION = "1920x1080"
RES_W, RES_H = 1920, 1080
FPS = 24
BITRATE = "2500k"
AUDIO_BITRATE = "192k"
INTRO_DUR = 10.0          # segundos de título visible al inicio
INTRO_FADE = 1.5
WATERMARK_TEXT = "@VersiculoDeDios"
MUSIC_VOL_DB = -12        # sleeping: más alto que Shorts (no hay voz que compita)
MUSICGEN_MODEL = "facebook/musicgen-medium"  # mono, ~4-5GB RAM — middle ground stereo-small vs stereo-medium

N_IMAGES   = 6            # imágenes en secuencia por video
XFADE_DUR  = 3.0          # segundos de crossfade entre imágenes
# Ken Burns patterns: alternated per image for cinematic variety
KB_PATTERNS = [
    "zoom_in",    # 1.00 → 1.04
    "pan_right",  # pan horizontal derecha
    "zoom_out",   # 1.04 → 1.00
    "pan_left",   # pan horizontal izquierda
    "zoom_in",
    "pan_right",
]

# ─── Sleep tema presets ───────────────────────────────────────────────────────
SLEEP_TEMAS = {
    "salmo91": {
        "titulo": "SALMO 91 PARA DORMIR · Protección Divina",
        "mood": "Reposo",
        "bg_candidates": ["fondo_ai_mount_sinai.jpg", "fondo_ai_starry_desert.jpg",
                          "fondo_ai_heaven_clouds.jpg"],
    },
    "salmo23": {
        "titulo": "SALMO 23 PARA DORMIR · El Buen Pastor",
        "mood": "Paz profunda",
        "bg_candidates": ["fondo_ai_cedar_forest.jpg", "fondo_ai_garden_eden.jpg",
                          "fondo_ai_morning_glory.jpg"],
    },
    "ansiedad": {
        "titulo": "VERSÍCULOS CONTRA ANSIEDAD · Para Dormir en Paz",
        "mood": "Reposo",
        "bg_candidates": ["fondo_ai_galilee_sunrise.jpg", "fondo_ai_heaven_clouds.jpg"],
    },
    "promesas": {
        "titulo": "PROMESAS DE DIOS PARA DORMIR · Descanso Sagrado",
        "mood": "Madrugada",
        "bg_candidates": ["fondo_ai_holy_land_sunset.jpg", "fondo_ai_aurora_faith.jpg"],
    },
    "rosario": {
        "titulo": "ROSARIO PARA DORMIR · Paz del Alma",
        "mood": "Devoción",
        "bg_candidates": ["fondo_ai_monastery_mountain.jpg", "fondo_ai_ancient_temple.jpg"],
    },
}


@dataclass
class SleepConfig:
    tema: str
    titulo: str
    mood: str
    duration_min: int
    bg_images: list  # list[Path] — 6 imágenes para secuencia xfade
    out_path: Path
    dry_run: bool = False


def _find_bg(candidates: list[str]) -> Path:
    """Devuelve el primer fondo del pool que existe (compat v1)."""
    for c in candidates:
        p = FONDOS_DIR / c
        if p.exists():
            return p
    available = sorted(FONDOS_DIR.glob("fondo_ai_*.jpg"))
    if not available:
        raise FileNotFoundError(f"Sin fondos en {FONDOS_DIR}")
    return available[0]


def _find_bg_multi(candidates: list[str], n: int = N_IMAGES) -> list:
    """
    Selecciona N imágenes diversas del pool para secuencia xfade.
    Prioriza los candidates del tema, luego rellena del pool completo.
    """
    import random
    # Collect candidate paths that exist
    priority = [FONDOS_DIR / c for c in candidates if (FONDOS_DIR / c).exists()]
    all_fondos = sorted(FONDOS_DIR.glob("fondo_ai_*.jpg"))
    # Exclude already-selected paths
    remaining = [p for p in all_fondos if p not in priority]
    random.shuffle(remaining)
    pool = priority + remaining
    selected = pool[:n]
    if len(selected) < n:
        # Repeat if not enough unique images
        while len(selected) < n:
            selected += pool[:n - len(selected)]
    return selected[:n]


def generate_audio(mood: str, duration_min: int, out_dir: Path, dry_run: bool = False) -> Path:
    """Genera audio ambient usando musicgen-medium (mono) — middle ground calidad/RAM."""
    from core.music_gen import generar_musica_musicgen
    model = MUSICGEN_MODEL
    out_path = out_dir / f"sleep_audio_{mood.replace(' ', '_')}_{duration_min}min.wav"
    if out_path.exists():
        print(f"  [audio] Cache hit: {out_path.name}")
        return out_path
    if dry_run:
        print(f"  [audio DRY] generaría {duration_min}min · {mood} · model={model}")
        return out_path
    total_sec = duration_min * 60
    print(f"  [audio] Generando {duration_min}min mood={mood} model={model}...")
    wav = generar_musica_musicgen(
        mood=mood,
        duracion_total=total_sec,
        duracion_clip=30,
        output_dir=str(out_dir),
        model_id=model,
    )
    import shutil
    shutil.copy(wav, str(out_path))
    return out_path


def build_overlay_pngs(titulo: str, out_dir: Path) -> tuple[Path, Path]:
    """Genera 2 PNGs RGBA via Pillow: titulo (centro) + watermark (top-right)."""
    from PIL import Image, ImageDraw, ImageFont
    # Title PNG (full frame, fondo transparente)
    title_png = out_dir / "_overlay_title.png"
    wm_png = out_dir / "_overlay_wm.png"

    # Try Montserrat first, fallback to system fonts
    font_paths = [
        str(PROJECT_DIR / "assets" / "fonts" / "Montserrat-ExtraBold.ttf"),
        "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    font_path = next((p for p in font_paths if os.path.exists(p)), None)

    # Title image
    img = Image.new("RGBA", (RES_W, RES_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 72) if font_path else ImageFont.load_default()
    # Wrap title if too long
    max_w = RES_W * 0.85
    lines = [titulo]
    while True:
        widest = max(draw.textbbox((0, 0), L, font=font)[2] for L in lines)
        if widest <= max_w or all(len(L.split()) == 1 for L in lines):
            break
        # split longest line in half by words
        idx = max(range(len(lines)), key=lambda i: draw.textbbox((0,0), lines[i], font=font)[2])
        words = lines[idx].split()
        mid = len(words) // 2
        lines = lines[:idx] + [" ".join(words[:mid]), " ".join(words[mid:])] + lines[idx+1:]
    line_h = font.getbbox("Mg")[3] + 16
    total_h = line_h * len(lines)
    y0 = (RES_H - total_h) // 2
    for i, L in enumerate(lines):
        bbox = draw.textbbox((0, 0), L, font=font)
        tw = bbox[2] - bbox[0]
        x = (RES_W - tw) // 2
        y = y0 + i * line_h
        # Shadow + text
        draw.text((x+3, y+3), L, font=font, fill=(0, 0, 0, 200))
        draw.text((x, y), L, font=font, fill=(255, 255, 255, 255))
    img.save(title_png)

    # Watermark image (esquina top-right, transparent fondo)
    wm_img = Image.new("RGBA", (RES_W, RES_H), (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(wm_img)
    wm_font = ImageFont.truetype(font_path, 32) if font_path else ImageFont.load_default()
    wbbox = wm_draw.textbbox((0, 0), WATERMARK_TEXT, font=wm_font)
    wtw = wbbox[2] - wbbox[0]
    wx = RES_W - wtw - 40
    wm_draw.text((wx+2, 42), WATERMARK_TEXT, font=wm_font, fill=(0, 0, 0, 180))
    wm_draw.text((wx, 40), WATERMARK_TEXT, font=wm_font, fill=(255, 255, 255, 170))
    wm_img.save(wm_png)

    return title_png, wm_png


def _kb_filter(pattern: str, seg_frames: int) -> str:
    """
    Returns a zoompan expression for one Ken Burns pattern.
    All patterns output RES_W x RES_H @ FPS.
    """
    F = seg_frames
    W, H = RES_W, RES_H
    scale_pad = int(W * 1.06)  # source upscaled so zoom/pan stays in-bounds

    if pattern == "zoom_in":
        # 1.00 → 1.04 centered
        return (
            f"scale={scale_pad}:-1:flags=lanczos,crop={W}:{H},"
            f"zoompan=z='1.00+0.04*on/{F}':d={F}:s={W}x{H}:fps={FPS}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',setsar=1"
        )
    elif pattern == "zoom_out":
        # 1.04 → 1.00 centered
        return (
            f"scale={scale_pad}:-1:flags=lanczos,crop={W}:{H},"
            f"zoompan=z='1.04-0.04*on/{F}':d={F}:s={W}x{H}:fps={FPS}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',setsar=1"
        )
    elif pattern == "pan_right":
        # slow pan left→right at constant zoom 1.03
        return (
            f"scale={scale_pad}:-1:flags=lanczos,crop={W}:{H},"
            f"zoompan=z=1.03:d={F}:s={W}x{H}:fps={FPS}"
            f":x='(iw-iw/zoom)*on/{F}':y='ih/2-(ih/zoom/2)',setsar=1"
        )
    else:  # pan_left
        return (
            f"scale={scale_pad}:-1:flags=lanczos,crop={W}:{H},"
            f"zoompan=z=1.03:d={F}:s={W}x{H}:fps={FPS}"
            f":x='(iw-iw/zoom)*(1-on/{F})':y='ih/2-(ih/zoom/2)',setsar=1"
        )


def build_video_filter(
    duration_sec: float,
    bg_images: list,
    title_png: Path,
    wm_png: Path,
    n_images: int = N_IMAGES,
) -> str:
    """
    Filter complex v2 — multi-image xfade + Ken Burns alternado + color grading.

    Inputs (ffmpeg -i order):
      [0..n-1] bg images (looped)
      [n]      watermark PNG
      [n+1]    title PNG
      [n+2]    audio (handled separately)

    Pipeline:
      1. Each image → alternating Ken Burns pattern
      2. xfade chain (fade 3s between segments)
      3. Color grading: colorbalance (night blue) + eq (saturation) + vignette
      4. Overlay watermark (always) + title (first 10s)
    """
    n = min(n_images, len(bg_images))
    seg_dur = duration_sec / n                  # effective seconds per image
    seg_frames = int(seg_dur * FPS)
    # Each image input needs slightly more than seg_dur to cover the xfade overlap
    input_dur = seg_dur + XFADE_DUR

    fade_out_start = duration_sec - 2.0
    wm_idx   = n       # watermark input index
    title_idx = n + 1  # title input index

    parts = []

    # Step 1 — Ken Burns per image
    for i in range(n):
        pattern = KB_PATTERNS[i % len(KB_PATTERNS)]
        kb = _kb_filter(pattern, seg_frames)
        parts.append(f"[{i}:v]{kb}[kb{i}]")

    # Step 2 — xfade chain
    # offset[i] = i*seg_dur - (i-1)*XFADE_DUR  (accounts for duration consumed by prior xfades)
    xf_offset = seg_dur - XFADE_DUR / 2  # == offset for i=1
    if n == 1:
        parts.append(f"[kb0]null[xfinal]")
    else:
        # First xfade (i=1): offset = seg_dur - XFADE_DUR/2
        first_out = "xfinal" if n == 2 else "xf1"
        parts.append(
            f"[kb0][kb1]xfade=transition=fade:duration={XFADE_DUR:.1f}"
            f":offset={xf_offset:.2f}[{first_out}]"
        )
        for i in range(2, n):
            prev_label = f"xf{i-1}"
            cur_label  = f"xf{i}" if i < n - 1 else "xfinal"
            # Correct cumulative offset: each prior xfade consumes XFADE_DUR from stream
            offset = i * seg_dur - (i - 1) * XFADE_DUR
            parts.append(
                f"[{prev_label}][kb{i}]xfade=transition=fade:duration={XFADE_DUR:.1f}"
                f":offset={offset:.2f}[{cur_label}]"
            )

    # Step 3 — color grading: night/sleep look
    # colorbalance: boost blue shadows+midtones, pull red highlights
    # eq: reduce saturation (0.75), slightly brighten gamma blue channel
    # vignette: subtle dark edges for depth
    parts.append(
        f"[xfinal]"
        f"colorbalance=rs=-0.08:gs=-0.05:bs=0.12:rm=-0.04:gm=-0.02:bm=0.08:rh=-0.10:gh=-0.05:bh=0.05,"
        f"eq=saturation=0.78:gamma_b=1.12,"
        f"vignette=PI/4,"
        f"fade=t=in:st=0:d=2.0,"
        f"fade=t=out:st={fade_out_start:.2f}:d=2.0"
        f"[vgraded]"
    )

    # Step 4 — overlays
    parts.append(f"[vgraded][{wm_idx}:v]overlay=0:0[vwm]")
    parts.append(
        f"[{title_idx}:v]format=rgba,"
        f"fade=t=in:st=0:d={INTRO_FADE:.2f}:alpha=1,"
        f"fade=t=out:st={INTRO_DUR - INTRO_FADE:.2f}:d={INTRO_FADE:.2f}:alpha=1[title]"
    )
    parts.append(
        f"[vwm][title]overlay=0:0:enable='between(t,0,{INTRO_DUR:.2f})'[vout]"
    )

    return ";".join(parts)


def build_audio_filter(duration_sec: float) -> str:
    """Audio filter: normaliza música, fade in/out, target LUFS -18 (sleep)."""
    fade_out_start = duration_sec - 3.0
    vol_linear = 10 ** (MUSIC_VOL_DB / 20)
    return (
        f"[1:a]volume={vol_linear:.4f},"
        f"afade=t=in:ss=0:d=2.0,"
        f"afade=t=out:st={fade_out_start:.2f}:d=3.0,"
        f"loudnorm=I=-18:TP=-1.5:LRA=11[a]"
    )


def render(cfg: SleepConfig) -> Path:
    if cfg.out_path.exists() and not cfg.dry_run:
        print(f"  ⚠️  Ya existe: {cfg.out_path}")
        return cfg.out_path

    out_dir = cfg.out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    n = len(cfg.bg_images)
    audio_path = generate_audio(cfg.mood, cfg.duration_min, out_dir, dry_run=cfg.dry_run)

    if cfg.dry_run:
        print(f"  [render DRY] {cfg.duration_min}min · {n} images · mood={cfg.mood}")
        for i, p in enumerate(cfg.bg_images):
            print(f"    img[{i}] {p.name}  ({KB_PATTERNS[i % len(KB_PATTERNS)]})")
        print(f"  Output: {cfg.out_path}")
        return cfg.out_path

    duration_sec = cfg.duration_min * 60
    seg_dur = duration_sec / n
    input_dur = seg_dur + XFADE_DUR + 1.0  # extra buffer

    title_png, wm_png = build_overlay_pngs(cfg.titulo, out_dir)

    vf = build_video_filter(duration_sec, cfg.bg_images, title_png, wm_png, n_images=n)
    af = build_audio_filter(duration_sec)
    audio_input_idx = n + 2  # bg images + wm + title
    full_filter = f"{vf};{af}".replace("[1:a]", f"[{audio_input_idx}:a]")

    # Build cmd: N bg image inputs + wm + title + audio
    cmd = ["ffmpeg", "-y"]
    for bg in cfg.bg_images:
        cmd += ["-loop", "1", "-t", f"{input_dur:.1f}", "-i", str(bg)]
    cmd += ["-loop", "1", "-t", f"{duration_sec + 1:.1f}", "-i", str(wm_png)]
    cmd += ["-loop", "1", "-t", f"{duration_sec + 1:.1f}", "-i", str(title_png)]
    cmd += ["-i", str(audio_path)]
    cmd += [
        "-filter_complex", full_filter,
        "-map", "[vout]", "-map", f"[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-b:v", BITRATE,
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-t", f"{duration_sec:.1f}",
        str(cfg.out_path),
    ]

    print(f"  [render] {cfg.duration_min}min · {n} imgs · xfade {XFADE_DUR}s → {cfg.out_path.name}...")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        err_log = out_dir / f"_ffmpeg_err_{cfg.tema}.log"
        err_log.write_text(result.stderr)
        raise RuntimeError(f"ffmpeg falló (code {result.returncode}). Log: {err_log}")

    size_mb = cfg.out_path.stat().st_size / 1024 / 1024
    print(f"  ✅ {elapsed:.1f}s render → {cfg.out_path.name} ({size_mb:.1f}MB)")
    return cfg.out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tema", choices=list(SLEEP_TEMAS.keys()), help="Tema preset")
    p.add_argument("--duration", type=int, default=60, help="Duración minutos (60, 90, 120)")
    p.add_argument("--titulo", help="Custom title (override tema preset)")
    p.add_argument("--mood", help="Custom mood (override tema preset)")
    p.add_argument("--bg", help="Custom background filename (en output/fondos/)")
    p.add_argument("--output", help="Custom output path")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--list", action="store_true", help="Listar temas disponibles")
    args = p.parse_args()

    if args.list:
        print("Temas sleep disponibles:")
        for k, v in SLEEP_TEMAS.items():
            print(f"  {k:12} → {v['titulo']} (mood: {v['mood']})")
        return

    if not args.tema and not args.titulo:
        p.error("Requiere --tema o --titulo")

    preset = SLEEP_TEMAS.get(args.tema, {})
    titulo = args.titulo or preset.get("titulo", args.tema or "Versículos Para Dormir")
    mood   = args.mood or preset.get("mood", "Reposo")

    if args.bg:
        single = FONDOS_DIR / args.bg
        if not single.exists():
            raise FileNotFoundError(f"Fondo no existe: {single}")
        bg_images = [single] * N_IMAGES  # tile single image across all slots
    else:
        bg_images = _find_bg_multi(preset.get("bg_candidates", []), n=N_IMAGES)

    out_name = f"sleep_{args.tema or 'custom'}_{args.duration}min.mp4"
    out_path = Path(args.output) if args.output else (OUT_BASE / out_name)

    cfg = SleepConfig(
        tema=args.tema or "custom",
        titulo=titulo,
        mood=mood,
        duration_min=args.duration,
        bg_images=bg_images,
        out_path=out_path,
        dry_run=args.dry_run,
    )

    print(f"\n{'='*60}")
    print(f"  SLEEP RENDER v2 · {cfg.tema} · {cfg.duration_min}min")
    print(f"  Titulo:  {cfg.titulo}")
    print(f"  Mood:    {cfg.mood}")
    print(f"  Images:  {len(cfg.bg_images)} × {cfg.duration_min // len(cfg.bg_images)}min each")
    for i, p in enumerate(cfg.bg_images):
        print(f"    [{i}] {p.name}  ({KB_PATTERNS[i % len(KB_PATTERNS)]})")
    print(f"  Model:   {MUSICGEN_MODEL}")
    print(f"  Output:  {cfg.out_path}")
    print(f"{'='*60}\n")

    render(cfg)


if __name__ == "__main__":
    main()
