"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (for check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/

Copied from the skill's assets/batches.py; the ADAPTER reads script/ TSVs (sos/*/*.tsv, eboot.tsv, sfo.tsv).
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import fit  # noqa: E402
import script as scriptio  # noqa: E402

TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"/[ACDKLNVWZacvwz]")  # engine control codes (docs/re/script.md §Control codes); only /K is used
FREE = set()
VARIABLE = r"%(?:name|family)"  # never used by the script; problems() rejects it outright
SPEAKERS = {"智樹": "Tomoki", "智樹Ａ": "Tomoki", "智樹Ｂ": "Tomoki", "智樹？": "Tomoki?", "イカロス": "Ikaros",
            "ニンフ": "Nymph", "そはら": "Sohara", "そはらＡ": "Sohara", "そはらＢ": "Sohara", "守形": "Sugata",
            "美香子": "Mikako", "？？？": "???", "智樹＆そはら": "Tomoki & Sohara", "智樹＆ニンフ": "Tomoki & Nymph"}
# JP regex -> EN regex that must appear (glossary ruling D1: honorifics kept; glossary.md §Honorifics). Regexes, not
# glossary rows, because has_term() needs a run boundary and さん is followed by a hiragana particle.
HONORIFICS = {"イカロスさん": "Ikaros-san", "イカロスちゃん": "Ikaros-chan", "そはらさん": "Sohara-san",
              "ニンフさん": "Nymph-san", "ニンフちゃん": "Nymph-chan", "桜井[君く]": "Sakurai-ku+n",
              "見月さん": "Mitsuki-san", "トモちゃん": "Tomo-cha+n", "英[く君]": "Ei-ku+n", "守形先輩": "Sugata-senpai", "守形さん": "Sugata-san"}
# '~' is Mikako's sing-song tail only (decision D8, glossary.md §Style rules): her lines, plus these where she speaks
# off-screen as ??? or someone imitates her.
MIKAKO_VOICE = {"SC20043.m5", "SC30800.m12", "SC34110.m9", "SC90040.m55"}
FORMS = {"dialogue": "dlg", "choice": "choice", "helpbar": "menu", "system": "menu", "xmb": "menu"}


def docs():
    """(path, rows, entries) per script file; entries carry source/box for the width check."""
    files = [(p, "sos") for p in sorted(SCRIPT.glob("sos/*/*.tsv"))]
    files += [(SCRIPT / "eboot.tsv", "eboot"), (SCRIPT / "sfo.tsv", "sfo")]
    for path, source in files:
        rows = scriptio.read_tsv(path)
        for r in rows:
            r["_source"], r["_box"], r["_file"] = source, fit.box_of(source, r), path.stem
        yield path, rows, rows


def save(path, rows):
    scriptio.write_tsv(path, rows)


BLANK = " 　"


def needs_english(entry):
    """A box holding only a full-width space (a pause) keeps its original bytes."""
    return bool(entry.get("jp", "").replace("\\n", "").strip("　 ")) and not entry.get("en")


def group_of(entry):
    """One script file stays in one batch (story order, shared context)."""
    return entry["_file"]


def entry_key(entry):
    return entry["id"]


def limit_label(entry):
    px, lines = fit.BOXES.get(entry["_box"], (0, 0))
    out = f"{px}px" + (f"x{lines}" if lines > 1 else "") if px else ""
    if entry["_source"] != "sos":
        out +=f"{' ' if out else ''}{entry['max']}B"
    return out


def width_problems(entry, en):
    text = scriptio.unesc(en)
    out = fit.problems(text, entry["_box"])
    if entry["_source"] != "sos":
        n = len(text.encode("utf-8" if entry["kind"] == "utf-8" else "cp932"))
        if n > int(entry["max"]):
            out.append(f"{n} bytes > slot max {entry['max']}")
    return out


