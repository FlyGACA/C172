"""Inside the engine: valve train, timing gears, piston pins and rings, the oil system, the inside of
the carburetor, and the engine control cables.

The basic model already has the crankshaft, camshaft, pistons, connecting rods, valves, cylinders,
accessories and the carburetor as a body. This pack adds what joins them and what is inside.

What is from where:
  poh        the oil system as the handbook describes it (p.7-18): suction strainer screen, engine-
             driven pump, bypass valve, flexible hose to the cooler on the lower right side of the
             firewall and back, pressure relief valve, breather; the carburetor as it describes it
             (p.7-19): up-draft, float type, fixed jet, accelerator pump, idle cut-off and manual
             mixture; carburetor heat from the muffler shroud
  type_data  what a four-cylinder, horizontally opposed, push-rod engine has: a camshaft at half
             crank speed, a tappet, push rod and rocker arm for each valve, valve springs, piston
             pins and rings
  estimated  every form, size and position. This is how the kind of engine works, drawn to fit the
             basic model; it is not Lycoming engineering data.
"""
import math

import bpy
from mathutils import Vector

from ..units import fs
from .. import engine as E
from . import geom2d
from .common import Plane, sheet, pipe, union, disc, rod, bar, tube, hex_prism, dome, part, new_bm, box, X, Y, Z

REF_OIL = "p.7-18"
REF_CARB = "p.7-19"
NOTE_TYPE = "Every engine of this kind has this part; its form and size here are representative, not Lycoming data"


def add(ctx, name, bm, system, en, ar, mat, status="type_data", smooth=True, group="ENGINE", **tags):
    tags.setdefault("assembly", "engine_internals")
    if status == "type_data":
        tags.setdefault("note", NOTE_TYPE)
        tags.setdefault("ref", "engine type: POH p.1-3, 7-16")
    return part(ctx, name, bm, group, system, en, ar, mat, status=status, smooth=smooth, **tags)


def gear_outline(radius, teeth, depth=0.0022):
    points = []
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        step = 2 * math.pi / teeth
        for da, r in ((-0.30, radius - depth), (-0.12, radius + depth), (0.12, radius + depth), (0.30, radius - depth)):
            points.append((r * math.cos(a + da * step), r * math.sin(a + da * step)))
    return points


def helix(start, end, radius, turns, steps=12):
    """Points of a coil spring from start to end."""
    start, end = Vector(start), Vector(end)
    axis = (end - start).normalized()
    helper = Z if abs(axis.z) < 0.9 else X
    a = axis.cross(helper).normalized(); b = axis.cross(a).normalized()
    count = int(turns * steps)
    return [start + (end - start) * (i / count) + (a * math.cos(2 * math.pi * i / steps) + b * math.sin(2 * math.pi * i / steps)) * radius for i in range(count + 1)]


def build(ctx):
    scene = bpy.data.objects
    zc = E.ORIGIN.z
    cam_z = zc + E.CAM_Z
    for c in (1, 2, 3, 4):
        build_cylinder(ctx, scene, c, zc, cam_z)
    build_gears(ctx, scene, zc, cam_z)
    build_oil(ctx, scene, zc)
    build_carburetor(ctx, scene, zc)
    build_controls(ctx, scene, zc)
    if getattr(ctx, "detail_level", 1) >= 2:
        build_engine_fasteners(ctx, zc)
    for name in ("ENGINE.crankshaft", "ENGINE.camshaft") + tuple(f"ENGINE.{kind}_{c}" for c in (1, 2, 3, 4) for kind in ("piston", "rod", "valve_intake", "valve_exhaust")):
        if name in scene:
            scene[name]["assembly"] = "engine_internals"


