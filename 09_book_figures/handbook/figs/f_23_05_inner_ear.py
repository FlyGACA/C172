"""Figure 23-5. The inner ear's balance organs, and how the canal fluid lags in a turn. Drawn again as an anatomical illustration (left): the three semicircular canals as glossy
glass tubes in three planes, their ampullae, the vestibule with the utricle and the saccule and their maculae (hair cells under a gel weighted with crystals), the vestibular nerve and
the cochlea as a spiral, on a card of pale tissue; and four rings of a canal in cross-section (right) with the cupula, the arrows of the old figure (actual rotation in black, the
rotation felt in blue, the fluid's movement in grey) and the key under them. The thirteen numbered callouts of the old figure and what they name are kept."""
import math

from figs import scene as S
from figs import h_a3 as H

n = S.n
U = "f2305"

INK = ("#1F2937", "#667489")
BLUE = ("#2F63C8", "#8DB3F2")
GREY = ("#5F6B7F", "#B4BECE")
AMBER = ("#7A4308", "#E9A537", "#C47A1B", "#FFE2A0")            # rim, body, core, light

CANALS = {"post": (78, 150, 20, 66, -8), "ant": (150, 118, 56, 62, 0), "hor": (214, 206, 62, 22, 0)}


def on_ellipse(key, angle):
    cx, cy, rx, ry, rot = CANALS[key]
    return H.ellipse_points(cx, cy, rx, ry, rot, 1, angle, angle)[0]


def arc_points(cx, cy, r, a0, a1, count=9):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / count)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / count))) for i in range(count + 1)]


# ---------------------------------------------------------------------------------------------------------------- the ear
def defs():
    return ("<defs>"
            + f'<linearGradient id="{U}ves" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.45" stop-color="#E9E1F6"/><stop offset="1" stop-color="#B9ABDC"/></linearGradient>'
            + f'<linearGradient id="{U}gel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6C468"/><stop offset="1" stop-color="#B8691A"/></linearGradient>'
            + f'<linearGradient id="{U}gelv" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F6C468"/><stop offset="1" stop-color="#B8691A"/></linearGradient>'
            + f'<radialGradient id="{U}amp" cx="0.36" cy="0.30" r="0.8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.5" stop-color="#D6E0F6"/><stop offset="1" stop-color="#7F92CC"/></radialGradient>'
            + f'<linearGradient id="{U}nerve" gradientUnits="userSpaceOnUse" x1="104" y1="0" x2="26" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.55" stop-color="#FFFFFF"/><stop offset="1" stop-color="#000000"/></linearGradient>'
            + f'<mask id="{U}nm" maskUnits="userSpaceOnUse" x="0" y="200" width="130" height="110"><rect x="0" y="200" width="130" height="110" fill="url(#{U}nerve)"/></mask>'
            + "</defs>")


def tissue():
    """The card of pale tissue the ear lies on: a soft rose gradient, broad mottling and a lighter patch behind the organs."""
    body = (f'<defs><radialGradient id="{U}tv" cx="0.5" cy="0.45" r="0.62"><stop offset="0" stop-color="#FFFAF6" stop-opacity="0.95"/><stop offset="1" stop-color="#F6DDD5" stop-opacity="0"/></radialGradient>'
            f'<filter id="{U}tn" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.016 0.022" numOctaves="3" seed="11"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 0.84  0 0 0 0 0.52  0 0 0 0 0.50  0 0 0 1.5 -0.62"/></filter></defs>'
            f'<rect x="8" y="8" width="300" height="364" filter="url(#{U}tn)" opacity="0.40"/><rect x="8" y="8" width="300" height="364" fill="url(#{U}tv)"/>')
    return S.card(U + "c", 8, 8, 300, 364, [(0, "#FBEAE4"), (1, "#F1D6CD")], body)


def glass(key, w=12.0, tone=0):
    cx, cy, rx, ry, rot = CANALS[key]
    d = H.d_of(H.ellipse_points(cx, cy, rx, ry, rot, 140), close=True)
    colours = [dict(base="#CFDAF4", edge="#4F6199", shade="#9DB1E4"), dict(base="#D7E1F7", edge="#566AA6", shade="#A6B9E9"), dict(base="#C4D1F0", edge="#4A5C94", shade="#94A8DD")][tone]
    return H.tube(d, w, p=U, **colours)


