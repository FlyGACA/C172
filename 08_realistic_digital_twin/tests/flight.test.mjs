// The flight model against the Pilot's Operating Handbook (Cessna Model 172N, 1978).
// Run: node --test 08_realistic_digital_twin/tests/flight.test.mjs
//
// Each test names the handbook page it checks and the tolerance it allows. The tolerances are the claim the
// model makes: inside them it reproduces the handbook; it makes no claim of certified fidelity.
import test from 'node:test';
import assert from 'node:assert/strict';
import * as F from '../js/flight.js';
import { createPilot, pilotStep, flyTakeoff, flyLanding } from '../js/pilot.js';
import { createState, step } from '../js/sim.js';
import { createDeck, stepDeck, deckInFlight, deckOnGround } from '../js/flightdeck.js';

const KT = 0.514444;
const near = (value, want, tol, what) => assert.ok(Math.abs(value - want) <= tol, `${what}: ${value.toFixed(2)} is not within ${tol} of ${want}`);
const within = (value, want, fraction, what) => assert.ok(Math.abs(value / want - 1) <= fraction, `${what}: ${value.toFixed(0)} is not within ${fraction * 100} % of ${want}`);
const isaDev = (altFt, tempC) => tempC - (15 - 0.0019812 * altFt);

// ------------------------------------------------------------------------------------------ provenance
test('every number of the model says where it comes from', () => {
  const rows = F.coefficientTable();
  assert.ok(rows.length > 70);
  for (const r of rows) {
    assert.ok(['poh', 'derived', 'estimated'].includes(r.source), `${r.name}: source ${r.source}`);
    assert.ok(r.note && r.note.length > 10, `${r.name}: a note`);
    if (r.source !== 'estimated') assert.match(r.ref, /^p\.\d/, `${r.name}: ${r.source} needs a handbook page`);
    else assert.equal(r.ref, '', `${r.name}: an estimate cites no page`);
  }
  const count = (s) => rows.filter((r) => r.source === s).length;
  assert.ok(count('poh') >= 10 && count('derived') >= 12, `poh ${count('poh')}, derived ${count('derived')}`);
});

test('numbers read from the handbook (p.1-2, 1-3, 1-5, 2-5, 2-7)', () => {
  near(F.FM.wingSpan.v / 0.3048, 36, 1e-9, 'span, ft');
  near(F.FM.propDiameter.v / 0.0254, 75, 1e-9, 'propeller, in');
  near(F.FM.ratedPower.v / 745.69987, 160, 1e-9, 'rated power, hp');
  near(F.FM.wingArea.v / 0.3048 ** 2, 2300 / 13.2, 0.3, 'wing area from the wing loading, sq ft');
  near(F.cgStation(2300, 0), 38.5, 1e-9, 'forward limit at 2300 lb');
  near(F.cgStation(1950, 0), 35.0, 1e-9, 'forward limit at 1950 lb');
  near(F.cgStation(1600, 0), 35.0, 1e-9, 'forward limit below 1950 lb');
  near(F.cgStation(2125, 0), 36.75, 1e-9, 'straight line between');
  near(F.cgStation(2300, 1), 47.3, 1e-9, 'aft limit');
});

test('airspeed calibration is the table of Figure 5-1 (p.5-8)', () => {
  for (const [flap, table] of Object.entries(F.AIRSPEED_CALIBRATION)) {
    for (const [kias, kcas] of table) {
      near(F.kcasFromKias(kias, Number(flap)), kcas, 1e-9, `flaps ${flap}: ${kias} KIAS`);
      near(F.kiasFromKcas(kcas, Number(flap)), kias, 1e-9, `flaps ${flap}: ${kcas} KCAS`);
    }
  }
  near(F.kcasFromKias(52, 0), 56.4, 0.01, 'lift-off speed, calibrated');
  near(F.kiasFromKcas(F.kcasFromKias(73, 0), 0), 73, 1e-9, 'round trip');
});

// ------------------------------------------------------------------------------------------ stall speeds
test('stall speeds are those of Figure 5-3 (p.5-11) within 1 KCAS at every bank angle', () => {
  const table = {      // [flaps, cg]: KCAS at 0, 30, 45, 60 degrees of bank
    '0 aft': [50, 54, 59, 71], '10 aft': [47, 51, 56, 66], '40 aft': [44, 47, 52, 62],
    '0 fwd': [53, 57, 63, 75], '10 fwd': [51, 55, 61, 72], '40 fwd': [47, 51, 56, 66],
  };
  for (const [key, row] of Object.entries(table)) {
    const [flap, cg] = key.split(' ');
    [0, 30, 45, 60].forEach((bank, i) => near(F.stallSpeedKcas({ flapDeg: Number(flap), cgFrac: cg === 'aft' ? 1 : 0, bankDeg: bank }), row[i], 1.0, `flaps ${key}, bank ${bank}`));
  }
  // the lift curve really tops out there: steady flight is possible just above and not below
  for (const [flap, cg, vs] of [[0, 1, 50], [40, 0, 47]]) {
    assert.equal(F.trim({ kcas: vs + 0.5, flapDeg: flap, cgFrac: cg, engineOn: false }).stalled, false);
    assert.equal(F.trim({ kcas: vs - 0.5, flapDeg: flap, cgFrac: cg, engineOn: false }).stalled, true);
  }
});

