"""Figure 31-11 (new). Night emergencies, from the last section of Chapter 31: four scenes.

1 electrical failure (a panel: the ammeter needle at its low end, a radio and the position lights kept on, the landing light kept off to save it for the landing, a torch in hand), 2 engine failure (best glide, 68 kt for the example aeroplane, a turn toward a lit aerodrome and away from a lit
town), 3 the landing light (a beam lighting the ground ahead; tested high, switched on in time, touchdown in the normal landing attitude at the slowest possible speed), 4 the four options: a lit aerodrome within gliding range, a lit town, a lit road and unlit open ground known to be suitable.
Shapes, colours and the numbers of the callouts; the only text is 68 KT, from the chapter. The drawings are generic."""
import math
import random

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar3110"
INK, BLUE, GREEN, AMBER, RED = "#334155", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
NIGHT = [(0.0, "#0B1633"), (0.55, "#1D2B58"), (0.9, "#3C4F86"), (1.0, "#4C5F95")]
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}


def frame(i, body, sky=True, base=None):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + (S.sky(uid + "k", x, y, PW, PH, NIGHT) if sky else "") + body
            + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def stars(i, seed, ymax=0.55):
    x, y = PX[i], PY[i]
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{n(rnd.uniform(x + 8, x + PW - 8))}" cy="{n(rnd.uniform(y + 6, y + PH * ymax))}" r="{n(rnd.uniform(0.6, 1.3))}" fill="#FFFFFF" opacity="{n(rnd.uniform(0.5, 0.95))}"/>' for _ in range(36))


def lamp(cx, cy, r=1.8, col="#FFE9A8", glow=8.0):
    return S.glow(f"{U}l{int(cx * 7)}{int(cy * 7)}", cx, cy, glow, col, 0.8) + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{r}" fill="#FFF6D6"/>'


def pill(cx, cy, text, fill="#1F2937", size=10.0):
    g = H._GLYPHS
    w = sum((size * 0.38 if c == " " else g["glyphs"][c]["advance"] * size / g["cap_height"]) + 0.4 for c in text) + 14.0
    h = size + 7.0
    return (f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4))


def ground(i, hz, col="#2A2F3F"):
    x, y = PX[i], PY[i]
    return f'<rect x="{n(x)}" y="{n(y + hz)}" width="{n(PW)}" height="{n(PH - hz)}" fill="{col}"/>'


def check(cx, cy, col=GREEN, s=1.0):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(11 * s)}" fill="#FFFFFF" stroke="{col}" stroke-width="2.4"/><path d="M{n(cx - 5 * s)} {n(cy)} l{n(4 * s)} {n(4.4 * s)} l{n(7 * s)} {n(-9 * s)}" fill="none" stroke="{col}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'


def warn(cx, cy, s=1.0):
    return (f'<path d="M{n(cx)} {n(cy - 12 * s)} L{n(cx + 13 * s)} {n(cy + 10 * s)} L{n(cx - 13 * s)} {n(cy + 10 * s)} Z" fill="#FACC15" stroke="{AMBER}" stroke-width="2" stroke-linejoin="round"/>'
            f'<line x1="{n(cx)}" y1="{n(cy - 5 * s)}" x2="{n(cx)}" y2="{n(cy + 2 * s)}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/><circle cx="{n(cx)}" cy="{n(cy + 6 * s)}" r="{n(1.4 * s)}" fill="{INK}"/>')


