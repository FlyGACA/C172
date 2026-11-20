"""Figure 4-2 (new: Chapter 4 had no figure). Keeping the AIP current: three AIRAC amendments, one supplement and the NOTAM on the calendar of autumn 2026.

Every date is the AIP's own (data/saudi_airspace.json, "aip"; typed from the official eAIP and asserted in data/build_saudi_facts.py):
    GEN 0.2, RECORD OF AIP AMENDMENTS     AIRAC AIP AMDT 10/26   published 20 Aug 2026   effective 01 Oct 2026
                                          AIRAC AIP AMDT 11/26   published 17 Sep 2026   effective 29 Oct 2026
                                          AIRAC AIP AMDT 12/26   published 15 Oct 2026   effective 26 Nov 2026      (this line is in the AMDT 12/26 package)
    AIP SUP 36/26                         dated 10 SEP 2026, "starting on17 September 2026 and remain current until the AIP is amended with the relevant information": the expansion of the
                                          urban VFR routes in Riyadh, which "supersedes the current VFR route procedures published under OERK AD 2.22"
    AD 2 OEAH, AD 2.2 item 3              Al Ahsa's elevation: 588 FT in AMDT 11/26, 599 FT in AMDT 12/26
What is worked out from them: each amendment is published 42 days before it takes effect, the effective dates lie 28 days apart and are Thursdays.

One lane for each amendment: a dot on the day it is published, a hatched bar while it is published but not yet in force, a full bar from its effective date until the next amendment's
(the weeks in which it is the newest part of the AIP), and a pale bar after that (what it brought stays in the AIP until a later amendment changes it). Below them the supplement, open
to the right because it has no end date, and the NOTAM, which can come on any day. The upright line is a flight on 17 November 2026: AMDT 11/26 is the newest in force, AMDT 12/26 is
published and nine days from taking effect, and the supplement is in force. The NOTAM lane shows no notice: none is invented here.

Letters: the names and numbers of the publications, dates as the AIP prints them (day and month), d for days, ft; the rest is numbered."""
import datetime as dt

from figs import h_a4 as A
from figs import h_b2 as H
from figs import h_b4 as B
from figs import scene as S
from figs import marks as M  # noqa: E402

n = S.n
W, HT = 640, 334
U = "ac2"
INK = H.INK
AIP = H.DATA["aip"]
AMDT = [(a["name"].split(" ")[-1], dt.date.fromisoformat(a["published"]), dt.date.fromisoformat(a["effective"])) for a in AIP["amendments"]]
assert [a[0] for a in AMDT] == ["10/26", "11/26", "12/26"]
assert all((e - p).days == 42 and e.weekday() == 3 for _, p, e in AMDT) and all((b[2] - a[2]).days == 28 for a, b in zip(AMDT, AMDT[1:]))
SUP = AIP["sup_36_26"]
SUP_DATED, SUP_FROM = dt.date.fromisoformat(SUP["dated"]), dt.date.fromisoformat(SUP["valid_from"])
assert SUP["name"] == "AIP SUP 36/26" and (SUP_DATED, SUP_FROM) == (dt.date(2026, 9, 10), dt.date(2026, 9, 17))
CHANGE = AIP["example_change"]
assert (CHANGE["icao"], CHANGE["amdt_11_26_ft"], CHANGE["amdt_12_26_ft"], CHANGE["effective"]) == ("OEAH", 588, 599, "2026-11-26")
FLIGHT = dt.date(2026, 11, 17)                         # the day of the flight in the figure: between the effective dates of AMDT 11/26 and AMDT 12/26
assert AMDT[1][2] < FLIGHT < AMDT[2][2] and AMDT[2][1] < FLIGHT and (AMDT[2][2] - FLIGHT).days == 9