// ------------------------------------------------------------------------------------------ engine and propeller
test('static RPM at full throttle is in the handbook range 2280 to 2400 (p.2-5)', () => {
  const rpm = F.equilibriumRpm(F.engineAt(1, 1), 0, 1);
  assert.ok(rpm >= 2280 && rpm <= 2400, `static ${rpm.toFixed(0)} RPM`);
  const idle = F.equilibriumRpm(F.engineAt(0, 1), 0, 1);
  assert.ok(idle > 600 && idle < 850, `idle ${idle.toFixed(0)} RPM`);
  // the propeller never gives more than the engine puts in
  for (let J = 0.05; J < 0.97; J += 0.05) assert.ok((J * F.propCt(J)) / F.propCp(J) < 0.86, `efficiency at J ${J.toFixed(2)}`);
});

const climbAt = (kias, altFt, tempC = null) => {
  const dev = tempC == null ? 0 : isaDev(altFt, tempC);
  return F.trim({ kcas: F.kcasFromKias(kias), altFt, isaDevC: dev, torque: F.fullThrottleTorque(F.chargeAt(altFt, dev)) }).climbFpm;
};

test('rate of climb at standard temperature is Figure 5-6 (p.5-15) within 25 ft/min from sea level to 12,000 ft', () => {
  const table = [[0, 73, 770], [1000, 73, 725], [2000, 72, 675], [3000, 72, 630], [4000, 71, 580], [5000, 71, 535], [6000, 70, 485], [7000, 69, 440], [8000, 69, 390],
    [9000, 68, 345], [10000, 68, 295], [11000, 67, 250], [12000, 67, 200]];
  for (const [alt, kias, fpm] of table) near(climbAt(kias, alt), fpm, 25, `climb at ${alt} ft`);
});

test('rate of climb at -20, 0, 20 and 40 °C is Figure 5-5 (p.5-14) within 45 ft/min', () => {
  const table = { 0: [73, 875, 815, 755, 695], 2000: [72, 765, 705, 650, 590], 4000: [71, 655, 600, 545, 485], 6000: [70, 545, 495, 440, 385], 8000: [69, 440, 390, 335, 280],
    10000: [68, 335, 285, 230, null], 12000: [67, 230, 180, null, null] };
  for (const [alt, row] of Object.entries(table)) {
    [-20, 0, 20, 40].forEach((tc, i) => { if (row[i + 1] != null) near(climbAt(row[0], Number(alt), tc), row[i + 1], 45, `climb at ${alt} ft, ${tc} °C`); });
  }
});

test('the best rate, best angle and best glide speeds fall where the handbook puts them', () => {
  const best = (fn, lo, hi) => { let b = [0, -1e9]; for (let k = lo; k <= hi; k += 0.5) { const v = fn(k); if (v > b[1]) b = [k, v]; } return b[0]; };
  near(best((k) => climbAt(k, 0), 55, 95), 73, 5, 'best rate of climb speed at sea level, KIAS (p.5-15: 73)');
  near(best((k) => climbAt(k, 10000), 55, 95), 68, 4, 'best rate of climb speed at 10,000 ft, KIAS (p.5-15: 68)');
  const angle = (k) => F.trim({ kcas: F.kcasFromKias(k), altFt: 0, torque: F.fullThrottleTorque(1) }).gamma;
  near(best(angle, 45, 90), 59, 4, 'best angle of climb speed at sea level, KIAS (p.4-3: 59)');
  const glide = (k) => { const t = F.trim({ kcas: F.kcasFromKias(k), altFt: 5000, engineOn: false }); return 1 / Math.tan(-t.gamma); };
  assert.ok(glide(65) > 0.98 * glide(best(glide, 50, 90)), 'the glide at 65 KIAS is within 2 % of the best the model has');
});

test('cruise is Figure 5-7 (p.5-16): true airspeed within 3 knots and power within 2.5 points on every line the engine can reach; at and above 8000 ft its full throttle is up to 7.5 knots short of the fastest lines', () => {
  const table = {      // altitude: [RPM, % BHP, KTAS] at standard temperature
    2000: [[2500, 75, 116], [2400, 67, 111], [2300, 60, 105], [2200, 53, 100], [2100, 47, 94]],
    4000: [[2550, 75, 118], [2500, 71, 115], [2400, 64, 110], [2300, 57, 105], [2200, 51, 99], [2100, 46, 93]],
    6000: [[2600, 75, 120], [2500, 67, 115], [2400, 60, 109], [2300, 54, 104], [2200, 49, 98], [2100, 44, 92]],
    8000: [[2650, 75, 122], [2600, 71, 120], [2500, 64, 114], [2400, 58, 109], [2300, 52, 103], [2200, 47, 97]],
    10000: [[2650, 71, 122], [2600, 68, 119], [2500, 61, 114], [2400, 55, 108], [2300, 50, 102], [2200, 45, 96]],
    12000: [[2600, 64, 118], [2500, 58, 113], [2400, 53, 107], [2300, 48, 101], [2200, 44, 95]],
  };
  let lines = 0, beyond = 0;
  for (const [altText, rows] of Object.entries(table)) {
    const alt = Number(altText);
    const full = F.fullThrottleTorque(F.chargeAt(alt));
    // level flight at full throttle: the fastest the model cruises at this altitude
    let lo = 60, hi = 140;
    for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (F.trim({ kcas: mid, altFt: alt }).torque < full) lo = mid; else hi = mid; }
    const top = F.trim({ kcas: lo, altFt: alt });
    for (const [rpm, pct, ktas] of rows) {
      lo = 60; hi = 140;                                                   // the level speed that turns this RPM
      for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (F.trim({ kcas: mid, altFt: alt }).rpm < rpm) lo = mid; else hi = mid; }
      const t = F.trim({ kcas: lo, altFt: alt });
      if (t.torque <= full) {
        lines++;
        near(t.tas / KT, ktas, 3, `${alt} ft, ${rpm} RPM: KTAS`);
        near((t.power / F.FM.ratedPower.v) * 100, pct, 2.5, `${alt} ft, ${rpm} RPM: % BHP`);
      } else {
        // The handbook's line asks more than the model's full throttle. The engine law is fitted to the climb table,
        // and the climb and cruise tables do not agree on the power left at altitude: this is the known departure.
        beyond++;
        assert.ok(alt >= 8000, `${alt} ft, ${rpm} RPM is out of reach`);
        assert.ok(top.tas / KT > ktas - 7.5 && top.tas / KT < ktas, `${alt} ft: full throttle gives ${(top.tas / KT).toFixed(1)} KTAS, the handbook's ${rpm} RPM line ${ktas}`);
        assert.ok(top.rpm > rpm - 125, `${alt} ft: full throttle turns ${top.rpm.toFixed(0)} RPM, the handbook line ${rpm}`);
      }
    }
  }
  assert.ok(lines >= 26 && beyond <= 8, `${lines} lines flown, ${beyond} beyond full throttle`);
});

