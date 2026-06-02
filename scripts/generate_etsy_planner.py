#!/usr/bin/env python3
"""
Generate 30-day Devotional Planner PDF for Etsy — @VersiculoDeDios
Letter size (8.5x11"), navy/gold color scheme, ReportLab
"""

import json
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics

BASE = Path(__file__).parent.parent
VERSICULOS_DIR = BASE / "data" / "versiculos"
OUT_PATH = BASE / "output" / "etsy" / "planner_devocional_30dias.pdf"

# Brand colors
NAVY = HexColor("#0D1220")
GOLD = HexColor("#C8A96E")
GOLD_LIGHT = HexColor("#E8D5A3")
WHITE = colors.white
DARK_GRAY = HexColor("#2A2A3A")
LIGHT_GRAY = HexColor("#F5F3EF")
LINE_COLOR = HexColor("#C8A96E")

W, H = LETTER   # 612 x 792 pts

MARGIN = 0.75 * inch
INNER_W = W - 2 * MARGIN


def load_all_versiculos() -> list[dict]:
    """Load versiculos rotating across themes for 30 days."""
    temas = ["paz", "fe", "sanacion", "esperanza", "fuerza", "gratitud"]
    all_v = []
    pools = {}
    for tema in temas:
        path = VERSICULOS_DIR / f"{tema}.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                pools[tema] = data["versiculos"]

    # Interleave themes for variety
    i = 0
    while len(all_v) < 30:
        tema = temas[i % len(temas)]
        pool = pools.get(tema, [])
        if pool:
            idx = (i // len(temas)) % len(pool)
            all_v.append({**pool[idx], "tema": tema})
        i += 1

    return all_v[:30]


def draw_cover(c: canvas.Canvas):
    """Draw the cover page."""
    # Background
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Subtle gold border frame
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.rect(MARGIN - 0.1 * inch, MARGIN - 0.1 * inch,
           W - 2 * (MARGIN - 0.1 * inch), H - 2 * (MARGIN - 0.1 * inch),
           fill=0, stroke=1)
    # Inner thin border
    c.setLineWidth(0.5)
    c.rect(MARGIN + 0.05 * inch, MARGIN + 0.05 * inch,
           W - 2 * (MARGIN + 0.05 * inch), H - 2 * (MARGIN + 0.05 * inch),
           fill=0, stroke=1)

    # Top decorative line
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(MARGIN + 0.3 * inch, H - MARGIN - 0.6 * inch,
           W - MARGIN - 0.3 * inch, H - MARGIN - 0.6 * inch)

    # Main title
    c.setFillColor(GOLD_LIGHT)
    c.setFont("Helvetica-Bold", 36)
    title1 = "PLANNER DEVOCIONAL"
    c.drawCentredString(W / 2, H - MARGIN - 1.4 * inch, title1)

    c.setFont("Helvetica-Bold", 48)
    c.setFillColor(GOLD)
    title2 = "30 DÍAS"
    c.drawCentredString(W / 2, H - MARGIN - 2.1 * inch, title2)

    # Subtitle
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 18)
    c.drawCentredString(W / 2, H - MARGIN - 2.7 * inch, "Versículos de Dios")

    # Divider ornament
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(W / 2 - 1.5 * inch, H / 2 + 0.2 * inch, W / 2 + 1.5 * inch, H / 2 + 0.2 * inch)
    c.setFont("Helvetica", 14)
    c.setFillColor(GOLD_LIGHT)
    c.drawCentredString(W / 2, H / 2 - 0.15 * inch, "✝")
    c.line(W / 2 - 1.5 * inch, H / 2 - 0.4 * inch, W / 2 + 1.5 * inch, H / 2 - 0.4 * inch)

    # Tagline
    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(W / 2, H / 2 - 0.85 * inch, "Un mes de reflexión, oración y gratitud")
    c.drawCentredString(W / 2, H / 2 - 1.15 * inch, "guiado por la Palabra de Dios")

    # Scripture
    c.setFillColor(GOLD_LIGHT)
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(W / 2, MARGIN + 1.8 * inch, '"Tu palabra es lámpara a mis pies')
    c.drawCentredString(W / 2, MARGIN + 1.5 * inch, 'y lumbrera a mi camino."')
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, MARGIN + 1.15 * inch, "Salmos 119:105")

    # Bottom line
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(MARGIN + 0.3 * inch, MARGIN + 0.7 * inch,
           W - MARGIN - 0.3 * inch, MARGIN + 0.7 * inch)

    # Logo / watermark
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, MARGIN + 0.3 * inch, "@VersiculoDeDios")

    c.showPage()


