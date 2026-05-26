"""
render_sleep.py — Pipeline para sleeping content cristiano 60-120 min.

Stack:
  - Audio: MusicGen local (core/music_gen.py) — moods "Reposo", "Madrugada", "Paz profunda"
  - Visual: 1-2 imágenes pool con Ken-Burns ULTRA-lento (5% zoom en duración total)
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
    bg_image: Path
    out_path: Path
    dry_run: bool = False


def _find_bg(candidates: list[str]) -> Path:
    """Devuelve el primer fondo del pool que existe."""
    for c in candidates:
        p = FONDOS_DIR / c
        if p.exists():
            return p
    # Fallback — cualquier fondo_ai_*.jpg disponible
    available = sorted(FONDOS_DIR.glob("fondo_ai_*.jpg"))
    if not available:
        raise FileNotFoundError(f"Sin fondos en {FONDOS_DIR}")
    return available[0]


def generate_audio(mood: str, duration_min: int, out_dir: Path, dry_run: bool = False) -> Path:
    """Genera audio ambient usando core/music_gen.py existente."""
    from core.music_gen import generate_playlist
    out_path = out_dir / f"sleep_audio_{mood.replace(' ', '_')}_{duration_min}min.wav"
    if out_path.exists():
        print(f"  [audio] Cache hit: {out_path.name}")
        return out_path
    if dry_run:
        print(f"  [audio DRY] generaría {duration_min}min de {mood}")
        return out_path
    total_sec = duration_min * 60
    print(f"  [audio] Generando {duration_min}min mood={mood} ({total_sec}s)...")
    audio_path = generate_playlist(
        moods=[mood],
        total_seconds=total_sec,
        output_dir=str(out_dir),
        crossfade_seconds=4.0,
    )
    return Path(audio_path)


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


def build_video_filter(duration_sec: float, bg_path: Path, title_png: Path, wm_png: Path) -> str:
    """
    Filter complex (NO drawtext — usa overlay PNG Pillow):
      [0:v] background zoompan ultra-lento
      [1:v] watermark PNG (always visible)
      [2:v] title PNG (visible 0-INTRO_DUR con fade)
    """
    frames = int(duration_sec * FPS)
    fade_out_start = duration_sec - 2.0
    intro_end = INTRO_DUR
    intro_fade = INTRO_FADE

    filter_str = (
        # 1. BG zoompan ultra-lento + fade in/out
        f"[0:v]scale={int(RES_W * 1.06)}:-1:flags=lanczos,"
        f"crop={RES_W}:{RES_H},"
        f"zoompan=z='1.00+0.05*on/{frames}':d={frames}:s={RES_W}x{RES_H}:fps={FPS}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',"
        f"setsar=1,"
        f"fade=t=in:st=0:d=1.5,"
        f"fade=t=out:st={fade_out_start:.2f}:d=2.0[vbase];"
        # 2. Watermark always on
        f"[vbase][1:v]overlay=0:0[vwm];"
        # 3. Title PNG: fade in/out alpha on PNG stream, then overlay with enable window
        f"[2:v]format=rgba,"
        f"fade=t=in:st=0:d={intro_fade:.2f}:alpha=1,"
        f"fade=t=out:st={intro_end - intro_fade:.2f}:d={intro_fade:.2f}:alpha=1[title];"
        f"[vwm][title]overlay=0:0:enable='between(t,0,{intro_end:.2f})'[vout]"
    )
    return filter_str


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

    # Audio
    audio_path = generate_audio(cfg.mood, cfg.duration_min, out_dir, dry_run=cfg.dry_run)

    if cfg.dry_run:
        print(f"  [render DRY] {cfg.duration_min}min · bg={cfg.bg_image.name} · mood={cfg.mood}")
        print(f"  Output: {cfg.out_path}")
        return cfg.out_path

    duration_sec = cfg.duration_min * 60

    # Generate overlay PNGs (title + watermark)
    title_png, wm_png = build_overlay_pngs(cfg.titulo, out_dir)

    vf = build_video_filter(duration_sec, cfg.bg_image, title_png, wm_png)
    af = build_audio_filter(duration_sec)
    full_filter = f"{vf};{af}"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", f"{duration_sec + 0.5:.1f}", "-i", str(cfg.bg_image),
        "-loop", "1", "-t", f"{duration_sec + 0.5:.1f}", "-i", str(wm_png),
        "-loop", "1", "-t", f"{duration_sec + 0.5:.1f}", "-i", str(title_png),
        "-i", str(audio_path),
        "-filter_complex", full_filter.replace("[1:a]", "[3:a]"),
        "-map", "[vout]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-b:v", BITRATE,
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-t", f"{duration_sec:.1f}",
        str(cfg.out_path),
    ]

    print(f"  [render] Renderizando {cfg.duration_min}min → {cfg.out_path.name}...")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        # Save error log
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
        bg_image = FONDOS_DIR / args.bg
        if not bg_image.exists():
            raise FileNotFoundError(f"Fondo no existe: {bg_image}")
    else:
        bg_image = _find_bg(preset.get("bg_candidates", []))

    out_name = f"sleep_{args.tema or 'custom'}_{args.duration}min.mp4"
    out_path = Path(args.output) if args.output else (OUT_BASE / out_name)

    cfg = SleepConfig(
        tema=args.tema or "custom",
        titulo=titulo,
        mood=mood,
        duration_min=args.duration,
        bg_image=bg_image,
        out_path=out_path,
        dry_run=args.dry_run,
    )

    print(f"\n{'='*60}")
    print(f"  SLEEP RENDER · {cfg.tema} · {cfg.duration_min}min")
    print(f"  Titulo: {cfg.titulo}")
    print(f"  Mood:   {cfg.mood}")
    print(f"  BG:     {cfg.bg_image.name}")
    print(f"  Output: {cfg.out_path}")
    print(f"{'='*60}\n")

    render(cfg)


if __name__ == "__main__":
    main()
