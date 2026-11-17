"""Figure 21-5 (new: the chapter's fixes were all at an invented station). A fix from one station: the two reporting points of Thumamah, as the AIP places them from the Riyadh DVOR/DME.

The AIP itself fixes Thumamah's two visual reporting points by a radial and a DME distance (AD 2 OETH 2.22.3, AMDT 11/26):
    Thumamah North VRP   RDL 358 from KSA 18.83 NM   251742.6N 0464022.0E
    Thumamah East VRP    RDL 025 from KSA 15.82 NM   251250.0N 0464820.0E
and AD 2 OERK 2.19 prints the station: DVOR/DME KSA, 115.000 MHZ (CH97X), declination 03° E, H24, 245849.2N 0464008.1E. data/build_saudi_facts.py holds all of it as printed and
asserts that the printed radials and distances agree with the printed coordinates (357.6° and 024.9° magnetic, 18.90 and 15.87 NM).

The map: true north up, 16.4 canvas units to the NM, an equirectangular frame round the station, on a shaded relief of the real country (NASA SRTM, public domain; figs/terrain_real.py).
The station stands where the AIP puts it, with a compass rose aligned to magnetic north (3° east of true north, so the radials lie 3° clockwise of their numbers on the page). The two
radials are drawn through the reporting points' printed coordinates and carry the AIP's numbers; the arc is the circle of 15.82 NM round the station. For the rest: Thumamah's runway
and its ATZ (Class G), the runways of King Khaled International and the northern part of the Riyadh control zone (Class D), as in Figure 17-9.

The card: what the two instruments show over the East VRP. A VOR indicator with the OBS on 025, FROM, the needle centred, and a DME readout of 15.8 NM (the slant range from 3 500 ft
AMSL to an antenna at 2 100 ft is longer than the ground distance by 0.002 NM). No aeroplane is drawn on the map: it would hide the point. Letters: identifiers, frequencies, radials, distances with their unit, class letters, FR; the rest is numbered."""
import math

from figs import h_a4 as A
from figs import h_b2 as H
from figs import h_b4 as B
from figs import scene as S
from figs import terrain_real as TR

n = S.n
W, HT = 640, 434
U = "fx5"
SCALE = 16.4                                         # canvas units to the NM
OETH, OERK = H.DATA["oeth"], H.DATA["oerk"]
KSA = OERK["ksa"]
NORTH, EAST = OETH["vrps"]
assert (KSA["id"], KSA["mhz"], KSA["declination_e_deg"]) == ("KSA", 115.0, 3)
assert (NORTH["from_ksa_printed"], EAST["from_ksa_printed"]) == ({"radial": 358, "nm": 18.83}, {"radial": 25, "nm": 15.82})
DECL = KSA["declination_e_deg"]
F = H.Frame(KSA["lat"], KSA["lon"], SCALE, 232.0, 366.0)                 # the station lies at (232, 366): the map shows 22 NM to the north of it and 25 to the east
TR.ensure("terrain-21-05-relief", F, (W, HT), veil=0.30, soft=1.0, exaggeration=9.0)
STN = F.xy(KSA["lon"], KSA["lat"])
NV, EV = F.xy(NORTH["lon"], NORTH["lat"]), F.xy(EAST["lon"], EAST["lat"])
T = F.xy(OETH["arp"]["lon"], OETH["arp"]["lat"])
K = F.xy(OERK["arp"]["lon"], OERK["arp"]["lat"])
ATZ = H.circle(T[0], T[1], F.r(OETH["atz"]["radius_nm"]))
CTR = H.circle(K[0], K[1], F.r(OERK["ctr"]["radius_nm"]))
RAY, RAY_HI = "#1B4FD0", "#8FB4FF"                    # the radials
ARC = "#B45309"                                      # the DME distance
ROSE_R = 30.0


def polar(true_deg, r):
    """A canvas point `r` units from the station on a true bearing."""
    a = math.radians(true_deg)
    return (STN[0] + r * math.sin(a), STN[1] - r * math.cos(a))


