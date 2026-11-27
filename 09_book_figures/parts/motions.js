// How the parts of the aircraft move when the controls do, as in the Phase 8 viewer (js/rig.js and js/kinematics.js): one
// control moves every part it moves in the real aircraft. No Three.js here; the catalogue applies the numbers about each
// part's own hinge or axis.
import * as K from '../../08_realistic_digital_twin/js/kinematics.js';

export const D2R = Math.PI / 180;

/** The headings the controls are grouped under. */
export const GROUPS = {
  flight: { en: 'Flight controls and doors', ar: 'أدوات الطيران والأبواب' },
  engine: { en: 'Engine', ar: 'المحرك' },
  levers: { en: 'Levers and knobs', ar: 'الأذرع والمقابض' },
  switches: { en: 'Switches', ar: 'المفاتيح' },
};

/** The panel switches: control key, part, English and Arabic names. A switch is up (+15 degrees) or down (-15 degrees). */
export const SWITCHES = [
  ['swBat', 'PANEL.master_bat', 'Master switch: battery', 'المفتاح الرئيسي: البطارية'],
  ['swAlt', 'PANEL.master_alt', 'Master switch: alternator', 'المفتاح الرئيسي: المولّد'],
  ['swAvionics', 'PANEL.switch_avionics_master', 'Avionics master', 'مفتاح الإلكترونيات الرئيسي'],
  ['swBeacon', 'PANEL.switch_beacon', 'Beacon', 'المنارة'],
  ['swNav', 'PANEL.switch_nav_lights', 'Navigation lights', 'أضواء الملاحة'],
  ['swLanding', 'PANEL.switch_landing_light', 'Landing light', 'ضوء الهبوط'],
  ['swTaxi', 'PANEL.switch_taxi_light', 'Taxi light', 'ضوء التاكسي'],
  ['swPitot', 'PANEL.switch_pitot_heat', 'Pitot heat', 'تسخين أنبوب بيتو'],
  ['swStrobe', 'PANEL.switch_strobe', 'Strobe', 'الضوء الومضي'],
];

/** The knobs that pull straight out toward the pilot: control key, part, how far it travels (metres) fully out, names. */
const PULLS = [
  ['throttle', 'PANEL.throttle', 0.085, 'Throttle knob pulled out', 'سحب مقبض الخانق'],
  ['mixture', 'PANEL.mixture', 0.07, 'Mixture knob pulled out', 'سحب مقبض الخليط'],
  ['carbHeat', 'PANEL.carb_heat', 0.07, 'Carburettor heat pulled out', 'سحب مقبض تسخين المكربن'],
  ['cabinHeat', 'PANEL.cabin_heat', 0.05, 'Cabin heat pulled out', 'سحب مقبض تدفئة المقصورة'],
  ['cabinAir', 'PANEL.cabin_air', 0.05, 'Cabin air pulled out', 'سحب مقبض هواء المقصورة'],
  ['primer', 'PANEL.primer', 0.06, 'Primer pulled out', 'سحب مضخة التحضير'],
  ['parking', 'INTERIOR.parking_brake', 0.035, 'Parking brake pulled out', 'سحب مقبض فرامل الإيقاف'],
];

