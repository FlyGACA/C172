"""Figure 21-9. A transponder control head and a safe way to change the code, drawn again as a piece of hardware (the old figure was a flat diagram). Kept from it: the head
with a five-position mode selector (off, standby, on, altitude, test; the selector on altitude), four code knobs under a display of the code 4600, the ident button and the reply
light; and below, the two orders of changing 4600 to 7200 on a head whose knobs change the active code as they turn: safe through 4200, unsafe through 7600 and 7500.

The head as a panel unit: a dark bezel with a soft metallic gradient and four screws, a recessed display with lit amber digits, knurled knobs with a highlight, a selector with a
pointer and five detents, a rubber ident button, a reply lamp lit amber. The two orders as rows of small lit displays joined by arrows, the unsafe codes in red. No words: the
positions and parts are numbered and the legend names them (the labels differ between models)."""
import math

from figs import h_b2 as H
from figs import marks as M
from figs import scene as S

n = S.n
W, HT = 640, 380
U = "tx21"
AMBER, GREEN, RED, INK = "#FFB23E", "#15803D", "#B91C1C", "#1E293B"
X, Y, WU, HU = 28.0, 18.0, 584.0, 178.0                    # the unit
SEL = (122.0, 108.0)                                        # the mode selector
POS = [210.0, 250.0, 295.0, 340.0, 25.0]                    # its five detents (degrees clockwise from up): off, standby, on, altitude, test
DIGITS_X = [266.5, 327.5, 388.5, 449.5]
DISP_Y = 52.0


def unit():
    g = S.gradient
    out = [f'<defs>{g(U + "b", [(0, "#4A5466"), (0.08, "#3A4354"), (0.55, "#262D3A"), (1, "#1A202B")])}'
           f'{g(U + "f", [(0, "#2E3646"), (1, "#1D232F")])}'
           f'<filter id="{U}s" x="-6%" y="-8%" width="112%" height="125%"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#0B1224" flood-opacity="0.45"/></filter>'
           f'<filter id="{U}g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.6"/></filter>'
           f'<radialGradient id="{U}k" cx="0.38" cy="0.32" r="0.75"><stop offset="0" stop-color="#8A94A6"/><stop offset="0.45" stop-color="#4B5466"/><stop offset="1" stop-color="#1B212C"/></radialGradient>'
           f'<radialGradient id="{U}l" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFE7A8"/><stop offset="0.45" stop-color="#FFB23E"/><stop offset="1" stop-color="#C46A10"/></radialGradient></defs>']
    out.append(f'<rect x="{n(X)}" y="{n(Y)}" width="{n(WU)}" height="{n(HU)}" rx="12" fill="url(#{U}b)" filter="url(#{U}s)"/>'
               f'<rect x="{n(X + 8)}" y="{n(Y + 8)}" width="{n(WU - 16)}" height="{n(HU - 16)}" rx="8" fill="url(#{U}f)" stroke="#0E131C" stroke-width="1.2"/>'
               f'<path d="M{n(X + 14)} {n(Y + 1.6)} H{n(X + WU - 14)}" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="1.2" stroke-linecap="round"/>')
    for sx, sy in ((X + 16, Y + 16), (X + WU - 16, Y + 16), (X + 16, Y + HU - 16), (X + WU - 16, Y + HU - 16)):
        out.append(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="4.2" fill="url(#{U}k)" stroke="#0E131C" stroke-width="0.8"/>'
                   f'<path d="M{n(sx - 2.6)} {n(sy + 1.4)} L{n(sx + 2.6)} {n(sy - 1.4)}" stroke="#121821" stroke-width="1.1"/>')
    return "".join(out)


def knob(cx, cy, r, ridges=24):
    out = [f'<circle cx="{n(cx + 1.5)}" cy="{n(cy + 3)}" r="{n(r)}" fill="#05080D" opacity="0.55" filter="url(#{U}g)"/>',
           f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{U}k)" stroke="#0E131C" stroke-width="1"/>']
    for i in range(ridges):
        a = math.radians(i * 360 / ridges)
        x0, y0 = cx + (r - 2.6) * math.sin(a), cy - (r - 2.6) * math.cos(a)
        x1, y1 = cx + r * math.sin(a), cy - r * math.cos(a)
        out.append(f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" stroke="#11161F" stroke-opacity="0.75" stroke-width="1"/>')
    out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 0.62)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.12" stroke-width="1"/>')
    return "".join(out)


def selector():
    cx, cy = SEL
    out = []
    for i, a in enumerate(POS):
        x, y = cx + 44 * math.sin(math.radians(a)), cy - 44 * math.cos(math.radians(a))
        x0, y0 = cx + 34 * math.sin(math.radians(a)), cy - 34 * math.cos(math.radians(a))
        out.append(f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(cx + 39 * math.sin(math.radians(a)))}" y2="{n(cy - 39 * math.cos(math.radians(a)))}" stroke="#E2E8F0" stroke-width="2" stroke-linecap="round"/>')
    out.append(knob(cx, cy, 28, 30))
    a = math.radians(POS[3])                                # on altitude
    out.append(f'<path d="M{n(cx + 25 * math.sin(a))} {n(cy - 25 * math.cos(a))} L{n(cx - 8 * math.sin(a))} {n(cy + 8 * math.cos(a))}" stroke="#F8FAFC" stroke-width="3.4" stroke-linecap="round"/>')
    return "".join(out)


