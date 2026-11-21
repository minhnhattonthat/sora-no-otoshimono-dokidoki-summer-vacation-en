"""Graphics survey: find every GIM (standalone or embedded in FSB/FAB/...) under work/res, dedupe by md5, decode to
work/gimpng/<n>.png, write work/gimpng/index.tsv (n, md5, w, h, every path:offset holding it) and contact sheets
work/gimpng/sheet_<group>_<k>.png labelled with n. Prints every GIM it could not decode, with the reason.

    python -X utf8 tools/gimsurvey.py [--res work/res] [--out work/gimpng] [--per 48]
"""
import argparse, collections, hashlib, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill import SCRIPTS  # noqa: E402
sys.path.insert(0, SCRIPTS)
import gim  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

MAGIC = b"MIG.00.1PSP\0"


def gims_in(d):
    o = d.find(MAGIC)
    while o != -1:
        # GIM root block at +0x10: u16 id, u16 unk, u32 block size (whole tree) -> total = 0x10 + size
        size, = struct.unpack_from("<I", d, o + 0x14)
        yield o, d[o:o + 0x10 + size]
        o = d.find(MAGIC, o + 0x10)


def group_of(path):
    p = path.replace("\\", "/").split("/RES/")[-1]
    return p.rsplit("/", 1)[0].replace("/", "_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="work/res"); ap.add_argument("--out", default="work/gimpng")
    ap.add_argument("--per", type=int, default=48)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    seen = {}  # md5 -> n
    where = collections.defaultdict(list)
    info = {}
    groups = collections.defaultdict(list)
    for root, _, files in os.walk(a.res):
        for fn in sorted(files):
            path = os.path.join(root, fn)
            d = open(path, "rb").read()
            for off, blob in gims_in(d):
                h = hashlib.md5(blob).hexdigest()
                rel = os.path.relpath(path, a.res).replace("\\", "/")
                if h not in seen:
                    n = len(seen)
                    seen[h] = n
                    try:
                        im = gim.parse(blob)[0]
                        w, hgt, rows = gim.to_rgba(blob, im)
                        img = Image.frombytes("RGBA", (w, hgt), b"".join(rows))
                        img.save(os.path.join(a.out, f"{n:04d}.png"))
                        info[n] = (h, w, hgt)
                        groups[group_of(rel)].append(n)
                    except Exception as e:  # report, never drop silently
                        print(f"SKIP {rel}:{off:#x} ({e!r})")
                        info[n] = (h, 0, 0)
                where[seen[h]].append(f"{rel}:{off:#x}")
    with open(os.path.join(a.out, "index.tsv"), "w", encoding="utf-8") as f:
        for n in sorted(info):
            h, w, hgt = info[n]
            f.write(f"{n}\t{h}\t{w}\t{hgt}\t{' '.join(where[n])}\n")
    for g, ns in sorted(groups.items()):
        for k in range(0, len(ns), a.per):
            chunk = ns[k:k + a.per]
            cells = []
            for n in chunk:
                im = Image.open(os.path.join(a.out, f"{n:04d}.png"))
                s = min(1.0, 240 / max(im.width, 1), 136 / max(im.height, 1))
                im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))))
                cells.append((n, im))
            cols = 6
            cw, ch = 248, 150
            sheet = Image.new("RGB", (cw * cols, ch * ((len(cells) + cols - 1) // cols)), (60, 60, 90))
            dr = ImageDraw.Draw(sheet)
            for i, (n, im) in enumerate(cells):
                x, y = (i % cols) * cw, (i // cols) * ch
                bg = Image.new("RGBA", im.size, (60, 60, 90, 255)); bg.alpha_composite(im.convert("RGBA"))
                sheet.paste(bg.convert("RGB"), (x + 4, y + 12))
                dr.text((x + 2, y), f"{n}", fill=(255, 255, 0))
            sheet.save(os.path.join(a.out, f"sheet_{g}_{k // a.per}.png"))
    print(len(seen), "unique GIMs,", sum(len(v) for v in where.values()), "copies,", len(groups), "groups")


if __name__ == "__main__":
    main()
