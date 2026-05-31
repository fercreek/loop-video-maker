"""
_build_120min_schedule.py — Genera descripciones + metadata + upload_schedule.json
para los 6×120min "PARA DORMIR". NO sube nada. Solo escribe archivos.

Cadencia: 1 cada 2 días, 9pm MTY (UTC-6 → 03:00 UTC día siguiente).
Orden por demanda SEO (venom 2026-05-31).
"""
import json
from pathlib import Path

PROJECT = Path(__file__).parent.parent
VID_DIR = PROJECT / "output" / "semana_2026-05-06" / "videos"
THUMB_DIR = PROJECT / "output" / "SUBIR" / "120min"
OUT_DIR = THUMB_DIR  # descripciones + metadata junto a thumbs
SCHEDULE_PATH = PROJECT / "data" / "upload_schedule.json"

DISCLOSURE = "\n\nContenido creado con asistencia de IA 🙏"

# orden = orden de publicación (por demanda SEO)
VIDEOS = [
    {
        "story_id": "paz120_salmos",
        "tema": "salmos",
        "title": "SALMOS PARA DORMIR PROFUNDAMENTE · Elimina Toda Ansiedad · 2 HORAS Sin Anuncios 📖",
        "verse": '"Jehová es mi pastor; nada me faltará." — Salmo 23:1',
        "intro": "📖 Deja que los Salmos calmen tu mente y eliminen toda ansiedad esta noche.",
        "body": "Dos horas de Salmos bíblicos con música instrumental suave para dormir profundamente. Para orar antes de dormir, soltar la ansiedad y descansar en el eterno cuidado de Dios.",
        "topics": "Salmos de paz, confianza, descanso y liberación de la ansiedad",
        "tags": ["salmos para dormir", "salmos para dormir profundamente", "eliminar la ansiedad", "salmos para la ansiedad", "musica cristiana para dormir", "salmo 23", "versiculos para dormir", "musica para dormir sin anuncios", "oracion nocturna", "VersiculoDeDios"],
    },
    {
        "story_id": "paz120_paz",
        "tema": "paz",
        "title": "MÚSICA CRISTIANA PARA DORMIR · Paz de Dios para Alejar la Angustia · 2 HORAS Sin Anuncios 🌙",
        "verse": '"Y la paz de Dios, que sobrepasa todo entendimiento, guardará vuestros corazones y vuestros pensamientos en Cristo Jesús." — Filipenses 4:7',
        "intro": "🌙 Que la paz de Dios guarde tu mente y aleje toda angustia mientras duermes.",
        "body": "Dos horas de música cristiana suave con versículos sobre la paz de Dios. Para dormir profundo, soltar toda preocupación y descansar en Su presencia.",
        "topics": "Paz de Dios, quietud, confianza y descanso del corazón",
        "tags": ["musica cristiana para dormir", "paz de dios", "musica para alejar la angustia", "versiculos para dormir", "filipenses 4:7", "musica para descansar", "musica instrumental cristiana", "musica para dormir sin anuncios", "relajacion cristiana", "VersiculoDeDios"],
    },
    {
        "story_id": "paz120_esperanza",
        "tema": "esperanza",
        "title": "SALMOS PARA DORMIR con Esperanza en Dios · 2 HORAS Sin Anuncios · Bendice tu Noche ✨",
        "verse": '"Porque yo sé los pensamientos que tengo acerca de vosotros... pensamientos de paz, y no de mal, para daros el fin que esperáis." — Jeremías 29:11',
        "intro": "✨ No pierdas la esperanza — Dios ya tiene tu mañana en Sus manos. Bendice tu noche.",
        "body": "Dos horas de Salmos y versículos de esperanza con música suave para dormir. Para los momentos oscuros, cuando necesitas descansar con la certeza de que el alba viene.",
        "topics": "Esperanza en Dios, restauración, promesas y nueva mañana",
        "tags": ["salmos para dormir", "esperanza en dios", "versiculos de esperanza", "jeremias 29:11", "musica cristiana para dormir", "bendice tu noche", "versiculos para dormir", "musica para dormir sin anuncios", "oracion nocturna", "VersiculoDeDios"],
    },
    {
        "story_id": "paz120_sanacion",
        "tema": "sanacion",
        "title": "SALMOS DE SANACIÓN PARA DORMIR · Sueño Profundo y Descanso · 2 HORAS Sin Anuncios 💚",
        "verse": '"Bendice, alma mía, a Jehová... él es quien sana todas tus dolencias." — Salmo 103:2-3',
        "intro": "💚 Mientras duermes, Dios sana y restaura. Entrégale tu cuerpo y tu alma esta noche.",
        "body": "Dos horas de Salmos de sanación con música instrumental suave para un sueño profundo. Para descansar confiando en que Dios renueva y restaura mientras duermes.",
        "topics": "Sanación, restauración, descanso profundo y renovación",
        "tags": ["salmos de sanacion", "salmos para dormir", "musica para sanacion", "sueño profundo", "musica cristiana para dormir", "salmo 103", "versiculos para dormir", "musica para dormir sin anuncios", "restauracion espiritual", "VersiculoDeDios"],
    },
    {
        "story_id": "paz120_fe",
        "tema": "fe",
        "title": "VERSÍCULOS PARA DORMIR que Fortalecen tu Fe · 2 HORAS Sin Anuncios · Palabra de Dios 🙏",
        "verse": '"La fe es la certeza de lo que se espera, la convicción de lo que no se ve." — Hebreos 11:1',
        "intro": "🙏 Duerme con fe — Dios trabaja mientras descansas. Él nunca duerme ni se adormece.",
        "body": "Dos horas de versículos sobre la fe y las promesas de Dios con música suave para dormir. Para entregarte a Su cuidado cada noche y fortalecer tu confianza en Él.",
        "topics": "Fe, promesas de Dios, confianza y descanso en Él",
        "tags": ["versiculos para dormir", "versiculos de fe", "palabra de dios", "hebreos 11", "musica cristiana para dormir", "fe en dios", "musica para descansar", "musica para dormir sin anuncios", "meditacion nocturna", "VersiculoDeDios"],
    },
    {
        "story_id": "paz120_provision",
        "tema": "provision",
        "title": "VERSÍCULOS PARA DORMIR · Provisión y Bendición de Dios · 2 HORAS Sin Anuncios 🕊️",
        "verse": '"Mi Dios, pues, suplirá todo lo que os falta conforme a sus riquezas en gloria en Cristo Jesús." — Filipenses 4:19',
        "intro": "🕊️ Descansa — tu Padre celestial conoce todo lo que necesitas y proveerá.",
        "body": "Dos horas de versículos sobre la provisión y bendición de Dios con música suave para dormir. Para soltar la preocupación por el mañana y descansar en Su fidelidad.",
        "topics": "Provisión, bendición, fidelidad de Dios y descanso",
        "tags": ["versiculos para dormir", "provision de dios", "bendicion de dios", "filipenses 4:19", "musica cristiana para dormir", "versiculos de provision", "musica para descansar", "musica para dormir sin anuncios", "oracion nocturna", "VersiculoDeDios"],
    },
]

