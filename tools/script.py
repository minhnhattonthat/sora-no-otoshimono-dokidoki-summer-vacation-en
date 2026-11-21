"""Text extraction to script/ TSV, and the TSV codec the build and tests use. See docs/re/script.md §Extract.

    python -X utf8 tools/script.py dump [--force]   write script/*.tsv from the ISO + work/eboot.elf (missing files
                                                     only; --force refreshes jp/speaker/max and keeps en/notes by id)

Sources:
  script/sos/<dir>/<NAME>.tsv  one per SOS file (RES/SCRIPT/SC/<dir>/<NAME>.SOS; the copies in
                               __PACK__/SUBSCRIPT.PTD are byte-identical and get the same text). One row per unique
                               pool slot shown as text: kind msg (dialogue box, opcode 7f) or choice (opcode 5d).
                               id NAME.m<first message index>; the slot's trailing \\n (every msg has one) is implied.
  script/eboot.tsv             EBOOT strings shown in game (id = RAM address; enc cp932/utf-8; max = bytes before the
                               next non-zero byte, NUL excluded).
  script/eboot_nontext.tsv     every other Japanese string the EBOOT scan finds, with why it is not text.
  script/sfo.tsv               PARAM.SFO TITLE (XMB).
TSV: id, kind, speaker, max, jp, en, notes. Newline is written \\n, backslash \\\\.
"""
import argparse, csv, hashlib, os, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)
import eboot, sos  # noqa: E402

SCRIPT = os.path.join(ROOT, "script")
ELF = os.path.join(ROOT, "work", "eboot.elf")
SFO = "/PSP_GAME/PARAM.SFO"
COLS = ["id", "kind", "speaker", "max", "jp", "en", "notes"]
SC = "RES/SCRIPT/SC/"
OP_SPEAKER, OP_MSG, OP_CHOICE = 0x53, 0x7F, 0x5D  # `40 op u16` statements in SOS bytecode
# SOS strtab strings that look like text but are keys: speaker names select a nameplate GIM (COMMON_00_NAME) through
# the EBOOT table at 0x088fb708 (script/eboot_nontext.tsv); TUTORIAL_REPLAY is a label.
SOS_KEYS = {"智樹", "智樹Ａ", "智樹Ｂ", "智樹？", "智樹＆ニンフ", "智樹＆そはら", "イカロス", "ニンフ", "そはらＡ",
            "そはらＢ", "そはら", "美香子", "守形", "？？？", "TUTORIAL_REPLAY"}


def esc(t):
    return t.replace("\\", "\\\\").replace("\n", "\\n")


def unesc(t):
    out, i = [], 0
    while i < len(t):
        if t[i] == "\\" and i + 1 < len(t):
            out.append({"n": "\n", "\\": "\\"}[t[i + 1]])
            i += 2
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None))
    for r in rows:
        assert None not in r and None not in r.values(), f"{path}: bad column count at {r.get('id')}"
    return rows


def write_tsv(path, rows, cols=COLS):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cols, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, lineterminator="\n")
        w.writeheader()
        for r in rows:
            assert not any("\t" in str(v) or "\n" in str(v) for v in r.values()), r
            w.writerow({c: r.get(c, "") for c in cols})


# ---- SOS ----

def sos_key(path):
    """RES/SCRIPT/SC/SC1/SC10000.SOS (or its SUBSCRIPT_PTD copy) -> SC1/SC10000."""
    return path[path.index(SC) + len(SC):-4]


def sos_sources(res_files):
    """{key: bytes} of the unique SOS files; asserts every copy of a key is identical."""
    out = {}
    for p, d in res_files.items():
        if p.endswith(".SOS"):
            k = sos_key(p)
            assert out.setdefault(k, d) == d, f"{p} differs from its other copy"
    return out


def statements(d):
    """[(op, u16)] in code order: `40 53|7f u16 40` speaker/message, `5d u16 40` choice (it follows a `7f u16`
    branch target, so no 40 before it). Byte-pattern match, not a full decoder: only used to label rows."""
    c_off, = struct.unpack_from("<I", d, 0x14)
    c_sz, = struct.unpack_from("<H", d, 0x2A)
    code = d[c_off:c_off + c_sz] + b"\x40"
    return [(code[k], struct.unpack_from("<H", code, k + 1)[0]) for k in range(1, len(code) - 3)
            if code[k + 3] == 0x40 and (code[k] == OP_CHOICE or code[k - 1] == 0x40 and code[k] in (OP_SPEAKER, OP_MSG))]


def sos_rows(d, name):
    """Rows (story order = message index order) for one SOS file; asserts every slot is classified."""
    info = sos.parse(d)
    slots, moffs, soffs = info["slots"], info["moffs"], info["soffs"]
    kind, speaker, spk = {}, {}, ""
    for op, n in statements(d):
        if op == OP_SPEAKER and n < len(soffs):
            spk = slots[soffs[n]].decode("cp932")
        elif op == OP_MSG and 0 < n < len(moffs):
            kind[n] = "msg"
            speaker.setdefault(n, spk)
            spk = ""
        elif op == OP_CHOICE and 0 < n < len(moffs):
            kind.setdefault(n, "choice")
    rows, done = [], set()
    for n, o in enumerate(moffs):
        s = slots[o]
        if not s or o in done:
            continue
        assert sos.is_text(s) and n in kind, f"{name} message {n} unreferenced or not text: {s[:30]!r}"
        done.add(o)
        t, k = s.decode("cp932"), kind[n]
        if k == "msg":
            if t.endswith("\n"):
                t = t[:-1]
            else:
                k = "msg_nonl"  # 5 shouts stored without the usual trailing newline; kept as the game has them
        dup = [m for m, x in enumerate(moffs) if x == o and m != n]
        rows.append(dict(id=f"{name.split('/')[-1]}.m{n}", kind=k, speaker=speaker.get(n, ""), max="",
                         jp=t, en="", notes=f"also m{','.join(map(str, dup))}" if dup else "", slot=o))
    for o in set(soffs) - set(moffs):
        s = slots[o]
        assert not sos.is_text(s) or s.decode("cp932") in SOS_KEYS, f"{name}: unclassified string {s!r}"
    return rows


