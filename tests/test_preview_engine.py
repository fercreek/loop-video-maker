"""
Unit tests para preview/preview_engine.py — sin servidor, sin browser.

Correr:
    .venv/bin/pytest tests/test_preview_engine.py -v
"""
from __future__ import annotations

import sys
import os

# Asegurar que el root del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from preview.preview_engine import generar_preview_html

VERSOS = [
    {"referencia": "Juan 3:16", "texto": "Porque de tal manera amó Dios al mundo..."},
    {"referencia": "Salmo 23:1", "texto": "El Señor es mi pastor, nada me faltará."},
]


def test_html_contiene_elementos_clave():
    """El HTML generado debe incluir todos los elementos de control del preview."""
    html = generar_preview_html(None, None, VERSOS)
    for attr in ['class="preview-root"', 'id="btnPlay"', 'id="btnNext"', 'id="btnPrev"', 'id="verseCounter"']:
        assert attr in html, f"Falta elemento: {attr}"
    assert "data-speed" in html, "Faltan botones de velocidad"


def test_html_contiene_versos():
    """El HTML debe incrustar el texto y referencia de los versículos."""
    html = generar_preview_html(None, None, VERSOS)
    assert "Juan 3:16" in html
    assert "Salmo 23:1" in html
    assert "Porque de tal manera" in html


def test_html_sin_audio_no_tiene_src():
    """Sin audio_path, el tag <audio> no debe tener atributo src con valor."""
    html = generar_preview_html(None, None, VERSOS)
    # No debe aparecer src="..." con un archivo real
    assert 'src="/file=' not in html
    assert "src=\"data:audio" not in html


def test_html_con_audio_tiene_src(tmp_path):
    """Con un archivo de audio real, el HTML debe embeber el audio en base64."""
    # Crear un WAV mínimo válido (44 bytes de header)
    wav = tmp_path / "test.wav"
    wav.write_bytes(
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    html = generar_preview_html(None, str(wav), VERSOS)
    assert "data:audio" in html


def test_html_verso_unico():
    """Con un solo versículo el contador debe empezar en 1/1."""
    versos = [{"referencia": "Gén 1:1", "texto": "En el principio..."}]
    html = generar_preview_html(None, None, versos)
    assert "Gén 1:1" in html
    assert "1 /" in html


def test_html_hasaudio_false_sin_audio():
    """La variable JS hasAudio debe ser false cuando no hay audio."""
    html = generar_preview_html(None, None, VERSOS)
    assert "const hasAudio = false" in html


def test_html_hasaudio_true_con_audio(tmp_path):
    """La variable JS hasAudio debe ser true cuando hay audio."""
    wav = tmp_path / "test.wav"
    wav.write_bytes(
        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        b"D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    )
    html = generar_preview_html(None, str(wav), VERSOS)
    assert "const hasAudio = true" in html
