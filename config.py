"""
config.py — Constantes centralizadas del pipeline.

Fuente única de verdad para:
- Render engine (FPS, workers, bitrate, presets)
- Temas (moods, labels)
- Visual templates (alternancia A/B)
- Eval targets (LUFS, duración, silencios)

Todos los scripts (render_60min, generate_video, iterate, eval_render)
importan desde aquí. No duplicar constantes en otros archivos.
"""
from __future__ import annotations

# ─── Render engine ───────────────────────────────────────────────────────────
SECONDS_PER_VERSE    = 20       # 20s × 180 verses = 60 min
VERSES_PER_BG        = 3        # fondos permanecen 3 versos = 60s — tiempo para apreciar Ken Burns
TARGET_MINUTES_DEFAULT = 60
RENDER_FPS = 12                 # 12fps — suficiente para Ken Burns lento
RENDER_FPS_HIRES = 24           # 24fps — modo viral/experimental (2× render time)
PARALLEL_JOBS = 6               # ffmpeg subprocesses paralelos (tune to CPU cores)
VIDEO_BITRATE = "3500k"         # target YouTube 1080p
X264_PRESET = "ultrafast"       # velocidad > compresión — YouTube re-encodea
CROSSFADE_SECONDS = 8.0         # crossfade entre tracks musicales
WATERMARK = "@VersiculoDeDios"

# ─── Output paths ────────────────────────────────────────────────────────────
OUTPUT_BASE_60MIN = "output/youtube_60min"
OUTPUT_BASE_DEFAULT = "output/youtube"
FONDOS_GLOB = "output/fondos/*.jpg"

# ─── Visual templates (alternancia A/B verso-por-verso) ─────────────────────
# A = centrado_bajo: gold ornaments, label, diamond separator (devotional)
# B = lateral_izq:   cinematic left-aligned, vertical gold bar, no label
VISUAL_TEMPLATES = [
    {"layout_preset": "centrado_bajo", "text_style": "fea"},
    {"layout_preset": "lateral_izq",   "text_style": "fea"},
]

# ─── Theme registry ──────────────────────────────────────────────────────────
# 8 temas activos. Cada tema tiene 3 moods combinados para evitar monotonía en 60min.
THEME_MOODS: dict[str, list[str]] = {
    # v3.9: all duplicates removed — Sanacion/Paz profunda used the same file,
    # Esperanza/Devoción used the same file. Now every theme has 3 unique tracks.
    "paz":       ["Paz profunda", "Reposo", "Contemplación"],         # night prayer — Reposo=365s loop
    "fe":        ["Adoración", "Devoción", "Paz profunda"],          # unchanged ✅
    "esperanza": ["Amanecer", "Adoración", "Reposo"],                # morning hope — long loop end
    "amor":      ["Adoración", "Paz profunda", "Paz tarde"],         # evening warmth
    "gratitud":  ["Reposo", "Adoración", "Paz profunda"],            # Reposo = 365s (was 91s Meditacion)
    "victoria":  ["Devoción", "Adoración", "Amanecer"],              # triumph → hope
    "fuerza":    ["Solemnidad", "Devoción", "Paz profunda"],         # solemn power
    "salmos":    ["Paz profunda", "Adoración", "Contemplación"],     # contemplative psalms
    # Batch experimental v3.8 — 2 temas nuevos
    "sanacion":  ["Contemplación", "Paz profunda", "Reposo"],        # deep healing
    "provision": ["Adoración", "Amanecer", "Paz profunda"],          # provision = hope+praise
}

THEME_LABELS: dict[str, str] = {
    "paz":       "Paz de Dios",
    "fe":        "Fe que mueve montañas",
    "esperanza": "Esperanza en Dios",
    "amor":      "El Amor de Dios",
    "gratitud":  "Gratitud a Dios",
    "victoria":  "Victoria en Cristo",
    "fuerza":    "Fuerza en Dios",
    "salmos":    "Salmos — Adoración",
    "sanacion":  "Sanidad y Restauración",
    "provision": "Provisión de Dios",
}

ALL_THEMES = list(THEME_MOODS.keys())

DEFAULT_MOODS = ["Paz profunda", "Meditacion", "Adoración"]


def get_moods(theme: str) -> list[str]:
    """Return mood list for theme, or DEFAULT_MOODS if unknown."""
    return THEME_MOODS.get(theme.lower(), DEFAULT_MOODS)


def get_label(theme: str) -> str:
    """Return human label for theme, or capitalized theme if unknown."""
    return THEME_LABELS.get(theme.lower(), theme.capitalize())


# ─── Eval targets (eval_render.py) ──────────────────────────────────────────
EVAL_TARGETS = {
    "duration_tolerance_sec": 5.0,          # ±5s vs nominal
    "min_bitrate_kbps": 3000,
    "expected_fps": RENDER_FPS,
    "mb_per_min_min": 18,
    "mb_per_min_max": 32,
    "lufs_target": -16.0,                    # YouTube normaliza >-14
    "lufs_tolerance": 3.0,
    "max_silence_sec": 2.0,
    "max_dip_db": 6.0,                       # crossfade boundary dip
    "skip_edge_seconds": 10.0,               # ignora fade-in/out para dips
    "thumbnail_max_mb": 2.0,                 # límite YouTube
    "thumbnail_width": 1280,
    "thumbnail_height": 720,
    "effect_dominance_threshold": 0.4,       # >40% mismo efecto = warning
}


# ─── Iter loop ──────────────────────────────────────────────────────────────
BATCH_SIZE = 5                              # videos por iteración

# ─── Quality gate (core/quality_gate.py) ────────────────────────────────────
QUALITY_GATE_THRESHOLD = 80         # score mínimo para "pass" (0-100)
QUALITY_GATE_AUTO_FIX_LUFS = True   # auto-aplicar loudnorm si LUFS fuera de rango

# ─── v3.9 production effects ─────────────────────────────────────────────────
GODRAY_ALPHA      = 0.15   # opacidad god-ray (0.0–1.0); 0.15 = sutil pero visible
GODRAY_BLUR       = 60     # radio Gaussian blur del god-ray (px)
AUDIO_FADE_IN_SEC = 5      # swell de entrada en audio (afade antes de loudnorm)
