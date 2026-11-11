"""The cabin as the handbook describes it: how the seats are adjusted, where the seat belts are fixed,
the doors and their openable window, the baggage net, the control lock, and the small things on and
under the instrument panel that the basic model leaves out.

What the handbook says, and this pack builds:
  seats       (p.7-11) the pilot's and front passenger's seats may be moved forward or aft: lift the
              tubular handle under the centre of the seat, slide the seat, release the handle and check
              that the seat is locked; the seat back angle is changed with a lever under the right
              front corner of the seat. The rear seat has a fixed one-piece bottom and two seat backs,
              each adjusted with a lever under its corner of the seat bottom.
  seat belts  (p.7-12 to 7-14, Figure 7-4) the seat belts are attached to fittings on the floorboard;
              each front shoulder harness is stowed behind a stowage sheath above the cabin door.
  doors       (p.7-15) a recessed outside handle and an inside handle on each door (basic model), a
              key-operated lock on the left door only, a door stop mechanism; the window of the left
              door opens outward: a latch on the lower edge of its frame holds it shut and a
              spring-loaded retaining arm holds it open. An openable right window is optional.
  baggage     (p.7-11) a baggage net with eight tie-down straps, tied to tie-down rings.
  control lock (p.7-16) a shaped steel rod with a red metal flag: it goes through the hole in the top
              of the pilot's control wheel shaft and the hole in the shaft collar on the instrument
              panel, and its flag then covers the ignition switch.
  panel       (Figure 7-2, p.7-6 to 7-9; p.7-28; p.7-35 to 7-38) the two light rheostat knobs, the
              lighter, the map compartment, the microphone on its bracket on the pedestal, the
              microphone and phone jacks near the lower left corner of the panel, the microphone
              keying switch on the left side of the pilot's control wheel, the airplane speaker.

What is from where:
  poh        that each of these exists, what it does and, where the handbook says so, where it is
  estimated  every form and size, the mechanism of the seat lock and of the door latch (the handbook
             says what the pilot does, not how the parts are made), the seat stops, the number and
             place of the tie-down rings, the place of the speaker.
The control lock is fitted only while the aircraft is parked: it is a part of detail level 2, in the
editable scene and the part tool, not in the web model, whose control wheel moves.
"""
import math

import bpy
from mathutils import Vector

from ..units import IN, fs, wl
from .. import airframe as A
from .. import cockpit as C
from . import structure_fuselage as SF
from .common import pipe, disc, rod, bar, dome, bolt, part, new_bm, box, tube, X, Y, Z

FLOOR = A.FLOOR_Z + 0.015          # top of the cabin floor panel
RAIL_TOP = FLOOR + 0.018           # top of a seat rail (structure_fuselage)
SEAT_BASE = FLOOR + 0.045          # centre line of the two base tubes of a front seat (cockpit.build_seats)
PAN_UNDERSIDE = 1.09               # underside of a seat cushion


def build(ctx):
    scene = bpy.data.objects
    build_seats(ctx, scene)
    build_belts(ctx, scene)
    build_doors(ctx, scene)
    build_baggage(ctx)
    build_control_lock(ctx, scene)
    build_panel_items(ctx, scene)


# ----------------------------------------------------------------------------- seats

