"""gfx group hexspecial (HEXCITE_20_HEX_SPECIAL): special-move cut-ins.

Every move is a run of frames of ONE animation (no sprite sheet): the game shows them in order, so each frame is the final
English lettering transformed the way the Japanese frame is (zoom about the frame-1 centre + a fade, see ZOOM / FADE).
  Tomoki Time   1155-1161 slide-in of the Latin TOMO*KI.TIME (already English: no row); 1162-1166 katakana ruby -> blank.
  Apollon       1167-1186 four cells x 5 frames: 最(ア) 終(ポ) 兵(ロ) 器(ン) -> ULTI(A) MATE(PO) WEA(LL) PON(ON).
  Paradise Song 1187-1193 slide-in + overshoot of 超々超音波振動子 -> PARADISE SONG; 1194-1198 ruby -> blank (hexmenu does too).
  Sohara Chop   1199-1206 そはら / チョップ -> SOHARA / CHOP (4 frames each).
  Crush         1207-1214 圧 / 殺 -> CRU / SH.
  New World     1215-1229 新 / 大 / 陸 -> NEW / WOR / LD.
Row en = "MAIN|RUBY" (ruby above the main text, the original's furigana line); "(none)" = blank frame.
Look: Open Sans ExtraBold Condensed caps, white (pink for Apollon) with an opaque 2 px outline + soft glow in the move's colour.
"""
import numpy as np
from PIL import Image, ImageFilter

import gfx
from gfx_hexstart import text, width

F_MAIN = "os:800:75"
F_WIDE = "os:800:90"
Z5 = [0.18, 0.32, 0.55, 1.2, 1.0]   # zoom per frame (measured on the Japanese: alpha>20 bbox vs the last frame)
A5 = [23, 55, 107, 255, 255]         # frame alpha (max alpha of the Japanese frame)
Z4 = [0.22, 0.48, 1.18, 1.0]
A4 = [37, 91, 255, 255]
ZW = [1.0, 1.0, 1.02, 1.05, 1.05, 1.09, 1.0]  # Paradise Song wipe frames 1187-1193
PINK, MAGENTA, BLUE, ORANGE, RED, NAVY = (255, 207, 245), (253, 0, 194), (1, 125, 244), (253, 58, 0), (193, 1, 1), (54, 76, 171)
WHITE = (255, 255, 255)

# move: (frames per cell, zoom, alpha, fill, glow, shear, cells [(first n, main, ruby)])
MOVES = {
    "apollon": (5, Z5, A5, PINK, MAGENTA, 0.0, [(1167, "ULTI", "A"), (1172, "MATE", "PO"), (1177, "WEA", "LL"), (1182, "PON", "ON")]),
    "sohara": (4, Z4, A4, WHITE, ORANGE, 0.18, [(1199, "SOHARA", ""), (1203, "CHOP", "")]),
    "crush": (4, Z4, A4, WHITE, RED, 0.18, [(1207, "CRU", ""), (1211, "SH", "")]),
    "world": (5, Z5, A5, WHITE, NAVY, 0.15, [(1215, "NEW", ""), (1220, "WOR", ""), (1225, "LD", "")]),
}
CELL = {n0: (k, count, i) for k, (count, *_, cells) in MOVES.items() for i, (n0, *_) in enumerate(cells)}
BLANK = set(range(1162, 1167)) | set(range(1194, 1199))
WIPE = range(1187, 1194)


def rows():
    """(n, jp, en) of every row of the tsv (see gfx/hexspecial.tsv)."""
    jp = {"apollon": ["最", "終", "兵", "器"], "sohara": ["そはら", "チョップ"], "crush": ["圧", "殺"], "world": ["新", "大", "陸"]}
    out = [(n, "トモ★キ・タイム", "(none)") for n in sorted(BLANK) if n < 1170]
    out += [(n, "パラダイス＝ソング", "(none)") for n in sorted(BLANK) if n > 1190]
    for n in WIPE:
        out.append((n, "超々超音波振動子", "PARADISE SONG"))
    for k, (count, _, _, _, _, _, cells) in MOVES.items():
        for (n0, main, ruby), j in zip(cells, jp[k]):
            out += [(n0 + i, j, f"{main}|{ruby}" if ruby else main) for i in range(count)]
    return sorted(out)


