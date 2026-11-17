"""Figure 13-3 (new). The latest takeoff time from A, from the worked example of Chapter 13 ("Daylight and delays"): a time scale from 14:00 to 18:00 worked backwards from the sunset at B.

Sunset at B is 17:40 local (the chapter's illustrative value); the day ends there (the hatched night). Working back: 15 minutes in hand (green, a rule of thumb), 30 minutes for a diversion to C (amber), so the latest landing at B is 17:40 - 0:30 - 0:15 = 16:55; the flight
takes 2 h 04 min (blue), so the latest takeoff from A is 16:55 - 2:04 = 14:51. Every number is the chapter's. Digits and colons only: the words are in the legend."""
import math

from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 236
U = "lt13"
INK, SLATE, BLUE, GREEN, AMBER, RED = "#334155", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C"
X0, PPH = 44.0, 138.0                                        # x of 14:00, canvas units per hour
BAR_Y, BAR_H = 112.0, 34.0
TAKEOFF, LANDING, DIVERT_END, SUNSET = 14 * 60 + 51, 16 * 60 + 55, 17 * 60 + 25, 17 * 60 + 40


def xt(minutes):
    return X0 + (minutes - 14 * 60) / 60.0 * PPH


def hhmm(m):
    return f"{m // 60}:{m % 60:02d}"


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, size=6.0, height=12.0):
    w = gwidth(s, size) + 12.0
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - height / 2)}" width="{n(w)}" height="{n(height)}" rx="{n(height / 2)}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.2" filter="url(#{U}ds)"/>'
            + H.glyph_text(s, x, y, size, "#FFFFFF", spacing=0.35))


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<filter id="{U}ds" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.3" flood-color="#1B2638" flood-opacity="0.3"/></filter>'
            f'<pattern id="{U}nt" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="7" height="7" fill="#1E293B"/><line x1="0" y1="0" x2="0" y2="7" stroke="#475569" stroke-width="2"/></pattern></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def scale():
    out = []
    for h in range(14, 19):
        x = xt(h * 60)
        out.append(f'<line x1="{n(x)}" y1="{n(BAR_Y - 36)}" x2="{n(x)}" y2="{n(BAR_Y + 54)}" stroke="{SLATE}" stroke-opacity="0.16" stroke-width="1"/>')
        out.append(H.glyph_text(f"{h}:00", x, BAR_Y + 66.0, 5.2, SLATE, spacing=0.3))
    return "".join(out)


def night():
    x = xt(SUNSET)
    return f'<rect x="{n(x)}" y="{n(BAR_Y - 36)}" width="{n(xt(18 * 60) - x + 14)}" height="{n(90)}" fill="url(#{U}nt)" fill-opacity="0.92" rx="4"/>'


def bars():
    out = []
    for a, b, col in ((TAKEOFF, LANDING, BLUE), (LANDING, DIVERT_END, "#F59E0B"), (DIVERT_END, SUNSET, "#4ADE80")):
        out.append(f'<rect x="{n(xt(a))}" y="{n(BAR_Y - BAR_H / 2)}" width="{n(xt(b) - xt(a))}" height="{BAR_H}" rx="6" fill="{col}" stroke="#FFFFFF" stroke-width="1.6" filter="url(#{U}ds)"/>')
    out.append(pill("2:04", (xt(TAKEOFF) + xt(LANDING)) / 2, BAR_Y, SLATE, 6.6, 14.0))
    out.append(pill("0:30", (xt(LANDING) + xt(DIVERT_END)) / 2, BAR_Y, SLATE, 6.0, 13.0))
    out.append(pill("0:15", (xt(DIVERT_END) + xt(SUNSET)) / 2, BAR_Y - 26.0, SLATE, 5.6, 12.0))
    return "".join(out)


def marks():
    out = []
    # the times above the bars: takeoff, landing, sunset
    for m, col in ((TAKEOFF, BLUE), (LANDING, AMBER)):
        x = xt(m)
        out.append(f'<line x1="{n(x)}" y1="{n(BAR_Y - BAR_H / 2 - 4)}" x2="{n(x)}" y2="{n(BAR_Y - 40)}" stroke="{col}" stroke-width="2.4"/>')
        out.append(pill(hhmm(m), x, BAR_Y - 48.0, col, 6.4, 14.0))
    x = xt(SUNSET)
    out.append(f'<line x1="{n(x)}" y1="{n(BAR_Y - 40)}" x2="{n(x)}" y2="{n(BAR_Y + 54)}" stroke="{RED}" stroke-width="3" stroke-dasharray="7 4"/>')
    out.append(pill(hhmm(SUNSET), x, BAR_Y - 50.0, RED, 6.4, 14.0))
    # a sun going down on the horizon at the sunset
    out.append(f'<path d="M{n(x - 16)} {n(BAR_Y - 66)} a16 16 0 0 1 32 0 Z" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.4"/><line x1="{n(x - 22)}" y1="{n(BAR_Y - 66)}" x2="{n(x + 22)}" y2="{n(BAR_Y - 66)}" stroke="{SLATE}" stroke-width="2"/>')
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.5
    out = []
    out.append(c(1, xt(TAKEOFF) - 20.0, BAR_Y + 54.0, xt(TAKEOFF), BAR_Y + 12.0, r=r))                    # the latest takeoff
    out.append(c(2, (xt(TAKEOFF) + xt(LANDING)) / 2, BAR_Y + 54.0, (xt(TAKEOFF) + xt(LANDING)) / 2 + 40, BAR_Y + 12.0, r=r))   # the flight
    out.append(c(3, (xt(LANDING) + xt(DIVERT_END)) / 2, BAR_Y + 54.0, (xt(LANDING) + xt(DIVERT_END)) / 2, BAR_Y + 14.0, r=r))   # the diversion
    out.append(c(4, (xt(DIVERT_END) + xt(SUNSET)) / 2 - 16.0, BAR_Y - 70.0, (xt(DIVERT_END) + xt(SUNSET)) / 2, BAR_Y - 32.0, r=r))   # the margin
    out.append(c(5, xt(SUNSET) + 78.0, BAR_Y - 56.0, xt(SUNSET) + 40.0, BAR_Y - 12.0, r=r))               # the sunset, after it the night
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), background(), scale(), night(), bars(), marks(), callouts()]


def plate():
    return {
        "id": "fig-13-03-latest-takeoff",
        "replaces": "fig-13-03-latest-takeoff.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-13-03-latest-takeoff.jpg",
        "caption": "Figure 13-3. The latest takeoff time from A, worked back from the sunset at B (an illustrative sunset)",
        "desc": ("Figure 13-3. The latest takeoff time from A, worked back from a sunset at B of 17:40 (an illustrative value): 15 minutes in hand, 30 minutes for a diversion to C, "
                 "so the latest landing at B is 16:55; the flight takes 2 h 04 min, so the latest takeoff is 14:51."),
        "legend": [
            "The latest takeoff from A, 14:51: the latest landing at B minus the 2 h 04 min of the flight. If the departure slips past it, shorten the flight or go another day.",
            "The flight from A to B, estimated elapsed time 2 h 04 min.",
            "A diversion from B to C, 30 minutes away, which must also end before sunset: so the latest landing at B is 16:55.",
            "15 minutes in hand (a rule of thumb) between the end of the diversion and sunset.",
            "Sunset at B, 17:40 local (an illustrative value). VFR flight from sunset to sunrise is prohibited unless the President authorizes it or the flight is a local flight under conditions set by the ATC facility (section 91.171).",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
