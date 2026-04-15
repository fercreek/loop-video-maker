"""
core/render_logger.py — Per-render learning logs, file event log, LEARNINGS.md

Every render session writes:
  logs/renders/YYYY-MM-DD_HH-MM_<theme>.md   ← config + metrics + auto-verdict
  logs/LEARNINGS.md                           ← running render index + lessons
  logs/files.log                              ← every CREATE / CLEAN / SKIP event

After watching the video, fill in the "Mejoras para próxima iteración" section
at the bottom of the render log. Those notes feed future iterations.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from datetime import datetime
from typing import Any


# ─── File event log ───────────────────────────────────────────────────────────

def log_file_event(
    event: str,          # "CREATE" | "CLEAN" | "SKIP" | "ERROR"
    path: str,
    size_mb: float | None = None,
    note: str = "",
    log_dir: str = "logs",
) -> None:
    """
    Append one line to logs/files.log.

    Format:
      2026-04-14 14:31  CREATE   output/youtube_60min/paz/paz_60min.mp4  1820 MB
      2026-04-14 14:31  CLEAN    output/youtube_60min/paz/paz_60min_work/ 320 MB freed
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "files.log")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    size_str = f"  {size_mb:.0f} MB" if size_mb is not None else ""
    note_str = f"  — {note}" if note else ""
    rel = os.path.relpath(path) if os.path.isabs(path) else path
    line = f"{ts}  {event:<8} {rel}{size_str}{note_str}\n"
    with open(log_path, "a") as f:
        f.write(line)


def clean_dir(path: str, label: str = "", log_dir: str = "logs") -> float:
    """
    Delete a directory tree, log the event, return MB freed.
    Safe no-op if path doesn't exist.
    """
    if not os.path.exists(path):
        return 0.0
    size_mb = _dir_size_mb(path)
    shutil.rmtree(path)
    log_file_event("CLEAN", path, size_mb,
                   note=label or "temp dir removed", log_dir=log_dir)
    return size_mb


def clean_file(path: str, label: str = "", log_dir: str = "logs") -> float:
    """
    Delete a single file, log the event, return MB freed.
    Safe no-op if file doesn't exist.
    """
    if not os.path.exists(path):
        return 0.0
    size_mb = os.path.getsize(path) / 1024 / 1024
    os.remove(path)
    log_file_event("CLEAN", path, size_mb,
                   note=label or "removed", log_dir=log_dir)
    return size_mb


def _dir_size_mb(path: str) -> float:
    total = 0
    for dirpath, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    return total / 1024 / 1024


# ─── Engine version ────────────────────────────────────────────────────────────
# Bump MANUALLY when you change a setting that meaningfully affects output quality.
# Patch auto-tracks git commit hash.
ENGINE_MAJOR = "v3"
ENGINE_MINOR = "2"  # bump for each intentional quality change


def _git_short_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=3,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def engine_version() -> str:
    return f"{ENGINE_MAJOR}.{ENGINE_MINOR}-{_git_short_hash()}"


# ─── Verdict helpers ──────────────────────────────────────────────────────────

def _speed_verdict(render_sec: float, video_minutes: int) -> str:
    ratio = (video_minutes * 60) / max(render_sec, 1)
    label = f"{ratio:.0f}× tiempo real"
    if render_sec < 5 * 60:
        return f"🚀 Excelente — {render_sec/60:.1f}min render ({label})"
    if render_sec < 10 * 60:
        return f"✅ OK — {render_sec/60:.1f}min render ({label})"
    if render_sec < 20 * 60:
        return f"⚠️  Lento — {render_sec/60:.0f}min render ({label})"
    return f"🔴 Muy lento — {render_sec/60:.0f}min render — revisar workers/fps"


def _size_verdict(size_mb: float, video_minutes: int) -> str:
    mb_per_min = size_mb / max(video_minutes, 1)
    if 20 <= mb_per_min <= 40:
        return f"✅ Tamaño esperado — {size_mb:.0f}MB ({mb_per_min:.0f}MB/min)"
    if mb_per_min < 20:
        return f"⚠️  Archivo pequeño — {size_mb:.0f}MB ({mb_per_min:.0f}MB/min) — revisar bitrate"
    return f"⚠️  Archivo grande — {size_mb:.0f}MB ({mb_per_min:.0f}MB/min) — considera bajar bitrate"


def _verse_verdict(unique: int, total: int) -> str:
    cycle_ratio = total / max(unique, 1)
    if cycle_ratio <= 2:
        return f"✅ Variedad alta — {unique} únicos / {total} total (ciclo {cycle_ratio:.1f}×)"
    if cycle_ratio <= 5:
        return f"ℹ️  Variedad media — {unique} únicos / {total} total (ciclo {cycle_ratio:.1f}×)"
    return f"⚠️  Alta repetición — {unique} únicos / {total} total (ciclo {cycle_ratio:.1f}×) — agregar más versos"


