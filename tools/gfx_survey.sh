#!/bin/sh
# Run the read-only graphics-text survey over contact-sheet chunks with codex exec (one process per chunk, in parallel).
# usage: sh tools/gfx_survey.sh work/gfxsurvey/chunk_*   -> work/gfxsurvey/<chunk>.out
for c in "$@"; do
  args=""
  for f in $(cat "$c"); do args="$args -i $f"; done
  # list the sheet names in the prompt so the folder is known even if the model can't see file names
  { cat tools/gfx_survey_prompt.md; echo; echo "Sheets attached, in order:"; cat "$c"; } > "$c.prompt"
  codex exec -s read-only --skip-git-repo-check $args - < "$c.prompt" > "$c.out" 2> "$c.err" &
done
wait
