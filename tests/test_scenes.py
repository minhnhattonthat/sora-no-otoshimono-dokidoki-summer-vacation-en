"""tools/debug/scenes.tsv is well-formed: routes parse, cheats exist, script bases fit the 32-byte literal."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "debug"))
import warp  # noqa: E402


def test_scene_rows():
    scenes = warp.load_scenes()
    assert {"title", "hub", "prologue"} <= set(scenes)
    for name, (n, base, cheats, route, settle, expect, note) in scenes.items():
        assert base in ("title", "hub") or base.startswith("script:"), name
        if base.startswith("script:"):
            assert len(f"res/script/sc/{base[7:]}") <= 31, name
        for c in filter(None, cheats.split(",")):
            assert c in warp.CHEATS, (name, c)
        warp.psp.parse_route(route)
        assert settle.isdigit(), name
        if expect:
            m, s = expect.split(":"); assert m.isdigit() and s.isdigit(), name
        assert note, name
