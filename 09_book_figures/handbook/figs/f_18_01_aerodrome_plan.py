"""Figure 18-1 (the Saudi round). The parts of an aerodrome seen from above, drawn from the real aerodrome: Thumamah (OETH).

The runway (4 000 x 50 m, true bearing 171/351), its two stopways and the thresholds are the AIP's (AD 2.12, AMDT 11/26); the pavements (the aprons, the links, the turn loops), the buildings, the road and the
berm were traced by the saudi-airspace project from satellite imagery (outlines only, +/-10 m; data/oeth_plan.json, built by data/build_oeth_plan.py) and the parked aeroplanes are the ones of its scene.
Two panels, both to scale: a strip with the whole aerodrome (4.4 km), and the northern 2.3 km in detail, with the ten numbered callouts. North is to the left (the arrow shows it): the runway lies along the
page. Thumamah has no control tower and the AIP lists no windsock or signal area for it, so the old figure's windsock, signal area and tower are not drawn."""
import json
import math
import os

from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 360
D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "oeth_plan.json")))
terrain.ensure("terrain-18-01-thumamah", size=(W * 4, HT * 4), seed=1870, kind="plain", features=(), veil=0.36, soft=2.8)

U = "t181"
PAINT = "#F4F1E6"
YEL = "#EDB92D"
# the detail panel: 2 330 m of the runway (s from -400 to 1 930) across 612 units; t (to the west) downwards
MX0, MY0, MW, MH = 14.0, 106.0, 612.0, 244.0
MS0, MT0 = -400.0, -300.0
KM = MW / 2330.0
# the overview strip: the whole aerodrome, 4 550 m across the same width
OX0, OY0, OW, OH = 14.0, 10.0, 612.0, 80.0
OS0, OT0 = -400.0, -205.0
KO = OW / 4550.0
RW = 25.0


def pm(t, s):
    return (MX0 + (s - MS0) * KM, MY0 + (t - MT0) * KM)


def po(t, s):
    return (OX0 + (s - OS0) * KO, OY0 + (t - OT0) * KO)


def pts_of(ring, f):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in (f(t, s) for t, s in ring))


def path_of(ring, f):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in (f(t, s) for t, s in ring)) + " Z"


def inside(pt, poly):
    x, y = pt
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


PAV = {p["name"]: p for p in D["pavements"]}
BLUE_NAMES = ("WEST TAXIWAY (s 300-900)", "DIAGONAL LINK (main apron to runway)", "MID LINK", "SOUTH LINK FILLET", "SOUTH TURN LOOP (TWY T)")
ORANGE_NAMES = ("MAIN APRON", "NORTH PARKING APRON", "APRON NORTH OF MAIN APRON")
BLUE, ORANGE = "#2F6FE0", "#F08A24"


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=4, relief=0.8, tone=0.0) + H.asphalt_filter(U + "at", seed=9, relief=0.7, tone=0.35) + H.concrete_filter(U + "co", seed=8)
            + H.paint_filter(U + "pw", seed=11, wear=1.0, thickness=0.45) + H.paint_filter(U + "py", seed=21, wear=0.8, thickness=0.4)
            + H.shadow_filter(U + "sh", 0.7, 1.1, 0.8, 0.34) + H.blur_filter(U + "bl", 0.8) + H.lamp_defs(U + "l")
            + f'<clipPath id="{U}cm"><rect x="{MX0}" y="{MY0}" width="{MW}" height="{MH}" rx="9"/></clipPath>'
            + f'<clipPath id="{U}co2"><rect x="{OX0}" y="{OY0}" width="{OW}" height="{OH}" rx="9"/></clipPath></defs>')


def holes_path(p, f):
    return path_of(p["ring"], f) + "".join(" " + path_of(h, f) for h in p["holes"])


def ground_card(x, y, w, h, tint_op):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#F4EBD3" fill-opacity="{tint_op}"/>')


