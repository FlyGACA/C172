"""Figure 8-1. The four strokes of a piston engine. Four cylinders cut away, one for each stroke: the head with its two valves and its spark plug, the piston with its rings, the connecting rod
and the crank turning clockwise; the gas in the cylinder is coloured for what it is doing (the fresh mixture drawn in, squeezed, burning, driven out), with the blue arrows showing which
way the piston moves. The drawing is made by this module (figs/parts.py has the gradients, figs/scene.py the callouts); the ten numbered callouts of the old figure are kept."""
import math

from figs import parts as P
from figs import scene as S

n = S.n
PW, GAP, X0, Y0 = 148.0, 10.0, 8.0, 8.0
R, L = 15.0, 56.0                       # crank radius and rod length
STROKES = [  # (crank angle clockwise from the top, gas, intake valve open, exhaust valve open, flame, arrow)
    (100, "intake", True, False, False, "down"),
    (250, "compress", False, False, False, "up"),
    (45, "power", False, False, True, "down"),
    (290, "exhaust", False, True, False, "up"),
]
GAS = {"intake": ("#BDE6FA", "#7CC5F0"), "compress": ("#7CC5F0", "#3E97DC"), "power": ("#FFE9A0", "#F2762E"), "exhaust": ("#D3D8E0", "#9AA3B2")}


def panel_defs():
    return (P.defs().replace("</defs>", "")
            + f'<radialGradient id="f0801flame" cx="0.5" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFFBE0"/><stop offset="0.35" stop-color="#FFD35A"/><stop offset="0.75" stop-color="#F2762E"/><stop offset="1" stop-color="#C73B12"/></radialGradient>'
            + "".join(f'<linearGradient id="f0801g{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>' for k, (a, b) in GAS.items())
            + "</defs>")


