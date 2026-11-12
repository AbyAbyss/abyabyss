#!/usr/bin/env python3
"""Generates the animated SVGs used by the profile README.

Run:  python3 scripts/build_assets.py

GitHub strips <style> and <script> from README markdown, but an SVG loaded
through <img> keeps its own CSS. Everything here is CSS-only (no JS, no
external fonts or images), adapts to light and dark through
prefers-color-scheme, and stops moving under prefers-reduced-motion.
"""
import random
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# Edit these to change what the hero types out.
TYPED_LINES = [
    "Building scalable backend systems",
    "Designing AI agents & LLM platforms",
    "MCP | Generative AI | Distributed Systems",
    "8 years across Node.js | Python | Golang",
]

PALETTE = """
svg{--bg0:#03141c;--bg1:#062630;--bg2:#020a10;--ink:#eafff9;--muted:#8db5b1;
--accent:#2ED3A7;--accent2:#4cc9f0;--accent3:#9d6bff;--ray:#bafff0;--line:rgba(46,211,167,.28);
--panel:#081b22;--node:#0e2a32;--sheen:#ffffff}
@media (prefers-color-scheme:light){svg{--bg0:#f6fffc;--bg1:#d8f5ee;--bg2:#b4e1e4;--ink:#06222b;
--muted:#3a6068;--accent:#0b8f6e;--accent2:#0a7ea4;--accent3:#6a3fd6;--ray:#ffffff;
--line:rgba(11,143,110,.35);--panel:#f1fbf8;--node:#ffffff;--sheen:#ffffff}}
"""


def sine_path(y, amp, period, start, end, close_to=None):
    """A smooth sine-like path made of quadratic curves."""
    half = period / 2
    d = f"M{start} {y} Q{start + half / 2} {y - amp} {start + half} {y}"
    x = start + half
    while x < end:
        x += half
        d += f" T{x:g} {y}"
    if close_to is not None:
        d += f" V{close_to} H{start} Z"
    return d


