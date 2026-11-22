"""Shoot a long scene (staff roll) every N frames from a warp row's state: one PNG per step, for sheet.py.

    python -X utf8 tools/debug/roll.py [ISO] --scene credits --out work/qa/gfxshots/roll [--every 300] [--frames 20000]
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warp  # noqa: E402
from drive import Drive  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso", nargs="?", default="build/sora_en.iso")
    ap.add_argument("--scene", default="credits"); ap.add_argument("--out", required=True)
    ap.add_argument("--every", type=int, default=300); ap.add_argument("--frames", type=int, default=20000)
    ap.add_argument("--key", help="tap this key before each step (advance a script: circle)")
    a = ap.parse_args()
    st = os.path.abspath(os.path.join(a.out, "start.ppst"))
    ok, got, _ = warp.warp(a.iso, a.scene, os.path.join(a.out, "_warp"), state_out=st)
    assert ok, f"{a.scene}: {got}"
    D = Drive(a.iso, a.out, state=st)
    try:
        while D.f < a.frames:
            if a.key: D.tap(a.key, after=0)
            D.run(a.every); D.shot(f"f{D.f:06d}.png")
    finally:
        D.close()
    print(f"{a.frames // a.every} shots -> {a.out}")


if __name__ == "__main__":
    main()
