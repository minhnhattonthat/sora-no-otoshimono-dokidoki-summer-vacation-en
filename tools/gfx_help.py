"""gfx group help (COMMU_10_HELP): 947 the Controls title over the wing wallpaper, 949 the controls table.

947: the Japanese title is replaced by the wallpaper's own pattern (it repeats every 65 px down), then Latin is drawn.
949: cells are repainted with the panel's flat translucent colour (dashed separators stay), text drawn flat.
The 949 `en` column lists, split on " | ": 3 headers, the D-Pad label, 9 rows x (Communication, Hexcite), the footnote."""
import numpy as np
from PIL import Image

import gfx_hexstart as hs
from gfx_hexstart import WHITE, text

CELL = (116, 194, 255, 204)
HEADBG = (62, 143, 225, 240)
BLUE = (68, 91, 190)
ROWS = [(33, 22), (57, 22), (81, 21), (104, 22), (128, 22), (152, 22), (176, 21), (199, 22), (223, 22)]  # (y, h) per cell row
COLS = [(84, 101, 134), (189, 110, 244)]  # (x, w, centre) of the Communication / Hexcite columns
HEADS = [(14, 9, 64, 21, 46), (84, 9, 101, 21, 134), (189, 9, 110, 21, 244)]  # (x, y, w, h, centre)
LABEL = (9, 33, 70, 22)  # the D-Pad label cell in column 1
FOOT = (6, 252, 300, 16)
TITLE = (32, 5, 105, 31)


def rects949():
    r = [HEADS[i][:4] for i in range(3)] + [LABEL]
    r += [(x, y, w, h) for y, h in ROWS for x, w, _ in COLS]
    return r + [FOOT]


def paint(a, rect, colour):
    x, y, w, h = rect
    a[y:y + h, x:x + w] = colour


def table(row, im):
    parts = row["en"].split(" | ")
    assert len(parts) == 3 + 1 + 18 + 1, len(parts)
    a = np.array(im)
    for hx, hy, hw, hh, _ in HEADS:
        paint(a, (hx, hy, hw, hh), HEADBG)
    paint(a, LABEL, CELL)
    for y, h in ROWS:
        for x, w, _ in COLS:
            paint(a, (x, y, w, h), CELL)
    paint(a, FOOT, (0, 0, 0, 0))
    a[FOOT[1], 7:302] = (255, 255, 255, 22)  # the panel's bottom glow runs through the footnote's first row
    out = Image.fromarray(a)
    for (hx, hy, hw, hh, cx), s in zip(HEADS, parts[:3]):
        text(out, s, "os:800:75", 13, [(2, (28, 95, 198), "hard"), (0, (240, 240, 30))], cx, 24, "c")
    text(out, parts[3], "os:800:75", 12, [(2, (56, 93, 231), "hard"), (0, (200, 202, 200))], LABEL[0] + LABEL[2] // 2 - 1, 48, "c")
    cells = iter(parts[4:22])
    for y, h in ROWS:
        for x, w, cx in COLS:
            hs.flat(out, next(cells), "os:700:75", 11, BLUE, cx, 0, 11, w - 2, align="c", maxlines=2, cy=y + h / 2)
    text(out, parts[22], "os:800:75", 12, [(2, (79, 113, 229), "hard"), (0, (231, 236, 31))], 10, 263, "l")
    return out


def wallpaper(row, im):
    """Controls title: pattern copied from 65 px lower, then white-outlined blue italic letters."""
    x, y, w, h = TITLE
    out = im.copy()
    out.paste(im.crop((x, y + 65, x + w, y + 65 + h)), (x, y))
    text(out, row["en"], "os:800:75", 22, [(3, WHITE, "hard"), (0, (76, 105, 227))], 38, 30, "l", shear=0.2)
    return out


def draw(row, im):
    n = int(row["n"])
    if n == 947:
        return wallpaper(row, im)
    if n == 949:
        return table(row, im)
    raise KeyError(n)
