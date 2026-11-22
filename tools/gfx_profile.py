"""gfx group profile (COMMU_10_CARDGALLERY 752-775): character profile blocks, blue labels + grey values on transparency.

en = lines joined by "|": "Label=value" (blue label, grey value), "^text" (value continuation, indented to the last
label's value), "text" (plain grey line at the left margin), "{small}" at the end of a value = 10 px whisper.
A label gets ":" unless it ends in "?" or ")" (as the original). Lines too wide for the 184 px are wrapped.
"""
from PIL import Image

import gfx
import gfx_hexstart as hs

BLUE, GREY = (0, 112, 197, 255), (119, 119, 119, 255)
LABEL, VALUE, SIZE, PITCH, BASE0, GAP = "os:700:75", "os:600:75", 13, 17, 14, 4


def balanced(s, maxw):
    """Wrap s to maxw, then to the narrowest width that gives the same number of lines (no orphan last word)."""
    n = len(gfx.typeset.wrap(s, VALUE, SIZE, maxw).split("\n"))
    lo, hi = 1, maxw
    while lo < hi:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if len(gfx.typeset.wrap(s, VALUE, SIZE, mid).split("\n")) <= n else (mid + 1, hi)
    return gfx.typeset.wrap(s, VALUE, SIZE, hi).split("\n")


def draw(row, im):
    cv = Image.new("RGBA", im.size, (0, 0, 0, 0))
    vx, k = 0, 0
    lines = []
    for ln in row["en"].split("|"):
        if ln.startswith("+"):  # soft join: the sentence flows on and is wrapped to the column
            lines[-1] += " " + ln[1:]
        else:
            lines.append(ln)
    for ln in lines:
        x, small, lab = 0, "", ""
        if "{" in ln:
            ln, small = ln.rstrip("}").split("{")
        if "=" in ln:
            lab, ln = ln.split("=", 1)
            lab += "" if lab[-1] in "?)" else ":"
            x = vx = hs.width(lab, LABEL, SIZE) + GAP
            hs.text(cv, lab, LABEL, SIZE, [(0, BLUE)], 0, BASE0 + k * PITCH)
        elif ln.startswith("^"):
            ln, x = ln[1:], vx
        for j, part in enumerate(balanced(ln, im.width - x) if ln else []):
            if j:
                k += 1
            base = BASE0 + k * PITCH
            w = hs.text(cv, part, VALUE, SIZE, [(0, GREY)], x, base)
            assert x + w <= im.width, (row["n"], part)
            end = x + w + 4
        if small:
            end += hs.text(cv, small, VALUE, 11,[(0, GREY)], end, BASE0 + k * PITCH)
            assert end <= im.width, (row["n"], small)
        k += 1
    bb = cv.getchannel("A").getbbox()
    assert bb[3] <= im.height, (row["n"], bb, k)
    return cv
