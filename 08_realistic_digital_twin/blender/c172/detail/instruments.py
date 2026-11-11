"""Inside the instruments: what is behind the dial of the six flight instruments and the tachometer,
and what joins the engine instruments to the engine.

What is from where:
  poh        what works each instrument: pitot and static pressure (p.7-31), suction from the
             engine-driven vacuum pump for the attitude and directional indicators (p.7-32); a direct
             pressure oil line to the oil pressure gage, an electrical-resistance sensor for the oil
             temperature gage and an engine-driven mechanical tachometer (p.7-17)
  estimated  everything inside the cases. It shows how an instrument of each kind works (capsule,
             aneroid, calibrated leak, gyro and gimbals, magnet and drag cup): the principle, drawn
             to fit the case, not the make installed in the aircraft.
Each instrument is an assembly (@airspeed_indicator, @altimeter, ...). Its case is a separate part,
so a figure can leave it out or draw it as a phantom round the mechanism.
"""
import math

import bpy
from mathutils import Vector

from ..units import fs
from ..shapes import revolve
from . import geom2d
from .engine_detail import gear_outline, helix
from .common import Plane, sheet, wall, pipe, disc, rod, bar, tube, part, new_bm, box, X, Y, Z

SYS = "INSTRUMENTS"
PANEL_THICKNESS = 0.012
DIAL_DEPTH = 0.0085               # the dials lie this far behind the face of the panel (cockpit.DIAL_DEPTH)
CASE_DEPTH = 0.10
FITTING = 0.006                   # how far a port stands out of the back of a case
FRONT = 0.016                     # the front of a case is square for this depth (mounting screws in its corners, a knob in one), the rest round
# Where each line joins its instrument, as (to the aircraft's left, up) of the instrument's axis.
# The air-pressure pack (pneumatic.py) ends its lines at these points.
PORTS = {
    "ASI": {"pitot": (0.012, 0.0), "static": (-0.012, 0.0)},
    "ALT": {"static": (0.0, 0.0)},
    "VSI": {"static": (0.0, 0.012)},
    "AI": {"air": (0.022, 0.0), "suction": (-0.020, 0.0)},
    "DG": {"air": (0.022, 0.0), "suction": (-0.020, 0.0)},
}
NOTE = "Shows how an instrument of this kind works; drawn to explain the principle, not the make installed in the aircraft"


