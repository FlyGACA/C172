"""Figure 5-7 (new). Ground effect, seen from in front: the wing (drawn as a bar of span B) at three heights above the surface, B, B/4 and B/10, to one scale (the span is 100 canvas units).

At one span the air flows freely round the wing: the wingtip vortices (rings at the tips) are large and the downwash (arrows below the wing) runs on to the ground. At a quarter of the span the surface restricts the vertical movement of the air:
the vortices shrink, the downwash is stopped and turned outward by the ground, and induced drag falls by roughly a quarter. At a tenth of the span the vortices are smaller still and induced drag falls by roughly half. The figures
are those of Chapter 5 (FAA-H-8083-25C ch. 5 and FAA-H-8083-3C ch. 6, as the chapter cites them); the sizes of the rings and the lengths of the arrows are drawn to show the idea, they are not measured. Digits, B and %."""
import math

from figs import h_b1 as B
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 214
U = "ge5"
GY = 172.0                                              # the ground
SPAN = 100.0                                            # B, in canvas units
CX = (118.0, 320.0, 522.0)
HEIGHTS = (1.0, 0.25, 0.10)                             # in spans
DRAG = ("100 %", "75 %", "50 %")                        # induced drag against the wing out of ground effect
BLUE, GREEN, AMBER, SLATE, RED = "#1D4ED8", "#15803D", "#B45309", "#475569", "#B91C1C"


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.2, height=12.0):
    w = gwidth(s, size) + 12.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.35))


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter>'
            f'<linearGradient id="{U}wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4F7FB"/><stop offset="1" stop-color="#AEB9C8"/></linearGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{GY - 8 + 22}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def ground():
    return B.soil(U + "so", [(8.0, GY), (W - 8.0, GY)], GY + 28.0, seed=57, strata=(0.4, 0.7), grit=8, haze=(4.0, 0.6))


def arrow(x0, y0, x1, y1, col, width=2.4, head=6.0):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * head * 0.62)} {n(hy + ny * head * 0.62)} L{n(hx - nx * head * 0.62)} {n(hy - ny * head * 0.62)} Z" fill="{col}"/>')


def vortex(x, y, r, col):
    """A wingtip vortex: a ring with a turning arrow."""
    a0, a1 = -40, 250
    p1 = (x + r * math.sin(math.radians(a1)), y - r * math.cos(math.radians(a1)))
    p0 = (x + r * math.sin(math.radians(a0)), y - r * math.cos(math.radians(a0)))
    path = f"M{n(p0[0])} {n(p0[1])} A{n(r)} {n(r)} 0 1 1 {n(p1[0])} {n(p1[1])}"
    t = (math.cos(math.radians(a1)), math.sin(math.radians(a1)))
    nn = (-t[1], t[0])
    tip = (p1[0] + t[0] * 2.5, p1[1] + t[1] * 2.5)
    hd = f"{n(tip[0] + t[0] * 5)},{n(tip[1] + t[1] * 5)} {n(tip[0] + nn[0] * 3.4)},{n(tip[1] + nn[1] * 3.4)} {n(tip[0] - nn[0] * 3.4)},{n(tip[1] - nn[1] * 3.4)}"
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{col}" fill-opacity="0.10"/>'
            f'<path d="{path}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/><polygon points="{hd}" fill="{col}"/>')


