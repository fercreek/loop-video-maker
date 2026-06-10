# Síntesis 3 simbiontes — Plan orgánico VD (2026-06-09)

> venom (estrategia) + carnage (red-team) + anti-venom (infra). Análisis a fondo del plan.
> **Tesis del cruce:** pulimos CONTENIDO sobre una capa de instrumentación/salud rota. Hay que arreglar el cimiento (token, medición, guard) antes/junto con el contenido.

---

## 🔴 P0 — muerden YA (cimiento roto)

### P0-1 · YT engagement MUERTO hace 27 días (anti-venom) — el hallazgo clave
`yt-comments-agent` reporta "success" cada 15min, pero `YOUTUBE_TOKEN_EXPIRY=2026-05-14` (hace 27d). El token expiró, el 401 se traga, marca verde. **El engagement de YouTube lleva ~1 mes sin postearse y nadie se enteró.**
- Doble golpe: el plan iba a meter el link-funnel (C4) en ESTE workflow muerto → habría fallado silencioso también.
- **Fix:** (a) re-auth del token YT (Fernando, OAuth), (b) nodo HTTP YT → `onError: stopWorkflow` para que el 401 dispare el error-workflow → alerta `@cero_ops_bot`, (c) cron de refresh proactivo cada 5d (testing-mode caduca a 7).

### P0-2 · La medición del loop es humo (venom H7 + carnage #4 + anti-venom §3)
`daily-stats-vdd` cuenta *acciones ejecutadas*, no *engagement recibido*. YT no da clics de links en comentarios. **El loop venom-nexo NO puede confirmar ninguna hipótesis** (¿el copy subió 4→50 likes? nadie lo sabe).
- **Fix (anti-venom design):** cron VPS "Métricas VD" cada 6h → jala Graph API por-post (likes/comments/shares/reach) + YT Analytics por-video → appendea series temporales a `/var/www/stats/engagement.jsonl`. venom lee eso para medir el loop REAL. Series por post (6h/24h/72h), no totales.

### P0-3 · Guard de uploads huérfanos (carnage #2 + anti-venom §4)
Lo que causó el incidente de hoy (2 TikToks ajenos colados 2 semanas).
- **Fix (anti-venom design):** cron VPS 1×/día → YT API lista uploads del canal − tracking local (`upload_schedule.json` + `lofi_push_plan.json`) = huérfanos → alerta `@cero_ops_bot`. Detecta el caso exacto: algo subió que el sistema no programó. VPS, no Mac (la regla: prod no depende de Mac encendida).

### P0-4 · IDs duplicados — ✅ RESUELTO HOY
3 exports compartían `XPWXiyjraNgqSODn` (diferían 107 y 931 líneas — peligro real de revert). Archivados a `n8n-exports/archived/`. Fuente de verdad única = `auto-publicador-vdd.json`.

---

## 🟠 Reorden estratégico (venom) — el plan optimiza vanity, no el gate ni el $

| Hallazgo | Acción |
|---|---|
| **Funnel mal anclado** — sleep 2h ret 10.8% quema tráfico | Apuntar funnel (C3+C4) a **Rut y Noemí `HeGUMgQlfFo` ret 25%**, no al sleep 2h. Sleep = secundario hasta arreglar intro. |
| **Motor B (Ko-fi+email) sin shippear = cuello del 1er dólar** | El link Ko-fi del C4 va a página vacía. Shippear lead magnet PDF + beehiiv ANTES que los cosméticos FB. |
| **Playlists binge = palanca YPP gratis** fuera del batch | Cambio 0 (5 min, Fernando, sin deploy): agregar sleep 2h + Rut a sus playlists binge. |
| **"Lunes mejor día" = supuesto sin data** | Medir day-of-week en próximo venom o marcar como hipótesis. No anclar el ritual ahí. |
| **Conversor "revelación/reframe/hook-25s" 12.9×** enterrado en Fase 2 | Sacar a producción semanal como 3 plantillas de Short — es la materia prima del funnel. |

**Reorden ROI venom:** 1) playlists binge · 2) Motor B mínimo · 3) funnel→Rut (C3+C4 corregidos) · 4) plantillas Short · 5-7) retiming/copy/cross-post FB (vanity, al fondo).

---

## 🟡 Otros fixes

- **Doble-key .env** (anti-venom pick): sobrescribir `N8N_API_KEY` con el valor válido de `N8N_API_KEY_VPS`, borrar la stale. Backup→prod, necesita OK.
- **yt-comments getDay() UTC bug** (carnage): rotación de CTA usa día UTC, no MX.
- **C5 cross-post async frágil** (carnage): polling REELS puede quedar stuck IN_PROGRESS, video_url debe ser público.
- **Health-gate + smoke-test deploys** (anti-venom): el skill `n8n-deploy` debe probar la key (curl→200) antes del PUT + disparar 1 exec post-deploy y verificar terminal-reach.

---

## Loop venom-nexo — veredicto
**Conservar el contrato de brief (es oro).** Cambiar cadencia de "semanal fija" a **event-driven** (venom H7): disparar al subir long-form o al cerrar ventana de hipótesis, no "es lunes". Y NO puede medir nada hasta que exista `engagement.jsonl` (P0-2).

---

## Orden de ejecución corregido

1. **P0-1** YT token re-auth + silent-success fix (engagement YT muerto 1 mes)
2. **P0-2** colector `engagement.jsonl` (sin esto el loop no mide)
3. **P0-3** guard huérfanos (previene próximo incidente)
4. **Cambio 0** playlists binge (5 min, ROI/esfuerzo máximo)
5. **Motor B mínimo** Ko-fi lead magnet + beehiiv (1er dólar)
6. **Funnel→Rut** (C3+C4 corregidos, tras arreglar P0-1)
7. Doble-key .env + getDay bug (quick fixes)
8. Cosméticos FB (retiming/copy ya deployados; cross-post C5 al fondo)
