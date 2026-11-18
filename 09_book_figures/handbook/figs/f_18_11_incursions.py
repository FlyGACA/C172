"""Figure 18-11 (new). Preventing runway incursions, from the chapter's section of that name: six scenes, one for each of the five educational habits and for "line up and wait".

1 study the aerodrome chart and brief the route before starting the engine (a chart with a route), 2 write the taxi clearance down and read it back (notepad, pencil, a speech bubble), 3 a runway-holding position is a stop line (seen from above: an aeroplane stopped
at the double yellow lines before a runway, a stop sign), 4 look both ways along the runway and up the final approach, even when cleared (arrows both ways and an approaching aeroplane), 5 eyes outside while moving, checklists when stopped (an eye over the taxiing aeroplane, a crossed-out clipboard),
6 "line up and wait" is not a takeoff clearance (an aeroplane lined up on runway 27 with a landing aeroplane on final, the take-off arrow crossed out). Shapes, colours and the numbers of the callouts; the only text is the runway number 27. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "ar1811"
CELLS = ((10.0, 10.0, 200.0, 150.0), (220.0, 10.0, 200.0, 150.0), (430.0, 10.0, 200.0, 150.0), (10.0, 170.0, 200.0, 150.0), (220.0, 170.0, 200.0, 150.0), (430.0, 170.0, 200.0, 150.0))
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
INK, RED, GREEN, BLUE = "#334155", "#B91C1C", "#15803D", "#1D4ED8"
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SAND = [(0.0, "#EBDCB4"), (1.0, "#D5BC8B")]


def panel(i, sky_stops, body):
    x, y, w, h = CELLS[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, w, h, sky_stops) + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def cross(cx, cy, r=13.0, col=RED, w=5.0):
    return f'<path d="M{n(cx - r)} {n(cy - r)} L{n(cx + r)} {n(cy + r)} M{n(cx + r)} {n(cy - r)} L{n(cx - r)} {n(cy + r)}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def eye(cx, cy, s=1.0, col=GREEN):
    return (f'<path d="M{n(cx - 22 * s)} {n(cy)} Q{n(cx)} {n(cy - 22 * s)} {n(cx + 22 * s)} {n(cy)} Q{n(cx)} {n(cy + 22 * s)} {n(cx - 22 * s)} {n(cy)} Z" fill="#FFFFFF" stroke="{col}" stroke-width="3.2"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(8 * s)}" fill="{col}"/><circle cx="{n(cx - 2.6 * s)}" cy="{n(cy - 2.6 * s)}" r="{n(2.4 * s)}" fill="#FFFFFF"/>')


def scene_1():                                               # the chart and the route
    x, y, w, h = CELLS[0]
    sheet = f'<rect x="{n(x + 26)}" y="{n(y + 22)}" width="148" height="112" rx="5" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2"/>'
    run = f'<rect x="{n(x + 40)}" y="{n(y + 40)}" width="104" height="12" rx="2" fill="#5B6577"/><line x1="{n(x + 46)}" y1="{n(y + 46)}" x2="{n(x + 138)}" y2="{n(y + 46)}" stroke="#F1F5F9" stroke-width="1.3" stroke-dasharray="6 5"/>'
    taxi = f'<path d="M{n(x + 60)} {n(y + 52)} V{n(y + 100)} H{n(x + 140)}" fill="none" stroke="#8B93A5" stroke-width="7" stroke-linejoin="round"/><rect x="{n(x + 130)}" y="{n(y + 92)}" width="30" height="22" rx="3" fill="#CBD5E1" stroke="#8B93A5" stroke-width="1.4"/>'
    route = S.ribbon(f"{U}r1", [(x + 150, y + 104), (x + 100, y + 100), (x + 62, y + 98), (x + 60, y + 60)], 4.4, "#E8782E", "#F6B36B", opacity=0.95, head=2.2, tail=0.4, per=8)
    return panel(0, [(0.0, "#CFE0F5"), (1.0, "#F1F6FC")], sheet + run + taxi + route)


def scene_2():                                               # write it down, read it back
    x, y, w, h = CELLS[1]
    pad = f'<rect x="{n(x + 22)}" y="{n(y + 26)}" width="86" height="104" rx="6" fill="#FFFBEB" stroke="#B45309" stroke-width="2"/>' + "".join(f'<line x1="{n(x + 32)}" y1="{n(y + 46 + k * 16)}" x2="{n(x + 98)}" y2="{n(y + 46 + k * 16)}" stroke="#94A3B8" stroke-width="2"/>' for k in range(5)) + f'<path d="M{n(x + 34)} {n(y + 44)} q6 -8 10 0 t10 0 t10 0" fill="none" stroke="{INK}" stroke-width="2.2"/><path d="M{n(x + 34)} {n(y + 60)} q6 -8 10 0 t10 0 t10 0 t10 0" fill="none" stroke="{INK}" stroke-width="2.2"/>'
    pencil = f'<path d="M{n(x + 92)} {n(y + 112)} L{n(x + 128)} {n(y + 76)} l7 7 L{n(x + 99)} {n(y + 119)} Z" fill="#FACC15" stroke="#92400E" stroke-width="1.4"/><path d="M{n(x + 92)} {n(y + 112)} L{n(x + 99)} {n(y + 119)} L{n(x + 88)} {n(y + 123)} Z" fill="#F5D0A9" stroke="#92400E" stroke-width="1.2"/>'
    bubble = f'<path d="M{n(x + 120)} {n(y + 34)} h58 a8 8 0 0 1 8 8 v34 a8 8 0 0 1 -8 8 h-40 l-14 12 v-12 h-4 a8 8 0 0 1 -8 -8 v-34 a8 8 0 0 1 8 -8 Z" fill="#FFFFFF" stroke="{BLUE}" stroke-width="2.6"/>' + "".join(f'<line x1="{n(x + 128)}" y1="{n(y + 50 + k * 13)}" x2="{n(x + 128 + 40 - k * 6)}" y2="{n(y + 50 + k * 13)}" stroke="{BLUE}" stroke-width="3" stroke-linecap="round"/>' for k in range(3))
    return panel(1, [(0.0, "#CFE0F5"), (1.0, "#F1F6FC")], pad + pencil + bubble)


def scene_3():                                               # a holding position is a stop line (from above)
    x, y, w, h = CELLS[2]
    sand = f'<defs><linearGradient id="{U}g3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBDCB4"/><stop offset="1" stop-color="#D5BC8B"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{U}g3)"/>'
    run = f'<rect x="{n(x)}" y="{n(y + 14)}" width="{n(w)}" height="34" fill="#5B6577"/><line x1="{n(x + 8)}" y1="{n(y + 31)}" x2="{n(x + w - 8)}" y2="{n(y + 31)}" stroke="#F1F5F9" stroke-width="2" stroke-dasharray="10 8"/>'
    taxi = f'<rect x="{n(x + 70)}" y="{n(y + 48)}" width="40" height="{n(h - 48)}" fill="#8B93A5"/><line x1="{n(x + 90)}" y1="{n(y + 60)}" x2="{n(x + 90)}" y2="{n(y + h)}" stroke="#FACC15" stroke-width="2.4"/>'
    hold = f'<line x1="{n(x + 70)}" y1="{n(y + 64)}" x2="{n(x + 110)}" y2="{n(y + 64)}" stroke="#FACC15" stroke-width="3"/><line x1="{n(x + 70)}" y1="{n(y + 70)}" x2="{n(x + 110)}" y2="{n(y + 70)}" stroke="#FACC15" stroke-width="3"/><line x1="{n(x + 70)}" y1="{n(y + 76)}" x2="{n(x + 110)}" y2="{n(y + 76)}" stroke="#FACC15" stroke-width="3" stroke-dasharray="5 4"/><line x1="{n(x + 70)}" y1="{n(y + 82)}" x2="{n(x + 110)}" y2="{n(y + 82)}" stroke="#FACC15" stroke-width="3" stroke-dasharray="5 4"/>'
    stop = "M" + " L".join(f"{n(x + 156 + 17 * math.cos(math.radians(22.5 + 45 * k)))},{n(y + 96 + 17 * math.sin(math.radians(22.5 + 45 * k)))}" for k in range(8)) + " Z"
    sign = f'<path d="{stop}" fill="{RED}" stroke="#FFFFFF" stroke-width="2.4"/><rect x="{n(x + 148)}" y="{n(y + 94)}" width="16" height="4.6" rx="2" fill="#FFFFFF"/>'
    return panel(2, SAND, sand + run + taxi + hold + sign)


def scene_4():                                               # look both ways, and up the final approach
    x, y, w, h = CELLS[3]
    sand = f'<defs><linearGradient id="{U}g4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBDCB4"/><stop offset="1" stop-color="#D5BC8B"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{U}g4)"/>'
    run = f'<rect x="{n(x)}" y="{n(y + 60)}" width="{n(w)}" height="34" fill="#5B6577"/><line x1="{n(x + 8)}" y1="{n(y + 77)}" x2="{n(x + w - 8)}" y2="{n(y + 77)}" stroke="#F1F5F9" stroke-width="2" stroke-dasharray="10 8"/><rect x="{n(x + 88)}" y="{n(y + 94)}" width="22" height="{n(h - 94)}" fill="#8B93A5"/>'
    arrows = "".join(f'<path d="M{n(x + 100 + sgn * 14)} {n(y + 40)} H{n(x + 100 + sgn * 70)} M{n(x + 100 + sgn * 62)} {n(y + 33)} L{n(x + 100 + sgn * 70)} {n(y + 40)} L{n(x + 100 + sgn * 62)} {n(y + 47)}" fill="none" stroke="{BLUE}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>' for sgn in (-1, 1))
    path = f'<line x1="{n(x + 6)}" y1="{n(y + 77)}" x2="{n(x + 40)}" y2="{n(y + 77)}" stroke="{RED}" stroke-width="2.4" stroke-dasharray="5 4"/>'
    return panel(3, SAND, sand + run + arrows + path + eye(x + 100, y + 22, 0.8, BLUE))


def scene_5():                                               # eyes outside while moving, checklists when stopped
    x, y, w, h = CELLS[4]
    apron = S.plain(f"{U}l5", x, x + w, y + 96, y + h, seed=5, tone="day")
    strip = f'<rect x="{n(x)}" y="{n(y + 118)}" width="{n(w)}" height="22" fill="#6B7385"/><line x1="{n(x + 6)}" y1="{n(y + 129)}" x2="{n(x + w - 6)}" y2="{n(y + 129)}" stroke="#F1F5F9" stroke-width="1.6" stroke-dasharray="9 7"/>'
    clip = f'<rect x="{n(x + 144)}" y="{n(y + 30)}" width="40" height="52" rx="5" fill="#F8FAFC" stroke="{INK}" stroke-width="2.4"/><rect x="{n(x + 155)}" y="{n(y + 26)}" width="18" height="8" rx="3" fill="{INK}"/>' + "".join(f'<line x1="{n(x + 150)}" y1="{n(y + 46 + k * 10)}" x2="{n(x + 178)}" y2="{n(y + 46 + k * 10)}" stroke="#94A3B8" stroke-width="2"/>' for k in range(3)) + cross(x + 164, y + 56, 16)
    return panel(4, DAY, apron + strip + clip + eye(x + 60, y + 38, 1.0))


def scene_6():                                               # line up and wait is not a takeoff clearance
    x, y, w, h = CELLS[5]
    sand = f'<defs><linearGradient id="{U}g6" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBDCB4"/><stop offset="1" stop-color="#D5BC8B"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{U}g6)"/>'
    run = f'<rect x="{n(x)}" y="{n(y + 54)}" width="{n(w)}" height="42" fill="#5B6577"/><line x1="{n(x + 8)}" y1="{n(y + 75)}" x2="{n(x + w - 24)}" y2="{n(y + 75)}" stroke="#F1F5F9" stroke-width="2" stroke-dasharray="10 8"/>' + H.glyph_text("27", x + 188, y + 75, 9.0, "#F8FAFC", rotate=-90.0, anchor="middle")
    final = ""
    go = f'<path d="M{n(x + 150)} {n(y + 118)} H{n(x + 30)} M{n(x + 40)} {n(y + 111)} L{n(x + 30)} {n(y + 118)} L{n(x + 40)} {n(y + 125)}" fill="none" stroke="{INK}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>' + cross(x + 90, y + 118, 15)
    return panel(5, SAND, sand + run + go)


def sprites():
    o = lambda name, x, y, wd, **k: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **k}
    c = lambda i: CELLS[i][:2]
    return [o("sprite-side", c(1)[0] + 148, c(1)[1] + 120, 40), o("sprite-top", c(2)[0] + 90, c(2)[1] + 112, 36, angle=0.0), o("sprite-top", c(3)[0] + 100, c(3)[1] + 118, 34, angle=0.0), o("sprite-top", c(3)[0] + 32, c(3)[1] + 77, 26, angle=90.0),
            o("sprite-side", c(4)[0] + 78, c(4)[1] + 96, 58), o("sprite-top", c(5)[0] + 70, c(5)[1] + 75, 38, angle=-90.0), o("sprite-top", c(5)[0] + 150, c(5)[1] + 75, 26, angle=-90.0)]


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(6))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="330" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), scene_5(), scene_6(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-18-11-incursions",
        "replaces": "fig-18-11-incursions.svg",             # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-18-11-incursions.jpg",
        "caption": "Figure 18-11. Preventing runway incursions: five habits, and a line-up that is not a takeoff clearance",
        "desc": ("Figure 18-11. Preventing runway incursions, six scenes: study the aerodrome chart and brief the route; write the taxi clearance down and read it back in full; treat every runway-holding position as a stop line; "
                 "look both ways along the runway and up the final approach, even when cleared; keep your eyes outside while moving and do checklists when stopped; and \"line up and wait\" is not a takeoff clearance."),
        "legend": [
            "Before starting the engine, study the aerodrome chart and brief your expected route.",
            "Write down the taxi clearance and read it back in full; if any part is unclear, ask.",
            "Treat every runway-holding position as a stop line until a clearance names that runway.",
            "Before entering or crossing a runway, look both ways along it and up the final approach, even when cleared.",
            "Keep your eyes outside while moving; do checklists when stopped.",
            "\"Line up and wait\" lets you enter the runway and line up, but it is not a takeoff clearance. While you wait you sit where landing aircraft touch down; if the wait grows long, ask the tower.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
