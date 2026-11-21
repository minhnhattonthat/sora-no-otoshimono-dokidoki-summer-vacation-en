"""Graphics text (docs/re/graphics.md): English redraws of the Japanese GIMs, one tsv per group.

    python -X utf8 tools/gfx.py gen [GROUP..]      write gfx/out/<group>/<n>.png (RGBA, the GIM's size); default all
    python -X utf8 tools/gfx.py preview GROUP..    work/gfx/preview_<group>.png: original | English, x2, on a dark bg
    python -X utf8 tools/gfx.py orig N [ZOOM]      work/gfx/orig_<n>.png: one survey image zoomed (to read its text)

gfx/<group>.tsv columns: n (survey number, work/gimpng/index.tsv), md5 (of the original GIM: pins n), jp, en, and
optionally rects ("x,y,w,h;x,y,w,h": the only area the redraw may change; empty = the whole image).
A group's look is a function draw(row, original RGBA) -> English RGBA of the same size: STYLES here, or
tools/gfx_<group>.py defining draw(). gen fails when a redraw changes a pixel outside the row's rects.
Build: repl(res) re-encodes every gfx/out PNG into every copy of its GIM. Needs work/gimpng (tools/gimsurvey.py).
"""
import csv, glob, hashlib, importlib, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill import SCRIPTS  # noqa: E402
sys.path.insert(0, SCRIPTS)
import gim, typeset  # noqa: E402
from PIL import Image, ImageChops, ImageFont  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFX = os.path.join(ROOT, "gfx")
OUT = os.path.join(GFX, "out")
SURVEY = os.path.join(ROOT, "work", "gimpng")
FONT = os.path.join(ROOT, "fonts", "OpenSans-Semibold.ttf")
VFONT = os.path.join(ROOT, "fonts", "OpenSans-Variable.ttf")  # OFL; axes weight 300-800, width 75-100


def _font(name, size, _plain=typeset.font):
    """typeset font names "os:WEIGHT:WIDTH" (e.g. "os:800:75" = ExtraBold Condensed) select the variable Open Sans."""
    if not name.startswith("os:"):
        return _plain(name, size)
    if (name, size) not in typeset._cache:
        f = ImageFont.truetype(VFONT, size)
        f.set_variation_by_axes([int(v) for v in name[3:].split(":")])
        typeset._cache[name, size] = f
    return typeset._cache[name, size]


typeset.font = _font  # text_image()/wrap() look font() up in typeset's globals


def rows(group):
    with open(os.path.join(GFX, group + ".tsv"), encoding="utf-8", newline="") as f:
        out = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    for r in out:
        r["group"] = group
    return out


def groups():
    return sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(GFX, "*.tsv")))


def index():
    """{n: (md5, [(res path, offset)])} from the survey."""
    out = {}
    with open(os.path.join(SURVEY, "index.tsv"), encoding="utf-8") as f:
        for line in f:
            n, md5, _, _, *copies = line.rstrip("\n").split("\t")
            out[int(n)] = (md5, [(c.rsplit(":", 1)[0], int(c.rsplit(":", 1)[1], 16)) for c in " ".join(copies).split()])
    return out


def original(n):
    return Image.open(os.path.join(SURVEY, f"{int(n):04d}.png")).convert("RGBA")


def out_path(r):
    return os.path.join(OUT, r["group"], f"{int(r['n']):04d}.png")


def rects(r):
    return [tuple(int(v) for v in s.split(",")) for s in (r.get("rects") or "").split(";") if s]


def outside(a, b, rs):
    """Pixels that differ between a and b outside the rects (all rects empty -> none can)."""
    if not rs:
        return 0
    diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v else 0)
    for x, y, w, h in rs:
        diff.paste(0, (x, y, x + w, y + h))
    return sum(1 for v in diff.getdata() if v)


# ---- styles: draw(row, original RGBA) -> English RGBA of the same size ----

def plate(r, im):
    """Speaker name plates: white antialiased Open Sans Semibold 17 centred on a transparent plate."""
    return typeset.text_image(im.width, im.height, r["en"], FONT, size=17, fill=(255, 255, 255, 255), valign="m")


STYLES = {"plate": plate}


def style(group):
    if group in STYLES:
        return STYLES[group]
    return importlib.import_module(f"gfx_{group}").draw


def gen(names=()):
    done = 0
    for g in names or groups():
        draw = style(g)
        os.makedirs(os.path.join(OUT, g), exist_ok=True)
        for r in rows(g):
            if not r["en"]:
                continue
            im = original(r["n"])
            new = draw(r, im)
            assert new.size == im.size, (g, r["n"], new.size, im.size)
            bad = outside(im, new, rects(r))
            assert not bad, f"{g} {r['n']}: {bad} pixels changed outside the declared rects"
            new.save(out_path(r))
            done += 1
    return done


def preview(group):
    pairs = [(original(r["n"]), Image.open(out_path(r)).convert("RGBA")) for r in rows(group) if r["en"]]
    z = 2
    w = max(a.width for a, _ in pairs) * z
    sheet = Image.new("RGBA", (2 * w + 8, sum(a.height * z + 4 for a, _ in pairs)), (50, 50, 80, 255))
    y = 0
    for a, b in pairs:
        for x, im in ((0, a), (w + 8, b)):
            sheet.alpha_composite(im.resize((im.width * z, im.height * z), Image.NEAREST), (x, y))
        y += a.height * z + 4
    path = os.path.join(ROOT, "work", "gfx", f"preview_{group}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)
    return path


def show(n, zoom=2):
    im = original(n)
    bg = Image.new("RGBA", im.size, (50, 50, 80, 255))
    bg.alpha_composite(im)
    path = os.path.join(ROOT, "work", "gfx", f"orig_{int(n):04d}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bg.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(path)
    return path


def repl(res):
    """{res path: bytes} with every gfx/out PNG encoded into every copy of its GIM (md5-checked against the survey)."""
    todo = [r for g in groups() for r in rows(g) if os.path.isfile(out_path(r))]
    if not todo:
        return {}
    idx, out = index(), {}
    assert len({r["n"] for r in todo}) == len(todo), "a GIM is drawn by two rows"
    for r in todo:
        n = int(r["n"])
        md5, copies = idx[n]
        assert r["md5"] == md5, f"{r['group']} {n}: not the GIM the tsv pinned (re-run tools/gimsurvey.py?)"
        im = Image.open(out_path(r)).convert("RGBA")
        new = None
        for path, off in copies:
            d = out.setdefault(path, bytearray(res[path]))
            size = 0x10 + int.from_bytes(d[off + 0x14:off + 0x18], "little")
            blob = bytes(d[off:off + size])
            assert hashlib.md5(blob).hexdigest() == md5, f"{path}:{off:#x} is not GIM {n}"
            if new is None:
                img = gim.parse(blob)[0]
                assert im.size == (img.w, img.h), f"{out_path(r)}: {im.size} != {(img.w, img.h)}"
                b = im.tobytes()
                new = gim.encode(blob, img, [b[4 * img.w * y:4 * img.w * (y + 1)] for y in range(img.h)])
            d[off:off + size] = new
    return {p: bytes(d) for p, d in out.items()}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    if cmd == "gen":
        print(f"{gen(args)} images -> gfx/out")
    elif cmd == "preview" and args:
        for g in args:
            print(preview(g))
    elif cmd == "orig" and args:
        print(show(args[0], int(args[1]) if len(args) > 1 else 2))
    else:
        sys.exit(__doc__)
