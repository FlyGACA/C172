"""Fuselage structure: frames, door posts, carry-through spars, floor structure and stringers (POH p.7-3).

"The construction of the fuselage is a conventional formed sheet metal bulkhead, stringer, and skin
design referred to as semimonocoque. Major items of structure are the front and rear carry-through
spars to which the wings are attached, a bulkhead and forgings for main landing gear attachment at
the base of the rear door posts, and a bulkhead with attaching plates at the base of the forward door
posts for the lower attachment of the wing struts. Four engine mount stringers are also attached to
the forward door posts and extend forward to the firewall."

What is from where:
  poh        the members named above, and the stations of the rear doorpost bulkhead (65.3), the aft
             cabin bulkhead (108) and the end of the aft baggage area (142), POH Fig 6-4
  estimated  the other frame stations, the number and position of the stringers, every section and gauge.
Frames stand square to the fuselage reference line, so they lean back in the build frame
(units.cessna_fs). Everything is kept behind the inside face of the skin as it is modelled.
"""
import math

from mathutils import Vector

from .. import units as U
from ..units import IN, fs, wl
from .. import airframe as A
from ..profiles import interp_pchip
from . import geom2d
from . import lanes
from .common import Plane, sheet, wall, strip, extrude_along, rect_section, hat_section, angle_section, bolt, part, new_bm, box, X, Z

SKIN = 0.016                 # inside face of the skin as modelled, measured from the outer surface (m)
KEEL_X = 0.20                # the two keel beams stand this far from the centreline
POST_HALF_WIDTH = 0.032      # a door post is a channel this wide each way from its centre line, fore and aft
POST_DEPTH = 0.0135          # and this deep, from the skin to the cabin lining
POST_SHIFT = 0.85            # runs in a post lie on its centre line and this far (in) ahead of and behind it
SEAT_RAIL_FS = (23.5, 56.0)  # the front seat rails: long enough for the seat travel of POH Figure 6-3 (occupant at station 34 to 46)
LEAN = math.tan(math.radians(U.FRL_PITCH_DEG))
FLOOR_Z = A.FLOOR_Z          # centre plane of the cabin floor panel under the seats (airframe.floor_z)

# Ring frames aft of the cabin: handbook station, depth of the ring (m), English and Arabic name.
FRAMES = [
    (108.0, 0.012, "Aft cabin bulkhead frame (station 108)", "إطار الحاجز الخلفي للمقصورة (المحطة 108)", "poh", "p.6-8 (Fig 6-4)"),
    (124.0, 0.030, "Tailcone frame, station 124", "إطار مخروط الذيل، المحطة 124", "estimated", ""),
    (142.0, 0.030, "Frame at the end of the aft baggage area (station 142)", "إطار نهاية منطقة الأمتعة الخلفية (المحطة 142)", "poh", "p.6-8 (Fig 6-4)"),
    (156.0, 0.030, "Tailcone frame, station 156", "إطار مخروط الذيل، المحطة 156", "estimated", ""),
    (172.0, 0.028, "Tailcone frame, station 172", "إطار مخروط الذيل، المحطة 172", "estimated", ""),
    (188.7, 0.026, "Tailcone frame, station 188.7", "إطار مخروط الذيل، المحطة 188.7", "estimated", ""),
    (209.0, 0.024, "Tailcone frame at the stabiliser front spar (station 209)", "إطار مخروط الذيل عند العارضة الأمامية للمثبت الأفقي (المحطة 209)", "estimated", ""),
]


# Openings in the last frame: (x, z, radius) for the elevator push-pull tube and the two rudder cables (controls.py).
TAIL_END_PASSAGES = [(0.0, 1.2285, 0.014), (0.040, 1.175, 0.007), (-0.040, 1.175, 0.007)]


