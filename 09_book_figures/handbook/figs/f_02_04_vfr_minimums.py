"""Figure 2-4 (new). VFR weather minimums, from that section of Chapter 2 (GACAR 91.165): four scenes with a cloud and the distances to keep from it.

1 Classes C and D, and Class E below 10 000 ft MSL: 5 km, 500 ft below, 1 000 ft above, 2 000 ft horizontal; 2 Class E at or above 10 000 ft MSL: 8 km, 1 000 ft below and above, 1 500 m horizontal; 3 Classes G and F, 1 200 ft or less above the surface, aeroplanes by day: 3 km, clear of clouds;
4 near a controlled aerodrome: no VFR beneath a ceiling of less than 1 000 ft in the surface area, and a ground visibility of 5 km to take off, land or enter the circuit. The text is the distances, from the chapter. Not to scale."""
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 404
U = "ar0204"
INK, BLUE, RED, AMBER, GREEN = "#1E293B", "#1D4ED8", "#B91C1C", "#B45309", "#15803D"
PW, PH = 304.0, 184.0
PX = (12.0, 324.0, 12.0, 324.0)
PY = (14.0, 14.0, 206.0, 206.0)
DAY = [(0.0, "#3F78C2"), (0.5, "#86B4E6"), (0.9, "#DCEBF8"), (1.0, "#F4F1DF")]
HIGH = [(0.0, "#2C5BA8"), (0.6, "#6E9ED8"), (1.0, "#BFD6F0")]
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}


