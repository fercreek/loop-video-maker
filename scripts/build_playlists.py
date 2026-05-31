"""
build_playlists.py — Crea playlists binge-ables y asigna videos.

Lee /tmp/classify.json (sleep/story/lofi videoIds).
Crea playlists nuevas (si no existen por título) y agrega los videos que falten.
Idempotente: no re-agrega videos ya presentes en la playlist.

Uso:
    python3 scripts/build_playlists.py --dry-run    # muestra plan
    python3 scripts/build_playlists.py              # ejecuta (writes a YouTube)
"""
import importlib.util, sys, json, argparse
from pathlib import Path

PROJECT = Path(__file__).parent.parent

PLAYLISTS = {
    "sleep": {
        "title": "PARA DORMIR · Música Cristiana y Salmos (Sin Anuncios)",
        "desc": "Salmos, versículos y música cristiana para dormir profundamente. Autoplay toda la noche, sin anuncios. Descansa en la paz de Dios. 🌙\n\nContenido creado con asistencia de IA 🙏",
    },
    "lofi": {
        "title": "Lo-Fi Cristiano · Para Orar, Estudiar y Descansar",
        "desc": "Música Lo-Fi cristiana para orar, estudiar la Biblia y descansar en Su presencia. 🕯️\n\nContenido creado con asistencia de IA 🙏",
    },
    "story": {
        "title": "Historias de la Biblia · Relatos Narrados",
        "desc": "Las grandes historias de la Biblia narradas: Noé, Moisés, José, Daniel, el Hijo Pródigo y más. 📖\n\nContenido creado con asistencia de IA 🙏",
    },
}


def load_yt():
    spec = importlib.util.spec_from_file_location("u", str(PROJECT / "scripts" / "upload_to_youtube.py"))
    u = importlib.util.module_from_spec(spec); sys.argv = ["x", "--dry-run"]
    spec.loader.exec_module(u)
    return u.load_youtube_service()


def existing_playlists(yt):
    out = {}
    tok = None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=tok).execute()
        for p in r["items"]:
            out[p["snippet"]["title"]] = p["id"]
        tok = r.get("nextPageToken")
        if not tok:
            break
    return out


def playlist_video_ids(yt, pid):
    ids = set(); tok = None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50, pageToken=tok).execute()
        for it in r["items"]:
            ids.add(it["contentDetails"]["videoId"])
        tok = r.get("nextPageToken")
        if not tok:
            break
    return ids


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    classify = json.loads(Path("/tmp/classify.json").read_text())
    yt = load_yt()
    existing = existing_playlists(yt)

    for key, meta in PLAYLISTS.items():
        videos = classify.get(key, [])
        if not videos:
            print(f"[{key}] sin videos — skip"); continue
        title = meta["title"]
        pid = existing.get(title)

        if not pid:
            if args.dry_run:
                print(f"[{key}] CREARÍA playlist: {title}  (+{len(videos)} videos)")
                pid = f"DRY-{key}"
                present = set()
            else:
                r = yt.playlists().insert(part="snippet,status", body={
                    "snippet": {"title": title, "description": meta["desc"], "defaultLanguage": "es"},
                    "status": {"privacyStatus": "public"},
                }).execute()
                pid = r["id"]
                print(f"[{key}] ✓ Playlist creada: {title} → {pid}")
                present = set()
        else:
            print(f"[{key}] reusa playlist existente: {title} ({pid})")
            present = playlist_video_ids(yt, pid)

        added = 0
        for vid, vtitle in videos:
            if vid in present:
                continue
            if args.dry_run:
                added += 1; continue
            try:
                yt.playlistItems().insert(part="snippet", body={
                    "snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}
                }).execute()
                added += 1
            except Exception as e:
                print(f"    ✗ {vid} {vtitle[:30]}: {e}")
        print(f"[{key}] {'agregaría' if args.dry_run else 'agregados'}: {added} videos")

    print("\n" + ("[DRY RUN] — quita --dry-run para ejecutar." if args.dry_run else "Playlists listas."))


if __name__ == "__main__":
    main()