def section_point(station, angle, inset=0.0):
    """Point of the hull section at a build station and a section angle (radians: 0 = left side,
    pi/2 = top, -pi/2 = bottom), moved `inset` metres inward along the normal of the section."""
    w, zb, zt, zc, nt, nb = interp_pchip(A.FUS_TABLE, station)

    def raw(a):
        c, s = math.cos(a), math.sin(a)
        n = nt if s >= 0 else nb
        h = (zt - zc) if s >= 0 else (zc - zb)
        return w * math.copysign(abs(c) ** (2 / n), c), zc + h * math.copysign(abs(s) ** (2 / n), s)

    x, z = raw(angle)
    if inset:
        x0, z0 = raw(angle - 0.02); x1, z1 = raw(angle + 0.02)
        tx, tz = x1 - x0, z1 - z0
        length = math.hypot(tx, tz) or 1e-9
        x += -tz / length * inset                     # the section runs anticlockwise: its inward normal is to the left
        z += tx / length * inset
    return Vector((x, fs(station), z))


def leaned_station(handbook_station, z):
    """Build-frame station of a handbook station at build-frame height z (m)."""
    return U.cessna_fs(handbook_station, (z - U.GROUND_Z) / IN)


def frame_outline(handbook_station, inset, count=56):
    """Outline of a leaned frame as 3D points, and the plane it lies in."""
    reference_z = wl(U.FRL_PIVOT_WL)
    cos_lean = 1 / math.hypot(1.0, LEAN)
    plane = Plane((0, fs(handbook_station), reference_z), X, (0, LEAN * cos_lean, cos_lean))
    points = []
    for i in range(count):
        angle = -math.pi / 2 + 2 * math.pi * i / count
        station = handbook_station
        for _ in range(3):                             # the station of a point depends on its height
            p = section_point(min(max(station, 0.0), A.FUS_END_FS), angle, inset)
            station = leaned_station(handbook_station, p.z)
        points.append(p)
    flat = [(p.x, (p.z - reference_z) / cos_lean) for p in points]
    return plane, flat


def ring_frame(ctx, handbook_station, depth, label_en, label_ar, status, ref):
    plane, outer = frame_outline(handbook_station, SKIN + 0.001)
    inner = geom2d.inset(outer, depth)
    bm = new_bm()
    sheet(bm, plane, outer, 0.001, [inner], offset=-0.0005)
    wall(bm, plane, outer, 0.001, 0.0, -0.014, closed=True, inward=True)        # flange under the skin, turned aft
    name = f"AIRFRAME.frame_fs{int(round(handbook_station)):03d}"
    tags = dict(ref=ref) if ref else {}
    return part(ctx, name, bm, "AIRFRAME", "AIRFRAME", label_en, label_ar, "bare_alu", status=status, inside="fuselage",
                station_in=handbook_station, pivot=plane.at(0, (wl(40) - plane.origin.z)),
                note="Formed sheet-metal frame (POH p.7-3); it stands square to the fuselage reference line, so it leans back in this model", **tags)


def post_station(which, water):
    """Station (in) of the centre line of a door post ("fwd" or "aft") at a water line (in)."""
    door = A.DOOR
    if which == "fwd":
        low, high = (door[0][0] - 1.4, door[0][1]), (door[3][0] - 1.4, door[3][1] + 4.5)
    else:
        low, high = (door[1][0] + 1.4, door[1][1]), (door[2][0] + 1.4, door[2][1] + 3.0)
    return low[0] + (high[0] - low[0]) * (water - low[1]) / (high[1] - low[1])


def post_point(which, side, water, shift=0.0, inset=None):
    """Point on the centre line of a door post, optionally shifted fore or aft (in): cables and pipes run up the posts."""
    return side_point(post_station(which, water) + shift, water, side, SKIN + 0.008 if inset is None else inset)


def side_point(station, water, side, inset):
    """Point on the hull side at (FS, WL), `inset` metres inside the outer surface."""
    z = wl(water)
    return Vector((side * (A.fus_half_width_at(station, z) - inset), fs(station), z))


