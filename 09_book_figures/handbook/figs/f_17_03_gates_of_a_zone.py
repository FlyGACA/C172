"""Figure 17-3 (new: the book says it in one sentence of a box). The gates of a control zone: how a VFR flight enters and leaves the Jeddah zone, and which unit it calls at which point.

One map, true north up, 13.4 canvas units to the NM, on an open satellite picture of Jeddah, its coast and the sea (Copernicus Sentinel-2, 30 m to the pixel; figs/imagery_real.py;
"Contains modified Copernicus Sentinel data 2026"). Everything drawn over it is the AIP's (AD 2 OEJN, AMDT 11/26; data/saudi_airspace.json):
  the zone           AD 2.17: JEDDAH CTR, a circle of 10 NM round the aerodrome reference point, SFC to 2 500 ft AMSL, Class D, Jeddah Tower, H24
  the runways        AD 2.12: 16R/34L, 16C/34C and 16L/34R between their thresholds
  the points         AD 2.22.12: VRP01 to VRP13 (there is no VRP07) at their printed coordinates, and what the same paragraph says of them: entry and exit to and from the zone by
                     VRP01, VRP05, VRP06 and VRP13, with Jeddah Approach called 10 NM before them; flights by VRP02, VRP03, VRP04 and VRP12 call Jeddah Tower East, flights by
                     VRP08, VRP09, VRP10 and VRP11 Jeddah Tower West
  the frequencies    AD 2.18 and the Visual Approach Chart (AD 2 OEJN - 205): approach 124.000 MHz, tower west 118.200 MHz, tower east 118.500 MHz (AD 2.22.11 names it too)
  the route          AD 2.22.11: the urban VFR route JDW1, VRP06 - AZIZI - VRP01 - KHOAR - ..., at most 500 ft above the ground; from AZIZI to VRP01 it crosses the zone, with a
                     clearance from Tower East asked for before entering. It is drawn as straight lines between the AIP's points (the AIP gives the points, not the track; its own
                     chart of the route was not seen), as far as the edge of the map towards KHOAR
The four gates lie outside the circle (11.3 to 15.1 NM from the reference point) and the eight other points inside it: worked out from the coordinates, not printed. AZIZI stands
at its printed coordinates, which lie 3 NM from where its printed bearing and distance put it (the facts file records it).
The key lies on the sea: for each of the three units the marker of its points, its sign and its frequency. Letters: the names of the points and of the route, frequencies,
the class letter, units and the location indicator; the rest is numbered."""
import math

from figs import h_b2 as H
from figs import h_b4 as B
from figs import imagery_real as IR
from figs import scene as S

n = S.n
W, HT = 640, 440
U = "jg3"
SCALE = 13.4                                         # canvas units to the NM
OEJN = H.DATA["oejn"]
ARP_LL = (OEJN["arp"]["lat"], OEJN["arp"]["lon"])
F = H.Frame(ARP_LL[0], ARP_LL[1], SCALE, 400.0, 220.0)
assert IR.covers(F, (W, HT), picture="oejn_area_s2"), "the satellite picture does not cover the map"
IR.ensure("terrain-17-03-jeddah", F, (W, HT), veil=0.08, saturation=0.95, lift=1.03, picture="oejn_area_s2", deep=(36, 78, 128))
ARP = F.xy(ARP_LL[1], ARP_LL[0])
POINTS = {p["id"]: p for p in OEJN["points"]}
XY = {k: F.xy(p["lon"], p["lat"]) for k, p in POINTS.items()}
GROUP = {"approach": [k for k, p in POINTS.items() if p["contact"] == "approach"], "tower_east": [k for k, p in POINTS.items() if p["contact"] == "tower_east"],
         "tower_west": [k for k, p in POINTS.items() if p["contact"] == "tower_west"]}
assert GROUP == {"approach": ["VRP01", "VRP05", "VRP06", "VRP13"], "tower_east": ["VRP02", "VRP03", "VRP04", "VRP12"], "tower_west": ["VRP08", "VRP09", "VRP10", "VRP11"]}
assert all(not POINTS[k]["inside_ctr_derived"] for k in GROUP["approach"]) and all(POINTS[k]["inside_ctr_derived"] for k in GROUP["tower_east"] + GROUP["tower_west"])
MHZ = {k: f'{OEJN["comms"][k]["mhz"]:.3f}' for k in ("approach", "tower_east", "tower_west")}
assert MHZ == {"approach": "124.000", "tower_east": "118.500", "tower_west": "118.200"}
COLOUR = {"approach": "#E8B923", "tower_east": "#1E5FB3", "tower_west": "#A8327A"}       # the gates amber (the book's reporting points), the east blue, the west magenta
DARK = {"approach": "#8A6A00", "tower_east": "#123C78", "tower_west": "#6E1B4E"}
ROUTE_MAX = OEJN["vfr"]["uvr"]["max_ft_agl"]
assert OEJN["vfr"]["uvr"]["JDW1"][:4] == ["VRP06", "AZIZI", "VRP01", "KHOAR"] and ROUTE_MAX == 500


