"""Figure 21-9 (new). Traffic by the clock, from Chapter 21 ("Vectors and traffic information"): the controller sees your track, not your heading; correcting for a wind from the left, your nose
points left of the track, so traffic called at 12 o'clock appears at about 1 o'clock.

From above, on the open picture of the desert east of Thumamah (backdrop-plan-desert, figs/oeth3d.backdrop_plan): the aeroplane (sprite-top) crabbing into a wind from the left, its nose 22 degrees
left of its track (the angle is drawn large); its track, straight ahead, dashed blue; around it two clocks: the controller's, set on the track (blue, dashed), and the pilot's, set on the nose
(green); traffic ahead on the track, crossing left to right (the model, tinted orange), on the controller's 12 o'clock and between the pilot's 12 and 1 o'clock. Digits only; the words are in the
legend."""
import math

from figs import h_b2 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 330
U = "ns21t"
INK, BLUE, GREEN, AMBER = "#334155", "#1D4ED8", "#15803D", "#B45309"
PX, PY, PW, PH = 12.0, 12.0, 616.0, 306.0
CX, CY = 300.0, 228.0                                       # the aeroplane
CRAB = 22.0                                                 # degrees, nose left of the track (drawn large)
R_ATC, R_PILOT = 46.0, 64.0
TX, TY = CX, 60.0                                           # the traffic, ahead on the track
OUT = {"width": 0.6, "colour": "#1E293B", "opacity": 0.85}
SHADOW = {"dx": 2.0, "dy": 3.0, "blur": 2.2, "opacity": 0.35}


def pt(r, deg, cx=CX, cy=CY):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def clock(r, rot, col, dash, uid):
    """A clock round the aeroplane: a ring and the twelve hour ticks, 12 o'clock at `rot` degrees clockwise from up."""
    ring = (f'<circle cx="{n(CX)}" cy="{n(CY)}" r="{n(r)}" fill="none" stroke="#08101F" stroke-opacity="0.35" stroke-width="4.2"/>'
            f'<circle cx="{n(CX)}" cy="{n(CY)}" r="{n(r)}" fill="none" stroke="{col}" stroke-width="2.2"' + (' stroke-dasharray="5 4"' if dash else "") + '/>')
    ticks = ""
    for h in range(12):
        a = rot + h * 30
        (x0, y0), (x1, y1) = pt(r - (6 if h % 3 == 0 else 3.5), a), pt(r + (6 if h % 3 == 0 else 3.5), a)
        ticks += f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="{col}" stroke-width="{2.4 if h % 3 == 0 else 1.4}" stroke-linecap="round"/>'
    return ring + ticks


def background():
    uid = f"{U}bg"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(PH)}" rx="10"/></clipPath>'
            f'<filter id="{uid}s" x="-5%" y="-5%" width="110%" height="112%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(PH)}" rx="10" fill="#E8DCC4" filter="url(#{uid}s)"/>')


def overlay():
    out = []
    # the track: straight ahead, what the controller sees
    out.append(M.arrow(CX, CY - R_PILOT - 10, CX, TY + 34, BLUE, width=2.4, dash="7 5"))
    out.append(f'<line x1="{n(CX)}" y1="{n(CY + 30)}" x2="{n(CX)}" y2="{n(CY - R_PILOT - 10)}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5" stroke-opacity="0.8"/>')
    # the nose: the heading, 22 degrees left of the track
    hx, hy = pt(R_PILOT + 26, -CRAB)
    out.append(M.arrow(*pt(R_PILOT + 4, -CRAB), hx, hy, GREEN, width=2.4))
    # the two clocks
    out.append(clock(R_ATC, 0.0, BLUE, True, "a") + clock(R_PILOT, -CRAB, GREEN, False, "p"))
    # the hours: the controller's 12 on the track; the pilot's 12 on the nose and 1 o'clock 30 degrees right of it
    out.append(M.chip(*pt((R_ATC + R_PILOT) / 2, 15.0), "12", BLUE, size=8.6))
    out.append(M.chip(*pt(R_PILOT + 16, -CRAB - 9), "12", GREEN, size=8.6))
    out.append(M.chip(*pt(R_PILOT + 16, -CRAB + 30 + 6), "1", GREEN, size=8.6))
    # the wind, from the left
    out.append(S.ribbon(f"{U}w", [(PX + 40, CY + 52), (PX + 100, CY + 50), (PX + 160, CY + 46)], 9.0, "#4A86D8", "#A8CBF2", opacity=0.92, head=2.1, tail=0.5, per=8))
    c = S.callout
    out.append(c(1, CX - 34, TY + 52, CX - 2, TY + 58, r=10.5)
               + c(2, hx - 40, hy - 6, hx - 4, hy + 4, r=10.5)
               + c(3, PX + 60, CY + 82, PX + 92, CY + 56, r=10.5)
               + c(4, TX + 64, TY - 16, TX + 26, TY, r=10.5)
               + c(5, *pt(R_PILOT + 52, 42.0), *pt(R_PILOT + 2, -CRAB + 30), r=10.5))
    return "".join(out)


