"""Impossible tic-tac-toe for the GitHub profile README.

How it works
  1. Each empty square in the README links to a pre-filled "new issue" page.
  2. Opening that issue triggers .github/workflows/tictactoe.yml.
  3. The workflow runs:  python3 tools/ttt.py play
     which reads the issue title (TITLE) and author (PLAYER) from the environment,
     plays the human move (X), lets the minimax bot answer (O), and rewrites the
     board between the TTT markers in README.md.

Other commands
  python3 tools/ttt.py assets   build the square/status SVGs (light + dark)
  python3 tools/ttt.py reset    wipe the saved game and stats, redraw the README
"""
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "assets" / "ttt" / "state.json"
README = ROOT / "README.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "Tejas14Feb/Tejas14Feb")
START, END = "<!-- TTT:START -->", "<!-- TTT:END -->"
HUMAN, BOT = "X", "O"
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
FONT = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
THEMES = {
    "light": dict(bg="#ffffff", fg="#0d1117", muted="#57606a", line="#d0d7de", accent="#FF9933", accent_text="#C46A00"),
    "dark": dict(bg="#000000", fg="#f0f0f0", muted="#9a9a9a", line="#2e2e2e", accent="#FF9933", accent_text="#FF9933"),
}
CELL = 120


# ------------------------------------------------------------------ game logic
def winner(b):
    for a, c, d in LINES:
        if b[a] != "." and b[a] == b[c] == b[d]:
            return b[a], (a, c, d)
    return None, ()


def minimax(b, bot_turn, depth):
    w, _ = winner(b)
    if w:
        return 10 - depth if w == BOT else depth - 10
    if "." not in b:
        return 0
    scores = []
    for i in range(9):
        if b[i] == ".":
            b[i] = BOT if bot_turn else HUMAN
            scores.append(minimax(b, not bot_turn, depth + 1))
            b[i] = "."
    return max(scores) if bot_turn else min(scores)


def best_move(b):
    best, moves = None, []
    for i in range(9):
        if b[i] == ".":
            b[i] = BOT
            s = minimax(b, False, 1)
            b[i] = "."
            if best is None or s > best:
                best, moves = s, [i]
            elif s == best:
                moves.append(i)
    return random.choice(moves)  # equally perfect moves, picked at random


def fresh_state():
    return {"board": "." * 9, "game": 1, "over": False, "result": None,
            "stats": {"bot": 0, "draws": 0, "humans": 0}, "recent": []}


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else fresh_state()


def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2) + "\n")


# ------------------------------------------------------------------ svg assets
def svg(w, h, body, t):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="{t["bg"]}"/>\n{body}\n</svg>\n')


def cell_svg(kind, t, n=None):
    """kind: empty | x | o | x-win | o-win"""
    win = kind.endswith("win")
    fill = t["accent"] if win else t["bg"]
    stroke = t["accent"] if win else t["line"]
    body = [f'<rect x="3" y="3" width="{CELL-6}" height="{CELL-6}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>']
    mark_color = "#000000" if win else (t["accent"] if kind.startswith("x") else t["fg"])
    if kind.startswith("x"):
        p = 34
        body.append(f'<path d="M{p} {p} L{CELL-p} {CELL-p} M{CELL-p} {p} L{p} {CELL-p}" '
                    f'stroke="{mark_color}" stroke-width="9" stroke-linecap="square"/>')
    elif kind.startswith("o"):
        body.append(f'<circle cx="{CELL/2}" cy="{CELL/2}" r="27" fill="none" stroke="{mark_color}" stroke-width="9"/>')
    elif n is not None:
        body.append(f'<text x="14" y="28" font-size="14" fill="{t["muted"]}">{n}</text>')
    return svg(CELL, CELL, "\n".join(body), t)


def status_svg(s, t):
    st = s["stats"]
    if s["over"]:
        line = {"bot": "BOT WINS", "draw": "DRAW", "human": "YOU WON?!"}[s["result"]]
        sub = "start a new game below"
    else:
        line = "YOUR MOVE"
        sub = "you are X · click any empty square"
    W, H = 1000, 130
    b = [
        f'<text x="40" y="44" font-size="13" letter-spacing="3" fill="{t["muted"]}">GAME #{s["game"]} · IMPOSSIBLE MODE</text>',
        f'<text x="40" y="86" font-size="34" font-weight="700" fill="{t["accent_text"] if s["over"] else t["fg"]}">{line}</text>',
        f'<text x="40" y="112" font-size="13" fill="{t["muted"]}">{escape(sub)}</text>',
    ]
    for i, (label, val) in enumerate([("BOT", st["bot"]), ("DRAWS", st["draws"]), ("HUMANS", st["humans"])]):
        x = 700 + i * 105
        color = t["accent_text"] if label == "BOT" else t["fg"]
        b.append(f'<text x="{x}" y="58" font-size="12" letter-spacing="2" fill="{t["muted"]}">{label}</text>')
        b.append(f'<text x="{x}" y="96" font-size="34" font-weight="700" fill="{color}">{val}</text>')
    b.append(f'<line x1="40" y1="{H-2}" x2="{W-40}" y2="{H-2}" stroke="{t["line"]}" stroke-width="1"/>')
    return svg(W, H, "\n".join(b), t)


def build_assets(s=None):
    for mode, t in THEMES.items():
        out = ROOT / "assets" / "ttt" / ("dark" if mode == "dark" else "")
        out.mkdir(parents=True, exist_ok=True)
        for kind in ["x", "o", "x-win", "o-win"]:
            (out / f"{kind}.svg").write_text(cell_svg(kind, t))
        for n in range(1, 10):
            (out / f"empty-{n}.svg").write_text(cell_svg("empty", t, n))
        (out / "status.svg").write_text(status_svg(s or load(), t))


