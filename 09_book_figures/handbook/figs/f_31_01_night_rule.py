"""Figure 31-1 (new). Night flying in the Kingdom, from the first section of Chapter 31: the time of the rule, the course's night training, the AIP's night training exercises and the passenger rule.

Above, 1: a day-to-night-to-day sky from sunset to sunrise, the period of section 91.171 as a red band from sunset (no VFR without an authorization or local ATC conditions) and the GACAR's night (end of evening civil twilight to beginning of morning civil twilight) as a darker band inside it: the dusk already counts.
Below, three tiles (2 and 3 on night renders of a generic aerodrome lit with permanent runway lights, figs/oeth3d.night_aerodrome_31_01: from the approach, and the tower and the runway from further off): 2 the course (3 H, a cross-country of more than 100 NM, 10 takeoffs and 10 full-stop landings); 3 some of the AIP's conditions for a night training exercise (the tower operating, 8 KM, a ceiling 1 000 FT above the procedure turn altitude, the same aerodrome at both ends);
4 carrying passengers (3 takeoffs and 3 full-stop landings within 90 days, between 1 H after sunset and 1 H before sunrise). The time line has no scale."""
import json
import math
import os

from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 356
U = "nt3101"
INK, SLATE, BLUE, GREEN, AMBER, RED, VIOLET = "#1E293B", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#7C3AED"
SHADOW = {"dx": 1.4, "dy": 2.6, "blur": 2.0, "opacity": 0.26}
OUT = {"width": 0.5, "colour": "#2B3648", "opacity": 0.85}


def gwidth(s, height, spacing=0.4):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(cx, cy, text, fill, size=8.4):
    return chip(cx, cy, text, fill, size=size)


def icon(kind, x, y, col):
    """A small sign drawn in a chip, left of its text: up (a takeoff), down (a landing), clock, route."""
    if kind == "up":
        return (f'<path d="M{n(x - 3.6)} {n(y + 3.2)} L{n(x + 3.0)} {n(y - 3.2)}" stroke="{col}" stroke-width="1.7" stroke-linecap="round"/>'
                f'<path d="M{n(x + 3.8)} {n(y - 4.0)} l-4.4 0.6 l3.8 3.8 Z" fill="{col}"/>')
    if kind == "down":
        return (f'<path d="M{n(x - 3.6)} {n(y - 3.2)} L{n(x + 3.0)} {n(y + 3.2)}" stroke="{col}" stroke-width="1.7" stroke-linecap="round"/>'
                f'<path d="M{n(x + 3.8)} {n(y + 4.0)} l-4.4 -0.6 l3.8 -3.8 Z" fill="{col}"/><path d="M{n(x - 4.2)} {n(y + 4.6)} H{n(x + 4.6)}" stroke="{col}" stroke-width="1.2" stroke-linecap="round"/>')
    if kind == "clock":
        return (f'<circle cx="{n(x)}" cy="{n(y)}" r="3.9" fill="none" stroke="{col}" stroke-width="1.4"/>'
                f'<path d="M{n(x)} {n(y - 2.3)} V{n(y)} L{n(x + 1.8)} {n(y + 1.1)}" fill="none" stroke="{col}" stroke-width="1.2" stroke-linecap="round"/>')
    if kind == "route":
        return (f'<circle cx="{n(x - 3.4)}" cy="{n(y + 2.4)}" r="1.5" fill="{col}"/><circle cx="{n(x + 3.4)}" cy="{n(y - 2.4)}" r="1.5" fill="{col}"/>'
                f'<path d="M{n(x - 3.4)} {n(y + 2.4)} Q{n(x)} {n(y + 2.4)} {n(x + 3.4)} {n(y - 2.4)}" fill="none" stroke="{col}" stroke-width="1.1" stroke-dasharray="1.6 1.4"/>')
    return ""


def chip(cx, cy, text, accent, kind=None, size=7.8):
    return M.chip(cx, cy, text, accent, size=size, kind=kind, dark=True)


