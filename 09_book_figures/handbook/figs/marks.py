"""The marks of the figures, in one style (the third design pass, after the owner's review of Figure 31-1): the labels that carry a figure's digits and codes, and
its plain arrows. A figure's own pill() and arrow() call these, so that every figure draws its labels and arrows the same way.

    chip(cx, cy, text, accent)   a label: dark glass, a bar of the accent colour on its left, the figures in a light shade of it (white for an ink label); with kind= a small sign before them (up: a takeoff
                                 or a climb, down: a landing or a descent, clock, route); light=True: a pale label, its border and its figures in the colour, for a pale chart
    arrow(x0, y0, x1, y1, col)   a straight arrow: a dark halo under it, a slim head along its line
    flight(p0, c, p1, col)       a path in the air: a smooth curve from p0 to p1 bent towards c, the same halo and head

The figures and the labels' text are drawn with the book's glyphs (figs/h_b2.glyph_text): no font is needed to render them."""
import math

from figs import h_b2 as H


def n(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def tint(colour, k=0.45):
    """The colour mixed with white (k of white): the accent drawn on the dark glass, light enough to read."""
    c = colour.lstrip("#")
    if len(c) != 6:
        return colour
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    if max(r, g, b) < 90:                                  # a near-black accent (the ink of a figure): a cool grey instead
        return "#CBD5E1"
    return "#{:02X}{:02X}{:02X}".format(*(round(v + (255 - v) * k) for v in (r, g, b)))


def width(text, size, spacing=0.4):
    g = H._GLYPHS
    k = size / g["cap_height"]
    return sum((size * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in text) - spacing


def icon(kind, x, y, col, s=1.0):
    if kind == "up":
        return (f'<path d="M{n(x - 3.6 * s)} {n(y + 3.2 * s)} L{n(x + 3.0 * s)} {n(y - 3.2 * s)}" stroke="{col}" stroke-width="{n(1.7 * s)}" stroke-linecap="round"/>'
                f'<path d="M{n(x + 3.8 * s)} {n(y - 4.0 * s)} l{n(-4.4 * s)} {n(0.6 * s)} l{n(3.8 * s)} {n(3.8 * s)} Z" fill="{col}"/>')
    if kind == "down":
        return (f'<path d="M{n(x - 3.6 * s)} {n(y - 3.2 * s)} L{n(x + 3.0 * s)} {n(y + 3.2 * s)}" stroke="{col}" stroke-width="{n(1.7 * s)}" stroke-linecap="round"/>'
                f'<path d="M{n(x + 3.8 * s)} {n(y + 4.0 * s)} l{n(-4.4 * s)} {n(-0.6 * s)} l{n(3.8 * s)} {n(-3.8 * s)} Z" fill="{col}"/>')
    if kind == "clock":
        return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(3.9 * s)}" fill="none" stroke="{col}" stroke-width="{n(1.4 * s)}"/>'
                f'<path d="M{n(x)} {n(y - 2.3 * s)} V{n(y)} L{n(x + 1.8 * s)} {n(y + 1.1 * s)}" fill="none" stroke="{col}" stroke-width="{n(1.2 * s)}" stroke-linecap="round"/>')
    if kind == "route":
        return (f'<circle cx="{n(x - 3.4 * s)}" cy="{n(y + 2.4 * s)}" r="{n(1.5 * s)}" fill="{col}"/><circle cx="{n(x + 3.4 * s)}" cy="{n(y - 2.4 * s)}" r="{n(1.5 * s)}" fill="{col}"/>'
                f'<path d="M{n(x - 3.4 * s)} {n(y + 2.4 * s)} Q{n(x)} {n(y + 2.4 * s)} {n(x + 3.4 * s)} {n(y - 2.4 * s)}" fill="none" stroke="{col}" stroke-width="{n(1.1 * s)}" stroke-dasharray="1.6 1.4"/>')
    return ""


