"""
Generación de música de fondo.
Priority order:
  1. Bundled loops (audio/loops/) — best quality, pre-selected worship tracks
  2. User-uploaded audio file — user provides their own track
  3. MusicGen local (requires torch + transformers)
  4. NumPy ambient synth — always works, last resort fallback
"""
from __future__ import annotations

import json
import os
import struct
import wave
import math
import random
import subprocess

import numpy as np

MOODS = {
    "Devoción": "devotional christian peaceful piano worship",
    "Paz profunda": "deep peace meditation ambient spiritual calm",
    "Esperanza": "hopeful uplifting gentle orchestral christian",
    "Meditación": "meditation spiritual calm ambient gentle",
    "Adoración": "worship instrumental gentle praise",
    "Salmos": "psalms ancient peaceful harp orchestral",
    "Sanación": "healing peaceful gentle ambient nature",
}

# ─── Bundled Loops ─────────────────────────────────────────────

_LOOPS_DIR = os.path.join(os.path.dirname(__file__), "..", "audio", "loops")
_MANIFEST_PATH = os.path.join(_LOOPS_DIR, "manifest.json")


def _load_manifest() -> dict:
    """Load the loops manifest. Returns empty dict if missing."""
    try:
        with open(_MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_available_loops() -> list[str]:
    """Return list of mood names that have a loop file present on disk."""
    manifest = _load_manifest()
    available = []
    for mood, info in manifest.get("moods", {}).items():
        loop_path = os.path.join(_LOOPS_DIR, info["file"])
        if os.path.isfile(loop_path):
            available.append(mood)
    return available


def _get_loop_path(mood: str) -> str | None:
    """Return the path to a loop file for the given mood, or None."""
    manifest = _load_manifest()
    info = manifest.get("moods", {}).get(mood)
    if not info:
        return None
    loop_path = os.path.join(_LOOPS_DIR, info["file"])
    return loop_path if os.path.isfile(loop_path) else None


def _decode_audio_to_wav(input_path: str, output_path: str, sr: int = 44100) -> str:
    """Decode any audio format to 16-bit stereo WAV using ffmpeg."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", str(sr), "-ac", "2", "-sample_fmt", "s16",
        "-f", "wav", output_path,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def _read_wav_samples(wav_path: str) -> tuple[np.ndarray, np.ndarray, int]:
    """Read a WAV file and return (left, right, sample_rate) as float32 arrays."""
    with wave.open(wav_path, "r") as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
    if n_channels == 2:
        left = samples[0::2]
        right = samples[1::2]
    else:
        left = samples
        right = samples.copy()
    return left, right, sr


def _crossfade_loop_stereo(
    left: np.ndarray, right: np.ndarray, sr: int,
    target_seconds: int, crossfade_sec: float = 3.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Extend a stereo audio clip to target duration using crossfade looping.
    Applies fade-in at start and fade-out at end.
    """
    target_samples = target_seconds * sr
    xf = min(int(crossfade_sec * sr), len(left) // 2)

    # Build output by repeating with crossfade overlap
    out_l = left.copy()
    out_r = right.copy()

    while len(out_l) < target_samples:
        fade_out = np.linspace(1, 0, xf, dtype=np.float32)
        fade_in = np.linspace(0, 1, xf, dtype=np.float32)

        # Crossfade region
        overlap_l = out_l[-xf:] * fade_out + left[:xf] * fade_in
        overlap_r = out_r[-xf:] * fade_out + right[:xf] * fade_in

        out_l = np.concatenate([out_l[:-xf], overlap_l, left[xf:]])
        out_r = np.concatenate([out_r[:-xf], overlap_r, right[xf:]])

    out_l = out_l[:target_samples]
    out_r = out_r[:target_samples]

    # Fade in/out
    fade_in_samples = min(sr * 3, target_samples)
    out_l[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples, dtype=np.float32)
    out_r[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples, dtype=np.float32)
    fade_out_samples = min(sr * 4, target_samples)
    out_l[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples, dtype=np.float32)
    out_r[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples, dtype=np.float32)

    return out_l, out_r


def _write_stereo_wav(
    path: str, left: np.ndarray, right: np.ndarray, sr: int = 44100,
) -> str:
    """Write stereo float32 arrays to a 16-bit WAV file."""
    n = len(left)
    with wave.open(path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        chunk_size = sr * 10
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            l16 = (np.clip(left[start:end], -1, 1) * 32767).astype(np.int16)
            r16 = (np.clip(right[start:end], -1, 1) * 32767).astype(np.int16)
            stereo = np.empty((end - start) * 2, dtype=np.int16)
            stereo[0::2] = l16
            stereo[1::2] = r16
            wf.writeframes(stereo.tobytes())
    return os.path.abspath(path)


def _generar_from_loop(
    mood: str, duracion_segundos: int, output_dir: str, loop_path: str = None,
) -> str:
    """
    Generate audio from a bundled loop or user-provided file.
    Decodes to WAV, loops with crossfade, writes output.
    """
    import tempfile

    if loop_path is None:
        loop_path = _get_loop_path(mood)
    if loop_path is None:
        raise FileNotFoundError(f"No loop file for mood '{mood}'")

    os.makedirs(output_dir, exist_ok=True)

    # Decode to temp WAV if not already WAV
    if loop_path.lower().endswith(".wav"):
        wav_path = loop_path
    else:
        tmp_wav = os.path.join(output_dir, "_temp_decoded.wav")
        wav_path = _decode_audio_to_wav(loop_path, tmp_wav)

    left, right, sr = _read_wav_samples(wav_path)

    # Clean up temp file
    if wav_path != loop_path and os.path.exists(wav_path):
        try:
            os.remove(wav_path)
        except OSError:
            pass

    # Loop to target duration
    out_l, out_r = _crossfade_loop_stereo(left, right, sr, duracion_segundos)

    out_path = os.path.join(output_dir, "musica_loop.wav")
    return _write_stereo_wav(out_path, out_l, out_r, sr)

# Progresiones de 4 acordes estilo himnos religiosos (frecuencias Hz)
# Referencia: himnos clásicos usan I-IV-V-I / I-vi-IV-V / I-V-vi-IV
_MOOD_CHORDS = {
    # "Devoción": I-IV-V-I en Do mayor — Himno clásico
    "Devoción": [
        (261.6, 329.6, 392.0),   # C maj  (I)
        (349.2, 440.0, 523.3),   # F maj  (IV)
        (392.0, 493.9, 587.3),   # G maj  (V)
        (261.6, 329.6, 392.0),   # C maj  (I) — resolución
    ],
    # "Paz profunda": I-vi-IV-V en Do — "Canon de Pachelbel" style
    "Paz profunda": [
        (261.6, 329.6, 392.0),   # C maj  (I)
        (220.0, 261.6, 329.6),   # A min  (vi)
        (349.2, 440.0, 523.3),   # F maj  (IV)
        (392.0, 493.9, 587.3),   # G maj  (V)
    ],
    # "Esperanza": I-V-vi-IV en Re — estilo alabanza moderna
    "Esperanza": [
        (293.7, 370.0, 440.0),   # D maj  (I)
        (415.3, 523.3, 622.3),   # Ab maj (V/relativo)
        (246.9, 293.7, 370.0),   # B min  (vi)
        (392.0, 493.9, 587.3),   # G maj  (IV)
    ],
    # "Meditación": i-VII-VI-VII en La menor — modal, Gregoriano
    "Meditación": [
        (220.0, 261.6, 329.6),   # A min  (i)
        (196.0, 246.9, 293.7),   # G maj  (VII)
        (174.6, 220.0, 261.6),   # F maj  (VI)
        (196.0, 246.9, 293.7),   # G maj  (VII) — no resuelve, etéreo
    ],
    # "Adoración": I-IV-I-V en Fa — cálido, himno de adoración
    "Adoración": [
        (349.2, 440.0, 523.3),   # F maj  (I)
        (261.6, 329.6, 392.0),   # C maj  (V/IV)
        (349.2, 440.0, 523.3),   # F maj  (I)
        (415.3, 523.3, 622.3),   # Ab maj (bVII — gospel)
    ],
    # "Salmos": i-iv-VII-III en La menor — estilo Salmo antiguo
    "Salmos": [
        (220.0, 261.6, 329.6),   # A min  (i)
        (293.7, 349.2, 440.0),   # D min  (iv)
        (196.0, 246.9, 293.7),   # G maj  (VII)
        (261.6, 329.6, 392.0),   # C maj  (III)
    ],
    # "Sanación": I-IV-vi-V en Re — suave y esperanzador
    "Sanación": [
        (293.7, 370.0, 440.0),   # D maj  (I)
        (392.0, 493.9, 587.3),   # G maj  (IV)
        (246.9, 293.7, 370.0),   # B min  (vi)
        (415.3, 493.9, 587.3),   # A maj  (V)
    ],
}


# ─── Osciladores ────────────────────────────────────────────────

def _osc(t, freq, phase=0.0, wave="sine"):
    """Oscilador simple: sine, triangle, soft_saw."""
    x = 2 * math.pi * freq * t + phase
    if wave == "sine":
        return np.sin(x)
    elif wave == "triangle":
        return (2 / math.pi) * np.arcsin(np.sin(x))
    elif wave == "soft_saw":
        return 0.6 * np.sin(x) + 0.3 * np.sin(2 * x) + 0.1 * np.sin(3 * x)
    return np.sin(x)


def _piano_note(t, freq, sr, amp=1.0):
    """
    Timbre sintético de piano: ataque rápido + decaimiento exponencial.
    Inharmonicity on upper partials (real piano strings are slightly stiff).
    6 partials with independent decay rates — brighter attack, warmer sustain.
    """
    block_t = t - t[0]
    # Slower decay = warmer grand piano sustain
    decay_rate = 1.2

    # Attack transient: 8ms click for key strike
    atk_samples = min(int(0.008 * sr), len(t))
    atk_env = np.ones(len(t), dtype=np.float32)
    if atk_samples > 0:
        atk_env[:atk_samples] = np.linspace(0, 1, atk_samples)

    # Main envelope with gentle sustain floor
    env = np.exp(-decay_rate * block_t)
    env = np.clip(env, 0.03, 1.0) * atk_env

    # Inharmonicity coefficient (real piano ~0.0001 for mid-range)
    B = 0.00012
    def partial_freq(n):
        return freq * n * math.sqrt(1 + B * n * n)

    # 6 partials with independent decay (higher = faster decay)
    note = (
        0.50 * np.sin(2 * math.pi * partial_freq(1) * t) +
        0.22 * np.sin(2 * math.pi * partial_freq(2) * t) * np.exp(-1.8 * block_t) +
        0.12 * np.sin(2 * math.pi * partial_freq(3) * t) * np.exp(-2.8 * block_t) +
        0.07 * np.sin(2 * math.pi * partial_freq(4) * t) * np.exp(-4.0 * block_t) +
        0.05 * np.sin(2 * math.pi * partial_freq(5) * t) * np.exp(-5.5 * block_t) +
        0.03 * np.sin(2 * math.pi * partial_freq(6) * t) * np.exp(-7.0 * block_t)
    )

    # Sympathetic resonance: very quiet octave below (pedal effect)
    resonance = 0.04 * np.sin(2 * math.pi * freq * 0.5 * t) * np.exp(-0.5 * block_t)
    note += resonance

    return amp * note * env


def _strings_note(t, freq, amp=1.0):
    """
    Timbre de cuerdas: 5-voice section with independent vibrato per voice.
    Slow attack (bowed strings), rich harmonic content.
    """
    # Slow bow attack — strings don't hit instantly
    block_t = t - t[0]
    bow_atk = np.clip(block_t / 0.8, 0, 1)  # 800ms attack

    # 5 voices with independent vibrato rates (real section)
    voices = [
        (1.0000, 5.2, 0.0),
        (1.0018, 5.7, 0.4),
        (0.9982, 5.0, 0.8),
        (1.0025, 5.9, 1.2),
        (0.9975, 4.8, 1.6),
    ]
    vibrato_depth = 0.0025

    note = np.zeros(len(t), dtype=np.float64)
    for detune, vib_rate, vib_phase in voices:
        vib = 1.0 + vibrato_depth * np.sin(2 * math.pi * vib_rate * t + vib_phase)
        f = freq * detune * vib
        voice = (
            0.50 * np.sin(2 * math.pi * f * t) +
            0.28 * np.sin(2 * math.pi * f * 2 * t) +
            0.12 * np.sin(2 * math.pi * f * 3 * t) +
            0.06 * np.sin(2 * math.pi * f * 4 * t)
        )
        note += voice / len(voices)

    return amp * note * bow_atk


def _choir_note(t, freq, amp=1.0):
    """
    Timbre de coro/pad vocal: 7 voices with breathy texture.
    Two formant bands (ahh ~500Hz, ooh ~350Hz) for vocal quality.
    """
    # Slow swell — choir takes time to build
    block_t = t - t[0]
    swell = np.clip(block_t / 1.5, 0, 1)  # 1.5s swell

    # 7 voices with gentle detuning
    offsets = [1.0, 1.0015, 0.9985, 1.003, 0.997, 1.005, 0.995]
    note = np.zeros(len(t), dtype=np.float64)
    for d in offsets:
        note += np.sin(2 * math.pi * freq * d * t) / len(offsets)

    # Dual formant bands for vocal warmth
    if freq < 400:
        # "Ahh" formant ~500Hz
        note += 0.10 * np.sin(2 * math.pi * 500 * t) * swell
        # "Ooh" formant ~350Hz
        note += 0.06 * np.sin(2 * math.pi * 350 * t) * swell

    # Breathy texture (filtered noise, very quiet)
    breath = np.random.randn(len(t)).astype(np.float32) * 0.015
    kernel = np.ones(256, dtype=np.float32) / 256
    breath = np.convolve(breath, kernel, mode='same')
    note += breath * swell

    return amp * note * swell


# ─── Envolventes ────────────────────────────────────────────────

def _adsr_envelope(n, sr, attack=2.0, decay=1.0, sustain=0.75, release=3.0):
    """Genera una envolvente ADSR para una nota de n muestras."""
    env = np.ones(n, dtype=np.float32) * sustain
    a = min(int(attack * sr), n)
    d = min(int(decay * sr), n - a)
    r = min(int(release * sr), n)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if d > 0:
        env[a:a + d] = np.linspace(1, sustain, d)
    if r > 0:
        env[-r:] = np.linspace(sustain, 0, r)
    return env


# ─── Efectos ────────────────────────────────────────────────────

def _comb_filter(signal, delay_samples, feedback, damping):
    """Feedback comb filter with one-pole lowpass damping — vectorized in chunks."""
    n = len(signal)
    out = np.zeros(n, dtype=np.float32)
    # Process in chunks of delay_samples for partial vectorization
    prev_filtered = 0.0
    for start in range(0, n, delay_samples):
        end = min(start + delay_samples, n)
        for i in range(start, end):
            rd = i - delay_samples
            delayed = out[rd] if rd >= 0 else 0.0
            filtered = (1 - damping) * delayed + damping * prev_filtered
            prev_filtered = filtered
            out[i] = signal[i] + feedback * filtered
    return out


def _allpass_filter(signal, delay_samples, gain=0.7):
    """Allpass filter — iterative for correctness, small delays only."""
    n = len(signal)
    buf = np.zeros(delay_samples, dtype=np.float32)
    out = np.zeros(n, dtype=np.float32)
    for i in range(n):
        buf_idx = i % delay_samples
        delayed = buf[buf_idx]
        out[i] = -gain * signal[i] + delayed
        buf[buf_idx] = signal[i] + gain * out[i]
    return out


def _reverb(signal, sr, room_size=0.6, damping=0.5):
    """
    Schroeder reverb: 4 comb filters in parallel → 2 allpass in series.
    """
    n = len(signal)

    # 4 parallel comb filters
    comb_configs = [
        (29.7, 0.805), (37.1, 0.827), (41.1, 0.783), (43.7, 0.764),
    ]
    comb_sum = np.zeros(n, dtype=np.float32)
    for delay_ms, g in comb_configs:
        delay_samp = int(delay_ms / 1000 * sr)
        if delay_samp >= n:
            continue
        comb_sum += _comb_filter(signal, delay_samp, g * room_size, damping)

    comb_sum *= 0.25

    # 2 series allpass (small delays — fast even iterative)
    ap1_delay = int(5.0 / 1000 * sr)   # ~220 samples
    ap2_delay = int(1.7 / 1000 * sr)   # ~75 samples
    diffused = _allpass_filter(comb_sum, ap1_delay, gain=0.7)
    diffused = _allpass_filter(diffused, ap2_delay, gain=0.7)

    wet_level = 0.30
    return (signal * (1 - wet_level) + diffused * wet_level).astype(np.float32)


def _chorus(signal, sr, rate_l=0.45, rate_r=0.53, depth_ms=4.0):
    """
    LFO chorus con rates independientes para L y R.
    Crea batido natural entre canales — calor orquestal.
    """
    n = len(signal)
    t = np.arange(n, dtype=np.float32) / sr
    max_d = int(sr * 0.025)  # buffer de 25ms
    buf = np.zeros(n + max_d, dtype=np.float32)
    buf[max_d:] = signal.astype(np.float32)

    depth_samp = depth_ms / 1000 * sr
    lfo_l = (np.sin(2 * np.pi * rate_l * t) * 0.5 + 0.5) * depth_samp + 3
    lfo_r = (np.sin(2 * np.pi * rate_r * t) * 0.5 + 0.5) * depth_samp + 4

    idx_l = (np.arange(n) + max_d - lfo_l.astype(int)).clip(0, n + max_d - 1)
    idx_r = (np.arange(n) + max_d - lfo_r.astype(int)).clip(0, n + max_d - 1)

    left  = signal * 0.65 + buf[idx_l] * 0.35
    right = signal * 0.65 + buf[idx_r] * 0.35
    return left.astype(np.float32), right.astype(np.float32)


# ─── Generación principal ────────────────────────────────────────

def generar_musica(mood: str, duracion_segundos: int, api_key: str,
                   output_dir: str = "output",
                   audio_file: str = None) -> str:
    """
    Genera música instrumental de fondo.
    Priority: user file > bundled loop > NumPy synth fallback.
    Retorna: path al archivo .wav
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. User-provided audio file
    if audio_file and os.path.isfile(audio_file):
        try:
            return _generar_from_loop(mood, duracion_segundos, output_dir, loop_path=audio_file)
        except Exception:
            pass  # Fall through to other options

    # 2. Bundled loop for this mood
    loop_path = _get_loop_path(mood)
    if loop_path:
        try:
            return _generar_from_loop(mood, duracion_segundos, output_dir)
        except Exception:
            pass  # Fall through to synth

    # 3. Fallback: NumPy ambient synth
    return _generar_ambient(mood, duracion_segundos, output_dir)


def generar_musica_musicgen(prompt: str, duracion_clip: int = 15,
                            duracion_total: int = 60,
                            output_dir: str = "output") -> str:
    """
    Genera música con MusicGen (Meta) local.
    Genera un clip corto y lo loopea con crossfade.

    Requiere: torch, transformers, soundfile
    """
    import torch
    import soundfile as sf
    from transformers import AutoProcessor, MusicgenForConditionalGeneration

    os.makedirs(output_dir, exist_ok=True)

    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    try:
        model = model.to(device)
    except Exception:
        device = "cpu"
        model = model.to(device)

    max_tokens = duracion_clip * 50
    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    audio_values = model.generate(**inputs, max_new_tokens=max_tokens)

    sr = model.config.audio_encoder.sampling_rate
    audio = audio_values[0, 0].cpu().numpy()

    if duracion_total > duracion_clip:
        audio = _crossfade_loop(audio, sr, duracion_total)

    path = os.path.join(output_dir, "musica_musicgen.wav")
    sf.write(path, audio, sr)
    return os.path.abspath(path)


def _crossfade_loop(audio, sr: int, duracion_total: int, crossfade_sec: float = 3.0):
    """Crea un loop largo con crossfade suave entre repeticiones."""
    crossfade_samples = int(crossfade_sec * sr)
    target_samples = duracion_total * sr
    output = audio.copy()

    while len(output) < target_samples:
        fade_out = np.linspace(1, 0, crossfade_samples).astype(np.float32)
        fade_in = np.linspace(0, 1, crossfade_samples).astype(np.float32)
        overlap_end = output[-crossfade_samples:] * fade_out
        overlap_start = audio[:crossfade_samples] * fade_in
        mixed = overlap_end + overlap_start
        output = np.concatenate([
            output[:-crossfade_samples],
            mixed,
            audio[crossfade_samples:]
        ])

    return output[:target_samples]


def _generar_ambient(mood: str, duracion_segundos: int, output_dir: str) -> str:
    """
    Two-pass ambient generator: piano, strings, choir, arpeggio, sub-bass.

    Pass 1: Render all chord blocks into memory with overlap regions.
    Pass 2: Crossfade overlaps, apply global normalization, reverb, chorus, write WAV.

    This eliminates per-block normalization pumping and abrupt chord transitions.
    """
    sr = 44100
    total_samples = sr * duracion_segundos
    block_sec = 8
    block_samples = sr * block_sec
    crossfade_sec = 2.0
    crossfade_samples = int(crossfade_sec * sr)

    chords = _MOOD_CHORDS.get(mood, _MOOD_CHORDS["Paz profunda"])
    path = os.path.join(output_dir, "musica_ambient.wav")

    # ═══ PASS 1: Render blocks into memory ══════════════════════════
    blocks = []
    time_offset = 0.0
    chord_idx = 0
    samples_generated = 0

    while samples_generated < total_samples + crossfade_samples:
        n = block_samples + crossfade_samples  # extra for overlap
        n = min(n, total_samples + crossfade_samples - samples_generated + crossfade_samples)
        if n <= 0:
            break

        t = np.linspace(time_offset, time_offset + n / sr, n,
                        endpoint=False).astype(np.float32)
        block_t = t - t[0]

        freqs = chords[chord_idx % len(chords)]

        # ── 1. PIANO: arpeggiated chord ─────────────────────────
        piano = np.zeros(n, dtype=np.float32)
        piano_amp = 0.20
        for i, freq in enumerate(freqs):
            note_offset = int(i * 0.10 * sr)  # 100ms stagger
            if note_offset < n:
                t_note = block_t[note_offset:]
                piano[note_offset:] += _piano_note(
                    t_note, freq, sr, amp=piano_amp / (i + 1) ** 0.4
                )

        # ── 2. STRINGS: sustained orchestral pad ────────────────
        strings = np.zeros(n, dtype=np.float32)
        strings_amp = 0.24
        for i, freq in enumerate(freqs):
            strings += _strings_note(t, freq, amp=strings_amp / (i + 1) ** 0.5)

        # ── 3. CHOIR: ethereal vocal pad ────────────────────────
        choir = np.zeros(n, dtype=np.float32)
        choir_amp = 0.14
        for i, freq in enumerate(freqs):
            choir += _choir_note(t, freq, amp=choir_amp / (i + 1) ** 0.7)

        # ── 4. ARPEGGIO: piano timbre, octave up ───────────────
        melody = np.zeros(n, dtype=np.float32)
        arp_rate = 2.5  # seconds per note
        arp_amp = 0.06
        for k in range(int((n / sr) / arp_rate) + 1):
            note_start = int(k * arp_rate * sr)
            note_len = min(int(arp_rate * sr), n - note_start)
            if note_start >= n or note_len <= 0:
                break
            note_idx = (chord_idx + k) % len(freqs)
            freq_arp = freqs[note_idx] * 2
            t_arp = block_t[note_start:note_start + note_len]
            # Use piano timbre for arpeggio instead of pure sine
            arp_note = _piano_note(t_arp, freq_arp, sr, amp=arp_amp)
            # Gentle envelope
            env_arp = np.ones(note_len, dtype=np.float32)
            atk = min(int(0.15 * sr), note_len)
            rel = min(int(0.6 * sr), note_len)
            if atk > 0:
                env_arp[:atk] = np.linspace(0, 1, atk)
            if rel > 0:
                env_arp[-rel:] *= np.linspace(1, 0, rel)
            melody[note_start:note_start + note_len] += arp_note * env_arp

        # ── 5. SUB-BASS: root note one octave below ────────────
        sub_bass = np.zeros(n, dtype=np.float32)
        sub_freq = freqs[0] * 0.5  # octave below root
        sub_bass = 0.10 * np.sin(2 * math.pi * sub_freq * t)
        # Gentle low-pass via smoothing
        kernel_sub = np.ones(512, dtype=np.float32) / 512
        sub_bass = np.convolve(sub_bass, kernel_sub, mode='same').astype(np.float32)

        # ── 6. BREATH noise ─────────────────────────────────────
        noise = np.random.randn(n).astype(np.float32) * 0.010
        kernel = np.ones(192, dtype=np.float32) / 192
        noise = np.convolve(noise, kernel, mode='same').astype(np.float32)

        # ── Mix layers ──────────────────────────────────────────
        pad = piano + strings + choir + melody + sub_bass + noise

        # ── ADSR per block (gentle shape, NOT normalization) ────
        env = _adsr_envelope(n, sr, attack=2.0, decay=1.5, sustain=0.85, release=3.0)
        pad *= env

        # ── LFO amplitude (organic movement) ────────────────────
        lfo_rate = 0.05 + random.uniform(-0.008, 0.008)
        lfo = 1.0 + 0.05 * np.sin(2 * math.pi * lfo_rate * t)
        pad *= lfo

        blocks.append(pad)
        samples_generated += block_samples  # advance by block_sec, not including overlap
        time_offset += block_sec
        chord_idx += 1

    # ═══ PASS 2: Crossfade + global normalize + effects + write ═══

    # Merge blocks with crossfade overlap
    if not blocks:
        blocks = [np.zeros(total_samples, dtype=np.float32)]

    merged = blocks[0][:block_samples + crossfade_samples].copy()
    for i in range(1, len(blocks)):
        block = blocks[i]
        overlap = min(crossfade_samples, len(merged), len(block))
        if overlap > 0:
            fade_out = np.linspace(1, 0, overlap, dtype=np.float32)
            fade_in = np.linspace(0, 1, overlap, dtype=np.float32)
            # Crossfade the overlapping region
            merged[-overlap:] = merged[-overlap:] * fade_out + block[:overlap] * fade_in
            # Append the rest of this block
            remaining_block = block[overlap:block_samples + crossfade_samples]
            if len(remaining_block) > 0:
                merged = np.concatenate([merged, remaining_block])
        else:
            merged = np.concatenate([merged, block[:block_samples]])

    # Trim to exact duration
    merged = merged[:total_samples]
    if len(merged) < total_samples:
        merged = np.concatenate([merged, np.zeros(total_samples - len(merged), dtype=np.float32)])

    # ── Global fade in/out ──────────────────────────────────────
    fade_in_samples = min(sr * 4, total_samples)
    merged[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples, dtype=np.float32)
    fade_out_samples = min(sr * 5, total_samples)
    merged[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples, dtype=np.float32)

    # ── Reverb (applied globally — consistent tail) ─────────────
    merged = _reverb(merged, sr, room_size=0.55, damping=0.35)

    # ── GLOBAL normalization (eliminates pumping) ───────────────
    peak = np.max(np.abs(merged))
    if peak > 0:
        merged = merged / peak * 0.72

    # ── Stereo chorus (warmth) ──────────────────────────────────
    left, right = _chorus(merged, sr, rate_l=0.40, rate_r=0.55, depth_ms=3.0)

    # ═══ Write WAV ══════════════════════════════════════════════════
    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)

        # Write in chunks to limit memory
        chunk_size = sr * 10  # 10 seconds at a time
        for start in range(0, total_samples, chunk_size):
            end = min(start + chunk_size, total_samples)
            l_chunk = (np.clip(left[start:end], -1, 1) * 32767).astype(np.int16)
            r_chunk = (np.clip(right[start:end], -1, 1) * 32767).astype(np.int16)
            stereo = np.empty((end - start) * 2, dtype=np.int16)
            stereo[0::2] = l_chunk
            stereo[1::2] = r_chunk
            wav_file.writeframes(stereo.tobytes())

    return os.path.abspath(path)


def generate_playlist(
    moods: list,
    total_seconds: int,
    output_dir: str,
    crossfade_seconds: float = 4.0,
    audio_files: dict = None,
) -> str:
    """
    Generate a single WAV of total_seconds by alternating between moods.
    Each mood gets total_seconds // len(moods) seconds.
    Smooth crossfade between segments.

    Args:
        moods: List of mood names (keys in MOODS dict or manifest)
        total_seconds: Total output duration in seconds
        output_dir: Directory for temp files and final output
        crossfade_seconds: Duration of crossfade between segments
        audio_files: Optional dict mapping mood -> file path override

    Returns:
        Absolute path to the combined WAV file.
    """
    if not moods:
        raise ValueError("moods list cannot be empty")

    os.makedirs(output_dir, exist_ok=True)
    sr = 44100
    xf_samples = int(crossfade_seconds * sr)
    segment_seconds = max(total_seconds // len(moods), 10)

    # Generate each mood segment into a temp sub-dir
    segment_paths = []
    for i, mood in enumerate(moods):
        seg_dir = os.path.join(output_dir, f"_seg_{i}")
        os.makedirs(seg_dir, exist_ok=True)
        override = (audio_files or {}).get(mood)
        path = generar_musica(
            mood=mood,
            duracion_segundos=segment_seconds,
            api_key="",
            output_dir=seg_dir,
            audio_file=override,
        )
        segment_paths.append(path)

    def _to_stereo_arrays(path):
        """Read any audio file into (left, right, sr) float32 arrays."""
        if path.lower().endswith(".wav"):
            return _read_wav_samples(path)
        tmp = path + "_decoded.wav"
        _decode_audio_to_wav(path, tmp, sr=sr)
        result = _read_wav_samples(tmp)
        try:
            os.remove(tmp)
        except OSError:
            pass
        return result

    # Crossfade-concatenate all segments
    out_l = np.array([], dtype=np.float32)
    out_r = np.array([], dtype=np.float32)

    for seg_path in segment_paths:
        left, right, _ = _to_stereo_arrays(seg_path)
        if len(out_l) == 0:
            out_l, out_r = left, right
        else:
            xf = min(xf_samples, len(out_l), len(left))
            if xf > 0:
                fade_out = np.linspace(1.0, 0.0, xf, dtype=np.float32)
                fade_in = np.linspace(0.0, 1.0, xf, dtype=np.float32)
                blend_l = out_l[-xf:] * fade_out + left[:xf] * fade_in
                blend_r = out_r[-xf:] * fade_out + right[:xf] * fade_in
                out_l = np.concatenate([out_l[:-xf], blend_l, left[xf:]])
                out_r = np.concatenate([out_r[:-xf], blend_r, right[xf:]])
            else:
                out_l = np.concatenate([out_l, left])
                out_r = np.concatenate([out_r, right])

    # Trim / pad to exact duration
    target = total_seconds * sr
    if len(out_l) > target:
        out_l, out_r = out_l[:target], out_r[:target]
    elif len(out_l) < target:
        pad = target - len(out_l)
        out_l = np.concatenate([out_l, np.zeros(pad, dtype=np.float32)])
        out_r = np.concatenate([out_r, np.zeros(pad, dtype=np.float32)])

    # Global fade in/out
    fi = min(sr * 3, target)
    fo = min(sr * 4, target)
    out_l[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    out_r[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    out_l[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    out_r[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)

    out_path = os.path.join(output_dir, "playlist.wav")
    return _write_stereo_wav(out_path, out_l, out_r, sr=sr)


def _generar_silencio(duracion_segundos: int, output_dir: str) -> str:
    """Genera un archivo WAV silencioso de la duración especificada."""
    path = os.path.join(output_dir, "musica_silencio.wav")
    sr = 44100
    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)
        block = struct.pack("<" + "h" * (sr * 2), *([0] * (sr * 2)))
        for _ in range(duracion_segundos):
            wav_file.writeframes(block)
    return os.path.abspath(path)
