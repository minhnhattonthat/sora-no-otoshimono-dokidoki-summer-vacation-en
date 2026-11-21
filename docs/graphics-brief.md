# Graphics brief - Sora no Otoshimono: DokiDoki Summer Vacation (PSP)

You redraw Japanese text drawn as graphics (banners, buttons, menu labels, cards, credits) in English for a fan patch.
Work only on the groups named in your dispatch, one at a time in the order given, each one finished before the next.
Do all the drawing yourself; do not dispatch subagents.

## Read first
1. `gfx/groups.txt` - your group's survey numbers and what they are; `docs/re/graphics.md` has the same rows in
   more detail. Each image is `work/gimpng/<n>.png` (4-digit n), sizes and md5 in `work/gimpng/index.tsv`
   (columns n, md5, w, h, copies). `python -X utf8 tools/gfx.py orig N 3` writes a zoomed copy on a dark background
   (`work/gfx/orig_<n>.png`) to read the text; read files with offset/limit (long files come back as a stub).
2. The pilot: `gfx/plate.tsv` and `tools/gfx.py` (read the whole docstring and `plate()`): how this game's images
   are made. Copy that approach; don't invent another one.
3. `glossary.md` (read in parts) and `docs/fonts.md` - names and terms exactly as in the glossary; only fonts under
   `fonts/`. Before translating a label, grep `script/` (`script/eboot.tsv`, `script/sos/*/*.tsv`, en column) for
   the same Japanese: card names, special moves and effects, outfit names already have an English wording; reuse it.
4. `$SKILL/references/graphics.md` §Lettering and §When the text is a texture (`$SKILL` = `python tools/skill.py`).

## You may write only
- `gfx/<group>.tsv`: tab-separated, header `n	md5	jp	en	rects`; one row per image you redraw (md5 copied
  from index.tsv; rects = "x,y,w,h;..." the only area your redraw may change, empty only when the whole image is
  text on transparency). Rows for images that turn out to hold no text: leave them out and say so in the report.
- `tools/gfx_<group>.py` defining `draw(row, im) -> RGBA Image` (same size as im). Import helpers from gfx
  (`import gfx`, then `gfx.FONT`, `gfx.typeset.text_image(...)`, font names `"os:WEIGHT:WIDTH"` for the variable
  Open Sans, e.g. `"os:800:75"` = ExtraBold Condensed). Share code between your own groups by importing your module.
- `gfx/out/<group>/` is written by `python -X utf8 tools/gfx.py gen <group>`; run it, never write PNGs by hand.
- Don't edit `tools/gfx.py`, the build, `glossary.md`, `docs/`, or another group's files; don't run build.py or an
  emulator; don't commit. If you need a change to shared code, describe it in your report.

## Style
- One font, size and fill per label class within a group (all buttons alike, all titles alike).
- Full words, no abbreviations to fit; condense (width axis down to 75) first. If something still won't fit, report it
  with the shortest wording you'd accept.
- Match the original's colour (`typeset.dominant`), outline or glow (`stroke=(w, colour)`), position and states
  (plain / selected / greyed variants of one label must read the same, only the colours differ).
- Text over artwork or a coloured panel: remove only the Japanese (`typeset.inpaint`, or repaint the panel colour
  inside the rect), then draw; never clear art to transparency.
- Antialiased text is fine at 12 px and up; below that, turn antialiasing off or test legibility at 3x zoom.
- PSP screen is 480x272: sizes in these textures are on-screen pixels.

## Check every image, offline
- `python -X utf8 tools/gfx.py gen <group>` must pass (it fails on any pixel changed outside a row's rects).
- `python -X utf8 tools/gfx.py preview <group>` and read `work/gfx/preview_<group>.png` (split it with
  `$SKILL/scripts/sheet.py ... --crop` if long): every letter readable, nothing left of the Japanese, no stray pixels.
- `python -X utf8 $SKILL/scripts/rectcover.py work/gimpng/<n>.png x,y,w,h..` on each row's rects exits 0 (the rect
  covers all of the original text; a neighbour touching the rect may be waived: say which in the report).

## Report (your final message, short)
Per group: rows done, rows left out and why, new terms (`JP<TAB>EN`), anything you couldn't fit, shared-code changes
you need.
