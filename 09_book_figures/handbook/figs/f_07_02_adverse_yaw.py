"""Figure 7-2 (new). Adverse yaw, from the section "Ailerons and adverse yaw" of Chapter 7, on the top view of the training aeroplane (sprite-top, nose up), in two panels.

Left, aileron alone, a roll to the right: the right aileron rises and the left one goes down (a short arrow beside each aileron); the left wing, with the lowered aileron (a blue patch; the raised one is grey), makes more lift and therefore more induced drag (red arrow, aft),
which holds it back and yaws the nose away from the turn, to the left (amber arrow at the nose). Right, aileron and rudder together in the same direction: the right rudder (green arrow at the fin, pushing the tail to the left) yaws the nose to the right, cancels
the swing and the nose goes round with the turn. The sizes of the arrows show the idea; they are not measured. No words: shapes, colours and the numbers of the callouts."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "ay7"
CX = (160.0, 480.0)
PW = 188.0                                                 # width of the top sprite
PY = 156.0                                                 # its centre
BLUE, AMBER, RED, GREEN, SLATE = "#1D4ED8", "#B45309", "#B91C1C", "#15803D", "#475569"
WING = 92.0                                                # half span on the canvas, about
TE = 8.0                                                   # y offset of the wing's trailing edge from the centre of the sprite (tuned by eye)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            f'<line x1="320" y1="22" x2="320" y2="{HT - 22}" stroke="{SLATE}" stroke-opacity="0.2" stroke-width="1"/>')


def arrow(x0, y0, x1, y1, col, width=3.4, head=8.0, halo=True):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    out = ""
    if halo:
        out += f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="#FFFFFF" stroke-width="{n(width + 3)}" stroke-linecap="round" opacity="0.85"/>'
    out += (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * head * 0.62)} {n(hy + ny * head * 0.62)} L{n(hx - nx * head * 0.62)} {n(hy - ny * head * 0.62)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="0.8" stroke-linejoin="round"/>')
    return out


def turn_arrow(cx, cy, r, a0, a1, col, width=3.6, head=9.0):
    """An arc from angle a0 to a1 (degrees, 0 = up, clockwise positive) with an arrowhead at a1."""
    p0 = (cx + r * math.sin(math.radians(a0)), cy - r * math.cos(math.radians(a0)))
    p1 = (cx + r * math.sin(math.radians(a1)), cy - r * math.cos(math.radians(a1)))
    sweep = 1 if a1 > a0 else 0
    d = f"M{n(p0[0])} {n(p0[1])} A{n(r)} {n(r)} 0 0 {sweep} {n(p1[0])} {n(p1[1])}"
    t = math.radians(a1 + (90 if a1 > a0 else -90))
    tx, ty = math.sin(t), -math.cos(t)
    nx, ny = -ty, tx
    bx, by = p1[0] + tx * head, p1[1] + ty * head
    return (f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{n(width + 3)}" stroke-linecap="round" opacity="0.85"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<path d="M{n(bx)} {n(by)} L{n(p1[0] + nx * head * 0.62)} {n(p1[1] + ny * head * 0.62)} L{n(p1[0] - nx * head * 0.62)} {n(p1[1] - ny * head * 0.62)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="0.8" stroke-linejoin="round"/>')


def panel(i):
    cx = CX[i]
    out = []
    # the ailerons, outboard on the trailing edges: the left one goes down (blue), the right one up (grey)
    for x, col in ((cx - 62.0, BLUE), (cx + 62.0, "#94A3B8")):
        out.append(f'<rect x="{n(x - 21)}" y="{n(PY - 20)}" width="42" height="9" rx="2.5" fill="{col}" stroke="#FFFFFF" stroke-width="1.6" filter="url(#{U}ds)"/>')
    # induced drag, aft: more on the wing with the lowered aileron
    out.append(arrow(cx - 62, PY - 8, cx - 62, PY + 52, RED, 3.6, 8.5))
    out.append(arrow(cx + 62, PY - 8, cx + 62, PY + 24, RED, 3.0, 7.5))
    if i == 0:
        out.append(turn_arrow(cx, PY + 4, 112.0, -4, -34, AMBER))          # the nose swings to the left, away from the turn
    else:
        out.append(arrow(cx + 24, PY + 66, cx - 10, PY + 66, GREEN, 3.8, 9.0))    # the rudder pushes the tail to the left
        out.append(turn_arrow(cx, PY + 4, 112.0, 4, 34, GREEN))             # and the nose to the right
    return "".join(out)


def callouts():
    c = S.callout
    out = []
    out.append(c(1, CX[0] - 112, 100.0, CX[0] - 78, PY - 17, r=9.5))        # the ailerons
    out.append(c(2, CX[0] - 96, 262.0, CX[0] - 64, PY + 46, r=9.5))         # the induced drag
    out.append(c(3, CX[0] + 74, 52.0, CX[0] - 34, PY - 100, r=9.5))         # the nose swings to the left
    out.append(c(4, CX[1] + 84, 262.0, CX[1] + 6, PY + 66, r=9.5))          # the rudder
    return "".join(out)


def sprites():
    return [A.plane(CX[i], PY, PW, name="sprite-top") for i in range(2)]


def layers():
    return [H.defs(U, W, HT), background(), *sprites(), panel(0), panel(1), callouts()]


def plate():
    return {
        "id": "fig-07-02-adverse-yaw",
        "replaces": "fig-07-02-adverse-yaw.svg",           # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-07-02-adverse-yaw.jpg",
        "caption": "Figure 7-2. Adverse yaw in a roll to the right, and how rudder in the same direction cancels it (seen from above)",
        "desc": ("Figure 7-2. Adverse yaw in a roll to the right, seen from above. Left, aileron alone: the left aileron goes down and the right one up; the left wing makes more lift and more induced drag, "
                 "and the nose swings to the left, away from the turn. Right, aileron and rudder together in the same direction: the rudder cancels the swing."),
        "legend": [
            "Turn the wheel right: the right aileron rises (grey) and the left one goes down (blue), and the aeroplane rolls right.",
            "The wing with the lowered aileron, the left, makes more lift and therefore more induced drag (the red arrows, longer on the left; the sizes are for the idea), which holds it back.",
            "So the nose first swings to the left, away from the turn (the amber arrow): adverse yaw, strongest at low airspeed and high angle of attack.",
            "Right panel: the right rudder, applied at the same time as the right aileron, pushes the tail to the left and the nose to the right (the green arrows), cancels the swing and keeps the ball centred.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
