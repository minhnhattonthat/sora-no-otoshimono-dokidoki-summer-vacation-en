"""Text coverage for textcover.py (PPSSPP has no Lua): a logging breakpoint on the text-box setter logs every string
the game shows, and every SOS script is played from the title by script warp, mashing circle.

    python -X utf8 tools/debug/cover.py strings --out work/qa/cover/strings.tsv   # id -> key list (this build)
    python -X utf8 tools/debug/cover.py run [ISO] --out work/qa/cover [--only SC1/SC10000,..] [--keys circle]
                                        [--jobs 3] [--limit 40000] [--tag p0]
    python -X utf8 tools/debug/cover.py scenes [ISO] --out work/qa/cover/scenes [--only NAME,..]   # scenes.tsv rows
    python -X utf8 $SKILL/scripts/textcover.py work/qa/cover work/qa/cover/strings.tsv --waive docs/text_unshown.tsv

Hook: 0x08817C88(a0 = box index, a1 = string) sets a text box's string (dialogue, help bar, Hexcite reactions);
called once per string. PPSSPPHeadless `-l --loglevel=1` prints `TXT <a1> <string>` per call; each run's
ppsspp.log becomes log.txt with `TEXT <key>` lines. Keys: EBOOT rows by address (a1 is the slot itself), SOS rows by
their built text (build.text_for), since a1 points into a decoded pool buffer. `run` cold-boots once per ISO
(OUT/_base: title state + the save the boot creates), then each script starts from that state and ends when the game
leaves the script scene (5:11) or after --limit frames. A choice needs a direction before circle: the default keys
down,up,circle take the first option, --keys down,circle the second, down,down,circle the third.
"""
import argparse, concurrent.futures as cf, glob, os, re, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import warp  # noqa: E402
from drive import Drive  # noqa: E402

HOOK = 0x08817C88
LOGARGS = ("-l", "--loglevel=1")
ENTRY = re.compile(r"BKP PC=08817c88: TXT ([0-9a-f]{8}) ")
STAMP = re.compile(r"^\d\d:\d\d:\d\d\d |^--debugger")


def rows():
    """[(id, source, built text)] for every script/ row the game can show, in a fixed order."""
    import build, script
    out = []
    for p in sorted(glob.glob(os.path.join(script.SCRIPT, "sos", "*", "*.tsv"))):
        for r in script.read_tsv(p):
            out.append((r["id"], "sos", build.text_for(r, None, {}, "sos")))
    for r in script.read_tsv(os.path.join(script.SCRIPT, "eboot.tsv")):
        out.append((r["id"], "eboot", build.text_for(r, None, {}, "eboot")))
    return out


def keymap():
    """(id -> key, eboot address -> key, built text -> [keys]); key = 0x10000000 + row index (no address clash)."""
    ids, by_addr, by_text = {}, {}, {}
    for i, (rid, src, text) in enumerate(rows()):
        k = 0x10000000 + i
        ids[rid] = k
        if src == "eboot": by_addr[int(rid, 16)] = k
        if text: by_text.setdefault(norm(text), []).append(k)
    return ids, by_addr, by_text


def norm(t): return "\n".join(l.rstrip() for l in t.replace("\r", "").split("\n")).strip()


