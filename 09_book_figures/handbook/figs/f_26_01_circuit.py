"""Figure 26-1 (the Saudi round). The circuit in the example aeroplane, with speed and flap setting at each point: runway 35 at Thumamah (OETH), left-hand, wind from the north.

The same ground and the same circuit as figure 18-7 (figs/h_b4.py): the aerodrome to scale from data/oeth_plan.json, north to the left (the arrow says so), the left-hand circuit for runway 35 on
the west side as a ribbon with arrowheads, five aeroplanes of the model on it, the abeam line and the 45 degree line, the old figure's five tags (speed and flap setting, with the small
aeroplane of the model and the flap as a bar turned down by its angle: figs/h_a1.py speed_card, as in figure 26-2) and its ten numbered callouts. Below, the circuit unrolled in a card of sky: the
ground at 1 870 ft and the circuit altitude 2 900 ft AMSL (AIP AD 2.22.2). The wind from the north is a pair of pale ribbons blowing to the south (the old figure's windsock is not drawn: the AIP
lists none for Thumamah). The shape of the circuit is illustrative: the AIP gives its directions and altitude and no size."""
from figs import h_a1 as A1
from figs import h_a4 as A4
from figs import h_b4 as B
from figs import scene as S
from figs import terrain

W, HT = 640, 450
terrain.ensure("terrain-26-01-thumamah", size=(W * 4, HT * 4), seed=2601, kind="plain", features=("wadis",), veil=0.34, soft=2.8)

PX, PY, PW, PH = 8, 4, 624, 230                    # the plan panel
SX, SY, SW, SH = 8, 242, 624, 200                  # the side panel
K = 0.0775                                         # units to the metre, as in figure 18-7
P = B.Plan(112.0, 84.0, K)
SPR = {"shadow": {"dx": 0.9, "dy": 1.5, "blur": 1.1, "opacity": 0.34}, "outline": {"width": 0.35, "colour": "#2B3648", "opacity": 0.8}}

D35, R = B.DOWNWIND, B.CORNER
C35 = B.circuit35(D=D35, R=R)
M = C35.marks
LIFT = B.LINE_UP_BEFORE_LIFT
S_LINEUP, S_ROTATE, S_AIM = 3975.0, 3275.0, 3694.6


def plan_markup():
    f = P.xy
    out = [f'<defs><clipPath id="b4pc"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9"/></clipPath></defs>', '<g clip-path="url(#b4pc)">', B.ground_card(PX, PY, PW, PH, 0.2)]
    out.append(B.aerodrome(P))
    out.append(B.construction(P, D35))
    page35 = [f(s, t) for s, t in C35.pts]
    wc = [B.strip_width(s, t) for s, t in C35.pts]
    out.append(B.ribbon_poly(page35, [a for a, _ in wc], [b for _, b in wc]))
    out.append(B.heads_on(P, C35, [M["up_end"] - 20, M["downwind"] + 1000, M["downwind"] + 3700, M["base_start"] + 650, M["final"] + 760], length=7.6, width=8.0))
    # the aiming point: the two bold stripes of the marking beside the centreline, then the marks of the route
    for sg in (-1, 1):
        a, b = f(S_AIM + 22.0, sg * 11.0), f(S_AIM - 22.0, sg * 11.0)
        out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#F8F6EE" stroke-width="1.0"/>')
    out.append(B.ring(*f(S_LINEUP, 0.0), r=4.2))
    out.append(B.dot_mark(*f(S_ROTATE, 0.0)))
    for s, t in ((-500.0, 0.0), (-1000.0, 360.0), (900.0, D35), (B.S_S + D35 + R, 330.0), (4850.0, 0.0)):
        out.append(B.small_ring(*f(s, t)))
    out.append(B.ring(*f(B.S_S, D35), r=4.4))
    ax, ay = f(S_AIM, 0.0)
    out.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="4.1" fill="#FFFFFF" fill-opacity="0.6"/><circle cx="{ax:.1f}" cy="{ay:.1f}" r="3.1" fill="#FFFFFF" stroke="{B.ORANGE}" stroke-width="1.5"/>')
    out.append("</g>")
    return "".join(out)