def _bg_verdict(bg_count: int) -> str:
    if bg_count >= 10:
        return f"✅ Visual rico — {bg_count} fondos"
    if bg_count >= 6:
        return f"✅ Visual adecuado — {bg_count} fondos"
    if bg_count >= 3:
        return f"⚠️  Poca variedad visual — {bg_count} fondos — agregar más pinturas"
    return f"🔴 Muy pocos fondos — {bg_count} — agregar pinturas al pool"


def _audio_verdict(moods: list[str]) -> str:
    n = len(moods)
    if n >= 3:
        return f"✅ Audio variado — {n} moods: {', '.join(moods)}"
    if n == 2:
        return f"✅ Audio variado — {n} moods: {', '.join(moods)}"
    return f"⚠️  Audio monotono — 1 mood: {moods[0]} — usa al menos 2 moods"


# ─── RenderLogger ─────────────────────────────────────────────────────────────

class RenderLogger:
    """
    Tracks one render from start to finish.

    Usage:
        logger = RenderLogger(theme="paz", config={...})
        logger.start()
        # ... render ...
        logger.end(output_path="/path/to/paz_60min.mp4", elapsed_sec=242)
    """

    def __init__(
        self,
        theme: str,
        config: dict[str, Any],
        log_dir: str = "logs",
    ):
        self.theme = theme
        self.config = config
        self.log_dir = log_dir
        self.renders_dir = os.path.join(log_dir, "renders")
        self.start_ts: float = 0.0
        self.version = engine_version()

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.log_path = os.path.join(self.renders_dir, f"{ts}_{theme}.md")

    # ── public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        os.makedirs(self.renders_dir, exist_ok=True)
        self.start_ts = time.time()
        started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c = self.config
        moods_str = " + ".join(c.get("moods", []))
        bg_count = len(c.get("background_images", []))

        lines = [
            f"# {self.theme.upper()} — {started_at} — {self.version}",
            "",
            "## Config",
            f"- Engine: `{self.version}`",
            f"- FPS: {c.get('fps', '?')}",
            f"- Segundos/verso: {c.get('seconds_per_verse', '?')}",
            f"- Duración objetivo: {c.get('duration_min', '?')} min",
            f"- Fondos: {bg_count} pinturas",
            f"- Audio moods: {moods_str or '?'}",
            f"- Watermark: {c.get('watermark', '?')}",
            f"- Workers: {c.get('workers', '?')}",
            f"- Text style: {c.get('text_style', '?')}",
            "",
            "## Estado",
            f"- Iniciado: {started_at}",
            "- Completado: _(en progreso)_",
            "",
        ]
        with open(self.log_path, "w") as f:
            f.write("\n".join(lines))

        print(f"  [log] {self.log_path}")

    def end(
        self,
        output_path: str,
        elapsed_sec: float,
        unique_verses: int = 0,
        total_verses: int = 0,
        error: str | None = None,
    ) -> None:
        ended_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = self.config
        duration_min = c.get("duration_min", 60)
        moods = c.get("moods", [])
        bg_count = len(c.get("background_images", []))

        if error:
            self._append_error(ended_at, error)
            return

        size_mb = os.path.getsize(output_path) / 1024 / 1024 if os.path.exists(output_path) else 0

        verdict_lines = [
            _speed_verdict(elapsed_sec, duration_min),
            _size_verdict(size_mb, duration_min),
            _verse_verdict(unique_verses, total_verses),
            _bg_verdict(bg_count),
            _audio_verdict(moods),
        ]

        lines = [
            f"## Métricas",
            f"- Completado: {ended_at}",
            f"- Render duration: **{elapsed_sec/60:.1f} min**",
            f"- Tamaño: **{size_mb:.0f} MB**",
            f"- Output: `{output_path}`",
            "",
            "## Veredicto automático",
        ]
        lines += [f"- {v}" for v in verdict_lines]
        lines += [
            "",
            "## Mejoras para próxima iteración",
            "> Después de ver el video, completa estas secciones:",
            ">",
            "> **¿Qué funcionó bien?**",
            "> (texto, fondos, música, ritmo visual...)",
            ">",
            "> **¿Qué mejorar?**",
            "> (texto muy pequeño, fondos repetitivos, música muy corta, etc.)",
            ">",
            "> **Ajustes de settings para próxima versión:**",
            "> - fps: _sin cambios / subir a X / bajar a X_",
            "> - segundos/verso: _sin cambios / cambiar a X_",
            "> - bitrate: _sin cambios / subir / bajar_",
            "> - fondos: _agregar / quitar_",
            "> - notas audio: ...",
            "",
        ]

        with open(self.log_path, "a") as f:
            f.write("\n".join(lines))

        # Log file creation event
        log_file_event("CREATE", output_path, size_mb, log_dir=self.log_dir)

        # Update LEARNINGS.md index line
        self._append_to_learnings_index(ended_at, elapsed_sec, size_mb, output_path)

        print(f"  [log] Veredicto guardado → {self.log_path}")

    # ── internal helpers ──────────────────────────────────────────────────────

    def _append_error(self, ts: str, error: str) -> None:
        with open(self.log_path, "a") as f:
            f.write(f"\n## ERROR — {ts}\n```\n{error}\n```\n")

    def _append_to_learnings_index(
        self, ts: str, elapsed_sec: float, size_mb: float, output_path: str
    ) -> None:
        learnings_path = os.path.join(self.log_dir, "LEARNINGS.md")
        rel_log = os.path.relpath(self.log_path, self.log_dir)
        render_min = elapsed_sec / 60
        duration_min = self.config.get("duration_min", 60)
        moods = " + ".join(self.config.get("moods", []))

        line = (
            f"| {ts[:10]} | {self.theme} | {self.version} | "
            f"{render_min:.1f}min render | {size_mb:.0f}MB | "
            f"{duration_min}min video | {moods} | "
            f"[log]({rel_log}) |\n"
        )

        if not os.path.exists(learnings_path):
            _create_learnings_file(learnings_path)

        # Append row to the renders table
        with open(learnings_path, "r") as f:
            content = f.read()

        marker = "<!-- renders-table-end -->"
        if marker in content:
            content = content.replace(marker, line + marker)
        else:
            content += line

        with open(learnings_path, "w") as f:
            f.write(content)


