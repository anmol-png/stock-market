#!/usr/bin/env python3
"""One-time: generate the Reels PWA icons (dark rounded square, accent gradient, "DI").

Outputs dashboard/reels/icon-{180,192,512}.png. Needs Pillow (`pip install pillow`).
Falls back to a plain accent square if the system font can't be loaded.
"""
from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard" / "reels"

BG = (11, 15, 23)          # --bg
ACCENT = (91, 157, 255)    # --accent
ACCENT2 = (169, 112, 255)  # --technology


def make(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img)
    # subtle diagonal accent gradient band across the lower half
    for y in range(size):
        t = y / size
        if t > 0.55:
            k = (t - 0.55) / 0.45
            col = tuple(int(BG[i] + (ACCENT[i] - BG[i]) * k * 0.35) for i in range(3))
            d.line([(0, y), (size, y)], fill=col)
    # accent bar (the "moot" bar from the card design)
    bar_w = max(6, size // 16)
    d.rounded_rectangle([size * 0.16, size * 0.30, size * 0.16 + bar_w, size * 0.74],
                        radius=bar_w // 2, fill=ACCENT)
    # "DI" monogram
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",
                                  int(size * 0.34), index=1)  # index 1 = bold
        d.text((size * 0.30, size * 0.36), "DI", font=font, fill=(231, 237, 245))
    except OSError:
        d.rounded_rectangle([size * 0.34, size * 0.38, size * 0.72, size * 0.66],
                            radius=size // 20, fill=ACCENT2)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for size in (180, 192, 512):
        make(size).save(OUT / f"icon-{size}.png")
        print(f"wrote {OUT.relative_to(ROOT)}/icon-{size}.png")


if __name__ == "__main__":
    main()