test('maximum glide is about 9.1 to 1 at 65 KIAS with the propeller windmilling (p.3-11)', () => {
  const t = F.trim({ kcas: F.kcasFromKias(65), altFt: 6000, engineOn: false });
  near(1 / Math.tan(-t.gamma), 9.1, 0.1, 'glide ratio');
  // flown, not only trimmed: 60 seconds of glide lose the height the ratio says
  const f = F.createFlight({ inFlight: { kias: 65, altFt: 6000, engineOn: false } });
  const p = createPilot(), start = [f.north, f.alt];
  for (let i = 0; i < 60 * 60; i++) F.stepFlight(f, { ...pilotStep(p, f, { kias: 65, bankDeg: 0 }, 1 / 60), trim: f.trimmed.trim, engineOn: false }, 1 / 60);
  near((f.north - start[0]) / (start[1] - f.alt), 9.1, 0.35, 'glide ratio flown for a minute');
  assert.ok(f.rpm > 900 && f.rpm < 1400, `windmilling at ${f.rpm.toFixed(0)} RPM`);
});

// ------------------------------------------------------------------------------------------ field performance
test('short-field takeoff distances are Figure 5-4 (p.5-12, 5-13): ground roll within 12 %, total over 50 ft within 14 %', () => {
  const rows = [      // field elevation, °C, weight, [ground roll, total], speeds
    [0, 0, 2300, [720, 1300]], [0, 20, 2300, [835, 1490]], [0, 40, 2300, [960, 1700]], [2000, 20, 2300, [1000, 1790]], [4000, 20, 2300, [1210, 2175]], [8000, 20, 2300, [1805, 3375]],
    [0, 20, 2100, [680, 1220], { rotateKias: 44, v50: 56 }], [0, 20, 1900, [540, 985], { rotateKias: 42, v50: 54 }],
  ];
  for (const [elev, tc, weight, [roll, total], o = {}] of rows) {
    const f = F.createFlight({ fieldElevFt: elev, isaDevC: isaDev(elev, tc), weightLb: weight });
    const r = flyTakeoff(f, o);
    within(r.groundRollFt, roll, 0.12, `takeoff ground roll, ${elev} ft ${tc} °C ${weight} lb`);
    within(r.totalFt, total, 0.14, `takeoff over 50 ft, ${elev} ft ${tc} °C ${weight} lb`);
    if (weight === 2300 && elev === 0) {
      within(r.groundRollFt, roll, 0.08, `takeoff ground roll at sea level, ${tc} °C`);
      within(r.totalFt, total, 0.09, `takeoff over 50 ft at sea level, ${tc} °C`);
      near(r.liftOffKias, 52, 2, 'lift-off speed, KIAS');
      near(r.kiasAt50, 59, 2.5, 'speed at 50 ft, KIAS');
    }
  }
});

test('short-field landing distances are Figure 5-10 (p.5-21): ground roll within 5 %, total over 50 ft within 7 %', () => {
  for (const [elev, tc, roll, total] of [[0, 0, 495, 1205], [0, 20, 530, 1265], [0, 40, 565, 1330], [4000, 20, 615, 1410], [8000, 20, 710, 1580]]) {
    const f = F.createFlight({ fieldElevFt: elev, isaDevC: isaDev(elev, tc) });
    const r = flyLanding(f);
    within(r.groundRollFt, roll, 0.05, `landing ground roll, ${elev} ft ${tc} °C`);
    within(r.totalFt, total, 0.07, `landing over 50 ft, ${elev} ft ${tc} °C`);
    assert.ok(r.touchdownFpm > -200, `touched down at ${r.touchdownFpm.toFixed(0)} ft/min`);
    assert.ok(r.touchdownKias > 40 && r.touchdownKias < 50, `touched down at ${r.touchdownKias.toFixed(1)} KIAS`);
  }
});