def ampulla(x, y, r=11.0, tilt=0.0):
    """The swelling at the end of a canal: a glossy bulb with the crista, a little amber flap, standing in it."""
    flap = (f'<g transform="rotate({n(tilt)} {n(x)} {n(y)})"><path d="M {n(x - 3.4)},{n(y + r * 0.55)} Q {n(x - 3.2)},{n(y - r * 0.1)} {n(x - 0.8)},{n(y - r * 0.42)} Q {n(x + 1.4)},{n(y - r * 0.5)} {n(x + 2.6)},{n(y - r * 0.2)} Q {n(x + 3.6)},{n(y + r * 0.2)} {n(x + 3.4)},{n(y + r * 0.55)} Z" '
            f'fill="url(#{U}gelv)" stroke="#7A4308" stroke-width="0.7"/><path d="M {n(x - 2)},{n(y + r * 0.4)} Q {n(x - 2)},{n(y - r * 0.05)} {n(x - 0.4)},{n(y - r * 0.3)}" fill="none" stroke="#FFF1C9" stroke-width="0.9" stroke-linecap="round" opacity="0.9"/></g>')
    return (f'<ellipse cx="{n(x + 1)}" cy="{n(y + 3.2)}" rx="{n(r)}" ry="{n(r)}" fill="#14233F" fill-opacity="0.2" filter="url(#{U}b2)"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#{U}amp)" stroke="#4F6199" stroke-width="1.3"/>'
            + flap
            + f'<ellipse cx="{n(x - r * 0.36)}" cy="{n(y - r * 0.42)}" rx="{n(r * 0.36)}" ry="{n(r * 0.22)}" fill="#FFFFFF" fill-opacity="0.85" transform="rotate(-28 {n(x - r * 0.36)} {n(y - r * 0.42)})"/>')


def maculae():
    """Hair cells under a gel weighted with crystals: the utricle's (a horizontal slab) and the saccule's (a vertical one)."""
    out = []
    # utricle: bristles hang from the roof into the gel
    for i in range(6):
        x = 114.5 + i * 5.2
        out.append(f'<line x1="{n(x)}" y1="199.5" x2="{n(x)}" y2="205.6" stroke="#6B3C0A" stroke-width="0.8"/><circle cx="{n(x)}" cy="199.6" r="1.35" fill="#5B3008"/>')
    out.append(f'<rect x="111" y="205.4" width="31.5" height="9.6" rx="3" fill="url(#{U}gel)" stroke="#7A4308" stroke-width="0.9"/>'
               f'<rect x="113" y="206.4" width="27" height="2.4" rx="1.2" fill="#FFF0C4" opacity="0.7"/>')
    for i in range(7):
        out.append(f'<ellipse cx="{n(114.5 + i * 4.3)}" cy="{n(213.6 - (i % 2) * 0.5)}" rx="1.35" ry="0.8" fill="#FFFFFF" stroke="#8A5A20" stroke-width="0.3"/>')
    # saccule: bristles come from the wall on the right and point into the gel
    for i in range(5):
        y = 216.5 + i * 4.7
        out.append(f'<line x1="161" y1="{n(y)}" x2="155" y2="{n(y)}" stroke="#6B3C0A" stroke-width="0.8"/><circle cx="161.2" cy="{n(y)}" r="1.35" fill="#5B3008"/>')
    out.append(f'<rect x="145.4" y="213.6" width="9.6" height="25" rx="3" fill="url(#{U}gelv)" stroke="#7A4308" stroke-width="0.9"/>'
               f'<rect x="146.4" y="215" width="2.4" height="22" rx="1.2" fill="#FFF0C4" opacity="0.7"/>')
    for i in range(6):
        out.append(f'<ellipse cx="{n(147.4 + (i % 2) * 0.5)}" cy="{n(216.5 + i * 4.2)}" rx="0.8" ry="1.35" fill="#FFFFFF" stroke="#8A5A20" stroke-width="0.3"/>')
    return "".join(out)


