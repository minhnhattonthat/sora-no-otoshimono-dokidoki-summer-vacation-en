"""Reviewer pairs files (docs/reviewer-brief.md) and story-pass chapter files (docs/story-reviewer-brief.md).

    python -X utf8 tools/pairs.py bNNN ...   -> work/tl/review/bNNN.txt: `>> id | speaker | JP` / `   EN`, story order
    python -X utf8 tools/pairs.py --chapters -> work/qa/story/chapters/<chapter>.txt, from script/ (re-run after edits)

English comes from work/tl/bNNN.out.tsv (falls back to script/ once merged). Batches hold whole script files, so the
neighbours a reviewer needs are in the same file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402

ROOT = batches.ROOT
STORY = ROOT / "work/qa/story/chapters"
CHUNK = 480  # rows per story chapter for the event pools (a reviewer reads it whole)
# Fixed story chapters (docs/synopsis.md §Structure); the card-event pools SC1-SC3 are cut into CHUNK-row parts.
FIXED = [("c00_prologue", ["SC0000"]), ("c01_chapter1", ["SC0001"]), ("c02_chapter2", ["SC0002"]),
         ("c03_chapter3", ["SC0003"]), ("c90_endings_true_bad", ["SC90010", "SC90020"]),
         ("c91_endings_after", ["SC90030", "SC90040", "SC90050"])]
POOLS = [("c1_cards", "SC1"), ("c2_amnesia", "SC2"), ("c3_lessons", "SC3")]
NOTE = ("# One file = one SOS script. Files sharing all but the last digit(s) are one event: the 0/00 file is the setup\n"
        "# (ends on a choice), the other files are ALTERNATIVE outcomes/branches of that choice, never played in a row.\n"
        "# SC000x3 merges back after the SC000x1/x2 branch. Speakers ending ? are unnamed in the original.\n")


def chapter_text(files):
    lines = [NOTE]
    for path in files:
        lines.append(f"## {path.stem}")
        for e in batches.scriptio.read_tsv(path):
            if not e.get("jp", "").replace("\\n", "").strip("　 "):
                continue
            spk = batches.SPEAKERS.get(e.get("speaker", ""), e.get("speaker", "")) or "-"
            lines.append(f">> {e['id']} | {spk} | {e['jp'].replace(chr(92) + 'n', ' / ')}")
            lines.append(f"   {e.get('en') or '(untranslated)'}")
    return "\n".join(lines) + "\n"


def chapters():
    sos = sorted(batches.SCRIPT.glob("sos/*/*.tsv"))
    out = {name: [p for p in sos if p.stem.startswith(tuple(pre))] for name, pre in FIXED}
    for name, d in POOLS:
        part, n, rows = [], 1, 0
        for p in [p for p in sos if p.parent.name == d]:
            size = len(batches.scriptio.read_tsv(p))
            # keep one event (same stem minus the last digit) in one part
            if rows + size > CHUNK and part and p.stem[:-1] != part[-1].stem[:-1]:
                out[f"{name}{n:02}"], part, n, rows = part, [], n + 1, 0
            part.append(p)
            rows += size
        out[f"{name}{n:02}"] = part
    out["c40_system"] = [p for p in sos if p.parent.name == "SC4" or p.stem == "SOUND"]
    out["c41_eboot"] = [batches.SCRIPT / "eboot.tsv", batches.SCRIPT / "sfo.tsv"]
    used = [p for v in out.values() for p in v]
    assert sorted(used) == sorted(sos + out["c41_eboot"]), "every script file in exactly one chapter"
    return out


def write_chapters():
    STORY.mkdir(parents=True, exist_ok=True)
    for old in STORY.glob("*.txt"):
        old.unlink()
    for name, files in chapters().items():
        (STORY / f"{name}.txt").write_text(chapter_text(files), encoding="utf-8", newline="\n")
        print(name, len(files), "files")


def write(batch, entries):
    ids = [r[0] for r in batches.read_tsv(batches.TL / f"{batch}.tsv")]
    out_path = batches.TL / f"{batch}.out.tsv"
    en = dict((r[0], "\t".join(r[1:])) for r in batches.read_tsv(out_path)) if out_path.exists() else {}
    lines = []
    for i in ids:
        e = entries[i]
        spk = batches.SPEAKERS.get(e["speaker"], e["speaker"]) or "-"
        lines.append(f">> {i} | {spk} | {e['jp'].replace(chr(92) + 'n', ' / ')}")
        lines.append(f"   {en.get(i) or e.get('en') or '(untranslated)'}")
    path = batches.TL / "review" / f"{batch}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if not sys.argv[1:]:
        sys.exit(__doc__)
    if sys.argv[1] == "--chapters":
        sys.exit(write_chapters())
    entries = batches.index()
    for b in sys.argv[1:]:
        print(write(b, entries))
