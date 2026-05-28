#!/usr/bin/env python3
"""
scripts/upload_lofi_batch.py — Sube batch lo-fi a YouTube con scheduled publish.

Uso:
    .venv/bin/python3 scripts/upload_lofi_batch.py --video v02   # sube v02 ahora público
    .venv/bin/python3 scripts/upload_lofi_batch.py --video v03   # sube v03 scheduled 5am May 29
    .venv/bin/python3 scripts/upload_lofi_batch.py --video v01   # sube v01 scheduled 5am May 30
    .venv/bin/python3 scripts/upload_lofi_batch.py --dry-run
"""
import argparse, json, os, sys, time
from pathlib import Path

PROJECT = Path(__file__).parent.parent
SCHEDULE = json.load(open(PROJECT / "data/lofi_upload_schedule.json"))["schedule"]

def get_entry(video_id):
    for v in SCHEDULE:
        if video_id in v["id"]:
            return v
    raise ValueError(f"No encontrado: {video_id}")

def load_yt():
    sys.path.insert(0, str(PROJECT))
    from core.youtube_client import _youtube
    return _youtube()

def upload_video(entry, publish_now=False, dry_run=False):
    file_path = PROJECT / entry["file"]
    thumb_path = PROJECT / entry["thumbnail"]

    if not file_path.exists():
        print(f"❌ Archivo no existe: {file_path}")
        return None

    print(f"\n📤 Subiendo: {entry['title'][:60]}")
    print(f"   Archivo: {file_path} ({file_path.stat().st_size/1024/1024:.0f}MB)")
    print(f"   Thumbnail: {thumb_path}")
    print(f"   Publish: {'AHORA' if publish_now else entry['publish_at']}")

    if dry_run:
        print("   [DRY RUN] No se subió nada")
        return "dry_run"

    yt = load_yt()

    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {
            "title": entry["title"],
            "description": entry["description"],
            "tags": entry["tags"],
            "categoryId": entry["category_id"],
            "defaultLanguage": "es",
        },
        "status": {
            "privacyStatus": "public" if publish_now else "private",
            "selfDeclaredMadeForKids": False,
        }
    }

    if not publish_now and entry.get("publish_at"):
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = entry["publish_at"]

    media = MediaFileUpload(str(file_path), mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    print("   Subiendo", end="", flush=True)
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"\r   Subiendo {pct}%   ", end="", flush=True)
    print()

    video_id = response["id"]
    print(f"   ✅ Video ID: {video_id}")
    print(f"   🔗 https://youtu.be/{video_id}")

    # Thumbnail
    if thumb_path.exists():
        try:
            from googleapiclient.http import MediaFileUpload as MFU
            yt.thumbnails().set(
                videoId=video_id,
                media_body=MFU(str(thumb_path), mimetype="image/jpeg")
            ).execute()
            print("   ✅ Thumbnail subido")
        except Exception as e:
            print(f"   ⚠️  Thumbnail failed: {e}")

    # Save result
    entry["video_id"] = video_id
    entry["status"] = "uploaded"
    json.dump({"batch":"lofi_batch_v1","schedule":SCHEDULE},
              open(PROJECT/"data/lofi_upload_schedule.json","w"), indent=2, ensure_ascii=False)

    return video_id

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="v01 | v02 | v03")
    ap.add_argument("--now", action="store_true", help="Publicar inmediato (sin schedule)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    entry = get_entry(args.video)
    upload_video(entry, publish_now=args.now, dry_run=args.dry_run)
