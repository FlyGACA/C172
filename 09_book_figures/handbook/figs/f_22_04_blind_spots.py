"""Figure 22-4. Blind spots of a high-wing and a low-wing aeroplane, seen from behind. Three cards of sky and desert. In the first the high-wing trainer of the model from behind (figs/sprites.py),
its pilot's eye marked, and the sky that its wing hides (above the sight lines from the eye over the wing tips) as a dark translucent cone with soft edges; in the second a low-wing
aeroplane drawn to match it (a white fuselage with its canopy and pilot, a wing low on the fuselage with a dihedral, the tailplane, the fin, the gear) with the ground that its wing hides
below the sight lines; in the third both together, the low-wing one descending onto the high-wing one climbing, each inside the other's cone, with the two red arrows. The four numbered
callouts of the old figure (1 twice, as it had it) are kept, in the same order and meaning (figs/scene.py makes the cards and the callouts, figs/h_a2.py the lamps)."""
from figs import h_a2 as H
from figs import scene as S

W, HT = 640, 330
U = "a224"
n = S.n
CARDS = [(6, 10, 204, 310), (218, 10, 204, 310), (430, 10, 204, 310)]
REAR_ASPECT = 303.0 / 1406.0          # the rear sprite's height over its width
EYE_X, EYE_Y, TIP_Y = 0.482, 0.38, 0.17       # the pilot's eye and the wing tips in the rear sprite, as fractions of its width and height


def defs():
    out = ["<defs>", H.lamp_defs(U + "l"), H.blur_filter(U + "b1", 2.4), H.blur_filter(U + "b2", 0.8), S.gradient(U + "bg", [(0, "#F7FAFE"), (1, "#E4EDF7")]), H.shadow_filter(U + "cs", 0, 2.4, 3.2, 0.30, "#10233F")]
    out.append(S.gradient(U + "ws", [(0, "#FFFFFF"), (0.5, "#F1F4F9"), (1, "#C4CCDA")], 0, 0, 1, 0))
    out.append(S.gradient(U + "wv", [(0, "#FFFFFF"), (1, "#CBD3E0")]))
    out.append(S.gradient(U + "gl", [(0, "#8FB4E4"), (0.5, "#4C79B8"), (1, "#27456F")]))
    out.append(S.gradient(U + "ts", [(0, "#F1F4F9"), (1, "#B9C3D3")]))
    out.append("</defs>")
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the cards
def cone(uid, points, colour, fade_from, fade_to, y_from, y_to):
    """A translucent cone of hidden view: the polygon, strongest next to the eye and fading away from it, with a soft edge."""
    return (f'<defs>{S.gradient(uid, [(0, colour, fade_from), (1, colour, fade_to)], 0, y_from, 0, y_to, "userSpaceOnUse")}</defs>'
            f'<polygon points="{S.pts(points)}" fill="url(#{uid})" filter="url(#{U}b1)"/>')


def sight_lines(eye, left, right):
    out = []
    for end in (left, right):
        out.append(f'<line x1="{n(eye[0])}" y1="{n(eye[1])}" x2="{n(end[0])}" y2="{n(end[1])}" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="3.6" stroke-linecap="round"/>'
                   f'<line x1="{n(eye[0])}" y1="{n(eye[1])}" x2="{n(end[0])}" y2="{n(end[1])}" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="1.3" stroke-dasharray="5 4" stroke-linecap="round"/>')
    return "".join(out)