def build_cylinder(ctx, scene, c, zc, cam_z):
    side = E.CYL[c][0]
    yc = E.cyl_center_y(c)
    rocker_x = side * (E.HEAD_X1 + 0.014)
    pivot_z = zc + 0.5 * E.PUSHROD_Z[1]                    # the rocker shaft, half way between the push rod and the valve
    for kind, dy, word_en, word_ar in (("intake", E.VALVE_DY, "intake", "السحب"), ("exhaust", -E.VALVE_DY, "exhaust", "العادم")):
        y = yc + dy
        bm = new_bm()
        rod(bm, (side * 0.028, y, cam_z), (side * 0.072, y, cam_z), 0.0105, segs=12)
        add(ctx, f"ENGINE.tappet_{kind}_{c}", bm, "ENGINE", f"Tappet (cam follower) of the {word_en} valve, cylinder {c}", f"تابع الكامة لصمام {word_ar}، الأسطوانة {c}", "steel",
            cyl=c, internal=True)
        bm = new_bm()
        rod(bm, (side * 0.072, y, zc + E.pushrod_z(0.072)), (rocker_x, y, zc + E.pushrod_z(rocker_x)), 0.004, segs=8)
        add(ctx, f"ENGINE.pushrod_{kind}_{c}", bm, "ENGINE", f"Push rod of the {word_en} valve, cylinder {c} (inside its shroud tube)", f"قضيب الدفع لصمام {word_ar}، الأسطوانة {c} (داخل أنبوبه)",
            "bare_alu", cyl=c, internal=True)
        bm = new_bm()
        bar(bm, (rocker_x, y, zc + E.pushrod_z(rocker_x) + 0.007), (rocker_x, y, zc - 0.007), 0.012, 0.014, X)
        disc(bm, (rocker_x, y, pivot_z), Y, 0.011, 0.016, segs=12, bore=0.0055)
        add(ctx, f"ENGINE.rocker_arm_{kind}_{c}", bm, "ENGINE", f"Rocker arm of the {word_en} valve, cylinder {c}: the push rod lifts one end, the other presses the valve open",
            f"الذراع المتأرجح لصمام {word_ar}، الأسطوانة {c}: يرفع قضيب الدفع أحد طرفيه فيضغط الآخر على الصمام ليفتحه", "steel", smooth=False, cyl=c, internal=True)
        seat = Vector((side * (E.HEAD_X0 + 0.062), y, zc))
        tip = Vector((side * (E.HEAD_X0 + 0.01 + E.VALVE_STEM - 0.012), y, zc))
        bm = new_bm()
        tube(bm, helix(seat, tip, 0.0125, 5), 0.0018, segs=5, cap=True)
        disc(bm, tip + X * (side * 0.002), X, 0.015, 0.003, segs=14, bore=0.0042)
        add(ctx, f"ENGINE.valve_spring_{kind}_{c}", bm, "ENGINE", f"Valve spring and retainer of the {word_en} valve, cylinder {c} (closes the valve)",
            f"نابض صمام {word_ar} وحلقة تثبيته، الأسطوانة {c} (يغلق الصمام)", "steel", cyl=c, internal=True)
    bm = new_bm()
    rod(bm, (rocker_x, yc - 0.055, pivot_z), (rocker_x, yc + 0.055, pivot_z), 0.0055, segs=8)
    add(ctx, f"ENGINE.rocker_shaft_{c}", bm, "ENGINE", f"Rocker shaft, cylinder {c} (the two rocker arms pivot on it)", f"محور الأذرع المتأرجحة، الأسطوانة {c}", "steel", cyl=c, internal=True)

    piston = scene[f"ENGINE.piston_{c}"]
    px = E.piston_x(c)
    bm = new_bm()
    rod(bm, (px, yc - 0.05, zc), (px, yc + 0.05, zc), 0.011, segs=12)
    add(ctx, f"ENGINE.piston_pin_{c}", bm, "ENGINE", f"Piston pin (wrist pin), cylinder {c}: joins the piston to the connecting rod", f"مسمار المكبس، الأسطوانة {c}: يربط المكبس بذراع التوصيل",
        "steel", cyl=c, internal=True, parent=piston)
    bm = new_bm()
    for g in (-0.012, 0.0, 0.012):
        disc(bm, (px + g, yc, zc), X, 0.0664, 0.0028, segs=28, bore=0.0592)
    add(ctx, f"ENGINE.piston_rings_{c}", bm, "ENGINE", f"Piston rings, cylinder {c} (compression rings and an oil control ring)", f"حلقات المكبس، الأسطوانة {c} (حلقات انضغاط وحلقة ضبط الزيت)",
        "steel", cyl=c, internal=True, parent=piston)


