"""Figure 20-2. Measuring a leg with a ruler, and checking it on the latitude scale. Drawn again as a chart lying on a table: warm paper with a printed graticule, the course line a dark
ribbon from the aerodrome A (a ringed runway symbol) to the point WADI (a dark triangle), a steel ruler laid along it with its zero at WADI, engraved in centimetres, a red hairline at
31.9 cm; at the right the latitude scale on a meridian, a steel strip engraved in minutes, with a pair of steel dividers set to the same length (86 minutes, 86 NM); and the chart's two scale
lines, in nautical miles and in kilometres, printed in its margin. The geometry, numbers and callouts of the old figure are kept (figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S

A, WADI = (410.0, 345.0), (133.7, 185.5)


def table():
    return (f'<defs>{S.gradient("c2t", [(0, "#C3CEDD"), (1, "#A5B4C9")])}<radialGradient id="c2v" cx="0.5" cy="0.5" r="0.75"><stop offset="0.55" stop-color="#10233F" stop-opacity="0"/><stop offset="1" stop-color="#10233F" stop-opacity="0.24"/></radialGradient>'
            '<filter id="c2n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="12"/><feColorMatrix type="matrix" values="0 0 0 0 0.2  0 0 0 0 0.26  0 0 0 0 0.36  0 0 0 0.35 -0.08"/></filter></defs>'
            '<rect x="0" y="0" width="640" height="465" fill="url(#c2t)"/><rect x="0" y="0" width="640" height="465" filter="url(#c2n)" opacity="0.5"/><rect x="0" y="0" width="640" height="465" fill="url(#c2v)"/>')


def sheet():
    out = [f'<defs>{S.gradient("c2p", [(0, "#FDF3E2"), (1, "#F2E3C6")])}{S.gradient("c2m", [(0, "#FBF8F1"), (1, "#F1EBDC")])}'
           '<filter id="c2s" x="-6%" y="-5%" width="112%" height="112%"><feDropShadow dx="1.5" dy="4" stdDeviation="4" flood-color="#10233F" flood-opacity="0.42"/></filter>'
           '<clipPath id="c2c"><rect x="20" y="15" width="595" height="380"/></clipPath></defs>',
           '<rect x="20" y="15" width="595" height="460" rx="3" fill="url(#c2m)" filter="url(#c2s)"/>',
           '<rect x="20" y="15" width="595" height="380" fill="url(#c2p)"/><g clip-path="url(#c2c)">']
    for x in range(20, 616, 25):
        out.append(f'<line x1="{x}" y1="15" x2="{x}" y2="395" stroke="#E3D2B2" stroke-opacity="0.8" stroke-width="0.6"/>')
    for y in range(15, 396, 25):
        out.append(f'<line x1="20" y1="{y}" x2="615" y2="{y}" stroke="#E3D2B2" stroke-opacity="0.8" stroke-width="0.6"/>')
    out.append('</g><rect x="20.5" y="15.5" width="594" height="379" fill="none" stroke="#7B6C52" stroke-width="1.1"/>')
    return "".join(out)


def course():
    out = [H.ribbon("c2l", [A, WADI], width=3.6, colours=("#111B30", "#2E3C58"), arrow=False, casing=1.2)]
    return "".join(out)


def ruler():
    """The ruler lies along the line, rotated 30 degrees about WADI, its zero there: a steel strip with engraved centimetres and a red hairline at 31.9."""
    ticks = []
    for i in range(0, 69):
        x = i * 5.0
        if x > 330:
            break
        ln = 11 if i % 10 == 0 else 8 if i % 2 == 0 else 5
        ticks.append(f'M{x:.1f},7 v{ln}')
    nums = "".join(H.text(i * 50.0, 32.0, str(i * 5), 11, "#1F2937", "bold", "middle") for i in range(0, 7))
    return (f'<defs>{S.gradient("c2r", [(0, "#F7F9FC"), (0.2, "#E4EAF2"), (0.6, "#CBD5E2"), (1, "#B1BDCE")])}'
            '<filter id="c2rs" x="-6%" y="-30%" width="112%" height="190%"><feDropShadow dx="1.6" dy="4" stdDeviation="3" flood-color="#10233F" flood-opacity="0.4"/></filter></defs>'
            f'<g transform="translate({WADI[0]} {WADI[1]}) rotate(30)">'
            '<rect x="-6" y="7" width="345" height="30" rx="2" fill="url(#c2r)" stroke="#7F8DA3" stroke-width="1" filter="url(#c2rs)"/>'
            '<rect x="-5" y="8" width="343" height="1.8" rx="0.9" fill="#FFFFFF" opacity="0.9"/><rect x="-5" y="34" width="343" height="1.4" rx="0.7" fill="#5F6E86" opacity="0.3"/>'
            f'<path d="{" ".join(ticks)}" stroke="#2A3548" stroke-width="0.9" fill="none"/>' + nums +
            '<line x1="319" y1="1" x2="319" y2="42" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.8"/><line x1="319" y1="1" x2="319" y2="42" stroke="#C4282B" stroke-width="1.8"/>'
            '</g>')


def markers():
    return ('<defs><linearGradient id="c2tg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4A5875"/><stop offset="1" stop-color="#10192B"/></linearGradient>'
            '<filter id="c2ms" x="-40%" y="-40%" width="190%" height="200%"><feDropShadow dx="1" dy="2.4" stdDeviation="1.6" flood-color="#10233F" flood-opacity="0.4"/></filter></defs>'
            f'<polygon points="{WADI[0]},{WADI[1] - 9} {WADI[0] + 7.9},{WADI[1] + 4.5} {WADI[0] - 7.8},{WADI[1] + 4.5}" fill="url(#c2tg)" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round" filter="url(#c2ms)"/>'
            f'<g filter="url(#c2ms)"><circle cx="{A[0]}" cy="{A[1]}" r="8" fill="#FFFFFF" stroke="#1D4ED8" stroke-width="2.2"/>'
            f'<line x1="403.5" y1="333.7" x2="416.5" y2="356.3" stroke="#FFFFFF" stroke-width="6.4" stroke-linecap="butt"/><line x1="403.5" y1="333.7" x2="416.5" y2="356.3" stroke="#1D4ED8" stroke-width="4" stroke-linecap="butt"/></g>')


def latitude_scale():
    out = [f'<defs>{S.gradient("c2v1", [(0, "#F7F9FC"), (0.3, "#DDE5EF"), (1, "#B5C1D2")], 0, 0, 1, 0)}'
           '<filter id="c2vs" x="-30%" y="-3%" width="170%" height="106%"><feDropShadow dx="2" dy="2.4" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.38"/></filter></defs>',
           '<rect x="486" y="8" width="40" height="352" rx="2.4" fill="url(#c2v1)" stroke="#7F8DA3" stroke-width="1" filter="url(#c2vs)"/>',
           '<rect x="487" y="9" width="1.8" height="350" rx="0.9" fill="#FFFFFF" opacity="0.9"/>']
    per = (345.0 - 26.0) / 86.0
    for m in range(0, 87):
        y = 345.0 - m * per
        ln = 12 if m % 10 == 0 else 8 if m % 5 == 0 else 4
        out.append(f'<line x1="{S.n(520 - ln)}" y1="{S.n(y)}" x2="520" y2="{S.n(y)}" stroke="#2A3548" stroke-width="{0.95 if ln > 4 else 0.7}"/>')
    for m in range(0, 81, 10):
        out.append(H.text(505.0, 345.0 - m * per + 3.8, str(m), 11, "#1F2937", "bold", "end"))
    out.append('<line x1="520" y1="353" x2="520" y2="14.9" stroke="#1F2937" stroke-width="1.6"/>')
    # the end of the 86 minutes: a red hairline and its number
    out.append(f'<line x1="505" y1="26" x2="527" y2="26" stroke="#FFFFFF" stroke-width="4.6" stroke-opacity="0.85"/><line x1="505" y1="26" x2="527" y2="26" stroke="#C4282B" stroke-width="2.2"/>')
    out.append(H.text(534.0, 18.0, "86", 15, "#B91C1C", "bold", "start", halo="#FFFFFF"))
    return "".join(out)


def dividers():
    hx, hy = 585.0, 185.5
    out = [f'<defs>{S.gradient("c2d", [(0, "#F4F7FB"), (0.5, "#C4CEDC"), (1, "#8794A8")], 0, 0, 1, 0)}<radialGradient id="c2h" cx="0.35" cy="0.3" r="0.85"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.5" stop-color="#C9D3E0"/><stop offset="1" stop-color="#6E7D93"/></radialGradient>'
           '<filter id="c2ds" x="-20%" y="-5%" width="140%" height="112%"><feDropShadow dx="2.4" dy="3.4" stdDeviation="2.2" flood-color="#10233F" flood-opacity="0.4"/></filter></defs>']
    for tip in ((522.0, 345.0), (522.0, 26.0)):
        dx, dy = tip[0] - hx, tip[1] - hy
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        w0, w1 = 4.4, 0.7
        poly = [(hx + nx * w0, hy + ny * w0), (tip[0] + nx * w1, tip[1] + ny * w1), (tip[0] - nx * w1, tip[1] - ny * w1), (hx - nx * w0, hy - ny * w0)]
        out.append(f'<polygon points="{S.pts(poly)}" fill="#C9D3E0" stroke="#6E7D93" stroke-width="0.7" stroke-linejoin="round" filter="url(#c2ds)"/>')
        out.append(f'<polygon points="{S.pts([(hx + nx * w0 * 0.2, hy + ny * w0 * 0.2), (tip[0] + nx * 0.1, tip[1] + ny * 0.1), (tip[0] + nx * w1, tip[1] + ny * w1), (hx + nx * w0, hy + ny * w0)])}" fill="#FFFFFF" opacity="0.7"/>')
        # the steel point
        out.append(f'<line x1="{S.n(tip[0] - ux * 7)}" y1="{S.n(tip[1] - uy * 7)}" x2="{S.n(tip[0] + ux * 1.2)}" y2="{S.n(tip[1] + uy * 1.2)}" stroke="#1F2937" stroke-width="1.4" stroke-linecap="round"/>')
    out.append(f'<circle cx="{hx}" cy="{hy}" r="7.4" fill="#10233F" opacity="0.3" transform="translate(2 3)"/><circle cx="{hx}" cy="{hy}" r="7" fill="url(#c2h)" stroke="#5A6A82" stroke-width="1"/>'
               f'<line x1="{hx - 4}" y1="{hy - 1.5}" x2="{hx + 4}" y2="{hy + 1.5}" stroke="#4A5870" stroke-width="1.6" stroke-linecap="round"/><circle cx="{hx - 2.4}" cy="{hy - 2.6}" r="1.6" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def scale_bars():
    out = []
    for (y, seg, n_seg, labels, x_labels) in ((414.0, 18.525, 4, ("0", "10", "20"), (40.0, 77.0, 114.1)), (442.0, 20.0, 4, ("0", "20", "40"), (40.0, 80.0, 120.0))):
        for i in range(n_seg):
            fill = "#1F2937" if i % 2 == 0 else "#FFFFFF"
            out.append(f'<rect x="{S.n(40 + i * seg)}" y="{y}" width="{S.n(seg)}" height="6" fill="{fill}" stroke="#1F2937" stroke-width="1"/>')
        for lab, x in zip(labels, x_labels):
            out.append(H.text(x, y + 18, lab, 11, "#1F2937", "normal", "middle"))
    return "".join(out)


def plate():
    layers = [
        table(), sheet(), course(), ruler(), markers(),
        H.text(436.0, 379.0, "31.9", 15, "#B91C1C", "bold", "start", halo="#FFFFFF"),
        latitude_scale(), dividers(), scale_bars(),
    ]
    c = S.callout
    layers.append("".join([
        c(1, 440, 323, 417, 347), c(2, 113.7, 139.5, 131.7, 177.5), c(3, 245, 347, 270, 315), c(4, 615, 215.5, 588, 190), c(5, 140.1, 417, 116.1, 417), c(6, 146, 445, 122, 445),
    ]))
    return {
        "id": "fig-20-02-chart-scale",
        "replaces": "fig-20-02-chart-scale.svg",
        "book_file": "plate-20-02-chart-scale.jpg",
        "caption": "Figure 20-2. Measuring a leg with a ruler, and checking it on the latitude scale",
        "desc": "Figure 20-2. Measuring a leg with a ruler, and checking it on the latitude scale",
        "legend": [
            "Aerodrome A.",
            "Point WADI.",
            "A ruler along the line, zero at WADI: 31.9 cm at A.",
            "Dividers set to the same length on a meridian: 86 minutes of latitude, 86 NM. The numbers are minutes.",
            "The chart's scale line in nautical miles.",
            "The scale line in kilometres.",
        ],
        "canvas": [640, 465],
        "background": "pale",
        "reskin": {"svg": "fig-20-02-chart-scale.svg", "blank": True, "layers": layers},
    }
