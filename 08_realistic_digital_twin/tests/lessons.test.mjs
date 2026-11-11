// The flight lessons: each one is flown by its demonstration pilot and must come out as the handbook says.
// Run: node --test 08_realistic_digital_twin/tests/lessons.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { LESSONS, startLesson, tickLesson, demonstrate } from '../js/lessons.js';
import { stepDeck, readySystems, beginFlight, STARTS } from '../js/flightdeck.js';
import { createPilot, pilotStep } from '../js/pilot.js';
import { createState, step } from '../js/sim.js';
import * as POH from '../js/poh_tables.js';
import { clMax } from '../js/flight.js';

const lesson = (id) => LESSONS.find((l) => l.id === id);
const wrap = (deg) => ((deg + 540) % 360) - 180;

/** Fly a lesson with a pilot given as a function (deck, ctx, t, dt) -> controls; returns what the lesson recorded. */
function fly(l, pilot, seconds, conditions = {}) {
  const { sim, deck, trim, ctx } = startLesson(l, conditions);
  const dt = 1 / 60;
  let t = 0, step = 0;
  while (t < seconds) {
    const c = pilot(deck, ctx, t, dt) || {};
    stepDeck(deck, { aileron: c.aileron ?? 0, elevator: c.elevator ?? 0, rudder: c.rudder ?? 0, trim, flapCommandDeg: c.flapCommandDeg ?? deck.controls.flapCommandDeg, brake: c.brake ?? 0 }, dt);
    t += dt;
    step = tickLesson(l, sim, ctx, dt);
  }
  return { sim, deck, ctx, step };
}

test('each lesson is complete: two languages, a handbook page, a place to begin, steps, a review question, a demonstration', () => {
  assert.deepEqual(LESSONS.map((l) => l.id), ['stall_recovery', 'go_around', 'engine_failure_after_takeoff']);
  const arabic = /[؀-ۿ]{3}/;
  for (const l of LESSONS) {
    for (const text of [l.title, l.brief, l.debrief, l.quiz.q, ...l.quiz.options, ...l.steps]) {
      assert.ok(text.en && text.en.length > 3, `${l.id}: English`);
      assert.match(text.ar, arabic, `${l.id}: Arabic for "${text.en}"`);
    }
    assert.match(l.poh, /^POH \d-\d/, `${l.id}: handbook page`);
    assert.equal(l.flight.kind, 'air');
    assert.ok(l.steps.length >= 6 && l.steps.every((s) => typeof s.done === 'function'), `${l.id}: steps checked by the flight`);
    assert.equal(typeof l.demo, 'function'); assert.equal(typeof l.report, 'function');
    assert.deepEqual(l.report({}), [], `${l.id}: nothing to report before it is flown`);
  }
});

test('stall and recovery, demonstrated: horn, stall, nose down, power, climb; less than 180 ft lost (POH 4-17, 5-11)', () => {
  const r = demonstrate(lesson('stall_recovery'), { seconds: 90 });
  const c = r.ctx;
  assert.equal(r.completed, true, `steps ${JSON.stringify(c.done)}`);
  const margin = c.hornKcas - c.stallKcas;
  assert.ok(margin >= POH.STALL_WARNING.knotsBefore[0] && margin <= POH.STALL_WARNING.knotsBefore[1], `horn ${margin.toFixed(1)} knots before the stall`);
  assert.ok(c.stallAlt - c.lowest < POH.STALL_KCAS.recoveryLossFt, `lost ${(c.stallAlt - c.lowest).toFixed(0)} ft`);
  assert.ok(c.entryError < 60, `altitude held within ${c.entryError.toFixed(0)} ft on the way in`);
  assert.ok(!c.secondary && c.maxBank < 10, 'no second stall, wings level');
  assert.equal(r.sim.controls.carbHeat, 0); assert.equal(r.sim.controls.throttle, 1);
  const lines = lesson('stall_recovery').report(c);
  assert.equal(lines.length, 3); assert.match(lines[1].en, /Height lost/); assert.match(lines[1].ar, /الارتفاع المفقود/);
});

test('stall lesson: holding the wheel back without recovering does not pass, and pulling up at once stalls again', () => {
  const l = lesson('stall_recovery');
  // the student closes the throttle, pulls and keeps pulling
  const stuck = fly(l, (deck, ctx, t) => {
    deck.sim.controls.carbHeat = 1; if (t > 1) deck.sim.controls.throttle = 0;
    const p = (ctx.p ??= createPilot());
    return ctx.stallKias == null ? pilotStep(p, deck.flight, { altFt: 3000, bankDeg: 0, maxPitchDeg: 30 }, 1 / 60) : pilotStep(p, deck.flight, { elevator: 1, bankDeg: 0 }, 1 / 60);
  }, 60);
  assert.equal(stuck.step, 4, 'the lesson waits at "wheel forward"');
  assert.ok(stuck.ctx.stallAlt - stuck.ctx.lowest > 300, `held in the stall it lost ${(stuck.ctx.stallAlt - stuck.ctx.lowest).toFixed(0)} ft`);
  // the student recovers but hauls the nose up at once
  const hasty = fly(l, (deck, ctx, t) => {
    deck.sim.controls.carbHeat = 1; if (t > 1) deck.sim.controls.throttle = 0;
    const p = (ctx.p ??= createPilot());
    if (ctx.stallKias == null) return pilotStep(p, deck.flight, { altFt: 3000, bankDeg: 0, maxPitchDeg: 30 }, 1 / 60);
    if (!ctx.unstalled) return pilotStep(p, deck.flight, { pitchDeg: -3, bankDeg: 0 }, 1 / 60);
    deck.sim.controls.throttle = 1; deck.sim.controls.carbHeat = 0;
    return pilotStep(p, deck.flight, { elevator: 0.9, bankDeg: 0 }, 1 / 60);
  }, 40);
  assert.equal(hasty.ctx.secondary, true, 'a second stall');
});

