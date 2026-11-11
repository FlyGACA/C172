// The survey of one aircraft and of one pilot in its seat, for the flight model and the pilot's seat.
//
// Until a survey is recorded here, nothing in the flight model or the seat is measured: the numbers are the
// handbook's, derived from the handbook's, or estimated. A survey does two different things:
//   - a ground or seat measurement REPLACES a number, and that number then carries the source 'measured';
//   - a flight observation is COMPARED with what the model does at the same weight, altitude and temperature.
//     It replaces nothing: fitting the model to an aircraft is a deliberate step, taken with the comparison in hand.
// Only observations marked verified count. The file that holds them is data/flight_survey.json.
import * as F from './flight.js';
import { flyTakeoff, flyLanding } from './pilot.js';
import { HEAD, CABIN, floorAt, applyMeasuredSeat, resetMeasuredSeat } from './seat.js';

const IN = 0.0254;
const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;
const isaDev = (altFt, oatC) => oatC - (15 - 0.0019812 * altFt);
/** What the model was built with: a number that a survey has replaced remembers it. */
const built = (name) => F.FM[name].was ?? F.FM[name].v;
const EYE0 = [...HEAD.eye], SEAT0 = { reach: HEAD.reach, shoulderBelow: HEAD.shoulderBelow, shoulderAside: HEAD.shoulderAside };

/** Where the centre of gravity is between its limits at a weight, from its station (in): 0 most forward, 1 most rearward. */
function cgFraction(weightLb, cgIn) {
  const fwd = F.cgStation(weightLb, 0), aft = F.cgStation(weightLb, 1);
  return Math.min(1, Math.max(0, (cgIn - fwd) / (aft - fwd)));
}
const conditions = (r) => ({ ...r.conditions, isaDevC: isaDev(r.conditions.pressure_altitude_ft, r.conditions.oat_c) });
/** Level flight at which the model turns a given RPM; NaN if full throttle does not give it. */
function levelAtRpm(rpm, c) {
  const at = (kcas) => F.trim({ kcas, altFt: c.pressure_altitude_ft, isaDevC: c.isaDevC, weightLb: c.weight_lb });
  let lo = 55, hi = 150;
  if (at(hi).rpm < rpm) return NaN;
  for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (at(mid).rpm < rpm) lo = mid; else hi = mid; }
  const t = at(lo);
  return t.torque > F.fullThrottleTorque(F.chargeAt(c.pressure_altitude_ft, c.isaDevC)) ? NaN : F.kiasFromKcas(t.kcas);
}
function onRunway(c) {
  const f = F.createFlight({ fieldElevFt: c.pressure_altitude_ft, isaDevC: c.isaDevC, weightLb: c.weight_lb });
  return F.setWind(f, 0, c.headwind_kt);                                   // the runway points north: a headwind is from the north
}

/** Conditions a record can carry, and what is plausible for each. */
export const CONDITIONS = {
  flap_deg: [0, 40], weight_lb: [1400, 2300], cg_in: [35, 47.3], pressure_altitude_ft: [-1000, 14000], oat_c: [-40, 50], kias: [40, 160], rpm: [1800, 2700], headwind_kt: [-10, 40],
};

/**
 * What a survey can record. kind: ground | seat | flight. unit and range: what the value must be in and between.
 * needs: the conditions that must come with it. replaces: the number it replaces once verified (ground and seat).
 * model(record): what the model has, in the same unit, at the record's conditions.
 */
