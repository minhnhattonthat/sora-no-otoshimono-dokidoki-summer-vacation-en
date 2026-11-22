"""gfx group hexcite (COMMON_20_HEX_*): the Menu / Pause buttons, Start! / Finish!, the RESULTANIME result words and the
IMG_GO "Finish?" frames.  The big words are text on transparency drawn by word(): ExtraBold Open Sans (condensed),
ring outlines, a vertical colour gradient sampled from the original, an inner bevel and a soft drop shadow, rendered once
at high resolution and then scaled to each animation frame: every frame of one word uses the same wording, shape and
the original frame's size and centre (all result words share one zoom schedule, frame height 41/71/93/107/93/82 px).
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import gfx
import gfx_usecard as uc

typeset = gfx.typeset
FONT = "os:800:75"
F = 160  # hi-res font size
WHITE = (255, 255, 255, 255)

# result words: survey n -> (style, English); frames of a style share one gradient
BLUE = [(65, 229, 255), (66, 223, 255), (60, 212, 255), (63, 207, 255), (61, 196, 255), (61, 187, 255), (70, 178, 252), (72, 156, 248),
        (85, 137, 245), (100, 130, 244)]
GREEN = [(212, 246, 106), (199, 242, 105), (160, 232, 98), (151, 231, 97), (130, 221, 95), (126, 221, 95), (113, 212, 93),
         (98, 198, 93), (98, 187, 96), (89, 175, 95)]
GOLD = [(253, 223, 103), (254, 226, 86), (254, 219, 104), (254, 208, 82), (254, 197, 88), (253, 187, 88), (252, 174, 87),
        (248, 150, 86), (246, 143, 97), (247, 161, 118)]
STYLES = {
    "lose": ([(5, WHITE)], BLUE),
    "draw": ([(5, (2, 151, 68, 255))], GREEN),
    "win": ([(5, (230, 0, 17, 255))], GOLD),
}
SHADOW = (5, 9, 3, 110)  # dx, dy, blur, alpha (final px)
REF_H = 107  # the largest result-frame height


def lerp_rows(stops, n):
    """n RGB rows interpolated through stops (top to bottom)."""
    xs = np.linspace(0, len(stops) - 1, n)
    st = np.array(stops, float)
    return np.stack([np.interp(xs, range(len(stops)), st[:, c]) for c in range(3)], axis=1)


def ring_mask(size, text, f, org, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).text(org, text, font=f, fill=255, anchor="ls", stroke_width=radius, stroke_fill=255)
    return m


def word(text, layers, stops, box_w, box_h, shadow=None, bevel=(3, 0.5), shear=0.1, stretch=1.35):
    """-> dict(hi, rx, ry, ob): hi-res RGBA, hi->final scale (rx, ry) for an outline box of box_w x box_h, outline bbox in hi."""
    f = typeset.font(FONT, F)
    l, t, r, b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=f, anchor="ls")
    gw, gh = r - l, b - t
    gw_eff = gw + shear * gh
    total = sum(w for w, _ in layers)
    rx_max, ry_max = (box_w - 2 * total) / gw_eff, (box_h - 2 * total) / gh
    rx = min(rx_max, ry_max)
    ry = min(ry_max, rx * stretch)
    avg = (rx + ry) / 2
    radii, acc = [], 0.0
    for w, _ in reversed(layers):  # innermost ring first: cumulative thickness from the glyph
        acc += w
        radii.append(acc)
    radii = [round(v / avg) for v in reversed(radii)]  # outermost first, in hi px
    pad = radii[0] + round((shadow[0] + shadow[1] + 3 * shadow[2]) / avg if shadow else 0) + 6 + int(shear * gh)
    size = (math.ceil(gw_eff) + 2 * pad, gh + 2 * pad)
    org = (pad - l, pad - t)
    base_y = org[1]

    def sheared(m):
        return m.transform(m.size, Image.AFFINE, (1, shear, -shear * base_y, 0, 1, 0), Image.BICUBIC)

    rings = [sheared(ring_mask(size, text, f, org, rad)) for rad in radii]
    glyph = sheared(ring_mask(size, text, f, org, 0))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    if shadow:
        sh = rings[0].filter(ImageFilter.GaussianBlur(shadow[2] / avg))
        sh = ImageChops.offset(sh, round(shadow[0] / avg), round(shadow[1] / avg)).point(lambda v: v * shadow[3] // 255)
        out.alpha_composite(Image.merge("RGBA", (Image.new("L", size, 0),) * 3 + (sh,)))
    for m, (_, col) in zip(rings, layers):
        col = tuple(col) + (255,) if len(col) == 3 else tuple(col)
        out.alpha_composite(Image.merge("RGBA", tuple(Image.new("L", size, c) for c in col[:3]) + (m.point(lambda v: v * col[3] // 255),)))
    # gradient over the glyph's rows
    top, bot = base_y - (-t), base_y + b
    rows = lerp_rows(stops, max(2, bot - top))
    grad = np.zeros((size[1], size[0], 3), np.uint8)
    for y in range(size[1]):
        grad[y] = rows[min(len(rows) - 1, max(0, y - top))]
    fill = Image.fromarray(grad).convert("RGBA")
    if bevel:
        inner = glyph.filter(ImageFilter.MinFilter(2 * round(bevel[0] / avg) + 1))
        light = Image.blend(fill, Image.new("RGBA", size, WHITE), bevel[1])
        fill = Image.composite(fill, light, inner)
    fill.putalpha(glyph)
    out.alpha_composite(fill)
    ob = rings[0].point(lambda v: 255 if v > 128 else 0).getbbox()
    return dict(hi=out, rx=rx, ry=ry, ob=ob)


def place(w, canvas_size, m, cx, cy):
    """Scale the word by m (relative to its largest frame) and put the outline bbox's centre at (cx, cy)."""
    hi, ob = w["hi"], w["ob"]
    kx, ky = w["rx"] * m, w["ry"] * m
    img = hi.resize((max(1, round(hi.width * kx)), max(1, round(hi.height * ky))), Image.LANCZOS)
    ox = round(cx - (ob[0] + ob[2]) / 2 * kx)
    oy = round(cy - (ob[1] + ob[3]) / 2 * ky)
    out = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    out.alpha_composite(img, (max(ox, 0), max(oy, 0)), (max(-ox, 0), max(-oy, 0)))
    return out


