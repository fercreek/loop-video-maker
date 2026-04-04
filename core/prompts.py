"""
core/prompts.py — Theme-specific cinematic prompts for Gemini image generation.

Each theme has multiple prompts to provide visual variety across batch runs.
"""
from __future__ import annotations

import random


THEME_PROMPTS = {
    "paz": [
        "Peaceful dawn landscape with golden light breaking through dark blue clouds, mountain silhouettes, warm amber horizon, cinematic, photorealistic, 4K, no text, no people",
        "Calm misty lake at sunrise with mountains in the distance, soft golden reflections on water, serene atmosphere, cinematic photography, 4K, no text",
        "Gentle morning fog over a quiet meadow, warm golden sunlight filtering through, peaceful biblical landscape, cinematic, 4K, no text, no people",
    ],
    "fe": [
        "Heavenly light rays breaking through storm clouds over mountains, dramatic golden sunset, biblical atmosphere, cinematic photography, 4K, no text",
        "Majestic mountain peak illuminated by powerful golden sunbeam piercing dark clouds, dramatic biblical scene, cinematic, 4K, no text, no people",
        "Ancient stone path leading toward brilliant golden light on the horizon, dramatic sky, faith journey, cinematic photography, 4K, no text",
    ],
    "esperanza": [
        "Sunrise over calm lake with mountains, warm golden light, misty atmosphere, serene biblical landscape, cinematic, photorealistic, 4K",
        "First light of dawn breaking over a vast green valley, golden rays illuminating the landscape, hope and renewal, cinematic, 4K, no text",
        "Rainbow arching over a peaceful landscape after rain, warm golden light, biblical atmosphere of hope, cinematic photography, 4K, no text",
    ],
    "sanacion": [
        "Soft morning light through forest trees, gentle golden rays, peaceful nature, healing atmosphere, cinematic photography, 4K, no text",
        "Crystal clear stream flowing through a sunlit forest, warm golden light filtering through leaves, healing nature, cinematic, 4K, no text",
        "Peaceful garden at dawn with dewdrops on flowers, soft golden light, gentle healing atmosphere, cinematic photography, 4K, no text",
    ],
    "gratitud": [
        "Golden harvest fields at sunset, warm amber light, thankful peaceful atmosphere, biblical landscape, cinematic, 4K",
        "Abundant vineyard at golden hour, warm sunset light over ripe grapes, thanksgiving atmosphere, biblical, cinematic, 4K, no text",
        "Bountiful meadow of wildflowers under golden sunset sky, gratitude and abundance, cinematic photography, 4K, no text",
    ],
    "salmos": [
        "Ancient rocky landscape with dramatic golden sky, biblical middle east, warm dramatic lighting, cinematic, 4K, no text, no people",
        "Desert mountains at golden hour with dramatic cloud formations, ancient biblical landscape, Psalm atmosphere, cinematic, 4K, no text",
        "Vast starry night sky over ancient desert hills, warm amber glow on horizon, biblical Psalms atmosphere, cinematic, 4K, no text",
    ],
    "amor": [
        "Warm sunset over ocean, golden orange sky reflection on water, peaceful loving atmosphere, cinematic, 4K",
        "Soft pink and golden sunset over a tranquil sea, warm light embracing the horizon, love and peace, cinematic photography, 4K, no text",
        "Beautiful garden of roses at golden hour, warm soft light, loving peaceful atmosphere, cinematic, 4K, no text",
    ],
    "fuerza": [
        "Dramatic mountain peak with powerful golden sunrise breaking through clouds, strength and majesty, cinematic, 4K",
        "Towering ancient oak tree standing strong against dramatic golden sky, powerful and enduring, biblical atmosphere, cinematic, 4K, no text",
        "Mighty waterfall cascading through rocky mountains at golden hour, strength and power of nature, cinematic photography, 4K, no text",
    ],
    "provision": [
        "Abundant green valley with golden light, flowing river, blessed landscape, biblical atmosphere, cinematic, 4K",
        "Lush green pastures beside still waters at golden hour, Psalm 23 landscape, provision and peace, cinematic photography, 4K, no text",
        "Overflowing wheat field at golden sunset, abundance and provision, warm biblical landscape, cinematic, 4K, no text",
    ],
    "victoria": [
        "Triumphant sunrise over vast landscape, golden rays breaking through dark clouds, victorious light, cinematic, 4K",
        "Dramatic sunrise from mountain summit, golden light conquering darkness, victory and triumph, cinematic photography, 4K, no text",
        "Brilliant golden light bursting through storm clouds over a vast plain, victory over darkness, cinematic, 4K, no text",
    ],
}


def get_prompt_for_theme(theme: str, index: int | None = None) -> str:
    """
    Return a cinematic prompt for the given theme.

    Args:
        theme: One of the 10 biblical themes.
        index: Specific prompt index. If None, picks randomly.

    Returns:
        A prompt string. Falls back to a generic prompt if theme is unknown.
    """
    prompts = THEME_PROMPTS.get(theme)
    if not prompts:
        return (
            "Beautiful cinematic biblical landscape with golden light, "
            "warm atmosphere, photorealistic, 4K, no text, no people"
        )
    if index is not None:
        return prompts[index % len(prompts)]
    return random.choice(prompts)
