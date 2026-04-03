"""
Configuración de pytest para tests de Loop Video Maker.

Prerequisito: la app debe estar corriendo en localhost:7860
    .venv/bin/python app.py

Correr tests:
    .venv/bin/pytest tests/ -v -m "not slow"
"""
from __future__ import annotations

import pytest_asyncio
from playwright.async_api import async_playwright, Page


BASE_URL = "http://localhost:7860"


@pytest_asyncio.fixture()
async def page() -> Page:
    """Fixture de página — function scope (una por test)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1400, "height": 900})
        pg = await ctx.new_page()
        await pg.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        yield pg
        await browser.close()


@pytest_asyncio.fixture()
async def page_con_preview() -> Page:
    """
    Página con preview ya renderizado (carga tema + vista previa).
    Útil para tests de controles del preview.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1400, "height": 900})
        pg = await ctx.new_page()
        await pg.goto(BASE_URL, wait_until="networkidle", timeout=30000)

        # Setup: cargar tema
        dropdown = pg.get_by_label("Tema bíblico")
        await dropdown.click()
        await pg.get_by_role("option", name="paz").click()
        await pg.wait_for_timeout(300)
        await pg.get_by_role("button", name="Cargar versículos").click()
        await pg.wait_for_function(
            "() => [...document.querySelectorAll('textarea')].some(t => t.value.includes('✓'))",
            timeout=15000,
        )

        # Setup: click vista previa (genera imagen placeholder automáticamente)
        await pg.get_by_role("button", name="Vista previa").click()
        # Esperar a que el HTML del preview aparezca en el DOM (Gradio usa SSE)
        await pg.wait_for_function(
            "() => document.querySelector('.preview-root') !== null",
            timeout=30000,
        )

        yield pg
        await browser.close()
