"""Figure 19-6 (new). The chapter's illustrative position report read part by part, and the periodic report: "Example Control, HZ-FGA, position, WADI at 0732, 4 500 feet, SABKA at 0751, aerodrome B next."

Above, the report as a scene (the aeroplane over WADI on the dashed route, SABKA and aerodrome B ahead, the level and the times); in the middle, the same report as five chips in the order it is spoken (1 identification with POSITION, 2 position and time,
3 level, 4 next position and time over, 5 ensuing waypoint); below, 6 the periodic report: a time line from the last contact at 0751, the window 20 to 40 minutes later (0811 to 0831) and the words OPERATIONS NORMAL.
The words in the picture are the example's own (Latin capitals and digits; the call sign's hyphen is drawn as a dash). The example is made up, as the chapter says."""
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 340
U = "rt1906"
COL = {1: "#475569", 2: "#15803D", 3: "#7C3AED", 4: "#B45309", 5: "#1D4ED8", 6: "#0F766E"}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SC = (10.0, 10.0, 620.0, 150.0)
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
WX = (120.0, 360.0, 560.0)                                   # WADI, SABKA, aerodrome B
RY = 118.0                                                   # the route on the ground
PY = 58.0                                                    # the aeroplane


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, colour, size=8.0):
    w = gwidth(text, size, 0.4) + 14.0
    h = size + 8.0
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4))


def point(x, y, col):
    return f'<path d="M{n(x)} {n(y - 9)} L{n(x + 8)} {n(y + 5)} L{n(x - 8)} {n(y + 5)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="1.6"/>'


def clock(cx, cy, col, h=7.5):
    import math
    a = math.radians(h * 30 - 90)
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="12" fill="#FFFFFF" stroke="{col}" stroke-width="2.4"/><line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(cy - 8)}" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + 6 * math.cos(a))}" y2="{n(cy + 6 * math.sin(a))}" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>')


