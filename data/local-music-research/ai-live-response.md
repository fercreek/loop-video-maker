# AI Live Research — Local Music Generation (CPU, no GPU)

- **Fuente:** Perplexity AI (Search mode, free plan) — live web search
- **URL del hilo:** https://www.perplexity.ai/search/045c8717-a604-43e1-bb6d-7a42a1d25470
- **Método:** Chrome MCP (Claude in Chrome) — navegación + query en vivo
- **Modelo:** Perplexity default (Search mode) — "Completed 5 steps", 39 fuentes citadas
- **Fecha:** 2026-06-22
- **Pregunta enviada:** Best 100% LOCAL, free, offline options to generate high-quality instrumental background music (calm pads, worship piano, ambient, sleep) for YouTube devotional videos on a 2019 Intel Core i7-9750H MacBook Pro, 16GB RAM, NO GPU (no CUDA, no Apple Silicon/MLX). Compare local neural models on CPU (MusicGen audiocraft CPU, musicgen.cpp quantized, AudioLDM2, Stable Audio Open) with real CPU generation times; algorithmic/synth tools (SuperCollider, Sonic Pi, FluidSynth + soundfonts); and royalty-free libraries (YouTube Audio Library, Pixabay). For each: runs well on Intel CPU without GPU? time per minute of audio, quality, YouTube monetization licensing safety. Give a prioritized recommendation with a comparison table.

---

## Respuesta completa (Perplexity, verbatim)

### Direct Answer: What Actually Works Well on Your Intel CPU

- **Top recommendation:** YouTube Audio Library + Pixabay (royalty-free libraries) — fastest, guaranteed monetization-safe, zero CPU load.
- **Best local AI option:** AudioLDM2 (quantized FP16) — runs on CPU, ~30–90 sec per 10 sec audio, good ambient/pad quality.
- **Algorithmic/synth:** SuperCollider + FluidSynth + high-quality piano soundfont — real-time, unlimited, perfect for worship piano.
- Neural models (MusicGen audiocraft CPU, musicgen.cpp quantized, Stable Audio Open) are **impractically slow** on your Intel CPU without GPU (10–30 min per minute of audio).

### Comparison Table: All Options Ranked

| Option | Runs on Intel CPU (no GPU)? | Time per 1 min audio | Quality (pads/piano/ambient/sleep) | YouTube Monetization Safe? | License Type |
|---|---|---|---|---|---|
| YouTube Audio Library | ✅ (not needed) | 0 sec (download) | ⭐⭐⭐⭐ (curated calm/worship) | ✅ 100% guaranteed | Royalty-free, copyright-safe |
| Pixabay Music | ✅ (not needed) | 0 sec (download) | ⭐⭐⭐⭐ (ambient/pads/sleep) | ✅ Yes (CC0, no attribution) | CC0 public domain |
| SuperCollider + FluidSynth + SoundFont | ✅ Yes, real-time | ~0 sec (real-time) | ⭐⭐⭐⭐⭐ (custom piano/pads) | ✅ Yes (you create it) | You own 100% |
| AudioLDM2 (quantized FP16) | ✅ Yes | ~3–9 min | ⭐⭐⭐⭐ (ambient/pads) | ✅ Yes (you generate) | Apache-2.0 weights |
| MusicGen (audiocraft CPU) | ⚠️ Yes, but slow | ~15–30 min | ⭐⭐⭐ (instrumental only) | ⚠️ Non-commercial license | Non-commercial |
| musicgen.cpp quantized | ⚠️ Yes, marginally faster | ~10–20 min | ⭐⭐⭐ | ⚠️ Non-commercial | Non-commercial |
| Stable Audio Open 1.0 | ⚠️ Yes, but slow | ~8–15 min | ⭐⭐⭐⭐ (stereo 44.1kHz) | ⚠️ Non-commercial license | Community License (non-comm.) |
| Sonic Pi | ✅ Yes (Ruby, CPU) | ~0 sec (real-time) | ⭐⭐⭐ (simple synths) | ✅ Yes (you create) | You own 100% |

**Key facts from benchmarks (source: danmackinlay):**
- Stable Audio Open: 47 sec audio in ~47 sec on GPU; CPU is 3–5× slower.
- AudioGen/MusicGen: ~10–30 sec on GPU; CPU is 10–15× slower.
- AudioLDM2: ~10 sec native on GPU; CPU ~30–90 sec for 10 sec audio.

