"""Warp: cold boot, land on a scene by name, shoot it, optionally save a state. See docs/re/debug.md.

    python -X utf8 tools/debug/warp.py [ISO] --scene NAME [--out DIR] [--state-out F] [--frames N]
    python -X utf8 tools/debug/warp.py [ISO] --list
    python -X utf8 tools/debug/warp.py [ISO] --all [--only a,b] [--out work/qa/warp] [--states work/states]

NAME is a row of tools/debug/scenes.tsv, or `sc:<file>` for any script (sc:sc1/sc10000.sos, sc:sc9/sc90010.sos).
scenes.tsv columns: name, base, cheat, route, settle, expect, note.
  base  title            the title menu (after creating the save data a fresh memstick asks for)
        hub              Communication Mode main menu (Level / Card / Hexcite / Menu), via an empty script
        script:<file>    Communication Mode starting at res/script/sc/<file>: the new-game script literal is poked
                         before Communication Mode is chosen, so the game loads that SOS the way it loads the prologue
  cheat comma-separated CHEATS names poked into GAME after the base (unlock = every gallery/dress-up/profile card)
  route emu.py route run from the base ("6 circle;200 -"), then SETTLE idle frames
  expect MODE:SCENE (u32s at MODE_ID / SCENE_ID) asserted before the shot; the state is saved only when it matches
Every base asserts the scene id too, so a warp never shoots a wrong screen silently.
"""
import argparse, csv, os, shutil, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drive import Drive, ISO  # noqa: E402
import psp  # noqa: E402  (drive put the skill's scripts on sys.path)

HERE = os.path.dirname(os.path.abspath(__file__))
SCENE_ID = 0x088FD1D4      # u32 scene within the mode; see docs/re/debug.md
MODE_ID = 0x088FD1D8       # u32 mode: 1 title, 2 logos, 3 free mode, 5 communication mode
START_SCRIPT = 0x088F4974  # "res/script/sc/sc0/sc00000.sos\0" + padding: 32 bytes, the new-game script
TITLE, SCRIPT, TUTORIAL, HUB = (1, 3), (5, 11), (5, 13), (5, 18)
GAME = 0x09EC0000          # game/save state object (scene manager at +0x238); CWCheat codes for this game address
                           # the same object at 0x08EC0000 (real-PSP heap layout), so cheat offsets carry over
CHEATS = {                 # name -> [(offset from GAME, bytes)]; from the 2010 CWCheat "CG CARD GALLERY ALL" code
    "unlock": [(0x3B0, b"\xff\xff\xff\xff"), (0x3B4, b"\x0f"), (0x3D3, b"\x1f"), (0x3D8, b"\x1f"), (0x3DD, b"\xff"),
               (0x3DE, b"\xff\xff"), (0x2E4, b"\xff" * 30 + b"\x00")],
    # Hexcite match (Free Mode; the Communication-mode first match is a guided tutorial that freezes on these):
    # my score u32 +0x774 (COM +0x79C), piece counts u32[7] me +0x82C / COM +0x848 in the order triangle,
    # parallelogram, trapezoid, hexagon, big triangle, big parallelogram, big trapezoid. One hexagon each (the
    # piece selected at the start must stay non-zero or the tray hangs) and 999 points: the match ends after two
    # moves with a win.
    "hexend": [(0x774, (999).to_bytes(4, "little")),
               (0x82C, bytes(12) + b"\x01\0\0\0" + bytes(12)), (0x848, bytes(12) + b"\x01\0\0\0" + bytes(12))],
    # Communication mode (scene manager SM = GAME+0x23C; docs/re/debug.md): SM+0xAA bit 0 = Hexcite tutorial seen,
    # so the hub's Hexcite starts a real match (opponent select 5:68) instead of the guided tutorial
    "hexdone": [(0x2E6, b"\x01")],
    "params": [(o, (20).to_bytes(4, "little")) for o in (0x27C, 0x294, 0x2AC, 0x2C4)],  # 4 params = chapter targets
    "lastchapter": [(0x27A, b"\x03\x00")],   # SM+0x3E chapter index 3: the chapter end runs ending sc90010
    "noturns": [(0x278, b"\x14\x00")],       # SM+0x3C turns used = 20 of 20: params short -> bad ending sc90020
    "lastturn": [(0x278, b"\x13\x00")],      # 19 of 20: the next real turn ends the chapter by itself (no overlay)
    # scene request SM+8 = 0x2D (chapter-end check); at the hub the main loop switches to it. Poke it last.
    "chapterend": [(0x244, b"\x2d\0\0\0")],
    # stress: Free Mode records (u16 per opponent: wins from +0x6F4 (Sohara +0x6F6), win streak Sohara +0x744; losses
    # and draws between) all 999; the opponent select caps them at 999 W / 999 L / 99 D / 99 streak
    "recmax": [(0x6F4, (999).to_bytes(2, "little") * 54)],
}
# Nymph's Card-submenu comment (table 0x088C07B4 + 0x100*N, picked by 0x0882CA78 from hand/params/visits): code poke
# of its `move a2, s4` (0x0882CBD0) -> `addiu a2, zero, N`, so entering Card shows comment N (text coverage)
CHEATS.update({f"comment{n}": [(0x0882CBD0 - GAME, (0x24060000 | n).to_bytes(4, "little"))] for n in range(8)})
# Hexcite post-match reaction: 98 records of 0xC4 at 0x088DCA8C (u32 result key, voice, text at +0x44; 7 characters
# x 2 variants x 7 results), record offset picked by `mflo s0` at 0x08845184 -> `addiu s0, zero, N*0xC4`
CHEATS.update({f"react{n}": [(0x08845184 - GAME, (0x24100000 | n * 0xC4).to_bytes(4, "little"))] for n in range(98)})


