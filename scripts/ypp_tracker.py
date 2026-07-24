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

from core.youtube_client import (
    _get_creds,
    _iso_duration_to_min,
    _youtube,
    get_channel_id,
    get_channel_videos,
    get_video_analytics,
)

YPP_GOAL         = 4000.0  # watch hours required (long-form, 365d)
LONGFORM_MIN_MIN = 10      # 10 minutes — clean gap: Shorts <2min, long-form >14min
LOG_PATH         = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ypp-progress.jsonl")


def _analytics_top_videos() -> dict[str, dict]:
    """
    {video_id: {watch_hours, views, avg_view_pct}} for the top videos by watch time (365d).

    The Analytics API caps this report at 200 rows and rejects startIndex>1, so this
    is the head of the distribution, not the whole channel. It is still essential:
    the uploads playlist silently omits videos (140 missing as of 2026-07-23,
    including the three highest-watch sleep videos), so neither source alone is complete.
    """
    from datetime import timedelta

    from googleapiclient.discovery import build

    an = build("youtubeAnalytics", "v2", credentials=_get_creds())
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=365)
    rows = an.reports().query(
        ids=f"channel=={get_channel_id()}",
        startDate=str(start),
        endDate=str(end),
        metrics="estimatedMinutesWatched,views,averageViewPercentage",
        dimensions="video",
        sort="-estimatedMinutesWatched",
        maxResults=200,
    ).execute().get("rows", [])

    return {
        r[0]: {
            "watch_hours":  round(r[1] / 60, 2),
            "views":        int(r[2]),
            "avg_view_pct": round(r[3], 1),
        }
        for r in rows
    }


def fetch_longform_hours() -> tuple[float, list[dict]]:
    """
    Returns (total_longform_watch_hours_365d, per_video_breakdown).

    Unions two incomplete sources — the Analytics top-200 and the uploads playlist —
    because each drops videos the other keeps. Long-form is filtered by duration, so
    Shorts in the analytics rows are discarded.
    """
    print("  Loading analytics top videos...")
    top = _analytics_top_videos()

    print("  Loading channel uploads...")
    meta = {}
    for v in get_channel_videos(max_results=2000):
        meta.setdefault(v["video_id"], v)

    missing_ids = [vid for vid in top if vid not in meta]
    if missing_ids:
        print(f"  {len(missing_ids)} videos con watch-time no estan en la playlist de uploads — resolviendo")
        yt = _youtube()
        for i in range(0, len(missing_ids), 50):
            resp = yt.videos().list(
                part="snippet,contentDetails",
                id=",".join(missing_ids[i:i + 50]),
            ).execute()
            for v in resp.get("items", []):
                meta[v["id"]] = {
                    "video_id":     v["id"],
                    "title":        v["snippet"]["title"],
                    "duration_min": _iso_duration_to_min(v["contentDetails"]["duration"]),
                }

    longform_meta = [v for v in meta.values() if v.get("duration_min", 0) >= LONGFORM_MIN_MIN]
    print(f"  Long-form videos found: {len(longform_meta)}")

    longform = []
    for i, v in enumerate(longform_meta, 1):
        vid_id = v["video_id"]
        an = top.get(vid_id)
        if an is None:
            # Below the analytics top-200 cutoff — needs its own query.
            print(f"  [{i}/{len(longform_meta)}] {v['title'][:45]}...")
            raw = get_video_analytics(vid_id, days=365)
            an = {
                "watch_hours":  raw.get("watch_time_hours", 0),
                "views":        raw.get("views", 0),
                "avg_view_pct": raw.get("avg_view_pct", 0.0),
            }
        longform.append({
            "video_id":     vid_id,
            "title":        v["title"][:60],
            "duration_min": v["duration_min"],
            **an,
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
    print(f"  Long-form watch hrs:  {total_hrs:>8.1f} / {YPP_GOAL:,.0f}")
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
