"""Air-pressure systems: pitot-static, vacuum, and the pneumatic stall warning
(POH p.7-31 to 7-34, Figure 7-9).

What the handbook says, and this pack builds:
  pitot-static   ram air from the pitot tube under the left wing goes to the airspeed indicator;
                 static pressure from the port on the lower left side of the forward fuselage goes
                 to the airspeed indicator, the rate-of-climb indicator and the altimeter; a static
                 pressure alternate source valve may be installed next to the throttle
  vacuum         an engine-driven pump draws air through the attitude and directional indicators;
                 a relief valve and the system air filter are on the aft side of the firewall below
                 the panel; a suction gage shows the suction; the pump discharges overboard
  stall warning  an inlet in the leading edge of the left wing is joined by tubing to an
                 air-operated horn near the upper left corner of the windshield

What is from where:
  poh        the members above and what joins what
  estimated  the route of every line and the form of the valve, the filter and the horn.
The basic model already has the pitot tube, the static port, the vacuum pump and the stall warning inlet.
"""
import bpy
from mathutils import Vector

from ..units import IN, fs
from . import lanes
from . import instruments as I
from . import structure_fuselage as SF
from .structure_fuselage import SKIN
from .common import pipe, union, disc, rod, part, new_bm, Y

LINE = 0.003                      # 1/4 in instrument line as drawn
APPROACH = 0.03                   # a line runs this far straight into an instrument port
HOSE = 0.008                      # vacuum hose


def build(ctx):
    scene = bpy.data.objects

    def port(instrument, name):
        """Where a line joins an instrument: the end of the port on the back of its case (instruments.py)."""
        return I.port(scene, instrument, name)

    build_pitot_static(ctx, scene, port)
    build_vacuum(ctx, scene, port)
    build_stall_warning(ctx, scene)


def join(bm, corners, radius, bend):
    """A line that ends at an instrument port: it arrives along the port's axis and carries the union nut."""
    end = corners[-1]
    pipe(bm, corners[:-1] + [end - Y * APPROACH, end], radius, bend=bend)
    union(bm, end, Y, radius)


def build_pitot_static(ctx, scene, port):
    def add(name, bm, group, en, ar, mat="bare_alu", status="poh", **tags):
        tags.setdefault("assembly", "pitot_static")
        tags.setdefault("ref", "p.7-31")
        return part(ctx, name, bm, group, "PITOT_STATIC", en, ar, mat, status=status, smooth=True, **tags)

    # ---- pitot line: from the pitot tube inboard through the leading edge, down the left forward door post, to the airspeed indicator
    tube = scene["PITOT_STATIC.pitot_tube"].matrix_world.translation.copy()
    station = tube.x / IN
    in_wing = lanes.wing_point("pitot", 1, station)
    at_wall = lanes.wing_point("pitot", 1, 0.52 / IN)
    bm = new_bm()
    pipe(bm, [tube + Vector((0, 0.004, 0.009)), in_wing, at_wall], LINE, bend=0.02)
    add("WING_L.pitot_line", bm, "WING_L", "Pitot pressure line, wing run: pitot tube to the wing root", "خط ضغط البيتوت، مسار الجناح: من أنبوب البيتوت إلى جذر الجناح",
        note="Plumbing connects the instruments to the sources (POH); the route through the leading edge is representative")
    # in the post it lies between the wiring (ahead of it) and the fuel pipe (behind it); it leaves the post below the wiring
    corners = [at_wall] + [SF.post_point("fwd", 1, w) for w in (66.0, 58.0, 52.0, 45.6)]
    corners += [SF.side_point(28.0, 45.0, 1, SKIN + 0.008), SF.side_point(22.0, 45.0, 1, SKIN + 0.008), SF.side_point(16.5, 45.3, 1, SKIN + 0.012)]
    asi = port("ASI", "pitot")
    corners += [Vector((asi.x + 0.02, asi.y - 0.06, asi.z - 0.04)), asi]
    bm = new_bm()
    join(bm, corners, LINE, 0.02)
    add("PITOT_STATIC.pitot_line", bm, "SYSTEMS", "Pitot pressure line, cabin run: down the door post to the airspeed indicator",
        "خط ضغط البيتوت، مسار المقصورة: نزولاً في قائم الباب إلى مؤشر السرعة الجوية", inside="fuselage",
        note="The pitot-static system supplies ram air pressure to the airspeed indicator (POH); route representative")

    # ---- static lines: port, tee behind the panel, three instruments
    static_port = scene["PITOT_STATIC.static_port"].matrix_world.translation.copy()
    # behind the cases the static lines run across in one layer, 30 mm behind the ports and level
    # with the gap between the two rows of instruments; the vacuum hoses turn 30 mm further forward
    asi_s, alt_s, vsi_s = port("ASI", "static"), port("ALT", "static"), port("VSI", "static")
    layer = asi_s.y - APPROACH
    level = 0.5 * (alt_s.z + scene["PANEL.VSI.bezel"].matrix_world.translation.z)
    tee = Vector((0.335, layer, level))
    inlet = Vector((0.43, fs(14.5), 1.52))
    bm = new_bm()
    pipe(bm, [static_port + Vector((-0.02, 0, 0)), static_port + Vector((-0.07, 0.02, 0.03)), inlet, tee], LINE, bend=0.03)
    branch = Vector((alt_s.x, layer, level))
    join(bm, [tee, Vector((asi_s.x, layer, level)), asi_s], LINE, 0.012)        # each turns up or down in the layer, then aft into its port
    join(bm, [tee, branch, alt_s], LINE, 0.012)
    join(bm, [branch, vsi_s], LINE, 0.012)
    add("PITOT_STATIC.static_line", bm, "SYSTEMS", "Static pressure lines: static port to the airspeed indicator, altimeter and rate-of-climb indicator",
        "خطوط الضغط الساكن: من المنفذ الساكن إلى مؤشر السرعة ومقياس الارتفاع ومؤشر معدل الصعود", inside="fuselage",
        note="Static pressure goes to the airspeed indicator, the rate-of-climb indicator and the altimeter (POH); route representative")
    throttle = scene["PANEL.throttle"].matrix_world.translation.copy()
    valve = throttle + Vector((0.045, -0.035, -0.045))
    bm = new_bm()
    rod(bm, valve - Y * 0.02, valve + Y * 0.02, 0.009, segs=10)
    rod(bm, valve + Y * 0.02, valve + Y * 0.06, 0.003, segs=6)
    disc(bm, valve + Y * 0.062, Y, 0.008, 0.008, segs=10)
    pipe(bm, [valve - Y * 0.02, valve + Vector((0.06, -0.07, 0.08)), Vector((0.40, layer + 0.015, 1.47)), inlet + (tee - inlet) * 0.5], LINE, bend=0.03)      # under the instruments, into the line from the port
    add("PITOT_STATIC.alternate_static_valve", bm, "SYSTEMS", "Alternate static source valve (optional equipment, next to the throttle)",
        "صمام المصدر البديل للضغط الساكن (تجهيز اختياري، بجانب الخانق)", "brass", inside="fuselage", optional=True,
        note="May be installed adjacent to the throttle; pulled ON it supplies static pressure from inside the cabin if the external port is blocked (POH p.7-31, 3-8)")
    for name in ("PITOT_STATIC.pitot_tube", "PITOT_STATIC.static_port", "PANEL.ASI.bezel", "PANEL.ALT.bezel", "PANEL.VSI.bezel"):
        if name in scene:
            scene[name]["assembly"] = "pitot_static"


