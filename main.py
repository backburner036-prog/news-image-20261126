#!/usr/bin/env python3
"""news-image-20261126 — the world's news of Thursday 26 November 2026
on a single broadsheet front page (1024x1024, Pillow only).

Post-opening rewrite: the same page, redrawn from scratch in this
session. No network access, no randomness, no timestamps in the output,
so two runs produce byte-identical PNGs.

Usage:  python3 main.py   ->  /output/entry.png (or ./entry.png)
"""
import os

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ canvas
PAGE_W, PAGE_H = 1024, 1024
MARGIN = 36
EDGE_L, EDGE_R = MARGIN, PAGE_W - MARGIN
CONTENT_W = EDGE_R - EDGE_L          # 952

PAPER_RGB = (247, 242, 231)          # warm newsprint
INK_RGB = (20, 18, 16)              # near-black
SECONDARY_RGB = (74, 70, 64)        # grey ink for decks and captions
SPOT_RGB = (163, 51, 39)            # brick red, the only spot colour
PANEL_RGB = (232, 224, 208)         # hairline / panel fill (unused fill)
SMOKE_RGB = (122, 116, 106)
SKYLINE_RGB = (52, 46, 40)
TOWER_RGB = (18, 16, 14)
WINDOW_RGB = (247, 222, 160)        # warm lit-window yellow

FONT_DIR_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_DIR_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_DIR_SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_DIR_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_DIR_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_DIR_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_DIR_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

_typefaces = {}


def typeface(path, size):
    """Memoised font loader; falls back to Pillow's default bitmap font."""
    slot = (path, size)
    face = _typefaces.get(slot)
    if face is None:
        try:
            face = ImageFont.truetype(path, size)
        except Exception:
            face = ImageFont.load_default()
        _typefaces[slot] = face
    return face


def fit_lines(pen, text, face, width):
    """Greedy word wrap: pack as many words per line as fit in `width`."""
    wrapped, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if pen.textlength(candidate, font=face) <= width or not current:
            current = candidate
        else:
            wrapped.append(current)
            current = word
    if current:
        wrapped.append(current)
    return wrapped


class Sheet:
    """A blank broadsheet plus a vertical cursor that sections advance."""

    def __init__(self):
        self.image = Image.new("RGB", (PAGE_W, PAGE_H), PAPER_RGB)
        self.pen = ImageDraw.Draw(self.image)
        self.y = 22                      # top margin of the nameplate

    # -- primitives ------------------------------------------------------
    def hline(self, thickness=1, colour=INK_RGB):
        self.pen.rectangle([EDGE_L, self.y, EDGE_R, self.y + thickness - 1],
                           fill=colour)
        self.y += thickness

    def double_hline(self):
        self.hline(3)
        self.y += 2                      # gap between the thick and thin rule
        self.hline(1)
        # self.y now sits 6 below where the double rule started

    def centred(self, text, face, colour=INK_RGB):
        width = self.pen.textlength(text, font=face)
        self.pen.text(((EDGE_L + EDGE_R - width) / 2, self.y), text,
                      font=face, fill=colour)
        self.y += face.size

    def advance(self, amount):
        self.y += amount

    def write_wrapped(self, text, face, width, leading, colour=INK_RGB,
                      x=EDGE_L):
        for line in fit_lines(self.pen, text, face, width):
            self.pen.text((x, self.y), line, font=face, fill=colour)
            self.y += leading


# ------------------------------------------------------------------ the news
MASTHEAD = "THE WORLD IN ONE PAGE"
DATELINE = "THURSDAY 26 NOVEMBER 2026"
DATELINE_NOTE = "SIX STORIES  ·  FIVE REGIONS  ·  ONE DAY, ONE PAGE"