def chip(cx, cy, text, accent, size=7.8, kind=None, anchor="middle", min_w=None, light=False, height=None):
    """A label. anchor "start" or "end": cx is its left or right end. height: the height of the label (else from the size of its figures)."""
    tw = width(text, size)
    s = size / 7.8
    iw = 11.0 * s if kind else 0.0
    w = max(tw + (10.0 if size < 7.0 else 15.0) * s + iw, min_w or 0.0)
    h = height if height else size + 9.0 * s
    if anchor == "start":
        cx += w / 2
    elif anchor == "end":
        cx -= w / 2
    x0, y0 = cx - w / 2, cy - h / 2
    small = light                                          # a label in a pale chart: pale, its border and its figures in the colour
    bar = tint(accent) if not light else accent
    fill, fill_op = ("#FFFFFF", 0.96) if light else ("#0B1224", 0.86)
    if light:
        ink = accent if (small and tint(accent) != "#CBD5E1") else "#1E293B"
    else:                                                  # the figures in a light shade of the label's colour, so that the colour keys of a figure still read
        ink = "#FFFFFF" if tint(accent) == "#CBD5E1" else tint(accent, 0.30)
    r = min(5.0 * s, h / 2)
    shadow = f'<rect x="{n(x0)}" y="{n(y0 + 1.1 * s)}" width="{n(w)}" height="{n(h)}" rx="{n(r)}" fill="#000814" fill-opacity="0.22"/>'
    body = f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" rx="{n(r)}" fill="{fill}" fill-opacity="{fill_op}" stroke="{bar}" stroke-opacity="{'0.95' if size < 7.0 else '0.6'}" stroke-width="{n((1.1 if size < 7.0 else 0.9) * s)}"/>'
    accent_bar = "" if small else f'<rect x="{n(x0 + 2.2 * s)}" y="{n(y0 + 2.6 * s)}" width="{n(2.6 * s)}" height="{n(h - 5.2 * s)}" rx="{n(1.3 * s)}" fill="{bar}"/>'
    sign = icon(kind, x0 + 12.0 * s, cy, bar, s) if kind else ""
    tx = (cx if size < 7.0 else x0 + 8.5 * s + iw + (w - 8.5 * s - iw - 6.5 * s) / 2)
    if small:
        shadow = f'<rect x="{n(x0)}" y="{n(y0 + 0.8 * s)}" width="{n(w)}" height="{n(h)}" rx="{n(r)}" fill="#000814" fill-opacity="0.10"/>'
    return shadow + body + accent_bar + sign + H.glyph_text(text, tx, cy, size, ink, spacing=0.4)


def _head(x1, y1, ux, uy, col, s):
    bx, by = x1 - ux * s, y1 - uy * s
    return (f'<path d="M{n(x1 + ux * 1.2)} {n(y1 + uy * 1.2)} L{n(bx - uy * s * 0.55)} {n(by + ux * s * 0.55)} L{n(bx + uy * s * 0.55)} {n(by - ux * s * 0.55)} Z" '
            f'fill="{col}" stroke="#0B1224" stroke-opacity="0.4" stroke-width="0.8" stroke-linejoin="round"/>')


def arrow(x0, y0, x1, y1, col, width=2.6, head=None, dash=None, halo=True, **_):
    """A straight arrow from (x0, y0) to (x1, y1)."""
    L = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    s = head if head else max(6.5, width * 2.6)
    ex, ey = x1 - ux * s * 0.7, y1 - uy * s * 0.7          # the line stops inside the head
    da = f' stroke-dasharray="{dash}"' if dash else ""
    out = ""
    if halo:
        out += f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(ex)}" y2="{n(ey)}" stroke="#0B1224" stroke-opacity="0.35" stroke-width="{n(width + 2.6)}" stroke-linecap="round"/>'
    out += f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(ex)}" y2="{n(ey)}" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"{da}/>'
    return out + _head(x1, y1, ux, uy, col, s)


def flight(p0, c, p1, col, dash=False, width=2.2):
    """A path in the air: a smooth curve from p0 to p1 bent towards c."""
    d = f"M{n(p0[0])} {n(p0[1])} Q{n(c[0])} {n(c[1])} {n(p1[0])} {n(p1[1])}"
    L = math.hypot(p1[0] - c[0], p1[1] - c[1]) or 1.0
    ux, uy = (p1[0] - c[0]) / L, (p1[1] - c[1]) / L
    da = ' stroke-dasharray="5 4"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="#0B1224" stroke-opacity="0.45" stroke-width="{n(width + 2.6)}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"{da}/>' + _head(p1[0], p1[1], ux, uy, col, 6.5))
