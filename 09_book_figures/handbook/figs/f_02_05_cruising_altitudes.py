"""Figure 2-5. VFR cruising altitudes on a real route: the ground under the line from Riyadh King Khaled (OERK) to Jeddah King Abdulaziz (OEJN), 460.5 NM on a great circle whose true
course is 246 degrees at Riyadh and 243 degrees at Jeddah, against the levels that the hemispheric rule of GACAR 91.169 allows.

What is drawn comes from open elevation data (NASA SRTM, public domain; data/open/fetch_route_terrain.py -> data/open/oerk_oejn_profile.json: the ground on the line and the highest ground within
10 NM of it, every nautical mile) and from the rule: x is the distance from Riyadh in NM, 0 to 460.5; y is the height above mean sea level in feet, linear, 0 to 13 500 (the vertical scale is
exaggerated about 140 times: 573 canvas units to 460.5 NM and 322 units to 13 500 ft). The route flown west is a magnetic course of 243 degrees at Riyadh (true 246 degrees, variation 3 degrees E, AD 2
OERK) and 239 degrees at Jeddah (true 243 degrees, variation 4 degrees E, AD 2 OEJN), so the levels are the even thousands plus 500 ft (4 500, 6 500, 8 500, 10 500, 12 500: orange); the route
flown east is 059 to 063 degrees magnetic, so the odd thousands plus 500 ft (3 500, 5 500, 7 500, 9 500, 11 500: blue). Where a level lies less than 500 ft above the ground under the line
(GACAR 91.67: 500 ft above the surface elsewhere) the level is drawn with a thick red stroke; where it clears the line but not the highest ground within 10 NM by 500 ft, a thick amber one.
The line of 3 000 ft above the ground (GACAR 91.169(a) counts the rule from there) and the horizontal line of 3 000 ft AMSL (the AIP counts it from there, ENR 1.1) are drawn dashed. Above 12 500 ft (the
maximum VFR cruising altitude, 91.169(b)) the picture is hatched. The ground under the line is FlyGACA's reading of a radar survey, not an AIP value. Digits, the ICAO codes and the units only."""
import json
import os

from figs import h_a1 as A1
from figs import h_b1 as B
from figs import scene as S

W, HT = 640, 390
U = "b201"
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(os.path.dirname(HERE), "data", "open", "oerk_oejn_profile.json"), encoding="utf-8") as _f:
    PROFILE = json.load(_f)
ROWS = PROFILE["profile"]                                   # [nm, ground on the line, highest ground within 10 NM], feet
TOTAL = PROFILE["great_circle_nm"]
ELEV_FROM, ELEV_TO = 2053, 50                              # AD 2.2 of OERK and OEJN (data/saudi_airspace.json)

BOX = (62.0, 8.0, 573.0, 322.0)
FT0, FT1 = 0.0, 13500.0
PL = B.Plot(BOX, (0.0, TOTAL), (FT0, FT1))
X, Y = PL.X, PL.Y
RIGHT = BOX[0] + BOX[2]
BOTTOM = BOX[1] + BOX[3]
WEST_C, EAST_C = "#C2410C", "#1D4ED8"
RED, AMBER = "#D32F2F", "#F59E0B"
WEST = [4500, 6500, 8500, 10500, 12500]                     # even thousands + 500: magnetic courses 180 to 359 (here 239 to 243)
EAST = [3500, 5500, 7500, 9500, 11500]                      # odd thousands + 500: courses 0 to 179 (here 059 to 063)
MIN_AGL = 500                                               # GACAR 91.67
MAX_VFR = 12500                                             # GACAR 91.169(b)

# the numbers the legend gives
LINE_MAX = max(ROWS, key=lambda r: r[1])                    # the crest of the Hijaz on the line
BAND_MAX = max(ROWS, key=lambda r: r[2])
assert (round(LINE_MAX[0]), LINE_MAX[1]) == (391, 4416) and BAND_MAX[2] == 5054, (LINE_MAX, BAND_MAX)
assert round(TOTAL, 1) == 460.5


def ground(nm):
    i = min(max(nm, 0.0), len(ROWS) - 1.001)
    k = int(i)
    return ROWS[k][1] + (ROWS[k + 1][1] - ROWS[k][1]) * (i - k)


