"""Shoot the Hexcite result word (Big Win!!, Win!, Narrow Win, Draw, Lose!, Crushed!!) for forced final scores.

    python -X utf8 tools/debug/hexresult.py [ISO] --state S --out work/qa/gfxshots/hexresult [--only big,draw]

--state: a Hexcite match in progress from the same ISO: the free_match state `cover.py reactions` makes
(work/qa/cover/reactions/free_match.ppst, the default) or `warp.py --scene comm_match --state-out F` (Communication).
Cheat hexend (one hexagon each), then the free_win mash (placing both hexagons) for --frames frames with my/COM scores
(GAME+0x774 / +0x79C) re-poked every 2 frames and a shot every 2 frames: OUT/<case>/f*.png. The word shows for
only a few frames (~f600, with the stars). Only Big Win!! is ever drawn: Win!/Narrow Win (stars, no word), Draw and
the losses (blue fade, no word) draw nothing in Free Mode even with the word index forced (--cat), and the original
ISO does the same; Communication mode shows no word at all (Finish! -> Winner/Loser panels).
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warp  # noqa: E402
from drive import Drive  # noqa: E402

# result word = SM+0x4A0 (GAME+0x6DC), set once at the match end from my - COM (table 0x088E1980: >=50 0 Big Win!!,
# 15..49 1 Win!, 1..14 2 Narrow Win, 0 3 Draw, -49..-1 4 Lose!, <=-50 5 Crushed!!) and read by the word state
# (0x08845A74, file table 0x088FEC0C). --cat re-pokes it as well, in case the scores alone don't stick.
CASES = {"big": (300, 0), "win": (300, 270), "narrow": (300, 290), "draw": (300, 300), "lose": (290, 300),
         "crushed": (0, 300)}
CAT = {"big": 0, "win": 1, "narrow": 2, "draw": 3, "lose": 4, "crushed": 5}
KEYS = "circle,right,circle,up,circle,left,circle,down".split(",")   # the free_win placing mash


def run(iso, st, out, me, com, frames, cat=None):
    D = Drive(iso, out, state=st)
    try:
        warp.cheat(D, "hexend")
        for i in range(frames // 20):
            D.r.press({KEYS[i % len(KEYS)]})
            for j in range(10):
                if j == 3: D.r.press(set())
                D.poke(warp.GAME + 0x774, me.to_bytes(4, "little")); D.poke(warp.GAME + 0x79C, com.to_bytes(4, "little"))
                if cat is not None: D.poke(warp.GAME + 0x6DC, cat.to_bytes(4, "little"))
                D.run(2); D.shot(f"f{D.f:06d}.png")
    finally:
        D.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso", nargs="?", default="build/sora_en.iso")
    ap.add_argument("--state", default="work/qa/cover/reactions/free_match.ppst")
    ap.add_argument("--out", required=True); ap.add_argument("--only")
    ap.add_argument("--frames", type=int, default=900)
    ap.add_argument("--cat", action="store_true", help="also poke the result-word index (GAME+0x6DC) every 2 frames")
    a = ap.parse_args()
    for name in (a.only.split(",") if a.only else CASES):
        me, com = CASES[name]
        run(a.iso, os.path.abspath(a.state), os.path.join(a.out, name), me, com, a.frames, CAT[name] if a.cat else None)
        print(name, "done", flush=True)


if __name__ == "__main__":
    main()
