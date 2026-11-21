"""Re-sign a patched EBOOT ELF into a ~PSP EBOOT.BIN (real PSP / Vita need it; PPSSPP alone boots a plain ELF).

    python -X utf8 tools/sign.py IN.elf OUT.bin

Uses sign_np -elf (github.com/swarzesherz/sign_np @ ac77d56, GPLv3, source in tools/sign_np/src) built for Linux and
run through WSL. Build it once:  wsl -e sh -c "cd tools/sign_np/src && gcc -O2 -w -I./libkirk -o ../sign_np *.c libkirk/*.c -lz"
Tag 4 = 0xD91612F0, the tag of the original EBOOT (docs/re/script.md §EBOOT).
"""
import os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = "tools/sign_np/sign_np"
TAG = 4
ELF_SIZE = 1430652  # the dump (work/eboot.elf) carries decrypt-buffer junk after the real ELF; ~PSP header +0x28


def sign(elf):
    assert elf[:4] == b"\x7fELF", "not an ELF"
    tmp = os.path.join(ROOT, "work", "sign")
    os.makedirs(tmp, exist_ok=True)
    with open(os.path.join(tmp, "in.elf"), "wb") as f:
        f.write(elf)
    out = os.path.join(tmp, "out.bin")
    if os.path.exists(out):
        os.remove(out)
    assert os.path.exists(os.path.join(ROOT, BIN)), f"{BIN} missing: build it (see tools/sign.py docstring)"
    r = subprocess.run(["wsl", "-e", BIN, "-elf", "work/sign/in.elf", "work/sign/out.bin", str(TAG)],
                       cwd=ROOT, capture_output=True)
    assert r.returncode == 0 and os.path.exists(out), r.stdout.decode(errors="replace")[-500:]
    d = open(out, "rb").read()
    assert d[:4] == b"~PSP" and struct.unpack_from("<I", d, 0xD0)[0] == 0xD91612F0, "sign_np output not ~PSP"
    return d


if __name__ == "__main__":
    with open(sys.argv[2], "wb") as f:
        f.write(sign(open(sys.argv[1], "rb").read()))