def cheat(D, names):
    for n in filter(None, names.split(",")):
        for off, data in CHEATS[n]: D.poke(GAME + off, data)


def where(D): return D.u32(MODE_ID), D.u32(SCENE_ID)


def wait_for(D, ms, limit, what):
    assert D.until(lambda d: where(d) == ms, limit, step=30), f"{what} not reached (mode:scene {where(D)})"


def boot_to_title(D):
    """Cold boot with an empty memstick: accept 'create save data', save, close the dialog, OK the autosave notice,
    then wait for the title menu."""
    D.run(2000); D.tap("circle", after=300)   # "no save data, create?" -> Yes
    D.tap("circle", after=400)                # "save this data?" -> Yes
    D.tap("cross", after=300)                 # "save completed" -> Back
    D.tap("circle", after=60)                 # autosave notice -> OK
    wait_for(D, TITLE, 3000, "title")
    D.run(700)                                # title menu fade-in (logo, card, menu)


def start_script(D, path):
    """From the title: make Communication Mode -> new game run res/script/sc/PATH instead of the prologue."""
    s = f"res/script/sc/{path}".encode() + b"\0"
    assert len(s) <= 32, path
    D.poke(START_SCRIPT, s.ljust(32, b"\0"))
    D.tap("circle", after=30)
    wait_for(D, SCRIPT, 1200, "script")


def to_hub(D):
    """Title -> empty script (sc_end) -> the 6-page tutorial that follows a new game -> 'read again?' No -> hub."""
    start_script(D, "sc_end.sos")
    wait_for(D, TUTORIAL, 3000, "tutorial")
    D.run(200)
    for _ in range(6): D.tap("circle", after=200)
    D.tap("right", after=30); D.tap("circle", after=30)
    wait_for(D, HUB, 3000, "hub")
    D.run(300)


def run_route(D, route):
    """emu.py route steps; a `cheat:NAME` step pokes CHEATS[NAME] at that point (for state that only exists
    mid-route, such as a Hexcite match); `until:M:S:LIMIT[:KEYS]` runs (tapping the comma-separated KEYS in turn,
    one every 20 frames) until mode:scene is M:S, and fails the warp if LIMIT frames pass first; `shot[:NAME]` takes
    an extra screenshot (multi-page screens: tutorials, credits)."""
    for step in route.split(";"):
        step = step.strip()
        if step.startswith("cheat:"):
            cheat(D, step[6:]); continue
        if step.startswith("shot"):   # shot or shot:NAME, an extra screenshot mid-route
            D.shot(f"{step[5:] or 'f%06d' % D.f}.png"); continue
        if step.startswith("until:"):
            m, s, limit, *keys = step[6:].split(":")
            ok = D.until(lambda d: where(d) == (int(m), int(s)), int(limit), step=20,
                         key=keys[0] if keys else None, every=20)
            assert ok, f"{step}: at {where(D)}"
            continue
        for n, keys in psp.parse_route(step):
            D.r.press(keys); D.run(n)
    D.r.press(set())


def load_scenes():
    with open(os.path.join(HERE, "scenes.tsv"), encoding="utf-8", newline="") as f:
        rows = [r + [""] * (7 - len(r)) for r in csv.reader(f, delimiter="\t") if r and not r[0].startswith("#")]
    return {r[0]: r for r in rows[1:]}


def warp(iso, name, out, state_out=None, frames=None, scenes=None):
    row = [name, "script:" + name[3:], "", "", "400", "5:11", ""] if name.startswith("sc:") else (scenes or load_scenes())[name]
    _, base, cheats, route, settle, expect = row[:6]
    # a save left by an earlier run (credits, game over) turns Communication Mode's New game into Continue
    shutil.rmtree(os.path.join(out, "memstick"), ignore_errors=True)
    D = Drive(iso, out)
    try:
        boot_to_title(D)
        if base == "hub": to_hub(D)
        elif base.startswith("script:"): start_script(D, base[7:])
        elif base != "title": raise SystemExit(f"{name}: unknown base {base!r}")
        cheat(D, cheats)
        if route: run_route(D, route)
        D.run(int(frames or settle or 300))
        got = where(D)
        ok = not expect or got == tuple(int(x) for x in expect.split(":"))
        shot = D.shot(f"{name.replace(':', '_').replace('/', '_')}.png")
        if state_out and ok: D.save(state_out)
        return ok, got, shot
    finally:
        D.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso", nargs="?", default=ISO)
    ap.add_argument("--scene"); ap.add_argument("--list", action="store_true"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--only", help="with --all: comma-separated names")
    ap.add_argument("--out", default="work/qa/warp"); ap.add_argument("--state-out")
    ap.add_argument("--states", default="work/states"); ap.add_argument("--frames", type=int)
    a = ap.parse_args()
    scenes = load_scenes()
    if a.list:
        for n, r in scenes.items(): print(f"{n:24} {r[1]:24} {r[6]}")
        return
    names = (a.only.split(",") if a.only else list(scenes)) if a.all else [a.scene]
    if not names[0]: ap.error("--scene, --list or --all")
    bad = 0
    for n in names:
        t = time.time()
        st = os.path.join(a.states, n.replace(":", "_").replace("/", "_") + ".ppst") if a.all else a.state_out
        try:
            ok, got, shot = warp(a.iso, n, os.path.join(a.out, n.replace(":", "_").replace("/", "_")), st, a.frames, scenes)
        except (AssertionError, EOFError, RuntimeError) as e:
            ok, got, shot = False, None, str(e)
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {n:24} {got} {shot}  {time.time() - t:.0f}s" + (f"  state {st}" if st and ok else ""),
              flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
