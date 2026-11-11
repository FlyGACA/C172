#!/usr/bin/env python3
"""Draw the atlas: one picture of every assembly under the skin, in the style of the book figures.

    python3 09_book_figures/atlas.py                 every picture (about a minute each)
    python3 09_book_figures/atlas.py fuel brakes     only the named ones
    python3 09_book_figures/atlas.py --list

Each picture is one call of the part tool (blender/part.py); atlas/README.md shows the pictures with
the command that made each, so that a figure of your own is a matter of changing the part ids, the
view direction and the tint. The pictures are drafts for choosing views, not finished figures: they
carry no labels.
"""
from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "atlas"
BLEND = ROOT / "08_realistic_digital_twin" / "models" / "C172N_realistic.blend"
SIZE = "1800x1125"

# name, title (en, ar), part ids, further options of `part.py render`
PICTURES = [
    ("structure_wing", "Wing structure: spars, ribs, stringers, fittings", "هيكل الجناح: العوارض والأضلاع والدعامات الطولية وتجهيزات الربط",
     ["WING_L.front_spar", "WING_L.rear_spar", "WING_L.aileron_spar", "WING_L.rib_*", "WING_L.nose_rib_*", "WING_L.stringer_*", "WING_L.spar_fitting_*", "WING_L.strut_fitting"],
     "--context --azimuth 28 --elevation 42 --tint #D4A84B --margin 0.62"),
    ("structure_fuselage", "Fuselage structure: frames, door posts, carry-through spars, floor structure, stringers",
     "هيكل جسم الطائرة: الإطارات وقوائم الأبواب والعوارض العابرة وهيكل الأرضية والدعامات الطولية",
     ["AIRFRAME.frame_*", "AIRFRAME.door_post_*", "AIRFRAME.carry_through_*", "AIRFRAME.floor_*", "AIRFRAME.keel_beam_*", "AIRFRAME.stringer_tail_*",
      "AIRFRAME.engine_mount_stringer_*", "AIRFRAME.seat_rail_*", "AIRFRAME.strut_attach_plate_*", "AIRFRAME.gear_forging_*"],
     "--context --azimuth 40 --elevation 24 --tint #D4A84B --margin 0.6"),
    ("structure_tail", "Tail structure: spars, ribs, hinges, balance weights, torque tube", "هيكل الذيل: العوارض والأضلاع والمفصلات وأثقال الموازنة وأنبوب العزم",
     ["EMPENNAGE.fin_*", "EMPENNAGE.rudder_rib_*", "EMPENNAGE.rudder_hinge_*", "EMPENNAGE.rudder_balance_weight", "EMPENNAGE.stabilizer_*", "EMPENNAGE.elevator_rib_*",
      "EMPENNAGE.elevator_spar_*", "EMPENNAGE.elevator_balance_weight_*", "EMPENNAGE.elevator_torque_tube"],
     "--context --azimuth 215 --elevation 30 --tint #D4A84B --margin 0.75"),
    ("flight_controls", "Flight controls: ailerons, elevator, rudder, trim and nose-wheel steering", "أنظمة التحكم بالطيران: الجنيحات والرافع والدفة والموازنة وتوجيه عجلة المقدمة",
     ["@aileron_control", "@elevator_control", "@rudder_control", "@elevator_trim", "@nose_steering"],
     "--context --frame aircraft --azimuth 215 --elevation 32 --grow 0.006 --tint #D9534F --margin 0.56"),
    ("controls_behind_panel", "Behind the instrument panel: control column, chains, rudder bars", "خلف لوحة العدادات: عمود القيادة والسلاسل وقضيبا الدفة",
     ["system:CONTROLS", "INTERIOR.yoke_*", "INTERIOR.pedal_*", "INTERIOR.trim_wheel"],
     "--focus CONTROLS.control_column CONTROLS.rudder_bar_fwd CONTROLS.elevator_bellcrank_fwd CONTROLS.trim_chain --azimuth 150 --elevation 28 --tint #D9A441 --margin 0.75"),
    ("controls_under_floor", "Under the cabin floor: cables and pulleys through the bulkheads and keel beams", "تحت أرضية المقصورة: الكابلات والبكرات عبر الحواجز والعوارض الطولية",
     ["system:CONTROLS", "AIRFRAME.floor_*", "AIRFRAME.keel_beam_*"],
     "--focus AIRFRAME.floor_frame_fs041 AIRFRAME.floor_bulkhead_strut AIRFRAME.floor_frame_fs017 AIRFRAME.floor_bulkhead_gear --azimuth 150 --elevation 38 --margin 0.66"),
    ("controls_tail", "At the tail: elevator bellcrank and horn, rudder horn, trim actuator", "عند الذيل: الذراع المرفقي وقرن الرافع، قرن الدفة، مشغّل الموازنة",
     ["system:CONTROLS", "EMPENNAGE.elevator_torque_tube"],
     "--context --focus CONTROLS.elevator_bellcrank_aft EMPENNAGE.trim_actuator EMPENNAGE.rudder_horn EMPENNAGE.trim_tab_horn --azimuth 215 --elevation 24 --tint #D9A441 --margin 0.85"),
    ("flap_drive", "Flap drive: motor, screw, drive pulleys, cables, push-pull rods, tracks", "تحريك القلابات: المحرك واللولب وبكرات التحريك والكابلات وقضبان الدفع والسكك",
     ["@flap_drive"], "--context --azimuth 200 --elevation 50 --grow 0.004 --tint #8E6BBF --margin 0.6"),
    ("fuel_system", "Fuel system: tanks, pipes down the door posts, selector valve, strainer, vent, primer", "نظام الوقود: الخزانان والأنابيب في قوائم الأبواب وصمام الاختيار والمصفاة والتهوية والتحضير",
     ["@fuel_system"], "--context --frame aircraft --azimuth 35 --elevation 30 --grow 0.006 --tint #3B7DD8 --margin 0.45"),
    ("air_systems", "Pitot-static, vacuum and stall warning", "أنظمة البيتوت والضغط الساكن والتفريغ وإنذار الانهيار",
     ["@pitot_static", "@vacuum_system", "@stall_warning"],
     "--context --focus PITOT_STATIC.pitot_tube VACUUM.overboard_vent PANEL.VSI.bezel STALL_WARNING.horn --azimuth 40 --elevation 26 --grow 0.004 --tint #2E9E6B --margin 0.62"),
    ("brakes", "Brakes: master cylinders on the pilot's pedals, pipes to the main wheels", "الكوابح: الأسطوانتان الرئيسيتان على دواستي الطيار والأنابيب إلى العجلتين الرئيسيتين",
     ["@brake_system"], "--context --azimuth 40 --elevation 20 --grow 0.004 --tint #E08A2E --margin 0.62"),
    ("electrical", "Electrical: battery, contactors, bus bar, heavy cables, wiring to the lights", "الكهرباء: البطارية والملامسات وقضيب التوزيع والكابلات الرئيسية وأسلاك الأضواء",
     ["@electrical_system"], "--context --frame aircraft --azimuth 35 --elevation 30 --grow 0.006 --tint #E3B020 --margin 0.5"),
    ("engine_internals", "Inside the engine: crankshaft, camshaft and timing gears, pistons, connecting rods and the valve train of the four cylinders",
     "داخل المحرك: عمود المرفق وعمود الكامات وتروس التوقيت والمكابس وأذرع التوصيل ومجموعة صمامات الأسطوانات الأربع",
     ["@engine_internals"],
     "--ghost ENGINE.crankcase_* ENGINE.cylinder_barrel_* ENGINE.cylinder_head_* ENGINE.rocker_cover_* ENGINE.pushrod_tubes_* --azimuth 245 --elevation 32 --margin 1.0"),
    ("engine_valve_train", "Valve train of cylinder 1: cam, tappets, push rods, rocker arms, valves and springs", "مجموعة صمامات الأسطوانة 1: الكامة والتوابع وقضبان الدفع والأذرع المتأرجحة والصمامات والنوابض",
     ["ENGINE.camshaft", "ENGINE.cam_gear", "ENGINE.crank_gear", "ENGINE.crankshaft", "ENGINE.tappet_*_1", "ENGINE.pushrod_*_1", "ENGINE.rocker_arm_*_1", "ENGINE.rocker_shaft_1",
      "ENGINE.valve_*_1", "ENGINE.piston_1", "ENGINE.rod_1", "ENGINE.piston_pin_1", "ENGINE.piston_rings_1"],
     "--ghost ENGINE.cylinder_head_1 ENGINE.rocker_cover_1 ENGINE.cylinder_barrel_1 ENGINE.pushrod_tubes_1 --focus ENGINE.rocker_cover_1 ENGINE.cam_gear ENGINE.piston_1 "
     "--azimuth 250 --elevation 28 --margin 0.75"),
    ("oil_system", "Oil system: sump, pump, suction screen, filter, cooler on the firewall and its hoses, valves, breather, gage line", "نظام الزيت: الحوض والمضخة ومصفاة السحب والفلتر والمبرّد على جدار الحريق وخراطيمه والصمامات والتنفيس وخط المقياس",
     ["@oil_system"], "--context --azimuth 300 --elevation 20 --grow 0.002 --tint #C9862B --margin 0.9"),
    ("carburetor", "Inside the carburetor and the airbox: venturi, throttle valve, nozzle, float, mixture valve, accelerator pump, carburetor heat valve",
     "داخل المكربن وصندوق الهواء: الحلق وصمام الخانق والفوهة والعوامة وصمام الخليط ومضخة التعجيل وصمام تسخين المكربن",
     ["@carburetor"], "--ghost INDUCTION.carburetor INDUCTION.airbox --focus INDUCTION.carburetor INDUCTION.airbox --azimuth 60 --elevation 15 --margin 1.3"),
    ("engine_controls", "Engine controls: throttle, mixture and carburetor heat cables from the panel to the carburetor and the airbox",
     "أدوات التحكم بالمحرك: كابلات الخانق والخليط وتسخين المكربن من اللوحة إلى المكربن وصندوق الهواء",
     ["@engine_controls", "@carburetor"], "--context --focus PANEL.throttle INDUCTION.carburetor --azimuth 60 --elevation 20 --grow 0.002 --tint #D9534F --margin 1.2"),
    ("cabin_air", "Cabin heating, ventilating and defrosting: muffler shroud, heat hose, heater valve, manifold, defroster, rear ducts, ventilating air door, control cables, the two ventilators with their ducts",
     "تدفئة المقصورة وتهويتها وإزالة الضباب: غلاف كاتم الصوت وخرطوم التدفئة وصمامها والمجمّع ومجرى إزالة الضباب والمجريان الخلفيان وباب هواء التهوية وكابلا التحكم وفتحتا التهوية بمجرييهما",
     ["@cabin_air"], "--context --focus CABIN_AIR.manifold CABIN_AIR.heat_hose CABIN_AIR.rear_duct_L CABIN_AIR.defroster_outlet CABIN_AIR.ventilator_L AIRFRAME.cabin_vent_R --azimuth 215 --elevation 30 --tint #E0703A --margin 1.0"),
    ("seats", "Seats: the front seats on their rails with rollers, seat lock, seat back levers and seat stops; the split-backed rear seat; belts and their anchors",
     "المقاعد: المقعدان الأماميان على سككهما مع البكرات وقفل المقعد وذراعي الظهر والمصدّات؛ المقعد الخلفي بظهرين؛ الأحزمة ومثبتاتها",
     ["@seats", "INTERIOR.shoulder_harness_*"], "--ghost INTERIOR.seat_*.cushion INTERIOR.seat_*.back* --azimuth 215 --elevation 14 --margin 1.05"),
    ("seat_lock", "Seat lock of the pilot's seat: tubular handle, pins in the rails, rollers, seat back lever, seat stops",
     "قفل مقعد الطيار: المقبض الأنبوبي والمسماران في السكّتين والبكرات وذراع الظهر ومصدّات المقعد",
     ["INTERIOR.seat_pilot.*", "AIRFRAME.seat_rail_*", "AIRFRAME.seat_stops"],
     "--ghost INTERIOR.seat_pilot.cushion INTERIOR.seat_pilot.back INTERIOR.seat_pilot.lap_belt AIRFRAME.seat_rail_3 AIRFRAME.seat_rail_4 --focus INTERIOR.seat_pilot.frame INTERIOR.seat_pilot.adjust_handle --azimuth 205 --elevation 10 --margin 1.25"),
    ("doors", "Cabin doors: hinges, outside and inside handles, latch, lock (left door), door stop; the openable window with its hinge, latch and retaining arm",
     "بابا المقصورة: المفصلات والمقبضان الخارجي والداخلي والمزلاج والقفل (الباب الأيسر) وآلية الإيقاف؛ النافذة القابلة للفتح بمفصلتها ومزلاجها وذراع تثبيتها",
     ["AIRFRAME.door_latch_L", "AIRFRAME.door_lock_L", "AIRFRAME.door_stop_L", "AIRFRAME.door_window_*_L", "AIRFRAME.door_window_L", "INTERIOR.door_inner_handle_L", "INTERIOR.armrest_L",
      "AIRFRAME.door_handle_L", "AIRFRAME.door_hinge_L_*"], "--azimuth 250 --elevation 10 --margin 1.1"),
    ("baggage", "Baggage area 1 behind the rear seat: baggage net with its eight straps and the tie-down rings",
     "منطقة الأمتعة 1 خلف المقعد الخلفي: شبكة الأمتعة بأشرطتها الثمانية وحلقات الربط",
     ["@baggage", "INTERIOR.seat_rear.*", "INTERIOR.baggage_bulkhead"], "--azimuth 150 --elevation 35 --margin 1.1"),
    ("control_lock", "Control lock: the rod through the pilot's control wheel shaft and its collar, the red flag over the ignition switch",
     "قفل التحكم: القضيب المار عبر عمود عجلة قيادة الطيار وطوقه، والعلم الأحمر فوق مفتاح الإشعال",
     ["INTERIOR.control_lock", "PANEL.control_wheel_collars", "INTERIOR.yoke_L", "INTERIOR.yoke_shaft_L", "PANEL.ignition_switch", "PANEL.lower_panel"],
     "--detail 2 --focus INTERIOR.control_lock INTERIOR.yoke_L --azimuth 150 --elevation 18 --margin 1.2"),
    ("avionics", "Avionics installation: the radio stack, the avionics bus, the antenna cables to the roof, the fin and the belly, the speaker, the microphone, the ELT",
     "تركيب الأفيونكس: مجموعة الراديو وقضيب توزيع الأفيونكس وكابلات الهوائيات إلى السقف والمثبت الرأسي وأسفل الجسم ومكبر الصوت والميكروفون وجهاز ELT",
     ["@avionics"], "--context --azimuth 215 --elevation 30 --grow 0.003 --tint #3A7BD5 --margin 0.75"),
    ("radio_stack", "Behind the radio stack: each unit in its tray, the avionics bus with a lead to each unit, the cables leaving for the antennas and the speaker",
     "خلف مجموعة الراديو: كل وحدة في حاملها وقضيب توزيع الأفيونكس بوصلة إلى كل وحدة والكابلات الخارجة إلى الهوائيات ومكبر الصوت",
     ["PANEL.radio_*", "ELECTRICAL.avionics_bus", "ELECTRICAL.wire_avionics_feed", "AVIONICS.coax_*", "ELECTRICAL.wire_speaker", "PANEL.upper_panel"],
     "--focus PANEL.radio_COMNAV1.chassis PANEL.radio_MARKER.chassis ELECTRICAL.avionics_bus --azimuth 40 --elevation 25 --size 1800x1350 --margin 1.6"),
    ("ground_equipment", "On the ground: tie-down ropes, tow bar, pitot tube cover, rudder gust lock, control lock, fuel sampler cup (detail level 2)",
     "على الأرض: حبال الربط وقضيب السحب وغطاء أنبوب البيتوت وقفل الدفة وقفل التحكم وكوب عيّنة الوقود (مستوى التفصيل 2)",
     ["@ground_equipment"], "--context --detail 2 --azimuth 35 --elevation 18 --grow 0.004 --tint #D9534F --margin 0.6"),
    ("lighting", "Lights: navigation, strobe, landing, beacon and tail lights; flood and dome lights in the overhead console; courtesy and map lights",
     "الأضواء: أضواء الملاحة والوميض والهبوط والمنارة والذيل؛ ضوءا إنارة اللوحة والمقصورة في الكونسول العلوي؛ أضواء المجاملة والخرائط",
     ["@lighting"], "--context --frame aircraft --azimuth 215 --elevation 28 --grow 0.004 --tint #E3B020 --margin 0.55"),
    ("behind_the_panel", "Behind the instrument panel: the instrument cases and the pitot, static and vacuum lines joined to them",
     "خلف لوحة العدادات: علب العدادات وخطوط البيتوت والضغط الساكن والتفريغ الموصولة بها",
     ["@instrument_cases", "@pitot_static", "@vacuum_system", "PANEL.upper_panel", "PANEL.TACH.drive_cable", "OIL.pressure_gauge_line", "OIL.temperature_sensor"],
     "--focus PANEL.ASI.case PANEL.VSI.case VACUUM.air_filter VACUUM.relief_valve --azimuth 35 --elevation 30 --size 1800x1200 --margin 1.15"),
    ("airspeed_indicator", "Inside the airspeed indicator: capsule, pitot inlet, static port, linkage, sector and pinion", "داخل مؤشر السرعة الجوية: الكبسولة ومدخل البيتوت ومنفذ الضغط الساكن والوصلة والقطاع المسنن والترس",
     ["@airspeed_indicator"], "--ghost PANEL.ASI.case --azimuth 50 --elevation 18 --margin 1.1"),
    ("altimeter", "Inside the altimeter: aneroid capsules, linkage, gear train to the three pointers, barometric setting", "داخل مقياس الارتفاع: الكبسولات اللاهوائية والوصلة وسلسلة التروس إلى المؤشرات الثلاثة وضبط الضغط الجوي",
     ["@altimeter"], "--ghost PANEL.ALT.case --azimuth 50 --elevation 18 --margin 1.1"),
    ("vertical_speed_indicator", "Inside the rate-of-climb indicator: capsule and calibrated leak", "داخل مؤشر معدل الصعود: الكبسولة والتسريب المعايَر",
     ["@vertical_speed_indicator"], "--ghost PANEL.VSI.case --azimuth 50 --elevation 18 --margin 1.1"),
    ("attitude_indicator", "Inside the attitude indicator: rotor with an upright axis, two gimbals, horizon bar, air nozzle", "داخل مؤشر الوضع: دوّار بمحور رأسي وحلقتان وقضيب الأفق وفوهة الهواء",
     ["@attitude_indicator"], "--ghost PANEL.AI.case --azimuth 50 --elevation 18 --margin 1.1"),
    ("directional_gyro", "Inside the directional indicator: rotor with a level axis, two gimbals, gears to the heading card, setting knob", "داخل المؤشر الاتجاهي: دوّار بمحور أفقي وحلقتان وتروس قرص الاتجاه ومقبض الضبط",
     ["@directional_gyro"], "--ghost PANEL.DG.case --azimuth 50 --elevation 18 --margin 1.1"),
    ("turn_coordinator", "Inside the turn coordinator: electric rotor, gimbal tilted 30 degrees, centring spring, damper", "داخل منسق الانعطاف: دوّار كهربائي وحلقة مائلة 30 درجة ونابض التوسيط والمخمّد",
     ["@turn_coordinator"], "--ghost PANEL.TC.case --azimuth 50 --elevation 18 --margin 1.1"),
    ("tachometer", "Inside the tachometer: drive cable, rotating magnet, drag cup and hairspring", "داخل عدّاد الدورات: كابل التدوير والمغناطيس الدوّار وكأس السحب والنابض الشعري",
     ["@tachometer"], "--ghost PANEL.TACH.case --focus PANEL.TACH.case PANEL.TACH.bezel --azimuth 50 --elevation 18 --margin 1.1"),
    ("rivets_wing", "Rivet rows and tank cover screws on the left wing (detail level 2)", "صفوف البرشام وبراغي غطاء الخزان على الجناح الأيسر (مستوى التفصيل 2)",
     ["WING_L.wing", "WING_L.flap", "WING_L.fuel_cap", "WING_L.rivets_*", "WING_L.fuel_tank_cover_screws"],
     "--focus WING_L.fuel_tank_cover_screws WING_L.rivets_rib_ws072_upper --azimuth 25 --elevation 48 --margin 0.5"),
    ("hardware_kit", "Standard hardware, each at its real size", "العتاد القياسي، كل قطعة بحجمها الحقيقي",
     ["HARDWARE.*"], "--azimuth 12 --elevation 18 --size 2000x700 --margin 0.6"),
]


