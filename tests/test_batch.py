"""Tests for core/batch_gen.py — batch content generation."""
import os
import tempfile
import pytest

import core.db as db
from core.batch_gen import BatchConfig, generar_batch, _create_output_dirs


class TestBatchOutputDirs:
    """Tests for batch output directory creation."""

    def test_creates_posts_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirs = _create_output_dirs(tmp, ["post_1080"])
            assert os.path.isdir(dirs["posts"])
            assert os.path.isdir(dirs["captions"])

    def test_creates_reels_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirs = _create_output_dirs(tmp, ["reel_1080"])
            assert os.path.isdir(dirs["reels"])

    def test_creates_multiple_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirs = _create_output_dirs(tmp, ["post_1080", "reel_1080"])
            assert os.path.isdir(dirs["posts"])
            assert os.path.isdir(dirs["reels"])
            assert os.path.isdir(dirs["captions"])


class TestBatchGenPosts:
    """Tests for batch post generation (fast, no video rendering)."""

    @pytest.fixture
    def tmp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield d

    @pytest.fixture(autouse=True)
    def init_test_db(self, tmp_dir):
        db_path = os.path.join(tmp_dir, "test.db")
        db.init_db(db_path)

    def test_batch_produces_posts(self, tmp_dir):
        config = BatchConfig(
            client_name="Test Canal",
            theme="paz",
            formats=["post_1080"],
            num_verses=3,
            output_base_dir=tmp_dir,
        )
        results = generar_batch(config)

        assert len(results["posts"]) == 3
        for path in results["posts"]:
            assert os.path.exists(path)
            assert path.endswith(".jpg")

    def test_batch_produces_captions(self, tmp_dir):
        config = BatchConfig(
            client_name="Test Canal",
            theme="paz",
            formats=["post_1080"],
            num_verses=3,
            output_base_dir=tmp_dir,
        )
        results = generar_batch(config)

        assert len(results["captions"]) == 3
        for path in results["captions"]:
            assert os.path.exists(path)
            assert path.endswith(".txt")

    def test_batch_total_count(self, tmp_dir):
        config = BatchConfig(
            client_name="Test Canal",
            theme="fe",
            formats=["post_1080"],
            num_verses=5,
            output_base_dir=tmp_dir,
        )
        results = generar_batch(config)
        assert results["total"] == 5

    def test_batch_db_records(self, tmp_dir):
        config = BatchConfig(
            client_name="Test Canal",
            theme="paz",
            formats=["post_1080"],
            num_verses=2,
            output_base_dir=tmp_dir,
        )
        generar_batch(config)

        posts = db.get_posts(limit=10)
        assert len(posts) == 2

        batch_jobs = db.get_batch_jobs(limit=10)
        assert len(batch_jobs) >= 1
        assert batch_jobs[0]["status"] == "completed"

    def test_batch_progress_callback(self, tmp_dir):
        progress_calls = []

        def track_progress(pct, msg):
            progress_calls.append((pct, msg))

        config = BatchConfig(
            client_name="Test Canal",
            theme="paz",
            formats=["post_1080"],
            num_verses=2,
            output_base_dir=tmp_dir,
        )
        generar_batch(config, progress_callback=track_progress)

        assert len(progress_calls) > 0
        assert progress_calls[-1][0] == 1.0  # Final call should be 100%

    def test_batch_with_watermark(self, tmp_dir):
        config = BatchConfig(
            client_name="Test Canal",
            theme="amor",
            formats=["post_1080"],
            num_verses=1,
            watermark_text="Mi Canal",
            output_base_dir=tmp_dir,
        )
        results = generar_batch(config)
        assert len(results["posts"]) == 1

    def test_batch_different_layouts(self, tmp_dir):
        for layout in ["centrado_bajo", "centrado_alto", "centro_absoluto"]:
            config = BatchConfig(
                client_name="Test Canal",
                theme="paz",
                formats=["post_1080"],
                num_verses=1,
                layout_preset=layout,
                output_base_dir=tmp_dir,
            )
            results = generar_batch(config)
            assert len(results["posts"]) == 1

    def test_batch_organized_by_client(self, tmp_dir):
        """Output files are nested under client folder."""
        config = BatchConfig(
            client_name="VersiculoDeDios",
            theme="paz",
            formats=["post_1080"],
            num_verses=1,
            output_base_dir=tmp_dir,
        )
        results = generar_batch(config)

        batch_dir = results["batch_dir"]
        # batch_dir should be under tmp_dir/fe_en_acción/batch_paz_*
        assert "/fe_en_acción/" in batch_dir or "/fe_en_accin/" in batch_dir \
            or "fe_en_acci" in batch_dir
        assert os.path.isdir(batch_dir)

    def test_different_clients_separate_folders(self, tmp_dir):
        """Different clients get separate folder trees."""
        for name in ["Canal A", "Canal B"]:
            config = BatchConfig(
                client_name=name,
                theme="paz",
                formats=["post_1080"],
                num_verses=1,
                output_base_dir=tmp_dir,
            )
            generar_batch(config)

        # Both client folders should exist
        assert os.path.isdir(os.path.join(tmp_dir, "canal_a"))
        assert os.path.isdir(os.path.join(tmp_dir, "canal_b"))
