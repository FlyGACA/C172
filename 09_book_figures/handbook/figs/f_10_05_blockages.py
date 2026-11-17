"""Figure 10-5 (new). What each blockage of the pitot-static system does to the three instruments, from the table of Chapter 10 ("When the pitot-static system is blocked"): three rows, three instruments each.

Row 1, pitot opening blocked and drain open: the airspeed indicator falls to zero, altimeter and VSI normal. Row 2, pitot opening and drain both blocked: the airspeed indicator acts like an altimeter (an up arrow for a climb,
a down arrow for a descent), altimeter and VSI normal. Row 3, static ports blocked and pitot clear: the airspeed indicator reads low above the altitude where the blockage occurred and high below it (a down arrow above a line, an up arrow below),
the altimeter is frozen (a padlock on the dial) and the VSI reads zero. Normal readings carry a green tick. On the left, the pitot head with its opening and drain (red block where it is blocked) or the static port with its red block.
Generic dials, not the face of any instrument. No words: shapes, colours and the numbers of the callouts."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "bl10"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
ROWY = (70.0, 158.0, 246.0)
COLX = (250.0, 380.0, 510.0)
R = 30.0


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            + "".join(f'<line x1="22" y1="{n(y)}" x2="{W - 22}" y2="{n(y)}" stroke="{SLATE}" stroke-opacity="0.18" stroke-width="1"/>' for y in (114.0, 202.0)))


def arrow(x0, y0, x1, y1, col, width=3.4, head=8.0):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * head * 0.62)} {n(hy + ny * head * 0.62)} L{n(hx - nx * head * 0.62)} {n(hy - ny * head * 0.62)} Z" fill="{col}"/>')


def dial(cx, cy, needle, col=INK, zero=False):
    """A round dial: face, a ring of ticks and a needle at `needle` degrees (0 = up, clockwise)."""
    out = [f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(R)}" fill="#FFFFFF" stroke="{SLATE}" stroke-width="2.4" filter="url(#{U}ds)"/>']
    for k in range(12):
        a = math.radians(k * 30)
        r0, r1 = R - 7, R - 3
        out.append(f'<line x1="{n(cx + r0 * math.sin(a))}" y1="{n(cy - r0 * math.cos(a))}" x2="{n(cx + r1 * math.sin(a))}" y2="{n(cy - r1 * math.cos(a))}" stroke="{SLATE}" stroke-width="1.4"/>')
    a = math.radians(needle)
    out.append(f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + (R - 9) * math.sin(a))}" y2="{n(cy - (R - 9) * math.cos(a))}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>'
               f'<circle cx="{n(cx)}" cy="{n(cy)}" r="3.4" fill="{col}"/>')
    return "".join(out)


def tick(x, y):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="9" fill="{GREEN}" stroke="#FFFFFF" stroke-width="1.4" filter="url(#{U}ds)"/>'
            f'<path d="M{n(x - 4.4)} {n(y + 0.4)} L{n(x - 1)} {n(y + 3.8)} L{n(x + 4.8)} {n(y - 3.6)}" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')


def padlock(x, y):
    return (f'<path d="M{n(x - 5)} {n(y - 2)} v-4 a5 5 0 0 1 10 0 v4" fill="none" stroke="{SLATE}" stroke-width="2.2"/>'
            f'<rect x="{n(x - 8)}" y="{n(y - 2)}" width="16" height="12" rx="2.4" fill="{BLUE}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>')


def head(i):
    """On the left: the pitot head (opening at the tip, drain underneath) or the static port, with the red block where it is blocked."""
    cx, cy = 100.0, ROWY[i]
    out = []
    if i < 2:
        out.append(f'<path d="M{n(cx - 44)} {n(cy - 8)} L{n(cx - 4)} {n(cy - 8)} L{n(cx + 40)} {n(cy - 12)} L{n(cx + 40)} {n(cy + 12)} L{n(cx - 4)} {n(cy + 8)} L{n(cx - 44)} {n(cy + 8)} Z" fill="#CBD5E1" stroke="{SLATE}" stroke-width="1.6" stroke-linejoin="round" transform="translate(0 0)" filter="url(#{U}ds)"/>')
        out.append(f'<ellipse cx="{n(cx - 44)}" cy="{n(cy)}" rx="4.6" ry="8" fill="{INK}"/>')                       # the opening, at the tip
        out.append(f'<circle cx="{n(cx - 14)}" cy="{n(cy + 8)}" r="2.8" fill="{INK}"/>')                           # the drain hole, underneath
        out.append(f'<rect x="{n(cx + 40)}" y="{n(cy - 6)}" width="14" height="12" fill="{SLATE}"/>')              # the mast
        out.append(f'<ellipse cx="{n(cx - 46)}" cy="{n(cy)}" rx="5.6" ry="9.4" fill="{RED}" stroke="#FFFFFF" stroke-width="1.4"/>')            # the opening is blocked
        if i == 1:
            out.append(f'<circle cx="{n(cx - 14)}" cy="{n(cy + 8)}" r="5" fill="{RED}" stroke="#FFFFFF" stroke-width="1.4"/>')                  # and the drain too
    else:
        out.append(f'<rect x="{n(cx - 8)}" y="{n(cy - 28)}" width="18" height="56" rx="5" fill="#CBD5E1" stroke="{SLATE}" stroke-width="1.6" filter="url(#{U}ds)"/>')
        out.append(f'<circle cx="{n(cx + 1)}" cy="{n(cy)}" r="6" fill="{INK}"/><circle cx="{n(cx + 1)}" cy="{n(cy)}" r="8.6" fill="{RED}" fill-opacity="0.9" stroke="#FFFFFF" stroke-width="1.4"/>')
        out.append(f'<line x1="{n(cx - 3)}" y1="{n(cy - 4)}" x2="{n(cx + 5)}" y2="{n(cy + 4)}" stroke="#FFFFFF" stroke-width="2"/><line x1="{n(cx + 5)}" y1="{n(cy - 4)}" x2="{n(cx - 3)}" y2="{n(cy + 4)}" stroke="#FFFFFF" stroke-width="2"/>')
    return "".join(out)


def cells():
    out = []
    # row 1: pitot blocked, drain open: ASI to zero, altimeter and VSI normal
    y = ROWY[0]
    out += [dial(COLX[0], y, -150, RED), H.glyph_text("0", COLX[0], y + 14, 6.0, SLATE, spacing=0.3), dial(COLX[1], y, 70), tick(COLX[1] + 26, y - 24), dial(COLX[2], y, 20), tick(COLX[2] + 26, y - 24)]
    # row 2: both blocked: ASI works like an altimeter (arrows up and down), altimeter and VSI normal
    y = ROWY[1]
    out += [dial(COLX[0], y, 60, AMBER), arrow(COLX[0] + 40, y + 6, COLX[0] + 40, y - 14, AMBER, 3.0, 7.0), arrow(COLX[0] + 52, y - 14, COLX[0] + 52, y + 6, AMBER, 3.0, 7.0),
            dial(COLX[1], y, 70), tick(COLX[1] + 26, y - 24), dial(COLX[2], y, 20), tick(COLX[2] + 26, y - 24)]
    # row 3: static blocked: ASI reads low above the altitude of the blockage and high below it, altimeter frozen, VSI zero
    y = ROWY[2]
    out += [dial(COLX[0], y, 40, AMBER), arrow(COLX[0] + 46, y - 20, COLX[0] + 46, y - 4, RED, 3.0, 7.0),
            f'<line x1="{n(COLX[0] + 36)}" y1="{n(y)}" x2="{n(COLX[0] + 56)}" y2="{n(y)}" stroke="{SLATE}" stroke-width="1.8"/>', arrow(COLX[0] + 46, y + 20, COLX[0] + 46, y + 4, GREEN, 3.0, 7.0),
            dial(COLX[1], y, 70), padlock(COLX[1] + 30, y - 26), dial(COLX[2], y, 90), H.glyph_text("0", COLX[2], y + 14, 6.0, SLATE, spacing=0.3)]
    return "".join(out)


def heads():
    out = []
    for x, label in zip(COLX, ("KT", "FT", "FT/MIN")):
        w = 6.0 * 3.6 + 12.0 + (8.0 if label == "FT/MIN" else 0.0)
        out.append(f'<rect x="{n(x - w / 2)}" y="{n(14.0)}" width="{n(w)}" height="12" rx="6" fill="{SLATE}" stroke="#FFFFFF" stroke-width="1.2"/>')
        out.append(H.glyph_text(label, x, 20.0, 5.6, "#FFFFFF", spacing=0.35))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join(c(i + 1, 36.0, ROWY[i] - 22, r=9.5) for i in range(3))


def layers():
    return [H.defs(U, W, HT), background(), *[head(i) for i in range(3)], heads(), cells(), callouts()]


def plate():
    return {
        "id": "fig-10-05-blockages",
        "replaces": "fig-10-05-blockages.svg",           # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-10-05-blockages.jpg",
        "caption": "Figure 10-5. What each blockage of the pitot-static system does to the airspeed indicator, altimeter and VSI",
        "desc": ("Figure 10-5. What each blockage of the pitot-static system does to the three instruments. Row 1: pitot opening blocked, drain open. Row 2: pitot opening and drain both blocked. "
                 "Row 3: static ports blocked, pitot clear. Normal readings carry a green tick."),
        "legend": [
            "Pitot opening blocked, drain open: the airspeed indicator falls to zero; the altimeter and the VSI are normal. From left to right: airspeed indicator, altimeter, VSI.",
            "Pitot opening and drain both blocked: the airspeed indicator acts like an altimeter, rising in a climb and falling in a descent and ignoring real speed changes (the two arrows); the altimeter and the VSI are normal. A pilot who believes the airspeed may raise the nose further and stall: trust attitude, power and the view outside.",
            "Static ports blocked, pitot clear: the airspeed indicator reads low above the altitude where the blockage occurred and high below it (the two arrows); the altimeter is frozen (the padlock) and the VSI reads zero. Open the alternate static source to confirm.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