def blender() -> str:
    return subprocess.run([str(ROOT / "08_realistic_digital_twin" / "scripts" / "get_blender.sh")], check=True, capture_output=True, text=True).stdout.strip()


def command(name: str, ids: list[str], options: str) -> list[str]:
    extra = shlex.split(options)
    size = [] if "--size" in extra else ["--size", SIZE]
    return ["render", "--name", name, "--part", *ids, *extra, *size, "--samples", "32"]


def readme() -> str:
    lines = [
        "# Atlas: what lies under the skin",
        "",
        "One picture of each assembly, drawn by the part tool. Written by `09_book_figures/atlas.py`; do not edit by hand.",
        "These are drafts for choosing views, without labels. Under each picture is the command that made it:",
        "change the ids, the direction (`--azimuth`, `--elevation`) or the tint and you have your own.",
        "The ids are in `08_realistic_digital_twin/docs/06_parts_index.md`.",
        "",
    ]
    for name, en, ar, ids, options in PICTURES:
        shown = "npm run part -- render --part " + " ".join(shlex.quote(i) for i in ids) + " " + " ".join(shlex.quote(a) for a in shlex.split(options))
        lines += [f"## {en}", "", f"<div dir=\"rtl\">{ar}</div>", "", f"![{en}]({name}.png)", "", "```", shown, "```", ""]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for name, en, _ar, _ids, _options in PICTURES:
            print(f"{name:<24} {en}")
        return 0
    wanted = [a for a in argv if not a.startswith("--")]
    unknown = sorted(set(wanted) - {p[0] for p in PICTURES})
    if unknown:
        print("unknown picture(s):", ", ".join(unknown), file=sys.stderr)
        return 2
    OUT.mkdir(exist_ok=True)
    executable = blender()
    failed = []
    for name, en, _ar, ids, options in PICTURES:
        if wanted and name not in wanted:
            continue
        args = [executable, "-b", str(BLEND), "--python", str(HERE / "blender" / "part.py"), "--", *command(name, ids, options), "--out", str(OUT)]
        result = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
        picture = OUT / f"{name}.png"
        if result.returncode != 0 or not picture.exists():
            failed.append(name)
            print(f"FAILED {name}\n{result.stdout[-1500:]}\n{result.stderr[-1500:]}", file=sys.stderr)
            continue
        flatten(picture)
        (OUT / f"{name}.json").unlink(missing_ok=True)
        print(f"ok {name:<24} {picture.stat().st_size / 1e3:.0f} kB")
    (OUT / "README.md").write_text(readme(), encoding="utf-8")
    return 1 if failed else 0


def flatten(path: Path) -> None:
    """Put the picture on white and store it compactly: the atlas is read on a page, not composed into one."""
    from PIL import Image
    image = Image.open(path).convert("RGBA")
    page = Image.new("RGBA", image.size, (255, 255, 255, 255))
    page.alpha_composite(image)
    page.convert("RGB").quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
