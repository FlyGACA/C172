"""Figure 18-8 (new in the open-data round: the book had no such figure). The AIP's local procedures at Thumamah (OETH) on a picture of the real country.

The ground is an open satellite picture (Copernicus Sentinel-2, 10 m to the pixel; figs/imagery_real.py; "Contains modified Copernicus Sentinel data 2026") in a flat map round the aerodrome
reference point, true north up, 47 canvas units to the NM: 6.5 km of country to the west of the aerodrome (the red dunes and the highway along them), 18.7 km to the east (the scarp, the plateau
and the East VRP) and 10 km to the north (the North VRP).

Drawn over it, from the AIP (AD 2.17, 2.21 and 2.22, AMDT 11/26), in the words of the page:
  the circuits        runway 35 left-hand, runway 17 right-hand, so both on the west side, 2 900 ft AMSL (the AIP gives no size: here the downwind leg lies 1 NM from the runway, which takes it
                      west of the fenced ground the picture shows where the AIP puts the wildlife reserve)
  departure, runway 35  runway heading to at least 2 600 ft AMSL, then a right turn to the North VRP, climbing to 3 000 ft AMSL
  departure, runway 17  runway heading to at least 2 300 ft AMSL, the right-hand circuit to the downwind leg, and after crossing abeam the numbers of 17 a right turn direct to the North VRP,
                      climbing to 3 000 ft AMSL; no turn to the east after departing runway 17
  arrival from the east   to the East VRP, 3 500 ft AMSL until past the mountain ridge, then down to the circuit altitude, towards mid-field and on to the downwind leg of the runway in use
  arrival from the west   clear of the circuit (west of the Thumamah highway) until a 45 degree entry to the downwind leg of the runway in use
  the ATZ             a circle of 5 NM round the reference point; the wildlife reserve "0.7 NM West of RWY 17/35" (a ring at that distance: the AIP gives no limits)
The arrivals are drawn for runway 35 in use. Where the turns are made, how wide the circuit is and which road the AIP calls the Thumamah highway (here: the highway along the dunes, the only
one west of the aerodrome) are this figure's reading, not the AIP's words: the book says so and asks for a check (its open items). Letters: codes and units only; the rest is numbered."""
import json
import math
import os

from figs import h_b2 as H
from figs import h_b4 as B
from figs import imagery_real as IR
from figs import scene as S

W, HT = 640, 434                                                     # the map (its picture is made at this size)
U = "lp8"
TOPH = 260                                                           # the 3D view above it (the airspace round): the plate is W x (HT + TOPH)
R3D = "oeth-18-08-procedures"
SCALE = 47.0                                                         # canvas units to the NM
OETH = H.DATA["oeth"]
F = H.Frame(OETH["arp"]["lat"], OETH["arp"]["lon"], SCALE, 165.0, 254.0)
assert IR.covers(F, (W, HT)), "the satellite picture does not cover the map"
IR.ensure("terrain-18-08-picture", F, (W, HT), veil=0.2, saturation=0.86, lift=1.05)          # (a name that starts with "terrain-": the ground of a plate, made when its module is read, as figs/terrain.py's)

M = 1852.0
ARP = F.xy(OETH["arp"]["lon"], OETH["arp"]["lat"])
NV, EV = (F.xy(v["lon"], v["lat"]) for v in OETH["vrps"])          # the North VRP and the East VRP


def _thr(rid):
    rw = next(r for r in OETH["runways"] if r["id"] == rid)
    return F.nm(rw["threshold"]["lon"], rw["threshold"]["lat"])


T17, T35 = _thr("17"), _thr("35")
_L = math.hypot(T35[0] - T17[0], T35[1] - T17[1])
UE, UN = (T35[0] - T17[0]) / _L, (T35[1] - T17[1]) / _L             # along the runway from the threshold of 17 to that of 35 (east, north)
WE, WN = UN, -UE                                                     # to the west of it
RWY_M = _L * M


