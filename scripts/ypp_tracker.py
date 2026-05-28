#!/usr/bin/env python3
"""
scripts/ypp_tracker.py — Daily YPP watch-hours tracker for @VersiculoDeDios

Filters long-form videos (>=10 min) from 365-day analytics, sums watch hours,
appends a daily entry to data/ypp-progress.jsonl, and prints a progress report.

Run daily (manually or via cron):
    .venv/bin/python3 scripts/ypp_tracker.py

Output:
    data/ypp-progress.jsonl  — one JSON line per day (append-only log)
    stdout                   — daily report
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.youtube_client import get_channel_videos, get_video_analytics

YPP_GOAL         = 3000.0  # watch hours required
LONGFORM_MIN_MIN = 10      # 10 minutes — clean gap: Shorts <2min, long-form >14min
LOG_PATH         = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ypp-progress.jsonl")


def fetch_longform_hours() -> tuple[float, list[dict]]:
    """
    Returns (total_longform_watch_hours_365d, per_video_breakdown).

    Strategy: get ALL channel videos, filter long-form by duration,
    then query analytics individually per video (avoids top-50 Shorts domination).
    """
    print("  Loading all channel videos...")
    all_videos = get_channel_videos(max_results=2000)
    seen_ids = set()
    deduped = []
    for v in all_videos:
        if v["video_id"] not in seen_ids:
            seen_ids.add(v["video_id"])
            deduped.append(v)
    longform_meta = [v for v in deduped if v.get("duration_min", 0) >= LONGFORM_MIN_MIN]
    print(f"  Long-form videos found: {len(longform_meta)}")

    longform = []
    for i, v in enumerate(longform_meta, 1):
        vid_id = v["video_id"]
        print(f"  [{i}/{len(longform_meta)}] {v['title'][:45]}...")
        an = get_video_analytics(vid_id, days=365)
        longform.append({
            "video_id":     vid_id,
            "title":        v["title"][:60],
            "duration_min": v["duration_min"],
            "watch_hours":  an.get("watch_time_hours", 0),
            "views":        an.get("views", 0),
            "avg_view_pct": an.get("avg_view_pct", 0.0),
        })

    total = round(sum(v["watch_hours"] for v in longform), 2)
    longform.sort(key=lambda x: x["watch_hours"], reverse=True)
    return total, longform


def load_previous_entry() -> dict | None:
    if not os.path.exists(LOG_PATH):
        return None
    with open(LOG_PATH) as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def append_entry(entry: dict) -> None:
    """Append entry, skipping if today already logged (prevents double-run drift)."""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            lines = [l.strip() for l in f if l.strip()]
        if lines:
            last = json.loads(lines[-1])
            if last.get("date") == entry.get("date"):
                print(f"  [ypp_tracker] entry for {entry['date']} already exists — skip")
                return
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def days_to_goal(current_hrs: float, daily_rate: float) -> str:
    if daily_rate <= 0:
        return "N/A"
    remaining = YPP_GOAL - current_hrs
    if remaining <= 0:
        return "0 (meta alcanzada)"
    return str(round(remaining / daily_rate))


def main() -> None:
    print("Fetching 365d long-form analytics...")
    total_hrs, breakdown = fetch_longform_hours()

    today     = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prev      = load_previous_entry()
    prev_hrs  = prev["longform_watch_hours"] if prev else None
    delta     = round(total_hrs - prev_hrs, 2) if prev_hrs is not None else None
    remaining = round(YPP_GOAL - total_hrs, 2)
    pct       = round((total_hrs / YPP_GOAL) * 100, 1)

    # Compute 7-day rolling rate from log if available
    daily_rate = 0.0
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            entries = [json.loads(l) for l in f if l.strip()]
        if len(entries) >= 7:
            week_ago_hrs = entries[-7]["longform_watch_hours"]
            daily_rate   = round((total_hrs - week_ago_hrs) / 7, 2)
        elif len(entries) >= 2:
            span    = len(entries) - 1
            daily_rate = round((total_hrs - entries[0]["longform_watch_hours"]) / span, 2)

    eta_days = days_to_goal(total_hrs, daily_rate)

    entry = {
        "date":                today,
        "longform_watch_hours": total_hrs,
        "delta_vs_yesterday":  delta,
        "remaining_hours":     remaining,
        "pct_complete":        pct,
        "daily_rate_7d":       daily_rate,
        "eta_days":            eta_days,
        "top_contributors":    breakdown[:5],
    }
    append_entry(entry)

    # ── Print report ─────────────────────────────────────────────────────────
    print()
    print("=" * 52)
    print(f"  YPP TRACKER — {today}")
    print("=" * 52)
    print(f"  Long-form watch hrs:  {total_hrs:>8.1f} / 3,000")
    print(f"  Progreso:             {pct:>7.1f}%")
    print(f"  Restante:             {remaining:>8.1f} hrs")
    if delta is not None:
        sign = "+" if delta >= 0 else ""
        print(f"  Delta vs ayer:        {sign}{delta:>7.1f} hrs")
    if daily_rate > 0:
        print(f"  Ritmo 7d:             +{daily_rate:.1f} hrs/día")
        print(f"  ETA a meta:           {eta_days} días")
    print()
    print("  Top long-form contributors (365d):")
    for i, v in enumerate(breakdown[:5], 1):
        print(f"    {i}. {v['watch_hours']:>6.1f}h  {v['duration_min']:.0f}min  {v['views']:>5} views  ({v['avg_view_pct']:.0f}% ret)")
    print("=" * 52)
    print(f"  Log → {LOG_PATH}")
    print()


if __name__ == "__main__":
    main()
