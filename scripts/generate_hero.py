"""Generate assets/hero.svg: an animated Windows Terminal / PowerShell card.

Usage, from the repo root:
    python scripts/generate_hero.py

Edit the CONFIG section and re-run whenever your details change.
No third-party packages needed.
"""

from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------- #
# CONFIG
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "hero.svg"

BANNER = "NIEL ADRIAN"
PS_USER = "niel"
COMMAND = ("Get-Profile", "-Verbose")

FIELDS = [
    ("Name", "Niel Adrian Garig"),
    ("Role", "Full-Stack Developer"),
    ("Location", "Bohol, Philippines"),
    ("Lab", "MAKASA Laboratory"),
    ("Status", "Building iQueue: campus queueing platform"),
    ("Stack", "{TypeScript, React, Next.js, React Native, Node.js, NestJS, Prisma, MySQL}"),
]

W = 1120

# Palette (Windows Terminal dark, with a neon accent).
WINDOW = "#0c0f1a"
TABBAR = "#161a29"
BORDER = "#262c40"
TEXT = "#e8ecf4"
MUTED = "#7c869e"
CMDLET = "#f9e2af"     # PowerShell cmdlet yellow
PARAM = "#9aa3b8"
KEY = "#3fdc9a"        # Format-List label green
CYAN = "#22d3ee"
VIOLET = "#a78bfa"
PINK = "#f472b6"
PS_BLUE = "#2671be"

MONO = "'Cascadia Code', 'Cascadia Mono', Consolas, ui-monospace, SFMono-Regular, Menlo, monospace"
SANS = "'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"
FONT_SIZE, CHAR_W, LINE_H = 16, 9.6, 27

# 5-row pixel font for the banner.
GLYPHS = {
    "N": ["X...X", "XX..X", "X.X.X", "X..XX", "X...X"],
    "I": ["XXX", ".X.", ".X.", ".X.", "XXX"],
    "E": ["XXXX", "X...", "XXX.", "X...", "XXXX"],
    "L": ["X...", "X...", "X...", "X...", "XXXX"],
    "A": [".XX.", "X..X", "XXXX", "X..X", "X..X"],
    "D": ["XXX.", "X..X", "X..X", "X..X", "XXX."],
    "R": ["XXX.", "X..X", "XXX.", "X.X.", "X..X"],
    "G": [".XXX", "X...", "X.XX", "X..X", ".XXX"],
    " ": ["..", "..", "..", "..", ".."],
}
CELL, BLOCK = 13, 11.5

# --------------------------------------------------------------------------- #


def run(x0, y, segments, extra=""):
    """A line of text where every character has an explicit x, so columns line
    up whatever monospace font the viewer ends up with."""
    spans, col = [], 0
    for text, colour in segments:
        if text.strip():
            xs = " ".join(f"{x0 + (col + k) * CHAR_W:.1f}" for k in range(len(text)))
            spans.append(f'<tspan x="{xs}" fill="{colour}">{escape(text)}</tspan>')
        col += len(text)
    return f'<text y="{y}"{extra} xml:space="preserve">{"".join(spans)}</text>'


def fade(begin):
    return f' class="f" style="animation-delay:{begin:.2f}s"'


def banner_rects(x0, y0):
    rects, x = [], x0
    for ch in BANNER:
        rows = GLYPHS[ch]
        for r, row in enumerate(rows):
            for c, on in enumerate(row):
                if on == "X":
                    rects.append((x + c * CELL, y0 + r * CELL))
        x += (len(rows[0]) + 1) * CELL
    return rects, x - CELL - x0