// ------------------------------------------------------------------------------------------ the stall, flown
/** Power-off stall: hold the altitude at idle until the wing stalls, hold the wheel back, then recover. */
function flyStall({ cg = 0.5, flap = 0, hold = 6, altFt = 3000, entryKias = 70 }) {
  const f = F.createFlight({ cgFrac: cg, inFlight: { kias: entryKias, altFt, flapDeg: flap } });
  const p = createPilot(), dt = 1 / 60, charge = F.chargeAt(altFt);
  const r = { maxAlpha: 0 };
  let phase = 'entry', tStall = 0, tRecover = 0, lowest = 1e9;
  while (f.t < 150) {
    let target, engine = F.engineAt(0, charge);
    if (phase === 'entry') target = { altFt, bankDeg: 0, maxPitchDeg: 30 };
    else if (phase === 'hold') target = { elevator: 1, bankDeg: 0 };
    else { engine = F.engineAt(1, charge); target = f.out.kias < 58 ? { pitchDeg: -3, bankDeg: 0 } : { pitchDeg: 6, bankDeg: 0 }; }
    F.stepFlight(f, { ...pilotStep(p, f, target, dt), trim: f.trimmed.trim, engineOn: true, engine, flapCommandDeg: flap }, dt);
    const o = f.out;
    if (r.warningKcas == null && o.stallWarning) r.warningKcas = o.kcas;
    if (phase === 'entry' && o.stalled) { phase = 'hold'; tStall = f.t; Object.assign(r, { stallKcas: o.kcas, stallKias: o.kias, loadFactor: o.loadFactor, pitchAtStall: o.pitchDeg, altAtStall: o.altFt }); }
    if (phase === 'hold') {
      r.maxAlpha = Math.max(r.maxAlpha, o.alphaDeg);
      r.lowestPitch = Math.min(r.lowestPitch ?? 99, o.pitchDeg);
      if (f.t - tStall > hold) { phase = 'recover'; tRecover = f.t; r.heldLossFt = r.altAtStall - o.altFt; r.altAtRecovery = o.altFt; r.alphaHeld = o.alphaDeg; r.sinkHeld = o.vsFpm; }
    }
    if (phase === 'recover') {
      lowest = Math.min(lowest, o.altFt);
      if (f.t - tRecover > 2 && o.vsFpm > 0 && !o.stalled) { r.recoveryLossFt = r.altAtRecovery - lowest; r.recoverySeconds = f.t - tRecover; r.alphaStall = o.alphaStallDeg; return r; }
    }
  }
  return r;
}

test('a power-off stall flown at 1 g comes at the handbook speed, with the horn 5 to 10 knots before (p.5-11, p.7-34)', () => {
  for (const [cg, flap, poh] of [[1, 0, 50], [0, 0, 53], [0.5, 0, 51.5], [1, 40, 44], [0, 40, 47]]) {
    const r = flyStall({ cg, flap, hold: 1, entryKias: flap ? 65 : 70 });
    assert.ok(r.stallKcas, `cg ${cg} flaps ${flap}: it stalls`);
    // the entry is not exactly 1 g: bring the speed to 1 g before comparing
    near(r.stallKcas / Math.sqrt(r.loadFactor), poh, 1.5, `stall speed, cg ${cg} flaps ${flap}, KCAS at 1 g`);
    const margin = r.warningKcas - r.stallKcas;
    assert.ok(margin >= 5 && margin <= 10, `cg ${cg} flaps ${flap}: horn ${margin.toFixed(1)} knots before the stall`);
  }
});

test('at the stall the nose drops with the wheel held back, and the recovery loses less than the 180 ft of the handbook (p.5-11)', () => {
  for (const cg of [0, 0.5, 1]) {
    const r = flyStall({ cg, hold: 6 });
    assert.ok(r.pitchAtStall - r.lowestPitch > 4, `cg ${cg}: the nose drops ${(r.pitchAtStall - r.lowestPitch).toFixed(1)} degrees`);
    assert.ok(r.sinkHeld < -250, `cg ${cg}: held in the stall it sinks ${r.sinkHeld.toFixed(0)} ft/min`);
    assert.ok(r.recoveryLossFt < 180, `cg ${cg}: recovery lost ${r.recoveryLossFt.toFixed(0)} ft`);
    assert.ok(r.recoverySeconds < 12, `cg ${cg}: recovered in ${r.recoverySeconds.toFixed(1)} s`);
  }
  // the further aft the centre of gravity, the deeper the wheel takes the aircraft into the stall
  const fwd = flyStall({ cg: 0, hold: 6 }), aft = flyStall({ cg: 1, hold: 6 });
  assert.ok(aft.maxAlpha > fwd.maxAlpha + 5, `aft ${aft.maxAlpha.toFixed(1)}, forward ${fwd.maxAlpha.toFixed(1)} degrees`);
  assert.ok(fwd.alphaHeld < fwd.alphaStall + 2.5, 'at the forward limit the elevator holds the aircraft barely beyond the stall');
  // one recovery at once, as it is taught: wheel forward, full throttle
  const prompt = flyStall({ cg: 0.5, hold: 0.5 });
  assert.ok(prompt.recoveryLossFt < 150, `recovery at once lost ${prompt.recoveryLossFt.toFixed(0)} ft`);
});

// ------------------------------------------------------------------------------------------ trim, flaps, power
/** Elevator free at a trim setting; the scripted pilot only keeps the wings level and the ball centred. */
function handsOff(start, change, seconds) {
  const f = F.createFlight({ inFlight: start, ...start });
  const tr = f.trimmed, p = createPilot(), dt = 1 / 60;
  const base = { elevator: 0, trim: tr.trim, engineOn: true, engine: start.engine ?? tr.torque, flapCommandDeg: f.flapDeg };
  let sum = 0, n = 0, low = 1e9, high = 0;
  while (f.t < seconds) {
    const c = pilotStep(p, f, { elevator: 0, bankDeg: 0 }, dt);
    F.stepFlight(f, { ...base, aileron: c.aileron, rudder: c.rudder, ...change(f.t, tr) }, dt);
    if (f.t > 6) { low = Math.min(low, f.out.kias); high = Math.max(high, f.out.kias); }
    if (f.t > seconds - 50) { sum += f.out.kias; n++; }
  }
  return { f, tr, mean: sum / n, low, high };
}

