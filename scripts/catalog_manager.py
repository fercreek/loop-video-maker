from __future__ import annotations
#!/usr/bin/env python3
"""
catalog_manager.py — CLI para gestionar el catálogo de videos de @VersiculoDeDios

Uso:
  python3 scripts/catalog_manager.py --summary
  python3 scripts/catalog_manager.py --list --filter script_ready
  python3 scripts/catalog_manager.py --list --filter rendered
  python3 scripts/catalog_manager.py --list --filter pending
  python3 scripts/catalog_manager.py --list --filter uploaded
  python3 scripts/catalog_manager.py --next 10
  python3 scripts/catalog_manager.py --mark-uploaded david-goliat --youtube-id abc123xyz
  python3 scripts/catalog_manager.py --mark-script noe
  python3 scripts/catalog_manager.py --update-views david-goliat --views 1250
"""

import json
import argparse
import sys
from datetime import date
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "data" / "video_catalog.json"

# ── ANSI colors ───────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
RED    = "\033[31m"
DIM    = "\033[2m"
BLUE   = "\033[34m"

# ── Search volume ordering ────────────────────────────────────────────────────
SEARCH_VOL_ORDER = {"muy_alto": 0, "alto": 1, "medio": 2, "bajo": 3}


# ── I/O helpers ───────────────────────────────────────────────────────────────

def load_catalog() -> dict:
    if not CATALOG_PATH.exists():
        print(f"{RED}Error: catálogo no encontrado en {CATALOG_PATH}{RESET}")
        sys.exit(1)
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_catalog(data: dict) -> None:
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{GREEN}Catálogo guardado.{RESET}")


def find_video(videos: list, video_id: str) -> Optional[dict]:
    for v in videos:
        if v["id"] == video_id:
            return v
    return None


# ── Formatters ────────────────────────────────────────────────────────────────

def status_badge(v: dict) -> str:
    s = v["status"]
    if s["uploaded"]:
        return f"{GREEN}SUBIDO{RESET}"
    if s["rendered"]:
        return f"{CYAN}RENDERIZADO{RESET}"
    if s["script"]:
        return f"{YELLOW}GUION LISTO{RESET}"
    return f"{DIM}PENDIENTE{RESET}"


def priority_color(p: int) -> str:
    colors = {1: RED, 2: YELLOW, 3: RESET}
    return colors.get(p, RESET)


def search_vol_label(sv: str) -> str:
    labels = {
        "muy_alto": f"{RED}MUY ALTO{RESET}",
        "alto":     f"{YELLOW}ALTO{RESET}",
        "medio":    f"{CYAN}MEDIO{RESET}",
        "bajo":     f"{DIM}BAJO{RESET}",
    }
    return labels.get(sv, sv)


def print_divider(char: str = "─", width: int = 80) -> None:
    print(char * width)


def print_row(cols: list, widths: list) -> None:
    row = ""
    for i, (col, w) in enumerate(zip(cols, widths)):
        # Strip ANSI for width calculation
        import re
        plain = re.sub(r"\033\[[0-9;]*m", "", col)
        pad = w - len(plain)
        row += col + " " * max(pad, 1) + "  "
    print(row)