def scene():
    x, y, w, h = SC
    uid = f"{U}s"
    body = S.sky(uid + "k", x, y, w, h, DAY) + S.plain(f"{U}l", x, x + w, y + 86, y + h, seed=8, tone="day")
    route = f'<line x1="{n(x + 40)}" y1="{n(RY)}" x2="{n(WX[2])}" y2="{n(RY)}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="9 6" stroke-opacity="0.95"/>'
    pts = point(WX[0], RY, COL[2]) + point(WX[1], RY, COL[4])
    rwy = f'<path d="M{n(WX[2] - 4)} {n(RY - 6)} L{n(WX[2] + 44)} {n(RY - 6)} L{n(WX[2] + 50)} {n(RY + 6)} L{n(WX[2] - 10)} {n(RY + 6)} Z" fill="#5B6577" stroke="#FFFFFF" stroke-width="1.2"/>'
    labels = pill(WX[0], RY + 22, "WADI", COL[2]) + pill(WX[1], RY + 22, "SABKA", COL[4]) + pill(WX[2] + 20, RY + 22, "B", COL[5])
    times = clock(WX[0] + 34, y + 22, COL[2]) + pill(WX[0] + 72, y + 22, "0732", COL[2]) + clock(WX[1] - 34, RY - 24, COL[4], h=7.85) + pill(WX[1] + 6, RY - 24, "0751", COL[4])
    level = (f'<line x1="{n(WX[0])}" y1="{n(PY + 16)}" x2="{n(WX[0])}" y2="{n(RY - 10)}" stroke="{COL[3]}" stroke-width="2.4" stroke-dasharray="5 4"/>' + pill(WX[0] - 46, (PY + RY) / 2 + 4, "4 500 FEET", COL[3]))
    nxt = S.ribbon(f"{U}r", [(WX[0] + 40, PY + 2), (WX[1] - 60, PY + 10), (WX[1] - 10, PY + 30)], 4.0, COL[4], "#F3B46B", opacity=0.9, head=2.2, tail=0.4, per=8)
    return ('<defs><clipPath id="' + uid + 'c"><rect x="' + n(x) + '" y="' + n(y) + '" width="' + n(w) + '" height="' + n(h) + '" rx="9"/></clipPath></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff"/><g clip-path="url(#{uid}c)">' + body + route + rwy + pts + nxt + level + labels + times
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


ROWS = (
    ((1, "EXAMPLE CONTROL, HZ–FGA, POSITION"), (2, "WADI AT 0732")),
    ((3, "4 500 FEET"), (4, "SABKA AT 0751"), (5, "AERODROME B NEXT")),
)


def chip(k, t, x, y, hgt=28.0, size=8.4):
    c = COL[k]
    wd = gwidth(t, size, 0.4) + 50.0
    return wd, (f'<defs><filter id="{U}cf{k}" x="-5%" y="-10%" width="110%" height="130%"><feDropShadow dx="0" dy="1.4" stdDeviation="1.6" flood-color="#10233F" flood-opacity="0.22"/></filter></defs>'
                f'<rect x="{n(x)}" y="{n(y)}" width="{n(wd)}" height="{n(hgt)}" rx="{n(hgt / 2)}" fill="#FFFFFF" stroke="{c}" stroke-width="2.4" filter="url(#{U}cf{k})"/>'
                + H.glyph_text(t, x + 36.0, y + hgt / 2, size, c, spacing=0.4, anchor="start") + S.callout(k, x + 15.0, y + hgt / 2, r=10.5))


def chips():
    out = []
    for r, row in enumerate(ROWS):
        x, y = 12.0, 172.0 + r * 36.0
        for k, t in row:
            wd, s = chip(k, t, x, y)
            out.append(s)
            x += wd + 9.0
    return "".join(out)


def periodic():
    x0, x1, y = 60.0, 600.0, 296.0
    k = (x1 - x0) / 50.0                                     # minutes 0 to 50 after the last contact
    out = (f'<rect x="12" y="250" width="616" height="80" rx="9" fill="#F1F5F9" stroke="#E2E8F0" stroke-width="1.4"/>'
           f'<line x1="{n(x0)}" y1="{n(y)}" x2="{n(x1)}" y2="{n(y)}" stroke="#94A3B8" stroke-width="3" stroke-linecap="round"/>'
           f'<rect x="{n(x0 + 20 * k)}" y="{n(y - 9)}" width="{n(20 * k)}" height="18" rx="4" fill="{COL[6]}" fill-opacity="0.85"/>')
    for m, t in ((0, "0751"), (20, "0811"), (40, "0831")):
        xx = x0 + m * k
        out += f'<line x1="{n(xx)}" y1="{n(y - 14)}" x2="{n(xx)}" y2="{n(y + 14)}" stroke="#334155" stroke-width="2"/>' + pill(xx, y + 24, t, "#334155" if m == 0 else COL[6], size=7.5)
    out += pill(x0 + 30 * k, y - 24, "OPERATIONS NORMAL", COL[6]) + S.callout(6, 30, 270, r=10.5)
    return out


def sprites():
    o = lambda name, x, y, wd, **kw: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **kw}
    return [o("sprite-side", WX[0], PY, 56)]


def layers():
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', scene(), *sprites(), chips(), periodic()]


def plate():
    return {
        "id": "fig-19-06-position-report",
        "replaces": "fig-19-06-position-report.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-19-06-position-report.jpg",
        "caption": "Figure 19-6. The illustrative position report read part by part, and the periodic report 20 to 40 minutes after the last contact",
        "desc": ("Figure 19-6. The chapter's illustrative position report, in a scene and in five chips in the order it is spoken: identification with the word position, WADI at 0732, 4 500 feet, SABKA at 0751, aerodrome B next. "
                 "Below, the periodic report: after the last contact at 0751, report between 0811 and 0831; with nothing else to say, operations normal."),
        "legend": [
            "Aircraft identification, with POSITION immediately before or after the call sign.",
            "Position and time in four digits: here WADI at 0732.",
            "Flight level or altitude: here 4 500 feet. With Mode C on, give the level to the nearest full 100 ft as the altimeter shows it.",
            "Next position and time over: here SABKA at 0751.",
            "The ensuing waypoint: here aerodrome B.",
            "Periodic report: 20 to 40 minutes after your last contact with the unit, here between 0811 and 0831 after 0751. If there is nothing else to say, report OPERATIONS NORMAL.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
