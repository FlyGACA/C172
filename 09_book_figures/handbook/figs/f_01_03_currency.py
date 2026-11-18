"""Figure 1-3 (new). Staying current as a private pilot, from the section "Staying current" of Chapter 1 (GACAR 61.17 and 61.21): three rows, each a bar that ends at "now" (a vertical line at the right).

Row 1, passengers by day: in the preceding 90 days at least 3 takeoffs and 3 landings (three pairs of an up arrow and a down arrow on the bar), as sole manipulator of the controls, in an aircraft of the same category and class. Row 2, passengers at night, between 1 hour after sunset and
1 hour before sunrise (a dark bar with a moon): in the preceding 90 days at least 3 takeoffs and 3 landings to a full stop (the landings marked with a stop bar) in that same period of the day. Row 3, the flight review: in the preceding 24 calendar months at least 1 hour of flight training
and 1 hour of ground training with an authorized instructor. The bars of the first two rows are the same length (90 days); the third is a different scale (24 months) and is drawn with a break to say so. No words but DAYS, MONTHS and H: the words are in the legend."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 290
U = "cu1"
INK, SLATE, BLUE, GREEN, AMBER, RED, NIGHT = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#1E3A8A"
X0, X1 = 150.0, 590.0
ROWY = (66.0, 142.0, 220.0)


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.0, height=12.0):
    w = gwidth(s, size) + 12.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.35))


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            + "".join(f'<line x1="22" y1="{n(y)}" x2="{W - 22}" y2="{n(y)}" stroke="{SLATE}" stroke-opacity="0.18" stroke-width="1"/>' for y in (104.0, 182.0))
            + f'<line x1="{n(X1 + 6)}" y1="26" x2="{n(X1 + 6)}" y2="{HT - 22}" stroke="{AMBER}" stroke-width="2.4" stroke-dasharray="5 4"/>')


def triangle(x, y, up, col, size=7.0):
    if up:
        return f'<path d="M{n(x)} {n(y - size)} L{n(x - size * 0.8)} {n(y + size * 0.6)} L{n(x + size * 0.8)} {n(y + size * 0.6)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="1"/>'
    return f'<path d="M{n(x)} {n(y + size)} L{n(x - size * 0.8)} {n(y - size * 0.6)} L{n(x + size * 0.8)} {n(y - size * 0.6)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="1"/>'


def sun(x, y):
    out = [f'<circle cx="{n(x)}" cy="{n(y)}" r="9" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.4" filter="url(#{U}ds)"/>']
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<line x1="{n(x + 12 * math.sin(a))}" y1="{n(y - 12 * math.cos(a))}" x2="{n(x + 16 * math.sin(a))}" y2="{n(y - 16 * math.cos(a))}" stroke="#F59E0B" stroke-width="2.4" stroke-linecap="round"/>')
    return "".join(out)


def moon(x, y):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="13" fill="{NIGHT}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            f'<circle cx="{n(x + 7)}" cy="{n(y - 5)}" r="11" fill="#FFFCF5"/>'
            f'<circle cx="{n(x + 20)}" cy="{n(y - 10)}" r="1.8" fill="#F59E0B"/><circle cx="{n(x + 17)}" cy="{n(y + 8)}" r="1.4" fill="#F59E0B"/>')


def books(x, y):
    return (f'<rect x="{n(x - 12)}" y="{n(y - 10)}" width="22" height="26" rx="2.6" fill="#1E3A8A" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            f'<rect x="{n(x - 8)}" y="{n(y - 5)}" width="14" height="8" rx="1.4" fill="#F8FAFC"/><line x1="{n(x - 8)}" y1="{n(y + 8)}" x2="{n(x + 6)}" y2="{n(y + 8)}" stroke="#F8FAFC" stroke-width="1.6"/>')


def bar(y, col, label, full=True):
    out = [f'<rect x="{n(X0)}" y="{n(y - 13)}" width="{n(X1 - X0)}" height="26" rx="8" fill="{col}" fill-opacity="0.92" stroke="#FFFFFF" stroke-width="1.4" filter="url(#{U}ds)"/>']
    out.append(pill(label, X0 + 50, y - 22, SLATE, 5.8, 11.0))
    return "".join(out)


def rows():
    out = []
    # row 1: passengers by day, 90 days, three takeoffs and three landings
    y = ROWY[0]
    out.append(sun(70, y))
    out.append(bar(y, "#93C5FD", "90 DAYS"))
    for k in range(3):
        x = X0 + 150 + k * 80
        out.append(triangle(x - 10, y, True, BLUE) + triangle(x + 10, y, False, BLUE))
    # row 2: passengers at night, 90 days, three takeoffs and three landings to a full stop
    y = ROWY[1]
    out.append(moon(70, y))
    out.append(bar(y, NIGHT, "90 DAYS"))
    for k in range(3):
        x = X0 + 150 + k * 80
        out.append(triangle(x - 10, y, True, "#93C5FD") + triangle(x + 10, y, False, "#93C5FD"))
        out.append(f'<rect x="{n(x + 17)}" y="{n(y - 8)}" width="3.2" height="16" rx="1" fill="{RED}" stroke="#FFFFFF" stroke-width="0.8"/>')   # the stop
    # row 3: flight review, 24 calendar months, 1 hour of flight and 1 hour of ground training
    y = ROWY[2]
    out.append(books(70, y))
    out.append(bar(y, "#86EFAC", "24 MONTHS"))
    out.append(f'<path d="M{n(X0 + 190)} {n(y - 12)} l7 8 l-7 10 l7 8" fill="none" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round"/>')   # the break: a different scale
    out.append(pill("1 H", X1 - 110, y, GREEN, 6.4, 14.0) + pill("1 H", X1 - 52, y, BLUE, 6.4, 14.0))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join(c(i + 1, 30.0, ROWY[i], r=9.5) for i in range(3))


def layers():
    return [H.defs(U, W, HT), background(), rows(), callouts()]


def plate():
    return {
        "id": "fig-01-03-currency",
        "replaces": "fig-01-03-currency.svg",              # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-01-03-currency.jpg",
        "caption": "Figure 1-3. Staying current: passengers by day, passengers at night and the flight review",
        "desc": ("Figure 1-3. Staying current as a private pilot, as three bars that end at now. Passengers by day: at least 3 takeoffs and 3 landings in the preceding 90 days. Passengers at night: at least 3 takeoffs and 3 landings "
                 "to a full stop in the preceding 90 days, in the period from 1 hour after sunset to 1 hour before sunrise. Flight review: in the preceding 24 calendar months, 1 hour of flight training and 1 hour of ground training."),
        "legend": [
            "Passengers by day: at least 3 takeoffs and 3 landings in the preceding 90 days, as sole manipulator of the controls, in an aircraft of the same category and class.",
            "Passengers at night, between 1 hour after sunset and 1 hour before sunrise: at least 3 takeoffs and 3 landings to a full stop (the red bars) in that same period of the day within the preceding 90 days.",
            "Flight review: in the preceding 24 calendar months, at least 1 hour of flight training (green) and 1 hour of ground training (blue) with an authorized instructor, covering the current Part 91 rules and the manoeuvres the instructor chooses. This bar is on another scale, as its break shows. The dashed line at the right is now.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