D0, D1 = dt.date(2026, 8, 13), dt.date(2026, 12, 17)   # the calendar shown
X0, X1 = 112.0, 626.0
PXD = (X1 - X0) / (D1 - D0).days
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
BLUE, BLUE_HI, BLUE_PALE = "#1D4ED8", "#3B82F6", "#BFD3FA"
AMBER, AMBER_HI = "#B45309", "#F59E0B"
RED = "#B91C1C"
SLATE = "#475569"
BAND_Y0, BAND_Y1 = 14.0, 40.0                          # the months
LANE = {"10/26": 92.0, "11/26": 126.0, "12/26": 160.0, "SUP": 234.0, "NOTAM": 274.0}
BAR = 12.0
LABEL_X = 100.0                                        # the lane labels end here
BOTTOM = 296.0                                         # the foot of the upright lines


def X(day):
    return X0 + (day - D0).days * PXD


def stamp(day):
    """A date as the AIP prints one, without the year: 29 OCT."""
    return f"{day.day:02d} {MONTHS[day.month - 1]}"


def gwidth(s, height, spacing=0.3):
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


def pill(s, x, y, colour, height=11.0, size=5.3, anchor="middle", solid=True):
    return M.chip(x, y, s, colour, size=size * 1.05, anchor=anchor, light=True, height=height)


def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F6F1E6"), (1, "#EBE2CE")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.0" stdDeviation="2.8" flood-color="#3B2A12" flood-opacity="0.24"/></filter>'
            f'<pattern id="{U}hb" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="{BLUE_PALE}" fill-opacity="0.55"/><rect width="1.5" height="5" fill="{BLUE}" fill-opacity="0.55"/></pattern>'
            f'<linearGradient id="{U}gb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLUE_HI}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>'
            f'<linearGradient id="{U}ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER_HI}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>'
            f'<linearGradient id="{U}fa" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="1" stop-color="#FFFCF5"/></linearGradient>'
            f'<linearGradient id="{U}gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.38"/><stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>'
            f'<rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>'
            f'<rect x="8" y="8" width="{W - 16}" height="{HT - 16}" rx="11" fill="#FFFCF5" filter="url(#{U}cs)"/>')


def calendar():
    """The months as a band along the top, a tick for every Thursday, and a faint column for every week."""
    out = []
    day = D0
    k = 0
    while day < D1:
        nxt = min(dt.date(day.year + (day.month == 12), day.month % 12 + 1, 1), D1)
        x0, x1 = X(day), X(nxt)
        out.append(f'<rect x="{n(x0)}" y="{n(BAND_Y0)}" width="{n(x1 - x0)}" height="{n(BAND_Y1 - BAND_Y0)}" fill="{SLATE}" fill-opacity="{0.16 if k % 2 == 0 else 0.08}"/>')
        out.append(f'<rect x="{n(x0)}" y="{n(BAND_Y1)}" width="{n(x1 - x0)}" height="{n(BOTTOM - BAND_Y1)}" fill="{SLATE}" fill-opacity="{0.045 if k % 2 == 0 else 0.0}"/>')
        if x1 - x0 > 40:
            out.append(H.glyph_text(MONTHS[day.month - 1] + (" 2026" if k == 0 else ""), (x0 + x1) / 2, BAND_Y0 + 9.0, 5.6, SLATE, spacing=0.5))
        day, k = nxt, k + 1
    day = D0                                              # (the calendar starts on a Thursday)
    assert D0.weekday() == 3
    while day <= D1:
        out.append(f'<line x1="{n(X(day))}" y1="{n(BAND_Y1 - 5.0)}" x2="{n(X(day))}" y2="{n(BAND_Y1)}" stroke="{SLATE}" stroke-width="0.8"/>')
        out.append(f'<line x1="{n(X(day))}" y1="{n(BAND_Y1)}" x2="{n(X(day))}" y2="{n(BOTTOM)}" stroke="{SLATE}" stroke-opacity="0.13" stroke-width="0.6"/>')
        day += dt.timedelta(days=7)
    out.append(f'<line x1="{n(X0)}" y1="{n(BAND_Y1)}" x2="{n(X1)}" y2="{n(BAND_Y1)}" stroke="{SLATE}" stroke-width="1.0"/>')
    return "".join(out)


