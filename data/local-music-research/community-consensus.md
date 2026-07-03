# Música instrumental de fondo 100% LOCAL en Mac Intel sin GPU — Consenso de la comunidad

> **Research date:** 2026-06-22
> **Hardware objetivo:** MacBook Pro Intel i7-9750H, 16GB RAM, **sin GPU dedicada / sin CUDA / sin MPS** (Intel = sin aceleración Apple Silicon)
> **Caso de uso:** música de fondo para videos YouTube devocionales (ambient / sleep / worship / piano)
> **Fuentes:** Reddit (r/musicgen, r/LocalLLaMA, r/StableDiffusion, r/youtubers, r/NewTubers, r/ambientmusic, r/edmproduction, r/WeAreTheMusicMakers), Hacker News, GitHub issues/discussions (audiocraft, fluidsynth, llama.cpp), HuggingFace forums/discussions, foros SuperCollider (scsynth.org) y Sonic Pi (in-thread), foros Linux audio, blogs de creadores.
> **Método:** 3 agentes de investigación en paralelo (CPU AI feasibility · prácticas de creadores devocionales · herramientas algorítmicas). Solo opiniones reales de comunidad, NO PR oficial. Incluye críticas y abandono.

---

## TL;DR — El veredicto honesto

1. **MusicGen / AudioLDM2 / Stable Audio Open en CPU Intel sin GPU = inviable en la práctica.** Toda historia de éxito depende de NVIDIA GPU o de aceleración Apple Silicon (MPS/MLX) — que tu Mac Intel **NO tiene**. Intel es el peor caso documentado.
2. **Los creadores devocionales/sleep que monetizan limpio NO generan localmente con AI.** Usan composición original/comisionada o librerías royalty-free con safelist (Epidemic Sound / Artlist). AI cruda (Suno/Udio) es el blanco #1 de desmonetización desde julio 2025.
3. **Las herramientas algorítmicas locales (Sonic Pi / SuperCollider / FluidSynth) SÍ funcionan en CPU y SÍ pueden sonar a ambient real** — pero requieren trabajo (constrain randomness + reverb), no son quick win, y el piano de soundfont gratis tiene techo de calidad.

---

## 1. ¿La gente corre MusicGen / AudioLDM2 / Stable Audio Open en CPU Intel sin GPU de forma usable?

**Respuesta de la comunidad: NO en tu hardware. Es el peor caso.**

### Lo que reportan (con números reales)

- **Docs oficiales de audiocraft exigen GPU.** "In order to use MusicGen locally **you must have a GPU**." CPU-only no es soportado oficialmente. → https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md
- **El match más cercano a tu hardware (musicgen-small, CPU, 16GB RAM) básicamente FALLÓ.** Un usuario en HuggingFace forum con exactamente `facebook/musicgen-small` en CPU 16GB obtuvo shape errors, luego un .wav de "0 segundos", y cuando salió audio era un "crippled sounding 5 second file" que "sounds like something under water and high pitch, not a music." Veredicto del hilo: 16GB CPU-only enfrenta "substantial practical limitations." → https://discuss.huggingface.co/t/trying-to-run-facebook-musicgen-small-on-cpu-with-16gb-ram/134517
- **Mejor dato de tiempo (y es Apple Silicon, NO Intel):** En **M2 Max 32GB con MPS**, AudioGen tarda ~60s para generar 5s de audio y ~100s para 10s (~10–12x más lento que realtime). Ese es el número *acelerado*; Intel CPU-only sería peor, sin MPS. El mismo autor **no logró que MusicGen corriera en MPS para nada**. → https://blog.peddals.com/en/apple-mps-to-generate-audio-with-meta-audiogen/
- **AudioLDM2 en CPU:** el blog oficial dice que el modelo sin optimizar es "very slow: a 10 second audio sample takes upwards of 30 seconds to generate" — y los speedups de 10x que citan (half-precision, flash attention, torch.compile) **requieren GPU**, que tu Mac Intel no tiene. → https://huggingface.co/blog/audioldm2
- **Stable Audio Open en CPU literalmente se cuelga.** En MacBook Air M2 (y confirmado en Windows Intel i9), `generate_diffusion_cond` "gets stuck indefinitely" tras "several minutes." Ingeniero de Stability AI confirmó que "the VAE decoder is certainly the biggest bottleneck" y que "doesn't work efficiently on CPUs without optimization." → https://huggingface.co/stabilityai/stable-audio-open-small/discussions/1
- **Referencias GPU para escala (qué tan lejos está el CPU):** Stable Audio Open solo hace 8 steps/sec en una RTX-3090. Un CPU está órdenes de magnitud por debajo. → https://huggingface.co/stabilityai/stable-audio-open-1.0

