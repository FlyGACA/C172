"""Figure 5-4 (new). Static and dynamic stability, in two rows of three.

Top, static stability: the ball in a bowl. After a disturbance the ball (and the aeroplane, with its nose pitched up by a gust, beside each bowl) tends to go back (positive: green), stay where it
was put (neutral: amber) or move further away (negative: red); the arrow is that tendency. Bottom, dynamic stability: the pitch of the aeroplane against time after the same disturbance, the
dashed line being the trimmed pitch: the oscillation dies out (positive: green, what a trainer's pitch does), goes on at the same size (neutral: amber) or grows (negative: red).
The curves are drawn from a damping factor of -0.6, 0 and +0.35 over three cycles; they show the idea, they are not data. No words: colours, arrows and the numbers of the callouts."""
import math

from figs import h_a1 as A1
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "st5"
GREEN, AMBER, RED, SLATE = "#15803D", "#B45309", "#B91C1C", "#475569"
COLS = (120.0, 320.0, 520.0)
TOP, BOTTOM = 30.0, 176.0                                  # the bowls, the curves
CASES = ((GREEN, "positive"), (AMBER, "neutral"), (RED, "negative"))


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            f'<line x1="14" y1="{n(BOTTOM - 14)}" x2="{W - 14}" y2="{n(BOTTOM - 14)}" stroke="{SLATE}" stroke-opacity="0.25" stroke-width="1"/>')


def surface(i):
    """The bowl, the plain or the hill, 130 units wide, its middle point at (COLS[i], TOP + 86)."""
    x, y0 = COLS[i], TOP + 80.0
    if i == 0:
        d = f"M{n(x - 64)} {n(y0 - 40)} C{n(x - 40)} {n(y0 + 8)} {n(x + 40)} {n(y0 + 8)} {n(x + 64)} {n(y0 - 40)}"
    elif i == 1:
        d = f"M{n(x - 64)} {n(y0)} L{n(x + 64)} {n(y0)}"
    else:
        d = f"M{n(x - 64)} {n(y0 + 36)} C{n(x - 40)} {n(y0 - 12)} {n(x + 40)} {n(y0 - 12)} {n(x + 64)} {n(y0 + 36)}"
    return f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{SLATE}" stroke-width="3.4" stroke-linecap="round"/>'


def ball(i):
    """The ball a little way from the middle, and the arrow of its tendency."""
    x, y0 = COLS[i], TOP + 80.0
    r = 8.5
    col = CASES[i][0]
    out = []
    if i == 0:                                              # on the slope of the bowl, to the left of the bottom; the arrow points down the slope, toward the bottom
        bx = x - 38.0
        by = _bowl(x, y0, bx) - r
        out.append(_ball(bx, by, r, col))
        out.append(_arrow(bx + 14, by + 8, bx + 38, by + 18, col))
    elif i == 1:
        bx, by = x - 20.0, y0 - r
        out.append(_ball(bx, by, r, col))
        out.append(f'<line x1="{n(bx + 16)}" y1="{n(by)}" x2="{n(bx + 30)}" y2="{n(by)}" stroke="{col}" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="1 5"/>')
    else:                                                   # on the top of the hill, a little to the left of the crest; the arrow points down the slope, away
        bx = x - 14.0
        by = _hill(x, y0, bx) - r
        out.append(_ball(bx, by, r, col))
        out.append(_arrow(bx - 12, by + 4, bx - 40, by + 22, col))
    return "".join(out)


def _bowl(x, y0, bx):
    # the cubic's shape: sample it
    p0, p1, p2, p3 = (x - 64, y0 - 40), (x - 40, y0 + 8), (x + 40, y0 + 8), (x + 64, y0 - 40)
    best = None
    for k in range(401):
        t = k / 400.0
        px = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]
        py = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
        if best is None or abs(px - bx) < best[0]:
            best = (abs(px - bx), py)
    return best[1]


def _hill(x, y0, bx):
    p0, p1, p2, p3 = (x - 64, y0 + 36), (x - 40, y0 - 12), (x + 40, y0 - 12), (x + 64, y0 + 36)
    best = None
    for k in range(401):
        t = k / 400.0
        px = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]
        py = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
        if best is None or abs(px - bx) < best[0]:
            best = (abs(px - bx), py)
    return best[1]


def _ball(x, y, r, col):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{col}" stroke="#FFFFFF" stroke-width="1.6" filter="url(#{U}ds)"/>'
            f'<circle cx="{n(x - r * 0.32)}" cy="{n(y - r * 0.34)}" r="{n(r * 0.3)}" fill="#FFFFFF" fill-opacity="0.55"/>')


