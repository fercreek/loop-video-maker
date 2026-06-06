#!/usr/bin/env python3
"""Carnage exec — publica anuncio Ko-fi en FB Palabra De Dios + IG palabradedios111.
Brief: data/brief-kofi-fb-ig-2026-06-04.md · APROBADO Fernando 2026-06-04.
Patrón hosting IG: FB photo temporal -> CDN URL -> IG container (mismo que schedule_vd.py).
"""
import json, os, time, requests

TOKENS = os.path.expanduser("~/Documents/cero/cero-content/scripts/configs/tokens.json")
IMG = "/Users/fernandocastaneda/Documents/loop-video-maker/output/etsy/kofi_cover_7dias.jpg"
PAGE_ID = "452922677899760"
IG_ID = "17841469453382962"
GRAPH = "https://graph.facebook.com/v19.0"

COPY_FB = """🕊️ Quiero regalarte algo.

Por meses hemos compartido la Palabra cada día — y muchos me han preguntado cómo apoyar este ministerio.

Hoy preparé un regalo para ti: "7 Días de Paz", un devocional gratuito. 7 días, 7 versículos, listo para imprimir y vivir tu tiempo a solas con Dios.

Descárgalo gratis aquí 👉 ko-fi.com/versiculosdedios

Y si Dios pone en tu corazón apoyar para que sigamos llevando Su Palabra a más personas, ahí mismo puedes hacerlo. Pero el regalo es tuyo, sin costo. 🙏

"Y la paz de Dios, que sobrepasa todo entendimiento, guardará vuestros corazones." — Filipenses 4:7

Contenido creado con asistencia de IA 🙏"""

COPY_IG = """🕊️ Quiero regalarte algo.

"7 Días de Paz" — un devocional gratuito. 7 días, 7 versículos, listo para imprimir.

Descárgalo gratis (link en bio o en ko-fi.com/versiculosdedios) 🙏

El regalo es tuyo, sin costo. Y si quieres apoyar el ministerio, ahí mismo puedes.

"La paz de Dios sobrepasa todo entendimiento." — Filipenses 4:7

Contenido creado con asistencia de IA 🙏
.
.
#VersiculosDeDios #DevocionalDiario #PazDeDios #FeCristiana #PalabraDeDios #Oracion #DiosEsBueno"""

token = json.load(open(TOKENS))["palabra-de-dios"]
result = {"fb": None, "ig": None, "errors": []}

# === FB: subir foto + publicar feed post con imagen ===
try:
    with open(IMG, "rb") as f:
        r = requests.post(f"{GRAPH}/{PAGE_ID}/photos",
            data={"message": COPY_FB, "published": "true", "access_token": token},
            files={"source": ("kofi_cover_7dias.jpg", f, "image/jpeg")})
    r.raise_for_status()
    j = r.json()
    photo_id = j.get("id")
    post_id = j.get("post_id")
    result["fb"] = {"photo_id": photo_id, "post_id": post_id}
    print(f"[FB] OK photo_id={photo_id} post_id={post_id}")
except Exception as e:
    body = getattr(e, "response", None)
    result["errors"].append(f"FB: {e} | {body.text if body is not None else ''}")
    print(f"[FB] ERROR: {result['errors'][-1]}")

# === IG: necesita URL pública. Reusar CDN URL de la foto FB recién subida ===
cdn_url = None
if result["fb"] and result["fb"].get("photo_id"):
    try:
        r = requests.get(f"{GRAPH}/{result['fb']['photo_id']}",
            params={"fields": "images", "access_token": token})
        r.raise_for_status()
        imgs = r.json().get("images", [])
        if imgs:
            cdn_url = max(imgs, key=lambda x: x.get("width", 0))["source"]
            print(f"[IG] CDN URL obtenida: {cdn_url[:80]}...")
    except Exception as e:
        result["errors"].append(f"IG cdn_url: {e}")
        print(f"[IG] ERROR cdn_url: {e}")

if cdn_url:
    try:
        r = requests.post(f"{GRAPH}/{IG_ID}/media",
            data={"image_url": cdn_url, "caption": COPY_IG, "access_token": token})
        r.raise_for_status()
        container = r.json()["id"]
        print(f"[IG] container={container}, esperando FINISHED...")
        status = ""
        for _ in range(20):
            time.sleep(3)
            status = requests.get(f"{GRAPH}/{container}",
                params={"fields": "status_code", "access_token": token}).json().get("status_code", "")
            if status in ("FINISHED", "ERROR"):
                break
        if status != "FINISHED":
            raise Exception(f"container status={status}")
        r2 = requests.post(f"{GRAPH}/{IG_ID}/media_publish",
            data={"creation_id": container, "access_token": token})
        r2.raise_for_status()
        ig_media_id = r2.json()["id"]
        result["ig"] = {"container_id": container, "media_id": ig_media_id}
        print(f"[IG] OK media_id={ig_media_id}")
    except Exception as e:
        body = getattr(e, "response", None)
        result["errors"].append(f"IG publish: {e} | {body.text if body is not None else ''}")
        print(f"[IG] ERROR: {result['errors'][-1]}")
else:
    result["errors"].append("IG: sin cdn_url (FB falló) -> IG pendiente")

print("\n=== RESULT ===")
print(json.dumps(result, indent=2, ensure_ascii=False))
