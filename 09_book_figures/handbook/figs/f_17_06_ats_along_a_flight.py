"""Figure 17-6. The air traffic services a VFR flight meets from departure to arrival: a plan of the flight from Riyadh King Khalid (OERK) to Thumamah (OETH), 15.5 NM on the true
bearing 346 degrees, on an aerial view of the plain, drawn to scale from the AIP (AMDT 11/26) data of data/saudi_airspace.json (frame: an equirectangular projection round the middle of
the two aerodromes, 17 canvas units to the NM, north up). The Riyadh control zone (Class D, 10 NM round OERK), the Thumamah aerodrome traffic zone (Class G, 5 NM round OETH), the final
director area for runway 15L (Class C, the rotated rectangle of the file) and the terminal control area (Class C: the faint indigo over all the ground, with the two zones cut out of it);
the runways as bars; the route as a ribbon with the model's aeroplane on it; the services as small icons (a tower, a hand-over, the UNICOM, the TIBA broadcasts, the arrival report) with
a band of amber under the whole route for the alerting service. No words: digits, class letters in discs, the ICAO codes and the scale."""
from figs import h_b2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 400
U = "b26"
SCALE = 17.0                                                         # canvas units to the NM

terrain.ensure("terrain-17-06-saudi", size=(W * 4, HT * 4), seed=1706, kind="plain", features=(), veil=0.42, soft=3.0)

OETH, OERK = H.DATA["oeth"], H.DATA["oerk"]
MID = ((OETH["arp"]["lat"] + OERK["arp"]["lat"]) / 2, (OETH["arp"]["lon"] + OERK["arp"]["lon"]) / 2)
F = H.Frame(MID[0], MID[1], SCALE, 320.0, 227.0)                    # the middle of the two aerodromes lies at (320, 227): the Thumamah zone is whole at the top, the Riyadh runways at the foot

T = F.xy(OETH["arp"]["lon"], OETH["arp"]["lat"])                    # Thumamah ARP
K = F.xy(OERK["arp"]["lon"], OERK["arp"]["lat"])                    # Riyadh ARP
ATZ = H.circle(T[0], T[1], F.r(OETH["atz"]["radius_nm"]))
CTR = H.circle(K[0], K[1], F.r(OERK["ctr"]["radius_nm"]))
FDA = H.poly(F.ring(H.DATA["areas"]["riyadh_final_director_east_15l"]["ring"][:-1]))
HEADING = 346.0                                                      # the reverse of the file's 166 degrees


def thr(rw):
    return F.xy(rw["threshold"]["lon"], rw["threshold"]["lat"])


def runways():
    out = []
    for a, b in (("15L", "33R"), ("15R", "33L")):
        ra = next(r for r in OERK["runways"] if r["id"] == a)
        rb = next(r for r in OERK["runways"] if r["id"] == b)
        out.append(H.runway(U, thr(ra), thr(rb), 3.2))
    r17 = next(r for r in OETH["runways"] if r["id"] == "17")
    r35 = next(r for r in OETH["runways"] if r["id"] == "35")
    out.append(H.runway(U, thr(r17), thr(r35), 3.2))
    return "".join(out)


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


def airspace():
    out = [H.hole_mask(U + "mt", W, HT, [(CTR["cx"], CTR["cy"], CTR["r"]), (ATZ["cx"], ATZ["cy"], ATZ["r"])]),      # the terminal control area excludes both zones
           H.hole_mask(U + "mf", W, HT, [(CTR["cx"], CTR["cy"], CTR["r"])])]                                       # the final director area excludes the control zone only
    # the terminal control area: the faint indigo over all the ground of the frame (its limit lies outside the frame)
    out.append(H.fill(H.poly([(0, 0), (W, 0), (W, HT), (0, HT)]), "C", 0.13, mask=U + "mt"))
    out.append(H.fill(FDA, "C", mask=U + "mf"))
    out.append(H.fill(CTR, "D"))
    out.append(H.fill(ATZ, "G"))
    out.append(H.gloss(U + "f", FDA, 0.22, mask=U + "mf"))
    out.append(H.gloss(U + "c", CTR, 0.34))
    out.append(H.gloss(U + "a", ATZ, 0.34))
    out.append(f'<g mask="url(#{U}mf)">' + H.inner_glow(U + "f", FDA, "C", 12, 0.22) + "</g>")
    out.append(H.inner_glow(U + "c", CTR, "D", 14, 0.30))
    out.append(H.inner_glow(U + "a", ATZ, "G", 12, 0.30))
    out.append(H.edge(FDA, "C", mask=U + "mf", uid=U))
    out.append(H.edge(CTR, "D", uid=U))
    out.append(H.edge(ATZ, "G", uid=U))
    return "".join(out)


R0 = thr(next(r for r in OERK["runways"] if r["id"] == "15L"))    # the north-western end of Riyadh's eastern runway: where a flight to the north-north-west leaves the ground
R1 = thr(next(r for r in OETH["runways"] if r["id"] == "35"))     # the threshold of Thumamah's runway 35, at its southern end: where the flight lands
N_END = thr(next(r for r in OETH["runways"] if r["id"] == "17"))  # the northern end of the same runway


