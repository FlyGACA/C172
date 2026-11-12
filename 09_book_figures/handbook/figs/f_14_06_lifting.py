"""Figure 14-6. Four ways air is lifted. Four scenes in cards: heated sand sending up bubbles of warm air under a cumulus, with air sinking over an oasis (convection); wind forced up
a mountain with cumulus building over the crest and the air falling on the lee side (orographic lift, and the sun-heated slopes); a cold wedge of air with the warm air riding up
over it under a rain cloud (frontal lift); and two winds meeting over a coast with a line of cumulus above where they meet (convergence). The clouds are the sprites of
figs/clouds.py, the land and the arrows come from figs/scene.py; the five numbered callouts of the old figure are kept (their places move with the pictures)."""
import math
import random

from figs import scene as S

CARDS = {"A": (8, 6, 304, 196), "B": (328, 6, 304, 196), "C": (8, 214, 304, 196), "D": (328, 214, 304, 196)}
DAY = [(0.0, "#3F78C2"), (0.55, "#86B4E6"), (0.95, "#DCEBF8"), (1.0, "#F4F1DF")]
GREY = [(0.0, "#6F86A8"), (0.5, "#A5B6CE"), (1.0, "#DCE4EE")]
ORANGE = ("#E8782E", "#F8BE73")
BLUE = ("#2F63C8", "#8DB3F2")
INK = ("#1F2937", "#667489")


