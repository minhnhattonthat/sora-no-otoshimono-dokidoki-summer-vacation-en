"""Boot an ISO in PPSSPPHeadless, run to a frame, dump user RAM + module list (RE helper; see docs/re/README.md).

    python -X utf8 tools/pspdbg.py ISO --out DIR [--frames N] [--state F] [--route-str "..."] [--dump-eboot]

Writes DIR/ram.bin (0x08800000..0x0a000000), DIR/modules.json. --dump-eboot sets DumpFileTypes=7 in the run's
memstick ppsspp.ini so PPSSPP writes the decrypted EBOOT to memstick/PSP/SYSTEM/DUMP/.
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill import SCRIPTS  # noqa: E402
sys.path.insert(0, SCRIPTS)
import psp  # noqa: E402

RAM, RAM_SIZE = 0x08800000, 0x01800000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso"); ap.add_argument("--out", required=True)
    ap.add_argument("--frames", type=int, default=600); ap.add_argument("--state")
    ap.add_argument("--route-str", default=""); ap.add_argument("--dump-eboot", action="store_true")
    ap.add_argument("--save-state")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ms = os.path.join(a.out, "memstick")
    if a.dump_eboot:
        os.makedirs(os.path.join(ms, "PSP", "SYSTEM"), exist_ok=True)
        open(os.path.join(ms, "PSP", "SYSTEM", "ppsspp.ini"), "w").write("[General]\nDumpFileTypes = 7\n")
    r = psp.Run(psp.find_emu(None), a.iso, a.out, state=a.state, memstick=ms)
    try:
        t = 0
        for step in psp.parse_route(a.route_str) if a.route_str else []:
            frames, keys = step
            r.press(keys); t += frames; r.run_to(t)
        r.press(set()); r.run_to(max(t, a.frames))
        with open(os.path.join(a.out, "ram.bin"), "wb") as f:
            for o in range(0, RAM_SIZE, 0x100000):
                f.write(r.ws.mem(RAM + o, 0x100000))
        mods = r.ws.call("hle.module.list")
        json.dump(mods, open(os.path.join(a.out, "modules.json"), "w"), indent=1)
        r.shot("final.png")
        if a.save_state: r.save_state(a.save_state)
    finally:
        r.close()


if __name__ == "__main__":
    main()
