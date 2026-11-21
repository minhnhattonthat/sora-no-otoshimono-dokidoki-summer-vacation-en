"""MIPS lookups in the EBOOT RAM image (work/dbg/eboot_mem.bin, module base 0x08804000; docs/re/debug.md).

    python -X utf8 tools/debug/mips.py dis START END        disassemble
    python -X utf8 tools/debug/mips.py calls TARGET         jal TARGET sites, with the a1/a2/a3 set just before
    python -X utf8 tools/debug/mips.py xref ADDR [ADDR..]   lui+addiu/ori/load/store pairs building ADDR, raw pointers
    python -X utf8 tools/debug/mips.py case ADDR            which mode-5 scene case (jump table 0x088C928C) holds ADDR
Run it with -I (not from a dir holding a dis.py: capstone imports the stdlib dis).
"""
import argparse, struct
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

BASE, TABLE, NCASES = 0x08804000, 0x088C928C, 101
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN); md.skipdata = True


def load(path):
    d = open(path, "rb").read()
    return d, struct.unpack_from(f"<{len(d) // 4}I", d)


def dis(d, a, b):
    for i in md.disasm(d[a - BASE:b - BASE], a): print(f"{i.address:08X} {i.mnemonic:8} {i.op_str}")


def calls(d, W, t):
    w = 0x0C000000 | ((t >> 2) & 0x3FFFFFF)
    for o, x in enumerate(W):
        if x != w: continue
        a = BASE + 4 * o; regs = {}
        for i in md.disasm(d[4 * o - 40:4 * o + 8], a - 40):
            op = i.op_str.split(", ")
            if op[0] in ("$a1", "$a2", "$a3"): regs[op[0]] = f"{i.mnemonic} {i.op_str}"
        print(f"{a:08X} " + " | ".join(regs[k] for k in sorted(regs)))


def xref(W, targets):
    for i, w in enumerate(W):
        if w in targets: print(f"ptr  {BASE + 4 * i:08X} -> {w:08X}")
        if w >> 26 != 0x0F: continue  # lui
        rt, hi = (w >> 16) & 31, (w & 0xFFFF) << 16
        for j in range(i + 1, min(i + 12, len(W))):
            v = W[j]; op = v >> 26
            if (v >> 21) & 31 != rt or op not in (0x09, 0x0D, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B): continue
            imm = v & 0xFFFF
            val = (hi | imm) if op == 0x0D else (hi + (imm - 0x10000 if imm & 0x8000 else imm)) & 0xFFFFFFFF
            if val in targets: print(f"code {BASE + 4 * j:08X} -> {val:08X}")


def case(d, a):
    t = struct.unpack_from(f"<{NCASES}I", d, TABLE - BASE)
    best = max(w for w in t if w <= a)
    print(f"{a:08X} in case(s) {[i for i, w in enumerate(t) if w == best]} starting {best:08X}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("dis", "calls", "xref", "case")); ap.add_argument("addr", nargs="+")
    ap.add_argument("--image", default="work/dbg/eboot_mem.bin")
    a = ap.parse_args()
    d, W = load(a.image); ad = [int(x, 16) for x in a.addr]
    if a.cmd == "dis": dis(d, ad[0], ad[1] if len(ad) > 1 else ad[0] + 0x80)
    elif a.cmd == "calls": [calls(d, W, t) for t in ad]
    elif a.cmd == "xref": xref(W, set(ad))
    else: [case(d, x) for x in ad]


if __name__ == "__main__":
    main()
