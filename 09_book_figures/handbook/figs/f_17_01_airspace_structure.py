"""Figure 17-1. Airspace blocks between Thumamah and Riyadh, seen from the side: a vertical section along the line from Thumamah (OETH) to Riyadh King Khalid (OERK), drawn from
data/saudi_airspace.json (AIP AMDT 11/26).

The frame: the distance along the line from OETH (the line is 15.5 NM long, true bearing 166 degrees; positive towards OERK, north on the left), from -9 to +27 NM, in an
equirectangular frame round the Thumamah ARP (x = dlon * 60 * cos(lat0), y = dlat * 60, 1 NM = 1852 m); the height above mean sea level, linear, from 0 to 22 000 ft. The scale is
574 canvas units to 36 NM (15.94 units to the NM) and 328 units to 22 000 ft (14.9 units to 1 000 ft). Every limit comes from the file: the ATZ (5 NM round OETH, surface to 3 000 ft), the control
zone (10 NM round OERK, surface to 4 500 ft), the Riyadh East terminal control area part 1 (700 ft above the ground to FL 195; the line leaves its ring where the file's ring
ends, inside the control zone), the final director area for 15L (700 ft above the ground to 11 000 ft; the line leaves its ring over the airport), FL 150. The ground runs between the two
aerodrome elevations, 1 870 and 2 053 ft. Beyond the end of the terminal area's ring the file has no limits (the Riyadh West terminal area is not in it), so what lies there is drawn fading out.
The ten numbered callouts are those of the brief's legend (figs/h_b1.py makes the pieces)."""
import math
import re

from figs import h_a1 as A1
from figs import h_b1 as B
from figs import scene as S

W, HT = 640, 372
U = "b171"
SEC = B.Section()
DATA = B.data()

BOX = (58.0, 8.0, 574.0, 328.0)          # the picture: x, y, width, height
S0, S1 = -9.0, 27.0                       # NM from OETH at its left and right edges
FT_TOP = 22000.0
PL = B.Plot(BOX, (S0, S1), (0.0, FT_TOP))
X, Y = PL.X, PL.Y
RIGHT = BOX[0] + BOX[2]
BOTTOM = BOX[1] + BOX[3]


def ft_of(text):
    """'700 FT AGL' -> 700, 'FL195' -> 19500, '11000 FT AMSL' -> 11000."""
    t = text.upper().replace(" ", "")
    if t.startswith("FL"):
        return int(t[2:]) * 100
    return int(re.match(r"\d+", t).group(0))


def in_frame(values):
    return [v for v in values if S0 < v < S1]


# ------------------------------------------------------------------------------------------------------------------ the limits, from the file
L = SEC.length                                                      # OETH to OERK: 15.5 NM
ATZ_R = DATA["oeth"]["atz"]["radius_nm"]                            # 5
CTR_R = DATA["oerk"]["ctr"]["radius_nm"]                            # 10
ATZ = (-ATZ_R, ATZ_R)
CTR = (L - CTR_R, L + CTR_R)
ATZ_TOP = DATA["oeth"]["atz"]["upper_ft_amsl"]                      # 3 000
CTR_TOP = DATA["oerk"]["ctr"]["upper_ft_amsl"]                      # 4 500
TMA_AREA = DATA["areas"]["riyadh_east_tma_part1"]
FDA_AREA = DATA["areas"]["riyadh_final_director_east_15l"]
AGL = ft_of(TMA_AREA["lower"])                                      # 700 ft above the ground
assert AGL == ft_of(FDA_AREA["lower"])
TMA_TOP = ft_of(TMA_AREA["upper"])                                  # FL 195
FDA_TOP = ft_of(FDA_AREA["upper"])                                  # 11 000
FL150 = 15000
TMA_CROSS, FDA_CROSS = SEC.crossings(TMA_AREA["ring"]), SEC.crossings(FDA_AREA["ring"])
assert min(TMA_CROSS) < S0 and min(FDA_CROSS) < S0                  # both blocks run on past the left edge of the picture
TMA_END = in_frame(TMA_CROSS)[-1]                                   # 17.97 NM: the line leaves the terminal area's ring, inside the control zone
FDA_END = in_frame(FDA_CROSS)[-1]                                   # 15.46 NM: it leaves the final director area over the airport
assert CTR[0] < TMA_END < CTR[1] and CTR[0] < FDA_END < CTR[1]
OETH_RWY = SEC.runway_span(DATA["oeth"]["runways"])
OERK_RWY = SEC.runway_span(DATA["oerk"]["runways"][:2])             # the other pair of runways lies on the same stretch of the line