def hero():
    W, H = 880, 360
    rnd = random.Random(7)
    css = [PALETTE]
    css.append(f"""
.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}
.ray{{fill:url(#ray);animation:sway 11s ease-in-out infinite alternate}}
@keyframes sway{{from{{transform:rotate(-3.5deg);opacity:.45}}to{{transform:rotate(3.5deg);opacity:1}}}}
.spot{{animation:roam 18s ease-in-out infinite}}
@keyframes roam{{0%,100%{{transform:translate(150px,110px)}}25%{{transform:translate(700px,90px)}}
50%{{transform:translate(590px,270px)}}75%{{transform:translate(250px,250px)}}}}
.spot2{{animation:roam2 23s ease-in-out infinite}}
@keyframes roam2{{0%,100%{{transform:translate(760px,280px)}}33%{{transform:translate(380px,320px)}}
66%{{transform:translate(120px,60px)}}}}
.p{{animation:rise linear infinite}}
@keyframes rise{{0%{{transform:translate(0,0);opacity:0}}12%{{opacity:.95}}80%{{opacity:.6}}
100%{{transform:translate(var(--dx),-430px);opacity:0}}}}
.cur{{fill:none;stroke:var(--line);animation:flow linear infinite}}
@keyframes flow{{to{{transform:translateX(-440px)}}}}
.in{{animation:in .9s cubic-bezier(.2,.7,.2,1) both}}
@keyframes in{{from{{opacity:0;transform:translateY(14px)}}}}
.sheen{{animation:sheen 7s ease-in-out infinite}}
@keyframes sheen{{0%,35%{{transform:translateX(0)}}75%,100%{{transform:translateX(1100px)}}}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 2s ease-out infinite}}
@keyframes ping{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3.4);opacity:0}}}}
.ch{{opacity:0;animation:ch 18s linear infinite}}
@keyframes ch{{0%,30%{{opacity:1}}30.01%,100%{{opacity:0}}}}
.ln{{animation:ln 18s linear infinite}}
@keyframes ln{{0%,21%{{opacity:1}}23%,100%{{opacity:0}}}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
""")

    # --- typing effect: every glyph sits on a fixed grid, so no font metrics needed
    size, cw = 18, 10.8
    box_w, box_h, box_y = 580, 46, 232
    box_x = (W - box_w) / 2
    tx, ty = box_x + 46, box_y + 30
    cycle, slot, type_t = 18.0, 4.5, 1.9
    typed = []
    for k, line in enumerate(TYPED_LINES):
        n = len(line)
        dt = type_t / n
        base = k * slot - cycle
        css.append(
            f"@keyframes c{k}{{0%{{transform:translateX(0);animation-timing-function:steps({n},start)}}"
            f"{type_t / cycle * 100:.3f}%,100%{{transform:translateX({n * cw:.1f}px)}}}}"
        )
        spans = "".join(
            f'<tspan class="ch" x="{tx + i * cw:.1f}" style="animation-delay:{base + i * dt:.3f}s">{escape(c)}</tspan>'
            for i, c in enumerate(line)
            if c != " "
        )
        typed.append(
            f'<g class="ln l{k}" style="animation-delay:{base:.2f}s">'
            f'<text class="mono" y="{ty}" font-size="{size}" fill="var(--ink)">{spans}</text>'
            f'<g class="curw" style="animation:c{k} {cycle}s linear {base:.2f}s infinite">'
            f'<rect class="blink" x="{tx}" y="{ty - 16}" width="9" height="21" rx="1.5" fill="var(--accent)"/></g></g>'
        )
    css.append("""
@media (prefers-reduced-motion:reduce){*{animation:none!important}.ln{opacity:0}.ln.l0{opacity:1}
.ch{opacity:1}.curw,.sheen,.ping{display:none}}
""")

    rays = "".join(
        f'<polygon class="ray" style="transform-origin:{x}px -40px;animation-duration:{d}s;animation-delay:-{dl}s" '
        f'points="{x - w / 2},-40 {x + w / 2},-40 {x + w * 1.6 + lean},{H + 30} {x - w * 1.6 + lean},{H + 30}"/>'
        for x, w, lean, d, dl in [(110, 46, 70, 11, 0), (300, 70, 40, 14, 5), (470, 38, 10, 9, 2),
                                  (640, 84, -40, 13, 7), (800, 44, -80, 10, 4)]
    )

    particles = ""
    for _ in range(38):
        x, r = rnd.uniform(10, W - 10), rnd.uniform(0.8, 2.6)
        dur, delay, dx = rnd.uniform(9, 24), rnd.uniform(0, 24), rnd.uniform(-40, 40)
        color = rnd.choice(["var(--accent)", "var(--accent)", "var(--accent2)", "var(--ray)"])
        particles += (
            f'<circle class="p" cx="{x:.0f}" cy="{H + 20}" r="{r:.1f}" fill="{color}" '
            f'style="--dx:{dx:.0f}px;animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>'
        )

    currents = "".join(
        f'<path class="cur" d="{sine_path(y, amp, 440, 0, W + 440)}" stroke-width="{sw}" '
        f'stroke-dasharray="{dash}" style="animation-duration:{d}s"/>'
        for y, amp, sw, dash, d in [(330, 10, 1.4, "none", 16), (340, 13, 1, "3 9", 24), (350, 8, 1.2, "none", 11)]
    )

    name = (
        f'font-size="60" font-weight="800" letter-spacing="-1.2" text-anchor="middle" x="{W / 2}" y="150"'
    )
    title = "Aby Saji Pappachan"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Aby Saji Pappachan. Technical Lead, Backend and AI Engineer. Open to work.</title>
