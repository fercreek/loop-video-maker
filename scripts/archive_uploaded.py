"""
archive_uploaded.py — Post-upload: archiva estado local de videos ya subidos.

Lee data/upload_schedule.json. Para cada entry con uploaded==true:
  - Mueve thumb + description + metadata de SUBIR/120min/ → SUBIDOS/120min/
  - (MP4 NO se mueve — queda en su carpeta de render original)
  - Acumula en output/SUBIDOS/_MANIFEST.json:
      tema, story_id, youtube_id, url, publish_date, publish_at_utc, archived_at

Idempotente: re-correr no duplica ni rompe (skip si ya archivado / archivo ausente).
NO toca YouTube. Solo filesystem local + manifest.

Uso:
    python3 scripts/archive_uploaded.py            # archiva todos los uploaded
    python3 scripts/archive_uploaded.py --dry-run  # muestra qué haría
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).parent.parent
SCHEDULE_PATH = PROJECT / "data" / "upload_schedule.json"
SUBIDOS_DIR = PROJECT / "output" / "SUBIDOS" / "120min"
MANIFEST_PATH = PROJECT / "output" / "SUBIDOS" / "_MANIFEST.json"


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"videos": []}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def move_if_exists(src: Path, dst_dir: Path, dry: bool) -> str | None:
    if not src.exists():
        return None
    dst = dst_dir / src.name
    if dst.exists():
        return str(dst)  # ya movido
    if dry:
        print(f"    [DRY] move {src.name} → {dst_dir}/")
        return str(dst)
    shutil.move(str(src), str(dst))
    return str(dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sched = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    manifest = load_manifest()
    known = {v["story_id"] for v in manifest["videos"]}

    if not args.dry_run:
        SUBIDOS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    archived = 0

    for s in sched["schedule"]:
        if not s.get("uploaded"):
            continue
        sid = s["story_id"]
        vid = s.get("youtube_id", "")

        # mover assets (mp4 NO)
        move_if_exists(Path(s["thumbnail_path"]), SUBIDOS_DIR, args.dry_run)
        new_desc = move_if_exists(Path(s["description_path"]), SUBIDOS_DIR, args.dry_run)
        new_meta = move_if_exists(Path(s["metadata_path"]), SUBIDOS_DIR, args.dry_run)

        if sid in known:
            print(f"  • {sid:22s} ya en manifest — assets sincronizados")
            continue

        entry = {
            "story_id": sid,
            "tema": sid.replace("paz120_", ""),
            "title": s["title"],
            "youtube_id": vid,
            "url": f"https://youtube.com/watch?v={vid}" if vid else "",
            "mp4_path": s["mp4_path"],  # queda en sitio original
            "publish_date": s["publish_date"],
            "publish_at_utc": s["publish_at_utc"],
            "status": "scheduled",  # private + publishAt → se vuelve public en la fecha
            "archived_at": now,
        }
        if not args.dry_run:
            manifest["videos"].append(entry)
        archived += 1
        print(f"  ✓ {sid:22s} → manifest  ({entry['url'] or 'sin id'})  publica {s['publish_date']}")

    if not args.dry_run:
        save_manifest(manifest)

    print(f"\n{'[DRY] ' if args.dry_run else ''}Archivados nuevos: {archived} · total en manifest: {len(manifest['videos'])}")
    print(f"Manifest → {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
