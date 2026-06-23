"""
Arma output/SUBIR/ — todo el contenido a la mano + calendario sugerido para subir.
Symlinks (no duplica GB) + INFO.txt por pieza (título, descripción, fecha/hora) + CALENDARIO.md.
Reusable: corre cuando haya contenido nuevo en output/.
Uso:  .venv/bin/python3 scripts/build_subir.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
SUBIR = ROOT / "output" / "SUBIR"

# ── COHERENCIA DÍA/NOCHE: la HORA se asigna según el tema de la pieza ──
# 🌙 noche (dormir/sleep/noche) → bedtime, cuando se busca "oración para dormir"
# 🌅 mañana (despertar/mañana/camino/trabajo) → al comenzar el día
# ☀️ día (neutral) → pico devocional de la tarde
NOCHE = ("dormir", "noche", "sleep", "descans", "salmo 91", "ansiedad", "paz del corazón")
MANANA = ("mañana", "despertar", "amanece", "comenzar el día", "camino", "trabajo", "gratitud al despertar")

def franja(texto: str, es_long: bool):
    t = texto.lower()
    if any(k in t for k in NOCHE):
        return "🌙 noche", "21:00 MTY" if es_long else "20:30 MTY"
    if any(k in t for k in MANANA):
        return "🌅 mañana", "06:30 MTY" if es_long else "06:30 MTY"
    return "☀️ día", "18:00 MTY" if es_long else "13:00 MTY"

# (sid, mp4, fecha) — la HORA la decide franja() según título/tema
LONGFORM = [
    ("oracion_dormir_paz",        ROOT/"output/stories/oracion_dormir_paz/oracion_dormir_paz.mp4",        "Lun 23 jun"),
    ("reflexion_dolor_proposito", ROOT/"output/stories/reflexion_dolor_proposito/reflexion_dolor_proposito.mp4", "Jue 26 jun"),
    ("salmo91_sleep",             ROOT/"output/sleep/sleep_salmo91_120min.mp4",                            "Sáb 28 jun"),
]
REELS = [
    ("fe_001",        "Lun 23 jun"),
    ("esperanza_001", "Mar 24 jun"),
    ("gratitud_001",  "Mié 25 jun"),
    ("proteccion_001","Jue 26 jun"),
    ("sanacion_001",  "Vie 27 jun"),
    ("familia_001",   "Sáb 28 jun"),
    ("trabajo_001",   "Dom 29 jun"),
    ("paz_001",       "Lun 30 jun"),
]


def link(src: Path, dst: Path):
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if src.exists():
        dst.symlink_to(src)
        return True
    return False


def lf_meta(sid):
    base = ROOT / "output" / "stories" / sid
    title, desc = sid, ""
    mj = base / "yt_metadata.json"
    dt = base / "yt_description.txt"
    if mj.exists():
        title = json.loads(mj.read_text()).get("title", sid)
    if dt.exists():
        desc = dt.read_text()
    return title, desc


def reel_meta(rid):
    pool = json.loads((ROOT/"data"/"oraciones_pool.json").read_text())
    items = pool.get("oraciones", pool if isinstance(pool, list) else [])
    for x in items:
        if isinstance(x, dict) and x.get("id") == rid:
            title = x.get("titulo", rid)
            desc = (x.get("texto", "") + "\n\n" + " ".join(x.get("hashtags", [])) + "\n\n" + x.get("cta", "")).strip()
            return title, desc
    return rid, ""


def find_reel_mp4(rid):
    for f in sorted((ROOT/"output"/"shorts").rglob(f"short_{rid}_*.mp4")):
        return f
    return None


def write_info(folder: Path, title, desc, when, mp4: Path, status):
    folder.mkdir(parents=True, exist_ok=True)
    if mp4 and mp4.exists():
        link(mp4, folder / "video.mp4")
        thumb = mp4.parent / "thumbnail.jpg"
        if not thumb.exists():
            thumb = mp4.with_name(mp4.stem + "_thumb.jpg")
        if thumb.exists():
            link(thumb, folder / "thumbnail.jpg")
    (folder / "INFO.txt").write_text(
        f"PUBLICAR:  {when}\nESTADO:    {status}\n\n=== TÍTULO ===\n{title}\n\n=== DESCRIPCIÓN ===\n{desc}\n",
        encoding="utf-8")


def main():
    SUBIR.mkdir(parents=True, exist_ok=True)
    cal = ["# 📅 CALENDARIO SUGERIDO — @VersiculoDeDios",
           "> Sube manual en YouTube Studio: arrastra el video.mp4, pega TÍTULO/DESCRIPCIÓN de INFO.txt, y programa en la fecha/hora indicada (zona MTY).",
           "> **La HORA es coherente con el tema:** 🌙 noche (dormir/sleep) al acostarse · 🌅 mañana (despertar/camino) al comenzar el día · ☀️ día (neutral) en el pico de la tarde.\n",
           "## 🎬 LONG-FORM (cuentan para las 4,000h del YPP)\n",
           "| # | Franja | Publicar | Pieza | Carpeta |",
           "|---|---|---|---|---|"]
    n = 0
    for i, (sid, mp4, fecha) in enumerate(LONGFORM, 1):
        if "salmo" not in sid:
            title, desc = lf_meta(sid)
        else:
            title = "SALMO 91 PARA DORMIR TODA LA NOCHE 2026 · Protección y Paz Mientras Descansas en Dios"
            desc = (
                "SALMO 91 PARA DORMIR TODA LA NOCHE. 2 horas de versículos de protección "
                "y música suave para descansar en la presencia de Dios. Déjalo sonar toda "
                "la noche y duerme en paz, cubierto bajo Su sombra.\n\n"
                "\"El que habita al abrigo del Altísimo morará bajo la sombra del Omnipotente\" "
                "— Salmo 91:1, Reina-Valera 1960\n\n"
                "🙏 Antes de dormir, déjanos un Amén en los comentarios.\n"
                "🔔 Suscríbete para nuevos videos para dormir y descansar en Dios cada semana.\n"
                "@VersiculoDeDios"
            )
        fr, hora = franja(title + " " + sid, es_long=True)
        when = f"{fecha} · {hora}"
        status = "✅ listo" if (mp4.exists()) else "⏳ renderizando"
        folder = SUBIR / f"LONGFORM_{i:02d}_{sid}"
        write_info(folder, title, desc, f"{when}  ({fr})", mp4, status)
        cal.append(f"| {i} | {fr} | {when} | {title[:46]} | `SUBIR/{folder.name}/` |")
        n += 1
    cal += ["\n## 🎞 REELS (subs + funnel→sleep)\n",
            "| # | Franja | Publicar | Reel | Carpeta |", "|---|---|---|---|---|"]
    for i, (rid, fecha) in enumerate(REELS, 1):
        title, desc = reel_meta(rid)
        fr, hora = franja(title + " " + rid, es_long=False)
        when = f"{fecha} · {hora}"
        mp4 = find_reel_mp4(rid)
        status = "✅ listo" if (mp4 and mp4.exists()) else "❌ falta"
        folder = SUBIR / "REELS" / f"{i:02d}_{rid}"
        write_info(folder, title, desc, f"{when}  ({fr})", mp4, status)
        cal.append(f"| {i} | {fr} | {when} | {title[:46]} | `SUBIR/REELS/{folder.name}/` |")
        n += 1
    (SUBIR / "CALENDARIO.md").write_text("\n".join(cal) + "\n", encoding="utf-8")
    print(f"✅ output/SUBIR/ armado — {n} piezas + CALENDARIO.md")
    print(f"   {SUBIR}")


if __name__ == "__main__":
    main()
