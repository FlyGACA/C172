"""Figure 18-7 (the Saudi round). The aerodrome traffic circuit from above and from the side: runway 35 at Thumamah (OETH).

Top panel: the aerodrome of Thumamah to scale (figs/h_b4.py draws the runway, stopways, pavements, buildings and road from data/oeth_plan.json, as figure 18-1 does) with the left-hand circuit
for runway 35 as a thick ribbon with arrowheads, the right-hand circuit for runway 17 on the same (west) side thin and dashed, five aeroplanes of the model on the circuit, the 45 degree
line and the abeam line, the joining line and the two ways of leaving. North is to the left (the arrow says so), the runway lies along the page. Bottom panel: the circuit unrolled, the
ground at 1 870 ft and the downwind leg at 2 900 ft AMSL. The AIP (AD 2.22.2) gives the directions (35 left-hand, 17 right-hand, both on the west side) and the altitude (2 900 ft AMSL,
1 030 ft above the aerodrome) and nothing about the size of the circuit: its rectangle is illustrative. Thumamah has no windsock in the AIP: none is drawn."""
from figs import h_a1 as A1
from figs import h_a2 as H2
from figs import h_b4 as B
from figs import scene as S
from figs import terrain

W, HT = 640, 610
terrain.ensure("terrain-18-07-thumamah", size=(W * 4, HT * 4), seed=1806, kind="plain", features=("wadis",), veil=0.34, soft=2.8)

PX, PY, PW, PH = 8, 8, 624, 316                    # the plan panel (the circuit is a long, shallow loop: it needs less height than the old figure's)
SX, SY, SW, SH = 8, 334, 624, 268                  # the side panel
K = 0.0775                                         # units to the metre: about 12.9 m to a unit (the whole circuit, 6.9 km, must lie in the panel)
P = B.Plan(187.0, 92.0, K)
SPR = {"shadow": {"dx": 0.9, "dy": 1.5, "blur": 1.1, "opacity": 0.34}, "outline": {"width": 0.35, "colour": "#2B3648", "opacity": 0.8}}

D35, R = 1000.0, 300.0
C35 = B.circuit35(D=D35, R=R)
C17 = B.circuit35(D=D35 + 180.0, R=R).mirrored(B.S_S)


