"""Figure 23-6. Vestibular illusions: the leans, the graveyard spiral and the somatogravic illusion. Three illustrated scenes on the old figure's canvas. Above: the leans, three
pictures of the aeroplane from behind on a wide desert sky (the aeroplane of the model, banked or level, with the pilot's head; the attitude felt drawn over it in blue dashes, the true
vertical in white dashes; a roll arrow; the pilot leaning in a glass cutaway of the cabin). Below left: the graveyard spiral, the old figure's track as a dark glossy tube (the far side of
each loop thinner and paler), the three red beads on it, the sand of the ground. Below right: the somatogravic illusion, the aeroplane nose-up in the sky over a plain, with the two
forces, what is felt as down, the angle theta and the red arrow that pushing the nose down would follow. The fifteen numbered callouts of the old figure are kept."""
import math

from figs import scene as S
from figs import h_a3 as H
from reskin import LOOK

n = S.n
U = "f2306"
INK = ("#1F2937", "#667489")
BLUE = ("#2F63C8", "#8DB3F2")
RED = ("#B3261E", "#F08A7A")
GREY = ("#6B7686", "#BAC4D3")
SKY = [(0.0, "#6F9FD4"), (0.62, "#B9D3EE"), (1.0, "#F2F5F7")]
FELT = "#1D4ED8"

SPRITE_W, WING_PX, CENTRE_PX = 1406.0, 68.0, 151.5            # sprite-rear: its width in px, the wing line and the middle of the picture (px from its top)


def rot(pt, deg, pivot):
    a = math.radians(deg)
    dx, dy = pt[0] - pivot[0], pt[1] - pivot[1]
    return (pivot[0] + dx * math.cos(a) - dy * math.sin(a), pivot[1] + dx * math.sin(a) + dy * math.cos(a))


STRETCH = 1.22                      # the aeroplane from behind is a thin picture; a little taller than true reads better at this size


def rear_sprite(w0, width, bank):
    """The aeroplane from behind: `w0` is the middle of its wing line, `width` its span, `bank` degrees clockwise (right wing down)."""
    k = width / SPRITE_W
    d = (CENTRE_PX - WING_PX) * k * STRETCH
    a = math.radians(bank)
    return {"name": "sprite-rear", "at": [round(w0[0] - d * math.sin(a), 2), round(w0[1] + d * math.cos(a), 2)], "width": width, "height": round(width * 303.0 / SPRITE_W * STRETCH, 2), "angle": bank, **LOOK}


def felt_outline(w0, width, angle):
    """The aeroplane's wing, fin and tailplane and the cabin, as blue dashed lines, turned by `angle` about the wing's middle: the attitude the pilot feels."""
    k = width / SPRITE_W * STRETCH
    lines = [[(-width / 2 + 2, 0), (width / 2 - 4, 0)], [(0, -9.0), (0, 18.0)], [(-26.0, 16.5), (26.0, 16.5)]]
    out = []
    for ln in lines:
        (xa, ya), (xb, yb) = [rot((w0[0] + x, w0[1] + y), angle, w0) for x, y in ln]
        out.append(f'<line x1="{n(xa)}" y1="{n(ya)}" x2="{n(xb)}" y2="{n(yb)}" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.85" stroke-linecap="round"/>'
                   f'<line x1="{n(xa)}" y1="{n(ya)}" x2="{n(xb)}" y2="{n(yb)}" stroke="{FELT}" stroke-width="1.9" stroke-dasharray="5.5 3.6" stroke-linecap="round"/>')
    hx, hy = rot((w0[0], w0[1] + 8.0), angle, w0)
    out.append(f'<circle cx="{n(hx)}" cy="{n(hy)}" r="8.6" fill="none" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.85"/><circle cx="{n(hx)}" cy="{n(hy)}" r="8.6" fill="none" stroke="{FELT}" stroke-width="1.9" stroke-dasharray="5.5 3.6"/>')
    return "".join(out)


