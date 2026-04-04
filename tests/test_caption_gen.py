"""Tests for core/caption_gen.py — caption generation with hashtags."""
import os
import tempfile

from core.caption_gen import (
    generar_caption,
    guardar_caption,
    BASE_HASHTAGS,
    THEME_HASHTAGS,
)


class TestCaptionGen:
    """Tests for caption generation."""

    def test_caption_has_verse_text(self):
        caption = generar_caption(
            "Y la paz de Dios que sobrepasa todo entendimiento",
            "Filipenses 4:7", "paz",
        )
        assert "Y la paz de Dios" in caption

    def test_caption_has_reference(self):
        caption = generar_caption("Texto", "Juan 3:16", "fe")
        assert "Juan 3:16" in caption

    def test_caption_has_version(self):
        caption = generar_caption("Texto", "Ref", "paz")
        assert "RVR1960" in caption

    def test_caption_has_base_hashtags(self):
        caption = generar_caption("Texto", "Ref", "paz")
        for tag in BASE_HASHTAGS[:3]:
            assert tag in caption

    def test_caption_has_theme_hashtags(self):
        caption = generar_caption("Texto", "Ref", "paz")
        paz_tags = THEME_HASHTAGS["paz"]
        found = any(tag in caption for tag in paz_tags)
        assert found, "Caption should include at least one theme hashtag"

    def test_caption_has_emoji(self):
        caption = generar_caption("Texto", "Ref", "amor")
        assert "❤️" in caption

    def test_guardar_caption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "caption.txt")
            result = guardar_caption("Mi caption de prueba", path)
            assert os.path.exists(result)
            with open(result, "r", encoding="utf-8") as f:
                assert "Mi caption de prueba" in f.read()

    def test_all_themes_have_hashtags(self):
        for theme in THEME_HASHTAGS:
            caption = generar_caption("Texto", "Ref", theme)
            assert len(caption) > 50, f"Caption for {theme} is too short"
