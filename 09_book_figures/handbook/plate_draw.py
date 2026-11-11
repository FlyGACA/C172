"""The drawing of the plates' callouts, in SVG: numbered markers, leaders, arrows, the centre-of-gravity symbol. Shared by
build_plates.py (renders with callouts) and vector_plates.py (figures that are drawings)."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
import sys                                             # noqa: E402
sys.path.insert(0, HERE)
import plates_spec                                     # noqa: E402
SPEC = plates_spec.load()
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


def text(s, x, y, height, fill="#FFFFFF", anchor="middle", halo=None, spacing=0.0):
    """A string as outlines (digits, signs, Greek letters, capitals): no font is needed and no word of either edition is
    in the file. (x, y) is the middle of the line at capital height; anchor is start, middle or end along x."""
    k = height / GLYPHS["cap_height"]
    advances = [(height * 0.38 if c == " " else GLYPHS["glyphs"][c]["advance"] * k) + spacing for c in s]
    total = sum(advances) - spacing
    x0 = x - (total / 2 if anchor == "middle" else total if anchor == "end" else 0.0)
    out, cursor = [], x0
    for c, adv in zip(s, advances):
        if c != " ":
            d = GLYPHS["glyphs"][c]["d"]
            t = f'transform="translate({num(cursor)} {num(y + height / 2)}) scale({k:.5f})"'
            if halo:
                out.append(f'<path d="{d}" {t} fill="{halo}" stroke="{halo}" stroke-width="{num(height * 0.34 / k)}" stroke-linejoin="round"/>')
            out.append(f'<path d="{d}" {t} fill="{fill}"/>')
        cursor += adv
    return "".join(out)


def icon(name, x, y, size=14.0, fill="#1D4ED8"):
    """Small pictograms, drawn in canvas units, centred on (x, y): a fuel drop, an eye (the place to look from)."""
    k = size / 14.0
    if name == "drop":
        d = "M0,-8 C2.6,-3.4 5.4,-0.6 5.4,2.6 A5.4,5.4 0 1 1 -5.4,2.6 C-5.4,-0.6 -2.6,-3.4 0,-8 Z"
        return (f'<g transform="translate({num(x)} {num(y)}) scale({k:.3f})"><path d="{d}" fill="{HALO}" stroke="{HALO}" stroke-width="3.4" stroke-linejoin="round" opacity=".92"/>'
                f'<path d="{d}" fill="{fill}"/><path d="M-2.4,3 A2.8,2.8 0 0 0 0,5.6" fill="none" stroke="#FFFFFF" stroke-width="1.3" stroke-linecap="round" opacity=".85"/></g>')
    if name == "eye":
        d = "M-10,0 C-5,-7 5,-7 10,0 C5,7 -5,7 -10,0 Z"
        return (f'<g transform="translate({num(x)} {num(y)}) scale({k:.3f})"><path d="{d}" fill="{HALO}" stroke="{HALO}" stroke-width="3.4" stroke-linejoin="round" opacity=".95"/>'
                f'<path d="{d}" fill="#FFFFFF" stroke="{colour("ink")}" stroke-width="1.6" stroke-linejoin="round"/><circle r="3.4" fill="{colour("ink")}"/></g>')
    raise ValueError(name)


_UID = [0]


def wedge(x, y, r, a0, a1, fill, opacity=0.34, fade=0.12):
    """A sector of a circle (angles in degrees, clockwise from straight up) filled with a colour that fades toward its rim."""
    _UID[0] += 1
    gid = f"wd{_UID[0]}"
    p0 = (x + r * math.sin(math.radians(a0)), y - r * math.cos(math.radians(a0)))
    p1 = (x + r * math.sin(math.radians(a1)), y - r * math.cos(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'<defs><radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{num(x)}" cy="{num(y)}" r="{num(r)}">'
            f'<stop offset="0" stop-color="{fill}" stop-opacity="{opacity}"/><stop offset="1" stop-color="{fill}" stop-opacity="{num(opacity * fade)}"/></radialGradient></defs>'
            f'<path d="M{num(x)},{num(y)} L{num(p0[0])},{num(p0[1])} A{num(r)},{num(r)} 0 {large} 1 {num(p1[0])},{num(p1[1])} Z" fill="url(#{gid})"/>')


def glowdot(x, y, r, fill, core=None):
    """A light seen from afar: a soft halo and a bright core."""
    _UID[0] += 1
    gid = f"gl{_UID[0]}"
    return (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{fill}" stop-opacity="0.95"/><stop offset="0.35" stop-color="{fill}" stop-opacity="0.45"/>'
            f'<stop offset="1" stop-color="{fill}" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="url(#{gid})"/>'
            f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r * 0.2)}" fill="{core or "#FFFFFF"}"/>')


def along(points, t):
    """The point and the direction (unit vector) at the fraction t of the length of a polyline."""
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])]
    target = max(0.0, min(1.0, t)) * sum(lengths)
    for (a, b), n in zip(zip(points, points[1:]), lengths):
        if target <= n or n == lengths[-1]:
            f = 0.0 if n == 0 else min(1.0, target / n)
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), ((b[0] - a[0]) / (n or 1), (b[1] - a[1]) / (n or 1))
        target -= n
    a, b = points[-2], points[-1]
    n = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    return b, ((b[0] - a[0]) / n, (b[1] - a[1]) / n)


def curve(points, fill, width=2.4, dash=None, arrow=None, head=None, halo=True, marks=()):
    """A polyline through points (canvas units), as a stroke with a white under-stroke, and an arrowhead at its end
    (arrow="end"), its start ("start") or both ("both"); the head follows the direction of the last segments."""
    d = "M" + " L".join(f"{num(x)},{num(y)}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    out = []
    if halo:
        out.append(f'<path d="{d}" fill="none" stroke="{HALO}" stroke-width="{num(width + 2.6)}" stroke-linecap="round" stroke-linejoin="round" opacity=".9"{dash_attr}/>')
    out.append(f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{num(width)}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}/>')
    hl = head or width * 3.6
    hw = width * 1.9

    def tip(tail, tip_pt):
        dx, dy = tip_pt[0] - tail[0], tip_pt[1] - tail[1]
        n = math.hypot(dx, dy) or 1.0
        ux, uy = dx / n, dy / n
        bx, by = tip_pt[0] - ux * hl, tip_pt[1] - uy * hl
        pts = f"{num(tip_pt[0])},{num(tip_pt[1])} {num(bx - uy * hw)},{num(by + ux * hw)} {num(bx + uy * hw)},{num(by - ux * hw)}"
        return (f'<polygon points="{pts}" fill="{HALO}" stroke="{HALO}" stroke-width="3.2" stroke-linejoin="round" opacity=".92"/>'
                f'<polygon points="{pts}" fill="{fill}"/>')
    for t in marks:                                         # arrowheads along the line, at these fractions of its length
        (px, py), (ux, uy) = along(points, t)
        tail = (px - ux * 2.0, py - uy * 2.0)
        out.append(tip(tail, (px + ux * hl * 0.5, py + uy * hl * 0.5)))
    if arrow in ("end", "both") and len(points) >= 2:
        out.append(tip(points[max(0, len(points) - 4)], points[-1]))
    if arrow in ("start", "both") and len(points) >= 2:
        out.append(tip(points[min(len(points) - 1, 3)], points[0]))
    return "".join(out)


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
            + (glyph(str(n), x, y, r * 0.98) if n < 10 else text(str(n), x, y, r * 0.78, "#FFFFFF", "middle", spacing=-r * 0.03)))


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
