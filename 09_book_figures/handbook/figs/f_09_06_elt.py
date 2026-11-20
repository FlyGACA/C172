"""Figure 9-6 (new). The emergency locator transmitter, a schematic on the side view of the training aeroplane (sprite-side).

A hard impact (red burst at the nose) trips the crash sensor of the ELT in the aft fuselage (the standards in Appendix C to Part 91: attached as far aft as practicable for automatic types); the ELT then transmits on 406 MHz (blue arcs) and
121.500 MHz (amber arcs) at the same time, and search and rescue (a mast with a receiver on the right) can find the aeroplane. The ELT switch in the cockpit is shown with its ARM position, as the chapter says to know where the switch is and that
it is armed. A schematic: the position of the unit is not that of any particular aeroplane. Digits, MHZ, ARM and the numbers of the callouts."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 270
U = "el9"
SIDE = (6.0, 60.0, 430.0)                                   # left, top, width of the side sprite's box (1536 x 640)
BLUE, AMBER, RED, SLATE, GREEN = "#1D4ED8", "#B45309", "#B91C1C", "#475569", "#15803D"


def sx(u, v):
    return SIDE[0] + u / 10.0 * SIDE[2], SIDE[1] + v / 10.0 * SIDE[2] * 640 / 1536


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.2, height=12.0):
    return M.chip(x, y, s, colour, size=size * 1.05, anchor="middle", light=True, height=height)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def burst(x, y, r, col):
    pts_ = []
    for k in range(16):
        a = math.radians(k * 22.5)
        rr = r if k % 2 == 0 else r * 0.45
        pts_.append((x + rr * math.sin(a), y - rr * math.cos(a)))
    return f'<polygon points="{" ".join(f"{n(a)},{n(b)}" for a, b in pts_)}" fill="{col}" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round" filter="url(#{U}ds)"/>'


def arcs(x, y, col, radii, spread=52.0, width=3.0):
    """Radiating arcs from a point, opening to the right and up."""
    out = []
    for r in radii:
        a0, a1 = math.radians(-90 - spread * 0.2), math.radians(-90 + spread * 1.5)
        p0 = (x + r * math.cos(a0 + math.radians(40)), y + r * math.sin(a0 + math.radians(40)))
        p1 = (x + r * math.cos(a1 + math.radians(-5)), y + r * math.sin(a1 + math.radians(-5)))
        out.append(f'<path d="M{n(p0[0])} {n(p0[1])} A{n(r)} {n(r)} 0 0 1 {n(p1[0])} {n(p1[1])}" fill="none" stroke="#FFFFFF" stroke-width="{n(width + 2.6)}" stroke-linecap="round" opacity="0.85"/>'
                   f'<path d="M{n(p0[0])} {n(p0[1])} A{n(r)} {n(r)} 0 0 1 {n(p1[0])} {n(p1[1])}" fill="none" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>')
    return "".join(out)


def elt_unit():
    x, y = sx(1.55, 3.95)
    return (f'<rect x="{n(x - 13)}" y="{n(y - 8)}" width="26" height="16" rx="3" fill="#F59E0B" stroke="{SLATE}" stroke-width="1.6" filter="url(#{U}ds)"/>'
            f'<line x1="{n(x + 4)}" y1="{n(y - 8)}" x2="{n(x + 4)}" y2="{n(y - 17)}" stroke="{SLATE}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<circle cx="{n(x - 6)}" cy="{n(y)}" r="2.6" fill="{RED}"/>')


def bez(p0, c, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1])


ARCH = {"blue": ((106.0, 104.0), (330.0, -52.0), (548.0, 128.0)), "amber": ((126.0, 100.0), (340.0, 4.0), (556.0, 140.0))}


def signals():
    x, y = sx(1.55, 3.95)
    out = [arcs(x + 4, y - 18, BLUE, (16, 26), 52.0, 3.0), arcs(x + 4, y - 18, AMBER, (36, 46), 52.0, 3.0)]
    for key, col in (("blue", BLUE), ("amber", AMBER)):
        p0, c, p2 = ARCH[key]
        d = f"M{n(p0[0])} {n(p0[1])} Q{n(c[0])} {n(c[1])} {n(p2[0])} {n(p2[1])}"
        out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="5.6" stroke-linecap="round" opacity="0.85"/><path d="{d}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-dasharray="7 5"/>')
        ex, ey = p2
        out.append(f'<path d="M{n(ex)} {n(ey)} L{n(ex - 9)} {n(ey - 8)} L{n(ex - 3)} {n(ey - 11)} Z" fill="{col}"/>')
    return "".join(out)


def rescue():
    """Search and rescue: a mast with a receiver dish, at the right."""
    x, y = 566.0, 200.0
    return (f'<line x1="{n(x - 40)}" y1="{n(y + 22)}" x2="{n(x + 40)}" y2="{n(y + 22)}" stroke="{SLATE}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M{n(x - 7)} {n(y + 22)} L{n(x)} {n(y - 46)} L{n(x + 7)} {n(y + 22)} Z" fill="#94A3B8" stroke="{SLATE}" stroke-width="1.6" stroke-linejoin="round" filter="url(#{U}ds)"/>'
            f'<path d="M{n(x - 24)} {n(y - 54)} Q{n(x)} {n(y - 28)} {n(x + 24)} {n(y - 54)} Z" fill="#E2E8F0" stroke="{SLATE}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<circle cx="{n(x)}" cy="{n(y - 42)}" r="3.4" fill="{GREEN}"/>')


def impact():
    x, y = sx(9.9, 5.0)
    return burst(x + 4, y + 2, 17, RED)


def switch():
    """The ELT switch in the cockpit, on the panel: a small box with the ARM rocker and its label."""
    x, y = sx(7.15, 3.7)
    return (f'<rect x="{n(x - 20)}" y="{n(y - 10)}" width="40" height="20" rx="4" fill="#F4F1E8" stroke="{SLATE}" stroke-width="1.5" filter="url(#{U}ds)"/>'
            f'<rect x="{n(x - 14)}" y="{n(y - 6)}" width="8" height="12" rx="2" fill="{GREEN}"/>'
            + H.glyph_text("ARM", x + 8.0, y, 5.0, SLATE, spacing=0.3))


def pills():
    bx, by = bez(*ARCH["blue"], 0.3)
    ax, ay = bez(*ARCH["amber"], 0.52)
    return pill("406 MHZ", bx, by, BLUE, 6.4, 13.0) + pill("121.5 MHZ", ax, ay, AMBER, 6.4, 13.0)


def callouts():
    c = S.callout
    r = 9.5
    out = []
    ex, ey = sx(1.55, 3.95)
    ix, iy = sx(9.9, 5.0)
    sw = sx(7.15, 3.7)
    out.append(c(1, ex - 4, ey + 56, ex, ey + 9, r=r))                  # the ELT in the aft fuselage
    out.append(c(2, ix - 14, iy + 56, ix + 2, iy + 14, r=r))            # the impact, the crash sensor switches it on
    bx, by = bez(*ARCH["blue"], 0.3)
    ax, ay = bez(*ARCH["amber"], 0.52)
    out.append(c(3, bx - 44, by - 22, bx - 24, by - 5, r=r))           # 406 MHz
    out.append(c(4, ax + 46, ay + 30, ax + 24, ay + 6, r=r))           # 121.5 MHz
    out.append(c(5, 566.0 + 40, 196.0, 566.0 + 8, 190.0, r=r))        # search and rescue
    out.append(c(6, sw[0] - 10, sw[1] - 46, sw[0] - 4, sw[1] - 11, r=r))     # the switch
    return "".join(out)


def sprites():
    return [A.plane(SIDE[0] + SIDE[2] / 2, SIDE[1] + SIDE[2] * 640 / 1536 / 2, SIDE[2], name="sprite-side")]


def layers():
    return [H.defs(U, W, HT), background(), *sprites(), rescue(), signals(), elt_unit(), impact(), switch(), pills(), callouts()]


def plate():
    return {
        "id": "fig-09-06-elt",
        "replaces": "fig-09-06-elt.svg",                     # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-09-06-elt.jpg",
        "caption": "Figure 9-6. The emergency locator transmitter: an impact switches it on and it transmits on two frequencies at once (schematic)",
        "desc": ("Figure 9-6. The emergency locator transmitter, a schematic on the side view of the training aeroplane: an impact trips the crash sensor of the ELT in the aft fuselage, "
                 "and it transmits on 406 MHz and 121.500 MHz at the same time so that search and rescue can find the aeroplane."),
        "legend": [
            "The ELT, attached as far aft as practicable for automatic types, so as to minimise crash damage. The position drawn is a schematic, not that of any particular aeroplane.",
            "An impact: the crash sensor switches the ELT on. It is a radio beacon, required on every flight.",
            "A transmission on 406 MHz.",
            "A transmission on 121.500 MHz at the same time. After a hard landing, listen on 121.5 MHz before shutdown: a sweeping tone may be your own ELT.",
            "Search and rescue, who use the signals to find the aeroplane.",
            "The ELT switch in the cockpit: know where it is and that it is armed.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
