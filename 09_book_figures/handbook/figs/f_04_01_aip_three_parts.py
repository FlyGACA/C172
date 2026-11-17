"""Figure 4-1 (new: Chapter 4 had no figure). Where to look in the AIP: its three parts, each closer than the one before, with the sections a VFR pilot opens for a local flight at Thumamah.

Three cards, one for each part of AIP-KSA as GEN 0.1.4.1 describes it, each with a real map at its own scale and, under it, the sections that have no place on a map:
    Part 1, GEN    the whole State: the land and its relief from open data (Natural Earth, public domain; figs/arabia_real.py) on the cone of the AIP's own charts, coasts and no boundaries
    Part 2, ENR    the airspace: the country round Riyadh on a shaded relief (NASA SRTM, public domain; figs/terrain_real.py), with the Riyadh terminal control area (ENR 2.1), the danger
                   and restricted areas nearest to Thumamah (ENR 5.1), the DVOR/DME KSA (ENR 4.1), and the two zones that are NOT in Part 2: the Riyadh control zone and the Thumamah
                   aerodrome traffic zone, each printed in AD 2.17 of its aerodrome
    Part 3, AD     one aerodrome: Thumamah on an open satellite picture (Copernicus Sentinel-2; figs/imagery_real.py; "Contains modified Copernicus Sentinel data 2026"), with what its
                   entry AD 2 OETH prints: the runway (AD 2.12), the obstacles (2.10), the traffic zone (2.17), the frequency (2.18), the wildlife reserve (2.21), the circuits and
                   the two reporting points (2.22)
The frame on each map is the whole of the next map, and a wedge joins the two. True north is up on the second and third maps; each map has its own scale bar.

Every tag is a section number of AIP-KSA, AMDT 11/26, in the colour of its part. The numbers and titles are the AIP's own (its table of contents, the menu of the eAIP), and every section
tagged here is one FlyGACA has read in part or in whole (the book's source registry says which paragraphs). The small words beside the tags are ICAO abbreviations and values the pages
print: UTC and the units (GEN 2.1.1, 2.1.2), TORA, LDA and SWY (GEN 2.2), SR and SS (GEN 2.7), AMDT, SUP and NOTAM (GEN 3.1.3), 1:500 000 (GEN 3.2.4), MET (GEN 3.5), SAR and 406 MHz
(GEN 3.6.3); TIBA 122.8 (ENR 1.1.5.2), VFR (ENR 1.2), the classes (ENR 1.4), 7700, 7600 and 7500 (ENR 1.6.2.4.3.1), QNH and 13 000 ft (ENR 1.7.2.1.1), FPL (ENR 1.10), the sheet 2546-C
(ENR 6); OETH, NTL, VFR (AD 1.3), 1 870 ft and 42 °C (AD 2.2), 0500-1200 UTC (AD 2.3, AD administration), TORA 4 000 m (AD 2.13), PAPI 3° (AD 2.14, runway 35), NIL (AD 2.19), the
Aerodrome Chart - ICAO (AD 2.24). The circuit is drawn 1 NM wide as in Figure 18-8 (the AIP gives no width), and the wildlife reserve as a ring 0.7 NM west of the runway (the AIP
gives no limits). Not for navigation. Letters: section numbers, codes, abbreviations and numbers with their units; the rest is numbered."""
import math

from figs import arabia_real as AR
from figs import h_b2 as H
from figs import h_b4 as B
from figs import imagery_real as IR
from figs import scene as S
from figs import terrain_real as TR

n = S.n
W, HT = 640, 412
U = "ai1"
INK = H.INK
PART = {"GEN": "#475569", "ENR": "#6D28D9", "AD": "#BE185D"}          # the colours of the three parts (none of them a colour of an airspace class)
PART_HI = {"GEN": "#64748B", "ENR": "#8B5CF6", "AD": "#DB2777"}
OETH, OERK, AREAS = H.DATA["oeth"], H.DATA["oerk"], H.DATA["areas"]
KSA = OERK["ksa"]
RW17, RW35 = (next(r for r in OETH["runways"] if r["id"] == i) for i in ("17", "35"))
assert (OETH["elev_ft"], OETH["ref_temp_c"]) == (1870, 42) and OETH["traffic"] == "VFR"                                    # AD 2.2
assert RW17["declared_m"]["TORA"] == 4000 and RW35["declared_m"]["TORA"] == 4000                                          # AD 2.13
assert (OETH["atz"]["radius_nm"], OETH["atz"]["transition_altitude_ft"], OETH["atz"]["class"]) == (5, 13000, "G")         # AD 2.17
assert (OETH["comms"]["unicom"]["mhz"], OETH["comms"]["tiba_mhz"]) == (124.4, 122.8)                                      # AD 2.18, ENR 1.1.5.2
assert (OERK["ctr"]["radius_nm"], OERK["ctr"]["class"]) == (10, "D") and KSA["id"] == "KSA"                               # AD 2 OERK 2.17 and 2.19 (ENR 4.1 lists the station too)
assert H.DATA["charts"]["sheet_of_oeth"] == "2546-C"                                                                      # ENR 6

# ----------------------------------------------------------------------------------------------------- the three cards
TOP, BOTTOM, HEAD = 10.0, 402.0, 26.0
CARDS = {"GEN": (10.0, 184.0), "ENR": (202.0, 214.0), "AD": (424.0, 206.0)}          # x of the left edge, width
MAP_Y, MAP_H, INSET = TOP + HEAD + 6.0, 140.0, 6.0
ROW_Y, ROW_STEP = 204.0, 30.0


def window(part):
    """The box of a card's map: x, y, width, height."""
    x, w = CARDS[part]
    return (x + INSET, MAP_Y, w - 2 * INSET, MAP_H)


GX, GY, GW, GH = window("GEN")
EX, EY, EW, EH = window("ENR")
AX, AY, AW, AH = window("AD")

