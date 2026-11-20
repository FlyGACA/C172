"""The marks of the figures, in one style (the third design pass, after the owner's review of Figure 31-1): the labels that carry a figure's digits and codes, and
its plain arrows. A figure's own pill() and arrow() call these, so that every figure draws its labels and arrows the same way.

    chip(cx, cy, text, accent)   a label written straight on the figure: the number large, its unit small; in its colour with a white halo, or (dark=True, on a
                                 night scene or a panel) white with a dark halo and a dot of its colour; kind= a small sign before it (up, down, clock, route)
    arrow(x0, y0, x1, y1, col)   a straight arrow: a dark halo under it, a slim head along its line
    flight(p0, c, p1, col)       a path in the air: a smooth curve from p0 to p1 bent towards c, the same halo and head

The figures and the labels' text are drawn with the book's glyphs (figs/h_b2.glyph_text): no font is needed to render them."""
import math
import re

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


UNIT = re.compile(r"^([<>+\-]?\d[\d .,]*)\s([A-Z°%/]{1,6})$")


def deepen(colour, k=0.18):
    """The colour a little darker: figures written in it on a pale ground read as well as ink."""
    c = colour.lstrip("#")
    if len(c) != 6:
        return colour
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#{:02X}{:02X}{:02X}".format(*(round(v * (1 - k)) for v in (r, g, b)))


def chip(cx, cy, text, accent, size=7.8, kind=None, anchor="middle", min_w=None, light=False, height=None, dark=False):
    """A label written straight on the figure, as on a good map (the fourth design pass, after the owner's review of the boxed labels): no box; the number
    large, its unit smaller after it; on a pale or bright ground the figures in the label's colour with a white halo round them, so that they read across
    lines, bars and pictures; on a dark ground (dark=True: night, a panel) white figures with a soft dark halo and a dot of the label's colour before them,
    which keeps a figure's colour key. kind= draws a small sign before the figures. The old arguments of the boxed label (light, min_w, height) are accepted
    and have no effect."""
    m = UNIT.match(text)
    num, unit = (m.group(1).strip(), m.group(2)) if m else (text, "")
    if size < 7.5:                                         # a small label in a chart: the figures a little larger, the unit nearly as large, to stay legible in print
        big, small = size * 1.28, size * 0.98
    else:
        big, small = size * 1.08, size * 0.76
    wn = width(num, big)
    wu = width(unit, small, 0.6) if unit else 0.0
    gap = size * 0.32 if unit else 0.0
    sign = size * 1.25 if kind else 0.0
    dot = size * 0.95 if dark and not kind else 0.0
    w = sign + dot + wn + gap + wu
    x0 = cx - w / 2 if anchor == "middle" else cx if anchor == "start" else cx - w
    if dark:
        ink, unit_ink, halo, halo_op = "#FFFFFF", "#E2E8F0", "#08101F", 0.62
    else:
        ink = deepen(accent) if tint(accent) != "#CBD5E1" else "#1E293B"
        unit_ink, halo, halo_op = ink, "#FFFFFF", 0.96
    hw = size * 0.55                                       # the halo: wide enough to part the figures from what is under them
    out = ""
    x = x0
    if kind:
        col = tint(accent, 0.15) if dark else deepen(accent)
        out += f'<circle cx="{n(x + sign * 0.42)}" cy="{n(cy)}" r="{n(size * 0.62)}" fill="{halo}" fill-opacity="{n(halo_op * 0.9)}"/>' + icon(kind, x + sign * 0.42, cy, col, size / 7.8)
        x += sign
    if dot:
        out += (f'<circle cx="{n(x + dot * 0.38)}" cy="{n(cy)}" r="{n(size * 0.34)}" fill="{halo}" fill-opacity="{n(halo_op)}"/>'
                f'<circle cx="{n(x + dot * 0.38)}" cy="{n(cy)}" r="{n(size * 0.24)}" fill="{tint(accent, 0.1)}"/>')
        x += dot
    def write(t, xx, hgt, colour, sp):
        return (H.glyph_text(t, xx, cy, hgt, halo, stroke=halo, stroke_width=hw, spacing=sp, anchor="start", opacity=halo_op)
                + H.glyph_text(t, xx, cy, hgt, colour, stroke=colour, stroke_width=hgt * 0.05, spacing=sp, anchor="start"))
    out += write(num, x, big, ink, 0.4)
    if unit:
        out += H.glyph_text(unit, x + wn + gap, cy + (big - small) / 2, small, halo, stroke=halo, stroke_width=hw * 0.85, spacing=0.6, anchor="start", opacity=halo_op)
        out += H.glyph_text(unit, x + wn + gap, cy + (big - small) / 2, small, unit_ink, spacing=0.6, anchor="start", opacity=0.85)
    return out


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
