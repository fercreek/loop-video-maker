# Story Pipeline — Estándares y Aprendizajes
> Última actualización: 2026-05-09 · Versión del pipeline: v3

---

## Stack actual (v3 — producción)

| Componente | Herramienta | Config |
|---|---|---|
| Script | Claude API → `data/stories/{id}.json` (generado en sesión, cacheado) | 14 escenas · ~2,500 palabras |
| Imágenes | Gemini Imagen 4.0 → `output/stories/{id}/images/` | 16:9 · 1920×1080 · con personajes |
| Narración | Edge TTS `es-MX-JorgeNeural` (historias) / `es-MX-DaliaNeural` (shorts) | rate="-8%" |
| Música | MusicGen cacheado en `audio/cache/*_norm.aac` | vol=0.07 bajo narración |
| Video | ffmpeg · Ken Burns crop expression · fade 1s in / 2s out | FPS=12 · ultrafast |
| Concat | stream copy (`-c copy`) — instantáneo | sin re-encode |
| Render time | ~2.5 min (14 escenas, 17 min video) | 4 workers paralelo |

---

## Historias publicadas

| ID | Título | Estado | Fecha | Notas |
|---|---|---|---|---|
| `david-goliat` | David y Goliat | ✅ v3 lista | 2026-05-09 | Primera historia. Ver decisiones abajo. |

---

## Cola de producción (próximas historias)

| ID | Historia | Ref bíblica | Escenas | Prioridad | Razón |
|---|---|---|---|---|---|
| `noe` | Noé y el Diluvio | Génesis 6-9 | 14 | 🔴 Alta | Volumen búsqueda muy alto |
| `jonas` | Jonás y la Ballena | Jonás 1-4 | 11 | 🔴 Alta | Historia corta, muy conocida |
| `moises` | Moisés y el Éxodo | Éxodo 1-15 | 18 | 🟡 Media | Épica, más producción |
| `jose` | José: De Esclavo a Rey | Génesis 37-50 | 16 | 🟡 Media | Drama largo, muy buscado |
| `daniel` | Daniel en el Foso | Daniel 6 | 11 | 🟢 Baja | Búsqueda media, competencia baja |
| `ester` | Ester y el Rey | Ester 1-10 | 12 | 🟢 Baja | Underserved, audiencia femenina |

---

## Estándares de contenido (NO repetir errores)

### Narración
- ✅ Voz: `jorge` para historias largas · `dalia` para shorts y oraciones
- ✅ Rate: `-8%` — ritmo pausado devocional
- ❌ NO usar macOS `say` — calidad inaceptable, descartado
- ❌ NO XTTS v2 — conflictos de dependencias Python (archivado, sin mantenimiento)
- ✅ ElevenLabs como upgrade premium cuando escale ($5/mes Starter)

### Imágenes
- ✅ INCLUIR personajes/figuras en prompts (sin "no people")
- ✅ Usar "cinematic biblical illustration", "dramatic oil painting"
- ✅ Usar "silhouette", "figure", "armored warrior" — Gemini-safe
- ❌ NO usar: "violence", "blood", "gore", "decapitation" — filtro Gemini
- ✅ OK usar: "dramatic confrontation", "heroic moment", "fallen warrior", "triumphant figure"
- ✅ Cerrar cada prompt con: `dramatic oil painting, cinematic lighting, rich warm earth tones, epic biblical scale, no text, no watermark`

### Video
- ✅ Ken Burns con `scale=2112:1188` + `crop` expression — 10-20x más rápido que zoompan
- ✅ 4 direcciones rotativas: L→R, R→L, top→bottom, bottom→top (por `scene_idx % 4`)
- ✅ Fade in 1.0s / Fade out 2.0s
- ❌ NO zoompan — tardaba 40 min, reemplazado
- ❌ NO drawtext — ffmpeg sin libfreetype en esta máquina
- ✅ Concat con stream copy (`-c copy`) — instantáneo, sin re-encode

### Música
- ✅ Tracks MusicGen en `audio/cache/*_norm.aac`
- ✅ Vol bajo narración: 0.07 (-23dB aprox)
- 🔮 v2: dinámica — bajar a near-zero en momentos intensos, swell en resolución

---

## YouTube — Estándares por historia

### Título
Formato: `[Personaje/Historia] | La Historia Completa Narrada en Español`
- David y Goliat → `David y Goliat | La Historia Completa Narrada en Español`
- Noé → `Noé y el Diluvio | La Historia Completa Narrada en Español`
- Jonás → `Jonás y la Ballena | La Historia Completa Narrada en Español`