def zone():
    return H.poly(F.ring(H.DATA["areas"]["oejn_ctr_ring"]))


def airspace():
    z = zone()
    return H.fill(z, "D", opacity=0.2) + H.inner_glow(U, z, "D", width=10.0, opacity=0.3) + H.edge(z, "D", dash="none", width=2.2, casing=4.6, uid=U)


def thresholds(a, b):
    ta, tb = (next(r for r in OEJN["runways"] if r["id"] == rid)["threshold"] for rid in (a, b))
    return F.xy(ta["lon"], ta["lat"]), F.xy(tb["lon"], tb["lat"])


RUNWAYS = [thresholds(a, b) for a, b in (("16R", "34L"), ("16C", "34C"), ("16L", "34R"))]


def runways():
    return "".join(H.runway(U, p0, p1, 2.0) for p0, p1 in RUNWAYS) + H.label("OEJN", ARP[0] + 2.0, ARP[1] + 27.0, 5.6, H.INK, spacing=0.3)


def marker(x, y, kind, size=10.0):
    """A reporting point in the colour of the unit its flights call; a gate is larger and stands in a ring."""
    h = size * (1.2 if kind == "approach" else 1.0)
    w = h * 1.06
    p = [(x, y - h * 0.62), (x + w * 0.5, y + h * 0.38), (x - w * 0.5, y + h * 0.38)]
    out = ""
    if kind == "approach":
        out += (f'<circle cx="{n(x)}" cy="{n(y - h * 0.06)}" r="{n(h * 0.98)}" fill="#FFFFFF" fill-opacity="0.5" stroke="#FFFFFF" stroke-width="2.6" filter="url(#{U}ds)"/>'
                f'<circle cx="{n(x)}" cy="{n(y - h * 0.06)}" r="{n(h * 0.98)}" fill="none" stroke="{DARK[kind]}" stroke-width="1.1"/>')
    return (out + f'<polygon points="{S.pts(p)}" fill="{COLOUR[kind]}" stroke="#FFFFFF" stroke-width="1.7" stroke-linejoin="round" filter="url(#{U}ds)"/>'
            f'<polygon points="{S.pts(p)}" fill="none" stroke="{DARK[kind]}" stroke-opacity="0.7" stroke-width="0.5" stroke-linejoin="round"/>')


NAME_AT = {"VRP01": (19.0, -8.0, "start"), "VRP02": (9.0, -6.0, "start"), "VRP03": (9.5, 0.5, "start"), "VRP04": (-9.5, 2.0, "end"), "VRP05": (-15.0, -4.0, "end"), "VRP06": (-15.0, 7.0, "end"),
           "VRP08": (-9.5, 2.0, "end"), "VRP09": (-9.5, 1.0, "end"), "VRP10": (-9.5, 2.0, "end"), "VRP11": (-8.0, -8.0, "end"), "VRP12": (5.0, -10.5, "start"), "VRP13": (-15.0, -4.0, "end"),
           "AZIZI": (8.0, 5.0, "start")}                        # where each name stands, from its point


def points():
    out = []
    for kind in ("tower_west", "tower_east", "approach"):
        for k in GROUP[kind]:
            x, y = XY[k]
            dx, dy, anchor = NAME_AT[k]
            out.append(marker(x, y, kind) + H.label(k, x + dx, y + dy, 5.7, H.INK, anchor=anchor, spacing=0.25, halo=2.6))
    return "".join(out)


def route_points():
    """VRP06 - AZIZI - VRP01 and on towards KHOAR, as far as the top of the map."""
    a, b, c = XY["VRP06"], XY["AZIZI"], XY["VRP01"]
    k = XY["KHOAR"]
    t = (6.0 - c[1]) / (k[1] - c[1])                          # where the leg to KHOAR leaves the picture
    return [a, b, c, (c[0] + (k[0] - c[0]) * t, 6.0)]


GATE_R = 12.6                                                 # the ring of a gate: the route stops at it


