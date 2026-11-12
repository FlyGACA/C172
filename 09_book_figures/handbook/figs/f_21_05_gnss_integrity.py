"""Figure 21-5. GNSS satellites, integrity monitoring and what degrades the signal. Drawn again as an illustrated picture on the old figure's canvas: a sky that darkens to space over
the curve of the earth, the satellites as spacecraft (a gold body, solar panels with cells, a dish) with a glowing link line to the aeroplane (four solid, a fifth dashed, a sixth dotted,
a low one cut off by the airframe), the tower of the interference with its red waves, and the two position plots as lit displays in a dark card, one set agreeing and one not, with the
warning. Every callout of the old figure is kept (figs/h_a4.py has the parts)."""
import math
import random

from figs import h_a4 as H
from figs import scene as S

SKY = [(0.0, "#0E1B42"), (0.34, "#274F9A"), (0.62, "#5F97D6"), (0.84, "#B8D5EE"), (1.0, "#F2EBD5")]
APEX, RADIUS = 312.0, 1000.0
AIR = (218.0, 226.2)                      # where the links meet: the antenna on the roof of the aeroplane


def gy(x):
    return APEX + RADIUS - math.sqrt(RADIUS * RADIUS - (x - 320.0) ** 2)


def stars():
    rnd = random.Random(21)
    out = []
    for _ in range(70):
        x, y = rnd.uniform(4, 636), rnd.uniform(4, 150)
        out.append(f'<circle cx="{S.n(x)}" cy="{S.n(y)}" r="{S.n(rnd.uniform(0.35, 0.95))}" fill="#FFFFFF" opacity="{S.n(rnd.uniform(0.35, 0.95) * (1 - y / 190))}"/>')
    return "".join(out)


def satellite(uid, x, y, s=0.74, tilt=0.0, grey=False):
    """A navigation satellite: a gold body with a dish under it, two solar wings of cells on short booms. Returns (markup, the point under the dish where the link leaves)."""
    wing = ("#8E98AB", "#586175") if grey else ("#3169DC", "#123A92")
    gold = ("#CFD3DA", "#8D94A3") if grey else ("#F8DE9C", "#C4912C")
    cell = "#D5E3FF" if not grey else "#E4E8EF"
    out = [f'<defs>{S.gradient(uid + "w", [(0, wing[0]), (1, wing[1])], 0, 0, 1, 1)}{S.gradient(uid + "b", [(0, gold[0]), (1, gold[1])], 0, 0, 1, 1)}{S.gradient(uid + "s", [(0, gold[1]), (1, "#6B5116" if not grey else "#5C6577")], 0, 0, 1, 0)}'
           f'{S.gradient(uid + "d", [(0, "#F4F7FB"), (1, "#8A96AB")], 0, 0, 1, 0)}</defs>',
           f'<g transform="translate({S.n(x)} {S.n(y)}) rotate({S.n(tilt)}) scale({S.n(s)})">']
    for sign in (-1, 1):
        x0 = 8.5 if sign > 0 else -8.5 - 21
        out.append(f'<line x1="{S.n(sign * 6)}" y1="0" x2="{S.n(sign * 9)}" y2="0" stroke="#AEB8C9" stroke-width="1.6"/>')
        out.append(f'<rect x="{S.n(x0)}" y="-6.5" width="21" height="13" rx="0.8" fill="url(#{uid}w)" stroke="#DCE8FF" stroke-opacity="0.8" stroke-width="0.6"/>')
        for i in range(1, 4):
            out.append(f'<line x1="{S.n(x0 + i * 5.25)}" y1="-6.5" x2="{S.n(x0 + i * 5.25)}" y2="6.5" stroke="{cell}" stroke-opacity="0.55" stroke-width="0.45"/>')
        for j in (-0.5, 0.5):
            out.append(f'<line x1="{S.n(x0)}" y1="{S.n(j * 6.5)}" x2="{S.n(x0 + 21)}" y2="{S.n(j * 6.5)}" stroke="{cell}" stroke-opacity="0.45" stroke-width="0.45"/>')
        out.append(f'<path d="M {S.n(x0 + 1)},-6 L {S.n(x0 + 20)},-6" stroke="#FFFFFF" stroke-opacity="0.4" stroke-width="0.7"/>')
    # the dish under the body, the little mast on top
    out.append(f'<path d="M -4,7 L 4,7 L 7.5,12.5 L -7.5,12.5 Z" fill="url(#{uid}d)" stroke="#6B778D" stroke-width="0.5"/><ellipse cx="0" cy="12.5" rx="7.5" ry="1.9" fill="#E8EEF7" stroke="#6B778D" stroke-width="0.5"/>')
    out.append(f'<line x1="0" y1="-7" x2="0" y2="-12" stroke="#AEB8C9" stroke-width="0.9"/><circle cx="0" cy="-12.4" r="1.2" fill="#E8EEF7"/>')
    out.append(f'<rect x="-6.2" y="-7" width="12.4" height="14" rx="1.2" fill="url(#{uid}b)" stroke="#7A5C1A" stroke-opacity="0.8" stroke-width="0.6"/>'
               f'<rect x="2.4" y="-7" width="3.8" height="14" fill="url(#{uid}s)" opacity="0.55"/>'
               f'<line x1="-5.4" y1="-5.8" x2="1.8" y2="-5.8" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="0.8"/>'
               f'<rect x="-3.6" y="-2.6" width="5" height="3.4" fill="#2A3550" opacity="0.5"/>')
    out.append("</g>")
    a = math.radians(tilt)
    # the point under the dish (0, 13) in the satellite's frame, turned by the tilt and scaled
    return "".join(out), (x - 13 * s * math.sin(a), y + 13 * s * math.cos(a))


