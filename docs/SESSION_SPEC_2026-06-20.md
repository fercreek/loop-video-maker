# SESSION SPEC 2026-06-20 — Continuar producción en la Mac potente
> Entry point para la PRÓXIMA sesión (otra Mac, más RAM, CPU anterior).
> Lee esto + `_NEXT.md` + `data/PLAN_MAESTRO_VD.md`. Cero historial de chat necesario.

---

## 🚀 ARRANQUE RÁPIDO (copy-paste en Mac B)
```bash
# 0. estar en el repo
cd ~/Documents/loop-video-maker && git pull

# 1. descomprimir el banco (AirDrop'd desde Mac A → ~/Downloads)
tar -xzf ~/Downloads/VD_BANCO_MacA.tar.gz     # secrets + guiones + fondos
tar -xf  ~/Downloads/VD_MUSICA_MacA.tar       # música cache

# 2. dependencias del sistema
brew install ffmpeg

# 3. entorno python
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 4. verificar YT (si da error de auth → re-login)
.venv/bin/python3 scripts/yt_stats.py || .venv/bin/python3 scripts/yt_auth.py
```
Si los 4 pasos corren limpio → **lista para producir.** Sigue con "QUÉ PRODUCIR" abajo.
Checklist de que el banco llegó: deben existir `config.json`, `data/yt_token.json`, `data/stories/*.json`, `output/fondos/*.jpg`, `audio/cache/`.

---

## 🎯 Qué vamos a hacer
Producir contenido long-form + reels NUEVO para subir watch-hours del gate YPP (4,000h long-form).
Esta Mac es la de generación pesada: **puede correr mflux (~9GB) y MusicGen sin RAM pressure** (la Mac vieja no podía). CPU anterior → ffmpeg por clip puede ir algo más lento, pero la generación de assets ya no swapea.

**El motor real (trazado venom):** el algoritmo empuja long-form fresco a los 14.3k subs + RELATED. NO es el formato. Producir fresco = combustible.

---

## ⚠️ SETUP en la Mac potente (ANTES de generar)

`git pull` trae el CÓDIGO pero `.gitignore` deja fuera secrets y assets. Hacer en orden:

### 1. Copiar a mano (NO están en git, no se regeneran)
Transferir vía AirDrop/USB/scp desde esta Mac:
- `config.json` (voces + keys)
- `data/yt_token.json` (OAuth YouTube) — o re-auth: `python3 scripts/yt_auth.py`
- `client_secret.json` (si re-auth)

### 2. venv + deps
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. mflux (para fondos nuevos) — si no está
La Mac potente es la que SÍ puede generar fondos. Verificar mflux + modelo FLUX en HF cache (~33GB). Si falta, instalar mflux en el venv (ver `docs/MFLUX_FONDOS.md`).

### 4. Assets — REGENERAR aquí (es la ventaja de esta Mac)
- Fondos: `python3 scripts/generate_fondos_mflux.py --count 2 --format 9:16` (reels) / `--format 16:9` (long-form)
- Música: MusicGen corre en `render_sleep.py` / `core/music_gen.py` al renderizar
- NO hace falta copiar `output/fondos` ni `audio/cache` de la Mac vieja — se generan aquí.

---

## ✅ Ya hecho (NO repetir — está en git)
- **Voz v3** (`core/narration_gen.py`): pitch -2Hz + pausas contemplativas. Aplica auto a todo render.
- **HOOK_STANDARD** (`docs/HOOK_STANDARD.md`): apertura hook-first obligatoria. Daniel 70% ret vs Ester 30% = la 1ª frase.
- **Plan reescrito** (`data/PLAN_MAESTRO_VD.md`): motor = sub-push, rotar 4 hooks, no matar sleep.
- **Optimización canal** ($0): playlists binge 100% · ~19 Shorts funnel.
- **18 historias + sleep YA están subidas.** NO re-subir. NO hay cola en disco.

---