def ground(s):
    return SEC.ground_ft(s)


def floor(s):
    return ground(s) + AGL


def span(a, b, step=1.0):
    k = max(1, int(math.ceil((b - a) / step)))
    return [a + (b - a) * i / k for i in range(k + 1)]


def ground_line(a, b):
    return [(s, ground(s)) for s in span(a, b)]


def floor_line(a, b):
    return [(s, floor(s)) for s in span(a, b)]


def rev(points):
    return list(reversed(points))


# ------------------------------------------------------------------------------------------------------------------ the blocks, as polygons of (distance, height)
ATZ_BOX = ground_line(*ATZ) + [(ATZ[1], ATZ_TOP), (ATZ[0], ATZ_TOP)]
CTR_BOX = ground_line(*CTR) + [(CTR[1], CTR_TOP), (CTR[0], CTR_TOP)]
# the terminal area: from the floor to FL 195, round and above the two boxes (it excludes them), as far as its own ring
TMA_BLOCK = floor_line(S0, ATZ[0]) + [(ATZ[0], ATZ_TOP), (ATZ[1], ATZ_TOP)] + floor_line(ATZ[1], CTR[0]) + [(CTR[0], CTR_TOP), (TMA_END, CTR_TOP), (TMA_END, TMA_TOP), (S0, TMA_TOP)]
# the final director area: from the floor to 11 000 ft, up to the control zone (it excludes only that), over it as far as its own ring; the ATZ lies wholly inside it
FDA_BLOCK = floor_line(S0, CTR[0]) + [(CTR[0], CTR_TOP), (FDA_END, CTR_TOP), (FDA_END, FDA_TOP), (S0, FDA_TOP)]
OVERLAP = floor_line(*ATZ) + [(ATZ[1], ATZ_TOP), (ATZ[0], ATZ_TOP)]
# class G, what is left: under the floor, outside the two boxes
G_LEFT = ground_line(S0, ATZ[0]) + rev(floor_line(S0, ATZ[0]))
G_SLOT = ground_line(ATZ[1], CTR[0]) + rev(floor_line(ATZ[1], CTR[0]))
G_RIGHT = ground_line(CTR[1], S1) + rev(floor_line(CTR[1], S1))
# the control area, Class A: above FL 195 over the terminal area, from FL 150 where the terminal area's ring has ended
A_BLOCK = [(S0, TMA_TOP), (TMA_END, TMA_TOP), (TMA_END, FL150), (S1, FL150), (S1, FT_TOP), (S0, FT_TOP)]
# what lies beyond the end of the ring over the control zone: not in the file, so drawn fading to the right and upwards
BEYOND = [(TMA_END, CTR_TOP), (CTR[1], CTR_TOP)] + floor_line(CTR[1], S1) + [(S1, FL150), (TMA_END, FL150)]


# ------------------------------------------------------------------------------------------------------------------ the picture
def page_and_card():
    out = [A1.page(U + "pg", W, HT)]
    grid = "".join(S.altitude_line(BOX[0], RIGHT, Y(ft), colour="#FFFFFF", opacity=0.7, dash="2 3.2", width=0.8) for ft in (5000, 10000, 20000))
    body = S.glow(U + "sg", BOX[0] + 70, BOX[1] + 40, 210, "#FFFFFF", 0.42) + grid
    out.append(S.card(U + "cd", BOX[0], BOX[1], BOX[2], BOX[3], B.SKY, body, radius=10))
    return out


def fade_defs():
    x0 = X(TMA_END)
    return (f'<defs><linearGradient id="{U}fg" gradientUnits="userSpaceOnUse" x1="{S.n(x0)}" y1="0" x2="{S.n(RIGHT)}" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#808080"/></linearGradient>'
            f'<mask id="{U}fm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{HT}"><rect x="0" y="0" width="{S.n(x0)}" height="{HT}" fill="#FFFFFF"/>'
            f'<rect x="{S.n(x0)}" y="0" width="{S.n(W - x0)}" height="{HT}" fill="url(#{U}fg)"/></mask></defs>')


