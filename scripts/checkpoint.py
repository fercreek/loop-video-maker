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
YPP_GOAL_H = 4000.0
FB_GOAL_FANS = 5000


def _yt_snapshot() -> dict:
    yt = _youtube()
    ch = yt.channels().list(part="statistics", id=get_channel_id()).execute()["items"][0]["statistics"]
    snap = {
        "subs": int(ch.get("subscriberCount", 0)),
        "total_views": int(ch.get("viewCount", 0)),
        "video_count": int(ch.get("videoCount", 0)),
    }
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
        total, _ = fetch_longform_hours()
        snap["longform_365d_h"] = round(total, 1)
        snap["ypp_pct"] = round(total / YPP_GOAL_H * 100, 1)
    except Exception as e:
        print(f"  ⚠️ long-form 365d falló: {str(e)[:80]}")
    return snap


def _fb_snapshot() -> dict:
    if not FB_TOKEN_PATH.exists():
        print(f"  ⚠️ sin token FB ({FB_TOKEN_PATH})")
        return {}
    tok = json.load(open(FB_TOKEN_PATH)).get("palabra-de-dios", "")
    if not tok:
        print("  ⚠️ token palabra-de-dios vacío"); return {}
    try:
        url = (f"https://graph.facebook.com/v21.0/{FB_PAGE_ID}"
               f"?fields=fan_count,followers_count&access_token={tok}")
        d = json.loads(urllib.request.urlopen(url, timeout=20).read())
        return {"fans": int(d.get("fan_count", 0)), "followers": int(d.get("followers_count", 0))}
    except Exception as e:
        print(f"  ⚠️ FB Graph falló: {str(e)[:80]}")
        return {}


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
    lines.append(f"• Subs: {yt.get('subs','?'):,}{_tg_sign(_delta(yt,pyt,'subs'))}")
    if "ypp_pct" in yt:
        dh = _delta(yt, pyt, "longform_365d_h")
        lines.append(f"• YPP: *{yt['ypp_pct']}%* ({yt['longform_365d_h']:,.0f}h/4000){_tg_sign(dh,'h')}")
        rem = YPP_GOAL_H - yt["longform_365d_h"]
        if days and dh and dh > 0:
            lines.append(f"  → {dh/days:.1f}h/día · ETA ~{round(rem/(dh/days))}d")
    lines.append(f"• Watch 28d: {yt.get('watch_hours_28d','?'):,}h{_tg_sign(_delta(yt,pyt,'watch_hours_28d'),'h')}")
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
    print(f"    Subs:            {yt.get('subs','?'):>10,}{_fmt_delta(_delta(yt,pyt,'subs'))}")
    if "ypp_pct" in yt:
        dh = _delta(yt, pyt, "longform_365d_h")
        print(f"    Long-form 365d:  {yt['longform_365d_h']:>10,.1f}h{_fmt_delta(dh,'h')}  →  {yt['ypp_pct']}% de 4,000h")
        rem = YPP_GOAL_H - yt["longform_365d_h"]
        if days and dh and dh > 0:
            rate = dh / days
            eta = round(rem / rate)
            print(f"    Ritmo: {rate:.1f}h/día → ETA YPP ~{eta} días  (faltan {rem:,.0f}h)")
        else:
            print(f"    Faltan {rem:,.0f}h para YPP")
    print(f"    Watch 28d:       {yt.get('watch_hours_28d','?'):>10,}h{_fmt_delta(_delta(yt,pyt,'watch_hours_28d'),'h')}")
    print(f"    Views 28d:       {yt.get('views_28d','?'):>10,}{_fmt_delta(_delta(yt,pyt,'views_28d'))}")

    print("\n  🔵 FACEBOOK — Palabra De Dios (umbral 5k → monetización)")
    if fb:
        dfans = _delta(fb, pfb, "fans")
        print(f"    Fans:            {fb['fans']:>10,}{_fmt_delta(dfans)}  →  {fb['fans']/FB_GOAL_FANS*100:.1f}% de 5,000")
        rem = FB_GOAL_FANS - fb["fans"]
        if days and dfans and dfans > 0:
            rate = dfans / days
            eta = round(rem / rate)
            print(f"    Ritmo: {rate:.1f} fans/día → ETA 5k ~{eta} días  (faltan {rem:,})")
        else:
            print(f"    Faltan {rem:,} fans para 5k")

    if not args.no_save:
        CHECKPOINTS.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINTS, "a") as f:
            f.write(json.dumps(now, ensure_ascii=False) + "\n")
        print(f"\n  ✅ Guardado en {CHECKPOINTS.name}  (--history para ver todos)")
    else:
        print("\n  (--no-save: no guardado)")

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
