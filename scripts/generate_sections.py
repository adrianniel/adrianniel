"""Generate the section images that sit under the hero card:
assets/projects.svg (featured projects) and assets/footer.svg.

Usage, from the repo root:
    python scripts/generate_sections.py

Uses the same palette as generate_hero.py. No third-party packages needed.
"""

import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

PROJECTS = [
    {
        "name": "Tumbli",
        "tag": "new",
        "desc": "A floating water buddy for Windows: a little bottle with a face that docks at the screen edge, fills up as you drink and reminds you to take a break.",
        "stack": ["Tauri", "Rust", "React", "TypeScript"],
    },
    {
        "name": "iQueue",
        "tag": "in progress",
        "desc": "Queue-management platform for campus offices: a student mobile app, an admin portal and a live display board.",
        "stack": ["Expo", "Next.js", "Express", "Prisma"],
    },
    {
        "name": "L.I.S.A.",
        "tag": "live",
        "desc": "Irrigation Survey & Analysis System for BISU Bilar: farmer surveys on a map, reports and AI-generated analysis.",
        "stack": ["React", "Express", "OpenLayers", "MySQL"],
    },
    {
        "name": "Dagohoy Pharmacy",
        "tag": "live",
        "desc": "Point-of-sale and pharmacy operations workspace with role-based screens for owners, admins and cashiers.",
        "stack": ["React", "TypeScript", "NestJS", "MySQL"],
    },
]

W = 1120
BG = "#0c0f1a"
CARD = "#0f1324"
BORDER = "#252b3f"
TEXT = "#e8ecf4"
MUTED = "#7c869e"
KEY = "#3fdc9a"
CYAN = "#22d3ee"
VIOLET = "#a78bfa"
PINK = "#f472b6"
CMDLET = "#f9e2af"

MONO = "'Cascadia Code', 'Cascadia Mono', Consolas, ui-monospace, SFMono-Regular, Menlo, monospace"
SANS = "'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"

STYLE = (
    "<style>"
    ".f{opacity:0;animation:fade .6s ease-out forwards}"
    "@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
    ".blink{animation:blink 1.05s steps(1) infinite}"
    "@keyframes blink{50%{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.f{opacity:1}}"
    "</style>"
)


def prompt_line(x, y, command, flag, delay=0.0):
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="16" class="f" style="animation-delay:{delay}s">'
        f'<tspan fill="{VIOLET}">&gt; </tspan><tspan fill="{CMDLET}">{escape(command)}</tspan>'
        f'<tspan fill="{MUTED}"> {escape(flag)}</tspan></text>'
    )


