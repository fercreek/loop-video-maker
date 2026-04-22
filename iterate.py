"""
iterate.py — Loop de mejora gradual por batches de 5 videos.

Workflow por iter:
1. Lee último iter_*.md para conocer estado previo
2. Renderiza próximos 5 temas (rotación)
3. Eval automático
4. Agrupa issues, identifica patrón dominante
5. Genera iter_NN_<date>.md con análisis
6. (Humano aplica fix manual o aprueba auto-fix de hipótesis comunes)

Uso:
    .venv/bin/python3 iterate.py             # próximo iter
    .venv/bin/python3 iterate.py --status    # estado actual sin renderizar
    .venv/bin/python3 iterate.py --themes amor paz fe ...  # batch custom
"""
from __future__ import annotations

import os
import sys
import json
import glob
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, ".")

from config import THEME_MOODS, THEME_LABELS, BATCH_SIZE, ALL_THEMES as _CONFIG_THEMES, OUTPUT_BASE_60MIN

# Rotación alfabética estable (histórica) — ver iterations/iter_01.md
ALL_THEMES = sorted(_CONFIG_THEMES)

ITER_DIR = "iterations"
EVAL_DIR = "eval"


def get_last_iter() -> tuple[int, dict | None]:
    """Return (next_iter_num, last_iter_metadata)."""
    iters = sorted(glob.glob(os.path.join(ITER_DIR, "iter_[0-9]*.md")))
    if not iters:
        return 1, None
    last = iters[-1]
    num = int(Path(last).stem.split("_")[1])
    meta = parse_iter(last)
    return num + 1, meta


def parse_iter(path: str) -> dict:
    """Extract minimal metadata from iter doc."""
    with open(path) as f:
        text = f.read()
    meta = {"path": path, "raw": text}
    for line in text.splitlines():
        if line.startswith("**Versión salida:**"):
            meta["output_version"] = line.split("`")[1] if "`" in line else None
        elif line.startswith("**Score promedio batch:**"):
            try:
                meta["score"] = int(line.split(":")[1].strip().split("/")[0])
            except Exception:
                pass
        elif line.startswith("# Iter "):
            meta["title"] = line[2:].strip()
    return meta


def pick_next_themes(prev_themes: list[str] | None) -> list[str]:
    """Rotate through themes."""
    if not prev_themes:
        return ALL_THEMES[:BATCH_SIZE]
    last_idx = ALL_THEMES.index(prev_themes[-1]) if prev_themes[-1] in ALL_THEMES else -1
    start = (last_idx + 1) % len(ALL_THEMES)
    return [ALL_THEMES[(start + i) % len(ALL_THEMES)] for i in range(BATCH_SIZE)]


def render_batch(themes: list[str]) -> list[dict]:
    """Render the 5 videos. Skip if already exists. Return per-video render info."""
    from render_60min import render_video
    info = []
    for theme in themes:
        # Force re-render: delete existing
        out_path = f"{OUTPUT_BASE_60MIN}/{theme}/{theme}_60min.mp4"
        existed = os.path.exists(out_path)
        if existed:
            os.remove(out_path)
        t0 = time.time()
        moods = THEME_MOODS[theme]
        label = THEME_LABELS[theme]
        try:
            path = render_video(theme, moods, label)
            info.append({
                "theme": theme,
                "path": path,
                "render_sec": time.time() - t0,
                "moods": moods,
                "ok": True,
            })
        except Exception as e:
            info.append({
                "theme": theme,
                "render_sec": time.time() - t0,
                "moods": moods,
                "ok": False,
                "error": str(e),
            })
    return info


def eval_batch(themes: list[str]) -> list[dict]:
    """Run eval_render on each video, return parsed results."""
    from eval_render import evaluate_video, write_json, append_summary
    results = []
    for theme in themes:
        path = f"{OUTPUT_BASE_60MIN}/{theme}/{theme}_60min.mp4"
        if not os.path.exists(path):
            continue
        try:
            r = evaluate_video(path)
            write_json(r)
            results.append(r)
        except Exception as e:
            print(f"  eval error {theme}: {e}")
    if results:
        append_summary(results)
    return results


