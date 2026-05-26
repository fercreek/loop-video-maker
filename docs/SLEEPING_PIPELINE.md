# Sleeping Video Pipeline — Spec

> Path realista a monetización YPP (3000h watch / 365d).
> Math: 10 videos sleeping × 1.5h × 200 views avg × 50% retention = 15000h acumulado año 1.

---

## Objetivo

Generar videos 90-120 min de audio ambient cristiano + imagen cinematic Ken-Burns lento, optimizados para "use case sleeping" (audiencia dormida o pre-dormir, alta retention pasiva).

## Diferencias vs `render_120min.py` actual

| Aspecto | 120min actual | Sleeping v1 |
|---------|---------------|-------------|
| Versos visibles | Cycling cada 30s | Sin texto (solo título inicial 10s) |
| Narración | Sin voz | Sin voz (v1) o whisper Salmo (v2) |
| Música | MusicGen 3 moods alternados | MusicGen 1 mood sostenido + rain/river fondo |
| Visual | Pinturas óleo cambiando | 1-2 imágenes mflux con Ken-Burns 5% en 120min |
| Resolución | 1920x1080 | 1920x1080 |
| Anti-strike | ✅ | ✅ (mismo stack propio) |

## Spec técnica v1

```yaml
duration_min: 90 | 120
resolution: 1920x1080
fps: 24  # lower fps OK para video estático casi
codec: h264, preset=fast, crf=22
audio:
  music_mood: "sleep_ambient" | "rain_piano" | "soft_strings"
  music_volume_db: -12  # más alto que Shorts (-18) porque no hay voz
  source: MusicGen local (audio/cache/)
  ambient_overlay: optional (rain.wav, river.wav at -28dB)
voice:
  enabled: false  # v1
  # v2: whisper Salmo via Edge TTS dalia rate=-30% volume=0.2
visual:
  bg_images: 1-2 mflux generated (presets: cielo_nocturno, gloria_eterna, paz_clasica)
  ken_burns:
    type: "ultra_slow_zoom_in"  # 1.00 → 1.05 en 90min = 0.056%/min
    duration_sec: TARGET_DURATION
overlay:
  intro_title_sec: 10  # solo primeros 10s
  intro_fade_sec: 1.5
  watermark: "@VersiculoDeDios" arriba derecha siempre
```

## Estimated render time

- Audio gen (MusicGen 90min): ~8-12 min
- Video render (1920x1080 @ 24fps, 90min, KB lento): ~15-25 min
- **Total:** ~25-40 min por video
- File size: ~600MB-1.2GB

## 5 temas v1 (alta intent ES)

1. **Salmo 91 para Dormir** (2h) — protección
2. **Rosario para Dormir** (1.5h) — católico mass appeal
3. **Salmo 23 + 91 + 121 Combo** (2h) — protección+confianza
4. **Versículos contra Ansiedad para Dormir** (1.5h)
5. **Promesas de Dios para Dormir** (2h)

## Title/thumbnail formula

**Title:** `[VERSÍCULO/CONCEPTO] para DORMIR · [DURATION]H · Sin Anuncios | Música Cristiana`

Ejemplos:
- `SALMO 91 para DORMIR · 2 HORAS de Protección Divina · Sin Anuncios`
- `VERSÍCULOS para DORMIR EN PAZ · 1H 30M · Música Cristiana Suave`

**Thumbnail:**
- Fondo: paisaje nocturno mflux (cielo_nocturno, luna, estrellas)
- Texto grande: "DORMIR EN PAZ" o "SALMO 91" tipografía elegante
- Subtítulo: "2 HORAS · SIN ANUNCIOS"
- Esquina: ícono Biblia o cruz luminosa

## Upload schedule

- 1 sleeping/semana (domingo 9pm MTY publish)
- Categoría: Music (no Education) — algoritmo asocia con relaxation/sleep
- Tags: `versiculos para dormir, salmo 91, oracion noche, musica cristiana, sleep prayer, biblia para dormir`
- Descripción: timestamps de cada Salmo + crédito MusicGen + invite suscribirse

## Pipeline architecture

```
render_sleep.py
  ├── load_sleep_config(tema, duration) → returns spec
  ├── generate_ambient_audio(mood, total_sec, crossfade)
  │     └── reuses core/music_gen.py
  ├── compose_visual(bg_images, duration, ken_burns_speed)
  │     └── reuses ffmpeg zoompan pattern from shorts_render
  ├── render_intro_overlay(titulo, fade_sec)
  │     └── Pillow text track 10s
  ├── ffmpeg_compose(audio, video, overlay) → mp4
  └── register_in_content_registry()
```

## Validación QA

Adaptar `scripts/qa_short.py` → `scripts/qa_longform.py`:
- Duration check: 85-130 min (vs Shorts 25-90s)
- LUFS: -18 (sleep target, no -16 que es para voz)
- Motion: SSIM threshold MÁS PERMISIVO (>0.99 OK porque ken-burns ultra-lento)
- Audio band: NO requiere voice band check (no hay voz)

## Roadmap implementación

- [ ] **Fase 1 (1-2h dev):** `render_sleep.py` v1 sin voz + 1 imagen + 1 mood
- [ ] **Fase 2 (30 min):** Generar 1 test video (Salmo 91 90min) → medir tiempo + tamaño
- [ ] **Fase 3 (1h):** `scripts/qa_longform.py` adaptado
- [ ] **Fase 4 (varios días):** Renderear 5 sleeping videos + upload schedule
- [ ] **Fase 5 (30 días):** Medir watch time real vs estimación

## Costo

- $0 software (todo local: MusicGen + mflux + ffmpeg)
- ~9GB RAM mflux + ~4GB MusicGen = cerrar Chrome antes de render
- Tiempo dev inicial: ~3-4h
- Tiempo render por video: ~25-40 min
