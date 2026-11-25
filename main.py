#!/usr/bin/env python3
"""news-image-20261126 — one image summing up the world's news of
Thursday 26 November 2026. Broadsheet front page, 1024x1024, drawn with
Pillow only. No network. All news data baked in as constants. Deterministic:
two runs write byte-identical PNGs.

Run:  python3 main.py   ->  /output/entry.png (or ./entry.png locally)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)   # warm paper
INK = (20, 18, 16)        # near-black ink
GREY = (74, 70, 64)       # secondary ink
RED = (163, 51, 39)       # single spot colour (brick red)
LIGHT = (232, 224, 208)   # hairline / panel fill

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        try:
            _cache[key] = ImageFont.truetype(path, size)
        except Exception:
            _cache[key] = ImageFont.load_default()
    return _cache[key]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, y, text, f, fill=INK, x0=0, x1=W):
    w = text_w(draw, text, f)
    draw.text(((x0 + x1 - w) / 2, y), text, font=f, fill=fill)
    return y + f.size


def rule(draw, y, x0, x1, weight=1, fill=INK):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)
    return y + weight


def double_rule(draw, y, x0, x1):
    rule(draw, y, x0, x1, 3)
    rule(draw, y + 5, x0, x1, 1)
    return y + 6


# ---------------------------------------------------------------- data
DATE_LINE = "THURSDAY 26 NOVEMBER 2026"
SUB_LINE = "SIX STORIES  ·  FIVE REGIONS  ·  ONE DAY, ONE PAGE"

LEAD_KICKER = "HONG KONG  —  LEAD STORY"
LEAD_HEAD = "FIRE SWEEPS SEVEN TOWERS: 44 DEAD, 279 MISSING IN TAI PO"
LEAD_DECK = ("A blaze that began on renovation scaffolding races through "
             "Wang Fuk Court, Hong Kong's deadliest fire in decades.")
LEAD_BODY = ("HONG KONG — Flames that started on the scaffolding of a "
             "32-storey tower at 2:51 p.m. jumped to seven of the eight "
             "blocks of the Wang Fuk Court estate, rising to a Level 5 "
             "alarm as 767 firefighters fought through the night. "
             "Forty-four people are dead, among them firefighter "
             "Ho Wai-ho, and 279 residents are missing. The estate, "
             "home to some 4,800 people, was wrapped in the "
             "construction netting now blamed for the rapid spread.")

BRIEFS = [
    ("UKRAINE WAR",
     "Russia's own books count 490,334 dead",
     "Leaked Rosstat death records, analysed by the BBC, put Russian "
     "military deaths since February 2022 near half a million."),
    ("UNITED STATES",
     "Thanksgiving: 81.5 million on the move",
     "Macy's parade steps off in New York, markets shut and the NFL "
     "plays three games as America sits down to dinner."),
    ("BANGLADESH",
     "Garment workers win a 36% pay rise",
     "Dhaka lifts the minimum wage for entry-level garment workers in "
     "the world's second-biggest clothing exporter."),
    ("SPACE",
     "Pakistan's first astronaut heads for Tiangong",
     "Muhammad Zeeshan Ali will fly on China's Shenzhou-24, the first "
     "foreign astronaut aboard its space station."),
    ("CHESS",
     "Gukesh meets Sindarov for the world crown",
     "The world champion from India faces Uzbekistan's Javokhir "
     "Sindarov in Geneva for the 2026 title."),
]

FOOTER = ("SOURCES: BBC  ·  THE GUARDIAN  ·  CBC  ·  JAGRAN JOSH  ·  SELFSTUDY   —   "
          "ALL EVENTS 26 NOVEMBER 2026")


# ---------------------------------------------------------------- hero
def draw_hero(draw, x0, y0, x1, y1):
    """Stylised Tai Po skyline: seven dark towers, smoke behind them,
    brick-red flames licking from the three tallest."""
    draw.rectangle([x0, y0, x1, y1], fill=(52, 46, 40))
    # smoke columns first, behind the towers
    for sx in (x0 + 150, x0 + 470, x0 + 790):
        for k in range(6):
            r = 14 + k * 7
            cy = y0 + 34 + k * 20
            draw.ellipse([sx - r, cy - r // 2, sx + r, cy + r // 2],
                         fill=(122, 116, 106))
    towers = 7
    gap = 8
    tw = (x1 - x0 - gap * (towers + 1)) // towers
    base = y1
    heights = [105, 130, 120, 150, 112, 138, 125]
    for i in range(towers):
        tx = x0 + gap + i * (tw + gap)
        th = heights[i]
        ty = base - th
        draw.rectangle([tx, ty, tx + tw, base], fill=(18, 16, 14))
        # lit windows, warm paper colour
        for r in range(4, th - 8, 16):
            for c in range(6, tw - 8, 14):
                if (r * 7 + c * 13 + i * 5) % 5 == 0:
                    draw.rectangle([tx + c, ty + r, tx + c + 5, ty + r + 7],
                                   fill=(247, 222, 160))
        # layered flame tongues on the three tallest towers
        # (tallest tower 150 + tallest flame 50 = 200 <= hero height 210)
        if i in (1, 3, 5):
            fx = tx + tw // 2
            for fw, fh in [(34, 36), (22, 50), (12, 32)]:
                draw.polygon([(fx - fw // 2, ty + 8),
                              (fx + fw // 2, ty + 8),
                              (fx, ty - fh)], fill=RED)
            # pale heart of the flame (window-light colour)
            draw.polygon([(fx - 6, ty + 8), (fx + 6, ty + 8),
                          (fx, ty - 22)], fill=(247, 222, 160))
    # caption bar
    cap = "WANG FUK COURT, TAI PO — SEVEN OF EIGHT TOWERS ALIGHT"
    draw.rectangle([x0, y1 - 24, x1, y1], fill=INK)
    draw.text((x0 + 10, y1 - 21), cap, font=font(SANS_B, 14), fill=PAPER)


# ---------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 36                      # margin
    x0, x1 = m, W - m

    y = 22
    # nameplate
    y = draw_centered(d, y, "THE WORLD IN ONE PAGE", font(SERIF_B, 54))
    y += 6
    y = double_rule(d, y, x0, x1)
    y += 8
    # dateline row
    d.text((x0, y), DATE_LINE, font=font(MONO_B, 15), fill=INK)
    sw = text_w(d, SUB_LINE, font(MONO, 15))
    d.text((x1 - sw, y), SUB_LINE, font=font(MONO, 15), fill=GREY)
    y += 24
    y = rule(d, y, x0, x1, 1)
    y += 10

    # lead kicker
    d.text((x0, y), LEAD_KICKER, font=font(SANS_B, 16), fill=RED)
    y += 26

    # lead headline (serif bold, wraps to <= 3 lines)
    for line in wrap(d, LEAD_HEAD, font(SERIF_B, 40), x1 - x0):
        d.text((x0, y), line, font=font(SERIF_B, 40), fill=INK)
        y += 48
    y += 2
    # deck, italic serif
    for line in wrap(d, LEAD_DECK, font(SERIF_I, 20), x1 - x0):
        d.text((x0, y), line, font=font(SERIF_I, 20), fill=GREY)
        y += 26
    y += 8

    # hero image
    hero_h = 210
    draw_hero(d, x0, y, x1, y + hero_h)
    y += hero_h + 12

    # lead body, two columns, drop cap on first column
    body_f = font(SERIF, 16)
    lh = 23
    col_w = (x1 - x0 - 24) // 2
    body_lines = wrap(d, LEAD_BODY, body_f, col_w)
    half = (len(body_lines) + 1) // 2
    cols = [body_lines[:half], body_lines[half:]]
    y_body = y
    for ci, lines in enumerate(cols):
        cx = x0 + ci * (col_w + 24)
        cy = y_body
        for li, line in enumerate(lines):
            if ci == 0 and li == 0:
                # drop cap: first letter big, rest of line after it
                d.text((cx, cy - 4), line[0], font=font(SERIF_B, 44), fill=RED)
                d.text((cx + 36, cy), line[1:], font=body_f, fill=INK)
            else:
                d.text((cx, cy), line, font=body_f, fill=INK)
            cy += lh
    y = y_body + max(len(c) for c in cols) * lh + 10
    y = rule(d, y, x0, x1, 1)
    y += 12

    # supporting briefs: 2 columns x 3 rows (last cell = index note)
    cell_w = (x1 - x0 - 24) // 2
    cell_h = 108
    for idx, (kicker, head, body) in enumerate(BRIEFS):
        r, c = divmod(idx, 2)
        bx = x0 + c * (cell_w + 24)
        by = y + r * cell_h
        d.text((bx, by), kicker, font=font(SANS_B, 14), fill=RED)
        by += 20
        for line in wrap(d, head, font(SERIF_B, 19), cell_w):
            d.text((bx, by), line, font=font(SERIF_B, 19), fill=INK)
            by += 24
        for line in wrap(d, body, font(SERIF, 15), cell_w):
            d.text((bx, by), line, font=font(SERIF, 15), fill=GREY)
            by += 21
    # sixth cell: the day in numbers
    bx = x0 + cell_w + 24
    by = y + 2 * cell_h
    d.text((bx, by), "THE DAY IN NUMBERS", font=font(SANS_B, 14), fill=RED)
    by += 20
    for num, lab in [("44", "dead in Tai Po"),
                     ("279", "missing in Hong Kong"),
                     ("490,334", "Russian war dead counted")]:
        d.text((bx, by), num, font=font(SERIF_B, 19), fill=INK)
        d.text((bx + 110, by + 3), lab, font=font(SERIF, 15), fill=GREY)
        by += 26
    y += 3 * cell_h + 6
    y = rule(d, y, x0, x1, 1)
    y += 8
    # footer — layout guard: the page must never clip its last line
    assert y + 16 <= H - 6, f"layout overflow: footer at y={y}"
    d.text((x0, y), FOOTER, font=font(MONO, 13), fill=GREY)
    return img


def validate(path):
    """Gate check: PNG, 1024x1024, <= 1 MiB — mirrors the bounty gate."""
    from PIL import Image as _Im
    size = os.path.getsize(path)
    with _Im.open(path) as im:
        assert im.format == "PNG", im.format
        assert im.size == (W, H), im.size
    assert size <= 1048576, f"entry too big: {size} bytes"
    return size


def main():
    img = build()
    out = "/output/entry.png" if os.path.isdir("/output") else "entry.png"
    img.save(out, "PNG")
    size = validate(out)
    print(f"wrote {out} {img.size} {size} bytes — VALID")


if __name__ == "__main__":
    main()
