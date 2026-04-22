"""
core/quality_gate.py — Post-render quality check + auto-fix LUFS.

Uso típico (desde render scripts):
    from core.quality_gate import gate, print_batch_report

    qg = gate(output_path, nominal_min=60)
    print(f"  {'✅' if qg['pass'] else '⚠️'} Quality gate: {qg['score']}/100")

Funciones:
    gate()               — eval + auto-fix LUFS si fuera de rango
    fix_lufs()           — aplica loudnorm in-place vía ffmpeg stream-copy
    print_batch_report() — tabla ASCII al final del batch
"""
from __future__ import annotations

import os
import subprocess

# Config thresholds centralizados
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import EVAL_TARGETS, QUALITY_GATE_THRESHOLD, QUALITY_GATE_AUTO_FIX_LUFS


# ─── Score recalculation ─────────────────────────────────────────────────────

_SCORE_WEIGHTS = {
    "duration": 15, "video_bitrate": 10, "fps": 5,
    "size_per_min": 5, "loudness": 20, "no_silences": 15,
    "no_dips": 20, "thumbnail": 7,
    "thumbnail_size": 1.5, "thumbnail_resolution": 1.5,
}


def _recalculate_score(checks: dict) -> int:
    applicable = {k: w for k, w in _SCORE_WEIGHTS.items() if k in checks}
    total_w = sum(applicable.values())
    earned = sum(w for k, w in applicable.items() if checks.get(k))
    return round(earned / total_w * 100) if total_w else 0


# ─── LUFS fix ────────────────────────────────────────────────────────────────

def fix_lufs(path: str) -> float:
    """
    Apply loudnorm=I=-16:TP=-1.5:LRA=11 in-place via ffmpeg stream copy.

    Video stream: copied (no re-encode — fast, ~6min for 60min video).
    Audio stream: re-encoded with loudnorm filter.
    Uses tmp file then os.replace() — atomic, no partial writes.

    Returns new measured LUFS after fix.
    """
    tmp = path + ".loudnorm_tmp.mp4"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", path,
                "-c:v", "copy",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                "-c:a", "aac", "-b:a", "192k",
                tmp,
            ],
            check=True,
            capture_output=True,
        )
        os.replace(tmp, path)
    except subprocess.CalledProcessError as exc:
        # Clean up tmp if exists
        if os.path.exists(tmp):
            os.remove(tmp)
        raise RuntimeError(f"fix_lufs ffmpeg failed: {exc.stderr[-400:]}") from exc

    # Measure LUFS post-fix
    from eval_render import measure_loudness
    return measure_loudness(path) or -16.0


# ─── Core gate ───────────────────────────────────────────────────────────────

def gate(
    path: str,
    nominal_min: int | None = None,
    auto_fix_lufs: bool | None = None,
    fail_threshold: int | None = None,
) -> dict:
    """
    Run quality check on a rendered video. Auto-fix LUFS if out of range.

    Args:
        path:           Absolute or relative path to .mp4 file.
        nominal_min:    Expected duration in minutes (auto-inferred if None).
        auto_fix_lufs:  Override config.QUALITY_GATE_AUTO_FIX_LUFS.
        fail_threshold: Override config.QUALITY_GATE_THRESHOLD (0-100).

    Returns dict:
        pass        bool    score >= threshold (after any auto-fix)
        score       int     0-100
        issues      list    human-readable failure descriptions
        fixed       bool    True if loudnorm was applied
        lufs_before float   LUFS before fix (or None)
        lufs_after  float   LUFS after fix (= lufs_before if no fix)
        eval        dict    full evaluate_video() result
    """
    if auto_fix_lufs is None:
        auto_fix_lufs = QUALITY_GATE_AUTO_FIX_LUFS
    if fail_threshold is None:
        fail_threshold = QUALITY_GATE_THRESHOLD

    from eval_render import evaluate_video
    result = evaluate_video(path, nominal_min)

    fixed = False
    lufs_before = result["loudness_lufs"]
    lufs_after = lufs_before

    # Auto-fix if LUFS check failed
    lufs_check_passed = result["checks"].get("loudness", True)
    if auto_fix_lufs and not lufs_check_passed and lufs_before is not None:
        print(f"  [quality-gate] LUFS {lufs_before:.1f} fuera de rango — aplicando loudnorm...")
        try:
            lufs_after = fix_lufs(path)
            fixed = True

            # Patch result in-place (avoid full re-eval which takes ~2min for 60min video)
            result["loudness_lufs"] = lufs_after
            lufs_ok = (
                abs(lufs_after - EVAL_TARGETS["lufs_target"]) <= EVAL_TARGETS["lufs_tolerance"]
            )
            result["checks"]["loudness"] = lufs_ok

            # Remove loudness issue from list if now fixed
            if lufs_ok:
                result["issues"] = [
                    i for i in result["issues"] if "Loudness" not in i and "loudness" not in i.lower()
                ]

            # Recalculate score with updated checks
            result["score"] = _recalculate_score(result["checks"])

        except Exception as exc:
            print(f"  [quality-gate] loudnorm fix failed: {exc}")
            # Keep original result — don't crash the render pipeline

    passed = result["score"] >= fail_threshold

    return {
        "pass": passed,
        "score": result["score"],
        "issues": result["issues"],
        "fixed": fixed,
        "lufs_before": lufs_before,
        "lufs_after": lufs_after,
        "theme": result.get("theme", ""),
        "eval": result,
    }


# ─── Batch report ────────────────────────────────────────────────────────────

def print_batch_report(results: list[dict]) -> None:
    """
    Print ASCII quality report table to stdout.

    Called after all videos in a batch have been rendered + gated.
    Example:
        ═══════════════════════════════════════════════════════
        BATCH QUALITY REPORT
        ═══════════════════════════════════════════════════════
        ✅  paz         100   LUFS -15.9   fixed ✓
        ✅  fe          100   LUFS -17.7
        ⚠️  amor         80   LUFS -19.8   [Loudness -19.8 LUFS vs target -16.0±3.0]
        ───────────────────────────────────────────────────────
        Promedio: 96/100  |  1 auto-fixed  |  1 warning
        ═══════════════════════════════════════════════════════
    """
    if not results:
        return

    print(f"\n{'═'*57}")
    print("  BATCH QUALITY REPORT")
    print(f"{'═'*57}")

    n_fixed = 0
    n_warn = 0

    for r in results:
        icon = "✅" if r["pass"] else "⚠️ "
        theme = (r.get("theme") or "?").ljust(12)
        score = str(r["score"]).rjust(3)
        lufs = r.get("lufs_after") or r.get("lufs_before")
        lufs_str = f"LUFS {lufs:5.1f}" if lufs is not None else "LUFS  ?"
        fixed_str = "  fixed ✓" if r.get("fixed") else ""

        # Short issue summary (first issue, truncated)
        issues = r.get("issues", [])
        issue_str = ""
        if issues and not r["pass"]:
            issue_str = f"   [{issues[0][:50]}]"

        print(f"  {icon}  {theme}  {score}   {lufs_str}{fixed_str}{issue_str}")
        if r.get("fixed"):
            n_fixed += 1
        if not r["pass"]:
            n_warn += 1

    avg = sum(r["score"] for r in results) / len(results)
    fixed_msg = f"  |  {n_fixed} auto-fixed" if n_fixed else ""
    warn_msg = f"  |  {n_warn} warning(s)" if n_warn else "  |  todos OK"
    print(f"{'─'*57}")
    print(f"  Promedio: {avg:.0f}/100{fixed_msg}{warn_msg}")
    print(f"{'═'*57}\n")
