"""Figure 17-9. The worked example in profile along the route: the three legs of the worked example (OETH - North VRP - East VRP - OETH, 5.2 + 8.7 + 8.9 = 22.8 NM, data/saudi_airspace.json
`worked_example_route`) unrolled into one line. x is the distance along the route in NM, from 0 to 22.8 (the picture runs from -1.9 to 24.8 so that the runway at each end shows whole); y is the
height above mean sea level in feet, linear, from 1 500 to 5 000. The scale is 574 canvas units to 26.7 NM (21.5 units to the NM) and 330 units to 3 500 ft (94.3 units to 1 000 ft): the
vertical scale is exaggerated (about 27 times against the horizontal one).

What is drawn comes from the file and from open elevation data: the ground under the straight lines between the points is the real ground (NASA SRTM, public domain; figs/terrain_real.py), level
at the aerodrome elevation, 1 870 ft, along the runway at each end: a scarp north of Thumamah that rises to about 2 630 ft, a plateau of 2 350 to 2 560 ft under the two visual reporting points, and
its eastern edge about 2 NM beyond the East VRP on the way back, which is the AIP's "mountain ridge"; the Thumamah ATZ (Class G, 5 NM round the ARP, surface to 3 000 ft), a box where the route is
within 5 NM of the aerodrome, x from 0 to 5 and from 17.8 to 22.8 (the boxes run on beyond the ends of the route: the zone goes on round the aerodrome); the Riyadh terminal control area and final
director area, Class C from 700 ft above the ground, so their floor follows the ground, over the whole route (both rings of the file contain every point of it), interrupted by the ATZ as in Figure
17-1 (the final director area contains the ATZ: the overlap is cross-hatched where its floor is below 3 000 ft); the route as a dark ribbon: runway heading to 2 600 ft (800 ft above the aerodrome), a
right turn to the North VRP (5.2 NM) and a climb to 3 000 ft, level at 3 500 ft from the North VRP to the East VRP (13.9 NM) and on past it until past the ridge, then the descent to the circuit
altitude, 2 900 ft, and the circuit (a thin dashed line at 2 900 ft over the last 5 NM). Two small figures give the highest ground under the route on the way out and on the way back. The AIP lists no
windsock for Thumamah, so none is drawn. The eight numbered callouts are those of the brief's legend (figs/h_b1.py makes the pieces)."""
import math
import re

from figs import h_a1 as A1
from figs import h_b1 as B
from figs import scene as S
from figs import terrain_real as TR

W, HT = 640, 380
U = "b178"
DATA = B.data()

BOX = (58.0, 8.0, 574.0, 330.0)
X0, X1 = -1.9, 24.8
FT0, FT1 = 1500.0, 5000.0
PL = B.Plot(BOX, (X0, X1), (FT0, FT1))
X, Y = PL.X, PL.Y
RIGHT = BOX[0] + BOX[2]
BOTTOM = BOX[1] + BOX[3]


# ------------------------------------------------------------------------------------------------------------------ what the file says
OETH = DATA["oeth"]
ROUTE_FILE = DATA["worked_example_route"]
LEGS = [leg["nm"] for leg in ROUTE_FILE["legs"]]                       # 5.2, 8.7, 8.9
N_VRP = LEGS[0]
E_VRP = LEGS[0] + LEGS[1]
TOTAL = sum(LEGS)
assert abs(TOTAL - ROUTE_FILE["total_nm"]) < 1e-9
ELEV = OETH["elev_ft"]                                                   # 1 870
ATZ_R = OETH["atz"]["radius_nm"]                                         # 5
ATZ_TOP = OETH["atz"]["upper_ft_amsl"]                                   # 3 000
AGL = int(re.match(r"\d+", DATA["areas"]["riyadh_final_director_east_15l"]["lower"]).group(0))      # 700 ft above the ground
CIRCUIT = OETH["runways"][1]["circuit"]["altitude_ft_msl"]               # 2 900 (the same for both runways)
assert CIRCUIT == OETH["circuit"]["airplane_ft_msl"]
DEPARTURE = OETH["procedures"]["departure_rwy35"]
TURN_FT = int(re.search(r"\((\d+) MSL\)", DEPARTURE).group(1))           # 2 600: 800 ft above the aerodrome
CLIMB_FT = int(re.search(r"climb to (\d+) MSL", DEPARTURE).group(1))     # 3 000
LEVEL_FT = int(re.search(r"maintain (\d+) MSL", OETH["procedures"]["arrival_east"]).group(1))      # 3 500
RIGHT_ATZ = (TOTAL - ATZ_R, TOTAL)                                       # 17.8 to 22.8
OETH_RWY = B.Section().runway_span(OETH["runways"])                      # the runway's thresholds projected on the line from OETH to OERK: -1.03 to +1.14 NM about the ARP

