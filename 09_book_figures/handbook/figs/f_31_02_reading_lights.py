"""Figure 31-2. Reading other aircraft by their lights: where they are, where they are heading and whether they are closing. On the old figure's canvas: a night plan on a card of dark desert
(figs/terrain.py) with your aeroplane in blue and the four others, the model from above by moonlight, each with its red, green and white lights as glowing lamps, their headings as pale
ribbons, your track dashed in blue and the lines of sight dotted; and the four windscreens as night views (stars over a faint horizon, the lights as glowing lamps: a red one fixed in the
screen and ringed, a green one drifting across, the green and red of the head-on aircraft with the starburst of its flashing light, the white tail light alone). The eight numbered callouts
of the old figure (and the four numbers of the windscreens) are kept."""
import math

from figs import scene as S
from figs import h_a3 as H

n = S.n
U = "f3102"
H.terrain_card("terrain-31-02", 290, 365, radius=8.0, seed=312, kind="night", features=("wadis",), veil=0.0, soft=3.0, dim=0.72, flatten=0.12)
SKY = [(0, "#060B1E"), (0.30, "#0E1A3E"), (0.52, "#2A3C6E"), (0.5495, "#34467A"), (0.5505, "#05070D"), (1, "#05070D")]
WHITE = ("#B9C6E8", "#F4F7FF")

# the others: (x, y, heading in degrees clockwise from north, red lamp, green lamp, white lamp), as in the old drawing
OTHERS = [(245, 265, 270, (242, 283), (242, 247), (260, 265)), (45, 265, 90, (48, 247), (48, 283), (30, 265)), (171, 65, 180, (189, 68), (153, 68), (171, 50)), (141, 169, 0, (123, 166), (159, 166), (141, 184))]
ARROWS = [[(223, 265), (209, 265), (193, 265)], [(67, 265), (81, 265), (97, 265)], [(171, 87), (171, 102), (171, 117)], [(141, 147), (141, 132), (141, 117)]]


def plan_card():
    return S.card(U + "P", 15, 20, 290, 365, [(0, "#0A0F1C"), (1, "#05070D")], "")


def plan():
    out = [{"name": "terrain-31-02", "at": [160, 202.5], "width": 290}, '<rect x="15" y="20" width="290" height="365" rx="8" fill="none" stroke="#ffffff" stroke-width="1.6"/>']
    track = (f'<line x1="165" y1="323" x2="165" y2="40" stroke="#6FA0FF" stroke-opacity="0.30" stroke-width="5" filter="url(#{U}b2)"/>'
             f'<line x1="165" y1="323" x2="165" y2="40" stroke="#8FB4FF" stroke-width="1.7" stroke-dasharray="6 4.2"/>')
    sights = "".join(f'<line x1="165" y1="345" x2="{x}" y2="{y}" stroke="#C9D3EA" stroke-opacity="0.75" stroke-width="1.1" stroke-dasharray="1.5 4.2" stroke-linecap="round"/>'
                     for x, y in ((245, 265), (45, 265), (171, 65), (141, 169)))
    out.append(track + sights)
    out.append("".join(S.ribbon(f"{U}ar{i}", a, 3.4, *WHITE, head=2.4) for i, a in enumerate(ARROWS)))
    return out


def planes():
    shadow = {"dx": 1.0, "dy": 2.0, "blur": 1.6, "opacity": 0.45}
    out = [{"name": "sprite-top-night", "at": [x, y], "width": 42, "angle": h, "shadow": shadow} for x, y, h, *_ in OTHERS]
    out.append({"name": "sprite-top-night", "at": [165, 345], "width": 42, "angle": 0, "tint": "#3F6FE6", "tint_strength": 0.75, "shadow": shadow})
    return out


def lights():
    out = []
    for _x, _y, _h, red, green, white in OTHERS:
        out.append(H.lamp(U, red[0], red[1], "r", 1.9, 1.5) + H.lamp(U, green[0], green[1], "g", 1.9, 1.5) + H.lamp(U, white[0], white[1], "w", 1.7, 1.3))
    return "".join(out)


