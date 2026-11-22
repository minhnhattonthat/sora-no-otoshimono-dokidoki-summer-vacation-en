"""Graphics group levelup (COMMU_10_LEVELUPDIALOG): unlock banners (pink italic, teal for the named part, white outline)
and the big gradient Level Up!! logo.  All of them are text on transparency, so each image is drawn from scratch."""
import gfx_usecard as U
from gfx import typeset
from PIL import Image, ImageFilter

PINK = (255, 106, 183, 255)
TEAL = (45, 189, 170, 255)
FONT = "os:800:85"
SIZE = 22


def runs(im, parts, box, size=SIZE, outline=3, shear=0.2):
    """parts = [(text, fill)]: one centred line in box; every outline is drawn before any fill, then slanted."""
    f = typeset.font(FONT, size)
    total = sum(f.getlength(t) for t, _ in parts)
    x0 = box[0] + (box[2] - total) / 2
    layer = U.blank(im)
    xs, x = [], x0
    for t, _ in parts:
        xs.append(x)
        x += f.getlength(t)
    for with_outline in (True, False):
        for (t, col), px in zip(parts, xs):
            b = (round(px) - 3, box[1], int(f.getlength(t)) + 8, box[3])
            if with_outline:
                U._pass(layer, t, b, FONT, size, U.WHITE, (outline, U.WHITE), align="l")
            else:
                U._pass(layer, t, b, FONT, size, col, None, align="l")
    cy = box[1] + box[3] / 2
    layer = layer.transform(im.size, Image.AFFINE, (1, shear, -shear * cy, 0, 1, 0), Image.BICUBIC)
    im.alpha_composite(layer)
    return im


def logo(im, s):
    """Level Up!!: pink top-to-bottom gradient, white outline, soft teal glow."""
    box = (0, 0, im.width, im.height)
    kw = dict(align="c", valign="m", shear=0.2, dy=-3)
    glow = U.blank(im)
    U.put(glow, s, box, FONT, 34,(67, 203, 199, 191), [(7, (67, 203, 199, 191))], **kw)
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(1.2)))
    U.put(im, s, box, FONT, 34,U.WHITE, [(3, U.WHITE)], **kw)
    mask = U.blank(im)
    U.put(mask, s, box, FONT, 34,U.WHITE, **kw)
    ys = [y for y in range(im.height) if any(mask.getpixel((x, y))[3] > 128 for x in range(im.width))]
    y0, y1 = min(ys), max(ys)
    grad = Image.new("RGBA", im.size)
    for y in range(im.height):
        t = min(1.0, max(0.0, (y - y0) / max(1, y1 - y0)))
        c = tuple(round(a + (b - a) * t) for a, b in zip((255, 150, 198), (255, 66, 163)))
        grad.paste(c + (255,), (0, y, im.width, y + 1))
    im.paste(grad, (0, 0), mask.getchannel("A"))
    return im


def draw(r, im):
    n = int(r["n"])
    en = r["en"]
    im = U.blank(im)
    if n == 958:
        return logo(im, en)
    box = (0, 3, im.width, 26)
    if n == 951:
        runs(im, [("Hexcite ES has become ", PINK), ("Hexcite", TEAL), ("!!", PINK)], box)
    else:  # Added <Name> to Opponents!! / Free Mode!!
        name, where = en.split("|")
        runs(im, [("Added ", PINK), (name, TEAL), (" to " + where + "!!", PINK)], box)
    return im
