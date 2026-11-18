"""Figure 15-9 (new). Reporting what you meet, from the last section of Chapter 15 (section 91.251): five panels.

1 moderate or severe turbulence and icing (a tossed aeroplane with jagged arrows and snowflakes), 2 severe mountain wave and thunderstorms (waves over a ridge, a storm cloud with lightning), 3 a heavy dust storm or sandstorm and a volcanic ash cloud
(a tan wall, a cone with a plume), 4 how the report goes: from the aeroplane by data link or by voice to the nearest air traffic services unit, without delay (a tower, a clock), 5 what the report says: what, where, at what level, when,
in what type of aircraft (five cards of symbols). Shapes, colours and the numbers of the callouts; no words. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar159"
CELLS = ((10.0, 10.0, 200.0, 190.0), (220.0, 10.0, 200.0, 190.0), (430.0, 10.0, 200.0, 190.0), (10.0, 210.0, 305.0, 184.0), (325.0, 210.0, 305.0, 184.0))
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
STORM = [(0.0, "#46557A"), (0.5, "#7A89AB"), (0.9, "#B7C1D6"), (1.0, "#C9CFDB")]
DUST = [(0.0, "#9FB4D4"), (0.5, "#D9D2C0"), (0.8, "#E6CFA0"), (1.0, "#E9D3A4")]
INK, RED = "#334155", "#B91C1C"
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


def arrow(uid, pts, width=4.5):
    return S.ribbon(uid, pts, width, "#E8782E", "#F6B36B", opacity=0.93, head=2.0, tail=0.4, per=8)


def scene_1():                                               # turbulence (jagged arrows) and icing (snowflakes)
    x, y, w, h = CELLS[0]
    zig = S.ribbon(f"{U}z1", [(x + 14, y + 118), (x + 40, y + 96), (x + 52, y + 124), (x + 84, y + 90), (x + 100, y + 120), (x + 132, y + 92)], 4.0, "#B91C1C", "#E57373", opacity=0.9, head=2.0, tail=0.4, per=4)
    snow = "".join(S.snowflake(x + sx, y + sy, r) for sx, sy, r in ((150, 60, 9.0), (172, 100, 7.0), (140, 132, 8.0), (176, 150, 6.0), (30, 52, 6.0)))
    return panel(0, DAY, S.plain(f"{U}l0", x, x + w, y + 150, y + h, seed=3, tone="day") + zig + snow)


def scene_2():                                               # waves over a ridge, a storm cloud with lightning
    x, y, w, h = CELLS[1]
    ridge = (f'<defs><linearGradient id="{U}rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9A8768"/><stop offset="1" stop-color="#5E503F"/></linearGradient></defs>'
             f'<path d="M{n(x - 4)} {n(y + h)} L{n(x - 4)} {n(y + 128)} C{n(x + 24)} {n(y + 112)} {n(x + 44)} {n(y + 96)} {n(x + 66)} {n(y + 98)} C{n(x + 92)} {n(y + 100)} {n(x + 104)} {n(y + 140)} {n(x + 146)} {n(y + 158)} L{n(x + w + 4)} {n(y + 160)} L{n(x + w + 4)} {n(y + h)} Z" fill="url(#{U}rg)"/>')
    waves = "".join(f'<path d="M{n(x + 50)} {n(y + 64 + k * 12)} q 14 -14 28 0 t 28 0 t 28 0" fill="none" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="2.2" stroke-linecap="round"/>' for k in range(3))
    return panel(1, STORM, S.plain(f"{U}l2", x, x + w, y + 158, y + h, seed=9, tone="storm") + ridge + waves + S.lightning(f"{U}t2", x + 156, y + 96, y + 156, seed=3))


def scene_3():                                               # a dust wall, a volcano and its plume
    x, y, w, h = CELLS[2]
    cone = f'<path d="M{n(x + 124)} {n(y + 168)} L{n(x + 148)} {n(y + 114)} L{n(x + 160)} {n(y + 114)} L{n(x + 188)} {n(y + 168)} Z" fill="#5B4B40"/><path d="M{n(x + 146)} {n(y + 114)} L{n(x + 162)} {n(y + 114)} L{n(x + 158)} {n(y + 120)} L{n(x + 150)} {n(y + 120)} Z" fill="#D9552B"/>'
    plume = "".join(f'<circle cx="{n(x + 154 + dx)}" cy="{n(y + 108 - dy)}" r="{n(r)}" fill="#4A4A55" fill-opacity="{n(o)}"/>' for dx, dy, r, o in ((0, 0, 11, 0.9), (-4, 18, 14, 0.85), (8, 38, 17, 0.8), (-6, 58, 20, 0.7), (6, 76, 22, 0.55)))
    return panel(2, DUST, S.plain(f"{U}l3", x, x + w, y + 120, y + h, seed=9, tone="dusk") + S.fog(f"{U}h3", x - 20, x + 130, y + 176, 118, seed=4, opacity=0.95, colour="#D8B672", wisp=1.0, foot=0.5, side_fade=0.35) + cone + plume)


def scene_4():                                               # aeroplane, voice arcs and a data-link zigzag, a tower, a clock
    x, y, w, h = CELLS[3]
    plain = S.plain(f"{U}l4", x, x + w, y + 126, y + h, seed=12, tone="day")
    tower = (f'<rect x="{n(x + 246)}" y="{n(y + 108)}" width="9" height="36" rx="2" fill="#D4DAE4" stroke="#6B7A93" stroke-width="1"/><path d="M{n(x + 236)} {n(y + 96)} H{n(x + 266)} L{n(x + 262)} {n(y + 108)} H{n(x + 240)} Z" fill="#8FB4E0" stroke="#4B6A97" stroke-width="1.2"/>'
             f'<rect x="{n(x + 234)}" y="{n(y + 92)}" width="34" height="5" rx="2" fill="#6B7A93"/><line x1="{n(x + 251)}" y1="{n(y + 92)}" x2="{n(x + 251)}" y2="{n(y + 78)}" stroke="#6B7A93" stroke-width="2"/>')
    arcs = "".join(f'<path d="M{n(x + 118 + k * 22)} {n(y + 56 - 12 - k * 6)} A {n(16 + k * 9)} {n(16 + k * 9)} 0 0 1 {n(x + 118 + k * 22)} {n(y + 56 + 12 + k * 6)}" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-opacity="0.9"/>' for k in range(3))
    data = f'<path d="M{n(x + 70)} {n(y + 112)} h26 v-10 h26 v10 h26 v-10 h26 v10 h26 v-10 h6" fill="none" stroke="#1D4ED8" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1 0"/>'
    clock = (f'<circle cx="{n(x + 276)}" cy="{n(y + 30)}" r="15" fill="#FFFFFF" stroke="{INK}" stroke-width="2.2"/><line x1="{n(x + 276)}" y1="{n(y + 30)}" x2="{n(x + 276)}" y2="{n(y + 20)}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
             f'<line x1="{n(x + 276)}" y1="{n(y + 30)}" x2="{n(x + 283)}" y2="{n(y + 35)}" stroke="{RED}" stroke-width="2.4" stroke-linecap="round"/>')
    return panel(3, DAY, plain + tower + arcs + data + clock)


def card(x, y, w, h, body):
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#FFFFFF" fill-opacity="0.95" stroke="#C3CCDA" stroke-width="1.2"/>' + body


def scene_5():                                               # five cards: what, where, level, when, type
    x, y, w, h = CELLS[4]
    cw, gap, cy0, ch = 52.0, 8.0, y + 54.0, 96.0
    x0 = x + (w - (5 * cw + 4 * gap)) / 2
    cards = []
    for k in range(5):
        cx = x0 + k * (cw + gap) + cw / 2
        cards.append(card(x0 + k * (cw + gap), cy0, cw, ch, ""))
        my = cy0 + ch / 2
        if k == 0:                                           # what: a warning triangle
            cards.append(f'<path d="M{n(cx)} {n(my - 22)} L{n(cx + 24)} {n(my + 18)} L{n(cx - 24)} {n(my + 18)} Z" fill="#F6C84C" stroke="{RED}" stroke-width="3" stroke-linejoin="round"/>'
                         f'<line x1="{n(cx)}" y1="{n(my - 8)}" x2="{n(cx)}" y2="{n(my + 5)}" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/><circle cx="{n(cx)}" cy="{n(my + 11.5)}" r="2" fill="{INK}"/>')
        elif k == 1:                                         # where: a map pin
            cards.append(f'<path d="M{n(cx)} {n(my + 24)} C{n(cx - 22)} {n(my - 2)} {n(cx - 20)} {n(my - 26)} {n(cx)} {n(my - 26)} C{n(cx + 20)} {n(my - 26)} {n(cx + 22)} {n(my - 2)} {n(cx)} {n(my + 24)} Z" fill="#DC2626" stroke="#FFFFFF" stroke-width="2"/><circle cx="{n(cx)}" cy="{n(my - 11)}" r="6" fill="#FFFFFF"/>')
        elif k == 2:                                         # level: a vertical double arrow between two lines
            cards.append(f'<line x1="{n(cx - 18)}" y1="{n(my - 24)}" x2="{n(cx + 18)}" y2="{n(my - 24)}" stroke="#6B7A93" stroke-width="2.4" stroke-dasharray="4 3"/><line x1="{n(cx - 18)}" y1="{n(my + 24)}" x2="{n(cx + 18)}" y2="{n(my + 24)}" stroke="#6B7A93" stroke-width="2.4" stroke-dasharray="4 3"/>'
                         f'<path d="M{n(cx)} {n(my - 20)} L{n(cx)} {n(my + 20)}" stroke="#1D4ED8" stroke-width="3" stroke-linecap="round"/><path d="M{n(cx - 7)} {n(my - 12)} L{n(cx)} {n(my - 21)} L{n(cx + 7)} {n(my - 12)} M{n(cx - 7)} {n(my + 12)} L{n(cx)} {n(my + 21)} L{n(cx + 7)} {n(my + 12)}" fill="none" stroke="#1D4ED8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        elif k == 3:                                         # when: a clock
            cards.append(f'<circle cx="{n(cx)}" cy="{n(my)}" r="24" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/><line x1="{n(cx)}" y1="{n(my)}" x2="{n(cx)}" y2="{n(my - 15)}" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/><line x1="{n(cx)}" y1="{n(my)}" x2="{n(cx + 11)}" y2="{n(my + 7)}" stroke="{RED}" stroke-width="3.2" stroke-linecap="round"/>'
                         + "".join(f'<line x1="{n(cx + 20 * math.sin(a))}" y1="{n(my - 20 * math.cos(a))}" x2="{n(cx + 23 * math.sin(a))}" y2="{n(my - 23 * math.cos(a))}" stroke="{INK}" stroke-width="2"/>' for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)))
    sprite = {"name": "sprite-top", "at": [x0 + 4 * (cw + gap) + cw / 2, cy0 + ch / 2], "width": 44, "outline": OUT, "shadow": SHADOW}
    return panel(4, DAY, S.plain(f"{U}l5", x, x + w, y + 168, y + h, seed=2, tone="day") + "".join(cards)), sprite


def sprites(extra):
    x0, y0 = CELLS[0][0], CELLS[0][1]
    x3, y3 = CELLS[3][0], CELLS[3][1]
    x1, y1 = CELLS[1][0], CELLS[1][1]
    o = lambda name, x, y, wd, **k: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **k}
    return [o("sprite-side", x0 + 82, y0 + 64, 70, angle=9.0), o("cloud-cb", x1 + 150, y1 + 80, 100), o("sprite-side", x3 + 62, y3 + 66, 62), extra]


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(5))


def layers():
    s5, sp5 = scene_5()
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), s5, *sprites(sp5), callouts()]


def plate():
    return {
        "id": "fig-15-09-reporting",
        "replaces": "fig-15-09-reporting.svg",              # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-15-09-reporting.jpg",
        "caption": "Figure 15-9. Reporting what you meet: which conditions, how the report goes and what it says",
        "desc": ("Figure 15-9. Reporting what you meet, five panels: moderate or severe turbulence and icing; severe mountain wave and thunderstorms; a heavy dust storm or sandstorm and a volcanic ash cloud; "
                 "the report goes by data link or by voice to the nearest air traffic services unit without delay; and what it says, five cards: what, where, at what level, when and in what type of aircraft."),
        "legend": [
            "Report moderate or severe turbulence and moderate or severe icing when you encounter or observe them.",
            "Report severe mountain wave, and thunderstorms, with or without hail, that are obscured, embedded, widespread or in squall lines.",
            "Report a heavy dust storm or heavy sandstorm, and a volcanic ash cloud or volcanic activity; and any other condition that, in your opinion, may affect the safety of other aircraft.",
            "The report goes by air–ground data link where available, or by voice, to the nearest air traffic services unit without delay, as an air report.",
            "Say what you met, where, at what level, when, and in what type of aircraft.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