test('trimmed, the aircraft flies on hands off; the trim wheel changes the speed it seeks', () => {
  // really hands off, at the speed the airframe is rigged for: two minutes without a hand or a foot
  const f = F.createFlight({ inFlight: { kias: 100, altFt: 3000 } });
  for (let i = 0; i < 120 * 60; i++) F.stepFlight(f, { elevator: 0, trim: f.trimmed.trim, engineOn: true, engine: f.trimmed.torque }, 1 / 60);
  near(f.out.kias, 100, 1, 'speed after two minutes');
  near(f.out.altFt, 3000, 30, 'altitude after two minutes');
  near(f.out.bankDeg, 0, 5, 'bank after two minutes');
  // nose-up trim: slower. Nose-down trim: faster. About five knots for a twentieth of the wheel's travel.
  const up = handsOff({ kias: 90, altFt: 3000 }, (t, tr) => (t > 5 ? { trim: tr.trim + 0.05 } : {}), 240);
  const down = handsOff({ kias: 90, altFt: 3000 }, (t, tr) => (t > 5 ? { trim: tr.trim - 0.05 } : {}), 240);
  assert.ok(up.mean < 87 && up.mean > 78, `nose-up trim: ${up.mean.toFixed(1)} KIAS`);
  assert.ok(down.mean > 93 && down.mean < 102, `nose-down trim: ${down.mean.toFixed(1)} KIAS`);
  // the trim covers the speed range at both ends of the centre of gravity range
  for (const cg of [0, 1]) for (const kias of [65, 120]) assert.ok(Math.abs(F.trim({ kcas: F.kcasFromKias(kias), altFt: 3000, cgFrac: cg }).trim) < 0.95, `cg ${cg}, ${kias} KIAS can be trimmed`);
  // a forward centre of gravity needs more nose-up trim than an aft one
  assert.ok(F.trim({ kcas: 80, altFt: 3000, cgFrac: 0 }).trim > F.trim({ kcas: 80, altFt: 3000, cgFrac: 1 }).trim + 0.2);
});

test('the long exchange of speed and height is slow and lightly damped', () => {
  const r = handsOff({ kias: 90, altFt: 3000 }, (t, tr) => (t > 5 && t < 9 ? { elevator: 0.15 } : {}), 200);
  assert.ok(r.low < 86 && r.high > 93, `the speed swings ${r.low.toFixed(1)} to ${r.high.toFixed(1)} KIAS`);
  near(r.f.out.kias, 90, 2.5, 'and it comes back to the trimmed speed');
});

test('lowering the flaps at a fixed trim and throttle balloons, then slows the aircraft (p.7-10)', () => {
  const settled = {};
  for (const flap of [10, 20, 30, 40]) {
    const r = handsOff({ kias: 80, altFt: 3000 }, (t) => (t > 5 ? { flapCommandDeg: flap } : {}), 300);
    settled[flap] = r.mean;
    assert.ok(r.low > 44, `flaps ${flap}: the balloon stops at ${r.low.toFixed(1)} KIAS, above the stall`);
    assert.ok(r.f.out.vsFpm < 0, `flaps ${flap}: more drag, the aircraft descends`);
  }
  near(settled[10], 73, 3, 'flaps 10: speed sought, KIAS');
  near(settled[20], 68, 3, 'flaps 20');
  near(settled[30], 64, 3, 'flaps 30');
  near(settled[40], 61, 3, 'flaps 40');
  // the flaps travel at the speed of their motor
  const f = F.createFlight({ inFlight: { kias: 80, altFt: 3000 } });
  for (let i = 0; i < 120; i++) F.stepFlight(f, { trim: f.trimmed.trim, engineOn: true, engine: f.trimmed.torque, flapCommandDeg: 40 }, 1 / 60);
  near(f.flapDeg, 2 * F.FM.flapRateDegS.v, 0.2, 'flap angle after two seconds');
});

test('power: more makes the aircraft climb at a lower speed, less makes it descend at a higher one', () => {
  const more = handsOff({ kias: 90, altFt: 3000 }, (t) => (t > 5 ? { engine: F.engineAt(1, F.chargeAt(3000)) } : {}), 240);
  assert.ok(more.f.out.altFt > 4500, `full throttle: ${more.f.out.altFt.toFixed(0)} ft after four minutes`);
  assert.ok(more.mean < 88 && more.mean > 72, `full throttle: ${more.mean.toFixed(1)} KIAS`);
  const less = handsOff({ kias: 90, altFt: 6000 }, (t) => (t > 5 ? { engine: F.engineAt(0, F.chargeAt(5000)) } : {}), 240);
  assert.ok(less.f.out.altFt < 4500, `idle: ${less.f.out.altFt.toFixed(0)} ft after four minutes`);
  assert.ok(less.mean > 90 && less.mean < 104, `idle: ${less.mean.toFixed(1)} KIAS`);
  // the go-around: full throttle from an approach with full flaps pitches the nose up hard (p.4-9: flaps to 20 at once)
  const go = handsOff({ kias: 60, altFt: 1000, flapDeg: 40, climbFpm: -500 }, (t) => (t > 5 ? { engine: F.engineAt(1, F.chargeAt(1000)) } : {}), 30);
  assert.ok(go.low < 50, `hands off, the speed falls to ${go.low.toFixed(1)} KIAS`);
});

