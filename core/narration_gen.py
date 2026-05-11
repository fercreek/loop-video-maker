"""
core/narration_gen.py — Genera audio de narración para historias bíblicas.

Backends (por prioridad):
  1. ElevenLabs API  — si elevenlabs_api_key en config.json (premium)
  2. Edge TTS        — Microsoft neural, GRATIS, voces ES-MX Jorge/Dalia ✅ DEFAULT
  3. macOS say       — DESCARTADO (calidad inaceptable)

Voces Edge TTS activas:
  jorge  → es-MX-JorgeNeural   (masculina, devocional — historias largas)
  dalia  → es-MX-DaliaNeural   (femenina, cálida — oraciones/shorts)

Cachea WAV en audio/narrations/{hash}.wav — no re-genera si ya existe.

Uso:
    from core.narration_gen import generate_narration
    wav_path = generate_narration("Texto a narrar", "scene_001")
    wav_path = generate_narration("Texto", "scene_001", voice="dalia")
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR    = Path(__file__).parent.parent
NARRATIONS_DIR = PROJECT_DIR / "audio" / "narrations"
CONFIG_PATH    = PROJECT_DIR / "config.json"

# ─── Edge TTS — voces activas ES-MX ──────────────────────────────────────────
EDGE_VOICES = {
    "jorge":  "es-MX-JorgeNeural",   # masculina — historias largas, narración épica
    "dalia":  "es-MX-DaliaNeural",   # femenina  — oraciones, shorts devocionales
    "carlos": "es-MX-CarlosNeural",  # masculina alternativa
    "marina": "es-MX-MarinaNeural",  # femenina alternativa
}

DEFAULT_VOICE = "jorge"   # narración devocional masculina
EDGE_RATE     = "-8%"     # ritmo ligeramente más pausado que default


def _text_hash(text: str, voice: str, backend: str = "edge") -> str:
    """Hash incluye backend para evitar colisiones edge vs elevenlabs en caché."""
    key = f"{backend}:{voice}:{text}"
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def get_audio_duration(wav_path: Path) -> float:
    """Retorna duración en segundos. Lanza RuntimeError si ffprobe falla."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(wav_path)],
        capture_output=True, text=True,
    )
    raw = result.stdout.strip()
    if not raw:
        raise RuntimeError(
            f"ffprobe duración vacía para {wav_path} — stderr: {result.stderr[:200]}"
        )
    return float(raw)


# ─── Edge TTS backend ─────────────────────────────────────────────────────────
async def _edge_tts_async(text: str, voice_name: str, mp3_path: Path, rate: str) -> list[dict]:
    """
    Llama Edge TTS async API → MP3 + word boundaries.
    Retorna lista de {word, offset_sec, duration_sec} para subtítulos sincronizados.
    """
    try:
        import edge_tts
    except ImportError:
        raise RuntimeError("edge-tts no instalado. Run: .venv/bin/pip install edge-tts")

    communicate = edge_tts.Communicate(text, voice_name, rate=rate)
    sentence_boundaries: list[dict] = []

    with open(mp3_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sentence_boundaries.append({
                    "type":        chunk["type"],
                    "text":        chunk["text"],
                    "offset_sec":  chunk["offset"]   / 10_000_000,
                    "duration_sec": chunk["duration"] / 10_000_000,
                })

    # Expandir SentenceBoundary → word-level usando estimación proporcional por caracteres
    # Precisión ~0.2-0.3s/palabra — suficiente para subtítulos karaoke
    word_boundaries: list[dict] = []
    for sb in sentence_boundaries:
        sentence_text = sb["text"].strip()
        sentence_start = sb["offset_sec"]
        sentence_dur   = sb["duration_sec"]
        words = sentence_text.split()
        if not words:
            continue
        total_chars = sum(len(w) for w in words) or 1
        cursor = sentence_start
        for word in words:
            word_dur = (len(word) / total_chars) * sentence_dur
            word_boundaries.append({
                "word":         word,
                "offset_sec":   cursor,
                "duration_sec": word_dur,
            })
            cursor += word_dur

    return word_boundaries


def _edge_to_wav(
    text: str,
    wav_path: Path,
    voice_key: str = DEFAULT_VOICE,
    rate: str = EDGE_RATE,
) -> list[dict]:
    """
    Edge TTS → MP3 → WAV 44100Hz estéreo.
    Retorna word boundaries [{word, offset_sec, duration_sec}] para subtítulos.
    También guarda sidecar JSON: {wav_path}.boundaries.json
    """
    voice_name = EDGE_VOICES.get(voice_key, EDGE_VOICES[DEFAULT_VOICE])
    mp3_path = wav_path.with_suffix(".mp3")

    # Ejecutar async → MP3 + boundaries
    boundaries = asyncio.run(_edge_tts_async(text, voice_name, mp3_path, rate))

    if not mp3_path.exists() or mp3_path.stat().st_size < 1000:
        raise RuntimeError(f"Edge TTS no generó audio válido en {mp3_path}")

    # MP3 → WAV 44100Hz estéreo (ffmpeg)
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp3_path), "-ar", "44100", "-ac", "2", str(wav_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg MP3→WAV falló: {result.stderr[-300:]}")

    mp3_path.unlink(missing_ok=True)

    # Guardar sidecar de boundaries para subtítulos
    if boundaries:
        import json as _j
        sidecar = wav_path.with_suffix(".boundaries.json")
        with open(sidecar, "w", encoding="utf-8") as f:
            _j.dump(boundaries, f, ensure_ascii=False, indent=2)

    return boundaries


# ─── ElevenLabs backend (premium opcional) ────────────────────────────────────
def _elevenlabs_to_wav(text: str, wav_path: Path, api_key: str, voice_id: str) -> None:
    """ElevenLabs API → WAV. Requiere: pip install elevenlabs."""
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import save
    except ImportError:
        raise RuntimeError("elevenlabs no instalado. Run: .venv/bin/pip install elevenlabs")

    client = ElevenLabs(api_key=api_key)
    mp3_path = wav_path.with_suffix(".mp3")

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    save(audio, str(mp3_path))

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp3_path), "-ar", "44100", "-ac", "2", str(wav_path)],
        check=True, capture_output=True,
    )
    mp3_path.unlink(missing_ok=True)


