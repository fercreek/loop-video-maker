# Contexto FB + IG — Versículos de Dios
> Este repo (loop-video-maker) es el repo principal de VD.
> Videos largos + Shorts aquí. Imágenes FB/IG tienen su propio pipeline documentado abajo.

---

## Cuentas activas

| Plataforma | Cuenta | ID API |
|------------|--------|--------|
| YouTube | @VersiculoDeDios-v1u | `UC2l5TZjHzRtaRjH8kT_yQ2w` |
| Facebook | Palabra De Dios | `452922677899760` |
| Instagram | @palabradedios111 | `17841469453382962` |
| Metricool | blogId `5906079` | Solo para videos |

---

## Pipeline de imágenes FB + IG (automatizado)

**Repo:** `~/Documents/context/assets/versiculos/`  
**Brand guidelines:** `~/Documents/context/content/brand-guidelines/versiculos-de-dios.md`

### Publicación automática (launchd)
- Horario: **9am · 1pm · 7pm MTY** — dispara solo, Mac encendida o no
- Script: `~/Documents/context/assets/versiculos/schedule_vd.py --publish-now`
- FB y IG publican **simultáneamente**
- Anti-duplicados: `published.json` (nunca subir dos veces la misma imagen)
- Log: `/tmp/versiculos_publish.log`

### Generar imágenes nuevas (cada semana)
```bash
cd ~/Documents/context/assets/versiculos

# Pillow v3 (rápido, gratis) — agregar versículos en VERSES del script
python3 gen_fb_pillow_v3.py        # output: fb-feed-v3/

# Gemini AI (oleo religioso) — para variedad premium
python3 gen_fb_gemini.py           # output: fb-feed-gemini/

# Publicar batch
python3 schedule_vd.py --dry-run   # revisar primero
python3 schedule_vd.py             # publicar (confirmar con Fernando)
```

### Token permanente
- Archivo: `~/Documents/cero/cero-content/scripts/configs/tokens.json` → key `"palabra-de-dios"`
- **Nunca expira** — no hay que renovar
- App: Agencia Cero (1265193065810940)

---

## Metricool — SOLO videos

Metricool (`blogId: 5906079`) se usa EXCLUSIVAMENTE para programar videos.  
Las imágenes van por `schedule_vd.py` — no usar Metricool para imágenes.

---

## Reglas de contenido

- **3 posts/día:** 9am · 1pm · 7pm MTY
- Imágenes: 1080×1080 · paleta sepia cálida (ver brand guidelines)
- Captions: versículo corto + referencia + 3-5 hashtags base `#PalabraDeDios #Fe #Biblia`
- NO duplicar versículos — revisar `published.json` y brand guidelines (sección "Versículos usados")

---

## Análisis de métricas

Después de cada batch semanal → `@agent venom` en Claude Code → solo lectura  
Recordatorio programado en calendario: Mayo 12, 9am

---

## Guía técnica completa

`~/Documents/context/notes/meta-api-publishing-guide.md` — errores comunes, tokens, BM setup
