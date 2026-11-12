"""Figure 18-8. Eight marshalling signals as the pilot sees them. Eight cards, each a picture of the marshaller facing the pilot on an apron: a head with a cap, ear defenders and
dark glasses, a hi-vis vest with reflective bands over a navy shirt, navy trousers and boots, gloves and two lit wands, soft shading from the upper left and a shadow on the ground,
each in the pose of the old figure (the same shoulders, elbows, hands and wands), with the motion of the signal as ribbon arrows (blue; red for the emergency stop). The eight numbered
callouts of the old figure are kept, in the same order (the pictures are drawn in figs/h_a2.py's style of lit forms; figs/scene.py makes the cards, the ribbons and the callouts)."""
import math

from figs import h_a2 as H
from figs import scene as S

W, HT = 640, 490
U = "a188"
n = S.n

CARD_W, CARD_H = 152, 232
COLS = [4, 164, 324, 484]
ROWS = [8, 248]

# ------------------------------------------------------------------------------------------------------------------ poses, in the old figure's coordinates
# each arm: shoulder, elbow, hand, tip of the wand
POSES = [
    dict(left=[(63, 102), (32, 108), (36, 76), (36, 50)], right=[(97, 102), (128, 108), (124, 76), (124, 50)], arrows="arcs2"),
    dict(left=[(223, 102), (202, 102), (182, 102), (162, 102)], right=[(257, 102), (288, 108), (284, 76), (284, 56)], arrows="arc_r"),
    dict(left=[(383, 102), (352, 108), (356, 76), (356, 56)], right=[(417, 102), (438, 102), (458, 102), (478, 102)], arrows="arc_l"),
    dict(left=[(543, 102), (520, 118), (502, 136), (495.3, 161.1)], right=[(577, 102), (600, 118), (618, 136), (624.7, 161.1)], arrows="vert"),
    dict(left=[(63, 342), (54, 314), (58, 288), (83.7, 257.4)], right=[(97, 342), (106, 314), (102, 288), (76.3, 257.4)], arrows="up_blue"),
    dict(left=[(223, 342), (214, 314), (218, 288), (243.7, 257.4)], right=[(257, 342), (266, 314), (262, 288), (236.3, 257.4)], arrows="up_red"),
    dict(left=[(383, 342), (364, 361), (346, 379), (327.6, 397.4)], right=[(417, 342), (436, 361), (454, 379), (472.4, 397.4)], arrows=None),
    dict(left=[(543, 342), (530, 368), (574, 340), (550, 340)], right=[(577, 342), (582, 372), (584, 398), (583.2, 422)], arrows="slice"),
]


