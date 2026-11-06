// Unit tests for the Phase 7 systems simulation. Run: node --test 07_kinematic_twin/tests/
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  POH, createState, step, evaluateMagCheck, annunciations, staticPressure, altitudeFromPressure,
  impactPressure, casFromImpact, alternateStaticKias,
} from '../js/sim.js';

const instruments = JSON.parse(readFileSync(new URL('../data/instruments.json', import.meta.url), 'utf8')).instruments;

/** POH p.4-7 "Starting Engine" flow, then settle on BOTH. */
function startEngine(s, { prime = 3 } = {}) {
  Object.assign(s.controls, { mixture: 1, carbHeat: 0, masterBat: true, masterAlt: true, throttle: 0.06, primeStrokes: prime });
  s.controls.ignition = 'START';
  for (let i = 0; i < 200 && !s.engine.running; i++) step(s, 0.05);
  s.controls.ignition = 'BOTH';
  step(s, 3);
  return s;
}
const settle = (s, sec = 12) => step(s, sec);
const rpm = (s) => s.engine.rpm;

test('ISA helpers round-trip', () => {
  assert.ok(Math.abs(staticPressure(0) - 29.92) < 1e-9);
  for (const h of [0, 3000, 7500, 12000]) assert.ok(Math.abs(altitudeFromPressure(staticPressure(h)) - h) < 2, `alt ${h}`);
  for (const v of [0, 45, 97, 128, 160]) assert.ok(Math.abs(casFromImpact(impactPressure(v)) - v) < 0.01, `ias ${v}`);
});

test('engine starts with the POH sequence and settles at idle on BOTH', () => {
  const s = startEngine(createState());
  assert.equal(s.engine.running, true);
  settle(s, 10);
  assert.ok(rpm(s) > 550 && rpm(s) < 900, `idle rpm ${rpm(s)}`);
  assert.ok(s.engine.oilPress > POH.oilPressMin, 'oil pressure rises after start (POH p.4-7 step 8)');
});

test('cold engine without priming is slow to start; over-priming floods and the POH clearing procedure works', () => {
  const s = createState();
  Object.assign(s.controls, { masterBat: true, throttle: 0.06, ignition: 'START' });
  step(s, 3);
  assert.equal(s.engine.running, false, 'no prime: no start within 3 s');
  const f = createState();
  Object.assign(f.controls, { masterBat: true, throttle: 0.06, primeStrokes: 12, ignition: 'START' });
  step(f, 4);
  assert.equal(f.engine.flooded, true);
  assert.equal(f.engine.running, false);
  Object.assign(f.controls, { mixture: 0, throttle: 1 }); // POH p.4-11: mixture idle cut-off, full throttle, crank
  step(f, 4);
  assert.equal(f.engine.flooded, false);
});

test('full-throttle static RPM is inside the POH 2280-2400 band (p.2-5)', () => {
  const s = startEngine(createState());
  s.controls.throttle = 1;
  settle(s);
  assert.ok(rpm(s) >= POH.staticRpm[0] && rpm(s) <= POH.staticRpm[1], `static rpm ${rpm(s)}`);
});

test('full carburetor heat at full throttle drops 100-225 RPM (p.7-19)', () => {
  const s = startEngine(createState());
  s.controls.throttle = 1;
  settle(s);
  const before = rpm(s);
  s.controls.carbHeat = 1;
  settle(s);
  const drop = before - rpm(s);
  assert.ok(drop >= POH.carbHeatFullThrottleDrop[0] && drop <= POH.carbHeatFullThrottleDrop[1], `drop ${drop}`);
});

function magCheck(s) {
  s.controls.throttle = 0.5;
  for (let i = 0; i < 40 && Math.abs(rpm(s) - 1700) > 10; i++) {
    s.controls.throttle += (1700 - rpm(s)) / 4000;
    settle(s, 4);
  }
  const both = rpm(s);
  s.controls.ignition = 'R'; settle(s, 6); const right = rpm(s);
  s.controls.ignition = 'BOTH'; settle(s, 6);
  s.controls.ignition = 'L'; settle(s, 6); const left = rpm(s);
  s.controls.ignition = 'BOTH'; settle(s, 6);
  return evaluateMagCheck({ both, right, left });
}

