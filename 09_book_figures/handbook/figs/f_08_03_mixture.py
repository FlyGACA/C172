"""Figure 8-3 (new). Mixture and leaning, as three balance scales: air (blue block, left pan) against fuel (amber block, right pan).

Left, sea level, full rich: air and fuel are in step (100 % and 100 %), the beam is level. Middle, 8 000 ft, still full rich: the air is thinner (about 79 % of its sea-level density, as Chapter 8 says)
but the fuel flow has not changed (100 %), so the fuel pan goes down: the mixture is too rich (red). Right, 8 000 ft, leaned: the fuel is cut to match the air (79 % and 79 %) and the beam is level again.
The engine may give about three-quarters of its sea-level power at 8 000 ft (the figure the chapter gives); no power is drawn for the rich case, for which the chapter gives no number; the picture shows the idea, the blocks are drawn in proportion to the percentages. Digits, FT, %, = and >."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 244
U = "mx8"
CX = (118.0, 320.0, 522.0)
BLUE, AMBER, GREEN, RED, SLATE = "#1D4ED8", "#B45309", "#15803D", "#B91C1C", "#475569"
AIR = (100, 79, 79)
FUEL = (100, 100, 79)
ALT = ("0 FT", "8 000 FT", "8 000 FT")
TILT = (0.0, 9.0, 0.0)                                   # degrees: the fuel (right) side goes down
PIV_Y = 100.0
HALF = 56.0


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
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            + "".join(f'<line x1="{n(x)}" y1="40" x2="{n(x)}" y2="{HT - 22}" stroke="{SLATE}" stroke-opacity="0.18" stroke-width="1"/>' for x in (219.0, 421.0)))


def scale(i):
    cx = CX[i]
    th = math.radians(TILT[i])
    bad = i == 1
    col = RED if bad else GREEN
    out = []
    # the post and the base
    out.append(f'<path d="M{n(cx - 28)} {n(HT - 30)} L{n(cx + 28)} {n(HT - 30)} L{n(cx + 7)} {n(PIV_Y + 6)} L{n(cx - 7)} {n(PIV_Y + 6)} Z" fill="#94A3B8" stroke="{SLATE}" stroke-width="1.4" stroke-linejoin="round"/>')
    # the beam: right end down by TILT
    lx, ly = cx - HALF * math.cos(th), PIV_Y - HALF * math.sin(th)
    rx, ry = cx + HALF * math.cos(th), PIV_Y + HALF * math.sin(th)
    out.append(f'<line x1="{n(lx)}" y1="{n(ly)}" x2="{n(rx)}" y2="{n(ry)}" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round"/><line x1="{n(lx)}" y1="{n(ly)}" x2="{n(rx)}" y2="{n(ry)}" stroke="{col}" stroke-width="5.4" stroke-linecap="round"/>')
    out.append(f'<circle cx="{n(cx)}" cy="{n(PIV_Y)}" r="6.4" fill="{SLATE}" stroke="#FFFFFF" stroke-width="1.6"/>')
    # the two pans, hanging from the beam ends, with the blocks
    for (x, y, val, c, side) in ((lx, ly, AIR[i], BLUE, -1), (rx, ry, FUEL[i], AMBER, 1)):
        py = y + 52.0
        out.append(f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(x - 18)}" y2="{n(py)}" stroke="{SLATE}" stroke-width="1.5"/><line x1="{n(x)}" y1="{n(y)}" x2="{n(x + 18)}" y2="{n(py)}" stroke="{SLATE}" stroke-width="1.5"/>')
        h = 0.42 * val
        out.append(f'<rect x="{n(x - 12)}" y="{n(py - h)}" width="24" height="{n(h)}" rx="3" fill="{c}" fill-opacity="0.9" stroke="#FFFFFF" stroke-width="1.4" filter="url(#{U}ds)"/>')
        out.append(f'<path d="M{n(x - 23)} {n(py)} Q{n(x)} {n(py + 13)} {n(x + 23)} {n(py)} Z" fill="#CBD5E1" stroke="{SLATE}" stroke-width="1.4" stroke-linejoin="round"/>')
        out.append(pill(f"{val} %", x, py + 25, c, 6.2, 12.0))
    # the sign between them
    out.append(pill("=" if i != 1 else ">", cx, PIV_Y - 28, col, 8.0, 14.0))
    # the altitude, at the top
    out.append(pill(ALT[i], cx, 26.0, SLATE, 7.0, 13.0))
    return "".join(out)


def power():
    """Under the scales: the power, in a pill, for the three."""
    out = []
    for i, cx in enumerate(CX):
        if i == 1:                                         # too rich: the chapter says power is lost, but gives no number, so none is drawn
            continue
        p = ("100 %", "75 %", "75 %")[i]
        out.append(pill(p, cx, HT - 17, SLATE, 7.0, 13.0))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join(c(i + 1, CX[i] - 82, 26.0, CX[i] - 36, 26.0, r=9.5) for i in range(3))


def layers():
    return [H.defs(U, W, HT), background(), *[scale(i) for i in range(3)], power(), callouts()]


def plate():
    return {
        "id": "fig-08-03-mixture",
        "replaces": "fig-08-03-mixture.svg",               # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-08-03-mixture.jpg",
        "caption": "Figure 8-3. Mixture and leaning: air against fuel at sea level, at 8 000 ft full rich and at 8 000 ft leaned",
        "desc": ("Figure 8-3. Mixture and leaning shown as three balance scales, air against fuel. At sea level, full rich, they balance. At 8 000 ft the air is about 79 % of its sea-level density "
                 "but with the mixture still full rich the fuel is 100 %, so the fuel side goes down: too rich. Leaned, the fuel is cut to 79 % and the scale balances again; the power is then about three-quarters of the sea-level power."),
        "legend": [
            "Sea level, mixture full rich: the air and the fuel are in step and the scale balances. This is the ratio the carburettor gives at sea-level density; the power below is the engine's full power (100 %).",
            "8 000 ft with the mixture still full rich: the air is thinner, about 79 % of its sea-level density, but the carburettor does not cut the fuel in proportion. The fuel side goes down: the mixture is richer, which wastes fuel, loses power, runs rough and fouls the plugs.",
            "8 000 ft, leaned: drawing the mixture control back cuts the fuel to match the air and the scale balances again. A normally aspirated engine at 8 000 ft may give only about three-quarters of its sea-level power, even with a good mixture (the pill below).",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
