"""Flight controls: what joins the control wheels, the pedals and the trim wheel to the control
surfaces (POH p.7-4 and 7-5, Figure 7-1, two sheets).

What the handbook figure shows, and this pack builds:
  ailerons   a control column behind the panel joins the two control wheels; cables run from it down
             to the floor, aft under the floor, up inside the rear door posts and out through each
             wing to a bellcrank just ahead of the aileron, which a push-pull rod joins to the
             aileron; a second cable joins the two bellcranks across the cabin roof
  elevator   the column rocks fore and aft; a push-pull rod takes that to a bellcrank under the
             floor, two cables run aft through the tailcone to a second bellcrank, and a push-pull
             rod joins that to the elevator
  rudder     two rudder bars carry the pedals; a cable from each runs aft under the floor and through
             the tailcone to the horn at the foot of the rudder; two rods run forward from the bars
             to the nose gear for steering
  trim       a chain on the trim wheel pulls two cables, which run aft to a screw actuator in the
             right half of the stabiliser; a push-pull rod joins the actuator to the trim tab

What is from where:
  poh        that each of these members exists and what it joins (Figure 7-1)
  estimated  every position, length, radius and bracket. The runs follow lanes.py so that nothing
             crosses and nothing passes through sheet metal. Two members are simplified: the
             bellcrank under the floor turns about an upright axis here because the model's floor
             is shallow, and the chains are drawn as flat bands.
"""
import math

import bpy
from mathutils import Vector

from .. import units as U
from ..units import IN, fs
from .. import airframe as A
from . import lanes
from . import structure_wing as SW
from . import structure_fuselage as SF
from .structure_fuselage import SKIN, TAIL_END_PASSAGES
from .common import (Plane, bar, cable, cable_run, pulley, turnbuckle, plate_lever, chain, arc, disc, rod, rod_end, bolt,
                     part, new_bm, box, tube, X, Y, Z)

SYS = "CONTROLS"
REF = "p.7-4, 7-5 (Fig 7-1)"
WING_ENTRY_Z = 2.05          # the aileron cable is cut into its cabin run and its wing run at this height in the door post
CABLE = 0.0016               # radius of a control cable as drawn (1/8 in)
BEND = 0.024                 # bend radius of a cable round a pulley
NOTE = "Shown in POH Figure 7-1; its position and size here are representative"


class System:
    """Makes the parts of one control system: same reference, same assembly tag."""

    def __init__(self, ctx, assembly):
        self.ctx = ctx
        self.assembly = assembly

    def add(self, name, bm, en, ar, mat="steel", group="SYSTEMS", status="poh", smooth=True, **tags):
        tags.setdefault("assembly", self.assembly)
        if status == "poh":
            tags.setdefault("ref", REF)
            tags.setdefault("note", NOTE)
        return part(self.ctx, name, bm, group, SYS, en, ar, mat, status=status, smooth=smooth, **tags)

    def lay(self, pieces, corners, pulleys, bend=BEND):
        """Lay one cable through `corners` and cut it into named pieces.
        pieces   [(name, group, en, ar, cut)]: the first has cut None; a later one starts at corner
                 number `cut` (1 = the first corner after the start): at the end of that corner's arc.
        pulleys  one entry per inner corner: None, or (name, group, en, ar, mount direction or None)."""
        path, found = cable_run(corners, bend)
        cuts = [0] + [found[cut - 1][4] for _n, _g, _e, _a, cut in pieces[1:]] + [len(path) - 1]
        for index, (name, group, en, ar, _cut) in enumerate(pieces):
            bm = new_bm()
            cable(bm, path[cuts[index]: cuts[index + 1] + 1], CABLE)
            self.add(name, bm, en, ar, "steel", group)
        for spec, hit in zip(pulleys, found):
            if spec is None or hit[0] is None:
                continue
            name, group, en, ar, mount = spec
            centre, axis, radius, _first, _last = hit
            reach = 0.012
            rim = radius + 0.003
            if mount == "floor":                 # hung from the underside of the cabin floor
                station = centre.y / IN + U.FS_ORIGIN
                mount, reach = Z, max(0.004, lanes.floor_underside(station) - centre.z - rim)
            elif mount == "belly":               # standing on the bottom of the hull
                station = centre.y / IN + U.FS_ORIGIN
                mount, reach = -Z, max(0.004, centre.z - rim - A.fus_surface_z(station, abs(centre.x)) - SKIN - 0.002)
            bm = new_bm()
            pulley(bm, centre, axis, radius, CABLE, mount=mount, reach=reach)
            self.add(name, bm, en, ar, "cast_alu", group)
        return path

    def turnbuckle(self, name, path, station, en, ar, group="SYSTEMS"):
        """A turnbuckle on a cable where it passes a fuselage station."""
        y = fs(station)
        for a, b in zip(path, path[1:]):
            if min(a.y, b.y) <= y <= max(a.y, b.y) and abs(b.y - a.y) > 1e-6:
                centre = a + (b - a) * ((y - a.y) / (b.y - a.y))
                direction = (b - a).normalized()
                bm = new_bm()
                turnbuckle(bm, centre - direction * 0.045, centre + direction * 0.045)
                return self.add(name, bm, en, ar, "brass", group, status="estimated",
                                note="Each cable has a turnbuckle to set its tension; its position is representative")
        return None


