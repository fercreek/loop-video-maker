"""
scripts/upload_to_youtube.py — Sube videos a YouTube usando schedule.

Lee data/upload_schedule.json → sube cada video como `private` con `publishAt`.
YouTube API auto-publica en la fecha programada.

Requiere:
  - data/yt_token.json (re-auth si vencido: python3 scripts/yt_auth.py)
  - google-api-python-client en venv

Uso:
    # Subir TODOS los videos pendientes en schedule
    python3 scripts/upload_to_youtube.py

    # Subir solo 1 (testing)
    python3 scripts/upload_to_youtube.py --max 1

    # Subir uno específico
    python3 scripts/upload_to_youtube.py --story david-goliat

    # Dry run — solo lista qué subiría
    python3 scripts/upload_to_youtube.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_DIR    = Path(__file__).parent.parent
SCHEDULE_PATH  = PROJECT_DIR / "data" / "upload_schedule.json"
CATALOG_PATH   = PROJECT_DIR / "data" / "video_catalog.json"
TOKEN_PATH     = PROJECT_DIR / "data" / "yt_token.json"
CLIENT_SECRETS = PROJECT_DIR / "data" / "yt_client_secrets.json"

YT_QUOTA_PER_UPLOAD = 1600
YT_DAILY_QUOTA      = 10000   # safe limit
MAX_UPLOADS_PER_DAY = YT_DAILY_QUOTA // YT_QUOTA_PER_UPLOAD   # = 6


def load_schedule() -> list[dict]:
    if not SCHEDULE_PATH.exists():
        raise RuntimeError(f"No existe {SCHEDULE_PATH}. Corre: python3 scripts/upload_schedule.py")
    with open(SCHEDULE_PATH) as f:
        data = json.load(f)
    return data.get("schedule", [])


def load_youtube_service():
    """Carga servicio autenticado de YouTube API."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "google-api-python-client no instalado.\n"
            "Run: .venv/bin/pip install google-api-python-client google-auth-oauthlib"
        )

    if not TOKEN_PATH.exists():
        raise RuntimeError(
            f"Token no existe en {TOKEN_PATH}.\n"
            "Run: python3 scripts/yt_auth.py"
        )

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        else:
            raise RuntimeError("Token vencido sin refresh_token. Run: python3 scripts/yt_auth.py")

    return build("youtube", "v3", credentials=creds)


def upload_video(youtube, entry: dict, dry_run: bool = False) -> str | None:
    """
    Sube un video a YouTube en modo private con publishAt.
    Retorna el videoId si OK, None si falla.
    """
    mp4 = Path(entry["mp4_path"])
    thumbnail = Path(entry["thumbnail_path"])
    description_file = Path(entry["description_path"])
    metadata_file = Path(entry["metadata_path"])

    if not mp4.exists():
        print(f"  ✗ MP4 no existe: {mp4}")
        return None

    metadata = json.load(open(metadata_file)) if metadata_file.exists() else {}
    description = description_file.read_text(encoding="utf-8") if description_file.exists() else ""

    title = metadata.get("title", entry["title"])
    tags = metadata.get("tags", [])
    publish_at = entry["publish_at_utc"]

    body = {
        "snippet": {
            "title":       title[:100],   # YT title limit 100
            "description": description[:5000],
            "tags":        tags[:500],
            "categoryId":  "22",   # People & Blogs (devotional)
            "defaultLanguage":      "es",
            "defaultAudioLanguage": "es-MX",
        },
        "status": {
            "privacyStatus":         "private",
            "publishAt":             publish_at,
            "selfDeclaredMadeForKids": False,
        },
    }

    if dry_run:
        print(f"  [DRY] Subiría: {title}")
        print(f"        Publica: {entry['publish_date']} {entry['publish_time_mty']} MTY")
        print(f"        MP4: {mp4.name} ({mp4.stat().st_size/1024/1024:.0f} MB)")
        return "dry-run-id"

    from googleapiclient.http import MediaFileUpload

    print(f"  📤 Subiendo: {title[:50]} ({mp4.stat().st_size/1024/1024:.0f} MB)...")
    media = MediaFileUpload(str(mp4), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"    Upload: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"  ✓ Subido: https://youtube.com/watch?v={video_id}")

    # Thumbnail
    if thumbnail.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail))
            ).execute()
            print(f"  ✓ Thumbnail asignado")
        except Exception as e:
            print(f"  ⚠ Thumbnail falló: {e}")

    return video_id


