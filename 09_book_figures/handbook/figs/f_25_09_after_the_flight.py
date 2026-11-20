"""Figure 25-9 (new). After the flight, from "Post-flight inspection and defects" and "The records" of Chapter 25: four scenes.

1 walk round again (the aeroplane on the ramp with five rings where the chapter says to look: oil or fuel streaks, tyres and brakes, blocked inlets, new propeller nicks or dents), 2 write every defect in the technical log and tell your instructor or maintenance
(a clipboard with a red mark and a tick, and a speech bubble crossed out: never by word of mouth alone), 3 the four records (the aircraft flight logbook, the pilot logbook, the instructor's entry and the technical log, as four books), 4 close the day
(complete the logbook the same day, close the flight plan, debrief with the instructor). Shapes, colours and the numbers of the callouts; no text. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar25a"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def tick(cx, cy, r=14.0, col=GREEN):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{col}" stroke="#FFFFFF" stroke-width="2"/>'
            f'<path d="M{n(cx - r * 0.5)} {n(cy + r * 0.05)} L{n(cx - r * 0.12)} {n(cy + r * 0.42)} L{n(cx + r * 0.55)} {n(cy - r * 0.38)}" fill="none" stroke="#FFFFFF" stroke-width="{n(r * 0.24)}" stroke-linecap="round" stroke-linejoin="round"/>')


def book(x, y, w, h, col, mark):
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="5" fill="{col}" stroke="#FFFFFF" stroke-width="1.8"/><rect x="{n(x)}" y="{n(y)}" width="10" height="{n(h)}" rx="5" fill="#000000" fill-opacity="0.22"/>'
            f'<rect x="{n(x + 20)}" y="{n(y + 14)}" width="{n(w - 32)}" height="{n(h * 0.34)}" rx="3" fill="#FFFFFF" fill-opacity="0.92"/>' + mark)


def scene1():
    x, y = PX[0], PY[0]
    uid = f"{U}s1"
    ring = lambda cx, cy, r=14: f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{r}" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="5 4"/>'
    body = (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/><g clip-path="url(#{uid}c)">'
            + S.sky(uid + "k", x, y, PW, PH, DAY) + S.plain(uid + "g", x, x + PW, y + 100, y + PH, seed=4, tone="day", acacias=((x + 28, y + 150, 0.9),), photo=True)
            + f'<rect x="{n(x)}" y="{n(y + 132)}" width="{n(PW)}" height="52" fill="#9AA3B2" fill-opacity="0.9"/></g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')
    return body


def rings():
    x, y = PX[0], PY[0]
    r = lambda cx, cy, rad=13: f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{rad}" fill="none" stroke="{RED}" stroke-width="3.2" stroke-dasharray="5 4"/>'
    return r(x + 252, y + 96, 15) + r(x + 218, y + 98, 12) + r(x + 233, y + 128, 11) + r(x + 156, y + 128, 11) + r(x + 66, y + 116, 11)


def scene2():
    x, y = PX[1], PY[1]
    clip = (f'<rect x="{n(x + 70)}" y="{n(y + 28)}" width="130" height="146" rx="10" fill="#C79A52" stroke="{INK}" stroke-width="2.4"/><rect x="{n(x + 82)}" y="{n(y + 44)}" width="106" height="120" rx="4" fill="#FFFFFF"/>'
            f'<rect x="{n(x + 110)}" y="{n(y + 20)}" width="50" height="18" rx="6" fill="#64748B" stroke="{INK}" stroke-width="2"/>')
    lines = "".join(f'<rect x="{n(x + 94)}" y="{n(y + 62 + k * 22)}" width="{n(68 if k % 2 == 0 else 54)}" height="5" rx="2" fill="#94A3B8"/><circle cx="{n(x + 178)}" cy="{n(y + 64 + k * 22)}" r="5" fill="{RED if k == 1 else GREEN}"/>' for k in range(5))
    bubble = (f'<path d="M{n(x + 214)} {n(y + 40)} h58 a10 10 0 0 1 10 10 v26 a10 10 0 0 1 -10 10 h-34 l-12 12 l-2 -12 h-10 a10 10 0 0 1 -10 -10 v-26 a10 10 0 0 1 10 -10 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>'
              f'<circle cx="{n(x + 248)}" cy="{n(y + 63)}" r="19" fill="none" stroke="{RED}" stroke-width="3.6"/><line x1="{n(x + 234)}" y1="{n(y + 77)}" x2="{n(x + 262)}" y2="{n(y + 49)}" stroke="{RED}" stroke-width="3.6" stroke-linecap="round"/>')
    return clip + lines + bubble + tick(x + 242, y + 140, 15.0)


def scene3():
    x, y = PX[2], PY[2]
    marks = (f'<path d="M{n(x + 50)} {n(y + 98)} l14 -8 l14 8 l-5 2 l-9 -4 l-9 4 Z" fill="#1E3A8A"/><circle cx="{n(x + 130)}" cy="{n(y + 90)}" r="8" fill="#1E40AF"/><path d="M{n(x + 118)} {n(y + 112)} q12 -16 24 0 Z" fill="#1E40AF"/>',
             f'<circle cx="{n(x + 210)}" cy="{n(y + 90)}" r="8" fill="#9A3412"/><path d="M{n(x + 198)} {n(y + 112)} q12 -16 24 0 Z" fill="#9A3412"/><circle cx="{n(x + 244)}" cy="{n(y + 108)}" r="9" fill="none" stroke="#9A3412" stroke-width="2.4"/>',
             f'<path d="M{n(x + 232)} {n(y + 82)} l22 22 M{n(x + 254)} {n(y + 82)} l-22 22" stroke="#92400E" stroke-width="5" stroke-linecap="round"/>')
    return (book(x + 22, y + 32, 112, 56, "#2563EB", "") + book(x + 168, y + 32, 112, 56, "#16A34A", "") + book(x + 22, y + 108, 112, 56, "#EA580C", "") + book(x + 168, y + 108, 112, 56, "#7C3AED", "")
            + f'<path d="M{n(x + 60)} {n(y + 66)} l14 -10 l14 10 l-5 2 l-9 -5 l-9 5 Z" fill="#1E3A8A"/><circle cx="{n(x + 224)}" cy="{n(y + 58)}" r="7" fill="#166534"/><path d="M{n(x + 212)} {n(y + 76)} q12 -14 24 0 Z" fill="#166534"/>'
            f'<circle cx="{n(x + 78)}" cy="{n(y + 134)}" r="7" fill="#9A3412"/><path d="M{n(x + 66)} {n(y + 152)} q12 -14 24 0 Z" fill="#9A3412"/><path d="M{n(x + 214)} {n(y + 132)} l22 22 M{n(x + 236)} {n(y + 132)} l-22 22" stroke="#4C1D95" stroke-width="5" stroke-linecap="round"/>')


def scene4():
    x, y = PX[3], PY[3]
    clock = (f'<circle cx="{n(x + 60)}" cy="{n(y + 66)}" r="30" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/><line x1="{n(x + 60)}" y1="{n(y + 66)}" x2="{n(x + 60)}" y2="{n(y + 46)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><line x1="{n(x + 60)}" y1="{n(y + 66)}" x2="{n(x + 76)}" y2="{n(y + 74)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    plan = (f'<rect x="{n(x + 130)}" y="{n(y + 36)}" width="56" height="70" rx="5" fill="#FFFFFF" stroke="{INK}" stroke-width="2.2"/>' + "".join(f'<rect x="{n(x + 140)}" y="{n(y + 48 + k * 14)}" width="{n(36 if k != 2 else 24)}" height="5" rx="2" fill="#94A3B8"/>' for k in range(4)) + tick(x + 186, y + 100, 13.0))
    talk = "".join(f'<path d="M{n(bx)} {n(by)} h50 a9 9 0 0 1 9 9 v20 a9 9 0 0 1 -9 9 h-30 l-10 10 l-2 -10 h-8 a9 9 0 0 1 -9 -9 v-20 a9 9 0 0 1 9 -9 Z" fill="{col}" stroke="#FFFFFF" stroke-width="1.8"/>' for bx, by, col in ((x + 74, y + 122, "#16A34A"), (x + 176, y + 126, "#2563EB")))
    return clock + plan + talk + tick(x + 262, y + 60, 15.0)


def tiles():
    return (scene1() + R.tile(f"{U}t2", PX[1], PY[1], PW, PH, "sand") + scene2() + R.tile(f"{U}t3", PX[2], PY[2], PW, PH, "slate") + scene3() + R.tile(f"{U}t4", PX[3], PY[3], PW, PH, "green") + scene4())


def sprites():
    return [{"name": "sprite-side", "at": [PX[0] + 152, PY[0] + 104], "width": 190, "outline": OUT, "shadow": SHADOW}]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', tiles(), *sprites(), rings(), callouts()]


def plate():
    return {
        "id": "fig-25-09-after-the-flight",
        "replaces": "fig-25-09-after-the-flight.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-25-09-after-the-flight.jpg",
        "caption": "Figure 25-9. After the flight: walk round again, write every defect, keep the four records, and close the day",
        "desc": ("Figure 25-9. After the flight in four scenes: the post-flight walk-round with the places to look ringed (streaks, tyres and brakes, inlets, propeller nicks); every defect written in the technical log and not passed on by word of mouth alone; "
                 "the four records (aircraft flight logbook, pilot logbook, instructor's entry, technical log); and the day closed with the logbook completed, the flight plan closed and a debrief."),
        "legend": [
            "Walk round again: oil or fuel streaks, fuel stains, tyres and brakes, blocked inlets, new propeller nicks or dents. Check the oil and refuel as your school directs.",
            "Write every defect in the technical log as your school requires, and tell your instructor or maintenance; never pass one on by word of mouth alone. An unairworthy aeroplane may not be operated.",
            "The records: the aircraft flight logbook, the pilot logbook, the instructor's entry and the technical log.",
            "Complete your logbook the same day, close any flight plan, and debrief with your instructor.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