# the ground under the route: open elevation data along the straight lines between the points, level along the runway at each end
_ARP = (OETH["arp"]["lat"], OETH["arp"]["lon"])
_VRPS = [(v["lat"], v["lon"]) for v in OETH["vrps"]]
_PROFILE = TR.profile([_ARP, _VRPS[0], _VRPS[1], _ARP], 0.05)          # (NM along the route, ft), every 0.05 NM
RUNWAY_END = 1.2                                                          # the runway reaches 1.14 NM from the reference point


def _raw(x):
    i = min(max(x / 0.05, 0.0), len(_PROFILE) - 1.001)
    k = int(i)
    return _PROFILE[k][1] + (_PROFILE[k + 1][1] - _PROFILE[k][1]) * (i - k)


def ground(x):
    """Feet above mean sea level under the route at x NM along it: the survey, smoothed over 0.3 NM; the aerodrome elevation along the runway and beyond the ends of the route."""
    d = min(x, TOTAL - x)                                                # how far along the route from the nearer end
    if d <= RUNWAY_END:
        return float(ELEV)
    h = sum(_raw(x + o) for o in (-0.15, -0.1, -0.05, 0.0, 0.05, 0.1, 0.15)) / 7.0
    f = min(1.0, (d - RUNWAY_END) / 0.5)                                 # blend from the runway's level to the survey over half a mile
    return ELEV + (h - ELEV) * f


def _highest(a, b):
    xs = [a + (b - a) * i / 400 for i in range(401)]
    x = max(xs, key=ground)
    return x, ground(x)


HIGH_OUT = _highest(RUNWAY_END, N_VRP)                                    # the scarp north of the aerodrome: about 2.7 NM, 2 630 ft
HIGH_BACK = _highest(E_VRP, TOTAL - RUNWAY_END)                           # the eastern edge of the plateau, the AIP's "mountain ridge": about 16.1 NM, 2 530 ft


def floor(x):
    return ground(x) + AGL


def span(a, b, step=0.08):
    k = max(1, int(math.ceil((b - a) / step)))
    return [a + (b - a) * i / k for i in range(k + 1)]


def ground_line(a, b):
    return [(x, ground(x)) for x in span(a, b)]


def floor_line(a, b):
    return [(x, floor(x)) for x in span(a, b)]


def rev(points):
    return list(reversed(points))


# ------------------------------------------------------------------------------------------------------------------ the blocks
def capped(a, b):
    """The Class C floor between a and b, no higher than the top of the ATZ (inside the zone the overlap ends there)."""
    return [(x, min(floor(x), ATZ_TOP)) for x in span(a, b)]


def raised(a, b):
    """The Class C floor between a and b, no lower than the top of the ATZ (the terminal area leaves the zone out)."""
    return [(x, max(floor(x), ATZ_TOP)) for x in span(a, b)]


ATZ_LEFT = ground_line(X0, ATZ_R) + [(ATZ_R, ATZ_TOP), (X0, ATZ_TOP)]
ATZ_RIGHT = ground_line(RIGHT_ATZ[0], X1) + [(X1, ATZ_TOP), (RIGHT_ATZ[0], ATZ_TOP)]
OVERLAP_LEFT = capped(X0, ATZ_R) + [(ATZ_R, ATZ_TOP), (X0, ATZ_TOP)]
OVERLAP_RIGHT = capped(RIGHT_ATZ[0], X1) + [(X1, ATZ_TOP), (RIGHT_ATZ[0], ATZ_TOP)]
FT_OVER = FT1 + 600.0                       # (the blocks run on above the picture)
TMA_BLOCK = [(X0, FT_OVER)] + raised(X0, ATZ_R) + floor_line(ATZ_R, RIGHT_ATZ[0]) + raised(RIGHT_ATZ[0], X1) + [(X1, FT_OVER)]
FDA_BLOCK = floor_line(X0, X1) + [(X1, FT_OVER), (X0, FT_OVER)]
G_BAND = ground_line(ATZ_R, RIGHT_ATZ[0]) + rev(floor_line(ATZ_R, RIGHT_ATZ[0]))
# over the high ground inside the zone's circle the floor of Class C (700 ft above the ground) lies above the top of the ATZ: the air between them is Class G outside the zone
G_OVER_LEFT = [(x, ATZ_TOP) for x in span(X0, ATZ_R)] + rev(raised(X0, ATZ_R))
G_OVER_RIGHT = [(x, ATZ_TOP) for x in span(RIGHT_ATZ[0], X1)] + rev(raised(RIGHT_ATZ[0], X1))

