"""gfx group hextutorial (HEXCITE_20_HEX_TUTORIAL): the line hint (1264) and the tutorial panels (1265-1289).

Panels are yellow cards with a faint triangle lattice (period 20.5 px across) and a vertical gradient. Each image is a list
of elements in SPEC: (kind, rect, options). The Japanese inside rect is removed by unpaint() (every pixel that differs from
the median of the same row shifted by +-41 px k times is text -> replaced by that median, so the lattice carries on), then
the English is drawn inside the same rect. Row en = the elements' texts joined by "|" (\\n = forced line break).
Kinds: title (orange, white outline), sub / key / get / head (red / green headings), body (grey 13 px block, auto
condensed), cap (grey caption block centred on cx), pic (a line drawn into the 192x24 hint, 1264).
Wording: see TEXT. Pieces = コマ; Circle/Cross/Square button; wing mark = 羽マーク; Key Point! = ポイント！.
"""
import numpy as np
from PIL import Image, ImageFilter

import gfx
from gfx_hexstart import text

typeset = gfx.typeset
WHITE = (255, 255, 255, 255)
ORANGE = (255, 107, 2, 255)
RED = (255, 0, 0, 255)
RED2 = (255, 53, 53, 255)
GREEN = (8, 143, 68, 255)
GREEN2 = (35, 145, 0, 255)
BLUE = (72, 71, 254, 255)
GRAY = (83, 83, 83, 255)
HALO = (255, 240, 230, 255)
FT = "os:800:85"

# ---- text: n -> (jp, en); elements joined by "|" ----
TEXT = {
    1264: ("このラインにコマを置いて", "Place a piece on this line"),
}
_OBJ_JP = ("ゲームの目的|盤上に自分のコマを置き、得点を得ます。\\nコマはCOMと交互に置いていき、お互いにコマが置けなくなると\\nゲームは終了となります。\\nゲームが終了した時点で得点の高いプレイヤーが勝利です。|得点について|"
           "ボードにコマを置こうとすると出現する緑のラインが得点となる辺です。この辺の数 ×5pt がコマを置いたときの得点になります。赤いラインは得点にならない辺です。ラインが出ないところにコマは置けません。")
_OBJ_EN = ("Object of the Game|Place your pieces on the board to score points. You and your opponent take turns placing pieces, and the game ends "
           "when neither of you can place any more. The player with the higher score at that point wins.|About Scoring|"
           "Lines appear when you try to place a piece. Green lines are the edges that score. Placing a piece scores 5 pt x the number of green "
           "edges. Red lines are edges that don't score. You can't place a piece where no lines appear.").replace(" x ", " × ")
for n in (1265, 1266):
    TEXT[n] = (_OBJ_JP, _OBJ_EN)
for n in (1267, 1268):
    TEXT[n] = ("得点|自分と相手の得点を表示します|持ちコマ|持ちコマの数を表示します|ボード|コマを置くボードです",
               "Score|Shows your score and\\nyour opponent's|Pieces|Shows how many\\npieces you have|Board|Where you place pieces")
TEXT[1269] = ("順番決め|ゲームを開始するとプレイヤーの「先攻」「後攻」を決めます。手ゴマ置き場が最後に光ったプレイヤーが先攻となります。",
              "Turn Order|When the game starts, it decides who goes “first” and who goes “second”. The player whose piece area lit up last goes first.")
TEXT[1270] = ("コマの配布|順番が決まると、プレイヤーにコマが配られます。コマの配布時にボーナスとして好きなコマを選べることがあります。",
              "Dealing Pieces|Once the turn order is set, pieces are dealt to the players. Sometimes you get a bonus when pieces are dealt: you can choose a piece you like.")
_CTL_JP = ("操作手順|ボードへ置きたい持ちコマにカーソルを合わせ、○ボタンでつかみます。つかんだコマをキャンセルするには、×ボタンを押して下さい。|"
           "コマをつかんだ状態でLボタンかRボタンを押すとコマが回転します。ボード上の置ける場所へコマを移動し、○ボタンで置きます。得点が加点され、相手の番になります。|：決定|：キャンセル")
