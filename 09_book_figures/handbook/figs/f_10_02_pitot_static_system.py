"""Figure 10-2. The pitot-static system and the instruments it feeds. A pitot tube under the wing facing the airstream (its open nose, its drain hole), a static port flush in the
fuselage skin, a cabin valve for the alternate static source, and the three instruments of the model themselves (the airspeed indicator on both lines, the altimeter and the vertical
speed indicator on the static line only), joined by a blue line for total pressure and a green line for static pressure. The instruments are the sprites of the twin (figs/sprites.py), the
rest is drawn by this module (figs/parts.py has the pipes, figs/scene.py the callouts); the seven numbered callouts of the old figure are kept."""
from figs import parts as P
from figs import scene as S

n = S.n
BLUE = ("#3F78D0", "#16356B", "#BBD6FA")
GREEN = ("#1FA971", "#0E5E3F", "#BFF0DA")
DIALS = {"asi": (300, 156), "alt": (420, 156), "vsi": (540, 156)}
DIAMETER = 98


def air():
    """The airstream meeting the pitot tube: translucent chevrons."""
    out = []
    for y in (30, 44, 58):
        for x in (2, 16):
            out.append(f'<path d="M {n(x)},{n(y - 6)} L {n(x + 9)},{n(y)} L {n(x)},{n(y + 6)}" fill="none" stroke="#7FB1F2" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>')
    return "".join(out)


def pitot():
    return (f'<g filter="url(#ptsh)"><rect x="64" y="-16" width="200" height="30" rx="14" fill="url(#ptsteelv)" stroke="#8A95A6" stroke-width="1.1"/>'
            f'<path d="M 100,14 L 118,14 L 114,38 L 104,38 Z" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/>'
            f'<path d="M 32,37 L 116,36 L 134,41 L 134,49 L 116,54 L 32,53 Q 24,50 24,45 Q 24,40 32,37 Z" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="1.1"/></g>'
            f'<rect x="38" y="39" width="76" height="3" rx="1.5" fill="#FFFFFF" opacity="0.7"/>'
            f'<ellipse cx="25" cy="45" rx="2.4" ry="5.6" fill="#16213A"/>'
            f'<ellipse cx="86" cy="52.4" rx="2.6" ry="1.9" fill="#16213A"/>'
            f'<rect x="118" y="38" width="14" height="12" rx="2" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="0.8"/>')


def static_port():
    return (f'<g filter="url(#ptsh)"><rect x="18" y="150" width="132" height="94" rx="16" fill="url(#ptsteelv)" stroke="#8A95A6" stroke-width="1.2"/></g>'
            + "".join(f'<circle cx="{n(x)}" cy="{n(y)}" r="1.5" fill="#8A95A6"/>' for x in (30, 138) for y in (162, 232))
            + f'<circle cx="84" cy="197" r="17" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1.2"/><circle cx="84" cy="197" r="11" fill="url(#ptsteelv)" stroke="#8A95A6" stroke-width="0.9"/>'
              f'<circle cx="84" cy="197" r="3" fill="#16213A"/><circle cx="75" cy="188" r="2" fill="#FFFFFF" opacity="0.7"/>')


def alternate_valve():
    return (f'<g filter="url(#ptsh)"><rect x="92" y="294" width="44" height="30" rx="6" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="1"/>'
            f'<rect x="136" y="302" width="26" height="14" rx="3" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="0.9"/></g>'
            f'<rect x="98" y="299" width="30" height="5" rx="2.5" fill="#FFFFFF" opacity="0.55"/>'
            f'<g transform="rotate(-24 114 294)"><rect x="110" y="272" width="8" height="24" rx="4" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.8"/><circle cx="114" cy="270" r="7.4" fill="url(#ptred)" stroke="#6E120D" stroke-width="0.9"/></g>'
            # cabin air going in
            f'<path d="M 54,309 h 28 m -8,-6 l 8,6 l -8,6" fill="none" stroke="#9FB2CC" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1 0"/>')


def lines():
    pitot_line = [(134, 44), (300, 44), (300, 108)]
    static_main = [(150, 197), (170, 197), (170, 258), (540, 258)]
    out = [P.tube(pitot_line, *BLUE, w=6.5), P.tube(static_main, *GREEN, w=6.5), P.tube([(162, 309), (210, 309), (210, 258)], *GREEN, w=6.5)]
    for x in (300, 420, 540):
        out.append(P.tube([(x, 258), (x, 204)], *GREEN, w=6.5))
    out += [P.chevrons(pitot_line, every=36), P.chevrons(static_main, every=36), P.chevrons([(162, 309), (210, 309), (210, 262)], every=30)]
    for x in (300, 420, 540):
        out.append(f'<circle cx="{n(x)}" cy="258" r="4" fill="#0E5E3F" stroke="#FFFFFF" stroke-width="1.2"/>')
    out.append(f'<circle cx="210" cy="258" r="4" fill="#0E5E3F" stroke="#FFFFFF" stroke-width="1.2"/>')
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 72, 92, 60, 49), c(2, 116, 96, 88, 55), c(3, 188, 222, 100, 204), c(4, 250, 318, 168, 312), c(5, 364, 92, 340, 118), c(6, 484, 92, 460, 118), c(7, 604, 92, 580, 118)])


def plate():
    return {
        "id": "fig-10-02-pitot-static-system",
        "replaces": "fig-10-02-pitot-static-system.svg",
        "book_file": "plate-10-02-pitot-static-system.jpg",
        "caption": "Figure 10-2. The pitot-static system and the instruments it feeds",
        "desc": "Figure 10-2. The pitot-static system and the instruments it feeds",
        "legend": [
            "Pitot tube, open to ram air at the front. The blue line carries total pressure.",
            "Drain hole.",
            "Static port. The green line carries static pressure.",
            "Alternate static source, a cabin valve that opens the static line to cabin air.",
            "Airspeed indicator, on both lines.",
            "Altimeter, static line only.",
            "Vertical speed indicator, static line only.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-10-02-pitot-static-system.svg", "blank": True,
                   "layers": [P.defs(), '<rect x="0" y="0" width="640" height="360" fill="url(#ptbg)"/>', air(), lines(), pitot(), static_port(), alternate_valve(),
                              {"name": "dial-31-04-asi", "at": list(DIALS["asi"]), "width": DIAMETER, "shadow": {"dx": 1.5, "dy": 3, "blur": 2.6, "opacity": 0.3}},
                              {"name": "dial-31-04-alt", "at": list(DIALS["alt"]), "width": DIAMETER, "shadow": {"dx": 1.5, "dy": 3, "blur": 2.6, "opacity": 0.3}},
                              {"name": "dial-31-04-vsi", "at": list(DIALS["vsi"]), "width": DIAMETER, "shadow": {"dx": 1.5, "dy": 3, "blur": 2.6, "opacity": 0.3}}, callouts()]},
    }
