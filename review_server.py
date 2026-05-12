#!/usr/bin/env python3
"""
Review server — serves static files + accepts POST /save to write review JSON.
Usage: python3 review_server.py [port]
"""
import http.server, json, os, sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ROOT = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                out_path = ROOT / 'data' / 'shorts_review.json'
                out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
                print(f"  [save] {out_path} — {len(data.get('shorts',[]))} items")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, fmt, *args):
        # Suppress static file noise, only show saves
        if '/save' in (args[0] if args else ''):
            super().log_message(fmt, *args)

if __name__ == '__main__':
    os.chdir(ROOT)
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        print(f"Review server on http://localhost:{PORT}/review_shorts.html")
        print(f"Auto-save → {ROOT}/data/shorts_review.json")
        httpd.serve_forever()
