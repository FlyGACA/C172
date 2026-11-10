"""Wing flap drive (POH p.7-10, Figure 7-3).

The flaps are single-slot flaps, electrically driven. What the handbook shows, and this pack builds:
an electric motor and transmission in the right wing turn a screw; the screw turns a drive pulley;
a push-pull rod joins that pulley to the right flap; two cables run from it across the cabin roof to
a second pulley in the left wing, whose push-pull rod moves the left flap, so that both flaps travel
together. Each flap rides on two tracks.

What is from where:
  poh        the members above and how they are joined
  estimated  every position and size. The two pulleys turn the same way, so the two cables run
             straight across without crossing; for that the push-pull rod leaves each pulley on the
             same side of the aircraft. The tracks are drawn as slotted plates beside two ribs.
"""
import math

import bpy
from mathutils import Vector

from .. import units as U
from ..units import IN
from .. import airframe as A
from . import geom2d
from . import lanes
from .structure_fuselage import SKIN
from .structure_wing import section_plane
from .common import Plane, sheet, bar, cable, plate_lever, arc, disc, rod, rod_end, bolt, part, new_bm, box

SYS = "CONTROLS"
REF = "p.7-10 (Fig 7-3)"
NOTE = "Shown in POH Figure 7-3; its position and size here are representative"
ASSEMBLY = "flap_drive"
PULLEY_BL = 64.0                 # wing station of the flap drive pulley in each wing
MOTOR_BL = (43.0, 51.0)          # the motor lies along the span, in the right wing
TRACK_BL = (37.4, 87.3)          # each flap rides on two tracks, beside the ribs at stations 39 and 85.6
CABLE = 0.0016


def add(ctx, name, bm, group, en, ar, mat, status="poh", smooth=True, **tags):
    tags.setdefault("assembly", ASSEMBLY)
    if status == "poh":
        tags.setdefault("ref", REF)
        tags.setdefault("note", NOTE)
    return part(ctx, name, bm, group, SYS, en, ar, mat, status=status, smooth=smooth, **tags)


def wing_frame(xabs, side, xc, dz=0.0):
    """Plane lying in the wing: u outboard, v aft, origin `dz` above the middle of the section."""
    middle = A.wing_hinge_point(xabs, side, xc)
    up = (A.wing_point(xabs, side, xc, 1.0) - A.wing_point(xabs, side, xc, 0.0)).normalized()
    out = (A.wing_hinge_point(xabs + 0.1, side, xc) - middle).normalized()
    aft = A.wing_hinge_point(xabs, side, xc + 0.1) - middle
    aft = (aft - out * aft.dot(out)).normalized()
    return Plane(middle + up * dz, out, aft), up


