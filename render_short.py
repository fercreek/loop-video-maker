"""
render_short.py — Pipeline completo para Shorts devocionales verticales 9:16.

Stack 100% propio (anti-strike):
  - Voz: ElevenLabs ES-MX (API) con fallback a macOS say
  - Música: pool local audio/cache/ (MusicGen / Kevin MacLeod CC-BY)
  - Imagen: fondos AI pool (Gemini Imagen 4.0) o pool horizontal re-escalado
  - Edición: ffmpeg puro — sin CapCut, sin templates externos

Output: MP4 1080x1920, subtítulos quemados, listo para YouTube Shorts.

Uso:
    # 1 short de prueba
    .venv/bin/python3 render_short.py --id fe_001

    # Batch semanal (7 shorts)
    .venv/bin/python3 render_short.py --count 7 --output-dir output/shorts/semana_2026-05-11

    # Batch temático
    .venv/bin/python3 render_short.py --tema paz --count 3

    # Forzar re-render
    .venv/bin/python3 render_short.py --count 7 --force

    # Ver lista de oraciones disponibles
    .venv/bin/python3 render_short.py --list

    # Dry run (no ejecuta, muestra plan)
    .venv/bin/python3 render_short.py --count 7 --dry-run
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import sys
import time
from pathlib import Path

# ─── Path setup ───────────────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))
for _pyver in ["python3.13", "python3.12", "python3.11", "python3.10", "python3.9"]:
    _site = PROJECT_DIR / ".venv" / "lib" / _pyver / "site-packages"
    if _site.exists():
        sys.path.insert(0, str(_site))
        break

from core.narration_gen import generate_narration, get_audio_duration, EDGE_VOICES
from core.shorts_render import (
    ShortClipConfig,
    render_short_clip,
    render_shorts_batch,
)

# ─── Paths ────────────────────────────────────────────────────────────────────
CONFIG_PATH      = PROJECT_DIR / "config.json"
POOL_PATH        = PROJECT_DIR / "data" / "oraciones_pool.json"
MANIFEST_PATH    = PROJECT_DIR / "data" / "shorts_manifest.json"
MUSIC_POOL_DIR   = PROJECT_DIR / "audio" / "cache"
FONDOS_POOL_DIR  = PROJECT_DIR / "output" / "fondos"
SHORTS_OUT_BASE  = PROJECT_DIR / "output" / "shorts"
NARR_DIR         = PROJECT_DIR / "audio" / "narrations"

# ─── Defaults ─────────────────────────────────────────────────────────────────
DEFAULT_VOICE    = "dalia"         # Edge TTS ES-MX femenina (cálida — oraciones)
DEFAULT_WORKERS  = 3               # ffmpeg paralelo (conservador en Mac)
TARGET_BATCH     = 7               # 1 semana de contenido
MAX_SHORT_SEC    = 58              # YouTube clasifica como Short si <60s
MIN_SHORT_SEC    = 25


# ─── Config ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"config.json no encontrado en {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        return json.load(f)


# ─── Pool de oraciones ────────────────────────────────────────────────────────
def load_pool() -> list[dict]:
    """Carga todas las oraciones del pool JSON."""
    if not POOL_PATH.exists():
        raise FileNotFoundError(f"Pool no encontrado: {POOL_PATH}")
    with open(POOL_PATH) as f:
        data = json.load(f)
    return data.get("oraciones", [])


def get_oraciones(
    tema: str | None = None,
    count: int = TARGET_BATCH,
    exclude_ids: set[str] | None = None,
    specific_id: str | None = None,
) -> list[dict]:
    """
    Selecciona oraciones del pool.

    Args:
        tema:        filtrar por tema (fe, paz, esperanza, etc.) — None = todos
        count:       cuántas retornar
        exclude_ids: IDs ya publicados/generados — no repetir
        specific_id: seleccionar 1 oración específica por ID

    Returns:
        Lista de dicts de oraciones seleccionadas
    """
    pool = load_pool()
    exclude_ids = exclude_ids or set()

    # Filtro por id específico
    if specific_id:
        matches = [o for o in pool if o["id"] == specific_id]
        if not matches:
            raise ValueError(f"Oración '{specific_id}' no encontrada en pool")
        return matches

    # Filtro por tema
    if tema:
        pool = [o for o in pool if o.get("tema", "").lower() == tema.lower()]
        if not pool:
            available_temas = sorted({o["tema"] for o in load_pool()})
            raise ValueError(f"Tema '{tema}' no encontrado. Disponibles: {available_temas}")

    # Excluir ya publicados
    pool = [o for o in pool if o["id"] not in exclude_ids]

    if not pool:
        raise ValueError("No hay oraciones disponibles (todos los IDs ya publicados o pool vacío)")

    # Shuffle para variedad, luego tomar count
    random.shuffle(pool)
    return pool[:count]


# ─── Manifest (tracking de publicados) ───────────────────────────────────────
def load_manifest() -> dict:
    """Carga el manifest de shorts generados."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {"generated": [], "published": []}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def get_published_ids() -> set[str]:
    return set(load_manifest().get("published", []))