def print_header(cols: list, widths: list) -> None:
    header_cols = [f"{BOLD}{c}{RESET}" for c in cols]
    print_row(header_cols, widths)
    print_divider("─", sum(widths) + len(widths) * 3)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_summary(data: dict) -> None:
    videos = data["videos"]
    total = len(videos)

    uploaded  = [v for v in videos if v["status"]["uploaded"]]
    rendered  = [v for v in videos if v["status"]["rendered"] and not v["status"]["uploaded"]]
    scripted  = [v for v in videos if v["status"]["script"] and not v["status"]["rendered"]]
    pending   = [v for v in videos if not v["status"]["script"]]

    print()
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  CATÁLOGO @VersiculoDeDios — RESUMEN{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"  Canal  : {data.get('channel', 'N/A')}")
    print(f"  Última actualización: {data.get('last_updated', 'N/A')}")
    print()

    print(f"  {BOLD}Estado de producción:{RESET}")
    print(f"    {GREEN}Subidos          : {len(uploaded):>3}{RESET}")
    print(f"    {CYAN}Renderizados     : {len(rendered):>3}{RESET}  (listos para subir)")
    print(f"    {YELLOW}Guion listo      : {len(scripted):>3}{RESET}  (listos para renderizar)")
    print(f"    {DIM}Pendientes       : {len(pending):>3}{RESET}  (sin guion)")
    print(f"    {'─' * 34}")
    print(f"    Total en catálogo: {total:>3}")
    print()

    # By type
    from collections import Counter
    type_counts = Counter(v["type"] for v in videos)
    print(f"  {BOLD}Por tipo:{RESET}")
    for t, c in sorted(type_counts.items()):
        print(f"    {t:<20} {c}")
    print()

    # By priority
    p_counts = Counter(v["priority"] for v in videos)
    print(f"  {BOLD}Por prioridad:{RESET}")
    for p in sorted(p_counts.keys()):
        bar = "█" * p_counts[p]
        color = priority_color(p)
        print(f"    {color}P{p}{RESET}: {p_counts[p]:>3}  {DIM}{bar}{RESET}")
    print()

    # Views total if any uploaded with views
    views_data = [(v["title"][:45], v["status"]["views"]) for v in uploaded if v["status"]["views"]]
    if views_data:
        total_views = sum(v for _, v in views_data)
        print(f"  {BOLD}Views acumuladas (subidos con datos): {total_views:,}{RESET}")
        print()

    # Top 5 pending by priority
    pending_sorted = sorted(
        pending,
        key=lambda v: (v["priority"], SEARCH_VOL_ORDER.get(v["search_volume"], 9))
    )[:5]

    if pending_sorted:
        print(f"  {BOLD}Top 5 próximos a producir:{RESET}")
        print_divider("─", 75)
        cols = ["#", "ID", "Título", "P", "Vol"]
        widths = [2, 28, 38, 2, 8]
        print_header(cols, widths)
        for i, v in enumerate(pending_sorted, 1):
            print_row(
                [
                    str(i),
                    v["id"][:28],
                    v["title"][:38],
                    f"{priority_color(v['priority'])}{v['priority']}{RESET}",
                    search_vol_label(v["search_volume"]),
                ],
                widths,
            )
        print()


def cmd_list(data: dict, filter_mode: str) -> None:
    videos = data["videos"]

    filter_map = {
        "script_ready": lambda v: v["status"]["script"] and not v["status"]["rendered"],
        "rendered":     lambda v: v["status"]["rendered"] and not v["status"]["uploaded"],
        "pending":      lambda v: not v["status"]["script"],
        "uploaded":     lambda v: v["status"]["uploaded"],
        "all":          lambda v: True,
    }

    if filter_mode not in filter_map:
        print(f"{RED}Filtro desconocido: {filter_mode}{RESET}")
        print(f"Opciones: {', '.join(filter_map.keys())}")
        sys.exit(1)

    filtered = [v for v in videos if filter_map[filter_mode](v)]

    label_map = {
        "script_ready": "GUION LISTO — pendientes de render",
        "rendered":     "RENDERIZADOS — pendientes de subir",
        "pending":      "PENDIENTES — sin guion",
        "uploaded":     "SUBIDOS A YOUTUBE",
        "all":          "TODOS",
    }

    print()
    print(f"{BOLD}{'=' * 78}{RESET}")
    print(f"{BOLD}  {label_map[filter_mode]} ({len(filtered)}){RESET}")
    print(f"{BOLD}{'=' * 78}{RESET}")

    if not filtered:
        print(f"  {DIM}Sin resultados.{RESET}\n")
        return

    cols   = ["ID", "Título", "Tipo", "P", "Vol", "Estado"]
    widths = [28, 38, 10, 2, 8, 14]
    print_header(cols, widths)

    for v in filtered:
        youtube_extra = ""
        if v["status"]["youtube_url"]:
            youtube_extra = f"  {DIM}{v['status']['youtube_url']}{RESET}"
        views_str = ""
        if v["status"]["views"] is not None:
            views_str = f"  {CYAN}{v['status']['views']:,} views{RESET}"

        print_row(
            [
                v["id"][:28],
                v["title"][:38],
                v["type"][:10],
                f"{priority_color(v['priority'])}{v['priority']}{RESET}",
                search_vol_label(v["search_volume"]),
                status_badge(v),
            ],
            widths,
        )
        if youtube_extra or views_str:
            print(f"  {youtube_extra}{views_str}")
    print()


