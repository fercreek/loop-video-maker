# SESSION RESUME — VersiculoDeDios pipeline
> Última sesión: 2026-05-10
> Próxima sesión: continuar desde aquí

---

## ⚡ Comando exacto de continuación

```bash
# Lo que querías correr al terminar:
python3 scripts/generate_fondos_mflux.py --preset cielo_nocturno --count 2 --format 9:16
```

Este script aún no existe. Pendiente crearlo en próxima sesión.

---

## 📊 Estado actual del pipeline

### Videos rendereados y listos para subir (4)

| Historia | Duración | Tamaño | Path |
|---|---|---|---|
| David y Goliat | 19.5 min | 518 MB | `output/stories/david-goliat/david-goliat.mp4` |
| Noé y el Diluvio | 20.5 min | 522 MB | `output/stories/noe/noe.mp4` |
| Jonás y la Ballena | 17.4 min | 428 MB | `output/stories/jonas/jonas.mp4` |
| Moisés y el Éxodo | 23.3 min | 606 MB | `output/stories/moises/moises.mp4` |

**Total: ~80 min · 2.1 GB · ninguno subido todavía**

### Pipeline tech stack (validado funcionando)

- Narración: **Edge TTS Jorge ES-MX Neural** (gratis, neural)
- Imágenes: **Gemini Imagen 4.0** con personajes (no "no people")
- Video: ffmpeg + Ken Burns crop linear + fade transitions
- Subtítulos: **karaoke sincronizado dorado** (PIL + word boundaries proporcionales)
- Cold open + End screen automáticos via JSON
- Música dinámica por mood (Solemnidad=0.04 → Gloria=0.13)
- Concat stream copy (instantáneo)
- Cleanup automático de clips/ post-render
- Render time: ~3-5 min por video

---

## 🧠 Inteligencia de venom (data fresca 2026-05-10)

### Canal status
- **11,700 subs** · 588 hrs/28d · 993 videos · YPP **19.6%** progress
- Best performer 28d: "Promesa Cumplida: Pacto Eterno" (Short)
- **8 videos 120min YA RENDEREADOS sin subir** (deuda técnica gigante)

### Patrones validados (TU canal)
- Hook ganador en Shorts: emoji + tensión narrativa
  - "3 DÍAS de silencio... ¿y después?"
  - "BATALLA GANADA aunque no veas victoria"
- Voz: ElevenLabs masculina ES-MX (Daniel/Antonio) — sin A/B con femenina aún

### Patrones industria (sin scraping aún)
- Shorts religiosos: 35-45s convierte mejor que 60s
- Hora pico ES devocional: **6-7am** (oración matutina) y **9-10pm** (antes de dormir) MTY/CDMX
- Long-form competencia: 100K-1M subs, retención 35-45% en 60min
- **Gap claro:** historias bíblicas largas con producción cinemática (la mayoría hace lectura plana sobre fondo estático) ← **TU pipeline ataca este gap directo**

---

## 📅 Calendario litúrgico — picos a planear

| Fecha | Evento | Subir contenido (10-14 días antes) |
|---|---|---|
| **24 may 2026** ⚡ | **Pentecostés** | Subir 10-14 may: Hechos 2, Espíritu Santo |
| 15 ago | Asunción de María | Subir 1-5 ago |
| 2 nov | Día de Muertos | Subir 20-25 oct: Apocalipsis 21, vida eterna |
| 30 nov - 24 dic | Adviento | Subir desde 20 nov: profecías Mesías, Isaías 9 |
| 24-25 dic | Navidad | Subir 18-22 dic: Lucas 2, Mateo 1 |

**Pentecostés es URGENTE — 14 días.**

---

## 🎯 Próximas 20 producciones (orden recomendado por venom)

### 10 Stories largas (15-25 min)
1. **Pentecostés / Hechos 2** ⚡ pico estacional 24 may
2. José en Egipto ← gap grande, alta búsqueda
3. Daniel y los leones
4. Sansón y Dalila
5. Ester salva a su pueblo
6. Ruth y Booz
7. Elías y los profetas de Baal
8. Job — la prueba
9. Abraham e Isaac (sacrificio)
10. Resurrección de Lázaro

