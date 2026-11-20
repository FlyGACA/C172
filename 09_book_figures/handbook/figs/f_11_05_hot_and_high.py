"""Figure 11-5 (new: the chapter's worked examples are invented aerodromes). Hot and high: the density altitude of twelve aerodromes of the Kingdom at their reference temperature.

Left, where the twelve lie: the land and its relief from open data (Natural Earth, public domain; figs/arabia_real.py) on the cone of the AIP's own charts, as in Figure 20-2, with
coasts and no boundary between countries. Each aerodrome is a dot at the reference point that AD 2.2 prints, with its location indicator.

Right, one bar for each, the highest first. The brown part is the elevation and the hot part what the heat adds; the bar ends at the density altitude, which is printed after it.
    elevation, reference temperature     AIP AD 2.2 of each aerodrome, item 3, AMDT 11/26 (data/saudi_airspace.json, "hot_and_high": typed from the official pages)
    density altitude                     worked out in data/build_saudi_facts.py, not printed in the AIP: the outside air temperature is the reference temperature, the QNH is
                                         1 013 hPa (so that the pressure altitude is the elevation), the air is dry, the atmosphere is the ICAO standard one; to the nearest 50 ft
The reference temperature of an aerodrome is the monthly mean of the daily maximum temperatures of its hottest month (ICAO Annex 14): an ordinary afternoon of that month, not a record.
Humidity and a QNH below 1 013 hPa, both usual in summer, raise the density altitude further; they are not in the bars.

Letters: location indicators, numbers with their units (ft, °C, NM), degrees of latitude and longitude; the rest is numbered."""
import math

from figs import arabia_real as AR
from figs import h_b2 as H
from figs import h_b4 as B
from figs import scene as S

n = S.n
W, HT = 640, 434
U = "hh4"
CONE = AR.Cone(AR.CONE.lat1, AR.CONE.lat2, 43.0, 24.0)             # the cone of the AIP's charts (the same two standard parallels as Figure 20-2), turned so that the meridian of 43 E is upright
ROWS = AR.FACTS["hot_and_high"]["aerodromes"]               # the twelve, the highest density altitude first
BY = {r["icao"]: r for r in ROWS}
assert len(ROWS) == 12 and [r["icao"] for r in ROWS][0] == "OEAB" and [r["icao"] for r in ROWS][-2:] == ["OEDF", "OEJN"]
assert BY["OEAB"]["density_altitude_rounded_ft_derived"] == 10350 and BY["OEDF"]["density_altitude_rounded_ft_derived"] == 3450 and BY["OEJN"]["density_altitude_rounded_ft_derived"] == 2650       # the legend's figures
assert (BY["OETH"]["elev_ft"], BY["OETH"]["ref_temp_c"], BY["OETH"]["density_altitude_rounded_ft_derived"]) == (1870, 42.0, 5300)
INK = H.INK
EARTH, EARTH_HI, EARTH_INK = "#9A6B3F", "#B98A5C", "#6B4A2A"          # the elevation
HOT_A, HOT_B = "#F0B429", "#C2410C"                                    # what the heat adds: amber to red

# ----------------------------------------------------------------------------------------------------- the map (left)
WEST, EAST, SOUTH, NORTH = 34.3, 51.7, 15.8, 31.0
MAP = (10.0, 30.0, 398.0, 392.0)                    # the box the piece of the chart is fitted into


def _fan(step=0.25):
    def par(lat, a, b):
        k = int(round(abs(b - a) / step))
        return [(lat, a + (b - a) * i / k) for i in range(k + 1)]
    return par(SOUTH, WEST, EAST) + par(NORTH, EAST, WEST)


_xy = [tuple(float(v) for v in CONE.xy(lat, lon)) for lat, lon in _fan()]
_x0, _x1, _y0, _y1 = min(p[0] for p in _xy), max(p[0] for p in _xy), min(p[1] for p in _xy), max(p[1] for p in _xy)
SCALE = min((MAP[2] - MAP[0]) / (_x1 - _x0), (MAP[3] - MAP[1]) / (_y1 - _y0))             # canvas units to the metre
OX = (MAP[0] + MAP[2]) / 2 - (_x0 + _x1) / 2 * SCALE
OY = (MAP[1] + MAP[3]) / 2 + (_y0 + _y1) / 2 * SCALE
AR.ensure_chart("terrain-11-04-arabia", CONE, (W, HT), SCALE, (OX, OY), WEST, EAST, SOUTH, NORTH, strength=1.25)


