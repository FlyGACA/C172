"""Fasteners: rivet rows, screws and bolts, and a kit of the standard hardware (detail level 2).

The skins are riveted to the ribs, spars, frames and stringers that the structure packs build, so
every rivet row here lies over one of those members: one row is one part, named after the member.
Screws hold what comes off for inspection (fuel tank covers, wing tips, inspection plates, the
cowling, the instruments); bolts join the major assemblies (wing struts, engine mount, propeller,
wheels).

HARDWARE.* is a kit: one specimen of each standard part (rivets, bolt, nuts, washer, screw, cotter
pin, turnbuckle, pulley, rod end, hinge, cowl fastener), built at its real size and kept out of
sight beside the aircraft, so that it can be drawn on its own (part.py render --part HARDWARE.bolt).

What is from where:
  estimated  everything. The POH does not show fasteners. Rows follow the modelled structure at a
             representative pitch; the real rivet patterns are in the manufacturer's structural
             repair manual. The kit shows the kinds of standard hardware used on light aircraft of
             this period, with representative sizes.
Level 2 parts are hidden in the saved scene and are not in the web models; a figure asks for them
with "detail": 2, the part tool by naming them.
"""
import math

import bpy
from mathutils import Vector

from .. import units as U
from ..units import IN, fs, wl
from .. import airframe as A
from .. import powerplant as P
from ..profiles import interp_pchip
from ..shapes import revolve
from . import structure_fuselage as SF
from . import structure_tail as ST
from . import structure_wing as SW
from .common import dome, disc, rod, bolt, hex_prism, bar, part, new_bm, box, X, Y, Z

LEVEL = 2
SYS = "FASTENERS"
RIVET_R, RIVET_H = 0.0032, 0.0013          # universal-head rivet head as drawn (1/8 in rivet)
SCREW_R, SCREW_H = 0.0042, 0.0017
NOTE_RIVETS = "Rivets at a representative pitch over this member; the real pattern is in the structural repair manual"


def add(ctx, name, bm, group, en, ar, mat="bare_alu", count=None, smooth=False, **tags):
    tags.setdefault("assembly", "fasteners")
    if count is not None:
        tags["count"] = count
    return part(ctx, name, bm, group, SYS, en, ar, mat, detail=2, status="estimated", smooth=smooth, **tags)


def rivets(bm, spots, radius=RIVET_R, height=RIVET_H, sides=6, rings=0):
    """A head at every (point, outward normal)."""
    for point, normal in spots:
        dome(bm, point, normal, radius, height, sides=sides, rings=rings)
    return len(spots)


def steps(a, b, pitch):
    """Positions from a to b, evenly spaced as near to `pitch` as divides the distance."""
    count = max(1, int(round(abs(b - a) / pitch)))
    return [a + (b - a) * i / count for i in range(count + 1)]


# ----------------------------------------------------------------------------- surfaces

def wing_spot(xabs, side, xc, upper, af=None):
    """Point on the wing skin and its outward normal."""
    af = af or A.wing_airfoil(xabs)
    c = A.wing_chord(xabs)
    d = 0.004
    p = A.wing_point(xabs, side, xc, A.airfoil_y(af, xc, upper))
    a = A.wing_point(xabs, side, max(0.0, xc - d), A.airfoil_y(af, max(0.0, xc - d), upper))
    b = A.wing_point(xabs, side, min(1.0, xc + d), A.airfoil_y(af, min(1.0, xc + d), upper))
    span = A.wing_point(xabs + 0.02, side, xc, A.airfoil_y(af, xc, upper)) - A.wing_point(xabs - 0.02, side, xc, A.airfoil_y(af, xc, upper))
    n = (b - a).cross(span).normalized()
    up = A.wing_point(xabs, side, xc, 1.0) - A.wing_point(xabs, side, xc, 0.0)
    if (n.dot(up) > 0) != upper:
        n = -n
    return p, n, c