def panel(i):
    cx = CX[i]
    h = HEIGHTS[i] * SPAN
    wy = GY - h                                           # the wing's lower surface
    out = []
    left, right = cx - SPAN / 2, cx + SPAN / 2
    # the wing: a bar of span B with rounded tips
    out.append(f'<rect x="{n(left)}" y="{n(wy - 7)}" width="{n(SPAN)}" height="7" rx="3.5" fill="url(#{U}wg)" stroke="#475569" stroke-width="1" filter="url(#{U}ds)"/>')
    # the lift, above the wing: the same in the three
    for k in (-0.62, -0.2, 0.2, 0.62):
        out.append(arrow(cx + k * SPAN / 2, wy - 10, cx + k * SPAN / 2, wy - 30, BLUE, 2.6, 6.4))
    # the vortices at the tips (smaller as the ground comes up)
    r = (15.0, 10.0, 5.6)[i]
    for sgn in (-1, 1):
        out.append(vortex(cx + sgn * (SPAN / 2 + r + 3), wy + 2 + (0.0 if i else 4.0), r, AMBER))
    # the downwash below the wing: it runs on to the ground (B), or is stopped and turned outward by it
    xs = (-0.5, -0.17, 0.17, 0.5)
    if i == 0:
        for k in xs:
            out.append(arrow(cx + k * SPAN / 2, wy + 4, cx + k * SPAN / 2, wy + 62, GREEN, 2.6, 6.4))
    else:
        for k in xs:
            out.append(arrow(cx + k * SPAN / 2, wy + 3, cx + k * SPAN / 2, GY - 2, GREEN, 2.2, 5.0 if i == 1 else 3.6))
        for sgn in (-1, 1):
            out.append(arrow(cx + sgn * 8, GY - 4, cx + sgn * (SPAN / 2 + 4), GY - 4, GREEN, 2.0, 4.6))
    # the height, to the left of the wing
    x = left - 46
    out.append(f'<line x1="{n(x)}" y1="{n(wy)}" x2="{n(x)}" y2="{n(GY)}" stroke="{SLATE}" stroke-width="1.5"/>'
               f'<line x1="{n(x - 4)}" y1="{n(wy)}" x2="{n(x + 4)}" y2="{n(wy)}" stroke="{SLATE}" stroke-width="1.5"/><line x1="{n(x - 4)}" y1="{n(GY)}" x2="{n(x + 4)}" y2="{n(GY)}" stroke="{SLATE}" stroke-width="1.5"/>')
    label = ("1 B", "0.25 B", "0.1 B")[i]
    out.append(pill(label, x, (wy + GY) / 2 if i == 0 else wy - 16, SLATE))
    # induced drag, at the top
    out.append(pill(DRAG[i], cx, 26.0, GREEN if i else SLATE, 7.0, 13.0))
    return "".join(out)


def span_marks():
    """The span B, once, under the first wing."""
    cx = CX[0]
    y = GY + 14
    return (f'<line x1="{n(cx - SPAN / 2)}" y1="{n(y)}" x2="{n(cx + SPAN / 2)}" y2="{n(y)}" stroke="#FFFFFF" stroke-width="1.6"/>'
            f'<line x1="{n(cx - SPAN / 2)}" y1="{n(y - 3)}" x2="{n(cx - SPAN / 2)}" y2="{n(y + 3)}" stroke="#FFFFFF" stroke-width="1.6"/><line x1="{n(cx + SPAN / 2)}" y1="{n(y - 3)}" x2="{n(cx + SPAN / 2)}" y2="{n(y + 3)}" stroke="#FFFFFF" stroke-width="1.6"/>'
            + H.glyph_text("B", cx, y - 0.2, 6.4, "#FFFFFF", spacing=0.3))


def callouts():
    c = S.callout
    out = []
    for i, cx in enumerate(CX):
        h = HEIGHTS[i] * SPAN
        out.append(c(i + 1, cx + (96 if i == 0 else 84), GY - h - 30, cx + SPAN / 2 - 10, GY - h - 4, r=9.5))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), ground(), span_marks(), *[panel(i) for i in range(3)], callouts()]


def plate():
    return {
        "id": "fig-05-07-ground-effect",
        "replaces": "fig-05-07-ground-effect.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-05-07-ground-effect.jpg",
        "caption": "Figure 5-7. Ground effect: the wing at one span, a quarter of a span and a tenth of a span above the surface",
        "desc": ("Figure 5-7. Ground effect: the wing at one span, a quarter of a span and a tenth of a span above the surface, seen from in front, to one scale. The wingtip vortices shrink, "
                 "the downwash is stopped and turned outward by the ground, and induced drag falls by roughly a quarter and then by roughly half."),
        "legend": [
            "One span above the surface (B): out of ground effect. The air moves freely round the wing: large wingtip vortices (amber) and a downwash (green) that runs on toward the ground. Induced drag is 100 % of its free-air value.",
            "A quarter of a span above the surface: the ground restricts the vertical movement of the air. The vortices shrink and the downwash is stopped and turned outward by the surface. Induced drag falls by roughly a quarter.",
            "A tenth of a span above the surface: the vortices are smaller still and the downwash is almost wholly turned aside. Induced drag falls by roughly half, so the wing gives the same lift at a lower angle of attack. The sizes of the rings and arrows show the idea; they are not measured.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