def P(s, t):
    """The canvas point of the runway frame's (s, t): s metres from the threshold of runway 17 towards that of 35, t metres to the west of the centreline (as data/oeth_plan.json)."""
    return F.at(T17[0] + (s * UE + t * WE) / M, T17[1] + (s * UN + t * WN) / M)


def units(metres):
    return metres / M * SCALE


def rounded(points, radius):
    """A polyline with its corners rounded by arcs of `radius` canvas units (shorter where a leg is short)."""
    out = [points[0]]
    for a, b, c in zip(points, points[1:], points[2:]):
        la, lc = H.dist(a, b), H.dist(c, b)
        u1 = ((a[0] - b[0]) / la, (a[1] - b[1]) / la)
        u2 = ((c[0] - b[0]) / lc, (c[1] - b[1]) / lc)
        phi = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1])))
        if phi > math.pi - 0.02:
            out.append(b)
            continue
        d = min(radius / math.tan(phi / 2), la * 0.48, lc * 0.48)
        r = d * math.tan(phi / 2)
        t1 = (b[0] + u1[0] * d, b[1] + u1[1] * d)
        t2 = (b[0] + u2[0] * d, b[1] + u2[1] * d)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        lb = math.hypot(*bis)
        centre = (b[0] + bis[0] / lb * r / math.sin(phi / 2), b[1] + bis[1] / lb * r / math.sin(phi / 2))
        a1 = math.atan2(t1[1] - centre[1], t1[0] - centre[0])
        a2 = math.atan2(t2[1] - centre[1], t2[0] - centre[0])
        sweep = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        count = max(5, int(abs(sweep) * r / 1.2))
        for i in range(count + 1):
            ang = a1 + sweep * i / count
            out.append((centre[0] + r * math.cos(ang), centre[1] + r * math.sin(ang)))
    out.append(points[-1])
    return out


def at_length(points, d):
    (x, y), (dx, dy) = H.along(points, d)
    return (x, y), (dx, dy)


def length(points):
    return sum(H.dist(a, b) for a, b in zip(points, points[1:]))


# ----------------------------------------------------------------------------------------------------- the routes (canvas points)
D35 = 1852.0                                        # the downwind leg of runway 35: 1 NM west of the runway (illustrative: the AIP gives no size)
D17 = D35 + 260.0                                   # that of runway 17 a little further out, so that the two can be told apart
CORNER = 330.0
C35 = B.circuit35(D=D35, R=CORNER)
C17 = B.circuit35(D=D17, R=CORNER).mirrored(B.S_S)
CIRCUIT35 = [P(s, t) for s, t in C35.pts]
CIRCUIT17 = [P(s, t) for s, t in C17.pts]
BLUE = (B.BLUE, B.BLUE_MID, B.BLUE_HI)
DEP = ("#A21CAF", "#C63BD3", "#F3C6F8")              # the departures (a cool colour: the ground is orange)
ARR = ("#047857", "#12A37B", "#A7F3D0")              # the arrivals
TURN_35 = -2000.0                                   # where the departure of runway 35 is drawn turning: about 1 NM beyond the end (illustrative; the AIP gives a height, 2 600 ft AMSL, not a place)
DEP35 = rounded([P(1400.0, 0.0), P(TURN_35, 0.0), NV], units(650.0))
_m17 = C17.marks
DEP17 = ([P(s, t) for s, t in C17.piece(0.0, _m17["downwind"])]
         + rounded([P(B.S_S - (-700.0) - CORNER, D17), P(-420.0, D17), NV], units(650.0))[1:])      # along the circuit of 17 to its downwind leg, past abeam the numbers of 17, then direct to the North VRP
