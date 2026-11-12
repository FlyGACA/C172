"""Figure 31-8. Planning a night cross-country around what you can and cannot see. The old plan drawn as an aerial night picture on a card of dark desert (figs/terrain.py, night; bare
hills fade in at the south-west, where the old figure has its contours): the three aerodromes with their asphalt, runway lamps and rotating beacons (the green lamp and its rays), the
lit highway as two rows of lamps, the two towns as clusters of amber and white lamps over a warm glow, the lit mast with its red lamp, a patch of dust (a brown haze, the lamps in it
soft and haloed), the dashed contours of the unlit high ground, the dashed ellipse of dark desert and the straight dashed line across it that was not chosen, and the planned route as
glossy white arrows along the lit features. The ten numbered callouts of the old figure (7 has no leader, as before) are kept."""
import math
import os
import re

from figs import scene as S
from figs import h_a3 as H

n = S.n
U = "f3108"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H.terrain_card("terrain-31-08", 620, 400, radius=8.0, seed=318, kind="night", features=("wadis",), veil=0.0, soft=3.0, dim=0.72, flatten=0.12, rock_at=(0.07, 0.93, 0.42), rock_gain=0.8, rock_contrast=1.9)
WHITE = ("#B9C6E8", "#F4F7FF")
CONTOURS = ["M 18 355 Q 70 319 120 343 Q 160 315 215 349", "M 18 370 Q 70 334 120 358 Q 160 330 215 364", "M 18 385 Q 70 349 120 373 Q 160 345 215 379", "M 18 400 Q 70 364 120 388 Q 160 360 215 394"]
RUNWAYS = [(60, 212, 40, 6), (540, 59, 40, 6), (565, 342, 40, 6)]
BEACONS = [(106, 201), (586, 48), (611, 331)]
ROUTE = [[(98, 223), (250, 285)], [(250, 285), (455, 280)], [(455, 280), (527, 181)], [(527, 181), (552, 74)]]


def old_lamps():
    with open(os.path.join(HERE, "old", "fig-31-08-night-cross-country.svg"), encoding="utf-8") as f:
        svg = f.read()
    circles = [(float(x), float(y), float(r), fill, op) for x, y, r, fill, op in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="(#[0-9a-f]+)"( opacity="[\d.]+")?', svg)]
    colour = {"#ffffff": "w", "#b45309": "a"}
    road = [(x, y, colour[f]) for x, y, r, f, op in circles if f in colour and r < 1.6 and op == ' opacity="0.9"']
    towns = [(x, y, colour[f]) for x, y, r, f, op in circles if f in colour and 1.4 <= r < 1.6 and not op]
    runway = [(x, y) for x, y, r, f, op in circles if f == "#ffffff" and r == 1.4 and not op]
    return road, towns, runway


def haze():
    return (f'<defs><filter id="{U}hz" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="7" result="b"/><feTurbulence type="fractalNoise" baseFrequency="0.034" numOctaves="3" seed="6" result="t"/>'
            f'<feDisplacementMap in="b" in2="t" scale="30"/></filter></defs>'
            f'<ellipse cx="520" cy="160" rx="58" ry="44" fill="#A06E36" fill-opacity="0.50" filter="url(#{U}hz)"/><ellipse cx="505" cy="170" rx="40" ry="30" fill="#C28A4A" fill-opacity="0.22" filter="url(#{U}hz)"/>')


def guides():
    contours = "".join(f'<path d="{d}" fill="none" stroke="#9AA9CC" stroke-opacity="0.75" stroke-width="1.5" stroke-dasharray="3 3"/>' for d in CONTOURS)
    desert = '<ellipse cx="300" cy="140" rx="135" ry="78" fill="none" stroke="#B4C0DD" stroke-opacity="0.75" stroke-width="1.4" stroke-dasharray="6 5"/>'
    direct = '<line x1="100" y1="207" x2="538" y2="68" stroke="#C9D3EA" stroke-opacity="0.85" stroke-width="1.4" stroke-dasharray="4 5"/>'
    return contours + desert + direct


def town_glow():
    return (f'<defs><radialGradient id="{U}tg" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFB561" stop-opacity="0.34"/><stop offset="1" stop-color="#FFB561" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="254" cy="302" rx="52" ry="38" fill="url(#{U}tg)"/><ellipse cx="456" cy="298" rx="58" ry="40" fill="url(#{U}tg)"/>')


def aerodromes():
    out = [f'<defs>{S.gradient(U + "as", [(0, "#3C4862"), (1, "#283147")])}</defs>']
    for x, y, w, h in RUNWAYS:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{U}as)" stroke="#5B6987" stroke-opacity="0.7" stroke-width="0.7"/>')
    return "".join(out)