def draw_intro(c: canvas.Canvas):
    """Draw intro / instructions page."""
    c.setFillColor(LIGHT_GRAY)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header bar
    c.setFillColor(NAVY)
    c.rect(0, H - 1.2 * inch, W, 1.2 * inch, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 0.75 * inch, "CÓMO USAR TU PLANNER")

    # Gold accent line
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(MARGIN, H - 1.4 * inch, W - MARGIN, H - 1.4 * inch)

    y = H - 1.9 * inch
    intro_text = [
        ("Este planner está diseñado para acompañarte durante 30 días de crecimiento "
         "espiritual y conexión con Dios a través de Su Palabra."),
        "",
        "INSTRUCCIONES DE USO:",
        "",
        "1. VERSÍCULO DEL DÍA — Medita en el versículo antes de comenzar tu día. "
           "Léelo en voz alta y permite que sus palabras penetren en tu corazón.",
        "",
        "2. REFLEXIÓN — Escribe tus pensamientos, lo que el versículo significa "
           "para ti hoy, y cómo puedes aplicarlo en tu vida.",
        "",
        "3. ORACIÓN DEL DÍA — Escribe tu oración personal a Dios. "
           "Sé honesto y transparente. No hay palabras incorrectas.",
        "",
        "4. GRATITUD — Anota tres cosas por las que estás agradecido hoy. "
           "La gratitud transforma nuestra perspectiva.",
        "",
        "Que estos 30 días sean de transformación y acercamiento a Dios.",
    ]

    c.setFont("Helvetica", 12)
    c.setFillColor(DARK_GRAY)
    for line in intro_text:
        if line == "":
            y -= 0.15 * inch
            continue
        if line.endswith(":") or line.startswith("INSTRUCCIONES"):
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(NAVY)
        elif line[0].isdigit() and line[1] == ".":
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(DARK_GRAY)
        else:
            c.setFont("Helvetica", 11)
            c.setFillColor(DARK_GRAY)

        # Wrap long lines
        max_chars = 90
        if len(line) > max_chars:
            words = line.split()
            current = ""
            for word in words:
                if len(current + " " + word) <= max_chars:
                    current = (current + " " + word).strip()
                else:
                    c.drawString(MARGIN, y, current)
                    y -= 0.22 * inch
                    current = word
            if current:
                c.drawString(MARGIN, y, current)
                y -= 0.28 * inch
        else:
            c.drawString(MARGIN, y, line)
            y -= 0.28 * inch

    # Footer
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(MARGIN, MARGIN + 0.4 * inch, W - MARGIN, MARGIN + 0.4 * inch)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, MARGIN + 0.15 * inch, "@VersiculoDeDios  ·  Planner Devocional 30 Días")

    c.showPage()


