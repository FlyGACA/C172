"""Figure 14-10 (new). What to look for in the weather of the Arabian Peninsula, from the last section of Chapter 14: five scenes, one for each point of its list.

Drawn in the style of the weather figures (figs/scene.py: sky, plain, dunes, sea, fog, ribbons, rain, lightning; the cloud and aeroplane sprites laid by reskin.py): 1 heat (a sun over the sand and the
thermals rising as ribbons), 2 dust and haze (a hazy layer hiding the hills and the ground ahead), 3 the summer shamal (wind ribbons and a wall of dust), 4 coastal humidity and fog (the sea, an
onshore ribbon and fog at the shore), 5 convection over high ground (a mountain with a cumulonimbus, rain and lightning). The chapter gives no climate statistics for places or months, and neither does the figure:
shapes, colours and the numbers of the callouts. The drawings are generic."""
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "ar14"
CELLS = ((10.0, 10.0, 200.0, 150.0), (220.0, 10.0, 200.0, 150.0), (430.0, 10.0, 200.0, 150.0), (10.0, 170.0, 305.0, 150.0), (325.0, 170.0, 305.0, 150.0))


def panel(i, sky_stops, body):
    x, y, w, h = CELLS[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, w, h, sky_stops) + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def thermals(x, y):
    return "".join(S.ribbon(f"{U}t{k}", [(x + dx, y), (x + dx + 6, y - 16), (x + dx - 4, y - 32), (x + dx + 6, y - 48), (x + dx - 2, y - 62)], 6.0, "#E8782E", "#F8BE73", opacity=0.88, head=2.2, tail=0.4, per=8)
                   for k, dx in enumerate((34, 82, 130, 172)))


