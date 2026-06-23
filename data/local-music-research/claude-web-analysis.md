# Música instrumental de fondo 100% LOCAL para videos devocionales — Análisis técnico

**Fecha:** 2026-06-22
**Autor:** venom (Claude web research)
**Hardware objetivo:** MacBook Pro 2019, Intel Core i7-9750H (6 cores / 12 threads, ~2.6–4.5 GHz), 16 GB RAM, **SIN GPU dedicada** (Intel UHD 630 integrada, sin CUDA, sin MLX/Apple Silicon).
**Caso de uso:** música de fondo para devocionales YouTube (oración / sleep / historias bíblicas) — pads calmados, piano worship, ambient, salmos.
**Meta crítica:** entrar al **YouTube Partner Program** → la salida tiene que ser **monetizable sin claims de Content ID ni problemas de licencia.**

---

## TL;DR — veredicto rápido

| Categoría | Veredicto para TU hardware | Riesgo licencia/monetización |
|---|---|---|
| **1. Modelos neuronales en CPU** | ❌ **Inviable en producción.** ~9 min de CPU por **10 s** de audio (≈54 min por minuto). Y los modelos buenos (MusicGen, AudioLDM2) son **CC-BY-NC = NO monetizable.** | 🔴 Alto |
| **2. Generación algorítmica (SuperCollider/Sonic Pi/FluidSynth)** | ✅ **La mejor opción.** Corre en tiempo real o más rápido en tu CPU, RAM mínima, calidad alta para pads/drones/piano. | 🟢 Cero (tú generas el audio) |
| **3. Sample-based royalty-free** | ✅ **Camino más rápido HOY.** Pero solo **YouTube Audio Library** es 100% seguro para monetizar. Pixabay/FMA/ccMixter = riesgo de Content ID. | 🟡 Variable (verde solo YT Audio Library) |

**Recomendación:** Sample-based (YouTube Audio Library) como base inmediata + **FluidSynth/Sonic Pi/SuperCollider** para generar pads/piano propios infinitos y 100% tuyos. Los modelos neuronales NO en este equipo.

---

## CATEGORÍA 1 — Modelos neuronales locales en CPU Intel

### Resumen de viabilidad

El problema no es uno, son **dos muros simultáneos** en tu equipo:

1. **Velocidad:** estos modelos son autoregresivos o de difusión, diseñados para GPU. En CPU Intel de 6 cores son brutalmente lentos.
2. **Licencia:** los modelos de mejor calidad (MusicGen, AudioLDM2) están bajo **CC-BY-NC 4.0** — la salida **no se puede monetizar** sin ambigüedad legal. Esto los descarta para YPP independientemente de la velocidad.

### Tabla comparativa

| Modelo | ¿Corre sin GPU? | Tiempo REAL en CPU i7 6-core | RAM | Calidad (pads/ambient) | Licencia MODELO | Salida monetizable YT |
|---|---|---|---|---|---|---|
| **MusicGen small (audiocraft)** | Sí (torch CPU) | **~9 min por 10 s de audio** (≈54 min/min); máx 30 s por gen | ~4 GB modelo + overhead | Media-alta; bueno para texturas | **CC-BY-NC 4.0** | 🔴 **NO** (no-comercial) |
| **MusicGen medium/large** | Técnicamente sí | Inviable (varias horas) | medium ~16 GB recomendado | Alta | CC-BY-NC 4.0 | 🔴 NO |
| **musicgen.cpp / ggml port** | **No existe un port maduro** | N/A | N/A | N/A | (heredaría CC-BY-NC) | 🔴 NO |
| **AudioLDM2** | Sí (difusión, CPU offload) | Muy lento en CPU (difusión multi-step) | **~20 GB RAM para CPU** → **NO cabe en 16 GB** | Alta para SFX/ambient | **CC-BY-NC-SA 4.0** | 🔴 **NO** (no-comercial) |
| **Stable Audio Open 1.0** | Sí | Lento en CPU (difusión); optimizable con OpenVINO/IPEX ~2x pero sigue lejos de RT | ~8-12 GB | Alta (ambient/texturas) | Stability Community License (comercial <$1M rev) | 🟡 **SÍ con registro** (ver nota) |
| **MAGNeT (audiocraft)** | Sí | ~7x más rápido que MusicGen en GPU; en CPU sigue lento pero el menos malo. small genera 10 s en ~4 s **en GPU** | small ~1.3 GB | Media (menor que MusicGen) | **CC-BY-NC 4.0** | 🔴 NO |
| **ACE-Step 1.5** | Sí (soporta Apple CPU / Intel XPU) | **CPU: 30+ min por track** | <4 GB VRAM en GPU; CPU usa RAM | Muy alta (entre Suno v4.5 y v5) | Código Apache/MIT; **pesos = StepFun propietario** (verificar) | 🟡 Verificar pesos |

