"""
scripts/download_fondos.py — Download public-domain oil paintings for the bg pool.

Source: The Metropolitan Museum of Art Open Access API
  https://metmuseum.github.io/ — free, no auth, high-res JPEGs.

Usage:
  .venv/bin/python3 scripts/download_fondos.py

Downloads to output/fondos/ — skips existing files.
Target: 30+ images in pool.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONDOS_DIR  = os.path.join(PROJECT_DIR, "output", "fondos")

MET_API     = "https://collectionapi.metmuseum.org/public/collection/v1"
MET_HEADERS = {"User-Agent": "loop-video-maker/3.9 (devotional-channel)"}

# ─── Curated Met object IDs ───────────────────────────────────────────────────
# All Hudson River School / American luminism / European romantic landscapes.
# IDs verified against Met Open Access catalog (isPublicDomain=true).
CURATED = [
    # Thomas Cole — Hudson River School founder
    ("fondo_cole_oxbow",         11417),
    ("fondo_cole_schroon",       11406),
    ("fondo_cole_dream",         11401),   # Dream of Arcadia
    ("fondo_cole_voyage1",       11387),   # Voyage of Life: Youth
    ("fondo_cole_voyage2",       11386),   # Voyage of Life: Manhood

    # Frederic Edwin Church
    ("fondo_church_twilight",    11290),
    ("fondo_church_jamaican",    11279),
    ("fondo_church_rainy",       11295),   # Rainy Season in the Tropics

    # George Inness — luminism, spiritual atmosphere
    ("fondo_inness_delaware",    11505),   # Delaware Water Gap
    ("fondo_inness_summer",      11504),   # Summer, Montclair

    # Albert Bierstadt — grand western vistas
    ("fondo_bierstadt_catskills", 11012),
    ("fondo_bierstadt_mtn",       11011),  # Mountain Brook
    ("fondo_bierstadt_merced",    11014),  # Valley of the Yosemite

    # Sanford Gifford — luminism, golden haze
    ("fondo_gifford_kauterskill", 11388),
    ("fondo_gifford_hunter",      11395),
    ("fondo_gifford_roman",       11396),  # A Gorge in the Mountains (Kauterskill Clove)

    # Asher B. Durand
    ("fondo_durand_woodland",     10481),
    ("fondo_durand_progress",     10488),  # Progress (The Advance of Civilization)
    ("fondo_durand_morning",      10486),  # Morning of Life

    # Worthington Whittredge — meadows, quiet nature
    ("fondo_whittredge_camp",     11438),  # Camp Meeting

    # John Frederick Kensett — serene water/air
    ("fondo_kensett_rhine",       12208),  # View on the Rhine
    ("fondo_kensett_beach",       12224),  # Beach at Beverly

    # Martin Johnson Heade — luminism, atmospheric
    ("fondo_heade_marsh",         10869),  # Sunrise on the Marshes
    ("fondo_heade_hay",           10870),  # Haystacks on the Newburyport Marshes

    # William Trost Richards — detailed landscapes
    ("fondo_richards_coast",      13449),  # On the Coast of New Jersey

    # Thomas Moran — vivid color, spiritual light
    ("fondo_moran_venice",        12651),  # Venice
    ("fondo_moran_cliffs",        12652),  # Cliffs of the Upper Colorado River, Wyoming Territory

    # European romantics
    ("fondo_corot_morning",       11133),  # Morning — Corot
    ("fondo_rousseau_forest",     11144),  # Forest of Fontainebleau — Rousseau
    ("fondo_daubigny_stream",     11137),  # Banks of the Oise — Daubigny
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=MET_HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())


def download_image(url: str, out_path: str) -> int:
    req = urllib.request.Request(url, headers=MET_HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp, open(out_path, "wb") as f:
        data = resp.read()
        f.write(data)
    return len(data)


def fetch_one(stem: str, obj_id: int) -> bool:
    out_path = os.path.join(FONDOS_DIR, f"{stem}.jpg")
    if os.path.exists(out_path):
        return True   # skip silently

    try:
        obj = fetch_json(f"{MET_API}/objects/{obj_id}")
        img_url = obj.get("primaryImage") or obj.get("primaryImageSmall", "")
        if not img_url:
            print(f"  ⚠ {stem} (id={obj_id}): no image")
            return False
        size = download_image(img_url, out_path)
        if size < 30_000:
            os.remove(out_path)
            print(f"  ⚠ {stem}: image too small ({size//1024}KB)")
            return False
        title = obj.get("title", "?")[:50]
        print(f"  OK {stem}  {size//1024}KB  [{title}]")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ⚠ {stem} (id={obj_id}): HTTP {e.code}")
        return False
    except Exception as e:
        if os.path.exists(out_path):
            os.remove(out_path)
        print(f"  ❌ {stem}: {e}")
        return False


def search_fallback(stem: str, artist: str, keyword: str) -> bool:
    """Search Met for a painting by artist+keyword. Returns True on success."""
    out_path = os.path.join(FONDOS_DIR, f"{stem}.jpg")
    if os.path.exists(out_path):
        return True

    query = f"{artist} {keyword}"
    try:
        result = fetch_json(
            f"{MET_API}/search?q={urllib.parse.quote(query)}"
            "&hasImages=true&isPublicDomain=true"
        )
        ids = result.get("objectIDs") or []
        for oid in ids[:8]:
            try:
                obj = fetch_json(f"{MET_API}/objects/{oid}")
                if obj.get("medium", "").lower().find("oil") < 0:
                    continue
                img_url = obj.get("primaryImage", "")
                if not img_url:
                    continue
                size = download_image(img_url, out_path)
                if size < 100_000:
                    os.remove(out_path)
                    continue
                title = obj.get("title", "?")[:50]
                print(f"  OK {stem} [search]  {size//1024}KB  [{title}]")
                return True
            except Exception:
                continue
    except Exception as e:
        print(f"  ❌ search {stem}: {e}")
    return False


# Extra search fallbacks if curated IDs fail / pool still below target
SEARCH_EXTRA = [
    ("fondo_crop_harvest",   "Winslow Homer",   "harvest fields"),
    ("fondo_meadow_light",   "George Inness",   "meadow light"),
    ("fondo_mountain_creek", "Asher Durand",    "mountain stream"),
    ("fondo_golden_valley",  "Thomas Cole",     "valley pastoral"),
    ("fondo_ocean_calm",     "Martin Heade",    "calm ocean coast"),
]


def main() -> None:
    os.makedirs(FONDOS_DIR, exist_ok=True)
    import glob

    # Count existing
    existing = set(
        os.path.basename(f).rsplit(".", 1)[0]
        for f in glob.glob(os.path.join(FONDOS_DIR, "*.jpg"))
        + glob.glob(os.path.join(FONDOS_DIR, "*.png"))
        if not os.path.basename(f).startswith("imagen_")
    )
    print(f"\nMet Museum Open Access download → {FONDOS_DIR}")
    print(f"Already have: {len(existing)} fondos\n")

    ok = fail = 0
    for stem, obj_id in CURATED:
        if stem in existing:
            continue   # already downloaded
        success = fetch_one(stem, obj_id)
        (ok if success else fail).__class__  # dummy
        if success:
            ok += 1
        else:
            fail += 1
        time.sleep(0.15)

    # Search fallbacks to hit target of 30
    all_now = [f for f in glob.glob(os.path.join(FONDOS_DIR, "*.jpg"))
               + glob.glob(os.path.join(FONDOS_DIR, "*.png"))
               if not os.path.basename(f).startswith("imagen_")]
    if len(all_now) < 30:
        print(f"\n--- Search fallbacks ({30 - len(all_now)} more needed) ---")
        for stem, artist, kw in SEARCH_EXTRA:
            if stem not in existing and len(all_now) < 30:
                if search_fallback(stem, artist, kw):
                    ok += 1
                else:
                    fail += 1
                all_now = [f for f in glob.glob(os.path.join(FONDOS_DIR, "*.jpg"))
                           if not os.path.basename(f).startswith("imagen_")]
                time.sleep(0.2)

    all_final = [f for f in glob.glob(os.path.join(FONDOS_DIR, "*.jpg"))
                 + glob.glob(os.path.join(FONDOS_DIR, "*.png"))
                 if not os.path.basename(f).startswith("imagen_")]
    # Drop tiny images
    dropped = 0
    for f in all_final:
        try:
            from PIL import Image as _PIL
            img = _PIL.open(f)
            if img.size[0] < 800 or img.size[1] < 600:
                os.remove(f)
                dropped += 1
        except Exception:
            pass

    all_final2 = [f for f in glob.glob(os.path.join(FONDOS_DIR, "*.jpg"))
                  + glob.glob(os.path.join(FONDOS_DIR, "*.png"))
                  if not os.path.basename(f).startswith("imagen_")]

    print(f"\n{'='*50}")
    print(f"  New this run: {ok}  |  Skipped/failed: {fail}  |  Dropped small: {dropped}")
    print(f"  Total fondos pool: {len(all_final2)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