export const SURVEY = {
  // ---- on the ground, engine off: these replace a number of the flight model
  elevator_up_deg: { kind: 'ground', unit: 'deg', range: [20, 32], needs: [], replaces: 'FM.elevatorUpDeg', model: () => built('elevatorUpDeg'),
    en: 'Elevator travel up', ar: 'مدى حركة الرافع إلى أعلى',
    how_en: 'Inclinometer on the elevator. Zero it with the elevator faired with the stabilizer, then hold the control wheel fully back and read the angle.',
    how_ar: 'ميزان زوايا على الرافع. صفّره والرافع على استقامة المثبّت الأفقي، ثم اسحب عجلة القيادة إلى آخرها واقرأ الزاوية.' },
  elevator_down_deg: { kind: 'ground', unit: 'deg', range: [15, 28], needs: [], replaces: 'FM.elevatorDownDeg', model: () => built('elevatorDownDeg'),
    en: 'Elevator travel down', ar: 'مدى حركة الرافع إلى أسفل',
    how_en: 'As above, with the control wheel fully forward.', how_ar: 'كما سبق، وعجلة القيادة مدفوعة إلى آخرها.' },
  flap_time_s: { kind: 'ground', unit: 's', range: [4, 20], needs: [], replaces: 'FM.flapRateDegS', model: () => 40 / built('flapRateDegS'),
    en: 'Time for the flaps to travel from up to 40°', ar: 'زمن حركة القلابات من الرفع الكامل إلى 40°',
    how_en: 'Stopwatch, on the ground, master switch on, engine off. Note the bus voltage in the notes.',
    how_ar: 'ساعة إيقاف، على الأرض، المفتاح الرئيسي ON والمحرك متوقف. دوّن جهد الناقل في الملاحظات.' },
  // ---- the pilot in the seat, as he or she sits to fly: these replace the estimates of the pilot's seat
  eye_to_panel_in: { kind: 'seat', unit: 'in', range: [16, 32], needs: [], replaces: 'HEAD.eye (fore and aft)', model: () => (CABIN.panelFaceZ - EYE0[2]) / IN,
    en: 'Eye: distance back from the face of the instrument panel', ar: 'العين: البعد إلى الخلف عن وجه لوحة العدادات',
    how_en: 'Seated to fly, head upright. Level tape from the eye straight ahead to the face of the panel (the metal, not a bezel or the glareshield).',
    how_ar: 'والطيار جالس كما يطير ورأسه معتدل. شريط قياس أفقي من العين إلى الأمام مباشرة حتى وجه اللوحة (المعدن، لا إطار عداد ولا الحاجب العلوي).' },
  eye_left_of_centreline_in: { kind: 'seat', unit: 'in', range: [8, 14], needs: [], replaces: 'HEAD.eye (sideways)', model: () => EYE0[0] / IN,
    en: 'Eye: distance to the left of the aircraft centreline', ar: 'العين: البعد إلى يسار خط منتصف الطائرة',
    how_en: 'From between the eyes to the centreline of the cabin (the middle of the pedestal).', how_ar: 'من بين العينين إلى خط منتصف المقصورة (منتصف القاعدة الوسطى).' },
  eye_above_floor_in: { kind: 'seat', unit: 'in', range: [32, 44], needs: [], replaces: 'HEAD.eye (height)', model: () => (EYE0[1] - floorAt(EYE0[2])) / IN,
    en: 'Eye: height above the cabin floor directly below it', ar: 'العين: الارتفاع فوق أرضية المقصورة تحتها مباشرة',
    how_en: 'Plumb line or tape from the eye to the floor panel (not the carpet edge or the seat rail).', how_ar: 'خيط شاقول أو شريط قياس من العين إلى لوح الأرضية (لا إلى حافة السجاد ولا إلى سكة المقعد).' },
  arm_reach_in: { kind: 'seat', unit: 'in', range: [22, 34], needs: [], replaces: 'HEAD.reach', model: () => SEAT0.reach / IN,
    en: 'Reach of the arm: shoulder joint to the centre of the closed fist', ar: 'مدى الذراع: من مفصل الكتف إلى منتصف القبضة المغلقة',
    how_en: 'Arm straight out, harness fastened as in flight.', how_ar: 'والذراع ممدودة، والحزام مربوط كما في الطيران.' },
  shoulder_below_eye_in: { kind: 'seat', unit: 'in', range: [7, 13], needs: [], replaces: 'HEAD.shoulderBelow', model: () => SEAT0.shoulderBelow / IN,
    en: 'Shoulder joint: height below the eye', ar: 'مفصل الكتف: الانخفاض عن العين', how_en: 'Seated to fly.', how_ar: 'والطيار جالس كما يطير.' },
  shoulder_width_in: { kind: 'seat', unit: 'in', range: [12, 20], needs: [], replaces: 'HEAD.shoulderAside', model: () => (2 * SEAT0.shoulderAside) / IN,
    en: 'Width between the two shoulder joints', ar: 'العرض بين مفصلي الكتفين', how_en: 'Seated to fly.', how_ar: 'والطيار جالس كما يطير.' },
  // ---- in flight or on the runway: these are compared with the model, they replace nothing
  static_rpm: { kind: 'flight', unit: 'rpm', range: [2000, 2700], needs: ['pressure_altitude_ft', 'oat_c'],
    model: (r) => { const c = conditions(r); return F.equilibriumRpm(F.engineAt(1, F.chargeAt(c.pressure_altitude_ft, c.isaDevC)), 0, F.densityAt(c.pressure_altitude_ft, c.isaDevC)); },
    en: 'Static RPM: full throttle, standing still', ar: 'دورات المحرك والطائرة واقفة: خانق كامل',
    how_en: 'Brakes held, into the wind, mixture rich, carburetor heat off. Read the tachometer when it settles.', how_ar: 'الكوابح مشدودة، والطائرة مواجهة للريح، الخليط غني، تسخين المكربن مغلق. اقرأ عداد الدورات بعد أن يستقر.' },
  stall_kias: { kind: 'flight', unit: 'kt', range: [30, 70], needs: ['flap_deg', 'weight_lb', 'cg_in'],
    model: (r) => { const c = r.conditions; return F.kiasFromKcas(F.stallSpeedKcas({ flapDeg: c.flap_deg, weightLb: c.weight_lb, cgFrac: cgFraction(c.weight_lb, c.cg_in) }), c.flap_deg); },
    en: 'Stalling speed, power off, wings level', ar: 'سرعة الانهيار، المحرك على التهدئة والجناحان مستويان',
    how_en: 'Throttle closed, slow down by about one knot a second, read the airspeed at the break. At a safe altitude, with an instructor.', how_ar: 'الخانق مغلق، أبطئ بنحو عقدة في الثانية، واقرأ السرعة عند لحظة الانهيار. على ارتفاع آمن ومع مدرّب.' },
  stall_warning_kias: { kind: 'flight', unit: 'kt', range: [35, 80], needs: ['flap_deg', 'weight_lb', 'cg_in'],
    model: (r) => { const c = r.conditions; return F.kiasFromKcas(F.stallSpeedKcas({ flapDeg: c.flap_deg, weightLb: c.weight_lb, cgFrac: cgFraction(c.weight_lb, c.cg_in) }) / Math.sqrt(F.FM.stallWarningMargin.v), c.flap_deg); },
    en: 'Airspeed at which the stall warning horn begins', ar: 'السرعة التي يبدأ عندها بوق إنذار الانهيار',
    how_en: 'In the same approach to the stall: the airspeed when the horn first sounds.', how_ar: 'في الاقتراب نفسه من الانهيار: السرعة عند أول صوت للبوق.' },
  climb_fpm: { kind: 'flight', unit: 'ft_min', range: [-200, 1200], needs: ['kias', 'pressure_altitude_ft', 'oat_c', 'weight_lb'],
    model: (r) => { const c = conditions(r); return F.trim({ kcas: F.kcasFromKias(c.kias), altFt: c.pressure_altitude_ft, isaDevC: c.isaDevC, weightLb: c.weight_lb, torque: F.fullThrottleTorque(F.chargeAt(c.pressure_altitude_ft, c.isaDevC)) }).climbFpm; },
    en: 'Rate of climb: full throttle, flaps up, steady speed', ar: 'معدل الصعود: خانق كامل، القلابات مرفوعة، سرعة ثابتة',
    how_en: 'Time the climb through 500 ft about the altitude noted, altimeter set to 29.92. Mixture as the handbook says for the altitude.', how_ar: 'وقّت الصعود عبر 500 قدم حول الارتفاع المدوَّن، ومقياس الارتفاع مضبوط على 29.92. الخليط كما يقول الدليل لذلك الارتفاع.' },
  cruise_kias: { kind: 'flight', unit: 'kt', range: [60, 140], needs: ['rpm', 'pressure_altitude_ft', 'oat_c', 'weight_lb'],
    model: (r) => levelAtRpm(r.conditions.rpm, conditions(r)),
    en: 'Indicated airspeed in level flight at a set RPM', ar: 'السرعة المبيَّنة في الطيران المستوي عند دورات محددة',
    how_en: 'Level, trimmed, mixture leaned as the handbook says; wait two minutes for the speed to settle.', how_ar: 'طيران مستوٍ وموازَن، والخليط مفقَّر كما يقول الدليل؛ انتظر دقيقتين حتى تستقر السرعة.' },
  glide_sink_fpm: { kind: 'flight', unit: 'ft_min', range: [300, 1500], needs: ['kias', 'flap_deg', 'pressure_altitude_ft', 'oat_c', 'weight_lb'],
    model: (r) => { const c = conditions(r); return -F.trim({ kcas: F.kcasFromKias(c.kias, c.flap_deg), altFt: c.pressure_altitude_ft, isaDevC: c.isaDevC, weightLb: c.weight_lb, flapDeg: c.flap_deg, engine: F.engineAt(0, F.chargeAt(c.pressure_altitude_ft, c.isaDevC)) }).climbFpm; },
    en: 'Rate of descent, throttle closed, steady speed', ar: 'معدل الهبوط، الخانق مغلق، سرعة ثابتة',
    how_en: 'Time the descent through 500 ft about the altitude noted. Carburetor heat as the handbook says.', how_ar: 'وقّت الهبوط عبر 500 قدم حول الارتفاع المدوَّن. تسخين المكربن كما يقول الدليل.' },
  takeoff_roll_ft: { kind: 'flight', unit: 'ft', range: [300, 3000], needs: ['weight_lb', 'pressure_altitude_ft', 'oat_c', 'headwind_kt'],
    model: (r) => { const c = conditions(r), k = Math.sqrt(c.weight_lb / F.FM.maxWeightLb.v); return flyTakeoff(onRunway(c), { rotateKias: 46 * k, v50: 59 * k }).groundRollFt; },
    en: 'Takeoff ground roll, short-field technique of the handbook', ar: 'مسافة الجري عند الإقلاع، بأسلوب المدرج القصير في الدليل',
    how_en: 'Paved, level, dry runway; flaps up; full throttle before the brakes are released. Count runway lights or measure from marks.', how_ar: 'مدرج معبّد مستوٍ جاف؛ القلابات مرفوعة؛ خانق كامل قبل تحرير الكوابح. عُدّ أضواء المدرج أو قِس من علامات.' },
  landing_roll_ft: { kind: 'flight', unit: 'ft', range: [200, 2500], needs: ['weight_lb', 'pressure_altitude_ft', 'oat_c', 'headwind_kt'],
    model: (r) => flyLanding(onRunway(conditions(r))).groundRollFt,
    en: 'Landing ground roll, short-field technique of the handbook', ar: 'مسافة الجري عند الهبوط، بأسلوب المدرج القصير في الدليل',
    how_en: 'Flaps 40°, power off, maximum braking, paved level dry runway.', how_ar: 'القلابات 40°، المحرك على التهدئة، أقصى كبح، مدرج معبّد مستوٍ جاف.' },
};

