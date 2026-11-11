#!/usr/bin/env python3
"""Put together the handbook's plates: a render of the 3D twin (renders/<id>.png, made by blender/render_plate.py)
laid on the figure's background, with the numbered callouts, arrows and leaders drawn over it as vector.

    python3 09_book_figures/handbook/build_plates.py [id ...]          then   node 09_book_figures/handbook/rasterize.mjs

Writes, for each plate in plates.json:
    out/<id>.svg            the figure, under the file name of the one it replaces in the book (the render is embedded
                            as a JPEG, the callouts are vector, the digits are outlines: it looks the same everywhere).
                            The book does not take an SVG with a picture in it (book_plates.py makes its JPEG)
    cache/flat-src/<id>.svg the same with the picture embedded lossless, for rasterize.mjs (not kept)
Needs Pillow only.
"""
import base64
import io
import json
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plate_draw import SPEC, GLYPHS, along, arrow, centre_of_gravity, curve, glowdot, icon, marker, leader, outline, tee, text, wedge, num, colour   # noqa: E402

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


def ground(base, plate, anchors):
    """What lies under the aircraft, drawn into the background before the render goes on: "ground" lists sectors of light
    ({"type": "wedge", "at": anchor or "pos": [x, y], "r", "from", "to" (degrees clockwise from straight up), "colour", "opacity", "fade"})
    and dotted lines ({"type": "dots", "from", "to", "step", "r", "colour", "opacity"}). A sector drawn over the picture (the "wedge"
    overlay) would dull the aircraft.""" 
    cw, ch = plate["canvas"]
    k = scale(plate)
    pts = {name: (u * cw, v * ch) for name, (u, v) in (anchors or {}).items()}
    for g in plate.get("ground", []):
        if g["type"] == "dots":                                                   # a dotted line: [x, y] to [x, y], dots r across, step apart (canvas units)
            (xa, ya), (xb, yb) = g["from"], g["to"]
            n = max(1, int(math.hypot(xb - xa, yb - ya) / g.get("step", 5.5)))
            rgb = tuple(int(g["colour"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
            big = Image.new("RGBA", (base.size[0] * 2, base.size[1] * 2), rgb + (0,))
            pen, rr = ImageDraw.Draw(big), g.get("r", 0.6) * k * 2
            for i in range(n + 1):
                px, py = (xa + (xb - xa) * i / n) * k * 2, (ya + (yb - ya) * i / n) * k * 2
                pen.ellipse([px - rr, py - rr, px + rr, py + rr], fill=rgb + (round(255 * g.get("opacity", 0.4)),))
            base.alpha_composite(big.resize(base.size, Image.LANCZOS))
            continue
        if g["type"] != "wedge":
            raise ValueError(f"{plate['id']}: unknown ground item {g['type']!r}")
        x, y = pts[g["at"]] if "at" in g else g["pos"]
        r = g["r"] * k
        cx, cy = x * k, y * k
        a0, a1 = math.radians(g["from"]), math.radians(g["to"])
        n = max(8, int(abs(g["to"] - g["from"])))
        ring = [(cx + r * math.sin(a0 + (a1 - a0) * i / n), cy - r * math.cos(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
        size = base.size
        big = Image.new("L", (size[0] * 2, size[1] * 2), 0)                     # drawn at twice the size so the edges are clean
        ImageDraw.Draw(big).polygon([(cx * 2, cy * 2)] + [(px * 2, py * 2) for px, py in ring], fill=255)
        mask = big.resize(size, Image.LANCZOS)
        radius = max(2, round(r))
        ramp = Image.new("L", size, 255)                                          # 0 at the centre, 255 at the rim and beyond
        ramp.paste(Image.radial_gradient("L").resize((2 * radius, 2 * radius), Image.BILINEAR), (round(cx) - radius, round(cy) - radius))
        opacity, fade = g.get("opacity", 0.34), g.get("fade", 0.12)
        ramp = ramp.point(lambda v: round(255 * opacity * (1 - (1 - fade) * v / 255)))
        colour = g["colour"].lstrip("#")
        layer = Image.new("RGBA", size, tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4)) + (0,))
        layer.putalpha(ImageChops.multiply(mask, ramp))
        base.alpha_composite(layer)


def picture(plate, lossless=False, anchors=None):
    """The render on the background, as JPEG bytes (or PNG bytes, for the flat copy the book's JPEG is made from)."""
    cw, ch = plate["canvas"]
    size = (round(cw * scale(plate)), round(ch * scale(plate)))
    base = background(SPEC["backgrounds"][plate["background"]], size).convert("RGBA")
    ground(base, plate, anchors)
    if "layers" in plate:                         # several pictures, each in a box of the canvas (canvas units)
        for name, path, _anchors, box in layers_of(plate):
            x, y, w, h = box
            piece = Image.open(path).convert("RGBA").resize((round(w * scale(plate)), round(h * scale(plate))), Image.LANCZOS)
            sheet = Image.new("RGBA", size, (0, 0, 0, 0))
            sheet.paste(piece, (round(x * scale(plate)), round(y * scale(plate))))
            base.alpha_composite(sheet)
    else:
        source = os.path.join(HERE, plate["source"]["image"]) if "source" in plate else os.path.join(HERE, "renders", plate["id"] + ".png")
        base.alpha_composite(Image.open(source).convert("RGBA").resize(size, Image.LANCZOS))
    buf = io.BytesIO()
    if lossless:
        base.convert("RGB").save(buf, "PNG", compress_level=6)
    else:
        base.convert("RGB").save(buf, "JPEG", quality=JPEG_QUALITY, subsampling=0, optimize=True, progressive=True)
    return buf.getvalue()


def layers_of(plate):
    """The pictures of a composite plate: [(name, png path, anchors path, box)], the box in canvas units."""
    out = []
    for layer in plate["layers"]:
        stem = os.path.join(HERE, "renders", f"{plate['id']}__{layer['name']}")
        out.append((layer["name"], os.path.join(HERE, layer["source"]) if "source" in layer else stem + ".png", stem + ".anchors.json", layer["box"]))
    return out


def load_geometry(plate):
    """(anchors, curves): name -> (u, v) and name -> [(u, v), ...], fractions of the whole canvas from its top left. A composite
    plate's layers are named layer.anchor."""
    if "layers" in plate:
        cw, ch = plate["canvas"]
        anchors, curves = {}, {}
        for name, _png, path, (x, y, w, h) in layers_of(plate):
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for k, (u, v) in data.get("anchors", {}).items():
                anchors[f"{name}.{k}"] = [(x + u * w) / cw, (y + v * h) / ch]
            for k, pts in data.get("curves", {}).items():
                curves[f"{name}.{k}"] = [[(x + u * w) / cw, (y + v * h) / ch] for u, v in pts]
        return anchors, curves
    if "source" in plate:          # a picture made by the illustration pipeline (blender/render_figure.py): anchors in pixels
        if "anchors" not in plate["source"]:
            return {}, {}
        with open(os.path.join(HERE, plate["source"]["anchors"]), encoding="utf-8") as f:
            data = json.load(f)
        return {k: [v["x"] / data["width"], v["y"] / data["height"]] for k, v in data["anchors"].items()}, {}
    with open(os.path.join(HERE, "renders", plate["id"] + ".anchors.json"), encoding="utf-8") as f:
        data = json.load(f)
    return data["anchors"], data.get("curves", {})


def load_anchors(plate):
    return load_geometry(plate)[0]


def overlays(plate, anchors, curves=None):
    cw, ch = plate["canvas"]
    pts = {name: (u * cw, v * ch) for name, (u, v) in anchors.items()}
    paths = {name: [(u * cw, v * ch) for u, v in pl] for name, pl in (curves or {}).items()}

    def where(p):                                  # an anchor name, or a point of the canvas
        return pts[p] if isinstance(p, str) else (p[0], p[1])
    out = []
    late = []                                    # markers go over everything
    for o in plate.get("overlays", []):
        kind = o["type"]
        if kind == "arrow":
            out.append(arrow(pts[o["from"]], pts[o["to"]], colour(o["colour"]), o.get("width", 3.4), o.get("head")))
        elif kind == "cg":
            p = pts[o["at"]]; out.append(centre_of_gravity(p[0], p[1], o.get("r", 8.5)))
        elif kind == "path":                                 # a 3D curve of the recipe, projected: an axis, a turning arrow, a track
            out.append(curve(paths[o["curve"]], colour(o.get("colour", "ink")), o.get("width", 2.4), o.get("dash"), o.get("arrow"), o.get("head"), o.get("halo", True), o.get("marks", ())))
        elif kind == "line":                                 # a polyline through anchors and canvas points
            out.append(curve([where(q) for q in o["points"]], colour(o.get("colour", "ink")), o.get("width", 2.4), o.get("dash"), o.get("arrow"), o.get("head"), o.get("halo", True)))
        elif kind == "text":                                 # digits, signs, Greek letters and capitals as outlines
            x, y = where(o["at"] if "at" in o else o["pos"])
            dx, dy = o.get("offset", [0, 0])
            out.append(text(o["s"], x + dx, y + dy, o.get("size", 12), colour(o.get("colour", "ink")), o.get("anchor", "middle"), "#FFFFFF" if o.get("halo", True) else None))
        elif kind == "wedge":                                # a sector of light round an anchor
            x, y = where(o["at"])
            out.append(wedge(x, y, o["r"], o["from"], o["to"], colour(o["colour"]), o.get("opacity", 0.34), o.get("fade", 0.12)))
        elif kind == "glowdot":                              # a light seen from afar, at an anchor or a point of the canvas
            x, y = where(o["at"] if "at" in o else o["pos"])
            late.append(glowdot(x, y, o.get("r", 12), colour(o["colour"]), o.get("core")))
        elif kind == "icon":                                 # a pictogram (drop, eye) at an anchor or a point of the canvas
            x, y = where(o["at"] if "at" in o else o["pos"])
            out.append(icon(o["name"], x, y, o.get("size", 14.0), colour(o.get("colour", "#1D4ED8"))))
        elif kind == "svg":                                  # free markup, in canvas units
            out.append(o["markup"])
        elif kind == "outline":
            out.append(outline([tuple(q) for q in o["path"]], o.get("closed", True), o.get("dash", "6 4.5"), o.get("width", 2.4)))
        elif kind == "tee":
            out.append(tee([pts[n] for n in o["points"]], tuple(o["lead"]) if "lead" in o else None))
        elif kind == "marker" and "on" in o:                    # a marker sitting on a curve of the recipe, at a fraction of its length
            x, y = along(paths[o["on"]["curve"]], o["on"]["t"])[0]
            late.append(marker(o["n"], x + o["on"].get("dx", 0), y + o["on"].get("dy", 0), o.get("r", 13.0)))
        elif kind == "marker":
            target = pts[o["at"]] if "at" in o else tuple(o["target"]) if "target" in o else tuple(o["pos"])   # an anchor of the picture, a point of the canvas, or the marker itself
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


def svg(plate, picture_bytes, anchors, mime="image/jpeg", curves=None):
    cw, ch = plate["canvas"]
    b64 = base64.b64encode(picture_bytes).decode("ascii")
    title = plate["caption"].split(". ", 1)[-1].rstrip(".")
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}" data-px-per-unit="{scale(plate)}">',
        f"  <title>{title}</title>",
        f"  <desc>{plate['desc']}</desc>",
        f'  <image width="{cw}" height="{ch}" preserveAspectRatio="none" href="data:{mime};base64,{b64}" xlink:href="data:{mime};base64,{b64}"/>',
        f'  <g id="callouts">{overlays(plate, anchors, curves)}</g>',
        "</svg>", ""])


def has_render(plate):
    """Whether the pictures of a plate are on disk. The raw renders of new plates are not kept in git (they are large): `npm run plates:render` makes them."""
    if "layers" in plate:
        return all(os.path.exists(png) and os.path.exists(anchors) for _n, png, anchors, _b in layers_of(plate))
    if "source" in plate:
        return os.path.exists(os.path.join(HERE, plate["source"]["image"]))
    if "render" in plate:
        return all(os.path.exists(os.path.join(HERE, "renders", plate["id"] + ext)) for ext in (".png", ".anchors.json"))
    return True


def main():
    wanted = sys.argv[1:]
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "cache", "flat-src"), exist_ok=True)
    for plate in SPEC["plates"]:
        if wanted and plate["id"] not in wanted:
            continue
        if not wanted and not has_render(plate):
            print(f"skipped {plate['id']}: no render on disk (npm run plates:render makes it; the finished plate is in out/book)")
            continue
        if "render" in plate or "source" in plate or "layers" in plate:
            anchors, curves = load_geometry(plate)
            text = svg(plate, picture(plate, anchors=anchors), anchors, curves=curves)
            with open(os.path.join(HERE, "cache", "flat-src", plate["id"] + ".svg"), "w", encoding="utf-8") as f:
                f.write(svg(plate, picture(plate, lossless=True, anchors=anchors), anchors, mime="image/png", curves=curves))
        else:
            from vector_plates import draw          # figures that are drawings, not renders
            text = draw(plate, GLYPHS, SPEC)
        path = os.path.join(HERE, "out", plate["id"] + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, os.path.dirname(HERE)), f"({len(text) / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