_CTL_EN = ("Controls|Move the cursor to the piece you want to place and press the Circle button to pick it up. To cancel a piece you have picked up, press the Cross button.|"
           "While holding a piece, press the L or R button to rotate it. Move it to where you want it on the board and press the Circle button to place it. "
           "Your score is added and it becomes your opponent's turn.|: OK|: Cancel")
for n in (1271, 1272):
    TEXT[n] = (_CTL_JP, _CTL_EN)
TEXT[1273] = ("ヘキサイトの初手の置き方|「ヘキサイト」では初めの1手のみボード中央にある六角形の内側に接するようにコマを置かなければなりません。|コマを置いてみてください\\n＊コマが置けるところにはラインが出現します。",
              "Placing Your First Piece in Hexcite|In “Hexcite”, only your first move must be placed so that it touches the inside of the hexagon at the center of the board.|"
              "Try placing a piece.\\n*Lines appear where a piece can be placed.")
TEXT[1274] = ("ヘキサイトESの初手の置き方|「ヘキサイトES」では初手に限らず外周の辺に接するようにも置くことが出来ます。|コマを置いてみてください\\n＊コマが置けるところにはラインが出現します。",
              "Placing Your First Piece in Hexcite ES|In “Hexcite ES”, a piece can also be placed touching the outer edges of the board, not just on the first move.|"
              "Try placing a piece.\\n*Lines appear where a piece can be placed.")
for n in (1275, 1276):
    TEXT[n] = ("コマの置き方|コマを置くときは、ボードに置かれているコマの辺に置きたいコマが接するように置かなければなりません。ボードのコマに対し、置きたいコマが辺からはみ出ている場合は置けません。L・Rボタンでコマを回転させて置ける位置を探しましょう。|ポイント！|コマが置けるところには赤と緑のラインが出ます。",
               "How to Place Pieces|When you place a piece, one of its edges must touch an edge of a piece already on the board. You can't place a piece if it "
               "sticks out past the edges of the pieces on the board. Rotate pieces with the L and R buttons to find a spot where they fit.|Key Point!|"
               "Red and green lines appear where you can place a piece.")
for n in (1277, 1278):
    TEXT[n] = ("得点について|緑のラインが得点となる辺で、この辺の数 ×5pt がコマを置いたときの得点になります。赤いラインは得点にならない辺です。ラインが出ないところにコマは置けません。|ゲット|ゲット",
               "About Scoring|Green lines are the edges that score. Placing a piece scores 5 pt × the number of green edges. Red lines are edges that don't score. "
               "You can't place a piece where no lines appear.|Get!|Get!")
_BZ_B = ("ボーナスポイントはこのボーナスゾーンを最後に埋め尽くしたプレイヤーの得点として通常得点に加算して与えられます。",
         "Bonus points go to the player who finishes filling a bonus zone, and are added to that player's normal score.")
TEXT[1279] = ("ヘキサイトのボーナスゾーン|「ヘキサイト」では、下図の６つの六角形がボーナスゾーンです。\\n" + _BZ_B[0],
              "Hexcite Bonus Zones|In “Hexcite”, the six hexagons in the diagram below are bonus zones.\\n" + _BZ_B[1])
TEXT[1280] = ("ヘキサイトESのボーナスゾーン|「ヘキサイトES」では、下図の６つの三角形がボーナスゾーンです。\\n" + _BZ_B[0],
              "Hexcite ES Bonus Zones|In “Hexcite ES”, the six triangles in the diagram below are bonus zones.\\n" + _BZ_B[1])
