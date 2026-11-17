"""Figure 20-2 (new: the book's section on chart projections had no figure). The projection of the Kingdom's charts: a cone on the globe, and the cone laid flat.

Both halves are drawn from real data and to scale (figs/arabia_real.py):
  the projection   the AIP's two visual chart series are "constructed on Lambert Conformal Conic Projection (Standard Parallels indicated on chart)" (GEN 3.2.4.2), and every one of
                   their 53 sheets prints the standard parallels 25°20' and 30°40' in its margin (ENR 6; data/saudi_airspace.json, "charts"). That cone has the constant n = 0.4696:
                   its half-angle is 28.0 degrees and its apex stands 2.13 earth radii above the centre of the earth. data/check_chart_cone.py measured the same constant on six sheets.
  on the left      the globe seen from above 18 N on the meridian of 45 E (the relief and the coasts of Natural Earth, public domain), the cone as glass over it, the two standard
                   parallels where glass and globe meet, and on the cone the piece that becomes the chart on the right
  on the right     that piece laid flat: from 31 to 59 E and from 13 to 34.5 N, the meridians straight lines every 3 degrees, the parallels arcs every 2 degrees, the 45 sheets of the
                   AIP's 1:500 000 chart (each 3 degrees by 2), the sheet of Riyadh and Thumamah (2546-C) lit, and the straight line from Jeddah (OEJN) to Riyadh (OERK), the AIP's
                   reference points, with its direction where it crosses three meridians: 063, 065 and 067 degrees (worked out below from the cone, not typed in)
No boundary between countries is drawn: coasts, and the sheets of the AIP's own chart index. Letters: degrees, sheet and place codes; the rest is numbered. Not for navigation."""
import math

from figs import arabia_real as AR
from figs import h_a4 as H
from figs import scene as S

W, HT = 640, 384
U = "cp2"
CONE = AR.CONE
DATA = AR.CHARTS
NAVY = "#1B2F57"
FIRE = ("#E0481B", "#FF8A3C")                       # the standard parallels
AMBER = ("#B45309", "#F59E0B")                     # the sheet of Riyadh
BLUE = ("#1D4ED8", "#93C5FD")                       # the three readings of the course

# ----------------------------------------------------------------------------------------------------- the globe and the cone in space (left)
VIEW = AR.Ortho(18.0, 45.0, 88.0, 112.0, 262.0)     # seen from above 18 N on the meridian of 45 E; 88 units to the earth's radius
ALPHA = math.asin(CONE.n)                           # the half-angle of the cone
Z_APEX = float(CONE.slant(CONE.lat1)) * math.cos(ALPHA) + math.sin(math.radians(CONE.lat1))      # the apex above the centre of the earth, earth radii
RIM_LAT = 9.0                                       # the glass is drawn down to where this parallel lies on the cone
EDGE = math.degrees(math.acos(-math.tan(ALPHA) * math.tan(math.radians(VIEW.lat))))            # the rulings this far either side of the middle meridian are the outline of the cone
AR.ensure_globe("terrain-20-02-globe", VIEW, (W, HT))

# ----------------------------------------------------------------------------------------------------- the chart (right)
WEST, EAST, SOUTH, NORTH = 31.0, 59.0, 13.0, 34.5
BOX = (240.0, 38.0, 633.0)                          # the left edge, the top and the right edge of the laid-out piece on the canvas
_half = float(CONE.rho(SOUTH)) * math.sin(CONE.n * math.radians(EAST - CONE.lon0))
SCALE = (BOX[2] - BOX[0]) / (2 * _half)             # canvas units to the metre
OX = (BOX[0] + BOX[2]) / 2
OY = BOX[1] + (CONE.rho0 - float(CONE.rho(NORTH)) * math.cos(CONE.n * math.radians(EAST - CONE.lon0))) * SCALE
AR.ensure_chart("terrain-20-02-chart", CONE, (W, HT), SCALE, (OX, OY), WEST, EAST, SOUTH, NORTH)

JEDDAH = (AR.FACTS["oejn"]["arp"]["lat"], AR.FACTS["oejn"]["arp"]["lon"])           # the aerodrome reference points of the AIP (AD 2.2)
RIYADH = (AR.FACTS["oerk"]["arp"]["lat"], AR.FACTS["oerk"]["arp"]["lon"])


