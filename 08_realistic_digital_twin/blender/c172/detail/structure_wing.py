"""Wing structure: spars, ribs, stringers and attach fittings (POH p.7-3).

"The externally braced wings, containing the fuel tanks, are constructed of a front and rear spar
with formed sheet metal ribs, doublers, and stringers. The entire structure is covered with aluminum
skin. The front spars are equipped with wing-to-fuselage and wing-to-strut attach fittings. The aft
spars are equipped with wing-to-fuselage attach fittings, and are partial-span spars."

What is from where:
  poh        that the wing is built this way, and which fittings each spar carries
  estimated  where the members lie. The spar lines are the two skin seams of the manufacturer's top
             view (14.5 % and 64.5 % of the chord); the rib stations are the wing stations usually
             quoted for this wing (confirm against the maintenance manual); gauges, flange widths,
             lightening holes and the number of stringers are representative.
The tank bay (between the spars, root rib to station 55.6) is left clear: fuel.py puts the tank there.
"""
import math

from mathutils import Vector

from .. import units as U
from ..units import IN
from .. import airframe as A
from . import geom2d
from . import lanes
from .common import Plane, sheet, wall, strip, extrude_along, angle_section, bolt, hex_prism, part, new_bm, box

# Wing stations of the ribs (inches from the centreline). Status: estimated (see the note above).
RIB_STATIONS = [23.62, 39.0, 55.62, 71.62, 85.62, 100.5, 118.0, 136.0, 154.0, 172.0, 190.0, 208.0]
TANK_BAY = (23.62, 55.62)                 # no centre rib between the spars inside the tank bay
SKIN = 0.0012                             # room left for the skin (m)
WEB = 0.001                               # rib web gauge as drawn
FLANGE = 0.014                            # width of a formed rib flange
SPAR_GAP = 0.006                          # chord fraction kept clear of each spar line by the ribs
REAR_SPAR_END = 100.5                     # the rear spar is a partial-span spar (POH): it ends where the aileron begins
AILERON_BELLCRANK_BL = 146.0              # wing station of the aileron bellcrank (controls.py) ...
AILERON_PUSHROD_BL = 148.0                # ... and of the push-pull rod from it to the aileron


