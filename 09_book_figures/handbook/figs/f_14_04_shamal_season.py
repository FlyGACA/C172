"""Figure 14-4. The summer shamal: season, direction, dust threshold and daily peak. Drawn again as four instrument cards on a warm ground, with the old figure's content and places and no
geography it did not have: the months as a calendar strip with the season shaded amber and the two dust events marked; the direction as a compass dial with a lit arrow from the
northwest; the wind speed as a gauge whose lit range starts at 11 m/s; the hour of the day as a day arc with the sun at noon. Every number and callout of the old figure is kept
(figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S

MONTHS = [(40.0, 47.6), (87.6, 43.0), (130.5, 47.6), (178.1, 46.0), (224.1, 47.6), (271.7, 46.0), (317.7, 47.6), (365.3, 47.6), (412.8, 46.0), (458.8, 47.6), (506.4, 46.0), (552.4, 47.6)]
AMBER = ("#FFC24D", "#E8860E")
LIGHT = "#C9D6EE"


def pol(cx, cy, r, std_deg):
    """A point at `std_deg` degrees counterclockwise from the right (the page's y is down)."""
    return cx + r * math.cos(math.radians(std_deg)), cy - r * math.sin(math.radians(std_deg))


def sector(cx, cy, r0, r1, a0, a1):
    """The path of a ring sector between radii r0 and r1, from the standard angle a0 to a1 (a0 > a1: clockwise on the page)."""
    p0, p1, p2, p3 = pol(cx, cy, r1, a0), pol(cx, cy, r1, a1), pol(cx, cy, r0, a1), pol(cx, cy, r0, a0)
    large = 1 if abs(a0 - a1) > 180 else 0
    return f"M {S.n(p0[0])},{S.n(p0[1])} A {r1},{r1} 0 {large} 1 {S.n(p1[0])},{S.n(p1[1])} L {S.n(p2[0])},{S.n(p2[1])} A {r0},{r0} 0 {large} 0 {S.n(p3[0])},{S.n(p3[1])} Z"


def ground():
    return (f'<defs>{S.gradient("s4g", [(0, "#F6ECD3"), (1, "#E4D1A6")])}</defs><rect x="0" y="0" width="640" height="290" fill="url(#s4g)"/>'
            '<defs><filter id="s4n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/>'
            '<feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.34  0 0 0 0 0.2  0 0 0 0.35 -0.08"/></filter></defs><rect x="0" y="0" width="640" height="290" filter="url(#s4n)" opacity="0.5"/>')


def calendar():
    out = [H.glass("s4a", 8, 12, 624, 144, r=12, top="#27395E", bottom="#0F182B")]
    out.append('<defs><filter id="s4b" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="3.2"/></filter>' + S.gradient("s4t", [(0, "#34476F"), (1, "#1A2744")]) + S.gradient("s4u", [(0, "#2B3C61"), (1, "#16213A")]) + S.gradient("s4s", [(0, "#FFD27A"), (0.5, "#F5A623"), (1, "#D9730D")]) + '</defs>')
    for i, (x, w) in enumerate(MONTHS):
        out.append(f'<rect x="{S.n(x + 0.9)}" y="64" width="{S.n(w - 1.8)}" height="30" rx="4" fill="url(#{"s4t" if i % 2 == 0 else "s4u"})" stroke="#FFFFFF" stroke-opacity="0.14" stroke-width="0.8"/>'
                   f'<rect x="{S.n(x + 2.2)}" y="64.8" width="{S.n(w - 4.4)}" height="1.2" rx="0.6" fill="#FFFFFF" opacity="0.22"/>')
    # the season shaded over the strip (a lit band), a lit bar under it, the two edges
    out.append('<rect x="268.6" y="64" width="119.7" height="30" rx="4" fill="#FFB020" opacity="0.62" style="mix-blend-mode:screen"/>')
    out.append('<rect x="268.6" y="102" width="119.7" height="18" rx="4" fill="#FFA21C" opacity="0.8" filter="url(#s4b)"/>')
    out.append('<rect x="268.6" y="102" width="119.7" height="18" rx="4" fill="url(#s4s)" stroke="#FFE7B3" stroke-opacity="0.9" stroke-width="0.9"/><rect x="271" y="103.6" width="115" height="2.2" rx="1.1" fill="#FFFFFF" opacity="0.55"/>')
    for x in (268.6, 388.3):
        out.append(f'<line x1="{x}" y1="60" x2="{x}" y2="120" stroke="#FFB020" stroke-width="4" opacity="0.7" filter="url(#s4b)"/><line x1="{x}" y1="60" x2="{x}" y2="120" stroke="#FFD27A" stroke-width="1.6"/>')
    for i, (x, w) in enumerate(MONTHS):
        inside = 268.6 <= x + w / 2 <= 388.3
        out.append(H.text(x + w / 2, 84.2, str(i + 1), 12, "#FFFFFF" if inside else LIGHT, "bold", "middle", halo="#17233F"))
    out.append(H.text(264.6, 134, "30/5", 11, "#FFC24D", "bold", "end") + H.text(392.3, 134, "16/8", 11, "#FFC24D", "bold", "start"))
    # the two dust events: marks pointing at the strip
    for x, lab in ((211.8, "23/4"), (360.7, "28–30/7")):
        out.append(f'<polygon points="{x - 6},46 {x + 6},46 {x},58" fill="#FFE9B0" stroke="#FFFFFF" stroke-width="0.8" stroke-linejoin="round"/>')
        out.append(H.text(x, 40, lab, 10.5, "#F4E7C8", "bold", "middle"))
    return "".join(out)


def compass():
    cx, cy, r = 110.0, 229.0, 46.0
    out = [H.glass("s4c", 8, 160, 196, 120, r=12, top="#27395E", bottom="#0F182B")]
    out.append(f'<defs><radialGradient id="s4f" cx="0.4" cy="0.35" r="0.85"><stop offset="0" stop-color="#2C4272"/><stop offset="1" stop-color="#0D1730"/></radialGradient>'
               f'{S.gradient("s4r", [(0, "#DDE6F5"), (0.5, "#8F9DB8"), (1, "#4A5671")], cx - r, cy - r, cx + r, cy + r, "userSpaceOnUse")}'
               '<filter id="s4w" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.6"/></filter></defs>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 4.4}" fill="url(#s4r)" stroke="#05080F" stroke-opacity="0.6" stroke-width="1"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#s4f)" stroke="#05080F" stroke-width="1.2"/>')
    out.append(f'<path d="M {cx - 40},{cy - 18} A 44,44 0 0 1 {cx - 12},{cy - 42}" fill="none" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="1.6" stroke-linecap="round"/>')
    for k in range(24):
        a = k * 15
        major = a % 45 == 0
        x0, y0 = pol(cx, cy, r - (7 if major else 3.6), 90 - a)
        x1, y1 = pol(cx, cy, r - 0.8, 90 - a)
        out.append(f'<line x1="{S.n(x0)}" y1="{S.n(y0)}" x2="{S.n(x1)}" y2="{S.n(y1)}" stroke="#DCE6F8" stroke-opacity="{0.95 if major else 0.5}" stroke-width="{1.5 if major else 0.8}" stroke-linecap="round"/>')
    # the north mark on the bezel and the two bearings
    out.append(f'<polygon points="{cx - 4.6},{cy - r - 9} {cx + 4.6},{cy - r - 9} {cx},{cy - r - 1.5}" fill="#FFD27A" stroke="#FFFFFF" stroke-width="0.7" stroke-linejoin="round"/>')
    out.append(H.text(cx, 176, "360°", 10.5, "#E6EEFC", "bold", "middle") + H.text(162, 236, "090°", 10.5, "#E6EEFC", "bold", "start"))
    # the lit arrow, from the northwest to the southeast (the old arrow: tail 71.8, 197.8, head 135.5, 261.5)
    out.append(H.ribbon("s4ar", [(71.8, 193.8), (135.5, 257.5)], width=5.2, colours=("#F29A1C", "#FFD27A"), head=2.3, casing=0.0, shadow=False, glow="#FFB020", opacity=1.0))
    return "".join(out)


def gauge():
    cx, cy = 324.0, 266.0
    R0, R1 = 62.0, 74.0
    out = [H.glass("s4d", 214, 160, 220, 120, r=12, top="#27395E", bottom="#0F182B")]
    # angle of a speed v (0 to 20 m/s) on the dial: 180 degrees at 0 down to 0 at 20
    ang = lambda v: 180.0 - 180.0 * v / 20.0
    out.append('<defs><filter id="s4gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>'
               + S.gradient("s4z", [(0, "#FFD27A"), (1, "#E8860E")]) + S.gradient("s4y", [(0, "#4A5C85"), (1, "#2A3A5E")]) + '</defs>')
    out.append(f'<path d="{sector(cx, cy, R0, R1, 180, 0)}" fill="url(#s4y)" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="0.8"/>')
    # the range above 11 m/s: a lit fan on the dial and a lit band, with dust in it
    a11 = ang(11)
    out.append(f'<defs><radialGradient id="s4fan" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{R0}"><stop offset="0" stop-color="#FFB020" stop-opacity="0"/><stop offset="1" stop-color="#FFB020" stop-opacity="0.5"/></radialGradient></defs>'
               f'<path d="M {cx},{cy} L {S.n(pol(cx, cy, R0 - 2, a11)[0])},{S.n(pol(cx, cy, R0 - 2, a11)[1])} A {R0 - 2},{R0 - 2} 0 0 1 {S.n(pol(cx, cy, R0 - 2, 0)[0])},{S.n(pol(cx, cy, R0 - 2, 0)[1])} Z" fill="url(#s4fan)"/>')
    out.append(f'<path d="{sector(cx, cy, R0, R1, a11, 0)}" fill="#FFA21C" opacity="0.8" filter="url(#s4gl)"/><path d="{sector(cx, cy, R0, R1, a11, 0)}" fill="url(#s4z)" stroke="#FFE7B3" stroke-opacity="0.9" stroke-width="0.9"/>')
    import random
    rnd = random.Random(14)
    for _ in range(46):
        a = rnd.uniform(0.6, a11 - 1.0)
        rr = rnd.uniform(R0 + 1.6, R1 - 1.6)
        x, y = pol(cx, cy, rr, a)
        out.append(f'<circle cx="{S.n(x)}" cy="{S.n(y)}" r="{S.n(rnd.uniform(0.5, 1.1))}" fill="#7A3E05" opacity="0.7"/>')
    # ticks, numerals
    for v in range(0, 21):
        major = v % 5 == 0
        x0, y0 = pol(cx, cy, R0 - (5.5 if major else 3), ang(v))
        x1, y1 = pol(cx, cy, R0 - 0.6, ang(v))
        out.append(f'<line x1="{S.n(x0)}" y1="{S.n(y0)}" x2="{S.n(x1)}" y2="{S.n(y1)}" stroke="#DCE6F8" stroke-opacity="{0.95 if major else 0.5}" stroke-width="{1.5 if major else 0.8}" stroke-linecap="round"/>')
    for v in (0, 5, 10, 15, 20):
        x, y = pol(cx, cy, R1 + 10.5, ang(v))
        out.append(H.text(x, y + 4, str(v), 11, "#E6EEFC", "bold", "middle"))
    # the threshold needle at 11 and its value
    nx, ny = pol(cx, cy, R1 + 3, a11)
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{S.n(nx)}" y2="{S.n(ny)}" stroke="#FFB020" stroke-width="5" opacity="0.8" filter="url(#s4gl)"/>'
               f'<line x1="{cx}" y1="{cy}" x2="{S.n(nx)}" y2="{S.n(ny)}" stroke="#FFD27A" stroke-width="2.4" stroke-linecap="round"/>'
               f'<circle cx="{cx}" cy="{cy}" r="5.4" fill="#16233D" stroke="#FFD27A" stroke-width="1.6"/>')
    x, y = pol(cx, cy, 44, a11 + 12)
    out.append(H.text(x, y + 4, "11", 12.5, "#FFC24D", "bold", "middle"))
    return "".join(out)