def P(lat, lon):
    """The canvas point of a place on the chart."""
    x, y = CONE.xy(lat, lon)
    return (OX + float(x) * SCALE, OY - float(y) * SCALE)


def parallel(lat, lon0=WEST, lon1=EAST, step=0.5):
    k = max(1, int(round(abs(lon1 - lon0) / step)))
    return [P(lat, lon0 + (lon1 - lon0) * i / k) for i in range(k + 1)]


def cell(west, south, east, north):
    return parallel(south, west, east) + parallel(north, east, west)


def K(lat, lon):
    """A place on the cone in space: canvas x, y and its depth towards the eye."""
    s = float(CONE.slant(lat))
    rr, z, dl = s * math.sin(ALPHA), Z_APEX - s * math.cos(ALPHA), math.radians(lon - VIEW.lon)
    return VIEW.space(rr * math.sin(dl), -rr * math.cos(dl), z)


APEX = VIEW.space(0.0, 0.0, Z_APEX)
POLE = VIEW.xy(90.0, VIEW.lon)


def _bearing(v):
    """Degrees clockwise from the top of the page of a canvas direction."""
    return math.degrees(math.atan2(v[0], -v[1])) % 360.0


def _polar(c, r, bearing):
    b = math.radians(bearing)
    return (c[0] + r * math.sin(b), c[1] - r * math.cos(b))


# the straight chart line from Jeddah to Riyadh, and the three places where its direction is read: on the meridians of Jeddah, of the middle of the line and of Riyadh
_J, _R = P(*JEDDAH), P(*RIYADH)
_LEN = math.hypot(_R[0] - _J[0], _R[1] - _J[1])
_DIR = ((_R[0] - _J[0]) / _LEN, (_R[1] - _J[1]) / _LEN)
_mx, _my = (CONE.xy(*JEDDAH)[0] + CONE.xy(*RIYADH)[0]) / 2, (CONE.xy(*JEDDAH)[1] + CONE.xy(*RIYADH)[1]) / 2
_mlat, _mlon = (float(v) for v in CONE.lat_lon(_mx, _my))
READINGS = []                                       # (the place on the canvas, its latitude and longitude, the direction of the line there in whole degrees)
for _lat, _lon in (JEDDAH, (_mlat, _mlon), RIYADH):
    READINGS.append((P(_lat, _lon), _lat, _lon, CONE.bearing(JEDDAH, RIYADH, _lon)))
COURSES = [f"{round(r[3]):03d}°" for r in READINGS]
_GC, GC_NM = AR.great_circle(JEDDAH, RIYADH, 200)
_off = max(abs(((P(la, lo)[0] - _J[0]) * (-_DIR[1]) + (P(la, lo)[1] - _J[1]) * _DIR[0]) / SCALE / float(CONE.scale(la))) for la, lo in _GC) / AR.NM
assert COURSES == ["063°", "065°", "067°"] and round(GC_NM, -1) == 460 and _off < 1.0 and round(CONE.n, 2) == 0.47, (COURSES, GC_NM, _off, CONE.n)      # the numbers the legend and the book quote


# ----------------------------------------------------------------------------------------------------- drawing
def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#0B1633"), (0.55, "#14274F"), (1, "#22407A")])}'
            f'<radialGradient id="{U}v" cx="0.5" cy="0.5" r="0.75"><stop offset="0.5" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity="0.35"/></radialGradient>'
            f'<filter id="{U}gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.6"/></filter>'
            f'<filter id="{U}sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5.5"/></filter>'
            f'<filter id="{U}soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.2"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>' + H.stars(20, 110, 4, 4, W - 4, HT - 4) + f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}v)"/>')


def _runs(points):
    """The runs of consecutive points that face the eye, of a list of (x, y, depth)."""
    out, run = [], []
    for x, y, d in points:
        if d > 0:
            run.append((x, y))
        elif run:
            out.append(run)
            run = []
    if run:
        out.append(run)
    return [r for r in out if len(r) > 1]


def _rim(a0, a1, count=80):
    return [K(RIM_LAT, VIEW.lon + a0 + (a1 - a0) * i / count)[:2] for i in range(count + 1)]


def cone_back():
    """The far half of the rim of the glass, seen through it: drawn before the globe, which hides the part behind it."""
    return f'<polyline points="{S.pts(_rim(EDGE, 360.0 - EDGE))}" fill="none" stroke="#DCEBFF" stroke-opacity="0.34" stroke-width="1" stroke-dasharray="3 3"/>'


