"""Figure 17-2 (new: the book says it in words only). One airspace, two classes: the control zone of Red Sea International (OERS) inside and outside the hours of its tower.

The same map twice, side by side, true north up, 12.9 canvas units to the NM, on an open satellite picture of the coast (Copernicus Sentinel-2, 20 m to the pixel;
figs/imagery_real.py; "Contains modified Copernicus Sentinel data 2026"). Everything drawn over it is the AIP's (AD 2 OERS, AMDT 11/26; data/saudi_airspace.json):
  the zone           AD 2.17: a clockwise arc of 10 NM round the reference point between two points, closed by the straight line between them (so the western part of the circle is
                     cut off), SFC to 2 500 ft AMSL, Class D, Red Sea Tower, hours 07:00-15:00; "CTR is considered ATZ outside hours of applicability with Airspace classification G"
  the frequencies    AD 2.18: Red Sea Tower 118.200 MHz, 0700-1500; TIBA 122.800 MHz, H24, "to be applied H24 outside Red Sea CTR/ATZ"; AD 2.22.1.2: TIBA on 122.8 MHz in Class G
                     airspace, among others "within uncontrolled aerodrome in non-TWR operating hours"
  the points         AD 2.22.12: entry and exit by the visual reporting points A to G, at their printed coordinates
  the runway         15L/33R (the parallel 15R/33L is closed and is not drawn)
On the left the hours of the tower (the zone blue, Class D, the tower and its frequency); on the right the rest of the day (the same outline green and dashed, Class G, the
broadcasts inside it, the picture a little darker). The AIP prints the hours without a time system; the book reads them as UTC and says so (its open item OI-022).
Letters: hours, frequencies, class letters and the letters of the points; the rest is numbered."""
import math

from figs import h_b2 as H
from figs import h_b4 as B
from figs import imagery_real as IR
from figs import scene as S

W, HT = 640, 362
U = "rs2"
SCALE = 12.9                                         # canvas units to the NM
OERS = H.DATA["oers"]
ARP_LL = (OERS["arp"]["lat"], OERS["arp"]["lon"])
PW, PH = 306.0, 346.0                                # one panel
PANELS = ((8.0, 8.0), (326.0, 8.0))                  # the top left corner of the left and of the right panel
LOCAL = H.Frame(ARP_LL[0], ARP_LL[1], SCALE, PW / 2, PH / 2 + 6.0)       # the map inside a panel, from the panel's own corner
assert IR.covers(LOCAL, (PW, PH), picture="oers_area_s2"), "the satellite picture does not cover the map"
IR.ensure("terrain-17-02-coast", LOCAL, (PW, PH), veil=0.1, saturation=0.95, lift=1.03, picture="oers_area_s2")
FRAMES = [H.Frame(ARP_LL[0], ARP_LL[1], SCALE, x + LOCAL.ox, y + LOCAL.oy) for x, y in PANELS]
HOURS = OERS["ctr"]["hours_utc"]                     # "07:00-15:00", as AD 2.17 prints it
OPEN, SHUT = HOURS.split("-")
TOWER_MHZ = f'{OERS["comms"]["tower"]["mhz"]:.3f}'
TIBA_MHZ = f'{OERS["comms"]["tiba"]["mhz"]:.1f}'
NIGHT = "#0B1B3A"


def zone(f):
    return H.poly(f.ring(OERS["ctr"]["ring"]))


def runway(f):
    a, b = (next(r for r in OERS["runways"] if r["id"] == rid)["threshold"] for rid in ("15L", "33R"))
    return f.xy(a["lon"], a["lat"]), f.xy(b["lon"], b["lat"])


def panel_ground(i):
    x, y = PANELS[i]
    return {"name": "terrain-17-02-coast", "at": [x + PW / 2, y + PH / 2], "width": PW}


def dusk(i):
    """Outside the hours of the tower the day is ending or has not begun: the picture of the right panel a little darker (the lines over it keep their colours)."""
    x, y = PANELS[i]
    return f'<rect x="{S.n(x)}" y="{S.n(y)}" width="{S.n(PW)}" height="{S.n(PH)}" fill="{NIGHT}" opacity="0.36"/>' if i == 1 else ""


def panel_frame(i):
    x, y = PANELS[i]
    return f'<rect x="{S.n(x + 0.6)}" y="{S.n(y + 0.6)}" width="{S.n(PW - 1.2)}" height="{S.n(PH - 1.2)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.2"/>'


