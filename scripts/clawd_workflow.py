"""Generate assets/clawd-workflow.svg: Clawd walking through a dev workflow.

Clawd is decoded from the same quadrant-block characters the Claude Code
terminal uses, so each quadrant becomes one gap-free pixel.
"""
from pathlib import Path

CLAWD_TEXT = [" ▐▛███▜▌", "▝▜█████▛▘", "  ▘▘ ▝▝"]
# quadrant bits: (upper-left, upper-right, lower-left, lower-right)
QUAD = {
    " ": (0, 0, 0, 0), "█": (1, 1, 1, 1), "▐": (0, 1, 0, 1), "▌": (1, 0, 1, 0),
    "▛": (1, 1, 1, 0), "▜": (1, 1, 0, 1), "▝": (0, 1, 0, 0), "▘": (1, 0, 0, 0),
}

ORANGE = "#D77757"
BG = "#262624"
FRAME = "#3a3936"
TEXT = "#ECEAE4"
DIM = "#8C8984"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
CW = 8.4  # monospace char width at 14px


def clawd_pixels():
    px = set()
    for row, line in enumerate(CLAWD_TEXT):
        for col, ch in enumerate(line):
            ul, ur, ll, lr = QUAD[ch]
            for dx, dy, on in ((0, 0, ul), (1, 0, ur), (0, 1, ll), (1, 1, lr)):
                if on:
                    px.add((col * 2 + dx, row * 2 + dy))
    return px


def clawd(x, y, pw, ph):
    """Merge each row's runs into rects so there are no seams between pixels."""
    px = clawd_pixels()
    out = []
    for py in sorted({p[1] for p in px}):
        xs = sorted(p[0] for p in px if p[1] == py)
        start = prev = xs[0]
        for cx in xs[1:] + [None]:
            if cx is not None and cx == prev + 1:
                prev = cx
                continue
            out.append(f'<rect x="{x + start * pw:g}" y="{y + py * ph:g}" '
                       f'width="{(prev - start + 1) * pw:g}" height="{ph:g}"/>')
            if cx is not None:
                start = prev = cx
    return f'<g fill="{ORANGE}">' + "".join(out) + "</g>"


def text(x, y, s, fill=TEXT, size=14, anchor="start", weight="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<text x="{x:g}" y="{y:g}" fill="{fill}" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" xml:space="preserve">{s}</text>')


STATIONS = [
    ("what if..?", [("?", ORANGE, 0)], "DISCUSS", "chat & ideas"),
    ("step 1,2,3", [("☰", "#8AB4F8", 0)], "PLAN", "map the path"),
    ("tap tap!", [], "BUILD", "write code"),
    ("all green", [("✓", "#7EC16E", -1), ("✓", "#7EC16E", 0), ("✓", "#7EC16E", 1)], "VERIFY", "test & check"),
    ("ship it!!", [("✦", "#F5C451", -1), ("✧", "#F5C451", 1)], "DEPLOY", "hello world"),
]

W, H = 960, 432
PITCH = 180
LEFT = 70
PW, PH = 5, 12  # terminal quadrants are more than twice as tall as wide


def build():
    g = []
    # window
    g.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{FRAME}"/>')
    g.append(f'<path d="M0.5 38 H{W - 0.5}" stroke="{FRAME}"/>')
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        g.append(f'<circle cx="{22 + i * 20}" cy="19.5" r="6" fill="{c}"/>')
    g.append(text(W / 2, 24, "✳ Claude Code", DIM, 13, "middle"))

    # welcome header, like the Claude Code start screen
    g.append(clawd(28, 60, 5, 12))
    g.append(text(126, 78, "Ting × Claude", TEXT, 15, weight="bold"))
    g.append(text(126, 99, "a little workflow with Clawd", DIM))
    g.append(text(126, 120, "~/ting", DIM))

    base = 162
    for i, (msg, props, label, cap) in enumerate(STATIONS):
        x = LEFT + i * PITCH
        bx = x - 10
        bw = 118
        g.append(f'<rect x="{bx}" y="{base - 14}" width="{bw}" height="34" rx="6" '
                 f'fill="none" stroke="{DIM}" stroke-width="1.2"/>')
        g.append(text(bx + bw / 2, base + 8, msg, TEXT, 14, "middle"))
        tx = bx + 26
        g.append(f'<path d="M{tx} {base + 20} V{base + 40} Q{tx} {base + 46} {tx + 6} {base + 46} '
                 f'H{tx + 10} V{base + 58}" fill="none" stroke="{DIM}" stroke-width="1.2"/>')

        cy = base + 62 + (-8 if label == "DEPLOY" else 0)  # deploy clawd hops
        g.append(clawd(x, cy, PW, PH))
        for s, color, row in props:
            g.append(text(x + 18 * PW + 6, base + 98 + row * 18, s, color, 15))

        if label == "BUILD":
            hx, hy = x + 18 * PW + 8, base + 80
            g.append(f'<rect x="{hx}" y="{hy}" width="18" height="8" fill="#C9C6BF"/>'
                     f'<rect x="{hx + 7}" y="{hy + 8}" width="4" height="18" fill="#B07A4F"/>')

        if i < len(STATIONS) - 1:
            g.append(text(x + PITCH - 44, base + 98, "─▶", DIM))

        cx = x + 9 * PW
        g.append(text(cx, base + 166, f"{i + 1} {label}", TEXT, 14, "middle", "bold"))
        g.append(text(cx, base + 187, cap, DIM, 13, "middle"))

    # ground: a double line like ═══
    gy = base + 136
    g.append(f'<path d="M{LEFT - 20} {gy} H{LEFT + 4 * PITCH + 120} M{LEFT - 20} {gy + 4} '
             f'H{LEFT + 4 * PITCH + 120}" stroke="{DIM}" stroke-width="1.2"/>')

    # loop back from DEPLOY to DISCUSS
    x0 = LEFT + 9 * PW
    x1 = LEFT + 4 * PITCH + 9 * PW
    ly, top = base + 236, base + 200
    g.append(f'<path d="M{x1} {top} V{ly - 10} Q{x1} {ly} {x1 - 10} {ly} H{x0 + 10} '
             f'Q{x0} {ly} {x0} {ly - 10} V{top + 8}" fill="none" stroke="{DIM}" stroke-width="1.2"/>')
    g.append(f'<path d="M{x0 - 5} {top + 10} L{x0} {top} L{x0 + 5} {top + 10} Z" fill="{DIM}"/>')
    mid = (x0 + x1) / 2
    g.append(f'<rect x="{mid - 150}" y="{ly - 12}" width="300" height="24" fill="{BG}"/>')
    g.append(text(mid, ly + 5, "↺  and again, happily forever  ↺", TEXT, 14, "middle"))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" font-family="{FONT}" shape-rendering="crispEdges">'
            f'<title>Clawd walks through Discuss, Plan, Build, Verify and Deploy, then loops back</title>'
            + "".join(g) + "</svg>\n")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "clawd-workflow.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}")