def build():
    o = []
    a = o.append
    pad = 24                    # transparent margin for the drop shadow
    win_x, win_y = pad, pad
    tab_h = 46
    left = win_x + 34
    y = win_y + tab_h + 44

    # ---------- timeline ----------
    t_banner_head = 0.2
    t_type = 0.8
    type_dur = 0.06 * (len(COMMAND[0]) + 1 + len(COMMAND[1]))
    t_load = t_type + type_dur + 0.3
    load_dur = 1.1
    t_banner = t_load + load_dur + 0.2
    t_fields = t_banner + 0.9

    body = []
    b = body.append

    # Header lines.
    b(run(left, y, [("PowerShell 7.5.0", MUTED)], fade(t_banner_head)))
    y += LINE_H * 2

    # Prompt + typed command (revealed by a clip rect that grows a char at a time).
    prompt = f"PS C:\\Users\\{PS_USER}> "
    cmd_x = left + len(prompt) * CHAR_W
    n_chars = len(COMMAND[0]) + 1 + len(COMMAND[1])
    steps = ";".join(f"{i * CHAR_W:.1f}" for i in range(n_chars + 1))
    b(run(left, y, [(prompt, TEXT)], fade(t_type - 0.4)))
    b(f'<clipPath id="typed"><rect x="{cmd_x}" y="{y - 20}" height="28" width="0">'
      f'<animate attributeName="width" values="{steps}" begin="{t_type}s" dur="{type_dur:.2f}s" '
      f'calcMode="discrete" fill="freeze"/></rect></clipPath>')
    b(f'<g clip-path="url(#typed)">'
      + run(cmd_x, y, [(COMMAND[0], CMDLET), (" ", TEXT), (COMMAND[1], PARAM)]) + "</g>")
    y += LINE_H

    # Loading bar.
    bar_x = left + len("Loading profile  ") * CHAR_W
    bar_w = 220
    b(run(left, y, [("Loading profile", MUTED)], fade(t_load)))
    b(f'<g{fade(t_load)}><rect x="{bar_x}" y="{y - 12}" width="{bar_w}" height="10" rx="5" fill="{BORDER}"/>'
      f'<rect x="{bar_x}" y="{y - 12}" width="0" height="10" rx="5" fill="url(#accent)">'
      f'<animate attributeName="width" from="0" to="{bar_w}" begin="{t_load}s" dur="{load_dur}s" '
      f'calcMode="spline" keySplines=".4 0 .2 1" fill="freeze"/></rect></g>')
    pct_x = bar_x + bar_w + 14
    b(f'<text x="{pct_x}" y="{y}" fill="{KEY}" opacity="0">100%'
      f'<set attributeName="opacity" to="1" begin="{t_load + load_dur}s" fill="freeze"/></text>')
    y += LINE_H * 2

    # Pixel banner with a shadow layer, wiped in from the left.
    banner_y = y - 14
    rects, banner_w = banner_rects(left, banner_y)
    b(f'<clipPath id="wipe"><rect x="{left - 10}" y="{banner_y - 10}" height="{5 * CELL + 30}" width="0">'
      f'<animate attributeName="width" from="0" to="{banner_w + 30}" begin="{t_banner}s" dur=".8s" '
      f'calcMode="spline" keySplines=".2 .7 .3 1" fill="freeze"/></rect></clipPath>')
    b('<g clip-path="url(#wipe)">')
    b(f'<g fill="{VIOLET}" fill-opacity=".22">'
      + "".join(f'<rect x="{x + 3:.1f}" y="{yy + 3:.1f}" width="{BLOCK}" height="{BLOCK}" rx="2"/>' for x, yy in rects)
      + "</g>")
    b('<g fill="url(#shine)" filter="url(#glow)">'
      + "".join(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{BLOCK}" height="{BLOCK}" rx="2"/>' for x, yy in rects)
      + "</g></g>")
    # Tagline beside the banner.
    tag_x = left + banner_w + 40
    b(f'<g{fade(t_banner + 0.5)}>'
      f'<text x="{tag_x}" y="{banner_y + 24}" font-family="{SANS}" font-size="20" font-weight="600" '
      f'fill="{TEXT}">Full-Stack Developer</text>'
      f'<text x="{tag_x}" y="{banner_y + 52}" font-family="{MONO}" font-size="14" fill="{MUTED}">'
      f'web · mobile · api · data</text></g>')
    y = banner_y + 5 * CELL + LINE_H + 16

    # Format-List output.
    key_w = max(len(k) for k, _ in FIELDS) + 1
    for i, (k, v) in enumerate(FIELDS):
        seg = [(k.ljust(key_w), KEY), (": ", MUTED)]
        if k == "Status":
            # Pulsing "live" dot in front of the status.
            dot_x = left + (key_w + 2) * CHAR_W + 4
            b(f'<g{fade(t_fields + i * 0.12)}><circle cx="{dot_x}" cy="{y - 5}" r="4" fill="{KEY}" class="pulse"/>'
              f'<circle cx="{dot_x}" cy="{y - 5}" r="4" fill="{KEY}"/></g>')
            seg.append(("  " + v, TEXT))
        else:
            seg.append((v, TEXT))
        b(run(left, y, seg, fade(t_fields + i * 0.12)))
        y += LINE_H

    # Final prompt with a blinking cursor.
    y += LINE_H
    t_end = t_fields + len(FIELDS) * 0.12 + 0.2
    b(run(left, y, [(prompt, TEXT)], fade(t_end)))
    cur_x = left + len(prompt) * CHAR_W
    b(f'<g{fade(t_end)}><rect class="blink" x="{cur_x:.1f}" y="{y - 15}" width="9" height="19" fill="{TEXT}"/></g>')

    win_h = y + 40 - win_y
    H = win_y + win_h + pad
    win_w = W - 2 * pad

    # ---------- document ----------
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{MONO}" font-size="{FONT_SIZE}" role="img" '
      f'aria-label="PowerShell window: Get-Profile for Niel Adrian Garig, Full-Stack Developer">')
    a("<defs>")
    a(f'<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="{left}" y1="0" x2="{left + banner_w}" y2="0">'
      f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/>'
      f'<stop offset="1" stop-color="{PINK}"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{banner_w * 0.35:.0f} 0;0 0" '
      f'dur="6s" repeatCount="indefinite"/></linearGradient>')
    a(f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/>'
      f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient>')
    a(f'<linearGradient id="winBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f1324"/>'
      f'<stop offset="1" stop-color="{WINDOW}"/></linearGradient>')
    a(f'<radialGradient id="aura" cx=".85" cy=".1" r=".6"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".16"/>'
      f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>')
    a('<filter id="glow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="4" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    a('<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
      '<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".45"/></filter>')
    a(f'<clipPath id="win"><rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" rx="12"/></clipPath>')
    a("</defs>")
    a("<style>"
      ".f{opacity:0;animation:fade .45s ease-out forwards}"
      "@keyframes fade{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}"
      ".blink{animation:blink 1.05s steps(1) infinite}"
      "@keyframes blink{50%{opacity:0}}"
      ".pulse{animation:pulse 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}"
      "@keyframes pulse{from{transform:scale(1);opacity:.8}to{transform:scale(3.4);opacity:0}}"
      "@media (prefers-reduced-motion:reduce){*{animation:none!important}.f{opacity:1}}"
      "</style>")

    # Window frame.
    a(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" rx="12" fill="url(#winBg)" filter="url(#shadow)"/>')
    a('<g clip-path="url(#win)">')
    a(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" fill="url(#aura)"/>')
    a(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{tab_h}" fill="{TABBAR}"/>')
    # Active tab.
    tab_x, tab_w = win_x + 10, 230
    a(f'<path d="M{tab_x} {win_y + tab_h}V{win_y + 16}a8 8 0 0 1 8-8H{tab_x + tab_w - 8}a8 8 0 0 1 8 8V{win_y + tab_h}Z" '
      f'fill="#0f1324"/>')
    a(f'<rect x="{tab_x}" y="{win_y + 8}" width="{tab_w}" height="2" fill="url(#accent)"/>')
    ix, iy = tab_x + 16, win_y + 18
    a(f'<rect x="{ix}" y="{iy}" width="18" height="18" rx="4" fill="{PS_BLUE}"/>'
      f'<path d="M{ix + 4} {iy + 5}l5 4-5 4" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
      f'<path d="M{ix + 10} {iy + 13.5}h4" stroke="#fff" stroke-width="1.8" stroke-linecap="round"/>')
    a(f'<text x="{ix + 28}" y="{iy + 14}" font-family="{SANS}" font-size="14" fill="{TEXT}">PowerShell</text>')
    a(f'<path d="M{tab_x + tab_w - 26} {iy + 5}l8 8m0-8l-8 8" stroke="{MUTED}" stroke-width="1.4" stroke-linecap="round"/>')
    # New-tab + dropdown.
    px = tab_x + tab_w + 20
    a(f'<path d="M{px} {iy + 9}h12M{px + 6} {iy + 3}v12" stroke="{MUTED}" stroke-width="1.5" stroke-linecap="round"/>')
    a(f'<path d="M{px + 30} {iy + 7}l5 5 5-5" stroke="{MUTED}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    # Window controls.
    rx = win_x + win_w
    cy = win_y + tab_h / 2
    a(f'<path d="M{rx - 150} {cy}h12" stroke="{MUTED}" stroke-width="1.3"/>')
    a(f'<rect x="{rx - 100}" y="{cy - 6}" width="12" height="12" rx="2" fill="none" stroke="{MUTED}" stroke-width="1.3"/>')
    a(f'<path d="M{rx - 46} {cy - 6}l12 12m0-12l-12 12" stroke="{MUTED}" stroke-width="1.3"/>')
    a(f'<rect x="{win_x}" y="{win_y + tab_h}" width="{win_w}" height="1" fill="{BORDER}"/>')
    a("".join(body))
    a("</g>")
    a(f'<rect x="{win_x + .5}" y="{win_y + .5}" width="{win_w - 1}" height="{win_h - 1}" rx="12" fill="none" stroke="{BORDER}"/>')
    a("</svg>")

    OUTPUT.write_text("".join(o), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({W}x{H}, {OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