def scene1():                                                # a panel: loads shed, the landing light kept for the landing
    x, y = PX[0], PY[0]
    base = f'<defs><linearGradient id="{U}g1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F2937"/><stop offset="1" stop-color="#0F172A"/></linearGradient></defs><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" fill="url(#{U}g1)"/>'
    dial = f'<circle cx="{n(x + 82)}" cy="{n(y + 84)}" r="46" fill="#0B1220" stroke="#E2E8F0" stroke-width="4"/>' + "".join(f'<line x1="{n(x + 82 + 40 * math.cos(math.radians(a)))}" y1="{n(y + 84 - 40 * math.sin(math.radians(a)))}" x2="{n(x + 82 + 35 * math.cos(math.radians(a)))}" y2="{n(y + 84 - 35 * math.sin(math.radians(a)))}" stroke="#F8FAFC" stroke-width="2"/>' for a in range(200, -21, -20)) + f'<path d="M{n(x + 82)} {n(y + 84)} L{n(x + 82 + 34 * math.cos(math.radians(188)))} {n(y + 84 - 34 * math.sin(math.radians(188)))}" stroke="#F87171" stroke-width="3.6" stroke-linecap="round"/><circle cx="{n(x + 82)}" cy="{n(y + 84)}" r="4.6" fill="#E2E8F0"/><path d="M{n(x + 58)} {n(y + 116)} h48" stroke="#F87171" stroke-width="3" stroke-linecap="round" stroke-opacity="0.8"/>'
    sw = ""
    for k, on in enumerate((True, True, False)):                 # radio, position lights, landing light
        cx = x + 172 + k * 36
        sw += f'<rect x="{n(cx - 12)}" y="{n(y + 54)}" width="24" height="64" rx="6" fill="#374151" stroke="#9CA3AF" stroke-width="1.6"/><rect x="{n(cx - 4.5)}" y="{n(y + (60 if on else 84))}" width="9" height="28" rx="3" fill="{"#22C55E" if on else "#6B7280"}"/><circle cx="{n(cx)}" cy="{n(y + 132)}" r="6" fill="{"#22C55E" if on else "#4B5563"}"/>'
    torch = f'<path d="M{n(x + 232)} {n(y + 158)} l30 -14 l6 12 l-30 14 Z" fill="#475569" stroke="#E2E8F0" stroke-width="1.6"/><path d="M{n(x + 264)} {n(y + 145)} L{n(x + 300)} {n(y + 132)} L{n(x + 302)} {n(y + 168)} L{n(x + 268)} {n(y + 156)} Z" fill="#FDE68A" fill-opacity="0.45"/>'
    return frame(0, base + dial + sw + torch, sky=False)


def scene2():                                                # engine failure: best glide toward a lit aerodrome, away from a lit town
    x, y = PX[1], PY[1]
    rnd = random.Random(2)
    town = "".join(lamp(x + 42 + rnd.uniform(-26, 26), y + 150 + rnd.uniform(-14, 10), 1.5, "#FFE9A8", 5.5) for _ in range(22))
    strip = "".join(lamp(x + 168 + k * 14, y + 160, 1.5, "#FFFFFF", 5.5) + lamp(x + 168 + k * 14, y + 170, 1.5, "#FFFFFF", 5.5) for k in range(7))
    glide = f'<path d="M{n(x + 110)} {n(y + 66)} L{n(x + 205)} {n(y + 156)}" stroke="#FFFFFF" stroke-width="2.4" stroke-dasharray="6 5" stroke-opacity="0.9"/>'
    away = f'<circle cx="{n(x + 42)}" cy="{n(y + 128)}" r="14" fill="none" stroke="{RED}" stroke-width="3"/><path d="M{n(x + 32)} {n(y + 118)} l20 20" stroke="{RED}" stroke-width="3"/>'
    return frame(1, stars(1, 3) + ground(1, 118) + town + strip + glide + away + pill(x + 170, y + 28, "68 KT", "#1F2937"))


def scene3():                                                # the landing light shows the ground ahead
    x, y = PX[2], PY[2]
    beam = f'<path d="M{n(x + 126)} {n(y + 86)} L{n(x + 312)} {n(y + 126)} L{n(x + 312)} {n(y + 190)} L{n(x + 190)} {n(y + 176)} Z" fill="#FDE68A" fill-opacity="0.32"/><path d="M{n(x + 126)} {n(y + 86)} L{n(x + 312)} {n(y + 126)} L{n(x + 190)} {n(y + 176)} Z" fill="#FEF3C7" fill-opacity="0.22"/>'
    lit = f'<ellipse cx="{n(x + 224)}" cy="{n(y + 150)}" rx="52" ry="16" fill="#D8C58C" fill-opacity="0.55"/>' + "".join(f'<circle cx="{n(x + 196 + k * 12)}" cy="{n(y + 148 + (k % 3) * 5)}" r="1.8" fill="#8A7B54"/>' for k in range(6))
    return frame(2, stars(2, 5) + ground(2, 120) + beam + lit)


