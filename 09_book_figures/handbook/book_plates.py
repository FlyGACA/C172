#!/usr/bin/env python3
"""The plates in the form the handbook takes them: what to put into handbook/ppl/figures/ of the book repository.

    python3 09_book_figures/handbook/build_plates.py && node 09_book_figures/handbook/rasterize.mjs && python3 09_book_figures/handbook/book_plates.py

The book accepts two kinds of artwork (its docs/handbook.md, Figures): an SVG of at most 40 KB with no picture in it, and a JPEG
colour plate of at most 800 KB, 3,200 px a side, 8-bit RGB, with no metadata. A render cannot be the first, so each plate
that is a render becomes a plate-NN-NN-name.jpg (the picture of cache/flat/, encoded once, as sharp as fits 780 KB), and a
plate that is a drawing stays an SVG. Each plate of plates.json names its file ("book_file"). Writes out/book/<book_file>
and stops if one of them breaks the book's rules (book_rules.py). Needs Pillow only.
"""
import io
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plate_draw import SPEC                                  # noqa: E402
from book_rules import problems_of_jpeg, problems_of_svg    # noqa: E402

OUT = os.path.join(HERE, "out", "book")
TARGET = 780_000                 # the book's limit is 800,000 bytes


def encode(image):
    """The sharpest JPEG that fits: 4:4:4 (thin coloured lines and the callouts keep their edges), 4:2:0 if it must."""
    for subsampling, qualities in ((0, range(94, 79, -2)), (2, range(92, 69, -2))):
        for quality in qualities:
            buf = io.BytesIO()
            image.save(buf, "JPEG", quality=quality, subsampling=subsampling, optimize=True, progressive=True)
            if buf.tell() <= TARGET:
                return buf.getvalue(), f"q{quality} {'4:4:4' if subsampling == 0 else '4:2:0'}"
    raise SystemExit("no quality fits: make the picture smaller")


def main():
    os.makedirs(OUT, exist_ok=True)
    wanted = sys.argv[1:]
    failed = False
    for plate in SPEC["plates"]:
        if wanted and plate["id"] not in wanted:
            continue
        name = plate["book_file"]
        path = os.path.join(OUT, name)
        if name.endswith(".jpg"):
            flat = os.path.join(HERE, "cache", "flat", plate["id"] + ".png")
            if not os.path.exists(flat):
                raise SystemExit(f"{flat} is missing: run build_plates.py and rasterize.mjs first")
            image = Image.open(flat).convert("RGB")
            data, how = encode(image)
            with open(path, "wb") as f:
                f.write(data)
            problems = problems_of_jpeg(name, data)
            note = f"{image.width} x {image.height} px, {how}"
        else:
            with open(os.path.join(HERE, "out", plate["id"] + ".svg"), encoding="utf-8") as f:
                text = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            problems = problems_of_svg(name, text)
            note = "vector"
        print(f"{name}: {os.path.getsize(path) / 1000:.0f} kB ({note})" + ("" if not problems else "  PROBLEMS: " + "; ".join(problems)))
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
