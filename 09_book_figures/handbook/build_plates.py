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

from PIL import Image, ImageChops, ImageDraw, ImageFilter

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
    dotted lines ({"type": "dots", "from", "to", "step", "r", "colour", "opacity"}), the ground ({"type": "band", "at": anchor, "colour", "colour2"}) and a
    soft shadow on it ({"type": "contact", "at": anchor, "rx", "ry", "opacity", "blur"}). A sector drawn over the picture (the "wedge"
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
        if g["type"] == "band":                                                    # the ground: from the anchor's line down to the bottom of the canvas, a gradient
            _x, y = pts[g["at"]] if "at" in g else (0, g["y"])
            top, bottom = g["colour"], g.get("colour2", g["colour"])
            y0 = round(y * k)
            band = Image.new("RGBA", base.size, (0, 0, 0, 0))
            for row in range(y0, base.size[1]):
                t = (row - y0) / max(1, base.size[1] - y0)
                ImageDraw.Draw(band).line([(0, row), (base.size[0], row)], fill=tuple(round(top[c] + (bottom[c] - top[c]) * t) for c in range(3)) + (round(255 * g.get("opacity", 1.0)),))
            base.alpha_composite(band)
            continue
        if g["type"] == "contact":                                                 # a soft flat shadow under an aeroplane standing on the ground
            x, y = pts[g["at"]] if "at" in g else g["pos"]
            layer = Image.new("L", base.size, 0)
            ImageDraw.Draw(layer).ellipse([(x - g["rx"]) * k, (y - g["ry"]) * k, (x + g["rx"]) * k, (y + g["ry"]) * k], fill=round(255 * g.get("opacity", 0.35)))
            layer = layer.filter(ImageFilter.GaussianBlur(g.get("blur", 6) * k))
            dark = Image.new("RGBA", base.size, (20, 24, 34, 0)); dark.putalpha(layer)
            base.alpha_composite(dark)
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
        k = scale(plate)
        for (name, path, _anchors, box), layer in zip(layers_of(plate), plate["layers"]):
            x, y, w, h = box
            piece = Image.open(path).convert("RGBA").resize((round(w * k), round(h * k)), Image.LANCZOS)
            if layer.get("round"):                       # rounded corners (canvas units): a picture in a frame
                big = Image.new("L", (piece.width * 2, piece.height * 2), 0)
                ImageDraw.Draw(big).rounded_rectangle([0, 0, big.width - 1, big.height - 1], radius=layer["round"] * k * 2, fill=255)
                piece.putalpha(ImageChops.multiply(piece.split()[3], big.resize(piece.size, Image.LANCZOS)))
            shadow = layer.get("shadow")
            if shadow:                                   # a soft shadow under the picture, so that it stands off the page (the box needs room for it)
                blurred = piece.split()[3].filter(ImageFilter.GaussianBlur(shadow.get("blur", 6) * k)).point(lambda v: round(v * shadow.get("opacity", 0.32)))
                dark = Image.new("RGBA", piece.size, (0, 0, 0, 0)); dark.putalpha(blurred)
                under = Image.new("RGBA", size, (0, 0, 0, 0))
                under.paste(dark, (round((x + shadow.get("dx", 0)) * k), round((y + shadow.get("dy", 3)) * k)))
                base.alpha_composite(under)
            sheet = Image.new("RGBA", size, (0, 0, 0, 0))
            sheet.paste(piece, (round(x * k), round(y * k)))
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


SPRITES = {}


def sprite_source(name):
    """A sprite cropped to the aeroplane in it: its width is then the wingspan (from above, ahead, behind) or the length (from the side)."""
    if name not in SPRITES:
        image = Image.open(os.path.join(HERE, "renders", name + ".png")).convert("RGBA")
        SPRITES[name] = image.crop(image.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    return SPRITES[name]


def sprite_image(o):
    """An overlay {"type": "sprite", "name": "sprite-top", "at": [x, y] or an anchor, "width": canvas units across the aeroplane, "angle": degrees clockwise,
    "tint": "#RRGGBB" (with "tint_strength"), "outline": {"width", "colour", "opacity"}, "shadow": {"dx", "dy", "blur", "opacity"}, "opacity"}: the
    aeroplane of figs/sprites.py as a picture, with its middle on the point. Returns (picture, its size in canvas units)."""
    k = o.get("px", 4.0)                                      # pixels to a canvas unit in the file (the plate itself is flattened at 3)
    source = sprite_source(o["name"])
    width = o["width"]
    image = source.resize((max(2, round(width * k)), max(2, round(width * k * source.height / source.width))), Image.LANCZOS)
    if o.get("tint"):                                         # a coat of another colour over the paint: other traffic, the aeroplane in question
        rgb = tuple(int(o["tint"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        r, g, b, a = image.split()
        base = Image.merge("RGB", (r, g, b))
        mixed = Image.blend(base, ImageChops.multiply(base, Image.new("RGB", image.size, rgb)), o.get("tint_strength", 0.5))
        image = Image.merge("RGBA", (*mixed.split(), a))
    ol, sh = o.get("outline"), o.get("shadow")
    pad = round(((ol["width"] if ol else 0) + (sh["blur"] * 3 + abs(sh.get("dx", 0)) + abs(sh.get("dy", 0)) if sh else 0) + 1) * k)
    canvas = Image.new("RGBA", (image.width + 2 * pad, image.height + 2 * pad), (0, 0, 0, 0))
    canvas.alpha_composite(image, (pad, pad))
    image = canvas
    if o.get("angle"):
        image = image.rotate(-o["angle"], resample=Image.BICUBIC, expand=True)
    layers = []
    if sh:
        dark = Image.new("RGBA", image.size, (0, 0, 0, 0))
        dark.putalpha(image.split()[3].filter(ImageFilter.GaussianBlur(sh["blur"] * k)).point(lambda v: round(v * sh.get("opacity", 0.3))))
        shifted = Image.new("RGBA", image.size, (0, 0, 0, 0)); shifted.alpha_composite(dark, (round(sh.get("dx", 2) * k), round(sh.get("dy", 3) * k)))
        layers.append(shifted)
    if ol:
        size = 2 * max(1, round(ol["width"] * k)) + 1
        edge = Image.new("RGBA", image.size, tuple(int(ol["colour"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (0,))
        edge.putalpha(image.split()[3].filter(ImageFilter.MaxFilter(size)).point(lambda v: round(v * ol.get("opacity", 0.85))))
        layers.append(edge)
    layers.append(image)
    out = layers[0]
    for layer in layers[1:]:
        out = Image.alpha_composite(out, layer)
    if o.get("opacity", 1.0) < 1.0:
        out.putalpha(out.split()[3].point(lambda v: round(v * o["opacity"])))
    return out, k


def sprite_markup(o, x, y):
    image, k = sprite_image(o)
    buf = io.BytesIO(); image.save(buf, "PNG", compress_level=6)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    w, h = image.width / k, image.height / k
    return f'<image x="{num(x - w / 2)}" y="{num(y - h / 2)}" width="{num(w)}" height="{num(h)}" preserveAspectRatio="none" href="data:image/png;base64,{b64}" xlink:href="data:image/png;base64,{b64}"/>'


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
            out.append(arrow(where(o["from"]), where(o["to"]), colour(o["colour"]), o.get("width", 3.4), o.get("head")))
        elif kind == "pair":                                 # two parallel arrows between two points, one each way (out and back); gap: [at the start, at the end]
            a, b = where(o["from"]), where(o["to"])
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            g0, g1 = o.get("gap", [0, 0]); off = o.get("offset", 5.0)
            p0, p1 = (a[0] + ux * g0, a[1] + uy * g0), (b[0] - ux * g1, b[1] - uy * g1)
            nx, ny = -uy * off, ux * off
            fill = colour(o["colour"])
            out.append(arrow((p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), fill, o.get("width", 3.0), o.get("head")))
            out.append(arrow((p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny), fill, o.get("width", 3.0), o.get("head")))
        elif kind == "sprite":                               # the aeroplane from figs/sprites.py, centred on a point of the canvas
            x, y = where(o["at"] if "at" in o else o["pos"])
            out.append(sprite_markup(o, x, y))
        elif kind == "polygon":                              # a filled shape through anchors and canvas points (a cover, a plug, a streamer)
            points = " ".join(f"{num(x)},{num(y)}" for x, y in (where(q) for q in o["points"]))
            edge = f' stroke="{colour(o.get("stroke", "#FFFFFF"))}" stroke-width="{o.get("width", 1.6)}" stroke-linejoin="round"' if o.get("stroke", "#FFFFFF") else ""
            out.append(f'<polygon points="{points}" fill="{colour(o["fill"])}" opacity="{o.get("opacity", 1.0)}"{edge}/>')
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
    if "reskin" in plate:
        return all(os.path.exists(os.path.join(HERE, "renders", sprite["id"] + ".png")) for sprite in SPEC["sprites"])
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
        if "reskin" in plate:                       # an old figure with the model's aeroplane in it (reskin.py): only the flat picture is made
            from reskin import reskin
            with open(os.path.join(HERE, "cache", "flat-src", plate["id"] + ".svg"), "w", encoding="utf-8") as f:
                f.write(reskin(plate, sprite_markup, lambda name: sprite_source(name).height / sprite_source(name).width))
            print("reskinned", plate["id"])
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
