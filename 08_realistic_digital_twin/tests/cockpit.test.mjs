// The pilot in the seat: the limits of the head, where the eyes and the shoulders are, and what a hand reaches.
import test from 'node:test';
import assert from 'node:assert/strict';
import { HEAD, REACH, REST, VIEWS, clampHead, neckPosition, eyePosition, gaze, shoulders, reachDistance, canReach, leanToReach, reachOf } from '../js/seat.js';

const near = (a, b, tol, what) => assert.ok(Math.abs(a - b) <= tol, `${what}: ${a} against ${b} (±${tol})`);
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const within = (x, [lo, hi]) => x >= lo - 1e-12 && x <= hi + 1e-12;

test('the head stays within its limits, whatever it is asked', () => {
  const far = clampHead({ yaw: 999, pitch: 999, forward: 9, side: 9, fov: 999 });
  assert.deepEqual(far, { yaw: HEAD.yaw[1], pitch: HEAD.pitch[1], forward: HEAD.leanForward[1], side: HEAD.leanSide[1], fov: HEAD.fov[1] });
  const back = clampHead({ yaw: -999, pitch: -999, forward: -9, side: -9, fov: -999 });
  assert.deepEqual(back, { yaw: HEAD.yaw[0], pitch: HEAD.pitch[0], forward: HEAD.leanForward[0], side: HEAD.leanSide[0], fov: HEAD.fov[0] });
  assert.deepEqual(clampHead(REST), REST, 'the head at rest is within the limits');
  for (const [name, [yaw, pitch]] of Object.entries(VIEWS)) assert.ok(within(yaw, HEAD.yaw) && within(pitch, HEAD.pitch), `the view "${name}" is one the head can take`);
  // a pilot looks over each shoulder, but not straight behind; looks at the floor between the seats, and at the roof
  assert.ok(HEAD.yaw[1] >= 110 && HEAD.yaw[1] < 180 && HEAD.yaw[0] === -HEAD.yaw[1]);
  assert.ok(HEAD.pitch[0] <= -60 && HEAD.pitch[1] >= 45 && HEAD.pitch[1] < 90);
  assert.equal(HEAD.leanForward[0], 0, 'the seat back is behind: no leaning back');
  assert.ok(HEAD.leanSide[1] < -HEAD.leanSide[0], 'the door is close on the left: less room to lean that way');
});

test('the eye: on the datum with the head level, swinging about the neck as the head turns', () => {
  const level = { yaw: 0, pitch: 0, forward: 0, side: 0 };
  assert.deepEqual(eyePosition(level).map((v) => +v.toFixed(9)), HEAD.eye, 'head level and straight: the eye is the datum');
  assert.ok(dist(eyePosition(REST), HEAD.eye) < 0.03, 'at rest the eye is within 3 cm of the datum');
  const arm = Math.hypot(HEAD.neckBelow, HEAD.neckBehind);
  for (const yaw of [-135, -60, 0, 75, 135]) for (const pitch of [-70, -11, 0, 40]) {
    const h = { yaw, pitch, forward: 0, side: 0 };
    near(dist(eyePosition(h), neckPosition(h)), arm, 1e-9, `the eye stays ${arm.toFixed(3)} m from the neck at yaw ${yaw}, pitch ${pitch}`);
  }
  // the head turned to the left carries the eye to the left and back; looking down carries it forward and down
  const left = eyePosition({ ...level, yaw: 90 });
  assert.ok(left[0] > HEAD.eye[0] + 0.05 && left[2] < HEAD.eye[2] - 0.05, `left: ${left}`);
  const down = eyePosition({ ...level, pitch: -60 });
  assert.ok(down[1] < HEAD.eye[1] - 0.03 && down[2] > HEAD.eye[2], `down: ${down}`);
  // the gaze: a unit vector; +X is the pilot's left, +Y up, +Z the nose
  for (const [h, want] of [[{ yaw: 0, pitch: 0 }, [0, 0, 1]], [{ yaw: 90, pitch: 0 }, [1, 0, 0]], [{ yaw: -90, pitch: 0 }, [-1, 0, 0]], [{ yaw: 0, pitch: 90 }, [0, 1, 0]]]) {
    gaze(h).forEach((v, i) => near(v, want[i], 1e-12, `gaze ${JSON.stringify(h)} [${i}]`));
  }
});