def air():
    """All the tints of the blocks of air, back to front."""
    P = PL.pts
    out = []
    # what is left: the pale grey-green of uncontrolled air
    for k, g in enumerate((G_LEFT, G_SLOT, G_RIGHT)):
        out.append(B.tint(f"{U}g{k}", P(g), "G", opacity=0.42, colour=B.GREY_G, top=0.9, bottom=1.1))
    # the control area and the terminal area beyond its ring, fading to the right (and the part beyond, upwards too)
    beyond_fill = (f'<defs>{S.gradient(U + "bf", [(0, B.COL["C"], 0.0), (0.22, B.COL["C"], B.FILL["C"] * 0.5), (0.6, B.COL["C"], B.FILL["C"] * 1.0), (1, B.COL["C"], B.FILL["C"] * 1.3)])}</defs>'
                   f'<polygon points="{S.pts(P(BEYOND))}" fill="url(#{U}bf)"/>')
    out.append(f'<g mask="url(#{U}fm)">' + B.tint(U + "ta", P(A_BLOCK), "A", top=1.1, bottom=0.8) + beyond_fill
               + B.edge(P([(CTR[1], floor(CTR[1])), (S1, floor(S1))]), B.COL["C"], opacity=0.9) + '</g>')
    # the terminal area (part 1) and the final director area, both Class C: where they overlap the fills add up
    out.append(B.tint(U + "tm", P(TMA_BLOCK), "C"))
    out.append(B.tint(U + "fd", P(FDA_BLOCK), "C", top=1.0, bottom=1.0))
    out.append(B.sheen(U + "sm", P(TMA_BLOCK), 0.16))
    out.append(B.gloss(U + "gl", P(TMA_BLOCK), 0.13))
    out.append(B.inner_glow(U + "gm", P(TMA_BLOCK), 3.0, 0.38))
    out.append(B.inner_glow(U + "gf", P(FDA_BLOCK), 3.0, 0.22))
    # the zone of the ATZ, Class G, over the final director area: the overlap is cross-hatched (green one way, indigo the other)
    out.append(B.tint(U + "az", P(ATZ_BOX), "G"))
    out.append(B.hatch(U + "h1", P(OVERLAP), B.COL["C"], 45, 2.5, 0.85, 0.95))
    out.append(B.hatch(U + "h2", P(OVERLAP), B.COL["G"], -45, 2.5, 0.85, 0.95))
    out.append(B.sheen(U + "sa", P(ATZ_BOX), 0.14))
    out.append(B.inner_glow(U + "ga", P(ATZ_BOX), 1.6, 0.4, 0.6))
    # the control zone, Class D
    out.append(B.tint(U + "cz", P(CTR_BOX), "D"))
    out.append(B.sheen(U + "sc", P(CTR_BOX), 0.10))
    out.append(B.inner_glow(U + "gc", P(CTR_BOX), 2.2, 0.32, 0.8))
    return "".join(out)


def ground_layer():
    top = [P_ for P_ in PL.pts(ground_line(S0, S1))]
    out = [B.soil(U + "so", top, BOTTOM, seed=171, haze=(4.5, 0.4))]
    out.append(B.bushes(7, top, 22, 0.6, x_from=BOX[0] + 4, x_to=RIGHT - 4))
    # a few trees, small, away from what the picture is about
    for x_s, kind, size in ((-3.7, "a", 7.5), (4.2, "p", 11.0), (9.4, "a", 7.5), (12.3, "p", 10.0), (21.2, "a", 7.0), (23.6, "p", 10.0), (26.0, "a", 7.0)):
        x = X(x_s)
        y = B.ground_y_at(top, x)
        out.append(S.palm(x, y, size, 0.1, int(x)) if kind == "p" else S.acacia(x, y, size, int(x)))
    return "".join(out)


def aerodromes():
    """Thumamah: a runway bar, hangars and a windsock (no tower); Riyadh: a runway bar, a terminal and the tower."""
    out = []
    yg0, yg1 = Y(ground(0.0)), Y(ground(L))
    out.append(B.runway_bar(X(OETH_RWY[0]), X(OETH_RWY[1]), yg0))
    out.append(B.hangar(U + "h1", X(1.9), yg0 - 0.2, 12.0, 5.2))
    out.append(B.hangar(U + "h2", X(3.1), yg0 - 0.2, 10.0, 4.6, "#D9D3C0"))
    out.append(B.windsock(U + "ws", X(-1.9), yg0, pole=9.0, length=10.5))
    out.append(B.runway_bar(X(OERK_RWY[0]), X(OERK_RWY[1]), yg1))
    out.append(B.hangar(U + "t1", X(17.2), yg1 - 0.2, 20.0, 4.6, "#E8DFC9"))
    out.append(B.tower(U + "tw", X(L + 0.55), yg1 - 0.4, 22.0))
    return "".join(out)


