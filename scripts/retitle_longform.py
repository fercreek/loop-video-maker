#!/usr/bin/env python3
"""
scripts/retitle_longform.py — Bulk retitle long-form videos for SEO.

Updates 46 video titles via YouTube Data API v3.
Keeps snippet fields intact (category, description, tags, etc.) — only title changes.

Run:
    .venv/bin/python3 scripts/retitle_longform.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.youtube_client import _youtube

NEW_TITLES = {
    # Biblical stories
    "uxwYipwPVlY": "El Buen Samaritano: El Extraño que lo Dio Todo por Ti | Historia Bíblica Completa",
    "0eJRwqC3dGs": "Pentecostés: El Día que Cambió al Mundo Para Siempre | Historia Bíblica Completa",
    "KPePog2wijo": "Sansón y Dalila: Cuando la Traición Destruyó al Hombre más Fuerte | Historia Bíblica",
    "nwiCsnBco2Q": "La Reina Ester: La Mujer que Salvó a su Pueblo con Valentía | Historia Bíblica",
    "9w16_VFEbBw": "David y Goliat: Cómo un Niño Venció al Gigante que Nadie se Atrevía | Historia Bíblica",
    "RXMxEkJpLvs": "Daniel en el Foso: La Fe que Venció a los Leones | Historia Bíblica Completa",
    "JgWIisil1r0": "Abraham e Isaac: La Prueba más Difícil que Dios le Puso a un Padre | Historia Bíblica",
    "iMPxY1zAsFw": "Job: El Hombre que lo Perdió Todo y Aún así Confió en Dios | Historia Bíblica",
    "HeGUMgQlfFo": "Rut y Noemí: La Lealtad que Dios Recompensó con Todo | Historia Bíblica Completa",
    "AEwRB7r21nA": "La Resurrección de Jesús: El Milagro que Cambió la Historia para Siempre | Biblia",
    "5PhNZPFp9sA": "Lázaro: Cuando Jesús Llamó a un Muerto por su Nombre y Respondió | Historia Bíblica",
    "V1GdUjw2GVk": "El Hijo Pródigo: El Padre que Corrió a Abrazar al que lo Había Abandonado | Biblia",
    # 120min sleep
    "lsL1YDjAbHs": "VERSÍCULOS DE PROVISIÓN PARA DORMIR · 2 HORAS · Salmo 23, 37, 91 | Sin Anuncios",
    "tvVef-iuFDk": "SALMOS PARA DORMIR Y ADORAR · 2 HORAS · Salmos 95, 96, 100, 150 | Sin Anuncios",
    "YA1IIG7FzBM": "SANIDAD Y RESTAURACIÓN PARA DORMIR · 2 HORAS · Salmos 91, 103, 147 | Sin Anuncios",
    "SIw4hjII0nM": "VERSÍCULOS DE FE PARA DORMIR · 2 HORAS · Salmos 27, 34, 91 | Sin Anuncios",
    "anhL193gX84": "ESPERANZA EN DIOS PARA DORMIR · 2 HORAS · Salmos 23, 121, 130 | Sin Anuncios",
    "oA2xnlVLB0s": "SALMO 23 Y 91 PARA DORMIR EN PAZ · 2 HORAS · Música Cristiana | Sin Anuncios",
    "mPaL156bODY": "SALMO 23, 91 Y 46 PARA DORMIR · 2 HORAS · Paz Profunda | Sin Anuncios",
    "iRvbBwtMMT8": "SALMO 91, 103 Y 147 PARA DORMIR · 2 HORAS · Sanidad del Alma | Sin Anuncios",
    "oWf1d1blf30": "SALMO 23, 37 Y 91 PARA DORMIR · 2 HORAS · Provisión y Abundancia | Sin Anuncios",
    "qx_5VvNLYNU": "SALMO 46, 55 Y 62 PARA DORMIR · 2 HORAS · Fuerza Cuando Quieres Rendirte | Sin Anuncios",
    "PcDuS5Zdzq0": "SALMOS 95, 96, 100 Y 150 PARA DORMIR · 2 HORAS · Adoración Profunda | Sin Anuncios",
    "dyKrTLUQV3k": "SALMO 18, 27 Y 46 PARA DORMIR · 2 HORAS · Victoria en Cristo | Sin Anuncios",
    "gv8OakHMcgs": "SALMO 36, 63 Y 136 PARA DORMIR · 2 HORAS · El Amor de Dios | Sin Anuncios",
    "t8irvqpb4sk": "SALMO 23, 121 Y 130 PARA DORMIR CON FE · 2 HORAS · Esperanza | Sin Anuncios",
    "TbiCe79N-kY": "SALMO 27, 34 Y 91 PARA DORMIR · 2 HORAS · Fe que Mueve Montañas | Sin Anuncios",
    # 60min sleep
    "gnPVVekKNVo": "SALMOS 100, 103 Y 107 PARA DORMIR · 1 HORA · Gratitud a Dios | Sin Anuncios",
    "J070cCjlTQ0": "SALMO 27, 46 Y 55 PARA DORMIR · 1 HORA · Fuerza Cuando Quieres Rendirte | Sin Anuncios",
    "c2YSkvOW1gQ": "SALMOS DE ADORACIÓN PARA DORMIR · 1 HORA · Versículos Bíblicos | Sin Anuncios",
    "2_2PLEmBjOo": "SALMO 18, 46 Y 118 PARA DORMIR · 1 HORA · Victoria en Cristo | Sin Anuncios",
    "yIrFLIo3JSI": "SALMO 23 Y 91 PARA DORMIR Y MEDITAR · 1 HORA · Paz Sobrenatural | Sin Anuncios",
    "t1kw99tfhqs": "SALMO 63 Y 139 PARA DORMIR · 1 HORA · El Amor de Dios Cuando te Sientes Solo",
    "65sd8KVeu-w": "SALMO 30 Y 62 PARA DORMIR · 1 HORA · Esperanza Cuando Todo Parece Perdido",
    # 40-60min older
    "wl_70CIoGno": "EL AMOR DE DIOS PARA DORMIR · 40 MINUTOS · Versículos Bíblicos | Música Cristiana",
    "Lad1VrQVTMk": "FE QUE MUEVE MONTAÑAS PARA DORMIR · 1 HORA · Versículos Bíblicos | Música Cristiana",
    "awFSfeBg91A": "FUERZA EN DIOS PARA DORMIR · 40 MINUTOS · Versículos para Ser Fuerte | Música Cristiana",
    "HbMt-L3A6So": "PAZ DE DIOS PARA DORMIR Y MEDITAR · 20 MINUTOS · Versículos Bíblicos | Música Cristiana",
    "5YebHbaypVE": "GRATITUD A DIOS PARA DORMIR · 40 MINUTOS · Versículos de Agradecimiento | Música Cristiana",
    # stress/anxiety
    "dWZFEFSZZGI": "MÚSICA CRISTIANA PARA DORMIR Y ALIVIAR ANSIEDAD · 2H 19MIN · Sin Anuncios 2026",
    "qbj_wlpU07M": "MÚSICA CRISTIANA PARA DORMIR Y ALIVIAR EL ESTRÉS · 1H 23MIN · Sin Anuncios 2026",
    # instrumental mid-length
    "hqs9m8vPsCw": "MÚSICA CRISTIANA DE ESPERANZA · 23 MINUTOS · Sonidos de Fe para el Camino",
    "AJshiGhIDDg": "MÚSICA CRISTIANA PARA LA ANSIEDAD · 29 MINUTOS · Paz en la Tormenta | Consuelo Divino",
    "6o59Au-zdFM": "MÚSICA CRISTIANA PARA EMPEZAR EL DÍA · 27 MINUTOS · Adoración en Su Presencia",
    "1I8ROdk-waw": "MÚSICA CRISTIANA PARA ORAR Y CALMAR LA ANSIEDAD · 26 MINUTOS · Refugio y Paz",
    # lo-fi
    "kUDaRMr5JqI": "LOFI CRISTIANO PARA ESTUDIAR Y DESCANSAR · Hip Hop Chill · Paz en Jesús | Mix 2026",
}

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "logs", "retitle_log.json")


def retitle(dry_run: bool = False) -> None:
    yt = _youtube()
    results = []
    total = len(NEW_TITLES)

    print(f"{'DRY RUN — ' if dry_run else ''}Updating {total} video titles...\n")

    for i, (vid_id, new_title) in enumerate(NEW_TITLES.items(), 1):
        print(f"[{i:>2}/{total}] {vid_id} → {new_title[:70]}...")

        if dry_run:
            results.append({"video_id": vid_id, "status": "dry_run", "new_title": new_title})
            continue

        try:
            # Fetch current snippet (required to preserve category, desc, tags)
            resp = yt.videos().list(part="snippet", id=vid_id).execute()
            if not resp.get("items"):
                print(f"         ⚠️  NOT FOUND — skipping")
                results.append({"video_id": vid_id, "status": "not_found"})
                continue

            snippet = resp["items"][0]["snippet"]
            old_title = snippet["title"]
            snippet["title"] = new_title

            yt.videos().update(
                part="snippet",
                body={"id": vid_id, "snippet": snippet},
            ).execute()

            print(f"         ✅  {old_title[:50]} → done")
            results.append({"video_id": vid_id, "status": "ok",
                             "old_title": old_title, "new_title": new_title})

            time.sleep(0.5)  # avoid quota burst

        except Exception as e:
            print(f"         ❌  ERROR: {e}")
            results.append({"video_id": vid_id, "status": "error", "error": str(e)})

    # Save log
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    ok    = sum(1 for r in results if r["status"] == "ok")
    err   = sum(1 for r in results if r["status"] == "error")
    nf    = sum(1 for r in results if r["status"] == "not_found")

    print(f"\n{'─'*52}")
    print(f"  Done: {ok} updated · {err} errors · {nf} not found")
    print(f"  Log → {LOG_PATH}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    retitle(dry_run=args.dry_run)
