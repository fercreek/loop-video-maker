#!/usr/bin/env python3
"""
scripts/tag_catalog.py — Backfill topic_cluster field in data/video_catalog.json

Assigns a cluster to every video so niche_report.py can aggregate by cluster.

Clusters:
  historia_misterio   — "hidden story" angle (what happened after, lesser-known)
  historia_redemption — transformation/second-chance stories
  historia_clasica    — default for classic Bible historia/personaje
  tematico            — thematic / doctrinal videos
  devocional          — devotional / reflective
  sleep_salmos        — sleep content with Psalms
  sleep_versos        — sleep content with verses/music
  lofi                — lo-fi Christian music
  devocional_corto    — Shorts / videos <5min

Run once, then re-run when new videos are added:
    .venv/bin/python3 scripts/tag_catalog.py
"""
from __future__ import annotations

import json
import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(PROJECT_DIR, "data", "video_catalog.json")
SCHEDULE_PATH = os.path.join(PROJECT_DIR, "data", "upload_schedule.json")


MISTERIO_IDS = {
    "vida-maria-despues-cruz", "lazaro-resurreccion", "vida-tiempos-jesus",
    "maria-magdalena", "tres-dias-sepulcro", "que-paso-despues",
    "bernabe-hijo-consolacion", "abigail-mujer-sabia",
}

MISTERIO_TITLE_PATTERNS = [
    r"así vivió", r"así era", r"los años que nadie", r"lo que nadie",
    r"qué pasó", r"qué contó", r"los 3 días", r"misterio", r"secreto",
    r"la noche que", r"lo que jesús", r"la conversación secreta",
]

REDEMPTION_IDS = {
    "hijo-prodigo", "pablo-camino-damasco", "zaqueo-cobrador",
    "ladron-en-la-cruz", "ananias-y-safira", "david-y-betsabe",
    "mujer-samaritana-pozo", "mujer-toco-manto",
}

REDEMPTION_TITLE_PATTERNS = [
    r"hijo pródigo", r"ladrón", r"perdona", r"perdonó", r"regresó",
    r"segunda oportunidad", r"de la oscuridad", r"cobrador de impuest",
]


def classify_catalog_video(video: dict) -> str:
    vid_id = video.get("id", "").lower()
    title  = video.get("title", "").lower()
    vtype  = video.get("type", "historia")
    dur    = video.get("duration_est_min", 99)

    # Shorts / very short
    if dur < 5 or vtype == "short":
        return "devocional_corto"

    # Devocional
    if vtype == "devocional":
        return "devocional"

    # Tematico
    if vtype == "tematico":
        return "tematico"

    # Sleep / lofi (shouldn't be in catalog but handle gracefully)
    if "sleep" in vid_id or "lofi" in vid_id or "dormir" in title:
        if "salmo" in title or "salmo" in vid_id:
            return "sleep_salmos"
        if "lofi" in vid_id or "lofi" in title:
            return "lofi"
        return "sleep_versos"

    # Historia misterio
    if vid_id in MISTERIO_IDS:
        return "historia_misterio"
    for pat in MISTERIO_TITLE_PATTERNS:
        if re.search(pat, title):
            return "historia_misterio"

    # Historia redemption
    if vid_id in REDEMPTION_IDS:
        return "historia_redemption"
    for pat in REDEMPTION_TITLE_PATTERNS:
        if re.search(pat, title):
            return "historia_redemption"

    # Default for historia + personaje
    return "historia_clasica"


def infer_schedule_cluster(entry: dict) -> str:
    story_id = entry.get("story_id", "").lower()
    title    = entry.get("title", "").lower()

    if "lofi" in story_id or "lofi" in title:
        return "lofi"
    if "sleep" in story_id or "dormir" in title or "para dormir" in title:
        if "salmo" in title or "salmo" in story_id:
            return "sleep_salmos"
        return "sleep_versos"
    if "salmos" in story_id or "salmos" in title:
        return "sleep_salmos"
    if any(x in story_id for x in ["120min", "60min", "90min", "larga"]):
        return "sleep_versos"
    return "historia_clasica"


def main() -> None:
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    changed = 0
    for v in catalog["videos"]:
        cluster = classify_catalog_video(v)
        if v.get("topic_cluster") != cluster:
            v["topic_cluster"] = cluster
            changed += 1

    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"  Tagged {changed} videos in {CATALOG_PATH}")

    # Show summary by cluster
    from collections import Counter
    counts = Counter(v.get("topic_cluster") for v in catalog["videos"])
    print("\n  Cluster breakdown:")
    for cluster, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {cluster:<25} {count:>3} videos")


if __name__ == "__main__":
    main()