class Instrument:
    """One panel instrument: a frame behind its dial and a way to add its parts."""

    def __init__(self, ctx, scene, key, assembly):
        self.ctx, self.key, self.assembly = ctx, key, assembly
        bezel = scene[f"PANEL.{key}.bezel"]
        deps = bpy.context.evaluated_depsgraph_get()
        corners = [bezel.matrix_world @ Vector(corner) for corner in bezel.evaluated_get(deps).bound_box]
        self.radius = 0.5 * (max(c.x for c in corners) - min(c.x for c in corners)) - 0.0045
        centre = bezel.matrix_world.translation
        self.origin = Vector((centre.x, centre.y - PANEL_THICKNESS, centre.z))        # on the back of the panel, on the instrument's axis
        for ob in scene:
            if ob.name.startswith(f"PANEL.{key}."):
                existing = [name for name in str(ob.get("assembly", "")).split(",") if name]
                ob["assembly"] = ",".join(existing + [assembly])

    def at(self, depth, a=0.0, b=0.0):
        """Point `depth` behind the panel, a to the aircraft's left of the axis and b above it."""
        return self.origin + Vector((a, -depth, b))

    def add(self, name, bm, en, ar, mat, smooth=True, **tags):
        tags.setdefault("note", NOTE)
        tags.setdefault("assembly", self.assembly)
        return part(self.ctx, f"PANEL.{self.key}.{name}", bm, "PANEL", SYS, en, ar, mat, status="estimated", smooth=smooth, internal=True, **tags)

    def case(self, en, ar, depth=CASE_DEPTH):
        """The case: a square front against the back of the panel, then a round barrel closed at the back."""
        bm = new_bm()
        r, wall_t = self.radius, 0.0012
        half = r + 0.0045
        plane = Plane(self.origin, X, Z)                      # its normal points forward, into the case
        square = geom2d.rounded_rectangle(0.0, 0.0, 2 * half, 2 * half, 0.007, 3)
        wall(bm, plane, square, wall_t, 0.0, FRONT)
        sheet(bm, plane, square, wall_t, [geom2d.circle(0.0, 0.0, r - wall_t, 28)], offset=FRONT - wall_t)
        revolve(bm, [(r - wall_t, -FRONT), (r, -FRONT), (r, -depth), (0.0, -depth), (0.0, -depth + wall_t), (r - wall_t, -depth + wall_t), (r - wall_t, -FRONT)],
                axis="Y", origin=self.origin, segs=28, cap_start=False, cap_end=False)
        return self.add("case", bm, en, ar, "black_plastic", smooth=False, assembly=self.assembly + ",instrument_cases")

    def knob(self, bm, a, b, pinion_depth=0.009, ring_depth=None):
        """A setting knob in a corner of the square front: knob, shaft through the panel, pinion, and (ring_depth) the ring gear it turns."""
        front = self.at(-PANEL_THICKNESS - 0.005, a, b)                 # the knob stands on the rim of its instrument
        rod(bm, front, front + Y * 0.012, 0.006, segs=12)
        rod(bm, front, self.at(pinion_depth + 0.003, a, b), 0.0012, segs=6)
        pinion = 0.0045
        sheet(bm, Plane(self.at(pinion_depth, a, b), X, Z), gear_outline(pinion, 9, 0.0008), 0.002, offset=-0.001)
        if ring_depth is not None:
            radius = math.hypot(a, b) - pinion
            sheet(bm, Plane(self.at(ring_depth), X, Z), gear_outline(radius, 64, 0.0008), 0.0015, [geom2d.circle(0.0, 0.0, radius - 0.0045, 40)], offset=-0.00075)

    def port(self, name):
        a, b = PORTS[self.key][name]
        return self.at(CASE_DEPTH + FITTING, a, b)

    def stub(self, bm, name, radius=0.003):
        """The short tube of a port, through the back of the case."""
        a, b = PORTS[self.key][name]
        rod(bm, self.at(CASE_DEPTH - 0.003, a, b), self.port(name), radius, segs=8)

    def pointer_shaft(self, en, ar, pinion_depth=0.022, length=0.03):
        """The shaft that carries the pointer, with a pinion and a hairspring."""
        bm = new_bm()
        rod(bm, self.at(-(PANEL_THICKNESS - DIAL_DEPTH)), self.at(length), 0.0012, segs=6)       # up to the dial, which lies in its recess in the panel
        plane = Plane(self.at(pinion_depth), X, Z)
        sheet(bm, plane, gear_outline(0.004, 10, 0.0008), 0.004, offset=-0.002)
        spiral = [self.at(pinion_depth + 0.008, 0.0015 * t * math.cos(2.4 * t), 0.0015 * t * math.sin(2.4 * t)) for t in (i * 0.12 for i in range(64))]
        tube(bm, spiral, 0.00035, segs=4, cap=True)
        return self.add("pointer_shaft", bm, en, ar, "brass")

    def linkage(self, source, en, ar, pivot=(0.0165, -0.012), depth=0.022):
        """Link from a capsule to a rocking shaft, and the sector gear on that shaft that turns the pointer's pinion.
        The sector's pivot lies one sector radius and one pinion radius from the instrument's axis, so the teeth mesh."""
        bm = new_bm()
        a, b = pivot
        sector_radius = math.hypot(a, b) - 0.004
        toward_axis = math.degrees(math.atan2(-b, -a))
        rocker = self.at(depth + 0.016, a, b)
        arm = rocker + Z * 0.009                                                           # the link pulls an arm on the shaft
        rod(bm, source, arm, 0.0009, segs=5)                                               # link
        bar(bm, rocker, arm, 0.003, 0.0012, X)
        rod(bm, rocker + X * 0.012, rocker - X * 0.012, 0.0013, segs=6)                    # rocking shaft
        bar(bm, rocker, self.at(depth, a, b), 0.004, 0.0012, X)                            # carries the sector forward to the pinion
        plane = Plane(self.at(depth, a, b), X, Z)
        teeth = [(0.0, 0.0)]
        for k in range(17):
            angle = math.radians(toward_axis - 25.6 + 3.2 * k)
            r = sector_radius + (0.0008 if k % 2 else -0.0008)
            teeth.append((r * math.cos(angle), r * math.sin(angle)))
        sheet(bm, plane, teeth, 0.0015, offset=-0.00075)
        return self.add("linkage", bm, en, ar, "brass", smooth=False)