test('healthy magneto check at 1700 RPM passes the POH limits (p.4-7: <=125 drop, <=50 differential)', () => {
  const r = magCheck(startEngine(createState()));
  assert.equal(r.pass, true, JSON.stringify(r));
  assert.ok(r.dropL > 20 && r.dropR > 20);
});

test('a weak right magneto produces an excessive drop and fails the check', () => {
  const r = magCheck(startEngine(createState({ faults: { magneto: { L: 'ok', R: 'weak' } } })));
  assert.equal(r.pass, false);
  assert.ok(r.issues.includes('drop_right_exceeds_125'), JSON.stringify(r));
});

test('a dead left magneto: engine runs on BOTH (right only) but stops when L is selected', () => {
  const s = startEngine(createState({ faults: { magneto: { L: 'dead', R: 'ok' } } }));
  assert.equal(s.engine.running, true);
  s.controls.ignition = 'L';
  settle(s, 2);
  assert.equal(s.engine.running, false);
});

test('ungrounded P-lead: no drop on the other magneto and the engine keeps running with the key OFF (hot mag)', () => {
  const s = startEngine(createState({ faults: { magneto: { L: 'ok', R: 'ungrounded' } } }));
  const r = magCheck(s);
  assert.ok(r.issues.includes('no_drop_suspect_grounding'), JSON.stringify(r));
  s.controls.ignition = 'OFF';
  settle(s, 3);
  assert.equal(s.engine.running, true);
  assert.ok(annunciations(s).includes('hot_magneto'));
});

test('leaning at 7000 ft gives an RPM peak below full rich (POH p.4-16 technique)', () => {
  const s = startEngine(createState({ flight: { onGround: false, iasTarget: 105, altTarget: 7000 } }));
  s.controls.throttle = 1;
  settle(s, 15);
  const rich = rpm(s);
  let best = rich, bestM = 1;
  for (let m = 1; m >= 0.5; m -= 0.02) {
    s.controls.mixture = m; settle(s, 4);
    if (rpm(s) > best) { best = rpm(s); bestM = m; }
  }
  assert.ok(best - rich > 25, `peak gain ${best - rich}`);
  assert.ok(bestM < 1, 'peak is leaner than full rich');
  s.controls.mixture = 0.3; settle(s, 4);
  assert.equal(s.engine.running, false, 'idle cut-off / excessive lean stops the engine');
});

test('carburetor ice: gradual RPM loss, carb heat gives an initial drop then recovery (p.3-16)', () => {
  const s = startEngine(createState({ flight: { onGround: false, iasTarget: 95, altTarget: 3000 }, faults: { carbIce: true } }));
  s.controls.throttle = 0.6;
  settle(s, 5);
  const clean = rpm(s);
  settle(s, 90);
  const iced = rpm(s);
  assert.ok(clean - iced > 60, `ice loss ${clean - iced}`);
  s.controls.carbHeat = 1; s.controls.throttle = 1; // POH: full throttle, carb heat full out
  settle(s, 1.5);
  s.controls.throttle = 0.6;
  settle(s, 60);
  s.controls.carbHeat = 0;
  settle(s, 5);
  assert.ok(rpm(s) > iced + 40, `recovered ${rpm(s)} vs iced ${iced}`);
  assert.ok(s.engine.ice < 0.2);
});

test('fuel selector OFF starves the engine after the carburetor bowl empties', () => {
  const s = startEngine(createState());
  s.controls.throttle = 0.5;
  settle(s, 5);
  s.controls.fuelSelector = 'OFF';
  settle(s, 2);
  assert.equal(s.engine.running, true, 'bowl keeps it running briefly');
  settle(s, 30);
  assert.equal(s.engine.running, false);
});

