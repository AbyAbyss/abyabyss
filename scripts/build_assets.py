#!/usr/bin/env python3
"""Generates every animated SVG used by the profile README.

    python3 scripts/build_assets.py

The README is a dive: the hero is the surface and each section sits in a
deeper ocean zone (200 m, 1,000 m, 4,000 m, 6,000 m, seabed).

GitHub strips <style> and <script> from README markdown, but an SVG loaded
through <img> keeps its own CSS. Every file here is CSS-only (no JS, no
external fonts or images) and:
  * switches palette with prefers-color-scheme (night dive / day dive)
  * enlarges its text when rendered narrow (media queries inside an SVG
    image are evaluated against the image's own size, so this is the
    phone layout)
  * stops moving under prefers-reduced-motion
"""
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# ---------------------------------------------------------------- content
NAME = "Aby Saji Pappachan"
ROLE = "TECHNICAL LEAD  ·  BACKEND & AI ENGINEER"
TYPED_LINES = [
    "Building scalable backend systems",
    "Designing AI agents & LLM platforms",
    "MCP | Generative AI | Distributed Systems",
    "8 years across Node.js | Python | Golang",
]
STACK = [
    ("nodejs", "Node.js", "#5FA04E"), ("typescript", "TypeScript", "#3178C6"), ("nestjs", "NestJS", "#E0234E"),
    ("python", "Python", "#4B8BBE"), ("go", "Golang", "#00ADD8"), ("graphql", "GraphQL", "#E10098"),
    ("llms", "LLMs", "#2ED3A7"), ("langchain", "LangChain", "#3FB6A8"), ("mcp", "MCP", "#9D6BFF"),
    ("duckdb", "DuckDB", "#E6C700"), ("airbyte", "Airbyte", "#615EFF"), ("airflow", "Apache Airflow", "#017CEE"),
    ("aws", "AWS", "#FF9900"), ("docker", "Docker", "#2496ED"), ("postgresql", "PostgreSQL", "#4169E1"),
    ("mongodb", "MongoDB", "#47A248"), ("redis", "Redis", "#DC382D"), ("rust", "Rust", "#DEA584"),
    ("pull-shark", "Pull Shark ×4", "#1F6FEB"), ("pair-extraordinaire", "Pair Extraordinaire ×4", "#2ED3A7"),
    ("quickdraw", "Quickdraw", "#F0A500"), ("yolo", "YOLO", "#9D6BFF"),
    ("arctic-code-vault", "Arctic Code Vault", "#7FB7C9"),
]
BUTTONS = [
    ("portfolio", "Portfolio", "abyabyss.github.io"),
    ("linkedin", "LinkedIn", "in/aby-saji"),
    ("email", "Email", "abyrocksaji@gmail.com"),
]

# ---------------------------------------------------------------- palette
# Water colour at each depth boundary: night dive (dark) and day dive (light).
ZD = ["#0c3a47", "#06242f", "#051c26", "#04151d", "#030f16", "#02090e", "#010508"]
ZL = ["#1a9cad", "#0e6d83", "#0b5a72", "#094960", "#07394f", "#052b40", "#031d30"]


def theme(top, bot):
    return (
        f"svg{{--top:{ZD[top]};--bot:{ZD[bot]};--ink:#eafff9;--dim:#86b3ad;--accent:#2ED3A7;--accent2:#4cc9f0;"
        "--accent3:#9d6bff;--line:rgba(46,211,167,.28);--glass:rgba(2,14,20,.58);--unlit:#5c9c93;--hull:#0f2f38;"
        "--sky0:#050a16;--sky1:#0d1b30;--skyink:#8fb0c9;--orb:#f3efd2;--stars:1;--ray:#bafff0;--rayo:.1}"
        f"@media (prefers-color-scheme:light){{svg{{--top:{ZL[top]};--bot:{ZL[bot]};--ink:#ffffff;--dim:#d2f1f1;"
        "--accent:#8af7da;--accent2:#b3efff;--accent3:#dccbff;--line:rgba(255,255,255,.34);--glass:rgba(3,40,54,.5);"
        "--unlit:#a5dcda;--hull:#0a4a5c;--sky0:#8fd6ff;--sky1:#e2f6ff;--skyink:#14587a;--orb:#fff6bf;--stars:0;"
        "--ray:#ffffff;--rayo:.26}}"
        f".sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}"
        ".fb{transform-box:fill-box;transform-origin:center}"
    )


REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}.rm{display:none}%s}"


def svg(w, h, title, css, defs, body, decorative=False):
    a11y = 'role="presentation"' if decorative else f'role="img" aria-label="{escape(title)}"'
    head = "" if decorative else f"<title>{escape(title)}</title>"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {a11y}>'
        f"{head}<style>{css}</style><defs>{defs}</defs>{body}</svg>\n"
    )


def sine(y, amp, period, start, end, close_to=None):
    half = period / 2
    d = f"M{start} {y} Q{start + half / 2} {y - amp} {start + half} {y}"
    x = start + half
    while x < end:
        x += half
        d += f" T{x:g} {y}"
    if close_to is not None:
        d += f" V{close_to} H{start} Z"
    return d


