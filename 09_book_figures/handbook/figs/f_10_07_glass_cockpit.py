"""Figure 10-7 (new). The electronic flight displays of Chapter 10, as a schematic (no values): a primary flight display (PFD) and a multi-function display (MFD).

PFD: 1 attitude across the screen (sky and ground, a pitch ladder), 2 an airspeed tape on the left with the colour bands of the traditional indicator's arcs, 3 altitude and vertical speed on the right, 4 heading below,
5 a bar under the bank pointer in place of the ball, 6 trend vectors showing where airspeed and altitude will be in 6 seconds (the only text, 6 S); 7 the MFD with the map and engine instruments; 8 invalid data: a red X in place of the indication.
Shapes, colours and callouts; no values are shown, the picture is a diagram of the layout the chapter describes."""
import math

from figs import h_b2 as H
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 360
U = "ar107"
SX0, SY0, SX1, SY1 = 48.0, 18.0, 432.0, 342.0            # the PFD screen
HZ = 176.0                                                  # the horizon
CX = 240.0


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, fill, size=8.0):
    return M.chip(cx, cy, text, fill, size=size, anchor="middle")


def pfd():
    out = [f'<defs><clipPath id="{U}sc"><rect x="{n(SX0)}" y="{n(SY0)}" width="{n(SX1 - SX0)}" height="{n(SY1 - SY0)}" rx="8"/></clipPath>'
           f'<linearGradient id="{U}sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B6CC4"/><stop offset="1" stop-color="#7FB4EC"/></linearGradient>'
           f'<linearGradient id="{U}gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9A6B3C"/><stop offset="1" stop-color="#5E3F20"/></linearGradient>'
           f'<filter id="{U}fs" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="2.4" stdDeviation="3" flood-color="#10233F" flood-opacity="0.35"/></filter></defs>',
           f'<rect x="40" y="10" width="400" height="340" rx="14" fill="#111827" filter="url(#{U}fs)"/>',
           f'<g clip-path="url(#{U}sc)"><rect x="{n(SX0)}" y="{n(SY0)}" width="{n(SX1 - SX0)}" height="{n(HZ - SY0)}" fill="url(#{U}sk)"/><rect x="{n(SX0)}" y="{n(HZ)}" width="{n(SX1 - SX0)}" height="{n(SY1 - HZ)}" fill="url(#{U}gd)"/>'
           f'<line x1="{n(SX0)}" y1="{n(HZ)}" x2="{n(SX1)}" y2="{n(HZ)}" stroke="#FFFFFF" stroke-width="2.4"/>']
    for k, wd in ((-1, 46), (1, 46), (-2, 24), (2, 24), (-3, 46), (3, 46), (-4, 24), (4, 24)):          # the pitch ladder
        y = HZ + k * 22.0
        out.append(f'<line x1="{n(CX - wd / 2)}" y1="{n(y)}" x2="{n(CX + wd / 2)}" y2="{n(y)}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.8"/>')
    # the aeroplane symbol
    out.append(f'<path d="M{n(CX - 44)} {n(HZ)} h24 l8 8 M{n(CX + 44)} {n(HZ)} h-24 l-8 8" fill="none" stroke="#FACC15" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{n(CX)}" cy="{n(HZ)}" r="3.4" fill="#FACC15"/>')
    # the bank scale, the pointer and the bar under it
    cy, r = 172.0, 108.0
    for a in (-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60):
        ra = math.radians(a)
        l = 10.0 if a % 30 == 0 else 6.0
        out.append(f'<line x1="{n(CX + r * math.sin(ra))}" y1="{n(cy - r * math.cos(ra))}" x2="{n(CX + (r - l) * math.sin(ra))}" y2="{n(cy - (r - l) * math.cos(ra))}" stroke="#FFFFFF" stroke-width="2"/>')
    out.append(f'<path d="M{n(CX)} {n(cy - r + 12)} l-7 13 h14 Z" fill="#FFFFFF"/>')
    out.append(f'<path d="M{n(CX - 12)} {n(cy - r + 29)} h24 l-3 6 h-18 Z" fill="#FFFFFF" fill-opacity="0.95"/>')           # the bar under the pointer
    # the airspeed tape (left) with its colour bands
    tx0, tx1 = 56.0, 100.0
    out.append(f'<rect x="{n(tx0)}" y="48" width="{n(tx1 - tx0)}" height="256" fill="#0B1220" fill-opacity="0.62"/>')
    for k in range(0, 17):
        y = 56 + k * 15.0
        out.append(f'<line x1="{n(tx1)}" y1="{n(y)}" x2="{n(tx1 - (9 if k % 2 == 0 else 5))}" y2="{n(y)}" stroke="#FFFFFF" stroke-width="1.6"/>')
    out.append(f'<rect x="{n(tx1 + 1)}" y="94" width="6" height="40" fill="#FACC15"/><rect x="{n(tx1 + 1)}" y="134" width="6" height="118" fill="#22C55E"/><rect x="{n(tx1 + 8)}" y="196" width="4" height="86" fill="#F8FAFC"/><rect x="{n(tx1 + 1)}" y="88" width="6" height="6" fill="#EF4444"/>')
    out.append(f'<path d="M{n(tx0 - 2)} {n(HZ - 12)} h{n(tx1 - tx0 - 8)} l8 12 l-8 12 h-{n(tx1 - tx0 - 8)} Z" fill="#0B1220" stroke="#FFFFFF" stroke-width="1.8"/>')
    # the altitude tape and the vertical speed (right)
    ax0, ax1 = 360.0, 408.0
    out.append(f'<rect x="{n(ax0)}" y="48" width="{n(ax1 - ax0)}" height="256" fill="#0B1220" fill-opacity="0.62"/>')
    for k in range(0, 17):
        y = 56 + k * 15.0
        out.append(f'<line x1="{n(ax0)}" y1="{n(y)}" x2="{n(ax0 + (9 if k % 2 == 0 else 5))}" y2="{n(y)}" stroke="#FFFFFF" stroke-width="1.6"/>')
    out.append(f'<path d="M{n(ax1 + 2)} {n(HZ - 12)} h-{n(ax1 - ax0 - 8)} l-8 12 l8 12 h{n(ax1 - ax0 - 8)} Z" fill="#0B1220" stroke="#FFFFFF" stroke-width="1.8"/>')
    out.append(f'<rect x="{n(ax1 + 6)}" y="80" width="12" height="192" rx="3" fill="#0B1220" fill-opacity="0.7"/><line x1="{n(ax1 + 6)}" y1="{n(HZ)}" x2="{n(ax1 + 18)}" y2="{n(HZ)}" stroke="#FFFFFF" stroke-width="1.4"/><path d="M{n(ax1 + 6)} {n(HZ)} L{n(ax1 + 18)} {n(HZ - 28)}" stroke="#F8FAFC" stroke-width="3" stroke-linecap="round"/>')
    # the trend vectors
    out.append(f'<line x1="{n(tx1 + 12)}" y1="{n(HZ)}" x2="{n(tx1 + 12)}" y2="{n(HZ - 40)}" stroke="#E879F9" stroke-width="4" stroke-linecap="round"/><path d="M{n(tx1 + 6)} {n(HZ - 34)} l6 -8 l6 8" fill="none" stroke="#E879F9" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<line x1="{n(ax0 - 6)}" y1="{n(HZ)}" x2="{n(ax0 - 6)}" y2="{n(HZ - 52)}" stroke="#E879F9" stroke-width="4" stroke-linecap="round"/><path d="M{n(ax0 - 12)} {n(HZ - 46)} l6 -8 l6 8" fill="none" stroke="#E879F9" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    # the heading strip (bottom)
    out.append(f'<rect x="132" y="310" width="216" height="28" rx="6" fill="#0B1220" fill-opacity="0.8"/>')
    for k in range(0, 15):
        x = 144 + k * 14.0
        out.append(f'<line x1="{n(x)}" y1="316" x2="{n(x)}" y2="{n(316 + (10 if k % 2 == 0 else 6))}" stroke="#FFFFFF" stroke-width="1.6"/>')
    out.append(f'<path d="M{n(CX)} 340 l-6 -10 h12 Z" fill="#FACC15"/><rect x="{n(CX - 16)}" y="302" width="32" height="14" rx="3" fill="#0B1220" stroke="#FFFFFF" stroke-width="1.4"/>')
    out.append('</g>')
    out.append(f'<rect x="{n(SX0)}" y="{n(SY0)}" width="{n(SX1 - SX0)}" height="{n(SY1 - SY0)}" rx="8" fill="none" stroke="#374151" stroke-width="2"/>')
    out.append(pill(tx1 + 62, HZ - 34, "6 S", "#C026D3"))
    return "".join(out)


def mfd():
    x, y, w, h = 452.0, 10.0, 178.0, 236.0
    out = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="12" fill="#111827" filter="url(#{U}fs)"/>',
           f'<defs><clipPath id="{U}mc"><rect x="{n(x + 8)}" y="{n(y + 8)}" width="{n(w - 16)}" height="{n(h - 16)}" rx="6"/></clipPath></defs><g clip-path="url(#{U}mc)">',
           f'<rect x="{n(x + 8)}" y="{n(y + 8)}" width="{n(w - 16)}" height="128" fill="#D6C9A4"/><path d="M{n(x + 8)} {n(y + 92)} C{n(x + 50)} {n(y + 70)} {n(x + 90)} {n(y + 110)} {n(x + 170)} {n(y + 60)} L{n(x + 170)} {n(y + 136)} L{n(x + 8)} {n(y + 136)} Z" fill="#8FB88A"/>',
           f'<path d="M{n(x + 8)} {n(y + 36)} C{n(x + 40)} {n(y + 50)} {n(x + 70)} {n(y + 30)} {n(x + 170)} {n(y + 44)} L{n(x + 170)} {n(y + 20)} L{n(x + 8)} {n(y + 20)} Z" fill="#7FB4EC"/>',
           f'<path d="M{n(x + 24)} {n(y + 124)} L{n(x + 78)} {n(y + 86)} L{n(x + 120)} {n(y + 96)} L{n(x + 158)} {n(y + 40)}" fill="none" stroke="#D946EF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{n(x + 78)}" cy="{n(y + 86)}" r="4" fill="#FFFFFF" stroke="#D946EF" stroke-width="1.6"/><circle cx="{n(x + 120)}" cy="{n(y + 96)}" r="4" fill="#FFFFFF" stroke="#D946EF" stroke-width="1.6"/>']
    for k, (c, f) in enumerate((("#22C55E", 0.72), ("#FACC15", 0.5), ("#22C55E", 0.62), ("#22C55E", 0.4))):          # the engine instruments
        yy = y + 146 + k * 20.0
        out.append(f'<rect x="{n(x + 16)}" y="{n(yy)}" width="{n(w - 32)}" height="11" rx="5" fill="#374151"/><rect x="{n(x + 16)}" y="{n(yy)}" width="{n((w - 32) * f)}" height="11" rx="5" fill="{c}"/>')
    out.append('</g>')
    return "".join(out)


