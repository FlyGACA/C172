"""Figure 7-2. Trailing-edge flap types and a leading-edge slat, in section. Six cards, each a wing section drawn as a lit solid (the outlines of the old figure, kept exactly: the same
aerofoil, the same hinge points, the same angles of deflection, the same slots): a light upper surface and a darker lower one, a rim of light along the top, a soft shadow, the flap in
amber hinged on a small metal pin and deflected as in the old figure, the dashed arc the flap travels, the dashed ghost of the retracted wing for the Fowler flap, thin streamlines of
air over and under each section, and the blue ribbons of the old figure where air runs through a slot. The six numbered callouts are kept."""
import math
import os
import re

from figs import scene as S
from figs import h_a3 as H

n = S.n
U = "f0702"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE = ("#2F63C8", "#8DB3F2")

# the six cards: x, y, w, h
CARDS = [(8, 6, 308, 112), (8, 122, 308, 112), (8, 238, 308, 112), (324, 6, 308, 112), (324, 122, 308, 112), (324, 238, 308, 112)]


def load_paths():
    """The paths of the old drawing, in the order the file has them: [(d, points)] (a polyline for the outlines, the sampled curve for the arcs and arrows)."""
    with open(os.path.join(HERE, "old", "fig-07-02-flap-types.svg"), encoding="utf-8") as f:
        svg = f.read()
    out = []
    for m in re.finditer(r'<path d="([^"]+)" fill="([^"]*)" stroke="([^"]*)" stroke-width="([\d.]+)"([^/]*)/>', svg):
        d = m.group(1)
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
        pts = [(nums[k], nums[k + 1]) for k in range(0, len(nums), 2)]
        if "C" in d:
            samples = [pts[0]]
            for i in range(0, len(pts) - 3, 3):
                a, b, c, e = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
                for k in range(1, 9):
                    t = k / 8.0
                    u = 1 - t
                    samples.append(tuple(u ** 3 * a[j] + 3 * u * u * t * b[j] + 3 * u * t * t * c[j] + t ** 3 * e[j] for j in (0, 1)))
            pts = samples
        out.append((d, pts))
    return out


def poly_d(pts):
    return "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in pts) + " Z"


def gradients():
    g = S.gradient
    return ("<defs>"
            + g(U + "wing", [(0, "#FFFFFF"), (0.30, "#E6EEFB"), (0.68, "#B4C5E6"), (1, "#7C91BA")])
            + g(U + "plain", [(0, "#FFD98B"), (0.5, "#F29A2C"), (1, "#B4590B")])
            + g(U + "split", [(0, "#FFB98A"), (0.5, "#E5622A"), (1, "#9A3412")])
            + g(U + "slot", [(0, "#FFD27A"), (0.5, "#E8861F"), (1, "#A8500C")])
            + g(U + "fowler", [(0, "#FFDB8A"), (0.5, "#F0A12E"), (1, "#A8680F")])
            + f'<radialGradient id="{U}pin" cx="0.36" cy="0.32" r="0.8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.5" stop-color="#C3CCDA"/><stop offset="1" stop-color="#5E6B82"/></radialGradient>'
            + "</defs>")


def solid(uid, d, grad, edge="#3F4D6A", shadow=True, opacity=1.0):
    """A section as a lit solid: a soft shadow, the gradient (light above, dark below), a thin outline, a bright line along its top edge and a dark one along its lower edge (both cut to the shape)."""
    return (f'<defs><clipPath id="{uid}c"><path d="{d}"/></clipPath></defs>'
            + (f'<path d="{d}" fill="#14233F" fill-opacity="0.24" transform="translate(1.8 3.6)" filter="url(#{U}b2)"/>' if shadow else "")
            + f'<path d="{d}" fill="url(#{grad})" stroke="{edge}" stroke-width="1.5" stroke-linejoin="round" opacity="{n(opacity)}"/>'
            + f'<g clip-path="url(#{uid}c)"><path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.5" transform="translate(0 1.9)"/>'
              f'<path d="{d}" fill="none" stroke="#25345A" stroke-opacity="0.32" stroke-width="2" transform="translate(0 -2.2)"/></g>')


def pin(uid, x, y, r=2.5):
    return f'<circle cx="{n(x + 0.5)}" cy="{n(y + 1.2)}" r="{n(r)}" fill="#14233F" fill-opacity="0.3"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#{U}pin)" stroke="#3F4D6A" stroke-width="0.7"/>'


def stream(uid, points, width=2.2, opacity=0.8):
    """A thin streamline of air: a soft light ribbon with a small head."""
    return S.ribbon(uid, points, width, "#7FA3DE", "#DCE8FA", opacity=opacity, head=2.2, tail=0.6, shadow=False, per=8)


def surfaces(pts):
    """The upper and lower surface of the old aerofoil (path 0: from the trailing edge along the upper surface to the leading edge and back along the lower) as functions of x."""
    upper = sorted(pts[:41])
    lower = sorted(pts[40:])

    def at(curve, x):
        for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1.0)
        return curve[0][1] if x < curve[0][0] else curve[-1][1]
    return (lambda x: at(upper, x)), (lambda x: at(lower, x))


