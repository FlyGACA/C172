"""Helpers of worker b1 (the Saudi round, the two side views: Figure 17-1 and Figure 17-8).

* the real geometry of the vertical section from Thumamah (OETH) to Riyadh King Khalid (OERK), worked out from data/saudi_airspace.json in an equirectangular frame round the
  Thumamah ARP (x_nm = (lon - lon0) * 60 * cos(lat0), y_nm = (lat - lat0) * 60): where the line crosses each ring of the file, the ground between the two elevations;
* a plot (the map from distance and height to canvas units), the colours of the airspace classes, boundaries (a dashed line over a white casing), hatches, class discs, small
  tags of numbers;
* the pieces that stand on the ground: a runway bar, hangars, a control tower, a windsock, an amber triangle for a visual reporting point, the soil of a section;
* the route as a thick dark ribbon with a white casing, small chevrons and an arrowhead.

Plain Python (no Blender, no Pillow). Every gradient, pattern, mask and filter takes an id made from the figure's `uid`, so that two pieces of one drawing never share one."""
import json
import math
import os
import random

from figs import h_a1 as A1
from figs import h_a2 as A2
from figs import scene as S

n = S.n
pts = S.pts

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the colours of the airspace, the same in every figure of the Saudi round
COL = {"G": "#1F7A4D", "D": "#1E5FB3", "C": "#3B5FC4", "A": "#6B4FB8"}
FILL = {"G": 0.22, "D": 0.20, "C": 0.16, "A": 0.20}
GREY_G = "#7E9A89"                       # uncontrolled Class G: the pale grey-green of what is left
DANGER = "#C2410C"
VRP_AMBER = "#E8B923"
ROUTE_INK = "#1F2937"
INK = "#1F2937"

SKY = [(0.0, "#C6DBF1"), (0.5, "#DFEBF7"), (0.85, "#EDF3F8"), (1.0, "#F1F4F5")]

_DATA = {}


def data():
    """data/saudi_airspace.json, read once."""
    if not _DATA:
        with open(os.path.join(HERE, "data", "saudi_airspace.json"), encoding="utf-8") as f:
            _DATA.update(json.load(f))
    return _DATA


# ------------------------------------------------------------------------------------------------------------------ the geometry of the section
class Section:
    """The vertical section along the line from the Thumamah ARP to the Riyadh ARP. `s` is the distance in NM from OETH along the line (positive towards OERK), the frame is the
    equirectangular one round the Thumamah ARP, 1 NM = 1852 m."""

    def __init__(self):
        d = data()
        a, b = d["oeth"]["arp"], d["oerk"]["arp"]
        self.lat0, self.lon0 = a["lat"], a["lon"]
        self.k = 60.0 * math.cos(math.radians(self.lat0))
        bx, by = self.xy(b["lon"], b["lat"])
        self.length = math.hypot(bx, by)
        self.u = (bx / self.length, by / self.length)
        self.bearing = (math.degrees(math.atan2(bx, by)) + 360.0) % 360.0
        self.elev0 = d["oeth"]["elev_ft"]
        self.elev1 = d["oerk"]["elev_ft"]

    def xy(self, lon, lat):
        return ((lon - self.lon0) * self.k, (lat - self.lat0) * 60.0)

    def s_of(self, lon, lat):
        x, y = self.xy(lon, lat)
        return x * self.u[0] + y * self.u[1]

    def off_of(self, lon, lat):
        """The distance from the line, positive to the left of the direction of travel (towards OERK)."""
        x, y = self.xy(lon, lat)
        return -x * self.u[1] + y * self.u[0]

    def crossings(self, ring):
        """The values of s where the line crosses the edges of a ring of the file (a list of [lon, lat]), sorted."""
        p = [self.xy(lon, lat) for lon, lat in ring]
        out = []
        for (ax, ay), (bx, by) in zip(p, p[1:]):
            ex, ey = bx - ax, by - ay
            det = self.u[0] * (-ey) - self.u[1] * (-ex)
            if abs(det) < 1e-12:
                continue
            s = (ax * (-ey) - ay * (-ex)) / det
            t = (self.u[0] * ay - self.u[1] * ax) / det
            if 0.0 <= t <= 1.0:
                out.append(s)
        return sorted(out)

    def ground_ft(self, s):
        """The ground between the two elevations: the aerodrome elevation of Thumamah up to that of Riyadh, one smooth step (no hills)."""
        t = min(1.0, max(0.0, s / self.length))
        return self.elev0 + (self.elev1 - self.elev0) * (3 * t * t - 2 * t ** 3)

    def runway_span(self, runways):
        """(s of one threshold, s of the other) of a pair of thresholds projected on the line."""
        a = self.s_of(runways[0]["threshold"]["lon"], runways[0]["threshold"]["lat"])
        b = self.s_of(runways[1]["threshold"]["lon"], runways[1]["threshold"]["lat"])
        return (min(a, b), max(a, b))


