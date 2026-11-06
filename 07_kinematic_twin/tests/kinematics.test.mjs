import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  CYLINDERS, CRANK_R, ROD_L, FIRING_ORDER, firingSequence, pinPosition, pistonPinDistance, pistonPosition,
  rodAngle, strokeOf, valveLift, sparkActive,
} from '../js/kinematics.js';

const index = JSON.parse(readFileSync(new URL('../data/model_index.json', import.meta.url), 'utf8'));
const D = Math.PI / 180;

test('firing order is Lycoming 1-3-2-4', () => {
  assert.deepEqual(FIRING_ORDER, [1, 3, 2, 4]);
  assert.deepEqual(firingSequence(), [1, 3, 2, 4]);
});

test('Lycoming numbering: odd cylinders on the right bank (-X), even on the left, No.1 right-front', () => {
  for (const [n, c] of Object.entries(CYLINDERS)) assert.equal(c.side, Number(n) % 2 ? -1 : 1);
  assert.ok(CYLINDERS[1].z > CYLINDERS[3].z && CYLINDERS[2].z > CYLINDERS[4].z);
  assert.ok(CYLINDERS[1].z > CYLINDERS[2].z, 'right bank is staggered forward');
});

test('JS kinematics match the geometry the Python builder wrote into the GLB', () => {
  assert.equal(index.crank_radius_m, CRANK_R);
  assert.equal(index.rod_length_m, ROD_L);
  assert.deepEqual(index.firing_order, FIRING_ORDER);
  for (const [n, c] of Object.entries(CYLINDERS)) {
    assert.equal(index.cylinders[n].z_m, c.z);
    assert.equal(index.cylinders[n].crank_pin_deg, c.pinDeg);
    assert.equal(index.cylinders[n].bank, c.side > 0 ? 'L' : 'R');
  }
});

test('at crank angle 0, cylinders 1 and 2 are at TDC and 3 and 4 at BDC', () => {
  assert.ok(Math.abs(pistonPinDistance(0, 1) - (CRANK_R + ROD_L)) < 1e-9);
  assert.ok(Math.abs(pistonPinDistance(0, 2) - (CRANK_R + ROD_L)) < 1e-9);
  assert.ok(Math.abs(pistonPinDistance(0, 3) - (ROD_L - CRANK_R)) < 1e-9);
  assert.ok(Math.abs(pistonPinDistance(0, 4) - (ROD_L - CRANK_R)) < 1e-9);
});

test('opposed pistons move as a boxer pair and connecting rods keep their length', () => {
  for (let deg = 0; deg < 720; deg += 7) {
    const t = deg * D;
    assert.ok(Math.abs(pistonPinDistance(t, 1) - pistonPinDistance(t, 2)) < 1e-12);
    assert.ok(Math.abs(pistonPinDistance(t, 3) - pistonPinDistance(t, 4)) < 1e-12);
    for (const c of [1, 2, 3, 4]) {
      const p = pinPosition(t, c), q = pistonPosition(t, c);
      assert.ok(Math.abs(Math.hypot(q[0] - p[0], q[1] - p[1]) - ROD_L) < 1e-12);
      const a = rodAngle(t, c);
      assert.ok(Math.abs(p[0] + ROD_L * Math.cos(a) - q[0]) < 1e-12);
    }
  }
});

test('strokes, valves and spark follow each cylinder\'s four-stroke cycle', () => {
  assert.equal(strokeOf(90, 1), 'power');
  assert.equal(strokeOf(90 + 180, 3), 'power');
  assert.equal(strokeOf(90 + 360, 2), 'power');
  assert.equal(strokeOf(90 + 540, 4), 'power');
  assert.equal(strokeOf(270, 1), 'exhaust');
  assert.ok(valveLift(270, 1, 'exhaust') > 0.95);
  assert.equal(valveLift(270, 1, 'intake'), 0);
  assert.ok(valveLift(450, 1, 'intake') > 0.9);
  assert.equal(valveLift(90, 1, 'intake') + valveLift(90, 1, 'exhaust'), 0, 'both closed on the power stroke');
  assert.ok(valveLift(0, 1, 'intake') === 0 && valveLift(360, 1, 'intake') > 0 && valveLift(360, 1, 'exhaust') > 0, 'overlap at exhaust TDC');
  assert.equal(sparkActive(-10, 1), true);
  assert.equal(sparkActive(350, 1), false, 'no spark at exhaust TDC (4-stroke)');
  assert.equal(sparkActive(170, 3), true);
});
