"""Release: build -> tests -> smoke -> jp_left -> qa_gate (every work/qa/**/manifest.tsv) -> textcover -> polish.md ->
README placeholders -> debug off -> xdelta3 patch -> re-apply + compare -> zip. Stops at the first failure.

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-build]

Out: release/Sora_no_Otoshimono_DokiDoki_Summer_Vacation_EN_v<ver>.zip (patch + README.txt, ZIP_STORED) next to the
.xdelta; the playable image stays in build/sora_en.iso. Refuses to overwrite an existing version without --force.
--skip-build reuses build/sora_en.iso when it is newer than every script/ and gfx/out/ file (else it rebuilds).
"""
import argparse, glob, hashlib, os, re, shutil, subprocess, sys, zipfile, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
from skill import SKILL  # noqa: E402

PY = [sys.executable, "-X", "utf8"]
ISO = os.path.join(ROOT, "build", "sora_en.iso")
NAME = "Sora_no_Otoshimono_DokiDoki_Summer_Vacation_EN_v{}"
REL = os.path.join(ROOT, "release")
JPSCAN = os.path.join(ROOT, "work", "release", "jpscan")
# Japanese a build may keep: EBOOT strings classified non-text (script/eboot_nontext.tsv, never shown) are skipped by
# scanning only shown-text slots; SOS pools after translation hold none. Offsets listed here are reviewed keeps.
KNOWN = os.path.join(ROOT, "docs", "jp_known.txt")


