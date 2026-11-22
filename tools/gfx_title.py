"""Group title (COMMON_10_TITLE): main menu 193-198 (plain = text over an underline bar, selected = text on a bar with a
wing) and New Game / Continue 199-202. White Open Sans ExtraBold, blue outline. label() and clean() are shared by
param, cardget and windows."""
import gfx
from gfx import typeset
from PIL import Image, ImageDraw

BLUE = (101, 141, 255, 255)
WHITE = (255, 255, 255, 255)


def clean(im, rect, xsrc):
    """Remove the lettering inside rect by copying the text-free column xsrc across it (the art there is horizontal bars)."""
    x, y, w, h = rect
    out = im.copy()
    col = im.crop((xsrc, y, xsrc + 1, y + h)).resize((w, h), Image.NEAREST)
    out.paste(col, (x, y))
    return out


def _layer(size, lines, f, x, baseline, pitch, fill, stroke, stroke_fill):
    """One text pass on a transparent layer whose RGB is already stroke_fill, so antialiased edges keep the right colour."""
    layer = Image.new("RGBA", size, tuple(stroke_fill[:3]) + (0,))
    d = ImageDraw.Draw(layer)
    for i, (t, tx) in enumerate(zip(lines, x)):
        d.text((tx, baseline + i * pitch), t, font=f, fill=fill, anchor="ls", stroke_width=stroke,
               stroke_fill=stroke_fill)
    return layer


def label(im, rect, text, size, baseline, weight=800, width=90, x=None, fill=WHITE, stroke=2, outline=BLUE,
          align="l", shadow=None, halo=None, pitch=0):
    """Draw text (\\n = new line, pitch px apart) onto im, clipped to rect (x,y,w,h). x = left edge of the glyphs (align l)
    or centre (align c); baseline = y of the first baseline. shadow = (dx, dy, colour); halo = (extra width, colour)
    drawn behind the outline."""
    x0, y0, w, h = rect
    f = typeset.font(f"os:{weight}:{width}", size)
    lines = text.split("\n")
    xs = [x - (f.getlength(t) / 2 if align == "c" else 0) for t in lines]
    passes = []
    if halo:
        passes.append(_layer(im.size, lines, f, xs, baseline, pitch, halo[1], stroke + halo[0], halo[1]))
    if shadow:
        sx = [v + shadow[0] for v in xs]
        passes.append(_layer(im.size, lines, f, sx, baseline + shadow[1], pitch, shadow[2], stroke, shadow[2]))
    passes.append(_layer(im.size, lines, f, xs, baseline, pitch, fill, stroke, outline if stroke else fill))
    mask = Image.new("L", im.size, 0)
    mask.paste(255, (x0, y0, x0 + w, y0 + h))
    out = im.copy()
    for p in passes:
        a = p.getchannel("A")
        p.putalpha(Image.composite(a, Image.new("L", im.size, 0), mask))
        out.alpha_composite(p)
    return out


def draw(row, im):
    n = int(row["n"])
    text = row["en"]
    if n <= 198:
        r = (40, 0, im.width - 40, im.height) if n <= 195 else (41, 0, im.width - 41, im.height)
        return label(clean(im, r, im.width - 2), r, text, 16, 36, x=47)
    r = (18, 0, im.width - 18, im.height)
    return label(clean(im, r, im.width - 2), r, text, 18, 18, x=65, align="c")