test('a lean moves the head, brings it down a little, and takes the shoulders part of the way', () => {
  const up = eyePosition(REST), fwd = eyePosition({ ...REST, forward: 0.2 }), side = eyePosition({ ...REST, side: -0.14 });
  near(fwd[2] - up[2], 0.2, 1e-12, 'forward');
  near(side[0] - up[0], -0.14, 1e-12, 'to the right');
  assert.ok(fwd[1] < up[1] && up[1] - fwd[1] < 0.04, `the head comes down ${((up[1] - fwd[1]) * 100).toFixed(1)} cm in a 20 cm lean`);
  const [l0, r0] = shoulders(REST), [l1, r1] = shoulders({ forward: 0.2, side: -0.14 });
  near(l0[0] - r0[0], 2 * HEAD.shoulderAside, 1e-12, 'shoulder width');
  near(r1[2] - r0[2], 0.2 * HEAD.shoulderShare, 1e-12, 'the shoulders go forward less than the eyes');
  near(r1[0] - r0[0], -0.14 * HEAD.shoulderShare, 1e-12, 'and less to the side');
  assert.deepEqual(shoulders({ ...REST, yaw: 90, pitch: -40 }), shoulders(REST), 'turning the head does not move the shoulders');
});

test('reach: within an arm of the nearer shoulder; a lean brings more within reach; some things stay out of reach', () => {
  const [left, right] = shoulders(REST);
  const ahead = (s, d) => [s[0], s[1], s[2] + d];
  assert.equal(reachDistance(ahead(right, 0.5)), 0.5);
  assert.ok(canReach(ahead(right, REACH - 0.001)) && !canReach(ahead(right, REACH + 0.001)));
  // the nearer shoulder counts: a point beside the left shoulder is not an arm and a width away
  near(reachDistance([left[0] + 0.3, left[1], left[2]]), 0.3, 1e-12, 'from the left shoulder');
  // 6 cm beyond the arm, straight ahead: a lean forward of less than 10 cm does it
  const justOut = ahead(right, REACH + 0.06);
  assert.equal(reachOf(justOut), 'lean');
  const lean = leanToReach(justOut);
  assert.ok(lean && lean.forward > 0.05 && lean.forward < 0.12 && Math.abs(lean.side) < 0.03, JSON.stringify(lean));
  assert.ok(within(lean.forward, HEAD.leanForward) && within(lean.side, HEAD.leanSide), 'a lean the seat allows');
  assert.ok(canReach(justOut, lean) && !canReach(justOut, { forward: lean.forward - 0.03, side: lean.side }), 'the least lean, to the step of the search');
  assert.equal(reachOf(justOut, lean), 'near');
  assert.deepEqual(leanToReach(ahead(right, 0.4)), { forward: 0, side: 0 }, 'already within reach: no lean');
  // 25 cm beyond the arm: no lean of this seat reaches it
  assert.equal(leanToReach(ahead(right, REACH + 0.25)), null);
  assert.equal(reachOf(ahead(right, REACH + 0.25)), 'far');
  // across the cabin, to the right: leaning that way helps; behind the seat: leaning forward does not
  const across = [right[0] - (REACH + 0.05), right[1], right[2]];
  assert.ok(leanToReach(across).side < -0.05);
  assert.equal(reachOf([right[0], right[1], right[2] - (REACH + 0.02)]), 'far');
});

