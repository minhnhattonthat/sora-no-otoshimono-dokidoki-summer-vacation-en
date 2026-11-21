"""Save editor: the save file is encrypted, so edit the plaintext game-state object (GAME) in RAM at the hub and let
the game write the save itself (Menu -> Save). See docs/re/debug.md.

    python -X utf8 tools/debug/save.py make NAME [--cheat unlock] [--poke OFF:HEX ...] [--out work/saves]
    python -X utf8 tools/debug/save.py check NAME [--out work/saves] [--route "6 circle;200 -;6 down;40 -;6 circle"]

make   cold boot -> hub, poke GAME, Menu -> Save -> Yes, keep the written folder in OUT/NAME/ULJM05639SoraOto
       (seed a run with `emu.py --sav OUT/NAME/ULJM05639SoraOto` or Drive(memstick=...)).
check  boot with that save: autosave notice -> title -> Communication Mode -> Continue; asserts the hub (5:18) is
       reached (a corrupted save never gets there) and shoots it to OUT/NAME/check/hub.png.
OFF is a hex offset from GAME (0x09EC0000), HEX the bytes to write there (little-endian for numbers).
"""
import argparse, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drive import Drive, ISO  # noqa: E402
from warp import GAME, HUB, TITLE, boot_to_title, cheat, run_route, to_hub, wait_for, where  # noqa: E402
import psp  # noqa: E402

SAVE_DIR = "ULJM05639SoraOto"
# hub -> Menu -> Save ("save data so far?" Yes) -> system dialog Yes (left first: overwriting the save the boot
# created, PPSSPP's dialog starts on No; Yes/No sit side by side) -> "completed" Back; the autosave notice follows
HUB_SAVE = ("120 -;6 down;40 -;6 down;40 -;6 circle;300 -;6 down;60 -;6 circle;100 -;6 left;30 -;6 circle;200 -;"
            "6 left;30 -;6 circle;400 -;6 cross;300 -")
MENU = (5, 38)       # hub -> Menu (Options / Save / Controls / Title)


def make(iso, name, out, cheats="", pokes=()):
    dest = os.path.join(out, name)
    shutil.rmtree(dest, ignore_errors=True)
    D = Drive(iso, os.path.join(dest, "make"))
    try:
        boot_to_title(D); to_hub(D)
        cheat(D, cheats)
        for p in pokes:
            off, hx = p.split(":"); D.poke(GAME + int(off, 16), bytes.fromhex(hx))
        run_route(D, HUB_SAVE)
        D.shot("saving.png")
        # the dialogs (scene 5:93) close at varying times: circle away the autosave notice until the Menu (or the hub,
        # if the route's cross already backed out) is back, then back out to the hub
        assert D.until(lambda d: where(d) in (MENU, HUB), 900, step=60, key="circle", every=60), where(D)
        if where(D) == MENU: D.tap("cross", after=200)
        wait_for(D, HUB, 600, "hub after saving")
        D.shot("saved.png")
    finally:
        D.close()
    shutil.copytree(os.path.join(dest, "make", "memstick", "PSP", "SAVEDATA", SAVE_DIR), os.path.join(dest, SAVE_DIR))
    return os.path.join(dest, SAVE_DIR)


def check(iso, name, out, route=""):
    dest = os.path.join(out, name)
    run = os.path.join(dest, "check")
    shutil.rmtree(run, ignore_errors=True)
    ms = os.path.join(run, "memstick")
    psp.seed_saves(ms, os.path.join(dest, SAVE_DIR))
    D = Drive(iso, run, memstick=ms)
    try:
        D.run(300); D.tap("circle", after=60)       # save loads silently, then the autosave notice
        wait_for(D, TITLE, 3000, "title")
        D.run(700)
        D.tap("circle", after=100)                  # Communication Mode -> New game / Continue
        D.tap("circle", after=30)                   # cursor starts on Continue when a save has progress
        wait_for(D, HUB, 3000, "hub from the save")
        D.run(300); D.shot("hub.png")
        if route: run_route(D, route); D.run(300)
        return where(D), D.shot("route.png" if route else "hub.png")
    finally:
        D.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("make", "check")); ap.add_argument("name")
    ap.add_argument("--iso", default=ISO); ap.add_argument("--out", default="work/saves")
    ap.add_argument("--cheat", default=""); ap.add_argument("--poke", action="append", default=[])
    ap.add_argument("--route", default="", help="check: route run from the loaded hub, shot to check/route.png")
    a = ap.parse_args()
    if a.cmd == "make":
        print("saved", make(a.iso, a.name, a.out, a.cheat, a.poke))
    else:
        got, shot = check(a.iso, a.name, a.out, a.route)
        print("ok", got, shot)


if __name__ == "__main__":
    main()
