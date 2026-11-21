"""Build build/sora_en.iso from the pinned dump.

    python -X utf8 build.py [--out build/sora_en.iso]

Steps: check the dump (rom.sha1) -> repack res.ptd with the edited files (ptd.repack; none yet, so the result is
byte-identical to the dump: tests/test_identity.py) -> swap it into a copy of the ISO (iso9660.patch).
"""
import argparse, hashlib, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_rom, iso9660, ptd  # noqa: E402

ROM = os.path.join(ROOT, "rom", "Sora no Otoshimono - DokiDoki Summer Vacation (Japan).iso")
RES = "/PSP_GAME/USRDIR/res/res.ptd"


def read_iso_file(iso, path):
    with open(iso, "rb") as f:
        lba, size = next((lba, ln) for p, lba, ln, _ in iso9660.listing(f) if p == path)
        f.seek(lba * 2048)
        return f.read(size)


def build(out, repl):
    """repl: {work/res-relative path: uncompressed bytes}."""
    res = read_iso_file(ROM, RES)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    iso9660.patch(ROM, out, {RES: ptd.repack(res, repl)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "sora_en.iso"))
    a = ap.parse_args()
    check_rom.check()
    build(a.out, {})
    with open(a.out, "rb") as f:
        print(a.out, hashlib.file_digest(f, "sha1").hexdigest())


if __name__ == "__main__":
    main()
