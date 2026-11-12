"""Figure 18-2. Naming a runway from its magnetic direction. Left, a compass as a lit instrument ring (a dark bezel with its scale lit, a pane of frosted glass in it) over an aerial view of
the desert, with a runway of asphalt on it turned to 334 degrees, its numbers painted at the ends (33 and 15); magnetic north is a lit blue arrow, the angle clockwise from north an
orange ribbon. Above right, the two sums on a card; below it, two parallel runways with their numbers and letters painted (33L and 33R, and from the other end 15R and 15L) and the two
approaches as ribbons. The six numbered callouts of the old figure (3 and 4 twice, as it had them) are kept, in the same order and meaning (figs/scene.py makes the callouts and
the ribbons, figs/h_a2.py the asphalt, the paint and the painted numerals)."""
import math

from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 360
terrain.ensure("terrain-18-02", size=(W * 4, HT * 4), seed=182, kind="plain", features=("wadis", "tracks"), veil=0.32, soft=2.8)

U = "a182"
CX, CY = 165.0, 185.0
PAINT = "#F6F3EA"
n = S.n


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=6, relief=0.8, tone=0.0) + H.paint_filter(U + "pw", seed=12, wear=0.35, thickness=0.35)
            + H.blur_filter(U + "bl", 1.4) + H.blur_filter(U + "bg", 2.2) + H.blur_filter(U + "b3", 0.8) + H.shadow_filter(U + "sh", 0.0, 2.6, 3.4, 0.38, "#1A1208")
            + f'<radialGradient id="{U}rg" cx="0.36" cy="0.3" r="0.9"><stop offset="0" stop-color="#7C879B"/><stop offset="0.35" stop-color="#3A4457"/><stop offset="0.75" stop-color="#1A2030"/><stop offset="1" stop-color="#0E121C"/></radialGradient>'
            + f'<radialGradient id="{U}gl" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.10"/><stop offset="0.8" stop-color="#FFFFFF" stop-opacity="0.16"/><stop offset="1" stop-color="#1A2A44" stop-opacity="0.34"/></radialGradient>'
            + f'<linearGradient id="{U}rf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.55"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
            + "</defs>")


# ------------------------------------------------------------------------------------------------------------------ the runway pieces, in a runway's own frame (its middle at the origin, its far end at -y)
def end_marks(cx, number, letter, y_end):
    """The paint at one end: four short threshold bars, the number and (if any) the letter below it; for the end at -y the caller turns the whole thing round."""
    out = "".join(f'<rect x="{n(cx + dx - 0.9)}" y="{n(y_end - 7)}" width="1.8" height="7"/>' for dx in (-7, -4, 4, 7))
    out += H.glyph_text(number, cx, y_end - (28.3 if letter else 16.7), 8.6, PAINT, spacing=0.8, stroke=PAINT, stroke_width=0.3)
    if letter:
        out += H.glyph_text(letter, cx, y_end - 16.4, 8.6, PAINT, stroke=PAINT, stroke_width=0.3)
    return out


