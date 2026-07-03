"""
VD Review Server — grid HTML para aprobar/rechazar contenido producido.
Escanea output/ en vivo (incluye lo que se renderice después), reproduce cada
video, y guarda decisiones en data/vd_review_decisions.json (auto-save por click).

Uso:  .venv/bin/python3 vd_review_server.py [puerto]   (default 8090)
Abrir: http://localhost:8090/
"""
import http.server, json, sys, urllib.parse, subprocess, datetime
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
ROOT = Path(__file__).parent
DECISIONS = ROOT / "data" / "vd_review_decisions.json"

TYPE_LABEL = {"stories": "LONG-FORM", "sleep": "SLEEP", "shorts": "REEL"}
TYPE_COLOR = {"stories": "#6c8cff", "sleep": "#9b7cff", "shorts": "#ff9f43"}


def ffdur(p: Path) -> str:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
            capture_output=True, text=True, timeout=20).stdout.strip()
        s = float(out)
        return f"{int(s//60)}:{int(s%60):02d}"
    except Exception:
        return "—"


def scan():
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from _mp4_ok import valid_mp4
    except Exception:
        valid_mp4 = lambda p: True
    items = []
    for sub in ("stories", "sleep", "shorts"):
        base = ROOT / "output" / sub
        if not base.exists():
            continue
        for mp4 in sorted(base.rglob("*.mp4")):
            rel = mp4.relative_to(ROOT).as_posix()
            vid = mp4.stem
            thumb = ""
            for cand in (mp4.parent / "thumbnail.jpg", mp4.with_name(mp4.stem + "_thumb.jpg")):
                if cand.exists():
                    thumb = cand.relative_to(ROOT).as_posix()
                    break
            items.append({"id": vid, "type": sub, "path": rel, "thumb": thumb,
                          "dur": ffdur(mp4), "size_mb": round(mp4.stat().st_size / 1e6),
                          "valid": valid_mp4(mp4)})
    return items


def load_decisions():
    if DECISIONS.exists():
        try:
            return json.loads(DECISIONS.read_text()).get("decisions", {})
        except Exception:
            return {}
    return {}


def page():
    items = scan()
    dec = load_decisions()
    cards = ""
    for it in items:
        st = dec.get(it["id"], {}).get("status", "pending")
        color = TYPE_COLOR.get(it["type"], "#888")
        label = TYPE_LABEL.get(it["type"], it["type"])
        poster = f'poster="/{it["thumb"]}"' if it["thumb"] else ""
        bad = not it.get("valid", True)
        badge2 = '<div class="badge" style="background:#ff3b3b">⛔ CORRUPTO — no subir</div>' if bad else ''
        btns = ('<div class="btns"><button class="rj" onclick="decide(\'%s\',\'rejected\')">❌ Rechazar</button></div>' % it['id']
                if bad else
                f'''<div class="btns">
            <button class="ap" onclick="decide('{it['id']}','approved')">✅ Aprobar</button>
            <button class="rj" onclick="decide('{it['id']}','rejected')">❌ Rechazar</button>
          </div>''')
        cards += f'''
        <div class="card {st}{' rejected' if bad else ''}" id="card-{it['id']}" data-id="{it['id']}" data-type="{it['type']}" data-path="{it['path']}" data-valid="{0 if bad else 1}">
          <div class="badge" style="background:{color}">{label} · {it['dur']} · {it['size_mb']}MB</div>
          {badge2}
          <video preload="none" controls {poster} src="/{it['path']}"></video>
          <div class="title">{it['id']}</div>
          {btns}
        </div>'''
    return HTML.replace("{{CARDS}}", cards).replace("{{N}}", str(len(items)))