def build_seats(ctx, scene):
    def add(name, bm, en, ar, mat="steel", status="poh", **tags):
        tags.setdefault("assembly", "seats")
        if status == "poh":
            tags.setdefault("ref", "p.7-11")
        return part(ctx, name, bm, "INTERIOR", "INTERIOR", en, ar, mat, status=status, smooth=tags.pop("smooth", True), **tags)

    y0 = fs(C.FRONT_SEAT_FS)
    for key, x, who_en, who_ar in (("pilot", 0.28, "pilot's seat", "مقعد الطيار"), ("copilot", -0.28, "front passenger's seat", "مقعد الراكب الأمامي")):
        name = f"INTERIOR.seat_{key}"
        # ---- four rollers: an inverted channel over the head of the rail, with the roller inside it
        bm = new_bm()
        for dx in (-0.12, 0.12):
            for dy in (0.06, 0.42):
                cx, cy = x + dx, y0 + dy
                box(bm, (0.036, 0.05, 0.004), center=(cx, cy, RAIL_TOP + 0.017))
                for sgn in (-1, 1):
                    box(bm, (0.003, 0.05, 0.0215), center=(cx + sgn * 0.0155, cy, RAIL_TOP + 0.00425))
                disc(bm, (cx, cy, RAIL_TOP + 0.0068), X, 0.0068, 0.02, segs=12)
        add(name + ".rollers", bm, f"Rollers of the {who_en}: the seat runs fore and aft on its two rails", f"بكرات {who_ar}: ينزلق المقعد إلى الأمام والخلف على سكّتيه", status="estimated", count=4,
            smooth=False, note="The front seats may be moved forward or aft (POH p.7-11); how the seat is carried on its rails is representative")
        # ---- seat lock: tubular handle under the centre of the seat, cross shaft, a pin into each rail
        shaft_y, shaft_z = y0 + 0.004, SEAT_BASE + 0.014
        bm = new_bm()
        rod(bm, (x - 0.12, shaft_y, shaft_z), (x + 0.12, shaft_y, shaft_z), 0.005, segs=8)
        pipe(bm, [Vector((x - 0.06, shaft_y, shaft_z)), Vector((x - 0.06, y0 - 0.034, shaft_z + 0.008)), Vector((x + 0.06, y0 - 0.034, shaft_z + 0.008)), Vector((x + 0.06, shaft_y, shaft_z))],
             0.006, bend=0.016)
        for sgn in (-1, 1):
            rod(bm, (x + sgn * 0.12, shaft_y, shaft_z), (x + sgn * 0.12, shaft_y, RAIL_TOP - 0.0045), 0.004, segs=8)        # the pin stands in a hole of the rail
        add(name + ".adjust_handle", bm, f"Seat lock of the {who_en}: tubular handle under the centre of the seat, with a pin into each rail",
            f"قفل {who_ar}: مقبض أنبوبي تحت منتصف المقعد، مع مسمار يدخل في كل سكة", "chrome",
            note="Lift the handle, slide the seat into position, release the handle and check that the seat is locked in place (POH p.7-11); the mechanism is representative")
        # ---- seat back lever under the right front corner, its rod to the seat back latch
        lx = x - 0.16
        bm = new_bm()
        bar(bm, (lx, y0 - 0.014, PAN_UNDERSIDE - 0.007), (lx, y0 + 0.11, PAN_UNDERSIDE - 0.012), 0.014, 0.004, Z)
        box(bm, (0.02, 0.02, 0.005), center=(lx, y0 - 0.022, PAN_UNDERSIDE - 0.007))
        rod(bm, (lx, y0 + 0.11, PAN_UNDERSIDE - 0.012), (lx, y0 + 0.42, PAN_UNDERSIDE - 0.012), 0.003, segs=6)
        box(bm, (0.02, 0.03, 0.02), center=(lx, y0 + 0.43, PAN_UNDERSIDE - 0.014))
        add(name + ".back_lever", bm, f"Seat back lever of the {who_en}: under the right front corner of the seat", f"ذراع ظهر {who_ar}: تحت الزاوية الأمامية اليمنى للمقعد", "chrome",
            note="Lift the lever, reposition the seat back, release the lever and check that the back is locked; the back is spring-loaded to the vertical position (POH p.7-11, four-way seat)")

    # ---- a stop at each end of each rail
    bm = new_bm()
    for x in (0.40, 0.16, -0.16, -0.40):
        for station, sign in ((SF.SEAT_RAIL_FS[0], 1), (SF.SEAT_RAIL_FS[1], -1)):
            centre = Vector((x, fs(station) + sign * 0.012, RAIL_TOP + 0.007))
            box(bm, (0.032, 0.016, 0.014), center=centre)
            dome(bm, centre + Z * 0.007, Z, 0.004, 0.003, sides=8, rings=1)
    part(ctx, "AIRFRAME.seat_stops", bm, "AIRFRAME", "AIRFRAME", "Seat stops: one at each end of each front seat rail", "مصدّات المقاعد: واحد عند كل طرف من كل سكة مقعد أمامي", "steel",
         status="estimated", assembly="seats", count=8, inside="fuselage", note="They keep a seat from running off its rails; not described in the POH, drawn representatively")

    # ---- rear seat: a lever for each seat back, under its corner of the seat bottom
    y0 = fs(C.REAR_SEAT_FS)
    for sgn, S, where_en, where_ar in ((1, "L", "left", "الأيسر"), (-1, "R", "right", "الأيمن")):
        lx = sgn * 0.335
        bm = new_bm()
        bar(bm, (lx, y0 - 0.014, PAN_UNDERSIDE - 0.007), (lx, y0 + 0.11, PAN_UNDERSIDE - 0.012), 0.014, 0.004, Z)
        box(bm, (0.02, 0.02, 0.005), center=(lx, y0 - 0.022, PAN_UNDERSIDE - 0.007))
        rod(bm, (lx, y0 + 0.11, PAN_UNDERSIDE - 0.012), (lx, y0 + 0.42, PAN_UNDERSIDE - 0.012), 0.003, segs=6)
        box(bm, (0.02, 0.03, 0.02), center=(lx, y0 + 0.43, PAN_UNDERSIDE - 0.014))
        add(f"INTERIOR.seat_rear.back_lever_{S}", bm, f"Adjustment lever of the {where_en} rear seat back: under the {where_en} corner of the seat bottom",
            f"ذراع ضبط ظهر المقعد الخلفي {where_ar}: تحت الزاوية {'اليسرى' if sgn > 0 else 'اليمنى'} لقاعدة المقعد", "chrome", ref="p.7-11, 7-12",
            note="The rear seat has a fixed one-piece bottom and individually adjustable seat backs: lift the lever and reposition the back (POH p.7-11, 7-12)")
    for name in list(scene.keys()):
        if name.startswith(("INTERIOR.seat_pilot.", "INTERIOR.seat_copilot.", "INTERIOR.seat_rear.")) and "assembly" not in scene[name]:
            scene[name]["assembly"] = "seats"


