"""Phase 3 identity build: unpack -> repack with no edits gives the original bytes (PTDs and the whole ISO)."""
import hashlib, os, sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build, ptd, yklz  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.isfile(build.ROM), reason="needs the ISO in rom/")


@pytest.fixture(scope="module")
def res():
    return build.read_iso_file(build.ROM, build.RES)


def test_ptd_identity(res):
    assert ptd.repack(res, {}) == res
    for f in ptd.toc(res)[1]:
        if f["name"].endswith(".PTD"):
            raw = res[f["off"]:f["off"] + f["size"]]
            assert ptd.repack(raw, {}) == raw, f["path"]


files = ptd.files


def test_ptd_edit(res):
    """Grow a YKLZ file in res.ptd and a file inside a nested PTD; everything else unpacks unchanged."""
    old = files(res)
    top = next(f["path"] for f in ptd.toc(res)[1] if f["comp"])
    nested = next(p for p in old if "_PTD/" in p)
    edits = {top: old[top] + b"\0" * 5000, nested: old[nested] + b"x" * 3000}
    new = files(ptd.repack(res, edits))
    assert new == {**old, **edits}
    with pytest.raises(AssertionError):
        ptd.repack(res, {"RES/NOPE.BIN": b""})


def test_iso_identity(tmp_path):
    out = tmp_path / "id.iso"
    want = open(os.path.join(ROOT, "rom.sha1")).read().split()[0]
    try:
        build.build(str(out), {})
        with open(out, "rb") as f:
            assert hashlib.file_digest(f, "sha1").hexdigest() == want
    finally:
        out.unlink(missing_ok=True)  # 1 GB; pytest keeps old tmp dirs