def segments(level):
    """The distances (NM) at which a level is under 500 ft above the line (red) and, where it is not, under 500 ft above the highest ground within 10 NM (amber): runs of consecutive rows."""
    out = {"red": [], "amber": []}
    for nm, g, h in ROWS:
        kind = "red" if level < g + MIN_AGL else "amber" if level < h + MIN_AGL else None
        if kind is None:
            continue
        runs = out[kind]
        if runs and nm - runs[-1][1] <= 1.01:
            runs[-1][1] = nm
        else:
            runs.append([nm, nm])
    return out


SEG = {lv: segments(lv) for lv in WEST + EAST}
assert not SEG[6500]["red"] and not SEG[6500]["amber"] and not SEG[7500]["red"] and not SEG[7500]["amber"]
assert SEG[4500]["red"] == [[388.0, 396.0]]
assert SEG[3500]["red"][-1] == [293.0, 403.0]
assert not SEG[5500]["red"] and SEG[5500]["amber"] == [[403.0, 403.0]]
RED3500 = sum(b - a + 1 for a, b in SEG[3500]["red"])
assert 280 <= RED3500 <= 300, RED3500


def line_points():
    return [(nm, g) for nm, g, _ in ROWS]


def band_points():
    return [(nm, h) for nm, _, h in ROWS]


# ------------------------------------------------------------------------------------------------------------------ the picture
def page_and_card():
    out = [A1.page(U + "pg", W, HT)]
    body = S.glow(U + "sg", BOX[0] + 90, BOX[1] + 50, 230, "#FFFFFF", 0.4)
    out.append(S.card(U + "cd", BOX[0], BOX[1], BOX[2], BOX[3], B.SKY, body, radius=10))
    return out


def over_cap():
    """Above 12 500 ft: hatched, and a bold line along 12 500."""
    top = [(0.0, FT1), (TOTAL, FT1), (TOTAL, MAX_VFR), (0.0, MAX_VFR)]
    return B.hatch(U + "hx", PL.pts(top), "#B91C1C", 45, 3.2, 0.8, 0.5) + S.altitude_line(BOX[0], RIGHT, Y(MAX_VFR), colour="#B91C1C", opacity=0.95, dash="6 3", width=1.5)


def level_lines():
    out = []
    for lv, col in [(v, WEST_C) for v in WEST] + [(v, EAST_C) for v in EAST]:
        out.append(f'<line x1="{S.n(BOX[0])}" y1="{S.n(Y(lv))}" x2="{S.n(RIGHT)}" y2="{S.n(Y(lv))}" stroke="{col}" stroke-opacity="0.62" stroke-width="0.9"/>')
    return "".join(out)


def reference_lines():
    """3 000 ft above the ground (follows the ground) and 3 000 ft AMSL (level)."""
    agl = PL.pts([(nm, g + 3000) for nm, g, _ in ROWS])
    out = [f'<path d="{B.dpath(agl)}" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-opacity="0.85" stroke-linejoin="round"/>',
           f'<path d="{B.dpath(agl)}" fill="none" stroke="#6D28D9" stroke-width="1.1" stroke-dasharray="5 3" stroke-linejoin="round"/>',
           S.altitude_line(BOX[0], RIGHT, Y(3000), colour="#0F766E", opacity=1.0, dash="2 3", width=1.6)]
    return "".join(out)


def ground_layer():
    top = PL.pts(line_points())
    band = PL.pts(band_points())
    out = [B.soil(U + "so", top, BOTTOM, seed=201, strata=(0.5, 0.74, 0.9), grit=22, haze=(4.0, 0.6))]
    # the highest ground within 10 NM of the line, above the ground on it
    poly = band + list(reversed(top))
    out.append(f'<polygon points="{B.pts(poly)}" fill="#8B5E2B" fill-opacity="0.34"/>')
    out.append(f'<path d="{B.dpath(band)}" fill="none" stroke="#6B4423" stroke-opacity="0.85" stroke-width="0.9" stroke-dasharray="2.2 1.8" stroke-linejoin="round"/>')
    out.append(f'<path d="{B.dpath(top)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.1" stroke-linejoin="round"/>')
    return "".join(out)


def flagged():
    """The stretches of a level under 500 ft above the ground: red under the line itself, amber under the highest ground within 10 NM."""
    out = []
    for lv in WEST + EAST:
        for kind, col in (("amber", AMBER), ("red", RED)):
            for a, b in SEG[lv][kind]:
                a, b = max(a - 0.5, 0.0), min(b + 0.5, TOTAL)
                out.append(f'<line x1="{S.n(X(a))}" y1="{S.n(Y(lv))}" x2="{S.n(X(b))}" y2="{S.n(Y(lv))}" stroke="{col}" stroke-width="3.6" stroke-linecap="round"/>')
    return "".join(out)


