"""Figure 21-1. VOR radials around a station, its identifier and its line-of-sight range. Drawn again as an illustrated picture on the old figure's canvas: the plan of the radials
on an aerial view of the country (figs/terrain.py), the station a hexagonal white building with a dome and its shadow, the radials light rays with a soft glow, the compass rose a
ring with ticks, the two courses ribbons with casings and the aeroplanes of the model larger; the identifier a lit panel; the line of sight a card with a section of the earth, the
station, the high ground and two aeroplanes. Every angle, number and callout of the old figure is kept (figs/h_a4.py has the parts)."""
from figs import h_a4 as H
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-21-01", size=(2560, 1640), seed=211, kind="plain", features=("scrub", "wadis", "tracks"), veil=0.3, soft=2.6)

CX, CY = 190.0, 222.0
R_IN, R_OUT = 132.0, 156.0


def plan():
    out = []
    # a pale disc under the plan, so that the rays stand out of the ground
    out.append(f'<defs><radialGradient id="a1d"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.22"/><stop offset="0.45" stop-color="#1B2B4A" stop-opacity="0.06"/><stop offset="1" stop-color="#1B2B4A" stop-opacity="0.40"/></radialGradient></defs>'
               f'<circle cx="{CX}" cy="{CY}" r="{R_IN}" fill="url(#a1d)"/>')
    # true north: the dashed line, tilted 9 degrees from magnetic north (the old figure's line, through the station)
    out.append('<line x1="210" y1="348.4" x2="160.6" y2="36.3" stroke="#FFFFFF" stroke-width="4.6" stroke-opacity="0.85" stroke-linecap="round"/>'
               '<line x1="210" y1="348.4" x2="160.6" y2="36.3" stroke="#3A4659" stroke-width="1.8" stroke-dasharray="7 5" stroke-linecap="butt"/>')
    # the twelve radials: light rays
    out.append(H.rays("a1y", CX, CY, range(0, 360, 30), 14, 129, w0=1.0, w1=2.8, a0=1.0, a1=0.72, glow=5.2, glow_opacity=0.62))
    # the compass ring
    labels = {0: "360", 30: "030", 60: "060", 90: "090", 120: "120", 150: "150", 180: "180", 210: "210", 240: "240", 270: "270", 300: "300", 330: "330"}
    out.append(H.bezel("a1z", CX, CY, R_IN, R_OUT, labels, bold={60, 240}))
    # the two courses: the 060 radial outbound and the 240 radial (ribbons with casings)
    for a in (60, 240):
        p0, p1 = H.polar(CX, CY, 30, a), H.polar(CX, CY, 118, a)
        out.append(H.ribbon(f"a1c{a}", [p0, p1], width=5.6, colours=H.BLUE, head=2.1))
    # magnetic north: the arrow above the ring
    out.append(H.ribbon("a1n", [(190, 62), (190, 30)], width=5.0, colours=("#16233D", "#4A5A78"), head=2.3))
    # the station
    out.append(H.vor_top("a1s", CX, CY, 1.32))
    return "".join(out)


def aeroplanes():
    a5 = H.polar(CX, CY, 80, 60)
    a4 = H.polar(CX, CY, 80, 240)
    return [H.plane(a4[0], a4[1], 56, 60), H.plane(a5[0], a5[1], 56, 60)]


def identifier():
    x, y, w, h = 374, 26, 222, 94
    out = [H.glass("a1i", x, y, w, h, r=9)]
    out.append(H.text(412, 64, "NKL", 25, "#FFFFFF", "bold", "middle", mono=True))
    # the Morse code of N K L (dash dot, dash dot dash, dot dash dot dot), lit capsules
    dash, dot, y0 = 14.4, 2.5, 59.0
    seq = [("-", 440), (".", 460.5), ("-", 482.6), (".", 503.1), ("-", 509.2), (".", 545.7), ("-", 551.8), (".", 572.3), (".", 580.9)]
    glow, crisp = [], []
    for kind, x0 in seq:
        if kind == "-":
            glow.append(f'<rect x="{S.n(x0 - 1.5)}" y="{S.n(y0 - 4)}" width="{S.n(dash + 3)}" height="8" rx="4" fill="#FFB52E"/>')
            crisp.append(f'<rect x="{S.n(x0)}" y="{S.n(y0 - 2.5)}" width="{S.n(dash)}" height="5" rx="2.5" fill="#FFD66E"/><rect x="{S.n(x0 + 1.5)}" y="{S.n(y0 - 1.6)}" width="{S.n(dash - 3)}" height="1.5" rx="0.75" fill="#FFF3C9" opacity="0.9"/>')
        else:
            glow.append(f'<circle cx="{S.n(x0)}" cy="{y0}" r="4.6" fill="#FFB52E"/>')
            crisp.append(f'<circle cx="{S.n(x0)}" cy="{y0}" r="{dot}" fill="#FFD66E"/><circle cx="{S.n(x0 - 0.6)}" cy="{y0 - 0.7}" r="1" fill="#FFF3C9"/>')
    out.append('<defs><filter id="a1ig" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur stdDeviation="2.4"/></filter></defs>'
               f'<g filter="url(#a1ig)" opacity="0.65">{"".join(glow)}</g>' + "".join(crisp))
    out.append(f'<line x1="{x + 14}" y1="82" x2="{x + w - 14}" y2="82" stroke="#FFFFFF" stroke-opacity="0.16" stroke-width="1"/>')
    out.append(H.text(412, 108, "VOR", 12.5, "#8DBBFF", "bold", "middle", mono=True))
    out.append(H.text(462, 108, "DME", 12.5, "#8DBBFF", "bold", "middle", mono=True))
    return "".join(out)


