"""Fuel system (POH p.7-20 to 7-23, Figures 7-5 and 7-6).

What the handbook says, and this pack builds:
  two vented tanks, one in each wing (standard 21.5 US gal each); fuel flows by gravity through two
  outlets of each tank to a four-position selector valve (BOTH, RIGHT, LEFT, OFF), then through a
  strainer to the carburetor; a manual primer draws fuel from the strainer and injects it into the
  cylinder intake ports; the two tanks are joined by a vent line, the left tank is vented overboard
  through a line with a check valve near the wing strut, and the right filler cap is vented; a
  float-type transmitter in each tank works the fuel quantity indicators; each tank sump has a
  quick-drain valve.

What is from where:
  poh        the members above and how they are joined
  estimated  where everything lies. The tank fills the bay between the spars from the root rib to
             wing station 55.6 (structure_wing.TANK_BAY); that bay holds about 21.5 US gal, the
             standard tank. The pipes follow lanes.py: down the door posts, under the floor to the
             valve between the front seats, forward to the strainer on the firewall. The basic model
             already has the selector handle, the strainer, the pipe from the strainer to the
             carburetor, the filler caps and the overboard vent.
"""
import bpy
from mathutils import Vector

from .. import units as U
from ..units import IN, fs
from .. import airframe as A
from . import lanes
from . import structure_fuselage as SF
from . import structure_wing as SW
from .structure_fuselage import SKIN
from .common import extrude_along, rect_section, pipe, union, disc, rod, part, new_bm, loft, Z

SYS = "FUEL"
REF = "p.7-20 to 7-23 (Fig 7-6)"
NOTE = "Shown in the POH fuel system schematic (Figure 7-6); its position and size here are representative"
ASSEMBLY = "fuel_system"
PIPE = 0.0048                      # 3/8 in fuel pipe as drawn
TANK_BL = (SW.TANK_BAY[0] + 1.4, SW.TANK_BAY[1] - 1.4)
TANK_XC = (0.185, 0.615)
TANK_CLEARANCE = 0.008
VALVE = Vector((0.0, fs(44.0), 0.875))


def add(ctx, name, bm, group, en, ar, mat, status="poh", smooth=True, **tags):
    tags.setdefault("assembly", ASSEMBLY)
    if status == "poh":
        tags.setdefault("ref", REF)
        tags.setdefault("note", NOTE)
    return part(ctx, name, bm, group, SYS, en, ar, mat, status=status, smooth=smooth, **tags)


def tank_ring(xabs, side, count=10):
    c = A.wing_chord(xabs)
    xs = [TANK_XC[0] + (TANK_XC[1] - TANK_XC[0]) * i / count for i in range(count + 1)]
    lower = [A.wing_surface_point(xabs, side, xc, False, inset=TANK_CLEARANCE / c) for xc in xs]
    upper = [A.wing_surface_point(xabs, side, xc, True, inset=TANK_CLEARANCE / c) for xc in reversed(xs)]
    return lower + upper


