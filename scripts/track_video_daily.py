#!/usr/bin/env python3
"""
scripts/track_video_daily.py — Daily per-video analytics tracker.

Pulls views + watch hours for ALL uploaded long-form videos (≥10min) over
the past 7 days and appends one row per video to data/video_daily_log.jsonl.

Designed to run via launchd at 6am MTY daily.

    .venv/bin/python3 scripts/track_video_daily.py [--days N]

Output:
    data/video_daily_log.jsonl — append-only, one JSON line per video per day
    stdout — progress + summary
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from core.youtube_client import get_channel_videos, get_video_analytics

LOG_PATH     = os.path.join(PROJECT_DIR, "data", "video_daily_log.jsonl")
CATALOG_PATH = os.path.join(PROJECT_DIR, "data", "video_catalog.json")
SCHEDULE_PATH = os.path.join(PROJECT_DIR, "data", "upload_schedule.json")

LONGFORM_MIN_MIN = 10   # minimum duration to be considered long-form


def load_cluster_map() -> dict[str, str]:
    """Build {youtube_id: topic_cluster} from catalog + upload_schedule."""
    cluster_map: dict[str, str] = {}

    # From video_catalog (already tagged by tag_catalog.py)
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH) as f:
            catalog = json.load(f)
        for v in catalog.get("videos", []):
            yt_id   = v.get("status", {}).get("youtube_id")
            cluster = v.get("topic_cluster")
            if yt_id and cluster:
                cluster_map[yt_id] = cluster

    # From upload_schedule (sleep/lofi not in catalog)
    if os.path.exists(SCHEDULE_PATH):
        with open(SCHEDULE_PATH) as f:
            raw = json.load(f)
        schedule = raw.get("schedule", raw) if isinstance(raw, dict) else raw
        if isinstance(schedule, list):
            for entry in schedule:
                yt_id    = entry.get("youtube_id")
                story_id = entry.get("story_id", "").lower()
                title    = entry.get("title", "").lower()
                if not yt_id:
                    continue
                cluster = _infer_schedule_cluster(story_id, title)
                cluster_map[yt_id] = cluster

    return cluster_map


MISTERIO_PATTERNS = [
    r"así vivió", r"así era", r"los años que nadie", r"lo que nadie",
    r"qué pasó", r"qué contó", r"los 3 días", r"misterio", r"secreto",
    r"la noche que", r"la conversación secreta",
]
REDEMPTION_PATTERNS = [
    r"hijo pródigo", r"ladrón", r"perdona", r"perdonó",
    r"cobrador de impuest", r"de la oscuridad",
]


def _classify_by_title(title: str, duration_min: int) -> str:
    """Fallback cluster inference from video title when catalog lookup fails."""
    t = title.lower()

    if duration_min < 5:
        return "devocional_corto"

    # Sleep / lofi
    if any(k in t for k in ["para dormir", "sueño", "dormir en", "lofi", "lo-fi", "musica para dormir"]):
        if "salmo" in t:
            return "sleep_salmos"
        if "lofi" in t or "lo-fi" in t:
            return "lofi"
        return "sleep_versos"

    import re
    for pat in MISTERIO_PATTERNS:
        if re.search(pat, t):
            return "historia_misterio"

    for pat in REDEMPTION_PATTERNS:
        if re.search(pat, t):
            return "historia_redemption"

    return "historia_clasica"


def _infer_schedule_cluster(story_id: str, title: str) -> str:
    if "lofi" in story_id or "lofi" in title:
        return "lofi"
    if "sleep" in story_id or "dormir" in title or "para dormir" in title:
        if "salmo" in title or "salmo" in story_id:
            return "sleep_salmos"
        return "sleep_versos"
    if "salmos" in story_id:
        return "sleep_salmos"
    if any(x in story_id for x in ["120min", "60min", "90min"]):
        return "sleep_versos"
    return "historia_clasica"


def already_logged_today(date_str: str) -> set[str]:
    """Return set of video_ids already logged for date_str."""
    logged = set()
    if not os.path.exists(LOG_PATH):
        return logged
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("date") == date_str:
                    logged.add(entry["video_id"])
            except json.JSONDecodeError:
                pass
    return logged


def main(days: int = 7) -> None:
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    logged   = already_logged_today(today)

    print(f"track_video_daily — {today} (period={days}d)")

    cluster_map = load_cluster_map()
    print(f"  Cluster map: {len(cluster_map)} videos mapped")

    print("  Loading channel videos...")
    all_videos = get_channel_videos(max_results=2000)

    # Deduplicate and filter long-form
    seen: set[str] = set()
    longform = []
    for v in all_videos:
        vid_id = v["video_id"]
        if vid_id in seen:
            continue
        seen.add(vid_id)
        if v.get("duration_min", 0) >= LONGFORM_MIN_MIN:
            longform.append(v)

    print(f"  Long-form candidates: {len(longform)}")

    new_rows: list[dict] = []

    for i, v in enumerate(longform, 1):
        vid_id = v["video_id"]
        if vid_id in logged:
            print(f"  [{i}/{len(longform)}] already logged — skip {vid_id}")
            continue

        print(f"  [{i}/{len(longform)}] {v['title'][:45]}...")

        try:
            an = get_video_analytics(vid_id, days=days)
        except Exception as exc:
            print(f"    ERROR: {exc}")
            continue

        dur     = v.get("duration_min", 0)
        cluster = cluster_map.get(vid_id) or _classify_by_title(v["title"], dur)

        row = {
            "date":             today,
            "video_id":         vid_id,
            "title":            v["title"][:70],
            "duration_min":     dur,
            "topic_cluster":    cluster,
            "views":            an.get("views", 0),
            "watch_hours":      an.get("watch_time_hours", 0),
            "avg_retention_pct": an.get("avg_view_pct", 0.0),
            "impressions":      an.get("impressions", None),
            "ctr_pct":          an.get("ctr", None),
            "period_days":      days,
        }
        new_rows.append(row)

    # Append to log
    with open(LOG_PATH, "a") as f:
        for row in new_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\n  Appended {len(new_rows)} rows → {LOG_PATH}")

    # Summary by cluster
    from collections import defaultdict
    by_cluster: dict[str, list[float]] = defaultdict(list)
    for row in new_rows:
        by_cluster[row["topic_cluster"]].append(row["watch_hours"])

    if by_cluster:
        print(f"\n  Watch hours ({days}d) by cluster:")
        for cluster, whs in sorted(by_cluster.items(), key=lambda x: -sum(x[1])):
            total = sum(whs)
            avg   = total / len(whs) if whs else 0
            print(f"    {cluster:<25} {total:>6.1f}h total  {avg:>5.1f}h/video  ({len(whs)} videos)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7,
                        help="Analytics period in days (default 7)")
    args = parser.parse_args()
    main(days=args.days)
