"""
scripts/ig_daemon.py — IG Reels uploader background daemon.

Why daemon: Instagram Graph API NO soporta scheduled_publish_time nativo.
Solución: daemon local que chequea schedule cada N min, publica AT target time.

Catch-up: si Mac off cuando llegó hora target, daemon publica al despertar
(marca entry con `late=true` para visibilidad).

Idempotente: nunca publica 2x el mismo ID.

Uso:
    # One-shot check (testear / cron)
    .venv/bin/python3 scripts/ig_daemon.py

    # Verbose
    .venv/bin/python3 scripts/ig_daemon.py --verbose

    # Force publish ahora (override hora target — debug only)
    .venv/bin/python3 scripts/ig_daemon.py --force venom_001

    # Dry-run (no publica)
    .venv/bin/python3 scripts/ig_daemon.py --dry-run

State:
    - Lee: data/shorts_schedule.json (plan venom)
    - Escribe: data/ig_state.json (qué se publicó cuándo + status)
    - Logs: logs/ig_daemon.log
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
SCHEDULE_PATH = PROJECT_DIR / "data" / "shorts_schedule.json"
STATE_PATH    = PROJECT_DIR / "data" / "ig_state.json"
LOG_DIR       = PROJECT_DIR / "logs"
LOG_PATH      = LOG_DIR / "ig_daemon.log"
TOKENS_FILE   = Path("/Users/fernandocastaneda/Documents/cero/cero-content/scripts/configs/tokens.json")

IG_USER_ID    = "17841469453382962"  # @palabradedios111

MTY_OFFSET    = timedelta(hours=-6)
MTY_TZ        = timezone(MTY_OFFSET)

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
log = logging.getLogger("ig_daemon")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"published": {}, "errors": {}, "last_check": None}


def save_state(state: dict) -> None:
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def get_ig_token() -> str:
    tokens = json.loads(TOKENS_FILE.read_text())
    return tokens["palabra-de-dios"]


def upload_to_ig(video_path: Path, caption: str, token: str, dry_run: bool = False) -> str | None:
    """
    Upload Reel to IG via Graph API.
    Returns media_id or None.

    Steps:
      1. POST /{ig-user-id}/media (returns creation_id) — uses video_url
      2. Poll status until FINISHED
      3. POST /{ig-user-id}/media_publish (with creation_id) — publishes
    """
    if dry_run:
        log.info(f"[DRY] Would upload {video_path.name} to IG with caption: {caption[:60]}...")
        return "dry-ig-id"

    import requests

    # IG Graph API requires video to be hosted (NOT direct upload). Use Resumable Upload API.
    # POST /{ig-user-id}/media with upload_type=resumable
    create_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"

    # Resumable upload approach for Reels
    create_params = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "access_token": token,
    }
    r = requests.post(create_url, params=create_params, timeout=60)
    r.raise_for_status()
    container = r.json()
    container_id = container.get("id")
    upload_url = container.get("uri")
    if not container_id or not upload_url:
        log.error(f"No container_id/upload_url: {container}")
        return None
    log.info(f"Container created: {container_id}")

    # Upload video in 4MB chunks (LSVP requires chunked upload, single-request = 400)
    CHUNK_SIZE = 4 * 1024 * 1024
    size = video_path.stat().st_size
    with open(video_path, "rb") as f:
        offset = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            headers = {
                "Authorization": f"OAuth {token}",
                "Content-Type": "application/octet-stream",
                "offset": str(offset),
                "file_size": str(size),
            }
            up = requests.post(upload_url, headers=headers, data=chunk, timeout=120)
            up.raise_for_status()
            offset += len(chunk)
            log.info(f"Uploaded {offset}/{size} bytes ({up.status_code})")
    log.info(f"Upload complete: {size} bytes")

    # Poll status
    status_url = f"https://graph.facebook.com/v19.0/{container_id}"
    for attempt in range(30):  # 30 * 5s = 2.5 min max
        time.sleep(5)
        r = requests.get(status_url, params={"fields": "status_code,status", "access_token": token}, timeout=30)
        s = r.json()
        code = s.get("status_code")
        log.info(f"Status check {attempt+1}: {code}")
        if code == "FINISHED":
            break
        if code == "ERROR":
            log.error(f"Status ERROR: {s}")
            return None
    else:
        log.error("Status FINISHED timeout (2.5 min)")
        return None

    # Publish
    pub_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    r = requests.post(pub_url, params={"creation_id": container_id, "access_token": token}, timeout=60)
    r.raise_for_status()
    media_id = r.json().get("id")
    log.info(f"PUBLISHED: media_id={media_id}")
    return media_id


def process_schedule(dry_run: bool = False, force_id: str | None = None, verbose: bool = False) -> dict:
    """
    Main loop: check schedule, publish what's due.
    Returns summary {published: [], skipped: [], errors: []}.
    """
    summary = {"published": [], "skipped": [], "errors": [], "checked": 0}

    if not SCHEDULE_PATH.exists():
        log.warning(f"No schedule file at {SCHEDULE_PATH}")
        return summary

    schedule = json.loads(SCHEDULE_PATH.read_text()).get("schedule", [])
    state = load_state()
    published = state.get("published", {})
    errors = state.get("errors", {})
    now = datetime.now(MTY_TZ)

    token = None  # lazy-load

    for entry in schedule:
        vid_id = entry["id"]
        summary["checked"] += 1

        # Skip if already published
        if vid_id in published:
            if verbose:
                log.info(f"{vid_id}: already published {published[vid_id]['ig_id']}")
            continue

        # Force override
        if force_id and force_id == vid_id:
            log.info(f"FORCE publish {vid_id}")
            target_time = now
        else:
            # Check if due
            target_str = entry.get("publish_mty", "")
            try:
                target_time = datetime.strptime(target_str, "%Y-%m-%d %H:%M MTY").replace(tzinfo=MTY_TZ)
            except Exception as e:
                log.warning(f"{vid_id}: bad publish_mty '{target_str}': {e}")
                continue

            if target_time > now:
                if verbose:
                    log.info(f"{vid_id}: not due yet ({target_str})")
                summary["skipped"].append({"id": vid_id, "reason": "not_due", "target": target_str})
                continue

        # Due — upload
        mp4 = Path(entry.get("mp4", ""))
        if not mp4.exists():
            err = f"mp4 missing: {mp4}"
            log.error(f"{vid_id}: {err}")
            errors[vid_id] = {"error": err, "at": now.isoformat()}
            summary["errors"].append({"id": vid_id, "error": err})
            continue

        if token is None:
            token = get_ig_token()

        # Build caption
        titulo = entry.get("titulo", "")
        hook   = entry.get("hook", "")
        caption = f"{titulo}\n\n{hook}\n\n#oracion #fe #dios #biblia #versiculos #reels\n@palabradedios111"

        late = (now - target_time).total_seconds() > 300  # >5 min late
        log.info(f"PUBLISHING {vid_id} ({'LATE' if late else 'on-time'}) → IG")

        try:
            media_id = upload_to_ig(mp4, caption, token, dry_run=dry_run)
            if media_id:
                published[vid_id] = {
                    "ig_id": media_id,
                    "published_at": now.isoformat(),
                    "target_at": target_time.isoformat(),
                    "late": late,
                }
                summary["published"].append({"id": vid_id, "ig_id": media_id, "late": late})
                # Clear error if was retried
                errors.pop(vid_id, None)
            else:
                err = "upload returned None"
                errors[vid_id] = {"error": err, "at": now.isoformat()}
                summary["errors"].append({"id": vid_id, "error": err})
        except Exception as e:
            err = str(e)[:300]
            log.exception(f"{vid_id}: upload failed: {err}")
            errors[vid_id] = {"error": err, "at": now.isoformat()}
            summary["errors"].append({"id": vid_id, "error": err})

    state["published"] = published
    state["errors"] = errors
    if not dry_run:
        save_state(state)
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", help="Force publish este id (override hora target)")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--status", action="store_true", help="Solo muestra status, no procesa")
    args = p.parse_args()

    if args.status:
        state = load_state()
        published = state.get("published", {})
        errors = state.get("errors", {})
        last = state.get("last_check", "never")
        print(f"Last check: {last}")
        print(f"Published: {len(published)}/20")
        for k, v in published.items():
            tag = " [LATE]" if v.get("late") else ""
            print(f"  ✅ {k}: {v['ig_id']} @ {v['published_at'][:19]}{tag}")
        print(f"Errors: {len(errors)}")
        for k, v in errors.items():
            print(f"  ❌ {k}: {v['error'][:80]}")
        return

    log.info(f"=== Daemon run: dry={args.dry_run} force={args.force} ===")
    summary = process_schedule(dry_run=args.dry_run, force_id=args.force, verbose=args.verbose)
    log.info(f"Summary: published={len(summary['published'])} skipped={len(summary['skipped'])} errors={len(summary['errors'])} checked={summary['checked']}")

    print(f"Checked: {summary['checked']}")
    print(f"Published: {len(summary['published'])}")
    for p in summary["published"]:
        tag = " [LATE]" if p.get("late") else ""
        print(f"  ✅ {p['id']}: {p['ig_id']}{tag}")
    print(f"Errors: {len(summary['errors'])}")
    for e in summary["errors"]:
        print(f"  ❌ {e['id']}: {e['error'][:80]}")
    if args.verbose:
        print(f"Skipped (not due): {len(summary['skipped'])}")


if __name__ == "__main__":
    main()
