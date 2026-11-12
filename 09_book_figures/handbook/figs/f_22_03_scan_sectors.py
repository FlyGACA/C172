"""Figure 22-3. A block scan through the windscreen and side windows. The view from the cockpit: a rubber-edged frame with its two window posts, the glass showing the sky, far hills and the
plain, the eighteen blocks of the scan as soft translucent cells in two rows (each with its dwell point as a glowing dot; the first row scanned one way, the second the other, as ribbons
of small arrows), the horizon, a bracket of 10 degrees, the red aircraft that one post hides, the hump of the glareshield and the instrument panel below with the model's own instruments
(figs/sprites.py) and engine gauges, and the two arrows that take the eye in and back out. The seven numbered callouts of the old figure are kept, in the same order and meaning
(figs/scene.py makes the callouts and the ribbons, figs/parts.py the gauges, figs/h_a2.py the lamps and the letters)."""
from figs import h_a2 as H
from figs import parts as P
from figs import scene as S

W, HT = 640, 360
U = "a223"
n = S.n
CELL_W, CELL_H = 30, 36


def defs():
    return ("<defs>" + H.lamp_defs(U + "l") + H.blur_filter(U + "b1", 1.1) + H.blur_filter(U + "b2", 2.6) + H.shadow_filter(U + "ms", 0.5, 0.9, 0.7, 0.35, "#0A1424") + H.shadow_filter(U + "ps", 0, 2.6, 3.4, 0.35, "#0A1220")
            + S.gradient(U + "bg", [(0, "#F7FAFE"), (1, "#E4EDF7")]) + S.gradient(U + "pl", [(0, "#E6D4A6"), (0.6, "#D3B986"), (1, "#B7996A")]) + S.gradient(U + "fr", [(0, "#3A4458"), (1, "#10141C")])
            + S.gradient(U + "pn", [(0, "#4A5366"), (0.4, "#262D3B"), (1, "#141923")]) + S.gradient(U + "hp", [(0, "#454E62"), (1, "#0D1017")])
            + S.gradient(U + "po", [(0, "#596378"), (0.5, "#2B3242"), (1, "#151A24")], 0, 0, 1, 0)
            + '<clipPath id="' + U + 'gc"><rect x="32" y="44" width="576" height="192" rx="3"/></clipPath>' + "</defs>")


def glass():
    """The view through the windscreen: sky, hills, plain, horizon."""
    out = [f'<g clip-path="url(#{U}gc)">', f'<defs>{S.gradient(U + "sk", [(0, "#6E9FD6"), (0.5, "#A9CBEC"), (1, "#E6F0FA")])}</defs>',
           f'<rect x="32" y="44" width="576" height="113" fill="url(#{U}sk)"/>',
           S.land_layer(U + "h1", S.ridge(5, 32, 608, 150, 16, step=4.0, peaks=0.5), 158, ("#8F9DC2", "#C3CEE3"), rim=False, haze=0.30, haze_colour="#EAF1FA"),
           S.land_layer(U + "h2", S.ridge(9, 32, 608, 154, 6, step=3.0), 158, ("#C9AE82", "#E0CDA2"), rim=False, haze=0.12),
           f'<rect x="32" y="156" width="576" height="82" fill="url(#{U}pl)"/>',
           f'<line x1="32" y1="156.4" x2="608" y2="156.4" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="1"/>',
           S.scrub(11, 34, 606, 160, 232, 26, scale=0.62),
           "</g>"]
    return "".join(out)


def cells():
    """Eighteen blocks in two rows: soft translucent cells with their dwell points, and the arrows of the two sweeps."""
    out = []
    for k in range(18):
        x = 33 + 32 * k
        for y in (102, 138):
            out.append(f'<rect x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" rx="3" fill="#BFD6FF" fill-opacity="0.13" stroke="#FFFFFF" stroke-opacity="0.72" stroke-width="0.9"/>'
                       f'<rect x="{x + 1}" y="{y + 1}" width="{CELL_W - 2}" height="{CELL_H - 2}" rx="2.4" fill="none" stroke="#3B6FE0" stroke-opacity="0.45" stroke-width="0.6"/>')
    return "".join(out)