def tower():
    x, base = 330.0, gy(330)
    top = base - 42
    out = [f'<defs>{S.gradient("g5st", [(0, "#56627A"), (1, "#222B3D")], 0, 0, 1, 0)}<filter id="g5bl" x="-30%" y="-30%" width="170%" height="170%"><feGaussianBlur stdDeviation="1.6"/></filter></defs>',
           f'<ellipse cx="{S.n(x + 7)}" cy="{S.n(base + 1.2)}" rx="16" ry="2.6" fill="#3A2E1E" opacity="0.32" filter="url(#g5bl)"/>']
    out.append(f'<path d="M {S.n(x - 10)},{S.n(base)} L {S.n(x - 2.2)},{S.n(top)} L {S.n(x + 2.2)},{S.n(top)} L {S.n(x + 10)},{S.n(base)}" fill="none" stroke="#2A3448" stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round"/>')
    for k in range(1, 5):
        t0, t1 = k / 5.0, (k + 1) / 5.0
        ya, yb = base - 42 * t0, base - 42 * t1
        wa, wb = 10 - 7.8 * t0, 10 - 7.8 * t1
        out.append(f'<path d="M {S.n(x - wa)},{S.n(ya)} L {S.n(x + wb)},{S.n(yb)} M {S.n(x + wa)},{S.n(ya)} L {S.n(x - wb)},{S.n(yb)}" stroke="#3B465C" stroke-width="0.9" fill="none"/>')
    out.append(f'<line x1="{S.n(x)}" y1="{S.n(top)}" x2="{S.n(x)}" y2="{S.n(top - 9)}" stroke="#2A3448" stroke-width="1.8" stroke-linecap="round"/>')
    out.append(f'<rect x="{S.n(x - 5)}" y="{S.n(top - 12)}" width="10" height="5" rx="1" fill="#F3F6FA" stroke="#7B879C" stroke-width="0.7"/><circle cx="{S.n(x)}" cy="{S.n(top - 13.5)}" r="1.5" fill="#FF6B5E"/>')
    # the red waves above it: three arcs with a glow
    cy = top - 8
    glow, core = [], []
    for r in (14, 26, 38):
        d = f"M {S.n(x - r * math.cos(math.radians(32)))},{S.n(cy - r * math.sin(math.radians(32)))} A {r},{r} 0 0 1 {S.n(x + r * math.cos(math.radians(32)))},{S.n(cy - r * math.sin(math.radians(32)))}"
        glow.append(f'<path d="{d}" fill="none" stroke="#FF4B3E" stroke-width="5.2" stroke-linecap="round"/>')
        core.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="4.6" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#D8261D" stroke-width="2.6" stroke-linecap="round"/>')
    out.append(f'<g filter="url(#g5bl)" opacity="0.75">{"".join(glow)}</g>' + "".join(core))
    return "".join(out), (x, cy - 38)


