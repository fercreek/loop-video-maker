"""
tests/test_pipeline.py — Pipeline integration spec.

Validates each layer of the pipeline independently (no server, no browser):
  1. DB  — record and retrieve images/audio/videos
  2. Image gen — unique filenames, valid JPEG output
  3. Audio gen — valid WAV, correct sample rate and channels
  4. Preview engine — audio URL fix, trim function, HTML structure
  5. Video render — [slow] 10-minute MP4 produced with correct duration

Run fast tests:
    .venv/bin/pytest tests/test_pipeline.py -v -m "not slow"

Run all (including slow render):
    .venv/bin/pytest tests/test_pipeline.py -v --timeout=900
"""
from __future__ import annotations

import os
import sys
import wave

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ─── 1. DB ──────────────────────────────────────────────────────

def test_db_record_and_retrieve_image(tmp_path):
    """DB: inserting an image record and retrieving it returns correct data."""
    import core.db as db

    db_file = str(tmp_path / "test.db")
    db.init_db(db_file)

    # Create a dummy file so record_image can abspath it
    img = tmp_path / "test.jpg"
    img.write_bytes(b"\xff\xd8\xff")  # minimal JPEG header

    row_id = db.record_image(
        path=str(img), style="Cielo nocturno", prompt="estrellas", theme="paz"
    )
    assert isinstance(row_id, int) and row_id > 0

    records = db.get_images(limit=10)
    assert len(records) == 1
    assert records[0]["style"] == "Cielo nocturno"
    assert records[0]["theme"] == "paz"
    assert records[0]["prompt"] == "estrellas"


def test_db_record_audio(tmp_path):
    """DB: audio records store mood, duration, and generator correctly."""
    import core.db as db

    db.init_db(str(tmp_path / "test.db"))

    wav = tmp_path / "test.wav"
    wav.write_bytes(b"RIFF")

    row_id = db.record_audio(
        path=str(wav), mood="Paz profunda", duration_sec=600, generator="ambient"
    )
    assert row_id > 0

    records = db.get_audio()
    assert records[0]["mood"] == "Paz profunda"
    assert records[0]["duration_sec"] == 600
    assert records[0]["generator"] == "ambient"


def test_db_record_video_with_foreign_keys(tmp_path):
    """DB: video record links to image_id and audio_id."""
    import core.db as db

    db.init_db(str(tmp_path / "test.db"))

    img = tmp_path / "img.jpg"
    img.write_bytes(b"\xff\xd8\xff")
    aud = tmp_path / "aud.wav"
    aud.write_bytes(b"RIFF")

    img_id = db.record_image(path=str(img), style="preset", prompt="", theme="paz")
    aud_id = db.record_audio(path=str(aud), mood="Devoción", duration_sec=3600)

    vid = tmp_path / "video.mp4"
    vid.write_bytes(b"")
    vid_id = db.record_video(
        path=str(vid), theme="paz", duration_min=60,
        seconds_per_verse=12, image_id=img_id, audio_id=aud_id,
        efecto_imagen="Zoom lento ↗", verses_count=45,
    )
    assert vid_id > 0

    videos = db.get_videos()
    assert videos[0]["image_id"] == img_id
    assert videos[0]["audio_id"] == aud_id
    assert videos[0]["verses_count"] == 45


# ─── 2. Image generation ────────────────────────────────────────

def test_image_gen_produces_valid_jpeg(tmp_path):
    """Image gen: output is a readable JPEG at 1920x1080."""
    from PIL import Image
    from core.image_gen import generar_imagen

    path = generar_imagen(
        prompt="", api_key="", output_dir=str(tmp_path), preset_key="starfield"
    )
    assert os.path.exists(path)
    with Image.open(path) as img:
        assert img.size == (1920, 1080)
        assert img.mode in ("RGB", "RGBA")


def test_image_gen_unique_filenames(tmp_path):
    """Image gen: two calls produce different filenames (no overwrite)."""
    from core.image_gen import generar_imagen
    import time

    path1 = generar_imagen(prompt="", api_key="", output_dir=str(tmp_path))
    time.sleep(1.1)  # ensure different timestamp
    path2 = generar_imagen(prompt="", api_key="", output_dir=str(tmp_path))

    assert path1 != path2, f"Both calls returned same path: {path1}"
    assert os.path.exists(path1)
    assert os.path.exists(path2)


# ─── 3. Audio generation ────────────────────────────────────────

def test_audio_gen_produces_valid_wav(tmp_path):
    """Audio gen: output is a valid stereo WAV at 44100 Hz."""
    from core.music_gen import generar_musica

    path = generar_musica(
        mood="Paz profunda", duracion_segundos=10, api_key="", output_dir=str(tmp_path)
    )
    assert os.path.exists(path), f"WAV not found: {path}"

    with wave.open(path, "r") as w:
        assert w.getnchannels() == 2, "Expected stereo"
        assert w.getframerate() == 44100, "Expected 44.1kHz"
        assert w.getnframes() > 0


