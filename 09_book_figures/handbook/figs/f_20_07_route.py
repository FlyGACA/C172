"""Figure 20-7. The example route from A to B, with the alternate C. Drawn again on an aerial view of the country (figs/terrain.py, plain with scrub only, so that every
feature on it is the figure's own; the pieces are in figs/mapkit.py). The geometry of the old flat figure is kept exactly (the three legs, the alternate, the diversion, the ticks every
10 NM, the 10-degree lines, the restricted area and the twelve callouts), and the checkpoints are drawn as they look from above: the town, the road crossing, the wadi junction at WADI,
the corner of the dune field at DUNE and the salt flat at X. Courses and distances are written on the figure (figs/marks.py)."""
from figs import mapkit as K
from figs import marks as M
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-20-07", size=(2560, 1640), seed=207, kind="plain", features=("scrub",), veil=0.25, soft=2.6)

n = S.n
W, HT = 640, 410
A, WADI, DUNE, B, C, X = (600.0, 202.0), (331.9, 47.2), (165.0, 91.9), (47.3, 260.0), (75.8, 378.4), (113.3, 165.6)
GREEN = "#047857"
RESTRICTED = [(258.0, 173.2), (330.0, 151.6), (340.8, 238.0), (250.8, 245.2)]


def ground():
    out = [K.dunes([(165, 91.9), (178, 40), (128, 16), (40, 16), (24, 64), (104, 84)], seed=7, uid="d207")]
    out.append(K.salt_flat(X[0], X[1], 18, 10, "s207"))
    out.append(K.wadi("M 296 12 Q 318 32 331.9 47.2 Q 346 66 356 104 Q 362 128 378 146") + K.wadi("M 392 14 Q 360 30 331.9 47.2"))
    out.append(K.road("M 446 12 C 438 50 430 84 425.4 101.2 S 410 160 392 214 S 372 300 362 400"))
    out.append(K.town(487.8, 137.2, seed=3, count=16, spread=11))
    out.append(K.restricted(RESTRICTED))
    return "".join(out)


def route():
    out = []
    for p in ((464.7, 152.7), (489.7, 109.4)):
        out.append(f'<line x1="{n(A[0])}" y1="{n(A[1])}" x2="{n(p[0])}" y2="{n(p[1])}" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.75"/>'
                   f'<line x1="{n(A[0])}" y1="{n(A[1])}" x2="{n(p[0])}" y2="{n(p[1])}" stroke="#334155" stroke-width="1.3" stroke-dasharray="5 3"/>')
    out.append(K.leg([A, WADI], "l1") + K.leg([WADI, DUNE], "l2") + K.leg([DUNE, B], "l3"))
    out.append(K.ticks(A, WADI, 36.0, start=36.0) + K.ticks(WADI, DUNE, 36.0, start=36.0) + K.ticks(DUNE, B, 36.0, start=36.0))
    # the alternate (blue, dashed) and the diversion from X (green, dashed, with its head)
    out.append(f'<line x1="{n(B[0])}" y1="{n(B[1])}" x2="{n(C[0])}" y2="{n(C[1])}" stroke="#FFFFFF" stroke-width="5" stroke-opacity="0.75"/>'
               f'<line x1="{n(B[0])}" y1="{n(B[1])}" x2="{n(C[0])}" y2="{n(C[1])}" stroke="{K.BLUE}" stroke-width="2.4" stroke-dasharray="8 4"/>')
    out.append(M.arrow(X[0], X[1], 77.6, 368.5, GREEN, width=2.6, dash="9 5"))
    # the turning points (triangles), the top of climb, the checkpoints, the aerodromes
    for x, y in (WADI, DUNE):
        out.append(f'<polygon points="{n(x)},{n(y - 9)} {n(x + 8)},{n(y + 5)} {n(x - 8)},{n(y + 5)}" fill="{K.INK}" stroke="#FFFFFF" stroke-width="1.6"/>')
    out.append(f'<circle cx="562.6" cy="180.4" r="4.8" fill="#FFFFFF" stroke="{K.INK}" stroke-width="2.2"/>')
    out.append(K.ring(487.8, 137.2) + K.ring(425.4, 101.2) + K.ring(*X))
    out.append(K.aerodrome(*A, 60) + K.aerodrome(*B, -60) + K.aerodrome(*C, 0))
    return "".join(out)


def labels():
    INK = K.INK
    out = [M.chip(448, 84, "300°", INK, size=9.0), M.chip(448, 100, "86 NM", INK, size=8.4),
           M.chip(236, 92, "255°", INK, size=9.0), M.chip(282, 84, "48 NM", INK, size=8.4),
           M.chip(66, 172, "215°", INK, size=9.0), M.chip(66, 188, "57 NM", INK, size=8.4),
           M.chip(36, 314, "166°", K.BLUE, size=9.0), M.chip(36, 330, "34 NM", K.BLUE, size=8.4),
           M.chip(122, 296, "190°", GREEN, size=9.0), M.chip(122, 312, "60 NM", GREEN, size=8.4)]
    out.append(K.north(605, 330, 380) + K.scale(400, 368, 36, 5))
    for i, v in enumerate(("0", "10", "20", "30", "40", "50 NM")):
        out.append(M.chip(400 + 36 * i, 388, v, INK, size=7.2))
    return "".join(out)


def layers():
    c = S.callout
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', {"name": "terrain-20-07", "at": [320, 205], "width": 640},
           ground(), route(), labels(), K.frame(W, HT, (10.0, 10.0, 630.0, 400.0))]
    out.append(c(1, 604, 240, 602, 212) + c(2, 568.6, 216.4, 563.6, 185) + c(3, 493.8, 183.2, 488.8, 144) + c(4, 441.4, 57.2, 427.4, 95.5)
               + c(5, 361.9, 33.2, 338, 43) + c(6, 157, 59.9, 164, 82) + c(7, 73.3, 151.6, 106.5, 164.6) + c(8, 26, 286, 40.5, 266)
               + c(9, 44, 386, 66.8, 380.4) + c(10, 315.8, 281.6, 295.8, 242.6) + c(11, 535.3, 106.6, 518.3, 130.6) + c(12, 148.1, 233.5, 104, 231))
    return out


def plate():
    return {
        "id": "fig-20-07-route",
        "replaces": "fig-20-07-route.svg",
        "book_file": "plate-20-07-route.jpg",
        "caption": "Figure 20-7. The example route from A to B, with the alternate C",
        "desc": "Figure 20-7. The example route from A to B, with the alternate C",
        "legend": [
            "Aerodrome A, departure, elevation 2 000 ft.",
            "Top of climb, 12 NM from A.",
            "Checkpoint: the town, 36 NM from A.",
            "Checkpoint: the road crossing, 56 NM from A.",
            "Point WADI, a wadi junction: turning point.",
            "Point DUNE, the corner of a dune field: turning point.",
            "Checkpoint X, a salt flat 25 NM after DUNE.",
            "Aerodrome B, destination.",
            "Aerodrome C, alternate.",
            "Restricted area.",
            "10° lines either side of leg 1.",
            "Diversion from X to C, 190°, 60 NM (see Diversion).",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-20-07-route.svg", "blank": True, "layers": layers()},
    }