def frame(i, stops, body):
    x, y = PX[i], PY[i]
    uid = f"{U}p{i}"
    return (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2" stdDeviation="2.4" flood-color="#10233F" flood-opacity="0.28"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="#ffffff" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, y, PW, PH, stops) + body + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(PW)}" height="{n(PH)}" rx="9" fill="none" stroke="#ffffff" stroke-width="1.6"/>')


def pill(cx, cy, text, fill=INK, size=8.5):
    g = H._GLYPHS
    w = sum((size * 0.38 if c == " " else g["glyphs"][c]["advance"] * size / g["cap_height"]) + 0.4 for c in text) + 12.0
    h = size + 7.0
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.4"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def dim(x1, y1, x2, y2, col="#FFFFFF"):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    def head(x, y, s):
        hx, hy = x - s * 7 * math.cos(a), y - s * 7 * math.sin(a)
        px, py = -math.sin(a) * 4.5, math.cos(a) * 4.5
        return f'<path d="M{n(x)} {n(y)} L{n(hx + px)} {n(hy + py)} L{n(hx - px)} {n(hy - py)} Z" fill="{col}"/>'
    return f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{col}" stroke-width="2.2"/>' + head(x2, y2, 1) + head(x1, y1, -1)


def box(cx, cy, w, h):                                       # the cloud's clearance box
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="6" fill="#FFFFFF" fill-opacity="0.08" stroke="#FFFFFF" stroke-width="1.8" stroke-dasharray="6 4"/>'


def scene1():
    x, y = PX[0], PY[0]
    cx, cy = x + 172, y + 84
    b = box(cx, cy - 6, 196, 120)
    d = dim(cx, cy - 66, cx, cy - 34) + pill(cx + 32, cy - 52, "1 000 FT") + dim(cx, cy + 22, cx, cy + 54) + pill(cx + 30, cy + 38, "500 FT") + dim(cx + 52, cy - 6, cx + 98, cy - 6) + pill(cx + 75, cy + 10, "2 000 FT")
    return frame(0, DAY, S.plain(f"{U}l1", x, x + PW, y + 150, y + PH, seed=3, tone="day", photo=True) + b + d + pill(x + 46, y + 166, "5 KM", BLUE))


def scene2():
    x, y = PX[1], PY[1]
    cx, cy = x + 172, y + 88
    b = box(cx, cy - 4, 196, 132)
    d = dim(cx, cy - 70, cx, cy - 34) + pill(cx + 32, cy - 56, "1 000 FT") + dim(cx, cy + 26, cx, cy + 62) + pill(cx + 32, cy + 44, "1 000 FT") + dim(cx + 52, cy - 4, cx + 98, cy - 4) + pill(cx + 75, cy + 12, "1 500 M")
    return frame(1, HIGH, b + d + pill(x + 46, y + 166, "8 KM", BLUE))


def scene3():
    x, y = PX[2], PY[2]
    line = S.altitude_line(x, x + PW, y + 70, colour="#FFFFFF", opacity=0.9, dash="6 5", width=1.8) + pill(x + 262, y + 70, "1 200 FT", AMBER)
    return frame(2, DAY, S.plain(f"{U}l3", x, x + PW, y + 150, y + PH, seed=7, tone="day", photo=True) + line + pill(x + 46, y + 166, "3 KM", BLUE))


def scene4():
    x, y = PX[3], PY[3]
    ground = S.plain(f"{U}l4", x, x + PW, y + 140, y + PH, seed=11, tone="storm", photo=True)
    runway = f'<path d="M{n(x + 120)} {n(y + 150)} L{n(x + 250)} {n(y + 150)} L{n(x + 270)} {n(y + 168)} L{n(x + 100)} {n(y + 168)} Z" fill="#5B6577"/><line x1="{n(x + 118)}" y1="{n(y + 159)}" x2="{n(x + 252)}" y2="{n(y + 159)}" stroke="#F1F5F9" stroke-width="1.4" stroke-dasharray="8 6"/>'
    tower = f'<rect x="{n(x + 62)}" y="{n(y + 112)}" width="8" height="38" fill="#D4DAE4" stroke="#6B7A93"/><path d="M{n(x + 52)} {n(y + 102)} H{n(x + 80)} L{n(x + 76)} {n(y + 112)} H{n(x + 56)} Z" fill="#8FB4E0" stroke="#4B6A97"/>'
    ceil = S.altitude_line(x, x + PW, y + 70, colour="#FFFFFF", opacity=0.95, dash="6 5", width=2) + dim(x + 210, y + 74, x + 210, y + 146) + pill(x + 244, y + 110, "1 000 FT", RED)
    return frame(3, [(0.0, "#6D7F9E"), (0.5, "#9FB0C8"), (1.0, "#D7DEE8")], ground + runway + tower + ceil + pill(x + 46, y + 166, "5 KM", BLUE))


def sprites():
    o = lambda name, x, y, w, **k: {"name": name, "at": [x, y], "width": w, "outline": OUT, "shadow": SHADOW, **k}
    return [o("cloud-cumulus-b", PX[0] + 172, PY[0] + 80, 96), o("sprite-side", PX[0] + 46, PY[0] + 100, 46),
            o("cloud-cumulus-b", PX[1] + 172, PY[1] + 84, 96), o("sprite-side", PX[1] + 46, PY[1] + 60, 46),
            o("cloud-cumulus-a", PX[2] + 120, PY[2] + 38, 110), o("cloud-cumulus-a", PX[2] + 250, PY[2] + 30, 80), o("sprite-side", PX[2] + 110, PY[2] + 104, 46),
            o("cloud-stratus", PX[3] + 152, PY[3] + 48, 320), o("sprite-side", PX[3] + 150, PY[3] + 112, 40, opacity=0.9)]


def callouts():
    return "".join(S.callout(i + 1, PX[i] + 17, PY[i] + 17, r=10.5) for i in range(4))


def layers():
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', scene1(), scene2(), scene3(), scene4(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-02-04-vfr-minimums",
        "replaces": "fig-02-04-vfr-minimums.svg",            # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-02-04-vfr-minimums.jpg",
        "caption": "Figure 2-4. VFR weather minimums: distance from cloud and flight visibility, low down by day, and near a controlled aerodrome",
        "desc": ("Figure 2-4. VFR weather minimums in four scenes: in Classes C and D, and in Class E below 10 000 ft MSL, 5 km and 500 ft below, 1 000 ft above and 2 000 ft horizontally from cloud; in Class E at or above 10 000 ft MSL, 8 km and 1 000 ft below and above, 1 500 m horizontally; "
                 "in Classes G and F at 1 200 ft or less above the surface, aeroplanes by day, 3 km and clear of clouds; and near a controlled aerodrome, no VFR beneath a ceiling of less than 1 000 ft and a ground visibility of 5 km to take off, land or enter the circuit. Not to scale."),
        "legend": [
            "Classes C and D, and Class E below 10 000 ft MSL: flight visibility 5 km; 500 ft below, 1 000 ft above and 2 000 ft horizontally from cloud.",
            "Class E at or above 10 000 ft MSL: 8 km; 1 000 ft below, 1 000 ft above and 1 500 m horizontally from cloud.",
            "Classes G and F, 1 200 ft or less above the surface, aircraft other than helicopters, by day: 3 km and clear of clouds.",
            "Near a controlled aerodrome: no VFR beneath a ceiling of less than 1 000 ft within the controlled airspace designated to the surface; to take off, land or enter the circuit, a ground visibility of at least 5 km. The AIP's own table is more demanding: plan to the more demanding figure.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
