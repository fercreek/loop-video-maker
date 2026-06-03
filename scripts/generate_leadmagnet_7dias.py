#!/usr/bin/env python3
"""
7 Dias de Paz -- Lead Magnet PDF v3
Photo backgrounds with Pillow overlay. Letter 612x792pt. NAVY/GOLD brand.
ALL strings are ASCII-only to avoid invisible-text bug with Helvetica in ReportLab.
"""
import json
import io
import os
import unicodedata
from pathlib import Path
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit, ImageReader

BASE = Path(__file__).parent.parent
VERSICULOS_FILE = BASE / "data" / "versiculos" / "paz.json"
OUT_FILE = BASE / "output" / "etsy" / "leadmagnet_7dias_paz.pdf"
FONDOS = BASE / "output" / "fondos"
BG_STILL  = FONDOS / "fondo_ai_still_waters.jpg"   # cover
BG_CLOUDS = FONDOS / "fondo_ai_heaven_clouds.jpg"  # intro + CTA

# Colors (ReportLab)
NAVY      = HexColor("#0D1220")
NAVY_MID  = HexColor("#1A2340")
GOLD      = HexColor("#C8A96E")
GOLD_LT   = HexColor("#E8D5A3")
WHITE     = HexColor("#FFFFFF")
CREAM     = HexColor("#F5F0E8")

W, H = LETTER  # 612 x 792

# ── GRID CONSTANTS ─────────────────────────────────────────────────────────────
COVER_ZONE_A_TOP = H          # 792
COVER_ZONE_A_BOT = H * 2/3   # 528
COVER_ZONE_B_TOP = H * 2/3   # 528
COVER_ZONE_B_BOT = H * 1/3   # 264
COVER_ZONE_C_TOP = H * 1/3   # 264
COVER_ZONE_C_BOT = 0

DAY_HEADER_H  = 92
DAY_VERSE_H   = 170
DAY_FOOTER_H  = 50

MARGIN = 0.75 * inch   # 54pt

# Overlay: navy #0D1220 at alpha 165 (~65%)
OVERLAY_COLOR = (13, 18, 32)
OVERLAY_ALPHA = 165

# ── ASCII NORMALIZER ────────────────────────────────────────────────────────────
_CHAR_MAP = {
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
    "ñ": "n", "Ñ": "N",
    "ü": "u", "Ü": "U",
    "—": "--", "–": "-", "‒": "-",
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "¿": "?", "¡": "!",
    "…": "...",
    "♥": "+", "❤": "+",
    "º": "o", "ª": "a",
}

def to_ascii(text):
    """Convert Spanish text to ASCII-safe string for ReportLab Helvetica."""
    result = []
    for ch in text:
        if ch in _CHAR_MAP:
            result.append(_CHAR_MAP[ch])
        elif ord(ch) > 127:
            # Try NFD decomposition (strip accent)
            nfd = unicodedata.normalize("NFD", ch)
            base = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
            result.append(base if base else "?")
        else:
            result.append(ch)
    return "".join(result)

# ── BACKGROUND HELPERS ──────────────────────────────────────────────────────────
def make_bg(img_path, overlay_color=OVERLAY_COLOR, overlay_alpha=OVERLAY_ALPHA):
    """
    Open a JPG, scale to cover full page at 2x resolution,
    composite an RGBA overlay, return an io.BytesIO JPEG buffer.
    """
    img = Image.open(img_path).convert("RGBA")
    # Scale to fill 612x792 (2x for sharpness: 1224x1584)
    target_w, target_h = int(W * 2), int(H * 2)
    # Cover-fill: scale so both dims >= target
    iw, ih = img.size
    scale = max(target_w / iw, target_h / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # Center-crop to target
    left = (new_w - target_w) // 2
    top  = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))
    # Overlay
    overlay = Image.new("RGBA", img.size, (*overlay_color, overlay_alpha))
    result = Image.alpha_composite(img, overlay).convert("RGB")
    buf = io.BytesIO()
    result.save(buf, "JPEG", quality=90)
    buf.seek(0)
    return buf