def cluster_issues(results: list[dict]) -> dict:
    """Find dominant failure patterns."""
    issue_counter = Counter()
    issue_examples = defaultdict(list)
    for r in results:
        for iss in r["issues"]:
            # Normalize: take first 30 chars as key
            key = iss.split(":")[0][:40]
            issue_counter[key] += 1
            issue_examples[key].append((r["theme"], iss))
    return {"counts": dict(issue_counter), "examples": dict(issue_examples)}


def hypothesize_root_cause(clusters: dict, results: list[dict]) -> str:
    """Generate hypothesis text from clustered issues."""
    if not clusters["counts"]:
        return "Sin issues detectados. Batch limpio."
    lines = []
    for issue_key, count in sorted(clusters["counts"].items(), key=lambda x: -x[1]):
        examples = clusters["examples"][issue_key][:3]
        lines.append(f"- **{issue_key}** — {count}/{len(results)} videos")
        for theme, iss in examples:
            lines.append(f"  - {theme}: `{iss[:120]}`")
    # Heuristic root cause map
    hints = []
    issues_str = " ".join(clusters["counts"].keys()).lower()
    if "silencio" in issues_str:
        hints.append("→ Audio: revisar `core/music_gen.py` boundaries y final del último loop.")
    if "loudness" in issues_str:
        hints.append("→ Audio: aplicar `loudnorm` post-mux o mejorar normalización en playlist gen.")
    if "thumbnail" in issues_str:
        hints.append("→ Thumb pipeline: integrar generate_thumbnail en render_60min.py si falta.")
    if "duración" in issues_str.lower() or "duracion" in issues_str:
        hints.append("→ Duración: revisar segundos_por_versiculo × versos vs target.")
    if "bitrate" in issues_str:
        hints.append("→ Encoding: subir bitrate o cambiar preset x264 en core/video_render.py:713.")
    if "fps" in issues_str:
        hints.append("→ Engine: render_fps no respetado, revisar config y -r flag.")
    if not hints:
        hints.append("→ Sin patrón heurístico. Inspección manual requerida.")
    lines.append("\n**Sugerencias:**")
    lines.extend(hints)
    return "\n".join(lines)


def write_iter_doc(num: int, prev_meta: dict | None, themes: list[str],
                   render_info: list[dict], eval_results: list[dict],
                   clusters: dict, hypothesis: str) -> str:
    """Generate iter_NN_<date>.md with all findings."""
    date = datetime.now().strftime("%Y-%m-%d")
    # Get current version tag
    try:
        current_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"], text=True
        ).strip()
    except Exception:
        current_tag = "unknown"
    try:
        current_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        current_commit = "unknown"

    avg_score = sum(r["score"] for r in eval_results) / len(eval_results) if eval_results else 0
    prev_score = prev_meta.get("score", 0) if prev_meta else 0
    delta = avg_score - prev_score

    # Build batch table
    score_by_theme = {r["theme"]: r["score"] for r in eval_results}
    batch_rows = []
    for i, info in enumerate(render_info, 1):
        theme = info["theme"]
        score = score_by_theme.get(theme, "—")
        moods = " + ".join(info["moods"])
        batch_rows.append(
            f"| {i} | {theme} | 60min | {moods} | {info['render_sec']/60:.1f}min | {score} |"
        )

    # Build issues table
    issue_rows = []
    for r in eval_results:
        for iss in r["issues"]:
            sev = "🔴" if "silencio" in iss.lower() or "duración" in iss.lower() else (
                "🟡" if "loudness" in iss.lower() else "🟢")
            issue_rows.append(f"| {r['theme']} | {iss[:80]} | {sev} | score {r['score']} |")
    if not issue_rows:
        issue_rows.append("| — | Sin issues | ✅ | — |")

    out_path = os.path.join(ITER_DIR, f"iter_{num:02d}_{date}.md")
    content = f"""# Iter {num:02d} — auto-generated {date}

**Fecha:** {date}
**Versión entrada:** {prev_meta.get('output_version', '—') if prev_meta else 'baseline'}
**Versión actual (HEAD):** `{current_tag}` ({current_commit})
**Versión salida:** _pendiente — aplicar fix y re-tag_

---

## Batch rendereado ({len(render_info)} videos)

| # | Tema | Duración | Moods | Render time | Score |
|---|------|----------|-------|-------------|-------|
{chr(10).join(batch_rows)}

**Score promedio batch:** {avg_score:.0f}/100
**Score batch anterior:** {prev_score}/100
**Δ:** {'+' if delta >= 0 else ''}{delta:.0f}

---

## Eval — issues detectados

| Video | Issue | Severidad | Score |
|-------|-------|-----------|-------|
{chr(10).join(issue_rows)}

---

## Patrón dominante / Root cause hypothesis

{hypothesis}

---

## Fix aplicado

_PENDIENTE — humano aplica fix basado en hipótesis arriba, luego:_

```bash
git add -A && git commit -m "fix(iterNN): <descripcion>"
git tag v3.X-iterNN-<feature>
# Re-correr este iter para validar:
.venv/bin/python3 iterate.py --themes {' '.join(themes[:1])}
```

---

## Verificación post-fix

_Re-render 1 video para confirmar mejora:_

| Métrica | Antes | Después | Δ |
|---|---|---|---|
| Score | {avg_score:.0f} | _TBD_ | _TBD_ |
| Issues totales | {sum(len(r['issues']) for r in eval_results)} | _TBD_ | _TBD_ |

---

## Lecciones

- _llenar tras fix_

---

## Siguiente iter

**Próximos 5 temas:** {', '.join(pick_next_themes(themes))}
**Hipótesis a probar:** _basada en clusters arriba_
"""
    with open(out_path, "w") as f:
        f.write(content)
    return out_path


