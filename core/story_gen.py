"""
core/story_gen.py — Genera guión narrativo de historia bíblica usando Claude API.

Cachea en data/stories/{story_id}.json — no re-genera si ya existe.
Cada escena incluye: texto narrativo + prompt Gemini Imagen + mood musical.

Uso desde render_story.py:
    from core.story_gen import generate_story, STORIES
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR    = PROJECT_DIR / "data" / "stories"
CONFIG_PATH = PROJECT_DIR / "config.json"

# ─── Catálogo: STORIES se lee dinámico desde data/video_catalog.json ─────────
CATALOG_PATH = PROJECT_DIR / "data" / "video_catalog.json"

DEFAULT_MOODS = ["Solemnidad", "Adoración", "Intercesión", "Liberación", "Gloria"]


def _load_catalog() -> dict:
    """Carga catálogo. Cache simple por proceso."""
    if not CATALOG_PATH.exists():
        return {"videos": []}
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _build_meta_from_catalog_entry(entry: dict) -> dict:
    """Mapea entry de catálogo → meta requerida por el pipeline."""
    scenes = entry.get("scenes_target", 14)
    return {
        "title":         entry["title"],
        "bible_ref":     entry.get("bible_ref", ""),
        "target_scenes": scenes,
        "target_words":  scenes * 160,   # ~160 palabras/escena
        "moods":         entry.get("moods", DEFAULT_MOODS),
    }


class _StoriesProxy:
    """Proxy dict-like que lee del catálogo en cada acceso. Single source of truth."""

    def _index(self) -> dict[str, dict]:
        catalog = _load_catalog()
        items = catalog.get("videos", catalog) if isinstance(catalog, dict) else catalog
        return {item["id"]: _build_meta_from_catalog_entry(item) for item in items}

    def __contains__(self, key: str) -> bool:
        return key in self._index()

    def __getitem__(self, key: str) -> dict:
        return self._index()[key]

    def get(self, key: str, default=None):
        return self._index().get(key, default)

    def keys(self):
        return self._index().keys()

    def __iter__(self):
        return iter(self._index())

    def items(self):
        return self._index().items()

    def __len__(self):
        return len(self._index())


STORIES = _StoriesProxy()

IMAGEN_STYLE = (
    "masterpiece oil painting on canvas, dramatic painterly brushstrokes, "
    "warm cinematic lighting, no people, no text, no watermark, "
    "photorealistic texture, rich color palette, 16:9 landscape, biblical epic atmosphere"
)

SYSTEM_PROMPT = """Eres un narrador bíblico experto. Generates guiones narrativos en español de México
para videos de YouTube de historias de la Biblia. El tono es cálido, inspirador, reverente y accesible.
NO uses lenguaje arcaico innecesario. La narración es en tercera persona, estilo documental devocional.
Respondes ÚNICAMENTE con JSON válido, sin markdown, sin texto adicional."""

def _build_user_prompt(meta: dict) -> str:
    return f"""Genera un guión narrativo completo de la historia bíblica "{meta['title']}" ({meta['bible_ref']}).

INSTRUCCIONES:
- Exactamente {meta['target_scenes']} escenas
- ~{meta['target_words']} palabras en total (distribuidas entre escenas)
- Cada escena: 120-220 palabras de texto narrativo
- Narración en español de México, tono devocional-inspirador
- NO incluir versículos en cita directa larga — parafrasear dramáticamente
- Cada escena debe tener claro momentum narrativo (causa → efecto → tensión → resolución)

