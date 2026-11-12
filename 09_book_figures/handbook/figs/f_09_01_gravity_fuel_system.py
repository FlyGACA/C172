"""Figure 9-1. A high-wing gravity-feed fuel system. The wing cut away to show its two tanks (the fuel and its level, the filler caps on top, a vent from each, a sump drain under each),
the lines that fall from the tanks to the fuel selector valve, the strainer at the lowest point with its glass bowl and quick drain, the primer on the line, and the carburettor on the
engine (seen from above, a flat four), below the tanks. The drawing is made by this module (figs/parts.py has the pipes and the fittings, figs/scene.py the callouts); the seven numbered
callouts of the old figure are kept."""
import math

from figs import parts as P
from figs import scene as S

n = S.n
AMBER = ("#EBA53A", "#8F5A12", "#FFE6AE")
DY = 18.0


def tank(x0, x1, level_y, seed):
    y0, y1 = 34.0, 92.0
    wave = "".join(f" Q {n(x0 + 12 + i * 26 + 6.5)},{n(level_y + (2.0 if i % 2 else -2.0))} {n(x0 + 12 + (i + 1) * 26)},{n(level_y)}" for i in range(int((x1 - x0 - 24) / 26)))
    return (f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" rx="12" fill="url(#ptcav)"/>'
            f'<path d="M {n(x0)},{n(level_y)}{wave} L {n(x1)},{n(level_y)} L {n(x1)},{n(y1 - 10)} Q {n(x1)},{n(y1)} {n(x1 - 10)},{n(y1)} L {n(x0 + 10)},{n(y1)} Q {n(x0)},{n(y1)} {n(x0)},{n(y1 - 10)} Z" fill="url(#ptfuel)"/>'
            f'<path d="M {n(x0 + 4)},{n(level_y + 1)}{wave}" fill="none" stroke="#FFF2C9" stroke-width="1.2" stroke-opacity="0.9"/>'
            f'<rect x="{n(x0 + 6)}" y="{n(y0 + 3)}" width="{n(x1 - x0 - 12)}" height="4" rx="2" fill="#FFFFFF" opacity="0.14"/>')


def wing():
    out = [f'<g filter="url(#ptsh)"><rect x="18" y="20" width="604" height="84" rx="28" fill="url(#ptsteelv)" stroke="#8A95A6" stroke-width="1.2"/></g>',
           '<rect x="26" y="23" width="588" height="5" rx="2.5" fill="#FFFFFF" opacity="0.75"/>',
           tank(48, 268, 58, 1), tank(372, 592, 58, 2)]
    # filler caps and their necks, on top of the tanks
    for cx in (104, 536):
        out.append(f'<rect x="{n(cx - 7)}" y="22" width="14" height="14" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.8"/>'
                   f'<ellipse cx="{n(cx)}" cy="21" rx="16" ry="5.6" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1"/><ellipse cx="{n(cx)}" cy="20.4" rx="10.5" ry="3.6" fill="url(#ptred)" stroke="#6E120D" stroke-width="0.8"/>'
                   f'<rect x="{n(cx - 6)}" y="19.2" width="12" height="2" rx="1" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(out)


def vents_and_drains():
    out = []
    for side, x_in, x_out in ((1, 56, 34), (-1, 584, 606)):
        out.append(P.tube([(x_in, 38), (x_out, 38), (x_out, 112)], "#C9D1DC", "#5A6578", "#FFFFFF", w=4.6))
        out.append(f'<path d="M {n(x_out - 3.6)},112 L {n(x_out + 3.6)},112 L {n(x_out + 3.6 + side * 2.6)},118 L {n(x_out - 3.6 + side * 2.6)},118 Z" fill="#2F3B4E" stroke="#5A6578" stroke-width="0.8"/>')
    for x in (262, 378):
        out.append(f'<rect x="{n(x - 3)}" y="92" width="6" height="13" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.7"/>' + P.hex_nut(x, 108, 6.0) + f'<rect x="{n(x - 2)}" y="112" width="4" height="8" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.7"/><circle cx="{n(x)}" cy="123" r="3.8" fill="url(#ptred)" stroke="#6E120D" stroke-width="0.8"/>')
    return "".join(out)


def lines():
    left = [(246, 92), (246, 122), (292, 152)]
    right = [(394, 92), (394, 122), (348, 152)]
    down = [(320, 192), (320, 238)]
    main = [(338, 258), (452, 258)]
    out = [P.tube(left, *AMBER, w=7), P.tube(right, *AMBER, w=7), P.tube(down, *AMBER, w=7), P.tube(main, *AMBER, w=7)]
    out += [P.chevrons(left + [(300, 158)], every=24), P.chevrons(right + [(340, 158)], every=24), P.chevrons(down, every=22), P.chevrons(main, every=30)]
    return "".join(out)


def selector():
    cx, cy = 320.0, 172.0
    return (f'<g filter="url(#ptsh)"><path d="M {n(cx - 22)},{n(cy - 16)} L {n(cx - 12)},{n(cy - 22)} L {n(cx - 4)},{n(cy - 14)} Z" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.8"/>'
            f'<path d="M {n(cx + 22)},{n(cy - 16)} L {n(cx + 12)},{n(cy - 22)} L {n(cx + 4)},{n(cy - 14)} Z" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.8"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="21" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1.2"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="14" fill="url(#ptblack)" stroke="#0E1422" stroke-width="1"/>'
            + "".join(f'<circle cx="{n(cx + 17.4 * math.cos(math.radians(a)))}" cy="{n(cy + 17.4 * math.sin(math.radians(a)))}" r="1.6" fill="#6B7686"/>' for a in range(0, 360, 45))
            + f'<g transform="rotate(38 {n(cx)} {n(cy)})"><rect x="{n(cx - 4)}" y="{n(cy - 5)}" width="38" height="10" rx="5" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/><circle cx="{n(cx + 33)}" cy="{n(cy)}" r="8" fill="url(#ptred)" stroke="#6E120D" stroke-width="1"/><ellipse cx="{n(cx + 31)}" cy="{n(cy - 3)}" rx="3.4" ry="2" fill="#FFFFFF" opacity="0.5"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="4.2" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.8"/>')


def strainer():
    cx = 320.0
    return (f'<g filter="url(#ptsh)"><rect x="{n(cx - 20)}" y="236" width="40" height="22" rx="5" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1"/></g>'
            f'<rect x="{n(cx - 12)}" y="229" width="24" height="9" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/>' + P.hex_nut(cx, 233, 5.2)
            + f'<path d="M {n(cx - 17)},258 Q {n(cx - 20)},292 {n(cx)},294 Q {n(cx + 20)},292 {n(cx + 17)},258 Z" fill="url(#ptcav)" stroke="#5A6578" stroke-width="1.2"/>'
            f'<path d="M {n(cx - 15)},268 Q {n(cx - 17)},291 {n(cx)},292 Q {n(cx + 17)},291 {n(cx + 15)},268 Z" fill="url(#ptfuel)"/>'
            f'<ellipse cx="{n(cx - 8)}" cy="270" rx="3" ry="8" fill="#FFFFFF" opacity="0.45" transform="rotate(8 {n(cx - 8)} 270)"/>'
            f'<line x1="{n(cx - 18)}" y1="259" x2="{n(cx + 18)}" y2="259" stroke="#5A6578" stroke-width="2"/>'
            f'<rect x="{n(cx - 2.6)}" y="293" width="5.2" height="9" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.7"/><circle cx="{n(cx)}" cy="306" r="4.4" fill="url(#ptred)" stroke="#6E120D" stroke-width="0.8"/>')


def primer():
    cx = 394.0
    return (f'<path d="M {n(cx)},232 L {n(cx)},258" stroke="url(#ptsteel)" stroke-width="3" opacity="0.0"/>'
            f'<g filter="url(#ptsh)"><rect x="{n(cx - 8)}" y="226" width="16" height="32" rx="4" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1"/></g>'
            f'<rect x="{n(cx - 2.2)}" y="204" width="4.4" height="24" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.7"/><rect x="{n(cx - 9)}" y="198" width="18" height="8" rx="3.5" fill="url(#ptred)" stroke="#6E120D" stroke-width="0.9"/>'
            f'<rect x="{n(cx - 8)}" y="236" width="16" height="3" fill="#5A6578" opacity="0.35"/><rect x="{n(cx - 8)}" y="243" width="16" height="3" fill="#5A6578" opacity="0.35"/>'
            + P.tube([(402, 232), (428, 232), (452, 196), (524, 196)], "#F0B654", "#8F5A12", "#FFE6AE", w=3.2, shadow=False).replace('stroke-linecap="round"', 'stroke-linecap="round" stroke-dasharray="6 4"', 2))


def engine():
    out = []
    for x in (530, 580):
        for (y0, y1) in ((168, 218), (282, 332)):
            fins = "".join(f'<line x1="{n(x)}" y1="{n(y0 + 6 + i * 6.5)}" x2="{n(x + 26)}" y2="{n(y0 + 6 + i * 6.5)}" stroke="#2A3550" stroke-opacity="0.35" stroke-width="1.6"/>' for i in range(int((y1 - y0 - 12) / 6.5) + 1))
            out.append(f'<g filter="url(#ptsh)"><rect x="{n(x)}" y="{n(y0)}" width="26" height="{n(y1 - y0)}" rx="4" fill="url(#ptblueh)" stroke="#183A74" stroke-width="1"/></g>' + fins)
            cap_y = y0 - 5 if y0 < 200 else y1 - 3
            out.append(f'<rect x="{n(x - 3)}" y="{n(cap_y)}" width="32" height="8" rx="3" fill="url(#ptgrey)" stroke="#5A6578" stroke-width="0.9"/>')
    out.append(f'<g filter="url(#ptsh)"><rect x="520" y="212" width="94" height="76" rx="12" fill="url(#ptblueh)" stroke="#183A74" stroke-width="1.2"/></g>'
               f'<rect x="528" y="216" width="78" height="5" rx="2.5" fill="#FFFFFF" opacity="0.35"/>'
               f'<circle cx="567" cy="250" r="15" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1"/><circle cx="567" cy="250" r="6" fill="url(#ptblack)"/>')
    return "".join(out)


def carburettor():
    return (f'<g filter="url(#ptsh)"><rect x="472" y="222" width="38" height="64" rx="7" fill="url(#ptcast)" stroke="#7A3A08" stroke-opacity="0.6" stroke-width="1"/>'
            f'<rect x="448" y="244" width="30" height="42" rx="7" fill="url(#ptcast)" stroke="#7A3A08" stroke-opacity="0.6" stroke-width="1"/></g>'
            f'<path d="M 484,230 L 498,230 L 498,246 Q 494,254 498,262 L 498,278 L 484,278 L 484,262 Q 488,254 484,246 Z" fill="url(#ptcav)"/>'
            f'<ellipse cx="491" cy="238" rx="7.4" ry="2.6" fill="#4F78B5" stroke="#16294A" stroke-width="0.8" transform="rotate(-12 491 238)"/>'
            f'<rect x="452" y="266" width="22" height="16" rx="4" fill="url(#ptfuel)"/><rect x="474" y="224" width="4" height="58" rx="2" fill="#FFF1C9" opacity="0.5"/>'
            + P.tube([(491, 222), (491, 200), (524, 196)], "#C9D1DC", "#5A6578", "#FFFFFF", w=5) + P.tube([(491, 286), (491, 306), (524, 304)], "#C9D1DC", "#5A6578", "#FFFFFF", w=5))


def callouts():
    c = S.callout
    d = DY
    return "".join([c(1, 72, -2 + d, 96, 17 + d), c(2, 22, 134 + d, 34, 114 + d), c(3, 230, 138 + d, 258, 112 + d), c(4, 376, 200 + d, 342, 180 + d), c(5, 262, 286 + d, 301, 278 + d),
                    c(6, 430, 214 + d, 401, 232 + d), c(7, 436, 312 + d, 478, 284 + d)])


def drawing():
    return (f'<g transform="translate(0 {n(DY)})">' + wing() + vents_and_drains() + lines() + engine() + carburettor() + primer() + selector() + strainer() + "</g>")


def plate():
    return {
        "id": "fig-09-01-gravity-fuel-system",
        "replaces": "fig-09-01-gravity-fuel-system.svg",
        "book_file": "plate-09-01-gravity-fuel-system.jpg",
        "caption": "Figure 9-1. A high-wing gravity-feed fuel system",
        "desc": "Figure 9-1. A high-wing gravity-feed fuel system",
        "legend": ["Filler cap.", "Tank vent.", "Tank sump drain.", "Fuel selector valve.", "Fuel strainer and quick drain, at the lowest point.", "Primer, for starting.", "Carburettor, below the tanks."],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-09-01-gravity-fuel-system.svg", "blank": True, "layers": [P.defs(), '<rect x="0" y="0" width="640" height="360" fill="url(#ptbg)"/>', drawing(), callouts()]},
    }