JOIN_E, JOIN_W = 2050.0, 1250.0                     # where the two arrivals reach the downwind leg of runway 35 (metres from the threshold of 17)
ARR_EAST = rounded([EV, P(JOIN_E, D35), P(JOIN_E + 2300.0, D35)], units(CORNER))
ARR_WEST = rounded([P(JOIN_W - 4700.0, D35 + 4700.0), P(JOIN_W, D35), P(JOIN_W + 520.0, D35)], units(CORNER))
RESERVE = P(1000.0, 0.7 * M)                         # the AIP: "0.7 NM West of RWY 17/35"; along the runway, abeam the round enclosure the picture shows at that distance (1 000 m from the threshold of 17)
RESERVE_R = units(400.0)
ATZ = H.circle(ARP[0], ARP[1], F.r(OETH["atz"]["radius_nm"]))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "oeth_area.json"), encoding="utf-8") as _f:
    HIGHWAY = [F.xy(lon, lat) for lat, lon in json.load(_f)["highway_west_lat_lon"]]      # the highway along the dunes, read off the same picture (data/build_oeth_area.py)
RIDGE = (468.6, 257.4)                              # where the arrival from the east passes the edge of the plateau (figs/terrain_real.py: the ground falls from about 2 540 to 2 030 ft there)
MIDFIELD = None                                     # where it crosses the runway: worked out below


def _cross(p0, p1, q0, q1):
    """Where the line p0 p1 meets the line q0 q1."""
    d1, d2 = (p1[0] - p0[0], p1[1] - p0[1]), (q1[0] - q0[0], q1[1] - q0[1])
    k = ((q0[0] - p0[0]) * d2[1] - (q0[1] - p0[1]) * d2[0]) / (d1[0] * d2[1] - d1[1] * d2[0])
    return (p0[0] + d1[0] * k, p0[1] + d1[1] * k)


MIDFIELD = _cross(EV, P(JOIN_E, D35), P(0.0, 0.0), P(RWY_M, 0.0))


def thin(points, colours, w=2.6, casing=1.1):
    return B.ribbon_line(points, w=w, base=colours[0], mid=colours[1], hi=colours[2], casing=casing)


def heads(points, at, colour, ln=8.6, wd=9.0):
    out = []
    for d in at:
        (x, y), (dx, dy) = at_length(points, d)
        out.append(B.head(x + dx * ln * 0.5, y + dy * ln * 0.5, dx, dy, ln, wd, colour))
    return "".join(out)


def end_head(points, colour, ln=10.5, wd=10.5):
    (x, y), (dx, dy) = at_length(points, length(points))
    return B.head(x + dx * ln * 0.55, y + dy * ln * 0.55, dx, dy, ln, wd, colour)


def circuits():
    out = [B.dashed_route(CIRCUIT17, B.BLUE, w=1.5, dash="4.6 3.2", casing=1.0, shadow=False),
           heads(CIRCUIT17, [C17.marks["base_start"] / C17.length * length(CIRCUIT17) + 6.0], B.BLUE, 5.8, 6.2),
           thin(CIRCUIT35, BLUE, w=2.3, casing=1.0),
           heads(CIRCUIT35, [length(CIRCUIT35) * 0.47, length(CIRCUIT35) * 0.86], B.BLUE, 7.0, 7.4)]
    return "".join(out)


def departures():
    out = [B.dashed_route(DEP17, DEP[0], w=2.2, dash="6.5 3.6", casing=1.15),
           heads(DEP17, [length(DEP17) * 0.2, length(DEP17) * 0.47, length(DEP17) * 0.8], DEP[0], 7.6, 8.0),
           thin(DEP35, DEP, w=3.0, casing=1.2),
           heads(DEP35, [length(DEP35) * 0.3, length(DEP35) * 0.72], DEP[0], 8.4, 8.8)]
    return "".join(out)


def no_turn_east():
    """After a takeoff from runway 17: a short arrow that turns to the east, struck out."""
    p = rounded([P(B.S_S + 620.0, 0.0), P(B.S_S + 1500.0, 0.0), P(B.S_S + 1500.0 - 250.0, -1500.0)], units(520.0))
    cx, cy = at_length(p, length(p) * 0.74)[0]
    r = 7.2
    return (B.dashed_route(p, "#7F1D1D", w=1.7, dash="3.6 2.8", casing=1.0, shadow=False) + end_head(p, "#7F1D1D", 7.0, 7.2)
            + f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{r + 1.5}" fill="#FFFFFF" filter="url(#{U}ds)"/>'
            f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{r}" fill="#FFFFFF" stroke="#C81E1E" stroke-width="2.2"/>'
            f'<line x1="{S.n(cx - r * 0.7)}" y1="{S.n(cy - r * 0.7)}" x2="{S.n(cx + r * 0.7)}" y2="{S.n(cy + r * 0.7)}" stroke="#C81E1E" stroke-width="2.2" stroke-linecap="round"/>')