def cmd_next(data: dict, n: int) -> None:
    videos = data["videos"]

    # Videos without script, ordered by priority ASC then search_volume DESC
    pending = [v for v in videos if not v["status"]["script"]]
    pending_sorted = sorted(
        pending,
        key=lambda v: (v["priority"], SEARCH_VOL_ORDER.get(v["search_volume"], 9))
    )[:n]

    print()
    print(f"{BOLD}{'=' * 78}{RESET}")
    print(f"{BOLD}  PRÓXIMOS {n} VIDEOS A PRODUCIR (por prioridad + volumen){RESET}")
    print(f"{BOLD}{'=' * 78}{RESET}")

    if not pending_sorted:
        print(f"  {GREEN}Todo el catálogo tiene guion. ¡Increíble!{RESET}\n")
        return

    cols   = ["#", "ID", "Título", "Tipo", "P", "Vol", "Escenas", "~Min"]
    widths = [3, 26, 36, 10, 2, 8, 7, 5]
    print_header(cols, widths)

    for i, v in enumerate(pending_sorted, 1):
        print_row(
            [
                str(i),
                v["id"][:26],
                v["title"][:36],
                v["type"][:10],
                f"{priority_color(v['priority'])}{v['priority']}{RESET}",
                search_vol_label(v["search_volume"]),
                str(v["scenes_target"]),
                str(v["duration_est_min"]),
            ],
            widths,
        )
        if v.get("notes"):
            print(f"   {DIM}↳ {v['notes'][:72]}{RESET}")
    print()


def cmd_mark_uploaded(data: dict, video_id: str, youtube_id: str | None) -> None:
    v = find_video(data["videos"], video_id)
    if not v:
        print(f"{RED}Video no encontrado: {video_id}{RESET}")
        sys.exit(1)

    v["status"]["uploaded"] = True
    v["status"]["upload_date"] = str(date.today())

    if youtube_id:
        v["status"]["youtube_id"] = youtube_id
        v["status"]["youtube_url"] = f"https://youtu.be/{youtube_id}"

    save_catalog(data)
    print(f"{GREEN}  [{video_id}] marcado como SUBIDO.{RESET}")
    if youtube_id:
        print(f"  YouTube: https://youtu.be/{youtube_id}")


def cmd_mark_script(data: dict, video_id: str) -> None:
    v = find_video(data["videos"], video_id)
    if not v:
        print(f"{RED}Video no encontrado: {video_id}{RESET}")
        sys.exit(1)

    v["status"]["script"] = True
    save_catalog(data)
    print(f"{YELLOW}  [{video_id}] marcado como GUION LISTO.{RESET}")


def cmd_mark_rendered(data: dict, video_id: str) -> None:
    v = find_video(data["videos"], video_id)
    if not v:
        print(f"{RED}Video no encontrado: {video_id}{RESET}")
        sys.exit(1)

    v["status"]["script"] = True
    v["status"]["rendered"] = True
    save_catalog(data)
    print(f"{CYAN}  [{video_id}] marcado como RENDERIZADO.{RESET}")


def cmd_update_views(data: dict, video_id: str, views: int) -> None:
    v = find_video(data["videos"], video_id)
    if not v:
        print(f"{RED}Video no encontrado: {video_id}{RESET}")
        sys.exit(1)

    v["status"]["views"] = views
    save_catalog(data)
    print(f"{CYAN}  [{video_id}] views actualizadas: {views:,}{RESET}")


