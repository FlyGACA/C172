"""Figure 17-7. The worked example in plan view: a local flight from Thumamah (OETH - North VRP - East VRP - OETH, 5.2 + 8.7 + 8.9 = 22.8 NM). A plan on an aerial view of the plain, drawn to
scale from the AIP (AMDT 11/26) data of data/saudi_airspace.json: an equirectangular frame round the Thumamah reference point, 13.33 canvas units to the NM (48 x 30 NM), north up, with
Thumamah left of the middle. The Thumamah aerodrome traffic zone (Class G, a true circle of 5 NM), the Riyadh final director area for runway 15L (Class C, the rotated rectangle of the
file, which contains the whole zone), the Riyadh control zone (Class D, a true circle of 10 NM round Riyadh, the northern part of it), the terminal control areas (Class C: the faint indigo
over all the ground, the two zones cut out of it), the three special use areas OED25, OED33 (danger) and OER212 (restricted) as the rings of the file with a red-orange hatch, the two
visual reporting points as amber triangles, the runway as a bar, the route as a ribbon with the model's aeroplane on it, a scale bar of 5 NM and a north arrow. No words: digits, class
letters in discs, the ICAO codes and the codes of the three areas."""
import math

from figs import h_b2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 400
U = "b27"
SCALE = 40.0 / 3.0                                                   # canvas units to the NM

terrain.ensure("terrain-17-07-saudi", size=(W * 4, HT * 4), seed=1707, kind="plain", features=(), veil=0.42, soft=3.0)

OETH, OERK = H.DATA["oeth"], H.DATA["oerk"]
AREAS = H.DATA["areas"]
F = H.Frame(OETH["arp"]["lat"], OETH["arp"]["lon"], SCALE, 284.0, 173.3)     # Thumamah lies at (284, 173.3): the frame shows 21.3 NM to the west of it, 26.7 to the east, 13 to the north, 17 to the south

T = F.xy(OETH["arp"]["lon"], OETH["arp"]["lat"])
K = F.xy(OERK["arp"]["lon"], OERK["arp"]["lat"])
ATZ = H.circle(T[0], T[1], F.r(OETH["atz"]["radius_nm"]))
CTR = H.circle(K[0], K[1], F.r(OERK["ctr"]["radius_nm"]))
FDA = H.poly(F.ring(AREAS["riyadh_final_director_east_15l"]["ring"][:-1]))
PRD = {k: H.poly(F.ring(v["ring"][:-1])) for k, v in AREAS["prd"].items()}
NV, EV = (F.xy(v["lon"], v["lat"]) for v in OETH["vrps"])          # the North VRP and the East VRP
ROUTE = [T, NV, EV, T]
LEG_HEADINGS = [20.0, 124.0, 270.0]


def thr(airport, rid):
    rw = next(r for r in airport["runways"] if r["id"] == rid)
    return F.xy(rw["threshold"]["lon"], rw["threshold"]["lat"])


def riyadh_runways():
    return "".join(H.runway(U, thr(OERK, a), thr(OERK, b), 3.0) for a, b in (("15L", "33R"), ("15R", "33L")))


def thumamah_runway():
    return H.runway(U, thr(OETH, "17"), thr(OETH, "35"), 3.2)


def grid():
    out = []
    step = 5 * SCALE
    x = T[0] % step
    while x < W:
        out.append(f'<line x1="{S.n(x)}" y1="0" x2="{S.n(x)}" y2="{HT}" stroke="#FFFFFF" stroke-opacity="0.26" stroke-width="0.6"/>')
        x += step
    y = T[1] % step
    while y < HT:
        out.append(f'<line x1="0" y1="{S.n(y)}" x2="{W}" y2="{S.n(y)}" stroke="#FFFFFF" stroke-opacity="0.26" stroke-width="0.6"/>')
        y += step
    return "".join(out)


