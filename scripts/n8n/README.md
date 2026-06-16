# Workflows n8n — Amplificación Cruzada VDD (anti-venom)

> Deploy: VPS `root@2.24.111.80`, `N8N_API_KEY_VPS` desde `/root/cero-agent/.env` (la primaria está muerta).
> Tokens FB/IG/YT desde `/root/cero-agent/.env` (Page = Palabra De Dios). NUNCA hardcodear.

## WF-1 — `vdd-short-to-3` (id `ZYC9kRoAgkMX7Tr2`) — **active**
Short YT → Reel FB + Reel IG, ambos con CTA al sleep long-form + Ko-fi.

- **Trigger:** Schedule cada 2h → GET `https://n8n.agenciacero.com.mx/media/shorts_push_manifest.json`.
- **Picker:** primer entry con `mp4_url` y no marcado en `/home/node/.n8n/vdd_reposted.json` (idempotente por `youtube_id`/`id`).
- **FB Reel:** `/video_reels` (start → upload hosted vía `upload_url` con header `file_url` → finish PUBLISHED).
- **IG Reel:** `/media` (media_type=REELS, video_url) → Wait 45s → `/media_publish`.
- **Log:** `/var/www/stats/actions.jsonl` + ping Telegram `@cero_ops_bot`.

### Contrato del manifest (lo llena la Mac post-upload de cada Short)
`https://n8n.agenciacero.com.mx/media/shorts_push_manifest.json`
```json
{
  "shorts": [
    {
      "id": "milagro_001",
      "youtube_id": "<id real cuando exista>",
      "hook": "¿Sientes que ya nada puede cambiar?",
      "titulo": "...",
      "mp4_url": "https://n8n.agenciacero.com.mx/media/short_<id>.mp4"
    }
  ]
}
```
**Paso Mac (post-render/upload):**
1. `scp output/shorts/.../short_<id>.mp4 root@2.24.111.80:/var/www/media/short_<id>.mp4`
2. Agregar el entry (con `mp4_url`) al manifest y re-subirlo a `/var/www/media/`.
   → en ≤2h el WF lo reposteará a FB+IG Reels.

> **Por qué un manifest y no poll YT:** Meta Reels exige un `video_url` público que pueda descargar. La API de YouTube NO devuelve el MP4, así que el Short se sirve desde `/var/www/media/` (nginx, mismo patrón que `/ig-images/`).

## WF-2 — auto-pin del comment funnel en cada Short nuevo — **NO construido (flag)**
Buildeable: el refresh del token YT funciona (scope `auth/youtube` full, incluye comments + setModerationStatus). Falta: decidir si el pin se ata a WF-1 (cuando el Short tenga `youtube_id`). Hoy WF-1 dispara por `mp4_url` que puede llegar antes del `youtube_id`. Pendiente de un trigger con `youtube_id` confirmado.

## WF-3 — `vdd-longform-push` (id `kaYFEkV6TThnH85M`) — **inactive (armado)**
Historia/sleep long-form → FB post (link YT) + comentario top en el video YT.

- **Trigger:** Schedule cada 3h → GET `https://n8n.agenciacero.com.mx/media/longform_push_manifest.json`.
- **Picker:** primer `youtube_id` con `publish_date <= hoy` no marcado en `/home/node/.n8n/vdd_longform_pushed.json`.
- **FB Post** + **Refresh YT Token** → **YT Top Comment** (commentThreads insert).
- **IG teaser:** NO incluido — requiere imagen teaser que hoy nadie genera (flag).
- State pre-sembrado con los 3 lofi (ya cubiertos por `lofi-push-vdd`, evitar dup FB).
- **Activar** cuando Fernando confirme el primer long-form a empujar (su identidad postea en YT).

### Contrato del manifest
```json
{ "videos": [ {
  "youtube_id": "xxxx", "youtube_url": "https://youtu.be/xxxx",
  "title": "...", "publish_date": "2026-06-20",
  "push_strategy": { "fb_post_copy": "...", "comentario_pinned": "..." }
} ] }
```
