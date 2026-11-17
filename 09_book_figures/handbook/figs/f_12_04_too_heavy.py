"""Figure 12-4 (new). Too heavy: the fix of carrying less fuel, from the worked flight of Chapter 12 ("Too heavy"), as two stacked bars of mass drawn to one scale from zero.

Top bar, the loading of the chapter's table: basic empty mass 760 kg (grey), pilot, front passenger and rear passenger 155 + 70 = 225 kg (blue), baggage 45 kg (amber) and fuel 108 kg for 150 L (green): 1138 kg, which crosses the red line of the maximum
takeoff mass, 1100 kg, by 38 kg (red). Bottom bar, after the first fix: the same except the fuel, 90 L = 64.8 kg: 1094.8 kg, inside the line. Every number is the chapter's own. Digits and KG; the words are in the legend."""
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 262
U = "th12"
X0 = 36.0
K = 530.0 / 1150.0                                         # canvas units per kilogram
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
SEG = (("#94A3B8", 760.0), (BLUE, 225.0), ("#F59E0B", 45.0))
BAR_H = 36.0
ROWS = (96.0, 186.0)
FUEL = (108.0, 64.8)
TOTAL = (1138.0, 1094.8)
MTOW = 1100.0


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.0, height=12.0):
    w = gwidth(s, size) + 12.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.35))


def xk(kg):
    return X0 + kg * K


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter>'
            f'<pattern id="{U}hz" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="{RED}"/><line x1="0" y1="0" x2="0" y2="6" stroke="#FFFFFF" stroke-width="2.2"/></pattern></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def bars():
    out = []
    for i, y in enumerate(ROWS):
        x = X0
        for col, kg in SEG:
            out.append(f'<rect x="{n(x)}" y="{n(y - BAR_H / 2)}" width="{n(kg * K)}" height="{BAR_H}" fill="{col}" stroke="#FFFFFF" stroke-width="1.4"/>')
            x += kg * K
        out.append(f'<rect x="{n(x)}" y="{n(y - BAR_H / 2)}" width="{n(FUEL[i] * K)}" height="{BAR_H}" fill="{GREEN}" stroke="#FFFFFF" stroke-width="1.4"/>')
        if i == 0:
            out.append(f'<rect x="{n(xk(MTOW))}" y="{n(y - BAR_H / 2)}" width="{n((TOTAL[0] - MTOW) * K)}" height="{BAR_H}" fill="url(#{U}hz)" stroke="#FFFFFF" stroke-width="1.2"/>')
        out.append(pill(("1138 KG", "1094.8 KG")[i], xk(TOTAL[i]) + (46 if i == 0 else 56), y, SLATE if i else RED, 6.4, 14.0))
    return "".join(out)


def limit():
    x = xk(MTOW)
    return (f'<line x1="{n(x)}" y1="46" x2="{n(x)}" y2="226" stroke="{RED}" stroke-width="3" stroke-dasharray="7 4"/>'
            + pill("1100 KG", x - 40.0, 40.0, RED, 6.4, 14.0))


def labels():
    out = []
    # the segment masses, under the bars
    for i, y in enumerate(ROWS):
        x = X0
        for (col, kg), txt in zip(SEG, ("760", "225", "45")):
            out.append(H.glyph_text(txt, x + kg * K / 2, y + BAR_H / 2 + 12.0, 5.2, SLATE, spacing=0.3))
            x += kg * K
        out.append(H.glyph_text(("108", "64.8")[i], x + FUEL[i] * K / 2 - 9.0, y + BAR_H / 2 + 12.0, 5.2, GREEN, spacing=0.3))
    out.append(pill("38 KG", xk(MTOW) + 24.0, ROWS[0] - 36.0, RED, 5.8, 12.0))
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.5
    out = []
    out.append(c(1, 22.0, ROWS[0] - 38.0, xk(300.0), ROWS[0] - BAR_H / 2 + 4.0, r=r))                              # the loading of the table
    out.append(c(2, 22.0, ROWS[1] - 38.0, xk(300.0), ROWS[1] - BAR_H / 2 + 4.0, r=r))                              # after the first fix
    out.append(c(3, xk(MTOW) - 6.0, 238.0, xk(MTOW), 214.0, r=r))                                                  # the maximum takeoff mass
    out.append(c(4, xk(TOTAL[0]) + 52.0, ROWS[0] - 36.0, xk(1119.0), ROWS[0] - 14.0, r=r))                          # the excess
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), bars(), limit(), labels(), callouts()]


def plate():
    return {
        "id": "fig-12-04-too-heavy",
        "replaces": "fig-12-04-too-heavy.svg",            # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-12-04-too-heavy.jpg",
        "caption": "Figure 12-4. Too heavy: the planned loading against the maximum takeoff mass, and the same loading with less fuel",
        "desc": ("Figure 12-4. Too heavy. Two bars of mass to one scale: the planned loading of 1138 kg, 38 kg over the maximum takeoff mass of 1100 kg, and the same loading with 90 L of fuel, 1094.8 kg, inside it. "
                 "From left to right: basic empty mass 760 kg, occupants 225 kg, baggage 45 kg and fuel."),
        "legend": [
            "The loading of the chapter's table: basic empty mass 760 kg (grey), pilot, front passenger and rear passenger 155 + 70 = 225 kg (blue), baggage 45 kg (amber) and fuel 108 kg, for 150 L (green): 1138 kg.",
            "The first fix: carry less fuel. 90 L is 64.8 kg, so the mass is 1094.8 kg. The trip needs 50 L and the 30-minute day reserve another 15 L, 65 L in all, so 25 L are left over for a diversion.",
            "The maximum takeoff mass, 1100 kg. The most fuel you can carry is this minus the zero-fuel mass: 1100 − 1030 = 70 kg, or 97.2 L.",
            "The excess of the planned loading, 38 kg (the red hatching): the loading is outside the envelope even though the CG is between its limits.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