def hull_spot(table, station, angle, lean_from=None):
    """Point on the fuselage or cowl skin at a section angle, and its outward normal. With lean_from
    (a handbook station) the point lies on the frame that stands square to the fuselage reference line."""
    def at(st, inset):
        w, zb, zt, zc, nt, nb = interp_pchip(table, st)
        c, s = math.cos(angle), math.sin(angle)
        n = nt if s >= 0 else nb
        h = (zt - zc) if s >= 0 else (zc - zb)
        x, z = w * math.copysign(abs(c) ** (2 / n), c), zc + h * math.copysign(abs(s) ** (2 / n), s)
        if inset:
            c2, s2 = math.cos(angle + 0.02), math.sin(angle + 0.02)
            c1, s1 = math.cos(angle - 0.02), math.sin(angle - 0.02)
            n2, h2 = (nt, zt - zc) if s2 >= 0 else (nb, zc - zb)
            n1, h1 = (nt, zt - zc) if s1 >= 0 else (nb, zc - zb)
            tx = w * math.copysign(abs(c2) ** (2 / n2), c2) - w * math.copysign(abs(c1) ** (2 / n1), c1)
            tz = h2 * math.copysign(abs(s2) ** (2 / n2), s2) - h1 * math.copysign(abs(s1) ** (2 / n1), s1)
            length = math.hypot(tx, tz) or 1e-9
            x += -tz / length * inset
            z += tx / length * inset
        return Vector((x, fs(st), z))

    st = station
    if lean_from is not None:
        for _ in range(3):
            st = min(max(SF.leaned_station(lean_from, at(st, 0.0).z), table[0][0]), table[-1][0])
    outer = at(st, 0.0)
    inner = at(st, 0.012)
    return outer, (outer - inner).normalized()


def tail_thickness(xabs, xc):
    return A.airfoil_y(A.AF_TAIL, xc, True) * A.stab_chord(xabs)


def stab_spot(xabs, side, xc, upper):
    c = A.stab_chord(xabs)
    t = tail_thickness(xabs, xc)
    return Vector((side * xabs, A.stab_te_y(xabs) - c + xc * c, A.STAB_Z + (t if upper else -t))), (Z if upper else -Z)


# ----------------------------------------------------------------------------- packs

def build(ctx):
    scene = bpy.data.objects
    build_wing(ctx, 1)
    build_wing(ctx, -1)
    build_fuselage(ctx)
    build_tail(ctx)
    build_screws(ctx, scene)
    build_bolts(ctx, scene)
    build_kit(ctx)


