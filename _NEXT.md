# _NEXT — Tareas pendientes

_Última actualización: 2026-04-28_

---

## 🔴 Prioritario — Renders pendientes

### 120min batch v3.11 (incompleto)

Completados con v3.11 (moods únicos + Ken Burns balanceado):
- ✅ paz
- ✅ fe
- ✅ esperanza
- ✅ amor

Pendientes — re-renderizar con `--force`:
- ⏳ gratitud
- ⏳ victoria
- ⏳ fuerza
- ⏳ salmos
- ⏳ sanacion
- ⏳ provision

**Comando para reanudar:**
```bash
caffeinate -i .venv/bin/python3 render_120min.py \
  --themes gratitud victoria fuerza salmos sanacion provision \
  --force --skip-qgate
```
Estimado: 6 × ~22 min = ~2.2 horas

---

## 🟡 Pendiente — Subir a YouTube

Carpeta lista: `output/SUBIR/`
- 60min: 10 videos + 10 thumbnails ✅
- 120min: 10 thumbnails ✅ / MP4s → re-renderizar primero (ver arriba)
- Chapters: `output/SUBIR/chapters.txt` ✅

**Después de completar renders 120min:**
1. Actualizar hard links en `output/SUBIR/120min/` con los 6 videos nuevos
2. Subir con cadencia: **1 video cada 3 días** (evitar filtro near-duplicate)
3. Pegar chapters de `output/SUBIR/chapters.txt` en cada descripción

---

## 🟢 Mejoras futuras (no bloqueantes)

- [ ] Shorts automáticos — extraer top 3 versículos como clips 60s
- [ ] 180min format — sleep/estudio, baja competencia
- [ ] Thumbnail con foto de persona (Midjourney) — mayor CTR
- [ ] Template descripción YouTube con crédito Kevin MacLeod
- [ ] Correr quality gate en los 4 videos 120min v3.11 ya renderizados