# the aerodrome (Part 3): the country the satellite picture covers round Thumamah
S_AD = 14.9                                           # canvas units to the NM
AD_ARP = (50.0, 80.0)                                 # where the reference point lies in the window
FA_LOCAL = H.Frame(OETH["arp"]["lat"], OETH["arp"]["lon"], S_AD, *AD_ARP)
FA = H.Frame(OETH["arp"]["lat"], OETH["arp"]["lon"], S_AD, AX + AD_ARP[0], AY + AD_ARP[1])
assert IR.covers(FA_LOCAL, (AW, AH)), "the satellite picture does not cover the aerodrome's map"
IR.ensure("terrain-04-01-ad", FA_LOCAL, (AW, AH), veil=0.16, saturation=0.86, lift=1.05)

# the airspace (Part 2): from the danger area OED33 in the south-west to the restricted area OER212 in the east
S_ENR = 4.3
ENR_ARP = (89.0, 58.0)
FE_LOCAL = H.Frame(OETH["arp"]["lat"], OETH["arp"]["lon"], S_ENR, *ENR_ARP)
FE = H.Frame(OETH["arp"]["lat"], OETH["arp"]["lon"], S_ENR, EX + ENR_ARP[0], EY + ENR_ARP[1])
for _lon, _lat in ((FE_LOCAL.lon0 - ENR_ARP[0] / S_ENR / FE_LOCAL.k, FE_LOCAL.lat0 + ENR_ARP[1] / S_ENR / 60.0), (FE_LOCAL.lon0 + (EW - ENR_ARP[0]) / S_ENR / FE_LOCAL.k, FE_LOCAL.lat0 - (EH - ENR_ARP[1]) / S_ENR / 60.0)):
    assert TR.META["west"] <= _lon <= TR.META["east"] and TR.META["south"] <= _lat <= TR.META["north"], "the elevation data do not cover the airspace map"
TR.ensure("terrain-04-01-enr", FE_LOCAL, (EW, EH), veil=0.26, soft=0.8, exaggeration=10.0)

# the State (Part 1): the Kingdom on the cone of the AIP's charts, the meridian of 45 E upright
CONE = AR.CONE
K_WEST, K_EAST, K_SOUTH, K_NORTH = 34.0, 56.2, 15.6, 32.8          # the box the Kingdom is fitted into


def _edge(step=0.5):
    out = []
    for lat in (K_SOUTH, K_NORTH):
        k = int(round((K_EAST - K_WEST) / step))
        out += [(lat, K_WEST + (K_EAST - K_WEST) * i / k) for i in range(k + 1)]
    return out


_xy = [tuple(float(v) for v in CONE.xy(lat, lon)) for lat, lon in _edge()]
_x0, _x1, _y0, _y1 = min(p[0] for p in _xy), max(p[0] for p in _xy), min(p[1] for p in _xy), max(p[1] for p in _xy)
S_GEN = min(GW / (_x1 - _x0), GH / (_y1 - _y0))                    # canvas units to the metre
G_ORIGIN = (GW / 2 - (_x0 + _x1) / 2 * S_GEN, GH / 2 + (_y0 + _y1) / 2 * S_GEN)          # in the window
AR.ensure_chart("terrain-04-01-gen", CONE, (GW, GH), S_GEN, G_ORIGIN, 28.2, 63.8, 8.2, 39.8, strength=1.2)


def PG(lat, lon):
    """The canvas point of a place on the map of the Kingdom."""
    x, y = CONE.xy(lat, lon)
    return (GX + G_ORIGIN[0] + float(x) * S_GEN, GY + G_ORIGIN[1] - float(y) * S_GEN)


# ----------------------------------------------------------------------------------------------------- small parts
def gwidth(s, height, spacing=0.3):
    """The width of a word set in the glyphs of the book's figures."""
    g = H._GLYPHS
    k = height / g["cap_height"]
    return sum((height * 0.38 if c == " " else g["glyphs"][c]["advance"] * k) + spacing for c in s) - spacing


TAG_H, TAG_T = 11.0, 5.3                              # the height of a tag and of its letters


def tag_w(code):
    return gwidth(code, TAG_T) + 10.0


def tag(code, x, y, anchor="middle"):
    """A section number on a pill in the colour of its part: (x, y) is the middle of the pill, or of its left or right end."""
    part = code.split(" ")[0]
    w = tag_w(code)
    x0 = x - w / 2 if anchor == "middle" else x if anchor == "start" else x - w
    return (f'<rect x="{n(x0)}" y="{n(y - TAG_H / 2)}" width="{n(w)}" height="{n(TAG_H)}" rx="{n(TAG_H / 2)}" fill="{PART[part]}" stroke="#FFFFFF" stroke-width="1.1" filter="url(#{U}ds)"/>'
            + H.glyph_text(code, x0 + w / 2, y, TAG_T, "#FFFFFF", spacing=0.3))


def leader(p, q, colour=INK):
    """A thin line from a tag to the thing it names, with a dot on the thing."""
    return (f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="2.2" stroke-linecap="round"/>'
            f'<line x1="{n(p[0])}" y1="{n(p[1])}" x2="{n(q[0])}" y2="{n(q[1])}" stroke="{colour}" stroke-width="0.9" stroke-linecap="round"/>'
            f'<circle cx="{n(q[0])}" cy="{n(q[1])}" r="1.5" fill="{colour}" stroke="#FFFFFF" stroke-width="0.7"/>')


def mini_scale(x, y, length, text, dark=True):
    """A small scale bar: a line with two ticks and its length over it."""
    c = INK if dark else "#FFFFFF"
    return (f'<rect x="{n(x - 4)}" y="{n(y - 10.5)}" width="{n(length + 8)}" height="{n(15)}" rx="4" fill="#FFFFFF" fill-opacity="0.82"/>'
            f'<path d="M {n(x)},{n(y - 2.2)} L {n(x)},{n(y + 1.2)} L {n(x + length)},{n(y + 1.2)} L {n(x + length)},{n(y - 2.2)}" fill="none" stroke="{c}" stroke-width="1.1" stroke-linejoin="round"/>'
            + H.glyph_text(text, x + length / 2, y - 5.2, 4.4, c, spacing=0.3))