def draw_daily_page(c: canvas.Canvas, dia: int, versiculo: dict):
    """Draw a single daily planner page."""
    tema = versiculo.get("tema", "")
    texto = versiculo.get("texto", "")
    referencia = versiculo.get("referencia") or versiculo.get("ref", "")

    # Background
    c.setFillColor(WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header — navy bar
    c.setFillColor(NAVY)
    c.rect(0, H - 1.1 * inch, W, 1.1 * inch, fill=1, stroke=0)

    # Day number
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, H - 0.55 * inch, f"DÍA {dia}")

    # Tema badge
    tema_label = tema.upper() if tema else ""
    c.setFont("Helvetica", 10)
    c.setFillColor(GOLD_LIGHT)
    c.drawString(MARGIN + 1 * inch, H - 0.55 * inch, f"·  {tema_label}")

    # Page number right
    c.setFont("Helvetica", 10)
    c.setFillColor(GOLD_LIGHT)
    c.drawRightString(W - MARGIN, H - 0.55 * inch, f"{dia} / 30")

    # Gold accent line below header
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(MARGIN, H - 1.25 * inch, W - MARGIN, H - 1.25 * inch)

    # === VERSÍCULO DEL DÍA ===
    y = H - 1.6 * inch

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "VERSÍCULO DEL DÍA")
    y -= 0.05 * inch

    # Thin gold underline
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(MARGIN, y, MARGIN + 1.8 * inch, y)
    y -= 0.25 * inch

    # Verse text box — light gold bg
    verse_box_h = 1.15 * inch
    c.setFillColor(HexColor("#FDF9F0"))
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.roundRect(MARGIN, y - verse_box_h, INNER_W, verse_box_h, 6, fill=1, stroke=1)

    # Verse text — wrap
    verse_y = y - 0.2 * inch
    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica-Oblique", 11)

    # Wrap verse text
    max_chars_verse = 85
    words = texto.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test) <= max_chars_verse:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    lines_shown = lines[:4]  # max 4 lines in box
    for line in lines_shown:
        if verse_y > y - verse_box_h + 0.1 * inch:
            c.drawString(MARGIN + 0.15 * inch, verse_y, line)
            verse_y -= 0.22 * inch

    # Reference — bold gold
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(MARGIN + INNER_W - 0.15 * inch, y - verse_box_h + 0.1 * inch, f"— {referencia}")

    y -= (verse_box_h + 0.25 * inch)

    # === REFLEXIÓN ===
    section_gap = 0.08 * inch
    line_spacing = 0.28 * inch
    num_lines = 5

    def draw_section(label: str, lines_count: int, cur_y: float) -> float:
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, cur_y, label)
        cur_y -= 0.05 * inch
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.8)
        c.line(MARGIN, cur_y, MARGIN + len(label) * 6.5, cur_y)
        cur_y -= 0.22 * inch

        # Writing lines
        c.setStrokeColor(HexColor("#CCBF9B"))
        c.setLineWidth(0.5)
        for j in range(lines_count):
            line_y = cur_y - j * line_spacing
            c.line(MARGIN, line_y, W - MARGIN, line_y)
        cur_y -= lines_count * line_spacing + section_gap
        return cur_y

    y = draw_section("REFLEXIÓN:", 5, y)
    y -= 0.1 * inch
    y = draw_section("ORACIÓN DEL DÍA:", 4, y)
    y -= 0.1 * inch

    # === GRATITUD ===
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "GRATITUD DE HOY:")
    y -= 0.05 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(MARGIN, y, MARGIN + 1.75 * inch, y)
    y -= 0.22 * inch

    gratitud_labels = ["1.", "2.", "3."]
    c.setStrokeColor(HexColor("#CCBF9B"))
    c.setLineWidth(0.5)
    for label in gratitud_labels:
        c.setFillColor(HexColor("#CCBF9B"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, label)
        c.line(MARGIN + 0.25 * inch, y, W - MARGIN, y)
        y -= line_spacing

    # === FOOTER ===
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(MARGIN, MARGIN + 0.42 * inch, W - MARGIN, MARGIN + 0.42 * inch)

    c.setFillColor(HexColor("#888888"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, MARGIN + 0.2 * inch,
                        "@VersiculoDeDios  ·  Planner Devocional 30 Días  ·  RVR1960")

    c.showPage()


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    versiculos = load_all_versiculos()
    print(f"Loaded {len(versiculos)} versiculos for 30 days")

    c = canvas.Canvas(str(OUT_PATH), pagesize=LETTER)
    c.setTitle("Planner Devocional 30 Días · Versículos de Dios")
    c.setAuthor("VersiculoDeDios")
    c.setSubject("Planner devocional cristiano 30 días")

    print("Drawing cover page...")
    draw_cover(c)

    print("Drawing intro page...")
    draw_intro(c)

    print("Drawing 30 daily pages...")
    for i, versiculo in enumerate(versiculos, 1):
        ref = versiculo.get("referencia") or versiculo.get("ref", "")
        print(f"  Día {i:02d} — {ref}")
        draw_daily_page(c, i, versiculo)

    c.save()
    size_mb = OUT_PATH.stat().st_size / (1024 * 1024)
    print(f"\nPDF saved: {OUT_PATH}")
    print(f"Pages: 32 (cover + intro + 30 days)")
    print(f"Size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
