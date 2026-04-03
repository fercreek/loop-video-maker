"""
Generación de imágenes de fondo.
- Local: 12 presets visuales con diferentes estilos de renderizado
- Gemini API: cuando el usuario configure su key
"""
from __future__ import annotations

import os
import math
import random
from datetime import datetime


# ─── Presets visuales ──────────────────────────────────────────────────────────

STYLE_PRESETS = {
    "amanecer_dorado": {
        "label": "Amanecer dorado",
        "keywords": ["amanecer", "mañana", "alba", "esperanza"],
        "style": "diagonal_gradient",
        "colors": [(10, 5, 30), (80, 30, 60), (180, 80, 20), (230, 150, 40)],
        "overlay": None,
    },
    "cielo_nocturno": {
        "label": "Cielo nocturno",
        "keywords": ["noche", "estrellas", "oscuro", "cosmos", "cielo"],
        "style": "starfield",
        "colors": [(5, 5, 20), (10, 10, 40), (15, 15, 60)],
        "overlay": None,
    },
    "luz_divina": {
        "label": "Luz divina",
        "keywords": ["luz", "gloria", "divino", "sagrado", "dios"],
        "style": "radial_gradient",
        "colors": [(240, 220, 160), (180, 130, 60), (80, 50, 20), (15, 10, 35)],
        "overlay": "rays",
    },
    "piedra_antigua": {
        "label": "Piedra antigua",
        "keywords": ["piedra", "roca", "antiguo", "templo", "fundamento"],
        "style": "stone_texture",
        "colors": [(70, 55, 45), (50, 40, 32), (35, 28, 22)],
        "overlay": None,
    },
    "agua_viva": {
        "label": "Agua viva",
        "keywords": ["agua", "río", "mar", "océano", "vida"],
        "style": "horizontal_gradient",
        "colors": [(5, 20, 50), (10, 50, 80), (20, 80, 100), (10, 40, 70)],
        "overlay": None,
    },
    "nube_celestial": {
        "label": "Nube celestial",
        "keywords": ["nube", "cielo", "blanco", "paz", "suave"],
        "style": "cloud_texture",
        "colors": [(180, 190, 210), (140, 155, 185), (100, 120, 160)],
        "overlay": None,
    },
    "aurora_boreal": {
        "label": "Aurora boreal",
        "keywords": ["aurora", "color", "arcoiris", "maravilla"],
        "style": "diagonal_gradient",
        "colors": [(10, 5, 40), (30, 20, 80), (20, 80, 90), (10, 120, 80)],
        "overlay": None,
    },
    "desierto_sagrado": {
        "label": "Desierto sagrado",
        "keywords": ["desierto", "arena", "seco", "provision", "maná"],
        "style": "diagonal_gradient",
        "colors": [(15, 10, 5), (80, 50, 20), (140, 90, 40), (100, 65, 25)],
        "overlay": None,
    },
    "gloria_eterna": {
        "label": "Gloria eterna",
        "keywords": ["gloria", "eterno", "corona", "victoria", "triunfo"],
        "style": "radial_gradient",
        "colors": [(255, 240, 180), (200, 160, 60), (100, 70, 20), (20, 15, 40)],
        "overlay": "rings",
    },
    "bosque_profundo": {
        "label": "Bosque profundo",
        "keywords": ["bosque", "árbol", "naturaleza", "verde", "campo"],
        "style": "radial_gradient",
        "colors": [(5, 30, 10), (10, 50, 20), (20, 80, 35), (5, 20, 8)],
        "overlay": None,
    },
    "sangre_de_cristo": {
        "label": "Sangre de Cristo",
        "keywords": ["cruz", "sangre", "sacrificio", "amor", "redención"],
        "style": "radial_gradient",
        "colors": [(80, 5, 10), (50, 5, 8), (25, 3, 5), (10, 2, 3)],
        "overlay": "cross",
    },
    "paz_clasica": {
        "label": "Paz clásica",
        "keywords": ["paz", "calma", "meditación", "salmo", "descanso"],
        "style": "linear_gradient",
        "colors": [(8, 15, 45), (15, 30, 70), (5, 10, 30)],
        "overlay": None,
    },
}

