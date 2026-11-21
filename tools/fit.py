"""Fit English to the measured boxes (tools/boxes.tsv, docs/re/script.md §Dialogue box width).

    python -X utf8 tools/fit.py "English text" [--box dialogue|choice|helpbar]   width per wrapped line

Translators write a box as one paragraph; the build word-wraps it here (an explicit \\n still forces a break).
The engine itself wraps mid-word at 391 px, so every dialogue-box line is broken by wrap() before it gets there.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import font  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def boxes():
    out = {}
    with open(os.path.join(ROOT, "tools", "boxes.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            c = line.rstrip("\n").split("\t")
            out[c[0]] = (int(c[2]), int(c[3]))
    return out


BOXES = boxes()
EBOOT_BOX = [(0x088C07B4, 0x088C1FB4, "dialogue"), (0x088DCAD0, 0x088E1514, "dialogue"),
             (0x088F3E3C, 0x088F3F7F, "helpbar")]


def box_of(source, row):
    """source: 'sos', 'eboot' or 'sfo' (the script/ file the row came from)."""
    if source == "sos":
        return "choice" if row["kind"] == "choice" else "dialogue"
    if source == "eboot" and row["kind"] == "cp932":
        addr = int(row["id"], 16)
        return next(b for lo, hi, b in EBOOT_BOX if lo <= addr <= hi)
    return "system" if source == "eboot" else "xmb"


def wrap(text, px):
    """Greedy word wrap to px; keeps explicit breaks. A single word wider than px stays whole (problems() flags it)."""
    out = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            if line and font.width(line + " " + word) > px:
                out.append(line)
                line = word
            else:
                line = f"{line} {word}" if line else word
        out.append(line)
    return "\n".join(out)


def fitted(text, box):
    """The text as the build inserts it: dialogue boxes word-wrapped, the rest as written."""
    if box != "dialogue":
        return text
    tail = "/K" if text.endswith("/K") else ""
    return wrap(text[:len(text) - len(tail)], BOXES[box][0]) + tail


def problems(text, box):
    px, lines = BOXES.get(box, (0, 0))
    if not px:
        return []
    shown = fitted(text, box)
    if shown.endswith("/K"):
        shown = shown[:-2]
    rows = shown.split("\n")
    out = []
    if len(rows) > lines:
        out.append(f"{len(rows)} lines > {lines} in the {box} box")
    wide = [font.width(r) for r in rows if font.width(r) > px]
    if wide:
        out.append(f"line {max(wide)} px > {px} px ({box})")
    return out


def main(argv):
    if not argv or argv[0].startswith("-"):
        sys.exit(__doc__)
    box = argv[argv.index("--box") + 1] if "--box" in argv else "dialogue"
    text = argv[0].replace("\\n", "\n")
    for line in fitted(text, box).split("\n"):
        print(f"{font.width(line):4d} px  {line}")
    bad = problems(text, box)
    print("OK" if not bad else "; ".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