def build_wing(ctx, side):
    S = "L" if side > 0 else "R"
    grp = "WING_" + S
    where_ar = "الأيسر" if side > 0 else "الأيمن"
    stations = [s * IN for s in SW.RIB_STATIONS]

    def chord_row(name, xabs, x0, x1, upper, en, ar):
        af = A.wing_airfoil(xabs)
        c = A.wing_chord(xabs)
        spots = [wing_spot(xabs, side, xc, upper, af)[:2] for xc in steps(x0, x1, 0.032 / c)]
        bm = new_bm()
        add(ctx, name, bm, grp, en, ar, count=rivets(bm, spots), outside=True, note=NOTE_RIVETS)

    def span_row(name, xc_fn, x_from, x_to, upper, en, ar, pitch=0.03):
        spots = [wing_spot(x, side, xc_fn(x), upper)[:2] for x in steps(x_from, x_to, pitch)]
        bm = new_bm()
        add(ctx, name, bm, grp, en, ar, count=rivets(bm, spots), outside=True, note=NOTE_RIVETS)

    for index, (station, x) in enumerate(zip(SW.RIB_STATIONS, stations)):
        tag = f"ws{int(round(station)):03d}"
        aft = 0.985 if station >= SW.RIB_STATIONS[-1] - 1e-6 else SW.cove_xc(x) - 0.01
        for upper, word_en, word_ar in ((True, "upper", "العلوي"), (False, "lower", "السفلي")):
            chord_row(f"{grp}.rivets_rib_{tag}_{word_en}", x, 0.012, aft, upper, f"Rivet row: {word_en} skin to the rib at wing station {station:g}",
                      f"صف برشام: الجلد {word_ar} على الضلع عند محطة الجناح {station:g}")
        if index + 1 < len(SW.RIB_STATIONS):
            middle = 0.5 * (station + SW.RIB_STATIONS[index + 1])
            for upper, word_en, word_ar in ((True, "upper", "العلوي"), (False, "lower", "السفلي")):
                chord_row(f"{grp}.rivets_nose_rib_ws{int(round(middle)):03d}_{word_en}", middle * IN, 0.015, A.FRONT_SPAR_XC - 0.012, upper,
                          f"Rivet row: {word_en} skin to the intermediate nose rib at wing station {middle:g}",
                          f"صف برشام: الجلد {word_ar} على ضلع المقدمة الوسيط عند محطة الجناح {middle:g}")
    root, tip, rear_end = A.CABIN_SIDE_X + 0.06, stations[-1], SW.REAR_SPAR_END * IN
    for upper, word_en, word_ar in ((True, "upper", "العلوي"), (False, "lower", "السفلي")):
        span_row(f"{grp}.rivets_front_spar_{word_en}", lambda x: A.FRONT_SPAR_XC, root, tip, upper, f"Rivet row: {word_en} skin to the front spar",
                 f"صف برشام: الجلد {word_ar} على العارضة الأمامية")
        span_row(f"{grp}.rivets_rear_spar_{word_en}", lambda x: A.REAR_SPAR_XC, root, rear_end, upper, f"Rivet row: {word_en} skin to the rear spar",
                 f"صف برشام: الجلد {word_ar} على العارضة الخلفية")
        span_row(f"{grp}.rivets_aileron_spar_{word_en}", lambda x: SW.cove_xc(x) - 0.012, rear_end + 0.03, tip, upper, f"Rivet row: {word_en} skin to the aileron hinge spar",
                 f"صف برشام: الجلد {word_ar} على عارضة مفصلات الجنيح")
    for number, (xc, upper, x_from, x_to) in enumerate([(0.30, True, 55.62, 190.0), (0.47, True, 55.62, 100.5), (0.34, False, 55.62, 190.0), (0.50, False, 55.62, 100.5)], 1):
        span_row(f"{grp}.rivets_stringer_{'upper' if upper else 'lower'}_{1 if xc < 0.4 else 2}", lambda x, xc=xc: xc, x_from * IN + 0.02, x_to * IN - 0.02, upper,
                 f"Rivet row: {'upper' if upper else 'lower'} skin to a stringer", f"صف برشام: الجلد {'العلوي' if upper else 'السفلي'} على دعامة طولية", pitch=0.04)

    # screws: the cover over the fuel tank bay, the wing tip, inspection plates under the wing
    bay = (SW.TANK_BAY[0] + 0.6, SW.TANK_BAY[1] - 0.6)
    spots = []
    for station in bay:
        c = A.wing_chord(station * IN)
        spots += [wing_spot(station * IN, side, xc, True)[:2] for xc in steps(0.17, 0.63, 0.05 / c)]
    for xc in (0.17, 0.63):
        spots += [wing_spot(x, side, xc, True)[:2] for x in steps(bay[0] * IN, bay[1] * IN, 0.05)[1:-1]]
    bm = new_bm()
    add(ctx, f"{grp}.fuel_tank_cover_screws", bm, grp, "Screws of the cover over the fuel tank bay", f"براغي غطاء حجرة خزان الوقود (الجناح {where_ar})", "steel",
        count=rivets(bm, spots, SCREW_R, SCREW_H, 8, 1), outside=True, note="The tank lies under a removable part of the upper skin; the screw pattern is representative")
    x_tip = A.TIP_START - 0.012
    c = A.wing_chord(x_tip)
    spots = [wing_spot(x_tip, side, xc, upper)[:2] for upper in (True, False) for xc in steps(0.04, 0.80, 0.06 / c)]
    bm = new_bm()
    add(ctx, f"{grp}.wing_tip_screws", bm, grp, "Wing tip attaching screws", f"براغي تثبيت طرف الجناح {where_ar}", "steel",
        count=rivets(bm, spots, SCREW_R, SCREW_H, 8, 1), outside=True, note="Representative")
    for station, xc, what_en, what_ar in ((100.0, 0.42, "wing structure", "هيكل الجناح"), (SW.AILERON_BELLCRANK_BL, 0.70, "aileron bellcrank", "الذراع المرفقي للجنيح"),
                                          (172.0, 0.42, "wing structure", "هيكل الجناح"), (64.0, 0.709, "flap drive pulley", "بكرة تحريك القلاب")):
        centre, normal, _c = wing_spot(station * IN, side, xc, False)
        spanwise = (wing_spot(station * IN + 0.05, side, xc, False)[0] - centre).normalized()
        chordwise = normal.cross(spanwise).normalized()
        bm = new_bm()
        disc(bm, centre + normal * 0.0004, normal, 0.062, 0.0012, segs=28)
        spots = [(centre + (spanwise * math.cos(a) + chordwise * math.sin(a)) * 0.053 + normal * 0.001, normal) for a in (math.pi / 3 * k for k in range(6))]
        rivets(bm, spots, SCREW_R, SCREW_H, 8, 1)
        add(ctx, f"{grp}.inspection_plate_ws{int(round(station)):03d}", bm, grp, f"Inspection plate under the wing at station {station:g} ({what_en})",
            f"لوحة فحص تحت الجناح عند المحطة {station:g} ({what_ar})", "bare_alu", count=6, outside=True,
            note="Round plates under the wing give access to what lies inside; number and position representative")


