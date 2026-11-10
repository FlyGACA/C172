"""What is fitted to the aircraft or used on it only on the ground: the things the preflight inspection
takes off or uses.

What the handbook says (Preflight Inspection, p.4-4 to 4-6, Figure 4-1; p.7-9; p.7-16):
  control wheel lock - REMOVE (detail/cabin.py builds it);
  rudder gust lock - REMOVE: a control surface lock over the vertical stabiliser and rudder (p.7-16);
  tail, wing and nose tie-downs - DISCONNECT;
  pitot tube cover - REMOVE;
  a sampler cup, with which a small quantity of fuel is drained from each fuel tank sump quick-drain
  valve before the first flight of the day and after each refuelling;
  a tow bar, attached to the nose gear, with which the aircraft is most easily moved by hand (p.7-9).

What is from where:
  poh        that each of these exists and what it is for
  estimated  every form and size, and where a rope is made fast to the ground.

All of it is detail level 2: in the editable scene and the part tool, where a figure of the preflight
inspection can show it, and in no web model.
"""
import bpy
from mathutils import Vector

from .. import units as U
from ..units import fs, wl
from .. import airframe as A
from .common import disc, rod, part, new_bm, box, tube, X, Y, Z

LEVEL = 2
SYS = "GROUND_EQUIPMENT"
ASSEMBLY = "ground_equipment"
REF = "p.4-5, 4-6 (Fig 4-1)"


def add(ctx, name, bm, group, en, ar, mat, status="poh", **tags):
    tags.setdefault("assembly", ASSEMBLY)
    tags.setdefault("ref", REF)
    # kit: not part of the aircraft as it flies, so left out of its measured envelope and shown in a figure only when named
    return part(ctx, name, bm, group, SYS, en, ar, mat, detail=2, status=status, smooth=tags.pop("smooth", True), outside=True, kit=True, **tags)


def ground_under(point):
    """The point on the ground straight under a build-frame point."""
    return Vector((point.x, point.y, U.ground_z(point.y)))


def rope(bm, ring, anchor, sag=0.03):
    middle = (ring + anchor) / 2 - Z * sag
    tube(bm, [ring, ring * 0.7 + anchor * 0.3 - Z * sag * 0.8, middle, ring * 0.3 + anchor * 0.7 - Z * sag * 0.8, anchor], 0.005, segs=6)
    disc(bm, anchor - Z * 0.004, Z, 0.035, 0.008, segs=14)                 # the ramp tie-down
    disc(bm, anchor + Z * 0.012, X, 0.014, 0.005, segs=12, bore=0.009)


