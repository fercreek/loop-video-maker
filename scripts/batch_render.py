"""
scripts/batch_render.py — Batch render del catálogo de historias bíblicas.

Itera el catálogo, salta historias ya renderizadas, maneja fallos sin abortar.
Concurrencia=1 (Gemini quota + GPU contention saturan single render).

Logs en `logs/batch_YYYY-MM-DD.jsonl` para análisis post-batch.

Uso:
    # Renderizar las próximas 3 (test pre-scale)
    python3 scripts/batch_render.py --max 3

    # Renderizar las próximas 10 con prioridad alta
    python3 scripts/batch_render.py --max 10 --priority 1

    # Dry run — solo lista qué se renderizaría
    python3 scripts/batch_render.py --max 5 --dry-run

    # Renderizar TODAS las pendientes (overnight batch)
    python3 scripts/batch_render.py --max 100
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR  = Path(__file__).parent.parent
CATALOG_PATH = PROJECT_DIR / "data" / "video_catalog.json"
LOGS_DIR     = PROJECT_DIR / "logs"
RENDER_TIMEOUT_SEC = 1500   # 25 min hard cap por video


def load_catalog() -> dict:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_catalog(data: dict) -> None:
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_pending_videos(catalog: dict, max_priority: int = 3, require_script: bool = True) -> list[dict]:
    """
    Retorna videos sin renderizar pero CON script JSON existente, ordenados por prioridad.
    Si require_script=False, incluye también los que necesitan generar script.
    """
    videos = catalog.get("videos", catalog) if isinstance(catalog, dict) else catalog
    stories_dir = PROJECT_DIR / "data" / "stories"
    pending = []
    for v in videos:
        status = v.get("status", {})
        if status.get("rendered"):
            continue
        if v.get("priority", 3) > max_priority:
            continue
        # Solo incluir si script existe (evita rendererar sin JSON)
        if require_script and not (stories_dir / f"{v['id']}.json").exists():
            continue
        pending.append(v)
    pending.sort(key=lambda v: (v.get("priority", 3), v.get("id", "")))
    return pending


def mark_rendered(video_id: str) -> None:
    """Marca video como rendered en el catálogo."""
    catalog = load_catalog()
    videos = catalog.get("videos", catalog) if isinstance(catalog, dict) else catalog
    for v in videos:
        if v["id"] == video_id:
            v.setdefault("status", {})["rendered"] = True
            v["status"]["rendered_at"] = datetime.now(timezone.utc).isoformat()
            break
    save_catalog(catalog)


def log_event(event: dict) -> None:
    """Append-only log JSONL en logs/batch_YYYY-MM-DD.jsonl."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"batch_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def render_one(video_id: str, voice: str = "jorge") -> tuple[bool, float, str]:
    """
    Invoca render_story.py como subprocess. Retorna (ok, elapsed_sec, msg).
    Timeout duro de 25 min — si excede, mata el proceso.
    """
    cmd = [
        ".venv/bin/python3", "render_story.py",
        "--story", video_id,
        "--voice", voice,
    ]
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_DIR),
            capture_output=True, text=True,
            timeout=RENDER_TIMEOUT_SEC,
        )
        elapsed = time.time() - t0
        if result.returncode == 0:
            return True, elapsed, "ok"
        return False, elapsed, f"exit={result.returncode}: {result.stderr[-300:]}"
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return False, elapsed, f"TIMEOUT after {RENDER_TIMEOUT_SEC}s"
    except Exception as e:
        elapsed = time.time() - t0
        return False, elapsed, f"exception: {e}"


def main():
    parser = argparse.ArgumentParser(description="Batch render del catálogo")
    parser.add_argument("--max", type=int, default=3, help="Máximo videos a renderizar")
    parser.add_argument("--priority", type=int, default=3, help="Prioridad máxima (1=más alta)")
    parser.add_argument("--voice", default="jorge", help="Voz Edge TTS")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar, no renderizar")
    args = parser.parse_args()

    catalog = load_catalog()
    pending = get_pending_videos(catalog, max_priority=args.priority)

    if not pending:
        print("✓ No hay videos pendientes con esa prioridad.")
        return

    to_render = pending[:args.max]

    print(f"\n{'='*65}")
    print(f"  BATCH RENDER — {len(to_render)} videos pendientes (de {len(pending)})")
    print(f"{'='*65}")
    for i, v in enumerate(to_render, 1):
        print(f"  {i:2d}. [{v['id']:<35s}] {v['title'][:40]} (P{v.get('priority', 3)})")
    print()

    if args.dry_run:
        print("[DRY RUN] No se renderizó nada. Quita --dry-run para ejecutar.")
        return

    # Confirmar si son muchos
    if len(to_render) >= 10:
        resp = input(f"\n¿Renderizar {len(to_render)} videos? Tiempo estimado: ~{len(to_render)*5} min. (y/N) ")
        if resp.lower() != "y":
            print("Cancelado.")
            return

    results: list[dict] = []
    start = time.time()

    for i, v in enumerate(to_render, 1):
        vid = v["id"]
        print(f"\n[{i}/{len(to_render)}] Renderizando: {vid} — {v['title'][:50]}")
        ok, elapsed, msg = render_one(vid, voice=args.voice)
        result = {
            "id": vid,
            "title": v["title"],
            "ok": ok,
            "elapsed_sec": round(elapsed, 1),
            "msg": msg,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        results.append(result)
        log_event({"event": "render_complete", **result})

        if ok:
            mark_rendered(vid)
            print(f"  ✓ OK ({elapsed:.1f}s) — marcado rendered en catálogo")
        else:
            print(f"  ✗ FALLO ({elapsed:.1f}s) — {msg}")

    total_elapsed = time.time() - start
    ok_count = sum(1 for r in results if r["ok"])
    fail_count = len(results) - ok_count

    print(f"\n{'='*65}")
    print(f"  BATCH COMPLETO — {total_elapsed/60:.1f} min total")
    print(f"  Éxitos: {ok_count} · Fallos: {fail_count}")
    print(f"{'='*65}")

    if fail_count:
        print("\n  Fallos:")
        for r in results:
            if not r["ok"]:
                print(f"    {r['id']:<35s} → {r['msg'][:60]}")

    log_event({
        "event": "batch_complete",
        "total_videos": len(results),
        "ok": ok_count,
        "failed": fail_count,
        "total_elapsed_sec": round(total_elapsed, 1),
        "ts": datetime.now(timezone.utc).isoformat(),
    })


if __name__ == "__main__":
    main()