class Plot:
    """The map from (distance, height) to canvas units: `box` is (x, y, w, h) of the picture, `xr` the distances at its left and right edges, `yr` the heights at its foot and top."""

    def __init__(self, box, xr, yr):
        self.box, self.xr, self.yr = box, xr, yr

    def X(self, s):
        x, y, w, h = self.box
        return x + (s - self.xr[0]) / (self.xr[1] - self.xr[0]) * w

    def Y(self, ft):
        x, y, w, h = self.box
        return y + h - (ft - self.yr[0]) / (self.yr[1] - self.yr[0]) * h

    def P(self, s, ft):
        return (self.X(s), self.Y(ft))

    def pts(self, points):
        return [self.P(s, f) for s, f in points]

    @property
    def unit_x(self):
        """Canvas units to one NM."""
        return self.box[2] / (self.xr[1] - self.xr[0])

    @property
    def unit_y(self):
        """Canvas units to one foot."""
        return self.box[3] / (self.yr[1] - self.yr[0])


# ------------------------------------------------------------------------------------------------------------------ lines, fills and marks
def dpath(points, close=False):
    return "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in points) + (" Z" if close else "")


def edge(points, colour, close=False, width=1.25, dash="7 4", casing=2.0, opacity=1.0, casing_opacity=0.88):
    """A boundary: a dashed line (7 4) over a white casing."""
    d = dpath(points, close)
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="{n(casing_opacity)}" stroke-width="{n(width + casing)}" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width)}" stroke-dasharray="{dash}" stroke-linejoin="round"/>')


def tint(uid, points, cls, opacity=None, top=0.8, bottom=1.2, colour=None):
    """The cross-section of a block of air: the colour of its class at the strength the brief gives (a little lighter along the top than along the foot, as a pane of glass is)."""
    op = FILL[cls] if opacity is None else opacity
    col = colour or COL[cls]
    return (f'<defs>{S.gradient(uid, [(0, col, op * top), (1, col, op * bottom)])}</defs>'
            f'<polygon points="{pts(points)}" fill="url(#{uid})"/>')


def sheen(uid, points, strength=0.28):
    """A faint light on the upper left of a pane: a diagonal gradient of white that dies out towards the middle."""
    return (f'<defs>{S.gradient(uid, [(0, "#FFFFFF", strength), (0.5, "#FFFFFF", 0.0)], 0, 0, 0.7, 1)}</defs>'
            f'<polygon points="{pts(points)}" fill="url(#{uid})"/>')


def gloss(uid, points, strength=0.12, bands=((0.30, 0.37), (0.45, 0.48))):
    """The reflection on a pane of glass: soft pale diagonal bands across the polygon (a gradient with narrow white stops, from the upper left to the lower right)."""
    stops = [(0.0, "#FFFFFF", 0.0)]
    for a, b in bands:
        stops += [(a, "#FFFFFF", 0.0), ((a + b) / 2, "#FFFFFF", strength), (b, "#FFFFFF", 0.0)]
    stops.append((1.0, "#FFFFFF", 0.0))
    return (f'<defs>{S.gradient(uid, stops, 0, 0, 1, 0.55)}</defs>'
            f'<polygon points="{pts(points)}" fill="url(#{uid})"/>')


def inner_glow(uid, points, width=3.2, opacity=0.55, blur=1.0, colour="#FFFFFF"):
    """The rim of a pane of glass: a soft pale line just inside the edge of the polygon (a wide stroke cut to the polygon and blurred)."""
    return (f'<defs><clipPath id="{uid}c"><polygon points="{pts(points)}"/></clipPath><filter id="{uid}f" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="{n(blur)}"/></filter></defs>'
            f'<g clip-path="url(#{uid}c)"><polygon points="{pts(points)}" fill="none" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width * 2)}" stroke-linejoin="round" filter="url(#{uid}f)"/></g>')