def flight(p0, c, p1, col, dash=False, width=2.2):
    """A path in the air: a smooth curve from p0 to p1 bent towards c, a dark halo under it and an arrowhead along its end."""
    d = f"M{n(p0[0])} {n(p0[1])} Q{n(c[0])} {n(c[1])} {n(p1[0])} {n(p1[1])}"
    tx, ty = p1[0] - c[0], p1[1] - c[1]
    L = math.hypot(tx, ty) or 1.0
    ux, uy = tx / L, ty / L
    s = 6.5
    bx, by = p1[0] - ux * s, p1[1] - uy * s
    head = f'M{n(p1[0] + ux * 1.5)} {n(p1[1] + uy * 1.5)} L{n(bx - uy * s * 0.55)} {n(by + ux * s * 0.55)} L{n(bx + uy * s * 0.55)} {n(by - ux * s * 0.55)} Z'
    da = ' stroke-dasharray="5 4"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="#0B1224" stroke-opacity="0.45" stroke-width="{n(width + 2.6)}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{n(width)}" stroke-linecap="round"{da}/>'
            f'<path d="{head}" fill="{col}" stroke="#0B1224" stroke-opacity="0.45" stroke-width="0.8"/>')


def ds():
    return f' filter="url(#{U}ds)"'


def timeline():
    """Tile 1: from day through the night to day, as a horizon: the sun sets into the dunes and rises out of them, a crescent moon and stars between; under the
    horizon the time bars (the period of section 91.171 in red, the GACAR's night in slate inside it); above it the hour after sunset and the hour before
    sunrise as dimension lines."""
    x, y, w, h = 12.0, 12.0, 616.0, 150.0
    uid = f"{U}tl"
    ss, ct, mt, sr = x + 110, x + 190, x + w - 190, x + w - 110   # sunset, end of civil twilight, start of morning twilight, sunrise
    f = lambda xx: n((xx - x) / w)
    defs = (f'<defs><linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="#8CBDEB"/><stop offset="{f(ss - 40)}" stop-color="#C9B79A"/><stop offset="{f(ss)}" stop-color="#F2A766"/>'
            f'<stop offset="{f(ct)}" stop-color="#4A4F86"/><stop offset="{f(ct + 60)}" stop-color="#1B2550"/><stop offset="0.5" stop-color="#0E1532"/>'
            f'<stop offset="{f(mt - 60)}" stop-color="#1B2550"/><stop offset="{f(mt)}" stop-color="#4A4F86"/><stop offset="{f(sr)}" stop-color="#F5B676"/>'
            f'<stop offset="{f(sr + 40)}" stop-color="#C9C2AC"/><stop offset="1" stop-color="#93C3EE"/></linearGradient>'
            f'<linearGradient id="{uid}v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000814" stop-opacity="0.35"/><stop offset="0.75" stop-color="#000814" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="{uid}d" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B3226"/><stop offset="1" stop-color="#1A1610"/></linearGradient>'
            f'<radialGradient id="{uid}s"><stop offset="0" stop-color="#FFE7A8" stop-opacity="0.95"/><stop offset="0.35" stop-color="#FFC56B" stop-opacity="0.55"/><stop offset="1" stop-color="#FF9E4A" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.0" stdDeviation="1.1" flood-color="#000814" flood-opacity="0.45"/></filter>'
            f'<filter id="{uid}gl" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>')
    gy = y + 92
    body = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{uid}g)"/><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(gy - y)}" fill="url(#{uid}v)"/>'
    for k in range(26):                                   # stars: small, of several sizes, only where the sky is dark
        sx = ct + 30 + (k * 47.9) % (mt - ct - 60)
        sy = y + 8 + (k * 29.3) % 64
        r = (0.55, 0.8, 1.1)[k % 3]
        body += f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(r)}" fill="#FFFFFF" fill-opacity="{n(0.45 + 0.18 * (k % 3))}"/>'
    mx, my = x + w / 2 + 44, y + 30                       # a crescent moon
    body += (f'<circle cx="{n(mx)}" cy="{n(my)}" r="9" fill="#F4ECCB"/><circle cx="{n(mx + 4.2)}" cy="{n(my - 2.6)}" r="8.2" fill="#0F1736"/>')
    for cx_ in (ss, sr):                                  # the sun on the horizon, in its glow
        body += f'<circle cx="{n(cx_)}" cy="{n(gy)}" r="40" fill="url(#{uid}s)"/><circle cx="{n(cx_)}" cy="{n(gy + 3)}" r="11.5" fill="#FFD98A"/>'
    dune = (f'M{n(x)} {n(gy + 2)} C{n(x + 80)} {n(gy - 5)} {n(x + 150)} {n(gy + 4)} {n(x + 230)} {n(gy)} S{n(x + 380)} {n(gy - 6)} {n(x + 460)} {n(gy + 1)} '
            f'S{n(x + 560)} {n(gy - 4)} {n(x + w)} {n(gy + 1)} V{n(y + h)} H{n(x)} Z')
    body += f'<path d="{dune}" fill="url(#{uid}d)"/>'
    for cx_, up in ((ss, False), (sr, True)):             # a chevron over each sun: setting, rising
        a, b = (gy - 22, gy - 16) if up else (gy - 16, gy - 22)
        body += f'<path d="M{n(cx_ - 5)} {n(b)} L{n(cx_)} {n(a)} L{n(cx_ + 5)} {n(b)}" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    guides = "".join(f'<line x1="{n(xx)}" y1="{n(y + 6)}" x2="{n(xx)}" y2="{n(y + h - 8)}" stroke="#FFFFFF" stroke-opacity="0.38" stroke-width="1" stroke-dasharray="2 3"/>' for xx in (ss, ct, mt, sr))
    ty1, ty2 = gy + 20, gy + 38                           # the time bars, under the horizon
    bars = (f'<line x1="{n(x + 14)}" y1="{n(ty1)}" x2="{n(x + w - 14)}" y2="{n(ty1)}" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="1.2"/>'
            f'<rect x="{n(ss)}" y="{n(ty1 - 4)}" width="{n(sr - ss)}" height="8" rx="4" fill="#EF4444" filter="url(#{uid}gl)" opacity="0.55"/>'
            f'<rect x="{n(ss)}" y="{n(ty1 - 4)}" width="{n(sr - ss)}" height="8" rx="4" fill="#DC2626"/>'
            f'<rect x="{n(ct)}" y="{n(ty2 - 3.5)}" width="{n(mt - ct)}" height="7" rx="3.5" fill="#94A3B8"/>'
            + "".join(f'<circle cx="{n(xx)}" cy="{n(yy)}" r="2.4" fill="#FFFFFF"/>' for xx, yy in ((ss, ty1), (sr, ty1), (ct, ty2), (mt, ty2))))
    p0, p1 = ss + 64, sr - 64                             # the passenger window, 1 H after sunset to 1 H before sunrise
    dy = y + 18
    def dimline(a, b):
        return (f'<line x1="{n(a)}" y1="{n(dy)}" x2="{n(b)}" y2="{n(dy)}" stroke="#FDE68A" stroke-width="1.5"/>'
                + "".join(f'<line x1="{n(xx)}" y1="{n(dy - 4)}" x2="{n(xx)}" y2="{n(dy + 4)}" stroke="#FDE68A" stroke-width="1.5"/>' for xx in (a, b)))
    dims = dimline(ss, p0) + dimline(p1, sr) + chip((ss + p0) / 2, dy + 14, "1 H", AMBER, "clock", size=7.0) + chip((sr + p1) / 2, dy + 14, "1 H", AMBER, "clock", size=7.0)
    return defs + f'<g clip-path="url(#{uid}c)">' + body + guides + bars + dims + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>'


