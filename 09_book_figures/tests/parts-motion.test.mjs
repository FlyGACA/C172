// Moving the aircraft like the real one: every moving part is a real part of a system model, the controls rest at zero, and
// one control moves what it moves in the aircraft (Phase 8's rig). No browser needed: `npm test`.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { ABOUT_PARENT_Z, CONTROLS, GLOWING, GROUPS, MOVING, PLUGS, SWITCHES, pose, rest, setScales } from '../parts/motions.js';

const path = (relative) => fileURLToPath(new URL(relative, import.meta.url));
const nodes = new Map();   // id -> the node's extras
for (const f of readdirSync(path('../parts/m')).filter((n) => n.endsWith('.glb'))) {
  const b = readFileSync(path(`../parts/m/${f}`)), json = JSON.parse(b.subarray(20, 20 + b.readUInt32LE(12)));
  for (const n of json.nodes) if (n.extras?.id) nodes.set(n.extras.id, n.extras);
}
setScales(JSON.parse(readFileSync(path('../../08_realistic_digital_twin/data/instruments.json'), 'utf8')).instruments);
const total = (p) => [...p.hinge.values(), ...p.spin.values(), ...[...p.move.values()].flat()].reduce((a, v) => a + Math.abs(v), 0);

test('at rest nothing is turned or shifted', () => assert.equal(total(pose(rest())), 0));

test('every part a control moves is in the models, with the hinge or axis it moves about', () => {
  for (const id of MOVING) {
    const x = nodes.get(id); assert.ok(x, `${id} is in no system model`);
    const p = pose(Object.fromEntries(CONTROLS.map((c) => [c.key, c.max])));
    if (p.hinge.has(id)) assert.ok(x.hinge_axis, `${id} is hinged here but the model gives it no hinge`);
    if (p.spin.has(id) && !ABOUT_PARENT_Z(id)) assert.ok(x.spin_axis, `${id} spins here but the model gives it no axis`);
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
    assert.ok(total(pose({ ...rest(), [c.key]: c.max, inst: 1 })) > 0 || pose({ ...rest(), [c.key]: c.max, swBat: 1, swBeacon: 1 }).glow.size > 0, `${c.key} moves nothing`);
    assert.ok(c.min <= (c.home ?? 0) && c.max > c.min && c.en && c.ar, c.key);
  }
  for (const [id, deg] of pose({ ...rest(), flaps: 40 }).hinge) { const r = nodes.get(id)?.range_deg; if (r && deg) assert.ok(deg >= r[0] && deg <= r[1], `${id} ${deg}`); }
});

test('turning the engine moves the crank, the propeller, the pistons, the rods and the valves, and two turns bring it back', () => {
  const at = (crank) => pose({ ...rest(), crank });
  const a = at(100);
  for (const id of ['ENGINE.crankshaft', 'POWERPLANT.spinner', 'ENGINE.crank_flange_pulley']) assert.ok(Math.abs(a.spin.get(id)) > 0, id);
  assert.equal(a.spin.get('ENGINE.camshaft'), -a.spin.get('ENGINE.crankshaft') / 2);
  for (const c of [1, 2, 3, 4]) { assert.ok(a.move.get(`ENGINE.piston_${c}`)[0] !== 0, `piston ${c}`); assert.ok(a.spin.get(`ENGINE.rod_${c}`) !== 0, `rod ${c}`); }
  // the valves open somewhere in the cycle and are shut at the start
  assert.ok([...Array(72).keys()].some((i) => at(i * 10).move.get('ENGINE.valve_intake_1')[0] !== 0), 'the intake valve never opens');
  const b = at(720), z = at(0);
  for (const [id, v] of b.move) for (let i = 0; i < 3; i++) assert.ok(Math.abs(v[i] - z.move.get(id)[i]) < 1e-9, `${id} is not back after two turns`);
});

test('a piston travels its full stroke in half a turn of the crank', () => {
  const x = (crank, c) => pose({ ...rest(), crank }).move.get(`ENGINE.piston_${c}`)[0];
  assert.ok(Math.abs(x(180, 1) - x(0, 1)) > 0.05, 'a piston moves its full stroke in half a turn');
});

