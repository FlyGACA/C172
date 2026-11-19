"""Give the book's flat vector figures (charts, flowcharts, tables: the SVGs that stay drawings) the look of its richer ones: the numbered callouts get the white ring
and the soft shadow of the plates' callouts, the boxes and diamonds of the flowcharts get a soft vertical gradient of their own colour and a drop shadow (dashed placeholder boxes are left flat). Nothing is moved, added or removed, and no number or colour key changes: the drawing is the same, only its finish.

    python3 restyle_flat_svgs.py <book>/handbook/ppl/figures [name.svg ...]

Works on the SVGs that have no <filter> yet (the richer ones are left alone), and is safe to run again (a file already restyled carries the marker id "rs-csh").
Keeps to the book's rules for an SVG (tools/handbook/render.py): presentation attributes only, no style, no script, no image, under 40 KB."""
import colorsys
import os
import re
import sys

DARK = {"#1f2937", "#1d4ed8", "#047857", "#b45309", "#b91c1c", "#6b7280", "#111827", "#374151", "#7c3aed", "#0f766e", "#1e40af"}


def attr(tag, name):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def light(colour):
    c = colour.lstrip("#")
    if len(c) != 6:
        return None
    r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)


def shade(colour, k):
    c = colour.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    if k >= 0:
        r, g, b = (round(v + (255 - v) * k) for v in (r, g, b))
    else:
        r, g, b = (round(v * (1 + k)) for v in (r, g, b))
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def restyle(svg):
    if "<filter" in svg or "rs-csh" in svg:
        return svg, 0
    grads, changed = {}, 0

    def grad_id(colour):
        colour = colour.lower()
        if colour not in grads:
            grads[colour] = f"rs-g{len(grads)}"
        return grads[colour]

    def callout(m):
        nonlocal changed
        tag = m.group(0)
        r, fill = attr(tag, "r"), (attr(tag, "fill") or "").lower()
        if r is None or fill not in DARK or attr(tag, "stroke") or attr(tag, "opacity") or attr(tag, "fill-opacity"):
            return tag
        if not 8.5 <= float(r) <= 12.5:
            return tag
        changed += 1
        return tag[:-2] + ' stroke="#ffffff" stroke-width="1.5" filter="url(#rs-csh)"/>'

    def box(m):
        nonlocal changed
        tag = m.group(0)
        fill, rx = (attr(tag, "fill") or "").lower(), attr(tag, "rx")
        w, h = float(attr(tag, "width") or 0), float(attr(tag, "height") or 0)
        hls = light(fill) if fill.startswith("#") else None
        if not rx or float(rx) < 2 or hls is None or hls[1] < 0.86 or w < 36 or h < 16 or attr(tag, "fill-opacity") or attr(tag, "opacity") or attr(tag, "filter") or attr(tag, "stroke-dasharray"):
            return tag
        if w > 420 and h > 220:                             # a page-sized panel: a gradient, no shadow
            changed += 1
            return tag.replace(f'fill="{attr(tag, "fill")}"', f'fill="url(#{grad_id(fill)})"')
        changed += 1
        return tag.replace(f'fill="{attr(tag, "fill")}"', f'fill="url(#{grad_id(fill)})" filter="url(#rs-sh)"')

    def diamond(m):
        nonlocal changed
        tag = m.group(0)
        fill = (attr(tag, "fill") or "").lower()
        hls = light(fill) if fill.startswith("#") else None
        pts = (attr(tag, "points") or "").replace(",", " ").split()
        if hls is None or hls[1] < 0.86 or not attr(tag, "stroke") or len(pts) != 8 or attr(tag, "fill-opacity") or attr(tag, "opacity") or attr(tag, "filter"):
            return tag
        xs, ys = [float(v) for v in pts[0::2]], [float(v) for v in pts[1::2]]
        if max(xs) - min(xs) < 30 or max(ys) - min(ys) < 20:
            return tag
        changed += 1
        return tag.replace(f'fill="{attr(tag, "fill")}"', f'fill="url(#{grad_id(fill)})" filter="url(#rs-sh)"')

    out = re.sub(r"<circle\b[^>]*/>", callout, svg)
    out = re.sub(r"<rect\b[^>]*/>", box, out)
    out = re.sub(r"<polygon\b[^>]*/>", diamond, out)
    if not changed:
        return svg, 0
    defs = ('<defs><filter id="rs-csh" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1" stdDeviation="1.6" flood-color="#10233f" flood-opacity="0.28"/></filter>'
            '<filter id="rs-sh" x="-6%" y="-10%" width="112%" height="130%"><feDropShadow dx="0" dy="1.6" stdDeviation="2" flood-color="#10233f" flood-opacity="0.16"/></filter>')
    for colour, gid in grads.items():
        top = shade(colour, 0.45) if colour != "#ffffff" else "#ffffff"
        bottom = shade(colour, -0.045) if colour != "#ffffff" else "#f1f5f9"
        defs += f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>'
    defs += "</defs>"
    out = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + defs, out, count=1)
    return out, changed


def main():
    folder = sys.argv[1]
    names = sys.argv[2:] or sorted(f for f in os.listdir(folder) if f.endswith(".svg"))
    for name in names:
        path = os.path.join(folder, name)
        svg = open(path, encoding="utf-8").read()
        out, changed = restyle(svg)
        if changed:
            assert len(out.encode()) < 40 * 1024, name
            open(path, "w", encoding="utf-8").write(out)
        print(f"{name}: {changed} marks" if changed else f"{name}: left as it is")


main()
