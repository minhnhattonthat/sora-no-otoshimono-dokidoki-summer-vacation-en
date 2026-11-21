# Synopsis: Sora no Otoshimono - DokiDoki Summer Vacation (PSP, 2010)

Built from a read of all SC0 and SC9, samples of SC1-SC4, docs/re/debug.md and graphics.md. "Unclear" = unverified.

## Premise
- Gag-comedy side story of Minazuki Suu's manga / the anime "Heaven's Lost Property", set in Sorami Town during the
  summer break. Tomoki is a middle-schooler (14).
- Prologue (SC00000): Tomoki "loves peace and the ordinary", but is surrounded by Sohara (killer chop), Sugata
  (flying pervert senpai chasing the New World), Mikako (student council president who plans dangerous events) and
  two Angeloids living at his house: Ikaros (calls him Master, airheaded) and Nymph (tsundere, came after Ikaros).
- Core plot: playing the board game Hexcite, Tomoki tells Ikaros to "reset everything back to the start". She obeys
  literally, initialises herself and loses her memories back to the night they met (SC00003). The game is about
  getting them back: a backup circuit exists but nobody knows how to trigger it (Nymph); the group tries
  re-enacting happy memories.
- Hexcite: territory-grabbing board game with polygon pieces (triangle, parallelogram, trapezoid, hexagon); Ikaros, a
  strategic Angeloid, is a prodigy. Free Mode lets you play it against Ikaros, Nymph, Sohara, or Sugata+Mikako.
- Communication Mode: hub with Card / Hexcite / Menu / Communicate / Outfits / Gallery. Four chapters (Level 1-4),
  20 turns each. Four emotion params: Happy 嬉しい / Sad 悲しい / Shy 恥しい / Anger 怒り. Meet every target before the
  turns run out -> "Level up!!" and a chapter-end script; fail -> bad ending (game over). Hexcite wins give cards;
  using a card plays an event script.

## Structure
- SC0: prologue + chapter-end scenes. SC000x0 plays when chapter x ends (x=0: prologue); SC000x1/x2 are the two
  branches of a choice; SC000x3 merges. Choices: 土下座 / ちゃぶ台返し; 頼む / いらない; じゃあ頼む / 別にいい;
  ニンフ、頼む / 守形先輩、お願いします.
- SC1: 19 card-event scenarios (SC10000..SC10180; x0 = setup with a 3-way choice, x1-x4 = outcomes). Daily-life
  gags: Sugata's hang-glider test, endurance contest, beach, hypnosis with a 5-yen coin, Sohara learning to swim,
  Mikako's stamina hotpot, the next town's festival, drunk Tomoki, pig-trotter taiyaki, Nymph sleeping / snacking,
  BBQ cleanup, Sohara wanting to be an idol (bunny outfit), Sugata and Mikako finding a "meteor" with a baby (a prank,
  SC10154), an Ikaros/Nymph body swap, carp streamer, chicks swallowing the school. Ikaros here does not mention the
  memory loss.
- SC2: 16 events (SC20000..SC20150), amnesiac Ikaros: making her smile, the amnesiac "Master" greeting, post office,
  summer heat, TV, Sohara's birthday, "orders are absolute" runaway (SC20130), a love-talk card (SC20150).
- SC3: ~50 "lessons" (SC30000..SC34900; x00 setup, x10/x20/x30 outcomes): Tomoki teaches Ikaros a concept or
  emotion (thanks, feelings, comedy, fear, trauma, hatred, praise, lies, shyness, desire, trust, beauty, quarrels,
  dreams, seduction, massage...). They raise the emotion params; the others drop in as helpers.
- SC4: system lines. 40000-40040 outfit-change cards (Uranus Queen mode, casual, school uniform, swimsuit...); 40100
  Nymph explains event cards; 40200-40411 Hexcite match banter (pre-match, win/lose/draw for each character);
  40500 choice はじめから読む / ゲームを始める.
- SC9: five endings.
- EBOOT (script/eboot.tsv): Nymph's hub-menu help lines (0x088C07B4..), Hexcite post-match reactions ending in /K
  (0x088DCAD0.., one set per opponent), Hexcite menu help bar, save-data dialogs.

### Chapter ends (SC0)
- SC00000-03 (prologue): Hexcite at Tomoki's house. Ikaros secretly plays easy so Tomoki wins; he tells her never to
  throw a game; she then crushes him. Tomoki cheats (grovels / flips the table) and says "reset". Ikaros obeys:
  imprinting starts over and she greets him as a new Master. Everyone agrees to re-enact happy memories. Mikako's
  "shock therapy" involves a gun.
