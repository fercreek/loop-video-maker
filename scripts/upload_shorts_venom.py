#!/usr/bin/env python3
"""
upload_shorts_scheduled.py — Sube Shorts a YouTube (private+publishAt) y Facebook (scheduled).

Un Short por día a las 5am MTY. Ambas plataformas, misma hora.

Uso:
    python3 scripts/upload_shorts_scheduled.py --dry-run    # ver plan
    python3 scripts/upload_shorts_scheduled.py              # subir todo

Requiere:
    data/yt_token.json
    /Users/fernandocastaneda/Documents/cero/cero-content/scripts/configs/tokens.json
"""
from __future__ import annotations

import argparse
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR   = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_DIR / "data" / "content_registry.json"
TOKEN_PATH    = PROJECT_DIR / "data" / "yt_token.json"
TOKENS_FILE   = Path("/Users/fernandocastaneda/Documents/cero/cero-content/scripts/configs/tokens.json")
SCHEDULE_PATH = PROJECT_DIR / "data" / "shorts_schedule.json"

FB_PAGE_ID    = "452922677899760"
MTY_OFFSET    = timedelta(hours=-6)
MTY_TZ        = timezone(MTY_OFFSET)

# Orden estratégico venom — replica bi_B78HZuJ4 (Reposo→Identidad/Libertad winners primero)
UPLOAD_ORDER = [
    "venom_001",  # Reposo (replica directa winner)
    "venom_004",  # Paz
    "venom_009",  # Miedo Vencido
    "venom_002",  # Nueva Criatura
    "venom_005",  # Refugio Salmo 91
    "venom_010",  # Ansiedad
    "venom_007",  # Sanación
    "venom_013",  # Gracia
    "venom_018",  # La Cruz
    "venom_006",  # Perdón
    "venom_014",  # Amor de Dios
    "venom_015",  # Fe que Mueve
    "venom_011",  # Propósito
    "venom_019",  # Resurrección Diaria
    "venom_008",  # Provisión
    "venom_003",  # Carga Ligera
    "venom_012",  # Esperanza
    "venom_016",  # Oración Real
    "venom_017",  # Espíritu Santo
    "venom_020",  # Familia Restaurada
]

BATCH_DIR = "semana_2026-05-25"  # venom batch folder

# Tags base para Shorts
BASE_TAGS = ["oración","oraciones","fe en dios","biblia","shorts","#shorts","versículos bíblicos","dios te ama"]
TOPIC_TAGS = {
    "tiempos_dificiles_001": ["tiempos difíciles","dios no te abandona","fortaleza en dios"],
    "dormir_001":            ["oración para dormir","dormir en paz","insomnio"],
    "ansiedad_001":          ["oración contra la ansiedad","paz interior","ansiedad y miedo"],
    "milagro_001":           ["oración para un milagro","nada es imposible para dios","fe para creer"],
    "manana_001":            ["oración de la mañana","buenos días señor","oración matutina"],
    "soledad_001":           ["oración para la soledad","dios te acompaña","solo y sin esperanza"],
    "hijos_001":             ["oración por los hijos","protección para mis hijos","familia cristiana"],
    "corazon_001":           ["oración para sanar el corazón","corazón roto","sanación"],
    "tristeza_001":          ["oración para la tristeza","cuando estás triste","consolación"],
    "trabajo_001":           ["oración por el trabajo","bendición laboral","puertas abiertas"],
}

DESCRIPTION_TEMPLATE = """{titulo}

{texto}

━━━━━━━━━━━━━━━━━━━━
🙏 Escribe AMÉN si esto te llegó al corazón
✝️ Suscríbete para más oraciones y versículos
@VersiculoDeDios

#oración #fe #dios #biblia #versiculos #shorts
"""


def build_schedule(start_date: datetime) -> list[dict]:
    """Genera el plan de publicación: 1 por día a las 5am MTY."""
    pool_data = json.loads((PROJECT_DIR / "data" / "oraciones_pool.json").read_text())
    pool = {o["id"]: o for o in pool_data.get("oraciones", [])}

    schedule = []
    for i, short_id in enumerate(UPLOAD_ORDER):
        pub_mty = datetime(
            start_date.year, start_date.month, start_date.day,
            5, 0, 0, tzinfo=MTY_TZ
        ) + timedelta(days=i)
        pub_utc = pub_mty.astimezone(timezone.utc)

        oracion = pool.get(short_id, {})
        mp4 = list((PROJECT_DIR / "output" / "shorts" / BATCH_DIR).glob(f"short_{short_id}_*.mp4"))

        schedule.append({
            "id":          short_id,
            "day":         i + 1,
            "titulo":      oracion.get("titulo", short_id),
            "hook":        oracion.get("hook", ""),
            "texto":       oracion.get("texto", ""),
            "mp4":         str(mp4[0]) if mp4 else None,
            "thumb":       str(PROJECT_DIR / "output" / "shorts" / BATCH_DIR / "thumbs" / f"{short_id}.jpg"),
            "publish_mty": pub_mty.strftime("%Y-%m-%d %H:%M MTY"),
            "publish_utc": pub_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "publish_ts":  int(pub_utc.timestamp()),
            "yt_id":       None,
            "fb_id":       None,
            "status":      "pending",
        })
    return schedule


