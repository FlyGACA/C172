// Moving the aircraft like the real one: every moving part is a real part of a system model, the controls rest at zero, and
// one control moves what it moves in the aircraft (Phase 8's rig). No browser needed: `npm test`.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { CONTROLS, MOVING, pose, rest } from '../parts/motions.js';

const path = (relative) => fileURLToPath(new URL(relative, import.meta.url));
const nodes = new Map();   // id -> the node's extras
for (const f of readdirSync(path('../parts/m')).filter((n) => n.endsWith('.glb'))) {
  const b = readFileSync(path(`../parts/m/${f}`)), json = JSON.parse(b.subarray(20, 20 + b.readUInt32LE(12)));
  for (const n of json.nodes) if (n.extras?.id) nodes.set(n.extras.id, n.extras);
}
const total = (p) => [...p.hinge.values(), ...p.spin.values(), ...[...p.move.values()].flat()].reduce((a, v) => a + Math.abs(v), 0);

test('at rest nothing is turned or shifted', () => assert.equal(total(pose(rest())), 0));

test('every part a control moves is in the models, with the hinge or axis it moves about', () => {
  for (const id of MOVING) {
    const x = nodes.get(id); assert.ok(x, `${id} is in no system model`);
    const p = pose(Object.fromEntries(CONTROLS.map((c) => [c.key, c.max])));
    if (p.hinge.has(id)) assert.ok(x.hinge_axis, `${id} is hinged here but the model gives it no hinge`);
    if (p.spin.has(id)) assert.ok(x.spin_axis, `${id} spins here but the model gives it no axis`);
  }
});

test('the ailerons move in opposite directions, the flaps together, and the yokes turn with the ailerons', () => {
  const a = pose({ ...rest(), aileron: 1 });
  assert.equal(a.hinge.get('WING_L.aileron'), -a.hinge.get('WING_R.aileron'));
  assert.ok(a.spin.get('INTERIOR.yoke_L') > 0 && a.spin.get('INTERIOR.yoke_L') === a.spin.get('INTERIOR.yoke_R'));
  const f = pose({ ...rest(), flaps: 40 });
  assert.equal(f.hinge.get('WING_L.flap'), 40); assert.equal(f.hinge.get('WING_R.flap'), 40);
});

test('the rudder control moves the rudder, the nose strut and all four pedals', () => {
  const r = pose({ ...rest(), rudder: 1 });
  for (const id of ['EMPENNAGE.rudder', 'GEAR.nose_strut', 'INTERIOR.pedal_L_L', 'INTERIOR.pedal_L_R', 'INTERIOR.pedal_R_L', 'INTERIOR.pedal_R_R']) assert.notEqual(r.hinge.get(id), 0, id);
});

test('every control moves something, and stays inside the range the model allows', () => {
  for (const c of CONTROLS) {
    assert.ok(total(pose({ ...rest(), [c.key]: c.max })) > 0, `${c.key} moves nothing`);
    assert.ok(c.min <= 0 && c.max > 0 && c.en && c.ar, c.key);
  }
  for (const [id, deg] of pose({ ...rest(), flaps: 40 }).hinge) { const r = nodes.get(id)?.range_deg; if (r && deg) assert.ok(deg >= r[0] && deg <= r[1], `${id} ${deg}`); }
});