## 📋 QUÉ PRODUCIR (pipeline en `data/historias_pipeline.json`)
Rotar 4 hooks. Lo genuinamente NUEVO (lo demás ya está live):
1. **`oracion_dormir_paz`** — "Oración Para Dormir en Paz 2026" (20min) — ataca SEARCH (única palanca que escala sin sub-push)
2. **`reflexion_dolor_proposito`** — "¿Por Qué Dios Permite el Dolor?" (15min) — tema validado (Short 4.9k views)
3. **Sleep nuevos** (venom #2): "SALMOS PARA DORMIR 2026 · 8 HORAS", "SALMO 91 PARA DORMIR 2026 · Toda la Noche" — 12x min/view. Probar 3h.
4. **Reels** (Shorts 9:16, bajo RAM): replicar fórmula `LLAMA DIVINA` (474 subs/1 short) → cross-post FB (alimenta umbral FB Content Monetization).

> 🔑 **TRUCO TÍTULOS — SEO futurista (outlier-analysis 06-22, replicabilidad 70-80%):** meter el AÑO FUTURO ("2026") en títulos de sleep/oración/música evergreen → novedad + posicionamiento de búsqueda anticipada. Visto en 2 outliers de competencia (1.1M + 568k views). Aplica SOLO a formato compilación/sleep/background — NO a historias narradas, NO a títulos de videos ya live.

---

## 🔒 ESTÁNDARES OBLIGATORIOS (gate de calidad)
Aplicar a TODO lo nuevo, en orden:
1. **Apertura hook-first** — pasar `docs/HOOK_STANDARD.md` ANTES de render (tensión en 1ª frase, no exposición lugar+tiempo).
2. **Loop carnage** — carnage-kill guion/visual → repair → `venom-design` thumbnail ≥9. No render raw.
3. **QA** — `scripts/qa_short.py` (reels, score ≥8) / `scripts/qa_longform.py` (long-form). No subir bajo score.
4. **Anti-dup** — ANTES de subir: confiar en `data/video_catalog.json` (`status.uploaded`), NO en match de títulos difuso. Normalizar acentos si cruzas. (Near-miss 06-20: subí 2 dups por "prodigo"≠"pródigo".)
5. **Supervisión** — Fernando revisa en QuickTime ANTES de subir. Nunca upload automático sin su OK.

---

## 🛠️ COMANDOS (flujo completo)

### Reels (Shorts 9:16 — ~1-2 min/reel, ~1-2GB RAM)
```bash
.venv/bin/python3 render_short.py --id <id> --voice dalia --force
.venv/bin/python3 scripts/qa_short.py output/shorts/semana_*/short_<id>_*.mp4   # score >=8
# Fernando revisa en QuickTime → si OK → upload
```

### Long-form historia (oración/reflexión — fondos reusados ~3GB, fondos nuevos ~9GB)
```bash
# 1. Escribir scene JSON en data/stories/<id>.json (aplicar HOOK_STANDARD en s01)
# 2. Render
.venv/bin/python3 render_story.py --id <id>           # historia/reflexión narrada
.venv/bin/python3 render_sleep.py --tema <tema> --duration 120   # sleep
# 3. QA
.venv/bin/python3 scripts/qa_longform.py output/sleep/<archivo>.mp4
# 4. Fernando revisa → upload supervisado
```

### Upload (SOLO tras review + anti-dup check)
```bash
# Agregar entry a data/upload_schedule.json (mp4_path, thumbnail_path, description_path, metadata_path, publish_at_utc)
echo "y" | .venv/bin/python3 scripts/upload_to_youtube.py --story <story_id> --yes
```

---

## 📌 Pendientes que necesitan esta Mac (de venom deep-dive)
- Generar oración guiada + reflexión (los 2 hooks nuevos) con voz v3 + hook-first + carnage.
- Sleep nuevos con títulos de búsqueda alta.
- Batch de reels estilo LLAMA DIVINA para FB.

## 📌 Pendientes manuales de Fernando (no requieren esta Mac)
- End screens historia→historia en Studio (apuntar a Rut/Daniel, mejor retención).
- Limpiar dup viejo: "VERSÍCULOS DE PROVISIÓN PARA DORMIR" aparece 2× (05-09).
- FB Content Monetization: form ENVIADO 06-20, en revisión de FB (esperar respuesta).
