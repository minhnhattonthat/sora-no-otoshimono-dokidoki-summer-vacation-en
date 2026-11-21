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
| COMMON_10_CARDGET | 40,41,44,46,53 | banner | きせかえ/コミュニケーション/イベント/プロフィール/必殺技 カードゲット!! (green outlined) | redraw "... Card Get!!" |
| COMMON_10_CARDGET | 42 | label | 枚ゲットしました！ (counter suffix, digits from 43) | redraw "got!" around a number |
| COMMON_10_CARDGET | 45 | label | ギャラリーに追加しました。 (on a wing) | redraw |
| COMMON_10_CARDGET | 48-52 | banner | 勝利数/連勝数/戦闘数/逆転数/点差 ボーナス! (pink) | redraw "... Bonus!" |
| COMMON_10_COM_USECARD | 66 | label | コンボカード (tiny tab) | redraw Combo Card |
| COMMON_10_COM_USECARD | 70 | prompt | 捨てるカードを入れ替えてください。 | redraw |
| COMMON_10_COM_USECARD | 71,72 | button | 捨てる (orange + purple) | redraw Discard |
| COMMON_10_COM_USECARD | 83 | prompt | 現在の手札 /『GET』がついているものは新たに獲得したカードです。/ ×閲覧終了 | redraw |
| COMMON_10_COM_USECARD | 88 | label | 着用中 (pink badge) | redraw Wearing |
| COMMON_10_COM_USECARD | 89 | latin | GET | keep |
| COMMON_10_LOADING | 112 | latin | Now Loading | keep |
| COMMON_10_OPTION | 114 | title | オプション設定 (on the panel bg) | redraw Options |
| COMMON_10_OPTION | 115 | label | panel: 既読のみ / 全て / □設定の初期化 / ×戻る (+ Slow/Fast/Min/Max) | redraw |
| COMMON_10_OPTION | 117 | menu | テキスト表示速度 / スキップ設定 / BGM 音量 / SE 音量 / ボイス音量 | redraw Text Speed / Skip / BGM / SE / Voice Volume |
| COMMON_10_OPTION | 123,124 | label | 既読のみ / 全て (selected) | redraw Read Only / All |
| COMMON_10_OPTION | 118-121,125-128 | latin | Fast/Slow/Min/Max | keep |
| COMMON_10_PARAMETER_1 | 182-184 | label | 悲しい / 怒り / 恥しい (emotions; 181 嬉しい) | redraw Sad / Angry / Shy (the 161 Latin uses Sad/Happy/Shy/Anger) |
| COMMON_10_WINDOWS | 209,210 | button | ▶オート / ▶▶スキップ | redraw Auto / Skip |
| COMMON_20_HEX_MENU | 212 | label | 好きなコマを選んで下さい / あと □ コマ | redraw |
| COMMON_20_HEX_MENU | 217,218 | menu | 再戦 / キャラクターをかえる / ヘキサイトをやめる (plain + selected) | redraw Rematch / Change Character / Quit Hexcite |
| COMMON_20_HEX_MENU | 219 | title | ヘキサイトメニュー | redraw Hexcite Menu |
| COMMON_20_HEX_MENU | 220,221 | menu | ゲームの説明 / ゲームをやめる / ゲームの再開 | redraw How to Play / Quit / Resume |
| COMMON_20_HEX_MENU | 222 | prompt | 必殺技を使いますか？ / 技名: / 効果: | redraw |
| COMMON_20_HEX_MENU | 223-226 | button | はい / いいえ (2 states) | redraw Yes / No |
| COMMON_20_HEX_OPTION | 234 | button | ×戻る | redraw Back |
| COMMON_20_HEX_OPTION | 235 | title | ゲーム設定 (orange) | redraw Game Settings |
| COMMON_20_HEX_OPTION | 240-254 | label | よわい / ふつう / つよい / あり / なし (3 colour states each) | redraw Weak / Normal / Strong / On / Off |
| COMMON_20_HEX_OPTION | 255 | label | 相手の強さ / 必殺技 | redraw Opponent / Specials |
| COMMON_20_HEX_RESULT | 277,279,282,284-286 | latin | Winner / Loser / Draw / pt | keep |
| COMMON_20_HEX_START | 299 | title | 対戦相手選択 (pink) | redraw Choose Opponent |
| COMMON_20_HEX_START | 304 | art | Tomoki's T-shirt print (色人?) | leave (character art) |
| COMMON_20_HEX_START | 321-331 | label | 戦闘服 / ??? / 私服 / 制服 / 水着 / 体操着 (grey + pink wing states) | redraw outfit names (Battle Suit / Casual / Uniform / Swimsuit / Gym Clothes) |
| COMMON_20_HEX_START | 350-354 | label | 戦闘服 / 私服 / 制服 / 水着 / 体操着 (blue wing) | redraw |
| COMMON_20_HEX_START | 332 | label | 勝敗数： 勝 敗 分 / 現在 連勝中 | redraw Record: W L D / Current streak |
| COMMON_20_HEX_START | 335-347 | card-art-text | 必殺技 + the six special-move names and effect texts (dim blue, same set as HEX_MENU 227-232) | redraw |
| COMMON_20_HEX_START | 349 | title | プレイヤー選択 (blue) | redraw Choose Player |
| COMMON_20_HEX_START | 356 | title | ゲーム選択 (orange) | redraw Choose Game |
| COMMON_20_HEX_START | 357,358 | logo | ヘキサイト / ヘキサイトES | redraw Hexcite / Hexcite ES |
| COMMON_20_HEX_START | 364 | label | □ゲーム設定 △チュートリアル | redraw Settings / Tutorial |
| COMMON_20_HEX_START | 306,333,359-362 | latin | Please Select; Player!; HEXCITE / HEXCITE ES card backs | keep |
| COMMU_00_CARD | 365-504 | latin | card fronts/backs: COMMUNICATION / EVENT / SPECIAL / PROFILE labels on character art (Tomoki's shirt print in 487-489 is art) | keep |
| COMMU_00_CARDNAME_GALLERY | 505-552 | card-name | communication card names (blue outlined), e.g. 感謝 嬉しい おしゃれ 可愛がる 育てる ツッコミ ツンデレ 甘える ストレス 羞恥心 告白 恐怖 驚く ロマン 秘密 かわいい 苦悩 思いやり 憧れ つらい 気持ちいい トラウマ 怒り 憎しみ ほめる イラ立ち やさしい お仕置き ウソ 仁義 悲しい 学ぶ 疑う 照れる 欲望 煩わしい 困る 好奇心 信じる うつくしい ワクワク 清楚 寂しい 別れ 眠る 争い 誓う 内緒 | redraw (read text off work/gimpng/<n>.png; check whether the same names exist as script text first) |
| COMMU_00_CARDNAME_GALLERY | 553-594 | card-name | event card titles (誘惑, 癒し, 成功は失敗から, 灼熱の我慢大会, 狩猟の誘い, アブない!?花火大会, ウハウハ催眠術, 秘密の水泳教室, 究極のめにう, ドキッと夏祭り, 王様だ～れだ?, 雨に降られて, ... 怒りの頂点, 乙女の恥じらい ...) + special moves 589-594 (秘密の気持ち, 最終兵器, 超々超音波振動子, そはらチョップ, 圧殺, 新大陸) | redraw |
| COMMU_00_CARDNAME_GALLERY | 595-606 | card-name | outfits 戦闘服 私服 制服 水着 体操着; full names 桜井智樹 イカロス ニンフ 見月そはら 五月田根美香子 守形英四郎; ？？？？？？ | redraw (glossary names) |
| COMMU_00_CARDNAME_GET | 607-674 | card-name | same titles in 『』 (blue, small) + profile cards 『<name> File.1-4』 for the six characters | redraw |
| COMMU_10_CARDGALLERY | 678-684 | label | gallery panels with tab + footer: プロフィール / きせかえ / 必殺技 / イベント / コミュニケーション + "<kind>カード収集率" | redraw Profile / Outfit / Special / Event / Communication + "... Cards Collected" |
| COMMU_10_CARDGALLERY | 711 | label | ○決定 ×戻る | redraw OK / Back |
| COMMU_10_CARDGALLERY | 752-775 | other | character profile text blocks, 4 per character (6 chars): 生年月日 / 血液型 / 趣味 / 身長 / 体重 / スリーサイズ / 好きな花・色・言葉・もの / 性格 / 苦手なこと / 将来の夢は? + values (multi-line) | redraw (biggest text redraw; translate as a batch first) |
| COMMU_10_CARDGALLERY | 676,677,688-706,712-750 | latin | L/R, Level 1-4, Get!!, File.1-4, digits | keep |
| COMMU_10_CHANGE | 784 | art | イカロス name tag on Ikaros's gym shirt | redraw Ikaros if legible in game (small), else leave |
| COMMU_10_COM_MENU | 788,795,804 | title | 何をする? / カード / メニュー (submenu window headers) | redraw What to do? / Cards / Menu |
| COMMU_10_COM_MENU | 789-812 | menu | buttons (2 states each): カード / ヘキサイト / メニュー / コミュニケーション / きせかえ / ギャラリー / オプション / セーブ / そうさせつめい / タイトル | redraw Cards / Hexcite / Menu / Communicate / Outfits / Gallery / Options / Save / Controls / Title |
| COMMU_10_COM_TUTORIAL | 814-819 | tutorial | 6 full tutorial pages (n/6): ゲームの目的, パラメーターの種類, パラメーターの増減, コミュニケーションカードのパラメーター, コミュニケーションカードの入手法, ゲームオーバー; titles, body text, callouts, ○次へ | redraw (dense; whole-page text) |
| COMMU_10_HELP | 947 | title | 操作説明 (on panel bg) | redraw Controls |
| COMMU_10_HELP | 949 | other | controls table: ボタン / コミュニケーション / ヘキサイト columns, per-button actions, ※アナログパッドで方向キーと同じ操作ができます | redraw (small text table) |
| COMMU_10_LEVELUPDIALOG | 951 | banner | ヘキサイトESがヘキサイトになりました!! | redraw |
| COMMU_10_LEVELUPDIALOG | 952-957 | banner | 対戦相手に ニンフ/美香子/守形 を追加!! ; フリーモードに ニンフ/美香子/守形 を追加!! | redraw |
| COMMU_10_LEVELUPDIALOG | 958 | banner | レベルアップ!! (large pink) | redraw Level Up!! |
| COMMU_20_HEX_CARD | 961,963,964 | button | ×持っていかない (big red + green + orange) | redraw Don't Take |
| COMMU_20_HEX_CARD | 966 | title | 必殺技カード選択 (green) | redraw Choose Special Card |
| COMMU_20_HEX_CARD | 967 | label | ※必殺技カードを持っていくと使用しなくても消費されます。 | redraw |
| COMMU_20_HEX_CARD | 968 | label | footer ○決定 ×戻る (tiny) | redraw |
| COMMU_20_HEX_CARD | 969-974 | label | special-move effect texts (white, same six as HEX_MENU) | redraw |
| COMMU_10_ENDING_A | 821-836 | art | ending CG polaroids (no text; 824 has a small speech-bubble doodle, check zoomed in phase 8) | leave |
| COMMU_10_ENDING_A | 837-847 | label | credits role headings: キャスト, シナリオ, プログラマー, グラフィックコーディネーター, ゲームグラフィック, グラフィック原画・彩色, 音響制作, 制作協力, スペシャルサンクス, プロデューサー, 広報 | redraw (D3: credits in English) |
| COMMU_10_ENDING_A | 848-868 | label | credits names: cast (role + voice actor, e.g. イカロス 早見沙織), staff and company names | redraw romanized (D3) |
| COMMU_10_ENDING_B | 910-926 | label | staff roll cards: 原作 水無月すう, 開発 株式会社ボトルキューブ, 開発プロデューサー, 開発進行管理, ディレクター, プランナー, スクリプター, インターフェースデザイン, サウンド, ヘキサイト提供 株式会社ジーユー, デバッグ, 説明書・パッケージデザイン, WEB制作, 製作/制作 株式会社角川書店, エグゼクティブプロデューサー, 制作総指揮, ©水無月すう/角川書店/空美町新大陸発見部 | redraw (D3) |
| COMMU_10_ENDING_B | 927 | logo | 角川書店 | leave (company logo) |
| COMMU_10_ENDING_C | 941,942 | label | ディレクター / 針生 一 (large) | redraw |
| HEXCITE | 985 | other | 仮 x4 on a sky bg (placeholder texture) | leave unless seen in game |
| HEXCITE | 1000,1001 | button | △メニュー表示 / △中断 | redraw Menu / Pause |
| HEXCITE | 1011,1012 | banner | 開始！ / 終了！ (big) | redraw Start! / Finish! |
| HEXCITE | 987 | art | Tomoki's shirt print | leave |
| HEXCITE | 995,996,999,1002,1004,1010 | latin | signatures, SPECIAL, pt, Pass! | keep |
| HEXCITE_20_HEX_RESULTANIME | 1055-1066 | result | ボロ負け!! / 負け! (6 zoom frames each) | redraw every frame (Crushing Defeat!! / Lose!) |
| HEXCITE_20_HEX_RESULTANIME | 1131-1154 | result | 引き分け / 大勝利!! / 勝ち! / チョイ勝ち (6 zoom frames each) | redraw every frame (Draw / Big Win!! / Win! / Close Win) |
| HEXCITE_20_HEX_SPECIAL | 1155-1166 | sfx | special cut-in: TOMO☆KI・TIME wipe frames (Latin) + トモキ・タイム ruby line 1162-1166 | redraw ruby line only (or blank it) |
| HEXCITE_20_HEX_SPECIAL | 1167-1187 | sfx | 最終兵器 cut-in: one kanji per texture (最 終 兵 器, ruby ア ポ ロ ン), 4-5 fade frames each | redraw as per-glyph English (layout set by the animation; RE in phase 8) |
| HEXCITE_20_HEX_SPECIAL | 1188-1198 | sfx | 超々超音波振動子 wipe frames + パラダイス＝ソング ruby | redraw |
| HEXCITE_20_HEX_SPECIAL | 1199-1206 | sfx | そはら / チョップ (fade frames) | redraw |
| HEXCITE_20_HEX_SPECIAL | 1207-1214 | sfx | 圧 / 殺 (one kanji each, fade frames) | redraw |
| HEXCITE_20_HEX_SPECIAL | 1215-1229 | sfx | 新 / 大 / 陸 (one kanji each, fade frames) | redraw |
| HEXCITE_20_HEX_TUTORIAL | 1264 | label | このラインにコマを置いて (red) | redraw |
| HEXCITE_20_HEX_TUTORIAL | 1265-1289 | tutorial | Hexcite tutorial panels (orange boxes, dense text): ゲームの目的, 得点について, ①ボード ②持ちコマ ③得点 callouts, 順番決め, コマの配布, 操作手順, ヘキサイト(ES)の初手の置き方, コマの置き方, ボーナスゾーン, 羽マークの獲得, 必殺技の発動, それではゲームを進めてみてください, パス, 減点, ゲームで勝つためのコツ (3 pages) | redraw (dense; second-largest text redraw) |
| IMG_BG | 1290-1312 | art | backgrounds; shop/festival-stall signage in 1301, 1306, 1307 is scenery | leave |
| IMG_BG | 1313-1316 | tutorial | communication tutorial pages again (パラメーターの種類, パラメーターの増減, コミュニケーションカードの入手法, ゲームオーバー) as full-screen images | redraw (same text as COM_TUTORIAL 814-819) |
| IMG_BG | 1318 | other | 羽根画像（仮） (grey placeholder) | leave unless seen in game |
| IMG_EV | 1622-1672 | art | event CGs (no drawn captions; check 1665/1670 zoomed for onomatopoeia in phase 8) | leave |
| IMG_GO | 1674-1678 | banner | おわり？ (game over, 5 frames) | redraw The End? |
| COMMON_20_HEX_MENU | 227-232 | card-art-text | special-move cards with name (ruby) + effect text: TOMO☆KI・TIME (トモキ・タイム), 最終兵器(アポロン), 超々超音波振動子(パラダイス・ソング), そはらチョップ, 圧殺, 新大陸 | redraw names + effects (glossary) |

No-text in surveyed sheets: COMMON_10_PARAMETER_0 134-149, 151-160, 162-178; COMMON_0 0-2; TITLE 185-187 (Bottle Cube, CRI, Gu logos: Latin), 190-191.

| IMG_CH | 1319-1621 | art | character sprites + face/mouth parts (no text; shirt prints are art) | leave |

No-text elsewhere: COMMON_10_LOADING 90-111, 113; COMMON_10_WINDOWS 203-208; COMMON_20_HEX_RESULT digits 257-295;
COMMU_10_ENDING 820; ENDING_A 869-909 (wings, wipe shapes); ENDING_B 928-935; ENDING_C 936-946 except 941-942;
FREEMODE 976-984 (digits); HEXCITE_1 1033-1054; RESULTANIME 1067-1130 (stars); HEX_SPECIAL 1230-1263; IMG_GO 1679-1700.

## Survey status
Complete (2026-11-22): every sheet in work/gimpng opened and listed above. Exact text for the dense groups (card names,
profiles 752-775, both tutorials, credits) is read off `work/gimpng/<n>.png` when that group is redrawn in phase 8;
first check whether the same strings also exist as script/EBOOT text (card names, special-move effects) so the
translation is shared. Animated groups (RESULTANIME, HEX_SPECIAL, IMG_GO) need every frame redrawn.
Video: none (no .pmf on the disc). Movies with burned-in text: none.