# ----------------------------------------------------------------------------- seat belts

def build_belts(ctx, scene):
    # ---- the ends of the seat belts and their fittings on the floorboard
    bm = new_bm()
    ends = [(x + s * 0.18, x + s * 0.15, fs(C.FRONT_SEAT_FS)) for x in (0.28, -0.28) for s in (1, -1)] + [(s * 0.36, s * 0.33, fs(C.REAR_SEAT_FS)) for s in (1, -1)]
    for x_belt, x_floor, y0 in ends:
        top = Vector((x_belt, y0 + 0.30, 1.08))
        foot = Vector((x_floor, y0 + 0.50, FLOOR + 0.012))
        bar(bm, top, foot, 0.045, 0.003, X)
        box(bm, (0.006, 0.032, 0.024), center=(x_floor, y0 + 0.505, FLOOR + 0.012))
        box(bm, (0.03, 0.04, 0.003), center=(x_floor, y0 + 0.505, FLOOR + 0.0015))
        bolt(bm, Vector((x_floor - 0.007, y0 + 0.505, FLOOR + 0.012)), X, 0.005, 0.014, nut=False)
    part(ctx, "INTERIOR.seat_belt_anchors", bm, "INTERIOR", "INTERIOR", "Seat belt anchors: the ends of the seat belts and their fittings on the floorboard", "مثبتات أحزمة المقاعد: أطراف الأحزمة ومرابطها على أرضية المقصورة",
         "belt", status="poh", ref="p.7-12", assembly="seats", count=6, note="All of the seat belts are attached to fittings on the floorboard; the buckle half is inboard of each front seat and the link half outboard "
                                                                              "(POH p.7-12). Where the fittings stand is representative")
    # ---- stowage sheath of each front shoulder harness, above the cabin door
    for sx, S, where_en, where_ar in ((1, "L", "left", "الأيسر"), (-1, "R", "right", "الأيمن")):
        bm = new_bm()
        bar(bm, SF.side_point(45.0, 66.2, sx, 0.046), SF.side_point(62.0, 66.2, sx, 0.046), 0.034, 0.008, X)
        part(ctx, f"INTERIOR.harness_sheath_{S}", bm, "INTERIOR", "INTERIOR", f"Stowage sheath of the shoulder harness, above the {where_en} cabin door", f"غمد تخزين حزام الكتف، فوق باب المقصورة {where_ar}",
             "interior_dark", status="poh", ref="p.7-12", assembly="seats", note="To stow the harness, fold it and place it behind the sheath (POH p.7-12); form representative")


