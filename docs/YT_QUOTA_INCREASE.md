# YouTube API Quota Increase — Plan

> Status: pending (decisión Fernando: hacer después)
> Última actualización: 2026-05-25

---

## Datos del proyecto

| Campo | Valor |
|-------|-------|
| Project ID | `versiculos-de-dios-youtube` |
| Project Number | `449814655542` |
| Client ID | `449814655542-m64ukgkfq1lq2fl1j3c6m53gsgkpe4kc.apps.googleusercontent.com` |
| Channel | VersiculoDeDios (@versiculodedios-v1u) |
| Channel URL | https://youtube.com/channel/UC2l5TZjHzRtaRjH8kT_yQ2w |
| Subs (May 2026) | 12,700 |
| Total videos | 1,059 |
| Total views | 1,002,165 |
| Country | MX |
| Created | 2024-10-06 |

## Form URL

https://support.google.com/youtube/contact/yt_api_form

## Quota actual y solicitada

- **Actual:** 10,000 units/día (default)
- **Solicitada:** 300,000 units/día (~180 uploads/día capacity)
- **Costo upload:** `videos.insert` 1,600 + `thumbnails.set` 50 = 1,650/video

## Respuestas form

| Pregunta | Respuesta |
|----------|-----------|
| Service | YouTube Data API v3 |
| Project ID | versiculos-de-dios-youtube |
| Quota requested | 300,000 units/day |
| In-scope APIs | videos.insert, thumbnails.set, channels.list, search.list (read-only stats) |
| Out-of-scope | NO scraping, NO data resale, NO third-party use |

## Justification (campo grande)

```
We operate VersiculoDeDios, a Spanish-language Christian devotional channel
(@versiculodedios-v1u, 12,700 subs, 1M+ views, 1,059 videos since Oct 2024).
We publish 3-5 short-form devotional content daily plus 1-2 long-form
relaxation/sleeping videos per week.

Current default quota of 10,000 units/day limits us to ~6 uploads/day, which
constrains our publishing cadence and prevents us from launching consistent
multi-platform batches (we cross-post to Facebook and Instagram via Meta
Graph API on the same schedule).

We request 300,000 units/day to enable:
- ~180 uploads/day capacity (vs current 6)
- Batch uploads for weekly content drops
- Reliable scheduled publishing across our 20-day content calendars

All content is original (rendered locally with FFmpeg, audio via MusicGen,
voice via Microsoft Edge TTS — anti-strike compliant). We do not scrape,
resell data, or use the API for purposes beyond our own channel management.

Compliance: full YouTube ToS adherence documented in internal anti-strike
ruleset.
```

## Cuándo enviar form

- Cuando Fernando esté listo (no urgencia inmediata — daemon resuelve batch actual en 3 días)
- Antes de próximo batch de 15+ videos (evitar mismo cuello de botella)

## Después de enviar

- Email a `fercreek@gmail.com` con resultado en 2-7 días
- Pueden pedir info adicional → responder rápido (24h evita escalada)
- Si rechazan: pedir reconsideración con datos adicionales (engagement, growth %, monetization plan)
