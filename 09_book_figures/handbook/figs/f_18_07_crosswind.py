"""Figure 18-7. Reading the windsock, and splitting the wind into headwind and crosswind. At the left a card with the sky and the desert in which three windsocks hang from their poles in
the three states (a slack sleeve, a half-filled one, one blown straight out), drawn as shaded cloth, with the wind coming from the left as a ribbon; over the aerial view of the desert, the
vector triangle (the wind, its headwind and its crosswind, with the angle between the wind and the runway) as ribbons and runway 33 of asphalt with its dashes, bars and number painted
(330 degrees, up). The seven numbered callouts of the old figure are kept, in the same order and meaning (figs/scene.py makes the card, the ribbons and the callouts; figs/h_a2.py the
asphalt, the paint and the windsocks)."""
import math

from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 340
terrain.ensure("terrain-18-07", size=(W * 4, HT * 4), seed=187, kind="plain", features=("wadis", "tracks"), veil=0.32, soft=2.8)

U = "a187"
PAINT = "#F6F3EA"
BLUE, ORANGE, RED = "#1D4ED8", "#B45309", "#B91C1C"
n = S.n


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=6, relief=0.8, tone=0.0) + H.paint_filter(U + "pw", seed=12, wear=0.35, thickness=0.4) + H.blur_filter(U + "bl", 1.4)
            + S.gradient(U + "gr", [(0, "#ECDCB2"), (1, "#CFB584")]) + "</defs>")


def card():
    """The card of the windsocks: sky, far hills, the plain, and the three poles with their socks."""
    x, y, w, h = 8, 16, 254, 308
    hills = S.land_layer(U + "h1", S.ridge(7, x, x + w, 212, 14, step=4.0, peaks=0.5), 232, ("#8F9CC0", "#C1CBE0"), rim=False, haze=0.3, haze_colour="#E8F0FA")
    hills += S.land_layer(U + "h2", S.ridge(9, x, x + w, 226, 6, step=4.0), 234, ("#CDB085", "#E3CFA4"), rim=False, haze=0.1)
    ground = f'<rect x="{x}" y="230" width="{w}" height="{y + h - 230}" fill="url(#{U}gr)"/><line x1="{x}" y1="230.4" x2="{x + w}" y2="230.4" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.8"/>'
    grit = "".join(f'<ellipse cx="{n(x + 14 + i * 21 + (i % 3) * 5)}" cy="{n(240 + (i * 37) % 70)}" rx="{2 + i % 3}" ry="0.9" fill="#9A7F4F" opacity="0.30"/>' for i in range(11))
    return S.card(U + "cd", x, y, w, h, S.SKY_PALE, hills + ground + grit, 10.0)


def socks():
    out = []
    # three states: slack (hangs, a little blown), half-filled (about 50 degrees out), blown straight out (a hair below the level)
    out.append(H.windsock(U + "s1", 52, 230, length=46, angle=9, mouth=13, pole=53, taper=0.5, wobble=1.0, droop=0.0, seed=2))
    out.append(H.windsock(U + "s2", 128, 230, length=50, angle=52, mouth=15, pole=53, taper=0.56, wobble=0.3, droop=0.0, seed=4))
    out.append(H.windsock(U + "s3", 204, 230, length=52, angle=88, mouth=16, pole=53, taper=0.58, droop=0.07, flutter=0.4, seed=6))
    out.append(S.ribbon(U + "wd", [(30, 52), (110, 50), (190, 52), (224, 52)], 9, "#2F63C8", "#8DB3F2", head=2.0, tail=0.4))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the triangle
def labels():
    def word(s_, x, y, colour, height=12.5, anchor="start"):
        return (H.glyph_text(s_, x, y, height, "#FFFFFF", anchor=anchor, stroke="#FFFFFF", stroke_width=3.2, spacing=0.4)
                + H.glyph_text(s_, x, y, height, colour, anchor=anchor, stroke=colour, stroke_width=0.35, spacing=0.4))
    return "".join([word("300°", 306, 46, BLUE, 13, "end"), word("20", 392, 134, BLUE, 13.5), word("17", 310, 170.6, ORANGE, 13.5, "end"), word("10", 370, 253.2, RED, 13.5, "middle"),
                    word("30°", 340, 120, "#1F2937", 12)])


