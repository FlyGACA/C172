"""Figure 21-6 (new). Homing and tracking to an NDB in a crosswind, from Chapter 21 ("NDB and ADF", the box "The homing trap"): keeping the ADF needle on the nose reaches the station,
but the wind drifts the aeroplane downwind on a curve, and it flies further; tracking holds a wind correction instead: to the station at 340 with a wind from the left, heading 330, the
needle 10 degrees right of the nose (330 + 010 = 340, the chapter's own rule).

From above, on an aerial view of the country (figs/terrain.py), in the style of Figure 21-3: the NDB a small hut with its wire antenna between two masts, inside the dotted ring of the
chart symbol; the course to it, 340, a blue ribbon; the homing path, worked out step by step (the nose always on the station, the wind added), a dark ribbon that bows downwind; an
aeroplane on each, and an ADF for each as a lit fixed-card dial (0 at the top, the nose); the wind a green ribbon. The wind and the angles are drawn large, so that the curve shows."""
import math

from figs import h_a4 as H
from figs import marks as M
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-21-06", size=(2560, 1640), seed=216, kind="plain", features=("scrub", "wadis", "tracks"), veil=0.3, soft=2.6)

n = S.n
STN = (226.0, 64.0)                                         # the NDB
A = (339.0, 374.0)                                          # the start: the station bears 340
COURSE = 340.0
WIND_TO = 70.0                                              # a wind from the left of the course, from 250
RATIO = 0.40                                                # wind speed / true airspeed, drawn large (the chapter's 10 degrees would be about 0.17)
AMBER, BLUE, GREEN, INK = "#B45309", "#1D4ED8", "#047857", "#1F2937"


def homing():
    """The homing path: at each step the heading is the bearing to the station, the ground velocity that heading plus the wind."""
    wx, wy = H.unit(WIND_TO)
    p, out = list(A), [A]
    while True:
        dx, dy = STN[0] - p[0], STN[1] - p[1]
        d = math.hypot(dx, dy)
        if d < 26:
            break
        p[0] += (dx / d + RATIO * wx) * 0.5
        p[1] += (dy / d + RATIO * wy) * 0.5
        out.append(tuple(p))
    return out


def bearing(p, q):
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1]))) % 360