def P(lat, lon):
    """The canvas point of a place on the chart."""
    x, y = CONE.xy(lat, lon)
    return (OX + float(x) * SCALE, OY - float(y) * SCALE)


FAN = [P(lat, lon) for lat, lon in _fan()]
PIN = {r["icao"]: P(r["lat"], r["lon"]) for r in ROWS}
# where the indicator of each stands against its dot: (dx, dy, anchor)
TAG = {"OETB": (6.0, 0.5, "start"), "OEHL": (6.0, 0.5, "start"), "OEMA": (-6.0, 0.5, "end"), "OEJN": (-6.0, 1.0, "end"), "OETF": (6.0, -1.5, "start"), "OEBA": (6.0, 0.5, "start"),
       "OEAB": (6.0, -2.5, "start"), "OENG": (6.0, 1.0, "start"), "OERK": (6.0, 4.5, "start"), "OETH": (-6.0, -3.5, "end"), "OEAH": (6.0, 3.0, "start"), "OEDF": (6.0, -1.0, "start")}


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F7F1E4"), (1, "#EFE4CD")])}'
            f'<filter id="{U}sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4.2"/></filter>'
            f'<linearGradient id="{U}hot" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{HOT_A}"/><stop offset="1" stop-color="{HOT_B}"/></linearGradient>'
            f'<linearGradient id="{U}earth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{EARTH_HI}"/><stop offset="1" stop-color="{EARTH}"/></linearGradient>'
            f'<linearGradient id="{U}gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.34"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>')


def chart_shadow():
    line = S.pts([(x + 2.0, y + 4.0) for x, y in FAN])
    return f'<polygon points="{line}" fill="#3B2A12" opacity="0.38" filter="url(#{U}sh)"/><polygon points="{S.pts(FAN)}" fill="#EFE1BE"/>'