def hatch(uid, points, colour, angle=45.0, spacing=3.0, width=0.7, opacity=0.85):
    """A polygon filled with parallel lines at `angle` degrees (0 vertical, positive clockwise)."""
    return (f'<defs><pattern id="{uid}" width="{n(spacing)}" height="{n(spacing)}" patternUnits="userSpaceOnUse" patternTransform="rotate({n(angle)})">'
            f'<line x1="0" y1="-1" x2="0" y2="{n(spacing + 1)}" stroke="{colour}" stroke-width="{n(width)}" stroke-opacity="{n(opacity)}"/></pattern></defs>'
            f'<polygon points="{pts(points)}" fill="url(#{uid})"/>')


def class_disc(cx, cy, letter, cls, r=6.3):
    """A small white disc with a ring and the letter of an airspace class, in the colour of the class."""
    col = COL[cls]
    size = r * 1.42
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#FFFFFF" fill-opacity="0.95" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="{n(cx)}" y="{n(cy + size * 0.36)}" font-family="sans-serif" font-size="{n(size)}" font-weight="bold" fill="{col}" text-anchor="middle">{letter}</text>')


def tag(x, y, text, colour=INK, size=9.0, anchor="start", weight="bold", halo=3.0):
    """A few digits (a height, a distance) with a white casing round the letters."""
    return (f'<text x="{n(x)}" y="{n(y)}" font-family="sans-serif" font-size="{n(size)}" font-weight="{weight}" fill="{colour}" text-anchor="{anchor}" '
            f'stroke="#FFFFFF" stroke-width="{n(halo)}" stroke-linejoin="round" paint-order="stroke">{text}</text>')


def plain_text(x, y, text, colour=INK, size=10.5, anchor="end", weight="normal"):
    return f'<text x="{n(x)}" y="{n(y)}" font-family="sans-serif" font-size="{n(size)}" font-weight="{weight}" fill="{colour}" text-anchor="{anchor}">{text}</text>'


# ------------------------------------------------------------------------------------------------------------------ the ground
def soil(uid, top_points, bottom_y, seed=1, tones=("#E7D5A4", "#CBAC72", "#9C7F4E"), strata=(0.30, 0.55, 0.78), grit=14, haze=(7.0, 0.75)):
    """The ground in section: the soil under the ground line (`top_points`, left to right) down to `bottom_y`, shaded from pale sand to a darker earth, with a few wavy layers
    and a little grit, a pale edge along the top and a soft haze of sand just above the line (the plain going away)."""
    rnd = random.Random(seed)
    x0, x1 = top_points[0][0], top_points[-1][0]
    poly = list(top_points) + [(x1, bottom_y), (x0, bottom_y)]
    top_y = min(y for _, y in top_points)
    out = [f'<defs>{S.gradient(uid, [(0, tones[0]), (0.5, tones[1]), (1, tones[2])])}{S.gradient(uid + "h", [(0, "#F4E8C6", 0.0), (1, "#F4E8C6", haze[1])])}</defs>']
    out.append(f'<polygon points="{pts(poly)}" fill="url(#{uid})"/>')
    for i, f in enumerate(strata):
        line = [(x, y + (bottom_y - y) * f + 1.6 * math.sin(x * 0.045 + i * 1.7) + 0.9 * math.sin(x * 0.13 + i)) for x, y in top_points]
        out.append(f'<path d="{dpath(line)}" fill="none" stroke="#5E4727" stroke-opacity="{n(0.20 + 0.04 * i)}" stroke-width="{n(0.8 + 0.35 * i)}" stroke-linejoin="round"/>')
        out.append(f'<path d="{dpath([(x, y - 1.1) for x, y in line])}" fill="none" stroke="#FFF3D2" stroke-opacity="0.16" stroke-width="0.6"/>')
    for _ in range(grit):
        x = rnd.uniform(x0 + 4, x1 - 4)
        i = min(len(top_points) - 2, max(0, int((x - x0) / (x1 - x0) * (len(top_points) - 1))))
        gy = top_points[i][1]
        y = gy + (bottom_y - gy) * rnd.uniform(0.18, 0.9)
        out.append(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rnd.uniform(1.4, 3.0))}" ry="{n(rnd.uniform(0.6, 1.1))}" fill="#6E5532" opacity="{n(rnd.uniform(0.18, 0.34))}"/>')
    out.append(f'<polygon points="{pts([(x, y - haze[0]) for x, y in top_points] + list(reversed(top_points)))}" fill="url(#{uid}h)"/>')
    out.append(f'<path d="{dpath(top_points)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.1" stroke-linejoin="round"/>')
    return "".join(out)


