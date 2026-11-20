"""Figure 16-4. Cloud amount in oktas, eighths of the sky. Drawn again as four skies (the old figure was four flat pie symbols): above each code, a card of sky over the
desert with the cloud sprites of the library covering about that much of it (FEW one or two small cumulus, SCT three or four, BKN a deck with blue gaps, OVC a grey sky under an even
layer); under each, the okta symbol of the old figure (dark sectors the least cover for the code, light ones the range up to the most), the code and its oktas; and the bracket under
BKN and OVC, the layers that can be a ceiling. The callouts of the old figure are kept."""
import math

from figs import h_a1 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 340
CARDS = [14.0 + i * 156.0 for i in range(4)]
CW, CY, CH, GY = 144.0, 14.0, 168.0, 146.0
CODES = [("FEW", "1–2", 1, 2), ("SCT", "3–4", 3, 4), ("BKN", "5–7", 5, 7), ("OVC", "8", 8, 8)]
OVERCAST = [(0.0, "#8F99A8"), (0.7, "#A9B2BE"), (1.0, "#C6CDD6")]
BROKEN = [(0.0, "#6F8FB8"), (0.6, "#A8BFD9"), (1.0, "#E6EDF4")]


def card(i):
    x = CARDS[i]
    stops = OVERCAST if i == 3 else (BROKEN if i == 2 else H.SKY)
    body = S.glow(f"k16g{i}", x + 110, CY + 30, 70, "#FFF1CC", 0.0 if i >= 2 else 0.4)
    if i == 3:                                              # overcast: an even grey base with a soft, mottled texture, no blue anywhere
        body += (f'<defs><filter id="k16t" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.018 0.05" numOctaves="4" seed="7"/>'
                 f'<feColorMatrix values="0 0 0 0 0.93  0 0 0 0 0.95  0 0 0 0 0.98  0 0 0 1.25 -0.38"/></filter>'
                 f'<filter id="k16u" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.03 0.08" numOctaves="3" seed="11"/>'
                 f'<feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.39  0 0 0 0 0.45  0 0 0 1.1 -0.45"/></filter></defs>'
                 f'<rect x="{n(x)}" y="{n(CY)}" width="{n(CW)}" height="{n(GY - CY)}" filter="url(#k16t)" opacity="0.75"/>'
                 f'<rect x="{n(x)}" y="{n(CY)}" width="{n(CW)}" height="{n(GY - CY)}" filter="url(#k16u)" opacity="0.6"/>')
    return S.card(f"k16{i}", x, CY, CW, CH, stops, body, radius=9)


def land(i):
    x = CARDS[i]
    body = (S.land_layer(f"k16f{i}", [(x, GY - 6), (x + 40, GY - 10), (x + 90, GY - 5), (x + CW, GY - 9)], CY + CH, S.SAND["far"], opacity=0.8, haze=0.3)
            + S.land_layer(f"k16p{i}", [(x, GY), (x + CW, GY + 2)], CY + CH, S.SAND["plain"])
            + S.scrub(16 + i, x + 6, x + CW - 6, GY + 6, CY + CH - 4, 7, scale=0.9))
    if i == 3:
        body += f'<rect x="{n(x)}" y="{n(CY)}" width="{n(CW)}" height="{n(CH)}" fill="#7C8796" opacity="0.18"/>'
    return S.card_front(f"k16l{i}", x, CY, CW, CH, body, radius=9)


def clouds():
    a, b, c, d = CARDS
    return [H.cloud("cloud-cumulus-a", a + 52, 66, 44, 0.95),
            H.cloud("cloud-cumulus-b", b + 36, 54, 48, 0.95), H.cloud("cloud-cumulus-a", b + 100, 80, 52, 0.95), H.cloud("cloud-cumulus-c", b + 60, 110, 40, 0.9),
            H.cloud("cloud-stratocumulus-deck", c + 72, 50, 142, 0.97), H.cloud("cloud-stratocumulus", c + 72, 88, 142, 0.97),
            H.cloud("cloud-cumulus-b", c + 40, 122, 56, 0.9), H.cloud("cloud-cumulus-a", c + 108, 118, 50, 0.9),
            ]


