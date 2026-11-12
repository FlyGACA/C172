"""Figure 18-3. Runway markings at a normal runway end and at a displaced threshold. Two close-ups of paint on asphalt, lit from the upper left: the asphalt has its grain and its
blotches, the paint is a little worn and stands a hair off the surface (a thin shadow on its lower right edge), the blast pad is lighter. They lie on a desert plain
(figs/terrain.py) with the aeroplane of the model coming in at the left. The eleven callouts of the old figure are kept, in the same order and meaning (figs/scene.py makes the
callouts and the ribbon, figs/h_a2.py the asphalt and the paint)."""
from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 420
terrain.ensure("terrain-18-03", size=(W * 4, HT * 4), seed=183, kind="plain", features=("wadis", "tracks"), veil=0.34, soft=2.8)

U = "a183"
PAINT = "#F6F3EA"
YEL = "#F2BE1A"


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=6, relief=0.9, tone=0.0) + H.asphalt_filter(U + "ap", seed=15, relief=0.8, tone=0.95, blotch=0.4)
            + H.paint_filter(U + "pw", seed=12, wear=0.35, thickness=0.5) + H.paint_filter(U + "py", seed=22, wear=0.3, thickness=0.5)
            + H.blur_filter(U + "bl", 1.4) + H.blur_filter(U + "bs", 0.7) + H.shadow_filter(U + "sh", 1.0, 1.6, 1.0, 0.3) + "</defs>")


def slab(x, y, w, h, fid, shoulder=5.0):
    """A strip of pavement: a graded shoulder, then the asphalt with its thin edge."""
    return (f'<rect x="{H.n(x - shoulder)}" y="{H.n(y - shoulder)}" width="{H.n(w + 2 * shoulder)}" height="{H.n(h + 2 * shoulder)}" rx="2" fill="#BFAD84" opacity="0.5" filter="url(#{U}bl)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#444" filter="url(#{U}{fid})"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#10151D" stroke-opacity="0.45" stroke-width="0.5"/>')


def cracks(x0, x1, y0, y1, seed):
    """A few hairline cracks and a sealed joint across the asphalt: dark thin wandering lines."""
    import random
    rnd = random.Random(seed)
    out = []
    for _ in range(5):
        x = rnd.uniform(x0 + 20, x1 - 20)
        pts_, cx, cy = [], x, y0 + rnd.uniform(0, 8)
        while cy < y1 - 2:
            pts_.append((cx, cy))
            cx += rnd.uniform(-3.0, 3.0)
            cy += rnd.uniform(5, 12)
        pts_.append((cx, y1))
        out.append(f'<polyline points="{S.pts(pts_)}" fill="none" stroke="#0A0D13" stroke-opacity="0.32" stroke-width="0.45" stroke-linejoin="round"/>')
    return "".join(out)


def rubber(x0, x1, y_centre):
    out = []
    for y in (y_centre - 14, y_centre + 14):
        out.append(f'<rect x="{x0}" y="{y - 3}" width="{x1 - x0}" height="6" rx="3" fill="#0A0E15" opacity="0.11" filter="url(#{U}bl)"/>')
    return "".join(out)


def bars(x, ys, w, h):
    return "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for y in ys)


def first_strip():
    out = [slab(70, 44, 580, 112, "as"), cracks(70, 640, 44, 156, 3), rubber(214, 440, 100)]
    paint = []
    # side stripes
    paint.append('<rect x="70" y="46.5" width="580" height="3"/><rect x="70" y="150.5" width="580" height="3"/>')
    # threshold stripes, eight of them
    paint.append(bars(76, (50, 61, 72, 83, 110, 121, 132, 143), 40, 7))
    # centreline dashes
    paint.append("".join(f'<rect x="{x}" y="98" width="26" height="4"/>' for x in range(174, 640, 44)))
    # touchdown zone markings, the aiming point
    paint.append(bars(220, (60, 68, 76, 119.5, 127.5, 135.5), 24, 4.5))
    paint.append(bars(298, (60, 127), 64, 13))
    paint.append(bars(410, (60, 68, 127.5, 135.5), 24, 4.5))
    paint.append(bars(490, (60, 135.5), 24, 4.5))
    paint.append(bars(570, (60, 135.5), 24, 4.5))
    nums = H.glyph_text("09", 141, 100, 25, PAINT, rotate=90, spacing=3, stroke=PAINT, stroke_width=0.6)
    out.append(f'<g fill="{PAINT}" filter="url(#{U}pw)">{"".join(paint)}{nums}</g>')
    return "".join(out)


