# Debug tool (phase 2): scene ids, warp, game-state object

Tools: `tools/debug/drive.py` (PPSSPPHeadless driver: mash, peek/poke, wait on RAM; emu.py's `--mash` is not wired
for PSP), `tools/debug/warp.py` + `tools/debug/scenes.tsv` (scene list). Addresses are PPSSPP RAM for the dump in
`rom.sha1` (module at 0x08804000).

## Scene ids - verified (RAM diffs of title / script / tutorial / hub dumps, then asserted by every warp)
- `0x088FD1D8` u32 mode, `0x088FD1D4` u32 scene. Written by the main loop at 0x0881E740/0x0881E748 from a request
  struct (heap 0x09EC023C: +4 mode, +8 scene). Poking the request struct to switch scenes crashed the game: don't.
- Seen (mode:scene): 2:x logos, 1:3 title, 3:2 Free Mode game select, 3:10 Hexcite match (free), 5:11 script
  (ADV), 5:13 Communication tutorial, 5:18 Communication hub, 9:4 Hexcite match from Communication Mode.

## Script warp - verified (sc9/sc90010 ending, sc_end, prologue)
- `0x088F4974`: `res/script/sc/sc0/sc00000.sos\0` + 2 pad bytes (32 bytes), the script Communication Mode -> new game
  loads. Poke any `res/script/sc/<file>` (<= 31 chars) at the title, choose Communication Mode: the game runs that SOS.
  `.adv` jumps inside resolve relative to it. After the script ends the game shows the 6-page tutorial (5:13), then
  the hub; `sc_end.sos` (empty) is the fast way to the hub.
- Script names also live in the card tables at 0x088D9058.. (32-byte entries: id, card_name_s, card_name, ca*_s/m/l,
  0, script or `SCR名`) and as `res/script/sc/%s` format strings.

## Game-state object 0x09EC0000 - verified for the gallery flags
- Holds the scene manager (+0x238) and the save fields. The 2010 CWCheat list (kaizou-world.seesaa.net, ULJM-05639)
  addresses the same object at 0x08EC0000 (real-PSP heap), so its offsets carry over:
  - gallery / dress-up / profile unlock ("CG CARD GALLERY ALL"): +0x3B0 u32 FFFFFFFF, +0x3B4 0F, +0x3D3 1F, +0x3D8 1F,
    +0x3DD FF, +0x3DE u16 FFFF, +0x2E4.. 30 bytes FF. Verified: all five gallery tabs 100%, dress-up list full.
  - "TECH CARD NOT DEC": bytes +0x408/+0x40A/+0x40C/+0x40E/+0x410 = 1 (guess: technique-card counts; not verified).
- Hub level 1 / 20 cards-left candidates (guess, unverified): u16 20s at +0x3D84/+0x3D9C/+0x3DB4/+0x3DCC (param
  targets?), 30s at +0x3DE4.., +0x3E98 = 14, +0x3EA0 = 1.

## Save file - not editable directly
- `PSP/SAVEDATA/ULJM05639SoraOto/IKAROS.SAV` (25244 bytes) is encrypted by the savedata layer (two saves of nearly the
  same state differ in every byte). Edit the plaintext object in RAM instead and let the game write it (autosave).
- The boot flow on an empty memstick: "no save data, create?" Yes -> "save?" Yes -> "save completed" (cross) ->
  autosave notice (circle) -> logos -> title. warp.py's `boot_to_title` does this and asserts 1:3.

## Not reached yet
- Hexcite needs real play: the Communication-mode first match forces a guided move ("place on this line"); mashing
  circle never finishes it. Card get, use-card, level-up dialog (res/commu/10_levelup), game over and the credits
  after an ending still need the level / card-count / inventory fields or a Hexcite auto-player.
