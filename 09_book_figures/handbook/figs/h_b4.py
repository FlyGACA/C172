"""Helpers of worker b4 (the circuit of Thumamah, figures 18-7 and 26-1; not a figure: plates_spec.py only loads f_*.py). Plain Python, no Blender, no Pillow.

The ground plan is the one of figure 18-1 (figs/f_18_01_aerodrome_plan.py): the runway and its stopways from the AIP, the pavements, the roofs and the road of Thumamah derived from open
Sentinel-2 imagery (data/oeth_plan.json; "Contains modified Copernicus Sentinel data 2026"), in the runway frame: `s` metres from the threshold of runway 17 (the north end) towards runway 35 (the south end), `t` metres to the west of the centreline. The
page is the frame itself: x = s, y = t (west down, so that north is to the left, a little up: the north arrow says so).

    Plan        the frame of a plan view: page x = x0 + s k, y = y0 + t k (k units to the metre)
    Path        a route in the frame (lines and arcs), measured along, with marks
    circuit35   the left-hand circuit for runway 35 (the AIP: circuit altitude 2 900 ft AMSL, both circuits on the west side); its shape is illustrative: the AIP gives no size
    aerodrome   the runway, stopways, pavements, buildings and road to scale, small
    route       a thick ribbon with a white casing and a soft shadow, with solid arrowheads along it
    north_arrow, scale_bar, ground_card, frame, wind_arrows, profile pieces (sky card, ground)

Every id that a piece defines starts with `b4`."""
import json
import math
import os

from figs import h_a1 as A1
from figs import h_a2 as H2
from figs import scene as S

n = S.n
pts = S.pts

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(HERE, "data", "oeth_plan.json"), encoding="utf-8") as _f:
    PLAN = json.load(_f)

RW = 25.0                      # half the width of the runway, metres
RWD = 36.0                     # drawn a little wider than life at the small scale of the circuit, so that the thin route over the runway leaves a dark margin (the plan of figure 18-1 is true to scale)
S_N, S_S = 0.0, 4004.6         # the two ends of the runway in the frame: the threshold of 17 (north) and of 35 (south), as the plan of figure 18-1 has them
STOP_N, STOP_S = 300.0, 60.0   # the stopways beyond them (AIP AD 2.12)
YEL = "#EDB92D"
BLUE, BLUE_MID, BLUE_HI = "#1D4ED8", "#3B73EE", "#A9C4FF"
ORANGE = "#C2410C"
GREEN = "#047857"
VIOLET = "#6B4FB8"
INK = "#1F2937"


# ------------------------------------------------------------------------------------------------------------------ the frame
class Plan:
    """A plan view of the runway frame: page x = x0 + s k, page y = y0 + t k (west down)."""

    def __init__(self, x0, y0, k):
        self.x0, self.y0, self.k = x0, y0, k

    def xy(self, s, t):
        return (self.x0 + s * self.k, self.y0 + t * self.k)

    def tsxy(self, t, s):
        return self.xy(s, t)

    def units(self, metres):
        return metres * self.k


# ------------------------------------------------------------------------------------------------------------------ a route in the frame
class Path:
    """A route in the runway frame as dense (s, t) points with the distance along it (metres): lines and arcs are added one after the other, `mark` notes a name for the distance so far."""

    def __init__(self, s, t):
        self.pts = [(s, t)]
        self.cum = [0.0]
        self.marks = {}

    def _add(self, p):
        q = self.pts[-1]
        d = math.hypot(p[0] - q[0], p[1] - q[1])
        if d > 1e-6:
            self.pts.append(p)
            self.cum.append(self.cum[-1] + d)

    def line(self, s, t, step=20.0):
        s0, t0 = self.pts[-1]
        length = math.hypot(s - s0, t - t0)
        for i in range(1, max(1, int(length / step)) + 1):
            k = i / max(1, int(length / step))
            self._add((s0 + (s - s0) * k, t0 + (t - t0) * k))
        return self

    def arc(self, cs, ct, r, a0, a1, step=10.0):
        """An arc about the centre (cs, ct) from the angle a0 to a1 (degrees; the point is (cs + r cos a, ct + r sin a))."""
        count = max(6, int(abs(math.radians(a1 - a0)) * r / step))
        for i in range(1, count + 1):
            a = math.radians(a0 + (a1 - a0) * i / count)
            self._add((cs + r * math.cos(a), ct + r * math.sin(a)))
        return self

    def mark(self, name):
        self.marks[name] = self.cum[-1]
        return self

    @property
    def length(self):
        return self.cum[-1]

    def at(self, d):
        """The point (s, t) at the distance d along the route and the unit direction (ds, dt) there."""
        d = max(0.0, min(self.cum[-1], d))
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= d:
                lo = mid
            else:
                hi = mid
        (s0, t0), (s1, t1) = self.pts[lo], self.pts[hi]
        seg = self.cum[hi] - self.cum[lo] or 1.0
        u = (d - self.cum[lo]) / seg
        return (s0 + (s1 - s0) * u, t0 + (t1 - t0) * u), ((s1 - s0) / seg, (t1 - t0) / seg)

    def piece(self, d0, d1):
        """The points from the distance d0 to d1 (the ends interpolated)."""
        out = [self.at(d0)[0]]
        out += [p for p, c in zip(self.pts, self.cum) if d0 < c < d1]
        out.append(self.at(d1)[0])
        return out

    def mirrored(self, about):
        """The same route turned round the middle of the runway: s becomes about - s (the circuit of the other runway)."""
        q = Path(about - self.pts[0][0], self.pts[0][1])
        q.pts = [(about - s, t) for s, t in self.pts]
        q.cum = list(self.cum)
        q.marks = dict(self.marks)
        return q