def port(scene, key, name):
    """The end of a port on the back of an instrument: where its line is joined."""
    centre = scene[f"PANEL.{key}.bezel"].matrix_world.translation
    a, b = PORTS[key][name]
    return Vector((centre.x + a, centre.y - PANEL_THICKNESS - CASE_DEPTH - FITTING, centre.z + b))


def capsule(bm, centre, radius, thickness, ripples=3):
    """A corrugated pressure capsule: two dished, rippled discs joined at the rim, axis fore and aft."""
    front, back = [(0.0, thickness / 2)], []
    for i in range(1, ripples * 2 + 1):
        r = radius * i / (ripples * 2 + 1)
        front.append((r, thickness / 2 * (1 - 0.55 * i / (ripples * 2 + 1)) + (0.0011 if i % 2 else -0.0011)))
    front.append((radius, 0.0))
    back = [(r, -y) for r, y in reversed(front[:-1])]
    revolve(bm, front + back, axis="Y", origin=centre, segs=40)


def ring(bm, centre, axis, radius, width=0.004, thickness=0.003):
    disc(bm, centre, axis, radius, thickness, segs=28, bore=radius - width)


def build(ctx):
    scene = bpy.data.objects
    airspeed(ctx, scene)
    altimeter(ctx, scene)
    vertical_speed(ctx, scene)
    attitude(ctx, scene)
    directional(ctx, scene)
    turn_coordinator(ctx, scene)
    tachometer(ctx, scene)
    engine_gauges(ctx, scene)


def airspeed(ctx, scene):
    i = Instrument(ctx, scene, "ASI", "airspeed_indicator")
    i.case("Airspeed indicator case (sealed: static pressure fills it)", "علبة مؤشر السرعة الجوية (محكمة: يملؤها الضغط الساكن)")
    centre = i.at(0.058)
    bm = new_bm()
    capsule(bm, centre, 0.024, 0.011)
    i.add("capsule", bm, "Airspeed capsule: pitot pressure inside, static pressure round it; it swells as the speed rises",
          "كبسولة السرعة: ضغط البيتوت بداخلها والضغط الساكن حولها؛ تنتفخ كلما زادت السرعة", "brass", smooth=False)
    bm = new_bm()
    pipe(bm, [centre - Y * 0.0055, centre - Y * 0.02, i.at(CASE_DEPTH - 0.012, 0.012, 0.0), i.at(CASE_DEPTH - 0.003, 0.012, 0.0)], 0.0022, bend=0.008)
    i.stub(bm, "pitot")
    i.add("pitot_inlet", bm, "Pitot pressure inlet: from the pitot line into the capsule", "مدخل ضغط البيتوت: من خط البيتوت إلى داخل الكبسولة", "bare_alu")
    bm = new_bm()
    i.stub(bm, "static")
    i.add("static_port", bm, "Static pressure port: opens into the case", "منفذ الضغط الساكن: يفتح على داخل العلبة", "bare_alu")
    i.linkage(centre + Y * 0.0055, "Link, rocking shaft and sector gear: turn the swelling of the capsule into rotation", "وصلة ومحور متأرجح وقطاع مسنن: تحوّل انتفاخ الكبسولة إلى دوران")
    i.pointer_shaft("Pointer shaft with pinion and hairspring", "محور المؤشر مع ترس صغير ونابض شعري")