test('running a tank to its unusable quantity stops the engine; selecting the other tank restarts it in flight', () => {
  const s = startEngine(createState({ flight: { onGround: false, iasTarget: 100, altTarget: 4000 }, fuel: { left: 1.62, right: 18 } }));
  s.controls.fuelSelector = 'LEFT';
  s.controls.throttle = 0.7;
  step(s, 120);
  assert.equal(s.engine.running, false);
  assert.ok(Math.abs(s.fuel.left - POH.fuelUnusablePerTank) < 1e-6, 'unusable fuel remains in the tank');
  s.controls.fuelSelector = 'RIGHT';
  step(s, 8);
  assert.equal(s.engine.running, true, 'windmilling engine restarts');
});

test('BOTH draws evenly from the two tanks', () => {
  const s = startEngine(createState({ flight: { onGround: false, iasTarget: 100, altTarget: 3000 } }));
  s.controls.throttle = 0.8;
  step(s, 600);
  assert.ok(Math.abs(s.fuel.left - s.fuel.right) < 0.01);
  assert.ok(s.fuel.left < 21.0);
});

test('alternator charges after start; POH light test (landing light on, ALT off) gives discharge + LOW VOLTAGE (p.7-26/7-27)', () => {
  const s = startEngine(createState({ flight: { onGround: false, iasTarget: 100, altTarget: 3000 } }));
  s.controls.avionics = true; s.controls.throttle = 0.7;
  settle(s, 10);
  assert.ok(s.ind.ammeter > 0, `charge ${s.ind.ammeter}`);
  assert.equal(s.elec.lowVoltage, false);
  s.controls.landingLight = true;
  settle(s, 2);
  assert.equal(s.elec.lowVoltage, false, 'alternator carries the landing light');
  s.controls.masterAlt = false;
  settle(s, 3);
  assert.ok(s.ind.ammeter < -5, `discharge ${s.ind.ammeter}`);
  assert.equal(s.elec.lowVoltage, true);
});

test('low RPM taxi with electrical load can light LOW VOLTAGE; it goes out at higher RPM (p.7-26 note)', () => {
  const s = startEngine(createState());
  Object.assign(s.controls, { avionics: true, landingLight: true, navLights: true, beacon: true, throttle: 0 });
  settle(s, 8);
  assert.equal(s.elec.lowVoltage, true);
  s.controls.throttle = 0.45;
  settle(s, 8);
  assert.equal(s.elec.lowVoltage, false);
});

test('over-voltage: ACU trips the alternator; recycling the master resets it but it trips again (p.3-9, p.7-26)', () => {
  const s = startEngine(createState({ faults: { alternator: 'overvoltage' }, flight: { onGround: false, iasTarget: 100, altTarget: 3000 } }));
  s.controls.throttle = 0.7;
  settle(s, 5);
  assert.equal(s.elec.acuTripped, true);
  assert.ok(s.ind.ammeter < 0);
  s.controls.masterBat = false; step(s, 0.5); s.controls.masterBat = true; step(s, 0.5);
  assert.equal(s.elec.acuTripped, false, 'reset by recycling the master');
  settle(s, 5);
  assert.equal(s.elec.acuTripped, true, 'persistent fault trips again');
});

test('suction is in the POH green arc at 1700 RPM and the gyros become unreliable after vacuum failure', () => {
  const s = startEngine(createState({ flight: { onGround: false, iasTarget: 100, altTarget: 3000, bank: 0 } }));
  s.controls.throttle = 0.6;
  settle(s, 120);
  assert.ok(s.ind.suction >= POH.suctionGreen[0] && s.ind.suction <= POH.suctionGreen[1], `suction ${s.ind.suction}`);
  assert.ok(Math.abs(s.ind.aiBank) < 1);
  s.faults.vacuum = true;
  settle(s, 300);
  assert.ok(s.ind.suction < 0.5);
  assert.ok(Math.abs(s.ind.aiBank) > 10, `ai drift ${s.ind.aiBank}`);
});

