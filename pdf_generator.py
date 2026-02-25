from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
import sys
import os

FOOTER_TEXT = "F.H.U. \"RÓŻA\" Baran Mieczysław\n\nTelefon: 608 056 322, 17 243 84 47"

# ====== PDF ======
A4_COLS = 2
A4_ROWS = 5

PAGE_MARGIN_X = 17.5 * mm
PAGE_MARGIN_Y = 11 * mm

A4_HORIZONTAL_SPACING = 5.8 * mm
A4_VERTICAL_SPACING = 5.8 * mm

# ====== KARTA =======
CARD_WIDTH = 50 * mm
CARD_HEIGHT = 85 * mm

CARD_PADDING_TOP = 12 * mm
CARD_PADDING_BOTTOM = 4 * mm
CARD_PADDING_LEFT = 3 * mm
CARD_PADDING_RIGHT = 3 * mm

CONTENT_WIDTH = CARD_WIDTH - CARD_PADDING_LEFT - CARD_PADDING_RIGHT

CROSS_FONT_SIZE = 36
CROSS_SPACING_AFTER = 2 * mm

SPACE_AFTER_NAME = 2 * mm
SPACE_AFTER_DYNAMIC = 4 * mm
SPACE_AFTER_STATIC_TEXT = 3 * mm
SPACE_AFTER_PRAYER = 2 * mm

FOOTER_HEIGHT = 7 * mm
FOOTER_LINE_MARGIN = 2 * mm
FOOTER_LINE_WIDTH = 0.3
FOOTER_PADDING_BOTTOM = 3 * mm

# ===== FONTY ======
NAME_FONT_SIZE = 12
BODY_FONT_SIZE = 7
FOOTER_FONT_SIZE = 5

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pdfmetrics.registerFont(ttfonts.TTFont("Tinos-Bold", resource_path("assets/fonts/Tinos-Bold.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("Tinos-BoldItalic", resource_path("assets/fonts/Tinos-BoldItalic.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("Tinos-Italic", resource_path("assets/fonts/Tinos-Italic.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("Tinos-Regular", resource_path("assets/fonts/Tinos-Regular.ttf")))

def draw_card(c, x, y, data):
    width = CARD_WIDTH
    height = CARD_HEIGHT
    center_x = x + width / 2

    current_y = y + height - CARD_PADDING_TOP

    c.setFont("Helvetica", CROSS_FONT_SIZE)
    c.drawCentredString(center_x, current_y, "✝")
    current_y -= CROSS_SPACING_AFTER

    name_style = ParagraphStyle(
        name="NameStyle",
        fontName="Tinos-BoldItalic",
        fontSize=NAME_FONT_SIZE,
        leading=NAME_FONT_SIZE + 2,
        alignment=1,
    )

    name_text = data["name"].replace("\n", "<br/>")
    p = Paragraph(name_text, name_style)
    w, h = p.wrap(CONTENT_WIDTH, height)
    p.drawOn(c, x + CARD_PADDING_LEFT, current_y - h)
    current_y -= h + SPACE_AFTER_NAME

    body_style = ParagraphStyle(
        name="BodyStyle",
        fontName="Tinos-Regular",
        fontSize=BODY_FONT_SIZE,
        leading=BODY_FONT_SIZE + 3,
        alignment=1,
    )

    dynamic_text = data["dynamic_text"].replace("\n", "<br/>")
    p = Paragraph(dynamic_text, body_style)
    w, h = p.wrap(CONTENT_WIDTH, height)
    p.drawOn(c, x + CARD_PADDING_LEFT, current_y - h)
    current_y -= h + SPACE_AFTER_DYNAMIC

    c.setFont("Tinos-Bold", BODY_FONT_SIZE)
    c.drawCentredString(center_x, current_y, "Prosi o modlitwę...")

    current_font_size = BODY_FONT_SIZE

    prayer_style = ParagraphStyle(
        name="PrayerStyle",
        fontName="Tinos-Italic",
        fontSize=current_font_size,
        leading=current_font_size + 3,
        alignment=0,
    )

    p = Paragraph(data["prayer"].replace("\n", "<br/>"), prayer_style)
    w, h = p.wrap(CONTENT_WIDTH, height)

    footer_top = y + FOOTER_HEIGHT
    available_height = current_y - footer_top - 20
    extra_space = available_height - h

    if extra_space < 0:
        current_font_size -= 1

        prayer_style = ParagraphStyle(
            name="PrayerStyle2",
            fontName="Tinos-Italic",
            fontSize=current_font_size,
            leading=current_font_size + 3,
            alignment=0,
        )

        p = Paragraph(data["prayer"].replace("\n", "<br/>"), prayer_style)
        w, h = p.wrap(CONTENT_WIDTH, height)

        available_height = current_y - footer_top
        extra_space = available_height - h

    if 5 < extra_space:
        current_y -= extra_space / 2
    else:
        current_y -= 3

    p.drawOn(c, x + CARD_PADDING_LEFT, current_y - h)
    current_y -= h + SPACE_AFTER_PRAYER
    c.setFont("Tinos-Italic", current_font_size)
    c.drawRightString(
        x + width - CARD_PADDING_RIGHT,
        current_y,
        "Amen"
    )

    footer_y = y + FOOTER_HEIGHT

    c.setLineWidth(FOOTER_LINE_WIDTH)
    c.line(
        x + FOOTER_LINE_MARGIN,
        footer_y,
        x + width - FOOTER_LINE_MARGIN,
        footer_y
    )

    footer_style = ParagraphStyle(
        name="FooterStyle",
        fontName="Tinos-Regular",
        fontSize=FOOTER_FONT_SIZE,
        leading=3,
        alignment=1,
    )

    available_width = width - (2 * FOOTER_LINE_MARGIN)
    footer_text = FOOTER_TEXT.replace("\n", "<br/>")

    p = Paragraph(footer_text, footer_style)
    w, h = p.wrap(available_width, FOOTER_HEIGHT)
    p.drawOn(
        c,
        x + FOOTER_LINE_MARGIN,
        y + FOOTER_PADDING_BOTTOM
    )

def generate_single_card_pdf(path, data):
    c = canvas.Canvas(path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
    draw_card(c, 0, 0, data)
    c.save()


def generate_a4_sheet_pdf(path, data, show_card_border=False):
    page_width, page_height = A4
    c = canvas.Canvas(path, pagesize=A4)

    visual_width = CARD_HEIGHT
    visual_height = CARD_WIDTH

    start_x = PAGE_MARGIN_X
    start_y = page_height - PAGE_MARGIN_Y

    for row in range(A4_ROWS):
        for col in range(A4_COLS):
            x = start_x + col * (visual_width + A4_HORIZONTAL_SPACING)
            y = start_y - (row + 1) * visual_height - row * A4_VERTICAL_SPACING

            c.saveState()
            c.setLineWidth(0.3)
            if show_card_border:
                c.rect(x, y, visual_width, visual_height)
            c.translate(x, y + visual_height)
            c.rotate(-90)
            draw_card(c, 0, 0, data)
            c.restoreState()

    c.save()