def toward(a, b, d):
    k = d / H.dist(a, b)
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def route():
    pts = route_points()
    a, b, c, e = pts
    out = []
    for run in ([toward(a, b, GATE_R), b, toward(c, b, GATE_R)], [toward(c, e, GATE_R), e]):
        pl = S.pts(run)
        out += [f'<polyline points="{pl}" fill="none" stroke="#FFFFFF" stroke-opacity="0.92" stroke-width="4.2" stroke-dasharray="6.5 4" stroke-linecap="round" stroke-linejoin="round" filter="url(#{U}ds)"/>',
                f'<polyline points="{pl}" fill="none" stroke="{H.INK}" stroke-width="1.9" stroke-dasharray="6.5 4" stroke-linecap="round" stroke-linejoin="round"/>']
    x, y = XY["AZIZI"]
    dx, dy, anchor = NAME_AT["AZIZI"]
    out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="3.9" fill="#FFFFFF" stroke="{H.INK}" stroke-width="1.6" filter="url(#{U}ds)"/>' + H.label("AZIZI", x + dx, y + dy, 5.7, H.INK, anchor=anchor, spacing=0.25, halo=2.6))
    b, c = pts[1], pts[2]
    turn = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0])) + 180.0                     # the name reads up the leg, from the south
    at = H.lerp(b, c, 0.60)
    off = (math.cos(math.radians(turn - 90)) * -8.6, math.sin(math.radians(turn - 90)) * -8.6)
    out.append(f'<g transform="rotate({n(turn + 180)} {n(at[0] + off[0])} {n(at[1] + off[1])})">' + H.label("JDW1", at[0] + off[0], at[1] + off[1], 6.0, H.INK, spacing=0.4, halo=2.6) + "</g>")
    return "".join(out)


def pill(x, y, text, wide, colour="#101B33"):
    """Digits and a unit on a dark plate."""
    return (f'<rect x="{n(x - wide / 2)}" y="{n(y - 8.2)}" width="{n(wide)}" height="16.4" rx="8.2" fill="{colour}" fill-opacity="0.84" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="0.8" filter="url(#{U}ds)"/>'
            f'<text x="{n(x)}" y="{n(y + 3.2)}" font-family="sans-serif" font-size="8.6" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{text}</text>')


ROUTE_PILL = (559.0, 369.0)
ZONE_DISC = (318.0, 236.0)


def limits():
    out = [H.class_disc(U, ZONE_DISC[0], ZONE_DISC[1], "D", 10.5), pill(ZONE_DISC[0], ZONE_DISC[1] + 22.0, "≤ 2 500 ft AMSL", 84.0, colour="#123C78")]
    out.append(pill(ROUTE_PILL[0], ROUTE_PILL[1], f"≤ {ROUTE_MAX} ft AGL", 74.0))
    return "".join(out)


KEY_X, KEY_W = 14.0, 206.0
KEY_ROWS = {"approach": 138.0, "tower_east": 222.0, "tower_west": 270.0}          # the top of each card
KEY_H = {"approach": 72.0, "tower_east": 40.0, "tower_west": 40.0}


def card(kind):
    x, y, h = KEY_X, KEY_ROWS[kind], KEY_H[kind]
    out = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(KEY_W)}" height="{n(h)}" rx="13" fill="#101B33" fill-opacity="0.8" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.8" filter="url(#{U}ds)"/>']
    cy = y + 20.0
    out.append(marker(x + 24.0, cy + 1.5, kind, size=12.0))
    if kind == "approach":
        out.append(H.radar(U, x + 62.0, cy, 12.5))
    else:
        out.append(H.tower_icon(U, x + 62.0, cy, 12.5, colour=COLOUR[kind]))
    out.append(H.glyph_text(MHZ[kind], x + 86.0, cy, 11.0, "#FFFFFF", spacing=0.7, anchor="start"))
    if kind == "approach":                                                   # ten miles before the gate: an aeroplane, the distance, the gate
        ly = y + 53.0
        x0, x1 = x + 52.0, x + 168.0
        out.append(f'<line x1="{n(x0)}" y1="{n(ly)}" x2="{n(x1)}" y2="{n(ly)}" stroke="#FFFFFF" stroke-width="1.2" stroke-dasharray="3.2 2.6" stroke-linecap="round"/>')
        for xx in (x0, x1):
            out.append(f'<line x1="{n(xx)}" y1="{n(ly - 5)}" x2="{n(xx)}" y2="{n(ly + 5)}" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round"/>')
        mid = (x0 + x1) / 2
        out.append(f'<rect x="{n(mid - 21)}" y="{n(ly - 7)}" width="42" height="14" rx="7" fill="#101B33"/>' + H.glyph_text("10 NM", mid, ly, 7.2, "#FFFFFF", spacing=0.5))
        out.append(marker(x1 + 15.0, ly + 1.2, kind, size=8.6))
    return "".join(out)


