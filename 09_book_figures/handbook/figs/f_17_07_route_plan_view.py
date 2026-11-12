"""Figure 17-7. The worked example in plan view: a route round a restricted area. A map card on a pale aerial picture of the desert (figs/terrain.py, veil 0.4): the zones as tinted
areas with dashed or solid outlines (the control zone, the two steps of the terminal control area, the restricted area with its hatched edge, the danger area, the prohibited area, the
TFR), the route as a blue line with a white casing and arrowheads, the direct line (grey, dashed, rejected) with its cross, and the places as symbols (the two aerodromes, the reporting point
WADI as a triangle, the turning point T as a ring), a north arrow and a scale of 10 NM. The eleven numbered callouts of the old figure are kept, in the same order and meaning
(figs/scene.py makes the card and the callouts, figs/h_a2.py the letters)."""
from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 400
terrain.ensure("terrain-17-07", size=(W * 4, HT * 4), seed=177, kind="plain", features=("wadis",), veil=0.40, soft=3.0)

U = "a177"
BLUE, RED, ORANGE, INK = "#1D4ED8", "#B91C1C", "#B45309", "#1F2937"
n = S.n
CARD = (12, 12, 616, 376)


def pts(points):
    return S.pts(points)


def defs():
    x, y, w, h = CARD
    return ("<defs>" + f'<clipPath id="{U}cc"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></clipPath>' + H.shadow_filter(U + "cs", 0, 2.4, 3.4, 0.30, "#10233F")
            + H.shadow_filter(U + "ss", 0.8, 1.4, 1.1, 0.35) + S.gradient(U + "bg", [(0, "#F7FAFE"), (1, "#E4EDF7")]) + S.gradient(U + "ap", [(0, "#FFFFFF"), (1, "#DDE3EC")], 0, 0, 1, 1)
            + S.gradient(U + "rw", [(0, "#4A5260"), (1, "#1C222D")], 0, 0, 1, 1) + "</defs>")