LEAD = {
    "kicker": "HONG KONG  —  LEAD STORY",
    "headline": "FIRE SWEEPS SEVEN TOWERS: 44 DEAD, 279 MISSING IN TAI PO",
    "deck": ("A blaze that began on renovation scaffolding races through "
             "Wang Fuk Court, Hong Kong's deadliest fire in decades."),
    "body": ("HONG KONG — Flames that started on the scaffolding of a "
             "32-storey tower at 2:51 p.m. jumped to seven of the eight "
             "blocks of the Wang Fuk Court estate, rising to a Level 5 "
             "alarm as 767 firefighters fought through the night. "
             "Forty-four people are dead, among them firefighter "
             "Ho Wai-ho, and 279 residents are missing. The estate, "
             "home to some 4,800 people, was wrapped in the "
             "construction netting now blamed for the rapid spread."),
}

BRIEFS = [
    {"kicker": "UKRAINE WAR",
     "headline": "Russia's own books count 490,334 dead",
     "body": ("Leaked Rosstat death records, analysed by the BBC, put "
              "Russian military deaths since February 2022 near half a "
              "million.")},
    {"kicker": "UNITED STATES",
     "headline": "Thanksgiving: 81.5 million on the move",
     "body": ("Macy's parade steps off in New York, markets shut and the "
              "NFL plays three games as America sits down to dinner.")},
    {"kicker": "BANGLADESH",
     "headline": "Garment workers win a 36% pay rise",
     "body": ("Dhaka lifts the minimum wage for entry-level garment "
              "workers in the world's second-biggest clothing exporter.")},
    {"kicker": "SPACE",
     "headline": "Pakistan's first astronaut heads for Tiangong",
     "body": ("Muhammad Zeeshan Ali will fly on China's Shenzhou-24, the "
              "first foreign astronaut aboard its space station.")},
    {"kicker": "CHESS",
     "headline": "Gukesh meets Sindarov for the world crown",
     "body": ("The world champion from India faces Uzbekistan's Javokhir "
              "Sindarov in Geneva for the 2026 title.")},
]

DAY_NUMBERS = [
    ("44", "dead in Tai Po"),
    ("279", "missing in Hong Kong"),
    ("490,334", "Russian war dead counted"),
]

SOURCES_LINE = ("SOURCES: BBC  ·  THE GUARDIAN  ·  CBC  ·  JAGRAN JOSH  ·  "
                "SELFSTUDY   —   ALL EVENTS 26 NOVEMBER 2026")
HERO_CAPTION = "WANG FUK COURT, TAI PO — SEVEN OF EIGHT TOWERS ALIGHT"

# ------------------------------------------------------------------ artwork
TOWER_HEIGHTS = [105, 130, 120, 150, 112, 138, 125]
FLAME_TOWERS = (1, 3, 5)             # the three tallest carry flames
FLAME_LAYERS = [(34, 36), (22, 50), (12, 32)]   # (width, height) per tongue