def circuit35(D=1000.0, R=300.0, xc=-700.0, lift=3275.0, aim=3694.6, xb=None):
    """The left-hand circuit for runway 35 (it lies on the west side: down the page): from the lift-off on the runway (s = `lift`) straight ahead (north: to the left) to the crosswind turn
    at s = `xc`, across (west) to the downwind line `D` metres from the runway, down it (south) to the point where the threshold is 45 degrees behind (D beyond the threshold), the turn to base,
    the base leg, the turn to final and final to the aiming point (s = `aim`). Corners are arcs of radius `R`. The shape is illustrative: the AIP gives direction and altitude only."""
    xb = (S_S + D) if xb is None else xb
    p = Path(lift, 0.0)
    p.mark("liftoff")
    p.line(xc, 0.0).mark("up_end")
    p.arc(xc, R, R, -90.0, -180.0)
    p.mark("cross_start")
    p.line(xc - R, D - R)
    p.mark("cross_end")
    p.arc(xc, D - R, R, 180.0, 90.0)
    p.mark("downwind")
    p.line(xb, D)
    p.mark("downwind_end")
    p.arc(xb, D - R, R, 90.0, 0.0)
    p.mark("base_start")
    p.line(xb + R, R)
    p.mark("base_end")
    p.arc(xb, R, R, 0.0, -90.0)
    p.mark("final")
    p.line(aim, 0.0)
    p.mark("end")
    return p


# ------------------------------------------------------------------------------------------------------------------ defs
def defs():
    return ("<defs>" + H2.blur_filter("b4bl", 1.0) + H2.blur_filter("b4bs", 0.6) + H2.shadow_filter("b4sh", 0.9, 1.4, 1.0, 0.32)
            + '<filter id="b4rs" x="-10%" y="-60%" width="120%" height="260%"><feGaussianBlur stdDeviation="1.05"/></filter>'
            + '<filter id="b4ds" x="-30%" y="-30%" width="170%" height="180%"><feDropShadow dx="0.5" dy="1.2" stdDeviation="1.0" flood-color="#10233F" flood-opacity="0.34"/></filter>'
            + "</defs>")


# ------------------------------------------------------------------------------------------------------------------ routes as ribbons
def _poly(page_pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in page_pts)


def ribbon_line(page_pts, w=3.4, base=BLUE, mid=BLUE_MID, hi=BLUE_HI, casing=1.15, shadow=True, opacity=1.0):
    """A thick route with a white casing, a soft shadow and a rounded, lit body (three strokes, the lightest a little to the upper left): a ribbon along the points of the page."""
    pl = _poly(page_pts)
    out = []
    if shadow:
        out.append(f'<polyline points="{pl}" fill="none" stroke="#10233F" stroke-opacity="0.34" stroke-width="{n(w + 1.4)}" stroke-linecap="round" stroke-linejoin="round" '
                   f'transform="translate(0.9 1.7)" filter="url(#b4rs)"/>')
    out.append(f'<polyline points="{pl}" fill="none" stroke="#FFFFFF" stroke-opacity="0.93" stroke-width="{n(w + 2 * casing)}" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{pl}" fill="none" stroke="{base}" stroke-opacity="{n(opacity)}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{pl}" fill="none" stroke="{mid}" stroke-opacity="{n(opacity)}" stroke-width="{n(w * 0.62)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(-0.12 -0.18)"/>')
    out.append(f'<polyline points="{pl}" fill="none" stroke="{hi}" stroke-opacity="0.8" stroke-width="{n(w * 0.2)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(-0.3 -0.42)"/>')
    return "".join(out)