def vestibule():
    """The vestibule (utricle and saccule in one glass sac), its maculae seen through it."""
    cx, cy, rx, ry = 135, 218, 41, 27
    return (f'<ellipse cx="{cx + 1.5}" cy="{cy + 4}" rx="{rx}" ry="{ry}" fill="#14233F" fill-opacity="0.22" filter="url(#{U}b2)"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{U}ves)" stroke="#6B5BA3" stroke-width="1.5"/>'
            f'<ellipse cx="{cx}" cy="{cy + 3}" rx="{rx - 5}" ry="{ry - 6}" fill="#B9ABDC" fill-opacity="0.35"/>'
            + maculae()
            + f'<path d="M {cx - 33},{cy - 8} Q {cx - 24},{cy - 22} {cx - 4},{cy - 23.5}" fill="none" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round" opacity="0.8" filter="url(#{U}b1)"/>'
            f'<path d="M {cx - 32},{cy - 9} Q {cx - 24},{cy - 21} {cx - 8},{cy - 23}" fill="none" stroke="#FFFFFF" stroke-width="1" stroke-linecap="round"/>')


def nerve():
    """The vestibular nerve: two branches of golden fibres leaving the vestibule at the lower left and fading out towards the brain."""
    thick = H.catmull_points([(106, 226), (88, 238), (62, 249), (28, 262)])
    thin = H.catmull_points([(108, 233), (86, 255), (64, 272), (38, 292)])
    body = H.ribbon_tube(thick, [4.2 - 1.0 * i / (len(thick) - 1) for i in range(len(thick))], ("#8F5412", "#EFB24F", "#CD8B2E", "#FFE6AE"), p=U, shadow=0.20)
    body += H.ribbon_tube(thin, [2.9 - 0.5 * i / (len(thin) - 1) for i in range(len(thin))], ("#8F5412", "#EFB24F", "#CD8B2E", "#FFE6AE"), p=U, shadow=0.18)
    fibres = ""
    for pl in (thick, thin):
        fibres += f'<path d="{H.d_of(pl[2:])}" fill="none" stroke="#9A5A12" stroke-width="0.4" stroke-opacity="0.6" stroke-dasharray="3 2"/>'
    return f'<g mask="url(#{U}nm)">{body}{fibres}</g>'


def cochlea():
    """The cochlea: a tube that coils inward for two and a quarter turns, thinning as it goes, with the short duct that joins it to the vestibule."""
    cx, cy, r0, turns = 149, 298, 28.0, 2.25
    steps = 190
    centre, widths = [], []
    for i in range(steps + 1):
        t = i / steps
        theta = math.radians(225.0 - 360.0 * turns * t)
        r = r0 * 0.5 ** (turns * t)
        centre.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
        widths.append((0.30 * r + 0.5) * min(1.0, 0.36 + t / 0.07))             # (it starts as thin as the duct that brings it and swells into the first whorl)
    stem = H.catmull_points([(141, 236), (137, 254), (131, 268), centre[0]])[:-1]
    out = H.ribbon_tube(stem + centre, [3.0] * len(stem) + widths, ("#8C6A3E", "#F6E8CB", "#DCC499", "#FFFFFF"), p=U, shadow=0.24)
    ridges = []
    for i in range(16, steps - 6, 9):                                   # the rungs of the spiral staircase, a hint of them across the tube
        (x, y), (x2, y2) = centre[i], centre[i + 1]
        tx, ty = x2 - x, y2 - y
        ln = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / ln, tx / ln
        ridges.append(f'<line x1="{n(x + nx * widths[i] * 0.78)}" y1="{n(y + ny * widths[i] * 0.78)}" x2="{n(x - nx * widths[i] * 0.78)}" y2="{n(y - ny * widths[i] * 0.78)}" stroke="#8C6A3E" stroke-opacity="0.32" stroke-width="0.6"/>')
    return out + "".join(ridges)


