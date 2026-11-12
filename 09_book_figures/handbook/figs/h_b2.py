"""Helpers of worker b2 for the plan views of real Saudi airspace (figures 17-6 and 17-7): the map frame (an equirectangular projection round a chosen origin, drawn to scale), the
airspace blocks of the AIP as translucent areas with a white casing and a dashed edge (class G green, D blue, C indigo; danger and restricted areas red-orange with a diagonal hatch),
runway bars, visual reporting points, the route as a ribbon with a white casing, small icons (a tower, a loudspeaker, a megaphone, a bell, a tick, a hand-over), a scale bar and a north
arrow, as SVG markup. Plain Python (no Blender, no Pillow). Every id made here starts with the `uid` the figure passes.

The facts are those of data/saudi_airspace.json (AIP AMDT 11/26); nothing is added to them here."""
import json
import math
import os

from figs import scene as S

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
n = S.n
pts = S.pts

with open(os.path.join(HERE, "data", "saudi_airspace.json"), encoding="utf-8") as _f:
    DATA = json.load(_f)
with open(os.path.join(HERE, "glyphs.json"), encoding="utf-8") as _f:
    _GLYPHS = json.load(_f)

INK = "#1F2937"
COL = {"G": "#1F7A4D", "D": "#1E5FB3", "C": "#3B5FC4", "A": "#6B4FB8"}        # the colours of the classes (the same in every figure of the Saudi round)
OPA = {"G": 0.22, "D": 0.20, "C": 0.16, "A": 0.16}
AMBER, RED = "#E8B923", "#C2410C"
ALERT = "#D9820B"                                                              # the alerting service (a deeper amber than the reporting points, so that it reads on sand)
SHADOW = "#2B2418"


# ------------------------------------------------------------------------------------------------------------------ the frame
class Frame:
    """A flat map of a piece of the country: x_nm = (lon - lon0) * 60 * cos(lat0), y_nm = (lat - lat0) * 60 (1 NM = 1852 m), north up; `s` canvas units to a nautical mile; the
    point (lon0, lat0) lies on the canvas at (ox, oy)."""

    def __init__(self, lat0, lon0, s, ox, oy):
        self.lat0, self.lon0, self.s, self.ox, self.oy = lat0, lon0, s, ox, oy
        self.k = 60.0 * math.cos(math.radians(lat0))

    def nm(self, lon, lat):
        """East and north of the origin, in NM."""
        return (lon - self.lon0) * self.k, (lat - self.lat0) * 60.0

    def xy(self, lon, lat):
        e, nn = self.nm(lon, lat)
        return self.ox + e * self.s, self.oy - nn * self.s

    def at(self, e, nn):
        """The canvas point for an offset of (e, nn) NM from the origin."""
        return self.ox + e * self.s, self.oy - nn * self.s

    def ring(self, coords):
        return [self.xy(lo, la) for lo, la in coords]

    def r(self, nm):
        return nm * self.s

    def bearing_point(self, p, deg, nm):
        """The canvas point `nm` NM from canvas point p on the true bearing `deg`."""
        a = math.radians(deg)
        return p[0] + math.sin(a) * nm * self.s, p[1] - math.cos(a) * nm * self.s


def circle(cx, cy, r):
    return {"kind": "circle", "cx": cx, "cy": cy, "r": r}


def poly(points):
    return {"kind": "poly", "pts": list(points)}


def shape_tag(shape, attrs):
    if shape["kind"] == "circle":
        return f'<circle cx="{n(shape["cx"])}" cy="{n(shape["cy"])}" r="{n(shape["r"])}" {attrs}/>'
    return f'<polygon points="{pts(shape["pts"])}" {attrs}/>'


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def along(points, d):
    """The point at distance d (canvas units) along the polyline, and the direction (unit vector) there."""
    for a, b in zip(points, points[1:]):
        seg = dist(a, b)
        if d <= seg or b is points[-1]:
            t = min(1.0, d / seg) if seg else 0.0
            ux, uy = ((b[0] - a[0]) / seg, (b[1] - a[1]) / seg) if seg else (0.0, -1.0)
            return lerp(a, b, t), (ux, uy)
        d -= seg
    return points[-1], (0.0, -1.0)