def outlines():
    """The boundaries: dashed (7 4) over a white casing, in the colour of the class. The edges that two blocks share are drawn once."""
    P = PL.pts
    c, g, d, a = B.COL["C"], B.COL["G"], B.COL["D"], B.COL["A"]
    out = []
    # the terminal area: its floor outside the two boxes, its ceiling, its end
    out.append(B.edge(P(floor_line(S0, ATZ[0])), c))
    out.append(B.edge(P(floor_line(ATZ[1], CTR[0])), c))
    out.append(B.edge(P([(S0, TMA_TOP), (TMA_END, TMA_TOP), (TMA_END, CTR_TOP)]), c))
    # the final director area: its floor across the zone of the ATZ, its ceiling and its end
    out.append(B.edge(P(floor_line(*ATZ)), c, width=1.1, opacity=0.9))
    out.append(B.edge(P([(S0, FDA_TOP), (FDA_END, FDA_TOP), (FDA_END, CTR_TOP)]), c))
    # the two boxes: the sides and the top (the foot is the ground)
    out.append(B.edge(P([(ATZ[0], ground(ATZ[0])), (ATZ[0], ATZ_TOP), (ATZ[1], ATZ_TOP), (ATZ[1], ground(ATZ[1]))]), g, width=1.45))
    out.append(B.edge(P([(CTR[0], ground(CTR[0])), (CTR[0], CTR_TOP), (CTR[1], CTR_TOP), (CTR[1], ground(CTR[1]))]), d, width=1.45))
    # FL 150, across the whole picture: thin
    out.append(B.edge(P([(S0, FL150), (S1, FL150)]), a, width=1.0, casing=2.0))
    return "".join(out)


INSET = 3.6                              # the dashed frame of the FIR stands this far inside the edge of the picture


def frame_clip():
    x0, y0, w, h = BOX
    return f'<defs><clipPath id="{U}fc"><rect x="{S.n(x0 + INSET)}" y="{S.n(y0 + INSET)}" width="{S.n(w - 2 * INSET)}" height="{S.n(h - INSET)}"/></clipPath></defs>'


def fir_frame():
    """The flight information region over everything: a dashed frame round the air of the picture (left, top, right; the ground is its foot)."""
    x0, y0, w, h = BOX
    return B.edge([(x0 + INSET, Y(ground(S0))), (x0 + INSET, y0 + INSET), (x0 + w - INSET, y0 + INSET), (x0 + w - INSET, Y(ground(S1)))], "#2F4B7C", width=1.2, casing=2.2, opacity=0.9)


def marks():
    """The letters of the classes in small discs, and the limits as digits."""
    out = []
    out.append(B.class_disc(X(6.8), Y(20800), "A", "A"))
    out.append(B.class_disc(X(12.0), Y(17300), "C", "C"))
    out.append(B.class_disc(X(10.0), Y(8000), "C", "C"))
    out.append(B.class_disc(X(10.2), Y(3300), "D", "D"))
    out.append(B.class_disc(X(-1.2), Y(ATZ_TOP) - 7.6, "G", "G", r=5.6))
    t = B.tag
    out.append(t(X(TMA_END) - 4, Y(TMA_TOP) - 3.4, "FL 195", B.COL["C"], 8.6, "end"))
    out.append(t(X(FDA_END) - 4, Y(FDA_TOP) - 3.4, "11 000", B.COL["C"], 8.6, "end"))
    out.append(t(RIGHT - 7, Y(FL150) - 3.4, "FL 150", B.COL["A"], 8.6, "end"))
    out.append(t(X(ATZ[0]) + 3, Y(ATZ_TOP) - 3.4, "3 000", B.COL["G"], 8.2))
    out.append(t(X(CTR[0]) + 3, Y(CTR_TOP) - 3.4, "4 500", B.COL["D"], 8.2))
    return "".join(out)


def axes():
    out = []
    x0 = BOX[0]
    for ft, label in ((0, "0"), (5000, "5 000"), (10000, "10 000"), (15000, "15 000"), (20000, "20 000")):
        y = Y(ft)
        out.append(B.plain_text(x0 - 7, y + 3.7, label))
        out.append(f'<line x1="{S.n(x0 - 4.5)}" y1="{S.n(y)}" x2="{S.n(x0)}" y2="{S.n(y)}" stroke="#4B5870" stroke-width="1"/>')
    out.append(B.plain_text(x0 - 7, BOX[1] + 7.5, "ft", "#4B5870", 9.5))
    yb = BOTTOM
    for s_ in (-5, 0, 5, 10, 15, 20, 25):
        x = X(s_)
        out.append(f'<line x1="{S.n(x)}" y1="{S.n(yb)}" x2="{S.n(x)}" y2="{S.n(yb + 4.5)}" stroke="#4B5870" stroke-width="1"/>')
        out.append(B.plain_text(x, yb + 15.5, str(s_).replace("-", "−"), anchor="middle"))
    out.append(B.plain_text(RIGHT, yb + 15.5, "NM", "#4B5870", 9.5))
    out.append(B.plain_text(X(0.0), yb + 28.5, "OETH", B.INK, 9.5, "middle", "bold"))
    out.append(B.plain_text(X(L), yb + 28.5, "OERK", B.INK, 9.5, "middle", "bold"))
    return "".join(out)