test('the arm and the seat are those of an adult: plausible numbers, labelled as estimates in the source', () => {
  assert.ok(REACH > 0.6 && REACH < 0.8, `reach ${REACH} m`);
  assert.ok(HEAD.shoulderAside * 2 > 0.3 && HEAD.shoulderAside * 2 < 0.45, 'shoulder width');
  assert.ok(HEAD.torso > 0.6 && HEAD.torso < 0.9);
  assert.deepEqual(HEAD.eye, [0.28, 1.55, 0.015], 'the eye of the Phase 8 model: the front seat occupant at station 37');
  // the eye never travels farther than this from the datum, whatever the head does: the browser test checks the cabin around it
  let worst = 0;
  for (const yaw of [HEAD.yaw[0], -90, 0, 90, HEAD.yaw[1]]) for (const pitch of [HEAD.pitch[0], 0, HEAD.pitch[1]]) for (const forward of HEAD.leanForward) for (const side of HEAD.leanSide) {
    worst = Math.max(worst, dist(eyePosition({ yaw, pitch, forward, side }), HEAD.eye));
  }
  assert.ok(worst < 0.36, `the eye stays within ${worst.toFixed(3)} m of its datum`);
});

// ---------------------------------------------------------------------------------------------- the controls
import { readFileSync } from 'node:fs';
import { cockpitControls } from '../js/cockpit_controls.js';
import { createState } from '../js/sim.js';

/** A host that only remembers what the hand did to it. */
function fakeHost() {
  const h = { flapDeg: 0, trimSet: 0, wheel: { x: 0, y: 0, held: false }, brake: false, knobs: {}, doors: { L: false, R: false }, strokes: 0 };
  h.flaps = { get: () => h.flapDeg, set: (deg) => { h.flapDeg = deg; } };
  h.trim = { get: () => h.trimSet, set: (v) => { h.trimSet = v; } };
  h.yoke = { get: () => ({ x: h.wheel.x, y: h.wheel.y }), set: (x, y) => { h.wheel = { x, y, held: true }; }, release: () => { h.wheel.held = false; } };
  h.parking = { get: () => h.brake, toggle: () => { h.brake = !h.brake; } };
  h.cabin = { get: (k) => !!h.knobs[k], toggle: (k) => { h.knobs[k] = !h.knobs[k]; } };
  h.door = { state: (side) => (h.doors[side] ? 'open' : 'closed'), toggle: (side) => { h.doors[side] = !h.doors[side]; } };
  h.prime = () => { h.strokes += 1; }; h.primes = () => h.strokes;
  return h;
}
const RIGHT = { upper: false, right: true }, LEFT = { upper: false, right: false }, UPPER = { upper: true, right: false }, LOWER = { upper: false, right: false };
const index = (lod) => new Set(JSON.parse(readFileSync(new URL(`../models/model_index_${lod}.json`, import.meta.url), 'utf8')).parts.map((p) => p.name));

test('every control is a part of the model, shows its state, and can be worked', () => {
  const controls = cockpitControls(), s = createState(), h = fakeHost(), high = index('high');
  assert.ok(Object.keys(controls).length >= 22, `${Object.keys(controls).length} controls`);
  for (const [name, def] of Object.entries(controls)) {
    assert.ok(high.has(name), `${name} is a part of the model`);
    assert.equal(typeof def.state(s, h), 'string', `${name} shows its state`);
    assert.ok(def.click || def.drag || def.wheel || def.press, `${name} can be worked`);
  }
  // the controls a flight needs are in every level of detail of the model
  for (const lod of ['medium', 'low']) for (const name of ['PANEL.throttle', 'PANEL.mixture', 'PANEL.carb_heat', 'PANEL.ignition_switch', 'PANEL.master_bat', 'PANEL.master_alt', 'PANEL.flap_switch', 'INTERIOR.trim_wheel', 'INTERIOR.yoke_L', 'FUEL.selector_handle']) {
    assert.ok(index(lod).has(name), `${name} is in the ${lod} model`);
  }
});

