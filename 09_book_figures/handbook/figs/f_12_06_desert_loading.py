"""Figure 12-6 (new). Desert flights and hot days, from the last section of Chapter 12: four scenes.

Drawn in the style of the other illustrated figures (figs/scene.py: sky, plain, ribbons, sun; the aeroplane sprites laid by reskin.py): 1 water and survival equipment (a jerrycan of water and a kit beside the baggage hold, 1 L = about 1 KG, the 45 KG baggage limit),
2 long distances (full tanks, and fewer people in the four seats), 3 heat and elevation (the sun, a mountain and the aeroplane at 1 100 KG, the maximum mass of the example tables of Chapter 11; the cooler morning as the way out), 4 the same useful load
that all of them draw on (one bar of 340 KG, cut into three parts). Digits, KG, L and the equals sign; the words are in the legend. The numbers are those of the chapter. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 404
U = "ar12d"
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


def side(i, seed, hz=100.0, extra=""):
    x, y = PX[i], PY[i]
    return frame(i, S.sky(f"{U}k{i}", x, y, PW, PH, DAY) + S.plain(f"{U}g{i}", x, x + PW, y + hz, y + PH, seed=seed, tone="day", acacias=((x + 30, y + 156, 0.9),), photo=True) + extra)


def pill(cx, cy, w, text, fill="#1F2937", h=12.0):
    return M.chip(cx, cy, text, fill, size=h * 0.8, min_w=w)


def jerrycan(cx, cy, s=1.0, col="#2563EB"):
    w, h = 34 * s, 44 * s
    return (f'<path d="M{n(cx - w / 2)} {n(cy + h / 2)} L{n(cx - w / 2)} {n(cy - h / 2 + 8 * s)} L{n(cx - w / 2 + 10 * s)} {n(cy - h / 2)} L{n(cx + w / 2)} {n(cy - h / 2)} L{n(cx + w / 2)} {n(cy + h / 2)} Z" fill="{col}" stroke="#1E3A8A" stroke-width="1.8" stroke-linejoin="round"/>'
            f'<rect x="{n(cx - 8 * s)}" y="{n(cy - h / 2 - 6 * s)}" width="{n(16 * s)}" height="{n(7 * s)}" rx="2" fill="#1E3A8A"/>'
            f'<path d="M{n(cx - 6 * s)} {n(cy + 2 * s)} q{n(6 * s)} {n(-10 * s)} {n(12 * s)} 0 q{n(-6 * s)} {n(10 * s)} {n(-12 * s)} 0 Z" fill="#BFDBFE"/>')


def kit(cx, cy, s=1.0):
    w, h = 44 * s, 32 * s
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(5 * s)}" fill="#EA580C" stroke="#9A3412" stroke-width="1.8"/>'
            f'<rect x="{n(cx - 10 * s)}" y="{n(cy - h / 2 - 7 * s)}" width="{n(20 * s)}" height="{n(8 * s)}" rx="3" fill="none" stroke="#9A3412" stroke-width="2.2"/>'
            f'<path d="M{n(cx - 4 * s)} {n(cy - 8 * s)} h{n(8 * s)} v{n(6 * s)} h{n(6 * s)} v{n(8 * s)} h{n(-6 * s)} v{n(6 * s)} h{n(-8 * s)} v{n(-6 * s)} h{n(-6 * s)} v{n(-8 * s)} h{n(6 * s)} Z" fill="#FFFFFF"/>')


def seat(cx, cy, filled, s=1.0):
    col = "#2563EB" if filled else "none"
    st = "#1E3A8A" if filled else "#94A3B8"
    dash = "" if filled else ' stroke-dasharray="4 3"'
    return (f'<circle cx="{n(cx)}" cy="{n(cy - 13 * s)}" r="{n(8 * s)}" fill="{col}" stroke="{st}" stroke-width="2"{dash}/>'
            f'<path d="M{n(cx - 15 * s)} {n(cy + 14 * s)} Q{n(cx - 15 * s)} {n(cy - 2 * s)} {n(cx)} {n(cy - 3 * s)} Q{n(cx + 15 * s)} {n(cy - 2 * s)} {n(cx + 15 * s)} {n(cy + 14 * s)} Z" fill="{col}" stroke="{st}" stroke-width="2"{dash}/>')


def scene_1():                                               # water and a kit, the baggage limit
    x, y = PX[0], PY[0]
    hold = (f'<rect x="{n(x + 150)}" y="{n(y + 78)}" width="130" height="64" rx="6" fill="#CBD5E1" stroke="{INK}" stroke-width="2.2"/>'
            f'<rect x="{n(x + 160)}" y="{n(y + 88)}" width="110" height="44" rx="4" fill="#E2E8F0" stroke="#94A3B8" stroke-width="1.4"/>')
    return side(0, 4, 96.0, hold + jerrycan(x + 186, y + 112, 1.0) + jerrycan(x + 216, y + 114, 1.0) + kit(x + 252, y + 118, 0.9)
                + pill(x + 215, y + 64, 64.0, "45 KG") + jerrycan(x + 60, y + 128, 1.4) + pill(x + 60, y + 78, 84.0, "1 L = 1 KG"))


def scene_2():                                               # long distances: full tanks, fewer people
    x, y = PX[1], PY[1]
    route = S.ribbon(f"{U}r", [(x + 14, y + 120), (x + 90, y + 98), (x + 180, y + 96), (x + 290, y + 70)], 4.4, "#2FA35A", "#9BE0B2", opacity=0.6, head=2.0, tail=0.5, per=8)
    tank = (f'<rect x="{n(x + 30)}" y="{n(y + 128)}" width="70" height="40" rx="10" fill="#FEF3C7" stroke="#B45309" stroke-width="2.2"/><rect x="{n(x + 33)}" y="{n(y + 131)}" width="64" height="34" rx="8" fill="#F59E0B"/>'
            f'<path d="M{n(x + 62)} {n(y + 138)} q9 12 0 20 q-9 -8 0 -20 Z" fill="#FFFFFF"/>')
    seats = "".join(seat(x + 140 + k * 36, y + 150, k < 2, 0.9) for k in range(4))
    return side(1, 7, 90.0, route + tank + seats)


def scene_3():                                               # heat and elevation
    x, y = PX[2], PY[2]
    sun = S.glow(f"{U}sg", x + 240, y + 36, 40, "#FFF2C4", 0.95) + f'<circle cx="{n(x + 240)}" cy="{n(y + 36)}" r="11" fill="#FFF7DC"/>'
    thermo = (f'<rect x="{n(x + 276)}" y="{n(y + 76)}" width="10" height="42" rx="5" fill="#F8FAFC" stroke="{INK}" stroke-width="2"/><circle cx="{n(x + 281)}" cy="{n(y + 122)}" r="9" fill="{RED}" stroke="{INK}" stroke-width="2"/>'
              f'<rect x="{n(x + 279)}" y="{n(y + 92)}" width="4" height="30" fill="{RED}"/>')
    return side(2, 9, 104.0, sun + thermo + pill(x + 120, y + 70, 78.0, "1 100 KG"))


def scene_4():                                               # the same useful load: four draws into one bar
    x, y = PX[3], PY[3]
    bx0, bw, by, bh = x + 24, PW - 48, y + 112, 44
    bar = (f'<rect x="{n(bx0)}" y="{n(by)}" width="{n(bw)}" height="{n(bh)}" rx="10" fill="#64748B" stroke="#FFFFFF" stroke-width="2"/><rect x="{n(bx0)}" y="{n(by)}" width="{n(bw)}" height="{n(bh * 0.36)}" rx="10" fill="#FFFFFF" fill-opacity="0.2"/>'
           + H.glyph_text("340 KG", bx0 + bw / 2, by + bh / 2 + 0.5, 17.0, fill="#FFFFFF"))
    xs = (x + 62, x + 120, x + 184, x + 244)
    arrows = "".join(S.ribbon(f"{U}d{k}", [(ax, y + 74), (ax, y + 88), (ax, y + 100), (ax, by - 2)], 5.0, "#2FA35A", "#9BE0B2", opacity=0.9, head=2.0, tail=0.5, per=6) for k, ax in enumerate(xs))
    fuel = f'<rect x="{n(xs[2] - 20)}" y="{n(y + 36)}" width="40" height="30" rx="8" fill="#FEF3C7" stroke="#B45309" stroke-width="2"/><path d="M{n(xs[2])} {n(y + 42)} q7 9 0 16 q-7 -7 0 -16 Z" fill="#F59E0B"/>'
    sun = S.glow(f"{U}sg4", xs[3], y + 50, 24, "#FFF2C4", 0.95) + f'<circle cx="{n(xs[3])}" cy="{n(y + 50)}" r="9" fill="#FDE68A" stroke="#F59E0B" stroke-width="1.6"/>'
    return frame(3, f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="#EAD9AE"/>' + bar + arrows + jerrycan(xs[0], y + 50, 0.8, "#BFDBFE") + kit(xs[1], y + 52, 0.7) + fuel + sun)


def sprites():
    o = lambda x, y, w, angle=0.0: {"name": "sprite-side", "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[1] + 210, PY[1] + 86, 56, -4.0), o(PX[2] + 150, PY[2] + 112, 70)]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-12-06-desert-loading",
        "replaces": "fig-12-06-desert-loading.svg",           # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-12-06-desert-loading.jpg",
        "caption": "Figure 12-6. Desert flights and hot days: water and a kit, long distances and heat all draw on the same useful load",
        "desc": ("Figure 12-6. Desert flights and hot days in four scenes: water and survival equipment weigh about a kilogram a litre and share the 45 kg baggage limit; long distances tempt full tanks and mean fewer people; "
                 "heat and elevation make a takeoff at the maximum mass of 1 100 kg worse; and all three draw on the same 340 kg of useful load."),
        "legend": [
            "Water and survival equipment: a litre of water has a mass of about a kilogram, so water for a full cabin and a kit soon take a large share of the 45 kg baggage limit. Put them on the loading sheet from the start, and weigh them.",
            "Long distances tempt you to fill the tanks. In a four-seat trainer that often means fewer passengers or less baggage. A planned fuel stop can be better than a heavy aeroplane.",
            "Heat and elevation: high density altitude lengthens the takeoff and weakens the climb, and a heavy aeroplane makes both worse. The example tables of Chapter 11 are for 1 100 kg, the maximum mass. If the numbers are tight, take off in the cooler morning, carry less, or plan a fuel stop.",
            "Water, survival equipment, long legs and hot days all draw on the same 340 kg of useful load.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
