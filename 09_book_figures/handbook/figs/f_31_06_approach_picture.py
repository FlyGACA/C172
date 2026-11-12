"""Figure 31-6. The approach picture at night: too high, on the path and too low. Three night windscreens and, under them, the three approaches in profile, on the old figure's canvas.
The windscreens are night scenes: a strip of starry sky over a black plain, the runway an asphalt trapezoid between its glowing edge lamps (white), with the green threshold row at its near
end, the red end row at its far end, the approach lights on the centre line below the threshold and the PAPI lamps (four white, two white and two red, four red) beside it; every lamp is
taken from the old drawing, so the shapes, the sizes and the places are the old figure's. Below: a night profile, the three paths to the threshold (the correct one a glowing green ribbon,
the other two dashed), the model's aeroplane by moonlight on each, the PAPI lamps at the threshold. The eight numbered callouts of the old figure are kept."""
import math
import os
import re

from figs import scene as S
from figs import h_a3 as H
from figs.kit import NIGHT, side_plane

n = S.n
U = "f3106"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3
GREEN = ("#0F9460", "#7DEBB4")
SKY = [(0, "#070D22"), (0.09, "#101D42"), (0.13, "#2A3C6E"), (0.1375, "#34467A"), (0.139, "#05070D"), (1, "#05070D")]
CARDS = [(15, 12, 196, 175), (222, 12, 196, 175), (429, 12, 196, 175)]
RUNWAYS = [[(71.9, 174.7), (154.1, 174.7), (131.7, 99.1), (94.3, 99.1)], [(278.9, 105.2), (361.1, 105.2), (338.7, 67.4), (301.3, 67.4)], [(485.9, 70.6), (568.1, 70.6), (545.7, 51.7), (508.3, 51.7)]]
PAPI_ROWS = [(151.6, 35.0), (93.6, 242.0), (64.8, 449.0)]               # y and first x of the PAPI lamps in the three windscreens (four lamps, 7.3 apart)
COLOURS = {"#ffffff": "w", "#047857": "g", "#b91c1c": "r"}


