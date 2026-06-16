"""
scripts/outlier_analyzer.py — Paso 2 (ANALIZA) de nuestro mini-OutlierLabs.

Pipeline completo del loop (inspirado en outlierlabs.app):
  1. DESCUBRE → scripts/outlier_finder.py  (views > subs → data/outliers.json)
  2. ANALIZA  → ESTE script                (POR QUÉ jaló + cómo replicarlo p/VDD)
  3. IMPLEMENTA → render_story.py / render_sleep.py (genera el contenido)

Qué hace: toma los top outliers (de data/outliers.json o un --video-id), jala su
metadata viva (título, descripción, tags, duración, views, subs, ratio), y le pide
a Claude que diseccione como OutlierLabs:
  - Portada/packaging (técnica del título, qué promete)
  - Hook (in media res, loop abierto, pregunta, etc.)
  - Narrativa/formato (estructura, stakes, por qué retiene)
  - Replicabilidad (% + qué se copia vs se adapta)
  - ADAPTACIÓN VDD: título + ángulo + formato concretos para @VersiculoDeDios
    (nicho cristiano/devocional ES) — listo para alimentar render_story/render_sleep.

Salida: data/briefs/outlier-analysis-{fecha}.md + .json

Uso:
    .venv/bin/python3 scripts/outlier_analyzer.py                 # top 3 de outliers.json
    .venv/bin/python3 scripts/outlier_analyzer.py --top 5
    .venv/bin/python3 scripts/outlier_analyzer.py --video-id dQw4w9WgXcQ
    .venv/bin/python3 scripts/outlier_analyzer.py --kind historia # filtra por tipo

Costo: ~1 llamada Claude por video (sonnet). Barato.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))
for _pyver in ["python3.13", "python3.12", "python3.11", "python3.9"]:
    _site = PROJECT_DIR / ".venv" / "lib" / _pyver / "site-packages"
    if _site.exists():
        sys.path.insert(0, str(_site))
        break

from core.youtube_client import _youtube

OUTLIERS_PATH = PROJECT_DIR / "data" / "outliers.json"
CONFIG_PATH = PROJECT_DIR / "config.json"
BRIEFS_DIR = PROJECT_DIR / "data" / "briefs"
# LLM de análisis: Gemini REST (la key que el repo ya tiene; genai/anthropic no en venv).
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_BASE = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _gemini_text(system: str, prompt: str, api_key: str) -> str:
    """Llama Gemini generateContent y devuelve el texto. Dependency-free (urllib).
    Thinking desactivado (thinkingBudget=0) para no quemar el budget de output."""
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{GEMINI_BASE}?key={api_key}", data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        resp = json.loads(r.read())
    cand = (resp.get("candidates") or [{}])[0]
    parts = cand.get("content", {}).get("parts", [])
    if not parts:
        raise RuntimeError(f"sin texto (finishReason={cand.get('finishReason')})")
    return parts[0]["text"].strip()

ANALYSIS_SCHEMA = {
    "packaging": "técnica del título y qué promete la portada — por qué genera el click",
    "hook": "el gancho de los primeros segundos (in media res / loop abierto / pregunta / cifra / contradicción)",
    "narrativa": "estructura y formato — por qué retiene (stakes, pacing, curiosidad, listicle, etc.)",
    "por_que_jalo": "1-2 frases: la razón central de que tenga más views que subs",
    "replicabilidad_pct": "0-100, qué tan replicable es el patrón",
    "copiable": ["elementos que se copian tal cual"],
    "adaptable": ["elementos que hay que adaptar a otro creador/nicho"],
    "vdd_adaptacion": {
        "formato": "historia | sleep | short",
        "titulo_sugerido": "título SEO concreto para @VersiculoDeDios (nicho cristiano/devocional ES)",
        "angulo": "el ángulo/gancho aplicado al nicho religioso",
        "por_que_funcionaria": "por qué este patrón jalaría en VDD",
    },
}

SYSTEM = (
    "Eres un analista de virality de YouTube experto, estilo OutlierLabs. "
    "Disectas POR QUÉ un video tuvo más views que suscriptores (outlier) y traduces "
    "el patrón en algo replicable para un canal cristiano/devocional en español "
    "(@VersiculoDeDios — historias bíblicas, contenido para dormir, oración). "
    "Eres concreto y honesto: si un patrón NO es replicable para ese nicho, lo dices. "
    "No inventas métricas; razonas desde título, descripción, formato, duración y el ratio outlier."
)


def _load_outliers() -> list[dict]:
    if not OUTLIERS_PATH.exists():
        raise SystemExit(f"No existe {OUTLIERS_PATH}. Corre primero scripts/outlier_finder.py")
    return json.load(open(OUTLIERS_PATH)).get("outliers", [])


def _fetch_meta(yt, video_id: str) -> dict | None:
    r = yt.videos().list(part="snippet,statistics,contentDetails", id=video_id).execute()
    items = r.get("items", [])
    if not items:
        return None
    it = items[0]
    sn = it["snippet"]
    return {
        "video_id": video_id,
        "title": sn["title"],
        "channel": sn["channelTitle"],
        "description": (sn.get("description", "") or "")[:1500],
        "tags": sn.get("tags", [])[:20],
        "duration": it["contentDetails"]["duration"],
        "views": int(it["statistics"].get("viewCount", 0)),
        "url": f"https://youtube.com/watch?v={video_id}",
    }


def analyze_one(api_key: str, meta: dict, ratio: float | None, subs: int | None) -> dict:
    canal_line = f"{meta['channel']} ({subs:,} subs)" if subs else meta['channel']
    prompt = f"""Analiza este video OUTLIER de YouTube (tuvo MUCHAS más views que el canal suscriptores → el TEMA jaló, no el creador).

