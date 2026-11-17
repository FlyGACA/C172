"""Figure 22-9 (new). Collision avoidance in Saudi conditions, from the last section of Chapter 22: five tiles, one for each point of its list.

1 busy training aerodromes (a circuit with three trainers round a runway), 2 mixed traffic (a large jet and a trainer, with the wake of the jet as a spiral behind it), 3 haze and dust (a distant aeroplane faint against a hazy band), 4 sun (a bright sun low in a windscreen, with its glare),
5 night (a moon and an aeroplane with its position lights and its anticollision light). Shapes, colours and the numbers of the callouts. The drawings are generic."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 180
U = "sc22"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
TW, TH = 112.0, 146.0
GX = (20.0, 143.0, 266.0, 389.0, 512.0)
GY = 18.0


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter>'
            f'<linearGradient id="{U}sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFDBFE"/><stop offset="1" stop-color="#F8FAFC"/></linearGradient>'
            f'<linearGradient id="{U}nt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0F172A"/><stop offset="1" stop-color="#1E3A8A"/></linearGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def tile(i):
    fill = f"url(#{U}nt)" if i == 4 else (f"url(#{U}sk)" if i in (2, 3) else "#EEF2F7")
    return f'<rect x="{n(GX[i])}" y="{n(GY)}" width="{n(TW)}" height="{n(TH)}" rx="9" fill="{fill}" stroke="#CBD5E1" stroke-width="1.2"/>'


def jet(x, y, s=1.0, col="#E2E8F0"):
    return (f'<path d="M{n(x)} {n(y - 30 * s)} q{n(5 * s)} {n(6 * s)} {n(5 * s)} {n(22 * s)} L{n(x + 34 * s)} {n(y + 6 * s)} L{n(x + 34 * s)} {n(y + 14 * s)} L{n(x + 5 * s)} {n(y + 10 * s)} L{n(x + 4 * s)} {n(y + 26 * s)} L{n(x + 14 * s)} {n(y + 32 * s)} L{n(x + 14 * s)} {n(y + 37 * s)} L{n(x)} {n(y + 34 * s)} '
            f'L{n(x - 14 * s)} {n(y + 37 * s)} L{n(x - 14 * s)} {n(y + 32 * s)} L{n(x - 4 * s)} {n(y + 26 * s)} L{n(x - 5 * s)} {n(y + 10 * s)} L{n(x - 34 * s)} {n(y + 14 * s)} L{n(x - 34 * s)} {n(y + 6 * s)} L{n(x - 5 * s)} {n(y - 8 * s)} q0 {n(-16 * s)} {n(5 * s)} {n(-22 * s)} Z" fill="{col}" stroke="{SLATE}" stroke-width="1.6" stroke-linejoin="round" filter="url(#{U}ds)"/>')


def icon(i):
    cx = GX[i] + TW / 2
    cy = GY + TH / 2 + 6
    o = []
    if i == 0:                                           # a circuit: a runway and an oval round it
        o.append(f'<rect x="{n(cx - 8)}" y="{n(cy - 28)}" width="16" height="56" rx="2" fill="#475569"/><line x1="{n(cx)}" y1="{n(cy - 24)}" x2="{n(cx)}" y2="{n(cy + 24)}" stroke="#F8FAFC" stroke-width="1.6" stroke-dasharray="5 4"/>')
        o.append(f'<rect x="{n(cx - 38)}" y="{n(cy - 42)}" width="76" height="84" rx="38" fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-dasharray="6 5"/>')
    elif i == 1:                                         # mixed traffic: a large jet, a trainer and the wake
        o.append(f'<path d="M{n(cx - 18)} {n(cy + 36)} q-26 -10 -8 -24 q22 -10 8 -22 q-14 -8 -4 -16" fill="none" stroke="{AMBER}" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="1 6"/>')
    elif i == 2:                                         # haze and dust: haze bands over the horizon
        o.append(f'<rect x="{n(GX[i] + 6)}" y="{n(cy - 6)}" width="{n(TW - 12)}" height="24" fill="#F1E3C0" fill-opacity="0.95"/><rect x="{n(GX[i] + 6)}" y="{n(cy + 18)}" width="{n(TW - 12)}" height="{n(GY + TH - 8 - cy - 18)}" rx="6" fill="#D9B97A" fill-opacity="0.95"/>')
        for k, (dx, dy, r) in enumerate(((-30, -22, 1.6), (-12, -36, 1.2), (20, -26, 1.8), (36, -40, 1.2), (-38, -44, 1.4), (6, -48, 1.6))):
            o.append(f'<circle cx="{n(cx + dx)}" cy="{n(cy + dy + 30)}" r="{r}" fill="#B45309" fill-opacity="0.55"/>')
    elif i == 3:                                         # the sun in a windscreen, with its glare
        o.append(f'<circle cx="{n(cx + 8)}" cy="{n(cy - 22)}" r="30" fill="#FDE68A" fill-opacity="0.45"/><circle cx="{n(cx + 8)}" cy="{n(cy - 22)}" r="16" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.6"/>')
        for k in range(12):
            a = math.radians(k * 30)
            o.append(f'<line x1="{n(cx + 8 + 20 * math.sin(a))}" y1="{n(cy - 22 - 20 * math.cos(a))}" x2="{n(cx + 8 + 30 * math.sin(a))}" y2="{n(cy - 22 - 30 * math.cos(a))}" stroke="#F59E0B" stroke-width="2.6" stroke-linecap="round"/>')
        o.append(f'<path d="M{n(GX[i] + 10)} {n(cy + 36)} L{n(GX[i] + 26)} {n(cy + 6)} L{n(GX[i] + TW - 26)} {n(cy + 6)} L{n(GX[i] + TW - 10)} {n(cy + 36)} Z" fill="#475569" fill-opacity="0.82" stroke="#1E293B" stroke-width="1.6"/>')
    else:                                                # night: a moon and an aeroplane with its lights
        o.append(f'<circle cx="{n(cx + 26)}" cy="{n(cy - 40)}" r="11" fill="#FDE68A"/><circle cx="{n(cx + 32)}" cy="{n(cy - 44)}" r="10" fill="#0F172A"/>')
        for dx, dy, r in ((-30, -34, 1.2), (-10, -50, 1.4), (14, -28, 1.0), (-38, -12, 1.2)):
            o.append(f'<circle cx="{n(cx + dx)}" cy="{n(cy + dy)}" r="{r}" fill="#F8FAFC"/>')
    return "".join(o)


def sprites():
    out = []
    cy = GY + TH / 2 + 6
    out.append(A.plane(GX[0] + TW / 2 - 38, cy + 6, 22.0, name="sprite-top", angle=0.0))
    out.append(A.plane(GX[0] + TW / 2 + 36, cy - 8, 22.0, name="sprite-top", angle=180.0))
    out.append(A.plane(GX[0] + TW / 2, cy - 42, 22.0, name="sprite-top", angle=90.0))
    out.append(A.plane(GX[1] + TW / 2 + 22, cy + 28, 34.0, name="sprite-top", angle=0.0))
    out.append(A.plane(GX[2] + TW / 2 + 6, cy - 24, 26.0, name="sprite-top", angle=0.0, opacity=0.38))
    out.append(A.plane(GX[4] + TW / 2 - 6, cy + 8, 52.0, name="sprite-top", angle=0.0, dark=True))
    return out


def front():
    """The jet over the trainer's tile and the position lights on the night aeroplane."""
    cx1 = GX[1] + TW / 2
    cy = GY + TH / 2 + 6
    out = [jet(cx1 - 14, cy - 22, 0.8)]
    lx = GX[4] + TW / 2 - 6
    ly = cy + 8
    out.append(f'<circle cx="{n(lx - 26)}" cy="{n(ly)}" r="3.2" fill="#EF4444" stroke="#FFFFFF" stroke-width="0.8"/><circle cx="{n(lx + 26)}" cy="{n(ly)}" r="3.2" fill="#22C55E" stroke="#FFFFFF" stroke-width="0.8"/><circle cx="{n(lx)}" cy="{n(ly + 28)}" r="3.4" fill="#F8FAFC" stroke="#FFFFFF" stroke-width="0.8"/>'
               f'<circle cx="{n(lx)}" cy="{n(ly - 4)}" r="4" fill="#F8FAFC" fill-opacity="0.9"/><circle cx="{n(lx)}" cy="{n(ly - 4)}" r="9" fill="#F8FAFC" fill-opacity="0.25"/>')
    return "".join(out)


