"""Figure 22-1 (new). The limits of the eye, from Chapter 22 ("The limits of the eye"): six scenes, one for each row of the section's table, in its order.

Drawn in the style of Figure 22-10 (figs/scene.py: sky, plain, fog; the aeroplane sprites laid by reskin.py): 1 small targets (a trainer head-on at 3 NM, about 0.1 degree across,
beside the full moon, four times as wide, to scale with each other); 2 empty-field myopia (a featureless hazy sky, the eyes focused 10 to 30 ft ahead, and a far aeroplane out of
focus beyond); 3 refocusing (from the panel, an instrument near, to the far aeroplane: several seconds, a clock); 4 structure (a window post with an aeroplane behind it, and the head moved from side to side to look round it); 5 conditions (haze and the sun low ahead, an aeroplane faint in the glare); 6 attention (a tablet on the knee and the eyes inside, the sky unwatched). Digits and
units only; the words are in the legend. The drawings are generic."""
from figs import h_b2 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "le22"
CELLS = tuple((10.0 + 210.0 * (k % 3), 10.0 + 160.0 * (k // 3), 200.0, 150.0) for k in range(6))
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
HAZE = [(0.0, "#B9C7D8"), (0.6, "#D5DCE4"), (1.0, "#E6E2D6")]
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
INK, BLUE, AMBER, RED = "#1E293B", "#1D4ED8", "#B45309", "#B91C1C"


def panel(i, sky_stops, body):
    x, y, w, h = CELLS[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, w, h, sky_stops) + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def plane(name, x, y, width, opacity=None, flip=False, blur=None):
    o = {"name": name, "at": [x, y], "width": width, "outline": OUT, "shadow": SHADOW}
    if opacity is not None:
        o["opacity"] = opacity
    if flip:
        o["flip"] = True
    return o


def eye(cx, cy, s=1.0, look=0.0):
    """An eye seen from the side-front: lids, iris and pupil; `look` shifts the iris (-1 to 1)."""
    return (f'<path d="M{n(cx - 13 * s)} {n(cy)} Q{n(cx)} {n(cy - 11 * s)} {n(cx + 13 * s)} {n(cy)} Q{n(cx)} {n(cy + 11 * s)} {n(cx - 13 * s)} {n(cy)} Z" fill="#FFFFFF" stroke="{INK}" stroke-width="{n(1.8 * s)}"/>'
            f'<circle cx="{n(cx + look * 4 * s)}" cy="{n(cy)}" r="{n(5 * s)}" fill="#2563EB"/><circle cx="{n(cx + look * 4 * s)}" cy="{n(cy)}" r="{n(2.2 * s)}" fill="#0B1224"/>')


def scene_1():                                               # small targets: head-on at 3 NM, beside the full moon
    x, y, w, h = CELLS[0]
    mx, my, r = x + 132, y + 62, 22.0
    moon = (S.glow(f"{U}mg", mx, my, 40, "#FFFFFF", 0.35) + f'<circle cx="{n(mx)}" cy="{n(my)}" r="{n(r)}" fill="#F3F6FA" opacity="0.92"/>'
            f'<circle cx="{n(mx - 6)}" cy="{n(my - 5)}" r="5" fill="#D5DCE6" opacity="0.7"/><circle cx="{n(mx + 7)}" cy="{n(my + 6)}" r="3.4" fill="#D5DCE6" opacity="0.7"/>')
    # the trainer head-on: a wing 11 units wide (a quarter of the moon's 44), a dot of a fuselage, the wheels
    tx, ty = x + 62, y + 62
    target = (f'<line x1="{n(tx - 5.5)}" y1="{n(ty)}" x2="{n(tx + 5.5)}" y2="{n(ty)}" stroke="#0F172A" stroke-width="1.1" stroke-linecap="round"/><circle cx="{n(tx)}" cy="{n(ty + 0.6)}" r="1.3" fill="#0F172A"/>')
    dims = (f'<path d="M{n(tx - 5.5)} {n(ty + 12)} v6 M{n(tx + 5.5)} {n(ty + 12)} v6 M{n(tx - 5.5)} {n(ty + 15)} h11" stroke="{INK}" stroke-width="1"/>'
            f'<path d="M{n(mx - r)} {n(my + r + 6)} v6 M{n(mx + r)} {n(my + r + 6)} v6 M{n(mx - r)} {n(my + r + 9)} h{n(2 * r)}" stroke="{INK}" stroke-width="1"/>')
    return panel(0, DAY, S.plain(f"{U}l0", x, x + w, y + 116, y + h, seed=4, tone="day", photo=True) + moon + target + dims)


def scene_2():                                               # empty-field myopia: the eyes focus 10 to 30 ft ahead
    x, y, w, h = CELLS[1]
    ex, ey, fx = x + 26, y + 70, x + 96
    cone = (f'<polygon points="{n(ex + 12)},{n(ey - 6)} {n(fx)},{n(ey)} {n(ex + 12)},{n(ey + 6)}" fill="{BLUE}" opacity="0.28"/>'
            f'<line x1="{n(ex + 12)}" y1="{n(ey - 6)}" x2="{n(fx)}" y2="{n(ey)}" stroke="{BLUE}" stroke-width="1.3"/><line x1="{n(ex + 12)}" y1="{n(ey + 6)}" x2="{n(fx)}" y2="{n(ey)}" stroke="{BLUE}" stroke-width="1.3"/>'
            f'<circle cx="{n(fx)}" cy="{n(ey)}" r="3.4" fill="#FFFFFF" stroke="{BLUE}" stroke-width="1.8"/>'
            f'<line x1="{n(fx + 6)}" y1="{n(ey)}" x2="{n(x + 150)}" y2="{n(ey)}" stroke="{BLUE}" stroke-width="1.2" stroke-dasharray="2 4" opacity="0.7"/>')
    return panel(1, HAZE, S.fog(f"{U}h1", x, x + w, y + h, 120, seed=8, opacity=0.9, colour="#E7E3D8", wisp=0.9, foot=1.0) + cone + eye(ex, ey, 1.0, 0.6))


def scene_3():                                               # refocusing: from the panel to the far aeroplane takes several seconds
    x, y, w, h = CELLS[2]
    px, py = x + 44, y + 104
    gauge = (f'<circle cx="{n(px)}" cy="{n(py)}" r="24" fill="#111827" stroke="#4B5563" stroke-width="3"/>'
             + "".join(f'<line x1="{n(px + 17 * c)}" y1="{n(py + 17 * s_)}" x2="{n(px + 21 * c)}" y2="{n(py + 21 * s_)}" stroke="#E5E7EB" stroke-width="1.4"/>'
                       for c, s_ in ((1, 0), (0.71, 0.71), (0, 1), (-0.71, 0.71), (-1, 0), (-0.71, -0.71), (0, -1), (0.71, -0.71)))
             + f'<line x1="{n(px)}" y1="{n(py)}" x2="{n(px + 12)}" y2="{n(py - 12)}" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/><circle cx="{n(px)}" cy="{n(py)}" r="2.6" fill="#FFFFFF"/>')
    ex, ey = x + 100, y + 60
    sight = (f'<line x1="{n(ex - 10)}" y1="{n(ey + 8)}" x2="{n(px + 18)}" y2="{n(py - 16)}" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="3 3"/>'
             f'<line x1="{n(ex + 14)}" y1="{n(ey - 2)}" x2="{n(x + 160)}" y2="{n(y + 36)}" stroke="{BLUE}" stroke-width="1.6" stroke-dasharray="3 3"/>'
             + M.flight((px + 30, py - 30), (x + 120, y + 100), (x + 150, y + 52), AMBER, width=1.8))
    return panel(2, DAY, S.plain(f"{U}l2", x, x + w, y + 120, y + h, seed=6, tone="day", photo=True) + sight + gauge + eye(ex, ey, 1.0, 0.0))


def scene_4():                                               # structure: a window post hides an aeroplane; moving the head uncovers it
    x, y, w, h = CELLS[3]
    post = (f'<defs>{S.gradient(U + "po", [(0, "#596378"), (0.5, "#2B3242"), (1, "#151A24")], 0, 0, 1, 0)}</defs>'
            f'<polygon points="{n(x + 104)},{n(y)} {n(x + 122)},{n(y)} {n(x + 112)},{n(y + h)} {n(x + 90)},{n(y + h)}" fill="url(#{U}po)"/>')
    sight = M.arrow(x + 62, y + 136, x + 86, y + 136, "#047857", width=2.2) + M.arrow(x + 58, y + 136, x + 34, y + 136, "#047857", width=2.2)
    return panel(3, DAY, S.plain(f"{U}l3", x, x + w, y + 104, y + h, seed=5, tone="day", photo=True) + post + sight + eye(x + 60, y + 118, 1.0, 0.7))


def scene_5():                                               # conditions: haze and a low sun ahead, an aeroplane faint in the glare
    x, y, w, h = CELLS[4]
    sun = S.glow(f"{U}g4", x + 128, y + 64, 84, "#FFF4D2", 0.98) + S.glow(f"{U}g4b", x + 128, y + 64, 38, "#FFFFFF", 0.95) + f'<circle cx="{n(x + 128)}" cy="{n(y + 64)}" r="10" fill="#FFFFFF"/>'
    return panel(4, [(0.0, "#6F97CC"), (0.5, "#B7CDE6"), (0.85, "#F2E4BE"), (1.0, "#EFDDB0")],
                 S.plain(f"{U}l4", x, x + w, y + 96, y + h, seed=3, tone="day", photo=True) + sun
                 + S.fog(f"{U}h4", x, x + w, y + 118, 70, seed=5, opacity=0.8, colour="#E6D2A0", wisp=1.0, foot=0.4))


def scene_6():                                               # attention: the eyes inside, on a tablet; the sky unwatched
    x, y, w, h = CELLS[5]
    tx, ty = x + 34, y + 84
    tablet = (f'<rect x="{n(tx + 2)}" y="{n(ty + 3)}" width="62" height="44" rx="5" fill="#0B1224" opacity="0.3"/>'
              f'<rect x="{n(tx)}" y="{n(ty)}" width="62" height="44" rx="5" fill="#1F2937" stroke="#4B5563" stroke-width="1.2"/><rect x="{n(tx + 4)}" y="{n(ty + 4)}" width="54" height="36" rx="2" fill="#DBEAFE"/>'
              f'<path d="M{n(tx + 8)} {n(ty + 32)} L{n(tx + 24)} {n(ty + 18)} L{n(tx + 36)} {n(ty + 26)} L{n(tx + 54)} {n(ty + 10)}" fill="none" stroke="#D946EF" stroke-width="2"/>'
              f'<circle cx="{n(tx + 24)}" cy="{n(ty + 18)}" r="2" fill="{BLUE}"/><circle cx="{n(tx + 36)}" cy="{n(ty + 26)}" r="2" fill="{BLUE}"/>')
    ex, ey = x + 112, y + 58
    sight = f'<line x1="{n(ex - 12)}" y1="{n(ey + 8)}" x2="{n(tx + 50)}" y2="{n(ty + 6)}" stroke="{AMBER}" stroke-width="1.8" stroke-dasharray="3 3"/>'
    return panel(5, DAY, S.plain(f"{U}l5", x, x + w, y + 122, y + h, seed=9, tone="day", photo=True) + sight + tablet + eye(ex, ey, 1.0, -0.8))


def sprites():
    c = CELLS
    return [plane("sprite-front", c[1][0] + 166, c[1][1] + 70, 26, opacity=0.28),
            plane("sprite-side", c[2][0] + 166, c[2][1] + 34, 34, flip=True),
            plane("sprite-side", c[3][0] + 110, c[3][1] + 56, 40, flip=True),
            plane("sprite-front", c[4][0] + 150, c[4][1] + 62, 30, opacity=0.4),
            plane("sprite-side", c[5][0] + 160, c[5][1] + 36, 36, flip=True)]


def post_again():
    """The window post of scene 4 drawn again over the aeroplane it hides."""
    x, y, w, h = CELLS[3]
    return (f'<defs><clipPath id="{U}pc"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath></defs>'
            f'<g clip-path="url(#{U}pc)"><polygon points="{n(x + 104)},{n(y)} {n(x + 122)},{n(y)} {n(x + 112)},{n(y + h)} {n(x + 90)},{n(y + h)}" fill="url(#{U}po)" opacity="0.8"/></g>')


def labels():
    c = CELLS
    out = [M.chip(c[0][0] + 62, c[0][1] + 92, "0.1°", INK, size=8.4), M.chip(c[0][0] + 62, c[0][1] + 34, "3 NM", INK, size=8.4),
           M.chip(c[1][0] + 78, c[1][1] + 96, "10–30 FT", BLUE, size=8.4),
           M.chip(c[2][0] + 134, c[2][1] + 110, "SEC", AMBER, size=8.4, kind="clock")]
    cal = S.callout
    out.append("".join(cal(k + 1, c[k][0] + 16, c[k][1] + 16, r=10) for k in range(6)))
    return "".join(out)


def layers():
    return ([H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), scene_5(), scene_6()]
            + sprites() + [post_again(), labels()])


def plate():
    return {
        "id": "fig-22-01-limits-of-eye",
        "replaces": "fig-22-01-limits-of-eye.svg",              # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-22-01-limits-of-eye.jpg",
        "caption": "Figure 22-1. Six limits of the eye in the search for traffic",
        "desc": ("Figure 22-1. Six scenes: a trainer head-on at 3 NM, a quarter of the width of the full moon; eyes focused 10 to 30 ft ahead in a featureless sky; the seconds "
                 "needed to refocus from the panel to the distance; a window post hiding an aeroplane; haze and a low sun hiding traffic; and the eyes on a tablet inside."),
        "legend": [
            "Small targets: a trainer head-on at 3 NM is about 0.1° across, a quarter of the width of the full moon.",
            "Empty-field myopia: with nothing to focus on, the eyes relax to a focus 10 to 30 ft away.",
            "Refocusing: from the panel to distant objects may take several seconds.",
            "Structure: a window post hides part of the sky; move your head.",
            "Conditions: haze, low visibility and the sun's position hide traffic.",
            "Attention: a tablet, passengers, fatigue or preoccupation take the eyes inside.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
