import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))


def test_tools_import():
    import tbl  # noqa: F401  the vendored codec must stay importable without the skill
