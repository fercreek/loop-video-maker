"""
scripts/yt_stats.py — CLI para ver métricas del canal @FeEnAcción.

Uso:
    .venv/bin/python3 scripts/yt_stats.py                  # resumen completo
    .venv/bin/python3 scripts/yt_stats.py --videos         # lista todos los videos
    .venv/bin/python3 scripts/yt_stats.py --analytics      # analytics 28 días por video
    .venv/bin/python3 scripts/yt_stats.py --recommend      # qué subir ahora
    .venv/bin/python3 scripts/yt_stats.py --days 7         # cambiar período analytics
"""
from __future__ import annotations

import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.youtube_client import (
    get_channel_summary,
    get_channel_videos,
    get_channel_analytics,
    get_upload_recommendations,
)


def fmt_dur(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    return f"{m}m{s:02d}s"


def fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def print_channel_summary():
    print("\n📺 CANAL @FeEnAcción")
    print("─" * 50)
    s = get_channel_summary()
    print(f"  Suscriptores:  {fmt_num(s['subscribers'])}")
    print(f"  Views totales: {fmt_num(s['total_views'])}")
    print(f"  Videos:        {s['video_count']}")


def print_videos(days: int = 28):
    print("\n🎬 VIDEOS EN EL CANAL")
    print("─" * 90)
    print(f"  {'Título':<55} {'Duración':>8} {'Views':>8} {'Likes':>6} {'Subido'}")
    print("  " + "─" * 86)
    for v in get_channel_videos():
        pub = v["published_at"][:10]
        title = v["title"][:54]
        print(f"  {title:<55} {str(v['duration_min'])+'min':>8} {fmt_num(v['views']):>8} {fmt_num(v['likes']):>6}  {pub}")


def print_analytics(days: int = 28):
    print(f"\n📊 ANALYTICS — últimos {days} días")
    print("─" * 95)
    an = get_channel_analytics(days=days)
    print(f"  Total views: {fmt_num(an['total_views'])}  |  Watch time: {an['total_watch_hours']:.1f}h")
    print()
    print(f"  {'Video ID':<15} {'Views':>8} {'WatchTime':>10} {'AvgDur':>8} {'Ret%':>6} {'Subs+':>6}")
    print("  " + "─" * 57)

    # Enrich with titles
    videos_meta = {v["video_id"]: v["title"] for v in get_channel_videos()}
    for v in an["videos"]:
        title = videos_meta.get(v["video_id"], v["video_id"])[:30]
        print(
            f"  {title:<35} {fmt_num(v['views']):>6} "
            f"{str(v['watch_time_hours'])+'h':>8} "
            f"{fmt_dur(v['avg_view_duration_sec']):>8} "
            f"{v['avg_view_pct']:>5.1f}% "
            f"{v['subscribers_gained']:>5}"
        )
    print()
    # Monetization progress
    total_wt_all = an["total_watch_hours"]
    MONETIZE_THRESHOLD = 4000
    print(f"  💰 Watch time total período: {total_wt_all:.1f}h  (threshold monetización: {MONETIZE_THRESHOLD}h/año)")


def print_recommendations():
    print("\n🚀 RECOMENDACIONES DE SUBIDA")
    print("─" * 60)
    r = get_upload_recommendations()
    print(f"  Último upload:    {r['latest_upload'][:10] if r['latest_upload'] else '—'}")
    print(f"  Días sin upload:  {r['days_since_upload']}")
    print(f"  Subir ahora:      {'✅ SÍ' if r['should_upload_now'] else '⏳ No urgente'}")
    print(f"  Pendientes 60min: {r['pending_60min']} videos")
    print(f"  Pendientes 120min:{r['pending_120min']} videos")
    print(f"  Views 28 días:    {fmt_num(r['total_views_28d'])}")
    print(f"  Watch time 28d:   {r['total_watch_hours_28d']:.1f}h")
    print()
    print("  Recomendaciones:")
    for rec in r["recommendations"]:
        print(f"    → {rec}")


def main():
    ap = argparse.ArgumentParser(description="YouTube stats para @FeEnAcción")
    ap.add_argument("--videos",    action="store_true", help="Lista todos los videos")
    ap.add_argument("--analytics", action="store_true", help="Analytics por video")
    ap.add_argument("--recommend", action="store_true", help="Qué subir ahora")
    ap.add_argument("--days",      type=int, default=28, help="Período analytics en días")
    args = ap.parse_args()

    try:
        if not any([args.videos, args.analytics, args.recommend]):
            # Default: todo
            print_channel_summary()
            print_videos()
            print_analytics(args.days)
            print_recommendations()
        else:
            if args.videos:
                print_channel_summary()
                print_videos()
            if args.analytics:
                print_analytics(args.days)
            if args.recommend:
                print_recommendations()
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        raise


if __name__ == "__main__":
    main()