def head(uid, x, y, r=7.4):
    """The pilot's head from behind: dark hair, a headset band and ear cups, lit from the upper left."""
    return (f'<defs><radialGradient id="{uid}" cx="0.36" cy="0.3" r="0.8"><stop offset="0" stop-color="#8A6A52"/><stop offset="0.5" stop-color="#4B3426"/><stop offset="1" stop-color="#1D130C"/></radialGradient></defs>'
            f'<ellipse cx="{n(x + 0.8)}" cy="{n(y + r * 0.55)}" rx="{n(r * 0.95)}" ry="{n(r * 0.9)}" fill="#14233F" fill-opacity="0.25"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#{uid})"/>'
            f'<path d="M {n(x - r * 0.98)},{n(y + r * 0.1)} Q {n(x)},{n(y - r * 1.5)} {n(x + r * 0.98)},{n(y + r * 0.1)}" fill="none" stroke="#2B3648" stroke-width="{n(r * 0.26)}" stroke-linecap="round"/>'
            f'<ellipse cx="{n(x - r * 0.98)}" cy="{n(y + r * 0.2)}" rx="{n(r * 0.26)}" ry="{n(r * 0.42)}" fill="#3A465C"/><ellipse cx="{n(x + r * 0.98)}" cy="{n(y + r * 0.2)}" rx="{n(r * 0.26)}" ry="{n(r * 0.42)}" fill="#3A465C"/>'
            f'<ellipse cx="{n(x - r * 0.38)}" cy="{n(y - r * 0.52)}" rx="{n(r * 0.3)}" ry="{n(r * 0.17)}" fill="#FFFFFF" fill-opacity="0.45" transform="rotate(-25 {n(x - r * 0.38)} {n(y - r * 0.52)})"/>')


