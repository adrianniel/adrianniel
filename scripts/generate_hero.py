"""Generate assets/hero.svg: an animated Windows Terminal card that plays a
short AI-shell session. Someone types `adrianniel`, the shell "thinks", then
streams the profile back.

Usage, from the repo root:
    python scripts/generate_hero.py

Edit the CONFIG section and re-run whenever your details change.
No third-party packages needed.
"""

import math
from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------- #
# CONFIG
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "hero.svg"

BANNER = "NIEL ADRIAN"
TYPED = "adrianniel"
TERMINAL_URL = "adrianniel.github.io"

FIELDS = [
    ("Name", "Niel Adrian Garig"),
    ("Role", "Full-Stack Developer"),
    ("Location", "Bohol, Philippines"),
    ("Lab", "MAKASA Laboratory"),
    ("Status", "Building iQueue: campus queueing platform"),
    ("Stack", "TypeScript · React · Next.js · React Native · Node.js · NestJS · Prisma · MySQL"),
]

W = 1120

# Palette (Windows Terminal dark, with a neon accent).
WINDOW = "#0c0f1a"
TABBAR = "#141827"
BORDER = "#252b3f"
TEXT = "#e8ecf4"
MUTED = "#7c869e"
CMDLET = "#f9e2af"
KEY = "#3fdc9a"
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
CELL, BLOCK = 12, 10.5

# Timeline (seconds).
T_WELCOME = 0.3
T_TYPE = 1.3
TYPE_STEP = 0.11
T_ENTER = T_TYPE + len(TYPED) * TYPE_STEP + 0.35
THINK = 1.5
T_REPLY = T_ENTER + THINK

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


def show_at(t):
    """Hidden until t, then visible (SMIL, so it works without CSS)."""
    return f'<set attributeName="visibility" to="visible" begin="{t:.2f}s" fill="freeze"/>'


def hide_at(t):
    return f'<set attributeName="visibility" to="hidden" begin="{t:.2f}s" fill="freeze"/>'


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


def star(cx, cy, r):
    """An 8-ray asterisk, the 'thinking' glyph."""
    d = []
    for i in range(4):
        a = math.pi * i / 4
        dx, dy = r * math.cos(a), r * math.sin(a)
        d.append(f"M{cx - dx:.1f} {cy - dy:.1f}L{cx + dx:.1f} {cy + dy:.1f}")
    return "".join(d)