# Para el dropdown de UI
PRESET_LABELS = {v["label"]: k for k, v in STYLE_PRESETS.items()}


# ─── API pública ───────────────────────────────────────────────────────────────

def generar_imagen(prompt: str, api_key: str, output_dir: str = "output",
                   preset_key: str = None) -> str:
    """
    Genera imagen de fondo 1920x1080.
    Si hay API key de Gemini, intenta usarla.
    Si no, genera con el preset local seleccionado.
    """
    os.makedirs(output_dir, exist_ok=True)

    if api_key:
        try:
            return _generar_con_gemini(prompt, api_key, output_dir)
        except Exception as e:
            print(f"Gemini falló ({e}), usando preset local...")

    return _generar_gradiente(prompt, output_dir, preset_key=preset_key)


def generar_imagen_rapida(color_hex: str = "#1a1a3e", output_dir: str = "output") -> str:
    """Genera una imagen sólida rápida para preview sin música/imagen configurada."""
    from PIL import Image

    os.makedirs(output_dir, exist_ok=True)
    color_hex = color_hex.lstrip("#")
    r, g, b = int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16)
    img = Image.new("RGB", (1920, 1080), (r, g, b))
    # Fixed name — intentional: rapid preview placeholder, one per color, reused across sessions
    path = os.path.join(output_dir, "imagen_rapida_preview.jpg")
    img.save(path, quality=95)
    return os.path.abspath(path)


# ─── Dispatcher ────────────────────────────────────────────────────────────────

def _generar_gradiente(prompt: str, output_dir: str, preset_key: str = None) -> str:
    """Dispatcher: elige preset y llama al renderer correspondiente."""
    from PIL import Image, ImageFilter
    import numpy as np

    width, height = 1920, 1080
    preset = _elegir_preset(prompt, preset_key)
    style = preset["style"]
    colors = preset["colors"]

    if style == "starfield":
        img_array = _render_starfield(colors, width, height)
    elif style == "radial_gradient":
        img_array = _render_radial_gradient(colors, width, height)
    elif style == "stone_texture":
        img_array = _render_stone_texture(colors, width, height)
    elif style == "cloud_texture":
        img_array = _render_cloud_texture(colors, width, height)
    elif style == "horizontal_gradient":
        img_array = _render_linear_gradient(colors, width, height, "horizontal")
    elif style == "diagonal_gradient":
        img_array = _render_linear_gradient(colors, width, height, "diagonal")
    else:
        img_array = _render_linear_gradient(colors, width, height, "vertical")

    # Ruido sutil para evitar bandas
    import numpy as np
    noise = np.random.randint(-6, 6, (height, width, 3), dtype=np.int16)
    img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    img = Image.fromarray(img_array)
    img = img.filter(ImageFilter.GaussianBlur(radius=2))

    # Overlays opcionales
    overlay = preset.get("overlay")
    if overlay == "rays":
        img = _overlay_rays(img, width, height)
    elif overlay == "rings":
        img = _overlay_rings(img, width, height)
    elif overlay == "cross":
        img = _overlay_cross(img, width, height)

    # Viñeta siempre
    img = _apply_vignette(img, width, height)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"imagen_{ts}.jpg")
    img.save(path, quality=95)
    return os.path.abspath(path)


# ─── Renderers ─────────────────────────────────────────────────────────────────