def paint_skyline(pen, left, top, right, bottom):
    """Stylised Tai Po at night: smoke, seven dark towers, red flames."""
    pen.rectangle([left, top, right, bottom], fill=SKYLINE_RGB)
    # Smoke rises behind the towers: three columns of widening puffs.
    for column_x in (left + 150, left + 470, left + 790):
        for step in range(6):
            radius = 14 + step * 7
            centre_y = top + 34 + step * 20
            pen.ellipse([column_x - radius, centre_y - radius // 2,
                         column_x + radius, centre_y + radius // 2],
                        fill=SMOKE_RGB)
    # Seven towers across the frame, 8 px gutters.
    tower_w = (right - left - 8 * 8) // 7
    for index, height in enumerate(TOWER_HEIGHTS):
        tower_x = left + 8 + index * (tower_w + 8)
        tower_top = bottom - height
        pen.rectangle([tower_x, tower_top, tower_x + tower_w, bottom],
                      fill=TOWER_RGB)
        # Lit windows in a fixed pseudo-random pattern.
        for row in range(4, height - 8, 16):
            for col in range(6, tower_w - 8, 14):
                if (row * 7 + col * 13 + index * 5) % 5 == 0:
                    pen.rectangle([tower_x + col, tower_top + row,
                                   tower_x + col + 5, tower_top + row + 7],
                                  fill=WINDOW_RGB)
        # Layered flame tongues; tallest tower (150) + tallest flame (50)
        # = 200, inside the 210 px hero height.
        if index in FLAME_TOWERS:
            flame_x = tower_x + tower_w // 2
            for flame_w, flame_h in FLAME_LAYERS:
                pen.polygon([(flame_x - flame_w // 2, tower_top + 8),
                             (flame_x + flame_w // 2, tower_top + 8),
                             (flame_x, tower_top - flame_h)], fill=SPOT_RGB)
            pen.polygon([(flame_x - 6, tower_top + 8),
                         (flame_x + 6, tower_top + 8),
                         (flame_x, tower_top - 22)], fill=WINDOW_RGB)
    # Caption bar pinned to the bottom of the hero.
    pen.rectangle([left, bottom - 24, right, bottom], fill=INK_RGB)
    pen.text((left + 10, bottom - 21), HERO_CAPTION,
             font=typeface(FONT_DIR_SANS_BOLD, 14), fill=PAPER_RGB)


# ------------------------------------------------------------------ sections
def paint_masthead(sheet):
    sheet.centred(MASTHEAD, typeface(FONT_DIR_SERIF_BOLD, 54))
    sheet.advance(6)
    sheet.double_hline()
    sheet.advance(8)
    # Dateline left, summary right, on the same row.
    sheet.pen.text((EDGE_L, sheet.y), DATELINE,
                   font=typeface(FONT_DIR_MONO_BOLD, 15), fill=INK_RGB)
    note_face = typeface(FONT_DIR_MONO, 15)
    note_w = sheet.pen.textlength(DATELINE_NOTE, font=note_face)
    sheet.pen.text((EDGE_R - note_w, sheet.y), DATELINE_NOTE,
                   font=note_face, fill=SECONDARY_RGB)
    sheet.advance(24)
    sheet.hline(1)
    sheet.advance(10)


def paint_lead(sheet):
    pen = sheet.pen
    pen.text((EDGE_L, sheet.y), LEAD["kicker"],
             font=typeface(FONT_DIR_SANS_BOLD, 16), fill=SPOT_RGB)
    sheet.advance(26)
    sheet.write_wrapped(LEAD["headline"],
                        typeface(FONT_DIR_SERIF_BOLD, 40), CONTENT_W, 48)
    sheet.advance(2)
    sheet.write_wrapped(LEAD["deck"],
                        typeface(FONT_DIR_SERIF_ITALIC, 20), CONTENT_W, 26,
                        colour=SECONDARY_RGB)
    sheet.advance(8)
    hero_h = 210
    paint_skyline(pen, EDGE_L, sheet.y, EDGE_R, sheet.y + hero_h)
    sheet.advance(hero_h + 12)


def paint_body_columns(sheet):
    """Lead story text in two columns, drop cap opening column one."""
    pen = sheet.pen
    body_face = typeface(FONT_DIR_SERIF, 16)
    leading = 23
    gutter = 24
    col_w = (CONTENT_W - gutter) // 2
    lines = fit_lines(pen, LEAD["body"], body_face, col_w)
    split = (len(lines) + 1) // 2
    columns = [lines[:split], lines[split:]]
    top = sheet.y
    for col_index, column in enumerate(columns):
        cursor_x = EDGE_L + col_index * (col_w + gutter)
        cursor_y = top
        for line_index, line in enumerate(column):
            if col_index == 0 and line_index == 0:
                # Drop cap: oversized first letter, text resumes beside it.
                pen.text((cursor_x, cursor_y - 4), line[0],
                         font=typeface(FONT_DIR_SERIF_BOLD, 44),
                         fill=SPOT_RGB)
                pen.text((cursor_x + 36, cursor_y), line[1:],
                         font=body_face, fill=INK_RGB)
            else:
                pen.text((cursor_x, cursor_y), line,
                         font=body_face, fill=INK_RGB)
            cursor_y += leading
    sheet.y = top + max(len(c) for c in columns) * leading + 10
    sheet.hline(1)
    sheet.advance(12)


def paint_brief_cell(sheet, brief, origin_x, origin_y, cell_w):
    pen = sheet.pen
    pen.text((origin_x, origin_y), brief["kicker"],
             font=typeface(FONT_DIR_SANS_BOLD, 14), fill=SPOT_RGB)
    cursor_y = origin_y + 20
    for line in fit_lines(pen, brief["headline"],
                          typeface(FONT_DIR_SERIF_BOLD, 19), cell_w):
        pen.text((origin_x, cursor_y), line,
                 font=typeface(FONT_DIR_SERIF_BOLD, 19), fill=INK_RGB)
        cursor_y += 24
    for line in fit_lines(pen, brief["body"],
                          typeface(FONT_DIR_SERIF, 15), cell_w):
        pen.text((origin_x, cursor_y), line,
                 font=typeface(FONT_DIR_SERIF, 15), fill=SECONDARY_RGB)
        cursor_y += 21


def paint_numbers_cell(sheet, origin_x, origin_y):
    pen = sheet.pen
    pen.text((origin_x, origin_y), "THE DAY IN NUMBERS",
             font=typeface(FONT_DIR_SANS_BOLD, 14), fill=SPOT_RGB)
    cursor_y = origin_y + 20
    for number, label in DAY_NUMBERS:
        pen.text((origin_x, cursor_y), number,
                 font=typeface(FONT_DIR_SERIF_BOLD, 19), fill=INK_RGB)
        pen.text((origin_x + 110, cursor_y + 3), label,
                 font=typeface(FONT_DIR_SERIF, 15), fill=SECONDARY_RGB)
        cursor_y += 26


def paint_briefs(sheet):
    """Five briefs + a numbers panel in a 2 x 3 grid."""
    gutter = 24
    cell_w = (CONTENT_W - gutter) // 2
    cell_h = 108
    grid_top = sheet.y
    for position, brief in enumerate(BRIEFS):
        row, col = divmod(position, 2)
        paint_brief_cell(sheet, brief,
                         EDGE_L + col * (cell_w + gutter),
                         grid_top + row * cell_h, cell_w)
    paint_numbers_cell(sheet, EDGE_L + cell_w + gutter, grid_top + 2 * cell_h)
    sheet.y = grid_top + 3 * cell_h + 6
    sheet.hline(1)
    sheet.advance(8)
    # Layout guard: the footer must never clip off the bottom of the page.
    assert sheet.y + 16 <= PAGE_H - 6, f"layout overflow: footer at y={sheet.y}"
    sheet.pen.text((EDGE_L, sheet.y), SOURCES_LINE,
                   font=typeface(FONT_DIR_MONO, 13), fill=SECONDARY_RGB)


def render_page():
    sheet = Sheet()
    paint_masthead(sheet)
    paint_lead(sheet)
    paint_body_columns(sheet)
    paint_briefs(sheet)
    return sheet.image


def check_output(path):
    """Gate check: PNG, 1024x1024, <= 1 MiB — mirrors the bounty gate."""
    size = os.path.getsize(path)
    with Image.open(path) as probe:
        assert probe.format == "PNG", probe.format
        assert probe.size == (PAGE_W, PAGE_H), probe.size
    assert size <= 1048576, f"entry too big: {size} bytes"
    return size


def main():
    page = render_page()
    target = "/output/entry.png" if os.path.isdir("/output") else "entry.png"
    page.save(target, "PNG")
    size = check_output(target)
    print(f"wrote {target} {page.size} {size} bytes — VALID")


if __name__ == "__main__":
    main()
