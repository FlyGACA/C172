"""Figure 6-3 (new). The generic stall recovery of Chapter 6, "The recovery", in its four steps and in its order: reduce the angle of attack, level the wings, add power, return to the flight path.

Four scenes of the same country of the Peninsula, in the style of the weather figures (figs/scene.py: sky, plain, ribbons; the aeroplane sprites laid by reskin.py): 1 the nose is pushed forward and the
disturbed air over the wing is red (the warning and the buffet), 2 the wings are levelled with coordinated aileron and rudder (the aeroplane seen from behind, banked, with a ribbon that rolls it back), 3 the throttle is
pushed forward and the thrust grows (a slider and a ribbon), 4 the aeroplane returns smoothly to its path and a ghost with a red cross marks the second stall to avoid. Shapes, colours and the numbers of the callouts. The drawings
are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar06s"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def panel(i, body, seed):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, PW, PH, DAY) + S.plain(f"{U}g{i}", x, x + PW, y + 128, y + PH, seed=seed, tone="day", acacias=((x + 30, y + 160, 0.9), (x + 270, y + 152, 0.8)), photo=True)
            + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def plane(x, y, width, angle=0.0, name="sprite-side", opacity=None):
    o = {"name": name, "at": [x, y], "width": width, "outline": OUT, "shadow": SHADOW}
    if angle:
        o["angle"] = angle
    if opacity is not None:
        o["opacity"] = opacity
    return o


def scene_1():                                               # nose pushed forward, disturbed air over the wing
    x, y = PX[0], PY[0]
    air = "".join(f'<path d="M{n(x + 100 + k * 18)} {n(y + 74 - k * 3)} q6 -8 12 0 t12 0 t12 0" fill="none" stroke="{RED}" stroke-width="2.6" stroke-linecap="round" stroke-opacity="0.85"/>' for k in range(3))
    push = S.ribbon(f"{U}r1", [(x + 214, y + 42), (x + 222, y + 62), (x + 224, y + 86), (x + 220, y + 106)], 6.4, "#2FA35A", "#9BE0B2", opacity=0.92, head=2.2, tail=0.4, per=8)
    return panel(0, air + push, 4)


def scene_2():                                               # wings level: the aeroplane from behind, banked, rolled back
    x, y = PX[1], PY[1]
    roll = S.ribbon(f"{U}r2", [(x + 84, y + 92), (x + 112, y + 56), (x + 164, y + 44), (x + 214, y + 66)], 6.0, "#2FA35A", "#9BE0B2", opacity=0.92, head=2.2, tail=0.4, per=8)
    return panel(1, roll, 7)


def scene_3():                                               # power: the throttle forward, the thrust grows
    x, y = PX[2], PY[2]
    slider = (f'<rect x="{n(x + 24)}" y="{n(y + 30)}" width="16" height="84" rx="8" fill="#E2E8F0" stroke="{INK}" stroke-width="2.2"/>'
              f'<rect x="{n(x + 20)}" y="{n(y + 36)}" width="24" height="18" rx="5" fill="{RED}" stroke="#7F1D1D" stroke-width="1.6"/>'
              + S.ribbon(f"{U}r3a", [(x + 58, y + 100), (x + 58, y + 80), (x + 58, y + 56), (x + 58, y + 38)], 5.4, "#2FA35A", "#9BE0B2", opacity=0.92, head=2.2, tail=0.4, per=8))
    thrust = S.ribbon(f"{U}r3b", [(x + 200, y + 90), (x + 230, y + 90), (x + 262, y + 90), (x + 290, y + 90)], 9.0, "#E8782E", "#F6B36B", opacity=0.92, head=2.0, tail=0.5, per=8)
    return panel(2, slider + thrust, 9)


def scene_4():                                               # back to the flight path, no second stall
    x, y = PX[3], PY[3]
    path = S.ribbon(f"{U}r4", [(x + 16, y + 132), (x + 70, y + 118), (x + 130, y + 96), (x + 200, y + 86)], 5.0, "#2FA35A", "#9BE0B2", opacity=0.8, head=2.0, tail=0.4, per=8)
    cross = (f'<circle cx="{n(x + 250)}" cy="{n(y + 64)}" r="17" fill="none" stroke="{RED}" stroke-width="3.6"/>'
             f'<line x1="{n(x + 238)}" y1="{n(y + 76)}" x2="{n(x + 262)}" y2="{n(y + 52)}" stroke="{RED}" stroke-width="3.6" stroke-linecap="round"/>')
    return panel(3, path, 12)


def sprites():
    return [plane(PX[0] + 130, PY[0] + 96, 78, angle=-16.0),
            plane(PX[1] + 168, PY[1] + 92, 86, name="sprite-rear", angle=-14.0),
            plane(PX[2] + 140, PY[2] + 96, 74),
            plane(PX[3] + 150, PY[3] + 86, 70, angle=-4.0),
            plane(PX[3] + 252, PY[3] + 56, 40, angle=-18.0, opacity=0.4)]


def overlay():
    x, y = PX[3], PY[3]
    return (f'<circle cx="{n(x + 252)}" cy="{n(y + 58)}" r="19" fill="none" stroke="{RED}" stroke-width="3.6"/>'
            f'<line x1="{n(x + 239)}" y1="{n(y + 71)}" x2="{n(x + 265)}" y2="{n(y + 45)}" stroke="{RED}" stroke-width="3.6" stroke-linecap="round"/>')


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), *sprites(), overlay(), callouts()]


def plate():
    return {
        "id": "fig-06-03-stall-recovery",
        "replaces": "fig-06-03-stall-recovery.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-06-03-stall-recovery.jpg",
        "caption": "Figure 6-3. The stall recovery in order: reduce the angle of attack, level the wings, add power, return to the flight path",
        "desc": ("Figure 6-3. The generic stall recovery in four scenes: the control column is moved forward to reduce the angle of attack; the wings are levelled with coordinated aileron and rudder; "
                 "power is added smoothly; the aeroplane returns to its flight path without pulling into a second stall."),
        "legend": [
            "Reduce the angle of attack: move the control column forward as far as needed to stop the warning and the buffet. Disconnect any autopilot or wing leveller first.",
            "Level the wings with coordinated aileron and rudder once the wing is flying. Use rudder to stop any yaw, so the stall cannot become a spin.",
            "Add power smoothly as needed, with right rudder. Power reduces the height lost, but only a lower angle of attack unstalls the wing.",
            "Return to the desired flight path smoothly, without pulling into a second stall (a secondary stall) or letting the speed run away.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