def _render_linear_gradient(colors: list, width: int, height: int,
                             direction: str = "vertical"):
    """Gradiente lineal multi-color en dirección vertical, horizontal o diagonal."""
    import numpy as np

    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    n = len(colors)

    # Jitter de ángulo para variación entre renders
    angle_jitter = random.uniform(-0.1, 0.1)

    for y in range(height):
        for_x = 0  # solo en diagonal
        if direction == "vertical":
            t = y / height
        elif direction == "horizontal":
            t = 0.5  # se calculará por x abajo
            pass
        else:  # diagonal
            t = (y / height + angle_jitter) % 1.0

        if direction == "horizontal":
            # Usar numpy para toda la fila
            t_row = (np.arange(width) / width + angle_jitter) % 1.0
            seg = np.clip((t_row * (n - 1)).astype(int), 0, n - 2)
            local_t = t_row * (n - 1) - seg
            c1 = np.array([colors[s] for s in seg])
            c2 = np.array([colors[s + 1] for s in seg])
            row = (c1 * (1 - local_t[:, None]) + c2 * local_t[:, None]).astype(np.uint8)
            img_array[y] = row
            continue

        # Interpolación multi-color
        seg = min(int(t * (n - 1)), n - 2)
        local_t = t * (n - 1) - seg
        c1 = colors[seg]
        c2 = colors[seg + 1]
        r = int(c1[0] * (1 - local_t) + c2[0] * local_t)
        g = int(c1[1] * (1 - local_t) + c2[1] * local_t)
        b = int(c1[2] * (1 - local_t) + c2[2] * local_t)
        img_array[y, :] = [r, g, b]

    return img_array


def _render_radial_gradient(colors: list, width: int, height: int):
    """Gradiente radial: color[0] en el centro, colors[-1] en los bordes."""
    import numpy as np

    # Centro con jitter aleatorio
    cx = width // 2 + random.randint(-width // 10, width // 10)
    cy = height // 2 + random.randint(-height // 10, height // 10)

    Y, X = np.mgrid[0:height, 0:width]
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    max_dist = math.sqrt(cx ** 2 + cy ** 2) * 1.1
    t = np.clip(dist / max_dist, 0.0, 1.0)

    n = len(colors)
    img_array = np.zeros((height, width, 3), dtype=np.float32)

    for i in range(n - 1):
        t0 = i / (n - 1)
        t1 = (i + 1) / (n - 1)
        mask = (t >= t0) & (t < t1)
        local_t = (t - t0) / (t1 - t0)
        c1 = np.array(colors[i], dtype=np.float32)
        c2 = np.array(colors[i + 1], dtype=np.float32)
        for ch in range(3):
            img_array[:, :, ch] += mask * (c1[ch] * (1 - local_t) + c2[ch] * local_t)

    # último tramo
    mask = t >= (n - 2) / (n - 1)
    img_array[:, :, :] += mask[:, :, None] * np.array(colors[-1], dtype=np.float32)

    return np.clip(img_array, 0, 255).astype(np.uint8)


def _render_starfield(colors: list, width: int, height: int):
    """Gradiente oscuro con estrellas procedurales usando numpy."""
    import numpy as np

    # Base: gradiente oscuro
    base = _render_linear_gradient(colors, width, height, "vertical")
    img_array = base.astype(np.float32)

    # Estrellas: puntos aleatorios de distintos tamaños y brillos
    n_stars = random.randint(600, 900)
    xs = np.random.randint(0, width, n_stars)
    ys = np.random.randint(0, height, n_stars)
    brightness = np.random.randint(120, 255, n_stars)

    for i in range(n_stars):
        x, y = xs[i], ys[i]
        b = brightness[i]
        img_array[y, x] = [b, b, b]
        # Algunas estrellas más grandes (glow de 1px)
        if b > 200 and x > 0 and x < width - 1 and y > 0 and y < height - 1:
            glow = b * 0.4
            img_array[y - 1, x] = np.clip(img_array[y - 1, x] + glow, 0, 255)
            img_array[y + 1, x] = np.clip(img_array[y + 1, x] + glow, 0, 255)
            img_array[y, x - 1] = np.clip(img_array[y, x - 1] + glow, 0, 255)
            img_array[y, x + 1] = np.clip(img_array[y, x + 1] + glow, 0, 255)

    return np.clip(img_array, 0, 255).astype(np.uint8)