### Detalle por modelo

**MusicGen (Meta/audiocraft)** — El número duro: una prueba documentada reporta **~9 minutos de CPU para generar 10 segundos** de audio, vs 35 s en una GPU T4. Eso es un factor real-time de ~54x más lento que tiempo real. Para un video sleep de 1 hora necesitarías ~54 horas de cómputo (y MusicGen solo genera 30 s por pasada por sus positional embeddings sinusoidales, así que tendrías que encadenar decenas de generaciones). **Los pesos son CC-BY-NC 4.0** → monetización en YouTube es legalmente ambigua/riesgosa (la mayoría interpreta "monetizado = comercial = prohibido"). **Doble descalificación.**
- Fuente velocidad: https://www.pragnakalp.com/generate-music-using-metas-musicgen-on-colab/
- Fuente licencia: https://huggingface.co/facebook/musicgen-large · https://news.ycombinator.com/item?id=36972893
- Setup CPU-only: https://github.com/facebookresearch/audiocraft/issues/599

**musicgen.cpp / ggml** — **No existe un port C++/ggml maduro de MusicGen.** La comunidad lo ha pedido (issues en llama.cpp) pero no hay implementación usable. Lo más cercano en el mundo ggml es **acestep.cpp** (port C++17 de ACE-Step 1.5 con GGML, corre en CPU). Pero aunque exista el binario, ACE-Step en CPU sigue siendo 30+ min por track.
- https://github.com/ServeurpersoCom/acestep.cpp
- https://github.com/ggml-org/llama.cpp/issues/11467

**AudioLDM2** — **Requiere ~20 GB de RAM para inferencia en CPU. Tu equipo tiene 16 GB → no cabe** sin swap agresivo (que lo hace aún más lento). Y es **CC-BY-NC-SA 4.0**, no-comercial. Descartado por RAM y por licencia.
- RAM: https://github.com/haoheliu/AudioLDM2/blob/main/README.md
- Licencia: https://huggingface.co/cvssp/audioldm2-music

**Stable Audio Open 1.0** — **El único modelo neuronal con licencia potencialmente monetizable.** La Stability AI Community License permite uso comercial si tu ingreso anual es **< $1,000,000 USD** (cumples), y **"You own any outputs generated"**. Pero requiere **registro** en stability.ai/community-license. Nota importante: el modelo *open* es distinto de la plataforma *Stable Audio* de pago — confusión común. En CPU es lento (difusión multi-step); OpenVINO/IPEX dan ~2x pero sigue muy por debajo de tiempo real en tu i7. **Si insistieras en un modelo neuronal, este es el único defendible legalmente — pero la velocidad lo hace poco práctico aquí.**
- Licencia: https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md · https://stability.ai/license

**MAGNeT** — Arquitectura no-autoregresiva, **~7x más rápido que MusicGen** (en GPU), genera 10 s en ~4 s en GPU. En CPU es el menos malo de los audiocraft, pero la calidad es **inferior** a MusicGen y es **CC-BY-NC 4.0** → no monetizable. Descartado por licencia.
- https://facebookresearch.github.io/audiocraft/docs/MAGNET.html · https://www.maginative.com/article/meta-unveils-magnet-a-breakthrough-model-that-generates-studio-quality-audio-7x-faster/

