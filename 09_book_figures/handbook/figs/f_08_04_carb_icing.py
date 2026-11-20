"""Figure 8-4 (new). Carburettor icing: when to expect it, and what carburettor heat shows, from Chapter 8 ("Carburettor and induction icing"). Only the chapter's own
statements are drawn: ice is most likely below about 21 °C with relative humidity above 80 %, but it can form with outside air as warm as 38 °C and humidity as low as 50 %; with a
fixed-pitch propeller the sign is a gradual fall in RPM; with full carburettor heat and ice present the RPM falls further and the engine may run rougher while the ice melts, then
power recovers; with no ice the RPM falls and stays steady until the heat is removed.

Two cards. Left, outside air temperature against relative humidity: the wide block where ice can form (pale blue) and the block where it is most likely (deep blue, with ice
crystals); the two blocks are the chapter's two statements, not an icing-probability chart. Right, the tachometer against time (schematic): the trace with ice (blue) and the trace
with no ice (grey), and the moment full heat is applied (amber). Digits, °C and % on the figure; the words are in the legend (figs/marks.py)."""
import math

from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 300
INK, BLUE, DEEP, AMBER, GREY = "#1E293B", "#3B82F6", "#1D4ED8", "#B45309", "#64748B"
# left chart: temperature 0..40 °C on x, humidity 40..100 % on y
LX0, LX1, LY0, LY1 = 62.0, 290.0, 236.0, 42.0


def tx(t):
    return LX0 + (LX1 - LX0) * t / 40.0


def hy(h):
    return LY0 + (LY1 - LY0) * (h - 40.0) / 60.0


def card(uid, x, y, w, h):
    return (f'<defs><filter id="{uid}s" x="-6%" y="-8%" width="112%" height="122%"><feDropShadow dx="0" dy="2" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.22"/></filter>'
            f'{S.gradient(uid + "g", [(0, "#FFFFFF"), (1, "#F3F6FA")])}</defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="10" fill="url(#{uid}g)" filter="url(#{uid}s)"/>')


def crystal(cx, cy, r, col="#FFFFFF"):
    out = ""
    for k in range(3):
        a = math.radians(k * 60)
        dx, dy = r * math.cos(a), r * math.sin(a)
        out += f'<line x1="{n(cx - dx)}" y1="{n(cy - dy)}" x2="{n(cx + dx)}" y2="{n(cy + dy)}" stroke="{col}" stroke-width="1.5" stroke-linecap="round"/>'
    return out


