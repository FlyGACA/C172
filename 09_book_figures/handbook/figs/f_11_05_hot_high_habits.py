"""Figure 11-5 (new). Planning a hot-and-high flight, from the last subsection group of Chapter 11: six scenes, one for each habit.

1 depart early (the sun's arc: a cool low morning sun, the high afternoon sun, the sunset that ends the VFR day), 2 reduce mass (a weight icon, +10% on the mass gives +21% on the takeoff distance, a bag taken off the aeroplane), 3 lean for best power where the AFM allows
(a mixture knob pulled back, an engine speed dial at its highest), 4 the point to abandon the takeoff (the runway from above, a flag at the halfway point and the 70% of lift-off speed to reach there), 5 climb out and the way back (rising ground ahead, a turn back toward lower ground and the aerodrome),
6 landing (a stable approach at the normal speed; +10% speed gives +21% landing distance). Shapes, colours and the numbers of the callouts; the only text is +10%, +21% and 70%, from the chapter. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "ar115"
CELLS = ((10.0, 10.0, 200.0, 150.0), (220.0, 10.0, 200.0, 150.0), (430.0, 10.0, 200.0, 150.0), (10.0, 170.0, 200.0, 150.0), (220.0, 170.0, 200.0, 150.0), (430.0, 170.0, 200.0, 150.0))
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
INK, RED, GREEN, BLUE, AMBER = "#334155", "#B91C1C", "#15803D", "#1D4ED8", "#B45309"
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}


def panel(i, sky_stops, body):
    x, y, w, h = CELLS[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, w, h, sky_stops) + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def pill(cx, cy, text, fill="#1F2937", size=9.0):
    g = H._GLYPHS
    w = sum((size * 0.38 if c == " " else g["glyphs"][c]["advance"] * size / g["cap_height"]) + 0.4 for c in text) + 14.0
    h = size + 7.0
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4))


def strip_runway(x0, x1, y, h=10.0):
    return f'<rect x="{n(x0)}" y="{n(y)}" width="{n(x1 - x0)}" height="{n(h)}" rx="2" fill="#5B6577"/><line x1="{n(x0 + 6)}" y1="{n(y + h / 2)}" x2="{n(x1 - 6)}" y2="{n(y + h / 2)}" stroke="#F1F5F9" stroke-width="1.3" stroke-dasharray="8 6"/>'


def scene_1():                                               # the sun's arc: morning, afternoon, sunset
    x, y, w, h = CELLS[0]
    arc = f'<path d="M{n(x + 26)} {n(y + 92)} Q{n(x + 100)} {n(y - 40)} {n(x + 176)} {n(y + 92)}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="5 5" stroke-opacity="0.85"/>'
    morning = S.glow(f"{U}m1", x + 26, y + 92, 20, "#FFF4D2", 0.55) + f'<circle cx="{n(x + 26)}" cy="{n(y + 92)}" r="7" fill="#EAF3FF" stroke="#9CC0EA" stroke-width="1.5"/>'
    noon = S.sun(f"{U}n1", x + 100, y + 28, 11)
    sunset = S.glow(f"{U}u1", x + 176, y + 92, 26, "#FFB347", 0.9) + f'<circle cx="{n(x + 176)}" cy="{n(y + 92)}" r="8" fill="#F28C28"/>'
    return panel(0, DAY, S.plain(f"{U}l1", x, x + w, y + 98, y + h, seed=4, tone="day") + strip_runway(x + 12, x + 150, y + 124) + arc + morning + noon + sunset)


def scene_2():                                               # reduce mass: +10% on mass, +21% on the takeoff distance
    x, y, w, h = CELLS[1]
    weight = f'<path d="M{n(x + 24)} {n(y + 100)} L{n(x + 34)} {n(y + 78)} H{n(x + 62)} L{n(x + 72)} {n(y + 100)} Z" fill="#475569" stroke="#FFFFFF" stroke-width="1.6"/><circle cx="{n(x + 48)}" cy="{n(y + 74)}" r="6" fill="none" stroke="#475569" stroke-width="3"/>'
    bag = (f'<rect x="{n(x + 150)}" y="{n(y + 92)}" width="26" height="20" rx="3" fill="#C2410C" stroke="#FFFFFF" stroke-width="1.5"/><path d="M{n(x + 157)} {n(y + 92)} v-5 h12 v5" fill="none" stroke="#7C2D12" stroke-width="2"/>'
           f'<path d="M{n(x + 150)} {n(y + 66)} l24 -18 M{n(x + 166)} {n(y + 46)} h10 v10" fill="none" stroke="{RED}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
    bars = (f'<rect x="{n(x + 20)}" y="{n(y + 124)}" width="64" height="8" rx="3" fill="#6B7A93"/><rect x="{n(x + 20)}" y="{n(y + 136)}" width="78" height="8" rx="3" fill="{RED}"/>')
    return panel(1, DAY, S.plain(f"{U}l2", x, x + w, y + 108, y + h, seed=7, tone="day") + weight + bag + bars + pill(x + 48, y + 56, "+10%", RED) + pill(x + 146, y + 134, "+21%", RED))


def scene_3():                                               # lean: the mixture knob pulled back, the speed dial at its highest
    x, y, w, h = CELLS[2]
    base = f'<defs><linearGradient id="{U}g3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4B5563"/><stop offset="1" stop-color="#1F2937"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{U}g3)"/>'
    dial = f'<circle cx="{n(x + 56)}" cy="{n(y + 78)}" r="36" fill="#111827" stroke="#E2E8F0" stroke-width="4"/>' + "".join(f'<line x1="{n(x + 56 + 31 * math.cos(math.radians(a)))}" y1="{n(y + 78 - 31 * math.sin(math.radians(a)))}" x2="{n(x + 56 + 27 * math.cos(math.radians(a)))}" y2="{n(y + 78 - 27 * math.sin(math.radians(a)))}" stroke="#F8FAFC" stroke-width="2"/>' for a in range(210, -40, -30)) + f'<path d="M{n(x + 56)} {n(y + 78)} L{n(x + 56 + 28 * math.cos(math.radians(-8)))} {n(y + 78 - 28 * math.sin(math.radians(-8)))}" stroke="#F87171" stroke-width="3.2" stroke-linecap="round"/><circle cx="{n(x + 56)}" cy="{n(y + 78)}" r="4" fill="#E2E8F0"/>'
    knob = (f'<rect x="{n(x + 118)}" y="{n(y + 46)}" width="62" height="64" rx="6" fill="#374151" stroke="#9CA3AF" stroke-width="1.6"/><rect x="{n(x + 144)}" y="{n(y + 62)}" width="10" height="46" rx="3" fill="#9CA3AF"/><circle cx="{n(x + 149)}" cy="{n(y + 52)}" r="15" fill="#DC2626" stroke="#FFFFFF" stroke-width="2.2"/>'
            f'<path d="M{n(x + 149)} {n(y + 130)} V{n(y + 110)} M{n(x + 142)} {n(y + 118)} L{n(x + 149)} {n(y + 110)} L{n(x + 156)} {n(y + 118)}" fill="none" stroke="#FBBF24" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return panel(2, [(0.0, "#4B5563"), (1.0, "#1F2937")], base + dial + knob)


def scene_4():                                               # the abort point: the runway from above, a flag at the halfway point, 70%
    x, y, w, h = CELLS[3]
    sand = f'<defs><linearGradient id="{U}g4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBDCB4"/><stop offset="1" stop-color="#D5BC8B"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{U}g4)"/>'
    run = f'<rect x="{n(x + 8)}" y="{n(y + 66)}" width="{n(w - 16)}" height="26" rx="3" fill="#5B6577"/><line x1="{n(x + 18)}" y1="{n(y + 79)}" x2="{n(x + w - 18)}" y2="{n(y + 79)}" stroke="#F1F5F9" stroke-width="2" stroke-dasharray="10 8"/>'
    mid = f'<line x1="{n(x + 100)}" y1="{n(y + 58)}" x2="{n(x + 100)}" y2="{n(y + 100)}" stroke="#F8FAFC" stroke-width="2.6"/><line x1="{n(x + 100)}" y1="{n(y + 58)}" x2="{n(x + 100)}" y2="{n(y + 42)}" stroke="#7C2D12" stroke-width="2.4"/><path d="M{n(x + 100)} {n(y + 42)} l18 6 l-18 6 Z" fill="{RED}"/>'
    arrow = f'<path d="M{n(x + 40)} {n(y + 116)} H{n(x + 100)} M{n(x + 92)} {n(y + 110)} L{n(x + 100)} {n(y + 116)} L{n(x + 92)} {n(y + 122)}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    return panel(3, [(0.0, "#EBDCB4"), (1.0, "#D5BC8B")], sand + run + mid + arrow + pill(x + 140, y + 116, "70%", INK))


def scene_5():                                               # climb out and the way back: rising ground ahead, a turn toward lower ground
    x, y, w, h = CELLS[4]
    hill = f'<path d="M{n(x + 96)} {n(y + h)} L{n(x + 96)} {n(y + 118)} C{n(x + 130)} {n(y + 108)} {n(x + 160)} {n(y + 70)} {n(x + w + 4)} {n(y + 50)} L{n(x + w + 4)} {n(y + h)} Z" fill="#9A8768"/>'
    runway = strip_runway(x + 10, x + 90, y + 122)
    turn = S.ribbon(f"{U}t5", [(x + 100, y + 46), (x + 74, y + 32), (x + 56, y + 52), (x + 76, y + 80), (x + 34, y + 108)], 4.6, "#E8782E", "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=8)
    return panel(4, DAY, S.plain(f"{U}l5", x, x + w, y + 112, y + h, seed=9, tone="day") + hill + runway + turn)


def scene_6():                                               # landing: a stable approach; +10% on the speed, +21% on the distance
    x, y, w, h = CELLS[5]
    run = strip_runway(x + 14, x + 186, y + 112, 12.0)
    d1 = f'<rect x="{n(x + 40)}" y="{n(y + 126)}" width="78" height="8" rx="3" fill="#6B7A93"/><rect x="{n(x + 40)}" y="{n(y + 137)}" width="94" height="8" rx="3" fill="{RED}"/>'
    path = f'<line x1="{n(x + 20)}" y1="{n(y + 30)}" x2="{n(x + 50)}" y2="{n(y + 112)}" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="5 5" stroke-opacity="0.9"/>'
    return panel(5, DAY, S.plain(f"{U}l6", x, x + w, y + 104, y + h, seed=3, tone="day") + run + path + d1 + pill(x + 122, y + 40, "+10%", RED) + pill(x + 164, y + 133, "+21%", RED))


def sprites():
    o = lambda name, x, y, wd, **k: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **k}
    c = lambda i: CELLS[i][:2]
    return [o("sprite-side", c(0)[0] + 66, c(0)[1] + 112, 40), o("sprite-side", c(1)[0] + 110, c(1)[1] + 84, 52), o("sprite-top", c(3)[0] + 40, c(3)[1] + 79, 36), o("sprite-side", c(4)[0] + 128, c(4)[1] + 44, 48, angle=-8.0), o("sprite-side", c(5)[0] + 62, c(5)[1] + 84, 52, angle=6.0)]


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(6))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="330" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), scene_5(), scene_6(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-11-05-hot-high-habits",
        "replaces": "fig-11-05-hot-high-habits.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-11-05-hot-high-habits.jpg",
        "caption": "Figure 11-5. Planning a hot-and-high flight: depart early, reduce mass, lean, an abort point, the climb out and the landing",
        "desc": ("Figure 11-5. Planning a hot-and-high flight, six scenes: depart early, before the afternoon heat and the sunset; reduce mass, because 10% more mass means at least 21% more takeoff distance; lean for best power where the AFM allows; "
                 "a point on the runway to abandon the takeoff, with about 70% of lift-off speed by the halfway point; the climb out, with a turn back toward lower ground; and a stable landing at the normal speed, since 10% too fast adds about 21% to the landing distance."),
        "legend": [
            "Depart early: density altitude is lowest in the cool of the morning and highest in the afternoon, and the VFR day ends at sunset.",
            "Reduce mass: 10% more takeoff mass means at least 21% more takeoff distance, and a weaker climb. Leave behind baggage, a passenger or fuel you do not need, but never fuel the flight needs.",
            "Lean for best power where the AFM allows: at a high density altitude a full-rich mixture can be too rich for the thin air. Do it only where your AFM allows it and by its method.",
            "Plan the point to abandon the takeoff: choose a point along the runway by which the aeroplane should be airborne, and stop if you reach it still on the ground. One check pilots use: about 70% of the lift-off speed by the halfway point.",
            "Climb out, and the way back: fly the AFM climb speed, and if the aeroplane will not climb as planned and the terrain ahead rises, turn toward lower ground or back to the aerodrome while you still have room.",
            "Landing hot and high: fly the normal indicated approach speeds; 10% too fast adds about 21% to the landing distance. A go-around climbs as poorly as a takeoff, so fly a stable approach and decide early.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
