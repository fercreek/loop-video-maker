"""
scripts/generate_mood_tracks.py — Genera tracks únicos con MusicGen y los guarda en audio/loops/.

Uso:
    python3 scripts/generate_mood_tracks.py --mood "Esperanza"
    python3 scripts/generate_mood_tracks.py --mood "Esperanza" "Sanación" "Salmos"
    python3 scripts/generate_mood_tracks.py --duplicates         # 8 moods problemáticos
    python3 scripts/generate_mood_tracks.py --all                # todos los moods
    python3 scripts/generate_mood_tracks.py --duration 600       # 10 min por track
    python3 scripts/generate_mood_tracks.py --model medium       # musicgen-stereo-medium
    python3 scripts/generate_mood_tracks.py --test               # 30s de prueba para escuchar
    python3 scripts/generate_mood_tracks.py --list               # ver estado de cada mood
"""
from __future__ import annotations

import sys
import os
import json
import argparse
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.music_gen import MUSICGEN_MOOD_PROMPTS, generar_musica_musicgen

LOOPS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio", "loops")
MANIFEST_PATH = os.path.join(LOOPS_DIR, "manifest.json")

# Moods problemáticos: duplicados o loops muy cortos
PRIORITY_MOODS = [
    "Esperanza",   # == devocion.mp3 (duplicado)
    "Sanación",    # == paz_profunda.mp3 (duplicado)
    "Salmos",      # == paz_profunda.mp3 (duplicado)
    "Quietud",     # 81s — loopea 14× en 20min
    "Meditación",  # 91s — loopea 13×
    "Gloria",      # 124s — loopea 9×
    "Silencio",    # 127s — loopea 9×
    "Júbilo",      # 150s — loopea 8×
]


def mood_to_filename(mood: str) -> str:
    import unicodedata
    s = "".join(
        c for c in unicodedata.normalize("NFD", mood)
        if unicodedata.category(c) != "Mn"
    ).lower()
    return s.replace(" ", "_") + "_musicgen.mp3"


def wav_to_mp3(wav_path: str, mp3_path: str, bitrate: str = "192k") -> str:
    cmd = ["ffmpeg", "-y", "-i", wav_path, "-b:a", bitrate, mp3_path]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()}")
    return mp3_path


def update_manifest(mood: str, filename: str, description: str) -> None:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["moods"][mood] = {"file": filename, "description": description}
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"  manifest.json actualizado: {mood!r} -> {filename}")


def generate_track(
    mood: str,
    duration_sec: int = 300,
    model_size: str = "small",
    test_mode: bool = False,
) -> str:
    model_id = f"facebook/musicgen-stereo-{model_size}"
    clip_duration = 30
    total_duration = 30 if test_mode else duration_sec

    print(f"\n[{mood}] Generando {total_duration}s con {model_id}...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        wav_path = generar_musica_musicgen(
            mood=mood,
            duracion_clip=clip_duration,
            duracion_total=total_duration,
            output_dir=tmp_dir,
            model_id=model_id,
        )

        if test_mode:
            out_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
            )
            os.makedirs(out_dir, exist_ok=True)
            import shutil
            out_path = os.path.join(out_dir, f"test_{mood.lower().replace(' ','_')}.wav")
            shutil.copy(wav_path, out_path)
            print(f"  Test WAV: {out_path}")
            print(f"  Escucha: open {out_path!r}")
            return out_path

        filename = mood_to_filename(mood)
        mp3_path = os.path.join(LOOPS_DIR, filename)
        wav_to_mp3(wav_path, mp3_path)

    description = (
        f"{mood} — MusicGen stereo-{model_size} | "
        f"{MUSICGEN_MOOD_PROMPTS.get(mood, '')[:60]}"
    )
    update_manifest(mood, filename, description)

    size_mb = os.path.getsize(mp3_path) / 1024 / 1024
    print(f"  Guardado: {mp3_path} ({size_mb:.1f} MB)")
    return mp3_path


def main():
    ap = argparse.ArgumentParser(
        description="Genera tracks MusicGen unicos para moods sin audio propio"
    )
    ap.add_argument("--mood", nargs="+", metavar="MOOD")
    ap.add_argument("--duplicates", action="store_true",
                    help="Los 8 moods problematicos")
    ap.add_argument("--all", action="store_true",
                    help="Todos los moods en MUSICGEN_MOOD_PROMPTS")
    ap.add_argument("--duration", type=int, default=300,
                    help="Duracion en segundos (default 300 = 5 min)")
    ap.add_argument("--model", choices=["small", "medium"], default="small",
                    help="Modelo: small (rapido) | medium (mejor calidad)")
    ap.add_argument("--test", action="store_true",
                    help="Genera 30s en output/ para escuchar, sin guardar en loops/")
    ap.add_argument("--list", action="store_true",
                    help="Lista moods y su estado")
    args = ap.parse_args()

    if args.list:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        existing = set(manifest.get("moods", {}).keys())
        print("\nMoods (MUSICGEN_MOOD_PROMPTS):")
        print(f"  {'Mood':<25} {'Estado'}")
        print("  " + "-" * 55)
        for mood in sorted(MUSICGEN_MOOD_PROMPTS.keys()):
            status = "ok (loop)" if mood in existing else "SIN TRACK -> MusicGen"
            flag = " [PRIORITARIO]" if mood in PRIORITY_MOODS else ""
            print(f"  {mood:<25} {status}{flag}")
        return

    if args.mood:
        moods = args.mood
    elif args.duplicates:
        moods = PRIORITY_MOODS
    elif args.all:
        moods = list(MUSICGEN_MOOD_PROMPTS.keys())
    else:
        print("Especifica --mood NOMBRE, --duplicates, --all, o --list")
        ap.print_help()
        sys.exit(1)

    invalid = [m for m in moods if m not in MUSICGEN_MOOD_PROMPTS]
    if invalid:
        print(f"Moods no reconocidos: {invalid}")
        sys.exit(1)

    print(f"\n{'─'*60}")
    print(f"Generando {len(moods)} track(s) | modelo: musicgen-stereo-{args.model}")
    print(f"Duracion: {args.duration}s | test={args.test}")
    print(f"{'─'*60}")

    errors = []
    for mood in moods:
        try:
            generate_track(
                mood=mood,
                duration_sec=args.duration,
                model_size=args.model,
                test_mode=args.test,
            )
        except Exception as e:
            print(f"ERROR en {mood!r}: {e}")
            import traceback
            traceback.print_exc()
            errors.append(mood)

    print(f"\nListo. {len(moods) - len(errors)}/{len(moods)} generado(s).")
    if errors:
        print(f"Fallidos: {errors}")
    if not args.test:
        print(f"Guardados en: {LOOPS_DIR}")


if __name__ == "__main__":
    main()
