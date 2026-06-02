# Carnage Execution Report — 2026-06-02
> Ejecutado por: carnage · Brief: brief-carnage-vd-2026-06-02.md
> Aprobación: Fernando 2026-06-02 (explícita en chat)

---

## Acción 1 — Stars Post FB (COMPLETADO)

**Status:** EJECUTADO

**post_id:** `452922677899760_122219066690553347`

**URL del post:** https://www.facebook.com/permalink.php?story_fbid=122219066690553347&id=452922677899760

**Copy publicado:** Exacto al brief — sin modificaciones.

**Pin:** BLOQUEADO via API (error 100: insufficient permissions con page access token).
El endpoint `POST /{post-id}` con `is_pinned=true` requiere permisos adicionales que el token de Agencia Cero no tiene.

**Acción manual requerida (2 clicks):**
1. Abrir https://www.facebook.com/palabradedios111
2. Ir al post publicado hoy
3. Click en "..." del post → "Fijar en inicio de página"

---

## Acción 2 — Meta Ads Campaña Page Likes (PARCIALMENTE COMPLETADO — blocker en ad creative)

### Objetos creados (todos en status PAUSED — NADA gasta dinero aún)

| Objeto | ID | Nombre |
|--------|-----|--------|
| Custom Audience (seed fans) | `120245942980230194` | VD-PageFans-Seed-2026-06-02 |
| Lookalike 1% MX | `120245943055860194` | VD-LAL1pct-MX-PageFans-2026-06-02 |
| Campaña | `120245943071430194` | VD-PageLikes-LAL1pct-Jun2026 |
| Adset | `120245943144590194` | VD-LAL1pct-MX-CO-PageLikes-$200MXN-Jun10 |
| Imagen subida | hash `2467b87819cea8cc51685fc7c65fa315` | thumb_v01_dormir_v4.jpg (1280x720) |

### Parámetros del adset confirmados

- Objetivo: OUTCOME_ENGAGEMENT → PAGE_LIKES
- Budget: $1,400 MXN lifetime (= $200/día × 7 días)
- Start: 2026-06-10 14:00 UTC (= 8am MTY)
- End: 2026-06-17 14:00 UTC
- Audiencia: LAL 1% MX desde fans de página 452922677899760
- Geo adset: MX + CO, age 25-55
- Bid strategy: LOWEST_COST_WITHOUT_CAP
- Status: PAUSED (no activo)

### Blocker — Ad Creative NO creado

**Error:** `error_subcode=1885183` — "Ads creative post was created by an app that is in development mode. It must be in public to create this ad."

**Causa raíz:** El ads token disponible pertenece a la app **Studio Link** (`app_id: 890432170517552`), que está en modo development. Meta bloquea la creación de ad creatives con apps en ese estado.

**Fix requerido (Fernando):**
1. Ir a https://developers.facebook.com/apps/890432170517552/review
2. Completar App Review → publicar la app a modo Live
   - O bien: crear un nuevo token con la app Agencia Cero (que ya está en modo live) con scopes `ads_management + ads_read`
3. Con el token correcto, ejecutar el siguiente comando para completar el creative + ad:

```bash
# Parámetros listos para ejecutar cuando tengas el token correcto:
# account_id: act_10157137032586982
# campaign_id: 120245943071430194
# adset_id: 120245943144590194
# image_hash: 2467b87819cea8cc51685fc7c65fa315
# page_id: 452922677899760

python3 - <<'EOF'
import urllib.request, urllib.parse, json

NEW_TOKEN = 'PONER_TOKEN_AQUI'  # token de app en modo live con ads_management
ACT_ID = 'act_10157137032586982'

# Step 1: crear creative
creative_data = {
    'name': 'VD-PageLikes-Creative-MusicaDormir-Jun2026',
    'object_story_spec': json.dumps({
        'page_id': '452922677899760',
        'link_data': {
            'image_hash': '2467b87819cea8cc51685fc7c65fa315',
            'link': 'https://www.facebook.com/palabradedios111',
            'message': '2 horas de música tranquila y versículos de paz. Sin anuncios. Gratis en YouTube.',
            'name': 'Música para dormir y relajar la mente',
            'call_to_action': {'type': 'LIKE_PAGE', 'value': {'page': '452922677899760'}}
        }
    }),
    'access_token': NEW_TOKEN
}
data = urllib.parse.urlencode(creative_data).encode('utf-8')
req = urllib.request.Request(f'https://graph.facebook.com/v19.0/{ACT_ID}/adcreatives', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
with urllib.request.urlopen(req) as resp:
    creative = json.loads(resp.read().decode())
    print('Creative ID:', creative['id'])

creative_id = creative['id']

# Step 2: crear ad
ad_data = {
    'name': 'VD-PageLikes-LAL1pct-MusicaDormir-Jun10',
    'adset_id': '120245943144590194',
    'creative': json.dumps({'creative_id': creative_id}),
    'status': 'PAUSED',
    'access_token': NEW_TOKEN
}
data2 = urllib.parse.urlencode(ad_data).encode('utf-8')
req2 = urllib.request.Request(f'https://graph.facebook.com/v19.0/{ACT_ID}/ads', data=data2, method='POST')
req2.add_header('Content-Type', 'application/x-www-form-urlencoded')
with urllib.request.urlopen(req2) as resp2:
    ad = json.loads(resp2.read().decode())
    print('Ad ID:', ad['id'])
EOF
```

**Alternativa rápida (sin código):**
Carnage ya tiene campaña + adset creados. En Ads Manager:
1. Abrir https://adsmanager.facebook.com/adsmanager/manage/ads?act=10157137032586982
2. Buscar campaña "VD-PageLikes-LAL1pct-Jun2026"
3. Ir al adset → crear ad manualmente con los mismos parámetros de copy e imagen

---

## Notas adicionales

### LAL 1% — nota técnica sobre el seed
La audiencia seed fue creada con `subtype=ENGAGEMENT` (fans actuales via `page_liked` event). El LAL se creó solo para MX porque Meta requiere ≥100 personas del país target en el seed — con `allow_international_seeds=true` acepta el seed global. Colombia quedó solo en el geo filter del adset (targeting), no en el LAL propiamente. Esto es behavior normal de Meta y no afecta la calidad de la audiencia para LATAM.

### Stars post — alcance esperado
El post orgánico está publicado pero no pineado (acción manual de 2 clicks pendiente). Sin pin, el post vivirá en el feed normal y verá alcance orgánico según el engagement que genere. Pinear = máxima visibilidad.

---

## Checklist para cerrar el loop (acciones pendientes Fernando)

- [ ] **AHORA ($0, 2 clicks):** Pinear post Stars en FB Page — https://www.facebook.com/palabradedios111
- [ ] **Esta semana (1 acción):** Publicar la app Studio Link a modo Live (developers.facebook.com) O generar token de Agencia Cero con ads_management — para poder crear el ad creative y completar la campaña
- [ ] **Jun 10 (1 click):** Activar campaña "VD-PageLikes-LAL1pct-Jun2026" en Ads Manager una vez el creative esté creado

---

## Para venom — loop de aprendizaje

Objetos creados y listos en el ad account:
- Seed audience `120245942980230194` — reutilizable para futuras campañas
- LAL 1% MX `120245943055860194` — reutilizable
- Campaña + adset configurados para Jun 10 — solo falta creative + activación
- Imagen lofi subida al ad account (hash `2467b87819cea8cc51685fc7c65fa315`) — disponible

El blocker es de token/app, no de estrategia ni de plataforma. Una vez resuelto el token, la campaña puede estar live en <5 minutos.
