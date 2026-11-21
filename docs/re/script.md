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
(largest original pool 0x2bae = 11 KiB, so English has ~5x room).

## Text
- Encoding Shift-JIS (cp932); line break `\n` (0x0A); every message ends with `\n`. No control codes found in 7813
  text slots (5932 unique, ~139k chars). Speaker names are separate strings (守形, 智樹, そはら, ニンフ, イカロス, 美香子 ...).
- Max line ~22-23 full-width chars, 1-3 lines (3 = rare). English budget: 391 px x 3 lines (§Dialogue box width).
- Non-text slots: resource paths (`..\..\..\img\bg\bg030a.tm2`, `.ogg`, `.anm`, `.adv`), label `TUTORIAL_REPLAY`.
  `sos.is_text()` separates them.

## Font - verified (phase 5 shots in work/qa/width/)
- RES/1ST/HG_G18.TFP (+ a byte-identical copy in __PACK__/1ST.PTD): `T2FP`, 8076 glyphs 18x18 4bpp (162 bytes each,
  row-major, low nibble = left pixel), u16 code table at 0x20 (ASCII 0x00.. at index = code, then Shift-JIS), glyph
  data from 0x3f78. Ink levels 0-12 draw; 13 drew nothing for a fully inked stem. DEBUGFNT.TFP: 12x12 debug font.
- Stock renderer: one-byte (ASCII) characters advance size/2 = 9 px, full-width 18; the stock ASCII glyphs are ~10-16 px
  wide so they overlap. ASCII text renders (no code page issue).
- English: tools/font.py re-renders ASCII 0x20-0x7E from fonts/OpenSans-Semibold.ttf (14 px, baseline row 14,
  Apache 2.0) into both TFP copies; ~7 px per character on average.

## VWF - verified (tools/vwf.py, tests/test_vwf.py)
- Tokenizer 0x088176FC (string -> kind, code, byte count): kind 1 = one-byte char, 2 = Shift-JIS, others = control
  codes. Two consumers add the one-byte advance size*scale>>1: layout (line widths for auto-wrap) 0x08817E64 and the
  draw loop 0x08818B50 (x in 1/16 px, scale 16 = 1.0). Both now `jal` a 4-instruction helper at 0x088EA3A0 that reads
  a 256-byte px table at 0x088EA3B0 (CRI ADX error strings overwritten), and add px*scale. A third copy at 0x08818224
  only sizes the unused name-substitution token.
- The EBOOT is a relocatable PRX (type 0xFFA0): vwf.apply appends 4 relocation entries (2 x R_MIPS_26, HI16/LO16) to
  the last relocation block. Re-signed with sign_np -elf, tag 0xD91612F0 = the original's (tools/sign.py, WSL gcc).

## Dialogue box width - verified (work/qa/width/w1, w2)
- Auto-wrap (layout 0x08817DD0): before each character, if the line's width so far is >= W the engine breaks the line
  there (mid-word). W = 391 px for the dialogue box: 48 digits (384) + `''` (390) + `C` stayed on the line, 391 broke.
  So a line fits when its total width <= 391 (font.width). Lines start at x = 22.
- 3 lines per box; a 4th line (explicit or wrapped) is not shown (text lost, no paging).

## Control codes - verified (tokenizer jump table 0x088BEB10)
- `/` + one of `A C D K L N V W Z a c v w z` is a control code; `//` = a literal `/`; `/` before any other byte is
  a literal `/`. English text must write `//` for a slash before those letters (safest: always `//`).
- `%` starts a token only when followed by `name` / `family` (compared at 0x088F1864/0x088F186C); else literal.
- No SOS message uses a control code; the Hexcite reactions end with `/K` (keep it).

## Bytecode references to text - verified (every non-empty message slot in all 403 SOS is reached; tests/test_script.py)
- `40 7f u16 40` = show message u16 (dialogue box); `40 53 u16 40` just before it = speaker (strtab index).
- `5d u16 40` = choice option text (message index), right after a `40 7f u16` branch (u16 = code offset, not a msg).
- 6614 messages + 88 choice options = 6702 unique slots. Every message ends with `\n` except 5 shouts (kind
  `msg_nonl`). Speakers: 6 messages have none.
