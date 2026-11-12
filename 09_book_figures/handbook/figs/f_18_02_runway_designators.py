"""Figure 18-2. Naming a runway from its magnetic direction, drawn from the AIP data of the Saudi round (data/saudi_airspace.json, AMDT 11/26).

Left, Thumamah (OETH): a compass as a lit instrument ring (a dark bezel with its scale lit, a pane of frosted glass in it) over an aerial view of the desert, magnetic north up, with
runway 17/35 of asphalt along its direction, 168 degrees magnetic (171 true less the 3 degrees E variation of the file), its numbers painted at the ends; magnetic north is a lit blue arrow,
the angle clockwise from north an orange ribbon, the two landings (towards 168 and towards 348 degrees) dark ribbons that start at the twin's aeroplane (sprite-top) and end at the near end
where the number is read.
Right, Jeddah (OEJN): the three parallel runways at one scale on a north-up frame around the aerodrome reference point (x_nm = (lon - lon0) * 60 * cos(lat0), y_nm = (lat - lat0) * 60,
1 NM = 1852 m), each bar centred on the middle of its two thresholds in the file, along the file's true bearing (160 degrees), as long as the declared length (4 000, 4 000 and 3 800 m);
the paint carries the designators at both ends and two ribbons (with an aeroplane each) show the approaches to 16 and to 34; 1 km is 45 canvas units (1 NM, 83.3), with a scale bar of 1 NM and a north arrow.
The width of the bars is exaggerated (15 units, 5.5 times the 60 m of the file) so that the numbers can be read, and the aeroplanes are symbols; lengths and positions are true (the drawn ends
are within 7.3 m of the thresholds of the file). figs/h_b3.py has the projection, the numbers and the paint; figs/scene.py the ribbons and the callouts."""
import math

from figs import h_a2 as H
from figs import h_b3 as B
from figs import scene as S
from figs import terrain

W, HT = 640, 360
terrain.ensure("terrain-18-02", size=(W * 4, HT * 4), seed=182, kind="plain", features=("wadis", "tracks"), veil=0.32, soft=2.8)

U = "b182"
n = S.n
FACTS = B.facts()

# ------------------------------------------------------------------------------------------------------------------ the data
OETH = FACTS["oeth"]
RW_N = next(r for r in OETH["runways"] if r["id"] == "17")           # the end at the north: landing towards its direction you read 17
RW_S = next(r for r in OETH["runways"] if r["id"] == "35")
MAG_N = round(RW_N["magnetic_deg_derived"])                            # 168 (171 true less 3 E)
MAG_S = round(RW_S["magnetic_deg_derived"])                            # 348
assert (MAG_N, MAG_S) == (168, 348) and OETH["mag_var_e_deg"] == 3

OEJN = FACTS["oejn"]
FRAME = B.Frame(OEJN["arp"]["lat"], OEJN["arp"]["lon"])
PAIRS = (("16R", "34L"), ("16C", "34C"), ("16L", "34R"))              # from the west to the east
JED = []
for a_id, b_id in PAIRS:
    a = next(r for r in OEJN["runways"] if r["id"] == a_id)
    b = next(r for r in OEJN["runways"] if r["id"] == b_id)
    assert a["length_m"] == b["length_m"] and abs((a["true_deg"] + 180) % 360 - b["true_deg"]) < 1e-6
    pa, pb = FRAME.xy(a["threshold"]["lat"], a["threshold"]["lon"]), FRAME.xy(b["threshold"]["lat"], b["threshold"]["lon"])
    JED.append({"n_id": a_id, "s_id": b_id, "mid": ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2), "len": a["length_m"] / 1000.0, "brg": a["true_deg"]})
BRG = JED[0]["brg"]                                                    # 160: the direction of landing on 16 (true)
UX, UY = math.sin(math.radians(BRG)), math.cos(math.radians(BRG))      # east and north parts of the direction 160

