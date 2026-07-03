# Síntesis: Música 100% LOCAL para VersículoDeDios en Mac Intel (sin GPU)
> Fuentes: claude-web (18 búsquedas) + AI live/Perplexity (39 fuentes) + community (~30 fuentes)
> Hardware: MacBook Pro 2019 · Intel i7-9750H · 16GB RAM · sin GPU dedicada
> Fecha: 2026-06-22

## Consenso cross-source (las 3 concuerdan)

| Veredicto | Detalle | Fuentes |
|---|---|---|
| **Neural local = inviable en esta Mac** | MusicGen/AudioLDM2/Stable Audio en CPU Intel: minutos por pocos segundos de audio (~54× slower que real-time). Community: "PyTorch on CPU painfully slow", "sounds underwater". | ✅ Las 3 |
| **IA rápida solo en Apple Silicon/GPU** | MLX/MPS/CUDA — no existe en i7-9750H. No hay `musicgen.cpp` maduro; cuantizar en CPU es *más lento*. | ✅ Las 3 |
| **Algorítmico local SÍ corre y SÍ suena bien** | Sonic Pi / SuperCollider / FluidSynth: real-time en tu i7, RAM mínima, **salida 100% tuya, cero Content ID**. Ambient Eno-style logrado por la comunidad. | ✅ Las 3 |
| **YouTube Audio Library = lo más seguro para monetizar** | Cero Content ID + 100% monetizable. El camino más rápido HOY. | ✅ Las 3 |
| **CC-BY-NC = la trampa** | MusicGen, AudioLDM2, MAGNeT y media biblioteca FMA/ccMixter son non-commercial → **prohibido monetizar**. Atribución ≠ licencia. | ✅ Las 3 |

## Conflictos detectados y resolución

**1. Licencia + RAM de AudioLDM2** — AI-live dijo "Apache-2.0, 3-9 min/min"; web dijo "CC-BY-NC, ~20GB RAM (no cabe en 16GB)".
→ **Resolución:** El código puede ser permisivo pero los *pesos* son CC-BY-NC (patrón confirmado por web+community). Y de cualquier forma **no corre práctico en CPU/16GB**. Veredicto: descartar en esta Mac, punto.

**2. Pixabay** — AI-live lo marcó "CC0 seguro"; web+community dijeron "comercial OK pero genera claims que hay que disputar".
→ **Resolución:** Pixabay es usable comercialmente pero **NO inmune a Content ID**. **YouTube Audio Library es estrictamente más seguro** → ese es el primario.

## Hallazgo nuevo crítico (community)
**Política YouTube "inauthentic content" (jul 2025):** +40% de canales de música 100% AI **desmonetizados** desde fin de 2025. El bloqueador de monetización **no es el motor de audio — es política + curación.** Música generada-por-código + tu curación + visuales devocionales originales = lado seguro. Volumen de AI cruda sin curar = lo que mata. Nicho sleep/devocional paga bien ($4–$10 RPM).

## Recomendación final por caso de uso (devocional dedicado, Intel sin GPU)

| Caso | Ganador | Por qué | Costo / CPU |
|---|---|---|---|
| **Máxima calidad, monetización a prueba de balas, YA** | **YouTube Audio Library** → loops + crossfade ffmpeg (ya en el repo) | Cero Content ID, cero CPU, real recordings | $0 / nulo |
| **Música propia infinita y diferenciada (sleep/ambient/pads)** | **Sonic Pi** (quick-win fin de semana) o SuperCollider (más calidad, más curva) | Salida 100% tuya → inmune a Content ID y a la política "inauthentic" | $0 / real-time |
| **Piano worship "bed" bajo narración** | **FluidSynth + soundfont** (Salamander/FluidR3) | "Good enough" como cama, no piano de estudio | $0 / bajo |
| **IA neural de música** | ❌ Ninguna en esta Mac | Lento + licencia + RAM. Guardar para Apple Silicon/GPU futura | — |

## Stack de música recomendado para esta Mac dedicada
1. **HOY:** bajar tracks de **YouTube Audio Library** (worship/ambient/piano) → meter a `audio/loops/` + `manifest.json` → el crossfade del repo los extiende a horas. Esto + los 32 loops + 10GB de cache de Mac A = música de sobra, monetizable, sin tocar el hardware.
2. **Diferenciación (semana siguiente):** montar **Sonic Pi** para generar pads/drones ambient propios infinitos (truco "Music for Airports": loops de distinta longitud). Output 100% tuyo.
3. **Opcional:** FluidSynth + soundfont para piano beds — **OJO gotcha: el reverb está roto por default, añadir reverb downstream** o suena seco/muerto.

## Evitar siempre
| Herramienta | Por qué |
|---|---|
| MusicGen / musicgen.cpp / AudioLDM2 / MAGNeT / Stable Audio en CPU | Inviable en Intel sin GPU + licencia CC-BY-NC (no monetizable) |
| Suno / Udio (AI cruda) para volumen | Política "inauthentic" → ola de desmonetización 2025 |
| Tracks CC-BY-NC de FMA/ccMixter | Non-commercial = prohibido en canal monetizado |
| Pixabay como primario | Comercial OK pero genera claims; YTAL es más seguro |

## Nota de verificación
Antes de monetizar con cualquier soundfont .sf2: verificar la licencia individual del soundfont (no todas son libres para uso comercial).