/** The controls, in the order they are offered. Each runs from `min` to `max`; the aircraft rests at 0. */
export const CONTROLS = [
  { group: 'flight', key: 'aileron', min: -1, max: 1, step: 0.01, en: 'Ailerons and yokes', ar: 'الجنيحات وعجلتا القيادة', note: { en: 'Turning the yoke: one aileron goes up, the other down, and both yokes turn.', ar: 'عند تدوير العجلة يُرفع جنيح ويُخفض الآخر وتدور العجلتان.' } },
  { group: 'flight', key: 'elevator', min: -1, max: 1, step: 0.01, en: 'Elevator and yokes in and out', ar: 'ذيل الارتفاع والعجلتان للداخل والخارج', note: { en: 'Pull back: elevator up; the yoke shafts slide.', ar: 'عند السحب للخلف يرتفع ذيل الارتفاع وينزلق عمودا العجلتين.' } },
  { group: 'flight', key: 'rudder', min: -1, max: 1, step: 0.01, en: 'Rudder, pedals and nose wheel', ar: 'الدفة والدواسات وعجلة الأنف', note: { en: 'The rudder, the four pedals and the nose strut move together.', ar: 'تتحرك الدفة والدواسات الأربع وساق عجلة الأنف معًا.' } },
  { group: 'flight', key: 'trim', min: -1, max: 1, step: 0.01, en: 'Elevator trim', ar: 'ضبط ذيل الارتفاع', note: { en: 'The trim tab and the trim wheel.', ar: 'لسان الضبط وعجلة الضبط.' } },
  { group: 'flight', key: 'flaps', min: 0, max: 40, step: 1, en: 'Flaps (degrees)', ar: 'القلابات (بالدرجات)', note: { en: 'Both flaps and the flap switch.', ar: 'القلابان ومفتاح القلابات.' } },
  { group: 'flight', key: 'doorL', min: 0, max: 1, step: 0.01, en: 'Left cabin door', ar: 'باب المقصورة الأيسر' },
  { group: 'flight', key: 'doorR', min: 0, max: 1, step: 0.01, en: 'Right cabin door', ar: 'باب المقصورة الأيمن' },
  { group: 'flight', key: 'baggage', min: 0, max: 1, step: 0.01, en: 'Baggage door', ar: 'باب الأمتعة' },
  { group: 'engine', key: 'cowl', min: 0, max: 1, step: 0.01, en: 'Upper cowl lifted off', ar: 'رفع الغطاء العلوي للمحرك' },
  { group: 'engine', key: 'crank', min: 0, max: 720, step: 1, en: 'Turn the engine by hand (degrees of crank)', ar: 'أدِر المحرك باليد (درجات عمود المرفق)', note: { en: 'Two turns make one cycle: the crankshaft, propeller, pistons, connecting rods, valves and camshaft move together (firing order 1-3-2-4). Lift the cowl to see them.', ar: 'دورتان تكوّنان دورة واحدة: يتحرك عمود المرفق والمروحة والمكابس وأذرع التوصيل والصمامات وعمود الحدبات معًا (ترتيب الإشعال 1-3-2-4). ارفع الغطاء لتراها.' } },
  ...PULLS.map(([key, , travel, en, ar]) => ({ group: 'levers', key, min: 0, max: 1, step: 0.01, travel, en, ar })),
  { group: 'levers', key: 'ignition', min: -2, max: 2, step: 1, names: [{ en: 'Off', ar: 'إيقاف' }, { en: 'Right', ar: 'يمين' }, { en: 'Left', ar: 'يسار' }, { en: 'Both', ar: 'كلاهما' }, { en: 'Start', ar: 'تشغيل' }], en: 'Ignition switch', ar: 'مفتاح الإشعال' },
  { group: 'levers', key: 'fuelSel', min: -1, max: 2, step: 1, names: [{ en: 'Left', ar: 'يسار' }, { en: 'Both', ar: 'كلاهما' }, { en: 'Right', ar: 'يمين' }, { en: 'Off', ar: 'إغلاق' }], en: 'Fuel selector', ar: 'محدد الوقود' },
  ...SWITCHES.map(([key, , en, ar]) => ({ group: 'switches', key, min: -1, max: 1, step: 1, toggle: true, en, ar })),
];

export const rest = () => Object.fromEntries(CONTROLS.map((c) => [c.key, 0]));

/**
 * What each part does at the given control settings. `hinge` is degrees before the part's own sign, `spin` is radians before its
 * own sign, and `move` is a shift in metres in the part's parent frame. A part in both `spin` and `move` is turned about its own
 * origin and then shifted. Parts not named stay where they are, and at rest every number is zero.
 */
