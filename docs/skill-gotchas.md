# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/emulator-qa.md (§emu.py, PPSSPP): `emu.py --mash` is ignored for PSP: psp.py never reads MASH, so a mashed route just idles. This repo uses `tools/debug/drive.py --mash circle`.
- references/emulator-qa.md (§Debug tool, PPSSPP): `memory.breakpoint.add {write: true}` never stopped PPSSPPHeadless qa-1 on a store the game makes (savedata param dataBuf); RAM diffs and cheat databases found the fields instead.
- references/emulator-qa.md (§Debug tool): CWCheat codes from a real PSP can address a heap object at a different base than PPSSPP (here 0x08EC0000 on PSP vs 0x09EC0000 in PPSSPP, +0x01000000); find the object by a known field and keep the cheat's offsets.
- references/platform-psp.md (save data): PPSSPP stores sceUtility savedata encrypted when the game asks for it; edit the plaintext copy in RAM and let the game save, rather than the .SAV file.
- references/emulator-qa.md (§emu.py): context-mode trims Read/Bash output of skill reference files and disassembly above ~4 KB even in the main thread; read with offset/limit.
