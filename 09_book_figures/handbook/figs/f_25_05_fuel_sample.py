"""Figure 25-5. Why water collects at the drain, and four fuel samples. Drawn again as objects (the old figure was a flat diagram); its layout, its ten callouts and its
legend are kept:

left, a fuel tank cut open on a grey card: metal walls with a lit edge, the fuel of 100LL blue with a lit surface, beads of condensed water on the walls above it, the water settled
in the low corner over the sump under a meniscus, the vent pipe, the drain valve and a clear sampler cup under it; right, on a white card, four clear sampler tubes with highlights:
clean blue fuel, fuel over a clear layer of water with a bubble, fuel with dark specks, and pale straw fuel (possibly jet fuel); a tick or a cross under each, and an arrow from the
tubes back to the drain: drain again until clean."""
from figs import scene as S

n = S.n
W, HT = 640, 340
U = "fs25"
GREEN, RED, AMBER, INK = "#047857", "#B91C1C", "#B45309", "#1F2937"
TANK = "M 40 70 L 240 70 L 240 200 L 80 220 L 40 220 Z"
FUEL = "M 40 140 L 240 140 L 240 200 L 80 220 L 40 220 Z"
WATER = "M 40 204 Q 76 200 112 204 L 80 220 L 40 220 Z"
TUBES = [350.0, 425.0, 500.0, 575.0]


def defs():
    g = S.gradient
    return (f'<defs>{g(U + "c", [(0, "#EEF2F6"), (1, "#DCE3EB")])}{g(U + "w", [(0, "#FFFFFF"), (1, "#F4F7FA")])}'
            f'{g(U + "f", [(0, "#5B92F0", 0.55), (1, "#2456C6", 0.75)])}{g(U + "j", [(0, "#F7E7B4", 0.75), (1, "#E3C77A", 0.85)])}'
            f'{g(U + "h2o", [(0, "#F2F8FF", 0.95), (1, "#D7E8F8", 0.95)])}'
            f'{g(U + "m", [(0, "#9AA5B4"), (0.5, "#6B7686"), (1, "#4A5463")], 0, 0, 1, 0)}'
            f'{g(U + "g", [(0, "#FFFFFF", 0.0), (0.18, "#FFFFFF", 0.65), (0.32, "#FFFFFF", 0.0), (0.82, "#FFFFFF", 0.0), (0.9, "#FFFFFF", 0.35), (1, "#FFFFFF", 0.0)], 0, 0, 1, 0)}'
            f'<filter id="{U}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.25"/></filter>'
            f'<filter id="{U}b"><feGaussianBlur stdDeviation="2"/></filter></defs>')


def drop(x, y, r):
    return (f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r)}" ry="{n(r * 1.15)}" fill="#DCEBFA" stroke="#5B7FA8" stroke-width="0.7"/>'
            f'<circle cx="{n(x - r * 0.35)}" cy="{n(y - r * 0.4)}" r="{n(r * 0.35)}" fill="#FFFFFF"/>')


