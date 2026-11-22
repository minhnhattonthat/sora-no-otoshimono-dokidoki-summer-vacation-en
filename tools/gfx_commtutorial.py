"""gfx group commtutorial (COMMU_10_COM_TUTORIAL 814-819 + the IMG_BG copies 1313-1316): the six communication tutorial
pages, full-screen art with Japanese titles, body lines, callouts and a few texts inside the miniature screenshots.

Every text is an "element": a rect in which the Japanese is erased, then English drawn at the same ink position.
Erase = the ink pixels (a colour test), grown a little, replaced per row by a linear blend of the nearest untouched pixels
left and right of each run (the art is horizontal bands / flat panels, so rows stay intact). Position = the ink bbox of the
original text (centre, left or right edge as the element says), so a label stays where its Japanese was.
en = the page's elements in PAGES order, joined by " | "; "\\n" breaks a line inside an element. 1313-1316 hold the same
pages as 818 817 815 814 (re-encoded) and get the same English.
"""
import numpy as np
from PIL import Image

import gfx
import gfx_hexstart as hs

WHITE = (255, 255, 255, 255)
PAGE = {814: 6, 815: 5, 816: 4, 817: 3, 818: 2, 819: 1, 1313: 2, 1314: 3, 1315: 5, 1316: 6}
BODY, LABEL, TITLE = "os:600:75", "os:700:75", "os:800:75"


def E(rect, size, font=LABEL, kind="dark", thr=170, grow=2, align="c", pitch=0, halo=None, colour=None, dx=0, dy=0, extra=(), flat=None):
    """kind: "dark" (a channel below thr), "light" (all channels above thr) or f(r, g, b arrays) -> ink mask."""
    return dict(rect=rect, size=size, font=font, kind=kind, thr=thr, grow=grow, align=align, pitch=pitch, halo=halo,
                colour=colour, dx=dx, dy=dy, extra=extra, flat=flat)


def title(rect=(100, 1, 280, 26)):  # rows 1-26: the underline bar below (y 27+) is art, not part of the title
    return E(rect, 20, TITLE, halo=2)


def body(size=12):
    return E((8, 34, 464, 34), size, BODY, align="l", pitch=15)


NEXT = E((446, 10, 26, 14), 11, LABEL, thr=140, colour=(114, 114, 114, 255))  # grey on the lilac button (min channel 162)
LITE = dict(kind="light", thr=100, grow=2, colour=(217, 216, 216, 255))  # blurry white lettering on a dark bar

PAGES = {
    6: [title(), body(), NEXT, E((96, 75, 60, 18), 12),
        E((236, 204, 155, 46), 32, TITLE, kind="light", thr=248, grow=7, flat=(228, 237, 254, 255),
          extra=[(5, (200, 210, 247, 150)), (2, (150, 165, 245, 255), "hard")])],
    5: [title((60, 1, 360, 26)), body(), NEXT, E((58, 83, 110, 24), 13), E((320, 85, 92, 22), 13),
        E((260, 225, 214, 41), 13, align="l", pitch=16),
        E((306, 179, 120, 13), 8, grow=1, halo=1, kind=lambda r, g, b: (r < 110) | (np.minimum(np.minimum(r, g), b) > 228),
          colour=(44, 187, 170, 255)),  # teal letters + their white outline
        E((337, 191, 66, 16), 8, align="l", kind=lambda r, g, b: r < 110)],  # right of the 3 sprite (x 328-336)
    4: [title((68, 1, 340, 26)), body(), NEXT,
        E((20, 75, 75, 18), 13), E((100, 75, 65, 17), 13), E((172, 74, 62, 18), 13), E((240, 75, 68, 18), 13),
        E((318, 74, 145, 19), 13),
        E((90, 170, 48, 16), 13), E((203, 170, 72, 16), 13), E((345, 170, 36, 16), 13),
        E((140, 240, 76, 17), 12), E((260, 240, 80, 17), 12)],
    3: [title((140, 1, 200, 26)), body(), NEXT,
        E((306, 76, 70, 18), 13, align="l"), E((306, 92, 164, 16), 11, BODY, align="l"),
        E((306, 140, 110, 17), 13, align="l"),
        E((310, 184, 36, 14), 11), E((350, 184, 36, 14), 11), E((394, 184, 28, 14), 11), E((427, 184, 38, 14), 11),
        E((306, 207, 110, 18), 13, align="l"),
        E((306, 236, 30, 14), 11), E((440, 236, 30, 14), 11),
        E((8, 203, 64, 16), 9, align="l", **LITE),
        E((225, 108, 39, 16), 9, kind=lambda r, g, b: (b - r) > 60, halo=1, dx=-2)],  # the orange arrow crosses at x 264+
    2: [title((140, 1, 200, 26)), body(), NEXT,
        E((176, 81, 140, 19), 13, align="l"), E((176, 97, 140, 21), 13, align="l"), E((176, 114, 140, 21), 13, align="l"),
        E((176, 133, 140, 18), 13, align="l"),
        E((298, 182, 90, 16), 13, align="l"), E((298, 214, 165, 17), 13, align="l"), E((298, 236, 165, 17), 13, align="l")],
    1: [title((140, 1, 200, 26)), body(), NEXT,
        E((126, 201, 68, 15), 10, TITLE, kind="light", thr=200, grow=1, colour=WHITE),
        E((100, 223, 216, 28), 10, BODY, thr=150, align="l", pitch=12)],
}


