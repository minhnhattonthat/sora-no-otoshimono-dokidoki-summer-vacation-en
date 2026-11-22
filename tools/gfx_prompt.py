"""Group prompt (COMMON_0): Yes/No buttons (n 3-6) and the orange-outlined confirm prompts (n 7-23).
Shared by title/param/cardget/windows: button() and outlined()."""
import gfx
from gfx import typeset
from PIL import Image

ORANGE = (243, 120, 23, 255)
WHITE = (255, 255, 255, 255)


def lines(r):
    return r["en"].replace("\\n", "\n").split("\n")


def condensed(text_lines, w, size, weight, stroke=0, widths=(100, 90, 80, 75)):
    """First width axis (down to 75) at which every line fits w; returns the font name."""
    for wd in widths:
        name = f"os:{weight}:{wd}"
        f = typeset.font(name, size)
        if max(f.getlength(t) for t in text_lines) + 2 * stroke + 2 <= w:
            return name
    raise ValueError(f"does not fit {w}px at size {size}: {text_lines}")


def outlined(im, text_lines, size=18, weight=700, stroke=3, fill=WHITE, colour=ORANGE, spacing=-1, valign="m", box=None):
    """White text with a coloured outline on transparency (the prompt look)."""
    box = box or (0, 0, im.width, im.height)
    name = condensed(text_lines, box[2], size, weight, stroke)
    return typeset.text_image(im.width, im.height, "\n".join(text_lines), name, size=size, fill=fill,
                              stroke=(stroke, colour), spacing=spacing, valign=valign, box=box, canvas=im)


def button(im, text, rect, size=16, weight=700, fill=WHITE, white_min=235):
    """Button label: remove the Japanese inside rect (x,y,w,h) from the panel, then centre the English there."""
    x, y, w, h = rect
    base = typeset.inpaint(im, (x, y, x + w, y + h), white_min=white_min)
    name = condensed([text], w, size, weight)
    return typeset.text_image(im.width, im.height, text, name, size=size, fill=fill, canvas=base, box=rect, valign="m")


def draw(row, im):
    t = lines(row)
    if int(row["n"]) <= 6:
        return button(im, " ".join(t), (14, 5, 52, 22))
    return outlined(Image.new("RGBA", im.size, (0, 0, 0, 0)), t)