def globe_lines():
    out = []
    for lat in (-60, -30, 0, 60):
        for run in _runs([VIEW.xy(lat, VIEW.lon - 180 + 3 * i) for i in range(121)]):
            out.append(f'<polyline points="{S.pts(run)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="0.7"/>')
    for k in range(-5, 7):
        lon = VIEW.lon + 30 * k
        for run in _runs([VIEW.xy(-88 + 2 * i, lon) for i in range(89)]):
            out.append(f'<polyline points="{S.pts(run)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="0.7"/>')
    return "".join(out)


def standard_parallels_on_globe():
    out = []
    for lat in (CONE.lat1, CONE.lat2):
        for run in _runs([VIEW.xy(lat, VIEW.lon - 180 + 2 * i) for i in range(181)]):
            line = S.pts(run)
            out.append(f'<polyline points="{line}" fill="none" stroke="{FIRE[1]}" stroke-width="3.2" opacity="0.65" filter="url(#{U}gl)"/>'
                       f'<polyline points="{line}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.9" stroke-linecap="round"/>'
                       f'<polyline points="{line}" fill="none" stroke="{FIRE[0]}" stroke-width="1.05" stroke-linecap="round"/>')
    return "".join(out)


def patch():
    """The piece of the cone that the chart on the right is: a pale sheet lying on the glass."""
    pts = ([K(SOUTH, WEST + (EAST - WEST) * i / 28)[:2] for i in range(29)] + [K(NORTH, EAST - (EAST - WEST) * i / 28)[:2] for i in range(29)])
    line = S.pts(pts)
    return (f'<polygon points="{line}" fill="#FFF1CF" fill-opacity="0.34" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.35" filter="url(#{U}soft)"/>'
            f'<polygon points="{line}" fill="none" stroke="#FFFFFF" stroke-width="1.25" stroke-linejoin="round"/>')


def cone_glass():
    front = _rim(-EDGE, EDGE)
    xs = [p[0] for p in front]
    out = [f'<defs><linearGradient id="{U}cg" gradientUnits="userSpaceOnUse" x1="{S.n(min(xs))}" y1="0" x2="{S.n(max(xs))}" y2="0">'
           '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.36"/><stop offset="0.16" stop-color="#FFFFFF" stop-opacity="0.13"/><stop offset="0.6" stop-color="#DCEBFF" stop-opacity="0.07"/>'
           '<stop offset="0.9" stop-color="#BFD9FF" stop-opacity="0.2"/><stop offset="1" stop-color="#EAF3FF" stop-opacity="0.34"/></linearGradient></defs>']
    body = S.pts([APEX[:2]] + front)
    out.append(f'<polygon points="{body}" fill="url(#{U}cg)"/>')
    for k in range(-3, 4):                                                    # the rulings of the cone: where the planes of the meridians cut it
        lon = VIEW.lon + 30 * k
        if abs(30 * k) < EDGE and k != 0:
            x, y, _ = K(RIM_LAT, lon)
            out.append(f'<line x1="{S.n(APEX[0])}" y1="{S.n(APEX[1])}" x2="{S.n(x)}" y2="{S.n(y)}" stroke="#FFFFFF" stroke-opacity="0.2" stroke-width="0.7"/>')
    streak = [APEX[:2], K(RIM_LAT, VIEW.lon - 62)[:2], K(RIM_LAT, VIEW.lon - 50)[:2]]
    out.append(f'<polygon points="{S.pts(streak)}" fill="#FFFFFF" opacity="0.16" filter="url(#{U}soft)"/>')
    out.append(f'<polyline points="{S.pts([front[0], APEX[:2], front[-1]])}" fill="none" stroke="#EAF3FF" stroke-opacity="0.9" stroke-width="1.1" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{S.pts(front)}" fill="none" stroke="#EAF3FF" stroke-opacity="0.9" stroke-width="1.2"/>')
    # the earth's axis, from the pole up to the apex, and the apex
    out.append(f'<line x1="{S.n(POLE[0])}" y1="{S.n(POLE[1])}" x2="{S.n(APEX[0])}" y2="{S.n(APEX[1])}" stroke="#FFFFFF" stroke-opacity="0.75" stroke-width="1.1" stroke-dasharray="4 3"/>'
               f'<circle cx="{S.n(POLE[0])}" cy="{S.n(POLE[1])}" r="2.2" fill="#FFFFFF" stroke="#2A4A8C" stroke-width="0.8"/>'
               f'<circle cx="{S.n(APEX[0])}" cy="{S.n(APEX[1])}" r="5" fill="#FFFFFF" opacity="0.6" filter="url(#{U}gl)"/><circle cx="{S.n(APEX[0])}" cy="{S.n(APEX[1])}" r="2.6" fill="#FFFFFF" stroke="#2A4A8C" stroke-width="0.9"/>')
    return "".join(out)


