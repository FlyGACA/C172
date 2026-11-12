"""Figure 8-3. A propeller blade section: blade angle, relative wind and angle of attack (angles exaggerated). The old figure's geometry kept exactly (the section turned 35 degrees to the
plane of rotation, the relative wind 22 degrees, so that the angle of attack is 13 degrees; every point and arc of it) and drawn as an illustration on a soft card: the blade section as a lit
solid (light upper surface, darker lower, a bright rim, a soft shadow), the plane of rotation, the chord line and the relative wind as light ribbons under it, the arcs of the blade angle
(grey) and the angle of attack (amber) with their ticks and Greek letters, the thrust as a green ribbon, and the triangle of rotational velocity, forward velocity and path as ribbons.
The nine numbered callouts of the old figure are kept."""
import math
import os
import re

from figs import scene as S
from figs import h_a3 as H

n = S.n
U = "f0803"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE = ("#2F63C8", "#8DB3F2")
GREEN = ("#0B7A4E", "#6FD1A2")
GREYBLUE = ("#5A6A88", "#B7C2D6")
AMBER = "#E8920F"
INKB = "#4B5B7C"


def blade_points():
    with open(os.path.join(HERE, "old", "fig-08-03-propeller-blade-angle.svg"), encoding="utf-8") as f:
        svg = f.read()
    m = re.search(r'<polygon points="([^"]+)" fill="url\(#bladeGrad\)"', svg)
    return [tuple(float(v) for v in p.split(",")) for p in m.group(1).split()]


def card():
    return S.card(U + "k", 8, 8, 624, 344, [(0, "#F8FAFE"), (1, "#DFE8F5")], "")


def band(x0, y0, x1, y1, colour, core, dash, width=7.0, opacity=0.62):
    """A light ribbon: a wide translucent band with a thin dashed line down its middle."""
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{core}" stroke-width="1.5" stroke-dasharray="{dash}" stroke-linecap="round"/>')


def lines():
    out = [band(40, 214, 610, 214, "#FFFFFF", "#6B7A96", "8 5", 8.0, 0.85)]
    out.append(band(127.1, 300, 520.3, 24.7, "#FFFFFF", "#6B7A96", "3 4", 8.0, 0.85))
    out.append(S.ribbon(U + "wd", [(556.0, 90.4), (342.0, 176.0), (129.5, 262.7)], 5.2, *GREEN, head=2.0, opacity=0.9))
    return "".join(out)


def blade():
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in blade_points()) + " Z"
    return (f'<defs>{S.gradient(U + "bl", [(0, "#FFFFFF"), (0.28, "#E2EBFA"), (0.62, "#A9BBE0"), (1, "#667CA8")])}<clipPath id="{U}bc"><path d="{d}"/></clipPath></defs>'
            f'<path d="{d}" fill="#14233F" fill-opacity="0.26" transform="translate(2.2 4.4)" filter="url(#{U}b2)"/>'
            f'<path d="{d}" fill="url(#{U}bl)" stroke="#3F4D6A" stroke-width="1.8" stroke-linejoin="round"/>'
            f'<g clip-path="url(#{U}bc)"><path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="2" transform="translate(0 2.4)"/>'
            f'<path d="{d}" fill="none" stroke="#25345A" stroke-opacity="0.32" stroke-width="2.4" transform="translate(0 -2.6)"/></g>')


def arcs():
    def arc(d, colour):
        return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="6.4" stroke-opacity="0.9" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{colour}" stroke-width="3" stroke-linecap="round"/>')
    ticks = [(485, 214, 478, 214, 1.5), (477, 160, 470, 162, 1.2), (460, 110, 453, 113, 1.2), (442.5, 79.2, 437, 84, 1.5)]
    out = [arc("M485.0,214.0 A235,235 0 0 0 442.5,79.2", INKB), arc("M421.5,144.7 A185,185 0 0 0 401.5,107.9", AMBER)]
    out += [f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{INKB}" stroke-width="{w}" stroke-linecap="round"/>' for a, b, c, d, w in ticks]
    out.append(f'<text x="490.3" y="143.2" font-family="serif" font-size="19" font-style="italic" fill="{INKB}" stroke="#FFFFFF" stroke-width="3.2" stroke-opacity="0.9" paint-order="stroke">β</text>')
    out.append(f'<text x="397.2" y="136.9" font-family="serif" font-size="19" font-style="italic" fill="{AMBER}" stroke="#FFFFFF" stroke-width="3.2" stroke-opacity="0.9" paint-order="stroke">α</text>')
    return "".join(out)


def vectors():
    r = S.ribbon
    return "".join([r(U + "th", [(282, 178), (282, 128), (282, 76)], 5.2, *GREEN, head=2.2),
                    r(U + "rp", [(340, 320), (445, 320), (550, 320)], 5.2, *BLUE, head=2.2),
                    r(U + "as", [(550, 320), (550, 280), (550, 235.2)], 5.2, *BLUE, head=2.2),
                    r(U + "rs", [(340, 320), (443, 280), (546, 237.2)], 4.6, *GREYBLUE, head=2.2, opacity=0.9)])


def callouts():
    c = S.callout
    return "".join([c(1, 40, 236, 70, 214), c(2, 590, 36, 496, 42), c(3, 536, 164), c(4, 445, 344, 445, 320), c(5, 596, 280, 552, 280), c(6, 612, 64, 560, 89), c(7, 439, 111),
                    c(8, 248, 96, 280, 110), c(9, 300, 300, 420, 287.7)])


def plate():
    layers = ['<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>', H.common_defs(U), card(), lines(), blade(), arcs(), vectors(), callouts()]
    return {
        "id": "fig-08-03-propeller-blade-angle",
        "replaces": "fig-08-03-propeller-blade-angle.svg",
        "book_file": "plate-08-03-propeller-blade-angle.jpg",
        "caption": "Figure 8-3. A propeller blade section: blade angle, relative wind and angle of attack (angles exaggerated)",
        "desc": "Figure 8-3. A propeller blade section: blade angle, relative wind and angle of attack (angles exaggerated)",
        "legend": [
            "Plane of rotation.",
            "Chord line of the blade section.",
            "Blade angle (β), between the chord line and the plane of rotation.",
            "The section's rotational velocity.",
            "The aeroplane's forward velocity.",
            "Relative wind, opposite to the section's path through the air.",
            "Angle of attack (α), between the chord line and the relative wind.",
            "Thrust.",
            "The section's path through the air, the sum of 4 and 5.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-08-03-propeller-blade-angle.svg", "blank": True, "layers": layers},
    }