def water_defs(w, h, rx=20):
    return (
        '<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--top)"/>'
        '<stop offset="1" style="stop-color:var(--bot)"/></linearGradient>'
        f'<clipPath id="card"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'
    )


def frame(w, h, rx=20):
    return (
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{rx - .75}" fill="none" '
        'stroke="var(--line)" stroke-width="1.5"/>'
    )


def snow(rnd, w, h, n, top=0):
    """Marine snow: specks that sink slowly and drift."""
    out = ""
    for _ in range(n):
        x, r = rnd.uniform(8, w - 8), rnd.uniform(.7, 2.2)
        dur, delay, dx = rnd.uniform(14, 34), rnd.uniform(0, 34), rnd.uniform(-30, 30)
        color = rnd.choice(["var(--accent)", "var(--accent2)", "var(--ray)", "var(--ray)"])
        out += (
            f'<circle class="sn" cx="{x:.0f}" cy="{top - 6}" r="{r:.1f}" fill="{color}" '
            f'style="--dx:{dx:.0f}px;--dy:{h - top + 12}px;animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>'
        )
    return out


SNOW_CSS = (
    ".sn{animation:sn linear infinite}"
    "@keyframes sn{0%{transform:translate(0,0);opacity:0}10%{opacity:.8}85%{opacity:.55}"
    "100%{transform:translate(var(--dx),var(--dy));opacity:0}}"
)


def sparks(rnd, box, n):
    """Bioluminescence: points that glow on and off in place."""
    x0, y0, x1, y1 = box
    out = ""
    for _ in range(n):
        color = rnd.choice(["var(--accent)", "var(--accent2)", "var(--accent3)"])
        out += (
            f'<circle class="sp" cx="{rnd.uniform(x0, x1):.0f}" cy="{rnd.uniform(y0, y1):.0f}" r="{rnd.uniform(1, 2.4):.1f}" '
            f'fill="{color}" style="animation-duration:{rnd.uniform(2.4, 6):.1f}s;animation-delay:-{rnd.uniform(0, 6):.1f}s"/>'
        )
    return out


SPARK_CSS = ".sp{animation:sp ease-in-out infinite}@keyframes sp{0%,100%{opacity:.08}50%{opacity:1}}"


