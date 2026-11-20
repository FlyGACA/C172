"""Figure 29-1. Leg A to B marked for flight: checkpoints, ticks, time marks and catching features. Drawn again on an aerial view of the country (figs/terrain.py, plain with
scrub only, so that every feature on it is the figure's own); the geometry of the old flat figure is kept exactly (track, checkpoints, ticks, 10-degree lines, time marks, the
features and the twelve callouts), and the features are drawn as they look from above, with the chart's marks over them:

the escarpment beyond B a band of shaded rock with its hachures; the wadis pale channels with scrub along them and the chart's dashed blue line; the road a grey road; the village
small flat-roofed houses with shadows; the power line its pylons and wires, with the substation a fenced yard; the pipeline a cleared strip with the chart's dash-dot line; the three
aerodromes small runways inside the chart's blue ring; the track a dark ribbon with a white casing, its ticks, the checkpoints orange rings and the planned minutes written on the
figure (figs/marks.py). North up; the scale in NM."""
import math

from figs import h_a4 as A
from figs import marks as M
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-29-01", size=(2560, 1840), seed=291, kind="plain", features=("scrub",), veil=0.25, soft=2.6)

n = S.n
W, HT = 640, 460
INK, ORANGE, BLUE = "#1F2937", "#B45309", "#1D4ED8"
TA, TB = (578.0, 360.0), (179.6, 81.0)
CP = [(503.3, 307.7, "12", (537.7, 301.6)), (378.8, 220.5, "25", (394.7, 192.9)), (279.2, 150.8, "36", (259.1, 179.4))]
ROAD = "M 473.8 417.8 C 476.1 406.6 482.8 368.9 487.7 350.5 C 492.6 332.2 498.6 324.7 503.3 307.7 C 508 290.6 509.9 264.9 515.9 248.2 C 522 231.6 535.7 214.5 539.7 207.7"
WADI1 = "M 269.9 256.8 C 272.2 247.9 282.3 221.4 283.8 203.8 C 285.4 186.1 281.3 167.1 279.2 150.8 C 277.1 134.4 270 119.7 271.3 105.9 C 272.5 92 283.9 73.9 286.5 67.5"
WADI2 = "M 279.2 150.8 C 284.7 147.6 302.4 139.9 312.1 131.8 C 321.8 123.6 333.2 106.9 337.4 101.9"
SCARP = [(94.7, 123.3), (123, 87.5), (148.4, 59.2), (168.8, 36.6)]
POWER = ((257.4, 264.7), (485.9, 181.5))
PIPE = ((534.4, 422.3), (111.1, 125.8))


def frame():
    r, k = 9.0, 0.5523 * 9.0
    x0, y0, x1, y1 = 8.0, 8.0, 632.0, 452.0
    m = (f'<rect x="0" y="0" width="{W}" height="{n(y0)}" fill="#ffffff"/><rect x="0" y="{n(y1)}" width="{W}" height="{n(HT - y1)}" fill="#ffffff"/>'
         f'<rect x="0" y="0" width="{n(x0)}" height="{HT}" fill="#ffffff"/><rect x="{n(x1)}" y="0" width="{n(W - x1)}" height="{HT}" fill="#ffffff"/>')
    for d in (f"M{n(x0)} {n(y0)} L{n(x0 + r)} {n(y0)} C{n(x0 + r - k)} {n(y0)} {n(x0)} {n(y0 + r - k)} {n(x0)} {n(y0 + r)} Z",
              f"M{n(x1)} {n(y0)} L{n(x1)} {n(y0 + r)} C{n(x1)} {n(y0 + r - k)} {n(x1 - r + k)} {n(y0)} {n(x1 - r)} {n(y0)} Z",
              f"M{n(x0)} {n(y1)} L{n(x0)} {n(y1 - r)} C{n(x0)} {n(y1 - r + k)} {n(x0 + r - k)} {n(y1)} {n(x0 + r)} {n(y1)} Z",
              f"M{n(x1)} {n(y1)} L{n(x1 - r)} {n(y1)} C{n(x1 - r + k)} {n(y1)} {n(x1)} {n(y1 - r + k)} {n(x1)} {n(y1 - r)} Z"):
        m += f'<path d="{d}" fill="#ffffff"/>'
    return m + f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" rx="{n(r)}" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'


