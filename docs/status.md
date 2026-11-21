# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (warp 35 scenes + save editor done; Communication-mode card/level scenes,
  credits, game over left). Last build: none yet.
- **Done:**
  - Step 0: ROM pinned (`rom.sha1`), PPSSPP v1.20.4 in `tools/ppsspp/`, PPSSPPHeadless qa-1 shared install, smoke boots
    the original ISO, pre-commit runs `tools/check.py`, guard hook blocks `sed -i`, rulings D1-D7 in docs/decisions.md.
  - Phase 1 recon (docs/re/ptd.md, script.md, graphics.md): PETA/YKLZ/SOS formats, `tools/unpack.py`, `tools/sos.py`
    (414 SOS byte-identical), graphics survey of all 1701 GIMs. Regenerate work/ with
    `python -X utf8 tools/unpack.py && python -X utf8 tools/gimsurvey.py`.
  - Phase 2 (docs/re/debug.md): scene ids, script warp (`--scene sc:<file>`), `tools/debug/warp.py --all` reaches all
    35 rows of `tools/debug/scenes.tsv` from a cold boot with mode:scene asserts and shots (work/qa/warp/<name>/,
    states in work/states/). New this session: route step `cheat:NAME` (mid-route pokes), cheat `hexend` + row
    `free_win` (Free Mode Hexcite forced win -> winner's post-match line, verified); Hexcite score/piece fields mapped.
  - Save editor `tools/debug/save.py make|check` (RAM pokes at the hub, then the game's own Menu -> Save): verified
    with `unlock_all` (work/saves/unlock_all/ULJM05639SoraOto): loads via Continue with no corruption dialog, gallery
    100%.
- **Next (phase 2 done-when):**
  1. Communication-mode first Hexcite is a guided tutorial that ignores pokes; steps 1-2 solved, step 3 not (moves in
     docs/re/debug.md). Finish it (or find the tutorial-done flag / card inventory field: start at the dispatcher
     0x08836420.. and GAME+0x3E90), then one forced win (cheat `hexend`) -> card get; save that with `save.py make`
     as the base for: use-card screen, level-up dialog (res/commu/10_levelup), game over. Add those rows.
  2. Credits: a warped ending (sc9) returns to the tutorial, no staff roll; find the credits mode:scene (setScene
     callers, 0x881EFE0 xref) or the ending flag.
  3. Cheap rows still missing: Options sub-screens, hub Menu -> Controls (そうさせつめい), Free Mode Hexcite ES,
     special-move cut-ins (tech cards: CWCheat +0x408.. counts).
  4. Then phase 3 identity build.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