export const STATUSES = ['raw', 'verified', 'rejected'];
export const COLUMNS = ['id', 'parameter', 'value', 'unit', 'tolerance', ...Object.keys(CONDITIONS), 'method', 'recorded_at', 'recorded_by', 'verification_status', 'notes'];

/** Everything wrong with a survey file, as sentences; empty if it is sound. */
export function validateSurvey(doc) {
  const errors = [];
  if (!doc || typeof doc !== 'object') return ['the survey is not an object'];
  if (doc.schema_version !== 1) errors.push('schema_version must be 1');
  if (!doc.aircraft || typeof doc.aircraft !== 'object') errors.push('aircraft is missing');
  if (!Array.isArray(doc.records)) return [...errors, 'records must be a list'];
  const seen = new Set();
  doc.records.forEach((r, i) => {
    const at = `record ${r && r.id ? r.id : i + 1}`;
    const bad = (m) => errors.push(`${at}: ${m}`);
    if (!r || typeof r !== 'object') { bad('not an object'); return; }
    if (typeof r.id !== 'string' || !/^[a-z0-9][a-z0-9._-]*$/.test(r.id)) bad('id must be lower-case letters, digits, dot, dash or underscore');
    else if (seen.has(r.id)) bad('the id is used twice'); else seen.add(r.id);
    const def = SURVEY[r.parameter];
    if (!def) { bad(`"${r.parameter}" is not something this survey records`); return; }
    if (r.unit !== def.unit) bad(`the unit of ${r.parameter} is ${def.unit}, not "${r.unit}"`);
    if (!Number.isFinite(r.value)) bad('the value is not a number');
    else if (r.value < def.range[0] || r.value > def.range[1]) bad(`${r.value} ${def.unit} is outside ${def.range[0]} to ${def.range[1]}: check the reading and the unit`);
    if (!Number.isFinite(r.tolerance) || r.tolerance < 0) bad('the tolerance must be zero or more');
    const c = r.conditions || {};
    for (const k of def.needs) {
      if (!Number.isFinite(c[k])) bad(`${r.parameter} needs ${k}`);
      else if (c[k] < CONDITIONS[k][0] || c[k] > CONDITIONS[k][1]) bad(`${k} ${c[k]} is outside ${CONDITIONS[k][0]} to ${CONDITIONS[k][1]}`);
    }
    for (const k of Object.keys(c)) if (!(k in CONDITIONS)) bad(`"${k}" is not a condition this survey records`);
    if (typeof r.method !== 'string' || !r.method.trim()) bad('how it was measured is missing');
    if (typeof r.recorded_at !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(r.recorded_at) || Number.isNaN(Date.parse(r.recorded_at))) bad('recorded_at must be a date, YYYY-MM-DD');
    if (typeof r.recorded_by !== 'string' || !r.recorded_by.trim()) bad('who recorded it is missing');
    if (!STATUSES.includes(r.verification_status)) bad(`verification_status must be one of ${STATUSES.join(', ')}`);
    if (typeof r.notes !== 'string') bad('notes must be text (it may be empty)');
  });
  // a verified measurement is of an identified aircraft
  const verified = doc.records.some((r) => r && r.verification_status === 'verified' && SURVEY[r.parameter] && SURVEY[r.parameter].kind !== 'seat');
  const a = doc.aircraft || {};
  if (verified && !(typeof a.tail_number === 'string' && a.tail_number.trim() && typeof a.serial_number === 'string' && a.serial_number.trim())) {
    errors.push('a verified measurement of the aircraft needs the registration and the serial number of that aircraft');
  }
  return errors;
}

