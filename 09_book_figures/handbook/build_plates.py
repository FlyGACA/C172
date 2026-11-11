#!/usr/bin/env python3
"""Put together the handbook's plates: a render of the 3D twin (renders/<id>.png, made by blender/render_plate.py)
laid on the figure's background, with the numbered callouts, arrows and leaders drawn over it as vector.

    python3 09_book_figures/handbook/build_plates.py [id ...]          then   node 09_book_figures/handbook/rasterize.mjs

Writes, for each plate in plates.json:
    out/<id>.svg            the figure, under the file name of the one it replaces in the book (the render is embedded
                            as a JPEG, the callouts are vector, the digits are outlines: it looks the same everywhere)
    out/preview/<id>.jpg    the same, flattened (rasterize.mjs), for review and for a plate-NN-NN-name.jpg if the book wants one
Needs Pillow only.
"""
import base64
import io
import json
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plate_draw import SPEC, GLYPHS, arrow, centre_of_gravity, marker, leader, tee, num, colour   # noqa: E402

PX_PER_UNIT = 3                  # the embedded picture: 3 px to a unit of the canvas (1920 px across the book's 640)
JPEG_QUALITY = 90


# ---------------------------------------------------------------------------------------------- background and picture
def background(spec, size):
    w, h = size
    if spec["type"] == "flat":
        return Image.new("RGB", size, tuple(spec["colour"]))
    top, bottom = spec["top"], spec["bottom"]
    column = Image.new("RGB", (1, h))
    column.putdata([tuple(round(top[c] + (bottom[c] - top[c]) * (y / max(1, h - 1)) ** 0.9) for c in range(3)) for y in range(h)])
    return column.resize((w, h), Image.NEAREST)


def scale(plate):
    return plate.get("px_per_unit", PX_PER_UNIT)


def picture(plate):
    """The render on the background, as JPEG bytes."""
    cw, ch = plate["canvas"]
    size = (round(cw * scale(plate)), round(ch * scale(plate)))
    source = os.path.join(HERE, plate["source"]["image"]) if "source" in plate else os.path.join(HERE, "renders", plate["id"] + ".png")
    render = Image.open(source).convert("RGBA").resize(size, Image.LANCZOS)
    base = background(SPEC["backgrounds"][plate["background"]], size).convert("RGBA")
    base.alpha_composite(render)
    buf = io.BytesIO()
    base.convert("RGB").save(buf, "JPEG", quality=JPEG_QUALITY, subsampling=0, optimize=True, progressive=True)
    return buf.getvalue()


def load_anchors(plate):
    """name -> (u, v), fractions of the picture from its top left."""
    if "source" in plate:          # a picture made by the illustration pipeline (blender/render_figure.py): anchors in pixels
        if "anchors" not in plate["source"]:
            return {}
        with open(os.path.join(HERE, plate["source"]["anchors"]), encoding="utf-8") as f:
            data = json.load(f)
        return {k: [v["x"] / data["width"], v["y"] / data["height"]] for k, v in data["anchors"].items()}
    with open(os.path.join(HERE, "renders", plate["id"] + ".anchors.json"), encoding="utf-8") as f:
        return json.load(f)["anchors"]


def overlays(plate, anchors):
    cw, ch = plate["canvas"]
    pts = {name: (u * cw, v * ch) for name, (u, v) in anchors.items()}
    out = []
    late = []                                    # markers go over everything
    for o in plate.get("overlays", []):
        kind = o["type"]
        if kind == "arrow":
            out.append(arrow(pts[o["from"]], pts[o["to"]], colour(o["colour"]), o.get("width", 3.4), o.get("head")))
        elif kind == "cg":
            p = pts[o["at"]]; out.append(centre_of_gravity(p[0], p[1], o.get("r", 8.5)))
        elif kind == "tee":
            out.append(tee([pts[n] for n in o["points"]], tuple(o["lead"]) if "lead" in o else None))
        elif kind == "marker":
            target = pts[o["at"]]
            if "pos" in o:
                m = tuple(o["pos"])
            elif "polar" in o:
                centre, ang, rad = o["polar"]
                a = math.radians(ang)
                m = (pts[centre][0] + rad * math.sin(a), pts[centre][1] - rad * math.cos(a))
            else:
                dx, dy = o.get("offset", [0, 0]); m = (target[0] + dx, target[1] + dy)
            if o.get("leader", "polar" in o):
                late.append(leader(m, target, gap=o.get("gap", 0.0)))
            late.append(marker(o["n"], m[0], m[1]))
        else:
            raise ValueError(f"{plate['id']}: unknown overlay {kind!r}")
    return "".join(out + late)


def svg(plate, jpeg, anchors):
    cw, ch = plate["canvas"]
    b64 = base64.b64encode(jpeg).decode("ascii")
    title = plate["caption"].split(". ", 1)[-1].rstrip(".")
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}" data-px-per-unit="{scale(plate)}">',
        f"  <title>{title}</title>",
        f"  <desc>{plate['desc']}</desc>",
        f'  <image width="{cw}" height="{ch}" preserveAspectRatio="none" href="data:image/jpeg;base64,{b64}" xlink:href="data:image/jpeg;base64,{b64}"/>',
        f'  <g id="callouts">{overlays(plate, anchors)}</g>',
        "</svg>", ""])


def main():
    wanted = sys.argv[1:]
    os.makedirs(os.path.join(HERE, "out", "preview"), exist_ok=True)
    for plate in SPEC["plates"]:
        if wanted and plate["id"] not in wanted:
            continue
        if "render" in plate or "source" in plate:
            anchors = load_anchors(plate)
            text = svg(plate, picture(plate), anchors)
        else:
            from vector_plates import draw          # figures that are drawings, not renders
            text = draw(plate, GLYPHS, SPEC)
        path = os.path.join(HERE, "out", plate["id"] + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, os.path.dirname(HERE)), f"({len(text) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
