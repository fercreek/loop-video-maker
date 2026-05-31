"""
swap_thumbnail.py — Reemplaza el thumbnail de un video ya publicado en YouTube.

Uso:
    python3 scripts/swap_thumbnail.py <videoId> <ruta_thumbnail.jpg>

Reusa load_youtube_service() de upload_to_youtube.py (token + refresh).
Solo hace thumbnails().set() — no toca título/desc/privacidad.
"""
import sys, importlib.util
from pathlib import Path

PROJECT = Path(__file__).parent.parent

def main():
    if len(sys.argv) != 3:
        print("Uso: python3 scripts/swap_thumbnail.py <videoId> <thumbnail.jpg>")
        sys.exit(1)
    video_id, thumb = sys.argv[1], sys.argv[2]
    if not Path(thumb).exists():
        print(f"✗ No existe: {thumb}"); sys.exit(1)

    spec = importlib.util.spec_from_file_location("u", str(PROJECT / "scripts" / "upload_to_youtube.py"))
    u = importlib.util.module_from_spec(spec); sys.argv = ["x", "--dry-run"]
    spec.loader.exec_module(u)
    yt = u.load_youtube_service()

    from googleapiclient.http import MediaFileUpload
    yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb)).execute()
    print(f"✓ Thumbnail actualizado: https://youtube.com/watch?v={video_id}")

if __name__ == "__main__":
    main()