def _render_stone_texture(colors: list, width: int, height: int):
    """Textura de piedra con ruido multi-octava y colorización."""
    import numpy as np
    from PIL import Image, ImageFilter

    # Ruido base (varias octavas)
    noise = np.zeros((height, width), dtype=np.float32)
    for octave in [8, 4, 2, 1]:
        scale_h = max(1, height // (octave * 4))
        scale_w = max(1, width // (octave * 4))
        small = np.random.rand(scale_h, scale_w).astype(np.float32)
        # Escalar al tamaño completo con PIL
        pil_small = Image.fromarray((small * 255).astype(np.uint8))
        pil_full = pil_small.resize((width, height), Image.BILINEAR)
        layer = np.array(pil_full).astype(np.float32) / 255.0
        # Blur para suavizar
        sigma = octave * 6
        pil_blur = Image.fromarray((layer * 255).astype(np.uint8))
        pil_blur = pil_blur.filter(ImageFilter.GaussianBlur(radius=sigma))
        layer = np.array(pil_blur).astype(np.float32) / 255.0
        noise += layer / (2 ** octave)

    # Normalizar
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)

    # Colorizar: interpolar entre colores del preset según valor de ruido
    n = len(colors)
    img_array = np.zeros((height, width, 3), dtype=np.float32)
    for i in range(n - 1):
        t0 = i / (n - 1)
        t1 = (i + 1) / (n - 1)
        mask = (noise >= t0) & (noise < t1)
        local_t = (noise - t0) / (t1 - t0 + 1e-8)
        c1 = np.array(colors[i], dtype=np.float32)
        c2 = np.array(colors[i + 1], dtype=np.float32)
        for ch in range(3):
            img_array[:, :, ch] += mask * (c1[ch] * (1 - local_t) + c2[ch] * local_t)

    return np.clip(img_array, 0, 255).astype(np.uint8)


def _render_cloud_texture(colors: list, width: int, height: int):
    """Nubes suaves con blurs de gran radio anidados."""
    import numpy as np
    from PIL import Image, ImageFilter

    # Base oscura
    base_color = np.array(colors[-1], dtype=np.float32)
    img_array = np.ones((height, width, 3), dtype=np.float32) * base_color

    # Capas de nubes con distintos tamaños
    for sigma, alpha in [(120, 0.5), (60, 0.35), (30, 0.25)]:
        noise = np.random.rand(height, width).astype(np.float32)
        pil_noise = Image.fromarray((noise * 255).astype(np.uint8))
        pil_blur = pil_noise.filter(ImageFilter.GaussianBlur(radius=sigma))
        layer = np.array(pil_blur).astype(np.float32) / 255.0

        # Colorizar con el color más claro del preset
        light_color = np.array(colors[0], dtype=np.float32)
        for ch in range(3):
            img_array[:, :, ch] += alpha * layer * (light_color[ch] - base_color[ch])

    return np.clip(img_array, 0, 255).astype(np.uint8)


# ─── Overlays ──────────────────────────────────────────────────────────────────

def _overlay_rays(img, width: int, height: int):
    """Rayos radiales suaves desde el centro."""
    from PIL import Image, ImageFilter
    import numpy as np

    cx = width // 2 + random.randint(-50, 50)
    cy = height // 2 + random.randint(-80, 20)
    n_rays = random.randint(8, 14)

    overlay = np.zeros((height, width), dtype=np.float32)
    Y, X = np.mgrid[0:height, 0:width]
    angles = np.arctan2(Y - cy, X - cx)

    for i in range(n_rays):
        ray_angle = (2 * math.pi * i / n_rays) + random.uniform(-0.15, 0.15)
        diff = np.abs(((angles - ray_angle + math.pi) % (2 * math.pi)) - math.pi)
        width_factor = random.uniform(0.03, 0.08)
        ray = np.exp(-diff ** 2 / (2 * width_factor ** 2))
        # Atenuar con la distancia al centro
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        ray *= np.clip(dist / (max(width, height) * 0.8), 0, 1)
        overlay += ray

    overlay = overlay / (overlay.max() + 1e-8)
    # Aplicar como capa dorada semitransparente
    pil_overlay = Image.fromarray((overlay * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius=8)
    )
    overlay_smooth = np.array(pil_overlay).astype(np.float32) / 255.0

    img_array = np.array(img).astype(np.float32)
    gold = np.array([230, 180, 80], dtype=np.float32)
    for ch in range(3):
        img_array[:, :, ch] = np.clip(
            img_array[:, :, ch] + overlay_smooth * gold[ch] * 0.35, 0, 255
        )

    return Image.fromarray(img_array.astype(np.uint8))


def _overlay_rings(img, width: int, height: int):
    """Anillos concéntricos dorados semitransparentes."""
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np

    cx, cy = width // 2, height // 2
    ring_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ring_layer)

    n_rings = random.randint(5, 8)
    max_r = int(math.sqrt(cx ** 2 + cy ** 2) * 1.1)

    for i in range(n_rings):
        r = int(max_r * (i + 1) / (n_rings + 1))
        alpha = int(80 * (1 - i / n_rings))
        thickness = random.randint(2, 5)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(220, 170, 60, alpha),
            width=thickness,
        )

    ring_layer = ring_layer.filter(ImageFilter.GaussianBlur(radius=3))
    img_rgba = img.convert("RGBA")
    img_rgba.paste(ring_layer, (0, 0), ring_layer)
    return img_rgba.convert("RGB")


