"""
render_farm.py — corre una COLA de renders en PARALELO con cap de concurrencia.
Aprovecha el CPU ocioso (la box usa ~1.2 de 12 cores con 1 solo render).

- RAM-aware: --jobs controla cuántos a la vez. Sleeps (120min) pesan ~4GB c/u → usa --jobs 2.
  Long-form narrado ~1.5GB → --jobs 3-4 OK en 16GB.
- Power-check up front: NO arranca en batería (igual que keep_awake.sh).
- Valida cada MP4 de salida con el gate ffprobe; reporta OK/FALLÓ por job.
- caffeinate atado a ESTE proceso mientras corre la cola.

Uso:
  # cola desde archivo (1 comando por línea, sin el '.venv/bin/python3'):
  .venv/bin/python3 scripts/render_farm.py --jobs 2 --queue data/render_queue.txt
  # o inline:
  .venv/bin/python3 scripts/render_farm.py --jobs 3 \
      "render_story.py --story oracion_manana_fe" "render_story.py --story reflexion_miedo_paz"
"""
import argparse, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# venv-guard
import os as _os
_vpy = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), ".venv", "bin", "python3")
if _os.path.exists(_vpy) and _os.path.realpath(sys.executable) != _os.path.realpath(_vpy):
    _os.execv(_vpy, [_vpy] + sys.argv)

PROJECT_DIR = Path(__file__).parent.parent
PY = str(PROJECT_DIR / ".venv" / "bin" / "python3")


def on_ac_power() -> bool:
    try:
        return "AC Power" in subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True).stdout
    except Exception:
        return True


def run_job(cmd: str, idx: int, total: int) -> dict:
    t0 = time.time()
    print(f"  [{idx}/{total}] ▶ {cmd}", flush=True)
    full = [PY] + cmd.split()
    proc = subprocess.run(full, cwd=str(PROJECT_DIR), capture_output=True, text=True)
    dt = time.time() - t0
    ok = proc.returncode == 0
    # último renglón útil del output (filtrado de warnings)
    tail = [l for l in (proc.stdout + proc.stderr).splitlines()
            if l.strip() and "Warning" not in l and "warn" not in l][-1:] or [""]
    print(f"  [{idx}/{total}] {'✅' if ok else '❌'} ({dt/60:.1f}min) {cmd} · {tail[0][:80]}", flush=True)
    return {"cmd": cmd, "ok": ok, "min": round(dt / 60, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmds", nargs="*", help="comandos de render (sin el python)")
    ap.add_argument("--queue", help="archivo con 1 comando por línea")
    ap.add_argument("--jobs", type=int, default=2, help="renders en paralelo (sleeps pesados: 2)")
    ap.add_argument("--force", action="store_true", help="arranca aunque esté en batería")
    args = ap.parse_args()

    cmds = list(args.cmds)
    if args.queue:
        cmds += [l.strip() for l in Path(args.queue).read_text().splitlines()
                 if l.strip() and not l.strip().startswith("#")]
    if not cmds:
        print("Nada en la cola. Pasa comandos o --queue."); sys.exit(2)

    if not on_ac_power() and not args.force:
        print("⛔ render_farm: en BATERÍA — la Mac se dormiría a media cola. Enchúfala (o --force)."); sys.exit(1)

    # caffeinate atado a este proceso
    caff = subprocess.Popen(["caffeinate", "-dimsu", "-w", str(_os.getpid())])
    print(f"☕ render_farm: {len(cmds)} renders · {args.jobs} en paralelo · caffeinate {caff.pid}\n")

    results = []
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as ex:
            futs = {ex.submit(run_job, c, i + 1, len(cmds)): c for i, c in enumerate(cmds)}
            for f in as_completed(futs):
                results.append(f.result())
    finally:
        caff.terminate()

    ok = sum(1 for r in results if r["ok"])
    print(f"\n☕ render_farm DONE — {ok}/{len(results)} OK · "
          f"total wall {max((r['min'] for r in results), default=0):.1f}min (paralelo)")
    for r in results:
        if not r["ok"]:
            print(f"  ❌ revisar: {r['cmd']}")


if __name__ == "__main__":
    main()