def windscreen(uid, x, y, w, h, seed, body):
    horizon = y + 50.6
    base = [H.stars(x, y, w, 50.0, 22, seed=seed), body,
            f'<defs>{S.gradient(uid + "gl", [(0, "#FFFFFF", 0.10), (1, "#FFFFFF", 0.0)], 0, 0, 1, 1)}</defs>'
            f'<polygon points="{S.pts([(x, y), (x + 46, y), (x, y + 38)])}" fill="url(#{uid}gl)"/>'
            f'<rect x="{x + w / 2 - 2}" y="{y + 76}" width="4" height="10" fill="#E8EEFC" fill-opacity="0.85"/><rect x="{x + w / 2 - 6}" y="{y + 74}" width="12" height="14" fill="#E8EEFC" fill-opacity="0.10" filter="url(#{U}b2)"/>']
    return S.card(uid + "c", x, y, w, h, SKY, "".join(base))


def view1():
    return windscreen(U + "v1", 330, 30, 140, 92, 11,
                      f'<circle cx="437.3" cy="80.6" r="11" fill="none" stroke="#FF6A58" stroke-opacity="0.35" stroke-width="3.6" filter="url(#{U}b1)"/>'
                      f'<circle cx="437.3" cy="80.6" r="11" fill="none" stroke="#FF7C6C" stroke-width="1.3" stroke-dasharray="3 2.2"/>' + H.lamp(U, 437.3, 80.6, "r", 3.0, 1.45))


def view2():
    return windscreen(U + "v2", 486, 30, 140, 92, 12,
                      H.lamp(U, 531.6, 80.6, "g", 1.7, 1.0) + H.lamp(U, 509.6, 80.6, "g", 3.0, 1.45)
                      + S.ribbon(U + "w2", [(527, 68.6), (520, 68.6), (512, 68.6)], 3.2, *WHITE, head=2.6))


def burst(cx, cy):
    spokes = "".join(f'<line x1="{n(cx + 2.6 * math.cos(math.radians(45 * i)))}" y1="{n(cy + 2.6 * math.sin(math.radians(45 * i)))}" x2="{n(cx + 7.6 * math.cos(math.radians(45 * i)))}" y2="{n(cy + 7.6 * math.sin(math.radians(45 * i)))}"/>' for i in range(8))
    return (f'<g stroke="#FF5A48" stroke-width="3.4" stroke-opacity="0.35" stroke-linecap="round" filter="url(#{U}b1)">{spokes}</g><g stroke="#FF8A78" stroke-width="1.5" stroke-linecap="round">{spokes}</g>'
            + H.lamp(U, cx, cy, "r", 1.2, 0.8))


def view3():
    return windscreen(U + "v3", 330, 190, 140, 92, 13,
                      f'<circle cx="400.8" cy="240.6" r="17" fill="none" stroke="#C9D3EA" stroke-opacity="0.8" stroke-width="1.2" stroke-dasharray="3 2.2"/>'
                      + H.lamp(U, 391.8, 240.6, "g", 3.0, 1.45) + H.lamp(U, 409.8, 240.6, "r", 3.0, 1.45) + burst(400.8, 229.6))


def view4():
    return windscreen(U + "v4", 486, 190, 140, 92, 14, H.lamp(U, 549.4, 240.6, "w", 3.0, 1.45))


def callouts():
    c = S.callout
    return "".join([c(1, 271, 293, 254, 273), c(2, 51, 225, 47, 245), c(3, 215, 71, 190, 68), c(4, 99, 173, 121, 171), c(5, 121, 349, 148, 345),
                    c(1, 332, 32), c(2, 488, 32), c(3, 332, 192), c(4, 488, 192), c(6, 458, 144, 443.3, 90.6), c(7, 516, 144, 519.6, 74.6), c(8, 440, 304, 400.8, 234.6)])


def plate():
    layers = ['<rect x="0" y="0" width="640" height="400" fill="#ffffff"/>', H.common_defs(U), H.night_defs(U), plan_card(), *plan(), *planes(), lights(), view1(), view2(), view3(), view4(), callouts()]
    return {
        "id": "fig-31-02-reading-lights",
        "replaces": "fig-31-02-reading-lights.svg",
        "book_file": "plate-31-02-reading-lights.jpg",
        "caption": "Figure 31-2. Reading other aircraft by their lights: where they are, where they are heading and whether they are closing",
        "desc": "Figure 31-2. Reading other aircraft by their lights: where they are, where they are heading and whether they are closing",
        "legend": [
            "Converging from your right: its red light.",
            "Crossing from your left, passing behind: its green light.",
            "Head-on: green and red, red on your right.",
            "Ahead, same direction: white tail light alone.",
            "Your aeroplane.",
            "A light fixed in the windscreen that grows: a collision course.",
            "A light drifting across the windscreen is passing; keep it in sight.",
            "The anticollision light flashes; stars do not.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-31-02-reading-lights.svg", "blank": True, "layers": layers},
    }