def frame():
    """White over what of the picture lies outside the panel (above, below, and the square corners outside the round ones), then the frame."""
    r, k = 10.0, 0.5523 * 10.0
    x0, y0, x1, y1 = PX, PY, PX + PW, PY + PH
    masks = (f'<rect x="0" y="0" width="{W}" height="{n(y0)}" fill="#ffffff"/><rect x="0" y="{n(y1)}" width="{W}" height="{n(HT - y1)}" fill="#ffffff"/>'
             f'<rect x="0" y="0" width="{n(x0)}" height="{HT}" fill="#ffffff"/><rect x="{n(x1)}" y="0" width="{n(W - x1)}" height="{HT}" fill="#ffffff"/>'
             + "".join(f'<path d="{d}" fill="#ffffff"/>' for d in (
                 f"M{n(x0)} {n(y0)} L{n(x0 + r)} {n(y0)} C{n(x0 + r - k)} {n(y0)} {n(x0)} {n(y0 + r - k)} {n(x0)} {n(y0 + r)} Z",
                 f"M{n(x1)} {n(y0)} L{n(x1)} {n(y0 + r)} C{n(x1)} {n(y0 + r - k)} {n(x1 - r + k)} {n(y0)} {n(x1 - r)} {n(y0)} Z",
                 f"M{n(x0)} {n(y1)} L{n(x0)} {n(y1 - r)} C{n(x0)} {n(y1 - r + k)} {n(x0 + r - k)} {n(y1)} {n(x0 + r)} {n(y1)} Z",
                 f"M{n(x1)} {n(y1)} L{n(x1 - r)} {n(y1)} C{n(x1 - r + k)} {n(y1)} {n(x1)} {n(y1 - r + k)} {n(x1)} {n(y1 - r)} Z")))
    return masks + f'<rect x="{n(PX)}" y="{n(PY)}" width="{n(PW)}" height="{n(PH)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'


def layers():
    ground = {"name": "backdrop-plan-desert", "at": [PX + PW / 2, PY + PH / 2], "width": PW, "whole": True}
    own = {"name": "sprite-top", "at": [CX, CY], "width": 64, "angle": -CRAB, "outline": OUT, "shadow": SHADOW}
    traffic = {"name": "sprite-top", "at": [TX, TY], "width": 40, "angle": 90, "tint": "#EA580C", "tint_strength": 0.55, "outline": OUT, "shadow": SHADOW}
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', background(), ground, frame(), own, traffic, overlay()]


def plate():
    return {
        "id": "fig-21-09-traffic-clock",
        "replaces": "fig-21-09-traffic-clock.svg",             # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-21-09-traffic-clock.jpg",
        "caption": "Figure 21-9. Traffic by the clock: the controller sees your track, you see past your nose",
        "desc": ("Figure 21-9. From above: the aeroplane crabbing into a wind from the left, its nose left of its track; the controller's clock set on the track and the pilot's clock set on the nose. "
                 "Traffic ahead on the track, called at 12 o'clock, appears at about 1 o'clock from the cockpit. The crab angle is drawn large."),
        "legend": [
            "The track: what the controller sees, and where the controller's 12 o'clock points.",
            "The heading: correcting for the wind, the nose points left of the track, and the pilot's clock turns with it.",
            "Wind from the left.",
            "Traffic called at 12 o'clock: ahead on the track.",
            "From the cockpit, the same traffic appears at about 1 o'clock.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