def airac_lines():
    """The effective dates: an upright dashed line through the lanes of the amendments, with the date on a flag above it."""
    out = []
    for _, _, eff in AMDT:
        x = X(eff)
        foot = LANE["12/26"] + (BAR / 2 if eff == AMDT[2][2] else 16.0)
        out.append(f'<line x1="{n(x)}" y1="{n(BAND_Y1)}" x2="{n(x)}" y2="{n(foot)}" stroke="#FFFFFF" stroke-width="2.4" stroke-opacity="0.9"/>'
                   f'<line x1="{n(x)}" y1="{n(BAND_Y1)}" x2="{n(x)}" y2="{n(foot)}" stroke="{BLUE}" stroke-width="1.1" stroke-dasharray="4 2.6"/>')
        out.append(pill(stamp(eff), x, 55.0, BLUE))
    return "".join(out)


def lane_labels():
    out = [H.glyph_text("AIRAC AIP AMDT", LABEL_X, LANE["10/26"] - 21.0, 4.7, BLUE, anchor="end", spacing=0.35), H.glyph_text("AIP SUP", LABEL_X, LANE["SUP"] - 15.0, 4.7, AMBER, anchor="end", spacing=0.35)]
    for name, _, _ in AMDT:
        out.append(pill(name, LABEL_X, LANE[name], BLUE, anchor="end"))
    out.append(pill("36/26", LABEL_X, LANE["SUP"], AMBER, anchor="end"))
    out.append(pill("NOTAM", LABEL_X, LANE["NOTAM"], RED, anchor="end"))
    for y in (LANE["SUP"] - 25.0, LANE["NOTAM"] - 20.0):
        out.append(f'<line x1="18" y1="{n(y)}" x2="{n(X1)}" y2="{n(y)}" stroke="{SLATE}" stroke-opacity="0.22" stroke-width="0.7" stroke-dasharray="2 2.4"/>')
    return "".join(out)


def bar(x0, x1, y, fill, h=BAR, r=3.0, opacity=1.0, stroke=None):
    s = f' stroke="{stroke}" stroke-width="0.8"' if stroke else ""
    return f'<rect x="{n(x0)}" y="{n(y - h / 2)}" width="{n(max(x1 - x0, 0.0))}" height="{n(h)}" rx="{n(r)}" fill="{fill}" opacity="{n(opacity)}"{s}/>'


def dot(x, y, colour, r=3.6):
    return f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#FFFFFF" stroke="{colour}" stroke-width="1.6" filter="url(#{U}ds)"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 0.36)}" fill="{colour}"/>'


def amendments():
    out = []
    for i, (name, pub, eff) in enumerate(AMDT):
        y = LANE[name]
        nxt = AMDT[i + 1][2] if i + 1 < len(AMDT) else eff + dt.timedelta(days=28)
        end = min(X(nxt), X1)
        out.append(bar(X(pub), X(eff), y, f"url(#{U}hb)", h=BAR - 2.0, stroke=BLUE_PALE))                       # published, not yet in force
        if X(nxt) < X1:
            out.append(bar(X(nxt) - 3.0, X1, y, BLUE_PALE, h=BAR - 4.0, opacity=0.75) + f'<rect x="{n(X1 - 40.0)}" y="{n(y - BAR / 2)}" width="40" height="{n(BAR)}" fill="url(#{U}fa)"/>')          # what it brought stays in the AIP
        out.append(f'<g filter="url(#{U}ds)">' + bar(X(eff), end, y, f"url(#{U}gb)") + "</g>" + bar(X(eff), end, y, f"url(#{U}gl)"))                                                              # the newest in force
        out.append(dot(X(pub), y, BLUE))
        out.append(H.glyph_text(stamp(pub), X(pub), y + 12.5, 4.3, SLATE, spacing=0.3))
    return "".join(out)


def bracket(x0, x1, y, text, colour=INK):
    """A measure over a bar: a line with two ticks and what it is worth."""
    mid = (x0 + x1) / 2
    w = gwidth("42", 4.8) + 14.0
    return (f'<path d="M {n(x0 + 0.6)},{n(y + 3.0)} L {n(x0 + 0.6)},{n(y)} L {n(mid - w / 2 - 2.0)},{n(y)} M {n(mid + w / 2 + 2.0)},{n(y)} L {n(x1 - 0.6)},{n(y)} L {n(x1 - 0.6)},{n(y + 3.0)}" fill="none" stroke="{colour}" stroke-width="0.9" stroke-linecap="round" stroke-linejoin="round"/>'
            + B.label(mid, y + 2.4, text, 6.8, "middle", colour=colour, halo=False))