def runway(cx, width, half, bottom_text, top_text, uid):
    """A runway lying along y: its asphalt, its dashes, and the marks at both ends (bottom_text = (number, letter) read from the bottom end; top_text from the top end)."""
    x0 = cx - width / 2
    out = [f'<rect x="{n(x0 - 3)}" y="{n(-half - 3)}" width="{n(width + 6)}" height="{n(2 * half + 6)}" fill="#BFAD84" opacity="0.5" filter="url(#{U}bl)"/>',
           f'<rect x="{n(x0)}" y="{n(-half)}" width="{n(width)}" height="{n(2 * half)}" fill="#444" filter="url(#{U}as)"/>',
           f'<rect x="{n(x0)}" y="{n(-half)}" width="{n(width)}" height="{n(2 * half)}" fill="none" stroke="#10151D" stroke-opacity="0.5" stroke-width="0.5"/>']
    dashes = "".join(f'<rect x="{n(cx - 0.7)}" y="{n(y)}" width="1.4" height="7"/>' for y in range(-38, 40, 14)) if half < 80 else ""
    bottom = end_marks(cx, bottom_text[0], bottom_text[1], half)
    top = f'<g transform="rotate(180 {n(cx)} 0)">{end_marks(cx, top_text[0], top_text[1], half)}</g>'
    out.append(f'<g fill="{PAINT}" filter="url(#{U}pw)">{dashes}{bottom}{top}</g>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the compass
def polar(r, deg):
    a = math.radians(deg)
    return CX + r * math.sin(a), CY - r * math.cos(a)


def compass():
    out = []
    R_IN, R_OUT = 112.0, 134.0
    ring = (f"M {CX - R_OUT},{CY} A {R_OUT},{R_OUT} 0 1 0 {CX + R_OUT},{CY} A {R_OUT},{R_OUT} 0 1 0 {CX - R_OUT},{CY} Z "
            f"M {CX - R_IN},{CY} A {R_IN},{R_IN} 0 1 1 {CX + R_IN},{CY} A {R_IN},{R_IN} 0 1 1 {CX - R_IN},{CY} Z")
    # the window: frosted glass over the ground, with a darker rim
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{R_IN}" fill="#F4F1E4" opacity="0.30"/>')
    return out, ring, R_IN, R_OUT


def compass_top(ring, R_IN, R_OUT):
    """The bezel, its lit scale and numerals, the sheen on the glass (drawn over the runway)."""
    out = []
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{R_IN}" fill="url(#{U}gl)"/>')
    out.append(f'<path d="{ring}" fill="url(#{U}rg)" fill-rule="evenodd" filter="url(#{U}sh)"/>')
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{R_OUT - 0.5}" fill="none" stroke="#C9D2E2" stroke-opacity="0.8" stroke-width="0.9"/><circle cx="{CX}" cy="{CY}" r="{R_IN + 0.4}" fill="none" stroke="#050810" stroke-opacity="0.85" stroke-width="1.0"/>'
               f'<circle cx="{CX}" cy="{CY}" r="{R_IN + 1.2}" fill="none" stroke="#7E8CA8" stroke-opacity="0.7" stroke-width="0.6"/>')
    # the scale: a tick every 10 degrees, longer every 30, lit (a blurred copy under the crisp one)
    ticks = []
    for deg in range(0, 360, 10):
        major = deg % 30 == 0
        a, b = polar(R_IN + 1.8, deg), polar(R_IN + ((7.0 if deg % 90 == 0 else 10.0) if major else 5.6), deg)
        ticks.append(f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke-width="{1.4 if major else 0.9}"/>')
    out.append(f'<g stroke="#8CC8FF" stroke-opacity="0.85" stroke-linecap="round" filter="url(#{U}bg)" fill="none">{"".join(ticks)}</g><g stroke="#F4F8FF" stroke-linecap="round" fill="none">{"".join(ticks)}</g>')
    # the numerals of the four cardinal points, round the ring so that they read outwards
    for deg, text in ((0, "360"), (90, "090"), (180, "180"), (270, "270")):
        x, y = polar(126.0, deg)
        for blur in (True, False):
            g = H.glyph_text(text, x, y, 8.4, "#FFE9A8" if blur else "#FFFDF2", rotate=deg, spacing=0.8, stroke="#FFE9A8" if blur else None, stroke_width=0.6 if blur else 0)
            out.append(f'<g filter="url(#{U}bg)" opacity="0.8">{g}</g>' if blur else g)
    # a reflection on the glass
    out.append(f'<path d="M {CX - 98},{CY - 28} A 102,102 0 0 1 {CX - 30},{CY - 96} L {CX - 36},{CY - 72} A 80,80 0 0 0 {CX - 80},{CY - 30} Z" fill="url(#{U}rf)" opacity="0.45"/>')
    return "".join(out)


def runway_in_compass():
    return f'<g transform="translate({CX} {CY}) rotate(334)">{runway(0, 18, 78, ("33", ""), ("15", ""), "m")}</g>'


def arrows_left():
    out = []
    # magnetic north: a lit blue arrow from the middle
    out.append(S.ribbon(U + "n", [(CX, CY - 4), (CX, CY - 46), (CX, CY - 98)], 6.4, "#1D4ED8", "#6FA0FF", head=2.1, tail=0.8))
    # the angle clockwise from north: an orange ribbon that goes round to the runway
    arc = [(CX + 34 * math.sin(math.radians(a)), CY - 34 * math.cos(math.radians(a))) for a in range(0, 335, 12)] + [(CX + 34 * math.sin(math.radians(334)), CY - 34 * math.cos(math.radians(334)))]
    out.append(S.ribbon(U + "o", arc, 5.2, "#D9660F", "#F7A24E", head=2.0, tail=0.9, per=2))
    # the two directions, as dark arrows that leave the ring, with their numbers
    for (x0, y0, x1, y1) in ((124.7, 102.3, 103.3, 58.4), (205.3, 267.7, 226.7, 311.6)):
        line = [(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2), (x1, y1)]
        out.append(S.ribbon(U + f"c{int(x0)}", line, 6.4, "#FFFFFF", "#FFFFFF", head=1.9, tail=1.0, per=2, shadow=False, opacity=0.95))
        out.append(S.ribbon(U + f"d{int(x0)}", line, 3.6, "#1F2937", "#566178", head=2.2, tail=1.0, per=2))
    out.append(f'<g>{H.glyph_text("334°", 74.4, 53.4, 11.5, "#FFFFFF", stroke="#FFFFFF", stroke_width=3.0, spacing=0.4)}{H.glyph_text("334°", 74.4, 53.4, 11.5, "#1F2937", stroke="#1F2937", stroke_width=0.3, spacing=0.4)}</g>')
    out.append(f'<g>{H.glyph_text("154°", 255.6, 326.6, 11.5, "#FFFFFF", stroke="#FFFFFF", stroke_width=3.0, spacing=0.4)}{H.glyph_text("154°", 255.6, 326.6, 11.5, "#1F2937", stroke="#1F2937", stroke_width=0.3, spacing=0.4)}</g>')
    # the hub
    out.append(f'<circle cx="{CX}" cy="{CY}" r="4.2" fill="#B9C2D2" stroke="#2B3446" stroke-width="0.8"/><circle cx="{CX - 1}" cy="{CY - 1}" r="1.5" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the right-hand side
def panel():
    x, y, w, h = 356, 22, 266, 66
    out = [f'<defs><clipPath id="{U}pc"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></clipPath></defs>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" filter="url(#{U}sh)"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FBF9F2" fill-opacity="0.92"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="#FFFFFF" stroke-width="1.4"/>']
    for yy, text in ((42, "334 / 10 = 33.4 ≈ 33"), (72, "154 / 10 = 15.4 ≈ 15")):
        out.append(f'<text x="392" y="{yy + 5}" font-family="sans-serif" font-size="15" fill="#1F2937" text-anchor="start">{text}</text>')
    return "".join(out)


def parallel():
    g = f'<g transform="translate(500 212) rotate(334)">'
    g += runway(-24, 20, 84, ("33", "L"), ("15", "R"), "p1") + runway(24, 20, 84, ("33", "R"), ("15", "L"), "p2")
    g += "</g>"
    out = [g]
    # the approach to 33 from the south and to 15 from the north: ribbons in the runway frame
    out.append(f'<g transform="translate(500 212) rotate(334)">' + S.ribbon(U + "p5", [(-24, 134), (-24, 118), (-24, 98)], 6, "#1D4ED8", "#6FA0FF", head=2.0, tail=0.7)
               + S.ribbon(U + "p6", [(-24, -134), (-24, -118), (-24, -96)], 6, "#C2570C", "#F7A24E", head=2.0, tail=0.7) + "</g>")
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 187, 103), c(2, 195, 219), c(3, 221.7, 251.9), c(4, 108.3, 118.1), c(3, 372, 42), c(4, 372, 72), c(5, 512.8, 336), c(6, 404.1, 109.1)])


