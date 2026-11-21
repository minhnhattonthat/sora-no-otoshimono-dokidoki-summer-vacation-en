"""Phase 4 extract: script/ TSV re-encodes to the original bytes, and every text source is covered."""
import glob, os, sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build, eboot, script, sfo, sos  # noqa: E402

needs_rom = pytest.mark.skipif(not os.path.isfile(build.ROM), reason="needs the ISO in rom/")


def test_escape():
    for t in ["a\nb", "x\\ny", "\\", "末尾\\"]:
        assert script.unesc(script.esc(t)) == t


def test_tsv_columns():
    for p in glob.glob(os.path.join(script.SCRIPT, "**", "*.tsv"), recursive=True):
        rows = script.read_tsv(p)  # asserts the column count per row
        assert rows and list(rows[0]) == script.COLS, p
        assert len({r["id"] for r in rows}) == len(rows), f"{p}: duplicate id"


@needs_rom
def test_sos_roundtrip_and_coverage():
    """Every SOS: TSV rows == fresh extraction (ids, kinds, jp), and rebuilding from TSV jp gives identical bytes."""
    src = script.sos_sources(script.res_files())
    seen = set()
    for key, d in src.items():
        fresh = script.sos_rows(d, key)  # asserts every pool slot is a row, empty, a path or a known key
        path = os.path.join(script.SCRIPT, "sos", key + ".tsv")
        if not fresh:
            assert not os.path.exists(path)
            continue
        seen.add(os.path.normpath(path))
        rows = script.read_tsv(path)
        assert [(r["id"], r["kind"], script.unesc(r["jp"])) for r in rows] == \
            [(r["id"], r["kind"], r["jp"]) for r in fresh], key
        new = {f["slot"]: script.sos_encode(r["kind"], script.unesc(r["jp"])) for f, r in zip(fresh, rows)}
        assert sos.build(d, new) == d, key
    files = {os.path.normpath(p) for p in glob.glob(os.path.join(script.SCRIPT, "sos", "**", "*.tsv"), recursive=True)}
    assert files == seen, "script/sos has files with no SOS source"


@pytest.mark.skipif(not os.path.isfile(script.ELF), reason="needs work/eboot.elf (docs/re/script.md)")
def test_eboot_roundtrip_and_coverage():
    d = open(script.ELF, "rb").read()
    text = script.read_tsv(os.path.join(script.SCRIPT, "eboot.tsv"))
    other = script.read_tsv(os.path.join(script.SCRIPT, "eboot_nontext.tsv"))
    for r in text + other:
        raw = script.eboot_encode(r["kind"], script.unesc(r["jp"]))
        o = eboot.ram2off(d, int(r["id"], 16))
        assert d[o:o + len(raw) + 1] == raw + b"\0", r["id"]
        assert len(raw) <= int(r["max"]), r["id"]
    assert all(r["notes"] for r in other), "every non-text row says why"
    hits = {f"{eboot.off2ram(d, o):08X}" for o, *_ in eboot.scan(d)}
    assert hits == {r["id"] for r in text} | {r["id"] for r in other}


@needs_rom
def test_sfo():
    rows = script.read_tsv(os.path.join(script.SCRIPT, "sfo.tsv"))
    title = sfo.read(build.read_iso_file(build.ROM, script.SFO))["TITLE"][4]
    assert [(r["id"], script.unesc(r["jp"])) for r in rows] == [("TITLE", title)]
