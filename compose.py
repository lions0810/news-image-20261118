#!/usr/bin/env python3
"""Compose the news-image-20261118 entry: a 1024x1024 newspaper front page.

Layout (canvas 1024x1024, white paper background):
  masthead black band ......... y   0..100  "THE WORLD IN ONE DAY" +
                                          "WEDNESDAY, 18 NOVEMBER 2026"
  photo grid, 2x2 ............. y 108..744  two rows of 314
      each cell: photo 500x236 + caption bar 78 (red kicker + bold headline)
  "MORE FROM THE DAY" list .... y 752..1024  heading + 8 one-line headlines

All text is rendered here with PIL (DejaVu fonts); the four panel
illustrations contain no text at all. Output is JPEG bytes written to a
file named entry.png (the competition accepts JPEG bytes under that name),
at most 1,048,576 bytes.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS_DIR = os.path.join(HERE, "panels")
OUT_PATH = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
MASTHEAD_H = 100
MARGIN = 8
CELL_W = 500
PHOTO_H = 228
CAPTION_H = 86
ROW_H = PHOTO_H + CAPTION_H  # 314
GUTTER = 8
GRID_TOP = MASTHEAD_H + MARGIN          # 108
LIST_TOP = GRID_TOP + 2 * ROW_H + GUTTER  # 744
LIST_Y = LIST_TOP + MARGIN              # 752

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PAPER = (250, 248, 242)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
DARK = (20, 20, 20)
GREY = (90, 90, 90)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PANELS = [
    {
        "file": "media-generation-panel-xi-putin-shenzhen-0-92c2fe18-8ecb-4c1f-a04a-138266af03f4.webp",
        "kicker": "CHINA  ·  APEC SUMMIT",
        "headline": "Xi meets Putin in Shenzhen ahead of Trump trilateral talks",
    },
    {
        "file": "media-generation-panel-gulf-war-hormuz-0-93e034b7-9e71-4003-9c4c-b813d149f9d8.webp",
        "kicker": "GULF  ·  WAR",
        "headline": "U.S. strikes Qeshm Island; Iran drones hit U.S. base in Kuwait",
    },
    {
        "file": "media-generation-panel-israel-knesset-0-f3ca275e-2745-4952-afae-64a2553771c5.webp",
        "kicker": "ISRAEL  ·  POLITICS",
        "headline": "Knesset elects Matan Kahana speaker as Netanyahu's foes win",
    },
    {
        "file": "media-generation-panel-alaska-senate-0-6c81b174-11bf-46ee-a0ca-384a49836676.webp",
        "kicker": "U.S.  ·  SENATE",
        "headline": "Peltola beats Sullivan in Alaska; Democrats eye 56\u201344 majority",
    },
]

# (kicker, rest) pairs; each renders as one line: bold red kicker + black text.
MORE = [
    ("UKRAINE", "Putin not ready for serious peace talks; 141 drones over Dnipro"),
    ("CYBER", "Tech-outage wave reaches the U.S. National Security Agency"),
    ("HEALTH", "U.S. loses its measles-free status"),
    ("INDIA", "Cyclone Akvan nears Odisha"),
    ("HAITI", "Thousands march in praise of El Salvador's Bukele"),
    ("MARKETS", "Nvidia revenue doubles to $115.84 billion"),
    ("RUSSIA", "Military plane crash kills 19"),
    ("ASIA", "Quad leaders meet in Manila; Trump announces Philippines trade deal"),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def centre_crop_resize(img, w, h):
    """Centre-crop to the target aspect ratio, then resize to (w, h)."""
    sw, sh = img.size
    target = w / h
    src = sw / sh
    if src > target:  # too wide: crop sides
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        img = img.crop((x0, 0, x0 + nw, sh))
    else:  # too tall: crop top/bottom
        nh = int(sw / target)
        y0 = (sh - nh) // 2
        img = img.crop((0, y0, sw, y0 + nh))
    return img.resize((w, h), Image.LANCZOS)


def wrap_text(draw, text, fnt, max_width, max_lines=2):
    """Greedy word wrap; returns a list of at most max_lines lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    return lines