def bushes(seed, points, count, scale=0.7, x_from=None, x_to=None):
    """Low scrub standing on a ground line (`points`, left to right): small dark clumps with a light top."""
    rnd = random.Random(seed)
    x0, x1 = (points[0][0] if x_from is None else x_from), (points[-1][0] if x_to is None else x_to)
    out = []
    for _ in range(count):
        x = rnd.uniform(x0, x1)
        gy = ground_y_at(points, x)
        k = scale * rnd.uniform(0.7, 1.25)
        out.append(f'<ellipse cx="{n(x)}" cy="{n(gy - 0.2)}" rx="{n(3.4 * k)}" ry="{n(1.5 * k)}" fill="#5F7345" opacity="0.8"/>'
                   f'<ellipse cx="{n(x - 0.4 * k)}" cy="{n(gy - 0.8 * k)}" rx="{n(2.4 * k)}" ry="{n(1.0 * k)}" fill="#7F8F55" opacity="0.9"/>')
    return "".join(out)


def ground_y_at(points, x):
    """The y of a polyline (sorted by x) at x."""
    for (xa, ya), (xb, yb) in zip(points, points[1:]):
        if xa <= x <= xb:
            t = 0.0 if xb == xa else (x - xa) / (xb - xa)
            return ya + (yb - ya) * t
    return points[-1][1] if x > points[-1][0] else points[0][1]


# ------------------------------------------------------------------------------------------------------------------ what stands on the ground
def runway_bar(x0, x1, yg, h=2.8):
    """A runway seen edge-on from the side: a dark bar on the ground line with a white casing and a dashed centre line."""
    return (f'<rect x="{n(x0 - 1.1)}" y="{n(yg - h - 1.1)}" width="{n(x1 - x0 + 2.2)}" height="{n(h + 1.8)}" rx="1.5" fill="#FFFFFF" fill-opacity="0.92"/>'
            f'<rect x="{n(x0)}" y="{n(yg - h)}" width="{n(x1 - x0)}" height="{n(h + 0.2)}" rx="0.9" fill="#2D3440"/>'
            f'<line x1="{n(x0 + 2.5)}" y1="{n(yg - h / 2)}" x2="{n(x1 - 2.5)}" y2="{n(yg - h / 2)}" stroke="#F4F1E8" stroke-width="0.5" stroke-dasharray="2.6 2.2"/>')


def hangar(uid, x, yg, w=13.0, h=5.6, colour="#E3DCC8"):
    """A small hangar: a flat-roofed block (A2.block) with a darker door."""
    out = [A2.block(x, yg, w, w * 0.34, h, colour, uid=uid, shadow=False)]
    out.append(f'<rect x="{n(x + w * 0.16)}" y="{n(yg - h * 0.72)}" width="{n(w * 0.68)}" height="{n(h * 0.72)}" fill="#7C8798" opacity="0.8"/>')
    return "".join(out)


def tower(uid, x, yg, height=21.0):
    """The control tower of Riyadh King Khalid: A2.tower, scaled so that it is `height` tall (its natural height is 52 units at s = 1), cut off at the ground line (its long shadow
    would fall on the soil of a section)."""
    k = height / 52.0
    return (f'<defs><clipPath id="{uid}cl"><rect x="{n(x - 40 * k)}" y="{n(yg - 70 * k)}" width="{n(90 * k)}" height="{n(70 * k + 0.3)}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid}cl)">{A2.tower(uid, x, yg, k)}</g>')


def windsock(uid, x, yg, pole=12.0, length=10.0):
    return A2.windsock(uid, x, yg, length=length, angle=72, mouth=3.2, segments=4, droop=0.1, pole=pole, taper=0.5, shadow=False)


def vrp(x, y, size=9.5):
    """A visual reporting point: an amber triangle with a white outline standing on (x, y) (its base on the point)."""
    h = size * 0.9
    tri = [(x, y - h), (x - size / 2, y), (x + size / 2, y)]
    return (f'<polygon points="{pts(tri)}" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="3.2" stroke-linejoin="round"/>'
            f'<polygon points="{pts(tri)}" fill="{VRP_AMBER}" stroke="#8A6A06" stroke-opacity="0.6" stroke-width="0.6" stroke-linejoin="round"/>')


