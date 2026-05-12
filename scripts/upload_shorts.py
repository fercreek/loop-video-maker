#!/usr/bin/env python3
"""
scripts/upload_shorts.py — Sube Shorts aprobados desde data/shorts_review.json.

Shorts se publican inmediatamente (public). YouTube detecta 9:16 < 60s → Short.

Uso:
    python3 scripts/upload_shorts.py               # todos los approved
    python3 scripts/upload_shorts.py --id dormir   # uno específico
    python3 scripts/upload_shorts.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR   = Path(__file__).parent.parent
REVIEW_PATH   = PROJECT_DIR / "data" / "shorts_review.json"
REGISTRY_PATH = PROJECT_DIR / "data" / "content_registry.json"
TOKEN_PATH    = PROJECT_DIR / "data" / "yt_token.json"

# Tags para Shorts devocionales en español
BASE_TAGS = [
    "oración", "oraciones", "oración cristiana", "versículos bíblicos",
    "fe en dios", "dios te ama", "biblia", "shorts", "#shorts",
    "oración poderosa", "devocional", "palabra de dios"
]

TOPIC_TAGS = {
    "dormir":           ["oración para dormir", "dormir en paz", "noches de paz", "insomnio"],
    "ansiedad":         ["oración contra la ansiedad", "ansiedad y miedo", "paz interior"],
    "manana":           ["oración de la mañana", "buenos días señor", "oración matutina"],
    "tristeza":         ["oración para la tristeza", "cuando estás triste", "consolación"],
    "trabajo":          ["oración por el trabajo", "bendición laboral", "puertas abiertas"],
    "hijos":            ["oración por los hijos", "protección para mis hijos", "familia"],
    "milagro":          ["oración para un milagro", "fe para creer", "nada es imposible"],
    "corazon":          ["oración para sanar el corazón", "corazón roto", "sanación"],
    "tiempos_dificiles":["tiempos difíciles", "dios no te abandona", "fortaleza"],
    "soledad":          ["oración para la soledad", "solo y sin esperanza", "dios te acompaña"],
}

DESCRIPTION_TEMPLATE = """{titulo}

{texto}

━━━━━━━━━━━━━━━━━━━━
🙏 Comparte si Dios te habló hoy
✝️ Suscríbete para más oraciones y versículos
@VersiculoDeDios

#oración #fe #dios #biblia #versiculos #shorts
"""


def load_youtube():
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Error: pip install google-api-python-client google-auth-oauthlib")

    if not TOKEN_PATH.exists():
        sys.exit(f"Token no existe. Run: python3 scripts/yt_auth.py")

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        else:
            sys.exit("Token vencido. Run: python3 scripts/yt_auth.py")

    return build("youtube", "v3", credentials=creds)


def build_body(s: dict) -> dict:
    tema = s.get("tema", s["id"].split("_")[0])
    tags = BASE_TAGS + TOPIC_TAGS.get(s["id"].replace("_001", ""), [])
    # Pull texto from oraciones pool for description
    try:
        pool = json.loads((PROJECT_DIR / "data" / "oraciones_pool.json").read_text())
        oracion = next((o for o in pool if o["id"] == s["id"]), {})
        texto = oracion.get("texto", "")
    except Exception:
        texto = ""

    description = DESCRIPTION_TEMPLATE.format(
        titulo=s["titulo"], texto=texto[:800]
    ).strip()

    return {
        "snippet": {
            "title":       s["titulo"][:100],
            "description": description[:5000],
            "tags":        [t[:30] for t in tags[:500]],
            "categoryId":  "22",
            "defaultLanguage":      "es",
            "defaultAudioLanguage": "es-MX",
        },
        "status": {
            "privacyStatus":          "public",   # Immediate publish
            "selfDeclaredMadeForKids": False,
        },
    }


def upload_short(youtube, s: dict, dry_run: bool = False) -> str | None:
    mp4 = PROJECT_DIR / s["mp4"]
    thumb_path = PROJECT_DIR / s.get("thumb", "")

    if not mp4.exists():
        print(f"  ✗ MP4 no existe: {mp4}")
        return None

    size_mb = mp4.stat().st_size / 1024 / 1024
    body = build_body(s)
    title = body["snippet"]["title"]

    if dry_run:
        print(f"  [DRY] {s['id']} — {title[:50]} ({size_mb:.0f} MB)")
        return "dry-run-id"

    from googleapiclient.http import MediaFileUpload

    print(f"  📤 {s['id']} — {title[:50]} ({size_mb:.0f} MB)...")
    media = MediaFileUpload(str(mp4), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"    {pct}%", end="\r")

    video_id = response["id"]
    url = f"https://youtube.com/shorts/{video_id}"
    print(f"  ✓ https://youtube.com/shorts/{video_id}")

    # Thumbnail
    if thumb_path.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumb_path))
            ).execute()
        except Exception as e:
            print(f"  ⚠ Thumbnail: {e}")

    return video_id


def update_registry(short_id: str, video_id: str, s: dict):
    if not REGISTRY_PATH.exists():
        return
    registry = json.loads(REGISTRY_PATH.read_text())
    now = datetime.now().strftime("%Y-%m-%d")
    # Support both flat list and {content: [...]} formats
    entries = registry.get("content", registry) if isinstance(registry, dict) else registry
    for entry in entries:
        if not isinstance(entry, dict): continue
        if entry.get("id") == short_id:
            entry.setdefault("upload", {})
            entry["upload"]["youtube_id"]  = video_id
            entry["upload"]["youtube_url"] = f"https://youtube.com/shorts/{video_id}"
            entry["upload"]["upload_date"] = now
            entry["upload"]["status"]      = "live"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id",      action="append", help="ID específico (puede repetir)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not REVIEW_PATH.exists():
        sys.exit(f"No existe {REVIEW_PATH}. Haz el review primero.")

    data = json.loads(REVIEW_PATH.read_text())
    shorts = data.get("shorts", [])

    # Filter
    if args.id:
        targets = [s for s in shorts if s["id"] in args.id]
    else:
        targets = [s for s in shorts if s.get("status") == "approved"]

    if not targets:
        print("No hay shorts para subir.")
        return

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Subiendo {len(targets)} Short(s)...\n")

    youtube = None if args.dry_run else load_youtube()
    uploaded = []

    for i, s in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {s['id']}")
        vid_id = upload_short(youtube, s, dry_run=args.dry_run)
        if vid_id and not args.dry_run:
            update_registry(s["id"], vid_id, s)
            uploaded.append((s["id"], vid_id))
        print()

    print(f"\n{'─'*40}")
    if args.dry_run:
        print(f"Dry run: {len(targets)} short(s) listos para subir")
    else:
        print(f"✅ {len(uploaded)}/{len(targets)} subidos")
        for sid, vid in uploaded:
            print(f"   {sid} → https://youtube.com/shorts/{vid}")


if __name__ == "__main__":
    main()
