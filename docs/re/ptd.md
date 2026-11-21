# Disc layout, PETA archives, YKLZ compression

Dump: ULJM05639, `rom.sha1`. Game made by Bottle Cube / Kadokawa Shoten; same PETA engine as Mirai Nikki 13th Diary Holder (PSP).

## ISO (iso9660.py list)
- `PSP_GAME/SYSDIR/EBOOT.BIN` encrypted (`~PSP`, ULJM05639_Sora-Oto_PSP); `BOOT.BIN` is all zeros. Loaded at 0x08804000.
- `PSP_GAME/USRDIR/res/res.ptd` (114 MB, all game data), `voice_adx.ptd` (604 MB, voices; PETA too), `cache_umd.dir` (the two paths).
- `PARAM.SFO` TITLE `そらのおとしもの　－ドキドキサマーバケーション－`; ICON0.PNG / PIC1.PNG (copies also in RES/1ST/).
- `SYSDIR/UPDATE/` is a firmware updater (leave alone).

## PETA (.ptd) - verified (tools/ptd.py, tools/unpack.py: all 1798 + 725 nested files unpack, every YKLZ decodes to its stated size)
- Header: `PETA`, u32 toc_end (0x1d800), u32 archive size, u32 sbox_end (0x120), u32 file count (0x10), u32 flags (0x14).
- 0x20..0x120: 256-byte S-box. TOC bytes [sbox_end, toc_end) obfuscated: plain = sbox[enc ^ (-(i - sbox_end) & 0xff)]
  (from github.com/rzhumen88/ptd-unpacker). Nested PTDs (RES/__PACK__/*.PTD, flags = 2) have a plain TOC.
  guess: obfuscation flag = byte 0x16 (res.ptd 0x00010030, nested 0x00000002).
- Deobfuscated TOC: 0x50-byte root record, then 0x50-byte dir records (u32 abs offset of the dir's first file record,
  u32 first file index, u32 count, u32 0, name[64] e.g. `RES/SCRIPT/SC/SC1`), then 0x40-byte file records
  (u32 byte offset, u32 stored size, u32 1 = YKLZ / 0 = raw, u32 0, name[48]). Files are 2048-aligned.
- RES/__PACK__ holds 11 nested PTDs that duplicate files (card names, cards, CH sprites, SUBSCRIPT SOS...): any
  edited file must be written to every copy (`work/res/index.tsv` lists all; `work/gimpng/index.tsv` lists GIM copies).

## YKLZ - verified (decoder disassembled at 0880B8C0 in the RAM image; tools/yklz.py; roundtrip pack/unpack test)
- 16-byte header: `YKLZ`, 00 00, u8 method (1 = LZ, 0 = stored), u8 dbits (0x0a), u32 LE output size, u32 (unused by
  the decoder).
- Stream: flag byte, MSB first, bit 1 = reference (b1 b2): len = (b1 >> (dbits-8)) + 3, disp = ((b1 & mask) << 8 | b2) + 1.
- `yklz.pack` is a greedy compressor in the same format (byte-identical recompression not needed: rebuilt entries replace
  whole files).

## Repack - verified (tools/ptd.py `repack`, build.py, tests/test_identity.py)
- Layout: files sit in the TOC's offset order (res.ptd: not index order), back to back, each aligned to 2048
  (res.ptd) or 16 (nested PTDs), zero padding; header u32 at +8 = archive size padded to the same alignment.
  `repack(buf, {})` reproduces res.ptd and all 11 nested PTDs; `build.py` with no edits gives the dump's SHA-1.
- Edits: `{work/res-relative path: bytes}`; YKLZ files are recompressed with `yklz.pack`, later files shift, the
  TOC offsets/sizes are rewritten and re-obfuscated. A grown res.ptd moves to the ISO's end (iso9660.patch).

## Free space / rebuild plan
- res.ptd TOC slack: toc_end 0x1d800 vs records ending 0x1d1a0. Files can grow if the archive is re-laid out (offsets are
  plain u32 in the TOC) and the ISO file grows (iso9660.patch moves a bigger file to the image end).