# ------------------------------------------------------------------------------------------------------------------ the layout
CX, CY = 150.0, 188.0                    # the compass
R_IN, R_OUT = 102.0, 122.0
BAR_T = 20.0                             # the width of the runway in the compass (a symbol: the runway is far narrower than long)
HALF_T = 77.0
K = 45.0                                 # Jeddah: canvas units to a kilometre (1 unit = 22.2 m)
BAR_J = 15.0                             # the width of a Jeddah bar (60 m would be 2.8 units)
NUM_H = 8.8                              # the painted numbers at Jeddah
NUM_T = 11.5                             # and at Thumamah, where the numbers are the point
PLANE = 28.0                             # the aeroplane that shows a landing (wingspan, canvas units: a symbol, not to scale)
REGION = (464.0, 184.0)                  # where the middle of the Jeddah runways goes
ROT = 0.0                                # degrees clockwise by which the Jeddah frame is turned on the page: 0 is north up, as the brief asks. 180 shows the same map south up, that is as
                                         # a pilot approaching runway 16 sees it (then 16L, 16C, 16R read from page left to right, as legend item 5 says, and the north arrow points down)


def ends(r):
    """The two ends of a Jeddah runway in km (north end, south end), from its middle, its true bearing and its declared length."""
    hx, hy = UX * r["len"] / 2, UY * r["len"] / 2
    return (r["mid"][0] - hx, r["mid"][1] - hy), (r["mid"][0] + hx, r["mid"][1] + hy)


S_PLANE = 1.46                                                         # km before the end of the middle runway where the aeroplane of an approach is drawn


def turn(p):
    """A point (east, north) in km as (right, up) on the page: the frame turned by ROT degrees clockwise."""
    a_ = math.radians(ROT)
    return p[0] * math.cos(a_) + p[1] * math.sin(a_), -p[0] * math.sin(a_) + p[1] * math.cos(a_)


def along(p, s_):
    """The point s_ km from p along the direction of landing on 16 (positive: towards the south-south-east), in km east and north."""
    return p[0] + UX * s_, p[1] + UY * s_


_n_mid, _s_mid = ends(JED[1])
_keys = [(q, 8.0) for r in JED for q in ends(r)] + [(along(_n_mid, -S_PLANE), PLANE * 0.6 + 4), (along(_s_mid, S_PLANE), PLANE * 0.6 + 4)]       # (a point, the margin round it in canvas units)
_us = [(turn(q)[0] - m / K, turn(q)[0] + m / K) for q, m in _keys]
_vs = [(turn(q)[1] - m / K, turn(q)[1] + m / K) for q, m in _keys]
OX = REGION[0] - K * (min(a_ for a_, _ in _us) + max(b_ for _, b_ in _us)) / 2                      # the canvas place of the reference point
OY = REGION[1] + K * (min(a_ for a_, _ in _vs) + max(b_ for _, b_ in _vs)) / 2


def to_canvas(p):
    u, v = turn(p)
    return OX + K * u, OY - K * v


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=6, relief=0.8, tone=0.0) + H.paint_filter(U + "pw", seed=12, wear=0.35, thickness=0.35)
            + H.blur_filter(U + "bl", 1.4) + H.blur_filter(U + "bg", 2.2) + H.blur_filter(U + "b3", 0.8) + H.shadow_filter(U + "sh", 0.0, 2.6, 3.4, 0.38, "#1A1208")
            + H.shadow_filter(U + "tg", 0.0, 1.2, 1.6, 0.30, "#1A1208")
            + f'<radialGradient id="{U}rg" cx="0.36" cy="0.3" r="0.9"><stop offset="0" stop-color="#7C879B"/><stop offset="0.35" stop-color="#3A4457"/><stop offset="0.75" stop-color="#1A2030"/><stop offset="1" stop-color="#0E121C"/></radialGradient>'
            + f'<radialGradient id="{U}gl" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.10"/><stop offset="0.8" stop-color="#FFFFFF" stop-opacity="0.16"/><stop offset="1" stop-color="#1A2A44" stop-opacity="0.34"/></radialGradient>'
            + f'<linearGradient id="{U}rf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.55"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
            + "</defs>")


# ------------------------------------------------------------------------------------------------------------------ the compass of Thumamah
def polar(r, deg):
    a = math.radians(deg)
    return CX + r * math.sin(a), CY - r * math.cos(a)


def compass_glass():
    return f'<circle cx="{CX}" cy="{CY}" r="{R_IN}" fill="#F4F1E4" opacity="0.30"/>'


def runway_in_compass():
    """Runway 17/35 along its magnetic direction: the frame's up (-y) points to 348, the end where you land towards 348 and read 35 is at the bottom."""
    return f'<g transform="translate({CX} {CY}) rotate({MAG_S})">{B.runway(U, BAR_T, HALF_T, (RW_S["id"], ""), (RW_N["id"], ""), NUM_T)}</g>'