def rects(n):
    return [e["rect"] for e in PAGES[PAGE[n]]]


def mask_of(a, e):
    x, y, w, h = e["rect"]
    reg = a[y:y + h, x:x + w].astype(int)
    if callable(e["kind"]):
        return e["kind"](reg[..., 0], reg[..., 1], reg[..., 2])
    lo = reg[..., :3].min(axis=2)  # lettering has a low channel (grey, blue, pink, ...); the pale wallpaper/panels none
    return (lo < e["thr"]) if e["kind"] == "dark" else (lo > e["thr"])


def grown(m, g):
    for _ in range(g):
        n = m.copy()
        n[1:] |= m[:-1]
        n[:-1] |= m[1:]
        n[:, 1:] |= m[:, :-1]
        n[:, :-1] |= m[:, 1:]
        m = n
    return m


def erase(a, e, m):
    """a (RGBA array, edited in place): each masked run in e's rect becomes the blend of its unmasked row neighbours."""
    x, y, w, h = e["rect"]
    reg = a[y:y + h, x:x + w]
    if e["flat"]:  # panel with a soft glow round the lettering: a flat panel colour is cleaner than blended rows
        reg[m] = e["flat"]
        return
    src = reg.astype(float)
    for j in range(h):
        i = 0
        while i < w:
            if not m[j, i]:
                i += 1
                continue
            k = i
            while k < w and m[j, k]:
                k += 1
            lo, hi = (i - 1 if i > 0 else None), (k if k < w else None)
            if lo is None and hi is None:  # the whole row is ink: nothing to blend from
                i = k
                continue
            for t in range(i, k):
                if lo is None:
                    reg[j, t] = src[j, hi]
                elif hi is None:
                    reg[j, t] = src[j, lo]
                else:
                    f = (t - lo) / (hi - lo)
                    reg[j, t] = (src[j, lo] * (1 - f) + src[j, hi] * f).round()
            i = k


def draw(row, im):
    n = int(row["n"])
    els = PAGES[PAGE[n]]
    texts = row["en"].split(" | ")
    assert len(texts) == len(els), (n, len(texts), len(els))
    a0 = np.array(im)
    a = a0.copy()
    jobs = []
    for e, s in zip(els, texts):
        m = mask_of(a0, e)
        ys, xs = np.nonzero(m)
        assert len(xs), (n, e["rect"])
        x, y, w, h = e["rect"]
        px = a0[y:y + h, x:x + w][m]
        vals, cnt = np.unique(px.reshape(-1, 4), axis=0, return_counts=True)
        colour = tuple(int(v) for v in (e["colour"] or vals[cnt.argmax()]))
        erase(a, e, grown(m, e["grow"]))
        jobs.append((e, s, colour, (x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1)))
    out = Image.fromarray(a)
    for e, s, colour, (x0, x1, y0, y1) in jobs:
        lines = s.replace("\\n", "\n").split("\n")
        x, y, w, h = e["rect"]
        layers = list(e["extra"]) + ([(e["halo"], WHITE, "hard")] if e["halo"] else [])
        layers.append((0, colour))
        ax = {"l": x0, "c": (x0 + x1) / 2, "r": x1}[e["align"]] + e["dx"]
        cy = (y0 + y1) / 2 + e["dy"]
        layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
        for i, ln in enumerate(lines):
            base = round(cy + 0.36 * e["size"] + (i - (len(lines) - 1) / 2) * e["pitch"])
            wd = hs.text(layer, ln, e["font"], e["size"], layers, round(ax), base, e["align"])
            left = ax if e["align"] == "l" else ax - wd / 2 if e["align"] == "c" else ax - wd
            assert x <= left and left + wd <= x + w, (n, ln, round(left), wd, e["rect"])
        out.alpha_composite(layer.crop((x, y, x + w, y + h)), (x, y))  # clipped: antialias/outline fringe stays inside rect
    return out