---

### Detailed Breakdown by Category

#### 1. Royalty-Free Libraries (Best for Your Use Case)

| Metric | YouTube Audio Library | Pixabay Music |
|---|---|---|
| CPU requirement | None (download) | None (download) |
| Time to get music | Instant | Instant |
| Quality for devotional | ⭐⭐⭐⭐ (worship, calm, ambient) | ⭐⭐⭐⭐ (sleep, pads, ambient) |
| Monetization safety | ✅ 100% guaranteed by YouTube | ✅ CC0 (no claims) |
| Attribution required | Some tracks yes, most no | No (CC0) |
| Search filters | Genre: "Calm", "Ambient"; Instrument: "Piano" | Mood: "Calm", "Peaceful"; Category: "Ambient" |

**Why this is #1 for you:**
- Zero CPU load (your i7-9750H has no GPU)
- Guaranteed no copyright claims on monetized YouTube videos
- Instant download vs. hours of AI generation
- Curated worship/calm/ambient tracks exist

**How to use:**
1. Go to YouTube Studio → Audio Library
2. Filter: Genre = "Calm" / "Ambient", Instrument = "Piano", Mood = "Peaceful"
3. Download instrumental tracks (check "Attribution required" column)

#### 2. Algorithmic/Synth Tools (Best for Custom Worship Piano)

**SuperCollider + FluidSynth + SoundFont (Top Pick)**

| Aspect | Details |
|---|---|
| Runs on Intel CPU? | ✅ Yes, real-time, low CPU usage |
| Time per 1 min audio | ~0 sec (real-time playback) |
| Quality | ⭐⭐⭐⭐⭐ with high-quality soundfont (e.g., "Great Piano", "FluidR3_GM") |
| Monetization | ✅ You create it → 100% owned, no claims |
| License | Free (SuperCollider: BSD, FluidSynth: GPL) |
| macOS setup | `brew install supercollider fluidsynth` + download .sf2 soundfont |

Why SuperCollider + FluidSynth:
- Wavetable synthesis is low CPU usage and produces rich sounds
- Perfect for worship piano: load a piano SoundFont, play MIDI or code sequences
- Real-time generation (no waiting for AI)
- Unlimited custom tracks, no licensing issues

Basic workflow:
```
// SuperCollider piano example
(
SynthDef(\piano, {
|out, amp = 0.5|
var sig = Piano::note(amp);
Out.ar(out, sig);
});
)
```
Then use FluidSynth with a SoundFont:
```bash
fluidsynth -a alsa -m alsa_seq /path/to/FluidR3_GM.sf2
```
> Nota: el comando usa `-a alsa` (Linux). En macOS el driver de audio es `coreaudio` (`-a coreaudio`). Perplexity copió el ejemplo de Linux.

**Sonic Pi (Alternative)**
- Ruby-based, runs on CPU, real-time
- Simpler but less professional sound than SuperCollider
- Good for learning music coding

#### 3. Local Neural AI Models (CPU Reality Check)

**AudioLDM2 (Best Neural Option for CPU)**

| Metric | Value |
|---|---|
| CPU-only? | ✅ Yes |
| Time per 10 sec audio | ~30–90 sec on CPU |
| Time per 1 min audio | ~3–9 min |
| Quality | ⭐⭐⭐⭐ (ambient, pads, 48kHz checkpoint) |
| License | Apache-2.0 (commercial OK) |
| macOS setup | Use `haoheliu/AudioLDM2` + OpenVINO for Intel CPU |

Why AudioLDM2 is best neural option:
- Latent diffusion = faster than token-based models
- Supports both music and SFX
- Apache-2.0 = commercial use allowed

**MusicGen (audiocraft CPU) & musicgen.cpp (Not Recommended)**

| Metric | Value |
|---|---|
| CPU-only? | ⚠️ Yes, but very slow |
| Time per 30 sec audio | ~150–300 sec on CPU (5–10× GPU) |
| Time per 1 min audio | ~15–30 min |
| Quality | ⭐⭐⭐ (32kHz, instrumental only) |
| License | ⚠️ Non-commercial |
| Monetization risk | ⚠️ Yes (non-commercial license) |

Problem: Non-commercial license = can't use on monetized YouTube.

**Stable Audio Open 1.0 (Not Recommended)**