def mask():
    """White over what of the sprites lies outside the four cards (a page with four rounded holes)."""
    outer = f"M0 0 H{W} V{HT} H0 Z"
    holes = ""
    r = 9.0
    for x in CARDS:
        x0, y0, x1, y1 = x, CY, x + CW, CY + CH
        holes += (f" M{n(x0 + r)} {n(y0)} H{n(x1 - r)} A{n(r)} {n(r)} 0 0 1 {n(x1)} {n(y0 + r)} V{n(y1 - r)} A{n(r)} {n(r)} 0 0 1 {n(x1 - r)} {n(y1)}"
                  f" H{n(x0 + r)} A{n(r)} {n(r)} 0 0 1 {n(x0)} {n(y1 - r)} V{n(y0 + r)} A{n(r)} {n(r)} 0 0 1 {n(x0 + r)} {n(y0)} Z")
    out = f'<path d="{outer}{holes}" fill="#ffffff" fill-rule="evenodd"/>'
    for x in CARDS:
        out += f'<rect x="{n(x)}" y="{n(CY)}" width="{n(CW)}" height="{n(CH)}" rx="9" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>'
    return out


def okta(cx, cy, lo, hi, r=26.0):
    out = [f'<circle cx="{n(cx + 1)}" cy="{n(cy + 2)}" r="{n(r)}" fill="#10233F" opacity="0.15"/>', f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="#FFFFFF"/>']
    for k in range(8):
        a0, a1 = math.radians(k * 45), math.radians((k + 1) * 45)
        p0 = (cx + r * math.sin(a0), cy - r * math.cos(a0))
        p1 = (cx + r * math.sin(a1), cy - r * math.cos(a1))
        fill = "#475569" if k < lo else ("#B6C2D2" if k < hi else None)
        if fill:
            out.append(f'<path d="M{n(cx)} {n(cy)} L{n(p0[0])} {n(p0[1])} A{n(r)} {n(r)} 0 0 1 {n(p1[0])} {n(p1[1])} Z" fill="{fill}"/>')
        out.append(f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(p0[0])}" y2="{n(p0[1])}" stroke="#334155" stroke-width="0.9"/>')
    out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="#1F2937" stroke-width="2"/>')
    return "".join(out)


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', H.defs()]
    out += [card(i) for i in range(4)]
    out += clouds()
    out += [land(i) for i in range(4)]
    out.append(mask())
    for i, (code, rng, lo, hi) in enumerate(CODES):
        cx = CARDS[i] + CW / 2
        out.append(okta(cx, 222, lo, hi))
        out.append(M.chip(cx, 266, code, "#1F2937", size=10.0) + M.chip(cx, 284, rng, "#334155", size=8.2))
    x0, x1 = CARDS[2] + 20, CARDS[3] + CW - 20
    out.append(f'<path d="M{n(x0)} 298 V306 H{n(x1)} V298" fill="none" stroke="#B91C1C" stroke-width="2"/>')
    c = S.callout
    out.append("".join(c(i + 1, CARDS[i] + 16, CY + 16) for i in range(4)) + c(5, (x0 + x1) / 2, 322, (x0 + x1) / 2, 306))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-16-04-sky-cover-oktas",
        "replaces": "fig-16-04-sky-cover-oktas.svg",
        "book_file": "plate-16-04-sky-cover-oktas.jpg",
        "caption": "Figure 16-4. Cloud amount in oktas, eighths of the sky",
        "desc": "Figure 16-4. Cloud amount in oktas, eighths of the sky",
        "legend": [
            "`FEW`: 1 to 2 oktas.",
            "`SCT`, scattered: 3 to 4 oktas.",
            "`BKN`, broken: 5 to 7 oktas.",
            "`OVC`, overcast: 8 oktas.",
            "A broken or overcast layer can be a ceiling.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-16-04-sky-cover-oktas.svg", "blank": True, "layers": layers()},
    }
