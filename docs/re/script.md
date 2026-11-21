# Script text (SOS) - verified

414 SOS files (403 in RES/SCRIPT/SC + 11 duplicates in __PACK__/SUBSCRIPT.PTD). tools/sos.py parses and rebuilds;
`sos.build(d)` with no edits is byte-identical for all 414 (identity test).

## Layout (u32 LE)
| off | field |
|---|---|
| 0x00 | magic 0x68744c87 |
| 0x04 | 2 |
| 0x0C | file size |
| 0x10 | table_off (0x140): (u16 kind, u16 arg) pairs |
| 0x14 | code_off: bytecode; references strings by index (e.g. `5c 01 00` = string 1) |
| 0x18 | pool_off (also at 0x24) |
| 0x1C | msgtab_off: u16 pool offset per message index (dialogue lines) |
| 0x20 | strtab_off: u16 pool offset per string index (speaker names, choice text, resource paths, .adv jumps) |
| 0x28 | u16 table_size, code_size, pool_size, n_msgs, n_strs, 1 |
| 0x40 | 256-byte S-box |

Pool: NUL-terminated strings, deduplicated, obfuscated: plain = sbox[enc ^ (-(i - pool_off) & 0xff)] (i = file offset).
Rebuild = rewrite pool + both u16 offset tables + size fields (0x0C, 0x2C). Pool offsets are u16: pool < 64 KiB per file
(largest original pool: check in phase 4).

## Text
- Encoding Shift-JIS (cp932); line break `\n` (0x0A); every message ends with `\n`. No control codes found in 7813
  text slots (5932 unique, ~139k chars). Speaker names are separate strings (守形, 智樹, そはら, ニンフ, イカロス, 美香子 ...).
- Max line ~22-23 full-width chars, 1-3 lines (3 = rare). Box width to measure in the marker build (phase 5).
- Non-text slots: resource paths (`..\..\..\img\bg\bg030a.tm2`, `.ogg`, `.anm`, `.adv`), label `TUTORIAL_REPLAY`.
  `sos.is_text()` separates them.

## Font
- RES/1ST/HG_G18.TFP: `T2FP`, 8076 glyphs 18x18 4bpp (162 bytes each), u16 code table at 0x20 (ASCII 0x00.. then
  Shift-JIS), glyph data from 0x3f78. DEBUGFNT.TFP: 12x12 debug font. Whether the renderer is fixed-pitch: phase 5.

## Other text sources
- EBOOT (needs decrypted ELF + re-sign): ~120 displayed strings found in the RAM image (tools/jpfilter.py over
  jpscan.py): menu help lines at 0x088c07b4.. (fixed 0x100 slots), Hexcite card-game reactions with `/K` code at
  0x088dcad0.. (0xC4 slots), save-dialog messages in UTF-8 at 0x088fb8e7.. (sceUtility dialogs), save title/detail
  strings (UTF-8) at 0x088f161c... Strings at 0x088f26b0+ are internal layout names (not shown).
- FSB (FSCN layout) / FAB files: only internal Japanese object names; not displayed (guess: verify in marker build).
