"""Variable-width one-byte characters: EBOOT patch (docs/re/script.md §VWF).

The engine advances every one-byte (ASCII) character by size/2 = 9 px in two places: the layout pass that measures
lines for auto-wrap (0x08817E64, line width u16 += size*scale>>1) and the draw loop (0x08818B50, x += size*scale>>1;
x is 1/16 px, scale 16 = 1.0). Both now call HELPER, which returns WIDTHS[code] (px at size 18; tools/font.py), and
add px*scale instead. HELPER + the 256-byte table overwrite CRI ADX error messages (printed only on a middleware
error). The EBOOT is a relocatable PRX: the two new `jal`s and HELPER's lui/lbu pair get new relocation entries,
appended to the last relocation block (its section and the 0x700000A0 segment both grow), so the code still works
wherever the module loads.

    apply(elf_bytes, widths) -> new elf bytes
"""
import struct

BASE = 0x08804000
HELPER = 0x088EA3A0  # 16 bytes of code, then TABLE (256 bytes): "E2007011601 : The size of work area..." onwards
TABLE = HELPER + 0x10
CAVE_END = TABLE + 0x100
LAYOUT, DRAW = 0x08817E64, 0x08818B50
ZERO, V0, V1, A0, A1, A2, S3, SP, RA = 0, 2, 3, 4, 5, 6, 19, 29, 31
R_26, R_HI16, R_LO16 = 4, 5, 6


def i_mem(op, rt, off, rs):
    return op << 26 | rs << 21 | rt << 16 | off & 0xFFFF


def lw(rt, off, rs): return i_mem(0x23, rt, off, rs)
def lh(rt, off, rs): return i_mem(0x21, rt, off, rs)
def lhu(rt, off, rs): return i_mem(0x25, rt, off, rs)
def lbu(rt, off, rs): return i_mem(0x24, rt, off, rs)
def lui(rt, imm): return 0x0F << 26 | rt << 16 | imm
def addu(rd, rs, rt): return rs << 21 | rt << 16 | rd << 11 | 0x21
def addiu(rt, rs, imm): return i_mem(0x09, rt, imm, rs)
def sll(rd, rt, sa): return rt << 16 | rd << 11 | sa << 6
def mult(rs, rt): return rs << 21 | rt << 16 | 0x18
def mflo(rd): return rd << 11 | 0x12
def jal(ram): return 3 << 26 | ((ram - BASE) >> 2)  # stored pre-relocation (vaddr), R_MIPS_26 adds the base
def jr(rs): return rs << 21 | 8


NOP = 0
HI, LO = (TABLE - BASE + 0x8000) >> 16, (TABLE - BASE) & 0xFFFF
assert LO < 0x8000, "lbu offset is signed"

# a2 = character code -> v0 = advance px. Leaf; touches v0 only.
HELPER_CODE = [lui(V0, HI), addu(V0, V0, A2), jr(RA), lbu(V0, LO, V0)]

# (address, original words, new words): the originals are asserted so a different EBOOT never gets patched blind.
SITES = [
    (LAYOUT,
     # lbu v0,0xe(s3); lh a1,0x44(s3); lw a0,0x20(s3); sll v1,v1,1; mult v0,a1; addu a0,a0,v1; lhu a1,(a0);
     # lw a2,4(sp); addiu v1,zero,0x2f; mflo v0; sra v0,v0,1; addu v0,v0,a1   (then beq a2,v1 / sh v0,(a0) kept)
     [0x9262000E, 0x86650044, 0x8E640020, 0x31840, 0x450018, 0x832021, 0x94850000, 0x8FA60004, 0x2403002F, 0x1012,
      0x21043, 0x451021],
     [lw(A2, 4, SP), jal(HELPER), lh(A1, 0x44, S3), lw(A0, 0x20, S3), sll(V1, V1, 1), mult(V0, A1),
      addu(A0, A0, V1), lhu(A1, 0, A0), addiu(V1, ZERO, 0x2F), mflo(V0), NOP, addu(V0, V0, A1)]),
    (DRAW,
     # lbu v0,0xe(s5); lw a0,0x5c(sp); mult v1,v0; mflo v0; sra v0,v0,1; addu a0,a0,v0  (then j / sw a0 kept)
     [0x92A2000E, 0x8FA4005C, 0x620018, 0x1012, 0x21043, 0x822021],
     [lw(A2, 4, SP), jal(HELPER), lw(A0, 0x5C, SP), mult(V1, V0), mflo(V0), addu(A0, A0, V0)]),
]
NEW_RELOCS = [(HELPER, R_HI16), (HELPER + 12, R_LO16), (LAYOUT + 4, R_26), (DRAW + 4, R_26)]


