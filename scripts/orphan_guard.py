#!/usr/bin/env python3
"""
scripts/orphan_guard.py — Daily reconciliation guard for @VersiculoDeDios.

Catches ORPHAN uploads: videos that appear on the channel but never went through
the tracking pipeline (e.g. manual phone uploads). Born from the 2026-06-09 incident
where two foreign TikToks (r43LS0y0Wrg, MdenXXdtW60, ~435h combined) lived ~2 weeks
undetected and posed a YPP/copyright-strike risk.

How it works
------------
1. Pull every videoId from the channel uploads playlist (YouTube Data API).
2. Build the KNOWN set = union of youtube_ids across the tracking JSONs
   (video_catalog.json primary + upload_schedule / shorts_schedule / content_registry
   / lofi_push_plan). The catalog alone only knows ~55 of 1000+ lifetime videos, so a
   lifetime diff is meaningless — we WINDOW by publish date (default 14 days). A daily
   guard only cares about what landed recently.
3. orphan = published within the window AND not in the KNOWN set.
4. For each orphan fetch contentDetails.licensedContent + lifetime watch hours.
   Severity HIGH  = licensedContent True (copyright signal) OR watch_hours >= threshold
                    (default 50h — the TikTok signature was ~217h each; normal new
                    shorts top out ~30h, so this fires on anomalies, not own content).
   Severity LOW   = everything else (logged, no alert).
5. Write data/orphan-uploads.json. With --alert, fire a venom-tone WhatsApp on any HIGH.

Exit codes: 0 = no orphans · 1 = LOW orphans only · 2 = at least one HIGH orphan.

Usage
-----
    .venv/bin/python3 scripts/orphan_guard.py                  # report only
    .venv/bin/python3 scripts/orphan_guard.py --window 14
    .venv/bin/python3 scripts/orphan_guard.py --alert          # WA on HIGH (daily/cron)
    .venv/bin/python3 scripts/orphan_guard.py --simulate XXXXX # test: flag a known video
    .venv/bin/python3 scripts/orphan_guard.py --catalog-only   # strict: diff vs catalog only
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import warnings
from datetime import datetime, timedelta, timezone

warnings.filterwarnings("ignore")  # silence google py3.9 EOL noise

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from google.oauth2.credentials import Credentials       # noqa: E402
from google.auth.transport.requests import Request       # noqa: E402
from googleapiclient.discovery import build              # noqa: E402

CHANNEL_ID   = "UC2l5TZjHzRtaRjH8kT_yQ2w"
UPLOADS_PL   = "UU2l5TZjHzRtaRjH8kT_yQ2w"   # uploads playlist = channel id with UU prefix
TOKEN_PATH   = os.path.join(ROOT, "data", "yt_token.json")
OUT_PATH     = os.path.join(ROOT, "data", "orphan-uploads.json")
ALLOWLIST    = os.path.join(ROOT, "data", "orphan-allowlist.json")

# Tracking files scanned for known youtube_ids. Catalog first (canonical), rest reduce
# false positives from legit-but-untracked uploads (shorts that never wrote their id back).
TRACKING_FILES = [
    "video_catalog.json",
    "upload_schedule.json",
    "shorts_schedule.json",
    "lofi_push_plan.json",
    "content_registry.json",
    "lofi_upload_schedule.json",
]
ID_KEYS  = {"youtube_id", "video_id", "videoId", "yt_id"}
ID_RE    = re.compile(r"[A-Za-z0-9_-]{11}")
WA_DEST  = "528117655605"   # Fernando
RECENT_H = 72   # orphan younger than this can't be vouched by analytics (lag) → MEDIUM


# ─── Auth ───────────────────────────────────────────────────────────────────
def _creds() -> Credentials:
    """Load creds using the token's OWN granted scopes — avoids the invalid_scope
    refresh failure when youtube_client requests a superset (force-ssl)."""
    if not os.path.exists(TOKEN_PATH):
        sys.exit(f"❌ Token missing: {TOKEN_PATH} — run scripts/yt_auth.py")
    scopes = json.load(open(TOKEN_PATH)).get("scopes")
    c = Credentials.from_authorized_user_file(TOKEN_PATH, scopes)
    if c.expired and c.refresh_token:
        c.refresh(Request())
        open(TOKEN_PATH, "w").write(c.to_json())
    return c


# ─── Known set from tracking files ──────────────────────────────────────────
def load_known(catalog_only: bool) -> set[str]:
    files = ["video_catalog.json"] if catalog_only else TRACKING_FILES
    known: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ID_KEYS and isinstance(v, str) and ID_RE.fullmatch(v):
                    known.add(v)
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    for f in files:
        p = os.path.join(ROOT, "data", f)
        if os.path.exists(p):
            try:
                walk(json.load(open(p)))
            except Exception as e:
                print(f"  ⚠️  skip {f}: {e}", file=sys.stderr)
    return known


def load_allowlist() -> dict:
    """Manually-acknowledged legit-own ids (e.g. cero-agent n8n auto-publishes that
    never write their youtube_id back to a local tracking file)."""
    if os.path.exists(ALLOWLIST):
        try:
            return json.load(open(ALLOWLIST))
        except Exception as e:
            print(f"  ⚠️  bad allowlist: {e}", file=sys.stderr)
    return {"description": "Orphan ids acknowledged as legit-own (not pipeline-tracked). "
                           "Guard treats these as known. HIGH orphans are NEVER auto-acked.",
            "acknowledged": []}


def allowlist_ids(al: dict) -> set[str]:
    return {a["video_id"] for a in al.get("acknowledged", [])}


# ─── Channel pull ───────────────────────────────────────────────────────────
def channel_videos(yt) -> dict[str, str]:
    """{videoId: publishedAt} for every video in the uploads playlist."""
    out: dict[str, str] = {}
    page = None
    while True:
        r = yt.playlistItems().list(
            part="contentDetails", playlistId=UPLOADS_PL,
            maxResults=50, pageToken=page,
        ).execute()
        for it in r["items"]:
            cd = it["contentDetails"]
            out[cd["videoId"]] = cd.get("videoPublishedAt")
        page = r.get("nextPageToken")
        if not page:
            break
    return out


def fetch_meta(yt, ids: list[str]) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        r = yt.videos().list(
            part="snippet,contentDetails", id=",".join(ids[i:i + 50]),
        ).execute()
        for v in r["items"]:
            meta[v["id"]] = {
                "title":            v["snippet"]["title"],
                "published_at":     v["snippet"]["publishedAt"],
                "duration":         v["contentDetails"]["duration"],
                "licensed_content": bool(v["contentDetails"].get("licensedContent", False)),
            }
    return meta


def fetch_watch_hours(an, ids: list[str]) -> tuple[dict[str, float], bool]:
    """Lifetime watch hours per video (estimatedMinutesWatched / 60).
    Returns (hours_by_id, degraded). degraded=True if ANY analytics call failed —
    callers must fail SAFE (escalate, don't assume 0h = harmless)."""
    wh: dict[str, float] = {}
    degraded = False
    today = str(datetime.now(timezone.utc).date())
    for i in range(0, len(ids), 200):  # analytics video filter caps ~500 ids
        chunk = ids[i:i + 200]
        try:
            r = an.reports().query(
                ids=f"channel=={CHANNEL_ID}", startDate="2024-01-01", endDate=today,
                metrics="estimatedMinutesWatched", dimensions="video",
                filters="video==" + ",".join(chunk), maxResults=500,
            ).execute()
        except Exception as e:
            degraded = True
            print(f"  ⚠️  analytics failed (escalating to fail-safe): {e}", file=sys.stderr)
            continue
        for row in r.get("rows", []):
            wh[row[0]] = round(row[1] / 60, 1)
    return wh, degraded


# ─── WhatsApp alert (venom tone) ────────────────────────────────────────────
def _alert_flag(o: dict) -> str:
    if o["licensed_content"]:
        return "📜 licensed"
    if o["severity"] == "MEDIUM":
        age = o.get("age_hours")
        return f"🟡 NUEVO ({age}h vida, sin vouch analytics)" if age is not None else "🟡 NUEVO"
    return f"{o['watch_hours']}h watch"


def build_alert(alerts: list[dict], window: int, degraded: bool = False) -> str:
    n_high = sum(1 for o in alerts if o["severity"] == "HIGH")
    n_med  = sum(1 for o in alerts if o["severity"] == "MEDIUM")
    lines = [
        "🕷 Venom reporta · Orphan Guard VDD",
        "",
        f"⚠️ {len(alerts)} upload(s) sin pasar pipeline (ventana {window}d). "
        f"HIGH {n_high} · MEDIUM {n_med}.",
    ]
    if degraded:
        lines.append("🛑 Analytics CAÍDA — todos escalados a HIGH (fail-safe).")
    lines.append("")
    for o in alerts:
        mark = "🛑" if o["severity"] == "HIGH" else "🟡"
        lines.append(f"{mark} {o['video_id']} · {_alert_flag(o)}")
        lines.append(f"   {o['title'][:48]}")
        lines.append(f"   youtube.com/watch?v={o['video_id']}")
    lines += [
        "",
        "Riesgo: YPP / copyright-strike (caso TikToks 06-09).",
        "Acción inmediata:",
        "• Revisar en YT Studio — borrar si es ajeno.",
        "• Si es propio: registrar en catalog, o `--ack-low` si quedó LOW.",
        "",
        "Reporte: data/orphan-uploads.json",
        "Fin del reporte. — Venom",
    ]
    return "\n".join(lines)


def notify_fallback(text: str, alerts: list[dict], out_path: str) -> None:
    """BUG-3 fix: if WhatsApp delivery fails, never lose the alert. Fire a macOS
    notification + drop a sentinel JSON next to the report so a missed HIGH is
    recoverable (and visible to the dashboard / next run)."""
    pending = os.path.join(os.path.dirname(out_path), "orphan_ALERT_PENDING.json")
    try:
        json.dump(
            {"pending_at": datetime.now(timezone.utc).isoformat(),
             "reason": "WhatsApp send failed", "message": text, "orphans": alerts},
            open(pending, "w"), indent=2, ensure_ascii=False,
        )
    except Exception as e:
        print(f"  ⚠️  could not write sentinel: {e}", file=sys.stderr)
    n = len(alerts)
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "WA falló · {n} orphan(s) · ver orphan_ALERT_PENDING.json" '
             f'with title "🛑 Orphan Guard VDD" sound name "Basso"'],
            check=False, timeout=10,
        )
    except Exception as e:
        print(f"  ⚠️  osascript failed: {e}", file=sys.stderr)


