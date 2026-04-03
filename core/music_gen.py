"""
Generación de música de fondo.
- Nivel 0: Ambient con NumPy (siempre funciona, sin deps extra)
  Timbres: piano sintético, cuerdas, coro, arpeggio melódico
  Progresiones: 4 acordes estilo himnos religiosos (I-IV-V-I)
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
    Referencia: piano acústico tiene ataque ~5ms, decaimiento ~1-3s.
    Armonicos: fundamental + 2a (más débil) + 3a (aún más débil).
    """
    # Envolvente piano: ataque 10ms, decaimiento exponencial
    decay_rate = 1.8  # más rápido = piano más seco; 1.2 = grand piano
    env = np.exp(-decay_rate * (t % (1.0 / max(freq * 0.001, 0.5))))
    # En bloques de tiempo lo simplificamos: decaimiento global del bloque
    block_t = t - t[0]
    env = np.exp(-decay_rate * block_t)
    env = np.clip(env, 0.02, 1.0)  # nunca cero — ligero sustain

    # Armonicos del piano (brillantez)
    note = (
        0.60 * np.sin(2 * math.pi * freq * t) +
        0.25 * np.sin(2 * math.pi * freq * 2 * t) * np.exp(-2.5 * block_t) +
        0.10 * np.sin(2 * math.pi * freq * 3 * t) * np.exp(-4.0 * block_t) +
        0.05 * np.sin(2 * math.pi * freq * 4 * t) * np.exp(-6.0 * block_t)
    )
    return amp * note * env


def _strings_note(t, freq, amp=1.0):
    """
    Timbre de cuerdas: soft_saw con vibrato lento.
    Referencia: sección de cuerdas orquestales — warm, sostenido.
    """
    vibrato_rate = 5.5   # Hz — vibrato estándar de cuerdas
    vibrato_depth = 0.003  # ±0.3% — sutil
    vib = 1.0 + vibrato_depth * np.sin(2 * math.pi * vibrato_rate * t)

    # 3 voces levemente desafinadas para efecto de sección
    detune = [1.0, 1.0015, 0.9985]
    note = sum(
        (1 / 3) * (
            0.55 * np.sin(2 * math.pi * freq * d * vib * t) +
            0.30 * np.sin(2 * math.pi * freq * d * vib * 2 * t) +
            0.15 * np.sin(2 * math.pi * freq * d * vib * 3 * t)
        )
        for d in detune
    )
    return amp * note


def _choir_note(t, freq, amp=1.0):
    """
    Timbre de coro/pad vocal: senos levemente desafinados + formante suave.
    Referencia: coro gospel/orquestal — etéreo, espiritual.
    """
    # 5 "voces" con detuning leve (simula unísono de coro)
    offsets = [1.0, 1.002, 0.998, 1.005, 0.995]
    note = sum(
        (1 / len(offsets)) * np.sin(2 * math.pi * freq * d * t)
        for d in offsets
    )
    # Formante vocal suave: refuerzo en ~500Hz (vowel "ahh")
    if freq < 300:
        formante = 0.15 * np.sin(2 * math.pi * 500 * t)
        note += formante
    return amp * note


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