def line_of_sight():
    x, y, w, h = 374, 140, 250, 252
    sky = [(0.0, "#5E93D2"), (0.5, "#A9CBEC"), (0.82, "#E4EEF6"), (1.0, "#F6EFD9")]

    def ground_y(px):                                    # the earth's curve: a quadratic from (374, 358) over (499, 312) to (624, 358)
        t = (px - 374) / 250.0
        return (1 - t) ** 2 * 358 + 2 * t * (1 - t) * 312 + t * t * 358

    arc = "M 374,358 Q 499,312 624,358"
    body = [S.sun("a1sun", 402, 176, 8.5, halo=4.0)]
    # aeroplane 8 (behind the high ground) goes first, the mountain stands over its tail
    body.append("@@P8@@")
    # the high ground
    outline = [(498, 347), (509, 331), (520, 316), (531, 303), (540, 291), (548, 279), (556, 290), (565, 303), (574, 317), (583, 331), (594, 350)]
    rough = S.jag(outline, 1.4, 7, 3)
    body.append(S.rock("a1m", rough, 362, 498, 594, 5, tones=("#D8C49C", "#9C8460"), spine=[(548, 279), (545, 302), (551, 326), (557, 352)]))
    # the earth: a slab with the curve on top, lit sand over darker earth
    body.append(f'<defs>{S.gradient("a1e", [(0, "#EBD9A9"), (0.25, "#DCC590"), (1, "#8F774F")], 0, 316, 0, 392, "userSpaceOnUse")}</defs>'
                f'<path d="{arc} L 624,392 L 374,392 Z" fill="url(#a1e)"/>')
    for k, off in enumerate((13, 26, 40)):
        body.append(f'<path d="M 374,{358 + off} Q 499,{312 + off} 624,{358 + off}" fill="none" stroke="#4A3820" stroke-opacity="{0.12 + 0.03 * k:.2f}" stroke-width="{0.9 + 0.3 * k:.1f}"/>')
    body.append(f'<path d="{arc}" fill="none" stroke="#FFF7E0" stroke-opacity="0.85" stroke-width="1.3"/>')
    st, tip = H.vor_side("a1v", 410, 349.5, 1.35)
    body.append(st)
    return S.card("a1los", x, y, w, h, sky, "".join(body)), tip, ground_y


def plate():
    los, tip, _ = line_of_sight()
    tx, ty = tip[0], tip[1] + 1
    # the signals: green to the aeroplane in line of sight, red to the high ground
    green = H.ribbon("a1g", [(tx + 4, ty - 2), (575, 197)], width=2.6, colours=H.GREEN, head=2.4, casing=1.2, glow="#7BFFC8", shadow=False)
    red = (f'<line x1="{tx + 4}" y1="{ty}" x2="524" y2="311.5" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.75" stroke-linecap="round"/>'
           f'<line x1="{tx + 4}" y1="{ty}" x2="524" y2="311.5" stroke="#C4282B" stroke-width="2.2" stroke-dasharray="6 4" stroke-linecap="butt"/>'
           '<g stroke-linecap="round"><line x1="518" y1="305.5" x2="530" y2="317.5" stroke="#FFFFFF" stroke-width="5.6"/><line x1="518" y1="317.5" x2="530" y2="305.5" stroke="#FFFFFF" stroke-width="5.6"/>'
           '<line x1="518" y1="305.5" x2="530" y2="317.5" stroke="#C4282B" stroke-width="2.8"/><line x1="518" y1="317.5" x2="530" y2="305.5" stroke="#C4282B" stroke-width="2.8"/></g>')
    p7 = H.plane(592, 190, 54, 0, name="sprite-side")
    p8 = H.plane(591, 301, 54, 0, name="sprite-side")
    # the card is one string with a marker where aeroplane 8 goes (a sprite is an image and cannot sit inside the string): the pieces join again when the layers do
    head, _, rest = los.partition("@@P8@@")
    layers = [{"name": "terrain-21-01", "at": [320, 205], "width": 640}, plan(), *aeroplanes(), identifier(), head, p8, rest, green, red, p7]
    c = S.callout
    layers.append("".join([
        c(1, 216, 44, 193, 46), c(2, 138, 42, 165.5, 56),
        c(3, 174, 282, 186, 234), c(4, 110.8, 301.2, 124, 276), c(5, 269.2, 142.8, 266, 168),
        c(6, 616, 66, 592, 64), c(7, 480, 232, 487, 262), c(8, 606, 262, 600, 296),
    ]))
    return {
        "id": "fig-21-01-vor-radials",
        "replaces": "fig-21-01-vor-radials.svg",
        "book_file": "plate-21-01-vor-radials.jpg",
        "caption": "Figure 21-1. VOR radials around a station, its identifier and its line-of-sight range",
        "desc": "Figure 21-1. VOR radials around a station, its identifier and its line-of-sight range",
        "legend": [
            "Magnetic north, the reference for every radial.",
            "True north on a chart; the angle between them, exaggerated here, is the variation (Chapter 10). A chart's compass rose around a VOR is aligned with magnetic north.",
            "The station, a fictional VOR/DME.",
            "On the 240 radial, flying to the station: course 060.",
            "On the 060 radial, flying away from the station: also course 060.",
            "The identifier, `NKL`, in Morse code.",
            "In line of sight: a usable signal.",
            "Hidden by terrain or the earth's curve: no signal, and the warning flag appears.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {"svg": "fig-21-01-vor-radials.svg", "blank": True, "layers": layers},
    }