def tank():
    out = [f'<rect x="14" y="14" width="256" height="312" rx="10" fill="url(#{U}c)" filter="url(#{U}s)"/>']
    # the shadow of the tank, its inside (the air above the fuel), the fuel, its lit surface, the water at the sump
    out.append(f'<path d="{TANK}" transform="translate(4 5)" fill="#10233F" opacity="0.25" filter="url(#{U}b)"/>')
    out.append(f'<path d="{TANK}" fill="#F8FAFC"/>')
    out.append(f'<path d="{FUEL}" fill="url(#{U}f)"/>')
    out.append(f'<path d="{WATER}" fill="url(#{U}h2o)"/><path d="M 40 204 Q 76 200 112 204" fill="none" stroke="#5B7FA8" stroke-width="1.4"/>')
    out.append('<path d="M 41 140 H 239" stroke="#BFD6FB" stroke-width="2.2"/><path d="M 41 141.6 H 239" stroke="#1D4ED8" stroke-width="0.8" opacity="0.6"/>')
    for x, y, r in ((90, 192, 3.5), (122, 182, 3.0), (106, 170, 2.5)):     # water sinking through the fuel
        out.append(drop(x, y, r))
    for x, y in ((46, 88), (46, 112), (100, 76), (160, 76), (220, 76), (234, 100), (234, 124), (130, 76)):
        out.append(drop(x, y, 3.2))
    # the metal walls: a thick casing with a lit top edge
    out.append(f'<path d="{TANK}" fill="none" stroke="url(#{U}m)" stroke-width="5" stroke-linejoin="round"/>'
               f'<path d="M 40 70 L 240 70" stroke="#E5E9EF" stroke-width="1.4"/>')
    # the vent
    out.append('<path d="M 210 70 L 210 44 L 230 34" fill="none" stroke="#475569" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
               '<path d="M 210 70 L 210 44 L 230 34" fill="none" stroke="#CBD5E1" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
    # the drain valve (brass), the drip, the sampler cup
    out.append('<rect x="53" y="220" width="14" height="14" rx="2" fill="#B88A2E" stroke="#6B4E14" stroke-width="1"/><rect x="55" y="222" width="4" height="10" fill="#E9C873" opacity="0.8"/>'
               '<path d="M 60 236 V 252" stroke="#3B6FD8" stroke-width="2" stroke-dasharray="3 3"/>')
    out.append(cup(47, 256, 26, 46, "f", water=0))
    return "".join(out)


def cup(x, y, w, h, kind, water=0, specks=False):
    """A clear sampler tube from (x, y), w wide and h deep, rounded at the bottom, filled with `kind` (f fuel, j jet fuel) to its top."""
    r = w / 2
    body = f"M {n(x)} {n(y)} L {n(x)} {n(y + h - r)} A {n(r)} {n(r)} 0 0 0 {n(x + w)} {n(y + h - r)} L {n(x + w)} {n(y)} Z"
    out = [f'<path d="{body}" transform="translate(3 4)" fill="#10233F" opacity="0.18" filter="url(#{U}b)"/>',
           f'<path d="{body}" fill="url(#{U}{kind})"/>']
    if water:
        wy = y + h - water
        wb = f"M {n(x)} {n(wy)} Q {n(x + r)} {n(wy - 5)} {n(x + w)} {n(wy)} L {n(x + w)} {n(y + h - r)} A {n(r)} {n(r)} 0 0 1 {n(x)} {n(y + h - r)} Z"
        out.append(f'<path d="{wb}" fill="url(#{U}h2o)"/><path d="M {n(x)} {n(wy)} Q {n(x + r)} {n(wy - 5)} {n(x + w)} {n(wy)}" fill="none" stroke="#5B7FA8" stroke-width="1.3"/>')
        for bx, by, br in ((x + r * 0.6, wy - 16, 4), (x + r * 1.4, wy - 30, 3), (x + r * 0.9, wy - 48, 2.5)):
            out.append(drop(bx, by, br))
    if specks:
        for bx, by, br in ((-0.48, 0.92, 2.4), (0.12, 0.98, 2.2), (0.46, 0.9, 2.5), (-0.18, 0.86, 2.0), (0.34, 0.8, 2.1), (-0.5, 0.78, 1.8), (0.0, 0.72, 2.0), (-0.3, 0.6, 1.5), (0.4, 0.55, 1.4)):
            out.append(f'<circle cx="{n(x + r + bx * r)}" cy="{n(y + by * (h - 4))}" r="{n(br)}" fill="#3A2C1E"/>')
    out.append(f'<path d="{body}" fill="url(#{U}g)"/>')
    out.append(f'<path d="M {n(x)} {n(y)} L {n(x)} {n(y + h - r)} A {n(r)} {n(r)} 0 0 0 {n(x + w)} {n(y + h - r)} L {n(x + w)} {n(y)}" fill="none" stroke="#334155" stroke-width="1.8"/>'
               f'<rect x="{n(x - 4)}" y="{n(y - 3)}" width="{n(w + 8)}" height="5" rx="2" fill="#E2E8F0" stroke="#334155" stroke-width="1.2"/>')
    return "".join(out)


def samples():
    out = [f'<rect x="292" y="14" width="334" height="312" rx="10" fill="url(#{U}w)" stroke="#CBD5E1" stroke-width="1.2" filter="url(#{U}s)"/>']
    out.append(cup(327, 70, 46, 170, "f"))
    out.append(cup(402, 70, 46, 170, "f", water=44))
    out.append(cup(477, 70, 46, 170, "f", specks=True))
    out.append(cup(552, 70, 46, 170, "j"))
    out.append(f'<path d="M 338 280 L 347 290 L 364 268" fill="none" stroke="{GREEN}" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>')
    for cx in TUBES[1:]:
        out.append(f'<path d="M {n(cx - 11)} 269 l 22 22 M {n(cx + 11)} 269 l -22 22" stroke="{RED}" stroke-width="4.4" stroke-linecap="round"/>')
    return "".join(out)


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', defs(), tank(), samples()]
    out.append(f'<path d="M 470 292 Q 470 314 446 314 L 100 314 Q 84 314 84 304" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>'
               f'<path d="M 470 292 Q 470 314 446 314 L 100 314 Q 84 314 84 304" fill="none" stroke="{AMBER}" stroke-width="2.4" stroke-linecap="round"/>'
               f'<polygon points="84,294 90,306 78,306" fill="{AMBER}" stroke="#FFFFFF" stroke-width="1"/>')
    c = S.callout
    out.append(c(1, 140, 104) + c(2, 190, 218, 112, 204) + c(3, 110, 248, 66, 230) + c(4, 190, 30, 210, 48)
               + c(5, 350, 44, 350, 68) + c(6, 425, 44, 425, 68) + c(7, 500, 44, 500, 68) + c(8, 575, 44, 575, 68)
               + c(9, 612, 300) + c(10, 540, 314, 466, 304))
    return out


def plate():
    return {
        "id": "fig-25-05-fuel-sample",
        "replaces": "fig-25-05-fuel-sample.svg",
        "book_file": "plate-25-05-fuel-sample.jpg",
        "caption": "Figure 25-5. Why water collects at the drain, and four fuel samples",
        "desc": "Figure 25-5. Why water collects at the drain, and four fuel samples",
        "legend": [
            "In a part-filled tank, moisture condenses on the walls.",
            "Water, heavier than fuel, settles at the sump.",
            "Drain valve: sample here.",
            "Vent: if blocked, the engine can stop with fuel in the tank (Chapter 9).",
            "Clean AVGAS 100LL: blue and clear.",
            "Water: a clear bubble or layer under the fuel.",
            "Sediment: dark specks.",
            "Wrong colour, no colour or a kerosene smell: possibly jet fuel. Do not fly.",
            "Look against a white background in good light.",
            "Drain again until clean; if water or dirt keeps coming, do not fly.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-25-05-fuel-sample.svg", "blank": True, "layers": layers()},
    }
