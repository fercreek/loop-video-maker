"""
core/youtube_client.py — Wrapper para YouTube Data API v3 + YouTube Analytics API.

Funciones principales:
    get_channel_videos()          → lista de videos del canal con metadata
    get_video_analytics(video_id) → views, watch time, CTR, retención
    get_channel_summary()         → subs, total views, video count
    get_upload_recommendations()  → analiza gaps y recomienda cuándo subir

Requiere: data/yt_token.json (generado por scripts/yt_auth.py)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

TOKEN_PATH  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "yt_token.json")

# Channel ID — set to "mine" to auto-resolve the authenticated channel,
# or override in config.json with {"youtube_channel_id": "UCxxxx"} for a specific channel.
# @VersiculoDeDios is the target channel (11K subs) under fercreek@gmail.com.
_CHANNEL_ID_OVERRIDE = None  # populated by get_channel_id() on first call
CHANNEL_HANDLE = "@VersiculoDeDios"


def get_channel_id(handle_or_id: str | None = None) -> str:
    """
    Resolve channel ID. Priority:
    1. Explicit handle_or_id argument
    2. config.json["youtube_channel_id"]
    3. List all channels on the account, pick @VersiculoDeDios
    4. Fall back to authenticated account's default channel ("mine")
    """
    global _CHANNEL_ID_OVERRIDE
    if _CHANNEL_ID_OVERRIDE:
        return _CHANNEL_ID_OVERRIDE

    # Check config.json override
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    if os.path.exists(cfg_path):
        import json
        with open(cfg_path) as f:
            cfg = json.load(f)
        if cfg.get("youtube_channel_id"):
            _CHANNEL_ID_OVERRIDE = cfg["youtube_channel_id"]
            return _CHANNEL_ID_OVERRIDE

    if handle_or_id:
        _CHANNEL_ID_OVERRIDE = handle_or_id
        return _CHANNEL_ID_OVERRIDE

    # Auto-detect via handle lookup (YouTube Data API v3 supports forHandle param)
    # Note: channels().list(mine=True) only returns the PRIMARY channel of the Google account.
    # To get @VersiculoDeDios (a Brand Account), we look it up by handle directly.
    yt = _youtube()
    try:
        resp = yt.channels().list(
            part="snippet,statistics",
            forHandle="VersiculoDeDios",
        ).execute()
        if resp.get("items"):
            ch = resp["items"][0]
            _CHANNEL_ID_OVERRIDE = ch["id"]
            print(f"  Auto-detected channel: {ch['snippet']['title']} ({ch['id']})")
            return _CHANNEL_ID_OVERRIDE
    except Exception:
        pass  # forHandle not available in older API versions — fall through

    # Fallback: use authenticated account's primary channel
    resp = yt.channels().list(part="snippet,statistics", mine=True).execute()
    channels = resp.get("items", [])
    if channels:
        _CHANNEL_ID_OVERRIDE = channels[0]["id"]
        print(f"  Using channel: {channels[0]['snippet']['title']} ({_CHANNEL_ID_OVERRIDE})")
        return _CHANNEL_ID_OVERRIDE

    raise RuntimeError("No se encontró ningún canal en la cuenta autenticada.")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


# ─── Auth ─────────────────────────────────────────────────────────────────────

def _get_creds() -> Credentials:
    if not os.path.exists(TOKEN_PATH):
        raise RuntimeError(
            f"Token no encontrado: {TOKEN_PATH}\n"
            "Corre: .venv/bin/python3 scripts/yt_auth.py"
        )
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def _youtube():
    return build("youtube", "v3", credentials=_get_creds())


def _analytics():
    return build("youtubeAnalytics", "v2", credentials=_get_creds())


# ─── Channel ──────────────────────────────────────────────────────────────────

def get_channel_summary() -> dict:
    """
    Returns basic channel stats.

    {
        "title": "VersiculoDeDios",
        "subscribers": 1234,
        "total_views": 56789,
        "video_count": 8,
        "channel_id": "UC...",
    }
    """
    yt = _youtube()
    resp = yt.channels().list(
        part="snippet,statistics",
        id=get_channel_id(),
    ).execute()

    ch = resp["items"][0]
    stats = ch["statistics"]
    return {
        "title":       ch["snippet"]["title"],
        "subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "channel_id":  get_channel_id(),
    }


# ─── Videos ───────────────────────────────────────────────────────────────────

def get_channel_videos(max_results: int = 50) -> list[dict]:
    """
    Returns list of all videos on the channel, newest first.

    Each item:
    {
        "video_id":     "abc123",
        "title":        "¡PAZ SOBRENATURAL!...",
        "published_at": "2026-04-22T10:00:00Z",
        "duration_iso": "PT1H2M3S",
        "duration_min": 62,
        "views":        1234,
        "likes":        56,
        "comments":     7,
        "thumbnail_url": "https://...",
    }
    """
    yt = _youtube()

    # Step 1: get video IDs from channel uploads playlist
    ch_resp = yt.channels().list(
        part="contentDetails",
        id=get_channel_id(),
    ).execute()
    uploads_playlist = ch_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Step 2: list videos in uploads playlist
    videos = []
    page_token = None
    while True:
        pl_resp = yt.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist,
            maxResults=min(max_results, 50),
            pageToken=page_token,
        ).execute()

        video_ids = [item["contentDetails"]["videoId"] for item in pl_resp["items"]]

        # Step 3: batch fetch stats + duration
        vid_resp = yt.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids),
        ).execute()

        for v in vid_resp["items"]:
            dur_iso = v["contentDetails"]["duration"]
            videos.append({
                "video_id":      v["id"],
                "title":         v["snippet"]["title"],
                "published_at":  v["snippet"]["publishedAt"],
                "duration_iso":  dur_iso,
                "duration_min":  _iso_duration_to_min(dur_iso),
                "views":         int(v["statistics"].get("viewCount", 0)),
                "likes":         int(v["statistics"].get("likeCount", 0)),
                "comments":      int(v["statistics"].get("commentCount", 0)),
                "thumbnail_url": v["snippet"]["thumbnails"].get("maxres", v["snippet"]["thumbnails"].get("high", {})).get("url", ""),
            })

        page_token = pl_resp.get("nextPageToken")
        if not page_token or len(videos) >= max_results:
            break

    return sorted(videos, key=lambda v: v["published_at"], reverse=True)


def _iso_duration_to_min(iso: str) -> int:
    """Convert PT1H2M3S → 62 minutes."""
    import re
    h = int(re.search(r"(\d+)H", iso).group(1)) if "H" in iso else 0
    m = int(re.search(r"(\d+)M", iso).group(1)) if "M" in iso else 0
    s = int(re.search(r"(\d+)S", iso).group(1)) if "S" in iso else 0
    return h * 60 + m + (1 if s >= 30 else 0)


# ─── Analytics ────────────────────────────────────────────────────────────────

def get_video_analytics(video_id: str, days: int = 28) -> dict:
    """
    Returns analytics for a specific video over the last N days.

    {
        "video_id":              "abc123",
        "period_days":           28,
        "views":                 1234,
        "watch_time_hours":      456.7,
        "avg_view_duration_sec": 1320,
        "avg_view_pct":          36.7,
        "subscribers_gained":    12,
        "likes":                 34,
        "shares":                5,
        "impressions":           8900,
        "ctr":                   4.5,   # %
    }
    """
    an = _analytics()
    end   = datetime.utcnow().date()
    start = end - timedelta(days=days)

    resp = an.reports().query(
        ids=f"channel=={get_channel_id()}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,shares",
        dimensions="video",
        filters=f"video=={video_id}",
    ).execute()

    if not resp.get("rows"):
        return {"video_id": video_id, "period_days": days, "views": 0, "watch_time_hours": 0,
                "avg_view_duration_sec": 0, "avg_view_pct": 0.0, "subscribers_gained": 0,
                "likes": 0, "shares": 0}

    row = resp["rows"][0]
    # columns: video, views, estimatedMinutesWatched, avgViewDuration, avgViewPct, subsGained, likes, shares
    return {
        "video_id":              video_id,
        "period_days":           days,
        "views":                 int(row[1]),
        "watch_time_hours":      round(int(row[2]) / 60, 1),
        "avg_view_duration_sec": int(row[3]),
        "avg_view_pct":          round(float(row[4]), 1),
        "subscribers_gained":    int(row[5]),
        "likes":                 int(row[6]),
        "shares":                int(row[7]),
    }


def get_channel_analytics(days: int = 28) -> dict:
    """
    Returns aggregate channel analytics over the last N days.
    Includes per-video breakdown.
    """
    an = _analytics()
    end   = datetime.utcnow().date()
    start = end - timedelta(days=days)

    resp = an.reports().query(
        ids=f"channel=={get_channel_id()}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained",
        dimensions="video",
        sort="-views",
        maxResults=50,
    ).execute()

    rows = resp.get("rows", [])
    videos = []
    for row in rows:
        videos.append({
            "video_id":              row[0],
            "views":                 int(row[1]),
            "watch_time_hours":      round(int(row[2]) / 60, 1),
            "avg_view_duration_sec": int(row[3]),
            "avg_view_pct":          round(float(row[4]), 1),
            "subscribers_gained":    int(row[5]),
        })

    total_views = sum(v["views"] for v in videos)
    total_wt    = sum(v["watch_time_hours"] for v in videos)

    return {
        "period_days":        days,
        "total_views":        total_views,
        "total_watch_hours":  round(total_wt, 1),
        "videos":             videos,
    }


# ─── Upload recommendations ───────────────────────────────────────────────────

def get_upload_recommendations() -> dict:
    """
    Cross-references local pending videos with channel analytics.
    Returns what to upload next and why.

    Logic:
      - Top performer theme → create more content in that theme
      - Themes missing from channel → upload first
      - Upload cadence: if last upload > 5 days ago → upload now
    """
    import glob

    summary  = get_channel_summary()
    videos   = get_channel_videos()
    analytics = get_channel_analytics(days=28)

    # Map video_id → analytics
    an_map = {v["video_id"]: v for v in analytics["videos"]}
    for v in videos:
        v["analytics"] = an_map.get(v["video_id"], {})

    # Latest upload date
    latest_upload = videos[0]["published_at"] if videos else None
    days_since_upload = None
    if latest_upload:
        from datetime import timezone
        pub = datetime.fromisoformat(latest_upload.replace("Z", "+00:00"))
        days_since_upload = (datetime.now(timezone.utc) - pub).days

    # Best performing theme (by avg_view_pct)
    best_video = max(videos, key=lambda v: v["analytics"].get("avg_view_pct", 0)) if videos else None

    # Local pending files
    pending_60  = sorted(glob.glob("output/SUBIR/pendiente/*_60min.mp4"))
    pending_120 = sorted(glob.glob("output/SUBIR/pendiente/*_120min.mp4"))

    # Build recommendation
    upload_now = days_since_upload is not None and days_since_upload >= 5
    recs = []
    if upload_now:
        recs.append(f"Han pasado {days_since_upload} días desde el último upload — subir ahora")
    if pending_60:
        recs.append(f"{len(pending_60)} videos 60min pendientes: {[os.path.basename(p) for p in pending_60[:3]]}")
    if pending_120:
        recs.append(f"{len(pending_120)} videos 120min pendientes (nuevo formato) — subir para diversificar")
    if best_video:
        recs.append(f"Top performer: '{best_video['title'][:50]}' — {best_video['analytics'].get('avg_view_pct', 0)}% retención media")

    return {
        "channel":             summary,
        "days_since_upload":   days_since_upload,
        "latest_upload":       latest_upload,
        "should_upload_now":   upload_now,
        "pending_60min":       len(pending_60),
        "pending_120min":      len(pending_120),
        "best_performer":      best_video,
        "recommendations":     recs,
        "total_watch_hours_28d": analytics["total_watch_hours"],
        "total_views_28d":     analytics["total_views"],
    }