def scenery(k, horizon):
    """Sky above and desert below the horizon (a card's body, in absolute coordinates)."""
    x, y, w, h = CARDS[k]
    uid = f"{U}s{k}"
    out = [f'<defs>{S.gradient(uid + "g", [(0, "#E2D0A2"), (0.35, "#D3BC8B"), (1, "#B89C69")])}</defs>']
    out.append(S.land_layer(uid + "h1", S.ridge(31 + k, x, x + w, horizon + 1, 9, step=3.0, peaks=0.45), horizon + 3, ("#97A6C6", "#C9D3E6"), rim=False, haze=0.32, haze_colour="#EAF1FA"))
    out.append(f'<rect x="{x}" y="{n(horizon)}" width="{w}" height="{n(y + h - horizon)}" fill="url(#{uid}g)"/><line x1="{x}" y1="{n(horizon)}" x2="{x + w}" y2="{n(horizon)}" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.9"/>')
    out.append(S.scrub(41 + k, x + 4, x + w - 4, horizon + 6, y + h - 6, 12, scale=0.7))
    return "".join(out)


def card(k, body):
    x, y, w, h = CARDS[k]
    return S.card(f"{U}c{k}", x, y, w, h, [(0, "#5C8FD0"), (0.55, "#9DC3EA"), (1, "#E6F0FA")], body, 8.0)


# ------------------------------------------------------------------------------------------------------------------ the aeroplanes
def high_wing(cx, wing_y, span):
    """The sprite of the model from behind, placed so that its wing tips are at wing_y; returns the sprite, the eye and the two wing tips."""
    height = span * REAR_ASPECT
    top = wing_y - TIP_Y * height
    sprite = {"name": "sprite-rear", "at": [cx, top + height / 2], "width": span, "outline": {"width": 0.5, "colour": "#223049", "opacity": 0.8}, "shadow": {"dx": 0.8, "dy": 1.6, "blur": 1.4, "opacity": 0.22}}
    eye = (cx - span / 2 + EYE_X * span, top + EYE_Y * height)
    return sprite, eye, (cx - span / 2, wing_y), (cx + span / 2, wing_y)


