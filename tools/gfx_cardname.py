"""Card-name images (COMMU_00_CARDNAME_GALLERY 505-606, CARDNAME_GET 607-674): English redraws.

gfx/cardname.tsv   152x32 blue text, white outline, centred on x=79; one line (18 px, else 15 px, else two 14 px lines);
                   en "MAIN|RUBY" = the original's small furigana line above a big main line (590, 591).
gfx/cardnameget.tsv 327x24 plain blue text in "quotes" (the originals' 「」), centred; "MAIN (RUBY)" is one line.
Shared by gfx_cardnameget.py. Baselines/sizes are fixed per class, so every label sits on the same line.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfx  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

BLUE = (0, 111, 196, 255)
WHITE = (255, 255, 255, 255)
FONT = "os:800:75"       # ExtraBold Condensed
MAXW = 146               # ink width (with outline) that fits the 152 px image around cx=79
CX = 79


def _mask(size, text, font, cx, base, sw):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).text((cx, base), text, font=font, fill=255, anchor="ms", stroke_width=sw)
    return m


def outlined(im, text, size, cx, base, sw, fill=BLUE, outline=WHITE, fontname=FONT):
    """Draw fill text with an sw px outline onto im (RGBA, in place), baseline at y=base, centred on cx."""
    f = gfx.typeset.font(fontname, size)
    for col, w in ((outline, sw), (fill, 0)):
        if not w and col is not fill:
            continue
        m = _mask(im.size, text, f, cx, base, w)
        im.alpha_composite(Image.composite(Image.new("RGBA", im.size, col), Image.new("RGBA", im.size, (0, 0, 0, 0)), m))
    return im


def width(text, size, sw, fontname=FONT):
    return gfx.typeset.font(fontname, size).getlength(text) + 2 * sw


def split(text, size, sw):
    """Two lines, the first as long as possible but not longer than the second by more than one word's worth."""
    ws = text.split(" ")
    best = min(range(1, len(ws)), key=lambda i: max(width(" ".join(ws[:i]), size, sw), width(" ".join(ws[i:]), size, sw)))
    return " ".join(ws[:best]), " ".join(ws[best:])


def draw(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    en = row["en"]
    if "|" in en:                                       # main line + small ruby line above
        main, ruby = en.split("|")
        outlined(out, ruby, 11, CX, 11, 1)
        outlined(out, main, 16, CX, 26, 2)
        assert width(main, 16, 2) <= MAXW and width(ruby, 11, 1) <= MAXW, (row["n"], en)
    elif width(en, 18, 2) <= MAXW:
        outlined(out, en, 18, CX, 25, 2)
    elif width(en, 15, 2) <= MAXW:                      # long: one step smaller, then two lines
        outlined(out, en, 15, CX, 24, 2)
    else:
        a, b = split(en, 14, 1)
        assert max(width(a, 14, 1), width(b, 14, 1)) <= MAXW, (row["n"], en)
        outlined(out, a, 14, CX, 13, 1)
        outlined(out, b, 14, CX, 27, 1)
    return out