def clock(i):
    """The hours of the panel: a small 24 hour dial with its share of the day lit, and the hours beside it on a dark plate."""
    x, y = PANELS[i]
    cx, cy, r = x + 25.0, y + 25.0, 13.5
    h0, h1 = (int(OPEN[:2]), int(SHUT[:2])) if i == 0 else (int(SHUT[:2]), int(OPEN[:2]) + 24)
    colour = H.COL["D"] if i == 0 else H.COL["G"]
    a0, a1 = h0 / 24 * 360, h1 / 24 * 360                                   # midnight at the top, the day runs clockwise
    arc = [(cx + r * math.sin(math.radians(a0 + (a1 - a0) * k / 40)), cy - r * math.cos(math.radians(a0 + (a1 - a0) * k / 40))) for k in range(41)]
    text = f"{OPEN}–{SHUT} UTC" if i == 0 else f"{SHUT}–{OPEN} UTC"
    wide = 118.0
    out = [f'<rect x="{S.n(x + 6)}" y="{S.n(y + 6)}" width="{S.n(wide + 38)}" height="38" rx="19" fill="#101B33" fill-opacity="0.82" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.8" filter="url(#{U}ds)"/>',
           f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{S.n(r)}" fill="#F7FAFF" stroke="#FFFFFF" stroke-width="1"/>',
           f'<polygon points="{S.pts([(cx, cy)] + arc)}" fill="{colour}" fill-opacity="0.9"/>']
    for hour in range(0, 24, 3):                                            # a tick every three hours
        a = math.radians(hour / 24 * 360)
        r0 = r - (3.6 if hour % 6 == 0 else 2.2)
        out.append(f'<line x1="{S.n(cx + r0 * math.sin(a))}" y1="{S.n(cy - r0 * math.cos(a))}" x2="{S.n(cx + r * math.sin(a))}" y2="{S.n(cy - r * math.cos(a))}" stroke="#101B33" stroke-width="0.8"/>')
    out.append(f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="{S.n(r)}" fill="none" stroke="#101B33" stroke-width="1"/><circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="1.5" fill="#101B33"/>')
    out.append(H.glyph_text(text, x + 46.0, cy, 8.6, "#FFFFFF", spacing=0.5, anchor="start"))
    return "".join(out)


def airspace(i):
    f = FRAMES[i]
    z = zone(f)
    cls = "D" if i == 0 else "G"
    out = [H.fill(z, cls, opacity=0.26 if i == 0 else 0.2), H.inner_glow(U + str(i), z, cls, width=10.0, opacity=0.32)]
    if i == 0:
        out.append(H.edge(z, cls, dash="none", width=2.2, casing=4.6, uid=U))
    else:
        out.append(H.edge(z, cls, dash="7 4.5", width=2.0, casing=4.4, uid=U, colour="#2FA36B"))
    return "".join(out)


def places(i):
    f = FRAMES[i]
    p0, p1 = runway(f)
    out = [H.runway(U, p0, p1, 2.4)]
    for v in OERS["vrps"]:
        x, y = f.xy(v["lon"], v["lat"])
        dx, dy = LETTER_AT[v["id"]]
        out.append(H.vrp(U, x, y, 9.5) + H.label(v["id"], x + dx, y + dy, 7.4, H.INK, spacing=0))
    return "".join(out)


LETTER_AT = {"A": (-9.5, -3.0), "B": (-9.5, 1.0), "C": (9.5, 5.0), "D": (-9.5, 3.0), "E": (10.0, 3.0), "F": (9.5, 5.0), "G": (10.0, -2.0)}       # where the letter of each point stands, from the point


def services(i):
    """Whose airspace it is: the class, and the voice a pilot hears or makes."""
    f = FRAMES[i]
    arp = f.xy(ARP_LL[1], ARP_LL[0])
    out = []
    disc = (arp[0] + 40.0, arp[1] - 74.0)
    out.append(H.class_disc(U, disc[0], disc[1], "D" if i == 0 else "G", 10.5))
    out.append(B.label(disc[0] + 15.0, disc[1] + 3.6, "≤ 2 500 ft", 9.4, "start"))
    voice = (arp[0] + 47.0, arp[1] + 44.0)
    if i == 0:
        out.append(H.tower_icon(U, voice[0], voice[1], 11.5))
        out.append(B.label(voice[0] + 15.0, voice[1] + 3.6, TOWER_MHZ, 9.6, "start", colour="#16438A"))
    else:
        out.append(H.megaphone(U, voice[0], voice[1], 11.0))
        out.append(B.label(voice[0] + 15.0, voice[1] + 3.6, TIBA_MHZ, 9.6, "start", colour="#145C39"))
    sea = OUTSIDE[i]                                                        # outside the zone the broadcasts go on at all hours
    out.append(H.megaphone(U, sea[0], sea[1], 9.6))
    out.append(B.label(sea[0] + 13.0, sea[1] + 3.4, TIBA_MHZ, 8.8, "start", colour="#145C39"))
    return "".join(out)


OUTSIDE = [(PANELS[0][0] + 30.0, PANELS[0][1] + 318.0), (PANELS[1][0] + 30.0, PANELS[1][1] + 318.0)]


def furniture():
    x, y = PANELS[1]
    return H.north_arrow(U, x + PW - 22.0, y + 36.0, 26.0) + H.scale_bar(U, x + PW - 108.0, y + PH - 22.0, 5 * SCALE, nm_total=5, segments=5, text="5 NM")


def rim(centre, toward, r):
    d = H.dist(centre, toward)
    return (centre[0] + (toward[0] - centre[0]) / d * r, centre[1] + (toward[1] - centre[1]) / d * r)


def callouts():
    c = S.callout
    f0, f1 = FRAMES
    arp0, arp1 = f0.xy(ARP_LL[1], ARP_LL[0]), f1.xy(ARP_LL[1], ARP_LL[0])
    out = []
    edge0 = f0.bearing_point(arp0, 118.0, 10.0)
    out.append(c(1, 292.0, 250.0, edge0[0], edge0[1], r=10))                                           # the boundary
    d0 = (arp0[0] + 40.0, arp0[1] - 74.0)
    out.append(c(2, d0[0] - 34.0, d0[1] - 26.0, *rim(d0, (d0[0] - 34.0, d0[1] - 26.0), 10.5), r=10))   # Class D in the hours of the tower
    v0 = (arp0[0] + 47.0, arp0[1] + 44.0)
    out.append(c(3, v0[0] + 6.0, v0[1] + 36.0, *rim(v0, (v0[0] + 6.0, v0[1] + 36.0), 11.5), r=10))     # the tower
    e = next(v for v in OERS["vrps"] if v["id"] == "E")
    ex, ey = f0.xy(e["lon"], e["lat"])
    out.append(c(4, ex - 36.0, ey + 20.0, ex - 5.0, ey + 2.6, r=10))                                   # the reporting points
    p0, p1 = runway(f0)
    mid = H.lerp(p0, p1, 0.35)
    out.append(c(5, mid[0] - 40.0, mid[1] - 22.0, mid[0] - 2.0, mid[1] - 1.0, r=10))                   # the runway
    d1 = (arp1[0] + 40.0, arp1[1] - 74.0)
    out.append(c(6, d1[0] - 34.0, d1[1] - 26.0, *rim(d1, (d1[0] - 34.0, d1[1] - 26.0), 10.5), r=10))   # Class G outside the hours
    v1 = (arp1[0] + 47.0, arp1[1] + 44.0)
    out.append(c(7, v1[0] + 6.0, v1[1] + 36.0, *rim(v1, (v1[0] + 6.0, v1[1] + 36.0), 11.0), r=10))     # the broadcasts inside
    s0 = OUTSIDE[0]
    out.append(c(8, s0[0] + 20.0, s0[1] - 30.0, *rim(s0, (s0[0] + 20.0, s0[1] - 30.0), 9.6), r=10))    # the broadcasts outside, at all hours
    return "".join(out)


def layers():
    out = [H.defs(U, W, HT), f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#EEF2F7"/>']
    for i in (0, 1):
        out += [panel_ground(i), dusk(i), airspace(i), places(i), panel_frame(i), services(i), clock(i)]
    out += [furniture(), callouts()]
    return out


def plate():
    return {
        "id": "fig-17-02-class-by-the-clock",
        "replaces": "fig-17-02-class-by-the-clock.svg",        # nothing: the book had no such figure (the name only keeps the rule that it starts with the id)
        "book_file": "plate-17-02-class-by-the-clock.jpg",
        "caption": "Figure 17-2. One airspace, two classes: the Red Sea control zone inside and outside the hours of its tower",
        "desc": ("Figure 17-2. One airspace, two classes: the Red Sea control zone inside and outside the hours of its tower. North is up. The zone, the hours, the frequencies and the reporting points "
                 "are the AIP's (AD 2 OERS, AMDT 11/26). The ground is an open satellite picture (contains modified Copernicus Sentinel data 2026); not for navigation."),
        "legend": [
            "The boundary of the zone, the same at all hours: a circle of 10 NM round the aerodrome reference point with its western part cut off along a straight line, from the surface to 2 500 ft AMSL.",
            "From 07:00 to 15:00 UTC, while Red Sea Tower is open: a control zone of Class D.",
            "Red Sea Tower, 118.200 MHz: in radio contact before the boundary, and inside only as the reply allows.",
            "The visual reporting points A to G: entry to the zone and exit from it are by them.",
            "Runway 15L/33R.",
            "Outside those hours: the same airspace is an aerodrome traffic zone of Class G, with no tower and no clearance.",
            "Inside it every aircraft then broadcasts its position and intentions on 122.8 MHz, the TIBA procedure.",
            "Outside the zone the TIBA procedure applies at all hours.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"blank": True, "layers": layers()},
    }