TEXT[1281] = ("羽マークの獲得|必殺技はヘキサイト盤上の羽マークを取らないと使うことが出来ません。羽マークが置かれているマスにコマを置いたプレイヤーが羽マーク獲得となります。羽マークを獲得すると必殺技が使えるようになります。羽マークは相手も獲得でき、相手に取られると必殺技を使用してくるかもしれません。",
              "Getting Wing Marks|You can't use a special move until you take a wing mark on the Hexcite board. The player who places a piece on a space with a wing mark "
              "takes it, and once you have a wing mark you can use your special move. Your opponent can take wing marks too, and if they do, they may use a special move on you.")
TEXT[1282] = ("必殺技の発動|自分の手番のときに□ボタンで必殺技が使えるようになり、必殺技は1度使うと消費されます。各キャラクター1人につき、1つの必殺技を持っています。コミュニケーションモードではカードを使うことで智樹が他のキャラクターの必殺技を使うことができます。",
              "Using Special Moves|On your turn, press the Square button to use your special move. A special move is used up after one use. Each character has one special move. "
              "In Communication Mode, Tomoki can use other characters' special moves by using cards.")
TEXT[1283] = ("それではゲームを進めてみてください", "Now, try playing the game.")
TEXT[1284] = ("パス|プレイヤーはコマを置くことができない場合は自動的にパスされます。お互いの持ちコマがなくなるか、どのプレイヤーもボードにコマを置くことができなくなると、その時点でゲームは終了となります。",
              "Pass|If a player can't place a piece, they pass automatically. The game ends when both players run out of pieces, or when neither player can place any piece on the board.")
_CAP = {"小三角": "Small Triangle", "大三角": "Large Triangle", "六": "Hexagon", "小台": "Small Trapezoid", "大台": "Large Trapezoid",
        "小ひ": "Small Rhombus", "大ひ": "Large Rhombus"}
_CAPJ = {"小三角": "三角形（小）", "大三角": "三角形（大）", "六": "六角形", "小台": "台形（小）", "大台": "台形（大）", "小ひ": "ひし形（小）", "大ひ": "ひし形（大）"}
_PEN = ("減点|ゲームが終了したときの余りコマが減点の対象となります。減点は余りコマの１辺につき -5pt です。|", "Penalty Points|Pieces left over when the game ends count against you. Each edge of a leftover piece costs -5 pt.|")
_K1285 = ["小三角", "大三角", "六", "小台", "大台", "小ひ", "大ひ"]
_K1286 = ["小三角", "大三角", "六", "小台", "小ひ"]
TEXT[1285] = (_PEN[0] + "|".join(_CAPJ[k] for k in _K1285), _PEN[1] + "|".join(_CAP[k] for k in _K1285))
TEXT[1286] = (_PEN[0] + "|".join(_CAPJ[k] for k in _K1286), _PEN[1] + "|".join(_CAP[k] for k in _K1286))
_TIPJ = "ゲームで勝つためのコツ"
TEXT[1287] = (_TIPJ + "|必殺技を有効活用する|羽マークを獲得すると固有の必殺技が使えます。\\n必殺技を使うとコマが置きやすくなったりなど、ゲームが有利になります。\\nまれに、自分に不利になることもあるので使うタイミングには注意してください。|"
              "ボーナスはなるべく逃さない|ボーナスの得点で勝敗は大きく変わります。\\nボーナスはなるべく取り、できるだけ相手に取らせないように気をつけましょう。|"
              "相手のコマを置けなくする|置くことが出来ずに余ったコマは最後に減点となります。\\n相手がコマを置けないようにゲームを進めることも勝利への近道となります。|"
              "大きなコマと六角形はなるべく残さない|大きなコマは後半で置けなくなることがあります。なるべく早く置くことが得策でしょう。\\nまた、六角形のコマを残すと -30pt となるため、残さないよう気をつけましょう。",
              "Tips for Winning|Make the Most of Special Moves|Taking a wing mark lets you use your character's special move. Special moves can make pieces easier to place and otherwise swing the game in your favor. "
              "Occasionally one can work against you, so watch your timing.|"
              "Don't Miss the Bonuses|Bonus points can swing the whole game. Take bonuses whenever you can, and take care not to let your opponent get them.|"
              "Keep Your Opponent from Placing|Pieces left over at the end count against you. Playing so that your opponent can't place their pieces is also a shortcut to victory.|"
              "Avoid Keeping Big Pieces and Hexagons|Big pieces can become impossible to place later on, so it's best to place them early. Also, a leftover hexagon costs -30 pt, so try not to keep one.")