def scope(uid, cx, cy, r, dots, far=None):
    """A position plot on a lit round display: rings and a cross, the fixes as green dots with a glow, one far fix in red with its dashed line."""
    out = [f'<defs><radialGradient id="{uid}r" cx="0.4" cy="0.35" r="0.85"><stop offset="0" stop-color="#1E4A6C"/><stop offset="1" stop-color="#0A1830"/></radialGradient>'
           f'<filter id="{uid}b" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2"/></filter></defs>']
    out.append(f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{S.n(r + 4)}" fill="#0A1020" stroke="#8FA6C8" stroke-opacity="0.55" stroke-width="1"/>')
    out.append(f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{S.n(r)}" fill="url(#{uid}r)" stroke="#4FD9A1" stroke-width="1.8"/>')
    out.append(f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{S.n(r * 0.5)}" fill="none" stroke="#9CC3E8" stroke-opacity="0.35" stroke-width="0.7"/>')
    out.append(f'<line x1="{S.n(cx - r)}" y1="{S.n(cy)}" x2="{S.n(cx + r)}" y2="{S.n(cy)}" stroke="#9CC3E8" stroke-opacity="0.25" stroke-width="0.6"/><line x1="{S.n(cx)}" y1="{S.n(cy - r)}" x2="{S.n(cx)}" y2="{S.n(cy + r)}" stroke="#9CC3E8" stroke-opacity="0.25" stroke-width="0.6"/>')
    if far:
        out.append(f'<line x1="{S.n(far[0])}" y1="{S.n(far[1])}" x2="{S.n(far[2])}" y2="{S.n(far[3])}" stroke="#FF6A5E" stroke-width="1.5" stroke-dasharray="3 3" stroke-linecap="round"/>')
    for dx, dy in dots:
        out.append(f'<circle cx="{S.n(cx + dx)}" cy="{S.n(cy + dy)}" r="5" fill="#4FF0AE" opacity="0.8" filter="url(#{uid}b)"/><circle cx="{S.n(cx + dx)}" cy="{S.n(cy + dy)}" r="3.6" fill="#6CF5BE" stroke="#E8FFF4" stroke-width="0.7"/>')
    if far:
        out.append(f'<circle cx="{S.n(far[2])}" cy="{S.n(far[3])}" r="7" fill="#FF4B3E" opacity="0.8" filter="url(#{uid}b)"/><circle cx="{S.n(far[2])}" cy="{S.n(far[3])}" r="4.6" fill="#FF6A5E" stroke="#FFE0DC" stroke-width="0.8"/>')
    return "".join(out)


def plate():
    ground, _ = H.planet("g5g", 0, 640, APEX, 390, RADIUS, colours=("#E9D8AC", "#BFA26C"), seed=5, scrub_count=26)
    sats = {1: (60, 104), 2: (135, 62), 3: (232, 46), 4: (318, 70), 5: (378, 122), 6: (28, 175), 7: (398, 214)}
    sat_markup, ends = [], {}
    for k, (sx, sy) in sats.items():
        tilt = -max(-16, min(16, 0.25 * math.degrees(math.atan2(AIR[0] - sx, AIR[1] - sy))))      # (turned a little toward the aeroplane)
        m, end = satellite(f"g5s{k}", sx, sy, 0.74, tilt, grey=(k == 7))
        sat_markup.append(m)
        ends[k] = end
    links = []
    for k in (1, 2, 3, 4):
        links.append(H.link(f"g5l{k}", ends[k], AIR, "#E8FBFF", "#52D8FF", 1.7))
    links.append(H.link("g5l5", ends[5], AIR, "#CFE0FF", "#5C8CFF", 1.8, "7 4.5", 6.0))
    links.append(H.link("g5l6", ends[6], AIR, "#C9FFE6", "#35E6A0", 2.0, "0.1 4.6", 6.0))
    # the low satellite: a beam that breaks before it reaches the aeroplane
    p7 = ends[7]
    links.append(H.link("g5l7", (p7[0] - 3, p7[1] + 1), (304, 227.4), "#E1E7F1", "#9AA6BC", 1.9, "6 4", 4.6, 1.0))
    links.append(H.link("g5l8", (284, 228.6), (256, 230.2), "#E1E7F1", "#9AA6BC", 1.6, "3 3.6", 3.6, 0.8))
    x_mark = ('<g stroke-linecap="round"><line x1="234" y1="224.5" x2="246" y2="236.5" stroke="#FFFFFF" stroke-width="5.8"/><line x1="234" y1="236.5" x2="246" y2="224.5" stroke="#FFFFFF" stroke-width="5.8"/>'
              '<line x1="234" y1="224.5" x2="246" y2="236.5" stroke="#D8261D" stroke-width="2.8"/><line x1="234" y1="236.5" x2="246" y2="224.5" stroke="#D8261D" stroke-width="2.8"/></g>')
    tower_markup, _ = tower()
    node = (f'<defs><radialGradient id="g5n"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/><stop offset="0.35" stop-color="#9FE6FF" stop-opacity="0.55"/><stop offset="1" stop-color="#52D8FF" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{AIR[0]}" cy="{AIR[1]}" r="13" fill="url(#g5n)"/>')
    orbit = '<path d="M20,150 Q210,-20 400,150" fill="none" stroke="#DCE8FF" stroke-opacity="0.42" stroke-width="1.1" stroke-dasharray="6 5"/>'
    # the right-hand card: two position plots and the warning
    card = [H.glass("g5c", 430, 20, 196, 352, r=12, top="#1F2E4B", bottom="#0C1527", opacity=0.97)]
    card.append(scope("g5p1", 528, 104, 40, [(-6, -4), (5, -7), (7, 5), (-4, 8), (1, 1)]))
    card.append(f'<line x1="446" y1="188" x2="610" y2="188" stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="1"/>')
    card.append(scope("g5p2", 520, 274, 40, [(-6, -4), (5, -7), (7, 5), (-4, 8)], far=(528, 268, 588, 226)))
    card.append('<defs><filter id="g5w" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>' + S.gradient("g5wg", [(0, "#FFC46B"), (1, "#D9731A")]) + '</defs>'
                '<rect x="504" y="324" width="32" height="32" rx="7" fill="#FFA43A" opacity="0.7" filter="url(#g5w)"/>'
                '<rect x="506" y="326" width="28" height="28" rx="6" fill="url(#g5wg)" stroke="#FFEBC6" stroke-width="1"/>'
                '<rect x="518" y="331" width="4" height="12" rx="2" fill="#FFFFFF"/><circle cx="520" cy="348" r="2.4" fill="#FFFFFF"/>')
    layers = [
        S.sky("g5k", 0, 0, 640, 390, SKY), stars(), orbit,
        ground,
        tower_markup,
        *sat_markup,
        *links, node, x_mark,
        H.plane(208, 234, 76, 0, name="sprite-side"),
        "".join(card),
    ]
    c = S.callout
    lerp = lambda p0, p1, t: (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
    t1, t2, t3 = lerp(ends[2], AIR, 0.5), lerp(ends[5], AIR, 0.42), lerp(ends[6], AIR, 0.5)
    t4 = lerp((p7[0] - 3, p7[1] + 1), (304, 227.4), 0.8)
    top = gy(330) - 42 - 8
    t5 = (330 + 26 * math.cos(math.radians(42)), top - 26 * math.sin(math.radians(42)))
    layers.append("".join([
        c(1, 178, 116, *t1), c(2, 396, 96, *t2), c(3, 52, 214, *t3), c(4, 334, 192, *t4), c(5, 384, 268, *t5),
        c(6, 466, 52, 494, 80), c(7, 466, 222, 486, 252),
    ]))
    return {
        "id": "fig-21-05-gnss-integrity",
        "replaces": "fig-21-05-gnss-integrity.svg",
        "book_file": "plate-21-05-gnss-integrity.jpg",
        "caption": "Figure 21-5. GNSS satellites, integrity monitoring and what degrades the signal",
        "desc": "Figure 21-5. GNSS satellites, integrity monitoring and what degrades the signal",
        "legend": [
            "Four satellites: a position in three dimensions and the time.",
            "A fifth, or four and the barometric altitude: a faulty satellite can be detected.",
            "A sixth, or five and the barometric altitude: it can be excluded.",
            "A low satellite hidden by the airframe or a bank.",
            "Interference: a stronger signal on the same frequency drowns the weak satellite signals.",
            "Positions from different sets of satellites agree: the position can be trusted.",
            "One set disagrees: a receiver with integrity monitoring warns you; one without may not.",
        ],
        "canvas": [640, 390],
        "background": "pale",
        "reskin": {"svg": "fig-21-05-gnss-integrity.svg", "blank": True, "layers": layers},
    }
