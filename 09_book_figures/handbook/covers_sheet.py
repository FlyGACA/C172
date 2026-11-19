"""A sheet of the cover proposals: each picture under the book's own cover page (covers_post.py mock), numbered.

    python3 covers_sheet.py [ar|en]     out/covers/<name>-mock-<lang>.jpg -> out/covers/cover-proposals-<lang>.jpg"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["cover-remake", "cover-cockpit", "cover-touchdown", "cover-sunrise", "cover-blueprint", "cover-topdown"]


def main(lang="ar"):
    tiles = []
    for n in ORDER:
        p = os.path.join(HERE, "out", "covers", f"{n}-mock-{lang}.jpg")
        if os.path.exists(p):
            tiles.append((n, Image.open(p).convert("RGB")))
    tw, th, pad = 900, int(900 * 2122 / 1500), 28
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * th + (rows + 1) * pad), "#060C1A")
    d = ImageDraw.Draw(sheet)
    from covers_blueprint import font as book_font
    font = book_font(44, "SpaceGrotesk-600-ext")
    for i, (n, im) in enumerate(tiles):
        x, y = pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.ellipse([x + 18, y + 18, x + 92, y + 92], fill="#E9BC60")
        d.text((x + 55, y + 55), str(i + 1), font=font, fill="#060C1A", anchor="mm")
    out = os.path.join(HERE, "out", "covers", f"cover-proposals-{lang}.jpg")
    sheet.save(out, quality=88)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ar")