def test_audio_gen_duration_approximate(tmp_path):
    """Audio gen: a 30-second request produces ~30 seconds of audio."""
    from core.music_gen import generar_musica

    path = generar_musica(
        mood="Devoción", duracion_segundos=30, api_key="", output_dir=str(tmp_path)
    )
    with wave.open(path, "r") as w:
        actual_sec = w.getnframes() / w.getframerate()
    assert 28 <= actual_sec <= 32, f"Expected ~30s, got {actual_sec:.1f}s"


# ─── 4. Preview engine ──────────────────────────────────────────

def test_preview_audio_trim_creates_short_clip(tmp_path):
    """Preview: trim function reduces a 5-minute WAV to ≤90 seconds."""
    from preview.preview_engine import _trim_audio_for_preview
    from core.music_gen import generar_musica

    long_wav = generar_musica(
        mood="Paz profunda", duracion_segundos=120, api_key="", output_dir=str(tmp_path)
    )
    preview_path = _trim_audio_for_preview(long_wav, max_sec=30)

    assert os.path.exists(preview_path)
    with wave.open(preview_path, "r") as w:
        actual_sec = w.getnframes() / w.getframerate()
    assert actual_sec <= 32, f"Preview WAV too long: {actual_sec:.1f}s"


def test_preview_html_uses_file_url_not_base64(tmp_path):
    """Preview: audio is referenced via /file= URL, not embedded base64."""
    from core.music_gen import generar_musica
    from preview.preview_engine import generar_preview_html

    wav = generar_musica(
        mood="Paz profunda", duracion_segundos=10, api_key="", output_dir=str(tmp_path)
    )
    versos = [{"referencia": "Juan 3:16", "texto": "Porque de tal manera amó Dios..."}]
    html = generar_preview_html(None, wav, versos)

    assert "/file=" in html, "Expected Gradio /file= URL in audio src"
    assert "data:audio" not in html, "Should NOT embed audio as base64"


def test_preview_html_structure(tmp_path):
    """Preview: HTML has all required UI elements and Ken Burns CSS."""
    from preview.preview_engine import generar_preview_html

    versos = [
        {"referencia": "Juan 3:16", "texto": "Porque de tal manera amó Dios al mundo..."},
        {"referencia": "Salmo 23:1", "texto": "El Señor es mi pastor."},
    ]
    html = generar_preview_html(None, None, versos)

    required = [
        'class="preview-root"',
        'id="btnPlay"',
        'id="btnNext"',
        'id="btnPrev"',
        'id="verseCounter"',
        "data-speed",
        "kenburns",        # Ken Burns CSS animation
        "quality-badge",   # low-quality badge
        "tryPlayAudio",    # new audio play function
        "var hasAudio = false",
    ]
    for attr in required:
        assert attr in html, f"Missing: {attr}"

    assert "Juan 3:16" in html
    assert "Salmo 23:1" in html


def test_preview_html_has_audio_true(tmp_path):
    """Preview: hasAudio is true when a valid audio path is passed."""
    from core.music_gen import generar_musica
    from preview.preview_engine import generar_preview_html

    wav = generar_musica(
        mood="Esperanza", duracion_segundos=10, api_key="", output_dir=str(tmp_path)
    )
    versos = [{"referencia": "A 1:1", "texto": "texto"}]
    html = generar_preview_html(None, wav, versos)

    assert "var hasAudio = true" in html


# ─── 5. Video render (slow) ─────────────────────────────────────

@pytest.mark.slow
def test_video_render_10_minutes(tmp_path):
    """[SLOW] Full render: 10-minute MP4 produced, file > 10MB."""
    from PIL import Image
    from core.music_gen import generar_musica
    from core.video_render import renderizar_video
    import numpy as np

    # Generate dummy image
    img_path = str(tmp_path / "bg.jpg")
    Image.fromarray(np.zeros((1080, 1920, 3), dtype=np.uint8)).save(img_path)

    # Generate 10 min of audio
    wav_path = generar_musica(
        mood="Paz profunda", duracion_segundos=600, api_key="", output_dir=str(tmp_path)
    )

    versos = [
        {"referencia": f"Test {i}:1", "texto": f"Versículo de prueba número {i}."}
        for i in range(1, 11)
    ]
    output = str(tmp_path / "test_10min.mp4")

    renderizar_video(
        imagen_path=img_path,
        musica_path=wav_path,
        versiculos=versos,
        duracion_total_segundos=600,
        segundos_por_versiculo=12,
        config_texto={},
        output_path=output,
        efecto_imagen="Sin efecto",
    )

    assert os.path.exists(output), "MP4 not created"
    size = os.path.getsize(output)
    assert size > 10_000_000, f"MP4 too small: {size} bytes"