export function pose(s) {
  const hinge = new Map(), spin = new Map(), move = new Map();
  const ail = s.aileron * 20;
  hinge.set('WING_L.aileron', -ail * 0.85); hinge.set('WING_R.aileron', ail * 0.85);
  hinge.set('EMPENNAGE.elevator', s.elevator > 0 ? -s.elevator * 28 : -s.elevator * 23);
  hinge.set('EMPENNAGE.rudder', s.rudder * 16);
  hinge.set('EMPENNAGE.trim_tab', -s.trim * 20);
  hinge.set('WING_L.flap', s.flaps); hinge.set('WING_R.flap', s.flaps);
  hinge.set('PANEL.flap_switch', -(s.flaps / 40) * 30);
  hinge.set('AIRFRAME.door_L', s.doorL * 62); hinge.set('AIRFRAME.door_R', s.doorR * 62);
  hinge.set('AIRFRAME.baggage_door', s.baggage * 95);
  hinge.set('GEAR.nose_strut', s.rudder * 10);
  for (const side of ['L', 'R']) {
    spin.set(`INTERIOR.yoke_${side}`, s.aileron * 80 * D2R);
    move.set(`INTERIOR.yoke_shaft_${side}`, [0, 0, s.elevator * 0.05]);
    hinge.set(`INTERIOR.pedal_${side}_L`, -s.rudder * 12); hinge.set(`INTERIOR.pedal_${side}_R`, s.rudder * 12);
  }
  spin.set('INTERIOR.trim_wheel', s.trim * 2.5);
  move.set('POWERPLANT.cowl_upper', [0, 0.9 * s.cowl, 0.4 * s.cowl]);

  // The engine, turned by hand: the same slider-crank as the Phase 8 viewer, measured from where the model is built (crank 0).
  const theta = s.crank * D2R, deg = s.crank;
  spin.set('ENGINE.crankshaft', theta); spin.set('ENGINE.camshaft', -theta / 2);
  spin.set('ENGINE.crank_flange_pulley', theta); spin.set('POWERPLANT.spinner', theta);
  for (const c of [1, 2, 3, 4]) {
    move.set(`ENGINE.piston_${c}`, [K.pistonPosition(theta, c)[0] - K.pistonPosition(0, c)[0], 0, 0]);
    const pin = K.pinPosition(theta, c), pin0 = K.pinPosition(0, c);
    move.set(`ENGINE.rod_${c}`, [pin[0] - pin0[0], pin[1] - pin0[1], 0]);
    spin.set(`ENGINE.rod_${c}`, K.rodAngle(theta, c) - K.rodAngle(0, c));
    const side = K.CYLINDERS[c].side;
    for (const kind of ['intake', 'exhaust']) move.set(`ENGINE.valve_${kind}_${c}`, [-side * (K.valveLift(deg, c, kind) - K.valveLift(0, c, kind)) * K.VALVE_LIFT, 0, 0]);
  }

  // Knobs that pull straight out toward the pilot (the model's -Z), the ignition key and the fuel selector turning, switches up or down.
  for (const [key, id, travel] of PULLS) move.set(id, [0, 0, -s[key] * travel]);
  spin.set('PANEL.ignition_switch', s.ignition * 35 * D2R);
  spin.set('FUEL.selector_handle', s.fuelSel * 90 * D2R);
  for (const [key, id] of SWITCHES) hinge.set(id, s[key] * 15);
  return { hinge, spin, move };
}

/** Every part that any control moves. */
export const MOVING = new Set(Object.values(pose(Object.fromEntries(CONTROLS.map((c) => [c.key, c.max])))).flatMap((m) => [...m.keys()]));

/** The connecting rods turn about the z axis of the frame they hang in; every other turning part about its own hinge or spin axis. */
export const ABOUT_PARENT_Z = (id) => /^ENGINE\.rod_\d$/.test(id);