def arrivals():
    out = [thin(ARR_WEST, ARR, w=2.8, casing=1.2), heads(ARR_WEST, [length(ARR_WEST) * 0.3, length(ARR_WEST) * 0.72], ARR[0], 8.2, 8.6),
           thin(ARR_EAST, ARR, w=2.8, casing=1.2), heads(ARR_EAST, [length(ARR_EAST) * 0.14, length(ARR_EAST) * 0.42, length(ARR_EAST) * 0.9], ARR[0], 8.2, 8.6)]
    # the 45 degree mark between the entry and the downwind leg
    j = P(JOIN_W, D35)
    a0 = math.atan2(P(JOIN_W - 1000.0, D35)[1] - j[1], P(JOIN_W - 1000.0, D35)[0] - j[0])
    a1 = math.atan2(ARR_WEST[0][1] - j[1], ARR_WEST[0][0] - j[0])
    rr = 19.0
    arc = [(j[0] + rr * math.cos(a0 + (a1 - a0) * i / 10), j[1] + rr * math.sin(a0 + (a1 - a0) * i / 10)) for i in range(11)]
    out.append(f'<polyline points="{S.pts(arc)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.2" stroke-linecap="round"/>'
               f'<polyline points="{S.pts(arc)}" fill="none" stroke="{B.INK}" stroke-width="1.2" stroke-linecap="round"/>')
    return "".join(out)


def highway():
    """The highway west of the aerodrome as a road of a map: a dark line in a pale casing over the line the picture shows."""
    line = S.pts(HIGHWAY)
    return (f'<polyline points="{line}" fill="none" stroke="#FFF7E0" stroke-opacity="0.85" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<polyline points="{line}" fill="none" stroke="#3A3F4A" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<polyline points="{line}" fill="none" stroke="#F4E3A1" stroke-width="0.35" stroke-dasharray="2.6 2.2" stroke-linecap="round"/>')


def reserve():
    """The wildlife reserve of AD 2.21: a ring where the AIP puts it, hatched (the AIP gives a distance from the runway and no limits)."""
    x, y = RESERVE
    return (f'<circle cx="{S.n(x)}" cy="{S.n(y)}" r="{S.n(RESERVE_R)}" fill="url(#{U}hatch)" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.0"/>'
            f'<circle cx="{S.n(x)}" cy="{S.n(y)}" r="{S.n(RESERVE_R)}" fill="none" stroke="#C81E1E" stroke-width="1.3" stroke-dasharray="3 2.2"/>')


def marks():
    out = [H.runway(U, P(0.0, 0.0), P(RWY_M, 0.0), 3.0), H.vrp(U, *NV, 11.5), H.vrp(U, *EV, 11.5)]
    # the arrival from the east: a tick where it passes the ridge, a ring where it crosses the runway at mid-field
    out.append(f'<line x1="{S.n(RIDGE[0])}" y1="{S.n(RIDGE[1] - 6.5)}" x2="{S.n(RIDGE[0])}" y2="{S.n(RIDGE[1] + 6.5)}" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="4.2" stroke-linecap="round"/>'
               f'<line x1="{S.n(RIDGE[0])}" y1="{S.n(RIDGE[1] - 6.5)}" x2="{S.n(RIDGE[0])}" y2="{S.n(RIDGE[1] + 6.5)}" stroke="{B.INK}" stroke-width="1.8" stroke-linecap="round"/>')
    out.append(B.ring(MIDFIELD[0], MIDFIELD[1], r=3.4, sw=1.5))
    out.append(H.label("17", P(-330.0, -420.0)[0], P(-330.0, -420.0)[1], 5.6, H.INK, spacing=0.3))
    out.append(H.label("35", P(RWY_M + 330.0, -420.0)[0], P(RWY_M + 330.0, -420.0)[1], 5.6, H.INK, spacing=0.3))
    return "".join(out)