# ---------------------------------------------------------------- hero
def hero():
    W, H, SKY = 880, 460, 58
    rnd = random.Random(11)
    css = [theme(0, 1), SNOW_CSS, SPARK_CSS]
    css.append("""
.star{opacity:var(--stars);animation:sp 4s ease-in-out infinite}
.ray{fill:url(#ray);animation:sway 12s ease-in-out infinite alternate}
@keyframes sway{from{transform:rotate(-4deg);opacity:.4}to{transform:rotate(4deg);opacity:1}}
.wv{animation:wv linear infinite}
@keyframes wv{to{transform:translateX(-220px)}}
.cur{fill:none;stroke:var(--line);animation:flow linear infinite}
@keyframes flow{to{transform:translateX(-440px)}}
.in{animation:in 1s cubic-bezier(.2,.7,.2,1) both}
@keyframes in{from{opacity:0;transform:translateY(16px)}}
.ping{animation:ping 2s ease-out infinite}
@keyframes ping{from{transform:scale(1);opacity:.8}to{transform:scale(3.6);opacity:0}}
.bob{animation:bob 7s ease-in-out infinite alternate}
@keyframes bob{from{transform:translate(0,5px)}to{transform:translate(-14px,-7px)}}
.sweep{transform-origin:0 0;animation:sweep 13s cubic-bezier(.45,0,.55,1) infinite}
@keyframes sweep{0%,6%{transform:rotate(17deg)}46%,54%{transform:rotate(80deg)}94%,100%{transform:rotate(17deg)}}
.prop{animation:prop .5s linear infinite}
@keyframes prop{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.15)}}
.bub{fill:none;stroke:var(--ink);stroke-opacity:.55;animation:bub ease-in infinite}
@keyframes bub{0%{transform:translate(0,0) scale(.4);opacity:0}15%{opacity:.9}
100%{transform:translate(var(--dx),-290px) scale(1.5);opacity:0}}
.lamp{animation:lamp 2.6s ease-in-out infinite}
@keyframes lamp{50%{opacity:.55}}
.ch{opacity:0;animation:ch 18s linear infinite}
@keyframes ch{0%,30%{opacity:1}30.01%,100%{opacity:0}}
.ln{animation:ln 18s linear infinite}
@keyframes ln{0%,21%{opacity:1}23%,100%{opacity:0}}
.blink{animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@media (max-width:560px){.mh{display:none}.pill{transform:scale(1.5)}.role{font-size:24px;letter-spacing:2px}
.role{transform:translateY(8px)}.termi{transform:translateY(16px) scale(1.42)}}
""")

    # typing: every glyph sits on a fixed grid, so font metrics don't matter
    size, cw = 18, 10.8
    box_w, box_h, box_y = 580, 46, 262
    box_x = (W - box_w) / 2
    tx, ty = box_x + 46, box_y + 30
    cycle, slot, type_t = 18.0, 4.5, 1.9
    typed = ""
    for k, line in enumerate(TYPED_LINES):
        n = len(line)
        dt, base = type_t / n, k * slot - cycle
        css.append(
            f"@keyframes c{k}{{0%{{transform:translateX(0);animation-timing-function:steps({n},start)}}"
            f"{type_t / cycle * 100:.3f}%,100%{{transform:translateX({n * cw:.1f}px)}}}}"
        )
        spans = "".join(
            f'<tspan class="ch" x="{tx + i * cw:.1f}" style="animation-delay:{base + i * dt:.3f}s">{escape(c)}</tspan>'
            for i, c in enumerate(line) if c != " "
        )
        typed += (
            f'<g class="ln l{k}" style="animation-delay:{base:.2f}s">'
            f'<text class="mono" y="{ty}" font-size="{size}" fill="var(--ink)">{spans}</text>'
            f'<g class="rm" style="animation:c{k} {cycle}s linear {base:.2f}s infinite">'
            f'<rect class="blink" x="{tx}" y="{ty - 16}" width="9" height="21" rx="1.5" fill="var(--accent)"/></g></g>'
        )
    css.append(REDUCED % ".ln{opacity:0}.ln.l0{opacity:1}.ch{opacity:1}")

    stars = "".join(
        f'<circle class="star" cx="{rnd.uniform(150, 720):.0f}" cy="{rnd.uniform(8, 44):.0f}" r="{rnd.uniform(.6, 1.3):.1f}" '
        f'fill="#fff" style="animation-delay:-{rnd.uniform(0, 4):.1f}s"/>' for _ in range(22)
    )
    rays = "".join(
        f'<polygon class="ray" style="transform-origin:{x}px {SKY}px;animation-duration:{d}s;animation-delay:-{dl}s" '
        f'points="{x - w / 2},{SKY} {x + w / 2},{SKY} {x + w * 1.7 + lean},{H} {x - w * 1.7 + lean},{H}"/>'
        for x, w, lean, d, dl in [(120, 44, 80, 12, 0), (330, 66, 30, 15, 5), (520, 36, -10, 10, 2),
                                  (700, 80, -90, 14, 7), (820, 40, -150, 11, 4)]
    )
    waves = (
        f'<path class="wv" style="animation-duration:9s" d="{sine(SKY + 1, 7, 220, 0, W + 220, close_to=SKY + 26)}" '
        'fill="var(--top)" fill-opacity=".55"/>'
        f'<g class="wv" style="animation-duration:6s"><path d="{sine(SKY + 5, 5, 220, -110, W + 220, close_to=SKY + 30)}" fill="var(--top)"/>'
        f'<path d="{sine(SKY + 5, 5, 220, -110, W + 220)}" fill="none" stroke="var(--ray)" stroke-opacity=".5" stroke-width="1.2"/></g>'
    )
    currents = "".join(
        f'<path class="cur" d="{sine(y, amp, 440, 0, W + 440)}" stroke-width="{sw}" stroke-dasharray="{dash}" '
        f'style="animation-duration:{d}s"/>'
        for y, amp, sw, dash, d in [(432, 9, 1.3, "none", 17), (444, 12, 1, "3 9", 26)]
    )

    # submersible, facing left; its lamp is the origin of the searchlight
    SX, SY = 752, 392
    LX, LY = SX - 44, SY + 5
    cone = "0,-3 0,3 -660,84 -660,-84"
    sub = f"""<g transform="translate({SX} {SY})">
<path d="M40 -2 L58 -14 L58 12 Z" fill="var(--hull)" stroke="var(--accent)" stroke-width="1.4" stroke-linejoin="round"/>
<ellipse class="prop fb" cx="61" cy="-1" rx="2.6" ry="13" fill="var(--accent)"/>
<rect x="-6" y="-29" width="22" height="15" rx="4" fill="var(--hull)" stroke="var(--accent)" stroke-width="1.4"/>
<path d="M8 -29 V-39 H2" fill="none" stroke="var(--accent)" stroke-width="1.6" stroke-linecap="round"/>
<rect x="-44" y="-17" width="90" height="34" rx="17" fill="var(--hull)" stroke="var(--accent)" stroke-width="1.6"/>
<circle cx="-22" cy="-1" r="9" fill="var(--accent2)" fill-opacity=".28" stroke="var(--accent2)" stroke-width="1.4"/>
<circle cx="4" cy="-1" r="4" fill="none" stroke="var(--accent)" stroke-opacity=".7"/>
<circle cx="20" cy="-1" r="4" fill="none" stroke="var(--accent)" stroke-opacity=".7"/>
<path d="M-30 22 H30 M-20 17 V22 M20 17 V22" stroke="var(--accent)" stroke-width="1.6" stroke-linecap="round" fill="none"/>
<circle class="lamp" cx="-44" cy="5" r="9" fill="#fff" fill-opacity=".25"/><circle cx="-44" cy="5" r="3.6" fill="#fff"/>
</g>"""
    bubbles = "".join(
        f'<circle class="bub fb" cx="{SX + 8 + i * 5}" cy="{SY - 40}" r="{r}" '
        f'style="--dx:{dx}px;animation-duration:{d}s;animation-delay:-{dl}s"/>'
        for i, (r, dx, d, dl) in enumerate([(3, -18, 6, 0), (2, 10, 7.5, 2.2), (4, -6, 9, 4.1), (2.4, 22, 6.6, 5.3)])
    )
    name_attrs = f'font-size="66" font-weight="800" letter-spacing="-1.4" text-anchor="middle" x="{W / 2}" y="196"'

    defs = water_defs(W, H, 22) + f"""
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--sky0)"/><stop offset="1" style="stop-color:var(--sky1)"/></linearGradient>
<linearGradient id="ray" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--ray);stop-opacity:var(--rayo)"/><stop offset="1" style="stop-color:var(--ray)" stop-opacity="0"/></linearGradient>
<radialGradient id="orb"><stop offset="0" style="stop-color:var(--orb)" stop-opacity=".55"/><stop offset="1" style="stop-color:var(--orb)" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="-660" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset=".5" style="stop-color:var(--accent)" stop-opacity=".16"/><stop offset="1" style="stop-color:var(--accent)" stop-opacity="0"/></linearGradient>
<clipPath id="nameclip"><text class="sans" {name_attrs}>{NAME}</text></clipPath>
"""
    beam = lambda fill: (  # noqa: E731
        f'<g class="bob"><g transform="translate({LX} {LY})"><g class="sweep"><polygon points="{cone}" fill="{fill}"/></g></g></g>'
    )
    body = f"""<g clip-path="url(#card)">
<rect width="{W}" height="{SKY + 8}" fill="url(#sky)"/>
{stars}
<circle cx="776" cy="30" r="44" fill="url(#orb)"/><circle cx="776" cy="30" r="11" style="fill:var(--orb)"/>
<rect y="{SKY + 20}" width="{W}" height="{H - SKY - 20}" fill="url(#water)"/>
{waves}
{rays}
{currents}
{snow(rnd, W, H, 26, top=SKY + 20)}
{sparks(rnd, (20, 110, W - 20, H - 40), 16)}
<g class="rm">{beam("url(#beam)")}</g>
{bubbles}
</g>
{frame(W, H, 22)}
<text class="mono mh" x="28" y="35" font-size="11" font-weight="700" letter-spacing="2.2" style="fill:var(--skyink)">00 M  ·  SURFACE</text>

<g class="in"><g class="pill fb">
<rect x="{W / 2 - 84}" y="88" width="168" height="28" rx="14" fill="var(--glass)" stroke="var(--line)"/>
<circle class="ping fb rm" cx="{W / 2 - 62}" cy="102" r="4" fill="var(--accent)"/><circle cx="{W / 2 - 62}" cy="102" r="4" fill="var(--accent)"/>
<text class="mono" x="{W / 2 + 9}" y="106.5" font-size="12" font-weight="700" letter-spacing="1.6" text-anchor="middle" fill="var(--ink)">OPEN TO WORK</text>
</g></g>

<g class="in" style="animation-delay:.15s">
<text class="sans" {name_attrs} style="fill:var(--unlit)">{NAME}</text>
<g clip-path="url(#nameclip)" class="rm">{beam("#ffffff")}</g>
</g>

<g class="in" style="animation-delay:.3s"><text class="sans role" style="transition:none" x="{W / 2}" y="232" font-size="15" font-weight="600" letter-spacing="3.4" text-anchor="middle" fill="var(--dim)">{escape(ROLE)}</text></g>

<g class="in" style="animation-delay:.45s"><g class="termi fb">
<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="12" fill="var(--glass)" stroke="var(--line)"/>
<text class="mono" x="{box_x + 20}" y="{ty}" font-size="{size}" font-weight="700" fill="var(--accent)">&gt;</text>
{typed}
</g></g>

<g class="bob">{sub}</g>
"""
    title = f"{NAME}. Technical Lead, Backend and AI Engineer. Open to work. " + ". ".join(TYPED_LINES) + "."
    return svg(W, H, title, "".join(css), defs, body)