def build_gears(ctx, scene, zc, cam_z):
    y = fs(-8.6)
    crank_r = E.CAM_Z / 3                                  # the cam gear has twice the teeth: the camshaft turns at half crank speed
    cam_r = 2 * crank_r
    for name, centre_z, radius, teeth, parent, en, ar in (
            ("ENGINE.crank_gear", zc, crank_r, 16, "ENGINE.crankshaft", "Crankshaft gear (drives the camshaft gear)", "ترس عمود المرفق (يدير ترس عمود الكامات)"),
            ("ENGINE.cam_gear", cam_z, cam_r, 32, "ENGINE.camshaft", "Camshaft gear (twice the teeth: the camshaft turns at half crankshaft speed)",
             "ترس عمود الكامات (ضعف عدد الأسنان: يدور عمود الكامات بنصف سرعة عمود المرفق)")):
        bm = new_bm()
        plane = Plane((0.0, y, centre_z), X, Z)
        sheet(bm, plane, gear_outline(radius, teeth), 0.012, [geom2d.circle(0.0, 0.0, 0.011, 12)], offset=-0.006)
        rod(bm, (0.0, y - 0.004, centre_z), (0.0, fs(-9.0) - 0.002, centre_z), 0.0115, segs=12)        # hub on the shaft end
        add(ctx, name, bm, "ENGINE", en, ar, "steel", smooth=False, internal=True, parent=scene[parent])