def mini_north(x, y, h=13.0):
    half = h * 0.26
    left = [(x, y - h / 2), (x - half, y + h / 2), (x, y + h * 0.26)]
    right = [(x, y - h / 2), (x + half, y + h / 2), (x, y + h * 0.26)]
    return (f'<polygon points="{S.pts(left)}" fill="{INK}" stroke="#FFFFFF" stroke-width="1.0" stroke-linejoin="round"/><polygon points="{S.pts(right)}" fill="#F4F1E6" stroke="#FFFFFF" stroke-width="1.0" stroke-linejoin="round"/>'
            f'<polygon points="{S.pts(right)}" fill="#F4F1E6" stroke="{INK}" stroke-width="0.5" stroke-linejoin="round"/>' + H.label("N", x, y - h / 2 - 5.0, 5.0, INK, spacing=0, halo=2.0))


# ----------------------------------------------------------------------------------------------------- the cards and their grounds
def background():
    return (f'<defs>{S.gradient(U + "bg", [(0, "#F4EFE3"), (1, "#E9E0CB")])}'
            f'<filter id="{U}cs" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="2.2" stdDeviation="3.0" flood-color="#3B2A12" flood-opacity="0.26"/></filter>'
            + "".join(f'<linearGradient id="{U}h{p}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{PART[p]}"/><stop offset="1" stop-color="{PART_HI[p]}"/></linearGradient>'
                      f'<clipPath id="{U}c{p}"><rect x="{n(CARDS[p][0])}" y="{n(TOP)}" width="{n(CARDS[p][1])}" height="{n(BOTTOM - TOP)}" rx="10"/></clipPath>'
                      f'<clipPath id="{U}m{p}"><rect x="{n(window(p)[0])}" y="{n(window(p)[1])}" width="{n(window(p)[2])}" height="{n(window(p)[3])}" rx="6"/></clipPath>' for p in PART)
            + f'</defs><rect x="0" y="0" width="{W}" height="{HT}" fill="url(#{U}bg)"/>')


def card(part):
    x, w = CARDS[part]
    return (f'<rect x="{n(x)}" y="{n(TOP)}" width="{n(w)}" height="{n(BOTTOM - TOP)}" rx="10" fill="#FFFCF5" filter="url(#{U}cs)"/>'
            f'<g clip-path="url(#{U}c{part})"><rect x="{n(x)}" y="{n(TOP)}" width="{n(w)}" height="{n(HEAD)}" fill="url(#{U}h{part})"/>'
            f'<rect x="{n(x)}" y="{n(TOP)}" width="{n(w)}" height="{n(HEAD * 0.5)}" fill="#FFFFFF" fill-opacity="0.10"/></g>'
            + H.glyph_text(part, x + 13.0, TOP + HEAD / 2 + 0.3, 11.0, "#FFFFFF", anchor="start", spacing=0.9)
            + f'<rect x="{n(x)}" y="{n(TOP)}" width="{n(w)}" height="{n(BOTTOM - TOP)}" rx="10" fill="none" stroke="{PART[part]}" stroke-opacity="0.55" stroke-width="1.0"/>')


def ground(part, name):
    """The picture of a card's map, cut to the rounded window: the opening of the group, the sprite, the close."""
    x, y, w, h = window(part)
    return [f'<g clip-path="url(#{U}m{part})">', {"name": name, "at": [x + w / 2, y + h / 2], "width": w}, "</g>"]


def window_frame(part):
    x, y, w, h = window(part)
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="6" fill="none" stroke="#FFFFFF" stroke-width="2.4"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="6" fill="none" stroke="{PART[part]}" stroke-width="1.1"/>')


# ----------------------------------------------------------------------------------------------------- Part 1: the State
ZOOM_E = [FE.xy(0, 0)]                                # (filled below: the corners of the airspace map as places)


def _enr_corner(dx, dy):
    """The place (lat, lon) at a point of the airspace map's window."""
    return (FE_LOCAL.lat0 - (dy - ENR_ARP[1]) / S_ENR / 60.0, FE_LOCAL.lon0 + (dx - ENR_ARP[0]) / S_ENR / FE_LOCAL.k)


GEN_FRAME = [PG(*_enr_corner(0, 0)), PG(*_enr_corner(EW, 0)), PG(*_enr_corner(EW, EH)), PG(*_enr_corner(0, EH))]          # the airspace map on the map of the Kingdom


def gen_map():
    out = [f'<g clip-path="url(#{U}mGEN)">', '<g fill="none" stroke="#35507A" stroke-opacity="0.34" stroke-width="0.45">']
    for lon in (35, 40, 45, 50, 55):
        out.append(f'<polyline points="{S.pts([PG(10 + 30 * i / 40, lon) for i in range(41)])}"/>')
    for lat in (15, 20, 25, 30):
        out.append(f'<polyline points="{S.pts([PG(lat, 30 + 30 * i / 60) for i in range(61)])}"/>')
    out.append("</g>")
    for lat in (20, 30):
        p = PG(lat, 35.0)
        out.append(H.label(f"{lat}°N", GX + 11.0, p[1] - 3.2, 3.9, "#35507A", spacing=0.2, halo=1.8))
    for lon in (40, 50):
        p = PG(16.6, lon)
        out.append(H.label(f"{lon}°E", p[0] + 9.0, GY + GH - 6.0, 3.9, "#35507A", spacing=0.2, halo=1.8))
    out.append("</g>")
    return "".join(out)


def box_of(points, grow=0.0, least=(0.0, 0.0)):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w, h = max(max(xs) - min(xs) + 2 * grow, least[0]), max(max(ys) - min(ys) + 2 * grow, least[1])
    return (cx - w / 2, cy - h / 2, w, h)