def triangle():
    out = []
    # the wind (solid) and its two parts (dashed lines under ribbons of the same colour, as the old figure drew them)
    out.append(f'<line x1="320" y1="58" x2="320" y2="226" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="5.4" stroke-dasharray="7 4"/><line x1="320" y1="58" x2="320" y2="226" stroke="{ORANGE}" stroke-width="2.4" stroke-dasharray="7 4"/>')
    out.append(f'<line x1="320" y1="231.2" x2="414" y2="231.2" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="5.4" stroke-dasharray="7 4"/><line x1="320" y1="231.2" x2="414" y2="231.2" stroke="{RED}" stroke-width="2.4" stroke-dasharray="7 4"/>')
    out.append(f'<polygon points="320,233.4 313.4,219.8 326.6,219.8" fill="{ORANGE}" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round"/><polygon points="422,231.2 408.4,224.6 408.4,237.8" fill="{RED}" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round"/>')
    out.append(S.ribbon(U + "w20", [(320, 58), (368, 141), (420, 231.2)], 6.4, "#1D4ED8", "#6FA0FF", head=2.1, tail=0.9, per=6))
    # the right angle and the 30 degrees
    out.append(f'<polyline points="320,219.2 332,219.2 332,231.2" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.2"/><polyline points="320,219.2 332,219.2 332,231.2" fill="none" stroke="#1F2937" stroke-width="1.2"/>')
    out.append(f'<path d="M 320,102 A 44,44 0 0 0 342,96.1" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.6"/><path d="M 320,102 A 44,44 0 0 0 342,96.1" fill="none" stroke="#1F2937" stroke-width="1.4"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the runway
def runway():
    x0, y0, w, h = 560, 34, 34, 282
    out = [f'<rect x="{x0 - 5}" y="{y0 - 5}" width="{w + 10}" height="{h + 10}" rx="2" fill="#BFAD84" opacity="0.5" filter="url(#{U}bl)"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#444" filter="url(#{U}as)"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="#10151D" stroke-opacity="0.5" stroke-width="0.5"/>']
    paint = "".join(f'<rect x="576.1" y="{y}" width="1.9" height="13"/>' for y in range(44, 240, 26))
    paint += "".join(f'<rect x="{x - 1.1}" y="302" width="2.2" height="12"/>' for x in (565, 570, 584, 589))
    paint += H.glyph_text("33", 577, 289, 11.5, PAINT, spacing=1.0, stroke=PAINT, stroke_width=0.4)
    out.append(f'<g fill="{PAINT}" filter="url(#{U}pw)">{paint}</g>')
    # the runway direction, up, with its number
    out.append(S.ribbon(U + "rd", [(577, 31), (577, 20), (577, 8)], 5.2, "#1F2937", "#566178", head=2.0, tail=0.9))
    out.append(H.glyph_text("330°", 584, 13, 12.5, "#FFFFFF", anchor="start", stroke="#FFFFFF", stroke_width=3.2, spacing=0.4) + H.glyph_text("330°", 584, 13, 12.5, "#1F2937", anchor="start", stroke="#1F2937", stroke_width=0.35, spacing=0.4))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 52, 258), c(2, 128, 258), c(3, 204, 258), c(4, 404, 166.6), c(5, 296, 194.6), c(6, 400, 253.2), c(7, 392, 108, 343, 100)])


def scenery():
    return S.scrub(61, 276, 520, 14, 40, 4, scale=0.85) + S.scrub(62, 436, 548, 120, 300, 6, scale=0.85) + S.scrub(63, 270, 300, 240, 330, 3, scale=0.85) + S.scrub(64, 600, 636, 40, 320, 3, scale=0.85)


def layers():
    return [{"name": "terrain-18-07", "at": [W / 2, HT / 2], "width": W}, defs(), scenery(), card(), socks(), runway(), triangle(), labels(), callouts()]


def plate():
    return {
        "id": "fig-18-07-crosswind",
        "replaces": "fig-18-07-crosswind.svg",
        "book_file": "plate-18-07-crosswind.jpg",
        "caption": "Figure 18-7. Reading the windsock, and splitting the wind into headwind and crosswind",
        "desc": "Figure 18-7. Reading the windsock, and splitting the wind into headwind and crosswind",
        "legend": [
            "Sock hanging down: calm or a light wind.",
            "Sock partly filled: a moderate wind.",
            "Sock straight out: a strong wind. In 1 to 3 the wind blows from the left.",
            "Wind from 300° at 20 kt.",
            "Headwind component, 17 kt.",
            "Crosswind component, 10 kt, from the left.",
            "The angle between the wind and the runway direction, 30°.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-07-crosswind.svg", "blank": True, "layers": layers()},
    }