def _smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def strip_width(s, t, wide=3.3, thin=1.35, casing_wide=1.15, casing_thin=0.2, ramp=160.0):
    """The width of a route and of its casing at a point of the frame: thin where it runs over the runway strip (the runway is only 50 m across, 4 units at this scale, and a thick ribbon
    would hide it), thick everywhere else, with a smooth change over `ramp` metres beyond the ends of the strip (stopways included)."""
    over = max(S_N - STOP_N - s, s - (S_S + STOP_S), 0.0)
    u = _smooth(over / ramp) if abs(t) < 60.0 else 1.0
    return thin + (wide - thin) * u, casing_thin + (casing_wide - casing_thin) * u


def ribbon_poly(page_pts, widths, casings, base=BLUE, mid=BLUE_MID, hi=BLUE_HI, shadow=True, opacity=1.0, cap_start=True):
    """A route as polygons of varying width (`widths`, `casings` per point): a white casing, the body, a lighter body inside it and a thin light edge to the upper left, a soft shadow."""
    def outline(scale, extra=0.0):
        left, right = [], []
        for i, (x, y) in enumerate(page_pts):
            a, b = page_pts[max(0, i - 1)], page_pts[min(len(page_pts) - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            m = math.hypot(tx, ty) or 1.0
            nx, ny = -ty / m, tx / m
            h = widths[i] * scale / 2 + (casings[i] if extra else 0.0)
            left.append((x + nx * h, y + ny * h))
            right.append((x - nx * h, y - ny * h))
        return left + right[::-1], left, right
    body, left, right = outline(1.0)
    case, _, _ = outline(1.0, 1)
    inner, _, _ = outline(0.62)
    out = []
    if shadow:
        out.append(f'<polygon points="{pts(case)}" fill="#10233F" fill-opacity="0.34" transform="translate(0.9 1.7)" filter="url(#b4rs)"/>')
    out.append(f'<polygon points="{pts(case)}" fill="#FFFFFF" fill-opacity="0.93" stroke="#FFFFFF" stroke-opacity="0.93" stroke-width="0.6" stroke-linejoin="round"/>')
    out.append(f'<polygon points="{pts(body)}" fill="{base}" fill-opacity="{n(opacity)}" stroke="{base}" stroke-width="0.4" stroke-linejoin="round"/>')
    out.append(f'<polygon points="{pts(inner)}" fill="{mid}" fill-opacity="{n(opacity)}" transform="translate(-0.12 -0.18)"/>')
    edge = [((a[0] * 0.35 + b[0] * 0.65), (a[1] * 0.35 + b[1] * 0.65)) for a, b in zip(left, page_pts)]
    out.append(f'<polyline points="{pts(edge)}" fill="none" stroke="{hi}" stroke-opacity="0.75" stroke-width="0.7" stroke-linecap="round" stroke-linejoin="round" transform="translate(-0.2 -0.3)"/>')
    return "".join(out)


def head(x, y, ux, uy, length=8.0, width=8.6, fill=BLUE, casing=1.0, notch=0.28):
    """A solid arrowhead with its tip at (x, y) pointing along the unit vector (ux, uy): a white casing, the colour, a notched back."""
    nx, ny = -uy, ux
    bx, by = x - ux * length, y - uy * length
    inner = (x - ux * length * (1 - notch), y - uy * length * (1 - notch))
    poly = [(x, y), (bx + nx * width / 2, by + ny * width / 2), inner, (bx - nx * width / 2, by - ny * width / 2)]
    return (f'<polygon points="{pts(poly)}" fill="#FFFFFF" fill-opacity="0.95" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="{n(casing * 2)}" stroke-linejoin="round"/>'
            f'<polygon points="{pts(poly)}" fill="{fill}" stroke="{fill}" stroke-width="0.5" stroke-linejoin="round"/>'
            f'<polyline points="{pts([poly[1], poly[0], poly[3]])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="0.7" stroke-linejoin="round" transform="translate(-0.2 -0.3)"/>')


def heads_on(P, path, dists, length=8.0, width=8.6, fill=BLUE, tip_at_end=False):
    """Arrowheads along a path: centred on each distance (metres), pointing along it."""
    out = []
    for d in dists:
        (s, t), (ds, dt) = path.at(d)
        x, y = P.xy(s, t)
        m = math.hypot(ds, dt) or 1.0
        ux, uy = ds / m, dt / m
        tip = (x + ux * length / 2, y + uy * length / 2) if not tip_at_end else (x, y)
        out.append(head(tip[0], tip[1], ux, uy, length, width, fill))
    return "".join(out)


def dashed_route(page_pts, colour, w=1.6, dash="5 3.4", casing=1.1, shadow=True):
    """A thin dashed route with a white casing (the same dashes, wider) and a soft shadow."""
    pl = _poly(page_pts)
    out = []
    if shadow:
        out.append(f'<polyline points="{pl}" fill="none" stroke="#10233F" stroke-opacity="0.22" stroke-width="{n(w + 1.0)}" stroke-dasharray="{dash}" stroke-linecap="round" stroke-linejoin="round" '
                   f'transform="translate(0.7 1.3)" filter="url(#b4bs)"/>')
    out.append(f'<polyline points="{pl}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="{n(w + 2 * casing)}" stroke-dasharray="{dash}" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{pl}" fill="none" stroke="{colour}" stroke-width="{n(w)}" stroke-dasharray="{dash}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


def ring(x, y, r=4.4, fill="#FFFFFF", stroke=INK, sw=1.7):
    """The white ring with a dark edge that marks a point of a route (the old figures')."""
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r + 1.1)}" fill="#FFFFFF" fill-opacity="0.55"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{n(sw)}" filter="url(#b4ds)"/>')


def square_mark(x, y, s=6.4, fill=ORANGE):
    """The orange square of the old figure (the downwind checks)."""
    return (f'<rect x="{n(x - s / 2 - 1.1)}" y="{n(y - s / 2 - 1.1)}" width="{n(s + 2.2)}" height="{n(s + 2.2)}" rx="1.4" fill="#FFFFFF" fill-opacity="0.92"/>'
            f'<rect x="{n(x - s / 2)}" y="{n(y - s / 2)}" width="{n(s)}" height="{n(s)}" rx="1" fill="{fill}" stroke="#7C2D12" stroke-width="0.6" filter="url(#b4ds)"/>')


def dot_mark(x, y, r=2.6):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r + 1.0)}" fill="#FFFFFF" fill-opacity="0.9"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{INK}" filter="url(#b4ds)"/>')


