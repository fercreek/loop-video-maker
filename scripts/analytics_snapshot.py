"""
scripts/analytics_snapshot.py — Guarda snapshot de analytics a logs/analytics/.

Corre automáticamente vía cron. Genera JSON + resumen legible.
Compara vs snapshot anterior si existe.

Uso:
    python3 scripts/analytics_snapshot.py
    python3 scripts/analytics_snapshot.py --label "post_paz_24h"
"""
from __future__ import annotations

import sys
import os
import json
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "logs", "analytics")


def load_latest_snapshot() -> dict | None:
    if not os.path.exists(LOGS_DIR):
        return None
    files = sorted([f for f in os.listdir(LOGS_DIR) if f.endswith(".json")])
    if not files:
        return None
    with open(os.path.join(LOGS_DIR, files[-1])) as f:
        return json.load(f)


def delta(new: int | float, old: int | float) -> str:
    d = new - old
    sign = "+" if d >= 0 else ""
    return f"{sign}{d:,.0f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="", help="Etiqueta para el snapshot (ej: post_paz_24h)")
    ap.add_argument("--days", type=int, default=7, help="Período analytics en días (default: 7)")
    args = ap.parse_args()

    try:
        from core.youtube_client import (
            get_channel_summary,
            get_channel_analytics,
            get_channel_videos,
        )
    except Exception as e:
        print(f"[snapshot] Import error: {e}")
        sys.exit(1)

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d_%H-%M")
    label = f"_{args.label}" if args.label else ""
    filename = f"{ts}{label}.json"

    os.makedirs(LOGS_DIR, exist_ok=True)

    print(f"[snapshot] Capturando analytics ({args.days}d)...")

    try:
        summary  = get_channel_summary()
        analytics = get_channel_analytics(days=args.days)
        videos   = get_channel_videos(max_results=20)
    except Exception as e:
        print(f"[snapshot] ERROR: {e}")
        sys.exit(1)

    snapshot = {
        "timestamp":     now.isoformat(),
        "label":         args.label,
        "period_days":   args.days,
        "channel": {
            "subscribers":  summary["subscribers"],
            "total_views":  summary["total_views"],
            "video_count":  summary["video_count"],
        },
        "period": {
            "total_views":       analytics["total_views"],
            "total_watch_hours": analytics["total_watch_hours"],
        },
        "top_videos": [
            {
                "title":                v["title"][:60],
                "video_id":             v["video_id"],
                "views":                v.get("analytics", {}).get("views", 0),
                "watch_time_hours":     v.get("analytics", {}).get("watch_time_hours", 0),
                "avg_view_pct":         v.get("analytics", {}).get("avg_view_pct", 0),
                "subscribers_gained":   v.get("analytics", {}).get("subscribers_gained", 0),
            }
            for v in videos[:10]
            if v.get("analytics")
        ],
    }

    path = os.path.join(LOGS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    # ── Print summary ──────────────────────────────────────────────
    prev = load_latest_snapshot()
    print(f"\n{'─'*55}")
    print(f"  SNAPSHOT {ts}{label}")
    print(f"{'─'*55}")
    print(f"  Suscriptores:    {summary['subscribers']:,}", end="")
    if prev:
        print(f"  ({delta(summary['subscribers'], prev['channel']['subscribers'])})", end="")
    print()
    print(f"  Vistas/{args.days}d:     {analytics['total_views']:,}", end="")
    if prev:
        print(f"  ({delta(analytics['total_views'], prev['period']['total_views'])})", end="")
    print()
    print(f"  Watch time/{args.days}d:  {analytics['total_watch_hours']:.0f}h", end="")
    if prev:
        diff_wt = analytics['total_watch_hours'] - prev['period']['total_watch_hours']
        print(f"  ({'+' if diff_wt>=0 else ''}{diff_wt:.0f}h)", end="")
    print()
    print()
    print(f"  Top 5 videos ({args.days}d):")
    for v in snapshot["top_videos"][:5]:
        ret = f"{v['avg_view_pct']:.0f}%" if v['avg_view_pct'] else "—"
        print(f"    {v['views']:>6} vistas  {ret:>5} ret  {v['title'][:45]}")
    print(f"\n  Guardado: {path}")
    print(f"{'─'*55}")


if __name__ == "__main__":
    main()
