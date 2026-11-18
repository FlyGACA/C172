"""Figure 19-1 (new). The rules of the first section of Chapter 19, as six tiles: section 91.97 (a), (b), (e) and (g), and the controlled-flight rules of sections 91.95, 91.127(c) and 91.99(f).

1 discipline and standard phraseology (a headset and a speech bubble with ICAO); 2 the first call (a tower, the aeroplane and the four things it says as four dots); 3 English or Arabic (two speech bubbles, EN and AR); 4 MAYDAY and PAN PAN at the start of the first call;
5 a controlled flight: continuous watch, and in Class D two-way contact before entering (a cylinder of airspace marked D, arrows both ways); 6 no taxiing on the manoeuvring area without a clearance (a taxiway, a stop line and the tower). Shapes, codes and the numbers of the callouts."""
from figs import h_a4 as A
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 288
U = "rt1901"
INK, SLATE, BLUE, GREEN, AMBER, RED, VIOLET = "#1E293B", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#7C3AED"
GX = (16.0, 224.0, 432.0)
GY = (16.0, 150.0)
TW, TH = 192.0, 122.0


def gwidth(s, height, spacing=0.4):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, fill, size=8.4):
    w = gwidth(text, size) + 14.0
    h = size + 8.0
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def bubble(x, y, w, h, fill="#FFFFFF", stroke=SLATE, tail="left"):
    tx = x + 16 if tail == "left" else x + w - 16
    d = -1 if tail == "left" else 1
    return (f'<path d="M{n(x + 8)} {n(y)} H{n(x + w - 8)} Q{n(x + w)} {n(y)} {n(x + w)} {n(y + 8)} V{n(y + h - 8)} Q{n(x + w)} {n(y + h)} {n(x + w - 8)} {n(y + h)} '
            f'H{n(tx + 8 if tail == "left" else tx + 4)} L{n(tx + d * 8)} {n(y + h + 10)} L{n(tx - 4 if tail == "left" else tx - 8)} {n(y + h)} H{n(x + 8)} Q{n(x)} {n(y + h)} {n(x)} {n(y + h - 8)} V{n(y + 8)} Q{n(x)} {n(y)} {n(x + 8)} {n(y)} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" filter="url(#{U}ds)"/>')


def tower(x, y, s=1.0):
    return (f'<rect x="{n(x - 4 * s)}" y="{n(y)}" width="{n(8 * s)}" height="{n(40 * s)}" rx="2" fill="#D4DAE4" stroke="{SLATE}" stroke-width="1.4"/>'
            f'<path d="M{n(x - 14 * s)} {n(y - 12 * s)} H{n(x + 14 * s)} L{n(x + 10 * s)} {n(y)} H{n(x - 10 * s)} Z" fill="#8FB4E0" stroke="{SLATE}" stroke-width="1.4"/><rect x="{n(x - 16 * s)}" y="{n(y - 16 * s)}" width="{n(32 * s)}" height="{n(5 * s)}" rx="2" fill="{SLATE}"/>')


