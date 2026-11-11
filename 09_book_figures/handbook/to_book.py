#!/usr/bin/env python3
"""Put the plates of out/book/ into the book repository: copy each file into handbook/ppl/figures/, point the chapters of both
editions at it, and remove the figure it replaces. Run it again after a plate changes: it only touches what differs.

    python3 09_book_figures/handbook/to_book.py /path/to/the/book/checkout

Then, in the book: python3 tools/handbook/build_handbook.py --swap --no-pdf (the PDFs once at the end: they are large), 
python3 tools/handbook/build_review_packet.py, and the checks of its CI."""
import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plate_draw import SPEC      # noqa: E402


def main():
    book = os.path.abspath(sys.argv[1])
    figures = os.path.join(book, "handbook", "ppl", "figures")
    chapters = sorted(glob.glob(os.path.join(book, "handbook", "ppl", "*", "[0-9a]*.md")))
    for plate in SPEC["plates"]:
        name, old = plate["book_file"], plate["replaces"]
        source = os.path.join(HERE, "out", "book", name)
        if not os.path.exists(source):
            continue
        target = os.path.join(figures, name)
        changed = []
        if not os.path.exists(target) or open(target, "rb").read() != open(source, "rb").read():
            shutil.copyfile(source, target)
            changed.append("copied")
        if old != name:
            for path in chapters:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                if f"/handbook/ppl/figures/{old})" in text:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(text.replace(f"/handbook/ppl/figures/{old})", f"/handbook/ppl/figures/{name})"))
                    changed.append(os.path.relpath(path, book))
            if os.path.exists(os.path.join(figures, old)):
                subprocess.run(["git", "-C", book, "rm", "-q", "-f", os.path.join("handbook", "ppl", "figures", old)], check=True)
                changed.append("removed " + old)
        if changed:
            print(f"{name}: " + ", ".join(changed))


main()
