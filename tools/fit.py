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


def greedy_lines(words, px):
    lines, line = 0, ""
    for word in words:
        if line and font.width(line + " " + word) > px:
            lines, line = lines + 1, word
        else:
            line = f"{line} {word}" if line else word
    return lines + 1


def balanced(words, px):
    """The greedy line count, with the breaks that minimise the summed squared slack: no one-word widow on the last line
    when the words allow it. A single word wider than px gets a line of its own."""
    n, sp = greedy_lines(words, px), font.width(" ")
    pre = [0]
    for w in words:
        pre.append(pre[-1] + font.width(w))
    inf = float("inf")
    cost = [[inf] * (len(words) + 1) for _ in range(n + 1)]
    back = [[0] * (len(words) + 1) for _ in range(n + 1)]
    cost[0][0] = 0
    for k in range(1, n + 1):
        for j in range(1, len(words) + 1):
            for i in range(j - 1, -1, -1):
                w = pre[j] - pre[i] + sp * (j - i - 1)
                if w > px and i < j - 1:
                    break
                c = cost[k - 1][i] + (px - w) ** 2
                if c < cost[k][j]:
                    cost[k][j], back[k][j] = c, i
    assert cost[n][len(words)] < inf  # the greedy breaks are one feasible answer
    out, j = [], len(words)
    for k in range(n, 0, -1):
        i = back[k][j]
        out.append(" ".join(words[i:j]))
        j = i
    return out[::-1]


def wrap(text, px):
    """Balanced word wrap to px; keeps explicit breaks."""
    return "\n".join(line for para in text.split("\n") for line in balanced(para.split(" "), px))


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
    if len(rows) > 1 and len(rows[-1].strip()) < STUB:
        out.append(f"last line {rows[-1].strip()!r} is a stub (< {STUB} chars); rephrase")
    return out


STUB = 6


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