def centre_of(shape):
    xs, ys = [p[0] for p in shape["pts"]], [p[1] for p in shape["pts"]]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def airspace():
    out = [H.hole_mask(U + "mt", W, HT, [(CTR["cx"], CTR["cy"], CTR["r"]), (ATZ["cx"], ATZ["cy"], ATZ["r"])]),      # the terminal control areas exclude both zones
           H.hole_mask(U + "mf", W, HT, [(CTR["cx"], CTR["cy"], CTR["r"])])]                                       # the final director area excludes the control zone only
    out.append(H.fill(H.poly([(0, 0), (W, 0), (W, HT), (0, HT)]), "C", 0.13, mask=U + "mt"))
    out.append(H.fill(FDA, "C", mask=U + "mf"))
    out.append(H.fill(CTR, "D"))
    out.append(H.fill(ATZ, "G"))
    out.append(H.gloss(U + "f", FDA, 0.22, mask=U + "mf"))
    out.append(H.gloss(U + "c", CTR, 0.34))
    out.append(H.gloss(U + "a", ATZ, 0.34))
    out.append(f'<g mask="url(#{U}mf)">' + H.inner_glow(U + "f", FDA, "C", 10, 0.22) + "</g>")
    out.append(H.inner_glow(U + "c", CTR, "D", 12, 0.30))
    out.append(H.inner_glow(U + "a", ATZ, "G", 10, 0.30))
    out.append(H.edge(FDA, "C", mask=U + "mf", uid=U))
    out.append(H.edge(CTR, "D", uid=U))
    out.append(H.edge(ATZ, "G", uid=U))
    return "".join(out)


def special_use():
    out = []
    for code, shape in PRD.items():
        cx, cy = centre_of(shape)
        if code == "OED25":                                           # a small area: its code stands under it, so that the hatch stays in view
            ys = [p[1] for p in shape["pts"]]
            out.append(H.special_use(U, shape, code, (cx, max(ys) + 9.5), 5.8))
        else:
            out.append(H.special_use(U, shape, code, (cx, cy), 7.4))
    return "".join(out)


def head_marks():
    """Where the small arrowheads go: the distances along the route of the middle of the first and the last leg, and a third of the way along the second (the aeroplane has its middle)."""
    d = [H.dist(a, b) for a, b in zip(ROUTE, ROUTE[1:])]
    return [d[0] * 0.5, d[0] + d[1] * 0.27, d[0] + d[1] + d[2] * 0.5]