### ¿Vale la pena o lo abandonan? (frustración real)

- **"The problem? Running it on a Mac means PyTorch on CPU, which is painfully slow."** — motivación literal de un dev para portar MusicGen fuera de CPU. Confirma "the original PyTorch on CPU is significantly slower." → https://medium.com/@andradeolivier/i-ported-musicgen-to-apple-silicon-generate-music-from-text-on-your-macbook-9eaf95992053
- **"official support is limited to NVIDIA GPUs or CPUs. macOS users are stuck with CPU-only execution. Frustrating, right?"** El autor de Peddals **abandonó** MusicGen en MPS ("I tried to make MusicGen work with MPS… but it didn't succeed"). → https://blog.peddals.com/en/apple-mps-to-generate-audio-with-meta-audiogen/

### Trucos (y trampas)

- **Float32, no float16, en CPU.** El fix más citado para que Stable Audio Open no se cuelgue: forzar float32 (los conv1d del decoder son catastróficamente lentos en float16 CPU). → https://huggingface.co/stabilityai/stable-audio-open-small/discussions/1
- **Cuantización NO ayuda en CPU/Mac — es MÁS lento.** bitsandbytes 8-bit en MusicGen corre "3-4x slower"; fp16 le gana. → https://huggingface.co/facebook/musicgen-large/discussions/8
- **NO existe un `musicgen.cpp` maduro.** A pesar del nombre, no hay port C++/ggml usado de MusicGen de Meta. Lo más cercano "music.cpp" es **acestep.cpp** (ACE-Step vía GGML, CPU/CUDA/Metal/Vulkan) — modelo distinto. MusicGen solo es feature-request abierto. → https://github.com/ServeurpersoCom/acestep.cpp · https://github.com/ggml-org/llama.cpp/issues/11467

### La distinción clave: Apple Silicon (MPS/MLX) vs Intel (tu peor caso)

**Cada camino usable se salta a Intel:**

- **El MusicGen rápido es MLX (solo Apple Silicon).** El port MLX hace musicgen-small **8s de audio en ~6.3s en M4 Max** — pero el repo **exige Mac con Apple Silicon (M1/M2/M3/M4)** y no menciona Intel. MLX literalmente no corre en tu i7. → https://medium.com/@andradeolivier/i-ported-musicgen-to-apple-silicon-generate-music-from-text-on-your-macbook-9eaf95992053
- **MPS = GPU de Apple Silicon.** No existe en Intel Macs.
- **Para Intel, todo termina en cores de CPU.** El thread del MusicGen Space solo ofrece `device='mps'` para M1 — sin opción de aceleración para Intel. → https://huggingface.co/spaces/facebook/MusicGen/discussions/3
- **Por qué Intel es uniquely bad:** sin CUDA (es Mac), sin MPS/Metal usable (eso maduró solo en Apple Silicon), y el i7-9750H es un chip móvil 6-core de 2019. Heredas el baseline lento que hasta los M-series huyen — sin la escotilla MLX/MPS que ellos usan.

**Conclusión §1:** Para i7-9750H/16GB/sin-GPU: MusicGen solo musicgen-small, muy lento, problemas frecuentes de calidad/RAM. AudioLDM2/Stable Audio se cuelgan o se arrastran. La respuesta pragmática de la comunidad: **cloud GPU (Colab/Replicate)** o aceptar runs lentos de modelo chico/clip corto. **No es producción viable en este Mac.**

---

