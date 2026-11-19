"""Figure 22-10 (new). Collision avoidance in Saudi conditions, from the last section of Chapter 22: five scenes, one for each point of its list.

Drawn in the style of the weather figures (figs/scene.py: sky, plain, fog, ribbons; the aeroplane and the cloud sprites laid by reskin.py): 1 busy training aerodromes (a circuit with three trainers round a runway),
2 mixed traffic (a large jet and a trainer behind it, with the wake of the jet as two spirals), 3 haze and dust (a distant aeroplane faint in a hazy layer), 4 sun (a bright sun low ahead, with its glare, and an aeroplane
lost in it), 5 night (a moon and an aeroplane with its position lights). Shapes, colours and the numbers of the callouts. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "ar22"
CELLS = ((10.0, 10.0, 200.0, 150.0), (220.0, 10.0, 200.0, 150.0), (430.0, 10.0, 200.0, 150.0), (10.0, 170.0, 305.0, 150.0), (325.0, 170.0, 305.0, 150.0))
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
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


def plane(x, y, width, angle=0.0, opacity=None, flip=False, tint=None):
    o = {"name": "sprite-side", "at": [x, y], "width": width, "outline": OUT, "shadow": SHADOW}
    if angle:
        o["angle"] = angle
    if opacity is not None:
        o["opacity"] = opacity
    if flip:
        o["flip"] = True
    if tint:
        o["tint"] = tint
        o["tint_strength"] = 0.5
    return o


def scene_1():                                               # a busy aerodrome: the runway and a circuit
    x, y, w, h = CELLS[0]
    strip = f'<path d="M{n(x + 20)} {n(y + 124)} L{n(x + w - 20)} {n(y + 124)} L{n(x + w - 6)} {n(y + 142)} L{n(x + 6)} {n(y + 142)} Z" fill="#5B6577"/><line x1="{n(x + 34)}" y1="{n(y + 133)}" x2="{n(x + w - 34)}" y2="{n(y + 133)}" stroke="#F1F5F9" stroke-width="1.6" stroke-dasharray="9 7"/>'
    circuit = S.ribbon(f"{U}c1", [(x + 150, y + 118), (x + 188, y + 96), (x + 176, y + 60), (x + 100, y + 52), (x + 30, y + 70)], 4.0, "#E8782E", "#F6B36B", opacity=0.55, head=2.0, tail=0.4, per=8)
    return panel(0, DAY, S.plain(f"{U}l0", x, x + w, y + 80, y + h, seed=4, tone="day", houses=((x + 170, y + 90, 0.8),), acacias=((x + 20, y + 112, 0.8),), photo=True) + strip + circuit)


def scene_2():                                               # a large aeroplane, the wake behind it, a trainer behind and below
    x, y, w, h = CELLS[1]
    wake = "".join(S.ribbon(f"{U}k{k}", [(x + 100, y + 56 + dy), (x + 74, y + 54 + dy), (x + 50, y + 62 + dy), (x + 26, y + 58 + dy)], 5.0, "#7C8FB5", "#C7D2E8", opacity=0.55, head=0.5, tail=1.0, per=8) for k, dy in enumerate((8, 22)))
    return panel(1, DAY, S.plain(f"{U}l1", x, x + w, y + 98, y + h, seed=7, tone="day", acacias=((x + 30, y + 130, 0.8),), photo=True) + wake)


def scene_3():                                               # haze and dust: a distant aeroplane faint in a tan layer
    x, y, w, h = CELLS[2]
    return panel(2, [(0.0, "#9FB4D4"), (0.5, "#D9D2C0"), (0.8, "#E6CFA0"), (1.0, "#E9D3A4")],
                 S.plain(f"{U}l2", x, x + w, y + 74, y + h, seed=9, tone="dusk", acacias=((x + 40, y + 124, 1.0),), photo=True)
                 + S.fog(f"{U}h2", x, x + w, y + 110, 80, seed=5, opacity=0.95, colour="#E0C890", wisp=1.0, foot=0.4))


def scene_4():                                               # the sun: low and bright ahead, an aeroplane lost in its glare
    x, y, w, h = CELLS[3]
    sun = S.glow(f"{U}g3", x + 210, y + 78, 96, "#FFF4D2", 0.98) + S.glow(f"{U}g3b", x + 210, y + 78, 44, "#FFFFFF", 0.95) + f'<circle cx="{n(x + 210)}" cy="{n(y + 78)}" r="11" fill="#FFFFFF"/>'
    return panel(3, [(0.0, "#4A7FC4"), (0.5, "#9DC1EC"), (0.85, "#F6E8C0"), (1.0, "#F6E8C0")], S.plain(f"{U}l3", x, x + w, y + 92, y + h, seed=3, tone="day", photo=True) + sun)


def scene_5():                                               # night: a moon, stars, and an aeroplane with its lights
    x, y, w, h = CELLS[4]
    stars = "".join(f'<circle cx="{n(x + sx)}" cy="{n(y + sy)}" r="{r}" fill="#FFFFFF" opacity="{o}"/>' for sx, sy, r, o in
                    [(30, 28, 1.0, 0.9), (70, 54, 0.8, 0.7), (110, 20, 1.2, 0.95), (160, 62, 0.8, 0.7), (205, 30, 1.0, 0.9), (250, 54, 0.8, 0.8), (285, 24, 1.0, 0.9), (60, 96, 0.8, 0.6), (240, 98, 0.8, 0.6), (140, 100, 0.7, 0.5)])
    moon = (S.glow(f"{U}mg", x + 252, y + 40, 34, "#FFF1C8", 0.55) + f'<circle cx="{n(x + 252)}" cy="{n(y + 40)}" r="10" fill="#F7EBC2"/>'
)
    return panel(4, [(0.0, "#0F1E3E"), (0.55, "#2B3A6B"), (0.9, "#4C5F95"), (1.0, "#5E6F9F")], S.plain(f"{U}l4", x, x + w, y + 108, y + h, seed=12, tone="storm", photo=True) + stars + moon)


def sprites():
    x0, y0 = CELLS[0][0], CELLS[0][1]
    x1, y1 = CELLS[1][0], CELLS[1][1]
    x2, y2 = CELLS[2][0], CELLS[2][1]
    x3, y3 = CELLS[3][0], CELLS[3][1]
    x4, y4 = CELLS[4][0], CELLS[4][1]
    return [plane(x0 + 60, y0 + 48, 34, angle=-4.0), plane(x0 + 168, y0 + 84, 34, angle=10.0), plane(x0 + 108, y0 + 112, 38, angle=3.0),
            plane(x1 + 124, y1 + 52, 98, tint="#5B7FC8"), plane(x1 + 62, y1 + 98, 38),
            plane(x2 + 118, y2 + 58, 40, opacity=0.5), plane(x2 + 60, y2 + 98, 22, opacity=0.22),
            plane(x3 + 120, y3 + 80, 40, opacity=0.35),
            plane(x4 + 152, y4 + 82, 60, angle=-3.0, opacity=0.9)]


def lights():
    x4, y4 = CELLS[4][0], CELLS[4][1]
    return (S.glow(f"{U}r5", x4 + 150, y4 + 72, 14, "#FF5A4A", 0.95) + S.glow(f"{U}gr5", x4 + 166, y4 + 86, 12, "#5AE08A", 0.9) + S.glow(f"{U}w5", x4 + 126, y4 + 72, 14, "#FFFFFF", 0.95)
            + f'<circle cx="{n(x4 + 150)}" cy="{n(y4 + 72)}" r="2.2" fill="#FFD0C8"/><circle cx="{n(x4 + 166)}" cy="{n(y4 + 86)}" r="1.8" fill="#D6FFE4"/><circle cx="{n(x4 + 126)}" cy="{n(y4 + 72)}" r="2.2" fill="#FFFFFF"/>')


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(5))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="330" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), scene_5(), *sprites(), lights(), callouts()]


def plate():
    return {
        "id": "fig-22-10-saudi-conditions",
        "replaces": "fig-22-10-saudi-conditions.svg",      # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-22-10-saudi-conditions.jpg",
        "caption": "Figure 22-10. Collision avoidance in Saudi conditions: five things to allow for",
        "desc": ("Figure 22-10. Collision avoidance in Saudi conditions, five tiles: busy training aerodromes, mixed traffic with large jets and their wake, haze and dust, the sun, and night."),
        "legend": [
            "Busy training aerodromes: several trainers can share one circuit and the nearby training areas. Expect traffic at your height, listen to every call and clear before every manoeuvre.",
            "Mixed traffic: at major aerodromes a trainer may share the circuit, runway or nearby airspace with large jets, with higher closing speeds and wake behind every movement. Joining and leaving procedures are in the aerodrome's AIP entry and your school's local orders.",
            "Haze and dust lower a distant aircraft's contrast against the sky, so you see it later, and you see less along a slant than the reported visibility suggests. Over featureless desert or above a haze layer, guard against empty-field myopia.",
            "Sun: a high, bright sun and windscreen glare hide traffic. Keep the windscreen clean.",
            "Night: night lessons are flown only under an authorization or local conditions (section 91.171), with position and anticollision lights on.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