# ------------------------------------------------------------------------------------------------------------------ the route, (distance along it, height)
PATH = [(0.0, ELEV), (1.5, TURN_FT), (2.4, CLIMB_FT), (N_VRP, LEVEL_FT), (17.0, LEVEL_FT), (18.9, CIRCUIT), (20.1, CIRCUIT)]


# ------------------------------------------------------------------------------------------------------------------ the picture
def page_and_card():
    out = [A1.page(U + "pg", W, HT)]
    grid = "".join(S.altitude_line(BOX[0], RIGHT, Y(ft), colour="#FFFFFF", opacity=0.7, dash="2 3.2", width=0.8) for ft in (2000, 2500, 3500, 4000, 4500))
    body = S.glow(U + "sg", BOX[0] + 70, BOX[1] + 40, 200, "#FFFFFF", 0.42) + grid
    out.append(S.card(U + "cd", BOX[0], BOX[1], BOX[2], BOX[3], B.SKY, body, radius=10))
    return out


def air():
    P = PL.pts
    out = []
    out.append(B.tint(U + "g0", P(G_BAND), "G", opacity=0.42, colour=B.GREY_G, top=0.9, bottom=1.1))
    out.append(B.tint(U + "g1", P(G_OVER_LEFT), "G", opacity=0.42, colour=B.GREY_G, top=1.0, bottom=1.0))
    out.append(B.tint(U + "g2", P(G_OVER_RIGHT), "G", opacity=0.42, colour=B.GREY_G, top=1.0, bottom=1.0))
    out.append(B.tint(U + "tm", P(TMA_BLOCK), "C"))
    out.append(B.tint(U + "fd", P(FDA_BLOCK), "C", top=1.0, bottom=1.0))
    out.append(B.sheen(U + "sm", P(TMA_BLOCK), 0.16))
    out.append(B.inner_glow(U + "gm", P(TMA_BLOCK), 3.0, 0.36))
    for k, (box, over) in enumerate(((ATZ_LEFT, OVERLAP_LEFT), (ATZ_RIGHT, OVERLAP_RIGHT))):
        out.append(B.tint(f"{U}az{k}", P(box), "G"))
        out.append(B.hatch(f"{U}ha{k}", P(over), B.COL["C"], 45, 3.4, 0.9, 0.9))
        out.append(B.hatch(f"{U}hb{k}", P(over), B.COL["G"], -45, 3.4, 0.9, 0.9))
        out.append(B.sheen(f"{U}as{k}", P(box), 0.14))
        out.append(B.inner_glow(f"{U}ag{k}", P(box), 2.0, 0.4, 0.7))
    return "".join(out)


def ground_layer():
    top = PL.pts(ground_line(X0, X1))
    out = [B.soil(U + "so", top, BOTTOM, seed=178, strata=(0.34, 0.6, 0.82), grit=10)]
    out.append(f'<path d="{B.dpath(top)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="1.0" stroke-linejoin="round"/>')
    out.append(B.bushes(5, top, 18, 0.9, x_from=BOX[0] + 4, x_to=RIGHT - 4))
    for x_nm, kind, size in ((4.2, "a", 10.0), (8.9, "a", 11.0), (10.9, "p", 15.0), (12.4, "a", 10.0), (19.4, "a", 11.0), (20.6, "p", 15.0)):
        x = X(x_nm)
        y = B.ground_y_at(top, x)
        out.append(S.palm(x, y, size, 0.1, int(x)) if kind == "p" else S.acacia(x, y, size, int(x)))
    return "".join(out)


def aerodromes():
    """The aerodrome at each end of the route: a runway bar and a hangar (no tower, and no windsock: the AIP lists none)."""
    out = []
    yg = Y(ELEV)
    for k, x0 in enumerate((0.0, TOTAL)):
        out.append(B.runway_bar(X(x0 + OETH_RWY[0]), X(x0 + OETH_RWY[1]), yg, h=3.4))
    out.append(B.hangar(U + "hl", X(-1.52), yg - 0.2, 15.0, 7.4))
    out.append(B.hangar(U + "hr", X(TOTAL + 1.22), yg - 0.2, 10.0, 5.6, "#D9D3C0"))
    return "".join(out)


