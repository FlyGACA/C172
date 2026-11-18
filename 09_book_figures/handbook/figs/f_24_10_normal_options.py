"""Figure 24-10 (new). The normal options of Chapter 24, "The go-around and the diversion are normal" and "Turning back without blame": four scenes.

Drawn in the style of the other illustrated figures (figs/scene.py: sky, plain, ribbons; the aeroplane and cloud sprites laid by reskin.py): 1 a go-around from an approach that is not stable (the descent path and the climb away), 2 a diversion (the route
A to B, the dust over B at the descent point and the way on to C, in plan), 3 a turn-back (the aeroplane turns away from a storm ahead), 4 the agreement before the first solo (the instructor and the student, and a green tick on the decision that costs
time). Shapes, colours and the numbers of the callouts. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar24n"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def frame(i, body):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def side(i, seed, hz=100.0, tone="day", stops=DAY, extra=""):
    x, y = PX[i], PY[i]
    return frame(i, S.sky(f"{U}k{i}", x, y, PW, PH, stops) + S.plain(f"{U}g{i}", x, x + PW, y + hz, y + PH, seed=seed, tone=tone, acacias=((x + 30, y + 150, 0.9),)) + extra)


def tick(cx, cy, r=15.0):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{GREEN}" stroke="#FFFFFF" stroke-width="2"/>'
            f'<path d="M{n(cx - r * 0.5)} {n(cy + r * 0.05)} L{n(cx - r * 0.12)} {n(cy + r * 0.42)} L{n(cx + r * 0.55)} {n(cy - r * 0.38)}" fill="none" stroke="#FFFFFF" stroke-width="{n(r * 0.24)}" stroke-linecap="round" stroke-linejoin="round"/>')


def scene_1():                                               # go-around: the approach path and the climb away
    x, y = PX[0], PY[0]
    rw = f'<path d="M{n(x + 150)} {n(y + 136)} L{n(x + PW)} {n(y + 136)} L{n(x + PW)} {n(y + 152)} L{n(x + 140)} {n(y + 152)} Z" fill="#5B6577"/><line x1="{n(x + 160)}" y1="{n(y + 144)}" x2="{n(x + PW)}" y2="{n(y + 144)}" stroke="#F1F5F9" stroke-width="1.8" stroke-dasharray="9 7"/>'
    down = S.ribbon(f"{U}a", [(x + 14, y + 50), (x + 60, y + 76), (x + 110, y + 106), (x + 150, y + 128)], 4.8, "#7C8FB5", "#C7D2E8", opacity=0.6, head=1.0, tail=0.5, per=8)
    up = S.ribbon(f"{U}b", [(x + 150, y + 128), (x + 190, y + 112), (x + 232, y + 82), (x + 284, y + 48)], 6.4, "#2FA35A", "#9BE0B2", opacity=0.92, head=2.2, tail=0.4, per=8)
    return side(0, 4, 100.0, extra=rw + down + up)


def scene_2():                                               # diversion: A, B with dust, C, in plan
    x, y = PX[1], PY[1]
    ground = f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="#E8D7AC"/>'
    for sx, sy, w in ((x + 24, y + 128, 40), (x + 244, y + 54, 40), (x + 200, y + 142, 40)):
        ground += f'<rect x="{n(sx)}" y="{n(sy)}" width="{n(w)}" height="10" rx="2" fill="#5B6577"/><line x1="{n(sx + 4)}" y1="{n(sy + 5)}" x2="{n(sx + w - 4)}" y2="{n(sy + 5)}" stroke="#F1F5F9" stroke-width="1.2" stroke-dasharray="6 4"/>'
    dust = S.fog(f"{U}d2", x + 190, x + PW, y + 100, 80, seed=5, opacity=0.95, colour="#C99F5E", wisp=1.0, foot=0.4, side_fade=0.3)
    route = S.ribbon(f"{U}r2", [(x + 54, y + 132), (x + 110, y + 112), (x + 170, y + 82), (x + 226, y + 62)], 5.0, "#2FA35A", "#9BE0B2", opacity=0.55, head=2.0, tail=0.4, per=8)
    divert = S.ribbon(f"{U}v2", [(x + 160, y + 86), (x + 178, y + 110), (x + 196, y + 130), (x + 214, y + 140)], 6.2, "#E8782E", "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=8)
    return frame(1, ground + dust + route + divert)


def scene_3():                                               # turn back: the storm ahead, the turn away
    x, y = PX[2], PY[2]
    turn = S.ribbon(f"{U}t3", [(x + 190, y + 84), (x + 230, y + 70), (x + 238, y + 112), (x + 190, y + 120), (x + 100, y + 116)], 6.0, "#E8782E", "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=8)
    return side(2, 9, 110.0, stops=[(0.0, "#3E5A8C"), (0.5, "#7C93B8"), (0.9, "#C9D2E0"), (1.0, "#E4DFCF")], extra=S.rain(f"{U}r3", x + 214, x + 292, y + 90, y + 142, slant=-8.0, count=30, seed=3, veil=0.08) + turn)


def person(cx, cy, col, head="#E7C9A0"):
    return (f'<circle cx="{n(cx)}" cy="{n(cy - 26)}" r="12" fill="{head}" stroke="{INK}" stroke-width="1.6"/>'
            f'<path d="M{n(cx - 24)} {n(cy + 30)} Q{n(cx - 24)} {n(cy - 8)} {n(cx)} {n(cy - 10)} Q{n(cx + 24)} {n(cy - 8)} {n(cx + 24)} {n(cy + 30)} Z" fill="{col}" stroke="{INK}" stroke-width="1.6"/>')


def scene_4():                                               # the agreement before the first solo
    x, y = PX[3], PY[3]
    bubble = (f'<path d="M{n(x + 96)} {n(y + 20)} h112 a12 12 0 0 1 12 12 v38 a12 12 0 0 1 -12 12 h-58 l-14 16 l-4 -16 h-36 a12 12 0 0 1 -12 -12 v-38 a12 12 0 0 1 12 -12 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="2" filter="url(#{U}ds)"/>'
              + tick(x + 130, y + 52, 16.0)
              + f'<path d="M{n(x + 160)} {n(y + 52)} q16 -22 34 -8 M{n(x + 194)} {n(y + 44)} l-10 -2 M{n(x + 194)} {n(y + 44)} l-2 10" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    return frame(3, f'<defs><filter id="{U}ds" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="1.6" stdDeviation="1.6" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
                 + S.sky(f"{U}k3", x, y, PW, PH, [(0.0, "#EAF1FA"), (1.0, "#F6EFE0")]) + f'<rect x="{n(x)}" y="{n(y + 150)}" width="{n(PW)}" height="34" fill="#E3C27F" fill-opacity="0.55"/>'
                 + bubble + person(x + 92, y + 130, "#1D4ED8") + person(x + 212, y + 130, "#B45309", "#D9B38C")
                 + f'<path d="M{n(x + 128)} {n(y + 126)} L{n(x + 176)} {n(y + 126)}" stroke="{GREEN}" stroke-width="4" stroke-linecap="round" stroke-dasharray="2 8"/>')


def sprites():
    o = lambda x, y, w, angle=0.0, name="sprite-side": {"name": name, "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[0] + 150, PY[0] + 118, 52, 8.0), o(PX[0] + 232, PY[0] + 88, 52, -14.0),
            o(PX[1] + 170, PY[1] + 84, 46, 90.0, "sprite-top"),
            {"name": "cloud-cb", "at": [PX[2] + 250, PY[2] + 58], "width": 110, "height": 100}, o(PX[2] + 140, PY[2] + 118, 56, 0.0)]


def callouts():
    c = S.callout
    labels = ((PX[1] + 40, PY[1] + 118, "A"), (PX[1] + 262, PY[1] + 44, "B"), (PX[1] + 218, PY[1] + 150, "C"))
    pills = "".join(f'<circle cx="{n(lx)}" cy="{n(ly - 20)}" r="9.5" fill="#1F2937" stroke="#FFFFFF" stroke-width="1.4"/>' + H.glyph_text(t, lx, ly - 20 + 0.5, 9.0, fill="#FFFFFF") for lx, ly, t in labels)
    return pills + "".join(c(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-24-10-normal-options",
        "replaces": "fig-24-10-normal-options.svg",           # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-24-10-normal-options.jpg",
        "caption": "Figure 24-10. The normal options: go around, divert, turn back, and agree beforehand that they are good decisions",
        "desc": ("Figure 24-10. The normal options of a flight in four scenes: a go-around from an approach that is not stable; a diversion from the route A to B to the alternate C when B is below the minimums at the descent point; "
                 "a turn-back away from a storm ahead; and the agreement with the instructor before the first solo that a precautionary turn-back, diversion or go-around that costs time is a good decision."),
        "legend": [
            "A go-around is a normal manoeuvre for any approach that is not going as it should. It becomes dangerous only when delayed. Brief it before you need it: \"if the approach is not stable by the point my school specifies, I go around\".",
            "A diversion is the same decision on a larger scale: \"if B is below my minimums at the descent point, I go to C\".",
            "Turning back is easier where it is never criticised.",
            "Before your first solo, agree with your instructor that a precautionary turn-back, diversion or go-around that costs time is a good decision and will be debriefed as one.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
