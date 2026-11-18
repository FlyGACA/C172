"""Figure 14-10 (new). What to look for in the weather of the Arabian Peninsula, from the last section of Chapter 14: five tiles, one for each point of its list.

1 heat (a sun over the ground with rising wavy lines, the thermals), 2 dust and haze (a hazy band over the horizon that hides the ground ahead), 3 the summer shamal (strong wind arrows blowing a wall of dust), 4 coastal humidity and fog (the sea, an onshore arrow and a layer of fog
at the shore), 5 convection over high ground (a mountain with a towering cumulonimbus and lightning). The chapter gives no climate statistics for places or months, and neither does the figure: shapes, colours and the numbers of the callouts. The drawings are generic."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 180
U = "ar14"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
TW, TH = 112.0, 146.0
GX = (20.0, 143.0, 266.0, 389.0, 512.0)
GY = 18.0
SAND = "#E3C27F"


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter>'
            f'<linearGradient id="{U}sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#93C5FD"/><stop offset="1" stop-color="#F8FAFC"/></linearGradient>'
            f'<linearGradient id="{U}st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#475569"/><stop offset="1" stop-color="#CBD5E1"/></linearGradient>'
            + "".join(f'<clipPath id="{U}c{i}"><rect x="{n(GX[i])}" y="{n(GY)}" width="{n(TW)}" height="{n(TH)}" rx="9"/></clipPath>' for i in range(5))
            + '</defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def tile(i):
    fill = f"url(#{U}st)" if i == 4 else f"url(#{U}sk)"
    return f'<rect x="{n(GX[i])}" y="{n(GY)}" width="{n(TW)}" height="{n(TH)}" rx="9" fill="{fill}" stroke="#CBD5E1" stroke-width="1.2"/>'


def cloud(x, y, s=1.0, col="#FFFFFF", op=1.0):
    return (f'<g fill="{col}" fill-opacity="{op}" stroke="#94A3B8" stroke-width="1.2"><circle cx="{n(x - 12 * s)}" cy="{n(y)}" r="{n(10 * s)}"/><circle cx="{n(x)}" cy="{n(y - 7 * s)}" r="{n(13 * s)}"/><circle cx="{n(x + 14 * s)}" cy="{n(y)}" r="{n(10 * s)}"/>'
            f'<rect x="{n(x - 20 * s)}" y="{n(y)}" width="{n(42 * s)}" height="{n(10 * s)}" stroke="none"/></g>')


def arrow(x0, y0, x1, y1, col, width=3.2, head=7.0):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * head * 0.62)} {n(hy + ny * head * 0.62)} L{n(hx - nx * head * 0.62)} {n(hy - ny * head * 0.62)} Z" fill="{col}"/>')


def icon(i):
    x0, x1 = GX[i], GX[i] + TW
    cx = x0 + TW / 2
    ground = GY + TH - 38
    o = [f'<g clip-path="url(#{U}c{i})">']
    if i == 0:                                           # heat: a sun and thermals over the sand
        o.append(f'<rect x="{n(x0)}" y="{n(ground)}" width="{n(TW)}" height="60" fill="{SAND}"/>')
        o.append(f'<circle cx="{n(cx + 22)}" cy="{n(GY + 34)}" r="14" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.6"/>')
        for k in range(10):
            a = math.radians(k * 36)
            o.append(f'<line x1="{n(cx + 22 + 18 * math.sin(a))}" y1="{n(GY + 34 - 18 * math.cos(a))}" x2="{n(cx + 22 + 25 * math.sin(a))}" y2="{n(GY + 34 - 25 * math.cos(a))}" stroke="#F59E0B" stroke-width="2.4" stroke-linecap="round"/>')
        for k, dx in enumerate((-28, -6, 16)):
            o.append(f'<path d="M{n(cx + dx)} {n(ground)} q-8 -14 0 -28 q8 -14 0 -28" fill="none" stroke="{RED}" stroke-width="2.6" stroke-linecap="round" stroke-opacity="0.8"/>')
    elif i == 1:                                         # dust and haze: a hazy band over the ground
        o.append(f'<rect x="{n(x0)}" y="{n(ground - 4)}" width="{n(TW)}" height="60" fill="#D9B97A"/>')
        o.append(f'<rect x="{n(x0)}" y="{n(ground - 34)}" width="{n(TW)}" height="40" fill="#F1E3C0" fill-opacity="0.92"/>')
        o.append(f'<rect x="{n(x0)}" y="{n(ground - 56)}" width="{n(TW)}" height="24" fill="#F1E3C0" fill-opacity="0.5"/>')
        for dx, dy, r in ((-34, -50, 1.6), (-14, -64, 1.2), (10, -46, 1.8), (30, -60, 1.2), (-26, -76, 1.4), (22, -84, 1.2)):
            o.append(f'<circle cx="{n(cx + dx)}" cy="{n(ground + dy + 34)}" r="{r}" fill="{AMBER}" fill-opacity="0.6"/>')
    elif i == 2:                                         # the shamal: wind arrows and a wall of dust
        o.append(f'<rect x="{n(x0)}" y="{n(ground)}" width="{n(TW)}" height="60" fill="{SAND}"/>')
        o.append(f'<path d="M{n(x1 - 8)} {n(ground)} L{n(x1 - 8)} {n(ground - 60)} Q{n(cx + 10)} {n(ground - 78)} {n(cx - 14)} {n(ground - 44)} Q{n(cx - 30)} {n(ground - 20)} {n(cx - 36)} {n(ground)} Z" fill="#C79A52" fill-opacity="0.85"/>')
        for k, dy in enumerate((-60, -40, -20)):
            o.append(arrow(x0 + 8, ground + dy, x0 + 46, ground + dy, INK, 3.4, 8.0))
    elif i == 3:                                         # coast: sea, an onshore arrow and fog at the shore
        o.append(f'<rect x="{n(x0)}" y="{n(ground - 8)}" width="{n(TW / 2 + 6)}" height="60" fill="#38BDF8"/><rect x="{n(cx + 6)}" y="{n(ground - 8)}" width="{n(TW / 2)}" height="60" fill="{SAND}"/>')
        o.append(f'<path d="M{n(x0)} {n(ground)} q10 -6 20 0 t20 0 t20 0 t14 0" fill="none" stroke="#FFFFFF" stroke-width="2.4"/>')
        o.append(f'<rect x="{n(x0)}" y="{n(ground - 36)}" width="{n(TW)}" height="30" fill="#F8FAFC" fill-opacity="0.85"/>')
        o.append(arrow(x0 + 10, ground - 52, x0 + 72, ground - 52, BLUE, 4.0, 9.0))
    else:                                                # convection over high ground: a mountain, a cumulonimbus and lightning
        o.append(f'<path d="M{n(x0)} {n(GY + TH)} L{n(x0)} {n(ground + 4)} L{n(cx - 20)} {n(ground - 30)} L{n(cx + 2)} {n(ground - 8)} L{n(cx + 24)} {n(ground - 36)} L{n(x1)} {n(ground + 6)} L{n(x1)} {n(GY + TH)} Z" fill="#7C6F5B" stroke="#4B4332" stroke-width="1.6"/>')
        o.append(f'<path d="M{n(cx - 24)} {n(GY + 70)} L{n(cx - 20)} {n(GY + 36)} Q{n(cx - 16)} {n(GY + 12)} {n(cx + 4)} {n(GY + 16)} Q{n(cx + 26)} {n(GY + 10)} {n(cx + 28)} {n(GY + 34)} L{n(cx + 36)} {n(GY + 70)} Z" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.4"/>')
        o.append(f'<path d="M{n(cx - 28)} {n(GY + 70)} L{n(cx + 40)} {n(GY + 70)} L{n(cx + 36)} {n(GY + 80)} L{n(cx - 24)} {n(GY + 80)} Z" fill="#64748B"/>')
        o.append(f'<path d="M{n(cx + 4)} {n(GY + 82)} L{n(cx - 4)} {n(GY + 104)} L{n(cx + 4)} {n(GY + 102)} L{n(cx - 2)} {n(GY + 124)} L{n(cx + 12)} {n(GY + 98)} L{n(cx + 4)} {n(GY + 100)} Z" fill="#FACC15" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>')
    o.append('</g>')
    return "".join(o)


def callouts():
    c = S.callout
    return "".join(c(i + 1, GX[i] + 14, GY + 14, r=9.0) for i in range(5))


def layers():
    return [H.defs(U, W, HT), background(), *[tile(i) for i in range(5)], *[icon(i) for i in range(5)], callouts()]


def plate():
    return {
        "id": "fig-14-10-arabia-weather",
        "replaces": "fig-14-10-arabia-weather.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-14-10-arabia-weather.jpg",
        "caption": "Figure 14-10. What to look for in the weather of the Arabian Peninsula: five things the physics tells you",
        "desc": ("Figure 14-10. What to look for in the weather of the Arabian Peninsula, five tiles: heat and thermals, dust and haze, the summer shamal, coastal humidity and fog, and convection over high ground. "
                 "The chapter gives no climate statistics for particular places or months, and neither does the figure."),
        "legend": [
            "Heat: high density altitude (Chapter 11) and thermals, with bumpy air at low level from late morning. Climbing higher usually brings smoother air.",
            "Dust and haze: strong wind lifts dust and a stable layer keeps it low. Haze can hide the horizon and the ground ahead even when the surface report looks acceptable.",
            "The summer shamal, and the dust storms it often fuels (Figure 14-4).",
            "Coastal humidity and fog: on the Red Sea and Gulf coasts the sea breeze brings moist air inland by day, raising the density altitude further. After clear, calm nights mist and fog are likely around dawn, and sea fog can drift ashore on an onshore wind.",
            "Convection over high ground: where moist air meets high ground, such as the south-western highlands, afternoon cumulus and thunderstorms are likely.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
