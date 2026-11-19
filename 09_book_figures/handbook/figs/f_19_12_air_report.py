"""Figure 19-12 (new). The illustrative air report of Chapter 19 read part by part: "Example Control, HZ-FGA, air report, 10 miles north of WADI at 0805, 4 500 feet, heavy dust storm ahead, visibility below 1 000 metres, turning back."

Above, the report as a scene (a tower at the left, the wadi, an aeroplane 10 miles north of it at 4 500 ft, a wall of dust ahead with visibility below 1 000 m, a turn back, the time as a clock); below, the same report as seven chips in the
order it is spoken, each with the colour of its part in the scene and a numbered callout: 1 who is called and who calls, 2 the words air report, 3 where, 4 when, 5 the level, 6 what is met, 7 what is done. The words in the picture are the example's own (Latin capitals and digits);
the explanations are in the legend. The example is made up, as the chapter says."""
import math

from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 326
U = "rt1910"
COL = {1: "#475569", 2: "#1D4ED8", 3: "#15803D", 4: "#B45309", 5: "#7C3AED", 6: "#B91C1C", 7: "#0F766E"}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SC = (10.0, 10.0, 620.0, 176.0)                              # the scene panel
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
PX, PY = 410.0, 66.0                                         # the aeroplane
GROUND = 138.0


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, colour, size=8.0):
    return M.chip(cx, cy, text, colour, size=size, anchor="middle")


