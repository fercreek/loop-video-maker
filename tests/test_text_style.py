"""Tests for core/text_style.py — Fe en Acción text overlay renderer."""
import numpy as np
import pytest

from core.text_style import render_fea_frame, render_simple_frame
from core.formats import get_font_size, get_layout, LAYOUT_PRESETS, FORMAT_DEFS


class TestFeaFrame:
    """Tests for the Fe en Acción style renderer."""

    def test_correct_dimensions_1080x1080(self):
        frame = render_fea_frame("Texto de prueba", "Juan 3:16", 1080, 1080)
        assert frame.shape == (1080, 1080, 4)

    def test_correct_dimensions_1080x1920(self):
        frame = render_fea_frame("Texto de prueba", "Juan 3:16", 1080, 1920,
                                  format_key="reel_1080")
        assert frame.shape == (1920, 1080, 4)

    def test_correct_dimensions_1920x1080(self):
        frame = render_fea_frame("Texto de prueba", "Juan 3:16", 1920, 1080,
                                  format_key="youtube_1080")
        assert frame.shape == (1080, 1920, 4)

    def test_has_alpha_channel(self):
        frame = render_fea_frame("Texto", "Ref", 1080, 1080)
        assert frame.shape[2] == 4

    def test_not_fully_transparent(self):
        frame = render_fea_frame("Texto visible", "Salmo 23:1", 1080, 1080)
        assert frame[:, :, 3].max() > 0, "Frame should have some non-transparent pixels"

    def test_not_fully_opaque(self):
        frame = render_fea_frame("Texto", "Ref", 1080, 1080)
        assert frame[:, :, 3].min() == 0, "Frame should have transparent areas"

    def test_with_watermark(self):
        frame = render_fea_frame("Texto", "Ref", 1080, 1080,
                                  config_overrides={"watermark_text": "Mi Canal"})
        assert frame.shape == (1080, 1080, 4)

    def test_all_layouts(self):
        for preset_key in LAYOUT_PRESETS:
            frame = render_fea_frame("Texto", "Ref", 1080, 1080,
                                      layout_preset=preset_key)
            assert frame.shape == (1080, 1080, 4), f"Failed for layout {preset_key}"

    def test_empty_reference(self):
        frame = render_fea_frame("Texto sin referencia", "", 1080, 1080)
        assert frame.shape == (1080, 1080, 4)


class TestSimpleFrame:
    """Tests for the backward-compatible simple renderer."""

    def test_correct_dimensions(self):
        config = {"tamano": 52, "posicion": "bottom"}
        frame = render_simple_frame("Texto", "Juan 3:16", 1920, 1080, config)
        assert frame.shape == (1080, 1920, 4)

    def test_positions(self):
        for pos in ["top", "center", "bottom"]:
            config = {"tamano": 52, "posicion": pos}
            frame = render_simple_frame("Texto", "Ref", 1920, 1080, config)
            assert frame.shape == (1080, 1920, 4)

    def test_not_fully_transparent(self):
        config = {"tamano": 52}
        frame = render_simple_frame("Texto visible", "Ref", 1920, 1080, config)
        assert frame[:, :, 3].max() > 0


class TestFontScaling:
    """Tests for format-aware font scaling."""

    def test_post_scale_is_1(self):
        assert get_font_size(58, "post_1080") == 58

    def test_reel_scale_is_085(self):
        assert get_font_size(58, "reel_1080") == int(58 * 0.85)

    def test_youtube_scale_is_1(self):
        assert get_font_size(58, "youtube_1080") == 58

    def test_unknown_format_defaults_to_youtube(self):
        assert get_font_size(58, "unknown_format") == 58


class TestLayoutPresets:
    """Tests for layout preset validity."""

    def test_all_y_values_in_range(self):
        for key, layout in LAYOUT_PRESETS.items():
            assert 0 < layout["label_y"] < 1, f"{key}.label_y out of range"
            assert 0 < layout["verse_y"] < 1, f"{key}.verse_y out of range"
            assert 0 < layout["brand_y"] <= 1, f"{key}.brand_y out of range"

    def test_label_above_verse(self):
        for key, layout in LAYOUT_PRESETS.items():
            assert layout["label_y"] < layout["verse_y"], \
                f"{key}: label should be above verse"

    def test_get_layout_default(self):
        layout = get_layout("nonexistent")
        assert layout == LAYOUT_PRESETS["centrado_bajo"]