def post_point(side, water):
    """Point on the centre line of the rear door post at a water line (in)."""
    return SF.post_point("aft", side, water, shift=0.95)      # behind the fuel pipe from the aft tank outlet, which lies ahead of the centre line


def wing_frame(xabs, side, xc):
    """Plane lying in the wing at a span position and chord fraction: u outboard, v aft, origin on the middle of the section."""
    origin = A.wing_hinge_point(xabs, side, xc)
    out = (A.wing_hinge_point(xabs + 0.1, side, xc) - origin).normalized()
    aft = A.wing_hinge_point(xabs, side, xc + 0.1) - origin
    aft = (aft - out * aft.dot(out)).normalized()
    return Plane(origin, out, aft)


def tail_run(x, station, z):
    return Vector((x, fs(station), z))


def build(ctx):
    bpy.context.view_layer.update()
    scene = bpy.data.objects
    shaft = scene["INTERIOR.yoke_shaft_L"].matrix_world.translation
    half, panel_y, wheel_z = abs(shaft.x), shaft.y, shaft.z
    floor_top = A.floor_z(12) + 0.015
    build_column_and_ailerons(ctx, half, panel_y, wheel_z, floor_top)
    build_elevator(ctx, panel_y, wheel_z)
    build_rudder(ctx, floor_top)
    build_trim(ctx)


# ----------------------------------------------------------------------------- column and ailerons