test('the propeller turns the aircraft left: right rudder in the climb, a little left in the glide', () => {
  const climb = F.trim({ kcas: F.kcasFromKias(73), altFt: 0, torque: F.fullThrottleTorque(1) });
  assert.ok(climb.rudder > 0.06 && climb.rudder < 0.35, `climb: rudder ${climb.rudder.toFixed(2)}`);
  assert.ok(climb.aileron > 0.01, `climb: aileron ${climb.aileron.toFixed(3)} against the torque`);
  const cruise = F.trim({ kcas: F.FM.rigKcas.v, altFt: 3000 });
  near(cruise.rudder, 0, 0.005, 'no rudder at the rigged cruise');
  near(cruise.aileron, 0, 0.005, 'no aileron at the rigged cruise');
  const glide = F.trim({ kcas: F.kcasFromKias(65), altFt: 3000, engineOn: false });
  assert.ok(glide.rudder < -0.01, `glide: rudder ${glide.rudder.toFixed(3)}`);
  // flown with the feet on the floor and the wings held level: the ball sits to the right and the nose goes left
  const full = F.engineAt(1, F.chargeAt(1000));
  const f = F.createFlight({ inFlight: { kias: 73, altFt: 1000, engine: full } });
  const p = createPilot();
  for (let i = 0; i < 15 * 60; i++) F.stepFlight(f, { ...pilotStep(p, f, { elevator: 0, bankDeg: 0, rudder: 0 }, 1 / 60), trim: f.trimmed.trim, engineOn: true, engine: full }, 1 / 60);
  assert.ok(f.out.slip > 0.006, `ball ${f.out.slip.toFixed(4)} to the right`);
  assert.ok(f.out.headingDeg > 300 && f.out.headingDeg < 358, `heading ${f.out.headingDeg.toFixed(1)}: it turns left`);
  // hands off as well: the left wing goes down
  const g = F.createFlight({ inFlight: { kias: 73, altFt: 1000, engine: full } });
  for (let i = 0; i < 6 * 60; i++) F.stepFlight(g, { trim: g.trimmed.trim, engineOn: true, engine: full }, 1 / 60);
  assert.ok(g.out.bankDeg < -8, `hands and feet off for six seconds: bank ${g.out.bankDeg.toFixed(1)}`);
});

// ------------------------------------------------------------------------------------------ controls
test('the controls act the right way round, with their secondary effects', () => {
  const fly = (control, seconds = 2) => {
    const f = F.createFlight({ inFlight: { kias: 90, altFt: 3000 } });
    const tr = f.trimmed, base = { trim: tr.trim, aileron: tr.aileron, rudder: tr.rudder, engineOn: true, engine: tr.torque };
    for (let i = 0; i < seconds * 60; i++) F.stepFlight(f, { ...base, ...control(tr) }, 1 / 60);
    return f;
  };
  const right = fly((tr) => ({ aileron: tr.aileron + 0.3 }));
  assert.ok(right.out.bankDeg > 12, `right aileron rolls right: ${right.out.bankDeg.toFixed(1)}`);
  assert.ok(right.out.betaDeg > 0.5, 'and the nose lags behind: adverse yaw');
  assert.ok(fly((tr) => ({ aileron: tr.aileron - 0.3 })).out.bankDeg < -12, 'left aileron rolls left');
  const back = fly(() => ({ elevator: 0.2 }), 1);
  assert.ok(back.out.pitchDeg > 6 && back.out.loadFactor > 1.2, `wheel back: pitch ${back.out.pitchDeg.toFixed(1)}, ${back.out.loadFactor.toFixed(2)} g`);
  assert.ok(fly(() => ({ elevator: -0.2 }), 1).out.pitchDeg < 1, 'wheel forward lowers the nose');
  const pedal = fly((tr) => ({ rudder: tr.rudder + 0.5 }), 3);
  assert.ok(pedal.out.headingDeg > 3 && pedal.out.headingDeg < 60, `right rudder yaws right: heading ${pedal.out.headingDeg.toFixed(1)}`);
  assert.ok(pedal.out.bankDeg > 8, 'and rolls right after it');
  // the same with the wings held level: a skid to the right, the ball goes left
  const skid = F.createFlight({ inFlight: { kias: 90, altFt: 3000 } });
  const feet = createPilot();
  for (let i = 0; i < 8 * 60; i++) F.stepFlight(skid, { ...pilotStep(feet, skid, { elevator: 0, bankDeg: 0, rudder: 0.4 }, 1 / 60), trim: skid.trimmed.trim, engineOn: true, engine: skid.trimmed.torque }, 1 / 60);
  assert.ok(skid.out.slip < -0.015 && skid.out.betaDeg < -3, `ball ${skid.out.slip.toFixed(3)}, sideslip ${skid.out.betaDeg.toFixed(1)}`);
  // the elevator stays inside its stops whatever the trim
  for (const [e, t, want] of [[1, 1, -F.FM.elevatorUpDeg.v], [-1, -1, F.FM.elevatorDownDeg.v], [0, 0.5, -0.5 * F.FM.trimAuthorityDeg.v]]) {
    near((F.elevatorAngle({ elevator: e, trim: t }) * 180) / Math.PI, want, 1e-9, `elevator ${e}, trim ${t}`);
  }
});