### 10 Shorts devocionales (oraciones — intent search alto)
1. Oración de la mañana
2. Oración para dormir
3. Oración por mi familia
4. Oración para la ansiedad
5. Oración de protección
6. Salmo 91 narrado
7. Oración por dinero/provisión
8. Oración para el matrimonio
9. Oración de sanidad
10. Oración por mis hijos

---

## 🛠 Comandos clave

```bash
# Renderizar nueva historia (cualquier ID en STORIES dict)
.venv/bin/python3 render_story.py --story <id> --voice jorge

# Catálogo
.venv/bin/python3 scripts/catalog_manager.py --summary
.venv/bin/python3 scripts/catalog_manager.py --next 10
.venv/bin/python3 scripts/catalog_manager.py --mark-uploaded <id> --youtube-id <yt>

# Edge TTS test
.venv/bin/python3 -m core.narration_gen --voice jorge --text "..."

# Re-auth YouTube (token vencido)
python3 scripts/yt_auth.py
```

---

## 🚧 Pendientes críticos (próxima sesión)

### Inmediato (alta prioridad)
- [ ] **Re-auth YouTube** — token vencido
- [ ] **Subir 4 videos rendereados** (David → Noé → Jonás → Moisés)
- [ ] **Generar Pentecostés story** ⚡ antes del 14 may (calendario)
- [ ] **Subir 8 videos 120min** ya rendereados (deuda técnica de venom)

### Backlog técnico
- [ ] Crear `scripts/generate_fondos_mflux.py` (preset+count+format)
- [ ] Crear `venom/scripts/fetch-yt-trends.py` para validar trends con data real
- [ ] Auto-update catálogo post-render (actualmente manual)
- [ ] Batch script para renderizar N historias secuenciales
- [ ] YouTube upload automation (actualmente manual)

### Backlog producto
- [ ] A/B testing voz Jorge vs Dalia en shorts (sin data aún)
- [ ] 6 oraciones más para `oraciones_pool.json` (tiene 14, queremos 30)
- [ ] Thumbnail automation desde imagen Scene 11 + texto Impact

---

## 📁 Archivos de referencia (para retomar contexto)

| Archivo | Para qué |
|---|---|
| `_RESUME-SESSION.md` | **ESTE archivo** — pickup point |
| `_NEXT.md` | Tareas inmediatas |
| `docs/STORY_PIPELINE.md` | Estándares completos del pipeline |
| `data/video_catalog.json` | Catálogo 100 videos con tracking |
| `data/stories/*.json` | Scripts de historias (4 listos: david-goliat, noe, jonas, moises) |
| `data/oraciones_pool.json` | Pool de 14 oraciones para shorts |
| `render_story.py` | Pipeline principal historias largas |
| `render_short.py` | Pipeline shorts (sin probar aún) |
| `core/narration_gen.py` | Edge TTS + word boundaries |
| `core/subtitle_burn.py` | Subtítulos karaoke PIL |
| `scripts/catalog_manager.py` | Gestión de catálogo |

---

## 🔑 Configuración crítica

`config.json` debe tener:
- `gemini_api_key` ✅ presente
- `claude_api_key` ❌ falta (no necesario si scripts ya generados manualmente)
- `elevenlabs_api_key` ❌ opcional (usamos Edge TTS gratis)

Tokens YouTube: `data/yt_token.json` ❌ vencido — re-auth antes de subir

---

## 💡 Decisión estratégica clave

**Estrategia híbrida confirmada por venom + agentes:**
- **Long-form (15-25 min):** historias narradas para watch time → YPP
- **Shorts (35-45s):** oraciones devocionales para subscriber growth
- **Subir en cluster:** 2-3 videos por semana mismo tema crea recommendation cluster

**No subir videos en isolation.** Subir David + Noé misma semana, Jonás + Moisés siguiente, etc.
