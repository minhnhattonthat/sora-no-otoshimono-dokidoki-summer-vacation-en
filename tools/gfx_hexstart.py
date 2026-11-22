"""gfx group hexstart (COMMON_20_HEX_START): titles, outfit labels, record line, special-move names + effects, logos, footer.

Also the shared lettering helpers for the groups hexcard, commenu, help and gallery (they import this module):
text()        draw one outlined/sheared line of Open Sans at a baseline, aligned by its ink;
flat()        a block of wrapped, flat-colour lines (effect texts);
fill_rect()   repaint a rect with a flat or per-row colour.
Special-move wording: gfx/hexstart.tsv (names and long effects); gfx/hexcard.tsv uses shorter effect lines.
"""
import math
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

import gfx

typeset = gfx.typeset
WHITE = (255, 255, 255, 255)


def _col(c):
    return tuple(c) + (255,) if len(c) == 3 else tuple(c)


def layer(s, fname, size, layers, xscale=1.0, shear=0.0, gap=0):
    """-> (RGBA image, baseline y in it). layers = [(stroke width, colour)] outermost first; width 0 = the glyphs.
    gap = extra px per word space (outlines eat the space between words at small sizes)."""
    f = typeset.font(fname, size)
    asc, desc = f.getmetrics()
    pad = max([ly[0] for ly in layers] + [0]) + 3 + int(abs(shear) * (asc + desc))
    words, xs, x = s.split(" "), [], 0.0
    for wd in words:
        xs.append(x)
        x += f.getlength(wd) + f.getlength(" ") + gap
    if not gap:
        words, xs, x = [s], [0.0], f.getlength(s) + f.getlength(" ")
    w, h = math.ceil(x) + 2 * pad, asc + desc + 2 * pad
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for sw, colour, *hard in layers:
        m = Image.new("L", (w, h), 0)
        for wd, wx in zip(words, xs):
            ImageDraw.Draw(m).text((pad + wx, pad + asc), wd, font=f, fill=255, anchor="ls", stroke_width=sw, stroke_fill=255)
        if hard:  # a ("hard") layer is solid: its antialiased edge pixels are pushed to opaque (pixel-art outlines)
            m = m.point(lambda v: min(255, v * 4))
        out.alpha_composite(Image.composite(Image.new("RGBA", (w, h), _col(colour)), Image.new("RGBA", (w, h), (0, 0, 0, 0)), m))
    base = pad + asc
    if shear:  # top leans right: out x = in x + shear * (base - y)
        out = out.transform(out.size, Image.AFFINE, (1, shear, -shear * base, 0, 1, 0), Image.BICUBIC)
    if xscale != 1.0:
        out = out.resize((max(1, round(w * xscale)), h), Image.LANCZOS)
    return out, base


def text(cv, s, fname, size, layers, x, base, align="l", xscale=1.0, shear=0.0, gap=0):
    """Composite s on cv so its ink starts (l) / is centred on (c) / ends (r) at x, baseline at y=base. -> ink width."""
    lay, b = layer(s, fname, size, layers, xscale, shear, gap)
    bb = lay.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    left, right = bb[0], bb[2]
    ox = {"l": x - left, "c": round(x - (left + right) / 2), "r": x - right}[align]
    cv.alpha_composite(lay, (ox, base - b)) if ox >= 0 and base - b >= 0 else _paste_clipped(cv, lay, ox, base - b)
    return right - left


def _paste_clipped(cv, lay, ox, oy):
    x0, y0 = max(-ox, 0), max(-oy, 0)
    lay = lay.crop((x0, y0, min(lay.width, cv.width - ox), min(lay.height, cv.height - oy)))
    cv.alpha_composite(lay, (ox + x0, oy + y0))


def width(s, fname, size, layers=((0, WHITE),), xscale=1.0, gap=0):
    lay, _ = layer(s, fname, size, layers, xscale, 0.0, gap)
    bb = lay.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    return bb[2] - bb[0]


