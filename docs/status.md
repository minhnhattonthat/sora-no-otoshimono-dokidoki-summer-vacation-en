# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (warp + 34-scene list done; save editor, credits, level-up/game over left).
  Last build: none yet.
- **Done:**
  - Step 0: ROM pinned (`rom.sha1`), PPSSPP v1.20.4 in `tools/ppsspp/`, PPSSPPHeadless qa-1 shared install, smoke boots
    the original ISO, pre-commit runs `tools/check.py`, guard hook blocks `sed -i`, rulings D1-D7 in docs/decisions.md.
  - Phase 1 recon (docs/re/ptd.md, script.md, graphics.md): PETA/YKLZ/SOS formats, `tools/unpack.py`, `tools/sos.py`
    (414 SOS byte-identical), graphics survey of all 1701 GIMs. Regenerate work/ with
    `python -X utf8 tools/unpack.py && python -X utf8 tools/gimsurvey.py`.
  - Phase 2 so far (docs/re/debug.md): scene ids (u32 mode 0x088FD1D8, scene 0x088FD1D4); script warp by poking the
    new-game literal 0x088F4974 (`--scene sc:sc1/sc10000.sos` reaches any SOS); hub via sc_end + tutorial skip;
    game-state object 0x09EC0000 = CWCheat object at 0x08EC0000 (+0x01000000), gallery/dress-up/profile unlock cheat
    verified. `tools/debug/warp.py --all` reaches all 34 rows of `tools/debug/scenes.tsv` from a cold boot, each
    asserted by mode:scene with a shot (work/qa/warp/<name>/, states in work/states/, ~20 min); tests/test_scenes.py
    lints the list. `tools/debug/drive.py`: mash/peek/poke driver (emu.py --mash does nothing on PSP).
- **Next (phase 2 done-when):**
  1. Save editor `tools/debug/save.py`: IKAROS.SAV is encrypted, so edit RAM (GAME object) at the hub, then hub Menu
     (row hub_menu, 5:38: Options / Save / Controls / Title) -> Save, keep `<out>/memstick/PSP/SAVEDATA/ULJM05639SoraOto`
     in work/saves/<name>/; test: boot with that save (`--sav`), title -> Communication Mode -> Continue, gallery 100%,
     no "corrupted" dialog. Map level / cards-left / parameters / card inventory in GAME (candidates in debug.md;
     pokes at the hub did not redraw the HUD, re-enter the hub to test).
  2. Scenes still missing: credits (a warped ending returns to the tutorial, no staff roll: find the credits
     mode:scene or the ending flag), level-up dialog (res/commu/10_levelup), card get / use-card screens, game over,
     Hexcite ES, Hexcite result + special-move cut-ins (needs a Hexcite win: poke scores or an auto-player; the
     Communication-mode first match forces a guided move), Options sub-screens, Menu -> Controls.
  3. Then phase 3 identity build.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