def build_oil(ctx, scene, zc):
    def oil(name, bm, en, ar, mat, status="poh", **tags):
        tags.setdefault("assembly", "oil_system")
        if status == "poh":
            tags.setdefault("ref", REF_OIL)
        tags.setdefault("note", "Named in the POH description of the oil system (p.7-18); position and form representative")
        return part(ctx, name, bm, "ENGINE", "OIL", en, ar, mat, status=status, smooth=True, **tags)

    pump = Vector((0.03, fs(-7.2), zc - 0.12))
    bm = new_bm()
    box(bm, (0.075, 0.006, 0.05), center=pump + Y * 0.012)
    for dx, direction in ((-0.0155, 1), (0.0155, -1)):
        plane = Plane(pump + X * dx, X, Z)
        sheet(bm, plane, gear_outline(0.0145, 8, 0.003), 0.016, [geom2d.circle(0.0, 0.0, 0.004, 8)], offset=-0.008)
    rod(bm, pump + X * -0.0155 - Y * 0.03, pump + X * -0.0155 + Y * 0.012, 0.004, segs=8)
    oil("OIL.pump", bm, "Oil pump (engine driven: two meshing gears)", "مضخة الزيت (يديرها المحرك: ترسان متعشقان)", "steel", internal=True)
    screen = Vector((0.06, fs(-13.0), zc - 0.235))
    bm = new_bm()
    rod(bm, screen - Y * 0.03, screen + Y * 0.03, 0.019, segs=14)
    pipe(bm, [screen + Y * 0.03, Vector((0.055, fs(-9.6), zc - 0.19)), pump + Vector((0.0155, -0.02, -0.02))], 0.007, bend=0.03)
    oil("OIL.suction_screen", bm, "Oil suction strainer screen and pick-up pipe (in the sump)", "مصفاة سحب الزيت وأنبوب السحب (في حوض الزيت)", "bare_alu", internal=True)
    bypass = Vector((-0.158, fs(-6.8), zc - 0.03))
    bm = new_bm()
    rod(bm, bypass + X * 0.012, bypass - X * 0.02, 0.014, segs=12)
    hex_prism(bm, bypass - X * 0.02, -X, 0.024, 0.008)
    oil("OIL.bypass_valve", bm, "Oil cooler bypass valve: cold oil goes straight to the filter, hot oil through the cooler",
        "صمام تجاوز مبرّد الزيت: الزيت البارد يذهب مباشرة إلى الفلتر والساخن يمر عبر المبرّد", "brass")
    relief = Vector((-E.CASE_HALF_W, 0.5 * (E.cyl_center_y(1) + E.cyl_center_y(3)), zc + 0.02))       # on the side of the crankcase, between two cylinders
    bm = new_bm()
    rod(bm, relief + X * 0.01, relief - X * 0.022, 0.011, segs=12)
    hex_prism(bm, relief - X * 0.022, -X, 0.02, 0.008)
    oil("OIL.pressure_relief_valve", bm, "Oil pressure relief valve: returns excess oil to the sump to hold the pressure", "صمام تنفيس ضغط الزيت: يعيد الزيت الزائد إلى الحوض ليضبط الضغط", "brass")
    cooler = Vector(E.OIL_COOLER)
    for key, dx, dz, en, ar in (("to_cooler", -0.03, 0.0, "Oil hose from the accessory housing to the oil cooler", "خرطوم الزيت من علبة الملحقات إلى المبرّد"),
                               ("from_cooler", 0.03, -0.04, "Oil hose from the oil cooler back to the accessory housing", "خرطوم الزيت العائد من المبرّد إلى علبة الملحقات")):
        start = bypass + Vector((-0.02, 0.0 + dx * 0.4, dz))
        end = cooler + Vector((dx, 0.0, 0.065))
        bm = new_bm()
        pipe(bm, [start, start + Vector((-0.06, 0.03, -0.05)), Vector((end.x - 0.02, end.y - 0.02, end.z + 0.16)), end + Z * 0.03, end], 0.008, bend=0.04)
        union(bm, end, -Z, 0.008)
        oil(f"OIL.hose_{key}", bm, en, ar, "hose_black")
    bm = new_bm()
    # past the right side of the magneto, over the accessory housing, then down between the magneto and the firewall
    pipe(bm, [Vector((-0.045, fs(-10.0), zc + 0.11)), Vector((-0.085, fs(-9.6), zc + 0.176)), Vector((-0.085, fs(-2.9), zc + 0.176)), Vector((-0.035, fs(-1.15), zc + 0.085)),
              Vector((-0.035, fs(-1.15), 1.10))], 0.007, bend=0.03)
    oil("OIL.breather_line", bm, "Crankcase breather line (vents overboard under the cowling)", "خط تنفيس علبة المرفق (ينفّس إلى الخارج تحت غطاء المحرك)", "hose_black", status="estimated",
        joins="ENGINE.crankcase_*",
        note="The POH mentions the breather (p.7-18: fill to five quarts to minimise loss of oil through the breather); its route is representative")
    for name in ("OIL.sump", "OIL.oil_filter", "OIL.oil_cooler", "OIL.dipstick_filler"):
        if name in scene:
            scene[name]["assembly"] = "oil_system"


