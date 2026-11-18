"""Figure 16-1 (new). The family of weather products, from the first section of Chapter 16: each product on one time axis, with the observed past and the forecast future either side of now (a clock).

Lanes: 1 METAR and SPECI at now, at one aerodrome; 2 the trend, a short arrow after the METAR; 3 TAF, a bar over its validity period; 4 SIGMET and AIRMET, bars for a stated period over an area (a hazard polygon);
5 area forecasts and significant weather charts, and winds and temperatures aloft (a chart and a wind arrow), hours ahead; 6 ATIS and air reports, now (radio arcs and the aeroplane). The product names are the codes the chapter uses; the time axis has no scale."""
from figs import h_b2 as H
from figs import scene as S

n = S.n
W, HT = 640, 300
U = "wx1601"
INK, SLATE, BLUE, GREEN, AMBER, RED, TEAL, VIOLET = "#1E293B", "#475569", "#1D4ED8", "#15803D", "#B45309", "#B91C1C", "#0F766E", "#7C3AED"
X0, X1, NOW = 150.0, 620.0, 250.0
LY = (34.0, 74.0, 114.0, 156.0, 200.0, 242.0)
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


def bar(xa, xb, y, col, dash=False, h=14.0):
    if dash:
        return f'<rect x="{n(xa)}" y="{n(y - h / 2)}" width="{n(xb - xa)}" height="{n(h)}" rx="{n(h / 2)}" fill="#FFFFFF" stroke="{col}" stroke-width="2.4" stroke-dasharray="6 4"/>'
    return f'<rect x="{n(xa)}" y="{n(y - h / 2)}" width="{n(xb - xa)}" height="{n(h)}" rx="{n(h / 2)}" fill="{col}" fill-opacity="0.85"/>'


def frame():
    return (f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>'
            f'<rect x="{n(X0)}" y="12" width="{n(NOW - X0)}" height="252" rx="6" fill="#CBD5E1" fill-opacity="0.75"/>'
            f'<rect x="{n(NOW)}" y="12" width="{n(X1 - NOW)}" height="252" rx="6" fill="#DBEAFE" fill-opacity="0.8"/>'
            + "".join(f'<line x1="12" y1="{n(y + 20)}" x2="{n(X1)}" y2="{n(y + 20)}" stroke="#E2E8F0" stroke-width="1.2"/>' for y in LY[:-1])
            + f'<line x1="{n(NOW)}" y1="12" x2="{n(NOW)}" y2="270" stroke="{INK}" stroke-width="2.4" stroke-dasharray="5 4"/>'
            + f'<line x1="{n(X0)}" y1="276" x2="{n(X1)}" y2="276" stroke="#94A3B8" stroke-width="3" stroke-linecap="round"/><path d="M{n(X1 + 6)} 276 L{n(X1 - 4)} 270 L{n(X1 - 4)} 282 Z" fill="#94A3B8"/>'
            + f'<circle cx="{n(NOW)}" cy="282" r="11" fill="#FFFFFF" stroke="{INK}" stroke-width="2.4"/><line x1="{n(NOW)}" y1="282" x2="{n(NOW)}" y2="274" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/><line x1="{n(NOW)}" y1="282" x2="{n(NOW + 6)}" y2="284" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')


def aerodrome(cx, cy, col):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="10" fill="#FFFFFF" stroke="{col}" stroke-width="2.4"/><line x1="{n(cx - 6)}" y1="{n(cy + 4)}" x2="{n(cx + 6)}" y2="{n(cy - 4)}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>'