def projects():
    pad, gap = 24, 20
    cols = 2 if len(PROJECTS) % 2 == 0 and len(PROJECTS) % 3 else 3
    rows = -(-len(PROJECTS) // cols)
    card_w = (W - 2 * pad - (cols - 1) * gap) / cols
    card_h = 236 if cols == 3 else 216
    top = 62
    H = top + rows * card_h + (rows - 1) * gap + pad
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="Featured projects: '
        + escape("; ".join(f"{p['name']}: {p['desc']}" for p in PROJECTS))
        + '">',
        "<defs>",
        # A highlight that travels around each card's border.
        f'<linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{card_w}" y2="{card_h}">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/>'
        f'<stop offset="1" stop-color="{PINK}"/></linearGradient>',
        f'<linearGradient id="fadeTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" '
        f'stop-opacity=".08"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>',
        "</defs>",
        STYLE,
        prompt_line(pad + 4, 32, "projects", "--featured"),
        f'<rect class="blink" x="{pad + 4 + 22 * 9.6:.1f}" y="18" width="9" height="18" fill="{TEXT}" opacity=".8"/>',
    ]
    perimeter = 2 * (card_w + card_h)
    for i, p in enumerate(PROJECTS):
        x = pad + (i % cols) * (card_w + gap)
        y = top + (i // cols) * (card_h + gap)
        delay = 0.25 + i * 0.18
        # Position on the outer group; the fade-in (a CSS transform) goes on the
        # inner one so it doesn't override the translate.
        g = [f'<g transform="translate({x:.1f} {y})"><g class="f" style="animation-delay:{delay:.2f}s">']
        g.append(f'<rect width="{card_w:.1f}" height="{card_h}" rx="14" fill="{CARD}" stroke="{BORDER}"/>')
        g.append(f'<rect width="{card_w:.1f}" height="90" rx="14" fill="url(#fadeTop)"/>')
        # Travelling light on the border.
        g.append(
            f'<rect x=".5" y=".5" width="{card_w - 1:.1f}" height="{card_h - 1}" rx="14" fill="none" '
            f'stroke="url(#edge)" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-dasharray="{perimeter * 0.18:.0f} {perimeter * 0.82:.0f}">'
            f'<animate attributeName="stroke-dashoffset" from="{perimeter:.0f}" to="0" dur="{6 + i}s" '
            f'begin="{delay:.2f}s" repeatCount="indefinite"/></rect>'
        )
        # Index + tag.
        g.append(f'<text x="22" y="34" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}">'
                 f'0{i + 1} / PROJECT</text>')
        tag_colour = {"live": KEY, "in progress": CYAN, "new": PINK}.get(p["tag"], VIOLET)
        tag_w = 22 + len(p["tag"]) * 7.4
        tx = card_w - 22 - tag_w
        g.append(f'<rect x="{tx:.1f}" y="18" width="{tag_w:.1f}" height="22" rx="11" fill="{tag_colour}" '
                 f'fill-opacity=".1" stroke="{tag_colour}" stroke-opacity=".5"/>')
        g.append(f'<circle cx="{tx + 11:.1f}" cy="29" r="3" fill="{tag_colour}">'
                 + ('<animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/>'
                    if p["tag"] != "shipped" else "")
                 + "</circle>")
        g.append(f'<text x="{tx + 19:.1f}" y="33" font-family="{MONO}" font-size="12" fill="{tag_colour}">'
                 f'{escape(p["tag"])}</text>')
        # Title + description.
        g.append(f'<text x="22" y="76" font-family="{SANS}" font-size="22" font-weight="700" fill="{TEXT}">'
                 f'{escape(p["name"])}</text>')
        for j, line in enumerate(textwrap.wrap(p["desc"], int((card_w - 44) / 7.4))[:4]):
            g.append(f'<text x="22" y="{106 + j * 21}" font-family="{SANS}" font-size="14.5" fill="{MUTED}">'
                     f'{escape(line)}</text>')
        # Stack chips.
        cx = 22
        for k, s in enumerate(p["stack"]):
            w = 18 + len(s) * 7.6
            colour = CYAN if k % 2 == 0 else VIOLET
            g.append(f'<rect x="{cx:.1f}" y="{card_h - 46}" width="{w:.1f}" height="26" rx="13" fill="{colour}" '
                     f'fill-opacity=".07" stroke="{colour}" stroke-opacity=".4"/>'
                     f'<text x="{cx + w / 2:.1f}" y="{card_h - 28}" text-anchor="middle" font-family="{MONO}" '
                     f'font-size="12" fill="{TEXT}">{escape(s)}</text>')
            cx += w + 8
        g.append("</g></g>")
        o.extend(g)
    o.append("</svg>")
    return "".join(o)


def footer():
    H = 70
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="Session ended">'
        "<defs>"
        f'<linearGradient id="line" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".3" stop-color="{CYAN}"/>'
        f'<stop offset=".7" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="-{W * 0.3:.0f} 0;{W * 0.3:.0f} 0;-{W * 0.3:.0f} 0" '
        f'dur="8s" repeatCount="indefinite"/></linearGradient>'
        "</defs>"
        + STYLE
        + f'<rect x="24" y="20" width="{W - 48}" height="1.5" fill="url(#line)"/>'
        f'<text x="{W / 2}" y="52" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">'
        f'<tspan fill="{VIOLET}">&gt; </tspan><tspan fill="{CMDLET}">exit</tspan>'
        f'<tspan>  ·  session saved  ·  thanks for visiting  </tspan>'
        f'<tspan fill="{KEY}">[0]</tspan></text>'
        "</svg>"
    )


if __name__ == "__main__":
    for name, svg in (("projects.svg", projects()), ("footer.svg", footer())):
        path = ASSETS / name
        path.write_text(svg, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")