const counted = (doc, includeRaw) => doc.records.filter((r) => r.verification_status === 'verified' || (includeRaw && r.verification_status === 'raw'));

/** Each observation beside what the model has: { id, parameter, kind, value, unit, model, difference, tolerance, within, replaces }. */
export function compareSurvey(doc, { includeRaw = false } = {}) {
  return counted(doc, includeRaw).map((r) => {
    const def = SURVEY[r.parameter], model = def.model(r);
    return { id: r.id, parameter: r.parameter, kind: def.kind, status: r.verification_status, value: r.value, unit: r.unit, model, difference: r.value - model, tolerance: r.tolerance,
      within: Number.isFinite(model) ? Math.abs(r.value - model) <= r.tolerance : null, replaces: def.replaces || null };
  });
}

/**
 * The numbers the verified ground and seat measurements replace: { fm: { name: { v, ref } }, seat: { eye, reach, ... }, records }.
 * Several verified records of one thing give their mean.
 */
export function measuredNumbers(doc) {
  const by = {};
  for (const r of counted(doc, false)) if (SURVEY[r.parameter].kind !== 'flight') (by[r.parameter] = by[r.parameter] || []).push(r);
  const value = (k) => (by[k] ? mean(by[k].map((r) => r.value)) : null), ref = (k) => `survey: ${by[k].map((r) => r.id).join(', ')}`;
  const fm = {}, seat = {};
  if (by.elevator_up_deg) fm.elevatorUpDeg = { v: value('elevator_up_deg'), ref: ref('elevator_up_deg') };
  if (by.elevator_down_deg) fm.elevatorDownDeg = { v: value('elevator_down_deg'), ref: ref('elevator_down_deg') };
  if (by.flap_time_s) fm.flapRateDegS = { v: 40 / value('flap_time_s'), ref: ref('flap_time_s') };
  if (by.eye_to_panel_in || by.eye_left_of_centreline_in || by.eye_above_floor_in) {
    const z = by.eye_to_panel_in ? CABIN.panelFaceZ - value('eye_to_panel_in') * IN : EYE0[2];
    seat.eye = [by.eye_left_of_centreline_in ? value('eye_left_of_centreline_in') * IN : EYE0[0], by.eye_above_floor_in ? floorAt(z) + value('eye_above_floor_in') * IN : EYE0[1], z];
  }
  if (by.arm_reach_in) seat.reach = value('arm_reach_in') * IN;
  if (by.shoulder_below_eye_in) seat.shoulderBelow = value('shoulder_below_eye_in') * IN;
  if (by.shoulder_width_in) seat.shoulderAside = (value('shoulder_width_in') * IN) / 2;
  return { fm, seat, records: Object.values(by).flat().map((r) => r.id) };
}

