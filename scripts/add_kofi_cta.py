#!/usr/bin/env python3
"""
scripts/add_kofi_cta.py — Append Ko-fi CTA block to video descriptions missing it.

Usage:
    .venv/bin/python3 scripts/add_kofi_cta.py [--cluster historia|sleep|all] [--dry-run]

Clusters: historia_clasica, historia_misterio, historia_redemption, sleep_salmos, sleep_versos, lofi
Default: historia (sleep already done)
"""
from __future__ import annotations
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.youtube_client import _youtube

KOFI_BLOCK = (
    "\n\n☕ ¿Esta historia te tocó el corazón? Apoya el ministerio "
    "(gratis: PDF \"7 Días de Paz\" 🕊️):\n"
    "👉 ko-fi.com/versiculosdedios\n"
)

SLEEP_KOFI_BLOCK = (
    "\n\n☕ ¿Este contenido te bendice? Apoya el ministerio "
    "(gratis: PDF \"7 Días de Paz\" 🕊️):\n"
    "👉 ko-fi.com/versiculosdedios\n"
)

CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "data", "video_catalog.json")


def get_ids_by_cluster(cluster_filter: str) -> list[str]:
    with open(CATALOG_PATH) as f:
        cat = json.load(f)
    ids = []
    for v in cat.get("videos", []):
        yt_id = v.get("status", {}).get("youtube_id")
        cluster = v.get("topic_cluster", "")
        if not yt_id:
            continue
        if cluster_filter == "all" or cluster_filter in cluster:
            ids.append(yt_id)
    return ids


def main(cluster: str = "historia", dry_run: bool = False) -> None:
    ids = get_ids_by_cluster(cluster)
    if not ids:
        print(f"No videos found for cluster filter '{cluster}'")
        return

    print(f"Checking {len(ids)} videos (cluster={cluster}, dry_run={dry_run})")
    yt = _youtube()

    updated = skipped = 0
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        resp = yt.videos().list(part="snippet", id=",".join(batch)).execute()
        for item in resp.get("items", []):
            vid_id = item["id"]
            snippet = item["snippet"]
            desc = snippet["description"]
            if "ko-fi" in desc.lower():
                print(f"  skip  {vid_id}  (already has Ko-fi)")
                skipped += 1
                continue

            block = SLEEP_KOFI_BLOCK if "sleep" in cluster or "lofi" in cluster else KOFI_BLOCK
            new_desc = desc.rstrip() + block
            if dry_run:
                print(f"  [DRY]  {vid_id}  {snippet['title'][:55]}")
                updated += 1
                continue

            snippet["description"] = new_desc
            if "categoryId" not in snippet:
                snippet["categoryId"] = "27"
            yt.videos().update(
                part="snippet",
                body={"id": vid_id, "snippet": snippet}
            ).execute()
            print(f"  ✅  {vid_id}  {snippet['title'][:55]}")
            updated += 1
            time.sleep(0.5)

    print(f"\nDone: {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", default="historia",
                        help="Cluster filter: historia | sleep | lofi | all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(cluster=args.cluster, dry_run=args.dry_run)