def plan_markup():
    out = [f'<defs><clipPath id="b4pc"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9"/></clipPath></defs>', f'<g clip-path="url(#b4pc)">', B.ground_card(PX, PY, PW, PH, 0.2)]
    out.append(B.aerodrome(P))
    f = P.xy
    # the circuit for runway 17 (right-hand, same side): thin, dashed, violet, under the thick ribbon
    out.append(B.dashed_runs(P, C17, B.VIOLET, w=1.5, dash="5 3.2"))
    out.append(B.heads_on(P, C17, [C17.marks["liftoff"] + 700, C17.marks["cross_start"] + 600, C17.marks["downwind"] + 3600, C17.marks["base_start"] + 700, C17.marks["final"] + 300], length=5.6, width=5.8, fill=B.VIOLET))
    # the construction lines of the old figure: the abeam line and the 45 degree line from the threshold to the downwind leg
    thr = f(B.S_S, 0.0)
    abeam = f(B.S_S, D35)
    diag = f(B.S_S + D35, D35)
    out.append(f'<line x1="{thr[0]:.1f}" y1="{thr[1] + 3:.1f}" x2="{abeam[0]:.1f}" y2="{abeam[1]:.1f}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.2" stroke-linecap="round"/>'
               f'<line x1="{thr[0]:.1f}" y1="{thr[1] + 3:.1f}" x2="{abeam[0]:.1f}" y2="{abeam[1]:.1f}" stroke="#5B6579" stroke-width="1.15" stroke-dasharray="2.2 3" stroke-linecap="round"/>')
    out.append(f'<line x1="{thr[0] + 2:.1f}" y1="{thr[1] + 2:.1f}" x2="{diag[0]:.1f}" y2="{diag[1]:.1f}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.2" stroke-linecap="round"/>'
               f'<line x1="{thr[0] + 2:.1f}" y1="{thr[1] + 2:.1f}" x2="{diag[0]:.1f}" y2="{diag[1]:.1f}" stroke="#5B6579" stroke-width="1.15" stroke-dasharray="2.2 3" stroke-linecap="round"/>')
    ar = 34.0
    out.append(f'<path d="M {thr[0]:.1f} {thr[1] + ar:.1f} A {ar} {ar} 0 0 0 {thr[0] + ar * 0.7071:.1f} {thr[1] + ar * 0.7071:.1f}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.4" stroke-linecap="round"/>'
               f'<path d="M {thr[0]:.1f} {thr[1] + ar:.1f} A {ar} {ar} 0 0 0 {thr[0] + ar * 0.7071:.1f} {thr[1] + ar * 0.7071:.1f}" fill="none" stroke="#5B6579" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(f'<text x="{thr[0] + 20:.1f}" y="{thr[1] + 55:.1f}" font-family="sans-serif" font-size="12" font-weight="bold" fill="{B.INK}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.85" paint-order="stroke">45°</text>')
    # leaving the circuit: straight out, or with a 45 degree turn in the direction of the circuit (left)
    lo = [f(-760.0, -45.0), f(-2000.0, -45.0)]
    out.append(B.dashed_route(lo, B.ORANGE, w=1.8, dash="6 4", casing=1.2, shadow=False))
    out.append(B.head(lo[1][0], lo[1][1], -1.0, 0.0, 8.0, 8.4, B.ORANGE))
    br = [f(-1560.0, -45.0), f(-1560.0 - 450.0, -45.0 + 450.0)]
    out.append(B.dashed_route(br, B.ORANGE, w=1.8, dash="6 4", casing=1.2, shadow=False))
    ux, uy = -0.7071, 0.7071
    out.append(B.head(br[1][0], br[1][1], ux, uy, 8.0, 8.4, B.ORANGE))
    # joining: a dashed line at 45 degrees to the middle of the downwind leg
    jm = f(2150.0, D35)
    jt = f(2150.0 - 1350.0, D35 + 1350.0)
    out.append(B.dashed_route([jt, jm], B.GREEN, w=2.0, dash="6.5 4", casing=1.2, shadow=False))
    out.append(B.head(jm[0] + 0.5, jm[1] + 3.5, 0.7071, -0.7071, 8.0, 8.6, B.GREEN))
    # the circuit for runway 35: the ribbon, its arrowheads, the marks
    page35 = [f(s, t) for s, t in C35.pts]
    wc = [B.strip_width(s, t) for s, t in C35.pts]
    out.append(B.ribbon_poly(page35, [a for a, _ in wc], [b for _, b in wc]))
    m = C35.marks
    out.append(B.heads_on(P, C35, [m["up_end"] - 90, m["cross_start"] + 700, m["downwind"] + 900, m["downwind"] + 4300, m["base_start"] + 700, m["final"] + 650], length=7.6, width=8.0))
    # the marks: the checks (square) and the abeam point (ring)
    out.append(B.square_mark(*f(3300.0, D35)))
    out.append(B.ring(*f(B.S_S, D35)))
    out.append("</g>")
    return "".join(out)


def plan_sprites():
    f = P.xy
    out = []
    w = 21.0

    def sp(s, t, angle, width=w, **kw):
        x, y = f(s, t)
        out.append({"name": "sprite-top", "at": [round(x, 1), round(y, 1)], "width": width, "angle": angle, **SPR, **kw})
    sp(-330.0, 0.0, 270)                       # upwind
    sp(1250.0, D35, 90)                        # downwind
    sp(B.S_S + D35 + R, 600.0, 0)               # base (flowing up the page)
    sp(4560.0, 0.0, 270)                       # final
    jx, jy = 2150.0 - 1350.0 * 0.34, D35 + 1350.0 * 0.34
    sp(jx, jy, 45, tint="#047857", tint_strength=0.55)   # joining
    return out


# ----------------------------------------------------------------------------------------------------- the side view: the circuit unrolled
GY = SY + SH - 36.0                                  # the ground line (1 870 ft AMSL)
VS = 0.158                                           # units to the foot (height exaggerated: the circuit is 14 km long and 1 030 ft high)
LIFT = B.LINE_UP_BEFORE_LIFT
M = C35.marks
ABEAM_D = LIFT + M["downwind"] + (B.S_S - (-700.0))
XMAP = [(0.0, 70.0), (LIFT, 90.0), (LIFT + M["up_end"], 230.0), (LIFT + M["downwind"], 281.0), (ABEAM_D, 447.0), (LIFT + M["downwind_end"], 479.0), (LIFT + M["final"], 540.0), (LIFT + M["end"], 598.0)]
PROF = B.Profile(XMAP, GY, VS, B.profile_knots(C35))
YDW = PROF.y_of_h(B.ABOVE_FT)                        # the downwind leg, 2 900 ft AMSL


def d_of(mark, plus=0.0):
    return LIFT + C35.marks[mark] + plus


def side_back():
    runways = ((66.0, PROF.x(d_of("up_end")) + 6), (PROF.x(LIFT + C35.marks["end"] - 310.0), SX + SW))
    clouds = [A1.cloud("cloud-cumulus-b", 52, SY + 28, 62, 0.92), A1.cloud("cloud-cumulus-a", 596, SY + 24, 70, 0.92)]
    return B.side_scene("b4p", (SX, SY, SW, SH), GY, PROF, 186, runways, clouds=clouds)


def side_markup():
    out = []
    # the circuit altitude as a dashed line across the card, the ground line, the bracket between them
    out.append(S.altitude_line(SX + 10, SX + SW - 10, YDW, colour="#3E5F8F", opacity=0.75, dash="6 4", width=1.3))
    out.append(B.bracket(60.0, YDW, GY, 6.0))
    out.append(B.label(14.0, YDW - 5.0, "2\u2002900 ft", 11.5, "start"))
    out.append(B.label(14.0, GY - 7.0, "1\u2002870 ft", 11.5, "start"))
    out.append(B.label(70.0, (YDW + GY) / 2 + 4.0, "1\u2002030 ft", 11.5, "start"))
    # the route: a ribbon with arrowheads
    pts_ = B.route_curve(PROF)
    out.append(B.air_under("b4air", pts_, GY, top_op=0.30, bottom_op=0.03))
    out.append(B.ribbon_line(pts_, w=3.4))
    for d in (2300.0, d_of("cross_start", 250.0), d_of("downwind", 1500.0), d_of("base_start", 560.0), d_of("final", 600.0)):
        x, y = PROF.point(d)
        ux, uy = PROF.unit(d)
        out.append(B.head(x + ux * 4.0, y + uy * 4.0, ux, uy, 7.6, 8.0))
    # the marks: the checks and the abeam point
    out.append(B.square_mark(*PROF.point(d_of("downwind", 4000.0)), s=6.0))
    out.append(B.ring(*PROF.point(ABEAM_D), r=4.2))
    return "".join(out)


def side_sprites():
    out = []
    for d, w, k in ((2300.0, 44.0, 0.62), (d_of("cross_start", 330.0), 42.0, 0.55), (d_of("downwind", 1500.0), 46.0, 0.0), (d_of("base_start", 400.0), 38.0, 0.5), (d_of("final", 760.0), 38.0, 0.5)):
        x, y = PROF.point(d)
        ang = PROF.slope(d) * k
        h = w * A1.ASPECT
        out.append({"name": "sprite-side", "at": [round(x, 1), round(y - h * 0.58, 1)], "width": w, "angle": round(ang, 1), "shadow": {"dx": 1.0, "dy": 1.8, "blur": 1.4, "opacity": 0.24}, "outline": {"width": 0.4, "colour": "#2B3648", "opacity": 0.85}})
    return out


def callouts():
    c = S.callout
    f = P.xy
    out = []
    # the plan: (number, disc, target in the frame)
    for k, disc, (s, t) in ((1, (140.0, 50.0), (-560.0, 0.0)), (2, (146.0, 128.0), (-1000.0, 520.0)), (3, (252.0, 206.0), (800.0, D35)), (4, (618.0, 102.0), (B.S_S + D35 + R, 330.0)),
                            (5, (556.0, 52.0), (4850.0, 0.0)), (6, (224.0, 296.0), (800.0, D35 + 1350.0)), (7, (440.0, 206.0), (3300.0, D35)), (8, (497.0, 206.0), (B.S_S, D35)),
                            (9, (466.0, 138.0), (B.S_S + D35 * 0.5, D35 * 0.5)), (10, (66.0, 52.0), (-1500.0, -45.0))):
        tx, ty = f(s, t)
        out.append(c(k, disc[0], disc[1], round(tx, 1), round(ty, 1)))
    # the side view: (number, distance flown, offset of the disc from the point)
    for k, d, (dx, dy) in ((1, 2000.0, (32.0, 18.0)), (2, d_of("cross_start", 330.0), (-38.0, -38.0)), (3, d_of("downwind", 2800.0), (0.0, -38.0)), (7, d_of("downwind", 4000.0), (0.0, 40.0)),
                           (8, ABEAM_D, (6.0, -38.0)), (4, d_of("base_start", 400.0), (38.0, -30.0)), (5, d_of("final", 760.0), (30.0, -38.0))):
        x, y = PROF.point(d)
        out.append(c(k, round(x + dx, 1), round(y + dy, 1), round(x, 1), round(y, 1)))
    return "".join(out)

def layers():
    return [{"name": "terrain-18-07-thumamah", "at": [W / 2, HT / 2], "width": W}, B.defs(), A1.defs(), plan_markup(), *plan_sprites(), B.frame(PX, PY, PW, PH),
            B.north_arrow(PX + PW - 34, PY + 32), B.scale_bar(PX + PW - 26 - 1000 * K - 40, PY + PH - 20, 1000 * K, "1 km"),
            *side_back(), side_markup(), *side_sprites(), callouts()]


def plate():
    return {
        "id": "fig-18-07-circuit",
        "replaces": "fig-18-07-circuit.svg",
        "book_file": "plate-18-07-circuit.jpg",
        "caption": "Figure 18-7. The aerodrome traffic circuit from above and from the side: runway 35 at Thumamah",
        "desc": "Figure 18-7. The aerodrome traffic circuit from above and from the side: runway 35 at Thumamah. North is to the left, as the arrow shows; the shape of the circuit is illustrative, its direction and altitude are the AIP's (AMDT 11/26); not for navigation.",
        "legend": [
            "Upwind leg: climb straight ahead after takeoff.",
            "Crosswind leg, at right angles to the runway beyond its end.",
            "Downwind leg, parallel to the runway, at circuit height.",
            "Base leg, descending.",
            "Final approach, lined up with the runway.",
            "Joining on a 45° line towards the middle of the downwind leg, at circuit height.",
            "Downwind checks.",
            "Abeam the threshold: reduce power and begin the descent.",
            "Turn on to base when the threshold is about 45° behind you.",
            "Leaving: straight out, or with a 45° turn in the direction of the circuit.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-07-circuit.svg", "blank": True, "layers": layers()},
    }
