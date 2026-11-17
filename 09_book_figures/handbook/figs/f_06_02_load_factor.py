"""Figure 6-2 (new). Load factor and stall speed in a level, coordinated turn, from the table of Chapter 6 ("Load factor"): four aeroplanes seen from behind at 0, 30, 45 and 60 degrees of bank (sprite-rear, turned by the bank angle).

At each, weight (red arrow, always the same length) acts down and lift (blue arrow) along the normal to the wings; in a level turn the vertical part of lift (dashed, equal to weight) holds the aeroplane up and the horizontal part (dashed) turns it, so lift is
longer by the factor n = 1 / cos(bank): 1.00, 1.15, 1.41 and 2.0 (the chapter's table, drawn to scale: the blue arrows are 32, 37, 45 and 64 units long against a weight of 32). Under each, the stall speed of the example aeroplane, whose 1 g stall speed
is 48 kt: about 52, 57 and 68 kt in the turns (the chapter's table). Digits, G, KT and the degree sign; the words are in the legend."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 262
U = "lf6"
CX = (84.0, 244.0, 402.0, 548.0)
BANK = (0.0, 30.0, 45.0, 60.0)
N = (1.0, 1.15, 1.41, 2.0)
NTXT = ("1 G", "1.15 G", "1.41 G", "2.0 G")
STALL = ("48 KT", "52 KT", "57 KT", "68 KT")
CY = 112.0
UNIT = 32.0                                                 # the length of the weight arrow, and of lift at one g
BLUE, RED, SLATE, GREEN, AMBER = "#1D4ED8", "#B91C1C", "#475569", "#15803D", "#B45309"


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.2, height=12.0):
    w = gwidth(s, size) + 12.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.35))


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            + "".join(f'<line x1="{n(x)}" y1="24" x2="{n(x)}" y2="{HT - 22}" stroke="{SLATE}" stroke-opacity="0.18" stroke-width="1"/>' for x in (168.0, 328.0, 488.0)))


def arrow(x0, y0, x1, y1, col, width=3.4, head=8.0, dash=None, halo=True):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    out = ""
    if halo:
        out += f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="#FFFFFF" stroke-width="{n(width + 3)}" stroke-linecap="round" opacity="0.85"/>'
    out += (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"{dd}/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * head * 0.62)} {n(hy + ny * head * 0.62)} L{n(hx - nx * head * 0.62)} {n(hy - ny * head * 0.62)} Z" fill="{col}" stroke="#FFFFFF" stroke-width="0.8" stroke-linejoin="round"/>')
    return out


def panel(i):
    cx = CX[i]
    th = math.radians(BANK[i])
    L = UNIT * N[i]
    out = []
    # the weight, down from the CG
    out.append(arrow(cx, CY, cx, CY + UNIT, RED, 3.6, 8.5))
    # the lift, along the normal to the wings (toward the lower wing)
    ex, ey = cx + L * math.sin(th), CY - L * math.cos(th)
    out.append(arrow(cx, CY, ex, ey, BLUE, 3.8, 9.0))
    if i:
        # its two parts: the vertical part equals the weight, the horizontal part turns the aeroplane
        vy = CY - UNIT
        out.append(f'<line x1="{n(cx)}" y1="{n(CY)}" x2="{n(cx)}" y2="{n(vy)}" stroke="{GREEN}" stroke-width="2" stroke-dasharray="4 3"/>')
        out.append(f'<line x1="{n(cx)}" y1="{n(vy)}" x2="{n(ex)}" y2="{n(vy)}" stroke="{AMBER}" stroke-width="2" stroke-dasharray="4 3"/>'
                   f'<line x1="{n(ex)}" y1="{n(vy)}" x2="{n(ex)}" y2="{n(ey)}" stroke="{SLATE}" stroke-width="1" stroke-opacity="0.5" stroke-dasharray="2 3"/>')
    return "".join(out)


def pills():
    out = []
    for i, cx in enumerate(CX):
        out.append(pill(f"{int(BANK[i])}°", cx - 36.0, 34.0, SLATE, 7.0, 13.0))
        out.append(pill(NTXT[i], cx, 188.0, BLUE, 7.0, 14.0))
        out.append(pill(STALL[i], cx, 222.0, RED if i else SLATE, 7.0, 14.0))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join(c(i + 1, CX[i] - 64.0, 34.0, CX[i] - 52.0, 34.0, r=9.0) for i in range(4))


def sprites():
    return [A.plane(CX[i], CY - 6.0, 104.0, angle=BANK[i], name="sprite-rear") for i in range(4)]


def layers():
    return [H.defs(U, W, HT), background(), *sprites(), *[panel(i) for i in range(4)], pills(), callouts()]


def plate():
    return {
        "id": "fig-06-02-load-factor",
        "replaces": "fig-06-02-load-factor.svg",           # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-06-02-load-factor.jpg",
        "caption": "Figure 6-2. Load factor and stall speed in a level, coordinated turn: 0, 30, 45 and 60 degrees of bank",
        "desc": ("Figure 6-2. Load factor and stall speed in a level, coordinated turn, seen from behind at 0, 30, 45 and 60 degrees of bank. Weight is the same in all four; lift grows by the load factor 1 / cos(bank), "
                 "1.15, 1.41 and 2.0, and the stall speed of an aeroplane that stalls at 48 kt in level flight becomes about 52, 57 and 68 kt."),
        "legend": [
            "Wings level: lift (blue) equals weight (red), the load factor is 1 g and the stall speed is the 1 g stall speed, 48 kt in this example.",
            "30 degrees of bank: lift must be longer than weight so that its vertical part (green, dashed) still equals weight and its horizontal part (amber, dashed) turns the aeroplane. Load factor 1.15; the stall speed rises by about 7 % to about 52 kt.",
            "45 degrees of bank: load factor 1.41; the stall speed rises by about 19 % to about 57 kt.",
            "60 degrees of bank: load factor 2.0, so the wing carries twice the weight; the stall speed rises by about 41 % to about 68 kt. The blue arrows are drawn to scale against the weight.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
