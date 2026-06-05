#!/usr/bin/env python3
"""
measure_experiment.py — pull dirigido a YT Analytics por VIDEO (no canal global).

La pieza que faltaba para operar Operación de Dios como LAB: cada experimento se mide
por su video_id contra su ventana, no contra el canal entero. Cierra el loop
experimento→medición→log.

Uso:
  python3 scripts/measure_experiment.py <video_id> [--days 14] [--since 2026-06-04]
  python3 scripts/measure_experiment.py <video_id> --exp EXP-001   # graba result al ledger

Métricas: views, watch-h, avg view duration, retención %, impresiones + CTR (si dispo).
Ledger: data/experiments.jsonl (1 línea/experimento).
"""
import argparse, json, os, sys, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LEDGER = BASE / "data" / "experiments.jsonl"


def yt_analytics():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    c = Credentials.from_authorized_user_file(str(BASE / "data" / "yt_token.json"))
    if not c.valid:
        c.refresh(Request())
    return build("youtubeAnalytics", "v2", credentials=c)


def measure(video_id, start, end):
    ya = yt_analytics()
    # metrics base (siempre disponibles)
    base_metrics = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage"
    r = ya.reports().query(
        ids="channel==MINE", startDate=start, endDate=end,
        metrics=base_metrics, dimensions="video", filters="video==" + video_id,
    ).execute()
    rows = r.get("rows", [])
    out = {"video_id": video_id, "window": f"{start}..{end}",
           "views": 0, "watch_h": 0.0, "avg_view_sec": 0, "retention_pct": 0.0}
    if rows:
        _, views, mins, avgdur, avgpct = rows[0]
        out.update(views=int(views), watch_h=round(mins / 60, 2),
                   avg_view_sec=int(avgdur), retention_pct=round(avgpct, 1))
    # impresiones + CTR (puede no estar disponible según permisos → try)
    try:
        ri = ya.reports().query(
            ids="channel==MINE", startDate=start, endDate=end,
            metrics="impressions,impressionsClickThroughRate",
            dimensions="video", filters="video==" + video_id,
        ).execute().get("rows", [])
        if ri:
            out["impressions"] = int(ri[0][1])
            out["ctr_pct"] = round(float(ri[0][2]), 2)
    except Exception:
        out["impressions"] = None
        out["ctr_pct"] = None
    return out


def record_to_ledger(exp_id, result):
    if not LEDGER.exists():
        print(f"⚠ {LEDGER} no existe — corre con el experimento creado primero.")
        return
    lines = LEDGER.read_text().splitlines()
    updated = False
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        e = json.loads(ln)
        if e.get("id") == exp_id:
            e.setdefault("measurements", []).append(result)
            lines[i] = json.dumps(e, ensure_ascii=False)
            updated = True
            break
    if updated:
        LEDGER.write_text("\n".join(lines) + "\n")
        print(f"✓ medición guardada en {exp_id}")
    else:
        print(f"⚠ experimento {exp_id} no encontrado en el ledger.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--since", help="fecha inicio YYYY-MM-DD (default: hoy - days)")
    ap.add_argument("--exp", help="ID de experimento para grabar el result al ledger")
    a = ap.parse_args()

    end = datetime.date.today().isoformat()
    if a.since:
        start = a.since
    else:
        start = (datetime.date.today() - datetime.timedelta(days=a.days)).isoformat()

    res = measure(a.video_id, start, end)
    res["measured_at"] = end
    print(f"\n=== {a.video_id} | {res['window']} ===")
    print(f"  views:        {res['views']}")
    print(f"  watch-h:      {res['watch_h']}h")
    print(f"  avg view:     {res['avg_view_sec']//60}:{res['avg_view_sec']%60:02d} min")
    print(f"  retención:    {res['retention_pct']}%")
    print(f"  impresiones:  {res.get('impressions')}")
    print(f"  CTR:          {res.get('ctr_pct')}%")
    if a.exp:
        record_to_ledger(a.exp, res)


if __name__ == "__main__":
    main()