def failure():
    x, y, w, h = 452.0, 256.0, 178.0, 94.0
    out = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="12" fill="#111827" filter="url(#{U}fs)"/>',
           f'<rect x="{n(x + 56)}" y="{n(y + 10)}" width="66" height="{n(h - 20)}" rx="4" fill="#1F2937" stroke="#374151" stroke-width="1.6"/>']
    for k in range(0, 5):
        out.append(f'<line x1="{n(x + 114)}" y1="{n(y + 20 + k * 14)}" x2="{n(x + 122)}" y2="{n(y + 20 + k * 14)}" stroke="#6B7280" stroke-width="1.6"/>')
    out.append(f'<path d="M{n(x + 66)} {n(y + 22)} L{n(x + 112)} {n(y + 72)} M{n(x + 112)} {n(y + 22)} L{n(x + 66)} {n(y + 72)}" stroke="#EF4444" stroke-width="7" stroke-linecap="round"/>')
    return "".join(out)


def callouts():
    c = S.callout
    return "".join((c(1, 196, 104, 170, 172, r=10.5), c(2, 128, 72, 106, 146, r=10.5), c(3, 332, 84, 374, 110, r=10.5), c(4, 108, 326, 140, 326, r=10.5),
                    c(5, 304, 70, 246, 112, r=10.5), c(6, 318, 150, 352, 138, r=10.5), c(7, 474, 34, r=10.5), c(8, 474, 280, r=10.5)))


