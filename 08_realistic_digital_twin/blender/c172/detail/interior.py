"""The cabin: heating, ventilating and defrosting; cabin and courtesy lights; door hinges; antennas.

What the handbook says, and this pack builds:
  cabin air   (p.7-29 to 7-31, Figure 7-8) heated air comes from a shroud round the exhaust muffler
              through a heater valve at the firewall into a cabin manifold just forward of the
              pilot's and copilot's feet, with outlet holes across it; two ducts lead from the
              manifold down each side of the cabin to an outlet at the front door post at floor
              level; a duct leads from the manifold to the windshield defroster outlet, which has
              two sliding valves; a ventilating air door on the right side of the forward fuselage
              lets outside air into the manifold; the CABIN HT knob works the heater valve and the
              CABIN AIR knob the door
  lights      (p.7-27 to 7-29) a red flood light in the forward part of the overhead console and
              the cabin dome light in its aft part; optional: a courtesy light under each wing
              just outboard of the cabin door, a map light on the left forward door post

What is from where:
  poh        the members above and what joins what
  estimated  every form, size and route; the door hinges and the two antennas, which the handbook
             does not describe, are what a 172 of this year carries, drawn representatively.
  ventilators (p.7-31) separate adjustable ventilators supply additional air, one near each upper
              corner of the windshield; each is fed through a duct from the inlet in the leading edge
              of its wing root (basic model). The duct runs in the nose of the wing above the wires and
              the pitot line and passes the root nose rib through an opening (lanes.py).
Not modelled: the two ventilators available for the rear cabin area (optional equipment).
"""
import bpy
from mathutils import Vector

from ..units import IN, fs, wl
from .. import airframe as A
from . import lanes
from . import structure_fuselage as SF
from . import structure_wing as SW
from .structure_fuselage import SKIN
from .common import pipe, disc, rod, bar, dome, part, new_bm, box, X, Y, Z

AIR = "CABIN_AIR"
REF_AIR = "p.7-29 to 7-31 (Fig 7-8)"
DUCT = 0.020                      # radius of a cabin air duct as drawn
HOSE = 0.022                      # the hose from the muffler shroud
VENT = 0.014                      # radius of a ventilator duct as drawn


def build(ctx):
    scene = bpy.data.objects
    build_cabin_air(ctx, scene)
    build_lights(ctx, scene)
    build_door_hinges(ctx)
    build_antennas(ctx)