def mark_uploaded(story_id: str, video_id: str) -> None:
    """Actualiza catalog + schedule."""
    # Catalog
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)
    videos = catalog.get("videos", catalog) if isinstance(catalog, dict) else catalog
    for v in videos:
        if v["id"] == story_id:
            v.setdefault("status", {})["uploaded"] = True
            v["status"]["youtube_id"] = video_id
            v["status"]["youtube_url"] = f"https://youtube.com/watch?v={video_id}"
            v["status"]["upload_date"] = datetime.now().strftime("%Y-%m-%d")
            break
    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    # Schedule
    with open(SCHEDULE_PATH) as f:
        sched_data = json.load(f)
    for s in sched_data["schedule"]:
        if s["story_id"] == story_id:
            s["uploaded"] = True
            s["youtube_id"] = video_id
            break
    with open(SCHEDULE_PATH, "w") as f:
        json.dump(sched_data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=MAX_UPLOADS_PER_DAY,
                        help=f"Máximo uploads (default {MAX_UPLOADS_PER_DAY} = YT quota límite)")
    parser.add_argument("--story", help="Subir solo esta story_id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="Saltar confirmación (requerido en background/no-TTY)")
    args = parser.parse_args()

    schedule = load_schedule()

    # Double-check against catalog — never re-upload if catalog says uploaded
    catalog_uploaded: set[str] = set()
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH) as f:
            cat = json.load(f)
        vids = cat.get("videos", cat) if isinstance(cat, dict) else cat
        catalog_uploaded = {v["id"] for v in vids if v.get("status", {}).get("uploaded")}

    pending = [
        s for s in schedule
        if not s.get("uploaded") and s["story_id"] not in catalog_uploaded
    ]
    if catalog_uploaded:
        skipped = [s["story_id"] for s in schedule if s["story_id"] in catalog_uploaded]
        if skipped:
            print(f"  ⏭  Saltando {len(skipped)} ya subidos (catálogo): {', '.join(skipped[:4])}{'...' if len(skipped)>4 else ''}")

    if args.story:
        pending = [s for s in pending if s["story_id"] == args.story]
        if not pending:
            print(f"⚠ {args.story} no está en schedule o ya subido.")
            return

    pending = pending[:args.max]

    if not pending:
        print("✓ Nada pendiente de subir.")
        return

    print(f"\n{'='*65}")
    print(f"  UPLOAD QUEUE — {len(pending)} videos (max {args.max}/día por quota YT)")
    print(f"{'='*65}\n")

    for s in pending:
        print(f"  • {s['story_id']:<30s} → {s['publish_date']} {s['publish_time_mty']} MTY")
    print()

    if args.dry_run:
        print("[DRY RUN] — quita --dry-run para ejecutar.")
        return

    # Confirmar
    if args.yes:
        print(f"\n✓ --yes: confirmando upload de {len(pending)} videos.")
    elif not sys.stdin.isatty():
        print("✗ stdin no interactivo: usa --yes para confirmar el upload.")
        sys.exit(1)
    else:
        resp = input(f"\n¿Subir {len(pending)} videos? (y/N) ")
        if resp.lower() != "y":
            print("Cancelado.")
            return

    youtube = load_youtube_service()

    for i, s in enumerate(pending, 1):
        print(f"\n[{i}/{len(pending)}] {s['story_id']}")
        try:
            vid = upload_video(youtube, s, dry_run=args.dry_run)
            if vid:
                mark_uploaded(s["story_id"], vid)
        except Exception as e:
            print(f"  ✗ Fallo: {e}")
            continue

    print(f"\n{'='*65}")
    print(f"  UPLOAD COMPLETO — {len(pending)} videos procesados")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