def build_carburetor(ctx, scene, zc):
    body = scene["INDUCTION.carburetor"]
    top = body.matrix_world.translation.copy()             # centre of the top face of the carburetor body
    low = top.z - 0.11
    barrel = Vector((0.0, top.y + 0.014, 0.0))

    def carb(name, bm, en, ar, mat, **tags):
        tags.setdefault("assembly", "carburetor")
        tags.setdefault("note", "The POH describes an up-draft, float-type, fixed-jet carburetor with an accelerator pump, an idle cut-off and a manual mixture control (p.7-19); "
                                "what is drawn inside the body shows how such a carburetor works and is representative")
        return part(ctx, name, bm, "ENGINE", "INDUCTION", en, ar, mat, status="poh", ref=REF_CARB, smooth=True, internal=True, **tags)

    from ..shapes import revolve
    bm = new_bm()
    throat = 0.034                                         # height of the throat above the bottom of the body
    profile = [(0.022, 0.004), (0.0125, throat), (0.019, 0.064), (0.021, 0.064), (0.0145, throat), (0.024, 0.004), (0.022, 0.004)]
    revolve(bm, profile, axis="Z", origin=(barrel.x, barrel.y, low), segs=24, cap_start=False, cap_end=False)
    carb("INDUCTION.carburetor_venturi", bm, "Carburetor venturi: the air speeds up in the throat, its pressure falls and draws fuel from the nozzle",
         "حلق المكربن (الفنتوري): تتسارع الهواء في الحلق فينخفض ضغطه ويسحب الوقود من الفوهة", "bare_alu")
    bm = new_bm()
    centre = Vector((barrel.x, barrel.y, low + 0.084))
    disc(bm, centre, (0.0, 0.5, 0.87), 0.0195, 0.0016, segs=24)
    rod(bm, centre - X * 0.058, centre + X * 0.066, 0.003, segs=8)
    bar(bm, centre + X * 0.064, centre + X * 0.064 + Vector((0, 0.004, -0.024)), 0.01, 0.003, X)      # the arm hangs down: its cable passes under the sump
    carb("INDUCTION.throttle_valve", bm, "Throttle valve (butterfly) with its shaft and arm: above the venturi in an up-draft carburetor",
         "صمام الخانق (الفراشة) مع محوره وذراعه: فوق الحلق في المكربن ذي السحب الصاعد", "brass")
    bm = new_bm()
    nozzle = Vector((barrel.x, barrel.y, low + throat + 0.004))
    pipe(bm, [Vector((0.0, top.y - 0.03, low + 0.014)), Vector((0.0, top.y - 0.006, low + 0.014)), Vector((0.0, nozzle.y - 0.002, low + 0.022)), nozzle], 0.0022, bend=0.006)
    carb("INDUCTION.main_nozzle", bm, "Main discharge nozzle and fixed jet: fuel from the float bowl enters the air stream in the throat",
         "الفوهة الرئيسية والنافورة الثابتة: يدخل الوقود من حجرة العوامة إلى تيار الهواء في الحلق", "brass")
    bm = new_bm()
    bowl = Vector((0.0, top.y - 0.036, low + 0.05))
    rod(bm, bowl - X * 0.022, bowl + X * 0.022, 0.014, segs=12)
    bar(bm, bowl + Vector((0, 0.0, 0.014)), bowl + Vector((0.0, -0.016, 0.03)), 0.006, 0.0015, X)
    rod(bm, bowl + Vector((0.0, -0.016, 0.03)), bowl + Vector((0.0, -0.016, 0.042)), 0.002, segs=6)
    carb("INDUCTION.carburetor_float", bm, "Float and needle valve: keep the fuel in the bowl at a constant level", "العوامة وصمامها الإبري: يحفظان مستوى الوقود في الحجرة ثابتًا", "brass")
    bm = new_bm()
    mix = Vector((-0.03, top.y - 0.02, low + 0.022))
    rod(bm, mix, mix - X * 0.036, 0.0035, segs=8)
    bar(bm, mix - X * 0.064 + X * 0.0, mix - X * 0.064 + Vector((0, 0.004, 0.028)), 0.01, 0.003, X)
    rod(bm, mix - X * 0.036, mix - X * 0.066, 0.003, segs=8)
    carb("INDUCTION.mixture_valve", bm, "Mixture control valve and arm: meters the fuel to the nozzle; fully lean is idle cut-off",
         "صمام ضبط الخليط وذراعه: يقنّن الوقود إلى الفوهة؛ الإفقار الكامل يقطع الوقود", "brass")
    bm = new_bm()
    pump = Vector((0.03, top.y - 0.03, low + 0.03))
    rod(bm, pump, pump + Z * 0.04, 0.006, segs=10)
    rod(bm, pump + Z * 0.04, pump + Z * 0.062, 0.002, segs=6)
    carb("INDUCTION.accelerator_pump", bm, "Accelerator pump: adds fuel when the throttle is opened quickly", "مضخة التعجيل: تضيف وقودًا عند فتح الخانق بسرعة", "brass")

    # carburetor heat: a valve in the airbox takes heated air from the muffler shroud instead of filtered air
    airbox = scene["INDUCTION.airbox"].matrix_world.translation.copy()
    muffler = scene["ENGINE.muffler"].matrix_world.translation.copy()
    flap = Vector((0.0, airbox.y + 0.045, airbox.z - 0.035))
    bm = new_bm()
    box(bm, (0.15, 0.002, 0.05), center=flap)
    rod(bm, flap - X * 0.105 + Z * 0.025, flap + X * 0.112 + Z * 0.025, 0.003, segs=8)
    bar(bm, flap + X * 0.11 + Z * 0.025, flap + X * 0.11 + Vector((0, 0.004, 0.055)), 0.01, 0.003, X)
    part(ctx, "INDUCTION.carb_heat_valve", bm, "ENGINE", "INDUCTION", "Carburetor heat valve in the airbox, with its shaft and arm", "صمام تسخين المكربن في صندوق الهواء مع محوره وذراعه", "bare_alu",
         status="poh", ref=REF_CARB, smooth=False, internal=True, assembly="carburetor",
         note="Pulling the carburetor heat knob turns this valve: the engine then draws heated air from the muffler shroud instead of filtered air (POH p.7-19); form representative")
    bm = new_bm()
    pipe(bm, [muffler + Vector((0.07, -0.06, -0.06)), muffler + Vector((0.07, -0.093, -0.046)), Vector((0.06, airbox.y + 0.073, airbox.z - 0.051)), Vector((0.06, airbox.y + 0.058, airbox.z - 0.041))],
         0.016, bend=0.03)
    part(ctx, "INDUCTION.carb_heat_hose", bm, "ENGINE", "INDUCTION", "Carburetor heat hose: heated air from the muffler shroud to the airbox", "خرطوم تسخين المكربن: هواء ساخن من غلاف كاتم الصوت إلى صندوق الهواء",
         "hose_black", status="poh", ref=REF_CARB, smooth=True, assembly="carburetor", joins="ENGINE.muffler*", note="Route representative")
    for name in ("INDUCTION.carburetor", "INDUCTION.airbox", "INDUCTION.air_filter", "INDUCTION.filter_duct", "PANEL.carb_heat", "PANEL.throttle", "PANEL.mixture"):
        if name in scene:                                  # the carburetor is part of the fuel system as well
            scene[name]["assembly"] = ",".join([a for a in str(scene[name].get("assembly", "")).split(",") if a] + ["carburetor"])


