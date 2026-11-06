// Scripted "student" runs proving each guided scenario can be completed with the POH actions.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createState, step } from '../js/sim.js';
import { SCENARIOS, evaluateSteps } from '../js/scenarios.js';

const byId = Object.fromEntries(SCENARIOS.map((s) => [s.id, s]));

function runner(id) {
  const sc = byId[id];
  const s = createState(structuredClone(sc.setup));
  const ctx = {};
  const advance = (sec) => {
    for (let t = 0; t < sec; t += 0.1) {
      step(s, 0.1);
      sc.tick?.(s, ctx, 0.1);
      evaluateSteps(sc, s, ctx);
    }
  };
  const current = () => evaluateSteps(sc, s, ctx);
  const ack = () => { ctx.done[current()] = true; };
  const choose = (i) => { const st = sc.steps[current()]; assert.equal(i, st.answer); ctx.done[current()] = true; };
  return { sc, s, ctx, advance, current, ack, choose };
}

test('every scenario has bilingual text, a POH reference and well-formed steps', () => {
  for (const sc of SCENARIOS) {
    assert.ok(sc.title.en && sc.title.ar && sc.brief.en && sc.brief.ar && sc.debrief.en && sc.debrief.ar, sc.id);
    assert.match(sc.poh, /POH/);
    for (const st of sc.steps) {
      assert.ok(st.en && st.ar, `${sc.id} step text`);
      assert.ok(st.ack || st.choice || typeof st.done === 'function', `${sc.id} step type`);
      if (st.choice) assert.ok(st.options.length >= 2 && st.answer < st.options.length);
    }
  }
});

test('engine start scenario completes with the POH sequence', () => {
  const r = runner('engine_start');
  Object.assign(r.s.controls, { mixture: 1, carbHeat: 0, masterBat: true, masterAlt: true });
  r.ctx.primes = 3; r.s.controls.primeStrokes = 3;
  r.s.controls.throttle = 0.06;
  r.advance(1);
  assert.equal(r.current(), 5);
  r.ack();
  r.s.controls.ignition = 'START';
  r.advance(3);
  r.s.controls.ignition = 'BOTH';
  r.advance(4);
  r.s.controls.avionics = true;
  r.advance(1);
  assert.equal(r.current(), r.sc.steps.length);
});

test('run-up scenario records magneto drops that pass the POH limits', () => {
  const r = runner('runup');
  Object.assign(r.s.controls, { fuelSelector: 'BOTH' });
  r.advance(2);
  for (let i = 0; i < 40 && Math.abs(r.s.engine.rpm - 1700) > 15; i++) { r.s.controls.throttle += (1700 - r.s.engine.rpm) / 4000; r.advance(3); }
  r.s.controls.ignition = 'R'; r.advance(5);
  r.s.controls.ignition = 'BOTH'; r.advance(4);
  r.s.controls.ignition = 'L'; r.advance(5);
  r.s.controls.ignition = 'BOTH'; r.advance(4);
  assert.ok(r.ctx.mag && r.ctx.mag.pass, JSON.stringify(r.ctx.mag));
  r.s.controls.carbHeat = 1; r.advance(3); r.s.controls.carbHeat = 0; r.advance(30);
  assert.equal(r.current(), 9, 'waits for the instruments acknowledgement');
  r.ack();
  r.s.controls.throttle = 0.1; r.advance(6);
  assert.equal(r.current(), r.sc.steps.length);
});

test('run-up fault scenario exposes the weak right magneto', () => {
  const r = runner('runup_fault');
  r.advance(2);
  for (let i = 0; i < 40 && Math.abs(r.s.engine.rpm - 1700) > 15; i++) { r.s.controls.throttle += (1700 - r.s.engine.rpm) / 4000; r.advance(3); }
  r.s.controls.ignition = 'R'; r.advance(5);
  r.s.controls.ignition = 'BOTH'; r.advance(4);
  r.s.controls.ignition = 'L'; r.advance(5);
  r.s.controls.ignition = 'BOTH'; r.advance(4);
  assert.equal(r.ctx.mag.pass, false);
  assert.ok(r.ctx.mag.dropR > 125);
});

test('leaning scenario reaches 25-50 RPM below peak', () => {
  const r = runner('leaning');
  r.advance(5);
  for (let m = 1; m > 0.4 && r.current() < 3; m -= 0.01) { r.s.controls.mixture = m; r.advance(1.5); }
  assert.equal(r.current(), 3, `peak ${r.ctx.peak} rpm ${r.s.engine.rpm}`);
});

test('carb ice scenario: full throttle + full heat clears the ice', () => {
  const r = runner('carb_ice');
  r.advance(60);
  assert.equal(r.current(), 1);
  r.s.controls.throttle = 1; r.s.controls.carbHeat = 1;
  r.advance(40);
  r.s.controls.carbHeat = 0; r.s.controls.throttle = 0.65;
  r.advance(2);
  assert.equal(r.current(), r.sc.steps.length);
});

test('static blockage scenario', () => {
  const r = runner('static_block');
  r.advance(40);
  assert.equal(r.current(), 1);
  r.s.controls.altStatic = true;
  r.advance(2);
  r.ack();
  assert.equal(r.current(), r.sc.steps.length);
});

test('pitot ice scenario: pitot heat clears the blockage', () => {
  const r = runner('pitot_ice');
  r.advance(25);
  r.s.controls.pitotHeat = true;
  r.advance(20);
  assert.equal(r.current(), r.sc.steps.length);
});

test('low-voltage scenario follows the POH 3-9 checklist to the end', () => {
  const r = runner('low_voltage');
  r.advance(6);
  assert.equal(r.current(), 1);
  r.s.controls.avionics = false; r.advance(0.5);
  r.s.controls.masterBat = false; r.s.controls.masterAlt = false; r.advance(0.5);
  r.s.controls.masterBat = true; r.s.controls.masterAlt = true; r.advance(5);
  assert.equal(r.current(), 5);
  r.s.controls.masterAlt = false; r.advance(0.5);
  Object.assign(r.s.controls, { landingLight: false, beacon: false, pitotHeat: false }); r.advance(0.5);
  r.ack();
  assert.equal(r.current(), r.sc.steps.length);
});

test('vacuum failure scenario', () => {
  const r = runner('vacuum_fail');
  r.advance(12);
  assert.equal(r.current(), 1);
  r.ack();
  r.advance(65);
  assert.ok(r.s.ind.tc > 0.3, 'turn coordinator shows a right turn');
  r.choose(0);
  assert.equal(r.current(), r.sc.steps.length);
});

test('engine failure scenario: POH 3-4 checklist restores power', () => {
  const r = runner('engine_failure');
  r.advance(60);
  assert.equal(r.s.engine.running, false);
  r.s.flight.iasTarget = 65; r.advance(5);
  r.s.controls.carbHeat = 1; r.s.controls.fuelSelector = 'BOTH'; r.advance(1);
  r.advance(1);
  assert.equal(r.current(), 6);
  r.ack();
  r.advance(6);
  assert.equal(r.s.engine.running, true);
  assert.equal(r.current(), r.sc.steps.length);
});
