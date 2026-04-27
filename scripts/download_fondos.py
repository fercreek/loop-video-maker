"""
scripts/download_fondos.py — Download 50+ public-domain oil paintings.

Sources:
  1. Metropolitan Museum of Art Open Access API (metmuseum.github.io)
  2. Art Institute of Chicago Open Access API (api.artic.edu)

Both are free, no auth required, high-res JPEGs via IIIF.
All results: isPublicDomain=true, landscape orientation, oil on canvas.

Usage:
  .venv/bin/python3 scripts/download_fondos.py

Target: 50 fondos in output/fondos/ (skips existing).
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
TARGET      = 50
MIN_WIDTH   = 1200
MIN_HEIGHT  = 700

MET_API = "https://collectionapi.metmuseum.org/public/collection/v1"
AIC_API = "https://api.artic.edu/api/v1"
HEADERS = {"User-Agent": "loop-video-maker/3.9 (devotional-youtube)"}


# ─── Met Museum curated IDs ───────────────────────────────────────────────────
MET_CURATED = [
    # Thomas Cole
    ("fondo_cole_oxbow",         11417),
    ("fondo_cole_voyage1",       11399),
    ("fondo_cole_catskill2",     11402),
    ("fondo_cole_expulsion",     11410),
    ("fondo_cole_arcadian",      11414),
    # Frederic Church
    ("fondo_church_jamaican",    11279),
    ("fondo_church_niagara",     11300),
    # George Inness
    ("fondo_inness_peace",       11508),
    ("fondo_inness_delaware2",   11503),
    # Albert Bierstadt
    ("fondo_bierstadt_catskills", 11012),
    ("fondo_bierstadt_mtn",       11011),
    ("fondo_bierstadt_sierra",    11013),
    # Sanford Gifford
    ("fondo_gifford_kauterskill", 11388),
    ("fondo_gifford_hunter",      11395),
    ("fondo_gifford_roman",       11396),
    # Asher Durand
    ("fondo_durand_woodland",     10481),
    ("fondo_durand_kindred",      10485),
    # Martin Heade
    ("fondo_heade_sunrise",       10865),
    ("fondo_heade_newbury",       10868),
    # Thomas Moran
    ("fondo_moran_cliffs",        12652),
    ("fondo_moran_mountain",      12655),
    # European romantics
    ("fondo_corot_morning",       11133),
    ("fondo_rousseau_forest",     11144),
    ("fondo_daubigny_stream",     11137),
    ("fondo_troyon_cattle",       11140),
    ("fondo_diaz_forest",         11141),
    # Winslow Homer
    ("fondo_homer_adirondacks",   11237),
    ("fondo_homer_coast",         11231),
    # John Kensett
    ("fondo_kensett_coast2",      11451),
    ("fondo_kensett_george2",     12154),
]

# ─── AIC search queries — oil landscape paintings ────────────────────────────
AIC_QUERIES = [
    "landscape sunrise golden",
    "pastoral meadow valley",
    "mountain forest light",
    "ocean seascape calm",
    "river countryside",
    "sky clouds dramatic",
    "forest path sunlight",
    "lake reflection serene",
    "harvest wheat field",
    "holy land landscape",
    "desert oasis biblical",
    "garden eden paradise",
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def dl_image(url: str, path: str) -> int:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
        data = r.read()
        f.write(data)
    return len(data)


def is_good(path: str) -> bool:
    try:
        from PIL import Image
        img = Image.open(path)
        w, h = img.size
        return w >= MIN_WIDTH and h >= MIN_HEIGHT and w / h > 1.0
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Source 1: Met Museum
# ──────────────────────────────────────────────────────────────────────────────

def met_fetch(stem: str, obj_id: int) -> bool:
    path = os.path.join(FONDOS_DIR, f"{stem}.jpg")
    if os.path.exists(path):
        return True
    try:
        obj  = fetch_json(f"{MET_API}/objects/{obj_id}")
        url  = obj.get("primaryImage") or obj.get("primaryImageSmall", "")
        if not url:
            return False
        size = dl_image(url, path)
        if size < 40_000 or not is_good(path):
            os.remove(path)
            return False
        print(f"  MET  {stem}  {size//1024}KB")
        return True
    except Exception:
        if os.path.exists(path):
            os.remove(path)
        return False


def met_search(stem: str, query: str) -> bool:
    path = os.path.join(FONDOS_DIR, f"{stem}.jpg")
    if os.path.exists(path):
        return True
    try:
        res = fetch_json(
            f"{MET_API}/search?q={urllib.parse.quote(query)}"
            "&hasImages=true&isPublicDomain=true"
        )
        for oid in (res.get("objectIDs") or [])[:10]:
            try:
                obj = fetch_json(f"{MET_API}/objects/{oid}")
                if "oil" not in obj.get("medium", "").lower():
                    continue
                url = obj.get("primaryImage", "")
                if not url:
                    continue
                size = dl_image(url, path)
                if size < 100_000 or not is_good(path):
                    if os.path.exists(path):
                        os.remove(path)
                    continue
                print(f"  MET  {stem} [search]  {size//1024}KB  [{obj.get('title','?')[:40]}]")
                return True
            except Exception:
                continue
    except Exception:
        pass
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Source 2: Art Institute of Chicago
# ──────────────────────────────────────────────────────────────────────────────

def aic_search(query: str, existing_stems: set, max_results: int = 8) -> list[tuple[str, str]]:
    """
    Search AIC for landscape oil paintings. Returns list of (stem, image_url).
    Skips IDs that already exist in fondos dir.
    """
    results = []
    try:
        params = urllib.parse.urlencode({
            "q": query,
            "fields": "id,title,image_id,is_public_domain,medium_display,width,height",
            "limit": 50,
        })
        data = fetch_json(f"{AIC_API}/artworks/search?{params}")
        artworks = data.get("data", [])
        for art in artworks:
            if len(results) >= max_results:
                break
            if not art.get("is_public_domain"):
                continue
            img_id = art.get("image_id")
            if not img_id:
                continue
            medium = (art.get("medium_display") or "").lower()
            if "oil" not in medium and "painting" not in medium:
                continue
            # Prefer landscape aspect ratio
            w = art.get("width", 0)
            h = art.get("height", 0)
            if h and w and (w / h) < 1.0:
                continue   # skip portrait
            stem = f"fondo_aic_{art['id']}"
            if stem in existing_stems:
                continue
            # IIIF URL: 3000px wide
            img_url = f"https://www.artic.edu/iiif/2/{img_id}/full/3000,/0/default.jpg"
            results.append((stem, img_url, art.get("title", "?")[:40]))
    except Exception as e:
        print(f"  AIC search error ({query}): {e}")
    return results


def aic_download(stem: str, url: str, title: str) -> bool:
    path = os.path.join(FONDOS_DIR, f"{stem}.jpg")
    if os.path.exists(path):
        return True
    try:
        size = dl_image(url, path)
        if size < 80_000 or not is_good(path):
            if os.path.exists(path):
                os.remove(path)
            return False
        print(f"  AIC  {stem}  {size//1024}KB  [{title}]")
        return True
    except Exception:
        if os.path.exists(path):
            os.remove(path)
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def count_fondos() -> int:
    import glob
    return len([
        f for f in glob.glob(os.path.join(FONDOS_DIR, "*.jpg"))
        + glob.glob(os.path.join(FONDOS_DIR, "*.png"))
        if not os.path.basename(f).startswith("imagen_")
    ])


def existing_stems() -> set:
    import glob
    return {
        os.path.basename(f).rsplit(".", 1)[0]
        for f in glob.glob(os.path.join(FONDOS_DIR, "*.jpg"))
        + glob.glob(os.path.join(FONDOS_DIR, "*.png"))
        if not os.path.basename(f).startswith("imagen_")
    }


def main() -> None:
    os.makedirs(FONDOS_DIR, exist_ok=True)
    print(f"\nDownloading oil paintings → {FONDOS_DIR}")
    print(f"Have: {count_fondos()}  |  Target: {TARGET}\n")

    ok = fail = 0

    # ── Phase 1: Met curated IDs ─────────────────────────────────────────────
    print("--- Phase 1: Met Museum curated IDs ---")
    for stem, oid in MET_CURATED:
        if count_fondos() >= TARGET:
            break
        stems = existing_stems()
        if stem in stems:
            continue
        if met_fetch(stem, oid):
            ok += 1
        else:
            fail += 1
        time.sleep(0.15)

    # ── Phase 2: AIC search ──────────────────────────────────────────────────
    if count_fondos() < TARGET:
        print(f"\n--- Phase 2: Art Institute of Chicago search ---")
        for query in AIC_QUERIES:
            if count_fondos() >= TARGET:
                break
            stems = existing_stems()
            candidates = aic_search(query, stems, max_results=5)
            for stem, url, title in candidates:
                if count_fondos() >= TARGET:
                    break
                if aic_download(stem, url, title):
                    ok += 1
                else:
                    fail += 1
                time.sleep(0.2)

    # ── Phase 3: Met search fallback ─────────────────────────────────────────
    if count_fondos() < TARGET:
        print(f"\n--- Phase 3: Met search fallback ---")
        extra_queries = [
            ("landscape golden light", "fondo_met_extra_1"),
            ("pastoral American 1850", "fondo_met_extra_2"),
            ("mountain river valley",  "fondo_met_extra_3"),
            ("seascape ocean coast",   "fondo_met_extra_4"),
            ("sunrise dawn sky",       "fondo_met_extra_5"),
        ]
        for query, stem in extra_queries:
            if count_fondos() >= TARGET:
                break
            if stem in existing_stems():
                continue
            if met_search(stem, query):
                ok += 1
            else:
                fail += 1
            time.sleep(0.25)

    total = count_fondos()
    print(f"\n{'='*55}")
    print(f"  New downloaded: {ok}  |  Failed: {fail}")
    print(f"  Total fondos pool: {total}  (target {TARGET})")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
