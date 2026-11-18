"""Figure 30-5 (new). A precautionary landing in four steps, from the section of Chapter 30 that follows the forced landing.

Four scenes of the same country of the Peninsula, in the style of the weather figures (figs/scene.py: sky, plain, scrub, acacias, dust, ribbons; the aeroplane and the cloud sprites laid
by reskin.py): 1 decide early (dust on the horizon, the sun low, a fuel gauge near empty), 2 choose the field (a flat firm plain beside a road, the radio call to ATC), 3 inspect it from a safe
height along the landing direction (poles and wires, a slope, animals), 4 land with the short-field technique at 60 kt and report the arrival. Shapes, colours and the numbers of the callouts;
the only digits are the 60 of the final approach speed of the example aeroplane (Chapter 26). The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar30p"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
HZ = 64.0                                                    # the horizon, from the top of a panel


def panel(i, sky_stops, body):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, PW, PH, sky_stops) + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def ground(i, tone="day", seed=3, **kw):
    x, y = PX[i], PY[i]
    return S.plain(f"{U}g{i}", x, x + PW, y + HZ, y + PH, seed=seed, tone=tone, **kw)


def dusk_sun(i, cx, cy, r=9.0):
    return S.glow(f"{U}sg{i}", cx, cy, r * 4.4, "#FFE3A8", 0.9) + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#FFF3CF"/>'


def gauge(cx, cy, r=21.0):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#FFFFFF" stroke="{INK}" stroke-width="2.4"/>'
            f'<path d="M{n(cx - r * 0.84)} {n(cy)} A{n(r * 0.84)} {n(r * 0.84)} 0 0 1 {n(cx - r * 0.42)} {n(cy - r * 0.73)}" fill="none" stroke="{RED}" stroke-width="4.6" stroke-linecap="round"/>'
            f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx - r * 0.66)}" y2="{n(cy - r * 0.36)}" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/><circle cx="{n(cx)}" cy="{n(cy)}" r="3" fill="{INK}"/>')


def waves(cx, cy, ang, col=BLUE, k=3):
    o = []
    for j in range(k):
        r = 9 + j * 7
        a0, a1 = math.radians(ang - 36), math.radians(ang + 36)
        o.append(f'<path d="M{n(cx + r * math.cos(a0))} {n(cy + r * math.sin(a0))} A{n(r)} {n(r)} 0 0 1 {n(cx + r * math.cos(a1))} {n(cy + r * math.sin(a1))}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-opacity="0.85"/>'
                 f'<path d="M{n(cx + r * math.cos(a0))} {n(cy + r * math.sin(a0))} A{n(r)} {n(r)} 0 0 1 {n(cx + r * math.cos(a1))} {n(cy + r * math.sin(a1))}" fill="none" stroke="{col}" stroke-width="2.8" stroke-linecap="round"/>')
    return "".join(o)


def scene_1():                                               # decide early: dusk, dust on the horizon, the gauge
    x, y = PX[0], PY[0]
    dust = (S.fog(f"{U}d1", x, x + PW, y + HZ + 22, 78, seed=5, opacity=0.95, colour="#D6B77C", wisp=1.0, foot=0.3, side_fade=0.22)
            + S.fog(f"{U}d2", x + 90, x + PW + 20, y + HZ + 30, 64, seed=11, opacity=0.9, colour="#C99F5E", wisp=1.1, foot=0.3, side_fade=0.3))
    return panel(0, [(0.0, "#4F6FB0"), (0.45, "#B3A3B4"), (0.75, "#F3C48E"), (1.0, "#F6D8A8")],
                 dusk_sun(0, x + 70, y + HZ - 6, 8.5) + ground(0, "dusk", 3, acacias=((x + 40, y + 120, 1.0), (x + 210, y + 138, 1.2)), houses=((x + 252, y + HZ + 12, 0.8),)) + dust
                 + gauge(x + 252, y + 40, 22.0))


def scene_2():                                               # choose the field: firm, flat, a road beside it; the call to ATC
    x, y = PX[1], PY[1]
    fy = y + 112
    field = (f'<path d="M{n(x + 70)} {n(fy)} L{n(x + 230)} {n(fy)} L{n(x + 262)} {n(fy + 52)} L{n(x + 38)} {n(fy + 52)} Z" fill="#B9A672" stroke="{GREEN}" stroke-width="2.6" stroke-dasharray="7 5" stroke-linejoin="round"/>'
             f'<path d="M{n(x + 238)} {n(fy)} L{n(x + 258)} {n(fy)} L{n(x + 304)} {n(fy + 52)} L{n(x + 276)} {n(fy + 52)} Z" fill="#64748B"/>'
             f'<line x1="{n(x + 248)}" y1="{n(fy + 2)}" x2="{n(x + 290)}" y2="{n(fy + 50)}" stroke="#E2E8F0" stroke-width="1.6" stroke-dasharray="6 5"/>')
    return panel(1, [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")],
                 ground(1, "day", 6, acacias=((x + 22, y + 96, 0.9), (x + 288, y + 90, 0.8)), houses=((x + 270, y + HZ + 10, 0.7),)) + field
                 + S.ribbon(f"{U}r2", [(x + 70, y + 100), (x + 110, y + 106), (x + 150, y + 118), (x + 150, y + 138)], 6.2, "#2FA35A", "#9BE0B2", opacity=0.92, head=2.1, tail=0.4, per=8)
                 + waves(x + 106, y + 40, 30.0, BLUE, 3))


def scene_3():                                               # inspect: poles and wires, a slope, animals, the low pass
    x, y = PX[2], PY[2]
    gy = y + 130
    poles = ""
    for px in (x + 58, x + 244):
        poles += f'<line x1="{n(px)}" y1="{n(gy)}" x2="{n(px)}" y2="{n(y + 60)}" stroke="#44403C" stroke-width="3.2"/><line x1="{n(px - 11)}" y1="{n(y + 66)}" x2="{n(px + 11)}" y2="{n(y + 66)}" stroke="#44403C" stroke-width="3"/>'
    wire = f'<path d="M{n(x + 58)} {n(y + 66)} Q{n(x + 151)} {n(y + 88)} {n(x + 244)} {n(y + 66)}" fill="none" stroke="{RED}" stroke-width="2.4"/>'
    animals = "".join(f'<ellipse cx="{n(ax)}" cy="{n(gy + 14)}" rx="8" ry="4.6" fill="#78552B" stroke="#FFFFFF" stroke-width="1"/><line x1="{n(ax - 4)}" y1="{n(gy + 17)}" x2="{n(ax - 4)}" y2="{n(gy + 24)}" stroke="#78552B" stroke-width="2"/><line x1="{n(ax + 4)}" y1="{n(gy + 17)}" x2="{n(ax + 4)}" y2="{n(gy + 24)}" stroke="#78552B" stroke-width="2"/><path d="M{n(ax + 7)} {n(gy + 12)} q4 -6 5 -9" fill="none" stroke="#78552B" stroke-width="2.2" stroke-linecap="round"/>' for ax in (x + 150, x + 172))
    return panel(2, [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")],
                 ground(2, "day", 9, acacias=((x + 28, y + 110, 1.1), (x + 276, y + 102, 1.0))) + poles + wire + animals
                 + S.ribbon(f"{U}r3", [(x + 24, y + 130), (x + 90, y + 126), (x + 170, y + 122), (x + 276, y + 112)], 5.0, "#2FA35A", "#9BE0B2", opacity=0.85, head=2.0, tail=0.4, per=8))


def scene_4():                                               # land and report: the short-field final at 60 kt
    x, y = PX[3], PY[3]
    strip = f'<path d="M{n(x)} {n(y + 140)} L{n(x + PW)} {n(y + 140)} L{n(x + PW)} {n(y + 160)} L{n(x)} {n(y + 160)} Z" fill="#CDB98A" fill-opacity="0.9"/>'
    return panel(3, [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")],
                 ground(3, "day", 12, acacias=((x + 270, y + 104, 0.9),), houses=((x + 232, y + HZ + 10, 0.7),)) + strip
                 + S.ribbon(f"{U}r4", [(x + 18, y + 70), (x + 80, y + 92), (x + 150, y + 118), (x + 196, y + 142)], 5.6, "#E8782E", "#F6B36B", opacity=0.9, head=2.1, tail=0.4, per=8)
                 + f'<rect x="{n(x + 238)}" y="{n(y + 16)}" width="50" height="26" rx="13" fill="#1F2937" stroke="#FFFFFF" stroke-width="1.6"/>' + H.glyph_text("60", x + 263, y + 29, 15.0, fill="#FFFFFF")
                 + waves(x + 262, y + 168, -125.0, GREEN, 3))


def sprites():
    out = [{"name": "cloud-cumulus-b", "at": [PX[1] + 236, PY[1] + 30], "width": 70, "height": 22}, {"name": "cloud-cumulus-b", "at": [PX[2] + 60, PY[2] + 24], "width": 64, "height": 20},
           {"name": "cloud-cumulus-a", "at": [PX[3] + 70, PY[3] + 30], "width": 60, "height": 20}]
    out.append({"name": "sprite-side", "at": [PX[0] + 120, PY[0] + 46], "width": 50, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}, "shadow": {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}})
    out.append({"name": "sprite-side", "at": [PX[1] + 70, PY[1] + 46], "width": 54, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}, "shadow": {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}})
    out.append({"name": "sprite-side", "at": [PX[2] + 150, PY[2] + 100], "width": 58, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}, "shadow": {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}})
    out.append({"name": "sprite-side", "at": [PX[3] + 150, PY[3] + 120], "width": 64, "angle": 10.0, "outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}, "shadow": {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}})
    return out


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-30-05-precautionary-landing",
        "replaces": "fig-30-05-precautionary-landing.svg",   # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-30-05-precautionary-landing.jpg",
        "caption": "Figure 30-5. A precautionary landing in four steps: decide early, choose the field, inspect it from above, land and report",
        "desc": ("Figure 30-5. A precautionary landing in four scenes: dust ahead, a low sun and a low fuel gauge decide the landing early; the field is chosen beside a road and ATC is told; "
                 "the field is flown over along the landing direction to check surface, slope, wires and animals; the landing is made with the short-field technique at 60 kt and the arrival is reported."),
        "legend": [
            "Decide early, while you still have fuel, light and power (dust ahead, a low sun or a falling fuel quantity), and tell ATC.",
            "Choose the field as for a forced landing: a long, firm, flat surface near a road, with the wind and the sun in mind.",
            "Fly over it along the landing direction at a safe height, within §91.67 and your school's procedures, to check the surface, the slope, wires and animals.",
            "Land with the short-field or soft-field technique of Chapter 26 (60 kt on final, full flap, in the example aeroplane), report the arrival to the nearest ATS unit and do not take off again until your school agrees.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