def altimeter(ctx, scene):
    i = Instrument(ctx, scene, "ALT", "altimeter")
    i.case("Altimeter case (sealed: static pressure fills it)", "علبة مقياس الارتفاع (محكمة: يملؤها الضغط الساكن)")
    bm = new_bm()
    for depth in (0.050, 0.062, 0.074):
        capsule(bm, i.at(depth), 0.022, 0.009, ripples=3)
    rod(bm, i.at(0.079), i.at(0.088), 0.0025, segs=8)
    bar(bm, i.at(0.088, -0.03, 0.022), i.at(0.088, 0.03, -0.022), 0.008, 0.002, Y)        # the stack stands on a bridge across the case, clear of the port
    i.add("aneroid_capsules", bm, "Aneroid capsules: sealed wafers that expand as the static pressure falls with height",
          "الكبسولات اللاهوائية: أقراص محكمة تتمدد كلما انخفض الضغط الساكن مع الارتفاع", "brass", smooth=False)
    bm = new_bm()
    i.stub(bm, "static")
    i.add("static_port", bm, "Static pressure port: opens into the case", "منفذ الضغط الساكن: يفتح على داخل العلبة", "bare_alu")
    i.linkage(i.at(0.0455), "Link, rocking shaft and sector gear: turn the expansion of the capsules into rotation", "وصلة ومحور متأرجح وقطاع مسنن: تحوّل تمدد الكبسولات إلى دوران")
    bm = new_bm()
    for depth, radius, teeth, a, b in ((0.010, 0.011, 22, 0.0, 0.0), (0.010, 0.0045, 9, 0.0155, 0.0), (0.016, 0.009, 18, 0.0155, 0.0), (0.016, 0.004, 8, 0.0025, 0.0)):
        sheet(bm, Plane(i.at(depth, a, b), X, Z), gear_outline(radius, teeth, 0.0008), 0.0015, [geom2d.circle(0, 0, 0.0012, 8)], offset=-0.00075)
    rod(bm, i.at(0.006, 0.0155, 0.0), i.at(0.02, 0.0155, 0.0), 0.0009, segs=5)
    i.add("gear_train", bm, "Gear train to the three pointers (hundreds, thousands, ten thousands of feet)", "سلسلة التروس إلى المؤشرات الثلاثة (مئات وآلاف وعشرات آلاف الأقدام)", "brass", smooth=False)
    bm = new_bm()
    i.knob(bm, 0.03, -0.03, ring_depth=0.009)
    i.add("baro_adjust", bm, "Barometric setting knob, its pinion and ring gear: turn the mechanism and the pressure scale together, to set the pressure from which height is counted",
          "مقبض ضبط الضغط الجوي وترسه والترس الحلقي: تدير الآلية وتدريج الضغط معًا لتحديد الضغط الذي يُحسب الارتفاع منه", "black_plastic", smooth=False)
    i.pointer_shaft("Pointer shafts with pinion and hairspring", "محاور المؤشرات مع ترس صغير ونابض شعري")


def vertical_speed(ctx, scene):
    i = Instrument(ctx, scene, "VSI", "vertical_speed_indicator")
    i.case("Rate-of-climb indicator case (static pressure reaches it only through the calibrated leak)", "علبة مؤشر معدل الصعود (يصلها الضغط الساكن عبر التسريب المعايَر فقط)")
    centre = i.at(0.056)
    bm = new_bm()
    capsule(bm, centre, 0.023, 0.010)
    i.add("capsule", bm, "Rate-of-climb capsule: joined straight to the static line, so it follows the static pressure at once",
          "كبسولة معدل الصعود: موصولة مباشرة بخط الضغط الساكن فتتبع الضغط الساكن فورًا", "brass", smooth=False)
    tee = i.at(CASE_DEPTH - 0.014, 0.0, 0.012)
    bm = new_bm()
    pipe(bm, [centre - Y * 0.005, centre - Y * 0.018, tee, i.at(CASE_DEPTH - 0.003, 0.0, 0.012)], 0.0022, bend=0.008)
    i.stub(bm, "static")
    i.add("static_inlet", bm, "Static pressure inlet: to the capsule", "مدخل الضغط الساكن: إلى الكبسولة", "bare_alu")
    bm = new_bm()
    tube(bm, [tee] + helix(tee + Vector((0.008, 0.0, 0.004)), tee + Vector((0.008, 0.016, 0.004)), 0.004, 4, 10) + [tee + Vector((0.016, 0.02, 0.0))], 0.0009, segs=5, cap=True)
    i.add("calibrated_leak", bm, "Calibrated leak: lets the pressure in the case follow the static pressure only slowly; the difference across the capsule is the rate of climb or descent",
          "التسريب المعايَر: يجعل ضغط العلبة يتبع الضغط الساكن ببطء؛ وفرق الضغط على الكبسولة هو معدل الصعود أو الهبوط", "copper")
    i.linkage(centre + Y * 0.005, "Link, rocking shaft and sector gear", "وصلة ومحور متأرجح وقطاع مسنن")
    i.pointer_shaft("Pointer shaft with pinion and hairspring", "محور المؤشر مع ترس صغير ونابض شعري")