def flat(cv, s, fname, size, colour, x, base, pitch, maxw, align="l", maxlines=None, xscale=1.0, cy=None):
    """Wrap s (explicit \\n kept) to maxw and draw lines at pitch from the first baseline (cy: centre the block on y
    instead, base ignored). -> number of lines."""
    lines = typeset.wrap(s, fname, size, maxw, xscale).split("\n")
    lo, hi = 1, maxw  # balance: narrowest width that still gives the same number of lines (no one-word last line)
    while lo < hi:
        mid = (lo + hi) // 2
        if len(typeset.wrap(s, fname, size, mid, xscale).split("\n")) <= len(lines):
            hi = mid
        else:
            lo = mid + 1
    lines = typeset.wrap(s, fname, size, hi, xscale).split("\n")
    assert maxlines is None or len(lines) <= maxlines, (s, lines)
    if cy is not None:
        base = round(cy + 0.36 * size - (len(lines) - 1) * pitch / 2)
    for i, ln in enumerate(lines):
        w = text(cv, ln, fname, size, [(0, colour)], x, base + i * pitch, align, xscale)
        assert w <= maxw + 1, (ln, w, maxw)
    return len(lines)


def fill_rect(im, rect, colour=None):
    """Repaint rect (x, y, w, h) of im: colour, or per row the commonest opaque colour of that row when None."""
    x, y, w, h = rect
    a = np.array(im)
    for yy in range(y, y + h):
        if colour is None:
            c = Counter(map(tuple, a[yy][a[yy][:, 3] > 200][:, :]))
            c.pop((112, 112, 112, 255), None)
            colr = c.most_common(1)[0][0]
        else:
            colr = _col(colour)
        a[yy, x:x + w] = colr
    return Image.fromarray(a)


def erase_dark(im, rect, thr, grow=1, iters=80):
    """Remove dark lettering (mean RGB < thr) inside rect by diffusing the surrounding colours into it (grow: halo px)."""
    x, y, w, h = rect
    a = np.array(im).astype(float)
    reg = a[y:y + h, x:x + w]
    mask = (reg[..., :3].mean(axis=2) < thr) & (reg[..., 3] > 60)
    m = mask.copy()
    for _ in range(grow):
        g = m.copy()
        g[1:] |= m[:-1]
        g[:-1] |= m[1:]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        m = g
    known, cur = ~m, reg.copy()
    cur[m] = 0
    for _ in range(iters):
        wsum, acc = np.zeros(m.shape), np.zeros(reg.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k, v = np.roll(known, (dy, dx), (0, 1)), np.roll(cur, (dy, dx), (0, 1))
            wsum += k
            acc += v * k[..., None]
        fill = m & ~known & (wsum > 0)
        cur[fill] = acc[fill] / wsum[fill][:, None]
        known |= fill
    a[y:y + h, x:x + w] = cur
    return Image.fromarray(a.round().clip(0, 255).astype("uint8"))


def clear(im, rect):
    out = im.copy()
    out.paste((0, 0, 0, 0), (rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]))
    return out


NAVY = (29, 72, 136)
HINT = 13  # size of the grey button-hint labels (OK / Back / Settings / Tutorial)
F_TITLE = "os:800:75"
F_LABEL = "os:700:75"
F_NAME = "os:800:75"
F_BODY = "os:600:85"
F_LOGO = "os:800:88"


# ---- styles ----
def title(row, im, rect_x1, ink_x0, jx1):
    """White heavy italic letters with a 3 px outline in the title's colour, on the bar kept below them.
    jx1 = last column of the Japanese ink: left of it the bar is rebuilt from column 2, right of it the original stays."""
    out = im.copy()
    col = typeset.dominant(im)
    bar = [im.getpixel((2, y)) for y in range(33, 37)]
    out.paste((0, 0, 0, 0), (3, 3, rect_x1, 40))
    for x in range(3, rect_x1):
        for i, p in enumerate(bar if x <= jx1 else [im.getpixel((x, y)) for y in range(33, 37)]):
            out.putpixel((x, 33 + i), p)
    text(out, row["en"], F_TITLE, 25, [(3, col), (0, WHITE)], ink_x0, 29, "l", shear=0.2)
    return out


