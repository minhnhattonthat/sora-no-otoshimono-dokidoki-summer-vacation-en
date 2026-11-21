"""PPSSPPHeadless driver for this game's debug tools: mash, RAM peek/poke, wait on RAM conditions (no Lua on PSP).

    python -X utf8 tools/debug/drive.py ISO --out DIR [--state S] [--route-str "..."] [--frames N]
        [--mash circle --mash-every 12] [--shot-every N] [--state-every N] [--state-out F] [--dump]

Library: `D = Drive(iso, out, state=...)`, then D.run(frames), D.tap(key), D.mash(key, frames, every),
D.peek(addr, n), D.poke(addr, bytes), D.u32(addr), D.until(pred, limit, step), D.shot(name), D.save(path).
emu.py's --mash is not wired for PSP (psp.py), hence this.
"""
import argparse, base64, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skill import SCRIPTS  # noqa: E402
sys.path.insert(0, SCRIPTS)
import psp  # noqa: E402

ISO = "rom/Sora no Otoshimono - DokiDoki Summer Vacation (Japan).iso"
RAM, RAM_SIZE = 0x08800000, 0x01800000


class Drive:
    def __init__(self, iso, out, state=None, memstick=None):
        self.r = psp.Run(psp.find_emu(None), iso, out, state=state, memstick=memstick)
        self.f = 0; self.out = out; self.nshot = 0

    def run(self, n):
        self.f += n; self.r.run_to(self.f)

    def hold(self, keys, n):
        self.r.press(set(keys)); self.run(n); self.r.press(set())

    def tap(self, key, hold=6, after=20):
        self.hold(key.split("+") if key and key != "-" else [], hold); self.run(after)

    def mash(self, key, frames, every=12, hold=4):
        """Tap KEY every EVERY frames for FRAMES frames; "circle,down" cycles through the keys (choices need a
        direction before circle)."""
        keys = key.split(","); end = self.f + frames
        while self.f < end:
            self.tap(keys[self.i % len(keys)], hold, max(1, every - hold)); self.i += 1

    i = 0

    def peek(self, addr, n): return self.r.ws.mem(addr, n)
    def u32(self, addr): return struct.unpack("<I", self.peek(addr, 4))[0]
    def u16(self, addr): return struct.unpack("<H", self.peek(addr, 2))[0]

    def poke(self, addr, data):
        self.r.ws.call("memory.write", address=addr, base64=base64.b64encode(bytes(data)).decode())

    def poke32(self, addr, v): self.poke(addr, struct.pack("<I", v))

    def until(self, pred, limit, step=10, key=None, every=12):
        """Run (mashing KEY if given) until pred(self) is true; False after LIMIT frames."""
        end = self.f + limit
        while self.f < end:
            if pred(self): return True
            if key: self.mash(key, step, every)
            else: self.run(step)
        return pred(self)

    def shot(self, name=None):
        self.nshot += 1
        return self.r.shot(name or f"f{self.f:06d}.png")

    def save(self, path): self.r.save_state(path)

    def dump(self, path):
        with open(path, "wb") as fh:
            for o in range(0, RAM_SIZE, 0x100000): fh.write(self.peek(RAM + o, 0x100000))

    def close(self): self.r.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso", nargs="?", default=ISO); ap.add_argument("--out", required=True)
    ap.add_argument("--state"); ap.add_argument("--route-str", default="")
    ap.add_argument("--memstick", help="memstick dir to use (and keep), e.g. a play.py SESSION/memstick")
    ap.add_argument("--frames", type=int, default=0); ap.add_argument("--mash")
    ap.add_argument("--mash-every", type=int, default=12); ap.add_argument("--shot-every", type=int, default=0)
    ap.add_argument("--state-every", type=int, default=0); ap.add_argument("--state-out")
    ap.add_argument("--dump", action="store_true", help="write DIR/ram.bin at the end")
    a = ap.parse_args()
    D = Drive(a.iso, a.out, state=a.state, memstick=a.memstick)
    try:
        for n, keys in psp.parse_route(a.route_str) if a.route_str else []:
            D.r.press(keys); D.run(n)
        D.r.press(set())
        start = D.f; nxt_shot = start + a.shot_every; nxt_state = start + a.state_every
        chunk = a.mash_every if a.mash else 30
        while D.f < start + a.frames:
            if a.mash: D.mash(a.mash, chunk, a.mash_every)
            else: D.run(chunk)
            if a.shot_every and D.f >= nxt_shot: D.shot(); nxt_shot += a.shot_every
            if a.state_every and D.f >= nxt_state:
                D.save(os.path.join(a.out, f"s{D.f:06d}.ppst")); nxt_state += a.state_every
        D.shot("final.png")
        print(f"mode {D.u32(0x088FD1D8)} scene {D.u32(0x088FD1D4)}")  # warp.py MODE_ID, SCENE_ID
        if a.state_out: D.save(a.state_out)
        if a.dump: D.dump(os.path.join(a.out, "ram.bin"))
    finally:
        D.close()


if __name__ == "__main__":
    main()