**ACE-Step 1.5** — El modelo *open* más fuerte de 2026 (SongEval 8.09, supera a Suno v5 según su paper). Soporta Mac/AMD/Intel/CUDA incluyendo Apple CPU. Pero: **CPU = 30+ minutos por track**, y los **pesos usan licencia propietaria StepFun** (el código es Apache/MIT) — hay que verificar términos de monetización en su HuggingFace antes de usar comercialmente. Genial en GPU, inútil en tu equipo.
- https://github.com/ACE-Step/ACE-Step-1.5 · https://studio.aifilms.ai/blog/ace-step-1-5-music-generation-open-source

### Aceleración Intel (OpenVINO / IPEX)

OpenVINO e Intel PyTorch Extension (IPEX, usa AVX) pueden dar **~2-3x de speedup** en CPU Intel convirtiendo a INT8 / formato OpenVINO. Pero 2-3x sobre "54x más lento que tiempo real" sigue siendo ~20x más lento que tiempo real. **No cierra la brecha** para producción de música de horas.
- https://github.com/rupeshs/fastsdcpu · https://intel.com/content/www/us/en/artificial-intelligence/posts/cpu-inference-performance-boost-openvino.html

### Veredicto Categoría 1

🔴 **Descartar para producción en este equipo.** Doble problema: (a) velocidad inviable (minutos-a-decenas-de-minutos por unos segundos de audio en CPU), (b) los modelos de mejor calidad son CC-BY-NC = no monetizables. El único con licencia limpia (Stable Audio Open, comercial <$1M) es demasiado lento en CPU sin GPU. Si algún día consigues GPU/Apple Silicon, **Stable Audio Open** (licencia limpia) o **ACE-Step** (verificar pesos) serían los candidatos.

---

## CATEGORÍA 2 — Generación algorítmica / sintética local ligera

**Esta es la ganadora técnica para tu hardware y tu caso de uso.** Pads calmados, drones, piano worship y ambient son *exactamente* el tipo de música que el código generativo produce excelente, en tiempo real, en CPU, con RAM mínima — y la salida es **100% tuya** (cero riesgo de licencia/Content ID).

### Tabla comparativa

