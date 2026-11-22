"""Graphics redraws that the screen can cut: staff-roll cards slide right while shown (docs/re/graphics.md)."""
import os
import pytest
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, ORIG = os.path.join(ROOT, "gfx", "out", "credits"), os.path.join(ROOT, "work", "gimpng")


@pytest.mark.skipif(not os.path.isdir(ORIG), reason="needs work/gimpng (tools/gimsurvey.py)")
def test_credit_cards_stay_on_screen():
    # cards 910-925 slide to screen x ~300 during the roll: ink past 180 px is cut at the screen edge
    for n in range(910, 926):
        assert Image.open(os.path.join(OUT, f"{n:04d}.png")).getbbox()[2] <= 180, n
