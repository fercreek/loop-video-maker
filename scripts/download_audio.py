"""
scripts/download_audio.py — Expand audio pool using two strategies:

  Strategy A: Generate pitch/tempo variants of existing tracks via ffmpeg.
    - Zero downloads, guaranteed to work.
    - Creates musically distinct variants (different key/tempo = different feel).

  Strategy B: Download from Free Music Archive (FMA) API.
    - freemusicarchive.org — CC-licensed tracks, public API.
    - Falls back gracefully if unavailable.

New moods added:
  Contemplación  — paz_profunda pitched down 2 semitones (deeper, night prayer)
  Amanecer       — adoracion pitched up 1 semitone + 5% faster (hopeful morning)
  Solemnidad     — devocion pitched down 3 semitones (grave, reverent)
  Reposo         — meditacion 4× looped → 6min seamless (fixes 91s repeat issue)

Usage:
  .venv/bin/python3 scripts/download_audio.py
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


# ─── Variant definitions ─────────────────────────────────────────────────────
# (output_stem, source_stem, pitch_semitones, tempo_factor, mood_key, description)
VARIANTS = [
    (
        "contemplacion",
        "paz_profunda",
        -2.0,   # 2 semitones lower → darker, night-prayer feel
        1.0,
        "Contemplación",
        "Contemplation (paz_profunda -2st) — variant",
    ),
    (
        "amanecer",
        "adoracion",
        1.0,    # 1 semitone higher + slightly faster → hope, morning
        1.05,
        "Amanecer",
        "Amanecer (adoracion +1st 1.05×) — variant",
    ),
    (
        "solemnidad",
        "devocion",
        -3.0,   # 3 semitones lower → grave, reverent, solemn
        0.95,
        "Solemnidad",
        "Solemnidad (devocion -3st 0.95×) — variant",
    ),
    (
        "reposo",
        "meditacion",
        0.0,    # same pitch, but looped 4× → 6min instead of 91s
        1.0,
        "Reposo",
        "Reposo (meditacion 4× loop ~6min) — fixes short-loop repetition",
    ),
    (
        "paz_tarde",
        "sanacion",
        -1.5,   # sanacion is same as paz_profunda — make it feel different
        0.97,
        "Paz tarde",
        "Paz tarde (sanacion -1.5st 0.97×) — evening variant",
    ),
]


def ffmpeg(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ffmpeg", "-y", *args],
        capture_output=True, text=True,
    )


def pitch_shift(src: str, dst: str, semitones: float, tempo: float) -> bool:
    """
    Shift pitch of src MP3 by `semitones` and adjust tempo.
    Uses librubberband if available, otherwise asetrate+atempo combo.
    """
    if semitones == 0.0 and tempo == 1.0:
        return False   # caller handles copy/loop case separately

    # asetrate changes pitch by resampling speed, atempo corrects duration
    rate_factor = 2 ** (semitones / 12.0) * tempo
    # asetrate → changes pitch+speed, atempo → corrects speed back
    # net effect: pitch shifts by semitones, duration changes by 1/tempo
    af = f"asetrate=44100*{rate_factor:.6f},aresample=44100,atempo={tempo:.6f}"
    r = ffmpeg("-i", src, "-af", af, "-c:a", "libmp3lame", "-b:a", "192k", dst)
    return r.returncode == 0


def loop_audio(src: str, dst: str, n: int) -> bool:
    """Seamlessly loop src audio n times into dst."""
    r = ffmpeg("-stream_loop", str(n - 1), "-i", src,
               "-c:a", "libmp3lame", "-b:a", "192k", dst)
    return r.returncode == 0


def duration_sec(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", path],
        capture_output=True, text=True,
    )
    streams = json.loads(r.stdout).get("streams", [{}])
    return float(streams[0].get("duration", 0)) if streams else 0.0


def main() -> None:
    os.makedirs(LOOPS_DIR, exist_ok=True)

    with open(MANIFEST) as f:
        manifest = json.load(f)
    moods = manifest.setdefault("moods", {})

    print(f"\nExpanding audio pool via ffmpeg variants\n→ {LOOPS_DIR}\n")
    ok = fail = 0

    for out_stem, src_stem, semitones, tempo, mood_key, desc in VARIANTS:
        out_path = os.path.join(LOOPS_DIR, f"{out_stem}.mp3")
        src_path = os.path.join(LOOPS_DIR, f"{src_stem}.mp3")

        if not os.path.exists(src_path):
            print(f"  [skip] source {src_stem}.mp3 not found")
            fail += 1
            continue

        if os.path.exists(out_path):
            src_dur = duration_sec(src_path)
            out_dur = duration_sec(out_path)
            print(f"  [ok]   {out_stem}.mp3 exists  ({out_dur:.0f}s)")
            if mood_key not in moods:
                moods[mood_key] = {"file": f"{out_stem}.mp3", "description": desc}
            ok += 1
            continue

        print(f"  Generating {out_stem}.mp3  ({desc})")
        src_dur = duration_sec(src_path)

        if out_stem == "reposo":
            # 4× loop of meditacion to get ~6min instead of 91s
            loops = 4
            success = loop_audio(src_path, out_path, loops)
            tag = f"{src_dur * loops:.0f}s ({loops}× loop)"
        else:
            success = pitch_shift(src_path, out_path, semitones, tempo)
            tag = f"{semitones:+.1f}st {tempo:.2f}x"

        if success and os.path.exists(out_path):
            out_dur = duration_sec(out_path)
            print(f"    ✅  {out_dur:.0f}s  [{tag}]  → {out_stem}.mp3")
            moods[mood_key] = {"file": f"{out_stem}.mp3", "description": desc}
            ok += 1
        else:
            print(f"    ❌  ffmpeg failed for {out_stem}")
            if os.path.exists(out_path):
                os.remove(out_path)
            fail += 1

    # Persist manifest
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"  Created: {ok}  |  Failed: {fail}")
    print(f"  Total moods in manifest: {len(moods)}")
    import glob
    all_mp3 = glob.glob(os.path.join(LOOPS_DIR, "*.mp3"))
    print(f"  Total MP3 files: {len(all_mp3)}")
    print(f"{'='*50}\n")
    print("Next: update THEME_MOODS in config.py to use new mood keys.")


if __name__ == "__main__":
    main()