def build(ctx):
    scene = bpy.data.objects
    for sx, S in ((1, "L"), (-1, "R")):
        grp = "WING_" + S
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        stations = [TANK_BL[0] + (TANK_BL[1] - TANK_BL[0]) * i / 5 for i in range(6)]

        # ---- tank, straps, quantity transmitter, sump drain
        bm = new_bm()
        loft(bm, [tank_ring(st * IN, sx) for st in stations], close=True, cap_start=True, cap_end=True)
        add(ctx, f"{grp}.fuel_tank", bm, grp, f"Fuel tank, {where_en} wing (standard tank: 21.5 US gal, 20 usable)",
            f"خزان الوقود في الجناح {where_ar} (الخزان القياسي: 21.5 غالون أمريكي، 20 قابلة للاستخدام)", "bare_alu", smooth=False, ref="p.7-20, 7-21 (Fig 7-5, 7-6)",
            note="One vented tank in each wing (POH). It is drawn filling the bay between the spars from the root rib to wing station 55.6, "
                 "which holds about 21.5 US gal; the real tank's outline is not in the POH")
        for number, st in enumerate((TANK_BL[0] + 7.0, TANK_BL[1] - 7.0), 1):
            c = A.wing_chord(st * IN)
            path, ups = [], []
            for i in range(11):
                xc = TANK_XC[0] + (TANK_XC[1] - TANK_XC[0]) * i / 10
                path.append(A.wing_surface_point(st * IN, sx, xc, True, inset=(TANK_CLEARANCE - 0.0012) / c))
                ups.append((A.wing_point(st * IN, sx, xc, 1.0) - A.wing_point(st * IN, sx, xc, 0.0)).normalized())
            bm = new_bm()
            extrude_along(bm, path, rect_section(0.03, 0.0012), lambda i: ups[i])
            add(ctx, f"{grp}.fuel_tank_strap_{number}", bm, grp, "Fuel tank hold-down strap", "حزام تثبيت خزان الوقود", "steel", status="estimated", smooth=False,
                note="How the tank is held in its bay is not in the POH; representative")
        inboard = TANK_BL[0] * IN
        centre = A.wing_hinge_point(inboard, sx, 0.40)
        span = (A.wing_hinge_point(inboard + 0.1, sx, 0.40) - centre).normalized()
        chordwise = (A.wing_hinge_point(inboard, sx, 0.5) - centre).normalized()
        bm = new_bm()
        disc(bm, centre - span * 0.004, span, 0.032, 0.008, segs=16)
        rod(bm, centre, centre + span * 0.19 + Z * 0.02, 0.003, segs=6)
        rod(bm, centre + span * 0.19 + Z * 0.02 - chordwise * 0.03, centre + span * 0.19 + Z * 0.02 + chordwise * 0.03, 0.016, segs=10)
        add(ctx, f"{grp}.fuel_quantity_transmitter", bm, grp, f"Fuel quantity transmitter, {where_en} tank (float type)", f"مرسل كمية الوقود، الخزان {where_ar} (عوّامة)", "brass",
            ref="p.7-22", note="A float-type transmitter in each tank works its electric fuel quantity indicator (POH); drawn on the inboard end of the tank, representative")
        c = A.wing_chord(inboard + 0.05)
        inside = A.wing_surface_point(inboard + 0.05, sx, 0.56, False, inset=(TANK_CLEARANCE + 0.004) / c)
        outside = A.wing_surface_point(inboard + 0.05, sx, 0.56, False, inset=-0.009 / c)
        bm = new_bm()
        rod(bm, inside, outside, 0.006, segs=8)
        disc(bm, outside, outside - inside, 0.009, 0.004, segs=10)
        add(ctx, f"{grp}.fuel_tank_drain", bm, grp, f"Fuel tank sump quick-drain valve, {where_en}", f"صمام التصريف السريع لحوض خزان الوقود {where_ar}", "brass", ref="p.7-23",
            outside=True, note="Each tank sump has a drain valve for the fuel sampler cup (POH); position representative")

        # ---- two outlets per tank: pipes to the cabin wall, down a door post, under the floor to the selector valve
        for key, which, word_en, word_ar in (("fwd", "fwd", "forward", "الأمامي"), ("aft", "aft", "aft", "الخلفي")):
            lane = f"fuel_{key}"
            at_tank = lanes.wing_point(lane, sx, TANK_BL[0])
            at_wall = lanes.wing_point(lane, sx, 0.535 / IN)
            bm = new_bm()
            pipe(bm, [at_tank, at_wall], PIPE)
            union(bm, at_tank, at_wall - at_tank, PIPE)
            add(ctx, f"{grp}.fuel_line_{key}", bm, grp, f"Fuel pipe from the {word_en} outlet of the {where_en} tank, wing run",
                f"أنبوب الوقود من المخرج {word_ar} للخزان {where_ar}، مسار الجناح", "bare_alu")
            station = at_wall.y / IN + U.FS_ORIGIN
            if which == "fwd":
                # forward along the top of the wall under the front carry-through spar, down the forward door post,
                # then forward of the strut attach plates and down under the floor
                wall_top = 2.056
                # (the rearmost run in the post: the wiring and the pitot line lie ahead of it and leave the post higher up)
                corners = [at_wall, SF.side_point(station - 1.0, (wall_top - U.GROUND_Z) / IN, sx, SKIN + 0.008),
                           SF.side_point(SF.post_station("fwd", 66.0) + SF.POST_SHIFT + 0.6, (wall_top - U.GROUND_Z) / IN, sx, SKIN + 0.008)]
                corners += [SF.post_point("fwd", sx, w, shift=SF.POST_SHIFT) for w in (62.0, 52.0, 42.0, 33.0, 27.0)]
                corners += [SF.side_point(25.2, 26.0, sx, SKIN + 0.008), Vector((sx * 0.42, fs(25.0), 0.900)),
                            Vector((sx * 0.40, fs(25.0), 0.897)), Vector((sx * 0.27, fs(25.0), 0.897)), Vector((sx * 0.215, fs(25.0), lanes.PIPE_LEVEL)),
                            Vector(lanes.point(f"fuel_fwd_{S}", 25.0)), Vector(lanes.point(f"fuel_fwd_{S}", 42.6)), VALVE + Vector((sx * 0.02, -0.022, 0.0))]
            else:
                # down the rear door post ahead of the aileron cable, then under the floor ahead of the gear bulkhead
                corners = [at_wall, SF.side_point(station + 0.3, (2.045 - U.GROUND_Z) / IN, sx, SKIN + 0.008),
                           SF.side_point(SF.post_station("aft", 63.0) - 0.75, (2.006 - U.GROUND_Z) / IN, sx, SKIN + 0.008)]
                corners += [SF.post_point("aft", sx, w, shift=-0.75) for w in (58.0, 48.0, 38.0, 33.0)]      # it leaves the post above the pulleys of the aileron cable
                # under the aileron cable, which rises to the post here, and inboard of the pulley at the side of the floor
                corners += [Vector((sx * 0.46, fs(67.2), 0.940)), Vector((sx * 0.33, fs(62.0), 0.897)), Vector((sx * 0.27, fs(62.0), 0.897)),
                            Vector((sx * 0.215, fs(62.0), lanes.PIPE_LEVEL)), Vector((sx * 0.03, fs(62.0), lanes.PIPE_LEVEL)),
                            Vector((sx * 0.03, fs(45.6), lanes.PIPE_LEVEL)), VALVE + Vector((sx * 0.02, 0.022, 0.0))]
            bm = new_bm()
            pipe(bm, corners, PIPE)
            add(ctx, f"FUEL.line_tank_{key}_{S}", bm, "SYSTEMS", f"Fuel pipe from the {word_en} outlet of the {where_en} tank: down the {word_en} door post to the selector valve",
                f"أنبوب الوقود من المخرج {word_ar} للخزان {where_ar}: نزولاً في قائم الباب {word_ar} إلى صمام الاختيار", "bare_alu")

        # ---- vent line joining the two tanks: wing run from the top of the tank to the cabin roof
        at_tank = lanes.wing_point("fuel_vent", sx, TANK_BL[0])
        station = at_tank.y / IN + U.FS_ORIGIN
        roof = Vector((sx * A.WING_ROOT_X, at_tank.y, A.fus_surface_z(station, A.WING_ROOT_X, top=True) - SKIN - 0.007))
        if sx > 0:
            left_roof = roof
        else:
            right_roof = roof
        bm = new_bm()
        pipe(bm, [at_tank, roof], 0.004)
        add(ctx, f"{grp}.fuel_vent_crossover", bm, grp, f"Vent line joining the two tanks, {where_en} wing run", f"خط التهوية الرابط بين الخزانين، مسار الجناح {where_ar}",
            "bare_alu", ref="p.7-22")

    station = left_roof.y / IN + U.FS_ORIGIN
    bm = new_bm()
    pipe(bm, [left_roof, Vector((0.0, left_roof.y, A.fus_top_z(station) - SKIN - 0.007)), right_roof], 0.004, bend=0.2)
    add(ctx, "FUEL.vent_crossover", bm, "SYSTEMS", "Vent line joining the two tanks, across the cabin roof", "خط التهوية الرابط بين الخزانين، عبر سقف المقصورة", "bare_alu", ref="p.7-22",
        note="The air space of the two tanks is joined by a vent line (POH p.7-22), which is why fuel can move from one tank to the other; route representative")

    # ---- selector valve under the floor, its shaft to the handle on the floor
    bm = new_bm()
    rod(bm, VALVE - Z * 0.022, VALVE + Z * 0.022, 0.026, segs=18)
    for dx, dy in ((0.02, -0.022), (-0.02, -0.022), (0.02, 0.022), (-0.02, 0.022), (0.0, -0.03)):
        union(bm, VALVE + Vector((dx, dy * 1.25, -0.003 if dx == 0.0 else 0.0)), (0.0, -1.0 if dy < 0 else 1.0, 0.0), PIPE)
    add(ctx, "FUEL.selector_valve", bm, "SYSTEMS", "Fuel selector valve (under the floor between the front seats)", "صمام اختيار الوقود (تحت الأرضية بين المقعدين الأماميين)", "brass",
        ref="p.7-22", note="Four positions: BOTH, RIGHT, LEFT and OFF (POH). The valve body is drawn under the handle; its form is representative")
    handle = scene["FUEL.selector_handle"].matrix_world.translation
    bm = new_bm()
    rod(bm, VALVE + Z * 0.022, Vector((handle.x, handle.y, handle.z)), 0.005, segs=8)
    add(ctx, "FUEL.selector_shaft", bm, "SYSTEMS", "Fuel selector shaft (handle to valve)", "عمود صمام اختيار الوقود (من المقبض إلى الصمام)", "steel", status="estimated")

    # ---- from the valve forward under the floor and through the firewall to the strainer
    strainer = scene["FUEL.strainer"]
    low = strainer.matrix_world.translation.copy()
    bm = new_bm()
    pipe(bm, [VALVE + Vector((0.0, -0.03, -0.003)), Vector(lanes.point("fuel_feed", 42.0)), Vector(lanes.point("fuel_feed", 13.0)), Vector(lanes.point("fuel_feed_fwd", 9.5)),
              Vector(lanes.point("fuel_feed_fwd", 3.2)), Vector((low.x * 0.5, fs(-0.4), lanes.FEED_LEVEL + 0.05)), Vector((low.x, low.y + 0.01, low.z + 0.03))], PIPE)
    add(ctx, "FUEL.line_valve_to_strainer", bm, "SYSTEMS", "Fuel pipe from the selector valve to the strainer", "أنبوب الوقود من صمام الاختيار إلى المصفاة", "bare_alu")

    # ---- primer: pump behind its knob on the panel, supply from the strainer, delivery to the engine
    knob = scene["PANEL.primer"].matrix_world.translation.copy()
    pump_front = Vector((knob.x, knob.y - 0.19, knob.z))
    bm = new_bm()
    rod(bm, Vector((knob.x, knob.y - 0.05, knob.z)), pump_front, 0.011, segs=12)
    add(ctx, "FUEL.primer_pump", bm, "SYSTEMS", "Manual primer pump (behind its knob on the panel)", "مضخة التحضير اليدوية (خلف مقبضها على اللوحة)", "brass", ref="p.7-22",
        note="The manual primer draws fuel from the strainer and injects it into the cylinder intake ports (POH); form representative")
    firewall_y = fs(1.0)
    bm = new_bm()
    pipe(bm, [Vector((low.x + 0.02, low.y + 0.03, low.z + 0.08)), Vector((low.x + 0.12, firewall_y + 0.03, low.z + 0.10)), Vector((knob.x - 0.02, firewall_y + 0.06, knob.z - 0.04)),
              pump_front + Vector((-0.012, 0.03, -0.012))], 0.0024, bend=0.03)
    add(ctx, "FUEL.primer_line_supply", bm, "SYSTEMS", "Primer supply line: strainer to primer pump", "خط تغذية التحضير: من المصفاة إلى مضخة التحضير", "copper", ref="p.7-22")
    from .. import engine as E
    side_x, level = 0.43, knob.z + 0.095                    # outboard of the battery and the engine mount, under the rocker boxes
    ports = [Vector((E.HEAD_X0 + 0.067, E.cyl_center_y(n) + 0.045, E.ORIGIN.z - 0.121)) for n in (4, 2)]      # on the intake pipe, just under each head
    bm = new_bm()
    pipe(bm, [pump_front + Vector((0.012, 0.03, 0.012)), Vector((side_x + 0.01, firewall_y + 0.05, level)), Vector((side_x, firewall_y - 0.05, level)), Vector((side_x, ports[1].y, level))],
         0.0024, bend=0.03)
    for port in ports:
        pipe(bm, [Vector((side_x, port.y, level)), port], 0.0024, bend=0.02)
    add(ctx, "FUEL.primer_line_delivery", bm, "SYSTEMS", "Primer delivery lines: primer pump to the cylinder intake ports", "خطوط التحضير: من مضخة التحضير إلى فتحات سحب الأسطوانات", "copper",
        ref="p.7-22", joins="INDUCTION.intake_pipe_*",
        note="The POH says the primer injects fuel into the cylinder intake ports; which cylinders are primed and the route of the lines are representative")

    for name in ("FUEL.selector_handle", "FUEL.selector_plate", "FUEL.strainer", "FUEL.line_to_carburetor", "FUEL.vent_line", "INDUCTION.carburetor",
                 "PANEL.primer", "PANEL.FUEL_L.bezel", "PANEL.FUEL_R.bezel"):
        if name in scene:
            scene[name]["assembly"] = ASSEMBLY