def floor_frame(ctx, name, station, label_en, label_ar, status="estimated", ref="", top_z=None, lean=True):
    """Under-floor bulkhead: the part of a frame below the cabin floor, with a hole for every cable
    and pipe that runs past it (lanes.py) and lightening holes where there is room left."""
    if top_z is None:
        top_z = A.floor_z(station) - 0.02
    points = []
    count = 64
    for i in range(count + 1):
        angle = -math.pi + math.pi * i / count           # right side, round the bottom, to the left side
        st = station
        for _ in range(3):
            p = section_point(st, angle, SKIN + 0.001)
            st = leaned_station(station, p.z) if lean else station
        if p.z <= top_z:
            points.append(p)
    if len(points) < 3:
        return None
    y_top = fs(leaned_station(station, top_z)) if lean else fs(station)
    left, right = points[-1], points[0]
    outline3d = list(points)
    if top_z - left.z > 0.002:
        outline3d.append(Vector((left.x, y_top, top_z)))
    if top_z - right.z > 0.002:
        outline3d.append(Vector((right.x, y_top, top_z)))
    cos_lean = 1 / math.hypot(1.0, LEAN) if lean else 1.0
    reference_z = wl(U.FRL_PIVOT_WL)
    plane = Plane((0, fs(station), reference_z), X, (0, (LEAN if lean else 0.0) * cos_lean, cos_lean))
    flat = [(p.x, (p.z - reference_z) / cos_lean) for p in outline3d]
    half = max(abs(p[0]) for p in flat)
    low = min(p[1] for p in flat); high = max(p[1] for p in flat)
    runs = [(x, (z - reference_z) / cos_lean, lanes.HOLE) for x, z in lanes.crossing(station)]
    runs = [(x, y, r) for x, y, r in runs if geom2d.inside((x, y - r - 0.004), flat) and y + r + 0.004 < high]
    lightening = []
    radius = min(0.045, (high - low) / 2 - 0.024)
    if radius > 0.018:
        lightening = [(cx, high - 0.022 - radius, radius) for cx in (-half * 0.52, 0.0, half * 0.52)]
        lightening = geom2d.clear_of(lightening, runs, 0.005)
        runs = [run for run in runs if not any(math.hypot(run[0] - cx, run[1] - cy) + run[2] < r for cx, cy, r in lightening)]
    holes = [geom2d.circle(cx, cy, r, 16) for cx, cy, r in lightening] + [geom2d.circle(cx, cy, r, 10) for cx, cy, r in runs]
    bm = new_bm()
    sheet(bm, plane, flat, 0.0012, holes, offset=-0.0006)
    tags = dict(ref=ref) if ref else {}
    return part(ctx, name, bm, "AIRFRAME", "AIRFRAME", label_en, label_ar, "bare_alu", status=status, inside="fuselage", station_in=station, **tags)


