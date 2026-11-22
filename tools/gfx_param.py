"""Group param (COMMON_10_PARAMETER_0/1): Down / Up beside their arrows (179, 180: coloured text, white outline) and the
four emotion words (181-184: Happy / Sad / Anger / Shy, as the Latin 161 sheet has them)."""
import gfx
from gfx import typeset
from gfx_title import label, WHITE
from PIL import Image

# text colour of each image, sampled from the original (most common non-white opaque colour)
COLOUR = {179: (1, 0, 253), 180: (255, 0, 1), 181: (255, 155, 5), 182: (69, 152, 212), 183: (194, 31, 38), 184: (173, 22, 211)}


def draw(row, im):
    n = int(row["n"])
    fill = COLOUR[n] + (255,)
    if n <= 180:  # arrows stay; the word sits between them (x 109-163)
        r = (104, 0, 64, 32)
        base = im.copy()
        base.paste((0, 0, 0, 0), (r[0], r[1], r[0] + r[2], r[1] + r[3]))
        return label(base, r, row["en"], 19, 24, width=90, x=136, align="c", fill=fill, outline=WHITE)
    blank = Image.new("RGBA", im.size, (0, 0, 0, 0))
    return label(blank, (0, 0, 72, 32), row["en"], 22, 23, width=80, x=36, align="c", fill=fill, stroke=3, outline=WHITE)