# ─── Public API ───────────────────────────────────────────────────────────────
def generate_narration(
    text: str,
    scene_id: str,
    voice: str = DEFAULT_VOICE,
    force: bool = False,
    story_id: str | None = None,
) -> Path:
    """
    Genera narración de audio para un texto dado.

    Args:
        text:     texto a narrar
        scene_id: identificador (ej: 'david-goliat_s01') — para naming del archivo
        voice:    clave de voz: 'jorge' | 'dalia' | 'carlos' | 'marina'
        force:    re-generar aunque exista caché
        story_id: si se provee, guarda en audio/narrations/{story_id}/ (evita fs slowdown 700+ archivos planos)

    Returns:
        Path al archivo WAV generado

    Priority:
        1. ElevenLabs (si elevenlabs_api_key en config.json)
        2. Edge TTS jorge/dalia (default, gratis, neural ES-MX)
    """
    narr_dir = (NARRATIONS_DIR / story_id) if story_id else NARRATIONS_DIR
    narr_dir.mkdir(parents=True, exist_ok=True)

    # Normalizar voz → edge key
    voice_key = voice.lower().strip()
    if voice_key not in EDGE_VOICES:
        voice_key = DEFAULT_VOICE

    # 1. Intentar ElevenLabs si configurado
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        el_key   = cfg.get("elevenlabs_api_key", "")
        el_voice = cfg.get("elevenlabs_voice_id", "")
        if el_key and el_voice:
            h = _text_hash(text, el_voice, backend="elevenlabs")
            wav_path = narr_dir / f"{scene_id}_{h}.wav"
            if wav_path.exists() and not force:
                dur = get_audio_duration(wav_path)
                print(f"  [narr] Caché ElevenLabs: {wav_path.name} ({dur:.1f}s)")
                return wav_path
            print(f"  [narr] ElevenLabs: {scene_id} ({len(text.split())} palabras)...")
            t0 = time.time()
            _elevenlabs_to_wav(text, wav_path, el_key, el_voice)
            dur = get_audio_duration(wav_path)
            print(f"  [narr] ElevenLabs OK {time.time()-t0:.1f}s → {dur:.1f}s → {wav_path.name}")
            return wav_path
    except Exception as e:
        print(f"  [narr] ElevenLabs skip ({e}) → Edge TTS")

    # 2. Edge TTS (default — neural, gratis, ES-MX)
    h = _text_hash(text, voice_key, backend="edge")
    wav_path = narr_dir / f"{scene_id}_{h}.wav"

    if wav_path.exists() and not force:
        dur = get_audio_duration(wav_path)
        print(f"  [narr] Caché Edge: {wav_path.name} ({dur:.1f}s)")
        return wav_path

    voice_name = EDGE_VOICES[voice_key]
    print(f"  [narr] Edge TTS [{voice_key}/{voice_name}]: {scene_id} ({len(text.split())} palabras)...")
    t0 = time.time()
    _edge_to_wav(text, wav_path, voice_key=voice_key, rate=EDGE_RATE)
    elapsed = time.time() - t0
    dur = get_audio_duration(wav_path)
    print(f"  [narr] Edge OK {elapsed:.1f}s → {dur:.1f}s audio → {wav_path.name}")

    return wav_path


def get_word_boundaries(wav_path: Path) -> list[dict]:
    """
    Carga word boundaries desde sidecar JSON generado por Edge TTS.
    Retorna lista vacía si no existe (e.g. ElevenLabs o say).
    """
    import json as _j
    sidecar = wav_path.with_suffix(".boundaries.json")
    if sidecar.exists():
        with open(sidecar, encoding="utf-8") as f:
            return _j.load(f)
    return []


# ─── CLI ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test narración Edge TTS")
    parser.add_argument("--text", default="En el nombre del Señor todo es posible. David tomó su honda y confió en Dios.")
    parser.add_argument("--voice", default=DEFAULT_VOICE, choices=list(EDGE_VOICES))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    wav = generate_narration(args.text, "test_narration", voice=args.voice, force=args.force)
    dur = get_audio_duration(wav)
    print(f"Output: {wav}  ({dur:.1f}s)")
