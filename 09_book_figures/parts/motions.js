// How the parts of the aircraft move when the controls do, as in the Phase 8 viewer (js/rig.js and js/kinematics.js): one
// control moves every part it moves in the real aircraft. No Three.js here; the catalogue applies the numbers about each
// part's own hinge or axis.
import * as K from '../../08_realistic_digital_twin/js/kinematics.js';
import { valueToAngle } from '../../shared/js/gauges.js';

export const D2R = Math.PI / 180;

/** The headings the controls are grouped under. */
export const GROUPS = {
  scene: { en: 'Scene', ar: 'المشهد' },
  flight: { en: 'Flight controls and doors', ar: 'أدوات الطيران والأبواب' },
  engine: { en: 'Engine', ar: 'المحرك' },
  levers: { en: 'Levers and knobs', ar: 'الأذرع والمقابض' },
  switches: { en: 'Switches', ar: 'المفاتيح' },
  instruments: { en: 'Instruments', ar: 'العدادات' },
  trainer: { en: 'Trainer', ar: 'المدرّب' },
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

/** The instrument scales (data/instruments.json, `instruments`), set once the page has read them; until then needles stay put. */
let SCALES = null;
export const setScales = (scales) => { SCALES = scales; };

/** The instruments: control key, scale, range, step, resting reading, names. Setting any of them puts every needle at its reading. */
const INSTRUMENTS = [
  ['asi', 'ASI', 0, 200, 1, 0, 'Airspeed (knots)', 'السرعة (عقدة)'],
  ['alt', 'ALT', 0, 12000, 50, 0, 'Altitude (feet)', 'الارتفاع (قدم)'],
  ['vsi', 'VSI', -2000, 2000, 50, 0, 'Vertical speed (feet per minute)', 'السرعة الرأسية (قدم في الدقيقة)'],
  ['hdg', null, 0, 360, 1, 0, 'Heading (degrees)', 'الاتجاه (بالدرجات)'],
  ['bank', null, -60, 60, 1, 0, 'Bank (degrees)', 'الميل الجانبي (بالدرجات)'],
  ['pitch', null, -20, 20, 1, 0, 'Pitch (degrees)', 'الميل الطولي (بالدرجات)'],
  ['turn', null, -3, 3, 0.1, 0, 'Turn rate (standard rates)', 'معدل الدوران (معدل قياسي)'],
  ['tach', 'TACH', 0, 3500, 50, 0, 'Engine speed (rpm)', 'سرعة المحرك (لفة في الدقيقة)'],
  ['oilP', 'OIL_P', 0, 120, 1, 0, 'Oil pressure (psi)', 'ضغط الزيت (psi)'],
  ['oilT', 'OIL_T', 50, 275, 1, 50, 'Oil temperature (°F)', 'حرارة الزيت (°F)'],
  ['suction', 'SUCTION', 0, 10, 0.1, 0, 'Suction (inches of mercury)', 'الشفط (بوصة زئبق)'],
  ['ammeter', 'AMMETER', -60, 60, 1, 0, 'Ammeter (amps)', 'مقياس التيار (أمبير)'],
  ['fuelL', 'FUEL_L', 0, 20, 0.5, 0, 'Fuel, left tank (gallons)', 'الوقود، الخزان الأيسر (غالون)'],
  ['fuelR', 'FUEL_R', 0, 20, 0.5, 0, 'Fuel, right tank (gallons)', 'الوقود، الخزان الأيمن (غالون)'],
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
  ...INSTRUMENTS.map(([key, scale, min, max, step, home, en, ar]) => ({ group: 'instruments', key, scale, min, max, step, home, en, ar })),
];

/** Every control at rest. `inst` is 0 until a reader sets an instrument; then every needle goes to its reading. */
export const rest = () => ({ ...Object.fromEntries(CONTROLS.map((c) => [c.key, c.home ?? 0])), inst: 0 });

/**
 * What each part does at the given control settings. `hinge` is degrees before the part's own sign, `spin` is radians before its
 * own sign, and `move` is a shift in metres in the part's parent frame. A part in both `spin` and `move` is turned about its own
 * origin and then shifted. Parts not named stay where they are, and at rest every number is zero.
 */
export function pose(s) {
  const hinge = new Map(), spin = new Map(), move = new Map(), glow = new Map();
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

  // (The strengths are lower than the Phase 8 viewer's: it adds a bloom to its glow and this view does not, so the same numbers wash out.)
  // Lamps light when their switch is up and the battery switch is up; the beacon and the strobes flash (see `isLit`). A spark plug glows at the
  // moment it fires, when the ignition is on and the engine is turned (a "hot prop": the magnetos need no battery).
  const lit = (id, color, k, flash) => glow.set(id, { color, k, flash });
  if (s.swBat > 0) {
    if (s.swBeacon > 0) lit('ELECTRICAL.beacon', 0xff2020, 1.6, 'beacon');
    if (s.swNav > 0) { lit('WING_L.nav_light', 0xff2020, 0.8); lit('WING_R.nav_light', 0x20ff40, 0.8); lit('ELECTRICAL.tail_nav_light', 0xffffff, 0.8); }
    if (s.swLanding > 0) lit('ELECTRICAL.landing_light', 0xffffff, 2);
    if (s.swStrobe > 0) { lit('WING_L.strobe', 0xffffff, 3, 'strobe'); lit('WING_R.strobe', 0xffffff, 3, 'strobe'); }
  }
  const mags = s.ignition === -1 ? ['R'] : s.ignition === 0 ? ['L'] : s.ignition > 0 ? ['L', 'R'] : [];
  for (const [id, cyl, mag] of PLUGS) if (mags.includes(mag) && K.sparkActive(deg, cyl)) lit(id, 0x66aaff, 1.6);

  // The instruments, once a reader has set one: the same readings-to-angles as the Phase 8 viewer.
  if (s.inst && SCALES) {
    const turn = (id, degrees) => spin.set(id, degrees * D2R);
    for (const [key, scale] of INSTRUMENTS.map((i) => [i[0], i[1]])) if (scale && scale !== 'ALT') turn(`PANEL.${scale}.needle_${scale}`, valueToAngle(SCALES[scale], s[key]));
    turn('PANEL.ALT.needle_ALT_100', (((s.alt % 1000) + 1000) % 1000) * 0.36);
    turn('PANEL.ALT.needle_ALT_1000', (((s.alt % 10000) + 10000) % 10000) * 0.036);
    turn('PANEL.ALT.needle_ALT_10000', s.alt * 0.0036);
    turn('PANEL.TC.needle_TC', s.turn * 20);
    turn('PANEL.AI.ball', -s.bank); move.set('PANEL.AI.ball', [0, -Math.max(-20, Math.min(20, s.pitch)) * 0.0005, 0]);
    turn('PANEL.DG.card', -s.hdg);
  }
  return { hinge, spin, move, glow };
}

/** The eight spark plugs: part, cylinder and the magneto that fires it (Lycoming: the right magneto fires the lower plugs of odd cylinders and the upper plugs of even ones). */
const PLUGS = [1, 2, 3, 4].flatMap((c) => ['bottom', 'top'].map((pos) => [`ENGINE.plug_${pos}_${c}`, c, (c % 2 === 1) === (pos === 'bottom') ? 'R' : 'L']));
export { PLUGS };
const LIGHTS = ['ELECTRICAL.beacon', 'WING_L.nav_light', 'WING_R.nav_light', 'ELECTRICAL.tail_nav_light', 'ELECTRICAL.landing_light', 'WING_L.strobe', 'WING_R.strobe'];
/** Every part that can light up. */
export const GLOWING = new Set([...LIGHTS, ...PLUGS.map((p) => p[0])]);

/** Every part that any control moves (the instruments count once an instrument is set). */
const NEEDLES = [...INSTRUMENTS.filter((i) => i[1] && i[1] !== 'ALT').map((i) => `PANEL.${i[1]}.needle_${i[1]}`), 'PANEL.ALT.needle_ALT_100', 'PANEL.ALT.needle_ALT_1000', 'PANEL.ALT.needle_ALT_10000', 'PANEL.TC.needle_TC', 'PANEL.AI.ball', 'PANEL.DG.card'];
export const MOVING = new Set([...Object.values(pose(Object.fromEntries(CONTROLS.map((c) => [c.key, c.max])))).slice(0, 3).flatMap((m) => [...m.keys()]), ...NEEDLES]);

/** The connecting rods turn about the z axis of the frame they hang in; every other turning part about its own hinge or spin axis. */
export const ABOUT_PARENT_Z = (id) => /^ENGINE\.rod_\d$/.test(id);

/** Whether a flashing lamp is lit at a moment (milliseconds): the patterns of the Phase 8 viewer's rig. A steady lamp is always lit. */
export function isLit(flash, ms) {
  if (flash === 'beacon') return Math.sin(ms / 90) > 0.3;
  if (flash === 'strobe') return ms % 1400 < 60;
  return true;
}

/**
 * Scenes: the controls and instruments set together to a state worth looking at. They pose the aircraft; nothing is simulated
 * between them. The values are typical and illustrative, not read from the POH. The `throttle`, `mixture` and other knob values
 * are how far the knob is pulled out: a closed throttle is 1, full throttle 0, and a rich mixture 0.
 */
export const SCENES = [
  { key: 'cold', en: 'Parked, as built', ar: 'متوقفة كما بُنيت', set: {} },
  { key: 'start', en: 'Engine start: starter turning', ar: 'تشغيل المحرك: البادئ يدير المحرك',
    set: { swBat: 1, swAlt: 1, mixture: 0, throttle: 0.9, primer: 0.4, ignition: 2, fuelSel: 1, crank: 90, tach: 200, oilP: 5, oilT: 60, ammeter: -30, fuelL: 12, fuelR: 12 } },
  { key: 'runup', en: 'Run-up at 1700 rpm, magneto on Right', ar: 'فحص المحرك عند 1700 لفة، المغناطيس الأيمن',
    set: { swBat: 1, swAlt: 1, swAvionics: 1, swBeacon: 1, mixture: 0, throttle: 0.55, ignition: -1, fuelSel: 1, crank: 700, tach: 1700, oilP: 60, oilT: 150, suction: 5, ammeter: 10, fuelL: 12, fuelR: 12, hdg: 90 } },
  { key: 'takeoff', en: 'Takeoff roll: full power, flaps 10', ar: 'الإقلاع: قدرة كاملة، قلابات 10',
    set: { swBat: 1, swAlt: 1, swAvionics: 1, swBeacon: 1, swNav: 1, swLanding: 1, swStrobe: 1, flaps: 10, mixture: 0, throttle: 0, ignition: 1, fuelSel: 1, elevator: 0.3, trim: 0.1, crank: 300, tach: 2300, oilP: 70, oilT: 180, suction: 5, ammeter: 8, asi: 55, vsi: 500, pitch: 8, hdg: 90, fuelL: 15, fuelR: 15 } },
  { key: 'cruise', en: 'Cruise at 5,500 feet', ar: 'الطيران المستوي على ارتفاع 5500 قدم',
    set: { swBat: 1, swAlt: 1, swAvionics: 1, swBeacon: 1, swNav: 1, swStrobe: 1, mixture: 0.2, throttle: 0.3, ignition: 1, fuelSel: 1, trim: 0.05, crank: 500, tach: 2400, oilP: 70, oilT: 190, suction: 5, ammeter: 6, asi: 110, alt: 5500, pitch: 2, hdg: 90, fuelL: 11, fuelR: 10 } },
  { key: 'landing', en: 'Final approach: flaps 40, landing light on', ar: 'الاقتراب النهائي: قلابات 40، ضوء الهبوط مضاء',
    set: { swBat: 1, swAlt: 1, swAvionics: 1, swBeacon: 1, swNav: 1, swLanding: 1, swStrobe: 1, flaps: 40, mixture: 0, throttle: 0.8, ignition: 1, fuelSel: 1, elevator: 0.2, trim: -0.2, crank: 100, tach: 1500, oilP: 60, oilT: 180, suction: 5, ammeter: 5, asi: 65, alt: 800, vsi: -500, pitch: -3, bank: 5, hdg: 270, fuelL: 5, fuelR: 5 } },
];

/** The four strokes, named in both languages. */
export const STROKE_NAMES = {
  intake: { en: 'Intake', ar: 'السحب' },
  compression: { en: 'Compression', ar: 'الانضغاط' },
  power: { en: 'Power', ar: 'القدرة' },
  exhaust: { en: 'Exhaust', ar: 'العادم' },
};

/** The stroke each cylinder is on at a crank angle (degrees, 0 to 720), cylinders 1 to 4. */
export const strokes = (crank) => [1, 2, 3, 4].map((cyl) => ({ cyl, stroke: K.strokeOf(crank, cyl) }));
