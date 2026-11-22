"""gfx group commenu (COMMU_10_COM_MENU): panel headers, 2-3 state menu buttons, Ikaros gym-shirt tag.
Text over a gradient is removed by interpolating each row between the columns just left and right of its rect, then the
English is drawn in the colours sampled from the Japanese (thin white glyphs + 3 px outline on buttons)."""
from collections import Counter

import numpy as np
from PIL import Image

import gfx_hexstart as hs
from gfx_hexstart import WHITE, text, typeset

F_BTN = "os:700:85"
GREYED = {796, 799}
F_HEAD = "os:800:75"
BTN, HEAD = 15, 18


def rowinterp(im, rect):
    """Repaint rect (x, y, w, h): every row blends linearly from the pixel left of it to the pixel right of it."""
    x, y, w, h = rect
    a = np.array(im).astype(float)
    t = (np.arange(w) + 1) / (w + 1)
    for yy in range(y, y + h):
        a[yy, x:x + w] = a[yy, x - 1] * (1 - t[:, None]) + a[yy, x + w] * t[:, None]
    return Image.fromarray(a.round().astype("uint8"))


def sample(im, rect):
    """(outline, fill) colours of the Japanese in rect: commonest strongly-different non-white colour, brightest ink."""
    bg = np.array(rowinterp(im, rect)).astype(int)
    a = np.array(im).astype(int)
    x, y, w, h = rect
    d = np.abs(a - bg).sum(axis=2)[y:y + h, x:x + w] > 60
    px = a[y:y + h, x:x + w][d]
    rgb = [tuple(p[:3]) for p in px if p[3] > 200]
    outline = Counter(c for c in rgb if min(c) < 215).most_common(1)[0][0]
    lum = sorted(rgb, key=lambda c: sum(c))[-max(3, len(rgb) // 20):]
    fill = tuple(int(sum(c[i] for c in lum) / len(lum)) for i in range(3))
    return outline, (WHITE[:3] if max(fill) >= 235 else fill)


# n -> (text rect x, y, w, h, centre x, baseline) ; states of one button share the rect
BUTTONS, BASE = {}, {}
for ns, (x0, x1, y0, y1) in {
    (789, 790): (41, 88, 6, 27), (791, 792): (25, 103, 6, 27), (793, 794): (32, 96, 5, 24),
    (796, 797, 798): (6, 121, 6, 26), (799, 800, 801): (30, 98, 6, 27), (802, 803): (26, 102, 4, 25),
    (805, 806): (25, 103, 5, 26), (807, 808): (39, 89, 5, 26), (809, 810): (11, 116, 5, 25), (811, 812): (33, 95, 5, 26),
}.items():
    for n in ns:
        top, bot = max(3, y0 - 1), min(28, y1 + 2)  # rows 0-2 and 29-31 hold the button's edge lines
        BUTTONS[n] = (x0 - 1, top, x1 - x0 + 3, bot - top + 1)
        BASE[n] = round((y0 + y1) / 2 + 4.5)
HEADERS = {788: (33, 11, 100, 26), 795: (49, 11, 63, 27), 804: (43, 11, 81, 27)}  # rect of the old header text


def button(row, im):
    rect = BUTTONS[int(row["n"])]
    outline, fill = sample(im, rect)
    if int(row["n"]) not in GREYED:
        fill = WHITE[:3]
    out = rowinterp(im, rect)
    text(out, row["en"], F_BTN, BTN, [(3, outline, "hard"), (0, fill)], rect[0] + rect[2] // 2, BASE[int(row["n"])], "c")
    return out


def header(row, im):
    n = int(row["n"])
    rect = HEADERS[n]
    out = rowinterp(im, rect)
    layers = [(2, WHITE, "hard"), (0, (37, 97, 205))] if n == 788 else [(3, (113, 97, 223), "hard"), (0, WHITE)]
    text(out, row["en"], F_HEAD, HEAD, layers, rect[0] + rect[2] // 2, 31, "c", gap=2)
    return out


def tag(row, im):
    """Ikaros's gym-shirt name patch: black katakana over shirt shading; dark pixels are diffused out, then Latin drawn."""
    out = hs.erase_dark(im, TAG, 60, grow=2)
    text(out, row["en"], "os:800:75", 13, [(0, (22, 22, 28))], 86, 142, "c")
    return out


TAG = (62, 128, 49, 19)


def draw(row, im):
    n = int(row["n"])
    if n == 784:
        return tag(row, im)
    if n in HEADERS:
        return header(row, im)
    if n in BUTTONS:
        return button(row, im)
    raise KeyError(n)