def build_column_and_ailerons(ctx, half, panel_y, wheel_z, floor_top):
    scene = bpy.data.objects
    ail = System(ctx, "aileron_control")
    col_y = panel_y - 0.125                     # the column stands behind the panel
    cross_z = wheel_z - 0.24                    # its pivot tube
    sprocket_y = panel_y - 0.150
    sprocket_r = 0.030

    bm = new_bm()
    rod(bm, (-half - 0.02, col_y, cross_z), (half + 0.02, col_y, cross_z), 0.014, segs=12)
    for sx in (1, -1):
        tube(bm, [Vector((sx * half, col_y, cross_z)), Vector((sx * half, col_y + 0.004, wheel_z - 0.03))], 0.012, segs=10)
        box(bm, (0.05, 0.05, 0.065), center=(sx * half, col_y + 0.012, wheel_z))
        rod(bm, (sx * half, col_y - 0.01, wheel_z), (sx * half, sprocket_y - 0.006, wheel_z), 0.008, segs=8)
    tube(bm, [Vector((0, col_y, cross_z)), Vector((0, col_y - 0.01, COLUMN_ARM_Z))], 0.012, segs=10)
    System(ctx, "aileron_control,elevator_control").add(
        "CONTROLS.control_column", bm, "Control column (joins the two control wheels; rocks fore and aft for the elevator)",
        "عمود القيادة (يربط عجلتي القيادة ويتأرجح أماماً وخلفاً للرافع)", "steel")
    for sx, S in ((1, "L"), (-1, "R")):
        x = sx * 0.14
        bm = new_bm()
        box(bm, (0.03, 0.042, 0.042), center=(x, col_y, cross_z))
        bar(bm, (x, col_y - 0.014, cross_z - 0.02), (x, col_y - 0.055, floor_top), 0.03, 0.003, X)
        bar(bm, (x, col_y + 0.014, cross_z - 0.02), (x, col_y + 0.055, floor_top), 0.03, 0.003, X)
        System(ctx, "aileron_control,elevator_control").add(
            f"CONTROLS.control_column_support_{S}", bm, "Control column pivot bearing and support", "محمل محور عمود القيادة ودعامته",
            "cast_alu", status="estimated", smooth=False)

    # sprocket and chain on each control wheel shaft
    for sx, S in ((1, "L"), (-1, "R")):
        centre = Vector((sx * half, sprocket_y, wheel_z))
        bm = new_bm()
        disc(bm, centre, Y, sprocket_r - 0.003, 0.005, segs=24)
        ail.add(f"CONTROLS.aileron_sprocket_{S}", bm, "Aileron sprocket on the control wheel shaft", "الترس المسنن للجنيح على عمود عجلة القيادة", "steel")
        bm = new_bm()
        path = [centre + Vector((-sprocket_r, 0, -0.05))] + arc(centre, X * sprocket_r, Z * sprocket_r, math.pi, 0.0, 10) + [centre + Vector((sprocket_r, 0, -0.05))]
        chain(bm, path, Y)
        ail.add(f"CONTROLS.aileron_chain_{S}", bm, "Aileron chain (turning the wheel pulls one cable and lets out the other)",
                "سلسلة الجنيح (تدوير العجلة يشد كابلاً ويرخي الآخر)", "steel", smooth=False)

    # the cable that joins the inboard ends of the two chains, so that the two wheels turn together
    inner = half - sprocket_r
    ail.lay([("CONTROLS.aileron_interconnect_cable", "SYSTEMS", "Cable joining the two control wheels", "الكابل الرابط بين عجلتي القيادة", None)],
            [(inner, sprocket_y, wheel_z - 0.05), (inner, sprocket_y, cross_z + 0.05), (-inner, sprocket_y, cross_z + 0.05), (-inner, sprocket_y, wheel_z - 0.05)],
            [("CONTROLS.aileron_interconnect_pulley_L", "SYSTEMS", "Pulley of the cable joining the control wheels", "بكرة الكابل الرابط بين عجلتي القيادة", -Z),
             ("CONTROLS.aileron_interconnect_pulley_R", "SYSTEMS", "Pulley of the cable joining the control wheels", "بكرة الكابل الرابط بين عجلتي القيادة", -Z)])

    bellcrank_x = SW.AILERON_BELLCRANK_BL * IN
    carry_ends = {}
    for sx, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        grp = "WING_" + S
        frame = wing_frame(bellcrank_x, sx, 0.70)
        chord = A.wing_chord(bellcrank_x)
        arm_direct = (-0.012, (lanes.wing_run("aileron_direct", SW.AILERON_BELLCRANK_BL)[0] - 0.70) * chord)
        arm_carry = (-0.012, (lanes.wing_run("aileron_carry", SW.AILERON_BELLCRANK_BL)[0] - 0.70) * chord)
        arm_rod = ((SW.AILERON_PUSHROD_BL - SW.AILERON_BELLCRANK_BL) * IN, 0.0)

        # direct cable: chain, down to the floor, aft under the floor, across to the rear door post, up the post, out along the wing
        outer = sx * (half + sprocket_r)
        post_top = post_point(sx, 61.0)
        post_foot = post_point(sx, A.DOOR[1][1] + 1.9)
        root_corner = lanes.wing_point("aileron_direct", sx, 0.512 / IN)
        corners = [
            (outer, sprocket_y, wheel_z - 0.05),
            (outer, sprocket_y, floor_top + 0.03),
            lanes.point(f"aileron_{S}", 19.5),
            lanes.point(f"aileron_{S}", lanes.AILERON_TURN_FS),
            (sx * 0.42, fs(lanes.AILERON_TURN_FS), lanes.LEVEL + 0.005),
            (sx * 0.455, post_foot.y, 1.000),                    # below the post: the cable then rises square to the wall, clear of the fuel pipe
            post_foot,
            post_top,
            post_top + (root_corner - post_top) * ((WING_ENTRY_Z - post_top.z) / (root_corner.z - post_top.z)),
            root_corner,
            lanes.wing_point("aileron_direct", sx, 27.0),
            frame.at(*arm_direct),
        ]
        ail.lay([(f"CONTROLS.aileron_cable_{S}", "SYSTEMS", f"Aileron direct cable, cabin run ({where_en}): control column to the wing root",
                  f"كابل الجنيح المباشر {where_ar}، مسار المقصورة: من عمود القيادة إلى جذر الجناح", None),
                 (f"{grp}.aileron_cable_direct", grp, f"Aileron direct cable, wing run ({where_en}): wing root to the aileron bellcrank",
                  f"كابل الجنيح المباشر {where_ar}، مسار الجناح: من جذر الجناح إلى الذراع المرفقي للجنيح", 8)],
                corners,
                [(f"CONTROLS.aileron_pulley_column_{S}", "SYSTEMS", "Aileron cable pulley at the foot of the control column", "بكرة كابل الجنيح عند قاعدة عمود القيادة", -Z),
                 (f"CONTROLS.aileron_pulley_floor_{S}", "SYSTEMS", "Aileron cable pulley under the floor, forward", "بكرة كابل الجنيح تحت الأرضية، الأمامية", "floor"),
                 (f"CONTROLS.aileron_pulley_aft_{S}", "SYSTEMS", "Aileron cable pulley under the floor, at the rear door posts", "بكرة كابل الجنيح تحت الأرضية عند قائمي الباب الخلفيين", "floor"),
                 (f"CONTROLS.aileron_pulley_side_{S}", "SYSTEMS", "Aileron cable pulley at the side of the cabin floor", "بكرة كابل الجنيح عند جانب أرضية المقصورة", "floor"),
                 (f"CONTROLS.aileron_pulley_sill_{S}", "SYSTEMS", "Aileron cable pulley below the rear door post", "بكرة كابل الجنيح تحت قائم الباب الخلفي", None),
                 (f"CONTROLS.aileron_pulley_post_{S}", "SYSTEMS", "Aileron cable pulley at the foot of the rear door post", "بكرة كابل الجنيح عند قاعدة قائم الباب الخلفي", None),
                 None,
                 None,
                 (f"{grp}.aileron_pulley_root", grp, "Aileron cable pulley in the wing root", "بكرة كابل الجنيح في جذر الجناح", None),
                 None])

        # bellcrank, its support between two ribs, and the push-pull rod to the aileron
        bm = new_bm()
        plate_lever(bm, frame, [arm_direct, arm_carry, arm_rod], hub=0.016, thickness=0.004)
        bolt(bm, frame.at(0, 0, -0.016), frame.n, 0.006, 0.032)
        ail.add(f"{grp}.aileron_bellcrank", bm, f"Aileron bellcrank ({where_en} wing)", f"الذراع المرفقي للجنيح (الجناح {where_ar})", "cast_alu", grp, smooth=False)
        bm = new_bm()
        inboard = (SW.RIB_STATIONS[7] - SW.AILERON_BELLCRANK_BL) * IN + 0.002
        outboard = (SW.RIB_STATIONS[8] - SW.AILERON_BELLCRANK_BL) * IN - 0.002
        for depth in (-0.013, 0.013):
            bar(bm, frame.at(inboard, 0.0, depth), frame.at(outboard, 0.0, depth), 0.034, 0.0025, frame.n)
        ail.add(f"{grp}.aileron_bellcrank_support", bm, "Aileron bellcrank support (between two ribs)", "دعامة الذراع المرفقي للجنيح (بين ضلعين)",
                "bare_alu", grp, status="estimated", smooth=False)
        rod_x = SW.AILERON_PUSHROD_BL * IN
        up = (A.wing_point(rod_x, sx, 0.8, 1.0) - A.wing_point(rod_x, sx, 0.8, 0.0)).normalized()
        horn_tip = A.wing_hinge_point(rod_x, sx, A.ail_xc(rod_x) + 0.02) - up * 0.012
        bm = new_bm()
        rod_end(bm, frame.at(*arm_rod), horn_tip, 0.006)
        ail.add(f"{grp}.aileron_pushrod", bm, f"Aileron push-pull rod ({where_en}): bellcrank to aileron", f"قضيب الدفع والسحب للجنيح {where_ar}: من الذراع المرفقي إلى الجنيح",
                "bare_alu", grp)
        bm = new_bm()
        horn_plane = Plane(horn_tip + up * 0.012, (A.wing_hinge_point(rod_x, sx, 0.9) - A.wing_hinge_point(rod_x, sx, 0.8)).normalized(), up)
        plate_lever(bm, horn_plane, [(0.0, -0.012), (0.03, 0.006)], hub=0.01, eye=0.007, thickness=0.003)
        ail.add(f"{grp}.aileron_horn", bm, f"Aileron control horn ({where_en})", f"قرن التحكم بالجنيح {where_ar}", "steel", grp, status="estimated", smooth=False,
                parent=scene[f"{grp}.aileron"], note="Where the push-pull rod is attached to the aileron; representative")

        # carry-through cable, wing run: from the bellcrank inboard to the cabin roof
        root = lanes.wing_point("aileron_carry", sx, 27.0)
        station = root.y / IN + U.FS_ORIGIN
        roof = Vector((sx * A.WING_ROOT_X, root.y, A.fus_surface_z(station, A.WING_ROOT_X, top=True) - SKIN - 0.006))
        carry_ends[sx] = roof
        bm = new_bm()
        cable(bm, [frame.at(*arm_carry), root, roof], CABLE)
        ail.add(f"{grp}.aileron_cable_carry_through", bm, f"Aileron carry-through cable, {where_en} wing run (joins the two aileron bellcranks)",
                f"الكابل الرابط بين الجنيحين، مسار الجناح {where_ar} (يربط الذراعين المرفقيين للجنيحين)", "steel", grp)

    left, right = carry_ends[1], carry_ends[-1]
    station = left.y / IN + U.FS_ORIGIN
    middle = Vector((0.0, left.y, A.fus_top_z(station) - SKIN - 0.006))
    bm = new_bm()
    cable(bm, [left, middle, right], CABLE)
    ail.add("CONTROLS.aileron_cable_carry_through", bm, "Aileron carry-through cable, across the cabin roof", "الكابل الرابط بين الجنيحين، عبر سقف المقصورة", "steel")
    for ob_name in ("WING_L.aileron", "WING_R.aileron", "INTERIOR.yoke_L", "INTERIOR.yoke_R"):
        if ob_name in scene:
            scene[ob_name]["assembly"] = "aileron_control" if "aileron" in ob_name else "aileron_control,elevator_control"