def fit_headline(draw, text, max_width, start_size=25):
    """Largest bold size (down to 20) whose wrap fits in 2 lines."""
    size = start_size
    while size > 20:
        fnt = font(SANS_BOLD, size)
        if len(wrap_text(draw, text, fnt, max_width)) <= 2:
            return fnt, wrap_text(draw, text, fnt, max_width)
        size -= 1
    fnt = font(SANS_BOLD, 20)
    return fnt, wrap_text(draw, text, fnt, max_width)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    draw.rectangle([0, 0, W, MASTHEAD_H], fill=BLACK)
    title_fnt = font(SERIF_BOLD, 52)
    title = "THE WORLD IN ONE DAY"
    tw = draw.textlength(title, font=title_fnt)
    draw.text(((W - tw) / 2, 8), title, font=title_fnt, fill=WHITE)
    draw.rectangle([MARGIN, 66, W - MARGIN, 68], fill=GOLD)
    date_fnt = font(SANS_BOLD, 24)
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    dw = draw.textlength(date, font=date_fnt)
    draw.text(((W - dw) / 2, 72), date, font=date_fnt, fill=GOLD)

    # ---- 2x2 photo grid -------------------------------------------------
    for i, panel in enumerate(PANELS):
        row, col = divmod(i, 2)
        x0 = MARGIN + col * (CELL_W + GUTTER)
        y0 = GRID_TOP + row * (ROW_H + GUTTER)
        src = Image.open(os.path.join(PANELS_DIR, panel["file"])).convert("RGB")
        img.paste(centre_crop_resize(src, CELL_W, PHOTO_H), (x0, y0))
        draw.rectangle([x0, y0, x0 + CELL_W - 1, y0 + PHOTO_H - 1],
                       outline=BLACK, width=1)
        # caption bar
        cy = y0 + PHOTO_H
        draw.rectangle([x0, cy, x0 + CELL_W, cy + CAPTION_H], fill=WHITE)
        kicker_fnt = font(SANS_BOLD, 16)
        draw.text((x0 + 10, cy + 6), panel["kicker"], font=kicker_fnt, fill=RED)
        head_fnt, lines = fit_headline(draw, panel["headline"], CELL_W - 20)
        ly = cy + 28
        for line in lines:
            draw.text((x0 + 10, ly), line, font=head_fnt, fill=DARK)
            ly += 26

    # ---- MORE FROM THE DAY ----------------------------------------------
    draw.rectangle([0, LIST_TOP, W, LIST_TOP + 2], fill=BLACK)
    head_fnt = font(SANS_BOLD, 22)
    draw.text((MARGIN + 4, LIST_Y + 2), "MORE FROM THE DAY",
              font=head_fnt, fill=BLACK)
    date2_fnt = font(SANS_BOLD, 16)
    right = "18 NOVEMBER 2026"
    rw = draw.textlength(right, font=date2_fnt)
    draw.text((W - MARGIN - 4 - rw, LIST_Y + 7), right,
              font=date2_fnt, fill=GREY)
    draw.rectangle([MARGIN, LIST_Y + 32, W - MARGIN, LIST_Y + 34], fill=GOLD)

    kicker_fnt = font(SANS_BOLD, 18)
    body_fnt = font(SANS, 18)
    line_y = LIST_Y + 44
    line_step = 27
    for kicker, rest in MORE:
        draw.text((MARGIN + 4, line_y), "\u25aa ", font=body_fnt, fill=RED)
        kx = MARGIN + 4 + draw.textlength("\u25aa ", font=body_fnt)
        draw.text((kx, line_y), kicker + ":  ", font=kicker_fnt, fill=RED)
        tx = kx + draw.textlength(kicker + ":  ", font=kicker_fnt)
        draw.text((tx, line_y), rest, font=body_fnt, fill=DARK)
        line_y += line_step

    img.save(OUT_PATH, format="JPEG", quality=88, optimize=True)
    print(f"wrote {OUT_PATH} ({os.path.getsize(OUT_PATH)} bytes)")


if __name__ == "__main__":
    main()