def send_wa(text: str) -> dict:
    key = os.environ.get("WASENDER_API_KEY")
    if not key:
        try:
            key = subprocess.check_output(
                ["heroku", "config:get", "WASENDER_API_KEY", "-a", "studio-link-staging"],
                text=True, stderr=subprocess.DEVNULL,
            ).strip()
        except Exception:
            key = ""
    if not key:
        return {"success": False, "error": "no WASENDER_API_KEY (env or heroku)"}
    import urllib.request
    req = urllib.request.Request(
        "https://wasenderapi.com/api/send-message",
        data=json.dumps({"to": WA_DEST, "text": text}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"success": True, "response": json.loads(resp.read())}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Main ───────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Daily orphan-upload guard for @VersiculoDeDios")
    ap.add_argument("--window", type=int, default=14, help="lookback days (default 14)")
    ap.add_argument("--high-hours", type=float, default=50.0,
                    help="watch-hours threshold for HIGH severity (default 50)")
    ap.add_argument("--catalog-only", action="store_true",
                    help="diff against video_catalog.json only (strict spec)")
    ap.add_argument("--simulate", metavar="VIDEOID",
                    help="pretend this id is missing from tracking — must flag as orphan")
    ap.add_argument("--alert", action="store_true", help="send WhatsApp on HIGH orphans")
    ap.add_argument("--ack-low", action="store_true",
                    help="absorb current LOW orphans into the allowlist (backfill; never acks HIGH)")
    ap.add_argument("--out", default=OUT_PATH, help="output JSON path")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    def log(*a):
        if not args.quiet:
            print(*a)

    creds = _creds()
    yt = build("youtube", "v3", credentials=creds)
    an = build("youtubeAnalytics", "v2", credentials=creds)

    al = load_allowlist()
    known = load_known(args.catalog_only) | allowlist_ids(al)
    if args.simulate:
        known.discard(args.simulate)  # force the known-good id to look orphaned
    log(f"  known ids: {len(known)}  (catalog_only={args.catalog_only}, "
        f"allowlist={len(allowlist_ids(al))})")

    chan = channel_videos(yt)
    log(f"  channel videos: {len(chan)}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.window)

    def in_window(pub: str | None) -> bool:
        if not pub:
            return False
        return datetime.fromisoformat(pub.replace("Z", "+00:00")) >= cutoff

    orphan_ids = [v for v, pub in chan.items() if in_window(pub) and v not in known]
    # --simulate: include the target even if outside the window, so the test always exercises
    if args.simulate and args.simulate in chan and args.simulate not in orphan_ids:
        orphan_ids.append(args.simulate)

    now = datetime.now(timezone.utc)

    def age_hours(pub: str | None) -> float | None:
        if not pub:
            return None
        return (now - datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 3600

    orphans: list[dict] = []
    degraded = False
    if orphan_ids:
        meta = fetch_meta(yt, orphan_ids)
        wh, degraded = fetch_watch_hours(an, orphan_ids)
        if degraded:
            log("  ⚠️  analytics degraded — orphans fail-safe to HIGH")
        for v in orphan_ids:
            m = meta.get(v, {})
            hours = wh.get(v, 0.0)
            licensed = m.get("licensed_content", False)
            age = age_hours(m.get("published_at", chan.get(v)))
            # Severity (fail-safe): a lagging metric (watch_hours) must not silence a
            # brand-new orphan — analytics lags 24-72h, exactly the early window the
            # guard exists to cover.
            if licensed or hours >= args.high_hours or degraded:
                sev = "HIGH"
            elif age is not None and age < RECENT_H:
                sev = "MEDIUM"   # too new for analytics to vouch → eyeball it
            else:
                sev = "LOW"
            orphans.append({
                "video_id":         v,
                "title":            m.get("title", "?"),
                "published_at":     m.get("published_at", chan.get(v)),
                "duration":         m.get("duration", "?"),
                "age_hours":        round(age, 1) if age is not None else None,
                "watch_hours":      hours,
                "licensed_content": licensed,
                "severity":         sev,
                "url":              f"https://youtube.com/watch?v={v}",
                "simulated":        bool(args.simulate and v == args.simulate),
            })
    rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    orphans.sort(key=lambda o: (rank[o["severity"]], -o["watch_hours"]))
    highs   = [o for o in orphans if o["severity"] == "HIGH"]
    alertable = [o for o in orphans if o["severity"] in ("HIGH", "MEDIUM")]

    meds = [o for o in orphans if o["severity"] == "MEDIUM"]
    report = {
        "generated_at":   now.isoformat(),
        "channel_id":     CHANNEL_ID,
        "window_days":    args.window,
        "high_hours_threshold": args.high_hours,
        "recent_hours":   RECENT_H,
        "analytics_degraded": degraded,
        "catalog_only":   args.catalog_only,
        "known_ids":      len(known),
        "channel_videos": len(chan),
        "orphan_count":   len(orphans),
        "high_count":     len(highs),
        "medium_count":   len(meds),
        "orphans":        orphans,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(report, open(args.out, "w"), indent=2, ensure_ascii=False)
    log(f"  → {args.out}")

    log(f"\n  orphans: {len(orphans)}  HIGH: {len(highs)}  MEDIUM: {len(meds)}"
        + ("  [analytics DEGRADED]" if degraded else ""))
    marks = {"HIGH": "🛑", "MEDIUM": "🟡", "LOW": "·"}
    for o in orphans[:25]:
        log(f"  {marks[o['severity']]} {o['video_id']}  {o['watch_hours']:>6}h  "
            f"lic={o['licensed_content']}  {o['title'][:40]}")

    if args.ack_low:
        lows = [o for o in orphans if o["severity"] == "LOW" and not o.get("simulated")]
        have = allowlist_ids(al)
        added = 0
        ts = now.isoformat()
        for o in lows:
            if o["video_id"] in have:
                continue
            al["acknowledged"].append({
                "video_id":  o["video_id"],
                "title":     o["title"],
                "acked_at":  ts,
                "reason":    "backfill --ack-low (legit-own, untracked auto-publish)",
            })
            added += 1
        json.dump(al, open(ALLOWLIST, "w"), indent=2, ensure_ascii=False)
        log(f"  ack-low: +{added} ids → {ALLOWLIST} ({len(al['acknowledged'])} total)")
        if added:
            log("  re-run without --ack-low to confirm clean report.")

    if alertable and args.alert:
        msg = build_alert(alertable, args.window, degraded)
        res = send_wa(msg)
        if res.get("success"):
            log("  WA alert: sent ✅")
        else:
            # BUG-3 fix: WA is the whole point — never drop an alert silently.
            log(f"  WA alert: FAILED ❌ {res.get('error')} — firing fallback")
            notify_fallback(msg, alertable, args.out)
    elif alertable:
        log(f"  ({len(alertable)} alertable orphan(s) — run with --alert to notify)")

    return 2 if highs else (1 if orphans else 0)


if __name__ == "__main__":
    sys.exit(main())