/** Apply a survey to the flight model and the seat. An unsound survey is refused whole. Returns what became measured. */
export function applySurvey(doc) {
  const errors = validateSurvey(doc);
  if (errors.length) throw new Error(`the survey is not sound: ${errors[0]}${errors.length > 1 ? ` (and ${errors.length - 1} more)` : ''}`);
  const m = measuredNumbers(doc);
  return { flight: F.applyMeasured(m.fm), seat: applyMeasuredSeat(m.seat), records: m.records };
}

/** Back to the model as it was built. */
export function resetSurvey() { F.resetMeasured(); resetMeasuredSeat(); }

// ---------------------------------------------------------------------------------------------- the sheet to fill in
/** Rows of the sheet to fill in: one for each thing to measure on the ground and in the seat, and the flight tests worth flying. */
export function templateRows() {
  const rows = [];
  const row = (id, parameter, c = {}) => rows.push({ id, parameter, value: '', unit: SURVEY[parameter].unit, tolerance: '', ...Object.fromEntries(Object.keys(CONDITIONS).map((k) => [k, c[k] ?? ''])), method: '', recorded_at: '', recorded_by: '', verification_status: 'raw', notes: '' });
  for (const [p, def] of Object.entries(SURVEY)) if (def.kind !== 'flight') row(p.replace(/_/g, '-'), p);
  row('static-rpm', 'static_rpm');
  for (const flap of [0, 10, 40]) { row(`stall-flaps-${flap}`, 'stall_kias', { flap_deg: flap }); row(`stall-warning-flaps-${flap}`, 'stall_warning_kias', { flap_deg: flap }); }
  for (const [alt, kias] of [[2000, 72], [6000, 70], [10000, 68]]) row(`climb-${alt}`, 'climb_fpm', { pressure_altitude_ft: alt, kias });
  for (const [alt, rpm] of [[4000, 2500], [4000, 2300], [8000, 2500], [8000, 2300]]) row(`cruise-${alt}-${rpm}`, 'cruise_kias', { pressure_altitude_ft: alt, rpm });
  row('glide-65-flaps-up', 'glide_sink_fpm', { kias: 65, flap_deg: 0 }); row('glide-60-flaps-40', 'glide_sink_fpm', { kias: 60, flap_deg: 40 });
  row('takeoff-roll', 'takeoff_roll_ft'); row('landing-roll', 'landing_roll_ft');
  return rows;
}