# publishAt: 1 cada 2 días, 9pm MTY (UTC-6) = 03:00 UTC día siguiente
# arranque: hoy 2026-05-31 21:00 MTY
SCHEDULE_DATES = [
    ("2026-05-31", "2026-06-01T03:00:00Z"),
    ("2026-06-02", "2026-06-03T03:00:00Z"),
    ("2026-06-04", "2026-06-05T03:00:00Z"),
    ("2026-06-06", "2026-06-07T03:00:00Z"),
    ("2026-06-08", "2026-06-09T03:00:00Z"),
    ("2026-06-10", "2026-06-11T03:00:00Z"),
]

FOOTER = (
    "\n\n━━━━━━━━━━━━━━━━━━━━\n"
    "🔔 Suscríbete para más música devocional para dormir\n"
    "👍 Dale like si descansaste en paz esta noche\n"
    "💬 ¿Qué versículo calma tu corazón?\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "@VersiculoDeDios"
)

schedule = []
for i, v in enumerate(VIDEOS):
    tema = v["tema"]
    mp4 = VID_DIR / f"{tema}_120min.mp4"
    thumb = THUMB_DIR / f"{tema}_thumb.jpg"
    desc_path = OUT_DIR / f"{tema}_description.txt"
    meta_path = OUT_DIR / f"{tema}_metadata.json"

    description = (
        f"{v['intro']}\n\n{v['body']}\n\n{v['verse']}\n\n"
        f"📖 Versículos sobre: {v['topics']}\n"
        f"🎵 Música instrumental suave para dormir · Piano · Cuerdas\n"
        f"🖼️ Pinturas clásicas al óleo en movimiento lento"
        f"{FOOTER}{DISCLOSURE}"
    )
    desc_path.write_text(description, encoding="utf-8")
    meta_path.write_text(json.dumps({"title": v["title"], "tags": v["tags"]}, ensure_ascii=False, indent=2), encoding="utf-8")

    pub_date, pub_utc = SCHEDULE_DATES[i]
    schedule.append({
        "story_id": v["story_id"],
        "title": v["title"],
        "mp4_path": str(mp4),
        "thumbnail_path": str(thumb),
        "description_path": str(desc_path),
        "metadata_path": str(meta_path),
        "publish_date": pub_date,
        "publish_time_mty": "21:00",
        "publish_at_utc": pub_utc,
        "uploaded": False,
    })

SCHEDULE_PATH.write_text(json.dumps({"schedule": schedule}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ {len(VIDEOS)} descripciones + metadata escritos en {OUT_DIR}")
print(f"✓ Schedule → {SCHEDULE_PATH}")
print("\nVerificación de archivos:")
for v in VIDEOS:
    tema = v["tema"]
    mp4 = VID_DIR / f"{tema}_120min.mp4"
    thumb = THUMB_DIR / f"{tema}_thumb.jpg"
    print(f"  {tema:10s} mp4={'OK' if mp4.exists() else 'FALTA'}  thumb={'OK' if thumb.exists() else 'FALTA'}")
