# Sora no Otoshimono: DokiDoki Summer Vacation English translation

Unofficial English fan translation of **Sora no Otoshimono: DokiDoki Summer Vacation** (そらのおとしもの ドキドキ
サマーバケーション; PSP, Kadokawa Shoten, 2010; ULJM05639): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story (all chapters, card events, lessons, endings) | Translated |
| Menus, help lines, Hexcite reactions, save dialogs, XMB title | Translated |
| Graphics with text (title menu, cards, profiles, gallery, Hexcite, tutorials, banners, XMB icon) | Translated |
| Title logo (kana そらのおとしもの), company logos, © notices | Left in Japanese |
| Voiced lines | Japanese audio, English text |
| Staff roll | Translated |

Known issues: none known; see [Issues](../../issues). Tested in PPSSPP only; a real PSP/Vita run is not confirmed yet.

## Base image

Redump: *Sora no Otoshimono - DokiDoki Summer Vacation (Japan)*, 830,013,440 bytes.

| Hash | Value |
|---|---|
| CRC32 | `FDD1008B` |
| MD5 | `dff51f00173f776ba27622eed4a39500` |
| SHA-1 | `a82a86614522c0c8088954543c3fa23d7cfe6332` |

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `gfx/` | Graphics text: English per image row, drawn by `tools/gfx_*.py`. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ISO

Needs Python 3.12+, your own dump of the Japanese game, and the EBOOT signer (`tools/sign_np`, built once under WSL;
see `tools/sign.py`).

```sh
git clone https://github.com/minhnhattonthat/sora-no-otoshimono-dokidoki-summer-vacation-en
cd sora-no-otoshimono-dokidoki-summer-vacation-en
# copy your dump to: rom/Sora no Otoshimono - DokiDoki Summer Vacation (Japan).iso
#   (830013440 bytes, SHA-1 a82a86614522c0c8088954543c3fa23d7cfe6332; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/dump_eboot.py                     # decrypted EBOOT -> work/eboot.elf (needs tools/ppsspp)
python -X utf8 tools/unpack.py && python -X utf8 tools/gimsurvey.py   # work/res, work/gimpng
python -X utf8 build.py                                # -> build/sora_en.iso
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Kadokawa Shoten's and is included only
so the translation can be checked against it. Sora no Otoshimono: DokiDoki Summer Vacation is (c) Kadokawa Shoten;
this project is not affiliated with them. Fonts: see `docs/fonts.md`. Do not share patched ISOs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