def run(step, cmd, **kw):
    print(f"== {step}: {' '.join(map(str, cmd))}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, **kw)
    if r.returncode:
        sys.exit(f"release stopped: {step} failed (exit {r.returncode})")
    return r


def hashes(path):
    md5, sha1, crc, n = hashlib.md5(), hashlib.sha1(), 0, 0
    with open(path, "rb") as f:
        while b := f.read(1 << 24):
            md5.update(b); sha1.update(b); crc = zlib.crc32(b, crc); n += len(b)
    return {"size": n, "crc32": f"{crc:08X}", "md5": md5.hexdigest(), "sha1": sha1.hexdigest()}


def stale():
    if not os.path.exists(ISO):
        return True
    t = os.path.getmtime(ISO)
    src = glob.glob(os.path.join(ROOT, "script", "**", "*.tsv"), recursive=True)
    src += glob.glob(os.path.join(ROOT, "gfx", "out", "**", "*.*"), recursive=True)
    return any(os.path.getmtime(p) > t for p in src)


def jp_left(repl, elf):
    """Scan what the build writes: the message/choice slots of every built SOS (the pool is obfuscated on disc, so
    scan it decoded; speaker names are name-plate keys, never drawn as text) and the plain EBOOT's shown-text slots."""
    import eboot, script, sos
    shutil.rmtree(JPSCAN, ignore_errors=True)
    os.makedirs(JPSCAN)
    n, pool = 0, bytearray()
    for p, b in sorted(repl.items()):
        if p.endswith(".SOS"):
            n += 1
            info = sos.parse(b)
            for o in sorted(set(info["moffs"])):  # message/choice slots; speaker slots (soffs) are name-plate keys
                pool += info["slots"][o] + b"\0"
    with open(os.path.join(JPSCAN, "sos_text.bin"), "wb") as f:
        f.write(pool)
    with open(os.path.join(JPSCAN, "slots.txt"), "w") as f:  # shown-text slots: "SLOT TARGET" = file offset twice
        for r in script.read_tsv(os.path.join(script.SCRIPT, "eboot.tsv")):
            o = eboot.ram2off(elf, int(r["id"], 16))
            f.write(f"{o:X} {o:X}\n")
    with open(os.path.join(JPSCAN, "EBOOT.elf"), "wb") as f:
        f.write(elf)
    known = ["--known", KNOWN] if os.path.exists(KNOWN) else []
    jl = [*PY, os.path.join(SKILL, "scripts", "jp_left.py")]
    run("jp_left SOS", [*jl, os.path.join(JPSCAN, "sos_text.bin"), "--sjis", *known])
    run("jp_left EBOOT", [*jl, os.path.join(JPSCAN, "EBOOT.elf"), "--sjis", "--slots",
                          os.path.join(JPSCAN, "slots.txt"), *known])
    print(f"jp_left: {n} SOS + EBOOT clean")


def debug_off(repl, elf):
    """The game ships no debug code of ours (warp/cheat tools poke RAM from the emulator), so the release build must
    simply be the plain one: no --marker/--qa probe text in the EBOOT or any SOS."""
    marker = re.compile(rb"\[[0-9A-F]{5}\]|\[SC\d{5}\.")
    bad = [p for p, b in repl.items() if p.endswith(".SOS") and marker.search(b)]
    assert not bad and not marker.search(bytes(elf)), f"marker/probe text in the release build: {bad[:5]}"
    print("debug off: plain build, no marker or probe text")


def readme_zip(orig, built, patch):
    return f"""Sora no Otoshimono: DokiDoki Summer Vacation - English patch v{VERSION}
Unofficial fan translation. No game data included: you need your own dump of the Japanese PSP game.
Project page and bug reports: https://github.com/minhnhattonthat/sora-no-otoshimono-dokidoki-summer-vacation-en

BASE IMAGE (Redump: Sora no Otoshimono - DokiDoki Summer Vacation (Japan), ULJM05639)
  Size   {orig['size']} bytes
  CRC32  {orig['crc32']}
  MD5    {orig['md5']}
  SHA-1  {orig['sha1']}
The patch only applies to this exact, unmodified ISO.

PATCHING
  xdelta3:  xdelta3 -d -s "Sora no Otoshimono - DokiDoki Summer Vacation (Japan).iso" {os.path.basename(patch)} sora_en.iso
  GUI:      Delta Patcher (Windows/Linux/macOS) or the online patcher at https://www.marcrobledo.com/RomPatcher.js/
Patched ISO: {built['size']} bytes, CRC32 {built['crc32']}, SHA-1 {built['sha1']}

PLAYING
  Tested in PPSSPP (v1.20). Start from a fresh boot; savestates made with another build keep the old text and code.
  Saves from the Japanese game load fine. Real PSP/PS Vita: not tested yet (the EBOOT is re-signed, ~PSP format).

TRANSLATED
  All dialogue, menus, help lines, Hexcite reactions, save dialogs, graphics with text (title menu, cards,
  profiles, gallery, Hexcite, tutorials, banners, staff roll) and the XMB title/icon.
  Left in Japanese: the kana title logo, company logos and copyright notices. Voices are Japanese.

KNOWN ISSUES
  None known. Report bugs on the project page (a savestate helps).

CREDITS
  Translation, tools and graphics: minhnhattonthat, with extensive AI assistance (Claude by Anthropic).
  Font: Open Sans (Apache 2.0). Original game (c) Kadokawa Shoten. This is an unofficial fan project, not
  affiliated with Kadokawa. Do not share pre-patched ISOs.
"""


def main():
    global VERSION
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's release files")
    ap.add_argument("--skip-build", action="store_true")
    a = ap.parse_args()
    VERSION = a.version
    name = NAME.format(a.version)
    patch, zpath = os.path.join(REL, name + ".xdelta"), os.path.join(REL, name + ".zip")
    if not a.force and (os.path.exists(patch) or os.path.exists(zpath)):
        sys.exit(f"{zpath} exists: pass --force to overwrite v{a.version}, or bump --version")
    import check_rom
    check_rom.check()
    orig = os.path.join(ROOT, "rom", "Sora no Otoshimono - DokiDoki Summer Vacation (Japan).iso")
    if a.skip_build and not stale():
        print("== build: reusing", ISO)
    else:
        run("build", [*PY, "build.py"])
    run("tests", [*PY, os.path.join("tools", "check.py")])
    run("smoke", [*PY, os.path.join(SKILL, "scripts", "emu.py"), ISO, "--out", "work/qa/smoke",
                  "--route", "tools/routes/boot.txt", "--smoke"])
    import build
    repl, _ = build.texts(None, {})  # what build.py wrote, for the scans below
    elf = build.eboot_strings()[0]
    jp_left(repl, elf)
    qg = [*PY, os.path.join(SKILL, "scripts", "qa_gate.py")]
    mans = sorted(glob.glob(os.path.join(ROOT, "work", "qa", "**", "manifest.tsv"), recursive=True))
    assert mans, "no work/qa/**/manifest.tsv"
    for m in mans:
        run(f"qa_gate {os.path.relpath(m, ROOT)}", [*qg, "check", m, os.path.join(os.path.dirname(m), "verdicts")])
    run("textcover", [*PY, os.path.join(SKILL, "scripts", "textcover.py"), "work/qa/cover",
                      "work/qa/cover/strings.tsv", "--waive", "docs/text_unshown.tsv"])
    open_lines = [l for l in open(os.path.join(ROOT, "docs", "polish.md"), encoding="utf-8") if l.startswith("- [ ]")]
    assert not open_lines, f"docs/polish.md has {len(open_lines)} unticked lines"
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    ph = re.findall(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|game|ext)>|<[A-Z][a-z]+ [^>]*>", readme)
    assert not ph, f"README.md template placeholders: {ph[:5]}"
    debug_off(repl, elf)
    os.makedirs(REL, exist_ok=True)
    o, b = hashes(orig), hashes(ISO)
    if os.path.exists(patch):
        os.remove(patch)
    # -S none: no secondary compressor, so web/GUI patchers (RomPatcher.js) can apply it too
    run("patch", ["xdelta3", "-e", "-9", "-S", "none", "-B", str(o["size"]), "-s", orig, ISO, patch])
    check = os.path.join(ROOT, "work", "release", "reapplied.iso")
    if os.path.exists(check):
        os.remove(check)
    run("re-apply", ["xdelta3", "-d", "-s", orig, patch, check])  # exactly the README's command
    got = hashes(check)
    os.remove(check)
    assert got["sha1"] == b["sha1"], f"re-applied patch gives {got['sha1']}, build is {b['sha1']}"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        z.write(patch, os.path.basename(patch))
        z.writestr("README.txt", readme_zip(o, b, patch).replace("\n", "\r\n"))
    print(f"release: {zpath} ({os.path.getsize(patch)} B patch); build sha1 {b['sha1']}")


if __name__ == "__main__":
    main()