def altitudes():
    """The altitudes the AIP gives, where they apply: digits and the foot."""
    lab = lambda text, x, y, anchor="middle": B.label(x, y, text, 9.6, anchor)
    turn = P(TURN_35, 0.0)
    below = P(B.S_S + 1500.0, 720.0)
    out = [lab("2\u2009600 ft", turn[0] + 10.0, turn[1] + 5.0, "start"),
           lab("3\u2009000 ft", NV[0] - 15.0, NV[1] + 24.0, "end"),
           lab("2\u2009300 ft", below[0], below[1] + 3.0),
           lab("3\u2009500 ft", (EV[0] + RIDGE[0]) / 2, EV[1] - 8.0),
           lab("2\u2009900 ft", 344.0, 252.0),
           lab("45\u00b0", P(JOIN_W, D35)[0] - 25.0, P(JOIN_W, D35)[1] - 3.0)]
    return "".join(out)


def sprites():
    spr = {"shadow": {"dx": 1.6, "dy": 2.4, "blur": 1.6, "opacity": 0.4}, "outline": {"width": 0.45, "colour": "#2B3648", "opacity": 0.9}}
    out = []
    for points, frac, width in ((DEP35, 0.56, 23.0), (ARR_EAST, 0.6, 23.0), (ARR_WEST, 0.5, 21.0)):
        (x, y), (dx, dy) = at_length(points, length(points) * frac)
        out.append({"name": "sprite-top", "at": [round(x, 1), round(y, 1)], "width": width, "angle": round(math.degrees(math.atan2(dx, -dy)), 1), **spr})
    return out


def rim(centre, toward, r):
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


def callouts():
    c = S.callout
    out = []
    out.append(c(1, 228.0, 308.0, *P(3350.0, -40.0), r=10))                                          # the runway (and the circuits west of it)
    out.append(c(2, 228.0, 114.0, *H.lerp(P(TURN_35, 0.0), NV, 0.42), r=10))                         # the departure of runway 35
    out.append(c(3, 70.0, 158.0, *H.lerp(P(-420.0, D17), NV, 0.11), r=10))                           # the departure of runway 17
    turn_e = P(B.S_S + 1500.0 - 180.0, -1050.0)
    out.append(c(4, 240.0, 358.0, turn_e[0] + 9.0, turn_e[1] + 3.0, r=10))                           # no turn to the east
    out.append(c(5, 286.0, 40.0, *rim(NV, (286.0, 40.0), 7.0), r=10))                                # the North VRP
    out.append(c(6, 612.0, 226.0, *rim(EV, (612.0, 226.0), 7.0), r=10))                              # the East VRP
    out.append(c(7, 450.0, 214.0, RIDGE[0] - 1.0, RIDGE[1] - 9.5, r=10))                             # the ridge
    out.append(c(8, 246.0, 276.0, *rim(MIDFIELD, (246.0, 276.0), 4.6), r=10))                        # mid-field
    hw = H.lerp(HIGHWAY[6], HIGHWAY[7], 0.2)
    out.append(c(9, 34.0, 304.0, hw[0] - 1.5, hw[1] + 1.5, r=10))                                    # the highway
    (ex, ey), _ = at_length(ARR_WEST, length(ARR_WEST) * 0.2)
    out.append(c(10, 32.0, 150.0, ex, ey - 2.0, r=10))                                               # the 45 degree entry
    out.append(c(11, 210.0, 224.0, *rim(RESERVE, (210.0, 224.0), RESERVE_R), r=10))                  # the wildlife reserve
    out.append(c(12, 426.0, 320.0, *rim(ARP, (426.0, 320.0), ATZ["r"]), r=10))                       # the edge of the ATZ
    return "".join(out)


