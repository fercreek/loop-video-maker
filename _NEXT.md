# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-05-11 · Canal: @VersiculoDeDios · 11,700 subs

---

## ⚡ En proceso (retomar aquí)

### 📤 Upload semana 2 — corriendo en background
- 6 videos subiendo ahora: buen-samaritano, hijo-prodigo, lazaro, resurreccion, ruth, job
- Quedan private hasta su fecha — YT Studio para revisar/eliminar si algo falla
- Notificación cuando termine → actualizar `_CALENDARIO-SUBIDA.md` con links

### 📋 Semana 3 — scripts por generar
- **Flujo nuevo:** render → **tú revisas MP4 en QuickTime** → "listo sube" → upload
- Historias pendientes (P1):
  1. La Creación del Mundo
  2. Torre de Babel
  3. Sodoma y Gomorra (Lot)
  4. Elías y los Profetas de Baal
  5. Gedeón y los 300
  6. Josué y Jericó
  7. Salomón y su Sabiduría
  8. Sermón del Monte
  9. Última Cena
  10. Pedro camina sobre el agua
- Generar: lanzar agentes Book Co-Author (igual sesión anterior)
- Render batch: `python3 scripts/batch_render.py --max 10 --priority 1`
- Revisar: `open output/stories/{id}/{id}.mp4` en QuickTime
- Subir: decirle a Claude "listo, sube"

---

## ✅ Completado 2026-05-11

- [x] 100-story catalog (`data/video_catalog.json`) — fuente de verdad
- [x] 16 videos renderizados (10 semana 1 + 6 semana 2)
- [x] **Semana 1 subida completa (10/10)** — programados may 11-24
  - abraham-e-isaac · daniel-foso-leones · david-goliat · ester-y-el-rey
  - jonas · jose-y-sus-hermanos · moises · noe · sanson-y-dalila · pentecostes
- [x] `_CALENDARIO-SUBIDA.md` — tracking completo con YT IDs
- [x] Copy auditado: hooks corregidos (4 genéricos → narrativos), tags 14/video
- [x] batch_render.py · upload_schedule.py · upload_to_youtube.py — scripts completos
- [x] YouTube token auto-refresh (no requiere re-auth manual)

---

## 💡 Backlog

- [ ] Shorts pipeline: `render_short.py` con `data/oraciones_pool.json` (14 oraciones listas)
- [ ] Pin comment primera hora de cada video publicado (pregunta emocional)
- [ ] Responder comentarios primeras 24h (señal algoritmo)
- [ ] Resolve strike Oraciones Cortas (90 días o respuesta solicitante)
- [ ] Auditar canal: bajar videos con audio CapCut narrado
- [ ] V2 retención: cold open con clímax, dinámica musical por mood, end screen verbal

---

## 🔒 Bloqueado

- Strike Oraciones Cortas → esperar 90 días o respuesta del solicitante