def build(ctx):
    scene = bpy.data.objects
    # ---- rudder gust lock: two plates over the fin and the rudder, bolted together through the gap, with a streamer
    water = 62.0
    (s0, w0), (s1, w1) = A.RUD_HINGE
    station = s0 + (s1 - s0) * (water - w0) / (w1 - w0)
    half = A.fin_half_thickness(station - 2.0, water)
    centre = Vector((0.0, fs(station), wl(water)))
    bm = new_bm()
    for sx in (1, -1):
        box(bm, (0.006, 0.26, 0.12), center=centre + X * (sx * (half + 0.006)))
    for dz in (-0.04, 0.04):
        rod(bm, centre + Vector((-half - 0.014, 0.0, dz)), centre + Vector((half + 0.014, 0.0, dz)), 0.003, segs=6)
    box(bm, (0.002, 0.035, 0.38), center=centre + Vector((half + 0.011, 0.05, -0.25)))
    add(ctx, "EMPENNAGE.rudder_gust_lock", bm, "EMPENNAGE", "Rudder gust lock: a control surface lock over the vertical stabiliser and the rudder", "قفل الدفة ضد هبّات الريح: قفل سطح تحكم فوق المثبت الرأسي والدفة",
        "knob_red", ref="p.4-5, 7-16", smooth=False, note="Fitted where high or gusty winds occur; removed in the preflight inspection (POH p.4-5, 7-16). Form representative")
    # ---- pitot tube cover with its streamer
    pitot = scene["PITOT_STATIC.pitot_tube"]
    corners = [pitot.matrix_world @ Vector(c) for c in pitot.bound_box]
    tip_y = min(c.y for c in corners); low = min(c.z for c in corners); x = pitot.matrix_world.translation.x
    axis = low + 0.011
    bm = new_bm()
    rod(bm, (x, tip_y - 0.008, axis), (x, tip_y + 0.07, axis), 0.016, segs=14)
    box(bm, (0.002, 0.03, 0.30), center=(x, tip_y + 0.03, axis - 0.165))
    add(ctx, "WING_L.pitot_tube_cover", bm, "WING_L", "Pitot tube cover, with its streamer", "غطاء أنبوب البيتوت، مع شريطه", "knob_red", ref="p.4-6", smooth=False,
        note="Removed in the preflight inspection, and the opening checked for stoppage (POH p.4-6). Form representative")
    # ---- tie-downs: a rope from each wing tie-down, from the tail tie-down and from the nose gear to the ramp
    for sx, S, where_en, where_ar in ((1, "L", "left", "الأيسر"), (-1, "R", "right", "الأيمن")):
        ring = scene[f"WING_{S}.tiedown"].matrix_world.translation.copy() - Z * 0.02
        anchor = ground_under(ring + Vector((sx * 0.75, 0.25, 0.0)))
        bm = new_bm()
        rope(bm, ring, anchor)
        add(ctx, f"WING_{S}.tie_down_rope", bm, f"WING_{S}", f"Tie-down rope of the {where_en} wing", f"حبل ربط الجناح {where_ar}", "belt",
            note="Wing tie-down: disconnected in the preflight inspection (POH p.4-5, 4-6). Where it is made fast on the ramp is representative")
    ring = scene["AIRFRAME.tail_tiedown"].matrix_world.translation.copy() - Z * 0.025
    bm = new_bm()
    rope(bm, ring, ground_under(ring + Y * 0.45))
    add(ctx, "AIRFRAME.tail_tie_down_rope", bm, "AIRFRAME", "Tail tie-down rope", "حبل ربط الذيل", "belt", ref="p.4-5",
        note="Tail tie-down: disconnected in the preflight inspection (POH p.4-5)")
    links = scene["GEAR.nose_torque_links"].matrix_world.translation.copy() - Z * 0.06
    bm = new_bm()
    rope(bm, links + Y * 0.03, ground_under(links + Vector((0.0, 0.55, 0.0))), sag=0.01)
    add(ctx, "GEAR.nose_tie_down_rope", bm, "GEAR", "Nose tie-down rope, on the nose gear", "حبل ربط المقدمة، على عجلة المقدمة", "belt", ref="p.4-6",
        note="Nose tie-down: disconnected in the preflight inspection (POH p.4-6). Where the rope is made fast to the nose gear is representative")
    # ---- fuel sampler cup, held under the quick-drain valve of the left tank
    drain = scene["WING_L.fuel_tank_drain"]
    bottom = min((drain.matrix_world @ Vector(c)).z for c in drain.bound_box)
    top = Vector((drain.matrix_world.translation.x, drain.matrix_world.translation.y, bottom - 0.004))
    bm = new_bm()
    disc(bm, top - Z * 0.05, Z, 0.021, 0.10, segs=20, bore=0.019)
    disc(bm, top - Z * 0.099, Z, 0.021, 0.002, segs=20)
    rod(bm, top - Z * 0.098, top + Z * 0.002, 0.0018, segs=6)                # the pin that opens the valve
    add(ctx, "WING_L.fuel_sampler_cup", bm, "WING_L", "Fuel sampler cup, under the sump quick-drain valve of the left tank", "كوب عيّنة الوقود، تحت صمام التصريف السريع لحوض الخزان الأيسر", "glass",
        ref="p.4-5", note="Before the first flight of the day and after each refuelling a small quantity of fuel is drained from each tank sump and checked for water, sediment and "
                          "the proper fuel grade (POH p.4-5). Form representative")
    # ---- tow bar on the nose gear
    tyre = scene["GEAR.nose_wheel.tyre"].matrix_world.translation.copy()      # on the axle
    ground = U.ground_z(tyre.y)
    joint = Vector((0.0, tyre.y - 0.55, ground + 0.21))
    grip = Vector((0.0, tyre.y - 1.75, ground + 0.60))
    bm = new_bm()
    for sx in (1, -1):
        tube(bm, [Vector((sx * 0.085, tyre.y, tyre.z)), Vector((sx * 0.085, tyre.y - 0.12, tyre.z)), joint], 0.009, segs=8)
        disc(bm, Vector((sx * 0.085, tyre.y, tyre.z)), X, 0.018, 0.012, segs=12)
    tube(bm, [joint, grip], 0.012, segs=10)
    rod(bm, grip - X * 0.16, grip + X * 0.16, 0.012, segs=10)
    add(ctx, "GEAR.tow_bar", bm, "GEAR", "Tow bar, attached to the nose gear", "قضيب السحب، موصول بعجلة المقدمة", "steel", ref="p.7-9",
        note="Moving the airplane by hand is most easily done with a tow bar attached to the nose gear strut; when it is towed by a vehicle the nose wheel must never be turned "
             "more than 30 degrees either side of centre (POH p.7-9). Form representative")
    lock = scene.get("INTERIOR.control_lock")
    if lock is not None:
        lock["assembly"] = ",".join([a for a in str(lock.get("assembly", "")).split(",") if a] + [ASSEMBLY])
        lock["kit"] = True