def second_strip():
    out = [slab(22, 236, 106, 112, "ap", 4.0), slab(128, 236, 522, 112, "as", 5.0), cracks(128, 640, 236, 348, 8), rubber(446, 560, 292)]
    # the blast pad is paved as the runway but lighter, with the yellow chevrons on it
    chev = "".join(f'<polyline points="{x},244 {x + 26},292 {x},340"/>' for x in (32, 62, 92))
    out.append(f'<g fill="none" stroke="{YEL}" stroke-width="6" stroke-linejoin="round" stroke-linecap="butt" filter="url(#{U}py)">{chev}</g>')
    paint = ['<rect x="128" y="238.5" width="522" height="3"/><rect x="128" y="342.5" width="522" height="3"/>']
    # the arrows that lead along the displaced part to the threshold, and the two arrowheads at its end
    for x in (142, 196, 250):
        paint.append(f'<rect x="{x}" y="290" width="30" height="4"/><polygon points="{x + 30},285 {x + 44},292 {x + 30},299"/>')
    paint.append('<polygon points="308,254 322,262 308,270"/><polygon points="308,314 322,322 308,330"/>')
    # the displaced threshold: a bar across the runway, the stripes after it, the designator, the centreline
    paint.append('<rect x="330" y="242" width="6" height="100"/>')
    paint.append(bars(342, (242, 253, 264, 275, 302, 313, 324, 335), 40, 7))
    paint.append("".join(f'<rect x="{x}" y="290" width="26" height="4"/>' for x in range(440, 650, 44)))
    paint.append(H.glyph_text("09", 407, 292, 25, PAINT, rotate=90, spacing=3, stroke=PAINT, stroke_width=0.6))
    out.append(f'<g fill="{PAINT}" filter="url(#{U}pw)">{"".join(paint)}</g>')
    return "".join(out)


def dimension(x0, x1, y, colour):
    """A double-headed dimension line with a white casing, and its two dashed extension lines."""
    return (f'<line x1="{x0 + 6}" y1="{y}" x2="{x1 - 6}" y2="{y}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.4" stroke-linecap="round"/>'
            f'<polygon points="{x0 - 1},{y} {x0 + 9},{y - 5.4} {x0 + 9},{y + 5.4}" fill="#FFFFFF" fill-opacity="0.9" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<polygon points="{x1 + 1},{y} {x1 - 9},{y - 5.4} {x1 - 9},{y + 5.4}" fill="#FFFFFF" fill-opacity="0.9" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<line x1="{x0 + 6}" y1="{y}" x2="{x1 - 6}" y2="{y}" stroke="{colour}" stroke-width="1.7" stroke-linecap="round"/>'
            f'<polygon points="{x0},{y} {x0 + 8},{y - 4.4} {x0 + 8},{y + 4.4}" fill="{colour}"/><polygon points="{x1},{y} {x1 - 8},{y - 4.4} {x1 - 8},{y + 4.4}" fill="{colour}"/>')


def dims():
    out = []
    for x, y0, y1 in ((128, 348, 380), (330, 348, 408)):
        out.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.2"/><line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="#2B3342" stroke-width="1" stroke-dasharray="3 3"/>')
    out.append(dimension(128, 632, 370, "#1F2937"))
    out.append(dimension(330, 632, 398, "#047857"))
    return "".join(out)


def scenery():
    return (S.scrub(31, 6, 64, 168, 232, 4, scale=0.85) + S.scrub(32, 150, 560, 6, 30, 5, scale=0.85) + S.scrub(33, 6, 120, 352, 412, 4, scale=0.85)
            + S.scrub(34, 420, 634, 356, 366, 2, scale=0.8) + S.scrub(35, 10, 60, 6, 40, 2, scale=0.85))


def aeroplane():
    plane = {"name": "sprite-top", "at": [30, 98], "width": 42, "angle": 90, "tint": "#2F66D6", "tint_strength": 0.62, "shadow": {"dx": 1.6, "dy": 2.6, "blur": 1.8, "opacity": 0.34}}
    arrow = S.ribbon(U + "ar", [(30, 134), (48, 134), (70, 134)], width=6, c1="#1D4ED8", c2="#5B8DF0", head=2.0)
    return plane, arrow


def callouts():
    c = S.callout
    return "".join([
        c(1, 96, 22, 96, 54), c(2, 140, 176, 143, 117), c(3, 200, 126, 200, 103), c(4, 232, 22, 232, 62.5), c(5, 330, 22, 330, 66.5), c(6, 470, 176, 470, 152),
        c(7, 64, 220, 48, 262), c(8, 208, 220, 211, 290.5), c(9, 333, 220, 333, 258), c(10, 238, 370), c(11, 480, 398)])


def layers():
    plane, arrow = aeroplane()
    return [{"name": "terrain-18-03", "at": [W / 2, HT / 2], "width": W}, defs(), scenery(), first_strip(), second_strip(), plane, arrow, dims(), callouts()]


def plate():
    return {
        "id": "fig-18-03-runway-markings",
        "replaces": "fig-18-03-runway-markings.svg",
        "book_file": "plate-18-03-runway-markings.jpg",
        "caption": "Figure 18-3. Runway markings at a normal runway end and at a displaced threshold",
        "desc": "Figure 18-3. Runway markings at a normal runway end and at a displaced threshold",
        "legend": [
            "Threshold stripes: the start of the part usable for landing; wider runways have more stripes.",
            "Designator, read from the approach.",
            "Centreline: keep the nose wheel on it.",
            "Touchdown zone marking: pairs of bars, with fewer bars further on.",
            "Aiming point: a target for the approach.",
            "Side stripe: the edge of the runway.",
            "Blast pad: yellow chevrons, not for use.",
            "Displaced part of the runway: white arrows lead to the threshold.",
            "Displaced threshold: a white bar across the runway, then the threshold stripes.",
            "Length available for takeoff, and for landing from the opposite direction.",
            "Length available for landing towards the displaced threshold.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-03-runway-markings.svg", "blank": True, "layers": layers()},
    }
