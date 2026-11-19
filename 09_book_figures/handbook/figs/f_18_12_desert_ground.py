"""Figure 18-12 (new). Desert realities on the ground, from the last subsection of Chapter 18: three scenes, one for each point.

1 sand on the pavement (a taxiway with markings fading under drifted sand, a ridge of sand at the edge, an aeroplane taxiing slowly), 2 heat shimmer (a runway with wavering air over its far end, an aircraft there hard to see, an eye that looks longer),
3 dust and stones (an aeroplane at high power over loose sand throws up dust and stones; a nicked propeller blade and a clogged air filter as small icons). Shapes, colours and the numbers of the callouts; no words. The drawings are generic."""
import math
import random

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 210
U = "ar1812"
CELLS = ((10.0, 10.0, 200.0, 190.0), (220.0, 10.0, 200.0, 190.0), (430.0, 10.0, 200.0, 190.0))
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
HAZE = [(0.0, "#A8B8D2"), (0.5, "#DCD3BD"), (0.85, "#E8D2A2"), (1.0, "#E9D3A4")]
INK, RED, GREEN = "#334155", "#B91C1C", "#15803D"
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


def eye(cx, cy, s=1.0, col=GREEN):
    return (f'<path d="M{n(cx - 22 * s)} {n(cy)} Q{n(cx)} {n(cy - 22 * s)} {n(cx + 22 * s)} {n(cy)} Q{n(cx)} {n(cy + 22 * s)} {n(cx - 22 * s)} {n(cy)} Z" fill="#FFFFFF" stroke="{col}" stroke-width="3.2"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(8 * s)}" fill="{col}"/><circle cx="{n(cx - 2.6 * s)}" cy="{n(cy - 2.6 * s)}" r="{n(2.4 * s)}" fill="#FFFFFF"/>')


def scene_1():                                               # sand on the pavement
    x, y, w, h = CELLS[0]
    land = S.plain(f"{U}l1", x, x + w, y + 80, y + h, seed=4, tone="day", photo=True)
    pave = f'<path d="M{n(x)} {n(y + 96)} L{n(x + w)} {n(y + 90)} L{n(x + w)} {n(y + 152)} L{n(x)} {n(y + 160)} Z" fill="#6B7385"/>'
    marks = "".join(f'<rect x="{n(x + 18 + k * 36)}" y="{n(y + 118 - k * 1.2)}" width="22" height="3.6" rx="1.5" fill="#F1F5F9" fill-opacity="{n(0.95 - k * 0.15)}"/>' for k in range(5))
    drift = "".join(f'<ellipse cx="{n(x + cx)}" cy="{n(y + cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="#E4CE9A" fill-opacity="0.9"/>' for cx, cy, rx, ry in ((48, 124, 34, 7), (104, 130, 30, 6), (152, 120, 38, 8), (182, 142, 24, 6)))
    ridge = f'<path d="M{n(x)} {n(y + 160)} Q{n(x + 50)} {n(y + 148)} {n(x + 100)} {n(y + 156)} T{n(x + w)} {n(y + 150)} L{n(x + w)} {n(y + h)} L{n(x)} {n(y + h)} Z" fill="#DCC48E"/><path d="M{n(x)} {n(y + 160)} Q{n(x + 50)} {n(y + 148)} {n(x + 100)} {n(y + 156)} T{n(x + w)} {n(y + 150)}" fill="none" stroke="#F6EBCB" stroke-width="2"/>'
    slow = f'<path d="M{n(x + 136)} {n(y + 64)} H{n(x + 180)} M{n(x + 172)} {n(y + 58)} L{n(x + 180)} {n(y + 64)} L{n(x + 172)} {n(y + 70)}" fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.9"/>'
    return panel(0, DAY, land + pave + marks + drift + ridge + slow)