def low_wing(uid, cx, cy, k):
    """A low-wing aeroplane from behind, its wing root level at cy: wing panels with a dihedral and blue tips, the fuselage with its canopy and the pilot, the fin with a red light,
    the tailplane and the gear. k scales it (1 is a wingspan of 180 units). Returns the markup, the eye and the two wing tips."""
    def P(x, y):
        return (cx + x * k, cy + y * k)
    out = []
    outline = f'stroke="#2B3648" stroke-width="{n(0.7 * k + 0.2)}" stroke-linejoin="round"'
    # the gear first (behind the wing)
    for sgn in (-1, 1):
        a, b = P(sgn * 28.5, 2.0), P(sgn * 28.5, 14.3)
        out.append(f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#5B6678" stroke-width="{n(1.9 * k + 0.4)}" stroke-linecap="round"/>'
                   f'<ellipse cx="{n(b[0])}" cy="{n(b[1] + 1.2 * k)}" rx="{n(3.9 * k)}" ry="{n(4.6 * k)}" fill="#1B202B" stroke="#05080F" stroke-width="0.4"/><ellipse cx="{n(b[0] - 1.0 * k)}" cy="{n(b[1] - 0.6 * k)}" rx="{n(1.0 * k)}" ry="{n(2.0 * k)}" fill="#7F8AA2" opacity="0.7"/>')
    # the tailplane, behind the fuselage
    tl, tr = P(-26, -11), P(26, -11)
    out.append(f'<polygon points="{S.pts([P(-27, -11.4), P(27, -11.4), P(27, -8.0), P(-27, -8.0)])}" fill="url(#{U}ts)" {outline}/>')
    # the wing: two panels, the tips higher than the roots (dihedral), tip caps in blue
    for sgn in (-1, 1):
        panel = [P(sgn * 12, -3.0), P(sgn * 90.2, -10.0), P(sgn * 90.2, -4.8), P(sgn * 12, 4.8)]
        out.append(f'<polygon points="{S.pts(panel)}" fill="url(#{U}wv)" {outline}/>')
        cap = [P(sgn * 83.0, -9.5), P(sgn * 90.2, -10.0), P(sgn * 90.2, -4.8), P(sgn * 83.0, -5.3)]
        out.append(f'<polygon points="{S.pts(cap)}" fill="#2F5FB8" {outline}/>')
        edge = [P(sgn * 12, 4.8), P(sgn * 90.2, -4.8)]
        out.append(f'<polyline points="{S.pts(edge)}" fill="none" stroke="#7C879C" stroke-opacity="0.6" stroke-width="{n(0.8 * k + 0.1)}"/>')
    # the fin and its light
    fin = [P(-1.9, -25.6), P(1.9, -25.6), P(1.2, -50.5), P(-1.2, -50.5)]
    out.append(f'<polygon points="{S.pts(fin)}" fill="url(#{U}ws)" {outline}/>')
    fx, fy = P(0, -51.2)
    out.append(H.lamp(U + "l", fx, fy, 1.3 * k + 0.2, "red", 3.0))
    # the fuselage seen from behind, with the stripe, the canopy and the pilot
    body = H.rrect_path(cx - 14.25 * k, cy - 26.5 * k, 28.5 * k, 28.5 * k, 6.65 * k)
    out.append(f'<path d="{body}" fill="url(#{U}ws)" {outline}/>')
    out.append(f'<rect x="{n(cx - 13.4 * k)}" y="{n(cy - 7.5 * k)}" width="{n(26.8 * k)}" height="{n(3.0 * k)}" fill="#2F5FB8" opacity="0.9"/>')
    cw = H.rrect_path(cx - 11.2 * k, cy - 24.2 * k, 22.4 * k, 14.6 * k, 5.4 * k)
    out.append(f'<path d="{cw}" fill="url(#{U}gl)" stroke="#1B2C4A" stroke-width="{n(0.5 * k + 0.1)}"/>')
    hx, hy = P(-5.7, -17.4)
    out.append(f'<ellipse cx="{n(hx)}" cy="{n(hy)}" rx="{n(3.6 * k)}" ry="{n(4.0 * k)}" fill="#1B2536" opacity="0.88"/><path d="M {n(hx - 5.4 * k)},{n(cy - 9.9 * k)} Q {n(hx)},{n(hy + 2.0 * k)} {n(hx + 5.4 * k)},{n(cy - 9.9 * k)} Z" fill="#1B2536" opacity="0.88"/>')
    out.append(f'<path d="M {n(cx - 9.6 * k)},{n(cy - 23.0 * k)} Q {n(cx)},{n(cy - 25.4 * k)} {n(cx + 9.6 * k)},{n(cy - 23.0 * k)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="{n(0.9 * k + 0.1)}" stroke-linecap="round"/>')
    return "".join(out), P(-5.7, -15.1), P(-90.2, -10.0), P(90.2, -10.0)


def eye_marker(eye, r=2.6):
    return H.lamp(U + "l", eye[0], eye[1], r, "blue", 3.8) + f'<circle cx="{n(eye[0])}" cy="{n(eye[1])}" r="{n(r + 1.4)}" fill="none" stroke="#FFFFFF" stroke-width="0.8" stroke-opacity="0.9"/>'


