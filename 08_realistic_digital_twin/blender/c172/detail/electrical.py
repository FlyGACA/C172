"""Electrical system: power sources, contactors, bus and main wiring (POH p.7-23 to 7-28, Figure 7-7).

What the handbook says: a 28-volt direct-current system powered by an engine-driven 60-amp
alternator and a 24-volt battery on the left forward side of the firewall; power goes to the
equipment through a bus bar and circuit breakers; a split master switch controls the battery
contactor and the alternator; an alternator control unit removes the alternator field on
over-voltage; an ammeter shows the battery charge or discharge rate.

What this pack builds: the battery and starter contactors, the alternator control unit, the bus bar
behind the circuit breakers, the heavy cables between them, and the wiring out to the wing-tip
lights, the landing light and the tail lights.

What is from where:
  poh        that these members exist (the contactors and the alternator control unit are in the
             schematic, Figure 7-7)
  estimated  where each one is mounted and the route of every cable and harness.
The basic model already has the battery, the alternator, the starter, the switches, the circuit
breakers and the lights.
"""
import bpy
from mathutils import Vector

from ..units import IN, fs, wl
from .. import airframe as A
from . import lanes
from . import structure_fuselage as SF
from . import structure_tail as ST
from .structure_fuselage import SKIN
from .common import pipe, rod, bolt, part, new_bm, box, X, Y

SYS = "ELECTRICAL"
REF = "p.7-23 to 7-28 (Fig 7-7)"
ASSEMBLY = "electrical_system"
CABLE = 0.0045                    # heavy battery and starter cable as drawn
HARNESS = 0.004                   # a bundle of wires


def add(ctx, name, bm, group, en, ar, mat, status="estimated", smooth=True, **tags):
    tags.setdefault("assembly", ASSEMBLY)
    if status == "poh":
        tags.setdefault("ref", REF)
    return part(ctx, name, bm, group, SYS, en, ar, mat, status=status, smooth=smooth, **tags)