def outlines():
    P = PL.pts
    c, g = B.COL["C"], B.COL["G"]
    out = []
    out.append(B.edge(P(floor_line(ATZ_R, RIGHT_ATZ[0])), c))
    out.append(B.edge(P(floor_line(X0, ATZ_R)), c, width=1.1, opacity=0.9))
    out.append(B.edge(P(floor_line(RIGHT_ATZ[0], X1)), c, width=1.1, opacity=0.9))
    out.append(B.edge(P([(X0, ATZ_TOP), (ATZ_R, ATZ_TOP), (ATZ_R, ground(ATZ_R))]), g, width=1.45))
    out.append(B.edge(P([(RIGHT_ATZ[0], ground(RIGHT_ATZ[0])), (RIGHT_ATZ[0], ATZ_TOP), (X1, ATZ_TOP)]), g, width=1.45))
    return "".join(out)


def verticals():
    """A thin dotted line up from each visual reporting point to the route, and the points themselves."""
    out = []
    for x_nm in (N_VRP, E_VRP):
        x = X(x_nm)
        yg = Y(ground(x_nm))
        out.append(f'<line x1="{S.n(x)}" y1="{S.n(yg - 9)}" x2="{S.n(x)}" y2="{S.n(Y(LEVEL_FT) + 3)}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="2.6" stroke-linecap="round"/>'
                   f'<line x1="{S.n(x)}" y1="{S.n(yg - 9)}" x2="{S.n(x)}" y2="{S.n(Y(LEVEL_FT) + 3)}" stroke="#3B4558" stroke-width="1" stroke-dasharray="1.6 3.2" stroke-linecap="round"/>')
        out.append(B.vrp(x, yg, 10.5))
    return "".join(out)


def circuit_line():
    """The circuit altitude over the last 5 NM: a thin dashed line."""
    y = Y(CIRCUIT)
    return B.edge([(X(RIGHT_ATZ[0]), y), (X(TOTAL), y)], "#1F2937", width=1.0, dash="4 3", casing=2.0)


def route_layer():
    pts_ = [PL.P(x, ft) for x, ft in PATH]
    return B.route(U + "rt", pts_, width=4.8, radius=16.0, every=36.0, head=8.5)


def marks():
    out = []
    t = B.tag
    out.append(B.class_disc(X(-0.9), Y(2330), "G", "G"))
    out.append(B.class_disc(X(23.3), Y(2380), "G", "G"))
    out.append(B.class_disc(X(9.0), Y(4650), "C", "C"))
    out.append(B.class_disc(X(11.0), Y(ground(11.0) + 350), "G", "G"))
    out.append(t(X(X0) + 5, Y(ATZ_TOP) - 3.4, "3 000", B.COL["G"], 8.8))
    out.append(t(X(1.6) + 9, Y(TURN_FT) - 5.0, "2 600", B.INK, 9.0))
    out.append(t(X(13.4), Y(LEVEL_FT) - 6.0, "3 500", B.INK, 9.2, "middle"))
    out.append(t(X(TOTAL) - 5, Y(CIRCUIT) + 12.0, "2 900", B.INK, 9.0, "end"))
    out.append(t(X(N_VRP) + 8, Y(ground(N_VRP)) - 3.0, "5.2", "#7A5C06", 9.0))
    out.append(t(X(E_VRP) + 8, Y(ground(E_VRP)) - 3.0, "13.9", "#7A5C06", 9.0))
    for x_nm, ft in (HIGH_OUT, HIGH_BACK):                                # the highest ground under the route, out and back, to the nearest 10 ft
        v = int(round(ft / 10.0) * 10)
        out.append(t(X(x_nm) + 2.0, Y(ft) + 27.0, f"{v // 1000} {v % 1000:03d}", "#5B4420", 8.6, "middle"))
    out.append(t(X(TOTAL) - 15, Y(1690) + 3.6, "1 870", B.INK, 9.0, "end"))
    return "".join(out)