def measures():
    name, pub, eff = AMDT[0]
    y = LANE[name] - 12.5
    return bracket(X(pub), X(eff), y, "42 d") + bracket(X(eff), X(AMDT[1][2]), y, "28 d")


def supplement():
    y = LANE["SUP"]
    x0 = X(SUP_FROM)
    tip = [(X1 - 1.0, y), (X1 - 9.0, y - BAR * 0.8), (X1 - 9.0, y + BAR * 0.8)]
    return (f'<g filter="url(#{U}ds)">' + bar(x0, X1 - 8.0, y, f"url(#{U}ga)") + f'<polygon points="{S.pts(tip)}" fill="{AMBER}"/></g>' + bar(x0, X1 - 8.0, y, f"url(#{U}gl)")
            + f'<line x1="{n(X(SUP_DATED))}" y1="{n(y)}" x2="{n(x0)}" y2="{n(y)}" stroke="{AMBER}" stroke-width="1.2" stroke-dasharray="2.2 1.6"/>' + dot(X(SUP_DATED), y, AMBER)
            + H.glyph_text(stamp(SUP_DATED), X(SUP_DATED) - 3.0, y + 12.5, 4.3, SLATE, spacing=0.3, anchor="end") + H.glyph_text(stamp(SUP_FROM), x0 + 3.0, y + 12.5, 4.3, AMBER, spacing=0.3, anchor="start"))


def notam():
    """Any day, any hour: a band the whole length of the calendar with a mark for every day (no notice is drawn: none is invented)."""
    y = LANE["NOTAM"]
    days = (D1 - D0).days
    ticks = "".join(f'<line x1="{n(X0 + (i + 0.5) * PXD)}" y1="{n(y - 2.6)}" x2="{n(X0 + (i + 0.5) * PXD)}" y2="{n(y + 2.6)}" stroke="{RED}" stroke-opacity="0.75" stroke-width="0.9"/>' for i in range(days))
    return bar(X0, X1, y, "#FEE2E2", h=BAR, stroke="#FCA5A5") + ticks + f'<rect x="{n(X1 - 40.0)}" y="{n(y - BAR / 2 - 1)}" width="41" height="{n(BAR + 2)}" fill="url(#{U}fa)"/>'


def flight():
    """The day of a flight: an upright line through every lane, the aeroplane above it and the date below."""
    x = X(FLIGHT)
    top, foot = 74.0, BOTTOM + 2.0
    out = [f'<line x1="{n(x)}" y1="{n(top)}" x2="{n(x)}" y2="{n(foot)}" stroke="#FFFFFF" stroke-width="3.4" stroke-opacity="0.9"/><line x1="{n(x)}" y1="{n(top)}" x2="{n(x)}" y2="{n(foot)}" stroke="{INK}" stroke-width="1.5"/>']
    for key in ("11/26", "12/26", "SUP", "NOTAM"):
        out.append(f'<circle cx="{n(x)}" cy="{n(LANE[key])}" r="3.0" fill="{INK}" stroke="#FFFFFF" stroke-width="1.3"/>')
    out.append(pill(stamp(FLIGHT), x, foot + 8.0, INK))
    return "".join(out)


CARD = (X(AMDT[2][2]) - 6.0, LANE["12/26"] + 14.0, 84.0, 30.0)             # the change that comes with AMDT 12/26: x, y, width, height


