"""Figure 26-3. The stabilized-approach gate and the go-around sequence. Two scenes in cards: a runway of the Peninsula seen almost edge-on (markings, edge lights), pale hills, the
approach path with the gate as a pane of glass in a steel frame on it, the heights as dotted lines with their numbers, the model seen from the right at the places of the old figure
(the stable one in green), the high-and-fast path in red, the go-around as a line with a casing and an arrowhead, the flap and speed boxes as small cards; the nine numbered callouts of
the old figure kept (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

A = (8, 4, 624, 218)
B = (8, 230, 624, 214)
GYA, GYB = 200.5, 420.5
W = 80.0
GREEN, AMBER, RED = "#047857", "#B45309", "#B91C1C"

LOWER = [(200, 403, 1, 20), (300, 408, -6, 10), (440, 368, -9, 10), (575, 314, -9, 0)]

GO_AROUND = "M 167.4 69 C 177.4 67.7 205.7 65.7 227.4 61 C 249 56.3 275.1 48.6 297.4 41 C 319.6 33.4 350.3 19.8 360.8 15.6"
APPROACH_LOW = "M 20 326 C 36.7 333.3 98.3 360.7 120 370 C 141.7 379.3 145 380 150 382"
GO_LOW = ("M 120 370 C 133.3 375.3 178.3 395.7 200 402 C 221.7 408.3 233.3 407.2 250 408 C 266.7 408.8 281.7 409.3 300 407 C 318.3 404.7 333.3 401.8 360 394 "
          "C 386.7 386.2 426.7 372.3 460 360 C 493.3 347.7 533.1 330.9 560 320 C 586.9 309.1 611.2 298.9 621.5 294.7")


def world_a():
    objects = H.windsock(560, GYA - 6.5, 24, wind=-1)
    return H.profile("a1a", A, GYA, seed=41, sun=(80, 60), runway_args={"x0": 330, "x1": 632, "threshold": True, "aim": 380, "half": 4.2, "dash_from": 356},
                     clouds=[H.cloud("cloud-cumulus-a", 498, 42, 84), H.cloud("cloud-cumulus-b", 596, 104, 50, 0.85)],
                     palms=[(34, GYA - 6, 0.55), (52, GYA - 4, 0.45)], acacias=[(250, GYA - 5, 0.5)], objects=objects)


def world_b():
    return H.profile("a1b", B, GYB, seed=43, sun=(80, 60), runway_args={"x0": 120, "x1": 632, "threshold": True, "half": 4.2, "dash_from": 150},
                     clouds=[H.cloud("cloud-cumulus-a", 262, 262, 80), H.cloud("cloud-cumulus-b", 120, 262, 54)],
                     palms=[(60, GYB - 6, 0.55), (78, GYB - 4, 0.45)], acacias=[(596, GYB - 5, 0.5)])


def heights():
    """The 300 and 500 ft lines of the old figure, dotted, with their numbers (and the 0 of the ground)."""
    out = [H.line_cased(44, 137, 330, 137, "#4B5870", 1.0, dash="3 4", casing=2.0, opacity=0.9), H.line_cased(44, 95, 330, 95, "#4B5870", 1.0, dash="3 4", casing=2.0, opacity=0.9)]
    for label, y in (("300", 137), ("500", 95), ("0", 200.5)):
        out.append(f'<rect x="{12}" y="{n_(y - 8)}" width="30" height="15" rx="4" fill="#FFFFFF" fill-opacity="0.92"/>'
                   f'<text x="38" y="{n_(y + 4)}" font-family="sans-serif" font-size="11" fill="#1F2937" text-anchor="end">{label}</text>')
    return "".join(out)


def n_(v):
    return S.n(v)


def gate():
    """The gate: a pane of glass in a steel frame standing across the approach path at 500 ft."""
    return ('<defs><linearGradient id="a1gate" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.55"/><stop offset="1" stop-color="#BFD6F2" stop-opacity="0.22"/></linearGradient></defs>'
            '<rect x="158.4" y="59" width="18" height="50" fill="url(#a1gate)"/>'
            '<rect x="158.4" y="59" width="18" height="50" fill="none" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.8"/>'
            '<rect x="158.4" y="59" width="18" height="50" fill="none" stroke="#1F2937" stroke-width="2.2"/>'
            '<line x1="159.5" y1="60.2" x2="161.5" y2="107" stroke="#FFFFFF" stroke-width="0.8" stroke-opacity="0.8"/>')


def paths():
    out = [H.line_cased(56, 40, 380, 200, GREEN, 2.6, casing=2.4),
           H.line_cased(44, 14, 167.4, 69, RED, 2.2, dash="6 4", casing=2.2),
           H.path_line(GO_AROUND, AMBER, 2.4, casing=2.2),
           H.arrow_head(367.4, 13, -22, 9, AMBER),
           H.path_line(APPROACH_LOW, GREEN, 2.2, casing=2.2),
           H.path_line(GO_LOW, AMBER, 2.4, casing=2.2),
           H.arrow_head(628, 292, -22, 9, AMBER)]
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 201.4, 139, 176.4, 106), c(2, 76, 137), c(3, 318, 126, 318, 147), c(4, 110, 18, 100, 39), c(5, 389.4, 19, 365, 15),
                    c(6, 185, 350, 196, 381), c(7, 290, 352, 296, 385), c(8, 426, 304, 434, 345), c(9, 590, 258, 578, 292)])


def layers():
    out = [H.page("a1page", 640, 450), H.defs()]
    out += world_a() + world_b()
    out.append(heights())
    out.append(paths())
    out.append(gate())
    out.append(H.plane_mid(318, 169.4, 2, W, tint="#0E9F6E", tint_strength=0.55))
    out.append(H.flap_mark(H.plane_mid(318, 169.4, 2, W), 30, length=0.085, width=1.8))
    for (tx, ty, ang, fl) in LOWER:
        o = H.plane_mid(tx, ty, ang, W)
        out.append(o)
        if fl:
            out.append(H.flap_mark(o, fl, length=0.085, width=1.8))
    out.append(H.foreground("a1a", A, GYA, seed=41, lights=(330, 632), scrub=10, scale=1.2))
    out.append(H.foreground("a1b", B, GYB, seed=43, lights=(120, 632), scrub=10, scale=1.2))
    out.append(H.speed_card("a1c1", 417, 99, "65", 30, mono=False))
    out.append(H.leader(417, 124, 346, 163.3))
    out.append(H.speed_card("a1c2", 327, 287.5, None, 20))
    out.append(H.leader(345, 313, 312, 382))
    out.append(H.speed_card("a1c3", 453, 247, "VY 75", 10))
    out.append(H.speed_card("a1c4", 565, 339.5, None, 0))
    out.append(H.leader(596, 339.5, 588, 322))
    out.append(callouts())
    return H.flatten(out)


def plate():
    return {
        "id": "fig-26-03-gate-go-around",
        "replaces": "fig-26-03-gate-go-around.svg",
        "book_file": "plate-26-03-gate-go-around.jpg",
        "caption": "Figure 26-3. The stabilized-approach gate and the go-around sequence",
        "desc": "Figure 26-3. The stabilized-approach gate and the go-around sequence",
        "legend": [
            "The gate, at 500 ft above the aerodrome in the FAA's guidance.",
            "The 300 ft line.",
            "Stable: continue to land.",
            "High and fast: not stable at the gate.",
            "Go around.",
            "Full power at once.",
            "Descent stopped, then flaps 20°.",
            "Positive climb at `VY` 75 kt; flaps 10° and then 0°.",
            "Moved to one side, runway in sight.",
        ],
        "canvas": [640, 450],
        "background": "pale",
        "reskin": {"svg": "fig-26-03-gate-go-around.svg", "blank": True, "layers": layers()},
    }
