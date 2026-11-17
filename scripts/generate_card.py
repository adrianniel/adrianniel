"""Generate the terminal-style profile card (dark + light) with an ASCII portrait.

Usage, from the repo root:
    pip install pillow
    python scripts/generate_card.py

Writes assets/card-dark.svg and assets/card-light.svg. Edit the CONFIG section
and re-run whenever your details change.
"""

from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance, ImageOps

# --------------------------------------------------------------------------- #
# CONFIG
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent
PORTRAIT = ROOT / "assets" / "portrait.png"  # transparent background works best
OUT_DIR = ROOT / "assets"

USER, HOST, CWD = "niel", "bohol", "~/adrianniel"
COMMAND = "fastfetch"

# Sections of the info panel: (title, [(key, value), ...]).
# A title of None draws no divider (used for the first block).
SECTIONS = [
    (None, [
        ("name", "Niel Adrian Garig"),
        ("role", "Full-Stack Developer"),
        ("based", "Bohol, Philippines"),
        ("lab", "MAKASA Laboratory"),
    ]),
    ("stack", [
        ("lang", "TypeScript · JavaScript · SQL"),
        ("web", "React · Next.js · Tailwind CSS"),
        ("mobile", "Expo · React Native"),
        ("api", "Node.js · Express · NestJS"),
        ("data", "Prisma · MySQL · MariaDB"),
    ]),
    ("now", [
        ("building", "iQueue: campus queueing"),
        ("learning", "real-time & mobile UX"),
    ]),
]

# Portrait width in characters; height follows the photo's shape.
COLS = 50
CROP_BOX = None  # (left, top, right, bottom) in pixels, or None for all

THEMES = {
    "dark": dict(
        window="#0d1117", bar="#161b22", border="#30363d",
        fg="#e6edf3", muted="#7d8590", faint="#30363d",
        user="#7ee787", path="#79c0ff", key="#d2a8ff",
        lift=60, scale=0.8,  # brighten photo colours for a dark background
    ),
    "light": dict(
        window="#ffffff", bar="#f6f8fa", border="#d0d7de",
        fg="#1f2328", muted="#656d76", faint="#d8dee4",
        user="#1a7f37", path="#0969da", key="#8250df",
        lift=0, scale=0.72,  # darken photo colours for a light background
    ),
}
DOTS = ["#ff5f57", "#febc2e", "#28c840"]
SWATCHES = ["#ff7b72", "#ffa657", "#e3b341", "#7ee787", "#79c0ff", "#d2a8ff", "#f778ba"]

FONT = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"
FONT_SIZE, CHAR_W, LINE_H = 24, 14.4, 30
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# --------------------------------------------------------------------------- #


def load_portrait():
    """Return rows of (char, (r, g, b)) cells; None colour means empty."""
    img = Image.open(PORTRAIT).convert("RGBA")
    if CROP_BOX:
        img = img.crop(CROP_BOX)
    w, h = img.size
    rows_n = round(COLS * (h / w) * (CHAR_W / LINE_H))
    small = img.resize((COLS, rows_n), Image.LANCZOS)
    rgb = ImageEnhance.Contrast(small.convert("RGB")).enhance(1.2)
    gray = ImageOps.grayscale(rgb)

    rows = []
    for y in range(rows_n):
        row = []
        for x in range(COLS):
            if small.getpixel((x, y))[3] < 110:
                row.append((" ", None))
                continue
            lum = gray.getpixel((x, y)) / 255
            # Dark areas (hair, eyes, frames) get dense glyphs.
            ch = RAMP[min(len(RAMP) - 1, int((1 - lum) * 0.75 * len(RAMP)) + 6)]
            row.append((ch, rgb.getpixel((x, y))))
        rows.append(row)
    return rows


def run(x0, y, segments, cls=""):
    """One line of text. Every character gets an explicit x so columns stay
    aligned whichever monospace font the viewer has."""
    spans, col = [], 0
    for text, colour, bold in segments:
        if text.strip():
            xs = " ".join(f"{x0 + (col + k) * CHAR_W:.1f}" for k in range(len(text)))
            weight = ' font-weight="600"' if bold else ""
            spans.append(f'<tspan x="{xs}" fill="{colour}"{weight}>{escape(text)}</tspan>')
        col += len(text)
    c = f' class="{cls}"' if cls else ""
    return f'<text y="{y}"{c} xml:space="preserve">{"".join(spans)}</text>'


