"""Graphics group hexoption (COMMON_20_HEX_OPTION): Back button, Game Settings title, value labels in white / orange /
blue states (dominant colour of the original), the two orange row tags."""
import gfx_usecard as U
from gfx import typeset

ORANGE = (255, 120, 0, 255)


def draw(r, im):
    n = int(r["n"])
    en = r["en"].split("|")
    if n == 234:  # grey Back on the orange tab; the x icon stays
        im = im.copy()
        U.erase(im, (36, 9, 34, 18))
        U.put(im, en[0], (36, 9, 34, 18), "os:600:85", 14, (99, 98, 98, 255), align="l", dx=0)
    elif n == 235:  # white italic title with an orange outline; the orange rule under it stays
        im = im.copy()
        U.clear(im, (0, 0, 208, 33))
        for j in (33, 34):  # white lower tips of the Japanese glyphs sit on the rule: paint them rule-orange
            for i in range(208):
                if im.getpixel((i, j))[1] > 140:
                    im.putpixel((i, j), ORANGE)
        U.put(im, en[0], (2, 2, 200, 31), "os:800:80", 22, U.WHITE,
              [(4, (255, 120, 0, 110)), (3, ORANGE)], align="l", dx=2, dy=-1, shear=0.2)
    elif 240 <= n <= 254:  # value labels: same text, colour from the original
        col = typeset.dominant(im) + (255,)
        im = U.blank(im)
        U.put(im, en[0], (0, 0, im.width, im.height), "os:700:85", 14, col)
    elif n == 255:  # two orange tags: white letters, orange outline
        im = U.blank(im)
        for s, (y, h) in zip(en, ((3, 20), (48, 20))):
            U.put(im, s, (0, y, im.width, h), "os:600:75", 13, U.WHITE, [(2, ORANGE)])
    return im