def card_origin(i):
    return COLS[i % 4], ROWS[i // 4]


def defs():
    g = S.gradient
    return ("<defs>"
            + g(U + "sl", [(0, "#3C4A6C"), (1, "#18202F")], 0, 0, 1, 1) + g(U + "vs", [(0, "#FBE632"), (0.55, "#EFCB10"), (1, "#D7AC00")], 0, 0, 0.6, 1)
            + g(U + "tr", [(0, "#3A455E"), (1, "#171D2B")], 0, 0, 1, 0.4) + g(U + "sv", [(0, "#F4F6F9"), (0.5, "#C5CCD6"), (1, "#9DA6B4")], 0, 0, 0, 1)
            + g(U + "cp", [(0, "#3A4866"), (1, "#1A2238")], 0, 0, 1, 1) + g(U + "vz", [(0, "#2A3350"), (1, "#121827")])
            + g(U + "df", [(0, "#FF9A45"), (0.5, "#EF6A1E"), (1, "#B83F08")], 0, 0, 1, 1) + g(U + "bt", [(0, "#4A505E"), (0.4, "#1D2029"), (1, "#0D0F15")])
            + g(U + "gl", [(0, "#FFFFFF"), (1, "#C9CFD9")], 0, 0, 1, 1)
            + f'<radialGradient id="{U}sk" cx="0.36" cy="0.3" r="0.85"><stop offset="0" stop-color="#F6D2B2"/><stop offset="0.6" stop-color="#E2A982"/><stop offset="1" stop-color="#B97D57"/></radialGradient>'
            + f'<radialGradient id="{U}nk" cx="0.5" cy="0.2" r="0.9"><stop offset="0" stop-color="#D6A07B"/><stop offset="1" stop-color="#A36C48"/></radialGradient>'
            + H.blur_filter(U + "b1", 1.6) + H.blur_filter(U + "b2", 3.4) + H.blur_filter(U + "b3", 0.7)
            + "</defs>")


# ------------------------------------------------------------------------------------------------------------------ the person
def limb(p0, p1, r0, r1, fill):
    """A tapering limb from p0 to p1 (half widths r0 and r1) with round ends."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    poly = [(p0[0] + nx * r0, p0[1] + ny * r0), (p1[0] + nx * r1, p1[1] + ny * r1), (p1[0] - nx * r1, p1[1] - ny * r1), (p0[0] - nx * r0, p0[1] - ny * r0)]
    # the lit edge: the side that faces the upper left
    sgn = 1 if (nx + ny) < 0 else -1
    hi = [(p0[0] + sgn * nx * r0 * 0.62, p0[1] + sgn * ny * r0 * 0.62), (p1[0] + sgn * nx * r1 * 0.62, p1[1] + sgn * ny * r1 * 0.62)]
    return (f'<polygon points="{S.pts(poly)}" fill="{fill}"/><circle cx="{n(p0[0])}" cy="{n(p0[1])}" r="{n(r0)}" fill="{fill}"/><circle cx="{n(p1[0])}" cy="{n(p1[1])}" r="{n(r1)}" fill="{fill}"/>'
            f'<line x1="{n(hi[0][0])}" y1="{n(hi[0][1])}" x2="{n(hi[1][0])}" y2="{n(hi[1][1])}" stroke="#B9C6E4" stroke-opacity="0.30" stroke-width="{n(max(0.5, r1 * 0.34))}" stroke-linecap="round"/>')


def band(y0, y1, x_left, x_right):
    return f'<polygon points="{S.pts([(x_left(y0), y0), (x_right(y0), y0), (x_right(y1), y1), (x_left(y1), y1)])}" fill="url(#{U}sv)" stroke="#8C95A4" stroke-opacity="0.5" stroke-width="0.3"/>'


def legs_and_boots():
    out = []
    for (hx, ax, bx) in ((72, 66, 66), (88, 94, 94)):
        out.append(limb((hx, 160), (ax, 224), 7.0, 4.9, f"url(#{U}tr)"))
        # the crease down the front of the trouser leg
        out.append(f'<line x1="{n(hx)}" y1="164" x2="{n(ax)}" y2="222" stroke="#6E7A96" stroke-opacity="0.22" stroke-width="0.8"/>')
        # the boot: a rounded toe cap with a lit top
        out.append(f'<path d="M {n(bx - 5.2)},223 L {n(bx + 5.2)},223 Q {n(bx + 7.2)},229 {n(bx + 6.4)},233.4 L {n(bx - 6.4)},233.4 Q {n(bx - 7.2)},229 {n(bx - 5.2)},223 Z" fill="url(#{U}bt)"/>'
                   f'<path d="M {n(bx - 4.4)},224.4 Q {n(bx)},226.6 {n(bx + 4.4)},224.4" fill="none" stroke="#9AA3B4" stroke-opacity="0.5" stroke-width="0.8" stroke-linecap="round"/>'
                   f'<rect x="{n(bx - 6.4)}" y="232.2" width="12.8" height="1.4" rx="0.7" fill="#05070B" opacity="0.9"/>')
    return "".join(out)


def torso():
    """The navy shirt at the collar, then the hi-vis vest: yellow, with silver reflective bands across it (two) and over the shoulders (two), and a front zip."""
    xl = lambda y: 64.4 + (66 - 64.4) * (y - 99.5) / (162 - 99.5)
    xr = lambda y: 95.6 + (94 - 95.6) * (y - 99.5) / (162 - 99.5)
    body = "M 64.4,99.5 Q 66,96.6 72,96.6 L 88,96.6 Q 94,96.6 95.6,99.5 L 94,162 L 66,162 Z"
    out = [f'<path d="{body}" fill="url(#{U}vs)" stroke="#8A6F00" stroke-opacity="0.6" stroke-width="0.7" stroke-linejoin="round"/>']
    out.append(band(121.5, 126, xl, xr) + band(139, 143.5, xl, xr))
    for x0 in (70.5, 85.5):                                     # the bands over the shoulders
        out.append(f'<polygon points="{S.pts([(x0, 97), (x0 + 4, 97), (x0 + 3.3 + (66 - 64.4) * 0.0, 162), (x0 - 0.7, 162)])}" fill="url(#{U}sv)" stroke="#8C95A4" stroke-opacity="0.5" stroke-width="0.3"/>')
    # the collar (the shirt) in a V, and the zip
    out.append(f'<polygon points="{S.pts([(73.4, 96.4), (86.6, 96.4), (80, 108.5)])}" fill="#1E2740"/><polyline points="{S.pts([(73.4, 96.4), (80, 108.5), (86.6, 96.4)])}" fill="none" stroke="#5B6786" stroke-opacity="0.7" stroke-width="0.6" stroke-linejoin="round"/>')
    out.append(f'<line x1="80" y1="108.5" x2="80" y2="162" stroke="#5E4C00" stroke-opacity="0.55" stroke-width="0.7"/>')
    # soft shade down the right side and under the arms
    out.append(f'<path d="M 88,97 L 95.6,99.5 L 94,162 L 86,162 Z" fill="#7A5E00" opacity="0.22"/><path d="M 66,160 L 94,160 L 94,162 L 66,162 Z" fill="#5B4800" opacity="0.30"/>')
    return "".join(out)


def head():
    out = []
    out.append(f'<path d="M 75,92 L 85,92 L 86,100 L 74,100 Z" fill="url(#{U}nk)"/>')
    out.append(f'<circle cx="80" cy="82" r="12" fill="url(#{U}sk)"/>')
    # the cap: a dome over the top of the head, with a peak above the eyes
    out.append(f'<path d="M 67.2,81.6 C 66.4,69.6 72.4,63.6 80,63.6 C 87.6,63.6 93.6,69.6 92.8,81.6 Z" fill="url(#{U}cp)"/>'
               f'<path d="M 70.4,68.4 C 73,65.4 77,64.4 80,64.4" fill="none" stroke="#9FB0D6" stroke-opacity="0.45" stroke-width="1.0" stroke-linecap="round"/>'
               f'<path d="M 66.6,80.4 Q 80,91 93.4,80.4 Q 80,84.6 66.6,80.4 Z" fill="url(#{U}vz)"/><path d="M 68.6,80.8 Q 80,88 91.4,80.8" fill="none" stroke="#6E7EA6" stroke-opacity="0.45" stroke-width="0.6"/>')
    # the dark glasses, a hint of a smile
    out.append(f'<rect x="71.6" y="84.2" width="7.4" height="4.4" rx="2" fill="#0F131C"/><rect x="81" y="84.2" width="7.4" height="4.4" rx="2" fill="#0F131C"/><line x1="79" y1="85.6" x2="81" y2="85.6" stroke="#0F131C" stroke-width="0.8"/>'
               f'<path d="M 72.6,85.2 L 75.2,85.2" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.7" stroke-linecap="round"/><path d="M 82,85.2 L 84.6,85.2" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.7" stroke-linecap="round"/>'
               f'<path d="M 77.4,94.4 Q 80,96.2 82.6,94.4" fill="none" stroke="#9A5A42" stroke-width="0.8" stroke-linecap="round"/>')
    # ear defenders: a band over the cap and a cup on each side
    out.append(f'<path d="M 66.4,84 C 65.4,60 94.6,60 93.6,84" fill="none" stroke="#2E364A" stroke-width="2.4" stroke-linecap="round"/>'
               f'<path d="M 66.6,81 C 66.2,65 72,60.6 78,60.2" fill="none" stroke="#7886A8" stroke-opacity="0.5" stroke-width="0.8" stroke-linecap="round"/>')
    for cx in (65.6, 94.4):
        out.append(f'<ellipse cx="{n(cx)}" cy="85" rx="4.4" ry="6.4" fill="url(#{U}df)" stroke="#7A2A04" stroke-opacity="0.7" stroke-width="0.6"/>'
                   f'<ellipse cx="{n(cx)}" cy="85" rx="2.4" ry="3.8" fill="#8E300A" opacity="0.5"/><path d="M {n(cx - 2.6)},80.4 Q {n(cx - 3)},84 {n(cx - 2.2)},87.4" fill="none" stroke="#FFD2A0" stroke-opacity="0.7" stroke-width="0.8" stroke-linecap="round"/>')
    return "".join(out)


def wand(hand, tip, uid):
    """A lit wand from the hand to its tip: a dark grip, an orange body with a bright core, a glow, and a white-hot tip."""
    hx, hy = hand
    tx, ty = tip
    dx, dy = tx - hx, ty - hy
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    gx, gy = hx + ux * min(9.0, ln * 0.34), hy + uy * min(9.0, ln * 0.34)
    out = [f'<line x1="{n(hx)}" y1="{n(hy)}" x2="{n(tx)}" y2="{n(ty)}" stroke="#FF8A2E" stroke-opacity="0.55" stroke-width="12" stroke-linecap="round" filter="url(#{U}b2)"/>',
           f'<line x1="{n(hx)}" y1="{n(hy)}" x2="{n(tx)}" y2="{n(ty)}" stroke="#7B2D05" stroke-opacity="0.9" stroke-width="6.2" stroke-linecap="round"/>',
           f'<line x1="{n(gx)}" y1="{n(gy)}" x2="{n(tx)}" y2="{n(ty)}" stroke="#F0621A" stroke-width="5.0" stroke-linecap="round"/>',
           f'<line x1="{n(gx)}" y1="{n(gy)}" x2="{n(tx)}" y2="{n(ty)}" stroke="#FFB45E" stroke-width="2.6" stroke-linecap="round"/>',
           f'<line x1="{n(gx + ux * 1.5)}" y1="{n(gy + uy * 1.5)}" x2="{n(tx - ux * 1.2)}" y2="{n(ty - uy * 1.2)}" stroke="#FFF1CC" stroke-width="1.2" stroke-linecap="round"/>',
           f'<line x1="{n(hx)}" y1="{n(hy)}" x2="{n(gx)}" y2="{n(gy)}" stroke="#2A303C" stroke-width="4.6" stroke-linecap="round"/>',
           f'<circle cx="{n(tx)}" cy="{n(ty)}" r="2.3" fill="#FFF7DC"/>']
    return "".join(out)


def arm(points, uid):
    s_, e, h, t = points
    out = [limb(s_, e, 4.6, 4.0, f"url(#{U}sl)"), limb(e, h, 3.9, 3.3, f"url(#{U}sl)")]
    # a thin silver band at the cuff
    dx, dy = h[0] - e[0], h[1] - e[1]
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    bx, by = e[0] + dx * 0.72, e[1] + dy * 0.72
    nx, ny = -uy, ux
    out.append(f'<polygon points="{S.pts([(bx + nx * 3.5, by + ny * 3.5), (bx + ux * 2.2 + nx * 3.4, by + uy * 2.2 + ny * 3.4), (bx + ux * 2.2 - nx * 3.4, by + uy * 2.2 - ny * 3.4), (bx - nx * 3.5, by - ny * 3.5)])}" fill="url(#{U}sv)" stroke="#8C95A4" stroke-opacity="0.5" stroke-width="0.25"/>')
    out.append(f'<circle cx="{n(e[0])}" cy="{n(e[1])}" r="3.9" fill="url(#{U}sl)"/>')
    out.append(wand(h, t, uid))
    out.append(f'<circle cx="{n(h[0])}" cy="{n(h[1])}" r="3.5" fill="url(#{U}gl)" stroke="#7C8594" stroke-width="0.5"/><circle cx="{n(h[0] - 1)}" cy="{n(h[1] - 1.1)}" r="1.1" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def person(i, pose):
    ox, oy = (160 * (i % 4), 240 * (i // 4))
    loc = lambda p: (p[0] - ox, p[1] - oy)
    left = [loc(p) for p in pose["left"]]
    right = [loc(p) for p in pose["right"]]
    out = [f'<g transform="translate({ox} {oy})">']
    out.append(f'<ellipse cx="86" cy="234" rx="34" ry="5" fill="#241B12" opacity="0.30" filter="url(#{U}b2)"/><ellipse cx="80" cy="233.6" rx="26" ry="3.4" fill="#241B12" opacity="0.28" filter="url(#{U}b1)"/>')
    out.append(legs_and_boots())
    out.append(torso())
    out.append(head())
    out.append(arm(left, "l") + arm(right, "r"))
    out.append("</g>")
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ the cards and the arrows
def arc_points(p0, p1, r, sweep, count=14):
    """Points along the small arc of radius r from p0 to p1 (the SVG arc with large-arc 0 and the given sweep flag)."""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    d = math.hypot(x1 - x0, y1 - y0)
    h = math.sqrt(max(r * r - (d / 2) ** 2, 0.0))
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    # the centre lies to the left or the right of the chord depending on the sweep
    cx, cy = (mx + uy * h, my - ux * h) if sweep == 0 else (mx - uy * h, my + ux * h)
    a0, a1 = math.atan2(y0 - cy, x0 - cx), math.atan2(y1 - cy, x1 - cx)
    da = a1 - a0
    while sweep == 1 and da < 0:
        da += 2 * math.pi
    while sweep == 0 and da > 0:
        da -= 2 * math.pi
    return [(cx + r * math.cos(a0 + da * k / count), cy + r * math.sin(a0 + da * k / count)) for k in range(count + 1)]


def two_way(uid, pts_, colour=("#1D4ED8", "#6C97F2"), width=4.6):
    """A ribbon with a head at each end, along the points."""
    mid = len(pts_) // 2
    a, b = pts_[mid:], pts_[:mid + 1][::-1]
    return S.ribbon(uid + "a", a, width, colour[0], colour[1], head=2.0, tail=1.0, per=4) + S.ribbon(uid + "b", b, width, colour[0], colour[1], head=2.0, tail=1.0, per=4)


def one_way(uid, pts_, colour=("#1D4ED8", "#6C97F2"), width=4.6):
    return S.ribbon(uid, pts_, width, colour[0], colour[1], head=2.0, tail=0.6, per=4)


def arrows(i, kind):
    blue, red = ("#1D4ED8", "#6C97F2"), ("#C81E1E", "#F28A80")
    if kind == "arcs2":
        return (two_way(U + "a1l", arc_points((3.7, 71.8), (53.6, 67.4), 46, 1)) + two_way(U + "a1r", arc_points((156.3, 71.8), (106.4, 67.4), 46, 0)))
    if kind == "arc_r":
        return two_way(U + "a2", arc_points((316.3, 71.8), (266.4, 67.4), 46, 0))
    if kind == "arc_l":
        return two_way(U + "a3", arc_points((323.7, 71.8), (373.6, 67.4), 46, 1))
    if kind == "vert":
        return two_way(U + "a4l", [(490, 136), (490, 158), (490, 180)]) + two_way(U + "a4r", [(630, 136), (630, 158), (630, 180)])
    if kind == "up_blue":
        return one_way(U + "a5l", arc_points((5, 340), (39.4, 289.0), 58, 1)) + one_way(U + "a5r", arc_points((155, 340), (120.6, 289.0), 58, 0))
    if kind == "up_red":
        return one_way(U + "a6l", arc_points((165, 340), (199.4, 289.0), 58, 1), red, 5.4) + one_way(U + "a6r", arc_points((315, 340), (280.6, 289.0), 58, 0), red, 5.4)
    if kind == "slice":
        return one_way(U + "a8", [(590, 354), (560, 354), (527, 354)], blue, 5.0)
    return ""


def shoulder_lines():
    """Card 5: the dashed level of the shoulders, which the arms are held out along before they are raised."""
    out = []
    for x0, x1 in ((8, 63), (97, 152)):
        out.append(f'<line x1="{x0}" y1="342" x2="{x1}" y2="342" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="5.4" stroke-linecap="butt"/>'
                   f'<line x1="{x0}" y1="342" x2="{x1}" y2="342" stroke="#5E6878" stroke-width="3.4" stroke-dasharray="4 4"/>')
    return "".join(out)


def card_body(x, y):
    """The apron and the far hills behind a card (card-relative drawing, placed at the card's corner)."""
    uid = f"{U}k{int(x)}_{int(y)}"
    w, h = CARD_W, CARD_H
    hz = 98.0                                                     # the horizon, level with the marshaller's shoulders
    hills = S.land_layer(uid + "h", S.ridge(int(x) + int(y), x, x + w, y + hz + 1, 11, step=4.0, peaks=0.4), y + hz + 4, ("#A8B7D2", "#C9D4E5"), rim=False, haze=0.3, haze_colour="#E8F0FA")
    apron = [f'<defs>{S.gradient(uid + "g", [(0, "#DAD5C6"), (0.35, "#C9C3B3"), (1, "#A9A292")])}</defs>',
             f'<rect x="{x}" y="{y + hz}" width="{w}" height="{h - hz}" fill="url(#{uid}g)"/>']
    # joints of the slabs in perspective
    vx, vy = x + w / 2, y + hz
    for k in range(-5, 6):
        bx = vx + k * 30
        apron.append(f'<line x1="{n(vx + k * 3)}" y1="{n(vy)}" x2="{n(bx * 1.0 + (bx - vx) * 0.6)}" y2="{n(y + h)}" stroke="#7C7565" stroke-opacity="0.30" stroke-width="0.5"/>')
    for k in range(1, 7):
        yy = vy + (h - hz) * (k / 6.0) ** 1.9
        apron.append(f'<line x1="{x}" y1="{n(yy)}" x2="{x + w}" y2="{n(yy)}" stroke="#7C7565" stroke-opacity="0.30" stroke-width="0.5"/>')
    apron.append(f'<line x1="{x}" y1="{n(vy)}" x2="{x + w}" y2="{n(vy)}" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="0.8"/>')
    return hills + "".join(apron)


def cards():
    out = []
    for i in range(8):
        x, y = card_origin(i)
        out.append(S.card(f"{U}c{i}", x, y, CARD_W, CARD_H, S.SKY_PALE, card_body(x, y)))
    return "".join(out)


def callouts():
    out = []
    for i in range(8):
        x, y = card_origin(i)
        out.append(S.callout(i + 1, x + 18, y + 20))
    return "".join(out)


def layers():
    out = [f'<defs>{S.gradient(U + "bg", [(0, "#F7FAFE"), (1, "#E7EEF7")])}</defs><rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>', defs(), cards()]
    for i, pose in enumerate(POSES):
        out.append(person(i, pose))
        if i == 4:
            out.append(shoulder_lines())
        out.append(arrows(i, pose["arrows"]))
    out.append(callouts())
    return out


def plate():
    return {
        "id": "fig-18-08-marshalling",
        "replaces": "fig-18-08-marshalling.svg",
        "book_file": "plate-18-08-marshalling.jpg",
        "caption": "Figure 18-8. Eight marshalling signals as the pilot sees them",
        "desc": "Figure 18-8. Eight marshalling signals as the pilot sees them",
        "legend": [
            "Straight ahead: arms out to the sides, bent at the elbows, wands moving up and down between chest and head.",
            "Turn left, from the pilot's point of view: the signalman's right arm, on your left, held out at 90° to the body, while the other hand signals \"come ahead\". The faster the signal, the faster the turn.",
            "Turn right: the mirror image.",
            "Slow down: extended arms patting downwards, the wands moving between waist and knees.",
            "Normal stop: arms held out at 90° to the sides and moved slowly up until the wands cross above the head.",
            "Emergency stop: arms and wands thrown abruptly up to the top of the head, wands crossed.",
            "Hold position, stand by: arms and wands held downwards at 45° to the sides until the aircraft is cleared for its next manoeuvre.",
            "Cut engines: the wand drawn across the throat in a slicing motion, from the signalman's left shoulder to the right.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-08-marshalling.svg", "blank": True, "layers": layers()},
    }