def rotor(bm, centre, axis, radius=0.019, width=0.014):
    """A gyro rotor: a heavy wheel with buckets cut in its rim for the air jet."""
    axis = Vector(axis).normalized()
    helper = Z if abs(axis.z) < 0.9 else X
    a = axis.cross(helper).normalized(); b = axis.cross(a).normalized()
    plane = Plane(centre, a, b)
    sheet(bm, plane, gear_outline(radius, 24, 0.0012), width, [geom2d.circle(0, 0, 0.002, 8)], offset=-width / 2)
    rod(bm, Vector(centre) - axis * (width / 2 + 0.004), Vector(centre) + axis * (width / 2 + 0.004), 0.002, segs=6)


def attitude(ctx, scene):
    i = Instrument(ctx, scene, "AI", "attitude_indicator")
    i.case("Attitude indicator case (the vacuum pump draws air through it)", "علبة مؤشر الوضع (تسحب مضخة التفريغ الهواء عبرها)")
    centre = i.at(0.056)
    note = "Driven by the suction of the engine-driven vacuum pump (POH p.7-32). " + NOTE
    bm = new_bm()
    rotor(bm, centre, Z)
    i.add("gyro_rotor", bm, "Attitude gyro rotor: spun by the air drawn through the case; its axis stays upright while the aircraft pitches and rolls round it",
          "دوّار جيروسكوب الوضع: يديره الهواء المسحوب عبر العلبة؛ يبقى محوره رأسيًا والطائرة تميل وتنحدر من حوله", "brass", smooth=False, note=note)
    bm = new_bm()
    ring(bm, centre, Y, 0.0245)
    rod(bm, centre + Z * 0.0245, centre + Z * 0.019, 0.0018, segs=6); rod(bm, centre - Z * 0.0245, centre - Z * 0.019, 0.0018, segs=6)
    rod(bm, centre + X * 0.0245, centre + X * 0.029, 0.0018, segs=6); rod(bm, centre - X * 0.0245, centre - X * 0.029, 0.0018, segs=6)
    i.add("inner_gimbal", bm, "Inner gimbal (carries the rotor): pivots about the lateral axis, so the rotor is free in pitch", "الحلقة الداخلية (تحمل الدوّار): تدور حول المحور العرضي فيتحرر الدوّار في الانحدار", "bare_alu", note=note)
    bm = new_bm()
    ring(bm, centre, Z, 0.031)
    rod(bm, centre + Y * 0.031, centre + Y * 0.04, 0.0018, segs=6); rod(bm, centre - Y * 0.031, centre - Y * 0.04, 0.0018, segs=6)
    i.add("outer_gimbal", bm, "Outer gimbal: pivots about the fore-and-aft axis, so the rotor is free in roll", "الحلقة الخارجية: تدور حول المحور الطولي فيتحرر الدوّار في الميلان", "bare_alu", note=note)
    bm = new_bm()
    bar(bm, centre + X * 0.027, i.at(0.004, 0.027, 0.0), 0.003, 0.001, X)
    bar(bm, i.at(0.004, 0.027, 0.0), i.at(0.004, -0.027, 0.0), 0.003, 0.001, Y)
    i.add("horizon_arm", bm, "Horizon bar and its arm: joined to the inner gimbal, so the bar stays level with the real horizon", "قضيب الأفق وذراعه: متصل بالحلقة الداخلية فيبقى القضيب بمحاذاة الأفق الحقيقي", "paint_white", smooth=False, note=note)
    bm = new_bm()
    pipe(bm, [i.port("air"), i.at(CASE_DEPTH - 0.02, 0.022, 0.0), centre + Vector((0.024, -0.012, 0.0))], 0.003, bend=0.008)
    i.add("air_nozzle", bm, "Air inlet and nozzle: directs the incoming filtered air onto the buckets of the rotor", "مدخل الهواء وفوهته: توجّه الهواء المرشّح الداخل على تجاويف الدوّار", "bare_alu", note=note)
    bm = new_bm()
    i.stub(bm, "suction", 0.004)
    i.add("suction_port", bm, "Suction port: the vacuum pump draws the air out of the case here", "منفذ التفريغ: تسحب مضخة التفريغ الهواء من العلبة من هنا", "bare_alu", note=note)