def on_route(nm_from_start, side=0.0):
    """The canvas point `nm_from_start` NM from the start of the route, `side` canvas units to the left of the direction of flight (negative: to the right)."""
    d = H.dist(R0, R1)
    ux, uy = (R1[0] - R0[0]) / d, (R1[1] - R0[1]) / d
    return (R0[0] + ux * nm_from_start * SCALE + uy * side, R0[1] + uy * nm_from_start * SCALE - ux * side)


def route_points():
    return [R0, R1]


def rim(centre, toward, r=10.0):
    """The point on the rim of a badge (centre, radius r) that lies towards `toward`: where a leader ends on an icon."""
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


TOWER = (K[0] + 27, K[1] - 12)                                       # the control tower of Riyadh (its place is not in the file: the symbol stands by the reference point)
UNICOM = (T[0] + 22, T[1] - 4)
TIBA = on_route(11.1)                                               # on the route, just inside the edge of the Thumamah zone
BELL = on_route(2.4, 17.0)
TICK = (N_END[0] - 13, N_END[1] - 15)
NECK = on_route(9.36)                                               # the stretch of the route between the two zones (0.5 NM)
BADGE = 10.0


def icons():
    return "".join([H.tower_icon(U, *TOWER, BADGE), H.speaker(U, *UNICOM, BADGE), H.megaphone(U, *TIBA, BADGE), H.bell(U, *BELL, BADGE), H.tick(U, *TICK, BADGE)])


def plane():
    p = on_route(5.4)
    return {"name": "sprite-top", "at": [p[0], p[1]], "width": 38, "angle": HEADING, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.9}, "shadow": {"dx": 2.8, "dy": 4.0, "blur": 2.4, "opacity": 0.36}}


def letters():
    out = [H.class_disc(U, T[0] + 44, T[1] - 52, "G"), H.class_disc(U, K[0] + 90, K[1] - 64, "D"), H.class_disc(U, 168, 132, "C"), H.class_disc(U, 452, 120, "C")]
    out.append(H.label("OETH", T[0] - 25, T[1] - 4, 7.0, H.INK, anchor="end"))
    out.append(H.label("OERK", K[0] - 44, K[1] + 24, 7.0, H.INK, anchor="end"))
    return "".join(out)


def callouts():
    c = S.callout
    d1, d2, d3, d4, d5, d6 = (414, 330), (228, 204), (372, 165), (338, 132), (T[0] - 46, T[1] - 36), (286, 292)
    on_cto = (303.0, 191.5)                                          # on the edge of the control zone, just beside the route
    return "".join([c(1, *d1, *rim(TOWER, d1, BADGE), r=10), c(2, *d2, *on_cto, r=10), c(3, *d3, *NECK, r=10), c(4, *d4, *rim(TIBA, d4, BADGE), r=10),
                    c(5, *d5, *rim(TICK, d5, BADGE), r=10), c(6, *d6, *rim(BELL, d6, BADGE), r=10)])


def layers():
    out = [H.defs(U, W, HT), f'<g filter="url(#{U}warm)">', {"name": "terrain-17-06-saudi", "at": [W / 2, HT / 2], "width": W}, "</g>", H.vignette(U, W, HT), grid(), airspace()]
    rp = route_points()
    out.append(H.band(U, rp + [N_END], 18.0, opacity=0.36))
    out.append(runways())
    out.append(H.route(U, rp, 5.0, head_len=13.5, chevrons=0, mid_heads=(0.2 * H.dist(R0, R1), 0.53 * H.dist(R0, R1))))
    out.append(icons())
    out.append(plane())
    out.append(letters())
    out.append(H.north_arrow(U, 608, 44, 30))
    out.append(H.scale_bar(U, 26, 376, 5 * SCALE))
    out.append(callouts())
    return out


def plate():
    return {
        "id": "fig-17-06-ats-along-a-flight",
        "replaces": "fig-17-06-ats-along-a-flight.svg",
        "book_file": "plate-17-06-ats-along-a-flight.jpg",
        "caption": "Figure 17-6. The air traffic services a VFR flight meets from departure to arrival",
        "desc": ("Figure 17-6. The air traffic services a VFR flight meets from departure to arrival. "
                 "North up; limits from the AIP (AMDT 11/26); the whole leg lies inside the Riyadh terminal control area except the two zones; not for navigation."),
        "legend": [
            "Riyadh King Khalid: the tower clears you to taxi and take off [[§91.99(f)]] [[§91.127(i)]].",
            "Leaving the Riyadh control zone (Class D): the tower hands you over to Riyadh Approach.",
            "In the Riyadh terminal control area (Class C): Riyadh Approach, which gives the clearance and the instructions, as far as the edge of the Thumamah ATZ.",
            "Approaching Thumamah, which has no tower: the UNICOM, and broadcasts on the TIBA frequency [[§91.121(d)]].",
            "After landing: the arrival report [[§91.73(h)]].",
            "The alerting service, from departure to the arrival report.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-17-06-ats-along-a-flight.svg", "blank": True, "layers": layers()},
    }