def card_back():
    x, y, w, h = CARD
    return (f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" filter="url(#{U}cs)"/>')


def casing(shape, width, extra=""):
    """A white casing under a line: the same shape (an SVG element without its closing) drawn wider in white."""
    return shape.replace("@@W@@", n(width)).replace("@@C@@", "#FFFFFF") + extra


def zones():
    out = []
    cx, cy = 190, 222
    # the terminal control area: two steps (tinted discs, dashed outlines), the control zone from the ground (solid)
    out.append(f'<circle cx="{cx}" cy="{cy}" r="140" fill="#2F66EA" fill-opacity="0.13"/><circle cx="{cx}" cy="{cy}" r="98" fill="#2F66EA" fill-opacity="0.15"/><circle cx="{cx}" cy="{cy}" r="56" fill="#2F66EA" fill-opacity="0.32"/>')
    for r in (140, 98):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.6"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BLUE}" stroke-width="1.9" stroke-dasharray="9 5"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="56" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.8"/><circle cx="{cx}" cy="{cy}" r="56" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    # the restricted area, with the ticks of a hatched edge
    r_ = [(355, 150), (445, 146), (452, 212), (362, 222)]
    out.append(f'<polygon points="{pts(r_)}" fill="#D32F2F" fill-opacity="0.16"/>')
    out.append(f'<polygon points="{pts(r_)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="9" stroke-linejoin="round"/>'
               f'<polygon points="{pts(r_)}" fill="none" stroke="{RED}" stroke-width="7" stroke-dasharray="1.5 3.5" stroke-opacity="0.85"/><polygon points="{pts(r_)}" fill="none" stroke="{RED}" stroke-width="1.7" stroke-linejoin="round"/>')
    # the danger area
    d_ = [(465, 305), (540, 300), (548, 352), (472, 358)]
    out.append(f'<polygon points="{pts(d_)}" fill="#F59E3B" fill-opacity="0.26"/><polygon points="{pts(d_)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.8" stroke-linejoin="round"/>'
               f'<polygon points="{pts(d_)}" fill="none" stroke="{ORANGE}" stroke-width="2.2" stroke-dasharray="6 4" stroke-linejoin="round"/>')
    # the prohibited area and the TFR
    out.append(f'<circle cx="330" cy="58" r="18" fill="#D32F2F" fill-opacity="0.22"/><circle cx="330" cy="58" r="18" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="5.4"/><circle cx="330" cy="58" r="18" fill="none" stroke="{RED}" stroke-width="2.5"/>')
    out.append(f'<circle cx="540" cy="75" r="28" fill="#D32F2F" fill-opacity="0.08"/><circle cx="540" cy="75" r="28" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.8"/><circle cx="540" cy="75" r="28" fill="none" stroke="{RED}" stroke-width="2.2" stroke-dasharray="5 4"/>')
    return "".join(out)


def letters():
    def word(s_, x, y, colour, height):
        return H.glyph_text(s_, x, y, height, "#FFFFFF", stroke="#FFFFFF", stroke_width=3.0, spacing=0.6) + H.glyph_text(s_, x, y, height, colour, stroke=colour, stroke_width=0.35, spacing=0.6)
    return "".join([word("CTR", 172, 254, BLUE, 9.5), word("TMA", 170, 100, BLUE, 9.5), word("R", 420, 163, RED, 13.5), word("D", 507, 330, ORANGE, 13.5), word("P", 330, 58, RED, 12)])


def direct_line():
    out = [f'<line x1="190" y1="222" x2="585" y2="170" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="5.6"/><line x1="190" y1="222" x2="585" y2="170" stroke="#6B7280" stroke-width="2.2" stroke-dasharray="5 5"/>',
           f'<g stroke-linecap="round"><line x1="393.7" y1="187.7" x2="406.3" y2="200.3" stroke="#FFFFFF" stroke-width="6.4"/><line x1="393.7" y1="200.3" x2="406.3" y2="187.7" stroke="#FFFFFF" stroke-width="6.4"/>'
           f'<line x1="393.7" y1="187.7" x2="406.3" y2="200.3" stroke="#6B7280" stroke-width="3"/><line x1="393.7" y1="200.3" x2="406.3" y2="187.7" stroke="#6B7280" stroke-width="3"/></g>']
    return "".join(out)


def route():
    line = "190,222 246,222 415,262 585,170"
    out = [f'<polyline points="{line}" fill="none" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="7.4" stroke-linejoin="round" stroke-linecap="round"/>',
           f'<polyline points="{line}" fill="none" stroke="#1D3FA8" stroke-width="4.4" stroke-linejoin="round" stroke-linecap="round"/>',
           f'<polyline points="{line}" fill="none" stroke="{BLUE}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>',
           f'<polyline points="{line}" fill="none" stroke="#8FB2FF" stroke-opacity="0.7" stroke-width="0.9" stroke-linejoin="round" stroke-linecap="round" transform="translate(-0.5 -0.8)"/>']
    for tri in ("337.3,243.6 325.2,247.0 327.9,235.2", "506.8,212.3 500.0,222.9 494.2,212.2"):
        out.append(f'<polygon points="{tri}" fill="{BLUE}" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round"/>')
    return "".join(out)


def aerodrome(cx, cy, r, bar):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{U}ap)" stroke="{INK}" stroke-width="1.7" filter="url(#{U}ss)"/>'
            f'<polygon points="{pts(bar)}" fill="url(#{U}rw)" stroke="#0B0F16" stroke-width="0.5"/>'
            f'<polyline points="{pts([(cx - r * 0.7, cy - r * 0.35), (cx - r * 0.2, cy - r * 0.8)])}" fill="none" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="1" stroke-linecap="round"/>')


def places():
    out = []
    out.append(aerodrome(190, 222, 15, [(181.4, 231.0), (202.1, 219.0), (198.6, 213.0), (177.9, 225.0)]))
    out.append(aerodrome(585, 170, 14, [(582.5, 181.3), (593.5, 162.2), (587.5, 158.7), (576.5, 177.8)]))
    # the reporting point WADI (a triangle) and the turning point T (a ring)
    out.append(f'<polygon points="246,213 254,228 238,228" fill="#FFFFFF" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round" filter="url(#{U}ss)"/>')
    out.append(f'<circle cx="415" cy="262" r="5.4" fill="#FFFFFF" stroke="{INK}" stroke-width="2.2" filter="url(#{U}ss)"/>')
    return "".join(out)


def north_and_scale():
    out = [S.ribbon(U + "na", [(606, 372), (606, 355), (606, 334)], 7, "#1F2937", "#566178", head=2.0, tail=0.8)]
    out.append(H.glyph_text("N", 606, 322, 12.5, "#FFFFFF", stroke="#FFFFFF", stroke_width=3.0) + H.glyph_text("N", 606, 322, 12.5, INK, stroke=INK, stroke_width=0.4))
    out.append(f'<g stroke-linecap="round"><line x1="30" y1="372" x2="100" y2="372" stroke="#FFFFFF" stroke-width="7"/><line x1="30" y1="366" x2="30" y2="378" stroke="#FFFFFF" stroke-width="5.4"/><line x1="100" y1="366" x2="100" y2="378" stroke="#FFFFFF" stroke-width="5.4"/>'
               f'<line x1="30" y1="372" x2="100" y2="372" stroke="{INK}" stroke-width="3"/><line x1="30" y1="366" x2="30" y2="378" stroke="{INK}" stroke-width="2"/><line x1="100" y1="366" x2="100" y2="378" stroke="{INK}" stroke-width="2"/></g>')
    out.append(H.glyph_text("10", 65, 360, 11, "#FFFFFF", stroke="#FFFFFF", stroke_width=3.0, spacing=0.6) + H.glyph_text("10", 65, 360, 11, INK, stroke=INK, stroke_width=0.35, spacing=0.6))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 160, 198), c(2, 102, 142), c(3, 248, 198), c(4, 413, 286), c(5, 466, 140), c(6, 562, 364), c(7, 358, 50), c(8, 580, 58), c(9, 589, 200), c(10, 338, 174, 346, 201), c(11, 118, 372)])


