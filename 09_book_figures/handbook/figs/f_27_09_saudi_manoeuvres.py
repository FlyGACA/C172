"""Figure 27-9 (new). These manoeuvres in Saudi Arabia, from the last section of Chapter 27: five scenes, one for each point of its box.

1 references over open desert (a farm circle, a track and a pipeline stand out from featureless dunes), 2 a forced-landing field within reach (the glide to flat firm ground, a cross over soft sand), 3 heat (afternoon thermals tossing the aeroplane),
4 the shamal (the 350 m circle seen from above in a 20 kt northwesterly, with the banks 43 degrees downwind and 21 degrees upwind), 5 dust and haze (a faint horizon: cross-check the attitude indicator). Shapes, colours and the numbers of the callouts; the only text
is 43°, 21° and 20 KT, from the chapter. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "ar279"
CELLS = ((10.0, 10.0, 200.0, 150.0), (220.0, 10.0, 200.0, 150.0), (430.0, 10.0, 200.0, 150.0), (10.0, 170.0, 305.0, 150.0), (325.0, 170.0, 305.0, 150.0))
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
HAZE = [(0.0, "#A8B8D2"), (0.5, "#DCD3BD"), (0.85, "#E8D2A2"), (1.0, "#E9D3A4")]
INK, RED, GREEN, BLUE = "#334155", "#B91C1C", "#15803D", "#1D4ED8"
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}


def panel(i, sky_stops, body):
    x, y, w, h = CELLS[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, w, h, sky_stops) + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def pill(cx, cy, w, text, fill="#1F2937", h=10.0):
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2 - 3.5)}" width="{n(w)}" height="{n(h + 7)}" rx="{n((h + 7) / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, h, fill="#FFFFFF"))


def scene_1():                                               # references over open desert
    x, y, w, h = CELLS[0]
    land = S.plain(f"{U}l1", x, x + w, y + 70, y + h, seed=4, tone="day", photo=True)
    dunes = S.dune(f"{U}d1", x, x + w, y + 84, 6.0, 3) + S.dune(f"{U}d2", x, x + w, y + 98, 5.0, 8)
    road = f'<path d="M{n(x + 128)} {n(y + h)} L{n(x + 162)} {n(y + 100)} L{n(x + 168)} {n(y + 100)} L{n(x + 148)} {n(y + h)} Z" fill="#6B7385"/><path d="M{n(x + 139)} {n(y + h)} L{n(x + 164)} {n(y + 100)}" stroke="#F1F5F9" stroke-width="1.4" stroke-dasharray="6 5"/>'
    pipe = f'<line x1="{n(x)}" y1="{n(y + 118)}" x2="{n(x + 126)}" y2="{n(y + 112)}" stroke="#3B4252" stroke-width="2.4"/><line x1="{n(x)}" y1="{n(y + 118)}" x2="{n(x + 126)}" y2="{n(y + 112)}" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.8"/>'
    farm = f'<ellipse cx="{n(x + 50)}" cy="{n(y + 128)}" rx="30" ry="11" fill="#5FA05A" stroke="#3E7A3A" stroke-width="1.6"/><ellipse cx="{n(x + 50)}" cy="{n(y + 128)}" rx="18" ry="6.5" fill="none" stroke="#8DC584" stroke-width="1.4"/><circle cx="{n(x + 50)}" cy="{n(y + 128)}" r="2.6" fill="#F1F5F9"/>'
    return panel(0, DAY, land + dunes + road + pipe + farm)


def scene_2():                                               # a forced-landing field within reach
    x, y, w, h = CELLS[1]
    field = f'<path d="M{n(x + 96)} {n(y + 118)} L{n(x + 184)} {n(y + 118)} L{n(x + 196)} {n(y + 138)} L{n(x + 84)} {n(y + 138)} Z" fill="#B9A682" stroke="#8A7650" stroke-width="1.2"/>'
    soft = S.dune(f"{U}d3", x, x + 82, y + 130, 8.0, 5, colours=("#F1E1B8", "#D7BC8A"))
    glide = f'<path d="M{n(x + 56)} {n(y + 50)} L{n(x + 100)} {n(y + 118)} M{n(x + 56)} {n(y + 50)} L{n(x + 182)} {n(y + 118)}" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="6 5" stroke-opacity="0.9"/>'
    check = f'<path d="M{n(x + 118)} {n(y + 128)} l9 9 l20 -22" fill="none" stroke="{GREEN}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>'
    cross = f'<path d="M{n(x + 20)} {n(y + 112)} l24 24 M{n(x + 44)} {n(y + 112)} l-24 24" stroke="{RED}" stroke-width="5.5" stroke-linecap="round"/>'
    return panel(1, DAY, S.plain(f"{U}l2", x, x + w, y + 92, y + h, seed=7, tone="day", photo=True) + soft + field + glide + check + cross)


def scene_3():                                               # heat: thermals under a high sun
    x, y, w, h = CELLS[2]
    sun = S.sun(f"{U}s3", x + 34, y + 36, 11)
    spirals = "".join(S.ribbon(f"{U}t3{k}", [(x + sx, y + 138), (x + sx - 10, y + 112), (x + sx + 10, y + 88), (x + sx - 8, y + 62)], 5.0, "#E8782E", "#F6B36B", opacity=0.85, head=2.0, tail=0.4, per=8) for k, sx in enumerate((70, 126, 176)))
    return panel(2, [(0.0, "#3A74C0"), (0.5, "#8FBBEA"), (0.85, "#F3E9C6"), (1.0, "#F6E8C0")], S.plain(f"{U}l3", x, x + w, y + 112, y + h, seed=3, tone="day", photo=True) + sun + spirals)


def scene_4():                                               # the shamal: the circle seen from above, the wind, the two banks
    x, y, w, h = CELLS[3]
    cx, cy, rx, ry = x + 160, y + 80, 78.0, 52.0
    ground = f'<defs><linearGradient id="{U}g4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBDCB4"/><stop offset="1" stop-color="#D5BC8B"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{U}g4)"/>'
    pts = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in [k * math.pi / 18 for k in range(0, 36)]] + [(cx + rx, cy + 1)]
    circle = S.ribbon(f"{U}c4", [(cx + rx * math.cos(a), cy - ry * math.sin(a)) for a in [-0.4 + k * (2 * math.pi - 0.2) / 24 for k in range(0, 25)]], 4.0, "#E8782E", "#F6B36B", opacity=0.9, head=2.2, tail=0.4, per=4)
    wind = S.ribbon(f"{U}w4", [(x + 56, y + 46), (x + 96, y + 72)], 9.0, "#1D4ED8", "#7FA7F0", opacity=0.9, head=2.0, tail=0.6, per=4)
    return panel(3, [(0.0, "#EBDCB4"), (1.0, "#D5BC8B")], ground + wind + circle + pill(x + 262, y + 112, 44, "43°", RED) + pill(x + 60, y + 102, 44, "21°", GREEN) + pill(x + 96, y + 24, 66, "20 KT", BLUE))


def scene_5():                                               # dust and haze: a faint horizon and the attitude indicator
    x, y, w, h = CELLS[4]
    haze = S.plain(f"{U}l5", x, x + w, y + 84, y + h, seed=9, tone="dusk", photo=True) + S.fog(f"{U}h5", x, x + w, y + 120, 90, seed=6, opacity=0.95, colour="#E0C890", wisp=1.0, foot=0.4)
    ai = (f'<circle cx="{n(x + 218)}" cy="{n(y + 66)}" r="30" fill="#1E3A8A" stroke="#E2E8F0" stroke-width="3.4"/><path d="M{n(x + 188)} {n(y + 66)} A30 30 0 0 1 {n(x + 248)} {n(y + 66)} Z" fill="#38BDF8"/><circle cx="{n(x + 218)}" cy="{n(y + 66)}" r="3.4" fill="#FACC15"/>'
          f'<path d="M{n(x + 200)} {n(y + 66)} H{n(x + 236)}" stroke="#FACC15" stroke-width="3.4" stroke-linecap="round"/>')
    return panel(4, HAZE, haze + ai)


def sprites():
    o = lambda name, x, y, wd, **k: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **k}
    x1, y1 = CELLS[1][0], CELLS[1][1]
    x2, y2 = CELLS[2][0], CELLS[2][1]
    x3, y3 = CELLS[3][0], CELLS[3][1]
    x4, y4 = CELLS[4][0], CELLS[4][1]
    return [o("sprite-side", x1 + 56, y1 + 50, 40, angle=6.0), o("sprite-side", x2 + 110, y2 + 70, 44, angle=-10.0), o("sprite-top", x3 + 160, y3 + 80, 32, angle=0.0), o("sprite-side", x4 + 96, y4 + 80, 56, opacity=0.8)]


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(5))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="330" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), scene_5(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-27-09-saudi-manoeuvres",
        "replaces": "fig-27-09-saudi-manoeuvres.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-27-09-saudi-manoeuvres.jpg",
        "caption": "Figure 27-9. These manoeuvres in Saudi Arabia: references, a forced-landing field, heat, the shamal, dust and haze",
        "desc": ("Figure 27-9. These manoeuvres in Saudi Arabia, five scenes: a farm circle, a track and a pipeline stand out from featureless dunes; a forced-landing field of flat firm ground within reach, not soft sand; afternoon thermals; "
                 "the 350 m circle in a 20 kt shamal needs about 43° of bank downwind and 21° upwind; dust and haze leave a faint horizon, so cross-check the attitude indicator."),
        "legend": [
            "References over open desert: dunes and gravel plains look alike, so use roads, tracks, pipelines, the banks of a wadi bed and farm circles, which give a circle and a centre point. Check that a reference still stands out from the far side, into the sun.",
            "A forced-landing field within reach throughout: flat, firm ground, not soft sand or a field crossed by irrigation equipment.",
            "Heat: afternoon thermals make the air bumpy at these heights, and morning air is usually smoother. High density altitude leaves less power for a steep turn and widens every turn.",
            "The shamal: in 20 kt of wind, at 90 kt, the 350 m circle needs about 43° downwind and 21° upwind: near the limit, so widen the radius.",
            "Dust and haze can leave a faint or false horizon: cross-check the attitude indicator more often, and postpone the lesson when the horizon is poor.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
