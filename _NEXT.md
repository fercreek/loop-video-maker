# _NEXT — loop-video-maker (VersiculoDeDios)
> Update: 2026-05-06 · Canal: @VersiculoDeDios-v1u · 11,517 subs (+2.1K/28d)

---

## ⚡ En proceso (retomar aquí)

- [ ] Render semana corriendo: `bi1jukqor` (sanacion/salmos/provision) + `bqbitq4xm` (paz/fe) → `output/semana_2026-05-06/`
- [ ] Re-auth YouTube token → `python3 scripts/yt_auth.py` (expiró Apr 27)
- [ ] Subir 2 videos/día mié–dom → ver `_SEMANA_2026-05-07.md`

---

## 📦 v4.0 (2026-05-06) — CURRENT

### Cambios principales
| Componente | Cambio | Resultado |
|---|---|---|
| **Audio** | MusicGen stereo-small para Esperanza/Sanación/Salmos | Sin duplicados → sin ContentID risk |
| **Fondos** | +40 Gemini Imagen 4.0 (bíblicos) → pool 93 | Sin repetición en 120min |
| **Texto** | 58px → 72px verso · 26→30px ref | Legible en mobile |
| **Cache audio** | `audio/cache/{hash}.wav` + `_norm.aac` | Mux 6min → 5s en re-renders |
| **Manifest** | Duplicados eliminados: Esperanza/Sanación/Salmos | Audio genuinamente único |
| **render_120min.py** | `--output-dir`, `--themes`, `--force`, `--skip-qgate` | Flexible por semana |
| **youtube_client.py** | Handle correcto + channel_id en config.json | Stats listos tras re-auth |

### Scripts nuevos v4.0
- `scripts/generate_mood_tracks.py` — tracks MusicGen por mood
- `scripts/generate_fondos_ai.py` — fondos bíblicos Gemini Imagen 4.0
- `scripts/yt_stats.py` — dashboard analytics (necesita re-auth)

### Workflow semanal
```bash
# 1. Generar videos de la semana (temas elegidos por analytics)
python3 render_120min.py --themes [temas] --output-dir output/semana_YYYY-MM-DD --skip-qgate

# 2. Ver métricas (tras re-auth)
python3 scripts/yt_stats.py

# 3. Generar más fondos si se agotan
python3 scripts/generate_fondos_ai.py --count 20

# 4. Generar tracks MusicGen para moods con loops cortos
python3 scripts/generate_mood_tracks.py --mood "Gloria" "Júbilo" --duration 300
```

---

## 💡 Backlog

- [ ] Loops cortos pendientes: Gloria(124s), Júbilo(150s), Meditación(91s), Quietud(81s), Silencio(127s) → `generate_mood_tracks.py`
- [ ] Shorts/Reels: cortar versículo destacado 9:16 60s de cada video
- [ ] Resolver copyright strike "Muerte Vencida" — 1 de 3 infracciones activa
- [ ] `pip install google-genai` → habilitar Gemini Lyria para música generativa
- [ ] Thumbnail v2: usar fondos AI como base (mayor impacto visual)

## ✅ Ready

- Ver `_SEMANA_2026-05-07.md` para orden y títulos de subida

## 🔒 Bloqueado

- `yt_stats.py` → `python3 scripts/yt_auth.py` (requiere browser)
- Strike "Muerte Vencida" → revisar qué audio causó el claim
