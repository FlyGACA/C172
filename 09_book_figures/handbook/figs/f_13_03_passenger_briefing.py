"""Figure 13-3 (new). The passenger briefing of GACAR 91.45(a): the eight subjects as eight tiles, each with a small drawing and its number, in the order of the rule (smoking, safety belts and harnesses, seat backs for takeoff and landing, fire extinguishers,
doors and emergency exits, survival equipment, ditching on a flight over water, oxygen equipment), and under them the rule of 91.45(b): the oral briefing in Arabic and in English (two speech bubbles marked AR and EN).
No words but AR, EN and O2: shapes, colours and the numbers of the callouts. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "pb13"
INK, SLATE, BLUE, GREEN, AMBER, RED, ORANGE = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#EA580C"
TW, TH = 142.0, 98.0
GX = (20.0, 175.0, 330.0, 485.0)
GY = (16.0, 126.0)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def tile(i):
    x, y = GX[i % 4], GY[i // 4]
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(TW)}" height="{n(TH)}" rx="9" fill="#EEF2F7" stroke="#CBD5E1" stroke-width="1.2"/>'


def icon(i):
    cx = GX[i % 4] + TW / 2 + 6
    cy = GY[i // 4] + TH / 2 + 4
    o = []
    if i == 0:                                           # smoking: a cigarette in a red crossed circle
        o.append(f'<rect x="{n(cx - 26)}" y="{n(cy - 4)}" width="40" height="8" rx="2" fill="#F8FAFC" stroke="{SLATE}" stroke-width="1.4"/><rect x="{n(cx + 8)}" y="{n(cy - 4)}" width="6" height="8" fill="#F59E0B"/><rect x="{n(cx - 26)}" y="{n(cy - 4)}" width="8" height="8" rx="2" fill="#C8A26B"/>'
                 f'<path d="M{n(cx + 18)} {n(cy - 4)} q4 -6 0 -10 q-4 -4 0 -8" fill="none" stroke="#94A3B8" stroke-width="1.8" stroke-linecap="round"/>')
        o.append(f'<circle cx="{n(cx - 2)}" cy="{n(cy)}" r="30" fill="none" stroke="{RED}" stroke-width="4.4"/><line x1="{n(cx - 23)}" y1="{n(cy + 21)}" x2="{n(cx + 19)}" y2="{n(cy - 21)}" stroke="{RED}" stroke-width="4.4" stroke-linecap="round"/>')
    elif i == 1:                                         # safety belt and harness: a lap belt with a buckle and a shoulder strap
        o.append(f'<path d="M{n(cx - 38)} {n(cy + 14)} L{n(cx - 6)} {n(cy + 14)} M{n(cx + 6)} {n(cy + 14)} L{n(cx + 38)} {n(cy + 14)}" stroke="{INK}" stroke-width="9" stroke-linecap="butt" fill="none"/>'
                 f'<path d="M{n(cx - 22)} {n(cy - 30)} L{n(cx)} {n(cy + 12)}" stroke="#1E3A8A" stroke-width="8" stroke-linecap="butt" fill="none"/>')
        o.append(f'<rect x="{n(cx - 11)}" y="{n(cy + 5)}" width="22" height="18" rx="3" fill="#E2E8F0" stroke="{SLATE}" stroke-width="1.6" filter="url(#{U}ds)"/><rect x="{n(cx - 4)}" y="{n(cy + 10)}" width="8" height="8" rx="1.5" fill="{RED}"/>')
    elif i == 2:                                         # seat backs: a seat in profile with the back upright and a dashed arc where it was reclined
        o.append(f'<path d="M{n(cx - 30)} {n(cy + 26)} L{n(cx - 30)} {n(cy + 8)} L{n(cx + 18)} {n(cy + 8)} L{n(cx + 18)} {n(cy + 26)} Z" fill="#64748B" stroke="{SLATE}" stroke-width="1.4" stroke-linejoin="round"/>'
                 f'<path d="M{n(cx - 30)} {n(cy + 8)} L{n(cx - 30)} {n(cy - 30)}" stroke="{SLATE}" stroke-width="12" stroke-linecap="round"/><path d="M{n(cx - 30)} {n(cy + 8)} L{n(cx - 30)} {n(cy - 30)}" stroke="#94A3B8" stroke-width="8" stroke-linecap="round"/>'
                 f'<path d="M{n(cx - 30)} {n(cy + 8)} L{n(cx - 58)} {n(cy - 22)}" stroke="{SLATE}" stroke-width="2" stroke-dasharray="4 3" stroke-linecap="round"/>'
                 f'<path d="M{n(cx - 52)} {n(cy - 6)} Q{n(cx - 44)} {n(cy - 20)} {n(cx - 36)} {n(cy - 22)}" fill="none" stroke="{GREEN}" stroke-width="2.6" stroke-linecap="round"/><path d="M{n(cx - 34)} {n(cy - 22)} L{n(cx - 42)} {n(cy - 25)} L{n(cx - 40)} {n(cy - 16)} Z" fill="{GREEN}"/>')
    elif i == 3:                                         # fire extinguisher
        o.append(f'<rect x="{n(cx - 13)}" y="{n(cy - 12)}" width="26" height="42" rx="8" fill="{RED}" stroke="#7F1D1D" stroke-width="1.4" filter="url(#{U}ds)"/><rect x="{n(cx - 6)}" y="{n(cy - 20)}" width="12" height="10" rx="2" fill="{INK}"/>'
                 f'<path d="M{n(cx + 6)} {n(cy - 16)} L{n(cx + 24)} {n(cy - 16)} L{n(cx + 26)} {n(cy - 4)}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><path d="M{n(cx - 6)} {n(cy - 20)} L{n(cx - 22)} {n(cy - 24)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
                 f'<rect x="{n(cx - 8)}" y="{n(cy + 2)}" width="16" height="12" rx="2" fill="#FFFFFF" fill-opacity="0.9"/>')
    elif i == 4:                                         # doors and emergency exits: a door ajar and an arrow out
        o.append(f'<rect x="{n(cx - 30)}" y="{n(cy - 30)}" width="34" height="56" rx="3" fill="{GREEN}" stroke="#14532D" stroke-width="1.6" filter="url(#{U}ds)"/>'
                 f'<path d="M{n(cx - 30)} {n(cy - 30)} L{n(cx - 52)} {n(cy - 22)} L{n(cx - 52)} {n(cy + 32)} L{n(cx - 30)} {n(cy + 26)} Z" fill="#166534" stroke="#14532D" stroke-width="1.4" stroke-linejoin="round"/>'
                 f'<line x1="{n(cx - 2)}" y1="{n(cy)}" x2="{n(cx + 36)}" y2="{n(cy)}" stroke="{GREEN}" stroke-width="5" stroke-linecap="round"/><path d="M{n(cx + 44)} {n(cy)} L{n(cx + 32)} {n(cy - 9)} L{n(cx + 32)} {n(cy + 9)} Z" fill="{GREEN}"/>')
    elif i == 5:                                         # survival equipment: a box with a cross and a bottle
        o.append(f'<rect x="{n(cx - 34)}" y="{n(cy - 18)}" width="52" height="42" rx="5" fill="{ORANGE}" stroke="#9A3412" stroke-width="1.6" filter="url(#{U}ds)"/><rect x="{n(cx - 20)}" y="{n(cy - 26)}" width="24" height="9" rx="3" fill="none" stroke="#9A3412" stroke-width="2.4"/>'
                 f'<path d="M{n(cx - 8)} {n(cy - 8)} h8 v8 h8 v8 h-8 v8 h-8 v-8 h-8 v-8 h8 Z" fill="#FFFFFF" transform="translate(-2 -2)"/>'
                 f'<rect x="{n(cx + 24)}" y="{n(cy - 2)}" width="14" height="26" rx="4" fill="#38BDF8" stroke="{SLATE}" stroke-width="1.4"/><rect x="{n(cx + 27)}" y="{n(cy - 8)}" width="8" height="7" fill="{SLATE}"/>')
    elif i == 6:                                         # ditching: waves and a lifebuoy
        o.append(f'<path d="M{n(cx - 48)} {n(cy + 22)} q8 -9 16 0 t16 0 t16 0 t16 0 t16 0 t16 0" fill="none" stroke="{BLUE}" stroke-width="3.4" stroke-linecap="round"/>'
                 f'<path d="M{n(cx - 48)} {n(cy + 32)} q8 -9 16 0 t16 0 t16 0 t16 0 t16 0 t16 0" fill="none" stroke="#60A5FA" stroke-width="3" stroke-linecap="round"/>')
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy - 8)}" r="22" fill="none" stroke="#FFFFFF" stroke-width="15"/><circle cx="{n(cx)}" cy="{n(cy - 8)}" r="22" fill="none" stroke="{ORANGE}" stroke-width="12" filter="url(#{U}ds)"/>')
        for k in range(4):
            a0 = math.radians(45 + 90 * k - 14)
            a1 = math.radians(45 + 90 * k + 14)
            o.append(f'<path d="M{n(cx + 22 * math.cos(a0))} {n(cy - 8 + 22 * math.sin(a0))} A22 22 0 0 1 {n(cx + 22 * math.cos(a1))} {n(cy - 8 + 22 * math.sin(a1))}" fill="none" stroke="#FFFFFF" stroke-width="12"/>')
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy - 8)}" r="28" fill="none" stroke="#9A3412" stroke-width="1.2"/><circle cx="{n(cx)}" cy="{n(cy - 8)}" r="16" fill="none" stroke="#9A3412" stroke-width="1.2"/>')
    else:                                                # oxygen equipment: a cylinder marked O2 and a mask
        o.append(f'<rect x="{n(cx - 12)}" y="{n(cy - 18)}" width="24" height="46" rx="9" fill="#16A34A" stroke="#14532D" stroke-width="1.4" filter="url(#{U}ds)"/><rect x="{n(cx - 5)}" y="{n(cy - 26)}" width="10" height="9" rx="2" fill="{INK}"/>')
        o.append(H.glyph_text("O2", cx, cy + 8, 6.0, "#FFFFFF", spacing=0.3))
        o.append(f'<path d="M{n(cx + 12)} {n(cy - 22)} Q{n(cx + 28)} {n(cy - 20)} {n(cx + 30)} {n(cy - 4)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
                 f'<path d="M{n(cx + 22)} {n(cy - 4)} Q{n(cx + 30)} {n(cy - 12)} {n(cx + 40)} {n(cy - 4)} Q{n(cx + 40)} {n(cy + 10)} {n(cx + 30)} {n(cy + 12)} Q{n(cx + 22)} {n(cy + 8)} {n(cx + 22)} {n(cy - 4)} Z" fill="#E2E8F0" stroke="{SLATE}" stroke-width="1.4"/>')
    return "".join(o)


def bubbles():
    """The rule of 91.45(b): the oral briefing in Arabic and in English, two speech bubbles side by side."""
    out = []
    y = 244.0
    for x, label, col in ((248.0, "AR", GREEN), (392.0, "EN", BLUE)):
        out.append(f'<path d="M{n(x - 50)} {n(y - 18)} h100 a10 10 0 0 1 10 10 v18 a10 10 0 0 1 -10 10 h-72 l-12 12 v-12 h-16 a10 10 0 0 1 -10 -10 v-18 a10 10 0 0 1 10 -10 Z" fill="{col}" stroke="#FFFFFF" stroke-width="1.6" stroke-linejoin="round" filter="url(#{U}ds)"/>')
        out.append(H.glyph_text(label, x, y - 2, 10.0, "#FFFFFF", spacing=0.6))
    out.append(f'<line x1="316" y1="{n(y - 14)}" x2="316" y2="{n(y + 10)}" stroke="{SLATE}" stroke-opacity="0.35" stroke-width="1.2"/>')
    return "".join(out)


def callouts():
    c = S.callout
    out = []
    for i in range(8):
        x, y = GX[i % 4], GY[i // 4]
        out.append(c(i + 1, x + 14, y + 14, r=9.0))
    out.append(c(9, 168.0, 244.0, 196.0, 244.0, r=9.0))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), *[tile(i) for i in range(8)], *[icon(i) for i in range(8)], bubbles(), callouts()]


def plate():
    return {
        "id": "fig-13-03-passenger-briefing",
        "replaces": "fig-13-03-passenger-briefing.svg",   # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-13-03-passenger-briefing.jpg",
        "caption": "Figure 13-3. The passenger briefing of GACAR 91.45: the eight subjects, and the briefing in Arabic and English",
        "desc": ("Figure 13-3. The passenger briefing of GACAR 91.45: the eight subjects as eight tiles (smoking, safety belts and harnesses, seat backs, fire extinguishers, doors and emergency exits, "
                 "survival equipment, ditching, oxygen equipment), and the oral briefing in Arabic and in English."),
        "legend": [
            "Smoking.",
            "Safety belts and harnesses.",
            "Seat backs for takeoff and landing.",
            "The fire extinguishers.",
            "The doors and emergency exits.",
            "The survival equipment.",
            "Ditching, on a flight over water.",
            "Any oxygen equipment.",
            "The oral briefing is given in both Arabic and English, unless the person giving it has established that every passenger understands one language; printed cards may supplement it. It may be omitted when the PIC determines that the passengers already know its contents.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
