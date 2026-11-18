"""Figure 2-3 (new). Minimum safe altitudes, GACAR 91.67. Each half is drawn to one scale in both directions: the town on the left at 0.07 canvas units to the foot (1 000 ft = 70 units,
2 000 ft = 140 units), the open country on the right at 0.08 (500 ft = 40 units). The two scales differ so that each half fills its side; the heights are in the labels.

Left, a congested area: a town of low buildings and one tower, 300 ft tall; the aeroplane is 1 000 ft above the highest obstacle within 2 000 ft horizontally of it (a bracket 2 000 ft to each
side of the aeroplane at its level, the tower inside it). Right, open country: the aeroplane 500 ft above the surface; a car and a person, each with a ring of 500 ft, which the aeroplane
does not enter; a dashed glide line from the aeroplane to the clear ground ahead, for the rule that applies everywhere (the height to land without undue hazard if the engine fails).
Not measured, not a map: the heights of the buildings and the distances are chosen to show the rule. Digits and the unit only (FT)."""
from figs import h_a1 as A1
from figs import h_b1 as B
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 262
U = "ma2"
KL, KR = 0.07, 0.08                                       # canvas units to the foot: the town, the open country
GY = 214.0                                                # the ground line
LEFT_PLANE = (168.0, GY - KL * (300 + 1000))              # 1 000 ft above the top of the 300 ft tower
RIGHT_PLANE = (398.0, GY - KR * 500)
TOWER_X = 112.0
MAN_X, CAR_X = 508.0, 592.0
SLATE, BLUE, AMBER, GREEN, RED = "#475569", "#1D4ED8", "#B45309", "#15803D", "#B91C1C"
# the buildings of the town: (x, width, height in ft); the tower is the highest and lies within 2 000 ft (120 units) of the aeroplane
TOWN = [(28, 24, 120), (56, 22, 180), (84, 20, 100), (132, 22, 150), (206, 24, 200), (234, 26, 120), (264, 22, 160)]
TOWER_FT = 300
assert max(h for _, _, h in TOWN) < TOWER_FT
assert abs(TOWER_X - LEFT_PLANE[0]) <= 2000 * KL                  # the tower is within 2 000 ft horizontally of the aeroplane


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=5.6, height=10.5):
    w = gwidth(s, size) + 10.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.1" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.3))