def key_plane():
    """The aeroplane of the approach card, ten miles out and flying towards the gate."""
    return {"name": "sprite-top", "at": [KEY_X + 36.0, KEY_ROWS["approach"] + 53.0], "width": 21, "angle": 90.0, "outline": {"width": 0.5, "colour": "#FFFFFF", "opacity": 0.9}}


def furniture():
    return H.north_arrow(U, 34.0, 44.0, 28.0) + H.scale_bar(U, 26.0, HT - 26.0, 5 * SCALE, nm_total=5, segments=5, text="5 NM")


def rim(centre, toward, r):
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


def callouts():
    c = S.callout
    out = []
    edge = F.bearing_point(ARP, 236.0, 10.0)
    out.append(c(1, edge[0] - 30.0, edge[1] + 30.0, edge[0], edge[1], r=10))                           # the zone
    mid = H.lerp(*RUNWAYS[2], 0.3)
    out.append(c(2, mid[0] + 34.0, mid[1] - 22.0, mid[0] + 2.0, mid[1] - 1.0, r=10))                   # the runways
    g = XY["VRP13"]
    out.append(c(3, g[0] - 6.0, g[1] - 40.0, *rim((g[0], g[1] - 0.7), (g[0] - 6.0, g[1] - 40.0), 12.0), r=10))        # a gate
    r4 = (KEY_X + 62.0, KEY_ROWS["approach"] + 20.0)
    out.append(c(4, r4[0] + 10.0, r4[1] - 40.0, *rim(r4, (r4[0] + 10.0, r4[1] - 40.0), 12.5), r=10))   # approach, ten miles before the gate
    e = XY["VRP04"]
    out.append(c(5, e[0] - 25.0, e[1] + 24.0, e[0] - 3.6, e[1] + 4.2, r=10))                           # the points of tower east
    w = XY["VRP08"]
    out.append(c(6, w[0] - 14.0, w[1] + 36.0, w[0] - 2.0, w[1] + 5.0, r=10))                           # the points of tower west
    pts = route_points()
    at = H.lerp(pts[1], pts[2], 0.33)
    out.append(c(7, at[0] + 40.0, at[1] + 12.0, at[0] + 2.0, at[1] + 0.5, r=10))                       # the urban VFR route
    return "".join(out)


def layers():
    out = [H.defs(U, W, HT), {"name": "terrain-17-03-jeddah", "at": [W / 2, HT / 2], "width": W}, airspace(), runways(), route(), points(), limits()]
    out += [card("approach"), key_plane(), card("tower_east"), card("tower_west"), furniture(), callouts()]
    return out


def plate():
    return {
        "id": "fig-17-03-gates-of-a-zone",
        "replaces": "fig-17-03-gates-of-a-zone.svg",           # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-17-03-gates-of-a-zone.jpg",
        "caption": "Figure 17-3. The gates of a control zone: the reporting points of the Jeddah zone, and the unit a VFR flight calls at each",
        "desc": ("Figure 17-3. The gates of a control zone: the reporting points of the Jeddah zone, and the unit a VFR flight calls at each. North is up. The zone, the runways, the points, "
                 "the frequencies and the route are the AIP's (AD 2 OEJN, AMDT 11/26). The ground is an open satellite picture (contains modified Copernicus Sentinel data 2026); not for navigation."),
        "legend": [
            "The Jeddah control zone: a circle of 10 NM round the aerodrome reference point, from the surface to 2 500 ft AMSL, Class D at all hours.",
            "The three parallel runways of King Abdulaziz International (OEJN).",
            "The gates VRP01, VRP05, VRP06 and VRP13, outside the zone: a VFR flight enters the zone and leaves it by one of them.",
            "Jeddah Approach, 124.000 MHz: called 10 NM before a gate.",
            "VRP02, VRP03, VRP04 and VRP12: a flight by these points calls Jeddah Tower East, 118.500 MHz.",
            "VRP08, VRP09, VRP10 and VRP11: a flight by these points calls Jeddah Tower West, 118.200 MHz.",
            "The urban VFR route JDW1, from VRP06 by AZIZI and VRP01 and on to the north-east, not above 500 ft above the ground unless ATC approves a higher altitude. From AZIZI to VRP01 it crosses the zone: the clearance is asked of Jeddah Tower East before entering.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