def compass_top():
    """The bezel, its lit scale and numerals, the sheen on the glass (drawn over the runway)."""
    ring = (f"M {CX - R_OUT},{CY} A {R_OUT},{R_OUT} 0 1 0 {CX + R_OUT},{CY} A {R_OUT},{R_OUT} 0 1 0 {CX - R_OUT},{CY} Z "
            f"M {CX - R_IN},{CY} A {R_IN},{R_IN} 0 1 1 {CX + R_IN},{CY} A {R_IN},{R_IN} 0 1 1 {CX - R_IN},{CY} Z")
    out = [f'<circle cx="{CX}" cy="{CY}" r="{R_IN}" fill="url(#{U}gl)"/>', f'<path d="{ring}" fill="url(#{U}rg)" fill-rule="evenodd" filter="url(#{U}sh)"/>',
           f'<circle cx="{CX}" cy="{CY}" r="{R_OUT - 0.5}" fill="none" stroke="#C9D2E2" stroke-opacity="0.8" stroke-width="0.9"/><circle cx="{CX}" cy="{CY}" r="{R_IN + 0.4}" fill="none" stroke="#050810" stroke-opacity="0.85" stroke-width="1.0"/>'
           f'<circle cx="{CX}" cy="{CY}" r="{R_IN + 1.2}" fill="none" stroke="#7E8CA8" stroke-opacity="0.7" stroke-width="0.6"/>']
    ticks = []
    for deg in range(0, 360, 10):
        major = deg % 30 == 0
        a, b = polar(R_IN + 1.8, deg), polar(R_IN + ((7.0 if deg % 90 == 0 else 10.0) if major else 5.6), deg)
        ticks.append(f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke-width="{1.4 if major else 0.9}"/>')
    out.append(f'<g stroke="#8CC8FF" stroke-opacity="0.85" stroke-linecap="round" filter="url(#{U}bg)" fill="none">{"".join(ticks)}</g><g stroke="#F4F8FF" stroke-linecap="round" fill="none">{"".join(ticks)}</g>')
    for deg, s in ((0, "360"), (90, "090"), (180, "180"), (270, "270")):
        x, y = polar(R_IN + 12.0, deg)
        for blur in (True, False):
            g = H.glyph_text(s, x, y, 8.0, "#FFE9A8" if blur else "#FFFDF2", rotate=deg, spacing=0.8, stroke="#FFE9A8" if blur else None, stroke_width=0.6 if blur else 0)
            out.append(f'<g filter="url(#{U}bg)" opacity="0.8">{g}</g>' if blur else g)
    out.append(f'<path d="M {CX - 90},{CY - 26} A 94,94 0 0 1 {CX - 28},{CY - 88} L {CX - 33},{CY - 66} A 74,74 0 0 0 {CX - 74},{CY - 28} Z" fill="url(#{U}rf)" opacity="0.45"/>')
    return "".join(out)


NOSE = PLANE * 0.40                                                    # from the middle of the picture of the aeroplane to its nose


def plane(x, y, heading):
    """The twin's aeroplane seen from above, flying towards `heading` degrees."""
    return {"name": "sprite-top", "at": [round(x, 2), round(y, 2)], "width": PLANE, "angle": heading, "shadow": {"dx": 1.2, "dy": 2.0, "blur": 1.5, "opacity": 0.26}}


def planes_left():
    out = []
    ta, tb = polar(R_OUT + 26.0, MAG_S), polar(R_OUT + 26.0, MAG_N)          # the aeroplane that lands towards 168 comes from the north-north-west, the other from the south-south-east
    out.append(plane(ta[0], ta[1], MAG_N))
    out.append(plane(tb[0], tb[1], MAG_S))
    out.append(B.label(f"{MAG_N}°", ta[0] + PLANE / 2 + 5, ta[1] - 2, 11.5, anchor="start"))
    out.append(B.label(f"{MAG_S}°", tb[0] - PLANE / 2 - 5, tb[1] + 2, 11.5, anchor="end"))
    return out


def arrows_left():
    out = []
    # magnetic north: a lit blue arrow from the middle
    out.append(S.ribbon(U + "n", [(CX, CY - 4), (CX, CY - 46), (CX, CY - 94)], 5.6, "#1D4ED8", "#6FA0FF", head=2.2, tail=0.8))
    # the angle clockwise from north to the runway: an orange ribbon that goes round
    r_arc = 38.0
    arc = [polar(r_arc, a) for a in range(0, MAG_N, 12)] + [polar(r_arc, MAG_N)]
    out.append(S.ribbon(U + "o", arc, 5.2, "#D9660F", "#F7A24E", head=2.0, tail=0.9, per=2))
    # the two landings: dark ribbons that come in along the runway and end at the near end, where the number is read (the aeroplane is laid over their tail)
    for tag, deg in (("a", MAG_S), ("b", MAG_N)):
        tail, head = polar(R_OUT + 26.0 - NOSE + 2.0, deg), polar(HALF_T + 9.0, deg)
        line = [tail, ((tail[0] + head[0]) / 2, (tail[1] + head[1]) / 2), head]
        out.append(S.ribbon(U + "c" + tag, line, 6.4, "#FFFFFF", "#FFFFFF", head=1.9, tail=1.0, per=2, shadow=False, opacity=0.95))
        out.append(S.ribbon(U + "d" + tag, line, 3.6, "#1F2937", "#566178", head=2.2, tail=1.0, per=2))
    # the hub
    out.append(f'<circle cx="{CX}" cy="{CY}" r="4.2" fill="#B9C2D2" stroke="#2B3446" stroke-width="0.8"/><circle cx="{CX - 1}" cy="{CY - 1}" r="1.5" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------------ Jeddah
def jeddah_runways():
    out = []
    for r in JED:
        cx, cy = to_canvas(r["mid"])
        half = K * r["len"] / 2
        out.append(f'<g transform="translate({n(cx)} {n(cy)}) rotate({n(BRG + 180 + ROT)})">{B.runway(U, BAR_J, half, (r["s_id"][:2], r["s_id"][2:]), (r["n_id"][:2], r["n_id"][2:]), NUM_H)}</g>')
    return "".join(out)


def approach_ribbons():
    """The two approaches along the middle runway: an aeroplane at the tail of a ribbon that ends before the near end (blue to 16, orange to 34)."""
    n_end, s_end = ends(JED[1])
    pts_n = [to_canvas(along(n_end, -s_)) for s_ in (S_PLANE - NOSE / K + 0.02, (S_PLANE + 0.24) / 2, 0.24)]
    pts_s = [to_canvas(along(s_end, s_)) for s_ in (S_PLANE - NOSE / K + 0.02, (S_PLANE + 0.24) / 2, 0.24)]
    ribbons = S.ribbon(U + "j1", pts_n, 5.6, "#1D4ED8", "#6FA0FF", head=2.1, tail=0.8) + S.ribbon(U + "j2", pts_s, 5.6, "#C2570C", "#F7A24E", head=2.1, tail=0.8)
    planes = [plane(*to_canvas(along(n_end, -S_PLANE)), BRG + ROT), plane(*to_canvas(along(s_end, S_PLANE)), BRG + 180 + ROT)]
    return ribbons, planes, pts_n, pts_s


def north_arrow(x, y):
    """A north arrow centred on (x, y): a dark ribbon pointing to the north of the Jeddah frame (up when ROT is 0), with N beyond its tip."""
    dx, dy = math.sin(math.radians(ROT)), -math.cos(math.radians(ROT))
    line = [(x - 19 * dx, y - 19 * dy), (x - 1 * dx, y - 1 * dy), (x + 19 * dx, y + 19 * dy)]
    return (S.ribbon(U + "na", line, 8.4, "#FFFFFF", "#FFFFFF", head=1.9, tail=1.0, per=2, shadow=False, opacity=0.95) + S.ribbon(U + "nb", line, 5.0, "#1F2937", "#566178", head=2.2, tail=1.0, per=2)
            + B.label("N", x + 35 * dx, y + 35 * dy, 12.5))


def scale_bar(x, y):
    """One nautical mile (1852 m): a bar of two halves, a dark and a pale one, on a white casing, with the length at its end."""
    w, h = K * B.NM, 4.2
    return (f'<rect x="{n(x - 2.5)}" y="{n(y - h / 2 - 2.5)}" width="{n(w + 5)}" height="{n(h + 5)}" rx="2.4" fill="#FFFFFF" fill-opacity="0.86"/>'
            f'<rect x="{n(x)}" y="{n(y - h / 2)}" width="{n(w / 2)}" height="{n(h)}" fill="#1F2937"/><rect x="{n(x + w / 2)}" y="{n(y - h / 2)}" width="{n(w / 2)}" height="{n(h)}" fill="#FFFFFF" stroke="#1F2937" stroke-width="0.8"/>'
            + B.label("1 NM", x + w + 8, y, 10.0, anchor="start", halo=2.6))


def tag(x, y, s, height=11.5):
    """A code in a small white label (the ICAO code of an aerodrome)."""
    w = B.width_of(s, height, height * 0.06) + 12
    return (f'<rect x="{n(x)}" y="{n(y - height / 2 - 4.5)}" width="{n(w)}" height="{n(height + 9)}" rx="5.5" fill="#FFFFFF" fill-opacity="0.92" filter="url(#{U}tg)"/>'
            + B.text(s, x + w / 2, y, height, "#1F2937", spacing=height * 0.06, stroke="#1F2937", stroke_width=height * 0.03))


def callouts(pts_n, pts_s):
    c = S.callout
    # 1 at the blue arrow, 2 at the orange ribbon, 3 and 4 at the numbers at the two ends of the runway in the compass
    n17 = polar(HALF_T - 17.0, MAG_S)                                  # the middle of the number at the north end (17): that end lies towards 348
    n35 = polar(HALF_T - 17.0, MAG_N)                                  # and the end of the 35 towards 168
    j5, j6 = pts_n[1], pts_s[1]
    return "".join([c(1, CX + 31, CY - 80, CX + 2, CY - 70), c(2, CX + 70, CY + 14, CX + 37, CY + 4), c(3, n17[0] - 40, n17[1] - 2, n17[0] - 11, n17[1]), c(4, n35[0] + 40, n35[1] + 2, n35[0] + 11, n35[1]),
                    c(5, j5[0] + 32, j5[1] - 6, j5[0] + 3, j5[1] + 1), c(6, j6[0] - 32, j6[1] + 6, j6[0] - 3, j6[1] - 1)])


def scenery():
    return S.scrub(51, 330, 460, 100, 330, 6, scale=0.85) + S.scrub(52, 560, 634, 100, 340, 5, scale=0.85) + S.scrub(53, 6, 30, 20, 340, 4, scale=0.85)


def layers():
    ribbons, planes, pts_n, pts_s = approach_ribbons()
    return [{"name": "terrain-18-02", "at": [W / 2, HT / 2], "width": W}, defs(), scenery(), compass_glass(), runway_in_compass(), jeddah_runways(), ribbons, compass_top(), arrows_left(),
            *planes_left(), *planes, north_arrow(600, 70), scale_bar(304, 334), tag(22, 24, OETH["icao"]), tag(300, 24, OEJN["icao"]), callouts(pts_n, pts_s)]


def plate():
    return {
        "id": "fig-18-02-runway-designators",
        "replaces": "fig-18-02-runway-designators.svg",
        "book_file": "plate-18-02-runway-designators.jpg",
        "caption": "Figure 18-2. Naming a runway from its magnetic direction",
        "desc": ("Figure 18-2. Naming a runway from its magnetic direction. Left, Thumamah (OETH): a compass with magnetic north up and runway 17/35 laid along its direction of 168 degrees magnetic, "
                 "with the two landings (towards 168 and towards 348 degrees) ending at the numbers 17 and 35. Right, Jeddah (OEJN), north up: its three parallel runways, 16L, 16C and 16R "
                 "(34R, 34C and 34L from the other end), the westernmost 3 800 m long and the other two 4 000 m. Runway widths are exaggerated so that the numbers can be read. "
                 "Thumamah drawn from its AIP data, Jeddah's runways from their thresholds, at one scale; not for navigation."),
        "legend": [
            "Magnetic north.",
            "The direction of the runway at Thumamah, 168° magnetic: 171° true less the variation, 3° E.",
            "Landing towards 168°, you read `17` at the near end (16.8 rounds to 17).",
            "Landing towards 348°, you read `35` (34.8 rounds to 35).",
            "Jeddah has three parallel runways. Flying towards runway 16, the pilot has `16L` on the left, `16C` ahead and `16R` on the right (the picture is north up, so the left runway is the one on the right of the page).",
            "Flying towards runway 34 from the other end, the same three runways are `34R` on the left, `34C` ahead and `34L` on the right.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-02-runway-designators.svg", "blank": True, "layers": layers()},
    }
