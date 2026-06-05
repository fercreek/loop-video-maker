# Flywheel Operación de Dios — Ko-fi × YouTube × FB/IG × Email
> 2026-06-04 · Síntesis venom (diseño) + carnage (ejecución) · read sources: PLAN_MONETIZACION_ALTERNA_2026-06-04.md, SYNTHESIS.md, cero-agent/n8n-exports/

## 🎡 El diagnóstico (venom)

Hoy NO hay flywheel — hay **embudos sueltos**. Único cruce activo = `auto-publicador-vdd` (YT→FB/IG). El loop NO cierra porque el **email del que descarga el PDF se tira a la basura**. Sin email no hay flecha de retorno.

```
  [1] YOUTUBE (motor: Short r43LS0y0Wrg 324h/28d) ◄──────────────┐
        │ pinned comment + descripción → Ko-fi                   │
        ▼                                                        │
  [2] AUTO-POST FB+IG  (✅ ya existe auto-publicador-vdd)         │
        │ comment fija: link YT + Ko-fi                          │
        ▼                                                        │
  [3] KO-FI (PDF gratis live) → captura EMAIL  ◄── PIEZA FALTA   │
        ▼                                                        │
  [4] BEEHIIV (email = eje) 1 email/sem: devocional + link ──────┘
        recircula al video LARGO (sube watch hours = gate YPP)
```

## 🔍 Gap analysis — workflows VDD actuales (carnage confirmó: todos `active:true` en prod)

| Pieza flywheel | Workflow hoy | Gap |
|----------------|--------------|-----|
| YT→FB/IG cross-post | `auto-publicador-vdd` ✅ (fija comment con link YT) | **No incluye Ko-fi** |
| Comment CTA Ko-fi | `yt/fb/ig-comments-agent` ✅ (responden, tienen pin) | **Nunca insertan Ko-fi/email** |
| Captura email | — | ❌ **0 — el eje no existe** |
| Email semanal recircula | — | ❌ no hay newsletter WF |

Mitad izquierda del flywheel (publicar+engagear) = cubierta. Mitad derecha (Ko-fi→email→recircular) = **0%**.

## 🛠️ Los 4 workflows (orden de impacto)

| # | Acción | Tipo | Esfuerzo | Riesgo prod |
|---|--------|------|----------|-------------|
| **1** | MOD `auto-publicador-vdd`: insertar línea Ko-fi en `first_comment`/post | edit 1 nodo | XS | MEDIO (WF activo 3×/día — deploy `n8n-deploy` gated, ojo bug `localhost:8765` FOCUS-333) |
| **2** | MOD comment-agents: CTA Ko-fi rotado **1 de cada 3** (anti-spam) | edit pool | S | MEDIO (WF activos) |
| **3** | NEW `kofi-email-capture`: webhook Ko-fi → beehiiv API | WF nuevo aislado | M | bajo prod, **BLOCKED sin beehiiv** |
| **4** | NEW `weekly-devotional-email`: Claude genera devocional + link video largo → beehiiv | WF nuevo | M | depende de #3 + lista con subs |

#1+#2 = CTA sobre tráfico que YA fluye (alcance hoy). #3 = convierte embudo en rueda. #4 = flecha de retorno.

## 🚦 Secuencia con gates (carnage)

```
GATE 0 — Fernando UI (5min c/u): Super Thanks · Reels Bonus invite · Stars pin
PASO 1 — WF#1+#2 deploy n8n   ⛔ GATE C: Fernando aprueba prompt + apruebo deploy gated
PASO 2 — pinned comment Ko-fi top videos YT  ⛔ GATE B: aprueba lista + texto
PASO 3 — Fernando crea beehiiv  ← DESBLOQUEA el flywheel real
PASO 4 — WF#3 kofi-email-capture  ⛔ GATE D: beehiiv API key + Ko-fi webhook URL
PASO 5 — WF#4 weekly email (cuando lista tenga subs)
```

## ⚠️ Flags (carnage)
- 🔴 4 WF VDD activos — deploy SOLO via `n8n-deploy` (deactivate→PUT→activate→smoke). Nunca PUT a pelo.
- 🔴 Bug `localhost:8765` (FOCUS-333) en auto-publicador — fijar a `172.18.0.1:8765` en el mismo deploy o no tocar ese nodo.
- 🔴 YT OAuth compartido cero↔loop — no rotar.
- 🟡 CTA 1 de cada 3 comments (audiencia 35-55 valora "tiempo devocional", no venta).
- 🟡 Disclosure IA siempre.

## ✅ Cuello único: **beehiiv** (Fernando, 1-2h). Sin él, flywheel lineal.

---

## 📌 Estado 2026-06-04 (avance)

- **beehiiv creado** ✅ — publicación "Versículos de Dios". Publication ID: `46a515e4-3b0d-4d6f-a041-8d63845fbee3`.
- **WF#3 `kofi-email-capture` CONSTRUIDO + testeado** (parser local OK) → `cero-agent/n8n-exports/kofi-email-capture.json`. Listo-para-deploy.
- **BLOCKED en:** beehiiv exige Stripe Identity Verification (foto ID, acción de Fernando) para generar API key. La página se trabó — reintentar con ID en mano.

### WF#3 — 3 pasos para go-live (post-verificación)
1. **beehiiv API key** — Settings → API → Stripe Identity Verification (Fernando, ~5min con ID) → genera key.
2. **VPS .env** — agregar `BEEHIIV_API_KEY=...` + `KOFI_VERIFICATION_TOKEN=...` → `force-recreate` container → correr `n8n-env-audit`.
3. **Deploy + conectar Ko-fi:**
   - Importar `kofi-email-capture.json` a n8n (skill `n8n-deploy`, es WF NUEVO).
   - Copiar el webhook URL de n8n (`https://.../webhook/kofi-capture-vdd`).
   - Ko-fi → Settings → API/Webhooks → pegar URL + copiar el Verification Token a `KOFI_VERIFICATION_TOKEN`.
   - Test: Ko-fi → Send test → verificar subscriber aparece en beehiiv.

### WF#4 — pendiente (después de WF#3 + lista con subs)
`weekly-devotional-email`: Claude Haiku genera devocional + link video largo → enviar vía beehiiv. Cierra el retorno del flywheel.