def zoom(src, dst, part):
    """The frame `src` (x, y, w, h) on one map and the wedge that opens from it to the left edge of the window `dst` of the next."""
    x, y, w, h = src
    dx, dy, _dw, dh = dst
    wedge = [(x + w, y), (dx, dy + 2.0), (dx, dy + dh - 2.0), (x + w, y + h)]
    c = PART[part]
    return (f'<polygon points="{S.pts(wedge)}" fill="{c}" fill-opacity="0.05"/>'
            + "".join(f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="2.0"/>'
                      f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="{c}" stroke-width="0.9" stroke-dasharray="3.2 2.2"/>' for a, b in ((wedge[0], wedge[1]), (wedge[3], wedge[2])))
            + f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="none" stroke="#FFFFFF" stroke-width="2.6"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="none" stroke="{c}" stroke-width="1.3"/>')


GEN_ZOOM = box_of(GEN_FRAME, least=(7.0, 5.0))

# ----------------------------------------------------------------------------------------------------- Part 2: the airspace
E_T = FE.xy(OETH["arp"]["lon"], OETH["arp"]["lat"])
E_K = FE.xy(OERK["arp"]["lon"], OERK["arp"]["lat"])
E_STN = FE.xy(KSA["lon"], KSA["lat"])
E_ATZ = H.circle(E_T[0], E_T[1], FE.r(OETH["atz"]["radius_nm"]))
E_CTR = H.circle(E_K[0], E_K[1], FE.r(OERK["ctr"]["radius_nm"]))
E_TMA = H.poly(FE.ring(AREAS["riyadh_east_tma_part1"]["ring"][:-1]))
PRD = {k: FE.ring(v["ring"][:-1]) for k, v in AREAS["prd"].items()}
# the aerodrome's map on the airspace map
ENR_FRAME = [FE.xy(FA_LOCAL.lon0 + (dx - AD_ARP[0]) / S_AD / FA_LOCAL.k, FA_LOCAL.lat0 - (dy - AD_ARP[1]) / S_AD / 60.0) for dx, dy in ((0, 0), (AW, 0), (AW, AH), (0, AH))]
ENR_ZOOM = box_of(ENR_FRAME)


def thr(frame, airport, rid):
    rw = next(r for r in airport["runways"] if r["id"] == rid)
    return frame.xy(rw["threshold"]["lon"], rw["threshold"]["lat"])


def station(x, y, r=4.2, colour="#1B4FD0"):
    """The mark of a VOR/DME on a chart, small: a hexagon in a square with a dot."""
    hexa = [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    return (f'<rect x="{n(x - r * 1.05)}" y="{n(y - r * 0.92)}" width="{n(r * 2.1)}" height="{n(r * 1.84)}" fill="#FFFFFF" fill-opacity="0.9" stroke="{colour}" stroke-width="0.8"/>'
            f'<polygon points="{S.pts(hexa)}" fill="#FFFFFF" stroke="{colour}" stroke-width="1.0" stroke-linejoin="round"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 0.24)}" fill="{colour}"/>')


def enr_map():
    out = [f'<g clip-path="url(#{U}mENR)">']
    holes = [(E_K[0], E_K[1], FE.r(OERK["ctr"]["radius_nm"])), (E_T[0], E_T[1], FE.r(OETH["atz"]["radius_nm"]))]          # ENR 2.1: "Excluding Riyadh CTR. KHASHM ALAN ATZ, THUMAMAH ATZ."
    out.append(f"<defs>{H.hole_mask(U + 'tm', W, HT, holes)}</defs>")
    out.append(H.fill(E_TMA, "C", opacity=0.10, mask=U + "tm") + H.edge(E_TMA, "C", dash="5 3", width=1.1, casing=2.6, mask=U + "tm"))
    out.append(H.fill(E_CTR, "D", opacity=0.16) + H.edge(E_CTR, "D", dash="5 3", width=1.2, casing=2.8))
    out.append(H.fill(E_ATZ, "G", opacity=0.18) + H.edge(E_ATZ, "G", dash="5 3", width=1.2, casing=2.8))
    for code, ring in PRD.items():
        cx, cy = sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
        out.append(H.special_use(U, H.poly(ring)))
        at = {"OED25": (cx + 0.5, cy + 12.5), "OER212": (cx, cy + 11.0), "OED33": (cx, cy - 1.0)}[code]
        out.append(H.label(code, at[0], at[1], 4.0, H.RED, spacing=0.25, halo=1.9))
    out.append(H.runway(U, thr(FE, OETH, "17"), thr(FE, OETH, "35"), 1.5))
    out.append(station(E_STN[0], E_STN[1]))
    out.append(H.label("KSA", E_STN[0] - 13.0, E_STN[1] + 0.3, 4.2, "#1B4FD0", spacing=0.25, halo=1.9))
    out.append(H.class_disc(U, EX + 120.0, EY + 14.0, "C", 5.4) + H.class_disc(U, CTR_DISC[0], CTR_DISC[1], "D", 5.4) + H.class_disc(U, E_T[0] - 8.5, E_T[1] + 9.5, "G", 4.6))
    out.append("</g>")
    return "".join(out)


CTR_DISC = (E_K[0] - 25.0, E_K[1] - 20.0)             # the letter of the control zone's class, and after it the tag of the section that prints the zone
CTR_TAG = (CTR_DISC[0] + 9.0, CTR_DISC[1])


def enr_tags():
    out = []
    p = (EX + 120.0 + 5.4, EY + 14.0)
    out.append(tag("ENR 2.1", p[0] + 4.0, p[1], "start"))                                                    # the terminal control area
    r212 = PRD["OER212"]
    cx, cy = sum(q[0] for q in r212) / len(r212), sum(q[1] for q in r212) / len(r212)
    out.append(tag("ENR 5.1", cx, cy - 4.0))                                                                 # the danger and restricted areas
    out.append(tag("ENR 4.1", E_STN[0], E_STN[1] + 11.0))                                                    # the station
    out.append(tag("AD 2.17", CTR_TAG[0], CTR_TAG[1], "start"))                                              # the control zone: in its aerodrome's entry
    return "".join(out)


# ----------------------------------------------------------------------------------------------------- Part 3: the aerodrome
A_T = FA.xy(OETH["arp"]["lon"], OETH["arp"]["lat"])
A_17, A_35 = thr(FA, OETH, "17"), thr(FA, OETH, "35")
A_ATZ = H.circle(A_T[0], A_T[1], FA.r(OETH["atz"]["radius_nm"]))
A_NV, A_EV = (FA.xy(v["lon"], v["lat"]) for v in OETH["vrps"])
_L = H.dist(A_17, A_35)
UX, UY = (A_35[0] - A_17[0]) / _L, (A_35[1] - A_17[1]) / _L          # along the runway from the threshold of 17 to that of 35
WX, WY = UY, -UX                                                      # to the west of it (left of the direction 17 -> 35 on the page is east; the west is to the right of it turned: see P)
if WX > 0:
    WX, WY = -WX, -WY


def PA(s_nm, t_nm):
    """A canvas point of the aerodrome's map: s NM from the threshold of 17 towards that of 35, t NM to the west of the centreline."""
    return (A_17[0] + (UX * s_nm + WX * t_nm) * S_AD, A_17[1] + (UY * s_nm + WY * t_nm) * S_AD)


RWY_NM = _L / S_AD
CIRCUIT = [PA(-0.55, 0.0), PA(-0.55, 1.0), PA(RWY_NM + 0.55, 1.0), PA(RWY_NM + 0.55, 0.0)]          # 1 NM wide, as Figure 18-8 draws it (the AIP gives no width)
RESERVE = PA(RWY_NM / 2, 0.7)                                         # "0.7 NM West of RWY 17/35" (AD 2.21)
OBSTACLE = PA(-1.62, 0.0)                                             # the escarpment on the centre line of runway 17, about 3 km out (AD 2.10)


def rounded(points, r):
    """A closed path through the corners of a rectangle, each rounded by `r`."""
    d = []
    k = len(points)
    for i in range(k):
        a, b, c = points[i - 1], points[i], points[(i + 1) % k]
        la, lc = H.dist(a, b), H.dist(c, b)
        p = (b[0] + (a[0] - b[0]) / la * r, b[1] + (a[1] - b[1]) / la * r)
        q = (b[0] + (c[0] - b[0]) / lc * r, b[1] + (c[1] - b[1]) / lc * r)
        d.append(("M" if i == 0 else "L") + f" {n(p[0])},{n(p[1])} Q {n(b[0])},{n(b[1])} {n(q[0])},{n(q[1])}")
    return " ".join(d) + " Z"


def ad_map():
    out = [f'<g clip-path="url(#{U}mAD)">']
    out.append(H.fill(A_ATZ, "G", opacity=0.07) + H.edge(A_ATZ, "G", dash="6 3.4", width=1.4, casing=3.0))
    d = rounded(CIRCUIT, 5.0)
    out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.0" stroke-linejoin="round"/><path d="{d}" fill="none" stroke="#2563EB" stroke-width="1.4" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{n(RESERVE[0])}" cy="{n(RESERVE[1])}" r="4.6" fill="#C2410C" fill-opacity="0.22" stroke="#FFFFFF" stroke-width="2.2"/>'
               f'<circle cx="{n(RESERVE[0])}" cy="{n(RESERVE[1])}" r="4.6" fill="none" stroke="#C2410C" stroke-width="1.0" stroke-dasharray="2.2 1.4"/>')
    out.append(H.runway(U, A_17, A_35, 2.4))
    o = OBSTACLE                                                      # an obstacle as charts mark one: a pointed mark with a dot under it
    out.append(f'<path d="M {n(o[0] - 3.4)},{n(o[1] + 3.0)} L {n(o[0])},{n(o[1] - 4.2)} L {n(o[0] + 3.4)},{n(o[1] + 3.0)}" fill="none" stroke="#FFFFFF" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>'
               f'<path d="M {n(o[0] - 3.4)},{n(o[1] + 3.0)} L {n(o[0])},{n(o[1] - 4.2)} L {n(o[0] + 3.4)},{n(o[1] + 3.0)}" fill="none" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round"/>'
               f'<circle cx="{n(o[0])}" cy="{n(o[1] + 2.4)}" r="1.0" fill="{INK}"/>')
    out.append(H.vrp(U, A_NV[0], A_NV[1], 8.0) + H.vrp(U, A_EV[0], A_EV[1], 8.0))
    out.append(H.label("17", A_17[0] + 6.5, A_17[1] - 1.0, 3.8, INK, spacing=0.2, halo=1.8) + H.label("35", A_35[0] + 6.5, A_35[1] + 3.0, 3.8, INK, spacing=0.2, halo=1.8))
    out.append("</g>")
    return "".join(out)


RADIO = (A_T[0] + 15.0, A_T[1] - 6.0)                 # the frequency: a loudspeaker beside the aerodrome


def ad_tags():
    out = []
    p = PA(RWY_NM * 0.72, 0.0)
    out.append(leader((p[0] + 20.0, p[1] + 9.0), (p[0] + 1.6, p[1])) + tag("AD 2.12", p[0] + 17.0, p[1] + 12.0, "start"))                         # the runway
    out.append(H.speaker(U, RADIO[0], RADIO[1], 6.6, PART["AD"]) + tag("AD 2.18", RADIO[0] + 9.5, RADIO[1], "start"))                              # the frequency
    a = math.radians(128.0)
    q = (A_T[0] + FA.r(5) * math.sin(a), A_T[1] - FA.r(5) * math.cos(a))
    out.append(tag("AD 2.17", q[0] + 3.0, q[1] - 9.0, "start") + leader((q[0] + 8.0, q[1] - 4.0), q))                                               # the traffic zone
    out.append(leader((AX + 30.0, OBSTACLE[1] - 6.0), (OBSTACLE[0] - 3.6, OBSTACLE[1] + 0.4)) + tag("AD 2.10", AX + 4.0, OBSTACLE[1] - 8.0, "start"))     # the obstacles
    out.append(leader((AX + 26.0, RESERVE[1] - 21.0), (RESERVE[0] - 3.4, RESERVE[1] - 3.0)) + tag("AD 2.21", AX + 4.0, RESERVE[1] - 24.0, "start"))       # the wildlife reserve
    c = CIRCUIT[2]
    out.append(leader((AX + 24.0, c[1] + 15.0), (c[0] + 2.0, c[1] - 2.0)) + tag("AD 2.22", AX + 4.0, c[1] + 18.0, "start"))                               # the circuits and the reporting points
    return "".join(out)


# ----------------------------------------------------------------------------------------------------- the rows under the maps: icons
def _badge(x, y, part, r=8.0):
    return H.badge(U, x, y, r, PART[part])


def ic_clock(x, y, c):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="4.6" fill="none" stroke="{c}" stroke-width="1.2"/>'
            f'<path d="M {n(x)},{n(y - 3.0)} L {n(x)},{n(y)} L {n(x + 2.3)},{n(y + 1.3)}" fill="none" stroke="{c}" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>')


def ic_book(x, y, c):
    return (f'<path d="M {n(x)},{n(y - 2.9)} Q {n(x - 2.6)},{n(y - 4.6)} {n(x - 5.2)},{n(y - 3.4)} L {n(x - 5.2)},{n(y + 3.4)} Q {n(x - 2.6)},{n(y + 2.2)} {n(x)},{n(y + 3.9)} '
            f'Q {n(x + 2.6)},{n(y + 2.2)} {n(x + 5.2)},{n(y + 3.4)} L {n(x + 5.2)},{n(y - 3.4)} Q {n(x + 2.6)},{n(y - 4.6)} {n(x)},{n(y - 2.9)} Z" fill="none" stroke="{c}" stroke-width="1.1" stroke-linejoin="round"/>'
            f'<line x1="{n(x)}" y1="{n(y - 2.9)}" x2="{n(x)}" y2="{n(y + 3.9)}" stroke="{c}" stroke-width="1.0"/>')


def ic_sun(x, y, c):
    rays = "".join(f'<line x1="{n(x + 4.2 * math.cos(math.radians(a)))}" y1="{n(y + 1.8 - 4.2 * math.sin(math.radians(a)))}" x2="{n(x + 5.7 * math.cos(math.radians(a)))}" y2="{n(y + 1.8 - 5.7 * math.sin(math.radians(a)))}" '
                   f'stroke="{c}" stroke-width="1.0" stroke-linecap="round"/>' for a in (20, 55, 90, 125, 160))
    return (f'<path d="M {n(x - 3.0)},{n(y + 1.8)} A 3.0,3.0 0 0 1 {n(x + 3.0)},{n(y + 1.8)} Z" fill="{c}"/>' + rays
            + f'<line x1="{n(x - 5.8)}" y1="{n(y + 2.9)}" x2="{n(x + 5.8)}" y2="{n(y + 2.9)}" stroke="{c}" stroke-width="1.2" stroke-linecap="round"/>')


def ic_page(x, y, c):
    return (f'<path d="M {n(x - 3.6)},{n(y - 4.8)} L {n(x + 1.2)},{n(y - 4.8)} L {n(x + 3.6)},{n(y - 2.4)} L {n(x + 3.6)},{n(y + 4.8)} L {n(x - 3.6)},{n(y + 4.8)} Z" fill="none" stroke="{c}" stroke-width="1.1" stroke-linejoin="round"/>'
            f'<path d="M {n(x + 1.2)},{n(y - 4.8)} L {n(x + 1.2)},{n(y - 2.4)} L {n(x + 3.6)},{n(y - 2.4)}" fill="none" stroke="{c}" stroke-width="0.9" stroke-linejoin="round"/>'
            + "".join(f'<line x1="{n(x - 1.9)}" y1="{n(y + dy)}" x2="{n(x + 1.9)}" y2="{n(y + dy)}" stroke="{c}" stroke-width="0.9" stroke-linecap="round"/>' for dy in (-0.6, 1.3, 3.1)))


def ic_chart(x, y, c):
    zig = [(x - 5.4, y - 3.0), (x - 1.8, y - 4.4), (x + 1.8, y - 3.0), (x + 5.4, y - 4.4), (x + 5.4, y + 3.0), (x + 1.8, y + 4.4), (x - 1.8, y + 3.0), (x - 5.4, y + 4.4)]
    return (f'<polygon points="{S.pts(zig)}" fill="none" stroke="{c}" stroke-width="1.1" stroke-linejoin="round"/>'
            f'<line x1="{n(x - 1.8)}" y1="{n(y - 4.4)}" x2="{n(x - 1.8)}" y2="{n(y + 3.0)}" stroke="{c}" stroke-width="0.9"/><line x1="{n(x + 1.8)}" y1="{n(y - 3.0)}" x2="{n(x + 1.8)}" y2="{n(y + 4.4)}" stroke="{c}" stroke-width="0.9"/>')


def ic_cloud(x, y, c):
    return (f'<path d="M {n(x - 3.8)},{n(y + 3.2)} A 2.6,2.6 0 0 1 {n(x - 3.6)},{n(y - 1.9)} A 3.4,3.4 0 0 1 {n(x + 2.6)},{n(y - 2.6)} A 2.9,2.9 0 0 1 {n(x + 3.6)},{n(y + 3.2)} Z" '
            f'fill="none" stroke="{c}" stroke-width="1.2" stroke-linejoin="round"/>')


def ic_buoy(x, y, c):
    bands = "".join(f'<line x1="{n(x + 2.5 * math.cos(math.radians(a)))}" y1="{n(y + 2.5 * math.sin(math.radians(a)))}" x2="{n(x + 5.3 * math.cos(math.radians(a)))}" y2="{n(y + 5.3 * math.sin(math.radians(a)))}" '
                    f'stroke="#FFFFFF" stroke-width="1.5"/>' for a in (45, 135, 225, 315))
    return f'<circle cx="{n(x)}" cy="{n(y)}" r="3.9" fill="none" stroke="{c}" stroke-width="2.6"/>' + bands


def ic_eye(x, y, c):
    return (f'<path d="M {n(x - 5.6)},{n(y)} Q {n(x)},{n(y - 5.4)} {n(x + 5.6)},{n(y)} Q {n(x)},{n(y + 5.4)} {n(x - 5.6)},{n(y)} Z" fill="none" stroke="{c}" stroke-width="1.1" stroke-linejoin="round"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="1.9" fill="{c}"/>')


def ic_code(x, y, c):
    """A transponder's window: four small digits' places in a box."""
    return (f'<rect x="{n(x - 5.2)}" y="{n(y - 3.0)}" width="10.4" height="6.0" rx="1.2" fill="none" stroke="{c}" stroke-width="1.1"/>'
            + "".join(f'<rect x="{n(x - 4.0 + i * 2.2)}" y="{n(y - 1.6)}" width="1.4" height="3.2" fill="{c}"/>' for i in range(4)))


def ic_altimeter(x, y, c):
    ticks = "".join(f'<line x1="{n(x + 3.6 * math.sin(math.radians(a)))}" y1="{n(y - 3.6 * math.cos(math.radians(a)))}" x2="{n(x + 4.8 * math.sin(math.radians(a)))}" y2="{n(y - 4.8 * math.cos(math.radians(a)))}" '
                    f'stroke="{c}" stroke-width="0.8"/>' for a in range(0, 360, 36))
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="5.0" fill="none" stroke="{c}" stroke-width="1.1"/>' + ticks
            + f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(x + 2.2)}" y2="{n(y - 2.9)}" stroke="{c}" stroke-width="1.2" stroke-linecap="round"/><circle cx="{n(x)}" cy="{n(y)}" r="0.9" fill="{c}"/>')