def plan_sprites():
    f = P.xy
    out = []

    def sp(s, t, angle, width=22.0):
        x, y = f(s, t)
        out.append({"name": "sprite-top", "at": [round(x, 1), round(y, 1)], "width": width, "angle": angle, **SPR})
    sp(-260.0, 0.0, 270)                       # climbing out
    sp(-1000.0, 640.0, 180)                    # crosswind (flowing down the page)
    sp(1850.0, D35, 90)                        # downwind
    sp(B.S_S + D35 + R, 640.0, 0)              # base (flowing up the page)
    sp(4540.0, 0.0, 270)                       # final
    return out


def wind():
    """Wind from the north: two pale ribbons blowing to the south (to the right of the page and 9 degrees down it: north is 9 degrees from the runway's axis)."""
    out = []
    for k, (x, y) in enumerate(((178.0, 16.0), (178.0, 41.0))):
        out.append(A4.ribbon(f"b4w{k}", [(x, y), (x + 92.0, y + 14.6)], width=7.0, colours=("#5681BF", "#C1D7F2"), head=2.0, casing=2.0, casing_opacity=0.8, per=8))
    return "".join(out)


def tags():
    out = []
    out += A1.speed_card("b4t2", 46, 12, "VY 75", 0)
    out += A1.speed_card("b4t3", 292, 12, "VR 55", 0)
    out += A1.speed_card("b4t4", 545, 17, "65", 30, flap_colour="#F59E0B", mono=False)
    out += A1.speed_card("b4t5", 545, 96, None, 20, flap_colour="#F59E0B")
    out += A1.speed_card("b4t6", 462, 178, None, 10, flap_colour="#F59E0B")
    f = P.xy
    leaders = ((79.0, 54.0, *f(-500.0, 0.0)), (340.0, 54.0, *f(S_ROTATE, 0.0)), (545.0, 47.0, *f(4850.0, 0.0)), (545.0, 108.0, *f(B.S_S + D35 + R, 330.0)), (462.0, 190.0, *f(B.S_S, D35)))
    return A1.flatten(out), "".join(A1.leader(x1, y1, x2, y2) for x1, y1, x2, y2 in leaders)


# ----------------------------------------------------------------------------------------------------- the side view
GY = SY + SH - 30.0
VS = 0.115
XMAP, ABEAM_D = B.unrolled_xmap(C35)
PROF = B.Profile(XMAP, GY, VS, B.profile_knots(C35))
YDW = PROF.y_of_h(B.ABOVE_FT)


def d_of(mark, plus=0.0):
    return LIFT + M[mark] + plus


def side_back():
    runways = ((66.0, PROF.x(d_of("up_end")) + 6), (PROF.x(LIFT + M["end"] - 310.0), SX + SW))
    clouds = [A1.cloud("cloud-cumulus-b", 54, SY + 24, 58, 0.92), A1.cloud("cloud-cumulus-a", 598, SY + 22, 64, 0.92)]
    return B.side_scene("b4p", (SX, SY, SW, SH), GY, PROF, 2601, runways, clouds=clouds)


def side_markup():
    out = [S.altitude_line(SX + 10, SX + SW - 10, YDW, colour="#3E5F8F", opacity=0.75, dash="6 4", width=1.3)]
    out.append(B.label(14.0, YDW - 5.0, "2 900 ft", 11.5, "start"))
    out.append(B.label(14.0, GY - 7.0, "1 870 ft", 11.5, "start"))
    pts_ = B.route_curve(PROF)
    out.append(B.air_under("b4air", pts_, GY, top_op=0.30, bottom_op=0.03))
    out.append(B.ribbon_line(pts_, w=3.2))
    for d in (1500.0, d_of("cross_start", 450.0), d_of("downwind", 3500.0), d_of("base_start", 650.0), d_of("final", 950.0)):
        x, y = PROF.point(d)
        ux, uy = PROF.unit(d)
        out.append(B.head(x + ux * 4.0, y + uy * 4.0, ux, uy, 7.2, 7.6))
    for d in (d_of("liftoff"), 2300.0, d_of("cross_start", 330.0), d_of("downwind", 2200.0), d_of("base_start", 330.0), d_of("final", 560.0)):
        out.append(B.small_ring(*PROF.point(d), r=2.6))
    out.append(B.dot_mark(*PROF.point(d_of("liftoff"))))
    out.append(B.ring(*PROF.point(ABEAM_D), r=4.0))
    x, y = PROF.point(LIFT + M["end"])
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.0" fill="#FFFFFF" fill-opacity="0.6"/><circle cx="{x:.1f}" cy="{y:.1f}" r="3.0" fill="#FFFFFF" stroke="{B.ORANGE}" stroke-width="1.5"/>')
    return "".join(out)


