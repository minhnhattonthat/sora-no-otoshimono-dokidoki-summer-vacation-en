"""Build build/sora_en.iso from the pinned dump.

    python -X utf8 build.py [--out build/sora_en.iso] [--marker] [--qa ID=TEXT ...]

Steps: check the dump (rom.sha1) -> text from script/ (en column; empty en keeps the original bytes) into every SOS
copy (sos.build), the EBOOT strings (in place) and PARAM.SFO; English glyphs into both HG_G18.TFP copies (font.py);
the VWF patch (vwf.py) into the EBOOT, re-signed by tools/sign.py -> repack res.ptd (ptd.repack) -> swap the files
into a copy of the ISO (iso9660.patch). build(out, {}) alone is byte-identical to the dump (tests/test_identity.py).
  --marker      every text row becomes "[id] ..." filler (phase 5 marker build; docs/re/script.md §Marker)
  --qa ID=TEXT  override one row (\\n = new line), for width probes; repeatable
"""
import argparse, hashlib, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_rom, iso9660, ptd  # noqa: E402

ROM = os.path.join(ROOT, "rom", "Sora no Otoshimono - DokiDoki Summer Vacation (Japan).iso")
RES = "/PSP_GAME/USRDIR/res/res.ptd"
EBOOT = "/PSP_GAME/SYSDIR/EBOOT.BIN"
SFO = "/PSP_GAME/PARAM.SFO"
FILLER = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs."


def read_iso_file(iso, path):
    with open(iso, "rb") as f:
        lba, size = next((lba, ln) for p, lba, ln, _ in iso9660.listing(f) if p == path)
        f.seek(lba * 2048)
        return f.read(size)


def build(out, repl, files=None):
    """repl: {work/res-relative path: uncompressed bytes}; files: {other ISO path: bytes} (EBOOT, PARAM.SFO)."""
    res = read_iso_file(ROM, RES)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    iso9660.patch(ROM, out, {RES: ptd.repack(res, repl), **(files or {})})


def eboot_marker(name, jp, n, tail=""):
    """One '[name] filler' line per Japanese line, all in n bytes (ASCII), keeping a trailing control code."""
    k = jp.count("\n") + 1
    room = (n - len(tail) - (k - 1)) // k
    return "\n".join(fill(f"[{name}]" if i == 0 else f"{i + 1}:", 391)[:room] for i in range(k)) + tail


def text_for(r, mode, qa):
    """The new text of a row, or None to keep the original bytes."""
    import script
    if r["id"] in qa:
        return qa[r["id"]]
    if mode == "marker":
        return None  # each caller builds its own marker (it knows the room)
    return script.unesc(r["en"]) if r["en"] else None


def fill(head, px):
    """head + filler words, as long as fits in px (font.width)."""
    import font
    out = head
    for w in FILLER.split():
        if font.width(out + " " + w) > px:
            break
        out += " " + w
    return out


def sos_marker(r, jp):
    """One full-width marker line per Japanese line (dialogue box: 391 px, docs/re/script.md §Width); the first
    starts with the id. Choices: the id and two words."""
    if r["kind"] == "choice":
        return fill(f"[{r['id']}]", 120)
    n = jp.count("\n") + 1
    return "\n".join(fill(f"[{r['id']}]" if i == 0 else f"{i + 1}:", 391) for i in range(n))


def texts(mode=None, qa=None):
    """(repl, files) for build(): every script/ row with new text, re-encoded the way script.py extracted it."""
    import eboot, script, sfo, sos, sign
    qa = qa or {}
    seen = set()
    res = script.res_files()
    repl = {}
    for k, d in sorted(script.sos_sources(res).items()):
        tsv = os.path.join(script.SCRIPT, "sos", k + ".tsv")
        if not os.path.exists(tsv):
            continue
        slot = {r["id"]: r["slot"] for r in script.sos_rows(d, k)}
        new = {}
        for r in script.read_tsv(tsv):
            t = text_for(r, mode, qa)
            if t is None and mode == "marker":
                t = sos_marker(r, script.unesc(r["jp"]))
            if t is not None:
                seen.add(r["id"])
                new[slot[r["id"]]] = script.sos_encode(r["kind"], t)
        if new:
            b = sos.build(d, new)
            for p in res:
                if p.endswith(".SOS") and script.sos_key(p) == k:
                    repl[p] = b
    import font, vwf
    tfp, widths = None, None
    for p in res:
        if p.endswith("/HG_G18.TFP"):
            tfp, widths = font.patch(res[p])
            repl[p] = tfp
    files = {}
    elf = bytearray(open(script.ELF, "rb").read()[:sign.ELF_SIZE])
    for i, r in enumerate(script.read_tsv(os.path.join(script.SCRIPT, "eboot.tsv"))):
        t = text_for(r, mode, qa)
        jp = script.unesc(r["jp"])
        tail = "/K" if jp.endswith("/K") else ""
        if t is None and mode == "marker":
            t = eboot_marker(r["id"][3:], jp, int(r["max"]), tail)  # 088C07B4 -> [C07B4]
        if t is None:
            continue
        seen.add(r["id"])
        b, n = script.eboot_encode(r["kind"], t), int(r["max"])
        if len(b) > n and r["id"] in qa:  # width probe only: clobbers the strings after the slot
            print(f"WARN --qa {r['id']}: {len(b)} bytes > max {n}, overwriting what follows (probe build only)")
        else:
            assert len(b) <= n, f"{r['id']}: {len(b)} bytes > max {n}"
        assert not tail or t.endswith(tail), f"{r['id']}: lost the {tail} control code"
        o = eboot.ram2off(elf, int(r["id"], 16))
        old = len(script.eboot_encode(r["kind"], jp))
        elf[o:o + max(len(b), old) + 1] = b.ljust(max(len(b), old) + 1, b"\0")
    files[EBOOT] = sign.sign(vwf.apply(bytes(elf), widths))
    r = script.read_tsv(os.path.join(script.SCRIPT, "sfo.tsv"))[0]
    t = text_for(r, mode, qa)
    if t is None and mode == "marker":
        t = "[TITLE] Sora no Otoshimono"
    if t is not None:
        seen.add(r["id"])
        files[SFO] = sfo.set_str(read_iso_file(ROM, SFO), "TITLE", t)
    assert set(qa) <= seen, f"--qa ids not found: {sorted(set(qa) - seen)}"
    return repl, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "sora_en.iso"))
    ap.add_argument("--marker", action="store_true")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT")
    a = ap.parse_args()
    check_rom.check()
    import script
    qa = dict(q.split("=", 1) for q in a.qa)
    build(a.out, *texts("marker" if a.marker else None, {k: script.unesc(v) for k, v in qa.items()}))
    with open(a.out, "rb") as f:
        print(a.out, hashlib.file_digest(f, "sha1").hexdigest())


if __name__ == "__main__":
    main()