def ear():
    """All of the organ, back to front."""
    out = [glass("post", 11.0, 2), glass("ant", 12.0, 1), glass("hor", 11.0, 0)]
    out.append(cochlea())
    out.append(nerve())
    out.append(vestibule())
    out += [ampulla(112, 176, 11.5, -20), ampulla(92, 210, 11.0, 8), ampulla(166, 208, 11.0, 70)]
    return "".join(out)


# ---------------------------------------------------------------------------------------------------------------- the four rings
def cupula(cx, cy, lean, w=1.0):
    """The cupula standing in the tube at the bottom of a ring (cx, cy is the middle of the tube there), upright or bent by `lean` units to one side."""
    base_l, base_r = cx - 5.4 * w, cx + 5.4 * w
    top_l, top_r = cx - 3.0 * w + lean, cx + 3.0 * w + lean
    y0, y1 = cy + 6.2, cy - 6.4
    bend = lean * 0.55
    d = (f'M {n(base_l)},{n(y0)} Q {n(base_l + bend)},{n(cy)} {n(top_l)},{n(y1)} Q {n(cx + lean)},{n(y1 - 2.0)} {n(top_r)},{n(y1)} Q {n(base_r + bend)},{n(cy)} {n(base_r)},{n(y0)} Z')
    return (f'<path d="{d}" fill="#14233F" fill-opacity="0.25" transform="translate(1 1.6)" filter="url(#{U}b1)"/>'
            f'<path d="{d}" fill="url(#{U}gelv)" stroke="#6E3A06" stroke-width="1"/>'
            f'<path d="M {n(cx - 3.2 * w + bend * 0.5)},{n(y0 - 1.5)} Q {n(cx - 2.2 * w + lean * 0.8)},{n(cy)} {n(cx - 1.4 * w + lean)},{n(y1 + 1.4)}" fill="none" stroke="#FFF2C9" stroke-width="1.3" stroke-linecap="round" opacity="0.9"/>')