def build_controls(ctx, scene, zc):
    """Push-pull cables from the knobs on the panel, through the firewall, to the arms on the carburetor and the airbox."""
    body = scene["INDUCTION.carburetor"].matrix_world.translation.copy()
    low = body.z - 0.11
    airbox = scene["INDUCTION.airbox"].matrix_world.translation.copy()
    firewall = fs(1.0)
    ends = {
        "throttle": Vector((0.064, body.y + 0.018, low + 0.060)),
        "mixture": Vector((-0.094, body.y - 0.016, low + 0.05)),
        "carb_heat": Vector((0.11, airbox.y + 0.049, airbox.z + 0.045)),
    }
    runs = (("throttle", "PANEL.throttle", "ENGINE.throttle_cable", "Throttle cable: knob to the throttle arm on the carburetor", "كابل الخانق: من المقبض إلى ذراع الخانق على المكربن",
             [(0.02, firewall + 0.09, 0.0), (0.05, firewall - 0.16, -0.065)], "INDUCTION.throttle_valve"),
            ("mixture", "PANEL.mixture", "ENGINE.mixture_cable", "Mixture cable: knob to the mixture arm on the carburetor", "كابل الخليط: من المقبض إلى ذراع الخليط على المكربن",
             [(-0.09, firewall + 0.09, -0.01), (-0.10, firewall - 0.16, -0.045)], "INDUCTION.mixture_valve"),
            ("carb_heat", "PANEL.carb_heat", "INDUCTION.carb_heat_cable", "Carburetor heat cable: knob to the valve in the airbox", "كابل تسخين المكربن: من المقبض إلى الصمام في صندوق الهواء",
             [(0.115, firewall + 0.09, -0.03), (0.135, firewall - 0.2, -0.085)], "INDUCTION.carb_heat_valve"))
    for key, knob_name, name, en, ar, via, joined in runs:
        knob = scene[knob_name].matrix_world.translation.copy()
        corners = [Vector((knob.x, knob.y - 0.05, knob.z))] + [Vector((x, y, knob.z + dz)) for x, y, dz in via] + [ends[key] + Vector((0.0, 0.07, 0.0)), ends[key]]
        bm = new_bm()
        pipe(bm, corners, 0.0032, bend=0.06)
        part(ctx, name, bm, "ENGINE", "ENGINE" if name.startswith("ENGINE") else "INDUCTION", en, ar, "hose_black", status="estimated", smooth=True, assembly="engine_controls", joins=joined,
             note="The throttle, mixture and carburetor heat controls are push-pull knobs on the panel (POH p.7-16, engine controls); the cables behind them are representative")