def layers():
    return [H.defs(U, W, HT), '<rect x="0" y="0" width="640" height="360" fill="#ffffff"/>', pfd(), mfd(), failure(), callouts()]


def plate():
    return {
        "id": "fig-10-07-glass-cockpit",
        "replaces": "fig-10-07-glass-cockpit.svg",          # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-10-07-glass-cockpit.jpg",
        "caption": "Figure 10-7. Electronic flight displays: the layout of a primary flight display and a multi-function display (schematic)",
        "desc": ("Figure 10-7. A schematic of the electronic flight displays: a primary flight display with attitude across the screen, an airspeed tape with the colour bands, altitude and vertical speed, heading, a bar under the bank pointer and trend vectors for 6 seconds; "
                 "a multi-function display with the map and engine instruments; and an indication replaced by a red X when the data are invalid. No values are shown."),
        "legend": [
            "Attitude is shown across the screen.",
            "The airspeed tape on the left carries the same colour bands as the arcs of the traditional indicator.",
            "Altitude and vertical speed are on the right.",
            "Heading is shown below.",
            "A bar under the bank pointer replaces the ball.",
            "Trend vectors show where airspeed and altitude will be in 6 seconds.",
            "The multi-function display carries the map and the engine instruments.",
            "Invalid data: the indication is replaced by a red X or a flag.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
