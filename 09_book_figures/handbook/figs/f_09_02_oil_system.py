"""Figure 9-2 (new: the book's section on the oil system had a paragraph and a table and no figure). A wet-sump oil system.

The engine cut open from the side: the crankcase with the crankshaft in its three bearings, and under it the sump with the oil in it. The path of the oil is drawn as tubes with small
arrowheads: from the pickup and its screen in the sump to the engine-driven pump (gold: oil at rest or under suction), then under pressure (red) past the relief valve, which lets
the excess back into the sump, through the filter and the cooler, and into the gallery along the top of the crankcase, from which it reaches the bearings; drops fall back into the
sump. The filler neck with its cap and the dipstick stand on the crankcase; the pressure gauge is tapped from the pressure line and the temperature gauge has its bulb in it.
The parts and their order are those of the FAA's Pilot's Handbook of Aeronautical Knowledge, chapter 7 (Figure 7-17 and the text beside it; read again 2026-11-17): oil sump, filler cap
and dipstick, low pressure oil screen, oil pump, oil pressure relief valve, high pressure oil screen, oil cooler and filter, engine and accessory bearings, the two gauges. The drawing
is this module's own (figs/parts.py has the tubes and the gauges, figs/scene.py the callouts). No words in the picture: eleven numbered callouts."""
import math

from figs import parts as P
from figs import scene as S

n = S.n
W, HT = 640, 360
SUCTION = ("#DDA02F", "#8A5A10", "#FFEDB8")           # oil at rest or drawn by the pump: gold
PRESSURE = ("#DE5138", "#8A2110", "#FFD3C6")          # oil under pressure: red
STEEL = ("#C9D1DC", "#5A6578", "#FFFFFF")
CRANK_Y = 132.0
BEARINGS = (110.0, 210.0, 310.0)
LEVEL = 254.0                                         # the surface of the oil in the sump


def defs():
    g = S.gradient
    return ("<defs>" + g("oloil", [(0, "#F0C258", 0.96), (1, "#B67A16", 0.96)]) + g("olcase", [(0, "#7FA8E6"), (0.5, "#4F7FD0"), (1, "#2F5AA8")])
            + g("olcav", [(0, "#16314F"), (1, "#0D2238")]) + g("olfin", [(0, "#E9EEF5"), (0.5, "#B9C3D2"), (1, "#8A95A6")], 0, 0, 1, 0)
            + f'<clipPath id="olsump"><path d="{SUMP_PATH}"/></clipPath>' + "</defs>")


SUMP_PATH = "M 84,196 L 336,196 L 336,282 Q 336,304 314,304 L 106,304 Q 84,304 84,282 Z"          # the sump: the lower part of the same casing


def crankcase():
    """The crankcase cut open, and the sump under it with its oil."""
    wave = "".join(f" Q {n(92 + i * 24 + 12)},{n(LEVEL + (1.8 if i % 2 else -1.8))} {n(92 + (i + 1) * 24)},{n(LEVEL)}" for i in range(10))
    return (f'<g filter="url(#ptsh)"><rect x="70" y="64" width="280" height="142" rx="16" fill="url(#olcase)" stroke="#183A74" stroke-width="1.2"/>'
            f'<path d="{SUMP_PATH}" fill="url(#olcase)" stroke="#183A74" stroke-width="1.2"/></g>'
            f'<rect x="82" y="74" width="256" height="122" rx="10" fill="url(#olcav)"/>'
            f'<path d="M 92,190 L 328,190 L 328,281 Q 328,296 313,296 L 107,296 Q 92,296 92,281 Z" fill="url(#olcav)"/>'                    # one cavity: the crankcase opens into the sump
            f'<g clip-path="url(#olsump)"><path d="M 92,{n(LEVEL)}{wave} L 328,{n(LEVEL)} L 328,296 L 92,296 Z" fill="url(#oloil)"/>'
            f'<path d="M 94,{n(LEVEL + 1)}{wave}" fill="none" stroke="#FFF2C9" stroke-width="1.2" stroke-opacity="0.9"/></g>'
            f'<rect x="80" y="68" width="260" height="5" rx="2.5" fill="#FFFFFF" opacity="0.4"/>')