def build_cabin_air(ctx, scene):
    def air(name, bm, en, ar, mat="panel_grey", group="SYSTEMS", status="poh", **tags):
        tags.setdefault("assembly", "cabin_air")
        tags.setdefault("ref", REF_AIR)
        return part(ctx, name, bm, group, AIR, en, ar, mat, status=status, smooth=tags.pop("smooth", True), **tags)

    firewall = fs(1.0)
    front, aft = firewall - 0.013, firewall + 0.013
    y_m, z_m = aft + 0.035, 1.17                             # the manifold: across the cabin, on the firewall, above the pedals
    left_end, right_end = 0.30, -0.37

    # ---- manifold with the front cabin air outlets
    bm = new_bm()
    box(bm, (left_end - right_end, 0.05, 0.06), center=(0.5 * (left_end + right_end), y_m, z_m))
    for k in range(8):
        x = right_end + 0.06 + k * (left_end - right_end - 0.12) / 7
        disc(bm, (x, y_m + 0.027, z_m), Y, 0.013, 0.005, segs=12, bore=0.009)
    air("CABIN_AIR.manifold", bm, "Cabin manifold with the front cabin air outlets: heated and outside air mix here, just forward of the pilot's and copilot's feet",
        "مجمّع هواء المقصورة مع فتحات الهواء الأمامية: يختلط فيه الهواء الساخن والخارجي، أمام قدمي الطيار ومساعده مباشرة", smooth=False,
        note="Outlet holes are spaced across the manifold (POH p.7-31); its form and the number of holes are representative")

    # ---- heater valve on the firewall, and the hose to it from the muffler shroud
    valve = Vector((-0.14, aft + 0.0225, 1.245))
    bm = new_bm()
    box(bm, (0.07, 0.045, 0.09), center=valve)
    rod(bm, valve + Vector((-0.035, 0.0, 0.025)), valve + Vector((-0.047, 0.0, 0.025)), 0.004, segs=8)        # the shaft of the valve plate
    bar(bm, valve + Vector((-0.045, 0.0, 0.025)), valve + Vector((-0.045, 0.012, 0.055)), 0.008, 0.003, X)    # its arm
    air("CABIN_AIR.heater_valve", bm, "Heater valve (on the firewall): lets heated air from the muffler shroud into the cabin manifold",
        "صمام التدفئة (على جدار الحريق): يُدخل الهواء الساخن من غلاف كاتم الصوت إلى مجمّع هواء المقصورة", "cast_alu", smooth=False,
        note="Worked by the CABIN HT knob: pulled out it opens the valve (POH p.7-29); form and position representative")
    muffler = scene["ENGINE.muffler"].matrix_world.translation.copy()
    bm = new_bm()
    pipe(bm, [muffler + Vector((-0.10, 0.067, 0.054)), Vector((valve.x, front - 0.10, valve.z)), Vector((valve.x, aft + 0.002, valve.z))], HOSE, bend=0.05)
    air("CABIN_AIR.heat_hose", bm, "Cabin heat hose: heated air from the shroud round the exhaust muffler to the heater valve",
        "خرطوم تدفئة المقصورة: هواء ساخن من الغلاف المحيط بكاتم الصوت إلى صمام التدفئة", "hose_black", joins="ENGINE.muffler*",
        note="Air is heated in a shroud round the exhaust muffler (POH Figure 7-8); route representative")

    # ---- windshield defroster: duct up the firewall from the manifold, outlet with two sliding valves under the glareshield
    foot = Vector((-0.30, y_m, z_m + 0.03))
    outlet = Vector((-0.20, aft + 0.105, 1.722))
    bm = new_bm()
    pipe(bm, [foot, Vector((foot.x, y_m, 1.66)), Vector((foot.x + 0.025, outlet.y - 0.012, 1.716))], 0.018, bend=0.04)
    air("CABIN_AIR.defroster_duct", bm, "Windshield defroster duct: from the cabin manifold up to the defroster outlet", "مجرى إزالة الضباب عن الزجاج الأمامي: من مجمّع المقصورة صعودًا إلى فتحة إزالة الضباب",
        "hose_black", note="A duct leads from the cabin manifold to the defroster outlet (POH p.7-31); route representative")
    bm = new_bm()
    box(bm, (0.24, 0.036, 0.012), center=outlet)
    for dx in (-0.06, 0.06):
        rod(bm, outlet + Vector((dx, 0.018, 0.0)), outlet + Vector((dx, 0.034, 0.0)), 0.004, segs=8)
        disc(bm, outlet + Vector((dx, 0.037, 0.0)), Y, 0.007, 0.006, segs=10)
    air("CABIN_AIR.defroster_outlet", bm, "Adjustable defroster outlet, with the two knobs of its sliding valves", "فتحة إزالة الضباب القابلة للضبط، مع مقبضي صماميها المنزلقين", smooth=False,
        note="Two knobs control sliding valves in the defroster outlet (POH p.7-31); the outlet is drawn under the forward edge of the glareshield")

    # ---- rear cabin air: a duct from each end of the manifold along the side of the cabin to an outlet at the front door post, at floor level
    for sx, S, end in ((1, "L", left_end), (-1, "R", right_end)):
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        inset = SKIN + 0.05
        corners = [Vector((end - sx * 0.01, y_m + 0.02, z_m)), SF.side_point(6.0, 31.3, sx, inset), SF.side_point(15.0, 31.3, sx, inset), SF.side_point(20.5, 26.5, sx, inset),
                   SF.side_point(23.4, 26.5, sx, inset)]              # the outlet: ahead of the strut attach plate at the foot of the door post
        bm = new_bm()
        pipe(bm, corners, DUCT, bend=0.05)
        disc(bm, corners[-1] + Y * 0.004, Y, DUCT + 0.006, 0.008, segs=14, bore=DUCT - 0.004)
        air(f"CABIN_AIR.rear_duct_{S}", bm, f"Rear cabin air duct, {where_en}: from the manifold along the side of the cabin to an outlet at the front door post, at floor level",
            f"مجرى هواء المقصورة الخلفية {where_ar}: من المجمّع بمحاذاة جانب المقصورة إلى فتحة عند قائم الباب الأمامي بمستوى الأرضية", "hose_black",
            note="Two ducts from the manifold supply the rear cabin, one down each side (POH p.7-31); route representative")

    # ---- ventilating air door on the right side of the forward fuselage, its duct into the manifold
    corners_out = [SF.side_point(st, w, -1, -0.0015) for st, w in ((4.0, 34.0), (8.0, 34.0), (8.0, 38.5), (4.0, 38.5))]
    corners_in = [SF.side_point(st, w, -1, 0.0025) for st, w in ((4.0, 34.0), (8.0, 34.0), (8.0, 38.5), (4.0, 38.5))]
    bm = new_bm()
    outer = [bm.verts.new(p) for p in corners_out]
    inner = [bm.verts.new(p) for p in corners_in]
    bm.faces.new(outer); bm.faces.new(list(reversed(inner)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((outer[i], inner[i], inner[j], outer[j]))
    door = SF.side_point(6.0, 36.2, -1, SKIN + 0.012)
    air("CABIN_AIR.ventilating_air_door", bm, "Ventilating air door (right side of the forward fuselage): lets outside air into the cabin manifold",
        "باب هواء التهوية (الجانب الأيمن من مقدمة جسم الطائرة): يُدخل الهواء الخارجي إلى مجمّع المقصورة", "paint_white", smooth=False,
        note="Worked by the CABIN AIR knob: pulled out it opens the door (POH p.7-29, Figure 7-8); size and position representative")
    bm = new_bm()
    pipe(bm, [door, Vector((-0.43, y_m + 0.01, 1.25)), Vector((right_end + 0.01, y_m, z_m + 0.03))], 0.024, bend=0.04)
    air("CABIN_AIR.ventilating_air_duct", bm, "Ventilating air duct: from the ventilating air door to the cabin manifold", "مجرى هواء التهوية: من باب هواء التهوية إلى مجمّع المقصورة", "hose_black",
        note="Route representative")

    # ---- push-pull cables from the two knobs
    heat = scene["PANEL.cabin_heat"].matrix_world.translation.copy()
    fresh = scene["PANEL.cabin_air"].matrix_world.translation.copy()
    arm = valve + Vector((-0.045, 0.012, 0.055))
    bm = new_bm()
    pipe(bm, [heat - Y * 0.05, Vector((-0.35, fs(13.5), heat.z - 0.012)), Vector((-0.35, fs(10.0), heat.z - 0.03)), Vector((arm.x - 0.004, arm.y + 0.06, arm.z + 0.01)), arm],
         0.003, bend=0.03)                                   # outboard of the end of the control column, then across to the valve
    air("CABIN_AIR.cabin_heat_cable", bm, "Cabin heat control cable: CABIN HT knob to the heater valve", "كابل التحكم بتدفئة المقصورة: من مقبض CABIN HT إلى صمام التدفئة", "hose_black", ref="p.7-29",
        note="Push-pull control; route representative")
    bm = new_bm()
    pipe(bm, [fresh - Y * 0.05, Vector((-0.40, fs(13.0), fresh.z - 0.01)), Vector((-0.41, fs(8.5), fresh.z - 0.01)), door + Vector((0.012, 0.03, 0.03)), door + Vector((0.004, 0.0, 0.02))],
         0.003, bend=0.03)
    air("CABIN_AIR.cabin_air_cable", bm, "Cabin air control cable: CABIN AIR knob to the ventilating air door", "كابل التحكم بهواء المقصورة: من مقبض CABIN AIR إلى باب هواء التهوية", "hose_black", ref="p.7-29",
        note="Push-pull control; route representative")

    # ---- adjustable ventilators near the upper corners of the windshield, each with its duct from the inlet in the wing root leading edge
    for sx, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        inlet = scene[f"AIRFRAME.cabin_vent_{S}"].matrix_world.translation.copy()
        lane = lanes.wing_point("vent_duct", sx, 21.0)                       # the duct runs inboard along this line, above the wires
        mouth = Vector((sx * 0.470, lane.y, lane.z - 0.008))                  # inside the cabin, at the upper corner
        bm = new_bm()
        pipe(bm, [inlet + Y * 0.018, lanes.wing_point("vent_duct", sx, 26.3), lane, mouth], VENT, bend=0.03)
        air(f"WING_{S}.ventilator_duct", bm, f"Ventilator duct, {where_en}: from the air inlet in the wing root leading edge to the ventilator",
            f"مجرى فتحة التهوية {where_ar}: من مدخل الهواء في مقدمة جذر الجناح إلى فتحة التهوية", "hose_black", group=f"WING_{S}", ref="p.7-31",
            note="Runs in the nose of the wing and through an opening in the root nose rib; route representative")
        tip = mouth + Vector((-sx * 0.036, 0.0, -0.036))
        bm = new_bm()
        rod(bm, mouth + Vector((sx * 0.006, 0.0, 0.006)), tip, VENT + 0.003, segs=16)
        disc(bm, tip, tip - mouth, VENT + 0.006, 0.006, segs=16, bore=VENT - 0.002)
        air(f"CABIN_AIR.ventilator_{S}", bm, f"Adjustable ventilator near the upper {where_en} corner of the windshield", f"فتحة تهوية قابلة للضبط قرب الزاوية العلوية {'اليسرى' if sx > 0 else 'اليمنى'} للزجاج الأمامي",
            "bare_alu", ref="p.7-31", note="Supplies additional outside air to the " + ("pilot" if sx > 0 else "copilot") + "; it is pulled out and turned to regulate and aim the air. Form representative")
    for name in ("PANEL.cabin_heat", "PANEL.cabin_air", "AIRFRAME.cabin_vent_L", "AIRFRAME.cabin_vent_R", "ENGINE.muffler_shroud"):
        if name in scene:
            scene[name]["assembly"] = "cabin_air"


def build_lights(ctx, scene):
    def light(name, bm, en, ar, mat, group="INTERIOR", ref="p.7-28", **tags):
        tags.setdefault("assembly", "lighting")
        return part(ctx, name, bm, group, "ELECTRICAL", en, ar, mat, status="poh", ref=ref, smooth=tags.pop("smooth", False), **tags)

    # ---- overhead console on the cabin ceiling between the front seats: red flood light forward, dome light aft
    station = 47.0
    top = A.headliner_z(station) - 0.001
    centre = Vector((0.0, fs(station), top - 0.014))
    bm = new_bm()
    box(bm, (0.15, 0.27, 0.028), center=centre)
    light("INTERIOR.overhead_console", bm, "Overhead console (carries the instrument flood light, the dome light and its switch)", "الكونسول العلوي (يحمل ضوء إنارة اللوحة وضوء المقصورة ومفتاحه)", "panel_grey",
          note="Named in the POH lighting description; form representative")
    bm = new_bm()
    dome(bm, centre + Vector((0.0, -0.085, -0.014)), -Z, 0.022, 0.008, sides=14, rings=2)
    light("ELECTRICAL.flood_light", bm, "Instrument panel flood light (red), in the forward part of the overhead console", "ضوء إنارة لوحة العدادات (أحمر)، في الجزء الأمامي من الكونسول العلوي", "nav_red", smooth=True,
          note="A single red flood light lights the instrument and control panels; its intensity is set with the PANEL LT rheostat (POH p.7-28)")
    bm = new_bm()
    dome(bm, centre + Vector((0.0, 0.07, -0.014)), -Z, 0.028, 0.008, sides=14, rings=2)
    box(bm, (0.012, 0.02, 0.006), center=centre + Vector((0.045, 0.07, -0.017)))
    light("ELECTRICAL.dome_light", bm, "Cabin dome light, in the aft part of the overhead console, with its switch", "ضوء المقصورة في الجزء الخلفي من الكونسول العلوي، مع مفتاحه", "nav_white", ref="p.7-29", smooth=True,
          note="Operated by a switch near the light; the same switch works the courtesy lights under the wings (POH p.7-28, 7-29)")

    # ---- courtesy light under each wing, just outboard of the cabin door (optional equipment)
    for sx, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        x = 0.74
        plane = SW.section_plane(x, sx)
        chord = A.wing_chord(x)
        base = plane.at(0.42 * chord, A.airfoil_y(A.wing_airfoil(x), 0.42, False) * chord + 0.001)
        bm = new_bm()
        dome(bm, base, -plane.v, 0.024, 0.007, sides=14, rings=2)
        light(f"WING_{S}.courtesy_light", bm, f"Courtesy light under the {where_en} wing, just outboard of the cabin door (optional equipment)",
              f"ضوء المجاملة تحت الجناح {where_ar}، خارج باب المقصورة مباشرة (تجهيز اختياري)", "nav_white", group=f"WING_{S}", smooth=True, optional=True, outside=True,
              note="Two courtesy lights, one under each wing, are operated by the dome light switch (POH p.7-28); position along the chord representative")

    # ---- map light on the left forward door post (optional equipment)
    post = SF.post_point("fwd", 1, 57.0, inset=SKIN + 0.035)
    bm = new_bm()
    box(bm, (0.018, 0.03, 0.055), center=post)
    dome(bm, post + Vector((-0.009, 0.0, 0.01)), -X, 0.009, 0.004, sides=10, rings=1)
    light("ELECTRICAL.doorpost_map_light", bm, "Map light on the left forward door post, with red and white bulbs (optional equipment)", "ضوء الخرائط على قائم الباب الأمامي الأيسر، بمصباحين أحمر وأبيض (تجهيز اختياري)",
          "black_plastic", ref="p.7-29", optional=True, note="Its switch below the light selects RED, OFF or WHITE (POH p.7-29); form representative")
    for name in ("WING_L.nav_light", "WING_R.nav_light", "WING_L.strobe", "WING_R.strobe", "ELECTRICAL.tail_nav_light", "ELECTRICAL.beacon", "ELECTRICAL.landing_light",
                 "ELECTRICAL.landing_light_lens"):
        if name in scene:
            scene[name]["assembly"] = ",".join([a for a in str(scene[name].get("assembly", "")).split(",") if a] + ["lighting"])


def build_door_hinges(ctx):
    """Two hinges on the forward edge of each cabin door, on the outside of the forward door post."""
    low, high = A.DOOR[0], A.DOOR[3]
    for sx, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        for key, water, word_en, word_ar in (("lower", 32.0, "Lower", "السفلية"), ("upper", 56.0, "Upper", "العلوية")):
            station = low[0] + (high[0] - low[0]) * (water - low[1]) / (high[1] - low[1])
            on_skin = SF.side_point(station, water, sx, 0.0)
            out = Vector((sx, 0.0, 0.0))
            bm = new_bm()
            box(bm, (0.004, 0.05, 0.04), center=on_skin + out * 0.002)                       # the two leaves, on the post and on the door
            rod(bm, on_skin + out * 0.006 - Z * 0.022, on_skin + out * 0.006 + Z * 0.022, 0.0045, segs=8)      # the knuckle and its pin
            part(ctx, f"AIRFRAME.door_hinge_{S}_{key}", bm, "AIRFRAME", "AIRFRAME", f"{word_en} hinge of the {where_en} cabin door", f"المفصلة {word_ar} لباب المقصورة {where_ar}", "bare_alu",
                 status="estimated", note="Each cabin door hangs on two hinges on its forward edge; form and height representative")


def build_antennas(ctx):
    # ---- navigation (VOR/LOC) antenna: a V of two rods on the fin
    water = 84.0
    (s0, w0), (s1, w1) = A.FIN_SPAR
    base_station = s0 + (s1 - s0) * (water - w0) / (w1 - w0) + 6.0
    bm = new_bm()
    for sx in (1, -1):
        base = Vector((sx * (A.fin_half_thickness(base_station, water) + 0.001), fs(base_station), wl(water)))
        rod(bm, base, base + Vector((sx * 0.30, 0.30, 0.0)), 0.003, segs=6)
        disc(bm, base, X, 0.012, 0.004, segs=10)
    part(ctx, "EMPENNAGE.nav_antenna", bm, "EMPENNAGE", "ELECTRICAL", "Navigation (VOR/LOC) antenna: a V of two rods on the vertical stabiliser", "هوائي الملاحة (VOR/LOC): قضيبان على شكل V على المثبت الرأسي",
         "steel", status="estimated", smooth=True, note="Not described in the POH; where a 172 of this year carries its navigation antenna, drawn representatively")
    # ---- transponder antenna: a short stub under the fuselage
    station = 58.0
    x = lanes.ALONG["coax_xpdr"][0]                             # at the end of its cable's lane under the floor
    belly = Vector((x, fs(station), A.fus_surface_z(station, abs(x))))
    bm = new_bm()
    disc(bm, belly - Z * 0.002, Z, 0.014, 0.004, segs=12)
    rod(bm, belly, belly - Z * 0.055, 0.0025, segs=6)
    dome(bm, belly - Z * 0.055, -Z, 0.005, 0.005, sides=8, rings=2)
    part(ctx, "AIRFRAME.transponder_antenna", bm, "AIRFRAME", "ELECTRICAL", "Transponder antenna: a short stub under the fuselage, left of the centreline", "هوائي المرسل المجيب: قضيب قصير تحت جسم الطائرة، يسار خط المنتصف", "steel", status="estimated", smooth=True,
         note="Not described in the POH; position representative")
