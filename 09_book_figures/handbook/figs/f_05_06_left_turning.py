"""Figure 5-6 (new). The four left-turning tendencies of a single-engine aeroplane with a propeller that turns clockwise as the pilot sees it, one panel each, in the order of Chapter 5's section: 1 torque reaction, 2 the spiralling slipstream, 3 gyroscopic precession, 4 P-factor, on the renders of the model
(sprite-rear, sprite-top): 1 torque reaction (the propeller turns clockwise, the aeroplane rolls the other way, left wing down), 2 P-factor (at high power with the nose high the descending
blade, on the pilot's right, bites harder: more thrust on the right, yaw to the left), 3 the spiralling slipstream (the air thrown back by the propeller corkscrews round the fuselage and
strikes the left side of the fin: the tail is pushed right, the nose left), 4 gyroscopic precession (a force on the top of the propeller disc, as when the tail comes up in the takeoff run,
acts a quarter of a turn on, at the right edge of the disc: the right side of the disc moves forward, the nose yaws left). Blue is the rotation, amber the cause, red the effect on the aeroplane.
Panels 1 and 4 are drawn as the pilot sees them (from behind, forward is away from the viewer: a cross in a circle); panels 2 and 3 are plans, north up, nose up, left is the pilot's left.
No words: arrows, colours and the numbers of the callouts."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 372
U = "lt5"
BLUE, AMBER, RED, SLATE = "#1D4ED8", "#B45309", "#B91C1C", "#475569"
PW, PH = 296.0, 164.0                                               # a panel
PANELS = {1: (12.0, 14.0), 2: (332.0, 14.0), 3: (12.0, 192.0), 4: (332.0, 192.0)}        # top left corner of each


def origin(k):
    return PANELS[k]


def background():
    out = [f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
           f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
           f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
           f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>']
    for k in PANELS:
        x, y = origin(k)
        out.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')
    return "".join(out)


def arc(cx, cy, r, a0, a1, col, width=3.2, head=True):
    """An arc about (cx, cy) from the angle a0 to a1 (degrees clockwise from straight up), arrowhead at a1."""
    p0 = (cx + r * math.sin(math.radians(a0)), cy - r * math.cos(math.radians(a0)))
    p1 = (cx + r * math.sin(math.radians(a1)), cy - r * math.cos(math.radians(a1)))
    sign = 1 if a1 > a0 else -1
    large = 1 if abs(a1 - a0) > 180 else 0
    path = f"M{n(p0[0])} {n(p0[1])} A{n(r)} {n(r)} 0 {large} {1 if sign > 0 else 0} {n(p1[0])} {n(p1[1])}"
    t = (math.cos(math.radians(a1)) * sign, math.sin(math.radians(a1)) * sign)
    nn = (-t[1], t[0])
    tip = (p1[0] + t[0] * 4, p1[1] + t[1] * 4)
    h = f"{n(tip[0] + t[0] * 7)},{n(tip[1] + t[1] * 7)} {n(tip[0] + nn[0] * 5.4)},{n(tip[1] + nn[1] * 5.4)} {n(tip[0] - nn[0] * 5.4)},{n(tip[1] - nn[1] * 5.4)}"
    out = (f'<path d="{path}" fill="none" stroke="#FFFFFF" stroke-width="{n(width + 3.4)}" stroke-linecap="round" opacity="0.9"/>'
           f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>')
    if head:
        out += f'<polygon points="{h}" fill="{col}" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round"/>'
    return out


def arrow(x0, y0, x1, y1, col, width=3.4):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - 8 * math.cos(ang), y1 - 8 * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="#FFFFFF" stroke-width="{n(width + 3.2)}" stroke-linecap="round" opacity="0.9"/>'
            f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * 5.6)} {n(hy + ny * 5.6)} L{n(hx - nx * 5.6)} {n(hy - ny * 5.6)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round"/>')


def into_page(x, y, col, r=7.4):
    """A cross in a circle: a force going away from the viewer (forward, for the pilot looking ahead)."""
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#FFFFFF" stroke="{col}" stroke-width="2"/>'
            f'<path d="M{n(x - r * 0.62)} {n(y - r * 0.62)} L{n(x + r * 0.62)} {n(y + r * 0.62)} M{n(x + r * 0.62)} {n(y - r * 0.62)} L{n(x - r * 0.62)} {n(y + r * 0.62)}" stroke="{col}" stroke-width="2" stroke-linecap="round"/>')


# ------------------------------------------------------------------------------------------------------------------ panel 1: torque reaction, seen from behind
def panel1():
    x, y = origin(1)
    cx, cy = x + PW / 2, y + 82.0
    out = [arc(cx, cy - 6, 30, 30, 170, BLUE, 3.2),                                  # the propeller, clockwise from the pilot's seat (drawn in front of the fuselage)
           arc(cx, cy - 6, 60, -30, -160, RED, 3.8)]                                  # the aeroplane rolls the other way: left wing down
    return "".join(out)


def sprites_1():
    x, y = origin(1)
    return A.plane(x + PW / 2, y + 86.0, 232.0, name="sprite-rear")


# ------------------------------------------------------------------------------------------------------------------ panel 2: P-factor, plan
def panel2():
    x, y = origin(4)
    cx, cy = x + PW / 2, y + 96.0
    nose = (cx, cy - 56.0)
    out = [arrow(cx + 16, nose[1] + 22, cx + 16, nose[1] - 22, AMBER, 4.6),             # more thrust on the right (the descending blade)
           arrow(cx - 16, nose[1] + 22, cx - 16, nose[1] + 4, AMBER, 3.0),              # less on the left
           arc(cx, cy + 6, 66, -3, -38, RED, 3.8)]                                         # the nose swings to the left
    return "".join(out)


def sprites_2():
    x, y = origin(4)
    cx, cy = x + PW / 2, y + 96.0
    return [A.plane(cx, cy, 118.0, name="sprite-top"), A.plane(x + 250.0, y + 34.0, 62.0, angle=-14.0, name="sprite-side")]


# ------------------------------------------------------------------------------------------------------------------ panel 3: spiralling slipstream, plan
def panel3():
    x, y = origin(2)
    cx, cy = x + PW / 2, y + 96.0
    out = []
    for phase, col in ((0.0, "#2563EB"), (math.pi, "#60A5FA")):
        pts_ = []
        for k in range(0, 121):
            t = k / 120.0
            yy = cy - 54 + t * 112                                                        # along the fuselage, nose to tail
            xx = cx + 15 * math.sin(phase + t * 4 * math.pi) * (0.6 + 0.8 * t)           # a corkscrew round it
            pts_.append((xx, yy))
        d = "M" + " L".join(f"{n(px)} {n(py)}" for px, py in pts_)
        out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="3.6" stroke-linecap="round" opacity="0.6"/><path d="{d}" fill="none" stroke="{col}" stroke-width="1.7" stroke-linecap="round" opacity="0.9"/>')
    out.append(arrow(cx - 34, cy + 40, cx - 10, cy + 40, AMBER, 3.6))                     # the air strikes the left side of the fin ...
    out.append(arrow(cx + 12, cy + 56, cx + 36, cy + 56, RED, 3.6))                       # ... and the tail goes right, so
    out.append(arc(cx, cy + 6, 66, -3, -38, RED, 3.8))                                    # ... the nose goes left
    return "".join(out)


def sprites_3():
    x, y = origin(2)
    return A.plane(x + PW / 2, y + 96.0, 118.0, name="sprite-top")


# ------------------------------------------------------------------------------------------------------------------ panel 4: gyroscopic precession, seen from behind
def panel4():
    x, y = origin(3)
    cx, cy = x + 94.0, y + 84.0
    r = 46.0
    out = [f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#E8EEF7" fill-opacity="0.9" stroke="{SLATE}" stroke-width="1.6"/>',
           f'<circle cx="{n(cx)}" cy="{n(cy)}" r="5" fill="{SLATE}"/>']
    for k in range(2):                                                                      # the two blades
        a = math.radians(-8 + 180 * k)
        out.append(f'<line x1="{n(cx + 40 * math.sin(a))}" y1="{n(cy - 40 * math.cos(a))}" x2="{n(cx - 40 * math.sin(a))}" y2="{n(cy + 40 * math.cos(a))}" stroke="{SLATE}" stroke-width="5" stroke-linecap="round" opacity="0.55"/>')
        break
    out.append(arc(cx, cy, r + 17, -60, 60, BLUE, 3.2))                                      # clockwise
    out.append(into_page(cx, cy - r + 1, AMBER, 8.0))                                        # the push on the top of the disc ...
    out.append(into_page(cx + r - 1, cy, RED, 8.0))                                          # ... acts a quarter turn on, at the right edge
    out.append(f'<path d="M{n(cx + 16)} {n(cy - r + 4)} A{n(r - 4)} {n(r - 4)} 0 0 1 {n(cx + r - 4)} {n(cy - 16)}" fill="none" stroke="{SLATE}" stroke-width="1.4" stroke-dasharray="3 3"/>')
    # the aeroplane in plan, nose swinging left
    px, py = x + 222.0, y + 96.0
    out.append(arc(px, py + 8, 62, -3, -40, RED, 3.8))
    return "".join(out)


def sprites_4():
    x, y = origin(3)
    return A.plane(x + 222.0, y + 96.0, 96.0, name="sprite-top")


def callouts():
    c = S.callout
    r = 9.5
    out = []
    for k in PANELS:
        x, y = origin(k)
        out.append(c(k, x + 18, y + 18, r=r))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), sprites_1(), *sprites_2(), sprites_3(), sprites_4(), panel1(), panel2(), panel3(), panel4(), callouts()]


def plate():
    return {
        "id": "fig-05-06-left-turning",
        "replaces": "fig-05-06-left-turning.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-05-06-left-turning.jpg",
        "caption": "Figure 5-6. The four left-turning tendencies of a single-engine aeroplane whose propeller turns clockwise as the pilot sees it",
        "desc": ("Figure 5-6. The four left-turning tendencies of a single-engine aeroplane whose propeller turns clockwise as the pilot sees it: torque reaction, P-factor, the spiralling slipstream "
                 "and gyroscopic precession, one picture each, on the training aeroplane. Blue is the rotation, amber the cause and red the effect on the aeroplane."),
        "legend": [
            "Torque reaction: the propeller turns clockwise (blue), so the aeroplane tends to roll the other way (red): left wing down. Strongest at high power and low speed.",
            "Spiralling slipstream: the air the propeller throws back corkscrews round the fuselage (blue) and strikes the left side of the fin (amber); the tail is pushed right and the nose yaws left (red).",
            "Gyroscopic precession: a push on the top of the propeller disc (amber), as when the tail comes up in the takeoff run, acts a quarter of a turn on, at the right edge of the disc (red): the right side of the disc moves forward and the nose yaws left. The disc is drawn as the pilot sees it.",
            "P-factor: at high power with the nose high, the descending blade (on the pilot's right) meets the air at a larger angle of attack than the rising one, so the thrust on the right is larger (amber) and the nose yaws left (red).",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