def register_generated(oracion_id: str, out_path: Path, duration: float) -> None:
    """Registra un short generado en el manifest."""
    manifest = load_manifest()
    # Evitar duplicados
    existing_ids = {e["id"] for e in manifest.get("generated", [])}
    if oracion_id not in existing_ids:
        manifest.setdefault("generated", []).append({
            "id": oracion_id,
            "path": str(out_path),
            "duration": round(duration, 1),
            "generated_at": time.strftime("%Y-%m-%d %H:%M"),
        })
        save_manifest(manifest)


# ─── Selección de imagen de fondo ─────────────────────────────────────────────
# Temas mapeados a nombres de fondos para coherencia visual
_TEMA_FONDO_KEYWORDS: dict[str, list[str]] = {
    "fe":           ["cross", "dove", "faith", "aurora", "galilee", "prayer"],
    "esperanza":    ["sunrise", "dawn", "divine", "aurora", "hope", "morning"],
    "paz":          ["peaceful", "lake", "calm", "garden", "olive", "quiet"],
    "gratitud":     ["temple", "altar", "worship", "thanksgiving", "harvest"],
    "protección":   ["armor", "shield", "mountain", "fortress", "eagle"],
    "sanación":     ["healing", "light", "restore", "spring", "water"],
    "familia":      ["family", "shepherd", "home", "blessing", "cedar"],
    "trabajo":      ["wheat", "harvest", "hands", "provision", "rain"],
}


def get_background_image(tema: str) -> Path:
    """
    Selecciona una imagen de fondo del pool que coincida con el tema.
    Estrategia: primero busca por keywords del tema, si no hay → aleatorio.
    Acepta imágenes 16:9 — el motor shorts_render las convierte a 9:16 con blur.

    Returns:
        Path a imagen JPG del pool de fondos
    """
    all_fondos = sorted(glob.glob(str(FONDOS_POOL_DIR / "*.jpg")))
    if not all_fondos:
        raise FileNotFoundError(
            f"Pool de fondos vacío en {FONDOS_POOL_DIR}. "
            f"Ejecuta: python3 scripts/generate_fondos_ai.py --count 20"
        )

    # Buscar por keywords del tema
    keywords = _TEMA_FONDO_KEYWORDS.get(tema.lower(), [])
    if keywords:
        keyword_matches = [
            f for f in all_fondos
            if any(kw in Path(f).stem.lower() for kw in keywords)
        ]
        if keyword_matches:
            return Path(random.choice(keyword_matches))

    # Fallback: cualquier fondo del pool
    return Path(random.choice(all_fondos))


# ─── Selección de música de fondo ─────────────────────────────────────────────
_TEMA_MUSIC_KEYWORDS: dict[str, list[str]] = {
    "fe":           ["adoracion", "devocion", "gracia", "paz"],
    "esperanza":    ["amanecer", "promesa", "gloria", "manantial"],
    "paz":          ["paz", "reposo", "silencio", "contemplacion"],
    "gratitud":     ["alabanza", "jubilo", "gloria"],
    "protección":   ["paz", "reposo", "solemnidad"],
    "sanación":     ["restauracion", "ungimiento", "sanacion", "paz"],
    "familia":      ["paz", "adoracion"],
    "trabajo":      ["gracia", "promesa"],
}


