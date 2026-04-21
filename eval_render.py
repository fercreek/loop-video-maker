"""
eval_render.py — Auto-evaluación objetiva de videos renderizados.

Mide cada MP4 y produce score 0-100 + issues.

Uso:
    .venv/bin/python3 eval_render.py output/youtube_60min/
    .venv/bin/python3 eval_render.py output/youtube_60min/amor/
    .venv/bin/python3 eval_render.py path/to/video.mp4

Output:
    eval/<theme>_<timestamp>.json   — detalle por video
    eval/summary.md                 — tabla acumulativa
"""
from __future__ import annotations

import sys
import os
import json
import glob
import subprocess
import re
from datetime import datetime
from pathlib import Path

EVAL_DIR = "eval"
os.makedirs(EVAL_DIR, exist_ok=True)

# ─── Targets ─────────────────────────────────────────────────────────────────
TARGETS = {
    "duration_tolerance_sec": 5.0,          # ±5s vs nominal
    "min_bitrate_kbps": 3000,
    "expected_fps": 12,
    "mb_per_min_min": 18,
    "mb_per_min_max": 32,
    "lufs_target": -16.0,                    # relaxing music sweet spot (YouTube normalizes >-14)
    "lufs_tolerance": 3.0,
    "max_silence_sec": 2.0,
    "max_dip_db": 6.0,                       # crossfade boundary dip
}


