# Loop Video Maker — System Design

## 1. Objetivo

Herramienta de escritorio local que genera videos .mp4 de versiculos
biblicos para YouTube. Corre 100% local, abre UI en navegador.

## 2. Entorno Actual Verificado

```
Python:    3.9.6 (system, macOS)
ffmpeg:    imageio-ffmpeg bundled (v7.1, aarch64)
Gradio:    4.36.0 (funcional, HTTP 200 verificado)
MoviePy:   2.1.2 (render test OK, genera .mp4 con libx264)
Pillow:    10.4.0 (text rendering OK)
NumPy:     2.0.2
Requests:  2.32.5
Anthropic: en requirements (para Claude API)
Fonts:     202 system fonts disponibles, assets/fonts/ vacio
```

## 3. Stack Definitivo con Evaluacion

### UI: Gradio 4.36.0 — CONFIRMADO

| Aspecto       | Estado |
|---------------|--------|
| Funciona      | Si, HTTP 200 en localhost:7860 |
| Python 3.9    | Si, con esta version especifica |
| Dark theme    | Si |
| Limitacion    | No usar Gradio >4.44 con Py 3.9 (bug huggingface_hub) |

**Decision**: Mantener `gradio==4.36.0` pin exacto en requirements.txt.

### Video Render: MoviePy 2.x + Pillow — CONFIRMADO

| Aspecto            | Estado |
|--------------------|--------|
| Genera .mp4        | Si, test de render exitoso (libx264) |
| ffmpeg             | Bundled via imageio-ffmpeg, NO necesita instalacion |
| TextClip           | Disponible, usa Pillow internamente en v2 |
| Audio              | AudioFileClip soporta WAV y MP3 |
| Python 3.9         | Si |

**Decision**: Usar MoviePy 2.x con Pillow para generar text overlays como
ImageClip (mas control que TextClip nativo). Esto evita dependencias de
ImageMagick que MoviePy 1.x requeria.

**Approach para texto en video**:
```
Pillow genera imagen PNG del texto con sombra
  -> numpy array
  -> MoviePy ImageClip con .with_position() y .with_opacity()
  -> CompositeVideoClip
```

### Imagenes: Gemini API via google-generativeai — NECESITA INSTALACION

| Opcion                    | Pros                              | Contras                        |
|---------------------------|-----------------------------------|--------------------------------|
| Gemini 2.0 Flash          | Gratis (tier free), genera imgs   | Requiere SDK + API key         |
| Imagen 3 (Vertex AI)      | Alta calidad                      | Requiere GCP project + billing |
| Placeholder Pillow         | Sin dependencias, offline         | Solo gradientes, no fotos      |
| Subir imagen propia       | Maximo control                    | Usuario debe tener la imagen   |

**Decision**: Estrategia dual:
1. **Placeholder mejorado** con Pillow (gradientes mas elaborados) para funcionar SIN API key
2. **Gemini 2.0 Flash** como opcion cuando el usuario configure su key
3. **Subir imagen propia** siempre disponible (ya implementado)

Paquete: `google-generativeai` (agregar a requirements.txt)

### Musica: Mubert API — PROBLEMATICO

| Aspecto            | Estado |
|--------------------|--------|
| API online         | Parcial — TTM endpoint responde pero requiere "application" token |
| Acceso free        | NO CLARO — su API parece ser enterprise/partnership only ahora |
| Alternativas cloud | Suno API (de pago), Udio (no API publica) |

**PROBLEMA CRITICO**: Mubert no tiene un tier gratuito accesible. Su API
requiere un token de "application" que se obtiene por partnership.

**Decision — 3 niveles**:
1. **Nivel 0 (offline, siempre funciona)**: Generar ambient drone con NumPy
   - Acordes suaves con sine waves + reverb simple
   - Fade in/out, capas de armonicos
   - NO es musica de calidad pero permite que el video se genere
2. **Nivel 1 (con archivo propio)**: Subir MP3/WAV propio
   - Muchos canales de YouTube usan musica royalty-free descargada
   - Loop automatico si el audio es mas corto que el video
3. **Nivel 2 (con API key)**: Mubert API si el usuario tiene acceso
   - Mantener el adaptador pero NO depender de el

### Versiculos: JSONs locales + Claude API — CONFIRMADO

| Aspecto            | Estado |
|--------------------|--------|
| 10 JSONs           | Si, 469 versiculos totales (43-59 por tema) |
| Estructura         | Consistente (id, texto, referencia, version) |
| Claude API         | Implementado en verse_gen.py |
| Funciona offline   | Si, los JSONs son suficientes sin API |

**Decision**: Mantener como esta. Funcional con y sin API key.

### Fonts: Necesitan descarga local

