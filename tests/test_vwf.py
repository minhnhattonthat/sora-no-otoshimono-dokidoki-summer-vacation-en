import os, struct, sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import eboot, font, sign, vwf  # noqa: E402

ELF = os.path.join(ROOT, "work", "eboot.elf")
TFP = os.path.join(ROOT, "work", "res", "RES", "1ST", "HG_G18.TFP")


@pytest.mark.skipif(not os.path.isfile(TFP), reason="run tools/unpack.py first (needs the ISO)")
def test_font_glyphs():
    tfp = open(TFP, "rb").read()
    new, w = font.patch(tfp)
    assert len(new) == len(tfp) and w[ord("0")] == w[ord("9")]
    assert all(0 < w[c] <= 18 for c in range(0x20, 0x7F)) and w[0xA1] == 9
    for c in range(0x20, 0x7F):
        o = font.glyph_offset(new, c)
        assert all((b & 15) <= font.INK and b >> 4 <= font.INK for b in new[o:o + 162]), chr(c)  # 13+ draws nothing
    assert font.width("Tomoki") == sum(w[ord(c)] for c in "Tomoki")


@pytest.mark.skipif(not (os.path.isfile(ELF) and os.path.isfile(TFP)), reason="needs work/eboot.elf and work/res")
def test_vwf_patch():
    elf = open(ELF, "rb").read()[:sign.ELF_SIZE]
    _, w = font.patch(open(TFP, "rb").read())
    new = vwf.apply(elf, w)
    assert len(new) == len(elf) + 8 * len(vwf.NEW_RELOCS)
    rd = lambda d, ram: struct.unpack_from("<I", d, eboot.ram2off(d, ram))[0]
    assert rd(new, vwf.LAYOUT + 4) == rd(new, vwf.DRAW + 4) == vwf.jal(vwf.HELPER)
    o = eboot.ram2off(new, vwf.TABLE)
    assert new[o:o + 256] == w
    # relocation block grew by exactly the new entries, which sit at its end; sections after it moved with it
    phoff, = struct.unpack_from("<I", new, 0x1C)
    ph = next(phoff + 32 * i for i in range(3) if struct.unpack_from("<I", new, phoff + 32 * i)[0] == 0x700000A0)
    off, size = struct.unpack_from("<I", new, ph + 4)[0], struct.unpack_from("<I", new, ph + 16)[0]
    tail = [struct.unpack_from("<II", new, off + size - 8 * len(vwf.NEW_RELOCS) + 8 * k)
            for k in range(len(vwf.NEW_RELOCS))]
    assert tail == [(ram - vwf.BASE, t) for ram, t in vwf.NEW_RELOCS]
    assert eboot.sections(new)[".shstrtab"][0] == eboot.sections(elf)[".shstrtab"][0] + 8 * len(vwf.NEW_RELOCS)
    assert eboot.sections(new)[".rodata"] == eboot.sections(elf)[".rodata"]