TEXT[1288] = (_TIPJ + "|小さなコマで邪魔をする|ポイント！|小さなコマを使って、相手のコマを置けなくする|相手は三角形を置きたい|ひし形を置いて邪魔をする",
              "Tips for Winning|Block Your Opponent with Small Pieces|Key Point!|Use small pieces to keep your opponent from placing theirs|Opponent wants to place a triangle|Place a rhombus to block them")
TEXT[1289] = (_TIPJ + "|効率よくボーナスを取る|ポイント！|相手のコマを見て、ボーナスをゲットする|ひし形と三角形で\\nボーナスポイントが\\n取れそうなとき|相手のコマが\\n無くなるときを狙って|自分のコマを置いて\\nボーナスゲット！",
              "Tips for Winning|Collect Bonuses Efficiently|Key Point!|Watch your opponent's pieces and take the bonus|When a rhombus and\\na triangle could win\\nyou bonus points|Aim for the moment\\nyour opponent runs\\nout of pieces|Place your piece\\nand get the bonus!")


# ---- layout: n -> [(kind, rect, opts)] in the order of the "|" parts ----
def _t(rect=(10, 8, 330, 22), x=16, base=23):
    return ("title", rect, dict(x=x, base=base))


def _b(rect, top, x, maxw, lines, pitch=16, hang=None, cand=None, kind="body", size=13):
    return (kind, rect, dict(top=top, x=x, maxw=maxw, lines=lines, pitch=pitch, hang=hang, cand=cand, size=size))


def _cap(cx, row, rect_y, base, w=78):
    return ("cap", (round(cx - w / 2), rect_y, w, 20 if row == 1 else 24), dict(cx=cx, base=base, cand=(46, 416)))


_C_ROW1 = (128, 137)
_C_ROW2 = (209, 220)
SPEC = {
    1264: [("pic", (0, 0, 192, 24), {})],
    1267: [],
    1269: [_t((10, 8, 310, 22)), _b((14, 35, 310, 56), 37, 24, 290, 3, 17)],
    1270: [_t((10, 8, 310, 22)), _b((14, 35, 310, 56), 37, 24, 290, 3, 17)],
    1273: [_t((10, 8, 300, 22)), _b((14, 33, 356, 38), 35, 19, 346, 2, 17), _b((14, 85, 356, 38), 87, 19, 346, 2, 16)],
    1283: [("big", (8, 8, 296, 30), dict(x=20, base=31, cand=(14, 298)))],
    1282: [_t((10, 8, 300, 22)), _b((14, 33, 356, 90), 35, 20, 350, 5, 17)],
    1284: [_t((10, 8, 300, 22)), _b((14, 33, 356, 90), 35, 20, 350, 5, 17)],
}
SPEC[1274] = SPEC[1273]
_PANEL_T = _t((10, 8, 330, 22))
SPEC[1265] = [_PANEL_T, _b((14, 29, 404, 68), 31, 20, 388, 4),
              ("sub", (24, 106, 170, 22), dict(x=30, base=123)),
              _b((24, 129, 254, 98), 132, 30, 246, 6)]
SPEC[1266] = SPEC[1265]
SPEC[1267] = [("cw", (37, 56, 98, 17), dict(x=38, base=69, colour=GREEN)),
              _b((17, 74, 120, 36), 77, 21, 114, 2, 17, kind="cb", size=12),
              ("cw", (71, 146, 84, 18), dict(x=73, base=159, colour=BLUE)),
              _b((50, 165, 104, 38), 168, 56, 96, 2, 17, kind="cb", size=12),
              ("cw", (350, 150, 120, 19), dict(x=353, base=164, colour=RED2)),
              _b((329, 170, 142, 18), 172, 334, 132, 1, 17, kind="cb", size=12)]
