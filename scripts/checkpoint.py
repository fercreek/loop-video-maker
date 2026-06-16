"""
scripts/checkpoint.py — Checkpoint de crecimiento de la vertical RELIGIÓN.

Snapshot diario de las DOS vías de @VersiculoDeDios / Palabra De Dios:
  - YouTube (VersiculoDeDios)  → gate YPP (4,000h long-form) + subs + watch 28d
  - Facebook (Palabra De Dios) → umbral 5,000 fans (FB Content Monetization)

Guarda cada corrida en data/checkpoints.jsonl y, al correr, COMPARA contra el
último checkpoint: deltas por métrica, ritmo/día, y ETA a la meta de cada vía.
Pensado para la sesión diaria de 1-2h de crecimiento.

Uso:
    .venv/bin/python3 scripts/checkpoint.py            # snapshot + compara vs último
    .venv/bin/python3 scripts/checkpoint.py --no-save  # solo ver, no guardar
    .venv/bin/python3 scripts/checkpoint.py --history  # lista todos los checkpoints

Fuentes: YT Data+Analytics API (core.youtube_client) · FB Graph API (token cero-content).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))
for _pyver in ["python3.13", "python3.12", "python3.11", "python3.9"]:
    _site = PROJECT_DIR / ".venv" / "lib" / _pyver / "site-packages"
    if _site.exists():
        sys.path.insert(0, str(_site))
        break

from core.youtube_client import _youtube, _analytics, get_channel_id

CHECKPOINTS = PROJECT_DIR / "data" / "checkpoints.jsonl"
FB_TOKEN_PATH = Path(os.path.expanduser("~/Documents/cero/cero-content/scripts/configs/tokens.json"))
FB_PAGE_ID = "452922677899760"   # Palabra De Dios
SLEEP_DEST_ID = "aqFlPGDD2ww"    # sleep Paz — destino del funnel de Shorts
YPP_GOAL_H = 4000.0
FB_GOAL_FANS = 5000


def _n(v):
    """Formato con comas si es número; si es '?'/None, devuelve string seguro (evita TypeError)."""
    return f"{v:,}" if isinstance(v, (int, float)) else str(v if v is not None else "?")


def _yt_snapshot() -> dict:
    snap = {}
    try:
        yt = _youtube()
        ch = yt.channels().list(part="statistics", id=get_channel_id()).execute()["items"][0]["statistics"]
        snap = {
            "subs": int(ch.get("subscriberCount", 0)),
            "total_views": int(ch.get("viewCount", 0)),
            "video_count": int(ch.get("videoCount", 0)),
        }
    except Exception as e:
        print(f"  ⚠️ YT channels falló: {str(e)[:80]}")
        return snap
    # 28d watch + views via Analytics
    try:
        ya = _analytics()
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=28)
        r = ya.reports().query(
            ids="channel==MINE", startDate=str(start), endDate=str(end),
            metrics="estimatedMinutesWatched,views,subscribersGained",
        ).execute()
        row = (r.get("rows") or [[0, 0, 0]])[0]
        snap["watch_hours_28d"] = round(row[0] / 60, 1)
        snap["views_28d"] = int(row[1])
        snap["subs_gained_28d"] = int(row[2])
    except Exception as e:
        print(f"  ⚠️ YT analytics 28d falló: {str(e)[:80]}")
    # long-form 365d (lo que cuenta YPP) — reusa ypp_tracker
    try:
        from ypp_tracker import fetch_longform_hours
        total, breakdown = fetch_longform_hours()
        snap["longform_365d_h"] = round(total, 1)
        snap["ypp_pct"] = round(total / YPP_GOAL_H * 100, 1)
        # Split por formato DENTRO de long-form: historia (≤35min) vs sleep/lofi (>35min)
        # → dice dónde está el ROI real al gate (qué producir más)
        hist = round(sum(v.get("watch_hours", 0) for v in breakdown if v.get("duration_min", 0) <= 35), 1)
        slp = round(sum(v.get("watch_hours", 0) for v in breakdown if v.get("duration_min", 0) > 35), 1)
        snap["format_split"] = {"historia_h": hist, "sleep_h": slp}
        # Top videos por watch-hours (para detectar movers vs el próximo checkpoint)
        top = sorted(breakdown, key=lambda v: v.get("watch_hours", 0), reverse=True)[:8]
        snap["top_videos"] = [
            {"video_id": v["video_id"], "title": v["title"][:48], "watch_hours": round(v.get("watch_hours", 0), 1)}
            for v in top
        ]
    except Exception as e:
        print(f"  ⚠️ long-form 365d falló: {str(e)[:80]}")
    # Funnel signal: views del sleep destino (a dónde mandan tráfico los Shorts wired)
    try:
        rv = yt.videos().list(part="statistics", id=SLEEP_DEST_ID).execute()
        snap["funnel_sleep_views"] = int(rv["items"][0]["statistics"].get("viewCount", 0))
    except Exception:
        pass
    return snap


def _fb_snapshot() -> dict:
    if not FB_TOKEN_PATH.exists():
        print(f"  ⚠️ sin token FB ({FB_TOKEN_PATH})")
        return {}
    tok = json.load(open(FB_TOKEN_PATH)).get("palabra-de-dios", "")
    if not tok:
        print("  ⚠️ token palabra-de-dios vacío"); return {}
    out = {}
    try:
        url = (f"https://graph.facebook.com/v21.0/{FB_PAGE_ID}"
               f"?fields=fan_count,followers_count&access_token={tok}")
        d = json.loads(urllib.request.urlopen(url, timeout=20).read())
        out = {"fans": int(d.get("fan_count", 0)), "followers": int(d.get("followers_count", 0))}
    except Exception as e:
        print(f"  ⚠️ FB Graph falló: {str(e)[:80]}")
        return out
    # Engagement 28d (best-effort: alcance + interacciones) → qué Reel jala, qué reciclar
    try:
        iu = (f"https://graph.facebook.com/v21.0/{FB_PAGE_ID}/insights"
              f"?metric=page_impressions_unique,page_post_engagements&period=days_28&access_token={tok}")
        di = json.loads(urllib.request.urlopen(iu, timeout=20).read())
        for m in di.get("data", []):
            vals = m.get("values", [])
            if vals and vals[-1].get("value") is not None:
                key = "reach_28d" if m["name"] == "page_impressions_unique" else "engagements_28d"
                out[key] = int(vals[-1]["value"])
    except Exception:
        pass  # insights a veces deprecados/sin permiso — fans es lo crítico
    return out


def _load_last() -> dict | None:
    if not CHECKPOINTS.exists():
        return None
    lines = [l for l in CHECKPOINTS.read_text().splitlines() if l.strip()]
    return json.loads(lines[-1]) if lines else None


def _delta(now, prev, key):
    a, b = now.get(key), prev.get(key) if prev else None
    if a is None or b is None:
        return None
    return a - b


def _fmt_delta(d, suffix=""):
    if d is None:
        return ""
    sign = "+" if d >= 0 else ""
    return f"  ({sign}{d:,.1f}{suffix})" if isinstance(d, float) else f"  ({sign}{d:,}{suffix})"


def _top_movers(now_yt, prev_yt, n=3):
    """Videos long-form que más watch-hours ganaron vs el checkpoint anterior."""
    cur = now_yt.get("top_videos") or []
    prev = {v["video_id"]: v.get("watch_hours", 0) for v in (prev_yt.get("top_videos") or [])}
    if not prev:
        return []
    movers = []
    for v in cur:
        if v["video_id"] in prev:
            d = round(v.get("watch_hours", 0) - prev[v["video_id"]], 1)
            if d > 0:
                movers.append((v["title"], d))
    movers.sort(key=lambda x: x[1], reverse=True)
    return movers[:n]


def _tg_sign(d, suffix=""):
    if d is None:
        return ""
    s = "+" if d >= 0 else ""
    return f" ({s}{d:,.1f}{suffix})" if isinstance(d, float) else f" ({s}{d:,}{suffix})"


def build_telegram_text(now, prev, days) -> str:
    """Mensaje compacto para Telegram (resumen diario de ambas verticales)."""
    yt, fb = now["youtube"], now["facebook"]
    pyt = prev.get("youtube", {}) if prev else {}
    pfb = prev.get("facebook", {}) if prev else {}
    head = f"🙏 *Checkpoint Religión* · {now['date']}"
    if prev:
        head += f" (vs {prev['date']}, {days:.1f}d)"
    lines = [head, ""]
    # YouTube
    lines.append("🔴 *YouTube — VersiculoDeDios*")
    lines.append(f"• Subs: {_n(yt.get('subs'))}{_tg_sign(_delta(yt,pyt,'subs'))}")
    if "ypp_pct" in yt:
        dh = _delta(yt, pyt, "longform_365d_h")
        lines.append(f"• YPP: *{yt['ypp_pct']}%* ({yt['longform_365d_h']:,.0f}h/4000){_tg_sign(dh,'h')}")
        rem = YPP_GOAL_H - yt["longform_365d_h"]
        if days and dh and dh > 0:
            lines.append(f"  → {dh/days:.1f}h/día · ETA ~{round(rem/(dh/days))}d")
    lines.append(f"• Watch 28d: {_n(yt.get('watch_hours_28d'))}h{_tg_sign(_delta(yt,pyt,'watch_hours_28d'),'h')}")
    fs = yt.get("format_split")
    if fs:
        lines.append(f"• Gate: historia {fs['historia_h']}h · sleep {fs['sleep_h']}h")
    movers = _top_movers(yt, pyt, n=2)
    if movers:
        lines.append("• 📈 Jaló: " + " · ".join(f"+{d:.1f}h {t[:24]}" for t, d in movers))
    lines.append("")
    # Facebook
    lines.append("🔵 *Facebook — Palabra De Dios*")
    if fb:
        dfans = _delta(fb, pfb, "fans")
        lines.append(f"• Fans: *{fb['fans']:,}* ({fb['fans']/FB_GOAL_FANS*100:.0f}% de 5k){_tg_sign(dfans)}")
        rem = FB_GOAL_FANS - fb["fans"]
        if days and dfans and dfans > 0:
            lines.append(f"  → {dfans/days:.1f} fans/día · ETA ~{round(rem/(dfans/days))}d")
        else:
            lines.append(f"  faltan {rem:,} para 5k")
        if "engagements_28d" in fb:
            lines.append(f"• Engagement 28d: {_n(fb.get('engagements_28d'))}{_tg_sign(_delta(fb,pfb,'engagements_28d'))}")
    return "\n".join(lines)


def send_telegram(text: str, token: str, chat_id: str) -> bool:
    import urllib.parse
    try:
        data = urllib.parse.urlencode({
            "chat_id": chat_id, "text": text, "parse_mode": "Markdown",
        }).encode()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20)
        return True
    except Exception as e:
        print(f"  ⚠️ Telegram send falló: {str(e)[:120]}")
        return False


def main():
    ap = argparse.ArgumentParser(description="Checkpoint crecimiento religión (YT+FB)")
    ap.add_argument("--no-save", action="store_true", help="no guardar, solo mostrar")
    ap.add_argument("--history", action="store_true", help="listar todos los checkpoints")
    ap.add_argument("--telegram", action="store_true",
                    help="enviar resumen a Telegram (creds en config.json: telegram_bot_token + telegram_chat_id, o env TG_BOT_TOKEN/TG_CHAT_ID)")
    args = ap.parse_args()

    if args.history:
        if not CHECKPOINTS.exists():
            print("Sin checkpoints aún."); return
        for l in CHECKPOINTS.read_text().splitlines():
            if not l.strip():
                continue
            e = json.loads(l)
            yt, fb = e.get("youtube", {}), e.get("facebook", {})
            print(f"{e['date']}  YT {yt.get('subs','?')} subs · YPP {yt.get('ypp_pct','?')}% "
                  f"({yt.get('longform_365d_h','?')}h) · FB {fb.get('fans','?')} fans")
        return

    print("📊 Checkpoint vertical RELIGIÓN — capturando...\n")
    now = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "ts": datetime.now(timezone.utc).isoformat(),
        "youtube": _yt_snapshot(),
        "facebook": _fb_snapshot(),
    }
    prev = _load_last()
    yt, fb = now["youtube"], now["facebook"]
    pyt = prev.get("youtube", {}) if prev else {}
    pfb = prev.get("facebook", {}) if prev else {}

    # días entre checkpoints (para ritmo/día)
    days = None
    if prev:
        d0 = datetime.fromisoformat(prev["ts"])
        days = max((datetime.now(timezone.utc) - d0).total_seconds() / 86400, 0.01)

    print("=" * 56)
    print(f"  CHECKPOINT {now['date']}" + (f"  ·  vs {prev['date']} ({days:.1f}d)" if prev else "  (primero)"))
    print("=" * 56)

    print("\n  🔴 YOUTUBE — VersiculoDeDios (gate YPP)")
    print(f"    Subs:            {_n(yt.get('subs')):>10}{_fmt_delta(_delta(yt,pyt,'subs'))}")
    if "ypp_pct" in yt:
        dh = _delta(yt, pyt, "longform_365d_h")
        print(f"    Long-form 365d:  {yt['longform_365d_h']:>10,.1f}h{_fmt_delta(dh,'h')}  →  {yt['ypp_pct']}% de 4,000h")
        rem = YPP_GOAL_H - yt["longform_365d_h"]
        if rem <= 0:
            print(f"    🎉 Meta YPP alcanzada ({yt['longform_365d_h']:,.0f}h)")
        elif days and dh and dh > 0:
            rate = dh / days
            eta = round(rem / rate)
            print(f"    Ritmo: {rate:.1f}h/día → ETA YPP ~{eta} días  (faltan {rem:,.0f}h)")
        else:
            print(f"    Faltan {rem:,.0f}h para YPP")
    print(f"    Watch 28d:       {_n(yt.get('watch_hours_28d')):>10}h{_fmt_delta(_delta(yt,pyt,'watch_hours_28d'),'h')}")
    print(f"    Views 28d:       {_n(yt.get('views_28d')):>10}{_fmt_delta(_delta(yt,pyt,'views_28d'))}")
    # Split por formato (dónde está el ROI al gate)
    fs = yt.get("format_split")
    if fs:
        print(f"    Formato (h gate): historia {fs['historia_h']}h · sleep {fs['sleep_h']}h")
    # Top movers (qué jaló desde el último checkpoint)
    movers = _top_movers(yt, pyt)
    if movers:
        print("    📈 Movers (Δh long-form):")
        for t, d in movers:
            print(f"       +{d:.1f}h  {t}")
    # Funnel (Shorts → sleep destino)
    fsv = yt.get("funnel_sleep_views")
    if fsv is not None:
        print(f"    Funnel sleep dest: {fsv:>8,} views{_fmt_delta(_delta(yt,pyt,'funnel_sleep_views'))}")

    print("\n  🔵 FACEBOOK — Palabra De Dios (umbral 5k → monetización)")
    if fb:
        dfans = _delta(fb, pfb, "fans")
        print(f"    Fans:            {fb['fans']:>10,}{_fmt_delta(dfans)}  →  {fb['fans']/FB_GOAL_FANS*100:.1f}% de 5,000")
        rem = FB_GOAL_FANS - fb["fans"]
        if rem <= 0:
            print(f"    🎉 Meta 5k alcanzada ({fb['fans']:,} fans)")
        elif days and dfans and dfans > 0:
            rate = dfans / days
            eta = round(rem / rate)
            print(f"    Ritmo: {rate:.1f} fans/día → ETA 5k ~{eta} días  (faltan {rem:,})")
        else:
            print(f"    Faltan {rem:,} fans para 5k")
        if "reach_28d" in fb:
            print(f"    Reach 28d:       {_n(fb.get('reach_28d')):>10}{_fmt_delta(_delta(fb,pfb,'reach_28d'))}")
        if "engagements_28d" in fb:
            print(f"    Engagement 28d:  {_n(fb.get('engagements_28d')):>10}{_fmt_delta(_delta(fb,pfb,'engagements_28d'))}")

    if args.no_save:
        print("\n  (--no-save: no guardado)")
    elif not (yt or fb):
        print("\n  ⚠️ Ambos APIs vacíos — NO guardo entry basura.")
    else:
        CHECKPOINTS.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINTS, "a") as f:
            f.write(json.dumps(now, ensure_ascii=False) + "\n")
        print(f"\n  ✅ Guardado en {CHECKPOINTS.name}  (--history para ver todos)")

    if args.telegram:
        cfg = json.load(open(PROJECT_DIR / "config.json")) if (PROJECT_DIR / "config.json").exists() else {}
        token = cfg.get("telegram_bot_token") or os.environ.get("TG_BOT_TOKEN", "")
        chat = cfg.get("telegram_chat_id") or os.environ.get("TG_CHAT_ID", "")
        if not token or not chat:
            print("  ⚠️ Faltan telegram_bot_token / telegram_chat_id (config.json o env)")
        elif send_telegram(build_telegram_text(now, prev, days or 1), token, str(chat)):
            print("  📲 Enviado a Telegram")


if __name__ == "__main__":
    main()