def old_lamps():
    """Every lamp of the three windscreens as the old drawing has it: [(x, y, r, colour)] per card (its halos and its callout discs left out)."""
    with open(os.path.join(HERE, "old", "fig-31-06-approach-picture.svg"), encoding="utf-8") as f:
        svg = f.read()
    circles = [(float(x), float(y), float(r), fill, op) for x, y, r, fill, op in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="(#[0-9a-f]+)"( opacity="[\d.]+")?', svg)]
    out = []
    for cx, cy, cw, ch in CARDS:
        out.append([(x, y, r, COLOURS[fill]) for x, y, r, fill, op in circles if cx <= x <= cx + cw and cy <= y <= cy + ch and fill in COLOURS and not op])
    return out


def window(k, lamps):
    x, y, w, h = CARDS[k]
    uid = f"{U}w{k}"
    poly = RUNWAYS[k]
    hz = 36.0
    body = [H.stars(x, y, w, hz - y, 16, seed=61 + k), f'<defs>{S.gradient(uid + "as", [(0, "#171E31"), (1, "#3A4560")])}<radialGradient id="{uid}ag" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFD9A0" stop-opacity="0.18"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient></defs>',
            f'<line x1="{x + 8}" y1="{hz}" x2="{x + w - 8}" y2="{hz}" stroke="#8FA0C8" stroke-opacity="0.45" stroke-width="1"/>',
            f'<ellipse cx="{(poly[0][0] + poly[1][0]) / 2}" cy="{(poly[0][1] + poly[2][1]) / 2}" rx="{(poly[1][0] - poly[0][0]) * 0.95}" ry="{(poly[0][1] - poly[2][1]) * 0.75}" fill="url(#{uid}ag)"/>',
            f'<polygon points="{S.pts(poly)}" fill="url(#{uid}as)"/>']
    # the lamps, nearest last so that the big ones lie over the small
    mid = (poly[0][0] + poly[1][0]) / 2
    row_y, row_x = PAPI_ROWS[k]
    for lx, ly, r, c in sorted(lamps, key=lambda a: a[1]):
        if abs(ly - row_y) < 0.2 and row_x - 1 <= lx <= row_x + 24:                 # the PAPI
            body.append(H.lamp(U, lx, ly, c, 2.3, 1.0))
        elif abs(lx - mid) < 0.7 and ly > poly[0][1] - 1:                              # the approach lights on the centre line
            body.append(H.lamp(U, lx, ly, c, 0.42 * r + 0.1, 0.4))
        else:
            body.append(H.lamp(U, lx, ly, c, 0.55 * r + 0.2, 0.42 if r < 1.6 else 0.6))
    return S.card(uid + "c", x, y, w, h, SKY, "".join(body))


def paths():
    out = []
    ends = [(25, 211.7), (25, 303.6), (25, 349.3)]
    for i, (sx, sy) in enumerate(ends):
        d = f"M {sx},{sy} L 490,393"
        if i == 1:
            out.append(f'<path d="{d}" fill="none" stroke="#3EE59A" stroke-opacity="0.30" stroke-width="8" stroke-linecap="round" filter="url(#{U}b2)"/>')
            out.append(S.ribbon(U + "gp", [(sx, sy), ((sx + 490) / 2, (sy + 393) / 2), (490, 393)], 4.6, *GREEN, head=1.0, opacity=0.95))
        else:
            out.append(f'<path d="{d}" fill="none" stroke="#BCD0FF" stroke-opacity="0.26" stroke-width="5" stroke-linecap="round" filter="url(#{U}b2)"/>'
                       f'<path d="{d}" fill="none" stroke="#DCE6FF" stroke-opacity="0.9" stroke-width="1.6" stroke-dasharray="6 4.4" stroke-linecap="round"/>')
    return "".join(out)


def profile():
    x, y, w, h = 10, 197, 620, 213
    hz = 393.0
    body = [H.stars(x, y, w, hz - y - 20, 80, seed=64),
            f'<defs>{S.gradient(U + "pgr", [(0, "#0A0F1C"), (1, "#05070D")])}{S.gradient(U + "phz", [(0, "#2C3C6C", 0.0), (0.55, "#2C3C6C", 0.55), (1, "#2C3C6C", 0.0)])}'
            f'<radialGradient id="{U}pag" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFD9A0" stop-opacity="0.22"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{U}pas" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#46526F"/><stop offset="1" stop-color="#1A2133"/></linearGradient></defs>'
            f'<rect x="{x}" y="{hz}" width="{w}" height="{y + h - hz}" fill="url(#{U}pgr)"/><rect x="{x}" y="{hz - 12}" width="{w}" height="22" fill="url(#{U}phz)"/>'
            f'<ellipse cx="530" cy="{hz}" rx="120" ry="22" fill="url(#{U}pag)"/>'
            f'<polygon points="{S.pts([(430, 393), (625, 393), (628, 399.4), (427, 399.4)])}" fill="url(#{U}pas)"/>'
            f'<line x1="430" y1="393" x2="625" y2="393" stroke="#9FB0D4" stroke-opacity="0.35" stroke-width="0.8"/>']
    body.append(H.lamp_row(U, [(436 + 15.5 * i, 392.6) for i in range(13)], "w", 1.35, 0.9))
    return S.card(U + "P", x, y, w, h, [(0, "#070D22"), (0.5, "#14214A"), (0.9, "#2A3C6E"), (0.925, "#05070D"), (1, "#05070D")], "".join(body))


def profile_papi():
    return "".join(H.lamp(U, x, 390, c, 2.1, 0.95) for x, c in ((482, "w"), (487, "w"), (492, "r"), (497, "r")))


def callouts():
    c = S.callout
    return "".join([c(1, 29, 25), c(2, 236, 25), c(3, 443, 25), c(4, 397, 131, 363, 107), c(5, 389, 94, 352.5, 85.6), c(6, 354, 68, 326, 66.4), c(7, 248, 68, 252, 92), c(8, 276, 138, 316, 127),
                    c(1, 66, 247), c(2, 66, 319), c(3, 66, 355), c(7, 516, 369, 494, 388)])


def plate():
    planes = [side_plane(130, 253.1, 13.2, 1.0, SILHOUETTE, grow=1.9, look=NIGHT), side_plane(130, 324.2, 6.6, 1.0, SILHOUETTE, grow=1.9, look=NIGHT),
              side_plane(130, 359.6, 3.3, 1.0, SILHOUETTE, grow=1.9, look=NIGHT)]
    lamps = old_lamps()
    layers = ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', H.common_defs(U), H.night_defs(U)]
    layers += [window(k, lamps[k]) for k in range(3)]
    layers += [profile(), paths(), profile_papi(), *planes, callouts()]
    return {
        "id": "fig-31-06-approach-picture",
        "replaces": "fig-31-06-approach-picture.svg",
        "book_file": "plate-31-06-approach-picture.jpg",
        "caption": "Figure 31-6. The approach picture at night: too high, on the path and too low",
        "desc": "Figure 31-6. The approach picture at night: too high, on the path and too low",
        "legend": [
            "Too high: runway long and steep; four white.",
            "On the path: two white, two red.",
            "Too low: runway flat and short; four red.",
            "Threshold lights, green.",
            "Edge lights, white.",
            "End lights, red.",
            "PAPI.",
            "Approach lights.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-31-06-approach-picture.svg", "blank": True, "layers": layers},
    }
