// How the parts of the aircraft move when the controls do, as in the Phase 8 viewer (js/rig.js): one control moves every part
// it moves in the real aircraft. No Three.js here; the catalogue applies the numbers about each part's own hinge or axis.
export const D2R = Math.PI / 180;

/** The controls, in the order they are offered. Each runs from `min` to `max`; `value` is where the aircraft rests. */
export const CONTROLS = [
  { key: 'aileron', min: -1, max: 1, step: 0.01, en: 'Ailerons and yokes', ar: 'الجنيحات وعجلتا القيادة', note: { en: 'Turning the yoke: one aileron goes up, the other down, and both yokes turn.', ar: 'عند تدوير العجلة يُرفع جنيح ويُخفض الآخر وتدور العجلتان.' } },
  { key: 'elevator', min: -1, max: 1, step: 0.01, en: 'Elevator and yokes in and out', ar: 'ذيل الارتفاع والعجلتان للداخل والخارج', note: { en: 'Pull back: elevator up; the yoke shafts slide.', ar: 'عند السحب للخلف يرتفع ذيل الارتفاع وينزلق عمودا العجلتين.' } },
  { key: 'rudder', min: -1, max: 1, step: 0.01, en: 'Rudder, pedals and nose wheel', ar: 'الدفة والدواسات وعجلة الأنف', note: { en: 'The rudder, the four pedals and the nose strut move together.', ar: 'تتحرك الدفة والدواسات الأربع وساق عجلة الأنف معًا.' } },
  { key: 'trim', min: -1, max: 1, step: 0.01, en: 'Elevator trim', ar: 'ضبط ذيل الارتفاع', note: { en: 'The trim tab and the trim wheel.', ar: 'لسان الضبط وعجلة الضبط.' } },
  { key: 'flaps', min: 0, max: 40, step: 1, en: 'Flaps (degrees)', ar: 'القلابات (بالدرجات)', note: { en: 'Both flaps and the flap switch.', ar: 'القلابان ومفتاح القلابات.' } },
  { key: 'doorL', min: 0, max: 1, step: 0.01, en: 'Left cabin door', ar: 'باب المقصورة الأيسر' },
  { key: 'doorR', min: 0, max: 1, step: 0.01, en: 'Right cabin door', ar: 'باب المقصورة الأيمن' },
  { key: 'baggage', min: 0, max: 1, step: 0.01, en: 'Baggage door', ar: 'باب الأمتعة' },
  { key: 'cowl', min: 0, max: 1, step: 0.01, en: 'Upper cowl lifted off', ar: 'رفع الغطاء العلوي للمحرك' },
  { key: 'prop', min: 0, max: 360, step: 1, en: 'Propeller (degrees)', ar: 'المروحة (بالدرجات)' },
];

export const rest = () => Object.fromEntries(CONTROLS.map((c) => [c.key, 0]));

/**
 * What each part does at the given control settings. `hinge` is degrees before the part's own sign, `spin` is radians before its
 * own sign, and `move` is a shift in metres in the part's parent frame. Parts not named stay where they are.
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
  spin.set('POWERPLANT.spinner', s.prop * D2R);
  move.set('POWERPLANT.cowl_upper', [0, 0.9 * s.cowl, 0.4 * s.cowl]);
  return { hinge, spin, move };
}

/** Every part that any control moves. */
export const MOVING = new Set([...Object.values(pose(Object.fromEntries(CONTROLS.map((c) => [c.key, 1])))).flatMap((m) => [...m.keys()])]);