def opaque_box(im):
    a = np.array(im)[..., 3] >= 250
    ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max(), ys.max()


_cache = {}


def result(row, im):
    n = int(row["n"])
    sty = STYLES[WORD_STYLE[(n - 1055) // 6 if n < 1131 else 2 + (n - 1131) // 6]]
    wkey = row["en"]
    if wkey not in _cache:
        _cache[wkey] = word(row["en"], sty[0], sty[1], 425, REF_H, shadow=SHADOW)
    x0, y0, x1, y1 = opaque_box(im)
    return place(_cache[wkey], im.size, (y1 - y0 + 1) / REF_H, (x0 + x1) / 2, (y0 + y1) / 2)


WORD_STYLE = ["lose", "lose", "draw", "win", "win", "win"]  # 1055 ボロ負け, 1061 負け, 1131 引き分け, 1137 大勝利, 1143 勝ち, 1149 チョイ勝ち


def banner(row, im):
    """1011 Start! / 1012 Finish!: pink + white double outline, orange / blue gradient."""
    n = int(row["n"])
    stops = [(255, 200, 20), (255, 190, 10), (255, 172, 19), (255, 146, 14), (255, 133, 14)] if n == 1011 else \
            [(30, 205, 255), (10, 196, 255), (19, 182, 255), (10, 156, 255), (19, 147, 254)]
    w = word(row["en"], [(6, (255, 95, 200, 191)), (4, WHITE)], stops, 210, 86, bevel=None)
    return place(w, im.size, 1.0, 112, 47)


def go(row, im):
    """IMG_GO frames: white text, the original frame's bounding box (same width, growing height, bottom fixed)."""
    a = np.array(im)[..., 3] > 40
    ys, xs = np.nonzero(a)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    f = typeset.font(FONT, 200)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), row["en"], font=f, anchor="ls")
    m = Image.new("L", (r - l + 8, b - t + 8), 0)
    ImageDraw.Draw(m).text((4 - l, 4 - t), row["en"], font=f, fill=255, anchor="ls")
    m = m.crop(m.getbbox()).resize((x1 - x0 + 1, y1 - y0 + 1), Image.LANCZOS)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", m.size, WHITE), (x0, y0), m)
    return out


def button(row, im):
    """1000 / 1001: remove the Japanese label from the panel (inpaint), set the English left-aligned after the icon."""
    n = int(row["n"])
    rect = (30, 6, 71, 18) if n == 1000 else (36, 4, 34, 18)
    x, y, w, h = rect
    base = uc.erase(im.copy(), rect)  # the panel is flat left to right, so per-row interpolation restores it
    if n == 1000:  # ... except beside the icon, whose dark edge would streak: repaint the flat grey
        base.paste((150, 157, 168, 230), (x, y, x + w, y + h))
    x0 = 33 if n == 1000 else 36
    return typeset.text_image(im.width, im.height, row["en"], "os:700:75", size=13, fill=WHITE, canvas=base,
                              box=(x0, y, w, h), align="l", valign="m")


def draw(row, im):
    n = int(row["n"])
    if n in (1000, 1001):
        return button(row, im)
    if n in (1011, 1012):
        return banner(row, im)
    if n >= 1674:
        return go(row, im)
    return result(row, im)