# ------------------------------------------------------------------------------------------------------------------ the route
def rounded(points, radius):
    """A polyline with its corners rounded (a quadratic curve cut back `radius` along each side): path data, and the list of the corners that were rounded."""
    d = [f"M {n(points[0][0])},{n(points[0][1])}"]
    for i in range(1, len(points) - 1):
        (ax, ay), (bx, by), (cx, cy) = points[i - 1], points[i], points[i + 1]
        la, lc = math.hypot(bx - ax, by - ay), math.hypot(cx - bx, cy - by)
        r = min(radius, la * 0.45, lc * 0.45)
        p1 = (bx + (ax - bx) / la * r, by + (ay - by) / la * r)
        p2 = (bx + (cx - bx) / lc * r, by + (cy - by) / lc * r)
        d.append(f"L {n(p1[0])},{n(p1[1])} Q {n(bx)},{n(by)} {n(p2[0])},{n(p2[1])}")
    d.append(f"L {n(points[-1][0])},{n(points[-1][1])}")
    return " ".join(d)


def route(uid, points, width=4.6, radius=14.0, every=34.0, head=7.5, shadow=True):
    """The route: a thick dark ribbon (#1F2937) along the polyline `points` with a white casing, small white chevrons along it and an arrowhead at the end. The last stretch is
    drawn up to the arrowhead's base so that the head, not the line, ends the route."""
    ex, ey = points[-1]
    px, py = points[-2]
    ang = math.atan2(ey - py, ex - px)
    ux, uy = math.cos(ang), math.sin(ang)
    body = list(points[:-1]) + [(ex - ux * head * 0.8, ey - uy * head * 0.8)]
    d = rounded(body, radius)
    out = [f'<defs><filter id="{uid}s" x="-10%" y="-30%" width="120%" height="170%"><feGaussianBlur stdDeviation="1.1"/></filter></defs>']
    if shadow:
        out.append(f'<path d="{d}" fill="none" stroke="#10233F" stroke-opacity="0.30" stroke-width="{n(width + 1.0)}" stroke-linecap="round" stroke-linejoin="round" filter="url(#{uid}s)" transform="translate(0.9 2.1)"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="{n(width + 3.0)}" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="{ROUTE_INK}" stroke-width="{n(width)}" stroke-linecap="butt" stroke-linejoin="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.20" stroke-width="{n(width * 0.28)}" stroke-linecap="butt" stroke-linejoin="round" transform="translate(0 {n(-width * 0.22)})"/>')
    # the chevrons, on the straight stretches
    total = 0.0
    seg = []
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        length = math.hypot(bx - ax, by - ay)
        seg.append((total, total + length, (ax, ay), (bx, by), length))
        total += length
    t = every * 0.6
    chev = []
    while t < total - head * 2.4:
        for s0, s1, a, b, length in seg:
            if s0 <= t <= s1:
                f = (t - s0) / length
                x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
                if min(t - s0, s1 - t) > radius * 0.75:
                    ang_s = math.atan2(b[1] - a[1], b[0] - a[0])
                    dx_, dy_ = math.cos(ang_s), math.sin(ang_s)          # along the route
                    mx_, my_ = -dy_, dx_                                  # across it
                    k = width * 0.30
                    p0 = (x - dx_ * k + mx_ * k * 1.05, y - dy_ * k + my_ * k * 1.05)
                    p1 = (x + dx_ * k * 0.9, y + dy_ * k * 0.9)
                    p2 = (x - dx_ * k - mx_ * k * 1.05, y - dy_ * k - my_ * k * 1.05)
                    chev.append(f'<polyline points="{pts([p0, p1, p2])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="{n(width * 0.2)}" stroke-linecap="round" stroke-linejoin="round"/>')
                break
        t += every
    out.append("".join(chev))
    nx, ny = -uy, ux
    tip = (ex, ey)
    base = (ex - ux * head, ey - uy * head)
    tri = [tip, (base[0] + nx * head * 0.62, base[1] + ny * head * 0.62), (base[0] - nx * head * 0.62, base[1] - ny * head * 0.62)]
    out.append(f'<polygon points="{pts(tri)}" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="3.4" stroke-linejoin="round" stroke-opacity="0.95"/>'
               f'<polygon points="{pts(tri)}" fill="{ROUTE_INK}" stroke="{ROUTE_INK}" stroke-width="0.6" stroke-linejoin="round"/>')
    return "".join(out)


def leader(x1, y1, x2, y2):
    """A thin leader from a label to the thing it names (a pale casing, a dark core, a dot at the thing): A1.leader."""
    return A1.leader(x1, y1, x2, y2)