def build():
    pad = 24
    win_x, win_y = pad, pad
    win_w = W - 2 * pad
    tab_h, status_h = 46, 34
    left = win_x + 34
    y = win_y + tab_h + 40
    body = []
    b = body.append

    # ---------- header + welcome box ----------
    b(run(left, y, [("PowerShell 7.5.0 · niel-shell v1.0", MUTED)], fade(0.1)))
    y += 22
    box_h = 62
    box_w = 560
    b(f'<g{fade(T_WELCOME)}>'
      f'<rect x="{left}" y="{y}" width="{box_w}" height="{box_h}" rx="10" fill="{VIOLET}" fill-opacity=".05" '
      f'stroke="{VIOLET}" stroke-opacity=".45"/>'
      + run(left + 18, y + 25, [("✻ ", VIOLET), ("Welcome to ", TEXT), ("Niel Adrian", VIOLET), ("'s terminal.", TEXT)])
      + run(left + 18, y + 48, [("Type ", MUTED), (TYPED, CMDLET), (" to see who I am.", MUTED)])
      + "</g>")
    y += box_h + 38

    # ---------- prompt + typing ----------
    prompt_y = y
    typed_x = left + 2 * CHAR_W
    b(run(left, y, [(">", VIOLET)], fade(T_WELCOME + 0.3)))
    steps = ";".join(f"{i * CHAR_W:.1f}" for i in range(len(TYPED) + 1))
    type_dur = len(TYPED) * TYPE_STEP
    b(f'<clipPath id="typed"><rect x="{typed_x}" y="{y - 20}" height="28" width="0">'
      f'<animate attributeName="width" values="{steps}" begin="{T_TYPE}s" dur="{type_dur:.2f}s" '
      f'calcMode="discrete" fill="freeze"/></rect></clipPath>')
    b(f'<g clip-path="url(#typed)">' + run(typed_x, y, [(TYPED, TEXT)]) + "</g>")
    # Cursor that follows the typing, then disappears on Enter.
    cur_xs = ";".join(f"{typed_x + i * CHAR_W:.1f}" for i in range(len(TYPED) + 1))
    b(f'<rect class="blink" x="{typed_x}" y="{y - 15}" width="9" height="19" fill="{TEXT}" visibility="hidden">'
      f'{show_at(T_WELCOME + 0.3)}'
      f'<animate attributeName="x" values="{cur_xs}" begin="{T_TYPE}s" dur="{type_dur + TYPE_STEP:.2f}s" '
      f'calcMode="discrete" fill="freeze"/>{hide_at(T_ENTER)}</rect>')
    y += LINE_H + 6

    # ---------- thinking ----------
    sx, sy = left + 6, y - 6
    b(f'<g visibility="hidden">{show_at(T_ENTER + 0.05)}{hide_at(T_REPLY)}'
      f'<g><path d="{star(sx, sy, 7)}" stroke="{VIOLET}" stroke-width="2" stroke-linecap="round"/>'
      f'<animateTransform attributeName="transform" type="rotate" from="0 {sx} {sy}" to="360 {sx} {sy}" '
      f'dur="1.2s" repeatCount="indefinite"/></g>'
      f'<text x="{left + 22}" y="{y}" fill="url(#shimmer)">Thinking…</text></g>')

    # ---------- reply ----------
    reply_top = y - 20
    rx = left + 18
    banner_y = y - 12
    rects, banner_w = banner_rects(rx, banner_y)
    b(f'<clipPath id="wipe"><rect x="{rx - 10}" y="{banner_y - 10}" height="{5 * CELL + 30}" width="0">'
      f'<animate attributeName="width" from="0" to="{banner_w + 30}" begin="{T_REPLY}s" dur=".8s" '
      f'calcMode="spline" keySplines=".2 .7 .3 1" fill="freeze"/></rect></clipPath>')
    b('<g clip-path="url(#wipe)">')
    b(f'<g fill="{VIOLET}" fill-opacity=".22">'
      + "".join(f'<rect x="{x + 3:.1f}" y="{yy + 3:.1f}" width="{BLOCK}" height="{BLOCK}" rx="2"/>' for x, yy in rects)
      + "</g>")
    b('<g fill="url(#shine)" filter="url(#glow)">'
      + "".join(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{BLOCK}" height="{BLOCK}" rx="2"/>' for x, yy in rects)
      + "</g></g>")
    tag_x = rx + banner_w + 36
    b(f'<g{fade(T_REPLY + 0.5)}>'
      f'<text x="{tag_x}" y="{banner_y + 22}" font-family="{SANS}" font-size="20" font-weight="600" '
      f'fill="{TEXT}">Full-Stack Developer</text>'
      f'<text x="{tag_x}" y="{banner_y + 48}" font-size="14" fill="{MUTED}">web · mobile · api · data</text></g>')
    y = banner_y + 5 * CELL + LINE_H + 14

    t_fields = T_REPLY + 0.8
    key_w = max(len(k) for k, _ in FIELDS) + 1
    for i, (k, v) in enumerate(FIELDS):
        t = t_fields + i * 0.14
        seg = [(k.ljust(key_w), KEY), (": ", MUTED)]
        if k == "Status":
            dot_x = rx + (key_w + 2) * CHAR_W + 4
            b(f'<g{fade(t)}><circle cx="{dot_x}" cy="{y - 5}" r="4" fill="{KEY}" class="pulse"/>'
              f'<circle cx="{dot_x}" cy="{y - 5}" r="4" fill="{KEY}"/></g>')
            seg.append(("  " + v, TEXT))
        else:
            seg.append((v, TEXT))
        b(run(rx, y, seg, fade(t)))
        y += LINE_H
    reply_bottom = y - LINE_H + 8

    # Gradient rule down the left of the reply, drawn as the answer streams in.
    rule_h = reply_bottom - reply_top
    b(f'<rect x="{left}" y="{reply_top}" width="2" height="0" fill="url(#rule)">'
      f'<animate attributeName="height" from="0" to="{rule_h}" begin="{T_REPLY}s" '
      f'dur="{0.8 + len(FIELDS) * 0.14:.2f}s" fill="freeze"/></rect>')

    # Fresh prompt.
    y += 14
    t_end = t_fields + len(FIELDS) * 0.14 + 0.25
    b(run(left, y, [(">", VIOLET)], fade(t_end)))
    b(f'<g{fade(t_end)}><rect class="blink" x="{typed_x}" y="{y - 15}" width="9" height="19" fill="{TEXT}"/></g>')

    win_h = y + 34 + status_h - win_y
    H = win_y + win_h + pad
    status_y = win_y + win_h - status_h

    # ---------- document ----------
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{MONO}" font-size="{FONT_SIZE}" role="img" '
      f'aria-label="Terminal: typing {TYPED} returns the profile of Niel Adrian Garig, Full-Stack Developer. '
      f'Click to open the interactive terminal.">')
    a("<defs>")
    a(f'<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="{rx}" y1="0" x2="{rx + banner_w}" y2="0">'
      f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/>'
      f'<stop offset="1" stop-color="{PINK}"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{banner_w * 0.35:.0f} 0;0 0" '
      f'dur="6s" repeatCount="indefinite"/></linearGradient>')
    a(f'<linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="{left}" y1="0" x2="{left + 160}" y2="0">'
      f'<stop offset="0" stop-color="{MUTED}"/><stop offset=".5" stop-color="{TEXT}"/>'
      f'<stop offset="1" stop-color="{MUTED}"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" values="-160 0;160 0" '
      f'dur="1.2s" repeatCount="indefinite"/></linearGradient>')
    a(f'<linearGradient id="rule" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}"/>'
      f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient>')
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
      ".cta{animation:nudge 2.4s ease-in-out infinite}"
      "@keyframes nudge{0%,100%{opacity:.75}50%{opacity:1}}"
      "@media (prefers-reduced-motion:reduce){*{animation:none!important}.f{opacity:1}}"
      "</style>")

    # Window frame.
    a(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" rx="12" fill="url(#winBg)" filter="url(#shadow)"/>')
    a('<g clip-path="url(#win)">')
    a(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" fill="url(#aura)"/>')
    a(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{tab_h}" fill="{TABBAR}"/>')
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
    px = tab_x + tab_w + 20
    a(f'<path d="M{px} {iy + 9}h12M{px + 6} {iy + 3}v12" stroke="{MUTED}" stroke-width="1.5" stroke-linecap="round"/>')
    a(f'<path d="M{px + 30} {iy + 7}l5 5 5-5" stroke="{MUTED}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    right = win_x + win_w
    cy = win_y + tab_h / 2
    a(f'<path d="M{right - 150} {cy}h12" stroke="{MUTED}" stroke-width="1.3"/>')
    a(f'<rect x="{right - 100}" y="{cy - 6}" width="12" height="12" rx="2" fill="none" stroke="{MUTED}" stroke-width="1.3"/>')
    a(f'<path d="M{right - 46} {cy - 6}l12 12m0-12l-12 12" stroke="{MUTED}" stroke-width="1.3"/>')
    a(f'<rect x="{win_x}" y="{win_y + tab_h}" width="{win_w}" height="1" fill="{BORDER}"/>')

    a("".join(body))

    # Status bar with the call to action.
    a(f'<rect x="{win_x}" y="{status_y}" width="{win_w}" height="{status_h}" fill="{TABBAR}"/>')
    a(f'<rect x="{win_x}" y="{status_y}" width="{win_w}" height="1" fill="{BORDER}"/>')
    sy = status_y + status_h / 2
    a(f'<circle cx="{win_x + 22}" cy="{sy}" r="3.5" fill="{KEY}" class="pulse"/>'
      f'<circle cx="{win_x + 22}" cy="{sy}" r="3.5" fill="{KEY}"/>'
      f'<text x="{win_x + 34}" y="{sy + 4}" font-size="12" fill="{MUTED}">online</text>')
    a(f'<text x="{right - 20}" y="{sy + 4}" text-anchor="end" font-size="13" class="cta">'
      f'<tspan fill="{CYAN}">▸ Click to open the interactive terminal</tspan>'
      f'<tspan fill="{MUTED}">  ·  {TERMINAL_URL}</tspan></text>')
    a("</g>")
    a(f'<rect x="{win_x + .5}" y="{win_y + .5}" width="{win_w - 1}" height="{win_h - 1}" rx="12" fill="none" stroke="{BORDER}"/>')
    a("</svg>")

    OUTPUT.write_text("".join(o), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({W}x{H}, {OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