# ── YouTube ──────────────────────────────────────────────────────────────────

def load_youtube():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if not creds.valid and creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload_youtube(youtube, entry: dict, dry_run: bool) -> str | None:
    mp4 = Path(entry["mp4"])
    if not mp4.exists():
        print(f"    ✗ MP4 no existe: {mp4.name}")
        return None

    tags = BASE_TAGS + TOPIC_TAGS.get(entry["id"], [])
    description = DESCRIPTION_TEMPLATE.format(
        titulo=entry["titulo"], texto=entry["texto"][:800]
    ).strip()

    body = {
        "snippet": {
            "title":       entry["titulo"][:100],
            "description": description[:5000],
            "tags":        tags,
            "categoryId":  "22",
            "defaultLanguage":      "es",
            "defaultAudioLanguage": "es-MX",
        },
        "status": {
            "privacyStatus":          "private",
            "publishAt":              entry["publish_utc"],
            "selfDeclaredMadeForKids": False,
        },
    }

    if dry_run:
        print(f"    [YT DRY] private → publica {entry['publish_mty']}")
        return "dry-yt-id"

    from googleapiclient.http import MediaFileUpload
    print(f"    📤 YouTube: {mp4.name} ({mp4.stat().st_size/1024/1024:.0f}MB)...")
    media = MediaFileUpload(str(mp4), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status: print(f"      {int(status.progress()*100)}%", end="\r")

    video_id = response["id"]
    print(f"    ✓ YT: https://youtube.com/shorts/{video_id} → publica {entry['publish_mty']}")

    # Thumbnail
    thumb = Path(entry["thumb"])
    if thumb.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumb))
            ).execute()
        except Exception as e:
            print(f"    ⚠ Thumbnail YT: {e}")

    return video_id


# ── Facebook ─────────────────────────────────────────────────────────────────

def get_fb_token() -> str:
    tokens = json.loads(TOKENS_FILE.read_text())
    return tokens["palabra-de-dios"]