def background():
    return (f'<defs><filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            + A1.page(U + "pg", W, HT) + S.card(U + "cd", 8, 8, W - 16, GY - 8 + 22, B.SKY, S.glow(U + "sg", 120, 60, 220, "#FFFFFF", 0.4), radius=11))


def ground():
    pts_ = [(8.0, GY), (W - 8.0, GY)]
    return B.soil(U + "so", pts_, GY + 30.0, seed=202, strata=(0.35, 0.65, 0.88), grit=16, haze=(5.0, 0.7))


def building(x, w, ft, i):
    h = ft * KL
    col = ("#E8DFC9", "#DDD2B8", "#EFE6D2")[i % 3]
    out = [f'<rect x="{n(x)}" y="{n(GY - h)}" width="{n(w)}" height="{n(h)}" fill="{col}" stroke="#8B7B5B" stroke-width="0.8"/>']
    rows = int(h // 5)
    for r in range(1, rows):
        for c in range(int(w // 7)):
            out.append(f'<rect x="{n(x + 3 + c * 7)}" y="{n(GY - h + 2 + r * 5 - 3)}" width="3" height="2.2" fill="#7C8798" opacity="0.7"/>')
    return "".join(out)


def town():
    out = [building(x, w, ft, i) for i, (x, w, ft) in enumerate(TOWN)]
    h = TOWER_FT * KL
    out.append(f'<rect x="{n(TOWER_X - 4)}" y="{n(GY - h + 6)}" width="8" height="{n(h - 6)}" fill="#D8D0BC" stroke="#8B7B5B" stroke-width="0.8"/>'
               f'<rect x="{n(TOWER_X - 8)}" y="{n(GY - h)}" width="16" height="9" rx="1.5" fill="#9CB7D4" stroke="#475569" stroke-width="0.9"/>'
               f'<line x1="{n(TOWER_X)}" y1="{n(GY - h)}" x2="{n(TOWER_X)}" y2="{n(GY - h - 7)}" stroke="#475569" stroke-width="1"/>')
    return "".join(out)


def car(x):
    return (f'<rect x="{n(x - 8)}" y="{n(GY - 6)}" width="16" height="4.4" rx="1.4" fill="{RED}"/><rect x="{n(x - 4.6)}" y="{n(GY - 9)}" width="9" height="3.6" rx="1.2" fill="#B02A2A"/>'
            f'<circle cx="{n(x - 4.6)}" cy="{n(GY - 1.6)}" r="1.8" fill="#1F2937"/><circle cx="{n(x + 4.6)}" cy="{n(GY - 1.6)}" r="1.8" fill="#1F2937"/>')


def person(x):
    return (f'<circle cx="{n(x)}" cy="{n(GY - 9.6)}" r="1.9" fill="#1F2937"/><line x1="{n(x)}" y1="{n(GY - 7.6)}" x2="{n(x)}" y2="{n(GY - 3.2)}" stroke="#1F2937" stroke-width="1.5"/>'
            f'<line x1="{n(x)}" y1="{n(GY - 3.2)}" x2="{n(x - 1.8)}" y2="{n(GY)}" stroke="#1F2937" stroke-width="1.2"/><line x1="{n(x)}" y1="{n(GY - 3.2)}" x2="{n(x + 1.8)}" y2="{n(GY)}" stroke="#1F2937" stroke-width="1.2"/>'
            f'<line x1="{n(x - 3.2)}" y1="{n(GY - 6)}" x2="{n(x + 3.2)}" y2="{n(GY - 6)}" stroke="#1F2937" stroke-width="1.2"/>')


def rings():
    out = []
    for x in (CAR_X, MAN_X):
        r = 500 * KR
        out.append(f'<path d="M{n(x - r)} {n(GY)} A{n(r)} {n(r)} 0 0 1 {n(x + r)} {n(GY)} Z" fill="{RED}" fill-opacity="0.08" stroke="{RED}" stroke-width="1.3" stroke-dasharray="4 3"/>')
    return "".join(out)


def dimension_v(x, y_top, y_bot, label, colour):
    """A vertical dimension line with arrowheads and a pill in the middle."""
    return (f'<line x1="{n(x)}" y1="{n(y_top)}" x2="{n(x)}" y2="{n(y_bot)}" stroke="{colour}" stroke-width="1.6"/>'
            f'<path d="M{n(x - 3.4)} {n(y_top + 6)} L{n(x)} {n(y_top)} L{n(x + 3.4)} {n(y_top + 6)}" fill="none" stroke="{colour}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="M{n(x - 3.4)} {n(y_bot - 6)} L{n(x)} {n(y_bot)} L{n(x + 3.4)} {n(y_bot - 6)}" fill="none" stroke="{colour}" stroke-width="1.6" stroke-linejoin="round"/>'
            + pill(label, x, (y_top + y_bot) / 2, colour))


def left_dimensions():
    px, py = LEFT_PLANE
    top_tower = GY - KL * TOWER_FT
    out = []
    # the bracket: 2 000 ft each side of the aeroplane, at its level
    xl, xr = px - 2000 * KL, px + 2000 * KL
    out.append(f'<line x1="{n(xl)}" y1="{n(py + 16)}" x2="{n(xr)}" y2="{n(py + 16)}" stroke="{AMBER}" stroke-width="1.5"/>'
               f'<line x1="{n(xl)}" y1="{n(py + 11)}" x2="{n(xl)}" y2="{n(py + 21)}" stroke="{AMBER}" stroke-width="1.5"/><line x1="{n(xr)}" y1="{n(py + 11)}" x2="{n(xr)}" y2="{n(py + 21)}" stroke="{AMBER}" stroke-width="1.5"/>'
               f'<line x1="{n(px)}" y1="{n(py + 11)}" x2="{n(px)}" y2="{n(py + 21)}" stroke="{AMBER}" stroke-width="1.5"/>')
    out.append(pill("2 000 FT", xl + 34, py + 16, AMBER))
    out.append(pill("2 000 FT", xr - 34, py + 16, AMBER))
    # the vertical 1 000 ft: from the top of the highest obstacle to the aeroplane's level
    out.append(dimension_v(TOWER_X, py + 16, top_tower - 8, "1 000 FT", BLUE))
    out.append(f'<line x1="{n(TOWER_X - 14)}" y1="{n(top_tower - 8)}" x2="{n(TOWER_X + 14)}" y2="{n(top_tower - 8)}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="2 2"/>')
    return "".join(out)


def right_dimensions():
    px, py = RIGHT_PLANE
    return (dimension_v(px - 46, py + 14, GY, "500 FT", GREEN)
            + f'<line x1="{n(px - 52)}" y1="{n(py + 14)}" x2="{n(px + 18)}" y2="{n(py + 14)}" stroke="{GREEN}" stroke-width="1" stroke-dasharray="2 2"/>'
            + pill("500 FT", (CAR_X + MAN_X) / 2, GY - 500 * KR - 10, RED))


def glide():
    px, py = RIGHT_PLANE
    return (f'<path d="M{n(px + 20)} {n(py + 8)} L{n(px + 50)} {n(GY - 5)}" stroke="{SLATE}" stroke-width="1.3" stroke-dasharray="5 3" fill="none"/>'
            f'<path d="M{n(px + 44)} {n(GY - 11)} L{n(px + 50)} {n(GY - 5)} L{n(px + 41)} {n(GY - 5.4)}" fill="none" stroke="{SLATE}" stroke-width="1.3" stroke-linejoin="round"/>')


def aeroplanes():
    look = {"outline": {"width": 0.6, "colour": "#1B2638", "opacity": 0.95}, "shadow": {"dx": 0.8, "dy": 1.8, "blur": 1.3, "opacity": 0.28}}
    return [{"name": "sprite-side", "at": [LEFT_PLANE[0], LEFT_PLANE[1] - 3.0], "width": 40, **look},
            {"name": "sprite-side", "at": [RIGHT_PLANE[0], RIGHT_PLANE[1] - 3.0], "width": 40, **look}]


def callouts():
    c = S.callout
    r = 9.5
    px, py = LEFT_PLANE
    qx, qy = RIGHT_PLANE
    top_tower = GY - KL * TOWER_FT
    ring = 500 * KR
    return "".join([
        c(1, px + 56, py - 24, px + 30, py + 16, r=r),
        c(2, TOWER_X + 36, top_tower - 24, TOWER_X + 5, top_tower + 3, r=r),
        c(3, qx - 78, qy - 12, qx - 46, (qy + 14 + GY) / 2 - 8, r=r),
        c(4, CAR_X + ring * 0.2, GY - ring - 26, CAR_X + ring * 0.5, GY - ring * 0.87, r=r),
        c(5, qx + 62, qy - 22, qx + 40, qy + 12, r=r),
    ])


def layers():
    return [background(), ground(), town(), car(CAR_X), person(MAN_X), rings(), left_dimensions(), right_dimensions(), glide(), *aeroplanes(), callouts(), divider()]


def divider():
    x = 322.0
    return (f'<line x1="{n(x)}" y1="30" x2="{n(x)}" y2="{n(GY)}" stroke="{SLATE}" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="3 5"/>')


def plate():
    return {
        "id": "fig-02-03-minimum-altitudes",
        "replaces": "fig-02-03-minimum-altitudes.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-02-03-minimum-altitudes.jpg",
        "caption": "Figure 2-3. Minimum safe altitudes: over a congested area and elsewhere, to one scale",
        "desc": ("Figure 2-3. Minimum safe altitudes: over a congested area and elsewhere, to one scale. Left, an aeroplane 1 000 ft above the highest obstacle within 2 000 ft of it over a town; "
                 "right, an aeroplane 500 ft above the surface in open country, outside a ring of 500 ft round a car and a person, with a glide line to clear ground. Heights and distances chosen to show the rule (GACAR 91.67); not a map."),
        "legend": [
            "Over a congested area of a city, town or settlement, or over an open-air assembly of people: at least 1 000 ft above the highest obstacle within 2 000 ft horizontally of the aeroplane.",
            "The highest obstacle within that distance, here a tower of 300 ft: the 1 000 ft is counted from its top, not from the roofs round it.",
            "Elsewhere: at least 500 ft above the surface.",
            "Over open water or sparsely populated areas you may fly lower than that, but never closer than 500 ft to any person, vessel, vehicle or structure: the ring round the car and the person.",
            "Anywhere: high enough that, if the engine fails, you can make an emergency landing without undue hazard to people or property on the surface. Over desert this rule usually decides your height, not the 500 ft.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
