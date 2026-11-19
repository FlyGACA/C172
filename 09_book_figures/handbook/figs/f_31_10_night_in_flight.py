"""Figure 31-10 (new). In flight at night over the Kingdom, from "In flight" of Chapter 31: four scenes.

1 lights deceive (the same town seen at 2 000 ft as separate points and at 5 000 ft as one mass of light), 2 the two cruise illusions (a false horizon: a sloping line of ground lights mixed with stars, with a level attitude indicator beside it to trust;
autokinesis: a single fixed light with an arrow, keep the eyes moving), 3 weather announces itself through the lights (lights fading one by one and a halo round them: restricted visibility or ground fog ahead; turn back while the lights behind are
clear), 4 the dark desert and the unlit high ground (no lights, no horizon; a ridge shows only where the stars stop). Shapes, colours and the numbers of the callouts; the only text is 2 000 FT and 5 000 FT. The drawings are generic."""
import math
import random

from figs import h_b2 as H
from figs import photo_ground as PG
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar31n"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
NIGHT = [(0.0, "#0B1633"), (0.55, "#1D2B58"), (0.9, "#3C4F86"), (1.0, "#4C5F95")]
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def frame(i, body):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def stars(i, seed, ymax=0.6):
    x, y = PX[i], PY[i]
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{n(rnd.uniform(x + 8, x + PW - 8))}" cy="{n(rnd.uniform(y + 6, y + PH * ymax))}" r="{n(rnd.uniform(0.6, 1.3))}" fill="#FFFFFF" opacity="{n(rnd.uniform(0.5, 0.95))}"/>' for _ in range(40))


def night(i, seed, hz=100.0, extra="", ground="#2A2F3F"):
    x, y = PX[i], PY[i]
    return frame(i, S.sky(f"{U}k{i}", x, y, PW, PH, NIGHT) + stars(i, seed) + (PG.side(x, x + PW, y + hz, y + PH, tone="night", offset=seed * 0.13 % 1.0) if ground == "#2A2F3F" else f'<rect x="{n(x)}" y="{n(y + hz)}" width="{n(PW)}" height="{n(PH - hz)}" fill="{ground}"/>') + extra)


def lamp(cx, cy, r=1.8, col="#FFE9A8", glow=9.0):
    return S.glow(f"{U}l{int(cx * 7)}{int(cy * 7)}", cx, cy, glow, col, 0.8) + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{r}" fill="#FFF6D6"/>'


def pill(cx, cy, w, text, fill="#1F2937", h=11.0):
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2 - 3.5)}" width="{n(w)}" height="{n(h + 7)}" rx="{n((h + 7) / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, h, fill="#FFFFFF"))


def town(cx, cy, rnd, count, spread):
    return "".join(lamp(cx + rnd.uniform(-spread, spread), cy + rnd.uniform(-spread * 0.4, spread * 0.4), 1.6, "#FFE9A8", 6.0) for _ in range(count))


def scene1():
    x, y = PX[0], PY[0]
    rnd = random.Random(3)
    return night(0, 4, 104.0, town(x + 78, y + 136, rnd, 26, 40) + pill(x + 78, y + 160, 76.0, "2 000 FT")
                 + S.glow(f"{U}m1", x + 228, y + 134, 52, "#FFE9A8", 0.9) + S.glow(f"{U}m2", x + 228, y + 134, 24, "#FFF6D6", 0.95) + pill(x + 228, y + 160, 76.0, "5 000 FT"))