def crankshaft():
    out = []
    # the shaft and its throws, in steel, behind the bearings; the propeller flange at the left
    out.append(f'<rect x="40" y="{n(CRANK_Y - 6)}" width="320" height="12" rx="5" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="0.9"/>'
               f'<rect x="34" y="{n(CRANK_Y - 19)}" width="10" height="38" rx="3" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="0.9"/>')
    for x, down in ((148.0, 1), (172.0, -1), (248.0, -1), (272.0, 1)):
        y = CRANK_Y + (4 if down > 0 else -26)
        out.append(f'<rect x="{n(x - 9)}" y="{n(y)}" width="18" height="22" rx="4" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="0.9"/>')
    for x in BEARINGS:                                                   # a main bearing: a ring round the shaft, held by a web of the crankcase
        out.append(f'<rect x="{n(x - 15)}" y="{n(CRANK_Y + 12)}" width="30" height="{n(196 - CRANK_Y - 12)}" fill="#2B4E94" opacity="0.85"/>'
                   f'<circle cx="{n(x)}" cy="{n(CRANK_Y)}" r="15" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="1"/><circle cx="{n(x)}" cy="{n(CRANK_Y)}" r="8.4" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="0.8"/>'
                   f'<path d="M {n(x - 11)},{n(CRANK_Y - 6)} A 13,13 0 0 1 {n(x + 3)},{n(CRANK_Y - 12.5)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="1.2" stroke-linecap="round"/>')
    return "".join(out)


def gallery():
    """Oil under pressure along the top of the crankcase, and down to each bearing."""
    main = [(300, 40), (300, 86), (110, 86)]
    out = [P.tube(main, *PRESSURE, w=6.2), P.chevrons([(300, 46), (300, 86), (112, 86)], every=30)]
    for x in BEARINGS:
        out.append(P.tube([(x, 86), (x, CRANK_Y - 16)], *PRESSURE, w=4.6, shadow=False))
    return "".join(out)


def drops():
    """The oil on its way back: drops under the bearings, falling into the sump."""
    out = []
    for x in BEARINGS:
        for dx, y in ((-7.0, 160.0), (5.0, 178.0), (-3.0, 206.0), (8.0, 226.0)):
            out.append(f'<path d="M {n(x + dx)},{n(y - 5)} Q {n(x + dx + 3.4)},{n(y + 0.5)} {n(x + dx)},{n(y + 3.4)} Q {n(x + dx - 3.4)},{n(y + 0.5)} {n(x + dx)},{n(y - 5)} Z" fill="#E9B340" stroke="#8A5A10" stroke-width="0.5"/>')
    return "".join(out)


def filler():
    """The filler neck with its cap, and the dipstick down into the oil."""
    x = 165.0
    return (f'<line x1="{n(x)}" y1="28" x2="{n(x)}" y2="272" stroke="#DCE3EC" stroke-width="2.2" stroke-linecap="round"/><line x1="{n(x)}" y1="28" x2="{n(x)}" y2="272" stroke="#5A6578" stroke-width="0.6" stroke-opacity="0.7"/>'
            f'<line x1="{n(x - 3.4)}" y1="250" x2="{n(x + 3.4)}" y2="250" stroke="#16314F" stroke-width="1.1"/><line x1="{n(x - 3.4)}" y1="262" x2="{n(x + 3.4)}" y2="262" stroke="#16314F" stroke-width="1.1"/>'
            f'<g filter="url(#ptsh)"><rect x="{n(x - 8)}" y="36" width="16" height="30" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/></g>'
            f'<rect x="{n(x - 12)}" y="24" width="24" height="13" rx="4" fill="#F2C230" stroke="#8A6A00" stroke-width="1"/><rect x="{n(x - 9)}" y="26.5" width="18" height="3" rx="1.5" fill="#FFFFFF" opacity="0.55"/>')