def bbox(im, thr):
    ys, xs = np.where(np.array(im)[..., 3] > thr)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def neon(size, lines, fill, glow, shear):
    """lines = [(text, font, px, cx, baseline)] -> RGBA: outline + glow in `glow`, flat `fill` letters on top."""
    t = Image.new("RGBA", size, (0, 0, 0, 0))
    for s, font, px, cx, base in lines:
        text(t, s, font, px, [(0, WHITE + (255,))], cx, base, "c", shear=shear)
    m = t.getchannel("A")
    ring = m.filter(ImageFilter.MaxFilter(5))
    halo = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3.2)).point(lambda v: min(255, int(v * 1.9)))
    ga = np.maximum(np.array(ring), np.array(halo)).astype("uint8")
    out = Image.new("RGBA", size, tuple(glow) + (0,))
    out.putalpha(Image.fromarray(ga))
    body = Image.new("RGBA", size, tuple(fill) + (255,))
    body.putalpha(m)
    out.alpha_composite(body)
    return out


def place(final, s, dx, dy, alpha, px, py):
    """final zoomed by s about (px, py), moved by (dx, dy), alpha scaled to `alpha` (0-255)."""
    w, h = final.size
    z = final.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS) if s != 1 else final.copy()
    a = z.getchannel("A").point(lambda v: v * alpha // 255)
    z.putalpha(a)
    out = Image.new("RGBA", final.size, (0, 0, 0, 0))
    ox, oy = round(px - s * px + dx), round(py - s * py + dy)
    x0, y0 = max(0, -ox), max(0, -oy)
    z = z.crop((x0, y0, min(z.width, w - ox), min(z.height, h - oy)))
    if z.width > 0 and z.height > 0:
        out.alpha_composite(z, (ox + x0, oy + y0))
    return out


def cell_size(k):
    """One font size for every chunk of move k: the biggest whose widest chunk fits the Japanese ink and band."""
    count, _, _, _, _, shear, cells = MOVES[k]
    n_last = cells[0][0] + count - 1
    jp = gfx.original(n_last)
    x0, y0, x1, y1 = bbox(jp, 128)
    ruby = bool(cells[0][2])
    limit = min(x1 - x0, jp.width - 16) - 2
    band = (y1 - y0) - (24 if ruby else 0)
    f = F_MAIN
    for px in range(90, 12, -1):
        if px * 0.72 <= band and all(width(m, f, px) <= limit for _, m, _ in cells):
            return px
    raise ValueError(k)


def cell(row, im):
    k, count, i = CELL[max(n0 for n0 in CELL if n0 <= int(row["n"]))]
    _, zoom, alphas, fill, glow, shear, cells = MOVES[k]
    n0, main, ruby = cells[i]
    j = int(row["n"]) - n0
    last = gfx.original(n0 + count - 1)
    x0, y0, x1, y1 = bbox(last, 128)
    cx = (x0 + x1) / 2
    px = cell_size(k)
    lines = []
    if ruby:
        rpx = 21
        lines.append((ruby, F_MAIN, rpx, cx, y0 + round(0.72 * rpx) + 1))
        top = y0 + 24
    else:
        top = y0
    cap = round(0.714 * px)
    lines.append((main, F_MAIN, px, cx, round(top + ((y1 - top) + cap) / 2 - 1)))
    final = neon(im.size, lines, fill, glow, shear)
    fx0, fy0, fx1, fy1 = bbox(gfx.original(n0), 12)
    return place(final, zoom[j], 0, 0, alphas[j], (fx0 + fx1) / 2, (fy0 + fy1) / 2)


def wipe(row, im):
    n = int(row["n"])
    jp = {m: gfx.original(m) for m in (n, 1193)}
    j = n - 1187
    s = ZW[j]
    lf = bbox(jp[1193], 128)
    lk = bbox(jp[n], 128)
    cx_jp = (lf[0] + lf[2]) / 2
    dx_jp = lk[0] - cx_jp - s * (lf[0] - cx_jp)
    px = 0
    for p in range(60, 12, -1):
        if width(row["en"], F_WIDE, p) <= (lf[2] - lf[0]) - 8 and p * 0.72 <= 40:
            px = p
            break
    cx = im.width / 2
    final = neon(im.size, [(row["en"], F_WIDE, px, cx, round(38 + 0.714 * px / 2))], WHITE, BLUE, 0.0)
    left_f = bbox(final, 128)[0]
    k = (476 - left_f) / (476 - cx_jp - (lf[0] - cx_jp))  # frame 1187's sliver lands where the Japanese one does
    return place(final, s, k * dx_jp, 0, 255, cx, 38)


def draw(row, im):
    n = int(row["n"])
    if row["en"] == "(none)":
        return Image.new("RGBA", im.size, (0, 0, 0, 0))
    return wipe(row, im) if n in WIPE else cell(row, im)