def entries(log):
    """[(address, text)] from a ppsspp.log with the breakpoint's multi-line TXT entries."""
    out, cur = [], None
    with open(log, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = ENTRY.search(line)
            if m:
                cur = [int(m.group(1), 16), line[m.end():]]; out.append(cur)
            elif cur and not STAMP.match(line):
                cur[1] += line
            else:
                cur = None
    return [(a, norm(t)) for a, t in out]


def convert(log, km):
    """Write log.txt (TEXT <key> per shown string) beside LOG; return (shown keys, unmatched texts)."""
    _, by_addr, by_text = km
    keys, miss = set(), []
    for a, t in entries(log):
        if a in by_addr: keys.add(by_addr[a])
        elif t in by_text: keys.update(by_text[t])
        elif t and t != "/K": miss.append(t)
    with open(os.path.join(os.path.dirname(log), "log.txt"), "w", encoding="utf-8") as f:
        f.writelines(f"TEXT {k:08X}\n" for k in sorted(keys))
        f.writelines(f"# unmatched: {t!r}\n" for t in miss)
    return keys, miss


def hook(D):
    D.r.ws.call("cpu.breakpoint.add", address=HOOK, enabled=False, log=True, logFormat="TXT {a1} {a1:s}")


def prepare(iso, base):
    """Cold boot to the title once: base/title.ppst + base/memstick (the save the boot creates; Communication Mode
    refuses to start without it)."""
    st = os.stat(iso); stamp = f"{st.st_size} {st.st_mtime_ns}"
    tag = os.path.join(base, "iso.txt")
    if os.path.exists(tag) and open(tag).read() == stamp: return
    shutil.rmtree(base, ignore_errors=True)
    D = Drive(iso, base)
    try: warp.boot_to_title(D); D.save(os.path.abspath(os.path.join(base, "title.ppst")))
    finally: D.close()
    open(tag, "w").write(stamp)


def play_script(iso, path, out, keys, limit, base):
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(os.path.join(base, "memstick"), os.path.join(out, "memstick"))
    D = Drive(iso, out, state=os.path.join(base, "title.ppst"), extra=LOGARGS)
    try:
        hook(D)
        warp.start_script(D, path)
        D.until(lambda d: warp.where(d) != warp.SCRIPT, limit, step=200, key=keys, every=10)
        return warp.where(D), D.f
    finally:
        D.close(); shutil.rmtree(os.path.join(out, "memstick"), ignore_errors=True)


def scripts():
    import script
    return sorted(os.path.relpath(p, os.path.join(script.SCRIPT, "sos"))[:-4].replace(os.sep, "/")
                  for p in glob.glob(os.path.join(script.SCRIPT, "sos", "*", "*.tsv")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["strings", "run", "scenes", "convert"])
    ap.add_argument("iso", nargs="?", default="build/sora_en.iso")
    ap.add_argument("--out", default="work/qa/cover"); ap.add_argument("--only")
    ap.add_argument("--keys", default="down,up,circle"); ap.add_argument("--tag", default="p0")
    ap.add_argument("--jobs", type=int, default=3); ap.add_argument("--limit", type=int, default=40000)
    a = ap.parse_args()
    km = keymap()
    if a.cmd == "strings":
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8", newline="") as f:
            f.writelines(f"{rid}\t{k:08X}\n" for rid, k in km[0].items())
        return print(f"{len(km[0])} strings -> {a.out}")
    if a.cmd == "convert":
        for log in glob.glob(os.path.join(a.out, "**", "ppsspp.log"), recursive=True): convert(log, km)
        return
    if a.cmd == "scenes":
        names = a.only.split(",") if a.only else list(warp.load_scenes())
        orig = warp.Drive
        warp.Drive = lambda iso, out, **k: (lambda D: (hook(D), D)[1])(orig(iso, out, extra=LOGARGS, **k))
        for n in names:
            d = os.path.join(a.out, n)
            try: ok, got, _ = warp.warp(a.iso, n, d)
            except (AssertionError, EOFError, RuntimeError) as e: ok, got = False, str(e)
            keys, miss = convert(os.path.join(d, "ppsspp.log"), km)
            print(f"{'ok ' if ok else 'BAD'} {n:24} {got} {len(keys)} strings, {len(miss)} unmatched", flush=True)
        return
    todo = a.only.split(",") if a.only else scripts()
    base = os.path.join(a.out, "_base"); prepare(a.iso, base)

    def one(k):
        t = time.time(); d = os.path.join(a.out, a.tag, k.replace("/", "_"))
        try: got, f = play_script(a.iso, k.lower() + ".sos", d, a.keys, a.limit, base)
        except (AssertionError, EOFError, RuntimeError) as e: got, f = str(e)[:80], 0
        keys, miss = convert(os.path.join(d, "ppsspp.log"), km)
        return f"{k:16} {got} f{f} {len(keys)} strings, {len(miss)} unmatched {time.time() - t:.0f}s"

    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for line in ex.map(one, todo): print(line, flush=True)


if __name__ == "__main__":
    main()
