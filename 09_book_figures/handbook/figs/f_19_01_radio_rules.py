"""Figure 19-1 (new; redrawn in the upgrade round around a render of the model's radio stack). The rules of the first section of Chapter 19: section 91.97 (a), (b), (e) and (g),
and the controlled-flight rules of sections 91.95, 91.127(c) and 91.99(f).

On the model's audio panel and COM/NAV radios: 1 discipline and standard phraseology (ICAO); 2 the first call (the four things it says as four dots, from the COMM window); 4 MAYDAY and PAN PAN.
Beside it: 3 English or Arabic (two speech bubbles); 5 a controlled flight, Class D: two-way contact before entering (a cylinder of airspace about the tower, arrows both ways);
6 no taxiing on the manoeuvring area without a clearance (a taxiway from above, the holding position marking with a red stop bar, and the aeroplane stopped before it). Shapes, codes and the numbers of the callouts."""
from figs import h_a4 as A
from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

n = S.n
W, HT = 640, 392
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


import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.28}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}


def anchors(name):
    with open(os.path.join(HERE, "renders", name + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    return d["size"], d["anchors"]


def card(uid, x, y, w, h, fill="#FFFFFF"):
    return (f'<defs><filter id="{uid}f" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="2" stdDeviation="2.6" flood-color="#10233F" flood-opacity="0.26"/></filter>'
            f'<clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="10"/></clipPath></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="10" fill="{fill}" filter="url(#{uid}f)"/><g clip-path="url(#{uid}c)">')


def close(x, y, w, h):
    return f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.8"/>'


def leader(p, q, col):
    return (f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="#FFFFFF" stroke-width="4.2" stroke-linecap="round"/>'
            f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="{col}" stroke-width="2" stroke-linecap="round"/>'
            f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="3.4" fill="{col}" stroke="#FFFFFF" stroke-width="1.4"/>')


POS = {}
RX, RY, RW, RH = 12.0, 12.0, 292.0, 368.0                    # the card of the radio stack


def radios():
    """The model's radio stack, cropped to the audio panel and the two COM/NAV radios: callouts 1 (phraseology), 2 (the first call) and 4 (MAYDAY, PAN PAN)."""
    (pw, ph), a = anchors("panel-19-01-radios")
    sw = RW / 0.52
    sh = sw * ph / pw
    x0 = RX - 0.24 * sw                                       # the window starts at 24 % of the picture's width and 21 % of its height
    y0 = RY - 0.21 * sh
    at = lambda fx, fy: (x0 + fx * sw, y0 + fy * sh)
    out = [card(f"{U}r", RX, RY, RW, RH, "#1F2125"), {"name": "panel-19-01-radios", "at": [x0 + sw / 2, y0 + sh / 2], "width": sw}]
    over = ""
    au = at(*a["audio"])
    over += bubble(RX + RW - 108, RY + 14, 92, 34, fill="#FFFFFF", stroke=BLUE, tail="left") + H.glyph_text("ICAO", RX + RW - 62, RY + 31, 11, BLUE, spacing=0.6)
    c1 = at(0.397, 0.461)                                     # the right edge of the COMM window of the first radio
    bx, by = RX + RW - 112, c1[1] + 46
    over += leader(c1, (bx + 6, by + 16), SLATE) + bubble(bx, by, 100, 32, fill="#FFFFFF", stroke=SLATE, tail="left")
    over += "".join(f'<circle cx="{n(bx + 20 + k * 20)}" cy="{n(by + 16)}" r="6" fill="{c}"/>' for k, c in enumerate((SLATE, BLUE, VIOLET, AMBER)))
    c2 = at(0.397, 0.648)
    px, py = RX + RW - 62, c2[1] + 58
    over += leader(c2, (px - 40, py), RED) + pill(px, py, "MAYDAY", RED, size=10) + pill(px, py + 30, "PAN PAN", AMBER, size=10)
    c1 = (bx, by)
    POS['mayday'] = (px - 62, py)
    out += [over, close(RX, RY, RW, RH)]
    return out, au, c1


TX, TW = 316.0, 312.0
TY = (12.0, 136.0, 260.0)
TH = 120.0


def languages():
    x, y = TX, TY[0]
    return (R.tile(f"{U}t3", x, y, TW, TH, "sand") + bubble(x + 70, y + 34, 76, 44) + H.glyph_text("EN", x + 108, y + 56, 15, BLUE, spacing=0.6)
            + bubble(x + 168, y + 46, 76, 44, tail="right") + H.glyph_text("AR", x + 206, y + 68, 15, GREEN, spacing=0.6))


def class_d():
    """Class D: a cylinder of airspace about the aerodrome, the aeroplane outside it calling before it enters (two-way arrows)."""
    x, y, w, h = TX, TY[1], TW, TH
    uid = f"{U}d"
    o = card(uid, x, y, w, h) + S.sky(uid + "k", x, y, w, h, [(0.0, "#4F86C9"), (0.6, "#9CC2EA"), (1.0, "#E9EEF0")]) + S.plain(uid + "l", x, x + w, y + 86, y + h, seed=4, tone="day", photo=True)
    cx, top, bot = x + 196, y + 30, y + 92
    o += (f'<path d="M{n(cx - 78)} {n(top)} V{n(bot)} A78 12 0 0 0 {n(cx + 78)} {n(bot)} V{n(top)}" fill="{BLUE}" fill-opacity="0.16" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 4"/>'
          f'<ellipse cx="{n(cx)}" cy="{n(top)}" rx="78" ry="12" fill="{BLUE}" fill-opacity="0.12" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 4"/>')
    o += (f'<rect x="{n(cx - 6)}" y="{n(bot - 34)}" width="7" height="34" rx="2" fill="#D4DAE4" stroke="{SLATE}" stroke-width="1.2"/>'
          f'<path d="M{n(cx - 15)} {n(bot - 44)} H{n(cx + 10)} L{n(cx + 7)} {n(bot - 34)} H{n(cx - 12)} Z" fill="#8FB4E0" stroke="{SLATE}" stroke-width="1.2"/>'
          f'<rect x="{n(cx + 18)}" y="{n(bot - 4)}" width="48" height="5" rx="1" fill="#5B6577"/>')
    o += pill(cx + 50, top + 22, "D", BLUE, size=10)
    o += (f'<path d="M{n(x + 92)} {n(y + 52)} h24" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/><path d="M{n(x + 120)} {n(y + 52)} l-8 -5 v10 Z" fill="{GREEN}"/>'
          f'<path d="M{n(x + 92)} {n(y + 64)} h24" stroke="{GREEN}" stroke-width="3" stroke-linecap="round"/><path d="M{n(x + 88)} {n(y + 64)} l8 -5 v10 Z" fill="{GREEN}"/>')
    return o + close(x, y, w, h)


def taxi():
    """On the manoeuvring area: a taxiway seen from above, the holding position marking (two solid and two dashed yellow lines) with a red stop bar,
    and the aeroplane stopped before it."""
    x, y, w, h = TX, TY[2], TW, TH
    uid = f"{U}x"
    o = card(uid, x, y, w, h, "#E3D3AE") + f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="#E3D3AE"/>'
    ty = y + h / 2
    o += f'<rect x="{n(x - 4)}" y="{n(ty - 26)}" width="{n(w + 8)}" height="52" fill="#6B7280"/>'
    o += f'<line x1="{n(x)}" y1="{n(ty)}" x2="{n(x + w)}" y2="{n(ty)}" stroke="#FACC15" stroke-width="2"/>'
    hx = x + 196                                              # the holding position: two solid lines, then two dashed ones toward the runway
    o += (f'<line x1="{n(hx)}" y1="{n(ty - 26)}" x2="{n(hx)}" y2="{n(ty + 26)}" stroke="#FACC15" stroke-width="2.2"/><line x1="{n(hx + 6)}" y1="{n(ty - 26)}" x2="{n(hx + 6)}" y2="{n(ty + 26)}" stroke="#FACC15" stroke-width="2.2"/>'
          f'<line x1="{n(hx + 12)}" y1="{n(ty - 26)}" x2="{n(hx + 12)}" y2="{n(ty + 26)}" stroke="#FACC15" stroke-width="2.2" stroke-dasharray="6 4"/><line x1="{n(hx + 18)}" y1="{n(ty - 26)}" x2="{n(hx + 18)}" y2="{n(ty + 26)}" stroke="#FACC15" stroke-width="2.2" stroke-dasharray="6 4"/>')
    o += "".join(f'<circle cx="{n(hx - 8)}" cy="{n(ty - 22 + k * 8.8)}" r="2.6" fill="#EF4444" stroke="#7F1D1D" stroke-width="0.8"/><circle cx="{n(hx - 8)}" cy="{n(ty - 22 + k * 8.8)}" r="5" fill="#EF4444" fill-opacity="0.25"/>' for k in range(6))
    o += f'<rect x="{n(hx + 30)}" y="{n(y - 4)}" width="{n(w)}" height="{n(h + 8)}" fill="#4B5563"/><line x1="{n(hx + 60)}" y1="{n(y)}" x2="{n(hx + 60)}" y2="{n(y + h)}" stroke="#F8FAFC" stroke-width="2.4" stroke-dasharray="12 8"/>'
    o += (f'<rect x="{n(x + 104)}" y="{n(y + 14)}" width="7" height="22" rx="2" fill="#D4DAE4" stroke="{SLATE}" stroke-width="1.1"/>'
          f'<path d="M{n(x + 96)} {n(y + 6)} H{n(x + 119)} L{n(x + 116)} {n(y + 14)} H{n(x + 99)} Z" fill="#8FB4E0" stroke="{SLATE}" stroke-width="1.1"/>')
    return o + close(x, y, w, h)


def sprites():
    return [{"name": "sprite-side", "at": [TX + 60, TY[1] + 58], "width": 52, "outline": OUT, "shadow": SHADOW},
            {"name": "sprite-top", "at": [TX + 140, TY[2] + TH / 2], "width": 64, "angle": 90.0, "outline": OUT, "shadow": SHADOW}]


def callouts(au, c1):
    c = S.callout
    return (c(1, RX + 18, RY + 18, r=10) + c(2, c1[0] - 2, c1[1] - 2, r=10) + c(4, POS['mayday'][0] - 14, POS['mayday'][1], r=10)
            + c(3, TX + 16, TY[0] + 16, r=10) + c(5, TX + 16, TY[1] + 16, r=10) + c(6, TX + 16, TY[2] + 16, r=10))


def layers():
    rad, au, c1 = radios()
    sp = sprites()
    return [H.defs(U, W, HT), background()] + rad + [languages(), class_d(), taxi()] + sp + [callouts(au, c1)]


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
