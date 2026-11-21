# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (text/format recon done; graphics-text survey partly done). Last build: none yet.
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
  - Graphics: `tools/gimsurvey.py` decodes all 1701 unique GIMs to work/gimpng with sheets; surveyed COMMON_0,
    10_TITLE, 00_NAME, 10_PARAMETER_0, XMB, PARAM.SFO (docs/re/graphics.md).
- **Next:** finish the graphics survey: open each remaining sheet listed in docs/re/graphics.md "Not yet surveyed"
  (regenerate with `python -X utf8 tools/unpack.py && python -X utf8 tools/gimsurvey.py` if work/ is gone), add rows,
  then phase 1 is done -> phase 2 (debug tool: PPSSPP has no Lua; warp by RAM poke via psp.py WebSocket or CWCheat).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