def build(ctx):
    scene = bpy.data.objects
    x_pulley = PULLEY_BL * IN
    chord = A.wing_chord(x_pulley)
    xc_a, dz = lanes.wing_run("flap_cable_a", PULLEY_BL)
    xc_b, _dz = lanes.wing_run("flap_cable_b", PULLEY_BL)
    xc_centre = 0.5 * (xc_a + xc_b)
    radius = 0.5 * (xc_b - xc_a) * chord               # the two cables lie on the two sides of the pulley
    roof = {}
    for sx, S in ((1, "L"), (-1, "R")):
        grp = "WING_" + S
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        frame, up = wing_frame(x_pulley, sx, xc_centre, dz)
        toward_right = -sx                              # in this frame u points outboard; the aircraft's right is -x
        arm_rod = (toward_right * 0.04, 0.0)            # the push-pull rod leaves on the aircraft's right side of both pulleys
        arm_screw = (0.0, -0.04)

        bm = new_bm()
        disc(bm, frame.origin, frame.n, radius + 0.003, 0.008, segs=28, rim=0.0046)
        plate = Plane(frame.origin - frame.n * (0.012 if sx > 0 else -0.012), frame.u, frame.v)      # the arms are a plate under the grooved rim
        plate_lever(bm, plate, [arm_rod] + ([arm_screw] if sx < 0 else []), hub=0.02, thickness=0.004)
        bolt(bm, frame.origin + up * 0.03, -up, 0.007, 0.06)
        add(ctx, f"{grp}.flap_drive_pulley", bm, grp, f"Flap drive pulley, {where_en} wing", f"بكرة تحريك القلاب، الجناح {where_ar}", "cast_alu", smooth=False)
        bm = new_bm()
        ribs = (55.62, 71.62)
        for depth in (0.03, -0.034):
            bar(bm, frame.at((ribs[0] - PULLEY_BL) * IN + 0.002, 0.0) + up * depth, frame.at((ribs[1] - PULLEY_BL) * IN - 0.002, 0.0) + up * depth, 0.036, 0.0025, up)
        add(ctx, f"{grp}.flap_drive_pulley_support", bm, grp, "Flap drive pulley support (between two ribs)", "دعامة بكرة تحريك القلاب (بين ضلعين)", "bare_alu",
            status="estimated", smooth=False)

        # push-pull rod to the flap, and the horn on the flap's leading edge
        rod_x = x_pulley + arm_rod[0]
        flap_up = (A.wing_point(rod_x, sx, 0.85, 1.0) - A.wing_point(rod_x, sx, 0.85, 0.0)).normalized()
        horn_root = A.wing_hinge_point(rod_x, sx, A.FLAP_XC + 0.03)
        horn_tip = horn_root - flap_up * 0.018
        bm = new_bm()
        rod_end(bm, plate.at(*arm_rod), horn_tip, 0.006)
        add(ctx, f"{grp}.flap_pushrod", bm, grp, f"Flap push-pull rod ({where_en}): drive pulley to flap", f"قضيب الدفع والسحب للقلاب {where_ar}: من بكرة التحريك إلى القلاب", "bare_alu")
        bm = new_bm()
        aft = (A.wing_hinge_point(rod_x, sx, 0.95) - A.wing_hinge_point(rod_x, sx, 0.85)).normalized()
        plate_lever(bm, Plane(horn_root, aft, flap_up), [(0.0, -0.018), (0.035, 0.0)], hub=0.011, eye=0.007, thickness=0.003)
        add(ctx, f"{grp}.flap_horn", bm, grp, f"Flap horn ({where_en})", f"قرن القلاب {where_ar}", "steel", status="estimated", smooth=False,
            parent=scene[f"{grp}.flap"], note="Where the push-pull rod is attached to the flap; representative")

        # the two cables: round the pulley, inboard along the wing, up to the cabin roof
        for key, sign in (("a", -1), ("b", 1)):
            wrap = arc(frame.origin, frame.u * radius, frame.v * radius, sign * math.pi / 2, 0.0, 8)           # from its side of the pulley round to the outboard edge
            wrap.reverse()
            root = lanes.wing_point(f"flap_cable_{key}", sx, 27.0)
            station = root.y / IN + U.FS_ORIGIN
            entry = Vector((sx * A.WING_ROOT_X, root.y, A.fus_surface_z(station, A.WING_ROOT_X, top=True) - SKIN - 0.006))
            roof[(sx, key)] = entry
            bm = new_bm()
            cable(bm, wrap + [root, entry], CABLE)
            add(ctx, f"{grp}.flap_cable_{key}", bm, grp, f"Flap synchronising cable {key.upper()}, {where_en} wing run",
                f"كابل مزامنة القلابين {key.upper()}، مسار الجناح {where_ar}", "steel")

        # two tracks per flap, with the arms and rollers that ride in them
        for index, (bl, word_en, word_ar) in enumerate(((TRACK_BL[0], "inboard", "الداخلي"), (TRACK_BL[1], "outboard", "الخارجي"))):
            xabs = bl * IN
            plane = section_plane(xabs, sx)
            c = A.wing_chord(xabs)
            af = A.wing_airfoil(xabs)

            def at(xc, fraction):                    # point of the section plane: chord fraction, 0 = lower skin .. 1 = upper skin
                low, high = A.airfoil_y(af, xc, False) * c, A.airfoil_y(af, xc, True) * c
                return (xc * c, low + (high - low) * fraction)

            outline = [at(0.662, 0.10), at(0.75, 0.12), at(0.75, 0.5), at(0.662, 0.5)]      # the lower half: the cables pass above it
            slot_a, slot_b = at(0.69, 0.38), at(0.738, 0.26)
            slot = geom2d.slot(0.5 * (slot_a[0] + slot_b[0]), 0.5 * (slot_a[1] + slot_b[1]), math.dist(slot_a, slot_b) + 0.014, 0.014, 6,
                               math.atan2(slot_b[1] - slot_a[1], slot_b[0] - slot_a[0]))
            bm = new_bm()
            sheet(bm, plane, outline, 0.003, [slot], offset=-0.0015)
            add(ctx, f"{grp}.flap_track_{word_en}", bm, grp, f"Flap track, {word_en} ({where_en} wing)", f"سكة القلاب {word_ar} (الجناح {where_ar})", "steel", smooth=False,
                note="Each flap rides on tracks (POH Figure 7-3); drawn as a slotted plate, representative")
            roller = plane.at(*slot_b)
            nose = A.wing_hinge_point(xabs, sx, A.FLAP_XC + 0.035)
            bm = new_bm()
            offset = plane.n * 0.006
            bar(bm, roller + offset, nose + offset, 0.02, 0.004, plane.n)
            disc(bm, roller, plane.n, 0.0065, 0.008, segs=12)
            add(ctx, f"{grp}.flap_roller_arm_{word_en}", bm, grp, f"Flap support arm and roller, {word_en} ({where_en})",
                f"ذراع إسناد القلاب وبكرته، {word_ar} ({where_ar})", "steel", status="estimated", smooth=False, parent=scene[f"{grp}.flap"],
                note="The arm carries a roller that runs in the flap track; representative")
        scene[f"{grp}.flap"]["assembly"] = ASSEMBLY

    # cables across the cabin roof, straight from one wing to the other
    for key in ("a", "b"):
        left, right = roof[(1, key)], roof[(-1, key)]
        station = left.y / IN + U.FS_ORIGIN
        middle = Vector((0.0, left.y, A.fus_top_z(station) - SKIN - 0.006))
        bm = new_bm()
        cable(bm, [left, middle, right], CABLE)
        add(ctx, f"CONTROLS.flap_cable_{key}", bm, "SYSTEMS", f"Flap synchronising cable {key.upper()}, across the cabin roof", f"كابل مزامنة القلابين {key.upper()}، عبر سقف المقصورة", "steel")

    # motor, transmission and screw, in the right wing inboard of the drive pulley
    sx = -1
    grp = "WING_R"
    frame, up = wing_frame(x_pulley, sx, xc_centre, dz)
    plate = Plane(frame.origin + frame.n * 0.012, frame.u, frame.v)
    screw_end = plate.at(0.0, -0.04)

    def on_line(bl):
        return lanes.wing_point("flap_screw", sx, bl)

    bm = new_bm()
    rod(bm, on_line(MOTOR_BL[0]), on_line(MOTOR_BL[1]), 0.025, segs=16)
    rod(bm, on_line(MOTOR_BL[0] - 0.5), on_line(MOTOR_BL[0]), 0.016, segs=12)
    add(ctx, "WING_R.flap_motor", bm, grp, "Flap motor (electric, in the right wing)", "محرك القلابات (كهربائي، في الجناح الأيمن)", "steel",
        note="The flaps are electrically driven (POH p.7-10); a 15-ampere FLAP circuit breaker protects the motor circuit. Position and size representative")
    bm = new_bm()
    box(bm, (0.085, 0.055, 0.05), center=on_line(MOTOR_BL[1] + 1.7))
    add(ctx, "WING_R.flap_transmission", bm, grp, "Flap transmission (gearbox between the motor and the screw)", "ناقل حركة القلابات (علبة تروس بين المحرك واللولب)",
        "cast_alu", smooth=False)
    bm = new_bm()
    rod(bm, on_line(MOTOR_BL[1] + 3.3), on_line(61.5), 0.006, segs=10)
    rod_end(bm, on_line(60.5), screw_end, 0.009)
    add(ctx, "WING_R.flap_jackscrew", bm, grp, "Flap actuator screw (the nut on it pushes the drive pulley round)", "لولب مشغّل القلابات (الصامولة عليه تدير بكرة التحريك)", "steel")
