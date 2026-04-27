"""
core/metrics_logger.py — Structured per-render metrics (JSON + step timers).

Escribe:
  logs/metrics/YYYY-MM-DD_HH-MM_<theme>_<format>.json   ← per-render detallado
  logs/metrics_summary.jsonl                              ← append-only, trend analysis

Métricas por step:
  audio_gen    — tiempo generando playlist + moods usados
  bg_prep      — procesamiento imágenes (split-tone, vignette)
  text_render  — pre-render PNGs de texto
  clips        — render paralelo ffmpeg (avg/min/max/top5-slow + effect distribution)
  concat       — stream copy clips → video_silent.mp4
  mux          — mezcla audio (afade + loudnorm)
  quality_gate — eval LUFS, bitrate, size

Uso en render scripts:
    from core.metrics_logger import RenderMetrics

    metrics = RenderMetrics(theme="paz", format_key="60min",
                            output_path=output_path, config={...})
    metrics.step_start("audio_gen")
    audio_path = generate_playlist(...)
    metrics.step_end("audio_gen", moods=moods, total_audio_sec=total_seconds)

    renderizar_video_fast(..., metrics=metrics)

    qg = gate(output_path, nominal_min=60)
    metrics.step_end("quality_gate", **qg)
    metrics.finish()
"""
from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any


class RenderMetrics:
    """
    Collects step timings and asset stats for one render session.
    Thread-safe for step_end() calls from the main thread only.
    """

    def __init__(
        self,
        theme: str,
        format_key: str,       # "60min" | "120min" | "10min" | "preview"
        output_path: str,
        config: dict[str, Any] | None = None,
        log_dir: str = "logs",
    ):
        self.theme = theme
        self.format_key = format_key
        self.output_path = output_path
        self.config = config or {}
        self.log_dir = log_dir

        self._steps: dict[str, dict] = {}
        self._step_starts: dict[str, float] = {}
        self._started_at = datetime.now(timezone.utc)
        self._session_start = time.time()

    # ── Step API ─────────────────────────────────────────────────────────────

    def step_start(self, name: str) -> None:
        """Mark start of a named step."""
        self._step_starts[name] = time.time()

    def step_end(self, name: str, **data: Any) -> None:
        """
        Mark end of named step. Computes elapsed from step_start().
        Pass any extra key=value pairs to store alongside timing.
        """
        t0 = self._step_starts.get(name, self._session_start)
        elapsed = round(time.time() - t0, 2)
        entry: dict[str, Any] = {"sec": elapsed}
        entry.update(data)
        self._steps[name] = entry

    @contextmanager
    def step(self, name: str, **data: Any):
        """
        Context-manager step timer. Extra data added at exit.
        Usage:
            with metrics.step("bg_prep", images_processed=36):
                ...
        """
        self.step_start(name)
        try:
            yield
        finally:
            self.step_end(name, **data)

    def update_step(self, name: str, **data: Any) -> None:
        """Add/overwrite keys in an existing step dict."""
        if name not in self._steps:
            self._steps[name] = {}
        self._steps[name].update(data)

    # ── Finalize ─────────────────────────────────────────────────────────────

    def finish(self) -> str:
        """
        Write JSON metrics file + append summary line.
        Call once after all steps + quality gate are recorded.
        Returns path to the JSON file.
        """
        total_sec = round(time.time() - self._session_start, 1)
        finished_at = datetime.now(timezone.utc)

        # Output file stats
        output_stats: dict[str, Any] = {}
        if self.output_path and os.path.exists(self.output_path):
            size_mb = os.path.getsize(self.output_path) / 1024 / 1024
            # Infer minutes from format_key ("60min" → 60, "120min" → 120)
            try:
                dur_min = int("".join(c for c in self.format_key if c.isdigit()) or "60")
            except ValueError:
                dur_min = 60
            output_stats = {
                "size_mb": round(size_mb, 1),
                "mb_per_min": round(size_mb / max(dur_min, 1), 1),
            }

        # Pull quality gate data from steps if recorded there
        qg = self._steps.get("quality_gate", {})

        doc: dict[str, Any] = {
            "theme": self.theme,
            "format": self.format_key,
            "engine_version": _engine_version(),
            "output_path": self.output_path,
            "started_at": self._started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "total_sec": total_sec,
            "total_min": round(total_sec / 60, 1),
            "config": self.config,
            "steps": self._steps,
            "output": {
                **output_stats,
                "lufs": qg.get("lufs_after"),
                "lufs_fixed": qg.get("fixed", False),
                "quality_score": qg.get("score"),
                "quality_pass": qg.get("pass"),
                "quality_issues": qg.get("issues", []),
            },
        }

        # Write per-render JSON
        metrics_dir = os.path.join(self.log_dir, "metrics")
        os.makedirs(metrics_dir, exist_ok=True)
        ts = self._started_at.strftime("%Y-%m-%d_%H-%M")
        filename = f"{ts}_{self.theme}_{self.format_key}.json"
        json_path = os.path.join(metrics_dir, filename)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2, default=str)

        # Append compact summary line (one JSON object per line) for trend analysis
        summary_path = os.path.join(self.log_dir, "metrics_summary.jsonl")
        summary: dict[str, Any] = {
            "ts": finished_at.isoformat(),
            "theme": self.theme,
            "format": self.format_key,
            "total_sec": total_sec,
            "size_mb": output_stats.get("size_mb"),
            "mb_per_min": output_stats.get("mb_per_min"),
            "quality_score": qg.get("score"),
            "lufs": qg.get("lufs_after"),
            "lufs_fixed": qg.get("fixed", False),
        }
        # Step seconds for trend charts
        for step_name in ("audio_gen", "bg_prep", "text_render", "clips", "concat", "mux", "quality_gate"):
            s = self._steps.get(step_name, {})
            if "sec" in s:
                summary[f"step_{step_name}_sec"] = s["sec"]

        # Clip stats summary
        clips = self._steps.get("clips", {})
        if clips.get("avg_sec"):
            summary["clips_avg_sec"] = clips["avg_sec"]
            summary["clips_per_sec"] = clips.get("clips_per_sec")

        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, ensure_ascii=False, default=str) + "\n")

        print(f"  [metrics] {json_path}")
        return json_path


# ── Helpers ───────────────────────────────────────────────────────────────────

def _engine_version() -> str:
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=3,
        )
        return f"v3.9-{r.stdout.strip()}"
    except Exception:
        return "v3.9-unknown"