def build_fuselage(ctx):
    grp = "AIRFRAME"
    table = A.FUS_TABLE
    pitch = 0.035

    def ring(name, handbook_station, a0, a1, keep, en, ar, lean=True):
        w, zb, zt, zc, _nt, _nb = interp_pchip(table, min(handbook_station, A.FUS_END_FS))
        radius = 0.5 * (w + 0.5 * (zt - zb))
        count = max(8, int(abs(a1 - a0) * radius / pitch))
        spots = []
        for i in range(count):
            spot = hull_spot(table, handbook_station, a0 + (a1 - a0) * (i + 0.5) / count, handbook_station if lean else None)
            if keep(spot[0]):
                spots.append(spot)
        if spots:
            bm = new_bm()
            add(ctx, name, bm, grp, en, ar, count=rivets(bm, spots), note=NOTE_RIVETS)

    for station, _depth, en, ar, _status, _ref in SF.FRAMES:
        below_window = (lambda p: p.z < wl(48.5)) if station < 120 else (lambda p: not (p.z > wl(42) and abs(p.x) < 0.05))
        ring(f"AIRFRAME.rivets_frame_fs{int(round(station)):03d}", station, -math.pi / 2, 1.5 * math.pi, below_window,
             f"Rivet row: skin to the frame at station {station:g}", f"صف برشام: الجلد على الإطار عند المحطة {station:g}")
    for station in (8.0, 17.0, A.STRUT_FS[0], 41.0, 65.3, 80.0, 95.0):
        ring(f"AIRFRAME.rivets_floor_frame_fs{int(round(station)):03d}", station, -math.pi, 0.0, lambda p, st=station: p.z < A.floor_z(st) - 0.03,
             f"Rivet row: belly skin to the under-floor frame at station {station:g}", f"صف برشام: جلد البطن على الإطار تحت الأرضية عند المحطة {station:g}",
             lean=abs(station - A.STRUT_FS[0]) > 1e-6)

    def line(name, spots, en, ar):
        bm = new_bm()
        add(ctx, name, bm, grp, en, ar, count=rivets(bm, spots), note=NOTE_RIVETS)

    for side, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "يسار") if side > 0 else ("right", "يمين")
        for degrees, _where in ((62, "upper"), (20, "upper side"), (-24, "lower side"), (-64, "lower")):
            angle = math.radians(degrees) if side > 0 else math.pi - math.radians(degrees)
            spots = [hull_spot(table, st, angle) for st in steps(119.0, A.FUS_END_FS - 2.0, pitch / IN)]
            line(f"AIRFRAME.rivets_stringer_tail_{abs(degrees):02d}{'U' if degrees > 0 else 'D'}_{S}", spots,
                 f"Rivet row: skin to a tailcone stringer ({where_en})", f"صف برشام: الجلد على دعامة طولية لمخروط الذيل ({where_ar})")
        spots = []
        for st in steps(5.0, 103.0, pitch / IN):
            x = side * SF.KEEL_X
            centre = Vector((x, fs(st), A.fus_surface_z(st, abs(x))))
            across = Vector((x + 0.01, fs(st), A.fus_surface_z(st, abs(x) + 0.01 * side))) - Vector((x - 0.01, fs(st), A.fus_surface_z(st, abs(x) - 0.01 * side)))
            normal = across.cross(Y).normalized()
            spots.append((centre, normal if normal.z < 0 else -normal))
        line(f"AIRFRAME.rivets_keel_beam_{S}", spots, f"Rivet row: belly skin to the {where_en} keel beam", f"صف برشام: جلد البطن على العارضة الطولية ({where_ar})")
        for which, word_en, word_ar in (("fwd", "forward", "الأمامي"), ("aft", "rear", "الخلفي")):
            spots = []
            for water in steps(27.0, 63.0, pitch / IN):
                outer = SF.post_point(which, side, water, inset=0.0)
                spots.append((outer, (outer - SF.post_point(which, side, water, inset=0.012)).normalized()))
            line(f"AIRFRAME.rivets_door_post_{which}_{S}", spots, f"Rivet row: skin to the {word_en} door post ({where_en})", f"صف برشام: الجلد على قائم الباب {word_ar} ({where_ar})")
        for level, water in (("upper", 49.0), ("lower", 28.5)):
            end = SF.post_station("fwd", water)
            spots = []
            for st in steps(1.6, end - 1.2, pitch / IN):
                outer = SF.side_point(st, water, side, 0.0)
                spots.append((outer, (outer - SF.side_point(st, water, side, 0.012)).normalized()))
            line(f"AIRFRAME.rivets_engine_mount_stringer_{level}_{S}", spots, f"Rivet row: skin to the {level} engine mount stringer ({where_en})",
                 f"صف برشام: الجلد على دعامة حامل المحرك {'العلوية' if level == 'upper' else 'السفلية'} ({where_ar})")