def ic_form(x, y, c):
    return (f'<rect x="{n(x - 4.6)}" y="{n(y - 4.4)}" width="9.2" height="8.8" rx="0.8" fill="none" stroke="{c}" stroke-width="1.1"/>'
            + "".join(f'<line x1="{n(x - 4.6)}" y1="{n(y + dy)}" x2="{n(x + 4.6)}" y2="{n(y + dy)}" stroke="{c}" stroke-width="0.8"/>' for dy in (-1.5, 1.4))
            + f'<line x1="{n(x - 1.4)}" y1="{n(y - 4.4)}" x2="{n(x - 1.4)}" y2="{n(y - 1.5)}" stroke="{c}" stroke-width="0.8"/><line x1="{n(x + 1.6)}" y1="{n(y - 1.5)}" x2="{n(x + 1.6)}" y2="{n(y + 1.4)}" stroke="{c}" stroke-width="0.8"/>')


def ic_list(x, y, c):
    return "".join(f'<circle cx="{n(x - 4.0)}" cy="{n(y + dy)}" r="0.9" fill="{c}"/><line x1="{n(x - 1.8)}" y1="{n(y + dy)}" x2="{n(x + 4.8)}" y2="{n(y + dy)}" stroke="{c}" stroke-width="1.1" stroke-linecap="round"/>' for dy in (-3.0, 0.0, 3.0))


