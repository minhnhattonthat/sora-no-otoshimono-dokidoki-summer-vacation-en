"""Unpack res.ptd (and the nested PTDs in RES/__PACK__) into work/res/, YKLZ-decompressed.

    python -X utf8 tools/unpack.py [--iso-dir work/iso] [--out work/res]
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ptd, yklz  # noqa: E402


def unpack_ptd(buf, out, log):
    _, files = ptd.toc(buf)
    for f in files:
        raw = buf[f["off"]:f["off"] + f["size"]]
        data = yklz.unpack(raw) if f["comp"] else raw
        dest = os.path.join(out, f["path"].replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(data)
        log.write(f'{f["index"]}\t{f["path"]}\t{f["off"]:#x}\t{f["size"]}\t{f["comp"]}\t{len(data)}\n')
        if f["name"].endswith(".PTD") and data[:4] == b"PETA":
            unpack_ptd(data, dest[:-4] + "_PTD", log)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso-dir", default="work/iso")
    ap.add_argument("--out", default="work/res")
    a = ap.parse_args()
    buf = open(os.path.join(a.iso_dir, "PSP_GAME/USRDIR/res/res.ptd"), "rb").read()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "index.tsv"), "w", encoding="utf-8") as log:
        unpack_ptd(buf, a.out, log)


if __name__ == "__main__":
    main()