def draw_bg(c, img_path):
    """Draw background+overlay for the current page."""
    buf = make_bg(img_path)
    c.drawImage(ImageReader(buf), 0, 0, W, H)

# ── DRAWING HELPERS ─────────────────────────────────────────────────────────────
def gold_bar(c, y, height=4):
    c.setFillColor(GOLD)
    c.rect(0, y, W, height, fill=1, stroke=0)

def gold_rule(c, y, x1=None, x2=None, lw=0.75):
    c.setStrokeColor(GOLD)
    c.setLineWidth(lw)
    c.line(x1 or MARGIN, y, x2 or W - MARGIN, y)

def ctext(c, text, y, font, size, color):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(W / 2, y, to_ascii(text))

def wrapped_ctext(c, text, y_top, font, size, color, max_w, lh=None):
    lh = lh or size * 1.5
    ascii_text = to_ascii(text)
    lines = simpleSplit(ascii_text, font, size, max_w)
    y = y_top - lh
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        c.drawCentredString(W / 2, y, line)
        y -= lh
    return len(lines) * lh

def write_lines(c, y_top, n, x1=None, x2=None, sp=22):
    x1 = x1 or MARGIN
    x2 = x2 or W - MARGIN
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    y = y_top
    for _ in range(n):
        c.line(x1, y, x2, y)
        y -= sp
    return y

def section_label(c, text, y):
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(GOLD)
    c.drawString(MARGIN, y, to_ascii(text))

def load_versiculos():
    data = json.load(open(VERSICULOS_FILE))
    return data["versiculos"][:7]

