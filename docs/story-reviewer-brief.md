# Story reviewer brief - Sora no Otoshimono: DokiDoki Summer Vacation (PSP)

You read one chapter of a JP->English fan translation straight through, in story order, the way a player
meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job is what they can't see.
Read-only: no edits, no git, no subagents. Return the report as your final message; the controller saves it.

## Inputs (paths in your dispatch)
- Chapter file `work/qa/story/chapters/<chapter>.txt`: every line of the chapter in story order,
  `>> id | speaker | JP` / `EN`. `## SCxxxxx` heads each script; read the `#` note at the top on branches (the files
  after an event's setup are ALTERNATIVE outcomes of one choice, not consecutive scenes). Read ALL of it before
  judging. Files over ~4 KB come back as a stub from a whole-file Read: read with offset/limit, ~150 lines a time.
- `docs/synopsis.md` (plot, who is who, late reveals), `docs/style-reference.md` (voice per character),
  `glossary.md` (rulings at the top). Read these in parts too.
- English is wrapped by the build; one entry = one text box. `~` is reserved for Mikako's voice (ruling D8).

## Judge, across the whole chapter
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks,
  register, how they address others (Ikaros: "Master"; honorifics per glossary). Name the line where a voice drifts or
  goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Names exactly as glossary.md; no "1th"-style suffix on numbers; no stiff stock phrases.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN`. Keep suggested EN short enough for a 3-line box (~120 chars).
### Assessment
`ok` (no Critical/Important) | `issue` - one sentence why. The controller writes this word into the chapter's verdict.
