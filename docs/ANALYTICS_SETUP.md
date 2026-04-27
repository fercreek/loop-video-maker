# Analytics Setup — YouTube Data API v3
**Canal:** @VersiculoDeDios · `UC2l5TZjHzRtaRjH8kT_yQ2w`

---

## Estado actual

Sin acceso a datos estructurados de YouTube Analytics desde el sistema.
YouTube Studio solo disponible vía browser manual.

Este doc describe cómo conectar YouTube Data API v3 para que Claude pueda
leer métricas directamente desde el proyecto.

---

## Qué se puede obtener

### YouTube Data API v3 (metadata + básicos)
- Lista de videos del canal (títulos, IDs, fechas)
- Thumbnails actuales
- Descripción, tags por video
- Conteo público: views, likes, comentarios

### YouTube Analytics API (métricas reales)
Requiere cuenta con permisos de propietario:
- **Views** por video y período
- **Watch time** (horas) — crítico para monetización
- **Average view duration** y **% retention**
- **CTR** (impresiones → clics)
- **Traffic sources** (búsqueda, sugeridos, externo)
- **Audience demographics** (país, edad, género)
- **Revenue** (si está monetizado)

---

## Setup (una sola vez, ~15 min)

### Paso 1 — Google Cloud Console
1. Ir a https://console.cloud.google.com/
2. Crear proyecto nuevo: "fea-analytics" (o usar uno existente)
3. Activar APIs:
   - **YouTube Data API v3**
   - **YouTube Analytics API**
4. Ir a "Credentials" → "Create credentials" → **OAuth 2.0 Client ID**
5. Application type: **Desktop app**
6. Descargar el JSON → guardarlo como `client_secret.json` en la raíz del proyecto

> `client_secret.json` está en `.gitignore` — nunca se sube a git.

### Paso 2 — Primera autenticación
```bash
.venv/bin/pip install google-auth google-auth-oauthlib google-api-python-client
.venv/bin/python3 scripts/yt_auth.py
```

Abre browser → autorizar con tu cuenta Google propietaria del canal → guarda token en `data/yt_token.json`.

### Paso 3 — Verificar
```bash
.venv/bin/python3 scripts/yt_stats.py --channel-info
```

Debe mostrar: nombre del canal, subs, total views.

---

## Archivos del módulo analytics (por crear)

```
scripts/
├── yt_auth.py          ← OAuth flow, guarda token
├── yt_stats.py         ← CLI: stats por video, canal, período
└── yt_report.py        ← genera docs/ANALYTICS_REPORT.md

core/
└── youtube_client.py   ← wrapper reutilizable (lista videos, get analytics)
```

---

## Datos que Claude puede leer una vez conectado

```python
# Ejemplo de uso desde Claude en este proyecto:
from core.youtube_client import get_channel_videos, get_video_analytics

videos = get_channel_videos(channel_id="UC2l5TZjHzRtaRjH8kT_yQ2w")
# → lista de {id, title, published_at, view_count, like_count}

analytics = get_video_analytics(video_id="abc123", days=30)
# → {views, watch_time_hours, avg_view_duration_sec, ctr, impressions}
```

---

## Report automático semanal

Una vez conectado, se puede programar un reporte semanal:
```bash
# Cada lunes — genera docs/ANALYTICS_REPORT.md con métricas de la semana
.venv/bin/python3 scripts/yt_report.py --days 7 --output docs/ANALYTICS_REPORT.md
```

El reporte incluiría:
- Top 5 videos por views (últimos 7 días)
- Video con mejor CTR thumbnail
- Video con mejor watch time %
- Comparativo semana anterior
- Recomendación de qué thumbnail A/B probar

---

## Alternativa sin setup: YouTube Studio manual

Si no quieres configurar OAuth:
1. Abre https://studio.youtube.com/channel/UC2l5TZjHzRtaRjH8kT_yQ2w/analytics
2. Comparte screenshot con Claude
3. Claude extrae datos del screenshot y genera análisis

Esta opción funciona ahora mismo sin ningún setup adicional.

---

## Acceso actual desde Claude (browser)

Claude puede abrir YouTube Studio vía computer-use o Chrome MCP:
- **Chrome MCP** — si la extensión está conectada en Chrome
- **Computer use** — siempre disponible, screenshots de pantalla

Limitación: datos no estructurados (solo lo que aparece en pantalla), no se pueden exportar a CSV ni procesar programáticamente.

---

## Checklist de activación

- [ ] Crear proyecto en Google Cloud Console
- [ ] Activar YouTube Data API v3 + YouTube Analytics API
- [ ] Crear OAuth 2.0 Client ID (Desktop app)
- [ ] Descargar `client_secret.json` → colocar en raíz del proyecto
- [ ] Correr `yt_auth.py` para generar token
- [ ] Crear `core/youtube_client.py` con funciones básicas
- [ ] Crear `scripts/yt_stats.py` para CLI rápido
- [ ] Primer reporte manual para validar datos

Tiempo estimado desde cero con Claude: ~30 min.
