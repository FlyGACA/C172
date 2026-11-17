"""Figure 9-5 (new). Cabin heat and carbon monoxide, a schematic on the side view of the training aeroplane (sprite-side): outside air enters at the front of the cowling (blue), is warmed in a shroud round the exhaust
muffler (amber) and goes through the firewall to the cabin vents (orange). If the muffler or a pipe cracks (red burst), carbon monoxide, colourless and odourless, joins the warmed air (red dots) and enters the
cabin with it. As Chapter 9 says, this is how most light aeroplanes heat the cabin; the routing of a particular aeroplane is in its manual, and the picture is a schematic, not a drawing of the aeroplane's ducts. No words:
colours, arrows and the numbers of the callouts."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "co9"
SIDE = (-176.0, -6.0, 800.0)                                # left, top, width of the side sprite's box (1536 x 640): enlarged, the tail is off the picture
BLUE, AMBER, ORANGE, RED, SLATE, GREEN = "#1D4ED8", "#B45309", "#EA580C", "#B91C1C", "#475569", "#15803D"


def sx(u, v):
    """A point of the side sprite given in tenths (0..10) of its box."""
    return SIDE[0] + u / 10.0 * SIDE[2], SIDE[1] + v / 10.0 * SIDE[2] * 640 / 1536


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def path_arrow(points, col, width=4.0, dash=None, head=10.0):
    d = "M" + " L".join(f"{n(x)} {n(y)}" for x, y in points)
    x0, y0 = points[-2]
    x1, y1 = points[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{n(width + 3.4)}" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round" stroke-linejoin="round"{dd}/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * head * 0.62)} {n(hy + ny * head * 0.62)} L{n(hx - nx * head * 0.62)} {n(hy - ny * head * 0.62)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="1" stroke-linejoin="round"/>')


def burst(x, y, r, col):
    pts_ = []
    for k in range(16):
        a = math.radians(k * 22.5)
        rr = r if k % 2 == 0 else r * 0.45
        pts_.append((x + rr * math.sin(a), y - rr * math.cos(a)))
    return f'<polygon points="{" ".join(f"{n(a)},{n(b)}" for a, b in pts_)}" fill="{col}" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round" filter="url(#{U}ds)"/>'


def flow():
    out = []
    # outside air in, at the front of the cowling, to the muffler's shroud
    out.append(path_arrow([sx(10.0, 5.0), sx(9.6, 5.35), sx(9.25, 5.7)], BLUE, 4.0))
    # the shroud round the muffler, under the engine
    mx, my = sx(9.02, 5.95)
    out.append(f'<ellipse cx="{n(mx)}" cy="{n(my)}" rx="22" ry="12" fill="{AMBER}" fill-opacity="0.25" stroke="{AMBER}" stroke-width="2.4" stroke-dasharray="4 2.4"/>')
    # the warmed air to the cabin, through the firewall
    out.append(path_arrow([sx(8.8, 5.7), sx(8.55, 5.3), sx(8.15, 4.95), sx(7.75, 4.6)], ORANGE, 4.4))
    # the carbon monoxide: a crack in the muffler and red dots that follow the warm air into the cabin
    out.append(burst(sx(9.12, 6.2)[0], sx(9.12, 6.2)[1], 11.0, RED))
    for k, (u, v) in enumerate(((8.9, 5.55), (8.72, 5.35), (8.52, 5.15), (8.3, 4.95), (8.08, 4.8), (7.9, 4.62), (7.72, 4.46))):
        x, y = sx(u, v)
        out.append(f'<circle cx="{n(x + 3.4)}" cy="{n(y + 6.4)}" r="{n(4.4 + 0.12 * k)}" fill="{RED}" stroke="#FFFFFF" stroke-width="0.9"/>')
    # the cabin, where the pilot breathes
    cx, cy = sx(7.3, 4.2)
    out.append(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="38" ry="26" fill="{RED}" fill-opacity="0.12" stroke="{RED}" stroke-width="1.6" stroke-dasharray="3 3"/>')
    return "".join(out)


def detector():
    """A carbon monoxide detector on the glareshield: a small box with a green light."""
    x, y = sx(7.78, 3.62)
    return (f'<rect x="{n(x - 9)}" y="{n(y - 6.6)}" width="18" height="13.2" rx="2.6" fill="#F4F1E8" stroke="{SLATE}" stroke-width="1.5" filter="url(#{U}ds)"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="3.4" fill="{GREEN}"/>')


def callouts():
    c = S.callout
    r = 9.5
    out = []
    out.append(c(1, *sx(9.97, 3.3), *sx(10.0, 4.95), r=r))        # the air in
    out.append(c(2, *sx(8.95, 8.5), *sx(9.0, 6.2), r=r))          # the muffler and its shroud
    out.append(c(3, *sx(8.05, 6.9), *sx(8.4, 5.2), r=r))          # the warmed air to the cabin
    out.append(c(4, *sx(9.8, 8.4), *sx(9.2, 6.35), r=r))          # the crack and the carbon monoxide
    out.append(c(5, *sx(6.7, 2.35), *sx(7.2, 3.9), r=r))          # the cabin: where the pilot breathes
    out.append(c(6, *sx(7.95, 2.6), *sx(7.78, 3.5), r=r))         # the detector
    return "".join(out)


def sprites():
    return [A.plane(SIDE[0] + SIDE[2] / 2, SIDE[1] + SIDE[2] * 640 / 1536 / 2, SIDE[2], name="sprite-side")]


def layers():
    return [H.defs(U, W, HT), background(), *sprites(), flow(), detector(), callouts()]


def plate():
    return {
        "id": "fig-09-05-carbon-monoxide",
        "replaces": "fig-09-05-carbon-monoxide.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-09-05-carbon-monoxide.jpg",
        "caption": "Figure 9-5. Cabin heat and carbon monoxide: outside air warmed round the exhaust muffler, and what a crack lets in (schematic)",
        "desc": ("Figure 9-5. Cabin heat and carbon monoxide: outside air warmed round the exhaust muffler, and what a crack lets in. A schematic on the side view of the training aeroplane: air enters "
                 "at the front of the cowling, is warmed in a shroud round the muffler and goes through the firewall to the cabin; a crack in the muffler lets carbon monoxide into the same air."),
        "legend": [
            "Outside air enters at the front of the cowling.",
            "The exhaust muffler, with the shroud round it that warms the air. The exhaust gas stays inside the muffler; only the air passes through the shroud.",
            "The warmed air goes through the firewall to the cabin vents.",
            "A crack in the muffler or in a pipe: carbon monoxide, colourless and odourless, joins the warmed air and goes into the cabin with it.",
            "The cabin, where the pilot breathes it. Early signs are headache, drowsiness, dizziness and blurred vision; there may be no smell.",
            "A carbon monoxide detector in the cockpit: a cheap safeguard. If the detector sounds or you have the signs, turn the heat off, open the fresh-air vents, use oxygen if you have it and land as soon as possible.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