def ic_pin(x, y, c):
    return (f'<path d="M {n(x)},{n(y + 5.2)} Q {n(x - 4.4)},{n(y - 0.2)} {n(x - 3.4)},{n(y - 2.4)} A 3.5,3.5 0 0 1 {n(x + 3.4)},{n(y - 2.4)} Q {n(x + 4.4)},{n(y - 0.2)} {n(x)},{n(y + 5.2)} Z" fill="{c}"/>'
            f'<circle cx="{n(x)}" cy="{n(y - 1.9)}" r="1.4" fill="#FFFFFF"/>')


def ic_distance(x, y, c):
    return (f'<rect x="{n(x - 5.0)}" y="{n(y - 3.4)}" width="10.0" height="2.6" fill="{c}"/>'
            f'<line x1="{n(x - 4.2)}" y1="{n(y + 2.4)}" x2="{n(x + 4.2)}" y2="{n(y + 2.4)}" stroke="{c}" stroke-width="1.0"/>'
            f'<polygon points="{S.pts([(x - 5.4, y + 2.4), (x - 3.2, y + 0.9), (x - 3.2, y + 3.9)])}" fill="{c}"/><polygon points="{S.pts([(x + 5.4, y + 2.4), (x + 3.2, y + 0.9), (x + 3.2, y + 3.9)])}" fill="{c}"/>')