test('a level turn: 30 degrees of bank turns about 7 degrees a second at 90 knots, with the ball in the middle', () => {
  const f = F.createFlight({ inFlight: { kias: 90, altFt: 3000 } });
  const p = createPilot();
  for (let i = 0; i < 40 * 60; i++) F.stepFlight(f, { ...pilotStep(p, f, { altFt: 3000, bankDeg: 30 }, 1 / 60), trim: f.trimmed.trim, engineOn: true, engine: f.trimmed.torque * 1.25 }, 1 / 60);
  near(f.out.bankDeg, 30, 1.5, 'bank');
  const expected = ((9.80665 * Math.tan(30 * Math.PI / 180)) / (f.out.ktas * KT)) * 180 / Math.PI;
  near(f.out.turnRateDps, expected, 0.5, 'turn rate, degrees a second');
  near(f.out.loadFactor, 1 / Math.cos(30 * Math.PI / 180), 0.05, 'load factor');
  near(f.out.slip, 0, 0.01, 'ball');
  near(f.out.altFt, 3000, 60, 'altitude');
});

// ------------------------------------------------------------------------------------------ on the ground
test('on the ground: it stands at its attitude on three wheels, the brakes hold full throttle, the pedals steer', () => {
  const f = F.createFlight();
  near(f.out.pitchDeg, F.FM.groundPitchDeg.v, 0.4, 'attitude at rest');
  assert.equal(f.out.wheels, 3);
  near(f.out.weightOnWheels, 2300 * 0.45359237 * 9.80665, 60, 'weight on the wheels, N');
  near(f.out.aglFt, 0, 0.3, 'wheels on the ground');
  const full = F.engineAt(1, 1);
  for (let i = 0; i < 6 * 120; i++) F.stepFlight(f, { brake: 1, engineOn: true, engine: full }, 1 / 120);
  near(Math.hypot(f.north, f.east), 0, 0.5, 'held by the brakes at full throttle, m');
  assert.ok(f.rpm > 2280 && f.rpm < 2400, `static ${f.rpm.toFixed(0)} RPM`);
  // taxi: a little power, right pedal turns right; the left brake turns left
  const taxi = (control) => {
    const g = F.createFlight();
    for (let i = 0; i < 12 * 120; i++) F.stepFlight(g, { engineOn: true, engine: F.engineAt(0.25, 1), ...control }, 1 / 120);
    return g;
  };
  const straight = taxi({});
  assert.ok(straight.out.groundSpeedKt > 4 && straight.out.groundSpeedKt < 25, `taxi at ${straight.out.groundSpeedKt.toFixed(1)} knots`);
  const turned = taxi({ rudder: 1 });
  assert.ok(turned.out.headingDeg > 15 && turned.out.headingDeg < 180, `right pedal: heading ${turned.out.headingDeg.toFixed(0)}`);
  const braked = taxi({ brakeLeft: 0.6 });
  assert.ok(braked.out.headingDeg > 200 && braked.out.headingDeg < 355, `left brake: heading ${braked.out.headingDeg.toFixed(0)}`);
  // closing the throttle and braking stops it
  const stop = taxi({});
  for (let i = 0; i < 10 * 120; i++) F.stepFlight(stop, { engineOn: true, engine: F.engineAt(0, 1), brake: 1 }, 1 / 120);
  near(stop.out.groundSpeedKt, 0, 0.05, 'stopped');
});

test('a steady wind carries the aircraft and shortens the takeoff', () => {
  const f = F.createFlight({ windFromDeg: 0, windKt: 20, inFlight: { kias: 100, altFt: 3000, headingDeg: 0 } });
  for (let i = 0; i < 20 * 60; i++) F.stepFlight(f, { trim: f.trimmed.trim, engineOn: true, engine: f.trimmed.torque }, 1 / 60);
  near(f.out.kias, 100, 0.5, 'airspeed with a headwind');
  near(f.out.groundSpeedKt, f.out.ktas - 20, 0.5, 'groundspeed with a headwind');
  const cross = F.createFlight({ windFromDeg: 90, windKt: 15, inFlight: { kias: 100, altFt: 3000, headingDeg: 0 } });
  for (let i = 0; i < 20 * 60; i++) F.stepFlight(cross, { trim: cross.trimmed.trim, engineOn: true, engine: cross.trimmed.torque }, 1 / 60);
  assert.ok(cross.east < -100, 'a wind from the right carries it left');
  near(cross.out.betaDeg, 0, 0.6, 'without sideslip');
  // the handbook's rule of thumb is a tenth less for each 9 knots of headwind (p.5-12); the physics gives more
  const calm = flyTakeoff(F.createFlight()), head = flyTakeoff(F.createFlight({ windFromDeg: 0, windKt: 9 }));
  const less = 1 - head.groundRollFt / calm.groundRollFt;
  assert.ok(less > 0.1 && less < 0.35, `9 knots of headwind: ground roll ${(less * 100).toFixed(0)} % shorter`);
});

test('the result does not depend on how the time is cut into steps', () => {
  const run = (dt) => {
    const f = F.createFlight({ inFlight: { kias: 90, altFt: 3000 } });
    const n = Math.round(20 / dt);
    for (let i = 0; i < n; i++) F.stepFlight(f, { trim: f.trimmed.trim, elevator: 0.05, aileron: f.trimmed.aileron + 0.02, rudder: f.trimmed.rudder, engineOn: true, engine: f.trimmed.torque }, dt);
    return f.out;
  };
  const a = run(1 / 120), b = run(1 / 30), c = run(0.1);
  near(b.altFt, a.altFt, 0.01, 'altitude, 30 against 120 steps a second');
  near(c.kias, a.kias, 0.01, 'speed, 10 against 120 steps a second');
  near(c.bankDeg, a.bankDeg, 0.01, 'bank');
});

