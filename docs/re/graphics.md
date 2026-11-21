# Graphics-text survey

Static sweep: `python -X utf8 tools/gimsurvey.py` decodes every GIM in work/res (standalone and embedded in FSB/FAB),
deduped by md5: 1701 unique, 3406 copies, 0 skipped. `work/gimpng/<n>.png`, `work/gimpng/index.tsv` (n -> every
file:offset copy; edits must go to every copy), sheets `work/gimpng/sheet_<group>_<k>.png` labelled with n.
GIM numbers below are survey numbers (stable as long as work/res is unpacked the same way).

## Surveyed (sheet -> Japanese texture rows)
| Sheet | GIM n | Kind | Japanese | Plan |
|---|---|---|---|---|
| COMMON_0 | 3,4,5,6 | button | はい / いいえ (purple + orange states) | redraw Yes / No |
| COMMON_0 | 7-23 | prompt | confirm prompts: ここまでのデータを保存しますか？, 中断データは削除されますがよろしいですか？, プロローグを飛ばしますか？, このカードを持っていきますか？, 必殺技カードが使えません。よろしいですか？, ゲームを途中でやめますか？, 設定を初期状態へ戻しますか？, セーブをしないとデータが保存されません。よろしいですか？, このカードを使いますか？, 設定を保存しますか？, このレベルの最初からはじめますか？, 最初からやり直しますか？, カードを捨てますか？, プレイ中のデータは削除されますがよろしいですか？, もう一度、読みますか？, チュートリアルを中断しますか？, クリアデータを保存しますか？ | redraw (orange outlined text) |
| COMMON_10_TITLE | 192 | logo | そらのおとしもの ドキドキサマーバケーション (with romaji SORA NO OTOSHIMONO) | official English logo exists for the anime (Heaven's Lost Property); redraw subtitle at least, decide in phase 8 |
| COMMON_10_TITLE | 193-198 | menu | コミュニケーションモード / フリーモード / オプション (plain + wing-selected) | redraw |
| COMMON_10_TITLE | 199-202 | menu | はじめから / つづきから (plain + selected) | redraw New Game / Continue |
| COMMON_10_TITLE | 188 | logo | 角川書店 (Kadokawa Shoten publisher logo) | leave (company logo) |
| COMMON_10_TITLE | 189 | label | © copyright line (small Japanese) | leave or English copyright |
| XMB | ICON0.PNG | logo | Japanese title logo | redraw (PNG in ISO + RES/1ST copy) |
| XMB | PIC1.PNG | label | © line | leave |
| PARAM.SFO | TITLE | text | そらのおとしもの　－ドキドキサマーバケーション－ | English title (sfo.py) |

| COMMON_00_NAME | 24-37 | label | speaker name plates: 智樹, 智樹A, 智樹B, 智樹？, イカロス, ニンフ, そはら, そはらA, そはらB, 美香子, 守形, ？？？, 智樹＆ニンフ, 智樹＆そはら (white text) | redraw (names per glossary) |
| COMMON_10_PARAMETER_0 | 179, 180 | label | ダウン / アップ (with arrows) | redraw Down / Up |
| COMMON_10_PARAMETER_0 | 181 | label | 嬉しい (emotion; sheet _1 likely holds the rest) | redraw |
| COMMON_10_PARAMETER_0 | 150, 161 | latin | Level; Sad/Happy/Shy/Anger | keep |

No-text in surveyed sheets: COMMON_10_PARAMETER_0 134-149, 151-160, 162-178; COMMON_0 0-2; TITLE 185-187 (Bottle Cube, CRI, Gu logos: Latin), 190-191.

## Not yet surveyed (open these sheets and add rows)
Open each with the Read tool one at a time (a 6x8 sheet costs ~2k tokens; `codex exec` via tools/gfx_survey.sh was
out of quota on 2026-11-22). Remaining: COMMON_10_CARDGET, 10_COM_USECARD, 10_LOADING, 10_OPTION,
10_PARAMETER_1, 10_WINDOWS, 20_HEX_MENU, 20_HEX_OPTION, 20_HEX_RESULT, 20_HEX_START (2); COMMU_00_CARD (3),
00_CARDNAME_GALLERY (3), 00_CARDNAME_GET (2), 10_CARDGALLERY (3), 10_CHANGE, 10_COM_MENU, 10_COM_TUTORIAL, 10_ENDING,
ENDING_A (2), ENDING_B, ENDING_C, 10_HELP, 10_LEVELUPDIALOG, 20_HEX_CARD; FREEMODE; HEXCITE (2), HEX_RESULTANIME (3),
HEX_SPECIAL (3), HEX_TUTORIAL; IMG_BG, IMG_CH (7), IMG_EV (2), IMG_GO.
Video: none (no .pmf on the disc). Movies with burned-in text: none.
