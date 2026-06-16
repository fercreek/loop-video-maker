#!/usr/bin/env python3
"""
checkpoint_vps.py — Checkpoint diario de la vertical RELIGIÓN, versión VPS (cero-agent).

VPS-native, CERO dependencias (solo stdlib urllib). Corre en root@2.24.111.80 sin
google-api-python-client ni venv. Lee credenciales desde el entorno (cargadas desde
~/cero-agent/.env por n8n / el wrapper).

Qué captura cada mañana (Mac-independiente):
  - YouTube (Data API v3 vía refresh_token YT en .env): subs, total views, video_count.
  - Facebook (Graph API, FB_PAGE_ACCESS_TOKEN): fans, followers.

YPP long-form 365d + watch 28d (requieren scope yt-analytics.readonly que el token del
VPS NO tiene — el de .env es force-ssl/comments) NO se calculan aquí. Se LEEN del último
checkpoint del archivo data/checkpoints.jsonl que la Mac sincroniza (scripts/checkpoint.py
local sí tiene el scope analytics). Si ese dato está viejo, el mensaje lo marca como stale.

Guarda cada corrida en data/checkpoints.jsonl (mismo formato que la Mac → histórico unificado)
y compara contra el último checkpoint para deltas/ritmo/ETA. Manda resumen a Telegram
(@cero_ops_bot, TG_MONITOR_BOT_TOKEN) al chat de Fernando con --telegram.

Uso:
    python3 checkpoint_vps.py              # snapshot + compara + guarda
    python3 checkpoint_vps.py --telegram   # + manda a Telegram
    python3 checkpoint_vps.py --no-save    # solo ver
    python3 checkpoint_vps.py --history    # lista checkpoints

Env requeridas (de ~/cero-agent/.env):
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN, YOUTUBE_CHANNEL_ID
    FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID
    TG_MONITOR_BOT_TOKEN  (+ TG chat id, default 95915749 = Fernando)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# data dir: env override (VPS) → else PROJECT_DIR/data (Mac/loop-video-maker layout)
_DATA_DIR = os.environ.get("CHECKPOINT_DATA_DIR")
if _DATA_DIR:
    CHECKPOINTS = Path(_DATA_DIR) / "checkpoints.jsonl"
else:
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    CHECKPOINTS = PROJECT_DIR / "data" / "checkpoints.jsonl"

YPP_GOAL_H = 4000.0
FB_GOAL_FANS = 5000
TG_CHAT_DEFAULT = "95915749"          # Fernando @fercreek
YPP_STALE_DAYS = 3                    # > este margen → marcar YPP como viejo


# ── helpers HTTP (stdlib only) ───────────────────────────────────────────────
def _get_json(url: str, headers: dict | None = None, timeout: int = 25) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def _yt_access_token() -> str:
    data = urllib.parse.urlencode({
        "client_id": os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
        "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    r = json.loads(urllib.request.urlopen(
        "https://oauth2.googleapis.com/token", data=data, timeout=25).read())
    return r["access_token"]


# ── snapshots ────────────────────────────────────────────────────────────────
def _yt_snapshot() -> dict:
    """Solo Data API (scope force-ssl alcanza): subs, total views, video count."""
    snap: dict = {}
    try:
        at = _yt_access_token()
        ch_id = os.environ["YOUTUBE_CHANNEL_ID"]
        url = ("https://youtube.googleapis.com/youtube/v3/channels"
               f"?part=statistics&id={ch_id}")
        d = _get_json(url, headers={"Authorization": "Bearer " + at})
        st = d["items"][0]["statistics"]
        snap["subs"] = int(st.get("subscriberCount", 0))
        snap["total_views"] = int(st.get("viewCount", 0))
        snap["video_count"] = int(st.get("videoCount", 0))
    except Exception as e:
        print(f"  ⚠️ YT Data API falló: {str(e)[:100]}")
    return snap


def _fb_snapshot() -> dict:
    tok = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
    pid = os.environ.get("FB_PAGE_ID", "")
    if not tok or not pid:
        print("  ⚠️ Falta FB_PAGE_ACCESS_TOKEN / FB_PAGE_ID"); return {}
    try:
        url = (f"https://graph.facebook.com/v21.0/{pid}"
               f"?fields=fan_count,followers_count&access_token={tok}")
        d = _get_json(url)
        return {"fans": int(d.get("fan_count", 0)),
                "followers": int(d.get("followers_count", 0))}
    except Exception as e:
        print(f"  ⚠️ FB Graph falló: {str(e)[:100]}")
        return {}


# ── carry-over de YPP (lo pesado lo provee la Mac) ───────────────────────────
def _last_known_ypp(history: list[dict]) -> dict | None:
    """Último checkpoint que TENGA datos analytics (longform_365d_h). Devuelve dict
    con valores + 'age_days' + 'source_date' o None si nunca hubo."""
    for e in reversed(history):
        yt = e.get("youtube", {})
        if "longform_365d_h" in yt:
            try:
                d0 = datetime.fromisoformat(e["ts"])
            except Exception:
                d0 = datetime.now(timezone.utc)
            age = (datetime.now(timezone.utc) - d0).total_seconds() / 86400
            return {
                "longform_365d_h": yt.get("longform_365d_h"),
                "ypp_pct": yt.get("ypp_pct"),
                "watch_hours_28d": yt.get("watch_hours_28d"),
                "source_date": e.get("date"),
                "age_days": age,
            }
    return None


# ── deltas / formato ─────────────────────────────────────────────────────────
def _load_history() -> list[dict]:
    if not CHECKPOINTS.exists():
        return []
    return [json.loads(l) for l in CHECKPOINTS.read_text().splitlines() if l.strip()]


def _delta(now, prev, key):
    a = now.get(key)
    b = prev.get(key) if prev else None
    if a is None or b is None:
        return None
    return a - b


def _tg_sign(d, suffix=""):
    if d is None:
        return ""
    s = "+" if d >= 0 else ""
    return f" ({s}{d:,.1f}{suffix})" if isinstance(d, float) else f" ({s}{d:,}{suffix})"


def build_telegram_text(now, prev, days, ypp) -> str:
    yt, fb = now["youtube"], now["facebook"]
    pyt = prev.get("youtube", {}) if prev else {}
    pfb = prev.get("facebook", {}) if prev else {}
    head = f"🙏 *Checkpoint Religión* · {now['date']}"
    if prev:
        head += f" (vs {prev['date']}, {days:.1f}d)"
    lines = [head, ""]

    # YouTube
    lines.append("🔴 *YouTube — VersiculoDeDios*")
    if "subs" in yt:
        lines.append(f"• Subs: {yt['subs']:,}{_tg_sign(_delta(yt, pyt, 'subs'))}")
        lines.append(f"• Videos: {yt.get('video_count', '?'):,}{_tg_sign(_delta(yt, pyt, 'video_count'))}")
    else:
        lines.append("• ⚠️ Data API no respondió")
    # YPP (carry-over de la Mac)
    if ypp and ypp.get("ypp_pct") is not None:
        stale = ypp["age_days"] > YPP_STALE_DAYS
        tag = f" ⏳viejo {ypp['age_days']:.0f}d (Mac apagada)" if stale else ""
        lines.append(f"• YPP: *{ypp['ypp_pct']}%* ({ypp['longform_365d_h']:,.0f}h/4000){tag}")
        rem = YPP_GOAL_H - ypp["longform_365d_h"]
        lines.append(f"  faltan {rem:,.0f}h long-form")
    else:
        lines.append("• YPP: sin dato (corre checkpoint.py en Mac)")
    lines.append("")

    # Facebook
    lines.append("🔵 *Facebook — Palabra De Dios*")
    if fb:
        dfans = _delta(fb, pfb, "fans")
        lines.append(f"• Fans: *{fb['fans']:,}* ({fb['fans'] / FB_GOAL_FANS * 100:.0f}% de 5k){_tg_sign(dfans)}")
        rem = FB_GOAL_FANS - fb["fans"]
        if days and dfans and dfans > 0:
            lines.append(f"  → {dfans / days:.1f} fans/día · ETA ~{round(rem / (dfans / days))}d")
        else:
            lines.append(f"  faltan {rem:,} para 5k")
    else:
        lines.append("• ⚠️ Graph API no respondió")

    lines.append("")
    lines.append("— Anti-Venom 🧬 (VPS · n8n)")
    return "\n".join(lines)


def send_telegram(text: str, token: str, chat_id: str) -> bool:
    try:
        data = urllib.parse.urlencode({
            "chat_id": chat_id, "text": text, "parse_mode": "Markdown",
        }).encode()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20)
        return True
    except Exception as e:
        print(f"  ⚠️ Telegram send falló: {str(e)[:160]}")
        return False


def main():
    ap = argparse.ArgumentParser(description="Checkpoint religión (VPS, zero-deps)")
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--history", action="store_true")
    ap.add_argument("--telegram", action="store_true")
    args = ap.parse_args()

    history = _load_history()

    if args.history:
        for e in history:
            yt, fb = e.get("youtube", {}), e.get("facebook", {})
            print(f"{e['date']}  YT {yt.get('subs', '?')} subs · YPP {yt.get('ypp_pct', '—')}% "
                  f"· FB {fb.get('fans', '?')} fans")
        return

    print("📊 Checkpoint vertical RELIGIÓN (VPS) — capturando...\n")
    now = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "vps",
        "youtube": _yt_snapshot(),
        "facebook": _fb_snapshot(),
    }
    prev = history[-1] if history else None
    ypp = _last_known_ypp(history)

    days = None
    if prev:
        try:
            d0 = datetime.fromisoformat(prev["ts"])
            days = max((datetime.now(timezone.utc) - d0).total_seconds() / 86400, 0.01)
        except Exception:
            days = 1.0

    yt, fb = now["youtube"], now["facebook"]
    print("=" * 52)
    print(f"  CHECKPOINT {now['date']} (VPS)" + (f"  · vs {prev['date']} ({days:.1f}d)" if prev else "  (primero)"))
    print("=" * 52)
    print("\n  🔴 YOUTUBE — VersiculoDeDios")
    print(f"    Subs:   {yt.get('subs', '?'):>10,}")
    print(f"    Videos: {yt.get('video_count', '?'):>10,}")
    if ypp and ypp.get("ypp_pct") is not None:
        stale = ypp["age_days"] > YPP_STALE_DAYS
        print(f"    YPP:    {ypp['ypp_pct']:>9}% ({ypp['longform_365d_h']:.0f}h/4000)"
              + (f"  ⏳ {ypp['age_days']:.0f}d viejo (Mac)" if stale else "  (Mac, fresco)"))
    print("\n  🔵 FACEBOOK — Palabra De Dios")
    if fb:
        print(f"    Fans:   {fb['fans']:>10,}  ({fb['fans'] / FB_GOAL_FANS * 100:.1f}% de 5k)")

    if not args.no_save and (yt or fb):
        CHECKPOINTS.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINTS, "a") as f:
            f.write(json.dumps(now, ensure_ascii=False) + "\n")
        print(f"\n  ✅ Guardado en {CHECKPOINTS.name}")

    if args.telegram:
        token = os.environ.get("TG_MONITOR_BOT_TOKEN", "")
        chat = os.environ.get("TG_CHAT_ID", "") or TG_CHAT_DEFAULT
        if not token:
            print("  ⚠️ Falta TG_MONITOR_BOT_TOKEN")
        elif send_telegram(build_telegram_text(now, prev, days or 1, ypp), token, str(chat)):
            print("  📲 Enviado a Telegram")


if __name__ == "__main__":
    main()