def frame(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="none" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="3.2"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="none" stroke="#6B6247" stroke-opacity="0.75" stroke-width="0.8"/>')


# ----------------------------------------------------------------------------------------------------- the detail panel
def detail():
    f = pm
    out = [f'<g clip-path="url(#{U}cm)">', ground_card(MX0, MY0, MW, MH, 0.18)]
    # the road to the west and the berm to the east of the runway (traced lines)
    road = " ".join(f"{x:.1f},{y:.1f}" for x, y in (f(t, s) for t, s in D["lines"]["ACCESS_ROAD"]))
    berm = " ".join(f"{x:.1f},{y:.1f}" for x, y in (f(t, s) for t, s in D["lines"]["EAST_BERM"]))
    out.append(f'<polyline points="{berm}" fill="none" stroke="#8E7A54" stroke-opacity="0.5" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{road}" fill="none" stroke="#B9AD90" stroke-opacity="0.6" stroke-width="7.6" stroke-linecap="round" stroke-linejoin="round"/>'
               f'<polyline points="{road}" fill="none" stroke="#4B5363" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#{U}at)"/>'
               f'<polyline points="{road}" fill="none" stroke="#F1E3A0" stroke-width="0.5" stroke-dasharray="3 3" stroke-linecap="round"/>')
    # pavements: a graded shoulder, then the surface (asphalt or concrete), then a tint for the zone
    order = [p for p in D["pavements"] if p["surface"] != "stopway"]
    for p in order:
        out.append(f'<path d="{holes_path(p, f)}" fill="none" stroke="#C8B78F" stroke-opacity="0.6" stroke-width="3.4" stroke-linejoin="round"/>')
    for p in order:
        d = holes_path(p, f)
        if p["surface"] == "concrete":
            out.append(f'<path d="{d}" fill="#9A9DA2" fill-rule="evenodd" filter="url(#{U}co)"/>')
        else:
            out.append(f'<path d="{d}" fill="#444" fill-rule="evenodd" filter="url(#{U}as)"/>')
        tint = BLUE if p["name"] in BLUE_NAMES else (ORANGE if p["name"] in ORANGE_NAMES else None)
        if tint:
            out.append(f'<path d="{d}" fill="{tint}" fill-opacity="0.30" fill-rule="evenodd"/>'
                       f'<path d="{d}" fill="none" fill-rule="evenodd" stroke="{tint}" stroke-width="1.1" stroke-dasharray="5 3" stroke-linejoin="round"/>')
        out.append(f'<path d="{d}" fill="none" fill-rule="evenodd" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.5" stroke-linejoin="round"/>')
    # the runway and its two stopways, then the paint
    x0, y0 = f(-RW, -300)
    x1, y1 = f(RW, 4064.6)
    out.append(f'<rect x="{x0 - 1.6:.1f}" y="{y0 - 1.6:.1f}" width="{x1 - x0 + 3.2:.1f}" height="{y1 - y0 + 3.2:.1f}" fill="#C8B78F" fill-opacity="0.55"/>')
    rx0, ry0 = f(-RW, 0)
    rx1, ry1 = f(RW, 4004.6)
    out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="#444" filter="url(#{U}as)"/>')
    out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{BLUE}" fill-opacity="0.26"/>')
    out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="none" stroke="#FFFFFF" stroke-opacity="0.5" stroke-width="0.5"/>')
    paint = []
    # edge lines and centreline (wider than life, so that they read at this scale)
    for t in (-RW + 1.5, RW - 1.5):
        a, b = f(t, 3), f(t, 4001.5)
        paint.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke-width="0.7" stroke-opacity="0.9"/>')
    s = 70.0
    while s < 3960:
        a, b = f(0, s), f(0, s + 30)
        paint.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke-width="1.0"/>')
        s += 50
    # threshold bars (6 on each side of the centreline), the touchdown-zone pairs and the aiming point as the AIP's list of markings names them (TDZ, THR, pre-THR)
    for k in range(6):
        for sg in (-1, 1):
            t = sg * (2.6 + 3.9 * k)
            a, b = f(t, 8), f(t, 38)
            paint.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke-width="0.85"/>')
    for s_at, nn in ((160, 3), (310, 3), (460, 2), (610, 2), (760, 1), (910, 1)):
        for k in range(nn):
            for sg in (-1, 1):
                t = sg * (8.0 + 3.1 * k)
                a, b = f(t, s_at), f(t, s_at + 24)
                paint.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke-width="1.1"/>')
    out.append(f'<g stroke="{PAINT}" filter="url(#{U}pw)">{"".join(paint)}</g>')
    # the designator, read from the approach (the top of the figures points down the runway)
    dx, dy = f(0, 78)
    out.append(H.glyph_text("17", dx, dy, 8.6, PAINT, rotate=90, spacing=1.2, stroke=PAINT, stroke_width=0.3))
    # the stopway (300 m north of the 17 threshold): yellow chevrons pointing towards the runway
    ch = []
    for k in range(10):
        s = -300 + 18 + k * 29.0
        a, b, c = f(-RW + 3, s - 11), f(0, s + 5), f(RW - 3, s - 11)
        ch.append(f'<polyline points="{a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f} {c[0]:.1f},{c[1]:.1f}" fill="none" stroke-width="1.5" stroke-linejoin="miter"/>')
    out.append(f'<g stroke="{YEL}" filter="url(#{U}py)">{"".join(ch)}</g>')
    # the threshold lights (green) and the red lights at the far end of the stopway
    for t in range(-24, 25, 4):
        a = f(t, -1.5)
        out.append(H.lamp(U + "l", a[0], a[1], 0.55, "green", 2.6, 0.9))
        a = f(t, -298.5)
        out.append(H.lamp(U + "l", a[0], a[1], 0.55, "red", 2.6, 0.9))
    # the runway edge lights, white, every 60 m (AD 2.14)
    for s in range(60, 1930, 60):
        for t in (-RW - 1.2, RW + 1.2):
            a = f(t, s)
            out.append(H.lamp(U + "l", a[0], a[1], 0.5, "white", 2.2, 0.85))
    # the taxiway edge lights are blue: along the west taxiway
    # the runway-holding position on the diagonal link: two solid and two dashed yellow lines across the taxiway, 40 m from the runway edge
    ax, ay = 0.77, -0.64                          # the axis of the link in (t, s), pointing away from the runway
    ptx, pty = 25 + 34 * ax, 1362 + 34 * ay
    hold = []
    for off, dash in ((15.0, None), (9.4, None), (0.0, "3.0 2.4"), (-5.6, "3.0 2.4")):
        pa = f(ptx + ax * off + 0.64 * 27, pty + ay * off + 0.77 * 27)
        pb = f(ptx + ax * off - 0.64 * 27, pty + ay * off - 0.77 * 27)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        hold.append(f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" stroke-width="1.35"{da}/>')
    out.append(f'<g stroke="{YEL}" fill="none" filter="url(#{U}py)">{"".join(hold)}</g>')
    # the buildings: oriented footprints with a soft shadow and the traced roof colour
    ROOF = {"white": "#F3F1EA", "light": "#E6E1D3", "green": "#6D9C6B", "grey": "#BCBEC1", "tan": "#CDB88A", "beige_grey_bays": "#D9CBAA", "white_oeth": "#F3F1EA"}
    for b in D["buildings"]:
        ring = [f(t, s) for t, s in b["ring"]]
        ps = " ".join(f"{x:.1f},{y:.1f}" for x, y in ring)
        k = b["height_m_estimated"] * KM * 0.5
        sh = " ".join(f"{x + 0.8 * k:.1f},{y + 1.0 * k:.1f}" for x, y in ring)
        out.append(f'<polygon points="{sh}" fill="#2B2418" fill-opacity="0.34" filter="url(#{U}bl)"/>')
        out.append(f'<polygon points="{ps}" fill="{ROOF.get(b["roof"], "#E6E1D3")}" stroke="#8C8470" stroke-width="0.4" stroke-linejoin="round"/>')
        if b["roof"] == "white_oeth":
            cx = sum(p[0] for p in ring) / 4
            cy = sum(p[1] for p in ring) / 4
            out.append(H.glyph_text("OETH", cx, cy, 5.6, "#27406B", spacing=0.8))
    # the parked aeroplanes (the model's own picture), nose along the runway axis
    shadow = {"dx": 0.9, "dy": 1.3, "blur": 1.0, "opacity": 0.32}
    spr = []
    for (t, s, hdg) in D["parked_aeroplanes"]:
        x, y = f(t, s)
        spr.append({"name": "sprite-top", "at": [x, y], "width": 5.6, "angle": -90 if hdg == 1 else 90, "shadow": shadow})
    # a scale bar (500 m) and the north arrow
    L = 500 * KM
    bx, by = MX0 + MW - 26 - L, MY0 + MH - 18
    out.append(f'<rect x="{bx - 8}" y="{by - 15}" width="{L + 16:.0f}" height="26" rx="6" fill="#FFFFFF" fill-opacity="0.82"/>'
               f'<line x1="{bx}" y1="{by}" x2="{bx + L:.1f}" y2="{by}" stroke="#1F2937" stroke-width="2.2"/><line x1="{bx}" y1="{by - 5}" x2="{bx}" y2="{by + 5}" stroke="#1F2937" stroke-width="2.2"/>'
               f'<line x1="{bx + L:.1f}" y1="{by - 5}" x2="{bx + L:.1f}" y2="{by + 5}" stroke="#1F2937" stroke-width="2.2"/>'
               f'<text x="{bx + L / 2:.1f}" y="{by - 6}" font-family="sans-serif" font-size="10" font-weight="bold" fill="#1F2937" text-anchor="middle">500 m</text>')
    out.append("</g>")
    return "".join(out), spr


def north_arrow():
    nt, ns = D["runway"]["north_in_ts_per_m"]          # north in the runway frame; the page: x = s, y = t
    vx, vy = ns, nt
    n = math.hypot(vx, vy)
    vx, vy = vx / n, vy / n
    cx, cy = MX0 + MW - 34, MY0 + 30
    return (f'<circle cx="{cx}" cy="{cy}" r="21" fill="#FFFFFF" fill-opacity="0.85"/>'
            f'<line x1="{cx - vx * 13:.1f}" y1="{cy - vy * 13:.1f}" x2="{cx + vx * 13:.1f}" y2="{cy + vy * 13:.1f}" stroke="#1F2937" stroke-width="2.2"/>'
            f'<polygon points="{cx + vx * 17:.1f},{cy + vy * 17:.1f} {cx + vx * 8 - vy * 5:.1f},{cy + vy * 8 + vx * 5:.1f} {cx + vx * 8 + vy * 5:.1f},{cy + vy * 8 - vx * 5:.1f}" fill="#1F2937"/>'
            f'<text x="{cx - vx * 21 - 4:.1f}" y="{cy - vy * 21 + (4 if vy > -0.5 else -2):.1f}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1F2937">N</text>')


# ----------------------------------------------------------------------------------------------------- the overview strip
def overview():
    f = po
    out = [f'<g clip-path="url(#{U}co2)">', ground_card(OX0, OY0, OW, OH, 0.30)]
    for p in D["pavements"]:
        if p["surface"] == "stopway":
            continue
        fill = "#9A9DA2" if p["surface"] == "concrete" else "#4B5363"
        out.append(f'<path d="{holes_path(p, f)}" fill="{fill}" fill-rule="evenodd" stroke="#FFFFFF" stroke-opacity="0.4" stroke-width="0.3"/>')
    x0, y0 = f(-RW, -300)
    x1, y1 = f(RW, 4064.6)
    out.append(f'<rect x="{x0:.1f}" y="{y0 - 0.6:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0 + 1.2:.1f}" fill="#3F4654"/>')
    for b in D["buildings"]:
        out.append(f'<polygon points="{pts_of(b["ring"], f)}" fill="#F3F1EA" stroke="#8C8470" stroke-width="0.25"/>')
    # the stopways in yellow (north 300 m, south 60 m)
    a, b = f(-RW, -300), f(RW, 0)
    out.append(f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0] - a[0]:.1f}" height="{b[1] - a[1]:.1f}" fill="none" stroke="{YEL}" stroke-width="0.8"/>')
    a, b = f(-RW, 4004.6), f(RW, 4064.6)
    out.append(f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0] - a[0]:.1f}" height="{b[1] - a[1]:.1f}" fill="none" stroke="{YEL}" stroke-width="0.8"/>')
    # the designators at both ends
    d1 = f(0, 60)
    d2 = f(0, 3940)
    out.append(H.glyph_text("17", d1[0] + 7, d1[1] - 9.5, 6.5, "#FFFFFF", rotate=0, stroke="#1F2937", stroke_width=0.4))
    out.append(H.glyph_text("35", d2[0] - 7, d2[1] - 9.5, 6.5, "#FFFFFF", rotate=0, stroke="#1F2937", stroke_width=0.4))
    # the part drawn in detail below
    fx0, fy0 = f(OT0, MS0)
    fx1, _ = f(OT0, MS0 + 2330)
    out.append(f'<rect x="{fx0 + 0.6:.1f}" y="{OY0 + 1.6}" width="{fx1 - fx0 - 1.2:.1f}" height="{OH - 3.2}" rx="4" fill="none" stroke="#FFFFFF" stroke-width="2.6"/>'
               f'<rect x="{fx0 + 0.6:.1f}" y="{OY0 + 1.6}" width="{fx1 - fx0 - 1.2:.1f}" height="{OH - 3.2}" rx="4" fill="none" stroke="#D1473B" stroke-width="1.1"/>')
    out.append("</g>")
    return "".join(out)