# ---------------------------------------------------------------- zone banners
def art_twilight():
    """Two schools of fish cross the whole banner, passing behind the title."""
    fish = '<path d="M0 0C6-8 20-8 28 0C20 8 6 8 0 0Z M26 0L37-7L33 0L37 7Z"/>'
    layout = [(0, 0, 1), (48, -18, .8), (56, 16, .9), (104, -6, .7), (112, 26, .75), (150, -26, .6), (168, 6, .65)]

    def school(y, scale, dur, delay, opacity, members):
        body = "".join(
            f'<g transform="translate({x} {fy}) scale({s})"><g class="fishy" style="animation-delay:-{i * .4}s">{fish}</g></g>'
            for i, (x, fy, s) in enumerate(members)
        )
        return (
            f'<g class="school rm" style="--y:{y}px;animation-duration:{dur}s;animation-delay:-{delay}s" '
            f'fill="var(--dim)" fill-opacity="{opacity}"><g transform="scale({scale})">{body}</g></g>'
        )
    css = (".school{animation:school linear infinite}"
           "@keyframes school{from{transform:translate(900px,var(--y))}to{transform:translate(-260px,var(--y))}}"
           ".fishy{animation:fishy 1.6s ease-in-out infinite alternate}@keyframes fishy{to{transform:translateY(3px)}}")
    return css, school(52, 1, 24, 3, .7, layout) + school(88, .7, 33, 19, .45, layout[:5])


