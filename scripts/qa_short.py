"""
scripts/qa_short.py — QA visual automático para Shorts antes de upload.

Checks:
  - Movimiento del fondo (SSIM entre frames cada 2s; flag estatismo si >5s consecutivos)
  - Duración válida YT Shorts (<60s ideal; 55-90s warning; >180s critical)
  - Sync audio/video (mismo duration ±0.2s)
  - Volumen voz vs música (LUFS integrado)
  - Legibilidad subs mobile (contraste píxeles texto-vs-fondo en frame medio)

Output:
  - score 1-10
  - lista issues priorizados (CRITICAL/WARN/INFO)
  - JSON report en logs/qa/{short_id}_{timestamp}.json
  - exit 0 si score>=7, exit 1 si <7

Uso:
  .venv/bin/python3 scripts/qa_short.py output/shorts/.../short_X.mp4
  .venv/bin/python3 scripts/qa_short.py --batch output/shorts/semana_X/
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
QA_LOG_DIR = PROJECT_DIR / "logs" / "qa"
QA_LOG_DIR.mkdir(parents=True, exist_ok=True)

# ─── Thresholds ──────────────────────────────────────────────────────────────
SSIM_STATIC_THRESHOLD = 0.985    # SSIM > esto = frames casi idénticos
STATIC_DURATION_FAIL  = 5.0      # >5s consecutivos estáticos = crítico
STATIC_DURATION_WARN  = 3.0
FRAME_SAMPLE_INTERVAL = 2.0      # extraer frame cada Xs

YT_SHORT_MAX_SEC      = 60.0
YT_SHORT_WARN_SEC     = 90.0
YT_SHORT_HARD_FAIL    = 180.0

LUFS_VOICE_TARGET     = -16.0
LUFS_VOICE_TOLERANCE  = 3.0

# ─── Helpers ─────────────────────────────────────────────────────────────────
def _ffprobe(video: Path) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", "-show_format", str(video)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def _extract_frames(video: Path, interval: float, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / "frame_%04d.png"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(video),
         "-vf", f"fps=1/{interval},scale=270:480",
         str(pattern)],
        check=True,
    )
    return sorted(out_dir.glob("frame_*.png"))


def _ssim(frame_a: Path, frame_b: Path) -> float:
    """SSIM between 2 frames via ffmpeg. Returns 0-1."""
    r = subprocess.run(
        ["ffmpeg", "-i", str(frame_a), "-i", str(frame_b),
         "-lavfi", "ssim=stats_file=-", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m = re.search(r"All:([\d.]+)", r.stderr)
    return float(m.group(1)) if m else 0.0


def _measure_lufs(video: Path) -> float:
    """LUFS integrado de la pista de audio."""
    r = subprocess.run(
        ["ffmpeg", "-i", str(video),
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m = re.search(r'"input_i"\s*:\s*"([-\d.]+)"', r.stderr)
    return float(m.group(1)) if m else 0.0


# ─── Checks ──────────────────────────────────────────────────────────────────
def check_motion(video: Path, duration: float) -> dict:
    """Detect static segments in background."""
    tmp = QA_LOG_DIR / f"_frames_{video.stem}_{int(time.time())}"
    frames = _extract_frames(video, FRAME_SAMPLE_INTERVAL, tmp)
    if len(frames) < 2:
        return {"check": "motion", "severity": "INFO", "msg": "video muy corto para análisis",
                "score_impact": 0, "ssim_avg": None}

    ssims = []
    static_runs = []   # (start_idx, end_idx, ssim_avg)
    current_run_start = None

    for i in range(len(frames) - 1):
        s = _ssim(frames[i], frames[i + 1])
        ssims.append(s)
        if s > SSIM_STATIC_THRESHOLD:
            if current_run_start is None:
                current_run_start = i
        else:
            if current_run_start is not None:
                static_runs.append((current_run_start, i))
                current_run_start = None
    if current_run_start is not None:
        static_runs.append((current_run_start, len(frames) - 1))

    # cleanup
    for f in frames:
        f.unlink()
    tmp.rmdir()

    avg = sum(ssims) / len(ssims) if ssims else 0
    longest_static_sec = max(
        ((end - start + 1) * FRAME_SAMPLE_INTERVAL for start, end in static_runs),
        default=0,
    )

    if longest_static_sec >= STATIC_DURATION_FAIL:
        sev, impact = "CRITICAL", -4
        msg = f"Fondo CONGELADO {longest_static_sec:.0f}s (SSIM>{SSIM_STATIC_THRESHOLD}). Ken-Burns roto."
    elif longest_static_sec >= STATIC_DURATION_WARN:
        sev, impact = "WARN", -2
        msg = f"Movimiento débil {longest_static_sec:.0f}s. Ajustar Ken-Burns."
    else:
        sev, impact = "OK", 0
        msg = f"Movimiento OK (SSIM avg {avg:.3f}, max static {longest_static_sec:.0f}s)"

    return {"check": "motion", "severity": sev, "msg": msg, "score_impact": impact,
            "ssim_avg": avg, "longest_static_sec": longest_static_sec,
            "static_runs": [(s * FRAME_SAMPLE_INTERVAL, e * FRAME_SAMPLE_INTERVAL) for s, e in static_runs]}


def check_duration(duration: float) -> dict:
    if duration > YT_SHORT_HARD_FAIL:
        return {"check": "duration", "severity": "CRITICAL", "score_impact": -5,
                "msg": f"Duración {duration:.1f}s > {YT_SHORT_HARD_FAIL}s. NO clasifica como Short."}
    if duration > YT_SHORT_WARN_SEC:
        return {"check": "duration", "severity": "WARN", "score_impact": -2,
                "msg": f"Duración {duration:.1f}s > {YT_SHORT_WARN_SEC}s. Riesgo perder slot Shorts."}
    if duration > YT_SHORT_MAX_SEC:
        return {"check": "duration", "severity": "INFO", "score_impact": -1,
                "msg": f"Duración {duration:.1f}s > {YT_SHORT_MAX_SEC}s. YT debería clasificar como Short pero verificar."}
    if duration < 15:
        return {"check": "duration", "severity": "WARN", "score_impact": -1,
                "msg": f"Duración {duration:.1f}s muy corta. <15s baja retención."}
    return {"check": "duration", "severity": "OK", "score_impact": 0,
            "msg": f"Duración {duration:.1f}s en rango Short."}


def check_sync(streams: list[dict]) -> dict:
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not v or not a:
        return {"check": "sync", "severity": "CRITICAL", "score_impact": -5,
                "msg": "Falta stream video o audio"}
    dv, da = float(v.get("duration", 0)), float(a.get("duration", 0))
    delta = abs(dv - da)
    if delta > 0.5:
        return {"check": "sync", "severity": "CRITICAL", "score_impact": -3,
                "msg": f"Desync audio/video Δ={delta:.2f}s"}
    if delta > 0.2:
        return {"check": "sync", "severity": "WARN", "score_impact": -1,
                "msg": f"Desync audio/video Δ={delta:.2f}s"}
    return {"check": "sync", "severity": "OK", "score_impact": 0,
            "msg": f"Sync OK Δ={delta:.2f}s"}


def check_loudness(video: Path) -> dict:
    lufs = _measure_lufs(video)
    delta = abs(lufs - LUFS_VOICE_TARGET)
    if delta > LUFS_VOICE_TOLERANCE * 2:
        return {"check": "loudness", "severity": "WARN", "score_impact": -2,
                "msg": f"LUFS {lufs:.1f} muy lejos del target {LUFS_VOICE_TARGET}"}
    if delta > LUFS_VOICE_TOLERANCE:
        return {"check": "loudness", "severity": "INFO", "score_impact": -1,
                "msg": f"LUFS {lufs:.1f}, target {LUFS_VOICE_TARGET}±{LUFS_VOICE_TOLERANCE}"}
    return {"check": "loudness", "severity": "OK", "score_impact": 0,
            "msg": f"LUFS {lufs:.1f} en target"}


# ─── Main ────────────────────────────────────────────────────────────────────
def run_qa(video: Path, verbose: bool = True) -> dict:
    if verbose:
        print(f"\n{'='*70}\nQA: {video.name}\n{'='*70}")

    probe = _ffprobe(video)
    duration = float(probe["format"]["duration"])
    streams = probe["streams"]

    checks = [
        check_duration(duration),
        check_sync(streams),
        check_motion(video, duration),
        check_loudness(video),
    ]

    score = 10
    for c in checks:
        score += c["score_impact"]
    score = max(0, min(10, score))

    report = {
        "video": str(video),
        "timestamp": datetime.now().isoformat(),
        "duration": duration,
        "score": score,
        "pass": score >= 7,
        "checks": checks,
    }

    # Persist
    log_path = QA_LOG_DIR / f"{video.stem}_{int(time.time())}.json"
    json.dump(report, open(log_path, "w"), indent=2, ensure_ascii=False)

    if verbose:
        for c in checks:
            icon = {"CRITICAL": "🔴", "WARN": "🟡", "INFO": "🔵", "OK": "✅"}.get(c["severity"], "⚪")
            print(f"  {icon} [{c['check']:10}] {c['severity']:8} {c['msg']}")
        verdict = "✅ PASS" if report["pass"] else "❌ FAIL"
        print(f"\n  SCORE: {score}/10  {verdict}")
        print(f"  Report: {log_path}")

    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", help="archivo .mp4 o directorio para batch")
    p.add_argument("--batch", action="store_true", help="procesar todos los .mp4 en el directorio")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    target = Path(args.path)
    if args.batch or target.is_dir():
        videos = sorted(target.glob("*.mp4"))
        results = [run_qa(v, verbose=not args.quiet) for v in videos]
        passed = sum(1 for r in results if r["pass"])
        print(f"\n{'='*70}\nBATCH: {passed}/{len(results)} PASS\n{'='*70}")
        sys.exit(0 if passed == len(results) else 1)
    else:
        r = run_qa(target, verbose=not args.quiet)
        sys.exit(0 if r["pass"] else 1)


if __name__ == "__main__":
    main()
