# Iter NN — <nombre-fix>

**Fecha:** YYYY-MM-DD
**Versión entrada:** `vX.Y-<tag>`
**Versión salida:** `vX.Y-<tag>`
**Commit inicio → fin:** `abc1234` → `def5678`

---

## Batch rendereado

| # | Tema | Duración | Moods | Render time | Score |
|---|------|----------|-------|-------------|-------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Score promedio batch:** X/100
**Score batch anterior:** Y/100 (iter NN-1)
**Δ:** +/-Z

---

## Eval — issues detectados

| Video | Issue | Severidad | Evidencia |
|-------|-------|-----------|-----------|
| | | | |

### Patrón dominante

_¿Mismo tipo de issue en >3 videos? Ese es el root cause candidato._

---

## Root cause analysis

**Hipótesis:** _¿Por qué falló?_

**Evidencia:** _logs, eval JSON, config_

**Confirmación:** _test que prueba/refuta hipótesis_

---

## Fix aplicado

**Archivo(s):** `core/...`
**Cambio:** _qué se modificó_
**Commit:** `git log -1`

---

## Verificación post-fix

Re-render 1 video para confirmar:
- Score antes: X
- Score después: Y
- Δ: +/-Z

---

## Lecciones

- _qué aprendimos (también copiado a `LEARNINGS.md`)_

---

## Siguiente iter

**Hipótesis a probar:** _qué probar en iter NN+1_
**Foco:** audio | video | thumb | performance
**Batch sugerido:** _próximos 5 temas_