def top3d():
    """The 3D view: the procedures at their heights over the ground (figs/oeth3d.procedures_18_08); callout 4 (no turn to the east) is in the map only."""
    from figs import panel3d as P3

    def marks(at):
        return H.vrp(U, *at("nv"), 10.0) + H.vrp(U, *at("ev"), 10.0)
    return P3.panel(R3D, (8.0, 8.0, 624.0, TOPH - 16.0), 0.62, U, CALLOUTS_3D, marks=marks)


CALLOUTS_3D = [(1, "rwy", 196.0, 200.0), (2, "dep35", 215.0, 34.0), (3, "dep17", 140.0, 34.0), (5, "nv", 302.0, 40.0), (6, "ev", 592.0, 172.0), (7, "ridge", 440.0, 32.0),
               (8, "mid", 252.0, 150.0), (9, "hw", 40.0, 190.0), (10, "entry", 40.0, 40.0), (11, "reserve", 120.0, 206.0), (12, "atz", 300.0, 228.0)]


def layers():
    from figs import panel3d as P3
    return [*top3d(), *P3.below(map_layers(), TOPH)]


def map_layers():
    out = [H.defs(U, W, HT), B.defs(), {"name": "terrain-18-08-picture", "at": [W / 2, HT / 2], "width": W}, H.vignette(U, W, HT, 0.12),
           H.edge(ATZ, "G", dash="8 4.5", width=1.7, uid=U), highway(), reserve(), circuits(), departures(), no_turn_east(), arrivals(), marks(), *sprites(), altitudes(),
           H.north_arrow(U, 612, 60, 30), H.scale_bar(U, 506, 408, 2 * SCALE, nm_total=2, segments=2, text="2 NM"), callouts()]
    return out


def plate():
    return {
        "id": "fig-18-08-local-procedures",
        "replaces": "fig-18-08-local-procedures.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-18-08-local-procedures.jpg",
        "caption": "Figure 18-8. The published procedures of Thumamah: departures, arrivals and the two circuits",
        "desc": ("Figure 18-8. The published procedures of Thumamah: departures, arrivals and the two circuits. Above, in 3D from the south-south-west at their heights over the ground "
                 "(heights, the ground's too, enlarged four times); below, the map, north up. The procedures are the AIP's (AD 2.22, AMDT 11/26); where the turns are "
                 "made and how wide the circuits are is illustrative. The ground is an open satellite picture (contains modified Copernicus Sentinel data 2026); not for navigation."),
        "legend": [
            "Runway 17/35 and its circuits, both west of the runway at 2 900 ft AMSL: left-hand for runway 35 (solid blue), right-hand for runway 17 (dashed).",
            "Departure from runway 35: runway heading to at least 2 600 ft AMSL, then a right turn to the North VRP, climbing to 3 000 ft AMSL.",
            "Departure from runway 17: runway heading to at least 2 300 ft AMSL, round the right-hand circuit to the downwind leg and, once abeam the numbers of runway 17, a right turn direct to the North VRP, climbing to 3 000 ft AMSL.",
            "After taking off from runway 17, no turn to the east: the AIP tells pilots not to accept a clearance that includes one.",
            "The North VRP, where the valley ends.",
            "The East VRP, a road intersection with two telecom towers: an arrival from the east keeps 3 500 ft AMSL from here.",
            "The mountain ridge: past it the arrival descends to the circuit altitude, 2 900 ft AMSL.",
            "Near mid-field: look for traffic in the circuit, then cross the runway at circuit altitude and join the downwind leg of the runway in use (drawn for runway 35).",
            "The highway west of the aerodrome: an arrival from the west stays west of it, clear of the circuit.",
            "The 45° entry to the downwind leg.",
            "The wildlife reserve 0.7 NM west of the runway, which pilots are asked not to overfly; the AIP gives no limits for it.",
            "The edge of the ATZ, 5 NM from the aerodrome reference point.",
        ],
        "canvas": [W, HT + TOPH],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