- SC00010-13 (chapter 1): re-enacting the autumn-festival cork-gun survival game, 10 million yen prize (Tomoki wants
  "Oppai of the World" DVDs). Ikaros banned from flying and her Gatling gun. Sugata+Mikako hunt them; Nymph flanks.
  Sohara, shot when Tomoki betrays her, is saved by Ikaros, who remembers Sohara.
- SC00020-23 (chapter 2): Nymph takes Ikaros to the field where they once fought and tries Paradise Song / Aegis /
  Uranus Queen to trigger memories. Ikaros refuses to attack ("you are family"). Nymph confesses her selfish wish;
  Tomoki arrives and says both are his family. Ikaros remembers Nymph.
- SC00030-33 (chapter 3): the desert-island re-enactment. Seeing Tomoki hold Nymph's hand, Ikaros feels pain in her
  power reactor, fears she is broken and flees in stealth. Nymph can't fly (clipped wings); Sugata can't glide
  (headwind, dusk). Tomoki finds her on foot. She remembers everyone but Tomoki and wants his memories back.
- Chapter 4 -> SC90010.

### Endings (SC9)
- SC90010 Ikaros (true ending): out of ideas, Sugata suggests a kiss; everyone objects. A date at the sea
  (watermelon, holding hands); Ikaros asks him for a kiss; friends interrupt; her memory returns ("a year since I met
  you, Master"). Party at Mikako's; staff roll.
- SC90020 bad ending (targets missed): Hexcite, give-up-or-kiss debate; Sohara and Nymph chop in; the blow starts the
  backup circuit... and Ikaros restarts with "Nice to meet you... Master": back to square one.
- SC90030 Ikaros after-story: she thanks him, he sleeps; she turns visitors away; on Mikako's advice she sleeps
  beside him; the friends burst in.
- SC90040 Nymph after-story: the sea, snacks, no swimsuit, hand-holding, "call me Tomoki" vs Master; Mikako walking
  her dog teases them; Nymph shoves him and storms off.
- SC90050 Sohara after-story: seaside stroll, a panty-flash gag (chop), she kisses his cheek ("special, because it's
  you"); they watch the sea.

## Who is who (voices: docs/style-reference.md)
- Tomoki Sakurai 桜井智樹: perverted but kind. 俺; お前 to Ikaros/Nymph; 先輩 / 守形先輩; 会長. "～っス" to seniors,
  "チクショー", "ぬわーっ!", lecher laughs ("グヒョヒョ").
- Ikaros イカロス (Type Alpha Angeloid, 愛玩用 = pet-class): 私; マスター (amnesiac: マイマスター); stiff です/ます,
  ellipsis pauses, 了解しました, 申し訳ありません. Calls Nymph ニンフ, Sohara そはらさん, Mikako 会長さん. Amnesiac mode:
  robotic ("なんなりと", "命令は絶対"). In body-swap events the speaker label is the body, the voice the other
  character's (SC10161/10163).
- Nymph ニンフ (Type Beta, electronic warfare): 私; トモキ, そはら, 守形, アルファー. Tsundere: ～わよ, ～じゃない, アンタ,
  バカトモキ, もう知らない!; loves snacks; secretly wants Tomoki as her Master; Synapse trauma.
- Sohara Mitsuki 見月そはら: childhood friend next door. 私; トモちゃん, イカロスさん, ニンフさん, 守形先輩. Chop;
  "トモちゃんのエッチ!"; gentle ～だよ / ～なんだから; jealous at times.
- Eishiro Sugata 守形英四郎: senior, New World Discovery Club, hang glider. 俺; lecturing ～だ / ～のだ, フム, ウム;
  智樹, 見月, 美香子. Deadpan.
- Mikako Satsukitane 五月田根美香子: student council president, daughter of the Satsukitane yakuza house (五月田根組),
  sadist. Drawl ～かしら～, あら～, ふふっ; 桜井君, 英くん (Sugata), イカロスちゃん, ニンフちゃん.

## Late reveals (don't leak early)
- The amnesia is self-inflicted (obeying "reset"); recall order: Sohara (SC00013), Nymph (00023), the others (00033),
  Tomoki last (90010).
- Ikaros's chest pain (SC00030) = feelings for Tomoki, never stated outright: keep it an "error".
- Nymph's wish that Tomoki become her Master; her fear of losing him.
- The baby/meteor is a prank (SC10154).
- Unclear: "マスターのマスター" in SC00033: translate literally ("Master's master").