def display(uid, x, y, w, h, code, colour=AMBER, size=26.0, frame=None):
    """A recessed display with the code lit in it."""
    out = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="5" fill="#05070B" stroke="{frame or "#3B4456"}" stroke-width="{2.2 if frame else 1.2}"/>',
           f'<rect x="{n(x + 2)}" y="{n(y + 2)}" width="{n(w - 4)}" height="{n(h * 0.42)}" rx="3" fill="#FFFFFF" opacity="0.05"/>']
    step = (w - 16) / len(code)
    for i, c in enumerate(code):
        cx = x + 8 + step * (i + 0.5)
        out.append(f'<g filter="url(#{U}g)" opacity="0.8">{H.glyph_text(c, cx, y + h / 2, size, colour)}</g>' + H.glyph_text(c, cx, y + h / 2, size, colour))
    return "".join(out)


def ident(cx, cy):
    return (f'<rect x="{n(cx - 30 + 1.5)}" y="{n(cy - 15 + 3)}" width="60" height="30" rx="9" fill="#05080D" opacity="0.5" filter="url(#{U}g)"/>'
            f'<rect x="{n(cx - 30)}" y="{n(cy - 15)}" width="60" height="30" rx="9" fill="#2B3240" stroke="#0E131C" stroke-width="1"/>'
            f'<rect x="{n(cx - 27)}" y="{n(cy - 12.5)}" width="54" height="12" rx="6" fill="#FFFFFF" opacity="0.08"/>')


def lamp(cx, cy):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="14" fill="#FFB23E" opacity="0.55" filter="url(#{U}g)"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="8" fill="url(#{U}l)" stroke="#6B3A0B" stroke-width="0.8"/>'
            f'<circle cx="{n(cx - 2.4)}" cy="{n(cy - 2.6)}" r="2.2" fill="#FFFFFF" opacity="0.75"/>')


def sequence(y, codes, bad, ok):
    out, xs = [], [104.0, 238.0, 372.0, 506.0][:len(codes)]
    for i, (x, code) in enumerate(zip(xs, codes)):
        frame = RED if i in bad else (GREEN if i == len(codes) - 1 else None)
        out.append(display(f"{U}q{y}{i}", x - 46, y - 18, 92, 36, code, "#FF6B5E" if i in bad else AMBER, 17.0, frame))
        if i:
            out.append(M.arrow(xs[i - 1] + 50, y, x - 52, y, GREEN if ok else RED, width=2.2, halo=False))
    end = xs[len(codes) - 1] + 76
    if ok:
        out.append(f'<path d="M{n(end - 11)} {n(y)} l7 8 l15 -17" fill="none" stroke="{GREEN}" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>')
    else:
        out.append(f'<path d="M{n(end - 9)} {n(y - 9)} l18 18 M{n(end + 9)} {n(y - 9)} l-18 18" stroke="{RED}" stroke-width="4.4" stroke-linecap="round"/>')
    return "".join(out)


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', unit(), selector()]
    out.append(display(f"{U}d", 228, 40, 260, 54, "4600"))
    for x in DIGITS_X:
        out.append(knob(x, 140, 16))
    out.append(ident(552, 74) + lamp(552, 136))
    out.append(sequence(250, ["4600", "4200", "7200"], (), True))
    out.append(sequence(320, ["4600", "7600", "7500", "7200"], (1, 2), False))
    c = S.callout
    cx, cy = SEL
    for i, a in enumerate(POS):
        out.append(c(i + 1, cx + 58 * math.sin(math.radians(a)), cy - 58 * math.cos(math.radians(a)), r=9.5))
    out.append(c(6, 500, 160, 470, 146) + c(7, 596, 104, 582, 86) + c(8, 586, 166, 562, 144) + c(9, 34, 250) + c(10, 34, 320))
    return out


def plate():
    return {
        "id": "fig-21-09-transponder",
        "replaces": "fig-21-09-transponder.svg",
        "book_file": "plate-21-09-transponder.jpg",
        "caption": "Figure 21-9. A transponder control head and a safe way to change the code",
        "desc": "Figure 21-9. A transponder control head and a safe way to change the code",
        "legend": [
            "Off.",
            "Standby: warmed up, not replying.",
            "On: replies with the code (Mode A).",
            "Altitude: code and pressure altitude (Modes A and C), the normal position in flight.",
            "Test.",
            "The code, one knob per digit.",
            "Ident: press only when ATC asks.",
            "Reply light.",
            "From 4600 to 7200 safely: the second knob first (4200), then the first (7200).",
            "The unsafe order passes 7600 and 7500.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-21-09-transponder.svg", "blank": True, "layers": layers()},
    }