def aerodromes():
    out = []
    out.append(B.runway_bar(X(0.0), X(2.4), Y(ELEV_FROM), h=3.0))
    out.append(B.runway_bar(X(TOTAL - 2.4), X(TOTAL), Y(ELEV_TO), h=3.0))
    return "".join(out)


def labels():
    """The levels in digits: the westbound ones (orange) at the right edge, the eastbound ones (blue) at the left edge."""
    out = []
    t = B.tag
    for lv in WEST:
        out.append(t(RIGHT - 3, Y(lv) - 2.6, f"{lv // 1000} {lv % 1000:03d}", WEST_C, 8.4, "end", halo=2.6))
    for lv in EAST:
        out.append(t(BOX[0] + 4, Y(lv) - 2.6, f"{lv // 1000} {lv % 1000:03d}", EAST_C, 8.4, "start", halo=2.6))
    out.append(t(X(300), Y(3000) + 11.0, "3 000 AMSL", "#0F766E", 8.0, "start", halo=2.6))
    out.append(t(X(60), Y(ground(60) + 3000) - 5.0, "3 000 AGL", "#6D28D9", 8.0, "start", halo=2.6))
    return "".join(out)


def axes():
    out = []
    x0 = BOX[0]
    for ft in range(0, 13001, 2000):
        y = Y(ft)
        out.append(B.plain_text(x0 - 7, y + 3.7, f"{ft // 1000} {ft % 1000:03d}" if ft >= 1000 else "0"))
        out.append(f'<line x1="{S.n(x0 - 4.5)}" y1="{S.n(y)}" x2="{S.n(x0)}" y2="{S.n(y)}" stroke="#4B5870" stroke-width="1"/>')
    out.append(B.plain_text(x0 - 7, BOX[1] + 10.0, "ft", "#4B5870", 9.5))
    yb = BOTTOM
    for v in (0, 100, 200, 300, 400):
        x = X(v)
        out.append(f'<line x1="{S.n(x)}" y1="{S.n(yb)}" x2="{S.n(x)}" y2="{S.n(yb + 4.5)}" stroke="#4B5870" stroke-width="1"/>')
        out.append(B.plain_text(x, yb + 15.5, str(v), anchor="middle"))
    x = X(TOTAL)
    out.append(f'<line x1="{S.n(x)}" y1="{S.n(yb)}" x2="{S.n(x)}" y2="{S.n(yb + 4.5)}" stroke="#4B5870" stroke-width="1"/>')
    out.append(B.plain_text(RIGHT + 3, yb + 15.5, "460.5", anchor="end"))
    out.append(B.plain_text(x0 - 7, yb + 15.5, "NM", "#4B5870", 9.5))
    out.append(B.plain_text(X(0.0) + 4, yb + 29.0, "OERK", B.INK, 9.5, "start", "bold"))
    out.append(B.plain_text(X(TOTAL), yb + 29.0, "OEJN", B.INK, 9.5, "end", "bold"))
    out.append(B.plain_text(X(0.0) + 4, yb + 41.0, "2 053", "#4B5870", 8.6, "start"))
    out.append(B.plain_text(X(TOTAL), yb + 41.0, "50", "#4B5870", 8.6, "end"))
    return "".join(out)


def aeroplanes():
    look = {"outline": {"width": 0.6, "colour": "#1B2638", "opacity": 0.95}, "shadow": {"dx": 0.8, "dy": 1.8, "blur": 1.3, "opacity": 0.28}}
    return [{"name": "sprite-side", "at": [X(120.0), Y(6500) - 3.0], "width": 34, **look},
            {"name": "sprite-side", "at": [X(250.0), Y(7500) - 3.0], "width": 34, "flip": True, **look}]


def arrows():
    """A small arrow on each flown level, the way it goes: west (to Jeddah) at 6 500, east (to Riyadh) at 7 500."""
    out = []
    for x0, lv, d, col in ((X(150.0), 6500, 1, WEST_C), (X(220.0), 7500, -1, EAST_C)):
        y = Y(lv)
        out.append(f'<path d="M{S.n(x0)} {S.n(y)} l{S.n(26 * d)} 0" stroke="{col}" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M{S.n(x0 + 26 * d)} {S.n(y - 3.4)} l{S.n(5.2 * d)} 3.4 l{S.n(-5.2 * d)} 3.4 z" fill="{col}"/>')
    return "".join(out)


