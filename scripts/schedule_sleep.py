"""
schedule_sleep.py — agrega un video SLEEP (output/sleep/*.mp4) a data/upload_schedule.json
para que upload_to_youtube.py lo programe por API (publishAt). Cierra BUG-4: los sleeps
no estaban en el catálogo de stories y el uploader los ignoraba.

Genera: thumbnail (frame del mp4) + descripción (template sleep) + metadata mínima.
Valida integridad con el gate ffprobe (no agenda un render incompleto).

Uso:
  .venv/bin/python3 scripts/schedule_sleep.py \
     --mp4 output/sleep/sleep_salmo91_120min.mp4 \
     --title "SALMO 91 PARA DORMIR TODA LA NOCHE 2026 · Protección y Paz" \
     --date 2026-06-28 --hora 21
"""
import argparse, json, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# venv-guard
import os as _os
_vpy = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), ".venv", "bin", "python3")
if _os.path.exists(_vpy) and _os.path.realpath(sys.executable) != _os.path.realpath(_vpy):
    _os.execv(_vpy, [_vpy] + sys.argv)

PROJECT_DIR = Path(__file__).parent.parent
SCHEDULE = PROJECT_DIR / "data" / "upload_schedule.json"
MTY = timezone(timedelta(hours=-6))
sys.path.insert(0, str(PROJECT_DIR / "scripts"))
from _mp4_ok import valid_mp4

DESC_TEMPLATE = """{title}

Deja sonar este video toda la noche y descansa en la presencia de Dios, cubierto bajo Su sombra.

"El que habita al abrigo del Altísimo morará bajo la sombra del Omnipotente" — Salmo 91:1, Reina-Valera 1960

🙏 Antes de dormir, déjanos un Amén en los comentarios.
🔔 Suscríbete para nuevos videos para dormir y descansar en Dios cada semana.
@VersiculoDeDios
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp4", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--hora", type=int, default=21, help="hora MTY (default 21 = 🌙 noche)")
    ap.add_argument("--desc-file", default=None)
    args = ap.parse_args()

    mp4 = (PROJECT_DIR / args.mp4) if not Path(args.mp4).is_absolute() else Path(args.mp4)
    if not valid_mp4(mp4):
        print(f"⛔ {mp4.name} no es un MP4 válido/completo — no se agenda (¿sigue renderizando?).")
        sys.exit(1)

    sid = mp4.stem
    out_dir = mp4.parent

    # 1) thumbnail: frame a los 8s
    thumb = out_dir / f"{sid}_thumb.jpg"
    subprocess.run(["ffmpeg", "-y", "-ss", "8", "-i", str(mp4), "-frames:v", "1",
                    "-vf", "scale=1280:720", str(thumb)], capture_output=True)

    # 2) descripción + metadata
    desc = Path(args.desc_file).read_text() if args.desc_file else DESC_TEMPLATE.format(title=args.title)
    desc_path = out_dir / f"{sid}_description.txt"; desc_path.write_text(desc, encoding="utf-8")
    meta_path = out_dir / f"{sid}_metadata.json"
    meta_path.write_text(json.dumps({"title": args.title}, ensure_ascii=False, indent=2))

    # 3) publishAt
    y, m, d = (int(x) for x in args.date.split("-"))
    pub_mty = datetime(y, m, d, args.hora, 0, 0, tzinfo=MTY)
    pub_utc = pub_mty.astimezone(timezone.utc)

    entry = {
        "story_id": sid, "title": args.title,
        "publish_date": args.date, "publish_day": pub_mty.strftime("%a"),
        "publish_time_mty": f"{args.hora:02d}:00",
        "publish_at_utc": pub_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mp4_path": str(mp4), "thumbnail_path": str(thumb),
        "description_path": str(desc_path), "metadata_path": str(meta_path),
        "chapters_count": 0, "priority": 1, "uploaded": False,
    }

    sched = json.loads(SCHEDULE.read_text()) if SCHEDULE.exists() else {"schedule": []}
    lst = sched["schedule"] if isinstance(sched, dict) and "schedule" in sched else sched
    lst[:] = [e for e in lst if e.get("story_id") != sid]  # reemplaza si ya estaba
    lst.append(entry)
    SCHEDULE.write_text(json.dumps(sched, ensure_ascii=False, indent=2))
    print(f"✅ {sid} agendado → {args.date} {args.hora:02d}:00 MTY 🌙")
    print(f"   Sube con: .venv/bin/python3 scripts/upload_to_youtube.py --dry-run")


if __name__ == "__main__":
    main()
