"""
core/caption_gen.py — Social media caption generation with hashtags.

Generates captions for Instagram, Facebook, and TikTok posts
using templates with verse text, reflections, and engagement questions.
"""
from __future__ import annotations

import os
import random


# ─── Hashtags ─────────────────────────────────────────────────────────────────

BASE_HASHTAGS = [
    "#VersiculoDeDios", "#PalabraDeVida", "#FeCristiana",
    "#Biblia", "#RVR1960", "#DiosTeAma", "#VersiculoBiblico",
    "#DiosConmigo", "#FeYEsperanza", "#palabradedios111",
]

THEME_HASHTAGS = {
    "paz": ["#PazDeDios", "#Salmos", "#TransquilidadEnDios"],
    "fe": ["#FeEnDios", "#ConfiaEnElSeñor", "#FeCristiana"],
    "esperanza": ["#EsperanzaEnDios", "#NuncaTeRindas", "#Esperanza"],
    "sanacion": ["#SanacionDivina", "#DiosSana", "#MilagrosDeDios"],
    "gratitud": ["#GraciasSeñor", "#GratitudADios", "#BendicionesDeDios"],
    "salmos": ["#Salmos", "#LibroDeLosSalmos", "#DavidYDios"],
    "amor": ["#AmorDeDios", "#DiosEsAmor", "#AmorIncondicional"],
    "fuerza": ["#FuerzaEnDios", "#TodoLoPuedo", "#FuerteEnElSeñor"],
    "provision": ["#ProvisionDeDios", "#NadaMeFaltara", "#DiosProvee"],
    "victoria": ["#VictoriaEnCristo", "#MasQueVencedor", "#TriunfoEnDios"],
}


# ─── Reflection and engagement templates ──────────────────────────────────────

THEME_EMOJIS = {
    "paz": "🕊️",
    "fe": "✝️",
    "esperanza": "🌅",
    "sanacion": "🙌",
    "gratitud": "🙏",
    "salmos": "📖",
    "amor": "❤️",
    "fuerza": "💪",
    "provision": "🌾",
    "victoria": "👑",
}

REFLECTIONS = {
    "paz": [
        "La paz de Dios no depende de las circunstancias, sino de Su presencia en tu vida.",
        "Cuando el mundo te agobia, recuerda que Dios ya venció al mundo.",
        "Su paz es un regalo que no se compra — se recibe con fe.",
    ],
    "fe": [
        "La fe no elimina las tormentas, pero te da la fuerza para caminar sobre ellas.",
        "Confiar en Dios significa soltar el control y dejar que Él dirija tus pasos.",
        "Tu fe no tiene que ser perfecta, solo tiene que ser genuina.",
    ],
    "esperanza": [
        "Mientras haya Dios, siempre habrá esperanza.",
        "No importa cuán oscura sea la noche, el amanecer siempre llega.",
        "La esperanza en Cristo nunca defrauda.",
    ],
    "sanacion": [
        "Dios sana no solo el cuerpo, sino también el alma herida.",
        "Entrega tus heridas a Dios — Él es el médico perfecto.",
        "La sanación comienza cuando ponemos nuestra confianza en Sus manos.",
    ],
    "gratitud": [
        "Un corazón agradecido abre las puertas de la bendición.",
        "Dar gracias en todo momento es un acto de fe poderoso.",
        "La gratitud transforma lo que tenemos en suficiente.",
    ],
    "salmos": [
        "Los Salmos nos enseñan a hablar con Dios desde el corazón.",
        "En cada Salmo hay una promesa que Dios tiene para ti hoy.",
        "David nos mostró que podemos ser honestos con Dios en todo momento.",
    ],
    "amor": [
        "El amor de Dios es incondicional — no tienes que ganártelo.",
        "Fuimos creados para amar porque Dios es amor.",
        "Nada puede separarte del amor de Dios.",
    ],
    "fuerza": [
        "Tu fuerza no viene de ti — viene del Dios todopoderoso.",
        "Cuando te sientes débil, es cuando Su poder se perfecciona en ti.",
        "Con Dios a tu lado, no hay gigante que te pueda derribar.",
    ],
    "provision": [
        "Dios no solo conoce tus necesidades — ya las tiene cubiertas.",
        "El que alimenta a las aves del cielo, mucho más cuidará de ti.",
        "Confía en Su provisión, porque Él nunca llega tarde.",
    ],
    "victoria": [
        "En Cristo ya eres más que vencedor.",
        "La batalla es del Señor — tu victoria ya está asegurada.",
        "No peleas para ganar, peleas desde la victoria que Cristo ya te dio.",
    ],
}

ENGAGEMENT_QUESTIONS = [
    "¿Qué significa este versículo para ti hoy?",
    "¿A quién le dedicarías este versículo?",
    "Comparte este versículo con alguien que lo necesite 💛",
    "¿Cómo aplicas esta palabra en tu vida diaria?",
    "Escribe AMÉN si crees en Sus promesas 🙏",
    "¿Cuál es tu versículo favorito sobre este tema?",
    "Etiqueta a alguien que necesita leer esto hoy 👇",
]


# ─── Caption generation ──────────────────────────────────────────────────────

def generar_caption(
    texto: str,
    referencia: str,
    theme: str,
    version: str = "RVR1960",
) -> str:
    """
    Generate a social media caption for a biblical verse post.

    Returns the full caption text ready to paste into Instagram/Facebook/TikTok.
    """
    emoji = THEME_EMOJIS.get(theme, "✨")

    # Pick a reflection for this theme
    reflections = REFLECTIONS.get(theme, REFLECTIONS["fe"])
    reflection = random.choice(reflections)

    # Pick an engagement question
    question = random.choice(ENGAGEMENT_QUESTIONS)

    # Build hashtags
    hashtags = BASE_HASHTAGS + THEME_HASHTAGS.get(theme, [])
    hashtag_str = " ".join(hashtags)

    caption = (
        f'{emoji} "{texto}"\n'
        f"— {referencia} ({version})\n"
        f"\n"
        f"{reflection}\n"
        f"\n"
        f"{question}\n"
        f".\n"
        f".\n"
        f"{hashtag_str}"
    )

    return caption


def guardar_caption(caption: str, output_path: str) -> str:
    """Save caption to a .txt file. Returns absolute path."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(caption)
    return os.path.abspath(output_path)