# ─── Initial LEARNINGS.md ─────────────────────────────────────────────────────

def _create_learnings_file(path: str) -> None:
    """Bootstrap LEARNINGS.md with Sprint 3 accumulated knowledge."""
    content = """\
# Loop Video Maker — Learnings

Registro acumulativo de aprendizajes por iteración.
Después de cada render, revisar el log y mover las mejores lecciones aquí.

---

## Historial de renders

| Fecha | Tema | Engine | Render | Tamaño | Duración | Moods | Log |
|-------|------|--------|--------|--------|----------|-------|-----|
<!-- renders-table-end -->

---

## Lecciones por versión

### v3.x — ffmpeg fast renderer (Sprint 3, 2026-04)

**Performance**
- MoviePy frame-by-frame = 3h por video de 60min. ffmpeg zoompan = 4min. Nunca volver a MoviePy para videos largos.
- `ThreadPoolExecutor(max_workers=6)` para clips en paralelo es seguro y efectivo en M-series Mac.
- 12fps es imperceptible para slow Ken Burns pans; reduce el frame count a la mitad.
- Config óptima 60min: 20s/verso × 180 versos, 12fps, 3500k bitrate → ~1.7GB, ~4min render.

**ffmpeg filter bugs**
- `fade=alpha=1` sobre text overlay DESPUÉS de zoompan → texto invisible (timestamp drift).
  Fix: aplicar fade al composite completo: `[bg][txt]overlay,fade=in,fade=out[out]`
- `format=rgba` funciona para overlay con fondo zoompan. `format=yuva420p` pierde el alpha.

**Borders / imágenes**
- `_autocrop_borders(threshold=8)`: std de columna border ≈ 0, columna contenido ≈ 10-100.
  Threshold 240 (error previo) hacía que nada se detectara como borde.
- Siempre usar `ImageOps.fit` (crop-to-fill) después de autocrop para evitar letterboxing.

**Audio**
- `generate_playlist()` con 3 moods + 8s crossfade elimina la monotonía de 60min con un solo loop.
- Tracks Kevin MacLeod CC-BY disponibles: paz_profunda, adoracion, meditacion, devocion, sanacion, esperanza.

**Texto**
- Stroke de referencia: offsets (-3,0),(3,0),(0,-3),(0,3) + alpha 240 mejora legibilidad en fondos claros.
- Fuente Cormorant Garamond Italic da el estilo devocional correcto.

---

## Ideas pendientes

- [ ] Descargar pinturas sin bordes de museo (versiones de alta resolución)
- [ ] Probar 15fps para ver si mejora la fluidez perceptible
- [ ] Agregar fade de audio al inicio/fin del video
- [ ] Template de descripción YouTube con crédito Kevin MacLeod
- [ ] Considerar texto animado (fade in letra por letra) para engagement
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