def art_midnight():
    """Jellyfish rise across the full width, some of them behind the depth gauge and title."""
    def jelly(x, s, color, dur, delay, dx):
        tent = "".join(f'<path d="M{tx} 3q4 9 0 18q-4 9 0 18" />' for tx in (-10, -3.5, 3.5, 10))
        return (
            f'<g class="drift rm" style="--x:{x}px;--dx:{dx}px;animation-duration:{dur}s;animation-delay:-{delay}s"><g transform="scale({s})">'
            f'<g class="tent fb" fill="none" stroke="{color}" stroke-opacity=".7" stroke-width="1.3" stroke-linecap="round">{tent}</g>'
            f'<path class="bell fb" d="M-16 2C-16-22 16-22 16 2Q12 7 8 2Q4 7 0 2Q-4 7-8 2Q-12 7-16 2Z" fill="{color}" '
            f'fill-opacity=".3" stroke="{color}" stroke-width="1.4"/>'
            f'<circle cx="0" cy="-8" r="3" fill="{color}"/></g></g>'
        )
    css = (".drift{animation:drift linear infinite}"
           "@keyframes drift{0%{transform:translate(var(--x),150px);opacity:0}12%,85%{opacity:1}"
           "100%{transform:translate(calc(var(--x) + var(--dx)),-60px);opacity:0}}"
           ".bell{animation:bell 2.2s ease-in-out infinite}@keyframes bell{50%{transform:scale(.84,1.12)}}"
           ".tent{animation:tent 2.2s ease-in-out infinite}@keyframes tent{50%{transform:scale(.8,1.15)}}")
    body = (jelly(110, .9, "var(--accent2)", 21, 4, 40) + jelly(300, 1.1, "var(--accent3)", 17, 12, -50)
            + jelly(470, .7, "var(--accent)", 24, 9, 30) + jelly(640, 1.15, "var(--accent3)", 16, 2, -40)
            + jelly(760, .8, "var(--accent2)", 20, 15, 30) + jelly(830, 1, "var(--accent)", 18, 7, -60))
    return css, body


def art_abyssal():
    """Chains of lights swim the full width of the banner, undulating as they go."""
    def chain(y, color, n, r0, dur, delay):
        beads = "".join(
            f'<g class="bead" style="animation-delay:-{i * .17:.2f}s">'
            f'<circle cx="{i * 17}" cy="0" r="{r0 * (2.6 - i * .05):.1f}" fill="{color}" fill-opacity=".14"/>'
            f'<circle cx="{i * 17}" cy="0" r="{r0 * (1 - i * .03):.1f}" fill="{color}"/></g>'
            for i in range(n)
        )
        return f'<g class="swim rm" style="--y:{y}px;animation-duration:{dur}s;animation-delay:-{delay}s">{beads}</g>'
    css = (".swim{animation:swim linear infinite}"
           "@keyframes swim{from{transform:translate(900px,var(--y))}to{transform:translate(-340px,var(--y))}}"
           ".bead{animation:bead 3.2s ease-in-out infinite}"
           "@keyframes bead{0%,100%{transform:translateY(-13px);opacity:.4}50%{transform:translateY(13px);opacity:1}}")
    return css, (chain(50, "var(--accent)", 18, 2.6, 19, 2) + chain(78, "var(--accent3)", 14, 1.9, 27, 15)
                 + chain(30, "var(--accent2)", 10, 1.5, 34, 24))