test('go-around, demonstrated: full throttle, carburetor heat cold, flaps 20 at once, 55 KIAS, flaps 10, flaps up (POH 4-9)', () => {
  const r = demonstrate(lesson('go_around'), { seconds: 90 });
  const c = r.ctx;
  assert.equal(r.completed, true, `steps ${JSON.stringify(c.done)}`);
  assert.ok(c.startAgl - c.minAgl < 40, `lost ${(c.startAgl - c.minAgl).toFixed(0)} ft before climbing`);
  assert.ok(c.minKias >= 50, `lowest speed ${c.minKias.toFixed(0)} KIAS`);
  assert.ok(!c.horn, 'no stall warning');
  assert.ok(c.flap20At - c.fullAt < 3, 'flaps to 20 at once');
  assert.equal(r.deck.flight.flapDeg, 0);
  assert.ok(r.deck.flight.out.aglFt > c.startAgl + 150 && r.deck.flight.out.vsFpm > -200, `clean and ${(r.deck.flight.out.aglFt - c.startAgl).toFixed(0)} ft above where it began`);
});

test('go-around: flaps left at 40 hardly climb; all the flaps up at once at 55 KIAS leave no margin from the stall', () => {
  const l = lesson('go_around');
  const pilot = (flaps) => (deck, ctx, t) => {
    const p = (ctx.p ??= createPilot());
    if (t > 1.5) { deck.sim.controls.throttle = 1; deck.sim.controls.carbHeat = 0; }
    return { ...pilotStep(p, deck.flight, { kias: t > 1.5 ? 55 : 60, bankDeg: 0, maxPitchDeg: 20 }, 1 / 60), flapCommandDeg: t > 2.8 ? flaps : 40 };
  };
  const gained = (r) => r.deck.flight.out.aglFt - r.ctx.minAgl;
  const proper = fly(l, pilot(20), 30), full = fly(l, pilot(40), 30);
  assert.ok(gained(full) < 0.8 * gained(proper), `flaps left at 40 gain ${gained(full).toFixed(0)} ft in 30 s, flaps 20 gain ${gained(proper).toFixed(0)} ft`);
  // at the forward centre of gravity limit the flaps-up stall is 47 KIAS: 55 KIAS with the flaps up is inside the stall warning
  const fwd20 = fly(l, pilot(20), 30, { cgFrac: 0 }), fwdUp = fly(l, pilot(0), 30, { cgFrac: 0 });
  const used = (r) => r.deck.flight.out.CL / clMax(r.deck.flight.flapDeg, 0);      // how much of its maximum lift the wing is using
  assert.ok(!fwd20.ctx.horn && used(fwd20) < 0.74, `flaps 20 at 55 KIAS: ${(used(fwd20) * 100).toFixed(0)} % of the maximum lift, no stall warning`);
  assert.ok(used(fwdUp) > 0.76, `flaps up at once at 55 KIAS: ${(used(fwdUp) * 100).toFixed(0)} % of the maximum lift, at the edge of the stall warning`);
  assert.ok(fwdUp.step < l.steps.length && full.step < l.steps.length, 'neither passes the checklist');
});

test('engine failure after takeoff, demonstrated: nose down to 65 KIAS, straight ahead, fuel and ignition secured, flaps before the master (POH 3-4, 3-11)', () => {
  const r = demonstrate(lesson('engine_failure_after_takeoff'), { seconds: 120 });
  const c = r.ctx, s = r.sim;
  assert.equal(r.completed, true, `steps ${JSON.stringify(c.done)}`);
  assert.equal(s.faults.engineFailure, true, 'the failure is the fault panel\'s engine failure');
  assert.ok(s.events.some((e) => e.type === 'engine_failed'));
  assert.ok(c.failAgl > 200 && c.failAgl < 300, `failed at ${c.failAgl.toFixed(0)} ft`);
  assert.ok(c.minKias >= 52 && c.maxKias <= 72, `glide between ${c.minKias.toFixed(0)} and ${c.maxKias.toFixed(0)} KIAS`);
  assert.ok(c.glideAfter < 6, `at the glide speed ${c.glideAfter.toFixed(1)} s after the failure`);
  assert.ok(c.maxTurn < 10, `heading changed ${c.maxTurn.toFixed(0)} degrees`);
  assert.ok(c.touchFpm > -400 && Math.abs(c.touchBank) < 8, `touchdown at ${c.touchFpm.toFixed(0)} ft/min`);
  assert.deepEqual([s.controls.mixture, s.controls.fuelSelector, s.controls.ignition, s.controls.masterBat], [0, 'OFF', 'OFF', false]);
  assert.ok(Math.abs(r.deck.flight.flapDeg - 20) < 1, 'the flaps were down before the master switch went off');
  assert.ok(r.deck.flight.out.onGround && r.deck.flight.out.wheels >= 2 && r.deck.flight.out.groundSpeedKt < c.touchKias, 'and it is on its wheels, slowing');
});