def ic_papi(x, y, c):
    return "".join(f'<circle cx="{n(x - 4.2 + i * 2.8)}" cy="{n(y)}" r="1.15" fill="{"#FFFFFF" if i < 2 else "#DC2626"}" stroke="{c if i < 2 else "#DC2626"}" stroke-width="0.7"/>' for i in range(4))


def ic_station(x, y, c):
    hexa = [(x + 4.4 * math.cos(math.radians(a)), y + 4.4 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    return f'<polygon points="{S.pts(hexa)}" fill="none" stroke="{c}" stroke-width="1.1" stroke-linejoin="round" stroke-dasharray="1.8 1.3"/><circle cx="{n(x)}" cy="{n(y)}" r="0.9" fill="{c}"/>'


ROWS = {
    "GEN": [("GEN 2.1", ic_clock, "UTC · NM · ft · hPa"), ("GEN 2.2", ic_book, "TORA · LDA · SWY"), ("GEN 2.7", ic_sun, "SR · SS"), ("GEN 3.1", ic_page, "AMDT · SUP · NOTAM"),
            ("GEN 3.2", ic_chart, "1:500 000"), ("GEN 3.5", ic_cloud, "MET"), ("GEN 3.6", ic_buoy, "SAR · 406 MHz")],
    "ENR": [("ENR 1.1", "megaphone", "TIBA 122.8"), ("ENR 1.2", ic_eye, "VFR"), ("ENR 1.4", "classes", ""), ("ENR 1.6", ic_code, "7700 · 7600 · 7500"),
            ("ENR 1.7", ic_altimeter, "QNH · 13 000 ft"), ("ENR 1.10", ic_form, "FPL"), ("ENR 6", ic_chart, "2546-C")],
    "AD": [("AD 1.3", ic_list, "OETH · NTL · VFR"), ("AD 2.2", ic_pin, "1 870 ft · 42 °C"), ("AD 2.3", ic_clock, "0500–1200 UTC"), ("AD 2.13", ic_distance, "TORA 4 000 m"),
           ("AD 2.14", ic_papi, "PAPI 3°"), ("AD 2.19", ic_station, "NIL"), ("AD 2.24", ic_chart, "ICAO")],
}
TAG_COL = 55.0                                        # the tags of a card end here (from its left edge): the icons stand in a column after them


def rows(part):
    x0, w = CARDS[part]
    out = []
    for i, (code, icon, words) in enumerate(ROWS[part]):
        y = ROW_Y + ROW_STEP * i
        if i:
            out.append(f'<line x1="{n(x0 + 9)}" y1="{n(y - ROW_STEP / 2)}" x2="{n(x0 + w - 9)}" y2="{n(y - ROW_STEP / 2)}" stroke="{PART[part]}" stroke-opacity="0.16" stroke-width="0.7"/>')
        out.append(tag(code, x0 + TAG_COL, y, "end"))
        ix = x0 + TAG_COL + 15.0
        if icon == "megaphone":
            out.append(H.megaphone(U, ix, y, 8.0, PART[part]))
        elif icon == "classes":
            out.append("".join(H.class_disc(U, ix + j * 14.0, y, letter, 5.6) for j, letter in enumerate("CDG")))
        else:
            out.append(_badge(ix, y, part) + icon(ix, y, PART[part]))
        if words:
            out.append(B.label(ix + 13.0, y + 2.5, words, 6.9, "start", colour="#334155", halo=False))
    return "".join(out)


# ----------------------------------------------------------------------------------------------------- callouts
def callouts():
    c = S.callout
    out = []
    for k, part in enumerate(("GEN", "ENR", "AD"), start=1):
        x, w = CARDS[part]
        out.append(c(k, x + w - 16.0, TOP + HEAD / 2, x + w - 16.0, TOP + HEAD / 2, r=8.6))
    zx, zy, zw, zh = GEN_ZOOM                                                                                   # the frame on the map of the State and the wedge to the next map
    mid = ((zx + zw + EX) / 2, (zy + EY + 2.0) / 2 + 3.0)
    out.append(c(4, mid[0] - 6.0, mid[1] - 17.0, mid[0], mid[1] - 3.0, r=8.6))
    t = (CTR_TAG[0] + tag_w("AD 2.17"), CTR_TAG[1])                                                            # the right end of the tag on the control zone
    out.append(c(5, E_K[0] + 45.0, E_K[1] - 8.0, t[0] + 1.0, t[1] + 1.0, r=8.6))
    return "".join(out)


def layers():
    out = [H.defs(U, W, HT), background()]
    out += [card(p) for p in ("GEN", "ENR", "AD")]
    out += ground("GEN", "terrain-04-01-gen") + [gen_map(), window_frame("GEN")]
    out += ground("ENR", "terrain-04-01-enr") + [enr_map(), window_frame("ENR")]
    out += ground("AD", "terrain-04-01-ad") + [ad_map(), window_frame("AD")]
    out += [zoom(GEN_ZOOM, window("ENR"), "ENR"), zoom(ENR_ZOOM, window("AD"), "AD")]
    out += [enr_tags(), ad_tags()]
    out.append(mini_scale(GX + 9.0, GY + GH - 20.0, 500 * AR.NM * S_GEN, "500 NM") + mini_scale(EX + 9.0, EY + 16.0, 10 * S_ENR, "10 NM") + mini_scale(AX + AW - 2 * S_AD - 12.0, AY + AH - 8.0, 2 * S_AD, "2 NM"))
    out.append(mini_north(EX + EW - 11.0, EY + EH - 13.0) + mini_north(AX + AW - 11.0, AY + 17.0))
    out += [rows(p) for p in ("GEN", "ENR", "AD")]
    out.append(callouts())
    return out


def plate():
    return {
        "id": "fig-04-01-aip-three-parts",
        "replaces": "fig-04-01-aip-three-parts.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-04-01-aip-three-parts.jpg",
        "caption": "Figure 4-1. Where to look in the AIP: its three parts, each closer than the one before, and the sections a VFR pilot opens for a flight at Thumamah",
        "desc": ("Figure 4-1. Where to look in the AIP: its three parts, each closer than the one before, and the sections a VFR pilot opens for a flight at Thumamah. Every tag is a section number "
                 "of AIP-KSA, AMDT 11/26. The grounds are open data (Natural Earth, NASA SRTM, and a Copernicus Sentinel-2 picture: contains modified Copernicus Sentinel data 2026); not for navigation."),
        "legend": [
            "Part 1, General (GEN): what holds for the whole State. Its tables and codes are in GEN 2 and its services in GEN 3.",
            "Part 2, En route (ENR): the rules of the air in ENR 1, and the airspace between aerodromes; here the country round Riyadh, with the terminal control area, the danger and restricted areas nearest to Thumamah and the DVOR/DME `KSA`.",
            "Part 3, Aerodromes (AD): one entry for each aerodrome, always under the same numbers; here Thumamah's, AD 2 OETH.",
            "Each part looks closer than the one before: the frame on a map is the whole of the next map.",
            "A control zone or an aerodrome traffic zone is not in Part 2: it is printed in AD 2.17 of its aerodrome, as this tag on the Riyadh control zone shows by its colour.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
