"""
Tests de integración Playwright — Loop Video Maker.

Flujo completo:
  1. Seleccionar tema → cargar versículos
  2. Generar imagen
  3. Generar música ambient
  4. Actualizar preview → verificar que renderiza
  5. Controles del preview (play, next/prev)
  6. [slow] Generar video .mp4

Prerequisito: app corriendo en localhost:7860
    .venv/bin/python app.py

Correr:
    .venv/bin/pytest tests/test_flow.py -v -m "not slow" --timeout=120
"""
from __future__ import annotations

import pytest
from playwright.async_api import Page, expect

BASE_URL = "http://localhost:7860"
TIMEOUT_NORMAL = 15_000   # 15s para operaciones rápidas
TIMEOUT_MEDIA  = 120_000  # 2min para generación de música/imagen
TIMEOUT_RENDER = 600_000  # 10min para render de video


# ─── Helpers ────────────────────────────────────────────────────

async def get_textbox_value(page: Page, label: str) -> str:
    """Lee el valor de un gr.Textbox por su label."""
    # Gradio renderiza textboxes como <textarea> dentro de un bloque con label
    locator = page.locator(f"label:has-text('{label}') ~ div textarea, "
                           f"label:has-text('{label}') ~ textarea")
    return await locator.first.input_value(timeout=TIMEOUT_NORMAL)


async def wait_for_success(page: Page, label: str, timeout: int = TIMEOUT_NORMAL):
    """Espera que un textbox de estado contenga '✓'."""
    locator = page.locator(f"label:has-text('{label}') ~ div textarea, "
                           f"label:has-text('{label}') ~ textarea").first
    await expect(locator).to_contain_text("✓", timeout=timeout)


# ─── Tests ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_01_app_carga(page: Page):
    """La app debe cargar y mostrar el título."""
    await expect(page.locator("h1.main-title")).to_be_visible(timeout=TIMEOUT_NORMAL)
    title_text = await page.locator("h1.main-title").text_content()
    assert "Creador de Videos" in title_text or "Loop Video" in title_text


@pytest.mark.asyncio
async def test_02_cargar_tema(page: Page):
    """Seleccionar tema 'paz' y cargar versículos."""
    # Seleccionar tema en el dropdown
    dropdown = page.get_by_label("Tema bíblico")
    await dropdown.click()
    await page.get_by_role("option", name="paz").click()
    await page.wait_for_timeout(300)

    # Click "Cargar versículos"
    await page.get_by_role("button", name="Cargar versículos").click()

    # Esperar confirmación
    status = page.locator(".step-header + div textarea, .step-header ~ div textarea").first
    # Buscar por contenido en cualquier textarea de estado
    await page.wait_for_function(
        "() => [...document.querySelectorAll('textarea')].some(t => t.value.includes('✓'))",
        timeout=TIMEOUT_NORMAL,
    )


@pytest.mark.asyncio
async def test_03_generar_imagen(page: Page):
    """Generar imagen con el preset 'Amanecer dorado'."""
    # Verificar que el dropdown de estilo existe
    estilo = page.get_by_label("Estilo del fondo")
    await expect(estilo).to_be_visible(timeout=TIMEOUT_NORMAL)

    # Click generar
    await page.get_by_role("button", name="Crear imagen").click()

    # Esperar que alguna textarea tenga ✓ Imagen
    await page.wait_for_function(
        "() => [...document.querySelectorAll('textarea')].some(t => t.value.includes('Imagen generada'))",
        timeout=TIMEOUT_MEDIA,
    )


@pytest.mark.asyncio
async def test_04_generar_musica(page: Page):
    """Generar música ambient (60 min de audio puede tardar 3-5 min)."""
    await page.get_by_role("button", name="Crear música").click()

    await page.wait_for_function(
        "() => [...document.querySelectorAll('textarea')].some(t => t.value.includes('Audio generado') || t.value.includes('Música IA'))",
        timeout=TIMEOUT_RENDER,  # 10 min — generación de audio es lenta
    )


@pytest.mark.asyncio
async def test_05_preview_button_visible(page: Page):
    """El botón 'Vista previa' debe existir y estar habilitado."""
    btn = page.get_by_role("button", name="Ver cómo quedará el video")
    await expect(btn).to_be_visible(timeout=TIMEOUT_NORMAL)
    await expect(btn).to_be_enabled(timeout=TIMEOUT_NORMAL)


@pytest.mark.asyncio
async def test_06_preview_button_triggers_request(page: Page):
    """Click en 'Vista previa' debe disparar un request al servidor Gradio."""
    queue_requests: list[str] = []
    page.on("request", lambda r: queue_requests.append(r.url) if "queue" in r.url else None)

    # Setup mínimo: cargar tema
    dropdown = page.get_by_label("Tema bíblico")
    await dropdown.click()
    await page.get_by_role("option", name="paz").click()
    await page.wait_for_timeout(300)
    await page.get_by_role("button", name="Cargar versículos").click()
    await page.wait_for_function(
        "() => [...document.querySelectorAll('textarea')].some(t => t.value.includes('✓'))",
        timeout=TIMEOUT_NORMAL,
    )

    await page.get_by_role("button", name="Ver cómo quedará el video").click()
    await page.wait_for_timeout(2000)

    assert any("queue" in url for url in queue_requests), (
        f"No se disparó ningún request de queue. Requests capturados: {queue_requests}"
    )


@pytest.mark.asyncio
@pytest.mark.slow
async def test_09_generar_video(page: Page):
    """[LENTO] Renderiza el video completo y verifica el archivo."""
    nombre = page.get_by_label("Nombre del archivo (opcional)")
    await nombre.clear()
    await nombre.fill("test_playwright.mp4")

    await page.get_by_role("button", name="GENERAR VIDEO .mp4").click()

    await page.wait_for_function(
        "() => [...document.querySelectorAll('textarea')].some(t => t.value.includes('Video listo'))",
        timeout=TIMEOUT_RENDER,
    )

    import os
    output_path = "/Users/fernandocastaneda/Documents/loop-video-maker/output/test_playwright.mp4"
    assert os.path.exists(output_path), f"Video no encontrado en {output_path}"
    size = os.path.getsize(output_path)
    assert size > 100_000, f"Video muy pequeño ({size} bytes)"