def beacon(cx, cy):
    spokes = "".join(f'<line x1="{n(cx + 3.4 * math.cos(math.radians(45 * i)))}" y1="{n(cy + 3.4 * math.sin(math.radians(45 * i)))}" x2="{n(cx + 9.6 * math.cos(math.radians(45 * i)))}" y2="{n(cy + 9.6 * math.sin(math.radians(45 * i)))}"/>' for i in range(8))
    return (f'<g stroke="#BFFFD9" stroke-width="3" stroke-opacity="0.28" stroke-linecap="round" filter="url(#{U}b1)">{spokes}</g><g stroke="#F3FFF8" stroke-width="1.3" stroke-linecap="round">{spokes}</g>'
            + H.lamp(U, cx, cy, "g", 2.6, 1.5))


def lamps():
    road, towns, runway = old_lamps()
    out = [H.lamp(U, x, y, c, 1.1, 0.7) for x, y, c in road]
    out += [H.lamp(U, x, y, c, 1.05, 0.65) for x, y, c in towns]
    out += [H.lamp(U, x, y, "w", 1.3, 0.8) for x, y in runway]
    out += [beacon(x, y) for x, y in BEACONS]
    out.append(H.lamp(U, 505, 175, "r", 2.8, 2.2))                           # the lit mast: its red lamp, with a wide red halo
    out += [H.lamp(U, x, y, "w", 1.3, 2.4) for x, y in ((545, 140), (480, 135), (560, 190))]          # lights in the dust: dim, with big soft halos
    return "".join(out)


def route():
    return "".join(S.ribbon(f"{U}rt{i}", seg, 4.6, *WHITE, head=2.3) for i, seg in enumerate(ROUTE))


def callouts():
    c = S.callout
    return "".join([c(1, 50, 186, 72, 207), c(2, 512, 41, 540, 56), c(3, 535, 384, 567, 353), c(4, 250, 350, 250, 318), c(5, 130, 265, 130, 291), c(6, 461, 206, 500, 178),
                    c(7, 300, 125), c(8, 205, 205, 228, 168), c(9, 590, 215, 570, 190), c(10, 240, 385, 200, 372)])


def plate():
    layers = ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', H.common_defs(U), H.night_defs(U), S.card(U + "c", 10, 10, 620, 400, [(0, "#0A0F1C"), (1, "#05070D")], ""),
              {"name": "terrain-31-08", "at": [320, 210], "width": 620}, '<rect x="10" y="10" width="620" height="400" rx="8" fill="none" stroke="#ffffff" stroke-width="1.6"/>',
              guides(), haze(), town_glow(), aerodromes(), route(), lamps(), callouts()]
    return {
        "id": "fig-31-08-night-cross-country",
        "replaces": "fig-31-08-night-cross-country.svg",
        "book_file": "plate-31-08-night-cross-country.jpg",
        "caption": "Figure 31-8. Planning a night cross-country around what you can and cannot see",
        "desc": "Figure 31-8. Planning a night cross-country around what you can and cannot see",
        "legend": [
            "Aerodrome A: beacon and runway lights.",
            "Destination B.",
            "Alternate C, lighting checked.",
            "Town lights: good checkpoints.",
            "Lit highway: a line to follow.",
            "Lit mast: red obstruction light.",
            "Dark desert: no checkpoints, no horizon.",
            "Direct line across the dark: not chosen.",
            "Haze or dust: lights fade and grow halos.",
            "Unlit high ground in the south-west.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-31-08-night-cross-country.svg", "blank": True, "layers": layers},
    }