# ----------------------------------------------------------------------------- doors and windows

def edge_station(a, b, water):
    """Station of the straight edge from a to b (FS, WL) at a water line."""
    return a[0] + (b[0] - a[0]) * (water - a[1]) / (b[1] - a[1])


def build_doors(ctx, scene):
    door_poly, window = A.DOOR, A.DOOR_WINDOW
    for sx, S, where_en, where_ar in ((1, "L", "left", "الأيسر"), (-1, "R", "right", "الأيمن")):
        door = scene.get(f"AIRFRAME.door_{S}")
        if door is None:
            continue

        def add(name, bm, en, ar, mat, status="poh", **tags):
            tags.setdefault("assembly", "doors")
            if status == "poh":
                tags.setdefault("ref", "p.7-15")
            return part(ctx, name, bm, "AIRFRAME", "AIRFRAME", en, ar, mat, status=status, smooth=tags.pop("smooth", False), parent=door, **tags)

        # ---- latch at the rear edge, worked by the inside and the outside handle
        water = 45.2
        rear = edge_station(door_poly[1], door_poly[2], water)
        latch = SF.side_point(rear - 1.7, water, sx, 0.022)
        bm = new_bm()
        box(bm, (0.018, 0.06, 0.04), center=latch)
        rod(bm, latch + Y * 0.03, latch + Y * 0.046, 0.005, segs=8)                                  # the bolt, into the rear door post
        inside = scene[f"INTERIOR.door_inner_handle_{S}"].matrix_world.translation.copy()
        rod(bm, Vector((sx * (abs(inside.x) + 0.022), inside.y + 0.01, inside.z)), latch + Vector((0.0, -0.03, -0.012)), 0.003, segs=6)
        outside = SF.side_point(60.7 - 3.35, water, sx, 0.012)
        rod(bm, outside, latch + Vector((0.0, -0.03, 0.008)), 0.003, segs=6)
        add(f"AIRFRAME.door_latch_{S}", bm, f"Latch of the {where_en} cabin door, with the rods from the inside and the outside handle", f"مزلاج باب المقصورة {where_ar}، مع القضيبين من المقبض الداخلي والخارجي",
            "steel", status="estimated", note="The door is pulled shut and latched, then locked with the inside handle (POH p.7-15); the latch and its rods are inside the door and drawn representatively")
        if sx > 0:
            # ---- key-operated lock: left door only
            bm = new_bm()
            disc(bm, SF.side_point(64.2, 43.0, sx, -0.003), X, 0.009, 0.008, segs=16)
            box(bm, (0.002, 0.008, 0.002), center=SF.side_point(64.2, 43.0, sx, -0.0075))
            add("AIRFRAME.door_lock_L", bm, "Key-operated lock of the left cabin door", "قفل بمفتاح لباب المقصورة الأيسر", "chrome", smooth=True, outside=True,
                note="Left door only: to lock the airplane, lock the right door with the inside handle, close the left door and lock it with the ignition key (POH p.7-15)")
        # ---- door stop
        low = 28.5
        front = edge_station(door_poly[0], door_poly[3], low)
        bm = new_bm()
        bar(bm, SF.side_point(front + 0.9, low, sx, 0.020), SF.side_point(front + 7.5, low, sx, 0.020), 0.02, 0.003, X)
        box(bm, (0.012, 0.02, 0.026), center=SF.side_point(front + 7.5, low, sx, 0.021))
        add(f"AIRFRAME.door_stop_{S}", bm, f"Door stop mechanism of the {where_en} cabin door", f"آلية إيقاف باب المقصورة {where_ar}", "steel", status="poh",
            note="The doors incorporate a door stop mechanism (POH p.7-15); its form and place are representative")
        # ---- openable window: hinge along the top, latch on the lower edge of the frame, spring-loaded retaining arm
        optional = dict(optional=True) if sx < 0 else {}
        note_right = " An openable right door window is optional equipment (POH p.7-15)." if sx < 0 else ""
        bm = new_bm()
        rod(bm, SF.side_point(window[3][0] + 1.6, window[3][1] + 0.35, sx, -0.004), SF.side_point(window[2][0] - 1.6, window[2][1] + 0.35, sx, -0.004), 0.004, segs=8)
        add(f"AIRFRAME.door_window_hinge_{S}", bm, f"Hinge of the {where_en} door window, along its upper edge", f"مفصلة نافذة الباب {where_ar}، بمحاذاة حافتها العلوية", "bare_alu", status="estimated",
            smooth=True, outside=True, note="The window opens outward about its upper edge; the hinge is drawn representatively." + note_right, **optional)
        mid = ((window[0][0] + window[1][0]) / 2, (window[0][1] + window[1][1]) / 2)
        body = SF.side_point(mid[0], mid[1] - 0.9, sx, 0.037)
        bm = new_bm()
        box(bm, (0.012, 0.05, 0.02), center=body)
        bar(bm, body, body + Vector((-sx * 0.03, 0.0, -0.012)), 0.014, 0.004, Y)
        add(f"AIRFRAME.door_window_latch_{S}", bm, f"Latch of the {where_en} door window, on the lower edge of the window frame", f"مزلاج نافذة الباب {where_ar}، على الحافة السفلية لإطار النافذة", "chrome",
            note="A detent equipped latch holds the window closed; to open the window, rotate the latch upward (POH p.7-15)." + note_right, **optional)
        a = SF.side_point(window[0][0] + 2.2, window[0][1] - 1.0, sx, 0.037)
        b = SF.side_point(window[0][0] + 9.5, window[0][1] - 1.5, sx, 0.037)
        bm = new_bm()
        rod(bm, a, b, 0.003, segs=6)
        rod(bm, a - Y * 0.004, a + Y * 0.03, 0.006, segs=8)                                           # its spring
        add(f"AIRFRAME.door_window_arm_{S}", bm, f"Spring-loaded retaining arm of the {where_en} door window", f"ذراع التثبيت النابضي لنافذة الباب {where_ar}", "steel", smooth=True,
            note="The retaining arm helps rotate the window outward and holds it there; the window may be opened at any speed up to 160 knots (POH p.7-15)." + note_right, **optional)
    for name in ("AIRFRAME.door_L", "AIRFRAME.door_R", "AIRFRAME.door_window_L", "AIRFRAME.door_window_R", "AIRFRAME.door_handle_L", "AIRFRAME.door_handle_R", "INTERIOR.door_inner_handle_L",
                 "INTERIOR.door_inner_handle_R", "INTERIOR.armrest_L", "INTERIOR.armrest_R", "AIRFRAME.door_hinge_L_lower", "AIRFRAME.door_hinge_L_upper", "AIRFRAME.door_hinge_R_lower",
                 "AIRFRAME.door_hinge_R_upper"):
        if name in scene:
            scene[name]["assembly"] = "doors"