def adf(uid, cx, cy, rel):
    """A fixed-card ADF: the card's 0 at the top (the nose), the needle at the relative bearing `rel`, a small aeroplane in the middle."""
    labels = {a: str(a // 10) for a in range(0, 360, 30)}
    out = [H.bezel(uid, cx, cy, 31, 47, labels, bold=(0,), step=10, major=30, size=10.0)]
    out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="31" fill="#0E1729" opacity="0.88"/>')
    tip = H.polar(cx, cy, 29, rel)
    tail = H.polar(cx, cy, -22, rel)
    ux, uy = H.unit(rel)
    px, py = -uy, ux
    head = [tip, (tip[0] - ux * 10 + px * 4.6, tip[1] - uy * 10 + py * 4.6), (tip[0] - ux * 10 - px * 4.6, tip[1] - uy * 10 - py * 4.6)]
    out.append(f'<defs><filter id="{uid}n" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter></defs>'
               f'<line x1="{n(tail[0])}" y1="{n(tail[1])}" x2="{n(tip[0] - ux * 8)}" y2="{n(tip[1] - uy * 8)}" stroke="#FFA43A" stroke-width="5" opacity="0.6" filter="url(#{uid}n)"/>'
               f'<line x1="{n(tail[0])}" y1="{n(tail[1])}" x2="{n(tip[0] - ux * 8)}" y2="{n(tip[1] - uy * 8)}" stroke="#FFB54D" stroke-width="2.6" stroke-linecap="round"/>'
               f'<polygon points="{S.pts(head)}" fill="#FFC56B" stroke="#FFF1CF" stroke-width="0.6"/>')
    # the lubber line and a small aeroplane, nose up
    out.append(f'<path d="M{n(cx)} {n(cy - 47)} l-4 -6 h8 Z" fill="#FFFFFF"/>'
               f'<path d="M{n(cx)} {n(cy - 9)} L{n(cx + 1.6)} {n(cy - 3)} L{n(cx + 9)} {n(cy - 1)} L{n(cx + 9)} {n(cy + 1.6)} L{n(cx + 1.6)} {n(cy + 1.6)} L{n(cx + 1.2)} {n(cy + 6.5)} '
               f'L{n(cx + 4)} {n(cy + 8)} L{n(cx - 4)} {n(cy + 8)} L{n(cx - 1.2)} {n(cy + 6.5)} L{n(cx - 1.6)} {n(cy + 1.6)} L{n(cx - 9)} {n(cy + 1.6)} L{n(cx - 9)} {n(cy - 1)} '
               f'L{n(cx - 1.6)} {n(cy - 3)} Z" fill="#E2E8F0" stroke="#0E1729" stroke-width="0.6"/>')
    out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="2.6" fill="#FFC56B" stroke="#0E1729" stroke-width="0.6"/>')
    return "".join(out)


def ndb(uid, cx, cy):
    """The NDB from above: the dotted ring of the chart symbol, a wire antenna between two masts, a small hut, their shadows."""
    out = [f'<defs><filter id="{uid}b" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="1.6"/></filter></defs>']
    for r, dot in ((30, 1.5), (23, 1.3)):
        for k in range(0, 360, 12 if r == 30 else 15):
            x, y = H.polar(cx, cy, r, k)
            out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{dot + 0.9}" fill="#FFFFFF" opacity="0.8"/><circle cx="{n(x)}" cy="{n(y)}" r="{dot}" fill="#7C2D12"/>')
    m1, m2 = (cx - 15, cy - 6), (cx + 15, cy + 6)
    out.append(f'<line x1="{n(m1[0] + 3)}" y1="{n(m1[1] + 4)}" x2="{n(m2[0] + 3)}" y2="{n(m2[1] + 4)}" stroke="#2C2216" stroke-opacity="0.35" stroke-width="1.6" filter="url(#{uid}b)"/>'
               f'<line x1="{n(m1[0])}" y1="{n(m1[1])}" x2="{n(m2[0])}" y2="{n(m2[1])}" stroke="#1F2937" stroke-width="1.1"/>')
    for mx, my in (m1, m2):
        out.append(f'<circle cx="{n(mx + 2.5)}" cy="{n(my + 3.5)}" r="2.6" fill="#2C2216" opacity="0.35" filter="url(#{uid}b)"/>'
                   f'<circle cx="{n(mx)}" cy="{n(my)}" r="2.4" fill="#F8FAFC" stroke="#475569" stroke-width="0.8"/>')
    out.append(f'<rect x="{n(cx - 4 + 2.5)}" y="{n(cy - 3.5 + 3.5)}" width="8" height="7" fill="#2C2216" opacity="0.35" filter="url(#{uid}b)"/>'
               f'<rect x="{n(cx - 4)}" y="{n(cy - 3.5)}" width="8" height="7" rx="0.8" fill="#F1F5F9" stroke="#64748B" stroke-width="0.8"/>')
    return "".join(out)


def plate():
    path = homing()
    T = (A[0] + (STN[0] - A[0]) * 0.3, A[1] + (STN[1] - A[1]) * 0.3)             # the tracking aeroplane
    ux, uy = H.unit(COURSE)
    Hm = max(path, key=lambda p: (p[1] - A[1]) * ux - (p[0] - A[0]) * uy)        # the homing aeroplane, where the wind has carried it furthest from the course
    crab = math.degrees(math.asin(RATIO))                                        # the drawn wind correction
    layers = [{"name": "terrain-21-06", "at": [320, 205], "width": 640}]
    # dotted threads from the aeroplanes to their dials
    layers.append(H.dotted([(Hm[0] + 24, Hm[1]), (513, 128)]) + H.dotted([(T[0] + 24, T[1] + 4), (513, 300)]))
    # the homing path (dark, bowing downwind) and the course (blue)
    layers.append(H.ribbon("n6h", path[::6] + [path[-1]], width=3.8, colours=("#1B2433", "#586377"), head=1.6, casing=1.8, per=4))
    s0 = H.polar(A[0], A[1], 4, COURSE)
    layers.append(H.ribbon("n6c", [s0, H.polar(STN[0], STN[1], 30, COURSE + 180)], width=5.6, colours=H.BLUE, head=2.0))
    # the wind
    layers.append(H.ribbon("n6w", [(54, 238), (102, 220)], width=5.0, colours=H.GREEN, head=2.2, casing=1.8))
    # the tracking aeroplane's heading ahead of it, and the angle to the course
    hx, hy = H.polar(T[0], T[1], 74, COURSE - crab)
    layers.append(H.halo_line(T[0], T[1], hx, hy, INK, 1.4, "4 3"))
    a0, a1 = H.polar(T[0], T[1], 52, COURSE - crab), H.polar(T[0], T[1], 52, COURSE)
    layers.append(H.halo_path(f"M{n(a0[0])},{n(a0[1])} A52,52 0 0,1 {n(a1[0])},{n(a1[1])}", AMBER, 2.0))
    layers.append(ndb("n6s", *STN))
    layers.append(H.plane(*Hm, 52, bearing(Hm, STN)))
    layers.append(H.plane(*T, 52, COURSE - crab))
    # the dials: homing above, tracking below
    layers.append(adf("n6a", 562, 128, 0.0))
    layers.append(adf("n6b", 562, 300, crab))
    # the labels written on the figure
    mid = H.polar(STN[0], STN[1], 130, COURSE + 180)
    layers.append(M.chip(mid[0] - 26, mid[1], "340", BLUE, size=9.0)
                  + M.chip(hx - 22, hy - 4, "330", INK, size=9.0)
                  + M.chip((a0[0] + a1[0]) / 2 - 4, (a0[1] + a1[1]) / 2 - 11, "10°", AMBER, size=9.0)
                  + M.chip(562, 196, "0", "#B45309", size=8.6) + M.chip(562, 368, "010", "#B45309", size=8.6))
    c = S.callout
    layers.append("".join([
        c(1, STN[0] - 52, STN[1] + 6, STN[0] - 30, STN[1] + 2),
        c(2, Hm[0] + 50, Hm[1] + 62, Hm[0] + 14, Hm[1] + 42),
        c(3, 624, 92, 606, 102),
        c(4, T[0] - 60, T[1] + 44, T[0] + 11, T[1] + 41),
        c(5, 624, 264, 606, 274),
        c(6, 40, 262, 58, 240),
    ]))
    return {
        "id": "fig-21-06-ndb-homing",
        "replaces": "fig-21-06-ndb-homing.svg",                 # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-21-06-ndb-homing.jpg",
        "caption": "Figure 21-6. Homing and tracking to an NDB in a crosswind",
        "desc": ("Figure 21-6. From above: an NDB, the course to it on 340 and a wind from the left. Homing, the aeroplane keeps the ADF needle on the nose and drifts downwind on a "
                 "curve; tracking, it heads 330 into the wind and the needle shows 010, 10 degrees right of the nose. The wind and the angles are drawn large."),
        "legend": [
            "The NDB: the ADF needle points at it.",
            "Homing: the needle kept on the nose; the wind drifts the aeroplane downwind on a curve, and it flies further.",
            "Homing: the needle on 0, the nose on the station.",
            "Tracking: the course to the station, 340, held by heading 330 into the wind.",
            "Tracking: the needle 10° right of the nose (relative bearing 010); 330 + 010 = 340.",
            "Wind from the left.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers},
    }
