"""
Módulo de gestión de versículos bíblicos.
Carga JSONs locales y genera más versículos usando Claude API.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "versiculos"


def cargar_temas() -> list[str]:
    """Retorna lista de temas disponibles leyendo los JSONs en data/versiculos/"""
    temas = []
    if DATA_DIR.exists():
        for f in sorted(DATA_DIR.glob("*.json")):
            temas.append(f.stem)
    return temas


def cargar_versiculos(tema: str) -> dict:
    """Carga el JSON del tema y retorna el dict completo."""
    path = DATA_DIR / f"{tema}.json"
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de versículos para el tema: {tema}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def versiculos_a_lista(datos: dict) -> list[dict]:
    """Convierte el dict del JSON a lista plana de versículos."""
    return datos.get("versiculos", [])


def generar_mas_versiculos(tema: str, cantidad: int, api_key: str) -> list[dict]:
    """
    Llama a Claude API para generar versículos adicionales sobre el tema.
    Retorna lista de dicts con keys: id, texto, referencia, version.
    """
    if not api_key:
        raise ValueError("Se requiere una API key de Claude para generar más versículos.")

    import anthropic

    # Cargar versículos existentes para evitar duplicados
    try:
        datos = cargar_versiculos(tema)
        existentes = [v["referencia"] for v in datos.get("versiculos", [])]
        referencias_existentes = ", ".join(existentes)
    except FileNotFoundError:
        referencias_existentes = "ninguno"

    prompt = f"""Genera exactamente {cantidad} versículos bíblicos sobre el tema "{tema}" en español,
versión Reina Valera 1960 (RVR1960).

REGLAS ESTRICTAS:
1. Solo versículos REALES y VERIFICABLES de la Biblia RVR1960
2. NO inventes versículos ni referencias
3. NO repitas estos versículos que ya existen: {referencias_existentes}
4. Responde SOLO con un JSON array válido, sin texto adicional

Formato exacto de respuesta (JSON array):
[
  {{"texto": "texto del versículo aquí", "referencia": "Libro Capítulo:Versículo", "version": "RVR1960"}},
  ...
]"""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    # Extraer JSON del response (puede venir envuelto en ```json ... ```)
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    nuevos = json.loads(response_text)

    # Asignar IDs
    try:
        datos = cargar_versiculos(tema)
        max_id = max((v.get("id", 0) for v in datos.get("versiculos", [])), default=0)
    except FileNotFoundError:
        max_id = 0

    for i, v in enumerate(nuevos, start=max_id + 1):
        v["id"] = i
        if "version" not in v:
            v["version"] = "RVR1960"

    return nuevos


def guardar_versiculos_extra(tema: str, nuevos: list[dict]) -> None:
    """Agrega versículos nuevos al JSON del tema."""
    datos = cargar_versiculos(tema)
    datos["versiculos"].extend(nuevos)
    path = DATA_DIR / f"{tema}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
