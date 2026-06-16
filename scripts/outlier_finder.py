"""
scripts/outlier_finder.py — Encuentra OUTLIERS del nicho religioso en YouTube.

Lección del podcast monetización (Yayas/dúo de dos, 2026-06-15):
  "Busca videos con MÁS VISITAS QUE SUSCRIPTORES (outlier) → el tema funciona
   por el TEMA, no por el creador → es replicable. Copia la esencia, hazlo mejor
   y enfócalo en TU nicho específico (las personas, no la categoría)."

Qué hace: para un set de queries del nicho (sleep/oración/historia bíblica/etc),
busca uploads recientes y rankea por OUTLIER INDEX = views/día del video ÷ mediana
views/día del canal (estándar Spotter/vidIQ: vs el propio canal, age-normalizado).
Índice alto = el tema jala MUY por encima del baseline del canal → replicable para VDD.
(views/subs queda como métrica secundaria, no como score primario.)

Uso:
    .venv/bin/python3 scripts/outlier_finder.py
    .venv/bin/python3 scripts/outlier_finder.py --published-days 60 --min-ratio 3 --max-per-query 25
    .venv/bin/python3 scripts/outlier_finder.py --queries "oracion para dormir" "salmo 91" --out data/outliers.json

Salida: tabla en consola (top N) + JSON en data/outliers.json.
Costo quota: search.list = 100u/query. Default ~9 queries = ~900u (de 10,000/día).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from core.youtube_client import _youtube, get_channel_id  # auth ya resuelto

OUT_DEFAULT = PROJECT_DIR / "data" / "outliers.json"

# Nicho VDD — queries semilla. El nicho son las PERSONAS, no "versículos":
# personas que buscan dormir en paz, calmar ansiedad, escuchar una historia bíblica.
DEFAULT_QUERIES = [
    "oracion para dormir",
    "salmos para dormir",
    "musica cristiana para dormir",
    "versiculos contra la ansiedad",
    "historia biblica",
    "salmo 91",
    "reflexion cristiana",
    "promesas de dios",
    "como confiar en dios",
]


def _dur_min(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return round(h * 60 + mi + s / 60)


def _fmt_kind(dur_min: int) -> str:
    return "short" if dur_min <= 1 else ("historia" if dur_min <= 35 else "long")


def _age_days(published_iso: str) -> float:
    pub = datetime.fromisoformat(published_iso.replace("Z", "+00:00"))
    return max((datetime.now(timezone.utc) - pub).total_seconds() / 86400.0, 0.5)


def _median(xs: list[float]) -> float:
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return 0.0
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def _channel_baselines(yt, uploads_map: dict[str, str]) -> dict[str, float]:
    """Mediana de views/día de los últimos ~15 uploads de cada canal = baseline.
    Esto reemplaza 'subs' como denominador (estándar vidIQ/Spotter: vs el propio canal)."""
    base: dict[str, float] = {}
    for ch, pl in uploads_map.items():
        try:
            r = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=15).execute()
            vids = [i["contentDetails"]["videoId"] for i in r.get("items", [])]
            if not vids:
                continue
            rr = yt.videos().list(part="snippet,statistics", id=",".join(vids)).execute()
            vpds = []
            for it in rr.get("items", []):
                v = int(it["statistics"].get("viewCount", 0))
                vpds.append(v / _age_days(it["snippet"]["publishedAt"]))
            med = _median(vpds)
            if med > 0:
                base[ch] = med
        except Exception:
            continue
    return base


def find_outliers(queries: list[str], published_days: int, max_per_query: int,
                  min_index: float, min_views: int, min_ratio: float = 0.0) -> list[dict]:
    yt = _youtube()
    own = get_channel_id()
    after = (datetime.now(timezone.utc) - timedelta(days=published_days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. search → video ids por query
    vid_query: dict[str, str] = {}
    for q in queries:
        try:
            r = yt.search().list(
                part="id", q=q, type="video", maxResults=min(max_per_query, 50),
                order="viewCount", publishedAfter=after,
                regionCode="MX", relevanceLanguage="es",
            ).execute()
        except Exception as e:
            print(f"  ⚠️ search '{q}' falló: {e}", file=sys.stderr)
            continue
        for it in r.get("items", []):
            vid = it["id"].get("videoId")
            if vid and vid not in vid_query:
                vid_query[vid] = q

    if not vid_query:
        return []

    # 2. videos.list → stats + canal + duración (batches de 50)
    vids = list(vid_query)
    vinfo: dict[str, dict] = {}
    for i in range(0, len(vids), 50):
        r = yt.videos().list(part="snippet,statistics,contentDetails",
                             id=",".join(vids[i:i + 50])).execute()
        for it in r.get("items", []):
            vinfo[it["id"]] = it

    # 3. channels.list → subs + uploads playlist (para baseline) — batches de 50
    ch_ids = sorted({v["snippet"]["channelId"] for v in vinfo.values()})
    subs: dict[str, int] = {}
    uploads_map: dict[str, str] = {}
    for i in range(0, len(ch_ids), 50):
        r = yt.channels().list(part="statistics,contentDetails",
                              id=",".join(ch_ids[i:i + 50])).execute()
        for it in r.get("items", []):
            hidden = it["statistics"].get("hiddenSubscriberCount")
            subs[it["id"]] = None if hidden else int(it["statistics"].get("subscriberCount", 0))
            uploads_map[it["id"]] = it["contentDetails"]["relatedPlaylists"]["uploads"]

    # 3b. baseline por canal = mediana views/día de sus uploads recientes
    baselines = _channel_baselines(yt, uploads_map)

    # 4. score = views/día (velocity) ÷ baseline del canal — age-normalizado en ambos lados
    rows = []
    for vid, it in vinfo.items():
        ch = it["snippet"]["channelId"]
        if ch == own:
            continue  # excluir nuestro propio canal
        views = int(it["statistics"].get("viewCount", 0))
        if views < min_views:
            continue
        age = _age_days(it["snippet"]["publishedAt"])
        vpd = views / age
        base = baselines.get(ch)
        s = subs.get(ch)
        ratio = round(views / s, 2) if s else None  # secundario (views/subs)
        if base:
            # Score primario real: velocity vs baseline del canal.
            index = round(vpd / base, 2)
            basis = "channel_baseline"
            if index < min_index:
                continue
            if min_ratio and (not ratio or ratio < min_ratio):
                continue
        else:
            # Canal sin baseline (nuevo / playlist vacía). NO contaminamos outlier_index
            # con views/subs (escala distinta). Solo se incluye si el usuario activó el
            # fallback con --min-ratio>0; si no, se omite para mantener el score limpio.
            if not min_ratio or not ratio or ratio < min_ratio:
                continue
            index = None              # sin baseline = sin índice comparable
            basis = "ratio_fallback"
        dmin = _dur_min(it["contentDetails"]["duration"])
        rows.append({
            "video_id": vid,
            "title": it["snippet"]["title"],
            "channel": it["snippet"]["channelTitle"],
            "channel_subs": s,
            "views": views,
            "views_per_day": round(vpd, 1),
            "outlier_index": index,   # score primario (vs baseline del canal); None si fallback
            "score_basis": basis,
            "ratio": ratio,                       # secundario (views/subs)
            "duration_min": dmin,
            "kind": _fmt_kind(dmin),
            "published_at": it["snippet"]["publishedAt"][:10],
            "query": vid_query[vid],
            "url": f"https://youtube.com/watch?v={vid}",
        })
    # outlier_index puede ser None (fallback sin baseline) → esos van al final
    rows.sort(key=lambda r: (r["outlier_index"] if r["outlier_index"] is not None else -1), reverse=True)
    return rows


def main():
    ap = argparse.ArgumentParser(description="Outlier finder nicho religioso (views > subs)")
    ap.add_argument("--queries", nargs="+", default=DEFAULT_QUERIES, help="queries semilla")
    ap.add_argument("--published-days", type=int, default=90, help="ventana de publicación (días)")
    ap.add_argument("--max-per-query", type=int, default=25, help="resultados por query (≤50)")
    ap.add_argument("--min-index", type=float, default=5.0,
                    help="índice mínimo = views/día ÷ baseline del canal (estándar Spotter/vidIQ)")
    ap.add_argument("--min-ratio", type=float, default=0.0,
                    help="filtro secundario views/subs (0 = off)")
    ap.add_argument("--min-views", type=int, default=5000, help="views mínimas (filtra ruido)")
    ap.add_argument("--top", type=int, default=25, help="cuántos mostrar en consola")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="JSON de salida")
    args = ap.parse_args()

    print(f"🔎 Outlier finder · {len(args.queries)} queries · últimos {args.published_days}d · "
          f"index≥{args.min_index}× canal · views≥{args.min_views}")
    rows = find_outliers(args.queries, args.published_days, args.max_per_query,
                         args.min_index, args.min_views, min_ratio=args.min_ratio)

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "params": {"queries": args.queries, "published_days": args.published_days,
                   "min_index": args.min_index, "min_ratio": args.min_ratio,
                   "min_views": args.min_views,
                   "score": "outlier_index = views/día ÷ mediana views/día del canal"},
        "count": len(rows),
        "outliers": rows,
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n  {len(rows)} outliers (index ≥ {args.min_index}× baseline del canal) → {args.out}\n")
    print(f"  {'index':>6} {'v/día':>8} {'views':>9} {'kind':<8} título")
    print(f"  {'-'*6} {'-'*8} {'-'*9} {'-'*8} {'-'*40}")
    for r in rows[:args.top]:
        idx = f"{r['outlier_index']:>6}" if r['outlier_index'] is not None else "  ~r{}".format(r['ratio'])
        print(f"  {idx:>6} {r['views_per_day']:>8,.0f} {r['views']:>9,} "
              f"{r['kind']:<8} {r['title'][:46]}")
    if not rows:
        print("  (sin outliers — baja --min-index o sube --published-days)")


if __name__ == "__main__":
    main()