<desc id="d">{escape(". ".join(TYPED_LINES))}.</desc>
<style>{"".join(css)}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--bg1)"/><stop offset=".45" style="stop-color:var(--bg0)"/><stop offset="1" style="stop-color:var(--bg2)"/></linearGradient>
<linearGradient id="ray" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--ray)" stop-opacity=".2"/><stop offset="1" style="stop-color:var(--ray)" stop-opacity="0"/></linearGradient>
<radialGradient id="spot"><stop offset="0" style="stop-color:var(--accent)" stop-opacity=".34"/><stop offset="1" style="stop-color:var(--accent)" stop-opacity="0"/></radialGradient>
<radialGradient id="spot2"><stop offset="0" style="stop-color:var(--accent3)" stop-opacity=".26"/><stop offset="1" style="stop-color:var(--accent3)" stop-opacity="0"/></radialGradient>
<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" style="stop-color:var(--ink)"/><stop offset=".55" style="stop-color:var(--accent)"/><stop offset="1" style="stop-color:var(--accent2)"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" style="stop-color:var(--sheen)" stop-opacity="0"/><stop offset=".5" style="stop-color:var(--sheen)" stop-opacity=".85"/><stop offset="1" style="stop-color:var(--sheen)" stop-opacity="0"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<clipPath id="nameclip"><text class="sans" {name}>{title}</text></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{rays}
<circle class="spot" r="230" fill="url(#spot)"/>
<circle class="spot2" r="190" fill="url(#spot2)"/>
{currents}
{particles}
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" stroke="var(--line)" stroke-width="1.5"/>

<g class="in">
<rect x="{W / 2 - 84}" y="34" width="168" height="28" rx="14" fill="var(--panel)" stroke="var(--line)"/>
<circle class="ping" cx="{W / 2 - 62}" cy="48" r="4" fill="var(--accent)"/>
<circle cx="{W / 2 - 62}" cy="48" r="4" fill="var(--accent)"/>
<text class="mono" x="{W / 2 + 9}" y="52.5" font-size="12" font-weight="700" letter-spacing="1.6" text-anchor="middle" fill="var(--ink)">OPEN TO WORK</text>
</g>

<g class="in" style="animation-delay:.15s">
<text class="sans" {name} fill="url(#name)">{title}</text>
<g clip-path="url(#nameclip)"><rect class="sheen" x="-120" y="90" width="110" height="80" fill="url(#sheen)"/></g>
</g>

<text class="sans in" style="animation-delay:.3s" x="{W / 2}" y="192" font-size="15" font-weight="600" letter-spacing="3.4" text-anchor="middle" fill="var(--muted)">TECHNICAL LEAD  ·  BACKEND &amp; AI ENGINEER</text>

<g class="in" style="animation-delay:.45s">
<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="12" fill="var(--panel)" fill-opacity=".72" stroke="var(--line)"/>
<text class="mono" x="{box_x + 20}" y="{ty}" font-size="{size}" font-weight="700" fill="var(--accent)">&gt;</text>
{"".join(typed)}
</g>

