"""Figure 26-10 (new). Saudi conditions at takeoff and landing, from the last section of Chapter 26: four scenes.

1 density altitude (Thumamah, elevation 1 870 ft, reference temperature 42 degrees, a density altitude of about 5 300 ft), 2 the shamal and its gusts (the runway 35 of Thumamah along 348 degrees from above, the wind from 318 degrees at 16 kt gusting 26 kt,
a crosswind of 8 kt and 13 kt in the gusts), 3 thermal turbulence and haze (the thermals over a hot plain; the runway looks further away in haze, so the aeroplane flies low: a dashed correct path and the lower one), 4 glare and sand (a low sun on final that
hides the runway, and sand blowing across it). Shapes, colours and the numbers of the callouts; the only text is the numbers and their units. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar26s"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def frame(i, body):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def side(i, seed, hz=100.0, stops=DAY, extra=""):
    x, y = PX[i], PY[i]
    return frame(i, S.sky(f"{U}k{i}", x, y, PW, PH, stops) + S.plain(f"{U}g{i}", x, x + PW, y + hz, y + PH, seed=seed, tone="day", acacias=((x + 28, y + 152, 0.9),), photo=True) + extra)


def pill(cx, cy, w, text, fill="#1F2937", h=11.0):
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2 - 3.5)}" width="{n(w)}" height="{n(h + 7)}" rx="{n((h + 7) / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, h, fill="#FFFFFF"))


def runway_side(x, y, y0=140.0):
    return f'<path d="M{n(x + 110)} {n(y + y0)} L{n(x + PW)} {n(y + y0)} L{n(x + PW)} {n(y + y0 + 14)} L{n(x + 100)} {n(y + y0 + 14)} Z" fill="#5B6577"/><line x1="{n(x + 120)}" y1="{n(y + y0 + 7)}" x2="{n(x + PW)}" y2="{n(y + y0 + 7)}" stroke="#F1F5F9" stroke-width="1.6" stroke-dasharray="9 7"/>'


def scene1():
    x, y = PX[0], PY[0]
    sun = S.glow(f"{U}sg1", x + 230, y + 34, 38, "#FFF2C4", 0.95) + f'<circle cx="{n(x + 230)}" cy="{n(y + 34)}" r="10" fill="#FFF7DC"/>'
    thermo = f'<rect x="{n(x + 268)}" y="{n(y + 62)}" width="10" height="40" rx="5" fill="#F8FAFC" stroke="{INK}" stroke-width="2"/><circle cx="{n(x + 273)}" cy="{n(y + 106)}" r="9" fill="{RED}" stroke="{INK}" stroke-width="2"/><rect x="{n(x + 271)}" y="{n(y + 76)}" width="4" height="30" fill="{RED}"/>'
    alt = (f'<line x1="{n(x + 40)}" y1="{n(y + 138)}" x2="{n(x + 40)}" y2="{n(y + 52)}" stroke="{INK}" stroke-width="2.4" stroke-dasharray="5 4"/>' + pill(x + 40, y + 42, 76.0, "5 300 FT") + pill(x + 40, y + 160, 76.0, "1 870 FT") + pill(x + 150, y + 160, 58.0, "42°C", "#B91C1C"))
    return side(0, 4, 104.0, extra=sun + thermo + runway_side(x, y, 120.0) + alt)


def scene2():
    x, y = PX[1], PY[1]
    cx = x + 150
    rw = f'<g transform="rotate(-12 {n(cx)} {n(y + 100)})"><rect x="{n(cx - 8)}" y="{n(y + 10)}" width="16" height="170" fill="#5B6577"/><line x1="{n(cx)}" y1="{n(y + 14)}" x2="{n(cx)}" y2="{n(y + 176)}" stroke="#F1F5F9" stroke-width="1.6" stroke-dasharray="9 7"/></g>'
    ground = f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="#E8D7AC"/>'
    w1 = S.ribbon(f"{U}w", [(x + 34, y + 40), (x + 70, y + 62), (x + 106, y + 84), (x + 130, y + 98)], 8.0, "#4B6FB5", "#A9C0E6", opacity=0.9, head=2.2, tail=0.4, per=8)
    w2 = S.ribbon(f"{U}w2", [(x + 24, y + 90), (x + 52, y + 106), (x + 80, y + 122), (x + 104, y + 134)], 6.0, "#4B6FB5", "#A9C0E6", opacity=0.6, head=2.2, tail=0.4, per=8)
    return frame(1, ground + rw + w1 + w2 + pill(x + 66, y + 28, 58.0, "16 KT") + pill(x + 220, y + 40, 58.0, "26 KT", "#B91C1C") + pill(x + 232, y + 120, 66.0, "8 KT") + pill(x + 232, y + 152, 66.0, "13 KT", "#B91C1C"))


def scene3():
    x, y = PX[2], PY[2]
    haze = S.fog(f"{U}h3", x + 100, x + PW, y + 140, 76, seed=5, opacity=0.9, colour="#E0C890", wisp=1.0, foot=0.3, side_fade=0.2)
    ok = S.ribbon(f"{U}o3", [(x + 24, y + 70), (x + 90, y + 88), (x + 160, y + 108), (x + 230, y + 126)], 4.0, "#2FA35A", "#9BE0B2", opacity=0.55, head=2.0, tail=0.4, per=8)
    low = S.ribbon(f"{U}l3", [(x + 24, y + 96), (x + 90, y + 112), (x + 160, y + 126), (x + 230, y + 134)], 4.6, "#E8782E", "#F6B36B", opacity=0.9, head=2.0, tail=0.4, per=8)
    th = "".join(S.ribbon(f"{U}t3{k}", [(x + 40 + 34 * k, y + 176), (x + 46 + 34 * k, y + 160), (x + 38 + 34 * k, y + 146), (x + 46 + 34 * k, y + 132)], 4.4, "#E8782E", "#F8BE73", opacity=0.55, head=2.0, tail=0.4, per=6) for k in range(3))
    return side(2, 9, 104.0, extra=runway_side(x, y, 140.0) + haze + th + ok + low)


def scene4():
    x, y = PX[3], PY[3]
    sun = S.glow(f"{U}g4", x + 214, y + 112, 96, "#FFF4D2", 0.98) + S.glow(f"{U}g4b", x + 214, y + 112, 44, "#FFFFFF", 0.95) + f'<circle cx="{n(x + 214)}" cy="{n(y + 112)}" r="11" fill="#FFFFFF"/>'
    sand = S.fog(f"{U}d4", x, x + PW, y + 174, 44, seed=7, opacity=0.9, colour="#D9B97A", wisp=1.1, foot=0.3, side_fade=0.1)
    return side(3, 12, 112.0, [(0.0, "#4A7FC4"), (0.5, "#9DC1EC"), (0.85, "#F6E8C0"), (1.0, "#F6E8C0")], runway_side(x, y, 140.0) + sun + sand)


def sprites():
    o = lambda x, y, w, angle=0.0, name="sprite-side": {"name": name, "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[0] + 168, PY[0] + 96, 56, 4.0), o(PX[1] + 150, PY[1] + 130, 40, -12.0, "sprite-top"), o(PX[2] + 140, PY[2] + 70, 56, 8.0), o(PX[3] + 120, PY[3] + 102, 56, 4.0)]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene1(), scene2(), scene3(), scene4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-26-10-saudi-conditions",
        "replaces": "fig-26-10-saudi-conditions.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-26-10-saudi-conditions.jpg",
        "caption": "Figure 26-10. Saudi conditions at takeoff and landing: density altitude, shamal and gusts, thermals and haze, glare and sand",
        "desc": ("Figure 26-10. Saudi conditions at takeoff and landing in four scenes: the density altitude of Thumamah (elevation 1 870 ft, reference temperature 42 degrees, about 5 300 ft); the shamal and its gusts on runway 35 (wind 318 degrees at 16 kt gusting 26 kt, "
                 "a crosswind of 8 kt and 13 kt in the gusts); thermal turbulence and haze, which makes the runway look further away so that you tend to fly low; and glare and sand."),
        "legend": [
            "Density altitude: at a high or hot aerodrome the roll is longer, the climb weaker and the groundspeed on final higher at the same indicated speeds. Thumamah prints an elevation of 1 870 ft and a reference temperature of 42 °C: the exact density altitude is about 5 300 ft (Figure 11-5).",
            "Shamal and gusts: the summer north-westerly blows almost continuously and peaks around midday, bringing crosswinds, gusts and dust. Runway 35 at Thumamah lies along 348°; with the wind 318° at 16 kt gusting 26 kt, the crosswind is 8 kt, 13 kt in the gusts.",
            "Thermal turbulence and haze: on hot afternoons, fly a power-on approach slightly above the normal speed. You see less along the slant than the reported visibility, and haze makes the runway look further away, so you tend to fly low.",
            "Glare and sand: a low sun on final can hide the runway and traffic; keep the windscreen clean, and go around if you lose the runway. Sand on the runway reduces braking and steering grip.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