- Speaker strings are keys, not text: the EBOOT table at 0x088fb708 (智樹Ａ, 智樹Ｂ, ... ？？？) maps them to the
  nameplate GIMs (COMMON_00_NAME, graphics.md). Leave them Japanese; the player sees the redrawn plate (marker
  build: plates unchanged with every message replaced).

## EBOOT - verified (decrypted dump, roundtrip test)
- Decrypted ELF: `python -X utf8 tools/dump_eboot.py` -> work/eboot.elf, pinned by `eboot.sha1` (PPSSPP GUI with
  DumpFileTypes = 7; headless ignores the ini). Relocatable PRX: RAM = 0x08804000 + vaddr; section headers kept.
  `tools/eboot.py` scans .rodata/.data only (.text hits are instruction bytes).
- Text (script/eboot.tsv, 137): Alpha's menu help lines 0x088c07b4.. (0x100 slots, cp932, `\n` breaks); Hexcite
  post-match reactions 0x088dcad0.. (0xC4 stride, 0x80 usable, end with `/K` = a control code, keep it); Hexcite
  menu help 0x088f3e3c..; save-data title/detail and sceUtility save-dialog messages (UTF-8) 0x088f161c.., 0x088fb978..,
  .data 0x088fcc88... `max` = bytes to the next non-zero byte. Verified in phase 7 (tests/test_build.py): no .data pointer
  or lui pair in the original ELF reaches past the first byte of any written string, so the zero slack is free.
- Not text (script/eboot_nontext.tsv, 687, each with its reason): kinsoku tables (0x088f1734.., pointed at from
  0x088fd198), name-substitution tokens 主人公の名前/苗字/名字 the renderer strncmp()s at 0x08817740 (no script uses
  them), speaker keys, ~650 layout object names.
- PARAM.SFO TITLE (XMB, UTF-8, 127 bytes) -> script/sfo.tsv; the same title is also in the EBOOT (save data).

## Extract - verified (tests/test_script.py)
`python -X utf8 tools/script.py dump [--force]` writes script/: sos/<dir>/<NAME>.tsv (395 files with text; the 11
SUBSCRIPT.PTD copies are byte-identical to RES/SCRIPT/SC and share one TSV), eboot.tsv, eboot_nontext.tsv, sfo.tsv.
Columns id, kind, speaker, max, jp, en, notes; `\n` written as `\\n`. Without --force it never touches an existing file;
--force keeps en/notes by id and warns when jp changed under a translation. Tests: re-encoding every TSV jp rebuilds
each SOS byte-identically and matches the EBOOT bytes; every pool slot and every EBOOT scan hit is a row or classified.

## Other box widths - verified (tools/boxes.tsv is the window data the fit lint reads)
- Alpha's help lines and the Hexcite reactions use the dialogue box (391 px x 3 lines; work/qa/width/boxes).
- Choices: two pills ~327 px wide, text centred, wrap between 312 and 325 px; budget 300 px, 1 line.
- Hexcite menu help bar: one line from x = 8, no wrap, clipped at x = 480; budget 464 px. Slots 27-43 bytes: repoint.

## Marker build - verified (phase 5)
`python -X utf8 build.py --marker --out build/sora_marker.iso`: every SOS row `[SC10000.m12] filler` (one full line
per Japanese line), EBOOT rows `[C07B4] ...` (last 5 hex digits of the id), SFO `[TITLE] ...`. `warp.py --all` on it
(work/qa/marker/tour, 48/48 ok): every dialogue box, help line, Hexcite reaction, help bar and choice shows its id;
every other Japanese on screen is a GIM in docs/re/graphics.md. Nameplates still read Japanese with the speaker keys
untouched, so the plate is the COMMON_00_NAME GIM, not text.

## Other text sources
- FSB (FSCN layout) / FAB files: only internal Japanese object names; none appeared on any of the 48 tour screens.