def art_hadal():
    """Sonar pings expand across the whole banner and an echo runs along the seabed."""
    rings = "".join(
        f'<circle class="ring fb" cx="770" cy="52" r="9" vector-effect="non-scaling-stroke" fill="none" stroke="var(--accent)" stroke-width="1.3" '
        f'style="animation-delay:-{i * 2}s"/>' for i in range(3)
    )
    bed = ("M0 108L40 102L85 109L130 100L170 106L215 99L260 108L300 103L345 110L390 101L430 107L470 100L515 108"
           "L560 102L600 107L640 98L668 106L705 101L730 109L770 102L800 107L835 99L880 108")
    css = (".ring{animation:ring 6s cubic-bezier(.2,.6,.4,1) infinite}"
           "@keyframes ring{from{transform:scale(1);opacity:.85}to{transform:scale(92);opacity:0}}"
           ".echo{stroke-dasharray:60 900;animation:echo 6s linear infinite}@keyframes echo{from{stroke-dashoffset:0}to{stroke-dashoffset:960}}")
    body = (
        f'{rings}<circle cx="770" cy="52" r="3.4" fill="var(--accent)"/>'
        f'<path d="{bed}" fill="none" stroke="var(--dim)" stroke-opacity=".4" stroke-width="1.3" stroke-linejoin="round"/>'
        f'<path class="echo rm" d="{bed}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    return css, body


def zone(idx, depth, label, title, art, seed):
    W, H = 880, 120
    rnd = random.Random(seed)
    art_css, art_body = art()
    lh, dx0, base = 46, 34, 86
    digits = ""
    for i, ch in enumerate(f"{depth:04d}"):
        d = int(ch)
        col = "".join(f'<text x="{dx0 + i * 24}" y="{base - k * lh}">{(d + k) % 10}</text>' for k in range(10))
        digits += f'<g class="roll" style="animation-delay:{i * .14:.2f}s">{col}</g>'
    css = theme(idx, idx + 1) + SNOW_CSS + SPARK_CSS + art_css + f"""
.roll{{animation:roll 9s cubic-bezier(.16,.84,.24,1) infinite backwards}}
@keyframes roll{{0%{{transform:translateY({9 * lh}px)}}16%,100%{{transform:translateY(0)}}}}
.tick{{animation:tick 3s ease-in-out infinite alternate}}
@keyframes tick{{from{{transform:translateY(-10px)}}to{{transform:translateY(10px)}}}}
@media (max-width:560px){{.mh{{display:none}}.title{{font-size:50px}}.art{{opacity:.45}}}}
""" + REDUCED % ""
    defs = water_defs(W, H) + f'<clipPath id="odo"><rect x="{dx0 - 4}" y="{base - 36}" width="110" height="46"/></clipPath>'
    ticks = "".join(
        f'<line x1="{W - 22 - (8 if i % 4 == 0 else 4)}" y1="{14 + i * 6.6:.1f}" x2="{W - 22}" y2="{14 + i * 6.6:.1f}"/>'
        for i in range(15)
    )
    body = f"""<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#water)"/>
{snow(rnd, W, H, 9)}{sparks(rnd, (210, 12, W - 40, H - 12), 4 + idx * 4)}
<g class="art">{art_body}</g></g>
{frame(W, H)}
<text class="mono" x="{dx0}" y="34" font-size="10" font-weight="700" letter-spacing="2.4" fill="var(--dim)">DEPTH</text>
<g clip-path="url(#odo)" class="mono" font-size="40" font-weight="700" fill="var(--ink)">{digits}</g>
<text class="mono" x="{dx0 + 100}" y="{base}" font-size="16" font-weight="700" fill="var(--accent)">m</text>
<line x1="186" y1="26" x2="186" y2="{H - 26}" stroke="var(--line)" stroke-width="1.5"/>
<text class="mono mh" x="210" y="48" font-size="11" font-weight="700" letter-spacing="2.4" fill="var(--accent)">{escape(label)}</text>
<text class="sans title" x="208" y="{base + 2}" font-size="36" font-weight="800" letter-spacing="-.6" fill="var(--ink)">{escape(title)}</text>
<g class="mh" stroke="var(--dim)" stroke-opacity=".6" stroke-width="1.2">{ticks}</g>
<path class="tick mh" d="M{W - 36} {H / 2} l-9 -5 v10 z" fill="var(--accent)"/>
"""
    return svg(W, H, f"{title}. {label.title()}, depth {depth} metres.", css, defs, body)


# ---------------------------------------------------------------- architecture
def architecture():
    W, H = 880, 372
    hub = (440, 150)
    left = [("Models", 70), ("Memory & RAG", 150), ("Subagents", 230)]
    right = [("MCP servers", 70), ("Tools & APIs", 150), ("Approvals", 230)]
    nw, nh, hw, hh = 172, 44, 204, 68
    css = theme(2, 3) + """
.wire{stroke-width:1.4;stroke-dasharray:4 6;stroke-opacity:.55;animation:march 1s linear infinite}
@keyframes march{to{stroke-dashoffset:-10}}
.pk{animation:pk 2.6s cubic-bezier(.4,0,.6,1) infinite}
@keyframes pk{0%{transform:translate(0,0);opacity:0}12%,88%{opacity:1}100%{transform:translate(var(--dx),var(--dy));opacity:0}}
.nd{stroke-width:1.5;animation:nd 2.6s ease-in-out infinite}
@keyframes nd{0%,55%,100%{stroke-opacity:.4}20%{stroke-opacity:1}}
.halo{animation:halo 3.2s ease-out infinite}
@keyframes halo{from{transform:scale(.6);opacity:.7}to{transform:scale(1.9);opacity:0}}
@media (max-width:560px){.mh{display:none}.n{transform:scale(1.45)}}
""" + REDUCED % ""

    def node(cx, cy, text, color, i, w=nw, h=nh):
        return (
            f'<g class="n fb"><rect class="nd" x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="11" '
            f'fill="var(--glass)" stroke="{color}" style="animation-delay:-{i * .43:.2f}s"/>'
            f'<text class="sans" x="{cx}" y="{cy + 5.5}" font-size="15" font-weight="600" text-anchor="middle" fill="var(--ink)">{escape(text)}</text></g>'
        )

    wires, nodes = "", ""
    for side, items, x in ((-1, left, 150), (1, right, 730)):
        for i, (text, y) in enumerate(items):
            x1, y1 = hub[0] + side * hw / 2, hub[1] + (y - hub[1]) * .3
            x2, y2 = x - side * nw / 2, y
            k = i + (3 if side > 0 else 0)
            wires += f'<line class="wire" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--accent)"/>'
            wires += (  # request out, result back
                f'<circle class="pk rm" cx="{x1}" cy="{y1}" r="3.4" fill="var(--accent)" '
                f'style="--dx:{x2 - x1}px;--dy:{y2 - y1}px;animation-delay:-{k * .43:.2f}s"/>'
                f'<circle class="pk rm" cx="{x2}" cy="{y2}" r="2.8" fill="var(--accent3)" '
                f'style="--dx:{x1 - x2}px;--dy:{y1 - y2}px;animation-delay:-{k * .43 + 1.3:.2f}s"/>'
            )
            nodes += node(x, y, text, "var(--accent)", k)
    data_y = 322
    data = ["Airbyte", "DuckDB", "Apache Airflow"]
    xs = [150, 440, 730]
    for i, text in enumerate(data):
        if i < 2:
            x1, x2 = xs[i] + nw / 2, xs[i + 1] - nw / 2
            wires += f'<line class="wire" x1="{x1}" y1="{data_y}" x2="{x2}" y2="{data_y}" stroke="var(--accent2)"/>'
            for j in range(3):
                wires += (
                    f'<circle class="pk rm" cx="{x1}" cy="{data_y}" r="3.2" fill="var(--accent2)" '
                    f'style="--dx:{x2 - x1}px;--dy:0px;animation-delay:-{i * .5 + j * .87:.2f}s"/>'
                )
        nodes += node(xs[i], data_y, text, "var(--accent2)", i)
    hx, hy = hub
    body = f"""<rect width="{W}" height="{H}" rx="20" fill="url(#water)"/>{frame(W, H)}
<text class="mono mh" x="26" y="34" font-size="11" font-weight="700" letter-spacing="2.4" fill="var(--accent)">AI PLATFORM</text>
<text class="mono mh" x="26" y="286" font-size="11" font-weight="700" letter-spacing="2.4" fill="var(--accent2)">DATA PLATFORM</text>
<line class="mh" x1="26" y1="266" x2="{W - 26}" y2="266" stroke="var(--line)"/>
{wires}
<g class="rm"><circle class="halo fb" cx="{hx}" cy="{hy}" r="70" vector-effect="non-scaling-stroke" fill="none" stroke="var(--accent)" stroke-width="1.2"/>
<circle class="halo fb" cx="{hx}" cy="{hy}" r="70" fill="none" stroke="var(--accent)" stroke-width="1.2" vector-effect="non-scaling-stroke" style="animation-delay:-1.6s"/></g>
{nodes}
<g class="n fb"><rect x="{hx - hw / 2}" y="{hy - hh / 2}" width="{hw}" height="{hh}" rx="14" fill="var(--bot)" stroke="var(--accent)" stroke-width="2"/>
<text class="sans" x="{hx}" y="{hy - 3}" font-size="18" font-weight="800" text-anchor="middle" fill="var(--ink)">Agent runtime</text>
<text class="mono" x="{hx}" y="{hy + 18}" font-size="12" text-anchor="middle" fill="var(--accent)">createAgent()</text></g>
"""
    title = ("AI platform: an agent runtime connected to models, memory and RAG, subagents, MCP servers, "
             "tools and APIs, and approvals. Data platform: Airbyte to DuckDB to Apache Airflow.")
    return svg(W, H, title, css, water_defs(W, H), body)


# ---------------------------------------------------------------- chips + buttons
SURFACE = (
    "svg{--bg:#0b1f27;--ink:#e6fffa;--dim:#8fb5b0;--edge:rgba(134,179,173,.3)}"
    "@media (prefers-color-scheme:light){svg{--bg:#f1faf8;--ink:#0b2b35;--dim:#47707a;--edge:rgba(11,43,53,.2)}}"
    f".sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}"
    ".run{animation:run 4.5s linear infinite}@keyframes run{to{stroke-dashoffset:-100}}"
)


def chip(label, color, i):
    H = 34
    W = round(34 + len(label) * 7.85 + 14)
    css = SURFACE + (
        ".fb{transform-box:fill-box;transform-origin:center}"
        ".pg{animation:pg 2.4s ease-out infinite}@keyframes pg{from{transform:scale(1);opacity:.7}to{transform:scale(3);opacity:0}}"
        + REDUCED % ""
    )
    delay = f"animation-delay:-{i * .37:.2f}s"
    body = (
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{H / 2 - 1}" fill="var(--bg)" stroke="var(--edge)" stroke-width="1.2"/>'
        f'<rect class="run rm" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{H / 2 - 1}" fill="none" stroke="{color}" '
        f'stroke-width="1.6" stroke-linecap="round" pathLength="100" stroke-dasharray="16 84" style="{delay}"/>'
        f'<circle class="pg fb rm" cx="18" cy="{H / 2}" r="4" fill="{color}" style="{delay}"/>'
        f'<circle cx="18" cy="{H / 2}" r="4" fill="{color}"/>'
        f'<text class="mono" x="31" y="{H / 2 + 4.5}" font-size="13" font-weight="700" fill="var(--ink)">{escape(label)}</text>'
    )
    return svg(W, H, label, css, "", body)


def button(label, sub, i):
    W, H = 252, 58
    css = SURFACE + (
        ".arr{animation:arr 1.6s ease-in-out infinite alternate}@keyframes arr{to{transform:translateX(6px)}}" + REDUCED % ""
    )
    body = (
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="var(--bg)" stroke="var(--edge)" stroke-width="1.2"/>'
        f'<rect class="run rm" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="#2ED3A7" stroke-width="2" '
        f'stroke-linecap="round" pathLength="100" stroke-dasharray="14 86" style="animation-delay:-{i * 1.5}s"/>'
        f'<text class="sans" x="20" y="26" font-size="16" font-weight="700" fill="var(--ink)">{escape(label)}</text>'
        f'<text class="mono" x="20" y="44" font-size="11.5" fill="var(--dim)">{escape(sub)}</text>'
        f'<path class="arr" d="M{W - 44} 29 h16 m-6 -6 l6 6 l-6 6" fill="none" stroke="#2ED3A7" stroke-width="2.2" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return svg(W, H, f"{label}: {sub}", css, "", body)


# ---------------------------------------------------------------- seabed footer
def seabed():
    W, H = 880, 230
    rnd = random.Random(5)
    pts, x = [], 0
    while x <= W:
        pts.append((x, 186 + rnd.uniform(-9, 9)))
        x += rnd.uniform(26, 60)
    pts.append((W, 188))
    ridge = "M0 190 " + " ".join(f"L{px:.0f} {py:.0f}" for px, py in pts)
    vents = ""
    for vx, vh in ((150, 34), (708, 44)):
        base = 186
        vents += (
            f'<path d="M{vx - 13} {base + 6} L{vx - 6} {base - vh} H{vx + 6} L{vx + 13} {base + 6} Z" fill="var(--bot)" '
            'stroke="var(--line)" stroke-width="1.3" stroke-linejoin="round"/>'
        )
        for j in range(7):
            vents += (
                f'<circle class="plume fb rm" cx="{vx + rnd.uniform(-3, 3):.0f}" cy="{base - vh - 2}" r="{rnd.uniform(2, 4):.1f}" '
                f'fill="var(--accent3)" style="--dx:{rnd.uniform(-26, 26):.0f}px;animation-delay:-{j * .7:.1f}s"/>'
            )
    css = theme(5, 6) + SNOW_CSS + SPARK_CSS + """
.plume{animation:plume 5s ease-out infinite}
@keyframes plume{0%{transform:translate(0,0) scale(.5);opacity:0}15%{opacity:.75}100%{transform:translate(var(--dx),-120px) scale(3.2);opacity:0}}
.glowline{stroke-dasharray:70 900;animation:gl 7s linear infinite}@keyframes gl{from{stroke-dashoffset:970}to{stroke-dashoffset:0}}
.up{animation:up 1.8s ease-in-out infinite alternate}@keyframes up{to{transform:translateY(-6px)}}
@media (max-width:560px){.mh{display:none}.big{font-size:44px}.small{font-size:25px}}
""" + REDUCED % ""
    body = f"""<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#water)"/>
{snow(rnd, W, H, 14)}{sparks(rnd, (20, 14, W - 20, 170), 34)}
{vents}
<path d="{ridge} V{H} H0 Z" style="fill:var(--bot)"/>
<path d="{ridge}" fill="none" stroke="var(--line)" stroke-width="1.4" stroke-linejoin="round"/>
<path class="glowline rm" d="{ridge}" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
</g>{frame(W, H)}
<text class="mono mh" x="{W / 2}" y="50" font-size="11" font-weight="700" letter-spacing="2.6" text-anchor="middle" fill="var(--accent)">SEABED  ·  END OF DIVE</text>
<text class="sans big" x="{W / 2}" y="98" font-size="34" font-weight="800" letter-spacing="-.6" text-anchor="middle" fill="var(--ink)">You've reached the bottom.</text>
<text class="sans small" x="{W / 2}" y="130" font-size="16" text-anchor="middle" fill="var(--dim)">The rest of the work is at abyabyss.github.io</text>
<path class="up mh" d="M{W / 2} 164 v-16 m-6 6 l6 -6 l6 6" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
"""
    return svg(W, H, "You've reached the bottom. The rest of the work is at abyabyss.github.io", css, water_defs(W, H), body)


# ---------------------------------------------------------------- build
if __name__ == "__main__":
    files = {
        "hero.svg": hero(),
        "zone-about.svg": zone(1, 200, "TWILIGHT ZONE  ·  200 TO 1,000 M", "About", art_twilight, 21),
        "zone-stack.svg": zone(2, 1000, "MIDNIGHT ZONE  ·  1,000 TO 4,000 M", "Stack", art_midnight, 22),
        "zone-projects.svg": zone(3, 4000, "ABYSSAL ZONE  ·  4,000 TO 6,000 M", "Projects", art_abyssal, 23),
        "zone-activity.svg": zone(4, 6000, "HADAL ZONE  ·  BELOW 6,000 M", "Activity", art_hadal, 24),
        "architecture.svg": architecture(),
        "seabed.svg": seabed(),
    }
    for i, (slug, label, color) in enumerate(STACK):
        files[f"chips/{slug}.svg"] = chip(label, color, i)
    for i, (slug, label, sub) in enumerate(BUTTONS):
        files[f"buttons/{slug}.svg"] = button(label, sub, i)
    for stale in OUT.rglob("*.svg"):
        stale.unlink()
    total = 0
    for rel, content in files.items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        total += len(content)
    print(f"wrote {len(files)} files, {total / 1024:.0f} KB total")
