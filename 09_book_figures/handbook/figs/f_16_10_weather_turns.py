"""Figure 16-10 (new). When the weather turns in flight, from the last section of Chapter 16: four scenes.

Drawn in the style of the other illustrated figures (figs/scene.py: sky, plain, fog, ribbons; the aeroplane sprites laid by reskin.py): 1 turn back while the visibility is still good (a dust wall ahead, clear air behind, the turn),
2 a dust storm can cover several aerodromes at once (three runways in plan under one band of dust; the chapter's "about 500 km wide" of April 2018), 3 a controlled VFR flight that cannot stay in VMC (a control zone in plan and the three
ways of the rule: an amended clearance to continue in VMC, leaving the airspace, or landing at the nearest suitable aerodrome), 4 report a heavy dust storm or sandstorm (the radio call from the aeroplane to the tower). Shapes, colours and the numbers
of the callouts; the only text is 500 KM. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar16w"
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


def side(i, seed, hz=100.0, extra=""):
    x, y = PX[i], PY[i]
    return frame(i, S.sky(f"{U}k{i}", x, y, PW, PH, DAY) + S.plain(f"{U}g{i}", x, x + PW, y + hz, y + PH, seed=seed, tone="day", acacias=((x + 30, y + 156, 0.9),)) + extra)


def plan(i, extra=""):
    x, y = PX[i], PY[i]
    return frame(i, f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="#E8D7AC"/>' + extra)


def strip(x, y, w=48.0, angle=0.0):
    return (f'<g transform="rotate({n(angle)} {n(x + w / 2)} {n(y + 5)})"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="10" rx="2" fill="#5B6577"/>'
            f'<line x1="{n(x + 4)}" y1="{n(y + 5)}" x2="{n(x + w - 4)}" y2="{n(y + 5)}" stroke="#F1F5F9" stroke-width="1.2" stroke-dasharray="6 4"/></g>')


def tower(cx, cy, s=1.0):
    return (f'<rect x="{n(cx - 4 * s)}" y="{n(cy - 6 * s)}" width="{n(8 * s)}" height="{n(26 * s)}" fill="#94A3B8" stroke="{INK}" stroke-width="1.6"/>'
            f'<rect x="{n(cx - 12 * s)}" y="{n(cy - 18 * s)}" width="{n(24 * s)}" height="{n(14 * s)}" rx="3" fill="#BFDBFE" stroke="{INK}" stroke-width="1.8"/>')


def waves(cx, cy, ang, col=BLUE, k=3):
    o = []
    for j in range(k):
        r = 9 + j * 7
        a0, a1 = math.radians(ang - 34), math.radians(ang + 34)
        d = f"M{n(cx + r * math.cos(a0))} {n(cy + r * math.sin(a0))} A{n(r)} {n(r)} 0 0 1 {n(cx + r * math.cos(a1))} {n(cy + r * math.sin(a1))}"
        o.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-opacity="0.85"/><path d="{d}" fill="none" stroke="{col}" stroke-width="2.8" stroke-linecap="round"/>')
    return "".join(o)


def scene_1():                                               # turn back while the visibility is good
    x, y = PX[0], PY[0]
    dust = (S.fog(f"{U}d1", x + 150, x + PW + 20, y + 146, 120, seed=5, opacity=1.0, colour="#C99F5E", wisp=1.0, foot=0.3, side_fade=0.15)
            + S.fog(f"{U}d1b", x + 180, x + PW + 20, y + 130, 100, seed=11, opacity=0.9, colour="#D9B97A", wisp=1.1, foot=0.3, side_fade=0.2))
    turn = S.ribbon(f"{U}t1", [(x + 190, y + 84), (x + 226, y + 70), (x + 232, y + 108), (x + 188, y + 118), (x + 90, y + 112)], 6.0, "#E8782E", "#F6B36B", opacity=0.92, head=2.2, tail=0.4, per=8)
    return side(0, 4, 100.0, dust + turn)


def scene_2():                                               # a dust storm over several aerodromes
    x, y = PX[1], PY[1]
    band = (S.fog(f"{U}d2", x - 10, x + PW + 10, y + 128, 120, seed=3, opacity=0.9, colour="#C99F5E", wisp=1.0, foot=0.2, side_fade=0.05)
            + S.fog(f"{U}d2b", x - 10, x + PW + 10, y + 120, 90, seed=14, opacity=0.9, colour="#D9B97A", wisp=1.1, foot=0.4))
    brk = (f'<path d="M{x + 16} {y + 22} L{x + 16} {y + 34} L{x + PW - 16} {y + 34} L{x + PW - 16} {y + 22}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
           f'<rect x="{n(x + PW / 2 - 34)}" y="{n(y + 8)}" width="68" height="22" rx="11" fill="#1F2937" stroke="#FFFFFF" stroke-width="1.4"/>' + H.glyph_text("500 KM", x + PW / 2, y + 19.5, 10.0, fill="#FFFFFF"))
    return plan(1, band + f'<g opacity="0.62">' + strip(x + 40, y + 70) + strip(x + 130, y + 104, 52.0, -8.0) + strip(x + 220, y + 76, 46.0, 10.0) + "</g>" + brk)


def scene_3():                                               # a control zone and the three ways out
    x, y = PX[2], PY[2]
    cx, cy = x + 120, y + 96
    zone = f'<circle cx="{n(cx)}" cy="{n(cy)}" r="72" fill="#3B82F6" fill-opacity="0.10" stroke="{BLUE}" stroke-width="2.6" stroke-dasharray="9 6"/>'
    r1 = S.ribbon(f"{U}a", [(cx - 10, cy + 6), (cx + 30, cy - 14), (cx + 80, cy - 30), (cx + 160, cy - 40)], 5.4, "#2FA35A", "#9BE0B2", opacity=0.9, head=2.2, tail=0.4, per=8)
    r2 = S.ribbon(f"{U}b", [(cx - 10, cy + 8), (cx + 30, cy + 8), (cx + 90, cy + 8), (cx + 164, cy + 8)], 5.4, "#E8782E", "#F6B36B", opacity=0.9, head=2.2, tail=0.4, per=8)
    r3 = S.ribbon(f"{U}c", [(cx - 10, cy + 10), (cx + 16, cy + 36), (cx + 50, cy + 52), (cx + 84, cy + 58)], 5.4, "#7C8FB5", "#C7D2E8", opacity=0.9, head=2.2, tail=0.4, per=8)
    return plan(2, zone + strip(x + 196, y + 142, 52.0) + r1 + r2 + r3 + tower(cx - 40, cy - 20))


def scene_4():                                               # report to ATC
    x, y = PX[3], PY[3]
    haze = S.fog(f"{U}d4", x, x + 160, y + 140, 70, seed=7, opacity=0.9, colour="#D9B97A", wisp=1.0, foot=0.3, side_fade=0.3)
    return side(3, 12, 110.0, haze + tower(x + 262, y + 134, 1.6) + waves(x + 152, y + 74, -8.0, BLUE, 3) + waves(x + 232, y + 100, 172.0, GREEN, 3))


def sprites():
    o = lambda x, y, w, angle=0.0, name="sprite-side": {"name": name, "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[0] + 150, PY[0] + 102, 56), o(PX[2] + 120, PY[2] + 96, 40, 90.0, "sprite-top"), o(PX[3] + 124, PY[3] + 90, 60)]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene_1(), scene_2(), scene_3(), scene_4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-16-10-weather-turns",
        "replaces": "fig-16-10-weather-turns.svg",           # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-16-10-weather-turns.jpg",
        "caption": "Figure 16-10. When the weather turns in flight: turn back early, expect dust over several aerodromes, use the controlled VFR options, and report",
        "desc": ("Figure 16-10. When the weather turns in flight, in four scenes: turn back while the visibility is still good; a dust storm can cover several aerodromes at once, as in April 2018 when a wall of dust about 500 km wide crossed the peninsula; "
                 "a controlled VFR flight that cannot stay in VMC asks for an amended clearance, leaves the airspace or lands at the nearest suitable aerodrome; and a heavy dust storm or sandstorm is reported."),
        "legend": [
            "The weather may differ from the forecast, so have an alternative and be ready to divert. Turn back while the visibility is still good.",
            "A dust storm can cover several aerodromes at once: in April 2018 a wall of dust about 500 km wide crossed the peninsula and nearly reached Riyadh.",
            "A controlled VFR flight that cannot stay in VMC: when VMC will not be practicable, the PIC requests an amended clearance to continue in VMC to the destination or an alternative aerodrome, or to leave the controlled airspace; failing that, continues in VMC and tells ATC that the aircraft is leaving the airspace or landing at the nearest suitable aerodrome. In a control zone the PIC may request special VFR.",
            "IFR is no option for a VFR student, so turn early, and report a heavy dust storm or sandstorm.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
