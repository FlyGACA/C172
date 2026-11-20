"""Figure 20-8 (new). The fuel for the example route of Chapter 20 ("Fuel and the reserve"), from the chapter's own table: taxi and run-up 4 L, trip A to B 62 L, contingency 7 L
(10 % of the trip fuel, rounded up), alternate B to C 8 L, final reserve 15 L (30 min at 30 L/h, by day): 96 L required, 150 L loaded (full tanks); and below, the GACAR minimum for a VFR flight
by day, the fuel to B and then 30 minutes at normal cruising speed (§91.161): 62 + 15 = 77 L at takeoff, 81 L at engine start.

Two bars of litres to the same scale (150 L = 560 units): above, the plan, cut into its five parts, and the rest of the full tanks pale; below, the minimum, the trip and the reserve only, under the
same trip. Digits and L; the words are in the legend. The numbers are those of the chapter; the labels are written on the figure (figs/marks.py)."""
from figs import h_b2 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 270
U = "nv20f"
INK, BLUE, GREEN, AMBER, RED, GREY, TEAL, VIOLET = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#94A3B8", "#0F766E", "#7C3AED"
X0, X1 = 40.0, 600.0
K = (X1 - X0) / 150.0                                       # units per litre
Y1, Y2, BH = 74.0, 182.0, 40.0
PLAN = [(4, GREY, "4"), (62, "#2563EB", "62"), (7, "#0D9488", "7"), (8, "#8B5CF6", "8"), (15, "#F59E0B", "15")]


def segments(parts, x, y):
    out, spans = [], []
    for litres, col, label in parts:
        w = litres * K
        out.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(BH)}" fill="{col}"/><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(BH * 0.36)}" fill="#FFFFFF" fill-opacity="0.22"/>'
                   f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(x)}" y2="{n(y + BH)}" stroke="#FFFFFF" stroke-width="1.6"/>')
        out.append(H.glyph_text(label, x + w / 2, y + BH / 2 + 0.5, 13.0 if w > 24 else 10.0, fill="#FFFFFF"))
        spans.append((x, w))
        x += w
    return "".join(out), spans, x