# ------------------------------------------------------------------------------------------------------------------ the aerodrome, small
PAV = {p["name"]: p for p in PLAN["pavements"]}
ROOF = {"white": "#F7F5EE", "light": "#EAE5D6", "green": "#7FA97C", "grey": "#C3C5C8", "tan": "#D2BE92", "beige_grey_bays": "#DDD0B0", "white_oeth": "#F7F5EE"}


def _path_of(ring_ts, P):
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in (P.xy(s, t) for t, s in ring_ts)) + " Z"


def aerodrome(P, runway_text=True, markings=True):
    """Thumamah to scale: the road as a faint line, the pavements (concrete pale grey, asphalt dark, each on a graded shoulder), the runway with its edge lines and centreline,
    the two stopways outlined in yellow, the buildings with a short shadow. Drawn at the plan's scale `P.k` (units to the metre): small, so the paint is a hair wider than life."""
    f = P.xy
    out = []
    road = " ".join(f"{x:.1f},{y:.1f}" for x, y in (f(s, t) for t, s in PLAN["lines"]["ACCESS_ROAD"]))
    out.append(f'<polyline points="{road}" fill="none" stroke="#B9AD90" stroke-opacity="0.55" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round"/>'
               f'<polyline points="{road}" fill="none" stroke="#4B5363" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>'
               f'<polyline points="{road}" fill="none" stroke="#F1E3A0" stroke-width="0.3" stroke-dasharray="1.6 1.6" stroke-linecap="round"/>')
    # the pavements
    order = [p for p in PLAN["pavements"] if p["surface"] != "stopway"]
    for p in order:
        d = _path_of(p["ring"], P) + "".join(" " + _path_of(h, P) for h in p["holes"])
        out.append(f'<path d="{d}" fill="none" stroke="#C8B78F" stroke-opacity="0.65" stroke-width="1.8" stroke-linejoin="round"/>')
    for p in order:
        d = _path_of(p["ring"], P) + "".join(" " + _path_of(h, P) for h in p["holes"])
        fill = "#A4A7AC" if p["surface"] == "concrete" else "#4B5363"
        out.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.3" stroke-linejoin="round"/>')
    # the runway and its stopways
    x0, y0 = f(S_N - STOP_N, -RWD)
    x1, y1 = f(S_S + STOP_S, RWD)
    out.append(f'<rect x="{x0 - 1.1:.2f}" y="{y0 - 1.1:.2f}" width="{x1 - x0 + 2.2:.2f}" height="{y1 - y0 + 2.2:.2f}" rx="0.8" fill="#C8B78F" fill-opacity="0.62"/>')
    rx0, _ = f(S_N, -RW)
    rx1, _ = f(S_S, -RW)
    out.append(f'<defs><linearGradient id="b4rwy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5E6677"/><stop offset="0.5" stop-color="#454D5C"/><stop offset="1" stop-color="#363D4B"/></linearGradient></defs>')
    out.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" fill="url(#b4rwy)"/>')
    for a, b in ((S_N - STOP_N, S_N), (S_S, S_S + STOP_S)):                  # the stopways, outlined in yellow
        xa, ya = f(a, -RWD)
        xb, yb = f(b, RWD)
        out.append(f'<rect x="{xa + 0.3:.2f}" y="{ya + 0.3:.2f}" width="{xb - xa - 0.6:.2f}" height="{yb - ya - 0.6:.2f}" fill="#2F3644" fill-opacity="0.55" stroke="{YEL}" stroke-width="0.7"/>')
    if markings:
        for sg in (-1, 1):                                                    # the edge lines
            a, b = f(S_N + 3, sg * (RWD - 2.2)), f(S_S - 3, sg * (RWD - 2.2))
            out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#F4F1E6" stroke-opacity="0.85" stroke-width="0.32"/>')
        a, b = f(S_N + 60, 0), f(S_S - 60, 0)
        out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#F4F1E6" stroke-opacity="0.9" stroke-width="0.5" stroke-dasharray="2.4 2.8"/>')
        for end in (S_N, S_S):                                                # the threshold bars, a little wider than life
            sg = 1 if end == S_N else -1
            for k in range(7):
                t = -RWD + 6 + k * (2 * RWD - 12) / 6
                a, b = f(end + sg * 6, t), f(end + sg * 40, t)
                out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#F4F1E6" stroke-width="0.45"/>')
    # the buildings, with a short shadow to the lower right
    for b in PLAN["buildings"]:
        ring_xy = [f(s, t) for t, s in b["ring"]]
        ps = " ".join(f"{x:.2f},{y:.2f}" for x, y in ring_xy)
        k = b["height_m_estimated"] * P.k * 0.5
        sh = " ".join(f"{x + 0.8 * k:.2f},{y + 1.0 * k:.2f}" for x, y in ring_xy)
        out.append(f'<polygon points="{sh}" fill="#2B2418" fill-opacity="0.34"/>')
        out.append(f'<polygon points="{ps}" fill="{ROOF.get(b["roof"], "#EAE5D6")}" stroke="#8C8470" stroke-width="0.3" stroke-linejoin="round"/>')
    if runway_text:                                                           # the designators, upright, above the two ends (as the strip of figure 18-1)
        d1, d2 = f(S_N + 60, -RWD), f(S_S - 60, -RWD)
        out.append(H2.glyph_text("17", d1[0] + 5.5, d1[1] - 7.5, 6.0, "#FFFFFF", rotate=0, stroke=INK, stroke_width=0.4))
        out.append(H2.glyph_text("35", d2[0] - 5.5, d2[1] - 7.5, 6.0, "#FFFFFF", rotate=0, stroke=INK, stroke_width=0.4))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ cards, north, scale
def ground_card(x, y, w, h, tint_op=0.2, r=9.0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#F4EBD3" fill-opacity="{tint_op}"/>'


def frame(x, y, w, h, r=9.0):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.2"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="#6B6247" stroke-opacity="0.75" stroke-width="0.8"/>')


def north_arrow(cx, cy):
    """A disc with the arrow of north (in the runway frame north is (-0.9872, -0.1593) on the page: to the left, a little up), the N beside the head."""
    nt, ns = PLAN["runway"]["north_in_ts_per_m"]
    vx, vy = ns, nt
    m = math.hypot(vx, vy)
    vx, vy = vx / m, vy / m
    ox, oy = cx - vx * 3.0, cy - vy * 3.0              # the arrow sits a little towards its tail, the N takes the head's side
    tail = (ox - vx * 15, oy - vy * 15)
    tip = (ox + vx * 11, oy + vy * 11)
    base = (ox + vx * 3, oy + vy * 3)
    return (f'<circle cx="{cx}" cy="{cy}" r="25" fill="#FFFFFF" fill-opacity="0.86"/>'
            f'<line x1="{tail[0]:.1f}" y1="{tail[1]:.1f}" x2="{base[0]:.1f}" y2="{base[1]:.1f}" stroke="{INK}" stroke-width="2.2"/>'
            f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {base[0] - vy * 5:.1f},{base[1] + vx * 5:.1f} {base[0] + vy * 5:.1f},{base[1] - vx * 5:.1f}" fill="{INK}"/>'
            f'<text x="{ox + vx * 19:.1f}" y="{oy + vy * 19 + 4:.1f}" font-family="sans-serif" font-size="11.5" font-weight="bold" fill="{INK}" text-anchor="middle">N</text>')


def scale_bar(x, y, length, label):
    """A bar `length` units long with its ends ticked and the label above it, on a pale plate; (x, y) is its left end."""
    return (f'<rect x="{x - 8}" y="{y - 15}" width="{length + 16:.0f}" height="26" rx="6" fill="#FFFFFF" fill-opacity="0.84"/>'
            f'<line x1="{x}" y1="{y}" x2="{x + length:.1f}" y2="{y}" stroke="{INK}" stroke-width="2.2"/><line x1="{x}" y1="{y - 5}" x2="{x}" y2="{y + 5}" stroke="{INK}" stroke-width="2.2"/>'
            f'<line x1="{x + length:.1f}" y1="{y - 5}" x2="{x + length:.1f}" y2="{y + 5}" stroke="{INK}" stroke-width="2.2"/>'
            f'<text x="{x + length / 2:.1f}" y="{y - 6}" font-family="sans-serif" font-size="10" font-weight="bold" fill="{INK}" text-anchor="middle">{label}</text>')


# ------------------------------------------------------------------------------------------------------------------ the circuit unrolled (the side view)
CIRCUIT_FT = 2900.0            # AIP AD 2.22.2: circuit altitude of aeroplanes, feet AMSL
AERODROME_FT = 1870.0          # the aerodrome elevation, feet AMSL
ABOVE_FT = CIRCUIT_FT - AERODROME_FT     # 1 030 ft above the aerodrome
LINE_UP_BEFORE_LIFT = 700.0    # the roll before the lift-off, metres (illustrative)


def profile_knots(path, lift_d=LINE_UP_BEFORE_LIFT):
    """The circuit unrolled: knots (d, h) of the aeroplane's height above the aerodrome (feet) against the distance flown from the line-up (metres), from the marks of the plan's route:
    the roll, the climb that reaches circuit height as the downwind leg begins, level downwind, the descent that begins abeam the threshold (power back), steeper on base, flatter on final,
    touching down at the end of the route. The heights between the marks are illustrative; the 1 030 ft are the AIP's (2 900 less 1 870)."""
    m = path.marks
    top = ABOVE_FT
    c0, c1 = lift_d, lift_d + m["downwind"]
    g = [(0.0, 0.0), (0.22, 0.24), (0.48, 0.52), (0.74, 0.80), (0.92, 0.965), (1.0, 1.0)]
    knots = [(0.0, 0.0), (c0, 0.0)] + [(c0 + (c1 - c0) * f, top * a) for f, a in g[1:]]
    abeam = lift_d + m["downwind"] + (S_S - path.at(m["downwind"])[0][0])
    end = lift_d + m["end"]
    knots.append((abeam, top))
    for u in (0.2, 0.4, 0.6, 0.8):                          # the descent: gentle where the power comes back, steepest through base, flattening as the aeroplane comes to the runway
        eased = u + 0.5 * (u * u * (3 - 2 * u) - u)
        knots.append((abeam + (end - abeam) * u, top * (1.0 - eased)))
    knots.append((end, 0.0))
    return knots


def _pchip(xs, ys):
    """A monotone cubic through the points (Fritsch and Carlson): no overshoot, so a level stretch stays level and nothing dips under the ground. Returns a function of x."""
    k = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(k - 1)]
    delta = [(ys[i + 1] - ys[i]) / h[i] for i in range(k - 1)]
    d = [0.0] * k
    for i in range(1, k - 1):
        if delta[i - 1] * delta[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            d[i] = (w1 + w2) / (w1 / delta[i - 1] + w2 / delta[i])

    def end(h0, h1, d0, d1):
        e = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
        if e * d0 <= 0:
            return 0.0
        if d0 * d1 <= 0 and abs(e) > 3 * abs(d0):
            return 3 * d0
        return e
    d[0] = end(h[0], h[1], delta[0], delta[1]) if k > 2 else delta[0]
    d[-1] = end(h[-1], h[-2], delta[-1], delta[-2]) if k > 2 else delta[-1]

    def f(x):
        i = 0
        while i < k - 2 and x > xs[i + 1]:
            i += 1
        u = (x - xs[i]) / h[i]
        h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
        return h00 * ys[i] + h10 * h[i] * d[i] + h01 * ys[i + 1] + h11 * h[i] * d[i + 1]
    return f


class Profile:
    """The frame of the unrolled circuit: the distance flown d (metres from the line-up) is put on the page by the smooth monotone map through `xmap` [(d, x), ...] (the legs are drawn to
    comparable lengths; the climb and the descent are not to scale), the height h (feet above the aerodrome) at page y = gy - vs h; the curve is a monotone cubic through the knots."""

    def __init__(self, xmap, gy, vs, knots, step=25.0):
        self.xmap, self.gy, self.vs = xmap, gy, vs
        self.xf = _pchip([k[0] for k in xmap], [k[1] for k in xmap])
        hf = _pchip([k[0] for k in knots], [k[1] for k in knots])
        self.end = knots[-1][0]
        self.hf = hf
        d, pts_ = 0.0, []
        while d < self.end:
            pts_.append((self.x(d), self.gy - hf(d) * vs))
            d += step
        pts_.append((self.x(self.end), self.gy - hf(self.end) * vs))
        self.curve = pts_

    def x(self, d):
        m = self.xmap
        if d <= m[0][0]:
            return m[0][1]
        if d >= m[-1][0]:
            return m[-1][1]
        return self.xf(d)

    def y_of_h(self, h):
        return self.gy - h * self.vs

    def point(self, d):
        d = max(0.0, min(self.end, d))
        return self.x(d), self.gy - self.hf(d) * self.vs

    def slope(self, d, span=140.0):
        """The angle of the curve at d in degrees on the page (down is positive)."""
        a, b = self.point(max(0.0, d - span)), self.point(min(self.end, d + span))
        return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

    def unit(self, d, span=140.0):
        a, b = self.point(max(0.0, d - span)), self.point(min(self.end, d + span))
        m = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        return (b[0] - a[0]) / m, (b[1] - a[1]) / m


def route_curve(prof, d0=0.0, d1=None, step=60.0):
    """The points of the profile curve from distance d0 to d1 (page coordinates), for a ribbon."""
    d1 = prof.end if d1 is None else d1
    out, d = [], d0
    while d < d1:
        out.append(prof.point(d))
        d += step
    out.append(prof.point(d1))
    return out


def bracket(x, y0, y1, w=6.0, colour=INK, sw=1.3):
    """A vertical bracket from y0 down to y1 opening to the right (a dimension of height), on a pale casing."""
    d = f"M {n(x + w)} {n(y0)} L {n(x)} {n(y0)} L {n(x)} {n(y1)} L {n(x + w)} {n(y1)}"
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="{n(sw + 2.4)}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{n(sw)}" stroke-linecap="round" stroke-linejoin="round"/>')


def label(x, y, text, size=11.5, anchor="middle", colour=INK, weight="bold", halo=True):
    stroke = ' stroke="#FFFFFF" stroke-width="3.2" stroke-opacity="0.85" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return f'<text x="{n(x)}" y="{n(y)}" font-family="sans-serif" font-size="{n(size)}" font-weight="{weight}" fill="{colour}" text-anchor="{anchor}"{stroke}>{text}</text>'


def air_under(uid, page_pts, y_bottom, colour="#FFFFFF", top_op=0.30, bottom_op=0.04):
    """A faint veil of light between the route and the ground (the volume of air the circuit flies through): a polygon under the curve with a vertical gradient."""
    poly = list(page_pts) + [(page_pts[-1][0], y_bottom), (page_pts[0][0], y_bottom)]
    top = min(y for _, y in page_pts)
    return (f'<defs>{S.gradient(uid, [(0, colour, top_op), (1, colour, bottom_op)], 0, top, 0, y_bottom, "userSpaceOnUse")}</defs>'
            f'<polygon points="{pts(poly)}" fill="url(#{uid})"/>')


def dashed_runs(P, path, colour, w=1.5, dash="5 3.2", casing=1.1):
    """A thin dashed route of the frame whose stretches over the runway strip are drawn thinner and without a casing (a casing wider than the thin route over the runway would show round it)."""
    def over(p):
        return (S_N - STOP_N - 20.0) <= p[0] <= (S_S + STOP_S + 20.0) and abs(p[1]) < 60.0
    runs, cur, flag = [], [], None
    for p in path.pts:
        o = over(p)
        if flag is None or o == flag:
            cur.append(p)
            flag = o
        else:
            cur.append(p)
            runs.append((flag, cur))
            cur, flag = [p], o
    runs.append((flag, cur))
    out = []
    for o, run in runs:
        if len(run) < 2:
            continue
        page = [P.xy(s, t) for s, t in run]
        out.append(dashed_route(page, colour, w=0.9 if o else w, dash=dash, casing=0.1 if o else casing, shadow=not o))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ pieces the two circuit figures share
DOWNWIND = 1000.0              # metres from the runway to the downwind leg (illustrative: the AIP gives no size)
CORNER = 300.0                 # radius of the corners of the circuit, metres (a turn at about 25 degrees of bank at 75 kt)


def unrolled_xmap(path, lift=LINE_UP_BEFORE_LIFT, x0=70.0, x1=598.0):
    """The map from the distance flown (metres from the line-up) to the page for the circuit unrolled: the legs are drawn to comparable lengths, smooth in between."""
    m = path.marks
    abeam = lift + m["downwind"] + (S_S - path.at(m["downwind"])[0][0])
    pts_ = [(0.0, x0), (lift, x0 + 20.0), (lift + m["up_end"], x0 + 160.0), (lift + m["downwind"], x0 + 211.0), (abeam, x0 + 377.0), (lift + m["downwind_end"], x0 + 409.0),
            (lift + m["final"], x0 + 470.0), (lift + m["end"], x1)]
    return pts_, abeam


def construction(P, D=DOWNWIND, radius=34.0, text_at=(20.0, 55.0)):
    """The abeam line and the 45 degree line from the threshold of 35 to the downwind leg, with the arc between them and the 45° in its place (the old figures' grey dashes)."""
    f = P.xy
    thr, abeam, diag = f(S_S, 0.0), f(S_S, D), f(S_S + D, D)
    out = []
    for a, b in (((thr[0], thr[1] + 3), abeam), ((thr[0] + 2, thr[1] + 2), diag)):
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.2" stroke-linecap="round"/>'
                   f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#5B6579" stroke-width="1.15" stroke-dasharray="2.2 3" stroke-linecap="round"/>')
    d = f"M {thr[0]:.1f} {thr[1] + radius:.1f} A {radius} {radius} 0 0 0 {thr[0] + radius * 0.7071:.1f} {thr[1] + radius * 0.7071:.1f}"
    out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.4" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#5B6579" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(f'<text x="{thr[0] + text_at[0]:.1f}" y="{thr[1] + text_at[1]:.1f}" font-family="sans-serif" font-size="12" font-weight="bold" fill="{INK}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.85" paint-order="stroke">45°</text>')
    return "".join(out)


def small_ring(x, y, r=2.7):
    """The small white point of a route (the old figures' white dot with a grey edge)."""
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r + 1.0)}" fill="#FFFFFF" fill-opacity="0.6"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#FFFFFF" stroke="#4B5870" stroke-width="1.2"/>')


