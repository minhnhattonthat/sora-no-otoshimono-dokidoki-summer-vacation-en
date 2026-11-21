"""Decrypted EBOOT ELF (PPSSPP DumpFileTypes=7 dump, work/eboot.elf): segment map and Japanese string scan.

    python -X utf8 tools/eboot.py [work/eboot.elf]      print every NUL-delimited Japanese string: RAM addr, enc, text

The ELF is a relocatable PRX loaded at 0x08804000; RAM = BASE + vaddr. A string is a run between NULs that decodes
fully as Shift-JIS (cp932) or UTF-8, has no control byte but \\n, and holds at least one non-ASCII character.
"""
import struct, sys

BASE = 0x08804000


def sections(d):
    """{name: (file_off, vaddr, size)} from the section headers."""
    shoff, = struct.unpack_from("<I", d, 0x20)
    n, si = struct.unpack_from("<2H", d, 0x30)
    secs = [struct.unpack_from("<10I", d, shoff + 40 * i) for i in range(n)]
    names = secs[si][4]
    return {d[names + s[0]:d.index(b"\0", names + s[0])].decode(): (s[4], s[3], s[5]) for s in secs}


DATA = (".rodata", ".rodata.0001", ".data")  # .text hits are instruction bytes that happen to decode


def segments(d):
    """[(file_off, vaddr, filesz)] of the PT_LOAD segments."""
    phoff, = struct.unpack_from("<I", d, 0x1C)
    n, = struct.unpack_from("<H", d, 0x2C)
    out = []
    for i in range(n):
        typ, off, va, _, fsz = struct.unpack_from("<5I", d, phoff + 32 * i)
        if typ == 1:
            out.append((off, va, fsz))
    return out


def ram2off(d, addr):
    v = addr - BASE
    for off, va, fsz in segments(d):
        if va <= v < va + fsz:
            return off + v - va
    raise ValueError(hex(addr))


def off2ram(d, o):
    for off, va, fsz in segments(d):
        if off <= o < off + fsz:
            return BASE + va + o - off
    raise ValueError(hex(o))


def decode(b):
    """(enc, text) or None. UTF-8 first: a valid multi-byte UTF-8 run is almost never valid-looking SJIS text."""
    if any(c < 0x20 and c != 0x0A for c in b) or all(c < 0x80 for c in b):
        return None
    for enc in ("utf-8", "cp932"):
        try:
            t = b.decode(enc)
        except UnicodeDecodeError:
            continue
        jp = [c for c in t if ord(c) >= 0x80]
        if len(jp) >= 2 and all(isjp(c) for c in jp):
            return enc, t
        return None  # pointer/float bytes that happen to decode
    return None


def isjp(c):
    """Characters the game's text uses; anything else in a hit means binary noise."""
    o = ord(c)
    return (0x3000 <= o <= 0x30FF or 0x4E00 <= o <= 0x9FFF or 0xFF01 <= o <= 0xFF5E
            or c in "…‥―－～“”‘’♪☆★○●◎△▲▽▼□■◇◆→←↑↓×÷±・゛゜〜々〇♥")


def scan(d):
    """[(file_off, enc, raw bytes, text)] for every NUL-delimited Japanese run in the data sections."""
    hits = []
    secs = sections(d)
    for off, _, fsz in (secs[n] for n in DATA):
        o, end = off, off + fsz
        while o < end:
            e = d.index(b"\0", o, end + 1) if b"\0" in d[o:end] else end
            r = decode(d[o:e]) if e > o else None
            if r:
                hits.append((o, r[0], d[o:e], r[1]))
            o = e + 1
    return hits


if __name__ == "__main__":
    d = open(sys.argv[1] if len(sys.argv) > 1 else "work/eboot.elf", "rb").read()
    for o, enc, _, t in scan(d):
        print(f"{off2ram(d, o):#x}\t{enc}\t{t!r}")
