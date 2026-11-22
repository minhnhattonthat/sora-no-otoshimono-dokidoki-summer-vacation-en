"""gfx group hexcard (COMMU_20_HEX_CARD): Don't Take buttons, Choose Special Card title, note, OK/Back footer, effect texts.
Lettering helpers come from gfx_hexstart (same title / footer styles)."""
import numpy as np
from PIL import Image

import gfx_hexstart as hs
from gfx_hexstart import WHITE, text, typeset

GREY = (112, 112, 112)
RED = (230, 0, 17)
F_HINT = hs.F_LABEL
HINT = hs.HINT


def column_fill(im, rect, src_x):
    """Repaint rect with, per row, the colour of column src_x (vertical-gradient buttons)."""
    x, y, w, h = rect
    a = np.array(im)
    for yy in range(y, y + h):
        a[yy, x:x + w] = a[yy, src_x]
    return Image.fromarray(a)


def footer_hint(im, labels, base):
    """OK / Back hint: grey text next to the kept button icons. labels = [(rect, x, string)]."""
    out = im.copy()
    for rect, x, s in labels:
        out = hs._bgfill(out, rect)
        text(out, s, F_HINT, HINT, [(0, GREY)], x, base, "l")
    return out


def button(row, im):
    n = int(row["n"])
    out = column_fill(im, (44, 5, 96, 22), 44)
    outline, fill = ((85, 123, 87), (200, 255, 201)) if n == 963 else (RED, WHITE[:3])
    text(out, row["en"], "os:800:88", 15, [(2, outline, "hard"), (0, fill)], 92, 20, "c")
    return out


def big(row, im):
    out = hs.clear(im, (0, 86, 128, 26))
    text(out, row["en"], "os:800:88", 20, [(3, RED), (2, (254, 241, 242), "hard"), (0, RED)], 64, 105, "c")
    return out


def note(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    text(out, row["en"], hs.F_LABEL, 12, [(0, (19, 146, 16))], 2, 12, "l")
    return out


def effect(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    hs.flat(out, row["en"], hs.F_BODY, 11, WHITE, im.width // 2, 12, 14, im.width - 4, align="c", maxlines=3)
    return out


def draw(row, im):
    n = int(row["n"])
    if n in (963, 964):
        return button(row, im)
    if n == 961:
        return big(row, im)
    if n == 966:
        return hs.title(row, im, 235, 7, 229)
    if n == 967:
        return note(row, im)
    if n == 968:
        return footer_hint(im, [((393, 10, 26, 18), 395, "OK"), ((449, 10, 31, 18), 451, "Back")], 23)
    if 969 <= n <= 974:
        return effect(row, im)
    raise KeyError(n)
