"""gfx group credits (COMMU_10_ENDING ED_A / ED_B / ED_C): role headings (white), staff names (blue / white), copyright.
Everything is lettering on transparency, so a redraw is a fresh canvas laid out from where the original lines sit:
the original ink is grouped into line clusters (rows of ink) and each English line is centred (headings) or left-aligned
(names) on its cluster. ED_B headings keep the white disc with the first letter in blue. 927 (Kadokawa logo) is not touched.
en = lines separated by \\n, one per cluster group (MAP: for the images where one line covers two original lines)."""
import numpy as np
from PIL import Image, ImageDraw

import gfx
import gfx_hexstart as hs

WHITE = (255, 255, 255, 255)
BLUE = (65, 182, 248, 255)
HEAD = "os:600:85"   # headings (white)
NAME = "os:600:80"   # names, labels and the copyright
SUBFONT = "os:700:75"
SUBPITCH = 12
SIZES = {"head": 20, "name": 21, "label": 16, "sub": 11}
MAP = {858: [(i, i) for i in range(1, 5)], 859: [(i, i) for i in range(1, 4)], 860: [(0, 0), (1, 1), (2, 2)], 861: [(0, 1), (2, 2), (3, 3)], 862: [(0, 1), (2, 3)]}


def clusters(im):
    a = np.array(im)[..., 3] > 40
    rows = np.nonzero(a.any(axis=1))[0]
    cl = []
    for y in rows:
        if cl and y - cl[-1][1] <= 1:
            cl[-1][1] = y
        else:
            cl.append([int(y), int(y)])
    out = []
    for y0, y1 in cl:
        xs = np.nonzero(a[y0:y1 + 1].any(axis=0))[0]
        out.append((y0, y1, int(xs.min()), int(xs.max())))
    return out


def fit(s, fname, size, maxw):
    """Largest size <= size (never below 8) at which s is at most maxw px wide."""
    while hs.width(s, fname, size) > maxw and size > 8:
        size -= 1
    return size


def put(cv, s, fname, size, colour, x, cy, maxw, align="l"):
    """Draw one line with its caps centred on y=cy; align c: x = centre, l: x = left ink edge (pulled left if too wide)."""
    size = fit(s, fname, size, maxw)
    w = hs.width(s, fname, size)
    if align == "l":
        x = min(x, cv.width - 1 - w)
    hs.text(cv, s, fname, size, [(0, colour)], x, round(cy + 0.357 * size), align)
    return size


def heading(cv, lines, cl, align_x=None):
    """Role heading images 837-847: white, centred on the original lines (941: left at x)."""
    if len(lines) != len(cl):  # e.g. 844: one Japanese line becomes two English ones, stacked on the original's centre
        y0, y1 = cl[0][0], cl[-1][1]
        x0, x1 = min(c[2] for c in cl), max(c[3] for c in cl)
        cl = [(round((y0 + y1) / 2 + (i - (len(lines) - 1) / 2) * 22),) * 2 + (x0, x1) for i in range(len(lines))]
    for i, s in enumerate(lines):
        y0, y1, x0, x1 = cl[i]
        cx = (x0 + x1) / 2
        put(cv, s, HEAD, SIZES["head"], WHITE, cx if align_x is None else align_x, (y0 + y1) / 2,
            2 * min(cx, cv.width - cx) - 4 if align_x is None else cv.width - 4, "c" if align_x is None else "l")


def names(cv, lines, n, cl):
    """Names / labels / sub lines. en lines starting with "+" continue the previous sub line (a second row, no cluster)."""
    groups = MAP.get(n, [(i, i) for i in range(len(cl))])
    assert sum(not s.startswith("+") for s in lines) == len(groups), (n, lines, groups)
    gi, items = iter(groups), []
    for s in lines:
        if s.startswith("+"):
            items.append(dict(s=s[1:], cls="sub", cy=items[-1]["cy"] + SUBPITCH))
            continue
        a, b = next(gi)
        y0, y1, x0, _ = cl[a]
        h = y1 - y0 + 1
        cls = "sub" if h <= 14 else "label" if (h <= 19 or h > 30) else "name"
        cy = (y0 + cl[b][1]) / 2 if a != b else (y0 + y1) / 2
        if cls == "label" and h > 30:  # two-line label (860): one line at the first line's height
            cy = y0 + 9
        if cls == "sub" and any(t.startswith("+") for t in lines):
            cy -= 1
        items.append(dict(s=s, cls=cls, cy=cy, x0=x0))
    nm = [i for i in items if i["cls"] == "name"]
    x = min([i["x0"] for i in nm] + [cv.width - 2 - hs.width(i["s"], NAME, SIZES["name"]) for i in nm]) if nm else 0
    cx = cv.width / 2
    for i in items:
        if i["cls"] == "name":
            put(cv, i["s"], NAME, SIZES["name"], BLUE, x, i["cy"], cv.width - 4)
            cx = x + hs.width(i["s"], NAME, SIZES["name"]) / 2
        elif i["cls"] == "label":
            put(cv, i["s"], NAME, SIZES["label"], BLUE, i["x0"], i["cy"], cv.width - 4)
        else:
            size = fit(i["s"], SUBFONT, SIZES["sub"], cv.width - 4)
            w = hs.width(i["s"], SUBFONT, size)
            hs.text(cv, i["s"], SUBFONT, size, [(0, BLUE)], max(w / 2 + 2, min(cv.width - 2 - w / 2, cx)),
                    round(i["cy"] + 0.357 * size), "c")


def disc(cv, ch):
    """ED_B heading disc: white circle (x 6-35, y 1-30) with the heading's first letter in blue."""
    ss = 8
    m = Image.new("L", (30 * ss, 30 * ss), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 30 * ss - 1, 30 * ss - 1), fill=255)
    m = m.resize((30, 30), Image.LANCZOS)
    cv.alpha_composite(Image.composite(Image.new("RGBA", (30, 30), WHITE), Image.new("RGBA", (30, 30), (0, 0, 0, 0)), m), (6, 1))
    f = "os:700:90"
    size = 23
    while hs.width(ch, f, size) > 21 and size > 12:
        size -= 1
    hs.text(cv, ch, f, size, [(0, BLUE)], 21, round(16 + 0.357 * size), "c")


def draw(row, im):
    n = int(row["n"])
    lines = row["en"].split("\\n")
    cv = Image.new("RGBA", im.size, (0, 0, 0, 0))
    cl = clusters(im)
    if n <= 847:
        heading(cv, lines, cl)
    elif n <= 868:
        names(cv, lines, n, cl)
        if n in (858, 859):  # "studio A-CAT" stays: keep the original pixels above the names
            top = im.crop((0, 0, im.width, 30))
            cv.paste(top, (0, 0))
    elif n <= 925:
        head, name = lines
        disc(cv, head[0])
        put(cv, head[1:], HEAD, SIZES["head"] + 1, WHITE, 36, 17.5, im.width - 38)
        put(cv, name, NAME, SIZES["name"], WHITE, 8, 61.5, im.width - 10)
    elif n == 926:
        size = 19
        put(cv, lines[0], NAME, size, WHITE, 9, 23, im.width - 10)
        put(cv, lines[1], NAME, size, WHITE, 57, 50.5, im.width - 57)
    elif n == 941:
        heading(cv, lines, cl, align_x=8)
    else:  # 942
        put(cv, lines[0], NAME, SIZES["name"], WHITE, 3, 17, im.width - 4)
    return cv