def upload_facebook(entry: dict, dry_run: bool) -> str | None:
    """
    Sube video a Facebook Page programado.
    Usa /{page-id}/videos con scheduled_publish_time.
    Facebook detecta 9:16 vertical automáticamente como Reel.
    """
    mp4 = Path(entry["mp4"])
    if not mp4.exists():
        print(f"    ✗ MP4 no existe para FB: {mp4.name}")
        return None

    token    = get_fb_token()
    pub_ts   = entry["publish_ts"]
    # FB requiere: mínimo 10 min en el futuro, máximo 30 días
    # IMPORTANTE: si pub_ts pasó, calcular desde el día siguiente al último video programado
    # (nunca agrupar múltiples videos en el mismo día vía API)
    now_ts   = int(datetime.now(timezone.utc).timestamp())
    if pub_ts < now_ts + 600:
        # Calcular cuántos videos de este batch ya tienen fb_id en el schedule
        try:
            sched = json.loads((PROJECT_DIR / "data" / "shorts_schedule.json").read_text())
            entries_done = [e for e in sched.get("schedule", []) if e.get("fb_id") and e["fb_id"] not in (None, "dry-fb-id")]
            # 1 día por video ya programado, +1 para este
            days_offset = len(entries_done) + 1
        except Exception:
            days_offset = 1
        # Publicar a las 5am MTY del día correspondiente
        base = datetime.now(MTY_TZ).replace(hour=5, minute=0, second=0, microsecond=0)
        if base.timestamp() < now_ts:
            base = base + timedelta(days=1)
        pub_ts = int((base + timedelta(days=days_offset - 1)).timestamp())

    description = (
        f"{entry['titulo']}\n\n"
        f"{entry['hook']}\n\n"
        f"🙏 Escribe AMÉN si esto te llegó al corazón\n"
        f"✝️ Síguenos para más oraciones diarias\n\n"
        f"#oración #fe #dios #biblia #versiculos #reels"
    )

    if dry_run:
        print(f"    [FB DRY] Video programado → {entry['publish_mty']}")
        return "dry-fb-id"

    print(f"    📤 Facebook: {mp4.name} ({mp4.stat().st_size/1024/1024:.0f}MB)...")

    url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/videos"
    with open(mp4, "rb") as f:
        resp = requests.post(url, data={
            "access_token":           token,
            "description":            description,
            "title":                  entry["titulo"][:255],
            "published":              "false",
            "scheduled_publish_time": str(pub_ts),
        }, files={"source": (mp4.name, f, "video/mp4")})

    data = resp.json()
    if "id" in data:
        vid_id = data["id"]
        print(f"    ✓ FB: {vid_id} → publica {entry['publish_mty']}")
        return vid_id
    else:
        err = data.get("error", {}).get("message", str(data))
        print(f"    ✗ FB error: {err}")
        return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run",    action="store_true")
    ap.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: tomorrow)")
    ap.add_argument("--only-yt",    action="store_true", help="Solo YouTube")
    ap.add_argument("--only-fb",    action="store_true", help="Solo Facebook")
    args = ap.parse_args()

    # Start date
    if args.start_date:
        start = datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        tomorrow = datetime.now(MTY_TZ) + timedelta(days=1)
        start = tomorrow

    schedule = build_schedule(start)

    mode = "DRY RUN" if args.dry_run else "SUBIENDO"
    print(f"\n{'─'*50}")
    print(f"  {mode} — {len(schedule)} Shorts · 1/día · 5am MTY")
    print(f"  {start.strftime('%Y-%m-%d')} → {(start + timedelta(days=9)).strftime('%Y-%m-%d')}")
    print(f"{'─'*50}\n")

    youtube = None
    if not args.only_fb and not args.dry_run:
        youtube = load_youtube()

    # Load existing schedule to skip already-uploaded items
    already_uploaded_yt = set()
    already_uploaded_fb = set()
    if SCHEDULE_PATH.exists() and not args.dry_run:
        try:
            prev = json.loads(SCHEDULE_PATH.read_text())
            for s in prev.get("schedule", []):
                if s.get("yt_id") and s["yt_id"] != "dry-yt-id":
                    already_uploaded_yt.add(s["id"])
                if s.get("fb_id"):
                    already_uploaded_fb.add(s["id"])
            if already_uploaded_yt or already_uploaded_fb:
                print(f"📋 Re-correr: skip {len(already_uploaded_yt)} YT + {len(already_uploaded_fb)} FB ya subidos\n")
        except Exception:
            pass

    results = []
    total = len(schedule)
    for entry in schedule:
        print(f"[{entry['day']:2}/{total}] {entry['id']}")
        print(f"       {entry['publish_mty']}")

        yt_id, fb_id = None, None

        if not args.only_fb:
            if entry["id"] in already_uploaded_yt:
                print(f"    ⏭  YT ya subido — skip")
                yt_id = "previously-uploaded"
            else:
                try:
                    yt_id = upload_youtube(youtube, entry, args.dry_run)
                    if not args.dry_run:
                        time.sleep(2)
                except Exception as e:
                    msg = str(e)[:200]
                    print(f"    ✗ YT error: {msg}")
                    if "quotaExceeded" in msg or "rateLimitExceeded" in msg:
                        print(f"    ⚠ YT quota daily exceeded — re-corre mañana")
            entry["yt_id"] = yt_id

        if not args.only_yt:
            if entry["id"] in already_uploaded_fb:
                print(f"    ⏭  FB ya subido — skip")
                fb_id = "previously-uploaded"
            else:
                try:
                    fb_id = upload_facebook(entry, args.dry_run)
                except Exception as e:
                    print(f"    ✗ FB error: {str(e)[:200]}")
            entry["fb_id"] = fb_id

        entry["status"] = "scheduled" if (yt_id or fb_id or args.dry_run) else "failed"
        results.append(entry)
        print()

    # DRY-RUN: NO sobrescribir schedule real (preserva yt_id/fb_id reales)
    if args.dry_run:
        print(f"{'─'*50}")
        print(f"✅ DRY RUN — {len(results)} entries · no se modifica {SCHEDULE_PATH.name}")
        return

    # Merge with prior schedule (preserve already-uploaded IDs)
    SCHEDULE_PATH.parent.mkdir(exist_ok=True)
    if SCHEDULE_PATH.exists() and not args.dry_run:
        try:
            prev = json.loads(SCHEDULE_PATH.read_text())
            prev_map = {s["id"]: s for s in prev.get("schedule", [])}
            for r in results:
                p = prev_map.get(r["id"], {})
                if p.get("yt_id") and r["yt_id"] in (None, "previously-uploaded"):
                    r["yt_id"] = p["yt_id"]
                if p.get("fb_id") and r["fb_id"] in (None, "previously-uploaded"):
                    r["fb_id"] = p["fb_id"]
        except Exception:
            pass

    SCHEDULE_PATH.write_text(json.dumps({
        "batch":      "venom_2026-05-25",
        "created":    datetime.now().isoformat(),
        "dry_run":    args.dry_run,
        "schedule":   results,
    }, ensure_ascii=False, indent=2))

    yt_ok = sum(1 for r in results if r.get("yt_id"))
    fb_ok = sum(1 for r in results if r.get("fb_id"))
    total = len(results)
    print(f"{'─'*50}")
    print(f"✅ YT: {yt_ok}/{total} programados · FB: {fb_ok}/{total} programados")
    print(f"   Plan guardado: {SCHEDULE_PATH}")
    if not args.dry_run:
        last_date = max(r["publish_mty"][:10] for r in results)
        print(f"\n   YouTube publica entre {start.strftime('%Y-%m-%d')} y {last_date} a las 5am MTY")
        print(f"   Facebook igual — revisa Meta Business Suite para confirmar")
        if yt_ok < total or fb_ok < total:
            print(f"\n   ⚠ Pendientes: re-corre mañana para los faltantes (skip auto los OK)")


if __name__ == "__main__":
    main()
