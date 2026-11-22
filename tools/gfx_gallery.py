"""gfx group gallery (COMMU_10_CARDGALLERY): the five tab/footer panels (678 Profile, 680 Dress-Up, 681 Special, 682 Event,
684 Communication) and the OK / Back footer 711. `en` of a panel row = "<tab> | <footer>"; the game draws the percentage
after the footer text (about x 240), so footers stay left of x 232."""
from PIL import Image

import gfx_hexcard as hc
import gfx_hexstart as hs
from gfx_hexstart import WHITE, text

# n -> (tab centre x, tab text colour)
TABS = {678: (401, (147, 38, 69)), 680: (320, (136, 88, 30)), 681: (240, (108, 40, 152)), 682: (159, (38, 80, 166)),
        684: (80, (33, 86, 39))}
FOOT = (8, 249, 225, 22)
TAB_Y = (8, 22)  # y, h of the tab text rect


def tab_rect(n):
    return (TABS[n][0] - 36, TAB_Y[0], 72, TAB_Y[1])


def panel(row, im):
    n = int(row["n"])
    tab, foot = row["en"].split(" | ")
    cx, colour = TABS[n]
    out = hs.erase_dark(im, tab_rect(n), 170, grow=2)
    text(out, tab, "os:700:75", 11, [(0, colour)], cx, 23, "c")
    out = hs.fill_rect(out, FOOT)
    text(out, foot, "os:800:75", 15, [(0, WHITE)], 13, 264, "l", shear=0.15)
    return out


def draw(row, im):
    n = int(row["n"])
    if n == 711:
        return hc.footer_hint(im, [((25, 2, 26, 19), 26, "OK"), ((81, 2, 30, 19), 82, "Back")], 16)
    return panel(row, im)
