"""Figure 23-8. The black-hole approach: the path flown when the runway's picture is held constant. Drawn again as a night scene on the old figure's canvas: a deep-blue sky with stars and the glow
of a town on the horizon, a featureless black ground (no lights, no texture), the unlit rising ground as a black silhouette against the sky, the runway as a row of glowing lamps with halos
and the PAPI (two white, two red) in front of it, the town's lights, the model's aeroplane (by night) on the approach, the correct path as a green ribbon and the sagging path as a red one,
with the dotted continuation the aeroplane never flies. The seven numbered callouts of the old figure and what they name are kept."""
import math

from figs import scene as S
from figs import h_a3 as H
from figs.kit import NIGHT, side_plane

n = S.n
U = "f2308"
HORIZON = 250

SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)                      # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
GREEN = ("#0F9460", "#7DEBB4")
RED = ("#C9302A", "#FF9484")

RED_PATH = [(40.0, 114.4), (72.2, 133.0), (104.5, 150.0), (136.8, 165.5), (169.0, 179.5), (201.2, 192.2), (233.5, 203.5), (265.8, 213.6), (298.0, 222.4), (330.2, 230.1), (362.5, 236.5)]
RED_DOTS = [(362.5, 236.5), (394.8, 241.9), (427.0, 246.1), (459.2, 249.2), (470.0, 250.0)]
HILL = "M 300 250 C 306.7 248.3 328 242.8 340 240 C 352 237.2 362 232.8 372 233 C 382 233.2 390.3 238.2 400 241 C 409.7 243.8 425 248.5 430 250 Z"


def glow_line(points, colour, width=9.0, opacity=0.32):
    return f'<polyline points="{S.pts(points)}" fill="none" stroke="{colour}" stroke-opacity="{n(opacity)}" stroke-width="{n(width)}" stroke-linecap="round" stroke-linejoin="round" filter="url(#{U}b2)"/>'


def sky_and_ground():
    out = [H.sky_night(U + "k", 0, 0, 640, HORIZON, HORIZON, glow_x=610, glow_strength=0.42), H.stars(0, 6, 640, HORIZON - 30, 120, seed=23)]
    # the far glow on the horizon and a thin haze above the ground
    out.append(f'<defs>{S.gradient(U + "gr", [(0, "#0B1224"), (0.5, "#070B16"), (1, "#03050A")])}{S.gradient(U + "hz", [(0, "#4A5E94", 0.55), (1, "#4A5E94", 0.0)])}</defs>'
               f'<rect x="0" y="{HORIZON}" width="640" height="{330 - HORIZON}" fill="url(#{U}gr)"/>'
               f'<rect x="0" y="{HORIZON - 7}" width="640" height="7" fill="url(#{U}hz)" opacity="0.8"/>')
    return "".join(out)


def hill():
    return (f'<path d="{HILL}" fill="#04060C"/>'
            f'<path d="M 300 250 C 306.7 248.3 328 242.8 340 240 C 352 237.2 362 232.8 372 233 C 382 233.2 390.3 238.2 400 241 C 409.7 243.8 425 248.5 430 250" fill="none" stroke="#7B90C8" stroke-opacity="0.45" stroke-width="0.9"/>')


def runway_lights():
    out = []
    # the faintly lit surface and the pool of light over it
    out.append(f'<defs><radialGradient id="{U}pool" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFE7B0" stop-opacity="0.26"/><stop offset="1" stop-color="#FFE7B0" stop-opacity="0"/></radialGradient></defs>'
               f'<ellipse cx="535" cy="249" rx="108" ry="18" fill="url(#{U}pool)"/>'
               f'<rect x="470" y="247" width="130" height="6" fill="#262E42"/><rect x="470" y="247" width="130" height="1.2" fill="#8E9BB8" fill-opacity="0.6"/>')
    out.append(H.lamp_row(U, [(470 + 13 * i, 246) for i in range(11)], "w", 1.7, 1.0))
    out.append(H.lamp_row(U, [(472 + 26 * i, 264) for i in range(5)], "w", 1.5, 0.85))
    return "".join(out)