def scene2():
    x, y = PX[1], PY[1]
    rnd = random.Random(5)
    slope = "".join(lamp(x + 24 + k * 11, y + 124 - k * 2.4, 1.6, "#FFE9A8", 6.0) for k in range(14)) + "".join(lamp(x + 30 + k * 10, y + 100 - k * 2.0 + rnd.uniform(-3, 3), 1.3, "#FFFFFF", 5.0) for k in range(8))
    ai = (f'<circle cx="{n(x + 98)}" cy="{n(y + 52)}" r="26" fill="#1E3A8A" stroke="#E2E8F0" stroke-width="3"/><path d="M{n(x + 72)} {n(y + 52)} A26 26 0 0 1 {n(x + 124)} {n(y + 52)} Z" fill="#38BDF8"/><circle cx="{n(x + 98)}" cy="{n(y + 52)}" r="3" fill="#FACC15"/>'
          f'<path d="M{n(x + 82)} {n(y + 52)} H{n(x + 114)}" stroke="#FACC15" stroke-width="3" stroke-linecap="round"/>')
    auto = lamp(x + 238, y + 70, 2.4, "#FFE9A8", 14.0) + f'<path d="M{n(x + 224)} {n(y + 54)} q-8 -2 -10 -12 M{n(x + 252)} {n(y + 86)} q8 2 10 12 M{n(x + 254)} {n(y + 54)} q8 -4 12 -14" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="3 4"/>'
    return night(1, 8, 140.0, slope + ai + auto)


def scene3():
    x, y = PX[2], PY[2]
    rnd = random.Random(7)
    near = town(x + 70, y + 150, rnd, 22, 36)
    fading = "".join(lamp(x + 196 + k * 12, y + 140 - k * 2, 1.7, "#FFE9A8", 5.0 + (5 - k) * 0.6) for k in range(6))
    halos = "".join(f'<circle cx="{n(x + 244 + k * 12)}" cy="{n(y + 128 - k * 2)}" r="{n(8 + k * 2)}" fill="#FFE9A8" fill-opacity="{n(0.28 - k * 0.04)}"/>' for k in range(4))
    turn = S.ribbon(f"{U}t3", [(x + 150, y + 64), (x + 190, y + 50), (x + 196, y + 86), (x + 150, y + 90), (x + 70, y + 84)], 5.0, "#E8782E", "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=8)
    return night(2, 9, 110.0, near + fading + halos + S.fog(f"{U}f3", x + 170, x + PW, y + 160, 70, seed=4, opacity=0.5, colour="#8794B4", wisp=1.0, foot=0.3, side_fade=0.2) + turn)


def scene4():
    x, y = PX[3], PY[3]
    ridge = S.ridge(5, x - 10, x + PW + 10, y + 120, 44.0, step=4.0, peaks=0.6)
    path = "M " + " L ".join(f"{n(px)},{n(py)}" for px, py in ridge) + f" L {n(x + PW + 10)},{n(y + PH)} L {n(x - 10)},{n(y + PH)} Z"
    return night(3, 12, 150.0, f'<path d="{path}" fill="#0A0F1E"/>', "#0A0F1E")


def sprites():
    o = lambda x, y, w, angle=0.0, name="sprite-side": {"name": name, "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[0] + 150, PY[0] + 52, 44), o(PX[2] + 215, PY[2] + 30, 44, 0.0), o(PX[3] + 120, PY[3] + 64, 50)]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene1(), scene2(), scene3(), scene4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-31-10-night-in-flight",
        "replaces": "fig-31-10-night-in-flight.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-31-10-night-in-flight.jpg",
        "caption": "Figure 31-10. In flight at night over the Kingdom: lights deceive, two illusions, weather in the lights, and the dark desert",
        "desc": ("Figure 31-10. In flight at night over the Kingdom in four scenes: lights seen separately at 2 000 ft merge into one mass at 5 000 ft; a false horizon and autokinesis; lights fading one by one and haloed, a sign of restricted visibility or ground fog, "
                 "so turn back while the lights behind are clear; and the dark desert with unlit high ground."),
        "legend": [
            "Lights deceive: lights seen separately at 2 000 ft may merge into one mass at 5 000 ft or higher, and a town appears long before you reach it.",
            "Two cruise illusions. A false horizon: ground lights mixed with stars, or a sloping cloud, suggest a horizon that is not level; trust the attitude indicator. Autokinesis: a single fixed light stared at for several seconds seems to move; keep your eyes moving and cross-check the instruments.",
            "Weather announces itself through the lights: lights fading one by one usually mean restricted visibility ahead, and a halo around them suggests ground fog. Turn back while lights behind you are still clear.",
            "Dark desert and unlit terrain: away from cities and highways there may be no lights at all, no checkpoints and no horizon; unlit high ground shows only where the stars or lights stop. Know each leg's safe altitude before takeoff.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