def directional(ctx, scene):
    i = Instrument(ctx, scene, "DG", "directional_gyro")
    i.case("Directional indicator case (the vacuum pump draws air through it)", "علبة المؤشر الاتجاهي (تسحب مضخة التفريغ الهواء عبرها)")
    centre = i.at(0.058)
    note = "Driven by the suction of the engine-driven vacuum pump (POH p.7-32). " + NOTE
    bm = new_bm()
    rotor(bm, centre, X)
    i.add("gyro_rotor", bm, "Directional gyro rotor: its axis lies level and keeps pointing the same way while the aircraft turns round it",
          "دوّار الجيروسكوب الاتجاهي: محوره أفقي ويبقى مشيرًا إلى الاتجاه نفسه والطائرة تدور من حوله", "brass", smooth=False, note=note)
    bm = new_bm()
    ring(bm, centre, Y, 0.0245)
    rod(bm, centre + X * 0.0245, centre + X * 0.019, 0.0018, segs=6); rod(bm, centre - X * 0.0245, centre - X * 0.019, 0.0018, segs=6)
    rod(bm, centre + Z * 0.0245, centre + Z * 0.029, 0.0018, segs=6); rod(bm, centre - Z * 0.0245, centre - Z * 0.029, 0.0018, segs=6)
    i.add("inner_gimbal", bm, "Inner gimbal (carries the rotor)", "الحلقة الداخلية (تحمل الدوّار)", "bare_alu", note=note)
    bm = new_bm()
    ring(bm, centre, X, 0.031)
    rod(bm, centre + Z * 0.031, centre + Z * 0.039, 0.0018, segs=6); rod(bm, centre - Z * 0.031, centre - Z * 0.039, 0.0018, segs=6)
    i.add("outer_gimbal", bm, "Outer gimbal: turns about the upright axis; the heading card is geared to it", "الحلقة الخارجية: تدور حول المحور الرأسي؛ وقرص الاتجاه معشّق بها", "bare_alu", note=note)
    # The card faces the pilot and turns about the fore-and-aft axis; the gimbal turns about the upright
    # one. A gear on the top of the gimbal turns a pinion and its shaft, and a second pinion turns the card.
    bm = new_bm()
    shaft_z = 0.0305
    sheet(bm, Plane(centre + Z * 0.0345, X, Y), gear_outline(0.0155, 26, 0.0008), 0.002, [geom2d.circle(0, 0, 0.002, 8)], offset=-0.001)       # on the gimbal's top pivot
    sheet(bm, Plane(i.at(0.0405, 0.0, shaft_z), X, Z), gear_outline(0.0038, 8, 0.0007), 0.004, offset=-0.002)                                   # pinion under its edge
    rod(bm, i.at(0.044, 0.0, shaft_z), i.at(0.004, 0.0, shaft_z), 0.0011, segs=6)                                                               # shaft, forward to the card
    sheet(bm, Plane(i.at(0.008, 0.0, shaft_z), X, Z), gear_outline(0.006, 12, 0.0007), 0.003, offset=-0.0015)                                   # pinion on the card gear
    sheet(bm, Plane(i.at(0.008), X, Z), gear_outline(0.0238, 44, 0.0007), 0.002, [geom2d.circle(0, 0, 0.003, 10)], offset=-0.001)               # the card's gear
    rod(bm, i.at(0.010), i.at(-0.002), 0.003, segs=8)
    i.add("card_gears", bm, "Gears from the outer gimbal to the heading card: the gimbal keeps its direction, so the card turns as the aircraft turns",
          "التروس من الحلقة الخارجية إلى قرص الاتجاه: تحافظ الحلقة على اتجاهها فيدور القرص مع دوران الطائرة", "brass", smooth=False, note=note)
    bm = new_bm()
    pipe(bm, [i.port("air"), i.at(CASE_DEPTH - 0.02, 0.022, 0.0), centre + Vector((0.006, -0.012, 0.024))], 0.003, bend=0.008)
    i.add("air_nozzle", bm, "Air inlet and nozzle: directs the incoming filtered air onto the buckets of the rotor", "مدخل الهواء وفوهته: توجّه الهواء المرشّح الداخل على تجاويف الدوّار", "bare_alu", note=note)
    bm = new_bm()
    i.stub(bm, "suction", 0.004)
    i.add("suction_port", bm, "Suction port: the vacuum pump draws the air out of the case here", "منفذ التفريغ: تسحب مضخة التفريغ الهواء من العلبة من هنا", "bare_alu", note=note)
    bm = new_bm()
    i.knob(bm, -0.03, -0.03, pinion_depth=0.0125, ring_depth=0.0125)
    i.add("setting_knob", bm, "Setting knob, its pinion and the ring gear on the card: pushed in, the knob holds the gimbals and turns the card, to set it to the magnetic compass",
          "مقبض الضبط وترسه والترس الحلقي على القرص: عند دفعه يمسك الحلقات ويدير القرص لضبطه على البوصلة المغناطيسية", "black_plastic", smooth=False, note=note)


