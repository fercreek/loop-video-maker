"""
fondo_pool.py — selecciona fondos coherentes con el tema.
Clasifica por BRILLO real (luminancia media con Pillow), no por nombre.
Contenido de dormir/noche → prefiere los fondos calmados/oscuros
(evita que salga un fondo diurno brillante en un video para dormir).
"""
import glob
from functools import lru_cache
from pathlib import Path

# Palabras que marcan contenido "noche / dormir / calma"
NIGHT_KEYS = ("dormir", "noche", "sleep", "paz", "miedo", "ansiedad",
              "reposo", "descans", "salmo91", "salmo23", "oracion", "reflexion")


def is_night(story_id: str) -> bool:
    s = (story_id or "").lower()
    return any(k in s for k in NIGHT_KEYS)


@lru_cache(maxsize=512)
def _brightness(path: str) -> float:
    """Luminancia media 0-255 (downscale para velocidad)."""
    try:
        from PIL import Image
        im = Image.open(path).convert("L").resize((64, 36))
        px = list(im.getdata())
        return sum(px) / len(px)
    except Exception:
        return 128.0  # neutral si falla


def calm_fondos(fondos_dir, max_brightness: float = 115.0) -> list[str]:
    """Fondos calmados/oscuros (luminancia <= umbral). Si ninguno, la mitad más oscura."""
    fondos = sorted(glob.glob(str(Path(fondos_dir) / "*.jpg")))
    if not fondos:
        return []
    scored = sorted((_brightness(f), f) for f in fondos)
    calm = [f for b, f in scored if b <= max_brightness]
    if calm:
        return calm
    return [f for _, f in scored[: max(1, len(scored) // 2)]]  # mitad más oscura


def pool_for(story_id: str, fondos_dir) -> list[str]:
    """Pool apropiado: calmado/noche si el tema lo pide, si no todos."""
    if is_night(story_id):
        return calm_fondos(fondos_dir)
    return sorted(glob.glob(str(Path(fondos_dir) / "*.jpg")))


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "output/fondos"
    fondos = sorted(glob.glob(str(Path(d) / "*.jpg")))
    rows = sorted((_brightness(f), Path(f).name) for f in fondos)
    print(f"{len(fondos)} fondos · luminancia 0-255 (oscuro→claro):")
    for b, n in rows:
        tag = "🌙 noche" if b <= 115 else "☀️ día"
        print(f"  {b:5.1f}  {tag}  {n}")
