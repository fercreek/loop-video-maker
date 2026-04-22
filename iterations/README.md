# Iteraciones — Loop Video Maker

Sistema de mejora gradual por batches de 5 videos.

## Loop

1. **Render batch** — 5 videos (next 5 themes en rotation)
2. **Eval** — `eval_render.py` mide los 5 + thumbnails
3. **Analizar** — agrupar issues por patrón, hipótesis de root cause
4. **Fix** — aplicar mejora a engine (audio, video, thumbs)
5. **Tag** — `v3.X-iterN-<feature>`
6. **Documentar** — `iter_NN_<date>.md` con: input version, batch, eval, hipótesis, fix, output version, lecciones
7. **Loop** — siguiente iter LEE último `iter_*.md` y prueba la fix

## Estructura

```
iterations/
├── README.md                       (este doc)
├── index.md                        (índice cronológico, scores, mejoras)
├── iter_01_v3.3-audio-fix.md      (primera iter completa)
├── iter_02_<next>.md
└── ...
```

## Plantilla `iter_NN.md`

Ver `_template.md`. Cada iter responde:

- ¿Qué versión entra?
- ¿Qué 5 videos rendereados?
- ¿Score promedio del batch?
- ¿Qué falló (audio, thumb, video)?
- ¿Por qué falló — root cause?
- ¿Qué fix se aplicó?
- ¿Qué versión sale?
- ¿Cuál es la siguiente hipótesis a probar?

## Reglas

- **5 videos por batch** (rotación: amor, esperanza, fe, fuerza, gratitud, paz, salmos, victoria — repite)
- **Score baseline = avg último batch**. Mejora = >+5 puntos.
- **No avanzar si batch < último batch**. Investigar regresión primero.
- **Lecciones acumulan en `LEARNINGS.md`** además del iter doc.
