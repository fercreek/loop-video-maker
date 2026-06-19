#!/usr/bin/env python3
"""
scripts/niche_report.py — Weekly niche performance report.

Reads data/video_daily_log.jsonl (last 7 days by default) and groups
performance by topic_cluster. Outputs:
  - data/niche_performance.json   — structured data for dashboards
  - data/STRATEGY_LOG.md          — human-readable weekly strategy log (prepend)
  - stdout                        — table summary

Designed to run weekly (Sunday 8am MTY via launchd).

    .venv/bin/python3 scripts/niche_report.py [--days N] [--week-label YYYY-Www]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

PROJECT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH       = os.path.join(PROJECT_DIR, "data", "video_daily_log.jsonl")
PERF_PATH      = os.path.join(PROJECT_DIR, "data", "niche_performance.json")
STRATEGY_PATH  = os.path.join(PROJECT_DIR, "data", "STRATEGY_LOG.md")


CLUSTER_LABEL = {
    "historia_clasica":     "Historia Clásica",
    "historia_misterio":    "Historia Misterio",
    "historia_redemption":  "Historia Redemption",
    "tematico":             "Temático",
    "devocional":           "Devocional",
    "devocional_corto":     "Devocional Corto",
    "sleep_salmos":         "Sleep — Salmos",
    "sleep_versos":         "Sleep — Versos",
    "lofi":                 "Lo-Fi Cristiano",
}


def load_log(days: int) -> list[dict]:
    if not os.path.exists(LOG_PATH):
        return []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    rows: list[dict] = []
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("date", "") >= cutoff:
                    rows.append(entry)
            except json.JSONDecodeError:
                pass
    return rows


def aggregate(rows: list[dict]) -> dict[str, dict]:
    by_cluster: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_cluster[row.get("topic_cluster", "unknown")].append(row)

    result: dict[str, dict] = {}
    for cluster, entries in by_cluster.items():
        # Deduplicate: keep highest watch_hours per video_id (in case run multiple times)
        best: dict[str, dict] = {}
        for e in entries:
            vid = e["video_id"]
            if vid not in best or e["watch_hours"] > best[vid]["watch_hours"]:
                best[vid] = e
        unique = list(best.values())

        total_wh     = sum(e["watch_hours"] for e in unique)
        total_views  = sum(e["views"] for e in unique)
        retentions   = [e["avg_retention_pct"] for e in unique if e.get("avg_retention_pct")]
        avg_ret      = round(sum(retentions) / len(retentions), 1) if retentions else 0.0
        avg_wh       = round(total_wh / len(unique), 1) if unique else 0.0
        top          = max(unique, key=lambda e: e["watch_hours"])

        result[cluster] = {
            "cluster":           cluster,
            "label":             CLUSTER_LABEL.get(cluster, cluster),
            "videos_count":      len(unique),
            "total_watch_hours": round(total_wh, 1),
            "avg_watch_hours":   avg_wh,
            "total_views":       total_views,
            "avg_retention_pct": avg_ret,
            "top_video": {
                "video_id":    top["video_id"],
                "title":       top["title"],
                "watch_hours": top["watch_hours"],
            },
        }
    return result


def rank_clusters(agg: dict[str, dict]) -> list[dict]:
    return sorted(agg.values(), key=lambda x: -x["total_watch_hours"])


def build_strategy_entry(ranked: list[dict], week_label: str, days: int) -> str:
    lines: list[str] = []
    lines.append(f"\n## {week_label} — Semana {_week_num()}\n")
    lines.append(f"*Período: últimos {days} días · generado {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    lines.append("\n| Cluster | Avg WH/video | Avg Ret | Total WH | Videos |\n")
    lines.append("|---|---|---|---|---|\n")

    for c in ranked:
        lines.append(
            f"| {c['label']} | {c['avg_watch_hours']:.1f}h"
            f" | {c['avg_retention_pct']:.1f}% | {c['total_watch_hours']:.1f}h"
            f" | {c['videos_count']} |\n"
        )

    # Simple insight
    if len(ranked) >= 2:
        top = ranked[0]
        sec = ranked[1]
        ratio = round(top["avg_watch_hours"] / sec["avg_watch_hours"], 1) if sec["avg_watch_hours"] else "?"
        lines.append(f"\n→ **Líder:** {top['label']} ({top['avg_watch_hours']:.1f}h/video avg)")
        if isinstance(ratio, float) and ratio > 1.1:
            lines.append(f" — {ratio}x vs {sec['label']}")
        lines.append("\n")
        lines.append(f"→ **Top video:** \"{top['top_video']['title'][:50]}\" ({top['top_video']['watch_hours']:.1f}h)\n")

    lines.append("\n→ **Acción recomendada:** *(completa manualmente — ¿qué producir esta semana?)*\n")
    lines.append("\n---\n")
    return "".join(lines)


def _week_num() -> str:
    return datetime.now().strftime("W%W")


def prepend_to_strategy_log(entry: str) -> None:
    existing = ""
    if os.path.exists(STRATEGY_PATH):
        with open(STRATEGY_PATH) as f:
            existing = f.read()

    if not existing:
        header = "# STRATEGY LOG — @VersiculoDeDios\n\n" \
                 "> Append-only. Cada domingo niche_report.py agrega una nueva semana.\n" \
                 "> Lee esto cada lunes antes de producir contenido.\n\n---\n"
        existing = header

    # Prepend new entry after the header
    header_end = existing.find("---\n")
    if header_end >= 0:
        insert_at = header_end + 4
        content = existing[:insert_at] + entry + existing[insert_at:]
    else:
        content = existing + entry

    with open(STRATEGY_PATH, "w") as f:
        f.write(content)


def main(days: int = 7, week_label: str | None = None) -> None:
    if not week_label:
        week_label = datetime.now().strftime("%Y-%m-%d")

    print(f"niche_report — week {week_label} (last {days} days)")

    rows = load_log(days)
    if not rows:
        print(f"  No data in {LOG_PATH} for last {days} days.")
        print("  Run scripts/track_video_daily.py first.")
        return

    print(f"  Loaded {len(rows)} log rows")

    agg    = aggregate(rows)
    ranked = rank_clusters(agg)

    # Save niche_performance.json
    perf_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days":  days,
        "week_label":   week_label,
        "clusters":     ranked,
    }
    with open(PERF_PATH, "w") as f:
        json.dump(perf_data, f, ensure_ascii=False, indent=2)
    print(f"  Saved → {PERF_PATH}")

    # Print table
    print(f"\n  Performance by cluster (last {days} days):\n")
    print(f"  {'Cluster':<27} {'Avg WH':>7} {'Avg Ret':>8} {'Total WH':>9} {'Videos':>7}")
    print("  " + "-" * 65)
    for c in ranked:
        print(f"  {c['label']:<27} {c['avg_watch_hours']:>7.1f} {c['avg_retention_pct']:>7.1f}%"
              f" {c['total_watch_hours']:>8.1f}h {c['videos_count']:>6}")

    # Prepend to strategy log
    entry = build_strategy_entry(ranked, week_label, days)
    prepend_to_strategy_log(entry)
    print(f"\n  Updated → {STRATEGY_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--week-label", type=str, default=None)
    args = parser.parse_args()
    main(days=args.days, week_label=args.week_label)
