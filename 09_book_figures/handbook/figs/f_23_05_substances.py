"""Figure 23-5 (new). Alcohol, medication and psychoactive substances, from that section of Chapter 23: four tiles.

1 section 91.21(a): no crew duty under the influence of a psychoactive substance that impairs performance; no time between drinking and flying and no blood-alcohol limit in the GACAR, the test is impairment (a glass and a capsule under a red stop sign);
2 section 91.21(c): a test on request, and the results of tests taken within 4 hours after acting as crew (a sample tube and a clock, 4 H); 3 alcohol: more than 16 hours in the body, inner-ear disturbance up to 48 hours (a time line from the last drink);
4 medication: no medicine until the AME agrees, and never the first doses of a new one (a medicine box, an arrow to a stethoscope, a tick). Shapes, the hours and the numbers of the callouts."""
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 262
U = "sb23"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
TW, TH = 300.0, 112.0
GX = (16.0, 324.0)
GY = (16.0, 136.0)


def gwidth(s, height, spacing=0.4):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, fill, size=8.5):
    w = gwidth(text, size) + 12.0
    h = size + 7.0
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.3"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def glass(cx, cy, s=1.0):
    return (f'<path d="M{n(cx - 14 * s)} {n(cy - 22 * s)} L{n(cx + 14 * s)} {n(cy - 22 * s)} L{n(cx + 10 * s)} {n(cy + 22 * s)} L{n(cx - 10 * s)} {n(cy + 22 * s)} Z" fill="#F1F5F9" stroke="{SLATE}" stroke-width="2.2" filter="url(#{U}ds)"/>'
            f'<path d="M{n(cx - 12.4 * s)} {n(cy - 4 * s)} L{n(cx + 12.4 * s)} {n(cy - 4 * s)} L{n(cx + 10 * s)} {n(cy + 22 * s)} L{n(cx - 10 * s)} {n(cy + 22 * s)} Z" fill="#D97706" fill-opacity="0.85"/>')


def capsule(cx, cy, angle=-35):
    return (f'<g transform="rotate({angle} {n(cx)} {n(cy)})"><rect x="{n(cx - 24)}" y="{n(cy - 11)}" width="48" height="22" rx="11" fill="#F8FAFC" stroke="{SLATE}" stroke-width="2.2" filter="url(#{U}ds)"/>'
            f'<path d="M{n(cx)} {n(cy - 11)} h13 a11 11 0 0 1 0 22 h-13 Z" fill="{BLUE}"/></g>')


def tick(cx, cy, r=13, col=GREEN):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{r}" fill="#FFFFFF" stroke="{col}" stroke-width="2.6" filter="url(#{U}ds)"/>'
            f'<path d="M{n(cx - r * 0.45)} {n(cy)} l{n(r * 0.3)} {n(r * 0.34)} l{n(r * 0.58)} {n(-r * 0.66)}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')


def tile1():                                            # under the influence: no crew duty
    x, y = GX[0], GY[0]
    cx, cy = x + TW / 2 + 8, y + TH / 2 + 2
    o = R.tile(f"{U}t1", x, y, TW, TH, "red") + glass(cx - 34, cy) + capsule(cx + 30, cy + 4)
    o += f'<circle cx="{n(cx)}" cy="{n(cy)}" r="44" fill="none" stroke="{RED}" stroke-width="6"/><line x1="{n(cx - 31)}" y1="{n(cy + 31)}" x2="{n(cx + 31)}" y2="{n(cy - 31)}" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>'
    return o


def tile2():                                            # a test on request: within 4 hours
    x, y = GX[1], GY[0]
    cx, cy = x + TW / 2 + 8, y + TH / 2 + 2
    o = R.tile(f"{U}t2", x, y, TW, TH, "blue")
    tx = cx - 58                                        # a sample tube in a stand
    o += (f'<rect x="{n(tx - 9)}" y="{n(cy - 34)}" width="18" height="62" rx="9" fill="#F8FAFC" stroke="{SLATE}" stroke-width="2.2" filter="url(#{U}ds)"/>'
          f'<path d="M{n(tx - 7)} {n(cy + 2)} h14 v17 a7 7 0 0 1 -14 0 Z" fill="#DC2626" fill-opacity="0.75"/><rect x="{n(tx - 11)}" y="{n(cy - 40)}" width="22" height="9" rx="3" fill="{BLUE}"/>')
    kx = cx + 8                                         # a clock: four hours of its face shaded
    import math
    a0, a1 = -90.0, -90.0 + 120.0
    p0 = (kx + 30 * math.cos(math.radians(a0)), cy + 30 * math.sin(math.radians(a0)))
    p1 = (kx + 30 * math.cos(math.radians(a1)), cy + 30 * math.sin(math.radians(a1)))
    o += (f'<circle cx="{n(kx)}" cy="{n(cy)}" r="34" fill="#FFFFFF" stroke="{SLATE}" stroke-width="3" filter="url(#{U}ds)"/>'
          f'<path d="M{n(kx)} {n(cy)} L{n(p0[0])} {n(p0[1])} A30 30 0 0 1 {n(p1[0])} {n(p1[1])} Z" fill="{BLUE}" fill-opacity="0.28"/>')
    for k in range(12):
        a = math.radians(k * 30 - 90)
        o += f'<line x1="{n(kx + 26 * math.cos(a))}" y1="{n(cy + 26 * math.sin(a))}" x2="{n(kx + 31 * math.cos(a))}" y2="{n(cy + 31 * math.sin(a))}" stroke="{SLATE}" stroke-width="1.8"/>'
    o += (f'<line x1="{n(kx)}" y1="{n(cy)}" x2="{n(kx)}" y2="{n(cy - 22)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
          f'<line x1="{n(kx)}" y1="{n(cy)}" x2="{n(p1[0] * 0.62 + kx * 0.38)}" y2="{n(p1[1] * 0.62 + cy * 0.38)}" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/><circle cx="{n(kx)}" cy="{n(cy)}" r="3.2" fill="{INK}"/>')
    o += pill(kx + 64, cy, "4 H", BLUE, size=10)
    return o