TX = (12.0, 220.0, 428.0)
TY, TW, TH = 174.0, 200.0, 170.0


HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NIGHT = [(0.0, "#050916"), (0.6, "#131C3A"), (1.0, "#2E3B66")]          # the sky of the night renders (figs/oeth3d.night_aerodrome_31_01), drawn under them


def at(rid, x):
    """The anchors of a night render laid over the tile at x (canvas units)."""
    with open(os.path.join(HERE, "renders", rid + ".anchors.json"), encoding="utf-8") as f:
        d = json.load(f)
    return lambda k: (x + d["anchors"][k][0] * TW, TY + d["anchors"][k][1] * TH)


def render_tile(uid, x, rid):
    """A tile whose picture is a night render of the generic aerodrome, with the sky drawn under it: [the card and the sky, the render, the frame]."""
    under = (f'<defs><clipPath id="{uid}c"><rect x="{n(x)}" y="{n(TY)}" width="{n(TW)}" height="{n(TH)}" rx="9"/></clipPath>'
             f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="1.6" stdDeviation="1.8" flood-color="#10233F" flood-opacity="0.26"/></filter></defs>'
             f'<rect x="{n(x)}" y="{n(TY)}" width="{n(TW)}" height="{n(TH)}" rx="9" fill="#FFFFFF" filter="url(#{uid}s)"/>'
             f'<g clip-path="url(#{uid}c)">' + S.sky(uid + "k", x, TY, TW, TH * 0.5, NIGHT) + '</g>')
    img = {"name": rid, "at": [x + TW / 2, TY + TH / 2], "width": TW, "whole": True}
    k = 0.5523 * 9.0                                       # white over the square corners of the render outside the card's round ones
    x1, y0, y1, r = x + TW, TY, TY + TH, 9.0
    corners = "".join(f'<path d="{d}" fill="#ffffff"/>' for d in (
        f"M{n(x)} {n(y0)} L{n(x + r)} {n(y0)} C{n(x + r - k)} {n(y0)} {n(x)} {n(y0 + r - k)} {n(x)} {n(y0 + r)} Z",
        f"M{n(x1)} {n(y0)} L{n(x1)} {n(y0 + r)} C{n(x1)} {n(y0 + r - k)} {n(x1 - r + k)} {n(y0)} {n(x1 - r)} {n(y0)} Z",
        f"M{n(x)} {n(y1)} L{n(x)} {n(y1 - r)} C{n(x)} {n(y1 - r + k)} {n(x + r - k)} {n(y1)} {n(x + r)} {n(y1)} Z",
        f"M{n(x1)} {n(y1)} L{n(x1 - r)} {n(y1)} C{n(x1 - r + k)} {n(y1)} {n(x1)} {n(y1 - r + k)} {n(x1)} {n(y1 - r)} Z"))
    frame = corners + f'<rect x="{n(x)}" y="{n(TY)}" width="{n(TW)}" height="{n(TH)}" rx="9" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>'
    return under, img, frame