def build_tail(ctx):
    grp = "EMPENNAGE"
    pitch = 0.032

    def along(line, water):
        (s0, w0), (s1, w1) = line
        return s0 + (s1 - s0) * (water - w0) / (w1 - w0)

    for side, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if side > 0 else ("right", "الأيمن")
        spots = []
        for water in steps(45.0, 90.0, pitch / IN):
            station = along(A.RUD_HINGE, water) - 1.6
            spots.append((Vector((side * A.fin_half_thickness(station, water), fs(station), wl(water))), X * side))
        bm = new_bm()
        add(ctx, f"EMPENNAGE.rivets_fin_spar_{S}", bm, grp, f"Rivet row: fin skin to the fin spar ({where_en} side)", f"صف برشام: جلد المثبت الرأسي على عارضته (الجانب {where_ar})",
            count=rivets(bm, spots), note=NOTE_RIVETS)
        for key, xc_fn, word_en, word_ar in (("front", lambda x: A.STAB_SPAR_XC, "forward", "الأمامية"),
                                             ("rear", lambda x: 1 - A.elev_chord(x) / A.stab_chord(x) - 0.045, "aft", "الخلفية")):
            for upper, face_en, face_ar in ((True, "upper", "العلوي"), (False, "lower", "السفلي")):
                spots = [stab_spot(x, side, xc_fn(x), upper) for x in steps(0.13, A.STAB_END - 0.03, pitch)]
                bm = new_bm()
                add(ctx, f"EMPENNAGE.rivets_stabilizer_{key}_spar_{face_en}_{S}", bm, grp, f"Rivet row: {face_en} stabiliser skin to the {word_en} spar ({where_en})",
                    f"صف برشام: جلد المثبت الأفقي {face_ar} على العارضة {word_ar} ({where_en})", count=rivets(bm, spots), note=NOTE_RIVETS)
        for station in ST.STAB_RIBS:
            x = station * IN
            c = A.stab_chord(x)
            hinge = 1 - A.elev_chord(x) / c
            for upper, face_en, face_ar in ((True, "upper", "العلوي"), (False, "lower", "السفلي")):
                spots = [stab_spot(x, side, xc, upper) for xc in steps(0.03, hinge - 0.06, pitch / c)]
                bm = new_bm()
                add(ctx, f"EMPENNAGE.rivets_stabilizer_rib_{S}{int(station):02d}_{face_en}", bm, grp, f"Rivet row: {face_en} stabiliser skin to the rib at butt line {station:g} ({where_en})",
                    f"صف برشام: جلد المثبت الأفقي {face_ar} على الضلع {station:g} ({where_ar})", count=rivets(bm, spots), note=NOTE_RIVETS)


def build_screws(ctx, scene):
    # cowling: quarter-turn fasteners along the joint between the two halves, screws round its rear edge
    for side, S in ((1, "L"), (-1, "R")):
        spots = []
        for st in steps(-29.5, -2.5, 3.4):
            w, _zb, _zt, zc, _nt, _nb = interp_pchip(P.COWL_TABLE, st)
            spots.append((Vector((side * w, fs(st), zc)), X * side))
        bm = new_bm()
        add(ctx, f"POWERPLANT.cowl_fasteners_{S}", bm, "POWERPLANT", f"Quarter-turn fasteners joining the upper and lower cowling ({'left' if side > 0 else 'right'} side)",
            f"مثبّتات ربع اللفة بين نصفي غطاء المحرك (الجانب {'الأيسر' if side > 0 else 'الأيمن'})", "steel", count=rivets(bm, spots, 0.0065, 0.002, 10, 1),
            note="The cowling comes off for inspection; the number and position of its fasteners are representative")
    spots = [hull_spot(P.COWL_TABLE, -0.9, -math.pi / 2 + 2 * math.pi * (i + 0.5) / 26) for i in range(26)]
    bm = new_bm()
    add(ctx, "POWERPLANT.cowl_screws_aft", bm, "POWERPLANT", "Screws round the rear edge of the cowling", "براغي الحافة الخلفية لغطاء المحرك", "steel",
        count=rivets(bm, spots, SCREW_R, SCREW_H, 8, 1), note="Representative")

    # instrument mounting screws: four round each instrument, on the face of the panel
    deps = bpy.context.evaluated_depsgraph_get()
    for bezel in sorted((ob for ob in scene if ob.name.startswith("PANEL.") and ob.name.endswith(".bezel") and not ob.get("no_screws")), key=lambda ob: ob.name):
        corners = [bezel.matrix_world @ Vector(corner) for corner in bezel.evaluated_get(deps).bound_box]
        xs, ys, zs = ([c[i] for c in corners] for i in range(3))
        radius = 0.5 * (max(xs) - min(xs))
        centre = Vector((0.5 * (max(xs) + min(xs)), bezel.matrix_world.translation.y + 0.0006, 0.5 * (max(zs) + min(zs))))      # the rim stands on the face of the panel
        reach = radius * 0.79
        spots = [(centre + Vector((sx * reach, 0, sz * reach)), Y) for sx in (-1, 1) for sz in (-1, 1)]
        instrument = bezel.name.split(".")[1]
        bm = new_bm()
        add(ctx, f"PANEL.{instrument}.screws", bm, "PANEL", f"Mounting screws of the instrument ({instrument})", f"براغي تثبيت العداد ({instrument})", "black_plastic",
            count=rivets(bm, spots, 0.0034, 0.0015, 8, 1), parent=bezel, note="Each instrument is held in the panel by four screws; representative")


