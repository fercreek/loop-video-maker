#!/usr/bin/env python3
"""
check_flywheel.py — ¿el flywheel convierte? Cuenta subscribers beehiiv (el eje).

Track A3 del plan: revisar cada 3-5 días si llega algún sub/apoyo real al flywheel
Ko-fi→email. Sin esto el flywheel está "vivo pero ciego".

Key: lee BEEHIIV_API_KEY del entorno. Si no está local, jala del VPS .env por SSH
(read-only, el key nunca se imprime).

Uso:
  python3 scripts/check_flywheel.py            # total + últimos 7 días
  BEEHIIV_API_KEY=... python3 scripts/check_flywheel.py
"""
import os, json, subprocess, urllib.request, datetime

PUB = "pub_46a515e4-3b0d-4d6f-a041-8d63845fbee3"   # no secreto (identifier)
VPS = "root@2.24.111.80"


def get_key():
    k = os.environ.get("BEEHIIV_API_KEY")
    if k:
        return k
    # fallback: jalar del VPS .env (no imprime el valor)
    try:
        out = subprocess.check_output(
            ["ssh", "-o", "ConnectTimeout=10", VPS,
             "grep '^BEEHIIV_API_KEY=' /root/cero-agent/.env | cut -d= -f2"],
            timeout=20).decode().strip()
        return out or None
    except Exception as e:
        print("⚠ no se pudo obtener BEEHIIV_API_KEY (env ni VPS):", str(e)[:80])
        return None


def api(path, key):
    req = urllib.request.Request(
        "https://api.beehiiv.com/v2/publications/" + PUB + path,
        headers={"Authorization": "Bearer " + key})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())


def main():
    key = get_key()
    if not key:
        return
    # total subs (la API pagina; usa limit=1 y lee total_results)
    r = api("/subscriptions?limit=1&status=active", key)
    total = r.get("total_results")
    if total is None:
        # fallback: contar página(s)
        rr = api("/subscriptions?limit=100&status=active", key)
        total = len(rr.get("data", []))
    # últimos 7 días por created (orden desc)
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    r7 = api("/subscriptions?limit=100&status=active&order_by=created&direction=desc", key)
    recent = [s for s in r7.get("data", []) if str(s.get("created", ""))[:10] >= week_ago]

    print("=== Flywheel — beehiiv (Versículos de Dios) ===")
    print(f"  Subscribers activos:   {total}")
    print(f"  Nuevos últimos 7 días: {len(recent)}")
    if recent:
        for s in recent[:10]:
            src = s.get("utm_source") or "—"
            print(f"    + {s.get('email','?')} | {src} | {str(s.get('created',''))[:10]}")
    print("\n  Apoyos Ko-fi: revisar manual en ko-fi.com/manage (sin API de conteo).")
    print("  Veredicto: subs>0 → flywheel convierte. 0 tras 5 días con tráfico → cuello upstream (Track B).")


if __name__ == "__main__":
    main()
