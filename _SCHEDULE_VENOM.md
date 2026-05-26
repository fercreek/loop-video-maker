# 📅 Schedule Venom — Living Spec

> Source of truth: `data/shorts_schedule.json` (machine-readable)
> Update: auto desde `scripts/upload_shorts_venom.py` (YT+FB) y `scripts/ig_daemon.py` (IG)
> Última sync: 2026-05-25 16:30

---

## Plan maestro

- **Total:** 20 Shorts venom
- **Cadencia:** 1/día
- **Hora:** 5:00 AM MTY (UTC-6) → 11:00 UTC
- **Ventana:** May 26 → Jun 14 (20 días)
- **Plataformas:** YouTube + Facebook + Instagram (3 canales)

---

## Tabla maestro — Status por día

Convención: ✅ subido / 🕐 programado / ❌ pendiente / ⚠️ error

| # | Fecha MTY | ID | Voz | Título | YT | FB | IG | Notas |
|---|-----------|-----|-----|--------|-----|-----|-----|-------|
| 1 | 2026-05-26 05:00 | venom_001 | Dalia | 🕊️ Reposo Profundo · #Paz | 🕐 cPnxbjtH9xQ | ✅ 1701988177657353 | ❌ | FB ya publicado |
| 2 | 2026-05-27 05:00 | venom_004 | Dalia | 🕊️ PAZ que SOBREPASA · #Filipenses4 | 🕐 Rt8Q-D1LJpk | ❌ | ❌ | |
| 3 | 2026-05-28 05:00 | venom_009 | Jorge | ⚔️ MIEDO VENCIDO · #Autoridad | 🕐 GFlD5gfxHkY | ❌ | ❌ | |
| 4 | 2026-05-29 05:00 | venom_002 | Jorge | 🔥 NUEVA CRIATURA · #Identidad | 🕐 ynG3d1IOYwg | 🕐 1701988177657353 | ❌ | |
| 5 | 2026-05-30 05:00 | venom_005 | Dalia | 🛡️ REFUGIO SECRETO · #Salmo91 | 🕐 1cN9Xu9dfWU | 🕐 2270533757047867 | ❌ | |
| 6 | 2026-05-31 05:00 | venom_010 | Dalia | 🌿 ANSIEDAD se VA · #Calma | 🕐 4oRb1kQgpGg | ❌ | ❌ | |
| 7 | 2026-06-01 05:00 | venom_007 | Dalia | 🙏 SANACION Profunda · #Esperanza | 🕐 6SHFkTJE4V4 | ❌ | ❌ | |
| 8 | 2026-06-02 05:00 | venom_013 | Dalia | 💎 GRACIA INFINITA · #Cruz | ❌ | ❌ | ❌ | YT quota wait |
| 9 | 2026-06-03 05:00 | venom_018 | Jorge | ✝️ LA CRUZ · #Salvacion | ❌ | ❌ | ❌ | YT quota wait |
| 10 | 2026-06-04 05:00 | venom_006 | Dalia | 🕊️ PERDON Total · #Sanacion | ❌ | ❌ | ❌ | YT quota wait |
| 11 | 2026-06-05 05:00 | venom_014 | Dalia | ❤️ AMOR de DIOS · #1Juan4 | ❌ | ❌ | ❌ | YT quota wait |
| 12 | 2026-06-06 05:00 | venom_015 | Jorge | 🔥 FE que MUEVE · #Hebreos11 | ❌ | ❌ | ❌ | YT quota wait |
| 13 | 2026-06-07 05:00 | venom_011 | Jorge | 🎯 PROPOSITO ETERNO · #Llamado | ❌ | ❌ | ❌ | YT quota wait |
| 14 | 2026-06-08 05:00 | venom_019 | Jorge | ⚡ RESURRECCION DIARIA · #Romanos6 | ❌ | ❌ | ❌ | YT quota wait |
| 15 | 2026-06-09 05:00 | venom_008 | Jorge | 💰 PROVISION DIVINA · #Confianza | ❌ | ❌ | ❌ | YT quota wait |
| 16 | 2026-06-10 05:00 | venom_003 | Jorge | 💪 CARGA LIGERA · #Mateo11 | ❌ | ❌ | ❌ | YT quota wait |
| 17 | 2026-06-11 05:00 | venom_012 | Dalia | ✨ ESPERANZA REAL · #TiempoDios | ❌ | ❌ | ❌ | YT quota wait |
| 18 | 2026-06-12 05:00 | venom_016 | Dalia | 🙏 ORACION REAL · #Relacion | ❌ | ❌ | ❌ | YT quota wait |
| 19 | 2026-06-13 05:00 | venom_017 | Jorge | 🕊️ ESPIRITU SANTO · #Guia | ❌ | ❌ | ❌ | YT quota wait |
| 20 | 2026-06-14 05:00 | venom_020 | Jorge | 🏠 FAMILIA RESTAURADA · #Generaciones | ❌ | ❌ | ❌ | YT quota wait |

---

## Pipeline upload por plataforma

### YouTube
- Script: `scripts/upload_shorts_venom.py`
- Mode: `private` + `publishAt` ISO timestamp
- Quota: ~6 uploads/día default. Reset midnight PT
- Re-corrida segura: skip auto IDs ya OK

### Facebook (Página Palabra De Dios)
- Mismo script
- Mode: `scheduled_publish_time` UNIX timestamp
- Min 10 min futuro, máx 6 meses
- Algunos errores 429 esporádicos — script retry next day

### Instagram (@palabradedios111)
- Script: `scripts/ig_daemon.py` (background daemon)
- Mode: API no soporta scheduling nativo → daemon publica AT target time
- Frecuencia: chequea cada 10 min
- **Catch-up:** si Mac estuvo off cuando llegó hora target, publica al despertar (con flag `late=true`)
- Logs: `logs/ig_daemon.log`

---

## Estado consolidado

| Métrica | Conteo |
|---------|--------|
| YT scheduled | 7 / 20 |
| YT pendientes | 13 |
| FB scheduled | 3 / 20 |
| FB ya publicado | 1 (venom_001) |
| FB pendientes | 16 |
| IG pendientes | 20 |

---

## Acciones próximas

1. ✅ **Mañana 2am MTY:** launchd dispara `upload_shorts_venom.py` → sube 13 YT + 17 FB pendientes
2. ⏳ **Setup ig_daemon:** instalar launchd LaunchAgent que corra cada 10 min
3. ⏳ **Manual verificación día 1 (May 26 5am):** confirmar venom_001 publicó en YT+FB+IG

---

## Cómo se actualiza este doc

- **Auto desde Python:** `scripts/sync_schedule_md.py` (TO BE BUILT) lee `data/shorts_schedule.json` + IG state → regenera tabla
- **Manual:** editar este archivo + tabla `_SCHEDULE_VENOM.md`
- **Trigger:** después de cada exitoso upload los scripts deben llamar `sync_schedule_md.py`