def pickup():
    """The pickup in the sump, with its screen, and the tube to the pump."""
    line = [(222, 286), (388, 286)]
    mesh = "".join(f'<line x1="{n(200 + i * 5.5)}" y1="279" x2="{n(200 + i * 5.5)}" y2="293" stroke="#3C4658" stroke-width="0.8"/>' for i in range(8))
    return (P.tube(line, *SUCTION, w=6.2, shadow=False) + P.chevrons([(250, 286), (388, 286)], every=34, colour="#5E3D08")
            + f'<rect x="196" y="278" width="46" height="16" rx="5" fill="url(#ptsteel)" stroke="#3C4658" stroke-width="1"/>' + mesh)


def pump():
    cx, cy = 404.0, 282.0
    gear = lambda x, y: (f'<circle cx="{n(x)}" cy="{n(y)}" r="8.6" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="0.9"/>'
                         + "".join(f'<line x1="{n(x + 5.6 * math.cos(math.radians(a)))}" y1="{n(y + 5.6 * math.sin(math.radians(a)))}" x2="{n(x + 9.8 * math.cos(math.radians(a)))}" y2="{n(y + 9.8 * math.sin(math.radians(a)))}" '
                                   f'stroke="#7A5614" stroke-width="2.2" stroke-linecap="round"/>' for a in range(0, 360, 45))
                         + f'<circle cx="{n(x)}" cy="{n(y)}" r="2.4" fill="#5A4410"/>')
    return (f'<g filter="url(#ptsh)"><rect x="{n(cx - 22)}" y="{n(cy - 20)}" width="44" height="40" rx="12" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1.1"/></g>'
            f'<rect x="{n(cx - 16)}" y="{n(cy - 14)}" width="32" height="28" rx="9" fill="url(#olcav)"/>' + gear(cx - 7.4, cy) + gear(cx + 7.4, cy))


def pressure_line():
    """From the pump past the relief valve, through the filter and the cooler, and back to the engine."""
    a = [(404, 262), (404, 228), (470, 228), (470, 212)]
    b = [(470, 140), (470, 118), (540, 118), (540, 150)]
    c = [(596, 150), (596, 40), (300, 40)]
    out = [P.tube(a, *PRESSURE, w=6.2), P.chevrons(a, every=26), P.tube(b, *PRESSURE, w=6.2), P.chevrons(b, every=26), P.tube(c, *PRESSURE, w=6.2), P.chevrons(c, every=34)]
    return "".join(out)


def relief():
    """The relief valve on a branch from the pressure line back into the sump: a brass body with its spring."""
    line = [(404, 244), (330, 244)]
    x, y = 354.0, 234.0
    spring = " ".join(f"L {n(x + 3 + i * 3.4)},{n(y + (4 if i % 2 else 16))}" for i in range(1, 6))
    return (P.tube(line, *SUCTION, w=5.0, shadow=False) + P.chevrons([(398, 244), (332, 244)], every=20, size=3.0, colour="#5E3D08")
            + f'<g filter="url(#ptsh)"><rect x="{n(x)}" y="{n(y)}" width="24" height="20" rx="4" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="1"/></g>'
            f'<path d="M {n(x + 3)},{n(y + 10)} {spring}" fill="none" stroke="#5A4410" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>')


def oil_filter():
    x0, y0, w, h = 450.0, 140.0, 40.0, 72.0
    pleats = "".join(f'<line x1="{n(x0 + 6 + i * 4.0)}" y1="{n(y0 + 10)}" x2="{n(x0 + 6 + i * 4.0)}" y2="{n(y0 + h - 10)}" stroke="#8A6A2A" stroke-width="1.1" stroke-opacity="0.75"/>' for i in range(8))
    return (f'<g filter="url(#ptsh)"><rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" rx="9" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="1.1"/></g>'
            f'<rect x="{n(x0 + 4)}" y="{n(y0 + 7)}" width="{n(w - 8)}" height="{n(h - 14)}" rx="5" fill="#F3E3B4" stroke="#8A6A2A" stroke-width="0.8"/>' + pleats
            + f'<rect x="{n(x0 + 3)}" y="{n(y0 + 3)}" width="5" height="{n(h - 6)}" rx="2.5" fill="#FFFFFF" opacity="0.5"/>')


