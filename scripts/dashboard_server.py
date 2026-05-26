"""
scripts/dashboard_server.py — Local dashboard para todos los daemons venom.

Puerto 8090. Sirve dashboard.html + /api/status + /api/log

Uso:
    .venv/bin/python3 scripts/dashboard_server.py &
    open http://127.0.0.1:8090/dashboard.html
"""
from __future__ import annotations

import json
import os
import subprocess
import http.server
import socketserver
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
os.chdir(PROJECT_DIR)

MTY = timezone(timedelta(hours=-6))
PORT = 8090

DAEMONS = [
    "com.versiculodedios.ig-daemon",
    "com.versiculodedios.yt-fb-uploader",
    "com.versiculodedios.morning-status",
]


def get_daemons_status():
    """Llamar launchctl list, parse output."""
    r = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    daemons = []
    for label in DAEMONS:
        pid, exit_code = 0, None
        for line in r.stdout.splitlines():
            if label in line:
                parts = line.split()
                pid = int(parts[0]) if parts[0].isdigit() else 0
                exit_code = int(parts[1]) if parts[1].isdigit() or parts[1].startswith('-') else None
                break
        daemons.append({"label": label.replace("com.versiculodedios.", ""), "pid": pid, "last_exit": exit_code})
    return daemons


def get_status():
    # YT/FB
    yt_ok = fb_ok = 0
    upcoming = []
    total = 0
    try:
        s = json.load(open("data/shorts_schedule.json"))
        items = s.get("schedule", [])
        total = len(items)
        yt_ok = sum(1 for e in items if e.get("yt_id"))
        fb_ok = sum(1 for e in items if e.get("fb_id"))

        # IG state
        ig_pub = {}
        if os.path.exists("data/ig_state.json"):
            ig = json.load(open("data/ig_state.json"))
            ig_pub = ig.get("published", {})

        now = datetime.now(MTY)
        for e in items:
            try:
                t = datetime.strptime(e["publish_mty"], "%Y-%m-%d %H:%M MTY").replace(tzinfo=MTY)
                delta = (t - now).total_seconds()
                if -3600 < delta < 172800:  # ±1h to +48h
                    upcoming.append({
                        "when": t.strftime("%m-%d %H:%M"),
                        "id": e["id"],
                        "yt": "✅" if e.get("yt_id") else "❌",
                        "fb": "✅" if e.get("fb_id") else "❌",
                        "ig": "✅" if e["id"] in ig_pub else "⏳",
                        "_sort": delta,
                    })
            except Exception:
                pass
        upcoming.sort(key=lambda x: x["_sort"])
        for u in upcoming: u.pop("_sort", None)
    except Exception as e:
        pass

    # IG count
    ig_count = len(ig_pub) if 'ig_pub' in dir() else 0

    # Errors recent
    errors = []
    for name in ["ig_daemon.log", "yt_fb_uploader.stderr"]:
        path = PROJECT_DIR / "logs" / name
        if path.exists():
            try:
                lines = path.read_text(errors='ignore').splitlines()[-50:]
                errs = [l for l in lines if 'ERROR' in l or 'Exception' in l or 'error' in l.lower()]
                if errs:
                    errors.append(f"{name}: {len(errs)} errors (ver logs)")
            except Exception:
                pass

    return {
        "yt_ok": yt_ok, "fb_ok": fb_ok, "ig_ok": ig_count, "total": total,
        "daemons": get_daemons_status(),
        "upcoming": upcoming,
        "errors": errors,
    }


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs): pass  # silenciar logs

    def do_GET(self):
        if self.path.startswith("/api/status"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps(get_status(), ensure_ascii=False).encode("utf-8"))
            return
        if self.path.startswith("/api/log"):
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            name = params.get("name", [""])[0]
            safe = name.replace("/", "").replace("..", "")
            path = PROJECT_DIR / "logs" / safe
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                lines = path.read_text(errors='ignore').splitlines()[-80:]
                self.wfile.write("\n".join(lines).encode("utf-8"))
            except Exception as e:
                self.wfile.write(f"Error reading {safe}: {e}".encode("utf-8"))
            return
        return super().do_GET()


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    with ThreadingServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Dashboard: http://127.0.0.1:{PORT}/dashboard.html")
        httpd.serve_forever()
