"""gfx group logo (COMMON_10_TITLE logo 192): only the subtitle is redrawn, in English. Cyan fill, white inner outline,
cyan outer outline and a soft dark shadow like the original katakana; the Japanese title and the romaji stay."""
from PIL import Image

import gfx_hexstart as hs

CYAN = (96, 196, 240, 255)
EDGE = (70, 170, 225, 255)
WHITE = (255, 255, 255, 255)
SHADOW = (35, 25, 21, 90)
RECT = (106, 96, 184, 23)


COPY = (244, 253, 232, 15)  # title background 189: Japanese copyright line, bottom right
COPY_INK = (93, 113, 179, 255)


def copyright(row, im):
    """Erase the line by interpolating each column between the rows above and below it (plain gradient there),
    then draw the English right-aligned where the Japanese ended (it runs further left, over more gradient)."""
    x, y, w, h = COPY
    out = im.copy()
    for xx in range(x, x + w):
        a, b = im.getpixel((xx, y - 1)), im.getpixel((xx, y + h))
        for i in range(h):
            t = (i + 1) / (h + 1)
            out.putpixel((xx, y + i), tuple(round(p + (q - p) * t) for p, q in zip(a, b)))
    hs.text(out, row["en"], "os:600:75", 10, [(0, COPY_INK)], 471, 265, align="r")
    return out


def draw(row, im):
    if row["n"] == "189":
        return copyright(row, im)
    x, y, w, h = RECT
    out = im.copy()
    out.paste((0, 0, 0, 0), (x, y + 1, x + w, y + h))
    for xx in range(x, x + w):  # row 96 = faint tops of the old letters beside the wing's white edge: keep the white
        if im.getpixel((xx, y))[0] < 200:
            out.putpixel((xx, y), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    f, size, cx = "os:800:75", 14, x + w // 2
    hs.text(sh, row["en"], f, size, [(2, SHADOW)], cx + 1, 111, align="c", gap=4)
    out.alpha_composite(sh)
    hs.text(out, row["en"], f, size, [(2, EDGE), (1, CYAN), (0, WHITE)], cx, 110, align="c", gap=4)
    return out