def cooler():
    x0, y0, w, h = 510.0, 150.0, 112.0, 102.0
    fins = "".join(f'<line x1="{n(x0 + 8 + i * 6.0)}" y1="{n(y0 + 8)}" x2="{n(x0 + 8 + i * 6.0)}" y2="{n(y0 + h - 8)}" stroke="#5A6578" stroke-width="1.5" stroke-opacity="0.55"/>' for i in range(17))
    coil = [(540, 150), (540, 232), (568, 232), (568, 170), (596, 170), (596, 150)]
    return (f'<g filter="url(#ptsh)"><rect x="{n(x0)}" y="{n(y0)}" width="{n(w)}" height="{n(h)}" rx="8" fill="url(#olfin)" stroke="#5A6578" stroke-width="1.1"/></g>' + fins
            + P.tube(coil, *PRESSURE, w=5.4, shadow=False) + P.chevrons(coil, every=30, size=3.2)
            + f'<rect x="{n(x0 + 4)}" y="{n(y0 + 3)}" width="{n(w - 8)}" height="4" rx="2" fill="#FFFFFF" opacity="0.6"/>')


def gauges():
    """The pressure gauge on a small tube from the pressure line; the temperature gauge with its bulb in the line."""
    px, tx, gy, r = 440.0, 530.0, 86.0, 22.0
    return (P.tube([(px, 40), (px, gy - r + 2)], *PRESSURE, w=3.2, shadow=False)
            + f'<line x1="{n(tx)}" y1="46" x2="{n(tx)}" y2="{n(gy - r + 2)}" stroke="#2F3B4E" stroke-width="1.4" stroke-dasharray="3 2"/>'
            f'<rect x="{n(tx - 4)}" y="33" width="8" height="15" rx="3.5" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="0.9"/>'
            + P.dial_vector(px, gy, r, needle_deg=28, arc=(-40, 62, "#1F9D55")) + P.dial_vector(tx, gy, r, needle_deg=-18, arc=(-52, 46, "#1F9D55")))


def callouts():
    c = S.callout
    return "".join([
        c(1, 46, 322, 122, 278),                # the sump and its oil
        c(2, 112, 22, 152, 30),                 # filler cap and dipstick
        c(3, 250, 334, 226, 296),               # the pickup and its screen
        c(4, 440, 330, 414, 300),               # the pump
        c(5, 428, 196, 379, 234),               # the relief valve
        c(6, 420, 176, 449, 176),               # the filter
        c(7, 600, 292, 586, 254),               # the cooler
        c(8, 232, 20, 232, 80),                 # oil under pressure to the bearings
        c(9, 40, 228, 100, 182),                # the oil drains back
        c(10, 392, 104, 419, 92),               # the pressure gauge
        c(11, 600, 100, 553, 90),               # the temperature gauge
    ])


def drawing():
    return crankcase() + filler() + crankshaft() + gallery() + drops() + pickup() + relief() + pressure_line() + pump() + oil_filter() + cooler() + gauges()


def plate():
    return {
        "id": "fig-09-02-oil-system",
        "replaces": "fig-09-02-oil-system.svg",                # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-09-02-oil-system.jpg",
        "caption": "Figure 9-2. A wet-sump oil system",
        "desc": "Figure 9-2. A wet-sump oil system",
        "legend": [
            "The sump under the engine: the oil lies in it (a wet sump).",
            "Filler cap and dipstick: check the level here before flight.",
            "The pickup in the sump, with its screen.",
            "The engine-driven oil pump.",
            "The pressure relief valve: it lets the excess back into the sump.",
            "The oil filter.",
            "The oil cooler.",
            "Oil under pressure, to the bearings.",
            "The oil drains back into the sump.",
            "Oil pressure gauge: it responds at once.",
            "Oil temperature gauge: it responds slowly.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": [P.defs(), defs(), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#ptbg)"/>', drawing(), callouts()]},
    }