def inside_point(name, t_hint, s_hint):
    """A point of the pavement `name` (not in a hole) nearest to the hint."""
    p = PAV[name]
    best = None
    for dt in range(-60, 61, 5):
        for ds in range(-60, 61, 5):
            q = (t_hint + dt, s_hint + ds)
            if inside(q, p["ring"]) and not any(inside(q, h) for h in p["holes"]):
                d = dt * dt + ds * ds
                if best is None or d < best[0]:
                    best = (d, q)
    return best[1] if best else (t_hint, s_hint)


def callouts():
    c = S.callout
    f = pm
    pts = {n: f(*inside_point(n, *h)) for n, h in (("WEST TAXIWAY (s 300-900)", (187.5, 600)), ("MAIN APRON", (150, 1150)), ("NORTH PARKING APRON", (225, 380)),
                                                     ("NORTH COMPLEX (turn loop, hangar apron, link)", (76, 12)))}
    hold = f(25 + 34 * 0.77, 1362 - 34 * 0.64)
    des = f(0, 78)
    sw = f(0, -150)
    b = next(x for x in D["buildings"] if x["id"] == "HANGAR_MAIN_N")
    hang = f(sum(p[0] for p in b["ring"]) / 4, sum(p[1] for p in b["ring"]) / 4)
    top, low = MY0 + 22, MY0 + MH - 20
    r1, r6 = f(0, 1000), f(8, 620)
    return "".join([
        c(1, 382, top, r1[0], r1[1] - 6),
        c(2, des[0] + 22, top, des[0] + 4, des[1] - 8),
        c(3, 262, low, *pts["WEST TAXIWAY (s 300-900)"]),
        c(4, 512, top, hold[0] + 1, hold[1] - 6),
        c(5, 350, low, *pts["MAIN APRON"]),
        c(6, 282, top, r6[0], r6[1] - 5),
        c(7, 172, low, *pts["NORTH PARKING APRON"]),
        c(8, sw[0], top, sw[0], sw[1] - 8),
        c(9, 80, low, *pts["NORTH COMPLEX (turn loop, hangar apron, link)"]),
        c(10, 432, low, hang[0], hang[1] + 3),
    ])


