"""Figure 10-4 (new). Reading the altimeter: two readings of the three-pointer dial, drawn as vectors (the dial of a sensitive altimeter: a pointer for hundreds of feet, a broader one for thousands, and a short one with a
triangle for tens of thousands; 0 to 9 round the face, 10 units to a turn).

The two readings are numbers the handbook already has: 1 870 ft, the elevation of Thumamah (AD 2 OETH 2.2; the altimeter on the ground with the reported setting, Chapter 10, "Setting the subscale"), and 6 500 ft, the first
westbound VFR level that clears the ground on the line from Riyadh to Jeddah (Figure 2-2). The pointers stand where the reading puts them: hundreds hand at (ft mod 1 000) / 1 000 of a turn, thousands hand at (ft mod 10 000) / 10 000,
tens-of-thousands hand at (ft mod 100 000) / 100 000. The window at the right of the face shows the setting in hectopascals: 1 013 in both (the standard setting, 1 013.2 hPa rounded), drawn only to show where it is; the figure
says nothing about what the setting should be. Digits only."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "al4"
R = 104.0
CENTRES = ((170.0, 138.0), (478.0, 138.0))
READINGS = (1870, 6500)
INK, SLATE, BLUE, AMBER, RED = "#1F2937", "#475569", "#1D4ED8", "#B45309", "#B91C1C"


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.4, height=12.0):
    w = gwidth(s, size) + 12.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.35))


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter>'
            f'<filter id="{U}hs" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="1.2" dy="2.2" stdDeviation="1.4" flood-color="#000000" flood-opacity="0.5"/></filter>'
            f'<radialGradient id="{U}bz" cx="0.35" cy="0.3" r="0.9"><stop offset="0" stop-color="#E5E9F0"/><stop offset="0.55" stop-color="#8E99AB"/><stop offset="1" stop-color="#3A4352"/></radialGradient>'
            f'<radialGradient id="{U}fc" cx="0.4" cy="0.35" r="0.85"><stop offset="0" stop-color="#2B3442"/><stop offset="1" stop-color="#11161E"/></radialGradient>'
            f'<linearGradient id="{U}gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.22"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def face(cx, cy):
    out = [f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(R + 12)}" fill="url(#{U}bz)" filter="url(#{U}ds)"/>',
           f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(R + 3)}" fill="#0B0F15"/>',
           f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(R)}" fill="url(#{U}fc)"/>']
    for k in range(50):                                                    # 50 ticks: 20 ft each
        a = math.radians(k * 7.2)
        major = k % 5 == 0
        r0, r1 = (R - 14, R - 3) if major else (R - 8, R - 3)
        out.append(f'<line x1="{n(cx + r0 * math.sin(a))}" y1="{n(cy - r0 * math.cos(a))}" x2="{n(cx + r1 * math.sin(a))}" y2="{n(cy - r1 * math.cos(a))}" stroke="#F4F1E8" stroke-width="{1.8 if major else 0.9}" stroke-linecap="round"/>')
    for d in range(10):
        a = math.radians(d * 36)
        out.append(H.glyph_text(str(d), cx + (R - 28) * math.sin(a), cy - (R - 28) * math.cos(a), 11.0, "#F4F1E8", spacing=0.3))
    # the setting window (3 o'clock): the pressure in hectopascals
    wx, wy = cx + 40, cy
    out.append(f'<rect x="{n(wx - 18)}" y="{n(wy - 7)}" width="36" height="14" rx="2.4" fill="#0B0F15" stroke="#8E99AB" stroke-width="1.2"/>'
               + H.glyph_text("1013", wx, wy, 7.2, "#F4F1E8", spacing=0.45))
    return "".join(out)


def hand(cx, cy, turn, kind):
    """A pointer standing at `turn` of a full turn (0 = straight up)."""
    a = turn * 360.0
    if kind == "hundreds":                                                # long and thin, with a counterweight
        body = (f'<path d="M{n(cx - 2.2)} {n(cy + 16)} L{n(cx - 1.4)} {n(cy - R + 10)} L{n(cx)} {n(cy - R + 4)} L{n(cx + 1.4)} {n(cy - R + 10)} L{n(cx + 2.2)} {n(cy + 16)} Z" fill="#F4F1E8" stroke="#0B0F15" stroke-width="0.6"/>'
                f'<circle cx="{n(cx)}" cy="{n(cy + 18)}" r="3.8" fill="#F4F1E8" stroke="#0B0F15" stroke-width="0.6"/>')
    elif kind == "thousands":                                             # medium, broad, with an arrow tip
        body = (f'<path d="M{n(cx - 3.6)} {n(cy + 12)} L{n(cx - 3.6)} {n(cy - 0.52 * R)} L{n(cx - 6.4)} {n(cy - 0.52 * R)} L{n(cx)} {n(cy - 0.72 * R)} L{n(cx + 6.4)} {n(cy - 0.52 * R)} L{n(cx + 3.6)} {n(cy - 0.52 * R)} L{n(cx + 3.6)} {n(cy + 12)} Z" fill="#F4F1E8" stroke="#0B0F15" stroke-width="0.7"/>')
    else:                                                                 # tens of thousands: short, with a triangle
        body = (f'<path d="M{n(cx - 1.8)} {n(cy + 4)} L{n(cx - 1.8)} {n(cy - 0.26 * R)} L{n(cx - 7)} {n(cy - 0.26 * R)} L{n(cx)} {n(cy - 0.46 * R)} L{n(cx + 7)} {n(cy - 0.26 * R)} L{n(cx + 1.8)} {n(cy - 0.26 * R)} L{n(cx + 1.8)} {n(cy + 4)} Z" fill="#FFFFFF" stroke="#0B0F15" stroke-width="0.8"/>')
    return f'<g transform="rotate({n(a)} {n(cx)} {n(cy)})" filter="url(#{U}hs)">{body}</g>'


def dial(i):
    cx, cy = CENTRES[i]
    ft = READINGS[i]
    out = [face(cx, cy)]
    out.append(hand(cx, cy, (ft % 100000) / 100000.0, "tens"))
    out.append(hand(cx, cy, (ft % 10000) / 10000.0, "thousands"))
    out.append(hand(cx, cy, (ft % 1000) / 1000.0, "hundreds"))
    out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="5.2" fill="#C9D1DD" stroke="#0B0F15" stroke-width="0.8"/>')
    out.append(f'<path d="M{n(cx - R + 10)} {n(cy - R * 0.55)} A{n(R)} {n(R)} 0 0 1 {n(cx + R * 0.1)} {n(cy - R + 4)} L{n(cx - R * 0.3)} {n(cy - R * 0.3)} Z" fill="url(#{U}gl)" opacity="0.8"/>')
    out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(R + 12)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="1"/>')
    # the knob (bottom left) that sets the window
    out.append(f'<rect x="{n(cx - R * 0.78 - 14)}" y="{n(cy + R * 0.78)}" width="14" height="14" rx="3.6" transform="rotate(-45 {n(cx - R * 0.78 - 7)} {n(cy + R * 0.78 + 7)})" fill="#8E99AB" stroke="#3A4352" stroke-width="1.2"/>')
    out.append(pill(f"{ft // 1000} {ft % 1000:03d} FT" if ft >= 1000 else f"{ft} FT", cx, cy + R + 36, SLATE if i == 0 else AMBER))
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.5
    cx, cy = CENTRES[0]
    a1 = math.radians(((READINGS[0] % 1000) / 1000.0) * 360)                      # the tip of the hundreds hand
    a2 = math.radians(((READINGS[0] % 10000) / 10000.0) * 360)
    t1 = (cx + (R - 12) * math.sin(a1), cy - (R - 12) * math.cos(a1))
    t2 = (cx + 0.6 * R * math.sin(a2), cy - 0.6 * R * math.cos(a2))
    t3 = (cx, cy - 0.38 * R)
    return "".join([
        c(1, cx - R - 34, cy - 58, t1[0], t1[1], r=r),
        c(2, cx - R - 34, cy + 6, t2[0], t2[1], r=r),
        c(3, cx - R - 34, cy - 106, t3[0], t3[1], r=r),
        c(4, cx + R + 38, cy - 2, cx + 58, cy, r=r),
        c(5, cx - R - 8, cy + R + 28, cx - R * 0.78 - 8, cy + R * 0.78 + 8, r=r),
    ])


def layers():
    return [H.defs(U, W, HT), background(), dial(0), dial(1), callouts()]


def plate():
    return {
        "id": "fig-10-04-reading-altimeter",
        "replaces": "fig-10-04-reading-altimeter.svg",         # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-10-04-reading-altimeter.jpg",
        "caption": "Figure 10-4. Reading the altimeter: three pointers, here at 1 870 ft and at 6 500 ft",
        "desc": ("Figure 10-4. Reading the altimeter: three pointers, here at 1 870 ft (the elevation of Thumamah) and at 6 500 ft (a cruising level). The hundreds pointer is the long thin one, the thousands "
                 "pointer the broad medium one and the tens-of-thousands pointer the short one with a triangle; the window at the right shows the setting in hectopascals."),
        "legend": [
            "The hundreds pointer: long and thin, one turn for each 1 000 ft. At 1 870 ft it stands between 8 and 9 (870 ft); at 6 500 ft, at 5 (500 ft).",
            "The thousands pointer: broad and medium, one turn for each 10 000 ft. At 1 870 ft it stands between 1 and 2 (1 thousand and a bit more); at 6 500 ft, between 6 and 7.",
            "The tens-of-thousands pointer: short, with a triangle, one turn for 100 000 ft. Below 10 000 ft it stands between 0 and 1: misread it and the error is thousands of feet.",
            "The setting window: the pressure in hectopascals that the altimeter measures from (1013 here, drawn only to show where the window is). Set to the reported setting (QNH), the altimeter on the ground reads the aerodrome elevation: 1 870 ft at Thumamah.",
            "The knob that sets the window. Moving the setting moves all three pointers.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
