"""
Generación de música de fondo.
- Nivel 0: Ambient con NumPy (siempre funciona, sin deps extra)
- Nivel 1: MusicGen local (requiere torch + transformers, calidad superior)
- Nivel 2: Subir MP3/WAV propio (el usuario provee el audio)
"""
from __future__ import annotations

import os
import struct
import wave
import math
import random

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

# Parámetros musicales por mood (frecuencias base en Hz para acordes)
_MOOD_CHORDS = {
    "Devoción": [(261.6, 329.6, 392.0), (293.7, 349.2, 440.0)],      # C maj, D min
    "Paz profunda": [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6)],   # C maj, A min
    "Esperanza": [(293.7, 370.0, 440.0), (329.6, 415.3, 493.9)],      # D maj, E maj
    "Meditación": [(220.0, 261.6, 329.6), (196.0, 246.9, 293.7)],     # A min, G min
    "Adoración": [(261.6, 329.6, 392.0), (349.2, 440.0, 523.3)],      # C maj, F maj
    "Salmos": [(220.0, 277.2, 329.6), (246.9, 311.1, 370.0)],         # A, B
    "Sanación": [(261.6, 329.6, 392.0), (220.0, 277.2, 329.6)],       # C maj, A
}


def generar_musica(mood: str, duracion_segundos: int, api_key: str,
                   output_dir: str = "output") -> str:
    """
    Genera música instrumental de fondo.
    Usa generación ambient con NumPy (funciona siempre).
    Retorna: path al archivo .wav
    """
    os.makedirs(output_dir, exist_ok=True)
    return _generar_ambient(mood, duracion_segundos, output_dir)


def generar_musica_musicgen(prompt: str, duracion_clip: int = 15,
                            duracion_total: int = 60,
                            output_dir: str = "output") -> str:
    """
    Genera música con MusicGen (Meta) local.
    Genera un clip corto y lo loopea con crossfade.

    Requiere: torch, transformers, soundfile
    duracion_clip: segundos del clip base (15-30)
    duracion_total: duración final en segundos

    Retorna: path al archivo .wav
    """
    import torch
    import soundfile as sf
    import numpy as np
    from transformers import AutoProcessor, MusicgenForConditionalGeneration

    os.makedirs(output_dir, exist_ok=True)

    # Cargar modelo
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    try:
        model = model.to(device)
    except Exception:
        device = "cpu"
        model = model.to(device)

    # Generar clip base
    # ~50 tokens = 1 segundo de audio en MusicGen
    max_tokens = duracion_clip * 50
    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    audio_values = model.generate(**inputs, max_new_tokens=max_tokens)

    sr = model.config.audio_encoder.sampling_rate
    audio = audio_values[0, 0].cpu().numpy()

    # Si la duración total es mayor que el clip, hacer loop con crossfade
    if duracion_total > duracion_clip:
        audio = _crossfade_loop(audio, sr, duracion_total)

    path = os.path.join(output_dir, "musica_musicgen.wav")
    sf.write(path, audio, sr)
    return os.path.abspath(path)


def _crossfade_loop(audio, sr: int, duracion_total: int, crossfade_sec: float = 3.0):
    """Crea un loop largo con crossfade suave entre repeticiones."""
    import numpy as np

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


def _osc(t, freq, phase=0.0, wave="sine"):
    """Oscilador simple: sine, triangle, soft_saw."""
    x = 2 * math.pi * freq * t + phase
    if wave == "sine":
        return np.sin(x)
    elif wave == "triangle":
        return (2 / math.pi) * np.arcsin(np.sin(x))
    elif wave == "soft_saw":
        # Saw suavizado: suma de 3 armónicos
        return 0.6 * np.sin(x) + 0.3 * np.sin(2 * x) + 0.1 * np.sin(3 * x)
    return np.sin(x)


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


def _reverb(signal, sr, room_size=0.6, damping=0.5):
    """Reverb de Schroeder simplificado: 4 delay lines en paralelo."""
    delays_ms = [29.7, 37.1, 41.1, 43.7]
    gains = [0.80 * room_size, 0.75 * room_size, 0.70 * room_size, 0.68 * room_size]
    wet = np.zeros_like(signal)
    for delay_ms, g in zip(delays_ms, gains):
        delay_samples = int(delay_ms / 1000 * sr)
        if delay_samples >= len(signal):
            continue
        delayed = np.zeros_like(signal)
        delayed[delay_samples:] = signal[:-delay_samples] * g
        wet += delayed
    wet *= (1 - damping) * 0.35
    return signal * 0.65 + wet