def ring(cx, cy, stage, uid):
    """One ring of a canal in cross-section: a glassy tube of fluid, the cupula at the foot, and the arrows of the stage (0 rest, 1 a turn begins, 2 a steady turn, 3 the turn stops)."""
    r = 38.0
    d = H.d_of(H.ellipse_points(cx, cy, r, r, 0, 120), close=True)
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r - 6}" fill="url(#{U}in)" />']
    out.append(H.tube(d, 12.0, base="#D9E8FB", edge="#4C6AA3", shade="#A9C6EC", p=U))
    out.append(cupula(cx, cy + r, {0: 0.0, 1: 5.5, 2: 0.0, 3: -5.5}[stage]))
    if stage in (1, 2):                                                    # the canal turns clockwise: the black arrow outside
        out.append(S.ribbon(uid + "k", arc_points(cx, cy, 56, 207, 452, 10), 5.2, *INK, head=2.3))
    if stage in (0, 2):
        out.append(f'<text x="{cx}" y="{cy + 5.5}" font-family="sans-serif" font-size="15" font-weight="bold" fill="#1D4ED8" text-anchor="middle">0</text>')
    if stage == 1:                                                         # the fluid lags: it slips counter-clockwise on the ring, and the turn is felt (blue, clockwise)
        out.append(S.ribbon(uid + "g1", arc_points(cx, cy, r, -117, -161, 4), 5.0, *GREY, head=2.2, shadow=False))
        out.append(S.ribbon(uid + "g2", arc_points(cx, cy, r, -18, -62, 4), 5.0, *GREY, head=2.2, shadow=False))
        out.append(S.ribbon(uid + "b", arc_points(cx, cy, 16, 200, 440, 9), 4.6, *BLUE, head=2.3))
    if stage == 3:                                                         # the fluid keeps going: clockwise relative to the stopped canal; the felt turn is the other way
        out.append(S.ribbon(uid + "g1", arc_points(cx, cy, r, -162, -118, 4), 5.0, *GREY, head=2.2, shadow=False))
        out.append(S.ribbon(uid + "g2", arc_points(cx, cy, r, -62, -18, 4), 5.0, *GREY, head=2.2, shadow=False))
        out.append(S.ribbon(uid + "b", arc_points(cx, cy, 16, 100, -140, 9), 4.6, *BLUE, head=2.3))
    return "".join(out)


def sequence_arrows():
    r = S.ribbon
    return "".join([r(U + "s1", [(466, 100), (480, 100), (494, 100)], 6.0, *GREY, head=2.0), r(U + "s2", [(560, 164), (560, 178), (540, 184), (440, 184), (400, 186), (400, 200)], 6.0, *GREY, head=2.0),
                    r(U + "s3", [(466, 268), (480, 268), (494, 268)], 6.0, *GREY, head=2.0)])


def key_row():
    """The key under the rings: the black arrow, the blue arrow, the cupula and a grey arrow in a piece of the tube, each with its callout."""
    r = S.ribbon
    y = 356
    out = [r(U + "k1", [(331, y), (343, y), (356, y)], 6.0, *INK, head=2.1), r(U + "k2", [(396, y), (412, y), (428, y)], 6.0, *BLUE, head=2.1)]
    out.append(cupula(478, y, 0.0, 0.95))
    out.append(f'<rect x="518" y="{y - 10}" width="42" height="20" rx="10" fill="url(#{U}in)" stroke="#4C6AA3" stroke-width="1.6"/>'
               f'<rect x="522" y="{y - 6}" width="34" height="12" rx="6" fill="#D9E8FB"/>')
    out.append(r(U + "k4", [(526, y), (538, y), (552, y)], 5.0, *GREY, head=2.0, shadow=False))
    return "".join(out)


def right_card():
    return S.card(U + "r", 324, 8, 308, 364, [(0, "#F7F9FE"), (1, "#E3EAF6")],
                  f'<defs><radialGradient id="{U}in" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E4ECF8"/></radialGradient></defs>')


def callouts():
    c = S.callout
    a, p, h = on_ellipse("ant", -42), on_ellipse("post", -62), on_ellipse("hor", 22)
    return "".join([
        c(1, 250, 50, a[0], a[1]), c(1, 36, 40, p[0], p[1]), c(1, 282, 160, h[0], h[1]),
        c(2, 222, 262, 172, 214), c(3, 60, 335, 127, 212), c(4, 30, 225, 44, 256), c(5, 232, 320, 176, 305),
        c(6, 334, 34), c(7, 494, 34), c(8, 334, 202), c(9, 494, 202),
        c(10, 370, 356), c(11, 444, 356), c(12, 498, 356), c(13, 574, 356)])


def plate():
    rings = "".join([ring(400, 100, 0, U + "a"), ring(560, 100, 1, U + "b"), ring(400, 268, 2, U + "c"), ring(560, 268, 3, U + "d")])
    return {
        "id": "fig-23-05-inner-ear",
        "replaces": "fig-23-05-inner-ear.svg",
        "book_file": "plate-23-05-inner-ear.jpg",
        "caption": "Figure 23-5. The inner ear's balance organs, and how the canal fluid lags in a turn",
        "desc": "Figure 23-5. The inner ear's balance organs, and how the canal fluid lags in a turn",
        "legend": [
            "The three semicircular canals, at about right angles: together they sense roll, pitch and yaw.",
            "The ampulla, where each canal widens: hair cells in a flap of gel, the cupula, which the fluid bends.",
            "The otolith organs: hair cells under a gel layer weighted with crystals. They sense gravity and linear acceleration, and cannot tell one from the other.",
            "The vestibular nerve.",
            "The cochlea, for hearing.",
            "No rotation: the cupula stands upright; no sensation.",
            "A turn begins: the fluid lags behind the canal and bends the cupula; you feel the turn.",
            "A steady turn: after some seconds the fluid moves with the canal, the cupula straightens, the sensation fades.",
            "The turn stops: the fluid keeps moving and bends the cupula the other way; you feel a turn in the opposite direction.",
            "Black arrow: actual rotation.",
            "Blue arrow: the rotation you feel; 0, none.",
            "The cupula.",
            "Grey arrows: the fluid's movement relative to the canal.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-23-05-inner-ear.svg", "blank": True,
                   "layers": ['<rect x="0" y="0" width="640" height="380" fill="#ffffff"/>', H.common_defs(U), defs(), tissue(), ear(), right_card(), sequence_arrows(), rings, key_row(), callouts()]},
    }
