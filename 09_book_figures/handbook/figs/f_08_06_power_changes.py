"""Figure 8-6 (new). The order of power changes, from the educational rule of thumb of Chapter 8 ("RPM up first, manifold pressure down first"), as two rows of three steps.

To increase power (green arrow at the left): 1 enrich as required (the red mixture knob, up arrow, dashed because it is "as required"), 2 raise the RPM (the blue propeller knob, up arrow), 3 raise the manifold pressure (the black throttle knob, up arrow).
To decrease power (amber arrow): 1 reduce the manifold pressure (throttle, down arrow), 2 reduce the RPM (propeller, down arrow), 3 lean as required (mixture, down arrow, dashed). The knobs are generic, not the quadrant of any aeroplane; the chapter says
that this is a rule of thumb and that the flight manual and its power tables take precedence. Digits, MP, RPM and MIX: the words are in the legend."""
import math

from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 244
U = "pw85"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
COLX = (160.0, 340.0, 520.0)
ROWY = (62.0, 172.0)
# (control, direction, optional) for each step of each row; control: "mix", "rpm", "mp"
STEPS = (
    (("mix", +1, True), ("rpm", +1, False), ("mp", +1, False)),      # to increase power
    (("mp", -1, False), ("rpm", -1, False), ("mix", -1, True)),      # to decrease power
)
KNOB = {"mix": ("#DC2626", "#7F1D1D", "MIX"), "rpm": ("#2563EB", "#1E3A8A", "RPM"), "mp": ("#1F2937", "#030712", "MP")}


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=5.8, height=11.0):
    return M.chip(x, y, s, colour, size=size * 1.05, anchor="middle", light=True, height=height)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            f'<line x1="22" y1="118" x2="{W - 22}" y2="118" stroke="{SLATE}" stroke-opacity="0.2" stroke-width="1"/>')


def arrow(x0, y0, x1, y1, col, width=4.0, head=10.0, dash=None):
    return M.arrow(x0, y0, x1, y1, col, width=width * 0.8, head=head, dash=dash)


def knob(x, y, kind, optional):
    fill, edge, label = KNOB[kind]
    dash = ' stroke-dasharray="4 3"' if optional else ""
    op = ' fill-opacity="0.55"' if optional else ""
    return (f'<rect x="{n(x - 4.4)}" y="{n(y + 13)}" width="8.8" height="20" fill="#94A3B8" stroke="{SLATE}" stroke-width="1"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="15" fill="{fill}"{op} stroke="{edge}" stroke-width="2.2"{dash} filter="url(#{U}ds)"/>'
            f'<circle cx="{n(x - 4.6)}" cy="{n(y - 5)}" r="4.4" fill="#FFFFFF" fill-opacity="0.35"/>'
            + pill(label, x, y + 44, SLATE))


def row(i):
    out = []
    y = ROWY[i]
    col = GREEN if i == 0 else AMBER
    # the arrow of the row, at the left: power up or power down
    if i == 0:
        out.append(arrow(54, y + 22, 54, y - 24, col, 8.0, 18.0))
    else:
        out.append(arrow(54, y - 24, 54, y + 22, col, 8.0, 18.0))
    for k, (kind, d, optional) in enumerate(STEPS[i]):
        x = COLX[k]
        out.append(knob(x, y, kind, optional))
        # the direction of the change beside the knob
        ax = x + 34
        if d > 0:
            out.append(arrow(ax, y + 14, ax, y - 14, GREEN, 4.2, 10.0, None))
        else:
            out.append(arrow(ax, y - 14, ax, y + 14, AMBER, 4.2, 10.0, None))
        if k < 2:
            cx = (COLX[k] + COLX[k + 1]) / 2 + 12
            out.append(f'<path d="M{n(cx - 6)} {n(y - 9)} L{n(cx + 5)} {n(y)} L{n(cx - 6)} {n(y + 9)}" fill="none" stroke="{SLATE}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


def callouts():
    c = S.callout
    out = []
    for i in range(2):
        for k in range(3):
            out.append(c(i * 3 + k + 1, COLX[k] - 34, ROWY[i] - 16, r=9.0))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), row(0), row(1), callouts()]


def plate():
    return {
        "id": "fig-08-06-power-changes",
        "replaces": "fig-08-06-power-changes.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-08-06-power-changes.jpg",
        "caption": "Figure 8-6. The order of power changes: RPM up first, manifold pressure down first (an educational rule of thumb)",
        "desc": ("Figure 8-6. The order of power changes, an educational rule of thumb. To increase power: enrich as required, raise the RPM, then raise the manifold pressure. "
                 "To decrease power: reduce the manifold pressure, then the RPM, then lean as required."),
        "legend": [
            "To increase power, first enrich as required (the red mixture control).",
            "Then raise the RPM (the blue propeller control).",
            "Then raise the manifold pressure (the black throttle).",
            "To decrease power, first reduce the manifold pressure (the throttle).",
            "Then reduce the RPM (the propeller control).",
            "Then lean as required (the mixture control). In short: RPM up first, manifold pressure down first. High manifold pressure at low RPM raises cylinder pressures and invites detonation. This is a rule of thumb; your flight manual and its power tables take precedence.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