def tag(x, y, s, size=6.4, colour="#35507A", anchor="middle"):
    return (f'<text x="{n(x)}" y="{n(y)}" font-family="sans-serif" font-size="{n(size)}" font-weight="bold" fill="{colour}" text-anchor="{anchor}" '
            f'stroke="#FFFFFF" stroke-width="2.2" stroke-opacity="0.85" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def graticule():
    out = [f'<g fill="none" stroke="#35507A" stroke-opacity="0.38" stroke-width="0.5">']
    for lon in (35, 40, 45, 50):
        a, b = P(SOUTH, lon), P(NORTH, lon)
        out.append(f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}"/>')
    for lat in (20, 25, 30):
        k = 70
        out.append(f'<polyline points="{S.pts([P(lat, WEST + (EAST - WEST) * i / k) for i in range(k + 1)])}"/>')
    out.append("</g>")
    for lon in (35, 40, 45, 50):
        x, y = P(SOUTH + 0.5, lon)
        out.append(tag(x + 1.6, y, f"{lon}°E", anchor="start"))
    for lat in (20, 25, 30):
        x, y = P(lat, WEST + 0.35)
        out.append(tag(x, y - 2.4, f"{lat}°N", anchor="start"))
    return "".join(out)


def chart_edge():
    return f'<polygon points="{S.pts(FAN)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.95" stroke-width="1.3" stroke-linejoin="round"/>'


def pins():
    out = []
    for r in ROWS:
        x, y = PIN[r["icao"]]
        out.append(f'<circle cx="{n(x)}" cy="{n(y + 0.9)}" r="4.0" fill="#2B2418" opacity="0.3"/><circle cx="{n(x)}" cy="{n(y)}" r="3.5" fill="#FFFFFF"/><circle cx="{n(x)}" cy="{n(y)}" r="2.3" fill="{HOT_B}"/>')
    for r in ROWS:
        x, y = PIN[r["icao"]]
        dx, dy, anchor = TAG[r["icao"]]
        out.append(H.label(r["icao"], x + dx, y + dy, 4.9, INK, anchor=anchor, spacing=0.3, halo=2.6))
    return "".join(out)


# ----------------------------------------------------------------------------------------------------- the bars (right)
CX, CY, CW, CH = 408.0, 22.0, 224.0, 390.0           # the card
ROW0, PITCH, BAR_H = CY + 52.0, 26.4, 13.0           # the middle of the first bar, from one bar to the next, the thickness of a bar
X0 = CX + 61.0                                       # sea level
FT = 0.0121                                          # canvas units to the foot
TICKS = (0, 2000, 4000, 6000, 8000, 10000)


def row_y(i):
    return ROW0 + PITCH * i


def num(v):
    return f"{int(v):,}".replace(",", " ")


def bar_end(r):
    return X0 + r["density_altitude_ft_derived"] * FT


def card():
    y0, y1 = row_y(0) - PITCH / 2 + 1.5, row_y(11) + PITCH / 2 - 1.5
    out = [f'<rect x="{n(CX + 1.5)}" y="{n(CY + 3.0)}" width="{n(CW)}" height="{n(CH)}" rx="10" fill="#3B2A12" opacity="0.3" filter="url(#{U}sh)"/>',
           f'<rect x="{n(CX)}" y="{n(CY)}" width="{n(CW)}" height="{n(CH)}" rx="10" fill="#FFFDF8" stroke="#FFFFFF" stroke-width="1.2"/>']
    for i in range(12):                                                                    # a faint band under every other row
        if i % 2 == 0:
            out.append(f'<rect x="{n(CX + 4)}" y="{n(row_y(i) - PITCH / 2)}" width="{n(CW - 8)}" height="{n(PITCH)}" rx="3" fill="#F3EADB" opacity="0.7"/>')
    for t in TICKS:
        x = X0 + t * FT
        out.append(f'<line x1="{n(x)}" y1="{n(y0)}" x2="{n(x)}" y2="{n(y1 + 4.0)}" stroke="#8A7B66" stroke-opacity="{0.75 if t == 0 else 0.3}" stroke-width="{0.9 if t == 0 else 0.6}"/>')
    for t, s in ((0, "0"), (5000, "5 000"), (10000, "10 000 ft")):
        x = X0 + t * FT
        if t == 5000:
            out.append(f'<line x1="{n(x)}" y1="{n(y1)}" x2="{n(x)}" y2="{n(y1 + 4.0)}" stroke="#8A7B66" stroke-opacity="0.6" stroke-width="0.6"/>')
        out.append(B.label(x - (0 if t < 10000 else 9.0), y1 + 13.0, s, 7.0, "middle", colour="#5E5345", halo=False))
    out.append(B.label(CX + 55.0, row_y(0) - PITCH / 2 - 3.5, "ft", 7.0, "end", colour=EARTH_INK, halo=False))
    return "".join(out)


def bars():
    out = []
    for i, r in enumerate(ROWS):
        y = row_y(i)
        xe, xd = X0 + max(r["elev_ft"] * FT, 0.9), bar_end(r)
        top = y - BAR_H / 2
        out.append(H.glyph_text(r["icao"], CX + 8.0, y, 5.0, INK, anchor="start", spacing=0.3))
        out.append(B.label(CX + 55.0, y + 2.6, num(r["elev_ft"]), 7.4, "end", colour=EARTH_INK, halo=False))
        clip = f'{U}b{i}'
        out.append(f'<defs><clipPath id="{clip}"><rect x="{n(X0)}" y="{n(top)}" width="{n(xd - X0)}" height="{n(BAR_H)}" rx="2.6"/></clipPath></defs>'
                   f'<rect x="{n(X0 + 0.6)}" y="{n(top + 1.6)}" width="{n(xd - X0)}" height="{n(BAR_H)}" rx="2.6" fill="#3B2A12" opacity="0.22"/>'
                   f'<g clip-path="url(#{clip})"><rect x="{n(X0)}" y="{n(top)}" width="{n(xe - X0)}" height="{n(BAR_H)}" fill="url(#{U}earth)"/>'
                   f'<rect x="{n(xe)}" y="{n(top)}" width="{n(xd - xe)}" height="{n(BAR_H)}" fill="url(#{U}hot)"/>'
                   f'<rect x="{n(X0)}" y="{n(top)}" width="{n(xd - X0)}" height="{n(BAR_H)}" fill="url(#{U}gloss)"/>'
                   f'<line x1="{n(xe)}" y1="{n(top)}" x2="{n(xe)}" y2="{n(top + BAR_H)}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="0.7"/></g>')
        out.append(B.label((xe + xd) / 2, y + 2.4, f'{r["ref_temp_c"]:g} °C', 6.6, "middle", colour="#FFFFFF", halo=False))
        out.append(B.label(xd + 4.0, y + 2.9, num(r["density_altitude_rounded_ft_derived"]), 8.4, "start", colour=INK, halo=False))
    return "".join(out)


def rim(centre, toward, r):
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


def leader(a, b):
    return (f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#FFFFFF" stroke-width="2.6" stroke-opacity="0.85" stroke-linecap="round"/>'
            f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#263244" stroke-width="1.1" stroke-linecap="round"/><circle cx="{n(b[0])}" cy="{n(b[1])}" r="1.8" fill="#263244" stroke="#FFFFFF" stroke-width="0.9"/>')


def callouts():
    c = S.callout
    out = []
    a = PIN["OEHL"]
    out.append(c(1, a[0] - 24.0, a[1] - 20.0, *rim(a, (a[0] - 24.0, a[1] - 20.0), 3.6), r=10))
    top = BY["OEAB"]
    y, xe, xd = row_y(0), X0 + top["elev_ft"] * FT, bar_end(top)
    up = y - BAR_H / 2
    out.append(c(2, X0 + 40.0, up - 17.0, X0 + 40.0, up + 1.0, r=8.6))                                   # the elevation
    out.append(c(3, (xe + xd) / 2, up - 17.0, (xe + xd) / 2, up + 1.0, r=8.6))                           # what the heat adds
    out.append(c(4, xd + 17.0, up - 17.0, xd + 17.0, up - 1.5, r=8.6))                                   # the density altitude
    a = PIN["OEAB"]
    out.append(c(5, a[0] - 30.0, a[1] + 19.0, *rim(a, (a[0] - 30.0, a[1] + 19.0), 3.6), r=10))
    y10, y11 = row_y(10), row_y(11)
    at = (bar_end(BY["OEDF"]) + 66.0, (y10 + y11) / 2)
    out.append(leader(at, (bar_end(BY["OEJN"]) + 30.0, y11)) + c(6, at[0], at[1], bar_end(BY["OEDF"]) + 30.0, y10, r=8.6))
    i = [r["icao"] for r in ROWS].index("OETH")
    out.append(c(7, bar_end(BY["OETH"]) + 52.0, row_y(i), bar_end(BY["OETH"]) + 31.0, row_y(i), r=8.6))
    return "".join(out)


def layers():
    return [background(), chart_shadow(), AR.sprite_box("terrain-11-04-arabia"), graticule(), chart_edge(), pins(), card(), bars(),
            H.defs(U, W, HT), H.scale_bar(U, 16.0, 410.0, 200 * AR.NM * SCALE, nm_total=200, segments=2, text="200 NM"), callouts()]


def plate():
    return {
        "id": "fig-11-05-hot-and-high",
        "replaces": "fig-11-05-hot-and-high.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-11-05-hot-and-high.jpg",
        "caption": "Figure 11-5. Hot and high: the density altitude of twelve aerodromes of the Kingdom at their reference temperature",
        "desc": ("Figure 11-5. Hot and high: the density altitude of twelve aerodromes of the Kingdom at their reference temperature. The elevations and the reference temperatures are the AIP's "
                 "(AD 2.2, AMDT 11/26); the density altitudes are worked out from them for dry air and a QNH of 1 013 hPa, to the nearest 50 ft. The map is on the projection of the AIP's charts, "
                 "from open data (Natural Earth), with coasts and no boundaries; not for navigation."),
        "legend": [
            "Each aerodrome at its reference point, with its location indicator; the shading is the relief of the land.",
            "The elevation of the aerodrome.",
            "What the heat adds, at the aerodrome's reference temperature.",
            "The density altitude at that temperature, to the nearest 50 ft.",
            "Abha, the highest of the twelve: above 10 000 ft.",
            "Dammam and Jeddah, at sea level: about 3 450 ft and 2 650 ft.",
            "Thumamah, the example of Chapters 17 and 18: 1 870 ft and 42 °C give about 5 300 ft.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
