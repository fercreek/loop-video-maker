"""
scripts/download_audio.py — Build 30-mood audio pool via ffmpeg pitch/tempo variants.

Strategy: 6 base tracks × ~3 variants each = 30 unique moods.
All variants generated locally via ffmpeg — zero downloads, zero API keys.

Pitch shift via asetrate (preserves duration at cost of slight quality).
Tempo correction via atempo (keeps original duration if desired).

Usage:
  .venv/bin/python3 scripts/download_audio.py

Idempotent — skips existing files, updates manifest.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOPS_DIR   = os.path.join(PROJECT_DIR, "audio", "loops")
MANIFEST    = os.path.join(LOOPS_DIR, "manifest.json")

sys.path.insert(0, PROJECT_DIR)

# ─── Variant catalog ─────────────────────────────────────────────────────────
# (output_stem, source_stem, semitones, tempo, mood_key, description)
# semitones: float — positive=higher/brighter, negative=lower/darker
# tempo: float — <1.0=slower, >1.0=faster  (1.0 = original speed)
# mood_key: Spanish name used in THEME_MOODS
#
# Source files:
#   paz_profunda.mp3  249s  (Meditation Impromptu 02 — Kevin MacLeod)
#   adoracion.mp3     190s  (Enchanted Valley)
#   meditacion.mp3     91s  (Peaceful Desolation)
#   devocion.mp3      520s  (Healing)
#   esperanza.mp3     520s  (Healing alt — same recording as devocion)
#   sanacion.mp3      249s  (= paz_profunda, same file different name)
#
# Existing (already generated, kept in manifest):
#   contemplacion   paz_profunda  -2.0  1.00  Contemplación
#   amanecer        adoracion     +1.0  1.05  Amanecer
#   solemnidad      devocion      -3.0  0.95  Solemnidad
#   reposo          meditacion     0.0  1.00  Reposo (4× loop)
#   paz_tarde       sanacion      -1.5  0.97  Paz tarde

NEW_VARIANTS = [
    # ── paz_profunda variants (deep, prayer, night, dawn) ──────────────────
    ("madrugada",     "paz_profunda", -4.0, 0.93, "Madrugada",
     "Madrugada — paz_profunda -4st 0.93x (vigilia nocturna)"),

    ("manantial",     "paz_profunda", +2.5, 1.04, "Manantial",
     "Manantial — paz_profunda +2.5st 1.04x (mañana fresca)"),

    ("gracia",        "paz_profunda", +1.0, 1.0,  "Gracia",
     "Gracia — paz_profunda +1st (tono más luminoso)"),

    # ── adoracion variants (praise, glory, bright) ────────────────────────
    ("gloria",        "adoracion",   +3.0, 1.08, "Gloria",
     "Gloria — adoracion +3st 1.08x (alabanza jubilosa)"),

    ("alabanza",      "adoracion",   -1.5, 1.0,  "Alabanza",
     "Alabanza — adoracion -1.5st (más solemne)"),

    ("jubilo",        "adoracion",   +1.5, 1.06, "Júbilo",
     "Jubilo — adoracion +1.5st 1.06x (celebración)"),

    # ── meditacion variants (quiet, silence, rest) ────────────────────────
    # reposo already exists (4× loop). Adding smaller loop + pitch variants.
    ("silencio",      "meditacion",  -2.0, 0.90, "Silencio",
     "Silencio — meditacion -2st 0.90x (quietud profunda)"),

    ("quietud",       "meditacion",  +1.0, 1.0,  "Quietud",
     "Quietud — meditacion +1st (serenidad leve)"),

    # ── devocion variants (reverence, offering, gravity) ─────────────────
    # solemnidad already exists (-3st 0.95x)
    ("reverencia",    "devocion",    -1.5, 0.92, "Reverencia",
     "Reverencia — devocion -1.5st 0.92x (gravedad reverente)"),

    ("ofrenda",       "devocion",    +1.0, 1.0,  "Ofrenda",
     "Ofrenda — devocion +1st (ofrenda cálida)"),

    ("intercesion",   "devocion",    -2.5, 0.97, "Intercesión",
     "Intercesion — devocion -2.5st 0.97x (intercesión profunda)"),

    # ── esperanza variants (hope, promise, longing) ───────────────────────
    ("promesa",       "esperanza",   +2.0, 1.05, "Promesa",
     "Promesa — esperanza +2st 1.05x (promesa brillante)"),

    ("anhelo",        "esperanza",   -2.0, 0.97, "Anhelo",
     "Anhelo — esperanza -2st 0.97x (anhelo tierno)"),

    ("fe_viva",       "esperanza",   +0.5, 1.02, "Fe viva",
     "Fe viva — esperanza +0.5st 1.02x (fe activa)"),

    # ── sanacion variants (healing, restoration, anointing) ──────────────
    # paz_tarde already exists (-1.5st 0.97x). contemplacion from paz_profunda.
    ("restauracion",  "sanacion",    +2.0, 1.03, "Restauración",
     "Restauracion — sanacion +2st 1.03x (restauración ascendente)"),

    ("ungimiento",    "sanacion",    -2.5, 0.95, "Ungimiento",
     "Ungimiento — sanacion -2.5st 0.95x (unción profunda)"),

    ("liberacion",    "sanacion",    +3.5, 1.07, "Liberación",
     "Liberacion — sanacion +3.5st 1.07x (liberación y gozo)"),

    # ── adoracion × paz combo — blend two tracks ─────────────────────────
    ("adoracion_paz", "adoracion",   -0.5, 0.98, "Adoración serena",
     "Adoracion serena — adoracion -0.5st 0.98x (alabanza contemplativa)"),
]


def ffmpeg_variant(src: str, dst: str, semitones: float, tempo: float) -> bool:
    """Pitch-shift + tempo-adjust src → dst MP3."""
    rate_factor = 2 ** (semitones / 12.0)
    # asetrate: changes pitch AND speed simultaneously
    # atempo: corrects speed back to original (if tempo=1.0) or adjusts it further
    # net result: duration changes by 1/tempo
    effective_tempo = rate_factor * tempo
    # atempo only accepts 0.5–100.0; chain two filters if needed
    if 0.5 <= effective_tempo <= 100.0:
        atempo_chain = f"atempo={effective_tempo:.6f}"
    elif effective_tempo < 0.5:
        atempo_chain = f"atempo=0.5,atempo={effective_tempo/0.5:.6f}"
    else:
        atempo_chain = f"atempo=2.0,atempo={effective_tempo/2.0:.6f}"

    af = f"asetrate=44100*{rate_factor:.6f},aresample=44100,{atempo_chain}"
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-af", af,
         "-c:a", "libmp3lame", "-b:a", "192k", "-q:a", "2", dst],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def duration_sec(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", path],
        capture_output=True, text=True,
    )
    streams = json.loads(r.stdout).get("streams", [{}])
    return float(streams[0].get("duration", 0)) if streams else 0.0


def main() -> None:
    os.makedirs(LOOPS_DIR, exist_ok=True)

    with open(MANIFEST) as f:
        manifest = json.load(f)
    moods = manifest.setdefault("moods", {})

    existing_count = len(moods)
    print(f"\nBuilding 30-mood audio pool  (have {existing_count})\n")

    ok = fail = skip = 0

    for out_stem, src_stem, semitones, tempo, mood_key, desc in NEW_VARIANTS:
        out_path = os.path.join(LOOPS_DIR, f"{out_stem}.mp3")
        src_path = os.path.join(LOOPS_DIR, f"{src_stem}.mp3")

        # Already exists — just ensure manifest entry
        if os.path.exists(out_path):
            if mood_key not in moods:
                moods[mood_key] = {"file": f"{out_stem}.mp3", "description": desc}
            skip += 1
            continue

        if not os.path.exists(src_path):
            print(f"  SKIP {out_stem} — source {src_stem}.mp3 not found")
            fail += 1
            continue

        print(f"  {mood_key:<18}  {src_stem}  {semitones:+.1f}st  {tempo:.2f}x", end="  ")
        success = ffmpeg_variant(src_path, out_path, semitones, tempo)
        if success and os.path.exists(out_path):
            dur = duration_sec(out_path)
            print(f"{dur:.0f}s  OK")
            moods[mood_key] = {"file": f"{out_stem}.mp3", "description": desc}
            ok += 1
        else:
            print("FAIL")
            if os.path.exists(out_path):
                os.remove(out_path)
            fail += 1

    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    import glob
    total_mp3  = len(glob.glob(os.path.join(LOOPS_DIR, "*.mp3")))
    total_mood = len(moods)

    print(f"\n{'='*55}")
    print(f"  New: {ok}  Skipped: {skip}  Failed: {fail}")
    print(f"  Total MP3 files : {total_mp3}")
    print(f"  Total moods     : {total_mood}")
    print(f"{'='*55}")

    if total_mood < 30:
        print(f"\n  NOTE: {30 - total_mood} moods still needed to reach 30.")


if __name__ == "__main__":
    main()
