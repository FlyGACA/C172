"""Figure 17-8. The worked example in profile along the route. A cut through the country in a card: the ground as a slice of desert (a front of sand and rock following the old figure's
profile, the ground seen from above along its back edge, a runway at each end), the control zone (Class D) and the terminal control area (Class C) as translucent blocks of glass with
depth, Class E and Class G as faint veils either side of the dashed base of Class E, the route as a green line with a casing and the model at its cruise, the 500 ft margins as short
orange dimension lines, the heights on the left and the distances below. Every altitude, floor, distance and place of the old figure is kept, with its eight numbered callouts
(figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

CARD = (62, 14, 566, 324)
DX, DY = 10.0, 8.0
GREEN, BLUE, AMBER, GREY = "#047857", "#1D4ED8", "#B45309", "#4B5563"
TERRAIN = [(70.0, 273.8), (140.8, 271.9), (193.9, 266.2), (247.0, 268.1), (309.0, 258.8), (388.7, 247.5), (450.7, 253.1), (530.3, 256.9), (610.0, 255.0)]
CTR = [(70, 198.8), (140.8, 198.8), (140.8, 273.8), (70, 273.8)]
TMA = [(140.8, 30), (247, 30), (247, 161.2), (193.9, 161.2), (193.9, 198.8), (140.8, 198.8)]
BASE_E = [(140.8, 234.4), (193.9, 228.8), (247.0, 230.6), (309.0, 221.2), (388.7, 210.0), (450.7, 215.6), (530.3, 219.4), (610.0, 217.5)]
ROUTE = "M 70 273.8 L 105.4 217.5 L 193.9 217.5 L 211.6 180 L 247 180 L 278 123.8 L 521.5 123.8 L 565.7 217.5 L 601.1 232.5 L 610 255"


def veils():
    """Class G between the ground and the base of Class E, Class E above it (to the top, round the terminal area): two faint veils."""
    g = [(x, y) for x, y in TERRAIN if x >= 140.8] + list(reversed(BASE_E))
    e = list(BASE_E) + [(610, 30), (247, 30), (247, 161.2), (193.9, 161.2), (193.9, 198.8), (140.8, 198.8)]
    grad = S.gradient
    return (f'<defs>{grad("a1vg", [(0, "#E8C98A", 0.3), (1, "#E8C98A", 0.12)])}{grad("a1ve", [(0, "#FFFFFF", 0.0), (1, "#FFFFFF", 0.26)])}</defs>'
            f'<polygon points="{S.pts(g)}" fill="url(#a1vg)"/><polygon points="{S.pts(e)}" fill="url(#a1ve)"/>')


def grid():
    out = []
    for ft, y in ((2000, 255), (4000, 180), (6000, 105), (8000, 30)):
        out.append(H.line_cased(70, y, 610, y, "#FFFFFF", 0.9, dash="3 4", casing=0.0, opacity=0.55))
    return "".join(out)


def ground():
    """The slice of ground: hills far behind, the top surface (the strip between the profile and the same profile moved back and up), the front of rock and sand, a runway each end."""
    strip = TERRAIN + [(x + DX, y - DY) for x, y in reversed(TERRAIN)]
    out = [S.land_layer("a1h", S.ridge(171, 66, 626, 250, 22, peaks=0.6), 272, ("#8391B3", "#BDC8DD"), rim=True, haze=0.3)]
    out.append(f'<defs>{S.gradient("a1gt", [(0, "#F1E3BC"), (1, "#DCC592")])}{S.gradient("a1gr", [(0, "#C9B287"), (1, "#8A7250")], 0, 0, 1, 0)}</defs>'
               f'<polygon points="{S.pts(strip)}" fill="url(#a1gt)"/>')
    out.append(S.scrub(9, 80, 610, 236, 268, 18, scale=0.55))
    for x0, x1, k in ((72, 100, 0), (576, 604, -1)):
        y = TERRAIN[0][1] if k == 0 else TERRAIN[-1][1]
        out.append(f'<polygon points="{S.pts([(x0, y - 2), (x1, y - 2), (x1 + 5, y - 6.2), (x0 + 5, y - 6.2)])}" fill="#3E4756"/><line x1="{x0 + 3}" y1="{S.n(y - 4.2)}" x2="{x1 + 3}" y2="{S.n(y - 4.2)}" stroke="#F4F6FA" stroke-width="0.9" stroke-dasharray="4 3"/>')
    right = [(610, 255), (610 + DX, 255 - DY), (610 + DX, 330 - DY), (610, 330)]
    out.append(f'<polygon points="{S.pts(right)}" fill="url(#a1gr)"/>')
    out.append(S.rock("a1rk", TERRAIN, 330, 70, 610, 12, tones=("#E6D2A2", "#9C7D52")))
    return "".join(out)


def label(x, y, text, colour, w=40):
    return H.pill(x, y, w, 16, text, colour, 11, border=colour)


def layers():
    x, y, w, h = CARD
    out = [H.page("a1page", 640, 380), H.defs()]
    out.append(S.card("a1rc", x, y, w, h, H.horizon_sky(0.76), S.glow("a1rg", 150, 70, 200, "#FFF1CC", 0.5), radius=10))
    out.append(S.card_front("a1rw", x, y, w, h, veils() + grid() + ground(), radius=10))
    out.append(S.card_front("a1rb", x, y, w, h, H.glass_prism("a1ctr", CTR, DX, DY, "#5E8CEB", 0.42, BLUE) + H.glass_prism("a1tma", TMA, DX, DY, "#8DB0F5", 0.34, BLUE), radius=10))
    for t, cx, cy, col, size in (("D", 123.1, 243.8, BLUE, 16), ("C", 193.9, 82.5, BLUE, 16), ("E", 406.4, 168.8, GREY, 16), ("G", 335.6, 241.9, GREY, 13)):
        out.append(f'<text x="{cx}" y="{cy}" font-family="monospace" font-size="{size}" font-weight="bold" fill="{col}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke">{t}</text>')
    # the base of Class E, the route, the turning point
    pts_e = " L ".join(f"{px},{py}" for px, py in BASE_E)
    out.append(H.path_line(f"M {pts_e}", "#6B7280", 1.6, dash="6 4", casing=2.0, glow=False))
    out.append(H.line_cased(362.1, 127.8, 362.1, 336, "#6B7A91", 1.2, dash="3 3", casing=2.0))
    out.append(H.line_cased(140.8, 274, 140.8, 337, "#6B7A91", 1.2, dash="3 3", casing=2.0))
    out.append(H.path_line(ROUTE, GREEN, 3.0, casing=2.6))
    out.append({"name": "sprite-side", "at": [405, 118.4], "width": 56, **H.LOOK})
    out.append(H.dim_line(185.1, 200.8, 185.1, 215.5, AMBER, 1.6, head=5, casing=2.0) + H.dim_line(233.8, 163.2, 233.8, 178, AMBER, 1.6, head=5, casing=2.0))
    out.append(label(167.4, 189.5, "3 500", BLUE) + label(213.4, 151.5, "4 500", BLUE) + label(335.6, 111.5, "5 500", GREEN, 44))
    # the scales
    for ft, yy in ((0, 330), (2000, 255), (4000, 180), (6000, 105), (8000, 30)):
        t = "0" if ft == 0 else f"{ft // 1000} 000"
        out.append(f'<text x="56" y="{yy + 4}" font-family="sans-serif" font-size="12" fill="#1F2937" text-anchor="end">{t}</text>')
    for k, t in enumerate(("0", "10", "20", "30", "40", "50", "60")):
        out.append(f'<text x="{S.n(70 + 88.5 * k + (0.1 if k == 6 else 0))}" y="366" font-family="sans-serif" font-size="12" fill="#1F2937" text-anchor="middle">{t}</text>')
    c = S.callout
    out.append("".join([c(1, 87.7, 172, 88, 200, r=10), c(2, 108, 131.2, 140.8, 131.2, r=10), c(3, 140.8, 348, r=10), c(4, 162.1, 208.1, r=10), c(5, 300.2, 111.8, r=10),
                         c(6, 477.2, 191.2, 477.2, 217, r=10), c(7, 583.4, 198.8, 583.4, 225, r=10), c(8, 362.1, 348, r=10)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-17-08-route-profile",
        "replaces": "fig-17-08-route-profile.svg",
        "book_file": "plate-17-08-route-profile.jpg",
        "caption": "Figure 17-8. The worked example in profile along the route",
        "desc": "Figure 17-8. The worked example in profile along the route",
        "legend": [
            "Control zone, Class D, to 3 500 ft: in contact with the tower.",
            "TMA, Class C, floors 3 500 ft and 4 500 ft; no clearance, so stay below.",
            "Point WADI, 8 NM.",
            "500 ft margins below the floors.",
            "Cruise at 5 500 ft.",
            "Base of Class E, 1 000 ft above the ground (dashed); Class G beneath.",
            "Descent into Class G and the circuit at B.",
            "Turning point T, 33 NM.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-17-08-route-profile.svg", "blank": True, "layers": layers()},
    }
