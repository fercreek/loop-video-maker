"""
render_story.py — Pipeline completo para videos largos de historias bíblicas.

Flujo:
  1. Genera/carga script de historia (Claude API → data/stories/{id}.json)
  2. Genera/carga imagen por escena (Gemini Imagen 4.0 → output/stories/{id}/images/)
  3. Genera/carga narración por escena (Edge TTS jorge/dalia → audio/narrations/)
  4. Ensambla cada escena: imagen + narración + música fondo
  5. Concatena todas las escenas → video final

Uso:
    .venv/bin/python3 render_story.py --story david-goliat
    .venv/bin/python3 render_story.py --story david-goliat --force-script
    .venv/bin/python3 render_story.py --story david-goliat --force-images
    .venv/bin/python3 render_story.py --story david-goliat --dry-run
    .venv/bin/python3 render_story.py --list

Historias disponibles: david-goliat, jonas, exodo, jose
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
import os
import random
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
for pyver in ["python3.13", "python3.12", "python3.11"]:
    site = Path(__file__).parent / ".venv" / "lib" / pyver / "site-packages"
    if site.exists():
        sys.path.insert(0, str(site))
        break

from core.story_gen import generate_story, STORIES
from core.narration_gen import generate_narration, get_audio_duration, get_word_boundaries, EDGE_VOICES
from core.subtitle_burn import generate_subtitle_sequence, write_concat_file

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent
CONFIG_PATH = PROJECT_DIR / "config.json"
STORIES_OUT = PROJECT_DIR / "output" / "stories"
MUSIC_POOL  = PROJECT_DIR / "audio" / "cache"
FONDOS_POOL = PROJECT_DIR / "output" / "fondos"

# ─── Video config ─────────────────────────────────────────────────────────────
FPS            = 12
RESOLUTION     = "1920x1080"
VIDEO_BITRATE  = "3500k"
CODEC_ARGS     = ["-c:v", "libx264", "-preset", "ultrafast"]
AUDIO_ARGS     = ["-c:a", "aac", "-b:a", "192k"]
MUSIC_VOL      = 0.07   # fallback si mood no está en dict
NARR_VOL       = 1.0
CROSSFADE_SEC  = 2.0    # fade out duración — más suave entre escenas

# Dinámica musical por mood — narración al frente en tensión, música sube en gloria
MOOD_MUSIC_VOL: dict[str, float] = {
    "Solemnidad":    0.04,   # tensión máxima — casi silencio
    "Adoración":     0.07,   # devocional — default
    "Contemplación": 0.06,   # serena y reflexiva
    "Intercesión":   0.05,   # oración intensa
    "Restauración":  0.08,   # esperanza creciente
    "Liberación":    0.03,   # clímax — narración domina completamente
    "Gloria":        0.13,   # resolución y celebración — música sube
    "Alabanza":      0.11,   # júbilo
    "Paz profunda":  0.07,
    "Reposo":        0.07,
    "Madrugada":     0.06,   # íntimo, despertar — música suave
    "Devoción":      0.06,   # reverente, cercano
}
WATERMARK      = "@VersiculoDeDios"
FONT_PATH      = str(PROJECT_DIR / "assets" / "fonts" / "CormorantGaramond-Regular.ttf")
TITLE_FONT_SZ  = 52
WATERMARK_SZ   = 28
CANVAS_W, CANVAS_H = 1920, 1080

# Gemini Imagen
IMAGEN_MODEL = "imagen-4.0-generate-001"
IMAGEN_BASE  = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGEN_MODEL}:predict"


# ─── Config helpers ───────────────────────────────────────────────────────────
def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def _ffmpeg_filters() -> str:
    r = subprocess.run(["ffmpeg", "-filters"], capture_output=True, text=True)
    return r.stdout + r.stderr


def _check_drawtext() -> bool:
    """Return True if ffmpeg was compiled with libfreetype (drawtext support)."""
    return "drawtext" in _ffmpeg_filters()


def _check_subtitles() -> bool:
    """Return True if ffmpeg was compiled with libass (subtitles/SRT injection support)."""
    return "subtitles" in _ffmpeg_filters()


# NOTE (2026-05-08): ffmpeg -filters | grep subtitles|drawtext|libass → no output on this machine.
# Both filters absent. Shorts pipeline falls back to PIL burn-in (Option A).
# When libass is available, SUBTITLES_FILTER_AVAILABLE=True enables SRT injection (Option B).
_filters_cache = _ffmpeg_filters()
DRAWTEXT_AVAILABLE = "drawtext" in _filters_cache
SUBTITLES_FILTER_AVAILABLE = "subtitles" in _filters_cache


def font_arg() -> str:
    """Return font path if drawtext available and font exists, else empty string."""
    if not DRAWTEXT_AVAILABLE:
        return ""
    if os.path.exists(FONT_PATH):
        return FONT_PATH
    for p in ["/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return p
    return ""


# ─── Gemini Imagen ────────────────────────────────────────────────────────────
def generate_scene_image(prompt: str, out_path: Path, api_key: str) -> bool:
    """Genera imagen 1920×1080 para una escena. Retorna True si OK."""
    url = f"{IMAGEN_BASE}?key={api_key}"
    payload = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9",
            "safetyFilterLevel": "BLOCK_ONLY_HIGH",
        },
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    MAX_RETRIES = 4
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                resp = json.loads(r.read())
            b64 = resp["predictions"][0].get("bytesBase64Encoded", "")
            if not b64:
                return False
            png_bytes = base64.b64decode(b64)
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
            img = img.resize((1920, 1080), Image.LANCZOS)
            img.save(str(out_path), "JPEG", quality=92)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 2)   # 4s, 8s, 16s
                print(f"    [img] 429 rate limit — reintentando en {wait}s (intento {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                body = e.read().decode()[:300]
                print(f"    [img] HTTP {e.code}: {body}")
                return False
        except Exception as ex:
            print(f"    [img] Error: {ex}")
            return False
    return False


def get_or_generate_image(
    scene: dict, story_id: str, images_dir: Path,
    api_key: str, force: bool = False,
) -> Path:
    """Genera o carga desde caché la imagen de una escena."""
    img_path = images_dir / f"scene_{scene['id']:02d}.jpg"

    if img_path.exists() and not force:
        print(f"  [img] Caché: {img_path.name}")
        return img_path

    print(f"  [img] Generando escena {scene['id']}: {scene['title'][:40]}...")
    ok = generate_scene_image(scene["image_prompt"], img_path, api_key)

    if not ok:
        # Fallback: reutilizar fondo del pool general
        pool = sorted(glob.glob(str(FONDOS_POOL / "*.jpg")))
        if pool:
            fallback = random.choice(pool)
            subprocess.run(
                ["ffmpeg", "-y", "-i", fallback,
                 "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
                 str(img_path)],
                capture_output=True,
            )
            print(f"  [img] Fallback pool: {Path(fallback).name}")
        else:
            raise RuntimeError(f"No se pudo generar imagen para escena {scene['id']} y pool vacío")

    return img_path


# ─── Background music ─────────────────────────────────────────────────────────
def get_bg_music(mood: str) -> Path | None:
    """
    Busca track de música de fondo en audio/cache/.
    Intenta encontrar uno que coincida con el mood; si no, cualquiera.
    """
    mood_lower = mood.lower().replace(" ", "_")
    # Busca por nombre de mood en cache
    patterns = [
        str(MUSIC_POOL / f"*{mood_lower}*_norm.aac"),
        str(MUSIC_POOL / f"*{mood_lower}*.wav"),
        str(MUSIC_POOL / "*paz*_norm.aac"),
        str(MUSIC_POOL / "*adoracion*_norm.aac"),
        str(MUSIC_POOL / "*_norm.aac"),
        str(MUSIC_POOL / "*.wav"),
    ]
    for pattern in patterns:
        files = sorted(glob.glob(pattern))
        if files:
            chosen = files[0]
            print(f"  [music] {Path(chosen).name} (mood: {mood})")
            return Path(chosen)
    print(f"  [music] Sin track para mood '{mood}' — se omite música de fondo")
    return None


# ─── FFmpeg scene assembly ────────────────────────────────────────────────────
def render_scene_clip(
    scene: dict,
    img_path: Path,
    narr_path: Path,
    music_path: Path | None,
    out_path: Path,
    scene_idx: int,
    total_scenes: int,
) -> None:
    """Renderiza clip MP4. Ken Burns vía scale+crop (10-20x más rápido que zoompan)."""
    duration = get_audio_duration(narr_path)
    duration += 0.8  # buffer al final

    font = font_arg()
    safe_title = scene["title"].replace("'", "\\'").replace(":", "\\:").replace(",", "\\,")
    watermark_text = WATERMARK.replace("@", "\\@")

    # ── Ken Burns: scale 110% + pan LINEAL — 4 direcciones rotativas por escena ──
    # Pan lineal puro (sin min() que desacelera y lo hace ver estático)
    dur = f"{duration:.2f}"
    pan_patterns = [
        f"x='(iw-ow)*t/{dur}':y='(ih-oh)/2'",            # L → R lineal
        f"x='(iw-ow)*(1-t/{dur})':y='(ih-oh)/2'",        # R → L lineal
        f"x='(iw-ow)/2':y='(ih-oh)*t/{dur}'",             # top → bottom lineal
        f"x='(iw-ow)/2':y='(ih-oh)*(1-t/{dur})'",         # bottom → top lineal
    ]
    pan = pan_patterns[scene_idx % len(pan_patterns)]

    fade_out_v = max(0, duration - CROSSFADE_SEC)
    vf = (
        f"scale=2112:1188:force_original_aspect_ratio=increase,"
        f"crop=1920:1080:{pan},"
        f"fade=t=in:st=0:d=1.0,"
        f"fade=t=out:st={fade_out_v:.2f}:d={CROSSFADE_SEC:.2f}"
    )

    # Drawtext: título primeros 4s + watermark permanente
    drawtext_filters = []
    if font:
        drawtext_filters.append(
            f"drawtext=fontfile='{font}'"
            f":text='{watermark_text}'"
            f":fontsize={WATERMARK_SZ}"
            f":fontcolor=white@0.6"
            f":x=w-text_w-30:y=h-text_h-20"
        )
        if scene["title"]:
            drawtext_filters.append(
                f"drawtext=fontfile='{font}'"
                f":text='{safe_title}'"
                f":fontsize={TITLE_FONT_SZ}"
                f":fontcolor=white@0.9"
                f":x=(w-text_w)/2:y=h/2-text_h/2"
                f":box=1:boxcolor=black@0.45:boxborderw=20"
                f":enable='between(t,0,4)'"
            )

    if drawtext_filters:
        vf += "," + ",".join(drawtext_filters)

    # ── Subtítulos karaoke (si hay word boundaries del Edge TTS) ──────────────
    boundaries = get_word_boundaries(narr_path)
    sub_concat_path: Path | None = None

    if boundaries:
        sub_dir = out_path.parent / f"subs_{out_path.stem}"
        sub_frames = generate_subtitle_sequence(boundaries, sub_dir, duration)
        sub_concat_path = sub_dir / "concat.txt"
        write_concat_file(sub_frames, sub_concat_path)

    # ── Audio filter graph ────────────────────────────────────────────────────
    mood_vol = MOOD_MUSIC_VOL.get(scene.get("mood", ""), MUSIC_VOL)
    narr_af = (
        f"[1:a]volume={NARR_VOL},"
        f"afade=t=in:ss=0:d=0.5,"
        f"afade=t=out:st={fade_out_v:.2f}:d={CROSSFADE_SEC}[narr]"
    )

    if sub_concat_path and music_path:
        # inputs: [0]=bg_img [1]=narr [2]=sub_concat [3]=music
        music_idx = 3
        sub_idx   = 2
        music_input = ["-stream_loop", "-1", "-i", str(music_path)]
        af = (
            f"{narr_af};"
            f"[{music_idx}:a]volume={mood_vol},atrim=0:{duration:.2f}[bgm];"
            f"[narr][bgm]amix=inputs=2:duration=first:normalize=0[a]"
        )
        fc = (
            f"[0:v]{vf}[bg];"
            f"[{sub_idx}:v]fps={FPS},scale={CANVAS_W}:{CANVAS_H}[sub];"
            f"[bg][sub]overlay=0:0:shortest=1[v];"
            f"{af}"
        )
        cmd = (
            ["ffmpeg", "-y"]
            + ["-loop", "1", "-t", f"{duration:.2f}", "-i", str(img_path)]
            + ["-i", str(narr_path)]
            + ["-f", "concat", "-safe", "0", "-i", str(sub_concat_path)]
            + music_input
            + ["-filter_complex", fc]
            + ["-map", "[v]", "-map", "[a]"]
            + ["-t", f"{duration:.2f}", "-r", str(FPS)]
            + CODEC_ARGS + AUDIO_ARGS + ["-b:v", VIDEO_BITRATE, str(out_path)]
        )
    elif sub_concat_path:
        # sin música
        af = narr_af.replace("[narr]", "[a]")
        fc = (
            f"[0:v]{vf}[bg];"
            f"[2:v]fps={FPS},scale={CANVAS_W}:{CANVAS_H}[sub];"
            f"[bg][sub]overlay=0:0:shortest=1[v];"
            f"{af}"
        )
        cmd = (
            ["ffmpeg", "-y"]
            + ["-loop", "1", "-t", f"{duration:.2f}", "-i", str(img_path)]
            + ["-i", str(narr_path)]
            + ["-f", "concat", "-safe", "0", "-i", str(sub_concat_path)]
            + ["-filter_complex", fc]
            + ["-map", "[v]", "-map", "[a]"]
            + ["-t", f"{duration:.2f}", "-r", str(FPS)]
            + CODEC_ARGS + AUDIO_ARGS + ["-b:v", VIDEO_BITRATE, str(out_path)]
        )
    elif music_path:
        # sin subtítulos, con música (fallback)
        music_input = ["-stream_loop", "-1", "-i", str(music_path)]
        af = (
            f"{narr_af};"
            f"[2:a]volume={mood_vol},atrim=0:{duration:.2f}[bgm];"
            f"[narr][bgm]amix=inputs=2:duration=first:normalize=0[a]"
        )
        fc = f"[0:v]{vf}[v];{af}"
        cmd = (
            ["ffmpeg", "-y"]
            + ["-loop", "1", "-t", f"{duration:.2f}", "-i", str(img_path)]
            + ["-i", str(narr_path)]
            + music_input
            + ["-filter_complex", fc]
            + ["-map", "[v]", "-map", "[a]"]
            + ["-t", f"{duration:.2f}", "-r", str(FPS)]
            + CODEC_ARGS + AUDIO_ARGS + ["-b:v", VIDEO_BITRATE, str(out_path)]
        )
    else:
        # sin subtítulos, sin música
        af = narr_af.replace("[narr]", "[a]")
        fc = f"[0:v]{vf}[v];{af}"
        cmd = (
            ["ffmpeg", "-y"]
            + ["-loop", "1", "-t", f"{duration:.2f}", "-i", str(img_path)]
            + ["-i", str(narr_path)]
            + ["-filter_complex", fc]
            + ["-map", "[v]", "-map", "[a]"]
            + ["-t", f"{duration:.2f}", "-r", str(FPS)]
            + CODEC_ARGS + AUDIO_ARGS + ["-b:v", VIDEO_BITRATE, str(out_path)]
        )

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    [ffmpeg] STDERR: {result.stderr[-600:]}")
        raise RuntimeError(f"ffmpeg falló en escena {scene['id']}")

    # Cleanup subtitle PNGs — no se necesitan post-render (~57GB en 100 historias)
    if sub_concat_path and sub_concat_path.parent.exists():
        import shutil
        shutil.rmtree(sub_concat_path.parent, ignore_errors=True)


def concat_scenes(scene_clips: list[Path], out_path: Path) -> None:
    """
    Concatena clips + normaliza audio a -14 LUFS (target YouTube).

    Stream copy NO normaliza audio. Re-encode con loudnorm sí — pero es lento.
    Estrategia: stream copy a temporal → loudnorm pass único → output final.
    """
    concat_list = out_path.parent / "concat_list.txt"
    tmp_concat  = out_path.parent / f"_tmp_{out_path.stem}.mp4"
    with open(concat_list, "w") as f:
        for clip in scene_clips:
            f.write(f"file '{clip.absolute()}'\n")

    # 1. Stream copy → tmp (rápido)
    print(f"\n[concat] Uniendo {len(scene_clips)} clips (stream copy) → tmp...")
    cmd_copy = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy",
        str(tmp_concat),
    ]
    result = subprocess.run(cmd_copy, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[concat] STDERR: {result.stderr[-600:]}")
        raise RuntimeError("Stream copy falló")

    # 2. Loudnorm a -14 LUFS (estándar YouTube) — re-encode solo audio, copy video
    print(f"[concat] Normalizando audio a -14 LUFS (target YouTube)...")
    cmd_loud = [
        "ffmpeg", "-y", "-i", str(tmp_concat),
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "copy",                # video sin re-encode
        "-c:a", "aac", "-b:a", "192k", # audio re-encode con loudnorm
        str(out_path),
    ]
    result2 = subprocess.run(cmd_loud, capture_output=True, text=True)
    if result2.returncode != 0:
        print(f"[concat] Loudnorm falló — usando tmp sin normalize: {result2.stderr[-300:]}")
        # Fallback: usar tmp directo si loudnorm rompe
        import shutil as _sh
        _sh.move(str(tmp_concat), str(out_path))
    else:
        tmp_concat.unlink(missing_ok=True)

    concat_list.unlink(missing_ok=True)


# ─── Main pipeline ────────────────────────────────────────────────────────────
def render_story(
    story_id: str,
    force_script: bool = False,
    force_images: bool = False,
    force_narr:   bool = False,
    voice: str = "jorge",
    dry_run: bool = False,
) -> Path:
    print(f"\n{'='*65}")
    print(f"  HISTORIA BÍBLICA: {STORIES[story_id]['title']}")
    print(f"{'='*65}")

    # 1. Story script
    print("\n[1/5] Generando/cargando script...")
    cache_path = PROJECT_DIR / "data" / "stories" / f"{story_id}.json"
    if dry_run and not cache_path.exists():
        # Muestra metadatos sin llamar a Claude
        meta = STORIES[story_id]
        print(f"\n[DRY RUN] Sin caché aún — metadatos del plan:")
        print(f"  Historia: {meta['title']} ({meta['bible_ref']})")
        print(f"  Escenas objetivo: {meta['target_scenes']}")
        print(f"  Palabras objetivo: ~{meta['target_words']}")
        print(f"  Moods musicales: {meta['moods']}")
        print(f"\n  Próximo paso: agregar claude_api_key a config.json")
        print(f"  Luego: .venv/bin/python3 render_story.py --story {story_id}")
        return PROJECT_DIR / "output" / "stories" / story_id / f"{story_id}.mp4"

    script = generate_story(story_id, force=force_script)
    scenes = script["scenes"]
    print(f"  {len(scenes)} escenas · {sum(len(s['text'].split()) for s in scenes)} palabras")

    if dry_run:
        print("\n[DRY RUN] Escenas:")
        for s in scenes:
            print(f"  {s['id']:2d}. {s['title']}")
            print(f"      {len(s['text'].split())} palabras · mood: {s['mood']}")
        return PROJECT_DIR / "output" / "stories" / story_id / f"{story_id}.mp4"

    cfg = load_config()
    gemini_key = cfg.get("gemini_api_key", "")

    # Dirs de salida
    story_out = STORIES_OUT / story_id
    images_dir = story_out / "images"
    clips_dir  = story_out / "clips"
    for d in [story_out, images_dir, clips_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 2. Imágenes por escena
    print(f"\n[2/5] Generando imágenes ({len(scenes)} escenas)...")
    images: list[Path] = []
    for scene in scenes:
        img = get_or_generate_image(
            scene, story_id, images_dir, gemini_key, force=force_images
        )
        images.append(img)
        time.sleep(0.3)  # rate limit Gemini

    # 3. Narración por escena — paralelo
    print(f"\n[3/5] Generando narraciones ({len(scenes)} escenas) [paralelo]...")
    def _gen_narr(scene: dict) -> tuple[int, Path]:
        scene_id_str = f"{story_id}_s{scene['id']:02d}"
        path = generate_narration(
            scene["text"], scene_id_str,
            voice=voice, force=force_narr, story_id=story_id,
        )
        return scene["id"], path

    narr_dict: dict[int, Path] = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for sid, path in ex.map(_gen_narr, scenes):
            narr_dict[sid] = path
    narrations = [narr_dict[s["id"]] for s in scenes]

    # 4. Render por escena — paralelo
    CLIP_WORKERS = 4
    print(f"\n[4/5] Renderizando {len(scenes)} clips [paralelo {CLIP_WORKERS}x]...")

    # Pre-buscar música fuera del threadpool (no thread-safe print)
    music_tracks = [get_bg_music(s.get("mood", "paz")) for s in scenes]

    def _render_one(args: tuple) -> tuple[int, Path]:
        i, scene = args
        clip_path = clips_dir / f"scene_{scene['id']:02d}.mp4"
        if clip_path.exists() and not force_images and not force_narr:
            print(f"  [clip] Caché: {clip_path.name}")
            return i, clip_path
        t0 = time.time()
        render_scene_clip(
            scene=scene,
            img_path=images[i],
            narr_path=narrations[i],
            music_path=music_tracks[i],
            out_path=clip_path,
            scene_idx=i,
            total_scenes=len(scenes),
        )
        elapsed = time.time() - t0
        dur = get_audio_duration(narrations[i])
        print(f"  [{scene['id']:02d}] OK {elapsed:.1f}s render → {dur:.1f}s video")
        return i, clip_path

    with ThreadPoolExecutor(max_workers=CLIP_WORKERS) as ex:
        results = list(ex.map(_render_one, enumerate(scenes)))
    scene_clips = [path for _, path in sorted(results)]

    # 4b. Cold open — clip prepuesto antes de escena 1
    cold_open_data = script.get("cold_open")
    if cold_open_data:
        co_text  = cold_open_data["text"]
        co_img_i = cold_open_data.get("image_scene", 1) - 1   # 0-indexed
        co_img_i = max(0, min(co_img_i, len(images) - 1))
        co_narr  = generate_narration(co_text, f"{story_id}_cold_open", voice=voice, force=force_narr, story_id=story_id)
        co_clip  = clips_dir / "cold_open.mp4"
        if not co_clip.exists() or force_narr:
            print(f"\n[cold_open] Renderizando ({len(co_text.split())} palabras)...")
            co_scene = {"id": 0, "title": "", "mood": "Solemnidad"}
            render_scene_clip(
                scene=co_scene, img_path=images[co_img_i], narr_path=co_narr,
                music_path=music_tracks[co_img_i], out_path=co_clip,
                scene_idx=0, total_scenes=len(scenes),
            )
            print(f"  [cold_open] OK → {get_audio_duration(co_narr):.1f}s")
        else:
            print(f"\n[cold_open] Caché: {co_clip.name}")
        scene_clips = [co_clip] + scene_clips

    # 4c. End screen — clip añadido después de escena 14
    end_screen_data = script.get("end_screen")
    if end_screen_data:
        es_text  = end_screen_data["text"]
        es_img_i = end_screen_data.get("image_scene", len(scenes)) - 1
        es_img_i = max(0, min(es_img_i, len(images) - 1))
        es_narr  = generate_narration(es_text, f"{story_id}_end_screen", voice=voice, force=force_narr, story_id=story_id)
        es_clip  = clips_dir / "end_screen.mp4"
        if not es_clip.exists() or force_narr:
            print(f"\n[end_screen] Renderizando ({len(es_text.split())} palabras)...")
            es_scene = {"id": 99, "title": "", "mood": "Gloria"}
            render_scene_clip(
                scene=es_scene, img_path=images[es_img_i], narr_path=es_narr,
                music_path=music_tracks[es_img_i], out_path=es_clip,
                scene_idx=3, total_scenes=len(scenes),
            )
            print(f"  [end_screen] OK → {get_audio_duration(es_narr):.1f}s")
        else:
            print(f"\n[end_screen] Caché: {es_clip.name}")
        scene_clips = scene_clips + [es_clip]

    # 5. Concat final
    print(f"\n[5/5] Concatenando video final ({len(scene_clips)} clips)...")
    final_out = story_out / f"{story_id}.mp4"
    concat_scenes(scene_clips, final_out)

    # Cleanup clips dir — ~427MB/historia, 42GB en 100 historias si no se borra
    import shutil
    final_size = final_out.stat().st_size
    if final_size > 100 * 1024 * 1024:
        clips_mb = (
            sum(f.stat().st_size for f in clips_dir.rglob("*") if f.is_file())
            / 1024 / 1024
        ) if clips_dir.exists() else 0
        shutil.rmtree(clips_dir, ignore_errors=True)
        print(f"  [cleanup] clips/ eliminado — {clips_mb:.0f} MB liberados")
    else:
        print(f"  [cleanup] SKIP — video final {final_size/1024/1024:.1f} MB < 100 MB (sanity check)")

    # ── Thumbnail auto — usa imagen más dramática (escena configurable o ~75%) ──
    try:
        from core.story_thumbnail import generate_story_thumbnail
        # 1. Escena dramática: campo `thumbnail_scene` en JSON, fallback 75%
        dramatic_idx = script.get("thumbnail_scene")
        if dramatic_idx is not None:
            dramatic_idx = max(0, min(int(dramatic_idx) - 1, len(scenes) - 1))
        else:
            dramatic_idx = min(int(len(scenes) * 0.75), len(scenes) - 1)

        # 2. Título thumbnail: campo `thumbnail_title` en JSON, fallback skipping stopwords
        STOPWORDS = {"y", "de", "el", "la", "los", "las", "del", "al", "en", "a"}
        title_text = script.get("thumbnail_title")
        if not title_text:
            story_title = script.get("title", story_id)
            words = [w for w in story_title.split() if w.lower() not in STOPWORDS]
            title_text = " ".join(words[:2]).upper() if words else story_title.upper()
        else:
            title_text = title_text.upper()
        thumb_out = story_out / "thumbnail.jpg"
        generate_story_thumbnail(
            bg_image=images[dramatic_idx],
            title_text=title_text,
            subtitle_text="Historia Bíblica",
            out_path=thumb_out,
        )
        print(f"  [thumbnail] OK → {thumb_out.name} (escena {dramatic_idx+1})")
    except Exception as e:
        print(f"  [thumbnail] WARN: {e}")

    # ── YouTube metadata auto (chapters reales del MP4) ──────────────────────
    try:
        sys.path.insert(0, str(PROJECT_DIR / "scripts"))
        from generate_yt_metadata import generate as gen_yt_metadata
        meta = gen_yt_metadata(story_id)
        print(f"  [yt_meta] OK → {len(meta['chapters'])} chapters, {len(meta['tags'])} tags")
    except Exception as e:
        print(f"  [yt_meta] WARN: {e}")

    # Stats
    all_narrations = narrations[:]
    if cold_open_data: all_narrations.insert(0, co_narr)
    if end_screen_data: all_narrations.append(es_narr)
    total_duration = sum(get_audio_duration(n) for n in all_narrations)
    size_mb = final_out.stat().st_size / 1024 / 1024

    # ── Quality gate — verifica integridad antes de declarar LISTO ────────────
    qg_issues: list[str] = []
    try:
        # 1. ffprobe parses MP4
        actual_dur = get_audio_duration(final_out)
        # 2. Duration delta (tolera 5%)
        expected_dur = total_duration + (len(all_narrations) * 0.8)  # buffers
        delta_pct = abs(actual_dur - expected_dur) / expected_dur if expected_dur else 0
        if delta_pct > 0.10:
            qg_issues.append(f"duración delta {delta_pct*100:.1f}% > 10%")
        # 3. Thumbnail existe
        thumb_path = story_out / "thumbnail.jpg"
        if not thumb_path.exists() or thumb_path.stat().st_size < 1000:
            qg_issues.append("thumbnail.jpg ausente o corrupto")
        # 4. yt_metadata.json válido
        meta_path = story_out / "yt_metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            if not meta.get("chapters"):
                qg_issues.append("yt_metadata.json sin chapters")
            if not meta.get("description"):
                qg_issues.append("yt_metadata.json sin description")
        else:
            qg_issues.append("yt_metadata.json no generado")
    except Exception as e:
        qg_issues.append(f"quality gate exception: {e}")

    if qg_issues:
        print(f"\n  ⚠ QUALITY GATE — {len(qg_issues)} issue(s):")
        for q in qg_issues:
            print(f"    - {q}")
    else:
        print(f"\n  ✓ Quality gate OK (duración + thumbnail + metadata)")

    print(f"\n{'='*65}")
    print(f"  LISTO: {final_out}")
    print(f"  Duración: {total_duration/60:.1f} min · Tamaño: {size_mb:.1f} MB")
    print(f"{'='*65}")

    return final_out


# ─── CLI ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render video largo de historia bíblica narrada"
    )
    parser.add_argument(
        "--story", default="david-goliat",
        choices=list(STORIES),
        help="Historia a renderizar",
    )
    parser.add_argument(
        "--voice", default="jorge",
        choices=list(EDGE_VOICES),
        help="Voz macOS ES-MX para narración",
    )
    parser.add_argument("--force-script",  action="store_true", help="Re-generar script aunque exista caché")
    parser.add_argument("--force-images",  action="store_true", help="Re-generar imágenes aunque existan")
    parser.add_argument("--force-narr",    action="store_true", help="Re-generar narraciones")
    parser.add_argument("--dry-run",       action="store_true", help="Mostrar plan sin ejecutar")
    parser.add_argument("--list",          action="store_true", help="Listar historias disponibles")

    args = parser.parse_args()

    if args.list:
        print("Historias disponibles:")
        for sid, meta in STORIES.items():
            print(f"  {sid:<20s} — {meta['title']} ({meta['bible_ref']})")
            print(f"  {'':20s}   {meta['target_scenes']} escenas · ~{meta['target_words']} palabras")
        return

    render_story(
        story_id=args.story,
        force_script=args.force_script,
        force_images=args.force_images,
        force_narr=args.force_narr,
        voice=args.voice,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
