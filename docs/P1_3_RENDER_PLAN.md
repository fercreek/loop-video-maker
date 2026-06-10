# P1-3 — 3 Shorts nuevos (milagro/soledad/tristeza)
> Generado 2026-06-10 · Pre-score venom pasó gate (todos L5 wired)
> Ejecutar DESPUÉS de Y1 funnel (primero wire los L4 existentes)

---

## Pre-scores (gate ≥6.0 = generar)

| ID | Score | Tier | Hook |
|----|-------|------|------|
| milagro_001 | 8.3 | L5 ✅ | ¿Necesitas un milagro hoy? |
| soledad_001 | 8.3 | L5 ✅ | ¿Te sientes completamente solo? |
| tristeza_001 | 8.2 | L5 ✅ | ¿Estás triste sin saber por qué? |

**Todos wired desde día 1:** pinned comment + end-screen → sleep 2h `6eHgRtGjaYA`.
Por eso funnel=9 (vs 2 de los L4 existentes).

---

## Comandos de render

```bash
cd /Users/fernandocastaneda/Documents/loop-video-maker

# 1. Render
.venv/bin/python3 render_short.py --id milagro_001 --voice dalia
.venv/bin/python3 render_short.py --id soledad_001 --voice dalia
.venv/bin/python3 render_short.py --id tristeza_001 --voice dalia

# 2. QA (score ≥8 requerido)
.venv/bin/python3 scripts/qa_short.py output/shorts/semana_*/short_milagro_001_*.mp4
.venv/bin/python3 scripts/qa_short.py output/shorts/semana_*/short_soledad_001_*.mp4
.venv/bin/python3 scripts/qa_short.py output/shorts/semana_*/short_tristeza_001_*.mp4

# 3. Fernando revisa 1 en QuickTime ANTES de subir los 3
# 4. Subir (si QA ≥8 y Fernando aprobó)
.venv/bin/python3 scripts/upload_shorts_venom.py
```

---

## Pinned comment (mismo para los 3)

```
🙏 Si esta oración te llegó al corazón...

Tengo preparado un espacio de 2 horas de música cristiana para descansar en Dios 👇
📖 https://youtu.be/6eHgRtGjaYA

¿Quieres ser parte de este ministerio?
☕ ko-fi.com/versiculosdedios
```

---

## Cadencia de publicación

- 1 Short/día (anti-slop)
- Sugerir: milagro → soledad → tristeza (días 1, 2, 3)
- Cross-post a FB Reels mismo día (workflow `auto-publicador-vdd` lo hace automático)

---

## Por qué estos 3 primero

Del gap analysis video-leveling (2026-06-09):
- Los 3 temas tienen keyword de búsqueda fuerte en español
- Ninguno publicado aún en el canal (pool sin usar)
- Formato "hook-25s" = plantilla ganadora documentada (`hvV1P06nUck` +474 subs)
- SEO: "necesito un milagro" / "sentirse solo" / "tristeza sin razón" = alta intención
