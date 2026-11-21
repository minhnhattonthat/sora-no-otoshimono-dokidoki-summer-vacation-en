# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool, not started (phase 1 recon done 2026-11-22). Last build: none yet.
- **Done:**
  - Step 0: ROM pinned (`rom.sha1`), PPSSPP v1.20.4 in `tools/ppsspp/`, PPSSPPHeadless qa-1 shared install, smoke boots
    the original ISO (route `tools/routes/boot.txt`, circle input changes screen), pre-commit runs `tools/check.py`
    (failing test rejected), guard hook blocks `sed -i`, rulings D1-D7 in docs/decisions.md.
  - Recon (docs/re/ptd.md, script.md): PETA archive TOC deobfuscation, YKLZ LZ format (RE'd from the EBOOT RAM image),
    SOS script format; `tools/unpack.py` unpacks res.ptd + nested PTDs into work/res; `tools/sos.py` parses and
    rebuilds all 414 SOS byte-identically. Text = Shift-JIS, `\n` breaks, no control codes, ~5.9k unique lines.
    EBOOT has ~120 displayed strings (menu help, Hexcite reactions with `/K`, UTF-8 save dialogs) -> needs decrypted
    ELF + re-sign later (headless PPSSPP ignored DumpFileTypes; use the windowed tools/ppsspp with
    memstick/PSP/SYSTEM/ppsspp.ini `[General] DumpFileTypes = 7`).
  - Graphics survey complete (docs/re/graphics.md): all 58 sheets of the 1701 unique GIMs read; ~70 rows. Big redraw
    groups: card names (505-674), character profiles (752-775), both tutorials (814-819, 1265-1289, 1313-1316),
    credits (837-868, 910-926, 941-942), Hexcite special cut-ins (1155-1229, per-glyph animation frames), result
    animations (1055-1066, 1131-1154). Regenerate sheets with
    `python -X utf8 tools/unpack.py && python -X utf8 tools/gimsurvey.py` if work/ is gone.
- **Next:** phase 2 debug tool (`references/emulator-qa.md` §Debug tool). PPSSPP has no Lua: warp by RAM poke over
  psp.py WebSocket (tools/pspdbg.py already reads RAM; module at 0x08804000) or CWCheat. Find the scene/script
  variable (current .SOS / .adv jump target), story flags, communication level, card inventory, Hexcite unlocks;
  build `tools/debug/warp.py --scene <name>` with a scene list (title, communication mode, each chapter, Hexcite,
  card gallery, profiles, tutorials, each ending A/B/C + credits, game over), and a save editor.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