def side_scene(uid, box, gy, prof, seed, runways, hangars=True, clouds=()):
    """The card of the unrolled circuit: sky with the sun's glow, hills on the horizon, desert, the runway edge-on at both ends of the route (the left one the whole 4 km of the departure,
    the right one from the threshold on), a pair of hangars at the north end of the first; returns the layers of figs/h_a1.py's profile card."""
    x, y, w, h = box
    objs = A1.runway(uid + "ra", runways[0][0], runways[0][1], gy, half=3.4, centre=True, threshold=True, lights=True, dash_from=runways[0][0] + 12) \
        + A1.runway(uid + "rb", runways[1][0], runways[1][1], gy, half=3.4, centre=True, threshold=True, lights=True)
    if hangars:
        hx = runways[0][1] - 62.0
        objs += A1.hangar(hx, gy - 3.2, 22.0, 11.0) + A1.hangar(hx + 28.0, gy - 3.2, 16.0, 9.0)
    return A1.profile(uid, box, gy, seed=seed, sun=(96, 56), clouds=list(clouds), far=22.0, mid=10.0, base=12.0, objects=objs, radius=14.0,
                      acacias=[(300.0, gy - 5.0, 0.55), (352.0, gy - 4.0, 0.42), (404.0, gy - 6.0, 0.5)], palms=[(268.0, gy - 5.0, 0.5)])