def build(ctx):
    # ---- ring frames aft of the cabin, and the last frame, which carries the rudder
    for station, depth, en, ar, status, ref in FRAMES:
        ring_frame(ctx, station, depth, en, ar, status, ref)
    end = A.FUS_END_FS - 1.0
    w, zb, zt, zc, nt, nb = interp_pchip(A.FUS_TABLE, end)
    plane = Plane((0, fs(end), 0), X, Z)
    outline = [(p.x, p.z) for p in (section_point(end, -math.pi / 2 + 2 * math.pi * i / 40, SKIN * 0.6) for i in range(40))]
    bm = new_bm()
    passages = [geom2d.circle(x, z, r, 10) for x, z, r in TAIL_END_PASSAGES]
    sheet(bm, plane, outline, 0.002, passages, offset=-0.001)
    part(ctx, "AIRFRAME.frame_tail_end", bm, "AIRFRAME", "AIRFRAME", "Last tailcone frame (carries the rudder hinges and the stabiliser rear spar)",
         "الإطار الأخير لمخروط الذيل (يحمل مفصلات الدفة والعارضة الخلفية للمثبت الأفقي)", "bare_alu", status="estimated", inside="fuselage", station_in=end)

    # ---- door posts: channels along the edges of the door opening, from the sill to the roof. The web lies
    # on the skin and the flanges stand inward as far as the cabin lining; pipes, cables and wires run in
    # the channel side by side (POST_SHIFT), each on the side from which it enters and leaves.
    door = A.DOOR
    posts = [("fwd", (door[0][0] - 1.4, door[0][1]), (door[3][0] - 1.4, door[3][1] + 4.5), "Forward door post", "قائم الباب الأمامي"),
             ("aft", (door[1][0] + 1.4, door[1][1]), (door[2][0] + 1.4, door[2][1] + 3.0), "Rear door post", "قائم الباب الخلفي")]
    for side, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if side > 0 else ("right", "الأيمن")
        for key, low, high, en, ar in posts:
            path, inward = [], []
            for i in range(9):
                t = i / 8
                station = low[0] + (high[0] - low[0]) * t
                water = low[1] + (high[1] - low[1]) * t
                path.append(side_point(station, water, side, SKIN + 0.0005))
                inward.append(Vector((-side, 0, 0)))
            bm = new_bm()
            w, d, t = POST_HALF_WIDTH, POST_DEPTH, 0.0015
            extrude_along(bm, path, [(-w, 0), (w, 0), (w, d), (w - t, d), (w - t, t), (-w + t, t), (-w + t, d), (-w, d)], lambda i: inward[i])
            part(ctx, f"AIRFRAME.door_post_{key}_{S}", bm, "AIRFRAME", "AIRFRAME", f"{en}, {where_en}", f"{ar} {where_ar}", "bare_alu",
                 status="poh", ref="p.7-3", inside="fuselage",
                 note="The door posts are named in the POH; their line follows the door opening of the manufacturer's side view, the section is representative")

    # ---- carry-through spars: the wing spars continued across the cabin roof
    for key, xc, en, ar in (("front", A.FRONT_SPAR_XC, "Front carry-through spar", "العارضة الأمامية العابرة للمقصورة"),
                            ("rear", A.REAR_SPAR_XC, "Rear carry-through spar", "العارضة الخلفية العابرة للمقصورة")):
        top = A.wing_surface_point(A.CABIN_SIDE_X, 1, xc, True)
        bottom = A.wing_surface_point(A.CABIN_SIDE_X, 1, xc, False)
        station = top.y / IN + U.FS_ORIGIN
        roof = A.fus_top_z(station) - SKIN - 0.004
        high = min(top.z - 0.004, roof)
        low = bottom.z + 0.004
        mid_y = 0.5 * (top.y + bottom.y)
        half = A.CABIN_SIDE_X + 0.02
        bm = new_bm()
        web = [Vector((-half, mid_y, high)), Vector((half, mid_y, high))]
        strip(bm, web, [p + Vector((0, 0, low - high)) for p in web], Vector((0, 0.003, 0)))
        for z, sign in ((high, -1), (low, 1)):
            edge = [Vector((-half, mid_y - 0.03, z)), Vector((half, mid_y - 0.03, z))]
            strip(bm, edge, [p + Vector((0, 0.063, 0)) for p in edge], Vector((0, 0, sign * 0.004)))
        part(ctx, f"AIRFRAME.carry_through_{key}", bm, "AIRFRAME", "AIRFRAME", en, ar, "bare_alu", status="poh", ref="p.7-3",
             note="The wings attach to the front and rear carry-through spars (POH); position from the wing spar lines, section representative")

    # ---- under-floor bulkheads
    strut_station = A.STRUT_FS[0]
    floor_frame(ctx, "AIRFRAME.floor_bulkhead_strut", strut_station, "Bulkhead at the base of the forward door posts (wing strut attachment)",
                "الحاجز عند قاعدة قائمي الباب الأماميين (ربط دعامة الجناح)", status="poh", ref="p.7-3", lean=False)
    floor_frame(ctx, "AIRFRAME.floor_bulkhead_gear", 65.3, "Bulkhead at the base of the rear door posts (main landing gear attachment)",
                "الحاجز عند قاعدة قائمي الباب الخلفيين (ربط عجلات الهبوط الرئيسية)", status="poh", ref="p.7-3; station p.6-8 (Fig 6-4)")
    for station in (8.0, 17.0, 41.0, 80.0, 95.0):
        floor_frame(ctx, f"AIRFRAME.floor_frame_fs{int(station):03d}", station, f"Under-floor frame, station {station:g}", f"إطار تحت الأرضية، المحطة {station:g}")

    # ---- strut attach plates and gear forgings
    for side, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if side > 0 else ("right", "الأيمن")
        foot = side_point(A.STRUT_FS[0], A.STRUT_FOOT_WL + 1.2, side, SKIN + 0.006)
        bm = new_bm()
        box(bm, (0.008, 0.11, 0.06), center=foot)
        box(bm, (0.008, 0.11, 0.06), center=foot + Vector((-side * 0.03, 0, 0)))
        bolt(bm, foot + Vector((side * 0.008, 0, -0.012)), Vector((-side, 0, 0)), 0.0095, 0.05)
        part(ctx, f"AIRFRAME.strut_attach_plate_{S}", bm, "AIRFRAME", "AIRFRAME", f"Wing strut attaching plates, {where_en}",
             f"صفائح ربط دعامة الجناح، {where_ar}", "steel", status="poh", ref="p.7-3")
        from ..gear import main_leg_points
        leg, _axle, attach = main_leg_points(side)
        bm = new_bm()
        for index in (0, 3):                           # inboard forging at the root of the leg, outboard one where it leaves the belly
            centre = leg[index]
            box(bm, (0.07, 0.085, 0.075), center=centre)
            bolt(bm, centre + Vector((0, -0.05, 0.02)), Vector((0, 1, 0)), 0.008, 0.10)
        part(ctx, f"AIRFRAME.gear_forging_{S}", bm, "AIRFRAME", "AIRFRAME", f"Main landing gear attach forgings, {where_en}",
             f"مسبوكات ربط ساق العجلة الرئيسية، {where_ar}", "steel", status="poh", ref="p.7-3",
             note="Forgings for main landing gear attachment at the base of the rear door posts (POH); shape representative")

    # ---- engine mount stringers: four, from the forward door posts to the firewall
    post_low, post_high = posts[0][1], posts[0][2]
    for side, S in ((1, "L"), (-1, "R")):
        for level, water, word_en, word_ar in (("upper", 49.0, "Upper", "العلوية"), ("lower", 28.5, "Lower", "السفلية")):
            t = (water - post_low[1]) / (post_high[1] - post_low[1])
            end_station = post_low[0] + (post_high[0] - post_low[0]) * t - POST_HALF_WIDTH / IN - 0.1      # up to the flange of the post
            path, inward = [], []
            for i in range(9):
                station = 0.6 + (end_station - 0.6) * i / 8
                path.append(side_point(station, water, side, SKIN + 0.001))
                inward.append(Vector((-side, 0, 0)))
            bm = new_bm()
            extrude_along(bm, path, hat_section(0.026, 0.011, 0.008, 0.0012), lambda i: -inward[i])
            part(ctx, f"AIRFRAME.engine_mount_stringer_{level}_{S}", bm, "AIRFRAME", "AIRFRAME",
                 f"{word_en} engine mount stringer, {'left' if side > 0 else 'right'}", f"دعامة حامل المحرك الطولية {word_ar}، {'اليسرى' if side > 0 else 'اليمنى'}",
                 "bare_alu", status="poh", ref="p.7-3", inside="fuselage",
                 note="Four engine mount stringers run from the forward door posts to the firewall (POH); height and section representative")

    # ---- tailcone stringers
    start, finish = 118.0, A.FUS_END_FS - 1.5
    stations = [start + (finish - start) * i / 14 for i in range(15)]
    angles = [(62, "upper"), (20, "upper side"), (-24, "lower side"), (-64, "lower")]
    number = 0
    for side, S in ((1, "L"), (-1, "R")):
        for degrees, _where in angles:
            number += 1
            angle = math.radians(degrees) if side > 0 else math.pi - math.radians(degrees)
            path = [section_point(st, angle, SKIN + 0.001) for st in stations]
            outward = []
            for st in stations:
                outer = section_point(st, angle, 0.0); inner = section_point(st, angle, 0.02)
                outward.append((outer - inner).normalized())
            bm = new_bm()
            extrude_along(bm, path, hat_section(0.022, 0.010, 0.009, 0.001), lambda i: outward[i])
            part(ctx, f"AIRFRAME.stringer_tail_{abs(degrees):02d}{'U' if degrees > 0 else 'D'}_{S}", bm, "AIRFRAME", "AIRFRAME",
                 f"Tailcone stringer ({_where}, {'left' if side > 0 else 'right'})", f"دعامة طولية لمخروط الذيل ({'يسار' if side > 0 else 'يمين'})",
                 "bare_alu", status="estimated", inside="fuselage", note="Stringers are named in the POH (p.7-3); their number and position are representative")

    # ---- seat rails for the front seats, and the two keel beams under the floor
    for index, x in enumerate((0.40, 0.16, -0.16, -0.40), 1):
        bm = new_bm()
        extrude_along(bm, [Vector((x, fs(SEAT_RAIL_FS[0]), FLOOR_Z + 0.015)), Vector((x, fs(SEAT_RAIL_FS[1]), FLOOR_Z + 0.015))],
                      [(-0.016, 0), (0.016, 0), (0.016, 0.004), (0.005, 0.004), (0.005, 0.014), (0.012, 0.014), (0.012, 0.018), (-0.012, 0.018),
                       (-0.012, 0.014), (-0.005, 0.014), (-0.005, 0.004), (-0.016, 0.004)], Z)
        part(ctx, f"AIRFRAME.seat_rail_{index}", bm, "AIRFRAME", "AIRFRAME", "Front seat rail", "سكة المقعد الأمامي", "bare_alu", status="estimated",
             inside="fuselage", assembly="seats", note="The front seats may be moved forward or aft (POH p.7-11): they run on two rails each; the rails are long enough for the "
                                                       "occupant's centre of gravity to range from station 34 to 46 (POH Figure 6-3); section representative")
    for side, S in ((1, "L"), (-1, "R")):
        x = side * KEEL_X
        stations = [4.0 + (104.0 - 4.0) * i / 40 for i in range(41)]
        top = [(fs(st), lanes.floor_underside(st) - 0.002) for st in stations]
        bottom = [(fs(st), A.fus_surface_z(st, abs(x)) + SKIN + 0.002) for st in stations]
        outline = bottom + list(reversed(top))
        plane = Plane((x, 0, 0), (0, 1, 0), (0, 0, 1))
        runs = [(fs(station), z, lanes.HOLE) for station, z in lanes.ACROSS.values()]
        frames = [fs(st) for st in (8.0, 17.0, A.STRUT_FS[0], 41.0, 65.3, 80.0, 95.0)]
        lightening = []
        for hole in geom2d.lightening_holes(outline, fs(6.0), fs(102.0), 16, 0.026, max_radius=0.03, segments=14):
            cx = sum(p[0] for p in hole) / len(hole); cy = sum(p[1] for p in hole) / len(hole)
            radius = max(p[0] for p in hole) - cx
            if all(abs(cx - y) > radius + 0.012 for y in frames):          # not where a bulkhead joins the beam
                lightening.append((cx, cy, radius))
        lightening = geom2d.clear_of(lightening, runs, 0.005)
        runs = [run for run in runs if not any(math.hypot(run[0] - cx, run[1] - cy) + run[2] < r for cx, cy, r in lightening)]
        holes = [geom2d.circle(cx, cy, r, 14) for cx, cy, r in lightening] + [geom2d.circle(cx, cy, r, 10) for cx, cy, r in runs]
        bm = new_bm()
        sheet(bm, plane, outline, 0.0015, holes, offset=-0.00075)
        part(ctx, f"AIRFRAME.keel_beam_{S}", bm, "AIRFRAME", "AIRFRAME", f"Under-floor keel beam, {'left' if side > 0 else 'right'}",
             f"العارضة الطولية تحت الأرضية، {'اليسرى' if side > 0 else 'اليمنى'}", "bare_alu", status="estimated", inside="fuselage",
             note="Representative: a web between the belly and the floor with lightening holes, and an opening for each pipe and cable that crosses the cabin")