# ----------------------------------------------------------------------------- elevator

COLUMN_ARM_Z = 0.985                    # lower end of the control column's arm, just above the floor
FWD_BELLCRANK_FS = 33.0
AFT_BELLCRANK_FS = 221.0
AFT_BELLCRANK_Z = 1.19


def build_elevator(ctx, panel_y, wheel_z):
    scene = bpy.data.objects
    elev = System(ctx, "elevator_control")
    col_y = panel_y - 0.125
    up_x = lanes.ALONG["elevator_up"][0]
    pivot = Vector((0.0, fs(FWD_BELLCRANK_FS), lanes.LEVEL))
    plane = Plane(pivot, X, Y)
    bm = new_bm()
    rod_end(bm, (0.0, col_y - 0.01, COLUMN_ARM_Z), plane.at(up_x, -0.012, 0.012), 0.008)
    elev.add("CONTROLS.elevator_pushrod_fwd", bm, "Elevator push-pull rod: control column to the bellcrank under the floor",
             "قضيب الدفع والسحب للرافع: من عمود القيادة إلى الذراع المرفقي تحت الأرضية", "bare_alu")
    bm = new_bm()
    plate_lever(bm, plane, [(up_x, 0.0), (-up_x, 0.0), (up_x, -0.012)], hub=0.016, thickness=0.004)
    bolt(bm, pivot + Z * 0.016, -Z, 0.006, 0.024)
    elev.add("CONTROLS.elevator_bellcrank_fwd", bm, "Forward elevator bellcrank (under the floor)", "الذراع المرفقي الأمامي للرافع (تحت الأرضية)", "cast_alu", smooth=False,
             note="Shown in POH Figure 7-1. Here it turns about an upright axis because the model's floor is shallow; position representative")

    aft_pivot = Vector((0.0, fs(AFT_BELLCRANK_FS), AFT_BELLCRANK_Z))
    aft_plane = Plane(aft_pivot, Y, Z)
    arms = {"up": (0.0, 0.034), "down": (0.0, -0.040), "rod": (0.006, 0.046)}
    for key, sign, word_en, word_ar in (("up", 1, "up", "رفع"), ("down", -1, "down", "خفض")):
        x = lanes.ALONG[f"elevator_{key}"][0]
        corners = [plane.at(x, 0.0), lanes.point(f"elevator_{key}", lanes.CLIMB_STATION), tail_run(x * 0.9, lanes.AFT_STATION, lanes.AFT_LEVEL),
                   tail_run(x * 0.75, lanes.TAIL_STATION, lanes.TAIL_LEVEL + 0.02), aft_plane.at(*arms[key])]
        path = elev.lay([(f"CONTROLS.elevator_cable_{key}", "SYSTEMS", f"Elevator cable (nose-{word_en} side): forward bellcrank to aft bellcrank",
                          f"كابل الرافع (جهة {word_ar} المقدمة): من الذراع المرفقي الأمامي إلى الخلفي", None)],
                        corners,
                        [(f"CONTROLS.elevator_pulley_seat_{key}", "SYSTEMS", "Elevator cable pulley under the rear seat", "بكرة كابل الرافع تحت المقعد الخلفي", "floor"),
                         (f"CONTROLS.elevator_pulley_bulkhead_{key}", "SYSTEMS", "Elevator cable pulley at the aft cabin bulkhead", "بكرة كابل الرافع عند الحاجز الخلفي للمقصورة", "belly"),
                         (f"CONTROLS.elevator_pulley_tailcone_{key}", "SYSTEMS", "Elevator cable pulley in the tailcone", "بكرة كابل الرافع في مخروط الذيل", "belly")])
        elev.turnbuckle(f"CONTROLS.elevator_turnbuckle_{key}", path, 150.0, "Elevator cable turnbuckle", "شدّاد كابل الرافع")

    bm = new_bm()
    plate_lever(bm, aft_plane, list(arms.values()), hub=0.016, thickness=0.004)
    bolt(bm, aft_pivot - X * 0.02, X, 0.006, 0.04)
    elev.add("CONTROLS.elevator_bellcrank_aft", bm, "Aft elevator bellcrank (in the tailcone)", "الذراع المرفقي الخلفي للرافع (في مخروط الذيل)", "cast_alu", smooth=False)
    bm = new_bm()
    foot = A.fus_surface_z(AFT_BELLCRANK_FS, 0.0) + SKIN + 0.002
    for sx in (-1, 1):
        bar(bm, aft_pivot + X * (sx * 0.016), Vector((sx * 0.016, aft_pivot.y, foot)), 0.03, 0.0025, X)
    box(bm, (0.06, 0.05, 0.003), center=(0, aft_pivot.y, foot + 0.0015))
    elev.add("CONTROLS.elevator_bellcrank_aft_support", bm, "Aft elevator bellcrank support", "دعامة الذراع المرفقي الخلفي للرافع", "bare_alu", status="estimated", smooth=False)

    # push-pull rod through the last frame to the horn on the elevator torque tube
    horn_plane = Plane((0.0, A.ELEV_HINGE_Y + 0.012, A.STAB_Z), Y, Z)
    horn_tip = horn_plane.at(0.0, -0.085)
    start = aft_plane.at(*arms["rod"])
    passage = TAIL_END_PASSAGES[0]
    expected = start.z + (horn_tip.z - start.z) * (fs(A.FUS_END_FS - 1.0) - start.y) / (horn_tip.y - start.y)
    assert abs(expected - passage[1]) < 0.006 and abs(passage[0]) < 1e-6, "the elevator push-pull rod misses its opening in the last frame"
    bm = new_bm()
    rod_end(bm, start, horn_tip, 0.007)
    elev.add("EMPENNAGE.elevator_pushrod_aft", bm, "Elevator push-pull rod: aft bellcrank to the elevator horn", "قضيب الدفع والسحب للرافع: من الذراع المرفقي الخلفي إلى قرن الرافع",
             "bare_alu", group="EMPENNAGE")
    bm = new_bm()
    plate_lever(bm, horn_plane, [(0.0, -0.085)], hub=0.022, eye=0.009, thickness=0.004)
    part(ctx, "EMPENNAGE.elevator_horn", bm, "EMPENNAGE", SYS, "Elevator horn on the torque tube", "قرن الرافع على أنبوب العزم", "steel", status="poh", ref=REF,
         note=NOTE, assembly="elevator_control", parent=scene["EMPENNAGE.elevator"])
    scene["EMPENNAGE.elevator"]["assembly"] = "elevator_control"


