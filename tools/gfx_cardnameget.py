"""Card-name titles in quotes (COMMU_00_CARDNAME_GET 607-674): plain blue Open Sans Bold (width 80), one line, centred.
Look shared with gfx_cardname (see there)."""
import gfx_cardname as c
from PIL import Image

FILL = (33, 73, 223, 255)   # the originals' colour
FONT = "os:700:80"
SIZE = 17
CX, BASE, MAXW = 163, 18, 321


def draw(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    assert c.width(row["en"], SIZE, 0, FONT) <= MAXW, (row["n"], row["en"])
    return c.outlined(out, row["en"], SIZE, CX, BASE, 0, fill=FILL, fontname=FONT)