def render(theme_name, art):
    t = THEMES[theme_name]
    pad, bar_h = 16, 52
    art_x = pad + 48
    info_x = art_x + COLS * CHAR_W + 72
    key_w = max(len(k) for _, items in SECTIONS for k, _ in items) + 3
    info_chars = max(key_w + len(v) for _, items in SECTIONS for _, v in items)
    rule_chars = info_chars

    info_lines = 2 + sum(len(items) + (2 if title else 0) for title, items in SECTIONS) + 2
    body_rows = max(len(art), info_lines)

    width = round(info_x + info_chars * CHAR_W + 64)
    prompt_y = pad + bar_h + 56
    body_y = prompt_y + 60
    end_y = body_y + body_rows * LINE_H + 18
    height = end_y + 40

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="{FONT_SIZE}">',
        "<style>"
        ".r{opacity:0;animation:in .5s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
        ".cur{animation:blink 1.1s steps(1) infinite}"
        "@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.r{animation:none;opacity:1}.cur{animation:none}}"
        "</style>",
        # Window.
        f'<rect x="{pad}" y="{pad}" width="{width - 2 * pad}" height="{height - 2 * pad}" '
        f'rx="14" fill="{t["window"]}" stroke="{t["border"]}"/>',
        f'<path d="M{pad} {pad + bar_h}V{pad + 14}a14 14 0 0 1 14-14H{width - pad - 14}'
        f'a14 14 0 0 1 14 14V{pad + bar_h}Z" fill="{t["bar"]}"/>',
        f'<rect x="{pad}" y="{pad + bar_h}" width="{width - 2 * pad}" height="1" fill="{t["border"]}"/>',
    ]
    for i, c in enumerate(DOTS):
        out.append(f'<circle cx="{pad + 26 + i * 22}" cy="{pad + bar_h / 2}" r="6.5" fill="{c}"/>')
    out.append(
        f'<text x="{width / 2}" y="{pad + bar_h / 2}" text-anchor="middle" dominant-baseline="central" '
        f'font-size="19" fill="{t["muted"]}">{USER}@{HOST}: {escape(CWD)}</text>'
    )

    def prompt(y, cmd=""):
        return run(art_x, y, [
            (f"{USER}@{HOST}", t["user"], True), (":", t["muted"], False),
            (CWD, t["path"], True), ("$ ", t["muted"], False), (cmd, t["fg"], False),
        ])

    out.append(prompt(prompt_y, COMMAND))

    # Portrait, revealed row by row.
    art_top = body_y + max(0, info_lines - len(art)) // 2 * LINE_H
    for r, row in enumerate(art):
        spans = []
        for c, (ch, rgb) in enumerate(row):
            if rgb is None:
                continue
            col = "#%02x%02x%02x" % tuple(min(255, int(v * t["scale"] + t["lift"])) for v in rgb)
            spans.append(f'<tspan x="{art_x + c * CHAR_W:.1f}" fill="{col}">{escape(ch)}</tspan>')
        if spans:
            out.append(
                f'<text y="{art_top + r * LINE_H}" class="r" style="animation-delay:{0.15 + r * 0.035:.2f}s" '
                f'xml:space="preserve">{"".join(spans)}</text>'
            )

    # Info panel, vertically centred next to the portrait.
    y = body_y + max(0, len(art) - info_lines) // 2 * LINE_H
    lines = [run(info_x, y, [(USER, t["user"], True), ("@", t["muted"], False), (HOST, t["user"], True)])]
    y += LINE_H
    lines.append(run(info_x, y, [("─" * rule_chars, t["faint"], False)]))
    for title, items in SECTIONS:
        if title:
            y += LINE_H * 2
            lines.append(run(info_x, y, [(f"{title} ", t["muted"], False),
                                         ("─" * (rule_chars - len(title) - 1), t["faint"], False)]))
        for key, value in items:
            y += LINE_H
            lines.append(run(info_x, y, [(key.ljust(key_w), t["key"], False), (value, t["fg"], False)]))
    for i, line in enumerate(lines):
        out.append(line.replace("<text ", f'<text class="r" style="animation-delay:{0.5 + i * 0.06:.2f}s" ', 1))

    # Colour swatches.
    y += LINE_H + 8
    delay = 0.5 + len(lines) * 0.06
    for i, c in enumerate(SWATCHES):
        out.append(f'<rect class="r" style="animation-delay:{delay:.2f}s" x="{info_x + i * 40}" '
                   f'y="{y}" width="30" height="16" rx="8" fill="{c}"/>')

    # Fresh prompt with a blinking cursor.
    out.append(prompt(end_y))
    cursor_x = art_x + (len(f"{USER}@{HOST}:{CWD}$ ")) * CHAR_W
    out.append(f'<rect class="cur" x="{cursor_x:.1f}" y="{end_y - 20}" width="12" height="26" '
               f'rx="2" fill="{t["fg"]}"/>')

    out.append("</svg>")
    path = OUT_DIR / f"card-{theme_name}.svg"
    path.write_text("".join(out), encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({width}x{height})")


if __name__ == "__main__":
    portrait = load_portrait()
    for name in THEMES:
        render(name, portrait)
