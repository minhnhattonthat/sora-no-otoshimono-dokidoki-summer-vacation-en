# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator in progress: tour gate was green on dc618f55; text coverage 6705/6844; credits
  fix rebuilt. Last good build: 2026-11-22 19:16 build/sora_en.iso sha1 14b5c6da... (dc618f55 + credits cards
  910-925 capped at 180 px), smoke ok; tour/qa_gate must be re-run on it. warp.py defaults to the ORIGINAL ISO: pass
  build/sora_en.iso.
- **Done:**
  - Step 0: ROM pinned (`rom.sha1`), PPSSPP v1.20.4 in `tools/ppsspp/`, PPSSPPHeadless qa-1 shared install, smoke boots
    the original ISO, pre-commit runs `tools/check.py`, guard hook blocks `sed -i`, rulings D1-D7 in docs/decisions.md.
  - Phase 1 recon (docs/re/ptd.md, script.md, graphics.md): PETA/YKLZ/SOS formats, `tools/unpack.py`, `tools/sos.py`
    (414 SOS byte-identical), graphics survey of all 1701 GIMs. Regenerate work/ with
    `python -X utf8 tools/unpack.py && python -X utf8 tools/gimsurvey.py`.
  - Phase 2 (docs/re/debug.md): `tools/debug/warp.py --all` reaches all 48 rows of `tools/debug/scenes.tsv` from a
    cold boot with mode:scene asserts and shots (work/qa/warp/<name>/, states in work/states/). Route steps
    `cheat:NAME` and `until:M:S:LIMIT[:KEYS]`. Communication mode: cheat `hexdone` (Hexcite tutorial-seen bit) ->
    real matches, forced win, card hand, card use, event, param-up; cheats `params`/`noturns`/`lastchapter` +
    `chapterend` (scene-request poke) -> level-up banner, game over (bad ending sc90020 + retry prompt), ending
    sc90010 + staff roll (row `credits`, state at the roll's start). Scene jump table mapped (0x088C928C).
    `tools/debug/mips.py` = EBOOT disasm/xref/case lookup.
  - Save editor `tools/debug/save.py make|check` verified with `unlock_all` (loads via Continue, gallery 100%).
  - Phase 3: `ptd.repack` (offset-order layout, 2048/16 alignment, TOC rewrite + re-obfuscation, nested PTDs by
    work/res path) and `build.py` (check_rom -> repack res.ptd -> iso9660.patch). tests/test_identity.py: every PTD
    and the whole ISO rebuild byte-identical; an edit test grows a YKLZ file and a nested file and checks the rest.
    `build.build(out, repl)` takes `{work/res path: bytes}`, the hook for phase 7 inserts.
  - Phase 4 (docs/re/script.md §Bytecode, §EBOOT, §Extract): `tools/script.py dump` -> script/sos (395 TSV, 6614
    msg + 88 choice + 5 msg_nonl rows, speaker column from bytecode), script/eboot.tsv (137 shown strings: help lines,
    Hexcite reactions with `/K`, save dialogs UTF-8), eboot_nontext.tsv (687 classified), sfo.tsv (XMB title).
    Decrypted EBOOT: `tools/dump_eboot.py` -> work/eboot.elf, pinned in `eboot.sha1`. tests/test_script.py:
    TSV re-encodes byte-identically (all SOS rebuild, EBOOT bytes match), every pool slot / scan hit covered.
  - Phase 5 (docs/re/script.md §Font, §VWF, §Dialogue box width, §Control codes, §Marker build): build.py inserts
    script/ (en column; SOS per copy, EBOOT in place, SFO), `--marker`, `--qa ID=TEXT` probes. tools/font.py: Open Sans
    Semibold 14 px ASCII glyphs (fonts/, Apache 2.0) into both HG_G18.TFP copies. tools/vwf.py: one-byte advance
    from a width table (layout 0x08817E64 + draw 0x08818B50 -> helper 0x088EA3A0), 4 relocations appended.
    tools/sign.py: sign_np -elf (WSL gcc build, tag 0xD91612F0 = original). yklz.pack fixed: no overlapping refs
    (game memcpys them; it ate font pixels). Marker tour `warp.py --all` 48/48 ok (work/qa/marker/tour).
    Width gate in tools/boxes.tsv: dialogue/help/Hexcite reaction 391 px x 3 lines, choice 300 px x 1,
    Hexcite help bar 464 px x 1; torture line renders (work/qa/width/vwf3).
  - Phase 6: script/ fully translated (6835/6840; the 5 left are full-width-space pause boxes that keep their bytes).
    tools/batches.py (split/check/merge, lint in tools/check.py: ASCII, no `/` but the trailing `/K`, glossary rows,
    honorific regexes, wrapped width per tools/boxes.tsv, EBOOT byte max), tools/fit.py (word-wrap; build.py wraps
    every dialogue-box string with it, translators write one paragraph per box), tools/pairs.py (review files).
    Docs: glossary.md, docs/synopsis.md, docs/style-reference.md, docs/translator-brief.md, docs/reviewer-brief.md.
    51 batches (work/tl, gitignored) by 11 translator agents; every batch reviewed, all Critical/Important fixed
    (fix001-fix007); Minors in docs/polish.md (polish pass before release). Phase 6 review (harness): `~` only in
    Mikako's voice (D8, linted), 43 lines rewritten (fix008); reviewer reports now saved to work/tl/review/.
  - Phase 7: only one EBOOT slot overflowed (088F3E3C helpbar, 35 > 27 B); rephrased "Pick your opponent's level."
    (also 088C1EB4, same JP; fix009), so no repoint needed; batches.py byte check now covers helpbar rows too.
    build.eboot_strings() asserts each slot holds the extracted string and returns the writes. tests/test_build.py
    (romdiff for this build): EBOOT writes stay in slots, never overlap, no .data pointer / lui pair reaches past a
    written string's first byte (so the `max` slack is verified free); res.ptd keeps its leaf set and only SOS +
    HG_G18.TFP leaves change; EBOOT signed (~PSP). Lint 0 problems, control codes matched, check.py green.
    Phase 7 review fixes: eboot.isjp takes ™/® -> 5 "Memory Stick™" save dialogs extracted + translated (all 5 have
    code readers, mips.py xref; written "Memory Stick" without ™, ASCII lint); lint fails untranslated rows and
    leading/trailing blank mismatches; fit.wrap is balanced (same line counts, 15 three-line boxes) + stub-last-line
    rule (< 6 chars); build asserts every TSV has a source and every row with English is written; tests/test_build.py
    ISO-level romdiff (old/new extents, dir records, PVD size, tail).
  - Phase 8 graphics, wave 1 (2026-11-22): tools/gfx.py pipeline (gfx/<group>.tsv + tools/gfx_<group>.py ->
    gfx/out/<group>/, build re-encodes every GIM copy). 18 of 24 groups in gfx/groups.txt drawn, 369 images, offline
    checked by graphics agents (gen diff check, rectcover; waivers = neighbouring art). In game so far: name plate
    (ev_sc1) and title menu (work/qa/gfx/w1/title) English. Build a16a46df..., smoke ok.
  - Phase 8 graphics, wave 2 (2026-11-22): profile, commtutorial, credits, hexcite, hexspecial, hextutorial, logo
    (subtitle 192 + title copyright 189) by 3 graphics agents; all 25 groups drawn. tools/gfx_icon0.py redraws the XMB
    icon (build.py ships gfx/out/xmb/ICON0.PNG to /PSP_GAME and both RES/1ST copies; test_build checks it). Wording
    unified (D9: Outfit, Gym Wear, pieces; おわり？ = The End?), glossary points at gfx/*.tsv for drawn terms. Tour
    shots of title, profiles, comm tutorial, Hexcite tutorial/match, credits all English (work/qa/w2sheet.png).
    Warp row level_up now waits for 5:48 (5:47 passed between polls on the English build and the mash opened Cards).
    Credit name readings the agent was unsure of: 針生一 Hajime Hario, 藤井慧 Kei Fujii, 久坂真生 Mao Kusaka, 長信考
    Nobutaka Cho, 鏡谷陽一 Yoichi Kagamiya, 松宮庸典 Tsunenori Matsumiya, 藤岡迅彦 Hayahiko Fujioka, 山下雅水 Masami
    Yamashita, 田邉香 Kaori Tanabe, 本田稔裕 Toshihiro Honda (gfx/credits.tsv; best-guess Hepburn).
  - Phase 8 QA session 3 (2026-11-22): `tools/debug/cover.py` = PSP text coverage (logging breakpoint on the
    text-box setter 0x08817C88, dialogue + choices + EBOOT help/reactions; every SOS script played from a cold-boot
    title state, mashing `down,up,circle` = first choice option). Choice boxes pass inkbox (SC10030 3 options,
    work/qa/gfxshots/choice_10030/t12.png, rects 58,40,304,22 88,82,304,22 118,124,304,22). In-game shots (work/qa/
    gfxshots/): all 6 Communication tutorial pages + Read it again? prompt, Hexcite tutorial panels up to "Place a
    piece on this line", whole staff roll (cast cards, role cards, disc cards), Start!/Finish!/Winner-Loser panel.
    Bug fixed: staff-roll disc cards 910-925 slide right while shown (screen x 232..300), so 913, 918, 921, 923
    were cut at the screen edge (the wider Japanese would be too); gfx_credits caps their ink at 180 px (font
    shrinks), tests/test_gfx.py; 913 = Project Manager, 923 = Kadokawa Shoten Co., Ltd., 925 制作総指揮 = General
    Producer (924 is Executive Producer).
    Text coverage pass p0 (build dc618f55): 6697/6844 shown; every SOS message and choice reached except the 5
    U+3000 pause boxes (shown, but logged as raw SJIS); waivers in docs/text_unshown.tsv (those 5 + 18 PPGe save
    dialogs). `cover.py scenes` (all 48 rows ok) -> 6705/6844, 23 waived, 116 failing (work/qa/cover/report.txt):
    hub cursor comments 088C07B4-088C12B4, Options help 088C15B4-088C19B4, Free settings help 088C1CB4-088C1FB4 and
    088F3E3C-088F3EA8, and the Hexcite post-match reactions 088DCAD0-088E1514 (per opponent x result).
    warp.py route step `shot[:NAME]` for multi-page rows.
- **Next:**
  1. DONE 2026-11-22: QA tour on build dc618f55 (`warp.py build/sora_en.iso --all --out work/qa/tour`, 48/48 ok),
     work/qa/manifest.tsv (delete work/qa/tour/*/memstick before `qa_gate.py init ... --glob "*.png"`), 3 visual-QA
     agents (docs/visual-qa-brief.md): 48 ok, 0 issues; `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts`
     exits 0. Any rebuild needs a new tour + init (verdicts of unchanged shots carry over). Cosmetic notes: param-up
     banner "Happy  Up" gap wider than JP (Up sprite is fixed); free_opponent record "D" closer to its digits.
  2. The credits fix is in the new build (see Phase line); reshoot the roll (`warp.py build/sora_en.iso --scene
     credits --state-out work/states/credits.ppst`, then Drive run(300)+shot loop to 20000 frames) and check disc cards
     910-925 aren't cut at the right edge; then new tour + qa_gate init + verdicts (any rebuild invalidates the gate).
  2b. Coverage: add scene rows (cover.py scenes --only) that walk the cursor over every hub / Options / Free settings
     item (shot each) and Free Mode matches vs each opponent with each result (poke scores like hexres: +0x774 me,
     +0x79C COM after free_match + 900 frames, then the free_win mash), then re-run textcover.
  3. Graphics frames still not shot: Hexcite result words (Big Win!!/Narrow Win/Draw/Lose!/Crushed!!: they play after
     Finish! and before the Winner/Loser panel, ~f1380-1400 after poking scores +0x774/+0x79C at free_match + 900
     frames; shoot every 4 frames there), special-move cut-ins (square in a Free Mode match), game-over The End?
     (IMG_GO, end of the bad ending), profile pages 2-24, later Hexcite tutorial panels (pick a piece up with circle
     on the tray first, then place). Tight card names 555, 556, 558, 560, 562, 569, 570, 573, 578, 581, 583, 604, 255.
  4. Text coverage logs (work/qa/cover/p0, scenes) stay valid across graphics-only rebuilds (keys = row order +
     EBOOT addresses); regenerate strings.tsv (`cover.py strings`) and re-run after any script/ edit. Choice
     branches 2/3 (`--keys down,circle --tag p1`) aren't needed for coverage (every option text and message was
     reached) but would show branch-only scenes.
  5. inkbox on centred menu boxes (hub menu, Hexcite menu), Hexcite /K reactions; stress saves (longest card names
     in hand: needs the hand array RE'd; max Hexcite record digits; params max).
- **Non-blocking:** XMB PIC1.PNG keeps its Japanese © line (legal notice, like the company logos). Title kana logo
  kept (D10, open to the user).
- **Known gaps (non-blocking):** Free Mode Hexcite ES is greyed (unlock flag not found; its text is shared with
  Hexcite). Poke-jumped chapter/ending scripts keep the previous screen's overlay drawn; the scripts themselves are
  shot clean by the ev_* / ending_* script-warp rows.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: the signed EBOOT and the VWF code (in .rodata, relocated)
  are only tested in PPSSPP; a boot on a real PSP/Vita before release would confirm them. Note: codex exec (used for read-only reviews) is out of quota until 2026-11-26.
  Title logo: keep the kana そらのおとしもの (D10 default) or redraw an English "Heaven's Lost Property" logo?
  Credit name readings marked best-guess above (gfx/credits.tsv) could be checked against an official source.