def plane():
    p = H.lerp(NV, EV, 0.64)
    return {"name": "sprite-top", "at": [p[0], p[1]], "width": 34, "angle": LEG_HEADINGS[1], "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.9}, "shadow": {"dx": 2.4, "dy": 3.4, "blur": 2.0, "opacity": 0.36}}


def letters():
    out = [H.class_disc(U, 253, 143, "G"), H.class_disc(U, 396, 331, "D"), H.class_disc(U, 128, 214, "C"), H.class_disc(U, 190, 96, "C"), H.class_disc(U, 560, 300, "C")]
    out.append(H.label("OETH", T[0] - 14, T[1] + 1, 6.4, H.INK, anchor="end"))
    out.append(H.label("OERK", K[0] - 28, K[1] + 8, 6.4, H.INK, anchor="end"))
    return "".join(out)


def rim(centre, toward, r):
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


def callouts():
    c = S.callout
    out = []
    # 1 the Thumamah zone
    d1 = (238, 84)
    a = math.atan2(d1[1] - T[1], d1[0] - T[0])
    out.append(c(1, *d1, T[0] + math.cos(a) * ATZ["r"], T[1] + math.sin(a) * ATZ["r"], r=10))
    # 2 the terminal control areas (west part and east part)
    d2 = (92, 170)
    out.append(c(2, *d2, *rim((128, 214), d2, 8), r=10))
    # 3 the final director area: its corner
    d3 = (556, 262)
    out.append(c(3, *d3, FDA["pts"][2][0], FDA["pts"][2][1], r=10))
    # 4 the control zone of Riyadh
    d4 = (504, 336)
    yy = 336.0
    xx = CTR["cx"] + math.sqrt(CTR["r"] ** 2 - (yy - CTR["cy"]) ** 2)
    out.append(c(4, *d4, xx, yy, r=10))
    # 5 and 6 the reporting points
    d5, d6 = (338, 80), (430, 210)
    out.append(c(5, *d5, *rim(NV, d5, 6.0), r=10))
    out.append(c(6, *d6, *rim(EV, d6, 6.0), r=10))
    # 7, 8, 9 the special use areas
    p7 = PRD["OED25"]["pts"]
    west = min(p7, key=lambda p: p[0])
    out.append(c(7, 176, 24, west[0], west[1], r=10))
    p8 = PRD["OER212"]["pts"]
    xs8 = [p[0] for p in p8]
    ys8 = [p[1] for p in p8]
    out.append(c(8, 586, max(ys8) + 28, 586, max(ys8), r=10))
    p9 = PRD["OED33"]["pts"]
    xs9 = [p[0] for p in p9]
    ys9 = [p[1] for p in p9]
    out.append(c(9, 86, min(ys9) - 30, 86, min(ys9), r=10))
    # 10 the runway, 11 the route
    out.append(c(10, 248, 206, T[0] + 1, T[1] + 14, r=10))
    mid3 = H.lerp(EV, T, 0.32)
    out.append(c(11, 356, 224, mid3[0], mid3[1], r=10))
    # 12 the scale
    out.append(c(12, 604, 378, 545, 378, r=10))
    return "".join(out)


def layers():
    out = [H.defs(U, W, HT), f'<g filter="url(#{U}warm)">', {"name": "terrain-17-07-saudi", "at": [W / 2, HT / 2], "width": W}, "</g>", H.vignette(U, W, HT), grid(), airspace(), special_use(), riyadh_runways()]
    out.append(H.route(U, ROUTE, 5.2, head_len=13.0, chevrons=0, mid_heads=head_marks()))
    out.append(thumamah_runway())                                  # the runway lies over the two ends of the ribbon: the route starts and ends at the aerodrome
    out.append(H.vrp(U, *NV, 11.0) + H.vrp(U, *EV, 11.0))
    out.append(plane())
    out.append(letters())
    out.append(H.north_arrow(U, 612, 296, 30))
    out.append(H.scale_bar(U, 480, 378, 5 * SCALE))
    out.append(callouts())
    return out


def plate():
    return {
        "id": "fig-17-07-route-plan-view",
        "replaces": "fig-17-07-route-plan-view.svg",
        "book_file": "plate-17-07-route-plan-view.jpg",
        "caption": "Figure 17-7. The worked example in plan view: a local flight from Thumamah",
        "desc": "Figure 17-7. The worked example in plan view: a local flight from Thumamah. North up; limits from the AIP (AMDT 11/26); not for navigation.",
        "legend": [
            "The Thumamah ATZ, Class G: radius 5 NM, surface to 3 000 ft AMSL.",
            "The Riyadh terminal control areas (East and West), Class C, from 700 ft above the ground: all the ground in the frame except the ATZ and the control zone.",
            "The Riyadh final director area for runway 15L, Class C, 700 ft above the ground to 11 000 ft AMSL: it covers the ATZ.",
            "The Riyadh control zone, Class D: radius 10 NM, surface to 4 500 ft AMSL.",
            "The North VRP.",
            "The East VRP.",
            "Danger area OED25: military, active by NOTAM, surface to 4 200 ft AMSL.",
            "Restricted area OER212: permanent, surface to 500 ft above the ground.",
            "Danger area OED33: firing, activity and height notified by NOTAM, surface to 4 500 ft AMSL.",
            "Thumamah, runway 17/35.",
            "The route: Thumamah, North VRP, East VRP, Thumamah.",
            "Scale: 5 NM.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-17-07-route-plan-view.svg", "blank": True, "layers": layers()},
    }