def true_of(p):
    return math.degrees(math.atan2(p[0] - STN[0], STN[1] - p[1])) % 360


N_TRUE, E_TRUE = true_of(NV), true_of(EV)            # the two radials as they lie on the page
N_R, E_R = H.dist(STN, NV), H.dist(STN, EV)
assert abs((N_TRUE - DECL - 358 + 180) % 360 - 180) < 0.6 and abs(E_TRUE - DECL - 25) < 0.6
assert abs(N_R / SCALE - 18.83) < 0.1 and abs(E_R / SCALE - 15.82) < 0.1


def thr(airport, rid):
    rw = next(r for r in airport["runways"] if r["id"] == rid)
    return F.xy(rw["threshold"]["lon"], rw["threshold"]["lat"])


def ground():
    return {"name": "terrain-21-05-relief", "at": [W / 2, HT / 2], "width": W}


def airspace():
    return (H.fill(CTR, "D", opacity=0.13) + H.edge(CTR, "D", dash="8 4.5", width=1.7, uid=U) + H.fill(ATZ, "G", opacity=0.13) + H.edge(ATZ, "G", dash="8 4.5", width=1.7, uid=U)
            + H.class_disc(U, T[0] - 58.0, T[1] + 44.0, "G", 7.4) + H.class_disc(U, K[0] + 96.0, K[1] - 118.0, "D", 7.4))


def aerodromes():
    out = [H.runway(U, thr(OETH, "17"), thr(OETH, "35"), 3.0)]
    out += [H.runway(U, thr(OERK, a), thr(OERK, b), 2.8) for a, b in (("15L", "33R"), ("15R", "33L"))]
    out.append(H.label("OETH", T[0] - 9.0, T[1] + 2.0, 5.2, H.INK, anchor="end", spacing=0.3))
    out.append(H.label("OERK", K[0] + 20.0, K[1] + 6.0, 5.2, H.INK, anchor="start", spacing=0.3))
    return "".join(out)


