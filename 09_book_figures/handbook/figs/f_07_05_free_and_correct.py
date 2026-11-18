"""Figure 7-5 (new). Control locks and the free-and-correct check of Chapter 7 ("Control locks"): four tiles.

1 the lock (a pin through the control column, with a red flag, and the green tick of the control that moves freely once every lock is removed), 2 the ailerons (the wheel turned to the right; the right aileron rises and the left aileron falls,
drawn as two wing sections seen from the side), 3 the elevator (the column pulled back; the elevator rises, a tail section seen from the side), 4 the rudder (the right pedal pushed; the rudder follows the pedal, a fin seen from above).
The statements are those of the chapter's warning: the correct aileron rises, the elevator rises when you pull, the rudder follows the pedal you push. Shapes, colours and the numbers of the callouts; no text. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar07f"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
TONES = ("red", "blue", "sand", "green")


def yoke(cx, cy, rot=0.0, pull=0.0, s=1.0):
    r = 24 * s
    return (f'<g transform="translate({n(cx)} {n(cy)}) rotate({n(rot)})"><rect x="{n(-5 * s)}" y="{n(8 * s)}" width="{n(10 * s)}" height="{n(46 * s)}" rx="3" fill="#94A3B8" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{n(-r)} {n(-4 * s)} Q{n(-r)} {n(-r)} {n(-r * 0.5)} {n(-r)} L{n(r * 0.5)} {n(-r)} Q{n(r)} {n(-r)} {n(r)} {n(-4 * s)}" fill="none" stroke="{INK}" stroke-width="{n(7 * s)}" stroke-linecap="round"/>'
            f'<path d="M{n(-r)} {n(-4 * s)} Q{n(-r)} {n(-r)} {n(-r * 0.5)} {n(-r)} L{n(r * 0.5)} {n(-r)} Q{n(r)} {n(-r)} {n(r)} {n(-4 * s)}" fill="none" stroke="#64748B" stroke-width="{n(4 * s)}" stroke-linecap="round"/>'
            f'<rect x="{n(-8 * s)}" y="{n(-6 * s)}" width="{n(16 * s)}" height="{n(14 * s)}" rx="4" fill="#475569" stroke="{INK}" stroke-width="1.6"/></g>')


def section(cx, cy, w=70.0, flap=0.0, col="#E2E8F0"):
    """A wing or tail section from the side, leading edge left: the body and a hinged trailing-edge flap turned by `flap` degrees (negative is up)."""
    body = f'<path d="M{n(cx - w / 2)} {n(cy)} Q{n(cx - w / 2 + 6)} {n(cy - 12)} {n(cx - w * 0.1)} {n(cy - 11)} L{n(cx + w * 0.18)} {n(cy - 4)} L{n(cx + w * 0.18)} {n(cy + 4)} L{n(cx - w * 0.1)} {n(cy + 6)} Q{n(cx - w / 2 + 6)} {n(cy + 7)} {n(cx - w / 2)} {n(cy)} Z" fill="{col}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
    fl = f'<g transform="rotate({n(flap)} {n(cx + w * 0.18)} {n(cy)})"><path d="M{n(cx + w * 0.18)} {n(cy - 4)} L{n(cx + w / 2)} {n(cy - 0.5)} L{n(cx + w / 2)} {n(cy + 1.5)} L{n(cx + w * 0.18)} {n(cy + 4)} Z" fill="#FDBA74" stroke="#9A3412" stroke-width="2" stroke-linejoin="round"/></g>'
    return body + fl


def vslide(cx, cy, dy, col=GREEN):
    return S.ribbon(f"{U}v{int(cx)}{int(cy)}", [(cx, cy), (cx, cy + dy * 0.4), (cx, cy + dy * 0.8), (cx, cy + dy)], 4.6, "#2FA35A" if col == GREEN else "#E8782E", "#9BE0B2" if col == GREEN else "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=6)


def tick(cx, cy, r=15.0):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{GREEN}" stroke="#FFFFFF" stroke-width="2"/>'
            f'<path d="M{n(cx - r * 0.5)} {n(cy + r * 0.05)} L{n(cx - r * 0.12)} {n(cy + r * 0.42)} L{n(cx + r * 0.55)} {n(cy - r * 0.38)}" fill="none" stroke="#FFFFFF" stroke-width="{n(r * 0.24)}" stroke-linecap="round" stroke-linejoin="round"/>')


def tile0():                                                  # the lock and the free check
    x, y = PX[0], PY[0]
    cx, cy = x + 90, y + 88
    lock = (f'<rect x="{n(cx - 40)}" y="{n(cy + 26)}" width="80" height="8" rx="3" fill="#EA580C" stroke="#9A3412" stroke-width="1.8"/><circle cx="{n(cx)}" cy="{n(cy + 30)}" r="9" fill="none" stroke="{INK}" stroke-width="2.6"/>'
            f'<path d="M{n(cx + 40)} {n(cy + 30)} L{n(cx + 70)} {n(cy + 22)} L{n(cx + 70)} {n(cy + 44)} Z" fill="{RED}" stroke="#7F1D1D" stroke-width="1.4"/>')
    return yoke(cx, cy, 0, 0, 1.15) + lock + tick(x + 238, y + 62, 17.0)


DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def scene(i, body, seed, top=False):
    x, y = PX[i], PY[i]
    uid = f"{U}s{i}"
    bg = (f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="#E3C27F"/><rect x="{n(x + 18)}" y="{n(y + 14)}" width="{n(PW - 36)}" height="{n(PH - 28)}" rx="6" fill="#9AA3B2"/>' if top
          else S.sky(uid + "k", x, y, PW, PH, DAY) + S.plain(uid + "g", x, x + PW, y + 112, y + PH, seed=seed, tone="day"))
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/><g clip-path="url(#{uid}c)">' + bg + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def inset(i, content):
    x, y = PX[i], PY[i]
    return f'<rect x="{n(x + 14)}" y="{n(y + 44)}" width="70" height="80" rx="9" fill="#FFFFFF" fill-opacity="0.92" stroke="{INK}" stroke-width="1.6"/>' + content


def tile1():                                                  # ailerons: right wheel, right aileron up, left aileron down
    x, y = PX[1], PY[1]
    return scene(1, inset(1, yoke(x + 49, y + 92, 28.0, 0, 0.62) + S.ribbon(f"{U}a1", [(x + 28, y + 62), (x + 40, y + 54), (x + 58, y + 54), (x + 70, y + 62)], 3.2, "#E8782E", "#F6B36B", opacity=0.9, head=2.0, tail=0.4, per=8))
                 + vslide(x + 262, y + 72, -26.0) + vslide(x + 146, y + 100, 26.0, "o"), 6)


def tile2():                                                  # elevator: column pulled back, elevator up
    x, y = PX[2], PY[2]
    return scene(2, inset(2, yoke(x + 49, y + 88, 0, 0, 0.7) + S.ribbon(f"{U}e2", [(x + 49, y + 124), (x + 53, y + 116), (x + 57, y + 108), (x + 57, y + 98)], 3.4, "#E8782E", "#F6B36B", opacity=0.9, head=2.0, tail=0.4, per=8))
                 + vslide(x + 170, y + 78, -28.0), 9)


def tile3():                                                  # rudder: right pedal pushed, the rudder follows
    x, y = PX[3], PY[3]
    pedals = (f'<rect x="{n(x + 24)}" y="{n(y + 96)}" width="16" height="24" rx="4" fill="#94A3B8" stroke="{INK}" stroke-width="1.6"/><rect x="{n(x + 46)}" y="{n(y + 84)}" width="16" height="24" rx="4" fill="#E2E8F0" stroke="{INK}" stroke-width="1.6"/>'
              + S.ribbon(f"{U}p3", [(x + 54, y + 126), (x + 54, y + 120), (x + 54, y + 112), (x + 54, y + 102)], 3.2, "#E8782E", "#F6B36B", opacity=0.9, head=2.0, tail=0.4, per=6))
    return scene(3, inset(3, pedals) + S.ribbon(f"{U}r3", [(x + 124, y + 84), (x + 126, y + 100), (x + 130, y + 118), (x + 136, y + 130)], 5.0, "#2FA35A", "#9BE0B2", opacity=0.92, head=2.2, tail=0.4, per=8), 12, top=True)


def sprites():
    o = lambda x, y, w, angle=0.0, name="sprite-side": {"name": name, "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[0] + 238, PY[0] + 112, 80), o(PX[1] + 204, PY[1] + 96, 120, 0.0, "sprite-rear"), o(PX[2] + 190, PY[2] + 100, 110), o(PX[3] + 180, PY[3] + 92, 120, 90.0, "sprite-top")]


def tiles():
    return R.tile(f"{U}t0", PX[0], PY[0], PW, PH, "red") + tile0() + tile1() + tile2() + tile3()


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', tiles(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-07-05-free-and-correct",
        "replaces": "fig-07-05-free-and-correct.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-07-05-free-and-correct.jpg",
        "caption": "Figure 7-5. Control locks, then free and correct: ailerons, elevator and rudder move the right way",
        "desc": ("Figure 7-5. The control lock and the free-and-correct check in four tiles: a lock pin through the control column with its red flag, removed before flight; the wheel turned to the right and the correct aileron rising; "
                 "the column pulled back and the elevator rising; and the right pedal pushed and the rudder following it."),
        "legend": [
            "A control lock, a pin through the control column or a clamp on the surfaces, stops a free surface from being slammed against its stops in wind. Removing every lock is a checklist item, followed by a check that the controls are free and correct.",
            "Ailerons: move the control wheel fully in each direction and watch outside; the correct aileron rises (here, to the right, the right aileron rises).",
            "Elevator: the elevator rises when you pull.",
            "Rudder: the rudder follows the pedal you push. Stiffness, noise or limited travel: stop and call maintenance.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