def bar(uid, y, parts, start, full):
    """A bar of litres: the parts from `start`, in a white track `full` litres long from X0, with a soft shadow."""
    body, spans, end = segments(parts, start, y)
    tw = full * K
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(X0)}" y="{n(y)}" width="{n(tw)}" height="{n(BH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-5%" y="-20%" width="110%" height="150%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#10233F" flood-opacity="0.24"/></filter>'
            f'<pattern id="{uid}h" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="7" height="7" fill="#F1F5F9"/><line x1="0" y1="0" x2="0" y2="7" stroke="#CBD5E1" stroke-width="2.2"/></pattern></defs>'
            f'<rect x="{n(X0)}" y="{n(y)}" width="{n(tw)}" height="{n(BH)}" rx="9" fill="url(#{uid}h)" filter="url(#{uid}s)"/><g clip-path="url(#{uid}c)">' + body + '</g>'
            f'<rect x="{n(X0)}" y="{n(y)}" width="{n(tw)}" height="{n(BH)}" rx="9" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>'), spans, end


def bracket(xa, xb, y, up=True, col=INK):
    d = -1 if up else 1
    return f'<path d="M{n(xa)} {n(y)} L{n(xa)} {n(y + 8 * d)} L{n(xb)} {n(y + 8 * d)} L{n(xb)} {n(y)}" fill="none" stroke="{col}" stroke-width="1.8" stroke-linejoin="round"/>'


def layers():
    plan, spans, end = bar(f"{U}p", Y1, PLAN, X0, 150)
    trip_x = spans[1][0]
    minimum, mspans, mend = bar(f"{U}m", Y2, [(62, "#2563EB", "62"), (15, "#F59E0B", "15")], trip_x, 81)
    out = [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', plan, minimum]
    # above the plan: 96 L required, 150 L loaded
    out.append(bracket(X0, end, Y1 - 6) + M.chip((X0 + end) / 2, Y1 - 26, "96 L", INK, size=10.0))
    out.append(bracket(X0, X1, Y1 + BH + 6, up=False, col=GREY) + M.chip((X0 + X1) / 2 + 150, Y1 + BH + 26, "150 L", INK, size=10.0))
    # below: the minimum, 77 L at takeoff and 81 L at engine start (with the taxi fuel)
    out.append(f'<rect x="{n(X0)}" y="{n(Y2)}" width="{n(4 * K)}" height="{n(BH)}" fill="{GREY}" fill-opacity="0.45"/>' + H.glyph_text("4", X0 + 2 * K, Y2 + BH / 2, 10.0, fill="#FFFFFF"))
    out.append(bracket(trip_x, mend, Y2 + BH + 6, up=False, col=RED) + M.chip((trip_x + mend) / 2, Y2 + BH + 26, "77 L", RED, size=10.0))
    out.append(bracket(X0, mend, Y2 - 6, col=GREY) + M.chip((X0 + mend) / 2, Y2 - 26, "81 L", INK, size=9.0))
    out.append(f'<line x1="{n(trip_x)}" y1="{n(Y1 + BH)}" x2="{n(trip_x)}" y2="{n(Y2)}" stroke="{GREY}" stroke-width="1" stroke-dasharray="3 3"/>')
    c = S.callout
    (sx0, sw0), (sx1, sw1), (sx2, sw2), (sx3, sw3), (sx4, sw4) = spans
    out.append(c(1, sx0 - 4, Y1 - 50, sx0 + sw0 / 2, Y1 + 4, r=10)
               + c(2, sx1 + sw1 * 0.5, Y1 - 50, sx1 + sw1 * 0.5, Y1 + 4, r=10)
               + c(3, sx2 + sw2 / 2 + 6, Y1 - 50, sx2 + sw2 / 2, Y1 + 4, r=10)
               + c(4, sx3 + sw3 / 2 + 22, Y1 - 50, sx3 + sw3 / 2, Y1 + 4, r=10)
               + c(5, sx4 + sw4 / 2 + 38, Y1 - 50, sx4 + sw4 / 2, Y1 + 4, r=10)
               + c(6, end + 22, Y1 - 26, end + 2, Y1 - 12, r=10)
               + c(7, X1 - 18, Y1 + BH + 26, X1 - 30, Y1 + BH, r=10)
               + c(8, mend + 26, Y2 + BH + 26, mend + 2, Y2 + BH + 12, r=10))
    return out


def plate():
    return {
        "id": "fig-20-08-fuel-plan",
        "replaces": "fig-20-08-fuel-plan.svg",                # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-20-08-fuel-plan.jpg",
        "caption": "Figure 20-8. The fuel for the example route: what the plan carries, and the GACAR minimum",
        "desc": ("Figure 20-8. The fuel for the example route A to B, as bars of litres to the same scale. Above, the plan: taxi and run-up 4 L, trip 62 L, contingency 7 L, alternate 8 L and "
                 "final reserve 15 L, 96 L required, with 150 L loaded in full tanks. Below, the GACAR minimum for a VFR flight by day: the trip and 30 minutes, 77 L at takeoff, 81 L at engine start."),
        "legend": [
            "Taxi and run-up: 4 L (example AFM).",
            "Trip, A to B: 62 L, from the navigation log.",
            "Contingency: 10% of the trip fuel, rounded up: 7 L (a rule of thumb).",
            "Alternate, B to C: 8 L, from the navigation log (a rule of thumb).",
            "Final reserve: 30 min at 30 L/h, by day: 15 L.",
            "Required by the plan: 96 L.",
            "Loaded: full tanks, 150 L.",
            "The GACAR minimum for a VFR flight by day: the fuel to B and then 30 minutes at normal cruising speed (section 91.161): 62 + 15 = 77 L at takeoff, 81 L at engine start.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
