"""Phase 7 EBOOT checks (references/pipeline.md §Checks, romdiff for the ELF): the string writes from script/eboot.tsv
change nothing outside their slots, never overlap, and no pointer or lui pair in the original ELF reaches into a
string past its first byte (a mid-string reference, or the slack an English string now fills)."""
import os, struct, sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build, eboot, script, sign  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.isfile(script.ELF), reason="needs work/eboot.elf (tools/dump_eboot.py)")
LOADS = {0x20, 0x21, 0x23, 0x24, 0x25}  # lb lh lw lbu lhu: rt = base + imm
I_WRITES_RT = {0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F} | LOADS  # addi(u) slti(u) andi ori xori lui, loads


def refs(elf):
    """{vaddr: [site]} for raw words and lui+addiu/ori/load pairs (vaddr = pre-relocation value, RAM - BASE)."""
    out = {}
    _, t0, tn = eboot.sections(elf)[".text"]
    for off, va, size in eboot.segments(elf):
        w = struct.unpack_from(f"<{size // 4}I", elf, off)
        for i, x in enumerate(w):
            if not t0 <= va + 4 * i < t0 + tn:  # in .text a raw match is an instruction word (sra/srl collide)
                out.setdefault(x, []).append(va + 4 * i)
            if x >> 26 != 0x0F:
                continue
            rt, hi = (x >> 16) & 31, (x & 0xFFFF) << 16
            for j in range(i + 1, min(i + 16, len(w))):
                v, op = w[j], w[j] >> 26
                if (v >> 21) & 31 == rt and op in {0x09, 0x0D, 0x28, 0x29, 0x2B} | LOADS:
                    imm = v & 0xFFFF
                    val = (hi | imm) if op == 0x0D else (hi + imm - (imm & 0x8000) * 2) & 0xFFFFFFFF
                    out.setdefault(val, []).append(va + 4 * j)
                if (op in I_WRITES_RT and (v >> 16) & 31 == rt) or (op == 0 and (v >> 11) & 31 == rt) \
                        or op in (0x02, 0x03) or (op == 0 and v & 0x3F == 0x08):  # rt redefined, or j/jal/jr
                    break
    return out


@pytest.fixture(scope="module")
def built():
    orig = open(script.ELF, "rb").read()[:sign.ELF_SIZE]
    elf, writes = build.eboot_strings()
    return orig, elf, writes


def test_writes_stay_in_slots(built):
    orig, elf, writes = built
    spans = sorted((eboot.ram2off(orig, a), eboot.ram2off(orig, a) + len(new)) for a, _, new in writes)
    assert all(b <= c for (_, b), (c, _) in zip(spans, spans[1:])), "two string writes overlap"
    inside = bytearray(len(orig))
    for a, b in spans:
        inside[a:b] = b"\1" * (b - a)
    stray = [hex(eboot.off2ram(orig, i)) for i in range(len(orig)) if orig[i] != elf[i] and not inside[i]]
    assert not stray, f"bytes changed outside the string slots: {stray[:8]}"


@pytest.mark.skipif(not os.path.isfile(build.ROM), reason="needs the ISO in rom/")
def test_res_leaves():
    """The English res.ptd keeps the leaf set; only the leaves the build replaced (SOS scripts, HG_G18.TFP) differ."""
    import ptd
    res = build.read_iso_file(build.ROM, build.RES)
    repl, files = build.texts()
    old, new = ptd.files(res), ptd.files(ptd.repack(res, repl))
    assert new.keys() == old.keys()
    changed = {k for k in old if old[k] != new[k]}
    assert changed == {k for k in repl if repl[k] != old[k]} and all(new[k] == repl[k] for k in changed)
    assert all(k.endswith((".SOS", "/HG_G18.TFP")) for k in changed)
    assert set(files) == {build.EBOOT, build.SFO} and files[build.EBOOT][:4] == b"~PSP"


def test_nothing_points_inside_a_written_string(built):
    orig, _, writes = built
    r = refs(orig)
    # the scanner sees both forms: the Hexcite help-bar pointer table (.data) and Alpha's help-line lui pair
    assert 0x088F3E58 - eboot.BASE in r and 0x088C07B4 - eboot.BASE in r
    bad =[(f"{a:08X}", f"+{k}", [hex(eboot.BASE + s) for s in r[a - eboot.BASE + k]])
           for a, _, new in writes for k in range(1, len(new)) if a - eboot.BASE + k in r]
    assert not bad, f"references into a rewritten string (would show a changed tail): {bad[:8]}"