def get_background_music(tema: str) -> Path | None:
    """
    Selecciona track de música del pool audio/cache/.
    Retorna None si el pool está vacío (el render continúa sin música).
    """
    patterns_by_priority = []

    keywords = _TEMA_MUSIC_KEYWORDS.get(tema.lower(), ["paz"])
    for kw in keywords:
        patterns_by_priority += [
            str(MUSIC_POOL_DIR / f"*{kw}*_norm.aac"),
            str(MUSIC_POOL_DIR / f"*{kw}*.wav"),
        ]

    # Fallback: cualquier track normalizado
    patterns_by_priority += [
        str(MUSIC_POOL_DIR / "*_norm.aac"),
        str(MUSIC_POOL_DIR / "*.wav"),
    ]

    for pattern in patterns_by_priority:
        matches = sorted(glob.glob(pattern))
        if matches:
            chosen = random.choice(matches)
            print(f"  [music] {Path(chosen).name}")
            return Path(chosen)

    print(f"  [music] WARN: Sin música disponible para tema '{tema}'")
    return None


# ─── Narración ────────────────────────────────────────────────────────────────
def generate_short_narration(
    oracion: dict,
    voice: str,
    force: bool = False,
) -> Path:
    """
    Genera narración para una oración.
    - Intenta ElevenLabs si está configurado en config.json
    - Fallback: macOS say

    El texto de narración = hook_text + "\n" + texto de la oración.
    """
    # Texto narrado = hook (si existe) + cuerpo de la oración
    hook = oracion.get("hook_text", oracion.get("hook", ""))
    texto = oracion["texto"]
    full_text = f"{hook}\n{texto}" if hook else texto

    scene_id = f"short_{oracion['id']}"
    resolved_voice = voice if voice in EDGE_VOICES else "dalia"

    return generate_narration(
        text=full_text,
        scene_id=scene_id,
        voice=resolved_voice,
        force=force,
    )