def axes():
    out = []
    x0 = BOX[0]
    for ft in range(1500, 5001, 500):
        y = Y(ft)
        out.append(B.plain_text(x0 - 7, y + 3.7, f"{ft // 1000} {ft % 1000:03d}" if ft >= 1000 else str(ft)))
        out.append(f'<line x1="{S.n(x0 - 4.5)}" y1="{S.n(y)}" x2="{S.n(x0)}" y2="{S.n(y)}" stroke="#4B5870" stroke-width="1"/>')
    out.append(B.plain_text(x0 - 7, BOX[1] + 24.0, "ft", "#4B5870", 9.5))
    yb = BOTTOM
    for v in (0, 5, 10, 15, 20):
        x = X(v)
        out.append(f'<line x1="{S.n(x)}" y1="{S.n(yb)}" x2="{S.n(x)}" y2="{S.n(yb + 4.5)}" stroke="#4B5870" stroke-width="1"/>')
        out.append(B.plain_text(x, yb + 15.5, str(v), anchor="middle"))
    x = X(TOTAL)
    out.append(f'<line x1="{S.n(x)}" y1="{S.n(yb)}" x2="{S.n(x)}" y2="{S.n(yb + 4.5)}" stroke="#4B5870" stroke-width="1"/>')
    out.append(B.plain_text(x, yb + 15.5, "22.8", anchor="middle"))
    out.append(B.plain_text(RIGHT, yb + 15.5, "NM", "#4B5870", 9.5))
    out.append(B.plain_text(X(0.0), yb + 28.5, "OETH", B.INK, 9.5, "middle", "bold"))
    out.append(B.plain_text(X(TOTAL), yb + 28.5, "OETH", B.INK, 9.5, "middle", "bold"))
    return "".join(out)


def aeroplane():
    look = {"outline": {"width": 0.6, "colour": "#1B2638", "opacity": 0.95}, "shadow": {"dx": 0.8, "dy": 1.8, "blur": 1.3, "opacity": 0.28}}
    return {"name": "sprite-side", "at": [X(10.6), Y(LEVEL_FT) - 3.0], "width": 40, **look}


def callouts():
    c = S.callout
    r = 10.0
    out = []
    out.append(c(1, X(19.6), Y(2420), X(RIGHT_ATZ[0]), Y(2420), r=r))
    out.append(c(2, X(9.3), Y(3000), X(9.3), Y(floor(9.3)), r=r))
    out.append(c(3, X(0.6), Y(3350), X(0.95), Y(2250), r=r))
    out.append(c(4, X(N_VRP), Y(1690), X(N_VRP), Y(ground(N_VRP)) + 1.0, r=r))
    out.append(c(5, X(8.2), Y(4120), X(8.2), Y(LEVEL_FT) - 3.0, r=r))
    out.append(c(6, X(E_VRP + 0.75), Y(1690), X(E_VRP), Y(ground(E_VRP)) + 1.0, r=r))
    out.append(c(7, X(21.9), Y(3550), X(21.9), Y(CIRCUIT), r=r))
    out.append(c(8, X(TOTAL), Y(1690), X(TOTAL), Y(ELEV) + 1.0, r=r))
    return "".join(out)


def layers():
    inner = [air(), ground_layer(), aerodromes(), outlines(), verticals(), circuit_line()]
    return [*page_and_card(), S.card_front(U + "fr", BOX[0], BOX[1], BOX[2], BOX[3], "".join(inner), radius=10), route_layer(), aeroplane(), S.card_front(U + "mk", BOX[0], BOX[1], BOX[2], BOX[3], marks(), radius=10), axes(), callouts()]


def plate():
    return {
        "id": "fig-17-09-route-profile",
        "replaces": "fig-17-09-route-profile.svg",
        "book_file": "plate-17-09-route-profile.jpg",
        "caption": "Figure 17-9. The worked example in profile along the route",
        "desc": ("Figure 17-9. The worked example in profile along the route. The three legs of the worked example unrolled: the Thumamah aerodrome traffic zone at each end, Class C from 700 ft above "
                 "the ground over the whole route, the climb out of Thumamah, the level at 3 500 ft past the North and East VRPs and the ridge, the descent to the circuit altitude. "
                 "Feet above mean sea level against nautical miles along the route; vertical scale exaggerated; the ground is from open elevation data (NASA SRTM) under the straight lines between the points; not for navigation."),
        "legend": [
            "The Thumamah ATZ, Class G, surface to 3 000 ft AMSL.",
            "Class C from 700 ft above the ground: the Riyadh terminal control area and final director area. A clearance and radio contact with Riyadh Approach are needed to enter.",
            "Departure from runway 35: runway heading to 2 600 ft AMSL (800 ft above the aerodrome), then a right turn to the North VRP and a climb to 3 000 ft AMSL.",
            "The North VRP, 5.2 NM.",
            "Level at 3 500 ft AMSL: the level the AIP gives for the East VRP, and an odd thousand plus 500 ft for an easterly course.",
            "The East VRP, 13.9 NM, and the ridge: the AIP says to stay at 3 500 ft AMSL until past the ridge.",
            "The circuit altitude of Thumamah: 2 900 ft AMSL, 1 030 ft above the aerodrome.",
            "The aerodrome elevation: 1 870 ft AMSL.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-17-09-route-profile.svg", "blank": True, "layers": layers()},
    }