def callouts():
    c = S.callout
    return "".join(c(i + 1, GX[i] + 14, GY + 14, r=9.0) for i in range(5))


def layers():
    return [H.defs(U, W, HT), background(), *[tile(i) for i in range(5)], *[icon(i) for i in range(5)], *sprites(), front(), callouts()]


def plate():
    return {
        "id": "fig-22-09-saudi-conditions",
        "replaces": "fig-22-09-saudi-conditions.svg",      # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-22-09-saudi-conditions.jpg",
        "caption": "Figure 22-9. Collision avoidance in Saudi conditions: five things to allow for",
        "desc": ("Figure 22-9. Collision avoidance in Saudi conditions, five tiles: busy training aerodromes, mixed traffic with large jets and their wake, haze and dust, the sun, and night."),
        "legend": [
            "Busy training aerodromes: several trainers can share one circuit and the nearby training areas. Expect traffic at your height, listen to every call and clear before every manoeuvre.",
            "Mixed traffic: at major aerodromes a trainer may share the circuit, runway or nearby airspace with large jets, with higher closing speeds and wake behind every movement. Joining and leaving procedures are in the aerodrome's AIP entry and your school's local orders.",
            "Haze and dust lower a distant aircraft's contrast against the sky, so you see it later, and you see less along a slant than the reported visibility suggests. Over featureless desert or above a haze layer, guard against empty-field myopia.",
            "Sun: a high, bright sun and windscreen glare hide traffic. Keep the windscreen clean.",
            "Night: night lessons are flown only under an authorization or local conditions (section 91.171), with position and anticollision lights on.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