def turn_coordinator(ctx, scene):
    i = Instrument(ctx, scene, "TC", "turn_coordinator")
    i.case("Turn coordinator case", "علبة منسق الانعطاف")
    centre = i.at(0.056)
    tilt = Vector((0.0, math.cos(math.radians(30)), math.sin(math.radians(30))))            # the gimbal axis: fore and aft, raised 30 degrees at the front
    bm = new_bm()
    rotor(bm, centre, X)
    i.add("gyro_rotor", bm, "Turn coordinator rotor (electric): spins about the lateral axis", "دوّار منسق الانعطاف (كهربائي): يدور حول المحور العرضي", "brass", smooth=False,
          note="The turn coordinator's gyro is electric, so it still works if the vacuum system fails. " + NOTE)
    bm = new_bm()
    ring(bm, centre, tilt.cross(X).normalized(), 0.026)
    rod(bm, centre + tilt * 0.026, centre + tilt * 0.04, 0.0018, segs=6); rod(bm, centre - tilt * 0.026, centre - tilt * 0.04, 0.0018, segs=6)
    rod(bm, centre + X * 0.026, centre + X * 0.02, 0.0018, segs=6); rod(bm, centre - X * 0.026, centre - X * 0.02, 0.0018, segs=6)
    i.add("gimbal", bm, "Gimbal: its axis is tilted 30 degrees, so the gyro answers to roll as well as to yaw", "حلقة الجيروسكوب: محورها مائل 30 درجة فيستجيب الجيروسكوب للميلان كما يستجيب للانعراج", "bare_alu")
    bm = new_bm()
    anchor = i.at(0.056, 0.03, 0.022)
    tube(bm, helix(centre + X * 0.027 + Z * 0.004, anchor, 0.0022, 6, 10), 0.0005, segs=4, cap=True)
    i.add("centring_spring", bm, "Centring spring: the further the gimbal is tilted, the faster the turn", "نابض التوسيط: كلما زاد ميل الحلقة كان الانعطاف أسرع", "steel")
    bm = new_bm()
    rod(bm, i.at(0.056, -0.032, -0.006), i.at(0.056, -0.032, 0.016), 0.004, segs=10)
    rod(bm, i.at(0.056, -0.032, -0.012), centre - X * 0.027, 0.0009, segs=5)
    i.add("damper", bm, "Damper (dashpot): steadies the gimbal", "مخمّد: يهدّئ حركة الحلقة", "bare_alu")


