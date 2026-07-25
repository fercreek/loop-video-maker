#!/usr/bin/env python3
"""
preview_schedule.py — Previsualiza qué está PROGRAMADO vs PÚBLICO vs PENDIENTE.
Cruza el estado REAL del canal YouTube (API) con los schedules locales.
Output: JSON a stdout (--json) o tabla legible (default).
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from core.youtube_client import _youtube, get_channel_id  # noqa

NOW = datetime.now(timezone.utc)


def fetch_channel_videos(limit=60):
    yt = _youtube()
    ch = get_channel_id()
    # uploads playlist
    r = yt.channels().list(part="contentDetails", id=ch).execute()
    uploads = r["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    vids, token = [], None
    while len(vids) < limit:
        pr = yt.playlistItems().list(part="contentDetails", playlistId=uploads,
                                     maxResults=50, pageToken=token).execute()
        vids += [i["contentDetails"]["videoId"] for i in pr["items"]]
        token = pr.get("nextPageToken")
        if not token:
            break
    out = []
    for i in range(0, len(vids), 50):
        chunk = vids[i:i+50]
        vr = yt.videos().list(part="snippet,status,contentDetails", id=",".join(chunk)).execute()
        for v in vr["items"]:
            st = v["status"]
            sn = v["snippet"]
            dur = v.get("contentDetails", {}).get("duration", "")
            out.append({
                "id": v["id"],
                "title": sn["title"],
                "privacy": st.get("privacyStatus"),
                "publishAt": st.get("publishAt"),          # solo si programado
                "publishedAt": sn.get("publishedAt"),
                "duration": dur,
                "is_short": _is_short(dur),
            })
    return out


def _is_short(iso_dur: str) -> bool:
    # PT#M#S — short si <= 3min aprox
    import re
    m = re.match(r"PT(?:(\d+)M)?(?:(\d+)S)?$", iso_dur or "")
    if not m:
        return False
    mins = int(m.group(1) or 0); secs = int(m.group(2) or 0)
    return (mins*60+secs) <= 180


def classify(v):
    p = v["privacy"]
    if p == "public":
        return "PÚBLICO"
    if p in ("private", "unlisted") and v["publishAt"]:
        pa = datetime.fromisoformat(v["publishAt"].replace("Z", "+00:00"))
        return "PROGRAMADO" if pa > NOW else "PROGRAMADO(vencido)"
    if p == "private":
        return "PRIVADO(sin fecha)"
    return p.upper()


def load_local():
    def rd(f):
        p = os.path.join(REPO, "data", f)
        return json.load(open(p)) if os.path.exists(p) else {}
    up = rd("upload_schedule.json")
    sh = rd("shorts_schedule.json")
    return up.get("schedule", []), sh.get("schedule", sh.get("shorts", []))


def main():
    as_json = "--json" in sys.argv
    try:
        vids = fetch_channel_videos()
        api_ok = True
    except Exception as e:
        vids, api_ok = [], False
        api_err = str(e)

    longform_sched, shorts_sched = load_local()

    # index API por id
    by_id = {v["id"]: v for v in vids}

    # Resolver directo cualquier youtube_id del schedule que no vino en el fetch
    if api_ok:
        missing = [e.get("youtube_id") for e in longform_sched
                   if e.get("youtube_id") and e.get("youtube_id") not in by_id]
        if missing:
            try:
                yt = _youtube()
                vr = yt.videos().list(part="snippet,status,contentDetails",
                                      id=",".join(missing)).execute()
                for v in vr["items"]:
                    st, sn = v["status"], v["snippet"]
                    dur = v.get("contentDetails", {}).get("duration", "")
                    by_id[v["id"]] = {"id": v["id"], "title": sn["title"],
                        "privacy": st.get("privacyStatus"), "publishAt": st.get("publishAt"),
                        "publishedAt": sn.get("publishedAt"), "duration": dur,
                        "is_short": _is_short(dur)}
            except Exception:
                pass

    # Long-form del schedule local: ¿cuál es su estado real en YT?
    longform_rows = []
    for e in longform_sched:
        yid = e.get("youtube_id")
        apiv = by_id.get(yid) if yid else None
        longform_rows.append({
            "title": e.get("title", "?"),
            "story_id": e.get("story_id"),
            "publish_date_plan": e.get("publish_date"),
            "youtube_id": yid,
            "estado_real": classify(apiv) if apiv else ("NO-EN-CANAL" if yid else "SIN-SUBIR"),
            "publishAt_real": apiv["publishAt"] if apiv else None,
        })

    # Shorts del schedule local
    shorts_rows = []
    for e in shorts_sched:
        yid = e.get("youtube_id")
        shorts_rows.append({
            "id": e.get("id") or e.get("short_id"),
            "youtube_id": yid,
            "fb_id": e.get("fb_id") or e.get("facebook_id"),
            "en_youtube": bool(yid),
            "en_facebook": bool(e.get("fb_id") or e.get("facebook_id")),
        })

    # Resumen del canal (todo lo real)
    canal = {"PÚBLICO": 0, "PROGRAMADO": 0, "PROGRAMADO(vencido)": 0,
             "PRIVADO(sin fecha)": 0}
    prog_list = []
    for v in vids:
        c = classify(v)
        canal[c] = canal.get(c, 0) + 1
        if c.startswith("PROGRAMADO"):
            prog_list.append({"title": v["title"], "publishAt": v["publishAt"],
                              "id": v["id"], "tipo": "Short" if v["is_short"] else "Video",
                              "estado": c})

    result = {
        "generated_at": NOW.isoformat(),
        "api_ok": api_ok,
        "canal_resumen": canal if api_ok else None,
        "programados_en_canal": sorted(prog_list, key=lambda x: x["publishAt"] or ""),
        "longform_schedule": longform_rows,
        "shorts_schedule": {
            "total": len(shorts_rows),
            "en_youtube": sum(1 for r in shorts_rows if r["en_youtube"]),
            "en_facebook": sum(1 for r in shorts_rows if r["en_facebook"]),
            "rows": shorts_rows,
        },
    }
    if not api_ok:
        result["api_error"] = api_err

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # tabla legible
    print(f"\n{'='*70}\n  PREVIEW — Estado real del canal @VersiculoDeDios\n  {NOW.strftime('%Y-%m-%d %H:%M UTC')}\n{'='*70}")
    if not api_ok:
        print(f"\n⚠️  API NO disponible: {api_err}\n   (re-auth: python3 scripts/yt_auth.py)")
    else:
        print("\n📊 CANAL (todo lo que existe en YT):")
        for k, n in canal.items():
            if n:
                print(f"   {k:22} {n}")
        print(f"\n🕐 PROGRAMADOS (saldrán solos):")
        if prog_list:
            for p in sorted(prog_list, key=lambda x: x["publishAt"] or ""):
                pa = p["publishAt"][:16].replace("T", " ") if p["publishAt"] else "?"
                flag = "⚠️vencido" if "vencido" in p["estado"] else ""
                print(f"   {pa}  [{p['tipo']:5}] {p['title'][:44]} {flag}")
        else:
            print("   (ninguno)")

    print(f"\n🎬 LONG-FORM (schedule local → estado real):")
    for r in longform_rows:
        print(f"   {r['estado_real']:20} {r['title'][:42]}  (plan {r['publish_date_plan']})")

    s = result["shorts_schedule"]
    print(f"\n📱 SHORTS (batch local):")
    print(f"   En YouTube: {s['en_youtube']}/{s['total']}   En Facebook: {s['en_facebook']}/{s['total']}")
    if s['en_youtube'] == 0:
        print(f"   ⚠️  NINGÚN short llegó a YouTube (solo FB/IG)")
    print()


if __name__ == "__main__":
    main()
