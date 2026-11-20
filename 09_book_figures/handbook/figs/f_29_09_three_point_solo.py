"""Figure 29-9. A three-point solo cross-country that meets Appendix A §V(a)(1). Drawn again on an aerial view of the country (figs/terrain.py, plain with scrub; the pieces
are in figs/mapkit.py); the geometry of the old flat figure is kept exactly (the three aerodromes, the three legs with their courses and distances, the circles of 25 and 50 NM about A,
the scale 3.7 units a nautical mile, and the nine callouts). The three aerodromes are small runways inside a green ring (a full-stop landing at each); A to B, the segment of more
than 50 NM, is the blue ribbon; the totals are written on the figure (figs/marks.py)."""
import math

from figs import mapkit as K
from figs import marks as M
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-29-09", size=(2560, 1680), seed=299, kind="plain", features=("scrub",), veil=0.25, soft=2.6)

n = S.n
W, HT = 640, 420
A, B, C = (438.0, 222.0), (244.0, 86.2), (263.7, 255.9)
GREEN = "#047857"


def circle(r, uid):
    return (f'<circle cx="{n(A[0])}" cy="{n(A[1])}" r="{n(r)}" fill="none" stroke="#10233F" stroke-opacity="0.35" stroke-width="3"/>'
            f'<circle cx="{n(A[0])}" cy="{n(A[1])}" r="{n(r)}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-dasharray="7 5"/>')


def head(p, q, col, s=10.0):
    """An arrowhead half way along p-q."""
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
    tip = (mx + ux * s * 0.6, my + uy * s * 0.6)
    a = (tip[0] - ux * s - uy * s * 0.55, tip[1] - uy * s + ux * s * 0.55)
    b = (tip[0] - ux * s + uy * s * 0.55, tip[1] - uy * s - ux * s * 0.55)
    return f'<polygon points="{S.pts([tip, a, b])}" fill="{col}" stroke="#FFFFFF" stroke-width="1.2"/>'


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', {"name": "terrain-29-09", "at": [320, 210], "width": 640}]
    out.append(circle(92.5, "c25") + circle(185.0, "c50"))
    out.append(K.leg([(428.2, 215.1), (253.9, 93.1)], "ab", colours=("#1B4FD0", "#6FA3F5"), width=4.6)
               + K.leg([(245.4, 98.1), (262.3, 244.0)], "bc") + K.leg([(275.4, 253.6), (426.2, 224.3)], "ca"))
    out.append(head(A, B, "#1D4ED8") + head(B, C, K.INK) + head(C, A, K.INK))
    for p, ang in ((A, 30), (B, 30), (C, -10)):
        out.append(K.aerodrome(*p, ang, ring="#1F2937", r=9) + f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="15" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-opacity="0.85"/>'
                   f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="15" fill="none" stroke="{GREEN}" stroke-width="2.6"/>')
    out.append(M.chip(360, 128, "305°", "#1D4ED8", size=9.0) + M.chip(360, 144, "64 NM", "#1D4ED8", size=8.4)
               + M.chip(220, 150, "173°", K.INK, size=9.0) + M.chip(220, 166, "46 NM", K.INK, size=8.4)
               + M.chip(320, 264, "079°", K.INK, size=9.0) + M.chip(320, 280, "48 NM", K.INK, size=8.4))
    out.append(M.chip(A[0], A[1] - 92.5, "25 NM", K.INK, size=7.8) + M.chip(A[0], A[1] - 185 + 12, "50 NM", K.INK, size=7.8))
    out.append(M.chip(150, 384, "64 + 46 + 48 = 158", K.INK, size=9.4))
    out.append(K.north(604, 22, 58) + K.scale(40, 30, 37, 3))
    for i, v in enumerate(("0", "10", "20", "30 NM")):
        out.append(M.chip(40 + 37 * i, 48, v, K.INK, size=7.2))
    out.append(K.frame(W, HT))
    c = S.callout
    out.append(c(1, 472, 240, 453, 228) + c(2, 214, 64.2, 232, 77.2) + c(3, 229.7, 271.9, 249.7, 261.9) + c(4, 312.8, 171.1, 315.8, 142.1)
               + c(5, 225.6, 198.3, 252.6, 196.3) + c(6, 376.6, 268.7, 372.6, 239.7) + c(7, 526.9, 297.5, 511.9, 284.5) + c(8, 582.2, 332.5, 595.2, 317.5)
               + c(9, 56, 384))
    return out


def plate():
    return {
        "id": "fig-29-09-three-point-solo",
        "replaces": "fig-29-09-three-point-solo.svg",
        "book_file": "plate-29-09-three-point-solo.jpg",
        "caption": "Figure 29-9. A three-point solo cross-country that meets Appendix A §V(a)(1)",
        "desc": "Figure 29-9. A three-point solo cross-country that meets Appendix A §V(a)(1)",
        "legend": [
            "Aerodrome A: departure and final full-stop landing.",
            "Aerodrome B: full-stop landing.",
            "Aerodrome C: full-stop landing.",
            "A to B: the segment of more than 50 NM.",
            "B to C.",
            "C to A.",
            "25 NM from A: the solo cross-country threshold.",
            "50 NM from A: B lies beyond it.",
            "Total distance, NM.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-29-09-three-point-solo.svg", "blank": True, "layers": layers()},
    }
