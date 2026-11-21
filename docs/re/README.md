# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise. RAM addresses are from `tools/pspdbg.py` RAM
images (module ULJM05639_Sora-Oto_PSP loaded at 0x08804000).

| File | Covers | State |
|---|---|---|
| ptd.md | ISO layout, PETA archives, YKLZ compression, free space | verified (unpack + roundtrip) |
| script.md | SOS script format, text encoding, font, EBOOT strings | verified (identity rebuild of all 414 SOS) |
| graphics.md | graphics-text survey (GIM textures, XMB images) | complete (all 58 sheets read by eye) |

Prior work: none for this game (no fan patch found, 2026-11). Mirai Nikki 13th Diary Holder (same engine) has a
`.ptd` unpacker (github.com/rzhumen88/ptd-unpacker) that gave the TOC deobfuscation.
