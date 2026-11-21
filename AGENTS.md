# Sora no Otoshimono: DokiDoki Summer Vacation (PSP) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`        -> build/sora_en.iso (checks the dump against `rom.sha1` first; not written yet, phase 3)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/sora_en.iso --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py build/sora_en.iso --scene <name>` (phase 2; PPSSPP has no Lua, warps poke RAM over psp.py; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (xdelta3 -B patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ISO: `rom/Sora no Otoshimono - DokiDoki Summer Vacation (Japan).iso` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`).
- Emulators: QA = PPSSPPHeadless QA fork qa-1 in `%LOCALAPPDATA%\translate-retro-game\ppsspp-headless\` (`fetch_emu.py ppsspp-headless`); people/EBOOT dump = `tools/ppsspp/` (v1.20.4, github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-Windows-x64.zip; gitignored). Savestates: `work/states/`.
- Text: `script/` (TSV). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- PSP: circle = OK, cross = cancel. EBOOT.BIN is encrypted; ship a re-signed `~PSP` EBOOT, never the plain ELF dump.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