# ----------------------------------------------------------------------------- baggage

def build_baggage(ctx):
    """Baggage net over baggage area 1 (behind the rear seat, station 82 to the rear cabin wall), with
    its eight straps tied to eight tie-down rings."""
    front, rear, half, height = fs(89.5), fs(109.5), 0.33, 1.22
    floor = lambda station: A.floor_z(station) + 0.015
    rings = [Vector((s * 0.30, fs(86.0), floor(86.0))) for s in (1, -1)] + [Vector((s * 0.30, fs(110.3), floor(110.3))) for s in (1, -1)]
    rings += [SF.side_point(station, 27.5, s, 0.05) for station in (93.0, 104.0) for s in (1, -1)]
    corners = [Vector((half, front, height)), Vector((-half, front, height)), Vector((half, rear, height)), Vector((-half, rear, height)),
               Vector((half, front + (rear - front) * 0.28, height)), Vector((-half, front + (rear - front) * 0.28, height)),
               Vector((half, front + (rear - front) * 0.72, height)), Vector((-half, front + (rear - front) * 0.72, height))]
    bm = new_bm()
    tube(bm, [Vector((half, front, height)), Vector((half, rear, height)), Vector((-half, rear, height)), Vector((-half, front, height)), Vector((half, front, height))], 0.004, segs=6)
    for k in range(1, 8):
        y = front + (rear - front) * k / 8
        tube(bm, [Vector((-half, y, height)), Vector((half, y, height))], 0.002, segs=4)
    for k in range(1, 10):
        x = -half + 2 * half * k / 10
        tube(bm, [Vector((x, front, height)), Vector((x, rear, height))], 0.002, segs=4)
    for corner, ring in zip(corners, rings):
        tube(bm, [corner, ring + Z * 0.012], 0.003, segs=5)
    part(ctx, "INTERIOR.baggage_net", bm, "INTERIOR", "INTERIOR", "Baggage net with its eight tie-down straps", "شبكة الأمتعة مع أشرطة ربطها الثمانية", "belt", status="poh", ref="p.7-11",
         assembly="baggage", smooth=True, inside="fuselage", note="The net secures the baggage and is attached by tying its straps to the tie-down rings (POH p.7-11); it is drawn stretched over an empty "
                                                                    "baggage area 1, station 82 to 108 (POH Figure 6-3)")
    bm = new_bm()
    for ring in rings:
        on_floor = abs(ring.z - floor((ring.y / IN) + 40.0)) < 0.002
        axis = Y if on_floor else Y
        box(bm, (0.03, 0.03, 0.003) if on_floor else (0.003, 0.03, 0.03), center=ring)
        disc(bm, ring + (Z * 0.012 if on_floor else Vector((-math.copysign(0.012, ring.x), 0.0, 0.0))), axis, 0.011, 0.004, segs=14, bore=0.007)
    part(ctx, "INTERIOR.baggage_tiedown_rings", bm, "INTERIOR", "INTERIOR", "Baggage tie-down rings", "حلقات ربط الأمتعة", "steel", status="poh", ref="p.7-11", assembly="baggage", count=8,
         smooth=True, inside="fuselage", note="The straps of the baggage net are tied to tie-down rings provided in the airplane (POH p.7-11); their number and place are representative")