test('ignition: one position at a time, never past BOTH by a click; START only while the key is held at BOTH', () => {
  const key = cockpitControls()['PANEL.ignition_switch'], s = createState(), h = fakeHost();
  assert.equal(s.controls.ignition, 'OFF');
  const seen = [];
  for (let i = 0; i < 5; i++) { key.click(s, h, RIGHT); seen.push(s.controls.ignition); }
  assert.deepEqual(seen, ['R', 'L', 'BOTH', 'BOTH', 'BOTH']);
  // pressed on the right half at BOTH: the starter, until the key is let go
  const letGo = key.press(s, h, RIGHT);
  assert.equal(s.controls.ignition, 'START'); assert.equal(key.state(s, h), 'START');
  letGo();
  assert.equal(s.controls.ignition, 'BOTH');
  // a press anywhere else is not the starter
  assert.equal(key.press(s, h, LEFT), null);
  s.controls.ignition = 'L';
  assert.equal(key.press(s, h, RIGHT), null); assert.equal(s.controls.ignition, 'L');
  // back toward OFF on the left half, and not beyond
  s.controls.ignition = 'BOTH';
  const back = [];
  for (let i = 0; i < 4; i++) { key.click(s, h, LEFT); back.push(s.controls.ignition); }
  assert.deepEqual(back, ['L', 'R', 'OFF', 'OFF']);
  // the mouse wheel turns it both ways, and never into START
  for (let i = 0; i < 6; i++) key.wheel(s, h, -1);
  assert.equal(s.controls.ignition, 'BOTH');
  key.wheel(s, h, 1);
  assert.equal(s.controls.ignition, 'L');
});

test('fuel selector: LEFT, BOTH, RIGHT, OFF round the dial, either way', () => {
  const sel = cockpitControls()['FUEL.selector_handle'], s = createState(), h = fakeHost();
  assert.equal(s.controls.fuelSelector, 'BOTH');
  const clockwise = [];
  for (let i = 0; i < 4; i++) { sel.click(s, h, RIGHT); clockwise.push(s.controls.fuelSelector); }
  assert.deepEqual(clockwise, ['RIGHT', 'OFF', 'LEFT', 'BOTH']);
  const other = [];
  for (let i = 0; i < 4; i++) { sel.click(s, h, LEFT); other.push(s.controls.fuelSelector); }
  assert.deepEqual(other, ['LEFT', 'OFF', 'RIGHT', 'BOTH']);
  sel.wheel(s, h, -1); assert.equal(s.controls.fuelSelector, 'RIGHT');
  sel.wheel(s, h, 1); assert.equal(sel.state(s, h), 'BOTH');
});

test('push-pull controls: pushed in is up the picture; throttle opens, mixture leans, carburetor heat comes on', () => {
  const c = cockpitControls(), s = createState(), h = fakeHost();
  s.controls.throttle = 0.2;
  c['PANEL.throttle'].drag(s, h, { dx: 0, dy: -34 });               // up the picture: pushed in
  near(s.controls.throttle, 0.4, 1e-9, 'throttle pushed in');
  c['PANEL.throttle'].drag(s, h, { dx: 0, dy: -500 }); assert.equal(s.controls.throttle, 1, 'to the stop');
  c['PANEL.throttle'].drag(s, h, { dx: 0, dy: 900 }); assert.equal(s.controls.throttle, 0, 'and back to idle');
  c['PANEL.throttle'].wheel(s, h, -1); near(s.controls.throttle, 0.04, 1e-9, 'the mouse wheel up pushes it in');
  assert.equal(c['PANEL.throttle'].state(s, h), '4 %');
  assert.equal(s.controls.mixture, 1);
  c['PANEL.mixture'].drag(s, h, { dx: 0, dy: 85 });                 // down the picture: pulled out, leaner
  near(s.controls.mixture, 0.5, 1e-9, 'mixture pulled');
  c['PANEL.mixture'].drag(s, h, { dx: 0, dy: 400 }); assert.equal(s.controls.mixture, 0, 'idle cut-off');
  assert.equal(c['PANEL.carb_heat'].state(s, h), 'OFF');
  c['PANEL.carb_heat'].click(s, h, LEFT); assert.equal(s.controls.carbHeat, 1); assert.equal(c['PANEL.carb_heat'].state(s, h), 'ON');
  c['PANEL.carb_heat'].click(s, h, LEFT); assert.equal(s.controls.carbHeat, 0);
  c['PANEL.carb_heat'].drag(s, h, { dx: 0, dy: 170 }); assert.equal(s.controls.carbHeat, 1, 'pulled out is ON');
});