def side_sprites():
    out = []
    for d, w, k in ((2750.0, 42.0, 0.6), (d_of("downwind", 1100.0), 44.0, 0.0), (d_of("base_start", 780.0), 38.0, 0.5)):
        x, y = PROF.point(d)
        ang = PROF.slope(d) * k
        h = w * A1.ASPECT
        out.append({"name": "sprite-side", "at": [round(x, 1), round(y - h * 0.58, 1)], "width": w, "angle": round(ang, 1), "shadow": {"dx": 1.0, "dy": 1.8, "blur": 1.4, "opacity": 0.24}, "outline": {"width": 0.4, "colour": "#2B3648", "opacity": 0.85}})
    return out


def callouts():
    c = S.callout
    f = P.xy
    out = []
    for k, disc, (s, t) in ((1, (452.0, 40.0), (S_LINEUP, 0.0)), (2, (386.0, 38.0), (S_ROTATE, 0.0)), (3, (96.0, 118.0), (-500.0, 0.0)), (4, (68.0, 146.0), (-1000.0, 360.0)),
                            (5, (200.0, 198.0), (900.0, D35)), (6, (422.0, 204.0), (B.S_S, D35)), (7, (560.0, 156.0), (B.S_S + D35 + R, 330.0)), (8, (516.0, 40.0), (4850.0, 0.0)),
                            (9, (418.0, 48.0), (S_AIM, 0.0))):
        tx, ty = f(s, t)
        out.append(c(k, disc[0], disc[1], round(tx, 1), round(ty, 1)))
    out.append(c(10, 150.0, 36.0, 182.0, 25.0))                     # the wind: its leader ends on the tail of the first ribbon
    for k, d, (dx, dy) in ((2, d_of("liftoff"), (-26.0, -36.0)), (3, 2300.0, (-34.0, -30.0)), (4, d_of("cross_start", 330.0), (-34.0, -30.0)), (5, d_of("downwind", 2200.0), (0.0, -34.0)),
                           (6, ABEAM_D, (6.0, -34.0)), (7, d_of("base_start", 330.0), (34.0, -26.0)), (8, d_of("final", 560.0), (24.0, -42.0)), (9, LIFT + M["end"], (-32.0, 12.0))):
        x, y = PROF.point(d)
        out.append(c(k, round(x + dx, 1), round(y + dy, 1), round(x, 1), round(y, 1)))
    return "".join(out)


def layers():
    tag_layers, tag_leaders = tags()
    return [{"name": "terrain-26-01-thumamah", "at": [W / 2, HT / 2], "width": W}, B.defs(), A1.defs(), plan_markup(), *plan_sprites(), wind(), tag_leaders, *tag_layers, B.frame(PX, PY, PW, PH),
            B.north_arrow(PX + PW - 34, PY + PH - 36), B.scale_bar(PX + 24, PY + PH - 20, 1000 * K, "1 km"),
            *side_back(), side_markup(), *side_sprites(), callouts()]


def plate():
    return {
        "id": "fig-26-01-circuit",
        "replaces": "fig-26-01-circuit.svg",
        "book_file": "plate-26-01-circuit.jpg",
        "caption": "Figure 26-1. The circuit in the example aeroplane, with speed and flap setting at each point",
        "desc": "Figure 26-1. The circuit in the example aeroplane, with speed and flap setting at each point. Runway 35 at Thumamah, left-hand; not for navigation.",
        "legend": [
            "Line up on runway 35, checks complete (Chapter 25), flaps up in this example.",
            "Full power; rotate at `VR` 55 kt.",
            "Climb at `VY` 75 kt; after-takeoff checks at a safe height.",
            "Crosswind turn to the left beyond the runway end, no lower than your school's height.",
            "Downwind at the circuit altitude, 2 900 ft AMSL: circuit power, before-landing checks.",
            "Abeam the threshold: power back, descent begins; below `VFE` 90 kt, flaps 10°.",
            "Base, with the threshold about 45° behind: flaps 20°. Look along final first.",
            "Final: flaps 30°, 65 kt, stable by the gate (Figure 26-3).",
            "The aiming point.",
            "Wind from the north.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-26-01-circuit.svg", "blank": True, "layers": layers()},
    }
