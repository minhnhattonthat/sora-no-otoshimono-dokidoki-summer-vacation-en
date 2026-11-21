# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7. Insert, fit, check next (phase 6 translation done). Last good build: 2026-11-22 pilot
  build/sora_en.iso (SC00000 pilot English only), sha1 a98ee044..., prologue shots work/qa/pilot. A full-English
  build currently stops at the helpbar byte assert (088F3E3C 35 > 27 bytes): phase 7 repoints those slots.
- **Done:**
  - Step 0: ROM pinned (`rom.sha1`), PPSSPP v1.20.4 in `tools/ppsspp/`, PPSSPPHeadless qa-1 shared install, smoke boots
    the original ISO, pre-commit runs `tools/check.py`, guard hook blocks `sed -i`, rulings D1-D7 in docs/decisions.md.
  - Phase 1 recon (docs/re/ptd.md, script.md, graphics.md): PETA/YKLZ/SOS formats, `tools/unpack.py`, `tools/sos.py`
    (414 SOS byte-identical), graphics survey of all 1701 GIMs. Regenerate work/ with
    `python -X utf8 tools/unpack.py && python -X utf8 tools/gimsurvey.py`.
  - Phase 2 (docs/re/debug.md): `tools/debug/warp.py --all` reaches all 48 rows of `tools/debug/scenes.tsv` from a
    cold boot with mode:scene asserts and shots (work/qa/warp/<name>/, states in work/states/). Route steps
    `cheat:NAME` and `until:M:S:LIMIT[:KEYS]`. Communication mode: cheat `hexdone` (Hexcite tutorial-seen bit) ->
    real matches, forced win, card hand, card use, event, param-up; cheats `params`/`noturns`/`lastchapter` +
    `chapterend` (scene-request poke) -> level-up banner, game over (bad ending sc90020 + retry prompt), ending
    sc90010 + staff roll (row `credits`, state at the roll's start). Scene jump table mapped (0x088C928C).
    `tools/debug/mips.py` = EBOOT disasm/xref/case lookup.
  - Save editor `tools/debug/save.py make|check` verified with `unlock_all` (loads via Continue, gallery 100%).
  - Phase 3: `ptd.repack` (offset-order layout, 2048/16 alignment, TOC rewrite + re-obfuscation, nested PTDs by
    work/res path) and `build.py` (check_rom -> repack res.ptd -> iso9660.patch). tests/test_identity.py: every PTD
    and the whole ISO rebuild byte-identical; an edit test grows a YKLZ file and a nested file and checks the rest.
    `build.build(out, repl)` takes `{work/res path: bytes}`, the hook for phase 7 inserts.
  - Phase 4 (docs/re/script.md §Bytecode, §EBOOT, §Extract): `tools/script.py dump` -> script/sos (395 TSV, 6614
    msg + 88 choice + 5 msg_nonl rows, speaker column from bytecode), script/eboot.tsv (137 shown strings: help lines,
    Hexcite reactions with `/K`, save dialogs UTF-8), eboot_nontext.tsv (687 classified), sfo.tsv (XMB title).
    Decrypted EBOOT: `tools/dump_eboot.py` -> work/eboot.elf, pinned in `eboot.sha1`. tests/test_script.py:
    TSV re-encodes byte-identically (all SOS rebuild, EBOOT bytes match), every pool slot / scan hit covered.
  - Phase 5 (docs/re/script.md §Font, §VWF, §Dialogue box width, §Control codes, §Marker build): build.py inserts
    script/ (en column; SOS per copy, EBOOT in place, SFO), `--marker`, `--qa ID=TEXT` probes. tools/font.py: Open Sans
    Semibold 14 px ASCII glyphs (fonts/, Apache 2.0) into both HG_G18.TFP copies. tools/vwf.py: one-byte advance
    from a width table (layout 0x08817E64 + draw 0x08818B50 -> helper 0x088EA3A0), 4 relocations appended.
    tools/sign.py: sign_np -elf (WSL gcc build, tag 0xD91612F0 = original). yklz.pack fixed: no overlapping refs
    (game memcpys them; it ate font pixels). Marker tour `warp.py --all` 48/48 ok (work/qa/marker/tour).
    Width gate in tools/boxes.tsv: dialogue/help/Hexcite reaction 391 px x 3 lines, choice 300 px x 1,
    Hexcite help bar 464 px x 1; torture line renders (work/qa/width/vwf3).
  - Phase 6: script/ fully translated (6835/6840; the 5 left are full-width-space pause boxes that keep their bytes).
    tools/batches.py (split/check/merge, lint in tools/check.py: ASCII, no `/` but the trailing `/K`, glossary rows,
    honorific regexes, wrapped width per tools/boxes.tsv, EBOOT byte max), tools/fit.py (word-wrap; build.py wraps
    every dialogue-box string with it, translators write one paragraph per box), tools/pairs.py (review files).
    Docs: glossary.md, docs/synopsis.md, docs/style-reference.md, docs/translator-brief.md, docs/reviewer-brief.md.
    51 batches (work/tl, gitignored) by 11 translator agents; every batch reviewed, all Critical/Important fixed
    (fix001-fix007); Minors in docs/polish.md (polish pass before release).
- **Next:**
  1. Phase 7: Hexcite help-bar strings (088F3E3C..088F3EA8) have 27-43-byte slots and the English is longer:
     repoint into free space (more CRI error strings near 0x088EA4B0+, add relocations like vwf.py). EBOOT `max` for
     free-standing strings is a guess until xrefs are checked (lint uses it). Then build green, romdiff ranges, smoke.
  2. Phase 8 QA: warp tour on the English build; check wrapped 3-line boxes, choices (300 px), Hexcite /K reactions.
- **Known gaps (non-blocking):** Free Mode Hexcite ES is greyed (unlock flag not found; its text is shared with
  Hexcite). Poke-jumped chapter/ending scripts keep the previous screen's overlay drawn; the scripts themselves are
  shot clean by the ev_* / ending_* script-warp rows.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: the signed EBOOT and the VWF code (in .rodata, relocated)
  are only tested in PPSSPP; a boot on a real PSP/Vita before release would confirm them. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