def _edge(af, x0, x1, upper):
    """Points of the upper or lower surface of a unit airfoil loop between chord fractions x0 < x1,
    ordered front to rear, including both ends."""
    n = len(af)
    side = af[: n // 2 + 1] if upper else [af[0]] + list(reversed(af[n // 2:]))          # trailing edge -> leading edge
    inner = sorted((p for p in side if x0 + 1e-6 < p[0] < x1 - 1e-6), key=lambda p: p[0])
    return [(x0, A.airfoil_y(af, x0, upper))] + inner + [(x1, A.airfoil_y(af, x1, upper))]


def rib_outline(xabs, x0, x1):
    """Outline (metres, in the plane of the section: chordwise, up) of a rib between chord fractions x0
    and x1, already set in from the skin. Counter-clockwise: lower edge front to rear, upper edge back."""
    af = A.wing_airfoil(xabs)
    c = A.wing_chord(xabs)
    lower = _edge(af, x0, x1, False)
    upper = _edge(af, x0, x1, True)
    if x0 <= 1e-6:                                    # nose rib: the leading edge closes the outline
        loop = lower + list(reversed(upper))[:-1]
    else:
        loop = lower + list(reversed(upper))
    loop = [(x * c, y * c) for x, y in loop]
    return geom2d.inset(loop, SKIN)


def section_plane(xabs, side):
    origin = A.wing_point(xabs, side, 0.0, 0.0)
    return Plane(origin, A.wing_point(xabs, side, 1.0, 0.0) - origin, A.wing_point(xabs, side, 0.0, 1.0) - origin)


def cove_xc(xabs):
    """Chord fraction where the fixed structure ends ahead of the flap or aileron."""
    if xabs > A.AIL_SPAN[1] + 0.005:
        return 1.0                                    # tip rib: full section
    xc = A.FLAP_XC if xabs < (A.FLAP_SPAN[1] + A.AIL_SPAN[0]) / 2 else A.ail_xc(xabs)
    af = A.wing_airfoil(xabs)
    half = 0.5 * (A.airfoil_y(af, xc, True) - A.airfoil_y(af, xc, False))
    return xc - half - 0.006


def _rib(ctx, grp, name, xabs, side, x0, x1, holes, label_en, label_ar, station):
    plane = section_plane(xabs, side)
    outline = rib_outline(xabs, x0, x1)
    c = A.wing_chord(xabs)
    xs = [p[0] for p in outline]
    lightening = []
    for hole in (geom2d.lightening_holes(outline, min(xs) + 0.012, max(xs) - 0.012, holes, 0.020, segments=18) if holes else []):
        cx = sum(p[0] for p in hole) / len(hole); cy = sum(p[1] for p in hole) / len(hole)
        lightening.append((cx, cy, max(p[0] for p in hole) - cx))
    # an opening for every cable, pipe or wire that passes this rib (lanes.py)
    af = A.wing_airfoil(xabs)
    runs = []
    for xc, dz in lanes.wing_crossing(station):
        middle = 0.5 * (A.airfoil_y(af, xc, True) + A.airfoil_y(af, xc, False)) * c + dz
        reach = lanes.HOLE + 0.004
        if all(geom2d.inside((xc * c + dx, middle + dy), outline) for dx, dy in ((reach, 0), (-reach, 0), (0, reach), (0, -reach))):
            runs.append((xc * c, middle, lanes.HOLE))
    lightening = geom2d.clear_of(lightening, runs, 0.005)
    runs = [run for run in runs if not any(math.hypot(run[0] - cx, run[1] - cy) + run[2] < r for cx, cy, r in lightening)]
    cut = [geom2d.circle(cx, cy, r, 18) for cx, cy, r in lightening] + [geom2d.circle(cx, cy, r, 10) for cx, cy, r in runs]
    bm = new_bm()
    sheet(bm, plane, outline, WEB, cut, offset=-WEB / 2)
    # formed flanges along the two skin edges, turned toward the wing root
    split = max(range(len(outline)), key=lambda i: outline[i][0])           # rear-most point of the lower edge
    lower = outline[: split + 1]
    upper = outline[split + 1:] if x0 > 1e-6 else outline[split + 1:] + outline[:1]
    toward_root = -side * FLANGE
    for path in (lower, upper):
        if len(path) >= 2:
            wall(bm, plane, path, WEB, 0.0, toward_root, closed=False, inward=True)
    return part(ctx, name, bm, grp, grp, label_en, label_ar, "bare_alu", status="estimated", pivot=plane.at(0.5 * (x0 + x1) * c, 0.0),
                station_in=station, note="Formed sheet-metal rib (POH p.7-3); station, gauge and lightening holes are representative")


def _spar(ctx, grp, name, side, xs, xc_fn, flange_dir, flange, web, label_en, label_ar, openings=(), **tags):
    """Channel-section spar along the span: a web between the skins with a flange under each skin.
    `openings` are (span position, half width, half height) of holes left in the web, e.g. for a push rod."""
    xs = sorted(set(list(xs) + [x + d for x, half_width, _hh in openings for d in (-half_width, half_width)]))
    tops, bottoms, chord_dirs, ups = [], [], [], []
    for x in xs:
        c = A.wing_chord(x)
        top = A.wing_surface_point(x, side, xc_fn(x), True, inset=(SKIN + 0.0015) / c)
        bottom = A.wing_surface_point(x, side, xc_fn(x), False, inset=(SKIN + 0.0015) / c)
        plane = section_plane(x, side)
        tops.append(top); bottoms.append(bottom); chord_dirs.append(plane.u); ups.append(plane.v)
    thick = [u * web for u in chord_dirs]

    def opening(xa, xb):
        return next((o for o in openings if o[0] - o[1] - 1e-6 <= xa and xb <= o[0] + o[1] + 1e-6), None)

    bm = new_bm()
    i = 0
    while i < len(xs) - 1:                                  # the web, run by run: whole, or above and below an opening
        this = opening(xs[i], xs[i + 1])
        j = i + 1
        while j < len(xs) - 1 and opening(xs[j], xs[j + 1]) is this:
            j += 1
        part_ = slice(i, j + 1)
        if this is None:
            strip(bm, tops[part_], bottoms[part_], thick[part_])
        else:
            middles = [(t + b) / 2 for t, b in zip(tops[part_], bottoms[part_])]
            strip(bm, tops[part_], [m + u * this[2] for m, u in zip(middles, ups[part_])], thick[part_])
            strip(bm, [m - u * this[2] for m, u in zip(middles, ups[part_])], bottoms[part_], thick[part_])
        i = j
    reach = [u * (flange_dir * flange) for u in chord_dirs]
    strip(bm, tops, [t + r for t, r in zip(tops, reach)], [-v * web * 1.2 for v in ups])
    strip(bm, bottoms, [b + r for b, r in zip(bottoms, reach)], [v * web * 1.2 for v in ups])
    mid = len(xs) // 2
    return part(ctx, name, bm, grp, grp, label_en, label_ar, "bare_alu", pivot=(tops[mid] + bottoms[mid]) / 2, **tags)


def build_side(ctx, side):
    S = "L" if side > 0 else "R"
    grp = "WING_" + S
    where_en = "left" if side > 0 else "right"
    where_ar = "الأيسر" if side > 0 else "الأيمن"
    stations = [s * IN for s in RIB_STATIONS]

    # ---- spars
    spar_xs = [A.CABIN_SIDE_X - 0.01] + stations
    _spar(ctx, grp, f"{grp}.front_spar", side, spar_xs, lambda x: A.FRONT_SPAR_XC, 1, 0.032, 0.0025,
          f"Front spar, {where_en} wing", f"العارضة الأمامية للجناح {where_ar}", status="poh", ref="p.7-3",
          note="Full-span spar carrying the wing-to-fuselage and wing-to-strut fittings (POH); its line is the skin seam at 14.5 % chord of the manufacturer's top view")
    rear_xs = [x for x in spar_xs if x <= REAR_SPAR_END * IN + 1e-6]
    _spar(ctx, grp, f"{grp}.rear_spar", side, rear_xs, lambda x: A.REAR_SPAR_XC, -1, 0.028, 0.002,
          f"Rear spar, {where_en} wing (partial span)", f"العارضة الخلفية للجناح {where_ar} (جزئية الامتداد)", status="poh", ref="p.7-3",
          note="Partial-span spar with the rear wing-to-fuselage fitting (POH); drawn from the root to the inboard end of the aileron, on the skin seam at 64.5 % chord")
    ail_xs = [x for x in stations if x >= REAR_SPAR_END * IN - 1e-6]
    _spar(ctx, grp, f"{grp}.aileron_spar", side, ail_xs, lambda x: cove_xc(x) - 0.012, -1, 0.02, 0.0015,
          f"Aileron hinge spar, {where_en} wing", f"عارضة مفصلات الجنيح، الجناح {where_ar}", status="estimated",
          openings=[(AILERON_PUSHROD_BL * IN, 0.022, 0.016)],
          note="Light channel closing the wing ahead of the aileron and carrying its hinges, with an opening for the aileron push-pull rod; representative")

    # ---- ribs
    for index, (station, x) in enumerate(zip(RIB_STATIONS, stations)):
        tag = f"ws{int(round(station)):03d}"
        ws_en = f"wing station {station:g}"
        ws_ar = f"محطة الجناح {station:g}"
        in_tank_bay = TANK_BAY[0] < station < TANK_BAY[1]
        _rib(ctx, grp, f"{grp}.rib_{tag}_nose", x, side, 0.0, A.FRONT_SPAR_XC - SPAR_GAP, 1,
             f"Nose rib, {ws_en}", f"ضلع مقدمة الجناح، {ws_ar}", station)
        rear_limit = A.REAR_SPAR_XC - SPAR_GAP if station <= REAR_SPAR_END else cove_xc(x) - 0.012 - SPAR_GAP
        if not in_tank_bay:
            _rib(ctx, grp, f"{grp}.rib_{tag}_main", x, side, A.FRONT_SPAR_XC + SPAR_GAP, rear_limit, 4 if station <= REAR_SPAR_END else 3,
                 f"Wing rib, {ws_en}", f"ضلع الجناح، {ws_ar}", station)
        if station <= REAR_SPAR_END:
            _rib(ctx, grp, f"{grp}.rib_{tag}_aft", x, side, A.REAR_SPAR_XC + SPAR_GAP, cove_xc(x), 1,
                 f"Trailing rib, {ws_en}", f"ضلع مؤخرة الجناح، {ws_ar}", station)
        elif station >= RIB_STATIONS[-1] - 1e-6:
            _rib(ctx, grp, f"{grp}.rib_{tag}_aft", x, side, cove_xc(x - 0.08) - 0.012 + SPAR_GAP, 0.985, 1,
                 f"Tip rib, trailing part, {ws_en}", f"ضلع طرف الجناح، الجزء الخلفي، {ws_ar}", station)
        # one more nose rib half-way to the next station keeps the leading-edge skin in shape
        if index + 1 < len(RIB_STATIONS):
            mid_station = 0.5 * (station + RIB_STATIONS[index + 1])
            _rib(ctx, grp, f"{grp}.nose_rib_ws{int(round(mid_station)):03d}", mid_station * IN, side, 0.0, A.FRONT_SPAR_XC - SPAR_GAP, 1,
                 f"Intermediate nose rib, wing station {mid_station:g}", f"ضلع مقدمة وسيط، محطة الجناح {mid_station:g}", round(mid_station, 2))

    # ---- stringers: angle sections riveted under the skins between the spars, outboard of the tank bay
    def stringer(name, xc, upper, x_from, x_to, label_en, label_ar):
        xs = [x for x in stations if x_from * IN - 1e-6 <= x <= x_to * IN + 1e-6]
        path, normals = [], []
        for x in xs:
            c = A.wing_chord(x)
            path.append(A.wing_surface_point(x, side, xc, upper, inset=SKIN / c))
            v = section_plane(x, side).v
            normals.append(-v if upper else v)
        bm = new_bm()
        extrude_along(bm, path, angle_section(0.013, 0.013, 0.001), lambda i: normals[i])
        return part(ctx, name, bm, grp, grp, label_en, label_ar, "bare_alu", status="estimated",
                    note="Stringers are named in the POH (p.7-3); their number and position here are representative")
    for number, (xc, upper, x_from, x_to) in enumerate([(0.30, True, 55.62, 190.0), (0.47, True, 55.62, 100.5),
                                                         (0.34, False, 55.62, 190.0), (0.50, False, 55.62, 100.5)], 1):
        stringer(f"{grp}.stringer_{'upper' if upper else 'lower'}_{1 if xc < 0.4 else 2}", xc, upper, x_from, x_to,
                 f"{'Upper' if upper else 'Lower'} skin stringer, {where_en} wing", f"دعامة طولية للجلد {'العلوي' if upper else 'السفلي'}، الجناح {where_ar}")

    # ---- attach fittings
    def fitting(name, xabs, xc, lower_only, label_en, label_ar, ref):
        plane = section_plane(xabs, side)
        c = A.wing_chord(xabs)
        af = A.wing_airfoil(xabs)
        y_top = A.airfoil_y(af, xc, True) * c - 0.024
        y_bot = A.airfoil_y(af, xc, False) * c + (0.008 if lower_only else 0.024)
        bm = new_bm()
        spots = [y_bot] if lower_only else [y_bot, y_top]
        for y in spots:
            centre = plane.at(xc * c, y)
            for offset in (-0.012, 0.012):                 # two plates, one each side of the spar web
                box(bm, (0.07, 0.006, 0.034), center=centre + plane.u * offset)
            bolt(bm, centre - plane.u * 0.022, plane.u, 0.008, 0.044)
        return part(ctx, name, bm, grp, grp, label_en, label_ar, "steel", status="poh", ref=ref, outside=lower_only)
    fitting(f"{grp}.spar_fitting_front", A.CABIN_SIDE_X + 0.012, A.FRONT_SPAR_XC, False,
            f"Front spar wing-to-fuselage fitting, {where_en}", f"تجهيزة ربط العارضة الأمامية بجسم الطائرة، {where_ar}", "p.7-3")
    fitting(f"{grp}.spar_fitting_rear", A.CABIN_SIDE_X + 0.012, A.REAR_SPAR_XC, False,
            f"Rear spar wing-to-fuselage fitting, {where_en}", f"تجهيزة ربط العارضة الخلفية بجسم الطائرة، {where_ar}", "p.7-3")
    fitting(f"{grp}.strut_fitting", A.STRUT_TOP_X, A.FRONT_SPAR_XC, True,
            f"Wing-to-strut fitting on the front spar, {where_en}", f"تجهيزة ربط الدعامة بالعارضة الأمامية، {where_ar}", "p.7-3")


def build(ctx):
    build_side(ctx, 1)
    build_side(ctx, -1)