## 2. ¿Qué usan los creadores devocionales/sleep/ambient EN LA PRÁCTICA para música segura de monetizar?

**No hay un "todos usan X." Se parte en 3 tiers, y el tier decide tu destino de monetización.**

- **Librerías royalty-free por suscripción (Epidemic Sound = default dominante de canales serios).** Epidemic posee 100% de su catálogo y hace **safelist de tu canal específico** — esto le dice a Content ID que tienes licencia válida y auto-suprime claims. Por eso es el pick de quien quiere monetizar limpio sin componer. Artlist igual. → https://www.epidemicsound.com/blog/avoid-copyright-claims-music-epidemic-sound-2/
- **Composición original/comisionada (los canales sleep top).** Los más grandes (ej. Yellow Brick Cinema) comisionan compositores + binaural beats / frecuencias Solfeggio / 8D / ASMR. Es el único camino que limpia 100% el bar de "reused/inauthentic content" Y evita Content ID (puedes registrar tus propios tracks). → https://videos.feedspot.com/sleep_music_youtube_channels/
- **Librerías gratis (YouTube Audio Library, Pixabay) — hobbyistas/principiantes, más riesgo a escala.** YT Audio Library es la única fuente que YouTube garantiza sin Content ID. Pixabay es gratis pero NO garantizada (ver §3). → https://www.foximusic.com/blog/youtube-content-id-for-music-guide-monetization/
- **AI (Suno/Udio) — creciendo rápido, riesgo máximo de monetización.** Viable para sleep/meditación SOLO si se curan fuerte con elementos humanos; dumps de AI cruda son el blanco #1 de enforcement. → https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/

**Consenso práctico:** Los creadores devocionales/sleep que monetizan aterrizan en **Epidemic/Artlist (licencia + safelist)** o **composición original**. "Royalty-free sacado de uploads random etiquetados free" es el error clásico que te rechaza del YPP. → https://www.tunepocket.com/make-money-youtube-sleep-videos/

---

## 3. Riesgos de monetización: AI-generada vs librerías royalty-free (Content ID, claims, licencias)

**Mecánica que casi nadie entiende:** Content ID es un match de huella de audio. NO verifica si tienes licencia. Un claim puede aparecer sobre música perfectamente licenciada. "Royalty-free" ≠ "invisible para YouTube." Un claim es *procedural, no punitivo* — si estás bien licenciado lo disputas con tu certificado y recuperas ingresos. → https://legismusic.com/is-royaltyfree-music-safe-for-monetised-youtube-channels

### AI music — el gran riesgo (y la política de julio 2025 que lo cambió todo)

- **Política YouTube explícita:** "fully AI-generated music (audio-only, unmodified) is ineligible for monetization and Content ID." Música AI pura ni siquiera se puede registrar para protegerse. → https://blog.genxnotes.com/en/can-you-get-youtube-content-id-on-suno-generated-ai-music/
- **Número duro / horror story:** **+40% de los canales de música AI pura han sido desmonetizados desde finales 2025** bajo la política renombrada "inauthentic content" (antes "repetitious content"). Perfil de enforcement = alta cadencia de uploads + títulos formulaicos + thumbnails casi idénticos + bajo watch time. → https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/
- **Riesgo de false claim:** Suno v4 / Udio pueden producir output que se parece a canciones con copyright en su training, disparando Content ID contra el track de *otro* — y la responsabilidad cae en TI, no en Suno. Su ToS te pasa el riesgo de copyright. → https://terms.law/ai-output-rights/suno/

### Royalty-free — ¿también dan claims? Sí, pero recuperables

- **Epidemic Sound** puede tirar un claim si tu canal aún no está safelisted, o en long-form donde YouTube detecta el track pero no confirma licencia. Con sub activa + safelist, se auto-limpian. → https://help.epidemicsound.com/hc/en-us/articles/26253712691730
- **Pixabay (gratis):** compositores registran sus tracks de Pixabay en Content ID, así que PUEDES recibir claim aunque sea gratis. No es strike, pero bloquea tu monetización hasta resolverlo. Gotcha real y común. → https://pixabay.com/blog/posts/how-to-clear-a-youtube-content-id-claim-with-a-pix-190/
- **YouTube Audio Library:** la única que YouTube garantiza sin claim — pero creadores reportan tracks antes "copyright-free" que después dispararon claims. Trata "safe" como "safest," no absoluto. → https://www.foximusic.com/blog/youtube-content-id-for-music-guide-monetization/

