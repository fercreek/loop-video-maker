"""Tests for core/post_gen.py — static JPG post generation."""
import os
import tempfile
import pytest
from PIL import Image

from core.post_gen import generar_post, _center_crop_resize
from core.image_gen import generar_imagen


class TestPostGen:
    """Tests for static post generation."""

    @pytest.fixture
    def tmp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield d

    @pytest.fixture
    def bg_image(self, tmp_dir):
        """Create a simple test background image."""
        img = Image.new("RGB", (1920, 1080), (50, 30, 20))
        path = os.path.join(tmp_dir, "bg.jpg")
        img.save(path, quality=95)
        return path

    def test_post_1080x1080(self, tmp_dir, bg_image):
        out = os.path.join(tmp_dir, "post.jpg")
        result = generar_post(
            texto="Y la paz de Dios, que sobrepasa todo entendimiento...",
            referencia="Filipenses 4:7",
            imagen_fondo_path=bg_image,
            output_path=out,
        )
        assert os.path.exists(result)
        img = Image.open(result)
        assert img.size == (1080, 1080)

    def test_post_is_jpeg(self, tmp_dir, bg_image):
        out = os.path.join(tmp_dir, "post.jpg")
        generar_post("Texto", "Ref", bg_image, out)
        img = Image.open(out)
        assert img.format == "JPEG"

    def test_post_not_blank(self, tmp_dir, bg_image):
        out = os.path.join(tmp_dir, "post.jpg")
        generar_post("Texto visible", "Juan 3:16", bg_image, out)
        img = Image.open(out)
        # The image should have varied pixel values (not solid color)
        import numpy as np
        arr = np.array(img)
        assert arr.std() > 5, "Post should not be a solid color"

    def test_post_with_watermark(self, tmp_dir, bg_image):
        out = os.path.join(tmp_dir, "post_wm.jpg")
        result = generar_post(
            texto="Texto", referencia="Ref", imagen_fondo_path=bg_image,
            output_path=out, watermark_text="Mi Canal",
        )
        assert os.path.exists(result)


class TestCenterCropResize:
    """Tests for the center crop resize helper."""

    def test_landscape_to_square(self):
        img = Image.new("RGB", (1920, 1080), (100, 100, 100))
        result = _center_crop_resize(img, 1080, 1080)
        assert result.size == (1080, 1080)

    def test_portrait_to_square(self):
        img = Image.new("RGB", (1080, 1920), (100, 100, 100))
        result = _center_crop_resize(img, 1080, 1080)
        assert result.size == (1080, 1080)

    def test_square_to_square(self):
        img = Image.new("RGB", (1080, 1080), (100, 100, 100))
        result = _center_crop_resize(img, 1080, 1080)
        assert result.size == (1080, 1080)

    def test_landscape_to_portrait(self):
        img = Image.new("RGB", (1920, 1080), (100, 100, 100))
        result = _center_crop_resize(img, 1080, 1920)
        assert result.size == (1080, 1920)