SPEC[1268] = SPEC[1267]
SPEC[1271] = [_PANEL_T,
              _b((8, 35, 410, 40), 37, 29, 380, 2, 17, hang=("1.", 12)),
              _b((8, 77, 410, 52), 79, 29, 380, 3, 16, hang=("2.", 12)),
              ("key", (73, 137, 46, 19), dict(x=75, base=151, cand=(20, 270))),
              ("key", (139, 137, 82, 19), dict(x=141, base=151, cand=(20, 270)))]
SPEC[1272] = SPEC[1271]
SPEC[1275] = [_PANEL_T, _b((14, 32, 404, 68), 34, 20, 392, 4),
              ("key", (196, 139, 100, 20), dict(x=200, base=153)),
              _b((196, 160, 190, 34), 162, 200, 184, 2, cand=(196, 386))]
SPEC[1276] = SPEC[1275]
SPEC[1277] = [_PANEL_T, _b((14, 32, 404, 68), 34, 20, 392, 4),
              ("get", (122, 213, 50, 22), dict(x=125, base=228, cand=(90, 410))),
              ("get", (294, 213, 50, 22), dict(x=297, base=228, cand=(90, 410)))]
SPEC[1278] = SPEC[1277]
SPEC[1279] = [_PANEL_T, _b((14, 32, 404, 52), 34, 21, 390, 3)]
SPEC[1280] = SPEC[1279]
SPEC[1281] = [_PANEL_T, _b((14, 32, 404, 100), 34, 20, 392, 6)]
SPEC[1285] = [_PANEL_T, _b((14, 32, 404, 36), 34, 20, 392, 2),
              _cap(83.5, 1, 130, 142), _cap(159.5, 1, 130, 142), _cap(311.5, 1, 130, 142),
              _cap(100, 2, 209, 222), _cap(174, 2, 209, 222), _cap(246, 2, 209, 222), _cap(322, 2, 209, 222)]
SPEC[1286] = [_PANEL_T, _b((14, 32, 404, 36), 34, 20, 392, 2),
              _cap(83.5, 1, 130, 142), _cap(159.5, 1, 130, 142), _cap(311.5, 1, 130, 142),
              _cap(178, 2, 209, 222), _cap(258, 2, 209, 222)]
_TIPT = ("tip", (262, 6, 210, 26), dict(x=459, base=24))


def _head(top, base):
    return ("head", (33, top, 420, 21), dict(x=35, base=base))


def _tb(rect, top, lines):
    return _b(rect, top, 18, 450, lines, kind="body", size=12)


SPEC[1287] = [_TIPT, _head(17, 32), _tb((14, 36, 454, 50), 38, 3), _head(92, 106), _tb((14, 111, 454, 34), 114, 2),
              _head(152, 166), _tb((14, 171, 454, 34), 173, 2), _head(212, 226), _tb((14, 231, 454, 34), 233, 2)]
_KEY = ("key", (46, 66, 100, 22), dict(x=50, base=81))
_CAP12 = dict(kind="body", size=12)
SPEC[1288] = [_TIPT, ("head", (33, 34, 420, 22), dict(x=37, base=50)), _KEY,
              _b((46, 87, 400, 17), 90, 50, 390, 1, 16, cand=(40, 440), kind="body", size=12),
              ("cap1", (50, 127, 196, 20), dict(cx=147, base=141, cand=(40, 440))),
              ("cap1", (274, 127, 200, 20), dict(cx=374.5, base=141, cand=(40, 470)))]
SPEC[1289] = [_TIPT, ("head", (33, 34, 420, 22), dict(x=37, base=50)), _KEY,
              _b((46, 87, 400, 17), 90, 50, 390, 1, 16, cand=(40, 440), kind="body", size=12),
              ("capn", (28, 120, 112, 46), dict(cx=84, top=124, pitch=13, cand=(24, 140))),
              ("capn", (170, 120, 122, 46), dict(cx=230, top=124, pitch=13, cand=(166, 300))),
              ("capn", (332, 120, 110, 46), dict(cx=388, top=124, pitch=13, cand=(330, 442)))]