def streams(prefix, dx, dy, yu, yl, lower=True, x_end=236):
    """Streamlines over (and under) a section: thin light ribbons that part round the aerofoil at offsets from its surface, in the old figure's coordinates moved by (dx, dy). They run
    from the left of the section to just short of the flap, where the old figure's own arrows take over."""
    xs = [24, 62, 100, 150, 200, x_end]
    out = []
    for i, (d, side) in enumerate(((13, -1), (27, -1), (13, 1))):
        if side > 0 and not lower:
            continue
        pts_ = []
        for x in xs:
            if x < 62:
                y = 64 + side * (d + 1.0)
            elif side < 0:
                y = yu(x) - d
            else:
                y = yl(x) + d
            pts_.append((x + dx, y + dy))
        out.append(stream(f"{U}{prefix}s{i}", pts_))
    return "".join(out)


def card(k, body):
    x, y, w, h = CARDS[k]
    return S.card(f"{U}k{k}", x, y, w, h, [(0, "#F6F9FE"), (1, "#DCE6F4")], "") + S.card_front(f"{U}k{k}", x, y, w, h, body)


def arc(d):
    return f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-opacity="0.8" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#2F63C8" stroke-width="1.5" stroke-dasharray="4 3" stroke-linecap="round"/>'


def cells(paths):
    P = lambda i: paths[i][1]
    D = lambda i: poly_d(P(i))
    yu, yl = surfaces(P(0))
    out = []
    # 1: the basic section
    out.append(card(0, streams("a", 0, 0, yu, yl) + solid(U + "w1", D(0), U + "wing")))
    # 2: plain flap: the wing's front, the wedge of the flap hinged at the top and swung down, the dashed arc of its tip
    out.append(card(1, streams("b", 0, 114, yu, yl) + arc(paths[2][0]) + solid(U + "w2", D(3), U + "wing") + solid(U + "f2", D(5), U + "split") + pin(U, 233.2, 169.0)))
    # 3: split flap: the whole section and a plate hinged under it
    out.append(card(2, streams("c", 0, 228, yu, yl) + arc(paths[9][0]) + solid(U + "w3", D(7), U + "wing") + solid(U + "f3", D(8), U + "slot") + pin(U, 231.2, 298.2, 2.0)))
    # 4: slotted flap
    out.append(card(3, streams("d", 310, 0, yu, yl, lower=False) + solid(U + "w4", D(10), U + "wing") + solid(U + "f4", D(11), U + "slot")
                    + S.ribbon(U + "r4", paths[12][1][::2] + [paths[12][1][-1]], 3.8, *BLUE, head=2.4)))
    # 5: Fowler flap, the retracted wing dashed
    ghost = (f'<path d="{D(13)}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-opacity="0.8" stroke-linejoin="round"/>'
             f'<path d="{D(13)}" fill="none" stroke="#6F7E9C" stroke-width="1.3" stroke-dasharray="4 3" stroke-linejoin="round"/>')
    out.append(card(4, streams("e", 304, 114, yu, yl, lower=False) + ghost + solid(U + "w5", D(14), U + "wing") + solid(U + "f5", D(15), U + "fowler")
                    + S.ribbon(U + "r5", paths[16][1][::2] + [paths[16][1][-1]], 3.8, *BLUE, head=2.4)))
    # 6: the leading-edge slat
    out.append(card(5, streams("f", 336, 228, yu, yl, lower=False, x_end=170) + solid(U + "w6", D(17), U + "wing") + solid(U + "f6", D(18), U + "slot")
                    + S.ribbon(U + "r6", paths[19][1][::2] + [paths[19][1][-1]], 3.8, *BLUE, head=2.4)))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 30, 30), c(2, 30, 144), c(3, 30, 258), c(4, 340, 30), c(5, 340, 144), c(6, 340, 258)])


def plate():
    paths = load_paths()
    layers = ['<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>', H.common_defs(U), gradients(), cells(paths), callouts()]
    return {
        "id": "fig-07-02-flap-types",
        "replaces": "fig-07-02-flap-types.svg",
        "book_file": "plate-07-02-flap-types.jpg",
        "caption": "Figure 7-2. Trailing-edge flap types and a leading-edge slat, in section",
        "desc": "Figure 7-2. Trailing-edge flap types and a leading-edge slat, in section",
        "legend": [
            "Basic section, flaps retracted.",
            "Plain flap: the rear of the wing hinges down. More lift, much more drag, and a nose-down pitching tendency.",
            "Split flap: only the lower surface hinges down. Slightly more lift than a plain flap, and more drag.",
            "Slotted flap: air from below flows through a slot and keeps the flow attached over the flap. Much more lift; common on light aeroplanes.",
            "Fowler flap: slides aft, then turns down, adding wing area as well as camber (dashed: the retracted wing). Early travel adds mostly lift, late travel mostly drag.",
            "Leading-edge slat: moves forward to open a slot, so the wing stalls at a higher angle of attack.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-07-02-flap-types.svg", "blank": True, "layers": layers},
    }
