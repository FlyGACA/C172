"""Figure 26-2 (the Saudi round). The circuit in the example aeroplane, with speed and flap setting at each point: runway 35 at Thumamah (OETH), left-hand, wind from the north.

The same ground and the same circuit as figure 18-7 (figs/h_b4.py): the aerodrome to scale from data/oeth_plan.json, north to the left (the arrow says so), the left-hand circuit for runway 35 on
the west side as a ribbon with arrowheads, five aeroplanes of the model on it, the abeam line and the 45 degree line, the old figure's five tags (speed and flap setting, with the small
aeroplane of the model and the flap as a bar turned down by its angle: figs/h_a1.py speed_card, as in figure 26-2) and its ten numbered callouts. Below, the circuit unrolled in a card of sky: the
ground at 1 870 ft and the circuit altitude 2 900 ft AMSL (AIP AD 2.22.2). The wind from the north is a pair of pale ribbons blowing to the south (the old figure's windsock is not drawn: the AIP
lists none for Thumamah). The shape of the circuit is illustrative: the AIP gives its directions and altitude and no size."""
import json
import os

from figs import h_a1 as A1
from figs import h_b4 as B
from figs import scene as S
from figs import terrain

W, HT = 640, 536
terrain.ensure("terrain-26-01-thumamah", size=(W * 4, HT * 4), seed=2601, kind="plain", features=("wadis",), veil=0.34, soft=2.8)

PX, PY, PW, PH = 8, 4, 624, 316                    # the top panel: the 3D view (figs/oeth3d.py circuit_26_02, blender/render_oeth.py)
SX, SY, SW, SH = 8, 328, 624, 200                  # the side panel

D35, R = B.DOWNWIND, B.CORNER
C35 = B.circuit35(D=D35, R=R)
M = C35.marks
LIFT = B.LINE_UP_BEFORE_LIFT
R3D = "oeth-26-02-circuit"                          # the 3D view of the top panel; its points (line-up, rotation, aiming point) are those of figs/oeth3d.circuit_26_02


# ----------------------------------------------------------------------------------------------------- the 3D view (the airport round)
def r3d():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders", R3D + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    w, h = d["size"]
    ih = PW * h / w
    y0 = PY + PH / 2 - ih / 2
    return lambda k: (round(PX + d["anchors"][k][0] * PW, 1), round(y0 + d["anchors"][k][1] * ih, 1))


_AT = []


def AT(k):
    """A point of the 3D view on the canvas (the anchors are read when the plate is laid out, after the render)."""
    if not _AT:
        _AT.append(r3d())
    return _AT[0](k)

CARD_W, CARD_H = 66.0, 42.0
# the five tags of the old figure, each at a free place of the picture, with a leader to its point
CARDS = (("b4t2", "climb", 548.0, 150.0, "VY 75", 0, None), ("b4t3", "rotate", 300.0, 262.0, "VR 55", 0, None), ("b4t4", "final", 16.0, 268.0, "65", 30, "#F59E0B"),
         ("b4t5", "base", 18.0, 150.0, None, 20, "#F59E0B"), ("b4t6", "abeam", 92.0, 96.0, None, 10, "#F59E0B"))


