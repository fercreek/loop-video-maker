#!/usr/bin/env python3
"""
upload_reels_batch.py — Sube un batch puntual de Shorts a YouTube (private + publishAt).

A diferencia de upload_shorts_scheduled.py (orden fijo de 10, path batch_v6, 5am, +FB),
este sube SOLO los IDs/archivos que se le pasan, 1/día a la hora indicada, YT-only.
FB/IG los crea n8n `vdd-short-to-3` automáticamente al publicarse el Short en YT.

Uso:
    python3 scripts/upload_reels_batch.py --dry-run
    python3 scripts/upload_reels_batch.py
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
TOKEN_PATH  = PROJECT_DIR / "data" / "yt_token.json"
POOL_PATH   = PROJECT_DIR / "data" / "oraciones_pool.json"
SEMANA_DIR  = PROJECT_DIR / "output" / "shorts" / "semana_2026-06-19"

MTY_TZ = timezone(timedelta(hours=-6))

# Batch 2026-06-19 — fórmula LLAMA DIVINA (hook-pregunta + CTA funnel → sleep).
# 1/día, 9am MTY, hooks más fuertes primero.
BATCH = [
    {"id": "milagro_001",  "date": "2026-06-20"},
    {"id": "soledad_001",  "date": "2026-06-21"},
    {"id": "tristeza_001", "date": "2026-06-22"},
]

BASE_TAGS  = ["oración", "oraciones", "fe en dios", "biblia", "shorts", "#shorts",
             "versículos bíblicos", "dios te ama"]
TOPIC_TAGS = {
    "milagro_001":  ["oración para un milagro", "nada es imposible para dios", "fe para creer"],
    "soledad_001":  ["oración para la soledad", "dios te acompaña", "solo y sin esperanza"],
    "tristeza_001": ["oración para la tristeza", "cuando estás triste", "consolación"],
}

# Guardrail anti-AI-slop: disclosure IA obligatorio en descripción.
DESCRIPTION_TEMPLATE = """{titulo}

{texto}

━━━━━━━━━━━━━━━━━━━━
🌙 Ve el video completo para dormir en el primer comentario fijado
🙏 Escribe AMÉN si esto te llegó al corazón
✝️ Suscríbete para más oraciones y versículos
@VersiculoDeDios

Contenido creado con asistencia de IA 🙏

#oración #fe #dios #biblia #versiculos #shorts
"""


def load_youtube():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def build_entries() -> list[dict]:
    pool = {o["id"]: o for o in json.loads(POOL_PATH.read_text())["oraciones"]}
    entries = []
    for item in BATCH:
        oid = item["id"]
        o = pool[oid]
        y, m, d = (int(x) for x in item["date"].split("-"))
        pub_mty = datetime(y, m, d, 9, 0, 0, tzinfo=MTY_TZ)
        pub_utc = pub_mty.astimezone(timezone.utc)
        mp4s = sorted(SEMANA_DIR.glob(f"short_{oid}_*.mp4"))
        entries.append({
            "id":          oid,
            "titulo":      o["titulo"],
            "texto":       o["texto"],
            "mp4":         str(mp4s[0]) if mp4s else None,
            "publish_mty": pub_mty.strftime("%Y-%m-%d %H:%M MTY"),
            "publish_utc": pub_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    return entries


def upload_one(youtube, entry: dict, dry_run: bool) -> str | None:
    mp4 = Path(entry["mp4"]) if entry["mp4"] else None
    if not mp4 or not mp4.exists():
        print(f"    ✗ MP4 no existe para {entry['id']}")
        return None

    tags = BASE_TAGS + TOPIC_TAGS.get(entry["id"], [])
    description = DESCRIPTION_TEMPLATE.format(
        titulo=entry["titulo"], texto=entry["texto"][:800]
    ).strip()
    body = {
        "snippet": {
            "title":                entry["titulo"][:100],
            "description":          description[:5000],
            "tags":                 tags,
            "categoryId":           "22",
            "defaultLanguage":      "es",
            "defaultAudioLanguage": "es-MX",
        },
        "status": {
            "privacyStatus":           "private",
            "publishAt":               entry["publish_utc"],
            "selfDeclaredMadeForKids": False,
        },
    }

    if dry_run:
        print(f"    [DRY] {entry['id']}: {mp4.name} → private, publica {entry['publish_mty']}")
        return "dry-id"

    from googleapiclient.http import MediaFileUpload
    print(f"    📤 {entry['id']}: {mp4.name} ({mp4.stat().st_size/1024/1024:.0f}MB)...")
    media = MediaFileUpload(str(mp4), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"      {int(status.progress()*100)}%", end="\r")
    vid = response["id"]
    print(f"    ✓ https://youtube.com/shorts/{vid} → publica {entry['publish_mty']}")
    return vid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    entries = build_entries()
    print(f"\n{'='*60}\n  BATCH REELS 2026-06-19 → YouTube (private+publishAt)\n{'='*60}")
    for e in entries:
        print(f"  · {e['id']:14s} {e['publish_mty']}  {'OK' if e['mp4'] else 'SIN MP4'}")
    print()

    youtube = None if args.dry_run else load_youtube()
    results = {}
    for e in entries:
        vid = upload_one(youtube, e, args.dry_run)
        results[e["id"]] = vid

    out = PROJECT_DIR / "data" / "reels_batch_2026-06-19.json"
    out.write_text(json.dumps({"entries": entries, "yt_ids": results}, ensure_ascii=False, indent=2))
    print(f"\n  Registro → {out.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