def change():
    x, y, w, h = CARD
    cx = x + w / 2
    eff = X(AMDT[2][2])
    return (f'<line x1="{n(eff)}" y1="{n(LANE["12/26"] + BAR / 2)}" x2="{n(eff)}" y2="{n(y)}" stroke="{BLUE}" stroke-width="1.1"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="6" fill="#FFFFFF" stroke="{BLUE}" stroke-width="1.0" filter="url(#{U}ds)"/>'
            + H.glyph_text("OEAH", cx, y + 8.5, 5.2, INK, spacing=0.5)
            + B.label(cx - 9.0, y + 23.0, "588 ft", 7.0, "end", colour=SLATE, halo=False) + B.label(cx + 9.0, y + 23.0, "599 ft", 7.0, "start", colour=BLUE, halo=False)
            + f'<line x1="{n(cx - 5.5)}" y1="{n(y + 20.6)}" x2="{n(cx + 3.0)}" y2="{n(y + 20.6)}" stroke="{INK}" stroke-width="1.1"/><polygon points="{S.pts([(cx + 6.0, y + 20.6), (cx + 2.2, y + 18.4), (cx + 2.2, y + 22.8)])}" fill="{INK}"/>')


def callouts():
    c = S.callout
    out = []
    x = X(AMDT[0][2])
    out.append(c(1, x - 32.0, 62.0, x - 17.5, 57.0, r=8.8))                                                   # an AIRAC effective date
    name, pub, eff = AMDT[1]
    out.append(c(2, X(pub) - 20.0, LANE[name] - 13.0, X(pub) - 3.4, LANE[name] - 2.6, r=8.8))                 # published 42 days ahead
    mid = (X(eff) + X(AMDT[2][2])) / 2
    out.append(c(3, mid - 26.0, LANE[name] + 19.0, mid - 14.0, LANE[name] + 5.5, r=8.8))                       # the newest in force
    out.append(c(4, X(FLIGHT) - 24.0, 80.0, X(FLIGHT) - 1.2, 84.0, r=8.8))                                     # the flight
    out.append(c(5, CARD[0] + CARD[2] - 6.0, CARD[1] + CARD[3] + 13.0, CARD[0] + CARD[2] - 14.0, CARD[1] + CARD[3] + 0.5, r=8.8))          # the change
    x = X(dt.date(2026, 10, 8))
    out.append(c(6, x, LANE["SUP"] - 19.0, x, LANE["SUP"] - 6.0, r=8.8))                                       # the supplement
    x = X(dt.date(2026, 9, 3))
    out.append(c(7, x, LANE["NOTAM"] + 20.0, x, LANE["NOTAM"] + 6.5, r=8.8))                                   # the NOTAM
    return "".join(out)


def layers():
    x = X(FLIGHT)
    return [H.defs(U, W, HT), background(), calendar(), lane_labels(), airac_lines(), notam(), amendments(), supplement(), measures(), flight(), A.plane(x, 61.0, 22.0, angle=90.0), change(), callouts()]


def plate():
    return {
        "id": "fig-04-02-airac-calendar",
        "replaces": "fig-04-02-airac-calendar.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-04-02-airac-calendar.jpg",
        "caption": "Figure 4-2. Keeping the AIP current: three AIRAC amendments, a supplement and the NOTAM on the calendar of autumn 2026",
        "desc": ("Figure 4-2. Keeping the AIP current: three AIRAC amendments, a supplement and the NOTAM on the calendar of autumn 2026. The dates are those AIP-KSA prints in GEN 0.2 and in "
                 "AIP SUP 36/26; the 42 and 28 days are worked out from them. Not for navigation."),
        "legend": [
            "An AIRAC effective date. The three here, 1 October, 29 October and 26 November 2026, are Thursdays 28 days apart.",
            "An AIRAC amendment is published before it takes effect: AMDT 11/26 on 17 September, 42 days ahead.",
            "From its effective date the amendment is part of the AIP. AMDT 11/26 is the newest in force from 29 October until AMDT 12/26 follows it on 26 November.",
            "A flight on 17 November: the AIP to use is the one that AMDT 11/26 made, and AMDT 12/26 has been published for a month, so what changes nine days later can already be read.",
            "One change that AMDT 12/26 brings: the elevation of Al Ahsa (`OEAH`) in AD 2.2, 588 ft until then and 599 ft from 26 November.",
            "A supplement in force: AIP SUP 36/26, dated 10 September and valid from 17 September 2026 until the AIP itself is amended. It replaces the urban VFR routes round Riyadh that the page AD 2 OERK still prints.",
            "NOTAM can come on any day and at any hour.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