def dashed_line(x0, y0, x1, y1, colour, width=1.6, dash="5 4", halo=True):
    return ((f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#FFFFFF" stroke-width="{n(width + 2.6)}" stroke-opacity="0.8" stroke-linecap="round"/>' if halo else "")
            + f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{colour}" stroke-width="{n(width)}" stroke-dasharray="{dash}" stroke-linecap="round"/>')


# ---------------------------------------------------------------------------------------------------------------- the leans
def top_card():
    x, y, w, h = 8, 8, 624, 190
    hz = 168
    body = (S.plain(U + "t", x, x + w, hz, y + h, seed=4, hills=16, palms=[(36, 184, 0.6), (612, 186, 0.55)], houses=[(588, 176, 0.5)], acacias=[(300, 184, 0.45)])
            + S.land_layer(U + "tl", S.ridge(9, x, x + w, hz + 1, 7, peaks=0.3), hz + 3, ("#8E9DC2", "#C3CDE2"), rim=False, haze=0.2))
    return S.card(U + "T", x, y, w, h, SKY, body)


def leans():
    """The true vertical of the first two pictures, white dashes (the third has its own in front of the cabin)."""
    return "".join(dashed_line(cx, 168, cx, 40, "#FFFFFF", 1.3, "3 4", halo=False) for cx in (120, 320))


def planes():
    out = []
    spec = [(120, 116, 184, 20.0, 0.0), (320, 116, 184, 0.0, -18.0)]
    for cx, cy, width, bank, felt in spec:
        out.append(("sprite", rear_sprite((cx, cy), width, bank)))
        out.append(("svg", felt_outline((cx, cy), width, felt)))
    return out


def cabin():
    """Panel 3: the aeroplane level (its wings either side of a glass cutaway of the cabin) and the pilot leaning towards the bank he rolled out of."""
    cx, cy = 520, 116
    out = [("sprite", rear_sprite((cx, cy), 184, 0.0))]
    glass = (f'<defs><linearGradient id="{U}gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.92"/><stop offset="1" stop-color="#CFE0F4" stop-opacity="0.82"/></linearGradient>'
             f'<linearGradient id="{U}shirt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4A6FB0"/><stop offset="0.55" stop-color="#2D4B86"/><stop offset="1" stop-color="#1B2F5C"/></linearGradient>'
             f'<linearGradient id="{U}seat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6A7488"/><stop offset="1" stop-color="#394357"/></linearGradient>'
             f'<clipPath id="{U}cc"><rect x="480" y="66" width="80" height="80" rx="20"/></clipPath></defs>'
             f'<rect x="480" y="66" width="80" height="80" rx="20" fill="#14233F" fill-opacity="0.25" transform="translate(1.5 3)" filter="url(#{U}b2)"/>'
             f'<rect x="480" y="66" width="80" height="80" rx="20" fill="url(#{U}gl)" stroke="#2B3648" stroke-width="3"/>'
             f'<g clip-path="url(#{U}cc)"><rect x="500" y="108" width="40" height="40" rx="6" fill="url(#{U}seat)"/>'
             f'<polygon points="496,146 544,146 534.7,111 517.8,104.7 505,110" fill="url(#{U}shirt)" stroke="#142245" stroke-width="0.9" stroke-linejoin="round"/>'
             f'<path d="M 512,112 L 534,112" stroke="#C9D5EC" stroke-width="1.1" opacity="0.7"/>'
             + head(U + "hp", 531, 94.7, 10.0) +
             f'<ellipse cx="500" cy="82" rx="15" ry="7" fill="#FFFFFF" fill-opacity="0.45" transform="rotate(-24 500 82)"/></g>'
             f'<rect x="481.4" y="67.4" width="77.2" height="77.2" rx="19" fill="none" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="0.8"/>')
    out.append(("svg", glass))
    out.append(("svg", dashed_line(520, 160, 520, 36, "#FFFFFF", 1.3, "3 4", halo=False)))
    out.append(("svg", dashed_line(516, 140, 539.9, 70.2, FELT, 1.7, "5 3")))
    return out


def roll_arrow():
    pts_ = [(370.2, 139.0), (373.0, 133.0), (375.4, 127.0), (376.9, 121.0), (377.8, 115.0), (378.0, 108.5)]
    return S.ribbon(U + "ra", pts_, 5.0, *INK, head=2.3)


def sequence():
    return S.ribbon(U + "q1", [(210, 112), (219, 112), (230, 112)], 6.0, *GREY, head=2.0) + S.ribbon(U + "q2", [(410, 112), (417, 112), (426, 112)], 6.0, *GREY, head=2.0)


# ---------------------------------------------------------------------------------------------------------------- the graveyard spiral
S1 = [(160.0, 275.2), (169.0, 275.5), (177.9, 275.6), (186.6, 275.4), (194.9, 275.0), (202.9, 274.3), (210.4, 273.5), (217.4, 272.5), (223.7, 271.3), (229.4, 269.9), (234.4, 268.4), (238.6, 266.8), (242.0, 265.0), (244.5, 263.2), (246.2, 261.4), (247.0, 259.5), (247.0, 258.6)]
D1 = [(247.0, 258.6), (244.1, 254.1), (236.0, 250.0), (223.2, 246.7), (206.5, 244.6), (187.2, 243.8), (166.3, 244.5), (145.3, 246.7), (125.5, 250.3), (108.0, 255.4), (94.0, 261.5), (84.3, 268.6), (79.4, 276.1), (78.9, 279.2)]
S2 = [(78.9, 279.2), (81.1, 286.9), (88.3, 294.3), (99.9, 301.0), (115.0, 306.8), (132.8, 311.5), (152.1, 314.9), (171.7, 316.9), (190.3, 317.7), (206.7, 317.3), (220.1, 315.9), (229.5, 313.7), (234.5, 311.1), (235.2, 309.5)]
D2 = [(235.2, 309.5), (232.6, 306.9), (225.5, 304.7), (214.4, 303.3), (200.0, 302.8), (183.4, 303.5), (165.4, 305.4), (147.4, 308.7), (130.4, 313.3), (115.5, 319.0), (103.5, 325.7), (95.3, 333.1), (91.2, 341.0), (90.8, 344.2)]
S3 = [(90.8, 344.2), (92.7, 352.2), (98.9, 359.9), (108.8, 367.0), (121.8, 373.4), (136.9, 378.8), (153.3, 383.1), (169.9, 386.3), (185.6, 388.4), (199.5, 389.5), (210.7, 389.8), (218.6, 389.5), (222.7, 388.9), (223.3, 388.4)]
D3 = [(223.3, 388.4), (221.0, 387.8), (215.0, 387.5), (205.6, 387.8), (193.6, 389.0), (179.6, 391.2), (164.6, 394.4), (149.5, 398.8), (135.3, 404.2), (122.9, 410.6), (113.1, 417.8), (106.3, 425.6), (102.9, 433.8), (102.6, 437.1)]
S4 = [(102.6, 437.1), (103.7, 443.8), (107.1, 450.3), (112.5, 456.6), (119.7, 462.5), (128.5, 468.0), (138.4, 473.0), (149.1, 477.4), (160.0, 481.2), (170.8, 484.5), (181.0, 487.2), (190.2, 489.3), (198.1, 491.1), (204.3, 492.5), (208.7, 493.6)]


def smooth_curve(points, per=4):
    return H.catmull_points(points, per)


def spiral_card():
    x, y, w, h = 8, 208, 304, 324
    hz = 506
    body = (S.plain(U + "s", x, x + w, hz, y + h, seed=7, hills=18, palms=[(34, 524, 0.5)], houses=[(250, 516, 0.5)])
            + S.land_layer(U + "sl", S.ridge(12, x, x + w, hz + 1, 8, peaks=0.35), hz + 3, ("#8E9DC2", "#C3CDE2"), rim=False, haze=0.2))
    return S.card(U + "S", x, y, w, h, SKY, body)


def tube_from(points, half, colours, shadow=0.0):
    pts_ = smooth_curve(points, 5)
    widths = [half] * len(pts_)
    return H.ribbon_tube(pts_, widths, colours, p=U, shadow=shadow)


def spiral():
    back = ("#46546E", "#8795AE", "#6F7E98", "#D5DEEE")             # the far side of a loop: paler, thinner
    front = ("#0E1626", "#2B3B58", "#1B2740", "#9DB1D8")
    out = []
    for seg in (D1, D2, D3):
        out.append(tube_from(seg, 1.55, back, shadow=0.0))
    for seg in (S1, S2, S3):
        pts_ = smooth_curve(seg, 5)
        # a front arc swells towards the middle (nearer the eye) and thins at its ends where it turns away
        widths = [1.7 + 1.5 * math.sin(math.pi * i / (len(pts_) - 1)) ** 0.8 for i in range(len(pts_))]
        out.append(H.ribbon_tube(pts_, widths, front, p=U, shadow=0.26))
    pts_ = smooth_curve(S4, 5)
    widths = [1.7 + 1.5 * math.sin(math.pi * 0.85 * i / (len(pts_) - 1)) ** 0.8 for i in range(len(pts_))]
    out.append(H.ribbon_tube(pts_, widths, front, p=U, shadow=0.26))
    # the arrowhead at the end of the track
    (x0, y0), (x1, y1) = S4[-2], S4[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + 9 * math.cos(ang), y1 + 9 * math.sin(ang))
    nx, ny = -math.sin(ang), math.cos(ang)
    head_pts = [(x1 - 3 * math.cos(ang) + nx * 6.5, y1 - 3 * math.sin(ang) + ny * 6.5), tip, (x1 - 3 * math.cos(ang) - nx * 6.5, y1 - 3 * math.sin(ang) - ny * 6.5)]
    out.append(f'<polygon points="{S.pts(head_pts)}" fill="#1B2740" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="0.9" stroke-linejoin="round"/>')
    # the three beads
    for k, (bx, by) in enumerate([(238.0, 250.8), (102.5, 362.8), (121.8, 463.9)]):
        out.append(H.ball(f"{U}bead{k}", bx, by, 5.4, "#FFE3DD", "#E5493C", "#8F1812", rim="#FFFFFF", p=U))
    shadow = f'<ellipse cx="160" cy="507" rx="66" ry="3.4" fill="#6B573A" fill-opacity="0.22" filter="url(#{U}b2)"/>'
    return shadow + "".join(out)


# ---------------------------------------------------------------------------------------------------------------- the somatogravic illusion
def somato_card():
    x, y, w, h = 322, 208, 310, 324
    hz = 470
    body = (S.plain(U + "g", x, x + w, hz, y + h, seed=9, hills=20, palms=[(600, 504, 0.55), (352, 508, 0.5)], houses=[(560, 496, 0.55)], acacias=[(420, 516, 0.5)])
            + S.land_layer(U + "gl2", S.ridge(15, x, x + w, hz + 1, 9, peaks=0.35), hz + 3, ("#8E9DC2", "#C3CDE2"), rim=False, haze=0.2))
    return S.card(U + "G", x, y, w, h, SKY, body)


def somato():
    out = []
    # the aeroplane's attitude felt (nose high): the old outline, turned 28 degrees nose up about (472, 300)
    shape = "M -19 -1 L 10 -3 Q 17 -2 18 1 Q 16 4 9 4 L -17 3 Z M -19 -1 L -23 -11 L -18 -11 L -11 -1 Z"
    felt = (f'<g transform="translate(472 300) rotate(-28) scale(2.2)"><path d="{shape}" fill="none" stroke="#FFFFFF" stroke-width="2.1" stroke-opacity="0.85" stroke-linejoin="round"/>'
            f'<path d="{shape}" fill="none" stroke="{FELT}" stroke-width="0.82" stroke-dasharray="2.3 1.5" stroke-linejoin="round"/></g>')
    out.append(felt)
    # the two forces and what is felt: from the pivot (468, 340)
    r = S.ribbon
    out.append(dashed_line(432, 340, 432, 430, "#7A879B", 1.2, "3 3"))
    out.append(dashed_line(468, 430, 432, 430, "#7A879B", 1.2, "3 3"))
    out.append(r(U + "gv", [(468, 340), (468, 380), (468, 424)], 5.4, *INK, head=2.2))
    out.append(r(U + "ac", [(468, 340), (452, 340), (437, 340)], 5.4, *INK, head=2.2))
    out.append(r(U + "fl", [(468, 340), (451, 382), (435.5, 422.5)], 5.4, *BLUE, head=2.2))
    out.append(f'<path d="M 468,386 C 464.5,386 458,385 450.9,382.7" fill="none" stroke="#FFFFFF" stroke-width="3.6" stroke-opacity="0.8"/><path d="M 468,386 C 464.5,386 458,385 450.9,382.7" fill="none" stroke="{FELT}" stroke-width="1.6"/>')
    out.append(f'<text x="456" y="404" font-family="sans-serif" font-size="14" font-weight="bold" fill="{FELT}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.85" paint-order="stroke">θ</text>')
    # the path pushing the nose down would follow
    out.append(r(U + "rd", [(524, 280), (548, 306), (561, 350), (567, 408)], 5.2, *RED, head=2.3))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([
        c(1, 32, 32), c(2, 232, 32), c(3, 432, 32), c(4, 52, 182, 66, 116.5), c(5, 608, 60, 522, 46),
        c(6, 274, 229, 243, 248), c(7, 288, 333, 108.5, 360.5), c(8, 40, 474, 116, 466), c(9, 288, 488, 268, 504),
        c(10, 352, 236), c(11, 504, 396, 471, 396), c(12, 392, 324, 436, 339), c(13, 392, 406, 442, 403), c(14, 542, 236, 492, 281), c(15, 606, 380, 564, 370)])


def plate():
    layers = ['<rect x="0" y="0" width="640" height="540" fill="#ffffff"/>', H.common_defs(U), top_card(), leans()]
    for kind, item in planes() + cabin():
        layers.append(item)
    layers += [roll_arrow(), sequence(), spiral_card(), spiral(), somato_card()]
    layers += [{"name": "cloud-cumulus-b", "at": [70, 242], "width": 44, "opacity": 0.95}, {"name": "cloud-cumulus-c", "at": [268, 410], "width": 36, "opacity": 0.9},
               {"name": "cloud-cumulus-a", "at": [590, 262], "width": 70, "opacity": 0.95}, {"name": "cloud-cumulus-b", "at": [372, 290], "width": 40, "opacity": 0.9}]
    layers += [{"name": "sprite-side", "at": [472, 300], "width": 100, "angle": -6.0, **LOOK}, somato()]
    layers.append(callouts())
    return {
        "id": "fig-23-06-vestibular-illusions",
        "replaces": "fig-23-06-vestibular-illusions.svg",
        "book_file": "plate-23-06-vestibular-illusions.jpg",
        "caption": "Figure 23-6. Vestibular illusions: the leans, the graveyard spiral and the somatogravic illusion",
        "desc": "Figure 23-6. Vestibular illusions: the leans, the graveyard spiral and the somatogravic illusion",
        "legend": [
            "A roll too slow for the canals: you feel level.",
            "A brisk roll to wings level: you now feel banked the other way.",
            "The pilot leans toward the original bank, or rolls back into it.",
            "Blue dashed: the attitude you feel.",
            "Grey dashed: the true vertical.",
            "A long, steady turn feels level as height is lost.",
            "Pulling back tightens the spiral.",
            "Rolling out feels like a turn the other way: the pilot re-enters.",
            "The ground.",
            "The somatogravic illusion, after takeoff or in a go-around.",
            "Gravity.",
            "Acceleration pressing you into the seat.",
            "What you feel as down: the two combined, tilted back by θ.",
            "The attitude you feel: nose high.",
            "Pushing the nose down heads for the ground.",
        ],
        "canvas": [640, 540],
        "background": "pale",
        "reskin": {"svg": "fig-23-06-vestibular-illusions.svg", "blank": True, "layers": layers},
    }
