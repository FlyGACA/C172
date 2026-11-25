#!/usr/bin/env python3
"""Pack the pictures and models that render_all.py made into the parts catalogue.

    python3 09_book_figures/parts/build.py --renders DIR

Reads DIR/alone, DIR/place and DIR/models and writes, beside this file: t/ (small pictures), l/ (the part on
its own), p/ (the part in the aircraft), m/ (one model per system) and parts.json, which the page reads.
Pictures are packed many to a sheet so the page asks for a few hundred files, not several thousand.
Needs Pillow. Nothing here is typed by hand: names, systems and sources come from the model's own records.
"""
import argparse
import glob
import json
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
# name, source folder, tile width, tile height, columns, tiles per sheet, WebP quality
SHEETS = (("thumb", "t", "alone", 240, 150, 10, 100, 78), ("large", "l", "alone", 1920, 1200, 2, 6, 82), ("place", "p", "place", 1200, 750, 3, 12, 82))


def on_paper(path, size):
    picture = Image.open(path).convert("RGBA")
    paper = Image.new("RGBA", picture.size, (255, 255, 255, 255))
    paper.alpha_composite(picture)
    return paper.convert("RGB").resize(size, Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--renders", required=True)
    args = parser.parse_args()
    parts = []
    for path in sorted(glob.glob(os.path.join(args.renders, "alone", "*.json"))):
        with open(path, encoding="utf-8") as stream:
            record = json.load(stream)
        first, rest = record["parts"][0], record["parts"][1:]
        parts.append({"k": os.path.splitext(record["picture"])[0], "s": first["system"], "id": first["id"], "en": first["label_en"], "ar": first["label_ar"],
                      "st": first["status"], "more": [[p["id"], p["label_en"], p["label_ar"]] for p in rest]})
    parts.sort(key=lambda p: (p["s"], p["k"]))
    missing = [f"{folder}/{p['k']}.png" for folder in ("alone", "place") for p in parts if not os.path.exists(os.path.join(args.renders, folder, p["k"] + ".png"))]
    systems = sorted({p["s"] for p in parts})
    missing += [f"models/{s}.glb" for s in systems if not os.path.exists(os.path.join(args.renders, "models", s + ".glb"))]
    if missing or not parts:
        print(f"parts: {len(missing)} file(s) missing from {args.renders}, e.g. {missing[:5]}", file=sys.stderr)
        return 1
    catalogue = {}
    for name, folder, source, width, height, columns, per, quality in SHEETS:
        shutil.rmtree(os.path.join(HERE, folder), ignore_errors=True)
        os.makedirs(os.path.join(HERE, folder))
        files = []
        for start in range(0, len(parts), per):
            chunk = parts[start:start + per]
            rows = -(-len(chunk) // columns)
            sheet = Image.new("RGB", (width * columns, height * rows), (255, 255, 255))
            for n, part in enumerate(chunk):
                sheet.paste(on_paper(os.path.join(args.renders, source, part["k"] + ".png"), (width, height)), ((n % columns) * width, (n // columns) * height))
            file = f"{folder}/{start // per:03d}.webp"
            sheet.save(os.path.join(HERE, file), quality=quality, method=4)
            files.append({"f": file, "rows": rows})
        catalogue[name] = {"cols": columns, "per": per, "files": files}
    shutil.rmtree(os.path.join(HERE, "m"), ignore_errors=True)
    os.makedirs(os.path.join(HERE, "m"))
    for system in systems:
        shutil.copyfile(os.path.join(args.renders, "models", system + ".glb"), os.path.join(HERE, "m", system + ".glb"))
    catalogue["parts"] = parts
    with open(os.path.join(HERE, "parts.json"), "w", encoding="utf-8") as stream:
        json.dump(catalogue, stream, ensure_ascii=False, separators=(",", ":"))
        stream.write("\n")
    print(f"parts: {len(parts)} parts in {len(systems)} systems written to {os.path.relpath(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