const quote = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
export function toCsv(rows) { return `${[COLUMNS.join(','), ...rows.map((r) => COLUMNS.map((c) => quote(r[c] ?? '')).join(','))].join('\n')}\n`; }

/** Read a filled sheet: rows without a value were not measured and are left out. Returns the records. */
export function fromCsv(text) {
  const lines = []; let cell = '', line = [], quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) { if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (ch === '"') quoted = false; else cell += ch; }
    else if (ch === '"') quoted = true;
    else if (ch === ',') { line.push(cell); cell = ''; }
    else if (ch === '\n' || ch === '\r') { if (ch === '\r' && text[i + 1] === '\n') i++; line.push(cell); cell = ''; if (line.some((c) => c !== '')) lines.push(line); line = []; }
    else cell += ch;
  }
  if (cell !== '' || line.length) { line.push(cell); if (line.some((c) => c !== '')) lines.push(line); }
  if (!lines.length) return [];
  const head = lines[0].map((h) => h.trim());
  for (const c of ['id', 'parameter', 'value', 'unit']) if (!head.includes(c)) throw new Error(`the sheet has no "${c}" column`);
  const records = [];
  for (const cells of lines.slice(1)) {
    const raw = Object.fromEntries(head.map((h, i) => [h, (cells[i] ?? '').trim()]));
    if (raw.value === '') continue;
    const num = (v) => (v === '' ? NaN : Number(v));
    const c = {};
    for (const k of Object.keys(CONDITIONS)) if (raw[k] !== undefined && raw[k] !== '') c[k] = num(raw[k]);
    records.push({ id: raw.id, parameter: raw.parameter, value: num(raw.value), unit: raw.unit, tolerance: num(raw.tolerance), conditions: c, method: raw.method || '', recorded_at: raw.recorded_at || '', recorded_by: raw.recorded_by || '',
      verification_status: raw.verification_status || 'raw', notes: raw.notes || '' });
  }
  return records;
}
