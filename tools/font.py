"""English glyphs for the dialogue font RES/1ST/HG_G18.TFP and their advance widths (the VWF table, tools/vwf.py).

    python -X utf8 tools/font.py [--sheet OUT.png]   preview the redrawn ASCII glyphs (4x zoom)

TFP (docs/re/script.md §Font): 'T2FP', u16 glyph count at 0x0E... we only rely on: u16 code table at 0x20 (ASCII codes
0x00-0x7F at glyph index = code), 18x18 4bpp glyphs (162 bytes, low nibble = left pixel) from 0x3F78. Ink levels 0-12:
level 13 draws nothing in game (a fully inked English stem vanished), though a few stock glyphs carry it.
ASCII 0x20-0x7E is re-rendered from fonts/OpenSans-Semibold.ttf (Apache 2.0) at SIZE px on baseline BASE; the advance
of each is its rounded font advance + TRACK. Every other code keeps its glyph and the stock half-width advance 9.
"""
import os, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTF = os.path.join(ROOT, "fonts", "OpenSans-Semibold.ttf")
SIZE, BASE, TRACK, INK = 14, 14, 0, 12
CELL, GLYPHS = 18, 0x3F78
HALF = 9  # the engine's stock advance for a one-byte character (size 18 / 2)


def glyph_offset(tfp, code):
    n = (GLYPHS - 0x20) // 2
    codes = struct.unpack_from(f"<{n}H", tfp, 0x20)
    return GLYPHS + 162 * codes.index(code)


def render(ch):
    """(18x18 ink levels row-major, advance px)."""
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(TTF, SIZE)
    im = Image.new("L", (CELL, CELL), 0)
    ImageDraw.Draw(im).text((0, BASE), ch, font=f, fill=255, anchor="ls")
    adv = round(f.getlength(ch)) + TRACK
    assert 0 < adv <= CELL, (ch, adv)
    return [round(p * INK / 255) for p in im.getdata()], adv


_W = None


def width(text):
    """Pixel width of one line as the engine lays it out (one-byte codes from the VWF table; anything else, i.e.
    a full-width Shift-JIS character, 18)."""
    global _W
    if _W is None:
        _W = bytearray([HALF] * 256)
        for c in range(0x20, 0x7F):
            _W[c] = render(chr(c))[1]
    return sum(_W[ord(c)] if ord(c) < 0x80 else 2 * HALF for c in text)


def pack(px):
    return bytes(px[i] | px[i + 1] << 4 for i in range(0, len(px), 2))


def patch(tfp):
    """(new TFP bytes, 256-byte advance table indexed by the one-byte code)."""
    out = bytearray(tfp)
    widths = bytearray([HALF] * 256)
    for c in range(0x20, 0x7F):
        px, widths[c] = render(chr(c))
        o = glyph_offset(tfp, c)
        out[o:o + 162] = pack(px)
    return bytes(out), bytes(widths)


def sheet(tfp, path, text="The quick brown fox jumps over the lazy dog. \"Tomoki!\" Ikaros, Nymph? 0123456789"):
    """Draw text the way the engine does (advance table, ink as grey) at 4x zoom."""
    from PIL import Image
    new, w = patch(tfp)
    W = sum(w[ord(c)] for c in text) + CELL
    im = Image.new("L", (W, CELL), 255)
    x = 0
    for c in text:
        o = glyph_offset(new, ord(c))
        g = new[o:o + 162]
        for i in range(CELL * CELL):
            v = g[i // 2] >> (4 * (i & 1)) & 15
            if v:
                p = (x + i % CELL, i // CELL)
                im.putpixel(p, min(im.getpixel(p), 255 - v * 255 // INK))
        x += w[ord(c)]
    im.resize((W * 4, CELL * 4), Image.NEAREST).save(path)
    return x


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default=os.path.join(ROOT, "work", "qa", "font_sheet.png"))
    a = ap.parse_args()
    tfp = open(os.path.join(ROOT, "work", "res", "RES", "1ST", "HG_G18.TFP"), "rb").read()
    print(a.sheet, sheet(tfp, a.sheet), "px")