def horizon():
    return f'<line x1="32" y1="156.4" x2="608" y2="156.4" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="1.3"/>'


def dots():
    out = []
    for k in range(18):
        x = 48 + 32 * k
        for y in (120, 156):
            out.append(H.lamp(U + "l", x, y, 2.6, "blue", 3.0, 0.9))
    return "".join(out)


def mini_arrow(x0, x1, y, colour, c2):
    """A small flat arrow (a bar and a head) from x0 to x1 with a gradient and a soft shadow."""
    d = 1 if x1 > x0 else -1
    head = 6.4
    hx = x1 - d * head
    p = [(x0, y - 1.5), (hx, y - 1.5), (hx, y - 4.0), (x1, y), (hx, y + 4.0), (hx, y + 1.5), (x0, y + 1.5)]
    return f'<polygon points="{S.pts(p)}" fill="{colour}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="0.7" stroke-linejoin="round" filter="url(#{U}ms)"/>'


def arrows():
    out = []
    for k in range(18):
        x = 33 + 32 * k
        out.append(mini_arrow(x + 27, x + 4, 110, "#E8782E", "#F8BE73"))
        out.append(mini_arrow(x + 3, x + 26, 166, "#2F63C8", "#8DB3F2"))
    out.append(S.ribbon(U + "up", [(598, 152), (598, 140), (598, 126)], 4.6, "#2F63C8", "#8DB3F2", head=2.0, tail=0.8))
    return "".join(out)


def aeroplane_behind_post():
    return {"name": "sprite-front", "at": [527.4, 130.0], "width": 38, "tint": "#FF6A5A", "tint_strength": 0.92, "outline": {"width": 0.5, "colour": "#7A1010", "opacity": 0.75}}


def frame():
    """The rubber-edged frame, the posts and the glass's sheen (drawn over the glass and the cells)."""
    out = [f'<polygon points="{S.pts([(60, 44), (112, 44), (84, 236), (32, 236)])}" fill="#FFFFFF" fill-opacity="0.08"/>',
           f'<polygon points="{S.pts([(300, 44), (330, 44), (238, 236), (208, 236)])}" fill="#FFFFFF" fill-opacity="0.06"/>',
           f'<polygon points="{S.pts([(470, 44), (480, 44), (400, 236), (390, 236)])}" fill="#FFFFFF" fill-opacity="0.05"/>']
    out.append(f'<rect x="20" y="30" width="600" height="14" fill="url(#{U}fr)"/><rect x="20" y="30" width="12" height="206" fill="url(#{U}fr)"/><rect x="608" y="30" width="12" height="206" fill="url(#{U}fr)"/><rect x="20" y="232" width="600" height="6" fill="url(#{U}fr)"/>')
    out.append(f'<rect x="19.4" y="29.4" width="601.2" height="209.2" rx="4" fill="none" stroke="#050810" stroke-width="1.2"/><rect x="32" y="44" width="576" height="188" rx="3" fill="none" stroke="#7D89A5" stroke-opacity="0.45" stroke-width="0.8"/>')
    for x in (121.6, 505.6):
        out.append(f'<rect x="{x}" y="44" width="12.8" height="192" fill="url(#{U}po)"/><rect x="{x + 1}" y="44" width="1.8" height="192" fill="#9AA6C0" opacity="0.5"/><rect x="{x - 0.4}" y="44" width="13.6" height="192" fill="none" stroke="#050810" stroke-opacity="0.7" stroke-width="0.6"/>')
    return "".join(out)


def panel():
    out = [f'<path d="M 236,236 Q 320,202 404,236 Z" fill="url(#{U}hp)"/><path d="M 244,235 Q 320,207 396,235" fill="none" stroke="#9AA9C8" stroke-opacity="0.45" stroke-width="1"/>',
           f'<rect x="122" y="236" width="396" height="112" rx="6" fill="url(#{U}pn)" stroke="#05080F" stroke-width="1.6" filter="url(#{U}ps)"/><rect x="123.5" y="237.5" width="393" height="109" rx="5" fill="none" stroke="#8592B0" stroke-opacity="0.35" stroke-width="0.8"/>']
    return "".join(out)


