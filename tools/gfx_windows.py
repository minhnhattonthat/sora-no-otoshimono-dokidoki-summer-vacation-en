"""Group windows (COMMON_10_WINDOWS): Auto (209, pink) / Skip (210, blue) buttons: the play arrows stay, the katakana is
painted over with the flat button colour and replaced by white text with a 1 px darker shadow."""
import gfx
from gfx_title import label, WHITE

BG = {209: (255, 113, 191, 255), 210: (89, 131, 255, 255)}
RECT = {209: (28, 1, 42, 18), 210: (24, 1, 50, 18)}  # text starts at x 29 / 25
SHADOW = {209: (196, 66, 140, 255), 210: (56, 88, 200, 255)}


def draw(row, im):
    n = int(row["n"])
    r = RECT[n]
    base = im.copy()
    base.paste(BG[n], (r[0], r[1], r[0] + r[2], r[1] + r[3]))
    return label(base, r, row["en"], 15, 15, weight=700, width=100, x=r[0] + 1, fill=WHITE, stroke=0, shadow=(1, 1, SHADOW[n]))
