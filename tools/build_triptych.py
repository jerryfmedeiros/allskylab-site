#!/usr/bin/env python3
"""Build images/triptych.{png,webp} from three all-sky frames.

Usage:  python3 tools/build_triptych.py <source-dir>

The thermal and mask frames carry a diagonal no-data hatch outside the circular
sky footprint. The hatch is high-frequency and the data is not, so the disc is
found by looking for the smooth region. Where the hatch is too low-contrast for
that to work, the circle is pinned in PANELS.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images"

VISIBLE = "aae6fb10da5339a57a76bbc39feccaa7.jpg"
THERMAL = "bc5e1fca88637e0f6bf8ae6455bbe185.jpg"
MASK = "b38e5f181bbf07fb9112bd026486de68.jpg"

# file, detect disc?, pinned circle (cx, cy, r) or None, shrink
PANELS = [
    (VISIBLE, False, None, 1.0),
    (THERMAL, True, None, 0.99),
    (MASK, True, (524, 510, 412), 0.925),
]

SIZE = 460
GAP = 34


def find_disc(img, blur=6, quiet=0.25):
    """Centre and radius of the smooth circular data region inside a hatched frame."""
    g = img.convert("L")
    hf = np.abs(np.asarray(g, np.float32)
                - np.asarray(g.filter(ImageFilter.GaussianBlur(1.5)), np.float32))
    hf = np.asarray(Image.fromarray(np.clip(hf, 0, 255).astype(np.uint8))
                    .filter(ImageFilter.GaussianBlur(blur)), np.float32)
    norm = (hf - hf.min()) / (hf.max() - hf.min() + 1e-9)

    ys, xs = np.nonzero(norm < quiet)
    w, h = img.size
    if len(xs) < 100:
        return w / 2, h / 2, min(w, h) * 0.47

    # percentiles, not min/max: a few stray quiet pixels out in the hatch would
    # otherwise stretch the extent to the whole frame
    x0, x1 = np.percentile(xs, [1, 99])
    y0, y1 = np.percentile(ys, [1, 99])
    return (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) / 2


def circular_mask(size, supersample=4):
    m = Image.new("L", (size * supersample,) * 2, 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * supersample - 1, size * supersample - 1),
                              fill=255)
    return m.resize((size, size), Image.LANCZOS)


def panel(path, detect, circle, shrink, size=SIZE):
    img = Image.open(path).convert("RGB")
    if circle is not None:
        cx, cy, r = circle
    elif detect:
        cx, cy, r = find_disc(img)
    else:
        w, h = img.size
        cx, cy, r = w / 2, h / 2, min(w, h) / 2
    r *= shrink

    box = tuple(int(round(v)) for v in (cx - r, cy - r, cx + r, cy + r))
    out = img.crop(box).resize((size, size), Image.LANCZOS).convert("RGBA")
    out.putalpha(circular_mask(size))
    return out


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    panels = [panel(src / name, det, circ, shr) for name, det, circ, shr in PANELS]

    width = SIZE * len(panels) + GAP * (len(panels) - 1)
    canvas = Image.new("RGBA", (width, SIZE), (0, 0, 0, 0))
    for i, p in enumerate(panels):
        canvas.paste(p, (i * (SIZE + GAP), 0), p)

    OUT.mkdir(exist_ok=True)
    canvas.save(OUT / "triptych.png", optimize=True)
    canvas.save(OUT / "triptych.webp", quality=88, method=6)

    for name in ("triptych.png", "triptych.webp"):
        print(f"{name:16s} {width}x{SIZE}  {(OUT / name).stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