def _overlay_cross(img, width: int, height: int):
    """Cruz de luz suave en el centro."""
    from PIL import Image, ImageFilter
    import numpy as np

    overlay = np.zeros((height, width), dtype=np.float32)
    cx, cy = width // 2, height // 2

    # Barra vertical
    bar_w = width // 30
    x1, x2 = max(0, cx - bar_w), min(width, cx + bar_w)
    overlay[:, x1:x2] += 1.0

    # Barra horizontal
    bar_h = height // 30
    y1, y2 = max(0, cy - bar_h * 2), min(height, cy + bar_h * 2)
    overlay[y1:y2, :] += 0.8

    overlay = np.clip(overlay, 0, 1)
    pil_overlay = Image.fromarray((overlay * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius=25)
    )
    overlay_smooth = np.array(pil_overlay).astype(np.float32) / 255.0

    img_array = np.array(img).astype(np.float32)
    for ch in range(3):
        img_array[:, :, ch] = np.clip(
            img_array[:, :, ch] + overlay_smooth * 200 * 0.3, 0, 255
        )

    return Image.fromarray(img_array.astype(np.uint8))


def _apply_vignette(img, width: int, height: int):
    """Oscurece los bordes (viñeta)."""
    from PIL import Image, ImageDraw
    import numpy as np

    cx, cy = width // 2, height // 2
    max_r = math.sqrt(cx * cx + cy * cy)
    Y, X = np.mgrid[0:height, 0:width]
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    brightness = np.clip(1 - (dist / max_r) ** 1.8 * 0.65, 0.0, 1.0)

    img_array = np.array(img).astype(np.float32)
    for ch in range(3):
        img_array[:, :, ch] *= brightness

    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))


# ─── Selección de preset ───────────────────────────────────────────────────────

def _elegir_preset(prompt: str, preset_key: str = None) -> dict:
    """Elige preset por key explícita o por palabras clave del prompt."""
    if preset_key and preset_key in STYLE_PRESETS:
        return STYLE_PRESETS[preset_key]

    prompt_lower = (prompt or "").lower()
    for key, preset in STYLE_PRESETS.items():
        for kw in preset.get("keywords", []):
            if kw in prompt_lower:
                return preset

    # Aleatorio para más variedad
    return random.choice(list(STYLE_PRESETS.values()))


# ─── Gemini ────────────────────────────────────────────────────────────────────

def _generar_con_gemini(prompt: str, api_key: str, output_dir: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    response = model.generate_content(
        f"Generate a beautiful, cinematic background image for a biblical YouTube video: {prompt}",
        generation_config=genai.GenerationConfig(
            response_mime_type="image/jpeg",
        ),
    )

    for part in response.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(output_dir, f"imagen_gemini_{ts}.jpg")
            with open(path, "wb") as f:
                f.write(part.inline_data.data)
            return os.path.abspath(path)

    raise RuntimeError("Gemini no retornó una imagen")


# Mantener compatibilidad con código que importe PALETAS
PALETAS = {k: {"top": v["colors"][0], "mid": v["colors"][len(v["colors"]) // 2],
               "bottom": v["colors"][-1]}
           for k, v in STYLE_PRESETS.items()}