def cmd_show(data: dict, video_id: str) -> None:
    v = find_video(data["videos"], video_id)
    if not v:
        print(f"{RED}Video no encontrado: {video_id}{RESET}")
        sys.exit(1)

    s = v["status"]
    print()
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  {v['title']}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"  ID          : {v['id']}")
    print(f"  Tipo        : {v['type']}")
    print(f"  Biblia      : {v['bible_ref']}")
    print(f"  Prioridad   : {priority_color(v['priority'])}P{v['priority']}{RESET}")
    print(f"  Vol búsqueda: {search_vol_label(v['search_volume'])}")
    print(f"  Escenas     : {v['scenes_target']}")
    print(f"  Duración    : ~{v['duration_est_min']} min")
    print(f"  Notas       : {v.get('notes', '')}")
    print()
    print(f"  {BOLD}Estado:{RESET}")
    print(f"    Guion     : {GREEN + 'Sí' if s['script'] else DIM + 'No'}{RESET}")
    print(f"    Renderizado: {GREEN + 'Sí' if s['rendered'] else DIM + 'No'}{RESET}")
    print(f"    Subido    : {GREEN + 'Sí' if s['uploaded'] else DIM + 'No'}{RESET}")
    if s["youtube_url"]:
        print(f"    URL       : {CYAN}{s['youtube_url']}{RESET}")
    if s["upload_date"]:
        print(f"    Subida    : {s['upload_date']}")
    if s["views"] is not None:
        print(f"    Views     : {s['views']:,}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="catalog_manager.py",
        description="Gestor del catálogo de videos @VersiculoDeDios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/catalog_manager.py --summary
  python3 scripts/catalog_manager.py --next 10
  python3 scripts/catalog_manager.py --list --filter pending
  python3 scripts/catalog_manager.py --list --filter script_ready
  python3 scripts/catalog_manager.py --list --filter rendered
  python3 scripts/catalog_manager.py --list --filter uploaded
  python3 scripts/catalog_manager.py --mark-uploaded david-goliat --youtube-id abc123xyz
  python3 scripts/catalog_manager.py --mark-script noe
  python3 scripts/catalog_manager.py --mark-rendered jonas
  python3 scripts/catalog_manager.py --update-views david-goliat --views 1250
  python3 scripts/catalog_manager.py --show abraham-e-isaac
        """,
    )

    # Action flags (mutually exclusive-ish — handled in main)
    p.add_argument("--summary",        action="store_true",  help="Mostrar resumen del catálogo")
    p.add_argument("--list",           action="store_true",  help="Listar videos (usa --filter)")
    p.add_argument("--next",           type=int, metavar="N", help="Mostrar los próximos N a producir")
    p.add_argument("--show",           metavar="ID",         help="Ver detalle de un video")
    p.add_argument("--mark-uploaded",  metavar="ID",         help="Marcar video como subido a YouTube")
    p.add_argument("--mark-script",    metavar="ID",         help="Marcar guion como listo")
    p.add_argument("--mark-rendered",  metavar="ID",         help="Marcar video como renderizado")
    p.add_argument("--update-views",   metavar="ID",         help="Actualizar views de un video")

    # Modifiers
    p.add_argument(
        "--filter",
        default="pending",
        choices=["pending", "script_ready", "rendered", "uploaded", "all"],
        help="Filtro para --list (default: pending)",
    )
    p.add_argument("--youtube-id", metavar="YT_ID", help="YouTube video ID para --mark-uploaded")
    p.add_argument("--views",      type=int,         help="Número de views para --update-views")

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Show help if no action given
    actions = [
        args.summary, args.list, args.next,
        args.show, args.mark_uploaded, args.mark_script,
        args.mark_rendered, args.update_views,
    ]
    if not any(actions):
        parser.print_help()
        sys.exit(0)

    data = load_catalog()

    if args.summary:
        cmd_summary(data)

    elif args.list:
        cmd_list(data, args.filter)

    elif args.next is not None:
        cmd_next(data, args.next)

    elif args.show:
        cmd_show(data, args.show)

    elif args.mark_uploaded:
        cmd_mark_uploaded(data, args.mark_uploaded, args.youtube_id)

    elif args.mark_script:
        cmd_mark_script(data, args.mark_script)

    elif args.mark_rendered:
        cmd_mark_rendered(data, args.mark_rendered)

    elif args.update_views:
        if args.views is None:
            print(f"{RED}Error: --update-views requiere --views N{RESET}")
            sys.exit(1)
        cmd_update_views(data, args.update_views, args.views)


if __name__ == "__main__":
    main()