def aeroplanes():
    look = {"outline": {"width": 0.55, "colour": "#1B2638", "opacity": 0.95}}
    vfr = {"name": "sprite-side", "at": [X(-6.5), Y(2220)], "width": 30, **look}
    circuit = {"name": "sprite-side-left", "at": [X(2.4), Y(2900)], "width": 27, **look}
    return vfr, circuit


def callouts():
    c = S.callout
    out = []
    r = 9.5
    out.append(c(1, BOX[0] + 20, BOX[1] + 19, BOX[0] + 34, BOX[1] + 3.6, r=r))
    out.append(c(2, X(-6.4), Y(12700), X(-6.4), Y(FL150), r=r))
    out.append(c(3, X(21.0), Y(3300), r=r))
    out.append(c(4, X(2.6), Y(17000), X(2.6), Y(TMA_TOP), r=r))
    out.append(c(5, X(-1.2), Y(8300), X(-1.2), Y(FDA_TOP), r=r))
    out.append(c(6, X(-8.0), Y(900), X(-8.0), Y(2150), r=r))
    out.append(c(7, X(-5.9), Y(900), X(-5.9), Y(1980), r=r))
    out.append(c(8, X(0.6), Y(900), X(0.6), Y(ground(0.0)) - 1.0, r=r))
    out.append(c(9, X(L), Y(900), X(L), Y(ground(L)) - 1.0, r=r))
    out.append(c(10, X(22.3), Y(17300), X(22.3), Y(FL150), r=r))
    return "".join(out)


def layers():
    vfr, circuit = aeroplanes()
    inner = [fade_defs(), frame_clip(), f'<g clip-path="url(#{U}fc)">' + air() + "</g>", ground_layer(), aerodromes(), f'<g clip-path="url(#{U}fc)">' + outlines() + "</g>", fir_frame(), marks()]
    return [*page_and_card(), S.card_front(U + "fr", BOX[0], BOX[1], BOX[2], BOX[3], "".join(inner), radius=10), vfr, circuit, axes(), callouts()]


def plate():
    return {
        "id": "fig-17-01-airspace-structure",
        "replaces": "fig-17-01-airspace-structure.svg",
        "book_file": "plate-17-01-airspace-structure.jpg",
        "caption": "Figure 17-1. Airspace blocks between Thumamah and Riyadh, seen from the side",
        "desc": ("Figure 17-1. Airspace blocks between Thumamah and Riyadh, seen from the side. A vertical section along the line from Thumamah (OETH) to Riyadh King Khalid (OERK): "
                 "the Thumamah aerodrome traffic zone, the Riyadh control zone, the terminal control area and the final director area, uncontrolled air under their floor, FL 150 and "
                 "the control area above. Drawn to the limits of the AIP (AMDT 11/26) along the line from Thumamah to Riyadh, 15.5 NM; the ground is schematic; not for navigation."),
        "legend": [
            "The Jeddah FIR: flight information and alerting service throughout.",
            "FL 150: at and above it, every flight is IFR [[§91.77]].",
            "The Riyadh control zone, Class D: radius 10 NM, surface to 4 500 ft AMSL.",
            "The Riyadh East terminal control area, Class C: from 700 ft above the ground to FL 195.",
            "The Riyadh final director area for runway 15L, Class C: 700 ft above the ground to 11 000 ft AMSL.",
            "Uncontrolled airspace (grey): Class G.",
            "A VFR aeroplane under the floor of the terminal area, outside every controlled block.",
            "Thumamah, without a tower: its aerodrome traffic zone is Class G, radius 5 NM, surface to 3 000 ft AMSL.",
            "Riyadh King Khalid, with a tower, inside its control zone.",
            "The Riyadh control area, Class A, from FL 150; its floor is the dashed line.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-17-01-airspace-structure.svg", "blank": True, "layers": layers()},
    }