def build_vacuum(ctx, scene, port):
    def add(name, bm, en, ar, mat="hose_black", status="poh", **tags):
        tags.setdefault("assembly", "vacuum_system")
        tags.setdefault("ref", "p.7-32, 7-33 (Fig 7-9)")
        return part(ctx, name, bm, "SYSTEMS", "VACUUM", en, ar, mat, status=status, smooth=True, **tags)

    pump = scene["VACUUM.engine_driven_pump"].matrix_world.translation.copy()       # on the accessory housing; it reaches aft toward the firewall
    firewall_y = fs(1.0)
    relief = Vector((0.17, firewall_y + 0.075, 1.555))
    filter_centre = Vector((0.385, firewall_y + 0.085, 1.50))
    suction = [port("AI", "suction"), port("DG", "suction")]
    air = [port("AI", "air"), port("DG", "air")]

    bm = new_bm()
    rod(bm, relief - Y * 0.028, relief + Y * 0.028, 0.02, segs=14)
    disc(bm, relief + Y * 0.036, Y, 0.027, 0.016, segs=14)
    add("VACUUM.relief_valve", bm, "Vacuum relief valve (sets the suction; on the aft side of the firewall)", "صمام تنفيس التفريغ (يضبط قيمة التفريغ؛ على الجهة الخلفية لجدار الحريق)", "cast_alu",
        note="Shown in POH Figure 7-9; position and form representative")
    bm = new_bm()
    rod(bm, filter_centre - Y * 0.04, filter_centre + Y * 0.04, 0.036, segs=18)
    add("VACUUM.air_filter", bm, "Vacuum system air filter (the gyros draw cabin air through it)", "مرشح هواء نظام التفريغ (تسحب الجيروسكوبات هواء المقصورة عبره)", "paint_white",
        note="Shown in POH Figure 7-9, on the aft side of the firewall below the instrument panel; position and form representative")

    bm = new_bm()
    pipe(bm, [pump + Vector((0.03, 0.07, 0.0)), Vector((pump.x + 0.065, firewall_y - 0.03, 1.72)), Vector((pump.x + 0.065, firewall_y + 0.03, 1.65)), relief - Y * 0.028 + Vector((0, 0, 0.012))],
         HOSE, bend=0.035)
    add("VACUUM.hose_pump_to_relief_valve", bm, "Vacuum hose: pump to relief valve (through the firewall)", "خرطوم التفريغ: من المضخة إلى صمام التنفيس (عبر جدار الحريق)")
    bm = new_bm()
    tee = Vector((suction[0].x, suction[0].y - 0.06, 0.5 * (suction[0].z + suction[1].z)))
    pipe(bm, [relief + Vector((0.022, 0.0, 0.0)), Vector((tee.x, relief.y, relief.z)), tee], HOSE, bend=0.03)
    for end in suction:
        pipe(bm, [tee, Vector((tee.x, tee.y, end.z)), end], HOSE, bend=0.02)
    add("VACUUM.hose_relief_valve_to_gyros", bm, "Vacuum hoses: relief valve to the attitude and directional indicators", "خراطيم التفريغ: من صمام التنفيس إلى مؤشر الوضع والمؤشر الاتجاهي")
    bm = new_bm()
    for end, dz in zip(air, (0.012, -0.012)):
        pipe(bm, [filter_centre + Y * 0.04 + Vector((0, 0, dz)), filter_centre + Y * 0.07 + Vector((0, 0, dz)), Vector((end.x, end.y - 0.10, end.z)), end], HOSE, bend=0.03)
    add("VACUUM.hose_filter_to_gyros", bm, "Inlet air hoses: air filter to the attitude and directional indicators", "خراطيم هواء الدخول: من المرشح إلى مؤشر الوضع والمؤشر الاتجاهي",
        "hose_blue")
    gauge = scene["PANEL.SUCTION.bezel"].matrix_world.translation + Vector((0.0, -0.045, 0.0))
    bm = new_bm()
    pipe(bm, [gauge, gauge + Vector((0.0, -0.04, 0.0)), Vector((tee.x - 0.03, tee.y - 0.01, gauge.z + 0.03)), tee + Vector((0, 0, -0.01))], LINE, bend=0.025)
    add("VACUUM.line_suction_gauge", bm, "Suction gage line", "خط مقياس التفريغ", "bare_alu", ref="p.7-34",
        note="The suction gage shows the suction available to the gyros; normal 4.5 to 5.4 in Hg (POH p.7-34)")
    bm = new_bm()
    # outboard of the oil filter and the battery contactor, inboard of the engine mount, then down the face of the firewall
    pipe(bm, [pump + Vector((0.04, 0.045, -0.005)), Vector((0.215, firewall_y - 0.054, 1.70)), Vector((0.215, firewall_y - 0.039, 1.60)), Vector((0.215, firewall_y - 0.039, 1.04))],
         HOSE, bend=0.03)
    add("VACUUM.overboard_vent", bm, "Vacuum pump discharge line (overboard vent)", "خط تصريف مضخة التفريغ (تنفيس إلى الخارج)")
    for name in ("VACUUM.engine_driven_pump", "PANEL.AI.bezel", "PANEL.DG.bezel", "PANEL.SUCTION.bezel"):
        if name in scene:
            scene[name]["assembly"] = "vacuum_system"