test('flap lever, trim wheel and control wheel act through the host', () => {
  const c = cockpitControls(), s = createState(), h = fakeHost();
  const lever = c['PANEL.flap_switch'];
  lever.click(s, h, LOWER); lever.click(s, h, LOWER); assert.equal(h.flapDeg, 20); assert.equal(lever.state(s, h), '20°');
  lever.click(s, h, UPPER); assert.equal(h.flapDeg, 10);
  for (let i = 0; i < 6; i++) lever.wheel(s, h, 1);
  assert.equal(h.flapDeg, 40, 'no farther than 40');
  for (let i = 0; i < 6; i++) lever.click(s, h, UPPER);
  assert.equal(h.flapDeg, 0, 'no higher than up');
  h.flapDeg = 17; lever.click(s, h, LOWER); assert.equal(h.flapDeg, 30, 'from between two positions: the next one down from the nearer');
  const trim = c['INTERIOR.trim_wheel'];
  trim.drag(s, h, { dx: 0, dy: 60 }); near(h.trimSet, 0.1, 1e-9, 'the rim rolled down is nose up');
  trim.wheel(s, h, -1); near(h.trimSet, 0.09, 1e-9, 'a step nose down');
  trim.drag(s, h, { dx: 0, dy: 9000 }); assert.equal(h.trimSet, 1);
  assert.equal(trim.state(s, h), '+1.00');
  h.trimSet = -0.25; assert.equal(trim.state(s, h), '−0.25');
  const wheel = c['INTERIOR.yoke_L'];
  h.wheel = { x: 0.2, y: -0.1, held: false };
  const from = wheel.grab(s, h);
  wheel.drag(s, h, { dx: 5, dy: 5, tx: 75, ty: 45, from });
  near(h.wheel.x, 0.7, 1e-9, 'turned to the right from where it was'); near(h.wheel.y, 0.2, 1e-9, 'and pulled back'); assert.equal(h.wheel.held, true);
  wheel.drag(s, h, { dx: 5, dy: 5, tx: 900, ty: -900, from }); assert.deepEqual([h.wheel.x, h.wheel.y], [1, -1], 'to its stops');
  wheel.release(s, h); assert.equal(h.wheel.held, false);
});

test('switches flip; primer, parking brake, cabin air and doors act through the host', () => {
  const c = cockpitControls(), s = createState(), h = fakeHost();
  for (const [part, key] of [['PANEL.master_bat', 'masterBat'], ['PANEL.master_alt', 'masterAlt'], ['PANEL.switch_avionics_master', 'avionics'], ['PANEL.switch_beacon', 'beacon'], ['PANEL.switch_nav_lights', 'navLights'], ['PANEL.switch_landing_light', 'landingLight'], ['PANEL.switch_pitot_heat', 'pitotHeat'], ['PANEL.switch_strobe', 'strobe']]) {
    assert.equal(c[part].state(s, h), 'OFF', part);
    c[part].click(s, h, LEFT); assert.equal(s.controls[key], true, part); assert.equal(c[part].state(s, h), 'ON');
    c[part].click(s, h, LEFT); assert.equal(s.controls[key], false, part);
  }
  for (let i = 0; i < 3; i++) c['PANEL.primer'].click(s, h, LEFT);
  assert.equal(h.strokes, 3); assert.equal(c['PANEL.primer'].state(s, h), '3');
  c['INTERIOR.parking_brake'].click(s, h, LEFT); assert.equal(h.brake, true); assert.equal(c['INTERIOR.parking_brake'].state(s, h), 'ON');
  c['PANEL.cabin_air'].click(s, h, LEFT); assert.equal(c['PANEL.cabin_air'].state(s, h), 'ON'); assert.equal(c['PANEL.cabin_heat'].state(s, h), 'OFF');
  c['INTERIOR.door_inner_handle_L'].click(s, h, LEFT); assert.equal(c['INTERIOR.door_inner_handle_L'].state(s, h), 'open'); assert.equal(c['INTERIOR.door_inner_handle_R'].state(s, h), 'closed');
  assert.ok(c['INTERIOR.door_inner_handle_L'].fixed, 'a door handle is reached for where the closed door has it');
});
