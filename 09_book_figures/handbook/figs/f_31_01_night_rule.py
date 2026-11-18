"""Figure 31-1 (new). Night flying in the Kingdom, from the first section of Chapter 31: the time of the rule, the course's night training, the AIP's night training exercises and the passenger rule.

Above, 1: a day-to-night-to-day sky from sunset to sunrise, the period of section 91.171 as a red band from sunset (no VFR without an authorization or local ATC conditions) and the GACAR's night (end of evening civil twilight to beginning of morning civil twilight) as a darker band inside it: the dusk already counts.
Below, three tiles: 2 the course (3 H, a cross-country of more than 100 NM, 10 takeoffs and 10 full-stop landings); 3 some of the AIP's conditions for a night training exercise (the tower operating, 8 KM, a ceiling 1 000 FT above the procedure turn altitude, the same aerodrome at both ends);
4 carrying passengers (3 takeoffs and 3 full-stop landings within 90 days, between 1 H after sunset and 1 H before sunrise). The time line has no scale."""
import math

from figs import h_b2 as H
from figs import h_rich as R
from figs import scene as S

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
    w = gwidth(text, size) + 14.0
    h = size + 8.0
    return f'<rect x="{n(cx - w / 2)}" y="{n(cy - h / 2)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" fill="{fill}" stroke="#FFFFFF" stroke-width="1.5"/>' + H.glyph_text(text, cx, cy, size, "#FFFFFF", spacing=0.4)


def ds():
    return f' filter="url(#{U}ds)"'


def timeline():
    x, y, w, h = 12.0, 12.0, 616.0, 150.0
    uid = f"{U}tl"
    ss, ct, mt, sr = x + 110, x + 190, x + w - 190, x + w - 110   # sunset, end of civil twilight, start of morning twilight, sunrise
    sky = (f'<defs><linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="0">'
           f'<stop offset="0" stop-color="#7FB2E6"/><stop offset="{n((ss - x) / w)}" stop-color="#E9A86B"/><stop offset="{n((ct - x) / w)}" stop-color="#3B4D86"/>'
           f'<stop offset="0.5" stop-color="#121B3A"/><stop offset="{n((mt - x) / w)}" stop-color="#3B4D86"/><stop offset="{n((sr - x) / w)}" stop-color="#F0B47A"/><stop offset="1" stop-color="#8DBDEB"/></linearGradient>'
           f'<clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9"/></clipPath>'
           f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter></defs>')
    gy = y + 96
    body = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{uid}g)"/>'
    body += f'<rect x="{n(x)}" y="{n(gy)}" width="{n(w)}" height="{n(y + h - gy)}" fill="#3A3428" fill-opacity="0.82"/>'
    for k in range(18):                                   # stars in the dark middle
        sx = ct + 10 + (k * 37.3) % (mt - ct - 20)
        sy = y + 10 + (k * 23.7) % 60
        body += f'<circle cx="{n(sx)}" cy="{n(sy)}" r="{n(1.0 + (k % 3) * 0.5)}" fill="#FFFFFF" fill-opacity="0.85"/>'
    for cx in (ss, sr):                                   # the sun on the horizon
        body += f'<circle cx="{n(cx)}" cy="{n(gy)}" r="16" fill="#FFD27A" stroke="#FFFFFF" stroke-width="1.6"/>'
    body += f'<rect x="{n(x)}" y="{n(gy)}" width="{n(w)}" height="{n(y + h - gy)}" fill="#3A3428"/>'
    # the bands
    band = (f'<rect x="{n(ss)}" y="{n(gy + 10)}" width="{n(sr - ss)}" height="14" rx="4" fill="{RED}" stroke="#FFFFFF" stroke-width="1.2"/>'
            f'<rect x="{n(ct)}" y="{n(gy + 30)}" width="{n(mt - ct)}" height="10" rx="3" fill="#94A3B8" stroke="#FFFFFF" stroke-width="1"/>'
            + "".join(f'<line x1="{n(xx)}" y1="{n(y + 4)}" x2="{n(xx)}" y2="{n(gy + 44)}" stroke="#FFFFFF" stroke-width="1.6" stroke-dasharray="4 4" stroke-opacity="0.85"/>' for xx in (ss, ct, mt, sr)))
    # the passenger window, 1 H after sunset to 1 H before sunrise
    p0, p1 = ss + 64, sr - 64
    band += f'<path d="M{n(ss)} {n(y + 14)} H{n(p0)} M{n(sr)} {n(y + 14)} H{n(p1)}" stroke="#FDE68A" stroke-width="2.4"/>' + pill((ss + p0) / 2, y + 26, "1 H", AMBER, size=7.4) + pill((sr + p1) / 2, y + 26, "1 H", AMBER, size=7.4)
    return sky + f'<g clip-path="url(#{uid}c)">' + body + band + f'</g><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="9" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>'


TX = (12.0, 220.0, 428.0)
TY, TW, TH = 174.0, 200.0, 170.0