test('pitot ram blocked with drain open: ASI decays toward zero', () => {
  const s = createState({ flight: { onGround: false, iasTarget: 100, altTarget: 3000 } });
  settle(s, 2);
  assert.ok(Math.abs(s.ind.ias - 100) < 2);
  s.faults.pitot = 'ram';
  settle(s, 30);
  assert.ok(s.ind.ias < 10, `ias ${s.ind.ias}`);
});

test('pitot ram and drain blocked: ASI acts like an altimeter (climb -> over-reads)', () => {
  const s = createState({ flight: { onGround: false, iasTarget: 90, altTarget: 3000 } });
  settle(s, 2);
  s.faults.pitot = 'ram_and_drain';
  s.flight.altTarget = 6000;
  settle(s, 300);
  assert.ok(s.ind.ias > 100, `ias ${s.ind.ias}`);
});

test('static port blocked: altimeter frozen, VSI zero, ASI under-reads in a climb; alternate static restores (p.3-8)', () => {
  const s = createState({ flight: { onGround: false, iasTarget: 90, altTarget: 3000 } });
  settle(s, 5);
  s.faults.staticBlocked = true;
  s.flight.altTarget = 5000;
  settle(s, 60);
  assert.ok(Math.abs(s.ind.alt - 3000) < 5, `alt ${s.ind.alt}`);
  assert.ok(Math.abs(s.ind.vsi) < 20);
  assert.ok(s.ind.ias < 85, `ias ${s.ind.ias}`);
  s.controls.altStatic = true;
  settle(s, 10);
  assert.ok(Math.abs(s.ind.alt - s.truth.alt) < 40, `alt ${s.ind.alt} vs ${s.truth.alt}`);
});

test('alternate static ASI matches the POH calibration table (p.5-9, flaps up, vents closed)', () => {
  const s = createState({ flight: { onGround: false, iasTarget: 100, altTarget: 3000 }, controls: { altStatic: true } });
  settle(s, 5);
  assert.ok(Math.abs(s.ind.ias - alternateStaticKias(100)) < 0.5);
  assert.equal(alternateStaticKias(100), 101);
  assert.equal(alternateStaticKias(80), 82);
});

test('standard-rate turn: 3 deg/s and the turn coordinator reaches the standard-rate mark', () => {
  const tas = 90;
  const bank = Math.atan((3 * tas * 1.06) / 1091) * 180 / Math.PI; // TAS ~ IAS*1.06 at 3000 ft
  const s = startEngine(createState({ flight: { onGround: false, iasTarget: 90, altTarget: 3000, bank } }));
  settle(s, 5);
  assert.ok(Math.abs(s.truth.turnRate - 3) < 0.2, `rate ${s.truth.turnRate}`);
  assert.ok(Math.abs(s.ind.tc - 1) < 0.08);
});

test('instrument markings in data/instruments.json match the POH constants used by the simulation', () => {
  const asi = Object.fromEntries(instruments.ASI.arcs.map((a) => [a.color, [a.from, a.to]]));
  assert.deepEqual(asi.white, POH.asiWhite);
  assert.deepEqual(asi.green, POH.asiGreen);
  assert.deepEqual(asi.yellow, POH.asiYellow);
  assert.equal(instruments.ASI.redlines[0].value, POH.vne);
  assert.equal(instruments.TACH.redlines[0].value, POH.maxRpm);
  assert.deepEqual([instruments.TACH.arcs[0].from, instruments.TACH.arcs[0].to], POH.tachGreenSL);
  assert.deepEqual([instruments.SUCTION.arcs[0].from, instruments.SUCTION.arcs[0].to], POH.suctionGreen);
  assert.deepEqual([instruments.OIL_P.arcs[0].from, instruments.OIL_P.arcs[0].to], POH.oilPressGreen);
  assert.deepEqual(instruments.OIL_P.redlines.map((r) => r.value), [POH.oilPressMin, POH.oilPressMax]);
  assert.deepEqual([instruments.OIL_T.arcs[0].from, instruments.OIL_T.arcs[0].to], POH.oilTempGreen);
});