def tile3():                                            # alcohol: a time line from the last drink
    x, y = GX[0], GY[1]
    o = R.tile(f"{U}t3", x, y, TW, TH, "sand")
    x0, x1, ly = x + 76, x + TW - 24, y + 66
    k = (x1 - x0) / 48.0
    o += glass(x + 46, y + 58, 0.9)
    o += (f'<defs><linearGradient id="{U}tl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{RED}"/><stop offset="{n(16 / 48)}" stop-color="{AMBER}"/><stop offset="1" stop-color="#FCD34D"/></linearGradient></defs>'
          f'<rect x="{n(x0)}" y="{n(ly - 8)}" width="{n(x1 - x0)}" height="16" rx="8" fill="url(#{U}tl)" stroke="#FFFFFF" stroke-width="1.4" filter="url(#{U}ds)"/>')
    for h, lab, col in ((16, "16 H", RED), (48, "48 H", AMBER)):
        xx = x0 + h * k
        o += f'<line x1="{n(xx)}" y1="{n(ly - 22)}" x2="{n(xx)}" y2="{n(ly + 12)}" stroke="{INK}" stroke-width="2.2"/>' + pill(min(xx, x1 - 18), ly - 32, lab, col)
    return o


def tile4():                                            # medication: the AME first
    x, y = GX[1], GY[1]
    cx, cy = x + TW / 2 + 8, y + TH / 2 + 2
    o = R.tile(f"{U}t4", x, y, TW, TH, "green")
    bx = cx - 92                                        # a medicine box with a cross
    o += (f'<rect x="{n(bx)}" y="{n(cy - 20)}" width="54" height="40" rx="4" fill="#FFFFFF" stroke="{SLATE}" stroke-width="2.2" filter="url(#{U}ds)"/>'
          f'<rect x="{n(bx + 21)}" y="{n(cy - 12)}" width="12" height="24" fill="{GREEN}"/><rect x="{n(bx + 15)}" y="{n(cy - 6)}" width="24" height="12" fill="{GREEN}"/>')
    o += capsule(bx + 50, cy + 22, angle=-20)
    o += f'<line x1="{n(cx - 22)}" y1="{n(cy)}" x2="{n(cx + 8)}" y2="{n(cy)}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><path d="M{n(cx + 16)} {n(cy)} L{n(cx + 6)} {n(cy - 7)} L{n(cx + 6)} {n(cy + 7)} Z" fill="{INK}"/>'
    sx = cx + 46                                        # a stethoscope
    o += (f'<path d="M{n(sx - 14)} {n(cy - 30)} v14 a14 14 0 0 0 28 0 v-14" fill="none" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>'
          f'<path d="M{n(sx)} {n(cy - 2)} v10 a12 12 0 0 0 24 0 v-4" fill="none" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>'
          f'<circle cx="{n(sx + 24)}" cy="{n(cy + 1)}" r="8" fill="#CBD5E1" stroke="{INK}" stroke-width="2.6"/>'
          f'<circle cx="{n(sx - 14)}" cy="{n(cy - 32)}" r="3" fill="{INK}"/><circle cx="{n(sx + 14)}" cy="{n(cy - 32)}" r="3" fill="{INK}"/>')
    o += tick(sx + 70, cy - 2)
    return o


def callouts():
    c = S.callout
    return "".join(c(i + 1, GX[i % 2] + 15, GY[i // 2] + 15, r=9.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), background(), tile1(), tile2(), tile3(), tile4(), callouts()]


def plate():
    return {
        "id": "fig-23-05-substances",
        "replaces": "fig-23-05-substances.svg",            # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-23-05-substances.jpg",
        "caption": "Figure 23-5. Alcohol, medication and psychoactive substances: the rule, the test, the hours alcohol lasts, and the AME first",
        "desc": ("Figure 23-5. Alcohol, medication and psychoactive substances in four tiles: no crew duty under the influence of a psychoactive substance that impairs performance, with no time limit and no blood-alcohol limit in the GACAR; "
                 "a test on request, and the results of tests taken within 4 hours after acting as crew; alcohol in the body for more than 16 hours and inner-ear disturbance for up to 48 hours; and no medicine until the AME agrees."),
        "legend": [
            "No one may act as a crew member while under the influence of a psychoactive substance that impairs human performance (section 91.21(a)). The GACAR sets no time between drinking and flying and no blood-alcohol limit: the test is impairment.",
            "A crew member must submit to a test on the request of an authorized law enforcement officer, and may have to furnish to GACA the results of tests taken within 4 hours after acting as crew (section 91.21(c)).",
            "Alcohol: impairment outlasts the feeling of being sober. Considerable amounts can remain in the body for more than 16 hours, and inner-ear disturbance and disorientation can last up to 48 hours; altitude multiplies the effect.",
            "Medication: fly on no medicine, prescribed or over the counter, until your AME has agreed it is compatible with flying, and never on the first doses of a new one (an educational rule of thumb).",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