def build(ctx):
    scene = bpy.data.objects
    firewall_y = fs(1.0)
    front = firewall_y - 0.013                      # forward face of the firewall
    aft = firewall_y + 0.013

    # ---- contactors on the engine side of the firewall, the control unit on the cabin side
    battery_contactor = Vector((0.13, front - 0.03, 1.40))
    starter_contactor = Vector((-0.215, front - 0.03, 1.40))       # inboard of the engine mount tubes, below the starter
    for name, centre, en, ar in (("ELECTRICAL.battery_contactor", battery_contactor, "Battery contactor (closed by the BAT half of the master switch)",
                                  "ملامس البطارية (يغلقه نصف BAT من المفتاح الرئيسي)"),
                                 ("ELECTRICAL.starter_contactor", starter_contactor, "Starter contactor (closed by the ignition switch in START)",
                                  "ملامس بادئ الحركة (يغلقه مفتاح الإشعال في وضع START)")):
        bm = new_bm()
        rod(bm, centre - X * 0.028, centre + X * 0.028, 0.022, segs=14)
        box(bm, (0.07, 0.006, 0.06), center=centre + Y * 0.027)
        for dx in (-0.016, 0.016):
            bolt(bm, centre + Vector((dx, 0, 0.022)), Vector((0, 0, 1)), 0.006, 0.016, head=False)
        add(ctx, name, bm, "SYSTEMS", en, ar, "black_plastic", status="poh",
            note="Shown in the POH electrical schematic (Figure 7-7); where it is mounted is representative")
    acu = Vector((0.33, aft + 0.016, 1.36))
    bm = new_bm()
    box(bm, (0.09, 0.03, 0.07), center=acu)
    add(ctx, "ELECTRICAL.alternator_control_unit", bm, "SYSTEMS", "Alternator control unit (voltage regulator and over-voltage protection)",
        "وحدة التحكم بالمولّد (منظم الجهد والحماية من الجهد الزائد)", "panel_grey", status="poh", smooth=False, ref="p.7-26",
        note="Removes the alternator field on over-voltage; the red LOW VOLTAGE light then comes on (POH p.7-26). Mounting position representative")

    # ---- bus bar behind the circuit breakers
    first = scene["PANEL.breaker_0_0"].matrix_world.translation.copy()
    last = scene["PANEL.breaker_0_9"].matrix_world.translation.copy()
    bus_y = first.y - 0.035
    bus_a, bus_b = Vector((first.x + 0.012, bus_y, first.z - 0.012)), Vector((last.x - 0.012, bus_y, last.z - 0.012))
    bm = new_bm()
    box(bm, (abs(bus_a.x - bus_b.x), 0.004, 0.014), center=(bus_a + bus_b) / 2)
    add(ctx, "ELECTRICAL.bus_bar", bm, "SYSTEMS", "Primary bus bar (behind the circuit breakers)", "قضيب التوزيع الرئيسي (خلف قواطع الدائرة)", "copper", status="poh", smooth=False,
        note="Power is distributed through a bus bar and circuit breakers (POH Figure 7-7); form representative")

    # ---- heavy cables
    battery = scene["ELECTRICAL.battery"].matrix_world.translation.copy()             # low centre of the battery box
    starter = scene["ELECTRICAL.starter"].matrix_world.translation.copy()
    alternator = scene["ELECTRICAL.alternator"].matrix_world.translation.copy()
    runs = [
        ("ELECTRICAL.cable_battery_to_contactor", "Battery cable: battery to battery contactor", "كابل البطارية: من البطارية إلى ملامس البطارية", "hose_red",
         [battery + Vector((-0.06, -0.04, 0.215)), Vector((0.175, battery.y - 0.014, 1.56)), Vector((0.14, battery.y + 0.041, 1.55)), Vector((0.14, front - 0.045, 1.50)),
          battery_contactor + Vector((0.016, 0, 0.05)), battery_contactor + Vector((0.016, 0, 0.022))]),
        ("ELECTRICAL.cable_contactor_to_starter_contactor", "Cable: battery contactor to starter contactor", "كابل: من ملامس البطارية إلى ملامس بادئ الحركة", "hose_red",
         [battery_contactor + Vector((-0.016, 0, 0.022)), battery_contactor + Vector((-0.05, 0.012, 0.035)), starter_contactor + Vector((0.06, 0.012, 0.035)),
          starter_contactor + Vector((0.016, 0, 0.022))]),
        ("ELECTRICAL.cable_starter", "Starter cable: starter contactor to starter", "كابل بادئ الحركة: من الملامس إلى بادئ الحركة", "hose_red",
         [starter_contactor + Vector((-0.016, 0, 0.022)), starter_contactor + Vector((-0.016, -0.004, 0.10)), Vector((starter.x - 0.048, starter_contactor.y - 0.012, starter.z))]),
        ("ELECTRICAL.cable_bus_feed", "Bus feed cable: battery contactor through the firewall to the bus bar", "كابل تغذية القضيب: من ملامس البطارية عبر جدار الحريق إلى قضيب التوزيع", "hose_red",
         [battery_contactor + Vector((0.0, 0.0, 0.022)), Vector((0.10, front - 0.01, 1.455)), Vector((0.10, aft + 0.05, 1.455)), Vector((-0.18, fs(8.0), 1.47)), bus_a + Vector((0.01, -0.06, 0.02)),
          bus_a + Vector((0.0, -0.004, 0.0))]),
        ("ELECTRICAL.cable_alternator", "Alternator output cable: alternator to the firewall", "كابل خرج المولّد: من المولّد إلى جدار الحريق", "hose_red",
         [alternator + Vector((0.03, 0.118, -0.058)), Vector((0.26, alternator.y + 0.12, 1.39)), Vector((0.42, alternator.y + 0.20, 1.39)), Vector((0.42, battery.y - 0.10, 1.32)),
          Vector((0.40, front - 0.02, 1.32)), Vector((0.40, aft + 0.02, 1.33)), acu + Vector((0.03, 0.0, -0.035))]),
        ("ELECTRICAL.cable_alternator_to_bus", "Cable: alternator control unit to the bus bar", "كابل: من وحدة التحكم بالمولّد إلى قضيب التوزيع", "hose_red",
         [acu + Vector((-0.03, 0.015, 0.02)), Vector((0.2, fs(6.5), 1.49)), Vector((-0.2, fs(9.5), 1.49)), bus_b + Vector((0.03, -0.07, 0.03)), bus_b + Vector((0.01, -0.004, 0.0))]),
        ("ELECTRICAL.ground_strap", "Battery ground strap: battery to the airframe", "شريط تأريض البطارية: من البطارية إلى هيكل الطائرة", "hose_black",
         [battery + Vector((0.07, 0.03, 0.205)), battery + Vector((0.07, 0.08, 0.25)), Vector((battery.x + 0.07, front - 0.003, 1.62))]),
    ]
    for name, en, ar, mat, corners in runs:
        bm = new_bm()
        pipe(bm, corners, CABLE, bend=0.03)
        add(ctx, name, bm, "SYSTEMS", en, ar, mat, note="Route representative")

    # ---- wiring to the landing light in the nose cowl
    light = scene["ELECTRICAL.landing_light"].matrix_world.translation.copy()
    bm = new_bm()
    pipe(bm, [Vector((0.36, aft + 0.02, 1.27)), Vector((0.36, front - 0.03, 1.25)), Vector((0.36, light.y + 0.13, 1.25)), Vector((0.10, light.y + 0.07, light.z - 0.01)),
              Vector((0.035, light.y + 0.06, light.z))], HARNESS * 0.75, bend=0.04)
    add(ctx, "ELECTRICAL.wire_landing_light", bm, "SYSTEMS", "Landing light wiring (through the firewall, along the lower cowl)", "أسلاك ضوء الهبوط (عبر جدار الحريق، بمحاذاة الغطاء السفلي)",
        "wire_yellow", note="Route representative")

    # ---- harness to each wing: up the forward door post, out through the leading edge to the tip lights
    for sx, S in ((1, "L"), (-1, "R")):
        where_en, where_ar = ("left", "الأيسر") if sx > 0 else ("right", "الأيمن")
        root = lanes.wing_point("wiring", sx, 0.51 / IN)
        start = (bus_a if sx > 0 else bus_b) + Vector((0.0, -0.05, 0.03))
        corners = [start, Vector((sx * 0.44, fs(15.5), 1.50)), SF.side_point(17.5, 47.6, sx, SKIN + 0.012), SF.side_point(22.0, 47.3, sx, SKIN + 0.008),
                   SF.side_point(28.0, 47.3, sx, SKIN + 0.008)]
        corners += [SF.post_point("fwd", sx, w, shift=-SF.POST_SHIFT) for w in (47.3, 52.0, 58.0, 66.0)]    # the foremost run in the post
        corners += [root]
        bm = new_bm()
        pipe(bm, corners, HARNESS, bend=0.025)
        add(ctx, f"ELECTRICAL.harness_wing_{S}", bm, "SYSTEMS", f"Wiring harness to the {where_en} wing, cabin run (up the forward door post)",
            f"ضفيرة أسلاك الجناح {where_ar}، مسار المقصورة (صعوداً في قائم الباب الأمامي)", "wire_yellow", inside="fuselage", note="Route representative")
        nav = scene[f"WING_{S}.nav_light"].matrix_world.translation.copy()
        strobe = scene[f"WING_{S}.strobe"].matrix_world.translation.copy()
        tip = lanes.wing_point("wiring", sx, 209.3)             # outboard of the last rib, in the wing tip
        bm = new_bm()
        pipe(bm, [root, lanes.wing_point("wiring", sx, 100.0), tip, Vector((nav.x - sx * 0.035, nav.y, nav.z - 0.01))], HARNESS, bend=0.02)
        pipe(bm, [tip, Vector((tip.x, strobe.y - 0.02, strobe.z - 0.01)), Vector((strobe.x - sx * 0.03, strobe.y, strobe.z - 0.005))], HARNESS * 0.7, bend=0.02)
        add(ctx, f"WING_{S}.wiring_harness", bm, "WING_" + S, f"Wiring harness in the {where_en} wing: to the navigation light and the strobe",
            f"ضفيرة الأسلاك في الجناح {where_ar}: إلى ضوء الملاحة والضوء الوامض", "wire_yellow", note="Runs through the leading edge ahead of the front spar; route representative")

    # ---- harness to the tail: right door post, above the headliner, down the pillar behind the rear side window, along the tailcone, up the fin
    ceiling = lambda st: A.headliner_z(st) + 0.010
    post_top = SF.post_point("fwd", -1, 66.0, shift=-SF.POST_SHIFT)
    corners = [post_top, Vector((-0.44, post_top.y + 0.015, post_top.z + 0.004)), Vector((-0.44, fs(41.5), ceiling(41.5))), Vector((-0.44, fs(60.0), ceiling(60.0))),
               Vector((-0.44, fs(71.3), ceiling(71.3))), Vector((-0.44, fs(86.0), ceiling(86.0))), SF.side_point(93.0, 63.5, -1, SKIN + 0.008), SF.side_point(95.6, 60.3, -1, SKIN + 0.008),
               SF.side_point(98.4, 56.2, -1, SKIN + 0.012), SF.side_point(102.9, 50.0, -1, SKIN + 0.024), SF.side_point(106.0, 46.3, -1, SKIN + 0.024)]
    corners += [SF.section_point(st, 3.1416 - 0.14, SKIN + 0.04) for st in (120.0, 150.0, 180.0, 205.0)]        # inside the ring frames
    fin_foot = Vector((0.0, fs(212.5), A.fus_top_z(212.5) - SKIN - 0.01))
    corners += [fin_foot]
    bm = new_bm()
    pipe(bm, corners, HARNESS, bend=0.03)
    add(ctx, "ELECTRICAL.harness_tail", bm, "SYSTEMS", "Wiring harness to the tail lights (above the headliner and along the tailcone)",
        "ضفيرة أسلاك أضواء الذيل (فوق بطانة السقف وبمحاذاة مخروط الذيل)", "wire_yellow", inside="fuselage", note="Route representative")
    beacon = scene["ELECTRICAL.beacon"].matrix_world.translation.copy()
    spar = A.FIN_SPAR
    bm = new_bm()
    pipe(bm, [fin_foot] + [Vector((0.0, fs(ST.fin_wire_station(water)), wl(water))) for water in (spar[0][1] + 3.0, spar[1][1] + 0.8)] + [Vector((0.0, beacon.y, beacon.z - 0.006))],
         HARNESS * 0.75, bend=0.03)
    part(ctx, "EMPENNAGE.wiring_fin", bm, "EMPENNAGE", SYS, "Wiring in the fin: to the flashing beacon and the tail navigation light", "الأسلاك في المثبت الرأسي: إلى المنارة الوامضة وضوء الملاحة الخلفي",
         "wire_yellow", status="estimated", smooth=True, assembly=ASSEMBLY, note="Runs up the fin behind its leading-edge former, through an opening in each rib; route representative")

    scene["ELECTRICAL.wire_landing_light"]["joins"] = "POWERPLANT.landing_light_recess,ELECTRICAL.landing_light*"
    for name in ("ELECTRICAL.battery", "ELECTRICAL.alternator", "ELECTRICAL.alternator_belt", "ELECTRICAL.starter", "PANEL.master_bat", "PANEL.master_alt", "PANEL.AMMETER.bezel",
                 "PANEL.low_volt"):
        if name in scene:
            scene[name]["assembly"] = ASSEMBLY
