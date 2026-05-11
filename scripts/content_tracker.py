"""
scripts/content_tracker.py — Sistema de tracking de contenido spec-driven.

Permite:
  1. Registrar nuevo contenido con su spec completo
  2. Actualizar métricas desde YouTube API
  3. Comparar performance entre sesiones y semanas
  4. Identificar qué specs generan mejores resultados (reproducibilidad)

Uso:
    # Ver resumen del registry
    python3 scripts/content_tracker.py --summary

    # Actualizar métricas de YouTube (requiere token válido)
    python3 scripts/content_tracker.py --pull-metrics

    # Reporte comparativo entre semanas
    python3 scripts/content_tracker.py --report

    # Ver qué spec tuvo mejor performance
    python3 scripts/content_tracker.py --best

    # Log de sesión actual
    python3 scripts/content_tracker.py --session 2026-05-11
"""
from __future__ import annotations

import argparse
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT_DIR      = Path(__file__).parent.parent
REGISTRY_PATH    = PROJECT_DIR / "data" / "content_registry.json"
SESSION_LOG_PATH = PROJECT_DIR / "logs" / "sessions"
TOKEN_PATH       = PROJECT_DIR / "data" / "yt_token.json"


# ─── Registry helpers ─────────────────────────────────────────────────────────

def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {"version": "1.0", "created": today(), "content": []}
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_registry(data: dict) -> None:
    data["updated"] = today()
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ─── Summary ──────────────────────────────────────────────────────────────────

def cmd_summary(args) -> None:
    reg = load_registry()
    content = reg.get("content", [])

    by_session: dict[str, list] = {}
    for c in content:
        s = c.get("session", "unknown")
        by_session.setdefault(s, []).append(c)

    print(f"\n{'='*70}")
    print(f"  CONTENT REGISTRY — {len(content)} piezas")
    print(f"  Long-form: {sum(1 for x in content if x['type']=='long_form')}")
    print(f"  Shorts:    {sum(1 for x in content if x['type']=='short')}")
    print(f"{'='*70}\n")

    for session_date in sorted(by_session.keys(), reverse=True):
        items = by_session[session_date]
        uploaded = [x for x in items if x.get("upload", {}).get("video_id")]
        print(f"  📅 Sesión {session_date} — {len(items)} piezas ({len(uploaded)} subidas)")
        for item in items:
            uid  = item.get("upload", {}).get("video_id", "—")
            m1   = item.get("metrics", {}).get("week_1")
            views = f"{m1['views']:,}" if m1 and m1.get("views") else "sin datos"
            t = item["type"].replace("long_form", "📹").replace("short", "🎬")
            print(f"    {t} {item['id']:<35s} YT:{uid:<15s} W1:{views}")
    print()


# ─── Pull metrics from YouTube API ────────────────────────────────────────────