def outfit(row, im):
    """Wing label (pink / blue) or bare grey label: bold text centred at x 46 (pushed right of the wing if long), white outline."""
    n = int(row["n"])
    base = 19
    w = width(row["en"], F_LABEL, 11, gap=2)
    cx = round(min(max(46, 25 + w / 2), 70 - w / 2))
    if n in GREY:
        out = clear(im, (22, 3, 50, 20))
        text(out, row["en"], F_LABEL, 11, [(0, (112, 112, 112))], cx, base - 2, "c", gap=2)
        return out
    out = im.copy()
    barc = im.getpixel((64, 16))
    tail = [[im.getpixel((x, y)) for y in range(14, 20)] for x in range(62, 68)]
    out.paste((0, 0, 0, 0), (22, 4, 72, 23))
    for x in range(22, 65):
        for y in range(14, 20):
            out.putpixel((x, y), barc)
    for i, colm in enumerate(tail):
        for j, p in enumerate(colm):
            out.putpixel((65 + i, 14 + j), p)
    fill = Counter(p[:3] for p in im.getdata() if p[3] > 250 and p[:3] != WHITE[:3] and p[:3] != barc[:3]).most_common(1)[0][0]
    text(out, row["en"], F_LABEL, 11, [(1, WHITE, "hard"), (0, fill)], cx, base - 1, "c", gap=2)
    return out


GREY = {321, 324, 326, 328, 330}
TITLES = {299: (195, 7, 184), 349: (217, 7, 206), 356: (163, 7, 152)}  # n: (rect end x, ink start x, last Japanese ink x)


def record(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    purple = (172, 24, 157)
    f, sz = F_LABEL, 14
    text(out, "Record:", f, sz, [(0, purple)], 5, 15, "l")
    for s, x in (("W", 104), ("L", 160), ("D", 202)):
        text(out, s, f, sz, [(0, purple)], x, 15, "l")
    text(out, "Current", f, sz, [(0, purple)], 98, 38, "r")
    text(out, "Win Streak", f, sz, [(0, purple)], 131, 38, "l")
    return out


def special_label(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    text(out, row["en"], F_NAME, 15, [(0, NAVY)], 6, 17, "l", shear=0.2)
    return out


def move_name(row, im):
    n = int(row["n"])
    if n == 336:
        return clear(im, (0, 0, 160, 12))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    text(out, row["en"], F_NAME, 21, [(0, NAVY)], 5, 27, "l", shear=0.2)
    return out


def move_effect(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    flat(out, row["en"].replace("\\n", "\n"), F_BODY, 12, NAVY, 3, 16, 17, im.width - 6, maxlines=4)
    return out


def logo(row, im):
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fill = typeset.dominant(im)
    text(out, row["en"], F_LOGO, 24, [(1, WHITE), (0, fill)], im.width // 2, 20, "c")
    return out


def footer(row, im):
    out = im.copy()
    for (x0, w, nx), s in zip(((31, 64, 33), (116, 79, 119)), row["en"].split(" / ")):
        out = _bgfill(out, (x0, 4, w, 26))
        text(out, s, F_LABEL, HINT, [(0, (112, 112, 112))], nx, 22, "l")
    return out


def _bgfill(im, rect):
    x, y, w, h = rect
    a = np.array(im)
    for yy in range(y, y + h):
        row = a[yy]
        sel = (row[:, 3] > 0) & ~((abs(row[:, 0].astype(int) - row[:, 1]) < 25) & (row[:, 0] < 200))
        c = Counter(map(tuple, row[sel])).most_common(1)
        a[yy, x:x + w] = c[0][0] if c else (0, 0, 0, 0)
    return Image.fromarray(a)


def draw(row, im):
    n = int(row["n"])
    if n in TITLES:
        return title(row, im, *TITLES[n])
    if 321 <= n <= 331 or 350 <= n <= 354:
        return outfit(row, im)
    if n == 332:
        return record(row, im)
    if n == 335:
        return special_label(row, im)
    if 336 <= n <= 341:
        return move_name(row, im)
    if 342 <= n <= 347:
        return move_effect(row, im)
    if n in (357, 358):
        return logo(row, im)
    if n == 364:
        return footer(row, im)
    raise KeyError(n)