def heat_bubble(uid, cx, cy, r):
    """A bubble of warm air: a soft orange glow with a bright core and a thin pale ring."""
    return (f'<defs><radialGradient id="{uid}" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFF4D6" stop-opacity="0.98"/><stop offset="0.55" stop-color="#FFBE66" stop-opacity="0.85"/>'
            f'<stop offset="0.9" stop-color="#F28A3C" stop-opacity="0.55"/><stop offset="1" stop-color="#F28A3C" stop-opacity="0.0"/></radialGradient></defs>'
            f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{S.n(r)}" fill="url(#{uid})"/><circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{S.n(r * 0.86)}" fill="none" stroke="#FFF3D6" stroke-opacity="0.75" stroke-width="0.9"/>')


def shimmer(x0, x1, y, count, seed):
    """Heat shimmer over the sand: short wavy light lines."""
    rnd = random.Random(seed)
    out = []
    for _ in range(count):
        x, yy = rnd.uniform(x0, x1), y - rnd.uniform(0, 16)
        out.append(f'<path d="M {S.n(x)},{S.n(yy)} q 2.4,-3 0,-6 q -2.4,-3 0,-6" fill="none" stroke="#FFFFFF" stroke-opacity="{S.n(rnd.uniform(0.3, 0.6))}" stroke-width="0.9" stroke-linecap="round"/>')
    return "".join(out)


def card_a():
    x, y, w, h = CARDS["A"]
    hz = y + 150
    far = S.land_layer("f1406af", S.ridge(3, x, x + w, hz + 1, 26, peaks=0.5), hz + 4, ("#7283AB", "#AAB8D2"), rim=True, haze=0.18)
    sand = f'<defs>{S.gradient("f1406as", [(0, "#E8D7AC"), (1, "#D0B686")])}{S.gradient("f1406ag", [(0, "#6FA05A"), (1, "#4F8244")])}</defs><rect x="{x}" y="{hz}" width="{w}" height="{y + h - hz}" fill="url(#f1406as)"/>'
    oasis = (f'<path d="M 216,{hz} Q 214,{hz + 24} 222,{y + h} L {x + w},{y + h} L {x + w},{hz} Z" fill="url(#f1406ag)"/>'
             f'<ellipse cx="268" cy="{hz + 28}" rx="34" ry="8" fill="#5AA9D8"/><ellipse cx="268" cy="{hz + 27}" rx="30" ry="5.5" fill="#8FCBEA"/>'
             + S.palm(238, hz + 22, 30, 0.1, 3) + S.palm(292, hz + 20, 27, -0.12, 5) + S.palm(262, hz + 12, 22, 0.05, 7) + S.acacia(246, hz + 40, 12, 4))
    ground = S.scrub(4, x, 214, hz + 6, y + h - 4, 14, colour=("#8A8A55", "#5E603E"), scale=0.55) + S.house(34, hz + 30, 18, 10, 3) + S.palm(78, hz + 34, 24, 0.1, 6) + shimmer(x + 14, 200, hz + 6, 12, 5)
    return S.card("f1406A", x, y, w, h, DAY, S.sun("f1406sa", x + 38, y + 30, 9) + far + sand + oasis + ground)


def card_b():
    x, y, w, h = CARDS["B"]
    bottom = y + h
    far = S.land_layer("f1406bf", S.ridge(9, x, x + w, y + 150, 36, peaks=0.6), bottom, ("#8190B2", "#B3BFD6"), rim=True, haze=0.2)
    outline = S.jag([(x, y + 186), (x + 40, y + 182), (x + 112, y + 174), (x + 142, y + 144), (x + 172, y + 112), (x + 200, y + 88), (x + 216, y + 82), (x + 230, y + 92), (x + 256, y + 118), (x + 276, y + 150), (x + w, y + 170)], 2.6, 7)
    mountain = S.rock("f1406bm", outline, bottom, x, x + w, 4, spine=[(x + 216, y + 82), (x + 210, y + 118), (x + 224, y + 150), (x + 206, y + 196)])
    bushes = S.scrub(8, x + 8, x + 112, y + 176, bottom - 2, 8, colour=("#8A8A55", "#5E603E"), scale=0.5) + S.acacia(x + 36, y + 196, 11, 3) + S.palm(x + 276, y + 176, 20, -0.1, 9)
    return S.card("f1406B", x, y, w, h, DAY, S.sun("f1406sb", x + 32, y + 28, 9) + far + mountain + bushes)


def card_c():
    x, y, w, h = CARDS["C"]
    hz = y + 176
    wedge = [(x, y + 176), (x, y + 90), (x + 48, y + 108), (x + 112, y + 138), (x + 150, y + 158), (x + 192, y + 176)]
    far = S.land_layer("f1406cf", S.ridge(14, x, x + w, hz - 2, 24, peaks=0.4), hz + 4, ("#8A98B8", "#B9C4D8"), rim=False, haze=0.2)
    ground = f'<defs>{S.gradient("f1406cg", [(0, "#E4D2A4"), (1, "#C9AD7A")])}</defs><rect x="{x}" y="{hz}" width="{w}" height="{y + h - hz}" fill="url(#f1406cg)"/>' + S.scrub(2, x, x + w, hz + 2, y + h - 2, 10, colour=("#8A8A55", "#5E603E"), scale=0.5)
    cold = (S.air("f1406cair", wedge, "#6D93D8", "#C6D8F4", 0.62)
            + f'<path d="M {x},{y + 90} C {x + 48},{y + 108} {x + 112},{y + 138} {x + 150},{y + 158} C {x + 170},{y + 166} {x + 184},{y + 172} {x + 194},{y + 176}" fill="none" stroke="#2F5DB5" stroke-width="1.8"/>')
    return S.card("f1406C", x, y, w, h, GREY, far + cold + ground + S.palm(x + 262, hz + 20, 24, -0.1, 2) + S.house(x + 222, hz + 14, 17, 10, 7) + S.acacia(x + 168, hz + 26, 11, 4))


def card_d():
    x, y, w, h = CARDS["D"]
    hz = y + 150
    shore = x + 150
    sea = S.sea("f1406ds", x, shore + 4, hz, y + h, seed=4, light="#4B97CC", dark="#2C6FAE")
    land = (f'<defs>{S.gradient("f1406dl", [(0, "#E8D7AC"), (1, "#CDB382")])}</defs>'
            f'<path d="M {shore},{hz - 1} C {shore + 8},{hz + 30} {shore - 8},{hz + 60} {shore + 4},{y + h} L {x + w},{y + h} L {x + w},{hz - 1} Z" fill="url(#f1406dl)"/>'
            f'<path d="M {shore},{hz - 1} C {shore + 8},{hz + 30} {shore - 8},{hz + 60} {shore + 4},{y + h}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-opacity="0.8"/>')
    far = S.land_layer("f1406df", S.ridge(5, shore - 4, x + w, hz + 1, 30, peaks=0.55), hz + 4, ("#7283AB", "#AAB8D2"), rim=True, haze=0.15)
    items = S.house(x + 214, hz + 34, 17, 10, 3) + S.house(x + 246, hz + 40, 14, 8, 5) + S.palm(x + 200, hz + 52, 25, 0.1, 6) + S.palm(x + 278, hz + 46, 22, -0.1, 7) + S.dhow(x + 62, y + 168, 0.9) + S.dhow(x + 108, hz + 14, 0.55)
    return S.card("f1406D", x, y, w, h, DAY, S.sun("f1406sd", x + 40, y + 30, 8) + far + sea + land + items)


def arrows():
    r = S.ribbon
    a = []
    # A: warm bubbles rise over the sand, the air sinks over the oasis
    a += [r("f1406a1", [(90, 196), (90, 160), (91, 118)], 6.0, *ORANGE), r("f1406a2", [(150, 196), (150, 150), (151, 100)], 6.0, *ORANGE), r("f1406a3", [(262, 80), (262, 120), (262, 158)], 6.0, *BLUE)]
    # B: the wind meets the slope, climbs it, and falls on the lee side
    a += [r("f1406b1", [(336, 170), (372, 170), (412, 168)], 6.0, *INK), r("f1406b2", [(458, 160), (482, 134), (510, 100), (532, 70)], 7.0, *ORANGE), r("f1406b3", [(576, 92), (598, 108), (614, 140)], 5.5, *BLUE)]
    # C: cold air pushes forward under the warm air, which is forced up over it
    a += [r("f1406c1", [(36, 380), (70, 380), (116, 380)], 7.0, *BLUE), r("f1406c2", [(298, 384), (262, 384), (214, 380)], 6.5, *INK), r("f1406c3", [(196, 378), (176, 350), (146, 322), (118, 300)], 7.5, *ORANGE)]
    # D: two winds meet and the air goes up
    a += [r("f1406d1", [(344, 350), (400, 350), (454, 350)], 6.0, *INK), r("f1406d2", [(616, 350), (562, 350), (508, 350)], 6.0, *INK), r("f1406d3", [(480, 346), (480, 326), (480, 298)], 7.0, *ORANGE)]
    return "".join(a)


def bubbles():
    return heat_bubble("f1406hb1", 90, 140, 15) + heat_bubble("f1406hb2", 150, 128, 15) + heat_bubble("f1406hb3", 91, 100, 10) + heat_bubble("f1406hb4", 151, 88, 10)


def rain_c():
    return S.rain("f1406rain", 86, 176, 296, 372, slant=-5, count=34, seed=4, colour="#2F55A8", veil=0.10, bottom=0.2)


def callouts():
    c = S.callout
    return "".join([c(1, 116, 160), c(2, 448, 118, 480, 126), c(3, 470, 52, 498, 54), c(4, 150, 338, 148, 326), c(5, 510, 326, 486, 326)])


CLOUDS = [
    {"name": "cloud-cumulus-a", "at": [118, 52], "width": 128},
    {"name": "cloud-cumulus-b", "at": [222, 36], "width": 46, "opacity": 0.9},
    {"name": "cloud-congestus", "at": [538, 58], "width": 54},
    {"name": "cloud-nimbostratus", "at": [130, 280], "width": 140, "height": 46},
    {"name": "cloud-cumulus-a", "at": [482, 278], "width": 136},
    {"name": "cloud-cumulus-b", "at": [404, 262], "width": 50, "opacity": 0.85},
    {"name": "cloud-cumulus-b", "at": [572, 264], "width": 52, "opacity": 0.85},
]


def plate():
    return {
        "id": "fig-14-06-lifting",
        "replaces": "fig-14-06-lifting.svg",
        "book_file": "plate-14-06-lifting.jpg",
        "caption": "Figure 14-6. Four ways air is lifted",
        "desc": "Figure 14-6. Four ways air is lifted",
        "legend": [
            "Convection: heated ground sends up bubbles of warm air; air sinks over cooler water or vegetation.",
            "Orographic lift: wind forced up a slope, descending on the lee side.",
            "Sun-heated slopes add their own rising air, so cumulus builds over high ground in the afternoon.",
            "Frontal lift: colder air pushes under warmer air.",
            "Convergence: surface winds meet and the air goes up, as where a sea breeze meets another wind.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-14-06-lifting.svg", "blank": True,
                   "layers": ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', card_a(), card_b(), card_c(), card_d(), *CLOUDS, rain_c(), bubbles(), arrows(), callouts()]},
    }
