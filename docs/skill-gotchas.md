# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/emulator-qa.md (§emu.py, PPSSPP): `emu.py --mash` is ignored for PSP: psp.py never reads MASH, so a mashed route just idles. This repo uses `tools/debug/drive.py --mash circle`.
- references/emulator-qa.md (§Debug tool, PPSSPP): `memory.breakpoint.add {write: true}` never stopped PPSSPPHeadless qa-1 on a store the game makes (savedata param dataBuf); RAM diffs and cheat databases found the fields instead.
- references/emulator-qa.md (§Debug tool): CWCheat codes from a real PSP can address a heap object at a different base than PPSSPP (here 0x08EC0000 on PSP vs 0x09EC0000 in PPSSPP, +0x01000000); find the object by a known field and keep the cheat's offsets.
- references/platform-psp.md (save data): PPSSPP stores sceUtility savedata encrypted when the game asks for it; edit the plaintext copy in RAM and let the game save, rather than the .SAV file.
- references/emulator-qa.md (§emu.py): context-mode trims Read/Bash output of skill reference files and disassembly above ~4 KB even in the main thread; read with offset/limit.
- references/platform-psp.md (save data): PPSSPP's sceUtility save dialog asks "overwrite the data?" with Yes/No side by side and the cursor on No when a save already exists (e.g. the one created at first boot); a route must press left before circle, or the save silently doesn't happen.
- scripts/disasm.py / capstone (references/platform-psp.md): capstone's MIPS disasm stops at the first undecodable word; ad-hoc scans of a PSP RAM image need md.skipdata = True or they silently cover only the first few KB.
- references/emulator-qa.md (§Debug tool): a guided in-game tutorial (here the first Communication-mode Hexcite match) can ignore RAM pokes and hang; check whether the same minigame has an unguided mode (Free Mode) for forced-result warps.
- references/emulator-qa.md (§Debug tool): faster than solving a guided tutorial by eye: find the scene-switch function's callers (jal xrefs + the a1/a2 immediates), read the case that enters the tutorial, and poke its "seen" bit (here one bit at SM+0xAA); a scene jump table indexed by scene id then maps every remaining screen (credits, game over) in an hour.
- references/emulator-qa.md (§Debug tool): poking only the scene-request field (no fade/arg fields) switches scenes cleanly from an idle menu, but the previous screen's overlay can stay drawn over the next script; shoot scripts from script warps instead.
- scripts/psp.py (references/emulator-qa.md §emu.py, PPSSPP): the docstring says each run gets a fresh OUT/memstick, but Run() never clears it, so a re-run into the same OUT boots with the previous run's saves (here New game became Continue and a warp landed on the wrong scene); clear OUT/memstick when memstick is None. Worked around in tools/debug/warp.py.
- scripts/ (scratch disasm): a helper named `dis.py` shadows the stdlib `dis` that capstone imports (circular import error); name scratch scripts something else.
- references/pipeline.md (Identity): PETA nested archives used 16-byte file alignment vs 2048 in the outer one; derive alignment per archive from the identity test, not one constant.
- references/platform-psp.md (EBOOT dump): PPSSPPHeadless (qa-1) ignores memstick/PSP/SYSTEM/ppsspp.ini, so `DumpFileTypes = 7` dumps nothing headless; run the GUI PPSSPPWindows64.exe with the ini set (this repo: tools/dump_eboot.py, ~10 s).
- references/pipeline.md (§Extract, PSP): the EBOOT carries name-substitution tokens (主人公の名前) the renderer strncmp()s and kinsoku tables in .rodata; jpscan-style filters list them as text. Restrict scans to .rodata/.data via section headers (the PRX dump keeps them) to drop .text noise.