# ------------------------------------------------------------------------------------------------------------------ text (outlines of Inter Bold: no font is needed)
def glyph_text(s, cx, cy, height, fill="#FFFFFF", rotate=0.0, spacing=0.0, stroke=None, stroke_width=0.0, anchor="middle", opacity=None):
    g = _GLYPHS
    k = height / g["cap_height"]
    advances = [(height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s]
    total = sum(advances) - spacing
    cursor = cx - (total / 2 if anchor == "middle" else total if anchor == "end" else 0.0)
    out = []
    edge = f' stroke="{stroke}" stroke-width="{n(stroke_width / k)}" stroke-linejoin="round"' if stroke else ""
    for c, adv in zip(s, advances):
        if c != " ":
            out.append(f'<path d="{g["glyphs"][c]["d"]}" transform="translate({n(cursor)} {n(cy + height / 2)}) scale({k:.5f})" fill="{fill}"{edge}/>')
        cursor += adv
    op = f' opacity="{n(opacity)}"' if opacity is not None else ""
    turn = f' transform="rotate({n(rotate)} {n(cx)} {n(cy)})"' if rotate else ""
    return f"<g{turn}{op}>" + "".join(out) + "</g>"


def label(s, x, y, height, colour=INK, anchor="middle", spacing=0.5, halo=2.8):
    """Letters in a colour with a white casing round them, to be read on a picture."""
    return (glyph_text(s, x, y, height, "#FFFFFF", stroke="#FFFFFF", stroke_width=halo, spacing=spacing, anchor=anchor, opacity=0.95)
            + glyph_text(s, x, y, height, colour, stroke=colour, stroke_width=height * 0.04, spacing=spacing, anchor=anchor))


# ------------------------------------------------------------------------------------------------------------------ filters, patterns and masks
def defs(uid, w, h):
    """Shadows, a soft blur, the hatch of the danger and restricted areas: put once among a figure's layers."""
    return ("<defs>"
            f'<filter id="{uid}ds" x="-30%" y="-30%" width="170%" height="180%"><feDropShadow dx="0.6" dy="1.2" stdDeviation="0.9" flood-color="{SHADOW}" flood-opacity="0.42"/></filter>'
            f'<filter id="{uid}dl" x="-30%" y="-30%" width="170%" height="180%"><feDropShadow dx="1.0" dy="2.0" stdDeviation="1.5" flood-color="{SHADOW}" flood-opacity="0.38"/></filter>'
            f'<filter id="{uid}warm" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="1.22"/></filter>'
            f'<filter id="{uid}b1" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.3"/></filter>'
            f'<filter id="{uid}b2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.6"/></filter>'
            f'<filter id="{uid}b3" filterUnits="userSpaceOnUse" x="-20" y="-20" width="{n(w + 40)}" height="{n(h + 40)}"><feGaussianBlur stdDeviation="3.2"/></filter>'
            f'<pattern id="{uid}hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="6" height="6" fill="{RED}" fill-opacity="0.07"/><rect width="1.3" height="6" fill="{RED}" fill-opacity="0.6"/></pattern>'
            "</defs>")


def hole_mask(uid, w, h, holes):
    """A mask that shows everything but the circles in `holes` [(cx, cy, r)]."""
    cut = "".join(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#000000"/>' for cx, cy, r in holes)
    return f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="-20" y="-20" width="{n(w + 40)}" height="{n(h + 40)}"><rect x="-20" y="-20" width="{n(w + 40)}" height="{n(h + 40)}" fill="#FFFFFF"/>{cut}</mask>'


def vignette(uid, w, h, strength=0.16):
    """The picture darkens a little towards its edges, as a photograph does: a radial gradient over the whole canvas."""
    return (f'<defs><radialGradient id="{uid}vg" cx="0.5" cy="0.48" r="0.78"><stop offset="0.55" stop-color="#2B2418" stop-opacity="0"/><stop offset="1" stop-color="#2B2418" stop-opacity="{n(strength)}"/></radialGradient></defs>'
            f'<rect x="0" y="0" width="{n(w)}" height="{n(h)}" fill="url(#{uid}vg)"/>')


# ------------------------------------------------------------------------------------------------------------------ airspace blocks
def fill(shape, cls, opacity=None, mask=None):
    """The tint of a block (class G, D or C), optionally with holes cut by a mask."""
    m = f' mask="url(#{mask})"' if mask else ""
    return shape_tag(shape, f'fill="{COL[cls]}" fill-opacity="{n(OPA[cls] if opacity is None else opacity)}"{m}')


def inner_glow(uid, shape, cls, width=9.0, opacity=0.2):
    """A soft band of the class's colour just inside the edge of the block, as light gathers at the rim of a pane of glass."""
    cid = uid + "gc"
    clip = f'<clipPath id="{cid}">' + shape_tag(shape, "") + "</clipPath>"
    ring = shape_tag(shape, f'fill="none" stroke="{COL[cls]}" stroke-width="{n(width)}" stroke-opacity="{n(opacity)}" filter="url(#{uid}b1)"')
    return f'<defs>{clip}</defs><g clip-path="url(#{cid})">{ring}</g>'


def gloss(uid, shape, strength=0.3, mask=None):
    """A soft highlight on the upper left of a block, as on a pane of glass (light falls from the upper left everywhere in the book)."""
    gid = uid + "gl"
    m = f' mask="url(#{mask})"' if mask else ""
    if shape["kind"] == "circle":
        g = (f'<radialGradient id="{gid}" cx="0.3" cy="0.26" r="0.78"><stop offset="0" stop-color="#FFFFFF" stop-opacity="{n(strength)}"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="{n(strength * 0.22)}"/>'
             f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>')
    else:
        g = (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0.6"><stop offset="0" stop-color="#FFFFFF" stop-opacity="{n(strength * 0.7)}"/><stop offset="0.6" stop-color="#FFFFFF" stop-opacity="{n(strength * 0.12)}"/>'
             f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>')
    return f"<defs>{g}</defs>" + shape_tag(shape, f'fill="url(#{gid})"{m}')


def edge(shape, cls, dash="7 4", width=1.6, casing=3.8, mask=None, colour=None, uid=None):
    """The boundary of a block: a white casing (with a soft shadow if `uid` is given), then the dashed line in the class's colour."""
    m = f' mask="url(#{mask})"' if mask else ""
    c = colour or COL[cls]
    sh = f' filter="url(#{uid}dl)"' if uid else ""
    body = (shape_tag(shape, f'fill="none" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="{n(width + casing - 1.6)}" stroke-linejoin="round"{sh}')
            + shape_tag(shape, f'fill="none" stroke="{c}" stroke-width="{n(width)}" stroke-dasharray="{dash}" stroke-linejoin="round"'))
    return f"<g{m}>{body}</g>"


def special_use(uid, shape, label_text=None, label_at=None, label_height=6.0):
    """A danger or a restricted area: a red-orange hatch, a solid edge on a white casing, and (if given) the code of the area in small letters."""
    out = [shape_tag(shape, f'fill="url(#{uid}hatch)"'),
           shape_tag(shape, f'fill="none" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="4.4" stroke-linejoin="round"'),
           shape_tag(shape, f'fill="none" stroke="{RED}" stroke-width="1.7" stroke-linejoin="round"')]
    if label_text:
        out.append(label(label_text, label_at[0], label_at[1], label_height, RED, spacing=0.4, halo=2.6))
    return "".join(out)


def class_disc(uid, x, y, letter, r=8.0):
    """A small disc in the colour of the class with its letter (G, D or C)."""
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{COL[letter]}" stroke="#FFFFFF" stroke-width="1.6" filter="url(#{uid}ds)"/>'
            + glyph_text(letter, x, y, r * 1.08, "#FFFFFF", stroke="#FFFFFF", stroke_width=0.25))


# ------------------------------------------------------------------------------------------------------------------ places
def runway(uid, p0, p1, width=2.6):
    """A runway bar between its two thresholds: a white casing, a dark bar (a lighter line down its middle)."""
    (x0, y0), (x1, y1) = p0, p1
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="{n(width + 3.2)}" stroke-linecap="butt" filter="url(#{uid}ds)"/>'
            f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#2B3340" stroke-width="{n(width)}" stroke-linecap="butt"/>'
            f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.4" stroke-dasharray="2.4 2.4"/>')


def vrp(uid, x, y, size=11.0):
    """A visual reporting point: an amber triangle with a white outline."""
    h = size
    w = size * 1.06
    p = [(x, y - h * 0.62), (x + w * 0.5, y + h * 0.38), (x - w * 0.5, y + h * 0.38)]
    return (f'<polygon points="{pts(p)}" fill="{AMBER}" stroke="#FFFFFF" stroke-width="1.7" stroke-linejoin="round" filter="url(#{uid}ds)"/>'
            f'<polygon points="{pts(p)}" fill="none" stroke="#8A6A00" stroke-opacity="0.55" stroke-width="0.5" stroke-linejoin="round"/>')


# ------------------------------------------------------------------------------------------------------------------ the route
def route(uid, points, width=5.0, heads=True, chevrons=34.0, colour=INK, head_len=None, marks=None, mid_heads=()):
    """The route as a ribbon: a white casing, a dark body with a lit edge, small white chevrons along it and an arrowhead at the end. `points` is the polyline (canvas units)."""
    hl = head_len or width * 2.1
    # the body stops where the head begins
    end = points[-1]
    ux, uy = (lambda a, b: ((b[0] - a[0]) / dist(a, b), (b[1] - a[1]) / dist(a, b)))(points[-2], points[-1])
    base = (end[0] - ux * hl * 0.8, end[1] - uy * hl * 0.8)
    body = list(points[:-1]) + [base]
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in body)
    out = [f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.96" stroke-width="{n(width + 3.6)}" stroke-linecap="round" stroke-linejoin="round" filter="url(#{uid}dl)"/>',
           f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{n(width)}" stroke-linecap="round" stroke-linejoin="round"/>',
           f'<path d="{d}" fill="none" stroke="#6B7788" stroke-opacity="0.75" stroke-width="{n(width * 0.16)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(-{n(width * 0.2)} -{n(width * 0.2)})"/>']
    if heads:
        nx, ny = -uy, ux
        wing = width * 1.35
        tri = [end, (end[0] - ux * hl + nx * wing, end[1] - uy * hl + ny * wing), (end[0] - ux * hl * 0.78, end[1] - uy * hl * 0.78), (end[0] - ux * hl - nx * wing, end[1] - uy * hl - ny * wing)]
        out.append(f'<polygon points="{pts(tri)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.8" stroke-linejoin="round" paint-order="stroke"/>')
    if chevrons or marks:
        total = sum(dist(a, b) for a, b in zip(points, points[1:]))
        spots = list(marks) if marks else []
        pos = chevrons * 0.6 if (chevrons and not marks) else total + 1
        while pos < total - hl * 1.8:
            spots.append(pos)
            pos += chevrons
        for pos in spots:
            (cx, cy), (dx, dy) = along(points, pos)
            nx, ny = -dy, dx
            s = width * 0.36
            a = (cx - dx * s * 1.1 + nx * s * 1.05, cy - dy * s * 1.1 + ny * s * 1.05)
            b = (cx + dx * s * 0.9, cy + dy * s * 0.9)
            c = (cx - dx * s * 1.1 - nx * s * 1.05, cy - dy * s * 1.1 - ny * s * 1.05)
            out.append(f'<polyline points="{pts([a, b, c])}" fill="none" stroke="#FFFFFF" stroke-width="{n(width * 0.2)}" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.92"/>')
    for pos in mid_heads:                                    # small arrowheads on the ribbon, wider than it, to say which way the flight goes
        (cx, cy), (dx, dy) = along(points, pos)
        nx, ny = -dy, dx
        ln, wd = width * 1.5, width * 1.0
        tri = [(cx + dx * ln * 0.55, cy + dy * ln * 0.55), (cx - dx * ln * 0.45 + nx * wd, cy - dy * ln * 0.45 + ny * wd), (cx - dx * ln * 0.2, cy - dy * ln * 0.2), (cx - dx * ln * 0.45 - nx * wd, cy - dy * ln * 0.45 - ny * wd)]
        out.append(f'<polygon points="{pts(tri)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.5" stroke-linejoin="round" paint-order="stroke"/>')
    return "".join(out)


def band(uid, points, width=13.0, colour=ALERT, opacity=0.42):
    """A soft band of colour laid along a polyline (the alerting service): wide, translucent, blurred, with round ends."""
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in points)
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width)}" stroke-linecap="round" stroke-linejoin="round" filter="url(#{uid}b1)"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-opacity="{n(opacity * 0.8)}" stroke-width="{n(width * 0.55)}" stroke-linecap="round" stroke-linejoin="round"/>')


# ------------------------------------------------------------------------------------------------------------------ icons (each in a white badge; the colour says whose it is)
def badge(uid, x, y, r=8.6, ring="#1F7A4D", fill_="#FFFFFF"):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill_}" stroke="{ring}" stroke-width="1.5" filter="url(#{uid}ds)"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r - 1.5)}" fill="none" stroke="{ring}" stroke-opacity="0.28" stroke-width="0.6"/>')


def _arc(cx, cy, r, a0, a1):
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    return f"M {n(p0[0])},{n(p0[1])} A {n(r)},{n(r)} 0 0 1 {n(p1[0])},{n(p1[1])}"


def speaker(uid, x, y, r=8.6, colour="#1F7A4D"):
    """A loudspeaker with sound waves, in a badge (the UNICOM)."""
    k = r * 0.62
    body = (f"M {n(x - 0.95 * k)},{n(y - 0.3 * k)} L {n(x - 0.5 * k)},{n(y - 0.3 * k)} L {n(x + 0.1 * k)},{n(y - 0.78 * k)} L {n(x + 0.1 * k)},{n(y + 0.78 * k)} "
            f"L {n(x - 0.5 * k)},{n(y + 0.3 * k)} L {n(x - 0.95 * k)},{n(y + 0.3 * k)} Z")
    waves = "".join(f'<path d="{_arc(x + 0.1 * k, y, rr * k, -44, 44)}" fill="none" stroke="{colour}" stroke-width="{n(k * 0.2)}" stroke-linecap="round"/>' for rr in (0.62, 1.04))
    return badge(uid, x, y, r, colour) + f'<path d="{body}" fill="{colour}" stroke="{colour}" stroke-width="{n(k * 0.08)}" stroke-linejoin="round"/>' + waves


def megaphone(uid, x, y, r=8.6, colour="#1F7A4D"):
    """A megaphone with sound waves, in a badge (the TIBA broadcasts)."""
    k = r * 0.62
    cx, cy = x - 0.12 * k, y
    horn = (f"M {n(cx - 0.9 * k)},{n(cy - 0.22 * k)} L {n(cx - 0.45 * k)},{n(cy - 0.22 * k)} L {n(cx + 0.45 * k)},{n(cy - 0.7 * k)} L {n(cx + 0.45 * k)},{n(cy + 0.7 * k)} "
            f"L {n(cx - 0.45 * k)},{n(cy + 0.22 * k)} L {n(cx - 0.9 * k)},{n(cy + 0.22 * k)} Z")
    handle = f'<rect x="{n(cx - 0.72 * k)}" y="{n(cy + 0.2 * k)}" width="{n(0.3 * k)}" height="{n(0.62 * k)}" rx="{n(0.08 * k)}" fill="{colour}"/>'
    waves = "".join(f'<path d="{_arc(cx + 0.45 * k, cy, rr * k, -42, 42)}" fill="none" stroke="{colour}" stroke-width="{n(k * 0.2)}" stroke-linecap="round"/>' for rr in (0.5, 0.92))
    return badge(uid, x, y, r, colour) + f'<path d="{horn}" fill="{colour}" stroke="{colour}" stroke-width="{n(k * 0.08)}" stroke-linejoin="round"/>' + handle + waves


def tower_icon(uid, x, y, r=9.5, colour="#1E5FB3"):
    """A control tower, in a badge: a glazed cab under a roof slab with a mast, a slender shaft, a foot."""
    k = r * 0.62
    cab = f'<rect x="{n(x - 0.62 * k)}" y="{n(y - 0.92 * k)}" width="{n(1.24 * k)}" height="{n(0.56 * k)}" rx="{n(0.1 * k)}" fill="{colour}"/>'
    glass = f'<rect x="{n(x - 0.46 * k)}" y="{n(y - 0.82 * k)}" width="{n(0.92 * k)}" height="{n(0.26 * k)}" fill="#FFFFFF" fill-opacity="0.75"/>'
    roof = f'<rect x="{n(x - 0.78 * k)}" y="{n(y - 1.04 * k)}" width="{n(1.56 * k)}" height="{n(0.16 * k)}" rx="{n(0.06 * k)}" fill="{colour}"/>'
    mast = f'<line x1="{n(x)}" y1="{n(y - 1.04 * k)}" x2="{n(x)}" y2="{n(y - 1.38 * k)}" stroke="{colour}" stroke-width="{n(0.12 * k)}" stroke-linecap="round"/>'
    shaft = f'<polygon points="{pts([(x - 0.2 * k, y - 0.36 * k), (x + 0.2 * k, y - 0.36 * k), (x + 0.3 * k, y + 0.84 * k), (x - 0.3 * k, y + 0.84 * k)])}" fill="{colour}"/>'
    foot = f'<rect x="{n(x - 0.56 * k)}" y="{n(y + 0.8 * k)}" width="{n(1.12 * k)}" height="{n(0.16 * k)}" rx="{n(0.06 * k)}" fill="{colour}"/>'
    return badge(uid, x, y, r, colour) + mast + roof + cab + glass + shaft + foot


def bell(uid, x, y, r=8.6, colour=ALERT):
    """A bell, in a badge (the alerting service)."""
    k = r * 0.66
    body = (f"M {n(x - 0.95 * k)},{n(y + 0.62 * k)} L {n(x - 0.72 * k)},{n(y + 0.3 * k)} L {n(x - 0.72 * k)},{n(y - 0.28 * k)} Q {n(x - 0.72 * k)},{n(y - 0.92 * k)} {n(x)},{n(y - 0.92 * k)} "
            f"Q {n(x + 0.72 * k)},{n(y - 0.92 * k)} {n(x + 0.72 * k)},{n(y - 0.28 * k)} L {n(x + 0.72 * k)},{n(y + 0.3 * k)} L {n(x + 0.95 * k)},{n(y + 0.62 * k)} Z")
    return (badge(uid, x, y, r, colour) + f'<path d="{body}" fill="{colour}"/><circle cx="{n(x)}" cy="{n(y + 0.9 * k)}" r="{n(0.26 * k)}" fill="{colour}"/>'
            f'<rect x="{n(x - 0.1 * k)}" y="{n(y - 1.15 * k)}" width="{n(0.2 * k)}" height="{n(0.3 * k)}" fill="{colour}"/>')


def tick(uid, x, y, r=8.6, colour=ALERT):
    """A tick in a badge (the arrival report)."""
    k = r * 0.6
    return badge(uid, x, y, r, colour) + f'<polyline points="{pts([(x - 0.62 * k, y + 0.02 * k), (x - 0.14 * k, y + 0.5 * k), (x + 0.72 * k, y - 0.5 * k)])}" fill="none" stroke="{colour}" stroke-width="{n(k * 0.3)}" stroke-linecap="round" stroke-linejoin="round"/>'


def handover(uid, x, y, r=8.6, colour="#1E5FB3"):
    """Two arrows in opposite directions, in a badge (the hand-over from one controller to the next)."""
    k = r * 0.6
    up = [(x - 0.8 * k, y - 0.34 * k), (x + 0.5 * k, y - 0.34 * k)]
    dn = [(x + 0.8 * k, y + 0.34 * k), (x - 0.5 * k, y + 0.34 * k)]
    out = [badge(uid, x, y, r, colour)]
    for (a, b), sgn in ((up, 1), (dn, -1)):
        out.append(f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="{colour}" stroke-width="{n(k * 0.26)}" stroke-linecap="round"/>'
                   f'<polygon points="{pts([(b[0] + sgn * 0.34 * k, b[1]), (b[0] - sgn * 0.12 * k, b[1] - 0.4 * k), (b[0] - sgn * 0.12 * k, b[1] + 0.4 * k)])}" fill="{colour}"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ north arrow and scale bar
def north_arrow(uid, x, y, h=30.0):
    """A north arrow: a kite, one half dark and one half light, with an N above it."""
    top, foot, notch = (x, y - h * 0.5), y + h * 0.5, y + h * 0.28
    half = h * 0.24
    left = [top, (x - half, foot), (x, notch)]
    right = [top, (x + half, foot), (x, notch)]
    return (f'<g filter="url(#{uid}ds)"><polygon points="{pts(left)}" fill="{INK}" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round"/>'
            f'<polygon points="{pts(right)}" fill="#F4F1E6" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round"/></g>'
            f'<polygon points="{pts(left)}" fill="{INK}"/><polygon points="{pts(right)}" fill="#F4F1E6" stroke="{INK}" stroke-width="0.6" stroke-linejoin="round"/>'
            + label("N", x, y - h * 0.5 - 8.0, 9.5, INK, spacing=0))


def scale_bar(uid, x, y, length, nm_total=5, segments=5, text="5 NM"):
    """A scale bar of `nm_total` NM, `length` canvas units long, from (x, y) to the right, on a pale plate, labelled with digits and the unit."""
    h = 4.0
    plate = f'<rect x="{n(x - 9)}" y="{n(y - 17)}" width="{n(length + 18 + 24)}" height="{n(34)}" rx="9" fill="#FFFFFF" fill-opacity="0.86" filter="url(#{uid}ds)"/>'
    segs = []
    sw = length / segments
    for i in range(segments):
        segs.append(f'<rect x="{n(x + i * sw)}" y="{n(y - h / 2)}" width="{n(sw)}" height="{n(h)}" fill="{INK if i % 2 == 0 else "#FFFFFF"}"/>')
    frame = f'<rect x="{n(x)}" y="{n(y - h / 2)}" width="{n(length)}" height="{n(h)}" fill="none" stroke="{INK}" stroke-width="0.9"/>'
    ticks = "".join(f'<line x1="{n(xx)}" y1="{n(y - h / 2 - 2.2)}" x2="{n(xx)}" y2="{n(y + h / 2 + 2.2)}" stroke="{INK}" stroke-width="0.9"/>' for xx in (x, x + length))
    txt = glyph_text("0", x, y - 9.4, 6.2, INK, stroke=INK, stroke_width=0.2) + glyph_text(text, x + length, y - 9.4, 6.2, INK, stroke=INK, stroke_width=0.2, spacing=0.4)
    return plate + "".join(segs) + frame + ticks + txt
