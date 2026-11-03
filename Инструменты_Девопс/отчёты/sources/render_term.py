#!/usr/bin/env python3
"""Render UTF-8 command capture logs as dark terminal-style PNGs."""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
]
BG = (12, 12, 12)
FG = (200, 200, 200)
CMD = (80, 250, 123)  # green prompt line
DIM = (140, 140, 140)
PAD = 18
LINE_H = 18
MAX_COLS = 100
MAX_LINES = 48


def load_font(size=14):
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap_line(s: str, cols: int) -> list[str]:
    if len(s) <= cols:
        return [s]
    out = []
    while s:
        out.append(s[:cols])
        s = s[cols:]
    return out


def render(text: str, out_path: Path, title_cmd: str | None = None):
    font = load_font(14)
    lines: list[tuple[str, tuple]] = []
    if title_cmd:
        for part in wrap_line(f"$ {title_cmd}", MAX_COLS):
            lines.append((part, CMD))
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    for ln in raw.split("\n"):
        # strip trailing spaces
        ln = ln.rstrip("\n")
        # expand tabs
        ln = ln.expandtabs(4)
        wrapped = wrap_line(ln, MAX_COLS) or [""]
        for w in wrapped:
            lines.append((w, FG))
    if len(lines) > MAX_LINES:
        lines = lines[: MAX_LINES - 1] + [("… (truncated)", DIM)]
    if not lines:
        lines = [("(no output)", DIM)]

    # measure
    tmp = Image.new("RGB", (10, 10))
    dr = ImageDraw.Draw(tmp)
    max_w = 0
    for t, _ in lines:
        bbox = dr.textbbox((0, 0), t if t else " ", font=font)
        max_w = max(max_w, bbox[2] - bbox[0])
    width = max(max_w + 2 * PAD, 640)
    height = PAD * 2 + LINE_H * len(lines) + 8
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    y = PAD
    for t, color in lines:
        draw.text((PAD, y), t, font=font, fill=color)
        y += LINE_H
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    print(f"wrote {out_path} ({width}x{height})")


def main():
    # args: out.png [--cmd "command"] [logfile or - for stdin]
    args = sys.argv[1:]
    if len(args) < 1:
        print("usage: render_term.py out.png [--cmd CMD] [file|-]", file=sys.stderr)
        sys.exit(2)
    out = Path(args[0])
    cmd = None
    rest = args[1:]
    if rest and rest[0] == "--cmd":
        cmd = rest[1]
        rest = rest[2:]
    src = rest[0] if rest else "-"
    if src == "-":
        text = sys.stdin.read()
    else:
        text = Path(src).read_text(encoding="utf-8", errors="replace")
    render(text, out, cmd)


if __name__ == "__main__":
    main()
