"""Dump the decrypted EBOOT ELF to work/eboot.elf with the repo's PPSSPP (tools/ppsspp), checked against eboot.sha1.

    python -X utf8 tools/dump_eboot.py

PPSSPPHeadless ignores ppsspp.ini, so this runs the GUI build with DumpFileTypes = 7, waits for
memstick/PSP/SYSTEM/DUMP/ULJM05639_EBOOT.BIN, kills it and sets the option back to 0.
"""
import hashlib, os, shutil, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build  # noqa: E402

EMU = os.path.join(ROOT, "tools", "ppsspp")
SYS = os.path.join(EMU, "memstick", "PSP", "SYSTEM")
DUMP = os.path.join(SYS, "DUMP", "ULJM05639_EBOOT.BIN")
OUT = os.path.join(ROOT, "work", "eboot.elf")


def main():
    os.makedirs(SYS, exist_ok=True)
    ini = os.path.join(SYS, "ppsspp.ini")
    open(ini, "w").write("[General]\nDumpFileTypes = 7\n")
    if os.path.exists(DUMP):
        os.remove(DUMP)
    p = subprocess.Popen([os.path.join(EMU, "PPSSPPWindows64.exe"), os.path.abspath(build.ROM)])
    try:
        for _ in range(120):
            time.sleep(0.5)
            if os.path.exists(DUMP) and os.path.getsize(DUMP) > 0x100000:
                time.sleep(1)  # let the write finish
                break
        else:
            sys.exit("no dump after 60 s")
    finally:
        p.kill()
        open(ini, "w").write("[General]\nDumpFileTypes = 0\n")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    shutil.copyfile(DUMP, OUT)
    got = hashlib.sha1(open(OUT, "rb").read()).hexdigest()
    want = open(os.path.join(ROOT, "eboot.sha1")).read().split()[0]
    print(OUT, got, "ok" if got == want else f"MISMATCH (want {want})")
    sys.exit(got != want)


if __name__ == "__main__":
    main()
