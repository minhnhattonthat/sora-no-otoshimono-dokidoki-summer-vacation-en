# Glossary - Sora no Otoshimono: DokiDoki Summer Vacation

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: a row's JP present in a line means one of its EN forms (`/`-separated)
must appear in the English; Avoid spellings fail.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Ikaros-san, Sakurai-kun, Sugata-senpai). Name order: Western (Tomoki Sakurai).
- Romanisation source: official English (Funimation anime "Heaven's Lost Property"), else earlier fan patch, else Hepburn without macrons.
- Credits: English.
- Register: casual, comedic teen ecchi comedy; natural spoken American English, contractions; jokes keep their punch.
  Sound effects and interjections: romanised or English onomatopoeia as fits ("Gwah!", "Kyaa!", "Heh heh heh..."),
  never left as kana.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...' (titles) or "...", ・・・ / …… -> ..., ！？ -> ?!, ～ (stretched vowel) ->
  stretch the word ("Sakurai-kuuun") or drop it; a literal `~` only as Mikako's sing-song tail (her lines, or
  someone imitating her; D8, linted by tools/batches.py), （inner thought） -> keep the parentheses: (thought).
- ASCII only. No `/` (it starts an engine control code), no `\` except `\n`, no `%name`. Keep `/K` at the very end
  of the Hexcite reaction lines that have it.
- Write each box as one paragraph; the build word-wraps it to the box (tools/fit.py). `\n` only for a forced break.
- Voices: docs/style-reference.md.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 桜井智樹 | Tomoki Sakurai | | protagonist; first person 俺 -> I | |
| 智樹 / トモキ | Tomoki | | | |
| イカロス | Ikaros | | Angeloid, calls Tomoki マスター | Icarus |
| ニンフ | Nymph | | Angeloid; calls Ikaros アルファー | Nimph |
| 見月そはら | Sohara Mitsuki | | Tomoki's childhood friend, next door | |
| そはら | Sohara | | | |
| 守形英四郎 | Eishiro Sugata | | New World Discovery Club president | |
| 守形 | Sugata | | | |
| 五月田根美香子 | Mikako Satsukitane | | student council president | |
| 美香子 | Mikako | | | |
| 五月田根 | Satsukitane | | 五月田根組 = the Satsukitane family (yakuza) | |

## Honorifics and forms of address
Name + honorific forms are linted by regex (tools/batches.py HONORIFICS; stretched forms like "Sakurai-kuuun" pass):
イカロスさん Ikaros-san, イカロスちゃん Ikaros-chan (Mikako), そはらさん Sohara-san, ニンフさん Nymph-san,
ニンフちゃん Nymph-chan, 桜井君/桜井くん Sakurai-kun (Mikako -> Tomoki), 見月さん Mitsuki-san, 守形先輩 Sugata-senpai,
守形さん Sugata-san, トモちゃん Tomo-chan (Sohara -> Tomoki), 英くん/英君 Ei-kun (Mikako -> Sugata).

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| マスター | Master | | Ikaros/Nymph -> Tomoki | |
| アルファー / タイプアルファー | Alpha | | Nymph's name for Ikaros; タイプアルファー = "Type Alpha" | Alfa |
| 会長 | President / Prez | | Mikako (student council president); 会長さん -> "Prez" or "the President"; Mikako's self-reference 会長 -> "your President" | |
| 先輩 | Senpai / -senpai | | Tomoki/Sohara -> Sugata | |
| マイマスター | my Master | | amnesiac Ikaros | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 空美町 | Sorami | | the town ("Sorami Town" where natural) | |
| 新大陸 | New World | | Sugata's dream; 新大陸発見部 = New World Discovery Club | New Continent |
| シナプス | Synapse | | the floating city of the Angeloids' masters | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| エンジェロイド | Angeloid | | | |
| 空の女王 / ウラヌス・クイーン | Uranus Queen | | Ikaros's mode | |
| そはらチョップ | Sohara Chop | | plain チョップ -> chop | |
| スイカ | watermelon | | Ikaros's favourite | |
| インプリンティング | imprinting | | | |
| ヘキサイト | Hexcite | | the board game (Hexcite ES = Free Mode variant) | |
| 新大陸発見部 | New World Discovery Club | | | |
| 新大陸発見レーダー | New World Detection Radar | | | |
| 五月田根組 | Satsukitane family | | Mikako's yakuza house | |
| 超々超音波振動子 / パラダイス＝ソング | Paradise Song | | Ikaros's weapon (ruby reading) | |
| ａｅｇｉｓ / 絶対防御圏 | Aegis | | Ikaros's shield (Absolute Defense Zone) | |
| Ａｒｔｅｍｉｓ / 永久追尾空対空弾 | Artemis | | Ikaros's homing missiles | |
| 思考制御プロテクト | thought-control protect | | | |
| 愛玩用 | pet-class | | 愛玩用エンジェロイド = pet-class Angeloid | |
| 戦略エンジェロイド | strategic Angeloid | | | |
| 電子戦用 | electronic-warfare | | Nymph's type | |
| 初期化 | reset / initialize / initializing / initialization | | Ikaros's reset (initialize / initialization) | |
| バックアップ回路 | backup circuit | | | |
| 動力炉 | power reactor | | Ikaros's core | |
| おっぱい・オブ・ザ・ワールド | Oppai of the World | | Tomoki's DVD series | |
| 必殺技 | special move | | Hexcite | |
| トモキ・タイム | Tomoki Time | | Hexcite special | |
| 海の家 | beach shack | | | |
| モテ男ジャミング | Heartthrob Jamming | | Nymph's hack | |
| 量子変換器 | quantum converter | | | |
| 鯉のぼり | carp streamer | | | |
| 三角木馬 | wooden horse | | "triangular wooden horse"; 全自動三角木馬 = "fully automatic wooden torture horse" | |
| トランスポート | Transport | | 転送（トランスポート） | |
| 英美郎 | Eimiro | | Mikako's blend of 英四郎 + 美香子 | |
| ブルマー | bloomers | | | |
| はっさく | hassaku | | "hassaku oranges" on first use | |
| 王様ゲーム | King Game | | | |
| 五月田根家杯 | Satsukitane Family Cup | | | |
| テキ屋 | vendor | | festival vendors (stall-running toughs) | |
| 秋祭り | autumn festival | | | |
| サバイバルゲーム | survival game | | | |
| 我慢大会 | endurance contest | | | |
| 五月田根家 | Satsukitane family | | | |
| 出撃 | launching | | "Type Alpha Ikaros, launching." | |
| 軽装モード | Light-armor mode | | outfit card | |
| 私服モード | casual-wear mode | | outfit card | |
| 未確認生物 | unidentified | | UMA: "unidentified life-form" | |

## Decisions from earlier batches
- b023 甘える -> "act spoiled" (active); 甘えさせる -> "pamper" (reviewer: "pampered" inverted Mikako's definition)
- b022 なんでやねん -> "What the heck?!" (the tsukkomi retort); ボケ / ツッコミ -> funny man / straight man
- b031 Mikako's self-reference 会長 -> "your President", never "the President"
- b003/b018 Ikaros's rare casual lines (to Nymph, jealous) show as light contractions; her normal register stays formal
- b043 流し打ち stays baseball ("opposite-field hitting")
- b001 タイプアルファー -> "Type Alpha"; ムシ (Nymph's old name for Tomoki) -> "bug"
- b051 Hexcite reaction sets (EBOOT 088DCAD0..): Ikaros, Nymph, Sohara, Mikako, Sugata, Tomoki in that order
