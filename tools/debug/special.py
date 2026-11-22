"""Shoot a Hexcite special-move cut-in from a match state: re-arm the special, press square, answer Yes, shoot.

    python -X utf8 tools/debug/special.py [ISO] --state S --out DIR [--frames 900] [--sp N] [--dump]

Square in a match (0x088475A4) opens "Use a special move?" only while SM+0x6F8 (GAME+0x934) == 0: the game sets it
to -1 until the player takes a wing mark (docs/re/debug.md). The cut-in plays for ~450 frames after Yes, then the
special's effect; shots every 2 frames: DIR/f*.png, plus ask.png / ask_yes.png. States: warp.py rows free_match
(Ikaros), free_match_sohara, free_match_tomoki with --state-out. --sp N also pokes the player's special id
(SP_ID below) before square, to reach Nymph / Mikako / Sugata, who are not Free Mode players. --dump prints the
SM words that differ between this state and --state2 (finding SP_ID).
"""
import argparse, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warp  # noqa: E402
from drive import Drive  # noqa: E402

ARM = warp.GAME + 0x934          # SM+0x6F8: 0 = special ready, -1 = no wing mark yet / used
SP_ID = warp.GAME + 0x928        # SM+0x6EC: my special = character id (GAME+0x818: Ikaros 0, Sohara 1, Tomoki 5)


def run(iso, st, out, frames, sp=None):
    D = Drive(iso, out, state=st)
    try:
        D.poke(ARM, bytes(4))
        if sp is not None: D.poke(SP_ID, struct.pack("<I", sp))
        D.run(2); D.hold({"square"}, 6); D.run(60); D.shot("ask.png")
        D.hold({"left"}, 6); D.run(20); D.shot("ask_yes.png"); D.hold({"circle"}, 6)
        for _ in range(frames // 2):
            D.run(2); D.shot(f"f{D.f:05d}.png")
    finally:
        D.close()


def dump(iso, a, b, out):
    snaps = []
    for st in (a, b):
        D = Drive(iso, out, state=st)
        try: snaps.append(D.peek(warp.GAME, 0x2000))
        finally: D.close()
    for off in range(0x23C, 0x2000, 4):
        x, y = (struct.unpack_from("<i", s, off)[0] for s in snaps)
        if x != y and -2 <= x < 64 and -2 <= y < 64: print(hex(off), x, y)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso", nargs="?", default="build/sora_en.iso")
    ap.add_argument("--state", required=True); ap.add_argument("--state2")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", type=int, default=900); ap.add_argument("--sp", type=int)
    ap.add_argument("--dump", action="store_true")
    a = ap.parse_args()
    if a.dump: dump(a.iso, a.state, a.state2, a.out)
    else: run(a.iso, os.path.abspath(a.state), a.out, a.frames, a.sp)


if __name__ == "__main__":
    main()