test('engine failure after takeoff: the turn back does not reach the runway (POH 3-11)', () => {
  const l = lesson('engine_failure_after_takeoff');
  const r = fly(l, (deck, ctx, t) => {
    const p = (ctx.p ??= createPilot()), o = deck.flight.out;
    if (deck.sim.engine.running) return pilotStep(p, deck.flight, { kias: 70, headingDeg: 0 }, 1 / 60);
    if (ctx.turned == null && Math.abs(wrap(o.headingDeg - 180)) < 12) ctx.turned = { agl: o.aglFt, east: deck.flight.east, north: deck.flight.north };
    if (o.onGround) return { brake: 1 };
    return pilotStep(p, deck.flight, ctx.turned ? { kias: 65, headingDeg: 180, minPitchDeg: -15 } : { kias: 65, bankDeg: 40, minPitchDeg: -15 }, 1 / 60);
  }, 60);
  const c = r.ctx;
  assert.ok(c.failed && !r.sim.engine.running);
  // it comes out of the turn low and well to the side of the runway (or meets the ground first), and ends off the runway
  if (c.turned) {
    assert.ok(c.turned.agl < 120, `after the turn: ${c.turned.agl.toFixed(0)} ft`);
    assert.ok(Math.abs(c.turned.east) > 100, `and ${Math.abs(c.turned.east).toFixed(0)} m to the side of the runway`);
  }
  assert.ok(c.landed && c.maxTurn > 90);
  assert.ok(Math.abs(r.deck.flight.east) > 50, `it ends ${Math.abs(r.deck.flight.east).toFixed(0)} m from the centre line`);
  assert.ok(c.touchFpm < -700, `and meets the ground at ${(-c.touchFpm).toFixed(0)} ft/min`);
  assert.equal(c.horn, true, 'with the stall warning sounding in the turn');
});

test('a lesson waits for the pilot: nothing done, nothing passed', () => {
  for (const l of LESSONS) {
    const r = fly(l, (deck, ctx) => pilotStep((ctx.p ??= createPilot()), deck.flight, { pitchDeg: deck.flight.out.pitchDeg, bankDeg: 0 }, 1 / 60), 5);
    assert.ok(r.step < 2, `${l.id}: at step ${r.step}`);
  }
});

test('the flaps are electric: with the master switch off they stay where they are (POH 7-10)', () => {
  const sim = readySystems();
  const { deck, trim } = beginFlight(sim, STARTS.cruise);
  const p = createPilot();
  const run = (seconds, flaps) => { for (let i = 0; i < seconds * 60; i++) stepDeck(deck, { ...pilotStep(p, deck.flight, { altFt: 3000, bankDeg: 0 }, 1 / 60), trim, flapCommandDeg: flaps }, 1 / 60); };
  run(3, 10);
  assert.ok(Math.abs(deck.flight.flapDeg - 10) < 0.1, 'powered: they travel');
  sim.controls.masterBat = false; sim.controls.masterAlt = false;
  run(4, 40);
  assert.ok(Math.abs(deck.flight.flapDeg - 10) < 0.1, `master off: ${deck.flight.flapDeg.toFixed(1)} degrees`);
  sim.controls.masterBat = true;
  run(7, 40);
  assert.ok(Math.abs(deck.flight.flapDeg - 40) < 0.1, 'power back: they go on');
});

test('the engine failure fault stops the engine for good, in the systems simulation alone as well', () => {
  const s = createState({ controls: { masterBat: true, masterAlt: true, ignition: 'BOTH', mixture: 1, throttle: 0.5, fuelSelector: 'BOTH' }, engine: { running: true, rpm: 2000, oilTempF: 170, oilPress: 60 },
    flight: { onGround: false, iasTarget: 90, altTarget: 3000 }, truth: { ias: 90, alt: 3000 } });
  step(s, 5);
  assert.equal(s.engine.running, true);
  s.faults.engineFailure = true;
  step(s, 5);
  assert.equal(s.engine.running, false);
  assert.equal(s.events.at(-1).type, 'engine_failed');
  step(s, 20);
  assert.equal(s.engine.running, false, 'the windmilling propeller does not restart it');
  s.faults.engineFailure = false;
  step(s, 5);
  assert.equal(s.engine.running, true, 'with the fault cleared the windmilling propeller restarts it (POH 3-4)');
});