HTML = """<!doctype html><html lang=es><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>VD Review · VersiculoDeDios</title>
<style>
:root{color-scheme:dark}
body{margin:0;background:#0e0f13;color:#e8e8ea;font:15px/1.5 -apple-system,system-ui,sans-serif}
header{position:sticky;top:0;z-index:10;background:#15161bdd;backdrop-filter:blur(8px);padding:14px 20px;border-bottom:1px solid #262830;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
h1{font-size:17px;margin:0;font-weight:700}
.counts span{margin-right:14px;font-size:13px;color:#9aa0aa}
.counts b{font-size:15px}
.ok{color:#37d67a}.no{color:#ff5a5a}.pe{color:#c9a227}
.save{margin-left:auto;background:#37d67a;color:#06210f;border:0;padding:9px 18px;border-radius:9px;font-weight:700;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;padding:20px}
.card{background:#16181f;border:2px solid #262830;border-radius:14px;overflow:hidden;transition:.15s}
.card.approved{border-color:#37d67a;box-shadow:0 0 0 1px #37d67a55}
.card.rejected{border-color:#ff5a5a;opacity:.55}
.badge{display:inline-block;margin:10px 10px 0;padding:3px 9px;border-radius:6px;font-size:11px;font-weight:700;color:#0e0f13}
video{width:100%;display:block;background:#000;margin-top:8px;max-height:240px}
.title{padding:8px 12px 2px;font-size:13px;color:#aab;word-break:break-all}
.btns{display:flex;gap:8px;padding:10px 12px 14px}
.btns button{flex:1;padding:10px;border:0;border-radius:9px;font-weight:700;cursor:pointer;font-size:14px}
.ap{background:#10351f;color:#37d67a}.rj{background:#351012;color:#ff5a5a}
.card.approved .ap{background:#37d67a;color:#06210f}
.card.rejected .rj{background:#ff5a5a;color:#210606}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#37d67a;color:#06210f;padding:10px 20px;border-radius:10px;font-weight:700;opacity:0;transition:.3s;pointer-events:none}
.toast.show{opacity:1}
</style></head><body>
<header>
  <h1>🕷 VD Review · {{N}} piezas</h1>
  <div class="counts">
    <span class=ok>Aprobados <b id=cAp>0</b></span>
    <span class=no>Rechazados <b id=cRj>0</b></span>
    <span class=pe>Pendientes <b id=cPe>0</b></span>
  </div>
  <button class=save onclick="saveAll()">💾 Guardar decisiones</button>
</header>
<div class=grid>{{CARDS}}</div>
<div class=toast id=toast></div>
<script>
function decide(id,status){
  const c=document.getElementById('card-'+id);
  c.classList.remove('approved','rejected');
  c.classList.add(status);
  c.dataset.status=status;
  recount(); save(false);
}
function recount(){
  let a=0,r=0,p=0;
  document.querySelectorAll('.card').forEach(c=>{
    const s=c.dataset.status||'pending';
    if(s=='approved')a++;else if(s=='rejected')r++;else p++;
  });
  cAp.textContent=a;cRj.textContent=r;cPe.textContent=p;
}
function collect(){
  const d={};
  document.querySelectorAll('.card').forEach(c=>{
    d[c.dataset.id]={status:c.dataset.status||'pending',type:c.dataset.type,path:c.dataset.path};
  });
  return d;
}
function save(toast){
  fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({decisions:collect()})})
    .then(()=>{if(toast)showToast('Guardado en data/vd_review_decisions.json')})
    .catch(()=>{});
}
function saveAll(){save(true)}
function showToast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200)}
// init estados desde server
document.querySelectorAll('.card').forEach(c=>{c.dataset.status=c.classList.contains('approved')?'approved':c.classList.contains('rejected')?'rejected':'pending'});
recount();
</script></body></html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            body = page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            data["reviewed_at"] = datetime.datetime.now().isoformat(timespec="seconds")
            DECISIONS.parent.mkdir(exist_ok=True)
            DECISIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            n = sum(1 for v in data.get("decisions", {}).values() if v["status"] != "pending")
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            print(f"  [save] {DECISIONS.name} — {n} decisiones")
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"VD Review server → http://localhost:{PORT}/")
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as h:
        h.serve_forever()
