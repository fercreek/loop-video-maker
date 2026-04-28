# _NEXT — Tareas pendientes

_Última actualización: 2026-04-28_

---

## 📺 Subida a YouTube — Estado

### Publicados / programados
| Video | Formato | Fecha | Estado |
|---|---|---|---|
| paz | 60min | 2026-04-28 | ✅ programado |
| fe | 120min | 2026-04-28 | ✅ programado |

### Cola pendiente (1 cada 3 días)
Sugerencia de orden — alternar tema y formato para máxima diversidad:

| # | Video | Formato | Fecha sugerida |
|---|---|---|---|
| 3 | esperanza | 60min | 2026-05-01 |
| 4 | paz | 120min | 2026-05-04 |
| 5 | amor | 60min | 2026-05-07 |
| 6 | fe | 60min | 2026-05-10 |
| 7 | gratitud | 120min | 2026-05-13 |
| 8 | victoria | 60min | 2026-05-16 |
| 9 | esperanza | 120min | 2026-05-19 |
| 10 | gratitud | 60min | 2026-05-22 |
| 11 | fuerza | 60min | 2026-05-25 |
| 12 | amor | 120min | 2026-05-28 |
| 13 | salmos | 60min | 2026-05-31 |
| 14 | sanacion | 60min | 2026-06-03 |
| 15 | provision | 60min | 2026-06-06 |

Metadata completo en: `output/SUBIR/metadata.txt`

---

## 🔴 Prioritario — Renders pendientes

### 120min batch v3.11 (incompleto)

Completados con v3.11 (moods únicos + Ken Burns balanceado):
- ✅ paz
- ✅ fe
- ✅ esperanza
- ✅ amor
- ✅ gratitud

Pendientes — re-renderizar con `--force`:
- ⏳ victoria
- ⏳ fuerza
- ⏳ salmos
- ⏳ sanacion
- ⏳ provision

**Comando para reanudar:**
```bash
caffeinate -i .venv/bin/python3 render_120min.py \
  --themes victoria fuerza salmos sanacion provision \
  --force --skip-qgate
```
Estimado: 5 × ~22 min = ~1.8 horas

---

## 🟢 Mejoras futuras (no bloqueantes)

- [ ] Shorts automáticos — extraer top 3 versículos como clips 60s
- [ ] 180min format — sleep/estudio, baja competencia
- [ ] Thumbnail con foto de persona (Midjourney) — mayor CTR
- [ ] Correr quality gate en los 5 videos 120min v3.11 ya renderizados