def build_bolts(ctx, scene):
    # wing struts: one bolt at each end
    for side, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "اليسرى") if side > 0 else ("right", "اليمنى")
        top, normal, _c = wing_spot(A.STRUT_TOP_X, side, A.FRONT_SPAR_XC, False)
        chordwise = (wing_spot(A.STRUT_TOP_X, side, A.FRONT_SPAR_XC + 0.05, False)[0] - top).normalized()
        bm = new_bm()
        bolt(bm, top + normal * 0.022 - chordwise * 0.027, chordwise, 0.0095, 0.054)
        add(ctx, f"WING_{S}.strut_bolt_upper", bm, "WING_" + S, f"Wing strut upper attach bolt ({where_en} strut to the front spar fitting)",
            f"مسمار الربط العلوي لدعامة الجناح {where_en}", "steel", count=1, outside=True, smooth=True, note="One bolt joins the strut to the wing-to-strut fitting; size representative")
        foot = SF.side_point(A.STRUT_FS[0], A.STRUT_FOOT_WL, side, -0.014)
        bm = new_bm()
        bolt(bm, foot - Y * 0.03, Y, 0.0095, 0.06)
        add(ctx, f"WING_{S}.strut_bolt_lower", bm, "WING_" + S, f"Wing strut lower attach bolt ({where_en} strut to the fuselage attaching plates)",
            f"مسمار الربط السفلي لدعامة الجناح {where_en}", "steel", count=1, outside=True, smooth=True, note="One bolt joins the strut to the attaching plates at the foot of the forward door post; size representative")

    # engine mount: four bolts through the firewall, where the mount's tubes meet it (engine.py)
    if "ENGINE.engine_mount" in scene:
        for number, (sx, dz) in enumerate(((1, 0.12), (-1, 0.12), (1, -0.40), (-1, -0.40)), 1):
            seat = Vector((sx * 0.33, fs(0.5) - 0.012, U.PROP_Z + dz))
            bm = new_bm()
            bolt(bm, seat, Y, 0.0095, 0.05)
            add(ctx, f"ENGINE.mount_bolt_{number}", bm, "ENGINE", f"Engine mount bolt {number} (mount to firewall)", f"مسمار حامل المحرك {number} (الحامل إلى جدار الحريق)", "steel",
                count=1, smooth=True, note="The engine mount is bolted to the firewall at four points; position and size representative")

    # propeller: six bolts into the crankshaft flange
    prop = scene["POWERPLANT.propeller"]
    hub = prop.matrix_world.translation.copy()
    for number in range(6):
        angle = math.pi / 3 * number + math.pi / 6
        seat = hub + Vector((math.cos(angle) * 0.057, -0.04, math.sin(angle) * 0.057))
        bm = new_bm()
        bolt(bm, seat, Y, 0.0095, 0.085, nut=False)
        add(ctx, f"POWERPLANT.propeller_bolt_{number + 1}", bm, "POWERPLANT", f"Propeller attach bolt {number + 1}", f"مسمار تثبيت المروحة {number + 1}", "steel", count=1, smooth=True,
            parent=prop, note="The fixed-pitch propeller is bolted to the crankshaft flange; six bolts and their size are representative")

    # wheels: axle nut with its cotter pin
    for name, side, width in (("GEAR.main_wheel_L", 1, U.MAIN_TYRE_W), ("GEAR.main_wheel_R", -1, U.MAIN_TYRE_W), ("GEAR.nose_wheel", 1, U.NOSE_TYRE_W)):
        tyre = scene[name + ".tyre"]
        axle = tyre.matrix_world.translation.copy()
        base = axle + X * (side * width * 0.44)
        bm = new_bm()
        rod(bm, axle + X * (side * width * 0.3), base + X * (side * 0.03), 0.011, segs=10)
        hex_prism(bm, base + X * (side * 0.004), X * side, 0.032, 0.014)
        rod(bm, base + X * (side * 0.011) - Z * 0.02, base + X * (side * 0.011) + Z * 0.02, 0.0016, segs=5)
        add(ctx, f"{name}.axle_nut", bm, "GEAR", "Axle nut with cotter pin", "صامولة المحور مع مسمار الخابور", "steel", count=1, smooth=True, parent=tyre,
            note="The wheel is held on its axle by a nut locked with a cotter pin; representative")