# ----------------------------------------------------------------------------- control lock

def build_control_lock(ctx, scene):
    shaft = scene["INTERIOR.yoke_shaft_L"].matrix_world.translation.copy()       # on the axis of the pilot's control wheel shaft, at the face of the instrument panel
    panel_face = shaft.y
    switch = scene["PANEL.ignition_switch"].matrix_world.translation.copy()
    lower_face = switch.y + C.LOWER_FACE                                            # aft face of the subpanel
    # ---- the collar of each control wheel shaft on the instrument panel
    bm = new_bm()
    for sx in (1, -1):
        disc(bm, (sx * abs(shaft.x), panel_face + 0.015, shaft.z), Y, 0.021, 0.03, segs=20, bore=0.0135)
    part(ctx, "PANEL.control_wheel_collars", bm, "PANEL", "INTERIOR", "Shaft collars of the control wheels, on the instrument panel", "طوقا عمودي عجلتي القيادة على لوحة العدادات", "black_plastic",
         status="poh", ref="p.7-16", assembly="control_lock", count=2, smooth=True, note="The hole in the top of the pilot's shaft collar takes the control lock (POH p.7-16); form representative")
    # ---- the lock: a rod through collar and shaft, bent over and down to a red flag in front of the ignition switch
    y_lock = panel_face + 0.015
    y_flag = lower_face + 0.046                                                   # clear of the key
    top = shaft.z + 0.050
    bm = new_bm()
    pipe(bm, [Vector((shaft.x, y_lock, shaft.z - 0.026)), Vector((shaft.x, y_lock, top)), Vector((switch.x, y_flag, top)), Vector((switch.x, y_flag, switch.z + 0.040))],
         0.0035, bend=0.012)
    box(bm, (0.08, 0.002, 0.088), center=(switch.x, y_flag, switch.z))
    part(ctx, "INTERIOR.control_lock", bm, "INTERIOR", "INTERIOR", "Control lock: a steel rod with a red flag, through the pilot's control wheel shaft and its collar",
         "قفل التحكم: قضيب فولاذي بعلم أحمر، يمر عبر عمود عجلة قيادة الطيار وطوقه", "knob_red", detail=2, status="poh", ref="p.7-16", assembly="control_lock",
         note="Locks the ailerons and the elevator in neutral while the airplane is parked. Its flag, labelled CONTROL LOCK, REMOVE BEFORE STARTING ENGINE, covers the ignition switch "
              "(POH p.7-16). Fitted only on the ground: shown in the editable scene and by the part tool, not in the web model")
    for name in ("INTERIOR.yoke_L", "INTERIOR.yoke_shaft_L", "PANEL.ignition_switch"):
        if name in scene:
            scene[name]["assembly"] = ",".join([a for a in str(scene[name].get("assembly", "")).split(",") if a] + ["control_lock"])