def lanes():
    o = ""
    y = LY[0]                                            # METAR and SPECI
    o += aerodrome(70, y + 4, GREEN) + f'<circle cx="{n(NOW)}" cy="{n(y + 4)}" r="7" fill="{GREEN}" stroke="#FFFFFF" stroke-width="2"/><circle cx="{n(NOW - 46)}" cy="{n(y + 4)}" r="5" fill="{GREEN}" fill-opacity="0.55"/><circle cx="{n(NOW - 92)}" cy="{n(y + 4)}" r="5" fill="{GREEN}" fill-opacity="0.55"/>'
    o += pill(NOW + 40, y + 4, "METAR", GREEN) + pill(NOW + 104, y + 4, "SPECI", GREEN)
    y = LY[1]                                            # trend
    o += aerodrome(70, y + 4, GREEN) + f'<circle cx="{n(NOW)}" cy="{n(y + 4)}" r="7" fill="{GREEN}" stroke="#FFFFFF" stroke-width="2"/>'
    o += S.ribbon(f"{U}tr", [(NOW + 10, y + 4), (NOW + 60, y + 4), (NOW + 96, y + 4)], 4.6, TEAL, "#5EC4B8", opacity=0.92, head=2.2, tail=0.4, per=6)
    y = LY[2]                                            # TAF
    o += aerodrome(70, y + 4, BLUE) + bar(NOW - 12, X1 - 30, y + 4, BLUE) + pill(NOW + 150, y + 4, "TAF", BLUE)
    y = LY[3]                                            # SIGMET and AIRMET over an area
    o += (f'<path d="M54 {n(y - 6)} L82 {n(y - 12)} L94 {n(y + 6)} L74 {n(y + 18)} L50 {n(y + 12)} Z" fill="{RED}" fill-opacity="0.25" stroke="{RED}" stroke-width="2" stroke-linejoin="round"/>'
          + bar(NOW - 30, NOW + 160, y - 4, RED, h=12) + pill(NOW + 64, y - 4, "SIGMET", RED, size=7.8)
          + bar(NOW + 10, NOW + 230, y + 13, AMBER, dash=True, h=12) + pill(NOW + 150, y + 13, "AIRMET", AMBER, size=7.8))
    y = LY[4]                                            # area forecasts, significant weather charts, winds aloft
    o += (f'<rect x="50" y="{n(y - 12)}" width="44" height="32" rx="3" fill="#FFFFFF" stroke="{VIOLET}" stroke-width="2"/>'
          f'<path d="M54 {n(y + 12)} q8 -16 16 -6 t18 -10" fill="none" stroke="{BLUE}" stroke-width="2.2"/><path d="M57 {n(y + 6)} l3 -5 l3 5 Z M69 {n(y + 4)} l3 -5 l3 5 Z" fill="{BLUE}"/>'
          f'<path d="M104 {n(y + 4)} h22 m0 0 l-6 -5 m6 5 l-6 5" fill="none" stroke="{VIOLET}" stroke-width="2.4" stroke-linecap="round"/>'
          + bar(NOW + 20, X1 - 10, y + 4, VIOLET, dash=True))
    y = LY[5]                                            # ATIS and air reports, now
    o += "".join(f'<path d="M{n(64 + k * 9)} {n(y - 4 - k * 3)} a{n(8 + k * 5)} {n(8 + k * 5)} 0 0 1 0 {n(16 + k * 6)}" fill="none" stroke="{SLATE}" stroke-width="2.4" stroke-linecap="round"/>' for k in range(3))
    o += f'<circle cx="{n(NOW)}" cy="{n(y + 4)}" r="7" fill="{SLATE}" stroke="#FFFFFF" stroke-width="2"/>' + pill(NOW + 40, y + 4, "ATIS", SLATE)
    return o


def sprites():
    return [{"name": "sprite-side", "at": [NOW + 120, LY[5] + 2], "width": 44, "outline": OUT, "shadow": SHADOW}]


def callouts():
    return "".join(S.callout(i + 1, 24, LY[i] + 4, r=10.0) for i in range(6))


def layers():
    return [H.defs(U, W, HT), frame(), lanes(), *sprites(), callouts()]


def plate():
    return {
        "id": "fig-16-01-weather-products",
        "replaces": "fig-16-01-weather-products.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-16-01-weather-products.jpg",
        "caption": "Figure 16-1. The family of weather products on one time axis: what has been observed, and what is expected",
        "desc": ("Figure 16-1. The family of weather products on one time axis, the observed past on the left of now and the forecast future on the right: METAR and SPECI at one aerodrome at the moment of observation; "
                 "the trend a short period after; the TAF over its validity period; SIGMET and AIRMET over an area for a stated period; area forecasts, significant weather charts and winds aloft hours ahead; ATIS and air reports now."),
        "legend": [
            "METAR and SPECI: observations at one aerodrome, at the moment of observation; a SPECI when the weather changes between routine reports.",
            "Trend, at the end of a METAR: the expected change at that aerodrome for a short period after the observation.",
            "TAF: the forecast for one aerodrome over the validity period printed in it.",
            "SIGMET, and AIRMET where issued: warnings of weather over an area for a stated period, hazardous (such as thunderstorms or dust storms) or less severe but important to low-level flights.",
            "Area forecasts and significant weather charts (cloud, weather, fronts and hazards along a route), and winds and temperatures aloft (wind from true north): hours ahead.",
            "ATIS and air reports: current aerodrome information, and what pilots meet in flight, now. Reports say what has been observed, forecasts what is expected: use them together.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