def scene4():                                                # the four options
    x, y = PX[3], PY[3]
    cells = ((x + 12, y + 14), (x + 158, y + 14), (x + 12, y + 102), (x + 158, y + 102))
    out = []
    for k, (cx, cy) in enumerate(cells):
        out.append(f'<rect x="{n(cx)}" y="{n(cy)}" width="134" height="76" rx="8" fill="#10192F" stroke="#33415C" stroke-width="1.6"/>')
    # a lit aerodrome
    cx, cy = cells[0]
    out.append("".join(lamp(cx + 22 + k * 15, cy + 50, 1.4, "#FFFFFF", 5) + lamp(cx + 22 + k * 15, cy + 60, 1.4, "#FFFFFF", 5) for k in range(7)) + check(cx + 116, cy + 18))
    # a lit town
    cx, cy = cells[1]
    rnd = random.Random(7)
    out.append("".join(lamp(cx + 20 + rnd.uniform(0, 80), cy + 26 + rnd.uniform(0, 40), 1.4, "#FFE9A8", 5) for _ in range(16)) + warn(cx + 116, cy + 18))
    # a lit road
    cx, cy = cells[2]
    out.append(f'<path d="M{n(cx + 12)} {n(cy + 60)} L{n(cx + 120)} {n(cy + 30)}" stroke="#475569" stroke-width="7" stroke-linecap="round"/>' + "".join(lamp(cx + 20 + k * 20, cy + 56 - k * 5.6, 1.5, "#FFE9A8", 5) for k in range(6)) + warn(cx + 116, cy + 18))
    # unlit open ground known to be suitable
    cx, cy = cells[3]
    out.append(f'<ellipse cx="{n(cx + 62)}" cy="{n(cy + 46)}" rx="48" ry="18" fill="#2A2F3F" stroke="#4B5875" stroke-width="1.4" stroke-dasharray="4 4"/>' + check(cx + 116, cy + 18))
    return frame(3, "".join(out), sky=False)


def sprites():
    o = lambda x, y, w, angle=0.0: {"name": "sprite-side", "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **({"angle": angle} if angle else {})}
    return [o(PX[1] + 96, PY[1] + 62, 46, 8.0), o(PX[2] + 100, PY[2] + 76, 52, 8.0)]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="404" fill="#ffffff"/>', scene1(), scene2(), scene3(), scene4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-31-11-night-emergencies",
        "replaces": "fig-31-11-night-emergencies.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-31-11-night-emergencies.jpg",
        "caption": "Figure 31-11. Night emergencies: electrical failure, engine failure, the landing light and the four options",
        "desc": ("Figure 31-11. Night emergencies, four scenes: electrical failure, with the loads shed, a radio and the position lights kept on, the landing light saved for the landing and a torch in hand; engine failure, with the best glide of 68 kt for the example aeroplane "
                 "toward a lit aerodrome and away from a lit town; the landing light, tested while high and switched on in time to light the terrain; and the four options: a lit aerodrome within gliding range, a lit town, a lit road and unlit open ground known to be suitable."),
        "legend": [
            "Electrical failure: fly the aeroplane, torch in hand. Shed every load you can spare at once; keep a radio and the position lights; save the landing light for landing. Tell ATC and land at the nearest suitable lit aerodrome.",
            "Engine failure: keep control; best glide, 68 kt for the example aeroplane. Turn toward an aerodrome or away from congested areas, find the cause and try a restart as the AFM checklist directs, and declare the emergency.",
            "Test the landing light while high and switch it on in time to light the terrain and obstacles; touch down in the normal landing attitude at the slowest possible speed. Without the light or outside references, hold a level landing attitude until you touch.",
            "The options: a lit aerodrome within gliding range is rarely in reach unless planned; a lit town has buildings, wires and people, so turn away; a lit road has poles, signs, wires and traffic; unlit open ground known to be suitable has no buildings or people, but you see its surface only in the landing light.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