def day_arc():
    cx, cy, r = 535.0, 262.0, 54.0
    out = [H.glass("s4e", 444, 160, 188, 120, r=12, top="#27395E", bottom="#0F182B")]
    out.append(f'<defs>{S.gradient("s4k", [(0, "#0C1630"), (0.18, "#2C3F7C"), (0.38, "#8E7FB8"), (0.5, "#FFD98A"), (0.62, "#8E7FB8"), (0.82, "#2C3F7C"), (1, "#0C1630")], cx - r, 0, cx + r, 0, "userSpaceOnUse")}'
               '<filter id="s4sg" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter></defs>')
    out.append(f'<path d="M {cx - r},{cy} A {r},{r} 0 0 1 {cx + r},{cy} Z" fill="url(#s4k)" stroke="#05080F" stroke-opacity="0.5" stroke-width="1"/>')
    out.append(f'<path d="M {cx - r},{cy} A {r},{r} 0 0 1 {cx + r},{cy}" fill="none" stroke="#E6EEFC" stroke-opacity="0.9" stroke-width="1.8"/>')
    out.append(f'<line x1="{cx - r - 6}" y1="{cy}" x2="{cx + r + 6}" y2="{cy}" stroke="#E6EEFC" stroke-opacity="0.8" stroke-width="1.6"/>')
    for h in range(0, 25):
        a = 180.0 - 180.0 * h / 24.0
        major = h % 6 == 0
        x0, y0 = pol(cx, cy, r + (0 if major else 0), a)
        x1, y1 = pol(cx, cy, r - (7 if major else 3.4), a)
        out.append(f'<line x1="{S.n(x0)}" y1="{S.n(y0)}" x2="{S.n(x1)}" y2="{S.n(y1)}" stroke="#FFFFFF" stroke-opacity="{0.95 if major else 0.55}" stroke-width="{1.5 if major else 0.8}"/>')
    labels = {0: (cx - r, cy + 14), 24: (cx + r, cy + 14)}
    for h, (x, y) in labels.items():
        out.append(H.text(x, y, f"{h:02d}", 11, "#E6EEFC", "bold", "middle"))
    for h in (6, 12, 18):
        x, y = pol(cx, cy, r - 17, 180.0 - 180.0 * h / 24.0)
        out.append(H.text(x, y + 4, f"{h:02d}", 11, "#E6EEFC" if h != 12 else "#3A2A08", "bold", "middle"))
    # the peak at noon: an amber mark pointing at the arc, and the sun above it
    out.append(f'<polygon points="{cx - 7},{cy - r - 12} {cx + 7},{cy - r - 12} {cx},{cy - r - 1.5}" fill="#FFB020" stroke="#FFFFFF" stroke-width="0.9" stroke-linejoin="round"/>')
    sx, sy = cx, cy - r - 36
    out.append(f'<circle cx="{sx}" cy="{sy}" r="22" fill="#FFC24D" opacity="0.65" filter="url(#s4sg)"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<line x1="{S.n(sx + 12.5 * math.cos(a))}" y1="{S.n(sy + 12.5 * math.sin(a))}" x2="{S.n(sx + 18 * math.cos(a))}" y2="{S.n(sy + 18 * math.sin(a))}" stroke="#FFC24D" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(f'<defs><radialGradient id="s4sd" cx="0.35" cy="0.3" r="0.85"><stop offset="0" stop-color="#FFF6D2"/><stop offset="0.6" stop-color="#FFC75A"/><stop offset="1" stop-color="#F08A1C"/></radialGradient></defs>'
               f'<circle cx="{sx}" cy="{sy}" r="9.5" fill="url(#s4sd)" stroke="#FFFFFF" stroke-width="1.2"/>')
    return "".join(out), (sx, sy)