def rose():
    """The compass rose of the station: a ring with a tick every 10 degrees, turned to magnetic north."""
    out = [f'<circle cx="{n(STN[0])}" cy="{n(STN[1])}" r="{n(ROSE_R)}" fill="#FFFFFF" fill-opacity="0.16" stroke="#FFFFFF" stroke-width="3.0" stroke-opacity="0.85"/>',
           f'<circle cx="{n(STN[0])}" cy="{n(STN[1])}" r="{n(ROSE_R)}" fill="none" stroke="{RAY}" stroke-width="1.2"/>']
    for a in range(0, 360, 10):
        long = a % 30 == 0
        p0, p1 = polar(a + DECL, ROSE_R - (5.2 if long else 2.8)), polar(a + DECL, ROSE_R)
        out.append(f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="{RAY}" stroke-width="{1.2 if long else 0.7}"/>')
    tip, a0, a1 = polar(DECL, ROSE_R + 8.5), polar(DECL - 7.0, ROSE_R + 1.0), polar(DECL + 7.0, ROSE_R + 1.0)                 # the mark of magnetic north
    out.append(f'<polygon points="{S.pts([tip, a0, a1])}" fill="{RAY}" stroke="#FFFFFF" stroke-width="1.0" stroke-linejoin="round"/>')
    return "".join(out)


def ray(true_deg, r):
    p0, p1 = polar(true_deg, ROSE_R), polar(true_deg, r)
    return (f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="4.4" stroke-linecap="round" filter="url(#{U}ds)"/>'
            f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="{RAY}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<line x1="{n(p0[0])}" y1="{n(p0[1])}" x2="{n(p1[0])}" y2="{n(p1[1])}" stroke="{RAY_HI}" stroke-width="0.7" stroke-linecap="round"/>')


def pill(x, y, s, colour, size=6.6, w=None):
    """A number on a white pill, to be read on the relief."""
    w = w or (len(s) * size * 0.66 + 9.0)
    return (f'<rect x="{n(x - w / 2)}" y="{n(y - size * 0.95)}" width="{n(w)}" height="{n(size * 1.9)}" rx="{n(size * 0.95)}" fill="#FFFFFF" fill-opacity="0.94" stroke="{colour}" stroke-width="1.0" filter="url(#{U}ds)"/>'
            + B.label(x, y + size * 0.36, s, size * 1.12, "middle", colour=colour, halo=False))


def radials():
    out = [ray(N_TRUE, N_R + 16.0), ray(E_TRUE, E_R + 26.0)]
    # the circle of 15.82 NM: the part of it either side of the East VRP
    a0, a1 = math.radians(E_TRUE - 15.0), math.radians(E_TRUE + 13.0)
    arc = [(STN[0] + E_R * math.sin(a0 + (a1 - a0) * i / 40), STN[1] - E_R * math.cos(a0 + (a1 - a0) * i / 40)) for i in range(41)]
    out.append(f'<polyline points="{S.pts(arc)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.8" stroke-linecap="round"/>'
               f'<polyline points="{S.pts(arc)}" fill="none" stroke="{ARC}" stroke-width="1.8" stroke-dasharray="6 3.4" stroke-linecap="round"/>')
    return "".join(out)


def labels():
    out = []
    p = polar(N_TRUE, N_R * 0.34)
    out.append(pill(p[0], p[1], "358", RAY))
    p = polar(E_TRUE, E_R * 0.36)
    out.append(pill(p[0], p[1], "025", RAY))
    p = polar(N_TRUE, N_R * 0.69)
    out.append(pill(p[0] + 28.0, p[1], "18.83 NM", ARC, w=46.0))
    p = polar(E_TRUE, E_R * 0.72)
    out.append(pill(p[0] + 28.0, p[1] + 9.0, "15.82 NM", ARC, w=46.0))
    out.append(H.label("KSA", STN[0] - 26.0, STN[1] + 45.0, 5.6, RAY, anchor="middle", spacing=0.4) + pill(STN[0] + 14.0, STN[1] + 45.0, "115.000", RAY, size=6.0, w=40.0))
    return "".join(out)


def points():
    return H.vrp(U, NV[0], NV[1], 11.5) + H.vrp(U, EV[0], EV[1], 11.5)


# ----------------------------------------------------------------------------------------------------- the card: the instruments over the East VRP
CX, CY, CW, CH = 458.0, 142.0, 170.0, 240.0
VOR = (CX + CW / 2, CY + 86.0)                       # the middle of the VOR indicator
VK = 0.92                                            # its size against the one of Figure 21-9


def vor_indicator():
    cx, cy = VOR
    g = lambda v: n(v * VK)
    out = [f'<defs><radialGradient id="{U}bz" cx="0.35" cy="0.3" r="0.9"><stop offset="0" stop-color="#4A5468"/><stop offset="1" stop-color="#0B101C"/></radialGradient>'
           f'<radialGradient id="{U}fc" cx="0.4" cy="0.35" r="0.85"><stop offset="0" stop-color="#262F42"/><stop offset="1" stop-color="#0E1424"/></radialGradient>'
           f'<radialGradient id="{U}kn" cx="0.35" cy="0.3" r="0.9"><stop offset="0" stop-color="#F4F6FA"/><stop offset="0.6" stop-color="#9AA5B8"/><stop offset="1" stop-color="#4A5468"/></radialGradient>'
           f'<filter id="{U}nd" x="-300%" y="-30%" width="700%" height="160%"><feGaussianBlur stdDeviation="2.0"/></filter></defs>',
           f'<g transform="translate({n(cx)} {n(cy)}) scale({VK})">',
           f'<circle cx="0" cy="0" r="68" fill="url(#{U}bz)" stroke="#8FA0BC" stroke-opacity="0.55" stroke-width="1"/>',
           f'<circle cx="0" cy="0" r="63" fill="url(#{U}fc)" stroke="#05080F" stroke-width="1.4"/>',
           '<path d="M -56,-24 A 61,61 0 0 1 -12,-59" fill="none" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="1.6" stroke-linecap="round"/>',
           '<rect x="-18" y="-58" width="36" height="17" rx="3" fill="#F4F6FA" stroke="#05080F" stroke-width="1"/>' + A.text(0, -45.2, "025", 12.5, "#111827", "bold", "middle") + '<polygon points="0,-33 -4.4,-40.4 4.4,-40.4" fill="#F4F6FA"/>']
    for i in range(-5, 6):
        out.append('<circle cx="0" cy="7.7" r="4.4" fill="none" stroke="#FFFFFF" stroke-width="1.3"/>' if i == 0 else f'<circle cx="{n(i * 8.3)}" cy="7.7" r="1.9" fill="#CBD5E6"/>')
    out.append(f'<rect x="-2.2" y="-31" width="4.4" height="54" rx="2.2" fill="#FFA43A" opacity="0.85" filter="url(#{U}nd)"/><rect x="-1.7" y="-31" width="3.4" height="54" rx="1.7" fill="#FFB347" stroke="#FFF1CF" stroke-opacity="0.8" stroke-width="0.5"/>')
    out.append('<rect x="-17" y="29" width="34" height="24" rx="3" fill="#F4F6FA" stroke="#05080F" stroke-width="1"/><polygon points="-6,47 -11,38 -1,38" fill="#111827"/>' + A.text(7, 45, "FR", 11, "#111827", "bold", "middle", mono=True))
    out.append(f'<circle cx="-48.5" cy="43.7" r="10.6" fill="#05080F" opacity="0.5"/><circle cx="-48.5" cy="43.7" r="9.6" fill="url(#{U}kn)" stroke="#2A3448" stroke-width="0.8"/>'
               + "".join(f'<line x1="{n(-48.5 + 6.2 * math.cos(math.radians(a)))}" y1="{n(43.7 + 6.2 * math.sin(math.radians(a)))}" x2="{n(-48.5 + 9.2 * math.cos(math.radians(a)))}" y2="{n(43.7 + 9.2 * math.sin(math.radians(a)))}" stroke="#3A4458" stroke-width="0.8"/>' for a in range(0, 360, 30)))
    out.append("</g>")
    return "".join(out)


DME = (CX + CW / 2, CY + 186.0)                      # the middle of the DME readout


def dme_readout():
    x, y = DME
    return (A.glass(U + "d", x - 56.0, y - 22.0, 112.0, 44.0, r=6, top="#101828", bottom="#05080F", opacity=1.0, shadow=False)
            + f'<defs><filter id="{U}dg" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="3"/></filter></defs>'
            + f'<text x="{n(x - 12.0)}" y="{n(y + 9.0)}" font-family="monospace" font-size="24" font-weight="bold" fill="#FFB52E" text-anchor="middle" filter="url(#{U}dg)" opacity="0.8">15.8</text>'
            + A.text(x - 12.0, y + 9.0, "15.8", 24, "#FFCF63", "bold", "middle", mono=True) + A.text(x + 36.0, y + 8.0, "NM", 10.5, "#8DBBFF", "bold", "middle", mono=True)
            + A.text(x, y + 38.0, "DME", 11, "#8DBBFF", "bold", "middle", mono=True))


def card():
    return A.glass(U + "k", CX, CY, CW, CH, r=12, top="#1F2E4B", bottom="#0C1527", opacity=0.97) + vor_indicator() + dme_readout()


def rim(centre, toward, r):
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


def callouts():
    c = S.callout
    out = [c(1, STN[0] - 62.0, STN[1] + 12.0, *rim(STN, (STN[0] - 62.0, STN[1] + 12.0), 13.0), r=10)]                     # the station
    p = polar(DECL + 62.0, ROSE_R)
    out.append(c(2, STN[0] + 62.0, STN[1] - 4.0, p[0], p[1], r=10))                                                           # the rose, turned to magnetic north
    p = polar(N_TRUE, N_R * 0.56)
    out.append(c(3, p[0] - 26.0, p[1], p[0] - 1.5, p[1], r=10))                                                               # the 358 radial
    out.append(c(4, NV[0] - 30.0, NV[1] - 2.0, *rim(NV, (NV[0] - 30.0, NV[1] - 2.0), 8.0), r=10))                         # the North VRP
    p = polar(E_TRUE, E_R * 0.54)
    out.append(c(5, p[0] + 23.0, p[1] + 13.0, p[0] + 1.2, p[1] + 0.8, r=10))                                                  # the 025 radial
    out.append(c(6, EV[0] + 30.0, EV[1] - 14.0, *rim(EV, (EV[0] + 30.0, EV[1] - 14.0), 8.0), r=10))                       # the East VRP
    a = math.radians(E_TRUE + 11.5)
    p = (STN[0] + E_R * math.sin(a), STN[1] - E_R * math.cos(a))
    out.append(c(7, p[0] + 22.0, p[1] + 18.0, p[0] + 1.0, p[1] + 1.0, r=10))                                                  # the circle of 15.82 NM
    out.append(c(8, CX + 18.0, CY + 20.0, VOR[0] - 44.0, VOR[1] - 44.0, r=10))                                               # the instruments
    out.append(c(9, T[0] - 44.0, T[1] - 52.0, *rim((T[0] - 6.0, T[1] - 6.0), (T[0] - 44.0, T[1] - 52.0), 4.0), r=10))     # Thumamah and its ATZ
    d = (K[0] + 96.0, K[1] - 118.0)
    out.append(c(10, d[0] + 30.0, d[1] + 6.0, *rim(d, (d[0] + 30.0, d[1] + 6.0), 7.6), r=10))                              # the Riyadh control zone
    return "".join(out)


def layers():
    return [H.defs(U, W, HT), ground(), H.vignette(U, W, HT, 0.12), airspace(), aerodromes(), radials(), rose(), A.vor_top(U + "s", STN[0], STN[1], 0.62, pad=False, shed=False),
            points(), labels(), card(), H.north_arrow(U, 612.0, 34.0, 26.0), H.scale_bar(U, 474.0, 410.0, 5 * SCALE, nm_total=5, segments=5, text="5 NM"), callouts()]


def plate():
    return {
        "id": "fig-21-05-fix-from-one-station",
        "replaces": "fig-21-05-fix-from-one-station.svg",       # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-21-05-fix-from-one-station.jpg",
        "caption": "Figure 21-5. A fix from one station: the two reporting points of Thumamah, as the AIP places them from the Riyadh VOR/DME",
        "desc": ("Figure 21-5. A fix from one station: the two reporting points of Thumamah, as the AIP places them from the Riyadh VOR/DME. True north is up; the station's compass rose is turned 3° to "
                 "the east, to magnetic north. The station, the radials and the distances are the AIP's (AD 2 OERK 2.19 and AD 2 OETH 2.22.3, AMDT 11/26); the ground is open elevation data (NASA SRTM); "
                 "not for navigation."),
        "legend": [
            "The DVOR/DME `KSA` at King Khaled International, 115.000 MHz.",
            "Its compass rose, aligned with magnetic north, which is 3° east of true north here (the declination AD 2.19 prints for the station): every radial lies 3° clockwise of its number on this map.",
            "The 358 radial.",
            "Thumamah North VRP: on the 358 radial, 18.83 NM from `KSA`.",
            "The 025 radial.",
            "Thumamah East VRP: on the 025 radial, 15.82 NM from `KSA`.",
            "A DME distance is a circle round the station: this arc is 15.82 NM from it, and it crosses the radial at the fix.",
            "The instruments over the East VRP: OBS 025, `FR`, the needle centred, and 15.8 NM on the DME.",
            "Thumamah and its ATZ.",
            "The Riyadh control zone, Class D.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