def ffprobe(path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {r.stderr}")
    return json.loads(r.stdout)


def measure_loudness(path: str) -> float | None:
    """Run ebur128, return integrated LUFS."""
    cmd = [
        "ffmpeg", "-nostats", "-i", path,
        "-filter_complex", "ebur128=peak=true",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    # Capture from Summary block: "Integrated loudness:\n    I:   -XX.X LUFS"
    m = re.search(r"Integrated loudness:\s*\n\s*I:\s+(-?\d+\.\d+)\s+LUFS", r.stderr)
    if m:
        return float(m.group(1))
    # Fallback: last match in stream (final integrated value)
    matches = re.findall(r"I:\s+(-?\d+\.\d+)\s+LUFS", r.stderr)
    return float(matches[-1]) if matches else None


def detect_silence(path: str, min_sec: float = 2.0) -> list[tuple[float, float]]:
    """Return list of (start, duration) silence intervals."""
    cmd = [
        "ffmpeg", "-nostats", "-i", path,
        "-af", f"silencedetect=noise=-40dB:d={min_sec}",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    starts = [float(m) for m in re.findall(r"silence_start:\s+([\d.]+)", r.stderr)]
    durs = [float(m) for m in re.findall(r"silence_duration:\s+([\d.]+)", r.stderr)]
    return list(zip(starts, durs))


def detect_dips(path: str, window_sec: float = 1.0) -> list[tuple[float, float]]:
    """
    Detect RMS dips > max_dip_db vs rolling median.
    Returns (timestamp_sec, dip_db).
    """
    cmd = [
        "ffmpeg", "-nostats", "-i", path,
        "-af", f"astats=metadata=1:reset={window_sec},ametadata=print:key=lavfi.astats.Overall.RMS_level",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    rms_vals = []
    current_t = 0.0
    for line in r.stderr.splitlines():
        tm = re.match(r"pts_time:([\d.]+)", line)
        if tm:
            current_t = float(tm.group(1))
        vm = re.search(r"RMS_level=(-?[\d.inf]+)", line)
        if vm and vm.group(1) not in ("-inf", "inf", "nan"):
            try:
                rms_vals.append((current_t, float(vm.group(1))))
            except ValueError:
                pass
    if len(rms_vals) < 10:
        return []
    # Rolling median over 20s window
    dips = []
    vals = [v for _, v in rms_vals]
    n = len(vals)
    for i in range(10, n - 10):
        window = sorted(vals[max(0, i - 10):i + 10])
        median = window[len(window) // 2]
        if median - vals[i] > TARGETS["max_dip_db"]:
            dips.append((rms_vals[i][0], median - vals[i]))
    # Skip dips in first/last 10s (fade in/out, not crossfade bugs)
    if rms_vals:
        total = rms_vals[-1][0]
        dips = [(t, d) for t, d in dips if 10 < t < total - 10]
    # Cluster adjacent dips
    if not dips:
        return []
    clustered = [dips[0]]
    for t, d in dips[1:]:
        if t - clustered[-1][0] < 5.0:
            if d > clustered[-1][1]:
                clustered[-1] = (t, d)
        else:
            clustered.append((t, d))
    return clustered


def evaluate_video(path: str, nominal_minutes: int | None = None) -> dict:
    """Run all checks on a single MP4. Return result dict with score + issues."""
    path = os.path.abspath(path)
    size_bytes = os.path.getsize(path)
    size_mb = size_bytes / 1024 / 1024

    probe = ffprobe(path)
    duration = float(probe["format"]["duration"])
    total_bitrate = int(probe["format"].get("bit_rate", 0)) // 1000  # kbps

    v_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    fps_str = v_stream.get("r_frame_rate", "0/1")
    num, den = (int(x) for x in fps_str.split("/"))
    fps = num / den if den else 0
    width, height = v_stream.get("width"), v_stream.get("height")
    v_bitrate = int(v_stream.get("bit_rate", 0)) // 1000 or total_bitrate

    a_stream = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)

    # Infer nominal duration if not provided
    if nominal_minutes is None:
        # Snap to nearest 5-min bucket
        nominal_minutes = round(duration / 60 / 5) * 5 or round(duration / 60)

    nominal_sec = nominal_minutes * 60
    mb_per_min = size_mb / (duration / 60) if duration else 0

    issues = []
    checks = {}

    # 1. Duration
    dur_diff = abs(duration - nominal_sec)
    checks["duration"] = dur_diff <= TARGETS["duration_tolerance_sec"]
    if not checks["duration"]:
        issues.append(f"Duración {duration:.0f}s vs nominal {nominal_sec}s (Δ {dur_diff:.0f}s)")

    # 2. Video bitrate
    checks["video_bitrate"] = v_bitrate >= TARGETS["min_bitrate_kbps"]
    if not checks["video_bitrate"]:
        issues.append(f"Bitrate video {v_bitrate}k < {TARGETS['min_bitrate_kbps']}k")

    # 3. FPS
    checks["fps"] = abs(fps - TARGETS["expected_fps"]) < 0.5
    if not checks["fps"]:
        issues.append(f"FPS real {fps:.1f} vs esperado {TARGETS['expected_fps']}")

    # 4. Size/min
    checks["size_per_min"] = TARGETS["mb_per_min_min"] <= mb_per_min <= TARGETS["mb_per_min_max"]
    if not checks["size_per_min"]:
        issues.append(f"MB/min {mb_per_min:.1f} fuera de [{TARGETS['mb_per_min_min']}-{TARGETS['mb_per_min_max']}]")

    # 5. Loudness
    lufs = measure_loudness(path) if a_stream else None
    if lufs is not None:
        checks["loudness"] = abs(lufs - TARGETS["lufs_target"]) <= TARGETS["lufs_tolerance"]
        if not checks["loudness"]:
            issues.append(f"Loudness {lufs:.1f} LUFS vs target {TARGETS['lufs_target']}±{TARGETS['lufs_tolerance']}")
    else:
        checks["loudness"] = False
        issues.append("No se pudo medir loudness")

    # 6. Silences
    silences = detect_silence(path, TARGETS["max_silence_sec"]) if a_stream else []
    checks["no_silences"] = len(silences) == 0
    if silences:
        issues.append(f"{len(silences)} silencios >{TARGETS['max_silence_sec']}s: {silences[:3]}")

    # 7. Dips (crossfade boundaries)
    dips = detect_dips(path) if a_stream else []
    checks["no_dips"] = len(dips) == 0
    if dips:
        issues.append(f"{len(dips)} dips audio >{TARGETS['max_dip_db']}dB: {[(f'{t:.0f}s', f'-{d:.1f}dB') for t,d in dips[:5]]}")

    # 8. Thumbnail
    video_dir = os.path.dirname(path)
    theme = Path(path).stem.replace("_60min", "").replace("_120min", "")
    # thumbnail_gen uses {theme}_thumb.jpg
    thumb_candidates = [
        os.path.join(video_dir, f"{theme}_thumb.jpg"),
        os.path.join(video_dir, f"{theme}_thumbnail.jpg"),
    ]
    thumb_path = next((p for p in thumb_candidates if os.path.exists(p)), thumb_candidates[0])
    checks["thumbnail"] = any(os.path.exists(p) for p in thumb_candidates)
    if not checks["thumbnail"]:
        issues.append(f"Thumbnail no encontrado: {thumb_path}")

    # Score: weighted average
    weights = {
        "duration": 15, "video_bitrate": 10, "fps": 5,
        "size_per_min": 5, "loudness": 20, "no_silences": 15,
        "no_dips": 20, "thumbnail": 10,
    }
    total_w = sum(weights.values())
    earned = sum(weights[k] for k, ok in checks.items() if ok)
    score = round(earned / total_w * 100)

    return {
        "path": path,
        "theme": theme,
        "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        "duration_sec": round(duration, 1),
        "nominal_minutes": nominal_minutes,
        "video_bitrate_kbps": v_bitrate,
        "total_bitrate_kbps": total_bitrate,
        "fps": round(fps, 2),
        "resolution": f"{width}x{height}",
        "size_mb": round(size_mb, 1),
        "mb_per_min": round(mb_per_min, 2),
        "loudness_lufs": round(lufs, 2) if lufs is not None else None,
        "silences": silences,
        "audio_dips": [(round(t, 1), round(d, 2)) for t, d in dips],
        "thumbnail_exists": checks["thumbnail"],
        "checks": checks,
        "issues": issues,
        "score": score,
    }


def find_videos(arg: str) -> list[str]:
    if os.path.isfile(arg) and arg.endswith(".mp4"):
        return [arg]
    if os.path.isdir(arg):
        return sorted(glob.glob(os.path.join(arg, "**", "*.mp4"), recursive=True))
    return []


def write_json(result: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    out_path = os.path.join(EVAL_DIR, f"{result['theme']}_{ts}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return out_path


def append_summary(results: list[dict]) -> str:
    out_path = os.path.join(EVAL_DIR, "summary.md")
    exists = os.path.exists(out_path)
    with open(out_path, "a") as f:
        if not exists:
            f.write("# Eval Summary — Loop Video Maker\n\n")
            f.write("| Fecha | Tema | Score | Duración | Bitrate | LUFS | Silencios | Dips | Issues |\n")
            f.write("|-------|------|-------|----------|---------|------|-----------|------|--------|\n")
        for r in results:
            date = r["evaluated_at"][:10]
            f.write(
                f"| {date} | {r['theme']} | **{r['score']}** | "
                f"{r['duration_sec']/60:.1f}min | {r['video_bitrate_kbps']}k | "
                f"{r['loudness_lufs']} | {len(r['silences'])} | {len(r['audio_dips'])} | "
                f"{len(r['issues'])} |\n"
            )
    return out_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    target = sys.argv[1]
    videos = find_videos(target)
    if not videos:
        print(f"No se encontraron .mp4 en {target}")
        sys.exit(1)

    print(f"Evaluando {len(videos)} video(s)...\n")
    results = []
    for v in videos:
        print(f"→ {v}")
        try:
            r = evaluate_video(v)
            json_path = write_json(r)
            status = "✅" if r["score"] >= 80 else "⚠️" if r["score"] >= 60 else "❌"
            print(f"  {status} Score {r['score']}/100  ({len(r['issues'])} issues)")
            for iss in r["issues"]:
                print(f"     - {iss}")
            print(f"  → {json_path}")
            results.append(r)
        except Exception as e:
            print(f"  ❌ Error: {e}")

    if results:
        summary = append_summary(results)
        avg = sum(r["score"] for r in results) / len(results)
        print(f"\n📊 Promedio: {avg:.0f}/100  ({len(results)} videos)")
        print(f"   Summary: {summary}")


if __name__ == "__main__":
    main()