def escarpment():
    """A band of shaded rock beyond the edge, rising to the north-west, with the chart's hachures along the edge."""
    back = [(x - 40 + (6 if i % 2 else -4), y - 36 + (5 if i % 2 else -3)) for i, (x, y) in enumerate(SCARP)]
    poly = SCARP + list(reversed(back))
    out = [f'<defs>{S.gradient("e29g", [(0, "#6E5638", 0.95), (0.35, "#9C8158", 0.8), (1, "#C9AE84", 0.0)], 1, 1, 0, 0)}<filter id="e29b"><feGaussianBlur stdDeviation="2.2"/></filter></defs>',
           f'<polygon points="{S.pts([(x + 4, y + 5) for x, y in SCARP] + [(x + 2, y + 2) for x, y in reversed(back)])}" fill="#2C2216" opacity="0.35" filter="url(#e29b)"/>',
           f'<polygon points="{S.pts(poly)}" fill="url(#e29g)"/>']
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in SCARP)
    out.append(f'<path d="{d}" fill="none" stroke="#3B2E1E" stroke-width="2"/>')
    for i in range(len(SCARP) - 1):
        (x0, y0), (x1, y1) = SCARP[i], SCARP[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        for t in range(0, int(L), 9):
            px, py = x0 + ux * t, y0 + uy * t
            out.append(f'<line x1="{n(px)}" y1="{n(py)}" x2="{n(px - uy * -6 + ux * 0)}" y2="{n(py + ux * -6)}" stroke="#3B2E1E" stroke-width="1.1"/>')
    return "".join(out)


def wadi(d, uid):
    return (f'<path d="{d}" fill="none" stroke="#F3E6C6" stroke-opacity="0.85" stroke-width="11" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="#9AA36A" stroke-opacity="0.45" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 6"/>'
            f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="5 3"/>')


def road():
    return (f'<path d="{ROAD}" fill="none" stroke="#2C2216" stroke-opacity="0.25" stroke-width="7.5"/>'
            f'<path d="{ROAD}" fill="none" stroke="#6B7280" stroke-width="5.2"/><path d="{ROAD}" fill="none" stroke="#F8FAFC" stroke-width="0.9" stroke-dasharray="4 4"/>')


def village():
    out = []
    for i, (x, y, w, h) in enumerate([(503.6, 288.6, 7, 6), (511.6, 286.6, 6, 6), (508.6, 295.6, 6, 7), (515.6, 293.6, 7, 6), (502.6, 298.6, 6, 6), (512.6, 301.6, 6, 6), (519.0, 299.0, 5, 5)]):
        out.append(f'<rect x="{n(x + 1.6)}" y="{n(y + 2)}" width="{w}" height="{h}" fill="#2C2216" opacity="0.35"/>'
                   f'<rect x="{n(x)}" y="{n(y)}" width="{w}" height="{h}" fill="#F1E7D3" stroke="#9C8A6A" stroke-width="0.6"/>')
    return "".join(out)


def power():
    (x0, y0), (x1, y1) = POWER
    out = [f'<line x1="{n(x0 + 2)}" y1="{n(y0 + 3)}" x2="{n(x1 + 2)}" y2="{n(y1 + 3)}" stroke="#2C2216" stroke-opacity="0.25" stroke-width="1.2"/>',
           f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{INK}" stroke-width="1.1"/>']
    for i in range(16):
        t = i / 15
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        out.append(f'<rect x="{n(x - 1.8)}" y="{n(y - 1.8)}" width="3.6" height="3.6" fill="#E2E8F0" stroke="{INK}" stroke-width="0.9" transform="rotate(-20 {n(x)} {n(y)})"/>')
    # the substation: a fenced yard with equipment, on the line
    out.append('<rect x="365.8" y="226.5" width="12" height="11" fill="#2C2216" opacity="0.3"/>'
               '<rect x="364" y="224.5" width="12" height="11" fill="#D9D4C6" stroke="#475569" stroke-width="0.9" stroke-dasharray="1.6 1"/>'
               '<rect x="366.5" y="227" width="3" height="3" fill="#64748B"/><rect x="371" y="227" width="3" height="3" fill="#64748B"/><rect x="368.5" y="231" width="4" height="2.5" fill="#64748B"/>')
    return "".join(out)


def pipeline():
    (x0, y0), (x1, y1) = PIPE
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#EADCBC" stroke-opacity="0.75" stroke-width="7"/>'
            f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="4"/>'
            f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{ORANGE}" stroke-width="2.2" stroke-dasharray="10 3 2 3"/>')


def aerodrome(cx, cy, ang):
    """A small runway seen from above inside the chart's blue ring."""
    return (f'<g transform="rotate({n(ang)} {n(cx)} {n(cy)})"><rect x="{n(cx - 14 + 1.5)}" y="{n(cy - 2.2 + 2)}" width="28" height="4.4" fill="#2C2216" opacity="0.3"/>'
            f'<rect x="{n(cx - 14)}" y="{n(cy - 2.2)}" width="28" height="4.4" rx="0.8" fill="#4B5563" stroke="#E5E7EB" stroke-width="0.6"/>'
            f'<line x1="{n(cx - 10)}" y1="{n(cy)}" x2="{n(cx + 10)}" y2="{n(cy)}" stroke="#FFFFFF" stroke-width="0.6" stroke-dasharray="2 2"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="10" fill="none" stroke="#FFFFFF" stroke-width="4.2" stroke-opacity="0.85"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="10" fill="none" stroke="{BLUE}" stroke-width="2.2"/>')


def track():
    out = []
    for p, q in (((578, 360), (440.2, 295.8)), ((179.6, 81), (303.5, 138.8)), ((578, 360), (470.5, 252.5)), ((179.6, 81), (276.3, 177.7))):
        out.append(A.halo_line(*p, *q, "#334155", 1.3, "4 3", casing=2.6, opacity=0.7))
    out.append(A.ribbon("t29", [TA, TB], width=3.6, colours=("#1B2433", "#475569"), arrow=False, casing=1.8, per=4))
    for (x0, y0), (x1, y1) in [((512.3, 321.3), (519.2, 311.5)), ((450, 277.7), (456.9, 267.9)), ((387.8, 234.1), (394.7, 224.3)), ((325.5, 190.5), (332.4, 180.7)),
                               ((263.3, 147), (270.2, 137.1)), ((201, 103.4), (207.9, 93.5))]:
        out.append(f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>'
                   f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    for x, y, _, _ in CP:
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="7" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-opacity="0.9"/>'
                   f'<circle cx="{n(x)}" cy="{n(y)}" r="7" fill="none" stroke="{ORANGE}" stroke-width="2.8"/>')
    return "".join(out)


def marks():
    out = []
    for x, y, t, (lx, ly) in CP + [(179.6, 81.0, "47", (198.7, 53.6))]:
        out.append(f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(lx)}" y2="{n(ly)}" stroke="#FFFFFF" stroke-width="2.6" stroke-opacity="0.8"/><line x1="{n(x)}" y1="{n(y)}" x2="{n(lx)}" y2="{n(ly)}" stroke="{INK}" stroke-width="1"/>')
        out.append(M.chip(lx + (8 if lx > x else -8), ly - 2, t, INK, size=9.0, kind="clock", anchor="start" if lx > x else "end"))
    # north arrow and scale
    out.append(f'<path d="M600 62 V36" stroke="#FFFFFF" stroke-width="4.4" stroke-linecap="round"/><path d="M600 62 V36" stroke="{INK}" stroke-width="2"/>'
               f'<polygon points="600,24 606.5,38 593.5,38" fill="{INK}" stroke="#FFFFFF" stroke-width="1"/>')
    out.append('<rect x="438" y="415" width="158" height="12" rx="3" fill="#FFFFFF" opacity="0.85"/>'
               f'<rect x="440" y="418" width="76" height="6" fill="{INK}"/><rect x="516" y="418" width="76" height="6" fill="#FFFFFF" stroke="{INK}" stroke-width="1"/>')
    out.append(M.chip(440, 438, "0", INK, size=7.4) + M.chip(516, 438, "10", INK, size=7.4) + M.chip(592, 438, "20 NM", INK, size=7.4))
    return "".join(out)


def layers():
    c = S.callout
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', {"name": "terrain-29-01", "at": [320, 230], "width": 640},
           escarpment() + pipeline() + wadi(WADI1, "a") + wadi(WADI2, "b") + road() + village() + power(),
           aerodrome(*TA, -30) + aerodrome(*TB, -30) + aerodrome(219.9, 429.6, 10),
           track(), marks(), frame()]
    out.append(c(1, 612, 384, 588, 368) + c(2, 519.3, 347.7, 506.3, 314.7) + c(3, 368.8, 260.5, 370, 237) + c(4, 239.2, 142.8, 272.2, 149.8)
               + c(5, 185.6, 121, 180.6, 91) + c(6, 253.9, 435.6, 230.9, 431.6) + c(7, 444, 166, 420, 184) + c(8, 457.5, 238.8, 454.5, 265.8)
               + c(9, 452.7, 333.8, 472.7, 313.8) + c(10, 93, 91.5, 112, 92) + c(11, 399.9, 361.1, 407.9, 339.1) + c(12, 415, 423))
    return out


def plate():
    return {
        "id": "fig-29-01-planned-route",
        "replaces": "fig-29-01-planned-route.svg",
        "book_file": "plate-29-01-planned-route.jpg",
        "caption": "Figure 29-1. Leg A to B marked for flight: checkpoints, ticks, time marks and catching features",
        "desc": "Figure 29-1. Leg A to B marked for flight: checkpoints, ticks, time marks and catching features",
        "legend": [
            "Aerodrome A, elevation 2 000 ft.",
            "Checkpoint 1, 12 NM: the village at the road crossing.",
            "Checkpoint 2, 32 NM, the midpoint: the substation on the power line.",
            "Checkpoint 3, 48 NM: the wadi junction.",
            "Aerodrome B, 64 NM.",
            "Aerodrome C, the alternate.",
            "Planned minutes from takeoff.",
            "A tick every 10 NM.",
            "10° lines out of A and into B.",
            "The escarpment beyond B: reaching it means you have passed B.",
            "The pipeline, 10 NM left of the track.",
            "Scale in NM; north up.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-29-01-planned-route.svg", "blank": True, "layers": layers()},
    }
