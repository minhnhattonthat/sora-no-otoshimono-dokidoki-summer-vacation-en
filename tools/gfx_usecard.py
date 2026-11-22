"""Graphics group usecard (Combo Card hand screens) + helpers the other menu groups import (option, hexmenu, hexoption,
levelup): erase() / put() on an RGBA original, then draw.  Text colours/outlines are sampled from the originals."""
import gfx
from gfx import typeset
from PIL import Image

YELLOW = (255, 241, 0, 255)
DARK_OUT = [(3, (60, 60, 60, 150)), (2, (67, 67, 67, 255))]  # yellow caption outline of the dark panels
WHITE = (255, 255, 255, 255)
SEMI = "os:700:90"  # white UI labels: Open Sans Bold, slightly condensed


def erase(im, rect):
    """Remove what is inside rect by interpolating the pixels just left/right of it per row (flat or vertical-gradient bg)."""
    x, y, w, h = rect
    px = im.load()
    for j in range(y, y + h):
        a, b = px[x - 1, j], px[x + w, j]
        for i in range(w):
            t = (i + 1) / (w + 1)
            px[x + i, j] = tuple(round(a[k] * (1 - t) + b[k] * t) for k in range(4))
    return im


def tile(im, rect, dx, dy):
    """Replace rect by the pixels (dx, dy) away: for a periodic background pattern."""
    x, y, w, h = rect
    im.paste(im.crop((x + dx, y + dy, x + dx + w, y + dy + h)), (x, y))
    return im


def clear(im, rect):
    """Make rect fully transparent (images that are text on transparency)."""
    x, y, w, h = rect
    im.paste((0, 0, 0, 0), (x, y, x + w, y + h))
    return im


def refill(im, rect, dy_of, text, line_rows=(), fade_from=None, grow=2):
    """Remove lettering over a dotted-pattern panel (the dots repeat every 4 rows) without touching the rest of rect:
    text(pixel) -> bool picks the glyph pixels, grown by `grow` px; a masked pixel is copied from the row dy_of(row)
    away (a multiple of 4, clear of text).  In line_rows (a horizontal rule under the title) a masked pixel is
    instead rebuilt from the pixel left of rect, flat until fade_from, then ramping to the pixel right of rect."""
    x, y, w, h = rect
    src = im.copy()
    px = src.load()
    ink = {(i, j) for j in range(y, y + h) for i in range(x, x + w) if text(px[i, j])}
    mask = {(i + a, j + b) for i, j in ink for a in range(-grow, grow + 1) for b in range(-grow, grow + 1)}
    f0 = x if fade_from is None else fade_from
    for i, j in mask:
        if not (x <= i < x + w and y <= j < y + h):
            continue
        if j in line_rows:
            a, b = px[x - 1, j], px[x + w, j]
            t = min(1.0, max(0.0, (i - f0) / max(1, x + w - f0)))
            im.putpixel((i, j), tuple(round(a[k] * (1 - t) + b[k] * t) for k in range(4)))
        else:
            im.putpixel((i, j), px[i, j + dy_of(j)])
    return im


def _pass(im, s, box, font, size, fill, stroke, **kw):
    # text_image's layer grows by the stroke width, which shifts left/top/right/bottom-aligned ink: undo it per pass
    sw = stroke[0] if stroke else 0
    a, v = kw.get("align", "c"), kw.get("valign", "m")
    box = (box[0] + {"l": -sw, "r": sw}.get(a, 0), box[1] + {"t": -sw, "b": sw}.get(v, 0), box[2], box[3])
    typeset.text_image(im.width, im.height, s, font, size=size, fill=fill, stroke=stroke, canvas=im, box=box, **kw)


def put(im, s, box, font=SEMI, size=14, fill=WHITE, strokes=(), shadow=None, dx=0, dy=0, shear=0.0, **kw):
    """Composite s centred (kw: align, valign, spacing, xscale, tracking) in box = (x, y, w, h) of im: optional shadow
    (dx, dy, colour), outline passes strokes = [(width, colour), ..] widest first, then the fill; shear = italic slant."""
    if shear:  # draw on a clear layer, slant it about the box's middle row, then composite
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        put(layer, s, box, font, size, fill, strokes, shadow, dx, dy, 0.0, **kw)
        cy = box[1] + box[3] / 2
        layer = layer.transform(im.size, Image.AFFINE, (1, shear, -shear * cy, 0, 1, 0), Image.BICUBIC)
        im.alpha_composite(layer)
        return im
    x, y, w, h = box
    box = (x + dx, y + dy, w, h)
    if shadow:
        _pass(im, s, (box[0] + shadow[0], box[1] + shadow[1], w, h), font, size, shadow[2], None, **kw)
    for sw, col in strokes:
        _pass(im, s, box, font, size, col, (sw, col), **kw)
    _pass(im, s, box, font, size, fill, None, **kw)
    return im


def caption(im, s, box, size=15, **kw):
    return put(im, s, box, "os:800:90", size, YELLOW, DARK_OUT, **kw)


def blank(im):
    return Image.new("RGBA", im.size, (0, 0, 0, 0))


# ---- usecard ----

def draw(r, im):
    im = im.copy()
    n = int(r["n"])
    en = r["en"].replace("\\n", "\n")
    if n == 66:  # tab label left of the >>> arrows
        erase(im, (6, 10, 81, 16))
        put(im, en, (6, 10, 81, 16), "os:700:85", 14, WHITE, align="l", dx=2)
    elif n == 70:
        erase(im, (14, 12, 264, 48))
        caption(im, en, (14, 12, 264, 48), 15, align="l", spacing=3, dx=5)
    elif n in (71, 72):
        erase(im, (13, 9, 62, 21))
        put(im, en, (13, 9, 62, 21), SEMI, 15, WHITE)
    elif n == 83:  # en = title | body | footer
        title, body, foot = en.split("|")
        for b in ((14, 8, 122, 30), (28, 44, 212, 48), (200, 102, 52, 18)):
            erase(im, b)
        caption(im, title, (14, 8, 122, 28), 16, align="l", dx=4)
        put(im, body, (28, 44, 212, 48), "os:600:90", 15, WHITE, shadow=(1, 1, (0, 0, 0, 170)), align="l", dx=5, spacing=1)
        put(im, foot, (200, 102, 52, 18), "os:700:90", 12, WHITE, shadow=(1, 1, (0, 0, 0, 170)), align="l", dx=3)
    elif n == 88:
        im = blank(im)
        put(im, en, (0, 0, 48, 24), "os:800:90", 15, (255, 90, 222, 255),
            [(4, (255, 255, 255, 40)), (3, (255, 255, 255, 90)), (2, WHITE)])
    return im
