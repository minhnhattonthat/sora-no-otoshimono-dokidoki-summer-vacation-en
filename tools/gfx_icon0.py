"""XMB icon ICON0.PNG (144x80, /PSP_GAME/ICON0.PNG + RES/1ST/ICON0.PNG): a shrunken copy of title logo 192.
Finds the logo's scale and offset in the icon, inpaints the Japanese subtitle there and draws the English one:
    python -X utf8 tools/gfx_icon0.py        -> gfx/out/xmb/ICON0.PNG (build.py ships it when present)"""
import os

import numpy as np
from PIL import Image

import gfx  # noqa: F401  (registers the "os:WEIGHT:WIDTH" fonts with typeset)
import gfx_hexstart as hs
import gfx_logo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "work", "res", "RES", "1ST", "ICON0.PNG")
OUT = os.path.join(ROOT, "gfx", "out", "xmb", "ICON0.PNG")
SUB = (106, 96, 290, 120)  # subtitle box in logo 192 (gfx_logo.RECT)


def fit(icon, logo):
    """(scale, x, y) placing logo in icon with the least colour error on the logo's opaque pixels."""
    ic = np.asarray(icon, float)
    best = None
    for s in np.arange(0.36, 0.56, 0.004):
        sm = logo.resize((round(logo.width * s), round(logo.height * s)), Image.LANCZOS)
        a = np.asarray(sm, float)
        m = a[..., 3] > 250
        for y in range(0, icon.height - sm.height + 1):
            for x in range(0, icon.width - sm.width + 1):
                d = np.abs(ic[y:y + sm.height, x:x + sm.width] - a[..., :3])[m].mean()
                if best is None or d < best[0]:
                    best = (d, s, x, y)
    return best


def inpaint(a, mask, iters=80):
    cur, known = a.copy(), ~mask
    cur[mask] = 0
    for _ in range(iters):
        acc, w = np.zeros_like(cur), np.zeros(mask.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(known, (dy, dx), (0, 1))
            acc += np.roll(cur, (dy, dx), (0, 1)) * k[..., None]
            w += k
        fill = mask & (w > 0)
        cur[fill] = acc[fill] / w[fill][:, None]
        known = known | fill
    return cur


def make():
    icon = Image.open(SRC).convert("RGB")
    jp = Image.open(os.path.join(ROOT, "work", "gimpng", "0192.png")).convert("RGBA")
    err, s, x, y = fit(icon, jp)
    assert err < 30, f"logo not found in the icon (error {err:.1f})"
    size = (round(jp.width * s), round(jp.height * s))
    x0, y0, x1, y1 = (round(v * s) for v in SUB)
    sub = np.zeros((icon.height, icon.width), bool)  # icon pixels the old subtitle touches (+1 px halo)
    ja = np.asarray(jp.resize(size, Image.LANCZOS))[..., 3] > 8
    ja[:y0], ja[y1:], ja[:, :x0], ja[:, x1:] = False, False, False, False
    sub[y:y + size[1], x:x + size[0]] = ja
    for _ in range(1):
        sub[1:] |= sub[:-1].copy(); sub[:-1] |= sub[1:].copy(); sub[:, 1:] |= sub[:, :-1].copy(); sub[:, :-1] |= sub[:, 1:].copy()
    out = Image.fromarray(inpaint(np.asarray(icon, float), sub).round().clip(0, 255).astype(np.uint8)).convert("RGBA")
    # the logo's own subtitle shrunk to this scale is ~6 px tall and unreadable: two lines at 10 px instead,
    # white on the logo's blue edge like the icon's katakana, centred under the old subtitle
    cx = x + (x0 + x1) // 2
    for line, base in (("DokiDoki", y + y1 - 2), ("Summer Vacation", y + y1 + 8)):
        hs.text(out, line, "os:800:75", 10, [(1, gfx_logo.EDGE), (0, gfx_logo.WHITE)], cx, base, align="c")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.convert("RGB").save(OUT, optimize=True)
    print(f"logo at scale {s:.3f} offset {x},{y} (error {err:.1f}) -> {OUT}")


if __name__ == "__main__":
    make()
