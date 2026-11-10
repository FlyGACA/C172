"""Wheel brakes (POH p.7-23).

What the handbook says, and this pack builds: a single-disc, hydraulically actuated brake on each
main wheel; each brake is connected by a hydraulic line to a master cylinder attached to each of the
pilot's rudder pedals; the copilot's pedals are interconnected with the pilot's; a parking brake is
worked by a handle under the left side of the instrument panel.

What is from where:
  poh        the members above
  estimated  the form of the master cylinders, the route of the two pipes (lanes.py: under the floor
             to the main-gear bulkhead and out along each leg) and the parking brake linkage.
The basic model already has the brake discs, the calipers and the pipe along each gear leg.
"""
import bpy
from mathutils import Vector

from ..units import fs
from .. import airframe as A
from ..gear import main_leg_points
from . import lanes
from .common import pipe, union, rod, rod_end, bar, part, new_bm, X

SYS = "BRAKES"
REF = "p.7-23"
ASSEMBLY = "brake_system"
PIPE = 0.003                      # 1/4 in brake pipe as drawn


def add(ctx, name, bm, group, en, ar, mat, status="poh", smooth=True, **tags):
    tags.setdefault("assembly", ASSEMBLY)
    if status == "poh":
        tags.setdefault("ref", REF)
    return part(ctx, name, bm, group, SYS, en, ar, mat, status=status, smooth=smooth, **tags)


def build(ctx):
    scene = bpy.data.objects
    floor_top = A.floor_z(6) + 0.015
    # the pilot's two pedals: the outer one works the left brake, the inner one the right brake
    pedals = {"L": scene["INTERIOR.pedal_L_R"].matrix_world.translation.copy(), "R": scene["INTERIOR.pedal_L_L"].matrix_world.translation.copy()}
    lower = {}
    for S, pivot in pedals.items():
        where_en, where_ar = ("left", "الأيسر") if S == "L" else ("right", "الأيمن")
        top = Vector((pivot.x, pivot.y - 0.012, pivot.z + 0.105))
        bottom = Vector((pivot.x, fs(5.6), floor_top + 0.012))
        axis = (bottom - top).normalized()
        bm = new_bm()
        rod(bm, top + axis * 0.045, bottom - axis * 0.01, 0.013, segs=12)          # cylinder body
        rod_end(bm, top, top + axis * 0.05, 0.004, eye=0.006)                        # piston rod up to the pedal
        bar(bm, bottom - axis * 0.012, bottom + Vector((0, 0, -0.012)), 0.024, 0.004, X)
        add(ctx, f"BRAKES.master_cylinder_{S}", bm, "SYSTEMS", f"Brake master cylinder on the pilot's pedal for the {where_en} brake",
            f"الأسطوانة الرئيسية للكوابح على دواسة الطيار للكابح {where_ar}", "cast_alu",
            note="A master cylinder is attached to each of the pilot's rudder pedals (POH): pressing the top of a pedal works the brake of that side; form representative")
        lower[S] = bottom

    # pipes from the master cylinders, under the floor, to the main-gear legs
    # each pipe is down on its lane before the first frame it passes (the frames lean: at this height frame 17 stands near station 15.5)
    left = [lower["L"] + Vector((0, 0.012, 0)), Vector((0.34, fs(8.0), 0.925)), Vector(lanes.point("brake_L_fwd", 12.8)), Vector(lanes.point("brake_L_fwd", 21.0)),
            Vector(lanes.point("brake_L", 25.0)), Vector(lanes.point("brake_L", 66.4))]
    # the right brake's pipe starts on the left of the cabin: it turns across outboard of the left keel beam, so that it passes the beam square
    right = [lower["R"] + Vector((0, 0.012, 0)), Vector((lower["R"].x + 0.03, fs(10.5), 0.905)), Vector((lower["R"].x + 0.04, fs(lanes.ACROSS["brake_R_cross"][0]), lanes.CROSS_LEVEL)),
             Vector((lanes.ALONG["brake_R_fwd"][0], fs(lanes.ACROSS["brake_R_cross"][0]), lanes.CROSS_LEVEL)), Vector(lanes.point("brake_R_fwd", 21.0)),
             Vector(lanes.point("brake_R", 25.0)), Vector(lanes.point("brake_R", 66.4))]
    for S, corners, sx in (("L", left, 1), ("R", right, -1)):
        where_en, where_ar = ("left", "الأيسر") if S == "L" else ("right", "الأيمن")
        bm = new_bm()
        pipe(bm, corners, PIPE, bend=0.025)
        union(bm, corners[0], corners[1] - corners[0], PIPE)
        add(ctx, f"BRAKES.line_{S}", bm, "SYSTEMS", f"Brake hydraulic line, {where_en}: master cylinder to the main-gear bulkhead",
            f"خط الكوابح الهيدروليكي {where_ar}: من الأسطوانة الرئيسية إلى حاجز عجلات الهبوط الرئيسية", "bare_alu",
            note="Each brake is connected by a hydraulic line to its master cylinder (POH); the route under the floor is representative")
        leg, _axle, _attach = main_leg_points(sx)
        bm = new_bm()
        pipe(bm, [corners[-1], leg[1] + Vector((0, 0.032, 0.012)), leg[2] + Vector((0, 0.032, 0))], PIPE, bend=0.02)
        part(ctx, f"GEAR.brake_line_feed_{S}", bm, "GEAR", SYS, f"Brake hydraulic line, {where_en}: from under the floor out to the gear leg",
             f"خط الكوابح الهيدروليكي {where_ar}: من تحت الأرضية إلى ساق العجلة", "bare_alu", status="estimated", smooth=True, assembly=ASSEMBLY,
             joins=f"GEAR.main_leg_{S}")

    # parking brake: a control from the handle under the panel to a lock on the two master cylinders
    handle = scene["INTERIOR.parking_brake"].matrix_world.translation.copy()
    tops = [Vector((p.x, p.y - 0.012, p.z + 0.105)) for p in pedals.values()]
    middle = (tops[0] + tops[1]) / 2 + Vector((0, 0.02, 0.01))
    bm = new_bm()
    pipe(bm, [handle + Vector((0, -0.02, 0)), handle + Vector((0, -0.14, -0.06)), middle + Vector((0, 0.06, 0.04)), middle], 0.0025, bend=0.04)
    add(ctx, "BRAKES.parking_brake_control", bm, "SYSTEMS", "Parking brake control (handle to the master cylinders)", "وصلة كابح الوقوف (من المقبض إلى الأسطوانات الرئيسية)", "steel",
        status="estimated", note="The parking brake holds the pressure set with the pedals (POH p.7-23: set the brakes, pull the handle aft, turn it 90 degrees down); linkage representative")
    bm = new_bm()
    bar(bm, tops[0] + Vector((0, 0.02, 0.01)), tops[1] + Vector((0, 0.02, 0.01)), 0.016, 0.004, Vector((0, 1, 0)))
    add(ctx, "BRAKES.parking_brake_lock", bm, "SYSTEMS", "Parking brake lock bar across the two master cylinders", "قضيب قفل كابح الوقوف على الأسطوانتين الرئيسيتين", "steel",
        status="estimated", smooth=False, note="Representative")

    for name in ("GEAR.brake_line_L", "GEAR.brake_line_R", "GEAR.main_wheel_L.brake_disc", "GEAR.main_wheel_R.brake_disc", "GEAR.main_wheel_L.brake_caliper",
                 "GEAR.main_wheel_R.brake_caliper", "INTERIOR.parking_brake"):
        if name in scene:
            scene[name]["assembly"] = ASSEMBLY
