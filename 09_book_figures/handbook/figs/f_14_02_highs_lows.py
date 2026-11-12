"""Figure 14-2. Isobars and surface wind around a high and a low in the northern hemisphere. Drawn again as a weather map on the old figure's canvas: a pale chart ground with its faint
grid, the pressure as smooth shading (warm over the high, soft blue over the low), the isobars as clean blue curves with a white casing and their values on small plates, the surface
wind as dark ribbons that follow the old arrows round the high (clockwise, outward) and the low (anticlockwise, inward), a sun at the high and a cloud with rain at the low; and the
inset, on its own card with the pressure gradient shaded, the wind above the friction layer along the isobars (blue ribbon) and the surface wind turned 30° toward the low. Every
number, direction and callout of the old figure is kept (figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S

HIGH, LOW = (168.0, 178.0), (492.0, 178.0)
HIGH_ISO = [(48, 36, "1024", 218), (94, 70, "1020", 252), (140, 104, "1016", 286)]
LOW_ISO = [(24, 19, "1000", 201), (48, 38, "1004", 220), (72, 57, "1008", 239), (96, 76, "1012", 258)]
HIGH_ARROWS = [((278.3, 190.8), (277.6, 224.8)), ((202.7, 254.6), (174.0, 272.8)), ((94.7, 238.8), (62.1, 229.1)), ((57.7, 165.2), (58.4, 131.2)), ((133.3, 101.4), (162.0, 83.2)), ((241.3, 117.2), (273.9, 126.9))]
LOW_ARROWS = [((558.3, 191.6), (545.7, 164.4)), ((512.2, 230.1), (531.8, 207.3)), ((447.0, 218.9), (477.0, 218.5)), ((425.7, 164.4), (438.3, 191.6)), ((471.8, 125.9), (452.2, 148.7)),
              ((537.0, 137.1), (507.0, 137.5)), ((561.8, 225.7), (567.7, 196.3)), ((406.1, 203.8), (432.4, 218.2)), ((505.6, 105.7), (478.4, 118.3))]
SLATE = ("#1B2433", "#5A6780")


def ground():
    out = [f'<defs>{S.gradient("m2g", [(0, "#F8F5EC"), (1, "#EDF1F4")])}'
           '<radialGradient id="m2h" gradientUnits="userSpaceOnUse" cx="168" cy="178" r="1" gradientTransform="translate(168 178) scale(190 140) translate(-168 -178)"><stop offset="0" stop-color="#FFA94D" stop-opacity="0.62"/><stop offset="0.55" stop-color="#FFC77F" stop-opacity="0.32"/><stop offset="1" stop-color="#FFD9A6" stop-opacity="0"/></radialGradient>'
           '<radialGradient id="m2l" gradientUnits="userSpaceOnUse" cx="492" cy="178" r="1" gradientTransform="translate(492 178) scale(132 102) translate(-492 -178)"><stop offset="0" stop-color="#4C86E6" stop-opacity="0.62"/><stop offset="0.55" stop-color="#7BAAF0" stop-opacity="0.32"/><stop offset="1" stop-color="#A9C8F6" stop-opacity="0"/></radialGradient></defs>'
           '<rect x="0" y="0" width="640" height="400" fill="url(#m2g)"/>']
    for x in range(0, 641, 64):
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="400" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.2"/>')
    for y in range(8, 401, 64):
        out.append(f'<line x1="0" y1="{y}" x2="640" y2="{y}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.2"/>')
    out.append('<ellipse cx="168" cy="178" rx="190" ry="140" fill="url(#m2h)"/><ellipse cx="492" cy="178" rx="132" ry="102" fill="url(#m2l)"/>')
    return "".join(out)


def isobars(centre, rings, side):
    out = []
    cx, cy = centre
    for rx, ry, _lab, _ly in rings:
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="5"/>')
    for rx, ry, _lab, _ly in rings:
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#2358C8" stroke-width="2"/>')
    for rx, ry, lab, ly in rings:
        lx = cx + side                                                                              # the values sit on their ring, a little off the vertical so that no arrow touches them
        ly = cy + ry * math.sqrt(max(0.0, 1 - (side / rx) ** 2)) + 3.6
        out.append(f'<rect x="{lx - 16}" y="{ly - 10.5}" width="32" height="14.5" rx="7.25" fill="#FFFFFF" stroke="#2358C8" stroke-width="0.8"/>' + H.text(lx, ly + 0.8, lab, 10, "#1E4DB0", "bold", "middle"))
    return "".join(out)


def sun(cx, cy):
    out = [S.glow("m2s", cx, cy, 36, "#FFD27A", 0.75)]
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<line x1="{S.n(cx + 13.5 * math.cos(a))}" y1="{S.n(cy + 13.5 * math.sin(a))}" x2="{S.n(cx + 19.5 * math.cos(a))}" y2="{S.n(cy + 19.5 * math.sin(a))}" stroke="#E8860E" stroke-width="2.6" stroke-linecap="round"/>')
    out.append(f'<defs><radialGradient id="m2d" cx="0.35" cy="0.3" r="0.85"><stop offset="0" stop-color="#FFF6D2"/><stop offset="0.6" stop-color="#FFC75A"/><stop offset="1" stop-color="#F08A1C"/></radialGradient></defs>'
               f'<circle cx="{cx}" cy="{cy}" r="10.5" fill="url(#m2d)" stroke="#FFFFFF" stroke-width="1.4"/>')
    return "".join(out)


def rain_streaks(cx, cy):
    out = []
    for dx in (-6.7, 0.0, 6.7):
        out.append(f'<line x1="{S.n(cx + dx + 1.2)}" y1="{S.n(cy)}" x2="{S.n(cx + dx - 0.8)}" y2="{S.n(cy + 7)}" stroke="#FFFFFF" stroke-width="4.2" stroke-linecap="round" stroke-opacity="0.8"/>'
                   f'<line x1="{S.n(cx + dx + 1.2)}" y1="{S.n(cy)}" x2="{S.n(cx + dx - 0.8)}" y2="{S.n(cy + 7)}" stroke="#2358C8" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="3 2.4"/>')
    return "".join(out)


def wind(arrows, centre, tag):
    out = []
    for i, (a, b) in enumerate(arrows):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nx, ny = -dy / length, dx / length
        if (centre[0] - mx) * nx + (centre[1] - my) * ny < 0:
            nx, ny = -nx, -ny
        m = (mx + nx * 0.11 * length, my + ny * 0.11 * length)
        out.append(H.ribbon(f"m2{tag}{i}", [a, m, b], width=5.6, colours=SLATE, head=2.0, casing=1.7, per=8))
    return "".join(out)


def inset():
    x, y, w, h = 300, 298, 332, 96
    out = [f'<defs>{S.gradient("m2i", [(0, "#9DBFF3"), (0.5, "#E8EEF6"), (1, "#FFD59B")])}'
           '<clipPath id="m2ic"><rect x="300" y="298" width="332" height="96" rx="9"/></clipPath>'
           '<filter id="m2is" x="-6%" y="-12%" width="112%" height="130%"><feDropShadow dx="0" dy="2.4" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.32"/></filter></defs>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#FFFFFF" filter="url(#m2is)"/>',
           f'<g clip-path="url(#m2ic)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#m2i)"/>']
    for yy in (318, 378):
        out.append(f'<line x1="308" y1="{yy}" x2="622" y2="{yy}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="5"/><line x1="308" y1="{yy}" x2="622" y2="{yy}" stroke="#2358C8" stroke-width="2"/>')
    out.append("</g>")
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>')
    for yy, lab in ((314, "1008"), (374, "1012")):
        out.append(f'<rect x="309" y="{yy - 11}" width="34" height="14.5" rx="7.25" fill="#FFFFFF" stroke="#2358C8" stroke-width="0.8"/>' + H.text(326, yy + 0.2, lab, 10, "#1E4DB0", "bold", "middle"))
    # the wind above the friction layer (along the isobars, low on the left) and at the surface (turned 30 degrees toward the low)
    out.append(H.ribbon("m2a1", [(370, 346), (470, 346)], width=6.0, colours=("#1B3E94", "#5B86E0"), head=2.0, casing=1.8))
    out.append('<line x1="515" y1="366" x2="605" y2="366" stroke="#FFFFFF" stroke-width="1.4" stroke-dasharray="4 3" stroke-opacity="0.95"/>')
    out.append(H.ribbon("m2a2", [(515, 366), (592.9, 321)], width=6.0, colours=SLATE, head=2.0, casing=1.8))
    out.append(H.text(577, 362, "30°", 11, "#1F2937", "bold", "start", halo="#FFFFFF"))
    return "".join(out)


def plate():
    cloud = {"name": "cloud-cumulus-b", "at": [492, 171], "width": 46}
    layers = [
        ground(),
        isobars(HIGH, HIGH_ISO, -22), isobars(LOW, LOW_ISO, 4),
        sun(168, 178),
        cloud, rain_streaks(492, 183),
        wind(HIGH_ARROWS, HIGH, "h"), wind(LOW_ARROWS, LOW, "l"),
        inset(),
    ]
    c = S.callout
    layers.append("".join([
        c(1, 140, 184, 158, 180), c(2, 522, 170, 506, 174), c(3, 196, 58, 194, 76), c(4, 48, 206, 62, 184), c(5, 602, 138, 568, 142),
        c(6, 180, 306, 176, 272), c(7, 420, 94, 468, 129), c(8, 420, 366, 420, 349), c(9, 534, 336, 548, 347),
    ]))
    return {
        "id": "fig-14-02-highs-lows",
        "replaces": "fig-14-02-highs-lows.svg",
        "book_file": "plate-14-02-highs-lows.jpg",
        "caption": "Figure 14-2. Isobars and surface wind around a high and a low in the northern hemisphere",
        "desc": "Figure 14-2. Isobars and surface wind around a high and a low in the northern hemisphere",
        "legend": [
            "High.",
            "Low.",
            "Isobar, in hPa.",
            "Widely spaced isobars: light wind.",
            "Closely spaced isobars: strong wind.",
            "Clockwise around the high, spiralling out.",
            "Anticlockwise around the low, spiralling in.",
            "Above the friction layer: along the isobars, low pressure on the left.",
            "At the surface: turned across the isobars toward the low.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-14-02-highs-lows.svg", "blank": True, "layers": layers},
    }