def encodable(char):
    """ASCII the English font has; '/' would start a control code and '\\' an escape (the TOKEN /K is removed first)."""
    return " " <= char <= "~" and char not in "/\\"
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    jp = jp.replace(" / ", "")
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    """Every rule, on one line of English (en as stored: \\n escaped)."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en.replace("\\n", ""))
    if bad := sorted({c for c in plain if not encodable(c)}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en:
        out.append("escape sequence or tab in the English")
    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have or (want and not en.endswith("/K")):
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)} (/K stays at the very end)")
    if re.search(VARIABLE, en):
        out.append("%name/%family is a renderer token; write the name")
    if "~" in en and entry.get("speaker") != "美香子" and entry["id"] not in MIKAKO_VOICE:
        out.append("'~' is Mikako's tail only (D8): stretch the word (\"sooo\") or drop it")
    jp_plain = TOKEN.sub("", jp).replace("\\n", "")
    en_terms = " ".join(TOKEN.sub(" ", en).replace("\\n", " ").split()).lower()
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(" ".join(e.split()).lower() in en_terms for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_re, en_re in HONORIFICS.items():
        if re.search(jp_re, jp_plain) and not re.search(en_re, en):
            out.append(f"honorific {jp_re} needs {en_re}")
    for side, strip in (("leading", str.lstrip), ("trailing", str.rstrip)):
        if (strip(jp_plain, BLANK) != jp_plain) != (strip(plain, BLANK) != plain):
            out.append(f"{side} blank differs from the JP")
    return out + width_problems(entry, en)


def index():
    result = {}
    for _, _, entries in docs():
        for e in entries:
            key = entry_key(e)
            if key in result:
                raise ValueError(f"duplicate batch key {key!r}: supply a unique addr or adapt entry_key")
            result[key] = e
    return result


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    index()  # reject ambiguous ids before writing any batches
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for _, _, entries in docs():
        for e in entries:
            if needs_english(e) and entry_key(e) not in taken:
                groups.setdefault(group_of(e), []).append(e)
    batches, cur, chars = [], [], 0
    for group in groups.values():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{entry_key(e)}\t{SPEAKERS.get(e['speaker'], e['speaker'])}\t{FORMS[e['_box']]}\t{limit_label(e)}\t"
                f"{e['jp'].replace(chr(92) + 'n', ' / ')}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]).replace("\\n", "") for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
    return bad, dict(rows)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if entry_key(e) in new and e.get("en") and e["en"] != new[entry_key(e)]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, rows, entries in docs():
        touched = False
        for e in entries:
            if entry_key(e) in new and e.get("en") != new[entry_key(e)]:
                e["en"] = new[entry_key(e)]
                touched = True
                changed += 1
        if touched:
            save(path, rows)
    print(f"merged: {changed} entries changed")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        bad += [f"{i}: untranslated: {e['jp']!r}" for i, e in entries.items() if needs_english(e)]
        print(f"{len(entries)} entries, {sum(bool(e.get('en')) for e in entries.values())} translated, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    failed = 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
        if cmd == "merge" and not bad:
            merge(rows, overwrite)
    return 1 if failed else 0


def _selftest():
    e = {"id": "x", "kind": "msg", "jp": "テスト", "_source": "sos", "_box": "dialogue", "max": ""}
    assert problems(e, "A fine line.", []) == []
    assert problems(e, "a/b", [])[0].startswith("unencodable")
    assert "D8" in problems(e, "Yaaay~!", [])[0] and problems(dict(e, speaker="美香子"), "Sakurai-kun~?", []) == []
    assert any("lines" in p for p in problems(e, " ".join(["word"] * 120), []))
    k = {"id": "088DCAD0", "kind": "cp932", "jp": "作戦成功。/K", "_source": "eboot", "_box": "dialogue", "max": "127"}
    assert problems(k, "Mission complete./K", []) == []
    assert problems(k, "Mission complete.", [])[0].startswith("control codes")
    assert any("bytes" in p for p in problems(k, "x" * 130 + "/K", []))
    assert problems(e, "Ikaros", [(["イカロス"], ["Ikaros"], [])]) == []
    assert problems(dict(e, jp="イカロス"), "She", [(["イカロス"], ["Ikaros"], [])]) == ["glossary: イカロス -> Ikaros"]
    assert needs_english(e) and not needs_english(dict(e, jp="　")) and not needs_english(dict(e, en="Test"))
    assert problems(e, " Lead.", []) == ["leading blank differs from the JP"]
    assert problems(dict(e, jp="　テスト"), " Lead.", []) == []
    assert fit.wrap("I finally found a game I might actually beat Tomo-chan at!", 391).split("\n")[-1] != "at!"
    assert "stub" in fit.problems("Hello there.\nOk.", "dialogue")[0]
    assert fit.fitted("Hi there\\nok".replace("\\n", "\n"), "dialogue") == "Hi there\nok"
    print("selftest ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))
