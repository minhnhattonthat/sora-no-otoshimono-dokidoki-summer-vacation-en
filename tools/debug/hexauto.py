"""Hexcite auto-player: places pieces by poking the held piece's position until the placement outline shows.

    python -X utf8 tools/debug/hexauto.py ISO --state S --out DIR [--turns N] [--tutorial] [--me 7 counts --com 7 counts]

Each turn: circle grabs the selected tray piece, then every rotation (R) x position (GAME+0x511C x, +0x5118 y, u16
screen px; x steps 10.5 = one triangle column, y 20 = one row; the d-pad only moves x by 2 columns, which is why the
guided tutorial's 3rd target is unreachable by hand) is poked until red/green outline pixels show, then circle.
--tutorial: the guided steps refuse every spot but the yellow target, so circle at each valid spot until my score
(GAME+0x774) changes, and on a miss drop the piece (cross) and try the next tray piece. Saves DIR/tNN.ppst per turn and
shoots every 30 frames between turns. docs/re/debug.md §Hexcite tutorial.
"""
import argparse, os, struct, sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drive import Drive  # noqa: E402

GAME = 0x09EC0000


def valid(D, out):
    p = os.path.join(out, "_probe.png")
    D.shot("_probe.png")
    a = np.asarray(Image.open(p).convert("RGB"), int)[20:215, 120:360]
    os.remove(p)
    red = ((a[..., 0] > 220) & (a[..., 1] < 70) & (a[..., 2] < 70)).sum()
    grn = ((a[..., 1] > 220) & (a[..., 0] < 90) & (a[..., 2] < 90)).sum()
    return red + grn > 40


def place(D, out, tutorial):
    score = D.u32(GAME + 0x774)
    D.tap("circle", hold=4, after=30)
    for _ in range(6):
        for y in range(19, 240, 20):
            for k in range(-9, 10):
                D.poke(GAME + 0x511C, round(241 + 10.5 * k).to_bytes(2, "little"))
                D.poke(GAME + 0x5118, y.to_bytes(2, "little"))
                D.run(2)
                if valid(D, out):
                    D.tap("circle", hold=4, after=10)
                    if not tutorial:
                        return True
                    D.run(120)
                    if D.u32(GAME + 0x774) != score:
                        return True
        D.tap("rtrigger", hold=4, after=10)
    D.tap("cross", hold=4, after=20)
    D.tap("right", hold=4, after=20)
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso")
    ap.add_argument("--state", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--turns", type=int, default=1)
    ap.add_argument("--tutorial", action="store_true")
    ap.add_argument("--me"), ap.add_argument("--com")
    ap.add_argument("--then-me", help="my 7 piece counts poked right after each placement (COM's turn): all 0 makes "
                    "me pass at my next turn while COM still has pieces")
    a = ap.parse_args()
    D = Drive(a.iso, a.out, state=a.state)
    D.run(5)
    for off, v in ((0x82C, a.me), (0x848, a.com)):
        if v:
            D.poke(GAME + off, struct.pack("<7I", *map(int, v.split(","))))
    for t in range(a.turns):
        ok = place(D, a.out, a.tutorial)
        if ok and a.then_me:
            D.poke(GAME + 0x82C, struct.pack("<7I", *map(int, a.then_me.split(","))))
        print("turn", t, "placed" if ok else "none", "frame", D.f, "score", D.u32(GAME + 0x774), flush=True)
        for _ in range(15):
            D.run(30)
            D.shot()
        D.save(os.path.join(a.out, f"t{t:02d}.ppst"))
    D.close()


if __name__ == "__main__":
    main()