test('the levers pull out toward the pilot, the ignition and fuel selector turn, and every switch goes up and down about its middle', () => {
  const p = pose({ ...rest(), throttle: 1, mixture: 1, ignition: 2, fuelSel: 2 });
  assert.ok(p.move.get('PANEL.throttle')[2] < 0 && p.move.get('PANEL.mixture')[2] < 0);
  assert.ok(p.spin.get('PANEL.ignition_switch') > 0 && p.spin.get('FUEL.selector_handle') > 0);
  for (const [key, id] of SWITCHES) { const up = pose({ ...rest(), [key]: 1 }).hinge.get(id), down = pose({ ...rest(), [key]: -1 }).hinge.get(id); assert.ok(up > 0 && down < 0 && up === -down, id); }
});

test('every control belongs to a heading and has names in both languages (a discrete one names each position)', () => {
  for (const c of CONTROLS) {
    assert.ok(GROUPS[c.group], `${c.key} has no heading`); assert.ok(c.en && c.ar, c.key);
    if (c.names) { assert.equal(c.names.length, c.max - c.min + 1, c.key); for (const n of c.names) assert.ok(n.en && n.ar, c.key); }
  }
  for (const g of Object.values(GROUPS)) assert.ok(g.en && g.ar);
});

test('the instruments: every needle is in the models, readings turn it the way the Phase 8 viewer does, and nothing moves until one is set', () => {
  assert.equal(total(pose({ ...rest(), asi: 120 })), 0, 'a reading set without `inst` moved a needle');
  const p = pose({ ...rest(), inst: 1, asi: 120, tach: 2300, alt: 4500, bank: 30, hdg: 90, turn: 1 });
  for (const id of ['PANEL.ASI.needle_ASI', 'PANEL.TACH.needle_TACH', 'PANEL.ALT.needle_ALT_100', 'PANEL.ALT.needle_ALT_1000', 'PANEL.ALT.needle_ALT_10000', 'PANEL.TC.needle_TC', 'PANEL.AI.ball', 'PANEL.DG.card']) {
    assert.ok(nodes.get(id)?.spin_axis, `${id} is not a spinning part in the models`); assert.ok(p.spin.has(id), `${id} is not driven`);
  }
  assert.ok(Math.abs(p.spin.get('PANEL.ALT.needle_ALT_100') - ((4500 % 1000) * 0.36 * Math.PI) / 180) < 1e-9);
  assert.ok(MOVING.has('PANEL.ASI.needle_ASI'));
  assert.ok(p.spin.get('PANEL.AI.ball') < 0 && p.spin.get('PANEL.DG.card') < 0, 'bank and heading turn the ball and the card the other way');
  for (const c of CONTROLS.filter((c) => c.scale && c.scale !== 'ALT')) { const sc = JSON.parse(readFileSync(path('../../08_realistic_digital_twin/data/instruments.json'), 'utf8')).instruments[c.scale].map; assert.equal(c.min, sc[0][0], c.key); assert.equal(c.max, sc.at(-1)[0], c.key); }
});

test('the lamps light when their switch and the battery switch are up, and a plug glows at its spark with the ignition on', () => {
  for (const id of GLOWING) assert.ok(nodes.has(id), `${id} is in no model`);
  const lamps = (s) => pose({ ...rest(), ...s }).glow;
  assert.equal(lamps({ swBeacon: 1 }).size, 0, 'a lamp lit with the battery switch down');
  assert.ok(lamps({ swBat: 1, swBeacon: 1 }).has('ELECTRICAL.beacon'));
  assert.deepEqual([...lamps({ swBat: 1, swNav: 1 }).keys()].sort(), ['ELECTRICAL.tail_nav_light', 'WING_L.nav_light', 'WING_R.nav_light']);
  assert.ok(lamps({ swBat: 1, swNav: 1 }).get('WING_L.nav_light').color !== lamps({ swBat: 1, swNav: 1 }).get('WING_R.nav_light').color, 'port red, starboard green');
  // plugs: the table matches the models, none glows with the ignition off, and with it on some fire within the cycle
  for (const [id, cyl, mag] of PLUGS) { const x = nodes.get(id); assert.equal(x.cyl, cyl, id); assert.equal(x.magneto, mag, id); }
  const fired = (ignition, crank) => [...pose({ ...rest(), ignition, crank }).glow.keys()].filter((id) => id.startsWith('ENGINE.plug'));
  assert.equal([...Array(72).keys()].flatMap((i) => fired(-2, i * 10)).length, 0, 'a plug fired with the ignition off');
  assert.ok([...Array(72).keys()].some((i) => fired(1, i * 10).length > 0), 'no plug fires in a whole cycle');
  assert.ok([...Array(72).keys()].every((i) => fired(-1, i * 10).every((id) => PLUGS.find((p) => p[0] === id)[2] === 'R')), 'on the right magneto only its plugs fire');
});
