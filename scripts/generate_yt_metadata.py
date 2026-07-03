"""
scripts/generate_yt_metadata.py — Genera metadata YouTube auto desde story JSON + MP4 final.

Lee:
  - data/stories/{id}.json         (cold_open, scenes, end_screen)
  - audio/narrations/*.wav          (durations para chapters reales)
  - data/video_catalog.json         (título canonical, tags)

Genera:
  - output/stories/{id}/yt_metadata.json   (título, descripción, chapters, tags)
  - output/stories/{id}/yt_description.txt (descripción copy-paste lista)

Uso:
    python3 scripts/generate_yt_metadata.py --story david-goliat
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR  = Path(__file__).parent.parent
STORIES_JSON = PROJECT_DIR / "data" / "stories"
NARR_DIR     = PROJECT_DIR / "audio" / "narrations"
OUTPUT_BASE  = PROJECT_DIR / "output" / "stories"
CATALOG_PATH = PROJECT_DIR / "data" / "video_catalog.json"

CHANNEL_TAG = "@VersiculoDeDios"

DEFAULT_TAGS = [
    "historias bíblicas en español", "biblia narrada", "historia bíblica completa",
    "historias de fe", "narración bíblica", "biblia audio español",
    "fe cristiana", "palabra de Dios", "versículos de dios",
]


def get_audio_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def fmt_timestamp(seconds: float) -> str:
    """Formato MM:SS o HH:MM:SS para chapters de YouTube."""
    s = int(seconds)
    h, m, s = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def build_chapters(story: dict, narr_dir: Path) -> list[dict]:
    """
    Calcula chapters reales basado en duraciones de WAVs.
    Retorna: [{timestamp_str, title, start_sec}]
    """
    story_id = story["story_id"]
    chapters: list[dict] = []
    cursor = 0.0

    # Cold open chapter (si existe)
    if story.get("cold_open"):
        co_files = sorted(narr_dir.rglob(f"{story_id}_cold_open_*.wav"))
        if co_files:
            chapters.append({
                "timestamp": fmt_timestamp(cursor),
                "title":     "Introducción",
                "start_sec": cursor,
            })
            cursor += get_audio_duration(co_files[0]) + 0.8  # buffer

    # Scenes
    for scene in story["scenes"]:
        sid = scene["id"]
        scene_files = sorted(narr_dir.rglob(f"{story_id}_s{sid:02d}_*.wav"))
        if not scene_files:
            continue
        chapters.append({
            "timestamp": fmt_timestamp(cursor),
            "title":     scene["title"],
            "start_sec": cursor,
        })
        cursor += get_audio_duration(scene_files[0]) + 0.8

    # End screen como chapter
    if story.get("end_screen"):
        chapters.append({
            "timestamp": fmt_timestamp(cursor),
            "title":     "Próxima historia",
            "start_sec": cursor,
        })

    # Primer chapter SIEMPRE en 0:00 (requerimiento YouTube)
    if chapters:
        chapters[0]["timestamp"] = "0:00"
        chapters[0]["start_sec"] = 0.0

    return chapters


def _normalize_hashtag(text: str) -> str:
    """Quita acentos y caracteres no alfanuméricos para hashtag."""
    import unicodedata
    s = unicodedata.normalize("NFD", text)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return "".join(c for c in s if c.isalnum())


# Wording coherente por tipo de contenido (no todo es "historia bíblica")
TYPE_WORDS = {
    "historia": {
        "intro": "narrada completa en español. {n} minutos de historia bíblica con narración inmersiva.",
        "cta": "Si esta historia te tocó el corazón, escríbenos en los comentarios:\n¿qué fue lo que más te impactó?",
        "subscribe": "nuevas historias bíblicas narradas cada semana",
        "basado": "Reina-Valera 1960 / adaptación narrativa",
    },
    "oracion": {
        "intro": "Una oración guiada de {n} minutos para acompañarte, con narración serena y música suave de fondo.",
        "cta": "Si esta oración te dio paz, déjanos un 🙏 Amén en los comentarios.",
        "subscribe": "nuevas oraciones para acercarte a Dios cada semana",
        "basado": "Reina-Valera 1960",
    },
    "reflexion": {
        "intro": "Una reflexión bíblica de {n} minutos para encontrar paz y esperanza, con narración serena.",
        "cta": "Si esta reflexión te tocó el corazón, escríbenos en los comentarios:\n¿qué fue lo que más necesitabas escuchar hoy?",
        "subscribe": "nuevas reflexiones que te acercan a Dios cada semana",
        "basado": "Reina-Valera 1960",
    },
    "sleep": {
        "intro": "{n} minutos para descansar en la presencia de Dios, con versículos y música suave para dormir.",
        "cta": "Que descanses en paz. Déjanos un 🙏 en los comentarios antes de dormir.",
        "subscribe": "nuevos videos para dormir y descansar en Dios cada semana",
        "basado": "Reina-Valera 1960",
    },
}


def build_description(story: dict, chapters: list[dict], total_dur_min: float) -> str:
    """Construye descripción completa lista para copy-paste a YouTube."""
    title = story["title"]
    bible_ref = story.get("bible_ref", "")
    words = TYPE_WORDS.get(story.get("type", "historia"), TYPE_WORDS["historia"])

    # Hook único por historia (campo `hook_text` en JSON, fallback genérico por tipo)
    custom_hook = story.get("hook_text") or story.get("description_hook")
    if custom_hook:
        hook = f"{custom_hook}\n\n"
    else:
        hook = f"{title}. {words['intro'].format(n=int(total_dur_min))}\n\n"

    desc = hook

    # Chapters
    desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    desc += "CAPÍTULOS\n"
    desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    for ch in chapters:
        desc += f"{ch['timestamp']} – {ch['title']}\n"
    desc += "\n"

    # Referencia bíblica
    if bible_ref:
        desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += "BASADO EN\n"
        desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"{bible_ref} — {words['basado']}\n\n"

    # CTA
    desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    desc += "PARA REFLEXIONAR\n"
    desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    desc += f"{words['cta']}\n\n"

    desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    desc += "SUSCRÍBETE\n"
    desc += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    desc += f"Activa la 🔔 para no perderte {words['subscribe']}.\n"
    desc += f"{CHANNEL_TAG}\n\n"

    # Hashtags — deduplicados, sin acentos, max 7 (sweet spot YT)
    title_tag = _normalize_hashtag(title.replace(" ", ""))
    raw_tags = [
        title_tag,                 # ej: DavidyGoliat
        "HistoriasBiblicas",
        "BibliaEnEspanol",
        "NarracionBiblica",
        "PalabraDeDios",
        "FeCristiana",
        "VersiculoDeDios",
    ]
    seen = set()
    unique_tags = []
    for t in raw_tags:
        key = t.lower()
        if key not in seen and t:
            seen.add(key)
            unique_tags.append(f"#{t}")
    desc += " ".join(unique_tags) + "\n"

    return desc


def find_story_in_catalog(story_id: str) -> dict | None:
    if not CATALOG_PATH.exists():
        return None
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)
    items = catalog.get("videos", catalog) if isinstance(catalog, dict) else catalog
    for item in items:
        if item.get("id") == story_id:
            return item
    return None


def generate(story_id: str) -> dict:
    """Genera metadata completo para una historia. Retorna dict."""
    story_path = STORIES_JSON / f"{story_id}.json"
    if not story_path.exists():
        raise RuntimeError(f"No existe {story_path}")

    with open(story_path) as f:
        story = json.load(f)

    chapters = build_chapters(story, NARR_DIR)

    # Duración total
    final_mp4 = OUTPUT_BASE / story_id / f"{story_id}.mp4"
    total_dur_sec = get_audio_duration(final_mp4) if final_mp4.exists() else 0
    total_dur_min = total_dur_sec / 60

    # Título: del catálogo si existe, si no del story JSON
    catalog_entry = find_story_in_catalog(story_id)
    title = catalog_entry["title"] if catalog_entry else story.get("title", story_id)

    # Type del catálogo (oracion/reflexion/sleep/historia) → wording coherente en la descripción
    if catalog_entry and catalog_entry.get("type"):
        story["type"] = catalog_entry["type"]
    story["title"] = title  # usar el título canónico del catálogo (con 2026, etc.)

    # Tags: default + story-specific (todos <= 30 chars, validación YouTube)
    bible_ref_tag = story.get("bible_ref", "").lower()
    short_title = story.get("title", "").split(":")[0].split("|")[0].strip().lower()

    raw_tags = DEFAULT_TAGS + [
        short_title,
        f"{short_title} biblia",
        f"{short_title} historia",
        bible_ref_tag,
        f"{short_title} narrada",
    ]

    # Dedupe + filter >30 chars (YouTube hard limit)
    tags_seen = set()
    tags: list[str] = []
    for t in raw_tags:
        t = t.strip()
        if not t or len(t) > 30 or t.lower() in tags_seen:
            continue
        tags_seen.add(t.lower())
        tags.append(t)

    description = build_description(story, chapters, total_dur_min)

    metadata = {
        "story_id":     story_id,
        "title":        title,
        "duration_sec": total_dur_sec,
        "duration_min": round(total_dur_min, 1),
        "chapters":     chapters,
        "tags":         tags,
        "description":  description,
    }

    # Save
    out_dir = OUTPUT_BASE / story_id
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "yt_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    with open(out_dir / "yt_description.txt", "w", encoding="utf-8") as f:
        f.write(description)

    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--story", required=True, help="story_id (ej: david-goliat)")
    args = parser.parse_args()

    md = generate(args.story)
    print(f"Título: {md['title']}")
    print(f"Duración: {md['duration_min']} min")
    print(f"Chapters: {len(md['chapters'])}")
    print(f"Tags: {len(md['tags'])}")
    print(f"\nGuardado en:")
    print(f"  output/stories/{args.story}/yt_metadata.json")
    print(f"  output/stories/{args.story}/yt_description.txt")


if __name__ == "__main__":
    main()