def layers():
    det, spr = detail()
    return [{"name": "terrain-18-01-thumamah", "at": [W / 2, HT / 2], "width": W}, defs(), overview(), frame(OX0, OY0, OW, OH), det, *spr, frame(MX0, MY0, MW, MH), north_arrow(), callouts()]


def plate():
    return {
        "id": "fig-18-01-aerodrome-plan",
        "replaces": "fig-18-01-aerodrome-plan.svg",
        "book_file": "plate-18-01-aerodrome-plan.jpg",
        "caption": "Figure 18-1. The parts of an aerodrome seen from above: Thumamah (OETH)",
        "desc": "Figure 18-1. The parts of an aerodrome seen from above: Thumamah (OETH). North is to the left, as the arrow shows; both panels are to scale; the pavements and buildings are traced outlines; not for navigation.",
        "legend": [
            "Runway 17/35: 4 000 m by 50 m, asphalt.",
            "Runway designator: `17` at the north end (in the strip, `35` at the south end).",
            "The parallel taxiway, one of the taxiways that join the apron to the runway (the AIP names taxiways `A` to `F` and `T`).",
            "Runway-holding position, the holding point where an aircraft stops before entering the runway.",
            "The main apron.",
            "Manoeuvring area: the runway and the taxiways (blue).",
            "Movement area: the manoeuvring area and the aprons (blue and orange).",
            "Stopway beyond the north end, 300 m by 50 m, with yellow chevrons pointing to the runway.",
            "The turn loop beside the north end, round a sand island.",
            "Hangar. Thumamah has no control tower: its radio is a UNICOM.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-01-aerodrome-plan.svg", "blank": True, "layers": layers()},
    }
