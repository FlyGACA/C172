"""Figure 8-7 (new). Propeller safety on the ground, from the last section of Chapter 8: four scenes, one for each of its first four points.

Drawn in the style of the other illustrated figures (figs/scene.py: sky, plain, ribbons; the aeroplane sprites laid by reskin.py): 1 a stopped propeller may be live (the aeroplane's nose, the propeller, an ignition key and a red spark),
2 before start the area around and behind is clear (the aeroplane seen from above on the apron, a green clear zone round it and a hand on the throttle), 3 never approach a running propeller from the front or the side (the red zones
ahead and abeam of the disc, the green zone behind), 4 the propeller blast throws sand and stones backward (ribbons and stones behind the aeroplane). Shapes, colours and the numbers of the callouts. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import photo_ground as PG
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar08p"
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


def side_panel(i, seed, extra=""):
    x, y = PX[i], PY[i]
    return frame(i, S.sky(f"{U}k{i}", x, y, PW, PH, DAY) + S.plain(f"{U}g{i}", x, x + PW, y + 100, y + PH, seed=seed, tone="day", acacias=((x + 30, y + 150, 0.9),), photo=True) + extra)


def apron_panel(i, extra=""):
    x, y = PX[i], PY[i]
    apron = (PG.plan(x, y, PW, PH, zoom=1.5, cx=0.3, cy=0.6) + f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="#FFF8EC" fill-opacity="0.3"/>'
             f'<rect x="{n(x + 18)}" y="{n(y + 14)}" width="{n(PW - 36)}" height="{n(PH - 28)}" rx="6" fill="#9AA3B2"/>'
             f'<line x1="{n(x + 18)}" y1="{n(y + PH / 2)}" x2="{n(x + PW - 18)}" y2="{n(y + PH / 2)}" stroke="#F1F5F9" stroke-width="2" stroke-dasharray="12 9" stroke-opacity="0.7"/>')
    return frame(i, apron + extra)


def key(cx, cy):
    return (f'<rect x="{n(cx - 3.5)}" y="{n(cy + 4)}" width="7" height="30" rx="2" fill="#94A3B8" stroke="{INK}" stroke-width="1.6"/>'
            f'<rect x="{n(cx + 3.5)}" y="{n(cy + 20)}" width="8" height="4" fill="#94A3B8" stroke="{INK}" stroke-width="1.2"/><rect x="{n(cx + 3.5)}" y="{n(cy + 28)}" width="6" height="4" fill="#94A3B8" stroke="{INK}" stroke-width="1.2"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="16" fill="#E2E8F0" stroke="{INK}" stroke-width="2.4"/><circle cx="{n(cx)}" cy="{n(cy)}" r="5.5" fill="{INK}"/>'
            f'<rect x="{n(cx - 20)}" y="{n(cy - 46)}" width="40" height="20" rx="10" fill="#1F2937" stroke="#FFFFFF" stroke-width="1.4"/>' + H.glyph_text("OFF", cx, cy - 36, 10.0, fill="#FFFFFF"))


def spark(cx, cy, r=14.0):
    pts = []
    for k in range(10):
        a = math.radians(k * 36 - 90)
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return f'<polygon points="{S.pts(pts)}" fill="#FACC15" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>'


def scene_1():
    x, y = PX[0], PY[0]
    return side_panel(0, 4, f'<circle cx="{n(x + 200)}" cy="{n(y + 98)}" r="30" fill="none" stroke="{RED}" stroke-width="3.2" stroke-dasharray="6 5"/>' + key(x + 252, y + 70) + spark(x + 205, y + 98))


def scene_2():
    x, y = PX[1], PY[1]
    cx, cy = x + PW / 2 - 4, y + PH / 2
    zone = f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="140" ry="76" fill="#2FA35A" fill-opacity="0.22" stroke="{GREEN}" stroke-width="3" stroke-dasharray="9 6"/>'
    return apron_panel(1, zone)


def scene_3():
    x, y = PX[2], PY[2]
    cx, cy = x + 190, y + PH / 2
    red = (f'<path d="M{n(cx)} {n(cy)} L{n(cx + 90)} {n(cy - 56)} A106 106 0 0 1 {n(cx + 90)} {n(cy + 56)} Z" fill="{RED}" fill-opacity="0.32"/>'
           f'<path d="M{n(cx)} {n(cy)} L{n(cx - 22)} {n(cy - 78)} L{n(cx + 40)} {n(cy - 78)} Z" fill="{RED}" fill-opacity="0.26"/><path d="M{n(cx)} {n(cy)} L{n(cx - 22)} {n(cy + 78)} L{n(cx + 40)} {n(cy + 78)} Z" fill="{RED}" fill-opacity="0.26"/>')
    green = f'<path d="M{n(cx - 20)} {n(cy - 20)} L{n(x + 28)} {n(cy - 30)} L{n(x + 28)} {n(cy + 30)} L{n(cx - 20)} {n(cy + 20)} Z" fill="#2FA35A" fill-opacity="0.34" stroke="{GREEN}" stroke-width="2.2" stroke-dasharray="7 5"/>'
    return apron_panel(2, red + green)


def scene_4():
    x, y = PX[3], PY[3]
    blast = "".join(S.ribbon(f"{U}b{k}", [(x + 150, y + yy), (x + 110, y + yy - 4), (x + 70, y + yy + 3), (x + 30, y + yy - 2)], 6.0, "#7C8FB5", "#C7D2E8", opacity=0.7, head=2.0, tail=0.5, per=8) for k, yy in enumerate((90, 112, 132)))
    stones = "".join(f'<ellipse cx="{n(x + sx)}" cy="{n(y + sy)}" rx="{r}" ry="{r * 0.7}" fill="#6B5B45" stroke="#FFFFFF" stroke-width="0.8"/>' for sx, sy, r in ((70, 100, 3.4), (46, 122, 2.8), (98, 128, 3.0), (30, 96, 2.4), (60, 140, 2.6)))
    dust = S.fog(f"{U}d4", x, x + 170, y + 150, 60, seed=4, opacity=0.8, colour="#E2C48C", wisp=1.1, foot=0.3, side_fade=0.3)
    return side_panel(3, 12, dust + blast + stones)


def sprites():
    o = lambda x, y, w, name="sprite-side", angle=0.0: {"name": name, "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[0] + 150, PY[0] + 96, 130), o(PX[1] + PW / 2 - 4, PY[1] + PH / 2, 120, "sprite-top", 90.0), o(PX[2] + 170, PY[2] + PH / 2, 120, "sprite-top", 90.0), o(PX[3] + 215, PY[3] + 100, 110)]


def hand():
    x, y = PX[1], PY[1]
    return (f'<rect x="{n(x + 40)}" y="{n(y + 22)}" width="50" height="22" rx="11" fill="#1F2937" stroke="#FFFFFF" stroke-width="1.4"/>' + H.glyph_text("CLEAR", x + 65, y + 33.5, 10.0, fill="#FFFFFF"))


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), *sprites(), hand(), callouts()]


def plate():
    return {
        "id": "fig-08-07-propeller-safety",
        "replaces": "fig-08-07-propeller-safety.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-08-07-propeller-safety.jpg",
        "caption": "Figure 8-7. Propeller safety on the ground: treat a stopped propeller as live, clear the area, never approach from the front or side, mind the blast",
        "desc": ("Figure 8-7. Propeller safety on the ground, four scenes: a stopped propeller may be live with the ignition key off; the area around and behind the aeroplane is cleared and CLEAR is called before start; "
                 "a running propeller is never approached from the front or the side; the propeller blast throws sand and stones backward."),
        "legend": [
            "A turning propeller is almost invisible. Whenever you touch a stopped one, assume the ignition is on: a magneto can be live with the switch OFF if its ground wire is broken, and moving the propeller can then start the engine.",
            "Before start, check that the area around and behind the aeroplane is clear, call \"CLEAR\" and wait, then hold the brakes with a hand on the throttle.",
            "Never approach a running propeller from the front or side; remove chocks from behind it, at idle, or with the engine stopped.",
            "Propeller blast throws sand and stones backward. Start and run up clear of people, aircraft and loose surfaces.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