# ── PAGE 1: COVER ───────────────────────────────────────────────────────────────
def page_cover(c, verse_text, verse_ref):
    draw_bg(c, BG_STILL)

    # Thin gold bars top/bottom
    gold_bar(c, H - 8, 8)
    gold_bar(c, H - 18, 4)
    gold_bar(c, 0, 8)
    gold_bar(c, 10, 4)

    # ── ZONE A: TITLE (top third) ──
    title_y = COVER_ZONE_A_BOT + (COVER_ZONE_A_TOP - COVER_ZONE_A_BOT) / 2
    ctext(c, "7 DIAS", title_y + 55, "Helvetica-Bold", 64, GOLD)
    ctext(c, "DE PAZ", title_y - 15, "Helvetica-Bold", 64, GOLD)

    rule_y = COVER_ZONE_A_BOT + 30
    gold_rule(c, rule_y, x1=MARGIN + inch, x2=W - MARGIN - inch, lw=1.5)

    # ── ZONE B: VERSE BOX (middle third) ──
    box_pad = 20
    box_x = MARGIN
    box_y = COVER_ZONE_B_BOT + 24
    box_w = W - MARGIN * 2
    box_h = COVER_ZONE_B_TOP - COVER_ZONE_B_BOT - 48

    # Navy mid semi-opaque box via ReportLab (no RGBA needed — overlay photo already darkened)
    c.setFillColor(NAVY_MID)
    c.roundRect(box_x, box_y, box_w, box_h, 10, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.roundRect(box_x, box_y, box_w, box_h, 10, fill=0, stroke=1)

    inner_top = box_y + box_h - box_pad - 10
    wrapped_ctext(c, verse_text, inner_top, "Helvetica-Oblique", 13,
                  GOLD_LT, box_w - 40, lh=20)
    ctext(c, "- " + verse_ref, box_y + 28, "Helvetica-BoldOblique", 11, GOLD)

    # ── ZONE C: INFO (bottom third) ──
    sub_y = COVER_ZONE_C_TOP - 36
    ctext(c, "Devocional gratuito  |  Versiculos de Dios", sub_y,
          "Helvetica", 12, WHITE)

    gold_rule(c, sub_y - 18,
              x1=MARGIN + 0.5 * inch, x2=W - MARGIN - 0.5 * inch, lw=0.75)

    kofi_y = COVER_ZONE_C_TOP / 2 + 20
    ctext(c, "ko-fi.com/versiculosdedios", kofi_y,
          "Helvetica-Bold", 14, GOLD)
    ctext(c, "Accede al planner completo de 30 dias", kofi_y - 22,
          "Helvetica", 10, GOLD_LT)

    ctext(c, "@VersiculoDeDios", 30, "Helvetica", 9, GOLD)
    c.showPage()

# ── PAGE 2: INTRO ───────────────────────────────────────────────────────────────
def page_intro(c):
    draw_bg(c, BG_CLOUDS)
    gold_bar(c, H - 8, 8)
    gold_bar(c, 0, 8)

    ctext(c, "UN REGALO PARA TI", H - 70, "Helvetica-Bold", 16, GOLD)
    gold_rule(c, H - 88, x1=MARGIN + 0.8 * inch, x2=W - MARGIN - 0.8 * inch)

    paras = [
        "Este devocional es un regalo.",
        "",
        "En los proximos 7 dias, la Palabra de Dios te dara paz.",
        "No importa lo que estes enfrentando ahora mismo,",
        "Dios tiene una promesa para ti en cada amanecer.",
        "",
        "Cada dia encontraras:",
        "  +  Un versiculo poderoso sobre la paz de Dios",
        "  +  Un espacio para tu reflexion personal",
        "  +  Un momento de oracion",
        "  +  Gratitud como ancla del corazon",
        "",
        "No necesitas horas. Solo unos minutos contigo y con Dios.",
        "Que estas paginas sean un oasis en tu dia.",
        "",
        "Al terminar los 7 dias encontraras como continuar",
        "con el Planner Devocional completo de 30 dias.",
    ]

    # Draw a semi-transparent backing rect so text stays legible over bright clouds
    text_block_h = (len(paras) + 2) * 20 + 20
    text_block_y = H - 130 - text_block_h
    c.setFillColor(NAVY_MID)
    c.roundRect(MARGIN - 10, text_block_y, W - (MARGIN - 10) * 2,
                text_block_h + 20, 8, fill=1, stroke=0)

    y = H - 130
    for p in paras:
        if p == "":
            y -= 10
            continue
        c.setFont("Helvetica", 12)
        c.setFillColor(WHITE if not p.startswith("  +") else GOLD_LT)
        c.drawString(MARGIN, y, to_ascii(p))
        y -= 20

    gold_rule(c, 90)
    ctext(c, "@VersiculoDeDios", 30, "Helvetica", 9, GOLD)
    c.showPage()

# ── DAILY PAGES ─────────────────────────────────────────────────────────────────
def page_day(c, n, verse_text, verse_ref):
    # WHITE body — clean for printing and writing
    c.setFillColor(WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── HEADER: photo background only in top 92pt ──
    bg = BG_STILL if n % 2 == 1 else BG_CLOUDS
    # Draw photo cropped to header height via clipping
    from reportlab.lib.utils import ImageReader
    from PIL import Image
    import io as _io
    img = Image.open(bg).convert("RGB")
    # Crop top portion proportional to header
    crop_h = int(img.height * DAY_HEADER_H / H)
    img_cropped = img.crop((0, 0, img.width, crop_h))
    buf = _io.BytesIO()
    img_cropped.save(buf, "JPEG", quality=85)
    buf.seek(0)
    c.drawImage(ImageReader(buf), 0, H - DAY_HEADER_H, W, DAY_HEADER_H)

    # Navy overlay on header photo
    c.setFillColor(HexColor("#0D122099"))
    c.rect(0, H - DAY_HEADER_H, W, DAY_HEADER_H, fill=1, stroke=0)
    gold_bar(c, H - DAY_HEADER_H - 4, 4)

    ctext(c, "DIA " + str(n), H - 52, "Helvetica-Bold", 26, GOLD)
    ctext(c, "PAZ  |  Versiculos de Dios", H - 74, "Helvetica", 10, GOLD_LT)

    # ── VERSE BOX ──
    verse_top = H - DAY_HEADER_H - 12
    verse_bot = verse_top - DAY_VERSE_H
    bx = MARGIN
    bw = W - MARGIN * 2

    # Cream box on white body
    c.setFillColor(CREAM)
    c.roundRect(bx, verse_bot, bw, DAY_VERSE_H, 8, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.roundRect(bx, verse_bot, bw, DAY_VERSE_H, 8, fill=0, stroke=1)

    vt_top = verse_bot + DAY_VERSE_H - 18
    wrapped_ctext(c, verse_text, vt_top, "Helvetica-Oblique", 12,
                  NAVY, bw - 40, lh=19)
    ctext(c, "- " + verse_ref, verse_bot + 20, "Helvetica-BoldOblique", 11, GOLD)

    # ── 3 WRITING SECTIONS ──
    write_space = verse_bot - DAY_FOOTER_H
    section_h = write_space / 3

    sections = [
        ("MI REFLEXION:", 5),
        ("MI ORACION DE HOY:", 4),
        ("SOY AGRADECIDO/A POR:", 3),
    ]

    y_cursor = verse_bot - 4
    for label, n_lines in sections:
        y_cursor -= 22
        section_label(c, label, y_cursor)
        y_cursor -= 14
        y_cursor = write_lines(c, y_cursor, n_lines, sp=section_h / n_lines - 2)
        y_cursor -= 8

    # Footer
    gold_rule(c, DAY_FOOTER_H - 8)
    ctext(c, "@VersiculoDeDios", 16, "Helvetica", 9, GOLD)
    c.showPage()

# ── PAGE 10: CTA ────────────────────────────────────────────────────────────────
def page_cta(c):
    draw_bg(c, BG_CLOUDS)
    gold_bar(c, H - 8, 8)
    gold_bar(c, H - 18, 4)
    gold_bar(c, 0, 8)
    gold_bar(c, 10, 4)

    ctext(c, "LO LOGRASTE", H - 100, "Helvetica-Bold", 20, GOLD)
    ctext(c, "7 dias de paz completados.", H - 130, "Helvetica", 13, WHITE)

    gold_rule(c, H - 155, x1=MARGIN + inch, x2=W - MARGIN - inch)

    ctext(c, "Quieres continuar los 30 dias?", H - 200,
          "Helvetica-Bold", 15, GOLD_LT)
    ctext(c, "El Planner Devocional Completo te espera.", H - 225,
          "Helvetica", 12, WHITE)

    # CTA box
    box_y = H / 3
    box_h = 100
    bx = MARGIN + 0.5 * inch
    bw = W - (MARGIN + 0.5 * inch) * 2
    c.setFillColor(NAVY_MID)
    c.roundRect(bx, box_y, bw, box_h, 10, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.roundRect(bx, box_y, bw, box_h, 10, fill=0, stroke=1)

    ctext(c, "ko-fi.com/versiculosdedios", box_y + box_h / 2 + 12,
          "Helvetica-Bold", 18, GOLD)
    ctext(c, "Planner 30 dias  -  Solo $5 USD", box_y + box_h / 2 - 10,
          "Helvetica", 11, GOLD_LT)
    ctext(c, "Gracias por cada cafecito que apoya este ministerio.",
          box_y + 20, "Helvetica-Oblique", 10, WHITE)

    ctext(c, "@VersiculoDeDios", 30, "Helvetica", 9, GOLD)
    c.showPage()

# ── MAIN ────────────────────────────────────────────────────────────────────────
def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    versiculos = load_versiculos()

    c = canvas.Canvas(str(OUT_FILE), pagesize=LETTER)

    page_cover(c, versiculos[0]["texto"], versiculos[0]["referencia"])
    page_intro(c)
    for i, v in enumerate(versiculos, 1):
        page_day(c, i, v["texto"], v["referencia"])
    page_cta(c)

    c.save()

    size = os.path.getsize(OUT_FILE)
    pages = 2 + len(versiculos) + 1
    print(f"PDF generado: {OUT_FILE}")
    print(f"Paginas: {pages}")
    print(f"Tamano: {size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
