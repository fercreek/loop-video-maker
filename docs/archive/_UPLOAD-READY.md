# 📅 UPLOAD READY — VersiculoDeDios
> Generado: 2026-05-11
> 10 videos rendereados listos · Schedule 11-24 may · Pentecostés cae 24 may ⚡

---

## 🎯 Schedule de subida (calendario)

| # | Fecha | Día | Hora MTY | Prioridad | Historia |
|---|---|---|---|---|---|
| 1 | **2026-05-11** | lun | 18:00 | 🔴 P1 | Abraham e Isaac: La Prueba del Sacrificio |
| 2 | 2026-05-14 | jue | 18:00 | 🔴 P1 | Daniel en el Foso de los Leones |
| 3 | 2026-05-15 | vie | 18:00 | 🔴 P1 | David y Goliat: El Gigante que Cayó |
| 4 | 2026-05-16 | sáb | 18:00 | 🔴 P1 | Ester y el Rey Asuero |
| 5 | 2026-05-17 | dom | 18:00 | 🔴 P1 | Jonás y la Ballena |
| 6 | 2026-05-18 | lun | 18:00 | 🔴 P1 | José y sus Hermanos |
| 7 | 2026-05-21 | jue | 18:00 | 🔴 P1 | Moisés y el Éxodo |
| 8 | 2026-05-22 | vie | 18:00 | 🔴 P1 | Noé y el Diluvio |
| 9 | 2026-05-23 | sáb | 18:00 | 🔴 P1 | Sansón y Dalila |
| 10 | **2026-05-24** | dom | 18:00 | ⚡ Pentecostés | Pentecostés: El Fuego del Espíritu Santo |

**Lógica:** 6pm MTY = pico devocional (venom analytics). Días preferidos: jue/vie/sáb/lun/dom (evita mié/mar = engagement bajo). Pentecostés cae exactamente el día litúrgico.

---

## 📁 Archivos por historia (verificados)

Cada `output/stories/{id}/` contiene:
- ✅ `{id}.mp4` — video final (–14.18 LUFS, watermark, Ken Burns)
- ✅ `thumbnail.jpg` — 1280×720 Impact Bold + título stopword-skipped
- ✅ `yt_metadata.json` — chapters reales + tags ≤30 chars + título
- ✅ `yt_description.txt` — copy-paste a YT Studio
- ✅ `images/` — 11-18 imágenes Gemini (con personajes)

---

## 🚀 Comandos para subir

### Opción A: Auto via YouTube API
```bash
# Re-auth si token vencido
python3 scripts/yt_auth.py

# Subir TODO según schedule (1 video al día, queda private + publishAt)
python3 scripts/upload_to_youtube.py

# Solo el primero (test)
python3 scripts/upload_to_youtube.py --max 1

# Solo Pentecostés (preview)
python3 scripts/upload_to_youtube.py --story pentecostes
```

### Opción B: Manual (YT Studio)
1. Abre `output/stories/{id}/yt_description.txt` → copy
2. Sube el `.mp4` a YT Studio
3. Pega descripción, sube `thumbnail.jpg`
4. Schedule para fecha+hora del schedule arriba

---

## 📊 Estado de producción

```
Total catálogo:    100 videos planificados
─────────────────────────────────────────
✅ Subidos:           0   (acción pendiente)
🎬 Renderizados:    10   (LISTOS para subir HOY)
📝 Guion listo:      6   (renderizando ahora en batch background)
⏳ Pendientes:      84   (próximos sprints de generación)
```

---

## 📝 Scripts generados (sin renderizar aún)

**Batch en background** — al terminar tendrás +6 videos:
- Ruth y Noemí
- Hijo Pródigo
- Buen Samaritano
- Lázaro Resurrección
- Resurrección de Jesús
- Job (sufrimiento)

Comando: `python3 scripts/batch_render.py --max 6 --priority 3` (corriendo)

---

## 🎁 Próximas semanas — generar más scripts

Próximos 10 P1 sin script aún:
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

Para generar: lanza agentes Book Co-Author en sesión Claude Code (igual que hicimos hoy).

---

## ⚠ Pre-flight checklist antes de subir

- [ ] Revisar 1 video completo en QuickTime (escuchar audio + ver thumbnail)
- [ ] Verificar `data/yt_token.json` existe y vigente
- [ ] Confirmar título de cada video en `yt_metadata.json`
- [ ] Si subes manual: pega descripción exacta de `yt_description.txt`
- [ ] Pin comment en primera hora: pregunta emocional ("¿qué fue lo que más te impactó?")
- [ ] Responder TODOS los comentarios primeras 24h (señal algoritmo)

---

## 📈 KPIs primeras 4 semanas (objetivo venom)

- Visitas/video meta: 1,000-5,000 en 7 días
- Retención promedio: >40% (vs 30% típico canal)
- Conversión a subscribers: >3%
- Watch time acumulado para YPP: +500 hrs/28d
- Crecimiento subs: 11,700 → ~14,000-15,000

---

## 🔧 Backlog técnico (no bloquea subida)

- Sansón render timeout 25min — re-render OK la 2da vez (root cause: ¿Edge TTS lento?)
- YouTube upload automation requiere `data/yt_client_secrets.json` + re-auth
- Multi-format adapter (Shorts desde stories largas) — v3
- Auto-update FB/IG cuando se sube YT video — v3