def course():
    """Tile 2: the runway lit at night from the approach (render night-31-01-runway); 3 H above, 10 takeoffs and 10 full-stop landings at the runway, >100 NM below."""
    x = TX[0]
    under, img, frame = render_tile(f"{U}t2", x, "night-31-01-runway")
    a = at("night-31-01-runway", x)
    (tx, ty), (ex, ey) = a("thr"), a("end")
    o = chip(x + 46, TY + 150, "3 H", BLUE, "clock", size=8.4)
    o += flight((ex, ey - 3), (ex - 8, ey - 24), (ex + 2, ey - 42), "#6EE7A0") + chip(ex + 4, ey - 56, "10", GREEN, "up", size=8.4)     # the takeoffs: off the far end, climbing away
    o += flight((tx + 40, ty - 52), (tx + 34, ty - 8), (tx + 6, ty - 3), "#FCA5A5") + chip(tx + 40, ty - 66, "10", RED, "down", size=8.4)  # the landings: down to the threshold
    o += chip(x + TW - 54, TY + 150, ">100 NM", VIOLET, "route", size=8.4)
    return [under, img, o + frame]


def exercise():
    """Tile 3: the tower and the runway lit at night (render night-31-01-tower); the ceiling 1 000 FT above, 8 KM, and a loop back to the same aerodrome."""
    x = TX[1]
    under, img, frame = render_tile(f"{U}t3", x, "night-31-01-tower")
    mx, my = x + TW * 0.36, TY + TH * 0.72                  # on the runway in the front of the view
    cl = TY + 46                                           # the ceiling: a layer of cloud above, its base dashed
    o = (f'<defs><linearGradient id="{U}cl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#CBD5E1" stop-opacity="0.0"/><stop offset="1" stop-color="#CBD5E1" stop-opacity="0.30"/></linearGradient></defs>'
         f'<rect x="{n(x)}" y="{n(TY)}" width="{n(TW)}" height="{n(cl - TY)}" fill="url(#{U}cl)"/>'
         f'<line x1="{n(x + 8)}" y1="{n(cl)}" x2="{n(x + TW - 8)}" y2="{n(cl)}" stroke="#E2E8F0" stroke-opacity="0.85" stroke-width="1.4" stroke-dasharray="6 4"/>')
    o += chip(x + TW - 50, cl - 13, "1 000 FT", AMBER, size=7.8)
    cx_, cy_ = x + TW * 0.47, TY + TH * 0.64              # a local flight: round the aerodrome and back to it, dashed
    o += (f'<ellipse cx="{n(cx_)}" cy="{n(cy_)}" rx="74" ry="21" fill="none" stroke="#0B1224" stroke-opacity="0.45" stroke-width="4.6"/>'
          f'<ellipse cx="{n(cx_)}" cy="{n(cy_)}" rx="74" ry="21" fill="none" stroke="#6EE7A0" stroke-width="2" stroke-dasharray="6 4"/>')
    o += flight((cx_ + 40, cy_ + 17.6), (cx_ + 22, cy_ + 20.6), (cx_ + 4, cy_ + 21), "#6EE7A0")
    o += chip(x + TW - 46, TY + 150, "8 KM", BLUE, size=8.4)
    return [under, img, o + frame]