def callouts():
    c = S.callout
    r = 9.5
    out = []
    out.append(c(1, X(50), Y(8050), X(50), Y(6500) - 1.5, r=r))                                                # westbound level
    out.append(c(2, X(285), Y(8850), X(285), Y(7500) - 1.5, r=r))                                             # eastbound level
    out.append(c(3, X(391) - 36, Y(2300), X(391), Y(LINE_MAX[1]) + 2.0, r=r))                                  # the crest on the line
    out.append(c(4, X(392) - 22, Y(4500) - 22, X(392), Y(4500) - 2.0, r=r))                                    # 4 500 westbound under the crest
    out.append(c(5, X(340), Y(5500) + 24, X(403), Y(5500), r=r))                                               # 5 500 eastbound over the crest
    out.append(c(6, X(250), Y(1350), X(250), Y(3000) + 1.0, r=r))                                         # 3 000 AMSL
    out.append(c(7, X(250), Y(4950), X(250), Y(ground(250) + 3000) + 1.0, r=r))                                   # 3 000 AGL
    out.append(c(8, X(300), Y(13050), X(300), Y(MAX_VFR) - 1.0, r=r))                                 # 12 500
    return "".join(out)


def layers():
    inner = [ground_layer(), aerodromes()]
    air = [over_cap(), level_lines(), reference_lines()]
    return [*page_and_card(), S.card_front(U + "fr", BOX[0], BOX[1], BOX[2], BOX[3], "".join(air + inner), radius=10),
            S.card_front(U + "fl", BOX[0], BOX[1], BOX[2], BOX[3], flagged() + arrows() + labels(), radius=10), *aeroplanes(), axes(), callouts()]


def plate():
    return {
        "id": "fig-02-05-cruising-altitudes",
        "replaces": "fig-02-05-cruising-altitudes.svg",      # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-02-05-cruising-altitudes.jpg",
        "caption": "Figure 2-5. VFR cruising altitudes on a real route: Riyadh to Jeddah, 460 NM, against the ground under the line",
        "desc": ("Figure 2-5. VFR cruising altitudes on a real route: Riyadh to Jeddah, 460 NM, against the ground under the line. Height above mean sea level in feet against nautical miles from "
                 "Riyadh; vertical scale exaggerated; the ground is from open elevation data (NASA SRTM) under a great circle between the two aerodrome reference points; the levels are those of "
                 "GACAR 91.169 for a magnetic course of about 240 degrees and for the opposite course. Not a route to fly and not for navigation."),
        "legend": [
            "Flying west, from Riyadh to Jeddah: the magnetic course is about 240° (243° at Riyadh, 239° at Jeddah), so the VFR levels are the even thousands plus 500 ft, 4 500, 6 500, 8 500, 10 500 and 12 500 ft. Orange.",
            "Flying east, from Jeddah to Riyadh: the course is about 060°, so the levels are the odd thousands plus 500 ft, 3 500, 5 500, 7 500, 9 500 and 11 500 ft. Blue.",
            "The ground under the line (white edge) and the highest ground within 10 NM of it (dashed). It stands between 3 000 and 3 500 ft for much of the route and climbs to the crest of the Hijaz mountains: 4 416 ft under the line, 391 NM from Riyadh, and 5 054 ft within 10 NM of it, 403 NM from Riyadh.",
            "4 500 ft westbound clears the crest under the line by only 84 ft, and is less than 500 ft above the ground along 9 NM of it (red). The first westbound level that clears all the ground by more than 500 ft is 6 500 ft.",
            "5 500 ft eastbound clears the ground under the line by more than 1 000 ft, but the highest ground within 10 NM of it by only 446 ft (amber). 3 500 ft eastbound is less than 500 ft above the ground along about 290 NM of the route (red).",
            "3 000 ft AMSL, where the AIP starts the rule (ENR 1.1). Every level in the figure is above it, so the AIP's rule applies to all of them.",
            "3 000 ft above the ground, where the GACAR starts the rule (§91.169(a)). Over a ground at 3 000 ft AMSL the rule starts at about 6 000 ft AMSL, and over the Hijaz at about 7 400 ft.",
            "12 500 ft MSL, the maximum VFR cruising altitude (§91.169(b)). Above it, hatched, there is no VFR level.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