def papi():
    return "".join(H.lamp(U, x, 237, c, 2.6, 1.15) for x, c in ((490, "w"), (497, "w"), (504, "r"), (511, "r")))


def town():
    """The lights of a town beyond the runway: lamps along a few streets and a loose scatter, amber and white, over a warm glow."""
    import random
    rnd = random.Random(8)
    out = [f'<defs><radialGradient id="{U}tg" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFC16B" stop-opacity="0.38"/><stop offset="1" stop-color="#FFC16B" stop-opacity="0"/></radialGradient></defs>'
           f'<ellipse cx="626" cy="268" rx="46" ry="24" fill="url(#{U}tg)"/>']
    lamps = []
    for k, (x0, y0, x1, y1) in enumerate([(598, 256, 640, 258), (598, 264, 640, 267), (600, 273, 640, 276), (604, 282, 640, 284)]):
        for i in range(9):
            t = i / 8.0
            lamps.append((x0 + (x1 - x0) * t + rnd.uniform(-1.0, 1.0), y0 + (y1 - y0) * t + rnd.uniform(-0.8, 0.8)))
    for x in (606, 616, 626, 636):
        for j in range(5):
            lamps.append((x + rnd.uniform(-1, 1), 258 + j * 6 + rnd.uniform(-1, 1)))
    for x, y in lamps:
        out.append(H.lamp(U, x, y, "a" if rnd.random() < 0.72 else "w", 0.85, 0.75))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 150, 292), c(2, 560, 222, 560, 244), c(3, 622, 220, 616, 258), c(4, 250, 120, 250, 176), c(5, 200, 242, 205, 195),
                    c(6, 372, 294, 362.5, 243.5), c(7, 505, 200, 500, 234)])


def plate():
    green = [(40.0, 114.4), (266.0, 182.2), (492.0, 250.0)]
    plane = side_plane(50, 108.4, 16, 1.0, SILHOUETTE, grow=1.7, look=NIGHT)
    layers = ['<rect x="0" y="0" width="640" height="330" fill="#050912"/>', H.common_defs(U), H.night_defs(U), sky_and_ground(), hill(), town(), runway_lights(),
              glow_line(green, "#3EE59A", 8.0, 0.28), S.ribbon(U + "g", green, 4.6, *GREEN, head=1.0, opacity=0.95),
              glow_line(RED_PATH, "#FF5A48", 9.0, 0.30), S.ribbon(U + "r", RED_PATH, 4.8, *RED, head=1.0, opacity=0.95),
              f'<polyline points="{S.pts(RED_DOTS)}" fill="none" stroke="#FF8A78" stroke-width="2.6" stroke-dasharray="0.1 6" stroke-linecap="round"/>',
              f'<circle cx="362.5" cy="236.5" r="9" fill="#FF4A3A" fill-opacity="0.25" filter="url(#{U}b2)"/><circle cx="362.5" cy="236.5" r="6" fill="none" stroke="#FF6A58" stroke-width="2.4"/>',
              plane, H.lamp(U, 20.8, 84.7, "r", 0.9, 1.0), papi(), callouts()]
    return {
        "id": "fig-23-08-black-hole",
        "replaces": "fig-23-08-black-hole.svg",
        "book_file": "plate-23-08-black-hole.jpg",
        "caption": "Figure 23-8. The black-hole approach: the path flown when the runway's picture is held constant",
        "desc": "Figure 23-8. The black-hole approach: the path flown when the runway's picture is held constant",
        "legend": [
            "Dark water or desert before the runway: no lights, no texture.",
            "Runway edge lights.",
            "Town lights beyond the runway.",
            "Green: the correct approach path.",
            "Red: the path flown by keeping the runway's picture unchanged; it sags well below the correct path.",
            "Unlit rising ground short of the runway, which the sagging path meets.",
            "The PAPI: two white and two red on the correct path, more red below it (Chapter 18).",
        ],
        "canvas": [640, 330],
        "background": "pale",
        "reskin": {"svg": "fig-23-08-black-hole.svg", "blank": True, "layers": layers},
    }