def plate():
    day, sun = day_arc()
    layers = [ground(), calendar(), compass(), gauge(), day]
    c = S.callout
    layers.append("".join([
        c(1, 22, 79, 41, 79), c(2, 328.4, 141, 328.4, 121), c(3, 177.8, 52, 204, 52), c(4, 410.7, 52, 368, 52),
        c(5, 30, 186, 75, 197), c(6, 418, 192, 376.5, 222.5), c(7, 466, 192, sun[0] - 14, sun[1] + 2),
    ]))
    return {
        "id": "fig-14-04-shamal-season",
        "replaces": "fig-14-04-shamal-season.svg",
        "book_file": "plate-14-04-shamal-season.jpg",
        "caption": "Figure 14-4. The summer shamal: season, direction, dust threshold and daily peak",
        "desc": "Figure 14-4. The summer shamal: season, direction, dust threshold and daily peak",
        "legend": [
            "Months, 1 being January.",
            "The usual summer shamal season, about 30 May to 16 August.",
            "23 April 2018: dust nearly reaches Riyadh.",
            "28–30 July 2018: the Rub' al Khali dust plume.",
            "Direction: from the northwest.",
            "Wind speed in m/s: above about 11 the wind can lift enough dust to bring visibility below 3.5 km.",
            "Hour of the day: the peak around noon.",
        ],
        "canvas": [640, 290],
        "background": "pale",
        "reskin": {"svg": "fig-14-04-shamal-season.svg", "blank": True, "layers": layers},
    }