### Gotchas de licencia (lo que en secreto NO es seguro)

- **Suno/Udio tier GRATIS = sin derechos comerciales.** Disputar un claim sobre output free-tier es en sí una violación de copyright de tu lado. Necesitas plan **pagado** — y aun así sigue siendo ineligible para Content ID y propenso a desmonetización como "inauthentic" si no se cura. → https://dynamoi.com/learn/ai-music-distribution/suno-commercial-rights-explained
- **Lock-in de Epidemic (queja #1 de creadores):** Videos publicados *mientras estás suscrito + safelisted* quedan "cleared forever" aun tras cancelar. PERO cualquier video que publiques *después* de cancelar recibe claim y lo monetiza Epidemic. Efectivamente debes seguir pagando para seguir publicando — lock-in de costo recurrente para un canal sleep. → https://www.cchound.com/epidemic-sound/what-happens-to-my-youtube-videos-after-i-cancel-my-epidemic-sound-subscription/
- **"Royalty-free" de uploads random / compilaciones "no copyright" = trampa.** Top causa de false claims y rechazo de YPP. Solo confía en fuentes con certificado de licencia o safelist. → https://www.tunepocket.com/make-money-youtube-sleep-videos/
- **Documentación = la red de seguridad real:** guarda cada certificado, factura, recibo. Seguridad = lo que puedes probar, no lo que el algoritmo asume.

### Ranking de seguridad (mejor → peor) para monetizar

1. Composición original/comisionada (hasta la puedes reclamar tú)
2. Epidemic Sound / Artlist con canal safelisted + sub activa
3. YouTube Audio Library
4. Pixabay (gratis pero claimable; guarda certificados)
5. Suno/Udio pagado con curación humana fuerte + disclosure AI
6. ❌ AI free-tier, compilaciones "no copyright," rips "free" random de YT

### Long-form (1hr+) sleep/ambient a escala

Es el caso más difícil: la política "inauthentic / easily-replicable-at-scale" apunta directo a la naturaleza del género (un video de lluvia 10hrs es estructuralmente idéntico a otro). YouTube **no hace excepción de género**. → https://dynamoi.com/learn/youtube-music-promotion/ambient-music-channel-monetization-rules

Lo que sobrevive a escala:
- **Diferencia visualmente cada video** (footage original / animación custom). Visual de screensaver en loop + alto volumen diario = el perfil exacto de red-flag.
- **Composición original pesa más** que stock licenciado/compilado para pasar review. Añade binaural/Solfeggio/8D/ASMR/narración para hacer cada sesión distinta.
- **RPM realidad:** sleep/meditación/cinematic es nicho *high-value* ($3–$10 RPM) vs type-beat spam ($0.30–$1). El watch-time largo + audiencia US/EU vale más que si la música es AI o no. → https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/
- **AI long-form viable SOLO con curación:** AI pagado + visuales únicos + disclosure + metadata variada + pasar cada track por el Copyright checker antes de publicar.

---

## 4. ¿Recomiendan herramientas algorítmicas (SuperCollider / Sonic Pi / FluidSynth) para ambient calmado? ¿Calidad real?

**Veredicto consistente: SÍ son capaces de ambient/drone/piano agradable y evolutivo, corriendo local en CPU. PERO (a) los sonidos default son criticados como cheap/synthetic y debes reemplazarlos, (b) es rabbit hole real, no quick win, (c) para piano convincente los soundfonts gratis tienen techo.**

### ¿Buena calidad o obviamente sintético?

**Sí, recomendado para ambient — se considera sweet spot:**
- Ambient/cinematic/sin-percusión es *el* género que le queda al algoritmo, porque "true randomness is not compatible with structured beat/rhythm" — los drones y la evolución lenta esconden las costuras. → https://scsynth.org/t/generative-ambient/6828
- Una pieza ambient generativa en el foro SuperCollider sacó "Nice! Sounds great!" — hecha de "banks of LFOs, noise and envelope generators."
- Un usuario de Sonic Pi hizo una pieza Eno-style ("Waiting for the Next Tomorrow") con reverb/flanger/echo + samples de vinilo; otros la llamaron "a lovely meditative piece" / "I totally dig the vibe." Prueba concreta de que el output se lee como ambient real. → https://in-thread.sonic-pi.net/t/i-tried-to-make-a-kinda-brian-eno-stuff-ended-up-with-kinda-lofi-generative-ambiant-brian-eno-style-stuff/9168

**PERO la crítica "obviamente sintético/cheap" es real y apunta a los DEFAULTS:**
- El synth default de SuperCollider es descrito abiertamente como "a cheesy old piano sound" y "extremely unconvincing synthesizer" — hay guías solo para sobreescribirlo. Out-of-the-box SÍ suena barato; debes definir tus SynthDefs o cargar buenos samples. → https://madskjeldgaard.dk/how-to-change-the-default-synth-in-supercollider/
- Lo que separa "buen ambient" de "mecánico/aburrido" es **constreñir el randomness** — escalas modales, gates de probabilidad, LFOs lentos (ej. 0.02 Hz en reverb decay), loops en capas cada 12–24 beats. Random puro = académico/sin rumbo; random constreñido = intencional. → https://www.synthtopia.com/content/2019/04/24/twenty-techniques-for-generative-music-inspired-by-brian-eno/

### ¿Quick win o rabbit hole? (curva de aprendizaje)

- **Sonic Pi = el lado bajo de la piscina (lo más cercano a quick win).** Educativo, Ruby, feedback auditivo inmediato, buen tutorial; la gente saca sonidos "within a couple of hours." Dicen que hace music programming "much easier compared to Csound and SuperCollider." → https://sonic-pi.net/tutorial.html · https://dev.to/sublimemarch/today-i-learned-how-to-generate-music-with-sonic-pi-566g
  - Caveat: sigue habiendo curva de sintaxis + teoría; hasta la pieza Eno necesitó debugging e iteración. "Primer loop lindo en una tarde," "track generativo pulido toma más."
- **SuperCollider = el rabbit hole profundo.** Comunidad: "start with Sonic Pi… when you tire of its sounds, then look into SuperCollider." Csound/SuperCollider "really good but have a big learning curve." → https://www.saashub.com/compare-supercollider-vs-sonic-pi · https://opguides.info/music/software/livecoding/

**Veredicto:** Sonic Pi = un fin de semana a "loop ambient decente." SuperCollider/TidalCycles = semanas-meses. La *síntesis* es rápida; el *gusto/mezcla para evitar output estéril* es lo lento.

### FluidSynth + soundfont de piano — ¿worship/piano convincente?

**Los soundfonts gratis son "good enough for background," no "studio piano":**
- **FluidR3_GM** — "a legend in the open-source community," pro-quality GM/GS, bueno para "classical, jazz, general listening." Gratis y confiable. → https://miditoolbox.com/posts/best-free-general-midi-soundfonts-2026
- **Salamander Grand Piano** — gran upgrade sobre defaults, 16 velocity layers (versión full); hay un "C5 Lite" (~24.5 MB) que queda "very close to the original." → https://github.com/sfzinstruments/SalamanderGrandPiano · https://musical-artifacts.com/artifacts/483

**La crítica honesta — dónde se rompe el piano de soundfont:**
- Sin rodeos: "Soundfonts like Salamander Lite **sound like a toy** compared to quality VSTs like Pianoteq." → https://forum.loopypro.com/discussion/38764/app-auv3-with-the-best-piano-sounds/p2
- FluidSynth **no reproduce el ruido de release del pedal de sustain** (clave de realismo); LinuxSampler maneja eso mejor. → https://linuxmusicians.com/viewtopic.php?t=18829
- **Gotcha de reverb:** El reverb de FluidSynth "has no effect" frecuentemente porque los soundfonts comunes (incl. FluidR3_GM) no setean GEN_REVERBSEND/GEN_CHORUSSEND — así que el output crudo suena dry/dead. **Razón #1 de que FluidSynth piano suene "lifeless" out of the box.** Solución: añade reverb downstream (DAW/SC). → https://github.com/FluidSynth/fluidsynth/discussions/900
- Para MIDI programado (no tocado en vivo) un sample library está bien; un soundfont pelón es el piso, no el techo. Pianoteq (modelado físico, CPU-only, sin GPU) si quieres realismo. → https://www.opussciencecollective.com/post/the-piano-compromise-part-2-pianoteq

**Veredicto worship/devocional:** FluidR3 o Salamander + **reverb post + velocidades suaves + voicing generativo lento** es suficientemente convincente para un bed devocional donde el piano va bajo, debajo de voz/visuales. Como piano solo expuesto al frente, el sintético-ness (sin ruido de pedal, tono dry, tails en loop) se vuelve audible. **Tip que la comunidad repite: la magia es el reverb/espacio, no el soundfont.**

### ¿Alguien lo hace para YouTube sleep/lofi a escala?

- **La técnica escala — background algorítmico es patrón conocido en YouTube.** Muchos streams lofi son "algorithmically composed, uploaded consistently, watched for hours"; algunos con seis cifras de views. Lofi Girl estimado hasta €100k/mes. → https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/
- **El RPM favorece tu nicho:** sleep/relaxation ≈ $4–$8 RPM, cinematic hasta $5–$10. Beat dumps genéricos caen a $0.30–$1.
- **El catch honesto — la calidad de audio NO es el gate principal; la política "inauthentic" sí.** Pero esa política apunta a dumps de *AI* cruda. Música generada por código con TU curación + visuales devocionales originales + edición humana está del lado *más seguro* — pero aun debes "add at least two of: original visuals, voiceover, curated structure, chapters." "Stock loops + stock music = fastest path to demonetization." → https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/

**Veredicto:** El output de SuperCollider/Sonic Pi/FluidSynth (bien procesado) pasa el bar de monetizable para un canal sleep/devocional. El riesgo es volumen-sin-curación disparando el filtro de inauthentic-content, NO que el synth suene mal.

---

## Síntesis práctica para el caso devocional (loop-video-maker)

- **Olvida AI local pesado en este Mac.** MusicGen/AudioLDM2/Stable Audio en i7-9750H sin GPU = inviable (peor caso documentado). Si quieres AI, va por cloud GPU (Colab/Replicate) — pero entonces ya no es "100% local" y entras al riesgo de monetización de §3.
- **Camino más rápido a un bed usable LOCAL:** Sonic Pi (curva gentil) para la lógica generativa + reverb pesado + samples suaves. Un fin de semana = background pad/piano evolutivo.
- **Para piano:** FluidSynth + Salamander/FluidR3 sirve *como bed bajo narración/visuales*, siempre que (1) añadas reverb downstream (no confíes en el reverb roto-por-default de FluidSynth), (2) uses velocity suave, (3) lo mantengas bajo en la mezcla. Piano solo expuesto = considera Pianoteq (CPU-only, sin GPU/AI).
- **Para evitar "académico/estéril":** constriñe randomness (escala modal, probabilidad, LFOs lentos), capa 2–3 loops en distintos timescales, apóyate en espacio/reverb.
- **Monetización (lo más importante):** el motor de audio no es el bloqueador; emparéjalo con visuales devocionales originales + curación para evitar la política inauthentic-content. Música generada-por-código + curación humana > música AI cruda en riesgo de claims. Y si vas con royalty-free, Epidemic/Artlist con safelist o YT Audio Library, guardando certificados.

---

## Caveats del research

- **HN y varios subreddits (r/ambientmusic, r/edmproduction) no se indexaron bien** para estos queries específicos; las opiniones de primera mano más fuertes vinieron de foros de practicantes dedicados (scsynth.org, in-thread.sonic-pi.net, LinuxMusicians) y de discussions de GitHub/HuggingFace — que son arguablemente las comunidades MÁS relevantes para el workflow local-CPU exacto.
- Parte del detalle negativo de monetización (40% desmonetización, false-claims AI, claims de Audio Library) viene de blogs de análisis para creadores más que de threads crudos de Reddit. Para quotes de fuente primaria de creadores, el siguiente paso sería Chrome MCP sobre r/NewTubers / r/PartneredYoutube en vivo.
- Threads de HN no se pudieron fetchear directo (HTTP 429 rate-limit); HN está representado solo vía snippets de búsqueda, no quotes profundos.

---

## Índice de fuentes

**CPU AI feasibility:**
- https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md
- https://discuss.huggingface.co/t/trying-to-run-facebook-musicgen-small-on-cpu-with-16gb-ram/134517
- https://blog.peddals.com/en/apple-mps-to-generate-audio-with-meta-audiogen/
- https://huggingface.co/blog/audioldm2
- https://huggingface.co/stabilityai/stable-audio-open-small/discussions/1
- https://huggingface.co/stabilityai/stable-audio-open-1.0
- https://huggingface.co/facebook/musicgen-large/discussions/8
- https://huggingface.co/spaces/facebook/MusicGen/discussions/3
- https://medium.com/@andradeolivier/i-ported-musicgen-to-apple-silicon-generate-music-from-text-on-your-macbook-9eaf95992053
- https://github.com/ServeurpersoCom/acestep.cpp
- https://github.com/ggml-org/llama.cpp/issues/11467
- https://github.com/facebookresearch/audiocraft/issues/435
- https://github.com/facebookresearch/audiocraft/issues/224

**Creadores devocionales / monetización:**
- https://www.epidemicsound.com/blog/avoid-copyright-claims-music-epidemic-sound-2/
- https://www.epidemicsound.com/how-it-works/license-music-legally/
- https://videos.feedspot.com/sleep_music_youtube_channels/
- https://meditationmusiclibrary.com/blogs/wednesday-wisdom-blog/royalty-free-sleep-videos-monetization
- https://www.foximusic.com/blog/youtube-content-id-for-music-guide-monetization/
- https://pixabay.com/blog/posts/how-to-clear-a-youtube-content-id-claim-with-a-pix-190/
- https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/
- https://legismusic.com/is-royaltyfree-music-safe-for-monetised-youtube-channels
- https://blog.genxnotes.com/en/can-you-get-youtube-content-id-on-suno-generated-ai-music/
- https://terms.law/ai-output-rights/suno/
- https://dynamoi.com/learn/ai-music-distribution/suno-commercial-rights-explained
- https://www.cchound.com/epidemic-sound/what-happens-to-my-youtube-videos-after-i-cancel-my-epidemic-sound-subscription/
- https://help.epidemicsound.com/hc/en-us/articles/26253712691730
- https://www.tunepocket.com/make-money-youtube-sleep-videos/
- https://dynamoi.com/learn/youtube-music-promotion/ambient-music-channel-monetization-rules

**Herramientas algorítmicas:**
- https://scsynth.org/t/generative-ambient/6828
- https://in-thread.sonic-pi.net/t/i-tried-to-make-a-kinda-brian-eno-stuff-ended-up-with-kinda-lofi-generative-ambiant-brian-eno-style-stuff/9168
- https://madskjeldgaard.dk/how-to-change-the-default-synth-in-supercollider/
- https://github.com/FluidSynth/fluidsynth/discussions/900
- https://forum.loopypro.com/discussion/38764/app-auv3-with-the-best-piano-sounds/p2
- https://linuxmusicians.com/viewtopic.php?t=18829
- https://miditoolbox.com/posts/best-free-general-midi-soundfonts-2026
- https://github.com/sfzinstruments/SalamanderGrandPiano
- https://musical-artifacts.com/artifacts/483
- https://www.synthtopia.com/content/2019/04/24/twenty-techniques-for-generative-music-inspired-by-brian-eno/
- https://www.saashub.com/compare-supercollider-vs-sonic-pi
- https://sonic-pi.net/tutorial.html
- https://opguides.info/music/software/livecoding/
- https://www.opussciencecollective.com/post/the-piano-compromise-part-2-pianoteq
