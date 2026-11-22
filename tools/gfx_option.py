"""Graphics group option (COMMON_10_OPTION): title on the wing pattern, panel labels, menu labels, selected choices."""
import gfx_usecard as U

BLUE = (76, 105, 227, 255)
MENU_OUT = [(2, (24, 104, 204, 255))]
GREY = (112, 112, 112, 255)
LABEL = "os:600:85"


def draw(r, im):
    im = im.copy()
    n = int(r["n"])
    en = r["en"]
    if n == 114:  # title: the wing pattern repeats every 65 rows, so copy the clean tile over the Japanese
        U.tile(im, (6, 4, 164, 34), 0, 65)
        U.put(im, en, (6, 4, 164, 34), "os:800:90", 23, BLUE, [(2, U.WHITE)], align="l", dx=1, shear=0.2)
    elif n == 115:  # en = Read Only|All|Reset Settings|Back
        ro, al, rs, bk = en.split("|")
        for b in ((164, 50, 120, 22), (168, 159, 76, 20), (271, 159, 29, 20)):
            U.erase(im, b)
        U.put(im, ro, (170, 50, 60, 22), LABEL, 13, U.WHITE)
        U.put(im, al, (240, 50, 38, 22), LABEL, 13, U.WHITE)
        U.put(im, rs, (168, 159, 76, 20), LABEL, 13, GREY)
        U.put(im, bk, (271, 159, 29, 20), LABEL, 13, GREY, align="l", dx=-1)
    elif n == 117:  # five left-aligned menu labels
        im = U.blank(im)
        for i, s in enumerate(en.split("|")):
            U.put(im, s, (0, 27 * i, 104, 18), "os:600:90", 14, U.WHITE, MENU_OUT, align="l", dx=-1)
    elif n in (123, 124):  # selected choice: blue letters, yellow outline
        im = U.blank(im)
        U.put(im, en, (0, 0, im.width, im.height), "os:700:85", 13, (25, 124, 199, 255), [(2, (255, 255, 0, 204))])
    return im
