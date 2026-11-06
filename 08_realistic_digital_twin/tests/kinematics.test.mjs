// Phase 8: the JS kinematics must agree with the engine geometry the Blender build wrote into the GLB
// (model_index_high.json carries every part's extras: cylinder number, bank side, magneto, animation hints).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { CYLINDERS, CRANK_R, ROD_L, FIRING_ORDER, firingSequence, pistonPinDistance, pinPosition, rodAngle, sparkActive, strokeOf } from '../js/kinematics.js';

const index = JSON.parse(readFileSync(new URL('../models/model_index_high.json', import.meta.url), 'utf8'));
const parts = new Map(index.parts.map((p) => [p.name, p]));

test('firing order is Lycoming 1-3-2-4 and crank pins pair 1/4 and 2/3', () => {
  assert.deepEqual(FIRING_ORDER, [1, 3, 2, 4]);
  assert.deepEqual(firingSequence(), [1, 3, 2, 4]);
  assert.equal(CYLINDERS[1].pinDeg, CYLINDERS[4].pinDeg);
  assert.equal(CYLINDERS[2].pinDeg, CYLINDERS[3].pinDeg);
  assert.equal(Math.abs(CYLINDERS[1].pinDeg - CYLINDERS[2].pinDeg), 180);
});

test('Lycoming numbering: odd cylinders right bank (-X), even left, No.1 right-front', () => {
  for (const [n, c] of Object.entries(CYLINDERS)) assert.equal(c.side, Number(n) % 2 ? -1 : 1);
  assert.ok(CYLINDERS[1].z > CYLINDERS[3].z && CYLINDERS[2].z > CYLINDERS[4].z);
  assert.ok(CYLINDERS[1].z > CYLINDERS[2].z, 'right bank staggered forward');
});

test('GLB engine parts exist for every cylinder with the expected animation hints', () => {
  for (const c of [1, 2, 3, 4]) {
    for (const nm of [`ENGINE.piston_${c}`, `ENGINE.rod_${c}`, `ENGINE.valve_intake_${c}`, `ENGINE.valve_exhaust_${c}`, `ENGINE.cylinder_barrel_${c}`, `ENGINE.cylinder_head_${c}`]) {
      assert.ok(parts.has(nm), nm);
      assert.equal(parts.get(nm).cyl, c);
    }
    assert.equal(parts.get(`ENGINE.piston_${c}`).animate, 'piston');
    assert.equal(parts.get(`ENGINE.rod_${c}`).animate, 'rod');
  }
  assert.equal(parts.get('ENGINE.crankshaft').spin_axis, 'z');
  assert.equal(parts.get('POWERPLANT.propeller').spin_axis, 'z');
});

test('POH p.7-19 plug map in the GLB: R magneto = lower right + upper left, L = lower left + upper right', () => {
  for (const c of [1, 2, 3, 4]) {
    const side = CYLINDERS[c].side;             // -1 right bank
    const top = parts.get(`ENGINE.plug_top_${c}`), bottom = parts.get(`ENGINE.plug_bottom_${c}`);
    assert.equal(bottom.magneto, side < 0 ? 'R' : 'L');
    assert.equal(top.magneto, side < 0 ? 'L' : 'R');
  }
});

test('at crank angle 0, cylinders 1 and 2 are at TDC and 3 and 4 at BDC', () => {
  assert.ok(Math.abs(pistonPinDistance(0, 1) - (CRANK_R + ROD_L)) < 1e-9);
  assert.ok(Math.abs(pistonPinDistance(0, 2) - (CRANK_R + ROD_L)) < 1e-9);
  assert.ok(Math.abs(pistonPinDistance(0, 3) - (ROD_L - CRANK_R)) < 1e-9);
  assert.ok(Math.abs(pistonPinDistance(0, 4) - (ROD_L - CRANK_R)) < 1e-9);
});

test('rod angle points from the crank pin toward the piston on its own bank', () => {
  for (let i = 0; i < 24; i++) {
    const th = (i / 24) * 2 * Math.PI;
    for (const c of [1, 2, 3, 4]) {
      const [px, py] = pinPosition(th, c);
      const d = pistonPinDistance(th, c);
      const x = CYLINDERS[c].side * d;
      const a = rodAngle(th, c);
      assert.ok(Math.abs(Math.hypot(x - px, 0 - py) - ROD_L) < 1e-9);
      assert.ok(Math.abs(Math.atan2(0 - py, x - px) - a) < 1e-9);
    }
  }
});

test('spark happens once per 720° per cylinder, in firing order', () => {
  const order = [];
  for (let d = 0; d < 720; d += 1) for (const c of [1, 2, 3, 4]) if (sparkActive(d, c, 2) && !sparkActive(d - 1, c, 2)) order.push(c);
  assert.equal(order.length, 4, 'one spark per cylinder per 720°');
  const i1 = order.indexOf(1);
  assert.deepEqual([...order.slice(i1), ...order.slice(0, i1)], [1, 3, 2, 4]);
  assert.equal(strokeOf(10, 1), 'power');
  assert.equal(strokeOf(190, 1), 'exhaust');
});

test('every exported part carries bilingual labels and a documentation status', () => {
  for (const p of index.parts) {
    assert.ok(p.label_en && p.label_ar, p.name);
    assert.ok(['poh', 'type_data', 'estimated'].includes(p.status), `${p.name}: ${p.status}`);
  }
  assert.ok(index.parts.length > 300);
  assert.ok(index.triangles < 600000);
});