# ─── Pipeline principal ───────────────────────────────────────────────────────
def run_pipeline(
    oraciones: list[dict],
    output_dir: Path,
    voice: str = DEFAULT_VOICE,
    workers: int = DEFAULT_WORKERS,
    force: bool = False,
    dry_run: bool = False,
) -> list[Path]:
    """
    Pipeline completo para N oraciones:
    1. Genera narraciones (paralelo 6 workers — macOS say es CPU-light)
    2. Selecciona imagen + música por oración
    3. Renderiza clips (paralelo workers)
    4. Registra en manifest

    Returns:
        Lista de Paths de MPs generados
    """
    print(f"\n{'='*65}")
    print(f"  SHORTS DEVOCIONALES — {len(oraciones)} oraciones")
    print(f"  Output: {output_dir}")
    print(f"{'='*65}")

    output_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        print("\n[DRY RUN] Plan de producción:")
        for i, o in enumerate(oraciones, 1):
            print(f"  {i:2d}. [{o['id']}] {o['titulo']}")
            print(f"      Tema: {o['tema']} · {len(o['texto'].split())} palabras")
        print(f"\n  Total: {len(oraciones)} shorts")
        print(f"  Tiempo estimado: ~{len(oraciones) * 15 // workers} seg en batch de {workers}x")
        return []

    # ── Paso 1: Narraciones ────────────────────────────────────────────────
    print(f"\n[1/3] Generando narraciones ({len(oraciones)}) [paralelo 6x]...")
    from concurrent.futures import ThreadPoolExecutor

    narr_dict: dict[str, Path] = {}
    errors: list[str] = []

    def _gen_one_narr(oracion: dict) -> tuple[str, Path | None]:
        try:
            path = generate_short_narration(oracion, voice=voice, force=force)
            return oracion["id"], path
        except Exception as e:
            print(f"  [narr] ERROR {oracion['id']}: {e}")
            return oracion["id"], None

    with ThreadPoolExecutor(max_workers=6) as ex:
        for oid, path in ex.map(_gen_one_narr, oraciones):
            if path:
                narr_dict[oid] = path
            else:
                errors.append(oid)

    if errors:
        print(f"  [narr] {len(errors)} narraciones fallaron: {errors}")

    # Filtrar oraciones con narración exitosa
    oraciones_ok = [o for o in oraciones if o["id"] in narr_dict]
    if not oraciones_ok:
        raise RuntimeError("Todas las narraciones fallaron — abortando")

    # ── Paso 2: Selección de recursos visuales/musicales ────────────────────
    print(f"\n[2/3] Asignando fondos e imágenes ({len(oraciones_ok)} shorts)...")
    configs: list[ShortClipConfig] = []

    for oracion in oraciones_ok:
        oid = oracion["id"]
        tema = oracion.get("tema", "fe")

        narr_path = narr_dict[oid]
        # Usa fondo específico de la oración si existe, sino usa tema
        fondo_especifico = oracion.get("fondo")
        if fondo_especifico and (FONDOS_POOL_DIR / fondo_especifico).exists():
            image_path = FONDOS_POOL_DIR / fondo_especifico
        else:
            image_path = get_background_image(tema)
        # Usa música específica si existe en la oración
        musica_especifica = oracion.get("musica")
        if musica_especifica:
            music_path = get_background_music(musica_especifica)
        else:
            music_path = get_background_music(tema)
        hook_text = oracion.get("hook", oracion.get("hook_text", ""))

        # Segunda imagen: diferente a la primera, para corte a los 18s (v3)
        fondo2_especifico = oracion.get("fondo2")
        if fondo2_especifico and (FONDOS_POOL_DIR / fondo2_especifico).exists():
            image2_path = FONDOS_POOL_DIR / fondo2_especifico
        else:
            # Elegir imagen distinta del pool del mismo tema
            all_fondos = sorted(glob.glob(str(FONDOS_POOL_DIR / "*.jpg")))
            candidatos = [f for f in all_fondos if f != str(image_path)]
            image2_path = Path(random.choice(candidatos)) if candidatos else None

        out_filename = f"short_{oid}_{time.strftime('%Y%m%d')}.mp4"
        out_path = output_dir / out_filename

        configs.append(ShortClipConfig(
            oracion_id=oid,
            text=oracion["texto"],
            narr_path=narr_path,
            image_path=image_path,
            image2_path=image2_path,
            out_path=out_path,
            music_path=music_path,
            hook_text=hook_text,
            force=force,
        ))

        img2_name = image2_path.name if image2_path else "—"
        print(f"  {oid}: {image_path.name} → {img2_name} + {music_path.name if music_path else 'sin música'}")

    # ── Paso 3: Render batch ────────────────────────────────────────────────
    print(f"\n[3/3] Renderizando {len(configs)} clips [paralelo {workers}x]...")
    t0 = time.time()

    generated_paths = render_shorts_batch(configs, max_workers=workers)

    elapsed = time.time() - t0
    print(f"\n  Render completado en {elapsed:.1f}s ({elapsed/len(configs):.1f}s/short)")

    # ── Registro en manifest ────────────────────────────────────────────────
    for cfg in configs:
        if cfg.out_path.exists():
            dur = get_audio_duration(cfg.narr_path)
            register_generated(cfg.oracion_id, cfg.out_path, dur)

    # ── Resumen ─────────────────────────────────────────────────────────────
    total_size_mb = sum(
        p.stat().st_size / 1024 / 1024
        for p in generated_paths
        if p.exists()
    )

    print(f"\n{'='*65}")
    print(f"  LISTO: {len(generated_paths)}/{len(configs)} shorts generados")
    print(f"  Tamaño total: {total_size_mb:.1f} MB")
    print(f"  Output: {output_dir}")
    if generated_paths:
        print(f"\n  Archivos:")
        for p in generated_paths:
            size_mb = p.stat().st_size / 1024 / 1024 if p.exists() else 0
            print(f"    {p.name} ({size_mb:.1f}MB)")
    print(f"\n  SIGUIENTE PASO: Verificar derechos en YouTube Studio antes de subir.")
    print(f"  Anti-strike: Studio → Subir → Verificar derechos → OK → Publicar")
    print(f"{'='*65}")

    return generated_paths


