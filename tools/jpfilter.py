"""Keep the sentence-like hits of a jpscan.py listing (kana-heavy runs), drop code noise. RE helper.

    python -X utf8 tools/jpfilter.py work/eboot_jp.txt > work/eboot_good.txt
"""
import ast, collections, re, sys

bins = collections.Counter()
good = []
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"(\w+)\s+(0x[0-9a-f]+)\s+(.*)", line.strip())
    if not m:
        continue
    enc, a, s = m.groups()
    s = ast.literal_eval(s)
    a = int(a, 16)
    kana = sum(1 for c in s if "぀" <= c <= "ヿ" or c in "、。…！？ー")
    if kana >= 2 and kana / len(s) > 0.3:
        good.append((a, enc, s))
        bins[a >> 16] += 1
for a, e, s in good:
    print(f"{a:#x}\t{e}\t{s!r}")
print(len(good), "strings", sum(len(s) for *_, s in good), "chars", sorted((hex(k << 16), v) for k, v in bins.items()),
      collections.Counter(e for _, e, _ in good), file=sys.stderr)
