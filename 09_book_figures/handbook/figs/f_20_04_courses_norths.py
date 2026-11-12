"""Figure 20-4. Measuring the true course, and the three norths. Drawn again as two sheets lying on a table: on the left the chart (warm paper with its printed graticule) with the meridian,
the course line across it and a glass protractor centred on the crossing, its straight edge along the meridian, its scale engraved and the line cutting it at 300° in a red ring; on the
right a worksheet (pale paper, printed grid) with the three norths and the heading as ribbons from one point (true north dark, magnetic north blue, compass north green, the heading red)
and the two angles between the norths as glowing amber arcs, five times larger than in the example. The geometry, numbers and callouts of the old figure are kept (figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S

CEN, RAD = (175.0, 185.0), 112.0
ORG = (480.0, 322.0)


def table():
    return (f'<defs>{S.gradient("n4t", [(0, "#C3CEDD"), (1, "#A5B4C9")])}<radialGradient id="n4v" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#10233F" stop-opacity="0"/><stop offset="1" stop-color="#10233F" stop-opacity="0.24"/></radialGradient>'
            '<filter id="n4n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="9"/><feColorMatrix type="matrix" values="0 0 0 0 0.2  0 0 0 0 0.26  0 0 0 0 0.36  0 0 0 0.35 -0.08"/></filter></defs>'
            '<rect x="0" y="0" width="640" height="360" fill="url(#n4t)"/><rect x="0" y="0" width="640" height="360" filter="url(#n4n)" opacity="0.5"/><rect x="0" y="0" width="640" height="360" fill="url(#n4v)"/>')


def sheet(uid, x, y, w, h, top, bottom, line, step, ox, oy):
    out = [f'<defs>{S.gradient(uid, [(0, top), (1, bottom)])}<filter id="{uid}s" x="-6%" y="-5%" width="112%" height="115%"><feDropShadow dx="1.5" dy="4" stdDeviation="4" flood-color="#10233F" flood-opacity="0.42"/></filter>'
           f'<clipPath id="{uid}c"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/></clipPath></defs>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="url(#{uid})" filter="url(#{uid}s)"/>', f'<g clip-path="url(#{uid}c)">']
    k = math.floor((x - ox) / step)
    px = ox + k * step
    while px <= x + w:
        out.append(f'<line x1="{S.n(px)}" y1="{y}" x2="{S.n(px)}" y2="{y + h}" stroke="{line}" stroke-opacity="0.8" stroke-width="0.6"/>')
        px += step
    k = math.floor((y - oy) / step)
    py = oy + k * step
    while py <= y + h:
        out.append(f'<line x1="{x}" y1="{S.n(py)}" x2="{x + w}" y2="{S.n(py)}" stroke="{line}" stroke-opacity="0.8" stroke-width="0.6"/>')
        py += step
    out.append("</g>")
    out.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="3" fill="none" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="1"/>')
    return "".join(out)


def chart():
    out = [sheet("n4l", 10, 10, 300, 340, "#FDF3E2", "#F3E4C8", "#E3D2B2", 25, 175, 185)]
    # the meridian (with its arrow) and the course line
    out.append('<line x1="175" y1="10" x2="175" y2="350" stroke="#FFFFFF" stroke-width="3.6" stroke-opacity="0.7"/><line x1="175" y1="10" x2="175" y2="350" stroke="#1F2937" stroke-width="1.4"/>'
               '<polygon points="175,12 181,23 169,23" fill="#1F2937" stroke="#FFFFFF" stroke-width="1" stroke-linejoin="round"/>')
    out.append(H.ribbon("n4c", [(278.9, 245.0), (27.8, 100.0)], width=3.6, colours=("#1B2433", "#4B5870"), arrow=False, casing=1.2))
    return "".join(out)


def protractor():
    cx, cy, r = CEN[0], CEN[1], RAD
    out = [f'<defs><linearGradient id="n4g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.78"/><stop offset="0.5" stop-color="#DCE8FB" stop-opacity="0.50"/><stop offset="1" stop-color="#B9CFF2" stop-opacity="0.58"/></linearGradient>'
           '<filter id="n4s" x="-12%" y="-8%" width="124%" height="118%"><feDropShadow dx="2" dy="4" stdDeviation="3" flood-color="#10233F" flood-opacity="0.38"/></filter>'
           f'<clipPath id="n4pc"><path d="M{cx},{cy - r} A{r},{r} 0 0,0 {cx},{cy + r} Z"/></clipPath></defs>']
    half = f"M{cx},{cy - r} A{r},{r} 0 0,0 {cx},{cy + r} Z"
    out.append(f'<defs><clipPath id="n4cut"><path clip-rule="evenodd" d="M0,0 H640 V360 H0 Z {half}"/></clipPath><filter id="n4bl" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.2"/></filter></defs>'
               f'<g clip-path="url(#n4cut)"><path d="{half}" fill="#10233F" opacity="0.40" transform="translate(3 5)" filter="url(#n4bl)"/></g>'
               f'<path d="{half}" fill="url(#n4g)" stroke="#1D4ED8" stroke-width="1.6" stroke-linejoin="round"/>')
    # a glossy sweep across the glass
    out.append(f'<g clip-path="url(#n4pc)"><path d="M{cx - 120},{cy - 40} L{cx - 20},{cy - 130} L{cx - 4},{cy - 130} L{cx - 104},{cy - 20} Z" fill="#FFFFFF" opacity="0.28"/>'
               f'<path d="M{cx - 40},{cy + 60} A 52,52 0 0 1 {cx},{cy + 8}" fill="none" stroke="#FFFFFF" stroke-opacity="0.0"/></g>')
    out.append(f'<path d="M{cx},{cy - r + 1} A{r - 1},{r - 1} 0 0,0 {cx},{cy + r - 1}" fill="none" stroke="#7FA2E8" stroke-opacity="0.55" stroke-width="2.4"/>')
    out.append(f'<path d="M{cx},{cy - r + 6} A{r - 6},{r - 6} 0 0,0 {cx},{cy + r - 6}" fill="none" stroke="#FFFFFF" stroke-opacity="0.65" stroke-width="1"/>')
    # the scale: a tick every 5 degrees (12 long at multiples of 30, 8 at 10, 4 at 5), 180 at the bottom to 360 at the top
    for deg in range(180, 361, 5):
        a = math.radians(deg)
        ln = 12 if deg % 30 == 0 else 8 if deg % 10 == 0 else 4
        x0, y0 = cx + r * math.sin(a), cy - r * math.cos(a) * -1 * -1
        # bearing deg: 180 is straight down, 270 to the left, 360 straight up
        x0, y0 = cx + r * math.sin(math.radians(deg)), cy - r * math.cos(math.radians(deg))
        x1, y1 = cx + (r - ln) * math.sin(math.radians(deg)), cy - (r - ln) * math.cos(math.radians(deg))
        out.append(f'<line x1="{S.n(x0)}" y1="{S.n(y0)}" x2="{S.n(x1)}" y2="{S.n(y1)}" stroke="#1B3F94" stroke-width="{1.1 if ln > 4 else 0.8}" stroke-linecap="round"/>')
    for deg in range(180, 361, 30):
        x, y = cx + 92 * math.sin(math.radians(deg)), cy - 92 * math.cos(math.radians(deg))
        out.append(H.text(x, y + 3.8, str(deg), 11, "#1B3F94", "bold" if deg == 300 else "normal", "middle"))
    # the straight edge along the meridian, and the centre
    out.append(f'<line x1="{cx}" y1="{cy - r}" x2="{cx}" y2="{cy + r}" stroke="#1D4ED8" stroke-width="1.8"/><line x1="{cx - 1.6}" y1="{cy - r}" x2="{cx - 1.6}" y2="{cy + r}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="0.9"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="3.4" fill="#1D4ED8" stroke="#FFFFFF" stroke-width="1.2"/>')
    # the line cuts the scale at 300: a red ring
    out.append(f'<circle cx="74.5" cy="127" r="5" fill="none" stroke="#FF5B4D" stroke-width="5" opacity="0.7" filter="url(#n4rg)"/><circle cx="74.5" cy="127" r="5" fill="none" stroke="#FFFFFF" stroke-width="4.6" stroke-opacity="0.9"/>'
               f'<circle cx="74.5" cy="127" r="5" fill="none" stroke="#C4282B" stroke-width="2"/>')
    return "".join(out)


def norths():
    out = [sheet("n4r", 330, 10, 300, 340, "#F7FAFD", "#E6EEF7", "#BFCFE2", 25, 480, 322)]
    x0, y0 = ORG
    out.append('<defs><filter id="n4a" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.4"/></filter></defs>')
    out.append(H.vector("n4n", (480.0, 322.0), (480.0, 82.0), 3.8, ("#16233D", "#4A5A78"), heads=1, head_len=13, head_w=11, glow="#5A6B8C"))
    out.append(H.vector("n4m", (480.0, 322.0), (535.4, 115.3), 3.8, ("#1B4FD0", "#6FA3F5"), heads=1, head_len=13, head_w=11, glow="#5B96FF"))
    out.append(H.vector("n4g2", (480.0, 322.0), (521.7, 85.6), 3.8, ("#0B8A66", "#4FD3A0"), heads=1, head_len=13, head_w=11, glow="#35E6A0"))
    out.append(H.vector("n4h", (480.0, 322.0), (336.2, 213.7), 4.4, ("#C4282B", "#F47D74"), heads=1, head_len=14, head_w=12, glow="#FF6A5E"))
    # the angles: amber arcs with a glow
    for d in ("M480.0,132.0 A190.0,190.0 0 0,1 529.2,138.5", "M507.8,164.4 A160.0,160.0 0 0,1 521.4,167.5"):
        out.append(f'<path d="{d}" fill="none" stroke="#FFB020" stroke-width="7" opacity="0.75" filter="url(#n4a)"/><path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="6.4" stroke-opacity="0.9" stroke-linecap="round"/>'
                   f'<path d="{d}" fill="none" stroke="#C2610E" stroke-width="3.2" stroke-linecap="round"/>')
    out.append(f'<defs><radialGradient id="n4d" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#6B7C99"/><stop offset="1" stop-color="#0F172A"/></radialGradient></defs><circle cx="480" cy="322" r="4.8" fill="url(#n4d)" stroke="#FFFFFF" stroke-width="1.5"/>')
    return "".join(out)


def plate():
    c = S.callout
    calls = "".join([
        c(1, 215, 40, 177, 60), c(2, 55, 295, 95, 245), c(3, 52.5, 87, 70.5, 122), c(4, 448, 74, 478, 86), c(5, 577.4, 119.3, 538.4, 117.3),
        c(6, 551.7, 65.6, 523.7, 83.6), c(7, 356.2, 191.7, 366.2, 235.7), c(8, 458.8, 155.6, 502.8, 134.6), c(9, 570.6, 183.8, 516.6, 166.8),
    ])
    glow_ring = '<defs><filter id="n4rg" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.4"/></filter></defs>'
    layers = [table(), chart(), glow_ring, protractor(), norths(), calls]
    return {
        "id": "fig-20-04-courses-norths",
        "replaces": "fig-20-04-courses-norths.svg",
        "book_file": "plate-20-04-courses-norths.jpg",
        "caption": "Figure 20-4. Measuring the true course, and the three norths",
        "desc": "Figure 20-4. Measuring the true course, and the three norths",
        "legend": [
            "The meridian nearest the middle of the leg.",
            "Protractor, centred on the crossing, its straight edge along the meridian.",
            "The line cuts the scale at 300°: the true course.",
            "True north.",
            "Magnetic north.",
            "Compass north.",
            "The aeroplane's heading: 307° from true north, 304° from magnetic north, 305° from compass north.",
            "Variation, here 3° E.",
            "Deviation, here 1° W.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-20-04-courses-norths.svg", "blank": True, "layers": layers},
    }