| Aspecto            | Estado |
|--------------------|--------|
| Preview HTML       | Usa Google Fonts CDN (requiere internet) |
| Video render       | Necesita .ttf local para Pillow |
| assets/fonts/      | Directorio existe pero VACIO |

**Decision**:
- Descargar EB Garamond Italic y Cinzel Regular de Google Fonts (OFL license)
- Bundlearlos en assets/fonts/
- Fallback a system fonts si no estan (Georgia italic, Times New Roman)

## 4. Diagrama de Componentes

```
                    +------------------+
                    |     app.py       |
                    |  (Gradio 4.36)   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------+--+   +------+-----+  +-----+-------+
     | verse_gen  |   | image_gen  |  | music_gen   |
     | (JSON +    |   | (Pillow +  |  | (NumPy +    |
     |  Claude)   |   |  Gemini)   |  |  MP3 upload)|
     +--------+---+   +------+-----+  +------+------+
              |              |               |
              +-------+------+-------+-------+
                      |              |
              +-------+----+  +------+-------+
              |preview_eng |  |video_render  |
              |(HTML/JS/   |  |(MoviePy 2.x +|
              | CSS base64)|  | Pillow text) |
              +------------+  +--------------+
                                     |
                              +------+------+
                              |  ffmpeg     |
                              | (bundled)   |
                              +-------------+
```

## 5. Data Flow — Generacion de Video

```
1. Usuario selecciona tema
   -> cargar_versiculos() -> JSON -> tabla editable

2. Usuario genera/sube imagen
   -> Pillow gradient | Gemini API | archivo subido -> .jpg 1920x1080

3. Usuario genera/sube musica
   -> NumPy ambient | archivo .mp3 subido | Mubert API -> .wav/.mp3

4. Preview
   -> preview_engine convierte img+audio a base64
   -> HTML autocontenido con JS animation engine
   -> Gradio gr.HTML renderiza inline

5. Render final
   -> ImageClip(imagen, duracion=total)
   -> Para cada versiculo:
      Pillow genera texto+sombra como RGBA image
      -> ImageClip con fade in (1.5s) + visible + fade out (1.5s)
   -> AudioFileClip(musica)
   -> CompositeVideoClip(fondo + [texto_clips])
   -> .write_videofile(codec=libx264, audio_codec=aac, bitrate=8000k)
   -> output/{nombre}.mp4
```

## 6. Cambios Requeridos al Plan Original

| Componente       | Plan Original          | Cambio                                    | Razon                           |
|------------------|------------------------|-------------------------------------------|---------------------------------|
| requirements.txt | gradio>=4.0.0          | gradio==4.36.0                            | Compatibilidad Python 3.9       |
| requirements.txt | (no tenia)             | + google-generativeai                     | SDK para Gemini image gen       |
| Mubert           | Dependencia principal  | Opcional, agregar upload MP3 + NumPy gen  | API no es accesible gratis      |
| Fonts            | "Descargar de Google"  | Bundlear con el proyecto                  | Necesario para render offline   |
| image_gen.py     | Solo placeholder       | Placeholder mejorado + subir propia       | Funcional sin API key           |
| music_gen.py     | Solo Mubert            | NumPy ambient + subir MP3 + Mubert opt.   | Funcional sin API key           |
| video_render     | TextClip directo       | Pillow -> numpy -> ImageClip              | Mas control, sin ImageMagick    |

## 7. Orden de Implementacion (Sprints revisados)

### Sprint 2A — Hacer funcional sin APIs (PRIORIDAD)
1. Descargar fonts y bundlear en assets/fonts/
2. Mejorar image_gen.py: gradientes mas bonitos con Pillow
3. Implementar music_gen.py: ambient con NumPy (acordes + pads)
4. Agregar boton "Subir mi propio audio" en app.py
5. Implementar video_render.py completo con MoviePy

### Sprint 2B — APIs opcionales
1. Conectar Gemini API en image_gen.py
2. Mantener Mubert como opcion si hay API key
3. Claude API ya funciona para generar versiculos

## 8. Riesgos y Mitigaciones

| Riesgo                                    | Impacto | Mitigacion                                |
|-------------------------------------------|---------|-------------------------------------------|
| Video de 60min tarda mucho en renderizar   | Alto    | Progress bar, estimar tiempo, render async|
| Fonts no disponibles en Windows           | Medio   | Bundlear .ttf, fallback a system fonts    |
| Python 3.9 deprecated                     | Bajo    | Codigo compatible 3.9-3.12 con __future__ |
| Memoria en videos largos (60-120 min)     | Alto    | Render por segmentos, no todo en RAM      |
| Mubert API inaccesible                    | Alto    | Ya mitigado: NumPy gen + upload propio    |