# ----------------------------------------------------------------------------- the hardware kit

def build_kit(ctx):
    group = ctx.group("HARDWARE", "Standard hardware (one of each kind, at its real size)", "العتاد القياسي (قطعة من كل نوع بحجمها الحقيقي)")
    group["detail"] = 2
    group["kit"] = True
    spot = [0]

    def place():
        """Where the next specimen stands: in a row behind the aircraft, out of sight until asked for."""
        spot[0] += 1
        return Vector((-0.3 + 0.04 * spot[0], fs(330.0), 0.6))

    def specimen(name, bm, en, ar, mat, origin, note):
        ob = add(ctx, name, bm, "HARDWARE", en, ar, mat, smooth=True, kit=True, pivot=origin, assembly="hardware_kit",
                 note=note + " Drawn at its real size; standard hardware of the kind used on light aircraft of this period, sizes representative")
        ob["system"] = "HARDWARE"
        return ob

    o = place()
    bm = new_bm()
    revolve(bm, [(0.0, -0.008), (0.0016, -0.008), (0.0016, 0.0), (0.0032, 0.0), (0.0029, 0.0008), (0.0018, 0.0013), (0.0, 0.0014)], axis="Z", origin=o, segs=20)
    specimen("HARDWARE.rivet_universal_head", bm, "Universal-head rivet (AN470 type)", "برشام برأس مقبّب (نوع AN470)", "bare_alu", o,
             "The rivet that joins most of the skin to the structure: the head stands proud of the skin.")
    o = place()
    bm = new_bm()
    revolve(bm, [(0.0, -0.008), (0.0016, -0.008), (0.0016, -0.0011), (0.0029, 0.0), (0.0, 0.0)], axis="Z", origin=o, segs=20)
    specimen("HARDWARE.rivet_countersunk", bm, "Countersunk (flush) rivet (AN426 type)", "برشام برأس غاطس (نوع AN426)", "bare_alu", o,
             "Used where the skin has to be smooth: the head sits flush in a countersink.")
    o = place()
    bm = new_bm()
    hex_prism(bm, o, Z, 0.0095, 0.0032)
    profile = [(0.0, 0.0), (0.0024, 0.0), (0.0024, -0.014)]
    for k in range(7):                                       # threads, drawn as grooves
        z = -0.014 - 0.0015 * k
        profile += [(0.0024, z), (0.0020, z - 0.00045), (0.0024, z - 0.0009)]
    profile += [(0.0021, -0.0255), (0.0, -0.0255)]
    revolve(bm, profile, axis="Z", origin=o, segs=16)
    specimen("HARDWARE.bolt", bm, "Hex-head bolt (AN3 type, 3/16 in)", "مسمار ملولب برأس سداسي (نوع AN3، 3/16 بوصة)", "steel", o,
             "Bolts join fittings, bellcranks, hinges and brackets.")
    o = place()
    bm = new_bm()
    hex_prism(bm, o, Z, 0.0095, 0.0042)
    revolve(bm, [(0.0026, 0.0042), (0.0042, 0.0042), (0.0042, 0.0062), (0.0026, 0.0062), (0.0026, 0.0042)], axis="Z", origin=o, segs=16, cap_start=False, cap_end=False)
    specimen("HARDWARE.nut_self_locking", bm, "Self-locking nut (AN365 type, with a fibre insert)", "صامولة ذاتية القفل (نوع AN365، بحشوة ليفية)", "steel", o,
             "The insert grips the thread so that the nut cannot work loose.")
    o = place()
    bm = new_bm()
    hex_prism(bm, o, Z, 0.0095, 0.0045)
    for k in range(6):
        angle = math.pi / 3 * k + math.pi / 6
        box(bm, (0.0024, 0.0024, 0.0022), center=o + Vector((math.cos(angle) * 0.0036, math.sin(angle) * 0.0036, 0.0056)))
    rod(bm, o + Vector((-0.007, 0, 0.0052)), o + Vector((0.007, 0, 0.0052)), 0.0006, segs=5)
    specimen("HARDWARE.nut_castle_with_cotter_pin", bm, "Castle nut with cotter pin (AN310 and AN380 types)", "صامولة تاجية مع مسمار خابور (نوعا AN310 و AN380)", "steel", o,
             "Used on bolts that turn in service (control joints, wheel axles): the pin through the slots and the bolt keeps the nut from turning.")
    o = place()
    bm = new_bm()
    disc(bm, o, Z, 0.0048, 0.0016, segs=20, bore=0.0025)
    specimen("HARDWARE.washer", bm, "Plain washer (AN960 type)", "حلقة مستوية (نوع AN960)", "steel", o, "Spreads the load under a nut or a bolt head.")
    o = place()
    bm = new_bm()
    revolve(bm, [(0.0, -0.012), (0.0019, -0.012), (0.0021, -0.0105), (0.0021, 0.0), (0.004, 0.0), (0.0038, 0.0013), (0.0024, 0.0021), (0.0, 0.0022)], axis="Z", origin=o, segs=18)
    box(bm, (0.0046, 0.0008, 0.0008), center=o + Z * 0.0021)
    box(bm, (0.0008, 0.0046, 0.0008), center=o + Z * 0.0021)
    specimen("HARDWARE.screw_pan_head", bm, "Pan-head machine screw with cross recess", "برغي برأس مستدير وشق متصالب", "steel", o,
             "Screws hold what is taken off for inspection: fairings, covers, inspection plates, instruments.")
    o = place()
    bm = new_bm()
    rod(bm, o - Z * 0.028, o + Z * 0.028, 0.0045, segs=12)                                  # barrel
    for sign in (-1, 1):
        rod(bm, o + Z * (sign * 0.02), o + Z * (sign * 0.05), 0.0022, segs=8)                # threaded ends
        bar(bm, o + Z * (sign * 0.05) + X * 0.003, o + Z * (sign * 0.066) + X * 0.003, 0.007, 0.0015, X)   # fork
        bar(bm, o + Z * (sign * 0.05) - X * 0.003, o + Z * (sign * 0.066) - X * 0.003, 0.007, 0.0015, X)
        rod(bm, o + Z * (sign * 0.061) - X * 0.005, o + Z * (sign * 0.061) + X * 0.005, 0.0016, segs=6)     # clevis pin
    specimen("HARDWARE.turnbuckle", bm, "Turnbuckle (barrel with a fork at each end)", "شدّاد (أسطوانة ملولبة بشوكة عند كل طرف)", "brass", o,
             "Sets the tension of a control cable: one end has a left-hand thread, so turning the barrel draws both ends in.")
    o = place()
    bm = new_bm()
    disc(bm, o, X, 0.022, 0.009, segs=28, rim=0.0046)
    disc(bm, o, X, 0.008, 0.011, segs=14, bore=0.0032)
    specimen("HARDWARE.cable_pulley", bm, "Control cable pulley", "بكرة كابل التحكم", "black_plastic", o, "Leads a control cable round a bend; it turns on a sealed bearing.")
    o = place()
    bm = new_bm()
    rod(bm, o - Z * 0.03, o - Z * 0.008, 0.004, segs=10)
    disc(bm, o, X, 0.009, 0.006, segs=18, bore=0.0055)
    disc(bm, o, X, 0.0055, 0.008, segs=14, bore=0.0025)
    specimen("HARDWARE.rod_end_bearing", bm, "Rod end bearing (at each end of a push-pull rod)", "محمل طرف القضيب (عند كل طرف من قضيب الدفع والسحب)", "steel", o,
             "A ball in a socket lets the rod swing while it pushes and pulls.")
    o = place()
    bm = new_bm()
    for index in range(5):                                                                 # five knuckles on one pin, leaves alternate
        z = -0.04 + 0.02 * index
        rod(bm, o + Z * (z - 0.0092), o + Z * (z + 0.0092), 0.003, segs=10)
        leaf = X if index % 2 == 0 else -X
        box(bm, (0.02, 0.0012, 0.0184), center=o + Z * z + leaf * 0.0125)
    rod(bm, o - Z * 0.053, o + Z * 0.053, 0.0012, segs=6)
    specimen("HARDWARE.hinge", bm, "Hinge with its pin (as on doors and control surfaces)", "مفصلة مع مسمارها (كما في الأبواب وأسطح التحكم)", "bare_alu", o,
             "Two leaves with interleaved knuckles turn on one pin.")
    o = place()
    bm = new_bm()
    revolve(bm, [(0.0, -0.013), (0.0022, -0.013), (0.0022, -0.002), (0.0036, -0.002), (0.0036, 0.0), (0.0068, 0.0), (0.0064, 0.0016), (0.0, 0.0022)], axis="Z", origin=o, segs=18)
    box(bm, (0.0105, 0.0012, 0.0008), center=o + Z * 0.0021)
    rod(bm, o + Vector((-0.004, 0, -0.011)), o + Vector((0.004, 0, -0.011)), 0.0008, segs=5)
    specimen("HARDWARE.quarter_turn_fastener", bm, "Quarter-turn fastener (cowling stud)", "مثبّت ربع اللفة (مسمار غطاء المحرك)", "steel", o,
             "A quarter of a turn with a screwdriver locks or releases it, which is why it is used on the cowling.")