def scrub():
    return S.scrub(71, 26, 120, 24, 70, 3, scale=0.85) + S.scrub(72, 40, 170, 330, 366, 3, scale=0.85) + S.scrub(73, 590, 620, 200, 300, 2, scale=0.85) + S.scrub(74, 250, 330, 330, 366, 2, scale=0.85)


def layers():
    return [defs(), card_back(), f'<g clip-path="url(#{U}cc)">', {"name": "terrain-17-07", "at": [W / 2, HT / 2], "width": W}, scrub(), "</g>",
            f'<rect x="{CARD[0]}" y="{CARD[1]}" width="{CARD[2]}" height="{CARD[3]}" rx="8" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>',
            zones(), direct_line(), route(), places(), letters(), north_and_scale(), callouts()]


def plate():
    return {
        "id": "fig-17-07-route-plan-view",
        "replaces": "fig-17-07-route-plan-view.svg",
        "book_file": "plate-17-07-route-plan-view.jpg",
        "caption": "Figure 17-7. The worked example in plan view: a route round a restricted area",
        "desc": "Figure 17-7. The worked example in plan view: a route round a restricted area",
        "legend": [
            "Control zone of A, Class D.",
            "TMA, Class C, two steps.",
            "Point WADI, leaving the zone.",
            "Turning point T.",
            "Restricted area R.",
            "Danger area D.",
            "Prohibited area P.",
            "The TFR.",
            "Aerodrome B.",
            "The direct line, rejected.",
            "Scale: 10 NM.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-17-07-route-plan-view.svg", "blank": True, "layers": layers()},
    }