# ─── CLI ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Renderiza Shorts devocionales verticales 9:16 para @VersiculoDeDios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s --id fe_001                                        # 1 short específico
  %(prog)s --count 7                                          # batch semanal
  %(prog)s --tema paz --count 3                               # 3 shorts de paz
  %(prog)s --count 7 --output-dir output/shorts/semana_2026-05-11
  %(prog)s --list                                             # ver pool
  %(prog)s --count 7 --dry-run                               # ver plan sin ejecutar
        """,
    )

    parser.add_argument(
        "--id",
        metavar="ORACION_ID",
        action="append",
        dest="ids",
        help="ID de oración específica (repetible: --id fe_001 --id paz_001)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=TARGET_BATCH,
        metavar="N",
        help=f"Número de shorts a generar (default: {TARGET_BATCH})",
    )
    parser.add_argument(
        "--tema",
        metavar="TEMA",
        help="Filtrar por tema: fe, esperanza, paz, gratitud, protección, sanación, familia, trabajo",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=None,
        help="Directorio de salida (default: output/shorts/semana_YYYY-MM-DD)",
    )
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        choices=list(EDGE_VOICES),
        help=f"Voz Edge TTS ES-MX (default: {DEFAULT_VOICE})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        metavar="N",
        help=f"Workers paralelos para ffmpeg (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-generar aunque ya existan narración y clip en caché",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrar plan sin ejecutar ffmpeg ni ElevenLabs",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar todas las oraciones disponibles en el pool",
    )
    parser.add_argument(
        "--no-exclude",
        action="store_true",
        help="Ignorar manifest — no excluir IDs ya publicados",
    )

    args = parser.parse_args()

    # ── --list ──────────────────────────────────────────────────────────────
    if args.list:
        pool = load_pool()
        manifest = load_manifest()
        published = set(manifest.get("published", []))
        generated = {e["id"] for e in manifest.get("generated", [])}

        print(f"\nPool de oraciones — {len(pool)} total\n")
        temas: dict[str, list] = {}
        for o in pool:
            temas.setdefault(o["tema"], []).append(o)

        for tema, oraciones in sorted(temas.items()):
            print(f"[{tema.upper()}]")
            for o in oraciones:
                status = ""
                if o["id"] in published:
                    status = " [PUBLICADO]"
                elif o["id"] in generated:
                    status = " [generado]"
                words = len(o["texto"].split())
                print(f"  {o['id']:<20s} {o['titulo'][:50]:<50s} ({words}p){status}")
        print()
        return

    # ── Seleccionar oraciones ────────────────────────────────────────────────
    exclude_ids = set() if args.no_exclude else get_published_ids()

    ids = args.ids  # list[str] | None  (--id es ahora action="append")
    if ids:
        # Múltiples --id: cargar cada uno directamente del pool
        pool = load_pool()
        pool_by_id = {o["id"]: o for o in pool}
        oraciones = [pool_by_id[i] for i in ids if i in pool_by_id]
        missing = [i for i in ids if i not in pool_by_id]
        if missing:
            print(f"⚠ IDs no encontrados en pool: {missing}")
    else:
        oraciones = get_oraciones(
            tema=args.tema,
            count=args.count,
            exclude_ids=exclude_ids,
            specific_id=None,
        )

    # ── Output dir ──────────────────────────────────────────────────────────
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        week_label = time.strftime("%Y-%m-%d")
        output_dir = SHORTS_OUT_BASE / f"semana_{week_label}"

    # ── Ejecutar pipeline ────────────────────────────────────────────────────
    run_pipeline(
        oraciones=oraciones,
        output_dir=output_dir,
        voice=args.voice,
        workers=args.workers,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