RESPONDE con este JSON exacto (sin markdown):
{{
  "story_id": "{list(k for k,v in __import__('core.story_gen', fromlist=['STORIES']).STORIES.items() if v['title'] == meta['title'])[0] if False else 'ID'}",
  "title": "{meta['title']}",
  "bible_ref": "{meta['bible_ref']}",
  "scenes": [
    {{
      "id": 1,
      "title": "Título corto de la escena (5-7 palabras)",
      "text": "Texto narrativo completo de la escena. 120-220 palabras...",
      "image_prompt": "Imagen descriptiva en inglés para Gemini Imagen, escena bíblica específica, {IMAGEN_STYLE}",
      "mood": "Nombre del mood musical (ej: Solemnidad, Adoración, Gloria, Liberación)"
    }}
  ]
}}"""


def _load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def _call_claude(story_id: str, meta: dict, api_key: str) -> dict:
    """Llama Claude API para generar el story script. Retorna dict parseado."""
    sys.path.insert(0, str(PROJECT_DIR / ".venv" / "lib" / "python3.13" / "site-packages"))
    # Try multiple python versions
    for pyver in ["python3.13", "python3.12", "python3.11"]:
        site = PROJECT_DIR / ".venv" / "lib" / pyver / "site-packages"
        if site.exists():
            sys.path.insert(0, str(site))
            break

    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic not found in .venv. Run: .venv/bin/pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=api_key)

    # Build user prompt with correct story_id
    user_prompt = f"""Genera un guión narrativo completo de la historia bíblica "{meta['title']}" ({meta['bible_ref']}).

INSTRUCCIONES:
- Exactamente {meta['target_scenes']} escenas
- ~{meta['target_words']} palabras en total (distribuidas entre escenas)
- Cada escena: 120-220 palabras de texto narrativo
- Narración en español de México, tono devocional-inspirador
- NO incluir versículos en cita directa larga — parafrasear dramáticamente
- Cada escena debe tener claro momentum narrativo

RESPONDE con este JSON exacto (sin markdown, sin ```json):
{{
  "story_id": "{story_id}",
  "title": "{meta['title']}",
  "bible_ref": "{meta['bible_ref']}",
  "scenes": [
    {{
      "id": 1,
      "title": "Título corto de la escena",
      "text": "Texto narrativo de 120-220 palabras...",
      "image_prompt": "Detailed English description for Gemini Imagen 4.0: specific biblical scene, landscape or setting with no people, {IMAGEN_STYLE}",
      "mood": "Mood musical (Solemnidad|Adoración|Gloria|Liberación|Contemplación|Intercesión|Restauración|Alabanza)"
    }}
  ]
}}"""

    print(f"  [claude] Generando historia: {meta['title']}...")
    t0 = time.time()
    msg = client.messages.create(
        model="claude-sonnet-4-7",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    elapsed = time.time() - t0
    raw = msg.content[0].text.strip()
    print(f"  [claude] Generado en {elapsed:.1f}s ({len(raw.split())} palabras)")

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    return json.loads(raw)


def generate_story(story_id: str, force: bool = False) -> dict:
    """
    Genera o carga desde caché el script de una historia bíblica.

    Args:
        story_id: clave en STORIES dict (ej: 'david-goliat')
        force: regenerar aunque exista caché

    Returns:
        dict con story script completo
    """
    if story_id not in STORIES:
        raise ValueError(f"Historia '{story_id}' no existe. Opciones: {list(STORIES)}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = DATA_DIR / f"{story_id}.json"

    if cache_path.exists() and not force:
        print(f"  [story] Cargando caché: {cache_path}")
        with open(cache_path) as f:
            return json.load(f)

    meta = STORIES[story_id]
    cfg  = _load_config()
    api_key = cfg.get("claude_api_key", "") or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "API key de Claude no encontrada.\n"
            "Agrega en config.json: {\"claude_api_key\": \"sk-ant-...\"}\n"
            "O exporta: export ANTHROPIC_API_KEY=sk-ant-..."
        )

    script = _call_claude(story_id, meta, api_key)

    # Inject moods from config if not present
    scene_moods = meta["moods"]
    for i, scene in enumerate(script.get("scenes", [])):
        if not scene.get("mood"):
            scene["mood"] = scene_moods[i % len(scene_moods)]

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"  [story] Guardado en {cache_path}")

    return script


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--story", default="david-goliat", choices=list(STORIES))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    script = generate_story(args.story, force=args.force)
    print(f"\nHistoria: {script['title']} — {len(script['scenes'])} escenas")
    for s in script["scenes"]:
        words = len(s["text"].split())
        print(f"  {s['id']:2d}. {s['title']:<40s} ({words} palabras) [{s['mood']}]")
