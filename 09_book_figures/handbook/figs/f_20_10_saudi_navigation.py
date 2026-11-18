"""Figure 20-10 (new). Navigating in the Kingdom, from the last section of Chapter 20: four scenes, one for each of its points.

1 few features (seen from above: dunes that look alike, a route with a checkpoint ring, a road across the route just beyond it as a catching feature, a pipeline and a town as lasting features), 2 haze and dust (a faint town and a low sun, the small features lost
in the haze), 3 high ground in the south-west (mountains with cloud on the tops and an aeroplane well clear above them, a dashed double arrow for the margin), 4 lost late in the day (a low sun, a question mark above an aeroplane, an aerodrome in sight
while there is daylight to land). Shapes, colours and the numbers of the callouts; no words. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar2010"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
HAZE = [(0.0, "#A8B8D2"), (0.5, "#DCD3BD"), (0.85, "#E8D2A2"), (1.0, "#E9D3A4")]
SUNSET = [(0.0, "#2F4A86"), (0.45, "#8E7FB4"), (0.8, "#F2A65A"), (1.0, "#F6C98A")]
INK, RED, GREEN = "#334155", "#B91C1C", "#15803D"
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}


def frame(i, sky_stops, body):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + (S.sky(uid + "k", x, y, PW, PH, sky_stops) if sky_stops else "") + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def scene1():                                                # from above: a route, a checkpoint, a catching feature, lasting features
    x, y = PX[0], PY[0]
    sand = f'<defs><linearGradient id="{U}g1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EBDCB4"/><stop offset="1" stop-color="#D5BC8B"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="url(#{U}g1)"/>'
    dunes = "".join(f'<path d="M{n(x - 6)} {n(y + 20 + k * 22)} q 40 -16 80 0 t 80 0 t 80 0 t 80 0" fill="none" stroke="{"#F6EBCB" if k % 2 == 0 else "#C9AE7B"}" stroke-width="3" stroke-opacity="0.7"/>' for k in range(8))
    road = f'<path d="M{n(x + 208)} {n(y + 10)} L{n(x + 246)} {n(y + PH - 8)}" stroke="#6B7385" stroke-width="9" stroke-linecap="round"/><path d="M{n(x + 208)} {n(y + 10)} L{n(x + 246)} {n(y + PH - 8)}" stroke="#F1F5F9" stroke-width="1.4" stroke-dasharray="7 6"/>'
    pipe = f'<path d="M{n(x + 4)} {n(y + 178)} L{n(x + 96)} {n(y + 152)}" stroke="#3B4252" stroke-width="3.2" stroke-linecap="round"/><path d="M{n(x + 4)} {n(y + 178)} L{n(x + 96)} {n(y + 152)}" stroke="#FFFFFF" stroke-opacity="0.4" stroke-width="1"/>'
    town = "".join(f'<rect x="{n(x + 38 + dx)}" y="{n(y + 36 + dy)}" width="{n(w)}" height="{n(h)}" rx="1.5" fill="#B7A58A" stroke="#7F6B4C" stroke-width="0.9"/>' for dx, dy, w, h in ((0, 0, 14, 10), (18, 4, 10, 12), (6, 16, 12, 9), (24, 22, 14, 10), (42, 8, 9, 9), (34, 40, 12, 9)))
    route = S.ribbon(f"{U}r1", [(x + 40, y + 160), (x + 120, y + 118), (x + 190, y + 86), (x + 276, y + 46)], 5.0, "#E8782E", "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=8)
    ring = f'<circle cx="{n(x + 160)}" cy="{n(y + 100)}" r="11" fill="none" stroke="{GREEN}" stroke-width="3.4"/><circle cx="{n(x + 160)}" cy="{n(y + 100)}" r="2.6" fill="{GREEN}"/>'
    return frame(0, None, sand + dunes + road + pipe + town + route + ring)


def scene2():                                                # haze and dust: a faint big feature, a low sun, the small ones lost
    x, y = PX[1], PY[1]
    plain = S.plain(f"{U}l2", x, x + PW, y + 98, y + PH, seed=9, tone="dusk")
    town = "".join(f'<rect x="{n(x + 40 + dx)}" y="{n(y + 82 + dy)}" width="{n(w)}" height="{n(h)}" fill="#8F8470"/>' for dx, dy, w, h in ((0, 0, 20, 16), (24, -6, 14, 22), (42, 4, 18, 12), (66, 0, 12, 14)))
    haze = S.fog(f"{U}h2", x, x + PW, y + 150, 100, seed=5, opacity=0.95, colour="#E0C890", wisp=1.0, foot=0.4)
    sun = S.glow(f"{U}s2", x + 258, y + 88, 70, "#FFF4D2", 0.95) + S.glow(f"{U}s2b", x + 258, y + 88, 30, "#FFFFFF", 0.95) + f'<circle cx="{n(x + 258)}" cy="{n(y + 88)}" r="9" fill="#FFFFFF"/>'
    return frame(1, HAZE, plain + town + haze + sun)


def scene3():                                                # high ground: mountains with cloud, an aeroplane well clear above
    x, y = PX[2], PY[2]
    far = S.land_layer(f"{U}m3a", S.ridge(3, x - 6, x + PW + 6, y + 120, 56.0, step=4.0, peaks=0.7), y + PH, (("#8794B4"), "#B3BFD6") if False else ("#8E97B4", "#B3BFD6"), rim=False)
    near = S.land_layer(f"{U}m3b", S.ridge(7, x - 6, x + PW + 6, y + 150, 66.0, step=4.0, peaks=0.8), y + PH, ("#8C7A62", "#5E503F"), rim=False)
    level = S.altitude_line(x + 150, x + 290, y + 72, colour="#FFFFFF", opacity=0.9, dash="6 5", width=2) + f'<path d="M{n(x + 262)} {n(y + 36)} V{n(y + 72)} M{n(x + 255)} {n(y + 44)} L{n(x + 262)} {n(y + 35)} L{n(x + 269)} {n(y + 44)} M{n(x + 255)} {n(y + 64)} L{n(x + 262)} {n(y + 73)} L{n(x + 269)} {n(y + 64)}" fill="none" stroke="{GREEN}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
    return frame(2, DAY, far + near + level)


def scene4():                                                # lost late in the day: a low sun, a question mark, an aerodrome in sight
    x, y = PX[3], PY[3]
    plain = S.plain(f"{U}l4", x, x + PW, y + 112, y + PH, seed=3, tone="dusk")
    sun = S.glow(f"{U}s4", x + 252, y + 112, 80, "#FFB347", 0.95) + f'<circle cx="{n(x + 252)}" cy="{n(y + 112)}" r="12" fill="#F28C28"/>'
    strip = f'<rect x="{n(x + 28)}" y="{n(y + 150)}" width="90" height="10" rx="2" fill="#5B6577"/><line x1="{n(x + 34)}" y1="{n(y + 155)}" x2="{n(x + 112)}" y2="{n(y + 155)}" stroke="#F1F5F9" stroke-width="1.3" stroke-dasharray="7 5"/>'
    q = (f'<circle cx="{n(x + 150)}" cy="{n(y + 40)}" r="17" fill="#FFFFFF" stroke="{RED}" stroke-width="3"/><path d="M{n(x + 144)} {n(y + 36)} a6 6 0 1 1 9 5 q-3 2 -3 6" fill="none" stroke="{RED}" stroke-width="3.6" stroke-linecap="round"/><circle cx="{n(x + 150)}" cy="{n(y + 52)}" r="2.2" fill="{RED}"/>')
    return frame(3, SUNSET, plain + sun + strip + q)


def sprites():
    o = lambda name, x, y, wd, **k: {"name": name, "at": [x, y], "width": wd, "outline": OUT, "shadow": SHADOW, **k}
    return [o("sprite-top", PX[0] + 120, PY[0] + 123, 34, angle=67.0), o("sprite-side", PX[1] + 168, PY[1] + 70, 46, opacity=0.9), o("sprite-side", PX[2] + 230, PY[2] + 34, 52),
            o("cloud-cumulus-b", PX[2] + 213, PY[2] + 86, 58), o("cloud-cumulus-b", PX[2] + 40, PY[2] + 124, 56), o("sprite-side", PX[3] + 150, PY[3] + 82, 52)]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene1(), scene2(), scene3(), scene4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-20-10-saudi-navigation",
        "replaces": "fig-20-10-saudi-navigation.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-20-10-saudi-navigation.jpg",
        "caption": "Figure 20-10. Navigating in the Kingdom: few features, haze and dust, high ground in the south-west, lost late in the day",
        "desc": ("Figure 20-10. Navigating in the Kingdom, four scenes: few features, with dunes that look alike, lasting features such as a road, a pipeline and a town, and a catching feature across the route just beyond a checkpoint; "
                 "haze and dust, which hide checkpoints and the horizon, worst towards a low sun; high ground in the south-west, with cloud on the tops, so plan an altitude well clear of the charted elevations; "
                 "and being uncertain of position late in the day, so decide early while there is daylight to land."),
        "legend": [
            "Few features: over sand, gravel plain and dunes there is little to fix on, and dunes look alike and move. Choose features that last: roads, power lines, pipelines, escarpments, towns, the coast. A line feature across the route just beyond a checkpoint is a catching feature: reaching it means you have passed the point.",
            "Haze and dust hide checkpoints and the horizon, worst towards a low sun: plan larger features and expect to see them late.",
            "High ground in the south-west rises to mountains and escarpments, often with cloud on the tops. Plan an altitude well clear of the charted elevations.",
            "Lost late in the day: a student uncertain of position in the afternoon must decide early, while there is daylight to land.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