def tiles():
    o = ""
    tones = ("blue", "slate", "sand", "red", "green", "slate")
    for i in range(6):
        o += R.tile(f"{U}t{i}", GX[i % 3], GY[i // 3], TW, TH, tones[i])
    # 1 discipline, standard phraseology
    x, y = GX[0], GY[0]
    o += (f'<path d="M{n(x + 36)} {n(y + 84)} v-10 a22 22 0 0 1 44 0 v10" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
          f'<rect x="{n(x + 28)}" y="{n(y + 78)}" width="13" height="22" rx="5" fill="{SLATE}"/><rect x="{n(x + 75)}" y="{n(y + 78)}" width="13" height="22" rx="5" fill="{SLATE}"/>')
    o += bubble(x + 96, y + 34, 80, 36) + H.glyph_text("ICAO", x + 136, y + 52, 11, BLUE, spacing=0.6)
    # 2 the first call: tower, aeroplane, four dots
    x, y = GX[1], GY[0]
    o += tower(x + 38, y + 66)
    o += bubble(x + 82, y + 26, 92, 30, tail="right")
    o += "".join(f'<circle cx="{n(x + 98 + k * 20)}" cy="{n(y + 41)}" r="6" fill="{c}"/>' for k, c in enumerate((SLATE, BLUE, VIOLET, AMBER)))
    # 3 English or Arabic
    x, y = GX[2], GY[0]
    o += bubble(x + 22, y + 40, 66, 40) + H.glyph_text("EN", x + 55, y + 60, 14, BLUE, spacing=0.6)
    o += bubble(x + 104, y + 52, 66, 40, tail="right") + H.glyph_text("AR", x + 137, y + 72, 14, GREEN, spacing=0.6)
    # 4 MAYDAY and PAN PAN
    x, y = GX[0], GY[1]
    o += pill(x + TW / 2, y + 52, "MAYDAY", RED, size=11) + pill(x + TW / 2, y + 88, "PAN PAN", AMBER, size=11)
    # 5 controlled flight, Class D: a cylinder and two-way arrows
    x, y = GX[1], GY[1]
    cx, top, bot = x + 120, y + 40, y + 102
    o += (f'<path d="M{n(cx - 52)} {n(top)} V{n(bot)} A52 12 0 0 0 {n(cx + 52)} {n(bot)} V{n(top)}" fill="{BLUE}" fill-opacity="0.18" stroke="{BLUE}" stroke-width="2"/>'
          f'<ellipse cx="{n(cx)}" cy="{n(top)}" rx="52" ry="12" fill="{BLUE}" fill-opacity="0.12" stroke="{BLUE}" stroke-width="2"/>' + pill(cx + 28, top + 30, "D", BLUE, size=10))
    o += tower(cx - 12, bot - 30, 0.7)
    o += (f'<path d="M{n(x + 30)} {n(y + 58)} h22" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/><path d="M{n(x + 56)} {n(y + 58)} l-7 -5 v10 Z" fill="{GREEN}"/>'
          f'<path d="M{n(x + 30)} {n(y + 70)} h22" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/><path d="M{n(x + 26)} {n(y + 70)} l7 -5 v10 Z" fill="{GREEN}"/>')
    # 6 no taxiing without a clearance: a taxiway, a stop line, the tower
    x, y = GX[2], GY[1]
    o += f'<rect x="{n(x + 24)}" y="{n(y + 76)}" width="{n(TW - 40)}" height="22" fill="#5B6577"/><line x1="{n(x + 28)}" y1="{n(y + 87)}" x2="{n(x + TW - 20)}" y2="{n(y + 87)}" stroke="#FACC15" stroke-width="2"/>'
    o += f'<line x1="{n(x + 120)}" y1="{n(y + 70)}" x2="{n(x + 120)}" y2="{n(y + 104)}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'
    o += tower(x + 160, y + 34, 0.8)
    return o


def sprites():
    return [A.plane(GX[1] + 156, GY[0] + 92, 36.0, name="sprite-top", angle=-90.0), A.plane(GX[1] + 66, GY[1] + 64, 30.0, name="sprite-top", angle=90.0),
            A.plane(GX[2] + 82, GY[1] + 87, 40.0, name="sprite-top", angle=90.0)]


def callouts():
    return "".join(S.callout(i + 1, GX[i % 3] + 15, GY[i // 3] + 15, r=9.5) for i in range(6))


def layers():
    return [H.defs(U, W, HT), background(), tiles(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-19-01-radio-rules",
        "replaces": "fig-19-01-radio-rules.svg",              # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-19-01-radio-rules.jpg",
        "caption": "Figure 19-1. The rules: discipline and phraseology, the first call, the languages, distress and urgency, the controlled flight and the taxi clearance",
        "desc": ("Figure 19-1. The rules of the radio as six tiles: the highest standard of discipline and ICAO standard phraseology; the contents of a first call to any ATC unit; English or Arabic; MAYDAY or PAN PAN at the start of the first distress or urgency call; "
                 "on a controlled flight a continuous watch, and in Class D two-way contact before entering; and no taxiing on the manoeuvring area of a controlled aerodrome without a clearance from the tower."),
        "legend": [
            "The highest standard of discipline; ICAO standard phraseology wherever it has been specified, and plain language only when no standard phrase serves (section 91.97(a)).",
            "A first call to any ATC unit gives the station called, your call sign, your level (with passing and cleared levels if you are not at the cleared level), your speed if ATC assigned one, and anything else the ATS authority requires.",
            "Air-ground radiotelephony is in English or Arabic.",
            "MAYDAY or PAN PAN at the start of the first distress or urgency communication.",
            "On a controlled flight, a continuous air-ground voice watch on the appropriate frequency. In Class D airspace, establish two-way contact with the ATC unit before you enter, and keep it while inside.",
            "On the manoeuvring area of a controlled aerodrome, you may not taxi without a clearance from the aerodrome control tower.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
