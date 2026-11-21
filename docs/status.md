# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build next (phase 2 debug tool done: 48 warp rows incl. cards, level-up, game over,
  credits, clear-data prompt). Last build: none yet.
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
- **Next:**
  1. Phase 3 identity build: unpack -> repack the ISO with no edits, byte-identical, as a test (`build.py`).
  2. Phase 4 extract (SOS scripts, PTD tables), roundtrip test.
- **Known gaps (non-blocking):** Free Mode Hexcite ES is greyed (unlock flag not found; its text is shared with
  Hexcite). Poke-jumped chapter/ending scripts keep the previous screen's overlay drawn; the scripts themselves are
  shot clean by the ev_* / ending_* script-warp rows.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