def rows():
    """(n, jp, en, rects) of every row (gfx/hextutorial.tsv)."""
    return [(n, jp, en, ";".join(",".join(map(str, r)) for _, r, _ in SPEC[n]) if n != 1264 else "")
            for n, (jp, en) in sorted(TEXT.items())]


# ---- erasing ----
def unpaint(src, dst, rect, cand=None, period=41, thr=18, grow=2, kmax=14):
    """Replace the lettering in rect of dst (an RGBA array copied from src) with the lattice carried across in x by `period`."""
    x, y, w, h = rect
    cx0, cx1 = cand or (x, x + w)
    xs0 = np.arange(x, x + w)
    stack = []
    for k in range(-kmax, kmax + 1):
        if k == 0:
            continue
        xs = xs0 + k * period
        ok = (xs >= cx0) & (xs < cx1)
        if not ok.any():
            continue
        c = np.full((h, w, 3), np.nan)
        c[:, ok] = src[y:y + h, xs[ok], :3]
        stack.append(c)
    band = src[y:y + h, cx0:cx1, :3].astype(float)
    isbg = (band[..., 0] >= 240) & (band[..., 1] >= 190) & (band[..., 2] >= 90) & (band[..., 2] <= 228)  # yellow panel, not lettering
    rowmed = np.stack([np.median(r[b], axis=0) if b.sum() >= 4 else np.median(r, axis=0) for r, b in zip(band, isbg)])[:, None, :]
    cands = np.stack(stack)
    cands[np.abs(cands - rowmed).max(axis=3) > 14] = np.nan  # only background-like candidates (not other lettering)
    with np.errstate(all="ignore"), __import__("warnings").catch_warnings():
        __import__("warnings").simplefilter("ignore")
        med = np.nanmedian(cands, axis=0)
    med = np.where(np.isnan(med), rowmed, med)
    cur = src[y:y + h, x:x + w, :3].astype(float)
    mask = (np.abs(cur - rowmed).max(axis=2) > thr).astype("uint8") * 255
    mask = np.array(Image.fromarray(mask).filter(ImageFilter.MaxFilter(2 * grow + 1))) > 0
    reg = dst[y:y + h, x:x + w]
    reg[mask, :3] = med[mask].round().astype("uint8")
    reg[mask, 3] = 255
    return int(mask.sum())


# ---- lettering ----
def fit_block(s, size, maxw, maxlines, hang_w=0):
    """-> (font name, size, lines) : first (size, width axis) at which the paragraphs wrap into <= maxlines lines of <= maxw."""
    paras = s.replace("\\n", "\n").split("\n")
    full, maxw = maxw, maxw - 8  # drawn with 1 extra px per word space
    for sz, wd in ((size, 100), (size, 92), (size, 85), (size, 80), (size, 75), (size - 1, 80), (size - 1, 75)):
        f = f"os:600:{wd}"
        lines = []
        for p in paras:
            ln = typeset.wrap(p, f, sz, maxw).split("\n")
            lo, hi = 1, maxw
            while lo < hi:
                mid = (lo + hi) // 2
                if len(typeset.wrap(p, f, sz, mid).split("\n")) <= len(ln):
                    hi = mid
                else:
                    lo = mid + 1
            lines += typeset.wrap(p, f, sz, hi).split("\n")
        if len(lines) <= maxlines and all(typeset.font(f, sz).getlength(t) + t.count(" ") <= full for t in lines):
            return f, sz, lines
    raise ValueError(f"does not fit {maxlines} lines x {maxw}px: {s}")


