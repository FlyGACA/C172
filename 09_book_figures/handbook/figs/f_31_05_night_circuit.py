"""Figure 31-5. A night circuit for runway 27: the lights you use and the traps. The old plan drawn as an aerial night picture on a card of dark desert (figs/terrain.py, kind night): the
aerodrome as dim asphalt (the runway, the taxiway and the apron) with every lamp of the old figure as a glowing lamp (runway edge lamps white, green threshold, red end, blue taxiway
edge, approach lights with their cross bar, the PAPI, the rotating beacon with its rays), the lit highway as two rows of lamps (white and amber), the town as a cluster of amber and white
lamps over a warm glow, the circuit as a glowing dashed line with its arrowheads, the join at 45 degrees in green, the two aeroplanes (the model from above by moonlight) with their red,
green and white lights and the landing light of the one on final. The thirteen numbered callouts of the old figure are kept."""
import math
import os
import re

from figs import scene as S
from figs import h_a3 as H

n = S.n
U = "f3105"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H.terrain_card("terrain-31-05", 620, 400, radius=8.0, seed=31, kind="night", features=("wadis",), veil=0.0, soft=3.0, dim=0.72, flatten=0.12)
CIRCUIT = "M 210 125 L 175 125 Q 145 125 145 155 L 145 300 Q 145 330 175 330 L 555 330 Q 585 330 585 300 L 585 155 Q 585 125 555 125 L 474 125"
GREEN = ("#0F9460", "#7DEBB4")