def scene_1():                                               # heat: a high sun, the sand, thermals
    x, y, w, h = CELLS[0]
    return panel(0, [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")],
                 S.glow(f"{U}g0", x + 150, y + 28, 40, "#FFF2C4", 0.9) + f'<circle cx="{n(x + 150)}" cy="{n(y + 28)}" r="9" fill="#FFF7DC"/>'
                 + S.plain(f"{U}l0", x, x + w, y + 70, y + h, seed=4, tone="day", acacias=((x + 22, y + 110, 0.9),)) + thermals(x, y + 134))


def scene_2():                                               # dust and haze: the hills and the ground ahead lost in a tan layer
    x, y, w, h = CELLS[1]
    return panel(1, [(0.0, "#9FB4D4"), (0.5, "#D9D2C0"), (0.8, "#E6CFA0"), (1.0, "#E9D3A4")],
                 S.plain(f"{U}l1", x, x + w, y + 70, y + h, seed=7, tone="dusk", acacias=((x + 40, y + 124, 1.0),), houses=((x + 150, y + 82, 0.7),))
                 + S.fog(f"{U}d1", x, x + w, y + 112, 84, seed=5, opacity=0.95, colour="#E0C890", wisp=1.0, foot=0.4)
                 + S.fog(f"{U}d2", x, x + w, y + 92, 60, seed=12, opacity=0.9, colour="#EAD8A8", wisp=1.1, foot=0.3))


def scene_3():                                               # the shamal: wind and a wall of dust
    x, y, w, h = CELLS[2]
    wind = "".join(S.ribbon(f"{U}w{k}", [(x + 8, y + yy), (x + 60, y + yy - 4), (x + 110, y + yy + 2), (x + 152, y + yy - 2)], 6.4, "#4B6FB5", "#A9C0E6", opacity=0.9, head=2.2, tail=0.4, per=8) for k, yy in enumerate((54, 84, 114)))
    return panel(2, [(0.0, "#6F8CB8"), (0.5, "#B5BFC8"), (0.85, "#DDC89A"), (1.0, "#E6D1A2")],
                 S.plain(f"{U}l2", x, x + w, y + 66, y + h, seed=9, tone="dusk", palms=((x + 30, y + 118, 0.9),))
                 + S.fog(f"{U}d3", x + 40, x + w + 30, y + 130, 104, seed=3, opacity=1.0, colour="#C99F5E", wisp=1.1, foot=0.3, side_fade=0.45)
                 + S.fog(f"{U}d4", x + 60, x + w + 20, y + 120, 60, seed=14, opacity=0.9, colour="#E2C48C", wisp=1.1, foot=0.3, side_fade=0.45) + wind)


def scene_4():                                               # coast: the sea, an onshore ribbon, fog at the shore
    x, y, w, h = CELLS[3]
    hz = y + 62
    land = S.plain(f"{U}l3", x + 170, x + w, hz, y + h, seed=3, tone="day", palms=((x + 236, y + 112, 1.0), (x + 266, y + 120, 0.9)), houses=((x + 214, hz + 10, 0.9), (x + 244, hz + 8, 0.8)))
    sea = S.sea(f"{U}s3", x, x + 176, hz, y + h, seed=2) + S.dhow(x + 60, hz + 34, 1.3)
    shore = f'<path d="M{n(x + 168)} {n(hz)} L{n(x + 188)} {n(hz)} L{n(x + 176)} {n(y + h)} L{n(x + 150)} {n(y + h)} Z" fill="#EAD9AF"/>'
    onshore = S.ribbon(f"{U}o3", [(x + 40, y + 112), (x + 110, y + 102), (x + 180, y + 106), (x + 250, y + 112)], 7.0, "#2F7FD0", "#A8D0F4", opacity=0.9, head=2.2, tail=0.4, per=8)
    return panel(3, [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")],
                 sea + land + shore + S.fog(f"{U}f3", x + 100, x + w, y + 126, 66, seed=6, opacity=0.9, wisp=1.0, foot=0.3, side_fade=0.4) + onshore)


def scene_5():                                               # convection over high ground: a mountain, a cumulonimbus, rain and lightning
    x, y, w, h = CELLS[4]
    return panel(4, [(0.0, "#3E5A8C"), (0.5, "#7C93B8"), (0.9, "#C9D2E0"), (1.0, "#E4DFCF")],
                 S.landscape(f"{U}m4", x, x + w, y + 72, y + h, seed=5, mountains=46.0, hills=14.0, acacias=((x + 40, y + 134, 0.8),))
                 + S.rain(f"{U}r4", x + 138, x + 222, y + 100, y + 136, slant=-8.0, count=34, seed=3, veil=0.07) + S.lightning(f"{U}b4", x + 176, y + 100, y + 132, seed=5))


def sprites():
    x3, y3 = CELLS[3][0], CELLS[3][1]
    x4, y4 = CELLS[4][0], CELLS[4][1]
    x0, y0 = CELLS[0][0], CELLS[0][1]
    x1, y1 = CELLS[1][0], CELLS[1][1]
    return [{"name": "cloud-cumulus-b", "at": [x0 + 58, y0 + 36], "width": 56, "height": 18},
            {"name": "sprite-side", "at": [x1 + 100, y1 + 56], "width": 46, "opacity": 0.55, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.7}},
            {"name": "cloud-cb", "at": [x4 + 190, y4 + 58], "width": 120, "height": 112},
            {"name": "cloud-cumulus-a", "at": [x3 + 70, y3 + 26], "width": 64, "height": 20}]


def callouts():
    return "".join(S.callout(i + 1, CELLS[i][0] + 17, CELLS[i][1] + 17, r=10.5) for i in range(5))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="330" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), scene_5(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-14-10-arabia-weather",
        "replaces": "fig-14-10-arabia-weather.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-14-10-arabia-weather.jpg",
        "caption": "Figure 14-10. What to look for in the weather of the Arabian Peninsula: five things the physics tells you",
        "desc": ("Figure 14-10. What to look for in the weather of the Arabian Peninsula, five tiles: heat and thermals, dust and haze, the summer shamal, coastal humidity and fog, and convection over high ground. "
                 "The chapter gives no climate statistics for particular places or months, and neither does the figure."),
        "legend": [
            "Heat: high density altitude (Chapter 11) and thermals, with bumpy air at low level from late morning. Climbing higher usually brings smoother air.",
            "Dust and haze: strong wind lifts dust and a stable layer keeps it low. Haze can hide the horizon and the ground ahead even when the surface report looks acceptable.",
            "The summer shamal, and the dust storms it often fuels (Figure 14-4).",
            "Coastal humidity and fog: on the Red Sea and Gulf coasts the sea breeze brings moist air inland by day, raising the density altitude further. After clear, calm nights mist and fog are likely around dawn, and sea fog can drift ashore on an onshore wind.",
            "Convection over high ground: where moist air meets high ground, such as the south-western highlands, afternoon cumulus and thunderstorms are likely.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
