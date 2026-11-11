"""The drawing of the plates' callouts, in SVG: numbered markers, leaders, arrows, the centre-of-gravity symbol. Shared by
build_plates.py (renders with callouts) and vector_plates.py (figures that are drawings)."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "plates.json"), encoding="utf-8") as f:
    SPEC = json.load(f)
with open(os.path.join(HERE, "glyphs.json"), encoding="utf-8") as f:
    GLYPHS = json.load(f)
PALETTE = SPEC["palette"]
HALO = "#FFFFFF"


def colour(name):
    return PALETTE.get(name, name)


def num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------------------------- drawing
def glyph(ch, cx, cy, height, fill="#FFFFFF"):
    """A digit (or alpha) as an outline, centred on (cx, cy), `height` units tall (capital height)."""
    g = GLYPHS["glyphs"][ch]
    s = height / GLYPHS["cap_height"]
    tx = cx - g["advance"] * s / 2
    ty = cy + GLYPHS["cap_height"] * s / 2
    return f'<path d="{g["d"]}" transform="translate({num(tx)} {num(ty)}) scale({s:.5f})" fill="{fill}"/>'


def arrow(p0, p1, fill, width, head=None):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    hl = head or width * 3.3
    hw = width * 1.85
    base = (p1[0] - ux * hl, p1[1] - uy * hl)
    pts = [(p0[0] + nx * width / 2, p0[1] + ny * width / 2), (base[0] + nx * width / 2, base[1] + ny * width / 2), (base[0] + nx * hw, base[1] + ny * hw), p1,
           (base[0] - nx * hw, base[1] - ny * hw), (base[0] - nx * width / 2, base[1] - ny * width / 2), (p0[0] - nx * width / 2, p0[1] - ny * width / 2)]
    d = " ".join(f"{num(x)},{num(y)}" for x, y in pts)
    return (f'<polygon points="{d}" fill="{HALO}" stroke="{HALO}" stroke-width="3.4" stroke-linejoin="round" opacity=".92"/>'
            f'<polygon points="{d}" fill="{fill}"/>')


def centre_of_gravity(x, y, r):
    quadrants = (f"M{num(x)},{num(y)} L{num(x - r)},{num(y)} A{num(r)},{num(r)} 0 0 1 {num(x)},{num(y - r)} Z "
                 f"M{num(x)},{num(y)} L{num(x + r)},{num(y)} A{num(r)},{num(r)} 0 0 1 {num(x)},{num(y + r)} Z")
    ink = colour("ink")
    return (f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r + 1.6)}" fill="{HALO}" opacity=".92"/>'
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="#FFFFFF" stroke="{ink}" stroke-width="1.5"/>'
            f'<path d="{quadrants}" fill="{ink}"/>')


def marker(n, x, y, r=13.0):
    return (f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r + 1.7)}" fill="{HALO}" opacity=".95"/>'
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{colour("marker")}"/>'
            + glyph(str(n), x, y, r * 0.98))


def leader(frm, to, r=13.0, gap=0.0):
    """From the edge of a marker at `frm` to the point `to`, with a dot on the point. With a gap it stops that far short of the
    point and has no dot (the point is a symbol of its own, like the centre of gravity)."""
    dx, dy = to[0] - frm[0], to[1] - frm[1]
    d = math.hypot(dx, dy)
    if d < r + 4 + gap:
        return ""
    start = (frm[0] + dx / d * r, frm[1] + dy / d * r)
    end = (to[0] - dx / d * gap, to[1] - dy / d * gap)
    c = colour("marker")
    line = (f'<line x1="{num(start[0])}" y1="{num(start[1])}" x2="{num(end[0])}" y2="{num(end[1])}" stroke="{HALO}" stroke-width="3.6" stroke-linecap="round" opacity=".9"/>'
            f'<line x1="{num(start[0])}" y1="{num(start[1])}" x2="{num(end[0])}" y2="{num(end[1])}" stroke="{c}" stroke-width="1.3" stroke-linecap="round"/>')
    if gap:
        return line
    return line + f'<circle cx="{num(to[0])}" cy="{num(to[1])}" r="3.4" fill="{c}" stroke="{HALO}" stroke-width="1.3"/>'


def outline(points, closed=True, dash="6 4.5", width=2.4):
    """A dashed amber outline round a group of things (the basic T of the six flight instruments), with a dark under-stroke."""
    d = "M" + " L".join(f"{num(x)},{num(y)}" for x, y in points) + (" Z" if closed else "")
    return (f'<path d="{d}" fill="none" stroke="#000000" stroke-width="{num(width + 1.6)}" stroke-linejoin="round" opacity=".28"/>'
            f'<path d="{d}" fill="none" stroke="#FFC233" stroke-width="{num(width)}" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="{dash}"/>')


def tee(points, lead=None):
    """The basic T through the centres of four instruments (airspeed, attitude, altimeter, heading): a dotted line along
    the top row and one down the middle, a dot on each instrument, and a lead from the marker that names it."""
    asi, ai, alt, dg = points
    amber = "#FFC233"
    parts = []
    segments = [(asi, alt), (ai, dg)] + ([(lead, asi)] if lead else [])
    for a, b in segments:
        parts.append(f'<line x1="{num(a[0])}" y1="{num(a[1])}" x2="{num(b[0])}" y2="{num(b[1])}" stroke="#000000" stroke-width="3.6" stroke-linecap="round" opacity=".28"/>')
        parts.append(f'<line x1="{num(a[0])}" y1="{num(a[1])}" x2="{num(b[0])}" y2="{num(b[1])}" stroke="{amber}" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="0.1 5.2"/>')
    for p in points:
        parts.append(f'<circle cx="{num(p[0])}" cy="{num(p[1])}" r="3.2" fill="{amber}" stroke="{HALO}" stroke-width="1.1"/>')
    return "".join(parts)