def _sections(d):
    shoff, = struct.unpack_from("<I", d, 0x20)
    n, si = struct.unpack_from("<2H", d, 0x30)
    names = struct.unpack_from("<10I", d, shoff + 40 * si)[4]
    out = []
    for i in range(n):
        s = struct.unpack_from("<10I", d, shoff + 40 * i)
        out.append((d[names + s[0]:d.index(b"\0", names + s[0])].decode(), shoff + 40 * i, s))
    return out


def apply(elf, widths):
    import eboot
    assert len(widths) == 256 and widths[0x20] > 0
    d = bytearray(elf)
    w32 = lambda ram, v: struct.pack_into("<I", d, eboot.ram2off(d, ram), v)
    r32 = lambda ram: struct.unpack_from("<I", d, eboot.ram2off(d, ram))[0]
    # relocation table: (vaddr offset, info) pairs in the 0x700000A0 segment
    phoff, = struct.unpack_from("<I", d, 0x1C)
    phnum, = struct.unpack_from("<H", d, 0x2C)
    ph = next(phoff + 32 * i for i in range(phnum) if struct.unpack_from("<I", d, phoff + 32 * i)[0] == 0x700000A0)
    r_off, r_size = struct.unpack_from("<I", d, ph + 4)[0], struct.unpack_from("<I", d, ph + 16)[0]
    rel = {struct.unpack_from("<I", d, o)[0] for o in range(r_off, r_off + r_size, 8)}
    for ram, old, new in SITES:
        assert [r32(ram + 4 * k) for k in range(len(old))] == old, f"{ram:#x}: not the expected code"
        assert not any(ram - BASE <= x < ram - BASE + 4 * len(old) for x in rel), f"{ram:#x}: relocated word"
        for k, v in enumerate(new):
            w32(ram + 4 * k, v)
    assert not any(HELPER - BASE <= x < CAVE_END - BASE for x in rel), "cave holds relocated words"
    assert d[eboot.ram2off(d, HELPER):eboot.ram2off(d, HELPER) + 11] == b"E2007011601", "cave moved"
    for k, v in enumerate(HELPER_CODE):
        w32(HELPER + 4 * k, v)
    o = eboot.ram2off(d, TABLE)
    d[o:o + 256] = widths
    # append the relocations at the end of the relocation segment (the last .rel section ends there too)
    end = r_off + r_size
    add = b"".join(struct.pack("<II", ram - BASE, t) for ram, t in NEW_RELOCS)  # ofs base 0, addr base 0
    struct.pack_into("<I", d, ph + 16, r_size + len(add))
    secs = _sections(d)
    last = [s for s in secs if s[2][1] == 0x700000A0 and s[2][4] + s[2][5] == end]
    assert len(last) == 1, "no relocation section ends at the segment end"
    struct.pack_into("<I", d, last[0][1] + 20, last[0][2][5] + len(add))
    for name, at, s in secs:
        if s[4] >= end and s[1] != 8:
            struct.pack_into("<I", d, at + 16, s[4] + len(add))
    shoff, = struct.unpack_from("<I", d, 0x20)
    assert shoff >= end
    struct.pack_into("<I", d, 0x20, shoff + len(add))
    return bytes(d[:end] + add + d[end:])