def update_index(iter_num: int, iter_path: str, score: float, themes: list[str]):
    index_path = os.path.join(ITER_DIR, "index.md")
    exists = os.path.exists(index_path)
    with open(index_path, "a") as f:
        if not exists:
            f.write("# Iteraciones — Índice\n\n")
            f.write("| Iter | Fecha | Score | Δ | Temas | Doc |\n")
            f.write("|------|-------|-------|---|-------|-----|\n")
        date = datetime.now().strftime("%Y-%m-%d")
        rel = os.path.relpath(iter_path, ITER_DIR)
        f.write(f"| {iter_num:02d} | {date} | {score:.0f} | _TBD_ | {', '.join(themes)} | [doc]({rel}) |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="Mostrar estado sin renderizar")
    ap.add_argument("--themes", nargs="+", help="Temas custom (default: rotación)")
    ap.add_argument("--no-render", action="store_true", help="Skip render, solo eval temas existentes")
    args = ap.parse_args()

    next_num, prev_meta = get_last_iter()
    print(f"\n🔁 Iter {next_num:02d}")
    if prev_meta:
        print(f"   Anterior: {prev_meta.get('title', '?')} (score {prev_meta.get('score', '?')})")

    if args.status:
        print(f"   Próximos temas sugeridos: {pick_next_themes(None)}")
        return

    themes = args.themes or pick_next_themes(None)
    print(f"   Temas batch: {themes}\n")

    if not args.no_render:
        print("📹 Renderizando...")
        render_info = render_batch(themes)
    else:
        render_info = [{"theme": t, "path": f"{OUTPUT_BASE_60MIN}/{t}/{t}_60min.mp4",
                        "render_sec": 0, "moods": THEME_MOODS[t], "ok": True} for t in themes]

    print("\n📊 Evaluando...")
    eval_results = eval_batch(themes)

    print("\n🔍 Clustering issues...")
    clusters = cluster_issues(eval_results)
    hypothesis = hypothesize_root_cause(clusters, eval_results)

    print("\n📝 Escribiendo iter doc...")
    iter_path = write_iter_doc(next_num, prev_meta, themes, render_info,
                                eval_results, clusters, hypothesis)
    avg = sum(r["score"] for r in eval_results) / len(eval_results) if eval_results else 0
    update_index(next_num, iter_path, avg, themes)

    print(f"\n✅ Iter {next_num:02d} listo: {iter_path}")
    print(f"   Score promedio: {avg:.0f}/100")
    print(f"   Issues:\n{hypothesis[:500]}")


if __name__ == "__main__":
    main()