def _arrow(x0, y0, x1, y1, col):
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - 7 * math.cos(ang), y1 - 7 * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    return (f'<line x1="{n(x0)}" y1="{n(y0)}" x2="{n(hx)}" y2="{n(hy)}" stroke="{col}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<path d="M{n(x1)} {n(y1)} L{n(hx + nx * 4.4)} {n(hy + ny * 4.4)} L{n(hx - nx * 4.4)} {n(hy - ny * 4.4)} Z" fill="{col}"/>')


def planes():
    out = []
    for i, x in enumerate(COLS):
        out.append(A1.plane_mid(x + 34, TOP + 10, angle=-14.0, width=46))
    return out


def tendencies():
    """Beside each bowl, the plane's pitch-up and the way it tends to go: back (green), nowhere (amber) or on up (red)."""
    out = []
    for i, x in enumerate(COLS):
        col = CASES[i][0]
        cx, cy = x + 34, TOP + 28
        if i == 0:
            out.append(_arrow(cx + 16, cy - 2, cx - 6, cy + 14, col))             # nose coming back down
        elif i == 1:
            out.append(f'<line x1="{n(cx - 12)}" y1="{n(cy + 6)}" x2="{n(cx + 14)}" y2="{n(cy + 6)}" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="1 5"/>')
        else:
            out.append(_arrow(cx - 6, cy + 4, cx + 14, cy - 16, col))              # nose going on up
    return "".join(out)


def curves():
    out = []
    y_mid = BOTTOM + 58.0
    for i, x in enumerate(COLS):
        col = CASES[i][0]
        x0, x1 = x - 76.0, x + 76.0
        out.append(f'<line x1="{n(x0)}" y1="{n(y_mid + 40)}" x2="{n(x1)}" y2="{n(y_mid + 40)}" stroke="{SLATE}" stroke-width="1.2"/><line x1="{n(x0)}" y1="{n(y_mid - 46)}" x2="{n(x0)}" y2="{n(y_mid + 40)}" stroke="{SLATE}" stroke-width="1.2"/>')
        out.append(f'<line x1="{n(x0)}" y1="{n(y_mid)}" x2="{n(x1)}" y2="{n(y_mid)}" stroke="{SLATE}" stroke-opacity="0.7" stroke-width="1" stroke-dasharray="3 3"/>')
        damp = (0.4, 0.0, -0.35)[i]
        a0 = (30.0, 22.0, 12.0)[i]
        pts_ = []
        for k in range(0, 301):
            t = k / 300.0 * 3.0                              # three cycles
            amp = a0 * math.exp(-damp * t)                                       # (the growing one starts smaller so that three cycles fit the frame)
            y = y_mid - amp * math.sin(2 * math.pi * t)
            pts_.append((x0 + 6 + (x1 - x0 - 12) * k / 300.0, y))
        d = "M" + " L".join(f"{n(px)} {n(py)}" for px, py in pts_)
        out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="5.4" stroke-linejoin="round" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{col}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')
        out.append(f'<path d="M{n(x1)} {n(y_mid + 40)} l-6 -3 l0 6 z" fill="{SLATE}"/>')
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.5
    out = []
    for i, x in enumerate(COLS):
        out.append(c(i + 1, x - 66, TOP + 6, r=r))
        out.append(c(i + 4, x - 66, BOTTOM + 18, r=r))
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), *[surface(i) for i in range(3)], *[ball(i) for i in range(3)], tendencies(), curves(), *planes(), callouts()]


def plate():
    return {
        "id": "fig-05-04-stability",
        "replaces": "fig-05-04-stability.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-05-04-stability.jpg",
        "caption": "Figure 5-4. Static and dynamic stability: a ball in a bowl, and the pitch of the aeroplane against time after a gust",
        "desc": ("Figure 5-4. Static and dynamic stability: a ball in a bowl, and the pitch of the aeroplane against time after a gust. Top, the three cases of static stability: the ball and the "
                 "aeroplane tend to go back (positive), to stay (neutral) or to move further away (negative). Bottom, the three cases of dynamic stability: the pitch oscillation dies out, goes on or grows."),
        "legend": [
            "Positive static stability: after a gust the ball, and the aeroplane with its nose pitched up, tend to go back toward where they were. A trainer is built like this.",
            "Neutral static stability: the ball stays where it was put; so would the aeroplane.",
            "Negative static stability: the ball, and the aeroplane, move further from where they were. An aeroplane like this would be hard to fly by hand.",
            "Positive dynamic stability: the pitch oscillates about the trimmed pitch (dashed) and the oscillation dies out. This is what a trainer's pitch does.",
            "Neutral dynamic stability: the oscillation goes on at the same size.",
            "Negative dynamic stability: the oscillation grows.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