def _reverb(signal, sr, room_size=0.6, damping=0.5):
    """Reverb de Schroeder: 4 delay lines en paralelo."""
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
    Genera audio con timbres de piano sintético, cuerdas y coro.
    Referencia sonora: himnos religiosos / música de adoración orquestal.

    Capas:
      1. Piano: ataque rápido, decaimiento natural, armonicos brillantes
      2. Cuerdas: soft_saw con vibrato — sección orquestal sostenida
      3. Coro/pad: senos desafinados — efecto vocal etéreo
      4. Melody arpeggio: nota aguda que sube y baja por el acorde
      5. Breath noise suave
      6. ADSR por bloque
      7. LFO de amplitud (movimiento orgánico)
      8. Reverb de Schroeder
      9. Fade global
     10. LFO chorus (L/R independiente) — calor de sala
    """
    sr = 44100
    total_samples = sr * duracion_segundos
    block_sec = 8   # cambiar acorde cada 8 seg (progresión de 4 acordes = 32s ciclo)
    block_samples = sr * block_sec

    chords = _MOOD_CHORDS.get(mood, _MOOD_CHORDS["Paz profunda"])

    path = os.path.join(output_dir, "musica_ambient.wav")

    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)

        samples_written = 0
        chord_idx = 0
        time_offset = 0.0

        while samples_written < total_samples:
            n = min(block_samples, total_samples - samples_written)
            t = np.linspace(time_offset, time_offset + n / sr, n,
                            endpoint=False).astype(np.float32)
            block_t = t - t[0]  # tiempo local del bloque (para envolventes)

            freqs = chords[chord_idx % len(chords)]

            # ── 1. PIANO: acorde arpegiado suavemente ───────────────
            piano = np.zeros(n, dtype=np.float32)
            piano_amp = 0.18
            for i, freq in enumerate(freqs):
                # Pequeño offset de ataque por voz (arpeggio de entrada)
                note_offset = int(i * 0.08 * sr)  # 80ms entre notas
                if note_offset < n:
                    t_note = block_t[note_offset:]
                    t_abs = t[note_offset:]
                    note = _piano_note(t_note, freq, sr, amp=piano_amp / (i + 1) ** 0.5)
                    piano[note_offset:] += note

            # ── 2. CUERDAS: pad sostenido orquestal ─────────────────
            strings = np.zeros(n, dtype=np.float32)
            strings_amp = 0.22
            for i, freq in enumerate(freqs):
                note_amp = strings_amp / (i + 1) ** 0.6
                strings += _strings_note(t, freq, amp=note_amp)

            # ── 3. CORO/PAD vocal: etéreo ────────────────────────────
            choir = np.zeros(n, dtype=np.float32)
            choir_amp = 0.15
            for i, freq in enumerate(freqs):
                note_amp = choir_amp / (i + 1) ** 0.8
                choir += _choir_note(t, freq, amp=note_amp)

            # ── 4. MELODY ARPEGGIO: una nota cada 2s, octava arriba ─
            melody = np.zeros(n, dtype=np.float32)
            arp_rate = 2.0  # segundos por nota
            arp_amp = 0.07
            for k in range(int(block_sec / arp_rate) + 1):
                note_start = int(k * arp_rate * sr)
                note_end = min(note_start + int(arp_rate * sr), n)
                if note_start >= n:
                    break
                note_idx = (chord_idx + k) % len(freqs)
                freq_arp = freqs[note_idx] * 2  # octava arriba
                t_arp = block_t[note_start:note_end]
                # Envolvente suave por nota (attack 200ms, release 800ms)
                env_arp = np.ones(len(t_arp))
                atk = min(int(0.2 * sr), len(t_arp))
                rel = min(int(0.8 * sr), len(t_arp))
                if atk > 0:
                    env_arp[:atk] = np.linspace(0, 1, atk)
                if rel > 0:
                    env_arp[-rel:] *= np.linspace(1, 0, rel)
                melody[note_start:note_end] += arp_amp * np.sin(
                    2 * math.pi * freq_arp * t_arp
                ) * env_arp

            # ── 5. BREATH noise ──────────────────────────────────────
            noise = np.random.randn(n).astype(np.float32) * 0.012
            kernel = np.ones(128, dtype=np.float32) / 128
            noise = np.convolve(noise, kernel, mode='same')

            # ── Mezcla de capas ──────────────────────────────────────
            pad = piano + strings + choir + melody + noise

            # ── 6. ADSR por bloque ───────────────────────────────────
            env = _adsr_envelope(n, sr, attack=1.5, decay=1.0, sustain=0.80, release=2.5)
            pad *= env

            # ── 7. LFO de amplitud (movimiento orgánico) ─────────────
            lfo_rate = 0.06 + random.uniform(-0.01, 0.01)
            lfo = 1.0 + 0.07 * np.sin(2 * math.pi * lfo_rate * t)
            pad *= lfo

            # ── 8. Reverb ────────────────────────────────────────────
            pad = _reverb(pad, sr, room_size=0.60, damping=0.40)

            # ── 9. Fade in / out global ──────────────────────────────
            if samples_written == 0:
                fi = min(sr * 4, n)
                pad[:fi] *= np.linspace(0, 1, fi)
            remaining = total_samples - samples_written
            if remaining <= sr * 5:
                fo = min(sr * 5, n)
                pad[-fo:] *= np.linspace(1, 0, fo)

            # ── Normalizar ───────────────────────────────────────────
            peak = np.max(np.abs(pad))
            if peak > 0:
                pad = pad / peak * 0.70

            # ── 10. LFO CHORUS: calor de sala ────────────────────────
            left, right = _chorus(pad, sr, rate_l=0.43, rate_r=0.57, depth_ms=3.5)

            # ── Escribir WAV ─────────────────────────────────────────
            left_16 = (np.clip(left, -1, 1) * 32767).astype(np.int16)
            right_16 = (np.clip(right, -1, 1) * 32767).astype(np.int16)
            stereo = np.empty(n * 2, dtype=np.int16)
            stereo[0::2] = left_16
            stereo[1::2] = right_16
            wav_file.writeframes(stereo.tobytes())

            samples_written += n
            time_offset += n / sr
            chord_idx += 1


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
