"""Group cardget (COMMON_10_CARDGET): teal "... Card Get!!" banners (40 41 44 46 53), blue counter suffix (42), the wing
note (45) and the pink "... Bonus!" banners (48-52)."""
import gfx
from gfx import typeset
from gfx_title import label, WHITE
from PIL import Image

TEAL = (46, 189, 170, 255)
PINK = (255, 70, 178, 255)
NOTE = (82, 116, 243, 255)
WING = (184, 227, 255, 217)


def draw(row, im):
    n = int(row["n"])
    text = row["en"].replace("\\n", "\n")
    blank = Image.new("RGBA", im.size, (0, 0, 0, 0))
    if n == 42:  # text only, sits right of the digit sprites at x 83
        return label(blank, (0, 0, im.width, im.height), text, 20, 24, weight=600, width=90, x=83, fill=(34, 68, 221, 255), stroke=0)
    if n == 45:  # on the wing: drop the opaque lettering pixels back to the wing colour, then redraw
        r = (36, 19, 88, 34)
        base = im.copy()
        for y in range(r[1], r[1] + r[3]):
            for x in range(r[0], r[0] + r[2]):
                p = base.getpixel((x, y))
                # lettering = opaque, or any colour off the wing's; the wing's own antialiased edge keeps its colour
                if p[3] == 255 or (p[3] and max(abs(p[i] - WING[i]) for i in range(3)) > 4):
                    base.putpixel((x, y), WING)
        return label(base, r, text, 14, 33, width=90, x=78, align="c", fill=NOTE, outline=WHITE, pitch=14)
    if n >= 48:  # pink bonus banners: white letters, pink outline
        return label(blank, (0, 0, im.width, im.height), text, 16, 17, width=75, x=im.width / 2, align="c", fill=WHITE, stroke=3, outline=PINK)
    return label(blank, (0, 0, im.width, im.height), text, 22, 24, width=90, x=im.width / 2, align="c", fill=TEAL, stroke=3,
                 outline=WHITE, halo=(1, (255, 255, 255, 80)))