def instruments():
    """The model's instruments (airspeed, attitude, altimeter | gauge, heading, vertical speed) in the top row, six small engine gauges below."""
    sprites = [{"name": "dial-31-04-asi", "at": [176, 276], "width": 40}, {"name": "dial-31-04-ai", "at": [230, 276], "width": 40}, {"name": "dial-31-04-alt", "at": [284, 276], "width": 40},
               {"name": "dial-09-03-dg", "at": [410, 276], "width": 40}, {"name": "dial-31-04-vsi", "at": [464, 276], "width": 40}]
    vector = P.dial_vector(356, 276, 19, needle_deg=18, arc=(-60, 60, "#2F8F5B"))
    small = "".join(P.dial_vector(x, 326, 16.5, needle_deg=nd, arc=arc) for x, nd, arc in ((176, -35, (-60, 20, "#2F8F5B")), (230, 20, (30, 90, "#D9A21B")), (284, 45, (-90, 10, "#2F8F5B")),
                                                                                    (356, -10, (-70, 40, "#2F8F5B")), (410, 60, (50, 100, "#C0392B")), (464, -50, (-90, -20, "#D9A21B"))))
    return sprites, vector, small


def bracket_and_arrows():
    out = []
    out.append(f'<g stroke-linecap="round"><line x1="321" y1="94" x2="351" y2="94" stroke="#FFFFFF" stroke-width="4.6"/><line x1="321" y1="89" x2="321" y2="99" stroke="#FFFFFF" stroke-width="4.2"/><line x1="351" y1="89" x2="351" y2="99" stroke="#FFFFFF" stroke-width="4.2"/>'
               f'<line x1="321" y1="94" x2="351" y2="94" stroke="#1F2937" stroke-width="1.6"/><line x1="321" y1="90" x2="321" y2="98" stroke="#1F2937" stroke-width="1.6"/><line x1="351" y1="90" x2="351" y2="98" stroke="#1F2937" stroke-width="1.6"/></g>')
    out.append(H.glyph_text("10°", 336, 84, 11.5, "#FFFFFF", stroke="#FFFFFF", stroke_width=3.2, spacing=0.4) + H.glyph_text("10°", 336, 84, 11.5, "#1F2937", stroke="#1F2937", stroke_width=0.35, spacing=0.4))
    # the eye goes down to the instruments and back out
    out.append(S.ribbon(U + "d1", [(310, 254), (310, 220), (310, 184)], 5.0, "#1F2937", "#566178", head=2.0, tail=0.8))
    out.append(S.ribbon(U + "d2", [(330, 182), (330, 216), (330, 254)], 5.0, "#1F2937", "#566178", head=2.0, tail=0.8))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 48, 206, 48, 160), c(2, 294, 78, 322, 92), c(3, 240, 212, 240, 160), c(4, 578, 78, 519, 78), c(5, 282, 240, 306, 234), c(6, 176, 70, 176, 112), c(7, 560, 206, 569.6, 157)])


def layers():
    sprites, vector, small = instruments()
    out = [defs(), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>', P.defs(), f'<rect x="20" y="30" width="600" height="208" rx="4" fill="#10141C"/>', glass(), cells(), horizon(), arrows(), dots(),
           aeroplane_behind_post(), frame(), panel(), *sprites, vector, small, bracket_and_arrows(), callouts()]
    return out


def plate():
    return {
        "id": "fig-22-03-scan-sectors",
        "replaces": "fig-22-03-scan-sectors.svg",
        "book_file": "plate-22-03-scan-sectors.jpg",
        "caption": "Figure 22-3. A block scan through the windscreen and side windows",
        "desc": "Figure 22-3. A block scan through the windscreen and side windows",
        "legend": [
            "Start at one side.",
            "One block, about 10° wide.",
            "Dwell point: look for at least 1 second.",
            "Window post: it can hide an aircraft, here the red one. Move your head to look past it.",
            "A short look at the instruments, then back outside.",
            "A second row, above the horizon, scanned back the other way.",
            "The horizon. An aircraft at your level appears on or near it; one above you, above it; one below, below it.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-22-03-scan-sectors.svg", "blank": True, "layers": layers()},
    }
