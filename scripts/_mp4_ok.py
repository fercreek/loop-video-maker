"""
Helper compartido: valida integridad de un MP4 con ffprobe.
Caza archivos corruptos/incompletos (ej. render cortado por sleep de la Mac)
antes de mostrarlos en review o subirlos al canal.
"""
import subprocess
from pathlib import Path


def valid_mp4(path) -> bool:
    """True si el MP4 existe y ffprobe lee duración>0 + al menos un stream de video."""
    p = Path(path)
    if not p.exists() or p.stat().st_size < 1024:
        return False
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration:stream=codec_type",
             "-of", "default=noprint_wrappers=1", str(p)],
            capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return False
    has_video = "codec_type=video" in out
    dur = 0.0
    for line in out.splitlines():
        if line.startswith("duration="):
            try:
                dur = float(line.split("=", 1)[1])
            except ValueError:
                dur = 0.0
    return has_video and dur > 0.5


if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        print(f"{'✅ válido ' if valid_mp4(f) else '⛔ INVÁLIDO'}  {f}")