def old_lamps():
    """The lamps the old drawing has for the highway and the town: [(x, y, colour)]."""
    with open(os.path.join(HERE, "old", "fig-31-05-night-circuit.svg"), encoding="utf-8") as f:
        svg = f.read()
    circles = [(float(x), float(y), float(r), fill) for x, y, r, fill, op in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="(#[0-9a-f]+)"( opacity="[\d.]+")?', svg)]
    colour = {"#ffffff": "w", "#b45309": "a"}
    town = [(x, y, colour[f]) for x, y, r, f in circles if x < 112 and y > 300 and f in colour and r < 2]
    road = [(x, y, colour[f]) for x, y, r, f in circles if x < 185 and y < 212 and f in colour and r < 2]
    return town, road


def surfaces():
    out = [f'<defs>{S.gradient(U + "as", [(0, "#3C4862"), (1, "#283147")])}<radialGradient id="{U}pool" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFD9A0" stop-opacity="0.20"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient>'
           f'<radialGradient id="{U}town" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFB561" stop-opacity="0.34"/><stop offset="1" stop-color="#FFB561" stop-opacity="0"/></radialGradient></defs>',
           f'<ellipse cx="340" cy="92" rx="230" ry="86" fill="url(#{U}pool)"/>',
           f'<ellipse cx="72" cy="352" rx="78" ry="56" fill="url(#{U}town)"/>']
    out.append(f'<rect x="290" y="38" width="90" height="24" rx="2" fill="url(#{U}as)" stroke="#5B6987" stroke-opacity="0.6" stroke-width="0.8"/>'
               f'<rect x="325" y="60" width="18" height="58" fill="url(#{U}as)"/>'
               f'<rect x="210" y="118" width="260" height="14" fill="url(#{U}as)" stroke="#5B6987" stroke-opacity="0.7" stroke-width="0.8"/>')
    out.append(f'<line x1="224" y1="125" x2="458" y2="125" stroke="#C9D3EA" stroke-opacity="0.45" stroke-width="1.1" stroke-dasharray="10 8"/>')
    return "".join(out)


def lamps():
    out = []
    town, road = old_lamps()
    out.append(H.lamp_row(U, [(x, y) for x, y, c in road if c == "w"], "w", 1.15, 0.6))
    out.append(H.lamp_row(U, [(x, y) for x, y, c in road if c == "a"], "a", 1.05, 0.6))
    for x, y, c in town:
        out.append(H.lamp(U, x, y, c, 0.95, 0.65))
    out.append(H.lamp_row(U, [(216 + 16 * i, y) for i in range(16) for y in (115, 135)], "w", 1.5, 0.9))
    out.append(H.lamp_row(U, [(472, 117 + 4 * i) for i in range(5)], "g", 1.5, 0.9))
    out.append(H.lamp_row(U, [(208, 117 + 4 * i) for i in range(5)], "r", 1.5, 0.9))
    out.append(H.lamp_row(U, [(x, y) for x in (321, 347) for y in (66, 78, 90, 102, 114)], "b", 1.45, 0.85))
    out.append(H.lamp_row(U, [(x, 125) for x in (482, 491, 500, 509, 527, 536, 545, 554)] + [(518, 110 + 5 * i) for i in range(7)], "w", 1.4, 0.8))
    out.append(H.lamp_row(U, [(425, 141), (425, 146)], "w", 1.7, 1.0) + H.lamp_row(U, [(425, 151), (425, 156)], "r", 1.7, 1.0))
    return "".join(out)


def beacon():
    spokes = []
    for i in range(10):
        a = math.radians(36 * i)
        spokes.append(f'<line x1="{n(395 + 4.2 * math.cos(a))}" y1="{n(40 + 4.2 * math.sin(a))}" x2="{n(395 + 11 * math.cos(a))}" y2="{n(40 + 11 * math.sin(a))}"/>')
    return (f'<g stroke="#BFFFD9" stroke-width="3" stroke-opacity="0.28" stroke-linecap="round" filter="url(#{U}b1)">{"".join(spokes)}</g>'
            f'<g stroke="#F3FFF8" stroke-width="1.3" stroke-linecap="round">{"".join(spokes)}</g>' + H.lamp(U, 395, 40, "g", 3.0, 1.5))


def circuit():
    glow = f'<path d="{CIRCUIT}" fill="none" stroke="#BCD0FF" stroke-opacity="0.22" stroke-width="6" stroke-linejoin="round" filter="url(#{U}b2)"/>'
    line = f'<path d="{CIRCUIT}" fill="none" stroke="#E3EBFF" stroke-opacity="0.9" stroke-width="2" stroke-dasharray="7 5" stroke-linejoin="round"/>'
    heads = [[(205, 125), (214, 120), (214, 129.9)], [(145, 230), (140.1, 221), (149.9, 221)], [(330, 330), (321, 334.9), (321, 325.1)], [(585, 230), (590, 239), (580, 239)], [(525, 125), (534, 120), (534, 129.9)]]
    tri = "".join(f'<polygon points="{S.pts(p)}" fill="#F1F5FF" stroke="#BCD0FF" stroke-opacity="0.5" stroke-width="0.8" stroke-linejoin="round"/>' for p in heads)
    dots = (f'<line x1="470" y1="136" x2="470" y2="324" stroke="#C9D3EA" stroke-opacity="0.7" stroke-width="1.1" stroke-dasharray="1.5 4.2" stroke-linecap="round"/>'
            f'<line x1="470" y1="125" x2="581" y2="324" stroke="#C9D3EA" stroke-opacity="0.7" stroke-width="1.1" stroke-dasharray="1.5 4.2" stroke-linecap="round"/>')
    ring = f'<circle cx="470" cy="330" r="8" fill="#FFFFFF" fill-opacity="0.18" filter="url(#{U}b2)"/><circle cx="470" cy="330" r="5" fill="none" stroke="#FFFFFF" stroke-width="2"/>'
    join = (f'<line x1="225" y1="405" x2="286" y2="338.5" stroke="#3EE59A" stroke-opacity="0.30" stroke-width="6" stroke-linecap="round" filter="url(#{U}b2)"/>'
            f'<line x1="225" y1="405" x2="286" y2="338.5" stroke="#5BE8A6" stroke-width="2.2" stroke-dasharray="5 4"/>'
            f'<polygon points="290,334 287.8,342.9 281.4,336.9" fill="#5BE8A6" stroke="#E8FFF2" stroke-opacity="0.6" stroke-width="0.7"/>')
    return glow + line + tri + dots + ring + join


def aeroplane_lights(cx, cy, heading, red_side):
    """Red on the left wingtip, green on the right, white at the tail: `heading` is 'e' or 'w' (the aeroplane flies east or west); red_side is the y offset of the red lamp."""
    if heading == "e":
        return H.lamp(U, cx + 2.7, cy - 17.4, "r", 1.5, 1.3) + H.lamp(U, cx + 2.7, cy + 17.4, "g", 1.5, 1.3) + H.lamp(U, cx - 13.5, cy, "w", 1.3, 1.1)
    return H.lamp(U, cx - 2.4, cy + 17.4, "r", 1.5, 1.3) + H.lamp(U, cx - 2.4, cy - 17.4, "g", 1.5, 1.3) + H.lamp(U, cx + 12.0, cy, "w", 1.3, 1.1)


def callouts():
    c = S.callout
    return "".join([c(1, 425, 44, 408, 41.5), c(2, 285, 100, 300, 115), c(3, 534, 85, 518, 110.5), c(4, 395, 173, 425, 146), c(5, 298, 80, 321, 78), c(6, 52, 104, 95.7, 116.5),
                    c(7, 120, 380, 96, 368), c(8, 196, 392, 236.9, 392), c(9, 300, 364, 300, 345), c(10, 500, 360, 473.5, 333.5), c(11, 611, 250, 586, 250),
                    c(12, 556, 226, 556, 160), c(13, 600, 70, 552, 120)])


def plate():
    shadow = {"dx": 1.0, "dy": 2.0, "blur": 1.6, "opacity": 0.45}
    layers = ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', H.common_defs(U), H.night_defs(U),
              S.card(U + "c", 10, 10, 620, 400, [(0, "#0A0F1C"), (1, "#05070D")], ""),
              {"name": "terrain-31-05", "at": [320, 210], "width": 620},
              surfaces(), circuit(), H.beam(U + "bm", 533, 125, 474, 125, 0.9, 13.0, "#FFF3D2", 0.7, 1.3, U), lamps(), beacon(),
              {"name": "sprite-top-night", "at": [300, 330], "width": 46, "angle": 90, "shadow": shadow}, {"name": "sprite-top-night", "at": [548, 125], "width": 46, "angle": 270, "shadow": shadow},
              aeroplane_lights(300, 330, "e", 0) + aeroplane_lights(548, 125, "w", 0),
              '<rect x="10" y="10" width="620" height="400" rx="8" fill="none" stroke="#ffffff" stroke-width="1.6"/>', callouts()]
    return {
        "id": "fig-31-05-night-circuit",
        "replaces": "fig-31-05-night-circuit.svg",
        "book_file": "plate-31-05-night-circuit.jpg",
        "caption": "Figure 31-5. A night circuit for runway 27: the lights you use and the traps",
        "desc": "Figure 31-5. A night circuit for runway 27: the lights you use and the traps",
        "legend": [
            "Aerodrome beacon.",
            "Runway edge lights white, threshold green, end red.",
            "Approach lights.",
            "PAPI, left of the runway seen from final.",
            "Taxiway edge lights, blue.",
            "A highway: a straight line of lights like a runway.",
            "Town lights.",
            "Joining at 45° to downwind, at circuit height.",
            "Downwind: runway lights parallel on your left; checks.",
            "Abeam the threshold: power back, descent, altimeter.",
            "Base, threshold about 45° behind: altimeter and vertical speed.",
            "Final over dark ground: expect the black hole.",
            "Traffic on final, landing light toward the runway.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-31-05-night-circuit.svg", "blank": True, "layers": layers},
    }
