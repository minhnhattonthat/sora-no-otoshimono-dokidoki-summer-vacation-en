"""Graphics group hexmenu (COMMON_20_HEX_MENU): Hexcite piece prompt, pause menus, title, Yes/No, special-move cards.
Parts of one image are '|'-separated in the en column.  Panels with a dotted pattern are cleaned with U.refill."""
import gfx_usecard as U
from gfx import typeset

BLUE = (1, 142, 221, 255)
PINK = (249, 77, 172, 255)
CARDPINK = (246, 106, 169, 255)
HALO = [(2, (236, 247, 255, 255))]
CARDHALO = [(1, (236, 247, 255, 255))]
TITLE = "os:800:80"
ITEM = "os:800:85"


def DARK(p):  # the blue letter cores (dots in the pattern are lighter)
    return p[0] < 60 and p[3] > 200


def menu(im, items, rect_x, rows, color, size=15):
    """Three-line pop-up menus: bullet at the left is kept, the text right of rect_x is replaced."""
    for s, (y, h) in zip(items, rows):
        U.clear(im, (rect_x, y, im.width - rect_x, h))
        U.put(im, s, (rect_x + 2, y, im.width - rect_x - 2, h), ITEM, size, color, HALO, align="l", dy=0)


def effect(im, s, box, size=14):
    s = typeset.wrap(s, "os:700:85", size, box[2] - 10)
    assert s.count("\n") < 3, s
    U.put(im, s, box, "os:700:85", size, BLUE, CARDHALO, align="l", valign="t", spacing=-1)


def draw(r, im):
    im = im.copy()
    n = int(r["n"])
    parts = r["en"].split("|")
    if n == 212:  # title | label | label
        title, l1, l2 = parts
        U.refill(im, (13, 16, 217, 20), lambda j: 20, DARK, line_rows=(32, 33, 34, 35), fade_from=215)
        U.put(im, title, (13, 14, 217, 22), TITLE, 18, BLUE, align="l", dx=4, shear=0.2)
        U.erase(im, (14, 50, 56, 21))
        U.erase(im, (74, 50, 36, 21))
        U.put(im, l1, (14, 50, 56, 21), ITEM, 15, PINK, HALO, align="l", dx=-2)
        U.put(im, l2, (74, 50, 36, 21), ITEM, 15, PINK, HALO, align="l", dx=-2)
    elif n in (217, 218):
        menu(im, parts, 24 if n == 217 else 28, ((2, 20), (26, 20), (50, 20)) if n == 217 else ((1, 22), (25, 22), (49, 22)),
             BLUE if n == 217 else (255, 103, 187, 255))
    elif n in (220, 221):
        menu(im, parts, 24 if n == 220 else 28, ((2, 20), (26, 20), (50, 20)) if n == 220 else ((1, 22), (25, 22), (49, 22)),
             BLUE if n == 220 else (255, 103, 187, 255))
    elif n == 219:
        U.refill(im, (122, 18, 164, 24), lambda j: 24 if j < 36 else -24, DARK, line_rows=(36, 37, 38, 39))
        U.put(im, parts[0], (122, 16, 156, 24), TITLE, 18, BLUE, align="r", shear=0.2)
    elif n == 222:  # title | Move: | Effect:
        title, l1, l2 = parts
        U.refill(im, (20, 18, 186, 22), lambda j: 24 if j < 32 else (-16 if j < 35 else -20), DARK,
                 line_rows=(35, 36, 37, 38), fade_from=195)
        U.put(im, title, (20, 17, 186, 22), TITLE, 18, BLUE, align="l", dx=4, shear=0.2)
        U.refill(im, (120, 60, 53, 22), lambda j: 48, lambda p: p[0] > 240 and p[1] < 110, grow=3)
        U.refill(im, (120, 84, 52, 22), lambda j: 48, DARK, grow=3)
        U.put(im, l1, (120, 60, 53, 22), ITEM, 14, PINK, HALO, align="l", dx=1)
        U.put(im, l2, (120, 84, 52, 22), ITEM, 14, BLUE, HALO, align="l", dx=1)
    elif n in (223, 224, 225, 226):
        box = (22, 6, 44, 22) if n < 225 else (16, 5, 56, 22)
        U.erase(im, box)
        U.put(im, parts[0], (0, 6, 88, 21), "os:700:90", 16, U.WHITE)
    elif n == 227:  # only the katakana ruby goes; the Latin name stays
        U.clear(im, (170, 0, 90, 14))
        U.clear(im, (132, 36, 180, 66))
        effect(im, parts[0], (132, 36, 180, 66))
    elif 228 <= n <= 232:  # name | ruby (may be empty) | effect
        name, ruby, eff = parts
        U.clear(im, (100, 0, 212, 100))
        U.put(im, name, (132, 12, 180, 24), TITLE, 17, CARDPINK, CARDHALO, align="l")
        if ruby:
            f = typeset.font(TITLE, 17)
            cx = 136 + f.getlength(name) / 2
            U.put(im, ruby, (int(cx - 40), 0, 80, 14), ITEM, 10, CARDPINK, [(1, (236, 247, 255, 255))])
        effect(im, eff, (132, 36, 180, 60))
    return im
