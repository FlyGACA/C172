"""Figure 22-5. Right-of-way geometry: converging, head-on, overtaking and landing. Four cards. The first three are aerial views of the desert (figs/terrain.py) with the aeroplanes of the
model from above: the one that has the right of way in green, the one that gives way in orange, its path as an orange ribbon, the tracks dashed; the fourth is a side view at dusk-free
daylight (sky, hills, the plain, a runway) with the aeroplane on final approach (green), the higher one that gives way (orange, with its dashed way out) and the one waiting on the surface
(orange). The eight numbered callouts of the old figure (3 twice, as it had it) are kept, in the same order and meaning (figs/scene.py makes the cards, the ribbons and the callouts;
figs/h_a2.py the pavement)."""
from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 430
terrain.ensure("terrain-22-05", size=(W * 4, HT * 4), seed=225, kind="plain", features=("wadis", "tracks"), veil=0.32, soft=2.8)

U = "a225"
GREEN, ORANGE = "#047857", "#B45309"
PLANE_GREEN, PLANE_ORANGE = "#13A874", "#F0862A"
n = S.n
SHADOW = {"dx": 1.5, "dy": 2.3, "blur": 1.7, "opacity": 0.32}
OUT = {"width": 0.5, "colour": "#1F2A3A", "opacity": 0.85}
CARDS = {"A": (8, 8, 306, 202), "B": (326, 8, 306, 202), "C": (8, 222, 306, 200), "D": (326, 222, 306, 200)}


def defs():
    return ("<defs>" + H.shadow_filter(U + "cs", 0, 2.4, 3.2, 0.30, "#10233F") + H.asphalt_filter(U + "as", seed=6, relief=0.7, tone=0.0) + H.blur_filter(U + "bl", 1.3)
            + S.gradient(U + "bg", [(0, "#F7FAFE"), (1, "#E4EDF7")]) + S.gradient(U + "pl", [(0, "#E9D9AE"), (1, "#CDB380")]) + "".join(f'<clipPath id="{U}c{k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath>' for k, (x, y, w, h) in CARDS.items())
            + "</defs>")


def card(k, inner):
    x, y, w, h = CARDS[k]
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#FFFFFF" filter="url(#{U}cs)"/>', f'<g clip-path="url(#{U}c{k})">', *inner, "</g>",
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>']


def terrain_inner(extra=""):
    return [{"name": "terrain-22-05", "at": [W / 2, HT / 2], "width": W}, extra]