def course():
    x = TX[0]
    o = R.tile(f"{U}t2", x, TY, TW, TH, "night")
    cx = x + TW / 2
    o += pill(cx, TY + 34, "3 H", BLUE, size=10)
    ry = TY + 112                                          # a runway with 10 up and 10 down
    o += f'<path d="M{n(cx - 70)} {n(ry)} L{n(cx + 70)} {n(ry)} L{n(cx + 80)} {n(ry + 18)} L{n(cx - 80)} {n(ry + 18)} Z" fill="#475569" stroke="#E2E8F0" stroke-width="1"/>'
    o += "".join(f'<circle cx="{n(cx - 74 + k * 18.5)}" cy="{n(ry + 20)}" r="1.8" fill="#FDE68A"/>' for k in range(9))
    o += f'<path d="M{n(cx - 60)} {n(ry - 6)} q20 -2 34 -30" fill="none" stroke="#86EFAC" stroke-width="3" stroke-linecap="round"/><path d="M{n(cx - 26)} {n(ry - 36)} l-1 9 l-7 -4 Z" fill="#86EFAC"/>' + pill(cx - 46, ry - 46, "10", GREEN)
    o += f'<path d="M{n(cx + 26)} {n(ry - 36)} q14 26 34 30" fill="none" stroke="#FCA5A5" stroke-width="3" stroke-linecap="round"/><path d="M{n(cx + 60)} {n(ry - 6)} l-9 -1 l4 -7 Z" fill="#FCA5A5"/>' + pill(cx + 46, ry - 46, "10", RED)
    o += pill(cx, TY + 150, ">100 NM", VIOLET)
    return o


def exercise():
    x = TX[1]
    o = R.tile(f"{U}t3", x, TY, TW, TH, "night")
    cx = x + TW / 2
    ty = TY + 80                                           # the tower
    o += (f'<rect x="{n(x + 34)}" y="{n(ty)}" width="10" height="56" rx="2" fill="#CBD5E1" stroke="#475569"/><path d="M{n(x + 22)} {n(ty - 14)} H{n(x + 56)} L{n(x + 52)} {n(ty)} H{n(x + 26)} Z" fill="#FDE68A" stroke="#475569" stroke-width="1.2"/>'
          f'<rect x="{n(x + 20)}" y="{n(ty - 18)}" width="38" height="5" rx="2" fill="#475569"/>')
    cl = TY + 44                                           # the ceiling
    o += f'<line x1="{n(x + 8)}" y1="{n(cl)}" x2="{n(x + TW - 8)}" y2="{n(cl)}" stroke="#E2E8F0" stroke-width="2" stroke-dasharray="6 4"/>' + pill(x + TW - 54, cl - 14, "1 000 FT", AMBER, size=7.6)
    o += pill(x + TW - 50, TY + 104, "8 KM", BLUE)
    o += S.ribbon(f"{U}lp", [(cx - 6, TY + 140), (cx + 40, TY + 128), (cx + 50, TY + 152), (cx + 6, TY + 156)], 3.4, "#86EFAC", "#BBF7D0", opacity=0.9, head=2.0, tail=0.3, per=6)
    return o


def passengers():
    x = TX[2]
    o = R.tile(f"{U}t4", x, TY, TW, TH, "night")
    cx = x + TW / 2
    cal_x, cal_y = cx - 28, TY + 36                        # a calendar of 90 days
    o += (f'<rect x="{n(cal_x)}" y="{n(cal_y)}" width="56" height="52" rx="5" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.6"{ds()}/><rect x="{n(cal_x)}" y="{n(cal_y)}" width="56" height="13" rx="4" fill="{RED}"/>'
          + H.glyph_text("90", cx, cal_y + 33, 13, INK, spacing=0.4))
    o += pill(cx - 40, TY + 118, "3", GREEN, size=10) + pill(cx + 40, TY + 118, "3", RED, size=10)
    o += f'<path d="M{n(cx - 58)} {n(TY + 140)} q18 -4 26 -14" fill="none" stroke="#86EFAC" stroke-width="2.6" stroke-linecap="round"/><path d="M{n(cx + 32)} {n(TY + 126)} q8 10 26 14" fill="none" stroke="#FCA5A5" stroke-width="2.6" stroke-linecap="round"/>'
    for k in range(3):                                     # three passengers' heads
        hx = cx - 18 + k * 18
        o += f'<circle cx="{n(hx)}" cy="{n(TY + 146)}" r="6" fill="#E2E8F0"/><path d="M{n(hx - 9)} {n(TY + 162)} q9 -12 18 0 Z" fill="#E2E8F0"/>'
    return o


def callouts():
    c = S.callout
    return c(1, 28, 28, r=10) + c(2, TX[0] + 16, TY + 16, r=10) + c(3, TX[1] + 16, TY + 16, r=10) + c(4, TX[2] + 16, TY + 16, r=10)


def layers():
    return [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', timeline(), course(), exercise(), passengers(), callouts()]


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