// ------------------------------------------------------------------------------------------ with the systems
const warm = () => createState({ controls: { masterBat: true, masterAlt: true, ignition: 'BOTH', mixture: 1, throttle: 0, fuelSelector: 'BOTH' }, engine: { running: true, rpm: 700, oilTempF: 170, oilPress: 60 } });

test('with the systems simulation: its engine turns the propeller, the propeller sets the tachometer', () => {
  const deck = createDeck(warm());
  deckOnGround(deck);
  for (let i = 0; i < 8 * 60; i++) stepDeck(deck, { brake: 1 }, 1 / 60);
  assert.ok(deck.sim.ind.rpm > 600 && deck.sim.ind.rpm < 850, `idle ${deck.sim.ind.rpm.toFixed(0)} RPM`);
  deck.sim.controls.throttle = 1;
  for (let i = 0; i < 8 * 60; i++) stepDeck(deck, { brake: 1 }, 1 / 60);
  assert.ok(deck.sim.ind.rpm > 2280 && deck.sim.ind.rpm < 2400, `static ${deck.sim.ind.rpm.toFixed(0)} RPM at full throttle (p.2-5)`);
  near(deck.sim.ind.ias, 0, 1, 'airspeed indicator at rest');
  // in cruise the tachometer shows what the cruise table says for the speed (p.5-16: 2000 ft, 105 KTAS at 2300 RPM)
  const cruise = createDeck(warm());
  const tr = deckInFlight(cruise, { kias: 103, altFt: 2000 });
  const p = createPilot();
  for (let i = 0; i < 60 * 60; i++) stepDeck(cruise, pilotStep(p, cruise.flight, { altFt: 2000, bankDeg: 0 }, 1 / 60), 1 / 60);
  near(cruise.flight.out.ktas, 105, 2.5, 'cruise KTAS');
  near(cruise.sim.ind.rpm, 2300, 60, 'cruise RPM');
  near(cruise.sim.ind.rpm, tr.rpm, 60, 'the systems engine gives what the trim asked of the throttle');
  near(cruise.sim.ind.ias, cruise.flight.out.kias, 0.5, 'the airspeed indicator shows the indicated airspeed of the calibration');
  near(cruise.sim.ind.alt, 2000, 40, 'altimeter');
  assert.ok(Math.abs(cruise.sim.ind.vsi) < 80, `vertical speed indicator ${cruise.sim.ind.vsi.toFixed(0)}`);
  assert.equal(cruise.sim.ind.stallWarning, false);
});

test('with the systems simulation: a fault acts on the flight (fuel off stops the pull; a blocked pitot only misleads)', () => {
  const deck = createDeck(warm());
  deckInFlight(deck, { kias: 90, altFt: 4000 });
  const p = createPilot();
  const fly = (seconds, target) => { for (let i = 0; i < seconds * 60; i++) stepDeck(deck, pilotStep(p, deck.flight, target, 1 / 60), 1 / 60); };
  fly(10, { altFt: 4000, bankDeg: 0 });
  // pitot blocked, drain open: the indicator falls to zero; the aircraft flies on at the same speed
  deck.sim.faults.pitot = 'ram';
  fly(25, { altFt: 4000, bankDeg: 0 });
  assert.ok(deck.sim.ind.ias < 25, `indicated ${deck.sim.ind.ias.toFixed(0)}`);
  near(deck.flight.out.kias, 90, 4, 'true indicated-equivalent speed');
  deck.sim.faults.pitot = 'none';
  // fuel selector off: the bowl empties, the engine stops, the propeller windmills, the aircraft glides
  deck.sim.controls.fuelSelector = 'OFF';
  fly(40, { kias: 65, bankDeg: 0 });
  assert.equal(deck.sim.engine.running, false);
  assert.ok(deck.sim.ind.rpm > 800 && deck.sim.ind.rpm < 1500, `windmilling ${deck.sim.ind.rpm.toFixed(0)} RPM`);
  assert.ok(deck.flight.out.vsFpm < -500 && deck.flight.out.vsFpm > -1000, `gliding at ${deck.flight.out.vsFpm.toFixed(0)} ft/min`);
  near(deck.flight.out.kias, 65, 3, 'best glide speed held');
  // fuel back on: the windmilling propeller restarts the engine (p.3-4)
  deck.sim.controls.fuelSelector = 'BOTH';
  fly(15, { kias: 75, bankDeg: 0 });
  assert.equal(deck.sim.engine.running, true);
  // the stall warning reaches the systems side
  deck.sim.controls.throttle = 0;
  fly(40, { altFt: deck.flight.out.altFt, bankDeg: 0, maxPitchDeg: 25 });
  assert.equal(deck.sim.ind.stallWarning, true);
});

test('with the systems simulation: scenario flight is untouched when no flight model flies', () => {
  const s = createState({ flight: { onGround: false, iasTarget: 100, altTarget: 3000 }, controls: { masterBat: true } });
  step(s, 30);
  near(s.truth.ias, 100, 1, 'scenario airspeed');
  near(s.truth.alt, 3000, 5, 'scenario altitude');
  assert.equal(s.ind.slip, 0);
  assert.equal(s.ind.stallWarning, false);
});