# ----------------------------------------------------------------------------- on and under the instrument panel

def build_panel_items(ctx, scene):
    face = scene["PANEL.ignition_switch"].matrix_world.translation.y + C.LOWER_FACE       # aft face of the subpanel

    def panel(name, bm, en, ar, mat, ref, system="PANEL", group="PANEL", **tags):
        return part(ctx, name, bm, group, system, en, ar, mat, status=tags.pop("status", "poh"), ref=ref, smooth=tags.pop("smooth", True), **tags)

    # ---- the two rheostat knobs of the instrument and radio lights
    bm = new_bm()
    for x in (-0.037, -0.060):                 # under the throttle, on its right
        disc(bm, (x, face + 0.002, 1.336), Y, 0.0095, 0.004, segs=16)
        disc(bm, (x, face + 0.010, 1.336), Y, 0.0070, 0.012, segs=14)
    panel("PANEL.light_rheostats", bm, "Instrument and radio dial light rheostat control knobs (PANEL LT, RADIO LT)", "مقبضا التحكم بشدة إضاءة العدادات وأقراص الراديو (PANEL LT و RADIO LT)", "black_plastic",
          "p.7-7 (Fig 7-2), 7-28", system="ELECTRICAL", assembly="lighting", count=2, note="Two rheostat knobs set the intensity of the instrument panel lighting and of the radio lighting (POH p.7-28); "
                                                                                             "their place on the panel is representative")
    # ---- lighter and map compartment
    bm = new_bm()
    disc(bm, (-0.262, face + 0.002, 1.362), Y, 0.011, 0.004, segs=16)
    disc(bm, (-0.262, face + 0.010, 1.362), Y, 0.0085, 0.012, segs=14)
    panel("PANEL.lighter", bm, "Lighter", "ولاعة", "chrome", "p.7-7 (Fig 7-2)", note="Named in the instrument panel figure; its place on the panel is representative")
    bm = new_bm()
    box(bm, (0.086, 0.003, 0.074), center=(-0.445, face + 0.0015, 1.3775))
    disc(bm, (-0.410, face + 0.006, 1.3775), Y, 0.005, 0.006, segs=10)
    panel("PANEL.map_compartment", bm, "Map compartment (door)", "حجرة الخرائط (الباب)", "panel_grey", "p.7-7 (Fig 7-2), 7-9", smooth=False,
          note="The right side of the subpanel contains the map compartment (POH p.7-9); size representative")
    # ---- microphone and phone jacks near the lower left corner of the panel
    bm = new_bm()
    for z in (1.375, 1.398):
        disc(bm, (0.485, face + 0.003, z), Y, 0.007, 0.006, segs=12, bore=0.003)
    panel("PANEL.microphone_jacks", bm, "Microphone and phone jacks, near the lower left corner of the instrument panel", "مقبسا الميكروفون والسماعة، قرب الزاوية السفلية اليسرى من لوحة العدادات",
          "chrome", "p.7-7 (Fig 7-2), 7-38", system="AVIONICS", assembly="avionics", count=2, note="The microphone and headset jacks are located near the lower left corner of the instrument panel (POH p.7-38)")
    # ---- hand microphone on its bracket on the pedestal
    pedestal = scene["INTERIOR.pedestal"]
    aft = max((pedestal.matrix_world @ Vector(c)).y for c in pedestal.bound_box)
    hang = Vector((-0.02, aft + 0.016, 1.262))
    bm = new_bm()
    box(bm, (0.044, 0.026, 0.07), center=hang)
    box(bm, (0.05, 0.004, 0.03), center=(hang.x, aft + 0.002, hang.z + 0.01))                         # the bracket
    cord = []
    turns, top, bottom = 9, hang.z - 0.035, hang.z - 0.19
    for i in range(turns * 8 + 1):
        t = i / (turns * 8)
        angle = 2 * math.pi * turns * t
        cord.append(Vector((hang.x + 0.007 * math.cos(angle), aft + 0.018 + 0.007 * math.sin(angle), top + (bottom - top) * t)))
    cord.append(Vector((hang.x, aft + 0.002, bottom - 0.01)))
    tube(bm, cord, 0.0022, segs=5)
    panel("INTERIOR.microphone", bm, "Hand microphone on its bracket on the control pedestal", "ميكروفون يدوي على حامله في قاعدة التحكم", "black_plastic", "p.7-7 (Fig 7-2), 7-9", system="AVIONICS",
          group="INTERIOR", assembly="avionics", note="The pedestal provides a bracket for the microphone (POH p.7-9); form representative")
    # ---- microphone keying switch on the left side of the pilot's control wheel
    yoke = scene["INTERIOR.yoke_L"]
    hub = yoke.matrix_world.translation.copy()
    bm = new_bm()
    box(bm, (0.009, 0.007, 0.013), center=hub + Vector((0.171, 0.0325, 0.086)))            # on the aft face of the left grip, under the thumb
    panel("INTERIOR.microphone_switch", bm, "Microphone keying switch, on the left side of the pilot's control wheel", "مفتاح تشغيل الميكروفون، على الجانب الأيسر من عجلة قيادة الطيار", "knob_red",
          "p.7-37, 7-38", system="AVIONICS", group="INTERIOR", assembly="avionics", optional=True, parent=yoke, smooth=False,
          note="Part of the microphone-headset combination: the pilot can transmit without taking a hand from the control wheel (POH p.7-37, 7-38)")
    # ---- the airplane speaker, in the cabin ceiling
    station = 58.5
    bm = new_bm()
    centre = Vector((0.0, fs(station), A.headliner_z(station) - 0.004))
    disc(bm, centre, Z, 0.055, 0.010, segs=24)
    for r in (0.018, 0.032, 0.046):
        disc(bm, centre - Z * 0.0055, Z, r + 0.003, 0.002, segs=24, bore=r)
    panel("ELECTRICAL.speaker", bm, "Airplane speaker, in the cabin ceiling", "مكبر صوت الطائرة، في سقف المقصورة", "black_plastic", "p.7-35 to 7-37", system="AVIONICS", group="INTERIOR",
          assembly="avionics", status="poh", note="Receiver audio is heard on the airplane speaker or on a headset, as selected on the audio control panel (POH p.7-35 to 7-37); where the speaker is "
                                                  "mounted is representative")
