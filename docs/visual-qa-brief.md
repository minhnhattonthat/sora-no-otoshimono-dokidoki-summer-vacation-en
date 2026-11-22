# Visual-QA reviewer brief - Sora no Otoshimono: DokiDoki Summer Vacation (PSP)

You review screenshots from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents. Read long text files with offset/limit
(outputs over ~4 KB come back as a stub). `$SKILL` = the path `python tools/skill.py` prints.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per shot. Read every shot in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original ISO's shots: `work/qa/warp/<id>/<id>.png` (same scene names), and `glossary.md`.

## How to look
- Read each shot whole first (480x272). Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHOT.png --crop x,y,w,h --zoom 3 --out work/qa/zoom/<id>.png` and read that.
- When something looks wrong, open the same scene from the original (`sheet.py EN.png --compare JP.png --out ...`).
  If the original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and name plate: a few pixels of misalignment don't show at
  full-shot scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible (text or text drawn as a picture);
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its button, a label, a name plate;
- garbage, wrong or missing glyphs, stray pixels or leftover Japanese strokes around redrawn English;
- broken line breaks: a word split mid-line, a box ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade, a cursor caught mid-blink, a scene still loading after a warp;
- anything identical in the original's shot;
- the "What to do?" hub menu drawn over a story scene, ending or game-over screen: a debug-warp artefact (the
  warp pokes a scene jump from the hub), not in normal play;
- the Kadokawa Shoten logo, the Bottle Cube / CRI / GU logos and the romaji "SORA NO OTOSHIMONO" stay as they are;
- dialogue speaker plates use English names, the honorifics are hyphenated (Ikaros-san), Mikako may end lines with `~`;
- digits drawn by the game next to redrawn words (counters, W/L/D record, "card(s) obtained!").

## Verdicts
Write your verdict file once you have read every shot, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which part of the screen, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
