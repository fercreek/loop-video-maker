#!/usr/bin/env python3
"""
upload_reels_batch_v2.py — Sube reels/Shorts a YouTube (private + publishAt) con anti-dup real.

Evolución de upload_reels_batch.py. Diferencias:
  - --semana configurable (no hardcoded a semana_2026-06-19).
  - Anti-dup PERSISTENTE: registro acumulativo data/reels_uploaded.json (id → yt_id).
    Re-correr el script SALTA los ids ya subidos. Cero duplicados.
  - pool.get() seguro: si un id no está en oraciones_pool.json, avisa y lo salta (no truena).

FB/IG NO se tocan — los crea n8n `vdd-short-to-3` al publicarse el Short en YT.

Uso:
    python3 scripts/upload_reels_batch_v2.py --semana semana_2026-06-22 --dry-run
    python3 scripts/upload_reels_batch_v2.py --semana semana_2026-06-22
    python3 scripts/upload_reels_batch_v2.py --semana semana_2026-06-22 --force   # ignora anti-dup
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR    = Path(__file__).parent.parent
TOKEN_PATH     = PROJECT_DIR / "data" / "yt_token.json"
POOL_PATH      = PROJECT_DIR / "data" / "oraciones_pool.json"
SHORTS_DIR     = PROJECT_DIR / "output" / "shorts"
UPLOADED_PATH  = PROJECT_DIR / "data" / "reels_uploaded.json"   # registro anti-dup acumulativo

MTY_TZ = timezone(timedelta(hours=-6))

# ── Calendario del batch — EDITA AQUÍ cada vez ────────────────────────────────
# 1/día. hora fija (HORA_MTY). hooks más fuertes primero.
HORA_MTY = 9   # 9am MTY
BATCH = [
    {"id": "fe_001",        "date": "2026-06-23"},
    {"id": "esperanza_001", "date": "2026-06-24"},
    {"id": "gratitud_001",  "date": "2026-06-25"},
]
# ──────────────────────────────────────────────────────────────────────────────

BASE_TAGS  = ["oración", "oraciones", "fe en dios", "biblia", "shorts", "#shorts",
              "versículos bíblicos", "dios te ama"]
# Tags por id — si falta, solo usa BASE_TAGS.
TOPIC_TAGS = {
    "fe_001":        ["oración de fe", "creer en dios", "fe que mueve montañas"],
    "esperanza_001": ["oración de esperanza", "no pierdas la esperanza", "dios tiene un plan"],
    "gratitud_001":  ["oración de gratitud", "gracias dios", "corazón agradecido"],
    "milagro_001":   ["oración para un milagro", "nada es imposible para dios", "fe para creer"],
    "soledad_001":   ["oración para la soledad", "dios te acompaña", "solo y sin esperanza"],
    "tristeza_001":  ["oración para la tristeza", "cuando estás triste", "consolación"],
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


def load_uploaded() -> dict:
    """Registro acumulativo {id: yt_id} de lo ya subido (anti-dup)."""
    if UPLOADED_PATH.exists():
        return json.loads(UPLOADED_PATH.read_text())
    return {}


def save_uploaded(reg: dict):
    UPLOADED_PATH.write_text(json.dumps(reg, ensure_ascii=False, indent=2))


def build_entries(semana: str) -> list[dict]:
    pool = {o["id"]: o for o in json.loads(POOL_PATH.read_text())["oraciones"]}
    semana_dir = SHORTS_DIR / semana
    entries = []
    for item in BATCH:
        oid = item["id"]
        o = pool.get(oid)
        if o is None:
            print(f"    ⚠ id '{oid}' no está en oraciones_pool.json — se salta.")
            continue
        y, m, d = (int(x) for x in item["date"].split("-"))
        pub_mty = datetime(y, m, d, HORA_MTY, 0, 0, tzinfo=MTY_TZ)
        pub_utc = pub_mty.astimezone(timezone.utc)
        mp4s = sorted(semana_dir.glob(f"short_{oid}_*.mp4"))
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
        print(f"    ✗ MP4 no existe para {entry['id']} ({entry['mp4']})")
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
    ap.add_argument("--semana",  default="semana_2026-06-22", help="carpeta en output/shorts/")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force",   action="store_true", help="ignora anti-dup, re-sube todo")
    args = ap.parse_args()

    entries  = build_entries(args.semana)
    uploaded = load_uploaded()

    print(f"\n{'='*60}\n  BATCH REELS · {args.semana} → YouTube (private+publishAt)\n{'='*60}")
    for e in entries:
        dup = (not args.force) and uploaded.get(e["id"])
        flag = "OK" if e["mp4"] else "SIN MP4"
        if dup:
            flag = f"YA SUBIDO ({dup}) → SKIP"
        print(f"  · {e['id']:16s} {e['publish_mty']}  {flag}")
    print()

    youtube = None if args.dry_run else load_youtube()
    results = {}
    for e in entries:
        if (not args.force) and uploaded.get(e["id"]):
            results[e["id"]] = uploaded[e["id"]]   # ya estaba, no re-subir
            continue
        vid = upload_one(youtube, e, args.dry_run)
        results[e["id"]] = vid
        # Persistir inmediato (sobrevive crash a media subida)
        if vid and vid != "dry-id":
            uploaded[e["id"]] = vid
            save_uploaded(uploaded)

    # Registro del batch (compat con formato viejo)
    out = PROJECT_DIR / "data" / f"reels_batch_{args.semana}.json"
    out.write_text(json.dumps({"entries": entries, "yt_ids": results}, ensure_ascii=False, indent=2))
    print(f"\n  Registro batch → {out.relative_to(PROJECT_DIR)}")
    print(f"  Registro anti-dup → {UPLOADED_PATH.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