def sos_encode(kind, text):
    return (text + ("\n" if kind == "msg" else "")).encode("cp932")


# ---- EBOOT ----

EBOOT_NONTEXT = [  # (first RAM addr, last, reason); checked against every scan hit
    (0x088F1734, 0x088F17E8, "kinsoku (line-break) tables (pointers at 0x088FD198/0x088FD1A8); engine data"),
    (0x088F1834, 0x088F1854, "name-substitution tokens the text renderer strncmp()s (0x08817740); no script uses them"),
    (0x088F1874, 0x088F18A4, "kinsoku (line-break) tables; engine data"),
    (0x088F1B2C, 0x088F1C20, "layout object names (title screen FSB)"),
    (0x088F2030, 0x088F2C64, "layout object names"),
    (0x088F3318, 0x088F3614, "layout object names"),
    (0x088F3EF0, 0x088F44E8, "layout object names"),
    (0x088F7AF8, 0x088F805C, "layout object names"),
    (0x088F88F4, 0x088FA028, "layout object names"),
    (0x088FB708, 0x088FB78C, "speaker-name keys matched against SOS speaker strings -> nameplate GIM"),
    (0x088FB808, 0x088FB810, "layout object names"),
]
EBOOT_NONTEXT_ONE = {0x088F3310: "layout object name (そはら, next to タイトル)",
                     0x088F44E0: "layout object name (ニンフ, between layout names)"}


EBOOT_STRIDE = [(0x088C07B4, 0x088C1FB4, 0x100), (0x088DCAD0, 0x088E1514, 0xC4)]  # fixed-size slot tables


def eboot_room(d, o, n):
    """Bytes usable for text at file offset o: up to the next non-zero byte (or the slot end), minus the NUL.
    guess for free-standing strings: the zeros after a string may be another field; phase 7 checks each xref."""
    e = o + n
    while d[e] == 0:
        e += 1
    a = eboot.off2ram(d, o)
    stride = next((s for lo, hi, s in EBOOT_STRIDE if lo <= a <= hi), e - o)
    return min(e - o, stride) - 1


def eboot_rows(d):
    text, other = [], []
    for o, enc, raw, t in eboot.scan(d):
        a = eboot.off2ram(d, o)
        why = EBOOT_NONTEXT_ONE.get(a) or next((r for lo, hi, r in EBOOT_NONTEXT if lo <= a <= hi), "")
        row = dict(id=f"{a:08X}", kind=enc, speaker="", max=str(eboot_room(d, o, len(raw))), jp=t, en="", notes=why)
        (other if why else text).append(row)
    return text, other


def eboot_encode(kind, text):
    return text.encode(kind)


# ---- dump ----

def merge(path, rows, force):
    """Write rows; an existing file keeps its en/notes by id (only with --force; else left alone)."""
    if os.path.exists(path):
        if not force:
            return False
        old = {r["id"]: r for r in read_tsv(path)}
        for r in rows:
            if r["id"] in old:
                o = old[r["id"]]
                if o["en"] and o["jp"] != esc(r["jp"]):
                    print(f"WARN {r['id']}: jp changed under an existing translation; re-queue it")
                r["en"], r["notes"] = o["en"], o["notes"] or r["notes"]
    write_tsv(path, [{**r, "jp": esc(r["jp"])} for r in rows])
    return True


def res_files():
    import build, ptd
    return ptd.files(build.read_iso_file(build.ROM, build.RES))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dump"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    import build, sfo
    n = 0
    for k, d in sorted(sos_sources(res_files()).items()):
        rows = sos_rows(d, k)
        if rows:
            n += merge(os.path.join(SCRIPT, "sos", k + ".tsv"), rows, a.force)
    elf = open(ELF, "rb").read()
    assert hashlib.sha1(elf).hexdigest() == open(os.path.join(ROOT, "eboot.sha1")).read().split()[0], \
        "work/eboot.elf is not the pinned decrypted EBOOT (docs/re/script.md §EBOOT)"
    text, other = eboot_rows(elf)
    n += merge(os.path.join(SCRIPT, "eboot.tsv"), text, a.force)
    n += merge(os.path.join(SCRIPT, "eboot_nontext.tsv"), other, a.force)
    _, _, mx, _, title = sfo.read(build.read_iso_file(build.ROM, SFO))["TITLE"]
    n += merge(os.path.join(SCRIPT, "sfo.tsv"), [dict(id="TITLE", kind="utf-8", max=str(mx - 1), jp=title)], a.force)
    print(n, "files written")


if __name__ == "__main__":
    main()