# ------------------------------------------------------------------------------------------------------------------ the three pictures
def figure():
    cards = []
    sprites = []
    marks = []
    # 1: the high wing
    sp1, eye1, tl1, tr1 = high_wing(108, 174.3, 180.4)
    x, y, w, h = CARDS[0]
    slope_l = (tl1[1] - eye1[1]) / (tl1[0] - eye1[0])
    slope_r = (tr1[1] - eye1[1]) / (tr1[0] - eye1[0])
    el = (x, eye1[1] + slope_l * (x - eye1[0]))
    er = (x + w, eye1[1] + slope_r * (x + w - eye1[0]))
    cards.append(card(0, scenery(0, eye1[1]) + cone(U + "k1", [eye1, el, (x, y), (x + w, y), er], "#0B2250", 0.34, 0.05, eye1[1], y) + sight_lines(eye1, el, er)))
    sprites.append(sp1)
    marks.append(eye_marker(eye1))
    # 2: the low wing
    lw2, eye2, tl2, tr2 = low_wing(U + "a", 320, 142.3, 1.0)
    x, y, w, h = CARDS[1]
    slope_l = (tl2[1] - eye2[1]) / (tl2[0] - eye2[0])
    slope_r = (tr2[1] - eye2[1]) / (tr2[0] - eye2[0])
    el = (x, eye2[1] + slope_l * (x - eye2[0]))
    er = (x + w, eye2[1] + slope_r * (x + w - eye2[0]))
    cards.append(card(1, scenery(1, eye2[1]) + cone(U + "k2", [eye2, el, (x, y + h), (x + w, y + h), er], "#4A2E0C", 0.34, 0.08, eye2[1], y + h) + sight_lines(eye2, el, er)))
    marks.append(lw2 + eye_marker(eye2))
    # 3: both, the low wing above and descending, the high wing below and climbing
    x, y, w, h = CARDS[2]
    lw3, eye3a, tl3a, tr3a = low_wing(U + "b", 512, 104.1, 0.654)
    sp3, eye3b, tl3b, tr3b = high_wing(556, 225.7, 117.8)

    def ends(eye, tl, tr):
        sl, sr = (tl[1] - eye[1]) / (tl[0] - eye[0]), (tr[1] - eye[1]) / (tr[0] - eye[0])
        return (x, eye[1] + sl * (x - eye[0])), (x + w, eye[1] + sr * (x + w - eye[0]))
    la, ra = ends(eye3a, tl3a, tr3a)
    lb, rb = ends(eye3b, tl3b, tr3b)
    body = scenery(2, 296)
    body += cone(U + "k3", [eye3a, la, (x, y + h), (x + w, y + h), ra], "#4A2E0C", 0.26, 0.10, eye3a[1], y + h)
    body += cone(U + "k4", [eye3b, lb, (x, y), (x + w, y), rb], "#0B2250", 0.28, 0.08, eye3b[1], y)
    body += sight_lines(eye3a, la, ra) + sight_lines(eye3b, lb, rb)
    cards.append(card(2, body))
    sprites.append(sp3)
    marks.append(lw3 + eye_marker(eye3a, 2.0) + eye_marker(eye3b, 2.0))
    arrows = (S.ribbon(U + "r1", [(512, 130), (519, 150), (526, 172)], 5.0, "#C81E1E", "#F28A80", head=2.0, tail=0.8) + S.ribbon(U + "r2", [(556, 190), (551, 170), (544, 148)], 5.0, "#C81E1E", "#F28A80", head=2.0, tail=0.8))
    return cards, sprites, marks, arrows, eye1, eye2


def callouts(eye1, eye2):
    c = S.callout
    return "".join([c(1, 40, 230, eye1[0] - 1.5, eye1[1] + 1.5), c(2, 60, 52), c(3, 258, 280), c(1, 332, 40, eye2[0] - 1.5, eye2[1] - 1.5), c(4, 470, 296)])


def layers():
    cards, sprites, marks, arrows, eye1, eye2 = figure()
    # order: the cards, the aeroplanes (the sprites are pictures; the low wings are markup), the eyes, the arrows, the callouts
    return [defs(), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>', *cards, sprites[0], marks[0], marks[1], sprites[1], marks[2], arrows, callouts(eye1, eye2)]


def plate():
    return {
        "id": "fig-22-04-blind-spots",
        "replaces": "fig-22-04-blind-spots.svg",
        "book_file": "plate-22-04-blind-spots.jpg",
        "caption": "Figure 22-4. Blind spots of a high-wing and a low-wing aeroplane, seen from behind",
        "desc": "Figure 22-4. Blind spots of a high-wing and a low-wing aeroplane, seen from behind",
        "legend": [
            "The pilot's eye.",
            "High wing: the wing hides the sky above and to the sides.",
            "Low wing: the wing hides the area below and to the sides.",
            "The worst case: a low-wing aeroplane descending onto a climbing high-wing one, each in the other's blind area.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-22-04-blind-spots.svg", "blank": True, "layers": layers()},
    }
