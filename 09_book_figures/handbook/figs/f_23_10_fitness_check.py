"""Figure 23-10 (new). The fitness check before every flight, from the last section of Chapter 23: seven questions as seven tiles, and the rule for the air as an eighth.

The chapter's list: ill or recovering (1, a thermometer), taking anything (2, a capsule), short of sleep (3, a moon and Z), short of food or water (4, a glass and an apple), under pressure (5, a clock pressed by two arrows), recently diving (6, a mask and bubbles) and going high or into dust
or darkness (7, a mountain, dust and a moon); 8 is the rule for the air: if your capacity is significantly reduced, do not continue beyond the nearest suitable aerodrome (an aeroplane, a runway and a red stop bar beyond it). Shapes, colours and the numbers of the callouts."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 236
U = "fc23"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
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
    return R.tile(f"{U}t{i}", x, y, TW, TH, ("red", "sand", "night", "green", "blue", "slate", "night", "red")[i])


def icon(i):
    cx = GX[i % 4] + TW / 2 + 6
    cy = GY[i // 4] + TH / 2 + 6
    o = []
    if i == 0:                                           # a thermometer
        o.append(f'<rect x="{n(cx - 6)}" y="{n(cy - 32)}" width="12" height="46" rx="6" fill="#F8FAFC" stroke="{SLATE}" stroke-width="2.2" filter="url(#{U}ds)"/><circle cx="{n(cx)}" cy="{n(cy + 18)}" r="12" fill="{RED}" stroke="{SLATE}" stroke-width="2.2"/>'
                 f'<rect x="{n(cx - 2.6)}" y="{n(cy - 12)}" width="5.2" height="32" rx="2.6" fill="{RED}"/>')
        for k in range(4):
            o.append(f'<line x1="{n(cx + 10)}" y1="{n(cy - 26 + k * 9)}" x2="{n(cx + 16)}" y2="{n(cy - 26 + k * 9)}" stroke="{SLATE}" stroke-width="1.6"/>')
    elif i == 1:                                         # a capsule and a tablet
        o.append(f'<g transform="rotate(-35 {n(cx - 6)} {n(cy - 4)})"><rect x="{n(cx - 30)}" y="{n(cy - 12)}" width="48" height="24" rx="12" fill="#F8FAFC" stroke="{SLATE}" stroke-width="2.2" filter="url(#{U}ds)"/>'
                 f'<path d="M{n(cx - 6)} {n(cy - 12)} h12 a12 12 0 0 1 0 24 h-12 Z" fill="{BLUE}"/></g>')
        o.append(f'<circle cx="{n(cx + 20)}" cy="{n(cy + 20)}" r="11" fill="#FDE68A" stroke="{SLATE}" stroke-width="2" filter="url(#{U}ds)"/><line x1="{n(cx + 13)}" y1="{n(cy + 20)}" x2="{n(cx + 27)}" y2="{n(cy + 20)}" stroke="{SLATE}" stroke-width="1.6"/>')
    elif i == 2:                                         # sleep: a crescent moon and Z
        o.append(f'<circle cx="{n(cx - 8)}" cy="{n(cy)}" r="22" fill="#F7EBC2" stroke="#FFFFFF" stroke-width="1.4" filter="url(#{U}ds)"/><circle cx="{n(cx + 4)}" cy="{n(cy - 8)}" r="19" fill="#43558C"/>')
        for k, s in enumerate((7.0, 5.6, 4.4)):
            o.append(H.glyph_text("Z", cx + 22 + k * 5, cy - 6 - k * 12, s, SLATE, spacing=0.3))
    elif i == 3:                                         # food and water: a glass and an apple
        o.append(f'<path d="M{n(cx - 36)} {n(cy - 22)} L{n(cx - 16)} {n(cy - 22)} L{n(cx - 20)} {n(cy + 24)} L{n(cx - 32)} {n(cy + 24)} Z" fill="#E0F2FE" stroke="{SLATE}" stroke-width="2.2" filter="url(#{U}ds)"/>'
                 f'<path d="M{n(cx - 33)} {n(cy + 10)} L{n(cx - 19)} {n(cy + 10)} L{n(cx - 20)} {n(cy + 24)} L{n(cx - 32)} {n(cy + 24)} Z" fill="#38BDF8"/>')
        o.append(f'<circle cx="{n(cx + 14)}" cy="{n(cy + 4)}" r="20" fill="{RED}" stroke="#7F1D1D" stroke-width="1.8" filter="url(#{U}ds)"/><path d="M{n(cx + 14)} {n(cy - 14)} q2 -10 10 -12" fill="none" stroke="#7F1D1D" stroke-width="2.4" stroke-linecap="round"/><path d="M{n(cx + 16)} {n(cy - 20)} q8 -8 14 0 q-8 6 -14 0 Z" fill="{GREEN}"/>')
    elif i == 4:                                         # pressure: a clock pressed by two arrows
        o.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="24" fill="#FFFFFF" stroke="{SLATE}" stroke-width="3" filter="url(#{U}ds)"/>'
                 f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(cy - 15)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + 11)}" y2="{n(cy + 4)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        for sgn in (-1, 1):
            x0 = cx + sgn * 52
            o.append(f'<line x1="{n(x0)}" y1="{n(cy)}" x2="{n(cx + sgn * 32)}" y2="{n(cy)}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/><path d="M{n(cx + sgn * 27)} {n(cy)} L{n(cx + sgn * 37)} {n(cy - 8)} L{n(cx + sgn * 37)} {n(cy + 8)} Z" fill="{RED}"/>')
    elif i == 5:                                         # diving: a mask and bubbles
        o.append(f'<rect x="{n(cx - 34)}" y="{n(cy - 16)}" width="68" height="36" rx="14" fill="#0EA5E9" stroke="{INK}" stroke-width="3.2" filter="url(#{U}ds)"/><rect x="{n(cx - 26)}" y="{n(cy - 9)}" width="22" height="22" rx="8" fill="#E0F2FE"/><rect x="{n(cx + 4)}" y="{n(cy - 9)}" width="22" height="22" rx="8" fill="#E0F2FE"/>'
                 f'<path d="M{n(cx - 34)} {n(cy)} h-8 M{n(cx + 34)} {n(cy)} h8" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
        for k, (dx, dy, r) in enumerate(((24, -26, 4), (32, -38, 5.4), (22, -48, 3.4))):
            o.append(f'<circle cx="{n(cx + dx)}" cy="{n(cy + dy + 16)}" r="{r}" fill="#BAE6FD" stroke="{SLATE}" stroke-width="1.4"/>')
    elif i == 6:                                         # high, dust or darkness: a mountain, dust and a moon
        o.append(f'<path d="M{n(cx - 44)} {n(cy + 26)} L{n(cx - 12)} {n(cy - 22)} L{n(cx + 6)} {n(cy + 2)} L{n(cx + 18)} {n(cy - 10)} L{n(cx + 46)} {n(cy + 26)} Z" fill="#94A3B8" stroke="{SLATE}" stroke-width="2.2" stroke-linejoin="round" filter="url(#{U}ds)"/>'
                 f'<path d="M{n(cx - 12)} {n(cy - 22)} L{n(cx - 20)} {n(cy - 10)} L{n(cx - 12)} {n(cy - 14)} L{n(cx - 4)} {n(cy - 8)} Z" fill="#FFFFFF"/>')
        o.append(f'<circle cx="{n(cx + 34)}" cy="{n(cy - 28)}" r="10" fill="#F7EBC2"/><circle cx="{n(cx + 39)}" cy="{n(cy - 32)}" r="9" fill="#3E5084"/>')
        for k, (dx, dy) in enumerate(((-30, 14), (-20, 20), (-6, 12), (6, 20), (20, 14), (30, 22), (-36, 24), (36, 10))):
            o.append(f'<circle cx="{n(cx + dx)}" cy="{n(cy + dy)}" r="2.4" fill="#B45309" fill-opacity="0.8"/>')
    else:                                                # the rule for the air: an aeroplane, a runway and a stop bar beyond it
        o.append(f'<rect x="{n(cx - 8)}" y="{n(cy - 30)}" width="46" height="62" rx="3" fill="#475569" stroke="#1E293B" stroke-width="1.4"/><line x1="{n(cx + 15)}" y1="{n(cy - 26)}" x2="{n(cx + 15)}" y2="{n(cy + 28)}" stroke="#F8FAFC" stroke-width="2" stroke-dasharray="6 5"/>')
        o.append(f'<line x1="{n(cx + 46)}" y1="{n(cy - 34)}" x2="{n(cx + 46)}" y2="{n(cy + 36)}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>')
    return "".join(o)


def sprites():
    cx = GX[3] + TW / 2 + 6 - 40
    cy = GY[1] + TH / 2 + 6 - 6
    return [A.plane(cx, cy, 42.0, name="sprite-top", angle=90.0)]


def callouts():
    c = S.callout
    return "".join(c(i + 1, GX[i % 4] + 14, GY[i // 4] + 14, r=9.0) for i in range(8))


def layers():
    return [H.defs(U, W, HT), background(), *[tile(i) for i in range(8)], *[icon(i) for i in range(8)], *sprites(), callouts()]


def plate():
    return {
        "id": "fig-23-10-fitness-check",
        "replaces": "fig-23-10-fitness-check.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-23-10-fitness-check.jpg",
        "caption": "Figure 23-10. A fitness check before every flight: seven questions, and the rule for the air",
        "desc": ("Figure 23-10. A fitness check before every flight: seven questions as seven tiles (ill or recovering, taking anything, short of sleep, short of food or water, under pressure, "
                 "recently diving, going high or into dust or darkness) and, as an eighth, the rule for the air: do not continue beyond the nearest suitable aerodrome if your capacity is significantly reduced."),
        "legend": [
            "Are you ill or recovering?",
            "Are you taking anything: medication or any other substance?",
            "Are you short of sleep?",
            "Are you short of food or water?",
            "Are you under pressure?",
            "Have you been diving recently?",
            "Are you going high, or into dust or darkness?",
            "In the air the question continues: if your capacity is significantly reduced, do not continue beyond the nearest suitable aerodrome (section 91.3(d)). Chapter 24 turns these questions into a checklist and personal minimums.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