# ------------------------------------------------------------------ readme
def issue_link(title, body):
    return f"https://github.com/{REPO}/issues/new?title={quote(title)}&body={quote(body)}"


def pic(name, alt, width, version=None):
    q = f"?v={version}" if version is not None else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/ttt/dark/{name}.svg{q}"/>'
            f'<img src="assets/ttt/{name}.svg{q}" width="{width}" alt="{escape(alt)}"/></picture>')


def render_readme(s):
    b = s["board"]
    _, line = winner(list(b))
    version = f'{s["game"]}-{b.count("X")}-{b.count("O")}-{int(s["over"])}'
    rows = []
    for r in range(3):
        cells = []
        for c in range(3):
            i = r * 3 + c
            n = i + 1
            v = b[i]
            if v == ".":
                img = pic(f"empty-{n}", f"Empty square {n}" + ("" if s["over"] else f", play here"), 100)
                if s["over"]:
                    cells.append(img)
                else:
                    cells.append(f'<a href="{issue_link(f"ttt|move|{n}", f"Press **Submit new issue** to play square {n}. No need to change anything.")}">{img}</a>')
            else:
                kind = v.lower() + ("-win" if i in line else "")
                cells.append(pic(kind, f"Square {n}: {v}", 100))
        rows.append("".join(cells))
    board_html = "<br>\n".join(rows)

    status = s["result"]
    status_alt = (f'Game {s["game"]}: ' + ("your move, you are X" if not s["over"] else
                  {"bot": "the bot won", "draw": "draw", "human": "you won"}[status]) +
                  f'. Bot {s["stats"]["bot"]}, draws {s["stats"]["draws"]}, humans {s["stats"]["humans"]}.')
    new_game = issue_link("ttt|new", "Press **Submit new issue** to start a new game.")
    if s["over"]:
        cta = f'<a href="{new_game}"><b>Start a new game →</b></a>'
    else:
        cta = (f'<sub>Click a square, then press <b>Submit new issue</b> on the page that opens. '
               f'A GitHub Action plays your move, the bot answers, and the board updates in about a minute. '
               f'<a href="{new_game}">Restart</a></sub>')

    recent = s["recent"][-6:][::-1]
    recent_md = "\n".join(f'| @{r["player"]} | {r["move"]} | {r["date"]} |' for r in recent) or "| nobody yet | | |"

    return f"""{START}
<p align="center">{pic("status", status_alt, "100%", version)}</p>
<p align="center">
{board_html}
</p>
<p align="center">{cta}</p>
<details>
<summary><b>Recent moves</b></summary>
<br>

| Player | Move | When (UTC) |
|---|---|---|
{recent_md}

</details>
{END}"""


def write_readme(s):
    text = README.read_text()
    block = render_readme(s)
    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    README.write_text(text)


# ------------------------------------------------------------------ play
def finish(s, result):
    s["over"], s["result"] = True, result
    key = {"bot": "bot", "draw": "draws", "human": "humans"}[result]
    s["stats"][key] += 1


def play(title, player):
    s = load()
    m = re.fullmatch(r"ttt\|(?:move\|([1-9])|new)", title.strip())
    if not m:
        return s, "That issue title isn't a valid move, so nothing changed."
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    if m.group(1) is None:  # new game
        if not s["over"] and s["board"] == "." * 9:
            return s, "A fresh game is already waiting. Go make the first move!"
        s.update(board="." * 9, game=s["game"] + 1, over=False, result=None)
        s["recent"].append({"player": player, "move": "new game", "date": now})
        return s, f"Started game #{s['game']}. Your move!"

    if s["over"]:
        return s, "That game is already over. Start a new one from the README."
    sq = int(m.group(1))
    b = list(s["board"])
    if b[sq - 1] != ".":
        return s, f"Square {sq} was already taken, probably by someone who moved just before you. Check the board and try again."

    b[sq - 1] = HUMAN
    msg = [f"You played square {sq}."]
    w, _ = winner(b)
    if w:
        finish(s, "human")
        msg.append("You actually won. That should be impossible, so please tell Tejas how!")
    elif "." not in b:
        finish(s, "draw")
        msg.append("Draw. That's the best anyone can do against this bot.")
    else:
        bot = best_move(b)
        b[bot] = BOT
        msg.append(f"The bot answered with square {bot + 1}.")
        w, _ = winner(b)
        if w:
            finish(s, "bot")
            msg.append("Bot wins this one. Start a new game from the README and try again.")
        elif "." not in b:
            finish(s, "draw")
            msg.append("Draw. That's the best anyone can do against this bot.")
        else:
            msg.append("Your move again on the README.")
    s["board"] = "".join(b)
    s["recent"].append({"player": player, "move": f"square {sq}", "date": now})
    s["recent"] = s["recent"][-20:]
    return s, " ".join(msg)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "assets":
        build_assets()
    elif cmd == "reset":
        s = fresh_state()
        save(s); build_assets(s); write_readme(s)
    elif cmd == "play":
        title = os.environ.get("TITLE", "")
        player = re.sub(r"[^A-Za-z0-9-]", "", os.environ.get("PLAYER", "someone"))[:39] or "someone"
        s, message = play(title, player)
        save(s); build_assets(s); write_readme(s)
        url = f"https://github.com/{REPO}#readme"
        Path(os.environ.get("TTT_MESSAGE_FILE", "ttt_message.md")).write_text(
            f"{message}\n\n[Back to the board]({url})\n")
        print(message)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