def chart():
    out = [card("ci8a", 14, 14, 300, 272)]
    out.append(f'<defs>{S.gradient("ci8p", [(0, "#BFDBFE", 0.95), (1, "#DBEAFE", 0.75)], 0, 0, 1, 1)}{S.gradient("ci8d", [(0, "#1D4ED8"), (1, "#3B82F6")], 0, 0, 1, 1)}</defs>')
    # grid
    for t in (0, 10, 20, 30, 40):
        out.append(f'<line x1="{n(tx(t))}" y1="{n(LY0)}" x2="{n(tx(t))}" y2="{n(LY1)}" stroke="#E2E8F0" stroke-width="1"/>')
    for h in (40, 60, 80, 100):
        out.append(f'<line x1="{n(LX0)}" y1="{n(hy(h))}" x2="{n(LX1)}" y2="{n(hy(h))}" stroke="#E2E8F0" stroke-width="1"/>')
    # where ice can form (to 38 °C, from 50 %), where it is most likely (to 21 °C, from 80 %)
    out.append(f'<rect x="{n(LX0)}" y="{n(LY1)}" width="{n(tx(38) - LX0)}" height="{n(hy(50) - LY1)}" fill="url(#ci8p)" stroke="{BLUE}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    out.append(f'<rect x="{n(LX0)}" y="{n(LY1)}" width="{n(tx(21) - LX0)}" height="{n(hy(80) - LY1)}" fill="url(#ci8d)" stroke="#FFFFFF" stroke-width="1.6"/>')
    for cx, cy in ((84, 62), (112, 86), (146, 58), (132, 104), (92, 98), (164, 90)):
        out.append(crystal(cx, cy, 6))
    # axes
    out.append(f'<path d="M{n(LX0)} {n(LY1 - 8)} V{n(LY0)} H{n(LX1 + 8)}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    for t in (0, 10, 20, 30, 40):
        out.append(M.chip(tx(t), LY0 + 14, str(t), GREY, size=6.8))
    for h in (40, 60, 80, 100):
        out.append(M.chip(LX0 - 16, hy(h), str(h), GREY, size=6.8))
    out.append(M.chip(LX1 + 14, LY0 + 14, "°C", INK, size=7.6) + M.chip(LX0 - 16, LY1 - 18, "%", INK, size=8.0))
    # the four numbers of the text, on the edges of the blocks
    out.append(f'<line x1="{n(tx(21))}" y1="{n(hy(80))}" x2="{n(tx(21))}" y2="{n(LY0)}" stroke="{DEEP}" stroke-width="1.2" stroke-dasharray="2 3"/>'
               f'<line x1="{n(tx(38))}" y1="{n(hy(50))}" x2="{n(tx(38))}" y2="{n(LY0)}" stroke="{BLUE}" stroke-width="1.2" stroke-dasharray="2 3"/>')
    out.append(M.chip(tx(21), LY0 + 32, "21 °C", DEEP, size=8.4) + M.chip(tx(38) - 6, LY0 + 32, "38 °C", BLUE, size=8.4)
               + M.chip(tx(21) + 26, hy(80), "80 %", DEEP, size=8.4) + M.chip(tx(38) + 4, hy(50) + 14, "50 %", BLUE, size=8.4, anchor="end"))
    c = S.callout
    out.append(c(1, 124, 136, 118, 112, r=10) + c(2, 236, 96, 222, 120, r=10))
    return "".join(out)


def traces():
    """The tachometer against time: with ice (blue) and with no ice (grey); full heat applied at x = 430."""
    x0, x1, yb, yt = 348.0, 606.0, 236.0, 46.0
    out = [card("ci8b", 326, 14, 300, 272)]
    for k in range(5):
        y = yt + (yb - yt) * k / 4
        out.append(f'<line x1="{n(x0)}" y1="{n(y)}" x2="{n(x1)}" y2="{n(y)}" stroke="#E2E8F0" stroke-width="1"/>')
    xh, xr = 430.0, 560.0                                   # heat applied; heat removed (the trace with no ice)
    out.append(f'<rect x="{n(xh)}" y="{n(yt)}" width="{n(x1 - xh)}" height="{n(yb - yt)}" fill="#FDE9C8" opacity="0.5"/>'
               f'<line x1="{n(xh)}" y1="{n(yt - 6)}" x2="{n(xh)}" y2="{n(yb)}" stroke="{AMBER}" stroke-width="2"/>')
    # no ice: steady, a step down at the heat, steady, back up when the heat is removed
    no_ice = f"M {n(x0)} 84 L {n(xh)} 84 L {n(xh + 8)} 112 L {n(xr)} 112 L {n(xr + 8)} 84 L {n(x1)} 84"
    out.append(f'<path d="{no_ice}" fill="none" stroke="#FFFFFF" stroke-width="5"/><path d="{no_ice}" fill="none" stroke="{GREY}" stroke-width="2.4" stroke-linejoin="round"/>')
    # ice: a gradual fall, a further fall and rough running at the heat while the ice melts, then recovery above where it was
    pts = [(x0, 96.0)]
    for i in range(1, 21):
        pts.append((x0 + (xh - x0) * i / 20, 96 + 54 * (i / 20) ** 1.3))
    pts.append((xh + 8, 186.0))
    for i in range(1, 25):
        x = xh + 8 + 62 * i / 24
        pts.append((x, 188 + (7 if i % 2 else -7) * (1 - i / 30)))
    for i in range(1, 15):
        t = i / 14
        pts.append((xh + 70 + 42 * t, 188 - 80 * (t * t * (3 - 2 * t))))
    pts.append((x1, 108.0))
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in pts)
    out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="5.4" stroke-linejoin="round"/><path d="{d}" fill="none" stroke="{DEEP}" stroke-width="2.6" stroke-linejoin="round"/>')
    for cx, cy in ((372, 150), (404, 176)):
        out.append(crystal(cx, cy, 5, BLUE))
    out.append(f'<path d="M{n(x0)} {n(yt - 8)} V{n(yb)} H{n(x1 + 8)}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    out.append(M.chip(x0 + 2, yt - 18, "RPM", INK, size=8.0, anchor="start") + M.chip(x1 - 6, yb + 16, "MIN", INK, size=7.6, kind="clock"))
    c = S.callout
    out.append(c(3, 384, 196, 400, 138, r=10) + c(4, xh, 262, xh, 238, r=10) + c(5, 476, 216, 468, 194, r=10) + c(6, 506, 68, 500, 110, r=10))
    return "".join(out)


def layers():
    return [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', chart(), traces()]


def plate():
    return {
        "id": "fig-08-04-carb-icing",
        "replaces": "fig-08-04-carb-icing.svg",                 # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-08-04-carb-icing.jpg",
        "caption": "Figure 8-4. Carburettor icing: when to expect it, and what carburettor heat shows",
        "desc": ("Figure 8-4. Left, outside air temperature against relative humidity: ice is most likely below about 21 °C with humidity above 80%, and can form up to 38 °C and "
                 "down to 50% humidity. Right, the tachometer against time: with ice the RPM falls gradually, falls further and runs rough when full carburettor heat is applied, "
                 "then recovers; with no ice it falls and stays steady until the heat is removed."),
        "legend": [
            "Ice most likely: outside air below about 21 °C, relative humidity above 80%.",
            "Ice possible: outside air as warm as 38 °C, humidity as low as 50%.",
            "The sign with a fixed-pitch propeller: a gradual fall in RPM.",
            "Full carburettor heat applied.",
            "With ice: RPM falls further and the engine may run rougher while the ice melts; then power recovers. Leave the heat on.",
            "With no ice: RPM falls and stays steady until you remove the heat.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
