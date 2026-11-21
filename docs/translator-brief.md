# Translator brief - Sora no Otoshimono: DokiDoki Summer Vacation (PSP, 2010)

You translate part of the Japanese script of "Sora no Otoshimono: DokiDoki Summer Vacation" (anime English title
"Heaven's Lost Property") into English for a fan patch. Visual-novel + board-game spin-off: a teen ecchi gag comedy.
Tomoki's careless "reset" order wiped Ikaros's memories, and the summer is spent getting them back.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents. Files over ~4 KB come back as a stub from a whole-file
Read: read with offset/limit (e.g. 80 lines at a time).

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md`, read in parts).
3. `docs/synopsis.md` - plot, structure, who is who, late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese` - form is dlg | choice | menu; ` / ` separates the lines of one
box (translate the box as one utterance); limit is the box: `391pxx3` = 3 lines of 391 px (about 150 characters in
all), `300px` = one line (about 40 characters), `127B` = byte limit of the slot (ASCII: 1 byte per character).
Lines are in story order within each script file (id prefix = file, SC10000.m5 = message 5); use neighbours for
context. Files SCxxxx0 are setups with a 3-way choice; x1..x4 are the outcomes of each choice.
The speaker column is who talks (blank = narration or a sound/pause box). In body-swap events (SC1016x) the speaker
is the body; the voice belongs to the other character.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; no tabs, no
Japanese or fullwidth characters, no curly quotes, no `\uXXXX`, no `/` (the engine reads it as a control code: write
"or", "and", "per"), no `\` except `\n`. Write each box as ONE paragraph: the build word-wraps it to the box. Use
`\n` only for a forced break (rare). Lines ending in `/K` (Hexcite reactions) keep `/K` as the very last two chars.

## Validate
`python -X utf8 tools/batches.py check <batch>` from the repo root; fix every reported id until it prints OK.
Dry-run one line: `python -X utf8 tools/fit.py "English text" [--box choice]` shows the wrapped lines and widths.
A dialogue box holds 3 lines; if a line won't fit, rephrase tighter without losing meaning (no abbreviations), and
if it truly can't, keep the meaning and report `LONG: id`.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible (docs/style-reference.md): Ikaros formal and flat with ellipses; Nymph bratty tsundere;
  Sohara warm and scolding; Sugata deadpan lecturer; Mikako sweet drawling sadist; Tomoki blunt, pervy, loud. A line
  any speaker could have said is a mistake.
- Names and terms exactly as in the glossary; honorifics kept, hyphenated (Ikaros-san, Sakurai-kun, Tomo-chan,
  Sugata-senpai, Ei-kun); Western name order. マスター = "Master" (capitalised), アルファー = "Alpha".
- Never abbreviate to fit.
- Punctuation: 「」 -> "...", …… -> "...", ！？ -> "?!", ～ stretches a word or goes, （thought） -> (thought).
  Drop furigana readings in parentheses after names.
- Onomatopoeia and interjections in English or romanised ("Gwah!", "Kyaa!", "Ngh...", "Heh heh heh"), never kana.
- A box that is only a pause (…… / ！？) stays a pause ("......", "?!").

## Consistency
Never edit `glossary.md` or any file other than your own `.out.tsv`. For a recurring name or term not in the
glossary, pick a form, use it consistently, and report it.

## Notes from earlier batches
- The check wants a glossary name in the English when the JP has it (ニンフ -> Nymph). Work it in naturally (a
  vocative "Nymph, ...", or the name in place of a pronoun); never bolt it on.
- Nymph's old insult for Tomoki ムシ = "bug".
- 海の家 = beach shack; 出撃 = "launching"; タイプアルファー = "Type Alpha"; 揉む in the massage gags = "knead" / "squeeze".

## Report (reply with only this)
Files written and entry count per batch; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
