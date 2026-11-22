# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All D1-D7 came from the owner's standing answers injected into the one-shot run (Orca task brief).

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-22 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). |
| D2 | 2026-11-22 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist (anime: Heaven's Lost Property, Funimation), else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-22 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-22 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms; engine work before abbreviating. |
| D5 | 2026-11-22 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); keep the Japanese logo only if no official English version exists. |
| D6 | 2026-11-22 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-11-22 | Existing saves / states | none provided | None; build the debug tool as usual. |
| D8 | 2026-11-22 | Literal `~` for ～ (phase 6 review: 181 lines had it against the rule) | ban everywhere; allow for Mikako only; allow freely | Agent default under the pre-approved run (D6): Mikako only (her lines, ??? lines that are her, imitations of her). Her drawl is a character trait and 134 of her 305 lines use it; others' 43 lines were rewritten (fix008: stretched words or dropped). Linted in tools/batches.py. |
| D9 | 2026-11-22 | Graphics wording (wave-1 agents differed) | per agent; one term each | Agent default (D6): きせかえ = "Outfit" (cards, gallery tab, Communication button "Outfits"); 体操着 = "Gym Wear" ("Gym Clothes" doesn't fit the 51 px outfit label); 持ちコマ = "pieces" (never "hand"), special-move effect lines identical in hexmenu/hexstart/hexcard; Hexcite record line keeps W/L/D (standard sports notation, digits are game-drawn); card counter "card(s) obtained!" (count is game-drawn, no plural suffix glued on). |
| D10 | 2026-11-22 | Title logo そらのおとしもの (D5: keep only if no official English version) | keep kana logo; redraw as "Heaven's Lost Property" | Agent default (D6), open to the user: keep it. The English logo belongs to the anime; this game had no English release, the logo already carries the romaji "SORA NO OTOSHIMONO", and the patch title (PARAM.SFO) is "Sora no Otoshimono: DokiDoki Summer Vacation". Subtitle and © line are English. |
| D11 | 2026-11-23 | Publish v1.0 | publish; hold | User: "publish". GitHub release v1.0 created with the patch zip (README as notes); repo visibility (private) left unchanged. |