def tachometer(ctx, scene):
    i = Instrument(ctx, scene, "TACH", "tachometer")
    i.case("Tachometer case", "علبة عدّاد الدورات")
    bm = new_bm()
    box(bm, (0.018, 0.012, 0.008), center=i.at(0.05))
    rod(bm, i.at(0.056), i.at(CASE_DEPTH + 0.004), 0.003, segs=8)
    i.add("magnet", bm, "Rotating magnet: turned by the drive cable at a speed proportional to engine speed", "المغناطيس الدوّار: يديره كابل التدوير بسرعة تتناسب مع سرعة المحرك", "steel", smooth=False)
    bm = new_bm()
    revolve(bm, [(0.0, 0.0), (0.014, 0.0), (0.014, -0.014), (0.0128, -0.014), (0.0128, -0.0012), (0.0, -0.0012)], axis="Y", origin=i.at(0.036), segs=20)
    i.add("drag_cup", bm, "Drag cup: the turning magnet drags it round against a hairspring; how far it turns is the engine speed", "كأس السحب: يسحبه المغناطيس الدوّار ضد نابض شعري؛ ومقدار دورانه هو سرعة المحرك", "bare_alu")
    i.pointer_shaft("Pointer shaft with hairspring", "محور المؤشر مع النابض الشعري", pinion_depth=0.02, length=0.036)
    back = i.at(CASE_DEPTH + 0.004)
    firewall = fs(1.0)
    bm = new_bm()
    pipe(bm, [back, back - Y * 0.05, Vector((back.x + 0.02, firewall + 0.10, back.z - 0.01)), Vector((-0.12, firewall - 0.06, 1.63)), Vector((-0.06, fs(-7.0) + 0.047, 1.62))], 0.004, bend=0.06)
    part(ctx, "PANEL.TACH.drive_cable", bm, "PANEL", SYS, "Tachometer drive cable: a flexible shaft turned by the engine", "كابل تدوير عدّاد الدورات: عمود مرن يديره المحرك", "hose_black",
         status="poh", ref="p.7-17", smooth=True, assembly="tachometer", joins="ENGINE.accessory_housing", note="The tachometer is engine-driven and mechanical (POH p.7-17); the route of its drive cable is representative")


def engine_gauges(ctx, scene):
    def back(key, depth=0.045):
        p = scene[f"PANEL.{key}.bezel"].matrix_world.translation
        return Vector((p.x, p.y - depth, p.z))

    firewall = fs(1.0)
    gauge = back("OIL_P")
    bm = new_bm()
    pipe(bm, [Vector((-0.10, fs(-7.0) + 0.045, 1.70)), Vector((-0.10, firewall - 0.07, 1.70)), Vector((-0.10, firewall + 0.045, 1.70)), Vector((gauge.x - 0.028, firewall + 0.06, 1.70)),
              Vector((gauge.x - 0.028, gauge.y - 0.10, gauge.z + 0.03)), gauge - Y * 0.03, gauge], 0.0024, bend=0.03)
    # from the back of the accessory housing, between the two sides of the engine mount; inside the cabin it crosses along the firewall and comes aft beside the radio stack
    part(ctx, "OIL.pressure_gauge_line", bm, "ENGINE", "OIL", "Oil pressure gage line: oil at engine pressure, direct from the engine to the gage", "خط مقياس ضغط الزيت: زيت بضغط المحرك مباشرة من المحرك إلى المقياس",
         "copper", status="poh", ref="p.7-17", smooth=True, assembly="oil_system", joins="ENGINE.accessory_housing", note="A direct pressure oil line from the engine works the oil pressure gage (POH p.7-17); route representative")
    sensor = Vector((0.07, fs(-7.0) + 0.047, 1.57))
    gauge = back("OIL_T")
    bm = new_bm()
    rod(bm, sensor - Y * 0.018, sensor + Y * 0.012, 0.005, segs=8)
    pipe(bm, [sensor + Y * 0.012, Vector((0.06, firewall - 0.04, 1.58)), Vector((0.06, firewall + 0.07, 1.66)), Vector((0.44, firewall + 0.07, 1.66)),
              Vector((0.44, gauge.y - 0.10, gauge.z + 0.02)), gauge - Y * 0.03, gauge], 0.0016, bend=0.04)      # along the firewall to the left wall, then aft to the gage at the edge of the panel
    part(ctx, "OIL.temperature_sensor", bm, "ENGINE", "OIL", "Oil temperature sensor (electrical resistance) and its wire to the gage", "حسّاس حرارة الزيت (مقاومة كهربائية) وسلكه إلى المقياس",
         "wire_yellow", status="poh", ref="p.7-17", smooth=True, assembly="oil_system", joins="ENGINE.accessory_housing", note="An electrical-resistance sensor works the oil temperature gage (POH p.7-17); position and route representative")
