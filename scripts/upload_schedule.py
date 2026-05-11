"""
scripts/upload_schedule.py — Genera calendario de subida YouTube.

Lee videos rendereados sin subir → asigna fecha + hora óptima (6pm MTY).
Genera `data/upload_schedule.json` con plan completo.

YouTube Data API v3: 1,600 quota/upload, daily cap 10,000 → MAX 6 uploads/día.
Recomendación: 1 video/día (algorithm-friendly), schedule mode `private` + publishAt.

Uso:
    python3 scripts/upload_schedule.py                    # genera schedule
    python3 scripts/upload_schedule.py --start 2026-05-11 # fecha de inicio
    python3 scripts/upload_schedule.py --per-day 1        # videos/día (default 1)
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_DIR  = Path(__file__).parent.parent
CATALOG_PATH = PROJECT_DIR / "data" / "video_catalog.json"
SCHEDULE_OUT = PROJECT_DIR / "data" / "upload_schedule.json"
OUTPUT_BASE  = PROJECT_DIR / "output" / "stories"

# Schedule config (Mexico City timezone UTC-6)
UPLOAD_HOUR_MTY  = 18    # 6pm MTY (peak devotional engagement)
UPLOAD_MIN       = 0
UPLOAD_TZ_OFFSET = -6    # UTC-6

# Días de la semana óptimos por venom analytics
PREFERRED_DAYS = [3, 4, 5, 0, 6]  # jue, vie, sab, lun, dom (mié/mar evitados)


def load_catalog() -> dict:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_schedule(schedule: list[dict]) -> None:
    SCHEDULE_OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "channel": "@VersiculoDeDios",
        "total_videos": len(schedule),
        "schedule": schedule,
    }
    with open(SCHEDULE_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_ready_videos(catalog: dict) -> list[dict]:
    """Videos rendereados sin subir, ordenados por prioridad."""
    videos = catalog.get("videos", catalog) if isinstance(catalog, dict) else catalog
    ready = []
    for v in videos:
        status = v.get("status", {})
        if status.get("rendered") and not status.get("uploaded"):
            # Verificar MP4 existe físicamente
            mp4 = OUTPUT_BASE / v["id"] / f"{v['id']}.mp4"
            if mp4.exists():
                ready.append(v)
    ready.sort(key=lambda v: (v.get("priority", 3), v.get("id", "")))
    return ready


def next_publish_date(after: datetime, used_dates: set[str]) -> datetime:
    """Busca siguiente fecha disponible, prefiriendo PREFERRED_DAYS."""
    candidate = after + timedelta(days=1)
    for _ in range(30):  # buscar hasta 30 días adelante
        date_str = candidate.strftime("%Y-%m-%d")
        if candidate.weekday() in PREFERRED_DAYS and date_str not in used_dates:
            return candidate
        candidate += timedelta(days=1)
    return candidate  # fallback


def build_schedule(ready: list[dict], start_date: datetime, per_day: int = 1) -> list[dict]:
    """
    Asigna fechas de publicación.
    Estrategia: 1 video/día en días preferidos (jue/vie/sab/lun/dom).
    """
    schedule: list[dict] = []
    used_dates: set[str] = set()
    current = start_date - timedelta(days=1)   # se incrementa antes del primer asignamiento

    for v in ready:
        story_id = v["id"]
        story_out = OUTPUT_BASE / story_id

        # Calcular siguiente fecha
        current = next_publish_date(current, used_dates)
        used_dates.add(current.strftime("%Y-%m-%d"))

        # Hora 6pm MTY (UTC-6) → 00:00 UTC del día siguiente
        utc_hour = (UPLOAD_HOUR_MTY - UPLOAD_TZ_OFFSET) % 24   # 18-(-6)=24 → 0
        utc_day_offset = (UPLOAD_HOUR_MTY - UPLOAD_TZ_OFFSET) // 24   # +1
        publish_dt = (current + timedelta(days=utc_day_offset)).replace(
            hour=utc_hour,
            minute=UPLOAD_MIN,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )

        # Cargar metadata generada
        meta_path = story_out / "yt_metadata.json"
        title = v["title"]
        chapters_count = 0
        if meta_path.exists():
            try:
                meta = json.load(open(meta_path))
                title = meta.get("title", title)
                chapters_count = len(meta.get("chapters", []))
            except Exception:
                pass

        entry = {
            "story_id":         story_id,
            "title":            title,
            "publish_date":     current.strftime("%Y-%m-%d"),
            "publish_day":      ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"][current.weekday()],
            "publish_time_mty": f"{UPLOAD_HOUR_MTY:02d}:{UPLOAD_MIN:02d}",
            "publish_at_utc":   publish_dt.isoformat(),
            "mp4_path":         str(story_out / f"{story_id}.mp4"),
            "thumbnail_path":   str(story_out / "thumbnail.jpg"),
            "description_path": str(story_out / "yt_description.txt"),
            "metadata_path":    str(story_out / "yt_metadata.json"),
            "chapters_count":   chapters_count,
            "priority":         v.get("priority", 3),
            "uploaded":         False,
        }
        schedule.append(entry)

    return schedule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help="Fecha inicio YYYY-MM-DD (default: hoy)")
    parser.add_argument("--per-day", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.start:
        start = datetime.strptime(args.start, "%Y-%m-%d")
    else:
        start = datetime.now()

    catalog = load_catalog()
    ready = get_ready_videos(catalog)

    if not ready:
        print("⚠ No hay videos rendereados sin subir.")
        return

    schedule = build_schedule(ready, start, per_day=args.per_day)

    print(f"\n{'='*70}")
    print(f"  UPLOAD SCHEDULE — {len(schedule)} videos")
    print(f"  Hora: {UPLOAD_HOUR_MTY:02d}:00 MTY (6pm pico devocional)")
    print(f"  Días preferidos: jue, vie, sáb, lun, dom")
    print(f"{'='*70}\n")

    for s in schedule:
        flag = "🔴" if s["priority"] == 1 else "🟡" if s["priority"] == 2 else "🟢"
        print(f"  {s['publish_date']} ({s['publish_day']}) {s['publish_time_mty']} MTY  "
              f"{flag} P{s['priority']}  {s['story_id'][:30]:<30s}  {s['title'][:50]}")

    if not args.dry_run:
        save_schedule(schedule)
        print(f"\n✓ Schedule guardado en: {SCHEDULE_OUT}")
    else:
        print(f"\n[DRY RUN] No se guardó. Quita --dry-run para persistir.")


if __name__ == "__main__":
    main()