### Thumbnail
- Figura principal (pequeña) vs amenaza/gigante (sombra grande)
- Contraste dramático claro/oscuro
- Texto: máx 3 palabras, Impact bold blanco, borde negro 4px
- Sin logo de canal en thumbnail
- Colores: ámbar/dorado vs oscuro — NO azul (competidores usan azul)

### Descripción
- Primeras 150 chars: hook emocional + keyword
- Chapters exactos (calcular del video renderizado)
- Versículo relevante de la historia
- CTA comentarios: pregunta abierta emocional
- Hashtags: 15-18 tags específicos

### Chapters
- Primer chapter SIEMPRE en `0:00`
- ~75s por escena → ajustar según duración real del render
- Usar títulos narrativos, no "Parte 1", "Parte 2"

### Subida
- Día: Jueves o Viernes
- Hora: 6pm MTY (UTC-6)
- Pin comment en primera hora: pregunta emocional abierta

### Primeras 2h post-upload
1. Pin comment con pregunta emocional
2. Short de 45s con escena climática → "Historia completa en el canal"
3. Responder TODOS los comentarios en primeras 24h

---

## Backlog v2 — Mejoras pendientes

### Alta prioridad (mayor impacto en retención)

- [ ] **Cold open** — primeros 30s mostrar clímax, luego empezar historia
  - Script: añadir campo `cold_open_text` al JSON de historia
  - Render: prepend audio+imagen de cold open antes de escena 1
  - Impacto: -15% drop en primeros 2 min

- [ ] **Dinámica musical** — música sube/baja por mood de escena
  - Escenas de tensión (Solemnidad): vol reducir a 0.03
  - Escenas climáticas (Liberación): swell a 0.12 en resolución
  - Escenas de resolución (Gloria): subir gradualmente hasta 0.15

- [ ] **Multi-imagen en escenas climáticas** — cross-dissolve mid-scene
  - Escenas 11, 12, 13 (carrera, piedra, victoria): 2 imágenes
  - Cross-dissolve al segundo 35 de la escena
  - Requiere re-encode (no stream copy) para xfade filter

- [ ] **Micro-tease al min 2** — narrador âncora retención
  - Después de escena 2: "En los próximos minutos vas a escuchar algo que nadie esperaba…"
  - Añadir en `story_gen.py` como campo `retention_hook` por escena

### Media prioridad

- [ ] **End screen verbal** — últimos 10s narrador dice próxima historia
  - "Si esta historia te tocó, la historia de Noé te va a impactar igual. La encuentras aquí."
  - Aumenta session time → clave para YPP

- [ ] **Subtítulos quemados** — PIL burn-in (libass no disponible)
  - Ver `core/subtitle_burn.py` (diseñado por Backend Architect agent)
  - Aumenta watch time en mobile (muted viewing)

- [ ] **Thumbnail automation** — generar thumbnail desde imagen Scene 10-11
  - Pillow: imagen base + overlay texto bold + contrast boost
  - Output: `output/stories/{id}/thumbnail.jpg`

### Baja prioridad / v3

- [ ] Parallelizar generación de imágenes Gemini (Semaphore 3 concurrent)
- [ ] Retry exponencial en Gemini 429
- [ ] Cache key de imágenes incluir hash del prompt (evitar stale)
- [ ] `as_completed()` en ThreadPoolExecutor (robustez si falla 1 escena)

---

## Anti-strike (OBLIGATORIO antes de subir)

1. ✅ Narración: Edge TTS (licenciado) — sin audio externo copiado
2. ✅ Imágenes: Gemini Imagen 4.0 (generadas) — sin imágenes de terceros
3. ✅ Música: MusicGen local — sin ContentID risk
4. ✅ Texto: narración propia, paráfrasis bíblica — no copia de canales
5. ⚠️ Verificar en YouTube Studio → Subir → Verificar derechos ANTES de publicar

---

## Comandos de referencia

```bash
# Nueva historia (primera vez — genera script en sesión con Claude)
# Editar data/stories/{id}.json manualmente o via Claude

# Render completo
.venv/bin/python3 render_story.py --story {id} --voice jorge

# Re-render solo narraciones (cambio de voz)
.venv/bin/python3 render_story.py --story {id} --force-narr --voice jorge

# Re-render solo imágenes (prompts actualizados)
rm output/stories/{id}/images/*.jpg output/stories/{id}/clips/*.mp4
.venv/bin/python3 render_story.py --story {id}

# Dry-run (ver plan sin ejecutar)
.venv/bin/python3 render_story.py --story {id} --dry-run

# Listar historias disponibles
.venv/bin/python3 render_story.py --list

# Test narración Edge TTS
.venv/bin/python3 -m core.narration_gen --voice jorge --text "texto de prueba"
```