def _generar_ambient(mood: str, duracion_segundos: int, output_dir: str) -> str:
    """
    Genera audio ambient enriquecido:
    - Pad de 3 capas (sine + triangle + soft_saw) con detune leve
    - Sub-bass suave
    - Ruido de fondo filtrado (breath)
    - Envolvente ADSR por nota
    - Reverb de Schroeder
    - Chorus/stereo widening
    - Fade global suave
    """
    sr = 44100
    total_samples = sr * duracion_segundos
    block_sec = 20
    block_samples = sr * block_sec

    chords = _MOOD_CHORDS.get(mood, _MOOD_CHORDS["Paz profunda"])
    chord_duration_sec = 10  # cambiar acorde cada 10 seg

    path = os.path.join(output_dir, "musica_ambient.wav")

    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)

        samples_written = 0
        chord_idx = 0
        chord_sec_counter = 0.0

        while samples_written < total_samples:
            n = min(block_samples, total_samples - samples_written)
            t = np.linspace(chord_sec_counter,
                            chord_sec_counter + n / sr, n,
                            endpoint=False).astype(np.float32)

            freqs = chords[chord_idx % len(chords)]

            # ── 1. PAD: 3 capas por nota, con detune suave ──────────────
            pad = np.zeros(n, dtype=np.float32)
            wave_types = ["sine", "triangle", "soft_saw"]
            layer_amps = [0.40, 0.25, 0.15]

            for i, freq in enumerate(freqs):
                note_amp = 1.0 / (i + 1) ** 0.7
                for wt, la in zip(wave_types, layer_amps):
                    detune = 1.0 + random.uniform(-0.002, 0.002)
                    phase = random.uniform(0, 2 * math.pi)
                    pad += note_amp * la * _osc(t, freq * detune, phase, wt)

                # Sub-octava para nota raíz
                if i == 0:
                    pad += 0.12 * np.sin(2 * math.pi * freq * 0.5 * t)

            # ── 2. BREATH: ruido suave de ambiente ──────────────────────
            noise = np.random.randn(n).astype(np.float32) * 0.018
            # Suavizar con ventana (simula filtro LP sencillo)
            kernel_size = 128
            kernel = np.ones(kernel_size, dtype=np.float32) / kernel_size
            noise = np.convolve(noise, kernel, mode='same')
            pad += noise

            # ── 3. ADSR por bloque ──────────────────────────────────────
            env = _adsr_envelope(n, sr, attack=2.5, decay=1.5, sustain=0.70, release=3.0)
            pad *= env

            # ── 4. LFO de amplitud muy suave (movimiento orgánico) ──────
            lfo_rate = 0.07 + random.uniform(-0.01, 0.01)
            lfo = 1.0 + 0.08 * np.sin(2 * math.pi * lfo_rate * t)
            pad *= lfo

            # ── 5. Reverb ───────────────────────────────────────────────
            pad = _reverb(pad, sr, room_size=0.55, damping=0.45)

            # ── 6. Fade in / out global ─────────────────────────────────
            if samples_written == 0:
                fi = min(sr * 5, n)
                pad[:fi] *= np.linspace(0, 1, fi)
            remaining = total_samples - samples_written
            if remaining <= sr * 5:
                fo = min(sr * 5, n)
                pad[-fo:] *= np.linspace(1, 0, fo)

            # ── 7. Normalizar ────────────────────────────────────────────
            peak = np.max(np.abs(pad))
            if peak > 0:
                pad = pad / peak * 0.72

            # ── 8. Stereo widening (chorus/delay asimétrico) ─────────────
            delay_l = int(sr * 0.007)   # 7ms izquierda
            delay_r = int(sr * 0.013)   # 13ms derecha
            left = np.zeros(n, dtype=np.float32)
            right = np.zeros(n, dtype=np.float32)
            left[delay_l:] = pad[:-delay_l] * 0.5 + pad[delay_l:] * 0.5
            right[delay_r:] = pad[:-delay_r] * 0.5 + pad[delay_r:] * 0.5
            left[:delay_l] = pad[:delay_l]
            right[:delay_r] = pad[:delay_r]

            # ── 9. Escribir WAV ──────────────────────────────────────────
            left_16 = (np.clip(left, -1, 1) * 32767).astype(np.int16)
            right_16 = (np.clip(right, -1, 1) * 32767).astype(np.int16)
            stereo = np.empty(n * 2, dtype=np.int16)
            stereo[0::2] = left_16
            stereo[1::2] = right_16
            wav_file.writeframes(stereo.tobytes())

            samples_written += n
            chord_sec_counter += n / sr
            if chord_sec_counter >= chord_duration_sec * (chord_idx + 1):
                chord_idx += 1

    return os.path.abspath(path)


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