def build_engine_fasteners(ctx, zc):
    """Level 2: the nuts that hold each cylinder to the crankcase and the screws of each rocker cover."""
    for c in (1, 2, 3, 4):
        side = E.CYL[c][0]
        yc = E.cyl_center_y(c)
        bm = new_bm()
        for k in range(8):
            a = 2 * math.pi * (k + 0.5) / 8
            hex_prism(bm, Vector((side * (E.CASE_HALF_W + 0.02), yc + 0.086 * math.cos(a), zc + 0.086 * math.sin(a))), X * side, 0.014, 0.008)
        part(ctx, f"ENGINE.cylinder_base_nuts_{c}", bm, "ENGINE", "FASTENERS", f"Cylinder base nuts, cylinder {c} (hold the cylinder to the crankcase)", f"صواميل قاعدة الأسطوانة {c} (تثبّت الأسطوانة على علبة المرفق)",
             "steel", detail=2, status="estimated", smooth=False, count=8, assembly="fasteners", note="Eight nuts are representative")
        bm = new_bm()
        x = side * (E.HEAD_X1 + 0.04)
        low, high = zc + E.ROCKER_BOX_Z[0], zc + E.ROCKER_BOX_Z[1]
        for y, z in ((yc - 0.066, low + 0.014), (yc + 0.066, low + 0.014), (yc - 0.066, high - 0.014), (yc + 0.066, high - 0.014), (yc - 0.066, 0.5 * (low + high)), (yc + 0.066, 0.5 * (low + high))):
            dome(bm, Vector((x, y, z)), X * side, 0.0045, 0.002, sides=8, rings=1)
        part(ctx, f"ENGINE.rocker_cover_screws_{c}", bm, "ENGINE", "FASTENERS", f"Rocker cover screws, cylinder {c}", f"براغي غطاء الأذرع المتأرجحة، الأسطوانة {c}", "steel", detail=2,
             status="estimated", smooth=False, count=6, assembly="fasteners", note="Six screws are representative")