def build_stall_warning(ctx, scene):
    def add(name, bm, group, en, ar, mat="bare_alu", status="poh", **tags):
        tags.setdefault("assembly", "stall_warning")
        tags.setdefault("ref", "p.7-34")
        return part(ctx, name, bm, group, "STALL_WARNING", en, ar, mat, status=status, smooth=True, **tags)

    inlet = scene["AIRFRAME.stall_warning"].matrix_world.translation.copy()
    station = inlet.x / IN
    at_wall = lanes.wing_point("stall_warning", 1, 0.50 / IN)
    bm = new_bm()
    pipe(bm, [inlet + Vector((0, 0.012, -0.004))] + [lanes.wing_point("stall_warning", 1, st) for st in (station - 1.0, 34.0, 28.0, 22.5)] + [at_wall], 0.004, bend=0.02)
    add("WING_L.stall_warning_tube", bm, "WING_L", "Stall warning tube, wing run: leading-edge inlet to the wing root", "أنبوب إنذار الانهيار، مسار الجناح: من فتحة الحافة الأمامية إلى جذر الجناح",
        note="Low pressure at the inlet as the stall approaches draws air through the horn (POH p.7-34); route representative")
    horn = Vector((0.485, fs(37.1), at_wall.z - 0.05))
    bm = new_bm()
    pipe(bm, [at_wall, horn + Vector((0.004, -0.008, 0.02))], 0.004, bend=0.02)
    rod(bm, horn - Y * 0.016, horn + Y * 0.016, 0.014, segs=12)
    disc(bm, horn + Y * 0.018, Y, 0.018, 0.004, segs=12)
    add("STALL_WARNING.horn", bm, "SYSTEMS", "Stall warning horn (air operated), near the upper left corner of the windshield",
        "بوق إنذار الانهيار (يعمل بالهواء)، قرب الزاوية العلوية اليسرى للزجاج الأمامي", "black_plastic",
        note="Sounds 5 to 10 knots above the stall in all flight conditions (POH p.7-34); position and form representative")
    scene["AIRFRAME.stall_warning"]["assembly"] = "stall_warning"