def cylinder(i, spec):
    theta, gas, intake_open, exhaust_open, flame, arrow = spec
    px, py = X0 + i * (PW + GAP), Y0
    cx = px + PW / 2
    cyc = py + 232.0                                      # the crank centre
    th = math.radians(theta)
    pin = (cx + R * math.sin(th), cyc - R * math.cos(th))
    piston_pin_y = cyc - (R * math.cos(th) + math.sqrt(L * L - (R * math.sin(th)) ** 2))
    ptop = piston_pin_y - 22.0                             # the crown of the piston
    out = [f'<g filter="url(#ptsh)"><rect x="{n(px)}" y="{n(py)}" width="{n(PW)}" height="296" rx="14" fill="#FFFFFF" fill-opacity="0.75" stroke="#C9D2DF" stroke-width="1"/></g>']
    chamber_top, bore_l, bore_r = py + 58.0, cx - 31.0, cx + 31.0
    # the gas between the head and the piston
    out.append(f'<rect x="{n(bore_l)}" y="{n(chamber_top)}" width="62" height="{n(ptop - chamber_top)}" fill="url(#f0801g{gas})"/>')
    # the walls of the cylinder (cut) with their fins, the head, the crankcase
    out.append(f'<g filter="url(#ptsh)"><rect x="{n(bore_l - 17)}" y="{n(chamber_top)}" width="17" height="112" fill="url(#ptcast)" stroke="#7A3A08" stroke-opacity="0.55" stroke-width="1"/>'
               f'<rect x="{n(bore_r)}" y="{n(chamber_top)}" width="17" height="112" fill="url(#ptcast)" stroke="#7A3A08" stroke-opacity="0.55" stroke-width="1"/></g>')
    out += [f'<line x1="{n(bore_l - 22)}" y1="{n(chamber_top + 10 + k * 13)}" x2="{n(bore_l - 17)}" y2="{n(chamber_top + 10 + k * 13)}" stroke="#7A3A08" stroke-width="2.4"/><line x1="{n(bore_r + 17)}" y1="{n(chamber_top + 10 + k * 13)}" x2="{n(bore_r + 22)}" y2="{n(chamber_top + 10 + k * 13)}" stroke="#7A3A08" stroke-width="2.4"/>' for k in range(8)]
    out.append(f'<g filter="url(#ptsh)"><path d="M {n(bore_l - 22)},{n(chamber_top + 2)} L {n(bore_l - 22)},{n(py + 24)} Q {n(bore_l - 22)},{n(py + 16)} {n(bore_l - 14)},{n(py + 16)} L {n(bore_r + 14)},{n(py + 16)} Q {n(bore_r + 22)},{n(py + 16)} {n(bore_r + 22)},{n(py + 24)} L {n(bore_r + 22)},{n(chamber_top + 2)} L {n(bore_r)},{n(chamber_top)} '
               f'L {n(bore_r)},{n(chamber_top)} L {n(bore_l)},{n(chamber_top)} Z" fill="url(#ptcast)" stroke="#7A3A08" stroke-opacity="0.55" stroke-width="1"/></g>'
               f'<rect x="{n(bore_l - 22)}" y="{n(py + 17)}" width="{n(62 + 44)}" height="4" rx="2" fill="#FFF1C9" opacity="0.6"/>')
    # ports and valves: the intake on the left, the exhaust on the right
    for side, x_stem, is_open, col in ((-1, cx - 17, intake_open, "#2E8BD6"), (1, cx + 17, exhaust_open, "#D6542B")):
        lift = 9.0 if is_open else 0.0
        out.append(f'<rect x="{n(x_stem - 5)}" y="{n(chamber_top - 4)}" width="10" height="7" fill="#0B2A35"/>')
        out.append(f'<rect x="{n(x_stem - 1.6)}" y="{n(py + 22)}" width="3.2" height="{n(chamber_top + lift - py - 22)}" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.6"/>')
        out.append(f'<ellipse cx="{n(x_stem)}" cy="{n(chamber_top + lift + 1)}" rx="7.4" ry="2.6" fill="{col}" stroke="#0E1422" stroke-width="0.9"/>')
        out.append(f'<rect x="{n(x_stem - 4)}" y="{n(py + 18)}" width="8" height="6" rx="2" fill="url(#ptgrey)" stroke="#5A6578" stroke-width="0.7"/>')
        # the port to the outside
        px_out = bore_l - 22 if side < 0 else bore_r + 22
        out.append(f'<path d="M {n(x_stem)},{n(chamber_top - 1)} L {n(x_stem)},{n(py + 40)} L {n(px_out)},{n(py + 40)}" fill="none" stroke="#0B2A35" stroke-width="9" stroke-linejoin="round"/>')
        out.append(f'<path d="M {n(x_stem)},{n(chamber_top - 1)} L {n(x_stem)},{n(py + 40)} L {n(px_out)},{n(py + 40)}" fill="none" stroke="url(#f0801g{"intake" if side < 0 else "exhaust"})" stroke-width="6.4" stroke-linejoin="round" opacity="{0.95 if is_open or (gas in ("intake",) and side < 0) else 0.35}"/>')
    # the spark plug
    out.append(f'<rect x="{n(cx - 3)}" y="{n(py + 2)}" width="6" height="{n(chamber_top + 4 - py - 2)}" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.7"/>'
               f'<rect x="{n(cx - 5)}" y="{n(py + 2)}" width="10" height="16" rx="2" fill="#FBFCFE" stroke="#9AA5B5" stroke-width="0.9"/><polygon points="{S.pts([(cx + 7 * math.cos(math.radians(a)), py + 24 + 2.4 * math.sin(math.radians(a))) for a in range(0, 360, 60)])}" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="0.7"/>'
               f'<path d="M {n(cx)},{n(chamber_top + 4)} l 0,3 l 5,3" fill="none" stroke="#5A6578" stroke-width="1.4"/>')
    if flame:
        out.append(f'<path d="M {n(bore_l + 1)},{n(chamber_top + 1)} L {n(bore_r - 1)},{n(chamber_top + 1)} L {n(bore_r - 1)},{n(ptop)} L {n(bore_l + 1)},{n(ptop)} Z" fill="url(#f0801flame)" opacity="0.92"/>'
                   f'<path d="M {n(cx - 7)},{n(chamber_top + 8)} l 5,-7 l 2,6 l 4,-9 l 2,10 l 5,-5" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    # the connecting rod, the piston, the crank
    out.append(f'<path d="M {n(cx)},{n(piston_pin_y)} L {n(pin[0])},{n(pin[1])}" stroke="#3E4A5E" stroke-width="9" stroke-linecap="round"/><path d="M {n(cx)},{n(piston_pin_y)} L {n(pin[0])},{n(pin[1])}" stroke="url(#ptsteel)" stroke-width="6" stroke-linecap="round"/>')
    out.append(f'<g filter="url(#ptsh)"><rect x="{n(bore_l + 1)}" y="{n(ptop)}" width="60" height="30" rx="3" fill="url(#ptgrey)" stroke="#5A6578" stroke-width="1"/></g>'
               + "".join(f'<line x1="{n(bore_l + 1)}" y1="{n(ptop + 5 + k * 5)}" x2="{n(bore_r - 1)}" y2="{n(ptop + 5 + k * 5)}" stroke="#5A6578" stroke-width="1.2"/>' for k in range(3))
               + f'<rect x="{n(bore_l + 4)}" y="{n(ptop + 1.5)}" width="54" height="2.4" fill="#FFFFFF" opacity="0.7"/><circle cx="{n(cx)}" cy="{n(piston_pin_y)}" r="3.6" fill="#3E4A5E" stroke="#FFFFFF" stroke-width="0.8"/>')
    out.append(f'<g filter="url(#ptsh)"><path d="M {n(px + 10)},{n(py + 172)} L {n(px + PW - 10)},{n(py + 172)} L {n(px + PW - 4)},{n(py + 290)} L {n(px + 4)},{n(py + 290)} Z" fill="url(#ptblueh)" stroke="#183A74" stroke-width="1" opacity="0.0"/></g>')
    out.append(f'<circle cx="{n(cx)}" cy="{n(cyc)}" r="25" fill="url(#ptgrey)" stroke="#5A6578" stroke-width="1.2"/><circle cx="{n(cx)}" cy="{n(cyc)}" r="8" fill="url(#ptblack)"/>'
               f'<circle cx="{n(pin[0])}" cy="{n(pin[1])}" r="6.4" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/>'
               f'<path d="M {n(cx - 20)},{n(cyc - 12)} A 22,22 0 0 1 {n(cx + 6)},{n(cyc - 21.5)}" fill="none" stroke="#2F63C8" stroke-width="2.6" stroke-linecap="round"/><path d="M {n(cx + 4)},{n(cyc - 27)} l 8,5.5 l -9.5,2.6 Z" fill="#2F63C8"/>')
    # the arrow of the piston, beside the cylinder
    ax = bore_r + 28
    a0, a1 = (chamber_top + 50, chamber_top + 96) if arrow == "down" else (chamber_top + 96, chamber_top + 50)
    out.append(S.ribbon(f"f0801a{i}", [(ax, a0), (ax, (a0 + a1) / 2), (ax, a1)], 5.0, "#2F63C8", "#8DB3F2"))
    return "".join(out), (cx, py, chamber_top, bore_l, bore_r, pin, ptop, cyc)


def callouts(geo):
    c = S.callout
    (cx1, py1, ct1, bl1, br1, pin1, pt1, cy1) = geo[0]
    (cx2, py2, ct2, bl2, br2, pin2, pt2, cy2) = geo[1]
    (cx3, py3, ct3, bl3, br3, pin3, pt3, cy3) = geo[2]
    (cx4, py4, ct4, bl4, br4, pin4, pt4, cy4) = geo[3]
    out = [c(k + 1, geo[k][0], 326) for k in range(4)]
    out += [c(5, cx1 - 62, py1 + 58, cx1 - 17, ct1 + 10), c(6, cx4 + 62, py4 + 58, cx4 + 17, ct4 + 10), c(7, cx3 + 62, py3 + 6, cx3 + 4, py3 + 8),
            c(8, cx2 - 62, pt2 + 14, bl2 + 4, pt2 + 14), c(9, cx2 + 58, cy2 - 52, (cx2 + pin2[0]) / 2, (pt2 + 22 + pin2[1]) / 2), c(10, cx1 - 62, cy1 + 36, cx1 - 24, cy1 + 10)]
    return "".join(out)


def plate():
    drawings, geo = [], []
    for i, spec in enumerate(STROKES):
        d, g = cylinder(i, spec)
        drawings.append(d); geo.append(g)
    return {
        "id": "fig-08-01-four-stroke-cycle",
        "replaces": "fig-08-01-four-stroke-cycle.svg",
        "book_file": "plate-08-01-four-stroke-cycle.jpg",
        "caption": "Figure 8-1. The four strokes of a piston engine",
        "desc": "Figure 8-1. The four strokes of a piston engine",
        "legend": [
            "**Intake.** The piston moves down with the intake valve open and draws in the fuel-air mixture.",
            "**Compression.** Both valves are closed; the rising piston squeezes the mixture.",
            "**Power.** The plugs fire near the top of the stroke; the burning mixture drives the piston down. Only this stroke delivers work.",
            "**Exhaust.** The exhaust valve opens and the rising piston pushes the burnt gas out.",
            "Intake valve.", "Exhaust valve.", "Spark plug (each cylinder has two).", "Piston; the blue arrows show which way it moves.", "Connecting rod.", "Crankshaft, turning clockwise in this drawing.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-08-01-four-stroke-cycle.svg", "blank": True,
                   "layers": [panel_defs(), '<rect x="0" y="0" width="640" height="360" fill="url(#ptbg)"/>', *drawings, callouts(geo)]},
    }