def scenery():
    return S.scrub(51, 330, 460, 100, 330, 6, scale=0.85) + S.scrub(52, 560, 634, 100, 340, 5, scale=0.85) + S.scrub(53, 6, 30, 20, 340, 4, scale=0.85)


def layers():
    face, ring, r_in, r_out = compass()
    return [{"name": "terrain-18-02", "at": [W / 2, HT / 2], "width": W}, defs(), scenery(), *face, runway_in_compass(), parallel(), compass_top(ring, r_in, r_out), arrows_left(), panel(), callouts()]


def plate():
    return {
        "id": "fig-18-02-runway-designators",
        "replaces": "fig-18-02-runway-designators.svg",
        "book_file": "plate-18-02-runway-designators.jpg",
        "caption": "Figure 18-2. Naming a runway from its magnetic direction",
        "desc": "Figure 18-2. Naming a runway from its magnetic direction",
        "legend": [
            "Magnetic north.",
            "The runway direction, 334°, measured clockwise from magnetic north.",
            "Landing towards 334°, you read `33` at the near end.",
            "Landing towards 154°, you read `15`.",
            "Approaching runway 33, the left runway is `33L` and the right one `33R`.",
            "From the other end, the same two runways are `15R` and `15L`.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-02-runway-designators.svg", "blank": True, "layers": layers()},
    }
