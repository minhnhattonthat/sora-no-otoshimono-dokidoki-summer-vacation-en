# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build next (phase 4 extract done). Last build: 2026-11-22 build/sora_en.iso,
  no edits, sha1 a82a8661... = dump, smoke ok.
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
- **Next:**
  1. Phase 5 marker build: build.py inserts script/ (SOS via sos.build per copy incl. SUBSCRIPT.PTD; EBOOT strings
     in place -> needs a re-signed ~PSP EBOOT: find a signer, e.g. sign_np; PARAM.SFO), every row -> `[id]` marker.
     Font: HG_G18.TFP 18x18 (fixed-pitch? VWF?); measure dialogue box / choice / help-line / Hexcite-reaction widths.
     Confirm: speaker strings are nameplate keys (leave JP), FSB/FAB names not shown, `/K` meaning.
- **Known gaps (non-blocking):** Free Mode Hexcite ES is greyed (unlock flag not found; its text is shared with
  Hexcite). Poke-jumped chapter/ending scripts keep the previous screen's overlay drawn; the scripts themselves are
  shot clean by the ev_* / ending_* script-warp rows.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