<text class="sans in" style="animation-delay:.6s" x="{W / 2}" y="308" font-size="13" letter-spacing=".4" text-anchor="middle" fill="var(--muted)">Walsall, United Kingdom  ·  Backend, AI and Platform engineering</text>
</svg>
"""


def pipeline():
    W, row_h, gap = 880, 96, 14
    H = row_h * 2 + gap
    rows = [
        ("AI PLATFORM", ["LLM models", "Agent runtime", "MCP", "Tools & APIs"], "var(--accent)"),
        ("DATA PLATFORM", ["Airbyte", "DuckDB", "Airflow", "Analytics"], "var(--accent2)"),
    ]
    nw, nh = 148, 40
    centers = [143, 341, 539, 737]
    body = ""
    for r, (label, nodes, color) in enumerate(rows):
        y0 = r * (row_h + gap)
        cy = y0 + 58
        body += (
            f'<rect x=".75" y="{y0 + .75}" width="{W - 1.5}" height="{row_h - 1.5}" rx="14" fill="var(--panel)" stroke="var(--line)" stroke-width="1.5"/>'
            f'<text class="mono" x="22" y="{y0 + 24}" font-size="11" font-weight="700" letter-spacing="2" fill="{color}">{label}</text>'
        )
        for i, node in enumerate(nodes):
            cx = centers[i]
            if i < len(nodes) - 1:
                x1, x2 = cx + nw / 2, centers[i + 1] - nw / 2
                body += f'<line class="wire" x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="{color}"/>'
                for j in range(2):
                    body += (
                        f'<circle class="pk" cx="{x1}" cy="{cy}" r="3.2" fill="{color}" '
                        f'style="--d:{x2 - x1}px;animation-delay:-{(i * .45 + j * .9 + r * .3):.2f}s"/>'
                    )
            body += (
                f'<rect class="nd" x="{cx - nw / 2}" y="{cy - nh / 2}" width="{nw}" height="{nh}" rx="10" '
                f'fill="var(--node)" stroke="{color}" style="animation-delay:{i * .45 + r * .3:.2f}s"/>'
                f'<text class="sans" x="{cx}" y="{cy + 5}" font-size="14" font-weight="600" text-anchor="middle" fill="var(--ink)">{escape(node)}</text>'
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">AI platform: LLM models to agent runtime to MCP to tools and APIs. Data platform: Airbyte to DuckDB to Airflow to analytics.</title>
<style>{PALETTE}
.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}
.wire{{stroke-width:1.5;stroke-dasharray:4 5;stroke-opacity:.6;animation:march .9s linear infinite}}
@keyframes march{{to{{stroke-dashoffset:-9}}}}
.pk{{animation:pk 1.8s linear infinite}}
@keyframes pk{{0%{{transform:translateX(0);opacity:0}}15%,85%{{opacity:1}}100%{{transform:translateX(var(--d));opacity:0}}}}
.nd{{stroke-width:1.5;stroke-opacity:.45;animation:nd 1.8s ease-in-out infinite}}
@keyframes nd{{0%,60%,100%{{stroke-opacity:.45;stroke-width:1.5}}25%{{stroke-opacity:1;stroke-width:2.4}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.pk{{display:none}}}}
</style>
{body}
</svg>
"""


def divider():
    W, H = 880, 16
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="presentation">
<style>
.s{{animation:s 5s cubic-bezier(.5,0,.5,1) infinite}}
@keyframes s{{from{{transform:translateX(-220px)}}to{{transform:translateX({W}px)}}}}
@media (prefers-reduced-motion:reduce){{.s{{display:none}}}}
</style>
<defs>
<linearGradient id="l"><stop offset="0" stop-color="#2ED3A7" stop-opacity="0"/><stop offset=".3" stop-color="#2ED3A7" stop-opacity=".55"/><stop offset=".7" stop-color="#9d6bff" stop-opacity=".55"/><stop offset="1" stop-color="#9d6bff" stop-opacity="0"/></linearGradient>
<linearGradient id="g"><stop offset="0" stop-color="#4cc9f0" stop-opacity="0"/><stop offset=".8" stop-color="#2ED3A7"/><stop offset="1" stop-color="#2ED3A7" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}"/></clipPath>
</defs>
<rect y="7.25" width="{W}" height="1.5" fill="url(#l)"/>
<g clip-path="url(#c)"><g class="s"><rect y="6.5" width="220" height="3" rx="1.5" fill="url(#g)"/><circle cx="182" cy="8" r="3.5" fill="#2ED3A7"/></g></g>
</svg>
"""


def footer():
    W, H = 880, 70
    layers = [(22, 16, "#9d6bff", .22, 19, "reverse"), (32, 20, "#4cc9f0", .26, 13, "normal"),
              (44, 14, "#2ED3A7", .42, 9, "reverse")]
    waves = "".join(
        f'<path class="w" d="{sine_path(y, amp, 440, -440, W + 440, close_to=H)}" fill="{c}" fill-opacity="{o}" '
        f'style="animation-duration:{d}s;animation-direction:{direction}"/>'
        for y, amp, c, o, d, direction in layers
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="presentation" preserveAspectRatio="none">
<style>
.w{{animation:w linear infinite}}
@keyframes w{{to{{transform:translateX(440px)}}}}
@media (prefers-reduced-motion:reduce){{.w{{animation:none}}}}
</style>
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#c)">{waves}</g>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in [("hero", hero), ("pipeline", pipeline), ("divider", divider), ("footer", footer)]:
        path = OUT / f"{name}.svg"
        path.write_text(fn())
        print(f"{path.relative_to(OUT.parent)}  {path.stat().st_size / 1024:.1f} KB")
