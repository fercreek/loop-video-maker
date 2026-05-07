"""
scripts/generate_fondos_ai.py — Genera fondos religiosos únicos con Gemini Imagen 4.0.

Cada imagen: 1920×1080, estilo pintura al óleo, temática bíblica/religiosa.
Guarda en output/fondos/ con prefijo fondo_ai_*.jpg

Uso:
    python3 scripts/generate_fondos_ai.py              # genera 40 imágenes
    python3 scripts/generate_fondos_ai.py --count 20   # genera N imágenes
    python3 scripts/generate_fondos_ai.py --dry-run    # muestra prompts sin generar
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONDOS_DIR  = os.path.join(PROJECT_DIR, "output", "fondos")
CONFIG_PATH = os.path.join(PROJECT_DIR, "config.json")

IMAGEN_MODEL = "imagen-4.0-generate-001"
BASE_URL     = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGEN_MODEL}:predict"

# ─── Prompts ──────────────────────────────────────────────────────────────────
# Oil painting style, cinematic, high quality, no people, no text
STYLE = "masterpiece oil painting on canvas, dramatic painterly brushstrokes, warm cinematic lighting, no people, no text, no watermark, photorealistic texture, rich color palette, 16:9 landscape"

PROMPTS: list[tuple[str, str]] = [
    # Biblical landscapes
    ("galilee_sunrise",   f"Sea of Galilee at sunrise, golden light reflecting on calm water, ancient olive trees on hillside, dramatic clouds, {STYLE}"),
    ("jordan_valley",     f"Jordan River valley at dawn, lush green banks, mist rising from the water, rolling hills in background, {STYLE}"),
    ("judean_desert",     f"Judean desert at sunset, rocky hills in warm amber and purple light, ancient stone path, vast sky with clouds, {STYLE}"),
    ("mount_sinai",       f"Mount Sinai at dawn, dramatic rocky peaks piercing golden clouds, divine rays of light from above, {STYLE}"),
    ("holy_land_sunset",  f"Ancient Holy Land sunset, terraced olive groves on hillside, golden hour light, biblical landscape, {STYLE}"),
    ("dead_sea",          f"Dead Sea landscape at sunrise, salt flats reflecting rose-colored sky, distant mountains, ethereal atmosphere, {STYLE}"),
    ("galilee_storm",     f"Sea of Galilee during a dramatic storm, dark turbulent waters, rays of light breaking through dark clouds, {STYLE}"),
    ("gethsemane",        f"Garden of Gethsemane at night, ancient olive trees illuminated by moonlight, peaceful and sacred atmosphere, {STYLE}"),

    # Divine nature
    ("heaven_clouds",     f"Majestic heavenly clouds at golden hour, rays of divine light breaking through, dramatic sky, celestial atmosphere, {STYLE}"),
    ("divine_sunrise",    f"Breathtaking sunrise over ancient mountains, divine golden light radiating from horizon, sacred atmosphere, {STYLE}"),
    ("sacred_forest",     f"Ancient forest with rays of golden light filtering through cathedral-like trees, sacred grove, peaceful, {STYLE}"),
    ("mountain_glory",    f"Mountain summit above the clouds at sunrise, golden light, vast panoramic view, majestic and awe-inspiring, {STYLE}"),
    ("river_life",        f"Crystal clear river flowing through lush valley, green meadows, weeping willows, peaceful and serene, {STYLE}"),
    ("starry_desert",     f"Desert night with breathtaking starry sky, milky way visible, ancient stone formations, spiritual atmosphere, {STYLE}"),
    ("garden_eden",       f"Lush paradise garden with abundant flowers and fruit trees, warm golden light, waterfalls, ethereal atmosphere, {STYLE}"),
    ("promised_land",     f"Fertile promised land at harvest time, golden wheat fields, olive groves, distant hills, abundant blessings, {STYLE}"),

    # Peaceful water scenes
    ("still_waters",      f"Still mountain lake at dawn, mirror-like reflection of snow-capped peaks, mist rising, Psalm 23 atmosphere, {STYLE}"),
    ("waterfall_light",   f"Majestic waterfall surrounded by lush forest, rainbow in mist, divine light filtering through trees, {STYLE}"),
    ("ocean_worship",     f"Pacific ocean at sunrise, waves crashing on rocky shore, dramatic clouds, rays of light, worship atmosphere, {STYLE}"),
    ("river_baptism",     f"Ancient river in golden light, peaceful waters, green banks, ancient landscape, sacred and holy atmosphere, {STYLE}"),

    # Sky and cosmos
    ("storm_peace",       f"Storm clouds parting to reveal divine golden light, dramatic contrast of dark and light, powerful and hopeful, {STYLE}"),
    ("aurora_faith",      f"Northern lights over snow-covered landscape, ethereal green and purple aurora, stars, awe-inspiring, {STYLE}"),
    ("sunset_grace",      f"Spectacular sunset over rolling hills, clouds illuminated in pink and gold, peaceful countryside, grace and mercy, {STYLE}"),
    ("morning_glory",     f"Early morning light breaking over misty valley, dew on grass, birds in flight, new mercies every morning, {STYLE}"),
    ("night_stars",       f"Clear night sky with millions of stars over ancient desert landscape, Milky Way, Abraham's covenant stars, {STYLE}"),

    # Ancient sacred places
    ("ancient_temple",    f"Ancient stone temple ruins at sunset, columns and archways, golden light, spiritual and historic atmosphere, {STYLE}"),
    ("monastery_mountain",f"Ancient monastery perched on dramatic mountain cliff, clouds below, golden sunset, peaceful and sacred, {STYLE}"),
    ("pilgrimage_road",   f"Ancient pilgrimage road through scenic landscape, golden hills, olive trees, distant city, journey and faith, {STYLE}"),
    ("vineyard_harvest",  f"Ancient vineyard in harvest season, golden grapes, warm autumn light, gentle hills, joy and abundance, {STYLE}"),
    ("shepherd_hills",    f"Rolling green hills of Judea, ancient stone walls, olive trees, sheep grazing, Good Shepherd atmosphere, {STYLE}"),

    # Dramatic divine moments
    ("parting_waters",    f"Dramatic parting of waters, walls of water on both sides, path through, dramatic clouds and divine light, {STYLE}"),
    ("burning_bush",      f"Rugged desert mountain with dramatic fire-lit clouds at sunset, ancient rocky landscape, divine encounter atmosphere, {STYLE}"),
    ("dove_descending",   f"Peaceful river scene at golden hour, gentle light descending from above, baptism atmosphere, {STYLE}"),
    ("cross_sunrise",     f"Sunrise over hilltop, dramatic golden light, dark silhouette of trees, resurrection and hope atmosphere, {STYLE}"),
    ("spirit_fire",       f"Pentecost atmosphere, dramatic golden and orange sky, ancient city rooftops, wind and fire imagery, {STYLE}"),

    # Seasons and renewal
    ("spring_renewal",    f"Spring meadow with wildflowers, fruit trees in bloom, soft golden light, butterflies, renewal and resurrection, {STYLE}"),
    ("autumn_provision",  f"Autumn harvest landscape, golden and red trees, pumpkins and wheat, warm sunlight, God's provision, {STYLE}"),
    ("winter_hope",       f"Snow-covered ancient landscape, single candle of warm light in distance, hope in darkness, peaceful winter, {STYLE}"),
    ("rain_blessing",     f"Countryside after rain, rainbow over green hills, glistening light, fresh and alive, blessing after storm, {STYLE}"),
    ("cedar_forest",      f"Ancient cedar forest, massive trees like the cedars of Lebanon, shafts of golden light, majestic and sacred, {STYLE}"),
]


def load_api_key() -> str:
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f).get("gemini_api_key", "")
    except Exception:
        return ""


def generate_image(prompt: str, api_key: str) -> bytes | None:
    """Call Gemini Imagen 4 and return raw PNG bytes, or None on failure."""
    url = f"{BASE_URL}?key={api_key}"
    payload = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9",
            "safetyFilterLevel": "BLOCK_ONLY_HIGH",
        },
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
        b64 = resp["predictions"][0].get("bytesBase64Encoded", "")
        if b64:
            return base64.b64decode(b64)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"    HTTP {e.code}: {body}")
    except Exception as ex:
        print(f"    Error: {ex}")
    return None


def save_jpeg(png_bytes: bytes, path: str, quality: int = 92) -> None:
    """Convert PNG bytes to JPEG and resize to 1920×1080."""
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    # Crop to 16:9 if needed
    w, h = img.size
    target_ratio = 16 / 9
    current_ratio = w / h
    if abs(current_ratio - target_ratio) > 0.05:
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            x = (w - new_w) // 2
            img = img.crop((x, 0, x + new_w, h))
        else:
            new_h = int(w / target_ratio)
            y = (h - new_h) // 2
            img = img.crop((0, y, w, y + new_h))
    img = img.resize((1920, 1080), Image.LANCZOS)
    img.save(path, "JPEG", quality=quality)


def main():
    ap = argparse.ArgumentParser(description="Genera fondos religiosos con Gemini Imagen 4")
    ap.add_argument("--count",    type=int, default=40,
                    help="Cuántas imágenes generar (default: 40, max: {})".format(len(PROMPTS)))
    ap.add_argument("--dry-run",  action="store_true",
                    help="Muestra prompts sin generar")
    ap.add_argument("--overwrite",action="store_true",
                    help="Regenera aunque ya exista el archivo")
    args = ap.parse_args()

    api_key = load_api_key()
    if not api_key and not args.dry_run:
        print("❌ No hay gemini_api_key en config.json")
        sys.exit(1)

    os.makedirs(FONDOS_DIR, exist_ok=True)
    to_generate = PROMPTS[:args.count]

    print(f"\nGemini Imagen 4.0 — {len(to_generate)} fondos religiosos")
    print(f"Output: {FONDOS_DIR}")
    print(f"{'─'*60}\n")

    ok, skipped, failed = 0, 0, 0
    for stem, prompt in to_generate:
        out_path = os.path.join(FONDOS_DIR, f"fondo_ai_{stem}.jpg")

        if args.dry_run:
            print(f"  [{stem}] {prompt[:80]}...")
            continue

        if os.path.exists(out_path) and not args.overwrite:
            print(f"  [skip] fondo_ai_{stem}.jpg ya existe")
            skipped += 1
            continue

        print(f"  [gen]  fondo_ai_{stem}...", end=" ", flush=True)
        t0 = time.time()
        png = generate_image(prompt, api_key)
        elapsed = time.time() - t0

        if png:
            try:
                save_jpeg(png, out_path)
                size_kb = os.path.getsize(out_path) // 1024
                print(f"✓  {size_kb}KB  ({elapsed:.1f}s)")
                ok += 1
            except Exception as e:
                print(f"✗ save error: {e}")
                failed += 1
        else:
            print(f"✗ generation failed ({elapsed:.1f}s)")
            failed += 1

        time.sleep(0.5)  # rate limit

    if not args.dry_run:
        total_fondos = len([f for f in os.listdir(FONDOS_DIR) if f.endswith(".jpg")])
        print(f"\n{'─'*60}")
        print(f"Generados: {ok}  |  Saltados: {skipped}  |  Fallidos: {failed}")
        print(f"Total fondos en pool: {total_fondos}")


if __name__ == "__main__":
    main()