def passengers():
    x = TX[2]
    under, img, frame = render_tile(f"{U}t4", x, "night-31-01-runway")
    o = f'<rect x="{n(x)}" y="{n(TY)}" width="{n(TW)}" height="{n(TH)}" fill="#0B1226" fill-opacity="0.35"/>'      # the picture dimmed, under the calendar and the passengers
    cx = x + TW / 2
    cw, chh = 60.0, 56.0                                    # a calendar of 90 days: a card with its binding rings, a red head, the number
    cal_x, cal_y = cx - cw / 2, TY + 34
    o += (f'<rect x="{n(cal_x)}" y="{n(cal_y)}" width="{n(cw)}" height="{n(chh)}" rx="6" fill="#F8FAFC"{ds()}/>'
          f'<path d="M{n(cal_x)} {n(cal_y + 6)} a6 6 0 0 1 6 -6 H{n(cal_x + cw - 6)} a6 6 0 0 1 6 6 V{n(cal_y + 15)} H{n(cal_x)} Z" fill="#DC2626"/>'
          + "".join(f'<rect x="{n(cal_x + cw * t - 2)}" y="{n(cal_y - 4)}" width="4" height="9" rx="2" fill="#475569"/>' for t in (0.3, 0.7))
          + H.glyph_text("90", cx, cal_y + 36, 15, "#1E293B", spacing=0.4))
    o += chip(cx - 42, TY + 112, "3", GREEN, "up", size=9.0) + chip(cx + 42, TY + 112, "3", RED, "down", size=9.0)
    for k in range(3):                                     # three passengers: a head and shoulders each, the middle one a little nearer
        hx, s_ = cx - 22 + k * 22, (1.0, 1.12, 1.0)[k]
        top = TY + 136
        o += (f'<circle cx="{n(hx)}" cy="{n(top)}" r="{n(5.4 * s_)}" fill="#E2E8F0"/>'
              f'<path d="M{n(hx - 9.5 * s_)} {n(top + 19 * s_)} C{n(hx - 9.5 * s_)} {n(top + 8 * s_)} {n(hx + 9.5 * s_)} {n(top + 8 * s_)} {n(hx + 9.5 * s_)} {n(top + 19 * s_)} Z" fill="#E2E8F0"/>')
    return [under, img, o + frame]


def callouts():
    c = S.callout
    return c(1, 28, 28, r=10) + c(2, TX[0] + 16, TY + 16, r=10) + c(3, TX[1] + 16, TY + 16, r=10) + c(4, TX[2] + 16, TY + 16, r=10)


def layers():
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', timeline(), *course(), *exercise(), *passengers(), callouts()]


def plate():
    return {
        "id": "fig-31-01-night-rule",
        "replaces": "fig-31-01-night-rule.svg",               # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-31-01-night-rule.jpg",
        "caption": "Figure 31-1. Night flying in the Kingdom: the time of the rule, the course's night training, the AIP's training exercises and the passenger rule",
        "desc": ("Figure 31-1. Night flying in the Kingdom. Above, from sunset to sunrise no VFR without an authorization or local ATC conditions, and the GACAR's night from the end of evening civil twilight inside it. "
                 "Below: the course's 3 hours of night training with a cross-country of more than 100 NM and 10 takeoffs and 10 full-stop landings; some of the AIP's conditions for a night training exercise (the tower, 8 km, a ceiling 1 000 ft above the procedure turn altitude, the same aerodrome at both ends); "
                 "and, to carry passengers from 1 hour after sunset to 1 hour before sunrise, 3 takeoffs and 3 full-stop landings within 90 days."),
        "legend": [
            "From sunset to sunrise no one may fly VFR in KSA airspace unless the President has authorized it or the flight is a local flight under conditions prescribed by the ATC facility (section 91.171). The GACAR's night begins at the end of evening civil twilight, but the prohibition and the lighting rule run from sunset: the dusk already counts.",
            "The course: at least 3 hours of night flight training, with one cross-country flight of more than 100 NM total distance and 10 takeoffs and 10 landings to a full stop, at an aerodrome with permanent runway lights.",
            "The AIP's night VFR training exercises, some of their conditions: the tower operating and an ATC clearance, a reported visibility of 8 km or more, a ceiling at least 1 000 ft above the procedure turn altitude, and the flight beginning and ending at the same aerodrome. The first condition needs an instrument rating: ask your instructor how your school meets it.",
            "Carrying passengers: from 1 hour after sunset to 1 hour before sunrise, only after 3 takeoffs and 3 full-stop landings in that period within the preceding 90 days.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