# ----------------------------------------------------------------------------- rudder and nose-wheel steering

RUDDER_BAR_FS = (9.0, 10.6)             # forward bar, aft bar
RUDDER_HORN_Z = TAIL_END_PASSAGES[1][1]
RUDDER_HORN_X = 0.062


def build_rudder(ctx, floor_top):
    scene = bpy.data.objects
    rud = System(ctx, "rudder_control")
    steer = System(ctx, "nose_steering")
    bar_z = floor_top + 0.027
    for index, (station, key, sx, word_en, word_ar) in enumerate(((RUDDER_BAR_FS[0], "fwd", 1, "forward", "الأمامي"), (RUDDER_BAR_FS[1], "aft", -1, "aft", "الخلفي"))):
        y = fs(station)
        lane_x = lanes.ALONG["rudder_L" if sx > 0 else "rudder_R"][0]
        bm = new_bm()
        rod(bm, (-0.40, y, bar_z), (0.40, y, bar_z), 0.011, segs=10)
        bar(bm, (lane_x, y, bar_z), (lane_x, y, lanes.LEVEL), 0.022, 0.006, X)                 # arm for the rudder cable, down through the floor
        bar(bm, (-sx * 0.07, y, bar_z), (-sx * 0.07, y - 0.004, bar_z + 0.05), 0.02, 0.006, X)  # arm for the steering rod
        rud.add(f"CONTROLS.rudder_bar_{key}", bm, f"Rudder bar, {word_en} (carries one pedal of each pilot, the cable arm and the steering arm)",
                f"قضيب الدفة {word_ar} (يحمل دواسة لكل طيار وذراع الكابل وذراع التوجيه)", "steel", assembly="rudder_control,nose_steering")
        bm = new_bm()
        for x in (-0.385, 0.0, 0.385):
            box(bm, (0.022, 0.034, 0.03), center=(x, y, bar_z - 0.004))
            box(bm, (0.04, 0.05, bar_z - 0.019 - floor_top), center=(x, y, (bar_z - 0.019 + floor_top) / 2))
        rud.add(f"CONTROLS.rudder_bar_bearings_{key}", bm, "Rudder bar bearing blocks", "كتل محامل قضيب الدفة", "cast_alu", status="estimated", smooth=False)

        # cable from the arm aft under the floor and through the tailcone to the rudder horn
        S = "L" if sx > 0 else "R"
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        end_x = sx * abs(TAIL_END_PASSAGES[1][0])
        corners = [(lane_x, y, lanes.LEVEL), lanes.point(f"rudder_{S}", lanes.CLIMB_STATION), tail_run(lane_x * 0.94, lanes.AFT_STATION, lanes.AFT_LEVEL),
                   tail_run(lane_x * 0.875, lanes.TAIL_STATION, lanes.TAIL_LEVEL), tail_run(end_x, A.FUS_END_FS - 0.2, RUDDER_HORN_Z)]
        path = rud.lay([(f"CONTROLS.rudder_cable_{S}", "SYSTEMS", f"Rudder cable, {where_en}: rudder bar to the rudder horn", f"كابل الدفة {where_ar}: من قضيب الدفة إلى قرن الدفة", None)],
                       corners,
                       [(f"CONTROLS.rudder_pulley_seat_{S}", "SYSTEMS", "Rudder cable pulley under the rear seat", "بكرة كابل الدفة تحت المقعد الخلفي", "floor"),
                        (f"CONTROLS.rudder_pulley_bulkhead_{S}", "SYSTEMS", "Rudder cable pulley at the aft cabin bulkhead", "بكرة كابل الدفة عند الحاجز الخلفي للمقصورة", "belly"),
                        (f"CONTROLS.rudder_pulley_tailcone_{S}", "SYSTEMS", "Rudder cable pulley in the tailcone", "بكرة كابل الدفة في مخروط الذيل", "belly")])
        rud.turnbuckle(f"CONTROLS.rudder_turnbuckle_{S}", path, 160.0, "Rudder cable turnbuckle", "شدّاد كابل الدفة")
        horn_y = fs(A.FUS_END_FS) + 0.018
        bm = new_bm()
        rod_end(bm, path[-1], (sx * RUDDER_HORN_X, horn_y, RUDDER_HORN_Z), 0.003, eye=0.005)
        part(ctx, f"EMPENNAGE.rudder_cable_link_{S}", bm, "EMPENNAGE", SYS, f"Rudder cable end link, {where_en}", f"وصلة نهاية كابل الدفة {where_ar}", "steel",
             status="estimated", assembly="rudder_control", smooth=True)

    horn_y = fs(A.FUS_END_FS) + 0.018
    bm = new_bm()
    plate_lever(bm, Plane((0.0, horn_y, RUDDER_HORN_Z), X, Y), [(RUDDER_HORN_X, 0.0), (-RUDDER_HORN_X, 0.0)], hub=0.02, eye=0.009, thickness=0.004)
    part(ctx, "EMPENNAGE.rudder_horn", bm, "EMPENNAGE", SYS, "Rudder horn (bellcrank at the foot of the rudder)", "قرن الدفة (ذراع مرفقي عند قاعدة الدفة)", "steel",
         status="poh", ref=REF, note=NOTE, assembly="rudder_control", parent=scene["EMPENNAGE.rudder"])

    # nose-wheel steering: a rod from each rudder bar forward through the firewall to the arm on the nose strut
    strut = scene["GEAR.nose_strut"]
    top = strut.matrix_world.translation.copy()
    down = -(strut.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()          # the strut's own z axis points up along it
    collar = top + down * 0.10
    bm = new_bm()
    disc(bm, collar, down, 0.056, 0.022, segs=20, bore=0.04)
    for sx in (-1, 1):
        bar(bm, collar + X * (sx * 0.05), collar + X * (sx * 0.085) + Y * 0.01, 0.02, 0.008, down)
    steer.add("CONTROLS.steering_arm", bm, "Nose gear steering arm (collar on the strut)", "ذراع توجيه عجلة المقدمة (طوق على الدعامة)", "steel", smooth=False,
              ref="p.7-10", note="The nose wheel is steered through the rudder pedals (POH p.7-10); shape and position representative")
    for sx, S, station in ((1, "L", RUDDER_BAR_FS[1]), (-1, "R", RUDDER_BAR_FS[0])):
        bm = new_bm()
        start = Vector((sx * 0.07, fs(station) - 0.004, bar_z + 0.05))
        end = collar + X * (sx * 0.085) + Y * 0.01
        rod_end(bm, start, end, 0.007)
        middle = (start + end) / 2
        direction = (end - start).normalized()
        rod(bm, middle - direction * 0.07, middle + direction * 0.07, 0.012, segs=10)       # the spring cartridge of the steering rod
        steer.add(f"CONTROLS.steering_rod_{S}", bm, f"Nose-wheel steering rod with spring cartridge, {'left' if sx > 0 else 'right'}",
                  f"قضيب توجيه عجلة المقدمة مع خرطوشة نابضية، {'الأيسر' if sx > 0 else 'الأيمن'}", "bare_alu", ref="p.7-10",
                  note="Spring-loaded rods link the rudder bars to the nose gear (POH p.7-10: steerable through the rudder pedals); position representative")
    for name in ("EMPENNAGE.rudder", "INTERIOR.pedal_L_L", "INTERIOR.pedal_L_R", "INTERIOR.pedal_R_L", "INTERIOR.pedal_R_R"):
        if name in scene:
            scene[name]["assembly"] = "rudder_control"


# ----------------------------------------------------------------------------- elevator trim

TRIM_ACTUATOR_BL = 22.0
TRIM_ACTUATOR_FS = 226.0


def build_trim(ctx):
    scene = bpy.data.objects
    trim = System(ctx, "elevator_trim")
    wheel = scene["INTERIOR.trim_wheel"].matrix_world.translation.copy()
    r = 0.028
    centre = wheel + X * 0.022
    bm = new_bm()
    disc(bm, centre, X, r - 0.003, 0.005, segs=22)
    rod(bm, wheel, centre + X * 0.006, 0.006, segs=8)
    trim.add("CONTROLS.trim_sprocket", bm, "Trim wheel sprocket", "الترس المسنن لعجلة الموازنة", "steel")
    bm = new_bm()
    path = [centre + Vector((0, -0.03, r))] + arc(centre, Y * r, Z * r, math.pi / 2, -math.pi / 2, 10) + [centre + Vector((0, -0.03, -r))]
    chain(bm, path, X)
    trim.add("CONTROLS.trim_chain", bm, "Trim wheel chain", "سلسلة عجلة الموازنة", "steel", smooth=False)

    x_act = -TRIM_ACTUATOR_BL * IN                       # the trim tab is on the right elevator
    y_act = fs(TRIM_ACTUATOR_FS)
    sprocket_r = 0.02
    for key, sign, lead, word_en, word_ar in (("up", 1, 0.14, "nose-up", "رفع المقدمة"), ("down", -1, 0.075, "nose-down", "خفض المقدمة")):
        lane = lanes.ALONG[f"trim_{key}"]
        z_end = A.STAB_Z + sign * sprocket_r
        corners = [
            centre + Vector((0, -0.03, sign * r)),
            centre + Vector((0, -lead, sign * r)),
            (centre.x, centre.y - lead, A.floor_z(22) + 0.045),
            lanes.point(f"trim_{key}", 30.5 if sign > 0 else 31.5),
            lanes.point(f"trim_{key}", lanes.CLIMB_STATION),
            tail_run(lane[0], lanes.AFT_STATION, lanes.AFT_LEVEL),
            tail_run(lane[0], lanes.TAIL_STATION, lanes.TAIL_LEVEL + 0.04),
            (-0.04, y_act, z_end),
            (x_act + 0.06, y_act, z_end),
        ]
        path = trim.lay([(f"CONTROLS.trim_cable_{key}", "SYSTEMS", f"Elevator trim cable ({word_en}): trim wheel to the tailcone", f"كابل موازنة الرافع ({word_ar}): من عجلة الموازنة إلى مخروط الذيل", None),
                         (f"EMPENNAGE.trim_cable_{key}", "EMPENNAGE", f"Elevator trim cable ({word_en}), run inside the stabiliser to the actuator",
                          f"كابل موازنة الرافع ({word_ar})، المسار داخل المثبت الأفقي إلى المشغّل", 7)],
                        corners,
                        [(f"CONTROLS.trim_pulley_pedestal_{key}", "SYSTEMS", "Trim cable pulley in the pedestal", "بكرة كابل الموازنة في قاعدة أدوات التحكم", None),
                         (f"CONTROLS.trim_pulley_floor_{key}", "SYSTEMS", "Trim cable pulley at the floor", "بكرة كابل الموازنة عند الأرضية", None),
                         (f"CONTROLS.trim_pulley_under_floor_{key}", "SYSTEMS", "Trim cable pulley under the floor", "بكرة كابل الموازنة تحت الأرضية", "floor"),
                         (f"CONTROLS.trim_pulley_seat_{key}", "SYSTEMS", "Trim cable pulley under the rear seat", "بكرة كابل الموازنة تحت المقعد الخلفي", "floor"),
                         (f"CONTROLS.trim_pulley_bulkhead_{key}", "SYSTEMS", "Trim cable pulley at the aft cabin bulkhead", "بكرة كابل الموازنة عند الحاجز الخلفي للمقصورة", "belly"),
                         (f"CONTROLS.trim_pulley_tailcone_{key}", "SYSTEMS", "Trim cable pulley in the tailcone", "بكرة كابل الموازنة في مخروط الذيل", "belly"),
                         (f"CONTROLS.trim_pulley_stabilizer_{key}", "SYSTEMS", "Trim cable pulley at the stabiliser", "بكرة كابل الموازنة عند المثبت الأفقي", None)])
        trim.turnbuckle(f"CONTROLS.trim_turnbuckle_{key}", path, 165.0, "Trim cable turnbuckle", "شدّاد كابل الموازنة")

    # actuator in the right stabiliser: chain on a sprocket turns a screw, the screw moves the push-pull rod of the tab
    axis_centre = Vector((x_act, y_act, A.STAB_Z))
    bm = new_bm()
    path = [Vector((x_act + 0.06, y_act, A.STAB_Z + sprocket_r))] + arc(axis_centre, -X * sprocket_r, Z * sprocket_r, math.pi / 2, -math.pi / 2, 8) \
        + [Vector((x_act + 0.06, y_act, A.STAB_Z - sprocket_r))]
    chain(bm, path, Y)
    part(ctx, "EMPENNAGE.trim_actuator_chain", bm, "EMPENNAGE", SYS, "Trim actuator chain", "سلسلة مشغّل الموازنة", "steel", status="poh", ref=REF, note=NOTE,
         assembly="elevator_trim")
    bm = new_bm()
    disc(bm, axis_centre, Y, sprocket_r - 0.003, 0.005, segs=18)
    rod(bm, axis_centre - Y * 0.012, axis_centre + Y * 0.085, 0.015, segs=12)                 # screw housing
    rod(bm, axis_centre + Y * 0.085, axis_centre + Y * 0.12, 0.006, segs=8)                   # screw
    for offset in (0.01, 0.07):
        box(bm, (0.05, 0.004, 0.05), center=axis_centre + Y * offset)                        # mounting plates
    part(ctx, "EMPENNAGE.trim_actuator", bm, "EMPENNAGE", SYS, "Elevator trim tab actuator (screw jack in the right half of the stabiliser)",
         "مشغّل لسان موازنة الرافع (رافعة لولبية في النصف الأيمن من المثبت الأفقي)", "cast_alu", status="poh", ref=REF, note=NOTE, assembly="elevator_trim", smooth=True)

    tab = scene["EMPENNAGE.trim_tab"]
    xabs = TRIM_ACTUATOR_BL * IN
    tab_chord = A.TRIM_TAB_CHORD[0] + (A.TRIM_TAB_CHORD[1] - A.TRIM_TAB_CHORD[0]) * (xabs - A.TRIM_TAB_SPAN[0]) / (A.TRIM_TAB_SPAN[1] - A.TRIM_TAB_SPAN[0])
    tab_hinge_y = A.stab_te_y(xabs) - tab_chord
    chord = A.stab_chord(xabs)
    xc = 1 - tab_chord / chord
    half_thickness = 0.45 * chord * (0.2969 * math.sqrt(xc) - 0.126 * xc - 0.3516 * xc ** 2 + 0.2843 * xc ** 3 - 0.1015 * xc ** 4)     # NACA 0009
    horn_root = Vector((x_act, tab_hinge_y + 0.012, A.STAB_Z - half_thickness))
    horn_tip = horn_root - Z * 0.024
    bm = new_bm()
    rod_end(bm, axis_centre + Y * 0.12 - Z * 0.004, horn_tip, 0.005, eye=0.006)
    part(ctx, "EMPENNAGE.trim_tab_pushrod", bm, "EMPENNAGE", SYS, "Trim tab push-pull rod: actuator to the tab horn", "قضيب الدفع والسحب للسان الموازنة: من المشغّل إلى قرن اللسان",
         "bare_alu", status="poh", ref=REF, note=NOTE, assembly="elevator_trim", smooth=True, parent=scene["EMPENNAGE.elevator"])
    bm = new_bm()
    plate_lever(bm, Plane(horn_root, Y, Z), [(0.0, -0.024)], hub=0.009, eye=0.006, thickness=0.003)
    part(ctx, "EMPENNAGE.trim_tab_horn", bm, "EMPENNAGE", SYS, "Trim tab horn", "قرن لسان الموازنة", "steel", status="poh", ref=REF, note=NOTE,
         assembly="elevator_trim", parent=tab)
    tab["assembly"] = "elevator_trim"
    scene["INTERIOR.trim_wheel"]["assembly"] = "elevator_trim"