def dashed(x0, y0, x1, y1):
    return (f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="4.2"/>'
            f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#5E6878" stroke-width="1.6" stroke-dasharray="5 5"/>')


def way(uid, points, width=5.4):
    """The path of the aeroplane that gives way: an orange ribbon."""
    return S.ribbon(uid, points, width, "#C2570C", "#F7A24E", head=2.0, tail=0.7, per=8)


def top(x, y, angle, tint, width=44):
    return {"name": "sprite-top", "at": [x, y], "width": width, "angle": angle, "tint": {GREEN: PLANE_GREEN, ORANGE: PLANE_ORANGE}[tint], "tint_strength": 0.78, "outline": OUT, "shadow": SHADOW}


def go(uid, points):
    return S.ribbon(uid, points, 4.6, GREEN, "#34C08A", head=2.0, tail=0.8, per=4)


# ------------------------------------------------------------------------------------------------------------------ the four cards
def card_a():
    inner = terrain_inner(dashed(126, 196, 126, 82) + dashed(312, 82, 126, 82)
                          + f'<circle cx="126" cy="82" r="7" fill="#FFFFFF" fill-opacity="0.4" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.9"/><circle cx="126" cy="82" r="7" fill="none" stroke="#B91C1C" stroke-width="2.2"/>')
    inner.append(way(U + "a1", [(126, 164), (134, 146), (162, 130), (212, 124), (262, 120), (290, 102), (298, 72), (298, 47), (298, 40)]))
    inner.append(go(U + "a2", [(214, 82), (200, 82), (182, 82)]))
    inner += [top(233.4, 82, 270, GREEN), top(126, 183.4, 0, ORANGE)]
    return card("A", inner)


def card_b():
    inner = terrain_inner(dashed(400, 100, 560, 100))
    inner.append(way(U + "b1", [(400, 100), (430, 104), (458, 122), (492, 142), (523, 148.5), (532, 150.5)]))
    inner.append(way(U + "b2", [(560, 100), (530, 96), (502, 78), (468, 58), (437, 51.5), (428, 49.5)]))
    inner += [top(380.6, 100, 90, ORANGE), top(579.4, 100, 270, ORANGE)]
    return card("B", inner)


def card_c():
    inner = terrain_inner(dashed(140, 370, 140, 284))
    inner.append(way(U + "c1", [(140, 370), (148, 344), (176, 322), (198, 296), (200, 262), (195.5, 240.9), (194, 232)]))
    inner.append(go(U + "c2", [(140, 246), (140, 238), (140, 224)]))
    inner += [top(140, 263.4, 0, GREEN), top(140, 389.4, 0, ORANGE)]
    return card("C", inner)


def side(x, y, angle, tint, width):
    return {"name": "sprite-side", "at": [x, y], "width": width, "angle": angle, "tint": {GREEN: PLANE_GREEN, ORANGE: PLANE_ORANGE}[tint], "tint_strength": 0.78, "outline": OUT}


def card_d():
    x, y, w, h = CARDS["D"]
    sky = f'<defs>{S.gradient(U + "sk", [(0, "#7EAAD9"), (0.55, "#B7D2EE"), (1, "#EEF4FB")])}</defs><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{U}sk)"/>'
    hills = S.land_layer(U + "h1", S.ridge(11, x, x + w, 376, 18, step=4.0, peaks=0.5), 398, ("#8F9CC0", "#C1CBE0"), rim=False, haze=0.3, haze_colour="#E8F0FA")
    hills += S.land_layer(U + "h2", S.ridge(13, x, x + w, 388, 7, step=4.0), 399, ("#CDB085", "#E3CFA4"), rim=False, haze=0.1)
    ground = f'<rect x="{x}" y="396" width="{w}" height="{y + h - 396}" fill="url(#{U}pl)"/><line x1="{x}" y1="396.4" x2="{x + w}" y2="396.4" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="0.9"/>'
    runway = (f'<rect x="508" y="394" width="130" height="7" fill="#444" filter="url(#{U}as)"/><rect x="508" y="394" width="130" height="1.2" fill="#9AA3B2" opacity="0.7"/>'
              + "".join(f'<rect x="{xx}" y="397" width="8" height="1.2" fill="#F4F1E8"/>' for xx in range(520, 630, 14)))
    inner = [sky, hills, ground, runway, dashed(334, 340, 514, 394)]
    way_pts = [(424, 266), (470, 272), (520, 272), (580, 266), (609.7, 254.4)]
    inner.append(S.ribbon(U + "d1", way_pts + [(618, 251)], 4.6, "#C2570C", "#F7A24E", head=2.0, tail=0.7, opacity=0.85, per=6))
    inner.append(f'<polyline points="{S.pts(way_pts)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.5" stroke-dasharray="5 5" stroke-linecap="round"/>')
    inner.append(f'<ellipse cx="486" cy="395.4" rx="17" ry="2.2" fill="{H.SHADOW}" opacity="0.35" filter="url(#{U}bl)"/>')
    inner += [side(404, 262, 0, ORANGE, 50), side(440, 367.8, 12, GREEN, 50), side(486, 390.5, 0, ORANGE, 36)]
    return card("D", inner)


def callouts():
    c = S.callout
    return "".join([c(1, 232, 36, 232, 64), c(2, 88, 170, 112, 180), c(3, 480, 178, 486, 142), c(3, 480, 26, 476, 56), c(4, 88, 262, 122, 262), c(5, 250, 336, 184, 318),
                    c(6, 384, 312, 426, 362), c(7, 372, 234, 396, 254), c(8, 462, 336, 484, 386)])


def layers():
    out = [defs(), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>']
    out += card_a() + card_b() + card_c() + card_d()
    out.append(callouts())
    return out


def plate():
    return {
        "id": "fig-22-05-right-of-way",
        "replaces": "fig-22-05-right-of-way.svg",
        "book_file": "plate-22-05-right-of-way.jpg",
        "caption": "Figure 22-5. Right-of-way geometry: converging, head-on, overtaking and landing",
        "desc": "Figure 22-5. Right-of-way geometry: converging, head-on, overtaking and landing",
        "legend": [
            "Converging, same category, about the same altitude: the aircraft on the other's right has the right of way [[§91.61(d)]].",
            "The other gives way, here by turning right to pass behind, not over, under or ahead.",
            "Head-on or nearly so: both alter course to the right [[§91.61(e)]].",
            "Overtaking: the aircraft being overtaken has the right of way.",
            "The overtaking aircraft alters course to the right and passes well clear [[§91.61(f)]].",
            "Landing, side view: of two aircraft approaching to land, the lower has the right of way, though it may not cut in front of one on final approach or overtake it [[§91.61(g)]].",
            "The higher aircraft gives way: it extends or goes around.",
            "An aircraft on final approach has the right of way over aircraft on the surface, such as one waiting to enter the runway.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-22-05-right-of-way.svg", "blank": True, "layers": layers()},
    }