FAN = parallel(SOUTH) + parallel(NORTH, EAST, WEST)


def chart_shadow():
    line = S.pts([(x + 2.5, y + 5.0) for x, y in FAN])
    return f'<polygon points="{line}" fill="#020716" opacity="0.6" filter="url(#{U}sh)"/><polygon points="{S.pts(FAN)}" fill="#EFE1BE"/>'


def tag(x, y, s, size=6.6, colour=NAVY, anchor="middle", weight="bold"):
    return (f'<text x="{S.n(x)}" y="{S.n(y)}" font-family="sans-serif" font-size="{S.n(size)}" font-weight="{weight}" fill="{colour}" text-anchor="{anchor}" '
            f'stroke="#FFFFFF" stroke-width="2.4" stroke-opacity="0.9" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def graticule():
    out = [f'<g fill="none" stroke="{NAVY}" stroke-opacity="0.5" stroke-width="0.5">']
    for lon in range(33, 58, 3):
        a, b = P(SOUTH, lon), P(NORTH, lon)
        out.append(f'<line x1="{S.n(a[0])}" y1="{S.n(a[1])}" x2="{S.n(b[0])}" y2="{S.n(b[1])}"/>')
    for lat in range(14, 35, 2):
        out.append(f'<polyline points="{S.pts(parallel(lat))}"/>')
    out.append("</g>")
    for lon in (36, 42, 48, 54):
        x, y = P(SOUTH + 0.62, lon)
        out.append(tag(x + 1.6, y, f"{lon}°", 6.8, anchor="start"))
    for lat in (16, 20, 24, 28, 32):
        x, y = P(lat, WEST + 0.35)
        out.append(tag(x, y + 7.2, f"{lat}°", 6.8, anchor="start"))
    return "".join(out)


def sheets():
    """The 45 sheets of the AIP's 1:500 000 chart, and the one that covers Riyadh and Thumamah."""
    out = [f'<g fill="#FFFFFF" fill-opacity="0.3" stroke="{NAVY}" stroke-opacity="0.85" stroke-width="0.6" stroke-linejoin="round">']
    edges = {}
    for s in DATA["sheets_500k"]:
        out.append(f'<polygon points="{S.pts(cell(s["west"], s["south"], s["east"], s["north"]))}"/>')
        for key in (("s", s["south"], s["west"]), ("s", s["north"], s["west"]), ("w", s["west"], s["south"]), ("w", s["east"], s["south"])):      # the sheet's four sides: along a parallel from a meridian, along a meridian from a parallel
            edges[key] = edges.get(key, 0) + 1
    out.append("</g>")
    rim = []                                                                  # a side that belongs to one sheet only is the edge of the area the series covers
    for (kind, fixed, start), count in edges.items():
        if count == 1:
            rim.append(S.pts(parallel(fixed, start, start + 3.0)) if kind == "s" else S.pts([P(start, fixed), P(start + 2.0, fixed)]))
    out.append(f'<g fill="none" stroke-linecap="round">' + "".join(f'<polyline points="{line}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="2.6"/>' for line in rim)
               + "".join(f'<polyline points="{line}" stroke="{NAVY}" stroke-width="1.15"/>' for line in rim) + "</g>")
    home = next(s for s in DATA["sheets_500k"] if s["sheet"] == DATA["sheet_of_oeth"])
    line = S.pts(cell(home["west"], home["south"], home["east"], home["north"]))
    out.append(f'<polygon points="{line}" fill="{AMBER[1]}" fill-opacity="0.42" stroke="#FFFFFF" stroke-width="2.6" stroke-linejoin="round"/>'
               f'<polygon points="{line}" fill="none" stroke="{AMBER[0]}" stroke-width="1.3" stroke-linejoin="round"/>')
    return "".join(out)


def standard_parallels_on_chart():
    out = []
    for lat, text in zip((CONE.lat1, CONE.lat2), DATA["projection"]["standard_parallels_printed"]):
        line = S.pts(parallel(lat))
        out.append(f'<polyline points="{line}" fill="none" stroke="{FIRE[1]}" stroke-width="4.4" opacity="0.7" filter="url(#{U}gl)"/>'
                   f'<polyline points="{line}" fill="none" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="2.9"/><polyline points="{line}" fill="none" stroke="{FIRE[0]}" stroke-width="1.6"/>')
        x, y = P(lat, EAST - 0.5)
        out.append(tag(x, y - 3.6, text.replace("'", "′"), 8.6, FIRE[0], "end"))
    return "".join(out)


def course_line():
    a = (_J[0] - _DIR[0] * 9.0, _J[1] - _DIR[1] * 9.0)
    b = (_R[0] + _DIR[0] * 11.0, _R[1] + _DIR[1] * 11.0)
    out = []
    # the wedges first, under the line: from the meridian (north) clockwise round to the line
    for (c, lat, lon, course), text in zip(READINGS, COURSES):
        up = P(lat + 2.6, lon)
        north = _bearing((up[0] - c[0], up[1] - c[1]))
        sweep = (_bearing(_DIR) - north) % 360.0                              # clockwise from the meridian round to the line: the direction read on the chart
        assert abs(sweep - course) < 0.05, (sweep, course)                    # the drawing agrees with the cone's own arithmetic
        sector = [c] + [_polar(c, 16.5, north + sweep * i / 16) for i in range(17)]
        out.append(f'<polygon points="{S.pts(sector)}" fill="{BLUE[1]}" fill-opacity="0.7" stroke="none"/>'
                   f'<polyline points="{S.pts(sector[1:])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="2.4"/><polyline points="{S.pts(sector[1:])}" fill="none" stroke="{BLUE[0]}" stroke-width="1.15"/>')
        # the meridian through the place, with a north arrowhead
        ux, uy = (up[0] - c[0]) / math.hypot(up[0] - c[0], up[1] - c[1]), (up[1] - c[1]) / math.hypot(up[0] - c[0], up[1] - c[1])
        tip = (up[0] + ux * 4.6, up[1] + uy * 4.6)
        head = [tip, (up[0] - uy * 2.5, up[1] + ux * 2.5), (up[0] + uy * 2.5, up[1] - ux * 2.5)]
        out.append(f'<line x1="{S.n(c[0])}" y1="{S.n(c[1])}" x2="{S.n(up[0])}" y2="{S.n(up[1])}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="2.6" stroke-linecap="round"/>'
                   f'<polygon points="{S.pts(head)}" fill="{NAVY}" stroke="#FFFFFF" stroke-width="1.5" stroke-linejoin="round" paint-order="stroke"/>'
                   f'<line x1="{S.n(c[0])}" y1="{S.n(c[1])}" x2="{S.n(up[0])}" y2="{S.n(up[1])}" stroke="{NAVY}" stroke-width="1.1" stroke-linecap="round"/>')
        lx, ly = _polar(c, 27.5, north + sweep * 0.46)
        out.append(tag(lx, ly + 3.0, text, 9.2, BLUE[0]))
    out.append(f'<line x1="{S.n(a[0])}" y1="{S.n(a[1])}" x2="{S.n(b[0])}" y2="{S.n(b[1])}" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="3.6" stroke-linecap="round"/>'
               f'<line x1="{S.n(a[0])}" y1="{S.n(a[1])}" x2="{S.n(b[0])}" y2="{S.n(b[1])}" stroke="#1F2937" stroke-width="1.6" stroke-linecap="round"/>')
    for c in (_J, _R):
        out.append(f'<circle cx="{S.n(c[0])}" cy="{S.n(c[1])}" r="2.9" fill="#FFFFFF" stroke="#1F2937" stroke-width="1.4"/>')
    out.append(tag(_J[0] - 5.0, _J[1] + 11.0, "OEJN", 7.8, "#1F2937", "end"))
    out.append(tag(_R[0] + 7.0, _R[1] + 10.6, "OERK", 7.8, "#1F2937", "start"))
    return "".join(out)


def chart_edge():
    return f'<polygon points="{S.pts(FAN)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.2" stroke-linejoin="round"/>'


def unroll():
    """From the piece on the cone to the same piece laid flat."""
    a = K(NORTH, EAST)
    return H.ribbon(U + "un", [(a[0] + 5.0, a[1] - 5.0), (196.0, 176.0), (228.0, 138.0), (258.0, 118.0)], width=4.6, colours=("#F2C14E", "#FFE6A3"), head=2.2, casing=1.2, glow="#FFD76A")


def callouts():
    c = S.callout
    out = []
    g = K(RIM_LAT + 6.0, VIEW.lon - 80.0)
    out.append(c(1, 22.0, 150.0, g[0] + 2.0, g[1], r=10))                                               # the cone
    sp = VIEW.xy(CONE.lat1, VIEW.lon - 62.0)
    out.append(c(2, 20.0, 222.0, sp[0], sp[1], r=10))                                                   # the standard parallels (on the globe)
    out.append(c(3, 160.0, 62.0, APEX[0] + 2.2, APEX[1] - 1.6, r=10))                                   # the apex
    pk = K(15.5, 54.0)
    out.append(c(4, 196.0, 318.0, pk[0], pk[1], r=10))                                                  # the piece of the cone
    return "".join(out)


def chart_callouts():
    c = S.callout
    out = []
    s2 = P(CONE.lat2, 54.4)
    out.append(c(2, 598.0, 20.0, s2[0], s2[1] - 1.0, r=10))                                             # the standard parallels (on the chart)
    m = P(31.6, 39.0)
    out.append(c(5, 352.0, 18.0, m[0], m[1], r=10))                                                     # a meridian
    p = P(18.0, 55.2)
    out.append(c(6, 618.0, 300.0, p[0], p[1], r=10))                                                    # a parallel
    sh = P(17.0, 49.5)
    out.append(c(7, 520.0, 366.0, sh[0], sh[1], r=10))                                                  # the sheets
    home = P(24.03, 46.3)
    out.append(c(8, 456.0, 234.0, home[0], home[1] - 0.3, r=10))                                              # sheet 2546-C
    ln = (_J[0] + _DIR[0] * _LEN * 0.33, _J[1] + _DIR[1] * _LEN * 0.33)
    out.append(c(9, 392.0, 262.0, ln[0], ln[1] + 0.8, r=10))                                            # the straight line
    w = _polar(READINGS[0][0], 12.0, 28.0)
    out.append(c(10, 226.0, 224.0, w[0] - 1.0, w[1], r=10))                                             # the three readings
    return "".join(out)


def layers():
    return [background(), cone_back(), AR.sprite_box("terrain-20-02-globe"), globe_lines(), patch(), standard_parallels_on_globe(), cone_glass(),
            chart_shadow(), AR.sprite_box("terrain-20-02-chart"), graticule(), sheets(), standard_parallels_on_chart(), course_line(), chart_edge(),
            unroll(), callouts(), chart_callouts()]


def plate():
    return {
        "id": "fig-20-02-chart-projection",
        "replaces": "fig-20-02-chart-projection.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-20-02-chart-projection.jpg",
        "caption": "Figure 20-2. The projection of the Kingdom's charts: a cone that cuts the globe along two parallels, laid flat",
        "desc": ("Figure 20-2. The projection of the Kingdom's charts: a cone that cuts the globe along two parallels, laid flat. The standard parallels are those printed on the sheets of the AIP's charts "
                 "(ENR 6, AMDT 11/26). Relief and coasts: Natural Earth (public domain); no boundaries are drawn. Not for navigation."),
        "legend": [
            "The cone: it stands on the earth's axis and cuts the globe along two parallels.",
            "The two standard parallels, where the cone meets the globe and the projection keeps the scale exactly: 25°20' and 30°40' N on the AIP's charts of the Kingdom.",
            "The apex of the cone, above the North Pole: every meridian of the chart is a straight line towards it.",
            "The piece of the cone that becomes the chart: laid flat, it is the fan on the right.",
            "A meridian: a straight line. The apex lies far above the top of the sheet, so the meridians close towards the north, by 0.47° for each degree of longitude.",
            "A parallel: an arc of a circle about the apex.",
            "The 45 sheets of the AIP's Aeronautical Chart — ICAO 1:500 000, each 3° of longitude by 2° of latitude.",
            "Sheet 2546-C, Riyadh, which covers Thumamah.",
            "A straight line from Jeddah (OEJN) to Riyadh (OERK), 460 NM: nowhere more than 1 NM from the great circle.",
            "The direction of that line at three meridians: 063° at Jeddah's, 065° at the middle of the line and 067° at Riyadh's. Measure at the middle.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