def scene():
    x, y, w, h = SC
    uid = f"{U}s"
    body = S.sky(uid + "k", x, y, w, h, DAY) + S.plain(f"{U}l", x, x + w, y + 104, y + h, seed=5, tone="day", photo=True)
    # the tower (1)
    tower = (f'<rect x="{n(x + 34)}" y="{n(y + 84)}" width="9" height="40" rx="2" fill="#D4DAE4" stroke="{COL[1]}" stroke-width="1.4"/><path d="M{n(x + 24)} {n(y + 72)} H{n(x + 54)} L{n(x + 50)} {n(y + 84)} H{n(x + 28)} Z" fill="#8FB4E0" stroke="{COL[1]}" stroke-width="1.4"/>'
             f'<rect x="{n(x + 22)}" y="{n(y + 68)}" width="34" height="5" rx="2" fill="{COL[1]}"/>')
    arcs = "".join(f'<path d="M{n(x + 150 + k * 26)} {n(y + 66 - 10 - k * 5)} A {n(14 + k * 7)} {n(14 + k * 7)} 0 0 0 {n(x + 150 + k * 26)} {n(y + 66 + 10 + k * 5)}" fill="none" stroke="{COL[2]}" stroke-width="3" stroke-linecap="round" stroke-opacity="0.95"/>' for k in range(3))
    # the wadi (3)
    wadi = (f'<path d="M{n(x + 214)} {n(y + 112)} q 16 6 30 2 t 32 4 L{n(x + 270)} {n(y + 124)} q -16 4 -30 0 t -28 -2 Z" fill="#6F5B3E"/>' + pill(x + 246, y + 150, "WADI", COL[3]))
    dim = (f'<line x1="{n(x + 246)}" y1="{n(y + 128)}" x2="{n(PX - 10 + 0)}" y2="{n(y + 128)}" stroke="{COL[3]}" stroke-width="2.4" stroke-dasharray="6 4"/>'
           f'<path d="M{n(x + 254)} {n(y + 123)} L{n(x + 246)} {n(y + 128)} L{n(x + 254)} {n(y + 133)} M{n(PX - 18)} {n(y + 123)} L{n(PX - 10)} {n(y + 128)} L{n(PX - 18)} {n(y + 133)}" fill="none" stroke="{COL[3]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
           + pill((x + 246 + PX - 10) / 2, y + 128, "10 MILES", COL[3]))
    compass = (f'<path d="M{n(x + 560)} {n(y + 36)} H{n(x + 596)} M{n(x + 588)} {n(y + 30)} L{n(x + 596)} {n(y + 36)} L{n(x + 588)} {n(y + 42)}" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.9"/>' + H.glyph_text("N", x + 548, y + 36, 9.0, "#FFFFFF"))
    # the level (5)
    level = (f'<line x1="{n(PX + 6)}" y1="{n(PY + 30)}" x2="{n(PX + 6)}" y2="{n(y + 128)}" stroke="{COL[5]}" stroke-width="2.4" stroke-dasharray="5 4"/>'
             f'<line x1="{n(x + 300)}" y1="{n(PY + 30)}" x2="{n(PX + 60)}" y2="{n(PY + 30)}" stroke="{COL[5]}" stroke-width="1.6" stroke-dasharray="3 4" stroke-opacity="0.7"/>' + pill(PX - 36, PY + 52, "4 500 FEET", COL[5]))
    # the dust wall (6) and visibility
    dust = S.fog(f"{U}d", x + 470, x + w + 20, y + 148, 150, seed=4, opacity=0.96, colour="#D8B672", wisp=1.0, foot=0.5, side_fade=0.25) + pill(x + 560, y + 120, "<1 000 M", COL[6])
    # the clock (4)
    clock = (f'<circle cx="{n(x + 250)}" cy="{n(y + 34)}" r="17" fill="#FFFFFF" stroke="{COL[4]}" stroke-width="3"/><line x1="{n(x + 250)}" y1="{n(y + 34)}" x2="{n(x + 250)}" y2="{n(y + 23)}" stroke="{COL[4]}" stroke-width="2.6" stroke-linecap="round"/>'
             f'<line x1="{n(x + 250)}" y1="{n(y + 34)}" x2="{n(x + 258)}" y2="{n(y + 39)}" stroke="{COL[4]}" stroke-width="2.6" stroke-linecap="round"/>' + pill(x + 286, y + 34, "0805", COL[4]))
    # the turn back (7)
    turn = S.ribbon(f"{U}t", [(PX + 54, PY + 10), (PX + 100, PY - 2), (PX + 102, PY - 26), (PX + 60, PY - 34), (PX - 30, PY - 26)], 5.0, COL[7], "#5EC4B8", opacity=0.92, head=2.2, tail=0.4, per=8)
    clip = f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath><filter id="{uid}f" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
    return (clip + f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}f)"/><g clip-path="url(#{uid}c)">' + body + tower + arcs + wadi + dim + compass + level + dust + clock + turn
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


ROWS = (
    ((1, "EXAMPLE CONTROL, HZ–FGA"), (2, "AIR REPORT"), (3, "10 MILES NORTH OF WADI")),
    ((4, "AT 0805"), (5, "4 500 FEET")),
    ((6, "HEAVY DUST STORM AHEAD, VISIBILITY BELOW 1 000 METRES"), (7, "TURNING BACK")),
)


def chips():
    out = []
    size, hgt, gap = 8.4, 28.0, 9.0
    y0 = 200.0
    for r, row in enumerate(ROWS):
        widths = [gwidth(t, size, 0.4) + 50.0 for _, t in row]
        x = 12.0
        y = y0 + r * (hgt + 8.0)
        for (k, t), wd in zip(row, widths):
            c = COL[k]
            out.append(f'<defs><filter id="{U}cf{k}" x="-5%" y="-10%" width="110%" height="130%"><feDropShadow dx="0" dy="1.4" stdDeviation="1.6" flood-color="#10233F" flood-opacity="0.22"/></filter></defs>'
                       f'<rect x="{n(x)}" y="{n(y)}" width="{n(wd)}" height="{n(hgt)}" rx="{n(hgt / 2)}" fill="#FFFFFF" stroke="{c}" stroke-width="2.4" filter="url(#{U}cf{k})"/>'
                       + H.glyph_text(t, x + 36.0, y + hgt / 2, size, c, spacing=0.4, anchor="start"))
            out.append(S.callout(k, x + 15.0, y + hgt / 2, r=10.5))
            x += wd + gap
    return "".join(out)


def sprites():
    o = lambda name, x, y, wd, **k: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **k}
    return [o("sprite-side", PX, PY, 62)]


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="326" fill="#ffffff"/>', scene(), *sprites(), chips()]


def plate():
    return {
        "id": "fig-19-12-air-report",
        "replaces": "fig-19-12-air-report.svg",              # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-19-12-air-report.jpg",
        "caption": "Figure 19-12. The illustrative air report read part by part",
        "desc": ("Figure 19-12. The chapter's illustrative air report, in a scene and in seven chips in the order it is spoken: who is called and who calls, the words air report, where (10 miles north of WADI), when (0805), the level (4 500 feet), "
                 "what is met (a heavy dust storm ahead, visibility below 1 000 metres) and what is done (turning back)."),
        "legend": [
            "Who is called and who calls: the station, then your call sign.",
            "The words air report, so that the station knows what kind of message follows.",
            "Where: the position, here 10 miles north of a named point.",
            "When: the time of the observation, here 0805.",
            "The level: here 4 500 feet.",
            "What you met: here a heavy dust storm ahead and visibility below 1 000 metres.",
            "What you are doing: here turning back.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