def gtext(layer, s, f, sz, x, base, align="l", gap=0, halo=True):
    """Grey body text with the original's 1 px pale halo (dilated by hand: PIL's stroker leaves ruled lines on condensed
    variable-font instances)."""
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    text(tmp, s, f, sz, [(0, GRAY)], x, base, align, gap=gap)
    if halo:
        ring = Image.new("RGBA", layer.size, HALO)
        ring.putalpha(tmp.getchannel("A").filter(ImageFilter.MaxFilter(3)))
        layer.alpha_composite(ring)
    layer.alpha_composite(tmp)
CHOSEN = {}


def _draw_el(layer, kind, rect, o, s, n):
    rx, ry, rw, rh = rect
    if kind == "title" or kind == "big" or kind == "tip":
        size = {"title": 15, "big": 17, "tip": 18}[kind]
        for wd in (85, 80, 75, 70):
            f = f"os:800:{wd}"
            if typeset.font(f, size).getlength(s) + 6 <= rw - 4:
                break
        else:
            raise ValueError(("title", n, s))
        text(layer, s, f, size, [(2, WHITE), (0, ORANGE)], o["x"], o["base"], "r" if kind == "tip" else "l", gap=2)
    elif kind in ("sub", "key", "get", "head", "cw"):
        size = 14 if kind != "cw" else 13
        col, outline = {"sub": (RED, 2), "key": (RED, 2), "get": (GREEN2, 2), "head": (RED2, 2), "cw": (o.get("colour"), 0)}[kind]
        for wd in (85, 80, 75):
            f = f"os:800:{wd}"
            if typeset.font(f, size).getlength(s) + 2 * outline <= rw - 6:
                break
        else:
            raise ValueError((kind, n, s))
        layers = [(outline, WHITE), (0, col)] if outline else [(0, col)]
        text(layer, s, f, size, layers, o["x"], o["base"], "l", gap=2)
    elif kind in ("body", "cb"):
        hang = o["hang"]
        f, sz, lines = fit_block(s, o["size"], o["maxw"], o["lines"])
        CHOSEN[n, o["top"]] = (sz, f)
        base = o["top"] + (11 if sz >= 13 else 10)
        for i, ln in enumerate(lines):
            gtext(layer, ln, f, sz, o["x"], base + i * o["pitch"], "l", gap=1)
        if hang:
            gtext(layer, hang[0], f, sz, o["x"] - hang[1], base, "l")
    elif kind in ("cap", "cap1", "capn"):
        lines = s.replace("\\n", "\n").split("\n")
        sz = 11 if kind == "cap" else 12
        f = "os:700:75" if kind == "cap" else "os:600:85"
        if kind == "cap":
            pitch = 10
            first = o["base"]
        elif kind == "cap1":
            pitch, first = 0, o["base"]
        else:
            pitch, first = o["pitch"], o["top"] + 10
        for i, ln in enumerate(lines):
            gtext(layer, ln, f, sz, o["cx"], first + i * pitch, "c", halo=kind != "cap")
    else:
        raise KeyError(kind)


def draw(row, im):
    n = int(row["n"])
    if n == 1264:
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        f = "os:800:75"
        text(lay, row["en"], f, 15, [(2, WHITE), (0, (254, 0, 2, 255))], im.width // 2, 17, "c", gap=3)
        return lay
    src = np.array(im)
    dst = src.copy()
    spec = SPEC[n]
    parts = row["en"].split("|")
    assert len(parts) == len(spec), (n, len(parts), len(spec))
    for kind, rect, o in spec:
        unpaint(src, dst, rect, o.get("cand"))
    out = Image.fromarray(dst)
    for (kind, rect, o), s in zip(spec, parts):
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        _draw_el(layer, kind, rect, o, s, n)
        rx, ry, rw, rh = rect
        a = np.array(layer.getchannel("A"))
        inside = np.zeros_like(a, dtype=bool)
        inside[ry:ry + rh, rx:rx + rw] = True
        stray = int(((a > 24) & ~inside).sum())
        assert not stray, f"{n} {kind} {s[:30]!r}: {stray} ink pixels outside rect {rect}"
        out.alpha_composite(layer.crop((rx, ry, rx + rw, ry + rh)), (rx, ry))
    return out