DATA DEL VIDEO:
- Título: {meta['title']}
- Canal: {canal_line}
- Views: {meta['views']:,}
- Ratio views/subs: {ratio if ratio else 'n/d'}
- Duración (ISO): {meta['duration']}
- Tags: {', '.join(meta['tags']) if meta['tags'] else '(sin tags)'}
- Descripción (recorte): {meta['description'][:800]}

Disecciona como OutlierLabs y responde SOLO con este JSON exacto (sin markdown, sin ```):
{{
  "packaging": "técnica del título/portada y qué promete",
  "hook": "el gancho probable de los primeros segundos",
  "narrativa": "estructura/formato y por qué retiene",
  "por_que_jalo": "1-2 frases con la razón central del outlier",
  "replicabilidad_pct": 0-100,
  "copiable": ["elemento 1", "elemento 2"],
  "adaptable": ["elemento 1"],
  "vdd_adaptacion": {{
    "formato": "historia|sleep|short",
    "titulo_sugerido": "título SEO concreto para @VersiculoDeDios",
    "angulo": "el ángulo aplicado al nicho cristiano/devocional",
    "por_que_funcionaria": "por qué jalaría en VDD"
  }}
}}"""
    raw = _gemini_text(SYSTEM, prompt, api_key)
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()
    return json.loads(raw)


def _to_markdown(results: list[dict]) -> str:
    lines = [
        "# Análisis de Outliers — Paso 2 (mini-OutlierLabs VDD)",
        f"> Generado: {datetime.now(timezone.utc).isoformat()} · {len(results)} videos analizados",
        "> Fuente: `data/outliers.json` (outlier_finder) · Análisis: Gemini 2.5-flash",
        "> Uso: cada `vdd_adaptacion` es un brief listo para render_story/render_sleep.",
        "",
    ]
    for r in results:
        m, a = r["meta"], r["analysis"]
        v = a.get("vdd_adaptacion", {})
        lines += [
            f"## {m['title'][:70]}",
            f"`{m['video_id']}` · {m['views']:,} views · ratio {r.get('ratio','n/d')} · {m['url']}",
            "",
            f"- **Packaging:** {a.get('packaging','')}",
            f"- **Hook:** {a.get('hook','')}",
            f"- **Narrativa:** {a.get('narrativa','')}",
            f"- **Por qué jaló:** {a.get('por_que_jalo','')}",
            f"- **Replicabilidad:** {a.get('replicabilidad_pct','?')}%",
            f"- **Copiable:** {', '.join(a.get('copiable',[]))}",
            f"- **Adaptable:** {', '.join(a.get('adaptable',[]))}",
            "",
            "### 🎯 Adaptación VDD",
            f"- **Formato:** {v.get('formato','?')}",
            f"- **Título sugerido:** {v.get('titulo_sugerido','')}",
            f"- **Ángulo:** {v.get('angulo','')}",
            f"- **Por qué funcionaría:** {v.get('por_que_funcionaria','')}",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Analiza outliers (paso 2) → brief VDD")
    ap.add_argument("--top", type=int, default=3, help="cuántos top outliers analizar")
    ap.add_argument("--video-id", help="analizar un video específico (ignora --top)")
    ap.add_argument("--kind", choices=["short", "historia", "long"], help="filtrar por tipo")
    ap.add_argument("--min-ratio", type=float, default=0, help="ratio mínimo a considerar")
    args = ap.parse_args()

    cfg = json.load(open(CONFIG_PATH)) if CONFIG_PATH.exists() else {}
    key = cfg.get("gemini_api_key", "")
    if not key:
        raise SystemExit("Falta gemini_api_key en config.json")
    yt = _youtube()

    # Construir lista de targets (con ratio/subs si vienen de outliers.json)
    targets = []
    if args.video_id:
        targets = [{"video_id": args.video_id, "ratio": None, "channel_subs": None}]
    else:
        rows = _load_outliers()
        if args.kind:
            rows = [r for r in rows if r.get("kind") == args.kind]
        rows = [r for r in rows if r.get("ratio", 0) >= args.min_ratio]
        targets = rows[:args.top]

    if not targets:
        raise SystemExit("Sin targets (revisa filtros o corre outlier_finder primero)")

    print(f"🧠 Analizando {len(targets)} outlier(s) con Gemini...")
    results = []
    for t in targets:
        vid = t["video_id"]
        meta = _fetch_meta(yt, vid)
        if not meta:
            print(f"  ⚠️ {vid} no existe — skip"); continue
        try:
            analysis = analyze_one(key, meta, t.get("ratio"), t.get("channel_subs"))
        except Exception as e:
            print(f"  ⚠️ {vid} análisis falló: {e}"); continue
        v = analysis.get("vdd_adaptacion", {})
        print(f"  ✓ {meta['title'][:42]:44} → [{v.get('formato','?')}] {v.get('titulo_sugerido','')[:40]}")
        results.append({"meta": meta, "ratio": t.get("ratio"), "analysis": analysis})

    if not results:
        raise SystemExit("Ningún análisis exitoso")

    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md_path = BRIEFS_DIR / f"outlier-analysis-{stamp}.md"
    json_path = BRIEFS_DIR / f"outlier-analysis-{stamp}.json"
    md_path.write_text(_to_markdown(results), encoding="utf-8")
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  ✅ {len(results)} análisis → {md_path}")
    print("  Cada 'Adaptación VDD' es un brief listo para producir.")


if __name__ == "__main__":
    main()