def cmd_pull_metrics(args) -> None:
    """Actualiza métricas de YouTube para todo el contenido subido."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("⚠ google-api-python-client no instalado.")
        return

    if not TOKEN_PATH.exists():
        print("⚠ Token no existe. Run: python3 scripts/yt_auth.py")
        return

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())

    yt = build("youtube", "v3", credentials=creds)

    reg = load_registry()
    content = reg.get("content", [])

    # Recopilar IDs con video_id de YouTube
    to_update = [
        c for c in content
        if c.get("upload", {}).get("video_id") and c["upload"]["video_id"] != "dry-run-id"
    ]

    if not to_update:
        print("No hay contenido con video_id de YouTube.")
        return

    video_ids = [c["upload"]["video_id"] for c in to_update]

    print(f"Actualizando métricas de {len(video_ids)} videos...")

    # YouTube API: chunks de 50
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        resp = yt.videos().list(
            part="statistics,contentDetails",
            id=",".join(chunk)
        ).execute()

        stats_map = {item["id"]: item for item in resp.get("items", [])}

        for c in to_update:
            vid = c["upload"]["video_id"]
            if vid not in stats_map:
                continue

            item = stats_map[vid]
            stats = item.get("statistics", {})
            duration_str = item.get("contentDetails", {}).get("duration", "")

            # Determinar qué semana es (días desde upload)
            upload_date = c.get("upload", {}).get("upload_date")
            if upload_date:
                delta_days = (datetime.now() - datetime.strptime(upload_date, "%Y-%m-%d")).days
            else:
                delta_days = 0

            metric_entry = {
                "pulled_at": today(),
                "days_since_upload": delta_days,
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "favorites": int(stats.get("favoriteCount", 0)),
            }

            metrics = c.setdefault("metrics", {})
            if delta_days <= 7:
                metrics["week_1"] = metric_entry
            elif delta_days <= 14:
                metrics["week_2"] = metric_entry
            elif delta_days <= 28:
                metrics["week_4"] = metric_entry
            else:
                metrics[f"day_{delta_days}"] = metric_entry

            v = metric_entry["views"]
            print(f"  ✓ {c['id']:<35s} {v:>8,} views | {metric_entry['likes']:>6,} likes")

    save_registry(reg)
    print(f"\n✓ Métricas guardadas en {REGISTRY_PATH}")


# ─── Report comparativo ───────────────────────────────────────────────────────

def cmd_report(args) -> None:
    """Compara performance entre sesiones y tipos de contenido."""
    reg = load_registry()
    content = reg.get("content", [])

    with_metrics = [c for c in content if c.get("metrics", {}).get("week_1")]

    if not with_metrics:
        print("No hay métricas de semana 1 aún. Run: --pull-metrics")
        return

    print(f"\n{'='*70}")
    print(f"  PERFORMANCE REPORT")
    print(f"{'='*70}\n")

    # Por tipo
    for tipo in ["long_form", "short"]:
        items = [c for c in with_metrics if c["type"] == tipo]
        if not items:
            continue
        avg_views = sum(c["metrics"]["week_1"]["views"] for c in items) / len(items)
        top = max(items, key=lambda c: c["metrics"]["week_1"]["views"])
        print(f"  {'📹 Long-form' if tipo=='long_form' else '🎬 Shorts'}")
        print(f"    Promedio views W1: {avg_views:,.0f}")
        print(f"    Top performer:     {top['id']} → {top['metrics']['week_1']['views']:,} views")
        print(f"    Spec del top:")
        for k, v in top.get("spec", {}).items():
            print(f"      {k}: {v}")
        print()

    # Top 5 global
    sorted_content = sorted(with_metrics, key=lambda c: c["metrics"]["week_1"]["views"], reverse=True)
    print(f"  TOP 5 GLOBAL (semana 1):")
    for i, c in enumerate(sorted_content[:5], 1):
        v = c["metrics"]["week_1"]["views"]
        print(f"    {i}. {c['id']:<35s} {v:>8,} views [{c['type']}]")


# ─── Best spec finder ─────────────────────────────────────────────────────────

def cmd_best(args) -> None:
    """Identifica qué parámetros de spec correlacionan con mayor performance."""
    reg = load_registry()
    content = [c for c in reg.get("content", []) if c.get("metrics", {}).get("week_1")]

    if not content:
        print("No hay métricas aún. Run: --pull-metrics")
        return

    print(f"\n{'='*70}")
    print(f"  BEST SPEC ANALYSIS — Parámetros que más correlacionan con views")
    print(f"{'='*70}\n")

    # Analizar por campo de spec
    spec_performance: dict[str, dict[str, list]] = {}
    for c in content:
        views = c["metrics"]["week_1"]["views"]
        for k, v in c.get("spec", {}).items():
            val = str(v)
            spec_performance.setdefault(k, {}).setdefault(val, []).append(views)

    for field, values in spec_performance.items():
        if len(values) <= 1:
            continue
        print(f"  Campo: {field}")
        for val, views_list in sorted(values.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
            avg = sum(views_list) / len(views_list)
            print(f"    {val:<40s} avg: {avg:>8,.0f} views (n={len(views_list)})")
        print()


# ─── Session log ──────────────────────────────────────────────────────────────

def cmd_session(args) -> None:
    """Muestra o crea log de una sesión específica."""
    session_date = args.session or today()
    reg = load_registry()
    session_items = [c for c in reg.get("content", []) if c.get("session") == session_date]

    print(f"\n  SESIÓN {session_date} — {len(session_items)} piezas generadas\n")

    for c in session_items:
        tipo = "📹 Long-form" if c["type"] == "long_form" else "🎬 Short"
        vid = c.get("upload", {}).get("video_id", "no subido")
        print(f"  {tipo} | {c['id']}")
        print(f"    Título: {c.get('title', '')[:60]}")
        print(f"    YouTube: {vid}")
        spec = c.get("spec", {})
        print(f"    Spec: voice={spec.get('voice','-')} | version={spec.get('version','-')} | hook={str(spec.get('hook',''))[:40]}")
        print()


# ─── Register new content ─────────────────────────────────────────────────────

def cmd_register(args) -> None:
    """Registra una nueva pieza de contenido en el registry."""
    reg = load_registry()
    content_id = input("ID del contenido: ").strip()
    tipo = input("Tipo (long_form/short): ").strip()
    title = input("Título: ").strip()

    entry = {
        "id": content_id,
        "type": tipo,
        "session": today(),
        "title": title,
        "spec": {},
        "upload": {"platform": None, "video_id": None, "upload_date": None},
        "metrics": {"week_1": None, "week_2": None, "week_4": None},
    }
    reg["content"].append(entry)
    save_registry(reg)
    print(f"✓ Registrado: {content_id}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Content tracker — spec-driven development")
    parser.add_argument("--summary",      action="store_true", help="Resumen del registry")
    parser.add_argument("--pull-metrics", action="store_true", help="Actualizar métricas desde YouTube")
    parser.add_argument("--report",       action="store_true", help="Reporte comparativo de performance")
    parser.add_argument("--best",         action="store_true", help="Análisis de specs ganadores")
    parser.add_argument("--session",      metavar="DATE",      help="Log de sesión (YYYY-MM-DD)")
    parser.add_argument("--register",     action="store_true", help="Registrar nueva pieza")
    args = parser.parse_args()

    if args.summary:      cmd_summary(args)
    elif args.pull_metrics: cmd_pull_metrics(args)
    elif args.report:     cmd_report(args)
    elif args.best:       cmd_best(args)
    elif args.session:    cmd_session(args)
    elif args.register:   cmd_register(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