def scene_2():                                               # heat shimmer: the far end of a runway
    x, y, w, h = CELLS[1]
    land = S.plain(f"{U}l2", x, x + w, y + 84, y + h, seed=9, tone="dusk", photo=True)
    run = f'<path d="M{n(x + 80)} {n(y + 90)} L{n(x + 120)} {n(y + 90)} L{n(x + 188)} {n(y + h)} L{n(x + 12)} {n(y + h)} Z" fill="#5B6577"/><line x1="{n(x + 100)}" y1="{n(y + 92)}" x2="{n(x + 100)}" y2="{n(y + h)}" stroke="#F1F5F9" stroke-width="2" stroke-dasharray="8 8"/>'
    waves = "".join(f'<path d="M{n(x + 52 + k * 5)} {n(y + 96 + k * 9)} q 12 -7 24 0 t 24 0 t 24 0 t 24 0" fill="none" stroke="#FFFFFF" stroke-opacity="{n(0.7 - k * 0.12)}" stroke-width="2.4" stroke-linecap="round"/>' for k in range(5))
    return panel(1, HAZE, land + run + waves + eye(x + 160, y + 40, 0.9))


def scene_3():                                               # dust and stones
    x, y, w, h = CELLS[2]
    land = S.plain(f"{U}l3", x, x + w, y + 96, y + h, seed=3, tone="day", photo=True)
    dust = S.fog(f"{U}d3", x - 20, x + 130, y + 150, 80, seed=4, opacity=0.95, colour="#D8B672", wisp=1.0, foot=0.5, side_fade=0.3)
    rnd = random.Random(8)
    stones = "".join(f'<circle cx="{n(x + 70 + rnd.uniform(-14, 40))}" cy="{n(y + 136 + rnd.uniform(-20, 12))}" r="{n(rnd.uniform(1.6, 2.8))}" fill="#6B5B45" stroke="#FFFFFF" stroke-width="0.6"/>' for _ in range(14))
    blade = f'<path d="M{n(x + 150)} {n(y + 36)} L{n(x + 164)} {n(y + 36)} L{n(x + 170)} {n(y + 100)} L{n(x + 144)} {n(y + 100)} Z" fill="#CBD5E1" stroke="#475569" stroke-width="2"/><path d="M{n(x + 170)} {n(y + 60)} l-6 3 l6 3 M{n(x + 168)} {n(y + 76)} l-5 3 l5 3" fill="none" stroke="{RED}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    filt = f'<rect x="{n(x + 144)}" y="{n(y + 112)}" width="30" height="30" rx="4" fill="#E2E8F0" stroke="#475569" stroke-width="2"/>' + "".join(f'<circle cx="{n(x + 150 + (k % 3) * 9)}" cy="{n(y + 118 + (k // 3) * 9)}" r="2.4" fill="#92711A"/>' for k in range(9))
    return panel(2, DAY, land + dust + stones + blade + filt)


def sprites():
    o = lambda name, x, y, wd, **k: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **k}
    c = lambda i: CELLS[i][:2]
    return [o("sprite-side", c(0)[0] + 96, c(0)[1] + 98, 56), o("sprite-side", c(1)[0] + 104, c(1)[1] + 98, 26, opacity=0.4), o("sprite-side", c(2)[0] + 74, c(2)[1] + 110, 56, angle=-4.0)]


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(3))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="210" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-18-12-desert-ground",
        "replaces": "fig-18-12-desert-ground.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-18-12-desert-ground.jpg",
        "caption": "Figure 18-12. Desert realities on the ground: sand on the pavement, heat shimmer, dust and stones",
        "desc": ("Figure 18-12. Desert realities on the ground, three scenes: sand on the pavement hides markings and builds ridges at the edge, so taxi slowly; heat shimmer makes distant objects waver, so look longer before you enter a runway; "
                 "dust and stones picked up by the propeller nick its blades and clog the air filter."),
        "legend": [
            "Sand on the pavement hides markings, reduces braking and steering grip, and builds ridges at the pavement edge that can catch a wheel. Taxi slowly where markings are faint, and report sand on a runway or taxiway to ATC.",
            "Heat shimmer over hot pavement makes distant objects waver, and a mirage can look like water. An aircraft at the far end of a runway may be hard to see: look longer before you enter.",
            "Dust and stones picked up by the propeller nick its blades and clog the air filter. Run up on clean pavement, avoid high power over loose sand, and keep clear of other aircraft's slipstream.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
