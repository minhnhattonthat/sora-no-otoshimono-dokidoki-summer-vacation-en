import glob, os, sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import sos, yklz  # noqa: E402


def test_yklz_roundtrip():
    raw = bytes(range(256)) * 3 + b"abcabcabcabc" * 50 + os.urandom(500) + b"\xcc" * 300 + b"ab" * 200
    # strict = the game's memcpy decoder: no reference may overlap its own output
    assert yklz.unpack(yklz.pack(raw), strict=True) == raw


SOS = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "work", "res", "**", "*.SOS"), recursive=True))


@pytest.mark.skipif(not SOS, reason="run tools/unpack.py first (needs the ISO)")
def test_sos_identity():
    for f in SOS:
        d = open(f, "rb").read()
        assert sos.build(d) == d, f