| Herramienta | Corre en tu CPU | Calidad pads/ambient | Esfuerzo setup | Esfuerzo por pieza | Salida monetizable |
|---|---|---|---|---|---|
| **FluidSynth + soundfonts (.sf2)** | ✅ Trivial (CLI, casi sin CPU) | Alta para piano/orquesta/coro (depende del sf2) | Bajo (brew install) | Bajo (necesitas MIDI) | 🟢 Sí (cuida licencia del sf2) |
| **Sonic Pi** | ✅ Tiempo real, ligero | Alta para drones/pads/ambient | Muy bajo (app + tutorial built-in) | Medio (escribes código musical) | 🟢 Sí (100% tuyo) |
| **SuperCollider** | ✅ Tiempo real (limita # de synths) | **La más alta** para drones/texturas/síntesis | Medio-alto (curva de aprendizaje) | Medio | 🟢 Sí (100% tuyo) |
| **Strudel (browser) / TidalCycles** | ✅ (Web Audio API, en navegador) | Alta para pads/ambient/IDM | Bajo (strudel.cc, sin instalar) | Medio | 🟢 Sí (100% tuyo) |
| **Síntesis por código (NumPy/Python)** | ✅ Genera offline rápido | Media (tú construyes todo) | Alto (programas la síntesis) | Alto | 🟢 Sí (100% tuyo) |

### Detalle por herramienta

**FluidSynth + SoundFonts — el más práctico para PIANO WORSHIP / orquesta / coro.** Es un sintetizador SoundFont2 por línea de comandos. Le das un .sf2 (piano, strings, pads, coro) + un archivo MIDI y renderiza audio. Consumo de CPU casi nulo, rinde más rápido que tiempo real. Comando para renderizar a archivo:
```
fluidsynth -nli -r 48000 -o synth.cpu-cores=6 -T oga -F salida.ogg FluidR3_GM.sf2 entrada.mid
```
El flujo ideal: generas progresiones de acordes worship en MIDI (a mano, con un generador algorítmico simple, o con plantillas) → FluidSynth las convierte a audio con un sf2 de piano/pad de alta calidad. **Necesitas: (1) buen soundfont, (2) MIDI.** Soundfonts gratis: Soundfonts 4U, Producers Buzz (top 18 pianos), archive.org. **Ojo con la licencia de cada .sf2** — la mayoría son CC o royalty-free, pero verifica antes de monetizar.
- https://www.fluidsynth.org/ · https://wiki.archlinux.org/title/FluidSynth
- Soundfonts: https://sites.google.com/site/soundfonts4u/ · https://www.producersbuzz.com/downloads/download-free-soundfonts-sf2/top-18-free-piano-soundfonts-sf2/

**Sonic Pi — el más accesible para AMBIENT / SLEEP / drones.** App gratis (Win/Mac/RPi) con tutorial built-in excelente. Trae samples ambient (`:ambi_lunar_land`, `:ambi_drone`) y synths que generas con código. Patrón típico para sleep/ambient: 3 loops concurrentes — un LFO lento modulando reverb, una capa de drones cada 12-24 beats, y texturas de fondo. Tiempo real, ligero. Puedes grabar la salida a WAV. **No necesitas saber programar mucho.** Ideal para producir horas de pad calmado generativo que nunca se repite igual.
- https://sonic-pi.net/ · https://sonic-pi.net/tutorial.html

**SuperCollider — la calidad técnica más alta para drones/texturas.** El motor de síntesis más poderoso de la lista. Hay infinidad de patches de ambient generativo (recreaciones de "Music for Airports" de Eno con 8 sinusoides meandering, drones de duración infinita, wavetable synthesis con armónicos). Curva de aprendizaje más alta que Sonic Pi. **Regla de performance clave:** libera los synths cuando terminan y pon un cap al número de synths activos, o congela la CPU. Para drones/pads infinitos de altísima calidad, es lo mejor.
- https://supercollider.github.io/ · https://sccode.org/tag/category/ambient · https://github.com/danielmkarlsson/a_loss_of_self (drone de duración infinita)

**Strudel / TidalCycles — pads en el navegador, sin instalar.** Strudel es el port JS de TidalCycles, corre en el navegador (strudel.cc) con Web Audio API. Hace "lush ambient pads", reverb, filtros, ritmos euclidianos. Cero instalación, cero riesgo de licencia. Bueno para prototipar texturas rápido. (TidalCycles "real" requiere SuperCollider de backend.)
- https://strudel.cc/ · https://tidalcycles.org/

**Síntesis por código (NumPy)** — Generar ondas/envolventes directamente en Python y escribir WAV. Máximo control, pero tú construyes toda la síntesis (osciladores, filtros, reverb) — mucho esfuerzo para igualar la calidad de SuperCollider/sf2. Útil solo para texturas muy específicas o pipelines automatizados. No es la primera opción.

### El truco "Music for Airports" para SLEEP de horas

Para devocionales de sleep, el patrón de Brian Eno es ideal y trivial de implementar local: **varios loops de distinta longitud que nunca coinciden** → produce horas de ambient que nunca se repite. Implementable en Sonic Pi o SuperCollider con pocas líneas. Genera 1 hora de pad único, 100% tuyo, en tiempo real.
- https://reverbmachine.com/blog/deconstructing-brian-eno-music-for-airports/

### Veredicto Categoría 2

🟢 **La mejor opción técnica para tu equipo y tu nicho.** Corre en tiempo real o más rápido en tu i7 sin GPU, RAM mínima, salida 100% tuya (cero Content ID, cero ambigüedad de licencia). Recomendación concreta:
- **Piano worship / orquesta / coro** → **FluidSynth + buen soundfont** (necesitas MIDI).
- **Ambient / sleep / drones / pads** → **Sonic Pi** (fácil) o **SuperCollider** (máxima calidad).
- Curva: Sonic Pi en una tarde; SuperCollider más, pero vale para drones premium.

---

## CATEGORÍA 3 — Sample-based local (royalty-free) — **CRÍTICO para monetización**

El camino más rápido para tener audio HOY. **Pero la licencia es donde te juegas el YPP.** No todas las fuentes "gratis" son seguras para monetizar. Esta es la jerarquía de riesgo:

### Tabla comparativa de SEGURIDAD para monetización YouTube

| Fuente | Licencia | ¿Content ID claims? | ¿Seguro para monetizar YPP? | Atribución |
|---|---|---|---|---|
| **YouTube Audio Library** | Pre-cleared por YouTube | 🟢 **Nunca** (YT garantiza) | ✅ **100% SÍ — la más segura** | A veces (CC tracks) |
| **Pixabay Music** | Pixabay License (comercial OK) | 🟡 **Puede pasar** (si el autor registró el track en Content ID) | 🟡 Sí, pero puede requerir disputar el claim | No requerida |
| **Free Music Archive (FMA)** | Varía por track (CC BY / CC BY-NC / etc.) | 🟡 Algunos autores usan Content ID | 🟡 Solo tracks **CC BY o CC0**; NUNCA CC-BY-NC | Sí (CC BY) |
| **ccMixter** | Varía (CC BY / CC BY-NC) | 🟡 Posible | 🟡 Solo **CC BY**; NUNCA CC-BY-NC | Sí |

### Reglas de oro de licencia (no negociables para YPP)

1. **CC-BY-NC (NonCommercial) = PROHIBIDO si monetizas.** YouTube monetizado se considera uso comercial. Esto descarta una gran parte de FMA y ccMixter.
2. **CC BY (solo atribución) = OK para monetizar**, con crédito completo en la descripción (nombre track, artista, URL fuente, tipo de licencia + link).
3. **Atribución NO reemplaza permiso/licencia.** Puedes acreditar perfecto y aún recibir un claim válido si el track nunca estuvo licenciado para ti.
4. **Un Content ID claim NO es un strike** (no penaliza el canal), pero **mientras está activo no monetizas ese video** (los ads van al reclamante). Se puede disputar (Pixabay da un certificado .txt como prueba), pero tarda hasta 30 días.

### La opción a prueba de balas: YouTube Audio Library

**Solo la YouTube Audio Library garantiza que NO habrá claim de Content ID y que puedes monetizar** estando en el YPP. Cada track está pre-clareado por YouTube. Es gratis y tiene mucho material ambient/piano/calmado apropiado para devocionales. **Caveat:** ese permiso es solo para YouTube — no puedes reusar el mismo track en TikTok/IG/proyectos de cliente sin verificar.
- https://support.google.com/youtube/answer/3376882

### Recombinación / crossfade de loops

Una vez tienes loops royalty-free seguros (ej. de YT Audio Library), puedes extender/variar localmente con crossfade y recombinación — **ffmpeg** o **pydub** (Python) hacen esto trivial en CPU: encadenar loops con fundidos cruzados para producir tracks largos de sleep sin costuras audibles. Esto es 100% local, rápido, y no cambia la licencia del audio fuente (sigue siendo seguro si la fuente lo era).

### Veredicto Categoría 3

🟡 **El camino más rápido HOY, pero la seguridad depende 100% de la fuente.**
- **Para monetizar sin riesgo → solo YouTube Audio Library.** Pre-clareada, cero Content ID, ideal arranque para YPP.
- **Pixabay** = comercial OK pero puede haber claims que tienes que disputar (molesto pero resoluble con su certificado).
- **FMA / ccMixter** = solo tracks **CC BY o CC0**, jamás CC-BY-NC. Riesgo de Content ID si el autor lo registró.
- Recombina loops con **ffmpeg/pydub** local para extender a horas.

---

## Síntesis final — pipeline recomendado para Versículos de Dios / devocionales

Dado tu hardware (Intel sin GPU) y tu meta (YPP / monetización limpia):

1. **AHORA (cero fricción):** YouTube Audio Library como fuente base de música calmada → monetización garantizada, cero Content ID. Extiende a duración de video con **ffmpeg/pydub** (crossfade de loops).

2. **CALIDAD PROPIA / DIFERENCIACIÓN (semanas):** Monta **FluidSynth + un buen soundfont de piano/pad** para piano worship, y **Sonic Pi** (o SuperCollider para drones premium) para ambient/sleep generativo infinito. Salida 100% tuya → cero riesgo de licencia, audio único que nadie más tiene, y corre perfecto en tu i7 sin GPU.

3. **NO uses modelos neuronales en este equipo.** MusicGen/AudioLDM2/MAGNeT son CC-BY-NC (no monetizables) y/o demasiado lentos (~9 min CPU por 10 s de audio; AudioLDM2 ni cabe en 16 GB). Stable Audio Open tiene licencia limpia (<$1M comercial) pero es impráctico en CPU. Reconsidéralos solo si consigues GPU o Apple Silicon.

---

## Fuentes

**Categoría 1 — Neuronales:**
- https://www.pragnakalp.com/generate-music-using-metas-musicgen-on-colab/ (CPU ~9 min / 10 s)
- https://facebookresearch.github.io/audiocraft/docs/MUSICGEN.html
- https://github.com/facebookresearch/audiocraft/issues/599 (setup CPU-only)
- https://huggingface.co/facebook/musicgen-large (licencia CC-BY-NC)
- https://news.ycombinator.com/item?id=36972893 (debate licencia)
- https://github.com/haoheliu/AudioLDM2/blob/main/README.md (~20 GB RAM CPU)
- https://huggingface.co/cvssp/audioldm2-music (CC-BY-NC-SA)
- https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md
- https://stability.ai/license (comercial <$1M)
- https://facebookresearch.github.io/audiocraft/docs/MAGNET.html
- https://www.maginative.com/article/meta-unveils-magnet-a-breakthrough-model-that-generates-studio-quality-audio-7x-faster/
- https://github.com/ACE-Step/ACE-Step-1.5 (CPU 30+ min/track)
- https://github.com/ServeurpersoCom/acestep.cpp (port C++/GGML)
- https://github.com/ggml-org/llama.cpp/issues/11467 (no hay musicgen.cpp)
- https://github.com/rupeshs/fastsdcpu (OpenVINO/IPEX ~2x CPU)

**Categoría 2 — Algorítmico:**
- https://www.fluidsynth.org/ · https://wiki.archlinux.org/title/FluidSynth
- https://sites.google.com/site/soundfonts4u/ · https://www.producersbuzz.com/downloads/download-free-soundfonts-sf2/top-18-free-piano-soundfonts-sf2/
- https://sonic-pi.net/ · https://sonic-pi.net/tutorial.html
- https://supercollider.github.io/ · https://sccode.org/tag/category/ambient
- https://github.com/danielmkarlsson/a_loss_of_self
- https://strudel.cc/ · https://tidalcycles.org/
- https://reverbmachine.com/blog/deconstructing-brian-eno-music-for-airports/

**Categoría 3 — Sample-based / licencias:**
- https://support.google.com/youtube/answer/3376882 (YT Audio Library — la segura)
- https://pixabay.com/blog/posts/how-to-clear-a-youtube-content-id-claim-with-a-pix-190/ (Pixabay claims)
- https://www.silvermansound.com/creative-commons-music-licensing-guide (CC BY vs CC-BY-NC)
- https://ccmixter.org/how-to-attribute-ccmixter-tracks
- https://freemusicarchive.org/faq/
- https://air.io/en/youtube-hacks/how-to-legally-use-music-without-losing-monetization
