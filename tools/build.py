"""Builds every SVG in assets/ (light) and assets/dark/ (dark).
Edit the content below and run:  python3 tools/build.py
"""
from pathlib import Path
from html import escape as esc

ROOT = Path(__file__).resolve().parent.parent
W = 1000
FONT = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
TODAY = (2026, 11)

THEMES = {
    "light": dict(bg="#ffffff", fg="#0d1117", muted="#57606a", line="#d0d7de", box="#ffffff",
                  accent="#FF9933", accent_text="#C46A00", accent_soft="#FFF1E0"),
    "dark":  dict(bg="#0d1117", fg="#e6edf3", muted="#8b949e", line="#30363d", box="#0d1117",
                  accent="#FF9933", accent_text="#FF9933", accent_soft="#2a1d0e"),
}

def svg(w, h, body, t, extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">
<style>
text {{ fill: {t["fg"]}; }}
.m {{ fill: {t["muted"]}; }}
.a {{ fill: {t["accent_text"]}; }}
.flow {{ stroke-dasharray: 5 7; animation: flow 1.6s linear infinite; }}
@keyframes flow {{ to {{ stroke-dashoffset: -24; }} }}
.blink {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .flow, .blink {{ animation: none; }} }}
{extra_css}
</style>
<rect width="{w}" height="{h}" fill="{t["bg"]}"/>
{body}
</svg>'''

def T(x, y, s, size=14, cls="", anchor="start", weight=400, ls=0):
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{ls}"{c}>{esc(s)}</text>'

def wrap(s, width_chars):
    out, line = [], ""
    for word in s.split():
        if len(line) + len(word) + 1 > width_chars:
            out.append(line); line = word
        else:
            line = f"{line} {word}".strip()
    return out + [line]

# ---------------------------------------------------------------- header
def header(t):
    b = []
    b.append(T(40, 46, "~/tejas14feb", 13, "m", ls=1))
    b.append(T(W - 40, 46, "vermillion, sd  ·  usd '27", 13, "m", "end", ls=1))
    b.append(f'<line x1="40" y1="64" x2="{W-40}" y2="64" stroke="{t["line"]}"/>')
    b.append(T(40, 140, "TEJAS BUDHARAMU", 56, weight=700, ls=6))
    b.append(f'<rect x="40" y="162" width="84" height="5" fill="{t["accent"]}"/>')
    b.append(T(40, 206, "Analytics Engineering  ·  Data Engineering  ·  Applied AI", 19, weight=600, ls=0.5))
    b.append(T(40, 238, "Computer Science, Business Analytics Minor  |  University of South Dakota  |  May 2027", 14, "m"))
    b.append(f'<line x1="40" y1="272" x2="{W-40}" y2="272" stroke="{t["line"]}"/>')
    return svg(W, 292, "\n".join(b), t)

# ---------------------------------------------------------------- section dividers
def section(n, title, t):
    slug = f"~/{n:02d}-{title.replace(' ', '-')}"
    b = [T(40, 74, f"{n:02d}", 64, weight=700),
         T(150, 62, title.upper(), 20, ls=9),
         f'<line x1="{150 + len(title)*21 + 24}" y1="56" x2="{W - 60 - len(slug)*9}" y2="56" stroke="{t["line"]}"/>',
         f'<rect x="{150 + len(title)*21 + 24}" y="54" width="28" height="4" fill="{t["accent"]}"/>',
         T(W - 40, 62, slug, 14, "m", "end", ls=1.5)]
    return svg(W, 100, "\n".join(b), t)

# ---------------------------------------------------------------- whoami
WHOAMI = [
    ("name", "tejas budharamu"),
    ("school", "university of south dakota, cs + business analytics minor"),
    ("grad", "may 2027"),
    ("now", "digital accessibility developer assistant @ usd"),
    ("before", "it governance analyst @ the bancorp bank"),
    ("focus", "analytics engineering, data engineering, applied ai"),
    ("building", "public-infrastructure-analytics (dbt + snowflake)"),
    ("status", "open to full-time roles starting 2027"),
]
ABOUT = ("I turn messy data into metrics people trust. I like the part of data work where a messy "
         "spreadsheet becomes a model, a metric, and a decision. I picked a Business Analytics minor "
         "next to CS because I want to be an engineer who solves real problems, not just writes code.")

def whoami(t):
    b = [f'<rect x="40.5" y="20.5" width="{W-81}" height="440" fill="{t["box"]}" stroke="{t["line"]}"/>',
         f'<line x1="40" y1="56" x2="{W-40}" y2="56" stroke="{t["line"]}"/>',
         T(64, 44, "tejas@usd: ~", 13, "m"),
         T(W - 64, 44, "zsh", 13, "m", "end"),
         T(64, 96, "$", 16, "a", weight=700), T(84, 96, "whoami", 16, weight=600)]
    y = 136
    for k, v in WHOAMI:
        b.append(T(84, y, k, 15, "a" if k == "status" else "m"))
        b.append(T(220, y, v, 15))
        y += 30
    y += 8
    for line in wrap(ABOUT, 96):
        b.append(T(84, y, line, 14, "m")); y += 22
    y += 14
    b.append(T(64, y, "$", 16, "a", weight=700))
    b.append(f'<rect class="blink" x="84" y="{y - 15}" width="10" height="19" fill="{t["accent"]}"/>')
    b[0] = f'<rect x="40.5" y="20.5" width="{W-81}" height="{y + 22 - 20}" fill="{t["box"]}" stroke="{t["line"]}"/>'
    return svg(W, y + 64, "\n".join(b), t)

# ---------------------------------------------------------------- system map (stack)
NODES = [  # (x, y, title, subtitle)
    (150, 290, "python", "pandas · numpy · seaborn"),
    (150, 400, "sql · r · matlab", "querying · statistics"),
    (370, 165, "dbt core", "layered models · etl/elt"),
    (630, 165, "snowflake · duckdb", "warehouse · local analytics"),
    (850, 290, "aws", "lambda · textract · bedrock"),
    (850, 400, "rest apis · ci/cd", "backend · deployment · git"),
    (850, 590, "scikit-learn · xgboost", "classification · forecasting"),
    (850, 700, "pytorch · bayesian", "lstm autoencoders · a/b tests"),
    (500, 705, "tableau · power bi", "plotly dash · excel · airtable"),
    (150, 590, "llm tooling · mcp", "audit bots · agentic workflows"),
    (150, 700, "kpi / kri design", "metrics people trust"),
]
GROUPS = [(150, 238, "LANGUAGES"), (500, 108, "DATA ENGINEERING"), (850, 238, "CLOUD & DEV"),
          (850, 538, "ML & STATISTICS"), (150, 538, "AI"), (500, 770, "BI & VISUALIZATION")]

def stack(t):
    cx, cy = 500, 440
    b = [T(40, 40, "SYSTEM MAP  /  RAW DATA TO DECISIONS", 13, ls=4),
         T(W - 40, 40, "FIG. 01", 13, "m", "end", ls=3),
         f'<line x1="40" y1="58" x2="{W-40}" y2="58" stroke="{t["fg"]}"/>']
    for x, y, *_ in NODES:
        b.append(f'<line class="flow" x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{t["accent"]}" stroke-width="1.4"/>')
    for x, y, title, sub in NODES:
        w = 228
        b.append(f'<rect x="{x - w/2}" y="{y - 30}" width="{w}" height="60" fill="{t["box"]}" stroke="{t["fg"]}" stroke-width="1.2"/>')
        b.append(T(x, y - 4, title, 15, anchor="middle", weight=600, ls=0.5))
        b.append(T(x, y + 17, sub, 11.5, "m", "middle", ls=0.5))
    for x, y, g in GROUPS:
        b.append(T(x, y, g, 12, anchor="middle", weight=600, ls=4))
    b.append(f'<rect x="{cx-125}" y="{cy-38}" width="250" height="76" fill="{t["box"]}" stroke="{t["accent"]}" stroke-width="2.4"/>')
    b.append(T(cx, cy - 6, "TEJAS.SYS", 20, "a", "middle", 700, 3))
    b.append(T(cx, cy + 20, "data in, decisions out", 12, "m", "middle", ls=0.5))
    b.append(f'<line x1="40" y1="800" x2="{W-40}" y2="800" stroke="{t["fg"]}"/>')
    b.append(T(W - 40, 826, "DASHED LINES  /  DATA IN MOTION", 12, "m", "end", ls=4))
    return svg(W, 846, "\n".join(b), t)

# ---------------------------------------------------------------- project cards
PROJECTS = {
    "p-infra": ("public-infrastructure-analytics", True,
                "Modeling Midwest public infrastructure spending data into clean, tested analytics layers.",
                ["dbt Core", "Snowflake", "SQL", "Git"]),
    "p-sdmts": ("sdmts supply chain mapping tool", False,
                "Moved a 2,671-record manufacturer database from Excel to Airtable and built the cleaning and validation pipelines behind a live supply chain map.",
                ["Airtable", "ETL", "Validation"]),
    "p-spotify": ("spotify-ml-project", False,
                  "Predicts whether a song lands in the top 25% by popularity from its audio features, across about 114K tracks.",
                  ["Python", "DuckDB", "XGBoost", "Dash"]),
    "p-ecg": ("iot-ecg-anomaly", False,
              "Detects cardiac anomalies in wearable ECG signals, comparing an LSTM autoencoder with an Isolation Forest baseline.",
              ["Python", "LSTM", "scikit-learn"]),
    "p-bayes": ("bayesian-cq-analysis", False,
                "Bayesian regression of phosphorus concentration against stream discharge, with exact posteriors and predictive checks.",
                ["Python", "SciPy", "Bayesian"]),
}

def card(key, t):
    name, featured, desc, tags = PROJECTS[key]
    w = 1000 if featured else 490
    h = 190 if featured else 230
    chars = 100 if featured else 46
    b = [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" fill="{t["box"]}" stroke="{t["accent"] if featured else t["line"]}" stroke-width="{2 if featured else 1.2}"/>',
         T(28, 46, name, 20 if featured else 17, weight=700)]
    if featured:
        b.append(f'<rect x="{w-170}" y="26" width="142" height="28" fill="{t["accent"]}"/>')
        b.append(T(w - 99, 45, "IN PROGRESS", 12, anchor="middle", weight=700, ls=2).replace("<text", f'<text style="fill:#000"'))
    y = 84
    for line in wrap(desc, chars):
        b.append(T(28, y, line, 14, "m")); y += 22
    x = 28
    for tag in tags:
        tw = len(tag) * 8.4 + 22
        b.append(f'<rect x="{x}" y="{h-50}" width="{tw}" height="26" fill="none" stroke="{t["fg"]}"/>')
        b.append(T(x + tw/2, h - 32, tag, 12, anchor="middle"))
        x += tw + 10
    return svg(w, h, "\n".join(b), t)

# ---------------------------------------------------------------- timelines
def mi(ym): return ym[0] * 12 + ym[1]
MON = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()

def timeline(rows, start, end, t, ticks_every=3):
    LX, RX = 400, W - 50
    top, rh = 70, 64
    h = top + len(rows) * rh + 70
    span = mi(end) - mi(start)
    X = lambda ym: LX + (mi(ym) - mi(start)) / span * (RX - LX)
    b = []
    m = mi(start)
    while m <= mi(end):
        y_, mo = divmod(m - 1, 12); ym = (y_, mo + 1)
        if mo % ticks_every == 0:
            strong = mo == 0
            b.append(f'<line x1="{X(ym)}" y1="{top-20}" x2="{X(ym)}" y2="{h-56}" stroke="{t["line"]}" stroke-dasharray="{"0" if strong else "2 4"}"/>')
            b.append(T(X(ym), h - 30, f"{MON[mo]} '{str(y_)[2:]}", 11, "m", "middle", 600 if strong else 400, 1))
        m += 1
    tx = X(TODAY)
    b.append(f'<line x1="{tx}" y1="{top-30}" x2="{tx}" y2="{h-56}" stroke="{t["accent"]}" stroke-width="1.5"/>')
    b.append(T(tx, top - 36, "NOW", 11, "a", "middle", 700, 2))
    for i, (title, org, s, e, segs) in enumerate(rows):
        y = top + i * rh
        live = e is None
        e2 = TODAY if live else e
        b.append(T(40, y + 20, title, 15, weight=700))
        b.append(T(40, y + 40, org, 12.5, "m"))
        x1, x2 = X(s), X(e2)
        if live:
            b.append(f'<rect x="{x1}" y="{y+10}" width="{x2-x1}" height="22" fill="{t["accent"]}"/>')
            b.append(f'<circle class="blink" cx="{x2}" cy="{y+21}" r="5" fill="{t["accent"]}"/>')
        else:
            b.append(f'<rect x="{x1}" y="{y+10}" width="{x2-x1}" height="22" fill="{t["fg"]}"/>')
        for lbl, ss, se in segs:
            sx1, sx2 = X(ss), X(se)
            b.append(f'<rect x="{sx1}" y="{y+10}" width="{sx2-sx1}" height="22" fill="{t["fg"]}"/>')
            b.append(T((sx1 + sx2) / 2, y + 48, lbl, 10.5, "m", "middle"))
        dates = f"{MON[s[1]-1].title()} {s[0]} - " + ("Present" if live else f"{MON[e[1]-1].title()} {e[0]}")
        if not segs:
            b.append(T(x1, y + 48, dates, 10.5, "m"))
        b.append(f'<line x1="40" y1="{y+rh-4}" x2="{RX}" y2="{y+rh-4}" stroke="{t["line"]}" stroke-width="0.6"/>')
    b.append(f'<line x1="40" y1="{h-56}" x2="{RX}" y2="{h-56}" stroke="{t["fg"]}"/>')
    b.append(f'<rect x="40" y="{h-20}" width="14" height="8" fill="{t["accent"]}"/>' + T(60, h - 12, "ongoing", 11, "m"))
    b.append(f'<rect x="140" y="{h-20}" width="14" height="8" fill="{t["fg"]}"/>' + T(160, h - 12, "completed", 11, "m"))
    return svg(W, h, "\n".join(b), t)

EXPERIENCE = [
    ("Digital Accessibility Developer Asst.", "Center for Digital Accessibility, USD", (2026, 8), None, []),
    ("IT Governance Analyst", "The Bancorp Bank, Sioux Falls SD", (2026, 5), (2026, 8), []),
    ("Data Analyst & Developer", "Coyote Business Consulting, SDMTS", (2025, 8), (2026, 4), []),
    ("Entrepreneur Lead, AI/ML Research", "National Science Foundation I-Corps", (2025, 5), (2025, 7), []),
]
LEADERSHIP = [
    ("President", "Indian Student Association", (2023, 8), None, []),
    ("Peer Mentor", "University of South Dakota", (2023, 8), (2025, 12), []),
    ("Finance Chair & Senator", "Student Government Association", (2024, 2), (2025, 9), []),
    ("President", "Residence Hall Association", (2024, 5), (2026, 5), []),
    ("VP for Finance", "Dakota Days", (2024, 5), (2024, 10), []),
    ("Brother", "Delta Sigma Pi, Alpha Eta", (2024, 8), None,
     [("internal control", (2025, 1), (2025, 5)), ("vp alumni rel.", (2026, 1), (2026, 5))]),
    ("Finance Director", "International Club", (2024, 8), (2025, 5), []),
    ("Coord. Presidents & Education", "MACURH", (2025, 5), (2026, 5), []),
]

# ---------------------------------------------------------------- awards
AWARDS = [
    ("OUTSTANDING STUDENT", "BUSINESS CONSULTANT", "Coyote Business Consulting", "NOV '25  +  APR '26", "x2"),
    ("STUDENT AMBASSADOR", "SCHOLARSHIP", "University of South Dakota", "AUG '25  +  JAN '26", "x2"),
    ("OMA MULTICULTURAL", "EXCELLENCE AWARD", "USD Coyote Excellence Awards", "APR '25", ""),
]

def trophy(cx, cy, c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2.2" stroke-linejoin="round">'
            f'<path d="M{cx-22} {cy-30} h44 v14 a22 22 0 0 1 -44 0 z" fill="{c}"/>'
            f'<path d="M{cx-22} {cy-24} h-10 a10 10 0 0 0 10 16"/>'
            f'<path d="M{cx+22} {cy-24} h10 a10 10 0 0 1 -10 16"/>'
            f'<path d="M{cx} {cy+6} v12"/><path d="M{cx-14} {cy+18} h28 v8 h-28 z" fill="{c}"/></g>')

def laurel(cx, cy, c, flip):
    import math
    out = []
    for i in range(6):
        ang = math.radians(115 + i * 22)
        if flip: ang = math.pi - ang
        x, y = cx + 50 * math.cos(ang), cy + 50 * math.sin(ang)
        rot = math.degrees(ang) + (90 if not flip else -90) + (-25 if not flip else 25)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.6" ry="9" transform="rotate({rot:.1f} {x:.1f} {y:.1f})" fill="{c}"/>')
    return "".join(out)

def awards(t):
    cw, gap, top = 290, 25, 70
    b = [T(W/2, 36, "★  HALL OF FAME  ★", 16, "a", "middle", 700, 6)]
    for i, (l1, l2, org, when, mult) in enumerate(AWARDS):
        x = 40 + i * (cw + gap); cx = x + cw / 2
        b.append(f'<rect x="{x}" y="{top}" width="{cw}" height="330" fill="{t["box"]}" stroke="{t["accent"]}" stroke-width="1.6"/>')
        b.append(f'<rect x="{x+6}" y="{top+6}" width="{cw-12}" height="318" fill="none" stroke="{t["line"]}"/>')
        b.append(T(cx, top + 34, "WINNER", 12, "a", "middle", 700, 4))
        b.append(trophy(cx, top + 100, t["accent"]))
        b.append(laurel(cx, top + 92, t["muted"], False) + laurel(cx, top + 92, t["muted"], True))
        if mult:
            b.append(f'<rect x="{x+cw-58}" y="{top+18}" width="40" height="22" fill="{t["fg"]}"/>')
            b.append(T(x + cw - 38, top + 34, mult, 12, anchor="middle", weight=700).replace("<text", f'<text style="fill:{t["bg"]}"'))
        b.append(f'<line x1="{x+40}" y1="{top+158}" x2="{x+cw-40}" y2="{top+158}" stroke="{t["line"]}"/>')
        b.append(T(cx, top + 192, l1, 15, anchor="middle", weight=700, ls=1))
        b.append(T(cx, top + 214, l2, 15, anchor="middle", weight=700, ls=1))
        b.append(T(cx, top + 252, org, 12, "m", "middle"))
        b.append(T(cx, top + 296, when, 12, "a", "middle", 600, 2))
    return svg(W, 420, "\n".join(b), t)

# ---------------------------------------------------------------- footer
def footer(t):
    b = [f'<line x1="40" y1="20" x2="{W-40}" y2="20" stroke="{t["line"]}"/>',
         f'<circle class="blink" cx="48" cy="56" r="6" fill="{t["accent"]}"/>',
         T(66, 61, "status: open to full-time roles in analytics and data engineering, starting 2027", 14),
         T(W - 40, 61, "~/eof", 13, "m", "end", ls=1)]
    return svg(W, 90, "\n".join(b), t)

# ---------------------------------------------------------------- build
SECTIONS = [(1, "whoami"), (2, "stack"), (3, "projects"), (4, "experience"), (5, "leadership"), (6, "awards")]

def build():
    for mode, t in THEMES.items():
        out = ROOT / "assets" / ("dark" if mode == "dark" else "")
        out.mkdir(parents=True, exist_ok=True)
        files = {"header": header(t), "whoami": whoami(t), "stack": stack(t),
                 "experience": timeline(EXPERIENCE, (2025, 4), (2027, 1), t),
                 "leadership": timeline(LEADERSHIP, (2023, 7), (2027, 1), t, 6),
                 "awards": awards(t), "footer": footer(t)}
        for n, title in SECTIONS:
            files[f"s{n:02d}"] = section(n, title, t)
        for k in PROJECTS:
            files[k] = card(k, t)
        for name, content in files.items():
            (out / f"{name}.svg").write_text(content)
    print("built", len(files) * 2, "svgs")

if __name__ == "__main__":
    build()
