"""
_build_lofi_schedule.py — Genera description.txt + metadata.json individuales
para los 3 lofi 2h + escribe data/lofi_upload_schedule.json.

Fuente: output/lofi/youtube_metadata.json (títulos/desc/tags ya curados).
NO sube nada. Solo escribe archivos. Cadencia c/2 días, 9pm MTY (03:00 UTC+1d),
continuando tras el último 120min (10 jun) → 12/14/16 jun.

Orden por demanda SEO: dormir → ansiedad → orar.

Para activar el upload de lofi (cuando toque):
    cp data/lofi_upload_schedule.json data/upload_schedule.json   # tras archivar 120min
    echo "y" | python3 scripts/upload_to_youtube.py
"""
import json
from pathlib import Path

PROJECT = Path(__file__).parent.parent
LOFI_DIR = PROJECT / "output" / "lofi"
META_SRC = LOFI_DIR / "youtube_metadata.json"
OUT_DIR = LOFI_DIR / "upload"
SCHEDULE_PATH = PROJECT / "data" / "lofi_upload_schedule.json"

DISCLOSURE = "\n\nContenido creado con asistencia de IA 🙏"

# orden de publicación + asset real + thumb elegido + fecha
PLAN = [
    {"key": "lofi_v01_dormir",   "story_id": "lofi_dormir",
     "mp4": "lofi_v01_dormir_2h.mp4",     "thumb": "thumbs/thumb_v01_dormir_v3.jpg",
     "date": "2026-06-12", "utc": "2026-06-13T03:00:00Z"},
    {"key": "lofi_v03_ansiedad", "story_id": "lofi_ansiedad",
     "mp4": "lofi_v03_verses_final.mp4",  "thumb": "thumbs/lofi_v03_thumb.jpg",
     "date": "2026-06-14", "utc": "2026-06-15T03:00:00Z"},
    {"key": "lofi_v02_orar",     "story_id": "lofi_orar",
     "mp4": "lofi_v02_verses_final.mp4",  "thumb": "thumbs/lofi_v02_thumb.jpg",
     "date": "2026-06-16", "utc": "2026-06-17T03:00:00Z"},
]

src = json.loads(META_SRC.read_text(encoding="utf-8"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

schedule = []
for p in PLAN:
    m = src[p["key"]]
    desc = m["description"]
    if "asistencia de IA" not in desc:
        desc = desc + DISCLOSURE
    desc_path = OUT_DIR / f"{p['story_id']}_description.txt"
    meta_path = OUT_DIR / f"{p['story_id']}_metadata.json"
    desc_path.write_text(desc, encoding="utf-8")
    meta_path.write_text(json.dumps({"title": m["title"], "tags": m["tags"]}, ensure_ascii=False, indent=2), encoding="utf-8")

    mp4 = LOFI_DIR / p["mp4"]
    thumb = LOFI_DIR / p["thumb"]
    schedule.append({
        "story_id": p["story_id"],
        "title": m["title"],
        "mp4_path": str(mp4),
        "thumbnail_path": str(thumb),
        "description_path": str(desc_path),
        "metadata_path": str(meta_path),
        "publish_date": p["date"],
        "publish_time_mty": "21:00",
        "publish_at_utc": p["utc"],
        "uploaded": False,
    })

SCHEDULE_PATH.write_text(json.dumps({"schedule": schedule}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ 3 lofi desc+metadata → {OUT_DIR}")
print(f"✓ Schedule → {SCHEDULE_PATH}\n")
for p in PLAN:
    mp4 = LOFI_DIR / p["mp4"]; thumb = LOFI_DIR / p["thumb"]
    print(f"  {p['story_id']:14s} mp4={'OK' if mp4.exists() else 'FALTA'}  thumb={'OK' if thumb.exists() else 'FALTA'}  publica {p['date']}")
    print(f"     {src[p['key']]['title']}")