| Metric | Value |
|---|---|
| CPU-only? | ⚠️ Yes, but slow |
| Time per 47 sec audio | ~47 sec on GPU; CPU ~3–5× slower ≈ 150–250 sec |
| Time per 1 min audio | ~8–15 min |
| Quality | ⭐⭐⭐⭐ (44.1kHz stereo) |
| License | ⚠️ Stability AI Community License (non-commercial) |
| Monetization risk | ⚠️ Yes (non-commercial) |

Problem: Non-commercial license blocks YouTube monetization.

---

### Prioritized Recommendation

For Your Exact Use Case (YouTube Devotional Videos, Intel CPU, No GPU):

| Priority | Option | Why |
|---|---|---|
| 1 | YouTube Audio Library | Instant, guaranteed monetization-safe, curated calm/worship tracks |
| 2 | Pixabay Music | Instant, CC0 (no attribution), great ambient/sleep/pads |
| 3 | SuperCollider + FluidSynth + Piano SoundFont | Custom worship piano, real-time, 100% owned, low CPU |
| 4 | AudioLDM2 (quantized) | If you must use AI: best CPU neural, Apache-2.0 (commercial OK) |
| Avoid | MusicGen, musicgen.cpp, Stable Audio Open | Non-commercial licenses + impractically slow on CPU |

**Quick Setup Guide (macOS):**

For YouTube Audio Library:
1. Open YouTube Studio → Audio Library
2. Search: "worship piano", "calm pads", "ambient sleep"
3. Filter: Instrument = Piano, Genre = Calm/Ambient, Duration = 2–5 min
4. Download (check attribution column)

For SuperCollider + FluidSynth:
```bash
# Install
brew install supercollider fluidsynth

# Download piano soundfont (example)
# (la URL que dio Perplexity está rota — buscar FluidR3_GM.sf2 o un .sf2 de piano de buena calidad)

# Play MIDI with piano
fluidsynth -a coreaudio ~/Sounds/FluidR3_GM.sf2
```

For AudioLDM2 (if you want AI):
```bash
# Use OpenVINO for Intel CPU acceleration
pip install openvino-dev torch
# Load haoheliu/AudioLDM2 with OpenVINO backend
```

**Bottom line (verbatim):** Use YouTube Audio Library + Pixabay for 90% of your needs (instant, safe). Use SuperCollider + FluidSynth for custom worship piano when you need something specific. Avoid CPU neural models unless you're okay with 10–30 min per track and verify license terms.

---

### Follow-up questions sugeridas por Perplexity
- Local AI music on an Intel Mac: benchmark test of generation speeds for MusicGen vs ACE-Step on Core i7 CPU vs integrated GPU
- Build a 'Prompt-to-Audio' local workflow (Stability Matrix) chaining mood-based presets for worship/ambient
- Best high-quality piano soundfonts for FluidSynth
- How to set up SuperCollider for real-time MIDI sequencing
- Step-by-step guide to installing AudioLDM2 on macOS Intel CPU

### Fuentes citadas por Perplexity (39 total; principales)
- support.google.com (YouTube Audio Library help)
- youtube.com (Audio Library / monetization)
- danmackinlay (blog) — benchmarks de tiempos CPU vs GPU para MusicGen/AudioLDM2/Stable Audio Open
- github.com (FluidSynth, SuperCollider, Sonic Pi)
- openvino (AudioLDM2 + OpenVINO en Intel CPU)
- wiki.archlinux (FluidSynth setup)

### Notas / caveats del analista (venom)
- Los tiempos de generación neural vienen de un solo blog (danmackinlay) — son aproximaciones, no benchmarks medidos en este equipo exacto. Verificar antes de comprometer pipeline.
- Perplexity copió 2 comandos de Linux (`-a alsa`); en macOS Intel usar `-a coreaudio`. La URL del soundfont en el quick-setup está rota.
- Mencionó ACE-Step en los follow-ups como alternativa no cubierta en la query original — posible candidato a investigar (modelo de música más reciente).
- El punto fuerte y consistente: para video devocional monetizado, librerías royalty-free (YT Audio Library + Pixabay CC0) ganan en velocidad + seguridad de licencia; los modelos neural pesados (MusicGen/Stable Audio Open) tienen DOBLE bloqueo: lentos en CPU + licencia non-commercial.