def plan3d():
    clip = (f'<defs><clipPath id="c3dq"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9"/></clipPath></defs><g clip-path="url(#c3dq)">')
    img = {"name": R3D, "at": [PX + PW / 2, PY + PH / 2], "width": PW, "whole": True}
    sky = (f'<defs><linearGradient id="c3dl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5D93D4"/><stop offset="0.6" stop-color="#A9CBEE"/>'
           f'<stop offset="1" stop-color="#E4EEF6"/></linearGradient></defs><rect x="{PX}" y="{PY}" width="{PW}" height="{PH * 0.25:.1f}" fill="url(#c3dl)"/>')
    marks = B.ring(*AT("lineup"), r=4.2) + B.dot_mark(*AT("rotate")) + B.ring(*AT("abeam"), r=4.4)
    ax, ay = AT("aim")
    marks += f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="4.1" fill="#FFFFFF" fill-opacity="0.6"/><circle cx="{ax:.1f}" cy="{ay:.1f}" r="3.1" fill="#FFFFFF" stroke="{B.ORANGE}" stroke-width="1.5"/>'
    for k in ("climb", "cross", "down", "base", "final"):
        marks += B.small_ring(*AT(k))
    (x0, y0), (x1, y1) = AT("n0"), AT("n1")
    north = B.north_arrow(PX + PW - 34, PY + PH - 34, (x1 - x0, y1 - y0))
    return [clip + sky, img, marks + north + "</g>" + f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="9" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>']


def tags3d():
    out, leaders = [], []
    for cid, pt, x, y, text, flap, col in CARDS:
        kw = {"flap_colour": col} if col else {}
        if cid == "b4t4":
            kw["mono"] = False
        out += A1.speed_card(cid, x, y, text, flap, **kw)
        tx, ty = AT(pt)
        lx, ly = min(max(tx, x), x + CARD_W), min(max(ty, y), y + CARD_H)      # the leader leaves the card at its point nearest the target
        leaders.append(A1.leader(lx, ly, tx, ty))
    return A1.flatten(out), "".join(leaders)


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
    out = []
    for k, pt, disc in ((1, "lineup", (214.0, 296.0)), (2, "rotate", (300.0, 186.0)), (3, "climb", (498.0, 170.0)), (4, "cross", (566.0, 84.0)), (5, "down", (398.0, 76.0)),
                        (6, "abeam", (204.0, 128.0)), (7, "base", (26.0, 224.0)), (8, "final", (150.0, 298.0)), (9, "aim", (264.0, 298.0)), (10, "wind", (300.0, 30.0))):
        tx, ty = AT(pt)
        out.append(c(k, disc[0], disc[1], tx, ty))
    for k, d, (dx, dy) in ((2, d_of("liftoff"), (-26.0, -36.0)), (3, 2300.0, (-34.0, -30.0)), (4, d_of("cross_start", 330.0), (-34.0, -30.0)), (5, d_of("downwind", 2200.0), (0.0, -34.0)),
                           (6, ABEAM_D, (6.0, -34.0)), (7, d_of("base_start", 330.0), (34.0, -26.0)), (8, d_of("final", 560.0), (24.0, -42.0)), (9, LIFT + M["end"], (-32.0, 12.0))):
        x, y = PROF.point(d)
        out.append(c(k, round(x + dx, 1), round(y + dy, 1), round(x, 1), round(y, 1)))
    return "".join(out)


def layers():
    tag_layers, tag_leaders = tags3d()
    return [{"name": "terrain-26-01-thumamah", "at": [W / 2, HT / 2], "width": W}, B.defs(), A1.defs(), *plan3d(), tag_leaders, *tag_layers,
            *side_back(), side_markup(), *side_sprites(), callouts()]


def plate():
    return {
        "id": "fig-26-02-circuit",
        "replaces": "fig-26-02-circuit.svg",
        "book_file": "plate-26-02-circuit.jpg",
        "caption": "Figure 26-2. The circuit in the example aeroplane, with speed and flap setting at each point",
        "desc": "Figure 26-2. The circuit in the example aeroplane, with speed and flap setting at each point. Runway 35 at Thumamah, left-hand; not for navigation.",
        "legend": [
            "Line up on runway 35, checks complete (Chapter 25), flaps up in this example.",
            "Full power; rotate at `VR` 55 kt.",
            "Climb at `VY` 75 kt; after-takeoff checks at a safe height.",
            "Crosswind turn to the left beyond the runway end, no lower than your school's height.",
            "Downwind at the circuit altitude, 2 900 ft AMSL: circuit power, before-landing checks.",
            "Abeam the threshold: power back, descent begins; below `VFE` 90 kt, flaps 10°.",
            "Base, with the threshold about 45° behind: flaps 20°. Look along final first.",
            "Final: flaps 30°, 65 kt, stable by the gate (Figure 26-4).",
            "The aiming point.",
            "Wind from the north.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-26-02-circuit.svg", "blank": True, "layers": layers()},
    }
