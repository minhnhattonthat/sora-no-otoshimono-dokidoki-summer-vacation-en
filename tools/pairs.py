"""Reviewer pairs files (docs/reviewer-brief.md).

    python -X utf8 tools/pairs.py bNNN ...   -> work/tl/review/bNNN.txt: `>> id | speaker | JP` / `   EN`, story order

English comes from work/tl/bNNN.out.tsv (falls back to script/ once merged). Batches hold whole script files, so the
neighbours a reviewer needs are in the same file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402

ROOT = batches.ROOT


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
    entries = batches.index()
    for b in sys.argv[1:]:
        print(write(b, entries))
